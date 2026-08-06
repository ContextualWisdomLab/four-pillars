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
  Interpreter --> Direct[NimReportInterpreter]
  Interpreter --> Gateway[ContextualOrchestratorReportInterpreter]
  Direct --> NIM[NVIDIA Hosted NIM]
  Gateway --> CO[Contextual Orchestrator]
  CO --> Approved[Organization-approved Model Workers]
  NIM --> Schema[Pydantic Schema Validation]
  Approved --> Schema
  Schema --> Quality[Deterministic & Editorial Quality Gate]
  Quality --> Render[HTML / PDF / JSON Renderer]
  Render --> Artifacts[(UUID Artifact Store)]
  API --> Artifacts
  Core --> Fingerprint[SHA-256 Calculation Fingerprint]
  Fingerprint --> Prompt
  Fingerprint --> Quality
```

The calculator does not depend on interpretation, rendering, HTTP, or the queue. `ReportService` composes structural ports. Direct NVIDIA NIM is the standalone default; Contextual Orchestrator is optional and selected explicitly. The worker is the only built-in component that combines calculation, interpretation, validation, and publication. Calculations remain available during model-provider outages, and custom queue, interpreter, or artifact implementations can be injected without rewriting calendar rules.

## Interpretation adapter class view

```mermaid
classDiagram
  class StructuredGenerationClient {
    <<Protocol>>
    +generate(system_prompt, user_payload, response_model, model, temperature, max_tokens)
  }
  class OpenAICompatibleJsonClient {
    -AsyncClient http
    -retry_budget
    -repair_budget
    +generate(...)
    +aclose()
  }
  class NimClient
  class ContextualOrchestratorClient
  class ReportInterpreter {
    <<Protocol>>
    +generate(subject_name, chart, daewoon, annual, monthly, user_context)
  }
  class NimReportInterpreter
  class ContextualOrchestratorReportInterpreter
  class ReportService

  StructuredGenerationClient <|.. NimClient
  StructuredGenerationClient <|.. ContextualOrchestratorClient
  OpenAICompatibleJsonClient <|-- NimClient
  OpenAICompatibleJsonClient <|-- ContextualOrchestratorClient
  ReportInterpreter <|.. NimReportInterpreter
  ReportInterpreter <|.. ContextualOrchestratorReportInterpreter
  NimReportInterpreter --> NimClient
  ContextualOrchestratorReportInterpreter --> ContextualOrchestratorClient
  ReportService --> ReportInterpreter
```

`NimTrace` remains the compatible application trace model for model identity, attempts, repairs, and raw validation content. Public trace artifacts expose only privacy-safe fields assembled by `analysis.py`. The orchestrator receives organization attribution separately; personal data and generated content are prohibited from attribution.

## Report sequence

```mermaid
sequenceDiagram
  actor U as User
  participant A as API
  participant Q as ReportJobRepository
  participant W as Worker
  participant C as Calculator
  participant I as Selected Interpreter
  participant M as Direct NIM or Contextual Orchestrator
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
  I->>M: versioned stage prompts + JSON response mode
  M-->>I: schema-oriented JSON content
  I-->>W: Pydantic-validated drafts and traces
  W->>G: fingerprint + synthesized report
  alt quality passes
    G-->>W: approved
  else editorial issue
    W->>I: bounded editorial repair
    I->>M: repair prompt + JSON Schema
    M-->>I: repaired complete report
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

The selected interpreter never changes during one job. Missing credentials, unavailable gateways, invalid responses, and exhausted retry or repair budgets become visible failures rather than provider fallback.

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

## Standalone deployment view

```mermaid
flowchart TB
  LB[TLS Reverse Proxy] --> API1[API Container]
  API1 --> V[(Shared Artifact Volume)]
  API1 --> DB[(SQLite WAL)]
  Worker1[Worker Container] --> DB
  Worker1 --> V
  Worker1 --> NIM[Hosted NVIDIA NIM]
  Secret[Secret Manager] --> API1
  Secret --> Worker1
  Probe[Health / Readiness Probes] --> API1
```

SQLite and a shared filesystem intentionally define the single-node edition. `INTERPRETATION_BACKEND=nvidia_nim` and `NVIDIA_NIM_API_KEY` provide the independent default.

## Organization MSA deployment view

```mermaid
flowchart TB
  Edge[Organization API / Auth Edge] --> API[Four Pillars API]
  API --> Repo[(PostgreSQL or Managed Queue Adapter)]
  Worker[Four Pillars Worker] --> Repo
  Worker --> Object[Object Storage ArtifactPublisher]
  Worker --> Gateway[Contextual Orchestrator]
  Gateway --> NIMW[NVIDIA NIM Worker]
  Gateway --> Other[Other Approved Worker]
  Ledger[(Usage / Cost Ledger)] <-- prompt-safe attribution --> Gateway
  Central[Central .github / naruon] --> Checks[Repository-owned Verification Commands]
  Secrets[Secret Manager] --> API
  Secrets --> Worker
  Traces[Organization Observability] -. future W3C Trace Context .- API
  Traces -. future W3C Trace Context .- Gateway
```

The organization form selects `INTERPRETATION_BACKEND=contextual_orchestrator`, uses a gateway-specific token, and may inject remote repository and artifact adapters. Four Pillars does not install or import gateway internals. `service=four-pillars` and optional account/team/group/company labels support usage attribution; subject data, prompts, outputs, fingerprints, paths, and credentials are excluded.

Current generation traces are local evidence, not W3C distributed traces. `traceparent`/`tracestate` propagation and RFC 9457 problem responses are documented future changes that require separate compatibility PRs.

## State machine

```mermaid
stateDiagram-v2
  [*] --> queued
  queued --> running: worker claims
  running --> completed: quality passes + artifacts published
  running --> failed: calculation, selected backend, schema, or rendering error
  running --> quality_failed: bounded editorial repair still fails
  completed --> [*]: retention or explicit deletion
  failed --> [*]: retention or explicit deletion
  quality_failed --> [*]: retention or explicit deletion
```

## Standards traceability

`docs/standards/REFERENCES.md` records APA 7th references for ISO/IEC 25010:2023, ISO/IEC 42001:2023, ISO/IEC 23894:2023, NIST AI RMF, NIST AI 600-1, RFC 9457, W3C Trace Context, and peer-reviewed LLM-judge research. `docs/standards/TRACEABILITY.md` maps architecture elements to controls, tests, workflows, limitations, and future work. The mapping is not an ISO certification or scientific validation of traditional interpretation.