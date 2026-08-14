"""The single Pillow layout engine — draws each slide record to a PIL Image.

All geometry/color/typography lives here, so PDF and PPTX (which both consume
these PNGs) are pixel-identical. Sizes are expressed in 1280x720 "points" and
scaled by theme.RENDER_SCALE for crisp rasterization.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
import theme

S = theme.RENDER_SCALE
W, H = theme.PX_W, theme.PX_H
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_LIGHT = os.path.join(ROOT, "build", "assets", "logo_light.png")
LOGO_DARK = os.path.join(ROOT, "build", "assets", "logo_dark.png")

COMPANY = "Exploreain"
FOOTER_TEXT = "EXPLOREAIN  ·  PRIVATE SOUTH INDIA JOURNEYS"

MARGIN = int(0.058 * W)

_fc = {}


def font(path, pt):
    k = (path, pt)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, int(pt * S))
    return _fc[k]


# ---------- image helpers ----------
def load_photo(path):
    im = Image.open(path)
    return ImageOps.exif_transpose(im).convert("RGB")


def cover_crop(im, tw, th):
    sw, sh = im.size
    scale = max(tw / sw, th / sh)
    nw, nh = max(tw, round(sw * scale)), max(th, round(sh * scale))
    im = im.resize((nw, nh), Image.LANCZOS)
    x, y = (nw - tw) // 2, (nh - th) // 2
    return im.crop((x, y, x + tw, y + th))


def placeholder(tw, th, hue_hex):
    """Region-hued gradient stand-in when a photo is missing."""
    base = Image.new("RGB", (tw, th), theme.rgb(hue_hex))
    ov = Image.new("L", (tw, th))
    for yy in range(th):
        ImageDraw.Draw(ov).line([(0, yy), (tw, yy)], fill=int(60 * yy / th))
    dark = Image.new("RGB", (tw, th), theme.rgb("#06121a"))
    return Image.composite(dark, base, ov)


# ---------- text helpers ----------
def _measure(draw, text, fnt):
    b = draw.textbbox((0, 0), text, font=fnt)
    return b[2] - b[0], b[3] - b[1]


def _wrap(draw, text, fnt, maxw):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if not cur or _measure(draw, t, fnt)[0] <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, path, start_pt, min_pt, maxw, maxh, spacing=1.14):
    """Shrink font until wrapped text fits (maxw, maxh). Returns (lines, fnt, lh)."""
    pt = start_pt
    lines, fnt, lh = [text], font(path, start_pt), 0
    while pt >= min_pt:
        fnt = font(path, pt)
        lines = _wrap(draw, text, fnt, maxw)
        asc, desc = fnt.getmetrics()
        lh = (asc + desc) * spacing
        if lh * len(lines) <= maxh:
            break
        pt -= 2
    return lines, fnt, lh


def draw_lines(draw, lines, fnt, x, y, fill, lh):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def draw_tracked(draw, text, fnt, x, y, fill, tracking):
    """Uppercase label with letter-spacing (PIL has none natively)."""
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += _measure(draw, ch, fnt)[0] + tracking


def _tracked_width(draw, text, fnt, tracking):
    if not text:
        return 0
    w = -tracking
    for ch in text:
        w += _measure(draw, ch, fnt)[0] + tracking
    return w


def draw_tracked_centered(draw, text, fnt, cx, y, fill, tracking):
    draw_tracked(draw, text, fnt, cx - _tracked_width(draw, text, fnt, tracking) // 2, y, fill, tracking)


def _rule(draw, x, y, w, color, thick=None):
    thick = thick or max(2, int(3 * S))
    draw.rectangle([x, y, x + w, y + thick], fill=color)


# ---------- scrims ----------
def vgrad_scrim(size, color_rgb, a_top, a_bottom, start=0.0):
    """Vertical alpha gradient overlay (RGBA)."""
    w, h = size
    ov = Image.new("RGBA", size, color_rgb + (0,))
    px = ov.load()
    for yy in range(h):
        f = max(0.0, (yy / h - start) / (1 - start)) if yy / h >= start else 0.0
        a = int(a_top + (a_bottom - a_top) * f)
        for xx in range(w):
            px[xx, yy] = color_rgb + (a,)
    return ov


def hgrad_scrim(size, color_rgb, a_left, a_right, end=1.0):
    w, h = size
    ov = Image.new("RGBA", size, color_rgb + (0,))
    px = ov.load()
    for xx in range(w):
        f = min(1.0, (xx / w) / end) if end else 1.0
        a = int(a_left + (a_right - a_left) * f)
        col = color_rgb + (a,)
        for yy in range(h):
            px[xx, yy] = col
    return ov


def _over(base_rgb, overlay_rgba):
    return Image.alpha_composite(base_rgb.convert("RGBA"), overlay_rgba).convert("RGB")


# ---------- layouts ----------
def _photo_or_placeholder(rec, tw, th):
    if rec.get("image") and os.path.exists(rec["image"]):
        return cover_crop(load_photo(rec["image"]), tw, th)
    return placeholder(tw, th, theme.REGION_HUE.get(rec.get("region", ""), theme.BRAND_2))


def layout_cover(rec):
    img = _photo_or_placeholder(rec, W, H)
    img = _over(img, vgrad_scrim((W, H), theme.rgb("#0a1520"), 0, 235, start=0.30))
    d = ImageDraw.Draw(img)
    x = MARGIN
    # build stack bottom-up
    title_lines, tfnt, tlh = fit(d, rec["title"], theme.SERIF, 60, 34, int(W * 0.66), int(H * 0.42))
    cap = rec.get("caption", "")
    cfnt = font(theme.SANS, 15)
    _, ch = _measure(d, "Ag", cfnt)
    kfnt = font(theme.SANS_SEMIBOLD, 12)
    _, kh = _measure(d, "AG", kfnt)
    block_h = kh + int(18 * S) + tlh * len(title_lines) + (int(20 * S) + ch if cap else 0)
    y = H - int(0.11 * H) - block_h
    draw_tracked(d, rec["kicker"].upper(), kfnt, x, y, theme.rgb(theme.GOLD), int(3.5 * S))
    y += kh + int(18 * S)
    y = draw_lines(d, title_lines, tfnt, x, y, (255, 255, 255), tlh)
    if cap:
        y += int(20 * S) - tlh + (tlh - ch)
        d.text((x, y), cap, font=cfnt, fill=(235, 238, 242))
    return img


def layout_overview(rec):
    img = Image.new("RGB", (W, H), theme.rgb(theme.PAPER))
    d = ImageDraw.Draw(img)
    top = int(0.13 * H)
    hl, hf, hlh = fit(d, rec["headline"], theme.SERIF, 46, 30, int(W * 0.5), int(H * 0.3))
    draw_lines(d, hl, hf, MARGIN, top, theme.rgb(theme.INK), hlh)
    # caption top-right
    capx = int(W * 0.66)
    cf = font(theme.SANS, 14.5)
    cl = _wrap(d, rec["caption"], cf, W - MARGIN - capx)
    asc, desc = cf.getmetrics()
    draw_lines(d, cl, cf, capx, top + int(6 * S), theme.rgb(theme.INK_SOFT), (asc + desc) * 1.3)
    # thumbnails row
    thumbs = rec.get("thumbs", [])[:4]
    if thumbs:
        n = len(thumbs)
        gap = int(0.02 * W)
        avail = W - 2 * MARGIN
        tw = (avail - gap * (n - 1)) // n
        th = int(0.34 * H)
        ty = H - int(0.12 * H) - th
        for i, p in enumerate(thumbs):
            tx = MARGIN + i * (tw + gap)
            thumb = cover_crop(load_photo(p), tw, th) if os.path.exists(p) else placeholder(tw, th, theme.BRAND_2)
            img.paste(thumb, (tx, ty))
    return img


def _feature_text_block(d, rec, x, y, maxw, ink, soft, on_dark=False):
    _rule(d, x, y, int(0.045 * W), theme.rgb(theme.GOLD))
    y += int(30 * S)
    hl, hf, hlh = fit(d, rec["headline"], theme.SERIF, 44, 26, maxw, int(H * 0.42))
    y = draw_lines(d, hl, hf, x, y, ink, hlh)
    y += int(14 * S)
    cf = font(theme.SANS, 15)
    cl = _wrap(d, rec.get("caption", ""), cf, maxw)
    asc, desc = cf.getmetrics()
    draw_lines(d, cl, cf, x, y, soft, (asc + desc) * 1.34)


def layout_feature_panel(rec):
    """Left colored panel + headline over a full-bleed photo on the right."""
    img = _photo_or_placeholder(rec, W, H)
    img = _over(img, hgrad_scrim((W, H), theme.rgb(theme.BRAND_2), 245, 0, end=0.62))
    img = _over(img, vgrad_scrim((W, H), theme.rgb("#08161f"), 0, 150, start=0.45))
    d = ImageDraw.Draw(img)
    x = MARGIN
    maxw = int(W * 0.42)
    ef = font(theme.SANS_SEMIBOLD, 12)
    kfh = _measure(d, "AG", ef)[1]
    hl, hf, hlh = fit(d, rec["headline"], theme.SERIF, 46, 28, maxw, int(H * 0.4))
    cf = font(theme.SANS, 15)
    cl = _wrap(d, rec.get("caption", ""), cf, maxw)
    asc, desc = cf.getmetrics()
    clh = (asc + desc) * 1.34
    block = kfh + int(20 * S) + hlh * len(hl) + int(16 * S) + clh * len(cl)
    y = H - int(0.12 * H) - block
    draw_tracked(d, rec.get("eyebrow", "").upper(), ef, x, y, theme.rgb("#e9c983"), int(3 * S))
    y += kfh + int(20 * S)
    y = draw_lines(d, hl, hf, x, y, (255, 255, 255), hlh)
    y += int(16 * S)
    draw_lines(d, cl, cf, x, y, (232, 237, 242), clh)
    return img


def layout_feature_split(rec):
    """Photo fills the left half; text + gold rule on the paper right half."""
    img = Image.new("RGB", (W, H), theme.rgb(theme.PAPER))
    half = W // 2
    img.paste(_photo_or_placeholder(rec, half, H), (0, 0))
    d = ImageDraw.Draw(img)
    x = half + int(0.06 * W)
    maxw = W - MARGIN - x
    # eyebrow
    ef = font(theme.SANS_SEMIBOLD, 12)
    y = int(H * 0.30)
    draw_tracked(d, rec.get("eyebrow", "").upper(), ef, x, y, theme.rgb(theme.GOLD), int(3 * S))
    y += _measure(d, "AG", ef)[1] + int(22 * S)
    hl, hf, hlh = fit(d, rec["headline"], theme.SERIF, 42, 26, maxw, int(H * 0.36))
    y = draw_lines(d, hl, hf, x, y, theme.rgb(theme.INK), hlh)
    y += int(16 * S)
    cf = font(theme.SANS, 15)
    cl = _wrap(d, rec.get("caption", ""), cf, maxw)
    asc, desc = cf.getmetrics()
    draw_lines(d, cl, cf, x, y, theme.rgb(theme.INK_SOFT), (asc + desc) * 1.34)
    return img


def layout_feature_framed(rec):
    """Text on the left; a framed photo on the right, on paper."""
    img = Image.new("RGB", (W, H), theme.rgb(theme.PAPER))
    d = ImageDraw.Draw(img)
    # framed photo right
    fx0 = int(W * 0.57)
    fx1 = W - MARGIN
    fy0 = int(H * 0.16)
    fy1 = H - int(H * 0.16)
    fw, fh = fx1 - fx0, fy1 - fy0
    photo = _photo_or_placeholder(rec, fw, fh)
    img.paste(photo, (fx0, fy0))
    # text left, vertically centered-ish
    x = MARGIN
    maxw = int(W * 0.40)
    ef = font(theme.SANS_SEMIBOLD, 12)
    hl, hf, hlh = fit(d, rec["headline"], theme.SERIF, 44, 26, maxw, int(H * 0.4))
    cf = font(theme.SANS, 15)
    cl = _wrap(d, rec.get("caption", ""), cf, maxw)
    asc, desc = cf.getmetrics()
    clh = (asc + desc) * 1.34
    ekh = _measure(d, "AG", ef)[1]
    block = ekh + int(22 * S) + int(30 * S) + hlh * len(hl) + int(16 * S) + clh * len(cl)
    y = (H - block) // 2
    draw_tracked(d, rec.get("eyebrow", "").upper(), ef, x, y, theme.rgb(theme.GOLD), int(3 * S))
    y += ekh + int(22 * S)
    _rule(d, x, y, int(0.045 * W), theme.rgb(theme.GOLD))
    y += int(30 * S)
    y = draw_lines(d, hl, hf, x, y, theme.rgb(theme.INK), hlh)
    y += int(16 * S)
    draw_lines(d, cl, cf, x, y, theme.rgb(theme.INK_SOFT), clh)
    return img


def layout_closing(rec):
    img = Image.new("RGB", (W, H), theme.rgb(theme.PAPER))
    d = ImageDraw.Draw(img)
    x = MARGIN
    y = int(H * 0.32)
    # logo
    if os.path.exists(LOGO_LIGHT):
        logo = Image.open(LOGO_LIGHT).convert("RGBA")
        lh = int(0.075 * H)
        lw = round(logo.width * lh / logo.height)
        logo = logo.resize((lw, lh), Image.LANCZOS)
        img.paste(logo, (x, y), logo)
        y += lh + int(34 * S)
    _rule(d, x, y, int(0.045 * W), theme.rgb(theme.GOLD))
    y += int(30 * S)
    hl, hf, hlh = fit(d, rec["title"], theme.SERIF, 48, 30, int(W * 0.7), int(H * 0.3))
    y = draw_lines(d, hl, hf, x, y, theme.rgb(theme.INK), hlh)
    y += int(16 * S)
    cf = font(theme.SANS, 15.5)
    cl = _wrap(d, rec.get("caption", ""), cf, int(W * 0.5))
    asc, desc = cf.getmetrics()
    draw_lines(d, cl, cf, x, y, theme.rgb(theme.INK_SOFT), (asc + desc) * 1.34)
    return img


def layout_dashboard(rec):
    """Opening 'by the numbers' slide — a row/grid of real-figure stat tiles."""
    img = Image.new("RGB", (W, H), theme.rgb(theme.PAPER))
    d = ImageDraw.Draw(img)
    x = MARGIN
    y = int(0.11 * H)
    ef = font(theme.SANS_SEMIBOLD, 12)
    draw_tracked(d, rec.get("eyebrow", "").upper(), ef, x, y, theme.rgb(theme.GOLD), int(3 * S))
    y += _measure(d, "AG", ef)[1] + int(20 * S)
    _rule(d, x, y, int(0.045 * W), theme.rgb(theme.GOLD))
    y += int(28 * S)
    hl, hf, hlh = fit(d, rec["title"], theme.SERIF, 44, 26, int(W * 0.84), int(H * 0.22))
    y = draw_lines(d, hl, hf, x, y, theme.rgb(theme.INK), hlh)

    tiles = rec.get("tiles", [])
    n = len(tiles) or 1
    cols = n if n <= 4 else 3
    rows = (n + cols - 1) // cols
    gap = int(0.022 * W)
    top = y + int(0.06 * H)
    bottom = H - int(0.155 * H)  # leave room for footer + watermark
    tw = (W - 2 * MARGIN - gap * (cols - 1)) // cols
    th = (bottom - top - gap * (rows - 1)) // max(1, rows)
    num_pt = 68 if rows == 1 else 56

    for i, (val, label) in enumerate(tiles):
        r, c = divmod(i, cols)
        tx = MARGIN + c * (tw + gap)
        ty = top + r * (th + gap)
        d.rounded_rectangle([tx, ty, tx + tw, ty + th], radius=int(14 * S),
                            fill=theme.rgb(theme.PAPER_2), outline=theme.rgb(theme.LINE), width=max(1, int(1 * S)))
        _rule(d, tx + int(26 * S), ty + int(26 * S), int(30 * S), theme.rgb(theme.GOLD))
        nf = font(theme.SERIF, num_pt)
        nh = _measure(d, val, nf)[1]
        lf = font(theme.SANS_SEMIBOLD, 12.5)
        lh = _measure(d, "AG", lf)[1]
        block = nh + int(16 * S) + lh
        by = ty + (th - block) // 2 + int(12 * S)
        d.text((tx + tw // 2, by), val, font=nf, fill=theme.rgb(theme.BRAND), anchor="ma")
        draw_tracked_centered(d, label.upper(), lf, tx + tw // 2, by + nh + int(16 * S),
                              theme.rgb(theme.INK_FAINT), int(2.4 * S))
    return img


def layout_data_card(rec):
    """Per-location DATA card: hero photo with the location's figures over a scrim."""
    img = _photo_or_placeholder(rec, W, H)
    img = _over(img, vgrad_scrim((W, H), theme.rgb("#08161f"), 165, 0, start=0.0))
    img = _over(img, vgrad_scrim((W, H), theme.rgb("#08161f"), 0, 232, start=0.40))
    d = ImageDraw.Draw(img)
    x = MARGIN
    ef = font(theme.SANS_SEMIBOLD, 12)
    y = int(0.12 * H)
    draw_tracked(d, rec.get("eyebrow", "").upper(), ef, x, y, theme.rgb("#e9c983"), int(3 * S))
    y += _measure(d, "AG", ef)[1] + int(16 * S)
    nl, nf, nlh = fit(d, rec["name"].title(), theme.SERIF, 60, 34, int(W * 0.72), int(H * 0.3))
    draw_lines(d, nl, nf, x, y, (255, 255, 255), nlh)

    cells = [
        (str(rec.get("experiences", 0)), "Experiences", True),
        (str(rec.get("attractions", 0)), "Attractions", True),
        (rec.get("district", "—"), "District", False),
    ]
    cw = (W - 2 * MARGIN) // 3
    ry = int(0.65 * H)
    for i, (val, label, isnum) in enumerate(cells):
        cx = MARGIN + i * cw
        _rule(d, cx, ry, int(32 * S), theme.rgb(theme.GOLD))
        vy = ry + int(22 * S)
        if isnum:
            vf = font(theme.SERIF, 54)
            d.text((cx, vy), val, font=vf, fill=(255, 255, 255))
            vh = _measure(d, val, vf)[1]
        else:
            vl, vf, vlh = fit(d, val, theme.SERIF, 30, 19, cw - int(24 * S), int(0.16 * H))
            yy = vy
            for ln in vl:
                d.text((cx, yy), ln, font=vf, fill=(255, 255, 255))
                yy += vlh
            vh = vlh * len(vl)
        lf = font(theme.SANS_SEMIBOLD, 11.5)
        draw_tracked(d, label.upper(), lf, cx, vy + vh + int(12 * S), (219, 227, 234), int(2.5 * S))
    return img


# ---------- watermark + footer (applied to every slide) ----------
_DARK_BOTTOM = {"cover", "feature-panel", "data"}  # bottom sits over a dark/photo area
_logo_cache = {}


def _load_logo(dark):
    path = LOGO_DARK if dark else LOGO_LIGHT
    if path not in _logo_cache:
        _logo_cache[path] = Image.open(path).convert("RGBA")
    return _logo_cache[path]


def add_branding(img, layout):
    d = ImageDraw.Draw(img)
    # footer: company name, bottom-centre, colour adapted to the slide
    ff = font(theme.SANS_SEMIBOLD, 9.5)
    track = int(2.2 * S)
    fy = H - int(0.05 * H)
    sx = W // 2 - _tracked_width(d, FOOTER_TEXT, ff, track) // 2
    if layout in _DARK_BOTTOM:
        fill, stroke = (255, 255, 255), 0
    elif layout in ("feature-split", "feature-framed"):
        fill, stroke = (255, 255, 255), max(1, int(2 * S))
    else:
        fill, stroke = theme.rgb(theme.INK_FAINT), 0
    for ch in FOOTER_TEXT:
        if stroke:
            d.text((sx, fy), ch, font=ff, fill=fill, stroke_width=stroke, stroke_fill=(8, 18, 26), anchor="lm")
        else:
            d.text((sx, fy), ch, font=ff, fill=fill, anchor="lm")
        sx += _measure(d, ch, ff)[0] + track
    # watermark: faint logo wordmark, bottom-right corner
    logo = _load_logo(layout in _DARK_BOTTOM).copy()
    lh = int(0.040 * H)
    lw = round(logo.width * lh / logo.height)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    logo.putalpha(logo.split()[3].point(lambda v: int(v * 0.5)))
    img.paste(logo, (W - MARGIN - lw, H - int(0.052 * H) - lh // 2), logo)
    return img


LAYOUTS = {
    "cover": layout_cover,
    "dashboard": layout_dashboard,
    "overview": layout_overview,
    "data": layout_data_card,
    "feature-panel": layout_feature_panel,
    "feature-split": layout_feature_split,
    "feature-framed": layout_feature_framed,
    "closing": layout_closing,
}


def render_slide(rec):
    return add_branding(LAYOUTS[rec["layout"]](rec), rec["layout"])
