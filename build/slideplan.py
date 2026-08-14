"""Compile an itinerary into an ordered list of slide records.

A slide record is a plain dict consumed by every renderer (Pillow PNG, PDF,
PPTX), so "what slides exist" is decided once, here, independent of "how they
are drawn". Each record has a "layout" plus the fields that layout needs.
"""
import imagemap

# feature layouts cycled across the per-destination slides for visual rhythm
FEATURE_CYCLE = ["feature-panel", "feature-split", "feature-framed"]

# trip length -> how many stops comfortably fit
DAYS_TO_STOPS = {7: 5, 10: 7, 14: 10}


def fit_stops(itinerary, stops):
    """Cap the stop list to what the chosen duration (days) comfortably fits."""
    days = itinerary.get("days")
    cap = DAYS_TO_STOPS.get(days)
    return stops[:cap] if cap else stops

# destination -> district(s) it sits in, for the "by the numbers" dashboard
DISTRICTS = {
    "KOCHI": ["Ernakulam"], "MUNNAR": ["Idukki"], "THEKKADY": ["Idukki"],
    "ALLEPPEY": ["Alappuzha"], "KUMARAKOM": ["Kottayam"],
    "VARKALA": ["Thiruvananthapuram"], "KOVALAM": ["Thiruvananthapuram"],
    "ATHIRAPPILLY": ["Thrissur"], "WAYANAD": ["Wayanad"],
    "KANNUR & BEKAL": ["Kannur", "Kasaragod"],
    "NORTH GOA": ["North Goa"], "SOUTH GOA & OLD GOA": ["South Goa"],
    "HAMPI": ["Vijayanagara"], "MYSORE": ["Mysuru"], "COORG": ["Kodagu"],
    "GOKARNA": ["Uttara Kannada"],
    "MADURAI": ["Madurai"], "THANJAVUR": ["Thanjavur"],
    "MAHABALIPURAM": ["Chengalpattu"], "PONDICHERRY": ["Puducherry"],
    "OOTY": ["Nilgiris"],
    "LAKSHADWEEP": ["Lakshadweep"], "ANDAMAN ISLANDS": ["Andaman"],
    "SRI LANKA": ["Sri Lanka"],
}


def compute_stats(itinerary, stops):
    """Real, itinerary-specific figures for the dashboard slide: (value, label)."""
    dests = len(stops)
    experiences = sum(len(s["dest"].get("details", [])) for s in stops)
    attractions = sum(len(s["dest"].get("attractions_list", [])) for s in stops)
    districts = set()
    for s in stops:
        for dist in DISTRICTS.get(s["name"], []):
            districts.add(dist)
    regions = len({s["region"] for s in stops})

    tiles = [(str(dests), "Destinations")]
    if itinerary.get("days"):
        tiles.append((str(itinerary["days"]), "Days"))
    elif itinerary.get("nights"):
        tiles.append((str(itinerary["nights"]), "Nights"))
    tiles.append((str(experiences), "Curated experiences"))
    if districts:
        tiles.append((str(len(districts)), "Districts"))
    if attractions:
        tiles.append((str(attractions), "Attractions"))
    if regions > 1:
        tiles.append((str(regions), "Regions"))
    return tiles


def district_of(name):
    return ", ".join(DISTRICTS.get(name, [])) or "—"


def build_slide_plan(itinerary, stops, copy):
    """itinerary dict + resolved stops + copy_bundle -> [slide record]."""
    stops = fit_stops(itinerary, stops)  # duration caps how many stops fit
    slides = []
    dest_copy = copy["destinations"]

    # 1) cover (full-bleed)
    cover_path = imagemap.slide_path(itinerary.get("cover_key")) if itinerary.get("cover_key") else None
    if not cover_path:
        cover_path = next((s["slide_path"] for s in stops if s["slide_path"]), None)
    caption_bits = [b for b in (itinerary.get("client"), itinerary.get("dates")) if b]
    slides.append({
        "layout": "cover",
        "kicker": (itinerary.get("prepared_by") or "Exploreain") + " · South India",
        "title": itinerary.get("title", "South India Tour"),
        "caption": "  ·  ".join(caption_bits),
        "image": cover_path,
    })

    # 2) dashboard — the journey in real numbers
    slides.append({
        "layout": "dashboard",
        "eyebrow": (itinerary.get("prepared_by") or "Exploreain") + " · at a glance",
        "title": itinerary.get("title", "South India Tour") + ", by the numbers",
        "tiles": compute_stats(itinerary, stops),
    })

    # 3) overview grid (up to 4 thumbnails)
    thumbs = [s["slide_path"] for s in stops if s["slide_path"]][:4]
    slides.append({
        "layout": "overview",
        "headline": copy["overview"]["headline"],
        "caption": copy["overview"]["caption"],
        "thumbs": thumbs,
    })

    # 3) per destination: a DATA card, then its MAIN-ATTRACTION (feature) card
    for i, s in enumerate(stops):
        dest = s["dest"]
        c = dest_copy.get(s["name"], {"headline": s["name"].title(), "caption": ""})
        common = {
            "name": s["name"],
            "eyebrow": s["region"].title(),
            "region": s["region"],
            "image": s["slide_path"],
            "index": i + 1,
        }
        slides.append(dict(common, **{
            "layout": "data",
            "district": district_of(s["name"]),
            "experiences": len(dest.get("details", [])),
            "attractions": len(dest.get("attractions_list", [])),
        }))
        slides.append(dict(common, **{
            "layout": FEATURE_CYCLE[i % len(FEATURE_CYCLE)],
            "headline": c["headline"],
            "caption": c["caption"],
        }))

    # 4) closing
    slides.append({
        "layout": "closing",
        "title": "Let's plan your journey.",
        "caption": "Private, tailored South India journeys — own fleet, own drivers, licensed local guides.",
        "prepared_by": itinerary.get("prepared_by") or "Exploreain",
    })

    return slides


if __name__ == "__main__":
    import sys, json
    from itinerary import load_catalogue, load_itinerary, resolve
    import deck_copy as copymod
    cat = load_catalogue()
    it = load_itinerary(sys.argv[1])
    stops, warn = resolve(it, cat)
    stops = fit_stops(it, stops)
    bundle = copymod.copy_bundle(stops, it, cat)
    plan = build_slide_plan(it, stops, bundle)
    print(f"{len(plan)} slides:")
    for i, sl in enumerate(plan):
        head = sl.get("title") or sl.get("headline") or ""
        print(f"  {i+1:2d}. {sl['layout']:16s} {head[:48]}")
