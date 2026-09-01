"""Regression tests for semantic report-job domain and SQLite identifiers."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from four_pillars.jobs import JobStore
from four_pillars.models import JobStatus, ReportJob


LEGACY_JOB_ID = "33333333-3333-4333-8333-333333333333"


def _create_legacy_report_job_database(database_path: Path) -> None:
    """Create the pre-rename report_jobs schema with one durable row."""
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE report_jobs (
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
        connection.execute(
            """
            INSERT INTO report_jobs(
                id,status,request_json,request_fingerprint,
                idempotency_key_digest,created_at,updated_at,error,artifact_dir
            ) VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (
                LEGACY_JOB_ID,
                JobStatus.FAILED.value,
                json.dumps({"subject_name": "legacy"}),
                "legacy-fingerprint",
                None,
                "2026-09-01T00:00:00+00:00",
                "2026-09-01T00:01:00+00:00",
                "legacy failure",
                None,
            ),
        )


def test_report_job_domain_model_uses_specific_owned_field_names() -> None:
    """Keep generic legacy keys out of the organization-owned domain model."""
    assert set(ReportJob.model_fields) == {
        "report_job_id",
        "job_status",
        "report_request",
        "created_at",
        "updated_at",
        "request_fingerprint",
        "idempotency_key_digest",
        "job_error_message",
        "artifact_dir",
    }
    assert {"id", "status", "request", "error"}.isdisjoint(ReportJob.model_fields)


def test_job_store_migrates_legacy_generic_columns_without_losing_rows(tmp_path: Path) -> None:
    """Rename legacy persisted identifiers transactionally and preserve durable data."""
    database_path = tmp_path / "jobs.sqlite3"
    _create_legacy_report_job_database(database_path)

    report_job_store = JobStore(database_path)

    with sqlite3.connect(database_path) as connection:
        schema_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(report_jobs)").fetchall()
        }
        index_names = {
            row[1] for row in connection.execute("PRAGMA index_list(report_jobs)").fetchall()
        }

    assert {"report_job_id", "job_status", "job_error_message"} <= schema_columns
    assert {"id", "status", "error"}.isdisjoint(schema_columns)
    assert "idx_report_jobs_job_status_created_at" in index_names
    assert "idx_report_jobs_created_at_job_id" in index_names
    assert "idx_report_jobs_job_status_created_at_job_id" in index_names
    assert {
        "idx_report_jobs_status_created",
        "idx_report_jobs_created_id",
        "idx_report_jobs_status_created_id",
    }.isdisjoint(index_names)

    migrated_job = report_job_store.get(LEGACY_JOB_ID)
    assert migrated_job is not None
    assert migrated_job.report_job_id == LEGACY_JOB_ID
    assert migrated_job.job_status is JobStatus.FAILED
    assert migrated_job.report_request == {"subject_name": "legacy"}
    assert migrated_job.job_error_message == "legacy failure"
