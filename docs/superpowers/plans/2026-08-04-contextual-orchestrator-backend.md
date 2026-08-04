# Contextual Orchestrator Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an optional Contextual Orchestrator interpretation backend while preserving direct NVIDIA NIM as the standalone default and publishing complete standards traceability.

**Architecture:** Introduce a structural structured-generation client protocol, implement an OpenAI-compatible orchestrator client and report-interpreter adapter, and select the adapter through validated Pydantic settings only when no custom interpreter is injected. Deterministic calculations, prompts, report schemas, quality gates, queues, artifacts, and repository ports remain unchanged. Add APA 7th standards documentation and make the hourly product loop detect missing traceability.

**Tech Stack:** Python 3.11/3.12, Pydantic 2, Pydantic Settings 2, HTTPX, FastAPI, contextual-orchestrator OpenAI-compatible API, NVIDIA NIM, pytest, pytest-cov, Ruff, GitHub Actions.

## Global Constraints

- `NVIDIA_NIM_API_KEY` remains the only direct hosted NVIDIA NIM credential.
- `CONTEXTUAL_ORCHESTRATOR_TOKEN` authenticates only the optional orchestrator backend.
- No backend silently falls back to another provider or adapter.
- Statement and branch coverage remain exactly 100 percent.
- Every public production API has a complete docstring.
- Database objects retain two-or-more-word naming; this feature adds no database object.
- Direct NIM remains the default standalone behavior.
- Traditional interpretation is not represented as scientific prediction.
- Standards and research references use APA 7th edition entries and explicit application notes.

---

### Task 1: Lock backend selection and request contracts

**Files:**
- Create: `tests/test_contextual_orchestrator.py`
- Modify: `tests/test_modular_service_ports.py`
- Modify: `tests/test_nim.py`

**Interfaces:**
- Consumes: existing `Settings`, `NimClient`, `ReportService`, and `ReportInterpreter` behavior.
- Produces: failing contracts for `ContextualOrchestratorClient`, `ContextualOrchestratorReportInterpreter`, and `build_report_interpreter(settings)`.

- [ ] **Step 1: Add settings and factory RED tests**

Require the default backend to build `NimReportInterpreter`, explicit `contextual_orchestrator` to build `ContextualOrchestratorReportInterpreter`, and an unknown backend to raise Pydantic validation error.

- [ ] **Step 2: Add HTTP contract RED tests**

Use `httpx.MockTransport` to require:

```python
assert request.url.path == "/v1/chat/completions"
assert request.headers["Authorization"] == "Bearer orchestrator-test-token"
assert body["model"] == "contextual-orchestrator"
assert body["response_format"] == {"type": "json_object"}
assert body["attribution"]["service"] == "four-pillars"
assert body["routing"] == {"channel": "sync", "latency_tolerant": False, "priority": "normal"}
```

- [ ] **Step 3: Add failure and repair RED tests**

Require missing token failure, one schema repair, transient 429 retry, permanent 400 failure, and explicit proof that the direct NIM client is not invoked.

- [ ] **Step 4: Run focused tests and record RED**

Run:

```bash
pytest tests/test_contextual_orchestrator.py tests/test_modular_service_ports.py tests/test_nim.py -v
```

Expected: collection or import failures because the new client, settings fields, adapter, and factory do not exist.

- [ ] **Step 5: Commit RED contracts**

```bash
git add tests/test_contextual_orchestrator.py tests/test_modular_service_ports.py tests/test_nim.py
git commit -m "test: require contextual orchestrator backend"
```

### Task 2: Add the structural generation boundary

**Files:**
- Create: `src/four_pillars/generation.py`
- Modify: `src/four_pillars/analysis.py`
- Test: `tests/test_contextual_orchestrator.py`

**Interfaces:**
- Produces: runtime-checkable `StructuredGenerationClient` protocol.
- Consumes: existing `NimTrace` and Pydantic response model contract.

- [ ] **Step 1: Define the protocol**

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
    ) -> tuple[T, NimTrace]: ...
```

Every public symbol receives a complete docstring. Protocol declarations raise `NotImplementedError` with the existing coverage exclusion convention.

- [ ] **Step 2: Depend on the protocol in `analysis.py`**

Change `generate_report(client: NimClient, ...)` to `generate_report(client: StructuredGenerationClient, ...)`; do not change staging, prompts, schemas, repair behavior, or traces.

- [ ] **Step 3: Run focused analysis and protocol tests**

```bash
pytest tests/test_analysis.py tests/test_modular_service_ports.py tests/test_contextual_orchestrator.py -v
```

- [ ] **Step 4: Commit**

```bash
git add src/four_pillars/generation.py src/four_pillars/analysis.py tests
git commit -m "refactor: define structured generation port"
```

### Task 3: Implement the Contextual Orchestrator client

**Files:**
- Create: `src/four_pillars/contextual_orchestrator.py`
- Modify: `src/four_pillars/settings.py`
- Test: `tests/test_contextual_orchestrator.py`

**Interfaces:**
- Produces: `ContextualOrchestratorClient`, `ContextualOrchestratorError`, and `ContextualOrchestratorSchemaError`.
- Consumes: `Settings`, `NimTrace`, Pydantic model schemas, and the orchestrator's OpenAI-compatible endpoint.

- [ ] **Step 1: Add validated settings**

Use `Literal["nvidia_nim", "contextual_orchestrator"]` and bounded `Field` values. Define the base URL, token, model, timeout, retry/repair budgets, and attribution labels. Keep credentials optional at load time.

- [ ] **Step 2: Implement client lifecycle and transport**

Construct an `httpx.AsyncClient` with Bearer authentication, bounded timeout, optional test transport, and a normalized base URL. Missing token raises `ContextualOrchestratorError` when the client is constructed.

- [ ] **Step 3: Implement bounded retries**

Retry network failures, HTTP 408, HTTP 429, and server errors. Honor integer `Retry-After`; otherwise use bounded exponential delay. Fail other 4xx responses immediately with at most 500 response characters.

- [ ] **Step 4: Implement structured generation and repair**

Build the same untrusted input envelope used by `NimClient`. Add orchestrator attribution and routing fields. Validate exactly one JSON object through the requested Pydantic model. On failure, include the model JSON Schema in at most the configured number of repair turns.

- [ ] **Step 5: Run focused client tests**

```bash
pytest tests/test_contextual_orchestrator.py -v
```

Expected: all client, retry, repair, authentication, and no-fallback tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/four_pillars/contextual_orchestrator.py src/four_pillars/settings.py tests/test_contextual_orchestrator.py
git commit -m "feat: add contextual orchestrator client"
```

### Task 4: Add interpretation adapter and settings factory

**Files:**
- Modify: `src/four_pillars/adapters.py`
- Modify: `src/four_pillars/service.py`
- Modify: `src/four_pillars/ports.py`
- Test: `tests/test_modular_service_ports.py`
- Test: `tests/test_service.py`

**Interfaces:**
- Produces: `ContextualOrchestratorReportInterpreter` and `build_report_interpreter(settings) -> ReportInterpreter`.
- Preserves: injected custom `ReportInterpreter` and all repository/publisher ports.

- [ ] **Step 1: Implement the orchestrator adapter**

Open one `ContextualOrchestratorClient` per report-generation operation and call `generate_report` with unchanged deterministic evidence.

- [ ] **Step 2: Implement the adapter factory**

```python
def build_report_interpreter(settings: Settings) -> ReportInterpreter:
    if settings.interpretation_backend == "nvidia_nim":
        return NimReportInterpreter(settings)
    return ContextualOrchestratorReportInterpreter(settings)
```

The `Literal` setting makes any third branch unreachable; tests cover both valid values.

- [ ] **Step 3: Use the factory only for standalone defaults**

Change `ReportService` to call `build_report_interpreter(settings)` only when `interpreter is None`. Do not change explicit injection.

- [ ] **Step 4: Verify service compatibility**

```bash
pytest tests/test_modular_service_ports.py tests/test_service.py tests/test_service_errors.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/four_pillars/adapters.py src/four_pillars/service.py src/four_pillars/ports.py tests
git commit -m "feat: select interpretation backend by settings"
```

### Task 5: Add APA 7 standards and research traceability

**Files:**
- Create: `docs/standards/REFERENCES.md`
- Create: `docs/standards/TRACEABILITY.md`
- Modify: `docs/technical/TRD.md`
- Modify: `docs/technical/MODULARITY.md`
- Modify: `docs/operations/NIM.md`
- Modify: `docs/operations/RUNBOOK.md`
- Modify: `README.md`
- Modify: `.env.example`
- Modify: `scripts/check_docs.py`
- Modify: `scripts/product_gap_audit.py`
- Test: `tests/test_hourly_product_loop.py`

**Interfaces:**
- Produces: a publishable APA 7 reference catalog and code/test/workflow control mapping.
- Consumes: ISO, NIST, IETF, W3C, ACL Anthology, and current Pydantic Settings guidance.

- [ ] **Step 1: Write `REFERENCES.md`**

Include full APA 7 entries, stable URLs or DOIs, applicability, and limitation notes. Cite ISO/IEC 25010:2023, ISO/IEC 42001:2023, ISO/IEC 23894:2023, NIST AI RMF 1.0, NIST AI 600-1, RFC 9457, W3C Trace Context, and peer-reviewed 2024 LLM-judge robustness/bias work.

- [ ] **Step 2: Write `TRACEABILITY.md`**

Map standards clauses or concepts to calculation immutability, schema validation, quality gates, prompt traces, privacy redaction, MSA ports, retries, scheduled review, coverage, and explicit external gaps. State that traditional interpretation is not scientific prediction.

- [ ] **Step 3: Update operator and technical documents**

Document both backends, environment variables, deployment examples, no-fallback behavior, orchestrator attribution, and local-versus-production TLS requirements.

- [ ] **Step 4: Strengthen scheduled document audits**

Require the two standards documents in `check_docs.py` and `product_gap_audit.py`. Require canonical tokens such as `ISO/IEC 25010:2023`, `ISO/IEC 42001:2023`, `NIST AI 600-1`, `RFC 9457`, `APA 7th`, and `ContextualOrchestratorClient`.

- [ ] **Step 5: Run document and hourly-loop tests**

```bash
python scripts/check_docs.py
python scripts/product_gap_audit.py
pytest tests/test_hourly_product_loop.py -v
```

- [ ] **Step 6: Commit**

```bash
git add .env.example README.md docs scripts tests/test_hourly_product_loop.py
git commit -m "docs: add AI standards traceability"
```

### Task 6: Complete full verification, review, and merge

**Files:**
- Modify: `CHANGELOG.md`
- Verify: all changed production, test, documentation, and workflow files.

**Interfaces:**
- Produces: one mergeable feature PR with an exact green head.

- [ ] **Step 1: Add Unreleased notes**

Document the optional orchestrator backend, settings, attribution, no-fallback boundary, standards doctoring, and scheduled regression checks. Do not advance the package version in the feature PR.

- [ ] **Step 2: Run the complete release-quality gate**

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

Expected: every command succeeds with exactly 100 percent statement and branch coverage.

- [ ] **Step 3: Review the complete diff**

Inspect every changed file, PR issue comment, review submission, inline thread, Security Scan finding, and Semgrep result. Correct every actionable finding and rerun all required gates on the exact final head.

- [ ] **Step 4: Merge with an expected-head guard**

Use squash merge only after Python 3.11, Python 3.12, container, Security Scan, Semgrep, and review-thread checks succeed on the same head.

### Task 7: Release Four Pillars v0.6.0

**Files:**
- Modify: `pyproject.toml`
- Modify: `src/four_pillars/version.py`
- Modify: `CHANGELOG.md`
- Modify: `tests/test_release_version.py`
- Create: `docs/superpowers/plans/2026-08-04-v0.6.0-release.md`

**Interfaces:**
- Produces: package/runtime/API version `0.6.0`, curated changelog section, wheel, source distribution, `SHA256SUMS`, and GitHub Release.

- [ ] **Step 1: Change the release test to require `0.6.0`**

Require the dated changelog section and core capabilities `contextual-orchestrator`, `StructuredGenerationClient`, `APA 7th`, `100% statement and branch coverage`, and `NVIDIA_NIM_API_KEY`.

- [ ] **Step 2: Record RED**

```bash
pytest tests/test_release_version.py -v
```

Expected: package/runtime/API remain `0.5.0` and the dated v0.6.0 section is missing.

- [ ] **Step 3: Align package, runtime, API, and changelog**

Set both version surfaces to `0.6.0`, move the integration notes from Unreleased into `## [0.6.0] - 2026-08-04`, retain planned items under Unreleased, and update comparison links.

- [ ] **Step 4: Run every release gate and review**

Repeat the complete Task 6 gate, build `four_pillars-0.6.0.tar.gz` and `four_pillars-0.6.0-py3-none-any.whl`, inspect every review and security finding, and merge only the exact green head.

- [ ] **Step 5: Verify publication and convergence**

Confirm `main` exposes `0.6.0`, tag `v0.6.0` targets the merged release commit, release assets include wheel, source distribution, and `SHA256SUMS`, and the repository has zero open PRs.