# emails_ko — Korean store closing emails (SEL01, SEL02, BUS01): answer key

Sources: `generated/sources/store_emails/{SEL01,SEL02,BUS01}/*.eml` (163 files).
Bodies hand-authored in `generator/emails_ko/bodies/<STORE>.py`; wrapped by `generator/emails_ko/build_eml.py`;
checks in `generator/emails_ko/check.py`. Per-file index (with the business date each email reports):
`generated/ground_truth/emails_ko_index.csv`. All times KST (+09:00).

| store | files | closings | extras |
|---|---|---|---|
| SEL01 청담 flagship | 60 | 51 | 1 dup, 1 correction, 2 fwd, 5 replies (AM ↔ store) |
| SEL02 현대 압구정본점 | 52 | 49 (one is a Sat+Sun recap) | 1 correction, 1 misdirected email, 1 AM reply |
| BUS01 신세계 센텀시티 | 51 | 48 (one is a Sat+Sun recap) | 1 OOO auto-reply, 1 fwd, 1 AM reply |

## Writers / personas

- **SEL01**: 김지현 (store manager) sends a numbered form "1) 매출 2) 입점/구매 3) 특이사항 4) 요청사항" with amounts in 천원,
  a signature and a KR/EN disclaimer from desktop Outlook on weekdays. On weekends she writes from her iPhone (shorter, no disclaimer).
  박민수 (assistant manager) is telegraphic, uses "~함/~임", amounts in M (58.3M), arrows, Konglish (컨버전, 셀아웃); mostly Mondays plus some Fridays.
  오하늘 (senior SA, invented) is casual and uses emoji, ㅠㅠ, ㅎㅎ and "iPhone에서 보냄"; she covers Sundays and holidays.
- **SEL02**: 이수진 (manager) uses a fixed "■ 매출 / ■ 객수 / ■ 특이사항" form and writes in department-store vocabulary
  (정기세일, 사은행사, 자스민 VIP, 보안팀, 공용 창고, 휴점). 최동욱 (assistant manager) is telegraphic, gives amounts in 만원, writes "객"
  for receipts and once reports the department-store POS gross figure. 강예린 (SA, invented) wrote 2 casual emails.
- **BUS01**: 정은비 (manager) has a warm ~요 tone, uses "▶" bullets, a little Busan dialect ("억수로") and some emoji.
  한승우 (assistant manager) is short and focused on menswear (ARTEM sizing), and signs off with "Samsung Galaxy 스마트폰에서 보냈습니다".
  배소연 (SA, invented) writes from the shared store mailbox on an old PC, so those mails are **euc-kr encoded** (9/15, 10/15). She also sent a CSV-only email.
- Area manager 윤성호 replies from his phone. He is out of office 9/24–9/28 (auto-reply in the BUS01 folder).

Metric vocabulary differs by store. "객수" = receipts at SEL02 (with "입점" = door count). SEL01 says "입점/구매(건)". BUS01 says "건".
Nobody reports units. Amounts are rounded net sales and match the KPI file, except where listed below.

## Main planted signals (what the emails say → what is true)

### IRIDIA powder pink (510) craze — "윤하은 패딩", "인디핑크", "핑크 크롭"
- Before the craze there are sporadic pink requests from 9/5 to 9/28 (all three stores). The launch quantity was tiny:
  SEL01 had only sizes 3 and 4, BUS01 had 3 units and sold out on 9/30, SEL02 had a single 00.
- **Oct 2**: the first wave of phone calls arrives at all three stores (SEL01 says 30+ calls). SEL02 sold its last 00 that afternoon.
- **Oct 3–4 (SEL01)**: a queue before opening, a record 318M KRW day and 1,125 visitors. The paper waitlist starts.
  The 10/5 reply gives the waitlist by size: 00:6 / 0:14 / 1:11 / 2:9 / 3:3 / 4:1 = **44**.
  Resale price on 크림 is above 4,000,000 KRW (retail 2,720,000).
- SEL02 waitlist: 23 on 10/4, 26 on 10/5 (by size in the email), "30+" on 10/6. BUS01: 11 on 10/6, 16 on 10/19.
- Substitution: ARIA pink is offered but rarely converts. IRIDIA black and off-white sell as stand-ins
  (SEL01 IRIDIA black x9 on 10/7, SEL02 off-white x7 on 10/13). IRIDIA black then hits zero in small sizes.
- **Arrival**: SEL01 on 10/18 (20 pcs), SEL02 and BUS01 on 10/19 (27 and 17 pcs). Size splits in the emails match the stock files.
- **Trap: holds versus available stock.** From 10/18 the stock files show 19–27 pink units on hand, while POS shows only
  0–2 sales a day. The emails explain why. SEL01: 12 holds on 10/19 and 11 on 10/21, so about 7–8 are free.
  SEL02: 14 holds on 10/20, about 10 free. BUS01: 5 holds, 11 free. Pickups lag (customers come at the weekend).
  Part of the demand has genuinely decayed: on 10/19, of the 44 waitlist contacts at SEL01, 6 had already bought on resale,
  7 cancelled and 15 did not answer. Resale fell to about 3.3M by 10/20, and BUS01 reports "문의도 0" on 10/21.
  Correct reading: there was a large unmet demand from 10/2 to about 10/18. After that the residual demand is smaller.
  Low sales after arrival are partly pickup lag, not a lack of demand.

### SEL01 customs hold (Incheon, missing KC certificate)
- 10/6: merchandising tells the store the top-up arrives on 10/8. On 10/8 a 315 pcs box arrives **without IRIDIA pink**.
  Logistics says part of the stock is held at Incheon customs because the KC document is missing.
- 10/9: the forwarded logistics email (Kelvin Ng, in English) gives an ETA of 12–13 Oct and says the held consignment "incl. IRIDIA top-up".
- 10/12 (sent next morning): "세관 물량은 오늘 들어온다고 함". **10/13: a 443 pcs delivery arrives.**
- **Trap**: in the 10/13 closing, SA 오하늘 writes "핑크도 들어왔어요". That is wrong: the pink items were ARIA 510 (7 pcs)
  and a VLOGO BEANIE 510. She read the "510" on the box label as IRIDIA. 김지현's correction email
  (`20261014_1048_SEL01_corr.eml`) fixes this. The real IRIDIA 510 arrives only on **10/18** (planned 10/15, carrier delay).
- **Cross-source discrepancy**: `shipments_dc_to_store.jsonl` shows the 10/8 shipment delivered on time and the
  10/13 one only 1 day late. The customs hold is not visible as a long delay there. The emails are the only source for the hold.
  Effective IRIDIA pink availability at SEL01: none from 10/4 (only size 4 left) to 10/18.

### AUREA black (domestic, drama effect)
- From 9/22 at SEL01, 9/19 at BUS01 and 9/27 at SEL02, the emails tie black AUREA demand to a weekend drama
  in which a (fictional) actress, 한소율, wears it.
- Stock-outs: SEL01 sizes 0 and 2 from 10/3 (Golden Week Chinese shoppers bought 11 that day), size 1 from 10/7,
  then only size 4 is left. SEL02 size 1 from 10/6, 0–2 from 10/13, all sizes from 10/17. BUS01 size 2 from 10/10, 0–2 from 10/15.
- Peak at SEL02: **20+ requests on 10/17** and 15+ on 10/18; the waitlist grows from 34 to 40+.
  The AM replies that the DC restock of 10/16 went to Europe first. No black AUREA reached Korea by 10/21.
  This is consistent with the stock files. Beige and navy partly substitute (SEL02 beige x6 on 10/9).

### VEL zipper defect
- First defective return: SEL01 9/28, SEL02 9/28, BUS01 9/28. The symptom is described as "슬라이더 헛돎" (the slider spins and does not catch).
  Customers bought the vests in August.
- SEL01 cumulative count: "누적 7건" on 10/1 is correct. "15건 넘었습니다" on 10/14 is correct (true count 16).
  SEL01 asks whether to stop selling. The AM says to keep selling but check every zipper before sale, and to code returns DEF.
- SEL02 says "누적 6건" on 10/8. The true DEF count is 7, so the store slightly undercounts.
- **Trap (BUS01 10/14)**: a VEL zipper return was coded QUALITY in POS instead of DEF, and the email says so explicitly.
  Counting only reason=DEF undercounts the defect.

### ARTEM fits large
- Repeated in all three stores (SEL01 9/10, 9/16, 9/22, 9/24; SEL02 9/11; BUS01 9/10, 9/13, 9/14, 10/7).
  Staff advise one size down, and there are exchanges 4→3, 5→4 and so on.

### Chuseok (Sep 24–26) and department-store rules
- SEL02 and BUS01 were **closed 9/25** because the department store was closed; both announce it on 9/24.
  SEL02 also lists the closure in its 9/30 HTML month-end table.
- SEL01 (street flagship) stayed open on 9/25 and made **+47%**. The email credits department stores being closed.
- SEL02: "명품 세일 제외" — the department-store fall sale (from 9/18) only applies the gift-voucher promotion to the brand.
  Security asked the store not to queue in front of it (10/4). From 10/19 the store does pickup by appointment only, with no walk-in sale.
- The pre-holiday dip (SEL02 9/23 at 39% and 9/24 at 59%) is explained as shoppers going to the gift-set floor.

### Chinese Golden Week (SEL01)
- The CN share reported for 9/30–10/8 is 30–40%+. Visitors are 싼커 (individual travellers who come via Xiaohongshu), not 유커 groups.
  Tax-refund questions; staff ask for a Chinese-speaking SA.
- 10/9: "중국 손님 확 줄었어요 (14%)". This matches customer_mix.

### Competitor pop-up (SEL01, from 10/15)
- Described as "캐나다 아웃도어 패딩 브랜드 (C사)" across the street, with a queue and giveaways. Photos are attached to the 10/15 email.
  Staff say it runs until the 2nd week of November.
- The 10/17 email states "입점 250명 정도 빠졌습니다" vs the previous Saturday (778 → 524, correct).
  The 10/18 reply estimates traffic −10~15% and "패딩 매출 30% 이상" down. **That down-jacket figure is a felt estimate and is overstated.**
  The store itself notes that the previous week was inflated by the pink and AUREA rush. The modelled effect is about −12% traffic
  and −10% on heavy outerwear.

### BIFF (BUS01, Oct 1–10)
- The opening on 10/1 is next door (영화의전당) and that day makes +37%. Afterwards traffic is up (visitors 169–218 vs about 100 in September)
  but **conversion is down** ("구경만"). There are foreign guests (JP 10% on 10/4, US 8% on 10/8).
  A forwarded stylist sponsorship request asks for IRIDIA pink; the AM refuses.

### Other logistics
- BUS01's 9/28 delivery was late because of the holiday backlog and arrived 10/1 (+3 days, matches shipments).
  SEL02's 9/28 delivery arrived 9/29 (+1 day).

## Traps / noise list

| file / date | what | correct reading |
|---|---|---|
| SEL01 `20261003_2219_SEL01_dup.eml` | duplicate of the 22:16 email (new Message-ID) | count once |
| SEL01 10/10 email, subject "[청담] 마감보고 10/09(토)" | wrong date in subject; body is Saturday 10/10 | business date 2026-10-10 |
| SEL01 `20261013_0921_SEL01.eml` | 10/12 closing sent the next morning | business date 2026-10-12 |
| SEL01 10/13 closing | "핑크도 들어왔어요" — wrong (ARIA/beanie 510) | corrected by `20261014_1048_SEL01_corr.eml`; IRIDIA 510 arrives 10/18 |
| SEL01 10/18 reply | down-jacket sales "-30% 이상" | felt estimate, overstated |
| SEL01 9/15 | **missing** (no email) | KPI 75.5M / 74.7M, uneventful |
| SEL02 10/3 (최동욱) | "백화점 마감 매출 1억 6,912만 (113%)" = department-store POS gross | KPI net 158,326,000 (106%) |
| SEL02 10/4 (최동욱) | "7,597만" typo, no % | corrected next morning (`_corr`): 1억 7,597만 = 175,970,000 (115%) |
| SEL02 `20261006_1612_SEL02_misc.eml` | email meant for the Hyundai floor MD (박영훈 과장) sent to the ops list | not a closing; the 10/6 closing apologises for it |
| SEL02 9/12 | no own email; covered by the Sat+Sun recap sent 9/13 | weekend total 184.0M / 235.3M correct |
| SEL02 9/9 | **missing**; 9/10 email says "5,600만대로 목표 근처" | KPI 56.25M / 58.6M |
| SEL02 10/8 | "VEL 누적 6건" | true DEF returns 7 |
| SEL02 9/30 | HTML part with the September month-end table (21.42억 / 23.04억 = 93.0%, LY +18.1%) | matches KPI |
| BUS01 9/8, 9/29 | **missing**; the 9/9 and 9/30 emails apologise | KPI 9/8 15.5M, 9/29 25.6M |
| BUS01 10/10 | no own email; covered by the Sat+Sun recap sent 10/11 (excuse: "POS 정산 오류" — no data issue exists) | numbers correct |
| BUS01 `20260924_2036_BUS01_ooo.eml` | AM auto-reply (Auto-Submitted header) | ignore as signal |
| BUS01 9/15, 10/15 | body charset **euc-kr**, 8-bit | decode properly |
| BUS01 10/17 | body only says "첨부 참조"; content in a **cp949** CSV (`BUS01_마감일보_1017.csv`, text/csv without charset) | 75,650,000 / 81,849,500, 28 receipts, 230 visitors |
| BUS01 10/14 | VEL zipper return coded QUALITY in POS | it is a zipper defect (DEF) |
| BUS01 10/19 | "Iridia 2 사이즈 변심 반품 (블랙)" | the colour is the writer's claim; POS has no colour on the return line |

## Things that are NOT in these emails (by design)
- No KC/customs mention at SEL02 or BUS01 beyond hearsay about SEL01 ("청담은 세관에서 막혔다고").
- No units, UPT or conversion % at SEL02 or BUS01. SEL01 sometimes gives conversion or ATV.
- No mention of ASTRA performance in Korea, except one or two single requests.
