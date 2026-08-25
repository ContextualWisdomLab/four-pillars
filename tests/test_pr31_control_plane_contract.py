"""Fail closed when canonical architecture evidence preserves obsolete repair authority."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    """Return one repository document as UTF-8 text."""
    return (ROOT / path).read_text(encoding="utf-8")


def test_one_shot_repair_workflow_is_absent_from_reviewed_product_tree() -> None:
    """A reviewed PR must not carry a branch-writing self-repair workflow."""
    assert not (ROOT / ".github/workflows/repair-pr31-ci.yml").exists()


def test_closed_pr_steward_is_documented_only_as_superseded_history() -> None:
    """Closed, unmerged PR #29 cannot remain active or shipped authority."""
    documents = (
        "docs/standards/DOCUMENTATION_AUDIT.md",
        "docs/adr/0005-architecture-description-and-maturity.md",
        "docs/architecture/SYSTEM_ARCHITECTURE.md",
        "docs/operations/AUTONOMOUS_DEVELOPMENT.md",
    )
    lines = [
        line
        for document in documents
        for line in _text(document).splitlines()
        if "PR #29" in line
    ]
    assert lines
    assert all("superseded" in line.casefold() for line in lines)
    assert all(
        "active_pr" not in line and "implemented_on_protected_main" not in line
        for line in lines
    )


def test_autonomous_maturity_requires_protected_main_and_full_evidence() -> None:
    """A merge alone must never upgrade an automation contract to shipped truth."""
    contract = _text("docs/operations/AUTONOMOUS_DEVELOPMENT.md").casefold()
    assert "only after integration into protected main at an exact commit" in contract
    for evidence in ("ci", "security", "coverage", "review", "provenance", "operational"):
        assert evidence in contract


def test_final_sweep_has_versioned_fail_closed_machine_record() -> None:
    """Termination evidence must be machine-auditable rather than internal prose only."""
    contract = _text("docs/operations/AUTONOMOUS_DEVELOPMENT.md")
    for field in (
        "final_sweep_record_v1",
        "scope",
        "protected_main_sha",
        "live_base_sha",
        "source_head_sha",
        "required_documents",
        "gate_results",
        "remaining_executable_work",
        "remaining_budget",
        "final_decision",
        "recorded_at",
        "provenance",
    ):
        assert field in contract
    normalized = contract.casefold()
    for state in ("missing", "stale", "unknown"):
        assert state in normalized
    assert "fail closed" in normalized
