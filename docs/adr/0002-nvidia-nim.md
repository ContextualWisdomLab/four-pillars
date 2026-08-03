# ADR 0002: NVIDIA NIM for LLM generation and evaluation

- Status: Accepted
- Date: 2026-08-03

## Context

The product needs structured Korean generation, an independently configurable judge, a hosted free-model option for development, and a provider contract that can be tested without coupling calendar code to a proprietary SDK. The project owner requires NVIDIA NIM for LLM development and tests.

## Decision

Use NVIDIA's hosted OpenAI-compatible NIM chat-completions API behind a small `NimClient`. Generation and evaluation model names are environment configuration. The default points to a Nemotron model previously available in the free hosted catalog, but operators must select a model currently available to their account. The client implements Bearer authentication, timeout, retries for transient errors, JSON-object response mode, Pydantic validation, one bounded schema repair, and trace metadata.

No silent model-provider fallback is permitted. Offline CI uses HTTPX mock transport. Live model tests and NIM-as-judge evaluation are opt-in, require `NVIDIA_NIM_API_KEY`, and must not run with secrets on untrusted fork pull requests.

## Consequences

The service can change NIM models without changing calculation or report schemas. Provider outages produce explicit report-job failures while calculation endpoints remain available. Prompt and model versions must be recorded for comparison. Operators are responsible for model availability, quota, hosted-data policy, and secret management.

## Rejected alternatives

- A provider-agnostic automatic fallback was rejected because it hides a material behavior and privacy change.
- Calling NIM directly from API route handlers was rejected because retries, schema repair, tracing, and worker isolation would be duplicated.
- Running live LLM tests on every pull request was rejected because it spends quota, increases flakiness, and risks secrets on forked code.
