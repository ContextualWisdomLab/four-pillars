"""Verify standalone defaults and replaceable service ports for MSA integrations."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from test_quality import valid_report

from four_pillars.adapters import FilesystemArtifactPublisher, NimReportInterpreter
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
from four_pillars.ports import (
    ArtifactPublisher,
    IdempotentReportJobRepository,
    ReportInterpreter,
    ReportJobHistoryRepository,
    ReportJobRepository,
)
from four_pillars.service import (
    HistoryNotSupportedError,
    IdempotencyNotSupportedError,
    ReportRequest,
    ReportService,
)
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


class LegacyRepository:
    """Forward the original repository contract without optional capabilities."""

    def __init__(self, delegate: JobStore) -> None:
        self.delegate = delegate

    def create(self, request: dict[str, Any]) -> ReportJob:
        """Create one queued job through the legacy contract."""
        return self.delegate.create(request)

    def get(self, job_id: str) -> ReportJob | None:
        """Return one stored legacy job."""
        return self.delegate.get(job_id)

    def claim_next(self) -> ReportJob | None:
        """Claim the next legacy job."""
        return self.delegate.claim_next()

    def finish(self, job_id: str, artifact_dir: Path) -> ReportJob:
        """Finish one legacy job."""
        return self.delegate.finish(job_id, artifact_dir)

    def fail(self, job_id: str, error: str, *, quality: bool = False) -> ReportJob:
        """Fail one legacy job."""
        return self.delegate.fail(job_id, error, quality=quality)

    def delete(self, job_id: str) -> bool:
        """Delete one terminal legacy job."""
        return self.delegate.delete(job_id)

    def purge(self, retention_days: int) -> list[str]:
        """Purge expired legacy jobs."""
        return self.delegate.purge(retention_days)


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
    assert isinstance(store, IdempotentReportJobRepository)
    assert isinstance(store, ReportJobHistoryRepository)
    assert isinstance(interpreter, ReportInterpreter)
    assert isinstance(publisher, ArtifactPublisher)


def test_optional_capabilities_preserve_existing_repository_adapters(tmp_path: Path) -> None:
    """Keep legacy adapters usable and fail optional operations explicitly."""
    configured = settings(tmp_path)
    repository = LegacyRepository(JobStore(configured.sqlite_path))
    service = ReportService(configured, store=repository)

    assert isinstance(repository, ReportJobRepository)
    assert not isinstance(repository, IdempotentReportJobRepository)
    assert not isinstance(repository, ReportJobHistoryRepository)
    assert service.enqueue(request()).status is JobStatus.QUEUED
    with pytest.raises(IdempotencyNotSupportedError, match="idempotent"):
        service.enqueue_idempotent(request(), "0" * 64)
    with pytest.raises(HistoryNotSupportedError, match="history"):
        service.list_jobs(limit=1)


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
    assert completed.artifact_dir is not None
    assert Path(completed.artifact_dir).name == queued.id
    assert service.available_artifacts(queued.id) == ["report.json"]
    assert len(interpreter.calls) == 1
    assert interpreter.calls[0]["subject_name"] == "모듈 사용자"
    assert interpreter.calls[0]["user_context"] == "MSA adapter contract"
    assert interpreter.calls[0]["chart"].fingerprint
    assert len(publisher.calls) == 1
    assert publisher.calls[0]["report"].calculation_fingerprint == interpreter.calls[0]["chart"].fingerprint
    assert publisher.calls[0]["directory"].name == f".{queued.id}.tmp"
