# Internal communications (non closing-email) — shared plan for all authoring agents

Project root: /home/lorenzo/dev/hackathons/fastweb-2026 (python: `.venv/bin/python`).
READ FIRST: `generator/WORLD_BRIEF.md`, `generator/EMAIL_SPEC.md`, `generator/events.py`, this file,
`generator/internal_comms/common.py` (helpers), `generator/internal_comms/_ref/weekly_digest.txt`
(per store, per ISO week W36..W43: days open, net sales local ccy in k, vs budget, top-3 customer nationalities,
active scenario events, # VEL defect returns, # ARTEM size returns, late/wrong deliveries, top unmet requests with counts).
Full per-day detail: `generated/ground_truth/writer_inputs/email_context/<STORE>.json`. Stock: `generated/sources/erp/inventory/store_stock_daily/`.

ISO weeks 2026: W36 Aug31–Sep6, W37 Sep7–13, W38 Sep14–20, W39 Sep21–27, W40 Sep28–Oct4, W41 Oct5–11,
W42 Oct12–18, W43 Oct19–25 (only 19–21 closed so far). Today is Thu 2026-10-22. Nothing may be dated after 2026-10-22 09:30 local.

## Output layout
- `generated/sources/erp_comms/area_manager_weekly/` (.eml, some .docx attached or standalone)
- `generated/sources/erp_comms/chat_exports/`
- `generated/sources/erp_comms/store_visit_reports/` (.docx / .pdf)
- `generated/sources/erp_comms/hq_memos/` (.pdf / .docx / .eml)
- `generated/sources/erp_comms/voice_of_customer/` (.csv / .xlsx / .txt)
- generator scripts + hand-authored content: `generator/internal_comms/<part>/`
- answer key: `generated/ground_truth/answer_keys/internal_comms_notes.md` (single file; parts were authored by one agent in the end). Fragment format: short intro, then a table or list
  `file -> what it says -> what is actually true / why it matters`. Plainly name events there (codes allowed ONLY in notes).

## Hard rules (same as WORLD_BRIEF realism rules)
- All text hand-authored by you as data (dicts / strings / literal lists). Code only wraps into formats. No f-string
  templating of prose from data. No two bodies sharing long identical sentences (check with `common.check_texts`).
- Never write event codes (E01, E06b...), "ground truth", "synthetic", "scenario", "simulated" inside generated/sources.
- Not AI-like: uneven length, personal habits, typos, missing accents, local language, corporate jargon where fitting,
  off-topic tangents. No "I hope this finds you well", no "Overall"/"In summary", no em-dash-heavy prose,
  no perfectly symmetrical bullet lists everywhere.
- Facts follow the scenario but with lag, approximations, partial coverage and some deliberate wrong info (documented).
- Do not modify anything under `generated/sources/erp/`, `generator/world.py`, `generator/events.py`, or other agents' dirs
  (`generator/emails_*`, `generated/sources/store_emails/`).

## People / addresses (domain valentino-retail.example; address = first.last@, no accents)
Store managers / assistant managers: see `generated/sources/erp/master_data/stores.csv`. Invent SAs freely
(keep a stable cast per store inside your part). Store mailbox: `<store lowercase>.store@valentino-retail.example`.

Area managers (AM) and whom they report to:
| AM | perimeter | lang of recap | To | Cc |
|---|---|---|---|---|
| Roberto Galli | MIL01 MIL02 ROM01 VEN01 COU01 CRT01 MAD01 | it | Francesca Valli (Regional Retail Director EMEA, Milan HQ) | Carlo Ruggeri (Country Mgr Italy) sometimes |
| Isabelle Moreau | PAR01 PAR02 CAN01 GVA01 | fr | Francesca Valli | Hélène Dubois-Rey (Country Mgr France) |
| Stefan Wagner | MUN01 BER01 ZRH01 STM01 | de (!) | Francesca Valli | Markus Engel (Country Mgr DACH) |
| Fiona McLeod | LON01 LON02 AMS01 CPH01 | en | Francesca Valli | Richard Ashby (Country Mgr UK) |
| Omar Haddad | DXB01 | en | Francesca Valli | — |
| Lauren Mitchell | NYC01 NYC02 MIA01 BHS01 ASP01 TOR01 | en | Mark Davidson (SVP Retail Americas, NYC) | — |
| 鈴木 拓也 Takuya Suzuki | TYO01 TYO02 OSA01 | ja | 森田 健二 Kenji Morita (Retail Director Japan) | Andrew Leung |
| 윤성호 Yoon Sung-ho | SEL01 SEL02 BUS01 | ko | 강민정 Kang Min-jung (Korea Country Manager) | Andrew Leung |
| 赵磊 Zhao Lei | SHA01 BJS01 CDU01 | zh-CN | 周雪 Zhou Xue (Greater China Retail Director, Shanghai) | 孙怡雯 Sun Yiwen (merch CN) |
| Vivian Lau | HKG01 TPE01 | en + some Cantonese/繁中 | Zhou Xue | Andrew Leung |
| Daniel Lim | SIN01 SYD01 | en (Singlish touches) | Andrew Leung (Regional Retail Director APAC, HK) | — |
Roberto is out of office Aug 31 → Sep 4. Francesca sometimes replies (short, English or Italian), e.g. asks Stefan to write in English.

HQ / functions (Milan unless noted):
- Merchandising EMEA: Chiara Bassi (merchandiser, women outerwear), Davide Longo (merchandiser, men + knit)
- Allocation & Replenishment EMEA: Luca Ferrari; DC Castel San Giovanni = "CSG", "DC-IT-CSG", "il magazzino"
- Product Quality / After-sales: Elena Rinaldi (quality-claims@)
- VM EMEA: Sofia Marchetti (vm-team@); Retail Excellence / training: Matteo Colombo
- Clienteling / CRM EMEA: Giorgia Sala (crm-emea@)
- Americas merch: Nicole Park (NYC); DC New Jersey "DC-US-NJ"
- APAC merch: Sun Yiwen 孙怡雯 (China), Jason Tsang (HK/TW), 山口 真理 Mari Yamaguchi (Japan), 오지은 Oh Ji-eun (Korea),
  Priya Nair (SEA/Oceania); APAC DC Hong Kong Tseung Kwan O "DC-HK-TKO", "TKO"
- DLs: retail-ops-italy@, retail-ops-france@, retail-ops-dach@, retail-ops-uk@, retail-ops-us@, retail-ops-japan@,
  retail-ops-korea@, retail-ops-china@, retail-ops-hktw@, merch-planning@, merch-planning-apac@, vm-team@,
  quality-claims@, all-stores-emea@, all-stores-apac@, all-stores-americas@, all-stores@

## Key facts derived from internal data (use as what people saw; with lag/noise)
- Black AUREA: zero at MIL01 from ~Sep 19-20, PAR01 ~Sep 28 (dwindling from Sep 21), PAR02 ~Sep 21, LON02 ~Sep 25,
  LON01 ran down to zero ~Oct 8. DC out until Oct 16 (420 units landing at CSG Oct 16). Unmet demand huge at
  PAR02 (97 requests W40), PAR01, MIL01, LON02 (~30-36/week). The first store re-allocation after Oct 16
  reached the ITALIAN stores on Oct 21 (MIL01 62 pcs, MIL02 36, **ROM01 40** despite halved footfall, VEN01 25, CRT01 8),
  while PAR01 (55) / PAR02 (74) / MAD01 / MUN01 are in transit for Oct 22 and LON01 (73) / LON02 (62) / GVA01 / ZRH01 for Oct 23;
  Asia/US later (SEL01 Oct 22, TYO01 Oct 23, SEL02 172 pcs Oct 26, NYC Oct 25...). So on Oct 21 PAR01/PAR02/LON02 are still at 0.
  Beige/navy do not substitute.
  Black Aurea requests also everywhere in Asia (SEL02 51 in W42, TYO01 23, OSA01 13...).
- VLOGO CARDIGAN size M: MIL01 at 0 (both black and navy) from Thu Oct 8; MIL02 navy M 0 from Oct 8, black M 0 from Oct 17;
  **ROM01 still has 3 navy M** and VEN01 1 black + 1 navy M (transfer opportunity). DC no M until ~Oct 30 (knit re-order wk44).
- IRIDIA powder pink (510): idol photo Oct 1 → Asia sells out in 1-3 days (SEL02/BUS01/CDU01/HKG01/OSA01/TYO01 at 0
  from Oct 2-6; SEL01/SHA01 kept only 1 piece, the display/damaged one). DC top-up landed Oct 8 but the first
  redistribution reached **EUROPE/US first: MIL01 +12 (Oct 10), PAR01 +12 (Oct 11), LON01 +12 (Oct 12), NYC01 +11 (Oct 14)**
  where pink barely sells, while Asia received only on Oct 16-19 (TYO01 15 on Oct 16, SEL01 ~19 on Oct 18, SEL02 27/BUS01 17/
  HKG01 10/SHA01 12 on Oct 18-19, OSA01 ~10 on Oct 20). CDU01 and BJS01 still 0 on Oct 21. Spill-over: IRIDIA black/off-white
  requests (HKG01 9 in W42, SEL01). DC black IRIDIA out Oct 6-20.
- VEL vest zipper slider defect: defect returns start Sep 28 at most stores (POS reason DEF), peak W40 (MIL01 16,
  PAR02 15, SHA01 15, TYO01 14, PAR01 14, LON01 13, NYC01 10, DXB01 7...). Units delivered from mid-August are affected.
- ASTRA (Couture capsule, launched Sep 24): strong in SHA01/BJS01/CDU01/HKG01 (ASTRA CAPE requests at SHA01), weak in
  EU/US (fit runs small, price perceived too high).
- ARTEM men's parka fits large → exchanges/returns reason SIZE (~10%), staff advise one size down.
- AMALIA chocolate brown requested in MIL/PAR/LON01/MAD; DC brown sizes 0,1,2 out from Sep 25 to Nov 10.
- ROM01: scaffolding + municipal pavement works in front of the entrance Sep 14 → Nov 6; sales ~-40/-50% vs budget.
- MAD01: picking error, navy NOVA received instead of black (Sep 26 and Oct 1 deliveries); black NOVA at 1 piece from
  ~Sep 20 until restock **Oct 11**. MAD01 door counter broken Oct 1-7 (zero visitors recorded).
- SEL01: IRIDIA replenishment held at Incheon customs (missing KC certificate), expected Oct 8, received **Oct 13**
  (logistics system shows that shipment as planned Oct 12 → arrived Oct 13). Competitor (Canadian outerwear brand) pop-up
  opposite SEL01 from Oct 15 with queues and giveaways.
- Cold snap Oct 12-19 (Munich first snow Wed Oct 14, snow to 1000 m in CH, max 2-6 °C) in MUN/BER/ZRH/STM/CPH/AMS/GVA;
  milder in Paris/London/Milan Oct 13-19. W42: BER01 +50% vs budget, MUN01 +26%, GVA01 +26%, CPH01 +11%.
- Golden Week Sep 30-Oct 8: Chinese tourists in MIL/PAR/LON02/TYO/OSA/SEL01/HKG/ZRH/VEN (CN share ~30% at MIL01/PAR);
  domestic version in SHA/BJS/CDU Oct 1-7.
- Japan: price increase +8% avg on carry-over items effective Nov 1, communicated to clients Oct 9 → pre-buying from Oct 12
  (TYO01 +22%, OSA01 +30% in W42). Unusually warm Sep 28-Oct 11 (27-29 °C), down jackets not moving.
- Strikes: Paris transport Tue Oct 13; Italian general strike Fri Oct 16. NYC02 POS outage Tue Oct 6 14:10-17:40, ~60% of
  that day's receipts posted with business date Oct 7. UNGA closures NYC01 Sep 21-26. TIFF Toronto Sep 10-20.
  Heat wave Beverly Hills Sep 8-12. MIA01 AC broken Sep 3-5. HKG01 typhoon: closed Sep 17, opened 15:00 Sep 18.
  Singapore GP Oct 9-11. BIFF Busan Oct 1-10. CPH01 staff shortage Sep 28-Oct 4 (open 11-17). LON01 private client
  evening Thu Oct 8 (45 VICs, ~25 purchases). Milan FW Sep 22-28, Paris FW Sep 29-Oct 7. VEN01 acqua alta Tue Oct 20
  (opened 12:00). CRT01 open Fri-Sun only in October; COU01 closed for season Sep 13 → Nov 26; STM01 closes Oct 19
  (Zwischensaison) until Dec 3. Double 11 presales from Oct 20 → CN stores softer, clients ask for Tmall price match.
  FW26 campaign US/UK from Sep 15: real effect ~+6%, agency claims +22%.
  SYD01: spring; forecast over-forecasts down jackets ~2.5x; customers want T-shirts/polos/light jackets.

## Cross-source planted distortions (assigned; each part documents its own)
AM weekly recaps:
- Roberto: "secondo me il tema Aurea nera è sovrastimato" (opinion, wrong: MIL01 lost ~45 requests in W41); ROM01 drop
  first blamed on "pochi americani / caldo" in W38, works said to end "fine ottobre" (true: Nov 6); W40 says MAD01 NOVA
  black issue "risolto" (true: restocked Oct 11); W41 says cardigan M out at MIL01 "da martedì" (true: Thursday Oct 8).
- Isabelle: suggests pushing beige/navy Aurea to Korean clients as substitute (data: does not convert); attributes PAR01
  W40 +41% to Fashion Week (mostly Golden Week Chinese tourists).
- Stefan: credits BER01 W42 +50% partly to new window display (cause: cold snap); "Astra läuft nicht – zu klein".
- Fiona: quotes agency "+22% uplift" from the campaign as fact; says CPH01 ran reduced hours "for two weeks" (one week).
- Lauren: skeptical of campaign uplift ("mid single digits at best" - correct); says NYC02 outage was "Monday" (it was Tue Oct 6).
- Suzuki: W40 calls pink IRIDIA "一時的なブーム" (wrong, demand persisted); blames slow down-jacket sales on fewer Chinese
  tourists (actually CN share was higher; real cause warm weather).
- Yoon: customs shipment "12일 입고" (true Oct 13); blames SEL01 W42 -18% only on competitor pop-up (also stock-outs).
- Zhao: over-generalises "ASTRA 全线卖爆" and asks for more; Double 11 worry.
HQ memos: VEL alert dated Oct 5 (after returns started Sep 28), states affected units "delivered from 1 September" (true:
mid-August) and "return rate below 3%" (true ~15%). FW26 launch brief: ASTRA "true to size" (runs small), ARTEM "regular fit"
(runs large), IRIDIA powder pink "limited regional colour, secondary" (became the hit). Golden Week staffing memo omits
LON02 and ZRH01 from the Mandarin-speaker support list. Cold-weather tips memo (Oct 13) says first snow in Munich
"expected around Oct 20" (it fell Oct 14).
