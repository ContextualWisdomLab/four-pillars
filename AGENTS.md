# AGENTS.md

## Repository mission

Four Pillars provides deterministic Korean Four Pillars calculation and schema-validated report generation as both an independently deployable product and a modular MSA component.

## Required agent behavior

- Read `CLAUDE.md`, `ARCHITECTURE.md`, `README.md`, `CHANGELOG.md`, the PRD, TRD, calculation policy, modularity contract, security policy, operations guides, ADRs, and doctoring before changing behavior.
- Work test-first and preserve explicit RED-to-GREEN evidence.
- Keep deterministic calculations independent from hosted model code.
- Treat Model Orchestration as an external bounded context. Product-owned LLM work must use the Contextual Orchestrator ACL and `orchestrator/free` unless a higher-level repository contract explicitly requires another virtual route.
- Do not add provider-native credentials, direct provider SDK calls, or silent fallback to Four Pillars product composition.
- Preserve `ReportInterpreter` as the application port; caller-owned MSA injection may replace that port without changing the repository-owned default.
- Maintain 100% production statement/branch coverage and complete public docstrings.
- Use APA 7 references for standards and research decisions.
- Never use `COPILOT_GITHUB_TOKEN` for model execution.
- Do not change existing review-agent credentials or identity.
- Use descriptive two-word-or-longer `snake_case` database object names.
- Audit DDD paths whenever responsibilities move. Move implementation, imports, tests, docs, UML, and architecture-fitness rules together; do not leave provider-specific names around a provider-neutral boundary without a tracked migration.
- Update `CHANGELOG.md` and affected architecture/operations/security documents.
- Do not fabricate customer, revenue, production, attestation, transfer, acquisition, or scientific-prediction evidence.

## Pull-request governance

For every open pull request: inspect review submissions and inline threads, repair actionable findings, rerun exact-head Checks, and merge only the unchanged green head. Waiting for a review or Check is not permission to weaken the gate; continue other bounded investigation instead.

Repository-local automation is a model-free quality sentinel. Model-backed autonomous development is owned by the shared ContextualWisdomLab hourly maintainer and must not be duplicated by a second repository-specific provider-credentialed writer. The shared writer may open bounded pull requests but has no authority to waive review, security, exact-head validation, or release policy.

## Code-owner review gates — disabled (on hold)

As of 2026-08-04, code-owner review requirements are disabled across the ContextualWisdomLab organization because there is one maintainer. Do not re-enable CODEOWNERS-based merge gates until multiple maintainers can satisfy them. This exception does not waive automated review, exact-head Checks, security scanning, or unresolved-thread requirements.
