# Standards and Research References

This catalog records the external standards and peer-reviewed research used to design, review, and operate Four Pillars. Entries follow APA 7th edition conventions as closely as the source type permits. ISO standards are listed by their issuing organizations and reference numbers; purchase of an ISO publication may be required to inspect its complete normative text.

These references govern software engineering, AI risk, model evaluation, privacy, reliability, interoperability, calculation evidence, and operations. They do **not** establish Four Pillars interpretation as scientifically validated prediction. The product treats traditional interpretation as symbolic, conditional content and keeps deterministic calendar calculations, AI-generated prose, and ordinary practical guidance visibly separate.

## International standards

### Software product quality

International Organization for Standardization, & International Electrotechnical Commission. (2023). *Systems and software engineering—Systems and software Quality Requirements and Evaluation (SQuaRE)—Product quality model* (ISO/IEC Standard No. 25010:2023). https://www.iso.org/standard/78176.html

**Application.** ISO/IEC 25010:2023 and its nine-characteristic product-quality model inform the PRD/TRD quality goals, deterministic correctness tests, interoperability ports, reliability controls, security boundaries, maintainability requirements, accessibility-aware browser workflow, and release acceptance criteria.

**Limitation.** Repository controls are an engineering crosswalk, not an ISO conformity assessment or certification.

### AI management system

International Organization for Standardization, & International Electrotechnical Commission. (2023). *Information technology—Artificial intelligence—Management system* (ISO/IEC Standard No. 42001:2023). https://www.iso.org/standard/42001

**Application.** ISO/IEC 42001:2023 and its management-system approach inform explicit AI ownership, documented trust boundaries, controlled provider selection, prompt/model traceability, risk review, scheduled quality loops, incident handling, change management, and continual improvement.

**Limitation.** Four Pillars has not undergone an accredited ISO/IEC 42001 certification audit.

### AI risk management

International Organization for Standardization, & International Electrotechnical Commission. (2023). *Information technology—Artificial intelligence—Guidance on risk management* (ISO/IEC Standard No. 23894:2023). https://www.iso.org/standard/77304.html

**Application.** ISO/IEC 23894:2023 informs context-specific AI risk identification, treatment, monitoring, provider boundaries, content-quality controls, privacy minimization, and explicit residual-risk documentation.

**Limitation.** This project uses a practical control mapping and does not reproduce the copyrighted standard.

## Public risk frameworks and profiles

Tabassi, E. (2023). *Artificial Intelligence Risk Management Framework (AI RMF 1.0)* (NIST AI 100-1). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.AI.100-1

**Application.** Govern, Map, Measure, and Manage concepts are reflected in documented ownership, immutable evidence, model/prompt traces, deterministic and editorial tests, risk-specific failure states, and the hourly product-quality review.

Autio, C., Schwartz, R., Dunietz, J., Jain, S., Stanley, M., Tabassi, E., Hall, P., & Roberts, K. (2024). *Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile* (NIST AI 600-1). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.AI.600-1

**Application.** The Generative AI Profile informs prompt-injection separation, schema validation, grounded-generation checks, bounded repair, human-review limitations, content safety, provenance metadata, and the rule that an LLM cannot change deterministic calculation evidence.

**Version note.** NIST updated the publication page in 2026, and AI RMF 1.0 itself is under revision. The project shall monitor authoritative NIST updates rather than assuming this crosswalk is permanent.

## Internet and web standards

Nottingham, M., Wilde, E., & Dalal, S. (2023). *Problem details for HTTP APIs* (RFC 9457). Internet Engineering Task Force. https://doi.org/10.17487/RFC9457

**Application.** RFC 9457 is the target error-interoperability standard for future machine-readable API problem responses. Existing HTTP status semantics remain stable until a separately tested migration is released. RFC 9457 obsoletes RFC 7807.

World Wide Web Consortium. (2021). *Trace context: W3C recommendation, 23 November 2021*. https://www.w3.org/TR/trace-context/

**Application.** W3C Trace Context is the target for future propagation of `traceparent` and `tracestate` across Four Pillars, Contextual Orchestrator, model gateways, and organization observability systems. Current model and prompt traces are local generation evidence and are not represented as distributed traces.

## Astronomical calculation and civil-calendar evidence

National Oceanic and Atmospheric Administration, Global Monitoring Laboratory. (n.d.). *General solar position calculations*. https://gml.noaa.gov/grad/solcalc/solareqns.PDF

Internet Assigned Numbers Authority. (2026, July 8). *Time zone database 2026c* [Data set]. https://data.iana.org/time-zones/releases/tzdata2026c.tar.gz

Korea Ministry of Government Legislation. (1986). *Standard time act* (Act No. 3919). https://www.law.go.kr/LSW/lsRvsRsnListP.do?chrClsCd=010202&lsId=000744&lsRvsGubun=all

**Application.** NOAA's longitude, UTC-offset, and equation-of-time relationship; IANA's historical Seoul offsets; and Korea's 135° E standard meridian support the explicit birthplace solar-time policy and its DST handling. The Bucheon case and claim limits are recorded in `docs/doctoring/bucheon-birth-time.md`.

Lee, J. (2026). *korean-lunar-calendar* (Version 0.4.0) [Computer software]. GitHub. https://github.com/usingsky/korean_lunar_calendar_py

**Application.** The declared conversion dependency follows the Korea Astronomy and Space Science Institute calendar basis. Its regular/leap-month result is independently cross-checked against the Hong Kong Observatory's published 1990 Gregorian-lunar table in the Bucheon evidence doctoring.

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

**Application.** The optional adapter uses the repository's OpenAI-compatible chat-completions surface, structured-output passthrough, Bearer authentication, organizational usage attribution, and routing metadata. Four Pillars does not duplicate or reach into the orchestrator's internal state.

## Review cadence

- `scripts/check_docs.py` and `scripts/product_gap_audit.py` verify that this catalog and its core references remain present.
- The hourly GitHub Actions loop executes those checks at minute 17 of every hour and on manual dispatch.
- A standards update does not alter production behavior automatically. It creates a documented review obligation followed by tests, a PR, security review, and a release when behavior changes.
- Consensus search capacity was unavailable during the 2026-08-07 review, so the astronomical and existing academic entries were verified directly against authoritative institute, standards-service, catalog, journal, and ACL sources. Future literature reviews should add independent peer-reviewed evidence rather than replacing deterministic software tests.
