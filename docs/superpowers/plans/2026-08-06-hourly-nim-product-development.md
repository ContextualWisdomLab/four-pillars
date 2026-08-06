# Hourly NVIDIA NIM Product Development Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:test-driven-development`, `superpowers:systematic-debugging`, and `superpowers:verification-before-completion` task by task.

**Goal:** Add a secure minute-47 OpenCode loop that turns an empty PR queue into at most one bounded, fully verified Four Pillars pull request using only `NVIDIA_NIM_API_KEY`.

**Architecture:** Keep the existing deterministic minute-17 quality sentinel. Add separate proposal, verification, and publication runners connected by an exact immutable patch artifact. Model code runs only on the read-only proposal runner; tests run on a second uncredentialed runner; a third non-executing publisher mints a repository-scoped App token only after revalidation.

**Tech Stack:** GitHub Actions, Bash, Python 3.11/3.12, OpenCode 1.17.13, NVIDIA NIM, GitHub CLI, Pydantic/FastAPI project tooling, pytest, Ruff, Hatchling, GitHub Actions artifacts, and a repository-scoped Maintainer GitHub App.

## Global Constraints

- Preserve deterministic Four Pillars calculations as immutable evidence.
- Keep `NVIDIA_NIM_API_KEY` exclusive to model proposal execution.
- Never use `COPILOT_GITHUB_TOKEN`.
- Do not alter existing reviewer App identities, credential names, or review semantics.
- Keep standalone operation and modular MSA compatibility with central `.github`, `naruon`, Contextual Orchestrator, and other services.
- Maintain exactly 100 percent production statement and branch coverage and complete public API docstrings.
- Require realistic tests, APA 7 doctoring, and two-word-or-longer `snake_case` database objects.
- Do not merge, approve, publish, release, deploy, or weaken repository protection from the scheduled development workflow.
- Do not bump package version for this workflow-only increment.
- Speed is not a priority; correctness, security, evidence, and buyer value are.

---

### Task 1: Lock the failing workflow and metadata contract

**Files:**
- Create: `tests/test_hourly_nim_product_development.py`
- Create: `docs/superpowers/specs/2026-08-06-hourly-nim-product-development-design.md`
- Create: `docs/superpowers/plans/2026-08-06-hourly-nim-product-development.md`

**Interfaces:**
- Consumes: existing repository paths and release commands.
- Produces: executable assertions for the future workflow, parser, operations docs, and root agent/architecture docs.

- [x] Write tests for minute-47 scheduling, manual dry run, NIM-only credentials, zero-open-PR gate, three-runner isolation, immutable artifact identity, restricted subprocess environment, complete release verification, research-grounded prompt, and no merge/release authority.
- [x] Write parser tests for Korean UTF-8 metadata, CRLF normalization, private output modes, invalid UTF-8, missing title/body, control and bidirectional characters, byte budgets, symlinks, and non-regular sources.
- [x] Write documentation contract tests for root `AGENTS.md`, `CLAUDE.md`, `ARCHITECTURE.md`, the operations runbook, and APA 7 doctoring.
- [ ] Push the contract-only commit and record the expected CI failure caused by missing implementation files.

### Task 2: Implement trusted PR metadata parsing

**Files:**
- Create: `scripts/prepare_agent_pr_message.py`
- Test: `tests/test_hourly_nim_product_development.py`

**Interfaces:**
- Consumes: `parse_pr_message(source_path, title_path, body_path, *, max_title_bytes, max_body_bytes)`.
- Produces: normalized title/body strings and owner-only UTF-8 output files.

- [ ] Open the source with `O_NOFOLLOW` where available and verify stable regular-file metadata.
- [ ] Decode strict UTF-8, normalize CRLF/CR, reject unsupported control and bidirectional characters, and require nonempty title/body.
- [ ] Enforce title/body byte budgets and atomically write mode-0600 outputs.
- [ ] Run focused parser tests and all Ruff/compile checks.

### Task 3: Implement the three-runner workflow

**Files:**
- Create: `.github/workflows/hourly-nim-product-development.yml`
- Test: `tests/test_hourly_nim_product_development.py`

**Interfaces:**
- Consumes: GitHub pull-request inventory, `NVIDIA_NIM_API_KEY`, repository-scoped Maintainer App configuration, repository release commands.
- Produces: zero or one ordinary pull request.

- [ ] Add minute-47 schedule, manual `dry_run`, repository-scoped non-cancelling concurrency, and read-only default permissions.
- [ ] Add a proposal runner that fails closed before model use unless PR inventory is readable and zero, credentials are configured, and exact `main` is checked out without persisted credentials.
- [ ] Install the immutable OpenCode 1.17.13 archive using SHA-256 `157afa289d1a8d9372de0ce19ac726119b937a1f6b201808d46f06e4e59bb348`.
- [ ] Configure only NVIDIA NIM and deny web/MCP/task/external-directory/interactive/remote-mutation capabilities.
- [ ] Run bounded candidate fallback with timeout, kill grace, clean reset, and bounded clean reinstall between candidates.
- [ ] Remove GitHub, OIDC, Actions runtime/cache, and runner command-file variables from untrusted execution.
- [ ] Run the full release gate before exporting a bounded binary/full-index patch.
- [ ] Bind artifact ID/digest, exact base, patch digest, changed-file count, byte count, and forbidden Git modes.
- [ ] Add a fresh uncredentialed verifier that independently validates the artifact, applies it, runs all release gates, and proves verification did not mutate it.
- [ ] Add a third fresh non-executing publisher that copies the trusted parser before patch application, independently revalidates the artifact, parses metadata, mints the App token late, rechecks queue/base, and creates exactly one PR.

### Task 4: Document operations, architecture, and agent authority

**Files:**
- Create: `docs/operations/HOURLY_NIM_PRODUCT_DEVELOPMENT.md`
- Create: `docs/doctoring/hourly-nim-product-development.md`
- Create: `ARCHITECTURE.md`
- Create: `CLAUDE.md`
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/standards/REFERENCES.md`
- Modify: `docs/standards/TRACEABILITY.md`

**Interfaces:**
- Consumes: implemented workflow/security contracts and primary sources.
- Produces: beginner-readable setup, architecture, standards, rollback, and residual-risk evidence.

- [ ] Explain schedule and queue behavior, required App/NIM configuration, three-runner trust boundary, failure/recovery, disablement/rollback, and residual risks.
- [ ] Record that OpenCode 1.18.13 was reviewed but the known-good 1.17.13 artifact remains pinned until its newer digest is independently verified.
- [ ] Record APA 7 references for Sakana Fugu, TRINITY, Conductor, NIST SP 800-218, GitHub Actions security guidance, and OpenCode.
- [ ] Distinguish source-supported facts, repository decisions, assumptions, and residual risks.
- [ ] Expand root agent and architecture guidance without re-enabling impossible code-owner gates.
- [ ] Add an Unreleased changelog entry without changing v0.7.0.

### Task 5: Make the product-gap audit enforce the new control

**Files:**
- Modify: `scripts/product_gap_audit.py`
- Modify: `tests/test_hourly_product_loop.py`
- Test: `tests/test_hourly_nim_product_development.py`

**Interfaces:**
- Consumes: workflow and documentation paths/tokens.
- Produces: deterministic gaps when the hourly NIM control or its doctoring disappears.

- [ ] Add workflow, operations, doctoring, root architecture, and agent-guidance contracts.
- [ ] Require NIM-only credential wording, no Copilot credential, three-runner names, minute-47 schedule, Fugu/Conductor/TRINITY traceability, and exact-head handoff.
- [ ] Exercise missing-file and missing-token cases through existing token-contract test helpers.
- [ ] Run the product-gap audit directly.

### Task 6: Verify, review, repair, and merge

**Files:** all files changed by Tasks 1–5.

- [ ] Run dependency integrity, product-gap audit, Ruff/docstrings, compileall, docs, prompts, all offline tests, package build, and pinned container build.
- [ ] Require 100 percent production statements and branches on Python 3.11 and 3.12.
- [ ] Require Security Scan and Semgrep on the exact head.
- [ ] Inspect CodeRabbit, OpenCode, human reviews, inline threads, issue comments, and all check runs.
- [ ] Fix each valid current-head finding and rerun every affected gate.
- [ ] Merge only the unchanged exact head with zero actionable threads and successful required Checks.
- [ ] Verify open PRs return to zero, then continue with the next buyer-visible product gap.
