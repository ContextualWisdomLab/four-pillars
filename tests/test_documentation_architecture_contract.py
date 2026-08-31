"""Keep the canonical architecture documentation complete and internally coherent."""

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
        "docs/technical/JOB_STATUS_SCHEMA.md",
        "docs/technical/TEST_STRATEGY.md",
        "docs/operations/OPERABILITY.md",
        "docs/operations/AUTONOMOUS_DEVELOPMENT.md",
        "docs/product-technical-gap-baseline.md",
    )
    for relative_path in required:
        assert (ROOT / relative_path).is_file(), relative_path


def test_product_technical_gap_baseline_is_evidence_bound() -> None:
    """Keep product priorities tied to maturity, proof, and acceptance evidence."""
    baseline = _text("docs/product-technical-gap-baseline.md")
    for phrase in (
        "implemented_on_protected_main",
        "active_pr",
        "planned",
        "superseded",
        "Acceptance evidence",
        "Contextual Orchestrator",
        "docs/product/PRD.md",
        "docs/technical/TRD.md",
        "docs/architecture/DATA_MODEL.md",
        "docs/security/THREAT_MODEL.md",
        "docs/technical/TEST_STRATEGY.md",
        "docs/operations/OPERABILITY.md",
        "scientific-prediction",
        "certification",
    ):
        assert phrase in baseline

    assert "PR #31 at `9a0ac33` (`active_pr`)" in baseline
    assert baseline.count("`active_pr` (#31)") == 2
    assert "`implemented_on_protected_main` (#31)" not in baseline


def test_documentation_maturity_has_canonical_labels_and_semantic_exclusivity() -> None:
    """Prevent active/planned claims from being classified as protected-main behavior."""
    audit = _text("docs/standards/DOCUMENTATION_AUDIT.md")
    architecture = _text("docs/architecture/SYSTEM_ARCHITECTURE.md")
    decision = _text("docs/adr/0005-architecture-description-and-maturity.md")
    combined = "\n".join((audit, architecture, decision))
    for maturity in (
        "implemented_on_protected_main",
        "accepted_architecture",
        "active_pr",
        "planned",
        "deprecated",
        "superseded",
    ):
        assert maturity in combined

    pr_steward_lines = [line for line in combined.splitlines() if "PR #29" in line]
    assert pr_steward_lines
    assert all("superseded" in line.casefold() for line in pr_steward_lines)
    assert "PR #29 is `active_pr`" not in combined
    assert "PR #29 is `implemented_on_protected_main`" not in combined

    planned_multi_node_lines = [
        line
        for line in combined.splitlines()
        if "multi-node" in line.casefold() and "planned" in line.casefold()
    ]
    assert planned_multi_node_lines
    assert all(
        "implemented_on_protected_main" not in line for line in planned_multi_node_lines
    )


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
    assert "Accepted with" not in index


def test_data_model_records_actual_schema_indexes_and_idempotency_syntax() -> None:
    """Describe the durable queue and its exact public idempotency contract."""
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
    for phrase in (
        "RFC 8941 structured-string",
        "8 through 128",
        "same key digest + different request fingerprint",
    ):
        assert phrase in data_model


def test_public_job_status_schema_is_redacted_and_bounded() -> None:
    """Define one canonical status projection instead of scattered field prose."""
    schema = _text("docs/technical/JOB_STATUS_SCHEMA.md")
    for allowed in (
        "`id`",
        "`status`",
        "`created_at`",
        "`updated_at`",
        "`error`",
        "`artifacts`",
        "4,000",
        "failed",
        "quality_failed",
    ):
        assert allowed in schema
    for forbidden_internal in (
        "`request_json`",
        "request fingerprint",
        "idempotency-key digest",
        "internal artifact directory",
    ):
        assert forbidden_internal in schema


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
        "credential-free verification",
        "fail closed",
        "NVIDIA_NIM_API_KEY",
        "COPILOT_GITHUB_TOKEN",
        "processing purpose is explicitly approved",
        "versioned model-input allow-list/schema",
    ):
        assert phrase.casefold() in normalized


def test_uml_matches_real_port_method_names() -> None:
    """Keep diagrams from inventing a second MSA contract."""
    uml = _text("docs/uml/governance-and-data.md")
    for signature in (
        "+finish(job_id, artifact_dir) ReportJob",
        "+fail(job_id, error, quality=false) ReportJob",
        "+purge(retention_days)",
        "+generate(subject_name, chart, daewoon, annual, monthly, user_context)",
        "+publish(directory, report, chart, daewoon, annual, monthly, traces)",
    ):
        assert signature in uml
    assert "+complete(job_id, artifact_dir)" not in uml
    assert "+publish(staged_path, job_id)" not in uml


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
    assert "(SSDF) Version 1.1" in doctoring
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
