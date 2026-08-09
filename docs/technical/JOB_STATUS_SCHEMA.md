# Public Report Job Status Schema

**Maturity:** `implemented_on_protected_main` for the API model and standalone lifecycle.  
**Canonical implementation model:** `four_pillars.api.ReportJobView`.

This document is the single documentation contract for fields exposed by `GET /v1/reports`, `GET /v1/reports/{job_id}`, and the corresponding browser history/status UI. It intentionally differs from the internal `ReportJob`, which contains confidential request/provenance fields.

## Allowed fields

| Field | Type | Public rule |
|---|---|---|
| `id` | string | opaque random job identifier; no personal meaning |
| `status` | enum | exactly `queued`, `running`, `completed`, `failed`, `quality_failed` |
| `created_at` | RFC 3339 datetime | lifecycle metadata only |
| `updated_at` | RFC 3339 datetime | lifecycle metadata only |
| `error` | string/null | bounded sanitized operational failure text; maximum 4,000 characters; expected non-null only for `failed`/`quality_failed` |
| `artifacts` | string[] | server allow-listed filenames; populated only for `completed` jobs when the files safely exist |

No other internal job fields may be serialized through this public model.

## Explicitly forbidden fields

The public status/history contract must never contain:

- `request_json` or the internal `request` object;
- subject name, birth date/time/timezone, location-derived context, or user notes;
- request fingerprint;
- idempotency key or idempotency-key digest;
- calculation fingerprint merely for status/history correlation;
- raw prompt or model response;
- generated report prose;
- raw/private model trace payloads;
- internal artifact directory/path;
- API/model/database credentials.

A user who is authorized to download a completed artifact receives report/calculation content through the artifact endpoint, not by expanding the history/status schema.

## Error contract

The built-in `JobStore.fail()` limits stored error text to 4,000 characters and `ReportJobView.error` enforces the same maximum at the public boundary. An injected MSA repository must therefore supply an error value that satisfies this contract.

Errors are operational diagnostics, not a channel for request or model content. Implementations should classify failures and avoid constructing errors from raw personal context, prompts, provider bodies, credentials, or internal file paths. The browser may display a shorter presentation-safe prefix, but that presentation limit does not expand the API contract.

## Lifecycle behavior

- `queued`: accepted and durably pending. `artifacts=[]`, `error=null`.
- `running`: claimed by a worker. `artifacts=[]`, `error=null`.
- `completed`: complete quality-approved artifact publication succeeded. `error=null`; allow-listed existing artifacts may be returned.
- `failed`: terminal operational/provider/calculation/rendering failure. `artifacts=[]`; bounded `error` may be returned.
- `quality_failed`: terminal deterministic/editorial quality failure after bounded repair. `artifacts=[]`; bounded `error` may be returned.

A future lifecycle state is a public API change and requires synchronized model, API, history/filter UI, data-model, operability, tests, PRD/TRD and changelog review.

## Collection and cursor privacy

`GET /v1/reports` returns only a list of this public model plus `next_cursor`. The cursor contains only a version, UTC creation timestamp and opaque job UUID. It must not embed error text, status, request/provenance data, subject context, or storage paths.

## Artifacts

Only server-defined artifact names are exposed. Artifact lists are derived from the configured trusted UUID directory/object prefix and do not accept arbitrary stored path values. A missing/untrusted directory yields no public artifact filename.

## Tests

Contract tests should prove:

- serialization contains only the fields above;
- stored private request/fingerprint/idempotency/artifact-path data never enters status/history responses;
- errors over 4,000 characters fail the public model or are bounded before it;
- completed artifact lists are allow-listed and path-bound;
- non-completed jobs expose no artifacts;
- lifecycle filters accept only the documented `JobStatus` values;
- cursors cannot carry confidential metadata.
