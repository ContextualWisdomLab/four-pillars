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

### Interpretation adapter

`nim.py`, `prompts/`, and `analysis.py` own the hosted NVIDIA NIM request contract, schema validation, bounded repair, staged interpretation, and prompt provenance. They consume serialized calculation evidence and cannot overwrite deterministic values.

The adapter requires `NVIDIA_NIM_API_KEY` only when interpretation is invoked. Calculation-only imports and endpoints have no hosted-service credential requirement.

### Application orchestration

`service.py` composes calculation, interpretation, quality validation, job state, and artifact publishing. It is the seam for a future dependency-injected application container. A larger platform may wrap this service or provide alternate repositories and publishers while preserving `ReportRequest`, `CalculationBundle`, and `GeneratedReport` semantics.

### Infrastructure adapters

`jobs.py` is the single-node SQLite queue adapter. `reporting.py` is the filesystem artifact publisher. `api.py`, `web.py`, and `cli.py` are delivery adapters. None of these redefine chart or report schemas.

A multi-node deployment should substitute a PostgreSQL or managed-queue adapter and object storage behind the application seam. It must preserve atomic claim semantics, terminal-state deletion, allow-listed artifact names, content hashes, and calculation fingerprints.

## Deployment forms

### Independent product

The shipped container can run an API command or a worker command against a shared artifact volume and SQLite database. This form is appropriate for one node, a private team deployment, or a product-specific service boundary.

### Imported Python module

Another Python service can import the package and call deterministic functions directly. No global application object, database, HTTP client, or filesystem directory is created by importing `four_pillars`.

### Internal MSA service

A platform can deploy the API and worker independently, front them with organization authentication, and replace local storage adapters. Versioned JSON and Pydantic contracts remain the compatibility boundary. Calls across services should carry the calculation version, prompt versions, and fingerprint so provenance is preserved end to end.

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

## Data and naming contracts

Database objects created by this product use at least two words in `snake_case`; `camelCase` and `PascalCase` are accepted for external systems that require them. One-word identifiers and mixed underscore/capital styles are rejected by the product-gap audit.

Public files and messages use UUID job identifiers rather than subject names. Artifacts remain under one validated job directory. Integrations must not put names, birth dates, or user notes in queue identifiers, object keys, metrics labels, or log correlation identifiers.

## Versioning and compatibility

Package and API versions follow Semantic Versioning. The changelog records user-visible and integration-visible changes. Calculation and prompt versions are independently recorded because a compatible application release may update one without changing the other.

A breaking calculation-policy change requires a new calculation version and new golden fixtures. A breaking report or API schema change requires a major package version. Prompt wording changes require a prompt semantic-version update and evaluation evidence.

## Integration acceptance criteria

An integration is conformant when:

- deterministic fixtures and fingerprints match the standalone package;
- hosted interpretation receives immutable evidence as untrusted input;
- no provider fallback occurs under the NVIDIA NIM model label;
- report quality validation runs before publication;
- queue claims are atomic and terminal states are distinguishable;
- artifact paths, names, hashes, retention, and deletion remain enforced;
- the canonical NIM credential is `NVIDIA_NIM_API_KEY`;
- database object names satisfy the repository naming policy; and
- the full repository gate remains at 100% statement and branch coverage.
