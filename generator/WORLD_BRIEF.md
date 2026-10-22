# Synthetic world brief (shared by all data-generation agents)

Hackathon: Moncler (luxury outerwear) — "Forecast che ascolta i negozi". Teams must build a system that fuses
numeric sales/forecast data, free-text store closing emails (multilingual), heterogeneous reports (PDF/XLSX/PPTX
with contradicting metric definitions), external data (weather, events, tourism, calendars, trends) and the
"agents" of other systems (warehouse, logistics, marketing, planning) into actionable recommendations
(what to replenish, where to move stock, what to tell clients). We are generating the **test data**.

"Today" is **Thursday 2026-10-22**. Last closed business day: 2026-10-21.

## Where things are

- `generator/config.py` — stores (39), styles, colours (with names in it/en/fr/de/es/ja/ko/zh), size runs.
- `generator/events.py` — **ground-truth scenario** (events E01..E45, DC stock-outs, stock caps, closures). READ IT.
- `generator/world.py` — simulator (already run). Do NOT modify or re-run it, do NOT modify `generated/sources/erp/`.
- `generated/sources/erp/` — already generated internal data:
  - `master_data/` stores.csv, styles.csv, sku_colour.csv, sku_size_ean.csv, price_list_FW26.csv, store_assortment.csv
  - `sales/daily_store_sku/sales_daily_YYYY_MM.csv` (2024-09-01 → 2026-10-21), `sales/pos_lines/pos_lines_2026-Www.csv` (line level, Aug→Oct 2026, with customer nationality, tax-free, returns + reason codes)
  - `kpi/store_daily_kpi.csv` (net sales local ccy, EUR at budget rate, receipts, visitors, conversion, budget, vs_budget_pct)
  - `traffic/door_counter_daily.csv`, `inventory/store_stock_daily/stock_eod_YYYY-MM-DD.csv` (size level, Aug→Oct 2026)
  - `logistics/shipments_dc_to_store.jsonl` (DC→store replenishments, planned vs actual arrival, wrong items)
  - `forecast/` statistical forecast (event-blind!): SKU×store×week runs every Monday, store weekly value, region xlsx
- `generated/ground_truth/` — hidden answers for evaluation (NOT a source): `scenario/events.json`,
  `demand/lost_sales_daily.csv`, `demand/true_demand_window.csv`, `writer_inputs/email_context/<STORE>.json` (per store per day: KPI, top sellers, customer nationality
  mix, **unmet requests** = customers asking for unavailable items/sizes, zero-stock key sizes, returns with reasons,
  deliveries received incl. delays / wrong items, active events).
- Output of the new sources goes under `generated/sources/<area>/`. Put any generator script you write in
  `generator/<your_area>/` so it is reproducible (python: `.venv/bin/python`; available libs: numpy, pandas,
  openpyxl, xlsxwriter, reportlab, python-pptx, python-docx, pyarrow, matplotlib; `soffice` is installed for
  conversions). If you need another lib: `uv pip install --python .venv <pkg>`.
- If you plant contradictions / traps / noise, document them in `generated/ground_truth/answer_keys/<your_area>_notes.md`
  (what is wrong, where, and what the correct reading is). That file is the answer key for testers.

## Key scenario facts (dates 2026)

- E01 Chinese Golden Week (Sep 30–Oct 8) tourists in MIL/PAR/LON02/TYO/OSA/SEL01/HKG/ZRH/VEN; E01b domestic in CN stores.
- E02 Korean tourists ask for **black MAIRE** (women's short down jacket) at PAR01, PAR02, MIL01, LON02 from ~Sep 19; black sold out ~Sep 21–24, DC out until Oct 16. Beige/navy don't substitute.
- E03 LOGO CARDIGAN **size M** finished at MIL01 on **Thursday Oct 8**; DC has no M until end of October.
- E04 ROM01 construction site / scaffolding in front of entrance Sep 14 → Nov 6: footfall halved.
- E05 Early cold snap Oct 12–19 (Munich first snow Oct 14, snow to 1000 m in CH, 2–6 °C max) in MUN/BER/ZRH/STM/CPH/AMS/GVA; milder echo Paris/London/Milan Oct 13–19.
- E06 Fictional K-pop idol **Yoon Ha-eun** (girl group **LUMIERE**) photographed Oct 1 at Paris Fashion Week in **ILVARO powder pink (510)** — a FW26 NEW product with no history. From Oct 2 sold out across Asia in 1–3 days; replenishment tiny (DC top-up Oct 8). Spill-over on ILVARO black/off-white.
- E07 Genius **POLARIS** capsule launched Sep 24: strong in China/HK, weak in EU/US (fit small, price high).
- E08 **TIB** men's down vest: zipper slider defect (units delivered from mid-Aug) → defect returns from Sep 28 (POS reason DEF).
- E09 Typhoon signal 8 Hong Kong: HKG01 closed Sep 17, opened 15:00 Sep 18.
- E10 Paris transport strike Tue Oct 13; E10b Italian general strike Fri Oct 16.
- E11 NYC02 POS outage Oct 6 14:10–17:40, sales posted with business date Oct 7.
- E13 Japan price increase on Nov 1 (announced to clients Oct 9) → pre-buying rush from Oct 12; E13w warm early October in Japan (27–29 °C, Sep 28–Oct 11) down jackets not moving.
- E14 SEL01 shipment held at Incheon customs (missing KC certificate) planned Oct 8 → arrived Oct 13. E14b MAD01 received navy MAYA instead of black (picking error) late Sep.
- E15 FW26 campaign US/UK from Sep 15: real effect ~+6%, agency claims +22%.
- E16 SYD01 (southern hemisphere spring): forecast uses northern seasonality and over-forecasts down jackets; customers want T-shirts/polos/light jackets.
- E18 LON01 private client evening Oct 8. E20 UNGA closures NYC01 Sep 21–26. E21 Milan FW Sep 22–28, Paris FW Sep 29–Oct 7.
- E22 Double 11 presales from Oct 20 → CN store traffic softer, clients ask for price matching.
- E24 TIFF Toronto Sep 10–20. E27 competitor (Canadian outerwear brand) pop-up across the street from SEL01 from Oct 15.
- E28 MIA01 AC broken Sep 3–5. E31 Acqua alta Venice Oct 20 (VEN01 opens at 12:00). E34 Singapore GP Oct 9–11.
- E37 CPH01 staff shortage Sep 28–Oct 4 (reduced hours). E39 heat wave Beverly Hills Sep 8–12. E40 MAD01 door counter broken Oct 1–7.
- E41 AMBRINE (new long down coat) in **chocolate brown** very requested in MIL/PAR/LON01/MAD, brown sizes 0–2 out at DC.
- E42 ARNEB (new men's parka) fits large → size exchanges, staff advise one size down. E43 BIFF Busan Oct 1–10.
- E44 CRT01 open Fri–Sun only in October. E45 STM01 closes for Zwischensaison from Oct 19. COU01 closed for the season (Sep 13 → Nov 26).
- Product names are style names (MAYA, MAIRE, ILVARO...). Store staff use nicknames, colour names in their own language,
  sizes in Moncler numbering (00/0/1/2/3/4 women, 1–7 men outerwear; XS–XXL knit/jersey; EU shoe sizes; TU accessories).

## Realism rules (everyone)

- It must look like data that came out of real, messy companies — NOT like AI output. Avoid uniform structure, avoid
  the same phrasing twice, avoid perfectly balanced bullet lists, avoid "Overall, ..." / "In summary" / em-dash-heavy prose.
- Mix structure levels: some sources are clean tables, some are half-structured, some are free text. Different
  systems use different IDs/names for the same thing (e.g. "MIL01", "Milano Montenapoleone", "Monte Napo", "MI-MN", store code 1001...).
- Plant realistic data-quality problems (missing values, duplicated rows, different date formats, decimal commas,
  local currencies, typos, encoding of accents, late/corrected files), but keep them documented in ground_truth notes.
- Signals should be consistent with the scenario, but with lag, partial coverage and noise — not every event appears
  in every source, and sources sometimes disagree or are wrong.
- Never mention event IDs (E01...) or the words "ground truth"/"synthetic" inside `generated/sources/`.
