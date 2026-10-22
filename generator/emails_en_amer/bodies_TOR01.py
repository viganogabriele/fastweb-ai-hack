STORE = "TOR01"

WRITERS = {
    "eg": "Émilie Gagnon <emilie.gagnon@moncler-retail.example>",
    "rc": "Ryan Chen <ryan.chen@moncler-retail.example>",
    "am": "Aisha Mohamed <aisha.mohamed@moncler-retail.example>",
    "box": "TOR01 Yorkville <tor01.store@moncler-retail.example>",
    "lm": "Lauren Mitchell <lauren.mitchell@moncler-retail.example>",
}

LM = "Lauren Mitchell <lauren.mitchell@moncler-retail.example>"
OPS = "retail-ops-canada@moncler-retail.example"
MERCH = "merch-planning-americas@moncler-retail.example"
CLI = "clienteling-na@moncler-retail.example"
EG = "Émilie Gagnon <emilie.gagnon@moncler-retail.example>"

DEFAULT_TO = [OPS]
DEFAULT_CC = [LM]

SIG_EG = """Émilie Gagnon
Directrice de boutique / Store Manager
Moncler Toronto Yorkville | 100 Yorkville Ave, Toronto ON M5R 1B9"""

HABIT_LINES = [SIG_EG, "Sent from my iPhone"]

EMAILS = [
    dict(key="0831", sent="2026-08-31 19:44", frm="rc", mailer="iphone", covers=["2026-08-31"],
         subject="TOR EOD 08/31",
         body="""Net 3.8K vs 18.3 plan. 4 trx. Worst day of the month, everyone at the cottage for the last week of summer.

Missed Marin navy 5, polo white S. Maya 5 return for size.

Ryan

Sent from my iPhone"""),

    dict(key="0901", sent="2026-09-01 19:51", frm="eg", covers=["2026-09-01"],
         subject="Yorkville - closing mardi 1er sept",
         body=f"""Bonsoir everyone,

Pas pire for a Tuesday : $24.6K vs $17.4K plan, 6 transactions. 2 Maire black, 2 polo white, 1 Peyre black (client going to Whistler in December) and Trailgrips.

Delivery arrived with 1 day late, the broker had a problem with the customs papers again. 113 pieces.

Asked : Tib off-white 2.

Merci,
Émilie

{SIG_EG}"""),

    dict(key="0902", sent="2026-09-02 19:38", frm="eg", covers=["2026-09-02"],
         subject="Yorkville - closing 2 sept",
         body=f"""Hi all,

$14.9K vs $19.5K. Maire black x3 again (the Maire black is very strong this week, 5 in 2 days) and now the size 0 is finished. Padded cardigans, hoodies.

Émilie"""),

    dict(key="0903", sent="2026-09-03 19:47", frm="eg", covers=["2026-09-03"],
         subject="Yorkville - closing 3 sept",
         body=f"""Hi,

$21.7K vs $27.5K, 12 transactions. Small things, hoodies, scarves, beanie.

Logo cardigan navy M is at zero.

Émilie"""),

    dict(key="0904", sent="2026-09-04 20:31", frm="eg", covers=["2026-09-04"],
         subject="Yorkville - closing vendredi 4 sept",
         body=f"""Bonsoir,

$32.3K vs $31.4K ✔. 15 transactions. Sweatshirts black x3, polos, belt bags. Almost only Canadians, the long weekend crowd shopping before leaving.

1 client asked the Hermine navy in 00, we never receive 00 in Hermine.
Maya 2 returned (colour, she wanted olive).

Bon long weekend à tous !

{SIG_EG}"""),

    dict(key="0905", sent="2026-09-05 19:22", frm="eg", covers=["2026-09-05"],
         subject="Yorkville - closing 5 sept",
         body=f"""$24.6K vs $45.9K plan. Quiet Saturday, long weekend, the city is empty. 8 transactions, Maire navy x2, Valbourg black.

Asked : Montgenevre black 6, Tib off-white 2 (2nd time this week).

Émilie"""),

    dict(key="0906", sent="2026-09-06 18:36", frm="am", covers=["2026-09-06"],
         subject="TOR closing Sun 06/09",
         body="""Hi team!

Sales $20.9K, plan $32.2K. 11 transactions. Hoodies navy x2, tees, sweatshirt.

A lady asked for the Hermine black in 3, we're out.

Have a good night 😊
Aisha"""),

    dict(key="0907", sent="2026-09-07 19:12", frm="rc", mailer="iphone", covers=["2026-09-07"],
         subject="TOR EOD 09/07",
         body="""Labour Day. Net 10.8K vs 24.0 plan, 5 trx. Padded cardi black x2, scarf, Trailgrip.

Delivery 126 units, on time this one.

Sent from my iPhone"""),

    dict(key="0908", sent="2026-09-08 19:55", frm="eg", covers=["2026-09-08"],
         subject="Yorkville - closing 8 sept",
         body=f"""Hi all,

$24.9K vs $22.8K ✔ 13 transactions. Chambre black x2, Valbourg black.

TIFF starts Thursday. Already today 2 stylists came to see the collection, one for an actor in a gala film. They want to borrow pieces for the press days at the Hazelton and the Shangri-La. I need the loan policy for Canada, is it the same memo form as the US ?

Ilvaro 2 returned (size).

{SIG_EG}"""),

    dict(key="0908re1", sent="2026-09-09 08:41", frm="lm", reply_to="0908", suffix="_re1", covers=[],
         to=[EG], cc=[OPS, CLI],
         subject="RE: Yorkville - closing 8 sept",
         body="""Hi Émilie, yes same memo form as the US (I'll send the PDF). Max 5 pieces per stylist, 72h, credit card on file or agency PO. Log everything in the pull sheet so we can track what converts. No samples of the Genius pieces before the 24th please.

Good luck with TIFF!
Lauren"""),

    dict(key="0909", sent="2026-09-09 20:07", frm="eg", covers=["2026-09-09"],
         subject="Yorkville - closing 9 sept",
         body=f"""Bonsoir,

$38.4K vs $26.0K (+48%) ! 13 transactions. Arneb black x2, padded cardigans, Chambre black x2, sweatshirts.

The Arneb : both clients took one size smaller after trying, it is really big. I told the team to always propose one size down first.

Asked : padded cardigan black M and navy S. Padded black XL is also gone.

Merci Lauren for the memo.

{SIG_EG}"""),

    dict(key="0910", sent="2026-09-10 20:24", frm="eg", covers=["2026-09-10"],
         subject="Yorkville - closing jeudi 10 sept (TIFF day 1)",
         body=f"""Hi all,

C'est parti ! TIFF opening night. $44.8K vs $27.9K plan (+61%), 14 transactions. Yorkville is full, the hotels are full, black SUVs everywhere on Avenue Rd.

- 3 stylists today, 7 pieces out on memo (Montgenevre, Maya, logo cardigans, 1 Hermine)
- Montgenevre black x2 sold, Trailgrips, hoodies, logo cardigan navy x2
- A gentleman from LA who is in the festival bought 2 Trailgrip for him and his son

King St is closed for the Festival Street until Sunday.

Émilie"""),

    dict(key="0911", sent="2026-09-11 20:52", frm="eg", covers=["2026-09-11"],
         subject="Yorkville - closing 11 sept",
         body=f"""Bonsoir la gang,

What a day, tabarnouche. $59.0K vs $33.9K plan, 24 transactions. Best day since March.

- an actress (I will not write her name, the one from the A24 film) came with her stylist, bought the Ilvaro black and took 2 more for her sisters → Ilvaro black now zero in 0, 1 and 3
- hoodies navy x4, turtleneck black x3, Trailgrip black x3
- paparazzi on Hazelton Ave all afternoon

Asked and missed :
- Bady powder pink 4, 2 different girls
- Peyre red 2
- Trailgrip black 39

Chambre 3 gift return.

Émilie

{SIG_EG}"""),

    dict(key="0912", sent="2026-09-12 20:16", frm="rc", mailer="iphone", covers=["2026-09-12"],
         attach=[{"name": "IMG_5512.jpg"}],
         subject="TOR EOD 09/12",
         body="""Net 44.5K vs 46.6 plan, 17 trx, traffic 189 (record for a Sat this year).

Émilie at the gala tonight with the stylist from yesterday so I'm closing. Pic of the line outside at 3pm attached lol, people waiting to see if someone famous comes out of the Hazelton.

Turtleneck brown x2, Peyre black, hoodies. Turtleneck black L asked. Maire black 0 + beige 2 + Ilvaro black 0/1/3 all at zero.

Sent from my iPhone"""),

    dict(key="0913", sent="2026-09-13 19:04", frm="rc", mailer="iphone", covers=["2026-09-13"],
         subject="TOR EOD 09/13",
         body="""Net 32.3K vs 34.0 plan. 11 trx. Peyre black x2 + Karakorum black x2.

Missed a LOT today, mostly TIFF people with no time to wait:
Maire black 0
Ilvaro black 0 and 3
Maya olive 5 and 6
Karakorum grey 4
Tib off-white 3
Peyre red 7

Can we get an Ilvaro black transfer from NY? Lost at least 2 because of it.

Sent from my iPhone"""),

    dict(key="0914", sent="2026-09-14 19:27", frm="rc", mailer="iphone", covers=["2026-09-14"],
         subject="TOR EOD 09/14",
         body="""Net 15.3K vs 25.0 plan. 12 trx, scarves, sweatshirts. Chinese clients ~1 in 6.

Women's Trailgrip cream 41 asked. Delivery 103.

Sent from my iPhone"""),

    # 9/15 no own email; combined in 0916

    dict(key="0916", sent="2026-09-16 20:12", frm="eg", covers=["2026-09-15", "2026-09-16"],
         subject="Yorkville - closing 15 + 16 sept",
         body=f"""Hi all, désolée, I didn't send yesterday, we were doing the memo returns until 9pm.

Tuesday 15 : $12.4K vs $25.4K. Mid-festival dip, the stylists are busy with premieres. 2 Tib returned (gift + change of mind), Hermine 1 returned.
Wednesday 16 : $22.3K vs $28.5K. Peyre black, scarf, cap.

Missed today : Arneb black 3 (because everybody sizes down, the 3 is gone !), sweatshirt grey M, women's Trailgrip black 36, Insolux black 40.

Memo status : 7 pieces out, 4 returned, 1 converted (Montgenevre black for the actor), 2 still out.

Émilie

{SIG_EG}"""),

    dict(key="0917", sent="2026-09-17 20:03", frm="eg", covers=["2026-09-17"],
         subject="Yorkville - closing 17 sept",
         body=f"""$15.8K vs $31.6K. Beanies, tees, Insolux black x2 (the first boots, a couple going to Mont-Tremblant).

Logo tee navy S asked.

Émilie"""),

    dict(key="0918", sent="2026-09-18 20:39", frm="eg", covers=["2026-09-18"],
         subject="Yorkville - closing vendredi 18",
         body=f"""Bonsoir,

$31.6K vs $37.7K. 13 transactions. Maya olive x2, women's Trailgrips, Peyre red.

Asked : turtleneck navy L x2, turtleneck navy XS, Rosiere black 1.
4 returns (Montgenevre 4 colour, logo cardigan XS, hoodie, polo).

Last weekend of TIFF.

{SIG_EG}"""),

    dict(key="0919", sent="2026-09-19 20:28", frm="eg", covers=["2026-09-19"],
         subject="Yorkville - closing samedi 19 sept",
         body=f"""Hi all,

$43.0K vs $49.7K plan. 20 transactions, traffic 224 !! Lots of international visitors (US, UK, Europe), the festival people doing their shopping before flying home.

Tees white x4, hoodies navy x4, Chamonix pants x2.

Asked : Montgenevre grey 5, Peyre black 1, Chamonix XS, tee white XL.

Émilie"""),

    dict(key="0920", sent="2026-09-20 18:42", frm="am", covers=["2026-09-20"],
         subject="TOR closing Sun 20/09",
         body="""Hi everyone,

$44.5K today vs $39.8K plan!! 16 transactions. Valbourg black x4 (a ski family from Montreal, all 4 of them) and Montgenevre black x2.

Chinese tourists in the afternoon.

Missed: Peyre black 3 (x2), Flammette navy 00, Chambre black 4, Tib off-white 5, gloves.

Last day of TIFF, quiet street after 4.

Aisha 😊"""),

    dict(key="0921", sent="2026-09-21 19:33", frm="rc", mailer="iphone", covers=["2026-09-21"],
         subject="TOR EOD 09/21",
         body="""Net 37.5K vs 27.2 plan, 16 trx. Chambre black x2, Tib black x2. Delivery 190 units.

Sent from my iPhone"""),

    dict(key="0921dup", sent="2026-09-21 19:35", frm="rc", mailer="iphone", suffix="_dup", covers=[],
         subject="TOR EOD 09/21",
         body="""Net 37.5K vs 27.2 plan, 16 trx. Chambre black x2, Tib black x2. Delivery 190 units.

Sent from my iPhone"""),

    dict(key="0921fwd", sent="2026-09-21 21:10", frm="eg", suffix="_fwd", covers=[],
         to=[LM], cc=[CLI],
         subject="TR: thank you!!",
         body=f"""Lauren, for your info, nice message from the stylist (the actor wore the Montgenevre at the premiere, there are photos on Getty). Voilà the power of TIFF :)

Émilie

-------- Message transféré --------
De : Jess Okafor <jess@okafor-styling.example>
Date : 20 sept. 2026 23:14
À : Émilie Gagnon <emilie.gagnon@moncler-retail.example>
Objet : thank you!!

Émilie - thank you so much for the last-minute pulls this week, you saved us. J. loved the Montgenevre and is keeping it. Will be back in the spring for the junket.
x Jess

{SIG_EG}"""),

    dict(key="0922", sent="2026-09-22 19:46", frm="eg", covers=["2026-09-22"],
         subject="Yorkville - closing 22 sept",
         body=f"""$23.3K vs $27.0K. Ambrine black x3 and Maire black x3, one lady bought 2 Ambrine (1 for her daughter in Montréal).

Ambrine black 1 now finished. Asked : Chamonix XS (2nd time), tee navy L, women's Trailgrip cream 40.

Émilie"""),

    dict(key="0923", sent="2026-09-23 19:51", frm="eg", covers=["2026-09-23"],
         subject="Yorkville - closing 23 sept",
         body=f"""$34.0K vs $29.0K ✔. Maire black x2, padded cardigan grey x2, logo cardigans.

Asked : Maire black 4 and tee white S.

First cold morning, 7 degrees at 8am ! The clients start to think about coats. In Toronto we always start before the US.

Émilie"""),

    dict(key="0924", sent="2026-09-24 20:14", frm="eg", covers=["2026-09-24"],
         subject="Yorkville - closing 24 sept (Polaris)",
         body=f"""Hi all,

$41.5K vs $35.9K (+16%). 16 transactions.

Polaris launch : 1 oversized black sold to a young guy who follows the Genius drops. The other clients tried and said the same thing: it is small in the shoulders and the price is very high for what it is. The cape nobody understands.

Arneb black x2 (sized down again, 6 → 5 and 5 → 4), Montgenevre black x2.

Maire black 4 asked (2nd day). Ilvaro 3 returned.

{SIG_EG}"""),

    dict(key="0925", sent="2026-09-25 20:33", frm="eg", covers=["2026-09-25"],
         subject="Yorkville - closing vendredi 25",
         body=f"""$41.5K vs $43.8K. Hermine black x4 !! (now out of 3), Maya olive x2.

Asked : Hermine black 3, Polaris oversized light blue XXL (a very tall client, the XXL fits like a L, he was disappointed).

Polaris cape sold 1.

Émilie"""),

    dict(key="0926", sent="2026-09-26 20:22", frm="eg", covers=["2026-09-26"],
         subject="Yorkville - closing samedi 26",
         body=f"""Bonsoir,

$50.0K vs $59.9K plan, 17 transactions, 200 people.

Tib black x3, logo cardigan black x3, Peyre black x2.

Missed, ouf, a long list :
- Hermine navy 0
- Ilvaro off-white 0
- Maya olive 6
- Karakorum navy 6
- padded cardigan grey XL
- turtleneck navy XS
- women's Trailgrip black 41

Ilvaro 0 returned (size), Karakorum 3 returned.

Émilie

{SIG_EG}"""),

    dict(key="0927", sent="2026-09-27 18:40", frm="am", covers=["2026-09-27"],
         subject="TOR closing 27/09",
         body="""Hi team!

Great Sunday: $52.1K vs $44.3K 🎉 15 transactions. Maya black x5!! Tib black x3, Montcla black x2, Maire black x2.

Missed Tib black 3. Tib 3 returned for size (exchanged for a 4).

Aisha"""),

    dict(key="0928", sent="2026-09-28 19:37", frm="rc", mailer="iphone", covers=["2026-09-28"],
         subject="TOR EOD 09/28",
         body="""Net 16.7K vs 33.0 plan. 11 trx. Belt bags x3.

2 Tib returns with broken zippers (sizes 7 and 2), both bought in August. Slider doesn't hold, opens from the bottom. Anyone else seeing this?

Missed Montgenevre navy 1, tee black XXL. Delivery 148.

Sent from my iPhone"""),

    dict(key="0929", sent="2026-09-29 19:58", frm="eg", covers=["2026-09-29"],
         subject="Yorkville - closing 29 sept",
         body=f"""$20.2K vs $34.0K. 6 transactions. Valbourg black, scarf, gloves.

Another Tib zipper (size 5). 3 in 2 days. I put the Tib black on the side and I check every zipper before selling.

Logo cardigan M returned, a hole near the button.

Émilie"""),

    dict(key="0930", sent="2026-09-30 20:04", frm="eg", covers=["2026-09-30"],
         subject="Yorkville - closing 30 sept",
         body=f"""Hi all,

$33.3K vs $36.5K. Tib navy x3 (I checked the zippers, all good), Montcla black x2. National Day for Truth and Reconciliation, some offices closed, more people in the afternoon.

Asked : Montcla black 7, Tib black 3.
Returned : Hermine 0, Polaris oversized (colour, he wants the light blue which we have only in XL), tee.

September : ~$925K vs ~$980K plan. Pas pire with TIFF.

{SIG_EG}"""),

    dict(key="1001", sent="2026-10-01 19:49", frm="eg", covers=["2026-10-01"],
         subject="Yorkville - fermeture 1er octobre",
         body=f"""Bonsoir à tous,

Journée tranquille : 19,7 K$ pour un plan de 39,5 K$. Casquettes, hoodies, 2 Maya noires.

Demandes manquées : Montcla noir 2, Karakorum noir 3, Tib noir 4, cable knit crème L.

Retours : Ilvaro 2 (cadeau), Maya 7 (taille), Karakorum 4 (qualité, la couture de la poche), hoodie L.

Oups, sorry, I wrote everything in French, long day. Quick version : $19.7K vs $39.5K plan, missed Montcla black 2, Karakorum black 3, Tib black 4, cable knit cream L. 4 returns incl. a Karakorum 4 with a pocket seam problem.

Émilie

{SIG_EG}"""),

    dict(key="1002", sent="2026-10-02 20:41", frm="eg", covers=["2026-10-02"],
         subject="Yorkville - closing vendredi 2 oct",
         body=f"""Hi all,

$59.5K vs $49.0K plan (+21%). 16 transactions.

- Arneb black x3 (the Arneb is THE jacket this fall in Toronto, the men compare it with the Goose parkas and they like that it is less bulky)
- Ilvaro black x3, Chinese students, one showed me a picture of the K-pop girl in the pink one in Paris
- Bady off-white x2

Missed : Maire black 1 and 4, Hermine black 2. Tib 5 zipper return.

{SIG_EG}"""),

    dict(key="1002re1", sent="2026-10-03 09:12", frm="lm", reply_to="1002", suffix="_re1", covers=[],
         to=[EG], cc=[OPS],
         subject="RE: Yorkville - closing vendredi 2 oct",
         body="""Great Friday! Is that CAD? And how many Arneb do you have left by size? Merch is asking which stores to prioritize for the re-order.

L.

Sent from my iPhone"""),

    dict(key="1002re2", sent="2026-10-03 10:05", frm="eg", reply_to="1002re1", suffix="_re2", covers=[],
         to=[LM], cc=[OPS, MERCH],
         subject="RE: Yorkville - closing vendredi 2 oct",
         body=f"""Hi Lauren, yes always CAD.

Arneb (we only have black) on hand tonight : size 1 → 1, 2 → 2, 3 → 0 (since mid-Sept), 4 → 4, 5 → 1, 6 → 0, 7 → 1.
Because we advise one size down, the 3 and the 6 go first (clients who are normally a 4 or a 7). Please send 3, 5 and 6, we have enough 4.

Émilie

{SIG_EG}"""),

    dict(key="1003", sent="2026-10-03 19:31", frm="rc", mailer="iphone", covers=["2026-10-03"],
         subject="TOR EOD 10/03",
         body="""Net 29.8K vs 62.4 plan. 15 trx, 172 traffic. Same Saturday LY was ~56K so the plan isn't crazy, we just didn't convert.

Beanies, caps, turtlenecks, sweatshirts.

Missed: beanie white x2, Maire cream 0, Ambrine black 1, Ecrins black 6, cable knit cream L.
Tib 2 zipper return.

Sent from my iPhone"""),

    dict(key="1004", sent="2026-10-04 19:08", frm="rc", mailer="iphone", covers=["2026-10-04"],
         subject="TOR EOD 10/04",
         body="""Net 14.9K vs 48.5 plan. Ouch. 9 trx

Missed:
Maya black 5 x2
Maire black 0 and 1
Maya olive 6
Karakorum black 3
Arneb black 6

Leafs preseason game tonight, Yorkville empty after 5

Sent from my iPhone"""),

    # 10/5 no own email; mentioned in 1006

    dict(key="1006", sent="2026-10-06 20:11", frm="eg", covers=["2026-10-06"],
         subject="Yorkville - closing 6 oct",
         body=f"""Bonsoir,

Ryan didn't send yesterday, Monday was ~$21K, 2 pink beanies, a Polaris oversized light blue and a Peyre. Delivery 194 pieces received.

Today $43.6K vs $35.0K (+25%) ! Bady off-white x3, Maya black x2, 2 Polaris capes (a couple, matching, c'est fou).

Asked : Maire black 0, Arneb black 6 (he was a 7 normally, so 6 was the right size).

{SIG_EG}"""),

    dict(key="1007", sent="2026-10-07 19:53", frm="eg", covers=["2026-10-07"],
         subject="Yorkville - closing 7 oct",
         body=f"""$38.6K vs $36.6K ✔. Caps, sweatshirts, padded cardigans black x2, Peyre red.

Tib 4 zipper. That's the 6th since end of September. Please, do we have instruction to return the batch ?

Émilie"""),

    dict(key="1008", sent="2026-10-08 20:18", frm="eg", covers=["2026-10-08"],
         subject="Yorkville - closing 8 oct",
         body=f"""$42.9K vs $43.0K, on plan. Maire beige x2, Polaris balaclava, Chamonix.

Asked : Ilvaro off-white 3, turtleneck black M.
Returns : 4 (Tib zipper again, logo cardigan XXL, Trailgrip gift, Insolux).

Émilie"""),

    dict(key="1009", sent="2026-10-09 20:47", frm="eg", covers=["2026-10-09"],
         subject="Yorkville - closing vendredi 9 oct",
         body=f"""Hi all,

$37.1K vs $49.6K. 14 transactions. Valbourg off-white x2, Maire beige x2, padded navy x2. Start of the Thanksgiving long weekend, lots of people leaving the city tonight.

Missed :
- padded cardigan navy XXL x2 (father and son)
- Hermine off-white 00
- Ecrins black 5
- Arneb black 6 (3rd time this week)
- cable knit cream L (4th time in 2 weeks !)
- tee white S

Arneb 5 is finished too now.

{SIG_EG}"""),

    dict(key="1010", sent="2026-10-10 19:36", frm="eg", covers=["2026-10-10"],
         subject="Yorkville - closing 10 oct",
         body=f"""$23.4K vs $72.4K plan (-68%). Thanksgiving Saturday, the city went to the cottages. 12 transactions, logo cardigan black x4.

Hoodie grey M x2 asked, hoodie black XS. Arneb 5 returned (size, took a 4 instead... exchange).

Émilie"""),

    dict(key="1011", sent="2026-10-11 18:29", frm="am", covers=["2026-10-11"],
         subject="TOR closing 11/10",
         body="""Hi!

$20.5K vs $48.2K plan, 9 transactions. Turtleneck navy x3 to a Chinese family.

Asked: logo cardigan black S, cable knit cream L.

Happy Thanksgiving everyone 🦃
Aisha"""),

    dict(key="1012", sent="2026-10-12 18:50", frm="rc", mailer="iphone", covers=["2026-10-12"],
         subject="TOR EOD 10/12",
         body="""Thanksgiving Monday, open 12-5. Net 25.4K vs 37.9 plan, 10 trx. Polaris oversized black, Chamonix, Valbourg cream.

Missed Maire black 0 + 3, Valbourg cream 2, padded grey XS. Maire black now zero in 0-3. Delivery 145, no Maire black inside.

Sent from my iPhone"""),

    dict(key="1013", sent="2026-10-13 20:02", frm="eg", covers=["2026-10-13"],
         subject="Yorkville - closing 13 oct",
         body=f"""Hi all,

$22.9K, 8 transactions. Maire beige x2, Valbourg black, Peyre black.

Asked : Maire black 2, Maya olive 6.

6 returns : Hermine 2, Bady 4 (size), Ilvaro 3 (colour, she wants pink...), beanie, and 2 more Tib with the zipper.

Émilie"""),

    dict(key="1014", sent="2026-10-14 20:09", frm="eg", covers=["2026-10-14"],
         subject="Yorkville - closing 14 oct",
         body=f"""$23.4K vs $42.4K. 7 transactions, small (beanies, gloves, Trailgrip).

Asked : logo cardigan black S, sweatshirt grey XS. 1 more Tib zipper.

Lauren arrives tomorrow, we are ready ! Store visit at 11h.

Émilie"""),

    dict(key="1015", sent="2026-10-15 20:36", frm="eg", covers=["2026-10-15"],
         subject="Yorkville - closing 15 oct + visit",
         body=f"""Bonsoir,

$30.7K vs $46.5K. Padded cardigans black x2, caps, beanies. Polo black XL asked.

Merci Lauren for the visit today. Recap of what we discussed :
1. October plan : we are ~35% under, the plan assumes a big cold-weather month but it is still 12-15 degrees in the afternoon. The clients buy when it's cold in the morning, then they wait.
2. Maire black : 0 in all sizes since the 12th, about 8 asks in October so far. Waitlist 9 names.
3. Arneb : send 3/5/6 (see my email of Oct 3).
4. Tib : 11 zipper returns since Sept 28, we keep the stock in the back.
5. Polaris : 8 pieces sold since launch, 1 returned. Better than we feared, but not a hit.

Émilie

{SIG_EG}"""),

    dict(key="1016", sent="2026-10-16 20:48", frm="eg", covers=["2026-10-16"],
         subject="Yorkville - closing vendredi 16",
         body=f"""$37.2K vs $52.9K. 12 transactions. Hoodies black x3, Maire navy x2, Chamonix.

Asked : Maire black 2 (x2), Maire black 4, Arneb black 2 (a young girl who wanted the men's parka for her, the 2 would have been perfect), polo white S.

Valbourg 2 returned (change of mind).

Émilie"""),

    dict(key="1017", sent="2026-10-17 19:58", frm="rc", mailer="iphone", covers=["2026-10-17"],
         subject="TOR EOD 10/17",
         body="""Net 61.3K vs 73.4 plan. 21 trx, 223 traffic. Cold morning (2 degrees), people finally shopping for coats.

Ilvaro black x3, Trailgrips, scarves, polos.

Missed (long one):
Maire black 0 x2, 2, 3
Flammette black 00
Chambre cream 3
Maya olive 2
logo cardi black S
padded grey M

The Maire black waitlist is now 12. Heard the DC got stock yesterday, can we confirm our allocation?

Sent from my iPhone"""),

    dict(key="1018", sent="2026-10-18 18:33", frm="am", covers=["2026-10-18"],
         subject="TOR closing 18/10",
         body="""Hi team,

$51.4K vs $56.1K plan. 16 transactions. Peyre black x2, Chambre black x2, Montgenevre black x2, hoodies.

Missed Maire black 1. Karakorum 6 gift return, Tib 5 zipper return.

Aisha"""),

    dict(key="1019", sent="2026-10-19 19:22", frm="rc", mailer="iphone", covers=["2026-10-19"],
         subject="TOR EOD 10/18",
         body="""Net 23.4K vs 41.4 plan. 9 trx. Hoodies navy, Bady black x2.

Missed padded black XXL x2, padded black L, Maire black 1, Maire beige 1.

Sent from my iPhone"""),

    dict(key="1020", sent="2026-10-20 20:01", frm="eg", covers=["2026-10-20"],
         subject="Yorkville - closing 20 oct",
         body=f"""Hi all,

$32.9K vs $42.4K. Arneb black x2 (sized down, perfect), gloves x2, Polaris cape white.

Maire black 1 asked (again). Rosiere 6 returned, quality (snap).

Delivery 202 pieces arrived with 1 day late, broker again. Still no Maire black in it.

{SIG_EG}"""),

    dict(key="1021", sent="2026-10-21 20:14", frm="eg", covers=["2026-10-21"],
         subject="Yorkville - closing 21 oct",
         body=f"""$29.1K vs $44.2K. Padded cardigans black x2, women's Trailgrip cream x2, Chamonix. A group of American tourists from Buffalo.

Asked : hoodie grey M, Insolux black 41.
Hermine 0 returned, quality (the hood snap).

En tout cas, we need the Maire black. Bonne soirée.

Émilie"""),
]
