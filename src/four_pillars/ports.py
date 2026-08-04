"""Define structural application ports for standalone and MSA integrations."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from .models import (
    Chart,
    DaewoonResult,
    LuckSnapshot,
    ReportDocument,
    ReportJob,
)

if TYPE_CHECKING:
    from .analysis import GeneratedReport


@runtime_checkable
class ReportJobRepository(Protocol):
    """Persist and transition durable report jobs behind the application service."""

    def create(self, request: dict[str, Any]) -> ReportJob:
        """Create one queued report job."""
        ...  # pragma: no cover - structural typing declaration

    def get(self, job_id: str) -> ReportJob | None:
        """Return one report job or ``None`` when it does not exist."""
        ...  # pragma: no cover - structural typing declaration

    def claim_next(self) -> ReportJob | None:
        """Atomically claim the next queued report job."""
        ...  # pragma: no cover - structural typing declaration

    def finish(self, job_id: str, artifact_dir: Path) -> ReportJob:
        """Transition a running job to completed with its artifact directory."""
        ...  # pragma: no cover - structural typing declaration

    def fail(self, job_id: str, error: str, *, quality: bool = False) -> ReportJob:
        """Transition a job to an operational or quality failure state."""
        ...  # pragma: no cover - structural typing declaration

    def delete(self, job_id: str) -> bool:
        """Delete one terminal job and return whether a row was removed."""
        ...  # pragma: no cover - structural typing declaration

    def purge(self, retention_days: int) -> list[str]:
        """Delete expired terminal rows and return their job identifiers."""
        ...  # pragma: no cover - structural typing declaration


@runtime_checkable
class ReportInterpreter(Protocol):
    """Interpret immutable chart and luck evidence into one validated report."""

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
        """Generate a report without mutating deterministic evidence."""
        ...  # pragma: no cover - structural typing declaration


@runtime_checkable
class ArtifactPublisher(Protocol):
    """Publish approved report artifacts into a caller-supplied staging directory."""

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
        """Create all artifacts and return their content digests."""
        ...  # pragma: no cover - structural typing declaration
