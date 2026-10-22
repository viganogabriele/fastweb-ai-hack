# Store closing emails - group `emails_en_intl` (English-speaking / international stores)

Stores: LON01, LON02, AMS01, CPH01, DXB01, SIN01, SYD01. Window 2026-08-31 -> 2026-10-21.
Output: `generated/sources/store_emails/<STORE>/*.eml` (368 files). Index of every file (kind, business date(s)
covered): `generated/ground_truth/emails_en_intl_index.csv`.
Generator: `generator/emails_en_intl/build.py` (wraps the hand-written bodies in `generator/emails_en_intl/stores/*.py`
into .eml; `check.py` = coverage + repeated-sentence check; `digest.py` = authoring aid).

General conventions
- Bodies were written by hand from `email_context/<STORE>.json`. Sales figures are mostly the KPI net sales rounded to
  0.1k in local currency (GBP/EUR/DKK/AED/SGD/AUD). Exceptions are listed below as traps.
- Unmet requests in the context file are reported most days, in staff wording (sizes in Moncler numbering,
  "tee" = LOGO T-SHIRT, "crew" = CREWNECK SWEATSHIRT, "tricot" = TRICOT PADDED CARDIGAN, "cardigan" = LOGO CARDIGAN,
  "grey" = grey melange, "pink" = powder pink 510, "brown/chocolate" = 23R).
- Emails sent after midnight or the next morning belong to the previous business day (see index `business_date`).
- Signatures, disclaimers and the DXB01 form header repeat on purpose (store habit). No other long sentence repeats.
- Encoding: emails with a corporate disclaimer (LON01 Olivia, DXB01) are quoted-printable, phone/webmail ones 8bit.
- Weather remarks were checked against `external_weather_truth.csv`; they are consistent except where noted.

## Missing / combined days (true gaps in the closing stream)

| Store | Day without own closing | Where the numbers appear |
|---|---|---|
| LON01 | Sun 06/09 | Mon 07/09 mail (28.3k) |
| LON01 | Tue 29/09 | combined in Wed 30/09 mail (27.7k) |
| LON02 | Sun 13/09 | never reported (KPI: 11.7k, -50%) |
| LON02 | Mon 12/10 | in Tue 13/10 mail by James (13.5k, 7 black Maire asks) |
| AMS01 | Mon 07/09 | Tue 08/09 mail ("EUR 4.2 only") |
| AMS01 | Sun 04/10 | Mon 05/10 mail (10.1k) |
| CPH01 | Tue 22/09 | Wed 23/09 mail (61.9k) |
| CPH01 | Fri 09/10 | Sat 10/10 mail (91.2k, delivery 85) |
| CPH01 | Sat 19/09 | sent Sun 20/09 10:14 (store closed Sundays) |
| DXB01 | Wed 16/09 | Thu 17/09 mail (86.2k) |
| DXB01 | Mon 05/10 | Tue 06/10 form (45.4k) |
| SIN01 | Sun 06/09 | Mon 07/09 mail |
| SIN01 | Wed 23/09 | Thu 24/09 mail |
| SYD01 | Sun 20/09 | Mon 21/09 mail |
| SYD01 | Sun 18/10 | Mon 19/10 mail |

CPH01 is closed on Sundays (no email expected). Duplicate sends (`_dup`, identical body, 2-8 min later):
LON01 03/10, LON02 17/10, DXB01 17/10 (second one after midnight, dated 18/10), SIN01 11/10, SYD01 17/10.

## LON01 - London New Bond Street (GBP)

Writers: Olivia Hartley (SM; tidy British, "Hi all", KPI line footfall/conv/ATV/UPT, Outlook + disclaimer, weekdays),
Daniel Okafor (AM; lowercase telegraphic bullets, "pls", "fyi", iPhone, Thu + Sat), Harriet Lowe (senior SA /
clienteling; chatty, "x", Sundays). Area manager Fiona McLeod, planner Tom Brennan.

Signals
- No tax-free in UK: tourists (US, Saudi, Chinese) walk out to buy in Paris/Milan (03/09, 18/09, 10/10).
- FW26 campaign (E15): go-live 15/09; a few clients come in "with the campaign picture" (19/09). Staff see little
  in-store impact -> consistent with the real ~+6% (not the agency +22%).
- Private client evening Thu 08/10 (E18): 45 confirmed, 41 came; "around 28 clients purchased" (event note says ~25).
- Black MAIRE: LON01 is not in the Korean-tourist list but black Maire sells out on 07-08/10 (sizes 0/1/2 at zero
  until 21/10). Waitlist grows 9 -> 12 -> 14 names (08/10, 09/10, 16/10). Planner (17/10) says DC stock landed
  16/10 but priority goes to Paris/Milan/Harrods; deliveries 19/10 still contain none -> unmet demand persists.
- Client forward (12/10 `_fwd`): VIC asking Maire black size 1 by 24/10.
- AMBRINE chocolate brown requested (03/10 "3 clients", 21/10). LON01 is assorted ONLY in AMBRINE black, so these
  requests never appear as unmet_requests in the context data -> invisible lost demand, only visible in emails.
- POLARIS (E07b): many try-ons, "zero sold", fits small, price (24/09, 25/09, 15/10).
- ARNEB fits large (E42): staff brief "size down" from 10-11/09; returns 01/10, 05/10.
- TIB zip defect (E08): first 3-4 DEF returns 28/09, 10 by 30/09; Olivia pulls TIB stock to check zips
  (4 of 11 faulty, "taken off sale") - stock files still show them on hand.
- Cold echo (E05b): 13/10 "proper cold", 14/10 +50%, record weekend 17-18/10 (Sat 113.5k in heavy rain, Sun 104.3k).
- Key-size gaps: Logo tee black S, Logo cardigan navy M (from 08/10), Trailgrip GTX 44, Karakorum black 5.

Traps
- 08/10 closing reports **£252.5k inc VAT** = gross. Net (KPI/flash) is 210.4k. Clarified in the reply thread
  (09/10 Fiona `_re1`, Dan `_re2`).
- 25/09 first mail says **£45.5k** (typo); `_re1` 14 min later corrects to 54.5k (KPI 54.5k).
- Mail sent 15/10 has subject **"close 14/10"** but contains 15/10 data (71.7k).
- 17/10 Daniel suspects the door counter double counted (982) - speculation, KPI visitors = 982.
- 21/09 `_ooo`: Fiona's out-of-office auto reply (no content).
- 07/09 "Did get 4 Maya black" - not verifiable from the email context.

## LON02 - Harrods concession (GBP)

Writers: Priya Raman (SM; CAPS section headers SALES/TRAFFIC/MISSED, HTML table on 4 Mondays), James Whitcombe
(AM; wordy, wry, Fri-Sun), Mei Lin Chen (Mandarin-speaking SA, Sundays 04/10 and 18/10, simple English).

Signals
- Harrods context: goods-in/loading bay delays (04/09), Brompton Road window for the campaign (14-15/09, photos
  IMG_4471/4472 attached), Harrods staffing plan / badge list, Harrods floor manager comments.
- E02 black MAIRE / Korean tourists: first noticed Sat 19/09 (5x size 1, 2x size 2, drama screenshot), then a daily
  count from 28/09 at Fiona's request. Beige/navy do not convert. Counts match unmet_requests except the traps below.
  Peak 13 requests on 27/09 and 08/10. "Korean groups seem to have tailed off" 15/10 (event ends 14/10).
- DC said black Maire back 16/10, but the 16/10 delivery has none and requests continue to 19/10.
- Golden Week (E01): 30/09 Chinese 46%, guided groups with no time to try on, tax-free complaints; 08/10 47%.
- Middle East clients (KW/SA/QA/AE) throughout; skiing purchases (Ecrins for Courchevel, Valbourg).
- AMBRINE brown (assorted here) requested several times (08/09, 23/09, 28/09, 03/10, 10/10, 14/10, 15/10) and 3 sold
  on 15/09.
- POLARIS: only capes; XL returned "tight on shoulders" (06/10), size S asked 14/10, 4 capes sold 17/10.
- TIB DEF returns from 29/09. LOGO CARDIGAN black/navy M out from 15-16/10, 4 requests on 19/10.

Traps
- 24/09: Priya writes "black Maire in 2 (x2)" - the context says **MAIRE navy** 2 x2 (+ black 0 x1). Colour error.
- 03/10: James counts **10** black Maire requests ("one more who didn't give a size"); unmet data = 9.
- 17/10: "Black Maire: 8" includes a walk-in for size 4 that is not in the data (unmet = 7).
- 17/10: Polaris capes "all to one Qatari family" - customer mix that day has no QA share (staff impression).
- 21/09 HTML table uses decimal commas ("11,0k"); 19/10 table rounds var% differently from the text (-53 vs -52).
- 08/09 claims a Flammette black 2 transfer from Bond Street - not verifiable.
- 01/10 13:12 "Rota w/c 5th Oct" sent to the ops list by mistake, retracted 3 min later (`_re1`). Not a closing.
- 09/10 "pink beanies ... K-pop video" - LON02 is not an ILVARO-pink store; staff gossip.

## AMS01 - Amsterdam P.C. Hooftstraat (EUR)

Writers: Sanne de Vries (SM; Dutch-English "Hoi all", "Groetjes", amounts as `EUR 8.465` = dot thousands separator),
Ruben Bakker (AM; lowercase, `15,5k` = decimal comma, Dutch words "slecht", "bonnen", "bezoekers", "koud", "ff"),
Lotte Jansen (SA; emojis, "gezellig", "Doei", Sundays).

Signals
- Warm September, summer basics (white tees/polos) sell; white tee M/L run out 19/09.
- ARNEB size-down advice from 09-10/09 (return 09/09, 02/10).
- Black Maire: size 0 out from 14/09, 0/1/2 out from 26/09, still none on 21/10; Fiona (16/10 `_re1`) says AMS gets
  stock after Paris/Milan/Harrods.
- POLARIS sells a little (light blue oversized 26/09 and 02/10, capes 29/09 and 05/10) - weak but not zero.
- TIB DEF returns 30/09 (2) and 01/10.
- Pink ILVARO asked once (03/10, Chinese girl with K-pop photo).
- Cold snap (E05) 12-19/10: staff ask heavy outerwear top-up on 09/10 (forecast), Peyre black 2 repeatedly asked,
  best weekend 16-18/10 (Sun 37.5k). 15/10 is weak despite the cold ("strange") - real data noise.
- Delivery planned 15/10 arrived 17/10 (2 days late), no black Maire in it.
- ADE (Amsterdam Dance Event) mentioned 17/10 as extra city traffic - local colour, not in the event list.

Traps
- Number formats: "EUR 22.300" = 22,300 euros, "15,5k" = 15.5k. "EUR 4.2" (08/09) = 4.2k.
- AMBRINE brown: Sanne says "we don't have the brown at all / not in our assortment" (09/10, 20/10). **Wrong**:
  AMS01 is assorted in AMBRINE 23R; it is simply out of stock in the requested sizes (requests are in unmet data).
- 19/10 18:53 `_re1`: Ruben's message in Dutch about the back-door key, meant for Sanne, sent to the ops list.
  No business content. Sanne apologises in the 20/10 mail.
- 0924 Polaris arrival quantities ("1 cape + 2 oversized") are staff recollection, not checked.

## CPH01 - Copenhagen Østergade (DKK, closed Sundays)

Writers: Mette Kjær (SM; polite Danish-English, "Hej all", "kr." with dot thousands, "eventually" used as Danish
"eventuelt" = possibly), Anders Holm (AM; terse, "øv", "lørdag"), Freja Lund (SA, 29/09 and 21/10).

Signals
- Chronic key-size gaps in heavy outerwear (Maya, Montcla, Ecrins, Montgenevre black 3 asked 3 times).
- Staff shortage (E37): announced 21/09, separate mail to Fiona (`ops_request`) proposing 11-17 hours from 28/09,
  approved 22/09 (`_re1`). Reduced hours 28/09 -> Sat 03/10 (emails sent ~17:30 instead of ~18:45); back to 10-18
  on Mon 05/10 with an agency hire.
- TIB DEF return 30/09. ARNEB size-down from 10/09, exchanges 23/09.
- POLARIS does OK here (balaclavas, white capes) - Norwegian customers.
- Cold snap (E05): 12/10 Mette asks planning for outerwear; 15/10 +103% (Maire navy x6), 17/10 black beanies x8,
  19/10 +68%; 20/10 drop when it warms up.

Traps
- 01/09: Mette first writes budget 56.100 then corrects herself in the same mail to 52.000 (KPI 52.0k).
- 15/10 mail says **246.000 kr.**; corrected in 16/10 mail to **264.000 kr.** (KPI 264.0k).
- Saturday 19/09 closing sent Sunday 20/09 10:14 (business date 19/09).
- 21/09 staffing mail names (Line, Kasper, Ida) are invented colour; event note says "2 sick + 1 resigned".

## DXB01 - Dubai Mall Fashion Avenue (AED)

Writers: Joel Santos (AM, Filipino; fixed "DAILY SALES REPORT - DXB01" form, "Kindly", "PFA", "Noted with thanks"),
Rania Khoury (SM, Lebanese; narrative "Dear All"), Priyanka Menon (senior SA, Indian English; "PFB", "kindly do the
needful", "revert", numbered lists). Area manager Omar Haddad. All with the Moncler ME disclaimer.

Signals
- Season start: residents back from summer (02/09), tourists from India/Saudi/Russia; buying outerwear for trips
  (Moscow, Almaty, London, Switzerland, ski in Gudauri/Courchevel/Niseko) while it is ~40 C outside.
- Saudi National Day 23/09 + long weekend -> record Sat 26/09.
- Late deliveries: planned 30/08 arrived 01/09 (2 days), planned 06/09 arrived 09/09 (3 days; "did not arrive" on 08/09).
- TIB DEF returns from 28/09 (3 in 2 days by 29/09, 3 more 03/10); 07/10 store says it checks zips before selling.
- ARNEB fits large, exchanges, sizing down works (20/10).
- POLARIS: only the white balaclava is assorted here (24/09); first 2 sold 12/10.
- Black Maire 0/1/2 all out by 17/10; 18/10 delivery has none; requests 16-21/10.
- Outerwear key sizes thin; transfer request from Doha/Riyadh (18/09) and heavy-outerwear request 16/10.

Traps
- 26/09 mail (sent 00:44 on 27/09) reports **AED 253.2k** = incl. 5% VAT; net = 241.1k. Clarified by Omar (`_re1`)
  and Joel (`_re2`).
- 01/10: body only "PFA." - data only in attachment `DXB01_DSR_01102026.xlsx` (values match KPI).
- 15/10 form: Joel "corrects" himself to "Arneb 2 exchanged to 1"; the data has the ARNEB **size 1** returned for
  exchange (his first wording was closer). Size info in this line is unreliable.
- 02/10 Rania says 2 pink ILVARO from the launch sold in September - DXB01 is not an E06 store and there are no
  pink unmet requests in the data; unverified.
- 13/10 -67% blamed on "browsers from cruise ship" - staff speculation.
- 17/10 `_dup` sent after midnight (file dated 18/10) with the 17/10 subject.

## SIN01 - Singapore Marina Bay Sands (SGD)

Writers: Grace Tan (SM; tidy, numbered lists, light Singlish), Muhammad Hafiz (AM; Singlish "lah", "very sian",
"shiok", "jialat", weekends/F1), Jasmine Lim (SA; emojis, some Sundays/weekdays). Area manager Daniel Lim.

Signals
- Tropical assortment reality: polos/tees/caps; outerwear bought for travel (Japan, Korea, Hokkaido, Harbin).
- POLARIS capes sold to travellers (25/09 x2, 19/10, 21/10).
- ILVARO powder pink (E06): first ask 21/09 (pre-event, IG), then craze from **Fri 02/10** (Yoon Ha-eun / LUMIERE
  photo). Store has only 00 and 3 in pink. Waitlist 7 (04/10) -> 10 (05/10) -> 12 (06/10) -> 14 (15/10).
  Daniel (06/10 `_re1`): DC top-up lands 08/10, SIN not before 15-20/10. Pink sz 3 sold 10/10 (tall Aussie).
  Pink arrived in the **20/10** delivery; one 0 sold within the hour. Spill-over: Ilvaro off-white sold as plan B (03/10).
- TIB DEF returns 28/09, 02/10 (2), 03/10.
- Singapore GP (E34) 09-11/10: footfall roughly double (260/313/215) but sales below budget each day; recap 12/10
  "SGD 98.3k vs 128.7k" -> traffic uplift did not convert (useful against naive traffic-based forecasting).
- Black Maire 0/1/2 out from 09/10 to 21/10.

Traps
- 20/10: Grace says "only 1 pc per size"; stock file on 21/10 shows 2 pcs in size 1 (6 pieces arrived, not 5).
- 21/10: one pink size 1 "on hold, not paid" - still in stock, not a sale.
- 11/10 `_dup`.

## SYD01 - Sydney Castlereagh Street (AUD) - southern-hemisphere spring

Writers: Chloe Mitchell (SM; chatty Aussie "Hey team", "shocker", "smashed it"), Arjun Patel (AM; numbers,
forecast/allocation complaints, CSV attachment), Liam O'Connor (SA; weekend one-liners, lowercase).

Signals (E16)
- Customers want tees, polos, caps, belt bags/backpacks and **light jackets**. The SS26 light jackets (MARIN,
  ALBENGA) were pulled to the DC end of August, so these requests never appear as unmet_requests -> invisible demand
  only visible in the emails (01/09, 11/09, 30/09).
- Deliveries are 60-70% outerwear (02/09, 09/09, 16/09, 07/10, 17/10 "mostly puffers again").
- Arjun's forecast complaints with numbers that match `store_weekly_value_forecast.csv` (same-week runs):
  W40 actual ~85k vs fcst 180.1k; W41 ~75k vs 183.1k; W42 ~67k vs 203.6k; W43 fcst 208.7k. Also SKU level
  "3-4 Maya a week" vs 2 sold in September (28/09).
- Daniel (29/09 `_re1`) confirms planning uses the global (northern) seasonality curve, no override before the next
  season; asks for a release list. Arjun's reply (30/09 `_re2`, which also contains the 30/09 closing) attaches
  `SYD01_outerwear_release_30Sep.csv` (staff count: 159 on hand, keep 62, release 97) and lists what they want instead.
  Actual outerwear on hand 21/10 in the stock file = 174.
- Local colour: Father's Day 06/09, AFL GF 26/09, NRL GF + daylight saving start 04/10, Labour Day 05/10 (+62%).
- Door counter down 14/09 (KPI visitors is null that day) - stated in the mail.
- Delivery planned 14/10 arrived Sat 17/10 (3 days late). Chloe on 16/10 says it was "due yesterday" (actually 14/10)
  and the courier said Monday; it came Saturday.
- POLARIS cape L asked twice (14/10, 16/10); the client buys an XL on 17/10.
- TIB DEF returns 28/09, 30/09, 01/10, 10/10.

Traps
- The CSV attachment is a staff estimate (colour/size detail not reconciled with the stock file).
- 04/10 Liam: "door counter time might be off by an hour" after the DST change - no evidence in the data.
- 17/10 `_dup`.
