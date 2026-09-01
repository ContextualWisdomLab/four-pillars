from __future__ import annotations

import json
from datetime import datetime

from click import unstyle
from typer.testing import CliRunner

from four_pillars.cli import app

runner = CliRunner()


def test_calculate_command_prints_golden_chart() -> None:
    result = runner.invoke(
        app,
        [
            "calculate",
            "--birth",
            "1990-06-15T08:30:00",
            "--timezone",
            "Asia/Seoul",
            "--gender",
            "female",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert [payload[key]["hanja"] for key in ("year", "month", "day", "hour")] == [
        "庚午",
        "壬午",
        "辛亥",
        "壬辰",
    ]


def test_calculate_command_applies_bucheon_apparent_solar_time() -> None:
    result = runner.invoke(
        app,
        [
            "calculate",
            "--birth",
            "1990-06-15T08:30:00",
            "--timezone",
            "Asia/Seoul",
            "--longitude",
            "126.766",
            "--time-basis",
            "apparent_solar",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    normalized = datetime.fromisoformat(payload["normalized_birth"])
    expected = datetime.fromisoformat("1990-06-15T07:57:00+09:00")
    assert abs((normalized - expected).total_seconds()) < 30
    assert payload["hour"]["hanja"] == "壬辰"


def test_calculate_command_distinguishes_regular_and_leap_lunar_months() -> None:
    shared = [
        "calculate",
        "--birth",
        "1990-05-23T08:30:00",
        "--calendar",
        "lunar",
    ]

    regular = runner.invoke(app, shared)
    leap = runner.invoke(app, [*shared, "--lunar-leap-month"])

    assert regular.exit_code == 0, regular.output
    assert leap.exit_code == 0, leap.output
    assert json.loads(regular.output)["normalized_birth"].startswith("1990-06-15T08:30:00")
    assert json.loads(leap.output)["normalized_birth"].startswith("1990-07-15T08:30:00")


def test_calculate_command_rejects_invalid_time_basis_without_traceback() -> None:
    result = runner.invoke(
        app,
        ["calculate", "--birth", "1990-06-15T08:30:00", "--time-basis", "invalid"],
    )
    assert result.exit_code == 2
    assert "Invalid value for '--time-basis'" in unstyle(result.output)
    assert "Traceback" not in result.output


def test_calculate_command_requires_longitude_for_solar_time() -> None:
    result = runner.invoke(
        app,
        [
            "calculate",
            "--birth",
            "1990-06-15T08:30:00",
            "--time-basis",
            "apparent_solar",
        ],
    )
    assert result.exit_code == 2
    assert "longitude is required" in result.output
    assert "Traceback" not in result.output


def test_calculation_commands_reject_non_finite_longitude() -> None:
    shared = ["--birth", "1990-06-15T08:30:00", "--longitude", "nan"]
    commands = (
        ["calculate", *shared],
        [
            "luck",
            *shared,
            "--annual-year",
            "2026",
            "--monthly-year",
            "2026",
            "--monthly-month",
            "8",
        ],
    )

    for command in commands:
        result = runner.invoke(app, command)
        assert result.exit_code == 2
        assert "longitude must be a finite number" in result.output
        assert "Traceback" not in result.output


def test_calculation_commands_reject_unsupported_lunar_date_without_traceback() -> None:
    shared = ["--birth", "0999-01-01T08:30:00", "--calendar", "lunar"]
    commands = (
        ["calculate", *shared],
        [
            "luck",
            *shared,
            "--annual-year",
            "2026",
            "--monthly-year",
            "2026",
            "--monthly-month",
            "8",
        ],
    )

    for command in commands:
        result = runner.invoke(app, command)
        assert result.exit_code == 2
        assert "outside the supported Korean calendar range" in result.output
        assert "Traceback" not in result.output


def test_luck_command_prints_daewoon_annual_and_monthly() -> None:
    result = runner.invoke(
        app,
        [
            "luck",
            "--birth",
            "1990-06-15T08:30:00",
            "--annual-year",
            "2026",
            "--monthly-year",
            "2026",
            "--monthly-month",
            "8",
            "--gender",
            "female",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["annual"]["pillar"]["hanja"] == "丙午"
    assert payload["monthly"]["pillar"]["hanja"] == "丙申"


def test_prompts_command_lists_versioned_hashes() -> None:
    result = runner.invoke(app, ["prompts"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["natal_analysis"]["version"] == "1.0.0"
    assert len(payload["llm_judge"]["sha256"]) == 64
