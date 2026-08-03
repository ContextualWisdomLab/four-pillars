from __future__ import annotations

import hashlib
import secrets
from functools import lru_cache
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

from .calendar import calculate_chart
from .fortune import calculate_annual_luck, calculate_daewoon, calculate_monthly_luck
from .models import BirthInput, Chart, DaewoonResult, LuckSnapshot, ReportJob
from .service import ReportRequest, ReportService
from .settings import Settings, get_settings

app = FastAPI(
    title="Four Pillars API",
    version="0.1.0",
    description="Deterministic Korean Four Pillars calculation with NVIDIA NIM report generation",
)


class LuckRequest(BaseModel):
    birth: BirthInput
    year: int = Field(ge=1900, le=2200)
    month: int = Field(default=1, ge=1, le=12)


@lru_cache(maxsize=1)
def get_service() -> ReportService:
    return ReportService(get_settings())


def require_api_key(
    settings: Settings = Depends(get_settings),
    x_api_key: str | None = Header(default=None),
) -> None:
    expected = settings.api_key_sha256
    if not expected:
        return
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required")
    actual = hashlib.sha256(x_api_key.encode()).hexdigest()
    if not secrets.compare_digest(actual, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index() -> str:
    return """<!doctype html><html lang='ko'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>Four Pillars</title><style>body{font-family:system-ui,sans-serif;margin:0;background:#f7f6f1;color:#17263f}main{max-width:920px;margin:8vh auto;padding:36px}section{background:white;border-radius:18px;padding:34px;box-shadow:0 16px 48px #17263f16}a{color:#315a84}code{background:#eaf1f7;padding:3px 6px;border-radius:5px}</style></head><body><main><section><p>FOUR PILLARS</p><h1>계산은 결정론적으로, 해석은 근거와 함께.</h1><p>원국·대운·세운·월운을 계산하고 NVIDIA NIM으로 스키마 검증된 보고서를 생성합니다.</p><p><a href='/docs'>API 문서 열기</a> · <a href='/health'>상태 확인</a></p><p>보고서 작업은 <code>POST /v1/reports</code>로 등록하고 별도 worker가 처리합니다.</p></section></main></body></html>"""


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": app.version}


@app.get("/ready")
def ready(service: ReportService = Depends(get_service)) -> dict[str, str]:
    service.settings.artifact_dir.mkdir(parents=True, exist_ok=True)
    probe = service.settings.artifact_dir / ".ready"
    probe.write_text("ok", encoding="utf-8")
    probe.unlink(missing_ok=True)
    service.store.get("00000000-0000-0000-0000-000000000000")
    return {"status": "ready"}


@app.post("/v1/chart", response_model=Chart, dependencies=[Depends(require_api_key)])
def chart(request: BirthInput) -> Chart:
    return calculate_chart(request)


@app.post("/v1/luck/daewoon", response_model=DaewoonResult, dependencies=[Depends(require_api_key)])
def daewoon(request: BirthInput) -> DaewoonResult:
    calculated = calculate_chart(request)
    return calculate_daewoon(calculated, request.gender)


@app.post("/v1/luck/annual", response_model=LuckSnapshot, dependencies=[Depends(require_api_key)])
def annual(request: LuckRequest) -> LuckSnapshot:
    return calculate_annual_luck(calculate_chart(request.birth), request.year)


@app.post("/v1/luck/monthly", response_model=LuckSnapshot, dependencies=[Depends(require_api_key)])
def monthly(request: LuckRequest) -> LuckSnapshot:
    return calculate_monthly_luck(calculate_chart(request.birth), request.year, request.month)


@app.post(
    "/v1/reports",
    response_model=ReportJob,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_api_key)],
)
def create_report(
    request: ReportRequest,
    service: ReportService = Depends(get_service),
) -> ReportJob:
    return service.enqueue(request)


@app.get("/v1/reports/{job_id}", response_model=ReportJob, dependencies=[Depends(require_api_key)])
def get_report(job_id: str, service: ReportService = Depends(get_service)) -> ReportJob:
    job = service.store.get(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report job not found")
    return job


@app.get("/v1/reports/{job_id}/artifacts/{filename}", dependencies=[Depends(require_api_key)])
def get_artifact(
    job_id: str,
    filename: str,
    download: bool = Query(default=True),
    service: ReportService = Depends(get_service),
) -> FileResponse:
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
    job = service.store.get(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report job not found")
    if job.artifact_dir:
        root = Path(job.artifact_dir).resolve()
        if root.parent == service.settings.artifact_dir.resolve() and root.exists():
            import shutil

            shutil.rmtree(root)
    if not service.store.delete(job_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only terminal jobs can be deleted")
