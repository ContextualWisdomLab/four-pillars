# Changelog

All notable changes to Four Pillars are documented in this file.

The format follows Keep a Changelog, and release numbers follow Semantic Versioning.

## [Unreleased]

### Added

- Optional RFC 8941 structured-string `Idempotency-Key` support for `POST /v1/reports`, with canonical request fingerprints, durable replay, browser retry reuse, and explicit replay response headers.
- A separate `IdempotentReportJobRepository` capability for atomic keyed creation, preserving compatibility for existing adapters that implement only the original repository port.

### Security

- Raw idempotency keys are never stored; only SHA-256 key digests and canonical request fingerprints are persisted, and reuse with a different payload is rejected.
- Keyed requests against legacy adapters fail explicitly instead of using unsafe process-local locking in a potentially multi-node deployment.

### Planned

- PostgreSQL and object-storage adapters for horizontally scalable multi-node deployments.
- Additional independent golden-chart fixtures near solar-term boundaries.

## [0.3.0] - 2026-08-04

### Added

- Runtime-checkable modular service ports for report-job repositories, report interpreters, and artifact publishers, with standalone SQLite, NVIDIA NIM, and filesystem adapters retained as defaults.
- Constructor injection in `ReportService`, allowing organization platforms and MSA deployments to replace persistence, hosted interpretation, or artifact delivery independently without forking deterministic calculation code.
- An hourly product-quality loop that runs the complete release gate and deterministic product-gap audit, enforces database object naming and modularity contracts, and maintains one idempotent regression issue.
- A reusable release workflow for `main` pushes, manual dispatch, and organization-level `workflow_call` validation, with curated changelog notes, versioned source and wheel artifacts, and SHA-256 checksums.
- Standalone/MSA modularity and hourly-loop operational runbooks.

### Changed

- Package and API versions advance to `0.3.0`.
- Protocol declarations fail explicitly on accidental direct invocation, while structural implementations remain inheritance-free.
- The full gate continues to enforce 100% statement and branch coverage and complete public API docstrings.

### Security

- Release publication uses a dedicated least-privilege job with `contents: write`; validation jobs remain read-only.
- Scheduled product checks and release validation never receive `NVIDIA_NIM_API_KEY`; hosted NVIDIA NIM evaluation remains a separate opt-in workflow.
- Release creation is idempotent and will not overwrite an existing version tag or release.

## [0.2.0] - 2026-08-04

### Added

- Deterministic Four Pillars calculation for solar and Korean lunar input, IANA time zones, optional solar-time correction, Li Chun year boundaries, twelve month-changing solar terms, year/month/day/hour pillars, Ten Gods, hidden stems, Twelve Growth Stages, element balance, interactions, and evidence fingerprints.
- Deterministic daewoon, annual luck, and monthly luck output with explicit date boundaries and interaction evidence.
- Versioned natal, daewoon, annual, monthly, practical-skills, synthesis, editorial-repair, and LLM-judge prompts for NVIDIA NIM.
- Schema-validated NVIDIA NIM generation with bounded network retries, bounded repair, prompt hashes, and no silent provider fallback.
- FastAPI, Typer CLI, SQLite job queue, separate worker process, browser studio, Docker packaging, and searchable HTML, PDF, and JSON report artifacts with SHA-256 manifests.
- PRD, TRD, calculation policy, API documentation, operations runbooks, ADRs, PlantUML domain diagrams, architecture documentation, security policy, and contribution guidance.
- Automated quality gates for deterministic grounding, required sections, relationship balance, vague or forbidden copy, medical claims, false authority, and future-event certainty.
- Public API docstring enforcement and 100% statement and branch coverage across the Python production package.
- Repository-wide credential standardization on `NVIDIA_NIM_API_KEY` for hosted NIM generation and opt-in live evaluation.

### Security

- Escaped user-controlled HTML, allow-listed artifact names, resolved path boundaries, UUID artifact directories, constant-time API-key digest comparison, non-root containers, redacted public job views, retention and deletion operations, dependency hashes, SAST, and dependency security scanning.

### Changed

- Calculation data is the immutable source of truth; model output may interpret but cannot replace pillars, date boundaries, Ten Gods, interactions, or the calculation fingerprint.
- Hosted model and evaluation model identifiers remain deployment configuration so operators can choose a currently available free NVIDIA NIM model.

[Unreleased]: https://github.com/ContextualWisdomLab/four-pillars/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/ContextualWisdomLab/four-pillars/releases/tag/v0.3.0
[0.2.0]: https://github.com/ContextualWisdomLab/four-pillars/releases/tag/v0.2.0
