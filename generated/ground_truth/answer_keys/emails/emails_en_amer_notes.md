# Store closing emails - USA/Canada group (emails_en_amer) - answer key

Stores: NYC01, NYC02, MIA01, BHS01, ASP01 (American English), TOR01 (Canadian English with Québécois French touches, CAD).
Output: `generated/sources/store_emails/<STORE>/YYYYMMDD_HHMM_<STORE>[suffix].eml` (local send time of the store;
suffixes `_dup` duplicate send, `_corr` correction, `_re1/_re2` replies, `_fwd` forward, `_ooo` auto-reply).
Bodies are hand-authored in `generator/emails_en_amer/bodies_<STORE>.py` (each email dict has a `covers` field =
business date(s) it reports on); wrapped by `build.py`; `check.py` checks forbidden strings, coverage and repeated sentences.
Per-store fragments also live in `generator/emails_en_amer/notes_<STORE>.md`.

File counts: NYC01 60, NYC02 55, MIA01 58, BHS01 53, ASP01 56, TOR01 55 (total 337).

Cross-store conventions / consistency
- Distribution lists: retail-ops-usa@ (US) / retail-ops-canada@ (TOR01); cc Lauren Mitchell (area manager USA & Canada, New York).
- Lauren is in Toronto Oct 14-16: identical Outlook out-of-office in NYC01 (10/14) and ASP01 (10/15); TOR01 reports her store visit on 10/15. She still answers BHS01 from her phone on 10/17.
- NYC02 POS outage 10/6 is also mentioned by NYC01 (SoHo sent two clients up to Madison).
- Transfer requests between stores (NYC01<->NYC02<->BHS01, MIA01->Madison, BHS01->Aspen, TOR01->NY) are mentioned in emails only; no transfer is confirmed.
- Mrs./Ellen Feldman appears as a Madison VIC (NYC01) and an Aspen local with a Red Mountain home (ASP01): plausibly the same client, not a planted signal.
- Dates in subjects use US formats (M/D, MM.DD); TOR01's Aisha uses DD/MM; Émilie uses French day/month words. Amounts: USD for US stores, CAD for TOR01, mostly net, rounded; documented exceptions (gross, typos) are listed per store.
- Every store has 1-2 business days without their own email (see "Traps"), which are usually recovered in a later email.

## NYC01 - New York Madison Avenue flagship (60 files)

Files: 50 closing emails (incl. one Sat+Sun recap and one next-morning catch-up), 1 duplicate, 1 correction, 3 Lauren Mitchell mails + 3 store answers, 1 Lauren out-of-office, 1 forwarded client email. Keys = MMDD (+ suffix).

Writers
- Rebecca Stein (SM, Outlook): semi-fixed recap with headers Sales / Traffic & Conv / Clienteling / Product / Ops, filled unevenly; numbers like "$52.4K vs $37.2K plan (+40%)", MTD, LY comp. Same signature + confidentiality disclaimer every time (habit line). Works Tue-Sat (+ Columbus Day Mon 10/12). Subject drifts "Madison EOD 9/3" -> "NYC01 EOD Recap | Tue 10/6" from 10/6. Adds "Units / Top 3 / Misses" from 10/2 after Lauren asks (lm1002). One iPhone mail (10/8, "See attached" + xlsx form).
- Marcus Bell (ASM, iPhone): lowercase dash lists, dry humour, rants about UNGA, max one emoji (9/7, 9/21). Closes Sun/Mon plus Rebecca's days off (8/31, 9/2, 9/11, 10/9, 10/13). Subjects "eod sun", "Madison closing 9/21", "closing mon 10/5". Picks up a "misses:" line in October. Fast sender (18:30-19:45).
- Priya Raman (senior client advisor): closes when both managers are off (9/17, 10/1, 10/14); always late (22:00-22:50); long chatty paragraphs, clients by name/initial (Caroline W., Mrs. A, Mrs. Feldman, Jonathan B.). 10/1 sent from the store mailbox (her Outlook locked). Forwards a VIC email 10/16.
- Lauren Mitchell (area manager USA/Canada, NY): replies 9/22, 10/2, 10/20; OOO 10/14.
- Also mentioned: Dana (SA, invented).

Planted signals
- UNGA week Mon 9/21-Sat 9/26 (keys 0919 heads-up, 0921, lm0922, 0922re, 0922, 0923, 0924, 0925, 0926 wrap): frozen zones 60th-72nd, motorcades, barricades on Madison/Park, Secret Service at The Mark / Carlyle / Pierre, drivers unable to reach the door, cancelled appointments. 0926 gives the week: ~$193K vs ~$341K plan (-$150K), "plan/forecast treated it like any other week". 9/23 (-4%) is a partial relief day (zone lifted ~1pm, postponed appointments came in). 9/21 also Yom Kippur (Rebecca: mostly UNGA). Recovery Sun 9/27 (key 0927, +4%, 481 visitors).
- Rosh Hashanah: Fri 9/11 quiet (0911), Sat 9/12 -30% / Sun 9/13 -44% (0913 recap, "plan didn't have the holiday").
- Labor Day weekend: Sat 9/5 +22% (0905), Mon 9/7 -41% (0907).
- FW26 campaign from 9/15: VM installs windows night of 9/14 (0914, cc vm-team), live 9/15 (0915). Clients mention ads 9/16, 10/10, 10/19. Real lift small: Rebecca 1020re "hard to see, maybe a few %".
- POLARIS (Genius) launch Thu 9/24 (key 0924, sent 9/25 morning): 1 cape (white) sold, 8-10 try-ons, "boxy but tight in the shoulders", price too high; 0 on 9/25; 1005 oversized jacket never sold; 1021: balaclava returned for SIZE, Rebecca proposes moving units to another store / not reordering.
- TIB zipper slider defect (DEF): first 9/28 (0928, size 3), 9/29 (6), 9/30 (6), 10/1 x3 (4,6,2, Priya), 10/2 x2 (4,2), 10/3 (4), 10/4 (2), 10/8 x2 (3,3, in xlsx), 10/10 (5), 10/11 (4), 10/17 (1). Running count in mails reaches #15 = matches POS. Batch "07/26" on label, units held, store asks for RTV/recall instruction (1002re, 1010). TIB still selling in non-defect sense (10/6 navy x4, 10/10 cream x4, 10/14 black x4).
- ARNEB runs large: early comments 9/5; exchange 2->1 on 9/10, 5->4 on 9/20 and 10/18; returns for size 9/24 (4), 10/2 (4), 10/3 (5); staff now size everyone down (0911, 1010, 1018).
- MAIRE black: strong sell-through 9/9 (x7, VIC with daughters, cc merch), black 3 sold out 10/2 (1002) -> unmet 10/3 (size 3), 10/4 (real size 4, see trap), 10/8 (3), 10/15 (1 and 4; black 1 now zero), 10/16 (3 + VIC Ellen Feldman, fwd 1016fw), 10/17 (0/1/3 all out), 10/20 (0 and 3). Waitlist 3 names (10/7) -> 5 names (10/21). 10/21 delivery: one black 1 came in, still nothing in 0/3. DC says nothing before mid-Oct (1005).
- KARAKORUM: black 3 zero from 9/12 (0913), still zero 9/15, lost sale 9/16. Navy 3 x2 on 10/10, navy 3 + navy 6 on 10/11 (1011), plus Karakorum 5 return for COLOUR (wanted navy).
- CHAMBRE black 4 x2 on 10/8 (only in xlsx attachment of key 1008). CHAMBRE cream 4 on 9/24.
- Other unmet requests mentioned: Valbourg cream 1 + logo cardigan black XS (9/4), Valbourg black 1 (9/5), logo cardigan black XS again (9/7), Maire beige 4 (9/8), Maya navy 7 (9/12), cable knit black S x2 + Maya black 1 (9/13), Trailgrip W cream 35 (9/15), Bady cream + wool turtleneck brown L (9/17), Maya navy 1 (9/18), Ambrine black 2 + Valbourg black 4 (9/19), TIB cream 6 (9/25), Rosiere olive 6 (9/26), Maya olive 7 (9/30), Ilvaro pink 1 (10/6), Montcla black 1 (10/10), Hermine navy 3 (10/13), logo tee white XS (10/14), Hermine navy 1 (10/16), Ilvaro black 00 / cable knit black XS / crewneck black XS / Insolux cream 38 (10/17), Ecrins black 2 + polo black XXL (10/18).
- ILVARO pink / K-pop: first ask 10/6 with a TikTok of the singer in Paris (store only had pink in 00 and 3); 10/13 two girls ask for "the pink one from tiktok", one buys black.
- Deliveries: 9/18 arrived 2 days late (planned Wed 9/16), Arneb 3/4 missing for two days (0918). 10/12 one day late because of the holiday (1012). Others on time; 10/21 314u biggest of the season.
- Big days: Sat 10/10 $115.9K (weather + appointment block, M. family ~$18K), Sat 10/17 $116.7K record (110 units, crewnecks to college crowd + Brazilian family), Fri 10/16 $97.3K, Mon 10/19 $96.0K.
- Cross-store: 10/6 SoHo POS down in the afternoon, two clients sent up to Madison (1006); transfer asks to SoHo/BH (0908, 0913, 1016).
- Month closes: Sept ~$1.28M vs $1.53M plan (-16%), comp ~+27%, "-6% without UNGA" (0930). Oct MTD 10/21 ~$1.49M vs $1.52M.

Traps / noise (with correct reading)
- Tue 9/1: no email at all, never recovered. KPI: $27.9K vs $27.8K plan.
- Sat 9/12: no own email; covered by Marcus's Sun recap "sat + sun recap" (key 0913) with both days.
- Thu 9/24: forgotten, sent Fri 9/25 08:52 (key 0924, subject "Madison EOD 9/24 - sorry, late"). Business date is 9/24, not 9/25.
- 9/7 (key 0907): Marcus writes "23.1k vs 38.9k LY"; 38.9K is the PLAN. LY same day was ~$23.8K (flat comp, not -41%).
- 9/8 (key 0908): Rebecca reports $52.4K; KPI net is $51,975 ($52.0K). Plan $37.2K and +40% are right.
- 9/16 (key 0916): subject says "Madison EOD 9/15" (copied); content is Wed 9/16 ($42.5K). 9/15 has its own mail (0915).
- 9/17 (key 0917): Priya says the Bady request was cream in "00"; the actual unmet request was BADY off-white size 0.
- 10/4 (key 1004): Marcus types $54.1K; correction 18:58 (1004c, suffix _corr): $45.1K, -37% vs plan.
- 10/4 (key 1004): Marcus calls it "maire black 3 again"; the actual request that day was MAIRE black size 4 (size 3 was the zero-stock size).
- 10/7: duplicate send (1007d, suffix _dup, 2 min later, identical body). Count once.
- 10/8 (key 1008): body only "See attached"; all facts (incl. CHAMBRE black 4 x2 and 2 TIB DEF) are in NYC01_closing_form_1008.xlsx.
- 10/11 (key 1011): sent to retail-ops-canada by mistake (autocomplete); it is a NYC01 email, not TOR01.
- 10/14 (key 1014): Priya's "$56.8K on the register" is GROSS (before returns: Maire 0, Bady 1, crewneck). Net in KPI is $53.1K (-14% vs plan, not -7%).
- 10/19 (key 1019): Marcus credits the +59% Monday mainly to the campaign. Wrong: driver was two VIC appointments (~$31K, Mrs. H: three Montcla + cardigans) plus the first properly cold Monday; Rebecca says so in 1020re ("campaign lift hard to see, maybe a few %"). Do not use 10/19 as campaign evidence.
- 9/24 POLARIS: "one cape sold" is correct (POS: POLARIS CAPE white x1). The later "one balaclava sold" (1021) is the store's statement; only the 10/21 SIZE return is in the context data.
- Lauren OOO (lm1014) is an auto-reply, no store facts. The lm*/re threads and 1016fw carry no daily KPIs (covers = []).
- Comps quoted are rough and only directional (+50s early Sept, ~+27% Sept close, ~+39% MTD 10/7, ~+50% MTD 10/21); MTD figures are rounded.

## NYC02 - New York SoHo (55 files)

Writers
- Tyler Brooks (SM): iPhone, lowercase, emoji-heavy, numbers in "k", short; closes most Tue-Sat.
- Ana Gutierrez (ASM): Outlook, fixed mini-form SALES / TRAFFIC / MISSED / NOTES + signature, occasional Spanish ("ojo"); data-precise; closes Mon, Sun and Tyler's days off; handles follow-ups.
- Jordan Lee (SA/keyholder): a few Sundays (9/6, 9/13, 9/27, 10/11), polite, full sentences, unsure about the process.

Planted signals
- POS outage Tue 10/6 14:10-17:40 (key 1006): manual slips keyed in on 10/7. System shows 10/6 $12.6K (-61%), 10/7 $50.1K (+60%). Correct split per store (keys 1007, 1007re2): 10/6 ~$31.5K / 20 trx, 10/7 ~$31.2K / 12 trx (12 slips, $18,930). Also ~4 walkouts (~$5-6K lost demand) not in any system. IT ticket INC0048213.
- ILVARO spill-over: first hint 10/2 (key 1002 "pink Moncler from the K-pop show"), explicit 10/3 (Yoon Ha-eun / LUMIERE, TikTok), IG DM forwarded to clienteling 10/3 (1003fwd), black/cream Ilvaro sold as substitute (10/3 cream x3, 10/8 black x4), unmet Ilvaro cream 3 (10/4, 10/8, 10/21), cream 0 (10/7), black 0 (10/9, 10/10). Pink never allocated to SoHo. Ilvaro black x3 on 9/21 is pre-hype normal demand.
- MAIRE black 2 out from ~9/23 with repeated asks (9/26 x2, 9/27, 10/4, 10/5 x3, 10/10, 10/11, 10/16, 10/17, 10/18) then 0 and 1 also out (10/10-10/12); 10/14 three asks in 0/1/2; waitlist grows 5 -> 9 -> 11-12 names. Customers substitute with beige only partially (10/5).
- TIB zipper defect: 9/29 first (logged as quality), then DEF returns 9/30, 10/1 x3, 10/3 x4, 10/10, 10/13 x2, 10/16, 10/17, 10/20; Ana quarantines 4 suspicious units 10/2; store asks for RTV instruction repeatedly. Store count "~15 since end of Sept" is right (14 DEF + 1 coded QUALITY).
- Other stock-outs with lost asks: Bady black 2 (8/31-9/5), Logo cardigan black S/XL (early Sep), Montgenevre navy 3/4/5 (mid Sep), Flammette black 0/3 (Sep), Tib black 5 (late Sep-10/3), Logo tee black M/L/XL (from 9/29), Montcla black 5 (from 10/13).
- POLARIS launch 9/24: tried on, "small in the shoulders", "$$$" (key 0924).
- Campaign: new windows 9/14-15, IG mentions 9/18; staff unsure it converts.
- Labor Day weekend (9/5-9/7) and Yom Kippur (9/21) soft days; Korean shoppers late Sep/Oct asking for black.

Traps / noise
- 9/8 (Tue): no email. Partially covered in 0909 ("tuesday was like 17-18k"; real $17.6K).
- 9/12 (key 0912): Ana writes $41.2K = gross before returns; net in KPI is $38.6K.
- 9/19 has no own email; covered by Sat+Sun combined recap sent 9/20 (key 0920), which also contains a self-corrected confusion about which day a Bady return happened.
- 9/24 (key 0924): Tyler says "0 sold i think" for POLARIS; POS shows 1 POLARIS CAPE sold that day.
- 9/25: duplicate send (0925dup, 2 min later, identical).
- 9/30 (key 0930): Tyler typo $38.3K (real $33.8K) and "Sept ~815k MTD" which wrongly includes Aug 31. Correction next morning by Ana (0930corr): $33.8K; Sept ~$784K vs ~$880K plan.
- 10/6 (key 1006): client asking "Bady pink 4" thought it was the TikTok Ilvaro; correct reading: unmet request is BADY powder pink size 4, not ILVARO.
- 10/13 (key 1013): subject says "Mon 10/12" but the content is Tue 10/13 (copy-paste); 10/12 has its own email.
- 10/15: no email that evening; sent next morning 10/16 09:14 ("sorry late"), covers 10/15.
- 10/11 (key 1011): Jordan says "we never had brown here I think" for Ambrine chocolate brown 2: speculation, not verified.
- 10/16 (-65%): store has no explanation; nothing in scenario explains it (noise day).

## MIA01 - Miami Design District (58 files)

Writers
- Daniela "Dani" Restrepo (SM): Colombian, warm, Spanglish ("hola", "ay", "gracias", "nada"), $ figures "vs plan", Outlook signature (sometimes omitted), closes most Tue-Sat; vents about assortment.
- Kevin Hall (ASM): iPhone, lowercase, sports emoji/refs (Dolphins, Heat), short, closes Sun/Mon + Dani's days off. Numbers error-prone.
- Valentina "Vale" Soto (SA/keyholder): bullet list, nervous about numbers, closes some Sundays (9/6, 9/13, 10/4, 10/11).

Planted signals
- AC failure Thu 9/3 - Sat 9/5 (keys 0902 noise warning, 0903 with 2 thermostat photos IMG_2207/2209 + ticket FAC-31877, 0903re1 Lauren approves portable units, 0903re2, 0904, 0905): 86°F inside on 9/3, walkouts, portable units from 9/4 16:30, compressor replaced Sat 9/5 15:00, portables returned 9/7. Sales 9/3 -69%, 9/4 -56%; 9/5 back on plan thanks to portables.
- Low outerwear / wrong assortment: heat (90s°F), outerwear only bought for trips (Europe, Switzerland, Aspen/Vail, Toronto); repeated unmet knit/jersey sizes (logo cardigan navy M/L/XL 10/9-10/17, turtleneck black L, padded cardigan L, cable knit various, logo tee navy S/M, hoodie grey XS/M, crewneck XL/XXL). Explicit escalation to merch on 10/13 (key 1013). Delivery 10/11 "only outerwear", 10/18 "some tees finally".
- Latin American clients: Brazilians (9/7 Brazil Independence Day + Labor Day, +60%; 9/27 Brazilian group to Switzerland +92%), Mexicans (9/16 Monterrey family), Venezuelan regular (Ambrine black 1, 9/17), Argentines/Colombians (9/26).
- Hurricane-season chatter 9/25-9/30 (tropical wave near the Bahamas, NHC 50%, clients cancel appointments, storm turns north). Door counts on those days are normal (51-62); the sales drop 9/29-9/30 is low conversion, the storm is only partially to blame. No actual closure.
- POLARIS weak: launch 9/24 tried on by 4, none sold ("small in the shoulders", price); first Polaris sale 9/27 (oversized), balaclavas 9/29 and 10/10; unmet Polaris cape XXL 10/5.
- TIB zipper defect: 9/30 two DEF returns ("slider opens in the middle").
- ARNEB: staff aware it runs big (10/1 advice), sale sized down 10/10, return 10/16 (Arneb 4 too big).
- Unmet outerwear asks mentioned: Maire navy 1/2/3, Maire black 1 (9/29, 10/11, 10/19) and 0/1/2 out by 10/20, Ambrine black 1 (9/17, 9/19), Flammette black 0/1 (9/28, 10/1, 10/2), Insolux black 38/39, Karakorum black 6/7/1, Maya navy 2/3/1.
- ILVARO: client returns Ilvaro 10/9 because she wants the pink one seen on TikTok (store never received pink).
- Campaign: Instagram only, no billboards in Miami (9/15); new FW26 windows 10/14-10/15.

Traps / noise
- 9/13 (key 0913): Vale writes plan 13.4K then doubts it; real plan is $12.4K.
- 9/21 (Mon): no email; mentioned in 0922 as "around $4K" (real $4.1K).
- 9/28 (key 0928): Kevin writes "+118% vs LY"; that is vs plan (budget $10.6K), not LY.
- 9/30 (key 0930): Sept "around $310K vs ~$355K plan" is correct (Sept only).
- 10/2: duplicate send (1002dup).
- 10/4 (key 1004): Vale's email only says "see attached" with a CSV closing form (date in MM/DD/YYYY); Lauren asks for the numbers in the body; Vale answers (1004re2).
- 10/8 (keys 1008wrong, 1008oops): internal staff schedule sent to retail-ops by mistake, followed by "please ignore". Contains no sales data (mentions Art Basel clienteling list).
- 10/10 (key 1010): Kevin writes $28.0K; correct is $20.8K (Dani's correction next morning, key 1010corr). Kevin also implies above plan; it was slightly below.
- 10/13 (key 1013): Dani says October is "around 40% under plan"; real MTD at 10/12 is ~-26% ($134K vs $180K). Exaggeration.
- 10/14: no own email; combined in 1015 (sent 10/15) with both days.
- 10/16: "2 Ilvaro black to the same girl, sizes 1 and 2" is the store's reading; POS just shows 2 units.

## BHS01 - Beverly Hills Rodeo Drive (53 files)

Writers
- Jennifer Kim (SM): Outlook, fixed numbered form "1) Sales 2) Clienteling 3) Product 4) Ops", subject "BH Rodeo - EOD MM.DD", signature + legal disclaimer, discreet about celebrities (initials, "our friend from the HBO series"). One HTML email with WTD table (10/3).
- Luis Ortega (ASM): iPhone, lowercase run-on, heat/Rodeo/LA references, 😎🥵🔥 emoji; closes Sun/Mon and some Saturdays.
- Sofia Marchetti (Senior Client Advisor): long, pulls/stylists-focused; closes 9/10, 9/21, 10/14.

Planted signals
- Heat wave Tue 9/8 - Sat 9/12 (keys 0907 warning, 0908, 0909, 0910, 0911, 0912): 99-104°F in BH, 105-108°F Valley, appointments cancelled, no outerwear try-ons, Rodeo empty midday; 9/12 Saturday -65%. Heat breaks Sun 9/13 (84°F). 9/9 only on plan thanks to a single ski client.
- Stylist pulls / celebrity: stylist K. (HBO series) pulls 9/4-9/8, 9/10-9/16 (bought a Maya black 9/16); R. Studio editorial hold 9/10; Emmys week pulls 9/18, returned 9/21 with makeup on a Bady collar (cleaning charged to stylist); Polaris sales mostly to stylists (9/29 oversized for a music video, 9/30 cape, 10/8 cape); studio wardrobe one-off buy 10/16 (~$12K: Maire off-white x4 + padded cardigan black x3) explained in thread 1016re1/re2.
- Ski-trip outerwear: Peyre red (9/9 Aspen, 9/25), Valbourg off-white/black (9/15 Deer Valley, 9/16, 9/22, 9/29), Insolux (9/1 Jackson Hole, 10/5, 10/7, 10/13, 10/15 x3, 10/18, 10/21), Gstaad/St. Moritz trips (9/3, 9/28); asks for transfers from Aspen (Peyre red 7, 9/21); unmet Valbourg black 00 (9/11), off-white 1 (9/19), black 4 (10/9), Insolux 37/35/38.
- ARNEB runs large: exchange 6->5 (9/6); size 3 keeps being asked (9/5, 9/18, 9/19) because staff advise sizing down -> request to allocate more 3s (key 0918).
- MAIRE black: asks for 3/4 from 9/26, 0/3 9/27, 3 on 10/8, 1 on 10/11/10/13/10/18, 0/3 on 10/15, 2 on 10/16/10/20; out in all sizes 0-3 by 10/14, Sofia has 6 clients waiting.
- Other repeated misses: Maya navy 5 (9/11, 9/17, 9/26 "4th time"), Chambre black 2/4/0 (10/5-10/14), Montcla navy 2/4/3, knit sizes (turtleneck black XS/M, polo navy M, cable knit various).
- TIB zipper defect: 10/1 (first one), 10/3 (second).
- POLARIS launch 9/24: zero sold launch day ("fits like a kids size", "for $3K I expect more"), then 5 units total, all stylist-driven.
- ILVARO pink asked by a stylist 10/21 (never allocated to BH).
- Campaign billboard on Sunset seen 9/14; clients ask about "the jacket in the ad" 9/15.
- Delivery due 9/22 arrived 9/23 (3 days late vs original ASN).
- Emmys Sun 9/20 + Yom Kippur eve: -84%.

Traps / noise
- 9/2 (key 0902): net $1.0K because returns offset sales; gross was higher. Jennifer's note about the AC "struggling" is unrelated to the MIA01 AC failure.
- 9/15: duplicate send (0915dup).
- 9/24 (Thu): no own email; covered by the 9/25 email ("~$11K, 5 trx", real $11.2K).
- 10/1 (key 1001): subject reads "EOD 09.31" (non-existent date); content is Thu 10/1.
- 10/3 (key 1003): HTML table (WTD 9/27-10/3) correct; Mon 9/28 shown as +35% (file +36%, rounding).
- 10/5 (key 1005): Luis reports "22.1k on 21 plan" = gross before 4 returns; net in KPI is $18.0K (-14% vs $21.0K plan).
- 10/7 (key 1007): Brazilian group's ski destination ambiguous ("Bariloche? they said Aspen in January").
- 10/16: +46% is a one-off studio buy, not a trend (confirmed in 1016re2).
- 10/17 (Sat): no own email; combined Sat+Sun recap from Luis on 10/18.

## ASP01 - Aspen resort (56 files)

Writers
- Hannah Novak (SM): Outlook, chatty small-town tone, weather/snow obsessed, names local clients (Mrs. Feldman of Red Mountain, Mrs. Castellano), subject "Aspen closing <day> M/D"; signature sometimes, sometimes just "Hannah".
- Chris Delgado (ASM): iPhone, ultra-terse lowercase, signs "-C" sometimes; closes Sun/Mon; forgets to send (9/14).
- Megan Liu (SA/keyholder): eager, fixed mini-form (Sales/Transactions/Traffic/Asks), asks process questions (ski allocation, new hours); closes 9/10, 9/18, 9/22, 10/2, 10/16; forgot 10/6.

Planted signals
- Shoulder season: town empties after Labor Day; restaurants announce closures, Gondola stops (9/8); leaf-peeper weekends 9/12-9/27 bring traffic but not sales (9/19), except Sun 9/20; reduced hours Mon-Wed 11-5 from 10/12 (thread 0928re1/re2, confirmed 1003, applied 1012: email sent 17:31). Seasonal hiring (J-1 from Argentina, offers 10/21).
- Zero-sales days: Mon 9/7 (Labor Day, key 0907 "donut", 18 visitors) and Mon 9/28 (key 0928, 17 visitors). Both have no row in store_daily_kpi; the emails confirm the store WAS open (not a data gap). Lauren's reply 0928re1 refers to both.
- Negative net days (returns > sales): 9/2 (-$525, polo gift return), 9/9 (-$1.6K, Ecrins 4 gift + Trailgrip 43), 9/10 (~-$900, Valbourg 1 colour return), 10/1 (-$1.3K, Arneb 3 quality return).
- First snow: forecast talk 10/8, snow on top of Ajax 10/12-13 (down to ~10,000 ft), Independence Pass closed by snow/ice morning of 10/14, 28°F, snowmaking tests; clients asking for ski pieces right away.
- Ski allocation gap: Peyre black down to 1 (9/17), sold out 9/25, asks 9/29 (women's fit) and 10/9 (size 3); Valbourg black 2 asked 10/10; Chamonix L out; Megan's stock count 9/18 (41 down jackets vs 6 ski pieces); last year allocation arrived Oct 28; formal request to merch 10/15 with xlsx wish list (key 1015merch). Opening day Thanksgiving Nov 26.
- MAIRE: black 2 asked 10/9, black 1 10/11, black out in all sizes 0-3 by 10/18; navy 1/2 asked 10/9, navy 00 (9/22, 10/7), navy 4 (10/20).
- ARNEB: return 9/30 (too big, no exchange), 10/1 (quality, seam); sale 10/16 sized down one (4 and 5 instead of 5 and 6) fit perfectly.
- TIB zipper defect: 9/30 (first), 10/4 (second).
- POLARIS not allocated to Aspen; manager says it doesn't fit the clientele (9/24).
- Pink ILVARO asked 9/5 (before the K-pop moment; no pink allocated). Brown Ambrine asked 9/4 (Dallas client).
- Campaign: no effect felt in the valley (9/15).
- Door counter offline 10/9 (key 1009): door_counter_daily has no row and KPI visitors is empty for ASP01 2026-10-09; Hannah estimates ~25 people.

Traps / noise
- 9/14 (Mon): no email; Hannah gives the number in 0915 ($3.0K, correct).
- 9/22 (key 0922): Megan writes "$35K"; correction 19 min later (0922corr) = $3.5K (KPI $3.5K).
- 9/30 (key 0930): "September closes around $97K vs $148K plan" correct for Sept only (excl. Aug 31). "Out of navy beanies" is the store's claim (unmet beanie navy TU).
- 10/6 (Tue): no email; 1007 says "a one-beanie day ($300)", correct.
- 10/15: Lauren's out-of-office auto-reply (1015ooo, "traveling Oct 14-16 (Toronto)", same text as in NYC01) in reply to the merch request.
- 10/18: duplicate send (1018dup).
- 9/27 (key 0927): "Chinese couple bought the Valbourg for Niseko" - store anecdote.
- 10/12 (key 1012): "2 trx" but lists 4 items (2 tickets with 2 items each): consistent with KPI (2 receipts, 4 units).

## TOR01 - Toronto Yorkville (55 files, amounts in CAD)

Writers
- Émilie Gagnon (SM, from Montréal): English with Québécois French ("pas pire", "bon", "voilà", "ouf", "tabarnouche", "c'est fou", "en tout cas"), French-style space before ":", "!" and "?", non-native slips ("arrived with 1 day late", "1 client asked the Hermine"), subject "Yorkville - closing <d> sept/oct", bilingual signature. On 10/1 she wrote the whole email in French, then added an English version. Forwards use "TR:" and French forward headers.
- Ryan Chen (ASM): iPhone, numbers-first ("Net 44.5K vs 46.6 plan, 17 trx"), subject "TOR EOD MM/DD"; closes Sat/Sun/Mon when Émilie is off.
- Aisha Mohamed (SA/keyholder): Sundays (9/6, 9/20, 9/27, 10/11, 10/18), cheerful, emoji, DD/MM dates in subject (Canadian habit).

Planted signals
- TIFF Sep 10-20: stylist pre-visits 9/8 + memo policy thread with Lauren (0908re1: max 5 pieces/72h, no Genius before 9/24); opening night 9/10 +61%; 9/11 +74% (actress from an A24 film buys Ilvaro black x3, paparazzi on Hazelton Ave); King St Festival Street closure 9/10-9/13; 9/12 photo of the queue (IMG_5512.jpg); memo pulls tracked (7 out, 1 converted); stylist thank-you forwarded 9/21 (0921fwd; actor wore Montgenevre at premiere). Mid-festival dip 9/15-9/17; post-TIFF 9/19-9/20 international shoppers.
- Earlier cold: first cold morning 7°C on 9/23 ("in Toronto we always start before the US"), 2°C morning on 10/17 with 223 visitors. Afternoons still 12-15°C mid-October (10/15) so outerwear purchases are hesitant.
- ARNEB strong in Toronto (compared to Canada Goose parkas, "less bulky"): sales 9/9 x2, 9/24 x2, 10/2 x3, 10/20 x2; always sized down; Arneb black 3 out from mid-Sept (ask 9/16), black 6 asked 10/4, 10/6, 10/9, 5 out by 10/9, black 2 asked 10/16 by a woman; 10/10 return 5 for size. Stock by size on 10/2 in 1002re2 matches stock_eod (1:1, 2:2, 3:0, 4:4, 5:1, 6:0, 7:1). Store asks merch for 3/5/6.
- MAIRE black: strong early Sept (5 sold 9/1-9/2), size 0 out from 9/2, asks 9/13, 9/23, 9/24 (size 4), 10/2 (1, 4), 10/4 (0, 1), 10/6, 10/12 (0, 3), 10/13 (2), 10/16 (2 x2, 4), 10/17 (0 x2, 2, 3), 10/18, 10/19, 10/20; zero in 0-3 from 10/12; waitlist 9 (10/15) then 12 (10/17); no Maire black in the 10/12 and 10/20 deliveries.
- TIB zipper defect: first 2 on 9/28 (sizes 7 and 2), then 9/29, 10/2, 10/3, 10/7, 10/8, 10/9, 10/13 x2, 10/14, 10/18; Émilie checks zippers before selling from 9/29.
- POLARIS: 9/24 one oversized sold, feedback small in the shoulders/expensive, cape not understood; light blue XXL asked by tall client 9/25 (fits like L); 8 pieces sold by 10/15 (summary in 1015), 1 returned (colour, 9/30).
- ILVARO: TIFF-driven sell-out of black 9/11-9/13 (transfer asked from NY), Chinese students with the K-pop photo buy Ilvaro black x3 on 10/2, Ilvaro off-white asked 9/26 and 10/8, return 10/13 (she wants pink).
- Canadian Thanksgiving weekend 10/9-10/12: -25%, -68%, -58%, -33% (cottages); Monday hours 12-5.
- National Day for Truth and Reconciliation 9/30 noted.
- Lauren's Toronto visit 10/15 (matches her out-of-office "traveling Oct 14-16 (Toronto)" seen in NYC01/ASP01); recap of the visit in 1015.
- Cross-border deliveries: 9/1 and 10/20 one day late due to customs broker.

Traps / noise
- 9/15 (Tue): no own email; combined into 0916 ("Tuesday 15: $12.4K").
- 9/21: duplicate send (0921dup).
- 10/1 (key 1001): body first in French with French number format ("19,7 K$"), then English summary.
- 10/3 (key 1003): Ryan's "Same Saturday LY was ~56K" is right (2025-10-04 = $56.4K).
- 10/5 (Mon): no own email; 1006 says "~$21K" (real $21.3K).
- 10/13 (key 1013): Émilie writes $22.9K with no plan; that is gross before 6 returns. Net in KPI is $18.0K (plan $36.6K, -51%).
- 10/19 (key 1019): subject "TOR EOD 10/18" but it is Monday 10/19 (10/18 is Aisha's Sunday email).
- 10/2 thread: Lauren asks "Is that CAD?". All TOR01 amounts are CAD (the KPI file also has CAD local; EUR column at budget rate).
- 9/12 (key 0912): "traffic 189 (record for a Sat this year)" is the store's claim; 9/19 later had 224.

