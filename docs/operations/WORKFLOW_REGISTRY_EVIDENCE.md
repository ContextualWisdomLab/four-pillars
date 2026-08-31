# GitHub Actions Registry Evidence — 2026-08-31

## Scope and provenance

- Repository: `ContextualWisdomLab/four-pillars`
- Protected-main SHA: `cd4f4e6361238a1db43c28540640a407c7bf7c6e`
- Remediation observation: `2026-08-31T10:25:03Z`
- Configuration recheck: `2026-08-31T11:18:45Z`
- Organization-scope recheck: `2026-08-31T11:44:55Z`
- Owner incident: [#33](https://github.com/ContextualWisdomLab/four-pillars/issues/33)
- Contemporaneous operator receipt: [issue comment 5477004993](https://github.com/ContextualWisdomLab/four-pillars/issues/33#issuecomment-5477004993)

The owner loop paginated the Actions workflow registry, resolved protected main
to the SHA above, and queried every targeted repository path at that exact ref.
Each target below was `active` immediately before mutation and returned HTTP 404
for its exact protected-main contents lookup. Each was then disabled through the
GitHub Actions workflow lifecycle API and re-fetched as `disabled_manually`.

## Disabled orphan identities

| Workflow ID | Registry path | Before | After |
|---:|---|---|---|
| 329062785 | `.github/workflows/app-finalize-v0.8.0.yml` | `active` | `disabled_manually` |
| 329045940 | `.github/workflows/complete-v0.8.0.yml` | `active` | `disabled_manually` |
| 329043383 | `.github/workflows/finalize-v0.8.0-on-push.yml` | `active` | `disabled_manually` |
| 326292475 | `.github/workflows/one-shot-calendar-repair.yml` | `active` | `disabled_manually` |
| 326264306 | `.github/workflows/one-shot-commercial-hardening-v2.yml` | `active` | `disabled_manually` |
| 326259221 | `.github/workflows/one-shot-commercial-hardening.yml` | `active` | `disabled_manually` |
| 326265735 | `.github/workflows/one-shot-final-hardening-gate.yml` | `active` | `disabled_manually` |
| 326244681 | `.github/workflows/one-shot-fix-contract.yml` | `active` | `disabled_manually` |
| 326239799 | `.github/workflows/one-shot-format-verify.yml` | `active` | `disabled_manually` |
| 326261167 | `.github/workflows/one-shot-hardening-review-merge.yml` | `active` | `disabled_manually` |
| 326335763 | `.github/workflows/one-shot-httpx2-lock.yml` | `active` | `disabled_manually` |
| 326303725 | `.github/workflows/one-shot-lock-dependencies.yml` | `active` | `disabled_manually` |
| 326233853 | `.github/workflows/one-shot-normalize.yml` | `active` | `disabled_manually` |
| 326246667 | `.github/workflows/one-shot-review-and-merge.yml` | `active` | `disabled_manually` |
| 326234992 | `.github/workflows/one-shot-verify.yml` | `active` | `disabled_manually` |
| 329039882 | `.github/workflows/prepare-v0.8.0-on-push.yml` | `active` | `disabled_manually` |
| 329047656 | `.github/workflows/recover-v0.8.0-release.yml` | `active` | `disabled_manually` |
| 334956756 | `.github/workflows/repair-pr31-ci.yml` | `active` | `disabled_manually` |

## Preserved supported identities

The source-backed `ci.yml`, `hourly-nim-product-development.yml`,
`hourly-product-loop.yml`, `nim-eval.yml`, and `release.yml` identities remained
`active`. GitHub-owned dynamic CodeQL workflow IDs `343204628` and `326312916`
also remained `active`; they were not misclassified as missing repository files.

## Publication boundary observation

At the configuration recheck time, the repository Actions API returned zero
repository variables and zero repository secrets. Because Actions can inherit
organization configuration, the owner loop also paginated the organization
Actions variable and secret inventories. Neither inventory contained the exact
`FOUR_PILLARS_MAINTAINER_APP_CLIENT_ID` variable or
`FOUR_PILLARS_MAINTAINER_APP_PRIVATE_KEY` secret. The documented maintainer App
credentials were therefore absent from both applicable scopes. This is
presence-and-visibility-only evidence; no variable or secret value was requested
or exposed. Issue
[#34](https://github.com/ContextualWisdomLab/four-pillars/issues/34) remains the
owner record for provisioning or replacing that independent publication
boundary.

## Remaining acceptance boundary

This receipt proves the bounded Four Pillars remediation, not organization-wide
recurrence prevention. Central issue
[`ContextualWisdomLab/.github#945`](https://github.com/ContextualWisdomLab/.github/issues/945)
and AppGuardrail issue
[`ContextualWisdomLab/appguardrail#929`](https://github.com/ContextualWisdomLab/appguardrail/issues/929)
remain responsible for the paginated read-only detector and adversarial tests.
