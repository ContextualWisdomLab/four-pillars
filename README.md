# Four Pillars

Deterministic Korean Four Pillars (사주·만세력) calculation and schema-validated AI-assisted report generation.

The product keeps **calendar calculation** and **AI interpretation** on separate trust boundaries. The calculation engine produces immutable pillars, solar-term boundaries, ten-god relationships, hidden stems, twelve growth stages, luck periods, warnings, and a SHA-256 fingerprint. The selected interpretation backend receives those facts as read-only evidence and returns schema-validated analysis. A quality gate rejects deterministic contradictions, unbalanced relationship guidance, vague copy, medical claims, and event certainty before HTML or PDF is emitted.

Hosted interpretation uses [Contextual Orchestrator](https://github.com/ContextualWisdomLab/contextual-orchestrator). The service never silently changes the selected interpretation boundary.

Repository automation uses two independent hourly control loops. The minute-17 loop is a deterministic, model-free release-quality sentinel. The minute-47 loop may use checksum-pinned OpenCode with `NVIDIA_NIM_API_KEY` to propose one bounded pull request only when the queue is empty; model execution, uncredentialed verification, and late publication occur on separate runners, and ordinary exact-head review retains every merge and release decision.

## Features

- Solar and Korean lunar birth input with IANA time zones
- Li Chun and twelve `jie` solar-term boundaries
- Year, month, day, and hour pillars with configurable day rollover
- Ten Gods, hidden stems, twelve growth stages, element balance, combinations and clashes
- Daewoon direction/start age, annual luck, and monthly luck
- Versioned AI prompts for natal, daewoon, annual, monthly, synthesis, practical skills, editorial repair, and LLM judging
- Hosted interpretation through Contextual Orchestrator
- Explicit credential separation and no silent provider fallback
- Searchable Korean A4 PDF, HTML, JSON, and generation manifest
- FastAPI service, Typer CLI, SQLite job queue, worker, Docker, and GitHub Actions
- Structural repository, interpreter, history, idempotency, and artifact-publisher ports for standalone or MSA use
- APA 7th standards and research traceability with hourly regression checks
- Proposal-only hourly OpenCode development with immutable patch handoff and three-runner isolation

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

### Direct NVIDIA NIM

Direct NIM is the default standalone path:

```bash
export INTERPRETATION_BACKEND='nvidia_nim'
export NVIDIA_NIM_API_KEY='...'
export NIM_MODEL='nvidia/llama-3.3-nemotron-super-49b-v1.5'
```

The model name is configuration, not a hard dependency; choose a model currently available to the account. Direct hosted tests are opt-in:

```bash
pytest -m nim_live
```

### Contextual Orchestrator

Point Four Pillars at an approved organization gateway without changing the calculation, prompts, report schemas, queue, or artifact format. Local development may use the validated loopback HTTP exception:

```bash
export INTERPRETATION_BACKEND='contextual_orchestrator'
export CONTEXTUAL_ORCHESTRATOR_BASE_URL='http://127.0.0.1:8100/v1'
export CONTEXTUAL_ORCHESTRATOR_TOKEN='...'
export CONTEXTUAL_ORCHESTRATOR_MODEL='contextual-orchestrator'
export CONTEXTUAL_ORCHESTRATOR_MODE='auto'
export CONTEXTUAL_ORCHESTRATOR_COMPANY='ContextualWisdomLab'
export CONTEXTUAL_ORCHESTRATOR_TEAM='fortune-products'
```

Production must instead use an approved HTTPS URL, for example `https://orchestrator.example.com/v1`. Settings reject remote HTTP endpoints before constructing a credential-bearing client; only `localhost`, `127.0.0.1`, and `::1` may use HTTP for local development.

The adapter sends prompt-safe usage attribution and an explicit orchestration mode through the orchestrator's OpenAI-compatible chat-completions endpoint. It intentionally omits `response_format`, tools, and function-calling fields because those capabilities select the orchestrator's single-agent passthrough path; `auto`, `route`, and `conduct` requests therefore retain real routing or multi-agent execution. Four Pillars still enforces the requested Pydantic schema after generation and may request a bounded repair through the same selected backend. Birth data, user context, generated copy, and credentials are never placed in attribution. A missing or unavailable orchestrator fails the report job visibly; it does not switch to direct NIM.

## Verification

```bash
python -m pip check
python scripts/product_gap_audit.py
ruff check .
python -m compileall -q src tests scripts
python scripts/check_docs.py
python scripts/check_prompts.py
pytest -m 'not nim_live' -W error::ResourceWarning --cov=four_pillars --cov-report=term-missing
python -m build --no-isolation
```

The release gate requires exactly 100 percent statement and branch coverage. Hosted model evaluation is supplementary and never replaces deterministic fixtures, rule-based quality checks, security review, or human review.

## Documents

- [Root Architecture](ARCHITECTURE.md)
- [Agent Development Contract](CLAUDE.md)
- [Changelog](CHANGELOG.md)
- [Product Requirements](docs/product/PRD.md)
- [Technical Requirements](docs/technical/TRD.md)
- [Calculation Rules](docs/technical/CALCULATION.md)
- [Standalone and MSA Modularity](docs/technical/MODULARITY.md)
- [Interpretation Operations](docs/operations/NIM.md)
- [Operations Runbook](docs/operations/RUNBOOK.md)
- [Hourly NVIDIA NIM Product Development](docs/operations/HOURLY_NIM_PRODUCT_DEVELOPMENT.md)
- [Hourly NIM/OpenCode Evidence Doctoring](docs/doctoring/hourly-nim-opencode-development.md)
- [APA 7th Standards and Research References](docs/standards/REFERENCES.md)
- [Standards Traceability](docs/standards/TRACEABILITY.md)
- [UML and Architecture](docs/uml/architecture.md)
- [Security Policy](SECURITY.md)

## Safety

This service provides a traditional symbolic interpretation for reflection. It does not establish facts about the future and must not replace medical, legal, financial, employment, or relationship decisions based on real evidence and qualified advice. Standards traceability governs the software and AI lifecycle; it is not scientific validation of fortune-telling claims or an ISO certification statement.
