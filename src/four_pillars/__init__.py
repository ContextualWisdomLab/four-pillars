"""Deterministic Four Pillars calculation with replaceable interpretation adapters."""

from .adapters import (
    ContextualOrchestratorReportInterpreter,
    NimReportInterpreter,
    build_report_interpreter,
)
from .calendar import calculate_chart
from .fortune import calculate_annual_luck, calculate_daewoon, calculate_monthly_luck
from .generation import StructuredGenerationClient
from .models import BirthInput, Chart, Gender
from .ports import (
    ArtifactPublisher,
    IdempotentReportJobRepository,
    ReportInterpreter,
    ReportJobHistoryRepository,
    ReportJobRepository,
)
from .version import __version__

__all__ = [
    "ArtifactPublisher",
    "BirthInput",
    "Chart",
    "ContextualOrchestratorReportInterpreter",
    "Gender",
    "IdempotentReportJobRepository",
    "NimReportInterpreter",
    "ReportInterpreter",
    "ReportJobHistoryRepository",
    "ReportJobRepository",
    "StructuredGenerationClient",
    "__version__",
    "build_report_interpreter",
    "calculate_annual_luck",
    "calculate_chart",
    "calculate_daewoon",
    "calculate_monthly_luck",
]
