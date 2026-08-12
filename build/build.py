import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "exploreain-catalogue.html")


def load_text(name):
    with open(os.path.join(HERE, name), "r", encoding="utf-8") as f:
        return f.read()


# read the JSON payloads as raw text (already valid JSON on disk)
data = load_text("catalogue.json")
images = load_text("images.json")
logo = load_text("logo.json")

# name -> {headline, caption}, resolved from the committed copy cache, for the
# in-browser deck builder (keyed the same way deck_copy keys the AI results)
import deck_copy  # noqa: E402
_cat = json.loads(data)
_cache = deck_copy._load_cache()
copy_by_name = {}
for _r in _cat["regions"]:
    for _d in _r["destinations"]:
        _k = deck_copy._dest_key(_d)
        if _k in _cache:
            copy_by_name[_d["name"]] = _cache[_k]
copy_json = json.dumps(copy_by_name, ensure_ascii=False)

# PptxGenJS bundle, inlined so the deck builder works offline / on static hosting
pptxgen = load_text(os.path.join("vendor", "pptxgen.bundle.js"))
assert "</script>" not in pptxgen, "pptxgen bundle contains </script> — needs escaping"


# harden against premature </script> termination inside the JSON payloads
def safe(s):
    return s.replace("</", "<\\/")


tpl = load_text("template.html")
html = (tpl
        .replace("/*__DATA__*/", safe(data))
        .replace("/*__IMAGES__*/", safe(images))
        .replace("/*__LOGO__*/", safe(logo))
        .replace("/*__COPY__*/", safe(copy_json))
        .replace("/*__PPTXGEN__*/", pptxgen))

# sanity: no placeholders left
for ph in ("/*__DATA__*/", "/*__IMAGES__*/", "/*__LOGO__*/", "/*__COPY__*/", "/*__PPTXGEN__*/"):
    assert ph not in html, "placeholder not replaced: " + ph

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print("wrote", OUT)
print("size %.2f MB" % (len(html.encode("utf-8")) / 1024 / 1024))
print("embedded images:", html.count("data:image"))
print("deck copy entries:", len(copy_by_name))
