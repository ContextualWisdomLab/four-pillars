from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from four_pillars.api import app, get_service
from four_pillars.jobs import JobStore
from four_pillars.models import JobStatus, ReportJob
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


class LegacyRepository:
    """Forward the required repository contract without history pagination."""

    def __init__(self, delegate: JobStore) -> None:
        self.delegate = delegate

    def create(self, request: dict[str, Any]) -> ReportJob:
        """Create one job through the delegate."""
        return self.delegate.create(request)

    def get(self, job_id: str) -> ReportJob | None:
        """Return one delegated job."""
        return self.delegate.get(job_id)

    def claim_next(self) -> ReportJob | None:
        """Claim one delegated job."""
        return self.delegate.claim_next()

    def finish(self, job_id: str, artifact_dir: Path) -> ReportJob:
        """Finish one delegated job."""
        return self.delegate.finish(job_id, artifact_dir)

    def fail(self, job_id: str, error: str, *, quality: bool = False) -> ReportJob:
        """Fail one delegated job."""
        return self.delegate.fail(job_id, error, quality=quality)

    def delete(self, job_id: str) -> bool:
        """Delete one delegated terminal job."""
        return self.delegate.delete(job_id)

    def purge(self, retention_days: int) -> list[str]:
        """Purge delegated terminal jobs."""
        return self.delegate.purge(retention_days)


def configured(tmp_path: Path) -> tuple[TestClient, ReportService]:
    settings = Settings(
        artifact_dir=tmp_path / "artifacts",
        database_url=f"sqlite:///{tmp_path / 'jobs.sqlite3'}",
    )
    service = ReportService(settings, JobStore(settings.sqlite_path))
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_service] = lambda: service
    return TestClient(app), service


def _set_job(
    service: ReportService,
    job_id: str,
    *,
    created_at: datetime,
    status: JobStatus,
    error: str | None = None,
) -> None:
    with closing(sqlite3.connect(service.settings.sqlite_path)) as connection, connection:
        connection.execute(
            """
            UPDATE report_jobs
            SET created_at=?, updated_at=?, status=?, error=?
            WHERE id=?
            """,
            (
                created_at.isoformat(),
                created_at.isoformat(),
                status.value,
                error,
                job_id,
            ),
        )


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


def test_report_history_is_paginated_filtered_and_privacy_safe(tmp_path: Path) -> None:
    http, service = configured(tmp_path)
    base = datetime(2026, 8, 4, 5, 0, tzinfo=UTC)
    older = service.store.create(
        {
            "subject_name": "비공개 이름",
            "birth": BIRTH,
            "user_context": "비공개 메모",
        }
    )
    newer = service.store.create({"subject_name": "두 번째 비공개 이름"})
    _set_job(
        service,
        older.id,
        created_at=base,
        status=JobStatus.COMPLETED,
    )
    _set_job(
        service,
        newer.id,
        created_at=base + timedelta(minutes=1),
        status=JobStatus.FAILED,
        error="redacted operational failure",
    )

    with http:
        first = http.get("/v1/reports", params={"limit": 1})
        first_payload = first.json()
        second = http.get(
            "/v1/reports",
            params={"limit": 1, "cursor": first_payload["next_cursor"]},
        )
        completed = http.get("/v1/reports", params={"status": "completed"})

    assert first.status_code == 200
    assert [item["id"] for item in first_payload["items"]] == [newer.id]
    assert first_payload["next_cursor"]
    assert [item["id"] for item in second.json()["items"]] == [older.id]
    assert second.json()["next_cursor"] is None
    assert [item["id"] for item in completed.json()["items"]] == [older.id]
    for item in [*first_payload["items"], *second.json()["items"]]:
        assert set(item) == {
            "id",
            "status",
            "created_at",
            "updated_at",
            "error",
            "artifacts",
        }
        assert "비공개" not in str(item)
        assert "request" not in item
        assert "request_fingerprint" not in item
        assert "idempotency_key_digest" not in item
        assert "artifact_dir" not in item


def test_report_history_rejects_invalid_query_input(tmp_path: Path) -> None:
    http, _ = configured(tmp_path)
    with http:
        assert http.get("/v1/reports", params={"cursor": "v1.invalid"}).status_code == 400
        assert http.get("/v1/reports", params={"cursor": "v1." + "A" * 300}).status_code == 400
        assert http.get("/v1/reports", params={"limit": 0}).status_code == 422
        assert http.get("/v1/reports", params={"limit": 101}).status_code == 422
        assert http.get("/v1/reports", params={"status": "unknown"}).status_code == 422


def test_report_history_fails_explicitly_for_legacy_repository(tmp_path: Path) -> None:
    settings = Settings(
        artifact_dir=tmp_path / "artifacts",
        database_url=f"sqlite:///{tmp_path / 'legacy.sqlite3'}",
    )
    repository = LegacyRepository(JobStore(settings.sqlite_path))
    service = ReportService(settings, store=repository)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_service] = lambda: service

    with TestClient(app) as http:
        response = http.get("/v1/reports")

    assert response.status_code == 501
    assert "history" in response.json()["detail"]
