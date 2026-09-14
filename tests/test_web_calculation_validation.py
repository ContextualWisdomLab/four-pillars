"""Make the calculation button use the browser's own field validation.

The primary call to action is ``type="button"``, so submitting never happens and
constraint validation never runs. ``birthPayload`` then reads ``.value`` from a
cleared required field and sends something like ``"T12:00:00"`` as the birth
timestamp, which the API rejects. The customer sees a server validation error
instead of the browser pointing at the field they emptied.
"""

from __future__ import annotations

from four_pillars.web import render_home

# The fields ``birthPayload`` reads that the form marks required.
VALIDATED_FIELDS = ("#birth-date", "#timezone")


def test_the_calculate_button_reports_field_validity() -> None:
    """The page asks the browser to show its own message on an invalid field."""
    assert "reportValidity()" in render_home()


def test_validation_runs_before_the_chart_request() -> None:
    """Checking after sending would not spare the customer the server error."""
    page = render_home()

    assert page.index("reportValidity()") < page.index("'/v1/chart'")


def test_exactly_the_fields_the_calculation_sends_are_checked() -> None:
    """Validating more would block a chart on a field the chart never uses."""
    page = render_home()
    start = page.index("function invalidBirthField()")
    body = page[start : page.index("\n", start)]

    for selector in VALIDATED_FIELDS:
        assert selector in body
    for unused in ("#annual-year", "#monthly-month", "#context"):
        assert unused not in body
