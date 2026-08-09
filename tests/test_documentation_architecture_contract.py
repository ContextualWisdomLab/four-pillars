"""Keep the canonical architecture documentation complete and internally coherent."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    """Return one repository Markdown document as UTF-8 text."""
    return (ROOT / path).read_text(encoding="utf-8")


def test_canonical_documentation_families_exist() -> None:
    """Require every acquisition-grade architecture document family."""
    required = (
        "docs/standards/DOCUMENTATION_AUDIT.md",
        "docs/standards/ARCHITECTURE_TRACEABILITY.md",
        "docs/doctoring/canonical-architecture-documentation.md",
        "docs/adr/README.md",
        "docs/adr/0004-purpose-bound-personal-data.md",
        "docs/adr/0005-architecture-description-and-maturity.md",
        "docs/adr/0006-calculation-evidence-provenance.md",
        "docs/adr/0007-autonomous-development-authority.md",
        "docs/architecture/SYSTEM_ARCHITECTURE.md",
        "docs/architecture/DATA_MODEL.md",
        "docs/uml/governance-and-data.md",
        "docs/security/THREAT_MODEL.md",
        "docs/technical/TEST_STRATEGY.md",
        "docs/operations/OPERABILITY.md",
        "docs/operations/AUTONOMOUS_DEVELOPMENT.md",
    )
    for relative_path in required:
        assert (ROOT / relative_path).is_file(), relative_path


def test_documentation_maturity_prevents_plans_from_becoming_shipped_claims() -> None:
    """Distinguish protected-main facts, accepted decisions, active PRs, and plans."""
    combined = "\n".join(
        (
            _text("docs/standards/DOCUMENTATION_AUDIT.md"),
            _text("docs/architecture/SYSTEM_ARCHITECTURE.md"),
            _text("docs/adr/0005-architecture-description-and-maturity.md"),
        )
    )
    for maturity in (
        "implemented_on_protected_main",
        "accepted_architecture",
        "active_pr",
        "planned",
        "superseded",
    ):
        assert maturity in combined
    assert "PR #29" in combined


def test_adr_index_names_existing_and_cross_cutting_decisions() -> None:
    """Make architecture decisions discoverable without reconstructing chat history."""
    index = _text("docs/adr/README.md")
    for decision in (
        "0001-deterministic-core-and-nim-boundary.md",
        "0002-nvidia-nim.md",
        "0003-explicit-contextual-orchestrator-backend.md",
        "0004-purpose-bound-personal-data.md",
        "0005-architecture-description-and-maturity.md",
        "0006-calculation-evidence-provenance.md",
        "0007-autonomous-development-authority.md",
    ):
        assert decision in index
    assert "supersed" in index.casefold()


def test_data_model_records_actual_standalone_schema_and_indexes() -> None:
    """Describe the durable queue that the standalone adapter really owns."""
    data_model = _text("docs/architecture/DATA_MODEL.md")
    for database_object in (
        "report_jobs",
        "idx_report_jobs_status_created",
        "idx_report_jobs_idempotency_key_digest",
        "idx_report_jobs_created_id",
        "idx_report_jobs_status_created_id",
    ):
        assert database_object in data_model
    assert "erDiagram" in data_model
    assert "request_json" in data_model
    assert "idempotency_key_digest" in data_model


def test_threat_model_uses_purpose_bound_privacy_not_blanket_masking() -> None:
    """Protect personal data without making the requested interpretation impossible."""
    threat_model = _text("docs/security/THREAT_MODEL.md").casefold()
    for phrase in (
        "purpose limitation",
        "blanket masking",
        "nvidia_nim_api_key",
        "contextual_orchestrator_token",
        "prompt injection",
        "retention",
        "deletion",
        "privileged access",
    ):
        assert phrase in threat_model


def test_test_strategy_requires_real_calculation_and_release_evidence() -> None:
    """Keep self-referential fixtures from becoming the only correctness oracle."""
    strategy = _text("docs/technical/TEST_STRATEGY.md")
    normalized = strategy.casefold()
    for evidence in (
        "KASI",
        "NAOJ",
        "Li Chun",
        "jie boundary",
        "100% production statement",
        "100% production branch",
        "NVIDIA_NIM_API_KEY",
    ):
        assert evidence.casefold() in normalized
    assert "independent" in normalized


def test_operability_covers_recovery_and_data_lifecycle() -> None:
    """Expose operational responsibilities that buyers and operators must verify."""
    operability = _text("docs/operations/OPERABILITY.md").casefold()
    for phrase in (
        "sli",
        "slo",
        "backup",
        "restore",
        "retention",
        "deletion",
        "incident",
        "multi-node",
        "artifact",
    ):
        assert phrase in operability


def test_autonomous_development_contract_is_work_conserving_and_safe() -> None:
    """Treat one PR as a safety bound rather than permission to stop early."""
    contract = _text("docs/operations/AUTONOMOUS_DEVELOPMENT.md")
    normalized = contract.casefold()
    for phrase in (
        "no-early-stop",
        "work-conserving",
        "waiting is local",
        "mandatory final sweep",
        "exact head",
        "exact live base",
        "NVIDIA_NIM_API_KEY",
        "COPILOT_GITHUB_TOKEN",
    ):
        assert phrase.casefold() in normalized


def test_prd_and_trd_link_the_canonical_architecture_graph() -> None:
    """Keep product and technical entry points connected to canonical evidence."""
    combined = _text("docs/product/PRD.md") + _text("docs/technical/TRD.md")
    for path in (
        "docs/architecture/DATA_MODEL.md",
        "docs/security/THREAT_MODEL.md",
        "docs/technical/TEST_STRATEGY.md",
        "docs/operations/OPERABILITY.md",
        "docs/standards/DOCUMENTATION_AUDIT.md",
    ):
        assert path in combined
    assert "purpose-bound" in combined.casefold()


def test_doctoring_tracks_current_and_draft_standards_separately() -> None:
    """Do not silently promote a public draft to final normative guidance."""
    doctoring = _text("docs/doctoring/canonical-architecture-documentation.md")
    assert "ISO/IEC/IEEE 42010:2022" in doctoring
    assert "ISO/IEC 25010:2023" in doctoring
    assert "ISO/IEC 42001:2023" in doctoring
    assert "ISO/IEC 23894:2023" in doctoring
    assert "NIST AI 600-1" in doctoring
    assert "SSDF Version 1.1" in doctoring
    assert "Version 1.2" in doctoring
    assert "Initial Public Draft" in doctoring


def test_traceability_maps_conversation_level_requirements_to_repository_evidence() -> None:
    """Keep cross-cutting architecture requirements connected to real evidence."""
    traceability = _text("docs/standards/ARCHITECTURE_TRACEABILITY.md")
    for requirement in (
        "Deterministic calculation is authoritative",
        "Purpose-bound personal data",
        "Safe idempotency",
        "Standalone + modular MSA",
        "Work-conserving autonomous development",
        "Backup/restore/retention/incident ownership",
    ):
        assert requirement in traceability
