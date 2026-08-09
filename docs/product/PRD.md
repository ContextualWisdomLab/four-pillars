# Four Pillars Product Requirements Document

## 1. Product vision

Four Pillars converts verified birth data into a transparent Korean manse calendar calculation and then produces a useful, readable report. The product must earn trust by showing exactly which calendar facts were calculated, where a solar-term boundary creates uncertainty, which statements are traditional symbolic interpretation, and which actions are ordinary planning techniques.

The product shall work independently with direct hosted NVIDIA NIM and as an organization module through Contextual Orchestrator. Model routing must never alter deterministic evidence, report schemas, prompt provenance, quality gates, or artifact contracts.

The repository and service are treated as one commercial product surface: calculation correctness, report usefulness, privacy/security, operator recoverability, release provenance, autonomous-maintenance governance, and code-current documentation are all part of product quality. Traditional Four Pillars interpretation remains symbolic and conditional; engineering standards do not make it scientifically predictive.

## 2. Users

- **Individual reader:** wants a clear natal, ten-year, annual, or monthly report without having to learn technical terminology.
- **Professional consultant:** needs reproducible calculations, editable context, consistent report structure, recoverable recent work, and exportable files.
- **Platform integrator:** needs an authenticated API, job status and history, deterministic JSON, report artifacts, traceable prompt/model versions, and replaceable MSA adapters.
- **Operator:** needs health checks, retention, deletion, audit-friendly manifests, safe failure states, explicit backend selection, prompt-safe model-usage visibility, and recovery/runbook evidence.
- **Security/compliance owner:** needs purpose-bound personal-data handling, least privilege, traceable releases, supply-chain evidence, and a truthful CSAP/SOC 2 readiness map without false certification claims.
- **Maintainer/reviewer:** needs exact-head evidence, bounded autonomous proposals/repairs, independent review authority, machine-checkable documentation contracts, and no need to reconstruct architecture from chat history.

## 3. Core jobs to be done

1. Enter solar or Korean lunar birth data, timezone, gender policy, and optional time correction.
2. Verify year, month, day, and hour pillars together with solar-term boundaries and a calculation fingerprint.
3. Inspect daewoon, annual luck, and monthly luck without confusing Gregorian month boundaries with solar terms.
4. Generate a Korean report whose claims remain consistent with the calculation.
5. Receive constructive possibilities, cautions, decision criteria, and practical techniques rather than a list of warnings.
6. Recover a recent durable report job after a page refresh, client restart, or operational handoff without exposing stored birth information in the collection response.
7. Filter recent work by lifecycle status, append older pages, restore active polling, and download completed files from the browser without retaining an individual UUID outside the service.
8. Download JSON, HTML, PDF, and a generation manifest, then delete the job when it is no longer needed.
9. Run the product independently or route interpretation through an approved organization gateway without forking calculation or report code.
10. Operate and maintain the repository through exact-head CI/review/release controls without giving a model path reviewer, merge, release, or deployment authority.
11. Reconstruct the product's current requirements, architecture, data model, trust boundaries, decisions, operations, and evidence from GitHub documentation alone.

## 4. Functional requirements

### 4.1 Deterministic calculation

The service shall calculate solar and Korean lunar input, IANA timezone conversion, optional local mean/apparent solar correction, Li Chun year boundaries, twelve month-changing `jie` boundaries, configurable midnight or late-Zi day rollover, hour pillar, ten gods, hidden stems, twelve growth stages, element balance, and core stem/branch interactions. Unknown birth time shall leave the hour pillar unresolved. A boundary within six hours shall create a visible warning.

Boundary-critical modern calculations shall be independently testable against committed authoritative evidence rather than only against the implementation itself. The current calculation evidence version is `calendar-1.1.0`; all twelve 2026 `jie` boundaries are validated against KASI and independently corroborated NAOJ minute values, with signed timing deltas and buyer-visible transition tests around the boundaries.

### 4.2 Luck calculations

The service shall calculate forward or reverse daewoon direction, start age from the relevant `jie`, eight configurable ten-year periods, Li Chun annual luck, and monthly luck that starts at the relevant `jie`. When gender is unspecified, the service shall return both direction scenarios rather than silently choosing one.

### 4.3 AI analysis and backend selection

Direct NVIDIA NIM shall remain the standalone default for LLM generation and LLM evaluation. An operator may explicitly select Contextual Orchestrator as an OpenAI-compatible organization gateway for report generation. No backend may silently fail over to another provider or adapter.

AI prompts shall be versioned and cover natal, daewoon, annual, monthly, practical skills, synthesis, editorial repair, and judging. Calculations are immutable input. A model response must pass Pydantic schema validation and deterministic/editorial quality checks before rendering.

The direct backend shall use only `NVIDIA_NIM_API_KEY`. The optional gateway shall use only `CONTEXTUAL_ORCHESTRATOR_TOKEN`. Missing credentials or backend failures shall be visible job failures rather than implicit routing changes.

The gateway adapter shall send prompt-safe organizational attribution, including `service=four-pillars` and optional account, team, group, and company values. Attribution shall not contain subject labels, birth information, notes, calculation fingerprints, prompt or report text, artifact paths, or credentials.

Contextual Orchestrator may execute route/conduct behavior behind its explicit boundary. Four Pillars shall not force provider-native JSON response mode when that would collapse orchestration into a single-agent passthrough; it shall instead require JSON in the prompt, validate the returned content against Pydantic schemas, and perform only the bounded configured repair on the same selected backend.

### 4.4 Report quality

Every required chapter shall contain a summary, constructive possibilities, cautions, and actions. The relationship chapter shall explain how trust, cooperation, or stability can improve. Copy shall use explicit subjects, objects, reasons, and dates. The service shall reject event certainty, diagnosis, treatment instructions, coercive life decisions, false authority claims, narrow one-off questions presented as universal rules, and known malformed phrases.

LLM-as-a-judge output shall remain supplementary. Deterministic fixtures, Pydantic schemas, rule-based quality checks, security review, and human review shall not be bypassed by a judge score.

### 4.5 Outputs and interfaces

The service shall provide FastAPI endpoints, a CLI, a durable SQLite job queue, a worker, calculation JSON, report JSON, searchable Korean HTML and A4 PDF, model/prompt traces, and SHA-256 file manifests. Artifacts shall be stored under random job identifiers without personal data in filenames.

The authenticated report API shall provide a redacted newest-first job collection with exact lifecycle-status filtering and opaque keyset continuation. Collection items and cursors shall exclude subject labels, birth input, user notes, stored requests, request fingerprints, idempotency material, generated report text, model traces, and artifact paths. The required repository contract shall remain backward compatible; history traversal shall be a separate optional capability for standalone and MSA adapters.

The browser studio shall present the collection as a responsive third workflow section based on the editable Figma desktop and mobile design. It shall load the latest 20 jobs, refresh the first page, filter by exact public status, append older pages from `next_cursor`, resume polling for queued or running jobs, and expose only server-supplied allow-listed artifact names for completed jobs. Authentication, cursor validation, ordering, privacy redaction, and adapter capability checks remain server-owned.

The browser shall render API-derived values only through safe DOM text APIs. It shall suppress stale asynchronous history responses, bound displayed operational-error copy, announce history updates through a polite live region, communicate status with text as well as color, and keep the API key only in current page memory. Authenticated artifact downloads shall use an in-memory request header rather than credentials in URLs or persistent browser storage.

### 4.6 Modular and organization integration

The calculation package shall import without creating a database, HTTP client, worker, application directory, or model connection. `ReportJobRepository`, `ReportInterpreter`, `ArtifactPublisher`, idempotency, and history capabilities shall remain structural and independently replaceable.

Settings-based interpretation selection shall apply only when a custom interpreter was not injected. Central `.github`, `naruon`, and other organization systems may compose or govern the service through documented versioned interfaces without copying product-specific calculation and quality rules or directly accessing Four Pillars application tables.

### 4.7 Personal-data governance and compliance readiness

Four Pillars shall not rely on blanket PII masking when masking would destroy deterministic calculation or personalized-report functionality. It shall preserve purpose-required values only inside authorized processing boundaries and minimize their propagation elsewhere.

Required principles include purpose classification, minimum payload per component, opaque public identifiers, authentication/authorization independent of network location, restricted identity linkage, TLS, production encryption-at-rest and separated key management, least privilege, bounded retention, deletion/export controls, auditable privileged/break-glass access, processor/region/egress documentation, and no raw birth/context/report content in public history, routine telemetry, usage attribution, filenames, or credentials.

The product shall maintain CSAP and SOC 2 engineering-readiness mappings without claiming certification or attestation. A real external assessment additionally requires organizational scope, policies, control owners, deployment configuration, operating evidence, vendor management, incident/backup/access-review evidence, and independent assessment.

### 4.8 Repository control plane and documentation authority

The implemented minute-17 deterministic quality sentinel and minute-47 NVIDIA/OpenCode product-development workflow have separate responsibilities and credential boundaries. The model-backed developer may propose a bounded pull request but cannot approve, merge, release, deploy, or act as an independent reviewer. A minute-07 exact-head PR steward is Proposed until its implementation reaches protected `main`; documentation and diagrams shall not describe it as shipped before then.

All autonomous development that invokes a model shall use `NVIDIA_NIM_API_KEY`, never `COPILOT_GITHUB_TOKEN`, and shall preserve existing review-agent identities and credential chains. Exact head/base/ref and immutable proposal evidence shall be revalidated before writes or governed merges. Waiting for checks or reviews does not authorize bypass and does not block non-conflicting work.

The repository shall maintain the authoritative documentation graph in `docs/architecture/DOCUMENTATION_MAP.md`, including PRD, TRD, root architecture, ADR index/records, UML, conceptual/logical ERD, API/calculation/modularity contracts, personal-data/security/compliance documents, operations, standards/doctoring/traceability, Figma references, AGENTS/CLAUDE, and CHANGELOG. Contradictions with protected-main code are repository defects.

## 5. Non-functional requirements

- Deterministic calculation p95 under 250 ms for modern dates on one CPU core.
- Report job state remains recoverable after API restart.
- Report-history traversal remains stable for equal timestamps and does not repeat existing rows when new jobs are inserted during a continuation sequence.
- Browser history remains usable after a page refresh, rejects stale response races, and does not persist credentials or report data locally.
- Offline CI never requires an external LLM key.
- Direct hosted NIM tests are opt-in and use the `NVIDIA_NIM_API_KEY` repository secret.
- A hosted Contextual Orchestrator test requires a separately deployed gateway and separately managed token.
- Production statement and branch coverage remain exactly 100 percent.
- Every public production API has a complete docstring.
- API authentication can be enabled with a SHA-256 API-key digest.
- Logs exclude raw birth context and generated report text by default.
- Model traces exclude credentials and raw generated content from published trace metadata.
- Report retention defaults to 30 days and terminal jobs can be deleted immediately.
- PDF text remains searchable and Korean glyphs render without shipping proprietary font files.
- Application-owned database objects use two-or-more-word names, preferably `snake_case`.
- Standards and peer-reviewed research traceability is maintained in APA 7th form and checked hourly.
- KASI/NAOJ calculation fixtures remain committed, offline, independently reviewable, and versioned with the calculation policy.
- Documentation must distinguish Current/Accepted/Proposed/Planned behavior and remain consistent with protected-main code.
- Repository automation must preserve model/proposal, verification, independent review, merge and release authority separation.
- Production deployment profiles handling personal data must document encryption-at-rest/key ownership, authorization scope, retention/deletion/export, backup semantics, subprocessors/regions and privileged-access controls before those profiles are advertised as enterprise/public-sector ready.

## 6. Success metrics

- 100 percent pass rate for committed golden calculation fixtures, including all externally sourced 2026 KASI/NAOJ `jie` fixtures.
- 0 deterministic contradictions in released reports.
- At least 95 percent schema-valid first-pass responses for each approved backend/model route in its evaluation set.
- At least 90 percent of evaluated reports score 3 or higher on completeness, balance, clarity, safety, and actionability, with deterministic fidelity fixed at 4.
- Less than 1 percent report-generation jobs end in an unclassified failure.
- 0 personal-data fields in report-history items, cursors, routine browser history rows, or orchestrator usage attribution.
- 0 duplicate job identifiers while traversing a stable continuation sequence.
- A user can recover an existing queued, running, completed, or failed job from the browser without re-entering its UUID.
- A platform operator can change the selected interpretation adapter without changing deterministic calculation or artifact formats.
- User can identify the relevant calculation evidence and one practical next step from each major chapter.
- 100 percent of canonical architecture/requirements/ADR/ERD/UML links required by the documentation contract are present and code-current at release.
- 0 autonomous model paths possess reviewer/merge/release/deployment authority.
- 0 release claims state CSAP/SOC 2/ISO certification or scientific predictive validation without external evidence.

## 7. Release scope

The current protected-main product includes one-person natal and luck reporting, Korean output, direct NIM and optional Contextual Orchestrator integration, API, CLI, queue, recent-work recovery, PDF/HTML/JSON output, quality gates, Docker, CI, KASI/NAOJ-backed modern solar-term evidence, standards traceability, and the minute-17/minute-47 repository control planes.

The minute-07 PR steward is Proposed while its PR remains unmerged. PostgreSQL/object-storage multi-node adapters, RFC 9457 problem responses, W3C Trace Context, tenant-scoped enterprise authorization, production KMS/break-glass evidence, consultant editing UI, compatibility matching, payments, multi-tenant billing, event prediction, medical diagnosis, automatic provider fallback, accredited certifications, and scientific validation of traditional interpretation are deliberately excluded until separate requirements, implementation and safety/release review exist.

## 8. Risks and mitigations

Approximate or incorrectly implemented solar longitude can be least reliable at a boundary, so the product uses a bounded VSOP87 apparent-solar-longitude implementation, independently sourced KASI/NAOJ fixtures, signed deltas, transition tests, a six-hour user warning, and an explicit calculation evidence version. Historical timezone and pre-1972 timescale limitations remain explicit.

Hosted model availability can vary, so the selected client retries transient errors and never falls back silently. Symbolic text can sound deterministic, so quality checks require conditional language and real-world decision disclaimers.

Personal data must remain usable for authorized calculation/reporting, so privacy is enforced by purpose-bound payloads, authorization, restricted linkage, opaque IDs, encryption/secret boundaries, retention/deletion/export, provider boundaries and governed privileged access rather than blanket masking. Current single-node source controls do not by themselves establish production KMS, tenant isolation, backup deletion or external certification; those remain deployment gaps.

Concurrent browser requests can complete out of order, so only the latest history request may update the visible collection. Contextual Orchestrator may route to multiple organization-approved providers, so deployment owners must document subprocessors, egress restrictions, retention, model availability, and incident responsibilities. LLM-as-a-judge methods can be adversarially manipulated or biased, so they remain supplementary to deterministic and human controls.

Autonomous repository development can create supply-chain or authority risk, so model execution, artifact verification, PR publication, independent review, merge and release remain separate. Proposed automation is never represented as implemented before protected-main integration.

The standards crosswalk is maintained for engineering governance and continual improvement. It is not an accredited certification or evidence that traditional Four Pillars interpretation predicts individual outcomes scientifically.
