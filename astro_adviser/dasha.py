"""
Vimshottari Dasha engine (3 levels).

Levels produced:
  1. Mahadasha       (MD)  - major period
  2. Antardasha      (AD / Bhukti) - sub period
  3. Pratyantardasha (PD)  - sub-sub period

The dasha is anchored on the Moon's nakshatra at birth. The same Moon
longitude is used for both KP and Parashara dashas; the small ayanamsa
difference between the two systems can shift the balance slightly, so the
adviser computes the dasha tree per chart (KP chart and Parashara chart),
which keeps the two systems internally consistent.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import List, Optional

from . import constants as C
from .ephemeris import NAK_SPAN


@dataclass
class DashaPeriod:
    lord: str
    level: int                  # 1=MD, 2=AD, 3=PD
    start: dt.datetime
    end: dt.datetime
    children: List["DashaPeriod"] = field(default_factory=list)

    @property
    def label(self) -> str:
        return {1: "Mahadasha", 2: "Antardasha", 3: "Pratyantardasha"}[self.level]

    def duration_days(self) -> float:
        return (self.end - self.start).total_seconds() / 86400.0

    def contains(self, when: dt.datetime) -> bool:
        return self.start <= when < self.end

    def chain_string(self) -> str:
        return self.lord


def _add_years(start: dt.datetime, years: float) -> dt.datetime:
    return start + dt.timedelta(days=years * C.DAYS_PER_YEAR)


def _seq_from(lord: str) -> List[str]:
    """Vimshottari order starting at ``lord``."""
    i = C.VIMSHOTTARI_ORDER.index(lord)
    return [C.VIMSHOTTARI_ORDER[(i + k) % 9] for k in range(9)]


def moon_balance(moon_longitude: float):
    """
    Return ``(starting_lord, elapsed_fraction, balance_years)`` for the
    Moon longitude at birth.

    ``elapsed_fraction`` is how far the Moon has travelled through its
    nakshatra (0..1); the balance of the first Mahadasha is the remaining
    fraction of that lord's full period.
    """
    nak_index = int((moon_longitude % 360.0) // NAK_SPAN)
    lord = C.NAKSHATRA_LORDS[nak_index]
    offset = (moon_longitude % 360.0) - nak_index * NAK_SPAN
    elapsed_fraction = offset / NAK_SPAN
    full_years = C.VIMSHOTTARI_YEARS[lord]
    balance_years = full_years * (1.0 - elapsed_fraction)
    return lord, elapsed_fraction, balance_years


def _build_antardashas(md_lord: str, md_start: dt.datetime,
                       md_end: dt.datetime) -> List[DashaPeriod]:
    """Sub-periods within a Mahadasha, including the 3rd (PD) level."""
    md_years = C.VIMSHOTTARI_YEARS[md_lord]
    ads: List[DashaPeriod] = []
    cursor = md_start
    for ad_lord in _seq_from(md_lord):
        # AD duration is proportional: MD_years * AD_years / 120.
        ad_years = md_years * C.VIMSHOTTARI_YEARS[ad_lord] / C.TOTAL_VIMSHOTTARI_YEARS
        ad_end = _add_years(cursor, ad_years)
        ad = DashaPeriod(lord=ad_lord, level=2, start=cursor, end=ad_end)

        # Pratyantardashas within this AD.
        pd_cursor = cursor
        for pd_lord in _seq_from(ad_lord):
            pd_years = ad_years * C.VIMSHOTTARI_YEARS[pd_lord] / C.TOTAL_VIMSHOTTARI_YEARS
            pd_end = _add_years(pd_cursor, pd_years)
            ad.children.append(
                DashaPeriod(lord=pd_lord, level=3, start=pd_cursor, end=pd_end)
            )
            pd_cursor = pd_end
        ads.append(ad)
        cursor = ad_end
    return ads


def build_dasha_tree(moon_longitude: float, birth: dt.datetime,
                     span_years: int = 120) -> List[DashaPeriod]:
    """
    Build the full Vimshottari Mahadasha list (each with AD and PD children),
    starting at birth and covering ``span_years``.
    """
    start_lord, elapsed, balance = moon_balance(moon_longitude)

    tree: List[DashaPeriod] = []
    # First MD starts before birth; we clamp its visible start to birth but
    # keep correct boundaries for the running period.
    full_first = C.VIMSHOTTARI_YEARS[start_lord]
    md_true_start = _add_years(birth, -(full_first - balance))

    cursor_lord_index = C.VIMSHOTTARI_ORDER.index(start_lord)
    cursor = md_true_start
    total = 0.0
    while total < span_years + full_first:
        lord = C.VIMSHOTTARI_ORDER[cursor_lord_index % 9]
        md_years = C.VIMSHOTTARI_YEARS[lord]
        md_end = _add_years(cursor, md_years)
        md = DashaPeriod(lord=lord, level=1, start=cursor, end=md_end)
        md.children = _build_antardashas(lord, cursor, md_end)
        tree.append(md)
        cursor = md_end
        total += md_years
        cursor_lord_index += 1
    return tree


def find_running(tree: List[DashaPeriod], when: dt.datetime):
    """
    Find the running MD / AD / PD for a given moment.
    Returns ``(md, ad, pd)`` (any may be None if out of range).
    """
    md = ad = pd = None
    for m in tree:
        if m.contains(when):
            md = m
            for a in m.children:
                if a.contains(when):
                    ad = a
                    for p in a.children:
                        if p.contains(when):
                            pd = p
                            break
                    break
            break
    return md, ad, pd


def periods_where(tree: List[DashaPeriod], lords_of_interest, start: dt.datetime,
                  end: dt.datetime, level: int = 2):
    """
    Collect periods (down to ``level``) between ``start`` and ``end`` whose
    lord is in ``lords_of_interest``. Used by the FAQ engine to find favorable
    windows (e.g. dasha of education/career significators).

    Returns a list of (md, ad, pd_or_None) tuples ordered chronologically.
    """
    out = []
    loi = set(lords_of_interest)
    for md in tree:
        if md.end < start or md.start > end:
            continue
        if level == 1:
            if md.lord in loi:
                out.append((md, None, None))
            continue
        for ad in md.children:
            if ad.end < start or ad.start > end:
                continue
            if level == 2:
                if md.lord in loi or ad.lord in loi:
                    out.append((md, ad, None))
                continue
            for pd in ad.children:
                if pd.end < start or pd.start > end:
                    continue
                if md.lord in loi or ad.lord in loi or pd.lord in loi:
                    out.append((md, ad, pd))
    return out


def format_period(md: Optional[DashaPeriod], ad: Optional[DashaPeriod] = None,
                  pd: Optional[DashaPeriod] = None) -> str:
    """Human-readable 'MD-AD-PD' chain with dates."""
    parts = []
    if md:
        parts.append(md.lord)
    if ad:
        parts.append(ad.lord)
    if pd:
        parts.append(pd.lord)
    chain = "-".join(parts)
    last = pd or ad or md
    if last is None:
        return chain
    return f"{chain} ({last.start.date()} to {last.end.date()})"
