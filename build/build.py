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

# harden against premature </script> termination inside the JSON payloads
def safe(s):
    return s.replace("</", "<\\/")

tpl = load_text("template.html")
html = (tpl
        .replace("/*__DATA__*/", safe(data))
        .replace("/*__IMAGES__*/", safe(images))
        .replace("/*__LOGO__*/", safe(logo)))

# sanity: no placeholders left
for ph in ("/*__DATA__*/", "/*__IMAGES__*/", "/*__LOGO__*/"):
    assert ph not in html, "placeholder not replaced: " + ph

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print("wrote", OUT)
print("size %.2f MB" % (len(html.encode("utf-8")) / 1024 / 1024))
print("embedded images:", html.count("data:image"))
