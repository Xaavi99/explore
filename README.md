# Exploreain — South India

Two things live here:

1. **The catalogue** — a single, self-contained `exploreain-catalogue.html`: an
   editorial guide to 24 South India destinations, published as a claude.ai
   Artifact.
2. **The presentation generator** — turn an itinerary into a shareable client
   deck (PDF + PPTX) whose slides reuse the catalogue's photos and blue design.

## Setup

```
pip install pillow pymupdf python-pptx anthropic
```

Pillow + pymupdf are enough for the catalogue; `python-pptx` and `anthropic`
are only needed for decks.

## Build the catalogue

```
python build/build_all.py
```

Regenerates `exploreain-catalogue.html` from `South_India_Catalogue.md`, the
photos in `slides/`, and the logo art. To publish, republish that file to the
existing Artifact URL. Details: [`build/README.md`](build/README.md).

## Generate a client deck

```
python build/deck.py itineraries/south-india-demo.json
# or run the catalogue build then a deck in one go:
python build/build_all.py --deck itineraries/goa-karnataka.json
```

Outputs to `dist/<slug>/`: `<slug>.pdf`, `<slug>.pptx` (image slides), and
`<slug>-editable.pptx` (native editable text).

An itinerary is a small JSON file in `itineraries/` — a title, client, dates,
and an ordered list of UPPERCASE destination names (validated against the
catalogue). See `itineraries/south-india-demo.json`.

**AI copy:** set `ANTHROPIC_API_KEY` to have Claude write each slide's headline
and caption; results are cached in `build/copy_cache.json` (committed) so
rebuilds are free. Without a key, deterministic fallback copy is used, so the
deck always builds. Full detail: [`build/README.md`](build/README.md).

## Layout

```
South_India_Catalogue.md      source content (exported from the claude.ai Project)
slides/                       source photos
exploreain-catalogue.html     built catalogue (the published artifact)
build/                        the pipeline (see build/README.md)
itineraries/                  itinerary inputs for the deck generator
dist/                         generated decks (git-ignored)
```
