"""Persist and atomically transition report jobs in a single-node SQLite queue."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from .history import decode_history_cursor, encode_history_cursor
from .idempotency import request_fingerprint
from .models import JobStatus, ReportJob


class IdempotencyKeyReuseError(ValueError):
    """Signal that one idempotency key was reused for a different request."""


class JobStore:
    """Manage durable report-job lifecycle state in the ``report_jobs`` table."""

    def __init__(self, database_path: Path) -> None:
        """Initialize the SQLite database path, schema, migrations, and queue indexes."""
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=30, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS report_jobs (
                    report_job_id TEXT PRIMARY KEY,
                    job_status TEXT NOT NULL,
                    request_json TEXT NOT NULL,
                    request_fingerprint TEXT NOT NULL,
                    idempotency_key_digest TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    job_error_message TEXT,
                    artifact_dir TEXT
                )
                """
            )
            schema_columns = {
                database_row["name"]
                for database_row in connection.execute("PRAGMA table_info(report_jobs)")
            }
            if "report_job_id" not in schema_columns and "id" in schema_columns:
                connection.execute(
                    "ALTER TABLE report_jobs RENAME COLUMN id TO report_job_id"
                )
            if "job_status" not in schema_columns and "status" in schema_columns:
                connection.execute(
                    "ALTER TABLE report_jobs RENAME COLUMN status TO job_status"
                )
            if "job_error_message" not in schema_columns and "error" in schema_columns:
                connection.execute(
                    "ALTER TABLE report_jobs RENAME COLUMN error TO job_error_message"
                )
            schema_columns = {
                database_row["name"]
                for database_row in connection.execute("PRAGMA table_info(report_jobs)")
            }
            if "request_fingerprint" not in schema_columns:
                connection.execute(
                    "ALTER TABLE report_jobs ADD COLUMN request_fingerprint TEXT"
                )
            if "idempotency_key_digest" not in schema_columns:
                connection.execute(
                    "ALTER TABLE report_jobs ADD COLUMN idempotency_key_digest TEXT"
                )
            legacy_job_rows = connection.execute(
                """
                SELECT report_job_id, request_json
                FROM report_jobs
                WHERE request_fingerprint IS NULL OR request_fingerprint=''
                """
            ).fetchall()
            for legacy_job_row in legacy_job_rows:
                request_digest = request_fingerprint(
                    json.loads(legacy_job_row["request_json"])
                )
                connection.execute(
                    "UPDATE report_jobs SET request_fingerprint=? WHERE report_job_id=?",
                    (request_digest, legacy_job_row["report_job_id"]),
                )
            connection.execute("DROP INDEX IF EXISTS idx_report_jobs_status_created")
            connection.execute("DROP INDEX IF EXISTS idx_report_jobs_created_id")
            connection.execute("DROP INDEX IF EXISTS idx_report_jobs_status_created_id")
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_report_jobs_job_status_created_at
                ON report_jobs(job_status, created_at)
                """
            )
            connection.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_report_jobs_idempotency_key_digest
                ON report_jobs(idempotency_key_digest)
                WHERE idempotency_key_digest IS NOT NULL
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_report_jobs_created_at_job_id
                ON report_jobs(created_at DESC, report_job_id DESC)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_report_jobs_job_status_created_at_job_id
                ON report_jobs(job_status, created_at DESC, report_job_id DESC)
                """
            )
            connection.execute("COMMIT")

    @staticmethod
    def _row_to_report_job(database_row: sqlite3.Row | None) -> ReportJob | None:
        """Translate one SQLite row into the semantic report-job domain model."""
        if database_row is None:
            return None
        return ReportJob(
            report_job_id=database_row["report_job_id"],
            job_status=JobStatus(database_row["job_status"]),
            report_request=json.loads(database_row["request_json"]),
            created_at=datetime.fromisoformat(database_row["created_at"]),
            updated_at=datetime.fromisoformat(database_row["updated_at"]),
            request_fingerprint=database_row["request_fingerprint"],
            idempotency_key_digest=database_row["idempotency_key_digest"],
            job_error_message=database_row["job_error_message"],
            artifact_dir=database_row["artifact_dir"],
        )

    @staticmethod
    def _request_json(request: dict[str, Any]) -> str:
        """Serialize one validated report request for durable storage."""
        return json.dumps(request, ensure_ascii=False, default=str)

    def create(self, request: dict[str, Any]) -> ReportJob:
        """Create and return one queued job containing a JSON-serializable request."""
        now = datetime.now(UTC)
        fingerprint = request_fingerprint(request)
        report_job = ReportJob(
            report_job_id=str(uuid.uuid4()),
            job_status=JobStatus.QUEUED,
            report_request=request,
            created_at=now,
            updated_at=now,
            request_fingerprint=fingerprint,
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO report_jobs(
                    report_job_id,job_status,request_json,request_fingerprint,
                    idempotency_key_digest,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?)
                """,
                (
                    report_job.report_job_id,
                    report_job.job_status.value,
                    self._request_json(request),
                    fingerprint,
                    None,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )
        return report_job

    def create_idempotent(
        self,
        request: dict[str, Any],
        idempotency_key_digest: str,
        fingerprint: str,
    ) -> tuple[ReportJob, bool]:
        """Create one job or replay the existing job for the same key and request.

        Args:
            request: Validated JSON-compatible report request.
            idempotency_key_digest: SHA-256 digest of the decoded client key.
            fingerprint: Canonical SHA-256 digest of ``request``.

        Returns:
            A pair containing the durable job and whether it was replayed.

        Raises:
            IdempotencyKeyReuseError: When the key already belongs to another request.
        """
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            database_row = connection.execute(
                "SELECT * FROM report_jobs WHERE idempotency_key_digest=?",
                (idempotency_key_digest,),
            ).fetchone()
            if database_row is not None:
                existing_job = self._row_to_report_job(database_row)
                assert existing_job is not None
                if existing_job.request_fingerprint != fingerprint:
                    raise IdempotencyKeyReuseError(
                        "Idempotency-Key is already used with a different payload"
                    )
                connection.execute("COMMIT")
                return existing_job, True

            now = datetime.now(UTC)
            report_job = ReportJob(
                report_job_id=str(uuid.uuid4()),
                job_status=JobStatus.QUEUED,
                report_request=request,
                created_at=now,
                updated_at=now,
                request_fingerprint=fingerprint,
                idempotency_key_digest=idempotency_key_digest,
            )
            connection.execute(
                """
                INSERT INTO report_jobs(
                    report_job_id,job_status,request_json,request_fingerprint,
                    idempotency_key_digest,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?)
                """,
                (
                    report_job.report_job_id,
                    report_job.job_status.value,
                    self._request_json(request),
                    fingerprint,
                    idempotency_key_digest,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )
            connection.execute("COMMIT")
        return report_job, False

    def get(self, job_id: str) -> ReportJob | None:
        """Return one job by UUID or ``None`` when no matching row exists."""
        with self._connect() as connection:
            database_row = connection.execute(
                "SELECT * FROM report_jobs WHERE report_job_id=?",
                (job_id,),
            ).fetchone()
        return self._row_to_report_job(database_row)

    def list_jobs(
        self,
        *,
        limit: int,
        cursor: str | None = None,
        status: JobStatus | None = None,
    ) -> tuple[list[ReportJob], str | None]:
        """Return one stable newest-first page of report jobs and its continuation."""
        if not 1 <= limit <= 100:
            raise ValueError("Report history limit must be between 1 and 100")
        history_boundary: tuple[str, str] | None = None
        if cursor is not None:
            boundary_created_at, boundary_job_id = decode_history_cursor(cursor)
            history_boundary = (boundary_created_at.isoformat(), boundary_job_id)
        fetch_limit = limit + 1
        with self._connect() as connection:
            if status is None and history_boundary is None:
                database_rows = connection.execute(
                    """
                    SELECT * FROM report_jobs
                    ORDER BY created_at DESC, report_job_id DESC
                    LIMIT ?
                    """,
                    (fetch_limit,),
                ).fetchall()
            elif status is not None and history_boundary is None:
                database_rows = connection.execute(
                    """
                    SELECT * FROM report_jobs
                    WHERE job_status=?
                    ORDER BY created_at DESC, report_job_id DESC
                    LIMIT ?
                    """,
                    (status.value, fetch_limit),
                ).fetchall()
            elif status is None:
                assert history_boundary is not None
                boundary_created_at, boundary_job_id = history_boundary
                database_rows = connection.execute(
                    """
                    SELECT * FROM report_jobs
                    WHERE created_at < ? OR (created_at = ? AND report_job_id < ?)
                    ORDER BY created_at DESC, report_job_id DESC
                    LIMIT ?
                    """,
                    (
                        boundary_created_at,
                        boundary_created_at,
                        boundary_job_id,
                        fetch_limit,
                    ),
                ).fetchall()
            else:
                assert history_boundary is not None
                boundary_created_at, boundary_job_id = history_boundary
                database_rows = connection.execute(
                    """
                    SELECT * FROM report_jobs
                    WHERE job_status=?
                      AND (created_at < ? OR (created_at = ? AND report_job_id < ?))
                    ORDER BY created_at DESC, report_job_id DESC
                    LIMIT ?
                    """,
                    (
                        status.value,
                        boundary_created_at,
                        boundary_created_at,
                        boundary_job_id,
                        fetch_limit,
                    ),
                ).fetchall()
        has_more = len(database_rows) > limit
        report_jobs = [
            self._row_to_report_job(database_row)
            for database_row in database_rows[:limit]
        ]
        report_page = [report_job for report_job in report_jobs if report_job is not None]
        next_cursor = None
        if has_more and report_page:
            last_report_job = report_page[-1]
            next_cursor = encode_history_cursor(
                last_report_job.created_at,
                last_report_job.report_job_id,
            )
        return report_page, next_cursor

    def claim_next(self) -> ReportJob | None:
        """Atomically claim the oldest queued job for a worker."""
        now = datetime.now(UTC).isoformat()
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            database_row = connection.execute(
                """
                SELECT report_job_id
                FROM report_jobs
                WHERE job_status=?
                ORDER BY created_at
                LIMIT 1
                """,
                (JobStatus.QUEUED.value,),
            ).fetchone()
            if database_row is None:
                connection.execute("COMMIT")
                return None
            update_cursor = connection.execute(
                """
                UPDATE report_jobs
                SET job_status=?, updated_at=?
                WHERE report_job_id=? AND job_status=?
                """,
                (
                    JobStatus.RUNNING.value,
                    now,
                    database_row["report_job_id"],
                    JobStatus.QUEUED.value,
                ),
            )
            connection.execute("COMMIT")
            if update_cursor.rowcount != 1:
                return None
        return self.get(database_row["report_job_id"])

    def finish(self, job_id: str, artifact_dir: Path) -> ReportJob:
        """Mark a job completed and record its published artifact directory."""
        return self._transition(job_id, JobStatus.COMPLETED, artifact_dir=str(artifact_dir))

    def fail(self, job_id: str, error: str, *, quality: bool = False) -> ReportJob:
        """Mark a job failed, optionally distinguishing deterministic quality failure."""
        job_status = JobStatus.QUALITY_FAILED if quality else JobStatus.FAILED
        return self._transition(
            job_id,
            job_status,
            job_error_message=error[:4000],
        )

    def _transition(
        self,
        job_id: str,
        job_status: JobStatus,
        *,
        job_error_message: str | None = None,
        artifact_dir: str | None = None,
    ) -> ReportJob:
        now = datetime.now(UTC).isoformat()
        with self._connect() as connection:
            update_cursor = connection.execute(
                """
                UPDATE report_jobs
                SET job_status=?,updated_at=?,job_error_message=?,artifact_dir=?
                WHERE report_job_id=?
                """,
                (job_status.value, now, job_error_message, artifact_dir, job_id),
            )
        if update_cursor.rowcount != 1:
            raise KeyError(f"Unknown report job: {job_id}")
        updated_report_job = self.get(job_id)
        if updated_report_job is None:
            raise KeyError(f"Unknown report job after transition: {job_id}")
        return updated_report_job

    def delete(self, job_id: str) -> bool:
        """Delete one terminal job and report whether a row was removed."""
        with self._connect() as connection:
            delete_cursor = connection.execute(
                """
                DELETE FROM report_jobs
                WHERE report_job_id=? AND job_status IN (?,?,?)
                """,
                (
                    job_id,
                    JobStatus.COMPLETED.value,
                    JobStatus.FAILED.value,
                    JobStatus.QUALITY_FAILED.value,
                ),
            )
        return delete_cursor.rowcount == 1

    def purge(self, retention_days: int) -> list[str]:
        """Delete expired terminal rows and return their job UUIDs for artifact cleanup."""
        retention_cutoff = (datetime.now(UTC) - timedelta(days=retention_days)).isoformat()
        with self._connect() as connection:
            database_rows = connection.execute(
                """
                SELECT report_job_id
                FROM report_jobs
                WHERE updated_at < ? AND job_status IN (?,?,?)
                """,
                (
                    retention_cutoff,
                    JobStatus.COMPLETED.value,
                    JobStatus.FAILED.value,
                    JobStatus.QUALITY_FAILED.value,
                ),
            ).fetchall()
            report_job_ids = [database_row["report_job_id"] for database_row in database_rows]
            connection.executemany(
                "DELETE FROM report_jobs WHERE report_job_id=?",
                ((job_id,) for job_id in report_job_ids),
            )
        return report_job_ids
