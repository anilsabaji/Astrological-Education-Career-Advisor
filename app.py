"""
Astro Adviser - web application.

Run with:
    uvicorn app:app --host 0.0.0.0 --port 8000

Then open http://localhost:8000 , enter birth details and get the
KP + Parashara education & career advice with 3-level Vimshottari dasha
timelines and FAQ answers.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from astro_adviser import constants as C
from astro_adviser.cities import CITIES
from astro_adviser.adviser import (BirthData, build_report, report_to_dict,
                                    upcoming_mahadashas)
from astro_adviser.ephemeris import norm360
from astro_adviser import faq as faqmod
from astro_adviser import parashara as par

BASE = Path(__file__).resolve().parent
app = FastAPI(title="Astro Adviser - Education & Career (KP + Parashara)")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE / "templates"))


def _svg_bars(items, maxval, marker=None, width=580, row_h=26):
    """Render a horizontal bar chart as an inline SVG string.
    items: list of dicts {label, value, color}. marker: optional value drawn
    as a vertical reference line (e.g. the required Shadbala)."""
    label_w, val_w, pad = 78, 46, 8
    bar_area = width - label_w - val_w - pad
    height = len(items) * row_h + 8
    maxval = maxval or 1
    parts = [f'<svg viewBox="0 0 {width} {height}" class="bar-svg" '
             f'role="img" preserveAspectRatio="xMinYMin meet">']
    if marker is not None:
        mx = label_w + bar_area * min(marker / maxval, 1.0)
        parts.append(f'<line x1="{mx:.1f}" y1="2" x2="{mx:.1f}" y2="{height-6}" '
                     f'class="bar-marker"/>')
    for i, it in enumerate(items):
        y = i * row_h + 4
        w = max(2, bar_area * min(it["value"] / maxval, 1.0))
        parts.append(
            f'<text x="0" y="{y+15}" class="bar-label">{it["label"]}</text>'
            f'<rect x="{label_w}" y="{y+3}" width="{w:.1f}" height="{row_h-9}" '
            f'rx="3" fill="{it["color"]}"/>'
            f'<text x="{label_w + w + 5:.1f}" y="{y+15}" class="bar-val">{it["value"]}</text>')
    parts.append('</svg>')
    return "".join(parts)


def _shadbala_svg(rows):
    items = []
    for s in rows:
        color = ("#34c98a" if (s.sufficient and s.benefic)
                 else "#e8a13a" if s.sufficient else "#e8607a")
        items.append({"label": s.planet, "value": s.rupas, "color": color})
    maxv = max([s.rupas for s in rows] + [1])
    avg_req = sum(s.required for s in rows) / len(rows)
    return _svg_bars(items, round(maxv + 0.5), marker=avg_req)


def _bhava_svg(rows):
    edu, car = {4, 5, 9}, {2, 10, 11}
    items = []
    for s in rows:
        color = ("#8b7bf0" if s.house in edu else "#f4b740" if s.house in car
                 else "#5a6ea0")
        items.append({"label": f"H{s.house} ({s.lord[:2]})", "value": s.rupas,
                      "color": color})
    maxv = max([s.rupas for s in rows] + [1])
    return _svg_bars(items, round(maxv + 0.5))


def _phala_color(verdict):
    v = (verdict or "").lower()
    if "strongly benefic" in v:
        return "#1f9d6b"
    if "benefic" in v:
        return "#34c98a"
    if "challeng" in v:
        return "#e8607a"
    if "mixed" in v:
        return "#e8a13a"
    return "#5a6ea0"           # node / variable


def _phala_ribbon_svg(maha, education_best, career_best, width=600):
    """A horizontal Gantt-style ribbon of the upcoming Mahadashas coloured by
    their Ishta/Kashta phala, with education (above) and career (below) best-
    period windows marked, plus a 'now' line."""
    import datetime as _dt

    def d(s):
        return _dt.date.fromisoformat(s).toordinal()

    if not maha:
        return ""
    t0 = d(maha[0]["start"])
    t1 = d(maha[-1]["end"])
    span = max(t1 - t0, 1)
    pad, top, band_h = 8, 34, 30
    height = top + band_h + 30
    now = _dt.date.today().toordinal()

    def x(t):
        return pad + (width - 2 * pad) * (t - t0) / span

    parts = [f'<svg viewBox="0 0 {width} {height}" class="ribbon-svg" '
             f'preserveAspectRatio="xMinYMin meet" role="img">']

    # Mahadasha segments.
    for m in maha:
        x0, x1 = x(d(m["start"])), x(d(m["end"]))
        w = max(x1 - x0, 1)
        parts.append(
            f'<rect x="{x0:.1f}" y="{top}" width="{w:.1f}" height="{band_h}" '
            f'fill="{_phala_color(m["verdict"])}" stroke="#0f1020" stroke-width="0.5"/>')
        if w > 26:
            parts.append(f'<text x="{x0 + w/2:.1f}" y="{top + band_h/2 + 4:.1f}" '
                         f'text-anchor="middle" class="ribbon-lord">{m["lord"]}</text>')

    # Year ticks (every ~5 years).
    start_year = _dt.date.fromordinal(t0).year
    end_year = _dt.date.fromordinal(t1).year
    step = 5 if (end_year - start_year) > 12 else 2
    yr = start_year - (start_year % step)
    while yr <= end_year:
        tx = x(_dt.date(yr, 1, 1).toordinal())
        if pad <= tx <= width - pad:
            parts.append(f'<line x1="{tx:.1f}" y1="{top}" x2="{tx:.1f}" '
                         f'y2="{top + band_h}" stroke="#0f1020" stroke-width="0.5" opacity="0.4"/>')
            parts.append(f'<text x="{tx:.1f}" y="{top + band_h + 14:.1f}" '
                         f'text-anchor="middle" class="ribbon-year">{yr}</text>')
        yr += step

    # Best-period window markers: education above, career below the band.
    def marks(rows, y, h):
        qcol = {"prime": "#34c98a", "favourable": "#8b7bf0", "workable": "#e8a13a"}
        for e in rows:
            mx0, mx1 = x(d(e["start"])), x(d(e["end"]))
            w = max(mx1 - mx0, 3)
            parts.append(f'<rect x="{mx0:.1f}" y="{y}" width="{w:.1f}" height="{h}" '
                         f'rx="1.5" fill="{qcol.get(e["quality"].lower(), "#8b7bf0")}">'
                         f'<title>{e["chain"]} ({e["quality"]})</title></rect>')
    marks(education_best, top - 10, 7)
    marks(career_best, top + band_h + 3, 7)

    # Now marker.
    if t0 <= now <= t1:
        nx = x(now)
        parts.append(f'<line x1="{nx:.1f}" y1="{top-12}" x2="{nx:.1f}" '
                     f'y2="{top + band_h + 12:.1f}" class="ribbon-now"/>')
        parts.append(f'<text x="{nx:.1f}" y="{top-14:.1f}" text-anchor="middle" '
                     f'class="ribbon-now-label">now</text>')
    parts.append('</svg>')
    return "".join(parts)


def _resolve_birth(name, dob, tob, city, latitude, longitude, tz) -> BirthData:
    """Build a BirthData from form/query inputs (city pick or raw coordinates)."""
    if city and city in CITIES:
        lat, lon, tzoff = CITIES[city]
        place = city
    else:
        try:
            lat = float(latitude)
            lon = float(longitude)
            tzoff = float(tz)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=422,
                detail="Provide a known city, or numeric latitude, longitude and tz.",
            )
        place = f"{lat:.4f}, {lon:.4f}"

    try:
        d = dt.datetime.strptime(dob, "%Y-%m-%d").date()
        t = dt.datetime.strptime(tob, "%H:%M").time()
    except ValueError:
        raise HTTPException(status_code=422,
                            detail="dob must be YYYY-MM-DD and tob must be HH:MM.")

    return BirthData(name=name or "Seeker", date=d, time=t, latitude=lat,
                     longitude=lon, tz_offset_hours=tzoff, place=place)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request, "index.html",
        {"cities": sorted(CITIES.keys()), "cities_json": json.dumps(CITIES)}
    )


@app.post("/report", response_class=HTMLResponse)
def report(
    request: Request,
    name: str = Form("Seeker"),
    dob: str = Form(...),
    tob: str = Form(...),
    city: str = Form(""),
    latitude: str = Form(""),
    longitude: str = Form(""),
    tz: str = Form(""),
):
    birth = _resolve_birth(name, dob, tob, city, latitude, longitude, tz)

    rep = build_report(birth)
    upcoming = upcoming_mahadashas(rep.dasha_tree, dt.datetime.now(), count=6)

    # Pre-compute planet table rows for both charts.
    def planet_rows(chart):
        rows = []
        for name in C.PLANETS:
            p = chart.planets[name]
            L = p.lordship
            rows.append({
                "name": name, "sign": p.sign,
                "deg": f"{p.degree_in_sign:.2f}", "house": p.house,
                "nak": L.nakshatra, "pada": L.pada,
                "star": L.star_lord, "sub": L.sub_lord, "subsub": L.sub_sub_lord,
                "retro": "R" if p.retrograde else "",
                "navamsa": par.navamsa_sign(p.longitude),
                "dasamsa": par.dasamsa_sign(p.longitude),
                "siddhamsa": par.siddhamsa_sign(p.longitude),
            })
        return rows

    context = {
        "birth": birth,
        "rep": rep,
        "kp_rows": planet_rows(rep.kp_chart),
        "par_rows": planet_rows(rep.par_chart),
        "upcoming": upcoming,
        "shadbala_rows": [rep.shadbala.planets[p] for p in rep.shadbala.ranking],
        "bhava_rows": [rep.bhava_bala.houses[h] for h in rep.bhava_bala.ranking],
        "shadbala_svg": _shadbala_svg([rep.shadbala.planets[p] for p in rep.shadbala.ranking]),
        "bhava_svg": _bhava_svg([rep.bhava_bala.houses[h] for h in rep.bhava_bala.ranking]),
        "phala": rep.phala_timeline,
        "ishta_ranking": rep.ishta_ranking,
        "education_best": rep.education_best,
        "career_best": rep.career_best,
        "current_age": rep.current_age,
        "life_stage": rep.life_stage,
        "ribbon_svg": _phala_ribbon_svg(rep.phala_timeline["mahadasha"],
                                        rep.education_best, rep.career_best),
        "kp_asc": rep.kp_chart.asc_lordship,
        "par_asc": rep.par_chart.asc_lordship,
        "kp_ascdeg": f"{norm360(rep.kp_chart.ascendant) % 30:.2f}",
        "par_ascdeg": f"{norm360(rep.par_chart.ascendant) % 30:.2f}",
    }
    return templates.TemplateResponse(request, "report.html", context)


# ---------------------------------------------------------------------------
# JSON API
# ---------------------------------------------------------------------------
@app.get("/api/cities")
def api_cities():
    """List the built-in cities and their coordinates / timezone."""
    return {c: {"latitude": v[0], "longitude": v[1], "tz_offset_hours": v[2]}
            for c, v in CITIES.items()}


@app.get("/api/faqs")
def api_faq_list():
    """List the FAQ keys and their question text."""
    return faqmod.FAQ_TITLES


@app.get("/api/report")
def api_report(
    dob: str = Query(..., description="Birth date YYYY-MM-DD"),
    tob: str = Query(..., description="Birth time HH:MM (24h, local)"),
    name: str = Query("Seeker"),
    city: str = Query(""),
    latitude: str = Query(""),
    longitude: str = Query(""),
    tz: str = Query(""),
):
    """Full education + career report (KP + Parashara) as structured JSON."""
    birth = _resolve_birth(name, dob, tob, city, latitude, longitude, tz)
    rep = build_report(birth)
    return JSONResponse(report_to_dict(rep))


@app.get("/api/faq/{key}")
def api_single_faq(
    key: str,
    dob: str = Query(...),
    tob: str = Query(...),
    name: str = Query("Seeker"),
    city: str = Query(""),
    latitude: str = Query(""),
    longitude: str = Query(""),
    tz: str = Query(""),
):
    """Answer a single FAQ (by key) with its dasha timeline as JSON."""
    if key not in faqmod.FAQ_REGISTRY:
        raise HTTPException(status_code=404,
                            detail=f"Unknown FAQ '{key}'. See /api/faqs.")
    birth = _resolve_birth(name, dob, tob, city, latitude, longitude, tz)
    rep = build_report(birth)
    answer = next(a for a, k in zip(rep.faqs, faqmod.FAQ_REGISTRY) if k == key)
    return {
        "question": answer.question, "verdict": answer.verdict,
        "summary": answer.summary, "kp_basis": answer.kp_basis,
        "parashara_basis": answer.parashara_basis,
        "timeline": [{"chain": w.chain, "start": w.start.date().isoformat(),
                      "end": w.end.date().isoformat(), "note": w.note}
                     for w in answer.timeline],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
