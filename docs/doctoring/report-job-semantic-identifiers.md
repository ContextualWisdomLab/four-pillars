# Report-job semantic identifiers

## Decision

Four Pillars owns the report-job delivery contract described by the PRD and TRD: a durable report job is queued, queried, paginated, downloaded, and deleted through the FastAPI delivery boundary. The Python/Pydantic model must therefore use report-job-specific ubiquitous language rather than generic one-word field names.

The internal contract changes are:

| Previous owned name | Specific owned name | Bounded-context meaning |
| --- | --- | --- |
| `id` | `report_job_id` | Opaque report-job identity |
| `status` | `job_status` | Report-job lifecycle state |
| `error` | `job_error_message` | Redacted terminal failure message |
| `artifacts` | `artifact_names` | Allow-listed generated artifact names |
| `items` | `report_jobs` | Redacted report-job summaries in one history page |

`created_at`, `updated_at`, and `next_cursor` are already semantically specific multiword names and remain unchanged.

## Compatibility / anti-corruption boundary

The established HTTP JSON contract remains unchanged for clients: report-job objects still serialize as `id`, `status`, `error`, and `artifacts`, and history pages still serialize their collection as `items`. Pydantic aliases isolate those compatibility keys at the HTTP adapter while organization-owned Python fields use `report_job_id`, `job_status`, `job_error_message`, `artifact_names`, and `report_jobs`.

`populate_by_name=True` permits internal construction with semantic names. FastAPI continues serializing response models by alias, so the browser studio and external platform integrators do not need a coordinated breaking migration. Legacy JSON payloads also remain valid inputs to the Pydantic compatibility boundary.

## Persistence and database impact

No SQLite table, column, index, constraint, cursor encoding, UPSERT/idempotency path, transaction, lock, artifact path, or retention rule changes. The durable job repository continues to own its existing schema and atomic `BEGIN IMMEDIATE` behavior. This repair is limited to the application delivery model and does not introduce a database migration or rollback requirement.

## Verification

`tests/test_api_naming_contract.py` is the regression contract. Its first commit precedes the production rename and requires the new semantic Pydantic field names while pinning the established JSON aliases. Existing API tests continue to assert the old wire keys, so both the internal naming invariant and backward-compatible external shape must pass together.

The exact-head verifier must run the focused naming/API tests and the repository's required full suite, 100% statement/branch coverage, Ruff/docstring checks, package/container validation, Security Scan, Semgrep, and review gates before merge.

## DDD traceability

- **Bounded context:** Report Job Delivery and History.
- **Aggregate/view:** `ReportJobView`; page aggregate `ReportJobPageView`.
- **Ubiquitous language:** report job, job status, artifact name, report history page, continuation cursor.
- **Invariant:** history responses remain privacy-redacted and contain no birth input, subject label, stored request, model text, trace, credential, or artifact path.
- **Invariant:** deterministic calculation and interpretation backends are unaffected by delivery-model naming.
- **Invariant:** generic compatibility keys exist only at the HTTP serialization boundary, not as organization-owned Python field names.

## Product and standards traceability

The rationale follows `docs/product/PRD.md` sections 3 and 4.5 (recoverable report jobs, authenticated redacted history, stable backward-compatible collection contract) and `docs/technical/TRD.md` sections 3.5, 4, 7, and 8 (delivery ownership, keyset history, durable job state, privacy-redacted response contract). Existing standards and research references remain authoritative in `docs/standards/REFERENCES.md` and `docs/standards/TRACEABILITY.md`; this rename does not introduce a new scientific, security, or persistence claim requiring a new external reference.
