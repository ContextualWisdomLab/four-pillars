# Canonical Architecture Documentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Four Pillars' architecture record acquisition-grade, machine-checkable, and unambiguous about protected-main reality versus active, planned, deprecated, or superseded work.

**Architecture:** Extend the existing PRD/TRD/UML/ADR/standards set with a canonical documentation graph rather than replacing it. Add a maturity model, logical ERD, public status schema, threat model, test strategy, operability contract, and autonomous-development control context on paths that do not race the active PR #29 branch. If architecture review exposes a current production defect on a disjoint path, fix that defect test-first in this PR rather than documenting a false operability guarantee.

**Tech Stack:** Markdown, Mermaid, Pytest, existing Four Pillars Python repository and GitHub Actions documentation checks.

## Global Constraints

- Do not edit paths currently written by PR #29: `AGENTS.md`, root `ARCHITECTURE.md`, `CHANGELOG.md`, `CLAUDE.md`, `SECURITY.md`, `.ruff.toml`, `scripts/check_docs.py`, or PR-steward source/tests.
- Treat `main` commit `cd4f4e6361238a1db43c28540640a407c7bf7c6e` as this branch's protected-main baseline until a deliberate rebase/base update occurs.
- Use exactly the canonical maturity labels `implemented_on_protected_main`, `accepted_architecture`, `active_pr`, `planned`, `deprecated`, and `superseded`; contract tests must verify that active/planned claims cannot simultaneously be labeled implemented.
- Preserve standalone direct NVIDIA NIM and explicit Contextual Orchestrator MSA integration.
- Hosted LLM credentials remain `NVIDIA_NIM_API_KEY`; `COPILOT_GITHUB_TOKEN` is prohibited for autonomous development.
- Do not introduce a database object unless a validated source defect makes it necessary; documentation must describe existing objects with their exact two-or-more-word names.
- Maintain 100% production statement and branch coverage; documentation/product tests must not lower or bypass that gate.
- Do not claim CSAP, SOC 2, ISO, NIST, or scientific certification/validation.

---

### Task 1: Establish documentation maturity and architecture viewpoints

**Files:**
- Create: `docs/standards/DOCUMENTATION_AUDIT.md`
- Create: `docs/architecture/SYSTEM_ARCHITECTURE.md`
- Test: `tests/test_documentation_architecture_contract.py`

**Interfaces:**
- Consumes: protected-main PRD, TRD, root architecture, UML, standards traceability.
- Produces: maturity vocabulary and authoritative viewpoint map used by all following tasks.

- [x] **Step 1: Write the failing documentation contract test**
- [x] **Step 2: Establish RED because canonical architecture/audit documents were absent**
- [x] **Step 3: Add the audit matrix and system architecture**
- [x] **Step 4: Extend the contract to all six maturity labels and mutual-exclusion semantics**

### Task 2: Add an ADR index and missing cross-cutting decisions

**Files:**
- Create: `docs/adr/README.md`
- Create: `docs/adr/0004-purpose-bound-personal-data.md`
- Create: `docs/adr/0005-architecture-description-and-maturity.md`
- Create: `docs/adr/0006-calculation-evidence-provenance.md`
- Create: `docs/adr/0007-autonomous-development-authority.md`
- Test: `tests/test_documentation_architecture_contract.py`

**Interfaces:**
- Consumes: ADRs 0001–0003, KASI calculation evidence, privacy/security behavior, and current automation.
- Produces: decision index, privacy design rule, documentation-authority rule, calculation-provenance rule and automation-authority rule.

- [x] **Step 1: Extend the test with ADR-index and decision assertions**
- [x] **Step 2: Establish RED for missing decisions/index**
- [x] **Step 3: Add index and accepted decisions with consequences, alternatives, reversal conditions, and implementation/test mappings**
- [x] **Step 4: Normalize ADR status vocabulary independently from architecture maturity**

### Task 3: Document the durable data model, public status schema and ERD

**Files:**
- Create: `docs/architecture/DATA_MODEL.md`
- Create: `docs/technical/JOB_STATUS_SCHEMA.md`
- Create: `docs/uml/governance-and-data.md`
- Test: `tests/test_documentation_architecture_contract.py`

**Interfaces:**
- Consumes: `src/four_pillars/jobs.py`, `src/four_pillars/ports.py`, API status/history models, idempotency syntax, artifact publication contract.
- Produces: logical/persistence model for standalone SQLite and replaceable MSA adapters plus one canonical redacted public-job schema.

- [x] **Step 1: Assert the ERD contains `report_jobs` and all four existing compliant indexes**
- [x] **Step 2: Establish RED for absent ERD/status schema**
- [x] **Step 3: Add Mermaid ERD, field-level data classification, canonical status fields/error bound and MSA adapter semantics**
- [x] **Step 4: Synchronize UML method names/signatures to the actual application ports**

### Task 4: Add threat model and purpose-bound PII control model

**Files:**
- Create: `docs/security/THREAT_MODEL.md`
- Test: `tests/test_documentation_architecture_contract.py`

**Interfaces:**
- Consumes: `SECURITY.md`, deterministic/LLM boundary, direct NIM/orchestrator secret separation, job/history/artifact flows.
- Produces: explicit assets, actors, trust zones, threats, controls, residual risks, and no-blanket-masking rule under explicit approved-purpose/allow-list constraints.

- [x] **Step 1: Add failing assertions for purpose limitation, no blanket masking, secret separation, prompt injection, retention/deletion, and privileged-access auditability**
- [x] **Step 2: Establish RED for absent threat model**
- [x] **Step 3: Write threat/control tables and Mermaid trust-boundary diagram**
- [x] **Step 4: Tie interpretation disclosure to approved purpose, authentication/authorization, field allow-list and minimum-necessary use; raw PII remains prohibited in ordinary logs/telemetry**

### Task 5: Promote testing and operability to release contracts

**Files:**
- Create: `docs/technical/TEST_STRATEGY.md`
- Create: `docs/operations/OPERABILITY.md`
- Modify: `src/four_pillars/api.py`
- Modify: `tests/test_complete_coverage_core.py`
- Test: `tests/test_documentation_architecture_contract.py`

**Interfaces:**
- Consumes: KASI/NAOJ fixture approach, CI gates, worker/job lifecycle, delete endpoint, runbook.
- Produces: realistic scientific/calculation test policy and SLI/SLO/recovery ownership with a deletion flow that preserves artifacts when durable row deletion is refused and leaves cleanup retryable after a post-row artifact failure.

- [x] **Step 1: Add assertions for independent solar-term fixtures, boundary tests, 100% statement/branch coverage, LLM contract separation, recovery, backup, retention, deletion, incident response, and multi-node adapter obligations**
- [x] **Step 2: Add RED regression tests for artifact preservation and retryable cleanup on report deletion**
- [x] **Step 3: Change delete ordering to validate the trusted artifact path, commit terminal row deletion first, then remove the artifact; retry a trusted orphan cleanup by job ID when the row was already deleted**
- [ ] **Step 4: Observe GREEN on exact-head CI and maintain 100% production statement/branch coverage**

### Task 6: Fix the no-early-stop autonomous-development control context

**Files:**
- Create: `docs/operations/AUTONOMOUS_DEVELOPMENT.md`
- Test: `tests/test_documentation_architecture_contract.py`

**Interfaces:**
- Consumes: existing minute-17 sentinel and minute-47 OpenCode workflow; proposed minute-07 PR steward remains `active_pr` until merged.
- Produces: durable prompt context that the existing product-development prompt reads under the operations documentation family.

- [x] **Step 1: Add assertions for no-early-stop, work-conserving queue, exact-head/base revalidation, waiting-is-local behavior, mandatory exit sweep, `NVIDIA_NIM_API_KEY`, and prohibition of `COPILOT_GITHUB_TOKEN`**
- [x] **Step 2: Establish RED for the missing durable contract**
- [x] **Step 3: Add the autonomous-development contract**
- [x] **Step 4: Make credential-free verification mandatory before publication and fail closed if that separation cannot be enforced**

### Task 7: Synchronize PRD, TRD, traceability and doctoring

**Files:**
- Modify: `docs/product/PRD.md`
- Modify: `docs/technical/TRD.md`
- Create: `docs/standards/ARCHITECTURE_TRACEABILITY.md`
- Create: `docs/doctoring/canonical-architecture-documentation.md`
- Test: `tests/test_documentation_architecture_contract.py`

**Interfaces:**
- Consumes: Tasks 1–6.
- Produces: product/technical entry points, requirement→evidence traceability, and APA 7 current-versus-draft standards evidence.

- [x] **Step 1: Add assertions for documentation completeness, purpose-bound PII controls, maturity labels and canonical architecture links**
- [x] **Step 2: Establish RED for missing links/evidence families**
- [x] **Step 3: Synchronize PRD/TRD and architecture traceability**
- [x] **Step 4: Add primary/current standards doctoring while keeping NIST SSDF 1.2 explicitly marked as an Initial Public Draft**

### Task 8: Full verification, review repair and merge

**Files:**
- Verify all changed files.

**Interfaces:**
- Consumes: complete documentation and deletion-safety increment.
- Produces: one reviewable architecture/governance PR that remains path-disjoint from PR #29.

- [ ] **Step 1: Run/review exact-head Ruff and compileall**
- [ ] **Step 2: Run/review `check_docs.py` and `check_prompts.py`**
- [ ] **Step 3: Run/review full non-hosted tests with exact 100% production statement/branch coverage**
- [ ] **Step 4: Build package/container and inspect security/SAST gates**
- [ ] **Step 5: Verify no changed path overlaps active PR #29 before further source writes**
- [ ] **Step 6: Address every valid current-head review thread and resolve only addressed threads**
- [ ] **Step 7: Revalidate live `main`/PR #29; if #29 merges first, update its maturity classification before this PR can merge**
- [ ] **Step 8: Merge only through exact-head repository governance, then update protected-main operational/documentation evidence and continue the product queue**
