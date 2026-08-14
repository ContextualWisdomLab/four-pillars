"""Lock the canonical Four Pillars documentation graph to current code contracts."""

from pathlib import Path

CANONICAL_FILES = (
    "README.md",
    "SECURITY.md",
    "AGENTS.md",
    "CLAUDE.md",
    "ARCHITECTURE.md",
    "CHANGELOG.md",
    "docs/product/PRD.md",
    "docs/technical/TRD.md",
    "docs/technical/API.md",
    "docs/technical/CALCULATION.md",
    "docs/technical/MODULARITY.md",
    "docs/operations/NIM.md",
    "docs/operations/RUNBOOK.md",
    "docs/operations/HOURLY_PRODUCT_LOOP.md",
    "docs/operations/HOURLY_NIM_PRODUCT_DEVELOPMENT.md",
    "docs/design/FIGMA.md",
    "docs/architecture/DOCUMENTATION_MAP.md",
    "docs/architecture/DOCUMENTATION_AUDIT_2026-08-09.md",
    "docs/adr/README.md",
    "docs/adr/0001-deterministic-core-and-nim-boundary.md",
    "docs/adr/0002-nvidia-nim.md",
    "docs/adr/0003-explicit-contextual-orchestrator-backend.md",
    "docs/adr/0004-purpose-bound-personal-data-controls.md",
    "docs/adr/0005-documentation-as-code-authority.md",
    "docs/adr/0006-standalone-modular-msa-boundary.md",
    "docs/adr/0007-autonomous-control-plane-authority.md",
    "docs/adr/0008-solar-term-evidence-and-calculation-versioning.md",
    "docs/adr/0009-release-provenance-and-operational-acceptance.md",
    "docs/erd/domain-model.md",
    "docs/uml/architecture.md",
    "docs/uml/control-plane.md",
    "docs/uml/domain.puml",
    "docs/security/DATA_GOVERNANCE.md",
    "docs/security/THREAT_MODEL.md",
    "docs/compliance/CSAP_SOC2_READINESS.md",
    "docs/doctoring/documentation-governance.md",
    "docs/doctoring/kasi-solar-term-golden-fixtures.md",
    "docs/standards/REFERENCES.md",
    "docs/standards/TRACEABILITY.md",
)


def _text(path: str) -> str:
    """Return one canonical UTF-8 documentation file after proving it exists."""
    document = Path(path)
    assert document.is_file(), f"canonical documentation is missing: {path}"
    text = document.read_text(encoding="utf-8")
    assert len(text.strip()) >= 120, f"canonical documentation is unexpectedly short: {path}"
    return text


def test_canonical_documentation_graph_is_present() -> None:
    """Keep every canonical architecture, decision, data, and assurance view in Git."""
    for path in CANONICAL_FILES:
        _text(path)


def test_adr_index_tracks_current_decisions_and_statuses() -> None:
    """Require the ADR index to expose accepted evidence and proposed gaps honestly."""
    index = _text("docs/adr/README.md")
    for number in range(1, 10):
        assert f"[{number:04d}]" in index
    assert "0008-solar-term-evidence-and-calculation-versioning.md" in index
    assert "| Accepted | Validate boundary-critical solar terms" in index
    assert "0004-purpose-bound-personal-data-controls.md" in index
    assert "0007-autonomous-control-plane-authority.md" in index
    assert "0009-release-provenance-and-operational-acceptance.md" in index
    assert index.count("| Proposed |") >= 5


def test_contextual_orchestrator_documentation_matches_production_native_json_mode() -> None:
    """Prevent docs from reintroducing provider-native JSON where the adapter disables it."""
    production = Path("src/four_pillars/contextual_orchestrator.py").read_text(encoding="utf-8")
    assert "native_json_mode=False" in production

    product = _text("docs/product/PRD.md")
    assert "shall not force provider-native JSON response mode" in product
    assert "Pydantic" in product
    assert "no backend may silently fail over" in product.casefold()

    for path in (
        "docs/technical/TRD.md",
        "docs/technical/MODULARITY.md",
        "docs/operations/NIM.md",
        "docs/uml/architecture.md",
        "docs/standards/TRACEABILITY.md",
    ):
        text = _text(path)
        if path == "docs/operations/NIM.md":
            assert "The orchestrator adapter deliberately omits `response_format`" in text
        else:
            assert "native_json_mode=False" in text
        assert "Pydantic" in text
        fallback_contract = {
            "docs/technical/TRD.md": "never silently fails over to another backend",
            "docs/technical/MODULARITY.md": "a failed selection never changes providers silently",
            "docs/operations/NIM.md": "never silently routes to another provider or adapter",
            "docs/uml/architecture.md": "visible failures rather than provider fallback",
            "docs/standards/TRACEABILITY.md": "no silent provider fallback",
        }
        assert fallback_contract[path] in text.casefold()


def test_calculation_policy_names_external_evidence_version_and_accepted_adr() -> None:
    """Bind the buyer-visible calculation policy to external evidence and versioning."""
    calculation = _text("docs/technical/CALCULATION.md")
    for token in (
        "calendar-1.1.0",
        "KASI",
        "NAOJ",
        "120 seconds",
        "ADR 0008",
        "A fixture is never regenerated from Four Pillars output",
    ):
        assert token in calculation


def test_modularity_forbids_shared_application_database_coupling() -> None:
    """Keep standalone and MSA composition behind versioned ports rather than table access."""
    modularity = _text("docs/technical/MODULARITY.md")
    for token in (
        "No shared application database",
        "versioned APIs, events, structural ports, or immutable artifacts",
        "must not reach directly into Four Pillars application tables",
        "must not depend on another service's private tables",
        "Purpose-bound personal data",
    ):
        assert token in modularity


def test_data_model_names_only_the_current_application_table_as_persisted() -> None:
    """Keep the ERD honest about SQLite persistence and descriptive object naming."""
    model = _text("docs/erd/domain-model.md")
    for token in (
        "report_jobs",
        "idx_report_jobs_status_created",
        "idx_report_jobs_idempotency_key_digest",
        "idx_report_jobs_created_id",
        "idx_report_jobs_status_created_id",
        "Only `report_job` maps to a current application-owned database table",
    ):
        assert token in model
    assert "retention_action` is conceptual today" in model


def test_personal_data_governance_preserves_necessary_pii_without_ambient_propagation() -> None:
    """Require purpose-bound privacy controls rather than business-breaking blanket masking."""
    governance = _text("docs/security/DATA_GOVERNANCE.md")
    for token in (
        "not blanket masking",
        "purpose-required",
        "break-glass",
        "encryption at rest",
        "retention",
        "deletion",
        "export",
        "NVIDIA_NIM_API_KEY",
        "CONTEXTUAL_ORCHESTRATOR_TOKEN",
    ):
        assert token.casefold() in governance.casefold()


def test_threat_model_covers_runtime_and_repository_invariants() -> None:
    """Keep the repository threat model scoped to assets, inputs, boundaries, and invariants."""
    threat_model = _text("docs/security/THREAT_MODEL.md")
    for token in (
        "Assets",
        "Trust boundaries",
        "Attacker-controlled or untrusted inputs",
        "Core security invariants",
        "Calculation integrity",
        "Authorization and privacy",
        "Repository governance",
        "NVIDIA_NIM_API_KEY",
        "Repository: ContextualWisdomLab/four-pillars",
        "Version: cd4f4e6361238a1db43c28540640a407c7bf7c6e",
    ):
        assert token in threat_model


def test_assurance_document_does_not_claim_external_certification() -> None:
    """Keep CSAP and SOC 2 as evidence-readiness targets rather than repository badges."""
    readiness = _text("docs/compliance/CSAP_SOC2_READINESS.md")
    assert "Certification/attestation status: **none claimed**" in readiness
    for token in ("CSAP", "SOC 2", "operating evidence", "independent", "KMS", "tenant"):
        assert token.casefold() in readiness.casefold()


def test_control_plane_distinguishes_current_and_proposed_automation() -> None:
    """Do not document the unmerged PR steward as protected-main behavior."""
    control_plane = _text("docs/uml/control-plane.md")
    assert "Minute-17 quality sentinel\\nImplemented" in control_plane
    assert "Minute-47 NVIDIA/OpenCode product developer\\nImplemented" in control_plane
    assert "Minute-07 PR steward\\nProposed" in control_plane
    assert "no approval / merge / release authority" in control_plane


def test_standards_catalog_contains_current_architecture_privacy_and_assurance_sources() -> None:
    """Preserve current authoritative sources needed by the documentation baseline."""
    references = _text("docs/standards/REFERENCES.md")
    for token in (
        "ISO/IEC/IEEE Standard No. 42010:2022",
        "ISO/IEC/IEEE Standard No. 29148:2018",
        "OMG Unified Modeling Language",
        "ISO/IEC Standard No. 27001:2022",
        "ISO/IEC Standard No. 27701:2025",
        "NIST Special Publication 800-207",
        "클라우드 서비스 보안인증제 안내서",
        "Trust Services Criteria",
        "Korea Astronomy and Space Science Institute",
        "National Astronomical Observatory of Japan",
    ):
        assert token in references


def test_doctoring_records_version_sensitive_claim_boundaries() -> None:
    """Require APA-backed doctoring for standards, assurance, and current code semantics."""
    doctoring = _text("docs/doctoring/documentation-governance.md")
    for token in (
        "APA 7th references",
        "native_json_mode=False",
        "ISO/IEC/IEEE 42010:2022",
        "ISO/IEC/IEEE 29148:2018",
        "ISO/IEC 27701:2025",
        "CSAP",
        "SOC 2",
        "NVIDIA_NIM_API_KEY",
        "Proposed",
    ):
        assert token in doctoring


def test_traceability_preserves_release_quality_and_credential_contracts() -> None:
    """Keep machine-readable quality and credential names synchronized with policy."""
    traceability = _text("docs/standards/TRACEABILITY.md")
    for token in (
        "ContextualOrchestratorClient",
        "StructuredGenerationClient",
        "NVIDIA_NIM_API_KEY",
        "CONTEXTUAL_ORCHESTRATOR_TOKEN",
        "100% statement and branch coverage",
        "traditional interpretation",
        "calendar-1.1.0",
    ):
        assert token in traceability
