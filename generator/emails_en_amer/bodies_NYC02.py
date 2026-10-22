STORE = "NYC02"

WRITERS = {
    "tb": "Tyler Brooks <tyler.brooks@moncler-retail.example>",
    "ag": "Ana Gutierrez <ana.gutierrez@moncler-retail.example>",
    "jl": "Jordan Lee <jordan.lee@moncler-retail.example>",
    "box": "NYC02 SoHo <nyc02.store@moncler-retail.example>",
    "lm": "Lauren Mitchell <lauren.mitchell@moncler-retail.example>",
}

LM = "Lauren Mitchell <lauren.mitchell@moncler-retail.example>"
OPS = "retail-ops-usa@moncler-retail.example"
MERCH = "merch-planning-americas@moncler-retail.example"
BOX = "nyc02.store@moncler-retail.example"

DEFAULT_TO = [OPS]
DEFAULT_CC = [LM]

SIG_AG = """Ana Gutierrez
Assistant Store Manager | Moncler SoHo
101 Greene St, New York, NY 10012
T (212) 555-0148"""

HABIT_LINES = [SIG_AG, "Sent from my iPhone"]

EMAILS = [
    # ---------------------------------------------------------------- late Aug / early Sep
    dict(key="0831", sent="2026-08-31 19:52", frm="ag", covers=["2026-08-31"],
         subject="SoHo closing Mon 8/31",
         body=f"""Hi all,

SALES: $32.3K vs $17.2K plan. Great way to close August, mostly 2 big tickets in the afternoon (Maya black + Montgenevre, same client).
TRAFFIC: ~110
MISSED:
- Montgenevre navy 4, 2 different guys asked. We have 3 and 5 only
- Albenga black 4
NOTES: Bady black 1 and 2 are both gone, Flammette black 2 too. Can we get a look at the replen for this week?

Thanks,
{SIG_AG}"""),

    dict(key="0901", sent="2026-09-01 19:41", frm="tb", mailer="iphone", covers=["2026-09-01"],
         subject="soho eod",
         body="""slow tuesday 😮‍💨 15.2k, 11 trx

delivery came in (165 pcs) but UPS showed up at 4:30 so we were processing on the floor till close. it was supposed to be here sunday

everyone is already in the hamptons mentally lol

Sent from my iPhone"""),

    dict(key="0902", sent="2026-09-02 19:38", frm="tb", mailer="iphone", covers=["2026-09-02"],
         subject="soho 9/2",
         body="""way better today 🙌 29.4k on 18.6 plan

logo cardis moving (3 black), hoodies too. couple korean girls in the afternoon bought the grey hoodie

still no bady black 2, ecrins black 5 also out now

Sent from my iPhone"""),

    dict(key="0903", sent="2026-09-03 20:06", frm="tb", mailer="iphone", covers=["2026-09-03"],
         subject="soho eod thurs",
         body="""27k vs 24 plan, decent

cable knit sweater black did 4 which is random but ok. chinese tour group-ish thing around 2, mostly looking

missed a trailgrip grey 39 and the womens trailgrip black 35, we never get 35s

some returns, small stuff (hoodie, tee, a sneaker size). beanie came back with a pulled thread

Sent from my iPhone"""),

    dict(key="0904", sent="2026-09-04 19:47", frm="ag", covers=["2026-09-04"],
         subject="SoHo closing Fri 9/4",
         body=f"""Hi all,

SALES: $21.7K vs $27.5K plan
TRAFFIC: ~150, lots of browsing, start of the long weekend
MISSED:
- Bady black 2 (again)
- Flammette navy 0
- Tib off-white 6
- Logo cardigan black S, we are out since Wednesday
- also hoodie navy M is at zero
NOTES: Tyler off through Monday, I'm closing the weekend with Jordan.

Thanks,
{SIG_AG}"""),

    dict(key="0905", sent="2026-09-05 19:33", frm="ag", covers=["2026-09-05"],
         subject="SoHo closing Sat 9/5",
         body=f"""Hi all,

SALES: $18.8K vs $39.2K plan. Not good.
TRAFFIC: ~170 but nobody buying, Labor Day weekend, city is empty except tourists
MISSED:
- Logo hoodie navy M x2
- Bady black 2
- Ambrine black 4
- Chamonix black M (ski pants, guy going to Chile)
- Logo cardigan black S
NOTES: Flammette black 0 and hoodie black XL also at zero now. Ojo, the Bady black 2 is the 3rd or 4th ask this week.

{SIG_AG}"""),

    dict(key="0906", sent="2026-09-06 18:41", frm="jl", covers=["2026-09-06"],
         subject="SoHo Sunday",
         body="""Hi everyone,

Not sure if I'm supposed to send this, Ana said to send the closing on Sundays when I close so here it is.

Sales were $22,900 (plan was 27,200). 14 transactions. A lot of Korean customers today, maybe 4 or 5 groups. One lady wanted a Bady in off white size 2 and we only had 0 and 3.

Delivery arrived this morning, 187 pieces, we put most of it away.

Thank you,
Jordan"""),

    dict(key="0907", sent="2026-09-07 19:20", frm="ag", covers=["2026-09-07"],
         subject="SoHo closing Mon 9/7 (Labor Day)",
         body=f"""Hi,

SALES: $9.4K vs $21.4K plan
TRAFFIC: ~70. Labor Day, dead
NOTES: Tib black x2 was most of the day. 3 returns (Marin 3 too small, cable knit M, beanie). Nothing else to flag.

{SIG_AG}"""),

    # 9/8 intentionally missing (no email sent)

    dict(key="0909", sent="2026-09-09 20:12", frm="tb", mailer="iphone", covers=["2026-09-09"],
         subject="soho eod",
         body="""17k (plan 23.8). meh

no email last night sorry, was me and Jordan and I just forgot. tuesday was like 17-18k, nothing crazy, logo cardi XL black is gone

today: chamonix pants x2, gloves x2, maire beige x2. one ask for bady off white 3

Sent from my iPhone"""),

    dict(key="0910", sent="2026-09-10 19:44", frm="tb", mailer="iphone", covers=["2026-09-10"],
         subject="soho 9/10 🔥",
         body="""32.6k on 26 plan 🔥 only 10 trx tho so big tickets, maya black x2 and maire black x2 to basically 2 people

flammette black 0 still out, logo cardi black XL out

Sent from my iPhone"""),

    dict(key="0911", sent="2026-09-11 20:21", frm="tb", mailer="iphone", covers=["2026-09-11"],
         subject="soho eod fri",
         body="""30.8k vs 29.6, small W

hoodies + tees as always. hermine black x2

maire cream 00 asked, trailgrip grey 45 asked. maire 2 came back (size)

hoodie black XL out

Sent from my iPhone"""),

    dict(key="0912", sent="2026-09-12 19:36", frm="ag", covers=["2026-09-12"],
         subject="SoHo closing Sat 9/12",
         body=f"""Hi all,

SALES: $41.2K vs $43.4K plan (just short)
TRAFFIC: ~195
MISSED:
- Trailgrip GTX black 41 and 45
NOTES: Montgenevre navy now out in 3 as well as 4. Hoodies and tees did the volume. Quieter in the evening, Rosh Hashanah.

{SIG_AG}"""),

    dict(key="0913", sent="2026-09-13 18:52", frm="jl", covers=["2026-09-13"],
         subject="SoHo Sunday 9/13",
         body="""Hi,

Sales today $24.1K, plan $31.1K. 14 transactions.

Two Bady in powder pink sold, both to the same girl (one for her sister). Someone asked for the Maire in beige size 00, we don't have it.

Delivery came, 209 units. A Tib came back size 4 too big.

Thanks!
Jordan"""),

    dict(key="0914", sent="2026-09-14 19:28", frm="ag", covers=["2026-09-14"],
         subject="SoHo closing Mon 9/14",
         body=f"""SALES: $21.1K vs $21.8K
TRAFFIC: ~105
MISSED: Chambre off-white 00
NOTES: Peyre black sold (first ski jacket of the season for us). Bady pink again x2. VM team came by at 9am for the campaign window, looks great.

{SIG_AG}"""),

    dict(key="0915", sent="2026-09-15 19:58", frm="tb", mailer="iphone", covers=["2026-09-15"],
         subject="soho eod - campaign day 1",
         body="""23.3k vs 22.6 ✅

new windows are 🔥🔥 people taking pics outside all day. not sure it turned into $ yet but vibes good

logo cardi black x3, tee black x3

montgenevre navy 4 and 5 both out now

Sent from my iPhone"""),

    dict(key="0916", sent="2026-09-16 20:03", frm="tb", mailer="iphone", covers=["2026-09-16"],
         subject="soho 9/16",
         body="""25.9k on 24.6 plan 👍

logo cardi black another 3. we need more of those, navy S also out now

one guy asked for chamonix S

Sent from my iPhone"""),

    dict(key="0917", sent="2026-09-17 19:45", frm="ag", covers=["2026-09-17"],
         subject="SoHo closing Thu 9/17",
         body=f"""Hi all,

SALES: $22.2K vs $29.1K plan
TRAFFIC: ~130, good mix of Brazilians and Mexicans this afternoon
MISSED:
- Karakorum grey 6
- Ecrins black 7
NOTES: Maire black x3 today. Maire navy 3 is out. 4 returns (Montcla 5, padded cardigan L, hoodie, polo) all size or change of mind.

{SIG_AG}"""),

    dict(key="0918", sent="2026-09-18 20:17", frm="tb", mailer="iphone", covers=["2026-09-18"],
         subject="soho fri 🙌",
         body="""40.8k vs 31.9 plan!! 🙌🙌 26 trx

flammette black x3, logo tees, hoodies. good energy all day

missed maya navy 6, karakorum grey 1 (?? who's a 1 lol), peyre black 3. rosiere black 3 out and ecrins black 5 out again

campaign maybe kicking in? few people mentioned the ads on ig

Sent from my iPhone"""),

    dict(key="0920", sent="2026-09-20 19:06", frm="ag", covers=["2026-09-19", "2026-09-20"],
         subject="SoHo closing Sat + Sun (9/19-9/20)",
         body=f"""Hi all, sending both days together, yesterday was a long one and I forgot to send before leaving. Sorry.

SAT 9/19
SALES: $32.8K vs $49.2K plan
TRAFFIC: ~185
MISSED: Flammette black 3 (out), Maya navy 6 (2nd ask this week)
NOTES: Polo black x3, Maire beige x3. A Bady 2 came back yesterday? no, that was Friday. Ecrins 5 gift return Saturday.

SUN 9/20
SALES: $21.4K vs $35.6K plan
TRAFFIC: ~130
NOTES: Maire navy x3. Delivery 189 pcs received. Quiet, Yom Kippur tonight so I expect tomorrow to be slow too.

Weekend short about $30K vs plan.

{SIG_AG}"""),

    dict(key="0921", sent="2026-09-21 19:24", frm="ag", covers=["2026-09-21"],
         subject="SoHo closing Mon 9/21",
         body=f"""SALES: $14.2K vs $25.1K
TRAFFIC: ~105
NOTES: 6 transactions. Ilvaro black x3 to a Brazilian family, the only real sale of the day. Flammette black 3 and Rosiere black 4 still out.

{SIG_AG}"""),

    dict(key="0922", sent="2026-09-22 19:49", frm="tb", mailer="iphone", covers=["2026-09-22"],
         subject="eod",
         body="""15.7k, plan 26. 7 trx 💀

uptown has the UN mess so everyone is staying home i think. honestly no reason, just dead

Sent from my iPhone"""),

    dict(key="0923", sent="2026-09-23 19:55", frm="tb", mailer="iphone", covers=["2026-09-23"],
         subject="soho 9/23",
         body="""28.7k vs 28.3, back to plan

hermine black x3. someone asked for flammette black 3 AGAIN, we've been out since like the 18th

maire black 2 now at zero 👀 that's our best size

Sent from my iPhone"""),

    dict(key="0924", sent="2026-09-24 20:09", frm="tb", mailer="iphone", covers=["2026-09-24"],
         subject="soho eod - polaris launch",
         body="""25.6k vs 32.8

tib black went crazy, 8 of them?? one guy bought 3 for his brothers

polaris drop today. honestly nobody bit. 5-6 people tried the cape and the oversized, all said it runs small in the shoulders and $$$ for what it is. 0 sold i think

missed: padded cardigan navy M, sweatshirt grey XL

Sent from my iPhone"""),

    dict(key="0925", sent="2026-09-25 20:31", frm="tb", mailer="iphone", covers=["2026-09-25"],
         subject="soho fri 🔥",
         body="""45.7k vs 38.1!! 🔥🔥

logo cardi black x5, bady black x5 (!!), tib black x4. friday crowd was spending

missed rosiere black 4, still out. maire black 2 still out

can we get more bady black? down to 1 in a 0 and a 3 i think

Sent from my iPhone"""),

    dict(key="0925dup", sent="2026-09-25 20:33", frm="tb", mailer="iphone", suffix="_dup", covers=[],
         subject="soho fri 🔥",
         body="""45.7k vs 38.1!! 🔥🔥

logo cardi black x5, bady black x5 (!!), tib black x4. friday crowd was spending

missed rosiere black 4, still out. maire black 2 still out

can we get more bady black? down to 1 in a 0 and a 3 i think

Sent from my iPhone"""),

    dict(key="0926", sent="2026-09-26 19:40", frm="tb", mailer="iphone", covers=["2026-09-26"],
         subject="SAT",
         body="""54.5k on 53.8 ✅ 23 trx

hermine black x7 lol where did that come from. tib navy x4

missed a ton:
maire black 2 x2
tib black 5 x2 (now 0 in 5)
bady cream 2
karakorum grey 6
rosiere black 4
polo black XS

lots of korean shoppers today, they all want black

Sent from my iPhone"""),

    dict(key="0927", sent="2026-09-27 18:37", frm="jl", covers=["2026-09-27"],
         subject="Sunday closing SoHo",
         body="""Hi,

$41.5K today, plan was $38K. 21 transactions.

The padded cardigan in navy sold 3. People asked for: Maire black size 2, Ambrine black 4, Tib black 5. I put the Maire lady on the waitlist (Ana showed me how).

Delivery 203 units received.

Have a good night,
Jordan"""),

    dict(key="0928", sent="2026-09-28 19:31", frm="ag", covers=["2026-09-28"],
         subject="SoHo closing Mon 9/28",
         body=f"""Hi all,

SALES: $42.6K vs $28.0K plan (+52%)
TRAFFIC: ~135, many Korean clients again (I'd say 1 in 10)
MISSED: Tib black 5
NOTES:
- Maire black x4 sold in sizes 0/1/3 but still no 2. Maire beige x3 also.
- Rosiere black x3
- Waitlist for Maire black 2 is at 5 names. Is there any coming? Madison says they are low too.

{SIG_AG}"""),

    dict(key="0929", sent="2026-09-29 19:46", frm="ag", covers=["2026-09-29"],
         subject="SoHo closing Tue 9/29",
         body=f"""SALES: $21.2K vs $30.3K
TRAFFIC: ~130
MISSED: Rosiere black 7
NOTES: 2 Tib returns. One was change of mind, the other one the client said the zipper pull came off in his hand, put it as quality. Logo tee black M now at zero.

{SIG_AG}"""),

    dict(key="0930", sent="2026-09-30 20:02", frm="tb", mailer="iphone", covers=["2026-09-30"],
         subject="soho eod 9/30",
         body="""38.3k vs 30.8 plan, end of month W 🙌

trailgrips, maire navy x2, bady pink x2, padded cardi navy (asked M which we don't have)

another tib back with a broken zipper. that's 2 in 2 days

Sept closes around 815k MTD i think, under plan but ok

Sent from my iPhone"""),

    dict(key="0930corr", sent="2026-10-01 10:12", frm="ag", suffix="_corr", reply_to="0930", covers=[],
         subject="RE: soho eod 9/30",
         body=f"""Small correction to Tyler's email from last night, sales yesterday were $33.8K not 38.3 (typo). Still above plan.
September total is ~$784K vs ~$880K plan for the month (his MTD included Aug 31).

{SIG_AG}

-----Original Message-----
From: Tyler Brooks <tyler.brooks@moncler-retail.example>
Sent: Wednesday, September 30, 2026 8:02 PM
To: retail-ops-usa@moncler-retail.example
Cc: Lauren Mitchell <lauren.mitchell@moncler-retail.example>
Subject: soho eod 9/30

38.3k vs 30.8 plan, end of month W 🙌
[...]"""),

    # ---------------------------------------------------------------- October
    dict(key="1001", sent="2026-10-01 20:14", frm="tb", mailer="iphone", covers=["2026-10-01"],
         subject="soho 10/1",
         body="""36.7k vs 35.2 👍

3 tib returns today ALL zipper. slider splits or the teeth dont catch. is there something going on with this batch?? we have like 20 in stock and im scared to sell them

scarves x4, montcla navy x3

missed logo tee black M x2, bady cream 1

Sent from my iPhone"""),

    dict(key="1002", sent="2026-10-02 19:39", frm="ag", covers=["2026-10-02"],
         subject="SoHo closing Fri 10/2",
         body=f"""Hi all,

SALES: $27.1K vs $41.6K plan
TRAFFIC: ~155
NOTES:
- Hermine black x3, logo cardigan black x2
- Hermine 0 return (size)
- Tib: I pulled the remaining stock to check zippers, 4 out of the 18 have a slider that feels loose. Kept them in the back for now. Please advise if there's an RTV.
- A few girls asked if we have "the pink Moncler from the K-pop show". I think it's the Ilvaro? We never received the pink.

{SIG_AG}"""),

    dict(key="1003", sent="2026-10-03 19:58", frm="tb", mailer="iphone", covers=["2026-10-03"],
         subject="SATURDAY 🔥🔥",
         body="""60.5k vs 55.9 plan 🔥 32 trx

ok so the ilvaro thing is real. yoon ha-eun from LUMIERE wore the pink one in paris and it's all over tiktok. we had girls coming in all afternoon with screenshots. we don't have pink at all so they bought the cream and black ilvaro, sold 3 cream

missed list is long:
hermine navy 3
bady cream 1
montgenevre grey 5
tib black 5
tib cream 2
rosiere black 2
trailgrip black 46

4 more tib zipper returns 😩 thats 9 this week

logo tee black XL out too now

Sent from my iPhone"""),

    dict(key="1003fwd", sent="2026-10-03 21:40", frm="ag", suffix="_fwd", covers=[],
         to=["clienteling-na@moncler-retail.example"], cc=[LM, MERCH],
         subject="Fwd: pink ilvaro?? 🎀",
         body=f"""Forwarding one of the DMs we got on the store IG today, we got maybe 15 like this. Is there any pink Ilvaro coming to the US at all? Even 5 pieces would help. Black and off-white Ilvaro are selling as a substitute but most of these girls want the pink only.

Ana

---------- Forwarded message ---------
From: Instagram Direct (via Sprinklr) <noreply-social@moncler-retail.example>
Date: Sat, Oct 3, 2026 at 3:12 PM
Subject: New message from @mina.k.nyc

hiii do u guys have the ilvaro in the pink that haeun wore?? size 1 or 2 🥺🥺 i can come today
i called madison and they said no. pls let me know!!

--
{SIG_AG}"""),

    dict(key="1004", sent="2026-10-04 19:12", frm="ag", covers=["2026-10-04"],
         subject="SoHo closing Sun 10/4",
         body=f"""Hi all,

SALES: $63.7K vs $41.0K plan (+55%)
TRAFFIC: ~205, Korean and Chinese students, lots of Ilvaro questions again
MISSED:
- Maire black 2
- Ilvaro off-white 3 (sold the last 3 yesterday)
NOTES: Montgenevre navy x4, Ambrine black x3, women's Trailgrip black x3. Delivery 222 pcs. No pink Ilvaro in it.

{SIG_AG}"""),

    dict(key="1005", sent="2026-10-05 19:26", frm="ag", covers=["2026-10-05"],
         subject="SoHo closing Mon 10/5",
         body=f"""SALES: $23.4K vs $31.3K
TRAFFIC: ~150
MISSED: Maire black 2 x3 (3 different clients, one Korean, two American)
NOTES: Maire beige x3 sold, 2 of them to people who wanted black and settled. Ilvaro size 3 returned, client said the snap was loose.

{SIG_AG}"""),

    dict(key="1006", sent="2026-10-06 20:48", frm="ag", covers=["2026-10-06"],
         subject="SoHo closing Tue 10/6 - POS DOWN this afternoon",
         body=f"""Hi all,

Heads up, our POS went down today from 2:10pm to about 5:40pm. Both registers and the handhelds froze, card terminals were offline too. IT ticket INC0048213, they said it was a store network issue (switch in the back room). Tyler was on the phone with the helpdesk for 2 hours.

During the outage we wrote manual sales slips and took card details on the backup imprinter per the procedure. Some clients didn't want to wait and left, I think we lost at least 3-4 sales.

SALES IN SYSTEM: $12.6K (8 transactions), this is only the morning and the last hour
MANUAL SLIPS: 12 slips, ~$18.9K. Tyler and I will key them in tomorrow morning when we open, so they will show with tomorrow's date.
REAL DAY: ~$31.5K vs $32.3K plan, so basically on plan

MISSED: Maire beige 0, Bady pink 4 (she thought it was the Ilvaro from TikTok, it isn't)
Maire black 2 and logo tee black L at zero.

Please don't panic about today's number in the dashboard 🙏

{SIG_AG}"""),

    dict(key="1007", sent="2026-10-07 20:05", frm="tb", mailer="iphone", covers=["2026-10-07"],
         subject="soho eod 10/7 (numbers look off)",
         body="""ok so the system says 50.1k today vs 31.2 plan, +60%. that's NOT real lol

it includes the 12 manual slips from yesterday's outage (~19k) that we keyed in this morning. so today on its own is more like 31k, right on plan. and yesterday is understated by the same amount. traffic counter says 125 which feels right

anyway today: hoodies, tees, montcla navy x2, hermine cream x2

missed hermine cream 1, ilvaro cream 0, logo cardi navy XS

POS working fine today, IT replaced the switch at 10am

Sent from my iPhone"""),

    dict(key="1007re1", sent="2026-10-08 08:37", frm="lm", reply_to="1007", suffix="_re1", covers=[],
         to=[BOX, "Tyler Brooks <tyler.brooks@moncler-retail.example>"], cc=["Ana Gutierrez <ana.gutierrez@moncler-retail.example>", OPS],
         subject="RE: soho eod 10/7 (numbers look off)",
         body="""Tyler, Ana - thanks for flagging. Two questions:
1) Can you send me the exact total of the manual slips so finance can reallocate it to 10/6 for the comp report? Ballpark isn't enough for them.
2) Were any of the manual sales tax-free/returns? Finance wants to know if anything needs to be adjusted.

Also, how many clients do you think walked during the outage?

Lauren

Lauren Mitchell
Area Manager USA & Canada
Moncler Retail

-----Original Message-----
From: Tyler Brooks <tyler.brooks@moncler-retail.example>
Sent: Wednesday, October 7, 2026 8:05 PM
Subject: soho eod 10/7 (numbers look off)

ok so the system says 50.1k today vs 31.2 plan, +60%. that's NOT real lol
[...]"""),

    dict(key="1007re2", sent="2026-10-08 10:21", frm="ag", reply_to="1007re1", suffix="_re2", covers=[],
         to=[LM], cc=["Tyler Brooks <tyler.brooks@moncler-retail.example>", OPS],
         subject="RE: soho eod 10/7 (numbers look off)",
         body=f"""Hi Lauren,

1) 12 slips, total $18,930 net (I'm attaching the photos of the slips to the finance ticket, not here). All 12 receipts are posted with business date 10/7 in the POS.
2) No returns, no exchanges during the outage. No tax-free (we don't do that here anyway).

Walkouts: we counted 4 for sure (one wanted a Montgenevre, one a Maire beige, 2 accessories) plus people who just left when they saw the sign. I'd say $5-6K lost.

So corrected: 10/6 ≈ $31.5K / 20 trx, 10/7 ≈ $31.2K / 12 trx.

Thanks,
Ana

{SIG_AG}

> On Thu, Oct 8, 2026 at 8:37 AM Lauren Mitchell <lauren.mitchell@moncler-retail.example> wrote:
> Tyler, Ana - thanks for flagging. Two questions:
> 1) Can you send me the exact total of the manual slips so finance can reallocate it to 10/6 for the comp report?
> 2) Were any of the manual sales tax-free/returns?"""),

    dict(key="1008", sent="2026-10-08 19:51", frm="tb", mailer="iphone", covers=["2026-10-08"],
         subject="soho thurs",
         body="""37.5k vs 36.4 ✅

ilvaro black x4 today, all to girls who wanted pink. now black is gone in 0 too

missed: bady pink 3, ilvaro cream 3, ambrine black 2, padded cardi navy S

bady black 0 out, montgenevre navy 3 out, rosiere black 3 out

Sent from my iPhone"""),

    dict(key="1009", sent="2026-10-09 20:26", frm="tb", mailer="iphone", covers=["2026-10-09"],
         subject="eod fri",
         body="""rough one, 25.1k vs 44.5 😬 210 people in, 16 trx

lots of lookers. ilvaro questions all day and we have nothing in pink, nothing in black 0 now. one girl took a maya navy for her bf instead lol

missed ilvaro black 0, maire navy 00, tib black 2, rosiere olive 5

Sent from my iPhone"""),

    dict(key="1010", sent="2026-10-10 19:44", frm="tb", mailer="iphone", covers=["2026-10-10"],
         subject="sat eod",
         body="""44.8k vs 57.9 plan. traffic good (300) conversion bad

scarves black x5, montcla black x5. people getting into fall mode finally

missed maire black 2 (yes again), ilvaro black 0, logo cardi black XXL
maire black 0 now also out

1 more tib zipper. bady 2 back for size

Sent from my iPhone"""),

    dict(key="1011", sent="2026-10-11 18:33", frm="jl", covers=["2026-10-11"],
         subject="Sunday 10/11 SoHo",
         body="""Hello,

Sales $52.8K vs plan $45.7K. Good day!

Bady black sold 4 and Maire navy 3, Montcla navy 3. Clients asked for Maire black 2 (waitlisted) and Ambrine in chocolate brown size 2, we never had brown here I think?

Ilvaro returned, size 2, she changed her mind (she wanted pink).

Delivery 270 pcs came in, no pink Ilvaro and no Maire black in it, I checked the packing list.

Jordan"""),

    dict(key="1012", sent="2026-10-12 19:17", frm="ag", covers=["2026-10-12"],
         subject="SoHo closing Mon 10/12",
         body=f"""SALES: $33.5K vs $31.5K
TRAFFIC: ~135 (Columbus Day, more tourists than locals)
MISSED: Maire black 0
NOTES: Trailgrips good (men's + women's, 6 pairs). Maire black is now at zero in 0, 1 and 2. Waitlist is at 9 names for black, sizes 0-2. Any news from the DC?

{SIG_AG}"""),

    dict(key="1013", sent="2026-10-13 19:34", frm="ag", covers=["2026-10-13"],
         subject="SoHo closing Mon 10/12",
         body=f"""SALES: $38.6K vs $33.0K
TRAFFIC: ~140
MISSED: Arneb navy 6 (I told him the 5 fits like a 6, he still wanted to wait)
NOTES:
- 2 more Tib zipper returns (5 and 3). We still have the 4 suspicious ones in the back.
- Hermine black x3
- Montcla black 5 is out

{SIG_AG}"""),

    dict(key="1014", sent="2026-10-14 20:07", frm="tb", mailer="iphone", covers=["2026-10-14"],
         subject="soho 10/14",
         body="""33.1k vs 36.3

3 people asked maire black in 0, 1, 2. one of each 😭 korean girl group came in literally just for that. this is the #1 thing we're missing rn

ambrine black x3 though

5 returns, mostly size stuff

Sent from my iPhone"""),

    dict(key="1015", sent="2026-10-16 09:14", frm="tb", mailer="iphone", covers=["2026-10-15"],
         subject="soho thurs (sorry late)",
         body="""forgot to send last night my bad 🙏

thurs 30.6k vs 40.8. gloves x4, beanies, polo black x3, tib navy x3. first cold morning so accessories started

nothing big missed. maire black still 0/1/2

Sent from my iPhone"""),

    dict(key="1016", sent="2026-10-16 20:11", frm="tb", mailer="iphone", covers=["2026-10-16"],
         subject="fri eod",
         body="""16k vs 46 plan 💀💀 9 trx

i have no explanation honestly. 170 in the door, nobody bought. bady pink x2 to one tourist

missed maire black 2, hermine cream 1, hoodie grey XL

another tib zipper

Sent from my iPhone"""),

    dict(key="1017", sent="2026-10-17 19:52", frm="tb", mailer="iphone", covers=["2026-10-17"],
         subject="SAT 10/17 🔥",
         body="""65.8k vs 64.6 🔥 bounced back

sneakers did great (trailgrip gtx + women's black 3 each), polos, hoodies. chinese and korean shoppers again

missed a bunch:
logo tee white M x2
maire black 2
flammette navy 3
montcla black 5
padded cardi grey M
cable knit black XS
polo black L

montcla navy 5 out too now. tib zipper #?? i lost count

Sent from my iPhone"""),

    dict(key="1018", sent="2026-10-18 18:45", frm="ag", covers=["2026-10-18"],
         subject="SoHo closing Sun 10/18",
         body=f"""Hi all,

SALES: $17.2K vs $46.4K plan
TRAFFIC: ~185
MISSED: Maire black 2, Maire navy 00
NOTES: Delivery 242 pcs. Still no Maire black. I heard the DC got the re-order on Friday? If so can we get sizes 0-2 for SoHo first, the waitlist is 11 names now.
Hermine 0 return (size), Maya 3 gift return, scarf with a pulled thread.

{SIG_AG}"""),

    dict(key="1019", sent="2026-10-19 19:31", frm="ag", covers=["2026-10-19"],
         subject="SoHo closing Mon 10/19",
         body=f"""SALES: $32.8K vs $34.8K
TRAFFIC: ~180
NOTES: Flammette black x3, scarves x3, cable knit black x2. 4 returns (Ambrine 4 size, Maya change of mind, polo, women's Trailgrip). Polo black L out.

{SIG_AG}"""),

    dict(key="1020", sent="2026-10-20 20:03", frm="tb", mailer="iphone", covers=["2026-10-20"],
         subject="soho eod tues",
         body="""33.9k vs 36.5. ok day

bady black x3 trailgrips x3 montcla navy x3

flammette black 4 asked

ANOTHER tib zipper. we've had like 15 back since end of sept. can someone please tell us what to do with the ones still on the floor

Sent from my iPhone"""),

    dict(key="1021", sent="2026-10-21 19:57", frm="tb", mailer="iphone", covers=["2026-10-21"],
         subject="soho 10/21",
         body="""44.9k vs 38.8 🙌

belt bags, logo cardi navy, montgenevre navy. good wednesday

missed ilvaro cream 3 (still asking for that one), trailgrip black 46

no maire black still. ana's waitlist has 11-12 people

Sent from my iPhone"""),
]
