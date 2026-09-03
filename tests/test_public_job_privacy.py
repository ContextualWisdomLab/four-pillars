"""Protect the public report-job projection from provider and request diagnostics."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from four_pillars.api import _job_view
from four_pillars.jobs import JobStore
from four_pillars.models import BirthInput, JobStatus
from four_pillars.service import ReportRequest, ReportService
from four_pillars.settings import Settings


def _service(tmp_path: Path) -> ReportService:
    """Return one isolated standalone service for public-view privacy tests."""
    settings = Settings(
        artifact_dir=tmp_path / "artifacts",
        database_url=f"sqlite:///{tmp_path / 'jobs.sqlite3'}",
    )
    return ReportService(settings, JobStore(settings.sqlite_path))


def test_public_failed_job_does_not_echo_internal_provider_diagnostics(tmp_path: Path) -> None:
    """Expose a stable public failure message instead of stored provider/request text."""
    service = _service(tmp_path)
    request = ReportRequest(
        subject_name="민감한 이름",
        birth=BirthInput(birth=datetime(1990, 6, 15, 8, 30), timezone="Asia/Seoul"),
        annual_year=2026,
        monthly_year=2026,
        monthly_month=8,
        user_context="내부 업무와 관계 메모",
    )
    job = service.store.create(request.model_dump(mode="json"))
    service.store.fail(
        job.id,
        "NimError: provider body mentioned 민감한 이름 and NVIDIA_NIM_API_KEY=secret-shaped-value",
    )
    stored = service.store.get(job.id)
    assert stored is not None and stored.status is JobStatus.FAILED

    public = _job_view(stored, service)

    assert public.error == "Report generation failed."
    assert "민감한 이름" not in public.model_dump_json()
    assert "NVIDIA_NIM_API_KEY" not in public.model_dump_json()


def test_public_quality_failure_has_a_distinct_non_sensitive_message(tmp_path: Path) -> None:
    """Keep quality failures actionable without echoing generated report prose."""
    service = _service(tmp_path)
    job = service.store.create({"subject_name": "quality"})
    service.store.fail(job.id, "ReportQualityError: generated private prose", quality=True)
    stored = service.store.get(job.id)
    assert stored is not None and stored.status is JobStatus.QUALITY_FAILED

    public = _job_view(stored, service)

    assert public.error == "Report quality validation failed."


def test_public_non_failure_states_do_not_expose_stored_error_text(tmp_path: Path) -> None:
    """Return no public error for non-failure lifecycle states."""
    service = _service(tmp_path)
    job = service.store.create({"subject_name": "queued"})

    public = _job_view(job.model_copy(update={"error": "unexpected internal text"}), service)

    assert public.error is None
