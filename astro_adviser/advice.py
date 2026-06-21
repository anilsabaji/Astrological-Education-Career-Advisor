"""
Combined education & career advice.

This module fuses the KP and Parashara findings into concrete, ranked
recommendations:

* education streams to pursue,
* career fields that balance EARNING and SATISFACTION,
* a job-vs-business verdict that both systems agree (or disagree) on.

The fusion works by collecting "field planets" from each system (weighted by
the strength / grade they earned there), expanding every planet into the
real-world fields it governs, and ranking those fields by the combined weight.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List

from . import constants as C
from . import kp, parashara as par, shadbala as sbmod
from .ephemeris import Chart


@dataclass
class Recommendation:
    title: str
    score: float
    drivers: List[str]          # planets/signs that point here
    reasoning: str


@dataclass
class EducationAdvice:
    promised: bool
    higher_education_likely: bool
    streams: List[Recommendation]
    strength_summary: str
    key_planets: List[str]
    kp_notes: List[str]
    par_notes: List[str]
    yogas: List[str]
    varga: object = None             # D-24 (Siddhamsa) analysis
    varga_summary: str = ""
    shadbala_notes: List[str] = field(default_factory=list)
    shadbala: object = None


@dataclass
class CareerAdvice:
    promised: bool
    fields: List[Recommendation]
    earning_rating: str
    earning_explanation: str
    satisfaction_rating: str
    satisfaction_explanation: str
    job_vs_business: str
    key_planets: List[str]
    kp_notes: List[str]
    par_notes: List[str]
    yogas: List[str]
    varga: object = None             # D-10 (Dasamsa) analysis
    varga_summary: str = ""
    shadbala_notes: List[str] = field(default_factory=list)
    shadbala: object = None


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _weighted_planets(*sources):
    """
    Merge several (planet_list, weight) sources into a planet->score dict.
    Earlier planets in each list get a small ranking bonus.
    """
    score: Dict[str, float] = defaultdict(float)
    for planets, weight in sources:
        for i, p in enumerate(planets):
            score[p] += weight * (1.0 - 0.12 * i)
    return score


def _rank_fields(planet_scores: Dict[str, float], mapping: Dict[str, List[str]],
                 sign_hint: str = None, top: int = 6) -> List[Recommendation]:
    """Expand planet scores into real-world fields and rank them."""
    field_score: Dict[str, float] = defaultdict(float)
    field_drivers: Dict[str, set] = defaultdict(set)

    for planet, sc in planet_scores.items():
        for fld in mapping.get(planet, []):
            field_score[fld] += sc
            field_drivers[fld].add(C.PLANET_SHORT.get(planet, planet))

    # Sign temperament adds a light nudge to matching fields.
    if sign_hint:
        for fld in C.SIGN_FIELDS.get(sign_hint, []):
            # fuzzy match against existing field titles
            for existing in list(field_score.keys()):
                if fld.split()[0].lower() in existing.lower():
                    field_score[existing] += 0.4
                    field_drivers[existing].add(sign_hint)

    ranked = sorted(field_score.items(), key=lambda kv: -kv[1])[:top]
    out: List[Recommendation] = []
    for fld, sc in ranked:
        drivers = sorted(field_drivers[fld])
        out.append(Recommendation(
            title=fld, score=round(sc, 3), drivers=drivers,
            reasoning=f"Indicated by {', '.join(drivers)}.",
        ))
    return out


# ---------------------------------------------------------------------------
# Education
# ---------------------------------------------------------------------------
def _apply_strength(planet_scores: Dict[str, float], sb) -> Dict[str, float]:
    """Scale each planet's contribution by its Shadbala strength factor."""
    if sb is None:
        return planet_scores
    return {p: sc * sbmod.strength_factor(sb, p) for p, sc in planet_scores.items()}


def advise_education(kp_chart: Chart, par_chart: Chart, sb=None) -> EducationAdvice:
    k = kp.judge_education(kp_chart)
    p = par.judge_education(par_chart)
    if sb is None:
        sb = sbmod.compute_shadbala(par_chart)

    planet_scores = _weighted_planets(
        (k.field_planets, 1.0),          # KP significators of 4 & 5
        (k.significators[:4], 0.6),      # KP significators of 4,5,9,11
        (p.field_planets, 1.0),          # Parashara karakas + 4/5 lords
        # D-24 (Siddhamsa) education-varga indicators, weighted by its strength.
        (p.varga.field_planets if p.varga else [], 0.6 + 0.6 * (p.varga.strength if p.varga else 0)),
    )
    # Weight each contributing planet by its Shadbala status (strong/benefic
    # planets pull their fields up; weak/kashta planets are discounted).
    planet_scores = _apply_strength(planet_scores, sb)

    # Use the 4th-house sign (KP) as a temperament hint.
    sign_hint = kp_chart.sign_of_house(4)
    streams = _rank_fields(planet_scores, C.PLANET_EDUCATION_STREAMS, sign_hint)

    promised = k.promised
    he = k.higher_education_likely

    # Blend the Parashara education score with the Shadbala of the learning
    # karakas (Mercury & Jupiter).
    me, ju = sb.planets.get(C.MERCURY), sb.planets.get(C.JUPITER)
    karaka_ratio = (min(me.ratio, 1.6) + min(ju.ratio, 1.6)) / 2 / 1.6 if me and ju else 0.5
    blended = p.strength_score * 0.65 + karaka_ratio * 0.35
    if blended >= 0.7:
        strength = "Strong - good academic potential"
    elif blended >= 0.5:
        strength = "Above average - steady learner"
    else:
        strength = "Moderate - benefits from focus and remedies"

    key_planets = sorted(planet_scores, key=lambda x: -planet_scores[x])[:4]

    # Shadbala status of the education-critical planets.
    note_planets = []
    for cand in [C.MERCURY, C.JUPITER] + key_planets:
        if cand not in note_planets and cand in sb.planets:
            note_planets.append(cand)
    shadbala_notes = [sbmod.status_line(sb, x) for x in note_planets[:4]]
    if me and ju:
        weak = [x for x in (C.MERCURY, C.JUPITER) if not sb.planets[x].sufficient]
        if weak:
            shadbala_notes.append(
                f"Learning karaka(s) {', '.join(weak)} are below the required "
                f"Shadbala - remedies and disciplined effort are advised.")

    varga_summary = ""
    if p.varga:
        v = p.varga
        varga_summary = (
            f"D-24 (Chaturvimsamsa), the education varga, has Lagna {v.asc_sign} "
            f"(lord {v.asc_lord}). Mercury sits in its {v.key_placements.get(C.MERCURY)}th "
            f"house and Jupiter in the {v.key_placements.get(C.JUPITER)}th, giving a "
            f"divisional academic strength of {v.strength}. "
            + (f"Vargottama planets: {', '.join(v.vargottama)}. " if v.vargottama else "")
        )

    return EducationAdvice(
        promised=promised, higher_education_likely=he, streams=streams,
        strength_summary=strength, key_planets=key_planets,
        kp_notes=k.notes, par_notes=p.notes,
        yogas=[y.name for y in p.yogas],
        varga=p.varga, varga_summary=varga_summary,
        shadbala_notes=shadbala_notes, shadbala=sb,
    )


# ---------------------------------------------------------------------------
# Career
# ---------------------------------------------------------------------------
_EARN_MAP = {"Strong": 3, "Good": 2, "Moderate": 1}


def advise_career(kp_chart: Chart, par_chart: Chart, sb=None) -> CareerAdvice:
    k = kp.judge_career(kp_chart)
    p = par.judge_career(par_chart)
    if sb is None:
        sb = sbmod.compute_shadbala(par_chart)

    planet_scores = _weighted_planets(
        (k.field_planets, 1.0),          # KP significators of 10 & 6
        (k.significators[:4], 0.6),      # KP significators of 2,6,10,11
        (p.field_planets, 1.1),          # planets in 10th + 10th lord + karaka
        # D-10 (Dasamsa) career-varga indicators, weighted by its strength.
        (p.varga.field_planets if p.varga else [], 0.7 + 0.7 * (p.varga.strength if p.varga else 0)),
    )
    planet_scores = _apply_strength(planet_scores, sb)

    sign_hint = par_chart.sign_of_house(10)
    fields = _rank_fields(planet_scores, C.PLANET_CAREER_FIELDS, sign_hint)

    # ---- Earning rating (KP + Parashara wealth + Shadbala of wealth givers) -
    kp_earn = _EARN_MAP.get(k.earning_strength, 1)
    par_earn = 3 if p.wealth_score >= 0.7 else 2 if p.wealth_score >= 0.4 else 1
    # Shadbala of the 2nd & 11th lords and Jupiter/Venus.
    wealth_planets = {par_chart.lord_of_house(2), par_chart.lord_of_house(11),
                      C.JUPITER, C.VENUS}
    wp_ratios = [sb.planets[x].ratio for x in wealth_planets if x in sb.planets]
    wealth_strength = sum(wp_ratios) / len(wp_ratios) if wp_ratios else 1.0
    sb_earn = 3 if wealth_strength >= 1.15 else 2 if wealth_strength >= 0.9 else 1
    combined = (kp_earn + par_earn + sb_earn) / 3.0
    if combined >= 2.5:
        earning_rating = "High earning potential"
    elif combined >= 1.75:
        earning_rating = "Good / comfortable earning"
    else:
        earning_rating = "Moderate earning - grows with the right dasha"
    earning_explanation = (
        f"KP rates earning capacity as '{k.earning_strength}' (2nd, 11th "
        f"significators and 11th cuspal sub-lord); Parashara wealth score is "
        f"{p.wealth_score}; the wealth-giving planets average "
        f"{round(wealth_strength, 2)}x their required Shadbala. "
        f"Together this reads as: {earning_rating.lower()}."
    )

    # ---- Satisfaction (5th/9th + dignity + Ishta/Kashta of career planets) --
    sat = _satisfaction(par_chart, p, list(planet_scores.keys()))
    benefic_field = [x for x in list(planet_scores.keys())[:4]
                     if x in sb.planets and sb.planets[x].benefic]
    sat_rating, sat_expl = sat
    if len(benefic_field) >= 2 and not sat_rating.startswith("High"):
        sat_expl += (f" The leading career planets ({', '.join(benefic_field)}) "
                     f"give Ishta (benefic) results in Shadbala, supporting "
                     f"genuine satisfaction.")

    # ---- Job vs business consensus ----
    kp_mode = ("Job / service" if (k.job_indicated and not k.business_indicated)
               else "Business / self-employment" if (k.business_indicated and not k.job_indicated)
               else "Both")
    par_mode = p.job_lean
    job_vs_business = _consensus_mode(kp_mode, par_mode)

    key_planets = sorted(planet_scores, key=lambda x: -planet_scores[x])[:4]

    # Shadbala status of the career-critical planets.
    tenth_lord = par_chart.lord_of_house(10)
    note_planets = []
    for cand in [tenth_lord] + key_planets:
        if cand not in note_planets and cand in sb.planets:
            note_planets.append(cand)
    shadbala_notes = [sbmod.status_line(sb, x) for x in note_planets[:4]]
    strongest = sb.ranking[0]
    shadbala_notes.append(
        f"The strongest planet overall is {strongest} ({sb.planets[strongest].rupas} "
        f"rupas); its periods and the fields it governs tend to deliver the best results.")

    varga_summary = ""
    if p.varga:
        v = p.varga
        pit = (", ".join(v.planets_in_focus) if v.planets_in_focus
               else "no planet (10th lord & lagna lord carry it)")
        varga_summary = (
            f"D-10 (Dasamsa), the career varga, has Lagna {v.asc_sign} "
            f"(lord {v.asc_lord}) and a 10th house of {v.focus_sign} (lord "
            f"{v.focus_lord}). Planets in its 10th: {pit}. Divisional career "
            f"strength {v.strength}. "
            + (f"Vargottama planets: {', '.join(v.vargottama)}. " if v.vargottama else "")
        )

    return CareerAdvice(
        promised=k.promised, fields=fields,
        earning_rating=earning_rating, earning_explanation=earning_explanation,
        satisfaction_rating=sat_rating, satisfaction_explanation=sat_expl,
        job_vs_business=job_vs_business, key_planets=key_planets,
        kp_notes=k.notes, par_notes=p.notes,
        yogas=[y.name for y in p.yogas],
        varga=p.varga, varga_summary=varga_summary,
        shadbala_notes=shadbala_notes, shadbala=sb,
    )


def _satisfaction(par_chart: Chart, p: par.ParCareerResult, field_planets):
    """
    Satisfaction is judged from how well the work aligns with the person's
    creative / dharmic houses (5 & 9) and the dignity of the planets that
    drive the career.
    """
    dig = par.all_dignities(par_chart)
    fifth = par.lord_placement(par_chart, 5)
    ninth = par.lord_placement(par_chart, 9)

    good = {1, 4, 5, 7, 9, 10, 11}
    align = 0
    if fifth.placed_in_house in good:
        align += 1
    if ninth.placed_in_house in good:
        align += 1
    # Average dignity of the leading field planets.
    digs = [dig[fp].score for fp in field_planets[:4] if fp in dig]
    avg_dig = sum(digs) / len(digs) if digs else 0.5

    score = align / 2 * 0.5 + avg_dig * 0.5
    if score >= 0.7:
        rating = "High - work is likely to feel meaningful"
    elif score >= 0.5:
        rating = "Good - reasonable contentment with the right field"
    else:
        rating = "Variable - satisfaction depends on choosing aligned work"

    expl = (
        f"The 5th lord ({fifth.lord}) sits in house {fifth.placed_in_house} and the "
        f"9th lord ({ninth.lord}) in house {ninth.placed_in_house}; the career-driving "
        f"planets carry an average dignity of {round(avg_dig,2)}. "
        f"This points to: {rating.lower()}."
    )
    return rating, expl


def _consensus_mode(kp_mode: str, par_mode: str) -> str:
    kp_job = "Job" in kp_mode or kp_mode == "Both"
    kp_biz = "Business" in kp_mode or kp_mode == "Both"
    par_job = "Job" in par_mode or "Both" in par_mode
    par_biz = "Business" in par_mode or "Both" in par_mode

    job = kp_job and par_job
    biz = kp_biz and par_biz
    if job and not biz:
        return (f"Service / salaried job is favoured. (KP: {kp_mode}; "
                f"Parashara: {par_mode}.)")
    if biz and not job:
        return (f"Independent business / self-employment is favoured. (KP: {kp_mode}; "
                f"Parashara: {par_mode}.)")
    if kp_job and par_biz and not kp_biz:
        return (f"KP leans to a job while Parashara leans to business - a salaried "
                f"start followed by an independent venture is the likely path. "
                f"(KP: {kp_mode}; Parashara: {par_mode}.)")
    if kp_biz and par_job and not kp_job:
        return (f"KP leans to business while Parashara leans to a job - structured "
                f"employment first, enterprise later. (KP: {kp_mode}; "
                f"Parashara: {par_mode}.)")
    return (f"Both job and business are workable; the running dasha decides the "
            f"emphasis. (KP: {kp_mode}; Parashara: {par_mode}.)")
