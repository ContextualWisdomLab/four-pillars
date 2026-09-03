"""Verify the hourly autonomous product-quality and gap-audit contract."""

from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path
from types import ModuleType

import pytest

WORKFLOW = Path(".github/workflows/hourly-product-loop.yml")
AUDIT_SCRIPT = Path("scripts/product_gap_audit.py")
RUNBOOK = Path("docs/operations/HOURLY_PRODUCT_LOOP.md")
REFERENCES = Path("docs/standards/REFERENCES.md")
TRACEABILITY = Path("docs/standards/TRACEABILITY.md")


def load_audit_module() -> ModuleType:
    """Import the product-gap audit script as a testable module."""
    spec = importlib.util.spec_from_file_location("product_gap_audit", AUDIT_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_hourly_workflow_is_scheduled_and_manually_dispatchable() -> None:
    """Run the loop once per hour and permit an operator to invoke it on demand."""
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "schedule:" in text
    assert "cron: '17 * * * *'" in text
    assert "workflow_dispatch:" in text
    assert "issues: write" in text
    assert "contents: read" in text
    assert "concurrency:" in text


def test_hourly_workflow_runs_the_full_release_gate_and_manages_one_issue() -> None:
    """Exercise every release gate and keep failures in one idempotent GitHub issue."""
    text = WORKFLOW.read_text(encoding="utf-8")

    for command in (
        "python scripts/product_gap_audit.py",
        "ruff check .",
        "python -m compileall -q src tests scripts",
        "python scripts/check_docs.py",
        "python scripts/check_prompts.py",
        "pytest -m 'not orchestrator_live'",
        "python -m build --no-isolation",
    ):
        assert command in text
    assert "[hourly-product-loop] release-quality regression" in text
    assert "gh issue create" in text
    assert "gh issue comment" in text
    assert "gh issue close" in text
    assert "NVIDIA_NIM_API_KEY" not in text
    assert "OPENAI_API_KEY" not in text
    assert "CONTEXTUAL_ORCHESTRATOR_TOKEN" not in text


def test_hourly_issue_sync_treats_setup_or_loop_skips_as_failures() -> None:
    """Never close a regression issue when setup failed before the loop produced outputs."""
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "steps.loop.outcome != 'success'" in text
    assert 'if [ ! -f "$report" ]; then' in text
    assert "Hourly loop did not produce a report" in text


def test_product_gap_audit_passes_the_repository_contract() -> None:
    """Report no release, orchestration, standards, prompt, or naming gaps."""
    module = load_audit_module()

    assert module.audit_repository(Path(".")) == []


def assert_token_contract_detects_missing_entries(
    tmp_path: Path,
    contracts: tuple[tuple[str, str], ...],
    audit_name: str,
) -> None:
    """Exercise every token contract with missing-file and missing-token cases."""
    module = load_audit_module()
    audit = getattr(module, audit_name)
    root = tmp_path / audit_name
    original_contents: dict[Path, str] = {}
    for relative, token in contracts:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        current = path.read_text(encoding="utf-8") if path.is_file() else ""
        path.write_text(f"{current}\n{token}\n", encoding="utf-8")
        original_contents[path] = path.read_text(encoding="utf-8")

    assert audit(root) == []

    for relative, token in contracts:
        path = root / relative
        path.unlink()
        missing_file = audit(root)
        assert any(gap.path == relative for gap in missing_file)

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(original_contents[path], encoding="utf-8")
        path.write_text("different contract", encoding="utf-8")
        missing_token = audit(root)
        assert any(gap.path == relative and token in gap.message for gap in missing_token)
        path.write_text(original_contents[path], encoding="utf-8")

    assert audit(root) == []


def test_report_history_contract_audit_detects_missing_tokens(tmp_path: Path) -> None:
    """Keep history code, indexes, API, and modular documentation in one audited unit."""
    module = load_audit_module()
    assert_token_contract_detects_missing_entries(
        tmp_path,
        module.HISTORY_CONTRACTS,
        "audit_history_contract",
    )


def test_interpretation_contract_audit_detects_missing_tokens(tmp_path: Path) -> None:
    """Keep orchestration settings, ACL adapters, tests, and operations docs aligned."""
    module = load_audit_module()
    assert_token_contract_detects_missing_entries(
        tmp_path,
        module.INTERPRETATION_CONTRACTS,
        "audit_interpretation_contract",
    )


def test_interpretation_audit_rejects_provider_runtime_configuration(tmp_path: Path) -> None:
    """Fail the architecture gate when product env docs advertise a provider-native route."""
    module = load_audit_module()
    root = tmp_path / "provider-runtime"
    for relative, token in module.INTERPRETATION_CONTRACTS:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(token, encoding="utf-8")
    env_path = root / ".env.example"
    env_path.write_text(
        env_path.read_text(encoding="utf-8") + "\nNVIDIA_NIM_API_KEY=forbidden\n",
        encoding="utf-8",
    )

    gaps = module.audit_interpretation_contract(root)

    assert any(gap.code == "direct_provider_runtime_config" for gap in gaps)


def test_standards_contract_audit_detects_missing_tokens(tmp_path: Path) -> None:
    """Keep APA references and standards traceability inside the hourly gate."""
    module = load_audit_module()
    assert_token_contract_detects_missing_entries(
        tmp_path,
        module.STANDARDS_CONTRACTS,
        "audit_standards_contract",
    )


def test_authority_fixture_contract_audit_detects_missing_tokens(
    tmp_path: Path,
) -> None:
    """Keep official solar-term evidence and provenance inside the hourly gate."""
    module = load_audit_module()
    assert_token_contract_detects_missing_entries(
        tmp_path,
        module.AUTHORITY_FIXTURE_CONTRACTS,
        "audit_authority_fixture_contract",
    )


def test_standards_doctoring_contains_authoritative_and_peer_reviewed_sources() -> None:
    """Document current software, astronomy, AI, HTTP, tracing, and evaluation evidence."""
    references = REFERENCES.read_text(encoding="utf-8")
    traceability = TRACEABILITY.read_text(encoding="utf-8")

    for token in (
        "APA 7th",
        "ISO/IEC Standard No. 25010:2023",
        "ISO/IEC Standard No. 42001:2023",
        "ISO/IEC Standard No. 23894:2023",
        "NIST AI 600-1",
        "RFC 9457",
        "W3C recommendation",
        "Korea Astronomy and Space Science Institute",
        "National Astronomical Observatory of Japan",
        "Planetary theories in rectangular",
        "10.3847/1538-3881/abd414",
        "10.18653/v1/2024.emnlp-main.427",
        "10.18653/v1/2024.emnlp-main.474",
    ):
        assert token in references
    for token in (
        "StructuredGenerationClient",
        "ContextualOrchestratorClient",
        "orchestrator/free",
        "traditional interpretation",
        "100% statement and branch coverage",
        "kasi_2026_jie_terms.json",
    ):
        assert token in traceability


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("report_jobs", True),
        ("idx_report_jobs_status_created", True),
        ("idx_report_jobs_created_id", True),
        ("idx_report_jobs_status_created_id", True),
        ("ReportJobs", True),
        ("reportJobs", True),
        ("jobs", False),
        ("report-jobs", False),
        ("Report_Jobs", False),
    ],
)
def test_database_identifier_policy_requires_two_word_supported_case(
    name: str,
    expected: bool,
) -> None:
    """Accept only two-word snake_case, camelCase, or PascalCase database names."""
    module = load_audit_module()

    assert module.is_valid_database_identifier(name) is expected


def test_database_schema_uses_only_policy_compliant_object_names(tmp_path: Path) -> None:
    """Apply the naming policy to every application-created SQLite schema object."""
    from four_pillars.jobs import JobStore

    database = tmp_path / "audit.sqlite3"
    JobStore(database)
    with sqlite3.connect(database) as connection:
        names = [
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table','index')"
            )
            if not row[0].startswith("sqlite_")
        ]
    module = load_audit_module()

    assert names
    assert all(module.is_valid_database_identifier(name) for name in names)


def test_hourly_loop_runbook_explains_scope_failure_and_recovery() -> None:
    """Give operators enough context to understand and recover the scheduled loop."""
    text = RUNBOOK.read_text(encoding="utf-8")

    for heading in (
        "## Schedule",
        "## Shared autonomous development loop",
        "## Release-quality gate",
        "## Product-gap audit",
        "## Failure issue lifecycle",
        "## Security and orchestration boundary",
        "## Manual recovery",
    ):
        assert heading in text
