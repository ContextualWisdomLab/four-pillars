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
      +finish(job_id, artifact_dir) ReportJob
      +fail(job_id, error, quality=false) ReportJob
      +delete(job_id) bool
      +purge(retention_days) list~str~
    }

    class IdempotentReportJobRepository {
      <<Optional Protocol>>
      +create_idempotent(request, idempotency_key_digest, fingerprint) tuple~ReportJob,bool~
    }

    class ReportJobHistoryRepository {
      <<Optional Protocol>>
      +list_jobs(limit, cursor, status) tuple~list_ReportJob,str?~
    }

    class JobStore {
      -database_path Path
      +create(request) ReportJob
      +get(job_id) ReportJob?
      +claim_next() ReportJob?
      +finish(job_id, artifact_dir) ReportJob
      +fail(job_id, error, quality=false) ReportJob
      +delete(job_id) bool
      +purge(retention_days) list~str~
      +create_idempotent(request, idempotency_key_digest, fingerprint) tuple~ReportJob,bool~
      +list_jobs(limit, cursor, status) tuple~list_ReportJob,str?~
    }

    class ReportInterpreter {
      <<Protocol>>
      +generate(subject_name, chart, daewoon, annual, monthly, user_context) GeneratedReport
    }

    class ArtifactPublisher {
      <<Protocol>>
      +publish(directory, report, chart, daewoon, annual, monthly, traces) dict~str,str~
    }

    class ReportService {
      -store ReportJobRepository
      -interpreter ReportInterpreter
      -publisher ArtifactPublisher
      +enqueue(request) ReportJob
      +enqueue_idempotent(request, key_digest) tuple~ReportJob,bool~
      +list_jobs(limit, cursor, status) tuple~list_ReportJob,str?~
      +process_next() ReportJob?
    }

    ReportJobRepository <|.. JobStore
    IdempotentReportJobRepository <|.. JobStore
    ReportJobHistoryRepository <|.. JobStore
    ReportService --> ReportJobRepository
    ReportService --> ReportInterpreter
    ReportService --> ArtifactPublisher
```

The method names and arguments intentionally mirror `src/four_pillars/ports.py` and `ReportService`; UML is not allowed to invent a second adapter contract. Optional protocols prevent one new API surface such as history or idempotency from breaking every existing MSA repository adapter.

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
    API-->>Client: canonical redacted ReportJobView
    Worker->>Repo: atomic claim_next
    Worker->>Calc: calculate immutable evidence
    Calc-->>Worker: chart/luck + fingerprint
    Worker->>LLM: evidence + untrusted context
    LLM-->>Worker: GeneratedReport schema
    Worker->>Gate: validate schema + deterministic fidelity + editorial quality
    alt accepted
        Gate-->>Worker: approved
        Worker->>Publisher: publish(directory, report, chart, daewoon, annual, monthly, traces)
        Publisher-->>Worker: artifact content digests
        Worker->>Repo: finish(job_id, artifact_dir)
    else rejected after bounded repair
        Gate-->>Worker: quality_failed
        Worker->>Repo: fail(job_id, error, quality=true)
    end
```

## Deletion compensation sequence

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Repo as ReportJobRepository
    participant Artifacts as Trusted artifact root

    Client->>API: DELETE /v1/reports/{job_id}
    API->>Repo: get(job_id)
    Repo-->>API: terminal job + stored artifact path
    API->>API: validate exact configured-root/job-id path
    API->>Repo: delete(job_id)
    alt repository refuses / non-terminal
        Repo-->>API: false
        API-->>Client: 409, artifacts unchanged
    else durable row deleted
        Repo-->>API: true
        API->>Artifacts: remove trusted tree
        alt cleanup succeeds
            API-->>Client: 204
        else cleanup fails
            API-->>Client: 500 retryable cleanup error
            Client->>API: retry DELETE same job_id
            API->>Artifacts: remove exact trusted orphan
            API-->>Client: 204
        end
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
    Implement --> CredentialFreeVerify
    CredentialFreeVerify --> Repair: valid failure/finding
    Repair --> CredentialFreeVerify
    CredentialFreeVerify --> ReviewReady: exact bounded increment green
    ReviewReady --> IndependentGovernance
    IndependentGovernance --> ProtectedMain: required reviews/checks/branch policy pass
    IndependentGovernance --> Deferred: check/review/provider wait
    Deferred --> Inventory: rotate; waiting is local
    ProtectedMain --> OperationalProof: changed control/release path requires runtime evidence
    OperationalProof --> Inventory: continue queue
```

The minute-47 product-development workflow may reach `ReviewReady` by proposing one bounded PR but does not own the `IndependentGovernance -> ProtectedMain` transition. Credential-free verification is mandatory before publication under ADR 0007. PR #29 proposes a steward for governed PR triage/merge queueing and remains `active_pr` until protected-main integration.

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
