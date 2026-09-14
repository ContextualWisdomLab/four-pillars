"""Tell the customer when their stated birth clock is not a single real instant.

Korea observed daylight saving in 1987 and 1988. A wall clock inside a
spring-forward gap never happened, and one inside an autumn fold happened
twice. ``normalize_birth`` attaches the zone with ``replace(tzinfo=...)``, which
resolves both cases to one instant without saying so.

The hour pillar is read from the wall clock and is unaffected. What moves is the
instant: a stated 02:30 on 1987-05-10 is carried as ``02:30+09:00``, an offset
Asia/Seoul did not have then, and that instant reads as 03:30 on the zone's own
clock. Solar-term boundaries are compared against the instant, so a birth near
one is judged an hour away from the time the customer wrote down.
"""

from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest

from four_pillars.calendar import calculate_chart
from four_pillars.models import BirthInput

GAP = datetime(1987, 5, 10, 2, 30)
FOLD = datetime(1987, 10, 11, 2, 30)
ORDINARY = datetime(1990, 6, 15, 8, 30)


def _warnings(birth: datetime) -> list[str]:
    return calculate_chart(BirthInput(birth=birth, timezone="Asia/Seoul")).boundary_warnings


@pytest.mark.parametrize("birth", [GAP, datetime(1988, 5, 8, 2, 30)])
def test_a_clock_inside_the_spring_gap_is_reported(birth: datetime) -> None:
    """A time the zone never had must not be resolved in silence."""
    assert any("존재하지 않습니다" in warning for warning in _warnings(birth))


@pytest.mark.parametrize("birth", [FOLD, datetime(1988, 10, 9, 2, 30)])
def test_a_clock_inside_the_autumn_fold_is_reported(birth: datetime) -> None:
    """A time the zone had twice must say which of the two was used."""
    assert any("두 번 존재합니다" in warning for warning in _warnings(birth))


def test_an_ordinary_clock_carries_no_transition_warning() -> None:
    """Nothing is invented for a birth nowhere near a transition."""
    for warning in _warnings(ORDINARY):
        assert "존재하지 않습니다" not in warning
        assert "두 번 존재합니다" not in warning


def test_the_gap_clock_denotes_an_instant_the_zone_reads_an_hour_later() -> None:
    """The fact the warning exists to disclose, asserted rather than asserted about."""
    normalized = calculate_chart(BirthInput(birth=GAP, timezone="Asia/Seoul")).normalized_birth
    # Re-reading has to go through UTC. astimezone into the zone the value already
    # carries returns it untouched and would hide exactly what is being measured.
    on_the_zone_clock = normalized.astimezone(UTC).astimezone(ZoneInfo("Asia/Seoul"))

    assert normalized.replace(tzinfo=None) == GAP
    assert on_the_zone_clock.replace(tzinfo=None) == datetime(1987, 5, 10, 3, 30)
