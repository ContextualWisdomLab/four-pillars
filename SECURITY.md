# Security Policy

## Supported version

Security fixes are applied to the latest minor release on `main`. Pre-release branches are not production-supported until merged.

## Reporting a vulnerability

Do not open a public issue for a vulnerability that could expose birth data, generated reports, API keys, artifact paths, prompt data, model-routing metadata, usage attribution, or deployment credentials. Send a private report to repository maintainers with reproduction steps, affected versions, impact, and a suggested mitigation when available. Maintainers will acknowledge a complete report within five business days and coordinate disclosure after a fix is available.

## Protected information

Birth date, birth time, location, calendar choice, relationship notes, work notes, and generated reports can identify a person or reveal sensitive circumstances. Production deployments must encrypt transport, restrict storage access, set a retention period, avoid logging raw prompts or reports, and provide deletion.

`CONTEXTUAL_ORCHESTRATOR_TOKEN`, API authentication values, database credentials, and organization gateway credentials must be stored as secrets and never committed. Provider-native credentials are not Four Pillars product-runtime configuration; they belong to the Contextual Orchestrator trust boundary.

## Security boundaries

The deterministic calculator is the source of truth for pillars and luck dates. LLM output cannot replace those values. User context is serialized as untrusted data rather than concatenated into system instructions. Pydantic schemas and deterministic/editorial quality gates run before publication.

The repository-owned interpretation route is explicit and fixed: `ContextualOrchestratorReportInterpreter` calls the approved gateway with virtual model `orchestrator/free`. A missing gateway credential, unavailable gateway, empty free pool, invalid response, or exhausted retry/repair budget fails the report job. The application does not silently call NVIDIA NIM, OpenAI, OpenRouter, Bytez, another provider, or a paid virtual route.

Provider discovery, provider credentials, free-pool eligibility, downstream failover, and provider-level retention/residency policy are owned by Contextual Orchestrator. A caller-owned MSA may inject another `ReportInterpreter`, but that is an external composition boundary and cannot be selected through Four Pillars product settings.

Usage attribution must never contain subject labels, birth data, user notes, calculation fingerprints, prompts, generated text, artifact paths, API authentication values, or model credentials. Operators must treat an attribution leak as a privacy incident and correct it through configuration or a reviewed software change rather than adding more sensitive labels for debugging.

HTML is escaped, artifact names are allow-listed, UUID directories prevent personal data in filenames, and API keys are compared through SHA-256 digests using constant-time comparison. Public report-history views and cursors exclude stored requests, private context, fingerprints, idempotency material, generated copy, traces, and internal paths.

## Deployment responsibilities

Production deployments must use TLS for the public API and non-loopback Contextual Orchestrator gateway, restrict egress to the approved gateway, rotate secrets, separate API and worker permissions, encrypt backups, and document orchestrator/downstream subprocessors, data residency, retention, and incident obligations.

A central `.github`, `naruon`, or platform deployment may add organization controls, but it must not bypass the repository's deterministic, privacy, quality, `orchestrator/free`, or no-direct-fallback contracts. Model credentials are excluded from ordinary pull-request, hourly, release, and untrusted-fork workflows.

Model-backed autonomous source development is owned by the shared ContextualWisdomLab hourly maintainer rather than a repository-specific provider-credentialed writer. The repository-local hourly workflow is model-free.

## Verification

Required checks include Ruff, compilation, document and prompt validation, all offline tests with exactly 100 percent statement and branch coverage, package and container builds, Security Scan, and Semgrep. Offline orchestration tests prove direct backend/non-free model settings are rejected, outbound requests use `orchestrator/free`, malformed output fails closed, and retries/repairs do not change the virtual route.

Hosted tests are opt-in and receive only the GitHub Secret `CONTEXTUAL_ORCHESTRATOR_TOKEN` plus a configured gateway URL. They must not receive NVIDIA, OpenAI, OpenRouter, Bytez, or other provider-native secrets. Live evaluation output omits raw model trace content.

The standards and research control mapping is maintained in `docs/standards/REFERENCES.md` and `docs/standards/TRACEABILITY.md`. That mapping supports engineering governance but is not an accredited security or AI-management certification.
