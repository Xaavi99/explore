"""The "cinematic journey" layout engine — dark road-trip themed slides.

Separate from deck_layouts.py (the blue company-overview engine, untouched).
See design/theme.md for the reference brief + mockups. Palette/fonts in
theme_journey.py.

Phase 2 of the build plan: this module currently holds only the road/path
geometry primitives (the highest-risk, most novel piece), sanity-checked via
the __main__ block below before any real slide is built on top of them.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import theme_journey as J
import deck_layouts as L  # reuse image loading/cropping + text-wrap helpers

S = J.RENDER_SCALE
W, H = J.PX_W, J.PX_H
MARGIN = int(0.058 * W)

_fc = {}


def font(path, pt):
    k = (path, pt)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, int(pt * S))
    return _fc[k]


# ---------- road/path geometry ----------
#
# Rebuilt after the first pass looked cramped/flat: the reference mockups
# (design/theme-day*.jpg) never plot the whole multi-stop route on a single
# day slide — each one shows a short two-stop window (previous stop, dim,
# near the top; current stop, glowing, further down), one gentle bend, a
# TAPERED ribbon (narrow/far at top, wide/near at bottom) with a beveled
# two-tone surface, and teardrop map-pins rather than plain circles. The
# full multi-stop road (road_column, below) is kept for a future
# route-overview slide, but now shares these same upgraded primitives.
def _road_x(t, x_left, x_right, cycles, phase):
    """t in [0,1] -> x position on a winding sine curve within [x_left, x_right]."""
    center = (x_left + x_right) / 2
    amplitude = (x_right - x_left) / 2 * 0.82  # margin so the curve doesn't clip
    return center + amplitude * math.sin(t * cycles * 2 * math.pi + phase)


def road_points(y_top, y_bottom, x_left, x_right, n_samples=240, cycles=2.4, phase=0.0):
    """Densely sampled (x, y) points along the winding road, top to bottom."""
    pts = []
    for i in range(n_samples + 1):
        t = i / n_samples
        y = y_top + t * (y_bottom - y_top)
        x = _road_x(t, x_left, x_right, cycles, phase)
        pts.append((x, y))
    return pts


def stop_positions(n_stops, y_top, y_bottom, x_left, x_right, cycles=2.4, phase=0.0):
    """n_stops (x, y) pin centers, evenly spaced by t along the same curve
    road_points draws — not true arc-length spacing, but plenty for a
    static illustration (this isn't a physically accurate map)."""
    pts = []
    for i in range(n_stops):
        t = i / (n_stops - 1) if n_stops > 1 else 0.0
        y = y_top + t * (y_bottom - y_top)
        x = _road_x(t, x_left, x_right, cycles, phase)
        pts.append((x, y))
    return pts


def _perp(dx, dy):
    n = math.hypot(dx, dy) or 1.0
    return (-dy / n, dx / n)


def _tangent_angle(pts, i):
    """Tangent direction in degrees (0 = pointing straight down) at sample
    index i, from its neighbors — used to orient the car along the curve."""
    if i <= 0:
        dx, dy = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
    elif i >= len(pts) - 1:
        dx, dy = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    else:
        dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
    return math.degrees(math.atan2(dx, dy))


def _road_ribbon(pts, w_top, w_bottom):
    """Tapered ribbon polygon — narrow at the top (far/early), wide at the
    bottom (near/current) — the perspective cue the flat-width first draft
    was missing entirely."""
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        t = i / (n - 1) if n > 1 else 0.0
        w = w_top + (w_bottom - w_top) * t
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == n - 1:
            dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
        else:
            dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
        px, py = _perp(dx, dy)
        left.append((x + px * w / 2, y + py * w / 2))
        right.append((x - px * w / 2, y - py * w / 2))
    return left + right[::-1]


def draw_road(draw, pts, w_top, w_bottom):
    """Beveled asphalt ribbon (dark edge + lighter inset surface, faking a
    raised/glossy look) + a dashed center line — takes an already-computed
    point list so both the windowed (2-stop) and full (N-stop) roads share
    one drawing routine."""
    draw.polygon(_road_ribbon(pts, w_top, w_bottom), fill=J.rgb(J.ROAD_EDGE))
    draw.polygon(_road_ribbon(pts, w_top * 0.72, w_bottom * 0.72), fill=J.rgb(J.ROAD_SURFACE))
    dash_w = max(2, int(2.2 * S))
    dash_len, gap_len = 5, 6
    i = 0
    while i < len(pts) - 1:
        if (i // dash_len) % 2 == 0:
            j = min(i + dash_len, len(pts) - 1)
            draw.line(pts[i:j + 1], fill=J.rgb(J.TEXT_SOFT), width=dash_w, joint="curve")
        i += dash_len if (i // dash_len) % 2 == 0 else gap_len


def _glow_dot(color_rgb, radius, blur):
    """A soft radial glow as a standalone RGBA image, for pasting under a
    crisp pin marker (cheap approximation of a bloom/halo effect)."""
    size = (radius + blur) * 2
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([blur, blur, blur + radius * 2, blur + radius * 2], fill=color_rgb + (160,))
    return im.filter(ImageFilter.GaussianBlur(blur / 2))


_glow_cache = {}


def draw_map_pin(img, x, y, r, state):
    """Teardrop map-pin (circular head + tapering point + small inner
    accent dot). (x, y) is the pin's ANCHOR — the tip, planted on the road —
    with the head floating above it, matching normal map-pin convention (the
    reference mockups' pins visibly touch the road at a point, not straddle
    it centered). state: 'done' | 'current' | 'future'."""
    head_cy = y - r * 1.15
    if state == "current":
        glow = _glow_cache.get("glow")
        if glow is None:
            glow = _glow_dot(J.rgb(J.GLOW), r, int(22 * S))
            _glow_cache["glow"] = glow
        img.paste(glow, (int(x - glow.width / 2), int(head_cy - glow.height / 2)), glow)
        fill, ring = J.rgb(J.GLOW), J.rgb(J.TEXT)
    elif state == "done":
        fill, ring = J.rgb(J.GLOW_DIM), J.rgb(J.PANEL_LINE)
    else:
        fill, ring = J.rgb(J.FUTURE), J.rgb(J.PANEL_LINE)
    d = ImageDraw.Draw(img)
    ang = math.radians(45)
    bx1, by1 = x - r * math.sin(ang), head_cy + r * math.cos(ang)
    bx2, by2 = x + r * math.sin(ang), head_cy + r * math.cos(ang)
    d.polygon([(bx1, by1), (x, y), (bx2, by2)], fill=fill)
    d.ellipse([x - r, head_cy - r, x + r, head_cy + r], fill=fill, outline=ring, width=max(1, int(2 * S)))
    ir = r * 0.3
    d.ellipse([x - ir, head_cy - ir, x + ir, head_cy + ir], fill=ring)


def draw_car(img, x, y, angle_deg=0.0):
    """Small stylized car glyph — two-tone chassis/cabin + wheel hints +
    a soft contact shadow — oriented to the road's local tangent rather
    than always pointing straight down."""
    w, h = int(22 * S), int(36 * S)
    pad = int(12 * S)
    body = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    cx, cy = body.width // 2, body.height // 2
    bd.ellipse([cx - w * 0.55, cy + h * 0.30, cx + w * 0.55, cy + h * 0.50], fill=(0, 0, 0, 90))
    for wx in (cx - w * 0.56, cx + w * 0.56):
        bd.rounded_rectangle([wx - int(3 * S), cy - h * 0.30, wx + int(3 * S), cy - h * 0.02],
                              radius=int(2 * S), fill=J.rgb("#454e5a"))
        bd.rounded_rectangle([wx - int(3 * S), cy + h * 0.04, wx + int(3 * S), cy + h * 0.32],
                              radius=int(2 * S), fill=J.rgb("#454e5a"))
    bd.rounded_rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
                          radius=int(9 * S), fill=J.rgb(J.TEXT))
    bd.rounded_rectangle([cx - w * 0.32, cy - h * 0.30, cx + w * 0.32, cy + h * 0.12],
                          radius=int(5 * S), fill=J.rgb(J.BG_2))
    body = body.rotate(-angle_deg, resample=Image.BICUBIC, center=(cx, cy))
    img.paste(body, (int(x - body.width / 2), int(y - body.height / 2)), body)


def road_column(n_stops, current_index, x_left, x_right, y_top, y_bottom,
                 cycles=None, phase=0.0):
    """The road and car are the main characters of this deck: ONE continuous
    route is drawn on every day slide, with the car parked at that day's
    station — its position visibly further down the same road on each
    subsequent slide, so flipping through the deck reads as the car
    progressing along the trip (the only "movement" a static PDF/PPTX can
    honestly give).

    `cycles` (bend count) auto-scales with n_stops when not overridden, so a
    3-stop and an 11-stop itinerary both read as gentle winding curves
    rather than a tight, cramped coil. Pin radius also scales down slightly
    for longer routes so pins don't crowd each other.

    Returns (image, pad): an RGBA image sized to fit the (x_left..x_right,
    y_top..y_bottom) box plus a `pad`-sized margin (for glow bleed), and that
    pad value. **Callers must paste at `(x_left - pad, y_top - pad)`** for
    the road content to land at the intended absolute position — the image
    is NOT simply anchored at (x_left, y_top)."""
    if cycles is None:
        cycles = max(0.9, min(2.2, n_stops * 0.22))
    pad = int(30 * S)
    img = Image.new("RGBA", (int(x_right - x_left + 2 * pad), int(y_bottom - y_top + 2 * pad)), (0, 0, 0, 0))
    ox, oy = pad - x_left, pad - y_top
    pts = road_points(y_top + oy, y_bottom + oy, x_left + ox, x_right + ox, cycles=cycles, phase=phase)
    draw = ImageDraw.Draw(img)
    draw_road(draw, pts, w_top=int(9 * S), w_bottom=int(17 * S))
    stop_pts = stop_positions(n_stops, y_top + oy, y_bottom + oy, x_left + ox, x_right + ox, cycles=cycles, phase=phase)
    r_current = max(9, 13 - max(0, n_stops - 5) * 0.4) * S
    r_other = max(6, 8 - max(0, n_stops - 5) * 0.3) * S
    for i, (x, y) in enumerate(stop_pts):
        state = "current" if i == current_index else ("done" if i < current_index else "future")
        draw_map_pin(img, x, y, int(r_current if state == "current" else r_other), state)
    if 0 <= current_index < len(stop_pts):
        # Walk forward ALONG the sampled curve from the pin, rather than
        # offsetting straight down in y — a fixed vertical offset drifts
        # off the road at sharp bends (a real bug: at a sine-wave peak the
        # road doubles back, so "straight down" from the pin lands in open
        # space beside the road, not on it).
        t_cur = (current_index / (n_stops - 1)) if n_stops > 1 else 0.0
        idx_cur = round(t_cur * (len(pts) - 1))
        margin = max(6, len(pts) // (n_stops * 3))
        # Walk forward (car "arriving" at the stop) when there's road left
        # to do so; at the LAST stop there isn't, so walk backward instead —
        # otherwise the car collides with the pin at the road's dead end.
        idx_car = idx_cur + margin if idx_cur + margin <= len(pts) - 1 else max(0, idx_cur - margin)
        car_x, car_y = pts[idx_car]
        draw_car(img, car_x, car_y, angle_deg=_tangent_angle(pts, idx_car))
    return img, pad


def paste_road(canvas_rgba, n_stops, current_index, x_left, x_right, y_top, y_bottom, **kw):
    """road_column() + correctly-offset paste onto canvas_rgba, in one call —
    the safe way to place a road; avoids the pad-offset footgun directly."""
    road, pad = road_column(n_stops, current_index, x_left, x_right, y_top, y_bottom, **kw)
    canvas_rgba.paste(road, (int(x_left - pad), int(y_top - pad)), road)


# ---------- small outline icons (restrained set — distance/time/stay only;
# no generic travel-app icons like "buses" that don't fit a private-car,
# named-guide operator) ----------
def icon_clock(draw, cx, cy, r, color, width):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)
    draw.line([cx, cy, cx, cy - r * 0.55], fill=color, width=width)
    draw.line([cx, cy, cx + r * 0.4, cy], fill=color, width=width)


def icon_pin(draw, cx, cy, r, color, width):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)
    draw.ellipse([cx - r * 0.35, cy - r * 0.35, cx + r * 0.35, cy + r * 0.35], fill=color)


def icon_home(draw, cx, cy, r, color, width):
    draw.line([cx - r, cy, cx, cy - r, cx + r, cy], fill=color, width=width, joint="curve")
    draw.line([cx - r * 0.6, cy - r * 0.1, cx - r * 0.6, cy + r * 0.7,
               cx + r * 0.6, cy + r * 0.7, cx + r * 0.6, cy - r * 0.1], fill=color, width=width, joint="curve")


ICONS = {"time": icon_clock, "pin": icon_pin, "stay": icon_home}


def _glass_panel(img_rgba, box, radius, fill_hex=J.BG_2, alpha=210, line_hex=J.PANEL_LINE):
    overlay = Image.new("RGBA", img_rgba.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle(box, radius=radius, fill=J.rgb(fill_hex) + (alpha,),
                          outline=J.rgb(line_hex) + (255,), width=max(1, int(1 * S)))
    return Image.alpha_composite(img_rgba, overlay)


def _highlights_height(d, items, colw):
    """Natural height the HIGHLIGHTS column will draw at, mirroring the real
    draw loop's spacing exactly — used to content-size the panel instead of
    always stretching it to fill available space (a light-content day was
    leaving a large empty card; see layout_journey_day)."""
    lbl_f = font(J.SANS_SEMIBOLD, 11)
    bf = font(J.SANS, 12.5)
    h = L._measure(d, "AG", lbl_f)[1] + int(10 * S)
    for item in items:
        h += L._text_h(d, item, bf, colw, spacing=1.25) + int(6 * S)
    return h


def _activities_height(d, activities, colw):
    """Natural height the TODAY (Morning/Afternoon/Evening/Night) column
    will draw at — see _highlights_height."""
    lbl_f = font(J.SANS_SEMIBOLD, 11)
    parts_f = font(J.SANS_SEMIBOLD, 11.5)
    bf = font(J.SANS, 12.5)
    h = L._measure(d, "AG", lbl_f)[1] + int(10 * S)
    for part in ("morning", "afternoon", "evening", "night"):
        val = (activities or {}).get(part)
        if not val:
            continue
        h += L._measure(d, "AG", parts_f)[1] + int(4 * S)
        h += L._text_h(d, val, bf, colw, spacing=1.22) + int(10 * S)
    return h


def _stat_row(draw, x, y, stats):
    """A slim, single row of icon + label/value pairs (distance/time/next-
    stop/stay-tier) — restrained, not a full app-style toolbar."""
    lf = font(J.SANS_SEMIBOLD, 10.5)
    vf = font(J.SANS, 13)
    cx = x
    for key, label, value in stats:
        if not value:
            continue
        r = int(9 * S)
        icon_fn = ICONS.get(key, icon_pin)
        icon_fn(draw, cx + r, y + r, r, J.rgb(J.GLOW), max(1, int(1.6 * S)))
        tx = cx + 2 * r + int(10 * S)
        draw.text((tx, y - int(2 * S)), label.upper(), font=lf, fill=J.rgb(J.TEXT_FAINT))
        draw.text((tx, y + int(13 * S)), value, font=vf, fill=J.rgb(J.TEXT))
        w = max(L._measure(draw, label.upper(), lf)[0], L._measure(draw, value, vf)[0])
        cx = tx + w + int(36 * S)


def layout_journey_day(rec):
    """One day of the tailored-plan deck: road (current stop lit) + hero/
    support photo + highlights + Morning/Afternoon/Evening/Night + a slim
    stats row. Dark cinematic theme — see design/theme.md."""
    img = Image.new("RGBA", (W, H), J.rgb(J.BG) + (255,))
    d = ImageDraw.Draw(img)

    # wordmark, top-left (text treatment, matches the reference exactly:
    # "explore" light + "ain" glow — no image asset needed)
    wf = font(J.SANS_BOLD, 20)
    d.text((MARGIN, int(0.045 * H)), "explore", font=wf, fill=J.rgb(J.TEXT))
    w0 = L._measure(d, "explore", wf)[0]
    d.text((MARGIN + w0, int(0.045 * H)), "ain", font=wf, fill=J.rgb(J.GLOW))

    # day counter, top-right
    dcf = font(J.SANS_SEMIBOLD, 13)
    dc_text = f"DAY {rec['day_of']} OF {rec['day_total']}"
    dcw = L._measure(d, dc_text, dcf)[0]
    d.text((W - MARGIN - dcw, int(0.05 * H)), dc_text, font=dcf, fill=J.rgb(J.TEXT_SOFT))

    # ---- road (left) — the full route, car parked at today's station (see
    # road_column's docstring: this is what makes the deck feel like the car
    # is progressing, one slide at a time) ----
    road_x0, road_x1 = MARGIN, int(0.26 * W)
    road_y0, road_y1 = int(0.14 * H), int(0.92 * H)
    paste_road(img, len(rec["route"]), rec["current_index"], road_x0, road_x1, road_y0, road_y1)

    # ---- content column (right) ----
    cx0 = road_x1 + int(0.03 * W)
    cx1 = W - MARGIN
    maxw = cx1 - cx0
    y = int(0.14 * H)

    hl, hf, hlh = L.fit(d, rec["title"], J.SANS_BOLD, 44, 28, maxw, int(0.12 * H))
    y = L.draw_lines(d, hl, hf, cx0, y, J.rgb(J.TEXT), hlh)
    if rec.get("subtitle"):
        y += int(6 * S)
        y = L._wrap_block(d, rec["subtitle"], font(J.SANS, 14), cx0, y, maxw, J.rgb(J.TEXT_SOFT), spacing=1.3)
    y = int(y) + int(18 * S)

    # Stats row is pinned to a fixed position near the bottom (rather than
    # floating after however tall the content above happens to be) — this
    # is what actually guarantees it never runs off the canvas; the panel
    # height below is then computed from real remaining space, not guessed.
    stats_y = H - int(0.09 * H)
    panel_gap = int(20 * S)

    # ---- hero + support photo ----
    # support_w/gap were previously nonzero even when there's no support
    # photo — hero_w shrank to leave room for it anyway, leaving a dead gap
    # to hero's left AND misaligning the hero's left edge against the title
    # above it (title starts at cx0; hero started at cx0+support_w+gap).
    # Only reserve that space when a support photo actually exists.
    hero_h = int(0.30 * H)
    has_support = bool(rec.get("support"))
    support_w = int(maxw * 0.22) if has_support else 0
    support_gap = int(0.015 * W) if has_support else 0
    hero_w = maxw - support_w - support_gap
    hero_im = L._photo_box(rec.get("hero"), hero_w, hero_h, hue=J.BG_2)
    img.paste(hero_im.convert("RGBA"), (cx0 + support_w + support_gap, y))
    if has_support:
        sup_im = L._photo_box(rec.get("support"), support_w, hero_h, hue=J.BG_2)
        img.paste(sup_im.convert("RGBA"), (cx0, y))
    y += hero_h + int(20 * S)

    # ---- highlights + activities, side by side in one glass panel ----
    # Panel is content-sized (like the legacy blue engine's cards/grid), not
    # stretched to fill all the way down to the stats row — a light-content
    # day (e.g. 2 highlights, 2 activities) was otherwise leaving a large
    # empty card. The old "fill remaining space" height is now only a CEILING
    # (`budget_max`), so the stats row still can't run off the canvas on a
    # heavy-content day.
    pad = int(20 * S)
    half = maxw // 2
    budget_max = stats_y - panel_gap - y
    natural_h = max(
        _highlights_height(d, rec.get("highlights", []), half - pad - int(12 * S)),
        _activities_height(d, rec.get("activities", {}), maxw - half - pad),
    ) + 2 * pad
    panel_h = max(int(0.10 * H), min(natural_h, budget_max))
    panel_box = (cx0, y, cx0 + maxw, y + panel_h)
    img = _glass_panel(img, panel_box, radius=int(14 * S))
    d = ImageDraw.Draw(img)
    hx, hy = cx0 + pad, y + pad
    lbl_f = font(J.SANS_SEMIBOLD, 11)
    d.text((hx, hy), "HIGHLIGHTS", font=lbl_f, fill=J.rgb(J.GLOW))
    hy += L._measure(d, "AG", lbl_f)[1] + int(10 * S)
    bf = font(J.SANS, 12.5)
    for item in rec.get("highlights", []):
        d.ellipse([hx, hy + int(6 * S), hx + int(4 * S), hy + int(10 * S)], fill=J.rgb(J.GLOW))
        hy = int(L._wrap_block(d, item, bf, hx + int(12 * S), hy, half - pad - int(12 * S),
                                J.rgb(J.TEXT_SOFT), spacing=1.25)) + int(6 * S)

    ax, ay = cx0 + half + pad, y + pad
    d.text((ax, ay), "TODAY", font=lbl_f, fill=J.rgb(J.GLOW))
    ay += L._measure(d, "AG", lbl_f)[1] + int(10 * S)
    parts_f = font(J.SANS_SEMIBOLD, 11.5)
    for part in ("morning", "afternoon", "evening", "night"):
        val = rec.get("activities", {}).get(part)
        if not val:
            continue
        d.text((ax, ay), part.upper(), font=parts_f, fill=J.rgb(J.TEXT_FAINT))
        ay += L._measure(d, "AG", parts_f)[1] + int(4 * S)
        ay = int(L._wrap_block(d, val, bf, ax, ay, maxw - half - pad, J.rgb(J.TEXT), spacing=1.22)) + int(10 * S)

    # ---- slim stats row (distance/time/next-stop/stay-tier; missing ones
    # simply don't appear — no placeholder dashes). Pinned position (see
    # stats_y above), not a continuation of the accumulated content flow.
    stats = [
        ("time", "Drive time", rec.get("drive_time")),
        ("pin", "Next", rec.get("next_stop")),
        ("stay", "Stay", rec.get("stay_tier")),
    ]
    _stat_row(d, cx0, stats_y, stats)

    return img.convert("RGB")


def layout_journey_cover(rec):
    """Full-bleed hero + dark scrim + title — the deck's opening slide."""
    base = L._photo_box(rec.get("hero"), W, H, hue=J.BG_2)
    img = L._over(base, L.vgrad_scrim((W, H), J.rgb(J.BG), 0, 235, start=0.25)).convert("RGBA")
    d = ImageDraw.Draw(img)

    wf = font(J.SANS_BOLD, 22)
    d.text((MARGIN, int(0.05 * H)), "explore", font=wf, fill=J.rgb(J.TEXT))
    w0 = L._measure(d, "explore", wf)[0]
    d.text((MARGIN + w0, int(0.05 * H)), "ain", font=wf, fill=J.rgb(J.GLOW))

    x = MARGIN
    y = int(0.66 * H)
    if rec.get("kicker"):
        kfnt = font(J.SANS_SEMIBOLD, 13)
        d.text((x, y), rec["kicker"].upper(), font=kfnt, fill=J.rgb(J.GLOW))
        y += L._measure(d, "AG", kfnt)[1] + int(16 * S)
    hl, hf, hlh = L.fit(d, rec["title"], J.SANS_BOLD, 60, 34, int(W * 0.72), int(H * 0.22))
    y = L.draw_lines(d, hl, hf, x, y, J.rgb(J.TEXT), hlh)
    if rec.get("subtitle"):
        y = int(y) + int(10 * S)
        L._wrap_block(d, rec["subtitle"], font(J.SANS, 16), x, y, int(W * 0.62), J.rgb(J.TEXT_SOFT), spacing=1.3)
    return img.convert("RGB")


def layout_journey_closing(rec):
    """Closing slide: the full route, fully lit, + trip stats. The only
    "final destination reached" moment a static deck can honestly give."""
    img = Image.new("RGBA", (W, H), J.rgb(J.BG) + (255,))
    d = ImageDraw.Draw(img)
    wf = font(J.SANS_BOLD, 20)
    d.text((MARGIN, int(0.045 * H)), "explore", font=wf, fill=J.rgb(J.TEXT))
    w0 = L._measure(d, "explore", wf)[0]
    d.text((MARGIN + w0, int(0.045 * H)), "ain", font=wf, fill=J.rgb(J.GLOW))

    road_x0, road_x1 = MARGIN, int(0.26 * W)
    road_y0, road_y1 = int(0.14 * H), int(0.92 * H)
    n = len(rec["route"])
    paste_road(img, n, n - 1, road_x0, road_x1, road_y0, road_y1)
    d = ImageDraw.Draw(img)

    cx0 = road_x1 + int(0.03 * W)
    maxw = W - MARGIN - cx0
    y = int(0.32 * H)
    lf = font(J.SANS_SEMIBOLD, 13)
    d.text((cx0, y), "JOURNEY COMPLETE", font=lf, fill=J.rgb(J.GLOW))
    y += L._measure(d, "AG", lf)[1] + int(16 * S)
    hl, hf, hlh = L.fit(d, rec["title"], J.SANS_BOLD, 46, 28, maxw, int(0.16 * H))
    y = int(L.draw_lines(d, hl, hf, cx0, y, J.rgb(J.TEXT), hlh)) + int(30 * S)

    # rec["stats"] is [(value, label), ...] — e.g. ("9", "Days"): big bold
    # number first, small caption label beneath it (KPI-tile convention).
    sx = cx0
    for value, label in rec.get("stats", []):
        vf = font(J.SANS_BOLD, 32)
        d.text((sx, y), value, font=vf, fill=J.rgb(J.GLOW))
        vw = L._measure(d, value, vf)[0]
        lf2 = font(J.SANS_SEMIBOLD, 11.5)
        d.text((sx, y + int(48 * S)), label.upper(), font=lf2, fill=J.rgb(J.TEXT_FAINT))
        sx += max(vw, L._measure(d, label.upper(), lf2)[0]) + int(48 * S)
    return img.convert("RGB")


LAYOUTS = {
    "journey_cover": layout_journey_cover,
    "journey_day": layout_journey_day,
    "journey_closing": layout_journey_closing,
}


def render_slide(rec):
    return LAYOUTS[rec["layout"]](rec)


if __name__ == "__main__":
    import imagemap
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 1) Isolated road-geometry sanity check: the full route at a short (3)
    # and long (11) stop count, at different current positions, confirming
    # the auto-tuned bend count stays gentle at both extremes.
    outdir = os.path.join(root, "dist", "_road_check")
    os.makedirs(outdir, exist_ok=True)
    for name, n, idx in [("full_3stops_first", 3, 0), ("full_3stops_last", 3, 2),
                          ("full_11stops_early", 11, 1), ("full_11stops_late", 11, 9)]:
        canvas = Image.new("RGB", (430, 720), J.rgb(J.BG)).convert("RGBA")
        paste_road(canvas, n, idx, x_left=30, x_right=370, y_top=40, y_bottom=680)
        canvas.convert("RGB").save(os.path.join(outdir, f"{name}.png"))
    print("road-geometry sanity renders -> dist/_road_check")

    # 2) The SAME day slide at three different points in the trip — Kerala
    # Signature Classic's Day 2 (Kochi), Day 4 (Munnar), Day 8 (Marari Beach)
    # — same route, same road shape, car at a different, further-along
    # station each time. This is the thing to check: flipping through these
    # in order should read as the car progressing down one continuous road.
    route = ["Kochi", "Munnar", "Thekkady", "Kumarakom to Alleppey", "Marari Beach"]
    days = [
        {
            "title": "Fort Kochi", "day_of": 2, "day_total": 9, "current_index": 0,
            "subtitle": "A full day on foot through the heritage quarter.",
            "hero": imagemap.slide_path("kochi"), "support": None,
            "highlights": ["Chinese fishing nets at sunset", "Mattancherry Palace", "Jew Town", "Evening Kathakali performance"],
            "activities": {"morning": "Fort Kochi heritage walk", "afternoon": "Mattancherry Palace & Jew Town",
                            "evening": "Kathakali performance", "night": None},
            "drive_time": None, "next_stop": "Munnar (~4 hrs)", "stay_tier": "Waterfront heritage stay",
        },
        {
            "title": "Munnar", "day_of": 4, "day_total": 9, "current_index": 1,
            "subtitle": "Eravikulam National Park at sunrise, then a full day among Munnar's tea estates.",
            "hero": imagemap.slide_path("munnar"), "support": imagemap.slide_path("munnar_tea"),
            "highlights": ["Eravikulam National Park at sunrise", "Guided tea-estate walk and tasting",
                           "Anamudi Peak views from the high shola grassland", "A free afternoon at the estate"],
            "activities": {"morning": "Eravikulam National Park — sunrise safari", "afternoon": "Guided tea-estate walk and tasting",
                            "evening": "Free time at the estate", "night": "Dinner at the property"},
            "drive_time": None, "next_stop": "Thekkady (~3.5 hrs)", "stay_tier": "Independent plantation-bungalow stay",
        },
        {
            "title": "Marari Beach", "day_of": 8, "day_total": 9, "current_index": 4,
            "subtitle": "Nothing booked — the trip's built-in free day.",
            "hero": imagemap.slide_path("alleppey"), "support": None,
            "highlights": ["Just the beach and the property", "A working fishing village", "Bicycles available for the village"],
            "activities": {"morning": "Free — beach", "afternoon": "Free — beach or village cycling",
                            "evening": "Free time at the property", "night": None},
            "drive_time": None, "next_stop": "Depart Kochi (~1.5–2 hrs)", "stay_tier": "Cottage-style beach resort",
        },
    ]
    outdir2 = os.path.join(root, "dist", "_journey_check")
    os.makedirs(outdir2, exist_ok=True)
    for d in days:
        rec = dict(d, route=route)
        p = os.path.join(outdir2, f"day{rec['day_of']:02d}_{rec['title'].lower().replace(' ', '_')}.png")
        layout_journey_day(rec).save(p)
        print(f"  wrote {os.path.relpath(p, root)}")
