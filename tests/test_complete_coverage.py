from __future__ import annotations

import runpy
import sys
from datetime import UTC, datetime, tzinfo
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from fastapi import HTTPException
from pydantic import BaseModel
from test_quality import valid_report

import four_pillars.api as api_module
import four_pillars.calendar as calendar_module
import four_pillars.cli as cli_module
import four_pillars.nim as nim_module
import four_pillars.prompts as prompts_module
import four_pillars.reporting as reporting_module
import four_pillars.service as service_module
from four_pillars.analysis import GeneratedReport, _allowed_pillars
from four_pillars.calendar import calculate_chart, normalize_birth
from four_pillars.constants import FORBIDDEN_COPY
from four_pillars.fortune import (
    calculate_annual_luck,
    calculate_daewoon,
    calculate_monthly_luck,
)
from four_pillars.jobs import JobStore
from four_pillars.models import (
    BirthInput,
    CalendarKind,
    Gender,
    TimeBasis,
)
from four_pillars.nim import NimClient, NimError, NimSchemaError
from four_pillars.prompts import PROMPT_NAMES, PromptTemplate
from four_pillars.quality import ReportQualityError, assert_report_quality, validate_report
from four_pillars.service import ReportRequest, ReportService
from four_pillars.settings import Settings, get_settings


class Answer(BaseModel):
    value: str


def report_request() -> ReportRequest:
    return ReportRequest(
        subject_name="완전 커버리지",
        birth=BirthInput(
            birth=datetime(1990, 6, 15, 8, 30),
            timezone="Asia/Seoul",
            gender=Gender.FEMALE,
        ),
        annual_year=2026,
        monthly_year=2026,
        monthly_month=8,
    )


def configured_service(tmp_path: Path) -> ReportService:
    settings = Settings(
        artifact_dir=tmp_path / "artifacts",
        database_url=f"sqlite:///{tmp_path / 'jobs.sqlite3'}",
    )
    return ReportService(settings, JobStore(settings.sqlite_path))


def nim_settings(**updates: object) -> Settings:
    values: dict[str, object] = {
        "nvidia_nim_api_key": "test-key",
        "nim_base_url": "https://nim.test/v1",
        "nim_model": "test-model",
        "nim_max_retries": 0,
        "nim_max_schema_repairs": 0,
    }
    values.update(updates)
    return Settings(**values)


def test_allowed_pillars_supports_an_unknown_birth_time() -> None:
    chart = calculate_chart(
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


def test_julian_date_rejects_a_naive_datetime() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        calendar_module._julian_date(datetime(2026, 1, 1))


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
        normalize_birth(value)


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
        normalize_birth(value)


def test_annual_luck_requires_a_timezone_aware_chart() -> None:
    chart = calculate_chart(BirthInput(birth=datetime(1990, 6, 15, 8, 30)))
    naive_chart = chart.model_copy(
        update={"normalized_birth": chart.normalized_birth.replace(tzinfo=None)}
    )

    with pytest.raises(ValueError, match="timezone-aware"):
        calculate_annual_luck(naive_chart, 2026)


class LostClaimConnection:
    def __enter__(self) -> LostClaimConnection:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def execute(self, statement: str, *_: object) -> SimpleNamespace:
        if statement.startswith("SELECT id"):
            return SimpleNamespace(fetchone=lambda: {"id": "lost-race"})
        if statement.startswith("UPDATE report_jobs"):
            return SimpleNamespace(rowcount=0)
        return SimpleNamespace()


def test_claim_next_returns_none_when_the_atomic_update_loses_a_race(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    store = JobStore(tmp_path / "jobs.sqlite3")
    monkeypatch.setattr(store, "_connect", lambda: LostClaimConnection())

    assert store.claim_next() is None


def test_transition_rejects_an_unknown_job(tmp_path: Path) -> None:
    store = JobStore(tmp_path / "jobs.sqlite3")

    with pytest.raises(KeyError, match="Unknown report job"):
        store.finish("missing", tmp_path / "missing")


def test_transition_rejects_a_row_that_disappears_after_update(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    store = JobStore(tmp_path / "jobs.sqlite3")
    job = store.create({"subject_name": "disappearing"})
    monkeypatch.setattr(store, "get", lambda _: None)

    with pytest.raises(KeyError, match="after transition"):
        store.fail(job.id, "failure")


def test_birth_input_removes_timezone_information_from_wall_clock() -> None:
    value = BirthInput(birth=datetime(1990, 6, 15, 8, 30, tzinfo=UTC))

    assert value.birth.tzinfo is None


@pytest.mark.asyncio
async def test_network_failures_retry_and_then_succeed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    async def no_sleep(_: float) -> None:
        return None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise httpx.ReadTimeout("timed out", request=request)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"value":"ok"}'}}]},
        )

    monkeypatch.setattr(nim_module.asyncio, "sleep", no_sleep)
    async with NimClient(
        nim_settings(nim_max_retries=1),
        transport=httpx.MockTransport(handler),
    ) as client:
        answer, trace = await client.generate(
            system_prompt="JSON",
            user_payload={},
            response_model=Answer,
        )

    assert answer.value == "ok"
    assert trace.attempts == 2


@pytest.mark.asyncio
async def test_network_failures_stop_at_the_retry_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    async def no_sleep(_: float) -> None:
        return None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ConnectError("offline", request=request)

    monkeypatch.setattr(nim_module.asyncio, "sleep", no_sleep)
    async with NimClient(
        nim_settings(nim_max_retries=1),
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(NimError, match="network retries"):
            await client.generate(
                system_prompt="JSON",
                user_payload={},
                response_model=Answer,
            )

    assert calls == 2


@pytest.mark.asyncio
async def test_non_json_http_payload_is_rejected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not-json")

    async with NimClient(
        nim_settings(),
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(NimError, match="non-JSON HTTP response"):
            await client.generate(
                system_prompt="JSON",
                user_payload={},
                response_model=Answer,
            )


@pytest.mark.parametrize("content", ["", None])
@pytest.mark.asyncio
async def test_empty_or_non_string_nim_content_is_rejected(content: object) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": content}}]},
        )

    async with NimClient(
        nim_settings(),
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(NimError, match="empty content"):
            await client.generate(
                system_prompt="JSON",
                user_payload={},
                response_model=Answer,
            )


def test_json_object_parser_covers_incomplete_fences_and_non_objects() -> None:
    assert NimClient._json_object('```json\n{"value":"ok"}') == {"value": "ok"}
    with pytest.raises(NimSchemaError, match="not a JSON object"):
        NimClient._json_object("```")
    with pytest.raises(NimSchemaError, match="one JSON object"):
        NimClient._json_object("[]")


@pytest.mark.asyncio
async def test_post_detects_an_impossible_empty_attempt_budget() -> None:
    settings = Settings.model_construct(
        nvidia_nim_api_key="test-key",
        nim_base_url="https://nim.test/v1",
        nim_model="test-model",
        nim_timeout_seconds=120.0,
        nim_max_retries=-1,
        nim_max_schema_repairs=0,
    )
    async with NimClient(settings, transport=httpx.MockTransport(lambda request: None)) as client:
        with pytest.raises(NimError, match="exhausted its retry budget"):
            await client._post({})


@pytest.mark.asyncio
async def test_generate_detects_an_impossible_empty_repair_budget() -> None:
    settings = Settings.model_construct(
        nvidia_nim_api_key="test-key",
        nim_base_url="https://nim.test/v1",
        nim_model="test-model",
        nim_timeout_seconds=120.0,
        nim_max_retries=0,
        nim_max_schema_repairs=-1,
    )
    async with NimClient(settings, transport=httpx.MockTransport(lambda request: None)) as client:
        with pytest.raises(NimSchemaError, match="unreachable schema repair state"):
            await client.generate(
                system_prompt="JSON",
                user_payload={},
                response_model=Answer,
            )


def test_unknown_prompt_is_rejected() -> None:
    with pytest.raises(KeyError, match="Unknown prompt"):
        prompts_module.load_prompt("missing")


def test_prompt_without_a_version_header_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakePromptFile:
        def read_text(self, *, encoding: str) -> str:
            assert encoding == "utf-8"
            return "missing semantic version header"

    class FakePromptRoot:
        def joinpath(self, name: str) -> FakePromptFile:
            assert name.endswith(".md")
            return FakePromptFile()

    monkeypatch.setattr(prompts_module, "files", lambda _: FakePromptRoot())

    with pytest.raises(ValueError, match="semantic version header"):
        prompts_module.load_prompt(PROMPT_NAMES[0])


def test_prompt_manifest_can_skip_an_empty_template(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_load(name: str) -> PromptTemplate | None:
        if name == PROMPT_NAMES[0]:
            return None
        return PromptTemplate(name=name, version="1.0.0", body="body", sha256="a" * 64)

    monkeypatch.setattr(prompts_module, "load_prompt", fake_load)

    manifest = prompts_module.prompt_manifest()

    assert PROMPT_NAMES[0] not in manifest
    assert set(manifest) == set(PROMPT_NAMES[1:])


def test_quality_gate_covers_empty_section_lists_and_absent_relationships() -> None:
    report = valid_report()
    report.sections["natal"].opportunities = []
    report.sections["daewoon"].cautions = []
    report.sections["annual"].actions = []
    report.sections.pop("relationships")

    codes = {issue.code for issue in validate_report(report, report.calculation_fingerprint)}

    assert {
        "missing_action",
        "missing_caution",
        "missing_opportunity",
        "missing_sections",
    } <= codes


def test_quality_gate_detects_forbidden_certainty_and_medical_copy() -> None:
    report = valid_report()
    report.executive_summary = f"{FORBIDDEN_COPY[0]} 반드시 사건이 발생하며 진단됩니다."

    codes = {issue.code for issue in validate_report(report, report.calculation_fingerprint)}

    assert {"event_certainty", "forbidden_copy", "medical_claim"} <= codes
    with pytest.raises(ReportQualityError):
        assert_report_quality(report, report.calculation_fingerprint)


def test_atomic_write_removes_temporary_file_after_replace_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    destination = tmp_path / "result.json"

    def fail_replace(source: str, target: Path) -> None:
        assert Path(source).exists()
        assert target == destination
        raise OSError("replace failed")

    monkeypatch.setattr(reporting_module.os, "replace", fail_replace)

    with pytest.raises(OSError, match="replace failed"):
        reporting_module._atomic_write(destination, b"payload")

    assert not list(tmp_path.glob(".result.json.*"))


@pytest.mark.asyncio
async def test_report_service_generate_uses_the_nim_boundary(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    entered: list[Settings] = []

    class FakeNimClient:
        def __init__(self, settings: Settings) -> None:
            entered.append(settings)

        async def __aenter__(self) -> object:
            return self

        async def __aexit__(self, *_: object) -> None:
            return None

    async def fake_generate_report(**payload: object) -> GeneratedReport:
        chart = payload["chart"]
        assert hasattr(chart, "fingerprint")
        report = valid_report().model_copy(
            update={"calculation_fingerprint": chart.fingerprint}
        )
        return GeneratedReport(report=report, traces={"fake": {"attempts": 1}})

    monkeypatch.setattr(service_module, "NimClient", FakeNimClient)
    monkeypatch.setattr(service_module, "generate_report", fake_generate_report)
    service = configured_service(tmp_path)

    bundle, generated = await service.generate(report_request())

    assert entered == [service.settings]
    assert generated.report.calculation_fingerprint == bundle.chart.fingerprint


@pytest.mark.asyncio
async def test_worker_sleeps_only_when_the_queue_is_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sleeps: list[float] = []

    class LoopService(ReportService):
        calls = 0

        async def process_next(self) -> object | None:
            self.calls += 1
            if self.calls == 1:
                return None
            if self.calls == 2:
                return object()
            raise StopAsyncIteration

    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    monkeypatch.setattr(service_module.asyncio, "sleep", fake_sleep)
    service = object.__new__(LoopService)

    with pytest.raises(StopAsyncIteration):
        await service.worker(0.25)

    assert sleeps == [0.25]


def test_artifact_reader_and_listing_cover_missing_and_symlinked_files(
    tmp_path: Path,
) -> None:
    service = configured_service(tmp_path)
    queued = service.store.create({"subject_name": "artifacts"})
    with pytest.raises(FileNotFoundError):
        service.artifact(queued.id, "report.pdf")

    service.store.claim_next()
    root = service.settings.artifact_dir / queued.id
    root.mkdir(parents=True)
    (root / "report.json").write_text('{"ok": true}', encoding="utf-8")
    outside = tmp_path / "outside.pdf"
    outside.write_bytes(b"outside")
    (root / "report.pdf").symlink_to(outside)
    completed = service.store.finish(queued.id, root)

    with pytest.raises(FileNotFoundError):
        service.artifact(completed.id, "report.pdf")
    with pytest.raises(FileNotFoundError):
        service.artifact(completed.id, "report.html")

    assert service.available_artifacts(completed.id) == ["report.json"]
    view = api_module._job_view(completed, service)
    assert view.artifacts == ["report.json"]


def test_package_main_invokes_the_cli_app(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[bool] = []
    monkeypatch.setattr(cli_module, "app", lambda: calls.append(True))
    sys.modules.pop("four_pillars.__main__", None)

    runpy.run_module("four_pillars.__main__", run_name="__main__")

    assert calls == [True]
