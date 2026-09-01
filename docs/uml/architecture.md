# Architecture and UML

## Component view

```mermaid
flowchart LR
  User[Reader / Consultant / Platform] --> API[FastAPI API]
  CLI[Typer CLI] --> Core
  API --> Core[Deterministic Calculation Core]
  API --> Queue[(SQLite WAL Job Store)]
  Worker[Report Worker] --> Queue
  Worker --> Core
  Worker --> Prompt[Versioned Prompt Registry]
  Worker --> Interpreter[ReportInterpreter Port]
  Interpreter --> ACL[ContextualOrchestratorReportInterpreter]
  ACL --> CO[Contextual Orchestrator / orchestrator/free]
  CO --> Approved[Eligible Free Model Workers]
  Approved --> Schema[Pydantic Schema Validation]
  Schema --> Quality[Deterministic & Editorial Quality Gate]
  Quality --> Render[HTML / PDF / JSON Renderer]
  Render --> Artifacts[(UUID Artifact Store)]
  API --> Artifacts
  Core --> Fingerprint[SHA-256 Calculation Fingerprint]
  Fingerprint --> Prompt
  Fingerprint --> Quality
```

The calculator does not depend on interpretation, rendering, HTTP, or the queue. `ReportService` composes structural ports. The repository-owned interpretation path is an anti-corruption layer into Contextual Orchestrator and fixes its virtual model to `orchestrator/free`. Provider discovery, provider credentials, and free-pool failover remain outside Four Pillars. Calculations remain available during orchestration outages, and custom queue, interpreter, or artifact implementations can be injected without rewriting calendar rules.

## Interpretation adapter class view

```mermaid
classDiagram
  class StructuredGenerationClient {
    <<Protocol>>
    +generate(system_prompt, user_payload, response_model, model, temperature, max_tokens)
  }
  class ContextualOrchestratorClient
  class ReportInterpreter {
    <<Protocol>>
    +generate(subject_name, chart, daewoon, annual, monthly, user_context)
  }
  class ContextualOrchestratorReportInterpreter
  class ReportService

  StructuredGenerationClient <|.. ContextualOrchestratorClient
  ReportInterpreter <|.. ContextualOrchestratorReportInterpreter
  ContextualOrchestratorReportInterpreter --> ContextualOrchestratorClient
  ReportService --> ReportInterpreter
```

Provider-specific compatibility transport remains transitional test infrastructure and is deliberately omitted from the product class view. ADR 0004 records its later move into a provider-neutral `infrastructure/orchestration` namespace.

## Report sequence

```mermaid
sequenceDiagram
  actor U as User
  participant A as API
  participant Q as ReportJobRepository
  participant W as Worker
  participant C as Calculator
  participant I as Orchestration ACL
  participant O as Contextual Orchestrator
  participant G as Quality Gate
  participant R as ArtifactPublisher
  participant S as Artifact Store

  U->>A: POST /v1/reports + optional Idempotency-Key
  A->>Q: atomic durable enqueue
  A-->>U: 202 + redacted job view
  W->>Q: atomic claim
  W->>C: calculate chart and luck
  C-->>W: immutable models + fingerprint
  W->>I: immutable evidence + untrusted context
  I->>O: orchestrator/free + versioned prompt
  O-->>I: schema-oriented JSON content
  I-->>W: Pydantic-validated drafts and traces
  W->>G: fingerprint + synthesized report
  alt quality passes
    G-->>W: approved
  else editorial issue
    W->>I: bounded editorial repair
    I->>O: same orchestrator/free route + repair prompt
    O-->>I: repaired complete report
    I-->>W: validated report
    W->>G: validate again
  end
  W->>R: approved report + evidence + privacy-safe traces
  R->>S: staged JSON, HTML, PDF, hashes
  S-->>W: complete publication
  W->>Q: mark completed
  U->>A: GET history / job / artifact
  A-->>U: redacted state or allow-listed file
```

The virtual route never changes during one job. Missing gateway credentials, an empty free pool, invalid responses, and exhausted retry or repair budgets become visible failures rather than direct-provider fallback.

## Calculation sequence

```mermaid
sequenceDiagram
  participant V as BirthInput Validator
  participant T as Time Normalizer
  participant J as Solar-Term Solver
  participant P as Pillar Calculator
  participant D as Derived Relations
  participant F as Fingerprint

  V->>T: local wall clock, timezone, policy
  T->>J: timezone-aware moment
  J-->>P: Li Chun, current jie, next jie
  P->>P: year / month / day / hour indices
  P->>D: visible pillars + day master
  D-->>F: ten gods, hidden stems, growth, elements, interactions
  F-->>V: immutable Chart
```

## Single-node product view

```mermaid
flowchart TB
  LB[TLS Reverse Proxy] --> API1[API Container]
  API1 --> V[(Shared Artifact Volume)]
  API1 --> DB[(SQLite WAL)]
  Worker1[Worker Container] --> DB
  Worker1 --> V
  Worker1 --> Gateway[Contextual Orchestrator]
  Gateway --> Free[orchestrator/free pool]
  Secret[Secret Manager] --> API1
  Secret --> Worker1
  Probe[Health / Readiness Probes] --> API1
```

SQLite and a shared filesystem intentionally define the single-node data plane. LLM-backed reports still use the organization orchestration boundary; standalone refers to application deployment, not provider routing ownership.

## Organization MSA deployment view

```mermaid
flowchart TB
  Edge[Organization API / Auth Edge] --> API[Four Pillars API]
  API --> Repo[(PostgreSQL or Managed Queue Adapter)]
  Worker[Four Pillars Worker] --> Repo
  Worker --> Object[Object Storage ArtifactPublisher]
  Worker --> Gateway[Contextual Orchestrator / orchestrator/free]
  Gateway --> FreeWorkers[Eligible Free Workers]
  Ledger[(Usage / Cost Ledger)] <-- prompt-safe attribution --> Gateway
  Central[Shared CWL Maintainer Loop] --> Checks[Repository-owned Verification Commands]
  Secrets[Secret Manager] --> API
  Secrets --> Worker
  Traces[Organization Observability] -. future W3C Trace Context .- API
  Traces -. future W3C Trace Context .- Gateway
```

Four Pillars uses a gateway-specific token and may inject remote repository and artifact adapters. `service=four-pillars` and optional account/team/group/company labels support usage attribution; subject data, prompts, outputs, fingerprints, paths, and credentials are excluded.

Current generation traces are local evidence, not W3C distributed traces. `traceparent`/`tracestate` propagation and RFC 9457 problem responses remain separately versioned changes.

## State machine

```mermaid
stateDiagram-v2
  [*] --> queued
  queued --> running: worker claims
  running --> completed: quality passes + artifacts published
  running --> failed: calculation, orchestration, schema, or rendering error
  running --> quality_failed: bounded editorial repair still fails
  completed --> [*]: retention or explicit deletion
  failed --> [*]: retention or explicit deletion
  quality_failed --> [*]: retention or explicit deletion
```

## Standards traceability

`docs/standards/REFERENCES.md` records APA 7th references for ISO/IEC 25010:2023, ISO/IEC 42001:2023, ISO/IEC 23894:2023, NIST AI RMF, NIST AI 600-1, RFC 9457, W3C Trace Context, and peer-reviewed LLM-judge research. `docs/standards/TRACEABILITY.md` maps architecture elements to controls, tests, workflows, limitations, and future work. The mapping is not an ISO certification or scientific validation of traditional interpretation.
