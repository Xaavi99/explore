"""Run the full catalogue build pipeline, and optionally a presentation deck.

    python build/build_all.py                          # catalogue only
    python build/build_all.py --deck itineraries/x.json  # catalogue, then deck

Catalogue steps:
  parse.py   South_India_Catalogue.md            -> build/catalogue.json
  images.py  slides/*.jpg (per SPEC)             -> build/images.json   (needs Pillow)
  logo.py    build/assets/logo_{light,dark}.png  -> build/logo.json     (needs Pillow)
  build.py   template.html + the three JSON files -> exploreain-catalogue.html

--deck then runs deck.py on the given itinerary (needs python-pptx; ANTHROPIC_API_KEY
for live AI copy, otherwise deterministic fallback). The deck is intentionally
NOT part of the default build — it has extra dependencies and optional API cost.
"""
import subprocess, sys, os, argparse

HERE = os.path.dirname(os.path.abspath(__file__))


def run(script, *args):
    print("\n=== " + script + (" " + " ".join(args) if args else "") + " ===")
    subprocess.run([sys.executable, os.path.join(HERE, script), *args], check=True)


def main():
    ap = argparse.ArgumentParser(description="Build the catalogue (and optionally a deck).")
    ap.add_argument("--deck", metavar="ITINERARY",
                    help="after the catalogue build, generate a deck from this itinerary JSON")
    args = ap.parse_args()

    for step in ("parse.py", "images.py", "logo.py", "build.py"):
        run(step)
    print("\nCatalogue build complete.")

    if args.deck:
        run("deck.py", os.path.abspath(args.deck))
        print("\nDeck build complete.")


if __name__ == "__main__":
    main()
