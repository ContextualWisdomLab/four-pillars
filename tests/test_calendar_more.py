from __future__ import annotations

from datetime import date, datetime

import pytest

from four_pillars.calendar import (
    calculate_chart,
    interactions_between,
    make_pillar,
    normalize_birth,
    sexagenary_index,
    solar_term_utc,
)
from four_pillars.fortune import calculate_daewoon, current_period
from four_pillars.models import BirthInput, Gender, TimeBasis


def test_mean_and_apparent_solar_time_adjust_wall_clock() -> None:
    civil = BirthInput(birth=datetime(1990, 6, 15, 8, 30), timezone="Asia/Seoul")
    mean = civil.model_copy(update={"longitude": 127.0, "time_basis": TimeBasis.MEAN_SOLAR})
    apparent = civil.model_copy(update={"longitude": 127.0, "time_basis": TimeBasis.APPARENT_SOLAR})
    civil_moment = normalize_birth(civil)
    mean_moment = normalize_birth(mean)
    apparent_moment = normalize_birth(apparent)
    assert mean_moment < civil_moment
    assert apparent_moment != mean_moment
    assert 25 <= (civil_moment - mean_moment).total_seconds() / 60 <= 40


def test_core_interactions_are_named() -> None:
    zi = make_pillar(sexagenary_index(0, 0), 0)
    wu = make_pillar(sexagenary_index(6, 6), 0)
    kinds = {item.kind for item in interactions_between([zi, wu])}
    assert "stem_clash" in kinds
    assert "branch_clash" in kinds

    jia_zi = make_pillar(0, 0)
    ji_chou = make_pillar(sexagenary_index(5, 1), 0)
    kinds = {item.kind for item in interactions_between([jia_zi, ji_chou])}
    assert "stem_combine" in kinds
    assert "branch_combine" in kinds


def test_impossible_stem_branch_parity_is_rejected() -> None:
    with pytest.raises(ValueError, match="parity"):
        sexagenary_index(0, 1)


def test_unsupported_solar_longitude_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        solar_term_utc(2026, 123.456)


def test_fingerprint_records_time_policy() -> None:
    base = BirthInput(birth=datetime(1990, 6, 15, 23, 30), timezone="Asia/Seoul")
    civil = calculate_chart(base)
    solar = calculate_chart(
        base.model_copy(update={"longitude": 127.0, "time_basis": TimeBasis.MEAN_SOLAR})
    )
    assert civil.fingerprint != solar.fingerprint


def test_current_daewoon_period_can_be_selected_by_date() -> None:
    chart = calculate_chart(BirthInput(birth=datetime(1990, 6, 15, 8, 30), timezone="Asia/Seoul"))
    periods = calculate_daewoon(chart, Gender.FEMALE, count=4).scenarios[0].periods
    selected = current_period(periods, periods[1].starts_at)
    assert selected == periods[1]
    assert current_period(periods, date(1800, 1, 1)) is None
