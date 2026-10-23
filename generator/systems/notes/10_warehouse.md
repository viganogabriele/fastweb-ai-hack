## Warehouse (`warehouse/`)

### How the DC stock was built
DC stock is reconstructed per plant × SKU × size so that it is *consistent with the internal shipments file*: every line of
`internal/logistics/shipments_dc_to_store.jsonl` is a goods issue on its `ship_date`; FW26 launch allocations (NOT in the internal
shipments file) are goods issues 2–8 days before launch (`outbound/LIKP...` delivery type `ZLAU`, refs `LAU<yymmdd><store>`);
e-commerce web reserve (storage location `W100`) is replenished from `0001` and consumed by online sales (same model as `ecommerce/`).
Receipts are PO goods receipts (regular + the key POs in `common.KEY_POS`). DC_CONSTRAINTS windows have **zero unrestricted stock**.

| SKU | DC truth |
|---|---|
| AUREA black `J20931A00012999` | Sells down from Aug 1 (IT10 ~536, HK30 ~656, US20 ~133) to **0 on Sep 11–12** in all DCs, zero until **Oct 16**. PO 4500218734: IT10 **420 pcs GR Oct 16** (the "420" everyone quotes for EMEA), HK30 1,040 GR Oct 16, US20 220 GR Oct 19, IT10 balance 300 GR Oct 19 (pulled in from Oct 30 on Oct 14). Big EMEA shipment Oct 20 (611 pcs), HK Oct 17 + Oct 21. Today ATP: IT10 15, US20 39, HK30 38. |
| IRIDIA powder pink `J20931A00618510` | Launch buy only (received ~Aug 17–21, all allocated to stores/web), **0 from launch Sep 3 to Oct 8**. Top-up PO 4500219960 = 600 pcs GR Oct 8 split **HK30 330 / IT10 190 / US20 80** (decided Sep 21, before the K-pop spike). E-com share HK 70 / IT 40 / US 15. Today ATP **HK30 88, IT10 70, US20 37** (+ W100 16 IT / 5 US) while Asian stores hold only a few units each against long waitlists and the APAC web reserve is empty → replenishment is event-blind (orders only up to the normal target). Next receipt PO 4500222417 (1,200 pcs) ETA **Nov 20** (Oct 5 first answer Nov 27; US line Nov 24). |
| IRIDIA black `J20931A00618999` | Reserved stock exhausted → 0 from **Oct 6/7 to Oct 20**; PO 4500221188 (850) GR Oct 20 (expedited from Oct 23). HK30 shipped 384 on Oct 21 (ATP 29 left); **IT10 275 / US20 88 ATP today, EMEA/US stores not yet replenished** (next EMEA order day Thu Oct 22). |
| VLOGO CARDIGAN size M (both colours) | DC zero from **Sep 30/Oct 1**; PO 4500221905 IT10 ETA **Oct 30** (120 black + 60 navy; vendor: 60% Oct 30 / 40% Nov 6), US20 Nov 3, HK30 Nov 4. NB **6 black M units sit in IT10 `RT01` (ungraded online returns)**, 3 at US20, 2 at HK30 – releasable stock nobody looks at. |
| AMALIA chocolate brown sizes 0/1/2 | DC zero from **Sep 25**; PO 4500222090 ETA **Nov 10** (IT10 150, HK30 60 Nov 12, US20 20 Nov 13). Sizes 00/3/4 still have a few units. |
| VEL (men's vest) | Batch `2607-A114` received Aug 11–12 (defective slider), shipped Aug 15 → Oct 2; QN **300004587** opened Sep 30, usage decision **Oct 2** → remaining batch blocked (`SPEME`, 0001) = **1,126 pcs** across DCs (IT10 527, HK30 419, US20 180; all colours); good batch `2609-B027` received Sep 18–21 used from Oct 3. Store + online defect returns land in `QM01` (HK: `QC-HOLD`), ~348 pcs by Oct 21. |
| NOVA black/navy (MAD01 mis-pick) | Book stock: deliveries 0080412337 / 0080412382 issued NOVA **999** but navy (742) left the DC. Cycle count **Oct 6**: +37 NOVA 999 / −37 NOVA 742 (BWART 701/702). Before Oct 6 the IT10 book stock of black NOVA is 37 lower than physical and navy 37 higher. |
| ASTRA black | STO 4700001288 IT10 → HK30: 71 pcs GI Oct 15, GR at TKO Oct 21 (ASN said Oct 20; flight offload). |

SS26 store stock returned on Sep 1 arrives Sep 4–12 in `RT01` and is moved to `OUT1` (stock lot) on Sep 15.

### Files and native quirks
- `sap_stock_IT10/MARD_AFS_IT10_YYYYMM.csv`: `;` separated, decimal comma `1.234,000`, dates `DD.MM.YYYY`, unit `ST`, UTF-8.
  **No extraction on Sundays** (missing days). **30.09.2026: the W100 block is duplicated** (job ran twice) → summing doubles web stock.
- `sap_stock_US20/...`: same SAP extract but downloaded with US settings: `,` separated, decimal point, `MM/DD/YYYY`, unit `PC`,
  **cp1252 encoding** (e.g. `DOPOSCI APRÈS-SKI`).
- Storage locations: `0001` main, `W100` e-commerce reserve (not available for stores), `QM01` quality block (SPEME), `RT01` returns
  awaiting grading (RETME), `OUT1` stock lot. VEL rows carry batch (`CHARG`) 2604-A031 / 2607-A114 / 2609-B027; other SKUs no batch.
- `pcl_tko_inventory/TKO_INV_SNAPSHOT_YYYYMMDD.csv` (3PL): own item codes + EAN, HKT, location types PICK/RESERVE/ECOM/QC-HOLD/RETURNS/B-GRADE,
  `Allocated Qty` = store orders not yet shipped. File name = stock date, `Snapshot Time` = next morning 06:05 HKT.
  **Missing file 20261001** (National Day). **20261018 is a stale copy of 20261017** (same timestamps/quantities).
  The SAP-side ATP snapshot of Oct 19 for HK30 therefore uses Oct 17 data.
- `pcl_tko_inventory/TKO_TRANSACTIONS_*.csv`: `DD/MM/YYYY HH:MM` HKT, signed quantities, client ref = SHP id; `TKO_ASN_INBOUND.csv` (ASN ETAs, pre-advised open POs).
- `outbound/LIKP_outbound_deliveries_2026-08_10.csv`: delivery `VBELN` ↔ `XABLN` (internal SHP id) ↔ `BOLNR` (AWB). 9 deliveries have empty BOLNR
  (label printed in carrier portal). `ZLAU` = launch allocations (73 deliveries, not in internal shipments file).
- `outbound/MSEG_goods_movements_IT10_US20.csv`: BWART 101 GR, 601 GI (store deliveries + daily e-com collective), 311 transfers
  (0001↔W100, RT01→0001/OUT1 grading), 344 VEL block, 653 defect returns into QM01, 641 STO, 701/702 NOVA inventory differences.
- `inbound/EKPO_EKET_purchase_orders_FW26.csv` (`EINDT_ORIG` vs `EINDT`, ~8% of lines under-delivered and short-closed) and
  `inbound/CDPOS_po_delivery_date_changes.csv` (delivery-date change log; key POs have `WERKS='*'`).
- `atp/ATP_projection_YYYYMMDD.csv`: Mondays Sep 7 → Oct 19 + today Oct 22, 06:00. ATP_NOW = LABST(0001) − open deliveries; W100,
  blocked and RT01 are excluded. Weekly receipt buckets use **the ETA known at that date** (e.g. AUREA black: Sep 7 snapshot → Sep 25,
  Sep 14/21 → Oct 2, Sep 28 → Oct 9, Oct 5/12 → Oct 16). Generic POs show the original ETA until 7 days before receipt.
- `quality/QMEL_quality_notifications.csv`: VEL QN 300004587 (block), ARTEM fit check QN 300004571 (closed "within tolerance" →
  advise one size down), NOVA mis-pick QN 300004590, ASTRA fit QN 300004602 (open), a damaged carton.
  `quality/quarantine_returns_detail.csv`: one RMA per returned unit (stores = POS DEF returns with POS receipt id; e-com returns);
  `IN_TRANSIT_TO_DC` = returned in store but not yet received.
- `reservations/ZRESV_reservations_export.csv`: PR sample for the singer's agency **REJECTED_NO_STOCK at HK30 on Oct 5 and never re-submitted**
  (IT10 had pink from Oct 8 and issued 2 pcs to Vogue Italia on Oct 14); LON01 event stock (Sep 25, issued Oct 2); manual store
  backorders for AUREA black (PAR01/PAR02/MIL01/LON02, still OPEN) and IRIDIA pink (Asian stores); MIL01 cardigan M backorder; VIC hold
  AMALIA brown 1 rejected Sep 25.
- `api_samples/`: SAP OData `A_MatlStkInAcctMod` (AUREA black IT10 on Oct 15 = 0, Oct 16 after GR, Oct 20 after the big GI), WMS gateway
  ATP JSON, PO JSON with date history, VEL quality stock, 3PL API (camelCase, HKT) incl. a **STALE** response (Oct 18 → data Oct 17 with
  warning) and errors (429, SAP 503 maintenance window Sunday night).

### Signals / correct readings
1. "Where to find stock": IRIDIA pink 195 pcs ATP across DCs today (88 HK30) while APAC stores hold single-digit units per size (BJS01, CDU01 at zero) and the APAC web is sold out – push to SEL/TYO/SHA/HKG
   now (HK30) and consider IT10→HK30 or direct IT10→APAC for the 70 IT10 units (EMEA demand is low). Next real supply Nov 20.
2. IRIDIA black is back (IT10 275 ATP): EMEA/US stores with spill-over demand (PAR01, LON01, NYC02) can be replenished on Thursday's run.
3. AUREA black: DC stock is gone again after the Oct 20/21 waves (IT10 15). The 420 headline was only the IT tranche.
4. VLOGO CARDIGAN M: no DC stock until Oct 30, but RT01 return units exist (6 at IT10) and IBT from MIL02 is stuck (see logistics).
5. VEL: ATP excludes blocked batch; anything that sums SPEME/QM01 into availability is wrong (see agents bug).
