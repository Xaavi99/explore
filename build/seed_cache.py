"""Seed build/copy_cache.json with house-voice copy transcribed from the
reference deck (South India Tour Presentation.pdf), keyed the same way the AI
path keys its results. Run once; thereafter these destinations are cache hits
(no API call). Destinations not seeded here fall to AI generation or fallback.

    python build/seed_cache.py
"""
import os, json

from itinerary import load_catalogue
import deck_copy

# destination NAME (uppercase) -> {headline, caption}, from the reference deck's voice
SEED = {
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
    "MADURAI": {
        "headline": "Tonight, they carry him to her chamber. As they have for centuries.",
        "caption": "Temple cities where what you watch is worship, not performance.",
    },
    "VARKALA": {
        "headline": "Pilgrims bathe where the cliff falls into the sea.",
        "caption": "A red laterite headland above Papanasam beach, its springs said to wash the years away.",
    },
    "LAKSHADWEEP": {
        "headline": "Six islands out of thirty-six let visitors in.",
        "caption": "Coral lagoons that take sixty days' paperwork to reach. Worth every one.",
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
