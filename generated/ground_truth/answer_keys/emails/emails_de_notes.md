# Store closing emails, German (group emails_de): answer key

Stores: MUN01 (München Maximilianstraße), BER01 (Berlin KaDeWe shop-in-shop), ZRH01 (Zürich Bahnhofstrasse),
STM01 (St. Moritz Via Serlas).
Output: `generated/sources/store_emails/<STORE>/<YYYYMMDD>_<HHMM>_<STORE>[_suffix].eml` (local send time, CEST +0200).
Generator: `generator/emails_de/` (`mun01.py`, `ber01.py`, `zrh01.py`, `stm01.py` hold the hand-written bodies,
`build.py` wraps them into .eml, `check.py` checks for repeated sentences). Rebuild with
`.venv/bin/python generator/emails_de/build.py`.

Suffixes: `_dup` = double send, `_re1/_re2` = reply depth (corrections sent as replies get this too),
`_am` = new thread opened by the area manager (Stefan Wagner), `_ooo` = auto-reply, `_fwd` = forward.
To: `retail-ops-dach@`, Cc: `stefan.wagner@` unless stated otherwise.

| Store | emails | daily closings | open days | extras |
|---|---|---|---|---|
| MUN01 | 50 | 43 | 44 (closed Sundays + Sat 03.10.) | dup, misdirected mail + "wrong list", customer complaint fwd, AM question + answer, correction |
| BER01 | 49 | 42 | 44 (closed Sundays + Sat 03.10.) | correction, AM question + OOO + deputy answer, dup, AM question + answer |
| ZRH01 | 49 | 43 | 45 (closed Sundays, open 03.10.) | AM question + answer, Outlook recall + correction, request to merch, dup |
| STM01 | 52 | 44 (3 are Sat+Sun recaps) | 49 (open 7/7 until 18.10.) | AM question + answer, inventory + pickup mails after closing, AM question + 2 OOO, dup |

## Writers

- **MUN01**: Katharina Huber (SM, Tue to Fri, structured, proper Umlaute, "Liebe Alle / Servus zusammen", "LG Katharina",
  Outlook signature). Florian "Flo" Brandl (ASM, Mon + Sat and the week of 05.10. while Katharina is on holiday,
  telegraphic, writes ae/oe/ue/ss, Denglisch "Traffic/Conversion/Bud", "VG Flo"). Veronika "Vroni" Maier (Senior SA,
  some Saturdays, chatty, Bavarian "Servus beinand / mei / Pfiat eich", emoji, iPhone).
- **BER01**: Jana Schulte (SM, direct, dash lists, "Kd./Kdn.", calls KaDeWe "das Haus", "VG Jana"; on holiday 05.–11.10.).
  Mehmet Aydın (ASM, formal Outlook HTML mails with a KPI table, long signature with disclaimer). Tobias "Tobi"
  Krüger (SA, some Saturdays, lowercase, iPhone).
- **ZRH01**: Swiss Standard German throughout: no ß, CHF with apostrophes (CHF 21'141), Helvetismen (Reisecar, Gilet,
  retournieren, allenfalls, Ferien, "Merci"). Reto Ammann (SM, the same "Tagesrapport" form every time, "Freundliche
  Grüsse"). Lea Baumgartner (ASM, "Hoi zäme", "Liebi Grüess", iPhone on Saturdays). Ying Zhang (Mandarin-speaking SA,
  non-native German, e.g. "Freundliche Grüssen", writes 01.10. and 07.10. during Golden Week).
- **STM01**: Gian-Andrea Caviezel (SM, Engadiner, Romansh greetings "Allegra", "Cordials salüds", "Grazcha fich",
  CHF x'xxx.–). Sabrina Gredig (ASM, practical, handles closing logistics). Nicola Tognina (SA from the Bergell,
  weekends, German mixed with Italian: "ciao a tutti", "va bene", "peccato", "pazzesco", small grammar errors, iPhone).

## Cross-store signals (what the emails show and how to read them)

- **Cold snap 12.–19.10.**: all four stores describe a weather shift with long/warm items, beanies, gloves and missing
  sizes. MUN01: 12.10. rain and 5 °C with conversion at only 5.8 %, 14.10. **first snow** at +72 % with beanie navy
  sold out and Hermine navy/black, Montgenevre grey 5, Maya navy 4 missing, then 15.–17.10. strong, and on 20.10. Föhn
  ends it. BER01: +86 % on 12.10., 17.10. +78 % with beanie white sold out and 4 unmet requests after that.
  ZRH01: 12.10. −83 % (sleet, people came in to warm up, 4 receipts) and then +99 % / +137 % on 13./14.10.
  (snow down to 1000 m). Read the 12.10. drop as a weather-day artefact, not as weak demand. STM01: snow from 12.10.,
  "last burst" 15.–18.10.
- **TIB zipper slider defect** (all reported as "Reißverschluss/Schieber"):
  MUN01 02.10. (Gr. 4, photos attached). MUN01 09.10. forwarded customer complaint: Tib navy Gr. 5 bought 18.09.,
  which matches POS `MUN01-260918-0012`. **This return is not yet in POS**, so the defect is under-counted in POS.
  MUN01 17.10.: Tib Gr. 3 return booked with reason **QUALITY** (not DEF) and without an original receipt. Vroni says
  it is the zipper, so count it as a defect.
  BER01: 28.09. (Gr. 4), 20.10. (Gr. 3), 21.10. (Gr. 5). Jana asks whether to take Tib off the floor.
  ZRH01: 29.09. (×2), 30.09., 01.10. (×2), 03.10. (×2), 12.10. Reto's 01.10. list gives purchase dates that match
  the POS original receipts; the colour of the 16.09. one is a guess.
  STM01: 28.09. (×2). These units were shipped back to the DC on 20.10. in a separate carton marked "Quality".
- **ARNEB fits large**: MUN01 04.09., 05.09., 28.09. (exchange 2→1, staff now advise one size down), 09.10.
  Flo says it is the "4th size return since launch", but email_context has 3, so treat his count as approximate.
  ZRH01 14.09. (4→3) and 05.10. (size 1 still too big, no smaller size exists).
- **Genius POLARIS weak (MUN01)**: launched 24.09. with many try-ons and 1 balaclava sold. Feedback: the oversized
  runs small, so customers size up, and the 2,900 € cape is too expensive. On 15.10. Katharina offers the Cape and
  light-blue Oversized for transfer, and on 19.10. says the balaclava is "the only item that really moves".
  At ZRH01 the capsule is neutral and the balaclava sells in the cold (5× on 16.10.). BER01 does not carry it and
  sends customers to Munich (not a lost sale in the data).
- **MAIRE black**: no stock in 0/1/2 at MUN01 from about 26.–30.09., at BER01 from 22./24.09. and at ZRH01 0/1 from
  28.09. Unmet requests come almost daily, and the deliveries on 01.10. and 15.10. carried no black Maire. The DC
  was back on 16.10., but the stores only get it with the shipments of 22.10. (MUN01, 35 pcs; BER01, 15 pcs) and
  23.10. (ZRH01, 20 pcs). The emails of 20./21.10. quote these counts correctly from the delivery notice.
- **Golden Week (ZRH01, 30.09.–08.10.)**: Chinese share 33–53 %, coach groups from Lucerne, tax-free forms,
  Ying translating. Record day Sat 03.10. (CHF 61,273), reported only on Monday 05.10. at 08:23.
  Long unmet lists: Bady black 0, Rosiere black 3 (4 requests between 03.10. and 08.10.), Maire black/beige/off-white,
  Hermine, Montgenevre navy.
- **Oktoberfest (MUN01, 19.09.–04.10.)**: Wiesn Saturday 19.09. +34 %, Italian weekend 26.09. (−13 %, very busy).
  Wiesn weekdays are below budget: tourists browse and don't buy down jackets at 20 °C. On 05.10. the city is empty
  after the Wiesn (−50 %).
- **Middle-East clients (MUN01)**: 03.09., 07.09., 21.09., 10.10. (Emirates, autumn holidays, mostly small items),
  20.10. ZRH01/STM01 also mention guests from Dubai, Riyadh and Abu Dhabi.

## Planted noise / traps per store

### MUN01
1. **19.09. gross vs net**: Flo reports "67,3k (brutto)" and "+59 %" against the net budget. The correct KPI is net
   56,580 € against 42,340 € (+33.6 %). The same mail was sent twice (`_dup`, one minute later).
2. **22.09. missing**: no mail. Katharina adds the figures in the 23.09. mail (16.1k / 22.6k, correct).
3. **09.09.** was sent the next morning (10.09. 08:47, "laptop did not boot").
4. **13.10.** subject says "Tagesabschluss 12.10.2026" (copy-paste), but the content is 13.10.
5. **16.10. typo**: "Umsatz 16,2k vs Bud 45,7k → +34 %" (the percentage is right). Correction at 20:09: 61.2k
   (KPI 61,245).
6. **08.10. 17:12**: the internal shift plan went to the ops list by mistake, followed by "Sorry, falscher Verteiler".
   It has no business signal.
7. **14.10.**: Stefan asks how much Hermine and beanies they need, and on 15.10. Katharina answers with **estimates**
   (Maire black 0–2 "at least 10"). These are opinions, not measured demand.
8. 26.09.: Vroni says "Maire black 00 we never had". This is an unverified staff claim.
9. 05.10.: Flo says the last 2 black Maire sold were "Gr. 3 and 4". The sizes are unverified (POS has the truth).
10. The deliveries of 05.09. and 12.09. were 2 days late, which matches logistics. The 21.10. "waiting list of 11
    customers" for black Maire is an anecdotal number.

### BER01
1. **Metric definition trap**: Mehmet's tables have "Frequenz Shop" (= door counter, matches KPI visitors) and
   "Frequenz Haus (lt. KaDeWe)" (31k–61k, the department-store total). Never use the second as traffic or as a
   conversion denominator.
2. **24.09.**: Jana writes 17.9k and corrects it to 19.7k at 21:03 (KPI 19,730).
3. **25.09.** was sent the next morning (warehouse Wi-Fi down).
4. **Missing 15.09.** (the 16.09. mail says "ca. 8k", KPI 8,130) and **07.10.** (the 08.10. mail says "ca. 13,7k",
   KPI 13,740).
5. **14.09.**: 3 accessory returns are booked as SIZE in POS but were really "didn't like it". Return reason codes
   are unreliable.
6. **12.10.**: double send (`_dup`).
7. **01.10.**: the body only says "siehe Anhang", and the figures are in the xlsx.
8. **06.10.**: Stefan asks Jana, gets an out-of-office reply, and Mehmet answers: "2–3 black Maire requests per week,
   mostly size 0 and 4". This matches email_context. His statement "0 and 2 at zero since 22.09." is slightly off
   (size 2 is zero from 24.09.).
9. **18./19.10.**: Stefan asks whether BER01 can give beanies to MUN01. Jana says no: white is at 0 and navy has
   3 left; 25 beanies arrive on 22.10. (matches shipment SHP02600514). There is no transferable stock.
10. **26.09. "Marathon weekend, less traffic in the house"**: anecdotal. The shop door counter (94) is a normal
    Saturday.
11. **14.10.**: brown turtleneck M requested. BER01 does stock brown and received 2 on 15.10., so it is a size
    stock-out, not an assortment gap.
12. **16.10.**: Maya black 8 sold the day after the 15.10. delivery (5 black Maya in that delivery). Rosiere olive 7
    was requested 3 times (10., 13., 15.10.).

### ZRH01
1. **13.10. VAT trap**: the first mail says "CHF 46'832 inkl. MWST" (gross, 8.1 % VAT), followed by an Outlook
   recall message ("Rückruf: …") and a corrected mail with net CHF 43,323 (KPI).
2. **30.09.** subject says "30.10.2026" (wrong month). Reto points it out in his 01.10. reply.
3. **Missing 08.09.** (mentioned on 09.09. without figures) and **22.09.** (the 23.09. mail gives CHF 18,533,
   which is correct).
4. **Sat 03.10.** was reported on Mon 05.10. 08:23 ("Nachtrag"), not on the day.
5. **09.10.**: the body only says "Rapport im Anhang", and the data is in the xlsx.
6. **16.10.**: double send.
7. **15.10.**: Reto asks merch for replenishment and suggests a transfer from St. Moritz. STM01 stock went back to
   the DC on 20.10., so the stock is available from the DC, not store-to-store.
8. **12.10. −83 %**: a sleet day with no unmet requests recorded. It must not be read as a demand collapse.
9. **ILVARO powder pink**: requested 26.09. (00) and 14.10. (size 1, the customer showed a photo of the Korean
   singer). 3 pieces arrived on 16.10. and were tried on but not sold by 17.10. There are weak spill-over signals in
   Europe.
10. 10.09.: Reto writes "Arneb 7 not in our assortment". This is an unverified staff claim, and the request itself
    is a real unmet request.

### STM01
1. The store is open every day (no closed weekday) until **18.10.**, closed for the Zwischensaison from **19.10.
   to 03.12.**, and reopens Fri **04.12.2026**. The 18.10. mail is the official closing announcement.
2. **Weekend recaps**: Sat+Sun in one mail sent on Sunday for 05./06.09., 19./20.09. and 03./04.10.
   Single weekend days are reported separately the rest of the time.
3. **Missing 15.09.** (in the 16.09. mail: CHF 1,895) and **30.09.** (in the 01.10. mail: CHF 5,910 + requests).
4. **Negative or zero days**: 01.09. −60 (return larger than sales), 02.09. zero sales (no KPI row), 13.09. CHF 169,
   24.09. −2,540 (returns of 2 Insolux GIFT + Montgenevre SIZE). The sign is correct.
5. **PEYRE (ski jacket)**: sizes 2/3/4 are repeatedly unmet (05.10., 08.10., 16.10. ×2, 17.10. ×2).
   The 09.10. delivery brought sizes 2+3, and the 16.10. delivery brought one size 4, which sold within an hour.
6. **14./15.10.**: Stefan suggests staying open until 25.10. because of the snow, and Gian-Andrea declines
   (holidays booked, hotels closed, lifts open end of November).
7. **19.10.**: inventory mail with a CSV (cp1252, `;` separator): 21 cartons of about 310 pieces, plus 2 defective
   Tib in a separate "Quality" carton. 20.10.: GEODIS pickup done, store locked.
8. **21.10.**: Stefan asks STM01 to ship Peyre/Chamonix L directly to Zürich and gets 2 auto-replies (Sabrina on
   holiday, store mailbox "closed until 3 December"). Correct reading: the goods are already on the way to the DC
   and the Zürich request must be served from the DC.
9. **17.10.**: double send from iPhone.
10. Repeated unmet requests: Maire off-white 00 3× (31.08., 07.09., 24.09.; the 24.09. mail says "third"),
    Ambrine brown 3× (12.09., 17.09., 02.10.).
