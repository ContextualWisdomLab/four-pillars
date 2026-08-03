from __future__ import annotations

from pathlib import Path

from four_pillars.jobs import JobStore
from four_pillars.models import JobStatus


def test_job_lifecycle_is_durable(tmp_path: Path) -> None:
    path = tmp_path / "jobs.sqlite3"
    store = JobStore(path)
    queued = store.create({"subject_name": "테스트"})
    assert queued.status is JobStatus.QUEUED

    reopened = JobStore(path)
    assert reopened.get(queued.id).status is JobStatus.QUEUED

    running = reopened.claim_next()
    assert running is not None
    assert running.id == queued.id
    assert running.status is JobStatus.RUNNING
    assert reopened.claim_next() is None

    artifact_dir = tmp_path / queued.id
    artifact_dir.mkdir()
    completed = reopened.finish(queued.id, artifact_dir)
    assert completed.status is JobStatus.COMPLETED
    assert completed.artifact_dir == str(artifact_dir)
    assert reopened.delete(queued.id)
    assert reopened.get(queued.id) is None


def test_only_terminal_jobs_can_be_deleted(tmp_path: Path) -> None:
    store = JobStore(tmp_path / "jobs.sqlite3")
    queued = store.create({"subject_name": "테스트"})
    assert not store.delete(queued.id)
    store.claim_next()
    failed = store.fail(queued.id, "NIM unavailable")
    assert failed.status is JobStatus.FAILED
    assert store.delete(queued.id)


def test_quality_failure_has_distinct_status(tmp_path: Path) -> None:
    store = JobStore(tmp_path / "jobs.sqlite3")
    job = store.create({"subject_name": "테스트"})
    store.claim_next()
    failed = store.fail(job.id, "relationship warning only", quality=True)
    assert failed.status is JobStatus.QUALITY_FAILED
