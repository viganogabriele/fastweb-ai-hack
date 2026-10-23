# VEN01 Venezia San Marco - closing emails answer key

59 .eml in `generated/sources/store_emails/VEN01/` = 49 closing emails (one is a Sat+Sun recap) + 10 extras
(1 OOO, 1 dup, 1 correction, 1 fwd, 1 morning alert, 3 replies from Roberto, 2 store answers).
Store closes 19:30; emails sent 20:00-21:30 unless noted.

## Writers
- **Chiara Zennaro** (SM) - Mon/Wed/Thu/Fri mostly. Warm, medium length, light Venetian touches ("ciò", "un fia'").
  Store habit: mini form `VEN01 - <giorno> <data>` / Fatturato / Budget or Ingressi / Scontrini / Note. Used on about
  half her emails, the "Note:" variant appears later. Subject "Chiusura VEN01 dd/mm" (stable, once "14.09").
- **Luca Boscolo** (AM) - Tue, Sat, some Wed/Fri. Telegraphic, lowercase, "x", "nn", "tt", "xke", k-numbers,
  "ostrega", "bon", "dai che", "Inviato da iPhone" sometimes. Subjects drift: "chiusura VEN 1/9" -> "VEN chiusura 8/9"
  -> "chiusura sab 12/9" -> "chiusura 6/10".
- **Marta Tagliapietra** (invented senior SA) - Sundays, from the shared store mailbox `ven01.store@...`
  (display name "Valentino Venezia San Marco"), polite, full sentences, signs "Marta".
- **Roberto Galli** (AM Italy) - OOO auto-reply 31/8; short phone replies 2/10, 5/10, 20/10, signs "R.".
- "Andrea" = Mandarin-speaking SA (mentioned only, never writes).

## Planted signals (email says -> data)
| date | email says | data |
|---|---|---|
| 31/8-6/9 | early Sept budget "fuori di testa", -50/-57% | KPI vs_budget -50.5 (4/9), -57.1 (5/9); budget looks inflated |
| 3/9 | delivery expected Wed arrived Thu (boat/Tronchetto), 121 pz | SHP02600188 planned 9/2, actual 9/3, 121u, delay 1 |
| 9/9-11/9 | delivery not arrived, then arrived 2 days late, 129 pz | SHP02600234 planned 9/9, actual 9/11, delay 2 |
| 5/9, 8/9 | Vtrack W black 38 asked twice + return of a 38 for colour | unmet 9/5 and 9/8 + RET COLOUR 9/8 |
| 10/9 on | ARTEM fits large, advise one size down; exchanges 26/9, 10-11/10, 14/10, 19/10 | ARTEM fit event; RET EXCHANGE_SIZE 10/10, 19/10, SIZE 14/10 |
| 10/9 on | black AUREA small sizes repeatedly asked/out (0,1 then 2 from 15/10) | ZERO AUREA black 1 from 9/10, 0 from 9/26, 2 from 10/15; unmet 9/10 (4), 9/18, 9/22 (1), 9/28, 10/2, 10/7, 10/8, 10/17 (0) |
| 21/10 | 25 black Aurea arrived 00-4 | SHP02600505 contains 25 J20931A00012-999 (DC back in stock 16/10) |
| 16/9, 21/9, 26/9, 1/10 | pink IRIDIA asked in 3 and 0 | unmet IRIDIA powder pink 3 (9/16, 9/21, 9/26), 0 (10/1). Store held pink 1 and 2 throughout; 3 sold 9/9, 0 sold 9/22 |
| 2/10 | k-pop singer seen in pink Iridia "ieri a Parigi" | idol photographed 1/10 PFW |
| 14/10, 21/10 | 2 pink Iridia arrived (0 and 3), then 2 more | shipments 10/14 and 10/21 each 2 units 510 |
| 29/9 -> 20/10 | VEL zipper slider returns, running count 1,3,6,7(3/10),8,9,10,11,12,13 | RET DEF: 9/29, 10/1 x2, 10/2 x3, 10/3, 10/6, 10/7, 10/9, 10/13, 10/16, 10/20 = 13. 14/10 VEL return is QUALITY (stain), correctly NOT counted |
| 30/9-8/10 | Golden Week, CN 30-67%, queues, groups with guides, open till 20:00 Wed/Thu 7-8/10 | CN share 30-67%; KPI +6..+37% |
| 3/10 | 315 ingressi, 38 scontrini, best day | KPI 67,360 net, 315 visitors, 38 receipts |
| 26/9 | AMALIA black x3 after window | top sellers AMALIA black x3 |
| 7/9, 1/10, 8/10 | Amalia "cioccolato/marrone" sold | sales AMALIA 23R 9/7, 10/1, 10/8 (not unmet here) |
| 15/10 | +50%, VIC family, 5 white beanies, 2 Astra Cape | KPI 50.2k; beanie white x5, Astra Cape x2 |
| 16/10 | general strike: vaporetti reduced, staff late, -50% | strike event; KPI -50.5 |
| 18/10-19/10 | Centro Maree forecast 105 -> 115-120 -> 118 | acqua alta 118 cm 20/10 |
| 20/10 | opened 12:00, MOSE late, ~4k, 38 ingressi, 4 scontrini, no stock damage, doormat/vestibule | partial opening 0.6; KPI 3,950 net, 38 visitors, 4 receipts, -85.8% |
| 10-11/10, 12-14/10, 19/10 | weak days blamed on rain / no ships | KPI -33..-70%; weather not verifiable in other sources (staff explanation) |

## Traps / noise
- **Missing days**: 2026-09-02 (Wed) and 2026-09-17 (Thu). Both later mentioned in passing: 3/9 "giornata piatta,
  sotto budget" (true 9.3k, -33%); 18/9 "sui 10k" (true 10,070, -55%).
- **Recap**: 2026-10-10 + 2026-10-11 in one email sent Sun 11/10 21:15 (business_date "2026-10-10,2026-10-11").
- **Sent next morning**: Sun 27/9 closing sent Mon 28/9 09:05 (store wifi down).
- **Duplicate**: 19/9 closing sent twice (21:05 and 21:07, identical body, `_dup`).
- **Correction**: 3/10 Luca writes "76,4k"; correction 22:05 -> 67,4k (true 67,360). The "+37%" in the first email was right.
- **Wrong date in subject**: email of 8/10 has subject "Chiusura VEN01 08/09" (body says "ultimo giorno di Golden Week").
- **Wrong list**: 24/9 closing sent only to vm-team@ as "Re: vetrine W39 - Amalia" (not to the DL, no Cc Roberto);
  re-summarised by Chiara on 25/9 ("19k, -27%" - true 19,020, -26.6%).
- **Self-contradiction**: Luca 26/9 "il rosa lo abbiamo mai avuto in negozio??" - false, he himself reported selling
  a pink Iridia tg 3 on 9/9, and pink sizes 1/2 were in stock all period.
- **Rounded / approximated numbers**: 13/9 "25k circa" (25,043); 20/9 "29k e qualcosa" (29,055); 20/10 "quasi 4k"
  (3,950); 30/9 "un terzo cinesi" (30%); 12/10 "2 Cosimo navy e accessori".
- 22/9 Luca says "cinesi 40% abbondante" (true 41%).
- 16/9 Chiara: big day explained by a family sent by the Gritti concierge (4 VEL black, 4 caps) - consistent with top sellers.
- 21/10: Luca lists the delivery; there is no delivery problem despite acqua alta the day before (true, on time).
- The authoring request suggested acqua-alta sales "about half"; the data says -86% vs budget and the email follows the data (~4k).
- The 2/10 VEL thread: Roberto asks for photos; store answer 3/10 10:12 with 3 placeholder JPEGs, list of
  returns by size/date (correct vs POS). 20/10 thread: Roberto asks about damages/insurance; answer 21/10 09:25
  (Cc facility-italy, 4 photos): no stock damage, vestibule stone/doormat, fitting-room carpet edge damp.
- City alert forwarded 19/10 22:40 (kind fwd) from a fictitious Comune address on `.example` domain.
