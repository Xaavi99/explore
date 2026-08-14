"""Generate a client presentation from an itinerary.

    python build/deck.py itineraries/south-india-demo.json

Outputs to dist/<slug>/: <slug>.pdf, <slug>.pptx (image slides),
<slug>-editable.pptx (native/editable). The deck follows the company-overview
template (blue palette); brand slides are fixed and the region cards are built
from the picked destinations grouped by region.
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

    plan = slideplan.build_slide_plan(itinerary, stops)
    out = deck_render.generate(plan, slug, itinerary.get("title", slug), DIST)
    print(f"\n{len(plan)} slides -> {os.path.join('dist', slug)}")
    for k in ("pdf", "pptx", "pptx_editable"):
        print(f"  {k:14s} {os.path.relpath(out[k], ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
