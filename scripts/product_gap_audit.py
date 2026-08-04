"""Audit release, modularity, interpretation, standards, and database naming."""

from __future__ import annotations

import argparse
import re
import sqlite3
import tempfile
import tomllib
from pathlib import Path
from typing import NamedTuple

from four_pillars.jobs import JobStore
from four_pillars.prompts import PROMPT_NAMES, prompt_manifest


class ProductGap(NamedTuple):
    """One statically detectable product or release-quality gap."""

    code: str
    severity: str
    path: str
    message: str


REQUIRED_DOCUMENTS = (
    "README.md",
    "CHANGELOG.md",
    "docs/product/PRD.md",
    "docs/technical/TRD.md",
    "docs/technical/CALCULATION.md",
    "docs/technical/API.md",
    "docs/technical/MODULARITY.md",
    "docs/operations/NIM.md",
    "docs/operations/RUNBOOK.md",
    "docs/operations/HOURLY_PRODUCT_LOOP.md",
    "docs/standards/REFERENCES.md",
    "docs/standards/TRACEABILITY.md",
    "docs/uml/architecture.md",
    "docs/uml/domain.puml",
)
REQUIRED_WORKFLOWS = (
    ".github/workflows/hourly-product-loop.yml",
    ".github/workflows/release.yml",
)
HISTORY_CONTRACTS = (
    ("src/four_pillars/ports.py", "class ReportJobHistoryRepository"),
    ("src/four_pillars/jobs.py", "idx_report_jobs_created_id"),
    ("src/four_pillars/jobs.py", "idx_report_jobs_status_created_id"),
    ("src/four_pillars/api.py", "class ReportJobPageView"),
    ("docs/technical/API.md", "### Report history"),
    (
        "docs/technical/MODULARITY.md",
        "### Optional report-job history repository",
    ),
)
INTERPRETATION_CONTRACTS = (
    ("src/four_pillars/generation.py", "class StructuredGenerationClient"),
    (
        "src/four_pillars/contextual_orchestrator.py",
        "class ContextualOrchestratorClient",
    ),
    (
        "src/four_pillars/adapters.py",
        "class ContextualOrchestratorReportInterpreter",
    ),
    ("src/four_pillars/adapters.py", "def build_report_interpreter"),
    ("src/four_pillars/settings.py", "contextual_orchestrator_token"),
    (".env.example", "INTERPRETATION_BACKEND=nvidia_nim"),
    (".env.example", "CONTEXTUAL_ORCHESTRATOR_TOKEN="),
    ("docs/operations/NIM.md", "No implicit fallback"),
)
STANDARDS_CONTRACTS = (
    ("docs/standards/REFERENCES.md", "APA 7th"),
    ("docs/standards/REFERENCES.md", "ISO/IEC 25010:2023"),
    ("docs/standards/REFERENCES.md", "ISO/IEC 42001:2023"),
    ("docs/standards/REFERENCES.md", "ISO/IEC 23894:2023"),
    ("docs/standards/REFERENCES.md", "NIST AI 600-1"),
    ("docs/standards/REFERENCES.md", "RFC 9457"),
    ("docs/standards/REFERENCES.md", "W3C"),
    (
        "docs/standards/REFERENCES.md",
        "10.18653/v1/2024.emnlp-main.427",
    ),
    (
        "docs/standards/REFERENCES.md",
        "10.18653/v1/2024.emnlp-main.474",
    ),
    ("docs/standards/TRACEABILITY.md", "traditional interpretation"),
    (
        "docs/standards/TRACEABILITY.md",
        "100% statement and branch coverage",
    ),
)
TEXT_SUFFIXES = {".md", ".py", ".toml", ".yaml", ".yml"}
IGNORED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "artifacts",
    "build",
    "dist",
    "tests",
}
SNAKE_CASE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)+$")
CAMEL_CASE = re.compile(r"^[a-z][a-z0-9]+(?:[A-Z][a-z0-9]+)+$")
PASCAL_CASE = re.compile(r"^[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+$")


def is_valid_database_identifier(name: str) -> bool:
    """Return whether a database object uses a supported two-word identifier style."""
    return bool(
        SNAKE_CASE.fullmatch(name)
        or CAMEL_CASE.fullmatch(name)
        or PASCAL_CASE.fullmatch(name)
    )


def _gap(code: str, path: str, message: str, severity: str = "high") -> ProductGap:
    return ProductGap(code=code, severity=severity, path=path, message=message)


def _text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or IGNORED_PARTS.intersection(path.parts):
            continue
        if path.name == ".env.example" or path.suffix in TEXT_SUFFIXES:
            files.append(path)
    return files


def _database_names() -> list[str]:
    with tempfile.TemporaryDirectory(prefix="four-pillars-audit-") as temporary:
        database = Path(temporary) / "audit.sqlite3"
        JobStore(database)
        with sqlite3.connect(database) as connection:
            return [
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type IN ('table','index')"
                )
                if not row[0].startswith("sqlite_")
            ]


def _audit_token_contracts(
    root: Path,
    contracts: tuple[tuple[str, str], ...],
    *,
    code: str,
    label: str,
) -> list[ProductGap]:
    gaps: list[ProductGap] = []
    for relative, token in contracts:
        path = root / relative
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        if token not in text:
            gaps.append(
                _gap(
                    code,
                    relative,
                    f"{label} is missing {token!r}.",
                )
            )
    return gaps


def audit_history_contract(root: Path) -> list[ProductGap]:
    """Return gaps in the optional report-history code and documentation contract."""
    return _audit_token_contracts(
        root,
        HISTORY_CONTRACTS,
        code="report_history_contract",
        label="Report-history contract",
    )


def audit_interpretation_contract(root: Path) -> list[ProductGap]:
    """Return gaps in explicit interpretation backend and credential boundaries."""
    return _audit_token_contracts(
        root,
        INTERPRETATION_CONTRACTS,
        code="interpretation_backend_contract",
        label="Interpretation-backend contract",
    )


def audit_standards_contract(root: Path) -> list[ProductGap]:
    """Return gaps in APA references and standards-to-control traceability."""
    return _audit_token_contracts(
        root,
        STANDARDS_CONTRACTS,
        code="standards_traceability_contract",
        label="Standards traceability",
    )


def audit_repository(root: Path) -> list[ProductGap]:
    """Return release-quality gaps that can be verified without network access."""
    root = root.resolve()
    gaps: list[ProductGap] = []

    for relative in REQUIRED_DOCUMENTS:
        path = root / relative
        if not path.is_file():
            gaps.append(
                _gap(
                    "missing_document",
                    relative,
                    "Required product or operations document is missing.",
                )
            )
        elif len(path.read_text(encoding="utf-8").strip()) < 120:
            gaps.append(
                _gap(
                    "thin_document",
                    relative,
                    "Required document is too short to be operationally useful.",
                )
            )

    for relative in REQUIRED_WORKFLOWS:
        if not (root / relative).is_file():
            gaps.append(
                _gap(
                    "missing_workflow",
                    relative,
                    "Required governance workflow is missing.",
                )
            )

    gaps.extend(audit_history_contract(root))
    gaps.extend(audit_interpretation_contract(root))
    gaps.extend(audit_standards_contract(root))

    pyproject_path = root / "pyproject.toml"
    version_path = root / "src/four_pillars/version.py"
    changelog_path = root / "CHANGELOG.md"
    if pyproject_path.is_file():
        pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        project_version = str(pyproject.get("project", {}).get("version", ""))
        coverage_floor = (
            pyproject.get("tool", {})
            .get("coverage", {})
            .get("report", {})
            .get("fail_under")
        )
        if coverage_floor != 100:
            gaps.append(
                _gap(
                    "coverage_floor",
                    "pyproject.toml",
                    "Statement and branch coverage must fail below 100%.",
                )
            )
        if version_path.is_file():
            match = re.search(
                r'^__version__\s*=\s*["\']([^"\']+)["\']',
                version_path.read_text(encoding="utf-8"),
                flags=re.MULTILINE,
            )
            runtime_version = match.group(1) if match else ""
            if runtime_version != project_version:
                gaps.append(
                    _gap(
                        "version_mismatch",
                        "src/four_pillars/version.py",
                        "Runtime and package versions differ.",
                    )
                )
        if (
            changelog_path.is_file()
            and f"## [{project_version}]"
            not in changelog_path.read_text(encoding="utf-8")
        ):
            gaps.append(
                _gap(
                    "missing_release_notes",
                    "CHANGELOG.md",
                    "Current package version has no changelog entry.",
                )
            )

    legacy_key = "NVIDIA_" + "API_KEY"
    for path in _text_files(root):
        if legacy_key in path.read_text(encoding="utf-8", errors="ignore"):
            gaps.append(
                _gap(
                    "legacy_nim_key",
                    path.relative_to(root).as_posix(),
                    "Use NVIDIA_NIM_API_KEY exclusively for direct hosted NVIDIA NIM.",
                )
            )

    manifest = prompt_manifest()
    if set(manifest) != set(PROMPT_NAMES):
        gaps.append(
            _gap(
                "prompt_manifest",
                "src/four_pillars/prompts",
                "Prompt manifest is incomplete.",
            )
        )
    for name, metadata in manifest.items():
        if not re.fullmatch(r"\d+\.\d+\.\d+", metadata["version"]):
            gaps.append(
                _gap(
                    "prompt_version",
                    f"src/four_pillars/prompts/{name}.md",
                    "Prompt version is not semantic.",
                )
            )
        if not re.fullmatch(r"[0-9a-f]{64}", metadata["sha256"]):
            gaps.append(
                _gap(
                    "prompt_digest",
                    f"src/four_pillars/prompts/{name}.md",
                    "Prompt digest is not SHA-256.",
                )
            )

    for name in _database_names():
        if not is_valid_database_identifier(name):
            gaps.append(
                _gap(
                    "database_identifier",
                    "src/four_pillars/jobs.py",
                    f"Database object {name!r} violates the naming policy.",
                )
            )

    for relative in ("src/four_pillars/calendar.py", "src/four_pillars/fortune.py"):
        text = (root / relative).read_text(encoding="utf-8")
        for forbidden_dependency in ("fastapi", "httpx"):
            if forbidden_dependency in text:
                gaps.append(
                    _gap(
                        "calculation_boundary",
                        relative,
                        f"Deterministic calculation core must not depend on {forbidden_dependency}.",
                    )
                )

    hourly_workflow = root / ".github/workflows/hourly-product-loop.yml"
    if hourly_workflow.is_file():
        workflow_text = hourly_workflow.read_text(encoding="utf-8")
        if (
            "cron: '17 * * * *'" not in workflow_text
            or "workflow_dispatch:" not in workflow_text
        ):
            gaps.append(
                _gap(
                    "hourly_schedule",
                    hourly_workflow.relative_to(root).as_posix(),
                    "Hourly schedule or manual dispatch is missing.",
                )
            )
        for secret in ("NVIDIA_NIM_API_KEY", "CONTEXTUAL_ORCHESTRATOR_TOKEN"):
            if secret in workflow_text:
                gaps.append(
                    _gap(
                        "hourly_secret_boundary",
                        hourly_workflow.relative_to(root).as_posix(),
                        f"Hourly quality workflow must not receive {secret}.",
                    )
                )

    release_workflow = root / ".github/workflows/release.yml"
    if release_workflow.is_file():
        workflow_text = release_workflow.read_text(encoding="utf-8")
        required_release_tokens = (
            "workflow_call:",
            "contents: write",
            "python scripts/release_notes.py",
            "gh release view",
            "gh release create",
        )
        if not all(token in workflow_text for token in required_release_tokens):
            gaps.append(
                _gap(
                    "release_workflow",
                    release_workflow.relative_to(root).as_posix(),
                    "Release workflow is incomplete or not reusable.",
                )
            )
        for secret in ("NVIDIA_NIM_API_KEY", "CONTEXTUAL_ORCHESTRATOR_TOKEN"):
            if secret in workflow_text:
                gaps.append(
                    _gap(
                        "release_secret_boundary",
                        release_workflow.relative_to(root).as_posix(),
                        f"Release workflow must not receive {secret}.",
                    )
                )

    return sorted(
        gaps,
        key=lambda item: (item.severity, item.code, item.path, item.message),
    )


def render_markdown(gaps: list[ProductGap]) -> str:
    """Render a concise Markdown report suitable for logs and an issue body."""
    lines = [
        "# Hourly Product Gap Audit",
        "",
        f"Status: **{'PASS' if not gaps else 'FAIL'}**",
        f"Detected gaps: **{len(gaps)}**",
        "",
    ]
    if not gaps:
        lines.append(
            "All deterministic release, modularity, interpretation, standards, "
            "prompt, credential, and database naming contracts passed."
        )
    else:
        lines.extend(
            ("| Severity | Code | Path | Finding |", "|---|---|---|---|")
        )
        for gap in gaps:
            message = gap.message.replace("|", "\\|")
            lines.append(
                f"| {gap.severity} | `{gap.code}` | `{gap.path}` | {message} |"
            )
    return "\n".join(lines) + "\n"


def main() -> int:
    """Run the offline audit, write optional Markdown output, and return status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    gaps = audit_repository(arguments.root)
    report = render_markdown(gaps)
    print(report, end="")
    if arguments.output is not None:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(report, encoding="utf-8")
    return 1 if gaps else 0


if __name__ == "__main__":
    raise SystemExit(main())
