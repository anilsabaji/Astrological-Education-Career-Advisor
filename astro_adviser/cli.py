"""
Command-line interface for the Astro Adviser.

Example:
    python -m astro_adviser.cli --name "Asha" --date 1990-08-15 --time 10:30 \
        --lat 28.6139 --lon 77.2090 --tz 5.5
"""

from __future__ import annotations

import argparse
import datetime as dt

from .adviser import BirthData, build_report


def _print_header(text: str):
    print("\n" + "=" * 72)
    print(text)
    print("=" * 72)


def main(argv=None):
    ap = argparse.ArgumentParser(description="KP + Parashara education & career adviser")
    ap.add_argument("--name", default="Seeker")
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--time", required=True, help="HH:MM (24h local)")
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--tz", type=float, required=True, help="UTC offset in hours")
    ap.add_argument("--place", default="")
    args = ap.parse_args(argv)

    birth = BirthData(
        name=args.name,
        date=dt.datetime.strptime(args.date, "%Y-%m-%d").date(),
        time=dt.datetime.strptime(args.time, "%H:%M").time(),
        latitude=args.lat, longitude=args.lon, tz_offset_hours=args.tz,
        place=args.place,
    )
    rep = build_report(birth)

    _print_header(f"ASTRO ADVISER  -  {birth.name}")
    print(f"Born {birth.date} {args.time}  ({birth.place or f'{args.lat},{args.lon}'}) "
          f"UTC{args.tz:+g}")
    print(f"Age now: {rep.current_age} ({rep.life_stage})")
    print(f"KP Lagna: {rep.kp_chart.asc_lordship.sign} "
          f"(sub-lord {rep.kp_chart.asc_lordship.sub_lord})   "
          f"Parashara Lagna: {rep.par_chart.asc_lordship.sign}")

    _print_header("CURRENT VIMSHOTTARI DASHA (3 levels)")
    print(f"  Mahadasha      : {rep.current.md_period}")
    print(f"  Antardasha     : {rep.current.ad_period}")
    print(f"  Pratyantardasha: {rep.current.pd_period}")

    _print_header("EDUCATION GUIDANCE")
    print(f"  Promise: {'Strong' if rep.education.promised else 'Moderate'} | "
          f"Higher education: {'Likely' if rep.education.higher_education_likely else 'With effort'}")
    print(f"  {rep.education.strength_summary}")
    print("  Recommended streams:")
    for i, r in enumerate(rep.education.streams, 1):
        print(f"    {i}. {r.title}  (drivers: {', '.join(r.drivers)})")
    if rep.education.varga:
        v = rep.education.varga
        print(f"  Divisional chart ({v.name}): Lagna {v.asc_sign}, strength "
              f"{int(v.strength * 100)}%"
              + (f", vargottama: {', '.join(v.vargottama)}" if v.vargottama else ""))
        print(f"    {rep.education.varga_summary}")
    if rep.education.shadbala_notes:
        print("  Planetary strength (Shadbala):")
        for n in rep.education.shadbala_notes:
            print(f"    - {n}")

    _print_header("CAREER GUIDANCE")
    print(f"  Earning      : {rep.career.earning_rating}")
    print(f"  Satisfaction : {rep.career.satisfaction_rating}")
    print(f"  Job/Business : {rep.career.job_vs_business}")
    print("  Recommended fields:")
    for i, r in enumerate(rep.career.fields, 1):
        print(f"    {i}. {r.title}  (drivers: {', '.join(r.drivers)})")
    if rep.career.linked_fields:
        print("  Collective recommendation (education x career):")
        for l in rep.career.linked_fields:
            print(f"    - {l['title']}  [{l['education_field']} x {l['career_field']}]")
    if rep.career.varga:
        v = rep.career.varga
        print(f"  Divisional chart ({v.name}): Lagna {v.asc_sign}, 10th "
              f"{v.focus_sign} (lord {v.focus_lord}), strength {int(v.strength * 100)}%")
        print(f"    {rep.career.varga_summary}")
    if rep.yogas:
        print("  Yogas present: " + ", ".join(y.name for y in rep.yogas))
    if rep.career.shadbala_notes:
        print("  Planetary strength (Shadbala):")
        for n in rep.career.shadbala_notes:
            print(f"    - {n}")

    if rep.shadbala:
        _print_header("SHADBALA (SIX-FOLD PLANETARY STRENGTH)")
        print(f"  {'Planet':8} {'Rupas':>6} {'Req':>4} {'Ratio':>6} {'Suff':>5} "
              f"{'Ishta':>6} {'Motion':<28} Declination")
        for p in rep.shadbala.ranking:
            s = rep.shadbala.planets[p]
            decl = f"{abs(s.declination):.1f}{'N' if s.declination >= 0 else 'S'}"
            print(f"  {p:8} {s.rupas:6} {s.required:4} {s.ratio:6} "
                  f"{('yes' if s.sufficient else 'no'):>5} "
                  f"{('Ishta' if s.benefic else 'Kashta'):>6} {s.motion:<28} {decl}")

    if rep.bhava_bala:
        _print_header("BHAVA BALA (HOUSE STRENGTHS)")
        for h in rep.bhava_bala.ranking:
            s = rep.bhava_bala.houses[h]
            print(f"  House {s.house:<2} (lord {s.lord:8}): {s.rupas:5} rupas")

    if rep.phala_timeline:
        _print_header("ISHTA / KASHTA DASHA-PHALA TIMELINE")
        print("  Upcoming Mahadashas (benefic vs challenging periods):")
        for e in rep.phala_timeline["mahadasha"]:
            ik = (f"Ishta {e['ishta']} / Kashta {e['kashta']}"
                  if e["ishta"] is not None else "node")
            print(f"    {e['lord']:8} {e['start']} to {e['end']}  [{ik}]  {e['verdict']}")
        if rep.phala_timeline["antardasha"]:
            print("  Antardashas within the current Mahadasha:")
            for e in rep.phala_timeline["antardasha"]:
                print(f"    {e['lord']:18} {e['start']} to {e['end']}  {e['verdict']}")

    def _best_block(title, rows):
        print(f"  {title}:")
        for e in rows:
            age = (f"age {e['age_start']}" if e["age_start"] == e["age_end"]
                   else f"age {e['age_start']}-{e['age_end']}")
            print(f"    {e['chain']:22} {e['start']} to {e['end']}  ({age}, "
                  f"{e['life_stage']})  [{e['md_lord']} - {e['phala']}]  => {e['quality']}")

    if rep.education_best or rep.career_best:
        _print_header("BEST PERIODS (KP WINDOWS x DASHA PHALA, AGE-AWARE)")
        print(f"  Native is currently {rep.current_age} ({rep.life_stage}); "
              f"career windows are shown from working age.")
        _best_block("Education growth", rep.education_best)
        _best_block("Career growth", rep.career_best)

    _print_header("TRANSIT (GOCHAR) TRIGGERS")
    print(f"  As of {rep.transit.as_of}")
    for p, t in rep.transit.positions.items():
        print(f"    {p:8}: {t.sign:11} ({t.house_from_lagna}H Lagna / "
              f"{t.house_from_moon}H Moon)")
    print(f"  Education: {rep.transit.education_trigger}")
    print(f"  Career   : {rep.transit.career_trigger}")
    print(f"  Saturn/Moon: {rep.transit.sade_sati}")

    _print_header("REMEDIAL SUGGESTIONS (UPAYA)")
    print("  For education:")
    for r in rep.edu_remedies:
        print(f"    - {r.planet}: {r.reason}")
        print(f"        Mantra : {r.measures['mantra']}")
        print(f"        Charity: {r.measures['charity']}")
    print("  For career:")
    for r in rep.career_remedies:
        print(f"    - {r.planet}: {r.reason}")
        print(f"        Mantra : {r.measures['mantra']}")
        print(f"        Charity: {r.measures['charity']}")

    _print_header("FREQUENTLY ASKED QUESTIONS")
    for a in rep.faqs:
        print(f"\n  Q: {a.question}")
        print(f"     Verdict: {a.verdict}")
        for w in a.timeline[:3]:
            print(f"       - {w.chain}: {w.start.date()} to {w.end.date()}")

    print()


if __name__ == "__main__":
    main()
