# Four Pillars Product Requirements Document

## 1. Product vision

Four Pillars converts verified birth data into a transparent Korean manse calendar calculation and then produces a useful, readable report. The product must earn trust by showing exactly which calendar facts were calculated, where a solar-term boundary creates uncertainty, which statements are traditional symbolic interpretation, and which actions are ordinary planning techniques.

The product shall run independently as an application while routing repository-owned LLM interpretation through the shared Contextual Orchestrator bounded context. Model/provider routing must never alter deterministic evidence, report schemas, prompt provenance, quality gates, or artifact contracts. Provider credentials and provider selection are not Four Pillars product concerns.

## 2. Users

- **Individual reader:** wants a clear natal, ten-year, annual, or monthly report without having to learn technical terminology.
- **Professional consultant:** needs reproducible calculations, editable context, consistent report structure, recoverable recent work, and exportable files.
- **Platform integrator:** needs an authenticated API, job status and history, deterministic JSON, report artifacts, traceable prompt/virtual-model versions, and replaceable MSA adapters.
- **Operator:** needs health checks, retention, deletion, audit-friendly manifests, safe failure states, an explicit Contextual Orchestrator boundary, and prompt-safe model-usage visibility.

## 3. Core jobs to be done

1. Enter solar or Korean lunar birth data, timezone, gender policy, and optional time correction.
2. Verify year, month, day, and hour pillars together with solar-term boundaries and a calculation fingerprint.
3. Inspect daewoon, annual luck, and monthly luck without confusing Gregorian month boundaries with solar terms.
4. Generate a Korean report whose claims remain consistent with the calculation.
5. Receive constructive possibilities, cautions, decision criteria, and practical techniques rather than a list of warnings.
6. Recover a recent durable report job after a page refresh, client restart, or operational handoff without exposing stored birth information in the collection response.
7. Filter recent work by lifecycle status, append older pages, restore active polling, and download completed files from the browser without retaining an individual UUID outside the service.
8. Download JSON, HTML, PDF, and a generation manifest, then delete the job when it is no longer needed.
9. Run the application independently or inside a larger CWL deployment without copying provider routing into the product.

## 4. Functional requirements

### 4.1 Deterministic calculation

The service shall calculate solar and Korean lunar input, IANA timezone conversion, optional local mean/apparent solar correction, Li Chun year boundaries, twelve month-changing `jie` boundaries, configurable midnight or late-Zi day rollover, hour pillar, ten gods, hidden stems, twelve growth stages, element balance, and core stem/branch interactions. Unknown birth time shall leave the hour pillar unresolved. A boundary within six hours shall create a visible warning.

### 4.2 Luck calculations

The service shall calculate forward or reverse daewoon direction, start age from the relevant `jie`, eight configurable ten-year periods, Li Chun annual luck, and monthly luck that starts at the relevant `jie`. When gender is unspecified, the service shall return both direction scenarios rather than silently choosing one.

### 4.3 AI analysis and model orchestration

All repository-owned LLM generation and LLM evaluation shall cross the `ReportInterpreter` application port into Contextual Orchestrator. The repository-owned virtual model shall be `orchestrator/free`. An unavailable gateway or empty eligible free pool shall fail visibly and shall not fall through to a provider-native client or paid virtual route.

Four Pillars shall not expose provider selection, provider-native credentials, or provider fallback as product runtime configuration. Contextual Orchestrator owns provider discovery, free-pool eligibility, downstream routing, provider credentials, and test-time compute allocation.

AI prompts shall be versioned and cover natal, daewoon, annual, monthly, practical skills, synthesis, editorial repair, and judging. Calculations are immutable input. A model response must pass Pydantic schema validation and deterministic/editorial quality checks before rendering.

The product gateway shall use `CONTEXTUAL_ORCHESTRATOR_TOKEN`. Missing credentials or orchestration failures shall be visible job failures rather than implicit routing changes.

The gateway adapter shall send prompt-safe organizational attribution, including `service=four-pillars` and optional account, team, group, and company values. Attribution shall not contain subject labels, birth information, notes, calculation fingerprints, prompt or report text, artifact paths, or credentials.

Provider passthrough fields that collapse routed/conducted orchestration to one upstream provider shall be omitted from the repository-owned gateway request. JSON correctness shall be enforced through explicit prompting, Pydantic validation, and bounded same-route repair.

A platform integrator may inject a custom `ReportInterpreter` when that integrator owns a separate MSA boundary. This structural port does not make provider routing a Four Pillars configuration choice.

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

Repository-owned composition shall construct `ContextualOrchestratorReportInterpreter` only when a custom interpreter was not injected. Central `.github`, `naruon`, and other organization systems may compose or govern the service through documented interfaces without copying product-specific calculation and quality rules.

Repository-specific provider-credentialed autonomous writers shall not duplicate the organization-level CWL development loop. The local hourly workflow remains a model-free quality sentinel.

## 5. Non-functional requirements

- Deterministic calculation p95 under 250 ms for modern dates on one CPU core.
- Report job state remains recoverable after API restart.
- Report-history traversal remains stable for equal timestamps and does not repeat existing rows when new jobs are inserted during a continuation sequence.
- Browser history remains usable after a page refresh, rejects stale response races, and does not persist credentials or report data locally.
- Offline CI never requires an external LLM key.
- Hosted LLM tests are opt-in, use `CONTEXTUAL_ORCHESTRATOR_TOKEN` plus the gateway URL, and exercise `orchestrator/free` only.
- Hosted Four Pillars workflows do not receive provider-native model credentials.
- Production statement and branch coverage remain exactly 100 percent.
- Every public production API has a complete docstring.
- API authentication can be enabled with a SHA-256 API-key digest.
- Logs exclude raw birth context and generated report text by default.
- Published model traces exclude credentials and raw generated content.
- Report retention defaults to 30 days and terminal jobs can be deleted immediately.
- PDF text remains searchable and Korean glyphs render without shipping proprietary font files.
- Application-owned database objects use two-or-more-word names, preferably `snake_case`.
- Standards and peer-reviewed research traceability is maintained in APA 7th form and checked hourly.
- DDD path audits flag provider-specific infrastructure names that remain around provider-neutral boundaries and require coherent code/test/doc moves.

## 6. Success metrics

- 100 percent pass rate for committed golden calculation fixtures.
- 0 deterministic contradictions in released reports.
- At least 95 percent schema-valid first-pass responses for the approved `orchestrator/free` evaluation set.
- At least 90 percent of evaluated reports score 3 or higher on completeness, balance, clarity, safety, and actionability, with deterministic fidelity fixed at 4.
- Less than 1 percent report-generation jobs end in an unclassified failure.
- 0 personal-data fields in report-history items, cursors, browser history rows, or orchestrator usage attribution.
- 0 duplicate job identifiers while traversing a stable continuation sequence.
- 0 repository-owned direct-provider LLM calls or provider-native runtime credentials.
- 0 `orchestrator/free` requests that silently cross to a paid product route when no eligible free model exists.
- A user can recover an existing queued, running, completed, or failed job from the browser without re-entering its UUID.
- A platform integrator can replace the injected `ReportInterpreter` without changing deterministic calculation or artifact formats.
- User can identify the relevant calculation evidence and one practical next step from each major chapter.

## 7. Release scope

The current target product includes one-person natal and luck reporting, Korean output, Contextual Orchestrator `orchestrator/free` integration, API, CLI, queue, recent-work recovery, PDF/HTML/JSON output, quality gates, Docker, CI, standards traceability, DDD architecture-fitness checks, and product documentation.

Historical direct-provider compatibility code may remain temporarily as test infrastructure while the provider-specific `nim.py` namespace is migrated. It is not part of the supported product runtime.

Compatibility matching, payments, multi-tenant billing, consultant editing UI, event prediction, medical diagnosis, automatic decisions, direct provider fallback, paid-route escalation from `orchestrator/free`, ISO certification, and scientific validation of traditional interpretation are deliberately excluded until separate requirements and safety review exist.

## 8. Risks and mitigations

Approximate solar longitude can be least reliable at a boundary, so the product emits a six-hour warning and records the policy. Hosted free-model availability can vary, so the Contextual Orchestrator client retries transient gateway errors within a bound and fails explicitly when no eligible route remains. Symbolic text can sound deterministic, so quality checks require conditional language and real-world decision disclaimers.

Personal data can persist in output, so storage uses UUIDs, retention, explicit deletion, restricted logs, redacted history items, cursors containing only UTC timestamps and random job UUIDs, safe browser rendering, and prompt-safe organizational attribution. Concurrent browser requests can complete out of order, so only the latest history request may update the visible collection.

Contextual Orchestrator may route among multiple approved free providers, so orchestration owners must document subprocessors, egress restrictions, retention, free-eligibility policy, model availability, and incident responsibilities. Four Pillars does not solve provider governance by bypassing the gateway. LLM-as-a-judge methods can be adversarially manipulated or biased, so they remain supplementary to deterministic and human controls.

The current `nim.py` filename is an architectural-debt signal because the active orchestration boundary is provider-neutral. The next bounded DDD refactor shall move that infrastructure together with imports, tests, UML, compatibility exports, and coverage evidence rather than performing a partial rename.

The standards crosswalk is maintained for engineering governance and continual improvement. It is not an accredited certification or evidence that traditional Four Pillars interpretation predicts individual outcomes scientifically.
