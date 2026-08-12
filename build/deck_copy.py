"""Slide copy: an evocative headline + one factual caption per destination.

AI generation uses the Anthropic SDK (Claude Sonnet 5 — chosen for this short,
high-volume copywriting) with structured outputs, and a COMMITTED cache
(build/copy_cache.json) keyed on content + prompt version + model, so a rebuild
only calls the API for genuinely new/changed destinations. With no API key (or
on any failure) it falls back to deterministic copy from catalogue.json, so the
deck always builds offline.
"""
import os, json, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_PATH = os.path.join(ROOT, "build", "copy_cache.json")

MODEL = "claude-sonnet-5"
PROMPT_VERSION = "v1"

SYSTEM = (
    "You write copy for Exploreain, a private South India travel company. "
    "For a destination, produce a slide of two parts, in this house voice:\n"
    "- headline: one short, evocative, present-tense sentence that puts the "
    "traveller in a specific human moment (like \"Your boatman's grandfather "
    "poled this same canal.\" or \"She takes two leaves and a bud, and never "
    "looks down.\"). No place name, no adjectives-for-adjectives' sake, no "
    "exclamation marks.\n"
    "- caption: one factual sentence of concrete detail (what/where/why it "
    "matters), plain and specific.\n"
    "Keep the headline under ~12 words and the caption under ~25 words."
)

_SCHEMA = {
    "type": "object",
    "properties": {
        "headline": {"type": "string"},
        "caption": {"type": "string"},
    },
    "required": ["headline", "caption"],
    "additionalProperties": False,
}

_SMALL = {"a", "an", "and", "the", "of", "to", "in", "on", "&"}


def titlecase(name):
    out = []
    for i, w in enumerate(name.strip().lower().split()):
        if w == "&":
            out.append("&")
        elif i != 0 and w in _SMALL:
            out.append(w)
        else:
            out.append(w[:1].upper() + w[1:])
    return " ".join(out)


# ---------- deterministic fallback ----------
def fallback_dest(dest):
    name = titlecase(dest["name"])
    subtitle = (dest.get("subtitle") or "").strip()
    highlights = dest.get("highlights") or []
    headline = subtitle or name
    caption = highlights[0] if highlights else dest.get("additional", "").split(".")[0]
    return {"headline": headline, "caption": caption.strip()}


def fallback_overview(catalogue, stops):
    regions = []
    for s in stops:
        if s["region"] not in regions:
            regions.append(s["region"])
    return {
        "headline": f"{len(stops)} destinations. One journey.",
        "caption": "A private, tailored route across " +
                   ", ".join(r.title() for r in regions) + ".",
    }


# ---------- cache ----------
def _load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_cache(cache):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1, sort_keys=True)


def _key(*parts):
    h = hashlib.sha256()
    h.update((PROMPT_VERSION + "\x00" + MODEL).encode("utf-8"))
    for p in parts:
        h.update("\x00".encode("utf-8"))
        h.update((p or "").encode("utf-8"))
    return h.hexdigest()


def _dest_key(dest):
    highlights = " | ".join(dest.get("highlights") or [])
    details = " ".join(
        p for d in dest.get("details", [])[:2] for p in d.get("paras", [])[:1]
    )[:1200]
    return _key("dest", dest["name"], dest.get("subtitle", ""), highlights, details)


# ---------- AI generation ----------
def _client():
    """Return an Anthropic client, or None if unavailable/unconfigured."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic
        return anthropic.Anthropic()
    except Exception:
        return None


def _ai_dest(client, dest):
    highlights = "; ".join(dest.get("highlights") or [])
    excerpt = " ".join(
        p for d in dest.get("details", [])[:2] for p in d.get("paras", [])[:1]
    )[:1200]
    user = (
        f"Destination: {titlecase(dest['name'])}\n"
        f"Subtitle: {dest.get('subtitle') or '(none)'}\n"
        f"Highlights: {highlights or '(none)'}\n"
        f"Context: {excerpt or '(none)'}"
    )
    resp = client.messages.create(
        model=MODEL,
        max_tokens=300,
        thinking={"type": "disabled"},
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": _SCHEMA}},
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    text = next(b.text for b in resp.content if b.type == "text")
    data = json.loads(text)
    return {"headline": data["headline"].strip(), "caption": data["caption"].strip()}


# ---------- public interface ----------
def copy_bundle(stops, itinerary, catalogue, use_ai=True):
    """Return {"destinations": {NAME: {headline,caption}}, "overview": {...}}.

    Cache hits cost nothing. Misses call the API when a key is configured,
    else fall back. Any new results are written back to copy_cache.json.
    """
    cache = _load_cache()
    client = _client() if use_ai else None
    dirty = False
    dests, used = {}, {"cache": [], "ai": [], "fallback": []}

    for s in stops:
        dest = s["dest"]
        k = _dest_key(dest)
        if k in cache:
            dests[s["name"]] = cache[k]
            used["cache"].append(s["name"])
            continue
        if client is not None:
            try:
                result = _ai_dest(client, dest)
                cache[k] = result
                dirty = True
                dests[s["name"]] = result
                used["ai"].append(s["name"])
                continue
            except Exception as e:
                print(f"  AI copy failed for {s['name']}: {e}")
        dests[s["name"]] = fallback_dest(dest)
        used["fallback"].append(s["name"])

    if dirty:
        _save_cache(cache)

    return {
        "destinations": dests,
        "overview": fallback_overview(catalogue, stops),
        "_used": used,
    }
