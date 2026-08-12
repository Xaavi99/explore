import os, io, json, base64
from PIL import Image
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "slides", "jpuKa.jpg")
OUT = os.path.join(ROOT, "build", "logo.json")

im = Image.open(SRC).convert("RGB")
px = im.load()
W, H = im.size

# --- find content bbox (non-white) ---
def nonwhite(r, g, b):
    return min(r, g, b) < 235
minx, miny, maxx, maxy = W, H, 0, 0
for y in range(H):
    for x in range(W):
        r, g, b = px[x, y]
        if nonwhite(r, g, b):
            if x < minx: minx = x
            if y < miny: miny = y
            if x > maxx: maxx = x
            if y > maxy: maxy = y
pad = 8
minx = max(0, minx - pad); miny = max(0, miny - pad)
maxx = min(W, maxx + pad); maxy = min(H, maxy + pad)
crop = im.crop((minx, miny, maxx + 1, maxy + 1))
cw, ch = crop.size
print("bbox", (minx, miny, maxx, maxy), "crop", crop.size)

# --- sample the dominant blue (saturated blue pixels) ---
blues = Counter()
cp = crop.load()
for y in range(ch):
    for x in range(cw):
        r, g, b = cp[x, y]
        if b > r + 30 and b > g + 20 and b > 120:
            blues[(r // 8 * 8, g // 8 * 8, b // 8 * 8)] += 1
blue = blues.most_common(1)[0][0]
print("dominant blue rgb", blue, "-> #%02x%02x%02x" % blue)

def build(dark):
    out = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    op = out.load()
    for y in range(ch):
        for x in range(cw):
            r, g, b = cp[x, y]
            d = 255 - min(r, g, b)
            a = min(255, round(d * 1.4))
            if a <= 2:
                continue
            is_blue = (b > r + 25 and b > g + 15 and b > 110)
            if is_blue:
                nr, ng, nb = (77, 178, 250) if dark else (r, g, b)
            elif dark:
                L = int(0.299 * r + 0.587 * g + 0.114 * b)
                nl = 245 - L  # invert dark->light
                nr = ng = nb = max(0, min(255, nl))
            else:
                nr, ng, nb = r, g, b
            op[x, y] = (nr, ng, nb, a)
    # resize to height 120px
    th = 120
    tw = round(cw * th / ch)
    out = out.resize((tw, th), Image.LANCZOS)
    buf = io.BytesIO()
    out.save(buf, format="PNG", optimize=True)
    return buf.getvalue(), (tw, th)

res = {}
for key, dark in [("logo_light", False), ("logo_dark", True)]:
    data, size = build(dark)
    res[key] = "data:image/png;base64," + base64.b64encode(data).decode("ascii")
    print(f"{key}: {size[0]}x{size[1]}  {len(data)//1024} KB")

res["_blue"] = "#%02x%02x%02x" % blue
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False)
print("aspect (w/h):", round((crop.size[0] / crop.size[1]), 3))
print("written ->", OUT)
