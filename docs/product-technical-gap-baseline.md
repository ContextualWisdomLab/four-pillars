# Four Pillars Product and Technical Gap Baseline

**Audit date:** 2026-08-31  
**Protected-main baseline:** `cd4f4e6361238a1db43c28540640a407c7bf7c6e`  
**Documentation source:** PR #31 at `9a0ac33` (`active_pr`)  
**Maturity vocabulary:** ADR 0005

## Purpose and evidence rules

This baseline turns the PRD, TRD, architecture, ADR, research, implementation,
tests, operations, and live pull-request evidence into one prioritized product
gap register. It does not replace those authoritative documents. A capability is
`implemented_on_protected_main` only when protected-main source and required
operational evidence prove it. Open work is `active_pr`; unimplemented work is
`planned`; closed, unmerged PR #29 is `superseded`.

Local tests, plans, PR prose, mergeability, and queued Checks are not release
evidence. Certification, customer, revenue, production, transfer, acquisition,
attestation, and scientific-prediction claims require their own external proof
and are not inferred here.

## Product boundary

Four Pillars owns deterministic Korean Four Pillars calculation, immutable
calculation evidence, schema-validated interpretation, durable report jobs,
privacy-safe recovery, and HTML/PDF/JSON artifacts. It supports a standalone
deployment and replaceable MSA ports. Direct NVIDIA NIM is the standalone model
adapter; an organization deployment may instead use Contextual Orchestrator.
Four Pillars does not define Contextual Orchestrator's internal provider
inventory.

The product does not claim that traditional interpretation is a scientifically
validated prediction of a person's future. It does not provide medical diagnosis
or automatic high-stakes decisions.

## Canonical specification map

| Concern | Authority | Current evidence |
|---|---|---|
| Product users, stories, scope, NFRs, metrics | `docs/product/PRD.md` | versioned product contract |
| Components, data flow, trust boundaries, release rules | `docs/technical/TRD.md` | technical contract and implementation links |
| System viewpoints and modular boundary | `docs/architecture/SYSTEM_ARCHITECTURE.md`, `docs/technical/MODULARITY.md` | standalone and MSA responsibilities |
| Domain and interaction views | `docs/uml/architecture.md`, `docs/uml/domain.puml`, `docs/uml/governance-and-data.md` | component, sequence, state, and domain diagrams |
| Durable data and indexes | `docs/architecture/DATA_MODEL.md` | logical ERD matched to `report_jobs` |
| Decisions and supersession | `docs/adr/README.md` | ADR 0001 through ADR 0007 |
| Calculation policy and provenance | `docs/technical/CALCULATION.md`, ADR 0006 | KASI/NAOJ fixtures and calculation version |
| API and public job projection | `docs/technical/API.md`, `docs/technical/JOB_STATUS_SCHEMA.md` | schema and privacy contracts |
| Security and personal data | `SECURITY.md`, `docs/security/THREAT_MODEL.md`, ADR 0004 | purpose-bound processing and secret separation |
| Quality and release proof | `docs/technical/TEST_STRATEGY.md` | 100% owned statement/branch coverage and independent fixtures |
| Lifecycle and recovery | `docs/operations/OPERABILITY.md`, `docs/operations/RUNBOOK.md` | SLI/SLO, backup, restore, retention, incident duties |
| Standards and research | `docs/standards/REFERENCES.md`, `docs/standards/TRACEABILITY.md` | APA 7 references and claim limits |
| Documentation fitness | `docs/standards/DOCUMENTATION_AUDIT.md`, `docs/standards/ARCHITECTURE_TRACEABILITY.md` | maturity and cross-document consistency |

## Functional baseline

| Capability | Maturity | Evidence | Acceptance boundary |
|---|---|---|---|
| Natal chart and luck calculation | `implemented_on_protected_main` | deterministic core, golden cases, calculation fingerprint | supported input policies remain versioned and independently checked |
| Li Chun and twelve `jie` boundaries | `implemented_on_protected_main` | KASI/NAOJ 2026 fixtures and transition tests | broader historical claims require new independent evidence |
| Korean lunar regular/leap input | `implemented_on_protected_main` | explicit calendar/leap flag and conversion tests | no inference of leap month from a solar date |
| Civil, mean-solar, apparent-solar policies | `active_pr` (#35 for CLI exposure) | existing core/API plus reviewed CLI and Bucheon evidence | unchanged green HEAD, required review, protected-main merge |
| Schema-validated report generation | `implemented_on_protected_main` | structural client port, bounded retry/repair, quality gate | selected backend failure remains visible; no silent backend switch |
| Contextual Orchestrator adapter | `implemented_on_protected_main` | explicit adapter/token/routing contract tests | Four Pillars treats it as one external gateway |
| Durable async jobs and stable history | `implemented_on_protected_main` | SQLite WAL repository, atomic claim/idempotency, cursor tests | single-node guarantees only |
| Searchable HTML/PDF/JSON artifacts | `implemented_on_protected_main` | renderer and manifest-integrity tests | visual changes require browser/visual review |
| Canonical acquisition-grade documentation | `active_pr` (#31) | architecture graph, ADR index, ERD, threat/test/operations contracts | unchanged green HEAD and protected-main merge |

## Prioritized gap register

| ID | Buyer-visible or operational gap | Status | Next bounded action | Acceptance evidence |
|---|---|---|---|---|
| GAP-01 | Canonical architecture evidence is not yet on protected `main`. | `active_pr` (#31) | Resolve exact-head review and Checks, then merge without changing the green head. | required Checks successful, unresolved actionable threads zero, qualifying review, protected-main commit |
| GAP-02 | CLI users cannot rely on protected-main longitude/time-basis exposure yet. | `active_pr` (#35) | Complete review/Checks and merge the unchanged green head. | CLI edge tests including non-finite longitude, docs, exact-head gates, protected-main commit |
| GAP-03 | The standalone SQLite/filesystem queue is not a supported horizontal multi-node deployment. | `planned` | Add a separately reviewed remote repository/queue and object-store adapter only when a deployment needs horizontal workers. | atomic distributed claim/idempotency tests, 3NF schema/migration, backup/restore, RPO/RTO, load evidence |
| GAP-04 | SLOs are defined but no repository evidence proves a deployed environment meets them. | `planned`, deployment-owned | Add reproducible reference-environment measurement and k6/browser load evidence before making performance claims. | environment manifest, raw results, p95 values, bottleneck analysis, repeatable command |
| GAP-05 | Backup/restore requirements exist without a current automated deployment drill artifact. | `planned`, deployment-owned | Implement a safe sampled restore drill for the selected database/artifact adapters. | timestamped restore result, manifest checks, queue-state handling, owner and follow-up |
| GAP-06 | Hosted interpretation quality targets are contracts, not current cross-provider production evidence. | `planned`, deployment-owned | Run maintained, consented evaluation sets through the selected backend without publishing sensitive prompts/reports. | model/backend/version, denominators, schema-first-pass and rubric distributions, failure classes |
| GAP-07 | Consultant editing/collaboration, tenancy, payments, and billing are excluded rather than silently half-built. | `planned` only after buyer validation | Validate a concrete buyer workflow before adding persistence/UI or payment dependencies. | approved user story, privacy/threat update, interaction design, E2E and accessibility acceptance |
| GAP-08 | No active automated PR steward exists after PR #29 closed unmerged. | `superseded`; no current product gap by itself | Keep manual/external exact-head governance unless throughput evidence justifies a new isolated steward. | measured queue cost, new authority ADR, credential separation, independent review and operational proof |
| GAP-09 | Traditional interpretation has cultural/source traceability but not scientific-prediction validity. | accepted claim limit | Preserve conditional language and deterministic provenance; do not market prediction validity. | report-quality regressions, source traceability, explicit disclaimer, no fabricated validation claim |
| GAP-10 | CSAP/SOC 2 readiness controls are designs, not certification. | `planned`, organization-owned | Collect deployed control evidence only if procurement requires it. | assessed scope, control owner, operating evidence, independent attestation where applicable |

## Sequencing

1. Merge GAP-01 and GAP-02 only from unchanged, exact green heads.
2. Rebase this baseline onto protected `main`, replace `active_pr` labels with
   protected-main evidence only after the merges are confirmed, and merge it.
3. Select the next implementation gap from measured buyer or operator evidence.
   GAP-03 through GAP-07 are not permission to build speculative infrastructure.
4. Re-run the gap audit after every material API, persistence, trust-boundary,
   calculation-policy, UI, or release change.

## Update contract

Each update must record the authoritative commit/PR, maturity, gap owner or
deployment boundary, next bounded action, and acceptance evidence. Remove a gap
only after its acceptance evidence exists; otherwise change its status or claim
limit. `scripts/product_gap_audit.py` remains a static contract audit and does
not by itself prove that this register is empty or that a commercial deployment
is operationally ready.

## References

The applicable APA 7 bibliography is maintained in
`docs/standards/REFERENCES.md`. This baseline applies ISO/IEC/IEEE 42010:2022
architecture-description concerns, ISO/IEC 25010:2023 product-quality concerns,
ISO/IEC 23894:2023 AI risk guidance, and NIST SP 800-218 SSDF practices through
the repository's existing doctoring and traceability; it does not restate or
upgrade those sources into certification claims.
