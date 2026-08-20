# New brand theme — reference

Reference material for the new client-deck theme (replacing the current blue
company-overview look in `build/theme.py` / `build/deck_layouts.py`). Images
live alongside this file in `design/`. Nothing here is wired into the build
yet — this is reference only until the design is finalized.

## Images

Two overview grids show a spread of slide variants being explored; the eight
"Day N" images are individual full-slide mockups in the dark, cinematic
"road trip" style that the brief below describes.

- `theme-overview-grid-dark.jpg` — grid of dark-theme slide variants (the
  "exploreain" branded style), including a "car progresses to target
  destination" concept strip at top.
- `theme-overview-grid-green.jpg` — grid of a second, lighter "Kerala
  Discovery" concept (green/white dashboard style, alternate branding) —
  shown for comparison, not the primary direction.
- `theme-day1-kochi.jpg` — Day 1: Kochi (Chinese fishing nets hero)
- `theme-day2-munnar.jpg` — Day 2: Munnar (Eravikulam National Park / tea)
- `theme-day3-periyar-thekkady.jpg` — Day 3: Periyar (Thekkady) wildlife
- `theme-day4-alleppey-houseboat.jpg` — Day 4: Alleppey houseboat stay
- `theme-day5-varkala.jpg` — Day 5: Varkala cliffs and beach
- `theme-day6-kovalam.jpg` — Day 6: Kovalam lighthouse and beaches
- `theme-day7-wayanad.jpg` — Day 7: Wayanad hills and wildlife
- `theme-day8-south-kerala-departure.jpg` — Day 8: South Kerala & departure
  (closing/summary slide with journey stats)

## Reference video (animatic)

`theme-video-frames/frame_00.png` .. `frame_07.png` — 8 evenly-spaced frames
extracted from an 8-second reference animation the user provided (same AI
concept as the images above, animated). Confirms the transition concept:
one persistent bordered card floats on a starfield background; between
"days" the header text, hero photo, and Details panel cross-fade/morph in
place while the road updates (new pin glows, car advances) — the whole
card never moves or re-lays-out. This is a screen-recording-style UI
animation, not something a static PDF/PPTX can reproduce (no cross-fade
between slides in that format) — our per-slide static "full road, current
pin lit" approach is the closest honest equivalent. Also confirms (again)
that the body/Details copy in these AI-generated mockups is placeholder
garble, not usable reference text — evaluate the mockups/video for layout
and motion language only, never for copy.

Common elements visible across the Day-N mockups: a winding road on the left
with a car icon marking progress and a pin per stop (past stops dim, current
stop glows green), a large hero photo with a smaller supporting photo, a
"Details" info panel on the right (title + bullet list, currently
cut off/truncated in these drafts), a bottom icon bar (Buses, Distance,
Weather, Food & Drink, Info, Vis' Accessibility), and a "Day N / total —
X% Completed" progress readout. Dark, near-black background throughout,
teal/green glow as the single accent color.

## Design brief (as given)

**Premium Interactive Travel Itinerary Presentation — Master Design
Document & AI Prompt**

### Vision

Create a premium, cinematic travel itinerary presentation that combines the
storytelling of Apple Keynotes, the polish of Airbnb, and the interactivity
of a modern travel dashboard.

The presentation should feel like an animated road trip where the audience
follows a vehicle travelling across the destination. Every slide represents
one step of the journey, while maintaining a consistent layout that can
later become a reusable PowerPoint template for any destination in the
world.

The objective is to create excitement before the trip while also clearly
communicating the itinerary.

### Overall style

**Theme**: Premium Luxury, Minimal, Dark UI, Cinematic, Modern Travel
Dashboard, Interactive Timeline, Game-inspired Progress System, High-end
Presentation.

**Inspirations**: Apple Keynote, Airbnb, Tesla UI, Google Maps, Forza
Horizon menus, flight information displays, luxury travel brochures.

### Layout structure

Every slide must keep exactly the same structure:

```
Logo                    Day X of 7

Road Progress | Hero Images | Activity Information Card

Bottom Progress Timeline
```

The audience should immediately recognise the layout without relearning it.

### Left navigation (journey tracker)

This becomes the primary navigation of the presentation. Instead of only
showing a simple road, create a continuous winding highway running from the
first destination to the final destination (e.g. Kochi → Munnar → Thekkady
→ Alleppey → Varkala → Kovalam → Trivandrum). Each destination becomes a
stop on the road.

### Vehicle animation

The most important improvement: the vehicle should physically travel along
the route, not stay in one place. E.g. Slide 1: parked at Kochi. Slide 2:
driving towards Munnar. Slide 3: reaches Munnar. Slide 4: leaving Munnar.
Slide 5: halfway to Thekkady. Continue to the last destination — the
audience should always know exactly where they are.

**Road status**: completed destinations are bright/highlighted/green accent;
the current destination is pulsing/glowing/animated; future destinations are
dark grey/muted/minimal.

### Progress bar

Replace "Day 1.2" style labels with an explicit readout, e.g.:

```
Day 2 of 7
██████░░░░░
28% Complete
```
or a dot/segment timeline (`●────●────●────○────○────○`). Always visible.

### Hero section

The hero image should occupy ~60% of the slide — large, immersive
photography, no small cluttered images. Preferred layout: one hero image +
two supporting images, OR one hero image + an information card.

### Destination header

Example: "Day 3 / Thekkady / Periyar Wildlife Sanctuary" + a short
description sentence.

### Activity card

Each destination should break activities into Morning / Afternoon / Evening
/ Night (e.g. Morning: Tea Plantation Tour; Afternoon: Jeep Safari; Evening:
Boat Ride; Night: Hotel Check-in) — creates a realistic itinerary feel.

### Travel information card

Include: distance travelled, driving time, next destination, weather,
elevation, recommended clothing, estimated expenses, hotel, food highlight.

### Visual hierarchy

Large: destination. Medium: hero image, timeline. Small: supporting info.
Tiny: notes. Never let all elements carry equal visual weight.

### Icons

Modern outline icons only (drive, food, stay, walking, tickets,
photography, shopping, adventure, nature, sunrise, sunset, duration,
weather, distance, budget, hotel, parking). No colourful emoji —
professional iconography only.

### Destination colours

Each destination gets a unique accent colour while the UI stays dark
overall (e.g. Kochi = deep navy, Munnar = forest green, Thekkady = dark
emerald, Alleppey = ocean blue, Varkala = sunset orange, Kovalam =
turquoise, Trivandrum = royal blue).

### Bottom timeline

Instead of static labels, show previous stop / current stop / next stop /
distance remaining / estimated arrival, e.g.:
`Kochi ----126 km---- Munnar ----92 km---- Thekkady`
— the current stop should glow.

### Micro animations

Fade images, zoom hero image, slide cards, move car, glow current stop,
progress-bar animation, road-completion animation. Avoid excessive effects
— everything should feel premium, not gimmicky.

### Route map

A dedicated slide showing the full route map; each new day gradually
illuminates the completed section; the car moves in real time.

### Statistics panel

At the end: total distance, total driving time, hotels, experiences,
cities, meals, activities, budget, days, weather summary — creates closure.

### Final slide

The vehicle reaches the final destination; the entire route becomes
illuminated. Display: "Journey Complete", day count, total distance,
experience count, "Thank You", large scenic background image.

### Reusability

The template must work for any destination (Kerala, Scotland, Iceland,
Japan, Italy, Norway, Switzerland, road trips, luxury tours, corporate
tours, family holidays) without changing the layout — only destination
names, colours, images and route should change.

### AI generation prompt (as given, verbatim)

> Create a premium cinematic travel itinerary presentation using a luxury
> dark dashboard interface. The presentation should feature a continuous
> winding road on the left representing the complete journey. Every
> destination is marked as a milestone, and a realistic vehicle smoothly
> moves along the route from slide to slide, indicating current progress.
> Completed destinations glow subtly, the current stop pulses with a
> premium accent, and future destinations remain muted.
>
> The main content area should feature a large immersive hero image with
> supporting images, a beautifully designed itinerary card organised into
> Morning, Afternoon, Evening and Night activities, travel statistics
> including distance, drive time, next destination, hotel, weather and
> highlights, and a clean bottom progress timeline. Use modern typography,
> generous spacing, glassmorphism cards, subtle gradients, cinematic
> shadows and smooth animations inspired by Apple Keynote, Airbnb and Tesla
> UI.
>
> Each destination should have its own accent colour while preserving the
> same overall layout. Maintain strict visual consistency across all slides
> so the presentation functions as a reusable master template for any
> future travel itinerary. Prioritise storytelling, movement and clarity,
> making the audience feel as though they are travelling along with the
> vehicle rather than simply viewing static slides. The final result should
> be presentation-ready, animation-friendly, and suitable for exporting as
> PowerPoint slides or short promotional videos.

## Open questions / notes for implementation later

- These mockups are AI-generated drafts with garbled/placeholder body copy
  (e.g. "Learn more about the unique ecology..." repeated verbatim across
  different destinations, truncated bullet text) — not usable as-is; real
  copy will need to come from the tailored-plan content pipeline
  (`build/plan_content/`), not from these images.
- "Vehicle animation" and "micro animations" imply PowerPoint slide
  transitions/animations, which `python-pptx` (the current render stack)
  cannot author — worth flagging when this gets scoped into an actual build
  plan.
- The brief's per-destination accent colour + dark UI is a significant
  departure from the current fixed blue/gold palette in `theme.py` — this
  is expected (a full theme replacement) but confirms `theme.py`/
  `deck_layouts.py` will need a substantial rewrite, not a palette tweak.
