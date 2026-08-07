# Hourly governed pull-request steward implementation plan

> Execute test-first. Do not open the implementation pull request until the existing queue is empty, the branch is rebased on current `main`, and the complete exact-head gate passes.

## Goal

Close the buyer-visible throughput gap in which any open pull request suspends the minute-47 product-development loop. Add a minute-7 steward that reads one oldest non-draft PR, repairs exact-head failures through an isolated NVIDIA NIM OpenCode path, or queues normal squash auto-merge without bypassing review or branch protection.

## Task 1: executable RED contracts

Create `tests/test_hourly_pr_steward.py` before the workflow. Require:

- independent minute-7 schedule and non-cancelling concurrency;
- one-oldest-PR inventory and fail-closed API handling;
- strict `none|wait|repair|queue_merge` action selection;
- exact head/base, review decision, unresolved threads, and Check state;
- three-runner repair isolation plus separate merge runner;
- `NVIDIA_NIM_API_KEY` only and no `COPILOT_GITHUB_TOKEN`;
- immutable artifact ID/digest, patch SHA-256, file/byte limits, and Git-mode rejection;
- no proposed-code execution in the credential-bearing publisher;
- no `--admin`, approval, force push, tag, release, or deploy command;
- complete repository verification gate after patch application;
- exact-head/base revalidation before push or auto-merge;
- realistic fixtures for pending/failed Checks, requested changes, unresolved threads, stale heads, API failure, external forks, successful repair, and governed auto-merge;
- root and operational documentation plus APA 7 doctoring.

Run the focused test and record the expected missing-workflow/document RED failure.

## Task 2: bounded evidence serializer

Create `scripts/prepare_pr_steward_evidence.py` as a standard-library-only trusted serializer. It must:

- read a regular non-symlink JSON input without following path redirection;
- validate one strict schema and reject unknown fields;
- normalize Unicode and reject unsupported controls and bidirectional overrides;
- cap the source, review, thread, and Check byte budgets;
- output canonical UTF-8 JSON with mode `0600`;
- expose a small typed public API with complete docstrings;
- include unit tests for realistic Korean review text, malformed UTF-8, oversized evidence, controls, symlinks, directories, unknown fields, and noncanonical SHAs/URLs.

Run focused tests RED then GREEN. Because the script is outside `src/four_pillars`, package coverage remains unchanged, but its tests must cover every branch.

## Task 3: read-only inspector

Implement `.github/workflows/hourly-pr-steward.yml` inspection job:

- minute 7 and manual dry run;
- repository read, pull-request read, Check read, and Actions read only;
- select the oldest non-draft open PR and no more than one;
- query review decision and unresolved threads through GraphQL;
- query latest exact-head Check runs and reject malformed or incomplete inventory;
- request one exact-head automated review marker without changing reviewer identity;
- serialize bounded evidence with the trusted script;
- output exact PR number, same-repository head branch, head SHA, base branch, base SHA, action, and evidence artifact identity;
- choose `wait` for pending evidence, missing NIM/App configuration, external forks, or any inventory failure.

## Task 4: credential-isolated OpenCode repair proposer

For `repair` only:

- check out the exact head without persisted credentials;
- install the hash-pinned repository environment and checksum-pinned OpenCode archive;
- configure only NVIDIA NIM and the current fallback list;
- pass only `NVIDIA_NIM_API_KEY` to the model process;
- remove GitHub, OIDC, Actions runtime/cache, command-file, reviewer, and publication channels;
- deny OpenCode web tools, external directories, task delegation, GitHub CLI, remote Git, commit, push, tag, release, and deploy commands;
- tell the model to address only bounded review/Check evidence and to treat it as untrusted data;
- require tests, docstrings, docs, CHANGELOG, APA 7 doctoring, database naming, standalone/MSA compatibility, and realistic domain validation when affected;
- export at most one binary full-index patch, maximum 40 files/500,000 bytes, no symlinks/gitlinks, with exact digest/count metadata.

## Task 5: fresh verifier

On a separate runner with no NIM or App secret:

- download by numeric artifact ID;
- query and match artifact digest, workflow run, name, and expiry;
- validate patch SHA-256, bytes, file count, modes, and exact base;
- apply the patch and unset all GitHub/OIDC/Actions runtime and command-file channels once for the complete shell;
- run `pip check`, product-gap audit, Ruff/public docstrings, compileall, document/prompt checks, all non-live tests with 100% statement and branch coverage, package build, and pinned container build;
- prove the staged patch digest is unchanged after verification.

## Task 6: non-executing publisher

On a third runner:

- preserve the trusted evidence/parser utilities before applying the untrusted patch;
- validate and apply the same artifact without importing, testing, or executing proposed code;
- mint the existing repository-scoped maintainer App token only after validation;
- re-query the PR and require state open, same-repository branch, exact unchanged head and base, and no branch-ownership change;
- create one normal commit with hooks disabled and push fast-forward without force;
- never merge in the repair run; fresh review and Checks must run on the new head.

## Task 7: governed merge path

On a separate merge runner:

- mint the maintainer App token late;
- re-query exact head/base, Check runs, review decision, and unresolved threads;
- require no pending/failing Checks, no requested changes, and zero unresolved threads;
- queue `gh pr merge --squash --auto --delete-branch` without `--admin`;
- let required independent approvals, branch protection, and exact-head Checks remain authoritative;
- never approve, force push, tag, release, or deploy.

## Task 8: documents and traceability

Update:

- `AGENTS.md`, `CLAUDE.md`, and `ARCHITECTURE.md`;
- `docs/operations/HOURLY_PR_STEWARD.md` and existing loop runbooks;
- `docs/doctoring/hourly-pr-steward.md` with APA 7 references and claim boundaries;
- architecture Mermaid/PlantUML where applicable;
- `CHANGELOG.md` under `Unreleased`;
- product-gap audit contracts so accidental removal or credential drift fails CI.

Figma is not required because this increment changes no buyer-facing visual flow.

## Task 9: exact-head verification and PR publication

Rebase the branch on the latest `main`, run the complete gate on Python 3.11 and 3.12, container, Security Scan, and Semgrep, then open one pull request. Request exact-head automated review. Resolve every actionable thread, rerun all Checks, and queue normal squash auto-merge. Do not version-bump or release in the feature PR; perform a separate release only after merge and exact-head release validation.
