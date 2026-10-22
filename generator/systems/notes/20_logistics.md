## Logistics (`logistics/`)

### Files
- `tms_shipments.csv` – one TMS load per internal shipment (538 `REPLENISHMENT`, same ids/dates as the internal jsonl) plus 73
  `LAUNCH_ALLOCATION` loads that do not exist in the internal file. Keys: `delivery_vbeln` (SAP), `shipment_ref` (SHP / LAU id), `awb`.
  `planned_delivery` = internal planned arrival; `carrier_edd` = carrier promise (differs only for SHP02600440: EDD **Oct 8**, internal plan Oct 12).
  `freight_cost_eur` from the lane cost model.
- `carrier_tracking_events.jsonl` – visibility-platform feed, **UTC** (`event_time_utc`), normalized status + raw carrier code/description
  in the carrier's language (BRT Italian, GEODIS French, SF Express Chinese/English, Nippon Express JP/EN). The event timeline always ends
  on the internal `actual_arrival`; 38 shipments still in transit (events up to Oct 22 06:00 UTC).
  Quirks: `shipper_reference` is the SAP delivery for DHL/FedEx/UPS/Nippon Express, the SHP id for GEODIS/SF/Kerry and
  `RIF.MITT. <last 6 of VBELN>` for BRT; **BRT timestamps are Italian local time mislabelled as `Z`** (2 h off in summer);
  ~1.5% duplicated events (webhook retries, same content, different `received_at_utc`); file is ordered by `received_at_utc`, not event time
  (out-of-order); ~1% events with null city.
- `customs_declarations.csv` – all non-domestic/extra-EU loads (CH, GB, AE, CA, all APAC except HKG01); `shipment_ref` left empty on ~30%
  of rows (join via `awb` / `tms_load_id`).
- `incidents/servicenow_incidents_logistics.csv` + `incidents/servicenow_worknotes.json` – `opened_at` shown in instance time (Europe/Rome,
  no offset). Multilingual work notes.
- `ibt_transfers_storelink_export.csv` – retail-ops IBT tool (internal store ids, local times). ~200 requests Aug 4 → Oct 21, 132 received
  (lead time request→receipt median 4 days, cost €16–58). SKU sometimes without size suffix (size in its own column). One request exported twice.
  **Executed IBTs are not reflected in `internal/inventory/store_stock_daily`** (that feed does not book IBT movements) – do not try to reconcile.
- `lane_matrix_lead_time_cost.csv` – 3 DCs + 39 stores → 39 stores (1,599 lanes; SAP plant codes). Contract transit, observed p50/p90 from
  the last 80 days (DC lanes only), pickup cut-off (stores: road 12:00 local, same-city courier 15:30; DCs 14:00 CET / 15:00 ET / 16:00 HKT),
  customs/documents, IBT policy, fixed + per-unit cost, CO2.

### Scenario signals
1. **SEL01 customs hold** – load `SHP02600440` / delivery `0080412440` / AWB `NX3467086408` (Nippon Express): picked up TKO Oct 7, arrived
   ICN Oct 8 03:20 KST, **customs hold Oct 8 (KC certificate missing)**, released Oct 12 17:24 KST, delivered **Oct 13**. Carrier EDD Oct 8,
   internal plan Oct 12 → the internal `delay_days=1` hides a 5-day slip vs the carrier promise. The load contained ILVARO **off-white only**;
   the pink top-up (20 pcs) left TKO on Oct 10 in `SHP02600455`, was **selected for inspection** (follow-up of the KC case) and delivered Oct 18
   (planned Oct 15). Incidents INC0042230 / INC0042398. Store staff believed pink was in the first box (work notes).
2. **MAD01 mis-pick** – deliveries 0080412337 (Sep 24→26) and 0080412382 (Sep 30→Oct 1): 17 + 20 MAYA navy shipped instead of black.
   INC0041877 (Spanish/Italian notes; DC first blames the store), duplicate INC0042011, root cause bin labels swapped (QN 300004590),
   cycle count Oct 6, black MAYA in delivery 0080412427 (shipped Oct 8, **arrived Oct 11, 3 days late**). 37 navy still at MAD01 (open).
   IBT MIL01→MAD01 MAYA black sizes 3/4 (2+2) received Oct 3.
3. **MAIRE black IBTs** – ROM01→MIL01 (2+1, received Sep 24), LON01→LON02 same day (Sep 25); rejected: CAN01→PAR01 (source refused),
   **COU01→MIL01 (store closed for the season although it holds 6 black Maire)**, GVA01→PAR02 (CH→EU cross-border not allowed),
   BER01→PAR01 on Fri Oct 2 13:xx (**after 12:00 cut-off**, first pickup Monday → client leaves Sunday → cancelled).
4. **LOGO CARDIGAN M** – IBT MIL02→MIL01 *approved* Oct 9 but never shipped (department store must release goods); ROM01→MIL01 and
   VEN01→MIL01 still `REQUESTED`. Same-city courier lane MIL02→MIL01 costs ~€16, same day if booked before 15:30.
5. **ILVARO pink IBTs in Asia** – SIN01→SEL01 rejected (cross-border, KC document), BUS01/SEL02→SEL01 rejected (no stock), BJS01→SHA01 rejected,
   TYO02→TYO01 1 pc received Oct 5. Cross-region IBT never allowed (route via DC / STO).
6. **SYD01** – IBT requests for polos/tees from SIN01 rejected (cross-border); INC0042302 complains about receiving puffers in spring.
7. Other delays have plausible causes in the events: HKG01 typhoon (SHP02600311, INC0040912), Rinascente goods-in slot (SHP02600413),
   ZRH01 damaged carton (SHP02600335), SYD01 flight offloaded (SHP02600449), SHA01 CIQ inspection still open (SHP02600501, INC0042777).
   NYC01 UNGA frozen zone caused a 2-hour delay, not a late day (INC0041190); Italian strike Oct 16 and acqua alta Oct 20: no delivery impact.

### Planted master-data issues in the lane matrix
- **MAD01 lanes**: `transit_days_contract` IT10→1501 = 1 (stale, last reviewed 2024-03-02) while observed p50 = 2 and p90 ≈ 4 –
  consistent with the planning parameter WBZ_TAGE=1 for MAD01 (also stale).
- **KR lanes do not list the KC certificate** in `documents` – the gap that caused the Incheon hold.
- COU01 as origin: `ibt_allowed` = "N - store closed for season"; CN destinations: not allowed (import licence); cross-region: not allowed.
- SYD01 lanes last reviewed 2025-01-20. Inter-DC lanes (IT10→HK30) are not in the matrix (managed manually; the logistics agent errors on them).
