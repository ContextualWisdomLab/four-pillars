# Interpretation Backend Operations

## Provider boundary

Four Pillars supports two explicit interpretation backends:

1. `nvidia_nim` — the standalone default, calling the hosted NVIDIA NIM OpenAI-compatible chat-completions endpoint directly; and
2. `contextual_orchestrator` — an optional organization gateway that provides OpenAI-compatible routing, usage attribution, provider governance, and shared model controls.

A process uses exactly one selected backend. The application never silently routes to another provider or adapter. Calculation-only endpoints remain available without either credential; an AI report job fails clearly when the selected credential or service is unavailable.

`NVIDIA_NIM_API_KEY` remains the only direct hosted NVIDIA NIM credential. `CONTEXTUAL_ORCHESTRATOR_TOKEN` authenticates only the optional gateway. Neither credential is written to traces, artifacts, logs, model prompts, or usage attribution.

## Direct NVIDIA NIM configuration

```env
INTERPRETATION_BACKEND=nvidia_nim
NVIDIA_NIM_API_KEY=nvapi-...
NIM_BASE_URL=https://integrate.api.nvidia.com/v1
NIM_MODEL=nvidia/llama-3.3-nemotron-super-49b-v1.5
NIM_EVAL_MODEL=nvidia/llama-3.3-nemotron-super-49b-v1.5
NIM_TIMEOUT_SECONDS=120
NIM_MAX_RETRIES=3
NIM_MAX_SCHEMA_REPAIRS=1
```

The model values are configuration because hosted catalogs and account entitlements can change. Operators must select a model currently available to the account and record it in deployment configuration. The generated report, trace, and manifest record the actual configured model.

## Contextual Orchestrator configuration

```env
INTERPRETATION_BACKEND=contextual_orchestrator
CONTEXTUAL_ORCHESTRATOR_BASE_URL=https://orchestrator.example.com/v1
CONTEXTUAL_ORCHESTRATOR_TOKEN=...
CONTEXTUAL_ORCHESTRATOR_MODEL=contextual-orchestrator
CONTEXTUAL_ORCHESTRATOR_MODE=auto
CONTEXTUAL_ORCHESTRATOR_TIMEOUT_SECONDS=7200
CONTEXTUAL_ORCHESTRATOR_MAX_RETRIES=3
CONTEXTUAL_ORCHESTRATOR_MAX_SCHEMA_REPAIRS=1
CONTEXTUAL_ORCHESTRATOR_ACCOUNT=
CONTEXTUAL_ORCHESTRATOR_TEAM=fortune-products
CONTEXTUAL_ORCHESTRATOR_GROUP=interpretation
CONTEXTUAL_ORCHESTRATOR_COMPANY=ContextualWisdomLab
```

`CONTEXTUAL_ORCHESTRATOR_TIMEOUT_SECONDS` applies to each gateway HTTP request,
not to the complete multi-stage report job. The default allows two hours per
request; validation permits an explicit value up to four hours.

`CONTEXTUAL_ORCHESTRATOR_MODE` accepts only `auto`, `route`, or `conduct`. `auto` delegates test-time compute allocation to the organization gateway; `route` requests one bounded routed worker; `conduct` requests deeper bounded multi-agent conduct. Four Pillars keeps synchronous delivery because its worker must receive and validate the complete response before it commits a report job. Batch orchestration requires a separately versioned asynchronous job contract.

The example `.env.example` uses loopback HTTP for local development. Production traffic should use TLS, an approved hostname, restricted egress, and a gateway token scoped to inference rather than administration.

The adapter sends the attribution value `service=four-pillars` and adds only configured account, team, group, and company labels. It never adds a subject name, birth value, user note, calculation fingerprint, prompt content, generated text, artifact path, API key, or Bearer token to attribution.

## Request contract

Both clients send `POST /chat/completions` with Bearer authentication, the selected model, system and user messages, and bounded temperature/max tokens. Calculation JSON and user notes are serialized inside an explicit untrusted `<input>` boundary. The model is instructed that user notes are data rather than executable instructions.

Direct NVIDIA NIM additionally receives:

```json
{
  "response_format": {"type": "json_object"}
}
```

Contextual Orchestrator requests instead send:

```json
{
  "mode": "auto",
  "include_orchestration_trace": false,
  "attribution": {
    "service": "four-pillars",
    "company": "ContextualWisdomLab",
    "team": "fortune-products"
  },
  "routing": {
    "channel": "sync",
    "latency_tolerant": false,
    "priority": "normal"
  }
}
```

The orchestrator adapter deliberately omits `response_format`. The organization gateway treats that field, tools, and function-calling fields as provider passthrough triggers because those provider features cannot be merged safely across agents. Sending `response_format` would therefore bypass `auto`, `route`, and `conduct` execution and silently collapse the integration to one upstream model. Four Pillars preserves real orchestration by requesting JSON in the prompt, validating the returned object with Pydantic, and allowing one bounded same-backend repair.

## Reliability

Network failures, timeouts, HTTP 408, HTTP 429, and server errors are retried. `Retry-After` is honored when it contains an integer delay; otherwise exponential delays are capped. Other client errors fail immediately. A response must contain `choices[0].message.content`, parse to one JSON object, and validate against the Pydantic response model. A bounded repair round may request the same complete object with the validation error and JSON Schema. Further failure ends the job.

The two adapters share the same structured-generation transport behavior and return compatible model/attempt/repair traces. They do not share credentials and do not fail over to one another.

## Offline tests

Normal CI uses `httpx.MockTransport` to test headers, endpoint shape, JSON parsing, attribution, compute mode, routing, native JSON-mode separation, schema repair, rate-limit retry, terminal errors, backend selection, and no-fallback behavior without spending model quota or exposing a secret. Run:

```bash
pytest -m 'not nim_live'
```

## Live model tests

Direct NIM live tests are opt-in and skipped when `NVIDIA_NIM_API_KEY` is absent. They verify that the configured hosted model returns valid JSON for a deterministic fixture and that the judge can score a report. Run locally:

```bash
pytest -m nim_live -vv
python scripts/nim_eval.py
```

The repository workflow `nim-eval.yml` runs only through manual dispatch and requires the `NVIDIA_NIM_API_KEY` repository secret. It must not run on contributions from untrusted forks because a prompt could attempt to exfiltrate secrets.

A hosted orchestrator test requires an independently deployed gateway and a separately managed `CONTEXTUAL_ORCHESTRATOR_TOKEN`. Four Pillars does not send `NVIDIA_NIM_API_KEY` to the orchestrator process. The orchestrator may manage its own NVIDIA workers according to organization policy.

## Cost and privacy

Use low temperature and bounded max tokens. Do not send data that the user has not authorized for hosted processing. Four Pillars traces record model name, attempt count, repair count, prompt version, and prompt hash—not raw birth data, personal notes, generated text, or credentials. The orchestrator's own cost ledger may aggregate prompt and completion tokens by prompt-safe organizational dimensions.

Apply retention and deletion to Four Pillars artifacts independently of provider or orchestrator account policies. An organization deployment must document subprocessors, data residency, retention, and incident obligations for every model route selected by the orchestrator.

## Incident response

### Selected backend unavailable

Keep the job failed or queued according to operator policy and continue serving deterministic calculations. Verify the selected backend, base URL, credential, DNS/TLS, route, model availability, and quota. Do not change providers under the same model label and do not add an undocumented fallback.

### Contextual requests unexpectedly use one upstream agent

Inspect the outbound request captured by the adapter contract test. It must include a valid `mode` and must not contain `response_format`, `tools`, `tool_choice`, `functions`, or `function_call`. Any of those provider-feature keys activates the gateway's single-agent passthrough path and is a regression in the integration boundary.

### Schema-valid but unsafe copy increases

Compare model, prompt versions, route, and failed quality findings. Pin the last known prompt/model/route combination, run deterministic and supplementary judge sets, inspect failures manually, and release a reviewed prompt, route, or model-configuration update. Never weaken fingerprint or allowed-pillar checks to increase completion rate.

### Orchestrator attribution or cost anomaly

Confirm that attribution contains only approved organizational labels. Compare the Four Pillars trace model and attempts with the orchestrator usage ledger. Treat missing, duplicated, or misattributed records as an observability incident; do not add personal data to labels as a debugging shortcut.

## Standards and evaluation limits

The applicable software, AI-management, AI-risk, Generative AI, HTTP, tracing, and LLM-judge sources are recorded in `docs/standards/REFERENCES.md` using APA 7th edition entries. `docs/standards/TRACEABILITY.md` maps those sources to code and tests. LLM-as-a-judge results are supplementary because peer-reviewed research reports adversarial and bias vulnerabilities; deterministic tests, rule-based quality gates, security review, and human review remain independent release controls.
