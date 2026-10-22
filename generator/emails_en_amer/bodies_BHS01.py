STORE = "BHS01"

WRITERS = {
    "jk": "Jennifer Kim <jennifer.kim@moncler-retail.example>",
    "lo": "Luis Ortega <luis.ortega@moncler-retail.example>",
    "sm": "Sofia Marchetti <sofia.marchetti@moncler-retail.example>",
    "box": "BHS01 Beverly Hills <bhs01.store@moncler-retail.example>",
    "lm": "Lauren Mitchell <lauren.mitchell@moncler-retail.example>",
}

LM = "Lauren Mitchell <lauren.mitchell@moncler-retail.example>"
OPS = "retail-ops-usa@moncler-retail.example"
MERCH = "merch-planning-americas@moncler-retail.example"
CLI = "clienteling-na@moncler-retail.example"
JK = "Jennifer Kim <jennifer.kim@moncler-retail.example>"

DEFAULT_TO = [OPS]
DEFAULT_CC = [LM]

SIG_JK = """Jennifer Kim
Store Manager | Moncler Beverly Hills
363 N Rodeo Drive, Beverly Hills, CA 90210
O 310.555.0192"""

DISCLAIMER = """This message and any attachments are confidential and intended solely for the addressee. If you have received it in error, please notify the sender and delete it. Moncler USA Retail LLC."""

HABIT_LINES = [SIG_JK, DISCLAIMER, "Sent from my iPhone"]

EMAILS = [
    dict(key="0831", sent="2026-08-31 19:48", frm="lo", mailer="iphone", covers=["2026-08-31"],
         subject="eod bh",
         body="""7.6k vs 11 plan. 3 tickets, backpack + hoodie + cardi + a montcla black to a local guy. quiet monday, everybody's still in malibu

Sent from my iPhone"""),

    dict(key="0901", sent="2026-09-01 20:12", frm="jk", covers=["2026-09-01"],
         subject="BH Rodeo - EOD 09.01",
         body=f"""Hi team,

1) Sales: $8.0K vs $10.8K plan (-26%). 6 trx, ATV ~$1.3K.
2) Clienteling: called 14 clients re: FW26 arrivals, 3 appointments booked for next week.
3) Product: logo cardigan black XXL asked, we don't carry XXL in black. Insolux off-white sold (client going to Jackson Hole at Christmas).
4) Ops: nothing.

Thanks,
{SIG_JK}

{DISCLAIMER}"""),

    dict(key="0902", sent="2026-09-02 19:56", frm="jk", covers=["2026-09-02"],
         subject="BH Rodeo - EOD 09.02",
         body=f"""Hi team,

1) Sales: $1.0K net (-92%). 4 small sales, but a Maire 3 came back for size + gloves + a beanie gift return, so the net is almost nothing.
2) Clienteling: n/a
3) Product: logo tee white XXL asked.
4) Ops: AC is struggling in the afternoons, maintenance coming Friday.

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="0903", sent="2026-09-03 20:21", frm="jk", covers=["2026-09-03"],
         subject="BH Rodeo - EOD 09.03",
         body=f"""Hi team,

1) Sales: $27.6K vs $15.0K plan (+83%). 12 trx.
2) Clienteling: Mrs. A. came in with her daughter and a Brazilian friend, Maya black x3 and navy x2 for the family trip to St. Moritz. Great appointment (Sofia).
3) Product: missed Hermine black 0 (we are out) and Montcla black 2.
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="0904", sent="2026-09-04 20:07", frm="jk", covers=["2026-09-04"],
         subject="BH Rodeo - EOD 09.04",
         body=f"""1) Sales: $16.3K vs $18.3K. 12 trx.
2) Clienteling: 2 pulls out for a stylist (K.), returning Tuesday.
3) Product: gloves x3 (?), Maire navy x2. Missed Tib navy 1 and Insolux off-white 38.
4) Ops: long weekend schedule posted.

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="0905", sent="2026-09-05 19:44", frm="lo", mailer="iphone", covers=["2026-09-05"],
         subject="eod bh sat",
         body="""11.1k vs 24.9 plan. not great. lots of mexican tourists walking rodeo but buying tees and cardis, nothing big

guy wanted arneb black in a 3, we only have 4 and up. hermine 0 came back, she changed her mind

starting to get hot, 95 today 🥵

Sent from my iPhone"""),

    dict(key="0906", sent="2026-09-06 18:52", frm="lo", mailer="iphone", covers=["2026-09-06"],
         subject="eod bh",
         body="""13.6k vs 18.6. hermine navy x2 nice. arneb exchange from 6 to 5, client said it was huge. delivery 106 in

Sent from my iPhone"""),

    dict(key="0907", sent="2026-09-07 19:02", frm="lo", mailer="iphone", covers=["2026-09-07"],
         subject="eod labor day",
         body="""12.3k vs 15.1 plan, 6 trx. 2 more hermine navy (same family as yesterday came back for the sister). hermine navy 1 now gone

heat warning starts tomorrow, they're saying 105+ in the valley all week

Sent from my iPhone"""),

    dict(key="0908", sent="2026-09-08 20:15", frm="jk", covers=["2026-09-08"],
         subject="BH Rodeo - EOD 09.08 (heat)",
         body=f"""Hi team,

1) Sales: $6.4K vs $14.2K plan (-55%). 7 trx, all small (caps, hoodie, cardigan).
2) Clienteling: 2 appointments cancelled, "too hot to leave the house". Stylist K. returned the pulls, no purchase.
3) Product: nobody touched outerwear today. Maya 2 returned (size).
4) Ops: 99°F on Rodeo at 2pm, 108 in Woodland Hills. Our AC kept the floor at 76 but the entrance gets hot every time the door opens. We are offering water/sparkling to every client.

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="0909", sent="2026-09-09 20:09", frm="jk", covers=["2026-09-09"],
         subject="BH Rodeo - EOD 09.09",
         body=f"""1) Sales: $16.4K vs $15.4K (+7%). Saved by one ski client: Peyre red + Trailgrip for a December trip to Aspen. Rest was knit/sweatshirts.
2) Clienteling: Sofia sent 6 lookbooks to the "ski list".
3) Product: Maya navy 6 asked.
4) Ops: still 100+. Street empty from 12 to 5.

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="0910", sent="2026-09-10 20:31", frm="sm", covers=["2026-09-10"],
         subject="BH closing Thurs + pulls",
         body="""Hi everyone, Jen is off today so I'm closing.

$14.3K vs $16.9K plan, 8 transactions. A British couple and a Chinese student, the rest locals running in and out because of the heat (it was 103 at 3pm, I'm not kidding).

Pulls update:
- K. (stylist for our friend from the HBO series): took Maya black 4, Bady black 1, logo cardigan navy L for a press day next week. Back on 9/16.
- R. Studio: asked for Hermine, Maire and Ambrine for an editorial on 9/22, I'm holding 1 each in 1/2 until Monday. Please tell me if that's ok with the allocation.
- Nobody else.

No outerwear sold today at all.

Sofia

Sofia Marchetti
Senior Client Advisor | Moncler Beverly Hills"""),

    dict(key="0911", sent="2026-09-11 20:24", frm="jk", covers=["2026-09-11"],
         subject="BH Rodeo - EOD 09.11",
         body=f"""1) Sales: $14.2K vs $21.4K (-34%). 11 trx, mostly accessories and sneakers.
2) Clienteling: quiet, Rosh Hashanah tonight, several clients out.
3) Product: missed Ilvaro black 2, Maya navy 5, Valbourg black 00 (ski).
4) Ops: heat continues, 101 today.

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="0912", sent="2026-09-12 19:39", frm="lo", mailer="iphone", covers=["2026-09-12"],
         subject="eod bh",
         body="""9.6k vs 27.5 plan 😩 4 tickets on a saturday. polos x2, backpack, sweatshirt, turtleneck

104 people through the door but its 100 degrees, nobody's gonna try on a down jacket. 1 guy asked karakorum navy 2

they say it breaks tomorrow 🙏

Sent from my iPhone"""),

    dict(key="0913", sent="2026-09-13 19:06", frm="lo", mailer="iphone", covers=["2026-09-13"],
         subject="eod sun",
         body="""18k vs 20.8. heat broke, 84 today. ambrine black x2, scarves, trailgrips. brazilian family again

bady cream 3 asked, out. delivery 116

Sent from my iPhone"""),

    dict(key="0914", sent="2026-09-14 19:33", frm="lo", mailer="iphone", covers=["2026-09-14"],
         subject="eod bh mon",
         body="""10.4k vs 16. logo tee black x4, maya olive x2. pretty quiet

saw the new billboard on sunset this morning, looks sick 😎

Sent from my iPhone"""),

    dict(key="0915", sent="2026-09-15 20:18", frm="jk", covers=["2026-09-15"],
         subject="BH Rodeo - EOD 09.15",
         body=f"""1) Sales: $12.9K vs $15.2K. 13 trx (!), lots of small tickets.
2) Clienteling: campaign is live, 2 clients called to ask about "the jacket in the ad".
3) Product: Valbourg off-white sold (Deer Valley trip). Returns: Maire 0 (quality, seam), Hermine 4 (size), logo cardigan XXL (size).
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="0915dup", sent="2026-09-15 20:19", frm="jk", suffix="_dup", covers=[],
         subject="BH Rodeo - EOD 09.15",
         body=f"""1) Sales: $12.9K vs $15.2K. 13 trx (!), lots of small tickets.
2) Clienteling: campaign is live, 2 clients called to ask about "the jacket in the ad".
3) Product: Valbourg off-white sold (Deer Valley trip). Returns: Maire 0 (quality, seam), Hermine 4 (size), logo cardigan XXL (size).
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="0916", sent="2026-09-16 20:27", frm="jk", covers=["2026-09-16"],
         subject="BH Rodeo - EOD 09.16",
         body=f"""1) Sales: $25.0K vs $16.6K (+51%).
2) Clienteling: K. returned the HBO pulls and bought the Maya black for the client. Also a ski family (Valbourg black + women's Trailgrips).
3) Product: missed Bady off-white 3 (2nd time) and Ecrins black 6. Montcla navy 4 now out.
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="0917", sent="2026-09-17 20:12", frm="jk", covers=["2026-09-17"],
         subject="BH Rodeo - EOD 09.17",
         body=f"""1) Sales: $21.3K vs $19.2K. 14 trx.
2) Clienteling: n/a
3) Product: Tib black x2, Maya black x2. Missed Ilvaro black 3, Maya navy 5 (we are out of navy 5 for 2 weeks now, 3rd ask).
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="0918", sent="2026-09-18 20:33", frm="jk", covers=["2026-09-18"],
         subject="BH Rodeo - EOD 09.18",
         body=f"""1) Sales: $21.1K vs $22.4K. 14 trx.
2) Clienteling: Emmys week, 3 stylists in today. Pulls out: 6 pieces (list in the pull log).
3) Product:
- Montcla navy 2 asked twice + navy 4. We are out of both.
- Arneb black 3: 3rd client asking for a 3. Because we tell everyone to size down, the 3 is the size that moves and we don't have it. Please send 3s.
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="0919", sent="2026-09-19 20:02", frm="jk", covers=["2026-09-19"],
         subject="BH Rodeo - EOD 09.19",
         body=f"""Hi team,

1) Sales: $34.4K vs $30.9K (+11%). 20 trx. Best Saturday in a month.
2) Clienteling: Maya black x4 (2 clients), cable knit off-white x3, logo cardigans.
3) Product, missed:
Tib black 5
Arneb black 3 (again)
Rosiere olive 7
Valbourg off-white 1
logo cardigan navy XXL
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="0920", sent="2026-09-20 19:12", frm="lo", mailer="iphone", covers=["2026-09-20"],
         subject="eod bh",
         body="""3.6k vs 22.9 plan. yeah. 3 tickets

emmys today so all our stylist people were downtown and the regulars were at viewing parties i guess. plus yom kippur tonight. dead dead dead

missed hoodie navy XXL, sweatshirt grey S and XXL

Sent from my iPhone"""),

    dict(key="0921", sent="2026-09-21 19:41", frm="sm", covers=["2026-09-21"],
         subject="BH closing Mon + pulls",
         body="""Hi all,

$13.2K vs $17.1K plan, 7 transactions. Polos, tees, beanie.

Pulls: 4 of the 6 Emmys pieces came back today. One Bady black has foundation on the inside of the collar, sending to the cleaner (Madame Paulette) tomorrow, the stylist's office agreed to pay. 2 pieces still out (Hermine black 1, logo cardigan black M), back Wednesday.

A client asked for the Peyre red in a 7 for his ski trip, we only had 5. Could Aspen check?

Also Karakorum navy 3 asked.

Sofia"""),

    dict(key="0922", sent="2026-09-22 20:11", frm="jk", covers=["2026-09-22"],
         subject="BH Rodeo - EOD 09.22",
         body=f"""1) Sales: $12.1K vs $17.4K. 7 trx.
2) Clienteling: Brazilian couple (Karakorum black x2).
3) Product: Maya black 2 asked. Valbourg black sold (another ski client).
4) Ops: delivery from the DC due today did not arrive. Tracking says 9/25.

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="0923", sent="2026-09-23 20:20", frm="jk", covers=["2026-09-23"],
         subject="BH Rodeo - EOD 09.23",
         body=f"""1) Sales: $19.1K vs $19.3K. 10 trx.
2) Clienteling: Korean family, beanies + Maire off-white x2.
3) Product: logo cardigan navy XXL asked again.
4) Ops: delivery arrived after all (111 units), 3 days late vs the original ASN. Processing tomorrow morning.

{SIG_JK}

{DISCLAIMER}"""),

    # 9/24 missing (no email)

    dict(key="0925", sent="2026-09-25 20:40", frm="jk", covers=["2026-09-24", "2026-09-25"],
         subject="BH Rodeo - EOD 09.25",
         body=f"""Hi team, sorry, no recap yesterday, we had the Polaris setup and inventory of the late delivery until 9pm.

Thu 9/24: ~$11K, 5 trx. Polaris launched, window looks great, zero Polaris sold, 3 try-ons. Feedback: "fits like a kids size", "for $3K I expect more". Flammette black 1 asked.

Fri 9/25:
1) Sales: $27.8K vs $26.4K. 16 trx.
2) Clienteling: Korean clients, Bady black x2 and Hermine off-white x2. Peyre red sold.
3) Product: Ambrine black 2 asked.
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="0926", sent="2026-09-26 20:07", frm="jk", covers=["2026-09-26"],
         subject="BH Rodeo - EOD 09.26",
         body=f"""1) Sales: $32.1K vs $35.6K. 16 trx.
2) Clienteling: Maire black x2, Bady black x2.
3) Product: Maire black 3 and 4 asked, Maya navy 5 asked (4th time!). Maire black 3 and Tib black 5 now at zero.
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="0927", sent="2026-09-27 19:05", frm="lo", mailer="iphone", covers=["2026-09-27"],
         subject="eod bh",
         body="""19.2k vs 27.2. maire navy x2, maya black x2. 2 more asking maire black, a 0 and a 3. we're out of both. delivery 145 pcs

Sent from my iPhone"""),

    dict(key="0928", sent="2026-09-28 19:36", frm="lo", mailer="iphone", covers=["2026-09-28"],
         subject="eod mon",
         body="""24.9k vs 18.4 💪 maya black x4 (2 to a producer guy going to gstaad for xmas), montcla black x2, chambre cream x2

Sent from my iPhone"""),

    dict(key="0929", sent="2026-09-29 20:23", frm="jk", covers=["2026-09-29"],
         subject="BH Rodeo - EOD 09.29",
         body=f"""1) Sales: $15.5K vs $19.1K. 8 trx.
2) Clienteling: first Polaris sold, oversized black, to stylist K. for a music video. Retail clients still not biting.
3) Product: Valbourg black sold (ski).
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="0930", sent="2026-09-30 20:16", frm="jk", covers=["2026-09-30"],
         subject="BH Rodeo - EOD 09.30",
         body=f"""1) Sales: $28.4K vs $22.4K (+27%). 11 trx. September closes at ~$493K vs ~$587K plan (-16%), heat week cost us a lot.
2) Clienteling: Polaris cape black sold (2nd Polaris, again a stylist, not a retail client).
3) Product: Chambre off-white 2 asked.
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="1001", sent="2026-10-01 20:09", frm="jk", covers=["2026-10-01"],
         subject="BH Rodeo - EOD 09.31",
         body=f"""1) Sales: $30.3K vs $23.7K (+28%). 19 trx.
2) Clienteling: Chinese clients (beanies x3, Montgenevre black x2, Maya black x2).
3) Product: crewneck white M asked. Montgenevre black 5 at zero. Tib 3 returned, zipper slider broke after 2 wears (DEF). First one we see.
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="1002", sent="2026-10-02 20:28", frm="jk", covers=["2026-10-02"],
         subject="BH Rodeo - EOD 10.02",
         body=f"""1) Sales: $25.2K vs $27.6K. 15 trx.
2) Clienteling: Ambrine black x2 and Hermine navy x2, all on appointments.
3) Product: missed Hermine off-white 2, Chambre black 2, Montgenevre black 5. Maire off-white 3 now out.
4) Ops: hoodie XL returned with a hole in the cuff.

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="1003", sent="2026-10-03 20:14", frm="jk", covers=["2026-10-03"],
         subject="BH Rodeo - EOD 10.03 + WTD",
         html="""<html><body style="font-family:Calibri,Arial,sans-serif;font-size:11pt">
<p>Hi team,</p>
<p>1) Sales: $32.7K vs $37.5K (-13%). 17 trx. Padded cardigans x5 (navy + black).<br>
2) Clienteling: Mexican family from Guadalajara.<br>
3) Product: Insolux off-white 38 asked. Tib 5 returned, zipper (DEF), 2nd one this week.<br>
4) Ops: WTD below.</p>
<table border="1" cellspacing="0" cellpadding="3" style="border-collapse:collapse;font-size:10pt">
<tr style="background:#1f1f1f;color:#fff"><th>Day</th><th>Net Sales</th><th>Plan</th><th>vs Plan</th><th>Trx</th></tr>
<tr><td>Sun 9/27</td><td>$19,200</td><td>$27,200</td><td>-29%</td><td>9</td></tr>
<tr><td>Mon 9/28</td><td>$24,900</td><td>$18,400</td><td>+35%</td><td>13</td></tr>
<tr><td>Tue 9/29</td><td>$15,500</td><td>$19,100</td><td>-19%</td><td>8</td></tr>
<tr><td>Wed 9/30</td><td>$28,400</td><td>$22,400</td><td>+27%</td><td>11</td></tr>
<tr><td>Thu 10/1</td><td>$30,300</td><td>$23,700</td><td>+28%</td><td>19</td></tr>
<tr><td>Fri 10/2</td><td>$25,200</td><td>$27,600</td><td>-9%</td><td>15</td></tr>
<tr><td>Sat 10/3</td><td>$32,700</td><td>$37,500</td><td>-13%</td><td>17</td></tr>
<tr style="font-weight:bold"><td>WTD</td><td>$176,200</td><td>$175,900</td><td>0%</td><td>92</td></tr>
</table>
<p>Jennifer Kim<br>Store Manager | Moncler Beverly Hills</p>
</body></html>""",
         body=f"""Hi team,

1) Sales: $32.7K vs $37.5K (-13%). 17 trx. Padded cardigans x5 (navy + black).
2) Clienteling: Mexican family from Guadalajara.
3) Product: Insolux off-white 38 asked. Tib 5 returned, zipper (DEF), 2nd one this week.
4) Ops: WTD below.

Day        Net Sales  Plan     vs Plan  Trx
Sun 9/27   $19,200    $27,200  -29%     9
Mon 9/28   $24,900    $18,400  +35%     13
Tue 9/29   $15,500    $19,100  -19%     8
Wed 9/30   $28,400    $22,400  +27%     11
Thu 10/1   $30,300    $23,700  +28%     19
Fri 10/2   $25,200    $27,600  -9%      15
Sat 10/3   $32,700    $37,500  -13%     17
WTD        $176,200   $175,900  0%      92

{SIG_JK}"""),

    dict(key="1004", sent="2026-10-04 19:01", frm="lo", mailer="iphone", covers=["2026-10-04"],
         subject="eod bh sunday",
         body="""35k vs 27.8 🙌 karakorum navy x2, hermine navy x2, montcla navy x2. good sunday, cooler weather finally makes people think about jackets

delivery 136

Sent from my iPhone"""),

    dict(key="1005", sent="2026-10-05 19:28", frm="lo", mailer="iphone", covers=["2026-10-05"],
         subject="eod mon",
         body="""22.1k on 21 plan. insolux cream x2 (ski mom + daughter), maya black x2, polaris balaclava

chambre black 2 and 4 asked, out

4 returns: maire 2 size, maya 6, hoodie, cap

Sent from my iPhone"""),

    dict(key="1006", sent="2026-10-06 20:19", frm="jk", covers=["2026-10-06"],
         subject="BH Rodeo - EOD 10.06",
         body=f"""1) Sales: $23.2K vs $21.6K (+7%). 12 trx.
2) Clienteling: British clients (2), hoodies navy x4 for a production crew gift.
3) Product, missed: Chambre black 2 (3rd ask in 2 days), Tib black 7, padded cardigan navy XS, crewneck white XL.
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="1007", sent="2026-10-07 20:05", frm="jk", covers=["2026-10-07"],
         subject="BH Rodeo - EOD 10.07",
         body=f"""1) Sales: $13.7K vs $23.1K (-41%). 10 trx.
2) Clienteling: Brazilian group, gloves + Maya olive + Insolux off-white x2 (ski in Bariloche next year? they said "Aspen in January").
3) Product: Flammette navy 3 asked. Returns: Karakorum 3, Rosiere 4 (size), Insolux 39.
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="1008", sent="2026-10-08 20:31", frm="jk", covers=["2026-10-08"],
         subject="BH Rodeo - EOD 10.08",
         body=f"""Hi team,

1) Sales: $37.0K vs $25.5K (+45%). 21 trx.
2) Clienteling: Polaris cape sold (stylist again). Maire navy x3.
3) Product, long list of misses today:
- Maire black 3
- Flammette navy 3 (2nd)
- Maya olive 2
- Rosiere olive 7
- logo cardigan black XS
- cable knit black XL
Black Maire: zero left in 0, 1 and 3. We sell it every week here, when will we get some?
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="1009", sent="2026-10-09 20:22", frm="jk", covers=["2026-10-09"],
         subject="BH Rodeo - EOD 10.09",
         body=f"""1) Sales: $27.4K vs $30.3K. 16 trx.
2) Clienteling: n/a
3) Product: Valbourg black 4 asked (ski). Ilvaro 1 returned, change of mind.
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="1010", sent="2026-10-10 19:57", frm="jk", covers=["2026-10-10"],
         subject="BH Rodeo - EOD 10.10",
         body=f"""1) Sales: $29.3K vs $42.4K (-31%). 16 trx. 200+ traffic, lots of tourists (Mexico, Middle East), low conversion.
2) Clienteling: Polaris balaclava sold.
3) Product: missed Bady off-white 00, Ambrine black 1.
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="1011", sent="2026-10-11 19:12", frm="lo", mailer="iphone", covers=["2026-10-11"],
         subject="eod sun",
         body="""40k vs 31 plan 🔥 hermine navy x4 and tib black x4. tib black 3 now gone and hermine navy 0 and 3 too

missed:
turtleneck black XS x2
maire black 1
cable knit cream L
polo navy M

delivery 188

Sent from my iPhone"""),

    dict(key="1012", sent="2026-10-12 19:33", frm="lo", mailer="iphone", covers=["2026-10-12"],
         subject="eod bh",
         body="""17k vs 22. rosiere black x2. turtleneck black M x2 asked + polo navy M, knit sizes keep running out

Sent from my iPhone"""),

    dict(key="1013", sent="2026-10-13 20:04", frm="jk", covers=["2026-10-13"],
         subject="BH Rodeo - EOD 10.13",
         body=f"""1) Sales: $12.9K vs $22.8K (-43%). 10 trx.
2) Clienteling: ski clients again, Insolux black x2, Trailgrips.
3) Product: Maire black 1 asked, Trailgrip black 45.
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="1014", sent="2026-10-14 20:12", frm="sm", covers=["2026-10-14"],
         subject="BH closing Wed",
         body="""Hi all, closing tonight for Jen.

$22.2K vs $23.3K plan, 13 transactions. Bady black x4 (two sisters, both a 1 and a 2), women's Trailgrips, Chambre black.

Misses: Chambre black 0, crewneck black XXL, women's Trailgrip black 36.

Maire black now out in every size 0-3. I have 6 clients waiting for it, mostly sizes 1 and 2. Is there any chance of a transfer from Madison or SoHo?

Sofia"""),

    dict(key="1015", sent="2026-10-15 20:25", frm="jk", covers=["2026-10-15"],
         subject="BH Rodeo - EOD 10.15",
         body=f"""1) Sales: $10.6K vs $28.6K (-63%). 9 trx. 140 people in, Korean tourists mostly browsing.
2) Clienteling: n/a
3) Product: Maire black 0 and 3 asked (out). Trailgrip grey 45, women's Trailgrip black 40. Insolux black x3 sold (ski).
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="1016", sent="2026-10-16 20:41", frm="jk", covers=["2026-10-16"],
         subject="BH Rodeo - EOD 10.16",
         body=f"""Hi team,

1) Sales: $44.8K vs $30.7K (+46%). 17 trx.
2) Clienteling: big day with a studio wardrobe buy (see below). Brazilian and Korean clients too.
3) Product, missed:
Maire black 2
Maya black 2
Montgenevre black 7
Tib black 3
women's Trailgrip black 39
Insolux black 37
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="1016re1", sent="2026-10-17 07:58", frm="lm", reply_to="1016", suffix="_re1", covers=[],
         to=[JK], cc=[OPS],
         subject="RE: BH Rodeo - EOD 10.16",
         body="""Great day Jen. What was the studio buy exactly? Want to make sure we don't read +46% as a trend in the forecast review on Monday.

L.

Sent from my iPhone"""),

    dict(key="1016re2", sent="2026-10-17 09:46", frm="jk", reply_to="1016re1", suffix="_re2", covers=[],
         to=[LM], cc=[OPS, CLI],
         subject="RE: BH Rodeo - EOD 10.16",
         body=f"""Hi Lauren,

Costume dept of a streaming series (Sofia's contact) bought 4 Maire off-white + 3 padded cardigans black for a winter episode, ~$12K in one ticket. Without it the day would be ~$33K, so close to plan. Definitely one-off.

Jen

{SIG_JK}

> On Oct 17, 2026, at 7:58 AM, Lauren Mitchell <lauren.mitchell@moncler-retail.example> wrote:
> Great day Jen. What was the studio buy exactly?"""),

    # 10/17 no own email; combined in 1018 by Luis

    dict(key="1018", sent="2026-10-18 19:27", frm="lo", mailer="iphone", covers=["2026-10-17", "2026-10-18"],
         subject="eod sat + sun",
         body="""forgot to send yesterday, sorry jen

sat 37.5k vs 47.2. beanies, trailgrips, maya olive x2, maire beige x2. 1 bady black 3 asked
sun 29.1k vs 35.2. turtleneck black x3, cardis, insolux black x2

sunday misses: maire black 1 (always), montcla navy 3, logo cardi navy M, cable knit cream XXL, insolux black 35 (ski girl, tiny feet lol)

2 bady 0 returned same client changed mind. delivery 184 in

Sent from my iPhone"""),

    dict(key="1019", sent="2026-10-19 19:41", frm="lo", mailer="iphone", covers=["2026-10-19"],
         subject="eod bh",
         body="""25.9k vs 23.7 ✅ chinese clients, tib black x2, bady cream x2

beanie back with a loose pompom lol

Sent from my iPhone"""),

    dict(key="1020", sent="2026-10-20 20:16", frm="jk", covers=["2026-10-20"],
         subject="BH Rodeo - EOD 10.20",
         body=f"""1) Sales: $36.0K vs $25.1K (+44%). 20 trx. No single big ticket today, just a good steady day, cooler weather.
2) Clienteling: Hermine black x2, Montgenevre black x2.
3) Product: Maire black 2 asked, Montcla navy 3 (2nd), cable knit black XS. Montcla navy 5 out too.
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),

    dict(key="1021", sent="2026-10-21 20:08", frm="jk", covers=["2026-10-21"],
         subject="BH Rodeo - EOD 10.21",
         body=f"""1) Sales: $22.0K vs $25.4K. 14 trx.
2) Clienteling: a stylist asked for the Ilvaro in powder pink, size 3, "the one from the K-pop photo". We never received pink in BH. Is there any for the US?
3) Product: Karakorum navy 2 asked. Insolux black x2 sold. Bady off-white 3 out again.
4) Ops: n/a

{SIG_JK}

{DISCLAIMER}"""),
]
