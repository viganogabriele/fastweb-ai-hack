## Planning (`planning/`)

### Files
- `FW26_merch_plan_OTB_v5.xlsx` – planner workbook, EUR k at budget FX, retail value. Sheets: `Summary` (cross-sheet formulas), `Assumptions`,
  `EMEA`, `AMERICAS`, `APAC` (category blocks × measures × months Aug-26→Jan-27; merged cells, frozen panes, live formulas:
  Receipts = Sales + EOP − BOP, OTB = Receipts − On Order, BOP = previous EOP, SUM totals, Var% formula), hidden sheet `OTB_v3_luglio`
  (pasted values, +12% vs LY – outdated). Cached values were computed with LibreOffice so `data_only` readers see numbers.
  Plan = LY (2025) actual × regional growth × category adjustment; Actual Sales Aug/Sep from internal daily sales, **Oct = MTD to Oct 21**
  compared with a full-month plan (Summary note warns; the Oct var% ~ −35% is NOT a real miss). Aug–Sep actual is ~10–15% under plan, in line
  with the internal KPI budget gap. Comments: EMEA outerwear on-order note about MAIRE black re-order; APAC "ILVARO pink: no upside foreseen".
  Assumptions: POLARIS EU = Genius FW25 CN/HK profile (factor 1.0); ILVARO "BADY × 0,55 (allocation) / forecast BADY × 0,6"; SYD01 profile NH_STD.
- `allocation_plan_FW26_new_products.xlsx` – allocation tool export. `Wave1_0309` (ILVARO, AMBRINE, ARNEB, ROSIERE, WOOL TURTLENECK) and
  `Wave2_Genius_2409` (POLARIS). `alloc_qty` **equals what stores really received** (= store stock EOD on launch day + launch-day POS sales;
  identical to the `ZLAU` deliveries in the WMS). `calc_qty` is the tool's pre-rounding value (±18%), `override=MANUAL` where they differ by > 1.5.
  Analogs: ILVARO→BADY × **0.55** (events.py note says forecast used 0.6 – the two numbers are both "true": allocation 0.55, forecast 0.6),
  AMBRINE→HERMINE × 0.8 with 70/30 black/brown split, ARNEB→MONTCLA 0.85, ROSIERE→KARAKORUM 0.9, POLARIS→"GENIUS FW25 DROP (CN/HK profile)" × 1.0
  for every region (the flaw behind EU/US over-allocation). Quirks: Wave2 uses **store names/aliases instead of codes** ("Monte Napo", "Harrods",
  "銀座"...) and has no `werks` column; one row duplicated (ILVARO 510, SEL02, size 1) → summing double counts 1–2 units; season_profile NH_STD everywhere.
- `replenishment_parameters_stores.csv` – SAP-ish (`;` separator, **decimal comma**), German/English field names: `BESTELLTAGE` (order days:
  EMEA/AMERICAS flagships MO/DO, others MO; APAC flagships DI/FR, others DI), `WBZ_TAGE` lead time (from world.py LEAD), `REICHWEITE_TAGE`
  cover 21 EMEA / 28 AMERICAS+APAC, safety 1.15, service level, `SAISON_PROFIL`. Planted: **SYD01 = NH_STD** (should be southern hemisphere,
  root of the ~2.5× heavy over-forecast); **MAD01 WBZ_TAGE = 1** last changed 2024 by a migration user (real transit 2–4 days);
  **STM01 still ACTIVE** although closed from Oct 19 (note says "bloccare riordini!"); CRT01 order day Monday although open Fri–Sun in October;
  COU01 `BLOCKED_SEASON`; ROM01 note "no parameter change" despite −50% footfall.
- `min_presentation_by_store_category.csv` – min units per core size and max facings; SYD01 has 34 outerwear facings vs 6 jersey.
- `sop_minutes/` – S&OP minutes Sep 7 (DOCX, IT), Sep 21 (MD, EN), Oct 2 ILVARO call notes (MD, IT), Oct 5 (DOCX, EN), Oct 19 (DOCX, IT)
  + `..._DRAFT.md` and `planner_running_notes_GBellini.md`. Each document reflects what was known **at that date** (PO ETAs from
  `common.KEY_POS` revision history).

### Planted contradictions / traps
- **Oct 19 DRAFT vs final**: draft says EMEA MAIRE allocation 60% to the four Korean-demand stores, IT balance 300 still due Oct 30,
  ILVARO pink re-order Nov 27, SEL01 pink arrived Oct 13, ILVARO black Oct 23, "Polaris STO arrived" – all wrong/outdated. Final DOCX: 45%,
  balance arrived Oct 19, re-order **Nov 20**, pink arrived **Oct 18**, ILVARO black Oct 20, STO arriving Oct 20 (actually received Oct 21).
- Oct 2 call notes: "~700 notify-me requests this morning" (export: ~190); "SEL01, SEL02, BUS01 sold out" (true for the day);
  split HK330/IT190/US80 **kept unchanged** although Asia was exploding → the 70 IT10 pink units still sit in Italy on Oct 22.
- Sep 7 Golden Week override +25% MIL/PAR "action" was **never loaded** (Sep 21: template rejected); the SYD01 forecast fix is parked in every
  meeting and still not done on Oct 19.
- Oct 19: Bellini keeps priority on PAR01/PAR02/MIL01/LON02 for the 420 MAIRE black **although the Korean tourist wave ended mid-October**
  (Moreau's warning) – risk of over-allocating; the correct move is to rebalance toward stores with current demand.
- Oct 19: "~110 pink at HK30 and ~80 at IT10 not shipped because the automatic replenishment only covers the event-free target" – this is the
  root cause the teams should detect and fix (event-aware proposal / demand multiplier).
- Oct 5: ILVARO black re-order ETA Oct 23 (true then); changed to Oct 20 on Oct 9.
