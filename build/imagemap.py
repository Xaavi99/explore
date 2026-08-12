"""Single source of truth for photo <-> destination/experience mappings.

Imported by images.py (catalogue build) and the deck generator so the two
never drift. NOTE: template.html still carries its own copy of DEST_IMG /
EXP_IMG in JS for the client-side render; keep that in sync by hand (or via a
future injection step). See build/README.md.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLIDES = os.path.join(ROOT, "slides")

# image key -> (slide filename, max long edge for catalogue WebP, jpeg-ish quality)
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

# destination name (UPPERCASE, as in catalogue.json) -> image key
DEST_IMG = {
    "KOCHI": "kochi", "MUNNAR": "munnar", "ALLEPPEY": "alleppey",
    "KUMARAKOM": "canoe", "VARKALA": "varkala", "MADURAI": "temple", "LAKSHADWEEP": "island",
    "THEKKADY": "thekkady", "WAYANAD": "wayanad", "KOVALAM": "kovalam",
    "ATHIRAPPILLY": "athirappilly", "KANNUR & BEKAL": "bekal",
    "NORTH GOA": "goa_north", "SOUTH GOA & OLD GOA": "goa_south",
    "HAMPI": "hampi", "MYSORE": "mysore", "COORG": "coorg", "GOKARNA": "gokarna",
    "THANJAVUR": "thanjavur", "MAHABALIPURAM": "mahabalipuram",
    "PONDICHERRY": "pondicherry", "OOTY": "ooty",
    "ANDAMAN ISLANDS": "andaman", "SRI LANKA": "srilanka",
}

# specific experience title -> image key
EXP_IMG = {
    "FORT KOCHI & CHINESE FISHING NETS": "kochi",
    "TEA PLANTATIONS & ESTATE WALK": "munnar_tea",
    "OVERNIGHT HOUSEBOAT CRUISE": "alleppey",
    "KAYAKING THE CANALS": "canoe",
    "VARKALA CLIFF & PAPANASAM BEACH": "varkala",
    "AGATTI ISLAND & LAGOON": "island",
}


def slide_path(key):
    """Full-resolution source photo for an image key, or None."""
    spec = SPEC.get(key)
    return os.path.join(SLIDES, spec[0]) if spec else None


def dest_slide_path(dest_name):
    """Full-res source photo for a destination (UPPERCASE name), or None."""
    return slide_path(DEST_IMG.get(dest_name))
