# Autonomous Development Contract

**Purpose:** durable control context for repository-local autonomous development and review automation.  
**Applies to:** the existing minute-47 NVIDIA NIM/OpenCode product-development workflow and any successor that reads operations documentation.  
**Maturity:** this contract becomes `implemented_on_protected_main` only after integration into protected main at an exact commit and completion of all required CI, security, coverage, review, provenance, and operational evidence; PR #29's PR steward is `superseded` historical evidence because it closed without merge.

## 1. No-early-stop rule

**NO-EARLY-STOP:** one inventory, one RCA, one documentation edit, one test result, one generated patch, one PR creation, one review request, one queued Check, one merge, or one discovered blocker is an intermediate state whenever another safe executable action remains inside the bounded run.

The repository's “one bounded PR per product-development run” rule is a writer-safety limit. It is not permission to stop after one trivial action. Within that one coherent increment the agent must continue from evidence → root cause → RED test/evidence → implementation/docs → GREEN verification → packaging/review preparation until the bounded increment is genuinely reviewable or the practical run budget is exhausted.

## 2. Work-conserving queue

The product-development loop is **work-conserving**. Repeatedly select the highest-value executable item:

1. protect/finish an existing open PR when this workflow is explicitly operating in repair mode and owns a safe branch lease;
2. fix a valid current defect test-first;
3. remove a repository-owned CI/security/documentation-contract blocker;
4. finish an incomplete bounded product slice already selected for the run;
5. repair authoritative documentation that current protected-main behavior has outgrown;
6. when PR/issues are empty, select the highest-impact buyer-visible product or operational Gap that fits one coherent PR;
7. use remaining safe budget for tests, coverage/docstrings, security/privacy, reliability, observability, accessibility, provenance, operability, or release evidence tied to that same increment.

Do not manufacture unrelated changes merely to keep the runner busy.

## 3. Waiting is local

**WAITING IS LOCAL.** A queued/pending review, Check, provider cooldown, external approval, occupied branch, or read-only dependency blocks only that action. Do not spend the run polling it. Continue disjoint analysis or implementation if it can be done without racing another writer or invalidating exact-head evidence.

Central `.github`, `naruon`, `contextual-orchestrator`, and repositories with their own enabled writer loops are read-only dependencies from this repository-local writer unless an explicit separate lease says otherwise.

## 4. Fresh exact evidence

At run start, and again immediately before any write/publish action, refresh:

- protected-main commit;
- every relevant open PR's **exact head**;
- the **exact live base** branch tip rather than trusting stale PR-body/base metadata;
- review decisions and unresolved threads;
- required/current Checks and workflow runs;
- source/ref/blob identity for the target write;
- release/version state;
- active writer/automation state when observable.

A source/ref/blob movement by another writer invalidates the branch lease for the stale operation. Freeze that branch rather than racing it.

## 5. RCA and feasibility

For any non-passing gate, identify:

- exact current failing boundary;
- first failing job/step or review condition;
- symptom versus immediate/root/systemic cause where material;
- correction owner;
- materially distinct smallest remedies;
- actual permissions/credentials/tool/API/workflow support;
- security/privacy blast radius and rollback;
- observable success evidence.

A theoretical fix is not enough. Reject remedies that need invented credentials, reviewers, authority, weakened tests/protection, stale evidence, or a write to a dependency currently owned by another loop.

## 6. TDD and verification

For source/behavior defects:

1. establish the smallest realistic RED regression at the intended production boundary;
2. prove the failure is the target defect rather than fixture/setup failure;
3. implement the narrowest root-cause fix;
4. observe GREEN;
5. run the focused suite and all affected release-quality gates;
6. preserve exactly 100% owned production statement and branch coverage and complete public docstrings;
7. update PRD/TRD/architecture/ADR/threat/test/operations/CHANGELOG documents when their contracts changed.

Calculation changes require independent authoritative/golden evidence, not an LLM-generated expected value.

For model-proposed code, **credential-free verification before publication is mandatory**. Candidate code must be reconstructed on an exact immutable base/head/artifact identity and executed without the model credential and without publication/merge/reviewer authority. If the selected workflow cannot enforce that boundary, publication must fail closed. An alternative is allowed only through a separate Accepted ADR that proves equivalent separation and executable regression tests; convenience is not a compensating control.

## 7. Model and credential boundary

Autonomous development that actually calls a hosted model uses only GitHub Secret **`NVIDIA_NIM_API_KEY`** through the immutably reviewed OpenCode/NVIDIA path. **`COPILOT_GITHUB_TOKEN` is prohibited** for autonomous product development.

Do not alter the existing independent review-agent identities, credential names, scopes, or key chain. Model execution does not receive merge/release/reviewer authority. Candidate patches cross trust zones as bounded artifacts and must be revalidated without the model credential before publication.

Do not pass unrelated GitHub/OIDC/Actions runtime credentials, command-file paths, provider secrets, personal data, or operator credentials into the model process merely because they exist in the runner environment.

## 8. LLM orchestration design

Where product behavior uses LLM orchestration, preserve direct NIM as a standalone option and Contextual Orchestrator as an explicit optional adapter. No silent provider fallback.

When orchestration depth is material, use current primary Fugu/Conductor/TRINITY-class evidence to design comparable-budget tests across single-model routing and staged/deeper conduct. Record workflow stages, recursion depth, task decomposition, access lists, role-specific reasoning effort, token/compute budget, deterministic fidelity, quality/safety outcomes, and reasoning-level ablation. Optimize correctness/evidence/reliability rather than latency alone.

## 9. Documentation completeness gate

A bounded increment is not review-ready if its material behavior cannot be understood from the repository's canonical documentation graph. Check at least:

- PRD and TRD;
- root/canonical Architecture;
- ADR index and affected ADRs;
- UML and ERD/data model when structure/state/persistence changes;
- Threat Model and privacy/control flows when trust/data changes;
- Test Strategy when evidence/quality policy changes;
- Operability/runbook when lifecycle/recovery/deployment changes;
- standards/research traceability and APA 7 doctoring;
- Figma reference for material visual workflow changes;
- CHANGELOG for user/operator-visible changes.

Documentation-only completion does not justify stopping if the same bounded increment still has an executable implementation/test task.

## 10. Privacy and security

Do not use blanket PII masking when it breaks deterministic calculation or a legitimate requested interpretation. That is not permission to send arbitrary personal data to a model.

Personal data may cross a model boundary only when all of the following are true:

1. the processing purpose is explicitly approved for the selected backend;
2. the caller is authenticated/authorized for that purpose;
3. the field is included in the versioned model-input allow-list/schema for that purpose;
4. the value is necessary for the requested result or an approved purpose-preserving transformation is applied;
5. the selected provider/region/retention/subprocessor boundary is the configured recipient;
6. the payload excludes unrelated identity, credentials, internal paths, private traces and data from other users/jobs.

Otherwise the field is omitted. Raw PII, prompts/reports, credentials and internal paths are never emitted to ordinary logs, metrics, traces, PR metadata, model attribution, or autonomous-development evidence. Any safe transformation is field- and purpose-specific; it must not be a blanket mask that silently changes the calculation or meaning.

Apply purpose limitation, minimum necessary disclosure, authentication/authorization, encryption, restricted telemetry/attribution, secret separation, retention/deletion, and audited privileged access as documented in ADR 0004 and the Threat Model.

Design for CSAP/SOC 2 procurement readiness without claiming certification. Preserve fail-closed evidence, least privilege, immutable pins where practical, artifact/provenance integrity, vulnerability management, incident/recovery responsibilities, and supply-chain checks.

## 11. Merge and release authority

The product-development model does not approve, merge, tag, release, deploy, or weaken protection. Existing GitHub review/Check/branch governance remains authoritative. PR #29 is `superseded` historical evidence; its former steward proposal has no current review, repair, merge-queue, or branch ownership authority.

A release is allowed only from an exact integrated protected-main commit with the repository's required CI/security/100% coverage/package/container/review/provenance/operational gates satisfied. Version and CHANGELOG move only actually shipped changes.

## 12. Mandatory final sweep

Before a run ends, perform a **MANDATORY FINAL SWEEP** of the bounded scope and repository queue. Ask internally:

- can an exact-head PR safely advance or merge under actual governance?
- can a current defect or failed Check be repaired?
- can an addressed review thread be resolved?
- can a Draft be advanced without racing another writer?
- can an accepted issue be executed?
- can protected-main operational/release evidence be run?
- is canonical documentation materially stale or missing?
- if PR/issues are empty, can one bounded buyer-visible Gap be implemented?

If any answer is yes and practical execution budget remains, ending is prohibited. Act and sweep again. The hourly recurrence is continuation after genuine budget exhaustion, not an excuse for voluntary early termination.

### Machine-readable termination evidence

Every voluntary termination decision must produce a versioned `final_sweep_record_v1` evidence object in the owning automation/run evidence channel. It is operational evidence, not a substitute for GitHub checks or review. At minimum it contains:

- `scope`: the bounded repository/product surfaces examined;
- `protected_main_sha`: exact protected-main identity observed for the sweep;
- `live_base_sha`: exact independently resolved base-ref identity used for branch-sensitive decisions;
- `source_head_sha`: exact contributor/source head identity evaluated;
- `required_documents`: canonical-document inventory with current/stale/missing classification;
- `gate_results`: exact required check/review/security/coverage/provenance results and their bound revisions;
- `remaining_executable_work`: concrete safe actions still executable now, if any;
- `remaining_budget`: bounded run/tool budget state used only to avoid starting work that cannot reach a safe stopping point;
- `final_decision`: continue, budget_continuation, or no_executable_lane;
- `recorded_at`: timestamp of the final fresh sweep; and
- `provenance`: workflow/run identity and evidence-source references sufficient to reconstruct the decision.

A missing, stale, or unknown identity, document state, gate result, remaining-work assessment, or provenance field must **fail closed**: it cannot justify `no_executable_lane` or product completion. A queued/pending gate remains non-passing, and a waiting lane cannot hide another executable lane. This record must be regenerated after any material ref/head/base/review/check change.

## 13. Scheduler roles

| Schedule/control | Current role | Maturity |
|---|---|---|
| minute 17 | deterministic product-quality sentinel | `implemented_on_protected_main` |
| minute 47 | NVIDIA NIM/OpenCode bounded product proposal | `implemented_on_protected_main` |
| minute 07 PR steward | PR #29 is `superseded`; no current execution authority | `superseded` |

Keep these roles non-overlapping. Consolidate/remove a loop if protected-main evidence shows it duplicates another writer or creates unsafe races.
