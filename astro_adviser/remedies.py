"""
Remedial suggestions (upaya).

Classical, low-risk remedies are suggested for the planets that (a) matter for
education / career in this chart and (b) are weak - debilitated, in an enemy
sign, or otherwise low in dignity. The aim is to strengthen a benefic
significator or pacify an afflicted one.

These are traditional, devotional / lifestyle remedies only (mantra, charity,
gemstone caution, fasting day, lifestyle). They are not a substitute for
professional advice and gemstones in particular should be worn only after
consulting a qualified astrologer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from . import constants as C
from . import kp, parashara as par
from .ephemeris import Chart


# Per-planet traditional remedy data.
REMEDY_DB: Dict[str, dict] = {
    C.SUN: {
        "deity": "Surya / Lord Rama",
        "mantra": "Om Hraam Hreem Hraum Sah Suryaya Namah (Sunday, sunrise)",
        "gem": "Ruby (gold, ring finger) - only if Sun is a functional benefic",
        "charity": "Donate wheat, jaggery or copper on Sundays",
        "day": "Sunday",
        "lifestyle": "Offer water to the rising Sun; respect father and elders.",
    },
    C.MOON: {
        "deity": "Chandra / Parvati / Shiva",
        "mantra": "Om Shraam Shreem Shraum Sah Chandraya Namah (Monday)",
        "gem": "Natural pearl (silver, little finger)",
        "charity": "Donate rice, milk or white clothes on Mondays",
        "day": "Monday",
        "lifestyle": "Stay hydrated, keep a calm routine, respect mother.",
    },
    C.MARS: {
        "deity": "Hanuman / Kartikeya",
        "mantra": "Om Kraam Kreem Kraum Sah Bhaumaya Namah (Tuesday)",
        "gem": "Red coral (gold/copper, ring finger)",
        "charity": "Donate red lentils (masoor) or sweets on Tuesdays",
        "day": "Tuesday",
        "lifestyle": "Channel energy through sport/discipline; recite Hanuman Chalisa.",
    },
    C.MERCURY: {
        "deity": "Lord Vishnu / Ganesha",
        "mantra": "Om Braam Breem Braum Sah Budhaya Namah (Wednesday)",
        "gem": "Emerald (gold, little finger)",
        "charity": "Donate green gram (moong) or green cloth on Wednesdays",
        "day": "Wednesday",
        "lifestyle": "Feed birds/cows green fodder; practise writing and study daily.",
    },
    C.JUPITER: {
        "deity": "Brihaspati / Lord Vishnu / Guru",
        "mantra": "Om Graam Greem Graum Sah Gurave Namah (Thursday)",
        "gem": "Yellow sapphire (gold, index finger)",
        "charity": "Donate turmeric, chana dal or yellow items on Thursdays",
        "day": "Thursday",
        "lifestyle": "Respect teachers and mentors; study scriptures; serve the learned.",
    },
    C.VENUS: {
        "deity": "Lakshmi / Shukra",
        "mantra": "Om Draam Dreem Draum Sah Shukraya Namah (Friday)",
        "gem": "Diamond / white sapphire (silver/platinum)",
        "charity": "Donate white sweets, curd or perfume on Fridays",
        "day": "Friday",
        "lifestyle": "Cultivate art/aesthetics; maintain cleanliness and harmony.",
    },
    C.SATURN: {
        "deity": "Shani / Hanuman / Bhairava",
        "mantra": "Om Praam Preem Praum Sah Shanaye Namah (Saturday)",
        "gem": "Blue sapphire (only after testing) / amethyst as a safe substitute",
        "charity": "Donate black sesame, mustard oil, iron or serve labourers on Saturdays",
        "day": "Saturday",
        "lifestyle": "Be disciplined and patient; serve the elderly and the needy.",
    },
    C.RAHU: {
        "deity": "Durga / Bhairava",
        "mantra": "Om Bhraam Bhreem Bhraum Sah Rahave Namah",
        "gem": "Hessonite (gomed) - only after testing",
        "charity": "Donate mustard oil, blankets or feed stray dogs on Saturdays",
        "day": "Saturday",
        "lifestyle": "Avoid short-cuts and deception; meditate to steady the mind.",
    },
    C.KETU: {
        "deity": "Ganesha / Lord Shiva",
        "mantra": "Om Sraam Sreem Sraum Sah Ketave Namah",
        "gem": "Cat's eye (lehsunia) - only after testing",
        "charity": "Donate multi-coloured cloth or feed dogs on Saturdays/Tuesdays",
        "day": "Tuesday",
        "lifestyle": "Practise spirituality and detachment; keep a pet dog if possible.",
    },
}


@dataclass
class Remedy:
    planet: str
    reason: str
    measures: dict


def _weak(score: float) -> bool:
    return score <= 0.35


def remedies_for(par_chart: Chart, kp_chart: Chart, domain: str) -> List[Remedy]:
    """
    Suggest remedies for the weak planets that matter to ``domain``
    ('education' or 'career').

    A planet is flagged when it is (a) a key significator/karaka for the domain
    and (b) weak by Parashara dignity, OR when the relevant cuspal sub-lord is
    weak.
    """
    dig = par.all_dignities(par_chart)

    if domain == "education":
        karakas = [C.MERCURY, C.JUPITER]
        houses = C.EDUCATION_POSITIVE
    else:
        karakas = [C.SUN, C.SATURN, C.MERCURY, C.JUPITER]
        houses = C.CAREER_POSITIVE

    # Candidate planets: domain karakas + strong KP significators of the houses.
    sig = kp.significators_of_houses(kp_chart, houses)[:5]
    candidates: List[str] = []
    for p in karakas + sig:
        if p not in candidates and p in REMEDY_DB:
            candidates.append(p)

    out: List[Remedy] = []
    for planet in candidates:
        d = dig[planet]
        reason = None
        if d.state == "Debilitated":
            reason = f"{planet} is debilitated in {d.sign} - strengthening it helps."
        elif d.state == "Enemy sign":
            reason = f"{planet} sits in an enemy sign ({d.sign}); pacifying it helps."
        elif _weak(d.score):
            reason = f"{planet} is weak (dignity score {d.score})."
        elif planet in (C.RAHU, C.KETU) and planet in sig[:3]:
            reason = (f"{planet} is a strong {domain} significator; a calming "
                      f"remedy keeps its results steady.")
        if reason:
            out.append(Remedy(planet=planet, reason=reason,
                              measures=REMEDY_DB[planet]))

    # If everything is strong, recommend strengthening the single best karaka
    # as a supportive (not corrective) measure.
    if not out:
        best = max(karakas, key=lambda k: dig[k].score)
        out.append(Remedy(
            planet=best,
            reason=(f"All key {domain} planets are reasonably strong; honouring "
                    f"{best} (the lead karaka) sustains and enhances results."),
            measures=REMEDY_DB[best],
        ))
    return out
