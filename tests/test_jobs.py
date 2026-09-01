from __future__ import annotations

from pathlib import Path

from four_pillars.jobs import JobStore
from four_pillars.models import JobStatus


def test_job_lifecycle_is_durable(tmp_path: Path) -> None:
    database_path = tmp_path / "jobs.sqlite3"
    report_job_store = JobStore(database_path)
    queued_job = report_job_store.create({"subject_name": "테스트"})
    assert queued_job.job_status is JobStatus.QUEUED

    reopened_store = JobStore(database_path)
    reopened_job = reopened_store.get(queued_job.report_job_id)
    assert reopened_job is not None
    assert reopened_job.job_status is JobStatus.QUEUED

    running_job = reopened_store.claim_next()
    assert running_job is not None
    assert running_job.report_job_id == queued_job.report_job_id
    assert running_job.job_status is JobStatus.RUNNING
    assert reopened_store.claim_next() is None

    artifact_dir = tmp_path / queued_job.report_job_id
    artifact_dir.mkdir()
    completed_job = reopened_store.finish(queued_job.report_job_id, artifact_dir)
    assert completed_job.job_status is JobStatus.COMPLETED
    assert completed_job.artifact_dir == str(artifact_dir)
    assert reopened_store.delete(queued_job.report_job_id)
    assert reopened_store.get(queued_job.report_job_id) is None


def test_only_terminal_jobs_can_be_deleted(tmp_path: Path) -> None:
    report_job_store = JobStore(tmp_path / "jobs.sqlite3")
    queued_job = report_job_store.create({"subject_name": "테스트"})
    assert not report_job_store.delete(queued_job.report_job_id)
    report_job_store.claim_next()
    failed_job = report_job_store.fail(queued_job.report_job_id, "NIM unavailable")
    assert failed_job.job_status is JobStatus.FAILED
    assert report_job_store.delete(queued_job.report_job_id)


def test_quality_failure_has_distinct_status(tmp_path: Path) -> None:
    report_job_store = JobStore(tmp_path / "jobs.sqlite3")
    queued_job = report_job_store.create({"subject_name": "테스트"})
    report_job_store.claim_next()
    failed_job = report_job_store.fail(
        queued_job.report_job_id,
        "relationship warning only",
        quality=True,
    )
    assert failed_job.job_status is JobStatus.QUALITY_FAILED
