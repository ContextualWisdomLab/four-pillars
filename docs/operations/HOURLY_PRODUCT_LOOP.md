# Hourly Product Quality Loop

The hourly product loop is the repository's autonomous release-readiness sentinel. It runs deterministic checks only, never changes application source, never calls a hosted model, and records a persistent GitHub issue only when a release-quality or product-contract regression is present.

## Schedule

GitHub Actions runs `.github/workflows/hourly-product-loop.yml` at minute 17 of every hour. The non-zero minute avoids the busiest boundary of the public scheduler while preserving an hourly interval. Operators can also use `workflow_dispatch` to run the same revision immediately after an incident, dependency update, infrastructure change, standards review, or repository restoration.

The workflow uses one concurrency group and does not cancel an in-progress run. A slow verification therefore finishes with coherent evidence instead of being replaced by the next scheduled invocation.

## Separate product-development loop

The deterministic sentinel is intentionally not a coding agent. A separate `.github/workflows/hourly-nim-product-development.yml` workflow runs at minute 47 and may use checksum-pinned OpenCode with `NVIDIA_NIM_API_KEY` to propose one bounded pull request only when open-PR inventory is readable and empty.

That workflow separates model execution, uncredentialed verification, and late publication onto three fresh runners. It never approves, merges, tags, releases, deploys, or changes reviewer-agent credentials. Its full trust boundary, configuration, failure modes, rollback, and APA 7 evidence are documented in `docs/operations/HOURLY_NIM_PRODUCT_DEVELOPMENT.md` and `docs/doctoring/hourly-nim-opencode-development.md`.

The two schedules use different concurrency groups and responsibilities. A minute-47 proposal cannot substitute for a minute-17 quality result, and the quality sentinel cannot publish source changes.

## Release-quality gate

Each invocation installs the hash-locked Python 3.12 CI environment and executes every release gate even when an earlier gate fails:

1. dependency consistency with `pip check`;
2. the deterministic product-gap audit;
3. Ruff, including production docstring enforcement;
4. Python bytecode compilation;
5. required-document and standards-traceability validation;
6. versioned-prompt validation;
7. all non-hosted tests with the 100% statement and branch coverage floor; and
8. source-distribution and wheel construction.

Every command writes a bounded log excerpt to `artifacts/hourly-product-loop.md` and the GitHub job summary. The final step fails the workflow only after all gates have run, so one hourly execution exposes the complete failure surface.

## Product-gap audit

`scripts/product_gap_audit.py` is offline and deterministic. It checks:

- product, technical, security, operations, UML, ADR, and standards documentation;
- package/runtime/changelog version consistency;
- the exactly 100% statement and branch coverage floor;
- prompt semantic versions and SHA-256 digests;
- direct `NVIDIA_NIM_API_KEY` and optional `CONTEXTUAL_ORCHESTRATOR_TOKEN` boundaries;
- explicit interpretation backend selection and no implicit fallback;
- Contextual Orchestrator adapter, attribution, and structural-generation contracts;
- ISO, NIST, IETF, W3C, and peer-reviewed APA 7th reference traceability;
- deterministic-core dependency boundaries;
- the presence of the hourly and reusable release workflows; and
- every application-owned database object name.

Database application objects must use at least two words in `snake_case`, `camelCase`, or `PascalCase`. `snake_case` is preferred. The current SQLite schema includes `report_jobs`, `idx_report_jobs_status_created`, `idx_report_jobs_idempotency_key_digest`, `idx_report_jobs_created_id`, and `idx_report_jobs_status_created_id`. SQLite-owned names beginning with `sqlite_` are outside the application naming policy.

The audit is independent of GitHub APIs and hosted services. It can be run before a commit with:

```bash
PYTHONPATH=src python scripts/product_gap_audit.py
```

A successful run emits a Markdown PASS report and exits with status zero. Each detected gap includes a stable code, severity, path, and remediation-oriented message.

## Standards and research review

`docs/standards/REFERENCES.md` records current engineering standards and peer-reviewed LLM-evaluation evidence using APA 7th entries. `docs/standards/TRACEABILITY.md` maps those sources to code, tests, workflows, limitations, and future gaps.

The hourly loop verifies required references and control tokens but does not automatically change behavior when a standard or paper changes. A material update must be researched against the authoritative source, documented, implemented with a failing regression test, reviewed, and released through the normal pull-request process.

The standards map is an engineering control record. It is not an ISO certification or scientific validation of traditional Four Pillars interpretation.

## Failure issue lifecycle

The workflow has read-only repository-content permission and issue write permission. It searches for one open issue titled `[hourly-product-loop] release-quality regression`.

- On failure, it creates the issue when none exists or appends the newest complete report as a comment.
- On recovery, it closes the same open issue with the verified commit SHA.
- It never creates one issue per gate or per hour, preventing alert floods while preserving a chronological incident record.

The issue is evidence and coordination, not an automated source-code change. Remediation follows the normal branch, test-first pull request, review, check, and merge process.

## Security and NIM boundary

The minute-17 hourly loop never calls direct hosted NVIDIA NIM or Contextual Orchestrator and receives neither `NVIDIA_NIM_API_KEY` nor `CONTEXTUAL_ORCHESTRATOR_TOKEN`. Hosted generation, the separate minute-47 proposal workflow, and LLM-as-a-judge evaluation retain independent secret and trust boundaries.

User birth data, notes, report prompts, generated prose, API authentication values, provider credentials, gateway attribution, and artifact content are not uploaded by the minute-17 loop. The scheduled audit verifies configuration names and source contracts only.

Actions are pinned to immutable commit SHAs. Dependencies are installed from hash-locked CI requirements. The GitHub token is scoped to repository metadata and issues required by the incident lifecycle.

## Manual recovery

When the workflow fails:

1. open the single regression issue and identify every failed gate;
2. reproduce the commands locally against the exact failing commit;
3. create a focused branch and a failing realistic regression test;
4. fix the root cause without weakening the gate;
5. update standards traceability or operations doctoring when the failure changes a control;
6. obtain pull request review and rerun CI, Security Scan, and Semgrep;
7. merge only the exact green head; and
8. manually dispatch the hourly workflow when immediate recovery confirmation is needed.

If issue synchronization itself fails, inspect repository issue permissions and GitHub CLI output. Do not grant content write permission to the scheduled workflow merely to repair issue management.