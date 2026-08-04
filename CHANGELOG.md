# Changelog

All notable changes to Four Pillars are documented in this file.

The format follows Keep a Changelog, and release numbers follow Semantic Versioning.

## [Unreleased]

### Planned

- Multi-node job-store adapters and horizontally scalable report workers.
- Additional independent golden-chart fixtures near solar-term boundaries.

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

[Unreleased]: https://github.com/ContextualWisdomLab/four-pillars/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/ContextualWisdomLab/four-pillars/releases/tag/v0.2.0
