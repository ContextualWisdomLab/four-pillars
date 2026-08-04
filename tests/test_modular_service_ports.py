"""Verify standalone defaults and replaceable service ports for MSA integrations."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from four_pillars.adapters import FilesystemArtifactPublisher, NimReportInterpreter
from four_pillars.ports import ArtifactPublisher, ReportInterpreter, ReportJobRepository
from test_quality import valid_report

from four_pillars.analysis import GeneratedReport
from four_pillars.jobs import JobStore
from four_pillars.models import (
    BirthInput,
    Chart,
    DaewoonResult,
    Gender,
    JobStatus,
    LuckSnapshot,
    ReportDocument,
    ReportJob,
)
from four_pillars.service import ReportRequest, ReportService
from four_pillars.settings import Settings


class RecordingInterpreter:
    """Return a deterministic fixture while recording the immutable evidence call."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def generate(
        self,
        *,
        subject_name: str,
        chart: Chart,
        daewoon: DaewoonResult,
        annual: LuckSnapshot,
        monthly: LuckSnapshot,
        user_context: str,
    ) -> GeneratedReport:
        self.calls.append(
            {
                "subject_name": subject_name,
                "chart": chart,
                "daewoon": daewoon,
                "annual": annual,
                "monthly": monthly,
                "user_context": user_context,
            }
        )
        report = valid_report().model_copy(
            update={
                "subject_name": subject_name,
                "title": f"{subject_name} 사주 보고서",
                "calculation_fingerprint": chart.fingerprint,
            }
        )
        return GeneratedReport(report=report, traces={"recording": {"attempts": 0}})


class RecordingPublisher:
    """Publish one allow-listed artifact and record the adapter invocation."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def publish(
        self,
        directory: Path,
        *,
        report: ReportDocument,
        chart: Chart,
        daewoon: DaewoonResult,
        annual: LuckSnapshot,
        monthly: LuckSnapshot,
        traces: dict[str, dict[str, Any]],
    ) -> dict[str, str]:
        self.calls.append(
            {
                "directory": directory,
                "report": report,
                "chart": chart,
                "daewoon": daewoon,
                "annual": annual,
                "monthly": monthly,
                "traces": traces,
            }
        )
        directory.mkdir(parents=True, exist_ok=False)
        (directory / "report.json").write_text(report.model_dump_json(), encoding="utf-8")
        return {"report.json": "fixture-digest"}


def request() -> ReportRequest:
    """Return a complete report request with integration context."""
    return ReportRequest(
        subject_name="모듈 사용자",
        birth=BirthInput(
            birth=datetime(1990, 6, 15, 8, 30),
            timezone="Asia/Seoul",
            gender=Gender.FEMALE,
        ),
        annual_year=2026,
        monthly_year=2026,
        monthly_month=8,
        user_context="MSA adapter contract",
    )


def settings(tmp_path: Path) -> Settings:
    """Return isolated storage configuration for one service test."""
    return Settings(
        artifact_dir=tmp_path / "artifacts",
        database_url=f"sqlite:///{tmp_path / 'report_jobs.sqlite3'}",
    )


def test_default_service_keeps_the_standalone_adapters(tmp_path: Path) -> None:
    """Construct SQLite, hosted NIM, and filesystem adapters when none are injected."""
    service = ReportService(settings(tmp_path))

    assert isinstance(service.store, JobStore)
    assert isinstance(service.interpreter, NimReportInterpreter)
    assert isinstance(service.publisher, FilesystemArtifactPublisher)


def test_concrete_adapters_satisfy_runtime_port_contracts(tmp_path: Path) -> None:
    """Expose structural ports that platform integrations can replace independently."""
    store = JobStore(tmp_path / "report_jobs.sqlite3")
    interpreter = RecordingInterpreter()
    publisher = RecordingPublisher()

    assert isinstance(store, ReportJobRepository)
    assert isinstance(interpreter, ReportInterpreter)
    assert isinstance(publisher, ArtifactPublisher)


@pytest.mark.asyncio
async def test_injected_ports_process_a_job_without_nim_or_default_filesystem_publisher(
    tmp_path: Path,
) -> None:
    """Run application orchestration with independently supplied repository and adapters."""
    configured = settings(tmp_path)
    store = JobStore(configured.sqlite_path)
    interpreter = RecordingInterpreter()
    publisher = RecordingPublisher()
    service = ReportService(
        configured,
        store=store,
        interpreter=interpreter,
        publisher=publisher,
    )

    queued = service.enqueue(request())
    completed = await service.process_next()

    assert isinstance(completed, ReportJob)
    assert completed.id == queued.id
    assert completed.status is JobStatus.COMPLETED
    assert service.available_artifacts(queued.id) == ["report.json"]
    assert len(interpreter.calls) == 1
    assert interpreter.calls[0]["subject_name"] == "모듈 사용자"
    assert interpreter.calls[0]["user_context"] == "MSA adapter contract"
    assert interpreter.calls[0]["chart"].fingerprint
    assert len(publisher.calls) == 1
    assert publisher.calls[0]["report"].calculation_fingerprint == interpreter.calls[0]["chart"].fingerprint
    assert publisher.calls[0]["directory"].name == queued.id
