# ADR 0002: Direct NVIDIA NIM for LLM generation and evaluation

- **Status:** Superseded for product runtime by ADR 0004
- **Date:** 2026-08-03
- **Historical extension:** ADR 0003
- **Superseded:** 2026-09-01

## Current status note

This ADR preserves the historical reason Four Pillars introduced a direct hosted NVIDIA NIM client. It is no longer the active product-runtime decision. ADR 0004 assigns provider discovery, provider credentials, free-pool eligibility, routing, and provider fallback to Contextual Orchestrator and fixes the repository-owned product route to `orchestrator/free`.

Direct NIM compatibility code may remain temporarily for offline migration tests, but operators must not use this ADR as current deployment guidance.

## Historical context

The product needed structured Korean generation, an independently configurable judge, a hosted model option for development, and a provider contract that could be tested without coupling calendar code to a proprietary SDK. At the time, the project owner required NVIDIA NIM for direct LLM development and hosted tests.

Organization deployments also needed shared routing and usage governance. ADR 0003 later added Contextual Orchestrator as an explicit optional gateway without replacing the direct NVIDIA NIM decision recorded here.

## Historical decision

Use NVIDIA's hosted OpenAI-compatible NIM chat-completions API as the standalone default behind `NimClient`. Generation and evaluation model names were environment configuration. The default pointed to a Nemotron model previously available in the hosted catalog, with operators responsible for selecting an available model.

The client implemented Bearer authentication, timeout, retries for transient errors, JSON-object response mode, Pydantic validation, bounded schema repair, and trace metadata. Direct hosted authentication used `NVIDIA_NIM_API_KEY`.

No silent model-provider fallback was permitted. Offline CI used HTTPX mock transport. Live direct-model tests and NIM-as-judge evaluation were opt-in.

## Historical consequences

The service could change direct NIM models without changing calculation or report schemas. Direct provider outages produced explicit report-job failures while calculation endpoints remained available. Prompt and model versions were recorded for comparison.

ADR 0004 changes the ownership boundary rather than weakening the failure rule: provider failure remains explicit, but Four Pillars no longer owns a provider-native production route.

## Rejected alternatives at the time

- A provider-agnostic automatic fallback was rejected because it hid material behavior and privacy changes.
- Calling NIM directly from API route handlers was rejected because retries, schema repair, tracing, and worker isolation would be duplicated.
- Running live LLM tests on every pull request was rejected because it spent quota, increased flakiness, and risked secrets on forked code.
- Reusing a provider credential as an organization-gateway credential was rejected because the services have different trust, authorization, and incident boundaries.

## Superseding rationale

The direct-provider option duplicated responsibilities already owned by Contextual Orchestrator and allowed the Fortune Interpretation application context to choose infrastructure providers. That violated the current DDD context map and prevented organization-wide enforcement of `orchestrator/free`, centralized routing, usage attribution, and zero-cost fail-closed policy.

See ADR 0004 for the active decision.
