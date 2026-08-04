# Standalone and Modular Service Architecture

Four Pillars is designed to run as an independent product and to be imported as a bounded module in a larger ContextualWisdomLab platform. The same deterministic domain contracts must survive both forms; integration may replace infrastructure adapters but must not redefine calendar evidence or prompt semantics.

## Architectural goals

1. **Standalone completeness:** one repository, image, API process, worker process, SQLite queue, local artifact store, browser studio, and CLI can calculate and publish reports without another service.
2. **Module portability:** callers can import calculation functions and Pydantic contracts without starting FastAPI, SQLite, a worker, or NVIDIA NIM.
3. **Bounded trust:** deterministic calculation, hosted interpretation, editorial validation, persistence, and delivery remain separate boundaries.
4. **Replaceable infrastructure:** a platform integration may replace the queue, artifact store, authentication edge, deployment workflow, and hosted model configuration while retaining application and domain behavior.
5. **Central governance compatibility:** organization `.github` workflows or a `naruon` orchestration repository can invoke the repository's checked-in scripts rather than duplicating product rules.

## Bounded components

### Deterministic calculation core

`calendar.py`, `fortune.py`, `constants.py`, and the immutable calculation models contain no FastAPI or HTTPX dependency. Their public integration surface is:

```python
from four_pillars import (
    BirthInput,
    calculate_annual_luck,
    calculate_chart,
    calculate_daewoon,
    calculate_monthly_luck,
)
```

This boundary owns solar and lunar normalization, solar terms, pillars, Ten Gods, hidden stems, Twelve Growth Stages, interactions, luck periods, warnings, and the evidence fingerprint. A platform must treat these outputs as immutable facts for the selected calculation policy.

### Interpretation boundary

`nim.py`, `prompts/`, and `analysis.py` own the hosted NVIDIA NIM request contract, schema validation, bounded repair, staged interpretation, and prompt provenance. They consume serialized calculation evidence and cannot overwrite deterministic values.

The default `NimReportInterpreter` in `adapters.py` opens a NIM client only when interpretation is invoked. It requires `NVIDIA_NIM_API_KEY` at that point. Calculation-only imports and endpoints have no hosted-service credential requirement.

### Application orchestration

`service.py` composes calculation, interpretation, quality validation, job state, and artifact publishing. `ReportService` accepts three independent structural ports from `ports.py`:

- `ReportJobRepository` for durable job creation, atomic claims, transitions, deletion, and retention;
- `ReportInterpreter` for turning immutable evidence into a validated `GeneratedReport`; and
- `ArtifactPublisher` for publishing approved artifacts into an isolated staging directory.

`IdempotentReportJobRepository` is a separate runtime-checkable capability layered on the repository boundary. It intentionally does not extend the required base port, so an existing organization adapter remains compatible with unkeyed report creation. Keyed requests require that optional capability and fail explicitly with HTTP 501 when it is absent; the service never substitutes process-local locking for a distributed atomicity guarantee.

If no ports are supplied, the service creates the standalone `JobStore`, `NimReportInterpreter`, and `FilesystemArtifactPublisher` adapters. `JobStore` implements both the base repository port and the optional idempotent capability. An integration may replace one adapter without replacing the others.

```python
from four_pillars.service import ReportService

service = ReportService(
    settings,
    store=postgres_report_repository,
    interpreter=internal_nim_interpreter,
    publisher=object_storage_publisher,
)
```

The injected implementations are structurally typed. They do not need to inherit product base classes, but their behavior must satisfy the documented protocol and integration acceptance criteria.

### Infrastructure adapters

`jobs.py` is the single-node SQLite implementation of `ReportJobRepository` and `IdempotentReportJobRepository`. `adapters.py` contains the default hosted-NIM interpreter and filesystem artifact publisher. `reporting.py` owns the atomic JSON, HTML, PDF, trace, and manifest writer. `api.py`, `web.py`, and `cli.py` are delivery adapters. None of these redefine chart or report schemas.

A multi-node deployment should substitute a PostgreSQL or managed-queue repository and object storage behind the same application ports. It must preserve atomic claim semantics, terminal-state deletion, allow-listed artifact names, content hashes, and calculation fingerprints. To accept `Idempotency-Key`, its repository must additionally implement the optional capability with a database-enforced uniqueness invariant.

## Deployment forms

### Independent product

The shipped container can run an API command or a worker command against a shared artifact volume and SQLite database. This form is appropriate for one node, a private team deployment, or a product-specific service boundary.

### Imported Python module

Another Python service can import the package and call deterministic functions directly. No global application object, database, HTTP client, or filesystem directory is created by importing `four_pillars`.

The top-level package exports the structural port contracts and optional idempotency capability for integration type annotations:

```python
from four_pillars import (
    ArtifactPublisher,
    IdempotentReportJobRepository,
    ReportInterpreter,
    ReportJobRepository,
)
```

### Internal MSA service

A platform can deploy the API and worker independently, front them with organization authentication, and replace local storage adapters. Versioned JSON and Pydantic contracts remain the compatibility boundary. Calls across services should carry the calculation version, prompt versions, and fingerprint so provenance is preserved end to end.

A remote repository adapter must keep claim and transition operations atomic. If it implements `IdempotentReportJobRepository`, keyed creation must also be atomic across all API instances. A remote artifact publisher must finish all files in the staging location before returning, because the application service publishes the completed directory only after the port returns successfully.

### Central workflow consumption

Organization-wide `.github` or `naruon` workflows should invoke these repository commands:

```bash
python -m pip install --require-hashes -r requirements/ci.txt
python scripts/product_gap_audit.py
ruff check .
python scripts/check_docs.py
python scripts/check_prompts.py
pytest -m 'not nim_live' --cov=four_pillars --cov-report=term-missing
python -m build --no-isolation
```

The repository remains the source of product-specific policy. Central workflows may add organization controls, attestations, deployment, or release promotion without copying the calculation and quality rules.

## Port behavior contracts

### Report job repository

The base repository owns durable lifecycle state. `claim_next` must atomically move at most one queued job to running. `finish` and `fail` must either update exactly one known job or report that the job does not exist. `delete` removes terminal jobs only. `purge` returns removed identifiers so the caller can clean corresponding artifacts.

### Optional idempotent report-job repository

`create_idempotent` must compare the supplied key digest and canonical request fingerprint and atomically return either the first job or a replay indicator. The same key with a different fingerprint must be rejected without creating a row. A unique database constraint must make this invariant safe across processes and nodes. Raw client keys must never be persisted. Deleting or purging a job also expires its idempotency digest.

### Report interpreter

The interpreter receives the subject label, natal chart, daewoon result, annual snapshot, monthly snapshot, and untrusted user context. It must return `GeneratedReport`; it must not mutate or recalculate deterministic evidence. Any hosted provider, model, prompt version, retry, and repair metadata remains traceable.

### Artifact publisher

The publisher receives a new staging path, the approved report, all deterministic evidence, and privacy-safe traces. It must create the staging directory and all intended files before returning. It must not publish outside the supplied path, and it returns content digests for observability even when the standalone service does not otherwise consume them.

## Data and naming contracts

Database objects created by this product use at least two words in `snake_case`; `camelCase` and `PascalCase` are accepted for external systems that require them. One-word identifiers and mixed underscore/capital styles are rejected by the product-gap audit.

Public files and messages use UUID job identifiers rather than subject names. Artifacts remain under one validated job directory. Integrations must not put names, birth dates, user notes, or raw idempotency keys in queue identifiers, object keys, metrics labels, or log correlation identifiers.

## Versioning and compatibility

Package and API versions follow Semantic Versioning. The changelog records user-visible and integration-visible changes. Calculation and prompt versions are independently recorded because a compatible application release may update one without changing the other.

A breaking calculation-policy change requires a new calculation version and new golden fixtures. A breaking report, port, or API schema change requires a major package version. Prompt wording changes require a prompt semantic-version update and evaluation evidence. Optional capabilities may be added in a minor version when the existing required port remains unchanged and unsupported use fails explicitly.

## Integration acceptance criteria

An integration is conformant when:

- deterministic fixtures and fingerprints match the standalone package;
- hosted interpretation receives immutable evidence as untrusted input;
- no provider fallback occurs under the NVIDIA NIM model label;
- report quality validation runs before publication;
- normal queue creation and queue claims are atomic, and terminal states are distinguishable;
- keyed creation is accepted only when the repository implements `IdempotentReportJobRepository` atomically;
- raw idempotency keys are not persisted and key reuse with a different payload is rejected;
- artifact paths, names, hashes, retention, and deletion remain enforced;
- supplied adapters satisfy the public structural ports without application forks;
- the canonical NIM credential is `NVIDIA_NIM_API_KEY`;
- database object names satisfy the repository naming policy; and
- the full repository gate remains at 100% statement and branch coverage.
