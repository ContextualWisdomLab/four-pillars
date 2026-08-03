# ADR 0001: Deterministic calculation core and immutable AI boundary

- Status: Accepted
- Date: 2026-08-03

## Context

Four Pillars reports combine calendar arithmetic with language generation. If an LLM calculates or silently changes pillars, the same birth input can produce inconsistent reports and reviewers cannot tell whether an error came from the calendar rule or the prose. Birth-time uncertainty and solar-term boundaries make hidden correction especially risky.

## Decision

All year, month, day, hour, ten-god, hidden-stem, growth-stage, interaction, daewoon, annual, and monthly calculations are produced by a deterministic Python core. The core returns typed models, explicit policies, boundary warnings, a calculation version, and a SHA-256 fingerprint. AI prompts receive the calculation as read-only evidence. The generated report repeats the fingerprint, and the quality gate rejects any mismatch.

The LLM may explain a missing hour pillar or multiple daewoon scenarios, but it may not choose a value that the calculator did not produce. Calculation-only API and CLI functions remain available without an LLM provider.

## Consequences

Calendar changes require code review, golden fixtures, and a version increment. Prompt changes cannot repair a calculation error. The boundary adds typed data and validation work, but it makes failures attributable, reports reproducible, and provider changes safer. Operators can continue serving calculations during NIM outages.

## Rejected alternatives

- Letting the LLM calculate from birth text was rejected because outputs are nondeterministic and difficult to audit.
- Embedding prose templates directly in the calculator was rejected because domain arithmetic and editorial policy would become coupled.
- Quietly selecting one result near a boundary was rejected because uncertainty belongs in the product output.
