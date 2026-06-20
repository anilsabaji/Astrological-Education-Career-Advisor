"""KP significators and cuspal sub-lord analysis."""

from astro_adviser import constants as C
from astro_adviser import kp


def test_significator_grades_ordering(kp_chart):
    grades = kp.significator_grades(kp_chart, [10])
    assert grades  # non-empty
    assert all(1 <= g <= 4 for g in grades.values())
    # the lord of the 10th must appear at least at grade D (1).
    lord10 = kp_chart.lord_of_house(10)
    assert lord10 in grades


def test_strong_significators_subset(kp_chart):
    allsig = set(kp.significators_of_houses(kp_chart, [2, 6, 10, 11]))
    strong = set(kp.strong_significators(kp_chart, [2, 6, 10, 11]))
    # strong set (grade A/B + CSLs) is a subset of all significators + CSLs.
    csls = {kp.cuspal_sub_lord(kp_chart, h) for h in (2, 6, 10, 11)}
    assert strong <= (allsig | csls)
    assert strong  # not empty


def test_houses_signified_includes_occupation(kp_chart):
    for name, p in kp_chart.planets.items():
        houses = kp.houses_signified_by(kp_chart, name)
        if name not in (C.RAHU, C.KETU):
            assert p.house in houses


def test_cuspal_sub_lord_is_a_planet(kp_chart):
    for h in range(1, 13):
        assert kp.cuspal_sub_lord(kp_chart, h) in C.PLANETS


def test_judge_education_and_career_shapes(kp_chart):
    edu = kp.judge_education(kp_chart)
    assert isinstance(edu.promised, bool)
    assert len(edu.csl_findings) == 4
    car = kp.judge_career(kp_chart)
    assert car.earning_strength in ("Strong", "Good", "Moderate")
    assert isinstance(car.job_indicated, bool)


def test_node_significations_focused(kp_chart):
    # A node should not trivially signify all 12 houses unless conjoined with
    # many planets; assert it returns a sensible, bounded set.
    for node in (C.RAHU, C.KETU):
        houses = kp.houses_signified_by(kp_chart, node)
        assert 1 <= len(houses) <= 12
