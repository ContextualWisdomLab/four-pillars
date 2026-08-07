# AGENTS.md

## Repository mission

Four Pillars provides deterministic Korean Four Pillars calculation and
schema-validated report generation as both a standalone product and a modular
MSA component.

## Required agent behavior

- Read `CLAUDE.md`, `ARCHITECTURE.md`, `README.md`, `CHANGELOG.md`, the PRD,
  TRD, calculation policy, modularity contract, security policy, operations
  guides, and doctoring before changing behavior.
- Work test-first and preserve explicit RED-to-GREEN evidence.
- Keep deterministic calculations independent from hosted model code.
- Maintain 100% production statement/branch coverage and complete public
  docstrings.
- Use APA 7 references for standards and research decisions.
- Use only `NVIDIA_NIM_API_KEY` for direct NVIDIA NIM.
- Never use `COPILOT_GITHUB_TOKEN` for model execution.
- Do not change existing review-agent credentials or identity.
- Use descriptive two-word-or-longer `snake_case` database object names.
- Update CHANGELOG.md and affected architecture/operations/security documents.
- Do not fabricate customer, revenue, production, attestation, transfer,
  acquisition, certification, or scientific-prediction evidence.
- Preserve useful review and Check diagnostics; do not apply blanket PII masking.
  Instead exclude customer birth data, generated reports, credentials, emails,
  and unrelated records, then enforce purpose limitation, least privilege,
  byte bounds, one-day retention, and exact artifact identity.

## Pull-request governance

For every open pull request: inspect review submissions and inline threads,
repair actionable findings, rerun exact-head Checks, and merge only the unchanged
green head. Waiting for a review or Check is not permission to weaken the gate;
continue other bounded investigation instead.

The minute-47 NVIDIA NIM OpenCode workflow is proposal-only. Its model runner has
no GitHub write authority. Its publisher may open one pull request after fresh
verification, but it has **no merge**, approval, release, deployment, or reviewer
authority. Existing exact-head review remains mandatory.

The minute-07 hourly exact-head PR steward may inspect only the oldest open
non-draft pull request. It may either wait, propose a same-repository repair, or
queue ordinary squash auto-merge. Inspection, OpenCode repair, fresh verification,
non-executing publication, and merge are separate trust zones. The model receives
only `NVIDIA_NIM_API_KEY` and untrusted bounded review/Check evidence; it never
receives a GitHub, OIDC, Actions runtime/cache, reviewer, publication, or merge
credential. Repair publication is a normal fast-forward commit, never a force
push. Merge remains subject to current reviews, unresolved-thread policy,
branch protection, and exact-head Checks; no steward job may approve, dismiss a
review, use `--admin`, tag, release, or deploy.

The steward workflow is repository-local and independently operable. Central
`.github`, `naruon`, contextual-orchestrator, and other MSA consumers may reuse
its workflow-call and deterministic evidence contracts without importing Four
Pillars application state or changing local governance.

## Code-owner review gates — disabled (on hold)

As of 2026-08-04, code-owner review requirements are disabled across the
ContextualWisdomLab organization because there is one maintainer. Do not
re-enable CODEOWNERS-based merge gates until multiple maintainers can satisfy
them. This exception does not waive automated review, exact-head Checks, security
scanning, or unresolved-thread requirements.
