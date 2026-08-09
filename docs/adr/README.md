# Four Pillars Architecture Decision Records

Architecture Decision Records (ADRs) capture durable decisions that materially constrain Four Pillars. A chat transcript, implementation plan, pull-request body, or code comment can provide evidence but does not replace an ADR when a decision changes product boundaries, public contracts, trust/authority, persistence, privacy, integration, calculation provenance, or release governance.

## Status vocabulary

- **Proposed** — under review or dependent on an unmerged/incomplete implementation.
- **Accepted** — governs protected-main implementation and has the required evidence described by the ADR.
- **Deprecated** — retained for history but should not guide new work.
- **Superseded by ADR NNNN** — replaced by a later accepted decision.
- **Rejected** — evaluated but not adopted.

An ADR becomes Accepted only when the represented behavior/governance contract is integrated into protected `main` or the decision is explicitly accepted as architecture before implementation and does not falsely describe unshipped behavior. Proposed work must never be described as shipped behavior.

## Required ADR structure

Every material ADR should state:

1. status and date;
2. context, drivers and assumptions;
3. decision and ownership boundaries;
4. alternatives considered and why they were rejected;
5. consequences and compatibility impact;
6. failure, degraded-mode and recovery behavior;
7. security, privacy and governance impact;
8. tests, operational acceptance and evidence required;
9. migration and rollback where applicable;
10. reversal/supersession conditions.

## Index

| ADR | Status | Decision |
|---|---|---|
| [0001](0001-deterministic-core-and-nim-boundary.md) | Accepted | Deterministic calculation owns factual chart/luck evidence; AI interpretation cannot rewrite it. |
| [0002](0002-nvidia-nim.md) | Accepted | Direct NVIDIA NIM is the standalone model boundary and uses `NVIDIA_NIM_API_KEY`. |
| [0003](0003-explicit-contextual-orchestrator-backend.md) | Accepted | Contextual Orchestrator is an explicit optional organization adapter with separate credentials and no silent fallback. |
| [0004](0004-purpose-bound-personal-data-controls.md) | Proposed | Preserve product-necessary PII through purpose-bound authorization and cryptographic/audit controls instead of blanket masking. |
| [0005](0005-documentation-as-code-authority.md) | Proposed | Maintain one code-current authoritative PRD/TRD/Architecture/ADR/UML/ERD/documentation graph. |
| [0006](0006-standalone-modular-msa-boundary.md) | Proposed | Standalone and organization deployments share stable ports; services do not reach into each other's application databases. |
| [0007](0007-autonomous-control-plane-authority.md) | Proposed | Separate deterministic quality, model-backed proposal, PR stewardship, independent review, merge and release authority. |
| [0008](0008-solar-term-evidence-and-calculation-versioning.md) | Accepted | Validate boundary-critical solar terms against independent KASI/NAOJ evidence and version calculation policy/fingerprints. |
| [0009](0009-release-provenance-and-operational-acceptance.md) | Proposed | Release only from integrated protected main with exact-source artifacts, checksums, acceptance evidence and future SBOM/provenance hardening. |

## Decision dependencies

```mermaid
flowchart LR
  A1[ADR 0001\nDeterministic evidence] --> A2[ADR 0002\nDirect NIM]
  A1 --> A3[ADR 0003\nContextual Orchestrator]
  A1 --> A6[ADR 0006\nStandalone / MSA]
  A1 --> A8[ADR 0008\nSolar evidence / versioning]
  A2 --> A3
  A4[ADR 0004\nPurpose-bound PII] --> A6
  A5[ADR 0005\nDocumentation authority] --> A1
  A5 --> A4
  A5 --> A6
  A5 --> A7[ADR 0007\nAutomation authority]
  A5 --> A8
  A7 --> A9[ADR 0009\nRelease provenance]
  A8 --> A9
```

## Review rule

A material change that contradicts an Accepted ADR must either preserve the accepted invariant or introduce a superseding ADR in the same/prerequisite PR. Editing an old Accepted ADR to erase the historical decision is prohibited except for spelling/link corrections that do not change meaning.

Proposed ADRs are explicit work items, not marketing claims. Their acceptance conditions must be checked against live protected-main code, exact-head test/review evidence, deployment/operational evidence where applicable, and current standards before status is changed.
