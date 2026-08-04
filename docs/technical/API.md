# API Reference

## Authentication

When `API_KEY_SHA256` is empty, development requests are accepted without a key. In production, store the lowercase SHA-256 digest of an API key and send the original key in `X-API-Key`. The service compares digests in constant time. Health and readiness endpoints remain unauthenticated for infrastructure probes.

The browser studio never writes the API key to `localStorage`, `sessionStorage`, cookies, or report requests. It keeps the value only in the current page memory and sends it through the request header.

## Browser studio

`GET /` serves an accessible responsive workflow that separates calculation review from AI generation. The user enters birth information, reviews the deterministic pillars, adjacent solar-term boundary and fingerprint, and then explicitly submits the same input for report generation. The page polls the redacted job endpoint and renders only artifact filenames supplied by the server.

The studio generates one UUID idempotency key when report enqueueing starts. A network failure keeps that key in page memory for the retry; a successful HTTP 202 response clears it. Changing any reviewed report input invalidates both the reviewed chart and the pending key. The key is never persisted by the browser.

## Calculation endpoints

`POST /v1/chart` accepts a `BirthInput` object with local ISO `birth`, IANA `timezone`, `gender`, `calendar`, `lunar_leap_month`, `birth_time_known`, optional `longitude`, `time_basis`, and `day_boundary`. It returns the normalized moment, four pillars, day master, element balance, interactions, adjacent solar terms, warnings, policy version, and fingerprint.

`POST /v1/luck/daewoon` accepts the same `BirthInput` and returns one direction scenario when gender is known or two scenarios when gender is unspecified.

`POST /v1/luck/annual` accepts `{ "birth": BirthInput, "year": 2026, "month": 1 }` and returns the Li-Chun-bounded annual snapshot. `month` is ignored by this endpoint.

`POST /v1/luck/monthly` accepts the same envelope and returns the requested Gregorian month's `jie`-bounded snapshot. A January `jie` month occurs before Li Chun and therefore uses the previous sexagenary year's stem when deriving the month pillar.

## Report jobs

`POST /v1/reports` validates a report request and returns HTTP 202 with a queued job. The body contains `subject_name`, `birth`, `annual_year`, `monthly_year`, `monthly_month`, and optional `user_context`. The request is durable before NIM is called.

`POST /v1/reports` and `GET /v1/reports/{job_id}` return only the job ID, public status, timestamps, bounded error text, and available artifact filenames. They never echo birth data, context notes, the stored request, or an internal artifact path.

A separate worker started with `four-pillars worker` claims jobs. This avoids tying long NIM calls to an HTTP request and allows the API to restart independently.

### Idempotent report creation

Clients may send an optional `Idempotency-Key` header when calling `POST /v1/reports`. The experimental contract follows `draft-ietf-httpapi-idempotency-key-header-07`: the field is an RFC 8941 **structured string**, not an unquoted token. The decoded value must contain 8 through 128 printable ASCII characters; only `\"` and `\\` string escapes are accepted. A quoted UUID is recommended, for example:

```http
Idempotency-Key: "8e03978e-40d5-43e8-bc93-6894a57f9324"
```

The service canonicalizes the validated JSON request with sorted object keys and compact separators, then computes a SHA-256 request fingerprint. It decodes the structured string and stores only its SHA-256 digest, never the raw client key.

The first key-and-fingerprint pair creates a durable queued job. Repeating the same key with the same payload returns HTTP 202 and the **same job**, including while that asynchronous job is queued or running. The `Idempotency-Replayed` response header is `false` for the first enqueue and `true` for a replay. Durable job creation is the completed HTTP operation; report generation remains a separately observable worker lifecycle.

A malformed field returns HTTP 400. Reusing the key with a different request fingerprint returns **HTTP 422** and does not create another job. Omitting the header preserves legacy behavior and creates a distinct job for each request.

The idempotency record has the same lifecycle as its report job. It remains replayable across process restarts, and it expires only when the terminal job is **deleted or purged** under the configured retention policy. Deleting or purging the row removes the stored key digest and permits a future request to use that value again. Multi-node repository adapters must enforce the key lookup, fingerprint comparison, and first insert atomically with a unique database constraint.

## Artifacts

`GET /v1/reports/{job_id}/artifacts/{filename}` accepts only `chart.json`, `daewoon.json`, `annual.json`, `monthly.json`, `report.json`, `traces.json`, `manifest.json`, `report.html`, or `report.pdf`. The optional `download=false` omits the attachment filename. Any path traversal or unknown name returns 404.

The service resolves the database path and requires it to be the direct UUID child for that job under the configured artifact root. A tampered database row cannot redirect file reads or deletes outside the configured root.

`DELETE /v1/reports/{job_id}` removes artifacts and the database row only when the job is terminal. Running and queued jobs return 409.

## Operations

- `GET /health` proves the API process is alive.
- `GET /ready` proves the artifact directory is writable and SQLite is readable.
- Interactive OpenAPI is available at `/docs`.

## Error behavior

Pydantic validation returns HTTP 422. Missing resources return 404. Authentication failures return 401. Non-terminal deletion returns 409. A malformed `Idempotency-Key` returns 400, and reuse for a different payload returns 422. Calculation policy errors are returned synchronously by calculation endpoints; report-generation failures are stored on the job. NIM content that remains schema-invalid after the bounded repair becomes a failed job. Report copy that remains unsafe or contains a sexagenary pillar absent from the deterministic evidence after editorial repair becomes `quality_failed` and is not published as a completed PDF.

## Example

```bash
curl -sS http://localhost:8000/v1/chart \
  -H 'Content-Type: application/json' \
  -d '{
    "birth":"1990-06-15T08:30:00",
    "timezone":"Asia/Seoul",
    "gender":"female",
    "calendar":"solar",
    "birth_time_known":true,
    "time_basis":"civil",
    "day_boundary":"midnight"
  }'
```
