# ADR 0007: Separate autonomous development, review, merge, and release authority

- Status: Proposed
- Date: 2026-08-09

## Context and drivers

Four Pillars uses repository automation for deterministic quality checks and product development. Model-backed automation is useful for discovering and proposing bounded buyer-visible improvements, but giving the same model path source-write, review, merge, release, and secret authority would create a confused-deputy and supply-chain risk. Review/CI can also take significantly longer than one scheduler invocation, so the control plane must remain work-conserving without treating waiting as permission to bypass gates.

Protected main currently contains a deterministic minute-17 quality sentinel and a minute-47 NVIDIA/OpenCode product-development proposal workflow. A minute-07 exact-head PR steward is under review and therefore remains Proposed until merged.

## Decision

### Authority zones

1. **Deterministic quality sentinel — Implemented.** The minute-17 workflow verifies repository quality/contracts without model credentials and may synchronize regression evidence according to its documented permissions. It is not a product-development model path.
2. **NVIDIA/OpenCode product developer — Implemented.** The minute-47 workflow uses only `NVIDIA_NIM_API_KEY` for model execution, selects at most one bounded product increment when the PR queue is empty, and separates proposal, verification, and PR publication across fresh runners. It does not approve, merge, release, deploy, or act as a reviewer.
3. **Exact-head PR steward — Proposed.** The minute-07 workflow may inspect the oldest eligible PR, classify current exact-head/base/review/check evidence, repair a same-repository head only through an isolated model path where needed, reverify, and queue governed expected-head merge only when all repository-policy gates are satisfied. Its implementation is not Current until its PR merges.
4. **Independent reviewers — Separate authority.** Human and existing automated review agents retain their current identities and credential contracts. Model-development credentials are never repurposed as reviewer identity.
5. **Merge authority — Governed, exact-head bound.** A merge requires the unchanged exact head, current live base semantics where required, all applicable checks/security gates, zero valid unresolved findings, and qualifying independent approval where repository policy requires it. Queued/stale/predecessor/synthetic evidence is not promoted to passing.
6. **Release authority — Protected-main only.** Release automation operates only from an integrated protected-main state and verifies release/version/artifact/provenance contracts separately from feature-PR checks.

### Credential separation

- Model-backed development uses `NVIDIA_NIM_API_KEY`; `COPILOT_GITHUB_TOKEN` is prohibited.
- Model execution receives no publication/merge/release/reviewer credential.
- Publication authority is late-bound after immutable artifact/evidence validation.
- Existing review-agent keys, names, Apps and scopes are not renamed or reused by development automation.
- Organization Contextual Orchestrator credentials remain separate from direct NIM development credentials.

### Evidence binding

Every write or governed merge decision revalidates exact target head/base/ref/blob as appropriate. Proposed patches cross trust zones as immutable/bounded artifacts with verified identity/digest, file count/size and prohibited Git modes. Publication does not execute model-authored code.

### Work-conserving waiting

A pending review, long-running OpenCode review, queued Check, rate limit or provider wait blocks only the action that requires it. Autonomous work may continue on non-conflicting repository work under the active writer lease. Automation must never manufacture approval or weaken a gate to avoid waiting.

## Alternatives considered

### Give one autonomous agent repository-admin authority

Rejected because compromise or prompt injection would collapse proposal, verification, review, merge and release separation.

### Let model automation merge its own green PRs

Rejected because passing tests do not establish independent review, current-base safety, semantic correctness, or release readiness.

### Use one hourly workflow for quality, product development, PR repair and releases

Rejected because it creates overlapping authority, larger secret exposure, difficult incident isolation and ambiguous ownership. Distinct roles may be consolidated only if the same separation is preserved explicitly.

## Consequences

- Automation can be slower to integrate because independent checks/reviews remain real gates.
- Long reviewer latency is handled by queue rotation rather than policy bypass.
- Multiple workflows require explicit non-overlap and documentation to prevent duplicate writers.
- Incident analysis can attribute failures to proposal, verification, publication, review, merge, or release boundaries.

## Failure and recovery

If a model/provider path fails, no merge/release authority is granted and the affected proposal/repair fails visibly. If evidence changes between inspection and mutation, the write/merge is abandoned and state is refetched. If a publisher branch exists but PR creation fails, cleanup is bounded and must not delete unrelated refs. If a reviewer is unavailable, the PR remains unmerged and other safe work continues.

## Security and governance impact

This decision limits blast radius through least privilege, fresh runners, immutable artifact binding, late credential materialization, and separation of duties. It is aligned with secure-development and supply-chain principles but does not claim CSAP, SOC 2 or ISO certification.

## Acceptance evidence

Before this ADR becomes Accepted:

- the minute-07 steward implementation reaches protected main or the ADR is revised to exclude it;
- workflow tests prove no `COPILOT_GITHUB_TOKEN` model path and preserve `NVIDIA_NIM_API_KEY` naming;
- tests prove model execution cannot use merge/release/reviewer credentials;
- exact-head/base/artifact/ref validation fails closed on stale/malformed evidence;
- branch/security/review gates remain mandatory and expected-head merge refuses head movement;
- control-plane UML and runbooks describe all implemented zones and label Proposed zones explicitly;
- protected-main operational runs prove the implemented scheduler paths, not merely source-level tests.

## Migration and rollback

Each automation workflow is independently removable/disableable. Rollback must preserve deterministic CI and normal human-reviewed PR/release operation. Disabling a model-backed workflow must never remove the ability to calculate, test, review, merge manually under policy, or operate the Four Pillars service.

## Supersession conditions

Supersede this ADR if repository governance adopts another automation architecture that demonstrably preserves equivalent or stronger model/write/review/merge/release separation, exact-state binding and least privilege.
