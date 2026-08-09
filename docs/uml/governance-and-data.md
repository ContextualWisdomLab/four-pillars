# Governance and Persistence UML Views

These views complement `docs/uml/architecture.md`. They focus on durable application boundaries and autonomous-development authority that were previously scattered across PR bodies and operations documents.

## Persistence port class view

```mermaid
classDiagram
    class ReportJobRepository {
      <<Protocol>>
      +create(request) ReportJob
      +get(job_id) ReportJob?
      +claim_next() ReportJob?
      +complete(job_id, artifact_dir)
      +fail(job_id, error)
      +delete(job_id)
    }

    class IdempotentReportJobRepository {
      <<Optional Protocol>>
      +create_idempotent(request, key_digest, request_fingerprint) tuple
    }

    class ReportJobHistoryRepository {
      <<Optional Protocol>>
      +list_jobs(limit, cursor, status) tuple
    }

    class JobStore {
      -database_path Path
      +create(request) ReportJob
      +create_idempotent(request, key_digest, request_fingerprint) tuple
      +list_jobs(limit, cursor, status) tuple
    }

    class ReportInterpreter {
      <<Protocol>>
      +generate(subject, chart, luck, context) tuple
    }

    class ArtifactPublisher {
      <<Protocol>>
      +publish(staged_path, job_id) Path
    }

    class ReportService {
      -repository ReportJobRepository
      -interpreter ReportInterpreter
      -publisher ArtifactPublisher
      +enqueue(request) ReportJob
      +run_next() ReportJob?
    }

    ReportJobRepository <|.. JobStore
    IdempotentReportJobRepository <|.. JobStore
    ReportJobHistoryRepository <|.. JobStore
    ReportService --> ReportJobRepository
    ReportService --> ReportInterpreter
    ReportService --> ArtifactPublisher
```

The optional protocols prevent one new API surface such as history or idempotency from breaking every existing MSA repository adapter.

## Job and artifact sequence

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Repo as ReportJobRepository
    participant Worker
    participant Calc as Deterministic Core
    participant LLM as Selected Interpreter
    participant Gate as Quality Gate
    participant Publisher as ArtifactPublisher

    Client->>API: POST report request + optional Idempotency-Key
    API->>Repo: atomic create/create_idempotent
    Repo-->>API: queued job
    API-->>Client: redacted job view
    Worker->>Repo: atomic claim
    Worker->>Calc: calculate immutable evidence
    Calc-->>Worker: chart/luck + fingerprint
    Worker->>LLM: evidence + untrusted context
    LLM-->>Worker: schema-oriented output
    Worker->>Gate: validate schema + deterministic fidelity + editorial quality
    alt accepted
        Gate-->>Worker: approved
        Worker->>Publisher: stage/publish artifact set
        Publisher-->>Worker: atomic visible location
        Worker->>Repo: completed
    else rejected after bounded repair
        Gate-->>Worker: quality_failed
        Worker->>Repo: quality_failed
    end
```

## Autonomous-development authority state view

```mermaid
stateDiagram-v2
    [*] --> Inventory
    Inventory --> SelectBoundedWork: executable item exists
    SelectBoundedWork --> RED: source/behavior defect
    SelectBoundedWork --> DocumentationImpact: architecture/documentation defect
    RED --> Implement
    DocumentationImpact --> Implement
    Implement --> Verify
    Verify --> Repair: valid failure/finding
    Repair --> Verify
    Verify --> ReviewReady: exact bounded increment green
    ReviewReady --> IndependentGovernance
    IndependentGovernance --> ProtectedMain: required reviews/checks/branch policy pass
    IndependentGovernance --> Deferred: check/review/provider wait
    Deferred --> Inventory: rotate; waiting is local
    ProtectedMain --> OperationalProof: changed control/release path requires runtime evidence
    OperationalProof --> Inventory: continue queue
```

The minute-47 product-development workflow may reach `ReviewReady` by proposing one bounded PR but does not own the `IndependentGovernance -> ProtectedMain` transition. PR #29 proposes a steward for governed PR triage/merge queueing and remains `active_pr` until protected-main integration.

## Documentation maturity class view

```mermaid
classDiagram
    class ArchitectureClaim {
      +claim_id
      +statement
      +maturity
      +evidence_ref
      +owner_document
    }
    class Maturity {
      <<enumeration>>
      implemented_on_protected_main
      accepted_architecture
      active_pr
      planned
      deprecated
      superseded
    }
    class Evidence {
      +exact_commit
      +test_or_contract
      +release_or_pr_ref
    }
    ArchitectureClaim --> Maturity
    ArchitectureClaim --> Evidence
```

This is a documentation model, not a runtime database schema. It prevents a mutable PR body or plan from being treated as evidence that a capability already exists on protected main.
