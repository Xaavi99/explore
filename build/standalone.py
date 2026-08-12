"""Wrap the artifact-format catalogue into a standalone page for static hosting
(e.g. GitHub Pages), written to docs/index.html.

    python build/standalone.py

The catalogue at repo root is authored in claude.ai "artifact" format (no
<html>/<head>/<body> — claude.ai supplies those). GitHub Pages needs a full
document named index.html; this adds the wrapper. Run it after build_all.py.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "exploreain-catalogue.html")
OUTDIR = os.path.join(ROOT, "docs")
OUT = os.path.join(OUTDIR, "index.html")

HEAD = (
    "<!doctype html>\n"
    '<html lang="en">\n<head>\n'
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    '<meta name="description" content="Exploreain — private, tailored South India journeys across Kerala, Goa, Karnataka and Tamil Nadu.">\n'
    "<title>South India Catalogue · Exploreain</title>\n"
    "</head>\n<body>\n"
)
FOOT = "\n</body>\n</html>\n"

with open(SRC, encoding="utf-8") as f:
    body = f.read()

os.makedirs(OUTDIR, exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(HEAD + body + FOOT)

# .nojekyll so GitHub Pages serves the file verbatim (no Jekyll processing)
open(os.path.join(OUTDIR, ".nojekyll"), "w").close()

print("wrote", OUT, "(%.2f MB)" % (os.path.getsize(OUT) / 1024 / 1024))
