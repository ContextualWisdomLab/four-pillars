# Model Orchestration Operations

## Product boundary

Four Pillars owns deterministic calendar calculations, interpretation intent, structured report schemas, evidence validation, report quality rules, and artifact publication. It does **not** own model-provider discovery or provider routing.

All product-owned LLM work crosses the Model Orchestration anti-corruption layer through Contextual Orchestrator. The product runtime accepts only:

```env
INTERPRETATION_BACKEND=contextual_orchestrator
CONTEXTUAL_ORCHESTRATOR_BASE_URL=https://orchestrator.example.com/v1
CONTEXTUAL_ORCHESTRATOR_TOKEN=...
CONTEXTUAL_ORCHESTRATOR_MODEL=orchestrator/free
CONTEXTUAL_ORCHESTRATOR_MODE=auto
CONTEXTUAL_ORCHESTRATOR_TIMEOUT_SECONDS=120
CONTEXTUAL_ORCHESTRATOR_MAX_RETRIES=3
CONTEXTUAL_ORCHESTRATOR_MAX_SCHEMA_REPAIRS=1
CONTEXTUAL_ORCHESTRATOR_ACCOUNT=
CONTEXTUAL_ORCHESTRATOR_TEAM=fortune-products
CONTEXTUAL_ORCHESTRATOR_GROUP=interpretation
CONTEXTUAL_ORCHESTRATOR_COMPANY=ContextualWisdomLab
```

`orchestrator/free` is the required virtual model for this product. Provider discovery, free-pool eligibility, failover within that pool, and provider credentials belong to Contextual Orchestrator. Four Pillars never silently routes around the gateway to a provider-native client.

Calculation-only endpoints remain available without an orchestration credential. A report job fails clearly when the gateway credential, route, or service is unavailable.

## DDD context map

```text
Deterministic Calculation domain
        |
        v
Fortune Interpretation application context
  - use case
  - immutable evidence
  - report schema
  - quality rules
        |
        | ReportInterpreter port
        v
Model Orchestration ACL
  - ContextualOrchestratorReportInterpreter
  - ContextualOrchestratorClient
        |
        v
Contextual Orchestrator bounded context
  - model/provider discovery
  - orchestrator/free eligibility
  - routing/fallback
  - usage attribution
  - test-time compute allocation
```

A caller-owned MSA may still inject a different `ReportInterpreter` implementation. That is an external composition decision; this repository's composition root does not instantiate a direct-provider interpreter.

## Request contract

The client calls the gateway's OpenAI-compatible `/chat/completions` endpoint with Bearer authentication, the fixed model `orchestrator/free`, system/user messages, bounded temperature and max tokens, and prompt-safe attribution.

Calculation JSON and user notes are serialized inside an explicit untrusted `<input>` boundary. User content cannot alter routing, credentials, tool policy, or system instructions.

The request includes orchestration metadata similar to:

```json
{
  "model": "orchestrator/free",
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

The adapter deliberately omits provider passthrough fields such as `response_format`, tools, and function-calling controls. Those fields can collapse an orchestrated request to a single upstream provider path. JSON correctness is instead enforced by prompt contract, Pydantic validation, and one bounded same-route repair.

## Reliability and fail-closed behavior

Timeouts, transport failures, HTTP 408/429, and server errors are retried within the configured budget. Other client errors fail immediately. A response must contain `choices[0].message.content`, parse to one JSON object, and validate against the requested Pydantic model.

A schema-invalid response may receive one bounded repair request through the same `orchestrator/free` route. Exhausted retries or repairs fail the report job. They never cause a provider-native fallback.

`CONTEXTUAL_ORCHESTRATOR_MODE` accepts `auto`, `route`, or `conduct`. These values change orchestration depth, not the cost pool. The virtual model remains `orchestrator/free` in every mode.

## Privacy and attribution

The adapter always supplies `service=four-pillars` and adds only configured account, team, group, and company dimensions. Do not place subject name, birth data, user notes, prompt text, generated text, artifact paths, API credentials, or Bearer tokens in attribution.

Four Pillars traces may record the virtual model identifier, attempt count, repair count, prompt version, and prompt digest. Provider selection and provider-level cost details belong to the orchestration system's own audit and usage ledgers.

Production deployments must use TLS or an explicitly controlled loopback path, approved egress, an inference-scoped gateway token, documented retention, and documented subprocessors/data-residency policy.

## Offline contract tests

Normal CI uses `httpx.MockTransport` and must prove:

- the outbound model is exactly `orchestrator/free`;
- `nvidia_nim`, `orchestrator/auto`, and arbitrary model identifiers are rejected as product runtime configuration;
- attribution contains only approved dimensions;
- transient retry does not alter the virtual route;
- provider-passthrough fields are absent;
- malformed output fails closed after bounded repair;
- the default `ReportService` composition resolves to the Contextual Orchestrator adapter.

Run the normal test suite without a live credential:

```bash
pytest -m 'not orchestrator_live'
```

## Live `orchestrator/free` test

Live testing is opt-in. It requires an independently deployed Contextual Orchestrator gateway, `CONTEXTUAL_ORCHESTRATOR_TOKEN`, and a configured `CONTEXTUAL_ORCHESTRATOR_BASE_URL`. It does not require any provider-native secret in this repository.

```bash
pytest -m orchestrator_live -vv
python scripts/orchestrator_eval.py
```

The manual workflow must fail closed when gateway configuration is missing. It must not receive NVIDIA, OpenAI, OpenRouter, Bytez, or other provider credentials.

## Incident response

### Gateway unavailable

Keep the report job failed or queued according to operator policy and continue serving deterministic calculations. Check gateway DNS/TLS, token scope, `/v1/chat/completions`, `orchestrator/free` pool health, orchestration mode, and worker capacity. Do not add a local direct-provider fallback.

### Request unexpectedly uses one upstream agent

Capture the outbound request in the adapter contract test. Confirm the virtual model remains `orchestrator/free` and provider-passthrough keys are absent. Treat a regression that bypasses orchestration as an architecture-boundary defect.

### Free pool has no eligible model

Fail the LLM-backed operation explicitly. `orchestrator/free` must not roll into a paid route merely to increase availability. The orchestration repository owns remediation of discovery/free-eligibility defects.

### Schema-valid but unsafe copy increases

Compare prompt versions, orchestration mode, route evidence, and deterministic quality findings. Never weaken calculation fingerprint checks or allowed-pillar validation to improve completion rate.

## Superseded provider-specific path

Historical direct-NVIDIA decisions remain in ADR 0002/0003 for traceability. ADR 0004 supersedes their product-runtime selection. Provider-native compatibility code that still exists in the source tree is transitional test infrastructure and is not an operator-visible product path.
