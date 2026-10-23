# Reports area - answer key (heterogeneous reports, definitions, contradictions)

Scope: everything under `generated/sources/reports/`. Generator: `generator/reports/` (`.venv/bin/python generator/reports/run_all.py`). All numbers below are recomputed by `build_notes.py` from the same data.

## 0. Reference truth used to judge the reports

- **Internal BI (`generated/sources/internal/kpi/store_daily_kpi.csv`, `sales/daily_store_sku`)** is the reference: net sales = gross - discounts - returns (returns booked on the processing day), **excluding VAT / consumption tax**, local currency. `net_sales_eur_bud` is at **budget rates** (`BUDGET_RATE`). Every report number is a transformation of these tables (plus POS lines, stock snapshots, shipments).
- Actual FX = monthly averages of `generated/sources/external/fx/ecb_reference` (TWD and AED crossed from `fxfeed_usd_base`). Sep-2026 avg: USD 1.1784, GBP 0.8694, CHF 0.9274, JPY 172.39, KRW 1629.78, CNY 8.1563. 'Constant FX' = 2025 full-year average: USD 1.1249, JPY 167.92, KRW 1592.53, CNY 8.0813, SGD 1.4718.
- 2025 receipts in BI are partly estimated (units/1.35) by the simulator's legacy POS, so **LY conversion/ATV/UPT are not reliable** (EMEA MBR shows conversion down in almost every store mostly because of this).
- Calendar September 2026 retail net sales: EMEA EUR 12.49 m at Sep actual FX / EUR 12.56 m at budget FX; APAC EUR 14.09 m / EUR 15.04 m; Americas EUR 3.13 m / EUR 3.42 m.

## 1. Inventory

| File | Author (fictional) | Format / language | Period & calendar | Key definitions |
|---|---|---|---|---|
| retail_controlling/weekly_flash/Flash_W36..W42_2026.xlsx (+ W40 v1 and v2_corrected) | Retail Controlling HQ (M. Galli) | XLSX, EN | ISO weeks Mon-Sun | net of returns, ex VAT, EUR at monthly avg FX of the month of the week's Thursday (October = MTD avg at issue date), LY at LY monthly FX, LFL at constant CY FX for stores trading >=5 days both weeks; vs budget at budget FX; SAP plant codes (1001=MIL01 ...) |
| retail_controlling/weekly_flash/export_classifica_negozi_sett42.csv | BI Italia export | CSV `;`, decimal comma, latin-1, IT headers | W42 | same as W42 flash; date dd.mm.yyyy |
| emea/EMEA_MBR_Sep26_v3_FINAL.pdf | EMEA Retail Excellence + F. Arrighi (EMEA Retail Director) | PDF 10 p., EN | calendar Sep 1-30 | EUR at BUDGET FX both years, net of returns, LFL = standalone DOS only (excl. MIL02, PAR02, LON02, BER01, COU01, CRT01, STM01), sell-through on VALUE |
| apac/APAC_Monthly_Review_SEP2026_v1.1.pptx | APAC Business Analytics HK | PPTX 13 slides, EN + JA/KO/ZH quotes | mixed (see 2.3) | constant FX 2025 avg, sales GROSS of returns, Japan tax-incl from country file, Korea dept stores on dept-store month |
| apac/japan/国内直営店_月次売上報告_2026年9月度_確定.xlsx | 日本支社 営業企画部 (小林) | XLSX, JA | 9月度 = Sun 30/8 - Sat 3/10 (5 weeks) | 税込 x1.10 on all sales (also tax-free), net of returns, JPY, 前年比 as ratio (116.4% = +16.4%) |
| apac/japan/【週次速報】国内店舗_2026年10月第3週(10.11-10.17).xlsx | 日本支社 営業企画部 | XLSX, JA | week Sun 11/10 - Sat 17/10 | 税込, 前年比 ratio, waiting-list counts approximate |
| apac/korea/[주간] 백화점 매출 보고_10월 3주차(10.12~10.18).xlsx | 발렌티노 코리아 리테일팀 (정다은) | XLSX, KO | weeks Mon-Sun numbered by month of Thursday; MTD on dept-store month (26th-25th) | VAT incl. x1.10, net of returns, 백만원 in summary / 천원 in detail; SEL01 shown 'for reference' |
| apac/china/中国区9月经营月报_2026_v2.pptx | 中国区零售运营部 | PPTX 9 slides, ZH | calendar Sep | 含税 x1.13 on stores, stores + 天猫 + 微信小程序, 售罄率 = sold/(sold+EOP stock) units |
| americas/AMER_Retail_Monthly_FY26_P08_Sep.xlsx | Valentino USA Retail Finance (J. Morales) | XLSX merged multi-row headers, EN | NRF 4-5-4: P08 = Sun 30/8 - Sat 3/10 (5 wks); P09 MTD 4/10-17/10 | USD, net of returns, CAD at plan rate 1.37 CAD/USD; Aspen LY stored as text; hidden 'chk' column |
| merchandising/FW26_NewIn_SellThrough_wk42_final.xlsx | Merchandising Planning (S. Bianchi) | XLSX, EN | cumulative since launch to Sun 18/10 (W40/W41/W42 snapshots) | ST% = units SOLD (gross, returns not netted) / units RECEIVED |
| marketing/HaldenRowe_Valentino_FW26_Campaign_Performance_US-UK_FINAL.pdf | Halden & Rowe (media agency) | PDF glossy 6 p., EN | weeks 1-4 of flight 15/9-13/10 | 'attributed uplift' = YoY exposed stores minus YoY 'unexposed' (ASP01, TOR01) |
| market_research/Castellane_Luxury_Outerwear_Pulse_Q3-2026.pdf | Castellane Advisory (syndicated) | PDF 8 p., EN | fieldwork 20/7-10/8, published 30/9 | market-level, not derived from internal data |
| tax_free/Aurelia_TFS_merchant_extract_VALENTINO_W36-W43_2026.xlsx + Aurelia_Merchant_Insights_Valentino_Sep-Oct2026.pdf | Aurelia Tax Free (refund operator) | XLSX + PDF, EN | ISO weeks; W43 partial | forms ISSUED (not validated), spend incl. VAT, EUR at monthly ECB avg; nationality = passport keyed at POS |
| customer_care_quality/CCQ_Monthly_Report_2026-09_rev1.2.docx (+ .pdf export) | QA & Customer Care (L. Moretti, C. Rinaldi) | DOCX/PDF, IT+EN | Sep + early warning to 11/10 | defect rate on same-period sales; ARTEM rate on receipts |
| board/Q3_2026_Trading_Update_BoD_draft_v5.pptx | Group Finance / IR prep | PPTX 6 slides, EN | calendar Q3 (Jul-Sep), Oct QTD 1-18/10 | organic = constant 2025 FX; rounded EUR m; digital/wholesale from consolidation |
| digital/Digital_Weekly_Channel_Report_W42_2026.xlsx | Digital Analytics (E. Conti) | XLSX, EN | ISO weeks on UTC days | demand = gross ordered value incl. VAT; notify-me = requests (not unique customers) |

## 2. Report by report: what was done to the numbers, and what is wrong

### 2.1 Weekly flash (Retail Controlling)

| Week | Net sales EUR (current FX) | Δ% reported | Δ% LFL cFX | vs budget | non-LFL stores |
|---|---|---|---|---|---|
| W36 | 5,558,026 | -5.1% | -5.3% | -12.3% | - |
| W37 | 6,516,951 | +7.1% | +6.8% | -10.4% | - |
| W38 | 7,044,533 | +8.7% | +8.4% | -9.9% | COU01 |
| W39 | 8,146,857 | +13.8% | +13.6% | -6.1% | COU01 |
| W40_v2 | 9,811,191 | +15.3% | +14.9% | +0.4% | COU01 |
| W41 | 10,119,330 | +19.5% | +18.9% | -3.9% | COU01, CRT01 |
| W42 | 11,013,510 | +26.1% | +25.5% | -2.2% | COU01, CRT01 |

- **W40 v1 is wrong (genuine mistakes, corrected in v2)**: KRW rate 1,366.9 used instead of 1,636.9 (digits transposed) -> South Korea 1,710,092 EUR in v1 vs 1,428,019 in v2; DXB01 (plant 1801) listed twice -> EMEA overstated by 117,728 EUR. Totals: v1 10,210,991 vs v2 9,811,191. Use v2. Note v2 still displays 'issued 06/10' on the cover while the change log says 07/10.
- W41 daily sheet: NYC02 06/10 low and 07/10 high because of the POS outage (receipts 14:10-17:40 posted with business date 07/10); weekly total is right, daily split is not. Not restated anywhere.
- W40/W41 MAD01 traffic = 0 for 01-07/10 (door counter broken) -> conversion shown 'n.m.'; the CSV ranking of W42 is fine but W41 conversion for MAD01 is not meaningful.
- CRT01 drops out of LFL from W40 (open Fri-Sun in Oct 2026, closed from 06/10 in 2025); COU01 out from W38. The October FX is the month-to-date average at issue date, so W40-W42 use slightly different October rates.
- Summing W36-W39 flashes does NOT give September: W36 starts 31/08 and W40 contains 28-30/09.

### 2.2 EMEA MBR September (PDF)

- Net sales EUR 12.56 m at **budget FX** (+3.8% vs LY, -11.1% vs budget). At actual Sep FX (flash convention) EMEA calendar September = EUR 12.49 m. Differences come from GBP/CHF/DKK/AED: e.g. LON01 = GBP 1,220,463 -> EUR 1.436 m at 0.85 (budget) vs EUR 1.404 m at 0.8694 (Sep avg).
- **Mistake 1 (stale number)**: executive summary says LFL **+10.0%**, the KPI table says **+6.3%**. The text kept the v2 figure (ROM01 excluded from LFL); v3 reinstated ROM01 (see appendix version history). Correct (per the MBR's own definition): +6.3%.
- **Mistake 2**: country table 'TOTAL EMEA' = 11,991,217 EUR = sum of European countries only; Middle East (DXB01, 570,331 EUR) is listed but not summed. Correct total 12,561,548.
- **Mistake 3 (overstatement in commentary)**: director writes 'Korean clients are now more than 10% of the sales in Saint-Honoré'. POS nationality for PAR01 in September gives **5.4%**. What is true: Korean demand for black AUREA was largely UNMET (sold out ~21-24/9, DC out until 16/10), so it does not show up in sales - see lost sales and store emails.
- ROM01: -26.6% in the month, visitors -51.0% vs LY since works began 14/09 (correct, consistent with 'footfall halved').
- Sell-through on VALUE (sales / (sales + EOP stock at full retail), EMEA, cut-off 30/09): CASHMERE TURTLENECK 52%, AMALIA 48%, RIVIERA 46%, ARTEM 45%, IRIDIA 42%, ASTRA BALACLAVA 20%, ASTRA OVERSIZED 16%, ASTRA CAPE 14%. Not comparable with Merchandising unit ST (see 2.8). AMALIA value ST mixes black and brown; brown alone sells much faster.
- Conversion LY is inflated by estimated 2025 receipts (see section 0); do not conclude that conversion collapsed.

### 2.3 APAC Monthly Review September (PPTX)

Total shown EUR 15.91 m (+12.8% vs LY, -1.6% vs budget). Reference: APAC calendar September net sales = EUR 14.09 m at Sep actual FX, EUR 15.04 m at budget FX. Reasons for the gap:
- **Japan** pasted from the Japan country file: tax-inclusive (x1.10) AND 5-week 9月度 30/8-3/10 (includes Golden Week 1-3/10). Japan file = JPY 893,426,820 vs BI calendar Sep ex-tax JPY 693,610,800 (x1.288). APAC Japan 5,320,550 EUR vs 4,023,498 at flash definitions. Growth (116.4% ratio = +16.4%) is internally consistent because LY was taken on the same basis.
- **Korea**: SEL02+BUS01 on department-store month 26/8-25/9 (VAT removed), SEL01 calendar month gross of returns. Korea file dept Sep = KRW 3,310,492,900 incl. VAT (= 3,009,539,000 ex VAT) vs BI calendar Sep KRW 3,145,760,000.
- **Sales before returns** for all non-Japan markets (APAC returns are only ~1.7% of sales, small effect) and constant FX (2025 avg rates are stronger for JPY/KRW/CNY than Sep-2026 actual -> higher EUR). Budget is at budget rates -> 'vs budget' mixes two FX bases.
- **Mistake (genuine)**: South-East Asia (SIN01) left in SGD: shown 785,635 'EUR k' while the constant-FX value is 533,792 EUR. Growth % for SEA is still right (both years in SGD). APAC total with the fix = 15,660,412.
- ASTRA units 24-30/9: Mainland China 129 vs all EMEA 77 (consistent with strong China / weak Europe). Golden Week Mainland China stores 1-7/10 +41.5% (local currency, same dates LY).
- Korea slide quotes a Korean-language comment that Chuseok reduced domestic visits; the numbers show Korea still growing (flagship strongest). Sydney slide correctly states the southern-hemisphere seasonality problem of the statistical forecast.

### 2.4 Japan country files (JA)

- 9月度 (5 weeks) 税込 JPY 893,426,820, 前年比 116.4%, 予算比 90.8%. Ex-tax equivalent JPY 812,206,200. Tax-free share of sales 38.5% (still grossed up by 10%: the file treats tax-free as tax-inclusive sales refunded at the counter - an overstatement of ~3.8% of the total).
- Weekly 速報 10/11-10/17: 前年比 166.7% (Ginza 189.2%) = pre-buying before the 1/11 price increase (announced 9/10) + cold from 12/10. Waiting-list counts for IRIDIA pink ({'TYO01': 8, 'TYO02': 6, 'OSA01': 7}) are approximations (≈60% of true unmet demand).
- Ratio convention: 前年比 116.4% means +16.4%; readers converting it as +116% are wrong.

### 2.5 Korea dept-store weekly (KO)

- Week 10/12-10/18: department stores +49.2% vs LY (IRIDIA frenzy, BIFF tail), Cheongdam flagship -4.7% (competitor pop-up from 15/10 hits outerwear; IRIDIA stock arrived 13/10 after customs). Units: 백만원 in summary, 천원 in detail - mixing them is a 1,000x error.
- Waiting lists IRIDIA 인디 핑크 ({'SEL02': 29, 'BUS01': 15, 'SEL01': 24}) approximate (≈55% of unmet demand, duplicates possible).
- The '9월 마감' sheet is on dept-store month 26/8-25/9 - this is what APAC used.

### 2.6 China monthly (ZH)

- Stores 含税 RMB 41,487,973 = BI net ex-VAT RMB 36,715,020 x 1.13; stores +18.3% vs LY.
- Online = Tmall (RMB 11,870,000, from TP partner statement - **not available in any other source**, treat as unverifiable) + WeChat mini program (RMB 5,504,835, = CN 'WeChat Mini Program' rows in `systems/ecommerce/shopify_sales_by_variant_daily.csv`).
- **Perimeter trap**: online growth shown +58.8% compares Tmall+WeChat 2026 with Tmall-only 2025 (mini program 'launched Nov 2025'); like-for-like Tmall growth is +8.5%. Omnichannel total +27.9% is inflated for the same reason.
- ASTRA 售罄率 is units sold / (sold + EOP stock) per store 24-30/9 - a third sell-through definition. 小红书 note counts are third-party, synthetic, not cross-checkable.
- Golden Week stores +41.5% (same as APAC deck, local currency).
- Overstatements: 'IRIDIA 粉色 登记预订顾客超过百名' - true unmet demand in the 3 CN stores was ~36 units to 7/10 (~62 to 21/10); '核心尺码全部售罄' is right (SHA01 kept single pieces in sizes 3/4). The APAC deck's 'sold out in all Asian stores' is likewise true only for core sizes.

### 2.7 Americas monthly (P08, 4-5-4)

- P08 = 30/8-3/10 (5 weeks): USD 4,406,071 (-0.2% vs P08 LY, -13.6% vs plan). Calendar September with the same conventions = USD 3,688,962. Flash/EMEA-style EUR figures will not tie (calendar + FX + CAD at plan rate 1.37 instead of market ~1.371).
- Aspen LY stored as text (sums in Excel will skip it). Hidden column 'chk' = sales minus plan. TOR01 CAD 1,050,628.
- P09 MTD tab: NYC02 10/6 USD 12,625 vs 10/7 USD 50,090 (POS outage shift).
- Commentary: 'Agency reports strong attributed uplift; our read on comp stores is more modest' - the US team is right (see 2.9).

### 2.8 Merchandising FW26 sell-through

- ST% = gross units sold / units received (allocation + replenishments). Received is reconstructed as on hand + sold - restocked returns.
- IRIDIA 510 Asian stores at W40: 88.5% (core sizes sold out; the remaining units are single pieces in fringe sizes 00/3/4); by W42 some stores show stock again (DC top-up 08/10, SEL01 customs release 13/10) so ST falls - this is NOT a demand drop.
- Store ST above 100% (e.g. SEL02 109%, BJS01 140%) because returned units are restocked and resold (gross sold counts them twice).
- **Mistake (genuine)**: 'Region summary' ST% = unweighted average of store ST%, not sum(sold)/sum(received). Examples: ASTRA CAPE APAC: shown 43.9% vs weighted 54.5%; ASTRA CAPE TOTAL: shown 37.3% vs weighted 46.8%. The 'Style x Region' sheet is weighted and correct.
- ARTEM unit ST inflated by size exchanges (exchange = return + new sale).

### 2.9 Agency campaign report (US/UK)

- Claim '+22% attributed sales uplift' = exposed YoY +10.0% minus 'unexposed' YoY -11.7% over 15/9-13/10 = +21.7 pp. Problems: (1) control = Aspen (off-season, small) + Toronto only; (2) MIA01 excluded ('operational disruption' = AC failure 3-5/9, before the flight) although Miami is in the OOH plan (the media table lists 'OOH (NYC, LA, MIA, LON)') - and the recommendation slide says to 'add Miami'; (3) cherry-picked window ends 13/10 after LON01's private client evening (08/10, VIC event unrelated to media); LON01 YoY 15/9-7/10 = +11.0%; (4) NYC01 benefits from Golden Week/celebrity spill-over; (5) YoY difference is not a sales uplift.
- Footfall '+16%' built the same way (+16.1 pp). Media KPIs (412M impressions, 4.8% ER, ROAS 5.6x) are agency-only, not verifiable.
- Correct reading: true incremental effect ≈ **+6%** (scenario). Over the whole flight 15/9-21/10 the six campaign stores are +12.3% YoY vs +9.4% for comparable non-campaign EMEA/Americas stores, i.e. a single-digit gap. The Board deck repeats +22% as fact (wrong).

### 2.10 Market research (Castellane)

Generic, lagging (fieldwork closed 10/8). Claims contradicted by internal data / stores:
- 'Korean demand cooling (-8 pp)', 'Korean spend in Europe slowing': Korea stores +17.7% in September (APAC deck), dept stores +49% week 12-18/10, Korean tourists chasing black AUREA in Paris/Milan/London, IRIDIA frenzy; even the tax-free operator says Korean spend in France +18% YoY.
- 'Cropped puffers losing share' vs IRIDIA (cropped) best sell-through and sold out in Asia. 'Brown niche 4%' vs AMALIA chocolate highest ST in EMEA and DC out of brown.
- 'Golden Week favours domestic/short-haul over Europe' vs Chinese tax-free spend at Valentino Europe x3 in W40-41 and strong MIL/PAR.
- 'Mild October in Central Europe' vs the cold snap 12-19/10 (first snow Munich 14/10). 'Capsule fatigue in China' vs ASTRA success in China.
- Right: Japan pull-forward before price increases; Double 11 pre-sales ~20/10 softening store traffic.

### 2.11 Tax-free operator (Aurelia)

- Forms ISSUED, spend incl. VAT, nationality as keyed. Only 54.5% of forms validated so far (recent weeks incomplete) - issued-based growth overstates realised tourist spend; spend incl. VAT >> our ex-VAT net sales (IT x1.22, FR x1.20 ...).
- Headlines: Korean spend at Valentino France+Italy W39-40 vs W36-37 +9.7% (modest - because black AUREA was out of stock), Chinese spend at Valentino Europe W40-41 vs W38-39 +212% (Golden Week). 'Korean travellers flocked' overstates the merchant data.
- **Data-quality issue**: in 'Forms by week' the W41 Italy rows are duplicated (12 rows, 367 forms double-counted).
- UK not covered (no tourist VAT refund); market-context YoY table is operator-network-wide and synthetic.

### 2.12 Customer Care & Quality (DOCX/PDF)

- VEL 'tasso di difettosità' 42.3% = 295 DEF returns 28/9-11/10 / 697 VEL units sold in the SAME window. Wrong denominator: the defect concerns units sold since 15/08 (2546 units) -> 11.6% so far (or 10.9% of 2706 units delivered to stores since 15/08). Scenario truth: ~15-16% of affected units will come back.
- ARTEM exchange rate 9.5% on receipts (September) vs 10.4% of units sold to 11/10 (scenario ~10%); 56.6% end as size exchange.
- Return rates by region (Sep, units, POS): {'AMERICAS': 6.9, 'APAC': 1.8, 'EMEA': 3.5}. Contact-centre volumes are synthetic (no other source).

### 2.13 Board Q3 trading update (PPTX)

- DOS Q3 reported EUR 66.0 m (+5.7%), constant FX EUR 67.1 m (+5.9% organic). Region chart in constant FX rounds to AMERICAS 7, APAC 32, EMEA 28 -> sums to 67 while the channel table shows 66 (reported FX) - not an error, two FX bases + rounding.
- **Mistake**: Group 'Organic +7%' in the channel table is not consistent with its components (DOS ~+6%, Digital +17% on 21m, Wholesale -4% on 39m) -> weighted ≈ +4%.
- October QTD (1-18/10) +23.6% organic. Quotes the agency '+22%' uplift as fact (wrong, see 2.9). Digital/wholesale figures are synthetic.

### 2.14 Digital weekly (XLSX)

- Demand = gross ordered value incl. VAT (W42 EUR 2,422,753) vs net after returns (EUR 2,282,214); UTC days. Notify-me IRIDIA 510: 1666 requests = 1591 unique e-mails; AUREA black 148 / 135.

## 3. Contradiction matrix (same topic, different numbers)

| Topic | Source A | Source B | Why different | Right reading |
|---|---|---|---|---|
| EMEA September sales | MBR EUR 12.56 m | Flash-convention EUR 12.49 m | budget vs actual FX | both arithmetically right; for actual performance use actual FX, for budget comparison budget FX |
| EMEA LFL September | MBR text +10.0% | MBR table +6.3% | stale v2 text (ROM01 excluded) | +6.3% (standalone DOS) |
| EMEA total | MBR country table 11,991,217 | MBR KPI table 12,561,548 | Middle East not summed | KPI table |
| Korea W40 | Flash v1 EUR 1,710,092 | Flash v2 EUR 1,428,019 | KRW typo | v2 |
| Japan September | JP file JPY 893,426,820 | BI JPY 693,610,800 | tax incl. + 5-week 9月度 | BI for HQ; JP file internally consistent |
| APAC September | APAC deck EUR 15.91 m | BI EUR 14.09 m (actual FX) | const FX, gross of returns, JP tax/5wks, KR dept month, SGD error | BI / flash |
| Korea dept Sep | KR file KRW 3,310,492,900 | BI calendar KRW 3,145,760,000 | VAT + 26-25 month | BI calendar for HQ |
| China online growth | China deck +58.8% | Tmall LFL +8.5% | new channel in CY only | LFL |
| Americas 'September' | P08 USD 4,406,071 | calendar Sep USD 3,688,962 | 4-5-4 (5 weeks incl. 1-3/10) | depends on calendar |
| FW26 sell-through | EMEA value ST (AMALIA 48%) | Merch unit ST / China 售罄率 | value vs units vs (sold+stock) | state definition; Merch weighted sheet for units |
| Campaign effect | Agency/Board +22% | Americas finance 'more modest'; data single-digit | control choice, perimeter, window, confounds | ≈ +6% |
| VEL defect rate | CCQ 42.3% | 11.6% of units sold since 15/08 | denominator | ~12% to date, ~15-16% expected |
| Korean demand | Castellane 'cooling -8pp' | stores, KR file, tax-free +18% FR | lagging survey (fieldwork Jul-Aug) | Korean demand strong |
| Korean share Saint-Honoré | MBR commentary >10% | POS 5.4% | anecdote vs data; unmet demand invisible in sales | ~5% of sales, but large lost sales on black AUREA |
| Golden Week Europe | Castellane: favours domestic | Aurelia: CN spend Valentino Europe +212% vs prior 2 wks | forecast vs actual | GW strong in Milan/Paris |
| October weather | Castellane: mild October | flash W42, board: cold snap 12/10 | seasonal forecast vs actual | cold snap happened |

## 4. Genuine mistakes planted (checklist)

1. Flash W40 v1: KRW rate transposed + DXB01 duplicated (fixed in v2).
2. EMEA MBR: exec-summary LFL stale (v2 number); country TOTAL excludes Middle East; 'Korean >10% of Saint-Honoré' unsupported.
3. APAC deck: Singapore not converted from SGD.
4. Merchandising: region ST% = unweighted mean of store ST%.
5. China deck: online/omnichannel growth on non-comparable perimeter (WeChat mini program only in CY).
6. Quality report: VEL defect rate on same-period sales (42%).
7. Board deck: Group organic +7% inconsistent with components; repeats agency +22%.
8. Tax-free XLSX: W41 Italy rows duplicated.
9. Japan file: tax-free sales also grossed up by 10%.
10. Americas: Aspen LY stored as text (Excel totals ignore it if recomputed with SUM).

## 5. Scenario signals and where they surface in reports

- Golden Week (CN tourists Europe/Japan, domestic China): flash W40 notes, EMEA outlook, APAC early-Oct slide, China GW slide, tax-free PDF, Japan 9月度 week 5.
- Black AUREA unmet Korean demand (PAR01/PAR02/MIL01/LON02): flash W39/W42 notes, EMEA commentary + actions, Korea issues sheet, digital notify-me (KR/GB).
- VLOGO CARDIGAN size M at MIL01 (from 8/10): NOT in reports (only emails/stock) - by design.
- ROM01 works: flash W38, EMEA (chart + commentary).
- Cold snap 12-19/10: flash W42, board outlook; contradicted by Castellane forecast.
- IRIDIA powder pink (Yoon Ha-eun / LUMIERE): APAC early-Oct slide, Japan weekly, Korea issues, China social slide, merch IRIDIA sheet, digital notify-me, CCQ contacts.
- ASTRA strong China / weak EU-US: APAC, China, EMEA, Americas commentary, merch ASTRA sheet, flash W39; contradicted by Castellane 'capsule fatigue'.
- VEL zipper defect: flash W40, EMEA, CCQ report, Japan/Korea comments, board risks.
- HKG01 typhoon 17-18/9: flash W38, APAC Greater China slide.
- Paris strike 13/10, Italy strike 16/10: flash W42 notes only.
- NYC02 POS outage 6/10: flash W41, Americas P09 tab.
- Japan price increase / warm weather: Japan files, APAC, board, Castellane (correct).
- SEL01 customs delay + competitor pop-up: flash W42, Korea issues, APAC early-Oct slide.
- US/UK campaign: agency report, Americas commentary, board; true effect ~+6%.
- Sydney seasonality / forecast: APAC SEA & Oceania slide and asks.
- AMALIA brown: EMEA (value ST, commentary, actions), merch highlights, Castellane contradicts.
- ARTEM fit: CCQ, Americas commentary (Toronto), merch, APAC.
- MAD01 door counter, CPH01 staffing, MIA01 AC, BHS01 heat, UNGA, TIFF, LON01 VIC evening, SIN GP, BIFF: flash notes / Americas / Korea.

## 6. Non-derivable (synthetic) content

Tmall figures (China deck), all agency media KPIs, Castellane market sizes/survey, Aurelia market-context table, contact-centre volumes (CCQ), Board digital & wholesale revenue, Xiaohongshu note counts, lab test '21 of 24' (CCQ). Waiting-list counts in JA/KO files are derived from hidden lost-sales truth x 0.55-0.6 (noisy proxy). Everything else is computable from internal data + external FX.