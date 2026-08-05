"""Verify settings-driven interpretation backend selection and port compatibility."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from test_quality import valid_report

import four_pillars
from four_pillars.adapters import (
    ContextualOrchestratorReportInterpreter,
    NimReportInterpreter,
    build_report_interpreter,
)
from four_pillars.analysis import GeneratedReport
from four_pillars.generation import GenerationTrace, StructuredGenerationClient
from four_pillars.models import BirthInput, Gender
from four_pillars.nim import NimTrace
from four_pillars.ports import ReportInterpreter
from four_pillars.service import (
    ReportRequest,
    ReportService,
    calculate_bundle,
)
from four_pillars.settings import Settings


def settings(tmp_path: Path, **updates: object) -> Settings:
    """Return isolated service settings with optional backend overrides."""
    values: dict[str, object] = {
        "artifact_dir": tmp_path / "artifacts",
        "database_url": f"sqlite:///{tmp_path / 'report_jobs.sqlite3'}",
    }
    values.update(updates)
    return Settings(**values)


def request() -> ReportRequest:
    """Return deterministic evidence input for one adapter call."""
    return ReportRequest(
        subject_name="통합 사용자",
        birth=BirthInput(
            birth=datetime(1990, 6, 15, 8, 30),
            timezone="Asia/Seoul",
            gender=Gender.FEMALE,
        ),
        annual_year=2026,
        monthly_year=2026,
        monthly_month=8,
        user_context="orchestrator adapter evidence",
    )


def test_top_level_package_exports_modular_interpretation_contract() -> None:
    """Expose integration ports without requiring internal module imports."""
    assert four_pillars.GenerationTrace is GenerationTrace
    assert NimTrace is GenerationTrace
    assert four_pillars.StructuredGenerationClient is StructuredGenerationClient
    assert four_pillars.build_report_interpreter is build_report_interpreter
    assert (
        four_pillars.ContextualOrchestratorReportInterpreter
        is ContextualOrchestratorReportInterpreter
    )


def test_backend_factory_preserves_direct_nim_default(tmp_path: Path) -> None:
    """Keep direct NVIDIA NIM as the standalone interpretation default."""
    configured = settings(tmp_path)

    interpreter = build_report_interpreter(configured)

    assert isinstance(interpreter, NimReportInterpreter)
    assert isinstance(interpreter, ReportInterpreter)


def test_backend_factory_builds_contextual_orchestrator_adapter(tmp_path: Path) -> None:
    """Select the organization orchestrator only when explicitly configured."""
    configured = settings(
        tmp_path,
        interpretation_backend="contextual_orchestrator",
        contextual_orchestrator_token="test-token",
    )

    interpreter = build_report_interpreter(configured)

    assert isinstance(interpreter, ContextualOrchestratorReportInterpreter)
    assert isinstance(interpreter, ReportInterpreter)


def test_report_service_uses_settings_factory_for_standalone_default(tmp_path: Path) -> None:
    """Compose the selected adapter without changing explicit dependency injection."""
    configured = settings(
        tmp_path,
        interpretation_backend="contextual_orchestrator",
        contextual_orchestrator_token="test-token",
    )

    service = ReportService(configured)

    assert isinstance(service.interpreter, ContextualOrchestratorReportInterpreter)


def test_report_service_preserves_an_explicit_interpreter(tmp_path: Path) -> None:
    """Never replace a caller-supplied MSA interpreter with a settings default."""
    configured = settings(
        tmp_path,
        interpretation_backend="contextual_orchestrator",
        contextual_orchestrator_token="test-token",
    )
    injected = NimReportInterpreter(configured)

    service = ReportService(configured, interpreter=injected)

    assert service.interpreter is injected


@pytest.mark.asyncio
async def test_orchestrator_adapter_forwards_immutable_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Open the selected client and pass every calculated model unchanged."""
    configured = settings(
        tmp_path,
        interpretation_backend="contextual_orchestrator",
        contextual_orchestrator_token="test-token",
    )
    report_request = request()
    bundle = calculate_bundle(report_request)
    expected = GeneratedReport(report=valid_report(), traces={})
    calls: list[dict[str, Any]] = []

    class FakeClient:
        """Minimal asynchronous client context used by the adapter test."""

        def __init__(self, received: Settings) -> None:
            self.received = received

        async def __aenter__(self) -> FakeClient:
            calls.append({"settings": self.received, "client": self})
            return self

        async def __aexit__(self, *_: object) -> None:
            return None

    async def fake_generate_report(**kwargs: Any) -> GeneratedReport:
        calls.append(kwargs)
        return expected

    monkeypatch.setattr(
        "four_pillars.adapters.ContextualOrchestratorClient",
        FakeClient,
    )
    monkeypatch.setattr(
        "four_pillars.adapters.generate_report",
        fake_generate_report,
    )
    interpreter = ContextualOrchestratorReportInterpreter(configured)

    generated = await interpreter.generate(
        subject_name=report_request.subject_name,
        chart=bundle.chart,
        daewoon=bundle.daewoon,
        annual=bundle.annual,
        monthly=bundle.monthly,
        user_context=report_request.user_context,
    )

    assert generated is expected
    assert calls[0]["settings"] is configured
    assert calls[1]["client"] is calls[0]["client"]
    assert calls[1]["subject_name"] == "통합 사용자"
    assert calls[1]["chart"] is bundle.chart
    assert calls[1]["daewoon"] is bundle.daewoon
    assert calls[1]["annual"] is bundle.annual
    assert calls[1]["monthly"] is bundle.monthly
    assert calls[1]["user_context"] == "orchestrator adapter evidence"
