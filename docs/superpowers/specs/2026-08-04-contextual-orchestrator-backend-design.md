# Contextual Orchestrator Interpretation Backend Design

## 1. Goal

Four Pillars shall remain a fully standalone deterministic manse-calendar and report service while gaining an optional interpretation adapter for `ContextualWisdomLab/contextual-orchestrator`. Direct NVIDIA NIM remains the default. Operators may select the orchestrator when they need organization-wide routing, usage attribution, provider governance, and shared model controls without changing calculation, report schemas, prompt versions, quality gates, queues, or artifact delivery.

The integration is additive and must not introduce a silent provider fallback. A deployment selects exactly one interpretation backend for a process: `nvidia_nim` or `contextual_orchestrator`.

## 2. Product gap

The existing service has a clean `ReportInterpreter` port, but its standalone default always constructs `NimReportInterpreter`. Organization deployments therefore need custom composition code and cannot opt into the shared orchestrator through ordinary validated settings. The gap is visible to buyers because model governance, usage attribution, provider egress policy, and cost controls would otherwise be duplicated across services.

## 3. Architecture decision

### 3.1 Preserve deterministic and quality boundaries

The calculation core remains the immutable source of year, month, day, and hour pillars; ten gods; hidden stems; growth stages; luck periods; interactions; and fingerprints. Interpretation backends receive serialized evidence as untrusted content. They may explain the evidence but may not replace it. The existing Pydantic schemas, allowed-pillar check, editorial gate, and artifact manifest remain authoritative.

### 3.2 Add a structural generation-client port

`analysis.py` shall depend on a runtime-checkable `StructuredGenerationClient` protocol instead of the concrete `NimClient` class. The protocol exposes one generic asynchronous method:

```python
async def generate(
    *,
    system_prompt: str,
    user_payload: dict[str, Any],
    response_model: type[T],
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 4096,
) -> tuple[T, NimTrace]: ...
```

`NimTrace` remains the stable trace payload for backward compatibility because its fields describe model identity, attempts, repairs, and raw content rather than a provider-specific wire format.

### 3.3 Add an orchestrator-compatible client

`ContextualOrchestratorClient` shall implement the same structured-generation contract over the orchestrator's OpenAI-compatible `POST /v1/chat/completions` endpoint. Each request shall:

- use Bearer authentication from `CONTEXTUAL_ORCHESTRATOR_TOKEN`;
- send `response_format={"type":"json_object"}` so the orchestrator selects its single-agent passthrough path and preserves structured output;
- send the selected orchestrator model, defaulting to `contextual-orchestrator`;
- attach attribution with at least `service=four-pillars` and optional account, team, group, and company dimensions;
- attach synchronous, latency-sensitive routing metadata;
- enforce the same timeout, retry, JSON extraction, Pydantic validation, and bounded schema-repair behavior as the direct NIM adapter;
- raise a backend-specific error rather than falling back to direct NIM.

The repair request shall include the required JSON Schema and preserve the untrusted-data boundary.

### 3.4 Select adapters through validated settings

`Settings` shall add:

```python
interpretation_backend: Literal["nvidia_nim", "contextual_orchestrator"] = "nvidia_nim"
contextual_orchestrator_base_url: str = "http://127.0.0.1:8100/v1"
contextual_orchestrator_token: str | None = None
contextual_orchestrator_model: str = "contextual-orchestrator"
contextual_orchestrator_timeout_seconds: float = 120
contextual_orchestrator_max_retries: int = 3
contextual_orchestrator_max_schema_repairs: int = 1
contextual_orchestrator_account: str = ""
contextual_orchestrator_team: str = ""
contextual_orchestrator_group: str = ""
contextual_orchestrator_company: str = "ContextualWisdomLab"
```

Pydantic shall reject unknown backend names and out-of-range operational values. Secrets remain optional at settings-load time so API health and deterministic calculation endpoints can start without an LLM credential. The selected adapter shall fail clearly only when report generation requires a missing credential.

`build_report_interpreter(settings)` shall return `NimReportInterpreter` or `ContextualOrchestratorReportInterpreter`. `ReportService` shall use this factory only when no interpreter was injected, preserving current MSA composition and tests.

## 4. MSA and standalone behavior

### Standalone

The default deployment remains unchanged: `INTERPRETATION_BACKEND=nvidia_nim` and `NVIDIA_NIM_API_KEY` authenticate direct hosted NIM calls.

### Organization module

An organization deployment may set `INTERPRETATION_BACKEND=contextual_orchestrator`, point at its approved orchestrator endpoint, and provide a dedicated Bearer token. The Four Pillars API, worker, queue, calculation module, report schemas, and artifacts remain unchanged.

### Custom composition

Callers may still inject any structural `ReportInterpreter`, `ReportJobRepository`, and `ArtifactPublisher`. Settings-based selection does not make the orchestrator a required package dependency and does not alter required repository ports.

## 5. Security and privacy

- No raw birth data, user context, generated report text, API key, or Bearer token enters usage attribution.
- Attribution fields contain operator-supplied organizational labels only.
- The orchestrator token is sent only in the `Authorization` header.
- Direct NIM and orchestrator tokens are never logged or written to traces.
- The client accepts a configurable base URL for approved internal or hosted gateways; production operators must use TLS except for explicitly local development.
- No backend failover occurs implicitly. An unavailable or misconfigured backend fails the report job visibly.
- Existing prompt-injection boundaries remain unchanged: user data is serialized inside an explicit untrusted-content envelope.

## 6. Reliability and observability

Both backends retain bounded retries for timeouts, network failures, HTTP 408, HTTP 429, and server errors. Other client errors fail immediately. `Retry-After` is honored when it is an integer number of seconds. A schema-invalid response receives at most the configured number of repair requests.

Traces retain model, attempt count, repair count, prompt version, and prompt SHA-256. The orchestrator additionally receives attribution so its own cost ledger can roll up use under `service=four-pillars` without exposing prompt content.

## 7. Standards and evidence traceability

A new `docs/standards/REFERENCES.md` shall provide APA 7th edition references, URLs, and application notes for:

- ISO/IEC 25010:2023 software product quality;
- ISO/IEC 42001:2023 AI management systems;
- ISO/IEC 23894:2023 AI risk management;
- NIST AI Risk Management Framework 1.0;
- NIST AI 600-1, Generative AI Profile;
- RFC 9457 Problem Details for HTTP APIs;
- W3C Trace Context;
- peer-reviewed 2024 research on LLM-as-a-judge robustness and bias.

A companion `docs/standards/TRACEABILITY.md` shall map each applicable control to code, tests, workflows, evidence, and explicit limitations. Traditional Four Pillars interpretation is not presented as scientific prediction; cited research governs software quality, AI evaluation, privacy, reliability, and governance.

The hourly product loop already runs `check_docs.py` and `product_gap_audit.py`; those checks shall require the standards documents and key APA/standards tokens so missing doctoring becomes a scheduled regression.

## 8. Testing

### Backend contract tests

- direct NIM remains the default;
- explicit orchestrator selection builds the orchestrator adapter;
- invalid backend names fail settings validation;
- missing orchestrator token fails generation with a clear error;
- Authorization header, endpoint path, model, response format, attribution, and routing are correct;
- successful structured output validates through Pydantic;
- one invalid output is repaired once;
- 429 and transient server responses retry within the configured budget;
- permanent 4xx errors fail immediately;
- no direct-NIM fallback occurs.

### Realistic system tests

The existing golden charts remain unchanged. A service-level test shall generate a report through a mock orchestrator transport and confirm that immutable evidence, prompt stages, quality validation, and artifact-independent report output remain compatible. Hosted tests remain opt-in. When a hosted NIM worker is configured behind contextual-orchestrator, its credential is supplied by the orchestrator deployment; Four Pillars continues to use `NVIDIA_NIM_API_KEY` only for direct hosted NIM tests.

### Quality gates

Production statement and branch coverage remain exactly 100 percent. Every public production API retains an explanatory docstring. Ruff, compileall, document checks, prompt checks, package builds, container builds, Security Scan, and Semgrep remain required.

## 9. Non-goals

- Replacing the deterministic calculation engine with an LLM.
- Making contextual-orchestrator a mandatory runtime dependency.
- Adding automatic provider fallback.
- Returning orchestration traces through the public Four Pillars API.
- Adding a new database object or modifying the durable job schema.
- Claiming that LLM-as-a-judge is a substitute for deterministic tests or human review.

## 10. Release strategy

The backend is an additive integration capability and shall be released as Four Pillars `v0.6.0` after the feature PR is green and merged. `CHANGELOG.md`, package metadata, runtime/API metadata, distribution artifacts, and the GitHub Release shall use the same version. The existing release workflow must publish the wheel, source distribution, and `SHA256SUMS` without receiving either LLM credential.