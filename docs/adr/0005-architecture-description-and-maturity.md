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

### Canonical maturity labels

Architecture descriptions SHALL use exactly these labels where lifecycle ambiguity matters:

| Label | Meaning | May be presented as shipped? |
|---|---|---|
| `implemented_on_protected_main` | The exact current protected-main source/tests or protected release directly implement the claim; required operational proof is complete where the claim depends on runtime operation. | yes |
| `accepted_architecture` | An Accepted ADR/design invariant governs future/current implementation, but the label alone does not prove every described capability is shipped. | no, unless separately evidenced as implemented |
| `active_pr` | The capability/change exists only on one or more open PR heads and remains subject to review, Checks, base movement, and merge. | no |
| `planned` | Future work or an approved backlog/design direction with no protected-main implementation claim. | no |
| `deprecated` | A protected-main/released capability still exists for compatibility but new designs should not depend on it and an exit/supersession path is expected. | yes, but only as deprecated current behavior |
| `superseded` | A historical decision/plan/PR is no longer authoritative because a newer accepted/implemented source replaced it. | no |

These labels are mutually exclusive for one claim at one point in time. A capability can move from `planned` → `active_pr` → `implemented_on_protected_main`; an implementation may later become `deprecated` and eventually `superseded`. `accepted_architecture` describes governing design authority and must be paired with separate implementation evidence when a document needs to assert that the design is shipped.

An `active_pr` or `planned` capability may not also be labeled `implemented_on_protected_main`. PR #29 is now a `superseded` historical proposal because it closed without merge; [ADR 0007](0007-autonomous-development-authority.md) records the replacement authority in the existing protected-main minute-17/minute-47 controls and denies the closed steward any current authority. It is neither an active capability nor protected-main behavior.

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
- `docs/standards/ARCHITECTURE_TRACEABILITY.md`
- `docs/standards/DOCUMENTATION_AUDIT.md`
- user-facing Figma references when implementation has a visual contract
- `CHANGELOG.md`, AGENTS/CLAUDE instructions, and release/provenance evidence.

### Change-impact rule

Every material change to a public API, deterministic calculation policy, prompt/interpretation schema, durable data model, lifecycle state, trust boundary, provider/secret, MSA port, user workflow, autonomous-development authority, recovery behavior, or release contract must either update the affected canonical documents in the same/prerequisite PR or explicitly state and verify why no documentation impact exists.

## Superseded steward proposal example

PR #29 is `superseded` evidence: it proposed a minute-07 exact-head PR steward but closed without merge. [ADR 0007](0007-autonomous-development-authority.md) is the accepted replacement authority: the existing minute-17 deterministic sentinel and minute-47 NVIDIA/OpenCode product-development workflow remain `implemented_on_protected_main`, while no PR steward is authorized. Documentation must not promote the closed proposal to `active_pr` or shipped status unless a new independently reviewed implementation is opened or reaches protected main.

## Machine-checkable fitness

Repository tests should verify existence and high-value cross-links for the canonical document families. The tests must check maturity semantics rather than mere word presence: known `active_pr` and `planned` claims must not share a line/classification entry with `implemented_on_protected_main`, and a documented transition to shipped status must require protected-main/operational evidence.

The documentation test should not attempt to prove architecture quality by word count alone; it should check stable invariants such as real database object names, explicit maturity labels, security credentials, independent calculation fixtures, purpose-bound privacy, recovery requirements, and links from PRD/TRD into the architecture graph.

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
