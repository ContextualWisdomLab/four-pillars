from __future__ import annotations

import hashlib
from pathlib import Path

from fastapi.testclient import TestClient

from four_pillars.api import app, get_service
from four_pillars.jobs import JobStore
from four_pillars.service import ReportService
from four_pillars.settings import Settings, get_settings


BIRTH = {
    "birth": "1990-06-15T08:30:00",
    "timezone": "Asia/Seoul",
    "gender": "female",
    "calendar": "solar",
    "birth_time_known": True,
    "time_basis": "civil",
    "day_boundary": "midnight",
}


def client(tmp_path: Path, api_key: str | None = None) -> TestClient:
    settings = Settings(
        artifact_dir=tmp_path / "artifacts",
        database_url=f"sqlite:///{tmp_path / 'jobs.sqlite3'}",
        api_key_sha256=hashlib.sha256(api_key.encode()).hexdigest() if api_key else None,
    )
    service = ReportService(settings, JobStore(settings.sqlite_path))
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_service] = lambda: service
    return TestClient(app)


def teardown_function() -> None:
    app.dependency_overrides.clear()


def test_health_and_chart_golden_case(tmp_path: Path) -> None:
    with client(tmp_path) as http:
        assert http.get("/health").json()["status"] == "ok"
        assert 'id="report-form"' in http.get("/").text
        response = http.post("/v1/chart", json=BIRTH)
    assert response.status_code == 200
    payload = response.json()
    assert [payload[key]["hanja"] for key in ("year", "month", "day", "hour")] == [
        "庚午",
        "壬午",
        "辛亥",
        "壬辰",
    ]


def test_optional_api_key_uses_sha256_digest(tmp_path: Path) -> None:
    with client(tmp_path, api_key="secret") as http:
        assert http.post("/v1/chart", json=BIRTH).status_code == 401
        assert http.get("/v1/reports").status_code == 401
        assert http.post("/v1/chart", json=BIRTH, headers={"X-API-Key": "wrong"}).status_code == 401
        assert http.post("/v1/chart", json=BIRTH, headers={"X-API-Key": "secret"}).status_code == 200
        assert http.get("/v1/reports", headers={"X-API-Key": "secret"}).status_code == 200


def test_report_request_is_queued_durably_without_echoing_sensitive_input(tmp_path: Path) -> None:
    body = {
        "subject_name": "최혜지",
        "birth": BIRTH,
        "annual_year": 2026,
        "monthly_year": 2026,
        "monthly_month": 8,
        "user_context": "직장과 생활 계획을 구체적으로 설명해 주세요.",
    }
    with client(tmp_path) as http:
        created = http.post("/v1/reports", json=body)
        assert created.status_code == 202
        job = created.json()
        fetched = http.get(f"/v1/reports/{job['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["status"] == "queued"
    for view in (job, fetched.json()):
        assert "request" not in view
        assert "artifact_dir" not in view
        assert view["artifacts"] == []


def test_unknown_artifact_name_is_not_resolved(tmp_path: Path) -> None:
    with client(tmp_path) as http:
        response = http.get("/v1/reports/missing/artifacts/../../etc/passwd")
    assert response.status_code in {404, 422}
