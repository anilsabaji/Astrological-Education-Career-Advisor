"""
KP (Krishnamurti Paddhati) analysis.

Implements the core KP tools used for education & career judgement:

* House significators using the classic four-step theory.
* Houses signified by a planet (occupation + ownership + via its star-lord;
  with node substitution for Rahu / Ketu).
* Cuspal Sub-Lord (CSL) analysis - the deciding factor in KP for whether a
  matter fructifies, and the kind of result (e.g. job vs business).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set

from . import constants as C
from .ephemeris import Chart

NODES = {C.RAHU, C.KETU}


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------
def owned_houses(chart: Chart, planet: str) -> List[int]:
    """Houses whose sign-lord is ``planet``."""
    return [h for h in range(1, 13) if chart.lord_of_house(h) == planet]


def planets_in_star_of(chart: Chart, lord: str) -> List[str]:
    """Planets whose nakshatra (star) lord is ``lord``."""
    return [name for name, p in chart.planets.items()
            if p.lordship.star_lord == lord]


def _node_agents(chart: Chart, node: str) -> List[str]:
    """
    The planets a node (Rahu/Ketu) represents, in KP priority:
      1. planets conjoined with it in the same sign
      2. its star-lord
      3. the lord of the sign it occupies (dispositor) - only as a fallback
         when there is no conjoined planet (keeps signification focused).
    """
    p = chart.planets[node]
    conjoined = [other for other, op in chart.planets.items()
                 if other != node and other not in NODES
                 and op.sign_index == p.sign_index]
    agents: List[str] = list(conjoined)
    agents.append(p.lordship.star_lord)
    if not conjoined:
        agents.append(p.lordship.sign_lord)
    # de-dup preserving order
    seen, out = set(), []
    for a in agents:
        if a not in seen:
            seen.add(a)
            out.append(a)
    return out


def houses_signified_by(chart: Chart, planet: str) -> Set[int]:
    """
    Houses a planet signifies in KP:
      * houses occupied / owned by its STAR-LORD (strongest source)
      * the house it occupies
      * the houses it owns
    For nodes, the agents' occupation/ownership are used as well.
    """
    houses: Set[int] = set()
    p = chart.planets[planet]

    # Via star lord (strongest in KP).
    star_lord = p.lordship.star_lord
    sl = chart.planets[star_lord]
    houses.add(sl.house)
    houses.update(owned_houses(chart, star_lord))

    # Via own occupation & ownership.
    houses.add(p.house)
    houses.update(owned_houses(chart, planet))

    if planet in NODES:
        for agent in _node_agents(chart, planet):
            ap = chart.planets[agent]
            houses.add(ap.house)
            houses.update(owned_houses(chart, agent))
    return houses


@dataclass
class Significators:
    house: int
    grade_A: List[str]   # planets in star of occupants
    grade_B: List[str]   # occupants
    grade_C: List[str]   # planets in star of lord
    grade_D: List[str]   # the house lord
    ordered: List[str]   # de-duplicated A->D ordering


def significators_of_house(chart: Chart, house: int) -> Significators:
    """Four-step KP significators of a house (strongest first)."""
    occupants = [p.name for p in chart.planets_in_house(house)]
    lord = chart.lord_of_house(house)

    grade_A: List[str] = []
    for occ in occupants:
        for pl in planets_in_star_of(chart, occ):
            if pl not in grade_A:
                grade_A.append(pl)

    grade_B = list(occupants)

    grade_C = [pl for pl in planets_in_star_of(chart, lord)]

    grade_D = [lord]

    # Nodes occupying / aspecting the house are powerful significators too.
    for node in NODES:
        np = chart.planets[node]
        if np.house == house and node not in grade_B:
            grade_B.append(node)

    ordered: List[str] = []
    for grp in (grade_A, grade_B, grade_C, grade_D):
        for pl in grp:
            if pl not in ordered:
                ordered.append(pl)

    return Significators(house, grade_A, grade_B, grade_C, grade_D, ordered)


def significator_grades(chart: Chart, houses: List[int]) -> Dict[str, int]:
    """
    planet -> best grade (4=A strongest .. 1=D) across a group of houses.
    Grade A = planet in star of occupant; B = occupant; C = planet in star of
    lord; D = the house lord.
    """
    score: Dict[str, int] = {}
    for h in houses:
        sig = significators_of_house(chart, h)
        for grade, group in zip((4, 3, 2, 1),
                                (sig.grade_A, sig.grade_B, sig.grade_C, sig.grade_D)):
            for pl in group:
                score[pl] = max(score.get(pl, 0), grade)
    return score


def significators_of_houses(chart: Chart, houses: List[int]) -> List[str]:
    """
    Combined, de-duplicated significators for a group of houses, ranked by the
    strongest grading a planet attains across the group.
    """
    score = significator_grades(chart, houses)
    return sorted(score, key=lambda p: (-score[p], C.PLANETS.index(p)))


def strong_significators(chart: Chart, houses: List[int],
                         min_grade: int = 3) -> List[str]:
    """
    Significators at grade >= ``min_grade`` (A/B by default), plus the cuspal
    sub-lords of those houses. This focused set is what KP uses to TIME an
    event through the Vimshottari dasha.
    """
    grades = significator_grades(chart, houses)
    strong = {p for p, g in grades.items() if g >= min_grade}
    for h in houses:
        strong.add(cuspal_sub_lord(chart, h))
    return sorted(strong, key=lambda p: (-grades.get(p, 2), C.PLANETS.index(p)))


# ---------------------------------------------------------------------------
# Cuspal Sub-Lord analysis
# ---------------------------------------------------------------------------
@dataclass
class CSLFinding:
    house: int
    sub_lord: str
    signifies: List[int]
    favorable: bool
    note: str


def cuspal_sub_lord(chart: Chart, house: int) -> str:
    return chart.cusps[house - 1].lordship.sub_lord


def analyse_csl(chart: Chart, house: int, positive: List[int],
                negative: List[int]) -> CSLFinding:
    """
    Judge a cusp by the houses its sub-lord signifies. If the CSL signifies the
    positive houses (and avoids the negative ones), the matter is promised.
    """
    csl = cuspal_sub_lord(chart, house)
    signifies = sorted(houses_signified_by(chart, csl))
    pos_hit = [h for h in positive if h in signifies]
    neg_hit = [h for h in negative if h in signifies]
    favorable = len(pos_hit) >= 1 and len(pos_hit) >= len(neg_hit)
    note = (f"CSL of house {house} is {csl}; it signifies houses "
            f"{signifies}. Positive links: {pos_hit or 'none'}; "
            f"cautionary links: {neg_hit or 'none'}.")
    return CSLFinding(house, csl, signifies, favorable, note)


# ---------------------------------------------------------------------------
# Education & career judgement (KP)
# ---------------------------------------------------------------------------
@dataclass
class KPEducationResult:
    promised: bool
    significators: List[str]
    csl_findings: List[CSLFinding]
    higher_education_likely: bool
    field_planets: List[str]
    notes: List[str]


def judge_education(chart: Chart) -> KPEducationResult:
    notes: List[str] = []
    sig = significators_of_houses(chart, C.EDUCATION_POSITIVE)  # 4,5,9,11

    findings = [
        analyse_csl(chart, 4, C.EDUCATION_POSITIVE, C.EDUCATION_NEGATIVE),
        analyse_csl(chart, 5, C.EDUCATION_POSITIVE, C.EDUCATION_NEGATIVE),
        analyse_csl(chart, 9, [9, 11, 4, 5], [8, 12, 3]),
        analyse_csl(chart, 11, C.EDUCATION_POSITIVE, C.EDUCATION_NEGATIVE),
    ]
    promised = sum(f.favorable for f in findings) >= 2

    # Higher education: 9th & 11th CSL favourable and 9 strongly signified.
    he = (findings[2].favorable and findings[3].favorable)
    if he:
        notes.append("9th & 11th cuspal sub-lords support higher / specialised "
                     "education and successful completion.")
    else:
        notes.append("Higher-education yoga is moderate; completion may need "
                     "extra effort or come through a supportive dasha.")

    # Field planets = strongest significators of 4/5 (learning faculties).
    field_planets = significators_of_houses(chart, [4, 5])[:4]

    return KPEducationResult(
        promised=promised, significators=sig, csl_findings=findings,
        higher_education_likely=he, field_planets=field_planets, notes=notes,
    )


@dataclass
class KPCareerResult:
    promised: bool
    significators: List[str]
    csl_findings: List[CSLFinding]
    job_indicated: bool
    business_indicated: bool
    field_planets: List[str]
    earning_strength: str
    notes: List[str]


def judge_career(chart: Chart) -> KPCareerResult:
    notes: List[str] = []
    sig = significators_of_houses(chart, C.CAREER_POSITIVE)  # 2,6,10,11

    findings = [
        analyse_csl(chart, 10, C.CAREER_POSITIVE, C.CAREER_NEGATIVE),
        analyse_csl(chart, 6, [6, 10, 2, 11], [5, 12]),
        analyse_csl(chart, 2, [2, 6, 10, 11], [8, 12]),
        analyse_csl(chart, 11, C.CAREER_POSITIVE, C.CAREER_NEGATIVE),
    ]
    promised = sum(f.favorable for f in findings) >= 2

    # Job vs business via 10th & 6th CSL connections.
    csl10 = houses_signified_by(chart, cuspal_sub_lord(chart, 10))
    csl6 = houses_signified_by(chart, cuspal_sub_lord(chart, 6))
    combined = csl10 | csl6
    job_indicated = 6 in combined
    business_indicated = 7 in combined
    if job_indicated and not business_indicated:
        notes.append("Service / salaried employment is favoured (strong 6th-house link).")
    elif business_indicated and not job_indicated:
        notes.append("Independent business / self-employment is favoured (strong 7th-house link).")
    elif job_indicated and business_indicated:
        notes.append("Both service and business are possible; a job first, then "
                     "independent work, is a common pattern for such charts.")
    else:
        notes.append("Career mode is mixed; the running dasha will tilt it toward "
                     "service or enterprise.")

    # Earning strength via 2 (wealth), 6 (regular income), 11 (gains).
    earn_sig = significators_of_houses(chart, [2, 11])
    strong_earn = any(p in earn_sig[:4] for p in (C.JUPITER, C.VENUS, C.MERCURY))
    eleven = analyse_csl(chart, 11, [2, 6, 10, 11], [8, 12])
    if eleven.favorable and strong_earn:
        earning_strength = "Strong"
    elif eleven.favorable or strong_earn:
        earning_strength = "Good"
    else:
        earning_strength = "Moderate"

    field_planets = significators_of_houses(chart, [10, 6])[:4]

    return KPCareerResult(
        promised=promised, significators=sig, csl_findings=findings,
        job_indicated=job_indicated, business_indicated=business_indicated,
        field_planets=field_planets, earning_strength=earning_strength,
        notes=notes,
    )
