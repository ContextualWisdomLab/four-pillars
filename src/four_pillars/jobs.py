from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from .models import JobStatus, ReportJob


class JobStore:
    def __init__(self, database_path: Path) -> None:
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
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS report_jobs (
                    id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    request_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    error TEXT,
                    artifact_dir TEXT
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_report_jobs_status_created ON report_jobs(status, created_at)"
            )

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
            error=row["error"],
            artifact_dir=row["artifact_dir"],
        )

    def create(self, request: dict[str, Any]) -> ReportJob:
        now = datetime.now(UTC)
        job = ReportJob(
            id=str(uuid.uuid4()),
            status=JobStatus.QUEUED,
            request=request,
            created_at=now,
            updated_at=now,
        )
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO report_jobs(id,status,request_json,created_at,updated_at) VALUES(?,?,?,?,?)",
                (
                    job.id,
                    job.status.value,
                    json.dumps(request, ensure_ascii=False, default=str),
                    now.isoformat(),
                    now.isoformat(),
                ),
            )
        return job

    def get(self, job_id: str) -> ReportJob | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM report_jobs WHERE id=?", (job_id,)).fetchone()
        return self._row(row)

    def claim_next(self) -> ReportJob | None:
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
        return self._transition(job_id, JobStatus.COMPLETED, artifact_dir=str(artifact_dir))

    def fail(self, job_id: str, error: str, *, quality: bool = False) -> ReportJob:
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
