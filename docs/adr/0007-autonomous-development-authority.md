# ADR 0007: Separate autonomous development, verification, review, and merge authority

- **Status:** Accepted
- **Architecture maturity:** minute-17/minute-47 controls are `implemented_on_protected_main`; the PR-steward extension remains `active_pr` (#29)
- **Date:** 2026-08-09

## Context

Four Pillars uses scheduled automation to keep product quality and development moving. A model-backed development agent is useful only if it cannot convert its own proposal into trusted verification, approval, merge, release, or deployment evidence. GitHub review/check latency must not freeze product development, but “automation keeps working” must not mean “one credential can write and approve everything.”

The repository currently has a deterministic minute-17 quality sentinel and a minute-47 NVIDIA NIM/OpenCode product-development proposal workflow. PR #29 proposes a separate minute-07 exact-head PR steward.

## Decision

1. **Distinct roles:** deterministic sentinel, model-backed product proposal, verification, independent review, merge/release governance, and deployment are separate authorities.
2. **Model credential:** model-backed autonomous development uses `NVIDIA_NIM_API_KEY`; `COPILOT_GITHUB_TOKEN` is prohibited for this purpose.
3. **Reviewer independence:** existing reviewer-agent identities, secret names, provider routing, and key chains are not repurposed as development-writer authority.
4. **Proposal isolation:** model execution does not receive repository merge/release/reviewer credentials. It produces a bounded candidate patch or working-tree increment only.
5. **Verification isolation:** candidate code MUST be verified on an exact immutable base/head without the model credential and without the publication credential before it can cross into a publishable change. If a workflow cannot enforce that credential-free verification boundary, publication is prohibited and the run fails closed. A compensating control is acceptable only after a separate reviewed ADR proves equivalent separation, bounded scope, exact artifact/head identity, no model access to the publication credential, and an executable regression test; absence of such an ADR is not permission to publish.
6. **Publication isolation:** publication authority is late-bound, scoped, revalidates exact base/head/queue state, and does not execute model-proposed code merely to create a PR.
7. **Exact-head governance:** reviews and Checks belong to one exact head. Stale/predecessor/synthetic-only/pending/skipped-required/cancelled/failed evidence does not become passing evidence.
8. **Work-conserving execution:** review/Check/provider waiting blocks only the affected action. Autonomous development follows `docs/operations/AUTONOMOUS_DEVELOPMENT.md` and performs a mandatory final sweep before ending a practical run.
9. **One PR is a safety bound:** minute-47 development may create at most one coherent PR per run; this does not permit stopping after one inventory, RCA, documentation edit, or test result while the same bounded increment still has safe executable work.
10. **PR steward:** PR #29 is `active_pr`. If merged, the steward may triage/repair/queue governed merge only within the authority proven by its exact protected-main implementation. This ADR does not pre-authorize unmerged PR behavior.
11. **Release authority:** autonomous development/review automation does not independently mint a release unless a separately reviewed release workflow, exact protected-main gates, provenance, and repository governance permit it.

## Security invariants

- no source writer races the same branch;
- no model self-approval;
- no model-created status string substitutes for a required Check/review;
- no silent widening of GitHub App/token permissions;
- no model access to unrelated OIDC/Actions runtime/command-file secrets;
- no candidate publication without a credential-free verification zone or a separately accepted equivalent-separation ADR;
- patch/artifact identity is cryptographically/boundedly checked across trust zones;
- symlink/gitlink/path or unbounded-output mechanisms cannot smuggle an uncontrolled proposal into the publisher;
- branch/head/base is refreshed immediately before a write/merge decision.

## Consequences

The control plane is slower than a single all-powerful bot, but evidence is attributable and failures cannot silently bypass governance. Long-running review systems can take hours without blocking unrelated safe work. The repository may have multiple schedulers only when they have distinct roles and writer boundaries; redundant writers should be consolidated or removed.

## Rejected alternatives

- **One bot token for code, review, merge, and release:** rejected for separation-of-duties and compromise blast radius.
- **Let the model credential remain available during verification because publication uses another token:** rejected because dependency/test commands are still an execution boundary capable of exfiltrating the model secret.
- **Use GitHub Copilot/`COPILOT_GITHUB_TOKEN` for scheduled development:** rejected by repository-owner credential policy and because the dedicated OpenCode/NIM path is the development authority.
- **Poll a pending review until the run ends:** rejected because waiting is local and wastes the development window.
- **Treat automated COMMENTED/model verdicts as independent approval:** rejected because review evidence and merge authority are distinct.

## Mapping

- `.github/workflows/hourly-product-loop.yml` — deterministic sentinel.
- `.github/workflows/hourly-nim-product-development.yml` — model-backed proposal/credential-free verification/publication separation.
- `docs/operations/AUTONOMOUS_DEVELOPMENT.md` — work-conserving execution contract.
- `docs/doctoring/hourly-nim-opencode-development.md` — original control-plane research/standards evidence.
- PR #29 — `active_pr` PR-steward extension; must be reclassified only after protected-main integration.
- `docs/security/THREAT_MODEL.md` — autonomous-development credential/supply-chain threats.

## Reversal conditions

Supersede this ADR if the repository moves to another autonomous-development architecture or if organization-wide governance provides a stronger centrally enforced separation model. The successor must preserve exact-head evidence, credential-free or equivalently isolated verification, non-self-approval, least privilege, and explicit credential/authority boundaries.

## References — APA 7th

Scarfone, K., Souppaya, M., & Dodson, D. (2022). *Secure Software Development Framework (SSDF) Version 1.1: Recommendations for mitigating the risk of software vulnerabilities* (NIST SP 800-218). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-218

International Organization for Standardization. (2023). *ISO/IEC 42001:2023 Information technology—Artificial intelligence—Management system*. ISO.
