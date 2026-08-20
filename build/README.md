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
{ "title": "...", "client": "...", "dates": "...",
  "prepared_by": "Exploreain", "cover_key": "kochi",
  "destinations": ["KOCHI", "MUNNAR", ...],
  "plan_content": "kerala-signature-classic" }
```
`destinations` is an ordered list of UPPERCASE catalogue names; validated against
`catalogue.json` (run `parse.py` first if it's missing).

`plan_content` is optional and points at a `build/plan_content/<name>.json`
sidecar (see below) — when present, a route/day-by-day/named-stays sequence is
inserted right after the region cards. Every slide carries a company **footer**
and a faint logo **watermark** (`add_branding` in `deck_layouts.py`).

## Tailored-plan content (`plan_content`)

For Kerala, `planning/kerala/README.md` + `planning/kerala/NN-*.md` hold five
concierge-grade day-by-day models (route rationale, day-by-day, named stays).
Those are prose, written for a human reader — not slide-fit copy. A
`build/plan_content/<slug>.json` sidecar is the compressed, structured bridge
between a model and the renderer:

```json
{
  "route": [{"stop": "Kochi", "nights": 2, "why": "one-line reason, ~90-110 chars"}],
  "days": [{"day": 1, "label": "Arrive Kochi", "body": "1-2 sentences, ~140-260 chars"}],
  "stays": [{"stop": "Kochi", "name": "Brunton Boatyard (CGH Earth)", "why": "one line"}]
}
```
Committed to git (not gitignored), mirroring `copy_cache.json`. `day` may be a
range string (e.g. `"3–7"`) for a merged multi-day block — `slideplan._day_bound`
handles that when chunking day slides (3 days per slide by default).

This is authored by the **`deck-content`** agent
(`.claude/agents/deck-content.md`), not a build-time API script — there's no
`ANTHROPIC_API_KEY` in this environment, and a Claude Code subagent can read
and reason over the prose models directly. Give it a free-text requirement
("8-night Kerala honeymoon") or a specific model path; it picks/compresses the
content, writes the sidecar + itinerary JSON, and runs the build. Five
examples already exist — `build/plan_content/kerala-*.json` paired with
`itineraries/kerala-*.json` — copy the shape from those rather than starting
from scratch.

Rendered by two dedicated layouts in `deck_layouts.py`: `table` (route/nights)
and `days` (day-by-day, auto-chunked); named stays reuse the existing `grid`
layout as-is.

## Modules

| Script            | Role |
|-------------------|------|
| `theme.py`        | Blue palette + Windows font paths (mirrored from `template.html`) |
| `imagemap.py`     | Shared `SPEC` / `DEST_IMG` / `EXP_IMG` (also used by `images.py`) |
| `itinerary.py`    | Load + validate an itinerary against `catalogue.json`; attaches `plan_content` |
| `slideplan.py`    | Itinerary → ordered slide records (cover, overview, region cards, tailored-plan route/days/stays, closing) |
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
