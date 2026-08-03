from __future__ import annotations

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


def configured(tmp_path: Path):
    settings = Settings(
        artifact_dir=tmp_path / "artifacts",
        database_url=f"sqlite:///{tmp_path / 'jobs.sqlite3'}",
    )
    service = ReportService(settings, JobStore(settings.sqlite_path))
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_service] = lambda: service
    return TestClient(app), service


def teardown_function() -> None:
    app.dependency_overrides.clear()


def test_root_readiness_and_luck_endpoints(tmp_path: Path) -> None:
    http, _ = configured(tmp_path)
    with http:
        assert "FOUR PILLARS" in http.get("/").text
        assert http.get("/ready").json() == {"status": "ready"}
        daewoon = http.post("/v1/luck/daewoon", json=BIRTH)
        annual = http.post("/v1/luck/annual", json={"birth": BIRTH, "year": 2026, "month": 1})
        monthly = http.post("/v1/luck/monthly", json={"birth": BIRTH, "year": 2026, "month": 8})
    assert daewoon.status_code == 200
    assert daewoon.json()["scenarios"][0]["direction"] == "reverse"
    assert annual.json()["pillar"]["hanja"] == "丙午"
    assert monthly.json()["pillar"]["hanja"] == "丙申"


def test_completed_artifact_can_be_downloaded_and_deleted(tmp_path: Path) -> None:
    http, service = configured(tmp_path)
    queued = service.store.create({"subject_name": "테스트"})
    service.store.claim_next()
    artifact_dir = service.settings.artifact_dir / queued.id
    artifact_dir.mkdir(parents=True)
    (artifact_dir / "report.json").write_text('{"ok":true}', encoding="utf-8")
    service.store.finish(queued.id, artifact_dir)

    with http:
        downloaded = http.get(f"/v1/reports/{queued.id}/artifacts/report.json")
        deleted = http.delete(f"/v1/reports/{queued.id}")
        missing = http.get(f"/v1/reports/{queued.id}")
    assert downloaded.status_code == 200
    assert downloaded.json() == {"ok": True}
    assert deleted.status_code == 204
    assert missing.status_code == 404
    assert not artifact_dir.exists()


def test_unknown_job_and_artifact_return_not_found(tmp_path: Path) -> None:
    http, _ = configured(tmp_path)
    with http:
        assert http.get("/v1/reports/missing").status_code == 404
        assert http.get("/v1/reports/missing/artifacts/report.pdf").status_code == 404
