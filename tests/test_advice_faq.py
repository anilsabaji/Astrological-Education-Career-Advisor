"""Advice fusion, FAQ engine, remedies and transits."""

import datetime as dt

from astro_adviser import advice, faq, remedies, transits
from astro_adviser import constants as C
from .conftest import REF_NOW


def test_education_advice(kp_chart, par_chart):
    a = advice.advise_education(kp_chart, par_chart)
    assert a.streams and len(a.streams) <= 6
    assert all(r.title for r in a.streams)
    # streams are ranked in non-increasing score order
    scores = [r.score for r in a.streams]
    assert scores == sorted(scores, reverse=True)


def test_career_advice(kp_chart, par_chart):
    a = advice.advise_career(kp_chart, par_chart)
    assert a.fields and len(a.fields) <= 6
    assert "earning" in a.earning_explanation.lower()
    assert a.satisfaction_rating
    assert a.job_vs_business


def test_all_faqs_answered(kp_chart, par_chart):
    tree_src = par_chart.planets[C.MOON].longitude
    from astro_adviser import dasha
    tree = dasha.build_dasha_tree(tree_src, dt.datetime(1990, 8, 15, 10, 30))
    ctx = faq.FAQContext(kp_chart, par_chart, tree, REF_NOW)
    answers = faq.answer_all(ctx)
    assert len(answers) == len(faq.FAQ_REGISTRY) == 11
    for a in answers:
        assert a.question and a.verdict
        # every timeline window must be chronologically valid
        for w in a.timeline:
            assert w.start < w.end
            assert w.chain.count("-") == 2  # MD-AD-PD


def test_faq_windows_within_horizon(kp_chart, par_chart):
    from astro_adviser import dasha
    tree = dasha.build_dasha_tree(par_chart.planets[C.MOON].longitude,
                                  dt.datetime(1990, 8, 15, 10, 30))
    ctx = faq.FAQContext(kp_chart, par_chart, tree, REF_NOW)
    a = faq.answer_faq("earning_growth", ctx)
    assert a.timeline  # the fixed fix: earning growth must yield windows
    for w in a.timeline:
        assert w.end > REF_NOW - dt.timedelta(days=400)


def test_remedies_detect_weakness():
    from astro_adviser.ephemeris import compute_chart
    kpc = compute_chart(dt.datetime(1995, 4, 1, 9, 0), 19.07, 72.87, 5.5, system="KP")
    parc = compute_chart(dt.datetime(1995, 4, 1, 9, 0), 19.07, 72.87, 5.5,
                         system="Parashara")
    recs = remedies.remedies_for(parc, kpc, "career")
    planets = {r.planet for r in recs}
    # Mercury is debilitated in this chart -> must be flagged.
    assert C.MERCURY in planets
    for r in recs:
        assert "mantra" in r.measures and "charity" in r.measures


def test_remedies_never_empty(par_chart, kp_chart):
    for dom in ("education", "career"):
        recs = remedies.remedies_for(par_chart, kp_chart, dom)
        assert recs  # always at least a supportive remedy


def test_transit_engine(par_chart):
    rep = transits.build_transit_report(par_chart, REF_NOW)
    # Saturn is in Pisces (sidereal) on 2026-06-20 - a real-world anchor.
    assert rep.positions[C.SATURN].sign == "Pisces"
    for p, t in rep.positions.items():
        assert 1 <= t.house_from_lagna <= 12
        assert 1 <= t.house_from_moon <= 12
    assert rep.education_trigger and rep.career_trigger and rep.sade_sati
