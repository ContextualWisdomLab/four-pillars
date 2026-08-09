# Canonical Architecture Documentation Design

**Status:** Approved-for-execution by repository-owner instruction  
**Date:** 2026-08-09  
**Scope:** Documentation architecture, documentation quality gates, and autonomous-development control context for Four Pillars.

## Problem

Four Pillars already has a substantive PRD, TRD, root architecture description, UML views, three accepted architecture decisions, calculation documentation, API documentation, runbooks, security policy, standards references, and research traceability. That set is strong enough to explain the current product, but it is not yet sufficient as an acquisition-grade canonical architecture record.

The missing information is concentrated in five places:

1. there is no authoritative ADR index with decision ownership and supersession links;
2. there is no logical ERD/data-model document connecting the durable SQLite schema to replaceable MSA persistence ports;
3. security policy exists, but there is no explicit threat model and purpose-bound PII control model;
4. testing and operability are described inside the TRD/runbook but not exposed as independently auditable release contracts;
5. documentation has no maturity vocabulary that distinguishes protected-main reality, accepted architecture, active-PR work, and future plans. This permits PR bodies and chat history to look more authoritative than protected-main code.

The current product-development prompt also reads all operations documentation. A canonical autonomous-development contract can therefore remove the observed premature-stop pattern without racing the active PR-steward branch or duplicating repository writers.

## Chosen approach

Add a **canonical documentation graph** on a branch based on protected `main`, using only paths that do not overlap the active PR-steward source branch. Do not rewrite `AGENTS.md`, `CLAUDE.md`, root `ARCHITECTURE.md`, `SECURITY.md`, `CHANGELOG.md`, or `scripts/check_docs.py` while PR #29 is actively modifying them.

The new graph consists of:

- `docs/standards/DOCUMENTATION_AUDIT.md` — completeness/maturity matrix;
- `docs/adr/README.md` — ADR index and supersession policy;
- `docs/adr/0004-purpose-bound-personal-data.md` — privacy decision without blanket masking;
- `docs/adr/0005-architecture-description-and-maturity.md` — canonical-truth and maturity decision;
- `docs/architecture/SYSTEM_ARCHITECTURE.md` — viewpoint-based architecture description;
- `docs/architecture/DATA_MODEL.md` — logical ERD and persistence invariants;
- `docs/security/THREAT_MODEL.md` — assets, actors, trust boundaries, threats, controls, residual risks;
- `docs/technical/TEST_STRATEGY.md` — realistic calculation/LLM/API/release evidence contract;
- `docs/operations/OPERABILITY.md` — SLI/SLO, recovery, retention, backup, incident and MSA responsibilities;
- `docs/operations/AUTONOMOUS_DEVELOPMENT.md` — work-conserving prompt context read by the existing minute-47 OpenCode workflow;
- `tests/test_documentation_architecture_contract.py` — machine-checkable documentation baseline.

PRD and TRD are updated narrowly to point to the new canonical documents and to state the purpose-bound privacy and documentation-maturity requirements. Root architecture and shared agent files are deliberately deferred until PR #29 lands, at which point one follow-up synchronization commit may update those overlapping paths from the merged baseline.

## Architecture-description model

ISO/IEC/IEEE 42010:2022 separates an architecture from its architecture description and requires explicit concerns, stakeholders, viewpoints, and model kinds. Four Pillars therefore treats the following as first-class viewpoints:

- product and buyer concerns;
- deterministic calculation and provenance;
- interpretation/LLM trust boundary;
- persistence and artifact lifecycle;
- privacy/security/data rights;
- standalone deployment;
- organization MSA integration;
- autonomous development/review/release governance;
- verification and operational recovery.

Each document states its maturity:

- **implemented_on_protected_main** — directly supported by the current protected-main source;
- **accepted_architecture** — approved design constraint with implementation mapping;
- **active_pr** — not shipped; exists only on an open PR;
- **planned** — future work; must not be described as current capability;
- **deprecated/superseded** — historical decision retained for traceability.

## Privacy decision

Do not blanket-mask birth data or report context when doing so prevents the service from functioning. Instead classify and minimize by purpose, restrict access, encrypt transport/storage, isolate credentials and identity linkage, use redacted public history/telemetry, bound retention, support deletion/export, and audit privileged access. Personal data may cross the model boundary only when required to perform the requested interpretation and only through the selected backend's documented processor/retention contract.

This is a design-for-readiness mapping for CSAP/SOC 2 style controls, not a certification claim.

## Automation decision

The minute-17 deterministic sentinel, minute-47 OpenCode product-development workflow, and proposed minute-07 PR steward have different roles. The new autonomous-development document defines a no-early-stop/work-conserving contract while preserving one source writer per branch and exact-head governance. The product-development workflow still creates at most one bounded PR per run; “one PR” is a safety boundary, not permission to stop after one inventory, RCA, documentation edit, or test result.

## Verification

The documentation contract test checks:

- all canonical document families exist;
- ADR index names existing decisions;
- ERD contains the actual `report_jobs` table and compliant index names;
- threat model records purpose-bound PII handling and secret separation;
- test strategy requires independent solar-term fixtures and 100% production statement/branch coverage;
- operability defines recovery, retention, deletion, backup, and incident responsibilities;
- autonomous-development contract contains no-early-stop, exact-head, NVIDIA_NIM_API_KEY, and COPILOT_GITHUB_TOKEN prohibition clauses;
- maturity vocabulary prevents active-PR claims from being represented as protected-main reality.

## Standards and evidence

The documentation model is grounded in current primary sources and the repository's existing research traceability. The governing references for this increment are:

- International Organization for Standardization. (2022). *ISO/IEC/IEEE 42010:2022 Software, systems and enterprise—Architecture description* (2nd ed.). ISO.
- International Organization for Standardization. (2023). *ISO/IEC 25010:2023 Systems and software engineering—Systems and software Quality Requirements and Evaluation (SQuaRE)—Product quality model* (2nd ed.). ISO.
- International Organization for Standardization. (2023). *ISO/IEC 23894:2023 Information technology—Artificial intelligence—Guidance on risk management*. ISO.
- International Organization for Standardization. (2023). *ISO/IEC 42001:2023 Information technology—Artificial intelligence—Management system*. ISO.
- Autio, C., Schwartz, R., Dunietz, J., Jain, S., Stanley, M., Tabassi, E., Hall, P., & Roberts, K. (2024). *Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile* (NIST AI 600-1). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.AI.600-1
- Scarfone, K., Souppaya, M., & Dodson, D. (2022). *Secure Software Development Framework (SSDF) Version 1.1: Recommendations for mitigating the risk of software vulnerabilities* (NIST SP 800-218). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-218

NIST's SP 800-218 Rev. 1 / SSDF 1.2 is an initial public draft as of 2026-08; it may inform future work but is not treated as a final normative source in this baseline.
