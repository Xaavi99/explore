"""Seed build/copy_cache.json with house-voice copy transcribed from the
reference deck (South India Tour Presentation.pdf), keyed the same way the AI
path keys its results. Run once; thereafter these destinations are cache hits
(no API call). Destinations not seeded here fall to AI generation or fallback.

    python build/seed_cache.py
"""
import os, json

from itinerary import load_catalogue
import deck_copy

# destination NAME (uppercase) -> {headline, caption}, in the reference deck's
# house voice: an evocative present-tense headline (no place name) + one factual
# caption. Hand-written for all 24 so decks need no API key.
SEED = {
    # --- Kerala ---
    "KOCHI": {
        "headline": "The morning catch is still on the sand when you arrive.",
        "caption": "Fort Kochi wakes early — cantilevered Chinese fishing nets worked by hand at the harbour's edge.",
    },
    "MUNNAR": {
        "headline": "She takes two leaves and a bud, and never looks down.",
        "caption": "Tea gardens above 1,500 metres, still picked by hand because no machine can judge it.",
    },
    "ALLEPPEY": {
        "headline": "Your boatman's grandfather poled this same canal.",
        "caption": "Two hours through water too narrow for anything with an engine, past houses that have no road.",
    },
    "KUMARAKOM": {
        "headline": "You hear the paddle before you hear the village.",
        "caption": "A country canoe threads the narrow canals off Vembanad Lake, past coir yards, kingfishers, and homes that open onto water.",
    },
    "THEKKADY": {
        "headline": "The elephants came down to drink before the boat did.",
        "caption": "A lake studded with the ghosts of a drowned forest, ringed by the spice hills of Periyar.",
    },
    "WAYANAD": {
        "headline": "The mist lifts off the ridge like it's deciding whether to stay.",
        "caption": "Cardamom and coffee under old-growth canopy in the Western Ghats, where the forest still holds elephants.",
    },
    "VARKALA": {
        "headline": "Pilgrims bathe where the cliff falls into the sea.",
        "caption": "A red laterite headland above Papanasam beach, its springs said to wash the years away.",
    },
    "KOVALAM": {
        "headline": "The lighthouse keeper has watched this sunset ten thousand times.",
        "caption": "Three crescent coves beneath a red-and-white lighthouse, where the Arabian Sea turns gold each evening.",
    },
    "ATHIRAPPILLY": {
        "headline": "You feel the falls in your chest before the bend reveals them.",
        "caption": "Kerala's widest waterfall, eighty feet into rainforest that still shelters hornbills.",
    },
    "KANNUR & BEKAL": {
        "headline": "By dawn the dancer is a god, and the village kneels.",
        "caption": "Home of the Theyyam ritual and Bekal's laterite sea-fort, where handlooms still clatter behind the beach.",
    },
    # --- Goa ---
    "NORTH GOA": {
        "headline": "The fort has watched for sails since before Goa was Goa.",
        "caption": "Red-laterite ramparts above the Arabian Sea, then beach shacks, feni, and Portuguese lanes inland.",
    },
    "SOUTH GOA & OLD GOA": {
        "headline": "A saint has lain in this church for four hundred years.",
        "caption": "The Basilica of Bom Jesus and Latin-quarter lanes, then long, near-empty sands to the south.",
    },
    # --- Karnataka ---
    "HAMPI": {
        "headline": "They once traded diamonds by the basket in this quiet.",
        "caption": "The boulder-strewn ruins of Vijayanagara — a stone chariot, soaring temples, and bazaars gone silent.",
    },
    "MYSORE": {
        "headline": "On the last night, they light the palace with a hundred thousand bulbs.",
        "caption": "A maharaja's city of silk, sandalwood, and the Indo-Saracenic Mysore Palace.",
    },
    "COORG": {
        "headline": "The estate has smelled of coffee blossom every March for a century.",
        "caption": "Misted hills of the Kodava people, terraced with coffee, cardamom, and pepper vines.",
    },
    "GOKARNA": {
        "headline": "Pilgrims and wanderers wash up on the same crescent of sand.",
        "caption": "A Shaivite temple town where sacred ghats give way to Om Beach and its rocky coves.",
    },
    # --- Tamil Nadu ---
    "MADURAI": {
        "headline": "Tonight, they carry him to her chamber. As they have for centuries.",
        "caption": "The thousand-pillared Meenakshi temple, its towers crowded with painted gods and unbroken worship.",
    },
    "THANJAVUR": {
        "headline": "The shadow of the tower never falls on the ground at noon.",
        "caption": "The Cholas' thousand-year-old Brihadeeswara temple, raised from granite hauled across a kingdom.",
    },
    "MAHABALIPURAM": {
        "headline": "The sculptors left their chisels in the rock, mid-thought.",
        "caption": "Pallava shore temples and bas-reliefs carved straight from the granite, facing the Bay of Bengal.",
    },
    "PONDICHERRY": {
        "headline": "Someone is speaking French in a café that predates the Republic.",
        "caption": "A former French colony of mustard-yellow villas, seafront promenades, and the ashram calm of Auroville.",
    },
    "OOTY": {
        "headline": "The little blue train still whistles up through the eucalyptus.",
        "caption": "A Raj-era hill station in the Nilgiris, reached by a UNESCO mountain railway through tea and pine.",
    },
    # --- Islands & cross-border ---
    "LAKSHADWEEP": {
        "headline": "Six islands out of thirty-six let visitors in.",
        "caption": "Coral lagoons that take sixty days' paperwork to reach. Worth every one.",
    },
    "ANDAMAN ISLANDS": {
        "headline": "The water is so clear the boat looks like it's floating on air.",
        "caption": "Coral reefs, rainforest, and the sobering colonial Cellular Jail, far out in the Bay of Bengal.",
    },
    "SRI LANKA": {
        "headline": "A king built his palace atop the rock, and dared the world to climb.",
        "caption": "Sigiriya's lion rock, hill-country tea, and ancient cities, a short hop across the strait.",
    },
}


def main():
    catalogue = load_catalogue()
    index = {d["name"]: d for r in catalogue["regions"] for d in r["destinations"]}
    cache = deck_copy._load_cache()
    added = 0
    for name, copy in SEED.items():
        dest = index.get(name)
        if not dest:
            print("skip (unknown):", name)
            continue
        cache[deck_copy._dest_key(dest)] = copy
        added += 1
    deck_copy._save_cache(cache)
    print(f"seeded {added} entries -> {deck_copy.CACHE_PATH}")


if __name__ == "__main__":
    main()
