from __future__ import annotations

import json

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
