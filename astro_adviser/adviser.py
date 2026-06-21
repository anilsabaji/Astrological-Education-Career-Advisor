"""
High-level orchestrator.

Given birth details it builds:
  * the KP chart (Krishnamurti ayanamsa + Placidus) and
  * the Parashara chart (Lahiri + whole-sign),
  * the 3-level Vimshottari dasha tree,
and produces the full education + career advice and the FAQ answers.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import List, Optional

from . import advice, dasha, faq, remedies, transits
from . import parashara as par
from . import shadbala as sbmod
from .ephemeris import Chart, compute_chart


@dataclass
class BirthData:
    name: str
    date: dt.date
    time: dt.time
    latitude: float
    longitude: float
    tz_offset_hours: float
    place: str = ""

    @property
    def datetime(self) -> dt.datetime:
        return dt.datetime.combine(self.date, self.time)


@dataclass
class CurrentDasha:
    md: Optional[str]
    ad: Optional[str]
    pd: Optional[str]
    md_period: str
    ad_period: str
    pd_period: str


@dataclass
class AdviceReport:
    birth: BirthData
    kp_chart: Chart
    par_chart: Chart
    dasha_tree: list
    current: CurrentDasha
    education: advice.EducationAdvice
    career: advice.CareerAdvice
    faqs: List[faq.FAQAnswer]
    yogas: list
    edu_remedies: list
    career_remedies: list
    transit: transits.TransitReport
    shadbala: object = None
    bhava_bala: object = None
    phala_timeline: object = None
    ishta_ranking: list = field(default_factory=list)
    education_best: list = field(default_factory=list)
    career_best: list = field(default_factory=list)
    current_age: int = 0
    life_stage: str = ""


def build_report(birth: BirthData, now: Optional[dt.datetime] = None) -> AdviceReport:
    now = now or dt.datetime.now()

    kp_chart = compute_chart(birth.datetime, birth.latitude, birth.longitude,
                             birth.tz_offset_hours, system="KP")
    par_chart = compute_chart(birth.datetime, birth.latitude, birth.longitude,
                              birth.tz_offset_hours, system="Parashara")

    tree = dasha.build_dasha_tree(par_chart.planets["Moon"].longitude,
                                  birth.datetime)
    md, ad, pd = dasha.find_running(tree, now)
    current = CurrentDasha(
        md=md.lord if md else None,
        ad=ad.lord if ad else None,
        pd=pd.lord if pd else None,
        md_period=dasha.format_period(md) if md else "-",
        ad_period=dasha.format_period(md, ad) if ad else "-",
        pd_period=dasha.format_period(md, ad, pd) if pd else "-",
    )

    # Shadbala (six-fold strength) on the Parashara rasi chart - shared by the
    # education and career assessments.
    shadbala = sbmod.compute_shadbala(par_chart)

    education = advice.advise_education(kp_chart, par_chart, sb=shadbala)
    career = advice.advise_career(kp_chart, par_chart, sb=shadbala)

    ctx = faq.FAQContext(kp_chart, par_chart, tree, now)
    faqs = faq.answer_all(ctx)

    yogas = par.detect_yogas(par_chart)

    edu_remedies = remedies.remedies_for(par_chart, kp_chart, "education")
    career_remedies = remedies.remedies_for(par_chart, kp_chart, "career")
    transit_report = transits.build_transit_report(par_chart, now)

    # Bhava Bala (house strengths) and the Ishta/Kashta dasha-phala timeline.
    bhava_bala = sbmod.compute_bhava_bala(par_chart, shadbala)
    phala_timeline = _dasha_phala_timeline(tree, shadbala, now)
    ishta_rank = sbmod.ishta_ranking(shadbala)

    # Combined "best periods": KP fructification windows overlaid with the
    # Ishta/Kashta phala of the running Mahadasha, age-aware.
    education_best = _best_periods(kp_chart, tree, shadbala, now, "education", birth.date)
    career_best = _best_periods(kp_chart, tree, shadbala, now, "career", birth.date)
    current_age = _age_years(birth.date, now)
    life_stage = _life_stage(current_age)
    career.shadbala_notes.append(
        f"Age context: the native is currently {current_age} years old "
        f"({life_stage}); the career windows below are shown from working age "
        f"and tagged with the age at that time.")

    # House-strength notes feed back into the two assessments.
    edu_hs = bhava_bala.group_strength([4, 5, 9])
    education.shadbala_notes.append(
        f"Bhava Bala: the education houses (4th, 5th, 9th) average "
        f"{round(edu_hs, 2)} rupas - {sbmod.house_strength_label(edu_hs)}.")
    car_hs = bhava_bala.group_strength([2, 10, 11])
    career.shadbala_notes.append(
        f"Bhava Bala: the career houses (2nd, 10th, 11th) average "
        f"{round(car_hs, 2)} rupas - {sbmod.house_strength_label(car_hs)}.")

    return AdviceReport(
        birth=birth, kp_chart=kp_chart, par_chart=par_chart, dasha_tree=tree,
        current=current, education=education, career=career, faqs=faqs,
        yogas=yogas, edu_remedies=edu_remedies, career_remedies=career_remedies,
        transit=transit_report, shadbala=shadbala, bhava_bala=bhava_bala,
        phala_timeline=phala_timeline, ishta_ranking=ishta_rank,
        education_best=education_best, career_best=career_best,
        current_age=current_age, life_stage=life_stage,
    )


def _age_years(birth_date, on):
    """Native's age in completed years on a given date/datetime."""
    return on.year - birth_date.year - (
        (on.month, on.day) < (birth_date.month, birth_date.day))


def _life_stage(age):
    if age < 18:
        return "Student years"
    if age < 25:
        return "Early career / entry"
    if age < 35:
        return "Career building"
    if age < 50:
        return "Career peak"
    if age < 60:
        return "Senior / consolidation"
    return "Retirement / advisory"


def _best_periods(kp_chart, tree, sb, now, domain, birth_date,
                  horizon_years=18, max_windows=6):
    """
    Overlay the KP fructification windows for ``domain`` with the Ishta/Kashta
    phala of the running Mahadasha, producing ranked "best periods".

    The native's AGE is taken into account: career windows are only sought from
    working age (~16+), and every window is annotated with the age range and
    life-stage so the advice is age-appropriate.
    """
    houses = [4, 9, 11] if domain == "education" else [2, 10, 11]
    from_date = now
    if domain == "career":
        try:
            work_start = dt.datetime(birth_date.year + 16, birth_date.month,
                                     birth_date.day)
        except ValueError:                      # e.g. 29 Feb birth
            work_start = dt.datetime(birth_date.year + 16, birth_date.month, 28)
        from_date = max(now, work_start)

    windows = faq.fructification_windows(
        kp_chart, tree, houses, from_date, horizon_years=horizon_years,
        max_windows=max_windows, require_levels=2)
    out = []
    for w in windows:
        md, _, _ = dasha.find_running(tree, w.start)
        md_lord = md.lord if md else None
        ishta, kashta, verdict = sbmod.period_phala(sb, md_lord) if md_lord else (None, None, "-")
        benefic = ishta is not None and ishta >= kashta
        prime = benefic and ("benefic" in verdict.lower())
        quality = "Prime" if prime else ("Favourable" if benefic else "Workable")
        age_start = _age_years(birth_date, w.start)
        age_end = _age_years(birth_date, w.end)
        out.append({
            "chain": w.chain,
            "start": w.start.date().isoformat(),
            "end": w.end.date().isoformat(),
            "md_lord": md_lord,
            "phala": verdict,
            "quality": quality,
            "age_start": age_start,
            "age_end": age_end,
            "life_stage": _life_stage(age_start),
            "note": w.note,
        })
    return out


def _dasha_phala_timeline(tree, sb, now, count=7):
    """
    Annotate the running + upcoming Mahadashas (and the current MD's
    Antardashas) with the dasha lord's Ishta/Kashta phala, so one can see which
    periods are likely benefic vs challenging.
    """
    maha = []
    current_md = None
    for md in tree:
        if md.end < now:
            continue
        ishta, kashta, verdict = sbmod.period_phala(sb, md.lord)
        entry = {
            "lord": md.lord, "start": md.start.date().isoformat(),
            "end": md.end.date().isoformat(), "ishta": ishta,
            "kashta": kashta, "verdict": verdict,
        }
        maha.append(entry)
        if md.start <= now < md.end:
            current_md = md
        if len(maha) >= count:
            break

    antardasha = []
    if current_md is not None:
        for ad in current_md.children:
            if ad.end < now:
                continue
            ishta, kashta, verdict = sbmod.period_phala(sb, ad.lord)
            antardasha.append({
                "lord": f"{current_md.lord}-{ad.lord}",
                "start": ad.start.date().isoformat(),
                "end": ad.end.date().isoformat(), "ishta": ishta,
                "kashta": kashta, "verdict": verdict,
            })
    return {"mahadasha": maha, "antardasha": antardasha}


def upcoming_mahadashas(tree, now: dt.datetime, count: int = 6):
    """Return the running + next few Mahadashas for display."""
    out = []
    for md in tree:
        if md.end < now:
            continue
        out.append(md)
        if len(out) >= count:
            break
    return out


# ---------------------------------------------------------------------------
# JSON serialization (for the API)
# ---------------------------------------------------------------------------
def _reco(r):
    return {"title": r.title, "score": r.score, "drivers": r.drivers}


def _window(w):
    return {"chain": w.chain, "start": w.start.date().isoformat(),
            "end": w.end.date().isoformat(), "note": w.note}


def _remedy(r):
    return {"planet": r.planet, "reason": r.reason, "measures": r.measures}


def _varga(v):
    if v is None:
        return None
    return {
        "division": v.division, "name": v.name, "asc_sign": v.asc_sign,
        "asc_lord": v.asc_lord, "focus_house": v.focus_house,
        "focus_sign": v.focus_sign, "focus_lord": v.focus_lord,
        "planets_in_focus": v.planets_in_focus,
        "key_placements": v.key_placements, "vargottama": v.vargottama,
        "field_planets": v.field_planets, "strength": v.strength,
        "notes": v.notes,
    }


def _strength(ps):
    return {
        "planet": ps.planet, "rupas": ps.rupas, "required": ps.required,
        "ratio": ps.ratio, "sufficient": ps.sufficient,
        "ishta": ps.ishta, "kashta": ps.kashta, "benefic": ps.benefic,
        "sthana": ps.sthana, "dig": ps.dig, "kala": ps.kala,
        "cheshta": ps.cheshta, "naisargika": ps.naisargika, "drik": ps.drik,
        "total_virupa": ps.total_virupa, "speed": ps.speed,
        "retrograde": ps.retrograde, "declination": ps.declination,
        "motion": ps.motion, "sub": ps.sub,
    }


def _shadbala(sb):
    if sb is None:
        return None
    return {"ranking": sb.ranking,
            "planets": {p: _strength(ps) for p, ps in sb.planets.items()}}


def _bhava(bb):
    if bb is None:
        return None
    return {
        "ranking": bb.ranking,
        "houses": {h: {"house": s.house, "lord": s.lord, "rupas": s.rupas,
                       "bhavadhipati": s.bhavadhipati, "occupant": s.occupant,
                       "drishti": s.drishti, "total_virupa": s.total_virupa}
                   for h, s in bb.houses.items()},
    }


def report_to_dict(rep: AdviceReport) -> dict:
    """Convert an :class:`AdviceReport` into a JSON-serializable dict."""
    b = rep.birth
    return {
        "birth": {
            "name": b.name, "date": b.date.isoformat(),
            "time": b.time.strftime("%H:%M"), "place": b.place,
            "latitude": b.latitude, "longitude": b.longitude,
            "tz_offset_hours": b.tz_offset_hours,
        },
        "native": {"current_age": rep.current_age, "life_stage": rep.life_stage},
        "lagna": {
            "kp": {"sign": rep.kp_chart.asc_lordship.sign,
                   "sub_lord": rep.kp_chart.asc_lordship.sub_lord},
            "parashara": {"sign": rep.par_chart.asc_lordship.sign},
        },
        "current_dasha": {
            "mahadasha": rep.current.md, "antardasha": rep.current.ad,
            "pratyantardasha": rep.current.pd,
            "mahadasha_period": rep.current.md_period,
            "antardasha_period": rep.current.ad_period,
            "pratyantardasha_period": rep.current.pd_period,
        },
        "education": {
            "promised": rep.education.promised,
            "higher_education_likely": rep.education.higher_education_likely,
            "strength_summary": rep.education.strength_summary,
            "key_planets": rep.education.key_planets,
            "streams": [_reco(r) for r in rep.education.streams],
            "kp_notes": rep.education.kp_notes,
            "parashara_notes": rep.education.par_notes,
            "yogas": rep.education.yogas,
            "remedies": [_remedy(r) for r in rep.edu_remedies],
            "divisional_chart": _varga(rep.education.varga),
            "divisional_summary": rep.education.varga_summary,
            "shadbala_notes": rep.education.shadbala_notes,
        },
        "career": {
            "earning_rating": rep.career.earning_rating,
            "earning_explanation": rep.career.earning_explanation,
            "satisfaction_rating": rep.career.satisfaction_rating,
            "satisfaction_explanation": rep.career.satisfaction_explanation,
            "job_vs_business": rep.career.job_vs_business,
            "key_planets": rep.career.key_planets,
            "fields": [_reco(r) for r in rep.career.fields],
            "kp_notes": rep.career.kp_notes,
            "parashara_notes": rep.career.par_notes,
            "yogas": rep.career.yogas,
            "remedies": [_remedy(r) for r in rep.career_remedies],
            "divisional_chart": _varga(rep.career.varga),
            "divisional_summary": rep.career.varga_summary,
            "shadbala_notes": rep.career.shadbala_notes,
        },
        "transits": {
            "as_of": rep.transit.as_of.isoformat(),
            "sade_sati": rep.transit.sade_sati,
            "education_trigger": rep.transit.education_trigger,
            "career_trigger": rep.transit.career_trigger,
            "notes": rep.transit.notes,
            "positions": {
                p: {"sign": t.sign, "house_from_lagna": t.house_from_lagna,
                    "house_from_moon": t.house_from_moon,
                    "influences": t.influences_from_lagna}
                for p, t in rep.transit.positions.items()
            },
        },
        "faqs": [
            {"question": a.question, "verdict": a.verdict, "summary": a.summary,
             "kp_basis": a.kp_basis, "parashara_basis": a.parashara_basis,
             "timeline": [_window(w) for w in a.timeline]}
            for a in rep.faqs
        ],
        "shadbala": _shadbala(rep.shadbala),
        "bhava_bala": _bhava(rep.bhava_bala),
        "ishta_ranking": rep.ishta_ranking,
        "phala_timeline": rep.phala_timeline,
        "best_periods": {
            "education": rep.education_best,
            "career": rep.career_best,
        },
    }
