# Four Pillars Test Strategy

**Maturity:** current release-quality requirements are `implemented_on_protected_main`; this document makes the evidence contract independently auditable.

## 1. Test objective

Testing must prove that Four Pillars produces deterministic calendar/luck evidence according to its declared policies, keeps interpretation subordinate to that evidence, protects personal/context data across public interfaces, survives realistic queue/retry/recovery cases, and can be packaged/released reproducibly enough for the supported deployment profile.

A test is not meaningful merely because it increases coverage. Assertions must exercise a real product, security, calculation, compatibility, or operational invariant.

## 2. Evidence hierarchy

1. Independent authoritative/golden calendar evidence and explicit calculation policy.
2. Deterministic property/boundary tests over the production calculation implementation.
3. API/persistence/artifact/security integration tests.
4. Offline structured-generation contract tests with controlled transports.
5. Bounded hosted NIM conformance/evaluation tests on trusted workflows.
6. LLM-as-a-judge or qualitative model scores as supplementary evidence only.

The system must not validate a calculation solely by comparing it with another code path that copied the same formula or fixture.

## 3. Calculation accuracy suite

### 3.1 Independent solar-term evidence

All month-changing solar terms used by production policy require committed external evidence. The current modern-date reference set uses **KASI** and **NAOJ** publication evidence. For 2026, all twelve `jie` instants are checked against independently transcribed source evidence and the bounded VSOP87 implementation has a minute-level error budget.

Tests must preserve source identity, source timestamp/calendar convention, expected instant, observed delta, and the calculation evidence version. A source disagreement is recorded and investigated; the fixture is not silently changed to match production output.

### 3.2 Boundary transition tests

Realistic tests must cover both sides of every material boundary, including:

- **Li Chun** year-pillar transition;
- each month-changing **jie boundary**;
- ±5 minute buyer-visible transition checks and the wider six-hour warning policy;
- configured midnight versus late-Zi day rollover;
- time-zone offsets around UTC date changes;
- leap-day/Gregorian calendar behavior within the supported range;
- Korean lunar conversion and leap-month cases supported by the dependency;
- unknown birth time leaving the hour pillar unresolved;
- local mean/apparent solar-time correction when configured;
- annual luck changing at Li Chun rather than January 1;
- January solar-term month using the correct pre-Li-Chun stem-year context.

### 3.3 Known chart/luck fixtures

Committed golden chart cases must include visible year/month/day/hour pillars and derived relations. At least the previously validated modern examples and annual/monthly examples remain covered. A change to a golden value requires a calculation-policy explanation and evidence-version review, not a prompt update.

### 3.4 Derived relation properties

Ten Gods, hidden stems, Twelve Growth stages, element balance, and stem/branch interactions require table/property tests that cover every supported stem/branch category, not only hand-picked report examples.

## 4. AI/LLM test separation

### Offline contract tests

Ordinary pull-request CI must not need a model key. Mock transport tests cover:

- Bearer authentication header construction;
- endpoint/base URL behavior;
- structured JSON response mode;
- strict Pydantic schema validation;
- bounded repair after malformed model output;
- 408/429/5xx retry classification and `Retry-After` behavior;
- terminal 4xx failure;
- explicit direct-NIM versus Contextual Orchestrator selection;
- separate credential names;
- no silent provider fallback;
- prompt-safe organization attribution;
- prompt injection/user-context separation.

### Hosted tests

Live model tests run only on trusted workflows and use GitHub Secret `NVIDIA_NIM_API_KEY`. They are excluded from untrusted fork PRs and from deterministic release-quality claims when the secret is unavailable.

A hosted test evaluates the exact configured model/endpoint contract and report-schema/quality behavior; it does not certify the model generally. Generation and judge models should be separately configurable where useful.

### Orchestration ablation

When Contextual Orchestrator conduct/routing changes materially, evaluate comparable work across at least:

- direct/single-model route;
- staged review/repair;
- deeper multi-agent conduct when justified.

Record workflow stages, recursion limits, task decomposition, access list, role-specific reasoning effort, token/compute budget, deterministic fidelity, schema success, unsupported-claim rate, balance/clarity/actionability, and failure recovery. Use Fugu/Conductor/TRINITY-class research as architectural evidence where applicable, but do not make model-specific quality claims without repository evaluation data.

## 5. Report-quality suite

Deterministic editorial tests require:

- every required chapter;
- summary, constructive possibilities, cautions, and actions;
- relationship chapter includes positive trust/cooperation/stability possibilities rather than warnings only;
- explicit subjects/objects/referents where ambiguity matters;
- no known malformed phrases;
- no certain future-event claims;
- no diagnosis/treatment instructions;
- no false claim that a calendar app/model is authoritative evidence;
- disclaimer that real-world decisions rely on real-world evidence.

The quality gate must reject a report whose calculation fingerprint or deterministic facts do not match the source evidence.

## 6. Persistence and concurrency suite

Test SQLite and repository-port contracts for:

- atomic job creation/claim;
- restart-visible queued/running/terminal state;
- idempotent same-key/same-payload replay;
- same-key/different-payload rejection;
- concurrent idempotent submissions creating at most one durable job;
- stable newest-first history under equal timestamps;
- exact status filtering;
- continuation while new rows are inserted;
- malformed/unsupported cursors fail closed;
- retention cleanup and explicit terminal deletion;
- no public-history serialization of `request_json`, fingerprints, idempotency material, generated content, traces, or internal paths.

Any future multi-node repository must run the same behavioral contract plus crash/retry/transaction-isolation tests appropriate to the backend.

## 7. Artifact/rendering suite

Test searchable Korean HTML/PDF/JSON generation for:

- HTML escaping;
- Korean glyph rendering using supported system/CID fonts without redistributing font files;
- no default footer/page number when the product contract says none;
- long text/page flow without clipping;
- staged publication and cleanup after failure;
- allow-listed artifact retrieval;
- manifest SHA-256 integrity;
- no personal data in artifact directory names.

Visual Inspection is required for material report-template changes. Figma is used when the product workflow/design changes rather than merely for wording edits.

## 8. Security/privacy suite

Include tests for:

- API-key digest authentication and constant-time comparison;
- path traversal/symlink/artifact allow-list boundaries;
- hostile Unicode/control characters where inputs cross security-sensitive metadata boundaries;
- HTML/script injection in displayed user context;
- user-context prompt injection as data, not instruction;
- direct NIM and orchestrator secret separation;
- no `NVIDIA_NIM_API_KEY` in logs/artifacts/traces;
- no `COPILOT_GITHUB_TOKEN` in autonomous-development workflows;
- purpose-bound public history/attribution redaction without blanket masking of calculation-required input;
- bounded operational errors;
- branch/exact-head and immutable artifact identity in autonomous development.

Security Scan, dependency review, SAST/Semgrep, and container/dependency integrity complement rather than replace application tests.

## 9. Coverage and docstring policy

Release-quality CI requires **100% production statement** coverage and **100% production branch** coverage for owned production Python code. Public production APIs require complete beginner-readable docstrings. Coverage may not be achieved by excluding meaningful production branches, marking realistic failures unreachable, or asserting only mock setup.

Scripts that constitute security/release control logic require direct tests appropriate to their threat boundary even when they are outside the runtime coverage measurement set.

## 10. Compatibility matrix

Current protected-main CI supports Python 3.11 and 3.12. A future Python-version change requires dependency resolution, package installation, unit/integration tests, and wheel/container smoke evidence before declaring support.

The product's external calculation range must remain explicit. Historical timezone/pre-1972 timescale limitations are tested/documented rather than hidden behind a broad “all dates” claim.

## 11. Performance and resource tests

At minimum, deterministic chart calculation p95 is measured against the PRD target on representative modern inputs without an LLM call. Report-generation latency is model/provider dependent and should be decomposed into queue time, calculation, model stages, quality/repair, rendering, and publication rather than treated as one opaque number.

Test resource bounds for request/history page size, prompt/output schema limits, error/log sizes, and report artifacts when a change touches those boundaries.

## 12. Release acceptance

A release candidate must be bound to the exact integrated protected-main commit and prove:

- Ruff and compilation;
- document/prompt consistency checks;
- all offline tests;
- **100% production statement** and **100% production branch** coverage;
- package build and installed-artifact smoke test where configured;
- runtime container build/import metadata;
- security/dependency/SAST gates required by repository policy;
- no valid unresolved review findings;
- version/CHANGELOG consistency;
- source/wheel checksums and repository release provenance/attestation gates where configured;
- operational acceptance for changed scheduler/recovery/release paths.

A queued, skipped-required, cancelled, stale-head, predecessor-head, synthetic-only, rate-limited, or failed check is not success.

## 13. References — APA 7th

International Organization for Standardization. (2023). *ISO/IEC 25010:2023 Systems and software engineering—Systems and software Quality Requirements and Evaluation (SQuaRE)—Product quality model* (2nd ed.). ISO.

Scarfone, K., Souppaya, M., & Dodson, D. (2022). *Secure Software Development Framework (SSDF) Version 1.1: Recommendations for mitigating the risk of software vulnerabilities* (NIST SP 800-218). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-218
