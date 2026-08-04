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
                    id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    request_json TEXT NOT NULL,
                    request_fingerprint TEXT NOT NULL,
                    idempotency_key_digest TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    error TEXT,
                    artifact_dir TEXT
                )
                """
            )
            columns = {
                row["name"] for row in connection.execute("PRAGMA table_info(report_jobs)")
            }
            if "request_fingerprint" not in columns:
                connection.execute(
                    "ALTER TABLE report_jobs ADD COLUMN request_fingerprint TEXT"
                )
            if "idempotency_key_digest" not in columns:
                connection.execute(
                    "ALTER TABLE report_jobs ADD COLUMN idempotency_key_digest TEXT"
                )
            legacy_rows = connection.execute(
                """
                SELECT id, request_json
                FROM report_jobs
                WHERE request_fingerprint IS NULL OR request_fingerprint=''
                """
            ).fetchall()
            for row in legacy_rows:
                fingerprint = request_fingerprint(json.loads(row["request_json"]))
                connection.execute(
                    "UPDATE report_jobs SET request_fingerprint=? WHERE id=?",
                    (fingerprint, row["id"]),
                )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_report_jobs_status_created ON report_jobs(status, created_at)"
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
                CREATE INDEX IF NOT EXISTS idx_report_jobs_created_id
                ON report_jobs(created_at DESC, id DESC)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_report_jobs_status_created_id
                ON report_jobs(status, created_at DESC, id DESC)
                """
            )
            connection.execute("COMMIT")

    @staticmethod
    def _row(row: sqlite3.Row | None) -> ReportJob | None:
        if row is None:
            return None
        return ReportJob(
            id=row["id"],
            status=JobStatus(row["status"]),
            request=json.loads(row["request_json"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            request_fingerprint=row["request_fingerprint"],
            idempotency_key_digest=row["idempotency_key_digest"],
            error=row["error"],
            artifact_dir=row["artifact_dir"],
        )

    @staticmethod
    def _request_json(request: dict[str, Any]) -> str:
        """Serialize one validated report request for durable storage."""
        return json.dumps(request, ensure_ascii=False, default=str)

    def create(self, request: dict[str, Any]) -> ReportJob:
        """Create and return one queued job containing a JSON-serializable request."""
        now = datetime.now(UTC)
        fingerprint = request_fingerprint(request)
        job = ReportJob(
            id=str(uuid.uuid4()),
            status=JobStatus.QUEUED,
            request=request,
            created_at=now,
            updated_at=now,
            request_fingerprint=fingerprint,
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO report_jobs(
                    id,status,request_json,request_fingerprint,
                    idempotency_key_digest,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?)
                """,
                (
                    job.id,
                    job.status.value,
                    self._request_json(request),
                    fingerprint,
                    None,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )
        return job

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
            row = connection.execute(
                "SELECT * FROM report_jobs WHERE idempotency_key_digest=?",
                (idempotency_key_digest,),
            ).fetchone()
            if row is not None:
                existing = self._row(row)
                assert existing is not None
                if existing.request_fingerprint != fingerprint:
                    raise IdempotencyKeyReuseError(
                        "Idempotency-Key is already used with a different payload"
                    )
                connection.execute("COMMIT")
                return existing, True

            now = datetime.now(UTC)
            job = ReportJob(
                id=str(uuid.uuid4()),
                status=JobStatus.QUEUED,
                request=request,
                created_at=now,
                updated_at=now,
                request_fingerprint=fingerprint,
                idempotency_key_digest=idempotency_key_digest,
            )
            connection.execute(
                """
                INSERT INTO report_jobs(
                    id,status,request_json,request_fingerprint,
                    idempotency_key_digest,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?)
                """,
                (
                    job.id,
                    job.status.value,
                    self._request_json(request),
                    fingerprint,
                    idempotency_key_digest,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )
            connection.execute("COMMIT")
        return job, False

    def get(self, job_id: str) -> ReportJob | None:
        """Return one job by UUID or ``None`` when no matching row exists."""
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM report_jobs WHERE id=?", (job_id,)).fetchone()
        return self._row(row)

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
        clauses: list[str] = []
        parameters: list[str | int] = []
        if status is not None:
            clauses.append("status=?")
            parameters.append(status.value)
        if cursor is not None:
            created_at, job_id = decode_history_cursor(cursor)
            boundary = created_at.isoformat()
            clauses.append("(created_at < ? OR (created_at = ? AND id < ?))")
            parameters.extend((boundary, boundary, job_id))
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        parameters.append(limit + 1)
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT * FROM report_jobs{where} ORDER BY created_at DESC, id DESC LIMIT ?",
                parameters,
            ).fetchall()
        has_more = len(rows) > limit
        jobs = [self._row(row) for row in rows[:limit]]
        page = [job for job in jobs if job is not None]
        next_cursor = None
        if has_more and page:
            last = page[-1]
            next_cursor = encode_history_cursor(last.created_at, last.id)
        return page, next_cursor

    def claim_next(self) -> ReportJob | None:
        """Atomically claim the oldest queued job for a worker."""
        now = datetime.now(UTC).isoformat()
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT id FROM report_jobs WHERE status=? ORDER BY created_at LIMIT 1",
                (JobStatus.QUEUED.value,),
            ).fetchone()
            if row is None:
                connection.execute("COMMIT")
                return None
            cursor = connection.execute(
                "UPDATE report_jobs SET status=?, updated_at=? WHERE id=? AND status=?",
                (JobStatus.RUNNING.value, now, row["id"], JobStatus.QUEUED.value),
            )
            connection.execute("COMMIT")
            if cursor.rowcount != 1:
                return None
        return self.get(row["id"])

    def finish(self, job_id: str, artifact_dir: Path) -> ReportJob:
        """Mark a job completed and record its published artifact directory."""
        return self._transition(job_id, JobStatus.COMPLETED, artifact_dir=str(artifact_dir))

    def fail(self, job_id: str, error: str, *, quality: bool = False) -> ReportJob:
        """Mark a job failed, optionally distinguishing deterministic quality failure."""
        status = JobStatus.QUALITY_FAILED if quality else JobStatus.FAILED
        return self._transition(job_id, status, error=error[:4000])

    def _transition(
        self,
        job_id: str,
        status: JobStatus,
        *,
        error: str | None = None,
        artifact_dir: str | None = None,
    ) -> ReportJob:
        now = datetime.now(UTC).isoformat()
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE report_jobs SET status=?,updated_at=?,error=?,artifact_dir=? WHERE id=?",
                (status.value, now, error, artifact_dir, job_id),
            )
        if cursor.rowcount != 1:
            raise KeyError(f"Unknown report job: {job_id}")
        result = self.get(job_id)
        if result is None:
            raise KeyError(f"Unknown report job after transition: {job_id}")
        return result

    def delete(self, job_id: str) -> bool:
        """Delete one terminal job and report whether a row was removed."""
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM report_jobs WHERE id=? AND status IN (?,?,?)",
                (
                    job_id,
                    JobStatus.COMPLETED.value,
                    JobStatus.FAILED.value,
                    JobStatus.QUALITY_FAILED.value,
                ),
            )
        return cursor.rowcount == 1

    def purge(self, retention_days: int) -> list[str]:
        """Delete expired terminal rows and return their job UUIDs for artifact cleanup."""
        cutoff = (datetime.now(UTC) - timedelta(days=retention_days)).isoformat()
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id FROM report_jobs WHERE updated_at < ? AND status IN (?,?,?)",
                (
                    cutoff,
                    JobStatus.COMPLETED.value,
                    JobStatus.FAILED.value,
                    JobStatus.QUALITY_FAILED.value,
                ),
            ).fetchall()
            ids = [row["id"] for row in rows]
            connection.executemany("DELETE FROM report_jobs WHERE id=?", ((job_id,) for job_id in ids))
        return ids
