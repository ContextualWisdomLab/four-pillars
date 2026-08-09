# Canonical Architecture Documentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Four Pillars' architecture record acquisition-grade, machine-checkable, and unambiguous about protected-main reality versus active or planned work.

**Architecture:** Extend the existing PRD/TRD/UML/ADR/standards set with a canonical documentation graph rather than replacing it. Add a maturity model, logical ERD, threat model, test strategy, operability contract, and autonomous-development control context on paths that do not race the active PR #29 branch; keep source behavior unchanged.

**Tech Stack:** Markdown, Mermaid, Pytest, existing Four Pillars Python repository and GitHub Actions documentation checks.

## Global Constraints

- Do not edit paths currently written by PR #29: `AGENTS.md`, `ARCHITECTURE.md`, `CHANGELOG.md`, `CLAUDE.md`, `SECURITY.md`, `.ruff.toml`, `scripts/check_docs.py`, or PR-steward source/tests.
- Treat `main` commit `cd4f4e6361238a1db43c28540640a407c7bf7c6e` as this branch's protected-main baseline.
- Use maturity labels so active-PR and planned behavior is never called shipped behavior.
- Preserve standalone direct NVIDIA NIM and explicit Contextual Orchestrator MSA integration.
- Hosted LLM credentials remain `NVIDIA_NIM_API_KEY`; `COPILOT_GITHUB_TOKEN` is prohibited for autonomous development.
- Do not introduce a database object; documentation must describe existing objects with their exact two-or-more-word names.
- Maintain 100% production statement and branch coverage; documentation tests must not lower or bypass that gate.
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

- [ ] **Step 1: Write the failing documentation contract test**

Create assertions for the two new files and for maturity labels `implemented_on_protected_main`, `accepted_architecture`, `active_pr`, `planned`, and `superseded`.

- [ ] **Step 2: Run the focused test and observe RED**

Run: `pytest -q tests/test_documentation_architecture_contract.py`

Expected: failure because canonical architecture/audit documents do not exist.

- [ ] **Step 3: Add the audit matrix and system architecture**

Record current protected-main behavior, active PR #29 as `active_pr`, stakeholder concerns, trust boundaries, standalone/MSA views, and missing-document remediation status.

- [ ] **Step 4: Re-run the focused test**

Expected: maturity/viewpoint assertions pass.

### Task 2: Add an ADR index and missing cross-cutting decisions

**Files:**
- Create: `docs/adr/README.md`
- Create: `docs/adr/0004-purpose-bound-personal-data.md`
- Create: `docs/adr/0005-architecture-description-and-maturity.md`
- Test: `tests/test_documentation_architecture_contract.py`

**Interfaces:**
- Consumes: ADRs 0001–0003 and privacy/security behavior already implemented on main.
- Produces: decision index, privacy design rule, and documentation-authority rule.

- [ ] **Step 1: Extend the test with ADR-index and decision assertions**
- [ ] **Step 2: Observe RED**
- [ ] **Step 3: Add index and accepted decisions with consequences, alternatives, reversal conditions, and implementation/test mappings**
- [ ] **Step 4: Observe GREEN**

### Task 3: Document the durable data model and ERD

**Files:**
- Create: `docs/architecture/DATA_MODEL.md`
- Test: `tests/test_documentation_architecture_contract.py`

**Interfaces:**
- Consumes: `src/four_pillars/jobs.py`, history/idempotency models, artifact publication contract.
- Produces: logical/persistence model for standalone SQLite and replaceable MSA adapters.

- [ ] **Step 1: Assert the ERD contains `report_jobs` and all four existing compliant indexes**
- [ ] **Step 2: Observe RED**
- [ ] **Step 3: Add Mermaid ERD and a field-level data classification/retention table**
- [ ] **Step 4: Observe GREEN**

### Task 4: Add threat model and purpose-bound PII control model

**Files:**
- Create: `docs/security/THREAT_MODEL.md`
- Test: `tests/test_documentation_architecture_contract.py`

**Interfaces:**
- Consumes: `SECURITY.md`, deterministic/LLM boundary, direct NIM/orchestrator secret separation, job/history/artifact flows.
- Produces: explicit assets, actors, trust zones, threats, controls, and residual risks.

- [ ] **Step 1: Add failing assertions for purpose limitation, no blanket masking, secret separation, prompt injection, retention/deletion, and privileged-access auditability**
- [ ] **Step 2: Observe RED**
- [ ] **Step 3: Write threat/control tables and Mermaid trust-boundary diagram**
- [ ] **Step 4: Observe GREEN**

### Task 5: Promote testing and operability to release contracts

**Files:**
- Create: `docs/technical/TEST_STRATEGY.md`
- Create: `docs/operations/OPERABILITY.md`
- Test: `tests/test_documentation_architecture_contract.py`

**Interfaces:**
- Consumes: KASI/NAOJ fixture approach, CI gates, worker/job lifecycle, runbook.
- Produces: realistic scientific/calculation test policy and SLI/SLO/recovery ownership.

- [ ] **Step 1: Add failing assertions for independent solar-term fixtures, boundary tests, 100% statement/branch coverage, LLM contract separation, recovery, backup, retention, deletion, incident response, and multi-node adapter obligations**
- [ ] **Step 2: Observe RED**
- [ ] **Step 3: Write test strategy and operability documents**
- [ ] **Step 4: Observe GREEN**

### Task 6: Fix the no-early-stop autonomous-development control context

**Files:**
- Create: `docs/operations/AUTONOMOUS_DEVELOPMENT.md`
- Test: `tests/test_documentation_architecture_contract.py`

**Interfaces:**
- Consumes: existing minute-17 sentinel and minute-47 OpenCode workflow; proposed minute-07 PR steward remains `active_pr` until merged.
- Produces: durable prompt context that the existing product-development prompt reads under the operations documentation family.

- [ ] **Step 1: Add failing assertions for no-early-stop, work-conserving queue, exact-head/base revalidation, waiting-is-local behavior, mandatory exit sweep, `NVIDIA_NIM_API_KEY`, and prohibition of `COPILOT_GITHUB_TOKEN`**
- [ ] **Step 2: Observe RED**
- [ ] **Step 3: Add the autonomous-development contract**
- [ ] **Step 4: Observe GREEN**

### Task 7: Synchronize PRD and TRD with the canonical graph

**Files:**
- Modify: `docs/product/PRD.md`
- Modify: `docs/technical/TRD.md`
- Test: `tests/test_documentation_architecture_contract.py`

**Interfaces:**
- Consumes: Tasks 1–6.
- Produces: product and technical requirement entry points linking the new authoritative documents.

- [ ] **Step 1: Add failing assertions for documentation completeness, purpose-bound PII controls, maturity labels, and links to ERD/threat/test/operability documents**
- [ ] **Step 2: Observe RED**
- [ ] **Step 3: Append narrow requirements/architecture sections without rewriting existing valid material**
- [ ] **Step 4: Observe GREEN**

### Task 8: Full verification and PR creation

**Files:**
- Verify all changed files.

**Interfaces:**
- Consumes: complete documentation increment.
- Produces: one reviewable documentation-governance PR that does not overlap PR #29's source files.

- [ ] **Step 1: Clone/fetch the exact branch into a clean workspace**
- [ ] **Step 2: Run `ruff check .`**
- [ ] **Step 3: Run `python -m compileall -q src tests scripts`**
- [ ] **Step 4: Run `python scripts/check_docs.py` and `python scripts/check_prompts.py`**
- [ ] **Step 5: Run `pytest -m 'not nim_live' -W error::ResourceWarning --cov=four_pillars --cov-report=term-missing`**
- [ ] **Step 6: Build `python -m build --no-isolation`**
- [ ] **Step 7: Confirm no changed path overlaps active PR #29 before opening the PR**
- [ ] **Step 8: Open one PR, inspect exact-head checks/reviews, repair any valid findings, and merge only through repository governance**
