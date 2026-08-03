from __future__ import annotations

from datetime import datetime

from four_pillars.calendar import calculate_chart
from four_pillars.fortune import calculate_annual_luck, calculate_daewoon, calculate_monthly_luck
from four_pillars.models import BirthInput, Gender


def chart_1990():
    return calculate_chart(BirthInput(birth=datetime(1990, 6, 15, 8, 30), timezone="Asia/Seoul"))


def test_unspecified_gender_returns_both_daewoon_directions() -> None:
    result = calculate_daewoon(chart_1990(), Gender.UNSPECIFIED, count=3)
    assert [scenario.direction for scenario in result.scenarios] == ["forward", "reverse"]
    assert all(len(scenario.periods) == 3 for scenario in result.scenarios)
    assert all(scenario.warning for scenario in result.scenarios)


def test_yang_year_male_runs_forward_and_female_reverse() -> None:
    chart = chart_1990()  # 庚 is yang
    assert calculate_daewoon(chart, Gender.MALE).scenarios[0].direction == "forward"
    assert calculate_daewoon(chart, Gender.FEMALE).scenarios[0].direction == "reverse"


def test_annual_pillars_and_li_chun_boundary() -> None:
    chart = chart_1990()
    annual_2026 = calculate_annual_luck(chart, 2026)
    annual_2027 = calculate_annual_luck(chart, 2027)
    assert annual_2026.pillar.hanja == "丙午"
    assert annual_2027.pillar.hanja == "丁未"
    assert annual_2026.starts_at.month == 2
    assert annual_2026.ends_at == annual_2027.starts_at


def test_august_2026_monthly_luck_is_bingshen_between_liqiu_and_bailu() -> None:
    monthly = calculate_monthly_luck(chart_1990(), 2026, 8)
    assert monthly.pillar.hanja == "丙申"
    assert monthly.starts_at.month == 8
    assert monthly.ends_at.month == 9
    assert monthly.starts_at < monthly.ends_at


def test_daewoon_periods_are_ordered_and_non_overlapping() -> None:
    scenario = calculate_daewoon(chart_1990(), Gender.FEMALE, count=4).scenarios[0]
    for left, right in zip(scenario.periods, scenario.periods[1:], strict=True):
        assert left.ends_at < right.starts_at
        assert right.start_age - left.start_age == 10
