"""Coordinate calculation, interpretation, job processing, and artifact access."""

from __future__ import annotations

import asyncio
import shutil
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from .adapters import FilesystemArtifactPublisher, build_report_interpreter
from .analysis import GeneratedReport
from .calendar import calculate_chart
from .fortune import calculate_annual_luck, calculate_daewoon, calculate_monthly_luck
from .idempotency import request_fingerprint
from .jobs import JobStore
from .models import BirthInput, Chart, DaewoonResult, JobStatus, LuckSnapshot, ReportJob
from .ports import (
    ArtifactPublisher,
    IdempotentReportJobRepository,
    ReportInterpreter,
    ReportJobHistoryRepository,
    ReportJobRepository,
)
from .quality import ReportQualityError
from .settings import Settings

ARTIFACT_NAMES = frozenset(
    {
        "chart.json",
        "daewoon.json",
        "annual.json",
        "monthly.json",
        "report.json",
        "traces.json",
        "manifest.json",
        "report.html",
        "report.pdf",
    }
)


class IdempotencyNotSupportedError(RuntimeError):
    """Signal that an injected legacy repository lacks atomic keyed creation."""


class HistoryNotSupportedError(RuntimeError):
    """Signal that an injected legacy repository lacks history pagination."""


class ReportRequest(BaseModel):
    """Validated request for deterministic evidence and one generated report."""

    model_config = ConfigDict(extra="forbid")

    subject_name: str = Field(min_length=1, max_length=80)
    birth: BirthInput
    annual_year: int = Field(ge=1900, le=2200)
    monthly_year: int = Field(ge=1900, le=2200)
    monthly_month: int = Field(ge=1, le=12)
    user_context: str = Field(default="", max_length=4000)


class CalculationBundle(BaseModel):
    """Immutable natal, daewoon, annual, and monthly evidence for report generation."""

    chart: Chart
    daewoon: DaewoonResult
    annual: LuckSnapshot
    monthly: LuckSnapshot


def calculate_bundle(request: ReportRequest) -> CalculationBundle:
    """Calculate all deterministic evidence required by the report prompts."""
    chart = calculate_chart(request.birth)
    daewoon = calculate_daewoon(chart, request.birth.gender)
    annual = calculate_annual_luck(chart, request.annual_year)
    monthly = calculate_monthly_luck(chart, request.monthly_year, request.monthly_month)
    return CalculationBundle(chart=chart, daewoon=daewoon, annual=annual, monthly=monthly)


class ReportService:
    """Provide the application boundary for durable asynchronous report generation."""

    def __init__(
        self,
        settings: Settings,
        store: ReportJobRepository | None = None,
        interpreter: ReportInterpreter | None = None,
        publisher: ArtifactPublisher | None = None,
    ) -> None:
        """Create standalone defaults while permitting independent adapter injection."""
        self.settings = settings
        self.settings.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.store = store if store is not None else JobStore(settings.sqlite_path)
        self.interpreter = (
            interpreter
            if interpreter is not None
            else build_report_interpreter(settings)
        )
        self.publisher = (
            publisher if publisher is not None else FilesystemArtifactPublisher()
        )

    def enqueue(self, request: ReportRequest) -> ReportJob:
        """Persist one validated report request as a queued job."""
        return self.store.create(request.model_dump(mode="json"))

    def enqueue_idempotent(
        self,
        request: ReportRequest,
        idempotency_key_digest: str,
    ) -> tuple[ReportJob, bool]:
        """Persist or replay through the repository's optional atomic capability.

        Raises:
            IdempotencyNotSupportedError: When an injected legacy repository does
                not implement ``IdempotentReportJobRepository``.
        """
        repository = self.store
        if not isinstance(repository, IdempotentReportJobRepository):
            raise IdempotencyNotSupportedError(
                "The configured report repository does not support idempotent creation"
            )
        payload = request.model_dump(mode="json")
        return repository.create_idempotent(
            payload,
            idempotency_key_digest,
            request_fingerprint(payload),
        )

    def list_jobs(
        self,
        *,
        limit: int,
        cursor: str | None = None,
        status: JobStatus | None = None,
    ) -> tuple[list[ReportJob], str | None]:
        """Return one report-history page through the optional repository capability.

        Raises:
            HistoryNotSupportedError: When an injected legacy repository does not
                implement ``ReportJobHistoryRepository``.
        """
        repository = self.store
        if not isinstance(repository, ReportJobHistoryRepository):
            raise HistoryNotSupportedError(
                "The configured report repository does not support report history"
            )
        return repository.list_jobs(limit=limit, cursor=cursor, status=status)

    async def generate(
        self,
        request: ReportRequest,
    ) -> tuple[CalculationBundle, GeneratedReport]:
        """Calculate immutable evidence and invoke the configured interpretation port."""
        bundle = calculate_bundle(request)
        generated = await self.interpreter.generate(
            subject_name=request.subject_name,
            chart=bundle.chart,
            daewoon=bundle.daewoon,
            annual=bundle.annual,
            monthly=bundle.monthly,
            user_context=request.user_context,
        )
        return bundle, generated

    async def process(self, report_job: ReportJob) -> ReportJob:
        """Generate one claimed job and atomically publish or fail its artifacts."""
        report_request = ReportRequest.model_validate(report_job.report_request)
        temporary_artifact_dir = (
            self.settings.artifact_dir / f".{report_job.report_job_id}.tmp"
        )
        final_artifact_dir = self.settings.artifact_dir / report_job.report_job_id
        shutil.rmtree(temporary_artifact_dir, ignore_errors=True)
        shutil.rmtree(final_artifact_dir, ignore_errors=True)
        try:
            calculation_bundle, generated_report = await self.generate(report_request)
            self.publisher.publish(
                temporary_artifact_dir,
                report=generated_report.report,
                chart=calculation_bundle.chart,
                daewoon=calculation_bundle.daewoon,
                annual=calculation_bundle.annual,
                monthly=calculation_bundle.monthly,
                traces=generated_report.traces,
            )
            temporary_artifact_dir.replace(final_artifact_dir)
            return self.store.finish(report_job.report_job_id, final_artifact_dir)
        except ReportQualityError as exc:
            shutil.rmtree(temporary_artifact_dir, ignore_errors=True)
            return self.store.fail(
                report_job.report_job_id,
                str(exc),
                quality=True,
            )
        except Exception as exc:
            shutil.rmtree(temporary_artifact_dir, ignore_errors=True)
            return self.store.fail(
                report_job.report_job_id,
                f"{type(exc).__name__}: {exc}",
            )

    async def process_next(self) -> ReportJob | None:
        """Claim and process the next queued job, or return ``None`` when idle."""
        report_job = self.store.claim_next()
        if report_job is None:
            return None
        return await self.process(report_job)

    async def worker(self, poll_seconds: float = 1.0) -> None:
        """Continuously process queued jobs and sleep only while the queue is empty."""
        while True:
            processed_job = await self.process_next()
            if processed_job is None:
                await asyncio.sleep(poll_seconds)

    def artifact(self, job_id: str, filename: str) -> Path:
        """Resolve one allow-listed artifact while enforcing its configured UUID boundary."""
        if filename not in ARTIFACT_NAMES:
            raise ValueError("Unsupported artifact name")
        report_job = self.store.get(job_id)
        if report_job is None or report_job.artifact_dir is None:
            raise FileNotFoundError(job_id)
        configured_root = self.settings.artifact_dir.resolve()
        artifact_root = Path(report_job.artifact_dir).resolve()
        if (
            artifact_root.parent != configured_root
            or artifact_root.name != report_job.report_job_id
        ):
            raise FileNotFoundError(job_id)
        artifact_path = (artifact_root / filename).resolve()
        if artifact_path.parent != artifact_root or not artifact_path.is_file():
            raise FileNotFoundError(filename)
        return artifact_path

    def available_artifacts(self, job_id: str) -> list[str]:
        """Return the sorted allow-listed artifact names that safely exist for a job."""
        available_artifact_names: list[str] = []
        for artifact_name in sorted(ARTIFACT_NAMES):
            try:
                self.artifact(job_id, artifact_name)
            except FileNotFoundError:
                continue
            available_artifact_names.append(artifact_name)
        return available_artifact_names


def default_request(subject_name: str, birth: BirthInput) -> ReportRequest:
    """Create a report request targeting the current local year and month."""
    now = datetime.now()
    return ReportRequest(
        subject_name=subject_name,
        birth=birth,
        annual_year=now.year,
        monthly_year=now.year,
        monthly_month=now.month,
    )
