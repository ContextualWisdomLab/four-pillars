# Changelog

All notable changes to Four Pillars are documented in this file.

The format follows Keep a Changelog, and release numbers follow Semantic Versioning.

## [Unreleased]

### Added

- An evidence-bound product and technical gap baseline mapping PRD, TRD, architecture, data, security, tests, operations, live PR maturity, next actions, and acceptance evidence without claiming certification or scientific prediction.
- Independent KASI/NAOJ 2026 golden fixtures for all twelve month-changing solar terms, enforcing a two-minute timing budget and five-minute year/month pillar transition checks without network or test-only ephemeris dependencies.
- Offline authority-fixture governance that detects missing evidence, provenance, tolerance, traceability, and calculation-version contracts in the hourly product-gap audit.

### Changed

- Apparent solar longitude now uses a bounded VSOP87 Earth series in Terrestrial Time with FK5, nutation, and aberration corrections; deterministic calculation evidence advances to `calendar-1.1.0`.
- Calculation and standards doctoring now trace the official Korean calendar basis, independent NAOJ cross-check, IERS time-scale policy, JPL DE440 claim boundary, signed before/after model errors, and residual historical-time risks.

### Planned

- PostgreSQL and object-storage adapters for horizontally scalable multi-node deployments.
- RFC 9457 Problem Details and W3C Trace Context propagation through a separately versioned compatibility change.
- Stage-aware test-time compute allocation and ablation across routed and conducted interpretation stages.

## [0.8.0] - 2026-08-06

### Added

- An hourly OpenCode product-development control plane scheduled at minute 47 that uses `NVIDIA_NIM_API_KEY`, bounded NVIDIA NIM model fallback, and a zero-open-PR single-flight gate to propose exactly one buyer-visible increment.
- A three-runner trust boundary separating the model-bearing proposal runner, the uncredentialed exact-artifact verifier, and the non-executing publication runner.
- An immutable handoff contract binding the exact base SHA, numeric artifact ID, artifact digest, patch SHA-256, changed-file count, diff-byte budget, and Git modes before verification or publication.
- A trusted PR-message parser that rejects symlinks, non-regular files, malformed UTF-8, control and bidirectional characters, and UTF-8 byte-budget violations before publication credentials exist.
- Root `ARCHITECTURE.md`, `CLAUDE.md`, expanded `AGENTS.md`, an operations runbook, Mermaid control-plane diagrams, executable workflow-security contracts, and APA 7 doctoring for GitHub Actions, OpenCode, NVIDIA NIM, NIST SP 800-218, Fugu, Conductor, and TRINITY.

### Changed

- Package and API versions advance to `0.8.0`; deterministic calculation-policy, prompt, database, cursor, idempotency, report schema, browser-history, artifact, and standalone/modular MSA contracts remain unchanged.
- The deterministic minute-17 quality sentinel remains read-only and model-free; commercial product development is isolated in the separate minute-47 workflow with no merge, approval, release, or deployment authority.
- Autonomous LLM increments must preserve immutable calculation evidence and evaluate single-model routing versus deep multi-agent execution with explicit workflow stages, access lists, bounded recursive depth, role-specific reasoning effort, and reasoning-level ablation grounded in Fugu, Conductor, and TRINITY.
- Exact-head CI continues to require Python 3.11 and 3.12 verification, container validation, dependency integrity, product-gap and documentation audits, public docstrings, package builds, and 100% statement and branch coverage.

### Security

- OpenCode model execution uses only `NVIDIA_NIM_API_KEY`; `COPILOT_GITHUB_TOKEN` remains prohibited and existing reviewer-agent identities, secret names, and provider routing are unchanged.
- The proposal runner receives no GitHub write token, OIDC token, Actions runtime/cache channel, GitHub command-file channel, reviewer credential, or publication credential; fallback dependency installation explicitly removes the NIM secret.
- The verifier receives neither model nor publication credentials, removes GitHub/OIDC/Actions runtime and command-file variables before every proposed verification command, and proves the post-verification patch digest is unchanged.
- The publisher executes no proposed code, validates artifact and patch identities plus queue and live-base state, preserves a trusted metadata parser before applying the proposal, and mints a repository-scoped Maintainer App token only for one branch and one pull request.
- Symlink and gitlink proposals are rejected, artifact identifiers and digests are validated lexically before API use, and remote branch inventory distinguishes absence from lookup failure so publication fails closed.

## [0.7.0] - 2026-08-06

### Added

- An optional Contextual Orchestrator interpretation backend using the organization gateway's OpenAI-compatible chat-completions contract, Bearer authentication, prompt-safe usage attribution, explicit routing metadata, and bounded `auto`, `route`, or `conduct` execution.
- A runtime-checkable `StructuredGenerationClient` port and settings-driven interpreter factory while preserving explicitly injected standalone and MSA interpreters.
- APA 7th standards and research references plus a standards-to-code, test, workflow, and residual-risk traceability matrix covering ISO/IEC 25010:2023, ISO/IEC 42001:2023, ISO/IEC 23894:2023, NIST AI RMF, NIST AI 600-1, RFC 9457, W3C Trace Context, and peer-reviewed LLM-judge research.
- ADR 0003 documenting direct NIM as the standalone default, Contextual Orchestrator as an optional organization adapter, credential separation, real route/conduct execution, and the no-fallback decision.
- Endpoint-security contracts that allow HTTPS remotely and cleartext HTTP only on explicit loopback hosts for local development.

### Changed

- Package and API versions advance to `0.7.0`; deterministic calculation-policy, prompt, database, cursor, idempotency, report schema, and artifact contracts remain unchanged.
- Staged interpretation now depends on a provider-neutral structural generation client rather than the concrete NIM client; both built-in adapters share bounded transport, retry, validation, and repair behavior.
- Direct NVIDIA NIM retains provider-native JSON mode, while Contextual Orchestrator deliberately omits `response_format`, tools, and function-calling fields so the gateway does not collapse the request into single-agent passthrough.
- `ReportService` selects the configured built-in interpreter only when a custom `ReportInterpreter` was not injected, preserving standalone and modular MSA composition.
- Product, technical, API, modularity, security, operations, UML, hourly-loop, and environment documentation describe both explicit interpretation backends and their trust boundaries.
- The hourly product-gap and document audits enforce interpretation, credential, standards, APA 7th, ADR, secret-exclusion, public-docstring, 100% statement and branch coverage, and database-naming contracts.

### Security

- Direct model access uses only `NVIDIA_NIM_API_KEY`; the optional organization gateway uses only `CONTEXTUAL_ORCHESTRATOR_TOKEN`. A selected-backend failure has no silent provider fallback.
- Remote credential-bearing model endpoints require HTTPS. Loopback HTTP is limited to `localhost`, `127.0.0.1`, or `::1` for local development.
- Contextual Orchestrator attribution contains only `service=four-pillars` and optional organization labels; personal data, prompt or report content, fingerprints, paths, API keys, and provider credentials are prohibited.
- Hourly and release workflows receive neither model credential, and hosted evaluation remains opt-in.
- LLM-as-a-judge output remains supplementary to deterministic fixtures, Pydantic schemas, rule-based quality gates, security review, and human review because peer-reviewed research documents adversarial and judgment-bias risks.
- Stranded report-job recovery requires proof that no worker owns the job and a fresh `Idempotency-Key`, preventing accidental replay of the existing queued or running record.

## [0.6.0] - 2026-08-05

### Added

- A responsive, accessible recent report panel in the browser studio, backed by the authenticated v0.5 report-history API and the editable Figma desktop/mobile design.
- Exact lifecycle-status filtering, refresh, cursor-based “load more,” active-job restoration and polling, completed artifact actions, explicit empty/error states, and stale-request suppression.
- Desktop and mobile layouts that preserve the existing calculation-first workflow while making recent durable work recoverable after a refresh, client restart, or operational handoff.

### Changed

- Browser artifact downloads now use authenticated in-memory fetch requests, so deployments protected by `X-API-Key` can download generated files without putting credentials in URLs or persistent browser storage.
- Package and API versions advance to `0.6.0`; deterministic calculation-policy, prompt, repository-port, cursor, and database contracts remain unchanged.
- The full release gate continues to require complete public API docstrings and 100% statement and branch coverage on Python 3.11 and 3.12.

### Security

- The browser renders every report-history field with safe DOM text APIs, truncates displayed operational errors, and never requests or reconstructs subject labels, birth data, context notes, fingerprints, idempotency material, generated copy, traces, or artifact paths.
- History and active-job requests use independent sequence guards so stale responses cannot repopulate a previous API-key context or replace a newer filter, page, or polling state.
- Authenticated artifact downloads use short-lived in-memory Blob URLs with delayed revocation; the API key remains page-memory-only and is never written to URLs, cookies, local storage, session storage, IndexedDB, or report data.
- Release validation and the browser recovery surface never receive or read `NVIDIA_NIM_API_KEY`; hosted NVIDIA NIM remains an explicit interpretation boundary.

## [0.5.0] - 2026-08-04

### Added

- An authenticated `GET /v1/reports` collection endpoint with optional lifecycle-status filtering, deterministic newest-first keyset pagination, and the existing privacy-safe public job view.
- A separate runtime-checkable `ReportJobHistoryRepository` capability, preserving compatibility for organization adapters that implement only the required report-job repository port.
- Versioned strict report-history cursors and the two compliant SQLite indexes `idx_report_jobs_created_id` and `idx_report_jobs_status_created_id` for stable unfiltered and status-filtered traversal.
- Product, API, technical, modularity, and hourly-audit contracts for recoverable recent work after a browser refresh, client restart, or operational handoff.

### Changed

- Package and API versions advance to `0.5.0`; deterministic calculation-policy and prompt versions remain unchanged.
- Report-history traversal uses `(created_at DESC, id DESC)` with a UUID tie-breaker and exclusive `limit + 1` continuation, avoiding offset drift and duplicate rows during a stable traversal.
- The full release gate continues to require complete public API docstrings and 100% statement and branch coverage on Python 3.11 and 3.12.

### Security

- Report-history items and cursors exclude subject labels, birth data, user context, stored requests, fingerprints, idempotency material, generated copy, model traces, and artifact paths.
- Cursors are bounded and fail closed on malformed, unsupported, noncanonical base64url, non-UTC timestamp, extra-field, or invalid-UUID input with HTTP 400.
- Legacy adapters fail explicitly with HTTP 501 instead of maintaining unsafe process-local history, and all SQLite history queries use static parameterized statements.
- Release validation, scheduled product checks, and history traversal never receive or read `NVIDIA_NIM_API_KEY`; hosted NVIDIA NIM remains an explicit interpretation boundary.

## [0.4.0] - 2026-08-04

### Added

- Optional RFC 8941 structured-string `Idempotency-Key` support for `POST /v1/reports`, with canonical request fingerprints, durable replay across process restarts, browser retry reuse, and explicit `Idempotency-Replayed` response headers.
- A separate runtime-checkable `IdempotentReportJobRepository` capability for atomic keyed creation, preserving compatibility for organization adapters that implement only the original repository port.
- Automatic migration of existing v0.3 SQLite job databases with canonical request fingerprint backfills and the two-word snake-case unique index `idx_report_jobs_idempotency_key_digest`.
- Published API and modularity contracts for malformed keys, different-payload reuse, key expiration, legacy-adapter behavior, and multi-node database atomicity.

### Changed

- Package and API versions advance to `0.4.0`; deterministic calculation-policy and prompt versions remain unchanged.
- Browser report retries keep one key only in page memory until durable enqueueing succeeds, then clear it; changing reviewed inputs invalidates the pending key.
- The full release gate continues to require 100% statement and branch coverage and complete public API docstrings.

### Security

- Raw idempotency keys are never stored; only SHA-256 key digests and canonical request fingerprints are persisted, and one key reused with a different payload is rejected.
- Keyed requests against legacy adapters fail explicitly with HTTP 501 instead of using unsafe process-local locking in a potentially multi-node deployment.
- Release validation, scheduled product checks, and idempotency handling never receive or read `NVIDIA_NIM_API_KEY`; hosted NVIDIA NIM remains an explicit interpretation boundary.

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

- Deterministic Four Pillars calculation for solar and Korean lunar input, IANA time zones, optional solar-time correction, Li Chun year boundaries, twelve month-changing solar terms, year, month, day, and hour pillars, Ten Gods, hidden stems, Twelve Growth Stages, element balance, interactions, and evidence fingerprints.
- Deterministic daewoon, annual luck, and monthly luck output with explicit date boundaries and interaction evidence.
- Versioned natal, daewoon, annual, monthly, practical-skills, synthesis, editorial-repair, and LLM-judge prompts for NVIDIA NIM.
- Schema-validated NVIDIA NIM generation with bounded network retries, bounded repair, prompt hashes, and no silent provider fallback.
- FastAPI, Typer CLI, SQLite job queue, separate worker process, browser studio, Docker packaging, and searchable Korean HTML, PDF, and JSON report artifacts with SHA-256 manifests.
- PRD, TRD, calculation policy, API documentation, operations runbooks, ADRs, PlantUML domain diagrams, architecture documentation, security policy, and contribution guidance.
- Automated quality gates for deterministic grounding, required sections, relationship balance, vague or forbidden copy, medical claims, false authority, and future-event certainty.
- Public API docstring enforcement and 100% statement and branch coverage across the Python production package.
- Repository-wide credential standardization on `NVIDIA_NIM_API_KEY` for hosted NIM generation and opt-in live evaluation.

### Security

- Escaped user-controlled HTML, allow-listed artifact names, resolved path boundaries, UUID artifact directories, constant-time API-key digest comparison, non-root containers, redacted public job views, retention and deletion operations, dependency hashes, SAST, and dependency security scanning.

### Changed

- Calculation data is the immutable source of truth; model output may interpret but cannot replace pillars, date boundaries, Ten Gods, interactions, or the calculation fingerprint.
- Hosted model and evaluation model identifiers remain deployment configuration so operators can choose a currently available free NVIDIA NIM model.

[Unreleased]: https://github.com/ContextualWisdomLab/four-pillars/compare/v0.8.0...HEAD
[0.8.0]: https://github.com/ContextualWisdomLab/four-pillars/releases/tag/v0.8.0
[0.7.0]: https://github.com/ContextualWisdomLab/four-pillars/releases/tag/v0.7.0
[0.6.0]: https://github.com/ContextualWisdomLab/four-pillars/releases/tag/v0.6.0
[0.5.0]: https://github.com/ContextualWisdomLab/four-pillars/releases/tag/v0.5.0
[0.4.0]: https://github.com/ContextualWisdomLab/four-pillars/releases/tag/v0.4.0
[0.3.0]: https://github.com/ContextualWisdomLab/four-pillars/releases/tag/v0.3.0
[0.2.0]: https://github.com/ContextualWisdomLab/four-pillars/releases/tag/v0.2.0
