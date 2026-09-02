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


LEGACY_REPORT_JOB_COLUMN_MIGRATIONS: tuple[tuple[str, str], ...] = (
    ("id", "ALTER TABLE report_jobs RENAME COLUMN id TO report_job_id"),
    ("status", "ALTER TABLE report_jobs RENAME COLUMN status TO job_status"),
    (
        "request_json",
        "ALTER TABLE report_jobs RENAME COLUMN request_json TO report_request_json",
    ),
    (
        "created_at",
        "ALTER TABLE report_jobs RENAME COLUMN created_at TO job_created_at",
    ),
    (
        "updated_at",
        "ALTER TABLE report_jobs RENAME COLUMN updated_at TO job_updated_at",
    ),
    (
        "error",
        "ALTER TABLE report_jobs RENAME COLUMN error TO failure_message",
    ),
    (
        "artifact_dir",
        "ALTER TABLE report_jobs RENAME COLUMN artifact_dir TO artifact_directory",
    ),
)

LEGACY_REPORT_JOB_INDEX_DROP_STATEMENTS: tuple[str, ...] = (
    "DROP INDEX IF EXISTS idx_report_jobs_status_created",
    "DROP INDEX IF EXISTS idx_report_jobs_created_id",
    "DROP INDEX IF EXISTS idx_report_jobs_status_created_id",
)


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
        database_connection = sqlite3.connect(
            self.database_path, timeout=30, isolation_level=None
        )
        database_connection.row_factory = sqlite3.Row
        database_connection.execute("PRAGMA journal_mode=WAL")
        database_connection.execute("PRAGMA foreign_keys=ON")
        return database_connection

    def _initialize(self) -> None:
        with self._connect() as database_connection:
            database_connection.execute("BEGIN IMMEDIATE")
            database_connection.execute(
                """
                CREATE TABLE IF NOT EXISTS report_jobs (
                    report_job_id TEXT PRIMARY KEY,
                    job_status TEXT NOT NULL,
                    report_request_json TEXT NOT NULL,
                    request_fingerprint TEXT NOT NULL,
                    idempotency_key_digest TEXT,
                    job_created_at TEXT NOT NULL,
                    job_updated_at TEXT NOT NULL,
                    failure_message TEXT,
                    artifact_directory TEXT
                )
                """
            )
            column_names = {
                schema_row["name"]
                for schema_row in database_connection.execute(
                    "PRAGMA table_info(report_jobs)"
                )
            }
            for legacy_column_name, migration_statement in (
                LEGACY_REPORT_JOB_COLUMN_MIGRATIONS
            ):
                if legacy_column_name in column_names:
                    database_connection.execute(migration_statement)
                    column_names = {
                        schema_row["name"]
                        for schema_row in database_connection.execute(
                            "PRAGMA table_info(report_jobs)"
                        )
                    }
            if "request_fingerprint" not in column_names:
                database_connection.execute(
                    "ALTER TABLE report_jobs ADD COLUMN request_fingerprint TEXT"
                )
            if "idempotency_key_digest" not in column_names:
                database_connection.execute(
                    "ALTER TABLE report_jobs ADD COLUMN idempotency_key_digest TEXT"
                )
            legacy_job_rows = database_connection.execute(
                """
                SELECT report_job_id, report_request_json
                FROM report_jobs
                WHERE request_fingerprint IS NULL OR request_fingerprint=''
                """
            ).fetchall()
            for legacy_job_row in legacy_job_rows:
                report_request_fingerprint = request_fingerprint(
                    json.loads(legacy_job_row["report_request_json"])
                )
                database_connection.execute(
                    "UPDATE report_jobs SET request_fingerprint=? WHERE report_job_id=?",
                    (
                        report_request_fingerprint,
                        legacy_job_row["report_job_id"],
                    ),
                )
            for index_drop_statement in LEGACY_REPORT_JOB_INDEX_DROP_STATEMENTS:
                database_connection.execute(index_drop_statement)
            database_connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_report_jobs_job_status_job_created_at
                ON report_jobs(job_status, job_created_at)
                """
            )
            database_connection.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_report_jobs_idempotency_key_digest
                ON report_jobs(idempotency_key_digest)
                WHERE idempotency_key_digest IS NOT NULL
                """
            )
            database_connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_report_jobs_job_created_at_report_job_id
                ON report_jobs(job_created_at DESC, report_job_id DESC)
                """
            )
            database_connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_report_jobs_job_status_job_created_at_report_job_id
                ON report_jobs(job_status, job_created_at DESC, report_job_id DESC)
                """
            )
            database_connection.execute("COMMIT")

    @staticmethod
    def _report_job_from_row(job_row: sqlite3.Row | None) -> ReportJob | None:
        """Translate one persisted report-job row into the semantic domain model."""
        if job_row is None:
            return None
        return ReportJob(
            report_job_id=job_row["report_job_id"],
            job_status=JobStatus(job_row["job_status"]),
            report_request=json.loads(job_row["report_request_json"]),
            job_created_at=datetime.fromisoformat(job_row["job_created_at"]),
            job_updated_at=datetime.fromisoformat(job_row["job_updated_at"]),
            request_fingerprint=job_row["request_fingerprint"],
            idempotency_key_digest=job_row["idempotency_key_digest"],
            failure_message=job_row["failure_message"],
            artifact_directory=job_row["artifact_directory"],
        )

    @staticmethod
    def _report_request_json(report_request: dict[str, Any]) -> str:
        """Serialize one validated report request for durable storage."""
        return json.dumps(report_request, ensure_ascii=False, default=str)

    def create(self, request: dict[str, Any]) -> ReportJob:
        """Create and return one queued job containing a JSON-serializable request.

        ``request`` remains the structural-port keyword for compatibility; the
        persistence implementation immediately translates it to report vocabulary.
        """
        report_request = request
        current_timestamp = datetime.now(UTC)
        report_request_fingerprint = request_fingerprint(report_request)
        report_job = ReportJob(
            report_job_id=str(uuid.uuid4()),
            job_status=JobStatus.QUEUED,
            report_request=report_request,
            job_created_at=current_timestamp,
            job_updated_at=current_timestamp,
            request_fingerprint=report_request_fingerprint,
        )
        with self._connect() as database_connection:
            database_connection.execute(
                """
                INSERT INTO report_jobs(
                    report_job_id,job_status,report_request_json,request_fingerprint,
                    idempotency_key_digest,job_created_at,job_updated_at
                ) VALUES(?,?,?,?,?,?,?)
                """,
                (
                    report_job.report_job_id,
                    report_job.job_status.value,
                    self._report_request_json(report_request),
                    report_request_fingerprint,
                    None,
                    current_timestamp.isoformat(),
                    current_timestamp.isoformat(),
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

        ``request`` and ``fingerprint`` remain structural-port keyword names for
        compatibility. They are translated immediately to report-domain vocabulary.

        Args:
            request: Validated JSON-compatible report request.
            idempotency_key_digest: SHA-256 digest of the decoded client key.
            fingerprint: Canonical SHA-256 digest of ``request``.

        Returns:
            A pair containing the durable job and whether it was replayed.

        Raises:
            IdempotencyKeyReuseError: When the key already belongs to another request.
        """
        report_request = request
        report_request_fingerprint = fingerprint
        with self._connect() as database_connection:
            database_connection.execute("BEGIN IMMEDIATE")
            matching_job_row = database_connection.execute(
                "SELECT * FROM report_jobs WHERE idempotency_key_digest=?",
                (idempotency_key_digest,),
            ).fetchone()
            if matching_job_row is not None:
                existing_report_job = self._report_job_from_row(matching_job_row)
                assert existing_report_job is not None
                if (
                    existing_report_job.request_fingerprint
                    != report_request_fingerprint
                ):
                    raise IdempotencyKeyReuseError(
                        "Idempotency-Key is already used with a different payload"
                    )
                database_connection.execute("COMMIT")
                return existing_report_job, True

            current_timestamp = datetime.now(UTC)
            report_job = ReportJob(
                report_job_id=str(uuid.uuid4()),
                job_status=JobStatus.QUEUED,
                report_request=report_request,
                job_created_at=current_timestamp,
                job_updated_at=current_timestamp,
                request_fingerprint=report_request_fingerprint,
                idempotency_key_digest=idempotency_key_digest,
            )
            database_connection.execute(
                """
                INSERT INTO report_jobs(
                    report_job_id,job_status,report_request_json,request_fingerprint,
                    idempotency_key_digest,job_created_at,job_updated_at
                ) VALUES(?,?,?,?,?,?,?)
                """,
                (
                    report_job.report_job_id,
                    report_job.job_status.value,
                    self._report_request_json(report_request),
                    report_request_fingerprint,
                    idempotency_key_digest,
                    current_timestamp.isoformat(),
                    current_timestamp.isoformat(),
                ),
            )
            database_connection.execute("COMMIT")
        return report_job, False

    def get(self, job_id: str) -> ReportJob | None:
        """Return one job by UUID or ``None`` when no matching row exists."""
        with self._connect() as database_connection:
            job_row = database_connection.execute(
                "SELECT * FROM report_jobs WHERE report_job_id=?", (job_id,)
            ).fetchone()
        return self._report_job_from_row(job_row)

    def list_jobs(
        self,
        *,
        limit: int,
        cursor: str | None = None,
        status: JobStatus | None = None,
    ) -> tuple[list[ReportJob], str | None]:
        """Return one stable newest-first page of report jobs and its continuation.

        ``limit``, ``cursor``, and ``status`` remain structural-port keyword names for
        compatibility and are translated to report-history vocabulary internally.
        """
        page_limit = limit
        history_cursor = cursor
        job_status_filter = status
        if not 1 <= page_limit <= 100:
            raise ValueError("Report history limit must be between 1 and 100")
        page_boundary: tuple[str, str] | None = None
        if history_cursor is not None:
            boundary_created_at, boundary_job_id = decode_history_cursor(history_cursor)
            page_boundary = (boundary_created_at.isoformat(), boundary_job_id)
        fetch_limit = page_limit + 1
        with self._connect() as database_connection:
            if job_status_filter is None and page_boundary is None:
                job_rows = database_connection.execute(
                    """
                    SELECT * FROM report_jobs
                    ORDER BY job_created_at DESC, report_job_id DESC
                    LIMIT ?
                    """,
                    (fetch_limit,),
                ).fetchall()
            elif job_status_filter is not None and page_boundary is None:
                job_rows = database_connection.execute(
                    """
                    SELECT * FROM report_jobs
                    WHERE job_status=?
                    ORDER BY job_created_at DESC, report_job_id DESC
                    LIMIT ?
                    """,
                    (job_status_filter.value, fetch_limit),
                ).fetchall()
            elif job_status_filter is None:
                assert page_boundary is not None
                boundary_created_at, boundary_job_id = page_boundary
                job_rows = database_connection.execute(
                    """
                    SELECT * FROM report_jobs
                    WHERE job_created_at < ?
                       OR (job_created_at = ? AND report_job_id < ?)
                    ORDER BY job_created_at DESC, report_job_id DESC
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
                assert page_boundary is not None
                boundary_created_at, boundary_job_id = page_boundary
                job_rows = database_connection.execute(
                    """
                    SELECT * FROM report_jobs
                    WHERE job_status=?
                      AND (
                        job_created_at < ?
                        OR (job_created_at = ? AND report_job_id < ?)
                      )
                    ORDER BY job_created_at DESC, report_job_id DESC
                    LIMIT ?
                    """,
                    (
                        job_status_filter.value,
                        boundary_created_at,
                        boundary_created_at,
                        boundary_job_id,
                        fetch_limit,
                    ),
                ).fetchall()
        has_more_jobs = len(job_rows) > page_limit
        nullable_report_jobs = [
            self._report_job_from_row(job_row) for job_row in job_rows[:page_limit]
        ]
        report_job_page = [
            report_job
            for report_job in nullable_report_jobs
            if report_job is not None
        ]
        next_history_cursor = None
        if has_more_jobs and report_job_page:
            last_report_job = report_job_page[-1]
            next_history_cursor = encode_history_cursor(
                last_report_job.job_created_at,
                last_report_job.report_job_id,
            )
        return report_job_page, next_history_cursor

    def claim_next(self) -> ReportJob | None:
        """Atomically claim the oldest queued job for a worker."""
        current_timestamp = datetime.now(UTC).isoformat()
        with self._connect() as database_connection:
            database_connection.execute("BEGIN IMMEDIATE")
            queued_job_row = database_connection.execute(
                """
                SELECT report_job_id FROM report_jobs
                WHERE job_status=? ORDER BY job_created_at LIMIT 1
                """,
                (JobStatus.QUEUED.value,),
            ).fetchone()
            if queued_job_row is None:
                database_connection.execute("COMMIT")
                return None
            update_cursor = database_connection.execute(
                """
                UPDATE report_jobs SET job_status=?, job_updated_at=?
                WHERE report_job_id=? AND job_status=?
                """,
                (
                    JobStatus.RUNNING.value,
                    current_timestamp,
                    queued_job_row["report_job_id"],
                    JobStatus.QUEUED.value,
                ),
            )
            database_connection.execute("COMMIT")
            if update_cursor.rowcount != 1:
                return None
        return self.get(queued_job_row["report_job_id"])

    def finish(self, job_id: str, artifact_dir: Path) -> ReportJob:
        """Mark a job completed and record its published artifact directory."""
        return self._transition(
            job_id,
            JobStatus.COMPLETED,
            artifact_directory=str(artifact_dir),
        )

    def fail(self, job_id: str, error: str, *, quality: bool = False) -> ReportJob:
        """Mark a job failed, optionally distinguishing deterministic quality failure."""
        failure_status = JobStatus.QUALITY_FAILED if quality else JobStatus.FAILED
        return self._transition(
            job_id,
            failure_status,
            failure_message=error[:4000],
        )

    def _transition(
        self,
        job_id: str,
        job_status: JobStatus,
        *,
        failure_message: str | None = None,
        artifact_directory: str | None = None,
    ) -> ReportJob:
        current_timestamp = datetime.now(UTC).isoformat()
        with self._connect() as database_connection:
            update_cursor = database_connection.execute(
                """
                UPDATE report_jobs
                SET job_status=?,job_updated_at=?,failure_message=?,artifact_directory=?
                WHERE report_job_id=?
                """,
                (
                    job_status.value,
                    current_timestamp,
                    failure_message,
                    artifact_directory,
                    job_id,
                ),
            )
        if update_cursor.rowcount != 1:
            raise KeyError(f"Unknown report job: {job_id}")
        transitioned_report_job = self.get(job_id)
        if transitioned_report_job is None:
            raise KeyError(f"Unknown report job after transition: {job_id}")
        return transitioned_report_job

    def delete(self, job_id: str) -> bool:
        """Delete one terminal job and report whether a row was removed."""
        with self._connect() as database_connection:
            delete_cursor = database_connection.execute(
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
        retention_cutoff = (
            datetime.now(UTC) - timedelta(days=retention_days)
        ).isoformat()
        with self._connect() as database_connection:
            expired_job_rows = database_connection.execute(
                """
                SELECT report_job_id FROM report_jobs
                WHERE job_updated_at < ? AND job_status IN (?,?,?)
                """,
                (
                    retention_cutoff,
                    JobStatus.COMPLETED.value,
                    JobStatus.FAILED.value,
                    JobStatus.QUALITY_FAILED.value,
                ),
            ).fetchall()
            report_job_ids = [
                expired_job_row["report_job_id"]
                for expired_job_row in expired_job_rows
            ]
            database_connection.executemany(
                "DELETE FROM report_jobs WHERE report_job_id=?",
                ((job_id,) for job_id in report_job_ids),
            )
        return report_job_ids
