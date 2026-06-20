"""
Transit (Gochar) triggers.

Dashas tell us *when a result is promised*; transits confirm *when it actually
matures*. This module looks at the slow planets - Jupiter, Saturn, Rahu and
Ketu - and reports:

* which natal house each is transiting (relative to the natal ascendant and to
  the natal Moon),
* the classic "double transit" of Jupiter + Saturn over the houses that matter
  for education (4, 9) and career (10, 6, 11),
* the Sade-Sati status of Saturn relative to the natal Moon.

These act as confirming triggers for the dasha windows produced by the FAQ
engine.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Dict, List

from . import constants as C
from .ephemeris import Chart, compute_chart

SLOW = [C.JUPITER, C.SATURN, C.RAHU, C.KETU]

# Vedic special aspects (houses counted from the planet, 1 = same house).
ASPECTS = {
    C.JUPITER: [5, 7, 9],
    C.SATURN: [3, 7, 10],
    C.MARS: [4, 7, 8],
    C.RAHU: [5, 7, 9],
    C.KETU: [5, 7, 9],
}


@dataclass
class TransitPos:
    planet: str
    sign: str
    house_from_lagna: int
    house_from_moon: int
    influences_from_lagna: List[int]   # houses occupied + aspected (from Lagna)


@dataclass
class TransitReport:
    as_of: dt.date
    positions: Dict[str, TransitPos]
    sade_sati: str
    education_trigger: str
    career_trigger: str
    notes: List[str]


def _house_from(sign_index: int, ref_sign_index: int) -> int:
    return (sign_index - ref_sign_index) % 12 + 1


def _influenced_houses(house_occupied: int, planet: str) -> List[int]:
    out = {house_occupied}
    for asp in ASPECTS.get(planet, []):
        out.add((house_occupied - 1 + (asp - 1)) % 12 + 1)
    return sorted(out)


def transit_positions(natal_par: Chart, now: dt.datetime) -> Dict[str, TransitPos]:
    """Current sidereal (Lahiri) positions mapped onto natal houses."""
    tr = compute_chart(now, natal_par.latitude, natal_par.longitude,
                       natal_par.timezone, system="Parashara")
    asc_idx = int(natal_par.ascendant // 30)
    moon_idx = natal_par.planets[C.MOON].sign_index

    positions: Dict[str, TransitPos] = {}
    for planet in SLOW:
        p = tr.planets[planet]
        h_lagna = _house_from(p.sign_index, asc_idx)
        h_moon = _house_from(p.sign_index, moon_idx)
        positions[planet] = TransitPos(
            planet=planet, sign=p.sign,
            house_from_lagna=h_lagna, house_from_moon=h_moon,
            influences_from_lagna=_influenced_houses(h_lagna, planet),
        )
    return positions


def _double_transit(positions: Dict[str, TransitPos], houses: List[int]) -> List[int]:
    """Houses influenced (occupied or aspected) by BOTH Jupiter and Saturn."""
    ju = set(positions[C.JUPITER].influences_from_lagna)
    sa = set(positions[C.SATURN].influences_from_lagna)
    both = ju & sa
    return sorted(h for h in houses if h in both)


def _sade_sati(positions: Dict[str, TransitPos]) -> str:
    """Saturn over the 12th, 1st or 2nd from the natal Moon = Sade Sati."""
    h = positions[C.SATURN].house_from_moon
    if h == 12:
        return "Sade Sati - first (rising) phase is active."
    if h == 1:
        return "Sade Sati - peak (janma) phase is active."
    if h == 2:
        return "Sade Sati - last (setting) phase is active."
    if h == 4:
        return "Saturn's Ardha-ashtama (half-Sade-Sati style) influence on home/mind."
    if h == 8:
        return "Ashtama Shani (Saturn in the 8th from Moon) - go steady, avoid risks."
    return "No Sade Sati currently."


def build_transit_report(natal_par: Chart, now: dt.datetime = None) -> TransitReport:
    now = now or dt.datetime.now()
    positions = transit_positions(natal_par, now)
    notes: List[str] = []

    # Education: double transit over 4 (study) / 9 (higher learning).
    edu_hits = _double_transit(positions, [4, 5, 9])
    if edu_hits:
        education_trigger = (f"Jupiter and Saturn jointly influence house(s) "
                             f"{edu_hits} - a strong window to start or complete "
                             f"important studies / exams.")
    else:
        ju_edu = [h for h in (4, 5, 9) if h in positions[C.JUPITER].influences_from_lagna]
        education_trigger = (f"Jupiter currently supports education house(s) "
                             f"{ju_edu}. " if ju_edu else
                             "No major Jupiter/Saturn trigger on education houses now; "
                             "rely on the dasha windows.")

    # Career: double transit over 10 (profession) / 6 / 11 (gains).
    car_hits = _double_transit(positions, [10, 6, 11, 2])
    if car_hits:
        career_trigger = (f"Jupiter and Saturn jointly influence house(s) "
                          f"{car_hits} - a classic 'double-transit' trigger for a "
                          f"job change, promotion or new venture.")
    else:
        ju_car = [h for h in (10, 6, 11, 2) if h in positions[C.JUPITER].influences_from_lagna]
        sa_car = [h for h in (10, 6, 11, 2) if h in positions[C.SATURN].influences_from_lagna]
        career_trigger = (f"Jupiter touches career house(s) {ju_car}; Saturn touches "
                          f"{sa_car}. Use these alongside the dasha timeline.")

    sade = _sade_sati(positions)
    if "active" in sade:
        notes.append("During Sade Sati, prefer consolidation over big risky moves; "
                     "discipline and service mitigate it.")

    # Jupiter's house from Moon (favourable in 2,5,7,9,11 from Moon).
    ju_moon = positions[C.JUPITER].house_from_moon
    if ju_moon in (2, 5, 7, 9, 11):
        notes.append(f"Transit Jupiter is in the {ju_moon}th from your Moon - "
                     f"generally favourable for growth and opportunities.")

    return TransitReport(
        as_of=now.date(), positions=positions, sade_sati=sade,
        education_trigger=education_trigger, career_trigger=career_trigger,
        notes=notes,
    )
