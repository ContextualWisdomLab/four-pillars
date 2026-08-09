# Four Pillars Data Model and ERD

- Status: Current conceptual/logical model with explicit persistence classification
- Baseline: protected `main` at `cd4f4e6361238a1db43c28540640a407c7bf7c6e`
- Reviewed: 2026-08-09

## Purpose

This document makes data ownership and persistence explicit. It is an architectural model, not a claim that every box is a database table. Four Pillars currently uses one application-owned SQLite table, `report_jobs`, plus filesystem artifacts. Several other entities are typed/domain concepts or generated files. GitHub automation evidence is external control-plane state, not application persistence.

Application-owned database object names must contain at least two descriptive words and use `snake_case` by default. The current table and indexes conform to that convention.

## Persistence classification

| Entity | Classification | Current storage / authority |
|---|---|---|
| `report_job` | Persisted | SQLite table `report_jobs` through `JobStore` |
| `report_request` | Embedded persisted payload | JSON field `report_jobs.request_json`; not a separate table |
| `calculation_evidence` | Derived / serialized artifact | Deterministic typed models and JSON; source of truth is calculation code + policy version + input |
| `fortune_snapshot` | Derived / serialized artifact | Daewoon/annual/monthly JSON generated for a job |
| `prompt_revision` | Package/config provenance | Versioned prompt files and hashes; not a DB table |
| `interpretation_attempt` | Runtime / privacy-safe trace artifact | `traces.json` contains bounded metadata; no credential storage |
| `report_document` | Generated artifact | `report.json`, `report.html`, `report.pdf` under opaque job directory |
| `artifact_manifest` | Generated artifact | `manifest.json` with hashes/provenance |
| `history_cursor` | Derived transport token | Opaque cursor derived from `created_at` + random job UUID; not persisted |
| `retention_action` | Operational event | Deletion/cleanup behavior; currently no separate audit table |
| `automation_proposal` | External control-plane concept | GitHub Actions artifact/branch/PR state, not application DB |
| `review_evidence` | External control-plane concept | GitHub review/check API evidence, not application DB |
| `release_evidence` | External control-plane concept | GitHub release/workflow/artifact state, not application DB |

## Current physical SQLite schema

`src/four_pillars/jobs.py` owns the schema:

```sql
CREATE TABLE IF NOT EXISTS report_jobs (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    request_json TEXT NOT NULL,
    request_fingerprint TEXT NOT NULL,
    idempotency_key_digest TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    error TEXT,
    artifact_dir TEXT
);
```

Current application-owned indexes:

- `idx_report_jobs_status_created`
- `idx_report_jobs_idempotency_key_digest` — unique when the digest is non-null
- `idx_report_jobs_created_id`
- `idx_report_jobs_status_created_id`

The table stores raw validated request JSON because deterministic calculation and personalized report generation require the semantic birth/context values. Public history APIs do not serialize that request. Privacy protection therefore relies on purpose-bound authorization, storage/retention controls and restricted propagation rather than pretending the stored request is non-personal data.

## Conceptual ERD

```mermaid
erDiagram
    report_job ||--|| report_request : embeds
    report_job ||--|| calculation_evidence : derives
    report_job ||--o{ fortune_snapshot : derives
    report_job ||--o{ interpretation_attempt : records
    report_job ||--o{ report_document : publishes
    report_job ||--|| artifact_manifest : publishes
    prompt_revision ||--o{ interpretation_attempt : governs
    calculation_evidence ||--o{ interpretation_attempt : grounds
    calculation_evidence ||--o{ fortune_snapshot : grounds
    report_document }o--|| artifact_manifest : hashed_by
    interpretation_attempt }o--|| artifact_manifest : hashed_by
    history_cursor }o--|| report_job : bounds_page_at
    retention_action }o--|| report_job : targets

    report_job {
        uuid job_id PK
        string lifecycle_status
        json request_json
        sha256 request_fingerprint
        sha256 idempotency_key_digest UK
        datetime created_at
        datetime updated_at
        string bounded_error
        string artifact_directory
    }

    report_request {
        string calendar_type
        datetime birth_local_time
        string iana_timezone
        string subject_label
        string optional_user_context
        string day_rollover_policy
        string solar_time_policy
    }

    calculation_evidence {
        string calculation_version
        sha256 calculation_fingerprint
        string year_pillar
        string month_pillar
        string day_pillar
        string optional_hour_pillar
        datetime relevant_solar_term
        string boundary_warning
    }

    fortune_snapshot {
        string snapshot_kind
        string pillar
        datetime period_start
        datetime period_end
        json interactions
    }

    prompt_revision {
        string prompt_name
        string prompt_version
        sha256 prompt_sha256
        string response_schema
    }

    interpretation_attempt {
        string provider_backend
        string model_identifier
        int request_attempt_count
        int schema_repair_count
        string stage_name
    }

    report_document {
        string artifact_name
        string media_type
        sha256 artifact_sha256
    }

    artifact_manifest {
        sha256 calculation_fingerprint
        string model_identifier
        json prompt_versions
        json file_hashes
    }

    history_cursor {
        string cursor_version
        datetime created_at_boundary
        uuid job_id_boundary
    }

    retention_action {
        string action_kind
        datetime requested_at
        string actor_scope
        string outcome
    }
```

### Reading this diagram

Only `report_job` maps to a current application-owned database table. The other entities describe distinct information/authority concepts so that future PostgreSQL, object-storage, audit, or multi-tenant adapters cannot collapse them into an implicit shared record. `retention_action` is conceptual today: the implementation performs cleanup/deletion but does not persist a dedicated audit row.

## Job lifecycle

```mermaid
stateDiagram-v2
    [*] --> queued
    queued --> running: worker claims atomically
    running --> completed: quality passes and artifacts publish
    running --> failed: calculation/provider/schema/render failure
    running --> quality_failed: bounded editorial repair still fails
    completed --> [*]: explicit delete or retention cleanup
    failed --> [*]: explicit delete or retention cleanup
    quality_failed --> [*]: explicit delete or retention cleanup
```

A lifecycle state is not permission. Authorization is evaluated at the API/deployment boundary; the job identifier itself is not an authorization credential.

## Data-authority boundaries

```mermaid
flowchart LR
    Input[Authorized birth/context input\nPII-bearing] --> Job[(report_jobs\nrestricted durable state)]
    Job --> Calc[Deterministic calculation\nimmutable evidence]
    Calc --> Interpret[Selected interpretation backend\nminimum purpose payload]
    Job --> Render[Artifact rendering]
    Interpret --> Render
    Render --> Store[Opaque job artifact directory\nrestricted]
    Job --> PublicHistory[Public/redacted job view\nno request payload]
    Calc --> Manifest[Fingerprint + provenance]
    Interpret --> Trace[Privacy-safe trace metadata]
    Store --> Delete[Retention / explicit deletion]

    Job -. prohibited .-> Telemetry[Ambient telemetry]
    Input -. prohibited .-> Attribution[Usage attribution]
    Store -. prohibited .-> PublicHistory
```

The dashed flows are prohibited default propagation, not missing implementation edges.

## Multi-node target model

A future PostgreSQL/managed-queue adapter may persist the same logical `report_job` lifecycle with transactional keyed creation/claim/history semantics. An object-storage publisher may persist `report_document` and `artifact_manifest` externally. Those adapters must not change the deterministic calculation or public artifact contract, and they must document:

- tenant/subject scoping;
- transaction/isolation and idempotency behavior;
- migration and rollback;
- encryption and key ownership;
- retention/deletion/export behavior;
- stable keyset history ordering;
- crash recovery and partial publication;
- backup/restore deletion semantics.

No service may integrate by directly querying another service's application tables.

## Naming audit

The currently owned table/index names satisfy the repository naming rule. Future migrations must reject one-word application-owned table/index/view/trigger names unless an externally fixed contract makes a different name unavoidable and the exception is documented.
