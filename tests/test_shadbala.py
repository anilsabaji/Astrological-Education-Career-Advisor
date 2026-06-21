"""Shadbala (six-fold strength) and its use of speed, direction & declination."""

import datetime as dt

from astro_adviser import constants as C
from astro_adviser import shadbala as sb
from astro_adviser.ephemeris import compute_chart


def test_ephemeris_has_speed_and_declination(par_chart):
    for p in par_chart.planets.values():
        assert -30 <= p.declination <= 30           # within obliquity + latitude
    # Saturn is retrograde in the reference chart (negative speed).
    assert par_chart.planets[C.SATURN].speed < 0
    assert par_chart.planets[C.SATURN].retrograde
    # Moon is the fastest body.
    assert par_chart.planets[C.MOON].speed > 10


def test_shadbala_seven_planets(par_chart):
    res = sb.compute_shadbala(par_chart)
    assert set(res.planets.keys()) == set(sb.SB_PLANETS)   # 7 grahas, no nodes
    assert len(res.ranking) == 7


def test_uccha_bala_exaltation_and_debilitation():
    # Jupiter exalted at Cancer 5 deg -> near max Uccha Bala (60).
    exalt_lon = C.SIGNS.index("Cancer") * 30 + 5
    assert sb.uccha_bala(C.JUPITER, exalt_lon) > 59
    # At debilitation (opposite point) -> ~0.
    assert sb.uccha_bala(C.JUPITER, (exalt_lon + 180) % 360) < 1


def test_naisargika_order():
    # Sun strongest, Saturn weakest naturally.
    assert sb.NAISARGIKA[C.SUN] == 60.0
    assert sb.NAISARGIKA[C.SATURN] < sb.NAISARGIKA[C.MOON]


def test_retrograde_gives_max_cheshta(par_chart):
    res = sb.compute_shadbala(par_chart)
    # Saturn is retrograde -> Cheshta Bala should be at the maximum (60).
    assert res.planets[C.SATURN].cheshta == 60.0


def test_luminary_cheshta_rules(par_chart):
    res = sb.compute_shadbala(par_chart)
    # Sun's cheshta == its ayana bala; Moon's == its paksha bala.
    assert abs(res.planets[C.SUN].cheshta - res.planets[C.SUN].sub["ayana"]) < 0.2
    assert abs(res.planets[C.MOON].cheshta - res.planets[C.MOON].sub["paksha"]) < 0.2


def test_ayana_bala_uses_declination():
    # North-preferring planet with high north declination -> high ayana bala.
    high = sb._ayana_bala(C.SUN, 23.0)
    low = sb._ayana_bala(C.SUN, -23.0)
    assert high > 55 and low < 5


def test_vara_bala_weekday():
    # 15 Aug 1990 was a Wednesday -> Mercury (the weekday lord) gets Vara bala.
    ch = compute_chart(dt.datetime(1990, 8, 15, 10, 30), 28.6139, 77.2090, 5.5,
                       system="Parashara")
    res = sb.compute_shadbala(ch)
    assert res.planets[C.MERCURY].sub["vara"] == 45.0


def test_rupas_and_sufficiency_reasonable(par_chart):
    res = sb.compute_shadbala(par_chart)
    for ps in res.planets.values():
        assert 2.0 <= ps.rupas <= 12.0          # realistic Shadbala range
        assert ps.required > 0
        assert isinstance(ps.sufficient, bool)
        assert isinstance(ps.benefic, bool)


def test_strength_factor_bounds(par_chart):
    res = sb.compute_shadbala(par_chart)
    for p in sb.SB_PLANETS:
        f = sb.strength_factor(res, p)
        assert 0.6 <= f <= 1.4
    # node returns neutral factor
    assert sb.strength_factor(res, C.RAHU) == 1.0


def test_status_line_mentions_motion_and_declination(par_chart):
    res = sb.compute_shadbala(par_chart)
    line = sb.status_line(res, C.SATURN)
    assert "Retrograde" in line and "declination" in line and "rupas" in line


def test_advice_uses_shadbala(kp_chart, par_chart):
    from astro_adviser import advice
    res = sb.compute_shadbala(par_chart)
    ea = advice.advise_education(kp_chart, par_chart, sb=res)
    ca = advice.advise_career(kp_chart, par_chart, sb=res)
    assert ea.shadbala is res and ea.shadbala_notes
    assert ca.shadbala is res and ca.shadbala_notes
    # every note references Shadbala rupas
    assert all("rupas" in n or "strongest" in n for n in ca.shadbala_notes)


def test_bhava_bala(par_chart):
    res = sb.compute_shadbala(par_chart)
    bb = sb.compute_bhava_bala(par_chart, res)
    assert len(bb.houses) == 12
    assert len(bb.ranking) == 12
    for h in range(1, 13):
        s = bb.houses[h]
        assert s.lord in C.PLANETS
        assert 2.0 <= s.rupas <= 16.0
        # bhavadhipati equals the house lord's total Shadbala
        assert abs(s.bhavadhipati - res.planets[s.lord].total_virupa) < 0.2
    # ranking sorted by rupas descending
    rupas = [bb.houses[h].rupas for h in bb.ranking]
    assert rupas == sorted(rupas, reverse=True)


def test_group_strength_and_label(par_chart):
    res = sb.compute_shadbala(par_chart)
    bb = sb.compute_bhava_bala(par_chart, res)
    edu = bb.group_strength([4, 5, 9])
    car = bb.group_strength([2, 10, 11])
    assert edu > 0 and car > 0
    assert sb.house_strength_label(9.5) == "very strong"
    assert sb.house_strength_label(7.5) == "strong"
    assert sb.house_strength_label(5.5) == "moderate"
    assert sb.house_strength_label(3.0) == "weak"


def test_period_phala_and_ishta_ranking(par_chart):
    res = sb.compute_shadbala(par_chart)
    ishta, kashta, verdict = sb.period_phala(res, C.JUPITER)
    assert ishta is not None and verdict
    # nodes have no shadbala -> variable verdict
    _, _, node_verdict = sb.period_phala(res, C.RAHU)
    assert "Variable" in node_verdict
    rank = sb.ishta_ranking(res)
    assert set(rank) == set(sb.SB_PLANETS)
    ishtas = [res.planets[p].ishta for p in rank]
    assert ishtas == sorted(ishtas, reverse=True)


def test_report_has_bhava_and_phala():
    import datetime as dt
    from astro_adviser.adviser import BirthData, build_report, report_to_dict
    b = BirthData(name="R", date=dt.date(1990, 8, 15), time=dt.time(10, 30),
                  latitude=28.6139, longitude=77.2090, tz_offset_hours=5.5)
    rep = build_report(b, now=dt.datetime(2026, 6, 20))
    assert rep.bhava_bala is not None
    assert rep.phala_timeline["mahadasha"]
    d = report_to_dict(rep)
    assert d["bhava_bala"]["ranking"]
    assert d["phala_timeline"]["mahadasha"]
    assert d["ishta_ranking"]


def test_best_periods_overlay():
    import datetime as dt
    from astro_adviser.adviser import BirthData, build_report, report_to_dict
    b = BirthData(name="R", date=dt.date(1990, 8, 15), time=dt.time(10, 30),
                  latitude=28.6139, longitude=77.2090, tz_offset_hours=5.5)
    rep = build_report(b, now=dt.datetime(2026, 6, 20))
    for rows in (rep.education_best, rep.career_best):
        assert rows
        for e in rows:
            assert e["quality"] in ("Prime", "Favourable", "Workable")
            assert e["chain"].count("-") == 2          # MD-AD-PD
            assert e["start"] < e["end"]
            assert e["md_lord"] in C.PLANETS or e["md_lord"] is None
            assert isinstance(e["age_start"], int) and e["life_stage"]
    # career windows must not start before working age (~16)
    assert all(e["age_start"] >= 15 for e in rep.career_best)
    d = report_to_dict(rep)
    assert d["best_periods"]["education"] and d["best_periods"]["career"]
    assert d["native"]["current_age"] >= 0 and d["native"]["life_stage"]


def test_age_aware_child_vs_adult():
    import datetime as dt
    from astro_adviser.adviser import BirthData, build_report
    child = BirthData(name="Kid", date=dt.date(2018, 5, 10), time=dt.time(9, 0),
                      latitude=19.07, longitude=72.87, tz_offset_hours=5.5)
    rep = build_report(child, now=dt.datetime(2026, 6, 20))
    assert rep.current_age == 8
    # a young child's career windows should begin at working age, not childhood
    assert min(e["age_start"] for e in rep.career_best) >= 16
