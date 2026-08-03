from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from four_pillars.analysis import GeneratedReport
from four_pillars.jobs import JobStore
from four_pillars.models import JobStatus, PracticalSkill, ReportDocument, ReportSection
from four_pillars.service import ReportRequest, ReportService, calculate_bundle
from four_pillars.settings import Settings
from four_pillars.models import BirthInput, Gender


REQUIRED = ("natal", "daewoon", "annual", "monthly", "work", "money", "relationships", "daily_rhythm")


def request() -> ReportRequest:
    return ReportRequest(
        subject_name="최혜지",
        birth=BirthInput(
            birth=datetime(1990, 6, 15, 8, 30),
            timezone="Asia/Seoul",
            gender=Gender.FEMALE,
        ),
        annual_year=2026,
        monthly_year=2026,
        monthly_month=8,
    )


def report(fingerprint: str) -> ReportDocument:
    sections = {
        key: ReportSection(
            title=key,
            summary="혜지 님은 현실 조건을 확인합니다.",
            opportunities=["신뢰와 협력을 높일 수 있습니다."],
            cautions=["결정을 서두르지 않습니다."],
            actions=["기한과 지원을 기록합니다."],
        )
        for key in REQUIRED
    }
    return ReportDocument(
        subject_name="최혜지",
        title="최혜지 사주 보고서",
        executive_summary="혜지 님은 책임 범위와 지원 조건을 확인합니다.",
        calculation_fingerprint=fingerprint,
        sections=sections,
        practical_skills=[
            PracticalSkill(
                name="주간 검토",
                purpose="일정을 확인합니다.",
                steps=["캘린더를 엽니다.", "완충 시간을 확보합니다."],
                when_to_use="매주 사용합니다.",
            )
        ],
        disclaimer="이 보고서는 전통 명리학의 상징 자료입니다. 의학·법률·재정 판단은 실제 정보와 전문가 의견을 우선합니다.",
        generated_at=datetime.now(UTC),
        model="fake-nim",
        prompt_versions={"synthesis": "1.0.0"},
    )


class FakeService(ReportService):
    async def generate(self, request: ReportRequest):
        bundle = calculate_bundle(request)
        return bundle, GeneratedReport(report=report(bundle.chart.fingerprint), traces={})


@pytest.mark.asyncio
async def test_worker_processes_job_and_publishes_complete_artifacts(tmp_path: Path) -> None:
    settings = Settings(
        artifact_dir=tmp_path / "artifacts",
        database_url=f"sqlite:///{tmp_path / 'jobs.sqlite3'}",
    )
    service = FakeService(settings, JobStore(settings.sqlite_path))
    queued = service.enqueue(request())
    completed = await service.process_next()
    assert completed is not None
    assert completed.id == queued.id
    assert completed.status is JobStatus.COMPLETED
    assert service.artifact(queued.id, "report.pdf").read_bytes().startswith(b"%PDF")
    assert service.artifact(queued.id, "manifest.json").is_file()
    with pytest.raises(ValueError):
        service.artifact(queued.id, "../../etc/passwd")


@pytest.mark.asyncio
async def test_process_next_returns_none_when_queue_is_empty(tmp_path: Path) -> None:
    settings = Settings(
        artifact_dir=tmp_path / "artifacts",
        database_url=f"sqlite:///{tmp_path / 'jobs.sqlite3'}",
    )
    service = FakeService(settings, JobStore(settings.sqlite_path))
    assert await service.process_next() is None
