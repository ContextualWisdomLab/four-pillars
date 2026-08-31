# Four Pillars Product Requirements Document

**Document maturity:** `implemented_on_protected_main` for shipped requirements; explicit `active_pr`/`planned` labels identify work that has not reached protected main.

## 1. Product vision

Four Pillars converts verified birth data into a transparent Korean manse calendar calculation and then produces a useful, readable report. The product earns trust by showing exactly which calendar facts were calculated, where a solar-term or time-policy boundary creates uncertainty, which statements are traditional symbolic interpretation, and which suggested actions are ordinary planning techniques rather than predictions.

The product works independently with direct hosted NVIDIA NIM and as an organization module through Contextual Orchestrator. Model routing must never alter deterministic evidence, report schemas, prompt provenance, quality gates, artifact contracts, or the user's selected recipient without explicit configuration.

The product is not represented as scientifically validated fortune prediction, medical/clinical advice, or a certified ISO/CSAP/SOC 2 system. Engineering standards and research are used to govern software quality, AI risk, security, privacy, and evidence.

## 2. Users and stakeholder outcomes

- **Individual reader:** wants clear natal, ten-year, annual, and monthly reports without learning specialist terminology; wants visible uncertainty, practical next steps, privacy, and deletion.
- **Professional consultant:** needs reproducible calculations, editable context, consistent report structure, recoverable recent work, calculation provenance, and exportable files.
- **Platform integrator:** needs authenticated APIs, durable status/history, deterministic JSON, report artifacts, traceable prompt/model/calculation versions, and replaceable MSA adapters.
- **Operator:** needs health/readiness, retention/deletion, backup/restore, incident handling, privacy-safe manifests/telemetry, explicit backend selection, and bounded model usage.
- **Security/privacy/AI reviewer:** needs purpose-bound personal-data flows, explicit trust boundaries, model/provider/secret separation, and evidence that AI cannot rewrite deterministic calculation.
- **Acquirer:** needs discoverable product/technical architecture, ADRs, ERD, threat model, test strategy, operability evidence, standards traceability, and exact-release provenance.

## 3. Core jobs to be done

1. Enter solar or Korean lunar birth data, IANA timezone, gender policy, and optional supported time correction.
2. Verify year, month, day, and hour pillars together with solar-term boundaries, calculation policy/version, warnings, and a fingerprint.
3. Inspect daewoon, annual luck, and monthly luck without confusing Gregorian month/year boundaries with solar-term boundaries.
4. Generate a Korean report whose facts remain consistent with the immutable calculation evidence.
5. Receive constructive possibilities, cautions, decision criteria, and practical techniques rather than warning-only or deterministic prose.
6. Recover recent durable report jobs after refresh/client restart/operational handoff without exposing stored birth/context data in collection responses.
7. Filter recent work by lifecycle status, append older pages, restore active polling, and download allow-listed completed files.
8. Download JSON, HTML, PDF, traces/manifest as permitted, and delete jobs when no longer needed.
9. Run independently or route interpretation through an approved organization gateway without forking calculation/report code.
10. Give operators and reviewers enough architecture/evidence to tell `implemented_on_protected_main`, `accepted_architecture`, `active_pr`, `planned`, and `superseded` claims apart.

## 4. Functional requirements

### 4.1 Deterministic calculation

The service SHALL calculate and/or represent:

- solar and supported Korean lunar input, including supported lunar leap-month semantics;
- IANA timezone conversion;
- optional local mean/apparent solar correction under explicit policy;
- Li Chun year boundaries;
- twelve month-changing `jie` boundaries;
- configurable midnight or late-Zi day rollover;
- hour pillar and explicit unknown-birth-time behavior;
- Ten Gods, hidden stems, Twelve Growth stages, element balance, and supported stem/branch interactions;
- SHA-256 calculation fingerprint and calculation evidence version;
- visible warning around configured solar-term boundary uncertainty.

The current modern solar-term implementation is validated against independent KASI/NAOJ evidence, including all twelve 2026 `jie` boundaries. Calculation changes require versioning and independent fixture review rather than model/prompt changes.

### 4.2 Luck calculations

The service SHALL calculate forward/reverse daewoon direction, start age from the relevant `jie`, configured ten-year periods, Li Chun annual luck, and monthly luck beginning at the relevant `jie`.

When gender policy does not determine one direction, the service SHALL expose both valid scenarios rather than silently choosing one. Temporary pillars SHALL be interpreted relative to the natal day master and the calculator's supported interaction rules.

### 4.3 AI interpretation and backend selection

Direct NVIDIA NIM SHALL remain the standalone default. An operator MAY explicitly select Contextual Orchestrator as an organization gateway. No backend may silently fail over to another provider/adapter.

Versioned prompts cover natal, daewoon, annual, monthly, practical skills, synthesis, editorial repair, and judging. Deterministic calculation is read-only evidence. Model output must pass strict Pydantic schema validation plus deterministic/editorial quality gates before publication.

The direct backend uses only `NVIDIA_NIM_API_KEY`. The optional gateway uses only `CONTEXTUAL_ORCHESTRATOR_TOKEN`. Missing credentials or selected-backend failure produces a visible job failure rather than recipient/routing substitution.

The organization gateway receives prompt-safe service/organizational attribution only. Attribution must not contain subject labels, birth information, personal notes, calculation fingerprints, prompt/report text, artifact paths, authentication material, or provider credentials.

LLM-as-a-judge output is supplementary. It cannot bypass deterministic fixtures, schemas, quality/security controls, exact-head review, or human governance.

### 4.4 Report quality

Every required chapter SHALL contain:

- a plain-language summary;
- constructive possibilities;
- cautions/conditions;
- actionable ordinary-life techniques or decision criteria.

The relationship chapter SHALL include how trust, cooperation, or stability may improve rather than presenting only warnings. Copy SHALL use explicit subjects/objects/referents where ambiguity changes meaning and SHALL avoid known malformed contrast phrases.

The service SHALL reject or repair:

- claims that a future event is certain;
- diagnosis/treatment instructions;
- coercive high-stakes life decisions;
- claims that the model/app is an authoritative source of truth for real-world outcomes;
- calculation/report contradictions;
- one-off narrow questions presented as universal rules;
- unsupported alteration of deterministic evidence.

### 4.5 Outputs, jobs, history, and browser

The service SHALL provide FastAPI endpoints, CLI, a durable standalone SQLite job queue, worker execution, deterministic calculation JSON, report JSON, searchable Korean HTML/PDF, privacy-safe traces, and SHA-256 file manifests. Artifacts use opaque job identifiers rather than personal names in paths.

Authenticated report history SHALL use a redacted newest-first collection, exact lifecycle-status filtering, and opaque exclusive keyset continuation. Collection items/cursors SHALL exclude stored request content, personal context, request fingerprints, idempotency material, generated report text, model traces, and internal artifact paths.

The browser studio SHALL support recent-job recovery, refresh, status filter, cursor-based older-page append, active polling restoration, and allow-listed artifact download. It SHALL suppress stale asynchronous responses, use safe DOM text APIs, provide accessible status announcements/non-color cues, bound displayed operational error text, and retain API credentials only in current page memory.

Material visual workflow changes SHALL update or explicitly map to the authoritative Figma design. Documentation-only or copy-only changes do not require Figma churn.

### 4.6 Idempotency

Clients MAY send a supported `Idempotency-Key`. The application SHALL store only a digest of the key plus a canonical request fingerprint. Same key/same request returns the existing durable job; same key/different request fails closed. Omitting the key preserves backward-compatible new-job semantics.

### 4.7 Modular standalone/MSA operation

The calculation package SHALL import without creating a database, HTTP client, worker, application directory, artifact store, or model connection.

`ReportJobRepository`, `ReportInterpreter`, `ArtifactPublisher`, and optional idempotency/history capabilities SHALL remain replaceable structural boundaries. Explicitly injected adapters outrank settings-based defaults.

Central `.github`, `naruon`, Contextual Orchestrator, and other CWL products MAY compose/govern Four Pillars through documented APIs, ports, and immutable artifacts. Four Pillars SHALL NOT require direct access to another service's private application database.

### 4.8 Purpose-bound personal-data processing

The application SHALL preserve personal birth/context data when it is required for the requested calculation/interpretation; **blanket masking that changes or breaks product behavior is not the privacy architecture**.

Instead the product SHALL apply purpose-bound controls described in ADR 0004 and `docs/security/THREAT_MODEL.md`: minimum necessary disclosure, authentication/authorization, TLS, secret separation, restricted history/telemetry/attribution, bounded retention/deletion, encryption and access control appropriate to the deployment, and auditable privileged access.

A new provider, external recipient, identity link, telemetry field, or personal-data processing purpose requires architecture/threat/privacy review.

### 4.9 Architecture and documentation completeness

Material changes SHALL keep the canonical documentation graph code-current:

- `docs/architecture/DATA_MODEL.md`
- `docs/security/THREAT_MODEL.md`
- `docs/technical/TEST_STRATEGY.md`
- `docs/operations/OPERABILITY.md`
- `docs/standards/DOCUMENTATION_AUDIT.md`
- PRD/TRD, Architecture/UML, ADR index, standards traceability, runbooks, and Figma references when applicable.

Open-PR or planned behavior must not be described as shipped protected-main behavior. Documentation completeness is a repository quality defect, but documentation-only completion is not a valid autonomous-development stopping condition while safe implementation/test/merge work remains.

## 5. Non-functional requirements

- Deterministic calculation p95 target < 250 ms for representative supported modern dates on one CPU core.
- Report-job state remains recoverable/inspectable after API restart under supported single-node semantics.
- History traversal is stable for equal timestamps and does not repeat existing rows if new jobs are inserted during a continuation sequence.
- Browser history remains usable after refresh and does not persist credentials/report data locally.
- Offline CI never requires an external model key.
- Direct hosted NIM tests are opt-in and use repository secret `NVIDIA_NIM_API_KEY` only on trusted workflows.
- Contextual Orchestrator hosted tests require separately managed gateway credentials/deployment.
- Owned production statement coverage = 100%; owned production branch coverage = 100%.
- Every public production API has a beginner-readable complete docstring.
- Application-owned database objects use descriptive two-or-more-word names, preferably `snake_case`.
- Logs/ordinary telemetry exclude raw birth context, user notes, prompt/report text, credentials, and internal artifact paths by default.
- Report retention defaults to 30 days and terminal jobs support explicit deletion.
- PDF text is searchable and Korean glyphs render without redistributing proprietary font files.
- Standards/research traceability is maintained in APA 7th form; standards mapping is not a certification claim.
- Backup/restore, retention/deletion, incident, queue-age/failure and artifact-integrity responsibilities are defined in `docs/operations/OPERABILITY.md`.

## 6. Success metrics

- 100% pass rate for committed independent/golden calculation fixtures.
- 0 deterministic contradictions in released reports.
- At least 95% schema-valid first-pass responses for each approved backend/model route in its maintained evaluation set, with model availability/version stated.
- At least 90% of maintained evaluated reports score 3+ on completeness, balance, clarity, safety, and actionability, with deterministic fidelity fixed at the maximum category.
- <1% report-generation jobs end in an unclassified failure under the measured production/evaluation environment.
- 0 confidential personal-data fields in report-history items/cursors or prompt-safe organization attribution.
- 0 duplicate job identifiers while traversing one stable continuation sequence.
- A user can recover queued/running/completed/failed/quality-failed work without manually retaining a UUID outside the service.
- An operator can change interpretation adapter without changing deterministic calculation/artifact schemas.
- A reviewer can trace every material architecture claim to protected-main evidence, an Accepted ADR, an `active_pr`, or a `planned` item without reconstructing chat history.

## 7. Release scope and exclusions

Current protected-main product scope includes single-person natal/luck reporting, Korean output, deterministic calculation with independently checked modern solar-term evidence, direct NIM, optional Contextual Orchestrator, API/CLI/queue, recent-work recovery, idempotency, PDF/HTML/JSON, quality/security gates, Docker, CI, standards traceability, and product documentation.

`superseded`: PR #29 proposed an exact-head hourly PR steward but closed without merge. It is not part of shipped scope or current execution authority.

`planned`/excluded until separately reviewed: compatibility matching, payments, multi-tenant billing, consultant editing/collaboration UI, medical diagnosis, automatic high-stakes decisions, automatic provider fallback, scientific validation of traditional interpretation, and certification claims.

## 8. Principal risks and mitigations

- **Boundary calculation risk:** use independent fixtures, calculation versions and visible warnings rather than AI correction.
- **Hosted model variability:** bounded retries/repair, explicit backend/model identity and no silent fallback.
- **Overconfident symbolic prose:** deterministic editorial rules, conditional language and real-world evidence disclaimer.
- **Personal data persistence/disclosure:** purpose-bound data flow, opaque paths, authenticated redacted history, retention/deletion, restricted telemetry/attribution, operator controls.
- **Concurrent browser responses:** sequence guards and stale-response suppression.
- **Organization gateway recipient risk:** deployment-owned subprocessor/egress/region/retention documentation.
- **LLM-judge manipulation/bias:** supplementary role only; deterministic/human controls remain authoritative.
- **Architecture drift:** canonical maturity labels, ADR index, ERD/threat/test/operability documents and machine-checkable documentation contract.

## 9. Canonical product evidence

Technical implementation requirements live in `docs/technical/TRD.md`; system viewpoints in `docs/architecture/SYSTEM_ARCHITECTURE.md`; detailed UML in `docs/uml/architecture.md`; durable data in `docs/architecture/DATA_MODEL.md`; decisions in `docs/adr/README.md`; threats in `docs/security/THREAT_MODEL.md`; tests in `docs/technical/TEST_STRATEGY.md`; operations in `docs/operations/OPERABILITY.md`; standards/research in `docs/standards/REFERENCES.md` and `docs/standards/TRACEABILITY.md`; documentation fitness in `docs/standards/DOCUMENTATION_AUDIT.md`.
