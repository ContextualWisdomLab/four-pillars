"""Provide the standalone NVIDIA NIM and filesystem application adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .analysis import GeneratedReport, generate_report
from .models import Chart, DaewoonResult, LuckSnapshot, ReportDocument
from .nim import NimClient
from .reporting import write_artifacts
from .settings import Settings


class NimReportInterpreter:
    """Generate schema-validated reports through the configured hosted NVIDIA NIM."""

    def __init__(self, settings: Settings) -> None:
        """Store the NIM connection and model settings without opening a network client."""
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
        """Open one bounded NIM client and interpret immutable calculation evidence."""
        async with NimClient(self.settings) as client:
            return await generate_report(
                client=client,
                subject_name=subject_name,
                chart=chart,
                daewoon=daewoon,
                annual=annual,
                monthly=monthly,
                user_context=user_context,
            )


class FilesystemArtifactPublisher:
    """Publish approved report files through the repository's atomic filesystem writer."""

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
