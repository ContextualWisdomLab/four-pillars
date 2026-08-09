# Standards and Research References

This catalog records the external standards and peer-reviewed research used to design, review, and operate Four Pillars. Entries follow APA 7th edition conventions as closely as the source type permits. ISO standards are listed by their issuing organizations and reference numbers; purchase of an ISO publication may be required to inspect its complete normative text.

These references govern requirements/architecture description, software engineering, AI risk, information security/privacy, assurance readiness, interoperability, calculation evidence, and operations. They do **not** establish Four Pillars interpretation as scientifically validated prediction. The product treats traditional interpretation as symbolic, conditional content and keeps deterministic calendar calculations, AI-generated prose, and ordinary practical guidance visibly separate.

## Architecture and requirements standards

International Organization for Standardization, International Electrotechnical Commission, & Institute of Electrical and Electronics Engineers. (2022). *Software, systems and enterprise—Architecture description* (ISO/IEC/IEEE Standard No. 42010:2022). https://www.iso.org/standard/74393.html

**Application.** The architecture-description standard informs Four Pillars' explicit stakeholder concerns, viewpoints and model kinds: PRD/TRD, root architecture, ADRs, runtime UML, repository-control-plane UML, conceptual/logical ERD, security/data-governance views, and the authoritative documentation map.

**Claim boundary.** Repository documentation has not undergone a formal ISO/IEC/IEEE 42010 conformance assessment.

International Organization for Standardization, International Electrotechnical Commission, & Institute of Electrical and Electronics Engineers. (2018). *Systems and software engineering—Life cycle processes—Requirements engineering* (ISO/IEC/IEEE Standard No. 29148:2018). https://www.iso.org/standard/72089.html

**Application.** PRD, TRD, API/calculation/modularity contracts and acceptance evidence separate stakeholder/product requirements from technical requirements and verification information. ISO lists Edition 2 as the current published edition, confirmed in 2024, while Edition 3 is under development as a DIS during the 2026-08-09 review.

**Version note.** The DIS is monitored as a future revision and is not treated as a published normative replacement.

Object Management Group. (2017). *OMG Unified Modeling Language (OMG UML), version 2.5.1*. https://www.omg.org/spec/UML/2.5.1

**Application.** UML 2.5.1 supplies the notation reference for class, component, sequence, state and deployment concepts represented as committed Mermaid/PlantUML source. Four Pillars does not claim that Mermaid itself is an OMG-conformant UML interchange tool.

## International standards

### Software product quality

International Organization for Standardization, & International Electrotechnical Commission. (2023). *Systems and software engineering—Systems and software Quality Requirements and Evaluation (SQuaRE)—Product quality model* (ISO/IEC Standard No. 25010:2023). https://www.iso.org/standard/78176.html

**Application.** ISO/IEC 25010:2023 and its nine-characteristic product-quality model inform the PRD/TRD quality goals, deterministic correctness tests, interoperability ports, reliability controls, security boundaries, maintainability requirements, accessibility-aware browser workflow, documentation quality, and release acceptance criteria.

**Limitation.** Repository controls are an engineering crosswalk, not an ISO conformity assessment or certification.

### AI management system

International Organization for Standardization, & International Electrotechnical Commission. (2023). *Information technology—Artificial intelligence—Management system* (ISO/IEC Standard No. 42001:2023). https://www.iso.org/standard/42001

**Application.** ISO/IEC 42001:2023 and its management-system approach inform explicit AI ownership, documented trust boundaries, controlled provider selection, prompt/model traceability, risk review, scheduled quality loops, incident handling, change management, and continual improvement.

**Limitation.** Four Pillars has not undergone an accredited ISO/IEC 42001 certification audit.

### AI risk management

International Organization for Standardization, & International Electrotechnical Commission. (2023). *Information technology—Artificial intelligence—Guidance on risk management* (ISO/IEC Standard No. 23894:2023). https://www.iso.org/standard/77304.html

**Application.** ISO/IEC 23894:2023 informs context-specific AI risk identification, treatment, monitoring, provider boundaries, content-quality controls, privacy minimization, and explicit residual-risk documentation.

**Limitation.** This project uses a practical control mapping and does not reproduce the copyrighted standard.

### Information-security management

International Organization for Standardization, & International Electrotechnical Commission. (2022). *Information security, cybersecurity and privacy protection—Information security management systems—Requirements* (ISO/IEC Standard No. 27001:2022). https://www.iso.org/standard/27001

International Organization for Standardization, & International Electrotechnical Commission. (2024). *Information security, cybersecurity and privacy protection—Information security management systems—Requirements—Amendment 1: Climate action changes* (ISO/IEC Standard No. 27001:2022/Amd 1:2024). https://www.iso.org/standard/88435.html

**Application.** The ISMS requirements inform risk-based ownership, access/change/incident/supplier controls, evidence collection, continual improvement, and the need to separate repository implementation from organizational operating controls.

**Limitation.** Four Pillars is not represented as ISO/IEC 27001 certified.

### Privacy-information management

International Organization for Standardization, & International Electrotechnical Commission. (2025). *Information security, cybersecurity and privacy protection—Privacy information management systems—Requirements and guidance* (ISO/IEC Standard No. 27701:2025). https://www.iso.org/standard/27701

**Application.** ISO/IEC 27701:2025 informs accountable PII-controller/processor boundaries, purpose-bound processing, data-classification and lifecycle governance, provider/subprocessor documentation, and the proposed personal-data ADR. The 2025 edition supersedes the withdrawn 2019 edition.

**Limitation.** This is engineering guidance and does not establish privacy-law compliance or ISO/IEC 27701 certification.

## Public risk, privacy, and security frameworks

Tabassi, E. (2023). *Artificial Intelligence Risk Management Framework (AI RMF 1.0)* (NIST AI 100-1). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.AI.100-1

**Application.** Govern, Map, Measure, and Manage concepts are reflected in documented ownership, immutable evidence, model/prompt traces, deterministic/editorial tests, risk-specific failure states, and scheduled quality review.

Autio, C., Schwartz, R., Dunietz, J., Jain, S., Stanley, M., Tabassi, E., Hall, P., & Roberts, K. (2024). *Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile* (NIST AI 600-1). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.AI.600-1

**Application.** The Generative AI Profile informs prompt-injection separation, schema validation, grounded-generation checks, bounded repair, human-review limitations, content safety, provenance metadata, and the rule that an LLM cannot change deterministic calculation evidence.

**Version note.** NIST updated the publication page in 2026, and AI RMF 1.0 itself is under revision. The project monitors authoritative NIST updates rather than assuming this crosswalk is permanent.

Rose, S., Borchert, O., Mitchell, S., & Connelly, S. (2020). *Zero trust architecture* (NIST Special Publication 800-207). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-207

**Application.** Resource-centric authorization and the absence of implicit trust based on network placement inform future tenant/job/artifact authorization, service identity separation, and governed privileged/break-glass access.

## CSAP and SOC 2 readiness sources

Korea Internet & Security Agency. (n.d.). *클라우드 보안인증제 제도소개* [Cloud Service Security Certification program introduction]. Retrieved August 9, 2026, from https://isms.kisa.or.kr/main/csap/intro/index.jsp

Korea Internet & Security Agency. (2024). *클라우드 서비스 보안인증제 안내서* [Cloud Service Security Certification program guide]. https://isms.kisa.or.kr/main/csap/notice/?boardId=bbs_0000000000000004&cntId=86&mode=view

Korea Internet & Security Agency. (2024). *클라우드서비스 보안인증기준 해설서* [Cloud service security certification criteria commentary]. https://isms.kisa.or.kr/main/csap/notice/?boardId=bbs_0000000000000004&cntId=87&mode=view

**Application.** KISA's materials define the Korean CSAP assurance boundary and inform the readiness inventory for cloud assets, scope, security controls, assessment evidence, provider responsibilities, and the explicit rule that repository engineering must not claim a certificate that has not been externally issued.

**Version note.** KISA guidance and certification type/grade procedures can change. An actual certification project must revalidate the then-current official materials and target scope.

American Institute of Certified Public Accountants. (2023). *2017 Trust Services Criteria for security, availability, processing integrity, confidentiality, and privacy (with revised points of focus—2022)*. AICPA & CIMA. https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022

American Institute of Certified Public Accountants. (2022). *SOC 2® reporting on an examination of controls at a service organization relevant to security, availability, processing integrity, confidentiality, or privacy*. AICPA & CIMA.

**Application.** Trust Services Criteria categories inform the readiness mapping for security, availability, processing integrity, confidentiality, privacy, system-description evidence, and operating-effectiveness gaps.

**Limitation.** A SOC 2 report requires an independent examination over an identified service/system and cannot be inferred from passing CI, a source review, or this crosswalk.

## Internet and web standards

Nottingham, M., Wilde, E., & Dalal, S. (2023). *Problem details for HTTP APIs* (RFC 9457). Internet Engineering Task Force. https://doi.org/10.17487/RFC9457

**Application.** RFC 9457 is the target error-interoperability standard for a future machine-readable API problem-response migration. Existing HTTP status semantics remain stable until a separately tested change is released. RFC 9457 obsoletes RFC 7807.

World Wide Web Consortium. (2021). *Trace context: W3C recommendation, 23 November 2021*. https://www.w3.org/TR/trace-context/

**Application.** W3C Trace Context is the target for future `traceparent`/`tracestate` propagation across Four Pillars, Contextual Orchestrator, model gateways, and organization observability systems. Current model/prompt traces are local generation evidence and are not represented as distributed traces.

## Astronomical calculation and civil-calendar evidence

Bretagnon, P., & Francou, G. (1988). Planetary theories in rectangular and spherical variables: VSOP87 solutions. *Astronomy and Astrophysics, 202*, 309–315.

**Application.** A bounded VSOP87 Earth longitude/radius series replaces the former compact solar approximation for modern month-changing solar-term roots. The coefficients remain local, deterministic, dependency-free, and reviewable.

International Earth Rotation and Reference Systems Service. (n.d.). *How is TT computed from TAI?* Retrieved August 7, 2026, from https://www.iers.org/iers/en/service/faqs/time/howisttcomputedfromtai-163

International Earth Rotation and Reference Systems Service. (2026, July 7). *Bulletin C 72: Information on UTC–TAI*. https://datacenter.iers.org/data/html/bulletinc-072.html

**Application.** Civil UTC is converted to Terrestrial Time with the conventional exact relation `TT = TAI + 32.184 s`; the tabled `TAI-UTC` offset is 37 seconds from 2017-01-01 through the end of 2026.

Korea Astronomy and Space Science Institute. (n.d.). *달력자료(월력요항): 2026년 달력자료*. Retrieved August 7, 2026, from https://astro.kasi.re.kr/life/post/calendardata

Korea Astronomy and Space Science Institute. (2025, June 30). *「2026년 월력요항」 발표*. https://www.kasi.re.kr/kor/post/newsMaterial/32031

National Astronomical Observatory of Japan. (2025, February 3). *Reki Yoko Reiwa 8 (2026): Solar terms*. https://eco.mtk.nao.ac.jp/koyomi/yoko/2026/rekiyou262.html.en

**Application.** KASI is the Korean calendar-production authority boundary. NAOJ independently publishes the same twelve 2026 minute values at the shared UTC+09:00 offset. The committed fixture is used offline and cannot silently change during CI.

National Institute of Standards and Technology. (2026). *Leap second and UT1–UTC information*. https://www.nist.gov/pml/time-and-frequency-division/time-realization/leap-seconds

Park, R. S., Folkner, W. M., Williams, J. G., & Boggs, D. H. (2021). The JPL planetary and lunar ephemerides DE440 and DE441. *The Astronomical Journal, 161*(3), 105. https://doi.org/10.3847/1538-3881/abd414

VizieR. (1995). *Planetary solutions VSOP87 (Catalog VI/81)*. Centre de Données astronomiques de Strasbourg. https://cdsarc.cds.unistra.fr/viz-bin/cat/VI/81

**Claim boundary.** Official minute values and the two-minute product budget validate modern Korean boundary behavior; they do not constitute legal, navigation, or research-grade ephemeris certification. DE440 is high-precision comparison context and does not secretly generate the committed fixture.

## Peer-reviewed LLM evaluation research

Raina, V., Liusie, A., & Gales, M. (2024). Is LLM-as-a-judge robust? Investigating universal adversarial attacks on zero-shot LLM assessment. In Y. Al-Onaizan, M. Bansal, & Y.-N. Chen (Eds.), *Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing* (pp. 7499–7517). Association for Computational Linguistics. https://doi.org/10.18653/v1/2024.emnlp-main.427

**Application.** The reported susceptibility of judge models to transferable adversarial phrases supports keeping deterministic assertions, Pydantic schemas, rule-based quality gates, security review, and human review independent from LLM-as-a-judge scores. Absolute LLM scoring is never the sole release gate.

Chen, G. H., Chen, S., Liu, Z., Jiang, F., & Wang, B. (2024). Humans or LLMs as the judge? A study on judgement bias. In Y. Al-Onaizan, M. Bansal, & Y.-N. Chen (Eds.), *Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing* (pp. 8301–8327). Association for Computational Linguistics. https://doi.org/10.18653/v1/2024.emnlp-main.474

**Application.** Evidence of misinformation-oversight, gender, authority, and presentation-related biases supports multi-method evaluation, explicit rubrics, blinded fixtures where feasible, deterministic fidelity as a hard constraint, and conservative interpretation of LLM-judge results.

## Framework and library documentation

Pydantic. (2026). *Pydantic Settings documentation*. https://docs.pydantic.dev/latest/concepts/pydantic_settings/

**Application.** `BaseSettings`, `SettingsConfigDict`, `Literal` backend selection, and bounded fields provide validated environment configuration while keeping credentials optional until a selected interpretation adapter is invoked.

Contextual Wisdom Lab. (2026). *Contextual Orchestrator* [Computer software]. GitHub. https://github.com/ContextualWisdomLab/contextual-orchestrator

**Application.** The optional adapter uses the repository's OpenAI-compatible chat-completions surface, Bearer authentication, organizational usage attribution, and routing metadata. Production Four Pillars currently sets `native_json_mode=False` for this adapter: JSON is required by the application prompt and enforced with Pydantic parsing/validation plus bounded same-backend repair rather than by sending provider-native `response_format`. Four Pillars does not duplicate or reach into orchestrator internal state.

## Review cadence

- `scripts/check_docs.py` and `scripts/product_gap_audit.py` verify the repository's core standards/documentation contracts; the documentation-baseline work expands the canonical graph that future checks should enforce.
- The deterministic hourly GitHub Actions quality loop executes its checks at minute 17 and on manual dispatch.
- A standards update does not alter production behavior automatically. It creates a documented review obligation followed by tests, a PR, security review, and a release when behavior changes.
- ISO/IEC/IEEE 29148 Edition 3 is monitored while it remains a DIS; published-project requirements continue to cite the current 2018 edition until a final superseding edition is issued and reviewed.
- KISA CSAP guidance and AICPA assurance material are revalidated for any actual assessment scope; this catalog does not claim certification/attestation.
- Consensus search capacity was unavailable during earlier review. The 2026-08-09 documentation baseline relied on current primary standards bodies, KISA, AICPA, NIST, institute, catalog, journal, and ACL sources; future literature review should add independent peer-reviewed evidence where it materially changes a product claim rather than replacing deterministic software tests.
