"""Divisional chart (varga) math and analysis."""

from astro_adviser import constants as C
from astro_adviser import varga
from astro_adviser import parashara as par


# ---- sign formulae --------------------------------------------------------
def test_navamsa_boundaries():
    assert varga.navamsa_sign(0.0) == "Aries"       # movable -> itself
    assert varga.navamsa_sign(30.0) == "Capricorn"  # fixed -> 9th
    assert varga.navamsa_sign(60.0) == "Libra"      # dual -> 5th


def test_dasamsa_boundaries():
    assert varga.dasamsa_sign(0.0) == "Aries"       # odd -> itself
    assert varga.dasamsa_sign(30.0) == "Capricorn"  # even -> 9th
    # 10th dasamsa of Aries (27-30 deg) is the 10th sign from Aries = Capricorn.
    assert varga.dasamsa_sign(29.5) == "Capricorn"


def test_siddhamsa_boundaries():
    # D-24: odd signs count from Leo, even from Cancer; each part = 1.25 deg.
    assert varga.siddhamsa_sign(0.0) == "Leo"
    assert varga.siddhamsa_sign(30.0) == "Cancer"
    assert varga.siddhamsa_sign(1.3) == "Virgo"     # 2nd part of Aries -> Leo+1


def test_divisional_sign_dispatch():
    assert varga.divisional_sign(0.0, 1) == "Aries"
    assert varga.divisional_sign(30.0, 9) == "Capricorn"
    assert varga.divisional_sign(0.0, 24) == "Leo"


def test_each_varga_uses_valid_signs():
    for d in (9, 10, 24):
        for deg in range(0, 360, 1):
            assert varga.divisional_sign(float(deg), d) in C.SIGNS


# ---- chart builder --------------------------------------------------------
def test_build_varga_structure(par_chart):
    for d in (9, 10, 24):
        v = varga.build_varga(par_chart, d)
        assert v.division == d
        assert v.asc_sign in C.SIGNS
        assert len(v.house_signs) == 12
        assert len(set(v.house_signs)) == 12       # whole-sign: 12 distinct
        for p in v.planets.values():
            assert 1 <= p.house <= 12
            assert p.sign in C.SIGNS
        # the ascendant sign occupies house 1
        assert v.sign_of_house(1) == v.asc_sign


def test_vargottama_consistency(par_chart):
    vargo = varga.vargottama_planets(par_chart)
    d9 = varga.build_varga(par_chart, 9)
    for name in vargo:
        assert par_chart.planets[name].sign == d9.planets[name].sign


# ---- analysis integration -------------------------------------------------
def test_dasamsa_analysis(par_chart):
    a = par.analyse_dasamsa(par_chart)
    assert a.division == 10
    assert a.focus_house == 10
    assert a.focus_lord in C.PLANETS
    assert 0.0 <= a.strength <= 1.0
    assert a.field_planets
    assert a.notes


def test_siddhamsa_analysis(par_chart):
    a = par.analyse_siddhamsa(par_chart)
    assert a.division == 24
    assert C.MERCURY in a.key_placements and C.JUPITER in a.key_placements
    assert 1 <= a.key_placements[C.MERCURY] <= 12
    assert 0.0 <= a.strength <= 1.0
    assert a.field_planets


def test_judge_results_carry_varga(par_chart):
    edu = par.judge_education(par_chart)
    car = par.judge_career(par_chart)
    assert edu.varga is not None and edu.varga.division == 24
    assert car.varga is not None and car.varga.division == 10


def test_advice_uses_varga(kp_chart, par_chart):
    from astro_adviser import advice
    ea = advice.advise_education(kp_chart, par_chart)
    ca = advice.advise_career(kp_chart, par_chart)
    assert ea.varga and "D-24" in ea.varga_summary
    assert ca.varga and "D-10" in ca.varga_summary
