# ADR 0002: Direct NVIDIA NIM for LLM generation and evaluation

- **Status:** Accepted; extended by ADR 0003
- **Date:** 2026-08-03

## Context

The product needs structured Korean generation, an independently configurable judge, a hosted model option for development, and a provider contract that can be tested without coupling calendar code to a proprietary SDK. The project owner requires NVIDIA NIM for direct LLM development and hosted tests.

Organization deployments also need shared routing and usage governance. ADR 0003 adds Contextual Orchestrator as an explicit optional gateway without replacing the direct NVIDIA NIM decision recorded here.

## Decision

Use NVIDIA's hosted OpenAI-compatible NIM chat-completions API as the standalone default behind `NimClient`. Generation and evaluation model names are environment configuration. The default points to a Nemotron model previously available in the hosted catalog, but operators must select a model currently available to their account.

The client implements Bearer authentication, timeout, retries for transient errors, JSON-object response mode, Pydantic validation, bounded schema repair, and trace metadata. Direct hosted authentication uses only `NVIDIA_NIM_API_KEY`.

No silent model-provider fallback is permitted. Offline CI uses HTTPX mock transport. Live direct-model tests and NIM-as-judge evaluation are opt-in, require `NVIDIA_NIM_API_KEY`, and must not run with secrets on untrusted fork pull requests.

## Consequences

The service can change direct NIM models without changing calculation or report schemas. Direct provider outages produce explicit report-job failures while calculation endpoints remain available. Prompt and model versions must be recorded for comparison. Operators are responsible for model availability, quota, hosted-data policy, and secret management.

When `INTERPRETATION_BACKEND=contextual_orchestrator`, Four Pillars does not use the direct NIM credential or client for report generation. The organization gateway manages its own downstream providers and credentials under ADR 0003.

## Rejected alternatives

- A provider-agnostic automatic fallback was rejected because it hides a material behavior and privacy change.
- Calling NIM directly from API route handlers was rejected because retries, schema repair, tracing, and worker isolation would be duplicated.
- Running live LLM tests on every pull request was rejected because it spends quota, increases flakiness, and risks secrets on forked code.
- Reusing `NVIDIA_NIM_API_KEY` as an organization-gateway credential was rejected because the two services have different trust, authorization, and incident boundaries.
