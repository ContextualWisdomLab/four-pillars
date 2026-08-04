# API Reference

## Authentication

When `API_KEY_SHA256` is empty, development requests are accepted without a key. In production, store the lowercase SHA-256 digest of an API key and send the original key in `X-API-Key`. The service compares digests in constant time. Health and readiness endpoints remain unauthenticated for infrastructure probes.

The browser studio never writes the API key to `localStorage`, `sessionStorage`, cookies, or report requests. It keeps the value only in current page memory and sends it through the request header. Calculation, history, polling, and artifact downloads reuse that in-memory header. The browser fetches an artifact as a same-origin blob before initiating the local download, so protected deployments do not place credentials in a URL.

## Browser studio

`GET /` serves an accessible responsive workflow that separates calculation review from AI generation. The user enters birth information, reviews deterministic pillars, the adjacent solar-term boundary and fingerprint, and then explicitly submits the same input for report generation. The page polls the redacted job endpoint and renders only artifact filenames supplied by the server.

The studio generates one UUID idempotency key when report enqueueing starts. A network failure keeps that key in page memory for retry; a successful HTTP 202 response clears it. Changing any reviewed report input invalidates the reviewed chart and pending key. The key is never persisted by the browser.

A third browser section displays the newest 20 redacted report jobs. It supports exact lifecycle-status filtering, first-page refresh, and cursor-based loading of older pages. Queued and running rows can restore the current-job panel and resume polling. Completed rows expose only server-supplied allow-listed artifact actions. Failed rows display bounded public error text. A newly enqueued or newly terminal job refreshes the first page so it remains recoverable after current page state is lost.

History status changes are announced through a dedicated polite live region. Status remains visible as text rather than color alone. API-derived strings are inserted through `textContent` and created DOM nodes, never interpreted as markup. Every history request carries a sequence number; an older response that completes after a newer filter, credential, refresh, or enqueue request is ignored. The browser follows reduced-motion preferences when moving focus back to the current-job area.

The editable product-design source is the Figma file `Four Pillars — Report History Studio`, desktop node `2:3` and mobile node `2:136`. The implementation extends the existing browser visual system and keeps the collection in one full-width panel beneath the calculation workflow.

## Calculation endpoints

`POST /v1/chart` accepts a `BirthInput` object with local ISO `birth`, IANA `timezone`, `gender`, `calendar`, `lunar_leap_month`, `birth_time_known`, optional `longitude`, `time_basis`, and `day_boundary`. It returns the normalized moment, four pillars, day master, element balance, interactions, adjacent solar terms, warnings, policy version, and fingerprint.

`POST /v1/luck/daewoon` accepts the same `BirthInput` and returns one direction scenario when gender is known or two scenarios when gender is unspecified.

`POST /v1/luck/annual` accepts `{ "birth": BirthInput, "year": 2026, "month": 1 }` and returns the Li-Chun-bounded annual snapshot. `month` is ignored by this endpoint.

`POST /v1/luck/monthly` accepts the same envelope and returns the requested Gregorian month's `jie`-bounded snapshot. A January `jie` month occurs before Li Chun and therefore uses the previous sexagenary year's stem when deriving the month pillar.

## Interpretation backend

Report-generation endpoints and job schemas do not change with the selected interpretation backend. The worker reads `INTERPRETATION_BACKEND` when the service is composed:

- `nvidia_nim` is the standalone default and authenticates direct model calls with `NVIDIA_NIM_API_KEY`.
- `contextual_orchestrator` calls an approved OpenAI-compatible gateway and authenticates with `CONTEXTUAL_ORCHESTRATOR_TOKEN`.

The selection applies only when no custom `ReportInterpreter` is injected. Missing credentials or backend failures are stored as ordinary job failures. The service never silently switches adapters.

Both built-in clients send schema-oriented chat-completions requests and require a Pydantic-valid JSON object. Contextual Orchestrator requests also include prompt-safe organizational attribution and synchronous routing metadata. Attribution never contains names, birth information, user notes, fingerprints, prompts, generated text, artifacts, or credentials.

The public API does not return provider administration details or the raw model response. Completed artifact metadata records the actual model, prompt versions, prompt hashes, attempts, repairs, and calculation fingerprint.

## Report jobs

`POST /v1/reports` validates a report request and returns HTTP 202 with a queued job. The body contains `subject_name`, `birth`, `annual_year`, `monthly_year`, `monthly_month`, and optional `user_context`. The request is durable before any model backend is called.

`POST /v1/reports`, `GET /v1/reports`, and `GET /v1/reports/{job_id}` return only job identifiers, public status, timestamps, bounded error text, and available artifact filenames. They never echo birth data, subject labels, context notes, stored requests, request fingerprints, idempotency material, generated report text, model traces, or internal artifact paths.

A separate worker started with `four-pillars worker` claims jobs. This avoids tying long model calls to an HTTP request and allows the API to restart independently.

### Idempotent report creation

Clients may send an optional `Idempotency-Key` header when calling `POST /v1/reports`. The experimental contract follows `draft-ietf-httpapi-idempotency-key-header-07`: the field is an RFC 8941 **structured string**, not an unquoted token. The decoded value must contain 8 through 128 printable ASCII characters; only `\"` and `\\` string escapes are accepted. A quoted UUID is recommended, for example:

```http
Idempotency-Key: "8e03978e-40d5-43e8-bc93-6894a57f9324"
```

The service canonicalizes the validated JSON request with sorted object keys and compact separators, computes a SHA-256 request fingerprint, decodes the structured string, and stores only its SHA-256 digest, never the raw client key.

The first key-and-fingerprint pair creates a durable queued job. Repeating the same key with the same payload returns HTTP 202 and the **same job**, including while that asynchronous job is queued or running. The `Idempotency-Replayed` response header is `false` for the first enqueue and `true` for a replay. Durable job creation is the completed HTTP operation; report generation remains a separately observable worker lifecycle.

A malformed field returns HTTP 400. Reusing the key with a different request fingerprint returns **HTTP 422** and does not create another job. Omitting the header preserves legacy behavior and creates a distinct job for each request.

The idempotency record has the same lifecycle as its report job. It remains replayable across process restarts and expires only when the terminal job is deleted or purged under the configured retention policy. Deleting or purging the row removes the stored key digest and permits future reuse. Multi-node repository adapters must enforce key lookup, fingerprint comparison, and first insert atomically with a unique database constraint.

Idempotency is an optional repository capability, so existing custom adapters remain compatible with normal report creation. An injected adapter that implements only `ReportJobRepository` continues to serve requests without the header. If a keyed request reaches an adapter that does not also implement `IdempotentReportJobRepository`, the API returns HTTP 501 rather than emulating unsafe process-local atomicity.

### Report history

`GET /v1/reports` returns a privacy-safe newest-first page of report jobs. It accepts:

- `limit`, default `20`, with a minimum of `1` and maximum of `100`;
- optional `status`, which must be one of the public `JobStatus` values; and
- optional `cursor`, which must be the opaque continuation token from the preceding response.

The response contains `items` and `next_cursor`. Each item has exactly the same redacted shape as `GET /v1/reports/{job_id}`. `next_cursor` is `null` when no later page exists.

Rows are ordered by `(created_at DESC, id DESC)`. The UUID is a deterministic tie-breaker for jobs created at the same timestamp. Pagination uses a keyset boundary rather than a numeric offset, so a continuation sequence does not repeat or skip its existing rows when new jobs are inserted. A new job created after the first page appears on a future first-page request, not inside an already-issued continuation sequence. Deleted and retention-purged rows naturally disappear.

The cursor is `v1.` followed by unpadded RFC 4648 base64url encoding of compact JSON containing only a UTC RFC 3339 timestamp and random job UUID. It is neither an authorization credential nor an encrypted token. Unknown versions, malformed base64url, invalid JSON, extra fields, non-UTC timestamps, and invalid UUIDs return HTTP 400. The same optional API-key authentication used by other report endpoints protects the collection.

History traversal is a separate optional repository capability. Existing adapters that implement only `ReportJobRepository` remain compatible with creation, lookup, processing, retention, and deletion. A history request against an adapter without `ReportJobHistoryRepository` returns HTTP 501 instead of maintaining unsafe process-local state.

## Artifacts

`GET /v1/reports/{job_id}/artifacts/{filename}` accepts only `chart.json`, `daewoon.json`, `annual.json`, `monthly.json`, `report.json`, `traces.json`, `manifest.json`, `report.html`, or `report.pdf`. The optional `download=false` omits the attachment filename. Any path traversal or unknown name returns 404.

The service resolves the database path and requires it to be the direct UUID child for that job under the configured artifact root. A tampered database row cannot redirect file reads or deletes outside the configured root.

`DELETE /v1/reports/{job_id}` removes artifacts and the database row only when the job is terminal. Running and queued jobs return 409.

## Operations

- `GET /health` proves the API process is alive.
- `GET /ready` proves the artifact directory is writable and SQLite is readable.
- Interactive OpenAPI is available at `/docs`.

## Error behavior

Pydantic validation returns HTTP 422. Missing resources return 404. Authentication failures return 401. Non-terminal deletion returns 409. A malformed `Idempotency-Key` returns 400, reuse for a different payload returns 422, and a keyed request against a legacy repository adapter without the optional capability returns 501. A malformed report-history cursor returns 400, invalid history limits or statuses return 422, and a history request against a legacy repository without `ReportJobHistoryRepository` returns 501.

Calculation policy errors are returned synchronously by calculation endpoints. Report-generation failures are stored on the job. Selected-backend transport, authentication, rate-limit, response-shape, and schema failures become failed jobs without implicit fallback. Report copy that remains unsafe or contains a sexagenary pillar absent from deterministic evidence after editorial repair becomes `quality_failed` and is not published as a completed PDF.

The browser maps collection HTTP 401 to an API-key prompt and HTTP 501 to an unsupported-repository message. Other bounded API details are rendered as plain text in the history live region. A collection error never exposes hidden request fields or clears successfully loaded rows unless it occurred while resetting the first page.

RFC 9457 Problem Details is a documented future target. This release does not change established public error payloads; a migration will require separate compatibility tests, API documentation, and a semantic release.

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
