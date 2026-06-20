"""
Astrological reference data used by both KP and Parashara analysis.

All longitudes are sidereal degrees (0..360) measured from 0 Aries.
"""

# ---------------------------------------------------------------------------
# Planets
# ---------------------------------------------------------------------------
# We use the 9 grahas of Vedic astrology. Rahu / Ketu are the lunar nodes
# (we use the True Node). Outer planets are not used for KP / Vimshottari.

SUN = "Sun"
MOON = "Moon"
MARS = "Mars"
MERCURY = "Mercury"
JUPITER = "Jupiter"
VENUS = "Venus"
SATURN = "Saturn"
RAHU = "Rahu"
KETU = "Ketu"
ASCENDANT = "Ascendant"

PLANETS = [SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN, RAHU, KETU]

# Short labels used in tables.
PLANET_SHORT = {
    SUN: "Su", MOON: "Mo", MARS: "Ma", MERCURY: "Me", JUPITER: "Ju",
    VENUS: "Ve", SATURN: "Sa", RAHU: "Ra", KETU: "Ke", ASCENDANT: "Asc",
}

# ---------------------------------------------------------------------------
# Rasis (zodiac signs) and their lords
# ---------------------------------------------------------------------------
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_LORD = {
    "Aries": MARS, "Taurus": VENUS, "Gemini": MERCURY, "Cancer": MOON,
    "Leo": SUN, "Virgo": MERCURY, "Libra": VENUS, "Scorpio": MARS,
    "Sagittarius": JUPITER, "Capricorn": SATURN, "Aquarius": SATURN,
    "Pisces": JUPITER,
}

# Sign nature for vocational hints.
FIRE_SIGNS = {"Aries", "Leo", "Sagittarius"}
EARTH_SIGNS = {"Taurus", "Virgo", "Capricorn"}
AIR_SIGNS = {"Gemini", "Libra", "Aquarius"}
WATER_SIGNS = {"Cancer", "Scorpio", "Pisces"}

MOVABLE_SIGNS = {"Aries", "Cancer", "Libra", "Capricorn"}
FIXED_SIGNS = {"Taurus", "Leo", "Scorpio", "Aquarius"}
DUAL_SIGNS = {"Gemini", "Virgo", "Sagittarius", "Pisces"}

# ---------------------------------------------------------------------------
# Nakshatras (27) and their Vimshottari lords
# ---------------------------------------------------------------------------
# Each nakshatra spans 13 deg 20 min (= 13.3333 deg).
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
    "Revati",
]

# ---------------------------------------------------------------------------
# Vimshottari dasha
# ---------------------------------------------------------------------------
# Order of the dasha lords and their durations in years (total 120).
VIMSHOTTARI_ORDER = [KETU, VENUS, SUN, MOON, MARS, RAHU, JUPITER, SATURN, MERCURY]

VIMSHOTTARI_YEARS = {
    KETU: 7, VENUS: 20, SUN: 6, MOON: 10, MARS: 7,
    RAHU: 18, JUPITER: 16, SATURN: 19, MERCURY: 17,
}

TOTAL_VIMSHOTTARI_YEARS = 120

# The 27 nakshatras map cyclically onto the 9 lords (3 nakshatras per lord),
# starting from Ashwini = Ketu.
NAKSHATRA_LORDS = [VIMSHOTTARI_ORDER[i % 9] for i in range(27)]

# A Vedic / Vimshottari "year" of 365.25 days is the standard convention.
DAYS_PER_YEAR = 365.25

# ---------------------------------------------------------------------------
# Dignities (Parashara)
# ---------------------------------------------------------------------------
# Exaltation sign (and exact degree) for each planet.
EXALTATION = {
    SUN: ("Aries", 10), MOON: ("Taurus", 3), MARS: ("Capricorn", 28),
    MERCURY: ("Virgo", 15), JUPITER: ("Cancer", 5), VENUS: ("Pisces", 27),
    SATURN: ("Libra", 20),
}
# Debilitation = opposite sign of exaltation.
DEBILITATION = {
    SUN: "Libra", MOON: "Scorpio", MARS: "Cancer", MERCURY: "Pisces",
    JUPITER: "Capricorn", VENUS: "Virgo", SATURN: "Aries",
}
# Own signs.
OWN_SIGNS = {
    SUN: ["Leo"], MOON: ["Cancer"], MARS: ["Aries", "Scorpio"],
    MERCURY: ["Gemini", "Virgo"], JUPITER: ["Sagittarius", "Pisces"],
    VENUS: ["Taurus", "Libra"], SATURN: ["Capricorn", "Aquarius"],
}
# Moolatrikona sign for finer strength.
MOOLATRIKONA = {
    SUN: "Leo", MOON: "Taurus", MARS: "Aries", MERCURY: "Virgo",
    JUPITER: "Sagittarius", VENUS: "Libra", SATURN: "Aquarius",
}

# Natural friendships (Parashara). f=friend, e=enemy, n=neutral.
NATURAL_RELATION = {
    SUN:     {MOON: "f", MARS: "f", JUPITER: "f", MERCURY: "n", VENUS: "e", SATURN: "e"},
    MOON:    {SUN: "f", MERCURY: "f", MARS: "n", JUPITER: "n", VENUS: "n", SATURN: "n"},
    MARS:    {SUN: "f", MOON: "f", JUPITER: "f", VENUS: "n", SATURN: "n", MERCURY: "e"},
    MERCURY: {SUN: "f", VENUS: "f", MOON: "e", MARS: "n", JUPITER: "n", SATURN: "n"},
    JUPITER: {SUN: "f", MOON: "f", MARS: "f", SATURN: "n", MERCURY: "e", VENUS: "e"},
    VENUS:   {MERCURY: "f", SATURN: "f", MARS: "n", JUPITER: "n", SUN: "e", MOON: "e"},
    SATURN:  {MERCURY: "f", VENUS: "f", JUPITER: "n", SUN: "e", MOON: "e", MARS: "e"},
}

# ---------------------------------------------------------------------------
# Karakas (significators) relevant to education & career
# ---------------------------------------------------------------------------
# Natural significators (Naisargika karaka).
KARAKAS = {
    "education": [MERCURY, JUPITER],        # intelligence, learning, wisdom
    "intelligence": [MERCURY],
    "wisdom": [JUPITER],
    "career": [SUN, SATURN, MERCURY, JUPITER],  # authority, karma, commerce, counsel
    "profession_karma": [SATURN],
    "authority": [SUN],
    "wealth": [JUPITER, VENUS],
}

# ---------------------------------------------------------------------------
# House significations
# ---------------------------------------------------------------------------
# Houses relevant for education (KP + Parashara):
#   2  -> speech, accumulated knowledge, value, family wealth
#   4  -> formal/basic schooling, foundational education, comforts
#   5  -> intelligence, higher education, learning capacity, mantra
#   9  -> higher learning, research, philosophy, luck in studies, abroad
#   11 -> fulfilment of desire, completion of education, gains from learning
EDUCATION_HOUSES = [2, 4, 5, 9, 11]
# For KP, "success" in education typically needs the 4-5-9-11 group.
EDUCATION_POSITIVE = [4, 5, 9, 11]
EDUCATION_NEGATIVE = [3, 8, 12]   # interruptions / drop-outs / change

# Houses relevant for career (KP + Parashara):
#   2  -> earnings, wealth, accumulated income
#   6  -> service / job / employment, daily work, competition
#   7  -> business / partnership / dealing with public
#   10 -> profession, status, karma, authority
#   11 -> gains, income realization, fulfilment, promotions
CAREER_HOUSES = [2, 6, 7, 10, 11]
CAREER_POSITIVE = [2, 6, 10, 11]
CAREER_NEGATIVE = [5, 8, 12]      # break in profession / loss / transfer abroad
# Houses that indicate JOB/SERVICE vs BUSINESS in KP:
JOB_HOUSES = [6, 10]              # 6 = service
BUSINESS_HOUSES = [7, 10]         # 7 = self-employment / partnership / trade

# ---------------------------------------------------------------------------
# Career-field mapping by planet (used to suggest concrete fields)
# ---------------------------------------------------------------------------
PLANET_CAREER_FIELDS = {
    SUN: [
        "Government / civil services", "Administration & leadership",
        "Politics", "Medicine (physician)", "Power / energy sector",
        "Cardiology", "Pharmaceuticals", "Public administration",
    ],
    MOON: [
        "Healthcare & nursing", "Hospitality", "Food & beverages / dairy",
        "Psychology & counselling", "Public relations", "Marine / shipping",
        "Real estate", "Childcare & education (early years)",
    ],
    MARS: [
        "Engineering (mechanical/civil)", "Defence / police / army",
        "Surgery", "Sports & athletics", "Real estate & construction",
        "Manufacturing", "Fire / safety", "Metallurgy",
    ],
    MERCURY: [
        "Information technology & software", "Accounting & finance",
        "Writing, editing & journalism", "Mathematics & data science",
        "Commerce & trading", "Communications & telecom",
        "Teaching", "Business analysis", "Linguistics",
    ],
    JUPITER: [
        "Teaching & academia", "Law & judiciary", "Banking & finance",
        "Advisory / consulting", "Religion & spirituality", "Economics",
        "Counselling", "Publishing", "Wealth management",
    ],
    VENUS: [
        "Arts, design & fashion", "Music, film & entertainment",
        "Luxury & beauty industry", "Interior & graphic design",
        "Hospitality & tourism", "Diplomacy", "Gemmology & jewellery",
        "Media & advertising",
    ],
    SATURN: [
        "Labour-intensive industries", "Mining & oil", "Agriculture",
        "Manufacturing & heavy industry", "Civil & structural work",
        "Logistics & supply chain", "Social work", "Law enforcement",
        "Research requiring persistence",
    ],
    RAHU: [
        "Aviation & aeronautics", "Foreign / overseas assignments",
        "Software & emerging technology", "Photography & cinematography",
        "Electronics", "Speculation / stock markets", "Pharma research",
        "Unconventional / disruptive ventures",
    ],
    KETU: [
        "Research & investigation", "Spirituality & healing",
        "Medicine / alternative medicine", "Mathematics", "Computing",
        "Forensics", "Occult sciences", "Religious / philosophical work",
    ],
}

# Education streams suggested per planet (used with 4/5/9 houses & their lords).
PLANET_EDUCATION_STREAMS = {
    SUN: ["Medicine", "Public administration / political science", "Management"],
    MOON: ["Psychology", "Nursing & healthcare", "Hotel management", "Liberal arts"],
    MARS: ["Engineering", "Defence studies", "Surgery / dentistry", "Physical education"],
    MERCURY: ["Commerce & accountancy", "Computer science / IT", "Mathematics & statistics",
              "Journalism & mass communication", "Business administration"],
    JUPITER: ["Law", "Economics", "Teaching / education", "Philosophy", "Finance & banking"],
    VENUS: ["Fine arts & design", "Fashion technology", "Music / performing arts",
            "Architecture", "Media studies"],
    SATURN: ["Civil engineering", "Geology / mining", "Agriculture", "Social sciences",
             "Labour / industrial studies"],
    RAHU: ["Aeronautical engineering", "Computer / data science", "Foreign languages",
           "Photography / film", "Electronics & communication"],
    KETU: ["Pure sciences & research", "Mathematics", "Pharmacy", "Spiritual / vedic studies",
           "Forensic science"],
}

# Sign-based vocational temperament (used as a secondary hint).
SIGN_FIELDS = {
    "Aries": ["Engineering", "Defence", "Sports", "Entrepreneurship"],
    "Taurus": ["Finance & banking", "Arts", "Agriculture", "Luxury goods"],
    "Gemini": ["IT & communication", "Writing", "Trade", "Teaching"],
    "Cancer": ["Healthcare", "Hospitality", "Real estate", "Public-facing roles"],
    "Leo": ["Administration", "Government", "Entertainment", "Leadership roles"],
    "Virgo": ["Accounting", "Analysis", "Healthcare", "Editing & research"],
    "Libra": ["Law", "Design", "Diplomacy", "Fashion & beauty"],
    "Scorpio": ["Research", "Medicine / surgery", "Investigation", "Defence"],
    "Sagittarius": ["Teaching", "Law", "Finance", "Travel / philosophy"],
    "Capricorn": ["Administration", "Engineering", "Mining", "Long-term enterprise"],
    "Aquarius": ["Technology & innovation", "Social work", "Science", "Networking roles"],
    "Pisces": ["Arts", "Spirituality", "Pharma / healthcare", "Marine / overseas work"],
}
