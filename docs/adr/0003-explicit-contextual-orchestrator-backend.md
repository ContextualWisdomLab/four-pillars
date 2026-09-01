# ADR 0003: Explicit Contextual Orchestrator interpretation backend

- **Status:** Superseded for product runtime by ADR 0004
- **Date:** 2026-08-04
- **Decision owners:** Four Pillars maintainers
- **Superseded:** 2026-09-01

## Current status note

This ADR records the intermediate architecture in which Four Pillars supported both a direct NVIDIA NIM backend and an optional Contextual Orchestrator backend. ADR 0004 supersedes that runtime-selection decision: the repository-owned product composition now uses Contextual Orchestrator only and fixes the virtual model to `orchestrator/free`.

The structural lessons in this ADR remain valid: deterministic evidence cannot be replaced by an LLM, the gateway is an HTTP service boundary rather than an imported implementation, prompt-safe attribution is required, provider passthrough fields can defeat route/conduct orchestration, and failures must not trigger an implicit provider change.

## Historical context

Four Pillars was originally complete as a standalone service with deterministic calculation, direct hosted NVIDIA NIM interpretation, quality validation, durable jobs, and file delivery. ContextualWisdomLab also operated `contextual-orchestrator`, an OpenAI-compatible gateway able to centralize routing, usage attribution, provider policy, and shared model governance for multiple products.

The integration had to preserve the rule that an LLM may interpret but may not replace calculated pillars, luck periods, interactions, or evidence fingerprints. It also had to keep provider credentials distinct from gateway credentials.

A further protocol constraint was identified: `response_format`, tools, and function-calling fields could select a one-agent provider-passthrough path, defeating the route/conduct behavior expected from the gateway.

## Historical decision

The repository supported two explicit built-in interpretation backends:

- `nvidia_nim`, then the standalone default; and
- `contextual_orchestrator`, then an optional organization gateway.

`analysis.py` depended on the runtime-checkable `StructuredGenerationClient` protocol. The orchestrator client omitted provider passthrough fields, sent a validated `auto`, `route`, or `conduct` mode, requested synchronous delivery, and relied on explicit JSON prompting plus Four Pillars Pydantic validation.

The orchestrator adapter added prompt-safe organizational attribution. Attribution always included `service=four-pillars`; optional account, team, group, and company values came from deployment settings. Personal data, prompt/report content, fingerprints, paths, and credentials were prohibited.

No implicit fallback was permitted. A missing token, unavailable gateway, invalid response, or exhausted retry/repair budget failed the selected report job visibly.

## What ADR 0004 changes

ADR 0004 removes the repository-owned provider choice. The product now treats Model Orchestration as a separate bounded context and integrates through an anti-corruption layer:

```text
Fortune Interpretation
  -> ReportInterpreter port
  -> Contextual Orchestrator ACL
  -> orchestrator/free
```

As a result:

- `Settings.interpretation_backend` accepts only `contextual_orchestrator`;
- the repository-owned virtual model is `orchestrator/free`;
- direct-provider credentials are not operator-facing product configuration;
- an empty free pool fails closed instead of crossing to a paid or local provider route;
- a caller may still inject a different `ReportInterpreter` when that caller owns the integration boundary;
- provider-specific transport code remaining in `nim.py` is transitional compatibility infrastructure, not an active product route.

## Preserved consequences

- Deterministic calculation remains available during gateway/model outages.
- Existing custom `ReportInterpreter` adapters remain compatible.
- Structured output is enforced after generation rather than with provider-native passthrough fields.
- Gateway availability, retention, residency, and downstream provider governance remain deployment concerns of the orchestration boundary.
- Prompt versions, virtual model, attempts, repairs, and calculation fingerprints remain traceable in Four Pillars evidence.

## Rejected alternatives that remain rejected

### Send `response_format` through Contextual Orchestrator

Rejected because it can select a single-agent passthrough path. Four Pillars keeps explicit prompting, Pydantic validation, and bounded same-route repair.

### Automatically fail over around the gateway

Rejected because it changes processor, policy, cost, retention, and model behavior without an explicit orchestration decision. Under ADR 0004, this also violates bounded-context ownership.

### Import Contextual Orchestrator internals as a Python dependency

Rejected because the OpenAI-compatible HTTP contract is the service boundary. Reaching into gateway internals would couple release cycles and violate the MSA boundary.

## Verification transition

Historical verification included direct NIM default-selection and live-provider tests. The active ADR 0004 verification instead requires:

- product settings reject `nvidia_nim` and unknown backend values;
- product settings reject any virtual model other than `orchestrator/free`;
- outbound gateway requests prove `model=orchestrator/free`;
- transient retry and schema repair remain on the same virtual route;
- provider passthrough fields are absent;
- default `ReportService` composition resolves to the Contextual Orchestrator adapter;
- the live workflow receives only `CONTEXTUAL_ORCHESTRATOR_TOKEN` and the gateway URL;
- the architecture-fitness audit fails if direct-provider runtime configuration reappears.

## Standards relationship

The decision history and its superseding control remain mapped to ISO/IEC 25010:2023 compatibility, reliability, security, maintainability, and flexibility concerns; ISO/IEC 42001:2023 management controls; ISO/IEC 23894:2023 and NIST AI RMF risk controls; and NIST AI 600-1 Generative AI controls. Full APA 7th references and limitations appear in `docs/standards/REFERENCES.md` and `docs/standards/TRACEABILITY.md`.
