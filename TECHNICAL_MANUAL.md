# Technical Manual — Astrological Education & Career Adviser

**How the results are derived · what parameters are considered · how each one influences the outcome**

*Version 1.0 · Developed by Dr. Anil Sabaji, email: anilsabaji@gmail.com*

---

## Table of contents

1. [Purpose & scope](#1-purpose--scope)
2. [System architecture](#2-system-architecture)
3. [Astronomical foundation](#3-astronomical-foundation)
4. [The two reference frames: KP and Parashara charts](#4-the-two-reference-frames-kp-and-parashara-charts)
5. [Lordship chain & KP sub-lords](#5-lordship-chain--kp-sub-lords)
6. [Vimshottari Dasha (3-level timing engine)](#6-vimshottari-dasha-3-level-timing-engine)
7. [KP analysis — significators & cuspal sub-lords](#7-kp-analysis--significators--cuspal-sub-lords)
8. [Parashara analysis — dignities, house lords, yogas](#8-parashara-analysis--dignities-house-lords-yogas)
9. [Divisional charts (Vargas)](#9-divisional-charts-vargas)
10. [Shadbala — six-fold planetary strength](#10-shadbala--six-fold-planetary-strength)
11. [Bhava Bala & Ishta/Kashta phala](#11-bhava-bala--ishtakashta-phala)
12. [Education assessment — parameters & influence](#12-education-assessment--parameters--influence)
13. [Career assessment — parameters & influence](#13-career-assessment--parameters--influence)
14. [Best Periods overlay (KP windows × dasha phala × age)](#14-best-periods-overlay-kp-windows--dasha-phala--age)
15. [FAQ engine — verdicts & timelines](#15-faq-engine--verdicts--timelines)
16. [Transit (Gochar) triggers](#16-transit-gochar-triggers)
17. [Remedial suggestions](#17-remedial-suggestions)
18. [The standalone browser edition](#18-the-standalone-browser-edition)
19. [Worked example & reproducibility](#19-worked-example--reproducibility)
20. [Parameter influence — master summary](#20-parameter-influence--master-summary)
21. [Limitations & disclaimer](#21-limitations--disclaimer)

---

## 1. Purpose & scope

The utility advises on the **right education field** and the **right career field** (for both
*earning* and *satisfaction*), and answers the questions most commonly put to an astrologer,
each with a **timeline**. It deliberately fuses **two independent astrological systems** so the
advice reflects agreement (or disagreement) between them:

* **KP (Krishnamurti Paddhati)** — a precise, sub-lord-driven system used here mainly for the
  *promise* of a result and its *timing*.
* **Parashara (classical Vedic)** — used for *dignity*, *yogas*, *divisional charts* and
  *planetary strength (Shadbala)*.

Every result is **derived from the birth chart by deterministic rules** (no machine learning, no
randomness). The same birth data always produces the same output.

---

## 2. System architecture

```
Birth data (date, time, lat, lon, tz)
        │
        ▼
 ephemeris.py ──► two Chart objects:  KP chart  +  Parashara chart
        │
        ├─► dasha.py        3-level Vimshottari tree (from the Moon)
        ├─► kp.py           significators, cuspal sub-lords (KP chart)
        ├─► parashara.py    dignities, yogas, vargas (Parashara chart)
        ├─► varga.py        divisional-chart geometry (D-2 … D-30)
        ├─► shadbala.py     six-fold strength + Bhava Bala + Ishta/Kashta
        │
        ▼
 advice.py  ──► fuses KP + Parashara + Shadbala into ranked field advice
 faq.py     ──► FAQ answers with dasha windows
 remedies.py / transits.py
        │
        ▼
 adviser.py ──► AdviceReport (orchestrator) + JSON serialization
        │
        ├─► app.py            FastAPI web app + JSON API + usage counter
        └─► docs/index.html   self-contained browser edition (JS port)
```

| Module | Responsibility |
|--------|----------------|
| `constants.py` | All reference data: planets, signs & lords, 27 nakshatras, Vimshottari years, dignities, karakas, house groups, field→planet mappings |
| `ephemeris.py` | Swiss-Ephemeris chart, sub-lord computation, Placidus cusps, speed & declination |
| `dasha.py` | 3-level Vimshottari dasha, running-period lookup, fructification scan |
| `kp.py` | KP four-step significators, houses-signified, cuspal sub-lord (CSL) judgement |
| `parashara.py` | Dignity/strength, house-lord placement, yogas, D-9/D-10/D-24 analysis |
| `varga.py` | Divisional-sign formulae and the `VargaChart` builder |
| `shadbala.py` | Six balas, Bhava Bala, Ishta/Kashta phala, strength factors |
| `advice.py` | Combines all of the above into ranked education/career recommendations |
| `faq.py` | The 11 FAQs with KP-promise + dasha timeline |
| `remedies.py` | Upaya for weak/afflicted key planets |
| `transits.py` | Slow-planet transit triggers, double-transit, Sade Sati |
| `adviser.py` | Orchestrates everything; best-periods overlay; age awareness; JSON |

---

## 3. Astronomical foundation

| Item | Choice | Why it matters |
|------|--------|----------------|
| **Ephemeris** | Swiss Ephemeris (`pyswisseph`), Moshier model (`FLG_MOSEPH`) | Sub-arc-minute planetary positions with **no external data files** |
| **Zodiac** | **Sidereal** (`FLG_SIDEREAL`) | Vedic astrology is sidereal (fixed-star based), not tropical |
| **Nodes** | **True Node** for Rahu; Ketu = Rahu + 180° | KP/Parashara conventionally use the lunar nodes |
| **Speed** | Longitude speed (deg/day) captured per planet | Drives **Cheshta Bala** & retrograde detection |
| **Declination** | Equatorial declination (`FLG_EQUATORIAL`) | Drives **Ayana Bala** |

**Ayanamsa** (the sidereal–tropical offset) is system-specific:

* **KP chart → Krishnamurti ayanamsa** (`SIDM_KRISHNAMURTI`)
* **Parashara chart → Lahiri ayanamsa** (`SIDM_LAHIRI`)

The two differ by only ≈ 6 arc-minutes, but that is enough to occasionally move a **sub-lord**
across a boundary — which is exactly why KP needs its own ayanamsa.

**Time handling.** Local birth time is converted to UTC using the timezone offset, then to a
Julian Day. The web/standalone front-ends capture the **DST-aware** offset automatically from the
city's IANA timezone.

---

## 4. The two reference frames: KP and Parashara charts

`compute_chart(...)` is called twice and returns two independent `Chart` objects:

| | KP chart | Parashara chart |
|---|----------|-----------------|
| Ayanamsa | Krishnamurti | Lahiri |
| Houses | **Placidus cusps** (unequal, real cusp degrees) | **Whole-sign** (house = sign from the ascendant) |
| Used for | Significators, **cuspal sub-lords**, timing | Dignity, yogas, vargas, **Shadbala** |

**Placidus cusps** are computed by Swiss Ephemeris (`houses_ex(..., b"P")`). They give each of the
12 house cusps an exact degree, which KP needs because the **sub-lord of the cusp degree** is the
deciding factor. The MC (10th cusp) is also stored for **Dig Bala**.

Each planet record carries: sidereal longitude, sign, house, retrograde flag, **speed**,
**declination**, and the full **lordship chain** (below).

---

## 5. Lordship chain & KP sub-lords

Every longitude is decomposed into a chain used throughout the engine:

```
longitude → Sign (lord) → Nakshatra (star lord) → Sub-lord → Sub-sub-lord
```

* **Sign lord** — ruler of the 30° sign.
* **Nakshatra / star lord** — ruler of the 13°20′ lunar mansion (one of the 9 Vimshottari lords).
* **Sub-lord** — the nakshatra span is divided into **9 unequal parts proportional to the
  Vimshottari dasha years** (Ketu 7, Venus 20, Sun 6, …), starting from the star lord. The part the
  longitude falls in gives the sub-lord.
* **Sub-sub-lord** — the same proportional division applied again *inside* the sub.

This proportional sub-division (`_subdivide`) is the mathematical heart of KP. **The sub-lord is
considered the final deciding authority** over the matters a planet/cusp signifies.

---

## 6. Vimshottari Dasha (3-level timing engine)

The Vimshottari dasha is the project's clock. It is anchored on the **Moon's nakshatra at birth**.

* **Cycle:** 120 years, in the fixed order Ketu 7 → Venus 20 → Sun 6 → Moon 10 → Mars 7 →
  Rahu 18 → Jupiter 16 → Saturn 19 → Mercury 17.
* **Balance at birth:** how far the Moon has travelled through its nakshatra fixes the remaining
  fraction of the first Mahadasha.
* **Three levels are built:**
  * **Mahadasha (MD)** — major period.
  * **Antardasha (AD / Bhukti)** — `MD_years × AD_years / 120`.
  * **Pratyantardasha (PD)** — `AD_years × PD_years / 120`.
* A "year" = **365.25 days**.

`find_running(tree, when)` returns the MD/AD/PD active on any date. `fructification_windows(...)`
scans the tree for periods where the running lords are the **significators** of a set of houses —
this is how every timeline in the app is produced (see §7).

---

## 7. KP analysis — significators & cuspal sub-lords

### 7.1 Four-step significators of a house

For any house H, planets are graded (strongest first):

| Grade | Rule | Meaning |
|-------|------|---------|
| **A** | Planets in the **star (nakshatra) of an occupant** of H | Strongest signification |
| **B** | **Occupants** of H | Strong |
| **C** | Planets in the **star of the lord** of H | Moderate |
| **D** | The **lord** of H | Present but weakest |

Nodes (Rahu/Ketu) occupying a house are added as strong significators, and a node represents
(in priority) its **conjoined planets → star lord → sign lord**.

### 7.2 Houses signified by a planet

A planet signifies the houses **occupied and owned by its star lord** (strongest), plus the house
it occupies and the houses it owns. This is what `houses_signified_by` returns and is reused for
cuspal-sub-lord judgement.

### 7.3 Cuspal Sub-Lord (CSL) — the decider

In KP, **whether a matter happens at all** is decided by the **sub-lord of the relevant house
cusp**. The engine asks: *does the CSL signify the positive houses for this matter, and avoid the
negative ones?*

| Matter | Cusps examined | Positive houses | Cautionary houses |
|--------|----------------|-----------------|-------------------|
| **Education** | 4, 5, 9, 11 | 4, 5, 9, 11 | 3, 8, 12 |
| **Higher education** | 9 & 11 | 9, 11, 4, 5 | 8, 12, 3 |
| **Career (promise)** | 10, 6, 2, 11 | 2, 6, 10, 11 | 5, 8, 12 |
| **Job vs business** | 10 & 6 CSL links | 6 → job, 7 → business | — |

A house's matter is judged **favorable** when its CSL signifies ≥ 1 positive house and at least as
many positive as cautionary houses. Education is "promised" when ≥ 2 of the four CSLs are
favorable; the same threshold applies to career.

### 7.4 Strong significators (for timing)

`strong_significators(houses)` = grade A/B significators **plus** the cuspal sub-lords of those
houses. These focused planets are what the dasha scan looks for when timing an event (§14, §15).

---

## 8. Parashara analysis — dignities, house lords, yogas

### 8.1 Planetary dignity (a 0–1 strength score)

| State | Score | Example |
|-------|-------|---------|
| Exalted | 1.00 | Jupiter in Cancer |
| Moolatrikona | 0.90 | Mars in Aries |
| Own sign | 0.85 | Mercury in Gemini |
| Friendly sign | 0.65 | — |
| Neutral sign | 0.50 | — |
| Enemy sign | 0.30 | — |
| Debilitated | 0.10 | Mercury in Pisces |

Friendship uses the natural-relationship table; nodes act through their dispositor (0.5).

### 8.2 House-lord placement

For the education houses (2, 4, 5, 9) and career houses (2, 6, 7, 10, 11), the engine records
**which house and sign each lord occupies** and its dignity. Lords falling in supportive houses
(kendras 1/4/7/10, trikonas 1/5/9, plus 2 & 11) strengthen the matter.

### 8.3 Yogas detected

| Yoga | Condition | Bearing |
|------|-----------|---------|
| **Budha-Aditya** | Sun + Mercury together | Intellect, communication |
| **Gaja-Kesari** | Jupiter in a kendra from the Moon | Wisdom, repute |
| **Saraswati** | Mercury, Jupiter, Venus in kendra/trikona/2nd | Learning, arts, eloquence |
| **Pancha-Mahapurusha** (Ruchaka/Bhadra/Hamsa/Malavya/Sasa) | A planet exalted/own in a kendra | Leadership in its domain |
| **Dhana** | 2nd/11th lords linked to 2/5/9/10/11 | Earning |
| **Raja** | A kendra lord conjoined a trikona lord | Rise in status |

Education uses Saraswati / Budha-Aditya / Gaja-Kesari; career uses Raja / Dhana / Mahapurusha.

---

## 9. Divisional charts (Vargas)

Divisional charts refine the rasi (D-1). Each is built by `build_varga` with **whole-sign houses
from the divisional ascendant**.

| Varga | Name | Role in this app |
|-------|------|------------------|
| **D-9** | Navamsa | Overall strength; **vargottama** = same sign in D-1 & D-9 (extra strong) |
| **D-10** | Dasamsa | **Career varga** — its 10th house/lord & occupants describe the profession |
| **D-24** | Chaturvimsamsa (Siddhamsa) | **Education varga** — Mercury/Jupiter & the learning houses (1/4/5/9) gauge academic capacity |
| D-2, D-3, D-7, D-12, D-30 | Hora, Drekkana, Saptamsa, Dwadasamsa, Trimsamsa | Used inside **Saptavargaja Bala** (§10) |

Each varga analysis produces a **strength score (0–1)** and a set of **field planets** that are fed,
weighted by that strength, into the recommendation engine.

---

## 10. Shadbala — six-fold planetary strength

Shadbala is computed for the **seven classical grahas** (Sun…Saturn) on the Parashara chart.
Strengths are in **virupas** (60 virupas = 1 **rupa**). The six balas:

### 10.1 Sthana Bala (positional)

| Component | How computed | Max |
|-----------|--------------|-----|
| **Uccha** | Angular distance from the planet's debilitation point ÷ 3 (0 at debilitation, 60 at exaltation) | 60 |
| **Saptavargaja** | Dignity across **7 vargas** (D-1,2,3,7,9,12,30) via compound friendship: Moolatrikona 45 / Own 30 / Great-friend 22.5 / Friend 15 / Neutral 7.5 / Enemy 3.75 / Great-enemy 1.875 | 315 |
| **Ojhayugma** | Correct odd/even sign in Rasi & Navamsa (15 each) | 30 |
| **Kendradi** | Kendra 60 / Panaphara 30 / Apoklima 15 | 60 |
| **Drekkana** | Male planets in 1st decanate, neuters in 2nd, females in 3rd → 15 | 15 |

### 10.2 Dig Bala (directional)

Each planet is strong in one cardinal house and powerless in the opposite. Dig Bala = angular
distance from the "powerless point" ÷ 3.

| Strong in | Powerless at | Planets |
|-----------|-------------|---------|
| 10th (MC) | 4th (Nadir) | Sun, Mars |
| 4th (Nadir) | 10th (MC) | Moon, Venus |
| 1st (Asc) | 7th (Desc) | Jupiter, Mercury |
| 7th (Desc) | 1st (Asc) | Saturn |

### 10.3 Kala Bala (temporal)

| Sub-bala | Basis | Note |
|----------|-------|------|
| **Nathonnatha** | Sun's hour angle (day vs night strength) | Mercury always 60 |
| **Paksha** | Moon–Sun elongation (benefics wax-strong, malefics dark-strong) | Moon's value doubled |
| **Tribhaga** | Ruler of the current third of day/night | Jupiter always 60 |
| **Vara** | Lord of the **weekday** of birth | +45 |
| **Hora** | Lord of the **planetary hour** (Chaldean order from sunrise) | +60 |
| **Masa / Abda** | Weekday lord of the solar **month / year** ingress (found by ephemeris search) | +30 / +15 |
| **Ayana** | **Declination**: `1.2766 × (23.45 ± δ)`; north-preferring planets add δ, Moon/Saturn subtract | uses declination |

### 10.4 Cheshta Bala (motional — speed & direction)

| Planet | Rule |
|--------|------|
| Sun | = its Ayana Bala |
| Moon | = its Paksha Bala |
| Mars…Saturn | **Retrograde → 60** (max); otherwise scaled by slowness `(1.5 − speed/mean)/1.5 × 60` (slow/near-stationary scores high, fast-direct low) |

This is precisely where **motion speed and direction enter the strength model** — a retrograde or
near-stationary planet is treated as motionally powerful.

### 10.5 Naisargika (natural, fixed)

Sun 60, Moon 51.43, Venus 42.86, Jupiter 34.29, Mercury 25.71, Mars 17.14, Saturn 8.57.

### 10.6 Drik Bala (aspectual)

Benefic full/special aspects on the planet add +15, malefic −15, divided by 4.

### 10.7 Total, sufficiency, and Ishta/Kashta

```
total_virupa = Sthana + Dig + Kala + Cheshta + Naisargika + Drik
rupas        = total_virupa / 60
ratio        = rupas / required          (required: Su 6.5, Mo 6, Ma 5, Me 7, Ju 6.5, Ve 5.5, Sa 5)
sufficient   = rupas ≥ required
Ishta phala  = √(Uccha × Cheshta)        (capacity to give GOOD results)
Kashta phala = √((60−Uccha) × (60−Cheshta))   (capacity to give DIFFICULT results)
benefic      = Ishta ≥ Kashta
```

### 10.8 Strength factor (how Shadbala influences advice)

```
strength_factor = clamp( 0.6 + 0.6 × min(ratio,1.6)/1.6  (+0.1 if benefic)  (+0.05 if retrograde),  0.6 … 1.4 )
```

Every planet's contribution to a recommendation is **multiplied by this 0.6–1.4 factor** — so a
strong, Ishta planet pulls its fields up and a weak/Kashta planet is discounted.

---

## 11. Bhava Bala & Ishta/Kashta phala

**Bhava Bala (house strength)** = `Bhavadhipati (Shadbala of the house lord, virupa)` +
`0.10 × Σ(Shadbala of occupants)` + `net aspect (benefic +20 / malefic −20)`, expressed in rupas
and labelled *weak / moderate / strong / very strong*. The education group (4/5/9) and career
group (2/10/11) are summarised in the assessment.

**Dasha-phala timeline** — each upcoming Mahadasha (and the current MD's Antardashas) is labelled
from its lord's Ishta/Kashta:

| Verdict | Condition |
|---------|-----------|
| **Strongly benefic** | Ishta ≥ Kashta and Ishta ≥ 40 |
| **Benefic / supportive** | Ishta ≥ Kashta |
| **Challenging** | Kashta − Ishta > 15 |
| **Mixed** | otherwise |
| **Variable** | node (no Shadbala) |

---

## 12. Education assessment — parameters & influence

`advise_education(kp_chart, par_chart, shadbala)` combines four weighted streams of "field planets".

### 12.1 What is collected and how it is weighted

| Source | Weight | Where it comes from |
|--------|--------|---------------------|
| KP field planets (significators of **4 & 5**) | **1.0** | `kp.judge_education` |
| KP significators of **4, 5, 9, 11** (top 4) | **0.6** | `kp.judge_education` |
| Parashara field planets (Mercury/Jupiter karakas + 4th/5th lords) | **1.0** | `parashara.judge_education` |
| **D-24** education-varga indicators | **0.6 + 0.6 × D24-strength** | `parashara.analyse_siddhamsa` |

Within each list, the *n*-th planet gets a small positional bonus `× (1 − 0.12 n)`. Then **every
planet score is multiplied by its Shadbala strength factor** (§10.8).

### 12.2 From planets to streams

Each scored planet is expanded into the **education streams it governs** (e.g. Mercury → IT,
commerce, accountancy, journalism; Jupiter → law, economics, teaching, finance). The 4th-house
**sign** adds a light temperament nudge (+0.4) to matching streams. The top 6 streams are returned.

### 12.3 Verdicts

* **Education promised** — from the KP CSL test on 4/5/9/11 (§7.3).
* **Higher education likely** — KP 9th & 11th CSLs both favorable.
* **Academic strength** — `0.65 × Parashara education score + 0.35 × (Shadbala of Mercury & Jupiter, capped)` → *Strong / Above average / Moderate*.

### 12.4 Influence summary

| Parameter | Effect on the result |
|-----------|----------------------|
| KP CSL of 4/5/9/11 | Decides **whether** education (and higher education) is promised |
| KP significators of 4/5 | Push their **streams** up the ranking |
| Mercury & Jupiter dignity + Shadbala | Set **academic strength**; weak ones trigger a remedy note |
| 4th/5th lords | Add their streams; placement affects strength |
| D-24 strength & field planets | Reinforce streams in proportion to divisional strength |
| Shadbala strength factor | Re-weights every planet (0.6–1.4×) |
| 4th-house sign | Light temperament nudge to matching streams |

---

## 13. Career assessment — parameters & influence

`advise_career(kp_chart, par_chart, shadbala)` mirrors education but on the career houses.

### 13.1 Field-planet sources & weights

| Source | Weight |
|--------|--------|
| KP field planets (significators of **10 & 6**) | **1.0** |
| KP significators of **2, 6, 10, 11** (top 4) | **0.6** |
| Parashara field planets (planets in 10th + 10th lord + strongest karaka) | **1.1** |
| **D-10** career-varga indicators | **0.7 + 0.7 × D10-strength** |

Again positional bonus `× (1 − 0.12 n)`, then × Shadbala strength factor; expanded into the
**career fields** each planet governs and ranked (10th-house sign nudges matching fields).

### 13.2 Earning rating (three independent votes, averaged)

| Vote | Source |
|------|--------|
| KP earning strength | 2nd/11th significators + 11th CSL → Strong=3 / Good=2 / Moderate=1 |
| Parashara wealth score | 2nd & 11th lord placement, Jupiter/Venus dignity, Dhana yoga → 3/2/1 |
| **Shadbala of wealth-givers** | average ratio of 2nd lord, 11th lord, Jupiter, Venus → ≥1.15 = 3, ≥0.9 = 2, else 1 |

`combined = mean of the three` → **High / Good / Moderate** earning.

### 13.3 Satisfaction rating

`0.5 × (5th & 9th lord alignment) + 0.5 × (average dignity of the leading career planets)`. If ≥ 2
of the top career planets are **Ishta** in Shadbala, the note is upgraded. → *High / Good /
Variable*. This is the engine's reading of **meaning/contentment**, distinct from earning.

### 13.4 Job vs business (consensus of both systems)

* **KP:** 10th & 6th CSL linked to the **6th** → service; to the **7th** → business.
* **Parashara:** 10th sign nature, planets in the 10th, and 6th-lord vs 7th-lord strength.
* The two verdicts are **reconciled**: agreement → that mode; KP-job + Parashara-business →
  *"salaried start then independent venture"*; etc.

### 13.5 Influence summary

| Parameter | Effect on the result |
|-----------|----------------------|
| KP CSL of 2/6/10/11 | Whether career & earning are **promised**; job-vs-business mode |
| Planets in 10th, 10th lord | Strongest colour on the **fields** (weight 1.1) |
| D-10 strength & planets | Reinforce fields; can shift the ranking markedly |
| 2nd/11th lords, Jupiter/Venus, Dhana yoga | **Earning** rating |
| 5th/9th lords + career-planet dignity & Ishta | **Satisfaction** rating |
| Shadbala strength factor & strongest planet | Re-weights fields; strongest planet's periods highlighted |

---

## 14. Best Periods overlay (KP windows × dasha phala × age)

`_best_periods(...)` answers *"when are the best windows for education/career growth?"* by
**overlaying two layers**:

1. **KP fructification windows** — scan the 3-level dasha for periods where a **majority of the
   running MD/AD/PD lords are strong significators** of the relevant houses (education 4/9/11,
   career 2/10/11).
2. **Dasha-phala quality** — the Ishta/Kashta verdict of the Mahadasha running at that window.

| Window quality | Meaning |
|----------------|---------|
| **Prime** | Benefic dasha era **and** active significators |
| **Favourable** | Benefic dasha era |
| **Workable** | Significators active but the era needs effort |

### Age awareness

The native's **age** is taken into account: **career windows are only sought from working age
(~16+)**, and every window is tagged with the age range and life-stage (Student years → Early
career → Career building → Career peak → Senior → Retirement). So a child's chart shows career
windows beginning at 16, while education windows start now.

---

## 15. FAQ engine — verdicts & timelines

Eleven common questions are answered the way an astrologer would — a **verdict** from the KP
promise cross-checked with Parashara, plus a **3-level dasha timeline**.

| Area | FAQs | Fructification houses |
|------|------|------------------------|
| Education | higher education, best study time, study abroad, competitive exams | 4/9/11, 4/5/11, 9/12, 6/10/11 |
| Career | when a job, government job, job vs business, promotion, career change, foreign career, income growth | 6/10/11, 1/6/10, 7/10/11, 2/10/11, 9/10/6, 7/10/12, 2/11 |

Each timeline window is a precise **MD–AD–PD** band with start/end dates, chosen because a majority
of those three running lords are significators of the question's houses.

---

## 16. Transit (Gochar) triggers

Dashas show what is *promised*; transits confirm when it *matures*. The engine reads the **slow
planets** (Jupiter, Saturn, Rahu, Ketu) for the current date and reports:

* Which natal house each transits (from Lagna and from the Moon).
* The **Jupiter + Saturn "double transit"** over education (4/5/9) and career (10/6/11) houses — a
  classic trigger for major events.
* **Sade Sati** status of Saturn relative to the natal Moon.

---

## 17. Remedial suggestions

For the planets that **matter to the domain** (education karakas Mercury/Jupiter; career karakas
Sun/Saturn/Mercury/Jupiter, plus the strong KP significators) and are **weak** (debilitated, enemy
sign, or low dignity), a traditional, low-risk **upaya** is suggested: presiding deity, mantra,
charity, fasting day, a gemstone caution, and a lifestyle measure. If all key planets are strong, a
supportive measure for the lead karaka is offered instead.

---

## 18. The standalone browser edition

`docs/index.html` is a **single self-contained file** that runs the whole engine **client-side**:

* Planetary positions come from the **astronomy-engine** library (no data files); the same
  sidereal maths, ayanamsa model and Placidus algorithm are re-implemented in JavaScript.
* It was **validated against the Python/Swiss-Ephemeris build to ≈ 0.004°** on planet longitudes,
  with Placidus cusp signs matching exactly.
* The full KP + Parashara + Vimshottari + Varga + Shadbala + Bhava-Bala + best-periods logic is
  ported, so the browser report matches the server report (the only deliberate difference is the
  use of the **mean node** for Rahu/Ketu, which can shift a node's sub-lord slightly).
* City search uses a live geocoding lookup and computes the **DST-aware** timezone offset for the
  birth date.

---

## 19. Worked example & reproducibility

Reference birth: **15 Aug 1990, 10:30, New Delhi (28.61 N, 77.21 E, +5.5)**.

* **KP Lagna** Virgo (sub-lord Saturn); **Parashara Lagna** Virgo.
* **Shadbala** (rupas, strongest first): Mars 8.26, Sun 8.11, Jupiter 7.85, Mercury 7.50,
  Saturn 7.03, Moon 6.83, Venus 6.78 — all above their required minimum.
* Sanity checks that confirm the maths: exalted **Jupiter → Uccha 59.8/60**; retrograde
  **Saturn → Cheshta 60**; **Vara Bala → Mercury 45** because 15 Aug 1990 was a **Wednesday**.

Run it yourself:

```bash
pip install -r requirements.txt
python -m astro_adviser.cli --name "Asha" --date 1990-08-15 --time 10:30 \
    --lat 28.6139 --lon 77.2090 --tz 5.5
python -m pytest      # 74 tests covering every module above
```

The engine is fully **deterministic**: identical inputs always yield identical output, which is why
the test-suite assertions (exact rupas, dasha boundaries, sub-lords) are stable.

---

## 20. Parameter influence — master summary

| Parameter | Computed in | Primarily influences |
|-----------|-------------|----------------------|
| Ayanamsa (KP vs Lahiri) | ephemeris | Sub-lords & cusp degrees → all KP verdicts |
| Cuspal sub-lord (CSL) | kp | **Whether** education/career is promised; job vs business |
| KP four-step significators | kp | **Field ranking** + **timing** of every window |
| Planetary dignity | parashara | Academic strength, satisfaction, wealth |
| Yogas | parashara | Strength notes; Dhana→earning, Raja→status |
| D-9 / D-10 / D-24 | varga/parashara | Reinforce streams/fields; vargottama strength |
| Shadbala (6 balas) | shadbala | **Re-weights every planet** (0.6–1.4×); earning vote |
| — speed & direction | shadbala (Cheshta) | Retrograde/slow planets gain motional strength |
| — declination | shadbala (Ayana) | North/south-preferring strength |
| Bhava Bala | shadbala | House-group strength (education 4/5/9, career 2/10/11) |
| Ishta / Kashta phala | shadbala | Satisfaction; **dasha-period quality** |
| Vimshottari dasha (3-level) | dasha | **All timelines**; best-period windows |
| Native's age | adviser | Filters career windows to working age; life-stage tags |
| Transits | transits | Confirmation triggers for promised results |

---

## 21. Limitations & disclaimer

* Shadbala has **minor school-to-school variations**; this implementation follows BPHS conventions
  with documented practical choices for sub-balas that need sunrise/ingress data.
* City timezone offsets in the browser use the IANA database (DST-aware); historical pre-1970
  offsets may differ by minutes in rare cases.
* The browser edition uses the **mean lunar node**; the server uses the **true node**.
* This utility is intended for **guidance and self-reflection**. It is **not** a substitute for
  professional educational, career, financial, medical or legal advice.

---

*Developed by Dr. Anil Sabaji · email: anilsabaji@gmail.com*
