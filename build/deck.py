"""Generate a client presentation from an itinerary.

    python build/deck.py itineraries/south-india-demo.json

Outputs to dist/<slug>/: <slug>.pdf, <slug>.pptx (image slides),
<slug>-editable.pptx (native/editable). The deck follows the company-overview
template (blue palette); brand slides are fixed and the region cards are built
from the picked destinations grouped by region.

When the itinerary carries a `plan_content` sidecar, an extra
<slug>-internal.pdf is also generated (see deck_render.generate_internal_pdf)
— it's the same deck plus a Named Stays slide naming our hotel/property
partners. That slide is INTERNAL ONLY: the client-facing outputs above never
include it, so partner relationships stay confidential from clients.
"""
import os, sys

from itinerary import load_catalogue, load_itinerary, resolve
import slideplan
import deck_render

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    it_path = argv[1]

    slug = os.path.splitext(os.path.basename(it_path))[0]
    catalogue = load_catalogue()
    itinerary = load_itinerary(it_path)
    stops, warnings = resolve(itinerary, catalogue)
    if warnings:
        print("WARN: no photo for", ", ".join(warnings), "(region placeholder used)")

    theme_name = itinerary.get("theme", "classic")
    plan = slideplan.build_slide_plan(itinerary, stops, theme=theme_name)
    out = deck_render.generate(plan, slug, itinerary.get("title", slug), DIST, theme_name=theme_name)
    print(f"\n{len(plan)} slides ({theme_name} theme) -> {os.path.join('dist', slug)}")
    for k in ("pdf", "pptx", "pptx_editable"):
        if out.get(k):
            print(f"  {k:14s} {os.path.relpath(out[k], ROOT)}")
        else:
            print(f"  {k:14s} (not available for the {theme_name} theme)")

    if itinerary.get("plan_content_data"):
        if theme_name == "classic":
            internal_plan = slideplan.build_slide_plan(itinerary, stops, internal=True, theme=theme_name)
            internal_pdf = deck_render.generate_internal_pdf(internal_plan, slug, DIST, theme_name=theme_name)
            print(f"  {'internal_pdf':14s} {os.path.relpath(internal_pdf, ROOT)}  (confidential — not for clients)")
        else:
            # Remove a stale internal PDF from an earlier classic-theme build
            # of this same slug — otherwise it lingers with old content.
            stale = os.path.join(DIST, slug, f"{slug}-internal.pdf")
            if os.path.exists(stale):
                os.remove(stale)
            print(f"  {'internal_pdf':14s} (not available for the {theme_name} theme — no Named Stays layout yet)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
