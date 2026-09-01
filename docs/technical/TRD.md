# Four Pillars Technical Requirements Document

## 1. Architecture principles

The system has four trust boundaries. The **calculation core** accepts validated birth input and produces immutable chart/luck models. The **interpretation application boundary** serializes those models as untrusted evidence and crosses a `ReportInterpreter` port into the external **Model Orchestration** bounded context through a Contextual Orchestrator anti-corruption layer. The **quality boundary** validates schema, fingerprint, completeness, balance, Korean copy, and safety. The **delivery boundary** stores and renders only approved results. No layer may silently assume responsibilities owned by another bounded context.

Four Pillars owns interpretation intent, prompts, evidence, report schemas, quality rules, and artifacts. Provider discovery, provider credentials, free-pool eligibility, routing, and provider fallback are owned by Contextual Orchestrator. The repository-owned runtime fixes the virtual model to `orchestrator/free` and fails closed when that route is unavailable.

The interpretation adapter never changes deterministic evidence. Traditional Four Pillars prose is symbolic and conditional; standards traceability governs software and AI operations rather than asserting scientific prediction.

## 2. Technology stack

- Python 3.11 and 3.12
- Pydantic 2 and Pydantic Settings 2 for data, orchestration, and configuration contracts
- FastAPI and Uvicorn for HTTP
- Typer for CLI
- SQLite WAL for the durable work queue
- HTTPX for the Contextual Orchestrator OpenAI-compatible ACL
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

### 3.3 `generation.py`, `contextual_orchestrator.py`, transitional `nim.py`, and `analysis.py`

`StructuredGenerationClient` is the structural boundary consumed by staged report generation. `ContextualOrchestratorClient` implements the active Model Orchestration anti-corruption layer for `POST /v1/chat/completions`. It owns the gateway Bearer transport, bounded retry, JSON extraction, Pydantic validation, bounded schema repair, prompt-safe attribution, and synchronous orchestration metadata needed by Four Pillars.

The active settings contract permits only the virtual model `orchestrator/free`. `auto`, `route`, and `conduct` may alter test-time compute depth, but they do not change the free-pool contract. The adapter intentionally omits `response_format`, tool, and function-calling passthrough fields that could collapse a routed/conducted request to one upstream provider path. JSON correctness is enforced by the prompt, Pydantic response model, and bounded same-route repair.

Attribution always includes `service=four-pillars` plus optional account, team, group, and company. Birth data, user notes, report content, fingerprints, paths, prompts, and credentials are prohibited from attribution.

`nim.py` remains temporarily because historical offline compatibility tests share portions of its transport implementation. It is not selected by the product composition root and its provider-specific namespace is a documented DDD debt. ADR 0004 requires a bounded follow-up that moves shared transport under a provider-neutral `infrastructure/orchestration` namespace while updating imports, compatibility exports, tests, UML, and coverage evidence together.

`analysis.py` calls versioned stage prompts through the structural client, synthesizes the report, and requests one editorial repair only when deterministic quality checks fail. The application trace contract records the virtual model, attempts, repairs, prompt versions, and prompt hashes without taking ownership of provider administration.

### 3.4 `quality.py`

The quality gate compares calculation fingerprints, verifies required chapters, requires opportunity/caution/action lists, tests constructive relationship guidance, scans forbidden/vague copy, rejects deterministic event certainty and medical directions, and validates the disclaimer. Failure becomes a `quality_failed` job after the bounded repair attempt.

### 3.5 `jobs.py`, `history.py`, `service.py`, and `api.py`

SQLite stores queued, running, completed, failed, and quality-failed jobs. `BEGIN IMMEDIATE` provides atomic keyed creation and claim operations. `history.py` encodes strict versioned continuation cursors containing only a UTC timestamp and random UUID. `JobStore` implements indexed `(created_at DESC, id DESC)` keyset traversal with exact optional status filtering. The service calculates, invokes the interpreter, writes to a temporary artifact directory, and atomically renames it. FastAPI exposes calculation, enqueue, redacted history, individual status, deletion, and allow-listed artifact endpoints.

The required `ReportJobRepository` remains backward compatible. Atomic keyed creation and history traversal are separate runtime-checkable capabilities, so an existing organization or MSA adapter can continue serving required operations and fails explicitly only when an unsupported optional endpoint is invoked.

When no interpreter is injected, `build_report_interpreter(settings)` builds `ContextualOrchestratorReportInterpreter`. The repository configuration no longer contains a provider selection branch. Explicitly injected MSA interpreters remain authoritative for caller-owned composition, but that extension point does not make provider selection a Four Pillars domain concern.

### 3.6 `reporting.py`

The renderer escapes HTML, uses fixed semantic colors, builds searchable Korean PDF with CJK CID fonts, emits intermediate calculation/report JSON, and records SHA-256 hashes in `manifest.json`. It deliberately omits footers and page numbers from the default report.

## 4. Data flow

1. API or CLI validates `BirthInput` and `ReportRequest`.
2. Calculation core creates `Chart`, `DaewoonResult`, annual `LuckSnapshot`, and monthly `LuckSnapshot`.
3. The chart fingerprint and full immutable JSON are passed to each prompt.
4. `ContextualOrchestratorReportInterpreter` sends the request through `orchestrator/free`.
5. The gateway returns content that is validated against the requested Pydantic model.
6. Synthesis returns the full report structure.
7. Quality gate compares report and deterministic source.
8. Optional editorial repair changes copy but cannot change calculations and remains on `orchestrator/free`.
9. Renderer writes JSON, HTML, PDF, traces, and manifest to a temporary UUID directory.
10. Successful generation atomically publishes the directory and marks the job completed.
11. Authenticated history reads return only redacted job summaries and an opaque exclusive keyset boundary; they never read or serialize stored report requests.

## 5. Calculation policy

Modern Gregorian dates use integer Julian day numbers for the sexagenary day and the bounded VSOP87 apparent-solar-longitude implementation for `jie` crossings. UTC is converted to Terrestrial Time through tabled `TAI-UTC` plus 32.184 seconds. The year changes at 315 degrees apparent solar longitude (Li Chun). Month branches start at Xiao Han, Li Chun, Jing Zhe, Qing Ming, Li Xia, Mang Zhong, Xiao Shu, Li Qiu, Bai Lu, Han Lu, Li Dong, and Da Xue.

The service records calculation version `calendar-1.1.0` and warns within six hours of a boundary. The KASI 2026 fixture and signed timing deltas are independently reviewable; historical timezone and pre-1972 timescale limitations remain explicit. See `CALCULATION.md` and `docs/doctoring/kasi-solar-term-golden-fixtures.md`.

## 6. Model orchestration contract

### Contextual Orchestrator ACL

The gateway token is supplied only through `CONTEXTUAL_ORCHESTRATOR_TOKEN`. The base URL, timeout, retry budget, repair budget, orchestration mode, and organizational attribution use `CONTEXTUAL_ORCHESTRATOR_*` settings. The model setting is constrained to `orchestrator/free`.

The gateway may route among eligible free NVIDIA or other provider workers according to Contextual Orchestrator policy, but Four Pillars receives no provider administration credential and cannot select a provider directly. If the free pool is empty, the operation fails explicitly rather than crossing to a paid route.

### Reliability

HTTP 408, 429, and 5xx responses are retried using integer `Retry-After` or bounded exponential delay. Network timeouts and connection failures are retried. Other 4xx responses fail immediately. Repair requests use the same virtual model. Exhausted retry/repair budgets become visible job failures and never trigger a provider-native fallback.

### Caller-owned interpreter injection

The `ReportInterpreter` port remains public for modular MSA composition. A caller may inject another implementation when it owns that integration boundary. The Four Pillars settings, API, runbook, and default composition nevertheless expose only the Contextual Orchestrator ACL. This preserves dependency inversion without reintroducing provider routing into the product domain.

## 7. Reliability and failure handling

The queue persists before model work begins. Workers claim one job atomically. Partial artifact directories are hidden with a dot prefix and deleted after failure. Terminal errors are truncated before database storage. A worker restart leaves already-running jobs visible for operational inspection; a future recovery command may requeue them after an operator confirms that no worker owns them. Calculation and quality errors are distinguished from orchestration/network/model errors.

History pages fetch one more row than requested and emit a cursor only when another row exists. Equal timestamps use the UUID as a deterministic tie-breaker. New concurrent inserts appear on a future first-page read rather than inside an existing continuation sequence. Unsupported cursor versions and malformed payloads fail closed.

## 8. Security and privacy

Birth context is untrusted data enclosed in a JSON input boundary. API keys use digest comparison. The gateway credential uses the Authorization header. Artifact names are allow-listed and path-resolved. HTML is escaped. UUIDs avoid personal filenames. Container execution uses a non-root account. Production must use TLS, restricted artifact storage, secret management, log redaction, and retention/deletion procedures.

Provider-native credentials are not Four Pillars product configuration. They remain inside the Contextual Orchestrator trust boundary. The repository's normal quality/release workflows receive no model credential; the manual live lane receives only the gateway token and URL.

Report-history responses and cursors exclude subject labels, birth data, user notes, request fingerprints, idempotency material, generated copy, model traces, and artifact paths. The history cursor is not an authorization credential; the same optional API-key dependency protects the endpoint.

Interpretation attribution contains organizational labels only. It must never contain personal information, prompt content, generated copy, fingerprints, paths, or credentials.

## 9. Observability

Health checks prove process availability; readiness verifies artifact writes and database reads. Job rows record state and timestamps. `traces.json` records virtual model, request-attempt count, and schema-repair count without storing credentials or raw model content. `manifest.json` records calculation fingerprint, virtual model, prompt versions, and file hashes. Contextual Orchestrator owns provider-route telemetry and may maintain its own usage/cost ledger by approved organizational dimensions.

Current generation traces are not W3C distributed traces. A future separately reviewed change may propagate `traceparent` and `tracestate` under the target-state controls in `docs/standards/TRACEABILITY.md`.

## 10. Test strategy

Unit tests cover known pillars, all twelve externally published 2026 solar-term instants and transitions, time policies, ten gods, daewoon direction, monthly period dates, queue transitions, idempotent creation, strict history cursors, stable multi-page traversal, privacy redaction, optional adapter behavior, quality rules, report rendering, and API authentication.

Offline orchestration contract tests use `httpx.MockTransport` to verify gateway authentication, endpoint shape, `orchestrator/free`, attribution, routing, absence of provider passthrough fields, schema validation, bounded repair, transient retry, terminal error, direct-backend rejection, non-free-model rejection, and no-fallback behavior.

Live model tests are marked `orchestrator_live`, require an independently deployed gateway and `CONTEXTUAL_ORCHESTRATOR_TOKEN`, and assert that the trace remains `orchestrator/free`. No provider-native secret is available to the live workflow.

CI compiles source, validates documents/prompts, runs Ruff, enforces exactly 100 percent statement and branch coverage, builds distributions, and verifies the pinned runtime container. LLM judge results are supplementary because peer-reviewed research documents adversarial and judgment-bias risks.

## 11. Deployment

The same image runs API or worker commands. Docker Compose mounts one shared artifact volume. SQLite is appropriate for a single-node deployment; a multi-node edition should replace `JobStore` with PostgreSQL or a managed queue while preserving required and optional application interfaces. A history-capable remote adapter must preserve deterministic exclusive keyset ordering across every API instance.

LLM-backed interpretation always uses Contextual Orchestrator in repository-owned composition. The gateway URL and token are deployment concerns; the gateway may itself be shared with central `.github`, `naruon`, and other services. The product can still be deployed independently as an application, but model-provider routing is intentionally a shared infrastructure responsibility.

The repository keeps one local model-free hourly quality sentinel. Model-backed autonomous product development is coordinated by the organization-level CWL hourly maintainer instead of a second provider-credentialed writer inside this repository.

## 12. Standards and research traceability

`docs/standards/REFERENCES.md` records APA 7th references for ISO/IEC 25010:2023, ISO/IEC 42001:2023, ISO/IEC 23894:2023, NIST AI RMF 1.0, NIST AI 600-1, RFC 9457, W3C Trace Context, KASI/NAOJ calendar evidence, VSOP87, IERS timescales, JPL DE440, and peer-reviewed LLM-judge research. `docs/standards/TRACEABILITY.md` maps those sources to code, tests, workflows, and residual gaps.

The mapping is maintained by `check_docs.py`, `product_gap_audit.py`, the hourly quality loop, PR review, and semantic releases. It is not an ISO certification statement or scientific validation of traditional interpretation.
