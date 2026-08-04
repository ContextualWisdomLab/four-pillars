"""Expose deterministic calculations, report jobs, and generated artifacts through FastAPI."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime
from functools import lru_cache
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Response, status
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, ConfigDict, Field

from .calendar import calculate_chart
from .fortune import calculate_annual_luck, calculate_daewoon, calculate_monthly_luck
from .idempotency import parse_idempotency_key, request_fingerprint
from .jobs import IdempotencyKeyReuseError
from .models import BirthInput, Chart, DaewoonResult, JobStatus, LuckSnapshot, ReportJob
from .service import ReportRequest, ReportService
from .settings import Settings, get_settings
from .version import __version__
from .web import render_home

app = FastAPI(
    title="Four Pillars API",
    version=__version__,
    description="Deterministic Korean Four Pillars calculation with NVIDIA NIM report generation",
)


class LuckRequest(BaseModel):
    """Validated birth input and target year or month for temporary luck calculations."""

    model_config = ConfigDict(extra="forbid")

    birth: BirthInput
    year: int = Field(ge=1900, le=2200)
    month: int = Field(default=1, ge=1, le=12)


class ReportJobView(BaseModel):
    """Public report-job status without the stored birth request or raw model text."""

    model_config = ConfigDict(extra="forbid")

    id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    error: str | None = None
    artifacts: list[str] = Field(default_factory=list)


@lru_cache(maxsize=1)
def get_service() -> ReportService:
    """Return the process-wide report service configured from the environment."""
    return ReportService(get_settings())


def require_api_key(
    settings: Settings = Depends(get_settings),
    x_api_key: str | None = Header(default=None),
) -> None:
    """Enforce optional SHA-256 API-key authentication with constant-time comparison."""
    expected = settings.api_key_sha256
    if not expected:
        return
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required")
    actual = hashlib.sha256(x_api_key.encode()).hexdigest()
    if not secrets.compare_digest(actual, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


def _job_view(job: ReportJob, service: ReportService) -> ReportJobView:
    artifacts = service.available_artifacts(job.id) if job.status is JobStatus.COMPLETED else []
    return ReportJobView(
        id=job.id,
        status=job.status,
        created_at=job.created_at,
        updated_at=job.updated_at,
        error=job.error,
        artifacts=artifacts,
    )


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index() -> str:
    """Render the browser-based calculation and report studio."""
    return render_home()


@app.get("/health")
def health() -> dict[str, str]:
    """Report process liveness and the served API version."""
    return {"status": "ok", "version": app.version}


@app.get("/ready")
def ready(service: ReportService = Depends(get_service)) -> dict[str, str]:
    """Verify writable artifact storage and readable job storage before serving traffic."""
    service.settings.artifact_dir.mkdir(parents=True, exist_ok=True)
    probe = service.settings.artifact_dir / ".ready"
    probe.write_text("ok", encoding="utf-8")
    probe.unlink(missing_ok=True)
    service.store.get("00000000-0000-0000-0000-000000000000")
    return {"status": "ready"}


@app.post("/v1/chart", response_model=Chart, dependencies=[Depends(require_api_key)])
def chart(request: BirthInput) -> Chart:
    """Calculate one immutable natal Four Pillars chart."""
    return calculate_chart(request)


@app.post("/v1/luck/daewoon", response_model=DaewoonResult, dependencies=[Depends(require_api_key)])
def daewoon(request: BirthInput) -> DaewoonResult:
    """Calculate the direction, start age, and periods of daewoon luck."""
    calculated = calculate_chart(request)
    return calculate_daewoon(calculated, request.gender)


@app.post("/v1/luck/annual", response_model=LuckSnapshot, dependencies=[Depends(require_api_key)])
def annual(request: LuckRequest) -> LuckSnapshot:
    """Calculate the solar-term-bounded annual luck snapshot for one year."""
    return calculate_annual_luck(calculate_chart(request.birth), request.year)


@app.post("/v1/luck/monthly", response_model=LuckSnapshot, dependencies=[Depends(require_api_key)])
def monthly(request: LuckRequest) -> LuckSnapshot:
    """Calculate one solar-term-bounded monthly luck snapshot."""
    return calculate_monthly_luck(calculate_chart(request.birth), request.year, request.month)


@app.post(
    "/v1/reports",
    response_model=ReportJobView,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_api_key)],
)
def create_report(
    request: ReportRequest,
    response: Response,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    service: ReportService = Depends(get_service),
) -> ReportJobView:
    """Persist or safely replay a validated report request as a queued job."""
    if idempotency_key is None:
        return _job_view(service.enqueue(request), service)
    try:
        canonical_key = parse_idempotency_key(idempotency_key)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    payload = request.model_dump(mode="json")
    fingerprint = request_fingerprint(payload)
    key_digest = hashlib.sha256(canonical_key.encode("utf-8")).hexdigest()
    try:
        job, replayed = service.enqueue_idempotent(request, key_digest, fingerprint)
    except IdempotencyKeyReuseError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    response.headers["Idempotency-Replayed"] = "true" if replayed else "false"
    return _job_view(job, service)


@app.get(
    "/v1/reports/{job_id}",
    response_model=ReportJobView,
    dependencies=[Depends(require_api_key)],
)
def get_report(job_id: str, service: ReportService = Depends(get_service)) -> ReportJobView:
    """Return the current public status and artifacts for one report job."""
    job = service.store.get(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report job not found")
    return _job_view(job, service)


@app.get("/v1/reports/{job_id}/artifacts/{filename}", dependencies=[Depends(require_api_key)])
def get_artifact(
    job_id: str,
    filename: str,
    download: bool = Query(default=True),
    service: ReportService = Depends(get_service),
) -> FileResponse:
    """Serve one allow-listed report artifact after path-boundary validation."""
    try:
        path = service.artifact(job_id, filename)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found") from exc
    media_types = {".pdf": "application/pdf", ".html": "text/html", ".json": "application/json"}
    return FileResponse(
        path,
        media_type=media_types.get(path.suffix, "application/octet-stream"),
        filename=path.name if download else None,
    )


@app.delete("/v1/reports/{job_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_api_key)])
def delete_report(job_id: str, service: ReportService = Depends(get_service)) -> None:
    """Delete a terminal job and only its validated UUID artifact directory."""
    job = service.store.get(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report job not found")
    if job.artifact_dir:
        root = Path(job.artifact_dir).resolve()
        configured_root = service.settings.artifact_dir.resolve()
        if root.parent == configured_root and root.name == job.id and root.exists():
            import shutil

            shutil.rmtree(root)
    if not service.store.delete(job_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only terminal jobs can be deleted")
