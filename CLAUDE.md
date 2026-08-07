# CLAUDE.md

## Mission

Develop Four Pillars as a commercial-quality deterministic calculation and
schema-validated report product. Preserve standalone operation and modular MSA
integration with ContextualWisdomLab/.github, naruon, Contextual Orchestrator,
and other CWL services.

## Non-negotiable boundaries

- Deterministic calculation evidence is authoritative and must never be replaced
  by model output.
- Direct hosted model work uses `NVIDIA_NIM_API_KEY`.
- Do not introduce or use `COPILOT_GITHUB_TOKEN` for model execution.
- Do not change existing reviewer-agent identities, secret names, or provider
  routing as part of product development.
- A selected interpretation backend never silently falls back to another
  provider.
- New database objects use descriptive two-word-or-longer `snake_case` names.
- Every public production API has a beginner-readable docstring.
- Production statement and branch coverage remain exactly 100%.
- Standards and research decisions are recorded with APA 7 references and clear
  claim limits.
- Traditional interpretation is symbolic content, not scientific prediction.

## Development sequence

1. Inspect open pull requests, review submissions, inline threads, and all
   exact-head Checks.
2. Fix actionable findings and reproduce failed Checks before changing code.
3. Write a realistic failing test or contract and observe the RED result.
4. Implement the smallest coherent change.
5. Run dependency integrity, product-gap audit, Ruff/docstrings, compileall,
   document and prompt checks, all non-hosted tests with 100% coverage, package
   build, container, Security Scan, and Semgrep.
6. Update CHANGELOG.md, architecture, operations, security, API, and doctoring.
7. Merge only the unchanged exact head whose required Checks pass and whose
   actionable review threads are zero.
8. Release only when package, runtime, API, changelog, artifacts, and version
   evidence are aligned.

## Hourly autonomous development

The minute-17 workflow is a read-only quality sentinel. The minute-47 OpenCode
workflow may propose one bounded pull request only when open PR inventory is
readable and empty. OpenCode receives NVIDIA NIM access but no repository-write,
OIDC, Actions runtime/cache, command-file, or reviewer credential.

The fresh verifier executes the exact immutable patch with no model or
publication credential. The fresh publisher executes no proposed code, validates
bounded PR metadata, mints a repository-scoped Maintainer App token late, and
opens one PR. It performs no approval, merge, tag, release, or deployment.

## LLM and orchestration work

For new runtime LLM behavior, use or improve Contextual Orchestrator. Ground
test-time compute in Fugu, Conductor, TRINITY, and related primary research:
choose between single-model routing and deep multi-agent conduct, use explicit
workflow stages and access lists, bound recursive depth, assign role-specific
reasoning effort, and provide ablation evidence. Speed is not the primary
optimization target.

## Visual work

Use Figma only when a buyer- or user-facing visual flow materially changes.
Keep implementation synchronized with the approved editable design and include
responsive, accessibility, keyboard, loading, error, empty, and recovery states.
