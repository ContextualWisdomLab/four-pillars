# ADR 0006: Preserve standalone operation and modular MSA boundaries

- Status: Proposed
- Date: 2026-08-09

## Context and drivers

Four Pillars must remain useful as an independently deployable product while also composing with ContextualWisdomLab's central `.github`, `naruon`, `contextual-orchestrator`, and future platform services. A repository-specific calculation engine cannot become dependent on another product's internal database or deployment topology without making standalone use fragile and MSA integration tightly coupled.

The existing implementation already exposes structural ports for report-job persistence, optional idempotency/history, report interpretation, and artifact publication. Direct NVIDIA NIM is the standalone interpretation path; Contextual Orchestrator is an optional organization adapter.

## Decision

1. **Domain ownership stays local.** Four Pillars owns birth/calendar input contracts, deterministic calculations, luck derivation, report schemas, quality policy, job lifecycle semantics, and artifact contract.
2. **Ports, not shared databases.** External systems may implement or call versioned ports/APIs/events but must not read or write Four Pillars application tables directly. Four Pillars likewise must not depend on another product's private application tables.
3. **Standalone defaults remain first-class.** SQLite WAL, local artifact publishing, direct NVIDIA NIM, FastAPI, worker, CLI, and browser workflows remain supported without an organization control plane.
4. **Organization adapters are explicit.** PostgreSQL/managed-queue repositories, object storage, organization authorization, and Contextual Orchestrator may replace individual adapters without changing deterministic calculation models.
5. **Injected adapters are authoritative.** Settings-based default construction applies only when an adapter was not explicitly injected.
6. **No silent backend fallback.** A selected model/organization adapter failure remains visible. Standalone and organization deployments do not silently switch privacy, provider, persistence, or authority class.
7. **Stable compatibility surface.** Repository, history/idempotency, interpreter and artifact contracts are versioned independently where necessary so optional capabilities can evolve without forcing all adapters to implement them at once.
8. **Cross-service authority is explicit.** Central `.github` governs repository automation; `contextual-orchestrator` owns organization LLM routing; `naruon` or other products may compose Four Pillars through supported contracts but do not become owners of calculation truth.

## Alternatives considered

### One organization-only deployment

Rejected because it removes independent operation and makes local/professional deployments depend on unrelated central services.

### Copy Four Pillars code into each consuming repository

Rejected because deterministic calculation and quality policy would fork, making evidence versions and defects diverge.

### Share one database across services

Rejected because it bypasses service authority, schema-version contracts, authorization boundaries, migrations and independent rollback.

## Consequences

- Some adapter interfaces must remain deliberately narrow and stable.
- Organization deployments may need dedicated adapter packages or deployment configuration.
- Cross-service workflows require explicit error, timeout, idempotency and version semantics instead of direct table access.
- The product can evolve local and organization deployments without forking calculation logic.

## Failure and recovery

An unavailable optional organization dependency must fail the affected operation visibly and must not corrupt local job/calculation state. Operators may explicitly reconfigure a supported adapter after diagnosing the outage; automatic provider/persistence fallback is not allowed. Durable job state and artifact publication must remain atomic within the selected adapter contract.

## Security and governance impact

Each service owns its credentials, authorization and data boundary. Organization tokens are not provider administration secrets. Central automation never gains model/reviewer/merge authority merely because it invokes Four Pillars. PII-bearing data crosses a service boundary only when required by the selected versioned contract and purpose.

## Acceptance evidence

Before this ADR becomes Accepted:

- canonical port/API contracts are linked from PRD/TRD/Architecture;
- tests prove imports do not create DB/model/network state;
- injected repository/interpreter/publisher adapters work without subclassing concrete standalone implementations;
- unsupported optional capabilities fail explicitly rather than emulating unsafe process-local behavior;
- organization diagrams show no direct cross-service application-DB access;
- future remote persistence/object-storage adapters include compatibility, migration and rollback tests.

## Migration and rollback

Current standalone behavior is unchanged. New adapters are additive. If an adapter release introduces incompatibility, rollback selects the previous adapter/version while keeping deterministic evidence and artifact schemas unchanged whenever the compatibility contract permits.

## Supersession conditions

Supersede this ADR if Four Pillars intentionally becomes a component with no standalone product, or if the organization adopts a different service-composition model with equivalent independent ownership and versioned authority boundaries.
