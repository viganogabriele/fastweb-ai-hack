# emails_it — answer key for the Italian/Spanish store closing emails

Stores: MIL01, MIL02, ROM01, VEN01, CRT01, COU01 (Italian), MAD01 (Spanish).
Sources: `generated/sources/store_emails/<STORE>/*.eml` (one RFC-822 file per email; suffixes `_re1`, `_dup`, `_fwd`,
`_corr`, `_ooo`... for extras). Generator: `generator/emails_it/` (`bodies/<STORE>.py` = hand-authored bodies,
`build_eml.py` = wrapper, `check.py` = coverage/repetition checks, `digest.py` = authoring aid).
Machine-readable index (file -> reported business date(s), kind, sender): `generated/ground_truth/emails_it_index.csv`.
The business date is NOT in the .eml: it must be inferred from subject/body/Date header (late sends, next-morning
sends, weekend recaps and a wrong date in a subject are planted).

| Store | emails | open days | open days with no own closing email |
|---|---|---|---|
| MIL01 | 63 | 52 | Sep 3, Sep 13 |
| MIL02 | 58 | 52 | Sep 8, Oct 12 |
| ROM01 | 57 | 52 | Sep 1, Sep 22 |
| VEN01 | 59 | 52 | Sep 2, Sep 17 |
| CRT01 | 42 | 40 (every day in Sep, Fri–Sun only in Oct) | Sep 3, Sep 24 |
| COU01 | 18 | 13 (Aug 31–Sep 12, then closed for the season until Nov 26) | Sep 8 |
| MAD01 | 59 | 52 | Sep 9, Sep 21 |

All dates are CEST (+02:00). Some "missing" days are mentioned in passing in the next email (see per-store sections).

## Cross-store consistency (verified against internal data)

- **VLOGO CARDIGAN size M (MIL01)**: sold out on Thu Oct 8 (black + navy). Oct 9 Giulia (MIL01) asks for a transfer
  (`richiesta transfer cardigan logo M`); MIL02 (Stefano) refuses, ROM01 (Alessandra) says she has 5 navy M but won't
  ship without Roberto's ok; Roberto answers MIL01 "no transfer for 1–2 pcs, wait for the DC (end of month)".
  ROM01 reminds on later days that nothing was sent. **No transfer happened** (consistent with stock data).
  Trap: MIL02 claims "only ONE M, black" — stock file shows MIL02 black M = 3 on Oct 8–9, 2 on Oct 10
  (store understating stock to avoid giving it away). ROM01's "5 navy M" matches stock (Oct 9 EOD = 5).
  MIL01 Oct 15 email says cardigan M missing "da venerdi" — wrong, it was Thursday Oct 8.
- **Black AUREA at MIL01**: zero in sizes 0–2 from ~Sep 20 to Oct 20; Korean requests reported repeatedly with
  approximate counts; Roberto says DC restock on Oct 16. Shipment SHP02600502 arrived **Oct 21** with 62 black Aurea
  (00:4, 0:14, 1:19, 2:13, 3:8, 4:4); Oct 21 email "una sessantina, piu' 1 e 0", 5 sold — matches.
- **Roberto Galli** (area manager) OOO auto-reply Aug 31–Sep 4 appears in several stores (same text by design: it is
  an auto-reply). He replies in threads at MIL01 (Amalia, Aurea, cardigan), MIL02, ROM01 (cantiere), VEN01
  (acqua alta), MAD01 (wrong delivery), COU01 (inventory/return).
- **Italian general strike Fri Oct 16** appears at MIL01, MIL02, ROM01, VEN01 (not CRT01/COU01).
- Repeated text across emails that is deliberate: signatures, legal disclaimers, the OOO auto-reply, duplicate sends.


---

## MIL01 Milano Montenapoleone - closing emails answer key

63 .eml files in `generated/sources/store_emails/MIL01/`: 49 closing emails (one of them is a Sat+Sun recap) + 14 extras.
Store closes at 19:30. Emails are sent 20:10-22:20, plus one sent the next morning.

### Writers
- **Giulia Ferrandi** (Store Manager, `giulia.ferrandi@`): writes most weekdays and Saturdays. Habit: mini form
  "MIL01 - CHIUSURA dd/mm" + Fatturato/bdg/% + Ingressi/scontrini/conv, then notes. The form is full on Sep 1, gets
  lazier from mid-September and is dropped on long or emotional days. Outlook HTML table on Oct 2 and Oct 8.
  Full corporate signature + one-line disclaimer on Sep 1, Oct 6 and Oct 17 (deliberate repeated habit).
  Frustration about the black Aurea grows until the long Oct 6 email; Oct 21 celebrates.
- **Marco Pellizzari** (assistant manager, `marco.pellizzari@`): Sundays and Mondays plus a few other days. Lowercase,
  telegraphic, "x", "nn", "cmq", "qlc", "xke'", often "Inviato da iPhone".
- **Sara Kim** (senior SA, invented, Korean-speaking): looks after Korean clients and keeps the WhatsApp waitlist.
  Writes Sep 20 and Oct 18 from the shared iPad (`mil01.store@`), and Oct 4 and Oct 13 from her own address. Most
  detailed reporter on Korean demand (counts requests, drama context).
- **Roberto Galli** (area manager) replies: short, from his phone, signs "R.".
- Team members mentioned in passing (invented): Fei (the only Mandarin speaker), Chiara, Davide, Stefano (MIL02 SM).

### Planted signals (date -> what the email says -> what the data says)
| Date | Email says | Data |
|---|---|---|
| Aug 31 | 165 pcs delivery expected Saturday arrived Monday | delivery delay 2 days |
| Sep 6 | delivery 1 day late, 241 pcs | d1 |
| Sep 7, 15 | Artem returned for size, "enorme di spalle", "veste largo" | ARTEM 3 SIZE returns (fit-large issue) |
| Sep 10 | first Italian clients asking for the **Amalia marrone**; only 1 per size (2 in size 1), black stocked deeper | AMALIA chocolate brown demand starts Sep 10; stock 00:1 0:1 1:2 2:1 3:1 4:1 (matches Giulia's Sep 11 reply) |
| Sep 12 | 3 asked brown Amalia, sold one size 1 | size 1 goes 2->1 on Sep 13 |
| Sep 16 | delivery brought ONE brown Amalia (size 1) | shipment Sep 16 has 23R size 1 x1 |
| Sep 18 | "58,0k ... +21%" then correction 85,0k | true net 85,020 (+21.1%) |
| Sep 19-22 | Korean girls with a phone screenshot ask for **black Aurea**; sizes 2 and 3 gone Sep 19, 0/1 by Sep 20; beige/navy/white refused; actress "Han Yu-ri" in drama "Lettere d'inverno" (fictional) | unmet requests from Sep 19; Giulia's count "14 since Saturday" (0:4,1:2,2:3,3:5) is exactly right |
| Sep 22-28 | Milan Fashion Week: buyers, stylists, press appointments, Italian singer with photographers Sep 24, door blocked Sat Sep 26 | visitors peak 1,048 on Sep 26 with 5.3% conversion; -5% vs budget |
| Sep 24-25 | Couture Astra launch: many try-ons, "veste piccolo per essere oversize", "2.400 euro per questo?" | Astra underperforms in EU (fit small, price high) |
| Sep 25 | black Aurea sold out in ALL sizes (00 sold that morning) | stock 0 in all sizes from Sep 25 to Oct 20 |
| Sep 28 | first Vel returned: zipper slider came off | first VEL DEF return (size 4) |
| Sep 29 / Sep 30 / Oct 1 / Oct 3 / Oct 4 | 2 / 5 / 2 / 2 / 3 Vel zip returns; Oct 1 forwarded customer complaint; Oct 3 "12-13 since last Monday" | DEF returns: Sep 28 1, Sep 29 2, Sep 30 5, Oct 1 2, Oct 2 1, Oct 3 2, Oct 4 3 (13 by Oct 3, correct) |
| Sep 30 - Oct 8 | Golden Week: ~half Chinese, tax-free queue, only one Mandarin speaker, tax-free terminal down ~1h on Oct 2 | CN share 33-49%, Oct 2 136.1k (+64%), Oct 8 143.8k (+90%) |
| Oct 1 | Artem sells (6) since staff advise one size down | ARTEM black x6; exchanges continue later anyway (Oct 4-12) |
| Oct 1 | brown Amalia sizes 1 and 2 finished, DC has no 0-1-2 | store stock 1:0, 2:0 from Oct 1; DC out of 23R 0/1/2 from Sep 25 |
| Oct 3 | Chinese bought all light Aurea (6 white, 5 beige), Koreans still want black | AUREA off-white x6, beige x5 |
| Oct 5, 7, 9, 13 | Iridia powder pink asked (k-pop singer photo) | IRIDIA 510 unmet; MIL01 only had a size 4 |
| Oct 6 | 22 black Aurea requests in one day (1:9, 2:6, 0:3, 00:2, 3:2) | exact match with unmet requests |
| Oct 7 | Roberto: "La nera rientra in DC il 16, poi vi arriva con il primo giro"; waitlist xlsx to merch-planning (23 names, "oltre 70 richieste") | DC out until Oct 16; ~78 unmet requests Sep 19-Oct 6 |
| Oct 7, 14, 17 | deliveries full of beige/white/navy Aurea, no black | shipments contain AUREA 034/20D/742, no 999 until Oct 21 |
| Oct 8 | **Vlogo Cardigan size M sold out, black and navy, Thursday**; DC has none until end of October | zero stock black M + navy M from Oct 8 (8+7 pcs -> 0) |
| Oct 9 | transfer request to MIL02/ROM01; Roberto refuses: "Aspettiamo il DC" | no transfer happened |
| Oct 10 | -37% (83.6k vs 132k): Marco blames an unrealistic budget + 2 staff sick + Fei off, conversion < 6% | KPI 83.6k vs 132.0k, conv 5.9%. Staff sickness is the store's own explanation (not in other data) |
| Oct 10-20 | cardigan M asked repeatedly | unmet VLOGO CARDIGAN M on Oct 10, 12, 15 (x2), 16 (x2), 17, 20 |
| Oct 13-19 | cold weather: Nova/Liviana/Riviera, beanies, Amalia black | milder cold snap in Milan Oct 13-19 |
| Oct 13 | 14 black Aurea requests (0:6, 2:5, 3:2, 1:1) | exact match |
| Oct 16 | general strike: metro stopped, staff in late, 45.7k vs 104.7k; only Astra balaclavas sell | KPI -56%; ASTRA BALACLAVA white x3 |
| Oct 18 | 8 black Amalia sold, at least half to women who wanted brown (sizes 1-2 missing) | AMALIA black x8 (substitution) |
| Oct 19 | brown Amalia size 1 asked twice | unmet AMALIA 23R size 1 x2 |
| Oct 20 | DC confirms black Aurea arriving tomorrow | shipment shipped Oct 20 |
| Oct 21 | black Aurea arrived (~60 pcs), 5 sold same day | delivery 467u incl. ~62 Aurea black; AUREA black x5 sold |

### Traps
- **Correction**: Sep 18 email says 58,0k; corrected 47 minutes later to 85,0k (true 85,020).
- **Duplicate send**: Oct 2 email sent twice (21:12 and 21:13, `_dup`), identical text + HTML.
- **Wrong date in subject**: Oct 14 email subject says "14/09" (business date is Oct 14).
- **Wrong list**: Oct 15 closing sent to `retail-ops-spain@` instead of the Italy list (Roberto in Cc).
- **Wrong weekday**: Oct 15 Marco says cardigan M missing "da venerdi"; it ran out on **Thursday Oct 8**.
- **Aurea/Nova confusion**: Oct 12 Marco writes "5 coreane x la nova nera" - it was the black **AUREA** (Nova black is in stock and selling). Truth for Oct 12: AUREA black size 1 x3, size 3 x2.
- **Misleading claim about MIL02**: Oct 10 Marco reports Stefano (MIL02) "ha un solo M nero e se lo tiene"; stock files show MIL02 had 3 black M on Oct 8-9 and 2 on Oct 10. Roberto's Oct 9 reply ("a Roma c'e' solo blu") is true but ROM01 held 4-6 **navy M**, which MIL01 also needed: a feasible transfer was not done.
- **Approximations**: Sep 30 "a quota trenta e passa" Aurea requests (true ~43 since Sep 19); Sep 27 recap "4 solo in tg 1" correct; Sep 20 Sara says 0/1/2 sold "ieri" (size 0 and 1 actually sold out on Sep 20 itself).
- Sep 9 "Ben tornato Roberto" - he was back Sep 7.
- Oct 13 Vel 7 return reported as stitching defect ("non zip questa volta"); POS reason is QUALITY, not DEF.
- Oct 10 budget complaint: "sabato scorso coi cinesi abbiamo fatto 125" is right (Oct 3 125.1k).
- Sep 23 email to vm-team says the Amalia on the window mannequin is black because brown stock is too thin.

### Missing days / timing
- **Sep 3** (Thu): no email; Sep 4 email gives "30,8k, -34%" in passing (correct) but business_date is only Sep 4.
- **Sep 13** (Sun): no email at all (true: 51.2k, -11%).
- **Sep 26 + Sep 27**: one recap sent Sunday Sep 27 21:48 (business_date both days).
- **Sep 8**: sent the next morning (Sep 9 08:52), "mi e' morto il telefono".

### Extras
- Aug 31 Roberto out-of-office auto-reply (`_ooo`, Auto-Submitted header).
- Sep 10-11 Roberto asks brown/black Amalia counts; Giulia answers with the size breakdown.
- Sep 21-22 Roberto asks how many black Aurea requests; Giulia answers 14 with sizes.
- Sep 23 email to vm-team with 2 placeholder window photos (IMG_4471.jpg, IMG_4473.jpg).
- Oct 1 forwarded customer complaint about the Vel zip (customer F. Colombo, bought Sep 12 size 4).
- Oct 7 Roberto reply ("rientra in DC il 16"), then waitlist to merch-planning with xlsx `lista_attesa_maire_nera_MIL01.xlsx` (23 rows, initials/nationality/size/contact).
- Oct 9 cardigan M transfer request to MIL02 + ROM01 store mailboxes; Roberto's refusal.
- Oct 21 Roberto reply ("Cardigan M confermato fine mese").

---

## MIL02 Milano Rinascente Duomo - email answer key

58 .eml in `generated/sources/store_emails/MIL02/` (49 closing emails covering 50 open days + 9 extras).

### Writers
- **Stefano Rocchi (SM)**, From his own address. Writes Mon/Tue/Wed/Thu/Fri evenings, 21:45-23:00. Longer emails, complains about
  Rinascente politics (corridor works without warning, VM moving our mannequin, no event space, verbal-only decisions,
  sensor/traffic data withheld, Card Days). Has a mini-form habit (INCASSO / BDG / INGRESSI (feed Rina) / SCONTRINI / NOTE):
  used in Aug-Sep, gets lazier ("inc 12,6 / bdg 21,5 / ingr 93" on 17/09), last used 07/10, then dropped. Corporate signature with a short
  "Riservato..." disclaimer on about 12 emails (deliberate repeated habit). Subject "MIL02 Rinascente - chiusura dd/mm", which drifts to
  "chiusura MIL02 dd/mm" from 19/10.
- **Ilaria Mancuso (AM)**: short lines, lots of emoji, "Ila". Mostly Sat plus some Tue/Wed/Thu. Subject "Chiusura Rinascente d/m" + emoji.
- **Matteo Brambilla (SA)**, invented. Writes from the shared iPad mailbox `mil02.store@` ("Valentino Rinascente Duomo"), all lowercase,
  Milanese touches ("ue'", "sciura"), signs "matteo". Usually Sundays, plus 03/09 and 08/10. Subject "chiusura rinascente dd/mm".
- **Roberto Galli (AM Italy)**: OOO auto-reply 31/08, traffic question 09/09, cardigan decision 09/10.
- Giulia Ferrandi (MIL01 SM) appears only quoted inside the cardigan thread.

### Planted signals (date -> email -> truth)
| date | email says | data |
|---|---|---|
| 31/08-02/09 | Rinascente corridor closed for floor works, nobody passes | traffic 54/55/46 (not in internal data, colour only) |
| 05/09 | Iridia nero tg 3 x2, Aurea nera 4, dolcevita marrone XS | unmet exactly these |
| 07/09 | Rinascente tax-free desk queue, a customer never came back | colour (no tax-free lost-sale record) |
| 10/09, 13/09, 16/09, 24/09, 30/09, 05/10, 11/10, 18/10, 20/10 | AMALIA brown asked for, "we don't carry it", sent to via Monte; 05/10 "Monte Napo doesn't have 0-1-2 in brown either" | Brown AMALIA was in demand in Milan. **MIL02 doesn't carry AMALIA at all** (not in store_assortment), so these requests are NOT in lost_sales/unmet. DC brown sizes 0/1/2 out from 25/09 to 10/11 |
| 18/09-20/09 | Black Aurea running out, 0 then 2 finished | ZERO black AUREA 0 from 19/09 and 2 from 20/09 |
| 23/09-20/10 | Black Aurea lost requests nearly every day; waitlist 7 (25/09) -> 9 (28/09) -> 14 (20/10) | unmet black AUREA 23-25/09, 28/09, 30/09-02/10, 04/10, 07/10, 14-16/10, 18/10, 20/10 |
| 25/09 | "Roberto said on the phone nothing before mid-October" | DC black out until 16/10; store receives it with the **21/10** delivery |
| 21/10 | Black Aurea arrived, 3 sold to waitlist | stock 21/10 sizes 00-4 = 3/8/8/7/5/2; AUREA black x3 sold |
| 22/09-28/09 | Fashion week: day 1 -40% (all at the shows/rooftop), then 23/09 +102%, 24/09 +62%, Rinascente extends to 22:00 Thu-Sat | KPI matches (10.9k, 40.7k, 38.6k) |
| 23/09 | **wrong number 47,1k**, corrected at 23:18 to 40,7k net | KPI 40,710 |
| 25/09-26/09 | Delivery due Wed 23/09 arrived Sat 26/09 (3 days late) | SHP02600323 planned 23/09, actual 26/09, delay 3 |
| 28/09, 29/09, 01/10 (x2), 03/10, 07/10, 11/10, 21/10 | VEL zipper defect returns. Ilaria pulls 2 of 6 vests from sale on 01/10. On 03/10 she writes "siamo a 6??" | 8 DEF returns in total. On 03/10 the real count was 5 |
| 30/09-08/10 | Golden Week: Chinese groups, tax-free desk crash 02/10, record 56,1k on 02/10, "ultimo giorno" 08/10 | CN share 32-51%. KPI 56,125 on 02/10 |
| 06/10 | Korean girl shows a photo of the LUMIERE singer in a pink short down jacket, "we never had pink" | IRIDIA powder pink isn't in MIL02 assortment; it's an Asia-only demand event, so this is anecdotal spill-over only |
| 07/10 | 4 black Iridia sold, linked to the pink story | IRIDIA black x4 (top seller) |
| 07/10-10/10 | Delivery expected 07/10 (DHL) not arrived, arrived Sat 10/10 | SHP02600413 planned 07/10, actual 10/10, delay 3 |
| 04/10-09/10 | Vtrack Gtx 42/44 lost (4 pairs on 09/10) | unmet 42 x2, 44 x2 on 09/10 |
| 06/10 | 5 navy tricot padded cardigans, M & XXL then missing | top seller x5. Unmet M, XXL |
| 09/10 | **Cardigan thread**: MIL01 (Giulia) asks for all VLOGO CARDIGAN M. Stefano: "I only have ONE M, black, and I'm keeping it; navy M is gone". Roberto: no transfer, wait for CSG at end of month | **No transfer happened.** Stefano's claim is **misleading**: black M stock EOD 08/10 = 3, 09/10 = 3, 10/10 = 2 (and 3 again on 12/10 after 2 returns). Navy M = 0 from 09/10. DC has no M until end of October |
| 10/10 | Ilaria: "come sempre Monte Napo pensa che siamo il loro magazzino" | rivalry colour |
| 10/10, 12/10, 16/10, 17/10 | navy cardigan M requested | unmet VLOGO CARDIGAN navy M on those days (12/10 has no email) |
| 17/10 | "and now the black M is gone too (irony)" | ZERO VLOGO CARDIGAN black M from 17/10 |
| 13/10-19/10 | First real cold, people want down jackets (Fiammetta x4 on 16/10) | mild cold echo in Milan 13-19/10 |
| 15/10-18/10 | Rinascente Card Days -10%, Valentino doesn't take part, customers go to the Woolrich corner next door | invented colour. Explains part of the -29% on 17/10 (budget 50.3k) |
| 16/10 | Strike: metro stopped, Duomo closed, 24,4k -35%, Rinascente staff missing, verbal "maybe early closing" | KPI 24,350, budget 37,210. Visitors 96 |
| 19/10 | ARTEM bought at via Monte, too big, customer came to exchange here, but MIL02 doesn't carry ARTEM | ARTEM not in MIL02 assortment. Fits large |
| 20/10-21/10 | Black Iridia 1 then 1+2 finished | ZERO IRIDIA black 1 (20/10), 1 and 2 (21/10) |

### Traffic and KPI notes
- The door counter for MIL02 is the Rinascente "dept-store feed". On 10/09 Stefano claims the sensor misses people coming in from the Herno side
  ("we lose ~30%") and quotes Rinascente building totals given verbally (~17-19k per day). Those numbers come from Stefano, not from any source.
  His conversion figures quoted (6% Tue, 21% Wed) match the KPI file.
- 04/10 (Matteo): "Rina closing says 41,8, ours is 41,07, they count gross with the card". The KPI net is 41,070. Rinascente's figure is a distractor.
- Most numbers are rounded net (k EUR). Ilaria's "-10%", "+35%" etc. match vs_budget_pct to within rounding. 20/10 "lista 14 nomi" can't be checked.

### Traps / noise
- **Missing days** (no email at all): 08/09 (Tue, 6.6k -54%) and 12/10 (Mon, 19.4k -18%, 2 VLOGO CARDIGAN M size returns). The next-day emails
  apologise but give no numbers. On 13/10 Stefano calls 12/10 "lunedi normale niente da segnalare", which hides the -18%.
- **Weekend recap**: `chiusura sab + dom 19-20/9` sent Sun 20/09 covers 19/09 and 20/09.
- **Sent next morning**: Sunday 04/10 closing sent Mon 05/10 09:14 ("wifi di Rina giu'"). Matteo also first writes "Aurea nere" and then corrects himself to navy.
- **Duplicate**: 02/10 closing sent twice (23:26 and 23:28, identical body).
- **Correction**: 23/09, 47,1k -> 40,7k.
- **Wrong date in subject**: email of 15/10 has subject "chiusura 15/09".
- **Wrong list**: Saturday 03/10 closing (Ilaria) went only to vm-team@ (no retail-ops, no Roberto). Never resent.
- **Personal message to the DL**: 14/10 13:22, from the store mailbox, subject "domani" (Matteo asks Ilaria to cover his opening shift). Not a closing email.
- **OOO**: Roberto's auto-reply to the 31/08 email.
- **Forward**: 11/09 Rinascente floor manager memo (fire drill 15/09 09:15, Fashion Week opening hours to 22:00 Thu-Sat, rooftop event 24/09).
  The 15/09 email confirms the drill.
- 28/09 Stefano says the first defective VEL was "blu tg 3". The size is right but the colour isn't in the data (MIL02 carries navy and off-white).
- 27/09 Matteo writes "2 Aria panna": ARIA off-white x2 is correct.

---

## ROM01 Roma Via Condotti - store emails answer key

57 .eml in `generated/sources/store_emails/ROM01/`: 49 closing emails (one is a Sat+Sun recap) + 8 extras
(1 OOO, 4 Roberto/store thread replies, 1 fwd, 1 dup, 1 correction). Store open all 52 days; closes 19:30.

### Writers
- **Alessandra De Santis** (SM, `ale`): most days (Tue-Sat). Articulate, proper sentences. Subject habit drifts:
  `[ROM01] Report serale dd/mm` (Aug 31 -> Sep 19), then `ROM01 report dd/mm` (from Sep 23), last one `report roma 20/10`.
  Mini form habit `Fatturato / Ingressi / Scontrini / Conv. / Note` used early; field **`Cantiere:`** added from Sep 16;
  form used on fewer days from Oct (last Oct 14). Corporate signature + one-line confidentiality disclaimer on some emails
  (deliberate repeated habit). Grows exasperated (Sep 23 formal budget-revision request, Oct 17 "vorrei una risposta",
  Oct 20 three lines "Non ho altro da aggiungere").
- **Fabio Cardarelli** (assistant SM, `fabio`): Sundays/Mondays and some other days, iPhone, lowercase, Roman
  ("aho", "daje", "mo'", "nun", "'na cifra", "ce stanno a sotterra'", "ce la famo"). Subject `chiusura ...` varying.
- **Giorgia Proietti** (SA, invented, writes from store mailbox `rom01.store@` on shared iPad): Sep 11, Sep 21, Oct 5,
  Oct 13, Oct 19. Polite, plain, signs "Giorgia - ROM01".
- **Roberto Galli** (area manager): OOO auto-reply Aug 31; replies Sep 15, Sep 24, Oct 2 (after store visit).

### Main theme: construction site (true: Sep 14 -> Nov 6, traffic x0.5)
| Date | Email says | Truth |
|---|---|---|
| Sep 14 | surprise cantiere comunale (pavimentazione) + ponteggio condominio, 2 of 3 windows covered by panels, nobody warned; 74 ingressi vs 138 previous Monday; 3 photos | visitors 74 (Sep 7: 138); net 11.53k vs 24.3k budget |
| Sep 15 (re2) | Municipio I says "fine ottobre"; vigili called; requests "siamo aperti" panel, totem at Piazza di Spagna corner, weekend person | real end Nov 6 |
| Sep 16 fwd | administrator's circular dated Sep 10: facade ponteggio ~7 weeks, Comune cantiere "fine ottobre 2026" | real end Nov 6 |
| Sep 16-27 | dust on products/windows, drills, carotatrice, courier can't reach door, home-made A3 sign removed by vigili, clients think store closed | qualitative |
| Sep 23 | concierges Hassler / de Russie / d'Inghilterra briefed; rest of Via Condotti & Piazza di Spagna not affected; formal budget revision request (Cc merch) | traffic about -50% vs pre-cantiere |
| Sep 30 | foreman: "diciamo novembre" | |
| Oct 2 | Roberto visits; his reply promises totem + panel + weekend hostess, asks merch to account for -50% traffic | |
| Oct 7 | totem + printed panel installed | |
| Oct 10/11 | hostess on weekends; Sat 192 ingressi "miglior giornata" | Sat Oct 10 visitors 192, net 56.37k (-19%) |
| Oct 14 | foreman: "6 novembre" for transenne, +1 week for ponteggio | matches Nov 6 |
| Oct 17 | budget still unchanged in system; 202 ingressi but conversion <10% | visitors 202, conv 9.9%, -56% |
| Oct 21 | 6 Nov confirmed, totem/hostess stay | |
Footfall pre-cantiere ~134-251/day; during ~61-202 (weekdays mostly 70-115).

### Other signals
- **VEL zipper defect**: first return Sep 28 (tg 4), Sep 29 tg 3 + tg 2 (Fabio "3 in due giorni"), Sep 30 tg 3, Oct 1, Oct 3, Oct 9, Oct 12 (Ale "credo 8": true DEF count Sep 28-Oct 12 = 8; Sep 30 "siamo a 4" also correct). Fabio Oct 3 jokes white Tibs don't break; Oct 11 Vel 5 return is change-of-mind (zip ok) - correct.
- **ARTEM fits large**: Sep 10 client sized down 5->4; Sep 25 two size exchanges 5->4 / 6->5 (true: EXCHANGE_SIZE 5 and 6); Oct 3 client wanted 7, advised 6; Oct 4 sold 2 sizing down.
- **Black AUREA** out in 0/1 from Oct 2-4, requests Oct 6, 7, 9, 10, 13, 14 (tg 0), 16, 17 (3x tg1 + tg3), 18 (2, 3). CSG says "meta' mese" (Oct 6). Arrived Oct 21 delivery (00:3, 0:9, 1:12, 2:9, 3:6, 4:3) - stated correctly. ROM01 is not a Korean-tourist store; requests come from mixed clients.
- **Italian general strike Oct 16**: ATAC stopped after 8:45, staff late, opened with 2 people; net 17.22k vs 55.86k (-69%), visitors 97.
- **VLOGO CARDIGAN M / MIL01** (Oct 9): MIL01 called; ROM01 has 5 navy M (true: on_hand M navy = 5 on Oct 9); refused without Roberto's ok. Oct 12 Roberto hasn't answered; Oct 21 confirms **no transfer was made** (stock M navy goes 6->5->4 only through sales).
- Golden Week: Oct 8 Fabio "a Milano hanno i cinesi, qua col cantiere nemmeno quelli" - no Chinese peak at ROM01 (correct).
- Deliveries: Sep 2 (163, on time), Sep 11 (218, 2 days late - correct), Sep 16 (243, unloaded on Via Belsiana), Sep 26 (176, planned Sep 23 - 3 days late; Fabio's courier/transenne explanation is an unverified staff claim), Sep 30 (204), Oct 7 (222, no black Aurea), Oct 14 (252, no black Aurea), Oct 21 (254, black Aurea).
- Other unmet requests mentioned: Aria powder pink 2 (Aug 31), Cosimo 6 (Sep 3, Sep 10), Monteluce grey 4 x2 (Sep 4), Nova olive 1 (Sep 5), hoodie grey XL (Sep 6), Amalia chocolate 2 (Sep 7) and 0 (Oct 18), Vel black 4 + Monteluce 5 (Sep 9), Sep 10 list, Fiammetta navy 3 + tricot grey XL (Sep 11), Valdora 00 (Sep 13, Sep 15), vlogo cardigan navy S + Vtrack 41 (Sep 14), Sep 23 list, T-shirt navy L (Sep 24), Nova olive 6 + Alpina 35 (Sep 25), Artem 7 (Oct 3), Cortina XL (Oct 4), Mistral navy 3 (Oct 11).

### Traps / noise
- **Missing days**: Sep 1 (Tue) and Sep 22 (Tue) have no email. Both are mentioned in passing next time: Sep 2 "ieri sotto i 10k" (true 9.86k), Sep 23 "ieri 15k e 70 ingressi" (true 15.04k, 70). business_date not set for them.
- **Recap**: Fabio Oct 11 covers Sat Oct 10 + Sun Oct 11 (business_date "2026-10-10,2026-10-11").
- **Sent next morning**: Sep 29 report sent Sep 30 08:47 (phone died).
- **Duplicate**: Sep 27 Fabio sent twice (20:04 and 20:06, identical, `_dup`).
- **Correction**: Oct 3 Fabio wrote 34,7k; correction 21:40 says 43,7k (true net 43.68k, -36%). The first email has no % (so the wrong figure is not self-evidently wrong).
- **Gross vs net**: Sep 21 Giorgia "fatturato 25,4k" = gross incl. VAT (true net 20.85k x 1.22); budget 27.6k quoted correctly so it looks only -8% instead of -24%.
- **Wrong colour**: Sep 17 Fabio "vendute 2 Aurea blu" - true top seller AUREA **black** x2 (navy Aurea sold Sep 21 / Oct 1 / Oct 10).
- **Wrong date in subject**: Oct 13 Giorgia subject "Chiusura ROM01 13/09" (business date 2026-10-13).
- **Wrong list**: Oct 19 Giorgia sent to `retail-ops-spain@` instead of Italy DL (Roberto still in Cc).
- Sep 15 Fabio wonders whether the Valdora 00 request is the same client as Sunday: two separate unmet requests in data (Sep 13 and Sep 15).
- Sep 25 "113 ingressi" inflated by people asking directions (true visitors 113, conv 12%).
- Oct 20 Ale gives sales 9.9k (true net 9.87k) and notes 3 returns (Aria 0, cable knit colour, Vtrack 42 - correct).
- No weather claims beyond "caldo" Sep 6.

---

## VEN01 Venezia San Marco - closing emails answer key

59 .eml in `generated/sources/store_emails/VEN01/` = 49 closing emails (one is a Sat+Sun recap) + 10 extras
(1 OOO, 1 dup, 1 correction, 1 fwd, 1 morning alert, 3 replies from Roberto, 2 store answers).
Store closes 19:30; emails sent 20:00-21:30 unless noted.

### Writers
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

### Planted signals (email says -> data)
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

### Traps / noise
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

---

## CRT01 Cortina d'Ampezzo - email answer key

42 emails (35 closing incl. 3 weekend recaps, 1 dup, 1 correction, 1 OOO, 2 Roberto replies, 2 misc store emails).
Open days 40 (Aug 31-Sep 30 daily; Oct 1 closed; from Oct 2 Fri-Sun only, E44). Closed days have no closing email.

### Writers
- **Martina Menardi** (SM): most days. Mini form habit "CRT01 - chiusura dd/mm / Fatt / Ingressi / Scontrini / Note"
  used regularly in early Sept, lazier from mid-Sept, mostly dropped in Oct (subject drifts to "chiusura cortina dd/mm").
  Exact net figures (usually = KPI). Signs "Martina" / "M.".
- **Davide Dibona** (AM): Tue/Sun and some weekends; telegraphic lowercase, "bondi", k-rounded numbers, signs "dav".
  Writes the weekend recaps Sep 19-20 and Oct 17-18.
- **Silvia Lacedelli** (SA) from the shared mailbox crt01.store: Sep 10, Sep 18. Formal, fixed signature (habit).
- **Roberto Galli**: OOO auto-reply Sep 1; replies Sep 29 (schedule) and Oct 5 (VEL zips).

### Planted signals (date -> email says -> data)
| date | email | truth |
|---|---|---|
| Aug 31 | Vtrack 45 returned, sole peeling; Aria rosa cipria 4, Mario navy 6 requested | returns VTRACK GTX 45 QUALITY, ARIA SIZE; unmet ARIA powder pink 4, MARIO navy 6 |
| Sep 2 | delivery 34 pz; Ettore 7, Vel navy 7, Piero 6 missed | SHP02600190 34u on time; unmet as stated |
| Sep 4-5 | Cortina XS / S requested, S sold out | unmet CORTINA black XS (Sep 4), S (Sep 5) |
| Sep 8-9 | Aurea nera selling, "0 e 2 finite" from Sep 9 | AUREA black sold x2 Sep 8 and x2 Sep 9; zero sizes 0 and 2 from Sep 9 to end of window |
| Sep 11, 18, 19, Oct 3 | Aurea nera requested in 2 / 00 / 3 / 2 | unmet AUREA black 2 (Sep 11, Oct 3), 00 (Sep 18), 3 (Sep 19) |
| Sep 14, 20, Oct 2, Oct 9 | Artem fits big, sold one size down; Oct 9 Artem return "ci ha ripensato" but Davide thinks too large | ARTEM fit issue (store-wide scenario); Oct 9 POS reason is CHANGE_MIND, not SIZE |
| Sep 16-17 | hoodie returns, "le felpe vestono piccole?" | VLOGO HOODIE returns M and S reason SIZE (Sep 16, 17) - store impression only |
| Sep 17 | Amalia marrone 2 requested, never received at CRT | unmet AMALIA chocolate brown 2 (brown allocation is Milan/Paris) |
| Sep 18 | Chinese tour group (bob track) | CN 50% |
| Sep 25/28 | Iridia nero finished (2 sold "ieri" = Sep 24), Iridia 0 requested Sep 28 | IRIDIA black x2 Sep 24, zero 0 and 1; unmet IRIDIA black 0 Sep 28 |
| Sep 28 | October schedule: open only Fri-Sun, Oct 1 closed, Wed deliveries suspended/moved to Friday | E44; no deliveries in October at all (Roberto promised Friday deliveries, none arrive - Davide Oct 14) |
| Sep 30, Oct 4 | Vel navy tg 4 returned, zip slider broken (first case, then second) | VEL returns size 4 reason DEF on Sep 30 and Oct 4 (zipper defect batch) |
| Oct 2 | Saudi family, Golden Week Chinese couple, 2 Artem | +83% day, SA 13%, CN 13% |
| Oct 10-11, 16-17 | Chinese groups, Germans/Austrians | CN 20-43%, DE 15-20% |
| Oct 14 | weekday visit: sample count, VM kit missing backdrop, asks Aurea nera 0/2, Piero, Liviana 1/4, Iridia nero for winter | store closed (no KPI); the "1 beanie navy missing" is an unverified claim |
| Oct 16 | first snow; dolcevita marrone XL request; Iridia return colour; Vtrack W 37 sole issue | unmet CASHMERE TURTLENECK chocolate brown XL; returns IRIDIA COLOUR, VTRACK W 37 QUALITY |

### Traps / noise
- **Missing days**: Sep 3 (Thu, 3.58k) - only alluded to in the Sep 4 email ("ieri giornata morta", no numbers);
  Sep 24 (Thu, 7.35k, IRIDIA black x2) - no email, sales mentioned with lag in Sep 25 email.
- **Weekend recaps** (business_date lists both days): Sep 19+20 (sent Sun night), Oct 3+4 (sent Mon Oct 5 10:20,
  next morning-ish), Oct 17+18.
- **Sent next morning**: Sep 15 email sent Sep 16 08:40 (subject "chiusura ieri 15/9").
- **Wrong date in subject**: Sep 26 email has subject "CRT01 chiusura 25/09" (body is Saturday Sep 26: 11.670 EUR,
  79 visitors). Sep 25 has its own correct email.
- **Wrong figure + correction**: Oct 2 email says "15.8k"; correction Oct 3 09:05 says 18.470 (true KPI 18,470, +83.4%).
- **Duplicate**: Sep 13 sent twice (20:40 and 20:44, identical body). Sep 13 also says "15k" (true 14,600).
- **Wrong list**: Sep 8 email (Aurea nera running short warning) sent to retail-ops-spain instead of Italy DL;
  Martina refers to it on Sep 9 ("Davide ieri ve l'aveva scritto").
- **OOO**: Roberto auto-reply to the Sep 1 email (out of office until Sep 4).
- Davide's rounding: Sep 1 4,4k (4,440), Sep 6 3,2k (3,160), Sep 22 6,7k (6,733), Oct 18 8k (8,040) - fine.
- Sep 19 "Aurea nera in 3, finita anche quella" - zero-stock list only shows 0 and 2; size 3 was an unmet request,
  so "finita" is the writer's assumption.
- Sep 6: "1 scontrino" with 3 pieces is correct (receipts=1, units=3).
- Sep 25 says cardigan S returned and exchanged for M (POS reason SIZE).

---

## COU01 Courmayeur - email answer key

18 emails: 12 closing emails (13 open days Aug 31 -> Sat Sep 12, one missing), 4 misc store emails
(inventory Sep 13, return to DC Sep 14, reopening prep Oct 6 and Oct 19; business_date blank), 1 Roberto reply,
1 Paolo answer with XLSX + JPG attachments. Closed for the season Sep 13 -> Nov 26: no closing emails.

### Writers
- **Paolo Bertholin** (SM): starts "Bon,", numbered points 1) fatturato 2) ingressi/scontrini 3) clienti, French bits
  ("voilà", "bref", "merci"), "Allora ciao". Corporate signature + one-line confidentiality disclaimer on several
  emails (deliberate repeated habit). Exact net figures.
- **Elisa Vuillermoz** (AM): "raga", lowercase, k-rounded, CAPS when frustrated, signs "Eli". Days: Sep 1, 3, 5, 7.
- **Sophie Glarey** (seasonal SA) from cou01.store mailbox: Sep 11.
- **Roberto Galli**: Sep 15 reply asking for inventory differences + DDT photo (CSG sees 8 colli, not 9).

### Planted signals
| date | email says | truth |
|---|---|---|
| Aug 31 | Swiss/Americans, 2 Nova nere; Fiammetta nero 4, Vtrack W 38 missed | US/CH/IT 20% each; unmet as stated |
| Sep 2, Sep 9 | deliveries 30 pz and 8 pz arriving 10 days before season close; asks to block replenishment | SHP02600189 30u, SHP02600235 8u, both on time |
| Sep 3-4 | 2 Vel bianchi sold, Vel bianco 4 finished and requested next day | VEL off-white x2 Sep 3; unmet VEL off-white 4 Sep 4 |
| Sep 5-6 | Amalia marrone 3 and 2 requested, never received | unmet AMALIA chocolate brown 3 (Sep 5), 2 (Sep 6) |
| Sep 7, 9, 11, 12 | "cappellino bianco" (VLOGO CAP white) finished, requested again and again; one arrived in the Sep 9 parcel and sold | unmet VLOGO CAP white Sep 7, 11, 12; VLOGO CAP white sold Sep 9 |
| Sep 6, 11, 12 | Iridia nero 2 / 00 / 00 requested | unmet IRIDIA black 2, 00, 00 |
| Sep 12 | last day: 2 jersey polo bianche M (Koreans), Fiammetta navy 00, Artem nero 7 | unmet as stated; KR 33% |
| Sep 13 | inventory with handheld: system 216, counted 214 (-3/+1); POS Z-closure, line suspension ticket | stock file COU01 Sep 12 = 216 units on hand |
| Sep 14 | BRT pickup 11:20, DDT 0058/26, 9 colli, 121 pz returned to CSG; 93 pz (heavy down + Alpina) stay in store | see traps |
| Sep 15 | Roberto: CSG booking shows 8 colli; Paolo: 8 merch + 1 hangers/VM material; XLSX with differences | XLSX: VLOGO CAP navy -1, VLOGO T-SHIRT white M -1, VALENTINO SCARF grey -1, VLOGO BEANIE white +1 |
| Oct 6 | winter allocation proposal (Aurea nera 0-2, Alpina, Piero/Valdora, white cap, small women sizes 00/0, brown Amalia); VEL zip: "our 7 white Vel are in the Sep 14 return"; painting Nov 2-6; 2 seasonal hires; reopening Fri Nov 27 | VEL zipper defect is real (from Sep 28, other stores); COU01 had 7 VEL off-white on Sep 12 |
| Oct 19 | snow above 1800 m, one hire done, Elisa back from Milan Nov 2, merch planning has not answered, opening confirmed Nov 27 | - |

### Traps / noise
- **Missing day**: Tue Sep 8 (4,020 EUR, 4 receipts; unmet ARTEM black 6, VALDORA off-white 1) has no email.
- **Wrong date in subject**: the Sep 9 email is titled "COU01 - Chiusura 08.09" (body = Wed Sep 9: 1,279 EUR,
  39 visitors, 8-piece delivery). Easy to mistake for the missing Sep 8.
- **Stock feed contradiction**: the internal store stock file keeps showing ~216-218 units on hand at COU01 after
  Sep 14, i.e. the return of 121 pieces to CSG is not reflected (and the -2 inventory difference is not booked).
  Emails are the correct reading: ~93 pieces physically in the store stockroom after Sep 14.
- Colli count disagreement (8 vs 9) between CSG pickup booking and DDT: 9th parcel is non-merchandise.
- Sep 10 email says "10 cartoni vuoti" arrived; 9 used.
- Elisa's help at MIL01: Sep 12 says "until mid-October", Oct 19 says she returns Nov 2 (plan changed).
- Sep 3 "reso cappellino, taglia unica ma stava piccolo" = POS return VLOGO CAP TU reason SIZE.
- Elisa's figures are rounded (4k = 4,041; 6,2k = 6,250); Paolo's are exact.
- "l'anno scorso a Natale eravamo già scoperti" (Oct 6) is an unverified claim.

---

## MAD01 Madrid Calle Serrano - email answer key

Output: `generated/sources/store_emails/MAD01/` (59 .eml). There are 49 closing emails and 10 extras. Language is Spanish (es-ES), plus some Argentinian Spanish from the SA, Roberto's Italian/Spanish mix, and the DC reply in English.

### Writers
| persona | address | role / habits |
|---|---|---|
| Lucía Fernández Ortega | lucia.fernandez@ | SM. Formal and polite ("Buenas noches", "Os paso el cierre"). Uses the **RESUMEN CIERRE** form (Venta neta / Ppto / Tráfico-Conv. / Tickets-UPT / Comentarios) in most emails until about Sep 19. After that she uses it only sometimes (Oct 2, Oct 17) and otherwise writes free text. Subject starts as "Cierre MAD01 - dd/mm" and drifts to "Cierre MAD01 dd/mm" and then to lowercase "cierre dd/mm". Some emails carry a corporate signature with a one-line confidentiality disclaimer, a deliberate repeated habit. Gives exact euros (e.g. 26.630 €). Writes Tue-Sat. |
| Javier Molina | javier.molina@ | AM. Short, casual and jokey ("q", "tb", "x", "jaja", "finde", "domingazo"), with no accents. Gives k figures (21,9k). Signs "Javi" or "J.", sometimes adds "Enviado desde mi iPhone". Writes most Sundays and Mondays. |
| Martina Echeverría | martina.echeverria@ or the store mailbox | Argentinian SA who handles the LatAm client book. Uses voseo and Argentinian forms ("mirá", "re linda", "acá", "feriado", "ustedes"). Writes from the shared iPad (mad01.store@) on Sep 7 and Oct 12, and from her own address on Oct 16 (fwd) and Oct 18. |
| Roberto Galli | roberto.galli@ | Area manager. Writes a funny mix of Italian and Spanish from his iPhone. Sends an OOO auto-reply on Aug 31. |

The default recipients are To retail-ops-spain@ and Cc Roberto.

### Planted signals (date -> email says -> truth)
- **Wrong delivery (NOVA navy instead of black)**
  - Sep 19: 4 black NOVA sold, replenishment requested. Sep 20 (Javier): about one black left per size, none in sizes 1 and 7. Stock agrees.
  - Sep 22-23: black NOVA at zero in size 3 (then 4). True: size 3 was zero from Sep 21 and size 4 from Sep 23.
  - Sep 24-25: the delivery did not arrive, DHL blames the hub. True: planned Sep 24, arrived Sep 26.
  - Sep 26: the delivery arrived 2 days late with 17 navy NOVA (sizes 1-7) instead of black. The email has photos IMG_4471-4473 and Cc dc-replenishment. True: shipment SHP02600337 had 17 lines with 742 received instead of 999. The size breakdown in the Sep 28 reply (1/2/5/4/3/1/1) is exact.
  - Sep 27: Roberto asks for the shipment number and sizes. Sep 28: Lucía answers "el envío del jueves 24, llegó el sábado" without the number.
  - Oct 1: the second wrong shipment, 20 more navy NOVA. True: SHP02600382 had 20 navy units. The email says "unos 50 navy". True: 52 on hand.
  - Oct 7 (fwd, sent 11:05): the DC reply came Oct 6 18:27. It confirms the picking error on both shipments and gives an ETA of Oct 8 for black. Navy units are to be kept until an RMA arrives.
  - Oct 8-9: the delivery did not arrive. Oct 11 (Javier): it arrived on a Sunday, 3 days late, with about 20 black NOVA in sizes 2-7, and 3 were sold. True: SHP02600427 was planned Oct 8 and arrived Oct 11. End-of-day black stock was 2/6/5/4/2/1 (sizes 2-7) after 3 were sold, so about 22 were received. Size 1 is still zero.
  - Oct 15: more black arrived. Oct 18: a client returned navy size 3 (POS reason COLOUR) and bought black.
  - Oct 21: still about 40 navy on hand (true: 39) and no RMA.
  - Requests for black NOVA appear on Sep 25, Sep 26, Sep 30, Oct 3 and 4 (recap), Oct 6 (3 clients), Oct 7 (size 2 x2) and Oct 9. These match the unmet_requests data.
- **Door counter broken Oct 1-7**
  - Oct 1: "marca 0".
  - Oct 2: ticket to it-helpdesk. Manual estimate of about 150 visitors and "conv aprox 11%".
  - Oct 4: recap estimates about 250 (Sat) and about 200 (Sun).
  - Oct 5: "Conversion 0%" with about 110 visitors.
  - Oct 6: Lucía's reply lists estimates of 90/150/250/200/110. The Oct 6 closing says about 130 and the Oct 7 closing about 140.
  - Oct 8: a technician replaced the sensor and the count is 155. **True traffic for Oct 1-7 is unknown.** The KPI file has visitors 0 and blank conversion. All the estimates and "conversion" figures that week are invented by staff and should not be used.
- **AMALIA chocolate brown**
  - Requested on Sep 13 (size 1), Sep 19 (2), Sep 23 (2), Oct 4 (0 x2), Oct 10 (1), Oct 11 (2), Oct 16 (1) and Oct 20 (0).
  - Oct 15: only a size 00 arrived (true: 00 stock went 0 to 1).
  - Oct 16: Martina forwards a request from a Colombian client for size 1 and asks for a transfer. Cc merch-planning.
- **ASTRA (Couture)**
  - Sep 24: launch day, 1 cape sold. Other clients find it small and expensive.
  - Sep 30: 2 capes sold to Chinese clients.
  - Oct 7: unmet request for black in size S.
  - Oct 18: one oversized jacket sold ("la única talla que le entraba").
  - Oct 19: white cape sold ("milagro").
  - Oct 20: unmet request for white in size L.
- **VEL zipper defect**: returns on Sep 29 (1), Sep 30 (2) and Oct 1 (2), with "van cinco" (true: 5 DEF returns). Oct 7: VEL black size 3 out of stock. Oct 21: VEL navy size 2 returned for quality.
- **ARTEM fits large**: staff advise one size down (Sep 10, 15, 18, 22, Oct 9, Oct 11 exchange).
- **LatAm clients**
  - The Sep 7 and Oct 12 emails (Martina) focus on Mexican, Colombian and Argentinian clients. MX/CO/AR clients also come up on Sep 2, 4, 12, 25, 29, Oct 4, 10, 16 and 18.
  - Tax-free comments on Sep 4, 25 and 27, and Oct 10 (queue at the till).
  - Oct 10: a Barranquilla client compares prices with Miami.
  - Clients are buying for ski or winter trips.
- **AUREA black**: unmet requests on Sep 7-8 (size 0), Oct 7, Oct 10, Oct 14 (zero in 0-2), Oct 16-17 and Oct 19. Oct 18: Roberto says merch will ship it next week. True: the DC is back from Oct 16, but MAD01 is still at zero through Oct 21.
- **Madrid colour**
  - Heat in early September (Sep 1, 3, 6).
  - El Corte Inglés mentioned Sep 5.
  - Puente del Pilar weekend, Oct 9-10: 301 visitors, a Hispanidad crowd.
  - Oct 12, national holiday: the store is open (true, 14.4k), and the morning was dead because of the parade at Colón/Castellana.
  - No fashion-week events are mentioned.

### Traps / noise
- **Wrong product name**: Sep 27 (Javier) says "Aurea azul marino hasta en la sopa". It should be the men's **NOVA** navy. Navy AUREA (women's) does exist and sells, e.g. 2 on Sep 28.
- **Wrong number + correction**: the Sep 12 closing says 39.900 € and +31%. True: 33.870 € and +11.2%. A correction was sent Sep 13 at 10:12 (kind=correction).
- **Wrong date in subject**: the Sep 16 email's subject says "Cierre MAD01 - 15/09". The body is Sep 16 data.
- **Duplicate**: Sep 25 was sent twice (21:58 and 21:59, `_dup`, identical body).
- **Wrong list**: the Oct 5 closing (Javier) went To **retail-ops-italy@** (Cc Roberto) and never reached retail-ops-spain. Roberto points this out on Oct 6.
- **Sent next morning**: the Oct 13 closing was sent Oct 14 at 09:48.
- **Recap**: Sat Oct 3 and Sun Oct 4 are in one email (Oct 4 21:30, business_date both days). The Saturday visitors figure is an estimate.
- **Missing days (no email)**: **2026-09-09** (true: 12.2k, -23%) and **2026-09-21** (true: 12.0k, -30%, unmet AMALIA brown 2, MISTRAL black 5).
- **Rounded or approximate figures**: Javier gives k values. Lucía's Oct 1 "unos 50 navy" is 52 and the Oct 11 "40 y pico" is 41. The "unas 20 piezas" of black NOVA on Oct 11 is about 22 received. The Oct 21 "pedido 4 veces este mes" for FIAMMETTA black 3 is correct (Oct 1, 3, 10, 21).
- **Soft claims without data**: no explanation is given for the very weak Sep 17 and Oct 20. DHL's "incidencia en el hub" is the store's report only. The Monterrey and Guadalajara client stories are colour and are not traceable in POS.
- **OOO**: Roberto's auto-reply on Aug 31 tells people to contact retail-ops-**italy** even for Spain.
- **Extras (10)**: ooo, correction, dup, Roberto re (Sep 27), Lucía re (Sep 28), Roberto re (Oct 6), Lucía re (Oct 6, Cc it-helpdesk), fwd DC (Oct 7), fwd client (Oct 16), Roberto re (Oct 18).
