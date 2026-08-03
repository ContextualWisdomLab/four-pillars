from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from four_pillars.jobs import JobStore
from four_pillars.models import BirthInput, JobStatus
from four_pillars.quality import QualityIssue, ReportQualityError
from four_pillars.service import ReportRequest, ReportService, default_request
from four_pillars.settings import Settings


def request() -> ReportRequest:
    return ReportRequest(
        subject_name="테스트",
        birth=BirthInput(birth=datetime(1990, 6, 15, 8, 30), timezone="Asia/Seoul"),
        annual_year=2026,
        monthly_year=2026,
        monthly_month=8,
    )


class FailingService(ReportService):
    async def generate(self, request: ReportRequest):
        raise RuntimeError("provider unavailable")


class QualityFailingService(ReportService):
    async def generate(self, request: ReportRequest):
        raise ReportQualityError([QualityIssue("copy", "bad copy", "$")])


def configured(tmp_path: Path, service_type):
    settings = Settings(
        artifact_dir=tmp_path / "artifacts",
        database_url=f"sqlite:///{tmp_path / 'jobs.sqlite3'}",
    )
    return service_type(settings, JobStore(settings.sqlite_path))


@pytest.mark.asyncio
async def test_provider_exception_marks_job_failed_and_removes_temp_directory(tmp_path: Path) -> None:
    service = configured(tmp_path, FailingService)
    queued = service.enqueue(request())
    result = await service.process_next()
    assert result is not None
    assert result.status is JobStatus.FAILED
    assert "provider unavailable" in result.error
    assert not (service.settings.artifact_dir / f".{queued.id}.tmp").exists()


@pytest.mark.asyncio
async def test_quality_exception_has_quality_failed_status(tmp_path: Path) -> None:
    service = configured(tmp_path, QualityFailingService)
    service.enqueue(request())
    result = await service.process_next()
    assert result is not None
    assert result.status is JobStatus.QUALITY_FAILED


def test_default_request_uses_current_year_and_month() -> None:
    birth = BirthInput(birth=datetime(1990, 6, 15, 8, 30), timezone="Asia/Seoul")
    created = default_request("테스트", birth)
    now = datetime.now()
    assert created.annual_year == now.year
    assert created.monthly_year == now.year
    assert created.monthly_month == now.month
