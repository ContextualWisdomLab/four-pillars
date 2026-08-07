# KASI Solar-Term Golden Fixtures Design

## Status and scope

This design is approved for autonomous execution by the standing repository-development mandate. It closes the highest-value bounded trust gap remaining after v0.8.0: the deterministic engine calculates month-changing solar terms, but released tests do not compare all twelve 2026 `jie` instants against an independently published Korean calendar authority.

The increment is calculation-validation work, not a new interpretation rule. It preserves standalone use, modular MSA composition, report schemas, prompts, persistence, API behavior, and the existing six-hour boundary-warning policy. Figma is not required because no visual user flow changes.

## Product problem

A buyer can currently see two known natal charts and a few self-consistency boundary tests. Those tests prove internal behavior but do not establish that every month-changing term agrees with an external official calendar source. A one- or two-minute solar-term error near Li Chun or a `jie` can change the year or month pillar, so the missing evidence is directly visible to users and consultants.

The product needs a committed, reviewable, offline fixture derived from the Korea Astronomy and Space Science Institute's 2026 calendar data, plus transition tests that prove the chart changes on the expected side of each published boundary.

## Approaches considered

### 1. Committed authoritative fixture — selected

Commit the twelve 2026 month-changing `jie` instants published in Korean Standard Time by KASI. Tests compare `jie_terms(2026, "Asia/Seoul")` with a two-minute maximum absolute error and verify month-branch transitions five minutes before and after each published instant. Li Chun additionally verifies the sexagenary year transition.

This approach is deterministic, offline, inspectable, dependency-free, and independent of the production calculation implementation.

### 2. Dynamic test-only ephemeris dependency — rejected

A test-only package backed by JPL ephemerides could calculate expected instants during CI. It would add a large dependency and supply-chain surface, complicate hash-pinned CI, and risk correlated interpretation or timescale choices. The repository needs a small immutable evidence artifact, not a second runtime astronomy stack.

### 3. Live authority lookup in CI — rejected

Fetching KASI or another observatory during each run would make correctness depend on network availability, HTML stability, rate limits, and upstream changes. Offline release gates and reproducibility take precedence.

## Authoritative evidence and claim boundary

The fixture uses KASI's published 2026 Korean calendar data. The source reports civil date, hour, and minute in Korean Standard Time, so each expected instant has minute precision. The test tolerance is therefore 120 seconds: strict enough to detect a materially shifted compact solar series while allowing source rounding and small analytical-model differences.

The National Astronomical Observatory of Japan's 2026 monthly calendar independently agrees with the July 2026 term times at the shared UTC+09:00 offset. JPL DE440 is cited as the current-century high-precision ephemeris context, but the committed values are not claimed to be directly generated from DE440. The fixture validates product fitness for modern Korean calendar use; it does not certify legal, navigation, or research-grade ephemeris accuracy.

Consensus research search was attempted but its monthly quota was exhausted. Primary KASI, NAOJ, and JPL sources remain sufficient for this bounded engineering claim, and the limitation is recorded in doctoring.

## Fixture contract

Create `tests/fixtures/kasi_2026_jie_terms.json` with:

- `schema_version`: `"1.0.0"`;
- `source_title`, `source_url`, `source_timezone`, `published_precision`;
- `retrieved_on`: `"2026-08-07"`;
- `maximum_absolute_error_seconds`: `120`;
- twelve ordered `terms` records containing `name_ko`, `longitude`, `expected_kst`, and `month_branch`.

Only month-changing `jie` terms are included: 소한, 입춘, 경칩, 청명, 입하, 망종, 소서, 입추, 백로, 한로, 입동, and 대설. The file is evidence data, not executable configuration.

## Accuracy and boundary behavior

For every record:

1. find the production term by Korean name;
2. parse `expected_kst` as an aware ISO-8601 datetime;
3. require absolute timing error no greater than 120 seconds;
4. calculate charts five minutes before and after the published instant;
5. require the pre-boundary month branch to differ from the fixture's target branch;
6. require the post-boundary month branch to equal the target branch.

For 입춘, also require the pre-boundary year pillar to be `乙巳` and the post-boundary year pillar to be `丙午`.

Five minutes is deliberately wider than the two-minute accuracy budget, so the transition assertions remain stable while still exercising the buyer-visible boundary.

## Repository components

- `tests/fixtures/kasi_2026_jie_terms.json`: immutable external evidence.
- `tests/test_solar_term_golden.py`: fixture schema, timing, and transition contracts with explicit pytest IDs.
- `docs/doctoring/kasi-solar-term-golden-fixtures.md`: source provenance, APA 7 references, conversion assumptions, tolerance rationale, and residual risk.
- `docs/technical/CALCULATION.md`: published validation scope and tolerance.
- `docs/standards/REFERENCES.md`: APA 7 entries for KASI, NAOJ, and Park et al. (2021).
- `docs/standards/TRACEABILITY.md`: map official fixture evidence to calculation correctness and tests.
- `scripts/product_gap_audit.py`: require the fixture, doctoring, and traceability tokens so hourly governance detects deletion or drift.
- `tests/test_hourly_product_loop.py`: exercise the expanded authority-fixture audit contract.
- `CHANGELOG.md`: record the unreleased validation capability without changing v0.8.0.

## Failure behavior

- missing fixture or doctoring: product-gap audit fails;
- malformed JSON, duplicate names, wrong timezone, unsupported longitude, or incomplete term set: focused test fails;
- timing error over 120 seconds: focused test reports the term ID and signed delta;
- incorrect month or year transition: focused boundary test fails;
- source changes: update through a reviewed fixture revision with new provenance; never fetch silently during CI.

If the current algorithm does not meet the fixture, the implementation must first inspect the signed error pattern. A constant offset indicates timezone or timescale handling; seasonal drift indicates the solar model; one isolated value suggests fixture transcription. Production calculation code changes are permitted only after that root-cause evidence and must retain 100% statement and branch coverage.

## Testing strategy

The first commit adds the design, plan, and a RED contract that requires the absent fixture and doctoring. The second commit adds the authoritative data and focused tests. CI then determines whether production calculation changes are necessary. The complete gate remains:

- Python 3.11 and 3.12;
- dependency integrity;
- product-gap audit;
- Ruff and public docstrings;
- compilation;
- document and prompt validation;
- offline tests with exactly 100% production statement and branch coverage;
- distribution and container builds;
- Security Scan and Semgrep.

No hosted LLM is needed. `NVIDIA_NIM_API_KEY` and `COPILOT_GITHUB_TOKEN` are absent from this test path.

## Modularity, security, and privacy

The fixture test imports only the deterministic calendar API and `BirthInput`. No database, HTTP client, worker, model, artifact publisher, or organization gateway is created. The change therefore works identically in standalone and MSA deployments.

The data contains public astronomical calendar values and no personal information. CI remains offline, and no new dependency or credential is introduced.

## Version decision

This bounded increment is recorded under `Unreleased`. It adds correctness evidence without changing public runtime behavior. After merge, the release loop may decide whether to publish a patch version together with any other accumulated fixes.