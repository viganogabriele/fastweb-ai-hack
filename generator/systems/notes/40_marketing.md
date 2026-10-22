## Marketing / CRM (`marketing/`)

### Files
- `campaign_calendar_FW26.xlsx` – sheet `Calendar FW26` (Gantt: merged month headers, week columns W31–W53, coloured fills by type,
  cell comments with notes), sheet `List` (one row per activity, budget SUM formula), sheet `v3_OLD` (**superseded July plan with wrong dates**:
  US/UK OOH Sep 22, POLARIS Oct 1, LON01 evening Oct 15, Japan price letter Oct 15 – do not use).
- `media_plan_FW26_by_market.xlsx` – market × channel, flight, budget local + EUR, impressions/CPM, agency, spend-to-date %.
  AU runs the global winter creative in September (spring in Sydney). Harrods windows are barter (not in budget).
- `HartwellRowe_FW26_Altitude_flash_results_US_UK_wk38-41.pdf` – agency flash report claiming **+22% "attributed sales uplift"**.
  Its own table shows store YoY of **+9.0% US / +16.4% UK / +12.3% total** (EUR at budget rate, Sep 15–Oct 11 vs LY). The 22% adds last-click
  e-com revenue and a proprietary "Halo Index 1.35", has no holdout, and counts the **LON01 private client evening (Oct 8)** in exposed sales.
  The pre-period YoY of the same doors (Aug 15–Sep 14) is ~0%, while control flagships (PAR01, MIL01, ...) are up even more during the same weeks
  (Golden Week). Correct reading: real incremental effect is single-digit (~+6%); do not use +22% for forecasting.
- `salesforce_campaigns_export.csv` – Campaign object export. LON01 evening `7015g00000Q8LnBAAV`: 45 contacts, 39 responses,
  description "Attended 36 (+9 guests). Purchasers 23, 27 transactions, GBP 41,881 (POS matched)". Quirk: `BudgetedCost/ActualCost` are EUR
  even when `CurrencyIsoCode` says GBP/CNY/KRW/... (export issue). Also MIL01 MFW appointments, PAR01 PFW viewing, SHA01 Polaris preview,
  JP price letter (DM+LINE, 4,120 contacts), Golden Week WeChat outbound, newsletters (Sep 17 icons newsletter **features MAIRE black as hero
  while DC is at zero**), ILVARO "Pink edit" social (launched Oct 6 when nothing was in stock), KR waitlist SMS planned for Nov 20.
- `salesforce_campaign_members_LON01_private_evening.csv` – 45 members: 23 "Attended - Purchased", 13 "Attended", 3 "Responded - No Show",
  6 "Declined"; 9 plus-ones. `External_Client_Id__c` = POS `customer_id`; `Event_Purchase_GBP__c` = that client's POS net amount on Oct 8.
  NB POS has **no transactions after ~19:00** on Oct 8: event purchases were rung through during the afternoon appointments, so time-based
  matching of "evening" sales fails; match by client id.
- `salesforce_clienteling_notes_export.csv` – ~1,030 Task rows (UTC `CreatedDate`, CRM store codes, owner = POS sales-associate code,
  `Client_External_Id__c` = POS customer id when the client bought something that day, else empty). Free text in the store language
  (it/fr/en/de/es/ja/ko/zh-CN/zh-HK/zh-TW), lower-case/typos/abbreviations. Signal notes are sampled from the true unmet demand:
  MAIRE black (Korean clients, Sep 17+; neutral wording before the drama), ILVARO pink (from Oct 2, mentions Yoon Ha-eun), AMBRINE brown,
  LOGO CARDIGAN M (MIL01 from Oct 8 + others in Oct), ARNEB "one size down" (from POS size returns), TIB zip complaints (from POS DEF returns),
  Japan pre-buying before Nov 1 (TYO/OSA from Oct 10), POLARIS (CN likes it; EU "small and expensive"), Double 11 price-matching (CN Oct 20–21),
  SYD01 polos/tees in spring, cold snap DACH/CPH/AMS, MAD01 "only navy MAYA", Golden Week groups. ~420 routine notes. 6 duplicated notes
  (mobile retry: same text/time, new Id).
- `store_waitlist_reservations.csv` – clienteling-app export (~400 entries, CRM store codes, UTC). Entries are a sample of real unmet
  demand for MAIRE black, ILVARO pink/black, AMBRINE brown, LOGO CARDIGAN M, MAYA black (MAD01). Status NOTIFIED/FULFILLED only after the
  store actually got stock back (from store stock files). Quirks: item as `sku-size`, as `sku` only, or as free text ("MAIRE black");
  ~30% of entries that should be NOTIFIED are still **OPEN** (associates never updated); 12 duplicate entries; 3 clients on both PAR01 and
  PAR02 waitlists; **4 rows with invalid store code `KR1`** (= KR02 / SEL01); walk-in leads have no client id.
- `PR_seeding_tracker_FW26.xlsx` – seeding log. **Park Ji-woo** (actress) seeded MAIRE black size 0 on Aug 25 for the drama "Winter Letters"
  (episode aired Sep 16) → the origin of the Korean Maire-black wave, but nobody told planning. LUMIERE stylist received BADY, **Yoon Ha-eun
  was NOT seeded**; row added Oct 2 "NOT SEEDED – organic"; gifting request Oct 5 "ON HOLD – ATP 0 at HK30", still pending Oct 16 (IT10 had
  stock and gave 2 pcs to Vogue Italia on Oct 12–14). One row has post date before the sent date (logged late).
- `social_listening_alerts_export.csv` – Talkwalker-like alerts (UTC). Key: Sep 16 Maire/drama (KR), Sep 18 Maire black sold out Paris,
  Sep 24 Polaris CN spike, Sep 27 Polaris sentiment drop EU, Sep 29 TIB zip, **Oct 1 21:05 UTC Yoon Ha-eun pink jacket**, Oct 1 23:40 ILVARO
  61k mentions, Oct 2 "sold out at 7:30", Oct 3 spill-over on black, Oct 4 resale x2, Oct 8 Seoul delivery stuck at customs, Oct 9 JP price increase,
  Oct 11 counterfeit ILVARO, Oct 14 Arneb runs big, Oct 14 snow Munich, Oct 15 Canada Goose pop-up opposite SEL01, Oct 17 Maire restock,
  Oct 18 ILVARO pink at Cheongdam, Oct 20 Double 11. Noise: daily volume alerts on generic topics, a **false positive** (Monclar village), brand-protection alert.
