"""Parashara dignities, divisional charts and yogas."""

from astro_adviser import constants as C
from astro_adviser import parashara as par


def test_known_dignities(par_chart):
    dig = par.all_dignities(par_chart)
    # In the reference chart: Moon exalted (Taurus), Jupiter exalted (Cancer),
    # Mars in Moolatrikona (Aries).
    assert dig[C.MOON].state == "Exalted"
    assert dig[C.JUPITER].state == "Exalted"
    assert dig[C.MARS].state == "Moolatrikona"
    assert dig[C.MOON].score == 1.0


def test_exaltation_signs_consistent():
    # Debilitation sign is opposite the exaltation sign for each planet.
    for planet, (exsign, _deg) in C.EXALTATION.items():
        ex_idx = C.SIGNS.index(exsign)
        deb_idx = C.SIGNS.index(C.DEBILITATION[planet])
        assert (ex_idx - deb_idx) % 12 == 6


def test_debilitation_detected():
    # 1 Apr 1995 chart -> Mercury debilitated in Pisces.
    import datetime as dt
    from astro_adviser.ephemeris import compute_chart
    ch = compute_chart(dt.datetime(1995, 4, 1, 9, 0), 19.07, 72.87, 5.5,
                       system="Parashara")
    assert par.dignity_of(ch, C.MERCURY).state == "Debilitated"


def test_navamsa_movable_sign_starts_itself():
    # Aries (movable) 0 deg -> navamsa Aries.
    assert par.navamsa_sign(0.0) == "Aries"
    # Taurus (fixed) 0 deg (=30) -> navamsa Capricorn (9th from Taurus).
    assert par.navamsa_sign(30.0) == "Capricorn"


def test_dasamsa_odd_even_rule():
    # Aries (odd) 0 deg -> Aries; Taurus (even) 0 deg -> 9th sign = Capricorn.
    assert par.dasamsa_sign(0.0) == "Aries"
    assert par.dasamsa_sign(30.0) == "Capricorn"


def test_yogas_present(par_chart):
    yogas = {y.name for y in par.detect_yogas(par_chart)}
    # The reference chart has strong benefics -> at least one wealth/status yoga.
    assert any("Dhana" in n or "Raja" in n for n in yogas)


def test_career_judgement_fields(par_chart):
    res = par.judge_career(par_chart)
    assert res.tenth_sign in C.SIGNS
    assert res.job_lean in ("Job / service", "Business / self-employment",
                            "Both (job then independent work)")
    assert 0.0 <= res.wealth_score <= 1.0
