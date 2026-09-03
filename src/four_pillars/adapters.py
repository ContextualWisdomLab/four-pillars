"""Provide interpretation and filesystem application adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .analysis import GeneratedReport, generate_report
from .contextual_orchestrator import ContextualOrchestratorClient
from .models import Chart, DaewoonResult, LuckSnapshot, ReportDocument
from .ports import ReportInterpreter
from .reporting import write_artifacts
from .settings import Settings


class ContextualOrchestratorReportInterpreter:
    """Generate reports through the organization Contextual Orchestrator gateway."""

    def __init__(self, settings: Settings) -> None:
        """Store orchestrator connection settings without opening a client."""
        self.settings = settings

    async def generate(
        self,
        *,
        subject_name: str,
        chart: Chart,
        daewoon: DaewoonResult,
        annual: LuckSnapshot,
        monthly: LuckSnapshot,
        user_context: str,
    ) -> GeneratedReport:
        """Interpret immutable evidence through one bounded orchestrator client."""
        async with ContextualOrchestratorClient(self.settings) as client:
            return await generate_report(
                client=client,
                subject_name=subject_name,
                chart=chart,
                daewoon=daewoon,
                annual=annual,
                monthly=monthly,
                user_context=user_context,
            )


def build_report_interpreter(settings: Settings) -> ReportInterpreter:
    """Build the sole product-owned LLM adapter through Contextual Orchestrator."""
    return ContextualOrchestratorReportInterpreter(settings)


class FilesystemArtifactPublisher:
    """Publish approved report files through the atomic filesystem writer."""

    def publish(
        self,
        directory: Path,
        *,
        report: ReportDocument,
        chart: Chart,
        daewoon: DaewoonResult,
        annual: LuckSnapshot,
        monthly: LuckSnapshot,
        traces: dict[str, dict[str, Any]],
    ) -> dict[str, str]:
        """Create JSON, HTML, PDF, trace, and manifest artifacts in a new directory."""
        return write_artifacts(
            directory,
            report=report,
            chart=chart,
            daewoon=daewoon,
            annual=annual,
            monthly=monthly,
            traces=traces,
        )
