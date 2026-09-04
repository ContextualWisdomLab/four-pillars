# Bucheon Birth-Time Claim — Evidence Doctoring

## Finding

The image is partly true. Longitude changes local mean solar time, and the equation of time changes apparent solar time. Using Bucheon longitude 126.766° E, the product's documented apparent-solar policy converts 1990-06-15 08:30 KST to 07:56:49, conventionally rounded to 07:57. South Korea's legal standard meridian is 135° E, and IANA timezone history records daylight saving in 1987 and 1988, not 1990.

The image overstates the chart impact. Civil 08:30 and apparent-solar 07:57 are both within the traditional 07:00–08:59 `辰` interval, so this case remains `庚午 壬午 辛亥 壬辰`. A correction can change a pillar near a two-hour or day boundary, but it does not do so merely because the displayed minute changes.

The lunar claim is false for this input. Solar 1990-06-15 corresponds to regular lunar 1990-05-23. Leap lunar 1990-05-23 is solar 1990-07-15. The API requires an explicit `calendar`; `lunar_leap_month` defaults to `false` and must be `true` for an intercalary month. It does not infer a leap month from a solar date.

## Product decision and checks

The deterministic core's existing `civil`, `mean_solar`, and `apparent_solar` policies remain explicit rather than changing the default. The CLI now exposes `--calendar`, `--lunar-leap-month`, `--longitude`, and `--time-basis` on `calculate` and `luck`. `tests/test_cli.py` asserts that the Bucheon result is within 30 seconds of 07:57, that the hour pillar remains `壬辰`, and that regular and leap lunar 1990-05-23 normalize to the two distinct solar dates. `tests/test_calendar.py` independently asserts the same regular and leap fifth-month conversions through the deterministic core.

The numeric longitude avoids retaining a birthplace label or adding a network geocoder. The calculation uses the IANA offset effective at the birth moment, so a historical DST hour is not separately subtracted a second time.

## Claim limits

Apparent solar time is an optional traditional calculation policy, not a correction to the person's legal birth record and not scientific evidence that Four Pillars predicts outcomes. Longitude precision, birthplace uncertainty, historical timezone data, equation-of-time approximation, and competing schools can matter near boundaries.

## APA 7th references

Internet Assigned Numbers Authority. (2026, July 8). *Time zone database 2026c* [Data set]. https://data.iana.org/time-zones/releases/tzdata2026c.tar.gz

Korea Ministry of Government Legislation. (1986). *Standard time act* (Act No. 3919). https://www.law.go.kr/LSW/lsRvsRsnListP.do?chrClsCd=010202&lsId=000744&lsRvsGubun=all

National Oceanic and Atmospheric Administration, Global Monitoring Laboratory. (n.d.). *General solar position calculations*. https://gml.noaa.gov/grad/solcalc/solareqns.PDF

Hong Kong Observatory. (2001). *Gregorian-lunar calendar conversion table of 1990 (Geng-wu—year of the Horse)*. https://www.hko.gov.hk/en/gts/time/calendar/pdf/files/1990e.pdf

Lee, J. (2026). *korean-lunar-calendar* (Version 0.4.0) [Computer software]. GitHub. https://github.com/usingsky/korean_lunar_calendar_py
