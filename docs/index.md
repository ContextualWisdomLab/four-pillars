# Four Pillars

Four Pillars is a deterministic Korean Four Pillars (사주·만세력) calculation service with schema-validated AI-assisted report generation. Calendar calculation and AI interpretation remain separate trust boundaries: deterministic birth-calendar facts are produced locally, while optional narrative interpretation is routed through Contextual Orchestrator and validated before report output.

## Start here

- [Repository README](../README.md) — setup, features, runtime configuration, and verification.
- [Product requirements](product/PRD.md) — product scope and acceptance boundaries.
- [Technical requirements](technical/TRD.md) — runtime, data, integration, and quality contracts.
- [Architecture](../ARCHITECTURE.md) — bounded contexts, ports, trust boundaries, and deployment shape.
- [Calculation rules](technical/CALCULATION.md) — deterministic calendar and Four Pillars calculation behavior.
- [Model orchestration operations](operations/ORCHESTRATION.md) — the `orchestrator/free` integration boundary.
- [Operations runbook](operations/RUNBOOK.md) — operating and recovery guidance.
- [Security policy](../SECURITY.md) — vulnerability reporting and security expectations.
- [Changelog](../CHANGELOG.md) — shipped and pending product changes.
- [Standards and research references](standards/REFERENCES.md) — APA-style technical and research traceability.

## Architecture at a glance

The calculation engine owns deterministic calendar facts and their integrity fingerprint. The application layer exposes those facts through service and CLI workflows. AI interpretation is optional and crosses a narrow `ReportInterpreter` port into Contextual Orchestrator; the repository does not own provider selection or direct provider credentials. Generated interpretation must satisfy the repository's schema and quality gates before HTML or PDF is emitted.

## Onboarding

Use the README quick start for a local Python environment. Calculation-only workflows require no model credential. Report generation requires an approved Contextual Orchestrator endpoint and token. Run the repository verification commands before proposing changes; the release contract requires full measured production statement and branch coverage in addition to the repository's security and review gates.

## Releases and deeper exploration

- [GitHub releases](https://github.com/ContextualWisdomLab/four-pillars/releases)
- [Ask DeepWiki](https://deepwiki.com/ContextualWisdomLab/four-pillars)
- [ContextualWisdomLab organization](https://github.com/ContextualWisdomLab)

This project provides a traditional symbolic interpretation for reflection. It does not establish facts about the future and is not a substitute for medical, legal, financial, employment, or relationship decisions based on real evidence and qualified advice.
