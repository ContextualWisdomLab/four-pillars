# Four Pillars Logical Data Model and ERD

**Persistence maturity:** standalone SQLite model is `implemented_on_protected_main`; remote/multi-node persistence is `planned` through the existing repository ports.

This document describes the durable application data that Four Pillars actually owns. It does not invent an enterprise schema merely because the MSA architecture permits a PostgreSQL adapter.

## 1. Standalone persistence

The built-in `JobStore` owns one durable application table: `report_jobs`. SQLite WAL provides the single-node queue. The table stores the validated report request because an asynchronous worker must be able to resume processing after the enqueue request has ended.

```mermaid
erDiagram
    report_jobs {
        TEXT id PK "opaque UUID"
        TEXT status "queued/running/completed/failed/quality_failed"
        TEXT request_json "confidential validated request JSON"
        TEXT request_fingerprint "SHA-256 canonical request fingerprint"
        TEXT idempotency_key_digest "nullable SHA-256 digest of decoded Idempotency-Key"
        TEXT created_at "UTC/RFC3339 timestamp"
        TEXT updated_at "UTC/RFC3339 timestamp"
        TEXT error "nullable bounded operational error"
        TEXT artifact_dir "nullable internal artifact directory"
    }

    report_jobs ||--o| report_artifact_set : "publishes after quality success"
    report_artifact_set {
        STRING job_id "logical relation; filesystem/object-store key"
        STRING manifest_sha256 "manifest/integrity evidence"
        STRING artifact_names "allow-listed files only"
    }
```

`report_artifact_set` is a **logical external resource**, not a second SQLite table. The standalone `ArtifactPublisher` materializes it under the job UUID directory. A remote object-store adapter may implement the same logical relation without creating this SQL object.

## 2. `report_jobs` fields

| Field | Purpose | Sensitivity | Public-history exposure |
|---|---|---|---|
| `id` | opaque durable job identity | operational | yes, authenticated |
| `status` | lifecycle state | operational | yes, authenticated |
| `request_json` | asynchronous processing input | confidential personal data | no |
| `request_fingerprint` | idempotency/integrity comparison | internal integrity | no |
| `idempotency_key_digest` | replay protection without storing raw client key | internal security metadata | no |
| `created_at` | lifecycle/audit ordering | operational | yes, authenticated |
| `updated_at` | lifecycle/audit state time | operational | yes, authenticated where model permits |
| `error` | bounded operator/user failure context | potentially sensitive operational data | only through deliberately bounded status contract |
| `artifact_dir` | internal publication location | internal path | no |

The raw Idempotency-Key is never stored. `request_json` and report artifacts are not telemetry fields.

## 3. Existing indexes and naming contract

The standalone database owns these indexes:

```text
idx_report_jobs_status_created
idx_report_jobs_idempotency_key_digest
idx_report_jobs_created_id
idx_report_jobs_status_created_id
```

All application-owned objects use descriptive multiword `snake_case`. The SQLite engine may own internal `sqlite_*` objects outside this naming contract.

Index purposes:

- `idx_report_jobs_status_created` — queue/status lifecycle lookup;
- `idx_report_jobs_idempotency_key_digest` — unique partial index preventing one non-null idempotency digest from creating multiple jobs;
- `idx_report_jobs_created_id` — stable newest-first keyset history traversal;
- `idx_report_jobs_status_created_id` — the same traversal under exact lifecycle-status filtering.

## 4. Lifecycle state model

```mermaid
stateDiagram-v2
    [*] --> queued
    queued --> running: atomic worker claim
    running --> completed: quality passes + artifact publication succeeds
    running --> failed: calculation/provider/schema/rendering/operational failure
    running --> quality_failed: bounded repair still fails deterministic/editorial gate
    completed --> deleted: explicit deletion or retention cleanup
    failed --> deleted: explicit deletion or retention cleanup
    quality_failed --> deleted: explicit deletion or retention cleanup
```

A transition to `completed` is valid only after the artifact publisher has successfully made the complete artifact set visible. Partial/staging directories are not completed resources.

## 5. Idempotency model

The API may receive one RFC-compatible `Idempotency-Key`. The application normalizes/decodes the allowed key contract, stores only a SHA-256 digest, and calculates a separate canonical request fingerprint.

- same key digest + same request fingerprint → return the existing job;
- same key digest + different request fingerprint → fail with an idempotency-key reuse error;
- no key → retain backward-compatible unique job creation.

The unique partial index is the final standalone race boundary. A multi-node adapter must provide an equivalent atomic uniqueness guarantee at its own consistency boundary.

## 6. History/cursor model

Public history does not serialize `request_json`, request fingerprints, idempotency material, generated report text, model traces, or internal artifact paths. Keyset order is:

```sql
ORDER BY created_at DESC, id DESC
```

A continuation cursor encodes only a strict version, UTC timestamp, and random job UUID. New inserts may appear on a later first-page read but do not mutate the ordering boundary of an existing continuation sequence.

## 7. Artifact data model

A successful job can publish the following logical artifact set:

```text
chart.json
luck JSON outputs
report.json
traces.json
manifest.json
report.html
report.pdf
```

The manifest binds files to hashes, calculation fingerprint, model/prompt identity, and generation evidence. Artifact filenames are server allow-listed. Subject names or birth data are not used in filesystem/object-store keys.

## 8. Standalone-to-MSA mapping

| Logical capability | Standalone adapter | MSA replacement requirement |
|---|---|---|
| ReportJobRepository | SQLite `report_jobs` | durable transactional repository/queue with equivalent lifecycle semantics |
| Idempotent creation | `BEGIN IMMEDIATE` + unique digest index | atomic compare/create with durable uniqueness |
| History traversal | SQLite composite indexes + opaque cursor | globally stable `(created_at, id)` exclusive keyset semantics across API replicas |
| ArtifactPublisher | UUID filesystem directory | object storage or governed artifact service with atomic visibility/integrity |
| ReportInterpreter | direct NIM by default | injected organization adapter such as Contextual Orchestrator |

A remote adapter must not expose another service's private database as the integration contract. Cross-service integration is through the Four Pillars ports/APIs and immutable artifacts.

## 9. Data retention and deletion

Default report retention is 30 days unless deployment policy sets another bounded value. Explicit deletion removes terminal job state and its published artifacts through the application boundary. Enterprise adapters must define:

- retention policy and legal/contractual overrides;
- artifact and database deletion ordering;
- backup expiration/deletion limitations;
- auditable privileged restoration;
- failure signaling when a deletion or cleanup operation is incomplete.

A successful API response must not claim deletion if the authoritative adapter reports a failure.

## 10. Planned multi-node evolution

`planned` multi-node deployment may use PostgreSQL and object storage, but schema design must be reviewed when implemented. It must preserve:

- opaque non-semantic identifiers;
- purpose-bound sensitive request storage;
- two-or-more-word `snake_case` database object names;
- atomic queue/idempotency semantics;
- stable history order;
- explicit tenant/authorization ownership if tenancy is introduced;
- rollback-compatible migrations and versioned contracts.

This document intentionally does not create hypothetical production tables for future features.
