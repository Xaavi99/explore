import json, re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "South_India_Catalogue.md")
OUT = os.path.join(ROOT, "build", "catalogue.json")

with open(SRC, encoding="utf-8") as f:
    lines = f.read().split("\n")

# strip trailing spaces
lines = [l.rstrip() for l in lines]

REAL_REGIONS = {"KERALA", "GOA", "KARNATAKA", "TAMIL NADU", "ISLAND & CROSS-BORDER JOURNEYS"}

# --- Tokenize into top-level blocks by heading level ---
i = 0
n = len(lines)

title = ""
intro = {"about": "", "discover": ""}
regions = []  # {name, subtitle, destinations:[]}
cur_region = None
cur_dest = None

def is_h1(l): return l.startswith("# ")
def is_h2(l): return l.startswith("## ")
def is_h3(l): return l.startswith("### ")

def is_attr_marker(s):
    """A standalone attraction title: a bold-wrapped line whose inner text is ALL CAPS
    (the catalogue convention), NOT a paragraph that merely begins/ends with bold spans."""
    s = s.strip()
    m = re.match(r"^\*\*(.+)\*\*$", s)
    if not m:
        return False
    inner = m.group(1)
    if "**" in inner:  # multiple bold spans -> it's a paragraph, not a title
        return False
    letters = [c for c in inner if c.isalpha()]
    return bool(letters) and inner == inner.upper()

def collect_para(start):
    """collect consecutive non-empty, non-heading, non-hr, non-bold-marker lines starting at start; return (text, nextindex)"""
    buf = []
    j = start
    while j < n:
        l = lines[j]
        if l.strip() == "" :
            j += 1
            if buf:  # paragraph break -> stop after collecting one paragraph group
                break
            continue
        if l.startswith("#") or l.strip() == "---" or is_attr_marker(l):
            break
        buf.append(l.strip())
        j += 1
    return " ".join(buf).strip(), j

def collect_list(start):
    items = []
    j = start
    while j < n:
        l = lines[j]
        s = l.strip()
        if s == "":
            j += 1
            continue
        if s.startswith("- "):
            items.append(s[2:].strip())
            j += 1
        else:
            break
    return items, j

# Section state machine over destination
def parse_dest_body(start, end):
    """parse lines[start:end] belonging to a destination"""
    d = {"subtitle": "", "attractions_list": [], "included": [], "highlights": [],
         "additional": "", "details": []}
    j = start
    # optional italic subtitle
    while j < end and lines[j].strip() == "":
        j += 1
    if j < end:
        s = lines[j].strip()
        if s.startswith("*") and s.endswith("*") and not s.startswith("**"):
            d["subtitle"] = s.strip("*").strip()
            j += 1
    while j < end:
        s = lines[j].strip()
        if s == "":
            j += 1; continue
        if s.startswith("### "):
            head = s[4:].strip().lower().rstrip(":")
            j += 1
            if head.endswith("attractions"):
                items, j = collect_list(j)
                d["attractions_list"] = items
            elif "included" in head:
                items, j = collect_list(j)
                d["included"] = items
            elif "highlight" in head:
                items, j = collect_list(j)
                d["highlights"] = items
            elif "additional" in head:
                # additional info: gather paragraphs until next heading/attraction/hr
                paras = []
                while j < end:
                    t = lines[j].strip()
                    if t == "":
                        j += 1; continue
                    if t.startswith("#") or t == "---" or is_attr_marker(t):
                        break
                    p, j = collect_para(j)
                    if p: paras.append(p)
                d["additional"] = "\n\n".join(paras)
            else:
                # unknown header, skip its paragraph
                p, j = collect_para(j)
        elif is_attr_marker(s):
            name = s.strip("*").strip()
            j += 1
            paras = []
            while j < end:
                t = lines[j].strip()
                if t == "":
                    j += 1; continue
                if t == "---" or is_attr_marker(t) or t.startswith("#"):
                    break
                p, j = collect_para(j)
                if p: paras.append(p)
            d["details"].append({"name": name, "paras": paras})
        elif s == "---":
            j += 1
        else:
            j += 1
    return d

# First pass: find indices of all headings to segment
# We'll walk and segment destinations by h2 within real regions.
i = 0
# title
while i < n and not is_h1(lines[i]):
    i += 1
if i < n:
    title = lines[i][2:].strip()
    i += 1

# find region boundaries
region_starts = [idx for idx,l in enumerate(lines) if is_h1(l)]
# first h1 is title; subsequent handled
# Build list of (name, start, end)
h1s = [(idx, lines[idx][2:].strip()) for idx in region_starts]

# intro: between title h1 and first real region h1
# Find first real region index
def region_index_for(name_upper):
    return name_upper in REAL_REGIONS

# locate intro about/discover
for idx,name in h1s:
    if name.upper().startswith("EXPLORE SOUTH INDIA"):
        # scan following lines until next h1 for ### About / ### Discover
        k = idx+1
        nexth1 = n
        for idx2,_ in h1s:
            if idx2 > idx:
                nexth1 = idx2; break
        while k < nexth1:
            s = lines[k].strip()
            if s.startswith("### About"):
                p,k = collect_para(k+1); intro["about"]=p; continue
            if s.startswith("### Discover"):
                p,k = collect_para(k+1); intro["discover"]=p; continue
            k+=1

# Build regions with destinations
# iterate h1s that are real regions
real_h1 = [(idx,name) for idx,name in h1s if name.upper() in REAL_REGIONS]
for ri,(idx,name) in enumerate(real_h1):
    # region end = next real region start OR next any h1 after idx OR n
    end = n
    for idx2,_ in h1s:
        if idx2 > idx:
            end = idx2; break
    # region subtitle
    reg = {"name": name, "subtitle": "", "destinations": []}
    k = idx+1
    while k < end and lines[k].strip()=="":
        k += 1
    if k < end:
        s = lines[k].strip()
        if s.startswith("*") and s.endswith("*") and not s.startswith("**"):
            reg["subtitle"] = s.strip("*").strip()
    # destinations = h2 within [idx,end)
    h2s = [j for j in range(idx,end) if is_h2(lines[j])]
    for di,dstart in enumerate(h2s):
        dend = h2s[di+1] if di+1 < len(h2s) else end
        city = lines[dstart][3:].strip()
        body = parse_dest_body(dstart+1, dend)
        body["name"] = city
        reg["destinations"].append(body)
    regions.append(reg)

data = {"title": title, "intro": intro, "regions": regions}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

# summary
print("TITLE:", title)
print("intro about len:", len(intro["about"]), "discover len:", len(intro["discover"]))
for r in regions:
    print(f"\nREGION: {r['name']}  sub={bool(r['subtitle'])}  dests={len(r['destinations'])}")
    for d in r["destinations"]:
        print(f"  - {d['name']}: attr_list={len(d['attractions_list'])} incl={len(d['included'])} high={len(d['highlights'])} add={'Y' if d['additional'] else 'n'} details={len(d['details'])}")
