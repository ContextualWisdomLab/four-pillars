"""Calculate apparent solar longitude with a compact VSOP87 Earth series.

The implementation keeps the deterministic calendar core offline while improving
modern solar-term timing. It evaluates a bounded subset of the published VSOP87
Earth series in Terrestrial Time, then applies FK5, nutation, and aberration
corrections for apparent geocentric ecliptic longitude.
"""

from __future__ import annotations

import math
from bisect import bisect_right
from datetime import UTC, datetime

SeriesTerm = tuple[float, float, float]
SeriesOrder = tuple[SeriesTerm, ...]
Series = tuple[SeriesOrder, ...]

# Effective UTC instants and TAI-UTC values. Before 1972 the first value is a
# deliberate coarse approximation; released Korean golden fixtures are modern.
_LEAP_SECONDS: tuple[tuple[datetime, float], ...] = (
    (datetime(1, 1, 1, tzinfo=UTC), 10.0),
    (datetime(1972, 7, 1, tzinfo=UTC), 11.0),
    (datetime(1973, 1, 1, tzinfo=UTC), 12.0),
    (datetime(1974, 1, 1, tzinfo=UTC), 13.0),
    (datetime(1975, 1, 1, tzinfo=UTC), 14.0),
    (datetime(1976, 1, 1, tzinfo=UTC), 15.0),
    (datetime(1977, 1, 1, tzinfo=UTC), 16.0),
    (datetime(1978, 1, 1, tzinfo=UTC), 17.0),
    (datetime(1979, 1, 1, tzinfo=UTC), 18.0),
    (datetime(1980, 1, 1, tzinfo=UTC), 19.0),
    (datetime(1981, 7, 1, tzinfo=UTC), 20.0),
    (datetime(1982, 7, 1, tzinfo=UTC), 21.0),
    (datetime(1983, 7, 1, tzinfo=UTC), 22.0),
    (datetime(1985, 7, 1, tzinfo=UTC), 23.0),
    (datetime(1988, 1, 1, tzinfo=UTC), 24.0),
    (datetime(1990, 1, 1, tzinfo=UTC), 25.0),
    (datetime(1991, 1, 1, tzinfo=UTC), 26.0),
    (datetime(1992, 7, 1, tzinfo=UTC), 27.0),
    (datetime(1993, 7, 1, tzinfo=UTC), 28.0),
    (datetime(1994, 7, 1, tzinfo=UTC), 29.0),
    (datetime(1996, 1, 1, tzinfo=UTC), 30.0),
    (datetime(1997, 7, 1, tzinfo=UTC), 31.0),
    (datetime(1999, 1, 1, tzinfo=UTC), 32.0),
    (datetime(2006, 1, 1, tzinfo=UTC), 33.0),
    (datetime(2009, 1, 1, tzinfo=UTC), 34.0),
    (datetime(2012, 7, 1, tzinfo=UTC), 35.0),
    (datetime(2015, 7, 1, tzinfo=UTC), 36.0),
    (datetime(2017, 1, 1, tzinfo=UTC), 37.0),
)
_LEAP_SECOND_EFFECTIVE_UTC = tuple(item[0] for item in _LEAP_SECONDS)
_TAI_MINUS_UTC_SECONDS = tuple(item[1] for item in _LEAP_SECONDS)

_LONGITUDE: Series = (
    (
        (175347046, 0, 0),
        (3341656, 4.6692568, 6283.07585),
        (34894, 4.6261, 12566.1517),
        (3497, 2.7441, 5753.3849),
        (3418, 2.8289, 3.5231),
        (3136, 3.6277, 77713.7715),
        (2676, 4.4181, 7860.4194),
        (2343, 6.1352, 3930.2097),
        (1324, 0.7425, 11506.7698),
        (1273, 2.0371, 529.691),
        (1199, 1.1096, 1577.3435),
        (990, 5.233, 5884.927),
        (902, 2.045, 26.298),
        (857, 3.508, 398.149),
        (780, 1.179, 5223.694),
        (753, 2.533, 5507.553),
        (505, 4.583, 18849.228),
        (492, 4.205, 775.523),
        (357, 2.92, 0.067),
        (317, 5.849, 11790.629),
        (284, 1.899, 796.298),
        (271, 0.315, 10977.079),
        (243, 0.345, 5486.778),
        (206, 4.806, 2544.314),
        (205, 1.869, 5573.143),
        (202, 2.458, 6069.777),
        (156, 0.833, 213.299),
        (132, 3.411, 2942.463),
        (126, 1.083, 20.775),
        (115, 0.645, 0.98),
    ),
    (
        (628331966747, 0, 0),
        (206059, 2.678235, 6283.07585),
        (4303, 2.6351, 12566.1517),
        (425, 1.59, 3.523),
        (119, 5.796, 26.298),
        (109, 2.966, 1577.344),
        (93, 2.59, 18849.23),
        (72, 1.14, 529.69),
        (68, 1.87, 398.15),
        (67, 4.41, 5507.55),
        (59, 2.89, 5223.69),
        (56, 2.17, 155.42),
        (45, 0.4, 796.3),
        (36, 0.47, 775.52),
        (29, 2.65, 7.11),
    ),
    (
        (52919, 0, 0),
        (8720, 1.0721, 6283.0758),
        (309, 0.867, 12566.152),
        (27, 0.05, 3.52),
        (16, 5.19, 26.3),
        (16, 3.68, 155.42),
        (10, 0.76, 18849.23),
        (9, 2.06, 77713.77),
        (7, 0.83, 775.52),
        (5, 4.66, 1577.34),
    ),
    (
        (289, 5.844, 6283.076),
        (35, 0, 0),
        (17, 5.49, 12566.15),
        (3, 5.2, 155.42),
        (1, 4.72, 3.52),
    ),
    ((114, 3.142, 0), (8, 4.13, 6283.08), (1, 3.84, 12566.15)),
    ((1, 3.14, 0),),
)

_RADIUS: Series = (
    (
        (100013989, 0, 0),
        (1670700, 3.0984635, 6283.07585),
        (13956, 3.05525, 12566.1517),
        (3084, 5.1985, 77713.7715),
        (1628, 1.1739, 5753.3849),
        (1576, 2.8469, 7860.4194),
        (925, 5.453, 11506.77),
        (542, 4.564, 3930.21),
        (472, 3.661, 5884.927),
        (346, 0.964, 5507.553),
        (329, 5.9, 5223.694),
        (307, 0.299, 5573.143),
        (243, 4.273, 11790.629),
        (212, 5.847, 1577.344),
        (186, 5.022, 10977.079),
    ),
    (
        (103019, 1.10749, 6283.07585),
        (1721, 1.0644, 12566.1517),
        (702, 3.142, 0),
        (32, 1.02, 18849.23),
        (31, 2.84, 5507.55),
        (25, 1.32, 5223.69),
        (18, 1.42, 1577.34),
    ),
    (
        (4359, 5.7846, 6283.0758),
        (124, 5.579, 12566.152),
        (12, 3.14, 0),
        (9, 3.63, 77713.77),
    ),
    ((145, 4.273, 6283.076), (7, 3.92, 12566.15)),
    ((4, 2.56, 6283.08),),
)


def _series_value(terms: SeriesOrder, tau: float) -> float:
    """Evaluate one VSOP87 polynomial order at a Julian-millennia value."""

    return math.fsum(
        amplitude * math.cos(phase + frequency * tau)
        for amplitude, phase, frequency in terms
    )


def _vsop87_value(series: Series, tau: float) -> float:
    """Evaluate and scale all bounded orders in one VSOP87 coordinate."""

    return math.fsum(
        _series_value(order, tau) * tau**power
        for power, order in enumerate(series)
    ) / 100_000_000.0


def _tai_minus_utc_seconds(moment: datetime) -> float:
    """Return the tabled TAI-UTC offset effective at one aware UTC instant."""

    utc = moment.astimezone(UTC)
    index = bisect_right(_LEAP_SECOND_EFFECTIVE_UTC, utc) - 1
    return _TAI_MINUS_UTC_SECONDS[index]


def _julian_ephemeris_date(moment: datetime) -> float:
    """Convert one aware civil instant to Julian Ephemeris Date in TT."""

    utc = moment.astimezone(UTC)
    j2000_utc = datetime(2000, 1, 1, 12, tzinfo=UTC)
    julian_utc = 2451545.0 + (utc - j2000_utc).total_seconds() / 86400.0
    terrestrial_offset = _tai_minus_utc_seconds(utc) + 32.184
    return julian_utc + terrestrial_offset / 86400.0


def _nutation_longitude(julian_centuries: float) -> float:
    """Return the dominant nutation-in-longitude correction in degrees."""

    t = julian_centuries
    node = math.radians(
        125.04452 - 1934.136261 * t + 0.0020708 * t * t + t**3 / 450000.0
    )
    sun = math.radians(280.4665 + 36000.7698 * t)
    moon = math.radians(218.3165 + 481267.8813 * t)
    arcseconds = (
        -17.20 * math.sin(node)
        - 1.32 * math.sin(2.0 * sun)
        - 0.23 * math.sin(2.0 * moon)
        + 0.21 * math.sin(2.0 * node)
    )
    return arcseconds / 3600.0


def apparent_solar_longitude(moment: datetime) -> float:
    """Return apparent geocentric solar ecliptic longitude in degrees.

    Args:
        moment: A timezone-aware civil datetime. It is converted to UTC and then
            Terrestrial Time before evaluating the bounded VSOP87 Earth series.

    Returns:
        The apparent longitude in the half-open range ``[0, 360)``.

    Raises:
        ValueError: If ``moment`` has no timezone information.
    """

    if moment.tzinfo is None:
        raise ValueError("Solar longitude requires a timezone-aware datetime")
    julian_ephemeris_date = _julian_ephemeris_date(moment)
    tau = (julian_ephemeris_date - 2451545.0) / 365250.0
    heliocentric_longitude = math.degrees(_vsop87_value(_LONGITUDE, tau))
    earth_radius = _vsop87_value(_RADIUS, tau)
    geocentric_longitude = (heliocentric_longitude + 180.0) % 360.0
    fk5_correction = -0.09033 / 3600.0
    centuries = (julian_ephemeris_date - 2451545.0) / 36525.0
    nutation = _nutation_longitude(centuries)
    aberration = -(20.4898 / earth_radius) / 3600.0
    return (geocentric_longitude + fk5_correction + nutation + aberration) % 360.0
