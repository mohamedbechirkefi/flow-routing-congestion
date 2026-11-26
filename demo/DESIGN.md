<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# FLOW demo: design plan

Owner request of 2026-11-26 (labs brief `DEMO-BRAND-brief.md`): every lab demo gets its own brand, motion and premium UI. This file is the plan, written before the code, and the review of that plan.

## Subject, audience, job

- **Subject.** Selfish against coordinated routing on congestible networks: the Braess paradox, user equilibrium against system optimum, the price of anarchy measured on seeded lattices.
- **Audience.** A curious technical reader, an admissions committee skimming for rigour, a transport researcher checking the protocol.
- **Primary job.** Answer the question in one sentence at the top, show the paradox working on the Braess network, then lay out the measured evidence, including the two contradicted exact checks, with the same weight as the supported results.

## Direction: the transit map and the guide sign

The vocabulary of the subject is road signage and network diagrams. Two artefacts carry the page:

1. **The guide sign.** Green highway guide panels with a white inset rule and mixed-case lettering in a Highway Gothic descendant. Real guide signs use mixed case for destinations, so the page gets strong signage without all-caps labels.
2. **The schematic route map.** Lines drawn at 0, 45 and 90 degrees, interchange rings for stations, line colours that mean something. The six registered experiments become stations on one line (EXP-001 to EXP-006 is a real sequence: the registration order), with the exploratory checks on a dotted branch.

## Colour (light only)

| Name | Hex | Role |
|---|---|---|
| Map paper | `#F1F4F2` | page background, a cool grey-green, never cream |
| Signal navy | `#13263B` | text, station rings, the sticky bar |
| Guide green | `#0B5D3B` | the guide sign, the logo plate, assumption tags, the system optimum |
| Motorway blue | `#1F4E9C` | links and measured series (with link e), focus ring |
| Warning amber | `#E8A100` | link e, the "new road" plate, hover rails (never text on light) |
| Jam red | `#A8261B` | the heaviest congestion step, the before-and-after gap |

Congestion is a five-step ramp from pale amber to jam red, always paired with line width so colour is never alone. The page is light only: a route map is read on paper, and one excellent scheme is better than two adequate ones.

## Type

- **Overpass** (Delve Withrington, Red Hat; an open interpretation of the Highway Gothic signage alphabet; OFL 1.1). Weights 400, 600 and 800. Headings, the sign, navigation, controls, chart labels, numbers with tabular figures.
- **PT Serif** (Alexandra Korolkova, Olga Umpeleva, Vladimir Yefimov; ParaType; OFL 1.1). Weights 400, 400 italic and 700 (the 700 cut also serves the 600 used by `strong`, so no synthetic bold). Body prose, captions, limitations. PT Serif was drawn for the Public Types of the Russian Federation project, a type family for public and civic print: sturdy wedge serifs and a large x-height that stay legible at small sizes, which fits the transit-map brief: the sign speaks in Overpass, the explanation in a plain public serif. It replaced Source Serif 4 on 2026-11-26 so that no two lab demos share a typeface (owner request).

PT Serif has a larger x-height and wider letters than Source Serif 4, so the scale was re-tuned: body 16.5 px with 1.68 line-height (was 17 px, 1.65), hero answer clamp 1.08 to 1.25 rem with 1.58 line-height, footer 0.94 rem. PT Serif has no tabular figures; every aligned number (tables, key figures, readouts, chart labels) was already set in Overpass, which has them.

Scale (1.25 ratio from 17 px body): 13.6, 17, 21.3, 26.6, 33.2, 41.5, then a fluid sign headline up to 64 px. Measure stays under 70 characters.

## Layout

```
+--------------------------------------------------------------------+
| [mark] Flow   Overview  Braess  Results  Assumptions  Method  Sandbox|  sticky bar, navy, 56 px
+--------------------------------------------------------------------+
|  +-------------------------------+   +--------------------------+  |
|  | GUIDE SIGN (green, inset rule)|   |  route-map illustration  |  |
|  |  Can individually optimal     |   |  s --a-- A --c-- t       |  |
|  |  routing worsen collective    |   |   \      | e     /      |  |
|  |  travel time?                 |   |    b --- B --- d         |  |
|  +-------------------------------+   |  "Illustration, not      |  |
|  answer sentence (serif, data)       |   study data"  [Replay]  |  |
|  status line                         +--------------------------+  |
+--------------------------------------------------------------------+
|  Overview: three distance-sign plates (headline values from data)  |
|  Braess explorer: slider, policy switch, before | after maps       |
|  Results: charts on map-paper panels                               |
|  Experiments as stations:                                          |
|     O EXP-001 ...                                                  |
|     |                                                              |
|     O EXP-002 ...         (dotted branch for exploratory checks)   |
|  Assumptions as a route legend, Method, Sandbox (dashed purple     |
|  works-zone border), Footer                                        |
+--------------------------------------------------------------------+
```

Left aligned throughout, a 12-column grid at desktop, one column under 720 px. Panels have two radii only: 14 px for sign plates, 6 px for controls.

## Motion

- **The one orchestrated moment (hero).** The four-station Braess map draws in (stations pop with a short stagger, lines fade in), small traveller dots split evenly over the upper and lower routes, then a warning-amber plate reads "New road opens", link e appears, the dots divert onto the zig-zag route and the shared links a and d warm from blue to jam red. It plays once and stops on the final frame; a Replay button replays it. WAAPI on `transform` and `opacity` only. Labelled "Illustration, not study data"; it shows no number.
- **Motion that answers the visitor.** The policy switch has a sliding indicator (transform, 220 ms, strong ease-out). Charts reveal once when scrolled into view (opacity and a 6 px rise, 30 ms stagger per row). The sandbox run button shows a moving progress rail while the worker runs. Headline values count up once from zero only where the value is a plain decimal in the data; the final text is the manuscript's exact string.
- **Reduced motion.** No hero motion (the final frame is drawn static), no count-up, no flow dashes; reveals become instant. Hover rails sit inside `(hover: hover) and (pointer: fine)`.

## The one memorable thing

The page opens on a real guide sign that asks the question, beside a route map in which opening a new road makes every trip slower.

## Review against the generated-page tells, and what changed

- *Cream and terracotta, near-black with one acid accent:* map paper is a cool grey-green and the accents are signage colours with meanings (green guide, blue motorway, amber warning). Kept.
- *All-caps tracked eyebrows:* the first draft had an uppercase "Preregistered simulation study" kicker over the sign, as on real motorway shields. Removed: the status is a sentence under the answer instead, and the evidence tags were changed from uppercase to sentence case.
- *Mono data labels:* none; numbers use Overpass tabular figures.
- *01/02/03 markers:* the experiment ids are real identifiers in registration order, shown as stations on one line. The first draft also numbered the page sections; removed, sections are not a sequence.
- *Identical rounded SaaS cards:* the first draft kept the three overview tiles as equal cards. Changed to distance-sign plates (green, inset rule, value right aligned like a distance), and the experiment panels hang from the station line instead of floating as cards.
- *Fade-up on every section:* only charts reveal, once; sections do not animate.
- *Other demos:* VIRAL uses a network map with nodes lighting up; FLOW avoids glowing nodes and particle graphs and keeps to schematic 45-degree lines and signage. SCALE uses blueprint gauges; FLOW has no gauges. FARE uses a departure board; FLOW has no split-flap digits.

## Screenshot critique (two passes)

- Pass 1: the sign headline broke into five ragged lines (size reduced so it sets in four); hero station labels collided with lines ("destination" moved beside t, map widened); dots sat at the map origin before their trip (now hidden until launched); paired charts stretched to equal heights and left dead space (grid rows now align to the start). Removed accessory: the drop shadow under the guide sign. Real signs are flat, and the inset rule already carries the form.
- Pass 2: the sandbox Reset button wrapped alone on a second row (run, cancel and reset now form one action group); count-up and chart reveal verified to end on the exact data strings.
