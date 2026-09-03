from __future__ import annotations

import shutil
from datetime import UTC, datetime, tzinfo
from pathlib import Path

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

import four_pillars.api as api_module
import four_pillars.calendar as calendar_module
from four_pillars.analysis import _allowed_pillars
from four_pillars.fortune import (
    calculate_annual_luck,
    calculate_daewoon,
    calculate_monthly_luck,
)
from four_pillars.jobs import JobStore
from four_pillars.models import BirthInput, CalendarKind, Gender, JobStatus, TimeBasis
from four_pillars.service import ReportService
from four_pillars.settings import Settings, get_settings


def configured_service(tmp_path: Path) -> ReportService:
    settings = Settings(
        artifact_dir=tmp_path / "artifacts",
        database_url=f"sqlite:///{tmp_path / 'jobs.sqlite3'}",
    )
    return ReportService(settings, JobStore(settings.sqlite_path))


def test_allowed_pillars_supports_an_unknown_birth_time() -> None:
    chart = calendar_module.calculate_chart(
        BirthInput(
            birth=datetime(1990, 6, 15, 8, 30),
            timezone="Asia/Seoul",
            gender=Gender.FEMALE,
            birth_time_known=False,
        )
    )
    daewoon = calculate_daewoon(chart, Gender.FEMALE, count=1)
    annual = calculate_annual_luck(chart, 2026)
    monthly = calculate_monthly_luck(chart, 2026, 8)

    allowed = _allowed_pillars(chart, daewoon, annual, monthly)

    assert chart.hour is None
    assert chart.year.hanja in allowed
    assert annual.pillar.hanja in allowed
    assert daewoon.scenarios[0].periods[0].pillar.hanja in allowed


def test_default_service_and_settings_are_loaded_from_environment(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    artifact_dir = tmp_path / "runtime-artifacts"
    database_path = tmp_path / "runtime.sqlite3"
    monkeypatch.setenv("ARTIFACT_DIR", str(artifact_dir))
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    api_module.get_service.cache_clear()
    get_settings.cache_clear()

    service = api_module.get_service()

    assert service.settings.artifact_dir == artifact_dir
    assert service.settings.sqlite_path == database_path
    api_module.get_service.cache_clear()
    get_settings.cache_clear()


def test_public_job_view_bounds_operational_error_text() -> None:
    """Keep the canonical status API from becoming an unbounded diagnostic channel."""
    now = datetime.now(UTC)

    with pytest.raises(ValidationError):
        api_module.ReportJobView(
            id="00000000-0000-0000-0000-000000000001",
            status=JobStatus.FAILED,
            created_at=now,
            updated_at=now,
            error="x" * 4001,
        )


def test_delete_report_handles_terminal_jobs_without_artifacts(tmp_path: Path) -> None:
    service = configured_service(tmp_path)
    job = service.store.create({"subject_name": "failed"})
    service.store.fail(job.id, "failed before artifacts")

    api_module.delete_report(job.id, service)

    assert service.store.get(job.id) is None


def test_delete_report_rejects_a_non_terminal_job(tmp_path: Path) -> None:
    service = configured_service(tmp_path)
    job = service.store.create({"subject_name": "queued"})

    with pytest.raises(HTTPException) as captured:
        api_module.delete_report(job.id, service)

    assert captured.value.status_code == 409
    assert service.store.get(job.id) is not None


@pytest.mark.parametrize(
    "missing_job_id",
    ["missing-job", "../escape", "00000000-0000-0000-0000-00000000000A"],
)
def test_delete_report_rejects_missing_jobs_without_a_trusted_orphan(
    missing_job_id: str,
    tmp_path: Path,
) -> None:
    """Return not-found without deleting outside or nonexistent artifact roots."""
    service = configured_service(tmp_path)

    with pytest.raises(HTTPException) as captured:
        api_module.delete_report(missing_job_id, service)

    assert captured.value.status_code == 404


def test_delete_report_rejects_a_non_uuid_orphan_directory(tmp_path: Path) -> None:
    """Never treat an arbitrary direct child as a recoverable report artifact."""
    service = configured_service(tmp_path)
    unrelated = service.settings.artifact_dir / "operator-backup"
    unrelated.mkdir(parents=True)
    marker = unrelated / "keep.txt"
    marker.write_text("keep", encoding="utf-8")

    with pytest.raises(HTTPException) as captured:
        api_module.delete_report("operator-backup", service)

    assert captured.value.status_code == 404
    assert marker.read_text(encoding="utf-8") == "keep"


def test_delete_report_rejects_a_staging_directory_name(tmp_path: Path) -> None:
    """Keep hidden staging directories outside the missing-row orphan recovery path."""
    service = configured_service(tmp_path)
    job = service.store.create({"subject_name": "staged"})
    staged = service.settings.artifact_dir / f".{job.id}.tmp"
    staged.mkdir(parents=True)
    marker = staged / "keep.txt"
    marker.write_text("keep", encoding="utf-8")
    service.store.delete(job.id)

    with pytest.raises(HTTPException) as captured:
        api_module.delete_report(f".{job.id}.tmp", service)

    assert captured.value.status_code == 404
    assert marker.read_text(encoding="utf-8") == "keep"


def test_delete_report_preserves_artifacts_when_terminal_row_delete_is_refused(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Never destroy the only artifact copy before durable deletion is accepted."""
    service = configured_service(tmp_path)
    job = service.store.create({"subject_name": "delete-refused"})
    service.store.claim_next()
    artifact_dir = service.settings.artifact_dir / job.id
    artifact_dir.mkdir(parents=True)
    (artifact_dir / "report.json").write_text("{}", encoding="utf-8")
    service.store.finish(job.id, artifact_dir)
    monkeypatch.setattr(service.store, "delete", lambda _: False)

    with pytest.raises(HTTPException) as captured:
        api_module.delete_report(job.id, service)

    assert captured.value.status_code == 409
    assert service.store.get(job.id) is not None
    assert (artifact_dir / "report.json").is_file()


def test_delete_report_can_retry_artifact_cleanup_after_row_deletion(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Keep a failed artifact cleanup retryable after the terminal row is removed."""
    service = configured_service(tmp_path)
    job = service.store.create({"subject_name": "cleanup-retry"})
    service.store.claim_next()
    artifact_dir = service.settings.artifact_dir / job.id
    artifact_dir.mkdir(parents=True)
    (artifact_dir / "report.json").write_text("{}", encoding="utf-8")
    service.store.finish(job.id, artifact_dir)
    real_rmtree = shutil.rmtree
    calls = 0

    def fail_once(path: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError("simulated cleanup failure")
        real_rmtree(path)

    monkeypatch.setattr(shutil, "rmtree", fail_once)

    with pytest.raises(HTTPException) as captured:
        api_module.delete_report(job.id, service)

    assert captured.value.status_code == 500
    assert service.store.get(job.id) is None
    assert artifact_dir.is_dir()

    api_module.delete_report(job.id, service)

    assert not artifact_dir.exists()


@pytest.mark.parametrize("artifact_mode", ["outside", "wrong_name", "missing"])
def test_delete_report_never_removes_an_untrusted_artifact_directory(
    artifact_mode: str,
    tmp_path: Path,
) -> None:
    service = configured_service(tmp_path)
    job = service.store.create({"subject_name": artifact_mode})
    service.store.claim_next()
    if artifact_mode == "outside":
        artifact_dir = tmp_path / "outside"
    elif artifact_mode == "wrong_name":
        artifact_dir = service.settings.artifact_dir / "different-job"
    else:
        artifact_dir = service.settings.artifact_dir / job.id
    if artifact_mode != "missing":
        artifact_dir.mkdir(parents=True)
    service.store.finish(job.id, artifact_dir)

    api_module.delete_report(job.id, service)

    assert service.store.get(job.id) is None
    if artifact_mode != "missing":
        assert artifact_dir.exists()


def test_solar_longitude_rejects_a_naive_datetime() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        calendar_module.apparent_solar_longitude(datetime(2026, 1, 1))


def test_solar_term_requires_a_bracketed_root(monkeypatch: pytest.MonkeyPatch) -> None:
    calendar_module.solar_term_utc.cache_clear()
    monkeypatch.setattr(calendar_module, "_angle_delta", lambda *_: 1.0)

    with pytest.raises(RuntimeError, match="not bracketed"):
        calendar_module.solar_term_utc(2199, calendar_module.JIE_TERMS[0][2])

    calendar_module.solar_term_utc.cache_clear()


def test_invalid_lunar_input_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    import korean_lunar_calendar

    class RejectingCalendar:
        def setLunarDate(self, *_: object) -> bool:
            return False

    monkeypatch.setattr(korean_lunar_calendar, "KoreanLunarCalendar", RejectingCalendar)
    value = BirthInput(
        birth=datetime(1990, 6, 15, 8, 30),
        calendar=CalendarKind.LUNAR,
    )

    with pytest.raises(ValueError, match="outside the supported"):
        calendar_module.normalize_birth(value)


class NullOffsetTimezone(tzinfo):
    def utcoffset(self, value: datetime | None) -> None:
        return None

    def dst(self, value: datetime | None) -> None:
        return None

    def tzname(self, value: datetime | None) -> str:
        return "NullOffset"


def test_solar_time_rejects_a_timezone_without_an_offset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(calendar_module, "ZoneInfo", lambda _: NullOffsetTimezone())
    value = BirthInput(
        birth=datetime(1990, 6, 15, 8, 30),
        longitude=127.0,
        time_basis=TimeBasis.MEAN_SOLAR,
    )

    with pytest.raises(ValueError, match="no UTC offset"):
        calendar_module.normalize_birth(value)


def test_annual_luck_requires_a_timezone_aware_chart() -> None:
    chart = calendar_module.calculate_chart(BirthInput(birth=datetime(1990, 6, 15, 8, 30)))
    naive_chart = chart.model_copy(
        update={"normalized_birth": chart.normalized_birth.replace(tzinfo=None)}
    )

    with pytest.raises(ValueError, match="timezone-aware"):
        calculate_annual_luck(naive_chart, 2026)


def test_birth_input_removes_timezone_information_from_wall_clock() -> None:
    value = BirthInput(birth=datetime(1990, 6, 15, 8, 30, tzinfo=UTC))

    assert value.birth.tzinfo is None
