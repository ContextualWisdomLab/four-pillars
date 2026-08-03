# Four Pillars

Deterministic Korean Four Pillars (사주·만세력) calculation and NVIDIA NIM-assisted report generation.

The product keeps **calendar calculation** and **AI interpretation** on separate trust boundaries. The calculation engine produces immutable pillars, solar-term boundaries, ten-god relationships, hidden stems, twelve growth stages, luck periods, warnings, and a SHA-256 fingerprint. NVIDIA NIM receives those facts as read-only evidence and returns schema-validated analysis. A quality gate rejects deterministic contradictions, unbalanced relationship guidance, vague copy, medical claims, and event certainty before HTML or PDF is emitted.

## Features

- Solar and Korean lunar birth input with IANA time zones
- Li Chun and twelve `jie` solar-term boundaries
- Year, month, day, and hour pillars with configurable day rollover
- Ten Gods, hidden stems, twelve growth stages, element balance, combinations and clashes
- Daewoon direction/start age, annual luck, and monthly luck
- Versioned AI prompts for natal, daewoon, annual, monthly, synthesis, practical skills, editorial repair, and LLM judging
- NVIDIA NIM-only LLM boundary; no silent provider fallback
- Searchable Korean A4 PDF, HTML, JSON, and generation manifest
- FastAPI service, Typer CLI, SQLite job queue, worker, Docker, and GitHub Actions

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
pytest
four-pillars calculate --birth '1990-06-15T08:30:00' --timezone Asia/Seoul
four-pillars serve
```

To generate AI reports, set a hosted NVIDIA NIM key:

```bash
export NVIDIA_NIM_API_KEY='...'
export NIM_MODEL='nvidia/llama-3.3-nemotron-super-49b-v1.5'
```

The model name is configuration, not a hard dependency; choose a free model available to the account. Live tests are opt-in:

```bash
pytest -m nim_live
```

## Documents

- [Product Requirements](docs/product/PRD.md)
- [Technical Requirements](docs/technical/TRD.md)
- [Calculation Rules](docs/technical/CALCULATION.md)
- [NIM Operations](docs/operations/NIM.md)
- [UML and Architecture](docs/uml/architecture.md)
- [Security Policy](SECURITY.md)

## Safety

This service provides a traditional symbolic interpretation for reflection. It does not establish facts about the future and must not replace medical, legal, financial, employment, or relationship decisions based on real evidence and qualified advice.
