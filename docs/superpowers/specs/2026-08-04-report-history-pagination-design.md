# Report History Pagination Design

## Goal

Add a privacy-safe, deterministic collection API for recent report jobs so consultants, operators, and platform integrations can recover work without retaining every job UUID outside the service.

## Product gap

The service currently supports report creation and direct lookup by UUID, but it cannot enumerate recent jobs. A browser refresh, a lost client-side identifier, an operational handoff, or an integration restart therefore makes otherwise durable work difficult to discover. The missing collection boundary is a material usability and operability gap even though the queue itself is durable.

## Scope

This change adds `GET /v1/reports` with keyset pagination and an optional lifecycle-status filter. It returns only the existing redacted public job view and never returns the stored report request, birth information, user context, idempotency-key digest, request fingerprint, or artifact directory.

Browser history presentation, subject-name search, full-text search, total counts, multi-tenant authorization, and cross-service aggregation are deliberately out of scope for this increment. They require separate product and privacy designs.

## HTTP contract

The collection endpoint accepts:

- `limit`: integer, default `20`, minimum `1`, maximum `100`;
- `cursor`: optional opaque continuation token returned by the previous page; and
- `status`: optional `JobStatus` value.

The response shape is:

```json
{
  "items": [
    {
      "id": "6f3b0be2-e9d6-46b5-b54f-787ef9ea3e7b",
      "status": "completed",
      "created_at": "2026-08-04T05:00:00Z",
      "updated_at": "2026-08-04T05:02:00Z",
      "error": null,
      "artifacts": ["report.html", "report.pdf"]
    }
  ],
  "next_cursor": "v1.eyJjcmVhdGVkX2F0IjoiLi4uIiwiam9iX2lkIjoiLi4uIn0"
}
```

Items are ordered by `(created_at DESC, id DESC)`. The UUID is the deterministic tie-breaker, so rows created at the same timestamp do not repeat or disappear between pages. The endpoint fetches `limit + 1` rows and emits a continuation token only when another page exists.

## Cursor format

The cursor is versioned as `v1.` followed by unpadded RFC 4648 base64url encoding of compact UTF-8 JSON containing:

```json
{"created_at":"RFC 3339 UTC timestamp","job_id":"UUID"}
```

The token is opaque to clients but is not an authorization credential and is not encrypted or signed. Decoding is strict: unknown versions, malformed base64url, invalid JSON, extra fields, non-UTC timestamps, or invalid UUIDs return HTTP 400. The token contains no personal data.

## Architecture

`ReportJobRepository` remains unchanged. A separate runtime-checkable `ReportJobHistoryRepository` capability exposes:

```python
def list_jobs(
    self,
    *,
    limit: int,
    cursor: str | None = None,
    status: JobStatus | None = None,
) -> tuple[list[ReportJob], str | None]:
    ...
```

`JobStore` implements both the original repository and the optional history capability. Existing organization adapters remain valid for report creation, lookup, processing, retention, and deletion. When a history request reaches an adapter without the optional capability, the application returns HTTP 501 rather than silently maintaining process-local history.

Cursor encoding and decoding live in a focused `history.py` module. The SQLite adapter owns the keyset query and uses two named indexes:

- `idx_report_jobs_created_id` on `(created_at DESC, id DESC)`; and
- `idx_report_jobs_status_created_id` on `(status, created_at DESC, id DESC)`.

Every database object name contains at least two words and uses `snake_case`.

## Data flow

1. FastAPI validates `limit` and the optional `JobStatus` query value.
2. `ReportService.list_jobs` verifies the optional history capability.
3. `JobStore.list_jobs` decodes the cursor, runs one indexed keyset query, and returns internal `ReportJob` objects plus a continuation token.
4. The delivery layer maps each internal job through the existing redacted `ReportJobView` conversion.
5. Completed jobs expose only allow-listed artifacts that still exist under the configured UUID directory.

## Error handling

- Invalid `limit` or `status` uses FastAPI/Pydantic HTTP 422 validation.
- Malformed or unsupported cursor input returns HTTP 400 with a stable generic detail.
- A repository without `ReportJobHistoryRepository` returns HTTP 501.
- An empty page returns `items=[]` and `next_cursor=null`.
- Concurrent inserts may appear on a future first-page request but do not invalidate an already-issued continuation sequence.
- Deleted or retention-purged rows naturally disappear from subsequent pages.

## Security and privacy

The collection response reuses the existing public job view and is protected by the same optional API-key dependency as other report endpoints. The cursor contains only a UTC timestamp and random UUID. Raw birth input, subject name, user context, generated copy, model traces, request fingerprints, and idempotency material remain outside the response and cursor.

## Testing and release gates

Tests must prove stable newest-first ordering, tie-breaking, multi-page traversal without duplicates, status filtering, empty pages, malformed-cursor rejection, privacy redaction, optional-adapter behavior, authenticated access, and compliant database index names. Public APIs receive complete docstrings. Statement and branch coverage remain exactly 100 percent, and the full Python 3.11/3.12, packaging, container, security, and SAST gates must pass on the exact merge candidate.
