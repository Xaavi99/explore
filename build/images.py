import os, io, json, base64
from PIL import Image, ImageOps
from imagemap import SPEC, SLIDES as SRC

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "build", "images.json")

# WebP data URIs — ~30% smaller than JPEG at matched quality, and rendered
# natively by every browser that can open a claude.ai Artifact. The catalogue
# is a single inlined file, so shrinking the photos (~94% of its bytes) is the
# only lever that meaningfully moves total size.


def encode(path, longedge, quality):
    im = Image.open(path)
    im = ImageOps.exif_transpose(im).convert("RGB")
    w, h = im.size
    scale = min(1.0, longedge / max(w, h))
    if scale < 1.0:
        im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="WEBP", quality=quality, method=6)
    data = buf.getvalue()
    b64 = base64.b64encode(data).decode("ascii")
    return "data:image/webp;base64," + b64, im.size, len(data), len(b64)


out = {}
total = 0
for key, (fname, longedge, q) in SPEC.items():
    uri, size, nbytes, nb64 = encode(os.path.join(SRC, fname), longedge, q)
    out[key] = uri
    total += nb64
    print(f"{key:12s} {size[0]}x{size[1]}  {nbytes//1024} KB  (b64 {nb64//1024} KB)")

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)
print(f"\nTOTAL base64: {total/1024/1024:.2f} MB  ->  {OUT}")
