STORE = "ASP01"

WRITERS = {
    "hn": "Hannah Novak <hannah.novak@valentino-retail.example>",
    "cd": "Chris Delgado <chris.delgado@valentino-retail.example>",
    "ml": "Megan Liu <megan.liu@valentino-retail.example>",
    "box": "ASP01 Aspen <asp01.store@valentino-retail.example>",
    "lm": "Lauren Mitchell <lauren.mitchell@valentino-retail.example>",
}

LM = "Lauren Mitchell <lauren.mitchell@valentino-retail.example>"
OPS = "retail-ops-usa@valentino-retail.example"
MERCH = "merch-planning-americas@valentino-retail.example"
HN = "Hannah Novak <hannah.novak@valentino-retail.example>"

DEFAULT_TO = [OPS]
DEFAULT_CC = [LM]

HABIT_LINES = ["Sent from my iPhone", "Hannah Novak\nStore Manager, Valentino Aspen\n520 E Hyman Ave, Aspen CO 81611"]
SIG_HN = "Hannah Novak\nStore Manager, Valentino Aspen\n520 E Hyman Ave, Aspen CO 81611"

EMAILS = [
    dict(key="0831", sent="2026-08-31 18:41", frm="cd", mailer="iphone", covers=["2026-08-31"],
         subject="asp eod",
         body="""2.5k, 3 trx. backpack, hoodie, camilla. guy wanted a vel black 1, and mario navy 5. -C

Sent from my iPhone"""),

    dict(key="0901", sent="2026-09-01 18:37", frm="hn", covers=["2026-09-01"],
         subject="Aspen closing Tuesday 9/1",
         body=f"""Hi all,

Two sales today, $2.5K total (Aurea navy and a navy backpack). A Chinese couple staying at the Little Nell, they said they are coming back for ski in February.

Gorgeous day, 78 and blue sky. Town is starting to fill up for the Labor Day weekend, JAS is in Snowmass Friday to Sunday so we should see some people.

{SIG_HN}"""),

    dict(key="0902", sent="2026-09-02 18:52", frm="hn", covers=["2026-09-02"],
         subject="Aspen closing Wed 9/2",
         body=f"""Hi all,

No sales today, and a jersey polo came back (gift return) so we are actually negative (-$525). 21 people in.

We had 3 asks we couldn't do: Aria black 00, Vel off-white 2, Vtrack grey 46. All sizes we just don't get here.

{SIG_HN}"""),

    dict(key="0903", sent="2026-09-03 18:33", frm="hn", covers=["2026-09-03"],
         subject="Aspen closing Thu 9/3",
         body=f"""Hi all,

$5.0K, 4 transactions. First ski piece of the season sold, a black Valdora to Mrs. Feldman (Red Mountain), she wanted to be "ahead of the crowd". Also a Aria black, sweatshirt, beanie.

{SIG_HN}"""),

    dict(key="0904", sent="2026-09-04 18:45", frm="hn", covers=["2026-09-04"],
         subject="Aspen closing Fri 9/4",
         body=f"""$2.8K, 5 small transactions (tees, scarf, Camilla).

Asks: Amalia in chocolate brown size 0 (lady visiting from Dallas saw it on Instagram) and Nova olive 5. We don't have brown at all.

Hannah"""),

    dict(key="0905", sent="2026-09-05 18:58", frm="hn", covers=["2026-09-05"],
         subject="Aspen closing Sat 9/5",
         body=f"""Hi all,

$8.1K vs $8.8K plan, 5 transactions. Busiest day in a while (40ish people). Aria black x2, Riviera black, hoodie.

A young woman wanted a pink Iridia in 3. We never got pink here, only the black.

Aria black 1 and 3 are gone now.

{SIG_HN}"""),

    dict(key="0906", sent="2026-09-06 18:22", frm="cd", mailer="iphone", covers=["2026-09-06"],
         subject="asp eod sun",
         body="""4.9k 4 trx. vel black, padded cardi, scarf, vtrack. 24 units delivery in. -C

Sent from my iPhone"""),

    dict(key="0907", sent="2026-09-07 18:15", frm="cd", mailer="iphone", covers=["2026-09-07"],
         subject="asp eod",
         body="""donut today. 0 sales. 18 people, all browsing on their way out of town. labor day = everyone driving back to denver

-C

Sent from my iPhone"""),

    dict(key="0908", sent="2026-09-08 18:36", frm="hn", covers=["2026-09-08"],
         subject="Aspen closing 9/8",
         body=f"""Hi all,

$3.7K, 3 transactions. Liviana off-white (local, Mrs. Castellano), beanie, tee, sweatshirt.

Officially shoulder season. Half of Main Street restaurants posted their closing dates, the Gondola stops this weekend. Only 15 people in today.

{SIG_HN}"""),

    dict(key="0909", sent="2026-09-09 18:41", frm="hn", covers=["2026-09-09"],
         subject="Aspen closing 9/9",
         body=f"""Negative day again, -$1.6K. We sold a cap and a sweatshirt but an Ettore 4 came back (gift, the wife bought the wrong size, they will come back later) and a Vtrack 43 for size.

{SIG_HN}"""),

    dict(key="0910", sent="2026-09-10 18:47", frm="ml", covers=["2026-09-10"],
         subject="Aspen store - closing report Thursday 9/10",
         body="""Hi everyone!

Megan here, closing tonight since Hannah and Chris are both off. Here is today:

Sales: 1 Aria black, but we also had a return of a Valdora size 1 (client didn't like the colour, she wants the off-white which we don't have in 1), so net it's about -$900.
Traffic: 20
Asks: a lady asked for the Camilla black in 3.

Question: should I put the Valdora back on the floor or keep it in the back for the ski season display? I left it in the back for now.

Thank you!
Megan"""),

    dict(key="0911", sent="2026-09-11 18:39", frm="hn", covers=["2026-09-11"],
         subject="Aspen closing 9/11",
         body=f"""$4.7K, one client (Houston, second home in Starwood): Piero black, beanie, vlogo cardigan navy, women's Vtrack.

Megan, keep the Valdora in the back, thanks.

Hannah"""),

    dict(key="0912", sent="2026-09-12 18:55", frm="hn", covers=["2026-09-12"],
         subject="Aspen closing Sat 9/12",
         body=f"""Hi all,

$5.1K vs $8.0K plan. 2 transactions. Vtrack, padded cardigan, Riviera black and a Aurea black (Mrs. Feldman again, her daughter this time).

Vlogo Hoodie navy M asked, the client exchanged his M for the black yesterday and we didn't have navy M either.

Leaves are starting to turn up at Maroon Bells, should bring the leaf peepers in the next 2 weeks.

{SIG_HN}"""),

    dict(key="0913", sent="2026-09-13 18:28", frm="cd", mailer="iphone", covers=["2026-09-13"],
         subject="asp eod",
         body="""1.2k. beanie, gloves, tee. ettore black 2 asked. delivery 18 units

Sent from my iPhone"""),

    # 9/14 missing (Chris)

    dict(key="0915", sent="2026-09-15 18:49", frm="hn", covers=["2026-09-15"],
         subject="Aspen closing 9/15",
         body=f"""Hi all,

Chris didn't send last night, Monday was $3.0K (cap, vlogo cardigan black, Ettore black).

Today $1.7K, 2 transactions (backpack, beanie, sweatshirt). 15 people.

Not much else. The new campaign is everywhere on Instagram but we don't feel it here, no billboards in the valley.

{SIG_HN}"""),

    dict(key="0916", sent="2026-09-16 18:41", frm="hn", covers=["2026-09-16"],
         subject="Aspen closing 9/16",
         body=f"""$5.0K vs $4.0K plan, 3 transactions. A Korean family on a Colorado road trip, Nova navy + Aurea navy + belt bag. Vlogo Cardigan black too.

Aurea navy 2 and Nova navy 4 are out now.

Hannah"""),

    dict(key="0917", sent="2026-09-17 18:35", frm="hn", covers=["2026-09-17"],
         subject="Aspen closing 9/17",
         body=f"""$3.8K. Piero black and Vel off-white, 2 clients. One from London.

Piero black is now down to 1 piece in a 5. If we get the early ski crowd in October we will be short.

Hannah"""),

    dict(key="0918", sent="2026-09-18 18:52", frm="ml", covers=["2026-09-18"],
         subject="Aspen store - closing report Friday 9/18",
         body="""Hi everyone,

Sales: $900 (1 vlogo cardigan navy)
Traffic: 20
Asks: none

It was really quiet, I used the time to count the back room. We have 41 down jackets and only 6 ski pieces (Piero, Valdora, Cortina). Is the ski allocation coming in October or November? Last year I think it came before Halloween?

Thanks!
Megan"""),

    dict(key="0919", sent="2026-09-19 18:47", frm="hn", covers=["2026-09-19"],
         subject="Aspen closing Sat 9/19",
         body=f"""Hi all,

$3.2K vs $7.3K plan, one client (Cosimo navy, vlogo cardigan, turtleneck, Vtrack). 32 people in, almost all leaf peepers from Texas and Denver, cameras out, not shopping.

To Megan's question: the ski allocation last year arrived Oct 28 in 2 shipments. Lauren/merch, can you confirm the dates for this year?

{SIG_HN}"""),

    dict(key="0920", sent="2026-09-20 18:31", frm="cd", mailer="iphone", covers=["2026-09-20"],
         subject="asp eod sun",
         body="""6k, 5 trx, beat plan. nova black, monteluce navy, belt bag, beanie. vtrack 46 back. gloves back for size

aspens are full gold, town busy for once

Sent from my iPhone"""),

    dict(key="0921", sent="2026-09-21 18:26", frm="cd", mailer="iphone", covers=["2026-09-21"],
         subject="asp eod",
         body="""5.1k on 4.2 plan. 4 trx. brits + some international, scarf, pink beanie, vtrack, alpina cream (first boots of the year)

-C

Sent from my iPhone"""),

    dict(key="0922", sent="2026-09-22 18:44", frm="ml", covers=["2026-09-22"],
         subject="Aspen store - closing report Tuesday 9/22",
         body="""Hi everyone,

Sales: $35K
Transactions: 3 (belt bag, padded cardigan navy, Aria black)
Traffic: 15
Asks:
- Aurea navy 00
- Aria black 2
- Aria powder pink 0 (Chinese student, she showed me a picture)
Delivery: 16 units arrived, it was supposed to come Sunday.

Megan"""),

    dict(key="0922corr", sent="2026-09-22 19:03", frm="ml", reply_to="0922", suffix="_corr", covers=[],
         subject="RE: Aspen store - closing report Tuesday 9/22",
         body="""Sorry!! Sales were $3.5K not $35K, I missed the decimal.

Megan"""),

    dict(key="0923", sent="2026-09-23 18:38", frm="hn", covers=["2026-09-23"],
         subject="Aspen closing 9/23",
         body=f"""$2.5K, 2 transactions (Nova black, beanie, cap, belt bag). Belt bag returned too, change of mind.

Nova black 5 is now out.

Hannah"""),

    dict(key="0924", sent="2026-09-24 18:50", frm="hn", covers=["2026-09-24"],
         subject="Aspen closing 9/24",
         body=f"""Hi all,

$2.8K. Nova black x2 (father and son), beanie, cable knit. Monteluce 4 returned, too small in the shoulders.

We didn't receive any Astra and honestly I don't think we need it here, our clients want technical ski stuff, not capes.

{SIG_HN}"""),

    dict(key="0925", sent="2026-09-25 18:43", frm="hn", covers=["2026-09-25"],
         subject="Aspen closing 9/25",
         body=f"""$7.7K vs $6.1K plan. Piero black (our last one, size 5), Alpina off-white, Monteluce black, beanie. 3 clients. Nice Friday.

We are out of Piero black completely now. Aria black 3 out too.

Hannah"""),

    dict(key="0926", sent="2026-09-26 18:56", frm="hn", covers=["2026-09-26"],
         subject="Aspen closing Sat 9/26",
         body=f"""Hi all,

$4.4K vs $8.0K plan, 4 transactions, all small (cap, hoodie, sweatshirt, Vtrack).

Lost 4 outerwear sales today, all size problems:
Liviana off-white 4
Nova olive 2
Cosimo navy 3
Monteluce navy 2

With 210 sqm we can't carry every size, but in shoulder season when 30 people come in and 4 ask for something specific, that's our month.

{SIG_HN}"""),

    dict(key="0927", sent="2026-09-27 18:29", frm="cd", mailer="iphone", covers=["2026-09-27"],
         subject="asp eod",
         body="""8.9k 🙌 valdora off white + padded cardi + cap + beanie. chinese couple bought the valdora for niseko lol

27 units in

Sent from my iPhone"""),

    dict(key="0928", sent="2026-09-28 18:12", frm="cd", mailer="iphone", covers=["2026-09-28"],
         subject="asp eod",
         body="""zero. 17 people, nobody bought anything. monday after the leaf weekend, town is dead

Sent from my iPhone"""),

    dict(key="0928re1", sent="2026-09-29 08:05", frm="lm", reply_to="0928", suffix="_re1", covers=[],
         to=[HN], cc=["Chris Delgado <chris.delgado@valentino-retail.example>", OPS],
         subject="RE: asp eod",
         body="""Hannah, that's the second zero day this month (Labor Day was the other). Can you propose reduced hours for Mon-Wed through Thanksgiving? Let's talk on our Thursday call. Need it before we finalize the payroll plan for Q4.

Thanks,
Lauren

Lauren Mitchell
Area Manager USA & Canada"""),

    dict(key="0928re2", sent="2026-09-29 11:37", frm="hn", reply_to="0928re1", suffix="_re2", covers=[],
         to=[LM], cc=["Chris Delgado <chris.delgado@valentino-retail.example>", OPS],
         subject="RE: asp eod",
         body=f"""Hi Lauren,

Proposal: Mon-Wed 11-5 from Oct 12 to Nov 22, Thu-Sun stay 10-6. That keeps 2 people per shift and saves ~70 hours. I'd keep full hours from Nov 23 for the opening week. Most of our Mon-Wed traffic is 15-20 people anyway.

Also a reminder that we need 2 seasonal hires for Thanksgiving to April. I have 3 candidates (one J-1 from Argentina, she worked in Bariloche).

{SIG_HN}

-----Original Message-----
From: Lauren Mitchell
Sent: Tuesday, September 29, 2026 8:05 AM
Subject: RE: asp eod

Hannah, that's the second zero day this month (Labor Day was the other)."""),

    dict(key="0929", sent="2026-09-29 18:39", frm="hn", covers=["2026-09-29"],
         subject="Aspen closing 9/29",
         body=f"""$3.9K, 4 transactions. Mexican couple and a British guy. Vel black, padded cardigan navy, backpack, sweatshirt.

Piero black 2 asked (a woman wanted it for herself, the men's 2 fits like a women's 4). We have zero Piero black.

Hannah"""),

    dict(key="0930", sent="2026-09-30 18:44", frm="hn", covers=["2026-09-30"],
         subject="Aspen closing 9/30",
         body=f"""Hi all,

$1.4K net. Valdora black, Monteluce navy, belt bag, but 2 returns:
- Artem 5, client said it was huge, went back to Chicago and decided not to exchange
- Vel 3, zipper slider broke (the pull came off), first defect we see on Vel

Navy beanie asked, we're out of navy beanies (?!). September closes around $97K vs $148K plan. Shoulder season plan was too aggressive.

{SIG_HN}"""),

    dict(key="1001", sent="2026-10-01 18:36", frm="hn", covers=["2026-10-01"],
         subject="Aspen closing 10/1",
         body=f"""-$1.3K today. A beanie and a cable knit sold, but an Artem 3 came back (quality, a seam on the hood opening). That's 2 Artem back in 2 days.

Hannah"""),

    dict(key="1002", sent="2026-10-02 18:48", frm="ml", covers=["2026-10-02"],
         subject="Aspen store - closing report Friday 10/2",
         body="""Hi everyone,

Sales: $2.0K
Transactions: 2 (scarf grey, hoodie navy, women's Vtrack)
Traffic: 23
Asks: Aurea off-white 00

Is it true we're closing early Mon-Wed from the 12th? Somebody asked me and I didn't know what to say.

Megan"""),

    dict(key="1003", sent="2026-10-03 18:51", frm="hn", covers=["2026-10-03"],
         subject="Aspen closing Sat 10/3",
         body=f"""$5.7K vs $8.7K plan, 5 transactions. Scarf, gloves, Vtrack, Monteluce navy. A Mexican family.

Monteluce black 3 asked and vlogo hoodie navy S.

Megan, yes Mon-Wed 11-5 from Oct 12, I'll post it.

Hannah"""),

    dict(key="1004", sent="2026-10-04 18:33", frm="cd", mailer="iphone", covers=["2026-10-04"],
         subject="asp eod sunday",
         body="""8.2k on 6.6. aurea navy x2 (mother/daughter), aurea black, liviana navy, piero black (from the delivery, 35 units in this morning, 2 piero came in)

vel 5 back zipper. 2nd one

Sent from my iPhone"""),

    dict(key="1005", sent="2026-10-05 18:27", frm="cd", mailer="iphone", covers=["2026-10-05"],
         subject="asp eod",
         body="""2.9k. aurea black, beanie, backpack. grey scarf asked (sold the last one sat)

Sent from my iPhone"""),

    # 10/6 missing (Megan); mentioned in 1007

    dict(key="1007", sent="2026-10-07 18:42", frm="hn", covers=["2026-10-07"],
         subject="Aspen closing 10/7",
         body=f"""Hi all,

Yesterday Megan forgot to send, it was a one-beanie day ($300).

Today $9.3K vs $5.4K plan! 6 transactions. Valdora black, Nova olive, pink beanie, cap and two Brazilian clients who are here early to look at a house in Snowmass.

Aurea navy 00 asked (second time in a week, not a size we ever get).

{SIG_HN}"""),

    dict(key="1008", sent="2026-10-08 18:39", frm="hn", covers=["2026-10-08"],
         subject="Aspen closing 10/8",
         body=f"""$4.5K, 3 transactions. Caps, belt bag, hoodie navy.

Snow in the forecast for next week above 11,000 ft! The mood in town changed overnight, everybody is talking about opening day.

Hannah"""),

    dict(key="1009", sent="2026-10-09 18:57", frm="hn", covers=["2026-10-09"],
         subject="Aspen closing Fri 10/9",
         body=f"""Hi all,

$7.7K vs $6.8K plan, 3 transactions. Logo cardigans navy x2, Piero black, Cortina black, belt bag. First Cortina of the year.

Lost:
- Aurea black 2
- Aurea navy 1 and 2 (same lady, she would have taken either)
- Piero black 3

The door counter was offline all day (power blip this morning reset the sensor, IT says it's back tonight). I'd guess ~25 people.

{SIG_HN}"""),

    dict(key="1010", sent="2026-10-10 18:49", frm="hn", covers=["2026-10-10"],
         subject="Aspen closing Sat 10/10",
         body=f"""$6.5K vs $9.4K, 6 transactions (beanies x2, belt bag, Nova navy...). Valdora black 2 asked, out.

Hannah"""),

    dict(key="1011", sent="2026-10-11 18:24", frm="cd", mailer="iphone", covers=["2026-10-11"],
         subject="asp eod",
         body="""2.6k. vtrack, jersey polo, nova black. aurea black 1 and nova olive 3 asked. 42 units in, mostly knit

Sent from my iPhone"""),

    dict(key="1012", sent="2026-10-12 17:31", frm="cd", mailer="iphone", covers=["2026-10-12"],
         subject="asp eod (new hours)",
         body="""first day 11-5. 6.8k, 2 trx: cortina + nova navy + vel black + amalia black. not bad for a monday

Sent from my iPhone"""),

    dict(key="1013", sent="2026-10-13 18:41", frm="hn", covers=["2026-10-13"],
         subject="Aspen closing 10/13",
         body=f"""Hi all,

$9.0K vs $5.1K plan, 5 transactions. 2 navy backpacks, Piero black, Valdora off-white, beanie.

It snowed on top of Ajax last night!! White down to about 10,000 ft this morning. Clients walking in asking "is the ski stuff in yet". This is the moment, and we have 2 Piero and 1 Valdora in the store.

{SIG_HN}"""),

    dict(key="1014", sent="2026-10-14 18:36", frm="hn", covers=["2026-10-14"],
         subject="Aspen closing 10/14",
         body=f"""$6.9K, 2 transactions. Monteluce navy, Fiammetta navy, Amalia black.

More snow up high. Independence Pass was closed this morning for snow and ice. 28°F at 7am in town. Chris saw the snowmaking crews testing on Aspen Highlands.

Hannah"""),

    dict(key="1015", sent="2026-10-15 18:48", frm="hn", covers=["2026-10-15"],
         subject="Aspen closing 10/15",
         body=f"""$3.6K, 4 transactions. Beanie, Vtrack, padded cardigan navy, Vel black.

Sending merch a separate note about the ski allocation.

Hannah"""),

    dict(key="1015merch", sent="2026-10-15 19:05", frm="hn", covers=[],
         to=[MERCH], cc=[LM],
         attach=[{"name": "ASP01_ski_wishlist_Oct26.xlsx", "rows": [
             ["Style", "Colour", "Sizes", "Qty wanted", "On hand", "Why"],
             ["PIERO", "black", "2,3,4,5", 8, 1, "asked 9/29, 10/9; sold out 9/25"],
             ["VALDORA", "black", "1,2,3", 6, 0, "asked 10/10"],
             ["VALDORA", "off-white", "1,2,3", 4, 0, "sold 9/27, 10/13"],
             ["CORTINA", "black", "S,M,L", 6, 1, "L out since 10/11"],
             ["ALPINA", "off-white", "37,38,39", 4, 1, ""],
             ["AUREA", "black", "0,1,2", 6, 1, "asked 10/9, 10/11"],
             ["WINTER GLOVES", "black", "TU", 12, 3, ""],
         ]}],
         subject="Aspen - ski season allocation request",
         body=f"""Hi merch team,

First snow on Ajax this week and clients are already asking for ski pieces. Right now we have on hand: 1 Piero, 0 Valdora, 1 Cortina (no L), 1 Alpina. Last year the ski allocation arrived Oct 28. Can we get at least part of it earlier?

Attached is my wish list with what we've been asked for. Black Aurea 0-2 also on there, we had a few asks.

Opening day is Thanksgiving (Nov 26) and the second-home owners start arriving the week before.

Thank you,
{SIG_HN}"""),

    dict(key="1015ooo", sent="2026-10-15 19:05", frm="lm", reply_to="1015merch", covers=[],
         to=[HN], cc=[],
         extra_headers={"Auto-Submitted": "auto-replied", "X-Auto-Response-Suppress": "All"},
         subject="Automatic reply: Aspen - ski season allocation request",
         body="""I am traveling Oct 14-16 (Toronto) with limited access to email. For urgent matters please contact retail-ops-usa@valentino-retail.example.

Lauren Mitchell"""),

    dict(key="1016", sent="2026-10-16 18:51", frm="ml", covers=["2026-10-16"],
         subject="Aspen store - closing report Friday 10/16",
         body="""Hi everyone,

Sales: $8.5K
Transactions: 3
Artem black x2!! (2 brothers from Chicago, I told them to size down because it runs big, they took a 4 and a 5 instead of 5 and 6 and the fit was perfect), Cortina black, sweatshirt, Aurea navy
Traffic: 26 (a Korean couple too)
Asks: none

Megan"""),

    dict(key="1017", sent="2026-10-17 18:54", frm="hn", covers=["2026-10-17"],
         subject="Aspen closing Sat 10/17",
         body=f"""$9.3K vs $9.9K plan, 4 transactions. Busiest Saturday since Labor Day (44 people). Piero black, Alpina off-white, gloves, beanie. Camilla black 2 asked.

Hannah"""),

    dict(key="1018", sent="2026-10-18 18:38", frm="cd", mailer="iphone", covers=["2026-10-18"],
         subject="asp eod sun",
         body="""9.8k on 7.9 🎿 aurea black x2, valdora cream, beanie, vtrack

missed camilla black 2 (same lady from yesterday came back w her sister), vel black 4, navy backpack

aurea black now 0 in everything 0-3. 58 units in today, still no ski stuff

Sent from my iPhone"""),

    dict(key="1018dup", sent="2026-10-18 18:40", frm="cd", mailer="iphone", suffix="_dup", covers=[],
         subject="asp eod sun",
         body="""9.8k on 7.9 🎿 aurea black x2, valdora cream, beanie, vtrack

missed camilla black 2 (same lady from yesterday came back w her sister), vel black 4, navy backpack

aurea black now 0 in everything 0-3. 58 units in today, still no ski stuff

Sent from my iPhone"""),

    dict(key="1019", sent="2026-10-19 17:26", frm="cd", mailer="iphone", covers=["2026-10-19"],
         subject="asp eod",
         body="""9.4k, 5 trx. piero black, nova olive + nova black, women's vtrack. cosimo navy 2 asked

Sent from my iPhone"""),

    dict(key="1020", sent="2026-10-20 17:39", frm="hn", covers=["2026-10-20"],
         subject="Aspen closing 10/20",
         body=f"""$6.7K, 3 transactions. Aria black x2 (British sisters), Piero black, beanie.

Aurea navy 4 asked. Aria black 0 now out too.

Interviews for seasonal staff done, 2 offers going out tomorrow if Lauren approves.

Hannah"""),

    dict(key="1021", sent="2026-10-21 17:44", frm="hn", covers=["2026-10-21"],
         subject="Aspen closing 10/21",
         body=f"""Hi all,

$3.0K, 2 transactions (women's Vtrack, Artem black). A cap came back (gift).

Asks: vlogo cardigan navy M, Vtrack black 44.

Quiet, 26 people, half of them asking when the Gondola opens. 5 weeks to opening day.

{SIG_HN}"""),
]
