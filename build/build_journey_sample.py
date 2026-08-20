"""One-off demo: render a FULL sample deck in the new cinematic-journey
theme (cover -> every day -> closing) for Kerala Signature Classic, as a
real PDF + PPTX you can open — so the concept can be judged as a deliverable,
not just individual slide PNGs.

NOT wired into the production pipeline (slideplan.py/deck.py) yet — that
needs the plan_content schema extension (hero_key/highlights/activities/
etc., see the build plan) and the deck-content agent update. This script
hardcodes the same content by hand for one model, as a demo only.

    python build/build_journey_sample.py
"""
import os

import imagemap
import deck_layouts_journey as J_layouts
import deck_render

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist", "journey-sample-kerala-signature-classic")

ROUTE = ["Kochi", "Munnar", "Thekkady", "Kumarakom to Alleppey (houseboat)", "Marari Beach"]
TOTAL_DAYS = 9

DAYS = [
    dict(day_of=1, current_index=0, title="Arrive Kochi", hero="kochi",
         subtitle="Land, transfer to the hotel and rest — the soft-landing day the whole trip is paced around.",
         highlights=["No sightseeing scheduled today", "Check in and settle in", "Rest after the flight"],
         activities={"afternoon": "Transfer to hotel", "evening": "Rest, no activity booked"},
         drive_time=None, next_stop="Fort Kochi tomorrow", stay_tier="Waterfront heritage stay"),
    dict(day_of=2, current_index=0, title="Fort Kochi", hero="kochi",
         subtitle="A full day on foot through the heritage quarter, closing with an evening Kathakali performance.",
         highlights=["Chinese fishing nets", "Mattancherry Palace", "Jew Town", "Evening Kathakali performance"],
         activities={"morning": "Fort Kochi heritage walk", "afternoon": "Mattancherry Palace & Jew Town",
                     "evening": "Kathakali performance"},
         drive_time=None, next_stop="Munnar (~4 hrs)", stay_tier="Waterfront heritage stay"),
    dict(day_of=3, current_index=1, title="Drive to Munnar", hero="munnar",
         subtitle="A scenic ~4-hour hill drive via waterfalls and roadside spice stops.",
         highlights=["Waterfalls en route", "Roadside spice-estate stops", "Arrive by mid-afternoon"],
         activities={"afternoon": "Arrive Munnar, rest of the day free at the estate"},
         drive_time="~4 hrs", next_stop="Munnar, full day tomorrow", stay_tier="Independent plantation-bungalow stay"),
    dict(day_of=4, current_index=1, title="Munnar", hero="munnar", support="munnar_tea",
         subtitle="Eravikulam National Park at sunrise, then a full day among Munnar's tea estates.",
         highlights=["Eravikulam National Park at sunrise", "Guided tea-estate walk and tasting",
                     "Anamudi Peak views from the high shola grassland", "A free afternoon at the estate"],
         activities={"morning": "Eravikulam National Park — sunrise safari", "afternoon": "Guided tea-estate walk and tasting",
                     "evening": "Free time at the estate", "night": "Dinner at the property"},
         drive_time=None, next_stop="Thekkady (~3.5 hrs)", stay_tier="Independent plantation-bungalow stay"),
    dict(day_of=5, current_index=2, title="Drive to Thekkady", hero="thekkady",
         subtitle="A relaxed ~3.5-hour drive via Kumily, arriving for lunch.",
         highlights=["Spice-plantation walk on arrival", "Evening Kalaripayattu & Kathakali double bill"],
         activities={"afternoon": "Spice plantation walk", "evening": "Kalaripayattu & Kathakali performance"},
         drive_time="~3.5 hrs", next_stop="Periyar boat safari tomorrow", stay_tier="Cottage stay in a working spice garden"),
    dict(day_of=6, current_index=3, title="Periyar, then Kumarakom", hero="canoe",
         subtitle="An early boat safari on Periyar Lake, then on to Kumarakom to board the houseboat before dusk.",
         highlights=["Periyar Lake boat safari", "Best wildlife odds early morning", "Board the houseboat before dusk"],
         activities={"morning": "Periyar Lake boat safari", "afternoon": "Drive to Kumarakom", "evening": "Board houseboat"},
         drive_time="~3 hrs", next_stop="Overnight on the backwaters", stay_tier="Private houseboat charter"),
    dict(day_of=7, current_index=3, title="Overnight Houseboat", hero="canoe",
         subtitle="Cruise the Vembanad backwaters from Kumarakom, meals cooked onboard, mooring before dusk.",
         highlights=["Cruise through Vembanad backwaters", "Meals cooked fresh onboard",
                     "Disembark at Alleppey for Marari Beach"],
         activities={"morning": "Cruising the backwaters", "afternoon": "Mooring, village views",
                     "evening": "Dinner cooked onboard"},
         drive_time=None, next_stop="Marari Beach", stay_tier="Private houseboat charter"),
    dict(day_of=8, current_index=4, title="Marari Beach", hero="alleppey",
         subtitle="Nothing booked — the trip's built-in free day.",
         highlights=["Just the beach and the property", "A working fishing village", "Bicycles available for the village"],
         activities={"morning": "Free — beach", "afternoon": "Free — beach or village cycling",
                     "evening": "Free time at the property"},
         drive_time=None, next_stop="Depart Kochi (~1.5–2 hrs)", stay_tier="Cottage-style beach resort"),
    dict(day_of=9, current_index=4, title="Depart", hero="alleppey",
         subtitle="Transfer to Kochi airport, roughly 1.5–2 hours from Marari.",
         highlights=["Free morning at the property", "Transfer to Kochi airport"],
         activities={"morning": "Free time", "afternoon": "Transfer to Kochi airport"},
         drive_time="~1.5–2 hrs", next_stop=None, stay_tier=None),
]


def build_plan():
    plan = [{
        "layout": "journey_cover",
        "kicker": "Exploreain · Private South India Journeys",
        "title": "Kerala — Signature Classic",
        "subtitle": "8 nights across hill country, wildlife, backwaters and coast.",
        "hero": imagemap.slide_path("kochi"),
    }]
    for d in DAYS:
        rec = dict(d)
        rec["layout"] = "journey_day"
        rec["route"] = ROUTE
        rec["day_total"] = TOTAL_DAYS
        rec["hero"] = imagemap.slide_path(rec["hero"])
        if rec.get("support"):
            rec["support"] = imagemap.slide_path(rec["support"])
        plan.append(rec)
    plan.append({
        "layout": "journey_closing",
        "title": "Kerala — Signature Classic",
        "route": ROUTE,
        "stats": [("9", "Days"), ("5", "Stops"), ("8", "Nights")],
    })
    return plan


def main():
    plan = build_plan()
    os.makedirs(DIST, exist_ok=True)
    png_dir = os.path.join(DIST, "slides")
    os.makedirs(png_dir, exist_ok=True)
    for f in os.listdir(png_dir):
        os.remove(os.path.join(png_dir, f))
    pngs = []
    for i, rec in enumerate(plan):
        img = J_layouts.render_slide(rec)
        p = os.path.join(png_dir, f"slide_{i + 1:02d}.jpg")
        img.save(p, format="JPEG", quality=90, optimize=True, progressive=True)
        pngs.append(p)

    pdf = os.path.join(DIST, "kerala-signature-classic-journey.pdf")
    pptx = os.path.join(DIST, "kerala-signature-classic-journey.pptx")
    deck_render.build_pdf(pngs, pdf)
    deck_render.build_image_pptx(pngs, pptx)

    print(f"{len(plan)} slides -> {os.path.relpath(DIST, ROOT)}")
    print(f"  pdf   {os.path.relpath(pdf, ROOT)}")
    print(f"  pptx  {os.path.relpath(pptx, ROOT)}")


if __name__ == "__main__":
    main()
