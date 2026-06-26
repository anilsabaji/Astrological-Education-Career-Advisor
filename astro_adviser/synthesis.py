"""
Education x Career synthesis.

The education engine recommends *streams* (e.g. Fine arts, Mathematics) and the
career engine recommends *fields* (e.g. Medicine, Engineering). This module
links the two into a single, more specific vocation - the "collective result".

Example: education = Fine arts (ARTS) + career = Medicine (MEDICINE)
         -> "Plastic & cosmetic surgeon".

It works by (a) classifying each stream/field into a broad domain, then
(b) looking up a curated (education-domain x career-domain) -> specialised-role
table, with a readable fallback when a pair is not catalogued.
"""

from __future__ import annotations

from typing import List

# ---------------------------------------------------------------------------
# Domain classification (keyword based; first match wins)
# ---------------------------------------------------------------------------
_DOMAIN_KEYWORDS = [
    ("MEDICINE", ["medicine", "medical", "surgeon", "surgery", "dentist", "dental",
                  "nursing", "healthcare", "health", "pharma", "pharmacy",
                  "physician", "clinical"]),
    ("PSYCHOLOGY", ["psychology", "counsel"]),
    ("ENGINEERING", ["engineering", "mechanical", "civil", "structural",
                     "manufacturing", "metallurgy", "aeronautic", "aviation",
                     "electronics", "construction", "geology", "mining"]),
    ("IT", ["information technology", "software", "computer", "data science",
            "data", "computing", "telecom", "electronics & communication"]),
    ("LAW", ["law", "judiciary", "legal"]),
    ("ARTS", ["fine art", "art", "design", "fashion", "music", "performing",
              "interior", "graphic", "beauty", "luxury", "photograph", "film",
              "cinematograph", "entertainment", "architecture"]),
    ("MEDIA", ["media", "journalism", "writing", "publishing", "communication",
               "advertising", "public relations", "language"]),
    ("DEFENCE", ["defence", "defense", "police", "army", "military",
                 "law enforcement"]),
    ("SCIENCE", ["science", "research", "mathematics", "physics", "forensic",
                 "investigation", "statistics"]),
    ("HOSPITALITY", ["hospitality", "hotel", "tourism", "food", "beverage",
                     "dairy", "marine", "shipping"]),
    ("AGRI", ["agriculture", "farming", "agri"]),
    ("SPIRITUAL", ["spiritual", "religion", "vedic", "occult", "healing",
                   "philosophy"]),
    ("FINANCE", ["finance", "banking", "account", "wealth", "stock", "economics",
                 "commerce", "trading", "business", "management"]),
    ("TEACHING", ["teaching", "academia", "education", "professor"]),
    ("ADMIN", ["government", "administration", "civil service", "political",
               "politics", "diplomacy", "leadership", "social"]),
    ("ENERGY", ["power", "energy", "oil"]),
    ("REALESTATE", ["real estate"]),
]


def classify(title: str) -> str:
    t = (title or "").lower()
    for domain, kws in _DOMAIN_KEYWORDS:
        if any(k in t for k in kws):
            return domain
    return "GENERAL"


# ---------------------------------------------------------------------------
# Curated (education-domain, career-domain) -> specialised roles
# ---------------------------------------------------------------------------
COMBINATIONS = {
    ("ARTS", "MEDICINE"): ["Plastic & cosmetic surgeon",
                           "Reconstructive / maxillofacial surgeon",
                           "Medical illustrator", "Art / music therapist"],
    ("ARTS", "ENGINEERING"): ["Industrial / product designer",
                              "Architectural & structural designer",
                              "Automotive / aerospace designer"],
    ("ARTS", "IT"): ["UX / UI designer", "Game / technical artist",
                     "Creative technologist", "Motion-graphics / VFX artist"],
    ("ARTS", "FINANCE"): ["Luxury-brand manager", "Art dealer / gallery business",
                          "Creative director (advertising)"],
    ("ARTS", "MEDIA"): ["Film director / cinematographer",
                        "Creative & content director", "Animation producer"],
    ("ARTS", "ADMIN"): ["Cultural-affairs / museum administrator",
                        "Arts-policy & council officer"],
    ("ARTS", "HOSPITALITY"): ["Hospitality interior designer",
                              "Culinary artist / pastry chef",
                              "Event & experience designer"],
    ("ARTS", "TEACHING"): ["Fine-arts / design educator", "Music / drama teacher"],
    ("ARTS", "LAW"): ["Entertainment & IP lawyer"],

    ("ENGINEERING", "MEDICINE"): ["Biomedical engineer",
                                  "Medical-devices / prosthetics engineer",
                                  "Clinical / rehabilitation engineer"],
    ("ENGINEERING", "IT"): ["Robotics / embedded-systems engineer",
                            "Hardware-software systems engineer",
                            "IoT solutions engineer"],
    ("ENGINEERING", "FINANCE"): ["Engineering project / cost manager",
                                 "Quantitative analyst (fintech)",
                                 "Techno-commercial manager"],
    ("ENGINEERING", "DEFENCE"): ["Defence / aerospace engineer",
                                 "Military systems & weapons engineer",
                                 "Naval / submarine engineer"],
    ("ENGINEERING", "ADMIN"): ["Engineering-services (govt) officer",
                               "Infrastructure & public-works administrator"],
    ("ENGINEERING", "SCIENCE"): ["R&D / materials engineer",
                                 "Aerospace research engineer"],
    ("ENGINEERING", "TEACHING"): ["Engineering professor / technical trainer"],

    ("IT", "MEDICINE"): ["Health-informatics specialist",
                         "Medical-software / telemedicine engineer",
                         "Bioinformatics / genomics analyst"],
    ("IT", "FINANCE"): ["Fintech engineer / product manager",
                        "Algorithmic-trading developer",
                        "Data scientist (banking)"],
    ("IT", "LAW"): ["Cyber-law & data-privacy specialist",
                    "Legal-tech engineer"],
    ("IT", "DEFENCE"): ["Cyber-security / cyber-defence specialist",
                        "Defence software engineer"],
    ("IT", "MEDIA"): ["Digital-media engineer",
                      "AdTech / streaming-platform developer"],
    ("IT", "ADMIN"): ["e-Governance / digital-public-services architect",
                      "Government IT officer"],
    ("IT", "SCIENCE"): ["Computational scientist",
                        "AI / machine-learning researcher"],
    ("IT", "HOSPITALITY"): ["Travel-tech / hospitality-platform developer"],

    ("FINANCE", "MEDICINE"): ["Hospital administrator",
                              "Health-economics / pharma-finance analyst",
                              "Medical-insurance & actuarial specialist"],
    ("FINANCE", "IT"): ["Fintech product / business manager",
                        "ERP & business-systems consultant"],
    ("FINANCE", "LAW"): ["Corporate / tax lawyer", "Company secretary",
                         "Compliance & risk officer"],
    ("FINANCE", "ADMIN"): ["Revenue / treasury-services officer",
                           "Public-finance & budget administrator"],
    ("FINANCE", "ENGINEERING"): ["Project-finance / infrastructure-finance manager"],
    ("FINANCE", "MEDIA"): ["Financial journalist / analyst"],
    ("FINANCE", "HOSPITALITY"): ["Hospitality finance & revenue manager"],

    ("LAW", "FINANCE"): ["Corporate / banking lawyer", "Tax & GST consultant",
                         "Mergers & acquisitions counsel"],
    ("LAW", "ADMIN"): ["Judge / magistrate",
                       "Civil-services (judicial/administrative) officer",
                       "Public-policy & legislative advisor"],
    ("LAW", "MEDIA"): ["Media & defamation lawyer", "Legal journalist"],
    ("LAW", "DEFENCE"): ["Military / JAG legal officer"],
    ("LAW", "IT"): ["Cyber-law / IP attorney"],
    ("LAW", "MEDICINE"): ["Medico-legal consultant / medical-negligence lawyer"],

    ("SCIENCE", "MEDICINE"): ["Medical / clinical researcher", "Pharmacologist",
                              "Geneticist / molecular biologist"],
    ("SCIENCE", "ENGINEERING"): ["R&D scientist", "Materials / nanotech scientist"],
    ("SCIENCE", "IT"): ["Data / computational scientist", "AI researcher"],
    ("SCIENCE", "DEFENCE"): ["Defence-research scientist", "Forensic scientist"],
    ("SCIENCE", "TEACHING"): ["Research professor / academic scientist"],
    ("SCIENCE", "ADMIN"): ["Scientific-services / space-agency officer"],

    ("MEDIA", "MEDICINE"): ["Medical journalist / health communicator"],
    ("MEDIA", "FINANCE"): ["Financial / business journalist"],
    ("MEDIA", "ADMIN"): ["Public-relations / information-services officer",
                         "Government communications / spokesperson"],
    ("MEDIA", "DEFENCE"): ["Defence / war correspondent"],

    ("PSYCHOLOGY", "MEDICINE"): ["Psychiatrist", "Clinical psychologist",
                                 "Neuropsychologist"],
    ("PSYCHOLOGY", "ADMIN"): ["HR / organisational-behaviour specialist"],
    ("PSYCHOLOGY", "TEACHING"): ["Educational psychologist / school counsellor"],
    ("PSYCHOLOGY", "DEFENCE"): ["Military / forensic psychologist"],

    ("ADMIN", "MEDICINE"): ["Public-health administrator",
                            "Health-services / hospital director"],
    ("ADMIN", "DEFENCE"): ["Defence administration / commissioned officer"],
    ("ADMIN", "FINANCE"): ["Revenue / audit & accounts services officer"],

    ("DEFENCE", "MEDICINE"): ["Armed-forces medical officer"],
    ("DEFENCE", "ENGINEERING"): ["Military engineering-services officer"],
    ("DEFENCE", "IT"): ["Cyber-warfare / signals officer"],

    ("HOSPITALITY", "FINANCE"): ["Hotel / hospitality business manager"],
    ("HOSPITALITY", "MEDIA"): ["Travel & lifestyle media entrepreneur"],
    ("HOSPITALITY", "ADMIN"): ["Tourism-department / hospitality administrator"],

    ("TEACHING", "MEDICINE"): ["Medical-college professor"],
    ("TEACHING", "IT"): ["Computer-science educator / ed-tech founder"],
    ("TEACHING", "FINANCE"): ["Commerce / management professor"],

    ("AGRI", "SCIENCE"): ["Agricultural scientist / agronomist"],
    ("AGRI", "FINANCE"): ["Agri-business & commodity manager"],
    ("AGRI", "ENGINEERING"): ["Agricultural / food-processing engineer"],

    ("SPIRITUAL", "MEDICINE"): ["Integrative / alternative-medicine practitioner "
                                "(Ayurveda, naturopathy)"],
    ("SPIRITUAL", "TEACHING"): ["Yoga / Vedic-studies teacher"],
    ("SPIRITUAL", "PSYCHOLOGY"): ["Spiritual counsellor / wellness coach"],
}


def _core(title: str) -> str:
    """First clause of a field title (before / , & ()), for readable fallbacks."""
    for sep in ("/", ",", "&", "("):
        title = title.split(sep)[0]
    return title.strip()


def _fallback(edu_title: str, career_title: str, edom: str, cdom: str) -> str:
    c, e = _core(career_title), _core(edu_title)
    if edom == cdom or "GENERAL" in (edom, cdom):
        return f"{c} specialist ({e} background)"
    return f"{c} with a {e} specialisation"


def synthesize(education_streams, career_fields, top_e: int = 2, top_c: int = 2,
               limit: int = 6) -> List[dict]:
    """
    Combine the top education streams with the top career fields into specific
    "collective" vocations. ``education_streams`` / ``career_fields`` are lists
    of objects (or dicts) exposing a ``title``.
    """
    def title_of(x):
        return x.title if hasattr(x, "title") else x.get("title", "")

    es = list(education_streams)[:top_e]
    cs = list(career_fields)[:top_c]
    if not es or not cs:
        return []

    # Pair them, prioritising the top-ranked education x top-ranked career.
    pairs = []
    for ci, c in enumerate(cs):
        for ei, e in enumerate(es):
            pairs.append((ei + ci, e, c))
    pairs.sort(key=lambda x: x[0])

    out, seen = [], set()
    for _, e, c in pairs:
        et, ct = title_of(e), title_of(c)
        edom, cdom = classify(et), classify(ct)
        roles = COMBINATIONS.get((edom, cdom)) or COMBINATIONS.get((cdom, edom))
        if not roles:
            roles = [_fallback(et, ct, edom, cdom)]
        for r in roles[:2]:
            if r in seen:
                continue
            seen.add(r)
            out.append({
                "title": r,
                "education_field": et,
                "career_field": ct,
                "basis": f"Education in {et} combined with a career in {ct}.",
            })
            if len(out) >= limit:
                return out
    return out
