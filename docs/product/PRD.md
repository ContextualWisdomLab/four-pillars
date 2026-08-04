# Four Pillars Product Requirements Document

## 1. Product vision

Four Pillars converts verified birth data into a transparent Korean manse calendar calculation and then produces a useful, readable report. The product must earn trust by showing exactly which calendar facts were calculated, where a solar-term boundary creates uncertainty, which statements are traditional symbolic interpretation, and which actions are ordinary planning techniques.

## 2. Users

- **Individual reader:** wants a clear natal, ten-year, annual, or monthly report without having to learn technical terminology.
- **Professional consultant:** needs reproducible calculations, editable context, consistent report structure, recoverable recent work, and exportable files.
- **Platform integrator:** needs an authenticated API, job status and history, deterministic JSON, report artifacts, and traceable prompt/model versions.
- **Operator:** needs health checks, retention, deletion, audit-friendly manifests, safe failure states, and NIM cost visibility.

## 3. Core jobs to be done

1. Enter solar or Korean lunar birth data, timezone, gender policy, and optional time correction.
2. Verify year, month, day, and hour pillars together with solar-term boundaries and a calculation fingerprint.
3. Inspect daewoon, annual luck, and monthly luck without confusing Gregorian month boundaries with solar terms.
4. Generate a Korean report whose claims remain consistent with the calculation.
5. Receive constructive possibilities, cautions, decision criteria, and practical techniques rather than a list of warnings.
6. Recover a recent durable report job after a page refresh, client restart, or operational handoff without exposing stored birth information in the collection response.
7. Download JSON, HTML, PDF, and a generation manifest, then delete the job when it is no longer needed.

## 4. Functional requirements

### 4.1 Deterministic calculation

The service shall calculate solar and Korean lunar input, IANA timezone conversion, optional local mean/apparent solar correction, Li Chun year boundaries, twelve month-changing `jie` boundaries, configurable midnight or late-Zi day rollover, hour pillar, ten gods, hidden stems, twelve growth stages, element balance, and core stem/branch interactions. Unknown birth time shall leave the hour pillar unresolved. A boundary within six hours shall create a visible warning.

### 4.2 Luck calculations

The service shall calculate forward or reverse daewoon direction, start age from the relevant `jie`, eight configurable ten-year periods, Li Chun annual luck, and monthly luck that starts at the relevant `jie`. When gender is unspecified, the service shall return both direction scenarios rather than silently choosing one.

### 4.3 AI analysis

Only NVIDIA NIM shall be used for LLM generation and LLM evaluation. AI prompts shall be versioned and cover natal, daewoon, annual, monthly, practical skills, synthesis, editorial repair, and judging. Calculations are immutable input. A model response must pass Pydantic schema validation and deterministic/editorial quality checks before rendering.

### 4.4 Report quality

Every required chapter shall contain a summary, constructive possibilities, cautions, and actions. The relationship chapter shall explain how trust, cooperation, or stability can improve. Copy shall use explicit subjects, objects, reasons, and dates. The service shall reject event certainty, diagnosis, treatment instructions, coercive life decisions, false authority claims, narrow one-off questions presented as universal rules, and known malformed phrases.

### 4.5 Outputs and interfaces

The service shall provide FastAPI endpoints, a CLI, a durable SQLite job queue, a worker, calculation JSON, report JSON, searchable Korean HTML and A4 PDF, model/prompt traces, and SHA-256 file manifests. Artifacts shall be stored under random job identifiers without personal data in filenames.

The authenticated report API shall provide a redacted newest-first job collection with exact lifecycle-status filtering and opaque keyset continuation. Collection items and cursors shall exclude subject labels, birth input, user notes, stored requests, request fingerprints, idempotency material, generated report text, model traces, and artifact paths. The required repository contract shall remain backward compatible; history traversal shall be a separate optional capability for standalone and MSA adapters.

## 5. Non-functional requirements

- Deterministic calculation p95 under 250 ms for modern dates on one CPU core.
- Report job state remains recoverable after API restart.
- Report-history traversal remains stable for equal timestamps and does not repeat existing rows when new jobs are inserted during a continuation sequence.
- Offline CI never requires an external LLM key.
- Live NIM tests are opt-in and use a repository secret.
- Production statement and branch coverage remain exactly 100 percent.
- Every public production API has a complete docstring.
- API authentication can be enabled with a SHA-256 API-key digest.
- Logs exclude raw birth context and generated report text by default.
- Report retention defaults to 30 days and terminal jobs can be deleted immediately.
- PDF text remains searchable and Korean glyphs render without shipping proprietary font files.

## 6. Success metrics

- 100 percent pass rate for committed golden calculation fixtures.
- 0 deterministic contradictions in released reports.
- At least 95 percent schema-valid first-pass NIM responses in the evaluation set.
- At least 90 percent of evaluated reports score 3 or higher on completeness, balance, clarity, safety, and actionability, with deterministic fidelity fixed at 4.
- Less than 1 percent report-generation jobs end in an unclassified failure.
- 0 personal-data fields in report-history items and cursors.
- 0 duplicate job identifiers while traversing a stable continuation sequence.
- User can identify the relevant calculation evidence and one practical next step from each major chapter.

## 7. Release scope

Version 0.1 includes one-person natal and luck reporting, Korean output, NIM integration, API, CLI, queue, PDF/HTML/JSON output, quality gates, Docker, CI, and product documentation. Compatibility matching, payments, multi-tenant billing, consultant editing UI, event prediction, medical diagnosis, and automatic decisions are deliberately excluded until separate requirements and safety review exist.

## 8. Risks and mitigations

Approximate solar longitude can be least reliable at a boundary, so the product emits a six-hour warning and records the policy. NIM availability can vary, so the client retries transient errors and never falls back to a different provider silently. Symbolic text can sound deterministic, so quality checks require conditional language and real-world decision disclaimers. Personal data can persist in output, so storage uses UUIDs, retention, explicit deletion, restricted logs, redacted history items, and cursors containing only UTC timestamps and random job UUIDs.
