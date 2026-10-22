# Store closing emails, Chinese group (emails_zh): answer key

Stores: **SHA01** (Shanghai Plaza 66, Simplified Chinese), **BJS01** (Beijing SKP, Simplified Chinese), **CDU01**
(Chengdu Taikoo Li, Simplified Chinese), **HKG01** (Hong Kong Canton Road, written Cantonese mixed with English,
Traditional characters), **TPE01** (Taipei 101, Traditional Chinese, Taiwanese Mandarin).

Output: `generated/sources/store_emails/<STORE>/<YYYYMMDD>_<HHMM>_<STORE>[suffix].eml`. All Date headers are +0800.
The file name timestamp is the **send** time, not the business date. Some emails are sent the next morning, and some
cover two business days.

Generator: `generator/emails_zh/` contains the following.
- `sha01_p1.py`, `sha01_p2.py` and the matching files for the other stores: every body is hand-authored as a literal string.
- `bodies_<STORE>.py`: personas, default To/Cc, and the assembled list.
- `build.py`: wraps the bodies into .eml files.
- `check.py`: day coverage and repeated-phrase check.
- `digest.py` and `kpi.py`: authoring aids that read `email_context`.

Rebuild with `.venv/bin/python generator/emails_zh/build.py`.

| Store | Files | Closing emails | Business days with no email of their own | Extras |
|---|---|---|---|---|
| SHA01 | 56 | 50 | 09-07 (none at all), 09-15 (reported in the 09-16 mail) | re1/re2, ooo, corr, dup, fwd |
| BJS01 | 54 | 49 | 09-04 (none), 09-19 (in a weekend recap sent 09-20), 10-13 (one line in the 10-14 mail) | wrong/wrong2, re1/re2, dup |
| CDU01 | 55 | 50 | 09-08 (none), 09-12 (in a weekend recap sent 09-13) | vm/vm2, re1/re2, dup |
| HKG01 | 54 | 50 (+ a 09-17 "store closed" note) | 09-15 (none), 10-03 (in the 10-04 mail) | re1/re2, fwd, dup |
| TPE01 | 53 | 49 | 09-07 (none), 10-06 (none), 09-22 (in the 09-23 mail) | re1/re2, corr, dup |

Distribution lists: CN stores send to `retail-ops-china@` with Cc 赵磊 Zhao Lei (`lei.zhao@`). HK/TW stores send to
`retail-ops-hktw@` with Cc Vivian Lau. Some emails also Cc `merch-planning-apac@`-style addresses, `aftersales-china@`
or `logistics-apac@`. Invented supporting people: merch planner CN 孙怡雯 (`yiwen.sun@`), merch HK/TW Jason Tsang
(`jason.tsang@`).

## General conventions and decoding hints

- **Gross vs net (most important numeric trap).** The KPI file (`store_daily_kpi.csv`) is net of VAT.
  - SHA01's store manager 王静 and TPE01's store manager 林怡君 report **VAT-inclusive (含稅/含税)** sales: CN ×1.13, TW ×1.05.
    They label it only occasionally.
  - 王静 also reports the target incl. VAT, so her achievement % is still correct.
  - 林怡君 reports the target **net** (as in the KPI file), so her **achievement % is inflated by about 5%**. Example: 10/15 she
    reports 133%, the true figure is 126%. The TPE01 file `20261016_0905_TPE01_corr.eml` states this explicitly.
  - SHA01's ASM 陈浩, BJS01, CDU01 (except the trap below), HKG01 and TPE01's ASM 吳承恩 report net figures that match the
    KPI file (rounded).
- Amount formats: "20.8w", "20.96万", "¥111,300", "HK$104.8k", "31.2萬", "NT$542,000", "59.7萬".
- Sizes use Moncler numbering. The SA nicknames and colours used in the bodies:
  - Colours: 黑 = black, 藏青/深藍/navy = navy, 米白/白 = off-white, 米色 = beige, 粉色/粉紅 = powder pink,
    咖色/巧克力色/啡色 = chocolate brown, 灰 = grey melange.
  - Products: 斗篷/cape = POLARIS CAPE, oversize/大廓形 = POLARIS OVERSIZED, 头套/頭套/balaclava = POLARIS BALACLAVA,
    Tib马甲/背心 = TIB, 开衫/開襟衫 = LOGO CARDIGAN, Tricot开衫 = TRICOT PADDED CARDIGAN, 卫衣/帽T/hoodie = LOGO HOODIE,
    圆领卫衣 = CREWNECK SWEATSHIRT, 高领 = WOOL TURTLENECK, 毛线帽/毛帽/beanie = LOGO BEANIE, 腰包 = LEGERE BELT BAG,
    GTX = TRAILGRIP GTX, Trailgrip 女款 = TRAILGRIP W.
- "有人问/没货/無貨/missed/冇貨" lines are the store's view of unmet requests. They are a partial, slightly noisy sample
  of `email_context.unmet_requests`, sometimes with lag, and sometimes requests that appear in no data at all
  (e.g. BJS01 09-28, "Maire black 2 asked").
- Local background colour that is NOT in the scenario and should not drive forecasts:
  - SHA01: a 30-minute mall power cut on 09-15; a "typhoon fringe rain" remark.
  - BJS01: an SKP member day on 09-23 (explains 40 receipts and the low ATV); a Beijing cold morning (6 °C) on 10-14
    and ski-opening talk (崇礼).
  - CDU01: a Taikoo Li pop-up on 09-05; a local blogger effect on BADY black on 09-27.
  - TPE01: a Taipei 101 VIP member day on 09-26 (explains +56%); Taiwan National Day fireworks on 10-10.

## Cross-store signals

| Signal (scenario) | Where it shows in this group | Notes |
|---|---|---|
| Golden Week domestic travel, Oct 1–7 (CN) | SHA01 10-01..10-07 (traffic 1,211 on 10-03, "拍照的比买的多", GW recap on 10-07); BJS01 10-02..10-07 (外地游客 from 山西/河北/东北, GW recap on 10-07); CDU01 10-01..10-07 (traffic about 2× normal, recap on 10-07) | Conversion drops at SHA01/BJS01 (5–8%). CDU01 conversion stays about 9%. |
| Golden Week outbound to HK | HKG01 09-30..10-08: mainland share 60–72%, queue at the door, 193% achievement on 10-02, "國慶假期完咗" on 10-09 | |
| POLARIS launch on Sep 24 | SHA01 09-22..09-26 (37 pre-bookings, queue of about 40 people, 14 units on day 1, XS cape requests, OVERSIZED black L sold out about 10-06); BJS01 09-24/25 (queue of about 20, cape black ×7 on 09-25); CDU01 09-24..10-11 (no queue, 13 units on 10-11 = best day) | **HKG01 is weak**: 0 units on 09-24, local clients say "too big, too expensive", only mainland clients buy (16 units in the whole window). TPE01 has only a small allocation and is not a theme. |
| ILVARO powder pink craze (Yoon Ha-eun 尹夏恩 / LUMIERE, from Oct 2) | SHA01 from 10-02 (waitlist 11 → 14), BJS01 from 10-02 (waitlist 9 + deposits), CDU01 from 10-02 (sold out on 10-02 morning), HKG01 from 10-02 (black ILVARO ×7 spill-over on the same day), TPE01 mild ("沒有韓國那麼誇張") | **Replenishment arrived only at SHA01 (10-18: 11 pcs), HKG01 (10-19: 10 pcs) and TPE01 (10-19: 5 pcs)**. BJS01 and CDU01 got none (CDU01 10-19: "上海到了我们没有分到"). After arrival, sales are close to zero and waitlist clients no longer come (SHA01 10-19/10-21, HKG01 10-19..10-21, TPE01 10-21). The craze had decayed; the stock arrived about 2 weeks late. |
| ILVARO spill-over to black/off-white | SHA01 10-06 (black ×5 "也是同款系列"), HKG01 10-02 (black ×7), CDU01 10-04 (black ×6), BJS01 10-06/10-10; TPE01 10-18 (off-white ×3) | HKG01 then runs out of black 0/1/2 and keeps reporting black requests to 10-21. |
| MAIRE black national stock-out (DC out Sep 12 → Oct 16) | All five: sizes 0/1/2 at zero from about early October. BJS01 is the strongest, then SHA01. Several stores "heard the DC received stock on 10-16" but **no store receives any black MAIRE by 10-21** (SHA01 10-19 and BJS01 10-19 chase logistics) | Transfer requests between stores fail: BJS01 asks SHA01 and CDU01 (SHA01 10-09; BJS01 10-09 csv mail). |
| TIB zipper-slider defect returns (from ~Sep 28) | SHA01 from 09-29 (six on 10-03, VIC complaint forwarded 10-19); BJS01 from 09-29 (most returns: 17); CDU01 from 09-28; HKG01 from 09-28; TPE01 from 09-28 (12, Dcard/PTT threats) | BJS01 has an **early precursor on 09-22** ("Tib 4码 质量退，拉链拉起来很涩"), coded QUALITY in POS. Stores repeatedly ask aftersales whether to pull TIB; no answer arrives in the window. TIB black keeps selling everywhere. |
| ARNEB fits large | SHA01 09-08 (first return), 09-10 ("建议小一码"), 09-25; BJS01 09-12/13; CDU01 09-07, 09-21, 09-22; HKG01 09-12 (Arneb black ×5 "要落一個碼"); TPE01 09-14/19 (clients normally size 3 need 2, small sizes missing) | Request for more small sizes: SHA01 09-12, 09-25; TPE01 09-19. |
| Double 11 presales from Oct 20 | SHA01 10-20/21 (Tmall comparison, price-match request, a MAYA return "天猫预售有赠品"); BJS01 10-20 (保价 question), 10-21; CDU01 10-20 (rain plus Tmall, 9 receipts) | HKG01 10-20 mentions mainland clients waiting for Tmall. TPE01 10-20 has one online question only. |
| HK typhoon signal 8 | HKG01 09-16 (warning, high importance), 09-17 (closed note sent 19:35), 09-18 (opened 15:00, HK$41k) | TPE01 09-17 mentions stranded HK tourists shopping in Taipei (cross-signal). |
| Japan price increase on Nov 1 | TPE01 10-15: Japanese tourists 24% of the mix, "日本11月要漲價，趁來台灣先買" | Cross-signal for the Japan stores. |
| AMBRINE chocolate brown, small sizes | CDU01 09-06, 09-11, 09-12, 10-15, 10-17 (and the 10-16 Q&A); BJS01 10-17 (xlsx note "Ambrine咖色2码") | SHA01 does not carry brown. |

## Store details and traps

### SHA01: Shanghai Plaza 66 (56 files)

Writers:
- **王静** (store manager): a fixed form `【SHA01 恒隆 每日营业报告】` with 重点事项 / 需要支持; iPhone; **figures incl. VAT ×1.13**.
- **陈浩** (assistant manager): telegraphic, English jargon, **net** figures ("w"); Outlook.
- **周婷婷 Tina** (senior SA): writes 10-03, 10-06 and 10-14; WeChat style with emoji and pasted group-chat lines.
- The store mailbox sends one email (09-19), which only says 见附件 and attaches an xlsx closing form whose figures are incl. VAT.

Traps:
1. `20261002_2314_SHA01.eml` reports "今日销售：10.24万" against a target of 93.62万 and an achievement of 124%, which is
   internally inconsistent. `20261003_0847_SHA01_corr.eml` corrects it to **102.4万**. That corrected figure is the NET
   value (KPI 1,024,200), whereas 王静 normally reports incl. VAT (115.7万 would have been her usual figure).
2. The gross/net mix between writers: 王静's numbers are about 13% above the KPI file; 陈浩's and Tina's match it.
3. The Golden Week summary inside `20261007_2244_SHA01.eml` is labelled "含税", but the totals (731万 sales, 562万
   target, 130%) are **net** sums. The label is wrong; the numbers match the KPI file.
4. `20261008_2239_SHA01.eml` has the subject "10/7 营业日报", copied from the previous day. The body is 10/8 data.
5. `20261017_2314_SHA01_dup.eml` is an exact duplicate of the 23:12 send. Count 10/17 once.
6. `20261001_2249_SHA01_ooo.eml` is Zhao Lei's out-of-office auto-reply (Oct 1–7). It is not store content.
7. `20260905_2258_SHA01.eml` says "Maya 藏青今天6件". The real top seller was **MAYA black ×6**; the colour is wrong.
8. **Ambiguous pink**: `20261012_2246_SHA01.eml` says "粉色短款今天卖了4件💗 夏恩效应还在". The items sold were
   **BADY powder pink ×4**, not ILVARO. ILVARO pink was still out of stock that day (00 and 2 requested).
9. The Q&A with Zhao Lei (`_re1` 09-25 09:14, `_re2` 09-25 11:02) gives a Polaris size split. The answer "20多件" ≈ 14
   (09-24) + morning sales of 09-25. It is broadly right; the per-size split is qualitative.
10. On 09-15 the store had no email of its own; 陈浩 reports 09-15 and 09-16 together in `20260916_2252_SHA01.eml`.
    09-07 has no email at all.
11. `20261019_1526_SHA01_fwd.eml` forwards a VIC's WeChat complaint (TIB zipper broke twice; threatens a 小红书 post)
    with an IMG attachment. It is a qualitative escalation, not a business-day report.
12. ILVARO pink stock commentary is accurate:
    - Sizes left before the craze: 1/1/3/4 (09-20 and 10-02 emails).
    - 1×2 sold on 10-04 and size 3 on 10-05, leaving only size 4.
    - 11 units arrived on 10-18.
    - 10-19: of 14 waitlist calls only 1 client bought.

### BJS01: Beijing SKP (54 files)

Writers:
- **刘洋** (store manager): pasted WeChat-group report `【SKP MMDD 日报】` with emoticons such as [抱拳] and [强]; net figures in "w".
- **张敏** (assistant manager): narrative, Foxmail; **bodies encoded GB18030** (16 emails). Parsers must honour the charset.
- **马骁** (SA): 09-11, 09-28, 10-10; homophone typos (在/再).
- The store mailbox sends 10-09 (a **GBK-encoded CSV** attachment) and 10-17 (an xlsx with only "见附件").

Traps:
1. **Wrong subject date**:
   - `20260924_2251_BJS01.eml` has the subject "【SKP 0923 日报】" but the body header says 0924 (Polaris day 1).
   - `20261015_2241_BJS01.eml` has **both** subject and body header "1014", but it is the 10-15 report (delivery of 514
     units, 64.5w = KPI 10-15). A real 10-14 report also exists: `20261014_2306_BJS01.eml` by 张敏, 79.1万. Take the
     business date from the send date and the content, not from the header.
2. **Deposits counted as sales**:
   - `20261005_2239_BJS01.eml` reports 58.7w / 134%. KPI net is 56.29万 / 128%. The extra ~2.4w is pink-ILVARO
     deposits (定金) and is unlabelled.
   - `20261006_2244_BJS01.eml` reports "66.0w（含定金）" / 146%. KPI is 63.59万 / 141%.
   - Deposits are not net sales.
3. **Wrong recipients**: `20260930_1612_BJS01_wrong.eml` is the internal Golden Week staff rota sent to retail-ops by
   mistake. `20260930_1621_BJS01_wrong2.eml` asks recipients to ignore it. It contains no business data.
4. `20261017_2315_BJS01.eml` (xlsx form): conversion is shown as **6.1%**, but 61/673 = **9.1%**. All other cells match the KPI file.
5. **Inflated lost-sales estimate**: Zhao Lei asks in `_re1` (10-12 09:21) and 张敏 answers in `_re2` (10-12 11:43):
   "四五十个" clients asked for black MAIRE since National Day. The facts give about 20 black-MAIRE requests between
   10-02 and 10-11 (33 in the whole window), concentrated in size 2 early on, then sizes 0/1. The answer double-counts
   repeat visitors.
6. **TIB "fully pulled" contradiction**: `20261007_2308_BJS01.eml` says all TIB were pulled from the floor from 10-07.
   TIB still sells afterwards (e.g. TIB black ×4 on 10-18; 10-15 returns). Zhao Lei notices this in `_re1` and 张敏
   explains ("后仓预留的客人来取"). The ban was not applied consistently, so TIB sales after 10-07 are real.
7. `20261018_2300_BJS01_dup.eml` duplicates the 22:59 send.
8. Missing days:
   - 09-04 has no email.
   - 09-19 is covered by the weekend recap `20260920_2312_BJS01.eml`. Its line "周末目标两天是130万左右" is approximate;
     the true figure is 122.8万.
   - 10-13 is only one line in `20261014_2306_BJS01.eml` ("昨天销售53万左右，达成105%", KPI 53.0万 / 105%).
9. BJS01 has no ILVARO pink restock. The 10-07 email mentions a pink size 3 that was returned and is back in stock.
10. The early TIB "拉链涩" QUALITY return on 09-22 precedes the official defect window (see the cross-store table).

### CDU01: Chengdu Taikoo Li (55 files)

Writers:
- **李娜** (store manager): chatty, Sichuan flavour (巴适/安逸/遭不住), KPI written inside prose; net figures in 万.
- **杨帆** (assistant manager): numbered lists, figures to the yuan, signs "Fan".
- **何雨桐** (SA): 09-21 and 10-10, unsure tone.

Traps:
1. `20260916_0912_CDU01.eml` is the **09-15** report sent the next morning ("昨晚网断了").
2. The weekend recap `20260913_2315_CDU01.eml` covers 09-12 and 09-13. There is no separate Saturday email.
3. 09-08 (the worst day, 6.8万 / 29%) has **no email**. Silence does not mean nothing happened.
4. **Waitlist inflation**: in `20261007_2252_CDU01.eml` 李娜 says pink ILVARO "登记了20多个客人". Walk-in pink requests by
   10-07 total about 12 (16 in the whole window). She also counts WeChat inquiries.
5. **Wrong recipients**: `20261008_2106_CDU01_vm.eml` is a VM window-photo email with three JPGs sent to retail-ops instead
   of the VM team. `20261008_2114_CDU01_vm2.eml` says "发错了". The VM mail also states that the pink ILVARO slot in the
   window was filled with BADY pink.
6. **Gross figure in the ASM's report**: `20261013_2241_CDU01.eml` (杨帆) reports "¥478,000 / 123.3%". That is the
   **incl.-VAT** value (KPI net 423,000; 109%). His other reports are net.
7. **AMBRINE brown Q&A**: Zhao Lei asks in `20261016_0934_CDU01_re1.eml` and 杨帆 answers in `20261016_1118_CDU01_re2.eml`.
   - He says sizes 0, 2 and 4 are missing and that clients ask mostly for 0 and 1.
   - Stock on 10-15 was actually 00:2, **0:2**, 1:2, 2:0, 3:1, 4:0, so the real gaps are sizes **2 and 4**.
   - Brown requests in the facts were size 1 (×2, September), 4 (09-12) and 2 (10-15, 10-17). Size 0 was never requested.
   - "6-7 clients" overstates it; there were 4 requests by 10-16 and 5 in the window.
8. `20261017_2305_CDU01_dup.eml` duplicates the 23:04 send.
9. `20261003_2336_CDU01.eml` contains a self-correction about an ARNEB exchange size. The exchange went 2 → 1 (POS shows size 1).
10. CDU01 sells its last two pink ILVARO units (00 and 2) on the morning of 10-02 and receives no restock through 10-21.

### HKG01: Hong Kong Canton Road (54 files)

Writers:
- **Karen Chan 陳嘉欣** (store manager): Cantonese–English mix; several Outlook **HTML** emails with a KPI table
  (multipart/alternative with a text version) on 09-02, 09-12, 09-25, 10-01, 10-17 and the 10-17 dup; a legal disclaimer
  footer on some.
- **Ming Wong** (assistant manager): short English with Cantonese, iPhone.
- **Sammi Lee** (SA): 09-27 and 10-16, pasted WhatsApp lines with timestamps.

Traps:
1. **Typhoon reopening time**:
   - 09-17 has the closed note `20260917_1935_HKG01.eml` (sales 0). It is not an open business day.
   - `20260918_2221_HKG01.eml` (Ming) says signal 8 was cancelled at 12:40 and the store **opened at 3pm**.
   - `20260920_2301_HKG01.eml` (Karen) says "前日 2點幾已經開返舖". This is wrong; the correct time is 15:00 (the day is
     modelled as 35% open).
2. **k vs 萬**: `20261010_2302_HKG01.eml` (Ming) reports "Sales HK$50.1k, ach 118%". The true figure is **HK$501.2k**
   (118% is correct). Nobody corrects it.
3. **Pink waitlist and transfer Q&A**: Vivian asks in `20261008_1006_HKG01_re1.eml` and Karen answers in
   `20261008_1237_HKG01_re2.eml`.
   - "Waitlist 15 clients" is inflated; walk-in pink requests by 10-07 were about 7.
   - "TPE 都冇粉紅" is **wrong**: TPE01 held pink ILVARO 00 and 2 until 10-16, then size 2 until the 10-19 restock.
     A transfer was possible.
4. **Wrong product name**: `20261008_2237_HKG01.eml` says "3 clients asked for 粉紅 Bady size 0/1/2". These were pink
   **ILVARO** requests. HKG01 does not carry BADY in powder pink.
5. `20261009_1542_HKG01_fwd.eml` forwards a Shanghai VIC's email (in Simplified Chinese) reserving pink ILVARO size 1 for
   a 10-24 visit. She is served after the 10-19 restock (mentioned in `20261019_2253_HKG01.eml`).
6. `20261017_2311_HKG01_dup.eml` duplicates the 23:09 HTML send.
7. Missing days: 09-15 has no email. 10-03 (a very busy Golden Week Saturday) is reported inside
   `20261004_2331_HKG01.eml` together with 10-04.
8. The delivery planned for 09-21 arrived **2 days late on 09-23** with the Polaris launch stock.
   `20260921_2233_HKG01.eml`, `20260922_2229_HKG01.eml` and `20260923_2247_HKG01.eml` cover it.
9. Restock picture:
   - 10 pink ILVARO units arrived on 10-19 and **none sold** by 10-21.
   - Black ILVARO was **not** restocked although it had the stronger unmet demand (0/1/2 out). The store explicitly asks
     to move pink elsewhere and to replenish black (`20261021_2244_HKG01.eml`).
10. 10-13 TIB return is "change mind, not zip". 10-04 TIB return is "gift, not zip". Not every TIB return is the defect.

### TPE01: Taipei 101 (53 files)

Writers:
- **林怡君 Jenny Lin** (store manager): friendly Taiwanese style (～, 喔, XD); **figures incl. 5% VAT** with achievement
  computed against the **net** budget (inflated about 5%); labels 含稅 only on 09-20 and 10-15.
- **吳承恩** (assistant manager): concise NT$ lines, **net** figures.
- **王筱涵 Vicky** (SA): 09-10 and 10-11, emoticons, figures incl. VAT, labelled.

Traps:
1. The gross/net mix, made explicit by `20261016_0905_TPE01_corr.eml`: "102.6萬是含稅，未稅 NT$976,900，達成率126%不是133%".
2. **Ambiguous pink**: `20261001_2212_TPE01.eml` says "粉紅色那個今天賣了兩個" right after the idol photo. The items were
   **LOGO BEANIE powder pink ×2**, not ILVARO. TPE01's only pink ILVARO sales in October are 10-03 (size 0) and 10-16 (size 00).
   BADY pink sold ×3 on 10-14..10-16 (`20261014_2211_TPE01.eml`, `20261016_2213_TPE01.eml`).
3. **TIB count understated**: Vivian asks in `20261005_0943_TPE01_re1.eml` and Jenny answers "7件" in
   `20261005_1316_TPE01_re2.eml`. The facts give **9** DEF returns by 10-04 and 12 in the window. The 10-21 email says
   "大概10件左右". The store also quarantines 4 stiff units, but TIB keeps selling.
4. **Wrong subject date**: `20261013_2207_TPE01.eml` has the subject "10/12" but the body is 10/13.
5. `20261017_2241_TPE01_dup.eml` duplicates the 22:39 send.
6. Missing days: 09-07 and 10-06 have no email. 09-22 is reported inside `20260923_2214_TPE01.eml` ("昨天忘了寄").
7. The pink ILVARO craze is **mild** at TPE01 (about 3 requests: 09-18 pre-craze, 10-17 ×2). The 5 pink units received on
   10-19 had not sold by 10-21. The off-white ILVARO sells better locally (10-18).

## Quick reconciliation tips for evaluators

- Use the KPI file as the truth for sales. Map each email to a business date using its content, not the subject. Apply:
  ÷1.13 for 王静 (SHA01); ÷1.05 for 林怡君 and Vicky (TPE01); remove deposits on BJS01 10-05 and 10-06; read CDU01 10-13
  as gross; read HKG01 10-10 "50.1k" as 501k; and count each duplicate once.
- The unmet-demand signals worth extracting from this group, in rough order of strength:
  1. MAIRE black (BJS01 > SHA01 > CDU01 > HKG01 > TPE01).
  2. ILVARO pink (SHA01, BJS01, CDU01, HKG01, from 10-02; a short-lived spike).
  3. ILVARO black (HKG01 especially, mid-October).
  4. POLARIS small sizes (SHA01: cape XS/S).
  5. AMBRINE brown size 2 (CDU01).
  6. ARNEB small sizes (all stores).
