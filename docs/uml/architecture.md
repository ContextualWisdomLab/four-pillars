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
  Worker --> NIM[NVIDIA Hosted NIM]
  NIM --> Schema[Pydantic Schema Validation]
  Schema --> Quality[Deterministic & Editorial Quality Gate]
  Quality --> Render[HTML / PDF / JSON Renderer]
  Render --> Artifacts[(UUID Artifact Store)]
  API --> Artifacts
  Core --> Fingerprint[SHA-256 Calculation Fingerprint]
  Fingerprint --> Prompt
  Fingerprint --> Quality
```

The calculator does not depend on NIM, rendering, HTTP, or the queue. The worker is the only component that combines those boundaries. This makes calculations available during provider outages and allows NIM, storage, or queue implementations to change without rewriting calendar rules.

## Report sequence

```mermaid
sequenceDiagram
  actor U as User
  participant A as API
  participant Q as SQLite Job Store
  participant W as Worker
  participant C as Calculator
  participant N as NVIDIA NIM
  participant G as Quality Gate
  participant R as Renderer
  participant S as Artifact Store

  U->>A: POST /v1/reports
  A->>Q: insert queued request
  A-->>U: 202 + job id
  W->>Q: BEGIN IMMEDIATE + claim
  W->>C: calculate chart and luck
  C-->>W: immutable models + fingerprint
  W->>N: natal / daewoon / annual / monthly prompts
  N-->>W: schema-validated JSON drafts
  W->>N: synthesis and practical skills
  N-->>W: report draft
  W->>G: fingerprint + report
  alt quality passes
    G-->>W: approved
  else editorial issue
    W->>N: bounded editorial repair
    N-->>W: repaired complete report
    W->>G: validate again
  end
  W->>R: render approved report
  R->>S: temp JSON, HTML, PDF, hashes
  S-->>W: atomic publish
  W->>Q: mark completed
  U->>A: GET job / artifact
  A-->>U: status or file
```

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

## Deployment view

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

SQLite and a shared filesystem intentionally define the single-node edition. A horizontally scaled edition replaces `JobStore` and the artifact adapter while keeping calculation, NIM, quality, and report interfaces stable.

## State machine

```mermaid
stateDiagram-v2
  [*] --> queued
  queued --> running: worker claims
  running --> completed: quality passes + artifacts published
  running --> failed: calculation, provider, schema, or rendering error
  running --> quality_failed: bounded repair still fails
  completed --> [*]: retention or explicit deletion
  failed --> [*]: retention or explicit deletion
  quality_failed --> [*]: retention or explicit deletion
```
