"""Calculate deterministic Korean Four Pillars charts and solar-term boundaries."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import UTC, date, datetime, timedelta
from functools import lru_cache
from itertools import combinations
from zoneinfo import ZoneInfo

from .constants import (
    BRANCH_COMBINES,
    BRANCH_ELEMENT,
    BRANCH_HARMS,
    BRANCHES_HANJA,
    BRANCHES_KO,
    BRANCH_CLASHES,
    ELEMENTS,
    GROWTH_STAGES,
    GROWTH_START_BRANCH,
    HIDDEN_STEMS,
    JIE_TERMS,
    STEM_COMBINES,
    STEM_ELEMENT,
    STEM_CLASHES,
    STEMS_HANJA,
    STEMS_KO,
    TEN_GODS_KO,
)
from .models import BirthInput, CalendarKind, Chart, Interaction, Pillar, SolarTerm, TimeBasis

CALCULATION_VERSION = "calendar-1.0.0"


def _julian_date(moment: datetime) -> float:
    if moment.tzinfo is None:
        raise ValueError("Julian date requires a timezone-aware datetime")
    return moment.astimezone(UTC).timestamp() / 86400.0 + 2440587.5


def _julian_day_number(value: date) -> int:
    a = (14 - value.month) // 12
    y = value.year + 4800 - a
    m = value.month + 12 * a - 3
    return (
        value.day
        + (153 * m + 2) // 5
        + 365 * y
        + y // 4
        - y // 100
        + y // 400
        - 32045
    )


def _normalize_angle(value: float) -> float:
    return value % 360.0


def _angle_delta(longitude: float, target: float) -> float:
    return (longitude - target + 180.0) % 360.0 - 180.0


def apparent_solar_longitude(moment: datetime) -> float:
    """Return the Sun's apparent geocentric ecliptic longitude in degrees.

    This is the compact Meeus/NOAA series. Around modern solar-term boundaries its
    error is normally much smaller than the six-hour warning window used by this
    service. The algorithm is deterministic and does not require a remote ephemeris.
    """
    jd = _julian_date(moment)
    t = (jd - 2451545.0) / 36525.0
    mean_longitude = _normalize_angle(280.46646 + 36000.76983 * t + 0.0003032 * t * t)
    mean_anomaly = math.radians(
        _normalize_angle(357.52911 + 35999.05029 * t - 0.0001537 * t * t)
    )
    equation = (
        (1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(mean_anomaly)
        + (0.019993 - 0.000101 * t) * math.sin(2 * mean_anomaly)
        + 0.000289 * math.sin(3 * mean_anomaly)
    )
    true_longitude = mean_longitude + equation
    omega = math.radians(125.04 - 1934.136 * t)
    return _normalize_angle(true_longitude - 0.00569 - 0.00478 * math.sin(omega))


@lru_cache(maxsize=1024)
def solar_term_utc(year: int, longitude: float) -> datetime:
    """Locate one supported month-changing solar term in UTC by bisection."""
    spec = next((item for item in JIE_TERMS if item[2] == longitude), None)
    if spec is None:
        raise ValueError(f"Unsupported month-changing solar longitude: {longitude}")
    _, _, _, month, approximate_day, _ = spec
    center = datetime(year, month, approximate_day, 12, tzinfo=UTC)
    lower = center - timedelta(days=6)
    upper = center + timedelta(days=6)
    lower_delta = _angle_delta(apparent_solar_longitude(lower), longitude)
    upper_delta = _angle_delta(apparent_solar_longitude(upper), longitude)
    if not (lower_delta <= 0 <= upper_delta):
        raise RuntimeError(f"Solar term root was not bracketed for {year=} {longitude=}")
    for _ in range(64):
        midpoint = lower + (upper - lower) / 2
        if _angle_delta(apparent_solar_longitude(midpoint), longitude) < 0:
            lower = midpoint
        else:
            upper = midpoint
    return lower + (upper - lower) / 2


def jie_terms(year: int, timezone: str) -> list[SolarTerm]:
    """Return all twelve month-changing solar terms in an IANA time zone."""
    zone = ZoneInfo(timezone)
    return [
        SolarTerm(
            name_ko=name_ko,
            name_hanja=name_hanja,
            longitude=longitude,
            occurs_at=solar_term_utc(year, longitude).astimezone(zone),
            month_branch_index=branch,
        )
        for name_ko, name_hanja, longitude, _, _, branch in JIE_TERMS
    ]


def _surrounding_terms(moment: datetime) -> list[SolarTerm]:
    terms: list[SolarTerm] = []
    for year in (moment.year - 1, moment.year, moment.year + 1):
        terms.extend(jie_terms(year, str(moment.tzinfo)))
    return sorted(terms, key=lambda term: term.occurs_at)


def _convert_lunar_to_solar(value: BirthInput) -> datetime:
    try:
        from korean_lunar_calendar import KoreanLunarCalendar
    except ImportError as exc:  # pragma: no cover - dependency is declared
        raise RuntimeError("korean-lunar-calendar is required for lunar input") from exc
    calendar = KoreanLunarCalendar()
    accepted = calendar.setLunarDate(
        value.birth.year,
        value.birth.month,
        value.birth.day,
        value.lunar_leap_month,
    )
    if not accepted:
        raise ValueError("The lunar date is outside the supported Korean calendar range")
    solar = date.fromisoformat(calendar.SolarIsoFormat())
    return datetime(
        solar.year,
        solar.month,
        solar.day,
        value.birth.hour,
        value.birth.minute,
        value.birth.second,
        value.birth.microsecond,
    )


def _equation_of_time_minutes(moment: datetime) -> float:
    day_number = moment.timetuple().tm_yday
    b = 2.0 * math.pi * (day_number - 81) / 364.0
    return 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)


def normalize_birth(value: BirthInput) -> datetime:
    """Convert validated birth input into the effective timezone-aware birth moment."""
    wall_clock = (
        _convert_lunar_to_solar(value)
        if value.calendar is CalendarKind.LUNAR
        else value.birth
    )
    zone = ZoneInfo(value.timezone)
    localized = wall_clock.replace(tzinfo=zone)
    if value.time_basis is TimeBasis.CIVIL:
        return localized
    if value.longitude is None:
        raise ValueError("longitude is required for mean or apparent solar time")
    offset = localized.utcoffset()
    if offset is None:
        raise ValueError("The selected timezone has no UTC offset at the birth moment")
    standard_meridian = offset.total_seconds() / 3600.0 * 15.0
    correction_minutes = 4.0 * (value.longitude - standard_meridian)
    if value.time_basis is TimeBasis.APPARENT_SOLAR:
        correction_minutes += _equation_of_time_minutes(localized)
    return localized + timedelta(minutes=correction_minutes)


def sexagenary_index(stem_index: int, branch_index: int) -> int:
    """Return the unique sexagenary-cycle index for a compatible stem and branch."""
    for index in range(60):
        if index % 10 == stem_index and index % 12 == branch_index:
            return index
    raise ValueError("Stem and branch parity cannot form a sexagenary pillar")


def ten_god(day_stem: int, target_stem: int) -> str:
    """Return the Korean Ten God relationship from a day stem to a target stem."""
    day_element = STEM_ELEMENT[day_stem]
    target_element = STEM_ELEMENT[target_stem]
    day_element_index = ELEMENTS.index(day_element)
    target_element_index = ELEMENTS.index(target_element)
    same_polarity = day_stem % 2 == target_stem % 2
    if day_element_index == target_element_index:
        key = "peer" if same_polarity else "rob_wealth"
    elif (day_element_index + 1) % 5 == target_element_index:
        key = "eating_god" if same_polarity else "hurting_officer"
    elif (day_element_index + 2) % 5 == target_element_index:
        key = "indirect_wealth" if same_polarity else "direct_wealth"
    elif (target_element_index + 1) % 5 == day_element_index:
        key = "indirect_resource" if same_polarity else "direct_resource"
    else:
        key = "seven_killings" if same_polarity else "direct_officer"
    return TEN_GODS_KO[key]


def growth_stage(day_stem: int, branch_index: int) -> str:
    """Return the Twelve Growth Stage for a day stem at one earthly branch."""
    start = GROWTH_START_BRANCH[day_stem]
    offset = (branch_index - start) % 12 if day_stem % 2 == 0 else (start - branch_index) % 12
    return GROWTH_STAGES[offset]


def make_pillar(index: int, day_master_stem: int | None = None) -> Pillar:
    """Build one immutable pillar with hidden stems and optional day-master relations."""
    index %= 60
    stem_index = index % 10
    branch_index = index % 12
    hidden_indexes = HIDDEN_STEMS[branch_index]
    return Pillar(
        stem_index=stem_index,
        branch_index=branch_index,
        stem=STEMS_HANJA[stem_index],
        branch=BRANCHES_HANJA[branch_index],
        korean=STEMS_KO[stem_index] + BRANCHES_KO[branch_index],
        hanja=STEMS_HANJA[stem_index] + BRANCHES_HANJA[branch_index],
        sexagenary_index=index,
        ten_god=ten_god(day_master_stem, stem_index) if day_master_stem is not None else None,
        hidden_stems=tuple(STEMS_HANJA[item] for item in hidden_indexes),
        hidden_ten_gods=(
            tuple(ten_god(day_master_stem, item) for item in hidden_indexes)
            if day_master_stem is not None
            else ()
        ),
        growth_stage=(growth_stage(day_master_stem, branch_index) if day_master_stem is not None else None),
    )


def _interaction(kind: str, left: Pillar, right: Pillar) -> Interaction:
    labels = {
        "stem_combine": "천간합",
        "stem_clash": "천간충",
        "branch_combine": "지지육합",
        "branch_clash": "지지충",
        "branch_harm": "지지해",
    }
    return Interaction(
        kind=kind,  # type: ignore[arg-type]
        left=left.hanja,
        right=right.hanja,
        description=f"{left.hanja}와 {right.hanja} 사이에 {labels[kind]}이 성립합니다.",
    )


def interactions_between(pillars: list[Pillar]) -> list[Interaction]:
    """Return supported stem and branch interactions among the supplied pillars."""
    result: list[Interaction] = []
    for left, right in combinations(pillars, 2):
        stem_pair = frozenset((left.stem_index, right.stem_index))
        branch_pair = frozenset((left.branch_index, right.branch_index))
        if stem_pair in STEM_COMBINES:
            result.append(_interaction("stem_combine", left, right))
        if stem_pair in STEM_CLASHES:
            result.append(_interaction("stem_clash", left, right))
        if branch_pair in BRANCH_COMBINES:
            result.append(_interaction("branch_combine", left, right))
        if branch_pair in BRANCH_CLASHES:
            result.append(_interaction("branch_clash", left, right))
        if branch_pair in BRANCH_HARMS:
            result.append(_interaction("branch_harm", left, right))
    return result


def _element_balance(pillars: list[Pillar]) -> dict[str, float]:
    balance = dict.fromkeys(ELEMENTS, 0.0)
    hidden_weights = (0.45, 0.25, 0.15)
    for pillar in pillars:
        balance[STEM_ELEMENT[pillar.stem_index]] += 1.0
        balance[BRANCH_ELEMENT[pillar.branch_index]] += 0.8
        for weight, hidden in zip(hidden_weights, HIDDEN_STEMS[pillar.branch_index], strict=False):
            balance[STEM_ELEMENT[hidden]] += weight
    return {key: round(value, 2) for key, value in balance.items()}


def _year_index(moment: datetime) -> tuple[int, SolarTerm]:
    lichun = jie_terms(moment.year, str(moment.tzinfo))[1]
    pillar_year = moment.year if moment >= lichun.occurs_at else moment.year - 1
    return (pillar_year - 1984) % 60, lichun


def _month_index(moment: datetime, year_stem: int) -> tuple[int, SolarTerm, SolarTerm]:
    terms = _surrounding_terms(moment)
    previous = max(
        (term for term in terms if term.occurs_at <= moment),
        key=lambda term: term.occurs_at,
    )
    following = min(
        (term for term in terms if term.occurs_at > moment),
        key=lambda term: term.occurs_at,
    )
    offset = (previous.month_branch_index - 2) % 12
    stem_index = (year_stem * 2 + 2 + offset) % 10
    return sexagenary_index(stem_index, previous.month_branch_index), previous, following


def _day_index(moment: datetime, late_zi: bool) -> int:
    day = moment.date()
    if late_zi and moment.hour >= 23:
        day += timedelta(days=1)
    return (_julian_day_number(day) + 49) % 60


def _hour_index(moment: datetime, day_stem: int) -> int:
    branch_index = ((moment.hour + 1) // 2) % 12
    stem_index = ((day_stem % 5) * 2 + branch_index) % 10
    return sexagenary_index(stem_index, branch_index)


def calculate_chart(value: BirthInput) -> Chart:
    """Calculate one immutable chart, warnings, interactions, and evidence fingerprint."""
    moment = normalize_birth(value)
    year_index, lichun = _year_index(moment)
    month_index, current_jie, next_jie = _month_index(moment, year_index % 10)
    day_index = _day_index(moment, value.day_boundary.value == "late_zi")
    day_stem = day_index % 10

    year = make_pillar(year_index, day_stem)
    month = make_pillar(month_index, day_stem)
    day = make_pillar(day_index, day_stem)
    hour = make_pillar(_hour_index(moment, day_stem), day_stem) if value.birth_time_known else None
    pillars = [year, month, day, *([hour] if hour is not None else [])]

    warnings: list[str] = []
    for label, boundary in (("입춘", lichun.occurs_at), (current_jie.name_ko, current_jie.occurs_at), (next_jie.name_ko, next_jie.occurs_at)):
        distance = abs((moment - boundary).total_seconds())
        if distance <= 6 * 3600:
            warnings.append(
                f"출생 시각이 {label} 경계에서 6시간 이내입니다. 원자료의 시각과 시간대 설정을 다시 확인하십시오."
            )
    if not value.birth_time_known:
        warnings.append("출생 시각이 없어 시주는 확정하지 않았습니다.")

    raw = {
        "normalized_birth": moment.isoformat(),
        "timezone": value.timezone,
        "calendar_input": value.calendar.value,
        "time_basis": value.time_basis.value,
        "day_boundary": value.day_boundary.value,
        "birth_time_known": value.birth_time_known,
        "pillars": [pillar.hanja for pillar in pillars],
        "current_jie": current_jie.model_dump(mode="json"),
        "next_jie": next_jie.model_dump(mode="json"),
        "version": CALCULATION_VERSION,
    }
    fingerprint = hashlib.sha256(
        json.dumps(raw, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    return Chart(
        normalized_birth=moment,
        timezone=value.timezone,
        calendar_input=value.calendar,
        time_basis=value.time_basis,
        day_boundary=value.day_boundary,
        birth_time_known=value.birth_time_known,
        year=year,
        month=month,
        day=day,
        hour=hour,
        day_master=day.stem,
        element_balance=_element_balance(pillars),
        interactions=interactions_between(pillars),
        current_jie=current_jie,
        next_jie=next_jie,
        boundary_warnings=warnings,
        calculation_version=CALCULATION_VERSION,
        fingerprint=fingerprint,
    )
