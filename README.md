# Astro Adviser — Education & Career (KP + Parashara)

An astrological adviser that helps choose the **right education field** and the
**right career field** (for both **earning** and **satisfaction**). It reads the
birth chart with **both** the **KP (Krishnamurti Paddhati)** and **Parashara**
(classical Vedic) systems, and predicts **timelines** using **3-level
Vimshottari dashas** — Mahadasha → Antardasha → Pratyantardasha.

It also answers the **education & career questions most commonly asked of an
astrologer**, each with a verdict and a dasha-based timeline.

> For guidance and self-reflection only.

---

## Try it in your browser (no install)

A fully self-contained, client-side edition lives in **[`docs/index.html`](docs/index.html)**.
It runs entirely in the browser (positions via the astronomy-engine model,
matching Swiss Ephemeris to ~0.004°), has tabs for **Overview/Dasha, Education,
Career, FAQ and Charts**, and a **Print / Save PDF** button that produces a
colourful PDF report.

**Live link (GitHub Pages):**
`https://anilsabaji.github.io/Astrological-Education-Career-Advisor/`

To enable the live link once: open the repo on GitHub → **Settings → Pages** →
under *Build and deployment* set **Source: Deploy from a branch**, **Branch:
`main` / `/docs`**, then **Save**. The URL above goes live in a minute or two.

The browser edition is rebuilt from the sources in [`standalone/`](standalone/)
(`npm install && npm run build`). Rahu/Ketu there use the mean lunar node.

---

## What it does

| Area | KP technique | Parashara technique |
|------|--------------|---------------------|
| **Education** | Significators & cuspal sub-lords of 4, 5, 9, 11 | 2/4/5/9 lords, Mercury & Jupiter karakas, Saraswati / Budha-Aditya / Gaja-Kesari yogas, **D-24 (Chaturvimsamsa) education varga** |
| **Career** | Significators & CSL of 2, 6, 10, 11; job (6) vs business (7) | 10th house/lord, planets in 10th, **D-10 (Dasamsa) career varga**, Sun/Saturn/Mercury/Jupiter karakas, Raja & Dhana yogas |
| **Earning** | 2nd, 11th significators + 11th CSL | 2nd & 11th lords, Jupiter/Venus strength, Dhana yoga |
| **Satisfaction** | — | Alignment of 5th & 9th lords + dignity of career planets |
| **Planetary strength** | — | **Shadbala** (six-fold strength), with motional speed, direction (retrograde) & declination |
| **House strength** | — | **Bhava Bala** for the education (4/5/9) and career (2/10/11) houses |
| **Timing** | Vimshottari dasha of the strong significators (majority of MD/AD/PD) | Cross-checked with karaka sub-periods + **Ishta/Kashta dasha-phala timeline** |

### Shadbala (six-fold strength)
The assessment weighs every contributing planet by its **Shadbala** — the classical
six strengths: **Sthana** (positional), **Dig** (directional), **Kala** (temporal,
including **Ayana Bala from declination**), **Cheshta** (motional, from **speed &
retrogression**), **Naisargika** (natural) and **Drik** (aspectual). Each planet's
total (in *rupas*), whether it meets its required minimum, its **Ishta/Kashta**
(benefic vs strained) result, its **motion** (retrograde / fast / slow) and its
**declination** are reported and folded into the education and career judgement:
stronger, Ishta, well-moving planets pull their fields up; weak or Kashta planets
are discounted, and the strongest planet's periods are highlighted.

**Bhava Bala** (house strength, led by the Bhavadhipati Bala — the Shadbala of
the house lord) ranks all 12 bhavas; the education (4/5/9) and career (2/10/11)
house groups are summarised in the assessment. An **Ishta/Kashta dasha-phala
timeline** annotates the running and upcoming Mahadashas (and the current
Mahadasha's Antardashas) as benefic, mixed or challenging, so you can see which
periods are most favourable.

### Divisional charts (Vargas)
Fine judgement uses the divisional charts, not just the rasi (D-1):

- **D-9 Navamsa** — overall strength; a planet in the same sign in D-1 and D-9
  is *vargottama* (specially strong).
- **D-10 Dasamsa** — the **career** varga: its Lagna lord, 10th house/lord and
  any planets in the 10th describe the actual profession; these reinforce the
  recommended career fields.
- **D-24 Chaturvimsamsa (Siddhamsa)** — the **education** varga: the strength of
  Mercury & Jupiter and the planets in the learning houses (1/4/5/9) here gauge
  academic capacity and reinforce the recommended streams.

Each varga contributes a strength score and a weighted set of "field planets"
that flow into the final education/career recommendations, so the divisional
charts genuinely change the advice (not just a display).

### FAQs answered
Higher education, best study windows, study abroad, competitive exams, when a
job comes, government job, job vs business, promotion/growth, career change,
foreign career, and income/wealth growth.

### Also included
- **Remedial suggestions (upaya)** — for the weak/afflicted planets that matter
  to education or career: deity, mantra, charity, fasting day, gemstone caution
  and lifestyle measures.
- **Transit (Gochar) triggers** — current Jupiter / Saturn / Rahu / Ketu
  transits, the Jupiter+Saturn "double transit" over education (4, 9) and career
  (10, 6, 11) houses, and Sade-Sati status — used to *confirm* the dasha windows.

---

## Astronomical basis

- **Engine:** Swiss Ephemeris (`pyswisseph`) in sidereal mode using the built-in
  Moshier model — no external ephemeris data files required.
- **KP chart:** Krishnamurti ayanamsa + Placidus house cusps (cuspal sub-lords).
- **Parashara chart:** Lahiri ayanamsa + whole-sign houses.
- **Sub-lords:** computed from Vimshottari proportions within each nakshatra
  (star → sub → sub-sub).

---

## Setup

```bash
cd astro_adviser
pip install -r requirements.txt
```

## Run the web app

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
# open http://localhost:8000
```

Enter the date, time and place of birth (pick a city for instant
coordinates/timezone, or type exact latitude / longitude / UTC offset).

## Run from the command line

```bash
python -m astro_adviser.cli --name "Asha" \
    --date 1990-08-15 --time 10:30 \
    --lat 28.6139 --lon 77.2090 --tz 5.5
```

## JSON API

The same engine is exposed as JSON (great for integrations / a custom UI):

| Endpoint | Purpose |
|----------|---------|
| `GET /api/report` | Full education + career report, dasha, transits, remedies, FAQs |
| `GET /api/faq/{key}` | A single FAQ answer with its 3-level dasha timeline |
| `GET /api/faqs` | List of FAQ keys and questions |
| `GET /api/cities` | Built-in cities with coordinates / timezone |

Location is given either as `city=` (a known city) **or** as
`latitude=`, `longitude=`, `tz=` (UTC offset in hours).

```bash
# Full report
curl "http://localhost:8000/api/report?name=Asha&dob=1990-08-15&tob=10:30&city=New%20Delhi,%20India"

# One question, with exact coordinates
curl "http://localhost:8000/api/faq/when_job?dob=1990-08-15&tob=10:30&latitude=28.6139&longitude=77.2090&tz=5.5"
```

## Tests

```bash
python -m pytest        # 72 tests: dasha, sub-lords, dignities, vargas, shadbala, bhava bala, KP, advice, FAQ, transits, API
```

---

## Project layout

```
astro_adviser/
├── app.py                  # FastAPI web app
├── requirements.txt
├── templates/              # Jinja2 templates (index, report)
├── static/style.css
└── astro_adviser/
    ├── constants.py        # planets, signs, nakshatras, dasha years, karakas, field maps
    ├── ephemeris.py        # Swiss-Ephemeris chart + KP sub-lord engine
    ├── dasha.py            # 3-level Vimshottari dasha
    ├── kp.py               # KP significators & cuspal sub-lord analysis
    ├── parashara.py        # dignities, yogas, D-9/D-10, house-lord analysis
    ├── advice.py           # fuses KP + Parashara into ranked field advice
    ├── varga.py            # divisional charts (D-9/D-10/D-24) + vargottama
    ├── shadbala.py         # six-fold planetary strength (speed, direction, declination)
    ├── faq.py              # FAQ engine with dasha timelines
    ├── remedies.py         # remedial suggestions (upaya) for weak planets
    ├── transits.py         # transit (gochar) triggers, double transit, Sade Sati
    ├── adviser.py          # orchestrator -> full report (+ JSON serialization)
    └── cli.py              # command-line interface
```

tests/                      # pytest suite (run with `python -m pytest`)

---

## How timing works (KP)

An event fructifies during the **conjoined Vimshottari period** (Dasha–Bhukti–
Antara) when a **majority of the three running lords** (MD, AD, PD) are the
**strong significators** (grade A/B + cuspal sub-lords) of the houses that must
activate for that result. The adviser scans the 3-level dasha tree and reports
those windows with exact start/end dates.
