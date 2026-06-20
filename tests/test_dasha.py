"""Vimshottari dasha correctness."""

import datetime as dt

from astro_adviser import constants as C
from astro_adviser import dasha
from .conftest import REF_DT, REF_NOW


def test_vimshottari_total_is_120():
    assert sum(C.VIMSHOTTARI_YEARS.values()) == 120


def test_nakshatra_lords_cycle():
    # 27 nakshatras, 9 lords repeating; Ashwini -> Ketu, Bharani -> Venus.
    assert C.NAKSHATRA_LORDS[0] == C.KETU
    assert C.NAKSHATRA_LORDS[1] == C.VENUS
    assert C.NAKSHATRA_LORDS[3] == C.MOON      # Rohini
    assert len(C.NAKSHATRA_LORDS) == 27


def test_moon_balance_fraction():
    # Moon near 0 of a Ketu nakshatra -> almost full Ketu balance.
    lord, frac, bal = dasha.moon_balance(0.01)
    assert lord == C.KETU
    assert 0.0 <= frac < 0.01
    assert abs(bal - 7.0) < 0.05


def test_mahadasha_durations(par_chart):
    moon = par_chart.planets[C.MOON].longitude
    tree = dasha.build_dasha_tree(moon, REF_DT)
    for md in tree:
        expected = C.VIMSHOTTARI_YEARS[md.lord] * C.DAYS_PER_YEAR
        assert abs(md.duration_days() - expected) < 1.0


def test_antardasha_and_prati_sum_to_parent(par_chart):
    moon = par_chart.planets[C.MOON].longitude
    tree = dasha.build_dasha_tree(moon, REF_DT)
    md = tree[1]
    ad_sum = sum(a.duration_days() for a in md.children)
    assert abs(ad_sum - md.duration_days()) < 0.01
    ad0 = md.children[0]
    pd_sum = sum(p.duration_days() for p in ad0.children)
    assert abs(pd_sum - ad0.duration_days()) < 0.01
    # 9 antardashas, each with 9 pratyantardashas.
    assert len(md.children) == 9
    assert all(len(a.children) == 9 for a in md.children)


def test_running_period_three_levels(par_chart):
    moon = par_chart.planets[C.MOON].longitude
    tree = dasha.build_dasha_tree(moon, REF_DT)
    md, ad, pd = dasha.find_running(tree, REF_NOW)
    assert md and ad and pd
    assert md.contains(REF_NOW) and ad.contains(REF_NOW) and pd.contains(REF_NOW)
    # The reference chart is in Jupiter mahadasha in 2026.
    assert md.lord == C.JUPITER


def test_first_antardasha_lord_equals_md_lord(par_chart):
    moon = par_chart.planets[C.MOON].longitude
    tree = dasha.build_dasha_tree(moon, REF_DT)
    for md in tree:
        assert md.children[0].lord == md.lord
        assert md.children[0].children[0].lord == md.lord
