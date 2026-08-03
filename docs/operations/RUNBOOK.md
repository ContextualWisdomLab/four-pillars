# Operations Runbook

## Start and stop

Create `.env` from `.env.example`, set secrets outside source control, and run `docker compose up -d --build`. The API listens on port 8000 and the worker shares the `artifacts` volume. Stop with `docker compose down`; add `-v` only when the operator intentionally deletes the SQLite database and all artifacts.

## Readiness checklist

1. `GET /health` returns `ok` and the expected version.
2. `GET /ready` returns `ready` and produces no permission error.
3. A golden chart request returns the committed pillar fixture and a fingerprint.
4. A queued report changes to running when the worker is available.
5. A NIM-enabled smoke job completes and its manifest hashes match the files.
6. PDF text can be selected and Korean glyphs display correctly.
7. API authentication rejects an incorrect key when enabled.

## Common incidents

### Jobs remain queued

Check that the worker container is running, points to the same `DATABASE_URL` and artifact volume, and can acquire the SQLite file. Restart one worker at a time. Do not mark jobs completed manually.

### Jobs remain running after a crash

Confirm that no worker owns the job. Preserve the database and temporary directory for evidence. The current release does not automatically requeue running jobs because duplicate hosted NIM calls can create inconsistent charges and artifacts. Operators may recreate the request as a new job after recording the incident.

### NIM returns 429 or 5xx

Inspect `traces.json` or job error for attempt count, verify account quota and model availability, and reduce concurrent workers. Retry only after the service's bounded retries finish. Do not add an undocumented provider fallback.

### Quality failures increase

Compare the model, prompt versions, and failed findings. Run offline fixtures and the live judge suite against the candidate model. Repair prompts or model configuration in a pull request; never weaken deterministic fingerprint checks to increase completion rate.

### PDF generation fails

Verify ReportLab is installed, the artifact volume is writable, and CJK CID font registration succeeds. Preserve `report.json` to reproduce locally. A PDF failure must not mark the job completed.

## Backups and recovery

For a single-node deployment, stop the worker briefly or use SQLite's online backup API, then copy the database and completed artifact directories to encrypted storage. Restore both the database and matching UUID directories. Manifests allow file-integrity verification after restore. NIM keys and API-key digests are restored from secret management, not backup archives.

## Retention and deletion

The default retention is 30 days. `four-pillars cleanup` deletes terminal database rows older than the configured period and their UUID directories. An authenticated DELETE endpoint removes an individual terminal job immediately. Logs must not retain raw report contents after artifacts are deleted.

## Release procedure

Run document/prompt validation, Ruff, compileall, offline tests with coverage, and package build. Review the PR, inspect CI and NIM evaluation when applicable, merge, deploy the immutable commit, run readiness checks, and record model/prompt/calculation versions. Roll back to the previous image if calculation fixtures, schema validation, quality pass rate, or output integrity regress.
