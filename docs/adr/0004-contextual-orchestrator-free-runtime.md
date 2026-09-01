# ADR 0004 — Contextual Orchestrator owns product LLM routing

- **Status:** Proposed
- **Date:** 2026-09-01
- **Decision scope:** report interpretation and LLM-backed quality evaluation
- **Supersedes:** the runtime-selection portions of ADR 0002 and ADR 0003

## Context

Four Pillars has a deterministic calculation core and a separate report-interpretation application boundary. The product previously allowed that application boundary to choose either a provider-native NVIDIA NIM adapter or Contextual Orchestrator. That duplicated model selection, credentials, retry/fallback policy, cost attribution, and provider-governance responsibility inside a product that does not own those concerns.

The ContextualWisdomLab orchestration bounded context already owns provider discovery, model routing, free-pool eligibility, fallback policy, usage attribution, and deeper multi-agent orchestration. Its `orchestrator/free` virtual model is the fail-closed zero-cost route: it may move among eligible free providers, but it must not fall through to a paid tier.

Under the DDD context map, Four Pillars' **Fortune Interpretation** application context owns interpretation intent, immutable calculation evidence, prompt/schema contracts, report quality rules, and user-facing artifacts. Provider selection belongs to the external **Model Orchestration** bounded context. The integration is therefore an anti-corruption layer, not a provider SDK embedded in the domain.

## Decision

1. Product-owned LLM calls go only through Contextual Orchestrator.
2. The product virtual model is fixed to `orchestrator/free` and configuration rejects a different virtual model.
3. `INTERPRETATION_BACKEND=nvidia_nim` is no longer a valid product runtime configuration.
4. Product environment examples and live evaluation workflows do not request provider-native credentials.
5. There is no silent fallback from Contextual Orchestrator to a provider-native client.
6. `ReportInterpreter` remains a public application port. A caller may inject its own implementation for an independently owned MSA composition, but this repository's composition root will not instantiate a provider-native interpreter.
7. The outgoing orchestration request must be covered by tests that prove the model identifier is `orchestrator/free`, provider-native backend values are rejected, malformed structured output fails closed, and transient retry does not change the virtual route.
8. Direct provider compatibility code may remain temporarily as a test harness while its existing offline tests are migrated. It is not a production composition option.

## DDD placement and follow-up

The current `nim.py` filename reflects the historical provider boundary and is no longer the correct long-term namespace for the shared OpenAI-compatible transport. The next bounded refactor shall move orchestration infrastructure under a provider-neutral infrastructure/ACL namespace, for example:

```text
src/four_pillars/
  domain/                    # deterministic calendar/fortune model
  application/               # report use cases and ports
  infrastructure/
    orchestration/           # Contextual Orchestrator ACL and HTTP transport
    persistence/             # job repository
    publishing/              # artifact publication
```

That move must update imports, compatibility exports, tests, UML, operational documentation, and coverage evidence in the same PR. This ADR does not claim the namespace move is already complete.

## Consequences

- Four Pillars no longer owns provider selection or a provider cost tier.
- A gateway outage fails report interpretation explicitly while deterministic calculations remain available.
- Free-pool policy changes can be delivered by Contextual Orchestrator without changing Four Pillars.
- Existing historical direct-NIM ADRs remain as decision history but are superseded for product runtime composition.
- The architecture-fitness audit must fail if direct-provider selection reappears in the composition root or active runtime configuration.
