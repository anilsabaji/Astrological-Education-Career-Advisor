"""
FAQ engine for education & career questions.

Each FAQ is answered the way an astrologer would:

1. A verdict (promise) from the KP cuspal sub-lord + significators, cross-checked
   with Parashara strength.
2. A TIMELINE built from the 3-level Vimshottari dasha - the windows when the
   Mahadasha / Antardasha / Pratyantardasha lords are the strong significators
   of the houses that must fructify for that event.

The same set of FAQs that astrologers are most often asked about education and
career is covered.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from . import constants as C
from . import dasha, kp, parashara as par
from .ephemeris import Chart


@dataclass
class TimelineWindow:
    chain: str                 # "MD-AD" or "MD-AD-PD"
    start: dt.datetime
    end: dt.datetime
    note: str


@dataclass
class FAQAnswer:
    question: str
    verdict: str
    summary: str
    timeline: List[TimelineWindow]
    kp_basis: str
    parashara_basis: str


# ---------------------------------------------------------------------------
# Core timing routine (KP dasha fructification)
# ---------------------------------------------------------------------------
def fructification_windows(kp_chart: Chart, tree, houses: List[int],
                           from_date: dt.datetime, horizon_years: int = 25,
                           max_windows: int = 4,
                           require_levels: int = 2) -> List[TimelineWindow]:
    """
    Find dasha windows when the running period lords are the strong KP
    significators of ``houses``.

    Following standard KP timing, an event fructifies in the conjoined
    Dasha-Bhukti-Antara (MD-AD-PD) when a MAJORITY of those three lords are
    significators of the relevant houses. ``require_levels`` is the minimum
    number of the three running lords (out of 3) that must be significators
    (default 2).
    """
    sig = set(kp.strong_significators(kp_chart, houses))
    end_date = from_date + dt.timedelta(days=horizon_years * 365.25)
    windows: List[TimelineWindow] = []

    for md in tree:
        if md.end < from_date or md.start > end_date:
            continue
        md_sig = md.lord in sig
        for ad in md.children:
            if ad.end < from_date or ad.start > end_date:
                continue
            ad_sig = ad.lord in sig
            for pd in ad.children:
                if pd.end < from_date or pd.start > end_date:
                    continue
                pd_sig = pd.lord in sig
                count = md_sig + ad_sig + pd_sig
                if count < require_levels:
                    continue
                quality = ("a precise, strongly favourable window"
                           if count == 3 else "a favourable window")
                windows.append(TimelineWindow(
                    chain=f"{md.lord}-{ad.lord}-{pd.lord}",
                    start=max(pd.start, from_date), end=pd.end,
                    note=(f"Dasha of {md.lord} (major), {ad.lord} (sub) and "
                          f"{pd.lord} (sub-sub): {count} of the 3 running lords "
                          f"are significators of houses {houses} - {quality}."),
                ))
                if len(windows) >= max_windows:
                    return windows
    return windows


def _verdict_from(promised: bool, strength: float) -> str:
    if promised and strength >= 0.6:
        return "Yes - clearly supported"
    if promised:
        return "Likely - supported with effort"
    if strength >= 0.6:
        return "Possible - the promise is mixed; timing and effort matter"
    return "Challenging - needs remedies and sustained effort"


# ---------------------------------------------------------------------------
# Context object passed to every FAQ handler
# ---------------------------------------------------------------------------
@dataclass
class FAQContext:
    kp_chart: Chart
    par_chart: Chart
    tree: list
    now: dt.datetime


# ---------------------------------------------------------------------------
# Individual FAQ handlers
# ---------------------------------------------------------------------------
def q_higher_education(ctx: FAQContext) -> FAQAnswer:
    k = kp.judge_education(ctx.kp_chart)
    p = par.judge_education(ctx.par_chart)
    he_csl = k.csl_findings[2]  # 9th CSL
    verdict = _verdict_from(k.higher_education_likely, p.strength_score)
    windows = fructification_windows(ctx.kp_chart, ctx.tree, [4, 9, 11],
                                     ctx.now - dt.timedelta(days=365 * 8),
                                     horizon_years=20)
    return FAQAnswer(
        question="Will I pursue / complete higher education?",
        verdict=verdict,
        summary=("Higher education is read from the 4th (schooling), 9th (higher "
                 "learning) and 11th (fulfilment) houses. "
                 + ("The chart supports advanced study. " if k.higher_education_likely
                    else "The chart gives moderate support; persistence is key. ")),
        timeline=windows,
        kp_basis=he_csl.note,
        parashara_basis=(f"Jupiter (higher-learning karaka) is "
                         f"{p.karaka_strength.get(C.JUPITER)}, Mercury is "
                         f"{p.karaka_strength.get(C.MERCURY)}; education strength "
                         f"score {p.strength_score}."),
    )


def q_best_study_time(ctx: FAQContext) -> FAQAnswer:
    windows = fructification_windows(ctx.kp_chart, ctx.tree, [4, 5, 11],
                                     ctx.now - dt.timedelta(days=365 * 10),
                                     horizon_years=22)
    return FAQAnswer(
        question="When is/was the most favourable time for my education?",
        verdict="Timing windows below",
        summary=("Study flourishes when the dasha lords signify the 4th, 5th and "
                 "11th houses. These are the strongest learning windows."),
        timeline=windows,
        kp_basis=("Periods chosen are dashas of the strong significators of "
                  "houses 4 (study), 5 (intellect) and 11 (success)."),
        parashara_basis=("Cross-check with Mercury / Jupiter sub-periods, which "
                         "reinforce concentration and results."),
    )


def q_study_abroad(ctx: FAQContext) -> FAQAnswer:
    # Abroad education: 9 (long journeys / higher study) + 12 (foreign lands) + 4.
    abroad_csl = kp.analyse_csl(ctx.kp_chart, 9, [9, 12, 3], [4, 8])
    foreign_link = 12 in kp.houses_signified_by(ctx.kp_chart,
                                                kp.cuspal_sub_lord(ctx.kp_chart, 9))
    verdict = "Likely" if foreign_link else "Only with a strong foreign dasha"
    windows = fructification_windows(ctx.kp_chart, ctx.tree, [9, 12],
                                     ctx.now - dt.timedelta(days=365 * 5),
                                     horizon_years=18)
    return FAQAnswer(
        question="Will I study abroad / in a foreign place?",
        verdict=verdict,
        summary=("Foreign education needs the 9th (higher study, distant places) "
                 "linked to the 12th (foreign residence). "
                 + ("Such a link is present. " if foreign_link
                    else "The link is weak, so it would need a strong 9th/12th dasha. ")),
        timeline=windows,
        kp_basis=abroad_csl.note,
        parashara_basis=("Check the 12th lord, 9th lord and Rahu - Rahu connected to "
                         "9/12 strongly supports overseas study."),
    )


def q_competitive_exams(ctx: FAQContext) -> FAQAnswer:
    # Exams / selection: 6 (competition), 10/11 (success), 9 (luck).
    csl6 = kp.analyse_csl(ctx.kp_chart, 6, [6, 10, 11], [8, 12])
    windows = fructification_windows(ctx.kp_chart, ctx.tree, [6, 10, 11],
                                     ctx.now - dt.timedelta(days=365 * 3),
                                     horizon_years=15)
    return FAQAnswer(
        question="Will I clear competitive exams / get selected?",
        verdict="Yes during the windows below" if csl6.favorable else "Competitive; choose the windows",
        summary=("Winning competition is shown by the 6th (defeating rivals) with "
                 "the 10th/11th (success and reward)."),
        timeline=windows,
        kp_basis=csl6.note,
        parashara_basis=("A strong Mars / Saturn and a well-placed 6th lord help in "
                         "competitive and entrance examinations."),
    )


def q_when_job(ctx: FAQContext) -> FAQAnswer:
    k = kp.judge_career(ctx.kp_chart)
    csl10 = k.csl_findings[0]
    windows = fructification_windows(ctx.kp_chart, ctx.tree, [6, 10, 11],
                                     ctx.now - dt.timedelta(days=365 * 6),
                                     horizon_years=18)
    return FAQAnswer(
        question="When will I get a job / start earning?",
        verdict="Yes - in the windows below" if k.promised else "Possible with effort",
        summary=("A job / first income comes when the dasha lords signify the 6th "
                 "(service), 10th (profession) and 11th (income)."),
        timeline=windows,
        kp_basis=csl10.note,
        parashara_basis=("The 10th lord and 6th lord periods, and Saturn (karaka of "
                         "service), time the start of regular work."),
    )


def q_government_job(ctx: FAQContext) -> FAQAnswer:
    # Govt job: Sun (authority) + 10/6, often 1/10 with Sun/Saturn.
    sun_house = ctx.kp_chart.planets[C.SUN].house
    sun_sig = kp.houses_signified_by(ctx.kp_chart, C.SUN)
    govt_link = bool({6, 10} & sun_sig)
    verdict = "Supported" if govt_link else "Private sector is more likely"
    windows = fructification_windows(ctx.kp_chart, ctx.tree, [1, 6, 10],
                                     ctx.now - dt.timedelta(days=365 * 6),
                                     horizon_years=18)
    return FAQAnswer(
        question="Will I get a government / public-sector job?",
        verdict=verdict,
        summary=("Government service is read from the Sun (authority) connected to "
                 "the 6th/10th houses. "
                 + ("The Sun links to service/profession here. " if govt_link
                    else "The Sun is not strongly tied to service here. ")),
        timeline=windows,
        kp_basis=(f"Sun is in house {sun_house} and signifies houses "
                  f"{sorted(sun_sig)}; a 6/10 link favours government work."),
        parashara_basis=("A strong Sun (exalted/own/with 10th lord) and Saturn for "
                         "discipline are the classic markers of government service."),
    )


def q_job_or_business(ctx: FAQContext):
    from .advice import advise_career
    ca = advise_career(ctx.kp_chart, ctx.par_chart)
    windows = fructification_windows(ctx.kp_chart, ctx.tree, [7, 10, 11],
                                     ctx.now - dt.timedelta(days=365 * 4),
                                     horizon_years=18)
    return FAQAnswer(
        question="Should I do a job or business?",
        verdict=ca.job_vs_business.split(".")[0],
        summary=ca.job_vs_business,
        timeline=windows,
        kp_basis=("Service is tied to the 6th house; business / self-employment to "
                  "the 7th house. The 10th cuspal sub-lord's links decide the mode."),
        parashara_basis=(f"Parashara reading of the 10th sign, planets in the 10th "
                         f"and the 6th vs 7th lord strength."),
    )


def q_promotion_growth(ctx: FAQContext) -> FAQAnswer:
    windows = fructification_windows(ctx.kp_chart, ctx.tree, [10, 11, 2],
                                     ctx.now - dt.timedelta(days=180),
                                     horizon_years=15)
    return FAQAnswer(
        question="When will I get promotion / career growth?",
        verdict="Growth windows below",
        summary=("Rise in status and salary comes in dashas of the 10th (status), "
                 "11th (gains) and 2nd (income) significators."),
        timeline=windows,
        kp_basis=("Windows are the conjoined dasha of the strong significators of "
                  "houses 2, 10 and 11."),
        parashara_basis=("A Raja-yoga or Dhana-yoga planet's dasha typically brings "
                         "the most visible promotion."),
    )


def q_career_change(ctx: FAQContext) -> FAQAnswer:
    # Change of job/career: 5 (away from 10 = leaving job), 9 (change), 10.
    windows = fructification_windows(ctx.kp_chart, ctx.tree, [9, 10, 6],
                                     ctx.now - dt.timedelta(days=180),
                                     horizon_years=15)
    return FAQAnswer(
        question="When is a good time to change job / switch careers?",
        verdict="Change windows below",
        summary=("A change of work is favoured when the dasha activates the 9th "
                 "(change, fortune) along with the 10th and 6th (new work)."),
        timeline=windows,
        kp_basis=("Transition periods are the dashas of significators of the 6th, "
                  "9th and 10th houses; the 12th of the old job (i.e. 9th) opening "
                  "marks the switch."),
        parashara_basis=("Movement of the 10th lord by transit/dasha and activation "
                         "of the 9th indicate a constructive change."),
    )


def q_foreign_career(ctx: FAQContext) -> FAQAnswer:
    csl10 = kp.cuspal_sub_lord(ctx.kp_chart, 10)
    sig10 = kp.houses_signified_by(ctx.kp_chart, csl10)
    foreign = bool({7, 12} & sig10)
    verdict = "Likely" if foreign else "Mainly domestic, with travel"
    windows = fructification_windows(ctx.kp_chart, ctx.tree, [7, 10, 12],
                                     ctx.now - dt.timedelta(days=365 * 4),
                                     horizon_years=18)
    return FAQAnswer(
        question="Will I have a foreign career / settle abroad for work?",
        verdict=verdict,
        summary=("Working abroad needs the 10th/7th (career, others' lands) tied to "
                 "the 12th (foreign residence). "
                 + ("That link is present. " if foreign else "That link is weak. ")),
        timeline=windows,
        kp_basis=(f"10th cuspal sub-lord {csl10} signifies houses {sorted(sig10)}; "
                  f"a 12th/7th link points to overseas work."),
        parashara_basis=("Rahu, the 12th lord and the 7th lord connected to the 10th "
                         "support a foreign or multinational career."),
    )


def q_earning_growth(ctx: FAQContext) -> FAQAnswer:
    windows = fructification_windows(ctx.kp_chart, ctx.tree, [2, 11],
                                     ctx.now - dt.timedelta(days=180),
                                     horizon_years=15)
    return FAQAnswer(
        question="When will my income / wealth increase?",
        verdict="Wealth windows below",
        summary=("Income peaks in dashas of the 2nd (accumulated wealth) and 11th "
                 "(gains and recurring income) significators."),
        timeline=windows,
        kp_basis=("Windows are dashas of the strong significators of the 2nd and "
                  "11th houses."),
        parashara_basis=("Dasha of a Dhana-yoga planet, or of Jupiter/Venus when "
                         "well placed, brings the clearest financial growth."),
    )


# Registry of FAQs (key -> handler).
FAQ_REGISTRY = {
    # Education
    "higher_education": q_higher_education,
    "best_study_time": q_best_study_time,
    "study_abroad": q_study_abroad,
    "competitive_exams": q_competitive_exams,
    # Career
    "when_job": q_when_job,
    "government_job": q_government_job,
    "job_or_business": q_job_or_business,
    "promotion_growth": q_promotion_growth,
    "career_change": q_career_change,
    "foreign_career": q_foreign_career,
    "earning_growth": q_earning_growth,
}

FAQ_TITLES = {
    "higher_education": "Will I pursue / complete higher education?",
    "best_study_time": "When is the most favourable time for my education?",
    "study_abroad": "Will I study abroad?",
    "competitive_exams": "Will I clear competitive exams / get selected?",
    "when_job": "When will I get a job?",
    "government_job": "Will I get a government job?",
    "job_or_business": "Should I do a job or business?",
    "promotion_growth": "When will I get promotion / career growth?",
    "career_change": "When is a good time to change job / switch careers?",
    "foreign_career": "Will I have a foreign career / settle abroad?",
    "earning_growth": "When will my income / wealth increase?",
}


def answer_faq(key: str, ctx: FAQContext) -> FAQAnswer:
    handler = FAQ_REGISTRY.get(key)
    if handler is None:
        raise KeyError(f"Unknown FAQ key: {key}")
    return handler(ctx)


def answer_all(ctx: FAQContext) -> List[FAQAnswer]:
    return [answer_faq(k, ctx) for k in FAQ_REGISTRY]
