# Calculation Rules

## Scope and policy

The deterministic engine targets modern Gregorian dates and Korean users. It accepts a local wall-clock birth value plus an IANA timezone. Korean lunar input is converted to a solar civil date before pillar calculation. The default time basis is civil time; optional mean or apparent solar time requires longitude. The calculation version and policies are embedded in every chart and fingerprint.

## Solar longitude and `jie`

The service uses the compact Meeus/NOAA apparent geocentric solar-longitude series. A binary search finds the instant at which longitude crosses each month-changing term. The twelve terms and month branches are: Xiao Han 285°/Chou, Li Chun 315°/Yin, Jing Zhe 345°/Mao, Qing Ming 15°/Chen, Li Xia 45°/Si, Mang Zhong 75°/Wu, Xiao Shu 105°/Wei, Li Qiu 135°/Shen, Bai Lu 165°/You, Han Lu 195°/Xu, Li Dong 225°/Hai, and Da Xue 255°/Zi.

The year pillar changes at Li Chun, not January 1. The month pillar changes at the latest `jie`, not the first day of a Gregorian month. A birth within six hours of Li Chun or the adjacent month-changing term receives a visible warning because input time, historical timezone, or algorithmic approximation can change the result.

## Year and month pillars

1984 after Li Chun is Jia-Zi. The sexagenary year index is `(pillar_year - 1984) mod 60`. The Yin-month stem is derived from the year stem: Jia/Ji begins with Bing, Yi/Geng with Wu, Bing/Xin with Geng, Ding/Ren with Ren, and Wu/Gui with Jia. Each following month advances one stem and branch.

## Day and hour pillars

The Gregorian integer Julian day number is converted to the sexagenary day by `(JDN + 49) mod 60`. The default day rollover is local midnight. The optional `late_zi` policy advances the day at 23:00. Hour branches are two-hour periods with Zi covering 23:00–00:59. The Zi-hour stem is derived from the day stem and advances one stem for each branch.

## Derived relationships

The day stem is the day master. Ten Gods are calculated from five-element production/control relationships and yin-yang polarity. Hidden stems follow the standard branch table. Twelve growth stages use each day stem's Chang Sheng branch and progress forward for yang stems and reverse for yin stems. Element balance is a transparent heuristic: visible stems, primary branch elements, and hidden stems receive fixed weights; the result is not a biological or psychological measurement.

The engine currently emits stem combinations/clashes and branch combinations/clashes/harms. It does not infer a guaranteed outcome from an interaction. AI receives the named relationship only as evidence to explain possible ordinary manifestations.

## Daewoon

When gender is known, direction follows the conventional year-stem polarity rule: yang-year male and yin-year female progress forward; yin-year male and yang-year female progress in reverse. When gender is unspecified, both scenarios are returned. Start age equals the time to the relevant next or previous `jie` divided by three days per year. The first period uses the month pillar one step in the selected direction and each period spans approximately ten tropical years.

## Annual and monthly luck

Annual luck begins at Li Chun and ends at the next Li Chun. Monthly luck begins at the `jie` occurring in the requested Gregorian month and ends at the next `jie`. The same day master is used to derive Ten Gods for temporary pillars. Interactions are calculated between each temporary pillar and each natal pillar.

## Golden examples

- 1990-06-15 08:30, Asia/Seoul, civil time, midnight rollover → `庚午 壬午 辛亥 壬辰`.
- 1989-07-24 06:27, Asia/Seoul, civil time, midnight rollover → `己巳 辛未 乙酉 己卯`.
- 2026 annual luck → `丙午` beginning at the 2026 Li Chun instant.
- 2027 annual luck → `丁未` beginning at the 2027 Li Chun instant.
- 2026 August monthly luck → `丙申` beginning at Li Qiu and ending at Bai Lu.

## Limitations

The compact solar series is appropriate for this product's modern range but is not a substitute for a licensed high-precision ephemeris in legal or research use. Historical timezone transitions, uncertain birth records, solar-term proximity, and competing schools of day rollover or daewoon timing can produce alternatives. The service exposes those policies and warnings rather than hiding them.
