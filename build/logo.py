"""Encode the transparent logo art into logo.json for injection.

The canonical logo art lives in build/assets/{logo_light,logo_dark}.png
(transparent wordmarks). This step re-encodes them as lossless WebP data URIs —
smaller than the source PNGs, with crisp edges and alpha preserved. The browser
picks the format from the data-URI mime type, so the template needs no change.

To regenerate the PNGs from a fresh raster logo, see logo_from_raster.py.
"""
import os, io, json, base64
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "build", "assets")
OUT = os.path.join(ROOT, "build", "logo.json")

res = {}
for key, fname in [("logo_light", "logo_light.png"), ("logo_dark", "logo_dark.png")]:
    im = Image.open(os.path.join(ASSETS, fname)).convert("RGBA")
    buf = io.BytesIO()
    im.save(buf, format="WEBP", lossless=True, method=6)
    data = buf.getvalue()
    res[key] = "data:image/webp;base64," + base64.b64encode(data).decode("ascii")
    print(f"{key}: {len(data)//1024} KB")

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False)
print("written ->", OUT)
