"""Validate the equation of time against published astronomy, not against itself.

The previous implementation was an unsourced three-term sine fit with no stated
error bound (#58). Replacing it is only meaningful if the replacement is checked
against values established independently of this code, so these tests assert the
shape of the curve every almanac publishes: two extremes with known magnitudes
and dates, and four zero crossings.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from four_pillars.solar import equation_of_time_minutes


def _year_curve(year: int) -> list[tuple[datetime, float]]:
    noon = datetime(year, 1, 1, 12, tzinfo=UTC)
    return [
        (noon + timedelta(days=offset), equation_of_time_minutes(noon + timedelta(days=offset)))
        for offset in range(365)
    ]


def test_the_february_minimum_matches_the_almanac() -> None:
    """About fourteen minutes and a quarter behind, in the second week of February."""
    moment, value = min(_year_curve(2026), key=lambda point: point[1])

    assert -14.5 < value < -14.0
    assert (moment.month, moment.day) == (2, 11)


def test_the_november_maximum_matches_the_almanac() -> None:
    """About sixteen and a half minutes ahead, in the first days of November."""
    moment, value = max(_year_curve(2026), key=lambda point: point[1])

    assert 16.2 < value < 16.7
    assert (moment.month, moment.day) == (11, 3)


def test_the_curve_crosses_zero_four_times_on_the_published_days() -> None:
    """Mid-April, mid-June, the start of September, and Christmas Day."""
    curve = _year_curve(2026)
    crossings = [
        curve[index][0]
        for index in range(1, len(curve))
        if curve[index - 1][1] * curve[index][1] < 0
    ]

    assert [(m.month, m.day) for m in crossings] == [(4, 16), (6, 13), (9, 2), (12, 25)]


def test_a_timezone_aware_moment_is_required() -> None:
    """A naive datetime has no instant, so it cannot have an equation of time."""
    with pytest.raises(ValueError, match="timezone-aware"):
        equation_of_time_minutes(datetime(2026, 6, 15, 12))


def test_the_result_is_stable_across_equivalent_instants() -> None:
    """The same instant expressed in another zone gives the same correction."""
    from zoneinfo import ZoneInfo

    utc_moment = datetime(2026, 3, 20, 3, 0, tzinfo=UTC)
    seoul_moment = utc_moment.astimezone(ZoneInfo("Asia/Seoul"))

    assert equation_of_time_minutes(utc_moment) == pytest.approx(
        equation_of_time_minutes(seoul_moment)
    )
