# Contextual Orchestrator Backend Implementation Plan

> **For agentic workers:** Use the Superpowers TDD, systematic-debugging, review, and verification workflow. Execute tasks in order and merge only an exact reviewed green head.

**Goal:** Add an optional Contextual Orchestrator interpretation backend while preserving direct NVIDIA NIM as the standalone default, immutable calculation evidence, strict report schemas, and complete standards traceability.

**Architecture:** Introduce a structural structured-generation client protocol, implement an OpenAI-compatible organization-gateway client and report-interpreter adapter, and select the adapter through validated Pydantic settings only when no custom interpreter is injected. Deterministic calculations, prompts, report schemas, quality gates, queues, artifacts, and repository ports remain unchanged.

**Tech stack:** Python 3.11/3.12, Pydantic 2, Pydantic Settings 2, HTTPX, FastAPI, Contextual Orchestrator, NVIDIA NIM, pytest, pytest-cov, Ruff, Docker, and GitHub Actions.

## Global constraints

- `NVIDIA_NIM_API_KEY` remains the only direct hosted NVIDIA NIM credential.
- `CONTEXTUAL_ORCHESTRATOR_TOKEN` authenticates only the optional organization gateway.
- No backend silently falls back to another provider or adapter.
- Remote credential-bearing endpoints use HTTPS; cleartext HTTP is restricted to explicit loopback hosts.
- Statement and branch coverage remain exactly 100 percent.
- Every public production API has a complete docstring.
- Database objects retain two-or-more-word naming; this feature adds no database object.
- Direct NIM remains the default standalone behavior.
- Traditional interpretation is not represented as scientific prediction.
- Standards and research references use APA 7th edition entries and explicit application notes.
- Contextual Orchestrator must execute `auto`, `route`, or `conduct`; provider-passthrough fields must not silently bypass orchestration.

---

## Task 1: Lock backend selection and wire contracts

**Files**

- Create `tests/test_contextual_orchestrator.py`.
- Modify `tests/test_modular_service_ports.py`.
- Modify `tests/test_nim.py`.

**Interfaces**

- Consume existing `Settings`, `NimClient`, `ReportService`, and `ReportInterpreter` behavior.
- Produce failing contracts for `ContextualOrchestratorClient`, `ContextualOrchestratorReportInterpreter`, and `build_report_interpreter(settings)`.

### Steps

1. Require the default backend to build `NimReportInterpreter`.
2. Require explicit `contextual_orchestrator` selection to build `ContextualOrchestratorReportInterpreter`.
3. Require an unknown backend or compute mode to fail Pydantic validation.
4. Use `httpx.MockTransport` to require the organization request contract:

   ```python
   assert request.url.path == "/v1/chat/completions"
   assert request.headers["Authorization"] == "Bearer orchestrator-test-token"
   assert body["model"] == "contextual-orchestrator"
   assert body["mode"] in {"auto", "route", "conduct"}
   assert body["include_orchestration_trace"] is False
   assert "response_format" not in body
   assert body["attribution"]["service"] == "four-pillars"
   assert body["routing"] == {
       "channel": "sync",
       "latency_tolerant": False,
       "priority": "normal",
   }
   ```

5. Keep the direct NIM contract requiring `response_format={"type":"json_object"}`.
6. Require missing-token failure, one schema repair, transient 429 retry, permanent 400 failure, and explicit proof that direct NIM is not invoked as fallback.
7. Run focused tests and record RED before production implementation.

## Task 2: Add the structural generation boundary

**Files**

- Create `src/four_pillars/generation.py`.
- Modify `src/four_pillars/analysis.py`.
- Test with `tests/test_contextual_orchestrator.py`.

**Interfaces**

- Produce runtime-checkable `StructuredGenerationClient`.
- Consume the provider-neutral `GenerationTrace` and Pydantic response-model contract.

### Protocol

```python
@runtime_checkable
class StructuredGenerationClient(Protocol):
    async def generate(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        response_model: type[T],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> tuple[T, GenerationTrace]: ...
```

Every public symbol receives a complete docstring. `analysis.py` depends on this protocol rather than a provider-specific client. Staging, prompts, schemas, deterministic evidence, editorial repair, and trace persistence remain unchanged.

## Task 3: Implement the Contextual Orchestrator client

**Files**

- Create `src/four_pillars/contextual_orchestrator.py`.
- Modify `src/four_pillars/settings.py`.
- Test with `tests/test_contextual_orchestrator.py` and `tests/test_backend_url_security.py`.

**Interfaces**

- Produce `ContextualOrchestratorClient`, `ContextualOrchestratorError`, and `ContextualOrchestratorSchemaError`.
- Consume `Settings`, `GenerationTrace`, Pydantic schemas, and the gateway's OpenAI-compatible endpoint.

### Steps

1. Add validated settings for backend, base URL, token, model, `auto|route|conduct` mode, timeout, retry/repair budgets, and prompt-safe attribution labels.
2. Require HTTPS for remote model endpoints and allow HTTP only on `localhost`, `127.0.0.1`, or `::1`.
3. Construct an `httpx.AsyncClient` with Bearer authentication, bounded timeout, and an optional test transport.
4. Retry network failures, HTTP 408, HTTP 429, and server errors; honor integer `Retry-After`; fail other client errors immediately.
5. Build the same untrusted input envelope used by direct NIM.
6. Add `mode`, synchronous routing metadata, and prompt-safe attribution.
7. Deliberately omit `response_format`, tools, and function-calling fields because the gateway treats those provider features as single-agent passthrough triggers.
8. Require one JSON object through explicit prompting, Pydantic validation, and at most the configured same-backend repair turns.
9. Preserve direct NIM native JSON mode and prove the two wire contracts independently.

## Task 4: Add interpretation adapter and settings factory

**Files**

- Modify `src/four_pillars/adapters.py`.
- Modify `src/four_pillars/service.py`.
- Modify `src/four_pillars/ports.py` only if the structural contract requires it.
- Test `tests/test_interpretation_backend.py`, `tests/test_modular_service_ports.py`, and service tests.

### Steps

1. Open one `ContextualOrchestratorClient` per report-generation operation.
2. Call `generate_report` with unchanged deterministic evidence.
3. Implement `build_report_interpreter(settings) -> ReportInterpreter` for exactly the two validated built-in values.
4. Use the factory only when no `ReportInterpreter` was injected.
5. Prove explicit MSA adapter injection remains authoritative.

## Task 5: Add APA 7 standards and research traceability

**Files**

- Create `docs/standards/REFERENCES.md`.
- Create `docs/standards/TRACEABILITY.md`.
- Modify product, technical, API, modularity, operations, architecture, security, README, and environment documentation.
- Strengthen `scripts/check_docs.py`, `scripts/product_gap_audit.py`, and hourly-loop tests.

### Steps

1. Add full APA 7 entries, stable URLs or DOIs, applicability, and limitations for ISO/IEC 25010:2023, ISO/IEC 42001:2023, ISO/IEC 23894:2023, NIST AI RMF 1.0, NIST AI 600-1, RFC 9457, W3C Trace Context, and peer-reviewed LLM-judge robustness and bias work.
2. Map standards concepts to calculation immutability, schema validation, quality gates, prompt traces, privacy redaction, MSA ports, retries, scheduled review, and coverage.
3. State explicitly that the mapping is neither ISO certification nor scientific validation of traditional interpretation.
4. Require every interpretation and standards contract token in the hourly offline audit.
5. Test every contract entry independently for both missing-file and missing-token failure.

## Task 6: Complete review findings and operational hardening

1. Review every CodeRabbit, security, Semgrep, and human thread against current code.
2. Require secure model endpoint validation before a Bearer request can be constructed.
3. Update stuck-job recovery so a replacement request uses a fresh `Idempotency-Key` only after ownership is cleared; never replay the stranded key accidentally.
4. Keep local loopback examples separate from production TLS examples.
5. Correct all historical provider-specific `NimTrace` references to `GenerationTrace` at the structural port.
6. Resolve a thread only after the corresponding exact-head tests pass.

## Task 7: Complete full verification, merge, and release follow-up

### Full gate

```bash
python -m pip check
python scripts/product_gap_audit.py
ruff check .
python -m compileall -q src tests scripts
python scripts/check_docs.py
python scripts/check_prompts.py
pytest -m 'not nim_live' -W error::ResourceWarning --cov=four_pillars --cov-report=term-missing
python -m build --no-isolation
docker build --tag four-pillars:contextual-orchestrator .
```

Expected result: every command succeeds on Python 3.11 and 3.12 with exactly 100 percent statement and branch coverage.

### Merge rules

- Inspect the complete diff, issue comments, reviews, code-scanning findings, and inline threads.
- Require zero unresolved actionable threads.
- Require CI, container, Security Scan, and Semgrep success on the same head.
- Squash merge with an expected-head guard.
- Do not release from an unverified head.

### Release relationship

Four Pillars v0.6.0 was released independently for the Figma-backed browser-history feature. This integration remains under `Unreleased` until it is merged and intentionally versioned in a subsequent release. It must not retarget or overwrite the existing v0.6.0 tag or assets.
