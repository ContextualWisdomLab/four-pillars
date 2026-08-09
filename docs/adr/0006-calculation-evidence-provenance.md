# ADR 0006: Versioned astronomical evidence and independent solar-term fixtures

- **Status:** Accepted
- **Date:** 2026-08-09

## Context

Year and month pillars change at solar-term boundaries. A calculator can appear correct on ordinary dates while being wrong by minutes near Li Chun or a month-changing `jie`, which can change the resulting pillar. Earlier implementations based on coarse approximations were not strong enough for a commercial product whose report may be generated exactly near a boundary.

A second copy of the same formula is not an independent oracle. The repository therefore needs externally reviewable timing evidence, a declared astronomical/timescale policy, explicit error budgets, and a calculation evidence version.

## Decision

1. The deterministic calendar core remains the source of truth under ADR 0001.
2. Modern solar-term roots use the repository's bounded VSOP87-based apparent-solar-longitude implementation and documented timescale/correction policy.
3. Production month/year transition behavior is checked against independent published evidence. The current committed 2026 fixture uses KASI and NAOJ evidence for all twelve month-changing `jie` boundaries.
4. Fixtures record source identity and expected timing; they are not silently rewritten to make the implementation pass.
5. Boundary tests exercise both sides of a transition. A buyer-visible ±5 minute transition suite complements the wider six-hour uncertainty warning.
6. Calculation outputs carry a version (`calendar-1.1.0` at this decision). Any material change to astronomical series, timescale conversion, boundary convention, day-rollover semantics, or historical timezone support requires evidence/version review.
7. Known historical/pre-1972/timezone/timescale limitations remain explicit. The product must not claim universal historical precision that the evidence does not support.
8. An LLM, prompt, generated report, or external calendar app cannot override a deterministic boundary result. A disagreement becomes an engineering investigation and may produce a new version only with reviewed evidence.

## Consequences

The calculation layer is slower and more complex than a table-free coarse approximation but remains bounded, offline, reproducible, and independently testable. Release review can attribute a changed pillar to an explicit calculation version and source-backed boundary change.

## Rejected alternatives

- **Use an LLM to resolve ambiguous dates:** rejected because it is nondeterministic and lacks numerical provenance.
- **Trust one third-party app as the oracle:** rejected because the source policy/version may be opaque.
- **Commit only ordinary-date examples:** rejected because transition defects are the highest-impact calculation errors.
- **Hide small timing discrepancies behind the six-hour warning:** rejected because a warning does not replace accuracy testing.

## Implementation and evidence mapping

- `src/four_pillars/solar.py`
- `src/four_pillars/calendar.py`
- `docs/technical/CALCULATION.md`
- `docs/doctoring/kasi-solar-term-golden-fixtures.md`
- committed KASI/NAOJ fixture data/tests introduced by PR #25
- `docs/technical/TEST_STRATEGY.md`

## Reversal conditions

Supersede this ADR if Four Pillars adopts a different astronomical engine/ephemeris or materially extends the supported historical range. The replacement must demonstrate independent transition evidence and declare migration/fingerprint consequences.
