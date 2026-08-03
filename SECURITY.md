# Security Policy

## Supported version

Security fixes are applied to the latest minor release on `main`. Pre-release branches are not production-supported until merged.

## Reporting a vulnerability

Do not open a public issue for a vulnerability that could expose birth data, generated reports, API keys, artifact paths, prompt data, or deployment credentials. Send a private report to the repository maintainers with reproduction steps, affected versions, impact, and a suggested mitigation when available. Maintainers will acknowledge a complete report within five business days and coordinate disclosure after a fix is available.

## Protected information

Birth date, birth time, location, calendar choice, relationship notes, work notes, and generated reports can identify a person or reveal sensitive circumstances. Production deployments must encrypt transport, restrict storage access, set a retention period, avoid logging raw report prompts, and provide deletion. `NVIDIA_API_KEY`, API authentication values, and database credentials must be stored as secrets and must never be committed.

## Security boundaries

The deterministic calculator is the source of truth for pillars and luck dates. LLM output cannot replace those values. User context is serialized as untrusted data, not concatenated into system instructions. HTML is escaped, artifact names are allow-listed, UUID directories prevent personal data in filenames, and API keys are compared through SHA-256 digests using constant-time comparison.
