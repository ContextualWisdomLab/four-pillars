# Standalone and Modular Service Architecture

Four Pillars can run as an independent product or be imported as a bounded module in a larger ContextualWisdomLab platform. Deterministic domain contracts survive both forms; integration may replace infrastructure adapters but must not redefine calendar evidence, prompt semantics, quality gates, or artifact provenance.

## Architectural goals

1. **Product completeness:** one repository, image, API process, worker process, SQLite queue, local artifact store, browser studio, CLI, and Contextual Orchestrator adapter can calculate and publish reports.
2. **Module portability:** callers can import calculation functions and Pydantic contracts without starting FastAPI, SQLite, a worker, or a model client.
3. **Bounded trust:** deterministic calculation, interpretation, editorial validation, persistence, and delivery remain separate boundaries.
4. **Replaceable infrastructure:** a platform integration may replace the queue, artifact store, authentication edge, deployment workflow, or injected interpretation port while retaining application and domain behavior.
5. **Central governance compatibility:** organization `.github`, `naruon`, Contextual Orchestrator, and other repositories consume checked-in contracts rather than duplicating product rules.
6. **Orchestration ownership:** provider discovery, provider credentials, free-pool eligibility, routing, and provider fallback belong to the Contextual Orchestrator bounded context.
7. **Fail closed:** the repository-owned LLM route is `orchestrator/free`; a gateway or free-pool failure never activates a direct provider.

## Bounded components

### Deterministic calculation core

`calendar.py`, `fortune.py`, `constants.py`, and immutable calculation models contain no FastAPI or HTTPX dependency. Their public integration surface includes:

```python
from four_pillars import (
    BirthInput,
    calculate_annual_luck,
    calculate_chart,
    calculate_daewoon,
    calculate_monthly_luck,
)
```

This boundary owns solar/lunar normalization, solar terms, pillars, Ten Gods, hidden stems, Twelve Growth Stages, interactions, luck periods, warnings, and the evidence fingerprint. A platform treats these outputs as immutable facts for the selected calculation policy.

### Structured-generation boundary

`generation.py` defines `StructuredGenerationClient`, the protocol consumed by `analysis.py`. The protocol returns a Pydantic-validated object and compatible generation trace. It does not expose provider administration or routing internals to the domain layer.

`infrastructure/orchestration/openai_compatible.py` owns provider-neutral OpenAI-compatible HTTP/JSON transport mechanics. `infrastructure/orchestration/contextual_orchestrator.py` implements the Model Orchestration anti-corruption layer: it labels user/calculation payloads as untrusted input, validates Pydantic output, applies bounded retry and schema repair, and attaches prompt-safe organizational attribution. The active product contract fixes the virtual model to `orchestrator/free`.

The historical provider-specific `nim.py` module and direct provider interpreter have been removed. `four_pillars.contextual_orchestrator` remains only as a compatibility re-export so existing imports can converge without creating a second implementation boundary.

### Interpretation adapters

`ContextualOrchestratorReportInterpreter` is the repository-owned implementation of `ReportInterpreter`. It opens `ContextualOrchestratorClient` only when a report is generated, attaches prompt-safe organizational attribution, and preserves strict report schemas.

`build_report_interpreter(settings)` has no provider-selection branch. Product configuration accepts only:

```env
INTERPRETATION_BACKEND=contextual_orchestrator
CONTEXTUAL_ORCHESTRATOR_MODEL=orchestrator/free
```

A caller may inject another `ReportInterpreter` directly for an independently owned MSA composition. That caller-owned choice does not reintroduce a provider option into Four Pillars' configuration or composition root.

### Application orchestration

`service.py` composes calculation, interpretation, quality validation, job state, and artifact publishing. `ReportService` accepts three required structural ports from `ports.py`:

- `ReportJobRepository` for durable job creation, atomic claims, transitions, deletion, and retention;
- `ReportInterpreter` for turning immutable evidence into a validated `GeneratedReport`; and
- `ArtifactPublisher` for publishing approved artifacts into an isolated staging directory.

Two runtime-checkable capabilities are layered on the repository boundary without extending the required base port:

- `IdempotentReportJobRepository` provides atomic keyed creation; and
- `ReportJobHistoryRepository` provides stable newest-first history traversal.

Existing organization adapters remain compatible with normal creation, lookup, processing, deletion, and retention. Keyed creation or history traversal fails explicitly with HTTP 501 when the corresponding capability is absent; the service never substitutes process-local locking or history for a distributed guarantee.

If no ports are supplied, the service creates `JobStore`, `ContextualOrchestratorReportInterpreter`, and `FilesystemArtifactPublisher`. `JobStore` implements the base repository plus both optional capabilities. An integration may replace one adapter without replacing the others.

```python
from four_pillars.service import ReportService

service = ReportService(
    settings,
    store=postgres_report_repository,
    interpreter=internal_report_interpreter,
    publisher=object_storage_publisher,
)
```

Injected implementations are structurally typed. They do not need to inherit product base classes, but their behavior must satisfy the documented protocol and acceptance criteria.

### Infrastructure adapters

`jobs.py` is the single-node SQLite implementation of the base, idempotency, and history repository contracts. `history.py` owns strict privacy-safe cursor encoding. `adapters.py` contains the application-facing orchestration adapter and filesystem publisher. `infrastructure/orchestration` owns the external model-gateway ACL and transport. `reporting.py` owns atomic JSON, HTML, PDF, trace, and manifest writing. `api.py`, `web.py`, and `cli.py` are delivery adapters. None redefine chart or report schemas.

A multi-node deployment should substitute PostgreSQL or a managed queue and object storage behind the same ports. It must preserve atomic claim semantics, terminal-state deletion, allow-listed artifact names, content hashes, fingerprints, database-enforced idempotency, and deterministic `(created_at DESC, id DESC)` history ordering.

## Deployment forms

### Independent product

The shipped container runs API or worker commands against a shared artifact volume and SQLite database. LLM-backed reports require an approved Contextual Orchestrator gateway. This form is appropriate for one node, a private team, or a product-specific service boundary; it is independent in application ownership, not in provider routing.

### Imported Python module

Another Python service can import the package and call deterministic functions directly. Importing `four_pillars` does not create a global application, database, HTTP client, worker, or filesystem directory.

The top-level package exposes the required structural ports and optional repository capabilities for integration type annotations.

### Internal MSA service with Contextual Orchestrator

A platform can deploy API and worker separately, front them with organization authentication, replace persistence and artifacts, and configure:

```env
INTERPRETATION_BACKEND=contextual_orchestrator
CONTEXTUAL_ORCHESTRATOR_BASE_URL=https://orchestrator.internal.example/v1
CONTEXTUAL_ORCHESTRATOR_TOKEN=...
CONTEXTUAL_ORCHESTRATOR_MODEL=orchestrator/free
CONTEXTUAL_ORCHESTRATOR_COMPANY=ContextualWisdomLab
CONTEXTUAL_ORCHESTRATOR_TEAM=fortune-products
```

Four Pillars sends schema-constrained requests through the gateway's OpenAI-compatible surface. Usage attribution contains only approved organization labels. Subject names, birth data, user notes, fingerprints, generated text, artifact paths, and credentials never become attribution dimensions.

Calls across services preserve virtual model, prompt versions, and calculation fingerprint through Four Pillars traces and manifests. Current traces are not W3C distributed traces; `traceparent` propagation is a separately documented target state.

### Central workflow consumption

Organization-wide maintainers and `naruon` workflows should invoke repository-owned commands:

```bash
python -m pip install --require-hashes -r requirements/ci.txt
python scripts/product_gap_audit.py
ruff check .
python -m compileall -q src tests scripts
python scripts/check_docs.py
python scripts/check_prompts.py
pytest -m 'not orchestrator_live' --cov=four_pillars --cov-report=term-missing
python -m build --no-isolation
```

The repository remains the source of product-specific policy. The organization-level autonomous development loop may add research, review orchestration, DDD audits, and bounded product increments without embedding another provider-credentialed writer in this repository.

## Port behavior contracts

### Report job repository

`claim_next` atomically moves at most one queued job to running. `finish` and `fail` update exactly one known job. `delete` removes terminal jobs only. `purge` returns removed identifiers so matching artifacts can be cleaned.

### Optional idempotent report-job repository

`create_idempotent` compares key digest and canonical request fingerprint and atomically returns the first job or a replay indicator. The same key with a different fingerprint is rejected. A unique database constraint makes this safe across processes/nodes. Raw keys are never persisted; deletion or purge expires the digest.

### Optional report-job history repository

`list_jobs` returns at most the requested limit in `(created_at DESC, id DESC)` order and an opaque continuation cursor only when a later row exists. The cursor contains only UTC timestamp and random job UUID. Malformed or unsupported cursors are rejected rather than guessed.

### Report interpreter

The interpreter receives subject label, natal chart, daewoon, annual snapshot, monthly snapshot, and untrusted context. It returns `GeneratedReport` and cannot mutate or recalculate evidence. Virtual-model/prompt/retry/repair metadata remains traceable. The repository-owned implementation never calls a direct provider.

### Structured generation client

A client accepts a system prompt, untrusted payload, Pydantic response model, optional model override within its own internal interface, temperature, and token bound. The product configuration prevents changing the repository-owned virtual model away from `orchestrator/free`. Contextual Orchestrator additionally receives approved attribution and routing metadata while returning the same application-level trace contract.

### Artifact publisher

The publisher receives a new staging path, approved report, deterministic evidence, and privacy-safe traces. It creates every intended file before returning, never publishes outside the supplied path, and returns content digests.

## Data and naming contracts

Application-owned database objects use at least two words, preferably `snake_case`; camelCase and PascalCase are accepted only for external systems requiring them. The product-gap audit rejects one-word or mixed invalid identifiers. This integration adds no database object.

Public files and messages use UUID job identifiers rather than subject names. Integrations must not put names, birth dates, notes, raw idempotency keys, request fingerprints, report copy, prompts, or model credentials in queue identifiers, history cursors, object keys, usage attribution, metrics labels, or trace correlation identifiers.

## Versioning and compatibility

Package/API versions follow Semantic Versioning. Calculation and prompt versions are independently recorded. A breaking calculation-policy change requires a new calculation version and golden fixtures. A breaking report, required-port, or API schema change requires a major version. Optional adapters may be added in a minor version when required ports and product trust boundaries remain compatible.

## Integration acceptance criteria

An integration is conformant when:

- deterministic fixtures and fingerprints match the package;
- interpretation receives immutable evidence as untrusted input;
- the repository composition routes LLM work only through Contextual Orchestrator;
- the product virtual model is `orchestrator/free` and direct-provider backend/model values are rejected;
- no provider-native credential appears in product runtime configuration;
- prompt/model/attempt/repair provenance remains available;
- report quality validation runs before publication;
- queue creation/claims are atomic and terminal states remain distinguishable;
- idempotency and history are exposed only through their optional capabilities;
- public collection items and cursors exclude private request/report fields;
- raw idempotency keys are not persisted;
- artifact paths, names, hashes, retention, and deletion remain enforced;
- supplied adapters satisfy structural ports without application forks;
- attribution contains organization labels only;
- database object names satisfy repository policy; and
- the full gate remains at exactly 100 percent statement and branch coverage.

## Standards doctoring

`docs/standards/REFERENCES.md` contains APA 7th references. `docs/standards/TRACEABILITY.md` maps ISO/IEC 25010:2023, ISO/IEC 42001:2023, ISO/IEC 23894:2023, NIST AI RMF, NIST AI 600-1, RFC 9457, W3C Trace Context, and peer-reviewed LLM-judge research to code/tests and residual gaps. Scheduled checks detect missing references or control mappings; the crosswalk is not an ISO certification or scientific validation of traditional interpretation.
