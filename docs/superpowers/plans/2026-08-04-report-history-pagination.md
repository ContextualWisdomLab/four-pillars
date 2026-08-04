# Report History Pagination Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a redacted, keyset-paginated `GET /v1/reports` collection API behind an optional MSA repository capability.

**Architecture:** Keep the required `ReportJobRepository` contract unchanged and add a separate runtime-checkable `ReportJobHistoryRepository`. A focused `history.py` module owns strict RFC 4648 base64url cursor encoding and decoding, while `JobStore` owns indexed SQLite keyset queries ordered by `(created_at DESC, id DESC)`. FastAPI maps internal jobs through the existing privacy-safe public view.

**Tech Stack:** Python 3.11/3.12, FastAPI, Pydantic 2, SQLite, pytest, coverage.py, Ruff, GitHub Actions.

## Global Constraints

- `NVIDIA_NIM_API_KEY` remains the only hosted NVIDIA NIM credential.
- Statement and branch coverage remain exactly 100%.
- Every production public API retains a complete docstring.
- Database object names contain at least two words and use `snake_case` unless an external system requires camelCase or PascalCase.
- Existing `ReportJobRepository` adapters remain compatible.
- Collection responses and cursors contain no birth input, subject name, user context, raw report text, fingerprint, idempotency material, or artifact path.
- Cursor timestamps are UTC RFC 3339 values, and the encoded payload uses unpadded RFC 4648 base64url.

---

### Task 1: Lock cursor and repository behavior with failing tests

**Files:**
- Create: `tests/test_report_history.py`
- Modify: `tests/test_modular_service_ports.py`

**Interfaces:**
- Consumes: existing `JobStore`, `JobStatus`, `ReportJob`, and legacy repository fixture.
- Produces: required behavior for `encode_history_cursor`, `decode_history_cursor`, `JobStore.list_jobs`, `ReportJobHistoryRepository`, and `HistoryNotSupportedError`.

- [ ] **Step 1: Add cursor contract tests**

Create tests that require:

```python
cursor = encode_history_cursor(created_at, job_id)
assert cursor.startswith("v1.")
assert decode_history_cursor(cursor) == (created_at, job_id)
```

Add parameterized rejection cases for an unknown version, malformed base64url, invalid JSON, extra JSON fields, a non-UTC timestamp, and a non-UUID job identifier.

- [ ] **Step 2: Add repository pagination tests**

Create five rows with controlled timestamps, including two rows with the same timestamp. Require newest-first `(created_at DESC, id DESC)` ordering, `limit + 1` continuation detection, no duplicate identifiers across pages, and `next_cursor is None` on the final page.

Require optional `JobStatus.COMPLETED` filtering and an empty page after the final cursor.

- [ ] **Step 3: Add optional-capability tests**

Extend the modular port test so `JobStore` satisfies `ReportJobHistoryRepository`, while the existing `LegacyRepository` does not. Require `ReportService.list_jobs` to raise `HistoryNotSupportedError` for that legacy adapter.

- [ ] **Step 4: Run focused tests to verify RED**

Run:

```bash
pytest tests/test_report_history.py tests/test_modular_service_ports.py -v
```

Expected: collection errors because the history module, port, service error, and repository method do not exist.

- [ ] **Step 5: Commit the RED contract**

```bash
git add tests/test_report_history.py tests/test_modular_service_ports.py
git commit -m "test: require privacy-safe report history pagination"
```

### Task 2: Implement cursor and SQLite keyset pagination

**Files:**
- Create: `src/four_pillars/history.py`
- Modify: `src/four_pillars/ports.py`
- Modify: `src/four_pillars/jobs.py`
- Modify: `src/four_pillars/__init__.py`

**Interfaces:**
- Consumes: the Task 1 tests and existing `ReportJob`/`JobStatus` models.
- Produces:
  - `encode_history_cursor(created_at: datetime, job_id: str) -> str`
  - `decode_history_cursor(cursor: str) -> tuple[datetime, str]`
  - `HistoryCursorError(ValueError)`
  - `ReportJobHistoryRepository.list_jobs(...)`
  - `JobStore.list_jobs(...)`

- [ ] **Step 1: Implement strict cursor encoding**

Serialize exactly `created_at` and `job_id` with sorted compact JSON. Require timezone-aware UTC input and a valid UUID. Encode with `base64.urlsafe_b64encode`, strip `=`, and prefix `v1.`.

- [ ] **Step 2: Implement strict cursor decoding**

Restore padding, decode with validation, parse UTF-8 JSON, reject non-dict payloads or any key set other than `{"created_at", "job_id"}`, parse `datetime.fromisoformat`, require offset zero, normalize to `UTC`, and validate the UUID. Raise `HistoryCursorError("Invalid report-history cursor")` for every invalid form.

- [ ] **Step 3: Add the optional history port**

Add:

```python
@runtime_checkable
class ReportJobHistoryRepository(Protocol):
    def list_jobs(
        self,
        *,
        limit: int,
        cursor: str | None = None,
        status: JobStatus | None = None,
    ) -> tuple[list[ReportJob], str | None]:
        ...
```

Export it from the top-level package without changing the required base repository.

- [ ] **Step 4: Add compliant indexes**

Create:

```sql
CREATE INDEX IF NOT EXISTS idx_report_jobs_created_id
ON report_jobs(created_at DESC, id DESC)
```

and:

```sql
CREATE INDEX IF NOT EXISTS idx_report_jobs_status_created_id
ON report_jobs(status, created_at DESC, id DESC)
```

Keep the existing indexes for backward-compatible migrations unless measurements justify their removal in a separate change.

- [ ] **Step 5: Implement the keyset query**

Use a cursor predicate equivalent to:

```sql
created_at < ? OR (created_at = ? AND id < ?)
```

Append an exact status predicate when supplied, order by `created_at DESC, id DESC`, and fetch `limit + 1` rows. Return only the requested limit and encode the final returned row as `next_cursor` when another row exists.

- [ ] **Step 6: Run focused tests to verify GREEN**

Run:

```bash
pytest tests/test_report_history.py tests/test_modular_service_ports.py -v
```

Expected: all focused tests pass.

- [ ] **Step 7: Commit repository implementation**

```bash
git add src/four_pillars/history.py src/four_pillars/ports.py src/four_pillars/jobs.py src/four_pillars/__init__.py tests/test_report_history.py tests/test_modular_service_ports.py
git commit -m "feat: add optional report history repository capability"
```

### Task 3: Expose the privacy-safe HTTP collection endpoint

**Files:**
- Modify: `src/four_pillars/service.py`
- Modify: `src/four_pillars/api.py`
- Modify: `tests/test_api.py`
- Modify: `tests/test_api_more.py`

**Interfaces:**
- Consumes: `ReportJobHistoryRepository.list_jobs` from Task 2.
- Produces:
  - `HistoryNotSupportedError`
  - `ReportService.list_jobs(...)`
  - `ReportJobPageView(items: list[ReportJobView], next_cursor: str | None)`
  - authenticated `GET /v1/reports`

- [ ] **Step 1: Add failing API tests**

Require default newest-first results, `limit=1` continuation, cursor traversal, `status=completed` filtering, privacy redaction for every item, invalid cursor HTTP 400, invalid limit/status HTTP 422, API-key authentication, and HTTP 501 for an adapter without the optional capability.

- [ ] **Step 2: Verify API RED**

Run:

```bash
pytest tests/test_api.py tests/test_api_more.py -v
```

Expected: GET `/v1/reports` is not implemented and returns method-not-allowed or validation mismatches.

- [ ] **Step 3: Implement service capability detection**

Add `HistoryNotSupportedError` and a `ReportService.list_jobs` method that uses `isinstance(self.store, ReportJobHistoryRepository)` and fails explicitly when absent.

- [ ] **Step 4: Implement the response model and route**

Add:

```python
class ReportJobPageView(BaseModel):
    items: list[ReportJobView]
    next_cursor: str | None = None
```

Implement `GET /v1/reports` with `limit: int = Query(default=20, ge=1, le=100)`, optional `cursor`, optional `JobStatus`, and the existing authentication dependency. Convert `HistoryCursorError` to HTTP 400 and `HistoryNotSupportedError` to HTTP 501.

- [ ] **Step 5: Run API tests to verify GREEN**

Run:

```bash
pytest tests/test_api.py tests/test_api_more.py -v
```

Expected: all API tests pass and public payloads remain redacted.

- [ ] **Step 6: Commit the API increment**

```bash
git add src/four_pillars/service.py src/four_pillars/api.py tests/test_api.py tests/test_api_more.py
git commit -m "feat: expose cursor-paginated report history"
```

### Task 4: Document, audit, and merge the exact green head

**Files:**
- Modify: `CHANGELOG.md`
- Modify: `docs/technical/API.md`
- Modify: `docs/technical/MODULARITY.md`
- Modify: `docs/product/PRD.md`
- Modify: `scripts/product_gap_audit.py`
- Modify: `tests/test_hourly_product_loop.py`

**Interfaces:**
- Consumes: the complete repository and HTTP implementation.
- Produces: user-facing history documentation, integration contracts, audit coverage for the optional port and indexes, and release-ready verification evidence.

- [ ] **Step 1: Document the endpoint**

Describe ordering, query parameters, response fields, cursor opacity, privacy exclusions, HTTP 400/422/501 behavior, and the fact that concurrent inserts appear only on a new first-page traversal.

- [ ] **Step 2: Document modularity**

State that history is a separate optional capability and define the atomic ordering and continuation invariants required of PostgreSQL or managed adapters.

- [ ] **Step 3: Update the changelog**

Add the redacted report-history collection endpoint, stable keyset pagination, and optional repository capability under `Unreleased` without advancing the version until the feature is fully reviewed and release-ready.

- [ ] **Step 4: Extend deterministic product-gap auditing**

Require `ReportJobHistoryRepository`, the two history indexes, and the documented `GET /v1/reports` contract. Keep every detected database object subject to the two-word naming rule.

- [ ] **Step 5: Run the complete release gate**

Run:

```bash
python -m pip check
python scripts/product_gap_audit.py
ruff check .
python -m compileall -q src tests scripts
python scripts/check_docs.py
python scripts/check_prompts.py
pytest -m 'not nim_live' -W error::ResourceWarning --cov=four_pillars --cov-report=term-missing
python -m build --no-isolation
docker build --tag four-pillars:history .
```

Expected: all commands succeed; every production statement and branch remains covered; public API docstrings are complete; package and container builds succeed.

- [ ] **Step 6: Review and resolve every PR finding**

Inspect the complete diff, issue comments, review submissions, and every inline thread. Fix each actionable finding, rerun all checks on the exact final head, and ensure all threads are resolved or obsolete.

- [ ] **Step 7: Merge with an expected-head guard**

Squash merge only after CI, Security Scan, and Semgrep succeed on the exact head SHA.
