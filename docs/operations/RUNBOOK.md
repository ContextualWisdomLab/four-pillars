# Operations Runbook

## Start and stop

Create `.env` from `.env.example`, configure the Contextual Orchestrator gateway, set secrets outside source control, and run `docker compose up -d --build`. The API listens on port 8000 and the worker shares the `artifacts` volume. Stop with `docker compose down`; add `-v` only when intentionally deleting the SQLite database and all artifacts.

Product LLM configuration is fixed to `INTERPRETATION_BACKEND=contextual_orchestrator` and `CONTEXTUAL_ORCHESTRATOR_MODEL=orchestrator/free`. Set `CONTEXTUAL_ORCHESTRATOR_BASE_URL` and `CONTEXTUAL_ORCHESTRATOR_TOKEN`. Credential-bearing model endpoints must use HTTPS, except explicit loopback HTTP addresses (`localhost`, `127.0.0.1`, or `::1`) used for local development.

Four Pillars does not accept provider-native credentials as a production routing mechanism. Provider discovery, free-pool eligibility, and failover inside that pool are Contextual Orchestrator responsibilities.

## Readiness checklist

1. `GET /health` returns `ok` and the expected version.
2. `GET /ready` returns `ready` and produces no permission error.
3. A golden chart request returns the committed pillar fixture and fingerprint.
4. A queued report changes to running when the worker is available.
5. An `orchestrator/free` smoke job completes and its manifest hashes match files.
6. `traces.json` records the virtual model, attempts, repairs, prompt versions, and prompt hashes without credentials or raw prompt content.
7. PDF text can be selected and Korean glyphs display correctly.
8. API authentication rejects an incorrect key when enabled.
9. The orchestrator usage ledger shows `service=four-pillars` and no personal data in attribution.
10. `python scripts/product_gap_audit.py` and `python scripts/check_docs.py` pass, including the direct-provider-bypass guard and standards traceability.

## Common incidents

### Jobs remain queued

Check that the worker container is running, points to the same `DATABASE_URL` and artifact volume, and can acquire the SQLite file. Restart one worker at a time. Do not mark jobs completed manually.

### Jobs remain running after a crash

Confirm through worker ownership and process evidence that no worker still owns the job. Preserve the database and temporary directory for incident evidence. The current release does not automatically requeue running jobs because duplicate model calls can create inconsistent charges and artifacts.

After ownership is cleared, record the stranded job ID and its original idempotency digest, then recreate the request with a newly generated `Idempotency-Key`. Reusing the prior key and payload would correctly replay the existing queued or running job rather than create recovery work. Do not delete or mutate the stranded row until retention, billing, and incident evidence obligations have been satisfied.

### Contextual Orchestrator is unavailable

Confirm gateway DNS/TLS, `/v1/chat/completions`, Bearer token scope, the `orchestrator/free` pool, compute mode, route capacity, and downstream worker health. Compare Four Pillars attempts with the gateway request/cost ledger.

Keep deterministic calculations available and let report jobs fail or remain queued according to operator policy. Do not add a local NVIDIA NIM, OpenAI, OpenRouter, Bytez, or other provider fallback.

### `orchestrator/free` has no eligible model

Treat an empty free pool as an explicit availability failure. The product must not silently switch to a paid route. Diagnose discovery, free-eligibility metadata, provider health, or route policy in the `contextual-orchestrator` repository.

### Contextual Orchestrator bypasses routing or conduct

Capture the outbound adapter request with the offline mock contract. It must include `model=orchestrator/free`, a valid `mode` (`auto`, `route`, or `conduct`), and no `response_format`, tool, or function-calling passthrough field. Those provider-feature keys can collapse the request to a single upstream provider path. Four Pillars enforces JSON through explicit prompting, Pydantic validation, and bounded same-route repair instead.

### Contextual Orchestrator rejects structured responses

Confirm that its deployed version accepts OpenAI-compatible messages, `mode`, `attribution`, and `routing`, and that it returns `choices[0].message.content`. Reproduce with the offline adapter contract and the orchestrator's route/conduct/free-pool tests. Do not restore provider passthrough fields as a workaround.

### Attribution or cost records are incorrect

Expected attribution always includes `service=four-pillars`; account, team, group, and company are optional deployment labels. It must not include subject names, birth data, notes, fingerprints, prompt/generated content, artifact paths, or credentials. Correct Four Pillars configuration or orchestrator ledger logic in a reviewed PR. Do not add sensitive labels to aid debugging.

### Quality failures increase

Compare `orchestrator/free`, orchestration mode, prompt versions, and failed findings. Run deterministic fixtures and the supplementary live judge suite where authorized. Repair prompts, orchestration, or eligible-route behavior in a pull request; never weaken fingerprint, allowed-pillar, medical, coercion, relationship-balance, or event-certainty controls to increase completion rate.

### PDF generation fails

Verify ReportLab, artifact-volume permissions, and CJK CID font registration. Preserve `report.json` to reproduce locally. A PDF failure must not mark the job completed.

### Standards or hourly checks fail

Read the single `[hourly-product-loop] release-quality regression` issue and attached logs. Restore missing APA references, traceability mappings, docstrings, coverage, database naming, or build evidence rather than suppressing the gate. A standard revision triggers review; it does not silently change production behavior.

## Backups and recovery

For a single-node deployment, stop the worker briefly or use SQLite's online backup API, then copy the database and completed artifact directories to encrypted storage. Restore both database and matching UUID directories. Manifests permit integrity verification. API keys and orchestrator tokens come from secret management, not backup archives.

A multi-node integration must document transaction guarantees, backup/restore point objectives, object-version recovery, idempotency uniqueness, and deterministic history ordering behind the same structural ports.

## Retention and deletion

Default retention is 30 days. `four-pillars cleanup` deletes terminal database rows older than the configured period and their UUID directories. An authenticated DELETE endpoint removes an individual terminal job immediately. Logs and gateway metadata must not retain raw report contents after authorized deletion beyond documented orchestrator/provider obligations.

## Security response

1. Revoke an exposed API or Contextual Orchestrator credential immediately.
2. Preserve bounded audit evidence without copying private report payloads into tickets.
3. Identify affected job IDs, virtual model, orchestration mode, prompts, artifacts, and time window.
4. Suspend generation while deterministic calculation endpoints remain available when safe.
5. Correct the root cause through tests and a reviewed PR.
6. Re-run Security Scan, Semgrep, the complete offline gate, and authorized `orchestrator/free` smoke tests.
7. Rotate credentials and restore service from an immutable release.
8. Document residual risk and user notification obligations.

## Release procedure

1. Update `CHANGELOG.md` for user-visible, integration-visible, security, architecture, and standards changes.
2. Run dependency, product-gap, Ruff/docstring, compileall, document, prompt, all offline tests with exactly 100% statement/branch coverage, package, container, Security Scan, and Semgrep gates.
3. Review the complete diff, issue comments, review submissions, code-scanning findings, and inline threads.
4. Merge only the exact head whose checks passed.
5. For a releaseable change, advance package/runtime/API version together and publish wheel, source distribution, and `SHA256SUMS` through the least-privilege release workflow.
6. Deploy the immutable commit, run readiness, and record calculation, prompt, `orchestrator/free`, orchestration mode, and artifact versions.
7. Roll back to the previous image if deterministic fixtures, schema validation, quality pass rate, privacy, or output integrity regress.

## Evidence and standards

`docs/standards/REFERENCES.md` contains APA 7th entries for the current engineering standards and peer-reviewed evaluation research. `docs/standards/TRACEABILITY.md` maps them to controls, tests, workflows, and residual gaps. The mapping supports continual improvement but is not an ISO certification or scientific validation of traditional Four Pillars interpretation.
