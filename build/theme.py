"""Deck theme: blue palette + fonts, mirrored from the catalogue.

Canonical palette lives in build/template.html `:root` (light). These values
are copied here so the deck renderers (Pillow + python-pptx) share one source
of truth and stay on the BLUE design. Colors are exposed as hex strings and as
RGB tuples for Pillow.
"""
import os

# ---- palette (hex, from template.html :root light) ----
BRAND      = "#0e73c4"
BRAND_2    = "#0a5896"
GOLD       = "#b58a2e"
ACCENT     = "#b0602a"
PAPER      = "#eef1f4"
PAPER_2    = "#f8f9fb"
PAPER_3    = "#e3e8ee"
INK        = "#16202b"
INK_SOFT   = "#47535f"
INK_FAINT  = "#6f7c88"
WHITE      = "#ffffff"

# region hues (UPPERCASE region name -> hex), for placeholder panels
REGION_HUE = {
    "KERALA": "#0e7c63", "GOA": "#b5533a", "KARNATAKA": "#a9752c",
    "TAMIL NADU": "#b8871c", "ISLAND & CROSS-BORDER JOURNEYS": "#2e7fa6",
}


def rgb(hex_str):
    h = hex_str.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgba(hex_str, alpha):
    return rgb(hex_str) + (int(round(alpha * 255)),)


# ---- slide geometry ----
SLIDE_W, SLIDE_H = 1280, 720          # points (16:9)
RENDER_SCALE = 2                       # rasterize at 2x for crisp PNGs
PX_W, PX_H = SLIDE_W * RENDER_SCALE, SLIDE_H * RENDER_SCALE

# ---- fonts ----
_FONTDIR = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")


def _first(*names):
    for n in names:
        p = os.path.join(_FONTDIR, n)
        if os.path.exists(p):
            return p
    # last resort: return the last candidate path (PIL will raise a clear error)
    return os.path.join(_FONTDIR, names[-1])


# Serif for headlines — Palatino Linotype (matches the reference face and the
# catalogue's stack); Georgia is the fallback if Palatino is absent.
SERIF         = _first("pala.ttf", "georgia.ttf")
SERIF_BOLD    = _first("palab.ttf", "georgiab.ttf", "pala.ttf")
SERIF_ITALIC  = _first("palai.ttf", "georgiai.ttf", "pala.ttf")
# Sans for captions/labels — Segoe UI.
SANS          = _first("segoeui.ttf", "arial.ttf")
SANS_SEMIBOLD = _first("seguisb.ttf", "segoeuib.ttf", "arialbd.ttf")
SANS_BOLD     = _first("segoeuib.ttf", "arialbd.ttf")

FONTS_OK = os.path.exists(SERIF) and os.path.exists(SANS)
