# Public Report Job Status Schema

**Maturity:** `active_pr`; promote only after exact protected-main integration and required operational evidence.  
**Canonical implementation model:** `four_pillars.api.ReportJobView`.

This document is the single documentation contract for fields exposed by `GET /v1/reports`, `GET /v1/reports/{job_id}`, and the corresponding browser history/status UI. It intentionally differs from the internal `ReportJob`, which contains confidential request/provenance fields.

## Allowed fields

| Field | Type | Public rule |
|---|---|---|
| `id` | string | opaque random job identifier; no personal meaning |
| `status` | enum | exactly `queued`, `running`, `completed`, `failed`, `quality_failed` |
| `created_at` | RFC 3339 datetime | lifecycle metadata only |
| `updated_at` | RFC 3339 datetime | lifecycle metadata only |
| `error` | string/null | stable non-sensitive public failure message; maximum 4,000 characters; non-null only for `failed`/`quality_failed` |
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
- provider response bodies or internal exception strings;
- internal artifact directory/path;
- API/model/database credentials.

A user who is authorized to download a completed artifact receives report/calculation content through the artifact endpoint, not by expanding the history/status schema.

## Error contract

The built-in `JobStore` may retain a bounded private diagnostic for operator/recovery purposes. `ReportJobView` does **not** echo that stored string.

The public projection maps terminal states to stable messages:

```text
failed         -> Report generation failed.
quality_failed -> Report quality validation failed.
all other states -> null
```

This prevents a provider exception, prompt/model content, personal context, credential-looking text, or internal path from becoming a public status/history disclosure. The public field retains the 4,000-character schema ceiling as a defensive compatibility bound, but current built-in messages are intentionally much shorter.

Detailed diagnostics belong only in separately authorized operational evidence with minimum-necessary access and retention. An injected MSA repository may store richer private diagnostics, but the API projection remains the same stable public contract.

## Lifecycle behavior

- `queued`: accepted and durably pending. `artifacts=[]`, `error=null`.
- `running`: claimed by a worker. `artifacts=[]`, `error=null`.
- `completed`: complete quality-approved artifact publication succeeded. `error=null`; allow-listed existing artifacts may be returned.
- `failed`: terminal operational/provider/calculation/rendering failure. `artifacts=[]`; public error is `Report generation failed.`.
- `quality_failed`: terminal deterministic/editorial quality failure after bounded repair. `artifacts=[]`; public error is `Report quality validation failed.`.

A future lifecycle state or public error-code/message taxonomy is a public API change and requires synchronized model, API, history/filter UI, data-model, threat/privacy model, operability, tests, PRD/TRD and changelog review.

## Collection and cursor privacy

`GET /v1/reports` returns only a list of this public model plus `next_cursor`. The cursor contains only a version, UTC creation timestamp and opaque job UUID. It must not embed error text, status, request/provenance data, subject context, or storage paths.

## Artifacts

Only server-defined artifact names are exposed. Artifact lists are derived from the configured trusted UUID directory/object prefix and do not accept arbitrary stored path values. A missing/untrusted directory yields no public artifact filename.

## Tests

Contract tests should prove:

- serialization contains only the fields above;
- stored private request/fingerprint/idempotency/artifact-path data never enters status/history responses;
- stored provider/prompt/personal/credential-shaped failure text does not enter `ReportJobView.error`;
- non-failure states expose `error=null` even if an injected/internal model object contains unexpected diagnostic text;
- errors over 4,000 characters cannot satisfy the public model if a future adapter bypasses the built-in stable projection;
- completed artifact lists are allow-listed and path-bound;
- non-completed jobs expose no artifacts;
- lifecycle filters accept only the documented `JobStatus` values;
- cursors cannot carry confidential metadata.
