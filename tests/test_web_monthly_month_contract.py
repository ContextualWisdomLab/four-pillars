"""Stop the studio from posting a monthly window it failed to parse.

The submit handler does `value.split('-').map(Number)` on the month field and
uses the result without checking it. When the value is not `YYYY-MM` the parse
degrades silently: an empty field yields year 0, because `Number('')` is 0, and
in every failing case the month is `undefined`, which `JSON.stringify` drops
from the request entirely. The server then answers a malformed request instead
of the page saying which field is wrong.

The field is `required`, but that only guarantees non-empty. A browser that does
not implement `type="month"` renders a plain text box, where `2026` and
`2026년 8월` both satisfy `required` and both produce a broken payload.
"""

from __future__ import annotations

from four_pillars.web import render_home


def test_the_month_field_constrains_a_text_fallback() -> None:
    """A browser without a month picker must still be held to YYYY-MM."""
    page = render_home()
    field = page[page.index('id="monthly-month"') : page.index('id="monthly-month"') + 220]

    assert "pattern=" in field


def test_the_submit_path_checks_the_parsed_window() -> None:
    """Parsing has to be verified before the request is built, not after."""
    page = render_home()

    assert "monthlyWindow" in page
    assert page.index("monthlyWindow") < page.index("'/v1/reports'")


def test_an_unparsable_window_is_reported_in_the_page() -> None:
    """The customer is told which field is wrong instead of reading a 422."""
    assert "분석 월" in render_home()
    assert "YYYY-MM" in render_home()
