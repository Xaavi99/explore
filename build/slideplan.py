"""Compile an itinerary into an ordered list of slide records.

A slide record is a plain dict consumed by every renderer (Pillow PNG, PDF,
PPTX), so "what slides exist" is decided once, here, independent of "how they
are drawn". Each record has a "layout" plus the fields that layout needs.
"""
import imagemap

# feature layouts cycled across the per-destination slides for visual rhythm
FEATURE_CYCLE = ["feature-panel", "feature-split", "feature-framed"]


def build_slide_plan(itinerary, stops, copy):
    """itinerary dict + resolved stops + copy_bundle -> [slide record]."""
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

    # 2) overview grid (up to 4 thumbnails)
    thumbs = [s["slide_path"] for s in stops if s["slide_path"]][:4]
    slides.append({
        "layout": "overview",
        "headline": copy["overview"]["headline"],
        "caption": copy["overview"]["caption"],
        "thumbs": thumbs,
    })

    # 3) per-destination feature slides, cycling layouts
    for i, s in enumerate(stops):
        c = dest_copy.get(s["name"], {"headline": s["name"].title(), "caption": ""})
        slides.append({
            "layout": FEATURE_CYCLE[i % len(FEATURE_CYCLE)],
            "name": s["name"],
            "eyebrow": s["region"].title(),
            "headline": c["headline"],
            "caption": c["caption"],
            "region": s["region"],
            "image": s["slide_path"],
            "index": i + 1,
        })

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
    bundle = copymod.copy_bundle(stops, it, cat)
    plan = build_slide_plan(it, stops, bundle)
    print(f"{len(plan)} slides:")
    for i, sl in enumerate(plan):
        head = sl.get("title") or sl.get("headline") or ""
        print(f"  {i+1:2d}. {sl['layout']:16s} {head[:48]}")
