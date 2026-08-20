"""Theme for the new "cinematic journey" deck — dark, road-trip UI.

Separate from theme.py (the blue company-overview palette), which stays
untouched. See design/theme.md for the reference brief + mockups this is
built from.

Note on accent colour: the brief text proposes a different colour per
destination; the actual delivered mockups (design/theme-day*.jpg) are
consistently a single teal glow for "current", regardless of destination.
This module follows the mockups (ground truth) over the aspirational brief
text — one consistent GLOW accent, not a rotating per-stop palette.
"""
import theme as T

rgb = T.rgb
rgba = T.rgba

# ---- palette ----
BG          = "#0a0e14"   # near-black background
BG_2        = "#0d1219"   # slightly lifted panel background (glass, before alpha)
PANEL_LINE  = "#232b35"   # hairline borders on cards/panels
GLOW        = "#34d1a0"   # teal — current stop, progress, active accents
GLOW_DIM    = "#1f7a5c"   # teal, muted (completed stops)
FUTURE      = "#3a4149"   # muted grey — future stops, inactive icons
ROAD_EDGE   = "#232b35"   # road ribbon — outer/dark edge (bevel shadow)
ROAD_SURFACE = "#3a4451"  # road ribbon — inner/lighter surface (bevel highlight)
TEXT        = "#f5f7fa"   # primary text on dark
TEXT_SOFT   = "#aab2bd"   # secondary text on dark
TEXT_FAINT  = "#6b7480"   # tertiary / captions

# ---- slide geometry (shared with theme.py) ----
SLIDE_W, SLIDE_H = T.SLIDE_W, T.SLIDE_H
RENDER_SCALE = T.RENDER_SCALE
PX_W, PX_H = T.PX_W, T.PX_H

# ---- fonts (reuse theme.py's resolved font paths; this UI is sans-only,
# no serif display face — a clean modern sans matches the reference better
# than the catalogue's classical Palatino) ----
SANS          = T.SANS
SANS_SEMIBOLD = T.SANS_SEMIBOLD
SANS_BOLD     = T.SANS_BOLD
