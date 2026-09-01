# ADR 0004 — Contextual Orchestrator owns product LLM routing

- **Status:** Accepted
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
3. `INTERPRETATION_BACKEND=nvidia_nim` is not a valid product runtime configuration.
4. Product environment examples and live evaluation workflows do not request provider-native credentials.
5. There is no silent fallback from Contextual Orchestrator to a provider-native client or paid route.
6. `ReportInterpreter` remains a public application port. A caller may inject its own implementation for an independently owned MSA composition, but this repository's composition root does not instantiate a provider-native interpreter.
7. The outgoing orchestration request is covered by tests proving the model identifier is `orchestrator/free`, provider-native backend values are rejected, malformed structured output fails closed, and transient retry does not change the virtual route.
8. Provider-native runtime settings, interpreter adapters, live tests, evaluation workflows, and the historical `nim.py` transport have been removed from the active product code.
9. Shared OpenAI-compatible transport and the Contextual Orchestrator client live under the provider-neutral `infrastructure/orchestration` namespace.
10. The top-level `four_pillars.contextual_orchestrator` module is a compatibility re-export only; implementation ownership remains in the infrastructure ACL.

## DDD placement

The accepted implementation is:

```text
src/four_pillars/
  generation.py                    # application structural generation port
  ports.py                         # application ports
  adapters.py                      # application-facing adapter composition
  infrastructure/
    orchestration/
      openai_compatible.py         # provider-neutral transport mechanics
      contextual_orchestrator.py   # Model Orchestration ACL
```

The deterministic calculation domain has no HTTP or orchestration dependency. The interpretation application boundary depends on `ReportInterpreter` and `StructuredGenerationClient`, not a provider-specific SDK or credential.

Future DDD reorganizations may move additional persistence, publishing, API, CLI, and web adapters under their own bounded infrastructure/interface namespaces, but they must move implementation, imports, tests, docs, UML, and architecture-fitness evidence together.

## Consequences

- Four Pillars no longer owns provider selection, provider credentials, or provider cost tiers.
- A gateway outage or empty free pool fails report interpretation explicitly while deterministic calculations remain available.
- Free-pool policy changes can be delivered by Contextual Orchestrator without changing Four Pillars.
- Existing historical direct-NIM ADRs remain as decision history but are superseded for product runtime composition.
- The architecture-fitness audit fails if direct-provider selection, provider-native runtime configuration, or the retired `src/four_pillars/nim.py` path reappears.
- The repository-specific provider-credentialed autonomous writer is retired; organization-wide model-backed development is coordinated by the shared CWL hourly maintainer.
