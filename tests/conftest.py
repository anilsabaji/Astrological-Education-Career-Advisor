"""Shared fixtures: a deterministic reference chart for all tests."""

import datetime as dt

import pytest

from astro_adviser.adviser import BirthData, build_report
from astro_adviser.ephemeris import compute_chart

# A fixed birth used across the suite (New Delhi, 15 Aug 1990, 10:30 IST).
REF_DT = dt.datetime(1990, 8, 15, 10, 30)
REF_LAT, REF_LON, REF_TZ = 28.6139, 77.2090, 5.5
# A fixed "now" so dasha/transit assertions are stable.
REF_NOW = dt.datetime(2026, 6, 20)


@pytest.fixture
def kp_chart():
    return compute_chart(REF_DT, REF_LAT, REF_LON, REF_TZ, system="KP")


@pytest.fixture
def par_chart():
    return compute_chart(REF_DT, REF_LAT, REF_LON, REF_TZ, system="Parashara")


@pytest.fixture
def birth():
    return BirthData(name="Ref", date=REF_DT.date(), time=REF_DT.time(),
                     latitude=REF_LAT, longitude=REF_LON, tz_offset_hours=REF_TZ,
                     place="New Delhi")


@pytest.fixture
def report(birth):
    return build_report(birth, now=REF_NOW)
