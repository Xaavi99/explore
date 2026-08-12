# Catalogue build pipeline

Generates the single, self-contained `exploreain-catalogue.html` (published as a
claude.ai Artifact) from the source markdown, slide photos, and logo art.

## Build

```
python build/build_all.py
```

Requires Python 3 + Pillow (`pip install pillow`) for the image steps.

## Steps

| Script      | Input                                   | Output                     |
|-------------|-----------------------------------------|----------------------------|
| `parse.py`  | `../South_India_Catalogue.md`           | `catalogue.json`           |
| `images.py` | `../slides/*.jpg` (per `SPEC` dict)      | `images.json` (needs Pillow) |
| `logo.py`   | `assets/logo_{light,dark}.png`           | `logo.json`                |
| `build.py`  | `template.html` + the three JSON files   | `../exploreain-catalogue.html` |

`catalogue.json`, `images.json`, `logo.json` are generated intermediates
(git-ignored). The three inputs of record are the markdown, the photos in
`slides/`, and the logo PNGs in `build/assets/`.

## Mapping images to destinations

Two places, kept in sync:
- `images.py` `SPEC` — `key -> (slide filename, max long edge, jpeg quality)`
- `template.html` `DEST_IMG` — `DESTINATION NAME (uppercase) -> key`
  (and `EXP_IMG` for specific experience write-ups)

A destination with no key falls back to a region-hued placeholder card.

## Logo

`build/assets/logo_{light,dark}.png` are transparent wordmarks (the canonical
art). `logo_from_raster.py` archives the original technique for regenerating
them from a flat raster logo (needs the source image + Pillow).

---

# Presentation generator (itinerary → PDF + PPTX)

Turns an itinerary into a shareable client deck. **Separate from the catalogue
build** — it is not part of `build_all.py` and has extra dependencies.

```
pip install pillow pymupdf python-pptx anthropic
python build/deck.py itineraries/south-india-demo.json
```

Outputs to `dist/<slug>/`:
- `<slug>.pdf` — pixel-perfect image slides (pymupdf)
- `<slug>.pptx` — same image slides in PowerPoint (python-pptx)
- `<slug>-editable.pptx` — native editable text/shapes (python-pptx)

## Itinerary format (`itineraries/*.json`)

```json
{ "title": "...", "client": "...", "dates": "...", "prepared_by": "Exploreain",
  "cover_key": "kochi", "destinations": ["KOCHI", "MUNNAR", ...] }
```
`destinations` is an ordered list of UPPERCASE catalogue names; validated against
`catalogue.json` (run `parse.py` first if it's missing).

## Modules

| Script            | Role |
|-------------------|------|
| `theme.py`        | Blue palette + Windows font paths (mirrored from `template.html`) |
| `imagemap.py`     | Shared `SPEC` / `DEST_IMG` / `EXP_IMG` (also used by `images.py`) |
| `itinerary.py`    | Load + validate an itinerary against `catalogue.json` |
| `slideplan.py`    | Itinerary → ordered slide records (cover, overview, features, closing) |
| `deck_copy.py`    | AI headline+caption per destination + committed cache + fallback |
| `deck_layouts.py` | The single Pillow layout engine (all geometry/color/type lives here) |
| `deck_render.py`  | Slide plan → PDF + image-PPTX + editable-PPTX |
| `deck.py`         | CLI entry point |

## AI copy

`deck_copy.py` calls Claude Sonnet 5 (via the `anthropic` SDK) for a headline +
caption per destination, using **structured outputs**. Set `ANTHROPIC_API_KEY`
to enable it; without a key it uses deterministic fallback copy from the
catalogue, so the deck always builds. Pass `--no-ai` to force fallback.

Results are cached in **`build/copy_cache.json`** (committed, not git-ignored),
keyed on destination content + prompt version + model — so rebuilds cost nothing
and only new/changed destinations hit the API. `seed_cache.py` pre-loads
house-voice copy transcribed from `South India Tour Presentation.pdf`.

## Fonts

Headlines use **Palatino Linotype** (`pala.ttf`), captions **Segoe UI**, both
present on Windows; falls back to Georgia/Arial. Fonts are rasterized into the
image slides at build time, so the PDF and image-PPTX need no fonts on the
viewer's machine. The *editable* PPTX references the fonts by name, so its text
depends on the viewer having them.
