# Standards Traceability and Control Evidence

This document maps current standards, authoritative calendar evidence, and peer-reviewed evaluation findings to concrete Four Pillars controls. It is an engineering traceability record, not a certificate, legal opinion, medical claim, or scientific validation of traditional interpretation.

## 1. System and authority context

Four Pillars separates deterministic calculation, interpretation, quality and delivery at runtime. Repository governance separately distinguishes model proposal/repair, deterministic verification, independent review, merge authority and protected-main release authority. `docs/architecture/DOCUMENTATION_MAP.md` defines the canonical documentation graph; `docs/uml/control-plane.md` models repository authority; `docs/erd/domain-model.md` distinguishes persisted and conceptual information.

`StructuredGenerationClient` is the structural model-client port. `ContextualOrchestratorClient` is the optional organization-gateway implementation. Direct NVIDIA NIM remains the standalone default. Provider/backend failures never silently change the selected privacy or provider boundary.

## 2. Architecture and requirements standards

| Source | Repository application | Claim boundary |
|---|---|---|
| ISO/IEC/IEEE 42010:2022 | explicit PRD/TRD/Architecture/ADR/UML/ERD/control-plane viewpoints and a documentation-authority map | no formal architecture-description conformity assessment claimed |
| ISO/IEC/IEEE 29148:2018 | separates stakeholder/product requirements, technical requirements, public contracts and acceptance evidence | 2018 is the current published edition used here; Edition 3 DIS is monitored but not treated as final |
| OMG UML 2.5.1 | notation reference for class/component/sequence/state/deployment concepts represented in Mermaid/PlantUML | Mermaid is not claimed as an OMG UML interchange certification tool |

## 3. ISO/IEC 25010:2023 product quality

| Concern | Control | Evidence | Residual gap |
|---|---|---|---|
| Functional suitability | deterministic pillar/luck calculation, KASI/NAOJ boundaries, immutable fingerprint | calendar/solar-term/fortune tests | modern fixture is not historical research ephemeris certification |
| Performance efficiency | deterministic calculation has no runtime network; LLM work is queued | calculation tests, API/worker split | hosted model latency external |
| Compatibility | FastAPI/JSON plus structural job/interpreter/publisher/history/idempotency ports | API and modularity tests | remote PostgreSQL/object-store adapters planned |
| Interaction capability | calculation-first accessible browser and recent-job recovery | web tests, Figma source | full assistive-tech certification not claimed |
| Reliability | durable queue, atomic claim/idempotency, bounded retry/repair, staged artifacts | jobs/idempotency/service/report tests | multi-node durable adapter not yet shipped |
| Security | API-key digest auth, Bearer provider auth, TLS policy, path boundaries, redacted history | hardening tests, Security Scan, Semgrep | tenant/KMS/break-glass evidence remains incomplete |
| Maintainability | modular ports, complete public docstrings, canonical docs, **100% statement and branch coverage** across owned production code | Ruff, compileall, pytest-cov, docs checks | coverage/document presence does not prove semantic correctness |
| Flexibility | direct NIM default, optional orchestrator, injected adapters | backend/modularity tests | no implicit fallback by design |
| Safety | conditional symbolic language, deterministic grounding, medical/coercive/event-certainty rejection | quality rules/tests | symbolic guidance can still be misunderstood outside product context |

## 4. ISO/IEC 42001:2023, ISO/IEC 23894:2023 and NIST AI RMF

### Govern

- deterministic calculation owns chart/luck facts; AI cannot rewrite them;
- direct model work uses `NVIDIA_NIM_API_KEY`; optional organization gateway uses `CONTEXTUAL_ORCHESTRATOR_TOKEN`;
- existing reviewer identities and credentials are independent of model-development credentials;
- prompts/models/attempts/repairs/fingerprints/artifact hashes are traceable;
- selected backend failure is visible and has no silent provider fallback.

### Map

- birth/context/report data is purpose-bound personal application data;
- public history excludes names, birth data, notes, stored request, fingerprints, idempotency material, generated text, traces and internal paths;
- user context is treated as untrusted content rather than control instructions;
- boundary warnings identify calendar/time conditions that can change a pillar.

### Measure

- exact golden pillar/date fixtures;
- all twelve KASI/NAOJ-backed 2026 `jie` boundaries and before/after public transitions;
- Pydantic response-contract validation;
- rule-based deterministic fidelity, completeness, constructive balance, wording and safety;
- LLM-as-a-judge only as supplementary evidence;
- release-quality Ruff, compileall, docs/prompts, package/container, security scans and **100% statement and branch coverage**.

### Manage

- bounded retries and repairs;
- explicit failed/quality-failed job states;
- retention and deletion;
- fail-closed provider/credential/configuration behavior;
- reviewed calculation-evidence version changes;
- work-conserving automation that defers waiting actions without bypassing checks/review.

These mappings support disciplined AI-management/risk practice; they are not ISO certification evidence.

## 5. Generative-AI controls from NIST AI 600-1

| Risk | Four Pillars treatment |
|---|---|
| Confabulation/grounding | immutable calculation evidence and allowed-pillar checks |
| Prompt injection | untrusted-context envelope and schema-bound output |
| Invalid structured output | application JSON contract, Pydantic validation, bounded repair |
| Overconfidence | conditional wording and real-world evidence disclaimer |
| Judge overreliance | deterministic/rule/security/human controls remain independent |
| Provider opacity | model/prompt/attempt/repair/fingerprint provenance |
| Privacy leakage | redacted public views, opaque identifiers, no raw content/secrets in ordinary traces or attribution |
| Provider concentration | explicit replaceable backend with no automatic fallback |

## 6. Information security, privacy, CSAP and SOC 2 readiness

ISO/IEC 27001:2022, ISO/IEC 27701:2025, NIST SP 800-207, KISA CSAP materials, and AICPA Trust Services Criteria inform engineering readiness.

Current evidence includes credential separation, least-privilege automation zones, TLS requirements for remote credential-bearing endpoints, redacted history, opaque job/artifact identifiers, path allow-listing/resolution, escaped HTML, retention/deletion and privacy-safe usage attribution.

`docs/security/DATA_GOVERNANCE.md` explicitly rejects blanket masking when it makes authorized deterministic calculation/reporting nonfunctional. The design instead minimizes where content flows and who/what can access it through purpose limitation, authorization, restricted linkage, encryption/key isolation, retention/deletion/export and governed privileged access.

Material gaps remain before enterprise/public-sector assessment readiness: tenant-scoped authorization, production encryption-at-rest/KMS reference configuration, auditable break-glass access, backup deletion/restore semantics, subject export, processor/region inventory, tamper-resistant audit evidence and operating-effectiveness records.

`docs/compliance/CSAP_SOC2_READINESS.md` distinguishes repository controls, operator-configured controls, missing controls and external assurance. No CSAP certification, SOC 2 attestation, ISO certification or scientific predictive validation is claimed.

## 7. Contextual Orchestrator traceability

| Contract | Code/evidence |
|---|---|
| structural client boundary | `StructuredGenerationClient` |
| explicit backend selection | validated `Settings.interpretation_backend` |
| standalone default | `NimReportInterpreter` / direct NVIDIA NIM |
| organization gateway | `ContextualOrchestratorReportInterpreter` |
| endpoint | OpenAI-compatible `/v1/chat/completions` |
| orchestrator JSON semantics | `ContextualOrchestratorClient(native_json_mode=False)`; JSON required by prompt; Pydantic parse/validation and bounded same-backend repair |
| direct NIM structured mode | `NimClient` may use provider-native JSON mode |
| attribution | service/account/team/group/company only; no personal/report/credential payload |
| credentials | `NVIDIA_NIM_API_KEY` versus `CONTEXTUAL_ORCHESTRATOR_TOKEN` |
| fallback | none; selected backend error remains visible |
| MSA replacement | structural job/interpreter/history/idempotency/publisher ports |

The earlier documentation statement that Contextual Orchestrator receives `response_format=json_object` was removed because it contradicted protected-main `native_json_mode=False` behavior.

## 8. Independent calendar evidence

| Contract | Evidence | Limitation |
|---|---|---|
| Korean authority boundary | KASI 2026 월력요항 | product evidence, not scientific validation of interpretation |
| independent cross-check | NAOJ 2026 solar-term table at UTC+09:00 | minute values do not prove sub-minute research precision |
| offline fixture | `tests/fixtures/kasi_2026_jie_terms.json` | reviewed update required for additional years |
| local solver | bounded VSOP87 implementation | not a full research ephemeris |
| timescale | tabled `TAI-UTC`; `TT = TAI + 32.184 s` | historical/pre-1972 support remains limited |
| buyer-visible transitions | public calculation immediately before/after each term | modern Korean fixture scope |
| evidence identity | `calendar-1.1.0` and fingerprint | changed policy intentionally changes evidence identity |

Accepted ADR 0008 records the decision and rollback/supersession contract.

## 9. Database naming and data authority

Only `report_jobs` is a current application-owned SQLite table. Current indexes are `idx_report_jobs_status_created`, `idx_report_jobs_idempotency_key_digest`, `idx_report_jobs_created_id`, and `idx_report_jobs_status_created_id`. All are descriptive multi-word `snake_case` names.

Calculation evidence, prompt revisions, report documents, manifests, traces, history cursors, retention actions and GitHub automation evidence are conceptual/derived/file/external-control-plane concepts unless a future migration explicitly persists them. See `docs/erd/domain-model.md`.

No integration may use direct cross-service application-database access.

## 10. Repository automation authority

| Authority | Current status | Boundary |
|---|---|---|
| minute-17 quality sentinel | Implemented | model-free deterministic release/product/docs checks |
| minute-47 NVIDIA/OpenCode product developer | Implemented | model proposal through `NVIDIA_NIM_API_KEY`; immutable verification and late publication; no approval/merge/release |
| minute-07 exact-head PR steward | Proposed while its PR remains unmerged | intended PR inspection/repair/reverify/governed expected-head merge queue |
| independent review | Separate | existing human/automated reviewer identities and keys unchanged |
| merge | Governed | exact unchanged head, current applicable base/review/check/security policy |
| release | Protected-main only | integrated version/changelog/package/container/checksum/provenance acceptance |

`docs/uml/control-plane.md` and ADR 0007 describe this separation. Review/check/provider latency blocks the dependent action only; it does not authorize a bypass.

## 11. Release and provenance

Current release automation validates protected main, builds source/wheel and the pinned container, creates `SHA256SUMS`, targets exact `GITHUB_SHA`, and avoids overwriting an existing version. Proposed ADR 0009 records that feature-PR green status is not sufficient release evidence and identifies SBOM/provenance/signing plus protected-main operational acceptance as remaining hardening work.

Release-quality workflows do not need model credentials. Hosted NIM evaluation remains explicit/supplementary.

## 12. Internet interoperability target states

### RFC 9457

Current FastAPI error behavior remains released behavior. `application/problem+json` is Planned as a separately versioned migration with safe problem types/details/instances and compatibility tests.

### W3C Trace Context

Current `traces.json` is local generation evidence, not distributed tracing. Future propagation of `traceparent`/`tracestate` requires separate privacy, malformed-header and cross-service tests.

## 13. LLM-as-a-judge limits

Peer-reviewed EMNLP 2024 work documents transferable adversarial attacks and judgment bias. Therefore deterministic fidelity cannot be overridden by a judge score; a judge is never the sole release/safety/publication gate; judge prompts/models are versioned; and incidents/human review can invalidate apparently high model scores.

## 14. Documentation traceability

`docs/architecture/DOCUMENTATION_MAP.md` defines canonical files/update triggers and authority ordering. `docs/adr/README.md` defines ADR status/supersession. Historical PR bodies, chat and implementation plans are provenance rather than current architecture authority. Material contradictions with protected-main code are repository defects.

The documentation baseline is grounded in ISO/IEC/IEEE 42010:2022, current published ISO/IEC/IEEE 29148:2018, and OMG UML 2.5.1. Proposed/Planned elements must be visibly marked until integrated.

## 15. Verification cadence and open evidence gaps

Deterministic release quality includes dependency integrity, product/documentation audit, Ruff/public-docstring checks, compilation, document/prompt checks, offline tests with **100% statement and branch coverage**, package build, container build, Security Scan and Semgrep. Hosted direct-NIM tests use GitHub Secret `NVIDIA_NIM_API_KEY`; an independently deployed Contextual Orchestrator uses its own token.

Open evidence gaps include:

- no accredited ISO/CSAP certification or SOC 2 examination;
- no production tenant authorization/KMS/break-glass/backup-deletion/subprocessor evidence yet;
- no production SLO, external penetration test or buyer-specific legal assessment in this repository;
- no claim that traditional interpretation predicts individual outcomes scientifically;
- no distributed trace propagation or RFC 9457 migration yet;
- no research-grade historical ephemeris/timezone fixture beyond the bounded modern KASI/NAOJ evidence;
- no mandatory release SBOM/provenance/signature set yet;
- proposed minute-07 PR stewardship remains unshipped until its exact implementation merges and obtains protected-main operational acceptance.
