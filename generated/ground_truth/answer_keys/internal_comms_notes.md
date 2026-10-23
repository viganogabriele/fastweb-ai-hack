# Internal communications (non closing-email): answer key

Sources: `generated/sources/internal_comms/` (133 files incl. 10 placeholder JPGs).
Generators and hand-written content: `generator/internal_comms/` (`PLAN.md`, `common.py`, `am_weekly/`, `chats/`,
`visit_reports/`, `hq_memos/`, `voc/`). Rebuild with `.venv/bin/python generator/internal_comms/<part>/build.py`.
All facts were checked against `email_context/*.json`, `inventory/store_stock_daily`, `logistics/shipments_dc_to_store.jsonl`
and `traffic/door_counter_daily.csv`. Event codes below refer to `generator/events.py`. They never appear in the sources.

## 0. Key facts that internal data shows and these sources echo (with lag/noise)

| Topic | Truth from internal data |
|---|---|
| Black AUREA (E02) | 0 on hand: MIL01 ~Sep 24-25, PAR02 ~Sep 21, PAR01 Sep 28, LON02 ~Sep 25, LON01 Oct 8, SEL01 Oct 3, TYO01 Oct 16. DC re-order at CSG Oct 16. **Store deliveries: Italy Oct 21 (MIL01 62, MIL02 36, ROM01 40, VEN01 25, CRT01 8). PAR01 55 / PAR02 74 / MAD01 30 / MUN01 35 in transit for Oct 22. LON01 73 / LON02 62 / GVA01 / ZRH01 on Oct 23.** Asia/US Oct 22-29 (SEL02 172 on Oct 26). |
| VLOGO CARDIGAN M (E03) | MIL01 0 in both colours from Thu Oct 8. MIL02 navy M 0 from Oct 8, black M 0 from Oct 17. **ROM01 still holds 3 navy M on Oct 21** (the transfer was approved but never shipped). VEN01 1+1. No M shipped from DC through Oct 21. |
| IRIDIA pink (E06) | Asia at 0 from Oct 2-6. The DC top-up went **first to EU/US** (MIL01 +12 on Oct 10, PAR01 +12 on Oct 11, LON01 +12 on Oct 12, NYC01 +11 on Oct 14, ZRH01 +3 on Oct 16, AMS01/MIA/BHS/ASP/DXB small lots on Oct 17-18). It reached Asia late: TYO01 Oct 16, SEL01 Oct 18, SEL02/BUS01/HKG01/SHA01 Oct 18-19, TYO02/OSA01 Oct 20. **CDU01 and BJS01 got nothing.** By then demand had decayed: TYO01 sold ~3 of 15, SEL01 1 of 20 on arrival day, BUS01 0 on arrival day. That is lost sales from misallocation. |
| VEL defect (E08) | DEF returns from Sep 28, peak in W40. Units delivered from mid-August are affected. |
| ROM01 works (E04) | Sep 14 → Nov 6. Door counter ~150 normal → ~70-90. Sales -36 to -52 % vs budget. |
| MAD01 (E14b/E40) | Navy NOVA instead of black on Sep 26 and Oct 1. Black NOVA restocked **Sun Oct 11** (20 pcs). Door counter 0 on Oct 1-7, fixed Oct 8. |

## 1. Area-manager weekly recaps (`area_manager_weekly/`, 89 files: 79 .eml + DOCX attachments)

Each AM folder holds one recap per ISO week W36-W42, plus replies and noise. Recaps go out Sunday evening to Tuesday morning in local time. KPI figures are rounded from the KPI file (net sales, local currency) and are usually right to the nearest k.

| AM / folder | Files | Habits and noise |
|---|---|---|
| Roberto Galli `EMEA_Galli_Italia_Spagna` | 9 | Telegraphic, numbers first, signs "R.". W36 sent late (Mon Sep 7, OOO until Sep 4) and very short. Francesca replies on W39 and he answers from iPhone. |
| Isabelle Moreau `EMEA_Moreau_France_Geneve` | 9 | Long and polite. W39 has an HTML table (multipart). Francesca asks for beige-substitution numbers on W41 and Isabelle admits "3 ou 4" sold. |
| Stefan Wagner `EMEA_Wagner_DACH` | 10 | German with traffic-light ratings. DOCX attachments W37 and W40. Francesca asks for English on Sep 22. W39 is in English, then he goes back to German ("sorry, auf Deutsch"). W42 has a **correction email**. |
| Fiona McLeod `EMEA_McLeod_UK_North` | 9 | British, bullet points. Francesca challenges the campaign uplift and Fiona answers. |
| Omar Haddad `EMEA_Haddad_MiddleEast` | 6 | Short. **No W39 recap** (annual leave Sep 24 → Oct 4). W40 covers W39+W40. W41 is 2 lines from iPhone. |
| Lauren Mitchell `AMER_Mitchell_US_Canada` | 8 | Crisp US corporate. **W40+W41 combined** (sent Tue Oct 13). Mark asks about the +22 % and Lauren answers. |
| 鈴木 拓也 `APAC_Suzuki_Japan` | 9 | Keigo with 【】 headings. W38 late (holiday). Morita asks about the price-increase rush and Suzuki answers. |
| 윤성호 `APAC_Yoon_Korea` | 8 | W40 flagged [긴급]. 강민정 replies, asking for a 1-per-person limit. |
| 赵磊 `APAC_Zhao_MainlandChina` | 8 | Numbered 一二三 sections. DOCX 周报 attached W37/W39/W41. W40 sent late (Oct 8, after Golden Week). 周雪 replies to W42. |
| Vivian Lau `APAC_Lau_HK_TW` | 6 | Code-switching. W38 late (typhoon). **W41 missing**, combined into W41+W42. |
| Daniel Lim `APAC_Lim_SEA_Oceania` | 7 | W39 sent late (Thu Oct 1). W42 is 5 lines from phone and promises a full recap that never arrives. |

### Planted distortions, wrong info and opinions (correct reading in the right-hand column)

| File | Says | Truth |
|---|---|---|
| Galli W38 (Sep 21) | ROM01 -45 % blamed on "few Americans, 30 °C"; doubts the construction site explains it | The construction site (from Sep 14) is the cause: footfall halved |
| Galli W39 (Sep 27) | "Il Comune parla di fine lavori a fine ottobre" | Works end **Nov 6**. His own visit report (Sep 24) and the ROM01 chat quote the sign: 06/11 |
| Galli W39 | "il tema Aurea nera è un po' sovrastimato … non farei allocazioni straordinarie" | Opinion, wrong. MIL01 logged 27 / 22 / 45 / 30 unmet black-Maire requests in W39-W42. He partly retracts in W41 ("ammetto che i numeri sono alti") |
| Galli W40 (Oct 5) | MAD01 "questione Nova nera risolta" | A second wrong delivery came Oct 1. Black restocked only **Oct 11**. His W41 then says "finalmente arrivata sabato" (actually Sunday Oct 11) |
| Galli W41 | Cardigan M out at MIL01 "da martedì" | Sold out **Thursday Oct 8** (chat, Teams, stock file) |
| Galli W42 | Says he asked HQ to give black Aurea to ROM01 too | Explains the odd 40 pcs at ROM01 (halved traffic) while Paris waits. Also: "Iridia rosa a MIL01: venduti 2-3 su 13", consistent with stock |
| Moreau W39/W40 + PAR02 visit report | Push beige/navy Aurea as a substitute | Beige/navy do not convert (E02 note). Later admitted: 3-4 beige sold vs 100+ requests |
| Moreau W40 | PAR01 +41 % credited mainly to Paris Fashion Week | CN share jumped to ~31 % (Golden Week). Tourism, not the shows, drove most of the uplift |
| Wagner W42 | BER01 +50 % partly credited to the new snow-scene window | Cause is the cold snap (E05). Same week MUN01 +26 %, ZRH01 +41 % without window changes |
| Wagner W42 | ZRH01 "CHF 294 T" | Typo, corrected the same day to **CHF 249 T** (correction email) |
| Wagner W40 | ZRH01 was not on the Mandarin support list | True: the Golden Week memo omits ZRH01 |
| McLeod W39/W41 | Campaign "+22 % uplift" stated as fact | Agency attribution. Real effect ~+6 % (E15). Lauren (Americas) says "mid single digits at best", which is correct |
| McLeod W40 | CPH01 reduced hours "for two weeks" | One week (Sep 28 → Oct 4). Her W41 says back to normal hours |
| McLeod W42 | LON01 pink Iridia "sold 3" | Stock 12 → 6 by Oct 18, so about 6 sold. Minor understatement |
| Mitchell W40+41 | NYC02 POS outage "on Monday", "Monday understated, Tuesday overstated" | Outage was **Tue Oct 6** 14:10-17:40. Sales were posted on **Oct 7**. Her NYC02 visit report (Oct 8) has the correct date |
| Mitchell W40+41 | Toronto weakness blamed on "Canadian brands everywhere", mild weather | Unverified AM excuse. Nothing in the event data drives TOR01 |
| Suzuki W39 | OSA01 weak because of a "台風接近の予報" | Unverified excuse. No typhoon in the event data |
| Suzuki W40 | Pink IRIDIA "一時的なブーム … 2～3週間で落ち着く"; weak down sales blamed on "中国のお客様は想定より少なく" | Pink: demand was real, and the late top-up lost it. Chinese share actually rose to 34 % (TYO01). The real cause of weak down sales was 27-29 °C weather (E13w), which he mentions only in passing |
| Suzuki reply Oct 13 | Black Aurea at TYO01 "残り1～2点" | Correct (stock 1). Kept consistent with the LINE chat |
| Yoon W41 (Oct 12) | Customs-held shipment "12일 입고 예정" | Arrived **Oct 13**. The logistics file shows planned Oct 12 → actual Oct 13. The scenario's original planned date was Oct 8, and the Kakao chat still says "12일에 들어온대요" on Oct 8 |
| Yoon W42 | SEL01 -18 % blamed mostly on the competitor pop-up | The pop-up (from Oct 15) is real but partial. SEL01 also lost 12 black-Maire + 3 pink + 3 black-Ilvaro requests in W42 |
| Zhao W40/W41 | "ASTRA 全线卖爆"; asks to re-order | Strong in CN (E07), but "sold out everywhere" is over-generalised. ASTRA is a one-shot capsule. The useful lever is moving unsold EU/US stock to Asia, which Lauren and Stefan both offer |
| Lau W41+42 | TPE01 weakness put down to Double 11 and 週年慶 waiting | Plausible but unverified. TPE01 has no scenario event |
| Lim (all weeks) | SYD01 forecast keeps pushing down jackets; clients want tees/polos/light jackets | **Correct**: this is E16, forecast bias with northern seasonality |
| Vivian W36 | Taipei 101 corridor renovation | Invented local colour, unverifiable |

## 2. Chat exports (`chat_exports/`)

| File | Format | Span | Planted signals (timestamps local) |
|---|---|---|---|
| `Chat WhatsApp con MIL01 Team.txt` | Android IT, `<Media omessi>`, deleted message, 2 numbers added on Sep 30 (Mandarin temps) | Sep 1 → Oct 21 | Amalia brown 1/2 out (Sep 10). Korean girls asking for black Aurea from Sep 19; last one sold Sep 24. VEL zip returns Sep 28-29, logged as QUALITY before the alert, switched to DEF after Oct 5 (18 in the box). Pink Iridia asked for by CN/KR tourists Oct 2 (only a dirty display piece). **"chi ha una M del cardigan logo?" Oct 8 21:02**, ROM01 has 3 navy M, transfer requested Oct 9, still not arrived Oct 14/17. 12 pink Iridia arrived Oct 10 that nobody wants. ARTEM size down. Strike Oct 16. **62 black Aurea arrive Oct 21** with size split, 5 sold the same day. VICs: Al Mansouri (Oct 3, 14.6k), Bertolini (CL55468641) reserving Aurea 1. **Wrong info:** Oct 9 15:33 Sara says "Luca dice che arriva lunedì 12". Marco corrects it the same day (DC Oct 16, store later). |
| `WhatsApp Chat - ROM01 Condotti/_chat.txt` + 10 JPG placeholders | iOS IT with `<allegato: …PHOTO….jpg>` | Sep 1 → Oct 21 | Works announced Sep 13. Scaffolding photos Sep 14. Door counter "74 ingressi, di solito 150". Sign says end **6 novembre**, foreman rumour "fine ottobre" (Sep 22). Traffic police forbid the sandwich board. Astra 0. VEL returns. Golden Week tourists avoid the hoarding. Clienteling calls. **Cardigan M parcel for MIL01 approved Oct 12 but courier never picks it up (Oct 13, 14, 17, 20, 21)**. Strike Oct 16. **40 black Aurea arrive Oct 21** ("e che ce famo?"). |
| `Discussion WhatsApp avec Boutique Paris SH.txt` | Android FR, `<Médias omis>` | Aug 31 → Oct 21 (no Sundays, store closed) | Amalia brown 0-2 out with no re-order. Korean clients asking for black Aurea from Sep 19 (K-drama "Winter Letters"). Stock run-down to 0 on Sep 28. Astra "taille petit, trop cher". VEL from Sep 28. Fashion Week + Chinese groups. Pink Iridia frenzy Oct 2, 0 stock. Beige substitute fails (Oct 10). 12 unrequested pink arrive. Strike Tue Oct 13 (lines 1/8/9). **Oct 21 "Milan a reçu 62 Aurea noires… nous zéro"**, answer: PAR01 55 pcs arriving Thu Oct 22 (correct per logistics). |
| `Chat de WhatsApp con Serrano Equipo.txt` | Android ES | Sep 1 → Oct 21 | Navy NOVA instead of black Sep 26 and again Oct 1 (~20 navy). Door counter at 0 from Oct 1 (ticket INC0049817), fixed Oct 8. Black NOVA arrives Oct 11. Amalia brown 1. VEL DEF. Black Aurea (30) expected Oct 22. |
| `Teams_RetailOpsEMEA_Stock-and-Transfers_export_20261022.json` | Graph-API-like JSON, threads with `replies`, mentions, reactions, one SharePoint attachment | Sep 7 → Oct 21 | Amalia brown thread. **Black Aurea stock check Sep 21: DC empty until Oct 16.** Astra feedback ("brief says true to size" vs stores "small"). LON02 and ZRH01 missing from the Mandarin support list. MAD01 wrong-delivery ticket (black arrives "Sunday" Oct 11). **Elena counts VEL returns on Oct 2, before the formal alert**; Francesca pushes for faster instructions. **Cardigan M transfer ROM01→MIL01**: requested Oct 9, approved Oct 12, never picked up (ZTL courier issue). **Pink Iridia EU→APAC thread**: allocation was "the launch split nobody updated". Stores offer to release, Luca puts it "on hold" pending sign-off, still on hold Oct 21. **Black Aurea wave plan (Oct 16)**: Italy Oct 21, FR/ES/DE Oct 22, UK/CH/NL/DK Oct 23. Camille, Priya and Isabelle protest; ROM01's 40 pcs are questioned; Francesca's rebalancing request comes too late. Cold-snap requests (MUN/ZRH/CPH/BER beanies, gloves, heavy), STM01 → MUN/ZRH transfer. ZRH01 got 3 unrequested pink. Stock-lookup app counts in-transit as available (known bug). |
| `KakaoTalk_…_발렌티노 점장방.txt` | KakaoTalk PC export | Sep 1 → Oct 21 | Black Aurea / K-drama "겨울편지". ARTEM runs big (Sep 10). Chuseok closures (SEL02/BUS01 closed Sep 25). Astra launch queue. VEL zip from Sep 28 (alert late Oct 5). **Pink Iridia frenzy Oct 2** (Yoon Ha-eun / LUMIERE), sold out, waitlists 60+/41/22, resale on KREAM 390만 vs 272만 list. 1-per-person limit. **Customs hold at Incheon (KC certificate) Oct 8. Wrong info: "12일에 들어온대요"**; arrived Oct 13 with no pink. Oct 13 MD confirms pink split 20/27/17 for Oct 18-19 and admits Europe got it first. Competitor pop-up Oct 15 with queue and tote-bag giveaway. **Pink arrives Oct 18-19 but uptake is poor** ("이미 샀거나", resale price < 300). Black Aurea due Oct 26 (SEL02 large). |
| `[LINE] 銀座・表参道・心斎橋 店長会.txt` | LINE export, tab-separated, CRLF | Sep 1 → Oct 21 | Heat (34 °C Sep, 29 °C Oct 5): down not moving. Silver Week. Astra queue. VEL from Sep 28, alert Oct 5. MD price-increase memo Sep 30 (confidential until Oct 9). Pink sold out Oct 2-4. ARTEM one size down. **Rumour "+15 %" (Oct 9, 中村) corrected to ~8 %.** Holiday rush Oct 12. **Nightly black-Maire counts: TYO01 2→1→0 (last one Oct 16)**, TYO02 8→3. Pink: TYO01 gets 15 on Oct 16 but only 3 taken. TYO02 6 / OSA01 10 on Oct 20, "1着だけ". "Did Europe get pink first?" Black Aurea ETA TYO01 Oct 23, others Oct 27 (matches logistics). |
| `微信群聊_华区门店管理群_20261022.txt` | WeChat third-party export | Sep 1 → Oct 21 | ARTEM 偏大. **ASTRA launch strong** (SHA01 14 pcs day one, CAPE white M/L 断码, waitlists). Astra is a one-shot capsule: the MD tries an EU→Asia transfer. VEL 拉链 from Sep 28. Golden Week domestic traffic. Pink Iridia (小红书, resale +5000) sold out. **Wrong info: "听说粉色10月15号到？"** (Oct 8), corrected by the MD. Oct 15 pink split: SHA01 only, **BJS01/CDU01 nothing**; "欧洲门店上周就到了货，卖不动". SHA01 gets 11 (+1 old = 12), clients already bought via 代购. Double 11 memo Oct 19; price-match questions Oct 20-21 (VIC threat to buy online). Black Aurea ETA SHA01 Oct 25, BJS/CDU Oct 29. |

## 3. Store visit reports (`store_visit_reports/`, 12 files, 6 templates)

| File | Template | Planted content / traps |
|---|---|---|
| `2026-09-24_ROM01_visita_RGalli.docx` | EMEA v3 (weights, 1-5) | Scaffolding hides windows. Sign: works end **06/11/2026**. AM estimates footfall **-30 %**, team says -50 % (counter: ~-50 %). His own W39 email later says "fine ottobre". Action to reduce ROM01 allocation, owner Luca, due "n/a", never done (ROM01 got 40 black Aurea). |
| `2026-10-02_MAD01_visita_RGalli.docx` | v3 | ~20 navy vs 3 black NOVA, ticket. Door counter 0, conversion to be ignored. VEL returns logged as QUALITY. |
| `2026-10-06_PAR02_visite_IMoreau.docx` | v3 (FR) | 64-name black-Maire waitlist, mostly tourists. Beige-substitute action (wrong lever). Amalia brown 0-2 missing. VEL 9 returns, no procedure yet. |
| `2026-09-30_LON02_visit_FMcLeod.docx` | v3 (EN), lazily filled (clienteling n/a, so the weighted score excludes it) | Not on the Mandarin list. Black Aurea gone. 2 VEL returns. |
| `2026-10-15_MUN01_Filialbesuch_SWagner.pdf` | v3 (DE), DOCX→PDF | First snow Wed Oct 14. NOVA black 3/4, beanies and gloves out. STM01 → MUN01 transfer proposal. ASTRA "zu klein, zu teuer". ARTEM one size down. |
| `2026-10-01_MIL01_VM_check_SMarchetti.pdf` | VM OK/KO checklist (EN) | Compliance 82 % (9/11). Black Aurea slot empty since ~Sep 19, filled with navy/beige (VM objects). Pink only 1 piece. Astra "great visibility, low conversion". VEL box in the back. |
| `2026-10-14_TYO01_店舗巡回レポート_鈴木.pdf` | JP ◎○△× | Price-increase rush. Black Aurea effectively out (1 left). Pink 0 since Oct 4, 40+ waitlist, arrival "16日". Comment repeats the "一時的なもの" view of pink (wrong). Early October 28 °C. |
| `2026-10-16_SEL01_매장방문보고서_윤성호.docx` | KR, score /100 (75) | Pop-up queue of 70-80 people. Pink: 1 soiled display piece, 90+ waitlist. **Customs shipment arrived 10/13** (contradicts his W41 "12일"). Black Aurea out since ~Oct 3. VEL ~15. |
| `2026-10-09_SHA01_巡店报告_赵磊.docx` | CN, 10-point | Astra strong, CAPE white out. Pink sold out ~Oct 3. VEL ~15, logged wrongly before Oct 5. ARTEM 偏大. |
| `2026-10-08_NYC02_Store_Walk_LMitchell.pdf` | Americas Meets/Below grid | **POS outage correctly dated Tue 10/6 2:10-5:40pm**, ~60 % of tickets keyed 10/7 (contradicts her own "Monday" email). Campaign "a bit up, nothing dramatic". 1 Astra Cape since launch. VEL 8. |
| `2026-09-29_SYD01_visit_DLim.docx` | short EN, x/5 | 140+ down jackets in stock, clients want tees/polos/light jackets. Forecast email lists down as top sellers (E16). Proposal to send heavy back to TKO. |
| `2026-09-22_HKG01_visit_report_VLau.pdf` | reportlab PDF, /100 | Typhoon closure Sep 17, reopened 15:00 Sep 18. Wet beanie/cap cartons written off. Astra prep. |

Scoring scales are deliberately inconsistent: weighted % (v3), compliance %, ◎○△×, /100, 10-point average, Meets/Below, x/5. They are not comparable across reports.

## 4. HQ memos (`hq_memos/`)

| File | Date / author | Wrong info / contradictions |
|---|---|---|
| `FW26_Launch_Brief_…_v2.pdf` | Aug 27, Merchandising (Bassi/Longo) | **ASTRA "true to size, do not suggest sizing down"**: it runs small (stores, VOC). **ARTEM "Fit is regular, offer usual size"**: it runs large (~10 % SIZE returns). **IRIDIA pink "limited regional colour… secondary… do not build outreach… do not open waitlists"**: it became the idol hit. Amalia brown "no re-order planned". |
| `2026-10-05_QUALITY_ALERT_QA-26-017_TIB.eml` + `QA-26-017_…pdf` | **Mon Oct 5 17:42**, Elena Rinaldi | Issued a week after returns began (Sep 28). Says affected units were "delivered from 1 September" (**truth: from mid-August**) and "return rate below 3 %" (**truth ~15 %**). Tells stores to use code DEF; before this, stores used QUALITY, which skews the POS reason codes for Sep 28-Oct 5. |
| `2026-10-09_RE_QUALITY_ALERT_…_update.eml` | Oct 9 | Corrects the scope to **mid-August**. Still no rate correction. Says "do not stop selling". |
| `2026-09-30_価格改定のお知らせ_11月1日_継続品番.docx` | Sep 30, MD Japan 山口 | +8 % average on carry-over, effective Nov 1, client communication from Oct 9. **Table inconsistency: NOVA ¥305,000 → ¥335,000 is +9.8 % but labelled +8 %.** The others are 7.7-8.1 %. FW26 newness and ASTRA are excluded. |
| `2026-09-22_Golden_Week_staffing_payments_taxfree.eml` | Sep 22, Matteo Colombo | Period stated as Sep 30 → Oct 8, "peak 1-7". **LON02 and ZRH01 are omitted** from the Mandarin support list, though both had big CN traffic (LON02 CN 27 %, ZRH01 21 % in W40). Teams thread and Fiona/Stefan complain. "No extra allocation planned." |
| `2026-10-02_ARNEB_sizing_note.eml` | Oct 2, Davide Longo | Denies a fit problem ("pattern unchanged… keep advising usual size"). Contradicted by stores and by HQ's own Oct 13 memo. |
| `2026-10-13_Cold_weather_selling_tips.eml` | **Tue Oct 13** (cold began Oct 12) | Says first Munich snow "expected around 20 October" (**it fell Wed Oct 14**). Recommends showing beige/off-white where black Aurea is missing (wrong lever). Now advises ARTEM "one size down" (contradicts the brief and the Oct 2 note). "No extra allocation of heavy down before end of October." |
| `2026-10-19_双十一期间门店价格政策执行说明.docx` | Oct 19, Greater China retail ops | No price match, script, VIC escalation, log price-match requests daily. Presale starts Oct 20 20:00. Consistent with E22. |

## 5. Voice of customer (`voice_of_customer/`)

**`clienteling_log_export_2026-09-01_2026-10-21.csv`** (UTF-8 BOM, 144 hand-written rows + 5 duplicates = 149 data rows)

- Columns: log_id, store, sa_name, client_id, tier, channel, contact_date, contact_time, direction, reason, product_mentioned, outcome, notes, phone_masked.
- Notes are hand-written in it/fr/en/de/es/ja/ko/zh/yue. Several client_ids are real POS customers, so the log can be joined to sales: e.g. CL55468641 "Bertolini" MIL01, CL31059483 "Mme de Vaucresson" PAR01, CL61585279 LON01, CL57891896 TYO01, CL28913290 SEL01, CL73619844 SHA01, CL11064687 HKG01.
- Signals:
  - black Aurea waitlists (MIL01, PAR01/PAR02, LON01/LON02, MUN01, TOR01, SEL01, BJS01; mostly tourists who leave)
  - pink Iridia waitlists Oct 2-6 in SEL/BUS/TYO/SHA/BJS/CDU/HKG/SIN/PAR/MIL, and **cancellations when stock finally arrives Oct 16-20** ("already bought in Seoul/代购/KREAM")
  - cardigan M (MIL01/MIL02 Oct 8-17)
  - Amalia brown 1/2 (MIL01, PAR01 VIC since Sep 11 still unserved Oct 20, PAR02, LON01, MAD01)
  - Japan price-increase outreach from Oct 9 and resulting purchases Oct 12-14
  - LON01 private evening invites and purchases Oct 8
  - VEL after-sales from Sep 28 (one "gilet comprato 3/9")
  - ARTEM exchanges one size down
  - ASTRA: EU "small/expensive" vs SHA01 "比想象中合身"
  - ROM01 clients thinking the store was closed
  - MAD01 black NOVA
  - Double 11 price-match (SHA01 VIC escalated Oct 21)
  - SYD01 asking for polos and light jackets in spring
  - NYC02 manual slips during the outage
- Noise:
  - store column mixes codes, names, short codes (`MI-MN`, `PAR-SH`, `Harrods`, `청담`, `銀座`) and legacy numeric `1001` (= MIL01)
  - ~6 % of dates in dd/mm/yyyy
  - **5 rows duplicated** (sync glitch, same log_id)
  - empty notes and missing client_ids
  - masked phones
  - **LON02 SA Priya Raman's row of 2026-10-15 is logged under store LON01**
  - **SEL01 row 2026-10-18 (박민수, CL28913290) has outcome "no answer" while the note says the client came in immediately** (the stock file confirms a pink sale that day)

**`instore_feedback_survey_export_20261022.xlsx`** (sheets `responses`, `README`)

- 93 hand-written responses + 3 double-submit duplicates with consecutive ids (96 rows).
- Availability scores (q1) are 1-2 where stock-outs hit: black Aurea MIL01/PAR01/PAR02/LON02/TYO01, pink Iridia SEL/TYO/SHA/CDU/HKG/SIN, NOVA black MAD01, cardigan M MIL01, beanies CPH01, Nova 3 MUN01.
- Comments carry the other signals: ROM01 scaffolding, VEL zips, Astra small (MUN01/PAR01), Japan heat and price-rush crowds, cold-snap happy buyers (MUN/AMS/ZRH), NYC02 paper receipts on Oct 6, NYC01 UNGA, BHS01 104 °F, MIA01 hot store (AC), Double 11 (SHA01/BJS01), DXB01 transliterated Arabic.
- Artefacts: "test test" and "테스트" rows (MIL01 Sep 15, SEL01 Oct 1), emoji-only, an NPS 0 with no answers, one timestamp without time (MIL01 2026-09-29), skipped items (None).
- README says SEL01/TYO01 tablets were only active from Oct 1, but there are earlier SHA01/SYD01 rows. That is a minor inconsistency, worded as "others partial".

**OCR cards**

- `ocr_comment_cards_ROM01_2026-10.txt`: scaffolding, "polvere", VEL, strike day. OCR errors: `2O26`, `gentilissirna`, `po1vere`, `gi1et`, `ottirno`, `[illegible]`, a blank page.
- `ocr_cards_PAR01_sept_oct.txt`: UTF-8 mojibake (`TrÃ¨s`, broken Hangul), `srnall`, `rernboursement`, `13/1O`. Content: black Aurea, Astra small, VEL, strike, Amalia brown VIC complaint.
- `OCR_店頭アンケート_心斎橋_202610.txt`: heat, ARTEM size down, price rush, pink "もう他で買ってしまいました", `1O月`, 判読不能.

## 6. Cross-source contradictions worth testing

1. **ROM01 end of works**: sign / visit report / chat say Nov 6. Galli W39 email and a chat rumour say end of October. Visit report traffic -30 % vs counter ~-50 %.
2. **NYC02 outage day**: Lauren's email says Monday. Her visit report and the VOC row say Tue Oct 6 (truth).
3. **SEL01 customs**: Kakao "12일" and Yoon W41 "12일 예정" vs visit report and Yoon W42 "13일" (truth Oct 13; scenario originally planned Oct 8).
4. **Cardigan M date**: Galli "da martedì" vs chat, Teams and stock showing Thu Oct 8. The ROM01→MIL01 transfer is approved in Teams but never shipped (ROM01 still 3 on Oct 21).
5. **Black Aurea allocation**: Italy first (ROM01 40 with half traffic) while PAR/LON wait 1-2 more days. Galli admits pushing ROM01. Isabelle and Camille protest. Data confirms the dates.
6. **Pink Iridia**: launch brief "secondary colour" → Asian frenzy → top-up to EU first (MIL01/PAR01/LON01 sit on 12 each, ZRH01 3 unrequested) → Asia late, CDU01/BJS01 nothing → poor uptake. Suzuki "temporary boom" is wrong about demand but right that it faded by the time stock came.
7. **VEL**: stores saw returns from Sep 28. The formal alert came Oct 5 with a wrong scope and rate, corrected on Oct 9 (scope only). Reason codes QUALITY vs DEF are mixed before Oct 5.
8. **ASTRA fit**: brief "true to size" vs EU/US "runs small" vs CN "fits well". Best action: move EU/US stock to CN/HK (proposed by Lauren, Stefan, Sun Yiwen; not executed).
9. **ARTEM fit**: brief "regular" → Oct 2 note "pattern unchanged" → Oct 13 memo "one size down". Stores, VOC and the POS SIZE returns agree it runs large.
10. **Campaign uplift**: agency +22 % (Fiona) vs stores "a bit up" and Lauren "mid single digits" (truth ~+6 %).
11. **Golden Week memo** omits LON02 and ZRH01, both of which had high CN share.
12. **Cold snap**: the HQ memo predicts Munich snow around Oct 20; it fell Oct 14 (Wagner, MUN01 report, Teams). The memo arrived a day after the cold began.
13. **Japan price table**: NOVA +9.8 % labelled +8 %. A store rumour says +15 %.
