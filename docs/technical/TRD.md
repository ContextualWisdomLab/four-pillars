# Four Pillars Technical Requirements Document

**Document maturity:** protected-main behavior is `implemented_on_protected_main`; open-PR/future behavior is labeled explicitly.

## 1. Architecture principles

Four Pillars has four application trust boundaries:

1. **Calculation boundary** — validated birth/time policy produces immutable typed chart/luck evidence.
2. **Interpretation boundary** — one explicitly selected structured-generation adapter receives immutable evidence plus untrusted user context.
3. **Quality boundary** — schema, fingerprint, completeness, balance, copy and safety rules decide whether prose may be published.
4. **Delivery boundary** — only approved results become durable artifacts and completed job state.

No layer may silently assume authority owned by an earlier layer. In particular, an LLM may interpret but cannot change deterministic evidence, and a persistence/provider adapter cannot change calendar policy.

The canonical technical architecture is split across this TRD plus:

- `docs/architecture/SYSTEM_ARCHITECTURE.md`
- `docs/uml/architecture.md`
- `docs/architecture/DATA_MODEL.md`
- `docs/adr/README.md`
- `docs/security/THREAT_MODEL.md`
- `docs/technical/TEST_STRATEGY.md`
- `docs/operations/OPERABILITY.md`
- `docs/standards/DOCUMENTATION_AUDIT.md`

## 2. Technology stack

Current protected-main stack:

- Python 3.11 and 3.12
- Pydantic 2 / Pydantic Settings 2
- FastAPI + Uvicorn
- Typer CLI
- SQLite WAL for the built-in single-node queue/history adapter
- HTTPX for direct NVIDIA NIM and explicit Contextual Orchestrator integration
- ReportLab CJK CID fonts for searchable Korean PDF
- Korean Lunar Calendar for supported Korean lunar/solar input conversion
- Pytest + pytest-cov + Ruff
- GitHub Actions with pinned/reviewed third-party actions where repository policy requires
- Docker/Compose for independent API + worker deployment.

No Rust/GPU arithmetic requirement is introduced because Four Pillars is not a psychometric/numerical-optimization product whose current workload justifies a new native compute plane. Deterministic astronomical/calendar code remains auditable Python; a future performance rewrite would require parity evidence and a separate ADR.

## 3. Deterministic calculation components

### 3.1 `solar.py`

`solar.py` evaluates the bounded VSOP87 Earth longitude/radius series in Terrestrial Time and applies the repository's documented FK5/nutation/aberration corrections without a network or hosted ephemeris dependency. Root solving locates apparent-solar-longitude crossings used by the Four Pillars calendar policy.

The implementation is independently checked against KASI/NAOJ 2026 solar-term evidence. All twelve production month-changing `jie` boundaries are covered with a minute-level budget, and buyer-visible year/month transition tests exercise both sides of relevant boundaries. Current calculation evidence version: `calendar-1.1.0`.

### 3.2 `calendar.py`

Responsibilities:

- validate/normalize solar or supported Korean lunar input;
- apply IANA timezone and configured local mean/apparent solar-time policy;
- determine Li Chun year and current/next month-changing `jie`;
- calculate year/month/day/hour pillars;
- preserve configurable midnight/late-Zi rollover;
- leave hour pillar unresolved when birth time is unknown;
- derive Ten Gods, hidden stems, Twelve Growth stages, element balance and supported interactions;
- emit boundary warnings;
- generate the immutable SHA-256 calculation fingerprint.

Calculation policy changes require calculation-version review, independent fixtures, test-strategy update, and ADR review if the source-of-truth semantics change.

### 3.3 `fortune.py`

Consumes the natal `Chart` and returns daewoon scenarios, annual snapshots and monthly snapshots. It preserves the natal day master for Ten-God relations and calculates supported interactions between temporary and natal pillars.

Annual luck changes at Li Chun; monthly luck changes at the relevant `jie`, not at Gregorian month boundaries. When the direction cannot be uniquely selected from configured gender policy, both scenarios are returned rather than guessed.

## 4. Structured generation and interpretation

### 4.1 Structural boundary

`StructuredGenerationClient` is the application protocol for structured generation. The implementation must be provider-neutral at the application layer while provider selection remains explicit at configuration/deployment time.

### 4.2 Direct NVIDIA NIM

`NimClient` uses direct hosted NVIDIA NIM under `NVIDIA_NIM_API_KEY`. It implements:

- Bearer authentication;
- request timeout;
- bounded transient retries;
- JSON object response mode;
- Pydantic schema validation;
- bounded schema repair;
- trace/model/attempt metadata.

A direct NIM failure is visible; it never silently changes provider.

### 4.3 Contextual Orchestrator

`ContextualOrchestratorClient` is an explicit optional OpenAI-compatible organization adapter using `CONTEXTUAL_ORCHESTRATOR_TOKEN`. It adds prompt-safe organization attribution and permits the gateway to implement approved routing/conduct behavior without exposing provider administration credentials to Four Pillars.

Attribution may include `service=four-pillars` and approved organization dimensions. It must not contain personal subject labels, birth/context input, prompt/report text, calculation fingerprint, internal paths, API credentials, or model-provider credentials.

Four Pillars does not import Contextual Orchestrator internals and does not access its private database. The gateway is an external/deployment boundary.

### 4.4 Analysis pipeline

`analysis.py` runs versioned prompt stages for natal, daewoon, annual, monthly, practical skills, synthesis, and a bounded editorial repair when required. Prompt/model identities and response schema are versioned/traceable.

User context and model output are untrusted data. A model cannot change the fingerprint or deterministic source values. LLM-as-a-judge is supplementary and cannot authorize publication, merge, release, or a calculation change.

## 5. Quality component

`quality.py` must fail closed when:

- calculation fingerprint/facts are inconsistent;
- required chapters are absent;
- constructive possibilities, cautions or actions are missing;
- relationship guidance becomes warning-only;
- copy uses known ambiguous/malformed patterns that alter meaning;
- generated text makes deterministic event-certainty claims;
- generated text gives diagnosis/treatment instructions;
- generated text presents the model/app as empirical authority for real-world outcomes;
- disclaimer/real-world evidence boundaries are absent where required.

One bounded editorial-repair path may improve prose but may not change calculations.

## 6. Persistence, history and idempotency

### 6.1 Standalone `JobStore`

`jobs.py` owns the built-in SQLite `report_jobs` table. Exact fields, lifecycle, indexes, sensitivity, and ERD are documented in `docs/architecture/DATA_MODEL.md`.

`BEGIN IMMEDIATE` is used for atomic keyed creation/claim boundaries. Existing additive migration code backfills request fingerprints and adds idempotency/history fields/indexes without introducing single-word application-owned database objects.

### 6.2 Repository capabilities

`ReportJobRepository` remains the required application port. Atomic idempotent creation and history traversal are separate optional runtime-checkable capabilities so existing MSA adapters remain compatible and unsupported endpoints fail explicitly rather than pretending success.

### 6.3 History

`history.py` owns strict versioned cursors containing only an exclusive UTC timestamp and opaque job UUID. Stable order is `(created_at DESC, id DESC)` with exact optional status filtering. The API fetches one extra row to decide whether to issue a continuation cursor.

History output never serializes `request_json`, personal context, request fingerprints, idempotency material, generated report text, traces, or internal artifact paths.

### 6.4 Idempotency

The raw client idempotency key is not stored. The standalone repository persists a SHA-256 key digest and canonical request fingerprint under an atomic uniqueness boundary. Same key/same request replays the job; same key/different request raises a stable conflict error.

Any multi-node adapter must preserve equivalent atomic semantics.

## 7. Service/application composition

`ReportService` composes calculation, durable repository, selected/injected interpreter, quality validation, and `ArtifactPublisher`.

Settings-based interpreter selection runs only when a custom interpreter has not been injected. An organization adapter can therefore replace interpretation/persistence/artifact components without forking the deterministic package.

Report generation stages output into a temporary/staging artifact location and publish atomically before the job becomes `completed`.

## 8. API and browser boundary

FastAPI exposes calculation, luck, report enqueue/status/history/delete and allow-listed artifact retrieval endpoints under the documented API contract.

The browser studio:

- can calculate first and expose fingerprint/boundaries before generation;
- can list/filter/append recent redacted jobs;
- resumes queued/running polling;
- suppresses stale history/poll responses with sequence guards;
- renders untrusted API values using safe DOM text operations;
- bounds error text;
- uses text/non-color state cues and polite live announcements;
- keeps API credentials in current page memory, not persistent browser storage;
- performs authenticated artifact downloads through headers rather than credential-bearing URLs.

## 9. Reporting/artifacts

`reporting.py` escapes HTML, uses the product report design, renders searchable Korean PDF with supported CJK CID fonts, emits calculation/report JSON and privacy-safe traces, and writes a SHA-256 manifest.

Default reports omit footers/page numbers according to the established product decision. Material report-template changes require visual inspection and, when the user flow/layout changes, synchronization with the authoritative Figma design.

## 10. Purpose-bound privacy and security

Four Pillars does not blanket-mask birth/context values required for the requested function. ADR 0004 and `docs/security/THREAT_MODEL.md` require **purpose-bound** processing:

- minimum necessary data sent across each boundary;
- authentication/authorization;
- TLS and deployment storage encryption/access control;
- redacted history and prompt-safe attribution;
- separate direct-NIM/orchestrator/application/database secrets;
- bounded retention and explicit deletion;
- restricted/auditable privileged access;
- provider/subprocessor/data-residency documentation for production deployment.

`NVIDIA_NIM_API_KEY` is a direct NIM secret. `CONTEXTUAL_ORCHESTRATOR_TOKEN` is a different organization-gateway secret. `COPILOT_GITHUB_TOKEN` is prohibited for repository autonomous development.

Artifact paths are rooted/allow-listed, HTML is escaped, API-key digest comparison is constant-time, and opaque UUIDs prevent subject names from becoming filesystem keys.

## 11. Reliability and recovery

The queue persists before model work. Workers claim atomically. Selected backend failure does not cause automatic provider fallback. Partial artifacts remain non-public and are cleaned after failed generation where the implementation can do so safely.

Current `running` rows remain visible after a worker crash; automatic requeue is not assumed safe without an ownership/lease rule. Backup/restore, incident, SLI/SLO, retention/deletion and multi-node obligations are defined in `docs/operations/OPERABILITY.md`.

## 12. Observability

Health proves process liveness. Readiness verifies the minimum authoritative repository/artifact capabilities for the deployment. Operational metrics distinguish calculation, queue, selected backend, schema repair, quality repair, rendering and artifact publication.

Ordinary telemetry excludes birth/context/request/report text, prompts, credentials, idempotency keys and internal artifact paths. `traces.json` records bounded model/attempt/repair identity evidence rather than published raw model content.

W3C distributed trace propagation is `planned` unless a protected-main implementation says otherwise.

## 13. Standalone and modular MSA deployment

### Standalone — `implemented_on_protected_main`

- SQLite WAL `JobStore`;
- filesystem artifact publisher;
- direct NVIDIA NIM by default;
- API + worker containers/processes;
- calculation endpoints independent from model availability.

### Organization MSA — supported architecture

An organization can inject a remote repository/queue, object-storage `ArtifactPublisher`, and Contextual Orchestrator while keeping domain/calculation/evidence contracts unchanged.

Cross-service integration with central `.github`, `naruon`, contextual-orchestrator or other CWL services uses explicit APIs/ports/events/artifacts. Direct cross-service application-database access is prohibited.

Multi-node persistence details are `planned` until a concrete adapter/migration is reviewed and tested.

## 14. Autonomous development/control plane

The existing minute-17 deterministic sentinel and minute-47 NVIDIA NIM/OpenCode product-development workflow are `implemented_on_protected_main`.

The work-conserving/no-early-stop contract is documented in `docs/operations/AUTONOMOUS_DEVELOPMENT.md`. One generated PR per product-development run is a writer-safety boundary, not permission to stop after one inventory/RCA/test/document change.

PR #29's minute-07 exact-head PR steward is `superseded` because it closed without merge. It has no current execution authority; any successor requires a fresh reviewed change and operational acceptance.

Model-based development uses `NVIDIA_NIM_API_KEY`, not `COPILOT_GITHUB_TOKEN`, and must not receive reviewer/merge/release identity. Independent review/Checks/branch governance remain separate authority.

## 15. Test and release contract

`docs/technical/TEST_STRATEGY.md` is the authoritative detailed test strategy. Required protected-main/release evidence includes:

- independent KASI/NAOJ solar-term fixtures and realistic Li Chun/`jie`/rollover transitions;
- deterministic chart/luck/derived-relation tests;
- persistence/idempotency/history/concurrency/privacy tests;
- offline NIM/orchestrator structured-generation contract tests;
- opt-in trusted hosted NIM tests using `NVIDIA_NIM_API_KEY`;
- report rendering/artifact integrity tests;
- exactly 100% owned production statement and branch coverage;
- public production docstring completeness;
- Ruff, compilation, document/prompt checks;
- package/container build;
- security/dependency/SAST gates required by repository policy;
- exact-head review/provenance/version/CHANGELOG acceptance.

Queued, pending, skipped-required, cancelled, stale/predecessor/synthetic-only or failed evidence is not passing evidence.

## 16. Architecture/documentation fitness

ADR 0005 establishes the authority/maturity model. The canonical graph must make product intent, technical ownership, system viewpoints, data/ERD, decisions, threats, testing, operability, standards/research, visual contracts and release history discoverable without chat reconstruction. `docs/product-technical-gap-baseline.md` is the prioritized evidence and action register.

A material code/API/model/workflow/persistence/lifecycle/trust-boundary change must update affected canonical documents or prove no impact. Documentation completeness is an engineering quality criterion, not a substitute for executable product work.

## 17. Standards and research traceability

`docs/standards/REFERENCES.md` and `docs/standards/TRACEABILITY.md` contain the broader APA 7th evidence map. `docs/standards/DOCUMENTATION_AUDIT.md` evaluates architecture completeness.

Current primary governance references include ISO/IEC/IEEE 42010:2022, ISO/IEC 25010:2023, ISO/IEC 23894:2023, ISO/IEC 42001:2023, NIST AI RMF 1.0 / NIST AI 600-1, and final NIST SSDF SP 800-218 v1.1. NIST SP 800-218 Rev. 1 / SSDF 1.2 remains a draft as of this baseline and is not treated as a final normative source.

The standards mapping is an engineering/readiness aid, not an ISO, CSAP, SOC 2, NIST or scientific-certification claim.
