# Four Pillars Documentation Audit — 2026-08-09

## Scope

This audit evaluates whether the repository documentation is sufficient to reconstruct the product and control plane described by current protected-main code and the active development history without relying on chat transcripts. It checks product requirements, technical requirements, architecture, ADRs, UML, ERD/data authority, API/calculation contracts, privacy/security/compliance, operations, standards/research traceability, release evidence and autonomous repository governance.

Baseline inspected: protected `main` at `cd4f4e6361238a1db43c28540640a407c7bf7c6e`. Active minute-07 PR steward work is unmerged and therefore classified Proposed rather than Current.

## Verdict before this baseline

**Substantial but not sufficient.** Existing PRD, TRD, root Architecture, three ADRs, runtime UML, API/calculation/modularity docs, operations, standards/doctoring and release history provided strong coverage. However, the repository still depended on implicit knowledge for the data model, documentation authority, privacy strategy, assurance readiness and autonomous-control-plane authority. One TRD statement also contradicted production Contextual Orchestrator request semantics.

## Gap matrix

| Documentation family | Prior state | Audit finding | Baseline action |
|---|---|---|---|
| PRD | Strong | Missing current calculation-evidence scope, control-plane requirements, no-blanket-masking strategy, CSAP/SOC 2 readiness and documentation-as-product requirements | Updated |
| TRD | Strong but stale in one material area | Incorrectly implied Contextual Orchestrator provider-native JSON `response_format`; lacked ERD/data-governance/control-plane/compliance detail | Updated to `native_json_mode=False` reality and expanded |
| Root Architecture | Strong | Current runtime/deployment view but minute-07 steward and new documentation/data-governance views not yet integrated | Follow-up after steward merge to avoid active-file conflict |
| ADRs | Incomplete | Only 0001–0003; no index/lifecycle and missing privacy, documentation, MSA/control-plane decisions | Added index and Proposed ADRs 0004–0007 |
| UML/runtime | Strong | Contextual Orchestrator JSON wording could mislead; no data/automation authority view | Updated runtime UML and added control-plane UML |
| ERD/data model | Missing | No canonical persisted-vs-conceptual data authority model | Added `docs/erd/domain-model.md` |
| Privacy/data governance | Fragmented | Security/privacy rules existed across TRD/API/runbooks but no explicit purpose-bound alternative to blanket PII masking | Added `docs/security/DATA_GOVERNANCE.md` and ADR 0004 |
| CSAP/SOC 2 readiness | Missing | No explicit separation of source controls, deployment gaps and external assessment claims | Added readiness map |
| Standards catalog | Good | Missing ISO/IEC/IEEE 42010, ISO/IEC/IEEE 29148, UML, current ISO 27701, ISO 27001, CSAP and SOC 2 sources | Updated |
| Traceability | Good but stale | Incorrect Contextual Orchestrator `response_format` statement; missing docs/privacy/assurance/control-plane mappings | Updated |
| API contract | Strong | No blocking gap identified in this audit | Keep code-current |
| Calculation/provenance | Strong | KASI/NAOJ + `calendar-1.1.0` already materially improved evidence | Referenced from PRD/TRD/ERD |
| Operations | Strong | New PR steward runbook lives in active PR and remains Proposed | Integrate only after PR merge |
| AGENTS/CLAUDE | Strong, actively changing | Active PR #29 modifies both; avoid competing writer changes | Follow up after active PR |
| CHANGELOG | Strong, actively changing | Active PR #29 modifies it; docs baseline should not create a conflicting release claim | Follow up after active PR |
| Figma | Adequate for current stable browser workflow | No new visual workflow is required by documentation baseline | No redesign |

## Material defect found

Protected-main `src/four_pillars/contextual_orchestrator.py` constructs `ContextualOrchestratorClient` with `native_json_mode=False`. The prior TRD and standards traceability described the gateway path as using `response_format={"type":"json_object"}`. That statement was code-stale and risked making future maintainers reintroduce a gateway passthrough behavior the implementation deliberately avoided.

The updated TRD/UML/traceability now state:

- direct NVIDIA NIM may use provider-native JSON mode;
- Contextual Orchestrator currently does not receive native JSON `response_format` from Four Pillars;
- Four Pillars instead requires JSON in its prompt, parses/validates with Pydantic and uses bounded same-backend repair;
- selected-backend failure still has no silent provider fallback.

## Current/Proposed boundary

The minute-17 deterministic quality sentinel and minute-47 NVIDIA/OpenCode product-development control plane are Current protected-main behavior. The minute-07 exact-head PR steward is Proposed while PR #29 is unmerged. This baseline's control-plane diagram and ADR 0007 label it accordingly. After the PR merges, its documentation status and root architecture/AGENTS/CLAUDE/CHANGELOG integration must be updated in a follow-up exact-head documentation pass.

## Remaining repository work after this baseline

1. Merge/fix active PR #29 under normal exact-head review/check governance.
2. After merge, update root `ARCHITECTURE.md`, `AGENTS.md`, `CLAUDE.md`, `CHANGELOG.md`, and `scripts/check_docs.py` from the integrated protected head rather than racing the active branch.
3. Promote ADR 0007 from Proposed to Accepted only after protected-main PR-steward implementation and operational acceptance exist.
4. Promote ADR 0005 when canonical-file/link/index consistency tests are integrated.
5. Promote ADR 0004 only after the remaining production tenant/KMS/break-glass/backup/export evidence exists; do not falsely claim completion.
6. Promote ADR 0006 after the current port/no-shared-DB rules and intended remote-adapter contracts are machine-checked at the authoritative documentation boundary.
7. Add a release/provenance ADR if release/SBOM/signing policy becomes materially more detailed than current workflow documentation.
8. Continue adding independent calendar fixtures beyond 2026 and historical-time policy evidence as product scope expands.

## Acceptance criterion

Documentation is considered sufficient only when the repository can answer, without chat history:

- what the product promises and deliberately does not promise;
- which calculation facts are authoritative and how they are independently tested;
- how AI can and cannot affect those facts;
- how standalone and organization deployments differ;
- what is actually persisted and who owns it;
- where personal data is necessary, where it is prohibited, how access/retention/deletion/export is controlled, and which controls remain deployment gaps;
- which automation can propose, verify, review, merge and release;
- which standards/research sources support each material design claim and what they do **not** prove;
- which work is Current, Accepted, Proposed or Planned;
- how to operate, recover, roll back and release the product.

This baseline closes the largest missing-document families; remaining items above are intentionally recorded as follow-up defects rather than silently described as complete.
