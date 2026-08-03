from __future__ import annotations

from datetime import date, datetime, timedelta

from .calendar import interactions_between, jie_terms, make_pillar, sexagenary_index
from .models import (
    Chart,
    DaewoonResult,
    DaewoonScenario,
    Gender,
    Interaction,
    LuckPeriod,
    LuckSnapshot,
)


def _natal_pillars(chart: Chart) -> list:
    return [chart.year, chart.month, chart.day, *([chart.hour] if chart.hour is not None else [])]


def _luck_interactions(chart: Chart, luck_pillar) -> list[Interaction]:
    result: list[Interaction] = []
    for natal in _natal_pillars(chart):
        result.extend(interactions_between([natal, luck_pillar]))
    return result


def _direction(chart: Chart, gender: Gender) -> str:
    year_stem_is_yang = chart.year.stem_index % 2 == 0
    forward = (gender is Gender.MALE and year_stem_is_yang) or (
        gender is Gender.FEMALE and not year_stem_is_yang
    )
    return "forward" if forward else "reverse"


def _start_age(chart: Chart, direction: str) -> float:
    boundary = chart.next_jie.occurs_at if direction == "forward" else chart.current_jie.occurs_at
    days = abs((boundary - chart.normalized_birth).total_seconds()) / 86400.0
    return round(days / 3.0, 2)


def _scenario(chart: Chart, direction: str, count: int) -> DaewoonScenario:
    start_age = _start_age(chart, direction)
    sign = 1 if direction == "forward" else -1
    first_start = chart.normalized_birth.date() + timedelta(days=round(start_age * 365.2425))
    periods: list[LuckPeriod] = []
    for offset in range(count):
        pillar = make_pillar(
            chart.month.sexagenary_index + sign * (offset + 1),
            chart.day.stem_index,
        )
        starts_at = first_start + timedelta(days=round(offset * 10 * 365.2425))
        ends_at = first_start + timedelta(days=round((offset + 1) * 10 * 365.2425) - 1)
        periods.append(
            LuckPeriod(
                sequence=offset + 1,
                direction=direction,
                pillar=pillar,
                start_age=round(start_age + offset * 10, 2),
                end_age=round(start_age + (offset + 1) * 10, 2),
                starts_at=starts_at,
                ends_at=ends_at,
                interactions=_luck_interactions(chart, pillar),
            )
        )
    return DaewoonScenario(
        label="순행" if direction == "forward" else "역행",
        direction=direction,
        start_age=start_age,
        periods=periods,
    )


def calculate_daewoon(chart: Chart, gender: Gender, count: int = 8) -> DaewoonResult:
    if count < 1 or count > 12:
        raise ValueError("count must be between 1 and 12")
    if gender is Gender.UNSPECIFIED:
        warning = "성별 정보가 없어 대운 방향을 확정하지 않고 순행과 역행을 모두 제공합니다."
        forward = _scenario(chart, "forward", count)
        reverse = _scenario(chart, "reverse", count)
        forward.warning = warning
        reverse.warning = warning
        return DaewoonResult(scenarios=[forward, reverse])
    return DaewoonResult(scenarios=[_scenario(chart, _direction(chart, gender), count)])


def calculate_annual_luck(chart: Chart, year: int) -> LuckSnapshot:
    zone = chart.normalized_birth.tzinfo
    if zone is None:
        raise ValueError("chart birth must be timezone-aware")
    starts = jie_terms(year, chart.timezone)[1].occurs_at
    ends = jie_terms(year + 1, chart.timezone)[1].occurs_at
    pillar = make_pillar((year - 1984) % 60, chart.day.stem_index)
    return LuckSnapshot(
        label=f"{year}년 세운",
        starts_at=starts,
        ends_at=ends,
        pillar=pillar,
        interactions=_luck_interactions(chart, pillar),
    )


def calculate_monthly_luck(chart: Chart, year: int, month: int) -> LuckSnapshot:
    if month < 1 or month > 12:
        raise ValueError("month must be between 1 and 12")
    current_terms = jie_terms(year, chart.timezone)
    starts = next(term for term in current_terms if term.occurs_at.month == month)
    candidates = sorted(
        [*current_terms, *jie_terms(year + 1, chart.timezone)],
        key=lambda term: term.occurs_at,
    )
    ends = min(term for term in candidates if term.occurs_at > starts.occurs_at)
    annual_index = (year - 1984) % 60
    annual_stem = annual_index % 10
    branch = starts.month_branch_index
    offset = (branch - 2) % 12
    stem = (annual_stem * 2 + 2 + offset) % 10
    pillar = make_pillar(sexagenary_index(stem, branch), chart.day.stem_index)
    warnings: list[str] = []
    return LuckSnapshot(
        label=f"{year}년 {month}월 월운",
        starts_at=starts.occurs_at,
        ends_at=ends.occurs_at,
        pillar=pillar,
        interactions=_luck_interactions(chart, pillar),
        boundary_warnings=warnings,
    )


def current_period(periods: list[LuckPeriod], on_date: date | None = None) -> LuckPeriod | None:
    target = on_date or date.today()
    return next((period for period in periods if period.starts_at <= target <= period.ends_at), None)
