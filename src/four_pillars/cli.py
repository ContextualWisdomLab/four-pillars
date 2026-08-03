from __future__ import annotations

import json
from datetime import datetime

import typer

from .calendar import calculate_chart
from .fortune import calculate_annual_luck, calculate_daewoon, calculate_monthly_luck
from .models import BirthInput, Gender
from .prompts import prompt_manifest

app = typer.Typer(no_args_is_help=True, help="Deterministic Four Pillars calculator and report utilities.")


def _dump(payload: object) -> None:
    if hasattr(payload, "model_dump"):
        payload = payload.model_dump(mode="json")
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


def _birth_input(birth: str, timezone: str, gender: str) -> BirthInput:
    return BirthInput(
        birth=datetime.fromisoformat(birth),
        timezone=timezone,
        gender=Gender(gender),
    )


@app.command()
def calculate(
    birth: str = typer.Option(..., help="Local wall-clock birth time in ISO-8601 format."),
    timezone: str = typer.Option("Asia/Seoul", help="IANA timezone name."),
    gender: str = typer.Option(Gender.UNSPECIFIED.value, help="male, female, or unspecified."),
) -> None:
    """Calculate the deterministic natal Four Pillars chart."""

    _dump(calculate_chart(_birth_input(birth, timezone, gender)))


@app.command()
def luck(
    birth: str = typer.Option(..., help="Local wall-clock birth time in ISO-8601 format."),
    timezone: str = typer.Option("Asia/Seoul", help="IANA timezone name."),
    gender: str = typer.Option(Gender.UNSPECIFIED.value, help="male, female, or unspecified."),
    annual_year: int = typer.Option(..., min=1600, max=2400),
    monthly_year: int = typer.Option(..., min=1600, max=2400),
    monthly_month: int = typer.Option(..., min=1, max=12),
    daewoon_count: int = typer.Option(8, min=1, max=12),
) -> None:
    """Calculate daewoon, annual luck, and one solar-term month."""

    birth_input = _birth_input(birth, timezone, gender)
    chart = calculate_chart(birth_input)
    payload = {
        "daewoon": calculate_daewoon(chart, birth_input.gender, count=daewoon_count).model_dump(mode="json"),
        "annual": calculate_annual_luck(chart, annual_year).model_dump(mode="json"),
        "monthly": calculate_monthly_luck(chart, monthly_year, monthly_month).model_dump(mode="json"),
    }
    _dump(payload)


@app.command()
def prompts() -> None:
    """List prompt versions and immutable SHA-256 digests."""

    _dump(prompt_manifest())
