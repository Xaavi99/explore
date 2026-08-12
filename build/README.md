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
