from __future__ import annotations

import runpy
import sys
from datetime import datetime
from pathlib import Path

import pytest
from test_quality import valid_report

import four_pillars.adapters as adapters_module
import four_pillars.api as api_module
import four_pillars.cli as cli_module
import four_pillars.prompts as prompts_module
import four_pillars.reporting as reporting_module
import four_pillars.service as service_module
from four_pillars.analysis import GeneratedReport
from four_pillars.constants import FORBIDDEN_COPY
from four_pillars.jobs import JobStore
from four_pillars.models import BirthInput, Gender
from four_pillars.quality import ReportQualityError, assert_report_quality, validate_report
from four_pillars.settings import Settings


def report_request() -> service_module.ReportRequest:
    return service_module.ReportRequest(
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


def configured_service(tmp_path: Path) -> service_module.ReportService:
    settings = Settings(
        artifact_dir=tmp_path / "artifacts",
        database_url=f"sqlite:///{tmp_path / 'jobs.sqlite3'}",
    )
    return service_module.ReportService(settings, JobStore(settings.sqlite_path))


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
        prompts_module.load_prompt(prompts_module.PROMPT_NAMES[0])


def test_prompt_manifest_can_skip_an_empty_template(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_load(name: str) -> prompts_module.PromptTemplate | None:
        if name == prompts_module.PROMPT_NAMES[0]:
            return None
        return prompts_module.PromptTemplate(
            name=name,
            version="1.0.0",
            body="body",
            sha256="a" * 64,
        )

    monkeypatch.setattr(prompts_module, "load_prompt", fake_load)

    manifest = prompts_module.prompt_manifest()

    assert prompts_module.PROMPT_NAMES[0] not in manifest
    assert set(manifest) == set(prompts_module.PROMPT_NAMES[1:])


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

    monkeypatch.setattr(adapters_module, "NimClient", FakeNimClient)
    monkeypatch.setattr(adapters_module, "generate_report", fake_generate_report)
    service = configured_service(tmp_path)

    bundle, generated = await service.generate(report_request())

    assert entered == [service.settings]
    assert generated.report.calculation_fingerprint == bundle.chart.fingerprint


@pytest.mark.asyncio
async def test_worker_sleeps_only_when_the_queue_is_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sleeps: list[float] = []

    class LoopService(service_module.ReportService):
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
