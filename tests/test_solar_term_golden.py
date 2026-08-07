"""Validate month-changing solar terms against external calendar evidence."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from four_pillars.calendar import apparent_solar_longitude, calculate_chart, jie_terms
from four_pillars.models import BirthInput

FIXTURE = Path("tests/fixtures/kasi_2026_jie_terms.json")
DOCTORING = Path("docs/doctoring/kasi-solar-term-golden-fixtures.md")
EXPECTED_NAMES = (
    "소한",
    "입춘",
    "경칩",
    "청명",
    "입하",
    "망종",
    "소서",
    "입추",
    "백로",
    "한로",
    "입동",
    "대설",
)


def _fixture() -> dict[str, Any]:
    """Return the committed external-evidence fixture as decoded JSON."""

    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _records() -> list[dict[str, Any]]:
    """Return ordered solar-term records from the committed fixture."""

    return list(_fixture()["terms"])


def _chart_at(moment: datetime) -> Any:
    """Calculate one Seoul chart from an aware fixture instant."""

    wall_clock = moment.replace(tzinfo=None)
    return calculate_chart(BirthInput(birth=wall_clock, timezone="Asia/Seoul"))


def test_authoritative_solar_term_evidence_is_committed() -> None:
    """Require the offline fixture and its provenance document."""

    assert FIXTURE.is_file()
    assert DOCTORING.is_file()


def test_kasi_fixture_schema_and_scope_are_bounded() -> None:
    """Reject silent timezone, tolerance, order, or coverage changes."""

    fixture = _fixture()
    records = _records()

    assert fixture["schema_version"] == "1.0.0"
    assert fixture["source_timezone"] == "Asia/Seoul"
    assert fixture["published_precision"] == "minute"
    assert fixture["maximum_absolute_error_seconds"] == 120
    assert tuple(record["name_ko"] for record in records) == EXPECTED_NAMES
    assert len({record["name_ko"] for record in records}) == 12
    assert all(
        datetime.fromisoformat(record["expected_kst"]).utcoffset()
        == timedelta(hours=9)
        for record in records
    )


def test_apparent_solar_longitude_requires_an_aware_datetime() -> None:
    """Reject ambiguous civil time before any ephemeris calculation occurs."""

    with pytest.raises(ValueError, match="timezone-aware"):
        apparent_solar_longitude(datetime(2026, 1, 1))


@pytest.mark.parametrize("record", _records(), ids=lambda record: record["name_ko"])
def test_calculated_jie_matches_kasi_within_two_minutes(
    record: dict[str, Any],
) -> None:
    """Keep every calculated 2026 month boundary within the published budget."""

    calculated = {term.name_ko: term for term in jie_terms(2026, "Asia/Seoul")}
    expected = datetime.fromisoformat(record["expected_kst"])
    actual = calculated[record["name_ko"]].occurs_at
    delta_seconds = (actual - expected).total_seconds()

    assert calculated[record["name_ko"]].longitude == record["longitude"]
    assert abs(delta_seconds) <= _fixture()["maximum_absolute_error_seconds"], (
        f"{record['name_ko']} differs from KASI by {delta_seconds:+.3f} seconds"
    )


@pytest.mark.parametrize("record", _records(), ids=lambda record: record["name_ko"])
def test_published_jie_changes_month_branch_on_the_expected_side(
    record: dict[str, Any],
) -> None:
    """Change each buyer-visible month pillar across the official boundary."""

    expected = datetime.fromisoformat(record["expected_kst"])
    before = _chart_at(expected - timedelta(minutes=5))
    after = _chart_at(expected + timedelta(minutes=5))

    assert before.month.branch != record["month_branch"]
    assert after.month.branch == record["month_branch"]


def test_kasi_lichun_changes_the_2026_year_pillar() -> None:
    """Change the sexagenary year across the independently published Li Chun."""

    record = next(record for record in _records() if record["name_ko"] == "입춘")
    expected = datetime.fromisoformat(record["expected_kst"])
    before = _chart_at(expected - timedelta(minutes=5))
    after = _chart_at(expected + timedelta(minutes=5))

    assert before.year.hanja == "乙巳"
    assert after.year.hanja == "丙午"
    assert after.calculation_version == "calendar-1.1.0"
