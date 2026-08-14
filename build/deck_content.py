"""Fixed brand copy for the company-overview deck + per-region card copy.

The deck mirrors the reference company template (16 slides), recolored to the
blue catalogue palette. Most slides are brand boilerplate that does NOT depend on
the itinerary; those live here as plain dicts. The per-destination personalization
happens only on the cover and the REGION cards, which are generated from the
picked stops grouped by catalogue region (see slideplan.build_slide_plan).

Region copy is keyed by the catalogue's region names (see build/catalogue.json):
KERALA, TAMIL NADU, KARNATAKA, GOA, ISLAND & CROSS-BORDER JOURNEYS.
"""

COMPANY = "Exploreain"
SITE = "Exploreain.com"

# order regions appear in the deck when several are picked
REGION_ORDER = ["KERALA", "TAMIL NADU", "KARNATAKA", "GOA", "ISLAND & CROSS-BORDER JOURNEYS"]

# UPPERCASE region -> curated card copy. `main` is filled dynamically from the
# picked stops; everything else is fixed marketing copy in the template's voice.
REGION_COPY = {
    "KERALA": {
        "title": "Backwaters, Hill Retreats & Wellness",
        "intro": "Famous for backwaters, Ayurveda, tea gardens and cultural richness — a relaxed premium destination blending heritage, hill retreats and soft adventure.",
        "experiences": "Houseboat cruise, Ayurveda retreat, tea plantation stay, Kathakali show and backwater village visits.",
        "traveller": "Couples, families and wellness travellers on a first visit to South India.",
    },
    "TAMIL NADU": {
        "title": "Temples, Tradition & Timeless Culture",
        "intro": "Rich in architecture, spirituality, art and classical heritage — the strongest cultural destination in South India.",
        "experiences": "Temple architecture tours, cultural immersion, classical art and dance, hill retreats and heritage hotels.",
        "traveller": "Culture-focused travellers, educational groups and heritage enthusiasts.",
    },
    "KARNATAKA": {
        "title": "Royal Heritage, Coffee Hills & Natural Beauty",
        "intro": "A blend of heritage cities, palaces, hill stations and wildlife — a strong mix of culture and nature.",
        "experiences": "Mysore Palace visit, coffee estate stays, Hampi heritage exploration, wildlife safari and premium nature retreats.",
        "traveller": "Culture lovers, heritage travellers and luxury nature seekers.",
    },
    "GOA": {
        "title": "Coastal Leisure, Lifestyle & Boutique Escapes",
        "intro": "Famous for beaches, leisure, vibrant nightlife and Portuguese heritage — suited to both luxury and fun-filled holidays.",
        "experiences": "Beach resort stays, sunset cruises, heritage walks, food and nightlife, and wellness by the sea.",
        "traveller": "Couples, groups, beach lovers and honeymoon travellers.",
    },
    "ISLAND & CROSS-BORDER JOURNEYS": {
        "title": "Islands, Reefs & Cross-Border Escapes",
        "intro": "Crystal-clear waters and serene beaches across the Andamans and Lakshadweep, plus Sri Lanka's heritage, tea country and wildlife — the finest island and cross-border finales.",
        "experiences": "Snorkelling and diving, island hopping, scenic train journeys, tea estates, leopard safaris and romantic beach stays.",
        "traveller": "Honeymooners, premium leisure seekers and travellers wanting a varied island or international finale.",
    },
}

# ---- fixed brand slides (itinerary-independent) ----

ABOUT = {
    "eyebrow": "About Exploreain",
    "title": "Crafting Unforgettable Journeys",
    "sections": [
        ("Identity", "We create seamless travel programs designed for comfort, discovery and cultural depth."),
        ("Ethos", "Reliable ground handling, authentic cultural access and personalised itineraries."),
        ("Standards", "24/7 dedicated concierge, with quality accommodation and experiences."),
    ],
    "photo_keys": ["temple", "munnar_tea"],
}

MAP = {
    "eyebrow": "Where We Operate",
    "title": "Our Destination Map",
    "intro": "Three connected worlds — one operator, one seamless itinerary.",
    "sections": [
        ("South India", "Kerala, Tamil Nadu & Karnataka — backwaters, hill stations, heritage towns, living temples, wildlife and authentic Ayurveda."),
        ("The Andamans", "Island escapes with turquoise water, white-sand beaches, marine experiences and relaxed barefoot luxury."),
        ("Sri Lanka", "Heritage cities, high tea country, leopard safaris, a golden coastline and deep wellness and culture."),
    ],
    "collage_keys": ["island", "andaman", "srilanka", "munnar"],
}

STAYS = {
    "eyebrow": "Sanctuaries of Luxury",
    "title": "Handpicked Four-Star Stays",
    "intro": "Comfortable, well-run four-star hotels and resorts, personally inspected, with contracted allocations and preferential rates for our partners.",
    "band_key": "kovalam",
    "cards": [
        ("Sterling Resorts", "Dependable hill and lake resorts at Munnar, Thekkady, Alleppey, Ooty and Kodaikanal — ideal for touring itineraries."),
        ("Fortune & Lemon Tree", "Reliable four-star city hotels in Kochi, Chennai, Madurai, Mysuru and Bengaluru, with consistent service standards."),
        ("Coastal & Island Resorts", "Novotel and Resort Rio in Goa; SeaShell and Symphony Palms in Havelock and Port Blair — relaxed beachfront comfort."),
        ("Cinnamon, Amaya & Heritance", "Trusted Sri Lankan four-star names across Colombo, Kandy, Nuwara Eliya, Sigiriya, Bentota and the Yala park gates."),
    ],
}

CULTURAL = {
    "eyebrow": "Culture and Local Life",
    "title": "Immersive Cultural Connection",
    "intro": "Genuine encounters arranged through artists, cooks and craftspeople we know personally — never staged for coaches.",
    "sections": [
        ("Arts & Performance", "Private classical dance recitals and Kalaripayattu martial arts showcases, with the artists explaining their craft."),
        ("Culinary Arts", "Chef-led market tours and heirloom recipe masterclasses in family kitchens across Kerala, Chettinad and Colombo."),
        ("Local Impact", "Supporting heritage preservation and sustainable artisan guilds — silk weavers, bronze casters and coir cooperatives."),
    ],
    "photo_keys": ["kochi", "temple"],
}

THEMES = {
    "eyebrow": "Sample Tour Themes",
    "title": "Tailor-Made Journeys",
    "band_key": "srilanka",
    "cards": [
        ("The Royal Journey", "Mysuru palaces, the Chettinad mansions and Sri Lanka's hill country, with private evening access and heritage stays.", "Heritage and architecture lovers"),
        ("Tropical Wellness", "Kerala Ayurveda under resident physicians, Goan beaches and the finest spas of the South, at a restorative pace.", "Relaxation and rejuvenation"),
        ("Wild Ceylon & Reefs", "Yala leopard safaris, Andaman diving and the tea estates in between — active days, comfortable nights.", "Adventure and wildlife enthusiasts"),
    ],
}

WHYCHOOSE = {
    "eyebrow": "Why Partner With Us",
    "title": "Why Choose Exploreain",
    "intro": "Built for direct, high-value clients who value a dependable ground partner.",
    "cards": [
        ("Seamless Coordination", "Expert local handling from arrival to departure."),
        ("Our Own Guides", "Consistent standards and no last-minute substitutions."),
        ("Premium Selection", "Carefully chosen guides and premium accommodations."),
        ("Authentic, In Comfort", "Genuine experiences delivered to international standards."),
        ("Clear & Reliable", "Punctuality, transparent invoicing and clear cancellation terms."),
        ("Always On", "24/7 emergency line, vetted vehicles and real-time trip monitoring."),
    ],
}

CONTACT = {
    "eyebrow": "Let's Build the Journey",
    "title": "Let us design your extraordinary South Asian journey",
    "lines": [
        (SITE, True),
        ("For custom itineraries and premium guided travel", False),
        ("Enquiries answered within one business day", False),
    ],
    "photo_key": "varkala",
}

QUOTE = {
    "quote": "From serene backwaters to sacred temples, tea-covered hills to tropical shores, Exploreain crafts journeys you will remember for a lifetime.",
    "attribution": "EXPLOREAIN.COM",
    "photo_key": "island",
}
