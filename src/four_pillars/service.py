from __future__ import annotations

import asyncio
import shutil
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from .analysis import GeneratedReport, generate_report
from .calendar import calculate_chart
from .fortune import calculate_annual_luck, calculate_daewoon, calculate_monthly_luck
from .jobs import JobStore
from .models import BirthInput, Chart, DaewoonResult, LuckSnapshot, ReportJob
from .nim import NimClient
from .quality import ReportQualityError
from .reporting import write_artifacts
from .settings import Settings


class ReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject_name: str = Field(min_length=1, max_length=80)
    birth: BirthInput
    annual_year: int = Field(ge=1900, le=2200)
    monthly_year: int = Field(ge=1900, le=2200)
    monthly_month: int = Field(ge=1, le=12)
    user_context: str = Field(default="", max_length=4000)


class CalculationBundle(BaseModel):
    chart: Chart
    daewoon: DaewoonResult
    annual: LuckSnapshot
    monthly: LuckSnapshot


def calculate_bundle(request: ReportRequest) -> CalculationBundle:
    chart = calculate_chart(request.birth)
    daewoon = calculate_daewoon(chart, request.birth.gender)
    annual = calculate_annual_luck(chart, request.annual_year)
    monthly = calculate_monthly_luck(chart, request.monthly_year, request.monthly_month)
    return CalculationBundle(chart=chart, daewoon=daewoon, annual=annual, monthly=monthly)


class ReportService:
    def __init__(self, settings: Settings, store: JobStore | None = None) -> None:
        self.settings = settings
        self.settings.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.store = store or JobStore(settings.sqlite_path)

    def enqueue(self, request: ReportRequest) -> ReportJob:
        return self.store.create(request.model_dump(mode="json"))

    async def generate(self, request: ReportRequest) -> tuple[CalculationBundle, GeneratedReport]:
        bundle = calculate_bundle(request)
        async with NimClient(self.settings) as client:
            generated = await generate_report(
                client=client,
                subject_name=request.subject_name,
                chart=bundle.chart,
                daewoon=bundle.daewoon,
                annual=bundle.annual,
                monthly=bundle.monthly,
                user_context=request.user_context,
            )
        return bundle, generated

    async def process(self, job: ReportJob) -> ReportJob:
        request = ReportRequest.model_validate(job.request)
        temporary = self.settings.artifact_dir / f".{job.id}.tmp"
        final = self.settings.artifact_dir / job.id
        shutil.rmtree(temporary, ignore_errors=True)
        shutil.rmtree(final, ignore_errors=True)
        try:
            bundle, generated = await self.generate(request)
            write_artifacts(
                temporary,
                report=generated.report,
                chart=bundle.chart,
                daewoon=bundle.daewoon,
                annual=bundle.annual,
                monthly=bundle.monthly,
                traces=generated.traces,
            )
            temporary.replace(final)
            return self.store.finish(job.id, final)
        except ReportQualityError as exc:
            shutil.rmtree(temporary, ignore_errors=True)
            return self.store.fail(job.id, str(exc), quality=True)
        except Exception as exc:
            shutil.rmtree(temporary, ignore_errors=True)
            return self.store.fail(job.id, f"{type(exc).__name__}: {exc}")

    async def process_next(self) -> ReportJob | None:
        job = self.store.claim_next()
        if job is None:
            return None
        return await self.process(job)

    async def worker(self, poll_seconds: float = 1.0) -> None:
        while True:
            processed = await self.process_next()
            if processed is None:
                await asyncio.sleep(poll_seconds)

    def artifact(self, job_id: str, filename: str) -> Path:
        allowed = {
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
        if filename not in allowed:
            raise ValueError("Unsupported artifact name")
        job = self.store.get(job_id)
        if job is None or job.artifact_dir is None:
            raise FileNotFoundError(job_id)
        root = Path(job.artifact_dir).resolve()
        candidate = (root / filename).resolve()
        if candidate.parent != root or not candidate.is_file():
            raise FileNotFoundError(filename)
        return candidate


def default_request(subject_name: str, birth: BirthInput) -> ReportRequest:
    now = datetime.now()
    return ReportRequest(
        subject_name=subject_name,
        birth=birth,
        annual_year=now.year,
        monthly_year=now.year,
        monthly_month=now.month,
    )
