"""Load and validate an itinerary JSON against the parsed catalogue.

Itinerary format (itineraries/*.json):
    {
      "title": "South India Tour",
      "client": "The Menon Family",
      "dates": "Nov 2026 · 12 nights",
      "prepared_by": "Exploreain",
      "cover_key": "kochi",            # optional image key for the cover
      "destinations": ["KOCHI", "MUNNAR", ...]   # ordered UPPERCASE names
    }
"""
import os, json, difflib

import imagemap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGUE = os.path.join(ROOT, "build", "catalogue.json")


def load_catalogue():
    with open(CATALOGUE, encoding="utf-8") as f:
        return json.load(f)


def _dest_index(catalogue):
    """UPPERCASE destination name -> (destination dict, region name)."""
    idx = {}
    for region in catalogue["regions"]:
        for dest in region["destinations"]:
            idx[dest["name"]] = (dest, region["name"])
    return idx


def load_itinerary(path):
    with open(path, encoding="utf-8") as f:
        it = json.load(f)
    if not it.get("destinations"):
        raise ValueError(f"{path}: itinerary has no 'destinations'")
    return it


def resolve(itinerary, catalogue):
    """Return an ordered list of resolved stops:
        [{"name","dest","region","image_key","slide_path"}]
    Raises on unknown destination names; warns (returns flags) for missing photos.
    """
    idx = _dest_index(catalogue)
    stops, warnings = [], []
    for entry in itinerary["destinations"]:
        # allow either a bare "NAME" or an override object {"name":..., "image_key":...}
        name = entry["name"] if isinstance(entry, dict) else entry
        override_key = entry.get("image_key") if isinstance(entry, dict) else None
        if name not in idx:
            close = difflib.get_close_matches(name, idx.keys(), n=3)
            hint = f" Did you mean: {', '.join(close)}?" if close else ""
            raise ValueError(f"Unknown destination '{name}'.{hint}")
        dest, region = idx[name]
        key = override_key or imagemap.DEST_IMG.get(name)
        path = imagemap.slide_path(key) if key else None
        if not path or not os.path.exists(path):
            warnings.append(name)
            path = None
        stops.append({
            "name": name, "dest": dest, "region": region,
            "image_key": key, "slide_path": path,
        })

    cover_key = itinerary.get("cover_key")
    if cover_key and cover_key not in imagemap.SPEC:
        raise ValueError(f"cover_key '{cover_key}' is not a known image key")

    return stops, warnings


if __name__ == "__main__":
    import sys
    cat = load_catalogue()
    it = load_itinerary(sys.argv[1])
    stops, warn = resolve(it, cat)
    print(f"'{it.get('title')}' — {len(stops)} stops")
    for s in stops:
        photo = os.path.basename(s["slide_path"]) if s["slide_path"] else "(placeholder)"
        print(f"  {s['name']:20s} [{s['region']}]  {photo}")
    if warn:
        print("WARN no photo for:", ", ".join(warn))
