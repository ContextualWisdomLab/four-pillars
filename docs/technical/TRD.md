# Four Pillars Technical Requirements Document

## 1. Architecture principles

The system has four trust boundaries. The **calculation core** accepts validated birth input and produces immutable chart/luck models. The **interpretation boundary** serializes those models as untrusted evidence and calls one explicitly selected OpenAI-compatible adapter: direct NVIDIA NIM by default or optional Contextual Orchestrator for organization routing and governance. The **quality boundary** validates schema, fingerprint, completeness, balance, Korean copy, and safety. The **delivery boundary** stores and renders only approved results. No layer may silently assume responsibilities owned by an earlier layer.

The selected interpretation adapter never changes deterministic evidence and never silently fails over to another backend. Traditional Four Pillars prose is symbolic and conditional; standards traceability governs software and AI operations rather than asserting scientific prediction.

## 2. Technology stack

- Python 3.11 through 3.14
- Pydantic 2 and Pydantic Settings 2 for data, LLM, and configuration contracts
- FastAPI and Uvicorn for HTTP
- Typer for CLI
- SQLite WAL for the durable work queue
- HTTPX for direct NVIDIA NIM and optional Contextual Orchestrator
- ReportLab CJK CID fonts for searchable Korean PDF
- Korean Lunar Calendar for solar/lunar input conversion
- Pytest, pytest-cov, Ruff, and GitHub Actions for verification
- Docker Compose for separate API and worker processes

## 3. Components

### 3.1 `calendar.py` and `solar.py`

`solar.py` evaluates a bounded VSOP87 Earth longitude/radius series in Terrestrial Time and applies FK5, dominant nutation, and aberration corrections without a network or third-party ephemeris dependency. `calendar.py` locates the month-changing roots, normalizes birth time, calculates four pillars, ten gods, hidden stems, growth stages, element balance, interactions, boundary warnings, and the SHA-256 fingerprint.

All twelve 2026 `jie` boundaries are checked against committed KASI/NAOJ minute-precision evidence with a two-minute budget and buyer-visible five-minute year/month transition tests. The calculation evidence version is `calendar-1.1.0`.

### 3.2 `fortune.py`

Consumes a `Chart` and creates daewoon scenarios, annual snapshots, and monthly snapshots. It preserves the chart day master when assigning ten gods and returns interactions between temporary pillars and natal pillars.

### 3.3 `generation.py`, `nim.py`, `contextual_orchestrator.py`, and `analysis.py`

`StructuredGenerationClient` is the structural boundary consumed by staged report generation. `nim.py` owns the shared OpenAI-compatible structured-generation transport: Bearer authentication, timeouts, retry, JSON extraction, Pydantic validation, and bounded schema repair. `NimClient` configures that behavior for direct hosted NVIDIA NIM.

`ContextualOrchestratorClient` configures the same behavior for `POST /v1/chat/completions` on the organization gateway. It adds prompt-safe attribution—always `service=four-pillars` plus optional account, team, group, and company—and synchronous routing metadata. It uses `response_format={"type":"json_object"}` so provider features survive the orchestrator's structured-output passthrough. No birth data, user notes, report content, fingerprint, path, or credential is used as attribution.

`analysis.py` calls versioned stage prompts through the structural client, synthesizes the report, and requests one editorial repair only when deterministic quality checks fail. The trace contract remains compatible across backends.

### 3.4 `quality.py`

The quality gate compares calculation fingerprints, verifies required chapters, requires opportunity/caution/action lists, tests constructive relationship guidance, scans forbidden/vague copy, rejects deterministic event certainty and medical directions, and validates the disclaimer. Failure becomes a `quality_failed` job after the bounded repair attempt.

### 3.5 `jobs.py`, `history.py`, `service.py`, and `api.py`

SQLite stores queued, running, completed, failed, and quality-failed jobs. `BEGIN IMMEDIATE` provides atomic keyed creation and claim operations. `history.py` encodes strict versioned continuation cursors containing only a UTC timestamp and random UUID. `JobStore` implements indexed `(created_at DESC, id DESC)` keyset traversal with exact optional status filtering. The service calculates, invokes the selected interpreter, writes to a temporary artifact directory, and atomically renames it. FastAPI exposes calculation, enqueue, redacted history, individual status, deletion, and allow-listed artifact endpoints.

The required `ReportJobRepository` remains backward compatible. Atomic keyed creation and history traversal are separate runtime-checkable capabilities, so an existing organization or MSA adapter can continue serving required operations and fails explicitly only when an unsupported optional endpoint is invoked.

When no interpreter is injected, `build_report_interpreter(settings)` selects `NimReportInterpreter` for `nvidia_nim` or `ContextualOrchestratorReportInterpreter` for `contextual_orchestrator`. Explicitly injected MSA interpreters remain authoritative.

### 3.6 `reporting.py`

The renderer escapes HTML, uses fixed semantic colors, builds searchable Korean PDF with CJK CID fonts, emits intermediate calculation/report JSON, and records SHA-256 hashes in `manifest.json`. It deliberately omits footers and page numbers from the default report.

## 4. Data flow

1. API or CLI validates `BirthInput` and `ReportRequest`.
2. Calculation core creates `Chart`, `DaewoonResult`, annual `LuckSnapshot`, and monthly `LuckSnapshot`.
3. The chart fingerprint and full immutable JSON are passed to each prompt.
4. The selected structured-generation backend returns a Pydantic-validated section or draft.
5. Synthesis returns the full report structure.
6. Quality gate compares report and deterministic source.
7. Optional editorial repair changes copy but cannot change calculations.
8. Renderer writes JSON, HTML, PDF, traces, and manifest to a temporary UUID directory.
9. Successful generation atomically publishes the directory and marks the job completed.
10. Authenticated history reads return only redacted job summaries and an opaque exclusive keyset boundary; they never read or serialize stored report requests.

## 5. Calculation policy

Modern Gregorian dates use integer Julian day numbers for the sexagenary day and the bounded VSOP87 apparent-solar-longitude implementation for `jie` crossings. UTC is converted to Terrestrial Time through tabled `TAI-UTC` plus 32.184 seconds. The year changes at 315 degrees apparent solar longitude (Li Chun). Month branches start at Xiao Han, Li Chun, Jing Zhe, Qing Ming, Li Xia, Mang Zhong, Xiao Shu, Li Qiu, Bai Lu, Han Lu, Li Dong, and Da Xue.

The service records calculation version `calendar-1.1.0` and warns within six hours of a boundary. The KASI 2026 fixture and signed timing deltas are independently reviewable; historical timezone and pre-1972 timescale limitations remain explicit. See `CALCULATION.md` and `docs/doctoring/kasi-solar-term-golden-fixtures.md`.

## 6. Interpretation backend contract

### Direct NVIDIA NIM

The direct key is supplied only through `NVIDIA_NIM_API_KEY`. The base URL, model, timeout, retry budget, and repair budget use the `NIM_*` settings. The client sends `response_format={"type":"json_object"}` and includes Pydantic JSON Schema in a bounded repair instruction when the first output is invalid.

### Contextual Orchestrator

The gateway token is supplied only through `CONTEXTUAL_ORCHESTRATOR_TOKEN`. The base URL, model, timeout, retry budget, repair budget, and organizational attribution use `CONTEXTUAL_ORCHESTRATOR_*` settings. The gateway may route to NVIDIA workers or other organization-approved providers, but Four Pillars sees one explicit orchestrator boundary and does not receive provider administration credentials.

### Shared reliability

HTTP 408, 429, and 5xx responses are retried using integer `Retry-After` or bounded exponential delay. Network timeouts and connection failures are retried. Other 4xx responses fail immediately. A selected backend failure is visible and never triggers implicit fallback.

## 7. Reliability and failure handling

The queue persists before model work begins. Workers claim one job atomically. Partial artifact directories are hidden with a dot prefix and deleted after failure. Terminal errors are truncated before database storage. A worker restart leaves already-running jobs visible for operational inspection; a future recovery command may requeue them after an operator confirms that no worker owns them. Calculation and quality errors are distinguished from network/model errors.

History pages fetch one more row than requested and emit a cursor only when another row exists. Equal timestamps use the UUID as a deterministic tie-breaker. New concurrent inserts appear on a future first-page read rather than inside an existing continuation sequence. Unsupported cursor versions and malformed payloads fail closed.

## 8. Security and privacy

Birth context is untrusted data enclosed in a JSON input boundary. API keys use digest comparison. Provider and orchestrator credentials use Authorization headers. Artifact names are allow-listed and path-resolved. HTML is escaped. UUIDs avoid personal filenames. Container execution uses a non-root account. Production must use TLS, restricted artifact storage, secret management, log redaction, and retention/deletion procedures.

Report-history responses and cursors exclude subject labels, birth data, user notes, request fingerprints, idempotency material, generated copy, model traces, and artifact paths. The history cursor is not an authorization credential; the same optional API-key dependency protects the endpoint.

Interpretation attribution contains organizational labels only. It must never contain personal information, prompt content, generated copy, fingerprints, paths, or credentials.

## 9. Observability

Health checks prove process availability; readiness verifies artifact writes and database reads. Job rows record state and timestamps. `traces.json` records model, request-attempt count, and schema-repair count without storing credentials or model content. `manifest.json` records calculation fingerprint, model, prompt versions, and file hashes. Contextual Orchestrator may maintain its own usage and cost ledger by approved organizational dimensions.

Current generation traces are not W3C distributed traces. A future separately reviewed change may propagate `traceparent` and `tracestate` under the target-state controls in `docs/standards/TRACEABILITY.md`.

## 10. Test strategy

Unit tests cover known pillars, all twelve externally published 2026 solar-term instants and transitions, time policies, ten gods, daewoon direction, monthly period dates, queue transitions, idempotent creation, strict history cursors, stable multi-page traversal, privacy redaction, optional adapter behavior, quality rules, report rendering, and API authentication.

Structured-generation contract tests use `httpx.MockTransport` to verify both direct NIM and orchestrator authentication, endpoint shape, JSON mode, attribution, routing, schema validation, bounded repair, transient retry, terminal error, backend selection, and no-fallback behavior. Live direct NIM tests are marked and skipped without `NVIDIA_NIM_API_KEY`.

CI compiles source, validates documents/prompts, runs Ruff, enforces exactly 100 percent statement and branch coverage, builds distributions, and verifies the pinned runtime container. LLM judge results are supplementary because peer-reviewed research documents adversarial and judgment-bias risks.

## 11. Deployment

The same image runs API or worker commands. Docker Compose mounts one shared artifact volume. SQLite is appropriate for a single-node deployment; a multi-node edition should replace `JobStore` with PostgreSQL or a managed queue while preserving required and optional application interfaces. A history-capable remote adapter must preserve deterministic exclusive keyset ordering across every API instance.

Direct NIM remains the default independent product. An organization module may select Contextual Orchestrator without installing it as a Python dependency or changing domain/application contracts. The Contextual Orchestrator URL and token are deployment concerns; the gateway may itself be shared with central `.github`, `naruon`, and other services.

## 12. Standards and research traceability

`docs/standards/REFERENCES.md` records APA 7th references for ISO/IEC 25010:2023, ISO/IEC 42001:2023, ISO/IEC 23894:2023, NIST AI RMF 1.0, NIST AI 600-1, RFC 9457, W3C Trace Context, KASI/NAOJ calendar evidence, VSOP87, IERS timescales, JPL DE440, and peer-reviewed LLM-judge research. `docs/standards/TRACEABILITY.md` maps those sources to code, tests, workflows, and residual gaps.

The mapping is maintained by `check_docs.py`, `product_gap_audit.py`, the hourly quality loop, PR review, and semantic releases. It is not an ISO certification statement or scientific validation of traditional interpretation.
