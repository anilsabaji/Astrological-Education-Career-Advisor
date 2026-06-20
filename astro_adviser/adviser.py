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
from dataclasses import dataclass
from typing import List, Optional

from . import advice, dasha, faq, remedies, transits
from . import parashara as par
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

    education = advice.advise_education(kp_chart, par_chart)
    career = advice.advise_career(kp_chart, par_chart)

    ctx = faq.FAQContext(kp_chart, par_chart, tree, now)
    faqs = faq.answer_all(ctx)

    yogas = par.detect_yogas(par_chart)

    edu_remedies = remedies.remedies_for(par_chart, kp_chart, "education")
    career_remedies = remedies.remedies_for(par_chart, kp_chart, "career")
    transit_report = transits.build_transit_report(par_chart, now)

    return AdviceReport(
        birth=birth, kp_chart=kp_chart, par_chart=par_chart, dasha_tree=tree,
        current=current, education=education, career=career, faqs=faqs,
        yogas=yogas, edu_remedies=edu_remedies, career_remedies=career_remedies,
        transit=transit_report,
    )


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
    }
