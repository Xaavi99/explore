"""Compile an itinerary into an ordered list of slide records.

The deck mirrors the company-overview template (blue palette). Most slides are
fixed brand content from deck_content; the cover and the REGION cards are the
only itinerary-driven slides — region cards are the picked stops grouped by
catalogue region. A slide record is a plain dict consumed by every renderer.
"""
import imagemap
import theme
import deck_content as C


def _paths(keys):
    return [imagemap.slide_path(k) for k in keys]


def _region_cards(stops):
    """Group picked stops by catalogue region -> one 'sections' slide each."""
    by_region = {}
    for s in stops:
        by_region.setdefault(s["region"], []).append(s)
    ordered = [r for r in C.REGION_ORDER if r in by_region]
    ordered += [r for r in by_region if r not in C.REGION_ORDER]  # any stragglers

    cards = []
    for i, region in enumerate(ordered):
        rstops = by_region[region]
        copy = C.REGION_COPY.get(region, {
            "title": region.title(), "intro": "",
            "experiences": "", "traveller": "",
        })
        names = " · ".join(s["name"].title() for s in rstops)
        sections = [("Main Destinations", names)]
        if copy.get("experiences"):
            sections.append(("Signature Experiences", copy["experiences"]))
        if copy.get("traveller"):
            sections.append(("Ideal Traveller", copy["traveller"]))
        cards.append({
            "layout": "sections",
            "editable": True,
            "img_side": "left" if i % 2 == 0 else "right",
            "eyebrow": region,
            "title": copy["title"],
            "title_font": theme.SERIF_BOLD,
            "title_pt": 34,
            "title_brand": True,
            "intro": copy.get("intro", ""),
            "sections": sections,
            "left_paths": [s["slide_path"] for s in rstops if s["slide_path"]],
        })
    return cards


def build_slide_plan(itinerary, stops):
    """itinerary dict + resolved stops -> [slide record]."""
    slides = []

    # 1) cover — itinerary title + client
    cover_path = imagemap.slide_path(itinerary["cover_key"]) if itinerary.get("cover_key") else None
    if not cover_path:
        cover_path = next((s["slide_path"] for s in stops if s["slide_path"]), None)
    caption_bits = [b for b in (itinerary.get("client"), itinerary.get("dates")) if b]
    slides.append({
        "layout": "cover",
        "kicker": (itinerary.get("prepared_by") or C.COMPANY) + " · South India",
        "title": itinerary.get("title", "South India Tour"),
        "caption": "  ·  ".join(caption_bits),
        "image": cover_path,
    })

    # 2) About (fixed)
    slides.append({
        "layout": "sections", "img_side": "left",
        "eyebrow": C.ABOUT["eyebrow"], "title": C.ABOUT["title"],
        "sections": C.ABOUT["sections"], "left_paths": _paths(C.ABOUT["photo_keys"]),
    })

    # 3) Destination Map (fixed)
    slides.append({
        "layout": "sections", "img_side": "right",
        "eyebrow": C.MAP["eyebrow"], "title": C.MAP["title"], "intro": C.MAP["intro"],
        "sections": C.MAP["sections"], "left_paths": _paths(C.MAP["collage_keys"]),
    })

    # 4) itinerary-driven region cards
    slides += _region_cards(stops)

    # 5) Handpicked Stays (fixed)
    slides.append({
        "layout": "cards", "eyebrow": C.STAYS["eyebrow"], "title": C.STAYS["title"],
        "intro": C.STAYS["intro"], "band": imagemap.slide_path(C.STAYS["band_key"]),
        "cards": C.STAYS["cards"],
    })

    # 6) Cultural Connection (fixed)
    slides.append({
        "layout": "sections", "img_side": "left",
        "eyebrow": C.CULTURAL["eyebrow"], "title": C.CULTURAL["title"], "intro": C.CULTURAL["intro"],
        "sections": C.CULTURAL["sections"], "left_paths": _paths(C.CULTURAL["photo_keys"]),
    })

    # 7) Sample Tour Themes (fixed)
    slides.append({
        "layout": "cards", "eyebrow": C.THEMES["eyebrow"], "title": C.THEMES["title"],
        "band": imagemap.slide_path(C.THEMES["band_key"]), "cards": C.THEMES["cards"],
    })

    # 8) Why Choose (fixed)
    slides.append({
        "layout": "grid", "eyebrow": C.WHYCHOOSE["eyebrow"], "title": C.WHYCHOOSE["title"],
        "intro": C.WHYCHOOSE["intro"], "cards": C.WHYCHOOSE["cards"],
    })

    # 9) Contact CTA (fixed)
    slides.append({
        "layout": "cta", "eyebrow": C.CONTACT["eyebrow"], "title": C.CONTACT["title"],
        "lines": C.CONTACT["lines"], "image": imagemap.slide_path(C.CONTACT["photo_key"]),
    })

    # 10) closing quote (fixed)
    slides.append({
        "layout": "quote", "quote": C.QUOTE["quote"], "attribution": C.QUOTE["attribution"],
        "image": imagemap.slide_path(C.QUOTE["photo_key"]),
    })

    return slides


if __name__ == "__main__":
    import sys
    from itinerary import load_catalogue, load_itinerary, resolve
    cat = load_catalogue()
    it = load_itinerary(sys.argv[1])
    stops, warn = resolve(it, cat)
    plan = build_slide_plan(it, stops)
    print(f"{len(plan)} slides:")
    for i, sl in enumerate(plan):
        head = sl.get("title") or sl.get("quote") or ""
        print(f"  {i+1:2d}. {sl['layout']:10s} {head[:52]}")
