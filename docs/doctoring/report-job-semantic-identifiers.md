# Report-job semantic identifiers

## Decision

Four Pillars owns the report-job delivery and persistence contract described by the PRD and TRD: a durable report job is queued, claimed, queried, paginated, downloaded, and deleted through the application boundary. Organization-owned Python and SQLite contracts therefore use report-job-specific ubiquitous language rather than generic one-word identifiers.

The authoritative internal/persisted vocabulary is:

| Previous owned name | Specific owned name | Bounded-context meaning |
| --- | --- | --- |
| `ReportJob.id` / DB `id` | `report_job_id` | Opaque report-job identity |
| `ReportJob.status` / DB `status` | `job_status` | Report-job lifecycle state |
| `ReportJob.request` | `report_request` | Validated durable report request |
| `ReportJob.error` / DB `error` | `job_error_message` | Redacted terminal failure message |
| `ReportJobView.artifacts` | `artifact_names` | Allow-listed generated artifact names |
| `ReportJobPageView.items` | `report_jobs` | Redacted report-job summaries in one history page |

`request_json`, `request_fingerprint`, `idempotency_key_digest`, `created_at`, `updated_at`, `artifact_dir`, and `next_cursor` were already semantically specific multiword names and remain unchanged.

## HTTP compatibility / anti-corruption boundary

The established HTTP JSON contract remains unchanged for clients: report-job objects still serialize as `id`, `status`, `error`, and `artifacts`, and history pages still serialize their collection as `items`. Pydantic aliases isolate those compatibility keys at the HTTP adapter while organization-owned Python fields use `report_job_id`, `job_status`, `job_error_message`, `artifact_names`, and `report_jobs`.

`populate_by_name=True` permits internal construction with semantic names. FastAPI continues serializing response models by alias, so the browser studio and external platform integrators do not need a coordinated breaking HTTP migration. Existing API regressions deliberately keep asserting the compatibility wire keys.

The browser JavaScript continues to read `job.id`, `job.status`, `job.error`, and `job.artifacts` because those names belong to the stable HTTP compatibility representation, not to the internal Python/domain contract.

## Persistence migration

The `report_jobs` table remains the single normalized durable report-job aggregate. On startup, `JobStore._initialize()` already acquires the repository's migration lock with `BEGIN IMMEDIATE`; the naming migration runs inside that same transaction and performs static SQLite column renames when legacy columns are present:

- `id` → `report_job_id`
- `status` → `job_status`
- `error` → `job_error_message`

The migration then preserves/backfills `request_fingerprint` and `idempotency_key_digest` exactly as before, drops the obsolete generic index names, and creates semantically specific equivalents:

- `idx_report_jobs_job_status_created_at`
- `idx_report_jobs_created_at_job_id`
- `idx_report_jobs_job_status_created_at_job_id`
- `idx_report_jobs_idempotency_key_digest` remains unchanged because it was already specific.

No row is copied into a second table, no new entity or duplicated dependency is introduced, and 3NF is unchanged. The queue remains single-node SQLite WAL with the same `BEGIN IMMEDIATE` claim/idempotency serialization, so hot-partition shape, writer-lock scope, read/write separation, UPSERT/idempotency behavior, retention semantics, and artifact addressing remain materially unchanged. Keyset pagination remains ordered by the same values, now expressed as `(created_at DESC, report_job_id DESC)`.

### Compatibility and rollback safety

The HTTP contract is backward compatible; the persisted SQLite schema intentionally advances. A binary downgrade to a version that still queries `id`, `status`, and `error` is not safe against a migrated database without an explicit reverse migration. Operational rollback must therefore either restore the pre-migration database backup/snapshot or rename `report_job_id`, `job_status`, and `job_error_message` back before starting an older binary. Forward startup is idempotent because renames are conditional on the legacy column existing and the semantic column being absent.

## Verification

The change follows TDD in two layers:

1. `tests/test_api_naming_contract.py` was committed before the API production rename and requires semantic Pydantic field names while pinning legacy JSON aliases.
2. `tests/test_report_job_naming_migration.py` was committed before the domain/SQLite repair and requires semantic `ReportJob` fields, legacy-row preservation, semantic persisted columns and indexes, and removal of generic persisted names.

Existing API tests continue to assert the old wire keys, while lifecycle, history, idempotency, service, hardening, modular-port, and coverage tests consume the semantic domain/storage names. The exact-head verifier must run the focused naming/migration tests and the repository's required full suite, 100% statement/branch coverage, Ruff/docstring checks, package/container validation, Security Scan, Semgrep, and independent review gates before merge.

## DDD traceability

- **Bounded context:** Report Job Delivery and History.
- **Aggregate:** `ReportJob` durable job state.
- **Views:** `ReportJobView`; page view `ReportJobPageView`.
- **Repository:** `ReportJobRepository` / SQLite `JobStore` implementation.
- **Ubiquitous language:** report job, report job identity, job status, report request, job error message, artifact name, report history page, continuation cursor.
- **Invariant:** history responses remain privacy-redacted and contain no birth input, subject label, stored request, model text, trace, credential, or artifact path.
- **Invariant:** deterministic calculation and interpretation backends are unaffected by delivery/persistence naming.
- **Invariant:** generic compatibility keys exist only at the HTTP serialization boundary, not as organization-owned Python fields or persisted SQLite columns.
- **Invariant:** migration preserves every existing report row and the identity/status/error semantics used by queue transitions, idempotent creation, history pagination, deletion, and purge.

## Product and standards traceability

The rationale follows `docs/product/PRD.md` sections 3 and 4.5 (recoverable report jobs, authenticated redacted history, stable backward-compatible collection contract) and `docs/technical/TRD.md` sections 3.5, 4, 7, and 8 (delivery ownership, keyset history, durable job state, privacy-redacted response contract). Existing standards and research references remain authoritative in `docs/standards/REFERENCES.md` and `docs/standards/TRACEABILITY.md`; this rename does not change the scientific model or introduce a new external standards claim.
