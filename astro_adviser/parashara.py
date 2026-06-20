"""
Parashara (classical Vedic) analysis.

Covers the tools a traditional astrologer uses for education & career:

* Planetary dignity & a simple Shadbala-style strength score.
* House-lord placement (2/4/5/9 for education, 2/6/7/10/11 for career).
* Naisargika karakas (Mercury & Jupiter for learning; Sun, Saturn, Mercury,
  Jupiter for profession).
* Classic yogas - Saraswati, Budhaditya, Gajakesari, Dhana, Raja, Pancha-
  mahapurusha - that bear on intellect, profession and wealth.
* Divisional confirmation via the Navamsa (D-9) and Dasamsa (D-10, the
  career varga).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from . import constants as C
from .ephemeris import Chart, norm360
from . import varga
from .varga import navamsa_sign, dasamsa_sign, siddhamsa_sign, build_varga


# ---------------------------------------------------------------------------
# Divisional sign helpers are provided by the varga module and re-exported here
# (navamsa_sign / dasamsa_sign / siddhamsa_sign) for backward compatibility.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Dignity & strength
# ---------------------------------------------------------------------------
@dataclass
class Dignity:
    planet: str
    sign: str
    state: str          # Exalted / Moolatrikona / Own / Friendly / Neutral /
                        # Enemy / Debilitated
    score: float        # 0..1 relative strength
    retrograde: bool


def _relation(planet: str, sign_lord: str) -> str:
    if planet == sign_lord:
        return "own"
    rel = C.NATURAL_RELATION.get(planet, {})
    return rel.get(sign_lord, "n")


def _dignity_state(planet: str, sign: str):
    """Return (state, score) of a planet placed in an arbitrary sign."""
    if planet in (C.RAHU, C.KETU):
        return "Node (acts via dispositor)", 0.5
    lord = C.SIGN_LORD[sign]
    if planet in C.EXALTATION and C.EXALTATION[planet][0] == sign:
        return "Exalted", 1.0
    if planet in C.DEBILITATION and C.DEBILITATION[planet] == sign:
        return "Debilitated", 0.1
    if planet in C.MOOLATRIKONA and C.MOOLATRIKONA[planet] == sign:
        return "Moolatrikona", 0.9
    if planet in C.OWN_SIGNS and sign in C.OWN_SIGNS[planet]:
        return "Own sign", 0.85
    rel = _relation(planet, lord)
    if rel == "f":
        return "Friendly sign", 0.65
    if rel == "e":
        return "Enemy sign", 0.3
    return "Neutral sign", 0.5


def dignity_in_sign(planet: str, sign: str) -> Dignity:
    """Dignity of a planet in a given sign (used for divisional charts)."""
    state, score = _dignity_state(planet, sign)
    return Dignity(planet, sign, state, score, False)


def dignity_of(chart: Chart, planet: str) -> Dignity:
    p = chart.planets[planet]
    state, score = _dignity_state(planet, p.sign)
    return Dignity(planet, p.sign, state, score, p.retrograde)


def all_dignities(chart: Chart) -> Dict[str, Dignity]:
    return {name: dignity_of(chart, name) for name in C.PLANETS}


# ---------------------------------------------------------------------------
# House-lord placement
# ---------------------------------------------------------------------------
@dataclass
class LordPlacement:
    house: int
    lord: str
    placed_in_house: int
    placed_in_sign: str
    dignity: str


def lord_placement(chart: Chart, house: int) -> LordPlacement:
    lord = chart.lord_of_house(house)
    p = chart.planets[lord]
    return LordPlacement(
        house=house, lord=lord, placed_in_house=p.house,
        placed_in_sign=p.sign, dignity=dignity_of(chart, lord).state,
    )


# ---------------------------------------------------------------------------
# Yogas
# ---------------------------------------------------------------------------
KENDRAS = {1, 4, 7, 10}
TRIKONAS = {1, 5, 9}


@dataclass
class Yoga:
    name: str
    present: bool
    detail: str


def _conjunct(chart: Chart, a: str, b: str) -> bool:
    return chart.planets[a].house == chart.planets[b].house


def detect_yogas(chart: Chart) -> List[Yoga]:
    yogas: List[Yoga] = []
    pl = chart.planets

    # Budha-Aditya (Sun + Mercury together) -> intelligence, communication.
    if _conjunct(chart, C.SUN, C.MERCURY):
        yogas.append(Yoga("Budha-Aditya Yoga", True,
                          "Sun and Mercury together sharpen intellect, "
                          "communication and administrative ability."))

    # Gaja-Kesari (Jupiter in kendra from Moon) -> wisdom, repute.
    diff = (pl[C.JUPITER].house - pl[C.MOON].house) % 12 + 1
    if diff in (1, 4, 7, 10):
        yogas.append(Yoga("Gaja-Kesari Yoga", True,
                          "Jupiter in a kendra from the Moon grants intelligence, "
                          "good judgement and lasting reputation."))

    # Saraswati Yoga (Mercury, Jupiter, Venus in kendra/trikona/2nd, with
    # Jupiter well placed) -> exceptional learning & expression.
    good = KENDRAS | TRIKONAS | {2}
    if all(pl[x].house in good for x in (C.MERCURY, C.JUPITER, C.VENUS)):
        yogas.append(Yoga("Saraswati Yoga", True,
                          "Mercury, Jupiter and Venus occupy supportive houses - "
                          "a classic combination for learning, arts and eloquence."))

    # Pancha-Mahapurusha yogas (planet exalted/own in a kendra).
    mahapurusha = {C.MARS: "Ruchaka", C.MERCURY: "Bhadra", C.JUPITER: "Hamsa",
                   C.VENUS: "Malavya", C.SATURN: "Sasa"}
    for planet, yname in mahapurusha.items():
        d = dignity_of(chart, planet)
        if pl[planet].house in KENDRAS and d.state in ("Exalted", "Own sign", "Moolatrikona"):
            yogas.append(Yoga(f"{yname} Yoga (Mahapurusha)", True,
                              f"{planet} is strong in a kendra - confers leadership "
                              f"and success in its domain."))

    # Dhana Yoga (lords of 2 & 11 related to 5/9/10 lords by placement).
    wealth_lords = {chart.lord_of_house(2), chart.lord_of_house(11)}
    gain_houses = {chart.planets[l].house for l in wealth_lords}
    if gain_houses & ({2, 5, 9, 10, 11}):
        yogas.append(Yoga("Dhana Yoga", True,
                          "Wealth-house lords (2nd & 11th) are linked to gain / "
                          "fortune houses - supports steady earning."))

    # Raja Yoga (a kendra lord and a trikona lord conjoined).
    kendra_lords = {chart.lord_of_house(h) for h in KENDRAS}
    trikona_lords = {chart.lord_of_house(h) for h in TRIKONAS}
    found = False
    for kl in kendra_lords:
        for tl in trikona_lords:
            if kl != tl and _conjunct(chart, kl, tl):
                found = True
    if found:
        yogas.append(Yoga("Raja Yoga", True,
                          "A kendra lord and trikona lord combine - supports rise "
                          "in status, authority and professional success."))

    return yogas


# ---------------------------------------------------------------------------
# Divisional-chart analysis (D-10 career, D-24 education)
# ---------------------------------------------------------------------------
@dataclass
class VargaAnalysis:
    division: int
    name: str
    asc_sign: str
    asc_lord: str
    focus_house: int                 # 10 for D-10, 1 for D-24 (lagna-centric)
    focus_sign: str
    focus_lord: str
    planets_in_focus: List[str]
    key_placements: Dict[str, int]   # important planet -> house in this varga
    vargottama: List[str]
    field_planets: List[str]
    strength: float                  # 0..1
    notes: List[str]


def analyse_dasamsa(chart: Chart) -> VargaAnalysis:
    """
    D-10 (Dasamsa) - the career varga. The 10th house of the D-10, its lord and
    any planets there describe the actual profession and rise in status; the
    D-10 lagna lord shows how one earns recognition.
    """
    d10 = build_varga(chart, 10)
    vargo = varga.vargottama_planets(chart)
    notes: List[str] = []

    tenth_sign = d10.sign_of_house(10)
    tenth_lord = d10.lord_of_house(10)
    planets_in_tenth = d10.planets_in_house(10)
    asc_lord = d10.lord_of_house(1)
    planets_in_lagna = d10.planets_in_house(1)

    notes.append(f"D-10 Lagna is {d10.asc_sign} (lord {asc_lord}); its 10th house "
                 f"is {tenth_sign} (lord {tenth_lord}).")
    if planets_in_tenth:
        notes.append(f"Planet(s) in the D-10 10th house: {', '.join(planets_in_tenth)}"
                     f" - the clearest signature of the actual profession.")
    else:
        notes.append("No planet sits in the D-10 10th house; the 10th lord and the "
                     "D-10 lagna lord carry the career signification.")

    # Strength of the D-1 career karakas evaluated in their D-10 sign.
    key = {}
    strong_count = 0
    for k in (C.SUN, C.SATURN, C.MERCURY, C.JUPITER):
        key[k] = d10.house_of_planet(k)
        ds = dignity_in_sign(k, d10.planets[k].sign)
        if ds.score >= 0.65 or d10.house_of_planet(k) in (KENDRAS | TRIKONAS):
            strong_count += 1
    if vargo:
        notes.append(f"Vargottama (same sign in D-1 & D-9): {', '.join(vargo)} - "
                     f"these planets give particularly reliable results.")

    # Career field planets from the D-10: 10th-house planets, 10th lord, lagna
    # lord, plus any career karaka that is vargottama.
    field: List[str] = []
    for p in planets_in_tenth + [tenth_lord, asc_lord] + planets_in_lagna:
        if p not in field:
            field.append(p)
    for k in (C.SUN, C.SATURN, C.MERCURY, C.JUPITER):
        if k in vargo and k not in field:
            field.append(k)

    strength = round(strong_count / 4.0 * 0.6
                     + (1.0 if planets_in_tenth else 0.5) * 0.2
                     + (0.2 if asc_lord in vargo or tenth_lord in vargo else 0.0), 3)

    return VargaAnalysis(
        division=10, name="Dasamsa (D-10)", asc_sign=d10.asc_sign,
        asc_lord=asc_lord, focus_house=10, focus_sign=tenth_sign,
        focus_lord=tenth_lord, planets_in_focus=planets_in_tenth,
        key_placements=key, vargottama=vargo, field_planets=field[:5],
        strength=strength, notes=notes,
    )


def analyse_siddhamsa(chart: Chart) -> VargaAnalysis:
    """
    D-24 (Chaturvimsamsa / Siddhamsa) - the education varga. Strength of Mercury
    & Jupiter here, and planets in the learning houses (1, 4, 5, 9) of the D-24,
    show academic capacity and the subjects one excels in.
    """
    d24 = build_varga(chart, 24)
    vargo = varga.vargottama_planets(chart)
    notes: List[str] = []

    asc_lord = d24.lord_of_house(1)
    learning_houses = [1, 4, 5, 9]
    learners: List[str] = []
    for h in learning_houses:
        learners.extend(d24.planets_in_house(h))

    me_h = d24.house_of_planet(C.MERCURY)
    ju_h = d24.house_of_planet(C.JUPITER)
    notes.append(f"D-24 Lagna is {d24.asc_sign} (lord {asc_lord}).")
    notes.append(f"In the D-24, Mercury is in house {me_h} and Jupiter in house "
                 f"{ju_h} (1/4/5/9/10 here strengthen academics).")
    if learners:
        notes.append(f"Planet(s) in the D-24 learning houses (1/4/5/9): "
                     f"{', '.join(sorted(set(learners)))}.")

    # Strength: Mercury / Jupiter well placed in D-24 + benefic learning houses.
    good = KENDRAS | TRIKONAS
    strong = 0
    for k, h in ((C.MERCURY, me_h), (C.JUPITER, ju_h)):
        ds = dignity_in_sign(k, d24.planets[k].sign)
        if h in good:
            strong += 1
        if ds.score >= 0.65:
            strong += 1
    strength = round(min(strong, 4) / 4.0 * 0.7
                     + min(len(set(learners)), 3) / 3.0 * 0.3, 3)

    # Education field planets from D-24: Mercury/Jupiter if well placed, lagna
    # lord, and planets in the learning houses.
    field: List[str] = []
    for k, h in ((C.MERCURY, me_h), (C.JUPITER, ju_h)):
        if h in (good | {10}):
            field.append(k)
    if asc_lord not in field:
        field.append(asc_lord)
    for p in learners:
        if p not in field and p not in (C.RAHU, C.KETU):
            field.append(p)

    return VargaAnalysis(
        division=24, name="Chaturvimsamsa (D-24)", asc_sign=d24.asc_sign,
        asc_lord=asc_lord, focus_house=1, focus_sign=d24.asc_sign,
        focus_lord=asc_lord, planets_in_focus=sorted(set(learners)),
        key_placements={C.MERCURY: me_h, C.JUPITER: ju_h},
        vargottama=vargo, field_planets=field[:5], strength=strength,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Education & career judgement (Parashara)
# ---------------------------------------------------------------------------
@dataclass
class ParEducationResult:
    edu_lords: List[LordPlacement]
    karaka_strength: Dict[str, str]
    yogas: List[Yoga]
    strength_score: float
    field_planets: List[str]
    notes: List[str]
    varga: VargaAnalysis = None       # D-24 analysis


def judge_education(chart: Chart) -> ParEducationResult:
    notes: List[str] = []
    edu_lords = [lord_placement(chart, h) for h in (2, 4, 5, 9)]

    dig = all_dignities(chart)
    karaka_strength = {
        C.MERCURY: dig[C.MERCURY].state,
        C.JUPITER: dig[C.JUPITER].state,
    }

    # 4th & 5th lord well placed (kendra/trikona/2/11) and good dignity.
    good = KENDRAS | TRIKONAS | {2, 11}
    well = [lp for lp in edu_lords if lp.house in (4, 5) and lp.placed_in_house in good]
    if well:
        notes.append("Education-house lord(s) occupy supportive houses, giving a "
                     "stable foundation for studies.")

    me, ju = dig[C.MERCURY].score, dig[C.JUPITER].score
    if me >= 0.8:
        notes.append("Mercury (karaka of intellect) is strong - quick grasp, good "
                     "with logic, numbers and analysis.")
    elif me <= 0.3:
        notes.append("Mercury is weak - concentration or examinations may need "
                     "extra discipline; remedies for Mercury can help.")
    if ju >= 0.8:
        notes.append("Jupiter (karaka of wisdom) is strong - favours higher studies, "
                     "philosophy, teaching, law or finance.")

    yogas = detect_yogas(chart)
    edu_yoga = [y for y in yogas if y.name in
                ("Saraswati Yoga", "Budha-Aditya Yoga", "Gaja-Kesari Yoga")]

    # D-24 (Siddhamsa) - the education varga.
    d24 = analyse_siddhamsa(chart)
    notes.append(f"Education varga D-24 strength is {d24.strength}; "
                 + d24.notes[1])

    # Composite education strength (now includes the D-24 confirmation).
    lord_score = sum(1 for lp in edu_lords if lp.placed_in_house in good) / 4.0
    score = round((me + ju) / 2 * 0.4 + lord_score * 0.25
                  + min(len(edu_yoga), 2) * 0.075 + d24.strength * 0.2, 3)

    # Field planets = strong learning karakas + 4th/5th lords + D-24 indicators.
    field_planets = []
    for cand in (C.MERCURY, C.JUPITER):
        if dig[cand].score >= 0.6:
            field_planets.append(cand)
    for lp in edu_lords:
        if lp.house in (4, 5) and lp.lord not in field_planets:
            field_planets.append(lp.lord)
    for p in d24.field_planets:
        if p not in field_planets:
            field_planets.append(p)

    return ParEducationResult(
        edu_lords=edu_lords, karaka_strength=karaka_strength, yogas=edu_yoga,
        strength_score=score, field_planets=field_planets[:5], notes=notes,
        varga=d24,
    )


@dataclass
class ParCareerResult:
    tenth_sign: str
    tenth_lord: LordPlacement
    planets_in_tenth: List[str]
    tenth_lord_dasamsa: str
    karaka_strength: Dict[str, str]
    yogas: List[Yoga]
    job_lean: str           # "Job", "Business", or "Both"
    wealth_score: float
    field_planets: List[str]
    notes: List[str]
    varga: VargaAnalysis = None       # D-10 analysis


def judge_career(chart: Chart) -> ParCareerResult:
    notes: List[str] = []
    tenth_sign = chart.sign_of_house(10)
    tenth_lord = lord_placement(chart, 10)
    planets_in_tenth = [p.name for p in chart.planets_in_house(10)]

    dig = all_dignities(chart)
    karaka_strength = {
        C.SUN: dig[C.SUN].state, C.SATURN: dig[C.SATURN].state,
        C.MERCURY: dig[C.MERCURY].state, C.JUPITER: dig[C.JUPITER].state,
    }

    # D-10 placement of the 10th lord (career confirmation).
    tenth_lord_dasamsa = dasamsa_sign(chart.planets[tenth_lord.lord].longitude)
    # Full D-10 (Dasamsa) career-varga analysis.
    d10 = analyse_dasamsa(chart)

    # Job vs business: Sun/Saturn/Moon strong + 6th/10th -> service;
    # Mars/Mercury/Rahu + 7th -> business. Use sign nature of 10th too.
    job_points = 0
    biz_points = 0
    # Movable 10th sign or Saturn/Sun influence on 10th -> service.
    if tenth_sign in C.MOVABLE_SIGNS:
        job_points += 1
    if tenth_sign in C.FIXED_SIGNS:
        biz_points += 1
    if C.SATURN in planets_in_tenth or C.SUN in planets_in_tenth:
        job_points += 1
    if C.MARS in planets_in_tenth or C.MERCURY in planets_in_tenth or C.RAHU in planets_in_tenth:
        biz_points += 1
    # 6th lord strength (service) vs 7th lord strength (business).
    if dig[chart.lord_of_house(6)].score >= 0.6:
        job_points += 1
    if dig[chart.lord_of_house(7)].score >= 0.6:
        biz_points += 1
    if job_points > biz_points:
        job_lean = "Job / service"
    elif biz_points > job_points:
        job_lean = "Business / self-employment"
    else:
        job_lean = "Both (job then independent work)"

    yogas = detect_yogas(chart)
    career_yoga = [y for y in yogas if y.name in
                   ("Raja Yoga", "Dhana Yoga") or "Mahapurusha" in y.name]

    # Wealth score from 2nd, 11th lords + Jupiter/Venus dignity + Dhana yoga.
    good = KENDRAS | TRIKONAS | {2, 11}
    second = lord_placement(chart, 2)
    eleventh = lord_placement(chart, 11)
    w = 0.0
    w += 0.25 if second.placed_in_house in good else 0.0
    w += 0.25 if eleventh.placed_in_house in good else 0.0
    w += 0.25 * max(dig[C.JUPITER].score, dig[C.VENUS].score)
    w += 0.25 if any(y.name == "Dhana Yoga" for y in yogas) else 0.0
    wealth_score = round(w, 3)

    # Field planets = planets in 10th + 10th lord + strongest career karaka,
    # enriched with the D-10 (Dasamsa) career-varga indicators.
    field_planets: List[str] = list(planets_in_tenth)
    if tenth_lord.lord not in field_planets:
        field_planets.append(tenth_lord.lord)
    strongest_karaka = max((C.SUN, C.SATURN, C.MERCURY, C.JUPITER),
                           key=lambda k: dig[k].score)
    if strongest_karaka not in field_planets:
        field_planets.append(strongest_karaka)
    for p in d10.field_planets:
        if p not in field_planets:
            field_planets.append(p)

    notes.append(f"The 10th house ({tenth_sign}) and its lord {tenth_lord.lord} "
                 f"(in house {tenth_lord.placed_in_house}, {tenth_lord.dignity}) "
                 f"set the professional tone.")
    if planets_in_tenth:
        notes.append(f"Planet(s) in the 10th: {', '.join(planets_in_tenth)} - "
                     f"these strongly colour the kind of work.")
    notes.extend(d10.notes)

    return ParCareerResult(
        tenth_sign=tenth_sign, tenth_lord=tenth_lord,
        planets_in_tenth=planets_in_tenth, tenth_lord_dasamsa=tenth_lord_dasamsa,
        karaka_strength=karaka_strength, yogas=career_yoga, job_lean=job_lean,
        wealth_score=wealth_score, field_planets=field_planets[:6], notes=notes,
        varga=d10,
    )
