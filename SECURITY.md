# Security Policy

## Supported version

Security fixes are applied to the latest minor release on `main`. Pre-release branches are not production-supported until merged.

## Reporting a vulnerability

Do not open a public issue for a vulnerability that could expose birth data, generated reports, API keys, artifact paths, prompt data, provider routes, usage attribution, or deployment credentials. Send a private report to repository maintainers with reproduction steps, affected versions, impact, and a suggested mitigation when available. Maintainers will acknowledge a complete report within five business days and coordinate disclosure after a fix is available.

## Protected information

Birth date, birth time, location, calendar choice, relationship notes, work notes, and generated reports can identify a person or reveal sensitive circumstances. Production deployments must encrypt transport, restrict storage access, set a retention period, avoid logging raw prompts or reports, and provide deletion. Birthplace correction accepts only bounded numeric longitude; the product neither retains a place name nor calls an external geocoder.

`NVIDIA_NIM_API_KEY`, `CONTEXTUAL_ORCHESTRATOR_TOKEN`, API authentication values, database credentials, and organization gateway credentials must be stored as secrets and never committed. Direct NVIDIA NIM and Contextual Orchestrator credentials are separate trust boundaries and must not be substituted, forwarded, or copied into one another's configuration.

## Security boundaries

The deterministic calculator is the source of truth for pillars and luck dates. LLM output cannot replace those values. User context is serialized as untrusted data rather than concatenated into system instructions. Pydantic schemas and deterministic/editorial quality gates run before publication.

Backend selection is explicit. A missing or unavailable selected backend fails the report job; the application does not silently fail over to another provider or adapter. The direct NIM client uses `NVIDIA_NIM_API_KEY`. The optional organization gateway uses `CONTEXTUAL_ORCHESTRATOR_TOKEN` and sends only approved organization labels as attribution.

Usage attribution must never contain subject labels, birth data, user notes, calculation fingerprints, prompts, generated text, artifact paths, API authentication values, or provider credentials. Operators must treat an attribution leak as a privacy incident and correct it through configuration or a reviewed software change rather than adding more sensitive labels for debugging.

HTML is escaped, artifact names are allow-listed, UUID directories prevent personal data in filenames, and API keys are compared through SHA-256 digests using constant-time comparison. Public report-history views and cursors exclude stored requests, private context, fingerprints, idempotency material, generated copy, traces, and internal paths.

## Deployment responsibilities

Production deployments must use TLS for the public API and non-loopback model gateways, restrict egress to approved providers, rotate secrets, separate API and worker permissions, encrypt backups, and document provider or orchestrator subprocessors, data residency, retention, and incident obligations.

A central `.github`, `naruon`, or platform deployment may add organization controls, but it must not bypass the repository's deterministic, privacy, quality, or no-fallback contracts. Hosted model secrets are excluded from ordinary pull-request, hourly, release, and untrusted-fork workflows.

## Verification

Required checks include Ruff, compilation, document and prompt validation, all offline tests with exactly 100 percent statement and branch coverage, package and container builds, Security Scan, and Semgrep. Hosted tests are opt-in: direct NIM tests use the GitHub Secret `NVIDIA_NIM_API_KEY`; a hosted Contextual Orchestrator test requires a separately managed gateway token and deployment.

The standards and research control mapping is maintained in `docs/standards/REFERENCES.md` and `docs/standards/TRACEABILITY.md`. That mapping supports engineering governance but is not an accredited security or AI-management certification.
