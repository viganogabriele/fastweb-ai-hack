# SPEC — "Vesper" concept film

GOAL:    a teammate watches once and knows what we build: tonight's store note becomes a
         linked signal, a corrected forecast, a feasible stock move and a human approval.
OUTPUT:  HyperFrames, 1920 x 1080, 30 fps
TIME:    73 s x 30 = 2190 frames. No music bed (no music source on this machine); SFX on actions.

LOOK:    Moncler's own world, two materials.
         Night  = lacquer black #0A0C11 ground, ink #F4F4F1, city-light amber #F2B544 (globe only),
                  real snow on the opening and end card (it is the brand's season, not decoration).
         Snow   = showroom / UI white #F2F3F5, panels #FFFFFF, ink navy #14213D.
         Accent = Moncler red #D7141A, rationed: chapter stamps, the stockout, "never", "decide".
         Data   = ice #BFD9EE for corrected-forecast band and flows.
         Display: Montserrat 800, uppercase, tracking 0.06em, 72-180 px. Body: Montserrat 500 30-40 px.
         Data: IBM Plex Mono 400/600 22-30 px. CJK: Noto Sans CJK JP (local).

OBJECTS: the globe at night (land as dots, stores as lights), closing-note email cards,
         a clothing rack with real catalog SKUs (MAIRE, HERMINE, FLAMMETTE, ...), a forecast chart
         with a censored stockout day, a dot-matrix map of Europe with DC-IT-CSG, MIL01, PAR01, LON01,
         the "Vesper" decision room (signal feed, decision card, investigator trace).

MOTION:  arrivals expo.out / power4.out, camera power2.inOut, exits power3.in (40% shorter).
         Words stagger 0.07 s, list rows 0.06 s. Chapter stamps print in 0.12 s (scale 1.12 -> 1).

SHOTS:
  S1  0.0- 7.4  globe turns with the 21:00 line; store lights fire, notes launch. "Every evening, 39 stores close" / "and write down what they saw"
  S2  7.0-15.4  notes slap onto a wall in 8 languages. "Free text in 8 languages" / "with zero product codes" / "Sales data arrives tomorrow" / "Lost demand never arrives". PAR01 card lifts into S3's sheet.
  S3 15.0-25.4  stamp AI READS; spans highlight, typed tags, JSON claim types in. whip out.
  S4 25.0-33.4  showroom rack scrolls; MAIRE black locks 0.97. Then "quello lungo nero": HERMINE vs FLAMMETTE -> asks MIL02 in Italian -> reply -> linked.
  S5 33.0-43.4  stamp CODE COUNTS; chart: censored day, band 8.6-10.2 vs 7.0; formulas.
  S6 43.0-51.4  Europe map: 6 units DC + 5 units MIL01 fly to PAR01, LON01 excluded cross-border; 6/6 checks; options A/B/C.
  S7 51.0-65.4  stamp HUMANS DECIDE; the Vesper room; punch-in on the card; cursor approves; draft via MCP; loop closes to the store in French.
  S8 65.0-73.0  "AI reads. Code counts. Humans decide." -> VESPER wordmark, credits.

BANNED:  glow halos and lens flares, floating decorative particles, glass cards, mesh gradients,
         pill chips, three cards in a row, everything fading and sliding up, titles moving while read,
         the logo docked in a corner, corner brackets/HUD readouts.
QA:      t = 3, 10, 13, 18, 22, 28, 31, 38, 47, 55, 60, 62, 70.
