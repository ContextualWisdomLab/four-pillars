# Four Pillars

Deterministic Korean Four Pillars (사주·만세력) calculation and schema-validated AI-assisted report generation.

The product keeps **calendar calculation** and **AI interpretation** on separate trust boundaries. The calculation engine produces immutable pillars, solar-term boundaries, ten-god relationships, hidden stems, twelve growth stages, luck periods, warnings, and a SHA-256 fingerprint. The interpretation application context receives those facts as read-only evidence and crosses a `ReportInterpreter` port into [Contextual Orchestrator](https://github.com/ContextualWisdomLab/contextual-orchestrator). A quality gate rejects deterministic contradictions, unbalanced relationship guidance, vague copy, medical claims, and event certainty before HTML or PDF is emitted.

Four Pillars does not select or authenticate individual model providers in its product runtime. Provider discovery, free-pool eligibility, routing, and provider fallback belong to Contextual Orchestrator. The repository-owned composition is fixed to the fail-closed `orchestrator/free` virtual route and never silently falls back to a direct provider.

Repository automation keeps a model-free hourly release-quality sentinel. Autonomous product development is coordinated by the shared ContextualWisdomLab maintainer loop rather than a repository-specific provider-credentialed coding workflow. This avoids duplicated writer authority and keeps model-routing policy in the orchestration bounded context.

## Features

- Solar and Korean lunar birth input with IANA time zones
- Li Chun and twelve `jie` solar-term boundaries
- Year, month, day, and hour pillars with configurable day rollover
- Ten Gods, hidden stems, twelve growth stages, element balance, combinations and clashes
- Daewoon direction/start age, annual luck, and monthly luck
- Versioned AI prompts for natal, daewoon, annual, monthly, synthesis, practical skills, editorial repair, and LLM judging
- Contextual Orchestrator anti-corruption layer fixed to `orchestrator/free`
- No product-runtime provider credentials or direct-provider fallback
- Searchable Korean A4 PDF, HTML, JSON, and generation manifest
- FastAPI service, Typer CLI, SQLite job queue, worker, Docker, and GitHub Actions
- Structural repository, interpreter, history, idempotency, and artifact-publisher ports for standalone or MSA use
- APA 7th standards and research traceability with hourly regression checks

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
pytest
four-pillars calculate --birth '1990-06-15T08:30:00' --timezone Asia/Seoul
uvicorn four_pillars.api:app --host 0.0.0.0 --port 8000
```

Calculation-only operations do not need a model credential. Report generation needs an approved Contextual Orchestrator gateway:

```bash
export INTERPRETATION_BACKEND='contextual_orchestrator'
export CONTEXTUAL_ORCHESTRATOR_BASE_URL='http://127.0.0.1:8100/v1'
export CONTEXTUAL_ORCHESTRATOR_TOKEN='...'
export CONTEXTUAL_ORCHESTRATOR_MODEL='orchestrator/free'
export CONTEXTUAL_ORCHESTRATOR_MODE='auto'
export CONTEXTUAL_ORCHESTRATOR_COMPANY='ContextualWisdomLab'
export CONTEXTUAL_ORCHESTRATOR_TEAM='fortune-products'
```

Production must use an approved HTTPS gateway URL. Settings reject remote HTTP endpoints before constructing a credential-bearing client; only `localhost`, `127.0.0.1`, and `::1` may use HTTP for local development.

The adapter sends prompt-safe usage attribution and a bounded orchestration mode through the gateway's OpenAI-compatible chat-completions endpoint. It intentionally omits provider passthrough fields such as `response_format`, tools, and function-calling controls because those can collapse orchestration to a provider-specific path. Four Pillars requests JSON in the prompt, validates the returned object with Pydantic, and permits a bounded repair through the same `orchestrator/free` route. Birth data, user context, generated copy, and credentials are never placed in attribution.

A missing gateway, empty free pool, or invalid response fails the report job visibly. The deterministic calculation path remains available and Four Pillars does not switch to NVIDIA NIM, OpenAI, OpenRouter, Bytez, or another provider directly.

## Verification

```bash
python -m pip check
python scripts/product_gap_audit.py
ruff check .
python -m compileall -q src tests scripts
python scripts/check_docs.py
python scripts/check_prompts.py
pytest -m 'not orchestrator_live' -W error::ResourceWarning --cov=four_pillars --cov-report=term-missing
python -m build --no-isolation
```

The release gate requires exactly 100 percent statement and branch coverage. Live `orchestrator/free` evaluation is supplementary and never replaces deterministic fixtures, rule-based quality checks, security review, or human review.

For an opt-in live test, configure the gateway URL and token, then run:

```bash
pytest -m orchestrator_live -vv
python scripts/orchestrator_eval.py
```

## Documents

- [Root Architecture](ARCHITECTURE.md)
- [Agent Development Contract](CLAUDE.md)
- [Changelog](CHANGELOG.md)
- [Product Requirements](docs/product/PRD.md)
- [Technical Requirements](docs/technical/TRD.md)
- [Calculation Rules](docs/technical/CALCULATION.md)
- [Standalone and MSA Modularity](docs/technical/MODULARITY.md)
- [Model Orchestration Operations](docs/operations/ORCHESTRATION.md)
- [Operations Runbook](docs/operations/RUNBOOK.md)
- [Hourly Product Quality Loop](docs/operations/HOURLY_PRODUCT_LOOP.md)
- [APA 7th Standards and Research References](docs/standards/REFERENCES.md)
- [Standards Traceability](docs/standards/TRACEABILITY.md)
- [UML and Architecture](docs/uml/architecture.md)
- [Security Policy](SECURITY.md)

## Safety

This service provides a traditional symbolic interpretation for reflection. It does not establish facts about the future and must not replace medical, legal, financial, employment, or relationship decisions based on real evidence and qualified advice. Standards traceability governs the software and AI lifecycle; it is not scientific validation of fortune-telling claims or an ISO certification statement.
