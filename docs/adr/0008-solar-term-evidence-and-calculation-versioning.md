# ADR 0008: External solar-term evidence and calculation-version provenance

- Status: Accepted
- Date: 2026-08-07
- Protected-main evidence: `cd4f4e6361238a1db43c28540640a407c7bf7c6e`

## Context and drivers

Year and month pillars change at astronomical solar-term boundaries. A self-consistent implementation can still be wrong if the same approximation produces both the runtime value and the test expectation. Boundary mistakes are buyer-visible because a few minutes can change the year/month pillar and therefore every downstream Ten-God/luck interpretation built from it.

The product therefore needs an oracle independent of the local solver, explicit timing tolerances, boundary-adjacent behavior tests, and a way to prevent old reports/calculations from being confused with a changed numerical policy.

## Decision

1. Modern solar-term calculation uses a local deterministic, bounded VSOP87-based apparent-solar-longitude implementation with explicit timescale handling rather than calling an online ephemeris during production/CI.
2. Boundary-critical acceptance uses committed **external authoritative fixtures**. For 2026, KASI minute values are the Korean authority boundary and NAOJ independently corroborates the same twelve month-changing `jie` values at UTC+09:00.
3. CI records and tests signed timing deltas against the external fixture with an explicit product budget; it does not generate the fixture from Four Pillars itself.
4. Public chart tests evaluate moments on both sides of every external boundary so the oracle verifies buyer-visible pillar transitions, not only root timestamps.
5. Calculation evidence carries a version. The externally validated modern solver is `calendar-1.1.0`; the version contributes to the calculation fingerprint.
6. A calculation-policy change capable of changing a pillar/boundary requires a new calculation-evidence version, new/updated independent fixtures, regression comparison, doctoring, and release notes.
7. Near-boundary user warnings remain separate from numerical test tolerance. The warning is a product uncertainty/verification prompt; it is not permission for an LLM to choose another pillar.

## Alternatives considered

### Use the same solver to generate test expectations

Rejected because it cannot detect systematic implementation error.

### Fetch KASI/NAOJ dynamically in CI or production

Rejected because external availability/content drift would make deterministic calculation and release tests non-reproducible.

### Treat minute-level agreement as research-grade ephemeris certification

Rejected. The acceptance claim is intentionally limited to Four Pillars' modern Korean product boundary behavior within the committed budget.

### Let interpretation compensate for a suspicious boundary

Rejected because AI cannot own or silently change deterministic evidence.

## Consequences

- Fixtures require reviewed maintenance when new years or authoritative sources are added.
- Calculation versioning makes policy changes visible and may intentionally change fingerprints.
- Historical timezone/timescale support needs separate evidence rather than extrapolating the modern fixture.
- KASI/NAOJ provide an independent product oracle without becoming runtime dependencies.

## Failure and recovery

A fixture tolerance failure, changed transition behavior, missing authority provenance, or unexpected calculation-version change fails CI/release. Maintainers must determine whether the solver, fixture transcription, timescale table, or external authority changed. A changed external publication is not copied into fixtures without reviewed provenance and before/after comparison.

## Security and governance impact

The fixture is public non-secret evidence. Network retrieval is excluded from release-critical execution, reducing availability/supply-chain variability. Source URLs, retrieval dates and claim boundaries are retained in doctoring/references.

## Acceptance evidence

- `tests/fixtures/kasi_2026_jie_terms.json` contains all twelve ordered 2026 `jie` terms and source metadata.
- `tests/test_solar_term_golden.py` checks source/schema/order/timezone, bounded timing deltas, and before/after public pillar transitions.
- `calendar-1.1.0` is emitted/fingerprinted.
- `docs/doctoring/kasi-solar-term-golden-fixtures.md`, calculation policy and standards references explain the oracle and limitations.
- CI/security/package gates passed on the protected-main change that introduced the evidence.

## Migration and rollback

`calendar-1.1.0` intentionally identifies the current policy. Rolling runtime code back to an older policy must also restore its calculation version; silently reporting `calendar-1.1.0` with older arithmetic is prohibited. Existing stored reports retain their original fingerprint/version evidence.

## Supersession conditions

Supersede this ADR if Four Pillars adopts a different independently validated astronomical engine or a broader ephemeris authority model. The replacement must preserve deterministic offline acceptance, explicit external provenance, boundary transition tests, versioned calculation evidence and no AI ownership of calendar truth.

## References

Bretagnon, P., & Francou, G. (1988). Planetary theories in rectangular and spherical variables: VSOP87 solutions. *Astronomy and Astrophysics, 202*, 309–315.

Korea Astronomy and Space Science Institute. (2025, June 30). *「2026년 월력요항」 발표*. https://www.kasi.re.kr/kor/post/newsMaterial/32031

National Astronomical Observatory of Japan. (2025, February 3). *Reki Yoko Reiwa 8 (2026): Solar terms*. https://eco.mtk.nao.ac.jp/koyomi/yoko/2026/rekiyou262.html.en

Park, R. S., Folkner, W. M., Williams, J. G., & Boggs, D. H. (2021). The JPL planetary and lunar ephemerides DE440 and DE441. *The Astronomical Journal, 161*(3), 105. https://doi.org/10.3847/1538-3881/abd414
