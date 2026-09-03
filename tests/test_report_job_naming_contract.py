from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from four_pillars.jobs import JobStore
from four_pillars.models import JobStatus, ReportJob


SEMANTIC_REPORT_JOB_COLUMNS = {
    "report_job_id",
    "job_status",
    "report_request_json",
    "request_fingerprint",
    "idempotency_key_digest",
    "job_created_at",
    "job_updated_at",
    "failure_message",
    "artifact_directory",
}
LEGACY_GENERIC_COLUMNS = {
    "id",
    "status",
    "request_json",
    "created_at",
    "updated_at",
    "error",
    "artifact_dir",
}
SEMANTIC_REPORT_JOB_INDEXES = {
    "idx_report_jobs_job_status_job_created_at",
    "idx_report_jobs_idempotency_key_digest",
    "idx_report_jobs_job_created_at_report_job_id",
    "idx_report_jobs_job_status_job_created_at_report_job_id",
}
LEGACY_GENERIC_INDEXES = {
    "idx_report_jobs_status_created",
    "idx_report_jobs_created_id",
    "idx_report_jobs_status_created_id",
}


def _legacy_report_job_database(database_path: Path) -> str:
    report_job_id = "11111111-1111-4111-8111-111111111111"
    current_timestamp = datetime(2026, 9, 2, 0, 0, tzinfo=UTC).isoformat()
    report_request = {"subject_name": "legacy"}
    database_connection = sqlite3.connect(database_path)
    database_connection.execute(
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
    database_connection.execute(
        """
        INSERT INTO report_jobs(
            id,status,request_json,request_fingerprint,
            idempotency_key_digest,created_at,updated_at,error,artifact_dir
        ) VALUES(?,?,?,?,?,?,?,?,?)
        """,
        (
            report_job_id,
            JobStatus.FAILED.value,
            json.dumps(report_request),
            "legacy-fingerprint",
            None,
            current_timestamp,
            current_timestamp,
            "legacy failure",
            "/tmp/legacy-artifacts",
        ),
    )
    database_connection.execute(
        "CREATE INDEX idx_report_jobs_status_created ON report_jobs(status, created_at)"
    )
    database_connection.execute(
        "CREATE INDEX idx_report_jobs_created_id ON report_jobs(created_at DESC, id DESC)"
    )
    database_connection.execute(
        "CREATE INDEX idx_report_jobs_status_created_id ON report_jobs(status, created_at DESC, id DESC)"
    )
    database_connection.commit()
    database_connection.close()
    return report_job_id


def _schema_identifiers(database_path: Path) -> tuple[set[str], set[str]]:
    database_connection = sqlite3.connect(database_path)
    column_names = {
        column_row[1]
        for column_row in database_connection.execute("PRAGMA table_info(report_jobs)")
    }
    index_names = {
        index_row[1]
        for index_row in database_connection.execute("PRAGMA index_list(report_jobs)")
        if not index_row[1].startswith("sqlite_autoindex")
    }
    database_connection.close()
    return column_names, index_names


def test_report_job_model_owns_semantic_fields_with_legacy_aliases() -> None:
    current_timestamp = datetime(2026, 9, 2, 0, 0, tzinfo=UTC)
    semantic_report_job = ReportJob(
        report_job_id="22222222-2222-4222-8222-222222222222",
        job_status=JobStatus.QUEUED,
        report_request={"subject_name": "semantic"},
        job_created_at=current_timestamp,
        job_updated_at=current_timestamp,
        request_fingerprint="semantic-fingerprint",
        failure_message=None,
        artifact_directory=None,
    )

    assert {
        "report_job_id",
        "job_status",
        "report_request",
        "job_created_at",
        "job_updated_at",
        "request_fingerprint",
        "idempotency_key_digest",
        "failure_message",
        "artifact_directory",
    } == set(ReportJob.model_fields)
    assert semantic_report_job.report_job_id == "22222222-2222-4222-8222-222222222222"
    assert semantic_report_job.job_status is JobStatus.QUEUED
    assert semantic_report_job.report_request == {"subject_name": "semantic"}

    legacy_report_job = ReportJob(
        id="33333333-3333-4333-8333-333333333333",
        status=JobStatus.FAILED,
        request={"subject_name": "legacy-api"},
        created_at=current_timestamp,
        updated_at=current_timestamp,
        request_fingerprint="legacy-api-fingerprint",
        error="legacy error",
        artifact_dir="/tmp/legacy-api-artifacts",
    )
    assert legacy_report_job.report_job_id == "33333333-3333-4333-8333-333333333333"
    assert legacy_report_job.job_status is JobStatus.FAILED
    assert legacy_report_job.failure_message == "legacy error"
    assert legacy_report_job.artifact_directory == "/tmp/legacy-api-artifacts"
    assert legacy_report_job.id == legacy_report_job.report_job_id
    assert legacy_report_job.status is legacy_report_job.job_status
    assert legacy_report_job.request == legacy_report_job.report_request
    assert legacy_report_job.error == legacy_report_job.failure_message
    assert legacy_report_job.artifact_dir == legacy_report_job.artifact_directory

    legacy_wire_shape = legacy_report_job.model_dump(by_alias=True)
    assert legacy_wire_shape["id"] == legacy_report_job.report_job_id
    assert legacy_wire_shape["status"] is JobStatus.FAILED
    assert legacy_wire_shape["request"] == {"subject_name": "legacy-api"}
    assert legacy_wire_shape["error"] == "legacy error"
    assert legacy_wire_shape["artifact_dir"] == "/tmp/legacy-api-artifacts"


def test_job_store_migrates_legacy_generic_schema_without_data_loss(tmp_path: Path) -> None:
    database_path = tmp_path / "legacy-jobs.sqlite3"
    report_job_id = _legacy_report_job_database(database_path)

    report_job_store = JobStore(database_path)
    column_names, index_names = _schema_identifiers(database_path)

    assert SEMANTIC_REPORT_JOB_COLUMNS == column_names
    assert LEGACY_GENERIC_COLUMNS.isdisjoint(column_names)
    assert SEMANTIC_REPORT_JOB_INDEXES == index_names
    assert LEGACY_GENERIC_INDEXES.isdisjoint(index_names)

    migrated_report_job = report_job_store.get(report_job_id)
    assert migrated_report_job is not None
    assert migrated_report_job.report_job_id == report_job_id
    assert migrated_report_job.job_status is JobStatus.FAILED
    assert migrated_report_job.report_request == {"subject_name": "legacy"}
    assert migrated_report_job.failure_message == "legacy failure"
    assert migrated_report_job.artifact_directory == "/tmp/legacy-artifacts"


def test_new_job_store_creates_only_semantic_database_identifiers(tmp_path: Path) -> None:
    database_path = tmp_path / "semantic-jobs.sqlite3"
    report_job_store = JobStore(database_path)
    created_report_job = report_job_store.create({"subject_name": "semantic"})

    column_names, index_names = _schema_identifiers(database_path)

    assert SEMANTIC_REPORT_JOB_COLUMNS == column_names
    assert LEGACY_GENERIC_COLUMNS.isdisjoint(column_names)
    assert SEMANTIC_REPORT_JOB_INDEXES == index_names
    assert LEGACY_GENERIC_INDEXES.isdisjoint(index_names)
    assert report_job_store.get(created_report_job.report_job_id) == created_report_job
