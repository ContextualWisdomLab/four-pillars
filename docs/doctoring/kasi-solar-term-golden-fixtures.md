# KASI 2026 Solar-Term Golden Fixtures — Evidence Doctoring

## Buyer-visible claim

Four Pillars now checks all twelve 2026 month-changing solar terms against independently published civil-calendar times at the Korean/Japanese UTC+09:00 offset. Each calculated instant must remain within 120 seconds of the minute-precision fixture, and a chart calculated five minutes before and after the published instant must change to the expected month branch. Li Chun additionally changes the sexagenary year from `乙巳` to `丙午`.

This closes a buyer-visible correctness gap. Near a `jie` boundary, a timing error can change the year or month pillar even when every downstream rule is internally consistent.

## Source selection

The Korea Astronomy and Space Science Institute (KASI) announcement states that the 2026 월력요항 is the statutory basis for Korean calendar production and includes the 24 solar terms. The KASI calendar-data page is a convenient institute-published presentation, but that page itself distinguishes its display from the formal announcement. The committed fixture therefore records the 2026 values as externally published evidence while treating the formal 월력요항 announcement as the authority boundary.

The National Astronomical Observatory of Japan (NAOJ) 2026 calendar independently publishes the same twelve instants at Japan Central Standard Time. Because both KST and JCST are UTC+09:00, the matching minute values provide a useful independent transcription cross-check without a timezone conversion.

`tests/fixtures/kasi_2026_jie_terms.json` is deliberately committed and reviewed. CI never scrapes KASI or NAOJ, so an upstream layout, network outage, rate limit, or later web correction cannot silently change a release result.

## Transcription and timezone policy

The fixture contains aware ISO-8601 timestamps with `+09:00`, declares `Asia/Seoul`, and preserves the published minute precision. It contains only the twelve month-changing `jie` values: 소한, 입춘, 경칩, 청명, 입하, 망종, 소서, 입추, 백로, 한로, 입동, and 대설.

The fixture is evidence rather than runtime configuration. Production still solves each requested apparent solar longitude and then converts the UTC root through the requested IANA timezone. The fixture cannot be imported by production code.

## Root-cause evidence

The first RED fixture run exposed a smooth seasonal bias in the previous compact Meeus/NOAA longitude approximation. Signed differences from the published 2026 values were:

| Term | Previous signed error (seconds) |
|---|---:|
| 소한 | -238.270 |
| 입춘 | -363.778 |
| 경칩 | -535.171 |
| 청명 | -688.310 |
| 입하 | -758.460 |
| 망종 | -622.251 |
| 소서 | -427.453 |
| 입추 | -173.890 |
| 백로 | +52.268 |
| 한로 | +72.079 |
| 입동 | -53.815 |
| 대설 | -195.738 |

The errors were not approximately constant, so a timezone or fixed-offset correction would have been unsound. The seasonal pattern identified the compact solar model as the root cause.

## Algorithm revision

`src/four_pillars/solar.py` evaluates a bounded subset of the published VSOP87 Earth longitude and radius series. Civil input is converted from UTC to Terrestrial Time using tabled `TAI-UTC` and the conventional exact relation `TT = TAI + 32.184 s`. The geocentric longitude then receives bounded FK5, dominant nutation-in-longitude, and aberration corrections.

The calculation remains deterministic, dependency-free, and offline. The calendar evidence version advances from `calendar-1.0.0` to `calendar-1.1.0`, so report fingerprints cannot silently mix results produced by the two solar models.

The GREEN fixture run produced these signed differences:

| Term | VSOP87 signed error (seconds) |
|---|---:|
| 소한 | -4.273 |
| 입춘 | -11.500 |
| 경칩 | -19.356 |
| 청명 | -0.899 |
| 입하 | +11.856 |
| 망종 | +62.249 |
| 소서 | +23.443 |
| 입추 | -5.567 |
| 백로 | +38.118 |
| 한로 | +48.214 |
| 입동 | +21.161 |
| 대설 | -25.171 |

Every absolute error is below 63 seconds and therefore below the explicit 120-second product budget.

## Accuracy budget

KASI and NAOJ publish the relevant civil instants to the nearest minute, not to sub-second precision. A 120-second maximum absolute difference:

- allows one minute of source rounding plus bounded analytical/model differences;
- is substantially narrower than the product's existing six-hour input-warning window;
- keeps the five-minute before/after transition tests outside the accepted timing uncertainty;
- fails large enough errors to change a practical near-boundary chart.

The budget is a product acceptance criterion, not a scientific statement that the fixture itself is accurate to 120 seconds.

## Boundary test design

For each term, pytest uses the Korean name as the case ID, checks the target longitude and timing budget, and calculates Seoul charts five minutes before and after the external instant. The pre-boundary month branch must differ from the target and the post-boundary branch must match it. Li Chun separately proves the buyer-visible year transition.

The tests exercise `BirthInput`, timezone normalization, root finding, year/month pillar selection, versioned fingerprints, and the same public deterministic path used by API and report generation. No model, database, worker, artifact publisher, or organization adapter is involved.

## Claim boundary and residual risk

The evidence supports modern 2026 Korean civil-calendar use. It does **not** claim:

- accredited astronomical, legal, navigation, or research-grade certification;
- equality with every historical almanac convention;
- full VSOP87 precision outside the supported modern product window;
- authoritative historical Korean local-time reconstruction before standardized civil time;
- that the bounded nutation series replaces IAU 2000A for high-precision astrometry;
- that JPL DE440 directly generated the committed fixture.

The code uses a coarse ten-second pre-1972 `TAI-UTC` fallback because the released evidence is modern. Historical birth dates remain protected by the six-hour warning policy but need separately sourced historical-time and ephemeris fixtures. The leap-second table must be reviewed whenever IERS Bulletin C announces a new UTC step. IERS Bulletin C 72 confirms that `UTC-TAI = -37 s` remains in force through the end of 2026.

DE440/DE441 is cited as current-century high-precision ephemeris context and as a future independent comparison option. It is not used as a hidden runtime dependency or represented as the source of the KASI/NAOJ minute values.

## Research-tool limitations

Consensus academic search was attempted, but the connected service reported that its monthly quota was exhausted. Primary KASI, NAOJ, IERS, CDS/VizieR, NIST, and peer-reviewed astronomical sources were used directly. Context7's pytest documentation was used to confirm explicit parametrized IDs and readable per-case failures; it did not supply astronomical evidence.

## APA 7th references

Bretagnon, P., & Francou, G. (1988). Planetary theories in rectangular and spherical variables: VSOP87 solutions. *Astronomy and Astrophysics, 202*, 309–315.

International Earth Rotation and Reference Systems Service. (n.d.). *How is TT computed from TAI?* Retrieved August 7, 2026, from https://www.iers.org/iers/en/service/faqs/time/howisttcomputedfromtai-163

International Earth Rotation and Reference Systems Service. (2026, July 7). *Bulletin C 72: Information on UTC–TAI*. https://datacenter.iers.org/data/html/bulletinc-072.html

Korea Astronomy and Space Science Institute. (n.d.). *달력자료(월력요항): 2026년 달력자료*. Retrieved August 7, 2026, from https://astro.kasi.re.kr/life/post/calendardata

Korea Astronomy and Space Science Institute. (2025, June 30). *「2026년 월력요항」 발표*. https://www.kasi.re.kr/kor/post/newsMaterial/32031

Meeus, J. (1998). *Astronomical algorithms* (2nd ed.). Willmann-Bell.

National Astronomical Observatory of Japan. (2025, February 3). *Reki Yoko Reiwa 8 (2026): Solar terms*. https://eco.mtk.nao.ac.jp/koyomi/yoko/2026/rekiyou262.html.en

National Institute of Standards and Technology. (2026). *Leap second and UT1–UTC information*. https://www.nist.gov/pml/time-and-frequency-division/time-realization/leap-seconds

Park, R. S., Folkner, W. M., Williams, J. G., & Boggs, D. H. (2021). The JPL planetary and lunar ephemerides DE440 and DE441. *The Astronomical Journal, 161*(3), 105. https://doi.org/10.3847/1538-3881/abd414

VizieR. (1995). *Planetary solutions VSOP87 (Catalog VI/81)*. Centre de Données astronomiques de Strasbourg. https://cdsarc.cds.unistra.fr/viz-bin/cat/VI/81
