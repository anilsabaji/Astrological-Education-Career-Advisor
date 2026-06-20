"""Chart computation, lordships and KP sub-lord machinery."""

from astro_adviser import constants as C
from astro_adviser.ephemeris import (NAK_SPAN, compute_chart, lordships,
                                      norm360, _subdivide)


def test_norm360():
    assert norm360(370) == 10
    assert norm360(-10) == 350
    assert norm360(0) == 0


def test_lordship_basic():
    # 0 deg = start of Aries / Ashwini / star-lord Ketu.
    L = lordships(0.0)
    assert L.sign == "Aries"
    assert L.sign_lord == C.MARS
    assert L.nakshatra == "Ashwini"
    assert L.star_lord == C.KETU
    assert L.pada == 1
    # First sub of Ashwini is also Ketu (sequence starts at the star lord).
    assert L.sub_lord == C.KETU


def test_subdivision_proportional():
    # Divide a nakshatra starting at Ketu; the first sub spans 7/120 of it.
    lord, start, length = _subdivide(0.0, NAK_SPAN, C.KETU)
    assert lord == C.KETU
    assert abs(length - NAK_SPAN * 7 / 120) < 1e-9
    # A point just past the Ketu sub should fall in Venus (next in order).
    lord2, _, _ = _subdivide(length + 1e-6, NAK_SPAN, C.KETU)
    assert lord2 == C.VENUS


def test_sublord_sequence_covers_nakshatra():
    # Sub-lords across a nakshatra must follow the Vimshottari order from the
    # star lord and total the 9 lords.
    seen = []
    star = C.NAKSHATRA_LORDS[0]  # Ketu
    step = NAK_SPAN / 900.0
    pos = 0.0
    while pos < NAK_SPAN:
        sub = lordships(pos).sub_lord
        if not seen or seen[-1] != sub:
            seen.append(sub)
        pos += step
    start_idx = C.VIMSHOTTARI_ORDER.index(star)
    expected = [C.VIMSHOTTARI_ORDER[(start_idx + i) % 9] for i in range(9)]
    assert seen == expected


def test_kp_vs_parashara_ayanamsa_close(kp_chart, par_chart):
    # KP (Krishnamurti) and Lahiri differ by only a few arc-minutes.
    assert abs(kp_chart.ayanamsa - par_chart.ayanamsa) < 0.2


def test_ketu_opposite_rahu(kp_chart):
    rahu = kp_chart.planets[C.RAHU].longitude
    ketu = kp_chart.planets[C.KETU].longitude
    assert abs(norm360(rahu - ketu) - 180.0) < 1e-6


def test_nodes_retrograde(kp_chart):
    assert kp_chart.planets[C.RAHU].retrograde
    assert kp_chart.planets[C.KETU].retrograde


def test_whole_sign_houses_are_contiguous(par_chart):
    # Parashara uses whole-sign houses: 12 distinct signs starting at the asc.
    assert len(set(par_chart.house_signs)) == 12
    asc_sign = par_chart.sign_of_house(1)
    assert C.SIGNS[(C.SIGNS.index(asc_sign) + 1) % 12] == par_chart.sign_of_house(2)


def test_all_planets_present(kp_chart):
    assert set(kp_chart.planets.keys()) == set(C.PLANETS)
    for p in kp_chart.planets.values():
        assert 1 <= p.house <= 12
        assert 0 <= p.longitude < 360
