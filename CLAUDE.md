# CLAUDE.md

## Mission

Develop Four Pillars as a commercial-quality deterministic calculation and schema-validated report product. Preserve independent application deployment and modular MSA integration with ContextualWisdomLab/.github, naruon, Contextual Orchestrator, and other CWL services.

## Non-negotiable boundaries

- Deterministic calculation evidence is authoritative and must never be replaced by model output.
- Product-owned LLM work crosses the Contextual Orchestrator anti-corruption layer and uses `orchestrator/free` as the repository runtime route.
- Provider discovery, provider credentials, free-pool eligibility, and provider fallback belong to Contextual Orchestrator, not Four Pillars.
- Do not introduce provider-native runtime credentials, direct provider selection, or silent gateway bypass.
- Do not introduce or use `COPILOT_GITHUB_TOKEN` for model execution.
- Do not change existing reviewer-agent identities or review policy as part of product development.
- A failed or empty `orchestrator/free` route fails visibly rather than escalating to a paid or direct provider route.
- New database objects use descriptive two-word-or-longer `snake_case` names.
- Every public production API has a beginner-readable docstring.
- Production statement and branch coverage remain exactly 100%.
- Standards and research decisions are recorded with APA 7 references and clear claim limits.
- Traditional interpretation is symbolic content, not scientific prediction.
- DDD path changes move code, imports, tests, docs, UML, and architecture-fitness contracts together.

## Development sequence

1. Inspect open pull requests, review submissions, inline threads, and all exact-head Checks.
2. Fix actionable findings and reproduce failed Checks before changing code.
3. Write a realistic failing test or contract and observe the RED result.
4. Implement the smallest coherent change.
5. Run dependency integrity, product-gap audit, Ruff/docstrings, compileall, document and prompt checks, all non-hosted tests with 100% coverage, package build, container, Security Scan, and Semgrep.
6. Update `CHANGELOG.md`, architecture, operations, security, API, ADRs, UML, and doctoring.
7. Merge only the unchanged exact head whose required Checks pass and whose actionable review threads are zero.
8. Release only when package, runtime, API, changelog, artifacts, and version evidence are aligned.

## Hourly autonomous development

The minute-17 repository workflow is a model-free quality sentinel. Model-backed source development is not duplicated inside this repository. The shared ContextualWisdomLab hourly maintainer owns organization-wide repository selection, direct-LLM-bypass discovery, DDD audits, bounded changes, review/check sequencing, and product-gap development.

When that shared maintainer needs an LLM, it uses Contextual Orchestrator and tests `orchestrator/free`. It does not receive authority to waive independent review, exact-head Checks, security scans, release policy, or unresolved-thread gates.

## LLM and orchestration work

For runtime LLM behavior, use or improve Contextual Orchestrator rather than adding a provider-native path. Ground test-time compute in Fugu, Conductor, TRINITY, and related primary research: choose between single-model routing and deep multi-agent conduct, use explicit workflow stages and access lists, bound recursive depth, assign role-specific reasoning effort, and provide ablation evidence. Speed is not the primary optimization target.

Four Pillars tests must prove that the product request remains on `orchestrator/free`, provider passthrough fields are absent where they bypass routing/conduct, malformed output fails closed, and direct-provider configuration cannot re-enter the composition root.

## Visual work

Use Figma only when a buyer- or user-facing visual flow materially changes. Keep implementation synchronized with the approved editable design and include responsive, accessibility, keyboard, loading, error, empty, and recovery states.
