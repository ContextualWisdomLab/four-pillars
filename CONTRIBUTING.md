# Contributing

## Development setup

Use Python 3.11 or 3.12. Create a virtual environment and run `pip install -e '.[dev]'`. Copy `.env.example` only when testing the API or NVIDIA NIM. Offline tests must not require an API key.

## Change workflow

1. Create a focused branch from `main`.
2. Write a failing test before production code for behavior changes.
3. Keep deterministic calculation, AI orchestration, rendering, and transport concerns in separate modules.
4. Run `ruff check .`, prompt and document validators, the non-live test suite, and coverage locally.
5. Open a pull request with calculation evidence and screenshots for visual changes.
6. Resolve review comments, rerun checks, and merge only when the branch is green.

## Domain changes

A calendar rule change must include at least one golden example, the boundary policy, the source or derivation, and a calculation-version increment. AI prompts may explain but may not correct deterministic values. Prompt changes require a version update and an evaluation fixture. Report copy must include constructive possibilities, cautions, and actions; a relationship section may not contain warnings only.

## Commit and review quality

Commits should be independently testable and use conventional prefixes such as `feat:`, `fix:`, `docs:`, `test:`, or `build:`. Reviewers must check deterministic fidelity, privacy, prompt injection boundaries, Korean readability, accessibility, output-file integrity, and failure behavior.
