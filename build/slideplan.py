"""Compile an itinerary into an ordered list of slide records.

Two distinct deck shapes come out of build_slide_plan, chosen by whether the
itinerary carries a `plan_content` sidecar (see build/plan_content/):

- **Tailored-plan deck** (plan_content present): a lean, plan-specific deck —
  cover, an overall stops summary (route/nights), then day-by-day. No general
  brand/marketing slides. Property names (plan_content's `stays`) are
  internal-only, gated behind build_slide_plan's `internal` flag.
- **General company-overview deck** (no plan_content): the original brand
  deck mirroring the company-overview template (blue palette) — cover, fixed
  brand content from deck_content, and REGION cards (picked stops grouped by
  catalogue region).

A slide record is a plain dict consumed by every renderer.
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


def _route_slide(pc):
    """Route & Nights table slide from plan_content."""
    rows = [(r["stop"], r["nights"], r["why"]) for r in pc["route"]]
    return {
        "layout": "table",
        "eyebrow": "Route & Pacing",
        "title": "Where You'll Stay, Night by Night",
        "intro": pc.get("route_intro", ""),
        "rows": rows,
    }


def _day_bound(day, end):
    """First/last day number out of a `day` field that may itself be a range
    (e.g. "3–7" for a merged multi-day block, per Kerala wellness-model style)."""
    parts = str(day).replace("–", "-").split("-")
    return parts[-1] if end else parts[0]


def _day_slides(pc, per_slide=3):
    """One or more Day-by-Day slides from plan_content, chunked so none overflow.
    Titles are derived from the actual `day` values (not chunk position), since
    a merged entry like "3–7" makes position and day-number diverge."""
    entries = pc["days"]
    slides = []
    for i in range(0, len(entries), per_slide):
        chunk = entries[i:i + per_slide]
        lo, hi = _day_bound(chunk[0]["day"], False), _day_bound(chunk[-1]["day"], True)
        title = f"Day {lo}" if lo == hi else f"Days {lo}–{hi}"
        days = [(f"Day {d['day']} — {d['label']}", d["body"]) for d in chunk]
        slides.append({
            "layout": "days", "eyebrow": "Day by Day", "title": title, "days": days,
        })
    return slides


def _stays_slide(pc):
    """Named-stays grid slide from plan_content (reuses the fixed grid layout).
    INTERNAL ONLY — never shipped to clients, so our stay partners stay
    confidential; see build_slide_plan's `internal` flag."""
    cards = [(f"{s['stop']} — {s['name']}", s["why"]) for s in pc["stays"]]
    return {
        "layout": "grid",
        "eyebrow": "Named Stays (Internal)",
        "title": "Where We Recommend You Stay",
        "intro": "Real, well-established properties chosen per stop for this itinerary.",
        "cards": cards,
    }


def _cover_slide(itinerary, stops):
    cover_path = imagemap.slide_path(itinerary["cover_key"]) if itinerary.get("cover_key") else None
    if not cover_path:
        cover_path = next((s["slide_path"] for s in stops if s["slide_path"]), None)
    caption_bits = [b for b in (itinerary.get("client"), itinerary.get("dates")) if b]
    return {
        "layout": "cover",
        "kicker": (itinerary.get("prepared_by") or C.COMPANY) + " · South India",
        "title": itinerary.get("title", "South India Tour"),
        "caption": "  ·  ".join(caption_bits),
        "image": cover_path,
    }


def build_slide_plan(itinerary, stops, internal=False):
    """itinerary dict + resolved stops -> [slide record].

    A tailored-plan itinerary (one with a `plan_content` sidecar) gets a lean,
    plan-specific deck: cover, an overall stops summary (route/nights), then
    day-by-day — none of the general brand/marketing slides. `internal=True`
    additionally includes the named-stays slide (specific hotel/property
    names) for internal planning use; the client-facing deck (the default)
    never includes it — property partners are confidential.

    An itinerary with no `plan_content` gets the general company-overview
    brand deck (unchanged from before tailored plans existed)."""
    pc = itinerary.get("plan_content_data")
    if pc:
        slides = [_cover_slide(itinerary, stops), _route_slide(pc)]
        slides += _day_slides(pc)
        if internal:
            slides.append(_stays_slide(pc))
        return slides

    slides = [_cover_slide(itinerary, stops)]

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
