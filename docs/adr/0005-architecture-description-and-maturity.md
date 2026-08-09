# ADR 0005: Canonical architecture description and maturity labels

- **Status:** Accepted
- **Date:** 2026-08-09

## Context

Four Pillars evolves through product code, architecture records, Figma designs, GitHub issues/PRs, generated Superpowers specs/plans, scheduled OpenCode development, automated review, and conversation history. Those sources do not have equal authority. A PR description can become stale when its head changes; a design may be approved but not implemented; an OpenCode proposal may exist only on a branch; and an old assistant summary may describe a capability that was later replaced.

Without an explicit authority and maturity model, a reviewer or acquirer must reconstruct reality from Git history and conversation context. That is incompatible with maintainable architecture description and acquisition diligence.

## Decision

Four Pillars SHALL maintain a canonical architecture-description graph aligned with the concerns/viewpoint approach of ISO/IEC/IEEE 42010:2022.

### Authority order

When sources conflict, use this order unless a higher-order repository policy explicitly says otherwise:

1. protected-main source, migrations/schema, and executable tests;
2. Accepted ADRs and externally observable API/schema/release contracts that agree with protected main;
3. code-current PRD/TRD/architecture/UML/data/threat/test/operability/traceability documents;
4. released artifacts and provenance bound to an exact protected-main commit;
5. open-PR source and exact-head evidence;
6. Figma designs and accepted specs for user-facing behavior;
7. issues, PR bodies/comments, generated plans, and conversation history.

Lower-ranked material may discover a defect or future requirement but cannot by itself prove shipped behavior.

### Maturity labels

Architecture descriptions SHALL use these labels where lifecycle ambiguity matters:

- `implemented_on_protected_main`
- `accepted_architecture`
- `active_pr`
- `planned`
- `deprecated`
- `superseded`

An `active_pr` capability may not be presented as `implemented_on_protected_main` until the implementation reaches protected main and any required operational acceptance succeeds.

### Canonical documentation graph

The minimum current graph is:

- `docs/product/PRD.md`
- `docs/technical/TRD.md`
- root `ARCHITECTURE.md`
- `docs/architecture/SYSTEM_ARCHITECTURE.md`
- `docs/uml/architecture.md`
- `docs/architecture/DATA_MODEL.md`
- `docs/adr/README.md` and Accepted ADRs
- `docs/security/THREAT_MODEL.md` and root `SECURITY.md`
- `docs/technical/TEST_STRATEGY.md`
- `docs/operations/OPERABILITY.md` and runbooks
- `docs/standards/REFERENCES.md`
- `docs/standards/TRACEABILITY.md`
- `docs/standards/DOCUMENTATION_AUDIT.md`
- user-facing Figma references when implementation has a visual contract
- `CHANGELOG.md`, AGENTS/CLAUDE instructions, and release/provenance evidence.

### Change-impact rule

Every material change to a public API, deterministic calculation policy, prompt/interpretation schema, durable data model, lifecycle state, trust boundary, provider/secret, MSA port, user workflow, autonomous-development authority, recovery behavior, or release contract must either update the affected canonical documents in the same/prerequisite PR or explicitly state and verify why no documentation impact exists.

## Current active-PR example

PR #29 proposes a minute-07 exact-head PR steward. Until that PR reaches protected main, the steward is `active_pr`. The existing minute-17 deterministic sentinel and minute-47 NVIDIA/OpenCode product-development workflow are `implemented_on_protected_main`. Documentation must preserve this distinction even if PR #29's description says its implementation is complete.

## Machine-checkable fitness

Repository tests should verify existence and high-value cross-links for the canonical document families. The test should not attempt to prove architecture quality by word count alone; it should check stable invariants such as real database object names, explicit maturity labels, security credentials, independent calculation fixtures, purpose-bound privacy, recovery requirements, and links from PRD/TRD into the architecture graph.

## Consequences

The repository gains one discoverable source of architecture truth and avoids presenting generated plans as shipped features. Documentation changes become part of engineering quality rather than a later editorial cleanup. The cost is a larger documentation set and explicit synchronization work when contracts change.

## Rejected alternatives

- **Treat README/root architecture as sufficient:** rejected because no single viewpoint captures product, data, threat, test, operations, and decision history.
- **Treat PR bodies as the architecture log:** rejected because bodies are mutable and routinely stale relative to head/base.
- **Generate documentation only at release time:** rejected because design/implementation divergence would survive too long.
- **Copy every chat decision verbatim:** rejected because conversation is useful evidence but not normalized, versioned architecture.

## Reversal conditions

Supersede this ADR only if Four Pillars adopts another explicit architecture-description framework that preserves equivalent stakeholder concerns, authority ordering, maturity semantics, decision history, and machine-checkable consistency.

## References — APA 7th

International Organization for Standardization. (2022). *ISO/IEC/IEEE 42010:2022 Software, systems and enterprise—Architecture description* (2nd ed.). ISO.

International Organization for Standardization. (2023). *ISO/IEC 25010:2023 Systems and software engineering—Systems and software Quality Requirements and Evaluation (SQuaRE)—Product quality model* (2nd ed.). ISO.

Scarfone, K., Souppaya, M., & Dodson, D. (2022). *Secure Software Development Framework (SSDF) Version 1.1: Recommendations for mitigating the risk of software vulnerabilities* (NIST SP 800-218). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-218
