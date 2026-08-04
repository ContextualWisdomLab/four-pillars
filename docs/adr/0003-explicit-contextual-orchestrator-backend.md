# ADR 0003: Explicit Contextual Orchestrator interpretation backend

- **Status:** Accepted
- **Date:** 2026-08-04
- **Decision owners:** Four Pillars maintainers

## Context

Four Pillars was originally complete as a standalone service with deterministic calculation, direct hosted NVIDIA NIM interpretation, quality validation, durable jobs, and file delivery. ContextualWisdomLab also operates `contextual-orchestrator`, an OpenAI-compatible gateway that can centralize routing, usage attribution, provider policy, and shared model governance for multiple products.

Without a checked-in adapter, organization deployments must write custom composition code and duplicate provider controls. Making the gateway mandatory would create the opposite problem: the product would no longer be independently deployable and deterministic calculation users would inherit an unrelated service dependency.

The integration must also preserve the existing rule that an LLM may interpret but may not replace calculated pillars, luck periods, interactions, or evidence fingerprints. Direct hosted NIM credentials use `NVIDIA_NIM_API_KEY`; they must not be repurposed as gateway credentials.

## Decision

Four Pillars will support two explicit built-in interpretation backends:

- `nvidia_nim`, the standalone default; and
- `contextual_orchestrator`, an optional organization gateway.

`Settings.interpretation_backend` is a validated literal. `ReportService` uses `build_report_interpreter(settings)` only when the caller did not inject a `ReportInterpreter`. Therefore settings improve standalone composition without weakening the structural MSA port.

`analysis.py` depends on a runtime-checkable `StructuredGenerationClient` protocol. Both built-in clients use the same OpenAI-compatible JSON transport behavior: Bearer authentication, untrusted-input envelope, `response_format={"type":"json_object"}`, bounded retries, Pydantic validation, and bounded repair.

The orchestrator adapter adds prompt-safe organizational attribution and synchronous routing metadata. Attribution always includes `service=four-pillars`; optional account, team, group, and company values come from deployment settings. Personal data, prompt/report content, fingerprints, paths, and credentials are prohibited from attribution.

No implicit fallback is permitted. A missing token, unavailable gateway, invalid response, or exhausted retry/repair budget fails the selected report job visibly. An operator may change backend configuration only as an explicit deployment change.

## Consequences

### Positive

- The repository remains independently runnable.
- Organization deployments gain shared routing and usage governance without forking calculation or report code.
- Existing custom `ReportInterpreter` adapters remain compatible.
- Backend credentials, traces, and failure behavior are explicit.
- The same deterministic and editorial controls run regardless of provider route.

### Negative

- Two built-in adapters increase the configuration and test surface.
- The shared transport currently preserves the historical `NimTrace` and error names for backward compatibility, even though their behavior is provider-neutral.
- Gateway availability and downstream provider governance become additional organization operational dependencies.
- A gateway may route to providers with different retention or residency terms; deployment owners must document those obligations.

## Rejected alternatives

### Make Contextual Orchestrator mandatory

Rejected because it would break standalone completeness and add a network dependency for deployments that need only direct NIM or deterministic calculation.

### Keep custom integration outside the repository

Rejected because every organization deployment would repeat selection, attribution, retry, schema, privacy, and no-fallback logic.

### Automatically fail over from one backend to another

Rejected because it changes processor, policy, cost, latency, retention, and sometimes model behavior without explicit operator consent. It also makes reproducibility and incident analysis weaker.

### Import Contextual Orchestrator internals as a Python dependency

Rejected because the OpenAI-compatible HTTP contract is the stable service boundary. Reaching into gateway internals would couple release cycles and violate the MSA boundary.

## Verification

- Settings tests prove direct NIM is the default, orchestrator selection is explicit, and unknown values fail validation.
- HTTP mock tests verify endpoint, Bearer token, JSON response mode, attribution, routing, retries, repair, and terminal failures.
- Adapter tests verify immutable calculation objects are forwarded unchanged.
- Modular-service tests verify explicit interpreter injection remains authoritative.
- The complete release gate enforces public docstrings and exactly 100 percent statement and branch coverage.
- `check_docs.py` and `product_gap_audit.py` require the backend and standards contracts every hour.

## Standards relationship

The decision is mapped to ISO/IEC 25010:2023 compatibility, reliability, security, maintainability, and flexibility concerns; ISO/IEC 42001:2023 management controls; ISO/IEC 23894:2023 and NIST AI RMF risk controls; and NIST AI 600-1 Generative AI controls. Full APA 7th references and limitations appear in `docs/standards/REFERENCES.md` and `docs/standards/TRACEABILITY.md`. This ADR is not a certification or scientific validation of traditional interpretation.