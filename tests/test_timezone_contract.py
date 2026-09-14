"""Verify that an unusable IANA timezone is rejected as input, never as a server fault."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from four_pillars.api import app
from four_pillars.calendar import calculate_chart
from four_pillars.models import BirthInput

UNUSABLE_TIMEZONES = (
    "Not/AZone",  # well-formed key, no such zone in the database
    "",  # empty key
    "/absolute",  # absolute path
    "../etc/passwd",  # traversal outside the timezone database
)


@pytest.fixture(name="chart_client")
def fixture_chart_client() -> TestClient:
    """Return a client that surfaces handler faults as responses, not raised errors."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.parametrize("timezone_key", UNUSABLE_TIMEZONES)
def test_unusable_timezone_fails_input_validation(timezone_key: str) -> None:
    """Reject every unusable key at the contract boundary with a field-scoped error."""
    with pytest.raises(ValidationError) as rejection:
        BirthInput(birth="1990-05-15T13:30:00", timezone=timezone_key)

    errors = rejection.value.errors()
    assert [error["loc"] for error in errors] == [("timezone",)]
    assert "timezone" in errors[0]["msg"].lower()


@pytest.mark.parametrize("timezone_key", UNUSABLE_TIMEZONES)
def test_chart_endpoint_reports_unusable_timezone_as_client_error(chart_client: TestClient, timezone_key: str) -> None:
    """Answer 422 for a caller timezone typo instead of a 500 internal error."""
    response = chart_client.post(
        "/v1/chart",
        json={"birth": "1990-05-15T13:30:00", "timezone": timezone_key, "gender": "male"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "timezone"]


def test_luck_endpoint_reports_unusable_timezone_as_client_error(
    chart_client: TestClient,
) -> None:
    """Apply the same contract to the nested birth input of temporary-luck requests."""
    response = chart_client.post(
        "/v1/luck/annual",
        json={
            "birth": {"birth": "1990-05-15T13:30:00", "timezone": "Not/AZone"},
            "year": 2026,
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "birth", "timezone"]


@pytest.mark.parametrize("timezone_key", ["Asia/Seoul", "UTC", "Etc/GMT+9", "America/New_York"])
def test_supported_timezones_still_calculate(timezone_key: str) -> None:
    """Keep every timezone the installed database resolves usable end to end."""
    chart = calculate_chart(BirthInput(birth="1990-05-15T13:30:00", timezone=timezone_key))

    assert chart.timezone == timezone_key
    assert chart.normalized_birth.utcoffset() is not None
