"""
Divisional charts (Vargas).

Divisional charts are the backbone of fine Parashara judgement. While the rasi
(D-1) shows the promise, the relevant varga shows whether and how it matures:

* **D-9  Navamsa**        - overall strength / dharma; a planet in the SAME sign
  in D-1 and D-9 is *vargottama* (very strong).
* **D-10 Dasamsa**        - career, profession, status and achievements
  (the primary CAREER varga).
* **D-24 Chaturvimsamsa** (Siddhamsa) - learning, knowledge and academic
  success (the primary EDUCATION varga).

This module is pure geometry (it depends only on constants + the rasi chart),
so it has no dependency on the analysis layer and can be imported anywhere.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List

from . import constants as C
from .ephemeris import Chart, norm360


# ---------------------------------------------------------------------------
# Divisional sign formulae (Parashara)
# ---------------------------------------------------------------------------
def navamsa_sign(longitude: float) -> str:
    """D-9 sign. Movable signs start from themselves, fixed from the 9th,
    dual from the 5th (element rule; avoids float-boundary errors)."""
    lon = norm360(longitude)
    sign_index = int(lon // 30)
    deg_in_sign = lon - sign_index * 30
    part = int(deg_in_sign / (30.0 / 9.0))       # 0..8
    if sign_index % 3 == 0:        # movable
        start = sign_index
    elif sign_index % 3 == 1:      # fixed -> 9th
        start = (sign_index + 8) % 12
    else:                          # dual -> 5th
        start = (sign_index + 4) % 12
    return C.SIGNS[(start + part) % 12]


def dasamsa_sign(longitude: float) -> str:
    """D-10 sign. Ten 3 deg parts: odd signs count from the sign itself,
    even signs from the 9th sign."""
    lon = norm360(longitude)
    sign_index = int(lon // 30)
    deg_in_sign = lon - sign_index * 30
    part = int(deg_in_sign // 3.0)               # 0..9
    if sign_index % 2 == 0:                       # odd ordinal sign
        start = sign_index
    else:                                         # even -> 9th
        start = (sign_index + 8) % 12
    return C.SIGNS[(start + part) % 12]


def siddhamsa_sign(longitude: float) -> str:
    """D-24 sign (Chaturvimsamsa / Siddhamsa) - the education varga.
    Twenty-four 1 deg 15 min parts: odd signs count from Leo, even from Cancer."""
    lon = norm360(longitude)
    sign_index = int(lon // 30)
    deg_in_sign = lon - sign_index * 30
    part = int(deg_in_sign / (30.0 / 24.0))      # 0..23
    if sign_index % 2 == 0:                       # odd ordinal sign -> from Leo
        start = C.SIGNS.index("Leo")
    else:                                         # even -> from Cancer
        start = C.SIGNS.index("Cancer")
    return C.SIGNS[(start + part) % 12]


DIVISION_FUNCS: Dict[int, Callable[[float], str]] = {
    9: navamsa_sign,
    10: dasamsa_sign,
    24: siddhamsa_sign,
}

VARGA_NAMES = {
    1: "Rasi (D-1)",
    9: "Navamsa (D-9)",
    10: "Dasamsa (D-10)",
    24: "Chaturvimsamsa (D-24)",
}


def divisional_sign(longitude: float, division: int) -> str:
    if division == 1:
        return C.SIGNS[int(norm360(longitude) // 30)]
    return DIVISION_FUNCS[division](longitude)


# ---------------------------------------------------------------------------
# Divisional chart model
# ---------------------------------------------------------------------------
@dataclass
class VargaPlanet:
    name: str
    sign: str
    sign_index: int
    house: int


@dataclass
class VargaChart:
    division: int
    name: str
    asc_sign: str
    asc_index: int
    planets: Dict[str, VargaPlanet]
    house_signs: List[str]

    def sign_of_house(self, house: int) -> str:
        return self.house_signs[house - 1]

    def lord_of_house(self, house: int) -> str:
        return C.SIGN_LORD[self.sign_of_house(house)]

    def house_of_sign(self, sign: str) -> int:
        return self.house_signs.index(sign) + 1

    def planets_in_house(self, house: int) -> List[str]:
        return [p.name for p in self.planets.values() if p.house == house]

    def house_of_planet(self, planet: str) -> int:
        return self.planets[planet].house


def _whole_sign_house(sign_index: int, asc_index: int) -> int:
    return (sign_index - asc_index) % 12 + 1


def build_varga(base_chart: Chart, division: int) -> VargaChart:
    """
    Build a divisional chart from a rasi (D-1) chart. Houses are whole-sign from
    the divisional ascendant - the standard way varga charts are cast.
    """
    func = (lambda lon: C.SIGNS[int(norm360(lon) // 30)]) if division == 1 \
        else DIVISION_FUNCS[division]

    asc_sign = func(base_chart.ascendant)
    asc_index = C.SIGNS.index(asc_sign)

    planets: Dict[str, VargaPlanet] = {}
    for name, p in base_chart.planets.items():
        sign = func(p.longitude)
        si = C.SIGNS.index(sign)
        planets[name] = VargaPlanet(
            name=name, sign=sign, sign_index=si,
            house=_whole_sign_house(si, asc_index),
        )

    house_signs = [C.SIGNS[(asc_index + i) % 12] for i in range(12)]
    return VargaChart(
        division=division, name=VARGA_NAMES.get(division, f"D-{division}"),
        asc_sign=asc_sign, asc_index=asc_index, planets=planets,
        house_signs=house_signs,
    )


# ---------------------------------------------------------------------------
# Vargottama (same sign in D-1 and D-9 -> a planet of special strength)
# ---------------------------------------------------------------------------
def vargottama_planets(base_chart: Chart) -> List[str]:
    d9 = build_varga(base_chart, 9)
    out = []
    for name, p in base_chart.planets.items():
        if p.sign == d9.planets[name].sign:
            out.append(name)
    return out
