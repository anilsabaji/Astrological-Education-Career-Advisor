"""
Core astronomical engine built on the Swiss Ephemeris (pyswisseph).

It produces a :class:`Chart` that carries everything the KP and Parashara
analysers need:

* sidereal planetary longitudes (using the Moshier ephemeris -> no data files)
* sign, nakshatra, pada
* KP star-lord / sub-lord / sub-sub-lord for every planet and house cusp
* house placement (Placidus cusps for KP, whole-sign for Parashara)

Two ayanamsas are supported:
* KP / Krishnamurti  -> used for the KP chart
* Lahiri             -> used for the Parashara chart
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Optional

import swisseph as swe

from . import constants as C

# Moshier ephemeris needs no external data files and is accurate to well
# under an arc-minute for the grahas across the supported date range.
_CALC_FLAGS = swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

NAK_SPAN = 360.0 / 27.0          # 13 deg 20 min
PADA_SPAN = NAK_SPAN / 4.0       # 3 deg 20 min

_SWE_PLANET = {
    C.SUN: swe.SUN,
    C.MOON: swe.MOON,
    C.MARS: swe.MARS,
    C.MERCURY: swe.MERCURY,
    C.JUPITER: swe.JUPITER,
    C.VENUS: swe.VENUS,
    C.SATURN: swe.SATURN,
    # Rahu = true north node; Ketu = 180 deg opposite.
    C.RAHU: swe.TRUE_NODE,
}


def norm360(x: float) -> float:
    """Normalise an angle into [0, 360)."""
    return x % 360.0


# ---------------------------------------------------------------------------
# KP sub-lord machinery (Vimshottari proportional division)
# ---------------------------------------------------------------------------
def _subdivide(offset: float, length: float, start_lord: str):
    """
    Divide a span of ``length`` degrees into 9 unequal parts using the
    Vimshottari proportions, beginning the sequence at ``start_lord``.

    Returns ``(lord, part_start_offset, part_length)`` for the part that
    contains ``offset`` (measured from the start of the span).
    """
    start_idx = C.VIMSHOTTARI_ORDER.index(start_lord)
    cursor = 0.0
    for i in range(9):
        lord = C.VIMSHOTTARI_ORDER[(start_idx + i) % 9]
        part_len = length * C.VIMSHOTTARI_YEARS[lord] / C.TOTAL_VIMSHOTTARI_YEARS
        if offset < cursor + part_len or i == 8:
            return lord, cursor, part_len
        cursor += part_len
    # Should never reach here.
    return start_lord, 0.0, length


@dataclass
class Lordship:
    """Star-lord / sub-lord / sub-sub-lord chain for a longitude."""
    sign: str
    sign_lord: str
    nakshatra: str
    nak_index: int
    pada: int
    star_lord: str       # nakshatra lord
    sub_lord: str
    sub_sub_lord: str


def lordships(longitude: float) -> Lordship:
    """Compute the full KP lordship chain for an absolute sidereal longitude."""
    lon = norm360(longitude)
    sign_index = int(lon // 30)
    sign = C.SIGNS[sign_index]
    sign_lord = C.SIGN_LORD[sign]

    nak_index = int(lon // NAK_SPAN)
    nakshatra = C.NAKSHATRAS[nak_index]
    star_lord = C.NAKSHATRA_LORDS[nak_index]

    nak_offset = lon - nak_index * NAK_SPAN
    pada = int(nak_offset // PADA_SPAN) + 1

    # Sub-lord: divide the nakshatra span.
    sub_lord, sub_start, sub_len = _subdivide(nak_offset, NAK_SPAN, star_lord)
    # Sub-sub-lord: divide the sub span.
    sub_offset = nak_offset - sub_start
    sub_sub_lord, _, _ = _subdivide(sub_offset, sub_len, sub_lord)

    return Lordship(
        sign=sign, sign_lord=sign_lord, nakshatra=nakshatra,
        nak_index=nak_index, pada=pada, star_lord=star_lord,
        sub_lord=sub_lord, sub_sub_lord=sub_sub_lord,
    )


# ---------------------------------------------------------------------------
# Planet & chart data structures
# ---------------------------------------------------------------------------
@dataclass
class PlanetPos:
    name: str
    longitude: float          # sidereal absolute degrees
    sign: str
    sign_index: int
    degree_in_sign: float
    retrograde: bool
    house: int                # bhava occupied
    lordship: Lordship

    @property
    def short(self) -> str:
        return C.PLANET_SHORT[self.name]


@dataclass
class HouseCusp:
    number: int
    longitude: float
    sign: str
    lordship: Lordship


@dataclass
class Chart:
    system: str                       # "KP" or "Parashara"
    when_local: dt.datetime
    when_utc: dt.datetime
    latitude: float
    longitude: float
    timezone: float
    ayanamsa: float
    ascendant: float
    asc_lordship: Lordship
    planets: dict                     # name -> PlanetPos
    cusps: list                       # list[HouseCusp] (index 0 == house 1)
    house_signs: list = field(default_factory=list)  # sign of each house 1..12

    # -- convenience lookups -------------------------------------------------
    def planets_in_house(self, house: int):
        return [p for p in self.planets.values() if p.house == house]

    def house_of_sign(self, sign: str) -> int:
        return self.house_signs.index(sign) + 1

    def sign_of_house(self, house: int) -> str:
        return self.house_signs[house - 1]

    def lord_of_house(self, house: int) -> str:
        return C.SIGN_LORD[self.sign_of_house(house)]

    def house_of_planet(self, planet: str) -> int:
        return self.planets[planet].house


# ---------------------------------------------------------------------------
# Chart computation
# ---------------------------------------------------------------------------
def _to_utc(local: dt.datetime, tz_offset_hours: float) -> dt.datetime:
    return local - dt.timedelta(hours=tz_offset_hours)


def _julian_day(utc: dt.datetime) -> float:
    hour = utc.hour + utc.minute / 60.0 + utc.second / 3600.0
    return swe.julday(utc.year, utc.month, utc.day, hour, swe.GREG_CAL)


def _whole_sign_house(planet_sign_index: int, asc_sign_index: int) -> int:
    return (planet_sign_index - asc_sign_index) % 12 + 1


def _placidus_house(longitude: float, cusps) -> int:
    """Determine the house for a longitude given 12 Placidus cusps."""
    lon = norm360(longitude)
    for i in range(12):
        start = norm360(cusps[i])
        end = norm360(cusps[(i + 1) % 12])
        span = norm360(end - start)
        if span == 0:
            span = 360.0
        if norm360(lon - start) < span:
            return i + 1
    return 1


def compute_chart(
    local_dt: dt.datetime,
    latitude: float,
    longitude: float,
    tz_offset_hours: float,
    system: str = "KP",
) -> Chart:
    """
    Build a :class:`Chart`.

    ``system`` selects the ayanamsa and the house system:
      * "KP"        -> Krishnamurti ayanamsa + Placidus cusps
      * "Parashara" -> Lahiri ayanamsa + whole-sign houses
    """
    utc = _to_utc(local_dt, tz_offset_hours)
    jd = _julian_day(utc)

    if system == "KP":
        swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    else:
        swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)

    # Ascendant + cusps (Placidus, sidereal).
    cusps_raw, ascmc = swe.houses_ex(jd, latitude, longitude, b"P", swe.FLG_SIDEREAL)
    ascendant = norm360(ascmc[0])
    asc_sign_index = int(ascendant // 30)

    # House cusps & their lordships (KP uses Placidus cusps explicitly).
    cusps: list[HouseCusp] = []
    if system == "KP":
        for i in range(12):
            clon = norm360(cusps_raw[i])
            cusps.append(HouseCusp(
                number=i + 1, longitude=clon,
                sign=C.SIGNS[int(clon // 30)], lordship=lordships(clon),
            ))
        house_signs = [c.sign for c in cusps]
    else:
        # Whole-sign: house N == the Nth sign starting from the ascendant sign.
        house_signs = [C.SIGNS[(asc_sign_index + i) % 12] for i in range(12)]
        for i in range(12):
            # Represent each whole-sign house cusp at the 0 deg of its sign.
            clon = ((asc_sign_index + i) % 12) * 30.0
            cusps.append(HouseCusp(
                number=i + 1, longitude=clon,
                sign=house_signs[i], lordship=lordships(clon),
            ))

    # Planets.
    planets: dict[str, PlanetPos] = {}
    for name in C.PLANETS:
        if name == C.KETU:
            rahu_lon = planets[C.RAHU].longitude
            lon = norm360(rahu_lon + 180.0)
            retro = True   # nodes are always retrograde
        else:
            res = swe.calc_ut(jd, _SWE_PLANET[name], _CALC_FLAGS)
            lon = norm360(res[0][0])
            speed = res[0][3]
            retro = speed < 0
            if name == C.RAHU:
                retro = True

        sign_index = int(lon // 30)
        if system == "KP":
            house = _placidus_house(lon, [c.longitude for c in cusps])
        else:
            house = _whole_sign_house(sign_index, asc_sign_index)

        planets[name] = PlanetPos(
            name=name, longitude=lon, sign=C.SIGNS[sign_index],
            sign_index=sign_index, degree_in_sign=lon - sign_index * 30,
            retrograde=retro, house=house, lordship=lordships(lon),
        )

    return Chart(
        system=system, when_local=local_dt, when_utc=utc,
        latitude=latitude, longitude=longitude, timezone=tz_offset_hours,
        ayanamsa=ayanamsa, ascendant=ascendant,
        asc_lordship=lordships(ascendant), planets=planets,
        cusps=cusps, house_signs=house_signs,
    )
