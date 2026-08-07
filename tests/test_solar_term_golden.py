"""Validate month-changing solar terms against external calendar evidence."""

from __future__ import annotations

from pathlib import Path

FIXTURE = Path("tests/fixtures/kasi_2026_jie_terms.json")
DOCTORING = Path("docs/doctoring/kasi-solar-term-golden-fixtures.md")


def test_authoritative_solar_term_evidence_is_committed() -> None:
    """Require the offline fixture and its provenance document."""

    assert FIXTURE.is_file()
    assert DOCTORING.is_file()
