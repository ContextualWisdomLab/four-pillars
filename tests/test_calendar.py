from __future__ import annotations

from datetime import datetime

import pytest

from four_pillars.calendar import calculate_chart, jie_terms, normalize_birth, ten_god
from four_pillars.models import BirthInput, CalendarKind, DayBoundary, TimeBasis


@pytest.mark.parametrize(
    ("birth", "expected"),
    [
        (datetime(1990, 6, 15, 8, 30), ("庚午", "壬午", "辛亥", "壬辰")),
        (datetime(1989, 7, 24, 6, 27), ("己巳", "辛未", "乙酉", "己卯")),
    ],
)
def test_known_korean_four_pillars(birth: datetime, expected: tuple[str, ...]) -> None:
    chart = calculate_chart(BirthInput(birth=birth, timezone="Asia/Seoul"))
    actual = (chart.year.hanja, chart.month.hanja, chart.day.hanja, chart.hour.hanja)
    assert actual == expected
    assert len(chart.fingerprint) == 64


def test_unknown_birth_time_does_not_invent_hour_pillar() -> None:
    chart = calculate_chart(
        BirthInput(
            birth=datetime(1990, 6, 15, 8, 30),
            timezone="Asia/Seoul",
            birth_time_known=False,
        )
    )
    assert chart.hour is None
    assert any("시주" in warning for warning in chart.boundary_warnings)


def test_month_changes_at_liqiu_not_first_day_of_august() -> None:
    before = calculate_chart(BirthInput(birth=datetime(2026, 8, 1, 12), timezone="Asia/Seoul"))
    after = calculate_chart(BirthInput(birth=datetime(2026, 8, 15, 12), timezone="Asia/Seoul"))
    assert before.month.branch == "未"
    assert after.month.hanja == "丙申"


def test_birth_near_jie_emits_boundary_warning() -> None:
    liqiu = jie_terms(2026, "Asia/Seoul")[7].occurs_at
    chart = calculate_chart(
        BirthInput(birth=liqiu.replace(tzinfo=None), timezone="Asia/Seoul")
    )
    assert chart.boundary_warnings
    assert any("입추" in warning for warning in chart.boundary_warnings)


def test_late_zi_policy_advances_day_at_2300() -> None:
    midnight = calculate_chart(
        BirthInput(
            birth=datetime(2026, 8, 3, 23, 30),
            timezone="Asia/Seoul",
            day_boundary=DayBoundary.MIDNIGHT,
        )
    )
    late_zi = calculate_chart(
        BirthInput(
            birth=datetime(2026, 8, 3, 23, 30),
            timezone="Asia/Seoul",
            day_boundary=DayBoundary.LATE_ZI,
        )
    )
    assert (late_zi.day.sexagenary_index - midnight.day.sexagenary_index) % 60 == 1


def test_lunar_new_year_2024_converts_to_solar_february_10() -> None:
    normalized = normalize_birth(
        BirthInput(
            birth=datetime(2024, 1, 1, 9),
            timezone="Asia/Seoul",
            calendar=CalendarKind.LUNAR,
        )
    )
    assert normalized.date().isoformat() == "2024-02-10"


def test_1990_regular_and_leap_fifth_lunar_months_are_distinct() -> None:
    regular = normalize_birth(
        BirthInput(
            birth=datetime(1990, 5, 23, 8, 30),
            calendar=CalendarKind.LUNAR,
        )
    )
    leap = normalize_birth(
        BirthInput(
            birth=datetime(1990, 5, 23, 8, 30),
            calendar=CalendarKind.LUNAR,
            lunar_leap_month=True,
        )
    )
    assert regular.date().isoformat() == "1990-06-15"
    assert leap.date().isoformat() == "1990-07-15"


def test_solar_time_requires_longitude() -> None:
    with pytest.raises(ValueError, match="longitude"):
        normalize_birth(
            BirthInput(
                birth=datetime(1990, 6, 15, 8, 30),
                timezone="Asia/Seoul",
                time_basis=TimeBasis.MEAN_SOLAR,
            )
        )


def test_ten_god_examples_for_xin_day_master() -> None:
    assert ten_god(7, 2) == "정관"  # 辛 controlled by opposite-polarity 丙
    assert ten_god(7, 8) == "상관"  # 辛 produces opposite-polarity 壬
    assert ten_god(7, 1) == "편재"  # 辛 controls same-polarity 乙
