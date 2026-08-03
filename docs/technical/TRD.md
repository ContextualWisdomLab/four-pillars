# Four Pillars Technical Requirements Document

## 1. Architecture principles

The system has four trust boundaries. The **calculation core** accepts validated birth input and produces immutable chart/luck models. The **AI boundary** serializes those models as untrusted evidence and calls only NVIDIA NIM. The **quality boundary** validates schema, fingerprint, completeness, balance, Korean copy, and safety. The **delivery boundary** stores and renders only approved results. No layer may silently assume responsibilities owned by an earlier layer.

## 2. Technology stack

- Python 3.11 and 3.12
- Pydantic 2 for immutable data contracts and LLM schemas
- FastAPI and Uvicorn for HTTP
- Typer for CLI
- SQLite WAL for the durable work queue
- HTTPX for hosted NVIDIA NIM
- ReportLab CJK CID fonts for searchable Korean PDF
- Korean Lunar Calendar for solar/lunar input conversion
- Pytest, pytest-cov, Ruff, and GitHub Actions for verification
- Docker Compose for separate API and worker processes

## 3. Components

### 3.1 `calendar.py`

Calculates timezone-normalized birth moments, optional solar-time correction, apparent solar longitude, month-changing solar terms, four pillars, ten gods, hidden stems, growth stages, element balance, interactions, warnings, and SHA-256 fingerprint. It has no network dependency.

### 3.2 `fortune.py`

Consumes a `Chart` and creates daewoon scenarios, annual snapshots, and monthly snapshots. It preserves the chart day master when assigning ten gods and returns interactions between temporary pillars and natal pillars.

### 3.3 `nim.py` and `analysis.py`

`NimClient` implements the OpenAI-compatible `/chat/completions` contract at a configurable NVIDIA base URL. It handles authentication, timeout, retry, rate limits, JSON extraction, Pydantic validation, and one bounded schema repair. `analysis.py` calls versioned stage prompts, synthesizes the report, and requests one editorial repair only when deterministic quality checks fail.

### 3.4 `quality.py`

The quality gate compares calculation fingerprints, verifies required chapters, requires opportunity/caution/action lists, tests constructive relationship guidance, scans forbidden/vague copy, rejects deterministic event certainty and medical directions, and validates the disclaimer. Failure becomes a `quality_failed` job after the bounded repair attempt.

### 3.5 `jobs.py`, `service.py`, and `api.py`

SQLite stores queued, running, completed, failed, and quality-failed jobs. `BEGIN IMMEDIATE` provides an atomic claim operation for one or more workers. The service calculates, calls NIM, writes to a temporary artifact directory, and atomically renames it. FastAPI exposes calculation, queue, status, deletion, and allow-listed artifact endpoints.

### 3.6 `reporting.py`

The renderer escapes HTML, uses fixed semantic colors, builds searchable Korean PDF with CJK CID fonts, emits intermediate calculation/report JSON, and records SHA-256 hashes in `manifest.json`. It deliberately omits footers and page numbers from the default report.

## 4. Data flow

1. API or CLI validates `BirthInput` and `ReportRequest`.
2. Calculation core creates `Chart`, `DaewoonResult`, annual `LuckSnapshot`, and monthly `LuckSnapshot`.
3. The chart fingerprint and full immutable JSON are passed to each prompt.
4. NIM returns a schema-validated section or draft.
5. Synthesis returns the full report structure.
6. Quality gate compares report and deterministic source.
7. Optional editorial repair changes copy but cannot change calculations.
8. Renderer writes JSON, HTML, PDF, traces, and manifest to a temporary UUID directory.
9. Successful generation atomically publishes the directory and marks the job completed.

## 5. Calculation policy

Modern Gregorian dates use integer Julian day numbers for the sexagenary day and a compact apparent-solar-longitude series for `jie` crossings. The year changes at 315 degrees apparent solar longitude (Li Chun). Month branches start at Xiao Han, Li Chun, Jing Zhe, Qing Ming, Li Xia, Mang Zhong, Xiao Shu, Li Qiu, Bai Lu, Han Lu, Li Dong, and Da Xue. The service records its calculation version and warns within six hours of a boundary. See `CALCULATION.md` for formulas and limitations.

## 6. NIM contract

The API key is supplied only through environment/secret storage. Generation uses `response_format={"type":"json_object"}` and Pydantic JSON Schema is included in a bounded repair instruction when the first output is invalid. HTTP 408, 429, and 5xx responses are retried using `Retry-After` or exponential delay. Other 4xx responses fail immediately. No model-provider fallback is allowed.

## 7. Reliability and failure handling

The queue persists before LLM work begins. Workers claim one job atomically. Partial artifact directories are hidden with a dot prefix and deleted after failure. Terminal errors are truncated before database storage. A worker restart leaves already-running jobs visible for operational inspection; a future recovery command may requeue them after an operator confirms that no worker owns them. Calculation and quality errors are distinguished from network/model errors.

## 8. Security and privacy

Birth context is untrusted data enclosed in a JSON input boundary. API keys use digest comparison. Artifact names are allow-listed and path-resolved. HTML is escaped. UUIDs avoid personal filenames. Container execution uses a non-root account. Production must use TLS, restricted artifact storage, secret management, log redaction, and retention/deletion procedures.

## 9. Observability

Health checks prove process availability; readiness verifies artifact writes and database reads. Job rows record state and timestamps. `traces.json` records model, request-attempt count, and schema-repair count without storing API keys. `manifest.json` records calculation fingerprint, model, prompt versions, and file hashes. Metrics and structured logs may be added behind the same service interfaces.

## 10. Test strategy

Unit tests cover known pillars, solar-term boundaries, time policies, ten gods, daewoon direction, monthly period dates, queue transitions, quality rules, report rendering, and API authentication. NIM contract tests use `httpx.MockTransport`; live hosted-NIM tests are marked and skipped without `NVIDIA_API_KEY`. CI compiles the source, validates documents/prompts, runs Ruff and coverage, and builds an installable wheel.

## 11. Deployment

The same image runs API or worker commands. Docker Compose mounts one shared artifact volume. SQLite is appropriate for a single-node deployment; a multi-node edition should replace `JobStore` with PostgreSQL or a managed queue while preserving the application interface. NIM base URL and model are configuration because free hosted model availability can change.
