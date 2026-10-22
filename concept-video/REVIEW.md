# REVIEW — Vesper concept film (74.85 s, 1920x1080, 30 fps)

## Creative calls
- One real note is followed end to end (PAR01, MAIRE black size 2, `J20931A00012-999-2`).
  Store ids, coordinates, timezones, catalog names and colours come from `generated/sources/erp/master_data/`.
  The DC is `DC-IT-CSG` (from `erp/logistics`). The forecast numbers (7.0 -> 8.6-10.2, need 11, 6 DC + 5 MIL01)
  are the worked example in `docs/project-design.md` §5. The unserved-unit values (0.4 / 0.6 / 10), the linking scores
  and the note texts on the wall are illustrative. The end card says so.
- Three chapter stamps carry the rule: AI READS (extraction + linking), CODE COUNTS (forecast + decision engine),
  HUMANS DECIDE (the room + approval).
- Worlds: night globe -> wall of notes -> email sheet -> showroom rack (real SKUs) -> planning chart ->
  dot-matrix Europe -> "Vesper" decision room -> snowy end card.
- "Vesper" (Latin for evening) is a placeholder product name.
- Storylines not built: (1) "a day in Camille's store", a live-action-style story from the store floor;
  (2) a split-screen race between a "sales-only detector" lane and the Vesper lane over D..D+4.

## Measured vs looked at
- `hyperframes check` passes, run in two halves (`--range 0,36` and `36,73`): the full run hits the 120 s runtime deadline
  because of the canvas scenes.
- Review sheets (beats, 14 seams, phone width) were inspected. Seams were retimed so every exit move is visible.
- Sound: 36 bundled Pixabay SFX, placed so each peak lands one frame after its picture. No music bed: there is no music
  source on this machine (no HeyGen sign-in, no local MusicGen). It was measured, not heard.

## Weakest shots / next steps
- S5 chart: the corrected band is visually modest next to the censored bar. A cumulative 7-day view would make the gap bigger.
- S1 continents are hand-traced low-poly outlines: they read as Earth at speed, not up close.
- S2 -> S3 hands off on a blank sheet for ~0.3 s.

## Warnings kept
- `contrast_aa_failure` on `#s7-reject` at 61.5 s: the ghost "Reject" button is meant to be secondary.
- `canvas_content_at_edge` on the full-bleed canvases (wall, snow): intended.
