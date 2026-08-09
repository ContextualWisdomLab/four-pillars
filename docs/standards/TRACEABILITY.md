# Standards Traceability and Control Evidence

This document maps applicable international standards, public frameworks, authoritative calendar evidence, peer-reviewed evaluation findings, Korean cloud-assurance guidance, and architecture/requirements notation sources to concrete Four Pillars controls. It is an engineering traceability record, not a certificate, legal opinion, medical claim, or scientific validation of traditional interpretation.

## 1. System context

Four Pillars has four runtime trust boundaries:

1. **Deterministic calculation:** validated birth input produces immutable chart and luck evidence with a SHA-256 fingerprint.
2. **Interpretation:** direct NVIDIA NIM or optional Contextual Orchestrator explains that evidence through versioned prompts and strict Pydantic schemas. `StructuredGenerationClient` is the structural model-client port and `ContextualOrchestratorClient` is the organization-gateway implementation.
3. **Quality:** deterministic/editorial rules reject unsupported pillars, missing sections, warning-only relationship copy, vague language, medical directions, coercive decisions, false authority, and event certainty.
4. **Delivery:** only approved reports become JSON, HTML, PDF, trace, and manifest artifacts under random job identifiers.

Repository operations add separate **proposal/repair**, **verification**, **independent review**, **merge**, and **release** authority zones. These are modeled in `docs/uml/control-plane.md`; no model output or green check alone collapses those authorities.

Traditional Four Pillars analysis is presented as symbolic and conditional. Deterministic calendar correctness is testable; generated life guidance is not represented as experimentally established prediction.

## 2. Architecture and requirements description

### ISO/IEC/IEEE 42010:2022

Four Pillars applies architecture-description separation through multiple explicit viewpoints:

| Concern/viewpoint | Canonical model |
|---|---|
| Stakeholder/product requirements | `docs/product/PRD.md` |
| Technical requirements and interfaces | `docs/technical/TRD.md` |
| Bounded contexts and deployment | `ARCHITECTURE.md` |
| Durable architecture decisions | `docs/adr/README.md` and numbered ADRs |
| Runtime component/sequence/state views | `docs/uml/architecture.md` |
| Repository automation authority | `docs/uml/control-plane.md` |
| Persistence and conceptual information model | `docs/erd/domain-model.md` |
| Documentation authority/update triggers | `docs/architecture/DOCUMENTATION_MAP.md` |

The standard informs the structure and expression of architecture descriptions; this project does not claim formal conformance assessment.

### ISO/IEC/IEEE 29148:2018

PRD/TRD/API/calculation/modularity documents separate stakeholder/product requirements from technical implementation constraints and acceptance evidence. As of the 2026-08-09 review, ISO lists Edition 2 (2018) as the published current edition, confirmed in 2024, while Edition 3 is at DIS stage. Four Pillars monitors the revision but does not treat the DIS as a published normative replacement.

### OMG UML 2.5.1

Mermaid and PlantUML are implementation notations; OMG UML 2.5.1 is the reference for UML concepts used by class, component, sequence, state and deployment views. Diagram source is committed and reviewable rather than maintained only as exported images.

## 3. ISO/IEC 25010:2023 product-quality crosswalk

| Quality concern | Four Pillars control | Verification evidence | Residual limitation |
|---|---|---|---|
| Functional suitability | Golden four-pillar fixtures, externally published KASI/NAOJ `jie` instants, Li Chun/month transitions, ten-god/luck calculations, immutable report evidence | `tests/test_calendar.py`, `tests/test_solar_term_golden.py`, `tests/test_fortune.py`, edge tests | Modern minute-precision evidence is not research-grade historical ephemeris certification |
| Performance efficiency | Deterministic calculation has no network dependency; long model calls run in a worker | calculation unit tests, API/worker separation | Hosted model latency is provider-dependent |
| Compatibility | FastAPI/JSON interfaces, OpenAI-compatible model adapters, structural repository/interpreter/publisher ports | `ports.py`, API tests, modular service tests | Remote PostgreSQL/object-storage adapters remain planned |
| Interaction capability | Accessible calculation-first browser workflow and recent-job recovery | `tests/test_web.py`, editable Figma desktop/mobile frames | Full assistive-technology certification is not claimed |
| Reliability | Durable SQLite queue, atomic claim/idempotent creation, bounded retries, schema repair, temporary artifact publication | job, idempotency, NIM, reporting, service tests | A multi-node deployment must replace SQLite with a durable shared adapter |
| Security | Digest API authentication, Bearer provider authentication, path boundaries, HTML escaping, privacy-redacted history | hardening, API, web, artifact, Security Scan, Semgrep | Production tenant/KMS/break-glass controls remain deployment/product gaps |
| Maintainability | Modular files/ports, complete public docstrings, exactly 100% statement/branch coverage, canonical documentation graph | Ruff, compileall, pytest-cov, docstring/docs contracts | Coverage/document presence does not prove defect absence or semantic currency |
| Flexibility | Direct NIM default, optional Contextual Orchestrator, injected custom adapters | interpretation-backend and modular-port tests | No implicit backend fallback is provided |
| Safety | Conditional language, medical/coercion/event-certainty rejection, deterministic grounding | `quality.py` and quality tests | Symbolic interpretation may still be misunderstood outside product context |

## 4. ISO/IEC 42001:2023 AI management-system crosswalk

| Management-system practice | Repository implementation | Evidence |
|---|---|---|
| Context and scope | PRD, TRD, calculation policy, AI/provider ADRs, traceability record | `docs/product`, `docs/technical`, `docs/adr`, `docs/standards` |
| Leadership/responsibility | Explicit calculation/model/quality/delivery and automation authorities | TRD, Architecture, control-plane UML, runbooks |
| AI risk/opportunity planning | Product-gap audit, quality gate, privacy minimization, no-fallback policy | audit script, `quality.py`, provider clients |
| Resources/competence | Versioned prompts, calculation explanations, runbooks, complete docstrings | prompts, docs, source |
| Operational control | Validated settings, immutable evidence, schema validation, bounded retry/repair | settings, analysis, model clients |
| Performance evaluation | Golden fixtures, realistic API/workflow tests, hosted NIM opt-in evaluation, supplementary LLM judge | tests, `scripts/nim_eval.py` |
| Continual improvement | Hourly quality/development governance, reviewed PRs, semantic releases | workflows, CHANGELOG |

**Conformity boundary.** These controls support disciplined AI management but do not constitute accredited ISO/IEC 42001 certification.

## 5. ISO/IEC 23894:2023 and NIST AI RMF crosswalk

### Govern

- Calculation, interpretation, quality, delivery and repository-control-plane authority is explicit.
- `NVIDIA_NIM_API_KEY` is limited to direct NIM/model development; `CONTEXTUAL_ORCHESTRATOR_TOKEN` is limited to the optional organization gateway.
- Provider choice is validated and never silently fails over.
- Prompts, models, attempts, repairs, fingerprints and artifact hashes are traceable.
- Existing independent reviewer-agent identities/credentials are not repurposed as development credentials.

### Map

- Birth/context/report content is personal/sensitive workflow data; public job history excludes names, birth data, notes, stored requests, fingerprints, idempotency data, generated text, traces and internal paths.
- The model receives serialized evidence and user context only inside an explicit purpose boundary.
- The service distinguishes deterministic facts, traditional symbolic interpretation and ordinary planning techniques.
- Boundary warnings identify inputs where solar-term or time-policy uncertainty may alter a pillar.

### Measure

- Golden calculations compare exact expected pillars/date boundaries.
- KASI/NAOJ minute-precision fixtures independently measure all twelve 2026 month-changing term roots and before/after transitions.
- Pydantic models measure response-contract validity.
- Rule-based checks measure deterministic fidelity, completeness, constructive balance, wording, safety and disclaimer presence.
- LLM-as-a-judge is supplementary because peer-reviewed work reports adversarial and judgment-bias vulnerabilities.
- Exactly 100% production statement/branch coverage, Ruff, compilation, docs/prompts, package/container builds, Security Scan and Semgrep are release-quality requirements.

### Manage

- Network/rate-limit/server/schema/quality failures have bounded treatment paths and observable states.
- Reports that remain schema-invalid/unsafe do not publish as completed.
- Terminal jobs support deletion/time-based purge.
- Provider misconfiguration fails clearly without changing provider.
- Calculation evidence or externally grounded fixture regression fails the product-quality contract.

## 6. Information security, privacy, CSAP and SOC 2 readiness

### ISO/IEC 27001:2022 and ISO/IEC 27701:2025

Four Pillars uses risk-based security/privacy principles to define product/deployment controls. The project specifically adopts purpose-bound personal-data processing in `docs/security/DATA_GOVERNANCE.md` and proposed ADR 0004 instead of blanket masking that would destroy calculation/report semantics.

Current code evidence includes opaque UUID job/artifact identities, redacted public history, credential separation, endpoint TLS policy, path allow-listing/resolution, escaped HTML, retention/deletion operations, prompt-safe orchestrator attribution, security scans and least-privilege automation zones.

Material gaps before enterprise/public-sector readiness include tenant-scoped authorization, production encryption-at-rest/KMS reference configuration, audited break-glass access, backup deletion semantics, processor/region inventory, data-subject export, and durable tamper-resistant audit evidence.

### KISA CSAP

`docs/compliance/CSAP_SOC2_READINESS.md` maps source/deployment evidence to CSAP-oriented engineering concerns. KISA defines CSAP as a cloud-service security certification process under Korean law with assessment scope and certification criteria. The repository does not claim certification; applicable service type/grade/scope and current KISA criteria must be revalidated for an actual assessment.

### AICPA SOC 2 Trust Services Criteria

The readiness map separates Security, Availability, Processing Integrity, Confidentiality and Privacy concerns and identifies missing organizational/operating evidence. A SOC 2 report is an independent examination of controls over a service organization and cannot be inferred from passing CI or source code.

### NIST SP 800-207

Authorization is resource/action based; possession of a UUID or network location is not authority. Future tenant mode and privileged support must authenticate/authorize each resource operation and preserve identity/service separation.

## 7. NIST AI 600-1 generative-AI controls

| Generative-AI risk | Control |
|---|---|
| Confabulation/grounding failure | Immutable calculation fingerprint; allowed-pillar check; full evidence sent to each applicable stage |
| Prompt injection | User context labelled untrusted and serialized inside an explicit boundary |
| Invalid structured output | Application JSON contract, Pydantic validation, bounded repair; provider-native JSON only where the selected client enables it |
| Harmful overconfidence | Conditional wording requirements, event-certainty rejection, real-world decision disclaimer |
| Evaluation overreliance | Deterministic tests and rule-based gates independent from LLM judge scores |
| Model/provider opacity | Model identity, prompt versions/SHA, attempts and repairs recorded |
| Privacy leakage | Redacted public views, random artifact paths, no secrets/raw content in routine traces or attribution |
| Provider concentration | Replaceable interpretation port and optional organization gateway, without unsafe automatic fallback |

## 8. RFC 9457 target state

Four Pillars currently preserves established FastAPI status behavior and bounded public error text. RFC 9457 remains a Planned separately versioned migration to `application/problem+json`.

Future acceptance requires stable problem `type` identifiers; correct `status`, concise `title`, bounded `detail` and safe `instance`; no stack/secret/birth/path/report leakage; preserved current status semantics; client/browser regressions; API documentation; and CHANGELOG coverage.

## 9. W3C Trace Context target state

Current `traces.json` is generation evidence, not a distributed trace. A future MSA observability PR should validate/propagate `traceparent`/`tracestate`, avoid personal/model content in identifiers/baggage, separate trace correlation from report content, and test malformed/propgated/privacy behavior.

## 10. LLM-as-a-judge evidence limits

Peer-reviewed EMNLP 2024 research reports transferable adversarial attacks and multiple judgment biases. Therefore deterministic fidelity cannot be overridden by a judge; a judge is never the sole release/safety/publication gate; prompts/models are versioned; evaluation includes deterministic fixtures/failure cases; and incidents/human review can invalidate a high judge score.

## 11. Contextual Orchestrator integration traceability

| Contract | Code | Test/evidence |
|---|---|---|
| Structural generation port | `StructuredGenerationClient` in `generation.py` | protocol/import/staged-analysis tests |
| Explicit backend selection | `Settings.interpretation_backend` | invalid/default/explicit selection tests |
| Standalone default | `build_report_interpreter` returns `NimReportInterpreter` | backend-factory test |
| Organization gateway | `ContextualOrchestratorReportInterpreter` | adapter evidence-forwarding test |
| OpenAI-compatible endpoint | `ContextualOrchestratorClient` posts `/v1/chat/completions` | mock-transport contract test |
| Orchestrator response semantics | `ContextualOrchestratorClient(native_json_mode=False)`; JSON-required prompt + Pydantic parse/validation + bounded same-backend repair | contextual-orchestrator adapter tests |
| Direct NIM structured mode | `NimClient` may use provider-native JSON mode | NIM request-contract tests |
| Organizational attribution | prompt-safe service/account/team/group/company fields | attribution tests |
| No implicit fallback | selected client raises backend-specific failure | missing-token/permanent-error tests |
| Credential separation | `NVIDIA_NIM_API_KEY` vs `CONTEXTUAL_ORCHESTRATOR_TOKEN` | credential/backend tests |
| MSA replacement | structural report/job/history/idempotency/publisher ports | modular service tests |

The earlier statement that Contextual Orchestrator sends `response_format=json_object` is intentionally removed because it contradicted protected-main `native_json_mode=False` behavior.

## 12. Database naming and ERD

`docs/erd/domain-model.md` is the canonical conceptual/logical model. Only `report_jobs` is a current application-owned SQLite table. Current indexes are `idx_report_jobs_status_created`, `idx_report_jobs_idempotency_key_digest`, `idx_report_jobs_created_id`, and `idx_report_jobs_status_created_id`. Other modeled concepts such as calculation evidence, prompt revision, report document, manifest, retention action and automation evidence are derived/file/external concepts unless a future migration explicitly persists them.

The product-gap audit rejects noncompliant application-owned tables/indexes. Future database objects use descriptive two-or-more-word `snake_case` names by default.

## 13. Independent calendar-evidence traceability

| Contract | Implementation | Verification evidence | Residual limitation |
|---|---|---|---|
| Official Korean calendar basis | KASI 2026 월력요항 announcement/institute calendar data | KASI doctoring | display page is convenient evidence; formal publication remains authority boundary |
| Independent UTC+09:00 cross-check | NAOJ 2026 Reki Yoko solar-term table | APA 7 entry and matching minute values | shared values do not prove sub-minute precision |
| Immutable offline fixture | `tests/fixtures/kasi_2026_jie_terms.json` | schema/order/timezone/tolerance tests | reviewed update needed for new years |
| Solar longitude | bounded VSOP87 Earth series in `solar.py` | twelve timing tests, Security Scan, Semgrep | bounded series is not a full research ephemeris |
| Timescale conversion | tabled `TAI-UTC`, `TT = TAI + 32.184 s` | naive-time rejection and modern fixtures | pre-1972 fallback is coarse; future leap seconds require maintenance |
| Buyer-visible transitions | public `calculate_chart` five minutes before/after | `tests/test_solar_term_golden.py` | historical local-time policy remains outside modern fixture |
| Versioned evidence | `calendar-1.1.0` | calculation-version/fingerprint assertions | different versions intentionally produce different fingerprints |
| Continual monitoring | authority fixture contracts/product-gap audit | hourly quality loop | static tokens do not replace semantic review |

## 14. Repository automation authority traceability

| Authority | Status | Evidence boundary |
|---|---|---|
| Minute-17 deterministic quality sentinel | Implemented | no model credential; release-quality/product/docs audits |
| Minute-47 NVIDIA/OpenCode product developer | Implemented | NIM model proposal only; immutable proposal/verification/late publication; no approval/merge/release |
| Minute-07 exact-head PR steward | Proposed until feature PR merges | intended oldest-eligible-PR inspection/repair/reverify/governed expected-head merge queue |
| Independent review | Existing separate agents/humans | existing identities/keys remain unchanged |
| Merge | Governed | exact unchanged head + current applicable base/review/check/security policy |
| Release | Protected-main only | version/changelog/package/checksum/provenance acceptance |

`docs/uml/control-plane.md` and proposed ADR 0007 define the state/sequence/authority model. Long-running review/check latency blocks only the dependent action; it never authorizes a bypass.

## 15. Verification and review cadence

The deterministic quality workflow runs hourly at minute 17 and on manual dispatch. The NVIDIA/OpenCode product developer runs separately at minute 47 under its queue and credential gates. A proposed minute-07 PR steward is not counted as protected-main behavior until merged.

Hosted direct-NIM model tests use GitHub Secret `NVIDIA_NIM_API_KEY`. A hosted Contextual Orchestrator test requires a separately deployed gateway and token; Four Pillars does not repurpose the NIM credential to that service. Release-quality verification remains deterministic and must not require an external model key.

## 16. Documentation traceability

`docs/architecture/DOCUMENTATION_MAP.md` defines canonical documents/update triggers. `docs/adr/README.md` defines decision status and supersession. The repository must distinguish Current/Accepted/Proposed/Planned claims. Historical PR bodies/plans are provenance, not current architecture authority. Contradictions with protected-main code are defects.

## 17. Open evidence gaps

- No accredited ISO/CSAP certification or SOC 2 examination.
- No production SLO, external penetration test, DPIA/legal opinion or buyer-specific compliance assessment in this repository.
- No claim that traditional interpretation predicts individual outcomes scientifically.
- No assurance an externally operated model remains free or available.
- No distributed trace propagation until a dedicated W3C Trace Context change lands.
- No RFC 9457 response migration until a dedicated compatibility change lands.
- No research-grade historical ephemeris/timezone fixture outside the bounded modern KASI/NAOJ evidence.
- No production tenant authorization/KMS/break-glass/backup-deletion/subprocessor evidence yet.
- Proposed minute-07 PR stewardship remains unshipped until its exact implementation merges and obtains protected-main operational acceptance.
