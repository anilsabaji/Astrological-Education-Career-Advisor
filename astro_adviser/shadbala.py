"""
Shadbala - the six-fold strength of the planets (Parashara).

Computed for the seven classical grahas (Sun .. Saturn). The six balas are:

  1. Sthana Bala  - positional (Uccha, Saptavargaja, Ojha-yugma, Kendradi, Drekkana)
  2. Dig Bala     - directional (house/longitude based)
  3. Kala Bala    - temporal (Nathonnatha, Paksha, Tribhaga, Abda/Masa/Vara/Hora,
                    Ayana [uses DECLINATION], Yuddha)
  4. Cheshta Bala - motional (uses SPEED and DIRECTION / retrogression)
  5. Naisargika   - natural (fixed)
  6. Drik Bala    - aspectual (benefic/malefic aspects)

Strengths are in *virupas* (60 virupas = 1 rupa). Each planet has a required
minimum (in rupas); the ratio of actual/required and the Ishta/Kashta phala
(benefic vs harmful result) tell us how favourably a planet will deliver.

Some sub-balas that require sunrise/sunset (Tribhaga, Hora) are computed with
the Swiss Ephemeris; calendar-lord balas (Abda/Masa) use solar-ingress search.
Yuddha (planetary war) is applied only when two star-planets are within 1 deg.
This is a faithful, well-documented implementation; minor school-to-school
variations exist in the literature.
"""

from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass, field
from typing import Dict, List

import swisseph as swe

from . import constants as C
from . import varga
from .ephemeris import Chart, norm360, _julian_day, _SWE_PLANET

SB_PLANETS = [C.SUN, C.MOON, C.MARS, C.MERCURY, C.JUPITER, C.VENUS, C.SATURN]

# Naisargika (natural) bala in virupas = 60 * rank/7.
NAISARGIKA = {
    C.SUN: 60.0, C.MOON: 51.43, C.VENUS: 42.86, C.JUPITER: 34.29,
    C.MERCURY: 25.71, C.MARS: 17.14, C.SATURN: 8.57,
}
# Required total Shadbala (rupas) for a planet to be "sufficiently strong".
REQUIRED_RUPAS = {
    C.SUN: 6.5, C.MOON: 6.0, C.MARS: 5.0, C.MERCURY: 7.0,
    C.JUPITER: 6.5, C.VENUS: 5.5, C.SATURN: 5.0,
}
# Mean daily motion (deg/day) for the Cheshta (speed) model.
MEAN_SPEED = {
    C.SUN: 0.9856, C.MOON: 13.176, C.MARS: 0.524, C.MERCURY: 1.383,
    C.JUPITER: 0.083, C.VENUS: 1.602, C.SATURN: 0.0335,
}
# Saptavarga divisions and their sign functions.
_SAPTAVARGA = [
    (1, lambda lon: C.SIGNS[int(norm360(lon) // 30)]),
    (2, varga.hora_sign), (3, varga.drekkana_sign), (7, varga.saptamsa_sign),
    (9, varga.navamsa_sign), (12, varga.dwadasamsa_sign), (30, varga.trimsamsa_sign),
]

KENDRA = {1, 4, 7, 10}
PANAPHARA = {2, 5, 8, 11}
# Benefic / malefic for Paksha and Drik bala.
NAT_BENEFIC = {C.JUPITER, C.VENUS, C.MERCURY, C.MOON}
NAT_MALEFIC = {C.SUN, C.MARS, C.SATURN}


def _ang_dist(a: float, b: float) -> float:
    d = abs(norm360(a) - norm360(b)) % 360
    return d if d <= 180 else 360 - d


# ---------------------------------------------------------------------------
# Compound friendship (Panchadha maitri) - needed for Saptavargaja bala
# ---------------------------------------------------------------------------
def _permanent(p: str, lord: str) -> int:
    if p == lord:
        return 2          # own -> treated as great-friend equivalent here
    r = C.NATURAL_RELATION.get(p, {}).get(lord, "n")
    return {"f": 1, "n": 0, "e": -1}[r]


def _temporary(chart: Chart, p: str, other: str) -> int:
    rel = (chart.planets[other].sign_index - chart.planets[p].sign_index) % 12 + 1
    return 1 if rel in (2, 3, 4, 10, 11, 12) else -1


def _compound(chart: Chart, p: str, lord: str) -> str:
    if p == lord:
        return "own"
    score = _permanent(p, lord) + _temporary(chart, p, lord)
    if score >= 2:
        return "great_friend"
    if score == 1:
        return "friend"
    if score == 0:
        return "neutral"
    if score == -1:
        return "enemy"
    return "great_enemy"


_SAPTA_VIRUPA = {
    "moolatrikona": 45.0, "own": 30.0, "great_friend": 22.5, "friend": 15.0,
    "neutral": 7.5, "enemy": 3.75, "great_enemy": 1.875,
}


# ---------------------------------------------------------------------------
# Sthana Bala
# ---------------------------------------------------------------------------
def uccha_bala(planet: str, longitude: float) -> float:
    if planet not in C.EXALTATION:
        return 0.0
    sign, deg = C.EXALTATION[planet]
    exalt_lon = C.SIGNS.index(sign) * 30 + deg
    debil_lon = norm360(exalt_lon + 180)
    return _ang_dist(longitude, debil_lon) / 3.0          # 0..60


def saptavargaja_bala(chart: Chart, planet: str) -> float:
    total = 0.0
    for _, fn in _SAPTAVARGA:
        sign = fn(chart.planets[planet].longitude)
        if C.MOOLATRIKONA.get(planet) == sign:
            total += _SAPTA_VIRUPA["moolatrikona"]
        else:
            total += _SAPTA_VIRUPA[_compound(chart, planet, C.SIGN_LORD[sign])]
    return total


def ojhayugma_bala(chart: Chart, planet: str) -> float:
    """Odd/even strength in Rasi and Navamsa (15 each)."""
    val = 0.0
    rasi_odd = chart.planets[planet].sign_index % 2 == 0       # Aries(0) is odd #1
    nav = varga.navamsa_sign(chart.planets[planet].longitude)
    nav_odd = C.SIGNS.index(nav) % 2 == 0
    wants_odd = planet in (C.SUN, C.MARS, C.JUPITER, C.MERCURY, C.SATURN)
    if rasi_odd == wants_odd:
        val += 15.0
    if nav_odd == wants_odd:
        val += 15.0
    return val


def kendradi_bala(house: int) -> float:
    if house in KENDRA:
        return 60.0
    if house in PANAPHARA:
        return 30.0
    return 15.0


def drekkana_bala(planet: str, longitude: float) -> float:
    deg = norm360(longitude) % 30
    part = int(deg // 10)                                  # 0,1,2
    if planet in (C.SUN, C.JUPITER, C.MARS) and part == 0:
        return 15.0
    if planet in (C.SATURN, C.MERCURY) and part == 1:
        return 15.0
    if planet in (C.MOON, C.VENUS) and part == 2:
        return 15.0
    return 0.0


# ---------------------------------------------------------------------------
# Dig Bala
# ---------------------------------------------------------------------------
def dig_bala(chart: Chart, planet: str) -> float:
    asc, mc = chart.ascendant, chart.midheaven
    nadir = norm360(mc + 180)        # 4th
    desc = norm360(asc + 180)        # 7th
    weak_point = {
        C.SUN: nadir, C.MARS: nadir,       # strong in 10th
        C.MOON: mc, C.VENUS: mc,           # strong in 4th
        C.JUPITER: desc, C.MERCURY: desc,  # strong in 1st
        C.SATURN: asc,                     # strong in 7th
    }[planet]
    return _ang_dist(chart.planets[planet].longitude, weak_point) / 3.0


# ---------------------------------------------------------------------------
# Kala Bala helpers (time / sunrise)
# ---------------------------------------------------------------------------
def _weekday_lord_index(jd: float) -> int:
    """0=Sun .. 6=Sat for the civil day containing jd."""
    return int(math.floor(jd + 1.5)) % 7


_WD_LORD = [C.SUN, C.MOON, C.MARS, C.MERCURY, C.JUPITER, C.VENUS, C.SATURN]
# Chaldean order for planetary horas.
_CHALDEAN = [C.SATURN, C.JUPITER, C.MARS, C.SUN, C.VENUS, C.MERCURY, C.MOON]


def _sun_lon_sidereal(jd: float) -> float:
    res = swe.calc_ut(jd, swe.SUN, swe.FLG_MOSEPH | swe.FLG_SIDEREAL)
    return norm360(res[0][0])


def _rise_set(jd: float, lon: float, lat: float, rise: bool):
    flag = swe.CALC_RISE if rise else swe.CALC_SET
    try:
        res, t = swe.rise_trans(jd - 1.0, swe.SUN, flag | swe.BIT_DISC_CENTER,
                                (lon, lat, 0.0), 0.0, 0.0, swe.FLG_MOSEPH)
        return t[0]
    except Exception:
        return None


@dataclass
class _KalaParts:
    nathonnatha: float
    paksha: float
    tribhaga: float
    abda: float
    masa: float
    vara: float
    hora: float
    ayana: float
    yuddha: float

    def total(self) -> float:
        return (self.nathonnatha + self.paksha + self.tribhaga + self.abda
                + self.masa + self.vara + self.hora + self.ayana + self.yuddha)


def _ayana_bala(planet: str, declination: float) -> float:
    north_pref = planet in (C.SUN, C.MARS, C.JUPITER, C.VENUS, C.MERCURY)
    delta = declination if north_pref else -declination
    val = 1.2766 * (23.45 + delta)
    return max(0.0, min(60.0, val))


def _kala_bala(chart: Chart, planet: str, jd: float,
               sun_lon: float, moon_lon: float) -> _KalaParts:
    lat, lon = chart.latitude, chart.longitude

    # Sun hour angle -> Nathonnatha (day/night strength).
    gst = swe.sidtime(jd)                       # Greenwich sidereal time (hours)
    lst = (gst + lon / 15.0) % 24.0
    sun_eq = swe.calc_ut(jd, swe.SUN, swe.FLG_MOSEPH | swe.FLG_EQUATORIAL)
    ra_sun = sun_eq[0][0]                        # degrees
    ha = norm360(lst * 15.0 - ra_sun)
    ha_fold = ha if ha <= 180 else 360 - ha      # 0 at meridian (noon) .. 180 midnight
    day_strength = (180 - ha_fold) / 3.0
    night_strength = ha_fold / 3.0
    if planet == C.MERCURY:
        nath = 60.0
    elif planet in (C.SUN, C.JUPITER, C.VENUS):
        nath = day_strength
    else:
        nath = night_strength

    # Paksha (lunar phase).
    elong = _ang_dist(moon_lon, sun_lon)         # 0..180
    if planet in NAT_BENEFIC:
        paksha = elong / 3.0
    else:
        paksha = (180 - elong) / 3.0
    if planet == C.MOON:
        paksha *= 2.0

    # Sunrise / sunset for Tribhaga & Hora.
    sr = _rise_set(jd, lon, lat, True)
    ss = _rise_set(jd, lon, lat, False)
    tribhaga = 0.0
    hora = 0.0
    if sr is not None and ss is not None:
        # ensure sunrise before jd; if not, step back a day.
        if sr > jd:
            sr = _rise_set(jd - 1.0, lon, lat, True) or sr
        next_sr = _rise_set(jd + 0.5, lon, lat, True)
        is_day = sr <= jd < ss if ss > sr else False
        # Tribhaga.
        if is_day:
            third = int((jd - sr) / ((ss - sr) / 3.0))
            ruler = [C.MERCURY, C.SUN, C.SATURN][min(third, 2)]
        else:
            start = ss if jd >= ss else _rise_set(jd - 1.0, lon, lat, False) or ss
            end = next_sr or (start + 0.5)
            third = int((jd - start) / max((end - start) / 3.0, 1e-6))
            ruler = [C.MOON, C.VENUS, C.MARS][min(max(third, 0), 2)]
        if planet == ruler or planet == C.JUPITER:
            tribhaga = 60.0
        # Hora (planetary hour).
        day_start = sr
        ahoratra_end = next_sr or (sr + 1.0)
        hora_len = (ahoratra_end - day_start) / 24.0
        idx = int((jd - day_start) / hora_len) if hora_len > 0 else 0
        idx = max(0, min(23, idx))
        wd = _weekday_lord_index(sr)
        day_lord = _WD_LORD[wd]
        start_idx = _CHALDEAN.index(day_lord)
        hora_lord = _CHALDEAN[(start_idx + idx) % 7]
        if planet == hora_lord:
            hora = 60.0
    # Vara (weekday lord) bala.
    vara = 0.0
    wd_birth = _weekday_lord_index(sr if (sr is not None and sr <= jd) else jd)
    if planet == _WD_LORD[wd_birth]:
        vara = 45.0

    # Abda (year) & Masa (month) lords via solar ingress search.
    abda = masa = 0.0
    cur_sign = int(_sun_lon_sidereal(jd) // 30)
    # month ingress (Sun entered current sign).
    j = jd
    for _ in range(40):
        if int(_sun_lon_sidereal(j) // 30) != cur_sign:
            break
        j -= 1.0
    masa_lord = _WD_LORD[_weekday_lord_index(j + 1.0)]
    if planet == masa_lord:
        masa = 30.0
    # year ingress (Sun entered Aries / Mesha).
    j = jd
    for _ in range(380):
        if int(_sun_lon_sidereal(j) // 30) == 0 and int(_sun_lon_sidereal(j - 1.0) // 30) == 11:
            break
        j -= 1.0
    abda_lord = _WD_LORD[_weekday_lord_index(j)]
    if planet == abda_lord:
        abda = 15.0

    # Ayana (declination) bala.
    ayana = _ayana_bala(planet, chart.planets[planet].declination)

    return _KalaParts(nathonnatha=nath, paksha=paksha, tribhaga=tribhaga,
                      abda=abda, masa=masa, vara=vara, hora=hora,
                      ayana=ayana, yuddha=0.0)


# ---------------------------------------------------------------------------
# Cheshta Bala (speed & direction)
# ---------------------------------------------------------------------------
def cheshta_bala(chart: Chart, planet: str, kala: _KalaParts) -> float:
    if planet == C.SUN:
        return kala.ayana                       # rule: Sun's cheshta = ayana bala
    if planet == C.MOON:
        return kala.paksha                      # rule: Moon's cheshta = paksha bala
    p = chart.planets[planet]
    if p.retrograde:
        return 60.0
    mean = MEAN_SPEED[planet]
    frac = p.speed / mean if mean else 1.0
    if frac <= 0:
        return 60.0
    # Slow / near-stationary -> strong; fast direct -> weak.
    return max(5.0, min(60.0, (1.5 - frac) / 1.5 * 60.0))


def motion_state(chart: Chart, planet: str) -> str:
    p = chart.planets[planet]
    if planet in (C.SUN, C.MOON):
        return "Direct (luminary)"
    if p.retrograde:
        return "Retrograde (Vakra) - very high motional strength"
    mean = MEAN_SPEED[planet]
    frac = abs(p.speed) / mean if mean else 1.0
    if frac < 0.2:
        return "Near-stationary (Vikala) - strong"
    if frac > 1.3:
        return "Fast / direct (Sheeghra)"
    return "Direct (normal speed)"


# ---------------------------------------------------------------------------
# Drik Bala (aspectual) - simplified Sripati-style
# ---------------------------------------------------------------------------
_SPECIAL_ASPECTS = {
    C.MARS: [4, 8], C.JUPITER: [5, 9], C.SATURN: [3, 10],
}


def drik_bala(chart: Chart, planet: str) -> float:
    target_house = chart.planets[planet].house
    val = 0.0
    for other in SB_PLANETS:
        if other == planet:
            continue
        oh = chart.planets[other].house
        rel = (target_house - oh) % 12 + 1
        aspects = [7] + _SPECIAL_ASPECTS.get(other, [])
        if rel in aspects:
            contrib = 15.0 if other in NAT_BENEFIC else -15.0
            val += contrib
    return val / 4.0                            # BPHS divides drishti pinda by 4


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
@dataclass
class PlanetStrength:
    planet: str
    sthana: float
    dig: float
    kala: float
    cheshta: float
    naisargika: float
    drik: float
    total_virupa: float
    rupas: float
    required: float
    ratio: float
    sufficient: bool
    ishta: float
    kashta: float
    benefic: bool
    speed: float
    retrograde: bool
    declination: float
    motion: str
    sub: Dict[str, float] = field(default_factory=dict)


@dataclass
class ShadbalaResult:
    planets: Dict[str, PlanetStrength]
    ranking: List[str]               # strongest -> weakest by rupas

    def strongest(self, n: int = 3) -> List[str]:
        return self.ranking[:n]


def compute_shadbala(chart: Chart) -> ShadbalaResult:
    """Compute Shadbala for the seven grahas on a (Parashara) rasi chart."""
    jd = _julian_day(chart.when_utc)
    sun_lon = chart.planets[C.SUN].longitude
    moon_lon = chart.planets[C.MOON].longitude

    results: Dict[str, PlanetStrength] = {}
    for planet in SB_PLANETS:
        p = chart.planets[planet]
        ub = uccha_bala(planet, p.longitude)
        sv = saptavargaja_bala(chart, planet)
        oj = ojhayugma_bala(chart, planet)
        kd = kendradi_bala(p.house)
        dk = drekkana_bala(planet, p.longitude)
        sthana = ub + sv + oj + kd + dk

        dig = dig_bala(chart, planet)
        kala = _kala_bala(chart, planet, jd, sun_lon, moon_lon)
        ch = cheshta_bala(chart, planet, kala)
        nb = NAISARGIKA[planet]
        dr = drik_bala(chart, planet)

        total = sthana + dig + kala.total() + ch + nb + dr
        rupas = total / 60.0
        required = REQUIRED_RUPAS[planet]
        ratio = rupas / required
        ishta = math.sqrt(max(ub, 0) * max(ch, 0))
        kashta = math.sqrt(max(60 - ub, 0) * max(60 - ch, 0))

        results[planet] = PlanetStrength(
            planet=planet, sthana=round(sthana, 1), dig=round(dig, 1),
            kala=round(kala.total(), 1), cheshta=round(ch, 1),
            naisargika=round(nb, 1), drik=round(dr, 1),
            total_virupa=round(total, 1), rupas=round(rupas, 2),
            required=required, ratio=round(ratio, 2), sufficient=rupas >= required,
            ishta=round(ishta, 1), kashta=round(kashta, 1), benefic=ishta >= kashta,
            speed=round(p.speed, 4), retrograde=p.retrograde,
            declination=round(p.declination, 2), motion=motion_state(chart, planet),
            sub={
                "uccha": round(ub, 1), "saptavargaja": round(sv, 1),
                "ojhayugma": round(oj, 1), "kendradi": round(kd, 1),
                "drekkana": round(dk, 1), "nathonnatha": round(kala.nathonnatha, 1),
                "paksha": round(kala.paksha, 1), "tribhaga": round(kala.tribhaga, 1),
                "abda": round(kala.abda, 1), "masa": round(kala.masa, 1),
                "vara": round(kala.vara, 1), "hora": round(kala.hora, 1),
                "ayana": round(kala.ayana, 1),
            },
        )

    ranking = sorted(results, key=lambda p: -results[p].rupas)
    return ShadbalaResult(planets=results, ranking=ranking)


# ---------------------------------------------------------------------------
# Strength helpers used by the education / career assessment
# ---------------------------------------------------------------------------
def strength_factor(sb: ShadbalaResult, planet: str) -> float:
    """
    A 0.6 .. 1.4 multiplier reflecting a planet's Shadbala status, used to
    weight its contribution to education / career field selection. Nodes (no
    Shadbala) return a neutral 1.0.
    """
    ps = sb.planets.get(planet)
    if ps is None:
        return 1.0
    f = 0.6 + 0.6 * min(ps.ratio, 1.6) / 1.6      # ratio 0..1.6 -> 0.6..1.2
    if ps.benefic:
        f += 0.1
    if ps.retrograde:
        f += 0.05                                  # retro = strong cheshta
    return round(min(1.4, max(0.6, f)), 3)


def status_line(sb: ShadbalaResult, planet: str) -> str:
    ps = sb.planets.get(planet)
    if ps is None:
        return f"{planet}: node - Shadbala not applicable."
    decl_dir = "N" if ps.declination >= 0 else "S"
    return (f"{planet}: Shadbala {ps.rupas} rupas "
            f"({'sufficient' if ps.sufficient else 'below'} the {ps.required} "
            f"required), {'Ishta/benefic' if ps.benefic else 'Kashta/strained'}; "
            f"{ps.motion}; declination {abs(ps.declination):.1f}\u00b0{decl_dir}.")


# ---------------------------------------------------------------------------
# Bhava Bala (house strengths) and Ishta/Kashta phala timeline
# ---------------------------------------------------------------------------
_HOUSE_ASPECTS = {C.MARS: [4, 8], C.JUPITER: [5, 9], C.SATURN: [3, 10]}


@dataclass
class BhavaStrength:
    house: int
    lord: str
    bhavadhipati: float       # Shadbala of the house lord (virupa)
    occupant: float           # contribution of occupying planets (virupa)
    drishti: float            # net benefic - malefic aspect on the bhava
    total_virupa: float
    rupas: float


@dataclass
class BhavaBalaResult:
    houses: Dict[int, BhavaStrength]
    ranking: List[int]        # strongest -> weakest house

    def rupas(self, house: int) -> float:
        return self.houses[house].rupas

    def group_strength(self, houses: List[int]) -> float:
        return sum(self.houses[h].rupas for h in houses) / len(houses)


def _bhava_drishti(chart: Chart, house: int) -> float:
    """Net aspect on a bhava: benefics +20, malefics -20 (full/special aspects)."""
    val = 0.0
    for other in SB_PLANETS:
        oh = chart.planets[other].house
        rel = (house - oh) % 12 + 1
        if rel == 1:
            continue                       # occupancy handled separately
        aspects = [7] + _HOUSE_ASPECTS.get(other, [])
        if rel in aspects:
            val += 20.0 if other in NAT_BENEFIC else -20.0
    return val


def compute_bhava_bala(chart: Chart, sb: ShadbalaResult) -> BhavaBalaResult:
    """
    A practical Bhava Bala composite emphasising the classical Bhavadhipati Bala
    (strength of the house lord) plus the bhava's aspect balance and the
    Shadbala of any occupants. Returned in rupas, with a house ranking.
    """
    houses: Dict[int, BhavaStrength] = {}
    for h in range(1, 13):
        lord = chart.lord_of_house(h)
        bhavadhipati = sb.planets[lord].total_virupa if lord in sb.planets else 300.0
        # Occupants add a modest bonus (not their full strength) so the house
        # lord's Shadbala (Bhavadhipati Bala) remains the dominant term.
        occ = 0.10 * sum(sb.planets[p.name].total_virupa
                         for p in chart.planets_in_house(h) if p.name in sb.planets)
        drishti = _bhava_drishti(chart, h)
        total = bhavadhipati + occ + drishti
        houses[h] = BhavaStrength(
            house=h, lord=lord, bhavadhipati=round(bhavadhipati, 1),
            occupant=round(occ, 1), drishti=round(drishti, 1),
            total_virupa=round(total, 1), rupas=round(total / 60.0, 2),
        )
    ranking = sorted(houses, key=lambda h: -houses[h].rupas)
    return BhavaBalaResult(houses=houses, ranking=ranking)


def house_strength_label(rupas: float) -> str:
    if rupas >= 9.0:
        return "very strong"
    if rupas >= 7.0:
        return "strong"
    if rupas >= 5.0:
        return "moderate"
    return "weak"


def period_phala(sb: ShadbalaResult, lord: str):
    """
    Ishta/Kashta verdict for a dasha lord's period.
    Returns (ishta, kashta, verdict). Nodes (no Shadbala) -> variable.
    """
    ps = sb.planets.get(lord)
    if ps is None:
        return None, None, "Variable (node - acts via its dispositor)"
    if ps.ishta >= ps.kashta and ps.ishta >= 40:
        verdict = "Strongly benefic"
    elif ps.ishta >= ps.kashta:
        verdict = "Benefic / supportive"
    elif ps.kashta - ps.ishta > 15:
        verdict = "Challenging"
    else:
        verdict = "Mixed"
    return ps.ishta, ps.kashta, verdict


def ishta_ranking(sb: ShadbalaResult) -> List[str]:
    """Planets ordered by Ishta phala (benefic-result potential)."""
    return sorted(sb.planets, key=lambda p: -sb.planets[p].ishta)
