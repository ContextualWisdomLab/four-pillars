# Four Pillars Authoritative Documentation Map

- Status: Current documentation authority map
- Baseline: protected `main` at `cd4f4e6361238a1db43c28540640a407c7bf7c6e`
- Reviewed: 2026-08-09

## Purpose

Four Pillars must be understandable and operable from the repository without reconstructing chat history, pull-request bodies, or historical implementation notes. This file identifies the canonical documentation surfaces, their authority, and the event that requires each surface to be reviewed.

This map follows the architecture-description separation in ISO/IEC/IEEE 42010:2022 and the requirements-information discipline in ISO/IEC/IEEE 29148:2018. ISO/IEC/IEEE 29148:2018 remains the published current edition as of this review, although an Edition 3 DIS is under development; Four Pillars must not treat the draft as a normative replacement before publication.

## Authority order

When documentation conflicts, use this order to determine what must be repaired:

1. **Protected production code and executable tests** define implemented behavior.
2. **Accepted ADRs** define intentional architecture decisions unless superseded.
3. **PRD/TRD and public API/calculation contracts** define current released requirements and externally meaningful behavior.
4. **Architecture/UML/ERD/security/operations documents** explain the current design and control boundaries.
5. **Doctoring and standards traceability** explain external evidence, claim boundaries, and residual risks.
6. **Historical Superpowers specs/plans and PR bodies** are implementation history, not current authority.

A conflict between levels is a repository defect; do not silently pick whichever prose is convenient.

## Canonical graph

| Concern | Canonical artifact | Minimum update trigger |
|---|---|---|
| Product problem, users, requirements, metrics, scope | `docs/product/PRD.md` | Buyer-visible behavior, major workflow, scope, success metric, privacy or integration contract changes |
| Technical requirements and system contracts | `docs/technical/TRD.md` | Component, persistence, calculation, model, API, reliability, security or deployment semantics change |
| System architecture | `ARCHITECTURE.md` | Bounded context, trust boundary, deployment topology, control plane or integration ownership changes |
| Architecture decisions | `docs/adr/README.md` and numbered ADRs | Material architectural decision, supersession, reversal condition or migration policy changes |
| UML / behavioral views | `docs/uml/architecture.md`, `docs/uml/control-plane.md` | Component, sequence, state, authority or deployment behavior changes |
| Durable/conceptual data model | `docs/erd/domain-model.md` | Database schema, persistence adapter, artifact/provenance model or data authority changes |
| Public API and schemas | `docs/technical/API.md` | Endpoint, status, idempotency, cursor, authorization, error or schema version changes |
| Deterministic calculation | `docs/technical/CALCULATION.md` | Calendar/time policy, solar-term solver, evidence version, external fixture or boundary budget changes |
| Standalone/MSA composition | `docs/technical/MODULARITY.md` | Port, adapter, cross-service ownership, queue/storage or orchestrator integration changes |
| AI/provider operations | `docs/operations/NIM.md` | Provider, credential, retry, repair, routing or live-evaluation behavior changes |
| Runtime operations | `docs/operations/RUNBOOK.md` | Worker lifecycle, retention, deletion, recovery, backup/restore, SLO or incident behavior changes |
| Personal-data governance | `docs/security/DATA_GOVERNANCE.md` | Data categories, authorization, retention, linkage, model payload or audit policy changes |
| CSAP/SOC 2 readiness | `docs/compliance/CSAP_SOC2_READINESS.md` | Control design/evidence, hosting boundary, subprocessors, audit scope or readiness status changes |
| Security policy | `SECURITY.md` | Vulnerability intake, supported versions, privileged workflows or security gates change |
| External standards/research | `docs/standards/REFERENCES.md` | Relied-on standard/paper is added, revised, withdrawn or superseded |
| Standard-to-code mapping | `docs/standards/TRACEABILITY.md` | Control implementation, test, residual gap or acceptance evidence changes |
| Release history | `CHANGELOG.md` | Any user/operator/security-visible shipped change |
| Automation operator contract | `AGENTS.md`, `CLAUDE.md` | Writer lease, review/merge authority, quality gate or autonomous-loop contract changes |
| UI source of truth | `docs/design/FIGMA.md` plus referenced Figma file/frames | Stable user-facing layout or workflow changes |

## Current completeness assessment

The repository already has substantial PRD, TRD, calculation/API/modularity, operations, standards, three ADRs, root architecture, UML, security guidance, Figma references, AGENTS/CLAUDE, and CHANGELOG coverage. The remaining documentation defects identified in the 2026-08-09 audit are being closed by this baseline:

- there was no ADR index or documented ADR lifecycle/supersession rule;
- there was no authoritative conceptual/logical ERD distinguishing the actual SQLite table from non-persisted evidence/artifact concepts;
- the control-plane diagrams did not cover the minute-17 quality sentinel, minute-47 NVIDIA/OpenCode product-development workflow, or the proposed minute-07 PR steward as separate authority zones;
- there was no explicit purpose-bound personal-data governance document expressing the product decision not to rely on blanket PII masking;
- there was no explicit CSAP/SOC 2 readiness map separating engineering preparation from certification/attestation claims;
- the TRD described Contextual Orchestrator native JSON response semantics inconsistently with production `ContextualOrchestratorClient(native_json_mode=False)` and therefore required correction;
- standards references lacked the architecture-description, requirements-engineering, UML, current privacy-management, information-security, SOC 2 Trust Services Criteria, and CSAP sources used by this documentation baseline.

## Shipped versus proposed

Architecture documents must label unmerged work explicitly. In particular, the minute-07 PR steward is **Proposed / under review** until its feature PR reaches protected `main`; diagrams may show it only with a Proposed marker. The minute-17 quality sentinel and minute-47 NVIDIA/OpenCode development loop are implemented protected-main control planes. Planned PostgreSQL/object-storage adapters, RFC 9457 responses, W3C Trace Context propagation, and deeper orchestration ablations remain Planned until separately reviewed implementation lands.

## Documentation acceptance

A documentation change is acceptable only when:

- claims match protected production code or are explicitly marked Proposed/Planned;
- accepted architectural decisions are indexed and are not contradicted without a superseding ADR;
- diagrams preserve calculation, interpretation, quality, delivery, review, merge, release and automation authority separation;
- data-model documents distinguish persisted entities from conceptual/derived artifacts;
- security/privacy documents use purpose-bound controls and do not claim CSAP, SOC 2, ISO, or scientific certification without external evidence;
- material external sources are recorded in APA 7th style in `docs/standards/REFERENCES.md` or the relevant doctoring record;
- relevant tests/checks can detect stale version, naming, file, or contract assertions where practical.

## References

International Organization for Standardization, International Electrotechnical Commission, & Institute of Electrical and Electronics Engineers. (2022). *Software, systems and enterprise—Architecture description* (ISO/IEC/IEEE Standard No. 42010:2022). https://www.iso.org/standard/74393.html

International Organization for Standardization, International Electrotechnical Commission, & Institute of Electrical and Electronics Engineers. (2018). *Systems and software engineering—Life cycle processes—Requirements engineering* (ISO/IEC/IEEE Standard No. 29148:2018). https://www.iso.org/standard/72089.html

Object Management Group. (2017). *OMG Unified Modeling Language (OMG UML), version 2.5.1*. https://www.omg.org/spec/UML/2.5.1
