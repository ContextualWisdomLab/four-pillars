"""Keep the deterministic luck calculations inside the PDF the customer keeps.

``render_pdf`` accepts ``daewoon``, ``annual``, and ``monthly`` and renders the
natal pillars only. The HTML artifact carries a 세운/월운 table and a 대운
table; the PDF carried neither, so a reader holding the downloaded report saw
interpretation about a luck period without the 간지 it was grounded in.

Each test changes exactly one calculation and asserts the bytes move. The last
test pins the method itself: identical input must produce identical bytes, so a
difference above can only come from the data.
"""

from __future__ import annotations

from pathlib import Path

from reportlab import rl_config
from test_reporting import bundle, report

from four_pillars.fortune import calculate_annual_luck, calculate_daewoon, calculate_monthly_luck
from four_pillars.models import Gender
from four_pillars.reporting import render_pdf

rl_config.invariant = 1


def _pdf(tmp_path: Path, name: str, daewoon, annual, monthly) -> bytes:
    chart = bundle()[0]
    target = tmp_path / f"{name}.pdf"
    render_pdf(target, report(), chart, daewoon, annual, monthly)
    return target.read_bytes()


def test_the_daewoon_scenario_reaches_the_pdf(tmp_path: Path) -> None:
    """A different daewoon direction means different 간지 on the page."""
    chart, daewoon, annual, monthly = bundle()
    other = calculate_daewoon(chart, Gender.MALE, count=2)

    assert _pdf(tmp_path, "a", daewoon, annual, monthly) != _pdf(
        tmp_path, "b", other, annual, monthly
    )


def test_the_annual_luck_reaches_the_pdf(tmp_path: Path) -> None:
    """The 세운 pillar and its Li-Chun-bounded dates must be printed."""
    chart, daewoon, annual, monthly = bundle()
    other = calculate_annual_luck(chart, 2027)

    assert _pdf(tmp_path, "a", daewoon, annual, monthly) != _pdf(
        tmp_path, "b", daewoon, other, monthly
    )


def test_the_monthly_luck_reaches_the_pdf(tmp_path: Path) -> None:
    """The 월운 pillar and its solar-term window must be printed."""
    chart, daewoon, annual, monthly = bundle()
    other = calculate_monthly_luck(chart, 2026, 3)

    assert _pdf(tmp_path, "a", daewoon, annual, monthly) != _pdf(
        tmp_path, "b", daewoon, annual, other
    )


def test_the_same_calculations_render_identical_bytes(tmp_path: Path) -> None:
    """Without this the three tests above could be measuring a timestamp."""
    _, daewoon, annual, monthly = bundle()

    assert _pdf(tmp_path, "a", daewoon, annual, monthly) == _pdf(
        tmp_path, "b", daewoon, annual, monthly
    )
