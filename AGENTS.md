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
  acquisition, or scientific-prediction evidence.

## Pull-request governance

For every open pull request: inspect review submissions and inline threads,
repair actionable findings, rerun exact-head Checks, and merge only the unchanged
green head. Waiting for a review or Check is not permission to weaken the gate;
continue other bounded investigation instead.

The hourly NVIDIA NIM OpenCode workflow is proposal-only. Its model runner has
no GitHub write authority. Its publisher may open one pull request after fresh
verification, but it has **no merge**, approval, release, deployment, or reviewer
authority. Existing exact-head review remains mandatory.

## Code-owner review gates — disabled (on hold)

As of 2026-08-04, code-owner review requirements are disabled across the
ContextualWisdomLab organization because there is one maintainer. Do not
re-enable CODEOWNERS-based merge gates until multiple maintainers can satisfy
them. This exception does not waive automated review, exact-head Checks, security
scanning, or unresolved-thread requirements.
