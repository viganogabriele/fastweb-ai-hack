STORE = "TOR01"

WRITERS = {
    "eg": "Émilie Gagnon <emilie.gagnon@valentino-retail.example>",
    "rc": "Ryan Chen <ryan.chen@valentino-retail.example>",
    "am": "Aisha Mohamed <aisha.mohamed@valentino-retail.example>",
    "box": "TOR01 Yorkville <tor01.store@valentino-retail.example>",
    "lm": "Lauren Mitchell <lauren.mitchell@valentino-retail.example>",
}

LM = "Lauren Mitchell <lauren.mitchell@valentino-retail.example>"
OPS = "retail-ops-canada@valentino-retail.example"
MERCH = "merch-planning-americas@valentino-retail.example"
CLI = "clienteling-na@valentino-retail.example"
EG = "Émilie Gagnon <emilie.gagnon@valentino-retail.example>"

DEFAULT_TO = [OPS]
DEFAULT_CC = [LM]

SIG_EG = """Émilie Gagnon
Directrice de boutique / Store Manager
Valentino Toronto Yorkville | 100 Yorkville Ave, Toronto ON M5R 1B9"""

HABIT_LINES = [SIG_EG, "Sent from my iPhone"]

EMAILS = [
    dict(key="0831", sent="2026-08-31 19:44", frm="rc", mailer="iphone", covers=["2026-08-31"],
         subject="TOR EOD 08/31",
         body="""Net 3.8K vs 18.3 plan. 4 trx. Worst day of the month, everyone at the cottage for the last week of summer.

Missed Mario navy 5, jersey polo white S. Nova 5 return for size.

Ryan

Sent from my iPhone"""),

    dict(key="0901", sent="2026-09-01 19:51", frm="eg", covers=["2026-09-01"],
         subject="Yorkville - closing mardi 1er sept",
         body=f"""Bonsoir everyone,

Pas pire for a Tuesday : $24.6K vs $17.4K plan, 6 transactions. 2 Aurea black, 2 jersey polo white, 1 Piero black (client going to Whistler in December) and Vtracks.

Delivery arrived with 1 day late, the broker had a problem with the customs papers again. 113 pieces.

Asked : Vel off-white 2.

Merci,
Émilie

{SIG_EG}"""),

    dict(key="0902", sent="2026-09-02 19:38", frm="eg", covers=["2026-09-02"],
         subject="Yorkville - closing 2 sept",
         body=f"""Hi all,

$14.9K vs $19.5K. Aurea black x3 again (the Aurea black is very strong this week, 5 in 2 days) and now the size 0 is finished. Padded cardigans, hoodies.

Émilie"""),

    dict(key="0903", sent="2026-09-03 19:47", frm="eg", covers=["2026-09-03"],
         subject="Yorkville - closing 3 sept",
         body=f"""Hi,

$21.7K vs $27.5K, 12 transactions. Small things, hoodies, scarves, beanie.

Vlogo Cardigan navy M is at zero.

Émilie"""),

    dict(key="0904", sent="2026-09-04 20:31", frm="eg", covers=["2026-09-04"],
         subject="Yorkville - closing vendredi 4 sept",
         body=f"""Bonsoir,

$32.3K vs $31.4K ✔. 15 transactions. Sweatshirts black x3, polos, belt bags. Almost only Canadians, the long weekend crowd shopping before leaving.

1 client asked the Liviana navy in 00, we never receive 00 in Liviana.
Nova 2 returned (colour, she wanted olive).

Bon long weekend à tous !

{SIG_EG}"""),

    dict(key="0905", sent="2026-09-05 19:22", frm="eg", covers=["2026-09-05"],
         subject="Yorkville - closing 5 sept",
         body=f"""$24.6K vs $45.9K plan. Quiet Saturday, long weekend, the city is empty. 8 transactions, Aurea navy x2, Valdora black.

Asked : Monteluce black 6, Vel off-white 2 (2nd time this week).

Émilie"""),

    dict(key="0906", sent="2026-09-06 18:36", frm="am", covers=["2026-09-06"],
         subject="TOR closing Sun 06/09",
         body="""Hi team!

Sales $20.9K, plan $32.2K. 11 transactions. Hoodies navy x2, tees, sweatshirt.

A lady asked for the Liviana black in 3, we're out.

Have a good night 😊
Aisha"""),

    dict(key="0907", sent="2026-09-07 19:12", frm="rc", mailer="iphone", covers=["2026-09-07"],
         subject="TOR EOD 09/07",
         body="""Labour Day. Net 10.8K vs 24.0 plan, 5 trx. Padded cardi black x2, scarf, Vtrack.

Delivery 126 units, on time this one.

Sent from my iPhone"""),

    dict(key="0908", sent="2026-09-08 19:55", frm="eg", covers=["2026-09-08"],
         subject="Yorkville - closing 8 sept",
         body=f"""Hi all,

$24.9K vs $22.8K ✔ 13 transactions. Camilla black x2, Valdora black.

TIFF starts Thursday. Already today 2 stylists came to see the collection, one for an actor in a gala film. They want to borrow pieces for the press days at the Hazelton and the Shangri-La. I need the loan policy for Canada, is it the same memo form as the US ?

Iridia 2 returned (size).

{SIG_EG}"""),

    dict(key="0908re1", sent="2026-09-09 08:41", frm="lm", reply_to="0908", suffix="_re1", covers=[],
         to=[EG], cc=[OPS, CLI],
         subject="RE: Yorkville - closing 8 sept",
         body="""Hi Émilie, yes same memo form as the US (I'll send the PDF). Max 5 pieces per stylist, 72h, credit card on file or agency PO. Log everything in the pull sheet so we can track what converts. No samples of the Couture pieces before the 24th please.

Good luck with TIFF!
Lauren"""),

    dict(key="0909", sent="2026-09-09 20:07", frm="eg", covers=["2026-09-09"],
         subject="Yorkville - closing 9 sept",
         body=f"""Bonsoir,

$38.4K vs $26.0K (+48%) ! 13 transactions. Artem black x2, padded cardigans, Camilla black x2, sweatshirts.

The Artem : both clients took one size smaller after trying, it is really big. I told the team to always propose one size down first.

Asked : padded cardigan black M and navy S. Padded black XL is also gone.

Merci Lauren for the memo.

{SIG_EG}"""),

    dict(key="0910", sent="2026-09-10 20:24", frm="eg", covers=["2026-09-10"],
         subject="Yorkville - closing jeudi 10 sept (TIFF day 1)",
         body=f"""Hi all,

C'est parti ! TIFF opening night. $44.8K vs $27.9K plan (+61%), 14 transactions. Yorkville is full, the hotels are full, black SUVs everywhere on Avenue Rd.

- 3 stylists today, 7 pieces out on memo (Monteluce, Nova, logo cardigans, 1 Liviana)
- Monteluce black x2 sold, Vtracks, hoodies, vlogo cardigan navy x2
- A gentleman from LA who is in the festival bought 2 Vtrack for him and his son

King St is closed for the Festival Street until Sunday.

Émilie"""),

    dict(key="0911", sent="2026-09-11 20:52", frm="eg", covers=["2026-09-11"],
         subject="Yorkville - closing 11 sept",
         body=f"""Bonsoir la gang,

What a day, tabarnouche. $59.0K vs $33.9K plan, 24 transactions. Best day since March.

- an actress (I will not write her name, the one from the A24 film) came with her stylist, bought the Iridia black and took 2 more for her sisters → Iridia black now zero in 0, 1 and 3
- hoodies navy x4, turtleneck black x3, Vtrack black x3
- paparazzi on Hazelton Ave all afternoon

Asked and missed :
- Aria powder pink 4, 2 different girls
- Piero red 2
- Vtrack black 39

Camilla 3 gift return.

Émilie

{SIG_EG}"""),

    dict(key="0912", sent="2026-09-12 20:16", frm="rc", mailer="iphone", covers=["2026-09-12"],
         attach=[{"name": "IMG_5512.jpg"}],
         subject="TOR EOD 09/12",
         body="""Net 44.5K vs 46.6 plan, 17 trx, traffic 189 (record for a Sat this year).

Émilie at the gala tonight with the stylist from yesterday so I'm closing. Pic of the line outside at 3pm attached lol, people waiting to see if someone famous comes out of the Hazelton.

Turtleneck brown x2, Piero black, hoodies. Turtleneck black L asked. Aurea black 0 + beige 2 + Iridia black 0/1/3 all at zero.

Sent from my iPhone"""),

    dict(key="0913", sent="2026-09-13 19:04", frm="rc", mailer="iphone", covers=["2026-09-13"],
         subject="TOR EOD 09/13",
         body="""Net 32.3K vs 34.0 plan. 11 trx. Piero black x2 + Cosimo black x2.

Missed a LOT today, mostly TIFF people with no time to wait:
Aurea black 0
Iridia black 0 and 3
Nova olive 5 and 6
Cosimo grey 4
Vel off-white 3
Piero red 7

Can we get an Iridia black transfer from NY? Lost at least 2 because of it.

Sent from my iPhone"""),

    dict(key="0914", sent="2026-09-14 19:27", frm="rc", mailer="iphone", covers=["2026-09-14"],
         subject="TOR EOD 09/14",
         body="""Net 15.3K vs 25.0 plan. 12 trx, scarves, sweatshirts. Chinese clients ~1 in 6.

Women's Vtrack cream 41 asked. Delivery 103.

Sent from my iPhone"""),

    # 9/15 no own email; combined in 0916

    dict(key="0916", sent="2026-09-16 20:12", frm="eg", covers=["2026-09-15", "2026-09-16"],
         subject="Yorkville - closing 15 + 16 sept",
         body=f"""Hi all, désolée, I didn't send yesterday, we were doing the memo returns until 9pm.

Tuesday 15 : $12.4K vs $25.4K. Mid-festival dip, the stylists are busy with premieres. 2 Vel returned (gift + change of mind), Liviana 1 returned.
Wednesday 16 : $22.3K vs $28.5K. Piero black, scarf, cap.

Missed today : Artem black 3 (because everybody sizes down, the 3 is gone !), sweatshirt grey M, women's Vtrack black 36, Alpina black 40.

Memo status : 7 pieces out, 4 returned, 1 converted (Monteluce black for the actor), 2 still out.

Émilie

{SIG_EG}"""),

    dict(key="0917", sent="2026-09-17 20:03", frm="eg", covers=["2026-09-17"],
         subject="Yorkville - closing 17 sept",
         body=f"""$15.8K vs $31.6K. Beanies, tees, Alpina black x2 (the first boots, a couple going to Mont-Tremblant).

Logo tee navy S asked.

Émilie"""),

    dict(key="0918", sent="2026-09-18 20:39", frm="eg", covers=["2026-09-18"],
         subject="Yorkville - closing vendredi 18",
         body=f"""Bonsoir,

$31.6K vs $37.7K. 13 transactions. Nova olive x2, women's Vtracks, Piero red.

Asked : turtleneck navy L x2, turtleneck navy XS, Riviera black 1.
4 returns (Monteluce 4 colour, vlogo cardigan XS, hoodie, jersey polo).

Last weekend of TIFF.

{SIG_EG}"""),

    dict(key="0919", sent="2026-09-19 20:28", frm="eg", covers=["2026-09-19"],
         subject="Yorkville - closing samedi 19 sept",
         body=f"""Hi all,

$43.0K vs $49.7K plan. 20 transactions, traffic 224 !! Lots of international visitors (US, UK, Europe), the festival people doing their shopping before flying home.

Tees white x4, hoodies navy x4, Cortina pants x2.

Asked : Monteluce grey 5, Piero black 1, Cortina XS, tee white XL.

Émilie"""),

    dict(key="0920", sent="2026-09-20 18:42", frm="am", covers=["2026-09-20"],
         subject="TOR closing Sun 20/09",
         body="""Hi everyone,

$44.5K today vs $39.8K plan!! 16 transactions. Valdora black x4 (a ski family from Montreal, all 4 of them) and Monteluce black x2.

Chinese tourists in the afternoon.

Missed: Piero black 3 (x2), Fiammetta navy 00, Camilla black 4, Vel off-white 5, gloves.

Last day of TIFF, quiet street after 4.

Aisha 😊"""),

    dict(key="0921", sent="2026-09-21 19:33", frm="rc", mailer="iphone", covers=["2026-09-21"],
         subject="TOR EOD 09/21",
         body="""Net 37.5K vs 27.2 plan, 16 trx. Camilla black x2, Vel black x2. Delivery 190 units.

Sent from my iPhone"""),

    dict(key="0921dup", sent="2026-09-21 19:35", frm="rc", mailer="iphone", suffix="_dup", covers=[],
         subject="TOR EOD 09/21",
         body="""Net 37.5K vs 27.2 plan, 16 trx. Camilla black x2, Vel black x2. Delivery 190 units.

Sent from my iPhone"""),

    dict(key="0921fwd", sent="2026-09-21 21:10", frm="eg", suffix="_fwd", covers=[],
         to=[LM], cc=[CLI],
         subject="TR: thank you!!",
         body=f"""Lauren, for your info, nice message from the stylist (the actor wore the Monteluce at the premiere, there are photos on Getty). Voilà the power of TIFF :)

Émilie

-------- Message transféré --------
De : Jess Okafor <jess@okafor-styling.example>
Date : 20 sept. 2026 23:14
À : Émilie Gagnon <emilie.gagnon@valentino-retail.example>
Objet : thank you!!

Émilie - thank you so much for the last-minute pulls this week, you saved us. J. loved the Monteluce and is keeping it. Will be back in the spring for the junket.
x Jess

{SIG_EG}"""),

    dict(key="0922", sent="2026-09-22 19:46", frm="eg", covers=["2026-09-22"],
         subject="Yorkville - closing 22 sept",
         body=f"""$23.3K vs $27.0K. Amalia black x3 and Aurea black x3, one lady bought 2 Amalia (1 for her daughter in Montréal).

Amalia black 1 now finished. Asked : Cortina XS (2nd time), tee navy L, women's Vtrack cream 40.

Émilie"""),

    dict(key="0923", sent="2026-09-23 19:51", frm="eg", covers=["2026-09-23"],
         subject="Yorkville - closing 23 sept",
         body=f"""$34.0K vs $29.0K ✔. Aurea black x2, padded cardigan grey x2, logo cardigans.

Asked : Aurea black 4 and tee white S.

First cold morning, 7 degrees at 8am ! The clients start to think about coats. In Toronto we always start before the US.

Émilie"""),

    dict(key="0924", sent="2026-09-24 20:14", frm="eg", covers=["2026-09-24"],
         subject="Yorkville - closing 24 sept (Astra)",
         body=f"""Hi all,

$41.5K vs $35.9K (+16%). 16 transactions.

Astra launch : 1 oversized black sold to a young guy who follows the Couture drops. The other clients tried and said the same thing: it is small in the shoulders and the price is very high for what it is. The cape nobody understands.

Artem black x2 (sized down again, 6 → 5 and 5 → 4), Monteluce black x2.

Aurea black 4 asked (2nd day). Iridia 3 returned.

{SIG_EG}"""),

    dict(key="0925", sent="2026-09-25 20:33", frm="eg", covers=["2026-09-25"],
         subject="Yorkville - closing vendredi 25",
         body=f"""$41.5K vs $43.8K. Liviana black x4 !! (now out of 3), Nova olive x2.

Asked : Liviana black 3, Astra Oversized light blue XXL (a very tall client, the XXL fits like a L, he was disappointed).

Astra Cape sold 1.

Émilie"""),

    dict(key="0926", sent="2026-09-26 20:22", frm="eg", covers=["2026-09-26"],
         subject="Yorkville - closing samedi 26",
         body=f"""Bonsoir,

$50.0K vs $59.9K plan, 17 transactions, 200 people.

Vel black x3, vlogo cardigan black x3, Piero black x2.

Missed, ouf, a long list :
- Liviana navy 0
- Iridia off-white 0
- Nova olive 6
- Cosimo navy 6
- padded cardigan grey XL
- turtleneck navy XS
- women's Vtrack black 41

Iridia 0 returned (size), Cosimo 3 returned.

Émilie

{SIG_EG}"""),

    dict(key="0927", sent="2026-09-27 18:40", frm="am", covers=["2026-09-27"],
         subject="TOR closing 27/09",
         body="""Hi team!

Great Sunday: $52.1K vs $44.3K 🎉 15 transactions. Nova black x5!! Vel black x3, Mistral black x2, Aurea black x2.

Missed Vel black 3. Vel 3 returned for size (exchanged for a 4).

Aisha"""),

    dict(key="0928", sent="2026-09-28 19:37", frm="rc", mailer="iphone", covers=["2026-09-28"],
         subject="TOR EOD 09/28",
         body="""Net 16.7K vs 33.0 plan. 11 trx. Belt bags x3.

2 Vel returns with broken zippers (sizes 7 and 2), both bought in August. Slider doesn't hold, opens from the bottom. Anyone else seeing this?

Missed Monteluce navy 1, tee black XXL. Delivery 148.

Sent from my iPhone"""),

    dict(key="0929", sent="2026-09-29 19:58", frm="eg", covers=["2026-09-29"],
         subject="Yorkville - closing 29 sept",
         body=f"""$20.2K vs $34.0K. 6 transactions. Valdora black, scarf, gloves.

Another Vel zipper (size 5). 3 in 2 days. I put the Vel black on the side and I check every zipper before selling.

Vlogo Cardigan M returned, a hole near the button.

Émilie"""),

    dict(key="0930", sent="2026-09-30 20:04", frm="eg", covers=["2026-09-30"],
         subject="Yorkville - closing 30 sept",
         body=f"""Hi all,

$33.3K vs $36.5K. Vel navy x3 (I checked the zippers, all good), Mistral black x2. National Day for Truth and Reconciliation, some offices closed, more people in the afternoon.

Asked : Mistral black 7, Vel black 3.
Returned : Liviana 0, Astra Oversized (colour, he wants the light blue which we have only in XL), tee.

September : ~$925K vs ~$980K plan. Pas pire with TIFF.

{SIG_EG}"""),

    dict(key="1001", sent="2026-10-01 19:49", frm="eg", covers=["2026-10-01"],
         subject="Yorkville - fermeture 1er octobre",
         body=f"""Bonsoir à tous,

Journée tranquille : 19,7 K$ pour un plan de 39,5 K$. Casquettes, hoodies, 2 Nova noires.

Demandes manquées : Mistral noir 2, Cosimo noir 3, Vel noir 4, cable knit crème L.

Retours : Iridia 2 (cadeau), Nova 7 (taille), Cosimo 4 (qualité, la couture de la poche), hoodie L.

Oups, sorry, I wrote everything in French, long day. Quick version : $19.7K vs $39.5K plan, missed Mistral black 2, Cosimo black 3, Vel black 4, cable knit cream L. 4 returns incl. a Cosimo 4 with a pocket seam problem.

Émilie

{SIG_EG}"""),

    dict(key="1002", sent="2026-10-02 20:41", frm="eg", covers=["2026-10-02"],
         subject="Yorkville - closing vendredi 2 oct",
         body=f"""Hi all,

$59.5K vs $49.0K plan (+21%). 16 transactions.

- Artem black x3 (the Artem is THE jacket this fall in Toronto, the men compare it with the Goose parkas and they like that it is less bulky)
- Iridia black x3, Chinese students, one showed me a picture of the K-pop girl in the pink one in Paris
- Aria off-white x2

Missed : Aurea black 1 and 4, Liviana black 2. Vel 5 zipper return.

{SIG_EG}"""),

    dict(key="1002re1", sent="2026-10-03 09:12", frm="lm", reply_to="1002", suffix="_re1", covers=[],
         to=[EG], cc=[OPS],
         subject="RE: Yorkville - closing vendredi 2 oct",
         body="""Great Friday! Is that CAD? And how many Artem do you have left by size? Merch is asking which stores to prioritize for the re-order.

L.

Sent from my iPhone"""),

    dict(key="1002re2", sent="2026-10-03 10:05", frm="eg", reply_to="1002re1", suffix="_re2", covers=[],
         to=[LM], cc=[OPS, MERCH],
         subject="RE: Yorkville - closing vendredi 2 oct",
         body=f"""Hi Lauren, yes always CAD.

Artem (we only have black) on hand tonight : size 1 → 1, 2 → 2, 3 → 0 (since mid-Sept), 4 → 4, 5 → 1, 6 → 0, 7 → 1.
Because we advise one size down, the 3 and the 6 go first (clients who are normally a 4 or a 7). Please send 3, 5 and 6, we have enough 4.

Émilie

{SIG_EG}"""),

    dict(key="1003", sent="2026-10-03 19:31", frm="rc", mailer="iphone", covers=["2026-10-03"],
         subject="TOR EOD 10/03",
         body="""Net 29.8K vs 62.4 plan. 15 trx, 172 traffic. Same Saturday LY was ~56K so the plan isn't crazy, we just didn't convert.

Beanies, caps, turtlenecks, sweatshirts.

Missed: beanie white x2, Aurea cream 0, Amalia black 1, Ettore black 6, cable knit cream L.
Vel 2 zipper return.

Sent from my iPhone"""),

    dict(key="1004", sent="2026-10-04 19:08", frm="rc", mailer="iphone", covers=["2026-10-04"],
         subject="TOR EOD 10/04",
         body="""Net 14.9K vs 48.5 plan. Ouch. 9 trx

Missed:
Nova black 5 x2
Aurea black 0 and 1
Nova olive 6
Cosimo black 3
Artem black 6

Leafs preseason game tonight, Yorkville empty after 5

Sent from my iPhone"""),

    # 10/5 no own email; mentioned in 1006

    dict(key="1006", sent="2026-10-06 20:11", frm="eg", covers=["2026-10-06"],
         subject="Yorkville - closing 6 oct",
         body=f"""Bonsoir,

Ryan didn't send yesterday, Monday was ~$21K, 2 pink beanies, a Astra Oversized light blue and a Piero. Delivery 194 pieces received.

Today $43.6K vs $35.0K (+25%) ! Aria off-white x3, Nova black x2, 2 Astra capes (a couple, matching, c'est fou).

Asked : Aurea black 0, Artem black 6 (he was a 7 normally, so 6 was the right size).

{SIG_EG}"""),

    dict(key="1007", sent="2026-10-07 19:53", frm="eg", covers=["2026-10-07"],
         subject="Yorkville - closing 7 oct",
         body=f"""$38.6K vs $36.6K ✔. Caps, sweatshirts, padded cardigans black x2, Piero red.

Vel 4 zipper. That's the 6th since end of September. Please, do we have instruction to return the batch ?

Émilie"""),

    dict(key="1008", sent="2026-10-08 20:18", frm="eg", covers=["2026-10-08"],
         subject="Yorkville - closing 8 oct",
         body=f"""$42.9K vs $43.0K, on plan. Aurea beige x2, Astra Balaclava, Cortina.

Asked : Iridia off-white 3, turtleneck black M.
Returns : 4 (Vel zipper again, vlogo cardigan XXL, Vtrack gift, Alpina).

Émilie"""),

    dict(key="1009", sent="2026-10-09 20:47", frm="eg", covers=["2026-10-09"],
         subject="Yorkville - closing vendredi 9 oct",
         body=f"""Hi all,

$37.1K vs $49.6K. 14 transactions. Valdora off-white x2, Aurea beige x2, padded navy x2. Start of the Thanksgiving long weekend, lots of people leaving the city tonight.

Missed :
- padded cardigan navy XXL x2 (father and son)
- Liviana off-white 00
- Ettore black 5
- Artem black 6 (3rd time this week)
- cable knit cream L (4th time in 2 weeks !)
- tee white S

Artem 5 is finished too now.

{SIG_EG}"""),

    dict(key="1010", sent="2026-10-10 19:36", frm="eg", covers=["2026-10-10"],
         subject="Yorkville - closing 10 oct",
         body=f"""$23.4K vs $72.4K plan (-68%). Thanksgiving Saturday, the city went to the cottages. 12 transactions, vlogo cardigan black x4.

Hoodie grey M x2 asked, hoodie black XS. Artem 5 returned (size, took a 4 instead... exchange).

Émilie"""),

    dict(key="1011", sent="2026-10-11 18:29", frm="am", covers=["2026-10-11"],
         subject="TOR closing 11/10",
         body="""Hi!

$20.5K vs $48.2K plan, 9 transactions. Turtleneck navy x3 to a Chinese family.

Asked: vlogo cardigan black S, cable knit cream L.

Happy Thanksgiving everyone 🦃
Aisha"""),

    dict(key="1012", sent="2026-10-12 18:50", frm="rc", mailer="iphone", covers=["2026-10-12"],
         subject="TOR EOD 10/12",
         body="""Thanksgiving Monday, open 12-5. Net 25.4K vs 37.9 plan, 10 trx. Astra Oversized black, Cortina, Valdora cream.

Missed Aurea black 0 + 3, Valdora cream 2, padded grey XS. Aurea black now zero in 0-3. Delivery 145, no Aurea black inside.

Sent from my iPhone"""),

    dict(key="1013", sent="2026-10-13 20:02", frm="eg", covers=["2026-10-13"],
         subject="Yorkville - closing 13 oct",
         body=f"""Hi all,

$22.9K, 8 transactions. Aurea beige x2, Valdora black, Piero black.

Asked : Aurea black 2, Nova olive 6.

6 returns : Liviana 2, Aria 4 (size), Iridia 3 (colour, she wants pink...), beanie, and 2 more Vel with the zipper.

Émilie"""),

    dict(key="1014", sent="2026-10-14 20:09", frm="eg", covers=["2026-10-14"],
         subject="Yorkville - closing 14 oct",
         body=f"""$23.4K vs $42.4K. 7 transactions, small (beanies, gloves, Vtrack).

Asked : vlogo cardigan black S, sweatshirt grey XS. 1 more Vel zipper.

Lauren arrives tomorrow, we are ready ! Store visit at 11h.

Émilie"""),

    dict(key="1015", sent="2026-10-15 20:36", frm="eg", covers=["2026-10-15"],
         subject="Yorkville - closing 15 oct + visit",
         body=f"""Bonsoir,

$30.7K vs $46.5K. Padded cardigans black x2, caps, beanies. Jersey Polo black XL asked.

Merci Lauren for the visit today. Recap of what we discussed :
1. October plan : we are ~35% under, the plan assumes a big cold-weather month but it is still 12-15 degrees in the afternoon. The clients buy when it's cold in the morning, then they wait.
2. Aurea black : 0 in all sizes since the 12th, about 8 asks in October so far. Waitlist 9 names.
3. Artem : send 3/5/6 (see my email of Oct 3).
4. Vel : 11 zipper returns since Sept 28, we keep the stock in the back.
5. Astra : 8 pieces sold since launch, 1 returned. Better than we feared, but not a hit.

Émilie

{SIG_EG}"""),

    dict(key="1016", sent="2026-10-16 20:48", frm="eg", covers=["2026-10-16"],
         subject="Yorkville - closing vendredi 16",
         body=f"""$37.2K vs $52.9K. 12 transactions. Hoodies black x3, Aurea navy x2, Cortina.

Asked : Aurea black 2 (x2), Aurea black 4, Artem black 2 (a young girl who wanted the men's parka for her, the 2 would have been perfect), jersey polo white S.

Valdora 2 returned (change of mind).

Émilie"""),

    dict(key="1017", sent="2026-10-17 19:58", frm="rc", mailer="iphone", covers=["2026-10-17"],
         subject="TOR EOD 10/17",
         body="""Net 61.3K vs 73.4 plan. 21 trx, 223 traffic. Cold morning (2 degrees), people finally shopping for coats.

Iridia black x3, Vtracks, scarves, polos.

Missed (long one):
Aurea black 0 x2, 2, 3
Fiammetta black 00
Camilla cream 3
Nova olive 2
logo cardi black S
padded grey M

The Aurea black waitlist is now 12. Heard the DC got stock yesterday, can we confirm our allocation?

Sent from my iPhone"""),

    dict(key="1018", sent="2026-10-18 18:33", frm="am", covers=["2026-10-18"],
         subject="TOR closing 18/10",
         body="""Hi team,

$51.4K vs $56.1K plan. 16 transactions. Piero black x2, Camilla black x2, Monteluce black x2, hoodies.

Missed Aurea black 1. Cosimo 6 gift return, Vel 5 zipper return.

Aisha"""),

    dict(key="1019", sent="2026-10-19 19:22", frm="rc", mailer="iphone", covers=["2026-10-19"],
         subject="TOR EOD 10/18",
         body="""Net 23.4K vs 41.4 plan. 9 trx. Hoodies navy, Aria black x2.

Missed padded black XXL x2, padded black L, Aurea black 1, Aurea beige 1.

Sent from my iPhone"""),

    dict(key="1020", sent="2026-10-20 20:01", frm="eg", covers=["2026-10-20"],
         subject="Yorkville - closing 20 oct",
         body=f"""Hi all,

$32.9K vs $42.4K. Artem black x2 (sized down, perfect), gloves x2, Astra Cape white.

Aurea black 1 asked (again). Riviera 6 returned, quality (snap).

Delivery 202 pieces arrived with 1 day late, broker again. Still no Aurea black in it.

{SIG_EG}"""),

    dict(key="1021", sent="2026-10-21 20:14", frm="eg", covers=["2026-10-21"],
         subject="Yorkville - closing 21 oct",
         body=f"""$29.1K vs $44.2K. Padded cardigans black x2, women's Vtrack cream x2, Cortina. A group of American tourists from Buffalo.

Asked : hoodie grey M, Alpina black 41.
Liviana 0 returned, quality (the hood snap).

En tout cas, we need the Aurea black. Bonne soirée.

Émilie"""),
]
