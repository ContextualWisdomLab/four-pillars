# Operations Runbook

## Start and stop

Create `.env` from `.env.example`, choose exactly one `INTERPRETATION_BACKEND`, set secrets outside source control, and run `docker compose up -d --build`. The API listens on port 8000 and the worker shares the `artifacts` volume. Stop with `docker compose down`; add `-v` only when intentionally deleting the SQLite database and all artifacts.

Direct standalone generation uses `INTERPRETATION_BACKEND=nvidia_nim` and `NVIDIA_NIM_API_KEY`. Organization routing uses `INTERPRETATION_BACKEND=contextual_orchestrator`, `CONTEXTUAL_ORCHESTRATOR_BASE_URL`, and `CONTEXTUAL_ORCHESTRATOR_TOKEN`. Credential-bearing model endpoints must use HTTPS, except explicit loopback HTTP addresses (`localhost`, `127.0.0.1`, or `::1`) used for local development. Do not configure automatic failover between backends.

Purpose-required birth/context/report data remains available to authorized product processing; privacy does not depend on blanket masking. Before an enterprise/public-sector deployment, operators must additionally document the selected authorization/tenant boundary, encryption-at-rest and key ownership, backup/restore retention, deletion/export behavior, model processor/region/egress boundary, and privileged-support process in accordance with `docs/security/DATA_GOVERNANCE.md` and `docs/compliance/CSAP_SOC2_READINESS.md`.

## Readiness checklist

1. `GET /health` returns `ok` and the expected version.
2. `GET /ready` returns `ready` and produces no permission error.
3. A golden chart request returns the committed pillar fixture, `calendar-1.1.0` calculation version, and expected fingerprint.
4. Boundary acceptance for the released modern scope matches committed KASI/NAOJ fixtures; do not regenerate those fixtures from Four Pillars output.
5. A queued report changes to running when the worker is available.
6. A selected-backend smoke job completes and its manifest hashes match files.
7. `traces.json` records model, attempts, repairs, prompt versions, and prompt hashes without credentials or raw prompt content.
8. PDF text can be selected and Korean glyphs display correctly.
9. API authentication rejects an incorrect key when enabled.
10. Contextual Orchestrator deployments show `service=four-pillars` in the shared usage ledger and no personal data in attribution.
11. Public report history does not expose stored request, subject/birth/context, fingerprint, idempotency material, generated copy, raw traces, or internal artifact path.
12. `python scripts/product_gap_audit.py` and `python scripts/check_docs.py` pass, including standards/documentation traceability.
13. The deployment owner can identify database/artifact backup location, key owner, retention period, deletion/export path, provider/subprocessor/region, and privileged-support escalation without copying raw report content into routine operational tickets.

## Common incidents

### Jobs remain queued

Check that the worker container is running, points to the same `DATABASE_URL` and artifact volume, and can acquire the SQLite file. Restart one worker at a time. Do not mark jobs completed manually.

### Jobs remain running after a crash

Confirm through worker ownership and process evidence that no worker still owns the job. Preserve the database and temporary directory for incident evidence. The current release does not automatically requeue running jobs because duplicate model calls can create inconsistent charges and artifacts.

After ownership is cleared, record the stranded job ID and its original idempotency digest, then recreate the request with a newly generated `Idempotency-Key`. Reusing the prior key and payload would correctly replay the existing queued or running job rather than create recovery work. Do not delete or mutate the stranded row until retention, billing, and incident evidence obligations have been satisfied.

### Direct NVIDIA NIM returns 429 or 5xx

Confirm `INTERPRETATION_BACKEND=nvidia_nim`, inspect the bounded job error/trace, verify account quota and model availability, and reduce concurrent workers. Retry only after the service's bounded retries finish. Do not add an undocumented provider fallback. Use `NVIDIA_NIM_API_KEY` exclusively for this path.

### Contextual Orchestrator is unavailable

Confirm `INTERPRETATION_BACKEND=contextual_orchestrator`, gateway DNS/TLS, `/v1/chat/completions`, Bearer token scope, selected orchestrator model, compute mode, route capacity, and downstream worker health. Compare Four Pillars attempts with the gateway request/cost ledger. Do not expose or forward `NVIDIA_NIM_API_KEY` from Four Pillars to the gateway and do not switch to direct NIM under the same job.

### Contextual Orchestrator bypasses routing or conduct

Capture the outbound adapter request with the offline mock contract. It must include `mode=auto`, `route`, or `conduct`, and it must not contain `response_format`, tools, or function-calling keys. The gateway treats those provider-feature fields as single-agent passthrough triggers, so their presence would silently bypass the organization route/conduct path. Four Pillars enforces JSON through explicit prompting, Pydantic validation, and a bounded same-backend repair instead. Protected-main `ContextualOrchestratorClient` currently configures `native_json_mode=False`.

### Contextual Orchestrator rejects structured responses

Confirm that its deployed version accepts OpenAI-compatible messages, `mode`, `attribution`, and `routing`, and that it returns `choices[0].message.content`. Reproduce with the offline adapter contract and the orchestrator's route/conduct tests. Do not restore `response_format` as a workaround because that changes execution to single-agent passthrough.

### Attribution or cost records are incorrect

Expected attribution always includes `service=four-pillars`; account, team, group, and company are optional deployment labels. It must not include subject names, birth data, notes, fingerprints, prompt/generated content, artifact paths, or credentials. Correct configuration or orchestrator ledger logic in a reviewed PR. Do not add sensitive labels to aid debugging.

### Quality failures increase

Compare selected backend, actual model, route, prompt versions, and failed findings. Run deterministic fixtures and the supplementary live judge suite where authorized. Repair prompts, routing, or model configuration in a pull request; never weaken fingerprint, allowed-pillar, medical, coercion, relationship-balance, or event-certainty controls to increase completion rate.

### Calculation boundary regression

Compare the emitted calculation version with `calendar-1.1.0`, the KASI/NAOJ fixture, signed timing deltas, timezone policy, TAI-UTC table, and exact boundary-adjacent failing case. Do not edit the external fixture to make a changed solver pass. Determine whether the solver, fixture transcription, timescale data, supported-policy assumption, or authoritative source changed. Any change capable of moving a user-visible pillar requires a new calculation-evidence version and release-visible review under ADR 0008.

### PDF generation fails

Verify ReportLab, artifact-volume permissions, and CJK CID font registration. Preserve `report.json` to reproduce locally. A PDF failure must not mark the job completed.

### Standards, documentation, or hourly checks fail

Read the single `[hourly-product-loop] release-quality regression` issue and attached logs. Restore missing APA references, traceability mappings, canonical-document contracts, docstrings, coverage, database naming, or build evidence rather than suppressing the gate. A standard revision triggers review; it does not silently change production behavior. A conflict between protected-main code and PRD/TRD/Architecture/ADR/UML/ERD is a repository defect governed by `docs/architecture/DOCUMENTATION_MAP.md`.

### Suspected personal-data exposure

1. Stop the affected secondary propagation path without corrupting authoritative job/artifact state.
2. Identify the purpose, affected job IDs/tenant scope, destinations, time range, provider/log/object-store boundaries, and credentials involved.
3. Do not paste raw birth/context/report content into an incident ticket merely to prove exposure; record object IDs, hashes, bounded metadata, and governed evidence location instead.
4. Revoke or rotate exposed credentials and suspend unsafe integrations.
5. Preserve audit evidence according to incident/legal obligations.
6. Repair authorization, minimum-payload, logging, attribution, retention, storage, or provider configuration through tests and a reviewed PR.
7. Execute required notification/legal/customer procedures through the responsible organization process.

### Privileged content inspection is required

Do not make routine logs less private or introduce a global “unmask” switch. If the deployment has an approved break-glass capability, use its time-bounded actor/reason/job/tenant scope and post-access review. If no such controlled path is implemented, treat raw-content inspection as an explicit security/compliance decision requiring the responsible operator rather than creating ambient engineer access. The target design is documented in `docs/security/DATA_GOVERNANCE.md`; the repository does not claim break-glass is implemented merely because this runbook describes the requirement.

## Backups and recovery

For a single-node deployment, stop the worker briefly or use SQLite's online backup API, then copy the database and completed artifact directories to encrypted storage. Restore both database and matching UUID directories. Manifests permit integrity verification. API keys, NIM keys, and orchestrator tokens come from secret management, not backup archives.

A production backup profile must document encryption/key ownership, backup access, retention, restore testing, and what happens when an authoritative job is deleted before an older backup expires. A restore must not silently resurrect data beyond its governed retention/legal state; this may require a deletion ledger or another externally governed reconciliation mechanism before regulated production use.

A multi-node integration must document transaction guarantees, backup/restore point objectives, object-version recovery, idempotency uniqueness, deterministic history ordering, tenant scope, encryption/KMS ownership, deletion/export semantics, and crash recovery behind the same structural ports.

## Retention, deletion, and export

Default retention is 30 days. `four-pillars cleanup` deletes terminal database rows older than the configured period and their UUID directories. An authenticated DELETE endpoint removes an individual terminal job immediately. Logs and gateway metadata must not retain raw report contents after authorized deletion beyond documented provider obligations.

An enterprise/public-sector profile must additionally define purpose-specific retention, authenticated subject/tenant export, backup deletion semantics, processor retention and proof of partial-failure recovery. These remain readiness gaps until code/deployment evidence exists.

## Security response

1. Revoke exposed API, NIM, orchestrator, GitHub App, or other privileged credentials immediately according to scope.
2. Preserve bounded audit evidence without copying private report payloads into tickets.
3. Identify affected job IDs, model routes, prompts, artifacts, release/commit versions, and time window.
4. Suspend generation while deterministic calculation endpoints remain available when safe.
5. Correct the root cause through realistic tests and a reviewed PR.
6. Re-run Security Scan, Semgrep, the complete offline gate, and authorized hosted smoke tests.
7. Rotate credentials and restore service from an immutable verified release.
8. Run readiness/recovery acceptance and document residual risk and notification obligations.

## Release procedure

1. Update `CHANGELOG.md` for user-visible, integration-visible, security, standards, calculation-policy, persistence/migration, automation-governance, and assurance-readiness changes that actually ship.
2. Run dependency, product-gap, Ruff/docstring, compileall, document, prompt, all offline tests with exactly 100% statement/branch coverage, package, container, Security Scan, and Semgrep gates on the integrated protected-main source.
3. Review the complete diff, issue comments, review submissions, code-scanning findings, and inline threads; a green feature PR does not replace integrated release validation.
4. Merge only the exact head whose required checks/reviews satisfy repository policy.
5. For a releasable change, advance package/runtime/API version together and publish wheel, source distribution, and `SHA256SUMS` through the least-privilege release workflow targeting exact protected-main `GITHUB_SHA`.
6. Verify published artifact names/checksums/source target after release. Do not overwrite an existing version; corrections use a new SemVer.
7. Deploy the immutable release, run readiness, and record calculation, prompt, model, route, artifact, migration and control-plane versions/evidence applicable to the release.
8. Roll back to the previous verified artifact if deterministic fixtures, schema validation, quality pass rate, privacy, authorization, queue/artifact integrity, or output integrity regress.

Mandatory release SBOM, standardized provenance/attestation, artifact-signature verification, and broader protected-main operational acceptance are still supply-chain hardening gaps documented in proposed ADR 0009. Do not claim those controls before they exist.

## Evidence and standards

`docs/standards/REFERENCES.md` contains APA 7th entries for the current engineering standards and peer-reviewed evaluation research. `docs/standards/TRACEABILITY.md` maps them to controls, tests, workflows, and residual gaps. `docs/doctoring/documentation-governance.md` records version-sensitive architecture/privacy/assurance evidence. The mapping supports continual improvement but is not an ISO certification, CSAP certificate, SOC 2 report, legal opinion, or scientific validation of traditional Four Pillars interpretation.
