# Standards Traceability and Control Evidence

This document maps applicable international standards, public frameworks, authoritative calendar evidence, and peer-reviewed evaluation findings to concrete Four Pillars controls. It is an engineering traceability record, not a certificate, legal opinion, medical claim, or scientific validation of traditional interpretation.

## 1. System context

Four Pillars has four deliberately separate trust boundaries:

1. **Deterministic calculation:** validated birth input produces immutable chart and luck evidence with a SHA-256 fingerprint.
2. **Interpretation:** the application crosses a `ReportInterpreter` port into Contextual Orchestrator. `StructuredGenerationClient` is the structural generation port and `ContextualOrchestratorClient` is the anti-corruption-layer implementation. Product-owned runtime composition fixes the virtual model to `orchestrator/free`; provider discovery and provider credentials remain outside this bounded context.
3. **Quality:** deterministic and editorial rules reject unsupported pillars, missing sections, warning-only relationship copy, vague language, medical directions, coercive decisions, false authority, and event certainty.
4. **Delivery:** only approved reports become JSON, HTML, PDF, trace, and manifest artifacts under random job identifiers.

Traditional Four Pillars analysis is presented as symbolic and conditional. Deterministic calendar correctness is testable; generated life guidance is not represented as experimentally established prediction.

## 2. ISO/IEC 25010:2023 product-quality crosswalk

| Quality concern | Four Pillars control | Verification evidence | Residual limitation |
|---|---|---|---|
| Functional suitability | Golden four-pillar fixtures, externally published KASI/NAOJ `jie` instants, Li Chun and month transitions, ten-god and luck calculations, immutable report evidence | `tests/test_calendar.py`, `tests/test_solar_term_golden.py`, `tests/test_fortune.py`, edge tests | Modern minute-precision evidence is not research-grade historical ephemeris certification |
| Performance efficiency | Deterministic calculation has no network dependency; long model calls run in a worker | calculation unit tests, API/worker separation | Orchestration latency depends on the selected eligible upstream route |
| Compatibility | FastAPI/JSON interfaces, OpenAI-compatible orchestration ACL, structural repository/interpreter/publisher ports | `ports.py`, API tests, modular service tests | Remote PostgreSQL/object-storage adapters remain operator work |
| Interaction capability | Accessible calculation-first browser workflow and recent-job recovery | `tests/test_web.py`, editable Figma desktop/mobile frames | Full assistive-technology certification is not claimed |
| Reliability | Durable SQLite queue, atomic claim/idempotent creation, bounded retries, schema repair, temporary artifact publication | job, idempotency, orchestration, reporting, and service tests | A multi-node deployment must replace SQLite with a durable shared adapter |
| Security | Digest API authentication, gateway Bearer authentication, path boundaries, HTML escaping, privacy-redacted history | hardening, API, web, artifact, Security Scan, Semgrep | Production TLS, gateway token rotation, and infrastructure controls are deployment responsibilities |
| Maintainability | Modular files and structural ports, complete public docstrings, exactly 100% statement and branch coverage | Ruff, compileall, pytest-cov, docstring rules | Coverage is evidence of execution, not proof of defect absence |
| Flexibility | Provider-neutral `ReportInterpreter` port with Contextual Orchestrator as repository-owned composition | interpretation-backend and modular-port tests | Provider-native product composition is intentionally rejected |
| Safety | Conditional language, medical/coercion/event-certainty rejection, deterministic grounding | `quality.py` and quality tests | Symbolic interpretation may still be misunderstood outside product context |

## 3. ISO/IEC 42001:2023 AI management-system crosswalk

| Management-system practice | Repository implementation | Evidence |
|---|---|---|
| Context and scope | PRD, TRD, calculation policy, AI/orchestration ADRs, this traceability record | `docs/product`, `docs/technical`, `docs/adr`, `docs/standards` |
| Leadership and responsibility | Trust boundaries and explicit operator/deployment responsibilities | TRD, RUNBOOK, SECURITY |
| AI risk and opportunity planning | Product-gap audit, quality gate, privacy minimization, no-direct-provider-fallback policy | `scripts/product_gap_audit.py`, `quality.py`, orchestration ACL |
| Resources and competence | Versioned prompts, calculation explanations, runbooks, complete docstrings | prompt files, docs, source |
| Operational control | Validated settings, immutable evidence, schema validation, bounded retry and repair | `settings.py`, `analysis.py`, orchestration client |
| Performance evaluation | Golden fixtures, realistic API/workflow tests, opt-in `orchestrator/free` evaluation, LLM judge as supplementary evidence only | test suite, `scripts/orchestrator_eval.py` |
| Continual improvement | Hourly scheduled gate, idempotent regression issue, PR review/check/merge loop, semantic releases | hourly workflow, release workflow, CHANGELOG |

**Conformity boundary.** These controls support disciplined AI management but do not constitute accredited ISO/IEC 42001 certification.

## 4. ISO/IEC 23894:2023 and NIST AI RMF crosswalk

### Govern

- Calculation, interpretation, quality, and delivery ownership is explicit.
- `CONTEXTUAL_ORCHESTRATOR_TOKEN` authenticates only the organization gateway; Four Pillars production configuration does not accept provider-native credentials.
- The product virtual model is fixed to `orchestrator/free`; provider discovery and free-pool eligibility are owned by Contextual Orchestrator.
- Prompts, virtual model, attempts, repairs, fingerprints, and artifact hashes are traceable.
- Hourly and release workflows receive no model credential.

### Map

- Subjects provide sensitive birth context, so public job history excludes names, birth data, notes, stored requests, fingerprints, idempotency data, generated text, traces, and internal paths.
- The model receives serialized evidence and user context inside an explicit untrusted-content envelope.
- The service distinguishes deterministic facts, traditional symbolic interpretation, and ordinary planning techniques.
- Boundary warnings identify inputs where solar-term or time-policy uncertainty may alter a pillar.

### Measure

- Golden calculations compare exact expected pillars and date boundaries.
- KASI/NAOJ minute-precision fixtures independently measure all twelve 2026 month-changing term roots and before/after pillar transitions.
- Pydantic models measure response-contract validity.
- Rule-based checks measure deterministic fidelity, completeness, constructive balance, wording, safety, and disclaimer presence.
- LLM-as-a-judge evaluation is supplementary because peer-reviewed work reports adversarial and judgment-bias vulnerabilities.
- Exactly 100% statement and branch coverage, Ruff, compilation, document/prompt checks, package/container builds, Security Scan, and Semgrep are release requirements.

### Manage

- Network, rate-limit, server, schema, and quality failures have bounded treatment paths and observable job states.
- A report that remains schema-invalid or unsafe is not published as completed.
- Terminal jobs support deletion and time-based purge.
- Orchestration misconfiguration fails clearly without changing to a provider-native route.
- The hourly loop creates or updates one regression issue and closes it only after the entire gate is green.
- Authority-fixture deletion, tolerance drift, provenance loss, or calculation-version regression fails the offline product-gap audit.

## 5. NIST AI 600-1 Generative AI controls

| Generative-AI risk | Control |
|---|---|
| Confabulation and grounding failure | Immutable calculation fingerprint; allowed-pillar check; full evidence sent to each stage |
| Prompt injection | User context labelled untrusted and serialized inside an explicit boundary |
| Invalid structured output | Prompted JSON object, Pydantic validation, bounded same-route repair |
| Harmful overconfidence | Conditional wording requirements, event-certainty rejection, real-world decision disclaimer |
| Evaluation overreliance | Deterministic tests and rule-based gates independent from LLM judge scores |
| Model/provider opacity | Virtual model, prompt versions, prompt SHA-256, attempts, and repairs recorded; provider route evidence remains in the orchestrator |
| Privacy leakage | Redacted public job views; random artifact paths; no secrets in traces or attribution |
| Provider concentration | Provider discovery and failover are centralized in Contextual Orchestrator; `orchestrator/free` fails closed rather than crossing into a paid tier |

## 6. RFC 9457 target state

Four Pillars currently preserves established FastAPI status behavior and bounded public error text. RFC 9457 is the target for a future separately versioned migration to `application/problem+json`.

Required future acceptance criteria:

- stable problem `type` identifiers;
- correct `status`, concise `title`, bounded `detail`, and safe `instance` values;
- no stack trace, secret, birth context, internal path, or generated report leakage;
- existing 400, 401, 404, 409, 422, 501, and 5xx semantics preserved;
- client and browser regression tests;
- explicit API documentation and CHANGELOG entry.

The current orchestrator integration does not change public API error shapes.

## 7. W3C Trace Context target state

Current `traces.json` is a generation-evidence artifact, not a distributed trace. A future MSA observability PR should:

- accept and validate `traceparent` and optional `tracestate` at the public API boundary;
- create a trace when none is supplied;
- propagate context to Contextual Orchestrator;
- avoid putting personal data or model content in trace identifiers or baggage;
- record trace correlation separately from report content;
- test malformed headers, parent-child propagation, and privacy behavior.

This work is intentionally separate from the orchestration-routing PR so provider integration remains reviewable.

## 8. LLM-as-a-judge evidence limits

Peer-reviewed EMNLP 2024 research reports that judge models can be manipulated by transferable adversarial phrases and that both human and LLM judges exhibit multiple forms of judgment bias. Four Pillars therefore applies the following policy:

- deterministic fidelity cannot be overridden by a judge score;
- an LLM judge is never the sole release, safety, or publication gate;
- judge prompts and virtual models are versioned and traceable;
- evaluation sets include stable deterministic fixtures and known failure cases;
- comparative or rubric-based evidence is preferred over unsupported absolute quality claims;
- production incidents and human review can invalidate an apparently high judge score.

## 9. Contextual Orchestrator integration traceability

| Contract | Code | Test/evidence |
|---|---|---|
| Structural generation port | `StructuredGenerationClient` in `generation.py` | protocol import and staged-analysis compatibility tests |
| Repository-owned composition | `Settings.interpretation_backend` accepts only `contextual_orchestrator` | direct/unknown backend rejection tests |
| Fixed zero-cost virtual route | `Settings.contextual_orchestrator_model` is `orchestrator/free` | settings and outbound-body tests |
| Organization gateway ACL | `ContextualOrchestratorReportInterpreter` | adapter evidence-forwarding test |
| OpenAI compatibility | `ContextualOrchestratorClient` posts `/v1/chat/completions` | mock-transport contract test |
| Strict output | prompted JSON, Pydantic model, bounded repair | successful and repair tests |
| Organizational attribution | prompt-safe `service`, account, team, group, company fields | attribution tests |
| No implicit fallback | gateway client raises backend-specific failure; repository factory has no direct-provider branch | missing-token, permanent-error, and architecture-fitness tests |
| Credential boundary | `CONTEXTUAL_ORCHESTRATOR_TOKEN` only in product runtime configuration | `.env.example`, docs, manual live workflow |
| MSA replacement | structural `ReportInterpreter`, job, history, idempotency, and publisher ports | modular service tests |

Historical `NimClient` compatibility tests remain temporarily while the provider-specific infrastructure namespace is retired. They are not a product runtime path. ADR 0004 records this transition and the DDD namespace follow-up.

## 10. Database naming

The integration introduces no database object. Existing application-owned objects continue to use two-or-more-word `snake_case`, including `report_jobs`, `idx_report_jobs_status_created`, `idx_report_jobs_idempotency_key_digest`, `idx_report_jobs_created_id`, and `idx_report_jobs_status_created_id`. `product_gap_audit.py` creates a temporary database and rejects any noncompliant application-owned table or index.

## 11. Independent calendar-evidence traceability

| Contract | Implementation | Verification evidence | Residual limitation |
|---|---|---|---|
| Official Korean calendar basis | KASI 2026 월력요항 announcement and institute calendar-data presentation | `docs/doctoring/kasi-solar-term-golden-fixtures.md` | Display page is convenient evidence; formal announcement remains the authority boundary |
| Independent UTC+09:00 cross-check | NAOJ 2026 Reki Yoko solar-term table | APA 7 entry and matching minute values | Shared values do not prove sub-minute precision |
| Immutable offline fixture | `tests/fixtures/kasi_2026_jie_terms.json` | schema/order/timezone/tolerance tests | Manual transcription requires reviewed updates |
| Solar longitude | bounded VSOP87 Earth series in `solar.py` | twelve timing tests, Security Scan, Semgrep | Bounded series is not a full research ephemeris |
| Timescale conversion | tabled `TAI-UTC`, `TT = TAI + 32.184 s` | naive-time rejection and all modern fixtures | pre-1972 fallback is coarse; future leap seconds require maintenance |
| Buyer-visible transitions | public `calculate_chart` five minutes before/after each term | `tests/test_solar_term_golden.py` | Historical local-time policy remains outside this modern fixture |
| Versioned evidence | `calendar-1.1.0` in chart and fingerprint | calculation-version assertion | Different versions intentionally produce different fingerprints |
| Continual monitoring | `AUTHORITY_FIXTURE_CONTRACTS` | hourly product-gap audit tests | Static tokens do not replace semantic review |

The JPL DE440/DE441 paper supplies current-century high-precision ephemeris context, not a hidden dependency or the direct generator of the fixture. The acceptance claim is limited to modern Korean product behavior within the explicit two-minute budget.

## 12. Verification and review cadence

The repository hourly workflow runs at `17 * * * *` and on manual dispatch. It performs dependency integrity, product-gap and database naming audit, Ruff and public-docstring checks, compilation, document and prompt checks, all offline tests with exactly 100% statement and branch coverage, and distribution build. Failures update one idempotent regression issue; recovery closes it with the verified commit.

Live model tests are explicit because they depend on an external gateway. The manual live lane requires `CONTEXTUAL_ORCHESTRATOR_TOKEN` and a configured gateway URL, tests `orchestrator/free`, and receives no NVIDIA, OpenAI, OpenRouter, Bytez, or other provider-native credential.

## 13. Open evidence gaps

- No accredited ISO certification or independent conformity assessment.
- No production SLO, external penetration test, data-protection impact assessment, or buyer-specific legal review in this repository.
- No claim that traditional interpretation predicts individual outcomes scientifically.
- No assurance that an externally operated free model remains available; `orchestrator/free` is expected to fail closed when its eligible pool is empty.
- Provider-specific `nim.py` naming remains transitional infrastructure and must move under the provider-neutral orchestration ACL namespace with imports/tests/docs updated together.
- No distributed trace propagation until the dedicated W3C Trace Context PR is implemented.
- No RFC 9457 response migration until the dedicated API compatibility PR is implemented.
- No research-grade historical ephemeris or timezone fixture outside the bounded modern KASI/NAOJ evidence.
- Consensus literature-search quota was unavailable during the prior review; primary institute, standards-service, catalog, journal, and ACL sources were verified directly, and future reviews should expand the evidence base.
