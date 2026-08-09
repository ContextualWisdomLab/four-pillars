# Four Pillars Technical Requirements Document

## 1. Architecture principles

The runtime system has four primary trust boundaries. The **calculation core** accepts validated birth input and produces immutable chart/luck models. The **interpretation boundary** serializes those models as untrusted evidence and calls one explicitly selected OpenAI-compatible adapter: direct NVIDIA NIM by default or optional Contextual Orchestrator for organization routing and governance. The **quality boundary** validates schema, fingerprint, completeness, balance, Korean copy, and safety. The **delivery boundary** stores and renders only approved results. No layer may silently assume responsibilities owned by an earlier layer.

Repository automation adds separate control-plane authorities: deterministic quality verification, model-backed product proposal/repair, independent review evidence, merge authority, and protected-main release authority. These authorities must not collapse into one model credential or one green status.

The selected interpretation adapter never changes deterministic evidence and never silently fails over to another backend. Traditional Four Pillars prose is symbolic and conditional; standards traceability governs software and AI operations rather than asserting scientific prediction.

The authoritative documentation graph is defined in `docs/architecture/DOCUMENTATION_MAP.md`. A contradiction between this TRD and protected-main code is a documentation defect, not permission to reinterpret production behavior.

## 2. Technology stack

- Python 3.11 and 3.12
- Pydantic 2 and Pydantic Settings 2 for data, LLM, and configuration contracts
- FastAPI and Uvicorn for HTTP
- Typer for CLI
- SQLite WAL for the durable standalone work queue
- HTTPX for direct NVIDIA NIM and optional Contextual Orchestrator
- ReportLab CJK CID fonts for searchable Korean PDF
- Korean Lunar Calendar for solar/lunar input conversion
- Local deterministic VSOP87-based solar-term solving with committed KASI/NAOJ external fixtures
- Pytest, pytest-cov, Ruff, and GitHub Actions for verification
- Docker Compose for separate API and worker processes
- Mermaid/PlantUML-as-code for architecture views

## 3. Components

### 3.1 `calendar.py`, `solar.py`, and deterministic evidence

`solar.py` evaluates a bounded VSOP87 Earth longitude/radius series in Terrestrial Time and applies FK5, dominant nutation, and aberration corrections without a network or third-party ephemeris dependency. `calendar.py` locates the month-changing roots, normalizes birth time, calculates four pillars, ten gods, hidden stems, growth stages, element balance, interactions, boundary warnings, and the SHA-256 fingerprint.

All twelve 2026 `jie` boundaries are checked against committed KASI/NAOJ minute-precision evidence with a two-minute budget and buyer-visible five-minute year/month transition tests. The calculation evidence version is `calendar-1.1.0`. External fixtures are immutable CI evidence; production never calls KASI/NAOJ dynamically to decide a pillar.

### 3.2 `fortune.py`

Consumes a `Chart` and creates daewoon scenarios, annual snapshots, and monthly snapshots. It preserves the chart day master when assigning ten gods and returns interactions between temporary pillars and natal pillars. Gender-unknown policy returns both direction scenarios rather than silently choosing one.

### 3.3 `generation.py`, `nim.py`, `contextual_orchestrator.py`, and `analysis.py`

`StructuredGenerationClient` is the structural boundary consumed by staged report generation. `nim.py` owns shared OpenAI-compatible structured-generation transport behavior: Bearer authentication, timeouts, retry, JSON extraction, Pydantic validation, and bounded schema repair. `NimClient` configures that behavior for direct hosted NVIDIA NIM.

`ContextualOrchestratorClient` configures the same transport base for `POST /v1/chat/completions` on the organization gateway. It adds prompt-safe attribution—always `service=four-pillars` plus optional account, team, group, and company—and synchronous routing metadata. It deliberately initializes the shared client with `native_json_mode=False`. Therefore Four Pillars does **not** send provider-native `response_format={"type":"json_object"}` through this adapter. The prompt requires JSON, returned content is parsed and validated with Pydantic, and one bounded same-backend repair may supply schema guidance after an invalid result. This prevents Four Pillars from accidentally forcing an orchestrator path into a provider-native structured-output passthrough while retaining strict application-level schema validation.

No birth data, user notes, report content, fingerprint, path, or credential is used as attribution. A selected orchestrator failure is visible and never triggers direct-NIM fallback.

`analysis.py` calls versioned stage prompts through the structural client, synthesizes the report, and requests one editorial repair only when deterministic/editorial quality checks fail. The trace contract remains compatible across backends.

### 3.4 `quality.py`

The quality gate compares calculation fingerprints, verifies required chapters, requires opportunity/caution/action lists, tests constructive relationship guidance, scans forbidden/vague copy, rejects deterministic event certainty and medical directions, and validates the disclaimer. Failure becomes a `quality_failed` job after the bounded repair attempt.

LLM judge output is supplementary; it cannot override deterministic fixtures, schemas, rule-based quality checks, security review, or required independent review.

### 3.5 `jobs.py`, `history.py`, `service.py`, and `api.py`

SQLite stores queued, running, completed, failed, and quality-failed jobs. `BEGIN IMMEDIATE` provides atomic keyed creation and claim operations. `history.py` encodes strict versioned continuation cursors containing only a UTC timestamp and random UUID. `JobStore` implements indexed `(created_at DESC, id DESC)` keyset traversal with exact optional status filtering. The service calculates, invokes the selected interpreter, writes to a temporary artifact directory, and atomically renames it. FastAPI exposes calculation, enqueue, redacted history, individual status, deletion, and allow-listed artifact endpoints.

The required `ReportJobRepository` remains backward compatible. Atomic keyed creation and history traversal are separate runtime-checkable capabilities, so an existing organization or MSA adapter can continue serving required operations and fails explicitly only when an unsupported optional endpoint is invoked.

When no interpreter is injected, `build_report_interpreter(settings)` selects `NimReportInterpreter` for `nvidia_nim` or `ContextualOrchestratorReportInterpreter` for `contextual_orchestrator`. Explicitly injected MSA interpreters remain authoritative.

The current physical persistence and conceptual data model are documented in `docs/erd/domain-model.md`. Only `report_jobs` is an application-owned SQLite table today; report documents, calculation evidence, traces, prompt revisions and automation evidence must not be misrepresented as separate persisted rows.

### 3.6 `reporting.py`

The renderer escapes HTML, uses fixed semantic colors, builds searchable Korean PDF with CJK CID fonts, emits intermediate calculation/report JSON, and records SHA-256 hashes in `manifest.json`. It deliberately omits footers and page numbers from the default report.

### 3.7 Repository automation control plane

Protected main currently contains two separate automation roles:

- the **minute-17 deterministic quality sentinel**, which receives no model credential and checks release/product/documentation contracts;
- the **minute-47 NVIDIA/OpenCode product-development workflow**, which may propose at most one bounded product PR when its queue gate permits and uses `NVIDIA_NIM_API_KEY` only on the isolated model runner.

A **minute-07 exact-head PR steward** is Proposed while its implementation PR remains unmerged. Architecture and runbooks may describe the intended contract only when clearly marked Proposed.

Model proposal/repair, uncredentialed exact-artifact verification, late-bound publication, independent review, merge decision, and release publication are distinct authorities. The model path cannot approve, merge, release, deploy, or reuse existing reviewer-agent credentials. Exact head/base/ref/blob and immutable artifact identity are revalidated at mutation boundaries. See ADR 0007 and `docs/uml/control-plane.md`.

## 4. Runtime data flow

1. API or CLI validates `BirthInput` and `ReportRequest`.
2. Calculation core creates `Chart`, `DaewoonResult`, annual `LuckSnapshot`, and monthly `LuckSnapshot`.
3. The chart fingerprint and full immutable JSON are passed to each applicable prompt.
4. The selected structured-generation backend returns a Pydantic-validated section or draft.
5. Synthesis returns the full report structure.
6. Quality gate compares report and deterministic source.
7. Optional editorial repair changes copy but cannot change calculations.
8. Renderer writes JSON, HTML, PDF, traces, and manifest to a temporary UUID directory.
9. Successful generation atomically publishes the directory and marks the job completed.
10. Authenticated history reads return only redacted job summaries and an opaque exclusive keyset boundary; they never read or serialize stored report requests.

## 5. Calculation policy

Modern Gregorian dates use integer Julian day numbers for the sexagenary day and the bounded VSOP87 apparent-solar-longitude implementation for `jie` crossings. UTC is converted to Terrestrial Time through tabled `TAI-UTC` plus 32.184 seconds. The year changes at 315 degrees apparent solar longitude (Li Chun). Month branches start at Xiao Han, Li Chun, Jing Zhe, Qing Ming, Li Xia, Mang Zhong, Xiao Shu, Li Qiu, Bai Lu, Han Lu, Li Dong, and Da Xue.

The service records calculation version `calendar-1.1.0` and warns within six hours of a boundary. The KASI 2026 fixture and signed timing deltas are independently reviewable; NAOJ provides independent corroboration at the same UTC+09:00 civil offset. Historical timezone and pre-1972 timescale limitations remain explicit. See `CALCULATION.md` and `docs/doctoring/kasi-solar-term-golden-fixtures.md`.

A future calculation-policy change that can change user-visible pillars requires a calculation evidence version increment, externally grounded boundary tests, regression fixtures and release notes. Prompt changes cannot silently repair calculation errors.

## 6. Interpretation backend contract

### Direct NVIDIA NIM

The direct key is supplied only through `NVIDIA_NIM_API_KEY`. The base URL, model, timeout, retry budget, and repair budget use the `NIM_*` settings. The client may use provider-native JSON mode and includes Pydantic JSON Schema in a bounded repair instruction when the first output is invalid.

### Contextual Orchestrator

The gateway token is supplied only through `CONTEXTUAL_ORCHESTRATOR_TOKEN`. The base URL, model, timeout, retry budget, repair budget, and organizational attribution use `CONTEXTUAL_ORCHESTRATOR_*` settings. The adapter sets `native_json_mode=False`; it omits provider-native JSON `response_format` while requiring JSON in the prompt and retaining Pydantic parsing/validation/repair in Four Pillars. The gateway may route to NVIDIA workers or other organization-approved providers, but Four Pillars sees one explicit orchestrator boundary and does not receive provider administration credentials.

### Shared reliability

HTTP 408, 429, and 5xx responses are retried using integer `Retry-After` or bounded exponential delay. Network timeouts and connection failures are retried. Other 4xx responses fail immediately. A selected backend failure is visible and never triggers implicit fallback.

## 7. Reliability and failure handling

The queue persists before model work begins. Workers claim one job atomically. Partial artifact directories are hidden with a dot prefix and deleted after failure. Terminal errors are truncated before database storage. A worker restart leaves already-running jobs visible for operational inspection; recovery/requeue behavior must prove no live worker still owns the same logical work before it is allowed to replay. Calculation and quality errors are distinguished from network/model errors.

History pages fetch one more row than requested and emit a cursor only when another row exists. Equal timestamps use the UUID as a deterministic tie-breaker. New concurrent inserts appear on a future first-page read rather than inside an existing continuation sequence. Unsupported cursor versions and malformed payloads fail closed.

Automation waiting is local: a queued review/check/provider result does not authorize a bypass and does not block non-conflicting work. Source/ref movement invalidates stale write assumptions.

## 8. Security, privacy, and data governance

Birth/context/report data is purpose-required confidential application data, not something the product can universally mask before authorized processing. The design follows `docs/security/DATA_GOVERNANCE.md` and proposed ADR 0004: preserve only the required semantic data inside the authorized flow, while restricting its propagation to public history, telemetry, attribution, filenames, traces and unrelated services.

API keys use digest comparison. Provider and orchestrator credentials use Authorization headers. Artifact names are allow-listed and path-resolved. HTML is escaped. UUIDs avoid personal filenames. Container execution uses a non-root account. Remote production traffic uses TLS. Production PII-bearing persistence requires encryption at rest and separated key ownership before the profile is advertised as enterprise/public-sector ready.

Report-history responses and cursors exclude subject labels, birth data, user notes, request fingerprints, idempotency material, generated copy, model traces, and artifact paths. The history cursor is not an authorization credential; the same optional API-key dependency protects the endpoint.

Interpretation attribution contains organizational labels only. It must never contain personal information, prompt content, generated copy, fingerprints, paths, or credentials.

Organization/multi-tenant deployment requires explicit tenant/subject authorization, tenant-isolated repositories/object storage, privileged-access/break-glass audit, retention/deletion/export and backup semantics. These controls are requirements/gaps until implementation and operational evidence exist.

## 9. CSAP and SOC 2 readiness boundary

`docs/compliance/CSAP_SOC2_READINESS.md` maps current repository evidence and deployment gaps to engineering concerns relevant to KISA CSAP and AICPA SOC 2 Trust Services Criteria. The project does not claim a CSAP certificate or SOC 2 report. Source controls alone cannot establish organizational policy, operating effectiveness, cloud assessment scope, vendor management, privileged-access reviews, backup exercises, incident response or assessor conclusions.

A release may describe an implemented readiness control only with exact code/deployment evidence and must distinguish repository controls, operator-configured reference controls, Planned work, and external certification/attestation.

## 10. Observability

Health checks prove process availability; readiness verifies artifact writes and database reads. Job rows record state and timestamps. `traces.json` records model, request-attempt count, and schema-repair count without storing credentials or raw generated content in its public metadata. `manifest.json` records calculation fingerprint, model, prompt versions, and file hashes. Contextual Orchestrator may maintain its own usage and cost ledger by approved organizational dimensions.

Current generation traces are not W3C distributed traces. A future separately reviewed change may propagate `traceparent` and `tracestate` under the target-state controls in `docs/standards/TRACEABILITY.md`.

Routine observability must remain identifier/digest/status oriented. Raw personal report content, if ever needed for production incident support, belongs behind a separately authorized and auditable privileged path rather than default logs.

## 11. Test strategy

Unit/integration tests cover known pillars, all twelve externally published 2026 solar-term instants and transitions, time policies, ten gods, daewoon direction, monthly period dates, queue transitions, idempotent creation, strict history cursors, stable multi-page traversal, privacy redaction, optional adapter behavior, quality rules, report rendering, API authentication, and applicable automation trust boundaries.

Structured-generation contract tests use `httpx.MockTransport` to verify both direct NIM and orchestrator authentication, endpoint shape, direct-NIM native JSON behavior, orchestrator non-native JSON behavior, attribution, routing, schema validation, bounded repair, transient retry, terminal error, backend selection, and no-fallback behavior. Live direct NIM tests are marked and skipped without `NVIDIA_NIM_API_KEY`.

CI compiles source, validates documents/prompts, runs Ruff, enforces exactly 100 percent statement and branch coverage, builds distributions, and verifies the pinned runtime container. LLM judge results are supplementary because peer-reviewed research documents adversarial and judgment-bias risks.

Documentation tests should progressively verify canonical documentation presence/link integrity, ADR index/status consistency, current calculation/version/provider semantics and DB naming without encoding transient PR SHAs as timeless architecture.

## 12. Deployment and modular MSA

The same image runs API or worker commands. Docker Compose mounts one shared artifact volume. SQLite is appropriate for a single-node deployment; a multi-node edition should replace `JobStore` with PostgreSQL or a managed queue while preserving required and optional application interfaces. A history-capable remote adapter must preserve deterministic exclusive keyset ordering across every API instance.

Direct NIM remains the default independent product. An organization module may select Contextual Orchestrator without installing it as a Python dependency or changing domain/application contracts. The Contextual Orchestrator URL and token are deployment concerns; the gateway may itself be shared with central `.github`, `naruon`, and other services.

No integration may depend on directly reading/writing another service's private application tables. Future PostgreSQL/object-storage adapters require explicit tenant/authorization, encryption/key ownership, migration/rollback, retention/deletion/export, crash recovery and backup/restore evidence. See proposed ADR 0006.

## 13. Architecture and documentation governance

`docs/architecture/DOCUMENTATION_MAP.md` defines canonical documentation and update triggers. `docs/adr/README.md` defines ADR status/supersession. `docs/erd/domain-model.md` distinguishes actual SQLite persistence from conceptual/derived/file/external-control-plane entities. `docs/uml/architecture.md` covers runtime views and `docs/uml/control-plane.md` covers repository automation authority.

Historical Superpowers specs/plans and PR bodies are provenance, not current architecture authority. Current/Accepted/Proposed/Planned status must be explicit. The proposed PR steward may not be described as implemented before protected-main merge.

## 14. Standards and research traceability

`docs/standards/REFERENCES.md` records APA 7th references for software quality, AI governance/risk, information security/privacy, requirements and architecture description, UML, CSAP/SOC 2 readiness, RFC/W3C targets, KASI/NAOJ calendar evidence, VSOP87, IERS timescales, JPL DE440, and peer-reviewed LLM-judge research. `docs/standards/TRACEABILITY.md` maps those sources to code, tests, workflows, documentation and residual gaps.

Key documentation standards for this baseline are ISO/IEC/IEEE 42010:2022 and ISO/IEC/IEEE 29148:2018. As of 2026-08-09, ISO lists the 2018 requirements-engineering edition as current/confirmed while Edition 3 is at DIS stage; the project monitors the revision without treating it as final. The mapping is not an ISO, CSAP or SOC 2 certification statement or scientific validation of traditional interpretation.
