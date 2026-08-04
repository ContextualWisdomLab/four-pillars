"""Verify settings-driven interpretation backend selection and port compatibility."""

from __future__ import annotations

from pathlib import Path

from four_pillars.adapters import (
    ContextualOrchestratorReportInterpreter,
    NimReportInterpreter,
    build_report_interpreter,
)
from four_pillars.ports import ReportInterpreter
from four_pillars.service import ReportService
from four_pillars.settings import Settings


def settings(tmp_path: Path, **updates: object) -> Settings:
    """Return isolated service settings with optional backend overrides."""
    values: dict[str, object] = {
        "artifact_dir": tmp_path / "artifacts",
        "database_url": f"sqlite:///{tmp_path / 'report_jobs.sqlite3'}",
    }
    values.update(updates)
    return Settings(**values)


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
