import os, io, json, base64
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "slides")
OUT = os.path.join(ROOT, "build", "images.json")

# key: (filename, max_long_edge, quality)
SPEC = {
    "kochi":      ("fort kochi.jpg",                              1600, 80),
    "munnar":     ("grok-image-f041bdff-1e78-4a60-93de-cfd9f2f5c9d0.jpg", 1300, 80),
    "munnar_tea": ("04e895b2-e731-499b-b026-639f4fced1bf.jpg",    1100, 80),
    "alleppey":   ("grok-image-bbc2be8c-02a5-4d18-97d0-02c4587bbff7.jpg", 1300, 80),
    "canoe":      ("grok-image-11b713b1-f499-4204-a524-aef8fccb49a1.jpg", 1100, 80),
    "varkala":    ("grok-image-76ed940d-5eb6-46f9-a5a5-16ab6a76435f.jpg", 1500, 80),
    "temple":     ("56015745-261f-416a-87dd-b2e39150c58e.jpg",    1100, 80),
    "island":     ("e67d27fb-0a0f-4439-9831-99b294b8e485.jpg",    1100, 80),
    # --- newly matched destinations (2026-08-12) ---
    "coorg":         ("1RoVj.jpg", 1280, 78),
    "athirappilly":  ("7rfpM.jpg", 1280, 78),
    "pondicherry":   ("873Uj.jpg", 1280, 78),
    "kovalam":       ("9UuWM.jpg", 1280, 78),
    "hampi":         ("bclWF.jpg", 1280, 78),
    "srilanka":      ("krdOo.jpg", 1280, 78),
    "gokarna":       ("lRR66.jpg", 1280, 78),
    "goa_south":     ("PWjIa.jpg", 1280, 78),
    "mahabalipuram": ("QZ58N.jpg", 1280, 78),
    "thanjavur":     ("sJURK.jpg", 1280, 78),
    "mysore":        ("Soxby.jpg", 1280, 78),
    "thekkady":      ("SRCMN.jpg", 1280, 78),
    "wayanad":       ("sJYgN.jpg", 1280, 78),
    "ooty":          ("U2Xrw.jpg", 1280, 78),
    "andaman":       ("TNw6e.jpg", 1280, 78),
    "goa_north":     ("jDTno.jpg", 1280, 78),
    "bekal":         ("QLLkd.jpg", 1280, 78),
}

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
