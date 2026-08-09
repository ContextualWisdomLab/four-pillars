# Calculation Rules

## Scope and policy

The deterministic engine targets modern Gregorian dates and Korean users. It accepts a local wall-clock birth value plus an IANA timezone. Korean lunar input is converted to a solar civil date before pillar calculation. The default time basis is civil time; optional mean or apparent solar time requires longitude.

The current externally validated calculation evidence version is **`calendar-1.1.0`**. The calculation version and selected policies are embedded in every chart and fingerprint. A policy change capable of moving a user-visible pillar or solar-term boundary requires a new calculation evidence version, independent golden evidence, migration/regression review, doctoring, and release notes; prompt or model changes cannot silently compensate for a calculation change. Accepted ADR 0008 records this provenance/versioning decision.

## Solar longitude and `jie`

The service uses a compact, dependency-free VSOP87 Earth longitude and radius series evaluated in Terrestrial Time. It converts the heliocentric Earth coordinate to apparent geocentric solar longitude and applies bounded FK5, nutation, and aberration corrections. A binary search finds the instant at which longitude crosses each month-changing term.

The twelve terms and month branches are: Xiao Han 285°/Chou, Li Chun 315°/Yin, Jing Zhe 345°/Mao, Qing Ming 15°/Chen, Li Xia 45°/Si, Mang Zhong 75°/Wu, Xiao Shu 105°/Wei, Li Qiu 135°/Shen, Bai Lu 165°/You, Han Lu 195°/Xu, Li Dong 225°/Hai, and Da Xue 255°/Zi.

The year pillar changes at Li Chun, not January 1. The month pillar changes at the latest `jie`, not the first day of a Gregorian month. A birth within six hours of Li Chun or the adjacent month-changing term receives a visible warning because input time, historical timezone, or algorithmic approximation can change the result. The six-hour warning is a conservative user-verification boundary and is distinct from the much smaller numerical acceptance tolerance used by modern external fixtures.

## Independent boundary validation

`tests/fixtures/kasi_2026_jie_terms.json` commits all twelve 2026 month-changing instants in Korean Standard Time from the KASI 2026 calendar evidence. The same minute values are independently published by NAOJ at the shared UTC+09:00 offset.

`tests/test_solar_term_golden.py` requires every calculated 2026 `jie` to remain within 120 seconds of the minute-precision fixture. It also calculates charts five minutes before and after each published instant, proving that the month branch changes on the expected side. Li Chun separately proves the sexagenary year transition from `乙巳` to `丙午`.

The fixture and timing budget are product correctness evidence, not research-grade ephemeris certification. The source publishes civil values to the minute; the two-minute budget accounts for source rounding and bounded analytical-model differences. KASI 2026 provenance, the previous model's signed seasonal errors, the VSOP87 revision, time-scale conversion, and residual risks are recorded in `docs/doctoring/kasi-solar-term-golden-fixtures.md`. `docs/adr/0008-solar-term-evidence-and-calculation-versioning.md` defines the accepted evidence, versioning, rollback, and supersession contract.

A fixture is never regenerated from Four Pillars output. Updating an external fixture requires review of the authority source, retrieval/transcription provenance, signed before/after deltas, affected policy/version, and buyer-visible transition behavior.

## Year and month pillars

1984 after Li Chun is Jia-Zi. The sexagenary year index is `(pillar_year - 1984) mod 60`. The Yin-month stem is derived from the year stem: Jia/Ji begins with Bing, Yi/Geng with Wu, Bing/Xin with Geng, Ding/Ren with Ren, and Wu/Gui with Jia. Each following month advances one stem and branch.

## Day and hour pillars

The Gregorian integer Julian day number is converted to the sexagenary day by `(JDN + 49) mod 60`. The default day rollover is local midnight. The optional `late_zi` policy advances the day at 23:00. Hour branches are two-hour periods with Zi covering 23:00–00:59. The Zi-hour stem is derived from the day stem and advances one stem for each branch.

Day rollover is a policy surface rather than a hidden school assumption. A future change to a default, historical-time interpretation, or accepted timezone range that changes output must be versioned and independently regression-tested.

## Derived relationships

The day stem is the day master. Ten Gods are calculated from five-element production/control relationships and yin-yang polarity. Hidden stems follow the standard branch table. Twelve growth stages use each day stem's Chang Sheng branch and progress forward for yang stems and reverse for yin stems. Element balance is a transparent heuristic: visible stems, primary branch elements, and hidden stems receive fixed weights; the result is not a biological or psychological measurement.

The engine currently emits stem combinations/clashes and branch combinations/clashes/harms. It does not infer a guaranteed outcome from an interaction. AI receives the named relationship only as evidence to explain possible ordinary manifestations.

## Daewoon

When gender is known, direction follows the conventional year-stem polarity rule: yang-year male and yin-year female progress forward; yin-year male and yang-year female progress in reverse. When gender is unspecified, both scenarios are returned. Start age equals the time to the relevant next or previous `jie` divided by three days per year. The first period uses the month pillar one step in the selected direction and each period spans approximately ten tropical years.

The direction/start-age rule is a declared traditional policy, not an empirically validated personal-outcome model. If another school/policy is supported later, it must be explicit in the input/evidence contract rather than silently chosen by an LLM.

## Annual and monthly luck

Annual luck begins at Li Chun and ends at the next Li Chun. Monthly luck begins at the `jie` occurring in the requested Gregorian month and ends at the next `jie`. The same day master is used to derive Ten Gods for temporary pillars. Interactions are calculated between each temporary pillar and each natal pillar.

## Golden examples

- 1990-06-15 08:30, Asia/Seoul, civil time, midnight rollover → `庚午 壬午 辛亥 壬辰`.
- 1989-07-24 06:27, Asia/Seoul, civil time, midnight rollover → `己巳 辛未 乙酉 己卯`.
- 2026 annual luck → `丙午` beginning at the 2026 Li Chun instant.
- 2027 annual luck → `丁未` beginning at the 2027 Li Chun instant.
- 2026 August monthly luck → `丙申` beginning at Li Qiu and ending at Bai Lu.

Golden examples and external boundary fixtures serve different purposes. The examples exercise known end-to-end pillar/luck results; the KASI/NAOJ fixture independently constrains boundary timing. Neither is replaced by LLM evaluation.

## Limitations

The bounded VSOP87 implementation is validated for the released modern fixture but is not a substitute for a full IAU 2000A implementation or a licensed high-precision ephemeris in legal, navigation, or research use. The pre-1972 `TAI-UTC` fallback is intentionally coarse, and the leap-second table requires review after any new IERS Bulletin C time step. Historical timezone transitions, uncertain birth records, solar-term proximity, and competing schools of day rollover or daewoon timing can produce alternatives. The service exposes those policies and warnings rather than hiding them.

The `calendar-1.1.0` evidence claim is bounded to the policy and fixtures described here. Extending the supported date range, historical timezone fidelity, or additional calendar authorities requires separately reviewed evidence rather than extrapolating the 2026 modern Korean fixture.
