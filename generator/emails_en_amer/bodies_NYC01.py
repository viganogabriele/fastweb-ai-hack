# Hand-authored closing emails for NYC01 (New York Madison Avenue flagship).
# Bodies are written one by one; the only shared pieces are the fixed signature /
# disclaimer blocks below (listed in HABIT_LINES).

STORE = "NYC01"

WRITERS = {
    "rs": "Rebecca Stein <rebecca.stein@valentino-retail.example>",
    "mb": "Marcus Bell <marcus.bell@valentino-retail.example>",
    "pr": "Priya Raman <priya.raman@valentino-retail.example>",
    "store": "Valentino Madison Avenue <nyc01.store@valentino-retail.example>",
    "lm": "Lauren Mitchell <lauren.mitchell@valentino-retail.example>",
}

LAUREN = "Lauren Mitchell <lauren.mitchell@valentino-retail.example>"
REBECCA = "Rebecca Stein <rebecca.stein@valentino-retail.example>"
MARCUS = "Marcus Bell <marcus.bell@valentino-retail.example>"
PRIYA = "Priya Raman <priya.raman@valentino-retail.example>"
OPS = "retail-ops-usa@valentino-retail.example"
MERCH = "merch-planning-americas@valentino-retail.example"
VM = "vm-team@valentino-retail.example"
CLT = "clienteling-na@valentino-retail.example"
STOREBOX = "nyc01.store@valentino-retail.example"

DEFAULT_TO = [OPS]
DEFAULT_CC = [LAUREN]

SIG_RS = """
--
Rebecca Stein
Store Manager | Valentino Madison Avenue
849 Madison Avenue, New York, NY 10065
T +1 212 555 0148 | rebecca.stein@valentino-retail.example

CONFIDENTIALITY NOTICE: This e-mail and any attachments are intended only for the named addressee(s) and may contain confidential, proprietary or privileged information. If you are not the intended recipient, please notify the sender immediately and delete this message. Any review, use, disclosure or distribution by others is strictly prohibited.
"""

SIG_PR = """
Priya Raman
Senior Client Advisor
Valentino Madison Avenue
+1 212 555 0163
"""

SIG_LM = """
Lauren Mitchell
Area Manager, USA & Canada
Valentino USA Inc. | New York
"""

HABIT_LINES = [SIG_RS.strip(), SIG_PR.strip(), SIG_LM.strip(),
               "Lauren Mitchell <lauren.mitchell@valentino-retail.example> wrote:"]

EMAILS = [

# ---------------------------------------------------------------- week of Aug 31
dict(key="0831", sent="2026-08-31 19:24", frm="mb", mailer="iphone",
     subject="eod mon 8/31", covers=["2026-08-31"],
     body="""end of summer monday, not bad actually
- 35.1k vs 28 plan
- 18 trans / 32 units
- beanies of all things. 4 black 3 pink, people shopping for fall already
- 2 valdora in the cream, 2 vel navy
- 1 return, adela sz 4, seam on the pocket opening up. tagged quality, its in the back for RTV
mostly locals, couple of brits. rebecca back thurs

Sent from my iPhone"""),

dict(key="0902", sent="2026-09-02 19:31", frm="mb", mailer="iphone",
     subject="Madison closing 9/2", covers=["2026-09-02"],
     body="""wed
- 30k even, plan 30.8 so basically flat
- delivery in this am, 90 units, mostly knit + jersey. all processed by 2pm
- logo hoodies moving, 3 navy 3 black
- returns: aria 1 (changed her mind), mistral 2 too small, 1 beanie for colour
couple of korean girls in the afternoon trying on aurea, only browsed
AC on the 2nd floor making the noise again, facilities ticket is open

Sent from my iPhone"""),

dict(key="0903", sent="2026-09-03 19:52", frm="rs", mailer="outlook",
     subject="Madison EOD 9/3", covers=["2026-09-03"],
     body="""Hi all,

Back from vacation, thank you Marcus for holding the fort.

Sales: $30.4K vs $40.1K plan (-24%). 21 trans, ATV ~$1.45K.
Traffic & Conv: 238 in, conv just under 9%. Lots of browsing, not much intent.
Clienteling: Priya and Dana are working the book for fall arrivals, appointments start next week.
Product: Two quality returns today, a Aurea in 0 (down coming through at the sleeve seam) and a Camilla vest in 3 (snap pulled off). Both set aside for RTV. Small group of Chinese tourists bought caps and beanies.
Ops: Nothing to flag.

Thanks,
Rebecca
""" + SIG_RS),

dict(key="0904", sent="2026-09-04 19:47", frm="rs", mailer="outlook",
     subject="Madison EOD 9/4", covers=["2026-09-04"],
     body="""Hi all,

Good start to the long weekend.

Sales: $55.2K vs $46.5K plan (+19%)
Traffic & Conv: 312 / 11.2%
Product: Tees and hoodies doing the work, black logo tee x4. Two misses: one client wanted the Valdora ski jacket in cream in a 1 (we only have 2 and 3), another asked for the vlogo cardigan in black XS, none in the building. Both on the waitlist.
Ops: Full team tomorrow, Marcus has Sunday and Monday.

R
""" + SIG_RS),

dict(key="0905", sent="2026-09-05 20:06", frm="rs", mailer="outlook",
     subject="Madison EOD Sat 9/5", covers=["2026-09-05"],
     body="""Hi all,

Sales: $79.0K vs $64.7K plan, +22%. MTD $223K, a little ahead of plan.
Traffic & Conv: 414 visitors, 11%. Solid Saturday for Labor Day weekend, tourists (UK, Mexico) plus the neighborhood regulars who stayed in the city.
Clienteling: L.K. picked up two hoodies and the Artem for her husband.
Product: Artem black sold 4 on its first real weekend. Two clients said it runs big and both took a size down after trying. Hoodies 5, cashmere scarves 3. One miss, Valdora black in a 1.

Have a good long weekend,
Rebecca
""" + SIG_RS),

dict(key="0906", sent="2026-09-06 18:37", frm="mb", mailer="iphone",
     subject="eod sun", covers=["2026-09-06"],
     body="""sun
- 43.3k / plan 50.8. didnt get there
- 42 units 27 trans
- mistral black x5 which is wild, it was 84 degrees out
- delivery 177u, all on the floor except the shoes
- 5 returns. vel 3 change of mind, valdora 2 (wanted the black instead), cortina pants colour, a sweatshirt, and a belt bag w a scratch on the buckle
bunch of brazilians and a mexican family from monterrey in the afternoon
tmrw normal hours 10-7 per lauren

Sent from my iPhone"""),

dict(key="0907", sent="2026-09-07 19:28", frm="mb", mailer="iphone",
     subject="Madison closing 9/7 labor day", covers=["2026-09-07"],
     body="""labor day, as expected. city is empty
- 23.1k vs 38.9k LY \U0001F629
- 15 trans, 198 thru the door
- small stuff, aria + alpina boots 2 each, 2 liviana black
- another client asking for vlogo cardigan black xs, thats 2 since friday. dc shows 0??
- 3 returns nothing interesting
everyone back tomorrow, rebecca opens

Sent from my iPhone"""),

# ---------------------------------------------------------------- week of Sep 7
dict(key="0908", sent="2026-09-08 19:58", frm="rs", mailer="outlook",
     subject="Madison EOD 9/8", covers=["2026-09-08"],
     body="""Hi all,

Sales: $52.4K vs $37.2K plan (+40%)
Traffic & Conv: 260 / 12.3%. The Hamptons crowd is back, felt like the first real fall day even though it was 80.
Clienteling: 6 appointments, 5 showed. Dana closed a $6K look for a top client (scarf, jersey polo, Nova).
Product: Cashmere scarves x3 and navy polos x3. Miss: Aurea in beige size 4, she wanted it today, we have it in 1 and 2 only. Asked SoHo, they have none either.
Returns: Nova 4 (changed his mind), cable knit M pilling, hoodie for colour, belt bag.

Rebecca
""" + SIG_RS),

dict(key="0909", sent="2026-09-09 20:12", frm="rs", mailer="outlook",
     subject="Madison EOD 9/9", cc=[LAUREN, MERCH], covers=["2026-09-09"],
     body="""Hi all,

Very strong Wednesday.

Sales: $58.3K vs $38.7K plan (+51%). MTD ~$400K vs $376K plan, comp running +50s.
Traffic & Conv: 265 / 9%, ATV $2.4K which says it all.
Clienteling: Mrs. R came in with both daughters and bought three Aurea black (0, 1, 2). Priya had been holding them since the delivery.
Product: Aurea black 7 units today. Copying merch planning because I'm worried about depth in black for October, we're at 1-2 per size in 0-3 after today. Also Nova navy x3 and Cosimo black x3.
Ops: Delivery 136u received and on the floor.

Thanks,
Rebecca
""" + SIG_RS),

dict(key="0910", sent="2026-09-10 19:44", frm="rs", mailer="outlook",
     subject="Madison EOD 9/10", covers=["2026-09-10"],
     body="""Hi all,

Sales: $41.4K vs $46.1K plan (-10%)
Traffic & Conv: 280 / 9.6%

Vlogo Hoodie black sold 8, mostly to a group of Mexican clients in the afternoon (they also looked at Aria, bought 2).
Artem: first exchange, a 2 for a 1. He said he was swimming in it. Third client in a week to say it runs large, so the team is now suggesting one size down at the fitting.
Aurea 3 returned for size, she'll come back for the 2.

Rebecca
""" + SIG_RS),

dict(key="0911", sent="2026-09-11 19:35", frm="mb", mailer="iphone",
     subject="closing fri 9/11", covers=["2026-09-11"],
     body="""rebecca off for the holiday, me tonight
- 48.4k vs 56.3 plan
- 32 trans
- quiet morning, its 9/11 and half the UES is at temple tonight so not a surprise
- vel 3 cream 3 navy, urban backpack x3
- artem, another one sized down at the fitting (5 to 4). starting to just tell everyone go one down
nothing else. one of the fitting room mirrors is loose, taped it

Sent from my iPhone"""),

# Sat 9/12: no email of its own (covered by Sunday recap)

dict(key="0913", sent="2026-09-13 18:52", frm="mb", mailer="iphone",
     subject="sat + sun recap", covers=["2026-09-12", "2026-09-13"],
     body="""sorry didnt send last night, closeout ran late and then i just forgot. both days here

sat 9/12
- 49.1k vs 70.7 plan. rough
- jersey polo black x8 (?? its still 80 out so ok)
- 1 guy wanted nova navy in a 7, none left in 7. sent a transfer request to soho
- cosimo black 3 is gone, 0 on hand

sun 9/13
- 29.8k vs 53.4 plan
- 19 trans
- 2 ladies asked for the cable knit in black S, nothing. also a nova black in a 1 for someones son
- delivery 227u, half still in boxes downstairs, will finish tmrw am

rosh hashanah weekend, most of our regulars away. figured slow but not this slow, the plan obviously didnt have the holiday in it
8 returns over both days, nothing defective

Sent from my iPhone"""),

dict(key="0914", sent="2026-09-14 19:22", frm="mb", mailer="iphone",
     subject="Madison closing 9/14", cc=[LAUREN, VM],
     covers=["2026-09-14"],
     body="""- 28.6k vs 41.9 plan
- 23 trans, small tickets, logo tees navy x5
- riviera 4 back for size, too short in the sleeve he said
- few korean tourists asking for aurea, didnt buy

VM here tonight for the campaign windows, they say done by 1am. ill stay till they lock up. the new backdrop is huge, hope it fits the 68th st window

Sent from my iPhone"""),

dict(key="0915", sent="2026-09-15 19:49", frm="rs", mailer="outlook",
     subject="Madison EOD 9/15", cc=[LAUREN, VM], covers=["2026-09-15"],
     body="""Hi all,

Sales: $26.9K vs $41.3K plan (-35%). Tough Tuesday.
Traffic & Conv: 253 / 7%
Product: Hoodies x5, a couple of Iridia black. Miss on the Vtrack women's in cream size 35, we never got the 35 in that color. Cosimo black 3 still at zero, transfer request sent Sunday, no answer yet.
Returns: 7 (!). Liviana 3 for size (too tight across the chest), 2 polos, a tee, the rest were gifts.
VM: Campaign windows went in overnight and look fantastic, thank you team. Campaign is live as of today. Too early to say anything about traffic.

Rebecca
""" + SIG_RS),

# subject carries the wrong date (copied from the previous evening)
dict(key="0916", sent="2026-09-16 19:55", frm="rs", mailer="outlook",
     subject="Madison EOD 9/15", covers=["2026-09-16"],
     body="""Hi all,

Sales: $42.5K vs $43.5K plan (-2%), basically on plan.
Traffic & Conv: 311 / 8.7%. Better footfall than the start of the week.
Clienteling: Two clients mentioned seeing the new ads, one on Instagram, one on the billboard on Houston. Nice to hear but they came in for other things.
Product: Vlogo Hoodie black x6, VEL in cream x4. Lost a Cosimo black 3 sale, we still have none.
Returns: Aurea 2 (quality, small tear by the zip pull), another Liviana 3 for size, second in two days. I'll keep an eye on whether the 3 runs small.

R
""" + SIG_RS),

dict(key="0917", sent="2026-09-17 22:14", frm="pr", mailer="outlook",
     cc=[LAUREN, CLT],
     subject="Madison closing - Thursday 9/17", covers=["2026-09-17"],
     body="""Hi everyone,

Closing tonight since Rebecca and Marcus are both off. We did $34.7K against $48K, so a bit short, only 15 transactions but the tickets were nice. Lots of people in (257) and quite a few British tourists in the afternoon, I think there's a big group at the Lowell.

Clienteling side: Caroline W. came for her fitting and took the Alpina in black plus a scarf, and she wants us to call her the moment the long Liviana in navy comes in. Mr. and Mrs. Abrams stopped by, just browsing for now, he's waiting for colder weather for the Monteluce. I sent four send-outs to clients at the Upper East Side hotels, two kept.

Two things we couldn't do: a lovely lady wanted the Aria in cream in a 00 and we don't have that size in cream at all, and a gentleman asked for the cashmere turtleneck in the chocolate brown in L, we only had S and M. I put both on the waitlist in the book.

One return, Iridia 2 for size, she's going to try the 3 when it comes.

Have a good night!
""" + SIG_PR),

dict(key="0918", sent="2026-09-18 20:03", frm="rs", mailer="outlook",
     subject="Madison EOD 9/18", covers=["2026-09-18"],
     body="""Hi all,

Sales: $46.0K vs $56.3K plan (-18%)
Traffic & Conv: 265 / 8.7%
Ops: The delivery due Wednesday finally showed up this morning, 2 days late, 169 units. We were missing Artem 3 and 4 for two days and had to send at least one client home. Can logistics tell us what happened?
Product: Artem black x3 as soon as it was on the floor. One miss, Nova navy in 1. Winter Gloves starting to move, which is funny in this heat.

Rebecca
""" + SIG_RS),

dict(key="0919", sent="2026-09-19 20:21", frm="rs", mailer="outlook",
     subject="Madison EOD Sat 9/19", cc=[LAUREN, MERCH], covers=["2026-09-19"],
     body="""Hi all,

Sales: $83.9K vs $80.2K plan (+5%). Comp ~+80% to LY Saturday, though LY was a weak one.
Traffic & Conv: 519 visitors, 7.5%. Busiest day since spring.
Product: Vtrack women's black x7 (!), Aurea black x4, Liviana black x4. Misses: Amalia black in 2 and the Valdora in black 4. Good mix of Chinese and Korean tourists in the afternoon, mostly on Aurea.

Heads-up for next week: UNGA starts Monday. NYPD notice says frozen zones and rolling closures around the hotels from 60th to 72nd, Madison and Park both affected. Plan for Mon-Sat is ~$340K and I honestly don't see us getting near it. I'll keep appointments flexible and offer send-outs to anyone who can't get here.

Rebecca
""" + SIG_RS),

dict(key="0920", sent="2026-09-20 18:41", frm="mb", mailer="iphone",
     subject="eod sun 9/20", covers=["2026-09-20"],
     body="""- 52.1k vs 58.1 plan
- 22 trans, nice tickets
- amalia black x4 !! first weekend it really moved
- artem exchange, 5 for a 4. runs big, we know. another artem 2 came back (gift, wrong guy)
- delivery 191u, all done
- nova navy 3, beanies navy 3

nypd already lining up barricades on park, tomorrow is going to be fun. plus yom kippur starts tonight

Sent from my iPhone"""),

# ---------------------------------------------------------------- UNGA week
dict(key="0921", sent="2026-09-21 19:47", frm="mb", mailer="iphone",
     subject="Madison closing 9/21", covers=["2026-09-21"],
     body="""unga day 1. yeah.
- 22.6k vs 42.7 plan
- 142 people thru the door all day. 142
- 15 trans
motorcade parked madison at 64th for like 40 min around 2, nobody in or out. two clients' drivers couldnt get to the door, one gave up, the other walked from 5th ave in heels and was not happy with us (or the UN). secret service all over the mark and the carlyle, the pierre has the whole block on lockdown
also yom kippur so our regulars were not shopping anyway
sold hoodies (4 black) and some beanies. thats about it \U0001F643
rest of the week will be like this, the plan is fantasy

Sent from my iPhone"""),

dict(key="lm0922", sent="2026-09-22 08:14", frm="lm", mailer="iphone",
     to=[MARCUS], cc=[OPS, REBECCA],
     subject="Re: Madison closing 9/21", reply_to="0921", suffix="_re1", covers=[],
     body="""Marcus, Rebecca - ouch. How much of yesterday is UNGA vs Yom Kippur? Planning is asking why NYC01 is so far off this week. Can you give me a rough count of clients who couldn't get in or cancelled, and what you expect for the rest of the week?

Thx
L

Sent from my iPhone"""),

dict(key="0922re", sent="2026-09-22 11:36", frm="rs", mailer="outlook",
     to=[LAUREN], cc=[MARCUS], reply_to="lm0922", suffix="_re2", covers=[],
     subject="RE: Madison closing 9/21",
     body="""Hi Lauren,

Mostly UNGA. Yom Kippur probably cost us a few of the regular Monday clients, but the real problem is access. Since yesterday morning:
- 4 appointments cancelled or moved, 2 more this morning
- at least 3 clients we know of turned back at the barricade at 66th or couldn't get a car to the door
- walk-in traffic is about half a normal Monday

For the rest of the week I'd expect -40 to -50% vs plan every day, worse on the days with the big motorcades (Tue/Wed per NYPD). The plan doesn't account for UNGA at all, it looks like a normal late-September week.

What we're doing: send-outs to clients at the Carlyle and The Mark, offering to hold pieces until Sunday, Priya is calling her top clients to move fittings to next week.

Rebecca

On Tue, Sep 22, 2026 at 8:14 AM Lauren Mitchell <lauren.mitchell@valentino-retail.example> wrote:
> Marcus, Rebecca - ouch. How much of yesterday is UNGA vs Yom Kippur? Planning is asking why NYC01 is so far off this week. Can you give me a rough count of clients who couldn't get in or cancelled, and what you expect for the rest of the week?
>
> Thx
> L
""" + SIG_RS),

dict(key="0922", sent="2026-09-22 20:09", frm="rs", mailer="outlook",
     subject="Madison EOD 9/22", covers=["2026-09-22"],
     body="""Hi all,

Sales: $20.6K vs $45.3K plan (-55%)
Traffic & Conv: 162 / 9%

Second day of UNGA and worse than yesterday. Madison was closed to traffic between 61st and 69th most of the afternoon. The few people who made it in were mostly guests staying at the hotels inside the zone, including a Mexican family at the Pierre who bought scarves and a Aurea black.
Two send-outs to The Mark, one kept (Vtrack Gtx).

Rebecca
""" + SIG_RS),

dict(key="0923", sent="2026-09-23 19:51", frm="rs", mailer="outlook",
     subject="Madison EOD 9/23", covers=["2026-09-23"],
     body="""Hi all,

Sales: $46.2K vs $47.9K plan (-4%)
Traffic & Conv: 171 in, 12.3% conv, ATV $2.2K

Small miracle: the frozen zone lifted around 1pm and three of Priya's postponed appointments came in at once. Aria black x3, Vlogo Cardigan navy x2, Mistral black x2. A few Chinese tourists too.
Delivery 135u in on time.
Astra is in the stockroom for tomorrow's launch, VM table goes up at 8am.

Rebecca
""" + SIG_RS),

# Thu 9/24: forgot to send, sent next morning
dict(key="0924", sent="2026-09-25 08:52", frm="rs", mailer="outlook",
     subject="Madison EOD 9/24 - sorry, late", covers=["2026-09-24"],
     body="""Good morning, sorry, this was sitting in my drafts last night.

Sales: $21.4K vs $58.0K plan (-63%). Worst day of the week by far.
Traffic & Conv: 199 / 5.5%, 11 trans.

Astra launch: we sold one cape (white). Maybe 8 to 10 clients tried pieces. The feedback is pretty consistent: the cape looks boxy on the hanger but is tight through the shoulders once on, and nobody loves the price for what it is. Nobody tried the balaclava. The oversized jacket got compliments, no takers.
Miss: Camilla vest in cream size 4.
Artem 4 returned for size, he wants the 3 when we get one back.

Motorcades again from 3 to 6, couldn't do anything about it.

Rebecca
""" + SIG_RS),

dict(key="0925", sent="2026-09-25 19:58", frm="rs", mailer="outlook",
     subject="Madison EOD 9/25", covers=["2026-09-25"],
     body="""Hi all,

Sales: $33.8K vs $62.7K plan (-46%)
Traffic & Conv: 253 / 9%

Barricades still up on Park, Madison open with a lot of stops. Some Chinese tourists, pink beanies x2.
Miss: VEL in cream size 6.
Astra: nothing today. Two more try-ons, same comments about the shoulders.

Rebecca
""" + SIG_RS),

dict(key="0926", sent="2026-09-26 20:14", frm="rs", mailer="outlook",
     subject="Madison EOD Sat 9/26 / UNGA week wrap", cc=[LAUREN, MERCH],
     covers=["2026-09-26"],
     body="""Hi all,

Sales: $48.8K vs $84.5K plan (-42%)
Traffic & Conv: 296 / 9.5%
Product: Urban Backpack backpacks x4, tees, navy beanies, VEL black x3. Miss: Riviera in olive size 6.

UNGA wrap: Mon-Sat we did roughly $193K against ~$341K plan, so about -$150K. All of it is access, not demand, clients told us over and over they'd come back next week. Please make sure next year's plan has UNGA week in it, the forecast treated it like any other week. Expecting a catch-up tomorrow and early next week.

Thank you to the team, it was not a fun week to be on the floor.

Rebecca
""" + SIG_RS),

dict(key="0927", sent="2026-09-27 18:33", frm="mb", mailer="iphone",
     subject="eod sun - we're back", covers=["2026-09-27"],
     body="""barricades gone, madison back to normal and it showed
- 69.4k vs 66.5 plan, +4
- 481 visitors
- aurea beige x4, nova black x3
- delivery 218u, 4 of us on it till noon
lot of the clients who couldnt come last week came today, 2 of priya's people picked up holds

Sent from my iPhone"""),

# ---------------------------------------------------------------- week of Sep 28
dict(key="0928", sent="2026-09-28 19:26", frm="mb", mailer="iphone",
     subject="Madison closing 9/28", covers=["2026-09-28"],
     body="""- 39.6k / 47 plan
- 19 trans but upt 2.0, people buying 2-3 pieces
- cable knit black x3

weird one: vel size 3 came back, zipper slider split in half, guy bought it end of august. teeth look fine, the slider itself cracked. tagged DEF and bagged it, photo in the shared drive

Sent from my iPhone"""),

dict(key="0929", sent="2026-09-29 19:46", frm="rs", mailer="outlook",
     subject="Madison EOD 9/29", cc=[LAUREN, MERCH], covers=["2026-09-29"],
     body="""Hi all,

Sales: $50.4K vs $52.0K plan (-3%)
Traffic & Conv: 308 / 8.8%
Product: Liviana black x3, navy hoodies x3, beanies.
Returns: Second VEL with a broken zipper in two days, size 6 this time, slider splitting at the base. Is QA aware of anything on VEL? Both units are from the August delivery.

Rebecca
""" + SIG_RS),

dict(key="0930", sent="2026-09-30 20:18", frm="rs", mailer="outlook",
     subject="Madison EOD 9/30 + September close", cc=[LAUREN, MERCH],
     covers=["2026-09-30"],
     body="""Hi all,

Sales: $42.9K vs $51.0K plan (-16%)
Traffic & Conv: 274 / 8%
Product: Nova black x3, Aurea black and cream x2 each. Miss: Nova olive 7.
Returns: 7 today. Third VEL zipper (6 again). Two Aria, an Ettore 3 for quality, small stuff.
Ops: Delivery 105u received.

September close: ~$1.28M vs $1.53M plan (-16%), comp ~+27% LY. Without UNGA week we would have been around -6%.

Rebecca
""" + SIG_RS),

dict(key="1001", sent="2026-10-01 22:31", frm="store", mailer="outlook",
     cc=[LAUREN, CLT], subject="Closing notes Thu 10/1", covers=["2026-10-01"],
     body="""Hi all, Priya here (sending from the store account, my Outlook is locked again, ticket is in)

$62.5K tonight, plan was $63.7K so almost there. 60 units which is a lot for a Thursday, 38 transactions. Navy logo hoodies flew (6), the Artem in black did 4, Alpina 4 and the women's Vtrack in black 4. Some Korean girls this afternoon and a Brazilian couple who bought matching hoodies.

The VEL situation is getting worse. Three came back today, a 4, a 6 and a 2, all the same problem, the zipper slider splits and won't close. One gentleman's slider came off completely while he was walking on Lexington and he was really upset, I gave him a replacement in the meantime but honestly I'm nervous the new one will do the same. All three are tagged DEF and bagged with the others.

On clienteling, Mrs. A came for her fitting and took the long Liviana, and I booked three appointments for Saturday. Everyone is asking about cold weather pieces now.

Good night,
Priya"""),

dict(key="lm1002", sent="2026-10-02 07:58", frm="lm", mailer="outlook",
     to=[STOREBOX, REBECCA], cc=[OPS],
     subject="RE: Closing notes Thu 10/1", reply_to="1001", suffix="_re1", covers=[],
     body="""Rebecca, Priya,

Thanks for flagging VEL. How many have you had back in total? QA is collecting batch numbers (inner care label) from all stores, please hold every unit, do not resell, and don't swap a customer into another unit from the same batch if you can avoid it.

Also, going forward could all of you lead the EOD with units, top 3 and misses (what clients asked for that we couldn't sell)? Planning keeps asking me for the misses and it's buried in the text.

Thanks,
""" + SIG_LM),

dict(key="1002re", sent="2026-10-02 12:41", frm="rs", mailer="outlook",
     to=[LAUREN], cc=[STOREBOX, MERCH], reply_to="lm1002", suffix="_re2", covers=[],
     subject="RE: Closing notes Thu 10/1",
     body="""Hi Lauren,

6 so far since Monday 9/28: sizes 3, 6, 6, 4, 6, 2. All the same failure, the slider cracks and the zipper won't close. All show batch 07/26 on the inner label. All 6 are held in the stockroom, nothing resold.

We still have 60-ish VEL in stock across colors and sizes. Do we pull them? I'd rather get a clear RTV or recall instruction than keep selling and taking them back. Priya swapped one client into a new unit yesterday, we'll call him.

Will do units / top 3 / misses from now on.

Rebecca
""" + SIG_RS + """
-----Original Message-----
From: Lauren Mitchell <lauren.mitchell@valentino-retail.example>
Sent: Friday, October 2, 2026 7:58 AM
To: nyc01.store@valentino-retail.example; Rebecca Stein <rebecca.stein@valentino-retail.example>
Cc: retail-ops-usa@valentino-retail.example
Subject: RE: Closing notes Thu 10/1

Rebecca, Priya,

Thanks for flagging VEL. How many have you had back in total? QA is collecting batch numbers (inner care label) from all stores, please hold every unit, do not resell, and don't swap a customer into another unit from the same batch if you can avoid it.

Also, going forward could all of you lead the EOD with units, top 3 and misses (what clients asked for that we couldn't sell)? Planning keeps asking me for the misses and it's buried in the text.
"""),

dict(key="1002", sent="2026-10-02 19:54", frm="rs", mailer="outlook",
     subject="Madison EOD 10/2", cc=[LAUREN, MERCH], covers=["2026-10-02"],
     body="""Hi all,

Sales: $77.7K vs $70.1K plan (+11%)
Units: 60 / 37 trans
Top: Aurea black x5, Nova black x4, Aria black x4, Vlogo Cardigan black x4
Misses: none at the desk today, but we sold our last Aurea black 3 at 4pm, so tomorrow will be a problem.

Returns: two more VEL with the zipper (4 and 2), that's 8. Artem 4 back for size (went to a 3), Nova 4 back for size.

Rebecca
""" + SIG_RS),

dict(key="1003", sent="2026-10-03 20:27", frm="rs", mailer="outlook",
     subject="Madison EOD Sat 10/3", covers=["2026-10-03"],
     body="""Hi all,

Sales: $61.4K vs $98.6K plan (-38%)
Units: 59 / 29 trans
Traffic & Conv: 552 in, 5.3%. The store was packed and nobody was buying big, lots of browsing and photo-taking. The $98K plan looks like it was built off a much bigger Saturday.
Top: Vtrack women's black x4, hoodies black x4, crewneck black x4
Misses: Aurea black 3, as expected. Client is on the waitlist.

Returns: VEL 4, zipper (#9). Artem 5 for size, Nova 7 for size, cable knit M.

R
""" + SIG_RS),

dict(key="1004", sent="2026-10-04 18:29", frm="mb", mailer="iphone",
     subject="eod sun", covers=["2026-10-04"],
     body="""- 54.1k vs 71.1 plan
- 21 trans, 426 in. lookers
- hoodies navy + black 3 each, nova navy 3, cashmere turtleneck in the brown x2
- aurea black 3 again, 2nd ask this week. nothing to give her
- vel zipper #10 (sz 2)
- delivery 231u, done by 3

Sent from my iPhone"""),

dict(key="1004c", sent="2026-10-04 18:58", frm="mb", mailer="iphone",
     subject="eod sun - correction", suffix="_corr", covers=["2026-10-04"],
     body="""correction, sales were 45.1k not 54.1k. fat fingers. so -37% vs plan. sorry

Sent from my iPhone"""),

dict(key="1005", sent="2026-10-05 19:31", frm="mb", mailer="iphone",
     subject="closing mon 10/5", covers=["2026-10-05"],
     body="""- 52.2k vs 52.6, flat
- units 41
- top: mistral navy x4, beanies black 3, belt bags 2
- misses: none today
aurea black 3 still zero, dc says nothing before mid oct
astra: still sitting on all the oversized jackets, not one sold since launch
artem 5 came back, change of mind

Sent from my iPhone"""),

# ---------------------------------------------------------------- week of Oct 5
dict(key="1006", sent="2026-10-06 20:02", frm="rs", mailer="outlook",
     subject="NYC01 EOD Recap | Tue 10/6", covers=["2026-10-06"],
     body="""Hi all,

Units: 42 / 24 trans
Sales: $50.1K vs $54.7K plan (-8%), MTD $349K vs $411K
Top 3: VEL navy x4 (yes, still selling), Urban Backpack x3, crewneck black x3
Misses: Iridia in pink, size 1. She showed us a TikTok of the K-pop singer wearing it in Paris. We only got pink in a 00 and a 3, nothing in between. First time anyone asked for it by name.

Other: SoHo called around 3, their registers were down for the afternoon and they sent two clients up to us, one bought.
Aurea black 3 still zero.

Rebecca
""" + SIG_RS),

dict(key="1007", sent="2026-10-07 19:49", frm="rs", mailer="outlook",
     subject="NYC01 EOD Recap | Wed 10/7", covers=["2026-10-07"],
     body="""Hi all,

Units: 57 / 37 trans
Sales: $68.5K vs $57.7K plan (+19%)
Top 3: Liviana black x4, vlogo hoodie black x3, Aurea beige x3
Misses: nothing new at the desk. Aurea black 3 at zero since Friday, waitlist is 3 names.
Delivery 165u, on time. No Aurea black in it.

Comp is running ~+39% MTD.

Rebecca
""" + SIG_RS),

dict(key="1007d", sent="2026-10-07 19:51", frm="rs", mailer="outlook",
     subject="NYC01 EOD Recap | Wed 10/7", suffix="_dup", covers=["2026-10-07"],
     body="""Hi all,

Units: 57 / 37 trans
Sales: $68.5K vs $57.7K plan (+19%)
Top 3: Liviana black x4, vlogo hoodie black x3, Aurea beige x3
Misses: nothing new at the desk. Aurea black 3 at zero since Friday, waitlist is 3 names.
Delivery 165u, on time. No Aurea black in it.

Comp is running ~+39% MTD.

Rebecca
""" + SIG_RS),

dict(key="1008", sent="2026-10-08 20:41", frm="rs", mailer="iphone",
     subject="NYC01 EOD 10/8", covers=["2026-10-08"],
     attach=[{"name": "NYC01_closing_form_1008.xlsx", "rows": [
         ["NYC01 MADISON - DAILY CLOSING FORM", ""],
         ["Business date", "10/08/2026"],
         ["Closed by", "R. Stein"],
         ["Net sales USD", 65900],
         ["Plan USD", 68550],
         ["vs plan", "-3.9%"],
         ["Transactions", 26],
         ["Units", 44],
         ["Traffic", 401],
         ["Conversion", "6.5%"],
         ["Top 3", "MISTRAL blk x5 / RIVIERA blk x3 / AUREA navy x3"],
         ["Misses", "CAMILLA vest blk sz 4 (2 clients) ; AUREA blk sz 3 (waitlist)"],
         ["Returns", "VEL x2 zipper DEF (3, 3) held ; valentino scarf ; tricot cardi M"],
         ["Deliveries", "none"],
         ["Notes", "Fiammetta navy x3. Cooler evening, outerwear picking up."],
     ]}],
     body="""See attached, running to a client dinner.
R

Sent from my iPhone"""),

dict(key="1009", sent="2026-10-09 19:38", frm="mb", mailer="iphone",
     subject="Madison closing fri 10/9", covers=["2026-10-09"],
     body="""covering for rebecca
- 66.4k vs 76.2 plan
- units 51
- top: nova black x5, alpina 3, amalia black 3
- misses: nobody asked for anything we didnt have, except the usual aurea black 3
first morning you actually needed a jacket, gloves selling again
2 aurea back: a 1 with feathers poking through the seam (quality) and a 2 for size

Sent from my iPhone"""),

dict(key="1010", sent="2026-10-10 20:44", frm="rs", mailer="outlook",
     subject="NYC01 EOD Recap | Sat 10/10", cc=[LAUREN, MERCH], covers=["2026-10-10"],
     body="""Hi all,

Best day of the year so far.

Units: 90 / 58 trans
Sales: $115.9K vs $105.8K plan (+10%)
Traffic & Conv: 758 / 7.7%
Top 3: Artem black x6 (everyone sized down, zero issues), Aria black x6, VEL cream x4
Misses: Cosimo navy in 3, two separate clients. Mistral black in 1.

What drove it: first cold weekend plus Priya's appointment block, the M. family alone was ~$18K. A couple of people mentioned the ads, but I'd say weather and appointments did the heavy lifting. Some Mexican and Brazilian clients in the afternoon.

VEL zipper #13 today (5). Still waiting on the RTV instruction.

Rebecca
""" + SIG_RS),

# sent to the wrong distribution list (Canada)
dict(key="1011", sent="2026-10-11 18:46", frm="mb", mailer="iphone",
     to=["retail-ops-canada@valentino-retail.example"],
     subject="eod sun 10/11", covers=["2026-10-11"],
     body="""- 72.5k / 81.1 plan
- units 62
- top: vlogo padded cardigan navy x4, liviana black x4, monteluce black 3
- misses: cosimo navy in a 3 and a 6, both today. we have black only in those sizes
lot of chinese tourists this afternoon, golden week stragglers?
cosimo 5 came back, wanted navy instead of black, couldnt swap him (see above)
vel #14 (4)

Sent from my iPhone"""),

dict(key="1012", sent="2026-10-12 20:11", frm="rs", mailer="outlook",
     subject="NYC01 EOD Recap | Mon 10/12", covers=["2026-10-12"],
     body="""Hi all,

Columbus Day, all hands on the floor.

Units: 59 / 32 trans
Sales: $74.2K vs $57.8K plan (+28%), MTD $812K vs $858K
Top 3: vlogo hoodie black x4, vlogo cardigan navy x3, Liviana navy x3
Misses: none logged. A few Canadian clients in town for Thanksgiving weekend.

Ops: Delivery that was due yesterday came today instead (holiday), 243 units, so we were short on hoodies in the morning. Still no Aurea black 3.

Rebecca
""" + SIG_RS),

dict(key="1013", sent="2026-10-13 19:33", frm="mb", mailer="iphone",
     subject="closing tue 10/13", covers=["2026-10-13"],
     body="""rebecca off today
- 61.2k vs 55.2 plan, +11
- units 46
- top: nova navy x5, mistral black 3, iridia black 3
- misses: liviana navy 3
iridia: 2 girls came in asking for "the pink one from tiktok". pink is down to one 00, nobody that tiny. one took the black
aria 3 back, quality, pocket zip

Sent from my iPhone"""),

dict(key="1014", sent="2026-10-14 22:48", frm="pr", mailer="outlook",
     cc=[LAUREN, CLT], subject="Madison closing Wed 10/14", covers=["2026-10-14"],
     body="""Hi everyone,

Closing again tonight! We did about $56.8K on the register today, plan was $61.4K. 47 units, 27 transactions.

Top three: VEL in black x4, black logo hoodies x3, Ettore black x3. And Nova black did 3 too.
Misses: only one, a young woman wanted the white logo tee in XS, we're out of XS in white.

Delivery came in at 11 (204 units) and the girls did an amazing job getting it out before the lunch rush. Still no black Aurea in a 3 in it, I had to call Mrs. Feldman again to tell her.

Clienteling: Jonathan B. bought the Ettore and the VEL for his trip to Aspen in November, I told him to come back if he has any problem with the zip. Caroline W.'s Liviana navy is still not here. A Aurea 0 came back for size, she's going to the 1.

Thank you and good night!
""" + SIG_PR),

dict(key="lm1014", sent="2026-10-14 22:48", frm="lm",
     to=[PRIYA], cc=[], reply_to="1014", suffix="_ooo", covers=[],
     extra_headers={"Auto-Submitted": "auto-replied", "X-Auto-Response-Suppress": "All"},
     subject="Automatic reply: Madison closing Wed 10/14",
     body="""I am traveling Oct 14-16 (Toronto) with limited access to email. For urgent matters please contact retail-ops-usa@valentino-retail.example.

Lauren Mitchell"""),

dict(key="1015", sent="2026-10-15 20:06", frm="rs", mailer="outlook",
     subject="NYC01 EOD Recap | Thu 10/15", cc=[LAUREN, MERCH], covers=["2026-10-15"],
     body="""Hi all,

Units: 54 / 32 trans
Sales: $57.5K vs $69.3K plan (-17%)
Top 3: vlogo beanie black x9 (it was 48 this morning), Liviana cream x3, Vtrack Gtx x3
Misses: Aurea black in 1, Aurea black in 4.

Aurea black is now at zero in both 1 and 3. Merch, is there anything coming before the end of the month? We lose at least one Aurea black sale a day at this point.

Rebecca
""" + SIG_RS),

dict(key="1016fw", sent="2026-10-16 11:05", frm="pr", mailer="outlook",
     to=[REBECCA], cc=[MARCUS], suffix="_fwd", covers=[],
     subject="FW: Aurea black - size 3?",
     body="""Rebecca, see below from Ellen Feldman (she's one of my VICs, around $40K last year). She's been on the waitlist for the Aurea black 3 since the beginning of October. Can we ask SoHo or Beverly Hills if they have one? I don't want to lose her to the navy, she'll just not buy.

Priya

---------- Forwarded message ---------
From: Ellen Feldman <ellen.feldman@example.com>
Date: Fri, Oct 16, 2026 at 9:12 AM
Subject: Aurea black - size 3?
To: Priya Raman <priya.raman@valentino-retail.example>

Hi Priya,

Any news on the black Aurea in a 3? We leave for Aspen on the 6th and I really wanted it for the trip. If it's not coming I could consider the navy but I really prefer the black. Could you check if another store has one?

Thank you!
Ellen
""" + SIG_PR),

dict(key="1016", sent="2026-10-16 20:19", frm="rs", mailer="outlook",
     subject="NYC01 EOD Recap | Fri 10/16", covers=["2026-10-16"],
     body="""Hi all,

Units: 77 / 42 trans
Sales: $97.3K vs $81.1K plan (+20%)
Top 3: Nova in navy and in black, 4 each, plus black crewnecks x4
Misses: the Aurea black 3 again (a walk-in, on top of Priya's VIC who is waiting), Liviana navy in 1.

Vlogo Cardigan navy XL is now gone too.
Asked SoHo and BH for a Aurea black 3 for the Feldman client, waiting to hear back.

R
""" + SIG_RS),

dict(key="1017", sent="2026-10-17 21:02", frm="rs", mailer="outlook",
     subject="NYC01 EOD Recap | Sat 10/17", cc=[LAUREN, MERCH], covers=["2026-10-17"],
     body="""Hi all,

New record for the store.

Units: 110 / 64 trans
Sales: $116.7K vs $110.1K plan (+6%)
Traffic & Conv: 762 / 8.4%
Top 3: relaxed sweatshirt black x9 AND white x9, Nova black x7, vlogo hoodie black x7
Misses: Iridia black 00, cable knit black XS, crewneck black XS, Alpina cream 38.

The crewnecks were a college crowd (parents' weekend?) plus a Brazilian family who took 6. Aurea black is now out in 0, 1 and 3, the size curve in black is basically gone.
VEL zipper #15 (size 1).

Very proud of the team today.

Rebecca
""" + SIG_RS),

dict(key="1018", sent="2026-10-18 18:38", frm="mb", mailer="iphone",
     subject="eod sun 10/18", covers=["2026-10-18"],
     body="""- 71.2k vs 89.9 plan
- units 73
- top: vita belt bag belt bags x5, hoodies black x5, logo cardi black 4 + navy 4
- misses: ettore black 2, jersey polo black xxl
artem exchange again, 5 for a 4. we size everyone down from the start now, this one was bought online
delivery 184u, in by 2
aurea back for size (2), aria 3, mistral 4 for size

Sent from my iPhone"""),

dict(key="1019", sent="2026-10-19 19:41", frm="mb", mailer="iphone",
     subject="Madison closing mon 10/19", covers=["2026-10-19"],
     body="""monday!!
- 96k vs 60.3 plan, +59%. best monday ive seen here
- units 78, 49 trans
- top: mistral black x5, vlogo cardigan black 4, nova black 4
- misses: none
honestly think the campaign is finally paying off. the billboards are everywhere now, 3 or 4 people today said they saw the ads. priya had mrs h in too which helped
aurea 0 back quality, a couple of crewnecks for size

Sent from my iPhone"""),

dict(key="lm1020", sent="2026-10-20 07:52", frm="lm", mailer="outlook",
     to=[MARCUS], cc=[REBECCA, OPS],
     subject="RE: Madison closing mon 10/19", reply_to="1019", suffix="_re1", covers=[],
     body="""Great Monday, well done team! Marcus, Rebecca: marketing is asking all stores for anecdotes on the campaign for Thursday's call. Is it really driving traffic at Madison? Can I quote yesterday?

""" + SIG_LM),

dict(key="1020re", sent="2026-10-20 10:18", frm="rs", mailer="outlook",
     to=[LAUREN], cc=[MARCUS], reply_to="lm1020", suffix="_re2", covers=[],
     subject="RE: Madison closing mon 10/19",
     body="""Hi Lauren,

I'd be careful quoting yesterday as a campaign day. Honestly the campaign lift is hard to see in our numbers, maybe a few % on traffic since mid-September. Yesterday was mostly two VIC appointments Priya set up (Mrs. H took three Mistral for her sons plus cardigans, the other client did a full look), roughly $31K between them, plus the first properly cold Monday. Traffic was 450, a normal October Monday is ~300-350.

Happy to give marketing a couple of anecdotes, a few clients do mention the billboards, but I wouldn't tie the +59% to it.

Rebecca

On Tue, Oct 20, 2026 at 7:52 AM Lauren Mitchell <lauren.mitchell@valentino-retail.example> wrote:
> Great Monday, well done team! Marcus, Rebecca: marketing is asking all stores for anecdotes on the campaign for Thursday's call. Is it really driving traffic at Madison? Can I quote yesterday?
""" + SIG_RS),

dict(key="1020", sent="2026-10-20 19:57", frm="rs", mailer="outlook",
     subject="NYC01 EOD Recap | Tue 10/20", covers=["2026-10-20"],
     body="""Hi all,

Units: 45 / 29 trans
Sales: $46.4K vs $61.7K plan (-25%)
Top 3: vlogo hoodie black x5, beanies navy x5, beanies black x3
Misses: Aurea black 0 and Aurea black 3. Both clients left their numbers.

Returns: Liviana 1 for size, Riviera 4 for size, Nova 4 for color, crewneck.
Quiet after yesterday, rain all afternoon.

R
""" + SIG_RS),

dict(key="1021", sent="2026-10-21 20:16", frm="rs", mailer="outlook",
     subject="NYC01 EOD Recap | Wed 10/21", cc=[LAUREN, MERCH], covers=["2026-10-21"],
     body="""Hi all,

Units: 59 / 36 trans
Sales: $79.8K vs $68.7K plan (+16%). MTD ~$1.49M vs $1.52M plan, comp around +50%.
Top 3: Aurea navy x3, Nova olive x3, Monteluce black x3 (Nova black x3 too)
Misses: none at the desk, the Aurea black waitlist is now 5 names.

Delivery: 314u, biggest of the season. One Aurea black in 1 came in, still nothing in 0 or 3.

Astra: the balaclava came back today, too tight (size). Since launch we've sold one cape and one balaclava, and the balaclava is now returned. I'd suggest we move the Astra units to a store where it's working, or at least not reorder. It's taking a full table.
Also a Aurea 1 returned for quality, Liviana 2 for size, logo cardi XL quality.

Rebecca
""" + SIG_RS),
]
