# API Reference

## Authentication

When `API_KEY_SHA256` is empty, development requests are accepted without a key. In production, store the lowercase SHA-256 digest of an API key and send the original key in `X-API-Key`. The service compares digests in constant time. Health and readiness endpoints remain unauthenticated for infrastructure probes.

## Calculation endpoints

`POST /v1/chart` accepts a `BirthInput` object with local ISO `birth`, IANA `timezone`, `gender`, `calendar`, `lunar_leap_month`, `birth_time_known`, optional `longitude`, `time_basis`, and `day_boundary`. It returns the normalized moment, four pillars, day master, element balance, interactions, adjacent solar terms, warnings, policy version, and fingerprint.

`POST /v1/luck/daewoon` accepts the same `BirthInput` and returns one direction scenario when gender is known or two scenarios when gender is unspecified.

`POST /v1/luck/annual` accepts `{ "birth": BirthInput, "year": 2026, "month": 1 }` and returns the Li-Chun-bounded annual snapshot. `month` is ignored by this endpoint.

`POST /v1/luck/monthly` accepts the same envelope and returns the requested Gregorian month's `jie`-bounded snapshot.

## Report jobs

`POST /v1/reports` validates a report request and returns HTTP 202 with a queued job. The body contains `subject_name`, `birth`, `annual_year`, `monthly_year`, `monthly_month`, and optional `user_context`. The request is durable before NIM is called.

`GET /v1/reports/{job_id}` returns `queued`, `running`, `completed`, `failed`, or `quality_failed`, timestamps, a bounded error string, and the internal artifact directory only after completion.

A separate worker started with `four-pillars worker` claims jobs. This avoids tying long NIM calls to an HTTP request and allows the API to restart independently.

## Artifacts

`GET /v1/reports/{job_id}/artifacts/{filename}` accepts only `chart.json`, `daewoon.json`, `annual.json`, `monthly.json`, `report.json`, `traces.json`, `manifest.json`, `report.html`, or `report.pdf`. The optional `download=false` omits the attachment filename. Any path traversal or unknown name returns 404.

`DELETE /v1/reports/{job_id}` removes artifacts and the database row only when the job is terminal. Running and queued jobs return 409.

## Operations

- `GET /health` proves the API process is alive.
- `GET /ready` proves the artifact directory is writable and SQLite is readable.
- Interactive OpenAPI is available at `/docs`.

## Error behavior

Pydantic validation returns HTTP 422. Missing resources return 404. Authentication failures return 401. Non-terminal deletion returns 409. Calculation policy errors are returned synchronously by calculation endpoints; report-generation failures are stored on the job. NIM content that remains schema-invalid after the bounded repair becomes a failed job. Report copy that remains unsafe after editorial repair becomes `quality_failed` and is not published as a completed PDF.

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
