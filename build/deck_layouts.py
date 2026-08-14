"""The single Pillow layout engine — draws each slide record to a PIL Image.

All geometry/color/typography lives here, so PDF and PPTX (which both consume
these PNGs) are pixel-identical. Sizes are expressed in 1280x720 "points" and
scaled by theme.RENDER_SCALE for crisp rasterization.

Layouts mirror the company-overview template, recolored to the blue palette:
  cover     — full-bleed hero
  sections  — image column + eyebrow/title/intro/labeled blocks (About, Map,
              Cultural, and the itinerary-driven Region cards)
  cards     — photo band header + a row of white cards (Stays, Themes)
  grid      — header + 2x3 white card grid (Why Choose)
  cta       — split brand panel + photo (Contact)
  quote     — full-bleed photo + centered italic quote (closing)
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
GOLD_HI = "#e9c983"  # lighter gold for eyebrows over dark photos

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


def _collage(paths, w, h):
    """Tile up to 4 photos into a WxH mosaic (photo-book feel)."""
    paths = [p for p in (paths or []) if p and os.path.exists(p)]
    if not paths:
        return placeholder(w, h, theme.BRAND_2)
    g = max(2, int(3 * S))
    canvas = Image.new("RGB", (w, h), theme.rgb(theme.PAPER))
    n = min(len(paths), 4)
    halfw, midh = (w - g) // 2, (h - g) // 2
    boxes = {
        1: [(0, 0, w, h)],
        2: [(0, 0, w, midh), (0, midh + g, w, h)],
        3: [(0, 0, halfw, midh), (halfw + g, 0, w, midh), (0, midh + g, w, h)],
        4: [(0, 0, halfw, midh), (halfw + g, 0, w, midh),
            (0, midh + g, halfw, h), (halfw + g, midh + g, w, h)],
    }[n]
    for (x0, y0, x1, y1), p in zip(boxes, paths[:n]):
        canvas.paste(cover_crop(load_photo(p), x1 - x0, y1 - y0), (x0, y0))
    return canvas


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


def _wrap_block(d, text, fnt, x, y, maxw, fill, spacing=1.3):
    lines = _wrap(d, text, fnt, maxw)
    asc, desc = fnt.getmetrics()
    return draw_lines(d, lines, fnt, x, y, fill, (asc + desc) * spacing)


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


def _over(base_rgb, overlay_rgba):
    return Image.alpha_composite(base_rgb.convert("RGBA"), overlay_rgba).convert("RGB")


def _photo_box(rec_image, tw, th, hue=None):
    if rec_image and os.path.exists(rec_image):
        return cover_crop(load_photo(rec_image), tw, th)
    return placeholder(tw, th, hue or theme.BRAND_2)


# ---------- section-block helper (labeled paragraph with a gold tick) ----------
def _labeled(d, x, y, maxw, label, body, label_color=None):
    lf = font(theme.SANS_SEMIBOLD, 11.5)
    th = _measure(d, "AG", lf)[1]
    d.rectangle([x, y, x + max(2, int(3 * S)), y + th], fill=theme.rgb(theme.GOLD))
    draw_tracked(d, label.upper(), lf, x + int(13 * S), y, label_color or theme.rgb(theme.GOLD), int(2.6 * S))
    y += th + int(9 * S)
    bf = font(theme.SANS_SEMIBOLD, 13)
    y = _wrap_block(d, body, bf, x, y, maxw, theme.rgb(theme.INK), spacing=1.28)
    return y + int(16 * S)


# ---------- layouts ----------
def layout_cover(rec):
    img = _photo_box(rec.get("image"), W, H)
    img = _over(img, vgrad_scrim((W, H), theme.rgb("#0a1520"), 0, 235, start=0.30))
    d = ImageDraw.Draw(img)
    x = MARGIN
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


def layout_sections(rec):
    """Image column on one side; eyebrow/title/intro + labeled blocks on the other.
    Drives About, Destination Map, Cultural Connection, and Region cards."""
    img = Image.new("RGB", (W, H), theme.rgb(theme.PAPER))
    side = rec.get("img_side", "left")
    imgw = int(W * 0.40)
    coll = _collage(rec.get("left_paths", []), imgw, H)
    if side == "left":
        img.paste(coll, (0, 0))
        tx0 = imgw + int(0.055 * W)
        tx1 = W - MARGIN
    else:
        img.paste(coll, (W - imgw, 0))
        tx0 = MARGIN
        tx1 = W - imgw - int(0.05 * W)
    maxw = tx1 - tx0
    d = ImageDraw.Draw(img)
    y = int(0.13 * H)
    ef = font(theme.SANS_SEMIBOLD, 12)
    draw_tracked(d, rec.get("eyebrow", "").upper(), ef, tx0, y, theme.rgb(theme.GOLD), int(3 * S))
    y += _measure(d, "AG", ef)[1] + int(16 * S)
    tcolor = theme.rgb(theme.BRAND_2) if rec.get("title_brand") else theme.rgb(theme.INK)
    hl, hf, hlh = fit(d, rec["title"], rec.get("title_font", theme.SERIF),
                      rec.get("title_pt", 38), 24, maxw, int(H * 0.26))
    y = draw_lines(d, hl, hf, tx0, y, tcolor, hlh)
    y += int(12 * S)
    _rule(d, tx0, y, int(0.05 * W), theme.rgb(theme.GOLD))
    y += int(24 * S)
    if rec.get("intro"):
        y = _wrap_block(d, rec["intro"], font(theme.SANS, 14.5), tx0, y, maxw,
                        theme.rgb(theme.INK_SOFT), spacing=1.32)
        y += int(20 * S)
    for label, body in rec["sections"]:
        y = _labeled(d, tx0, y, maxw, label, body)
    return img


def layout_cards(rec):
    """Top photo band with eyebrow/title, then a row of white cards on cream."""
    img = Image.new("RGB", (W, H), theme.rgb(theme.PAPER_3))
    d = ImageDraw.Draw(img)
    bandh = int(0.30 * H)
    band = _photo_box(rec.get("band"), W, bandh)
    band = _over(band, vgrad_scrim((W, bandh), theme.rgb("#08161f"), 110, 205))
    img.paste(band, (0, 0))
    ef = font(theme.SANS_SEMIBOLD, 12)
    ey = int(0.085 * H)
    draw_tracked(d, rec["eyebrow"].upper(), ef, MARGIN, ey, theme.rgb(GOLD_HI), int(3 * S))
    ty = ey + _measure(d, "AG", ef)[1] + int(14 * S)
    hl, hf, hlh = fit(d, rec["title"], theme.SERIF, 40, 26, int(W * 0.72), int(H * 0.14))
    draw_lines(d, hl, hf, MARGIN, ty, (255, 255, 255), hlh)

    y = bandh + int(0.055 * H)
    if rec.get("intro"):
        y = _wrap_block(d, rec["intro"], font(theme.SANS, 13.5), MARGIN, y, W - 2 * MARGIN,
                        theme.rgb(theme.INK_SOFT), spacing=1.3)
        y += int(0.03 * H)
    cards = rec["cards"]
    n = len(cards)
    gap = int(0.022 * W)
    cw = (W - 2 * MARGIN - gap * (n - 1)) // n
    cy = y
    chh = H - int(0.085 * H) - cy
    pad = int(24 * S)
    for i, card in enumerate(cards):
        cx = MARGIN + i * (cw + gap)
        d.rectangle([cx, cy, cx + cw, cy + chh], fill=theme.rgb(theme.WHITE),
                    outline=theme.rgb(theme.LINE), width=max(1, int(1 * S)))
        _rule(d, cx, cy, cw, theme.rgb(theme.GOLD), thick=max(3, int(4 * S)))
        yy = cy + pad + int(8 * S)
        title, body = card[0], card[1]
        suited = card[2] if len(card) > 2 else None
        yy = _wrap_block(d, title, font(theme.SERIF, 20), cx + pad, yy, cw - 2 * pad,
                         theme.rgb(theme.INK), spacing=1.06)
        yy += int(14 * S)
        _wrap_block(d, body, font(theme.SANS_SEMIBOLD, 12.5), cx + pad, yy, cw - 2 * pad,
                    theme.rgb(theme.INK_SOFT), spacing=1.32)
        if suited:
            sf = font(theme.SANS_SEMIBOLD, 10.5)
            sfh = _measure(d, "AG", sf)[1]
            sy = cy + chh - pad - sfh * 2 - int(10 * S)
            _rule(d, cx + pad, sy - int(14 * S), int(0.03 * W), theme.rgb(theme.GOLD))
            draw_tracked(d, "BEST SUITED FOR", sf, cx + pad, sy, theme.rgb(theme.GOLD), int(2 * S))
            sy += sfh + int(6 * S)
            d.text((cx + pad, sy), suited, font=font(theme.SANS, 12), fill=theme.rgb(theme.INK))
    return img


def layout_grid(rec):
    """Header + a 2x3 grid of white value cards (Why Choose)."""
    img = Image.new("RGB", (W, H), theme.rgb(theme.PAPER_3))
    d = ImageDraw.Draw(img)
    x = MARGIN
    y = int(0.09 * H)
    ef = font(theme.SANS_SEMIBOLD, 12)
    draw_tracked(d, rec["eyebrow"].upper(), ef, x, y, theme.rgb(theme.GOLD), int(3 * S))
    y += _measure(d, "AG", ef)[1] + int(14 * S)
    hl, hf, hlh = fit(d, rec["title"], theme.SERIF, 40, 26, int(W * 0.7), int(H * 0.14))
    y = draw_lines(d, hl, hf, x, y, theme.rgb(theme.INK), hlh)
    y += int(8 * S)
    if rec.get("intro"):
        itf = font(theme.SANS, 13.5)
        d.text((x, y), rec["intro"], font=itf, fill=theme.rgb(theme.INK_SOFT))
        y += _measure(d, "AG", itf)[1] + int(22 * S)
    cards = rec["cards"]
    cols = 3
    rows = (len(cards) + cols - 1) // cols
    gap = int(0.02 * W)
    cw = (W - 2 * MARGIN - gap * (cols - 1)) // cols
    top = y
    chh = (H - int(0.11 * H) - top - gap * (rows - 1)) // rows
    pad = int(24 * S)
    for i, (t, b) in enumerate(cards):
        r, c = divmod(i, cols)
        cx = MARGIN + c * (cw + gap)
        cy = top + r * (chh + gap)
        d.rectangle([cx, cy, cx + cw, cy + chh], fill=theme.rgb(theme.WHITE),
                    outline=theme.rgb(theme.LINE), width=max(1, int(1 * S)))
        _rule(d, cx, cy, cw, theme.rgb(theme.GOLD), thick=max(3, int(4 * S)))
        yy = cy + pad + int(6 * S)
        yy = _wrap_block(d, t, font(theme.SERIF, 19), cx + pad, yy, cw - 2 * pad,
                         theme.rgb(theme.INK), spacing=1.06)
        yy += int(10 * S)
        _wrap_block(d, b, font(theme.SANS, 13), cx + pad, yy, cw - 2 * pad,
                    theme.rgb(theme.INK_SOFT), spacing=1.3)
    return img


def layout_cta(rec):
    """Split: brand-blue panel with the call to action + full-bleed photo right."""
    img = Image.new("RGB", (W, H), theme.rgb(theme.BRAND_2))
    panelw = int(W * 0.52)
    img.paste(_photo_box(rec.get("image"), W - panelw, H, hue=theme.BRAND), (panelw, 0))
    d = ImageDraw.Draw(img)
    x = MARGIN
    maxw = panelw - MARGIN - int(0.03 * W)
    ef = font(theme.SANS_SEMIBOLD, 12)
    y = int(0.24 * H)
    draw_tracked(d, rec["eyebrow"].upper(), ef, x, y, theme.rgb(GOLD_HI), int(3 * S))
    y += _measure(d, "AG", ef)[1] + int(20 * S)
    hl, hf, hlh = fit(d, rec["title"], theme.SERIF, 42, 26, maxw, int(H * 0.4))
    y = draw_lines(d, hl, hf, x, y, (255, 255, 255), hlh)
    y += int(18 * S)
    _rule(d, x, y, int(0.05 * W), theme.rgb(theme.GOLD))
    y += int(28 * S)
    for text, strong in rec["lines"]:
        lf = font(theme.SANS_SEMIBOLD if strong else theme.SANS, 15 if strong else 14)
        d.text((x, y), text, font=lf, fill=(255, 255, 255) if strong else (205, 220, 235))
        y += _measure(d, "AG", lf)[1] + int(14 * S)
    return img


def layout_quote(rec):
    img = _photo_box(rec.get("image"), W, H)
    img = _over(img, vgrad_scrim((W, H), theme.rgb("#08161f"), 150, 150))
    d = ImageDraw.Draw(img)
    ql, qf, qlh = fit(d, "“" + rec["quote"] + "”", theme.SERIF_ITALIC, 34, 22,
                      int(W * 0.72), int(H * 0.5))
    block = qlh * len(ql)
    y = (H - block) // 2 - int(0.03 * H)
    for ln in ql:
        w = _measure(d, ln, qf)[0]
        d.text(((W - w) // 2, y), ln, font=qf, fill=(255, 255, 255))
        y += qlh
    y += int(22 * S)
    draw_tracked_centered(d, rec["attribution"], font(theme.SANS_SEMIBOLD, 12), W // 2, y,
                          theme.rgb(GOLD_HI), int(3.5 * S))
    return img


# ---------- watermark + footer (applied to every slide) ----------
_DARK_BOTTOM = {"cover", "cta", "quote"}  # bottom sits over a dark/photo area
_logo_cache = {}


def _load_logo(dark):
    path = LOGO_DARK if dark else LOGO_LIGHT
    if path not in _logo_cache:
        _logo_cache[path] = Image.open(path).convert("RGBA")
    return _logo_cache[path]


def add_branding(img, layout, rec=None):
    d = ImageDraw.Draw(img)
    dark = layout in _DARK_BOTTOM
    ff = font(theme.SANS_SEMIBOLD, 9.5)
    track = int(2.2 * S)
    fy = H - int(0.05 * H)
    fill = (255, 255, 255) if dark else theme.rgb(theme.INK_FAINT)
    fw = _tracked_width(d, FOOTER_TEXT, ff, track)

    logo = _load_logo(dark).copy()
    lh = int(0.040 * H)
    lw = round(logo.width * lh / logo.height)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    logo.putalpha(logo.split()[3].point(lambda v: int(v * 0.5)))
    ly = H - int(0.052 * H) - lh // 2
    gap = int(0.02 * W)

    # On split (sections) slides the image column fills one side, so the footer
    # + logo form a lockup on the paper (text) side; elsewhere the footer is
    # centered with the logo in the bottom-right corner.
    img_side = (rec or {}).get("img_side") if layout == "sections" else None
    if img_side == "right":      # text on the LEFT -> lockup bottom-left
        lx = MARGIN
        fx = lx + lw + gap
    elif img_side == "left":     # text on the RIGHT -> lockup bottom-right
        lx = W - MARGIN - lw
        fx = lx - gap - fw
    else:                        # full-bleed / grid / cards -> centered footer
        lx = W - MARGIN - lw
        fx = W // 2 - fw // 2

    sx = fx
    for ch in FOOTER_TEXT:
        d.text((sx, fy), ch, font=ff, fill=fill, anchor="lm")
        sx += _measure(d, ch, ff)[0] + track
    img.paste(logo, (lx, ly), logo)
    return img


LAYOUTS = {
    "cover": layout_cover,
    "sections": layout_sections,
    "cards": layout_cards,
    "grid": layout_grid,
    "cta": layout_cta,
    "quote": layout_quote,
}


def render_slide(rec):
    return add_branding(LAYOUTS[rec["layout"]](rec), rec["layout"], rec)
