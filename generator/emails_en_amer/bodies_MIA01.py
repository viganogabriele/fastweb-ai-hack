STORE = "MIA01"

WRITERS = {
    "dr": "Daniela Restrepo <daniela.restrepo@valentino-retail.example>",
    "kh": "Kevin Hall <kevin.hall@valentino-retail.example>",
    "vs": "Valentina Soto <valentina.soto@valentino-retail.example>",
    "box": "MIA01 Design District <mia01.store@valentino-retail.example>",
    "lm": "Lauren Mitchell <lauren.mitchell@valentino-retail.example>",
}

LM = "Lauren Mitchell <lauren.mitchell@valentino-retail.example>"
OPS = "retail-ops-usa@valentino-retail.example"
MERCH = "merch-planning-americas@valentino-retail.example"
BOX = "mia01.store@valentino-retail.example"
DR = "Daniela Restrepo <daniela.restrepo@valentino-retail.example>"

DEFAULT_TO = [OPS]
DEFAULT_CC = [LM]

SIG_DR = """Daniela Restrepo | Store Manager
Valentino Miami Design District
140 NE 39th St, Miami, FL 33137"""

HABIT_LINES = [SIG_DR, "Sent from my iPhone"]

EMAILS = [
    dict(key="0831", sent="2026-08-31 20:41", frm="kh", mailer="iphone", covers=["2026-08-31"],
         subject="MIA EOD",
         body="""5.5k vs 7.5 plan. 2 tickets, both in the afternoon. nova black and aurea navy to the same lady

nova 3 came back for size, exchanged for nothing, refund

end of aug, glad its over lol

Sent from my iPhone"""),

    dict(key="0901", sent="2026-09-01 20:52", frm="dr", covers=["2026-09-01"],
         subject="Miami closing 9/1",
         body=f"""Hola team,

$7.4K today vs $7.8K plan, 7 tickets, so almost there. Belt bags x2 and 2 Nova black. A Brazilian couple came at 6 asking for the Aurea in navy size 2 and 3, we have been out of those since last week. Also cream Aurea 2. Can somebody check if Madison has them?

Super hot outside, 94 and humid, the street was empty until 5.

Dani

{SIG_DR}"""),

    dict(key="0902", sent="2026-09-02 20:38", frm="dr", covers=["2026-09-02"],
         subject="Miami closing 9/2",
         body=f"""Hi all,

$3.4K vs $7.4K. Bad one, only small stuff (beanie, jersey polo, 2 tees). Mistral 7 came back, was a gift.

The AC started making a weird noise around 3pm, I called the landlord. Hopefully nothing.

Dani

{SIG_DR}"""),

    dict(key="0903", sent="2026-09-03 21:15", frm="dr", covers=["2026-09-03"],
         attach=[{"name": "IMG_2207.jpg"}, {"name": "IMG_2209.jpg"}],
         subject="Miami closing 9/3 - AC DOWN",
         body=f"""Hi all,

Ay, what a day. The AC died completely this morning at 11:30. By 2pm the thermostat inside said 86°F (pictures attached). The Design District management sent their HVAC guy, he says the compressor is gone and the part comes Friday or Saturday. We put 3 fans on the floor and opened the back door but honestly nobody wants to try a down jacket at 86 degrees.

$3.5K vs $11.6K plan. 4 tickets, all accessories and a tee. At least 3 clients walked in, said "it's so hot in here" and left after 2 minutes.

Staff is fine, we are drinking a lot of water. I moved the leather and the knitwear away from the window.

Can somebody from facilities call me tomorrow first thing? I already opened ticket FAC-31877.

Dani

{SIG_DR}"""),

    dict(key="0903re1", sent="2026-09-04 08:22", frm="lm", reply_to="0903", suffix="_re1", covers=[],
         to=[DR], cc=[OPS, "facilities-na@valentino-retail.example"],
         subject="RE: Miami closing 9/3 - AC DOWN",
         body="""Dani, so sorry. Facilities is on it, Mark will call you at 10.

Can you rent portable units for the weekend so we don't lose Saturday? Approved up to $1,500, send me the invoice. And please keep the team on short shifts if it gets above 85 inside.

Lauren

Sent from my iPhone

> On Sep 3, 2026, at 9:15 PM, Daniela Restrepo <daniela.restrepo@valentino-retail.example> wrote:
>
> Ay, what a day. The AC died completely this morning at 11:30."""),

    dict(key="0903re2", sent="2026-09-04 12:47", frm="dr", reply_to="0903re1", suffix="_re2", covers=[],
         to=[LM], cc=[OPS],
         subject="RE: Miami closing 9/3 - AC DOWN",
         body=f"""Gracias Lauren! Spoke with Mark. Portable units coming at 4pm today (2 of them, $1,180 for 4 days). The compressor is ordered, technician says Saturday afternoon or Sunday morning.

Today so far 2 tickets. It's 84 inside with the fans.

Dani

{SIG_DR}"""),

    dict(key="0904", sent="2026-09-04 20:58", frm="dr", covers=["2026-09-04"],
         subject="Miami closing 9/4",
         body=f"""Hi all,

$5.9K vs $13.4K. 4 tickets. Portable units arrived 4:30 and it got better, 79-80 inside by 7pm but still sticky. A Chinese client bought a scarf and beanie, everyone else was just passing through to cool off lol.

One tee returned with a hole in the seam, and a Nova 2 the client changed her mind.

Tomorrow should be better. Fingers crossed.

Dani

{SIG_DR}"""),

    dict(key="0905", sent="2026-09-05 20:49", frm="dr", covers=["2026-09-05"],
         subject="Miami closing Sat 9/5",
         body=f"""Hola,

$18.5K vs $17.3K plan!! With the portable units it was ok inside, 76. 11 tickets, Brazilians and a British family on holiday. Caps, 2 Mistral navy, padded cardigan.

Technician came at 3pm and installed the new compressor, it's working. We will keep the portables until Monday just in case.

Somebody asked for the logo tee navy in S, we don't have S.

Long weekend, I'm off tomorrow, Valentina is closing.

Dani

{SIG_DR}"""),

    dict(key="0906", sent="2026-09-06 18:44", frm="vs", covers=["2026-09-06"],
         subject="closing miami sunday",
         body="""Hi,

- Sales: 10.7K (plan 13.2K)
- 7 transactions
- Jersey Polo navy x2 and Camilla off white x2 (to a mother and daughter, matching lol)
- 1 client asked Riviera olive 7, we don't have
- delivery 72 units, all good, all in the stockroom

AC is perfect today.

Vale"""),

    dict(key="0907", sent="2026-09-07 20:35", frm="kh", mailer="iphone", covers=["2026-09-07"],
         subject="eod miami labor day",
         body="""15k vs 9.4 plan 💪 nice

brazilian holiday today too so the place was full of brazilians. nova navy x4 (!!) all going to europe next month

nova navy 4 and 5 are now gone. aurea 2 return size

returned the portable acs

Sent from my iPhone"""),

    dict(key="0908", sent="2026-09-08 20:40", frm="dr", covers=["2026-09-08"],
         subject="Miami 9/8",
         body=f"""$13.0K vs $9.2K. 6 tickets, nice mix (Brazil, Mexico, UK). Hoodies, caps, tees.

Nothing special, AC still fine 🙏

Dani"""),

    dict(key="0909", sent="2026-09-09 20:46", frm="dr", covers=["2026-09-09"],
         subject="Miami closing 9/9",
         body=f"""Hi,

$6.0K, plan $9.7K. Only 3 tickets but one was a Nova black + Cosimo black for a Brazilian guy moving to London.

A lady asked for the Alpina black 38 for a ski trip to Aspen in December. We don't carry many boots here, we had 1 pair in 39. Is it possible to get a 38 from Aspen or Madison?

Dani

{SIG_DR}"""),

    dict(key="0910", sent="2026-09-10 20:31", frm="dr", covers=["2026-09-10"],
         subject="Miami closing 9/10",
         body=f"""$6.0K vs $11.5K. 7 small tickets, tees and caps. Korean couple, Mexican family. Rain all afternoon.

Aria black 3 and Iridia black 3 still at zero, nobody asked though.

Dani"""),

    dict(key="0911", sent="2026-09-11 21:05", frm="kh", mailer="iphone", covers=["2026-09-11"],
         subject="MIA EOD fri",
         body="""12.6k vs 12.9 basically even

missed a vel cream 2, cable knit cream L and hoodie grey XS. all sizes we dont have. small store problems

belt bag, sweatshirt, turtleneck, cable knit. 7 trx

Sent from my iPhone"""),

    dict(key="0912", sent="2026-09-12 20:57", frm="dr", covers=["2026-09-12"],
         subject="Miami closing Sat 9/12",
         body=f"""Hi all,

$7.3K vs $18.4K plan. Not good at all. Traffic was ok (almost 100 people) but it's 93 degrees and nobody is thinking about jackets. 5 tickets, sweatshirts and one Vtrack. A guy wanted the Vtrack grey in 42, we only had 43 and 44.

Honestly the plan for September has a lot of outerwear in it and Miami in September is summer. We need more tees, polos and caps, those are what sells.

Dani

{SIG_DR}"""),

    dict(key="0913", sent="2026-09-13 18:39", frm="vs", covers=["2026-09-13"],
         subject="closing miami sunday 9/13",
         body="""Hello,

- Sales 10.4K vs 13.4K plan (I think? the plan sheet says 12.4)
- 6 transactions
- belt bag, tees, women's vtrack cream
- client asked the cashmere turtleneck black S, we are out of S
- delivery 76 units

Vale"""),

    dict(key="0914", sent="2026-09-14 20:33", frm="kh", mailer="iphone", covers=["2026-09-14"],
         subject="eod",
         body="""7.2k vs 9.2. padded cardi black x2. pink beanie. nova 3 return again for size (2nd nova 3 this month, are they running small??)

Sent from my iPhone"""),

    dict(key="0915", sent="2026-09-15 20:44", frm="dr", covers=["2026-09-15"],
         subject="Miami closing 9/15",
         body=f"""Hi all,

$8.9K vs $9.4K. 7 tickets. Vel off-white x2 to a Mexican client, caps, Vtrack women's.

The new campaign is live on Instagram, two clients mentioned it. We don't have any billboard in Miami? I saw the NY ones on LinkedIn, so nice.

Dani

{SIG_DR}"""),

    dict(key="0916", sent="2026-09-16 20:51", frm="dr", covers=["2026-09-16"],
         subject="Miami closing 9/16",
         body=f"""Hola,

$16.3K vs $9.7K plan 🎉 8 tickets. Mexican independence day, and we had a really nice Mexican family from Monterrey who bought sweatshirts and beanies for the whole family and a Mistral. Also a Korean girl.

Missed: Nova navy 2 (for the girlfriend), and the black crewneck in XL which is out.

Dani

{SIG_DR}"""),

    dict(key="0917", sent="2026-09-17 20:29", frm="dr", covers=["2026-09-17"],
         subject="Miami closing 9/17",
         body=f"""Hi,

$4.7K vs $11.1K. 3 tickets.

2 asks that we lost: Amalia black size 1 (we are out of 1 and 2 now) and Cosimo navy 5. The Amalia client is a regular from Caracas, she is going to NY in October, maybe Madison can hold one for her?

2 returns for size, Camilla 0 and Nova 6.

Dani

{SIG_DR}"""),

    dict(key="0918", sent="2026-09-18 21:02", frm="dr", covers=["2026-09-18"],
         subject="Miami closing Fri 9/18",
         body=f"""Hi all,

$12.3K vs $13.6K. 7 tickets. Turtleneck black x2.

Lost:
Aurea navy 1
Vlogo Cardigan black XL
Vtrack women's black 35 (we never get 35)

Aurea navy is now out in 1 and 2. Aurea black 1 and cream 1 out too. For a store our size, when 1 size goes we lose the client.

Dani

{SIG_DR}"""),

    dict(key="0919", sent="2026-09-19 21:22", frm="kh", mailer="iphone", covers=["2026-09-19"],
         subject="MIA EOD sat",
         body="""14k vs 17.9. aurea beige x2 to korean sisters.

lost amalia black 1 (again, thats 2 this week) and vel cream 6

Sent from my iPhone"""),

    dict(key="0920", sent="2026-09-20 18:51", frm="kh", mailer="iphone", covers=["2026-09-20"],
         subject="sunday",
         body="""5.6k vs 12.9 plan. slow sunday, dolphins game. 7 small tickets. aria 4 gift return. delivery 68 pcs

Sent from my iPhone"""),

    # 9/21 missing: Kevin forgot; mentioned in 0922

    dict(key="0922", sent="2026-09-22 20:39", frm="dr", covers=["2026-09-22"],
         subject="Miami closing 9/22",
         body=f"""Hi all,

Kevin forgot to send yesterday, sorry. Monday was very slow, around $4K.

Today $9.2K vs $10.2K plan. 4 tickets, Nova black x2, Alpina black (finally a boot sale), sweatshirt.

Dani

{SIG_DR}"""),

    dict(key="0923", sent="2026-09-23 20:36", frm="dr", covers=["2026-09-23"],
         subject="Miami closing 9/23",
         body=f"""$11.3K vs $10.0K ✔️ 8 tickets. White beanies x3 (?!), Nova black x2 to a Brazilian man.

Lost: Fiammetta black 00 and cable knit cream XXL.

Dani"""),

    dict(key="0924", sent="2026-09-24 20:58", frm="dr", covers=["2026-09-24"],
         subject="Miami closing 9/24 - Astra launch",
         body=f"""Hi all,

$8.8K vs $12.4K. 8 tickets.

Astra is in the window since this morning. 4 people tried it, mostly the oversized. Comments: beautiful but it runs small in the shoulders, and $ is too much for something they will wear 2 weeks a year. Nobody bought today. Honestly for Miami I don't see it, maybe for the Brazilian clients going to Europe.

Lost: cable knit beige S, sweatshirt grey L, jersey polo navy S. Again knitwear and jersey sizes.

Dani

{SIG_DR}"""),

    dict(key="0925", sent="2026-09-25 20:47", frm="dr", covers=["2026-09-25"],
         subject="Miami closing 9/25",
         body=f"""$11.0K vs $14.1K. 9 tickets, Nova black x2, caps, tees.

Vtrack grey 40 asked, out.

Everybody is talking about the tropical wave near the Bahamas, the cone is not on us for now. Pray for us 🙏

Dani"""),

    dict(key="0926", sent="2026-09-26 21:12", frm="dr", covers=["2026-09-26"],
         subject="Miami closing Sat 9/26",
         body=f"""Hola,

$24.5K vs $19.8K plan 🎉 15 tickets. Good Saturday, lots of international clients (Argentina, Colombia, a couple from Spain). Scarves, padded cardigans, logo cardigans, tees.

Aurea black 4 asked, we never had 4 in black.

Dani

{SIG_DR}"""),

    dict(key="0927", sent="2026-09-27 19:08", frm="kh", mailer="iphone", covers=["2026-09-27"],
         subject="MIA EOD sunday 🔥",
         body="""29.7k vs 15.4!!! best day in weeks 🏀🔥

brazilian group in the afternoon going to switzerland, bought cosimo black x2, mistral navy x2 and 1 astra oversized black (first astra sold!!)

missed cosimo black 6 for the dad

delivery 65 pcs

Sent from my iPhone"""),

    dict(key="0928", sent="2026-09-28 20:44", frm="kh", mailer="iphone", covers=["2026-09-28"],
         subject="MIA EOD 9/28",
         body="""23.2k, +118% vs LY 💪💪

nova navy x2, mistral navy x2, fiammetta black x2. 9 trx

lost fiammetta black 1 and cable knit cream M. fiammetta black 0 and 1 both out now

vel 6 return change of mind

Sent from my iPhone"""),

    dict(key="0929", sent="2026-09-29 20:52", frm="dr", covers=["2026-09-29"],
         subject="Miami closing 9/29",
         body=f"""Hi all,

$3.1K vs $11.0K. 5 small tickets incl. 1 Astra Balaclava.

Lost:
Aurea black 1
Nova navy 3
Alpina black 39

The storm is the only topic, half my clients cancelled appointments "until we know where it goes". The NHC says 50% now. Everybody is at Publix buying water instead of shopping. It will probably turn north like always.

Dani

{SIG_DR}"""),

    dict(key="0930", sent="2026-09-30 20:41", frm="dr", covers=["2026-09-30"],
         subject="Miami closing 9/30",
         body=f"""Hi,

$2.8K vs $11.8K. 2 tickets, terrible end of month. September closed around $310K vs ~$355K plan.

2 Vel returned today, both with the zipper broken (the slider opens in the middle). Client was not happy, he bought 2 for him and his son in August. I gave refund. Is there a problem with this Vel?

Lost: Nova olive 2, Mistral navy 3, Vtrack women's cream 40.

Storm turned north, nada. Good news at least.

Dani

{SIG_DR}"""),

    dict(key="1001", sent="2026-10-01 20:55", frm="dr", covers=["2026-10-01"],
         subject="Miami closing 10/1",
         body=f"""$11.8K vs $13.6K. 4 tickets, Mistral black x2, Nova olive, cable knit beige.

A Brazilian client asked the Fiammetta black size 1 (again, 3rd time in a week) and a man the Artem navy in 1. I told him Artem is big so 1 would be like a 2 but we don't have either.

Dani

{SIG_DR}"""),

    dict(key="1002", sent="2026-10-02 20:47", frm="kh", mailer="iphone", covers=["2026-10-02"],
         subject="MIA EOD fri",
         body="""13.9k vs 14.8. 12 trx which is good for us. nova black x3, tees, sweatshirts

lost fiammetta black 0 and alpina black 39

aurea 1 back for quality (stitching on the pocket). nova 4 change of mind

Sent from my iPhone"""),

    dict(key="1002dup", sent="2026-10-02 20:48", frm="kh", mailer="iphone", suffix="_dup", covers=[],
         subject="MIA EOD fri",
         body="""13.9k vs 14.8. 12 trx which is good for us. nova black x3, tees, sweatshirts

lost fiammetta black 0 and alpina black 39

aurea 1 back for quality (stitching on the pocket). nova 4 change of mind

Sent from my iPhone"""),

    dict(key="1003", sent="2026-10-03 21:10", frm="dr", covers=["2026-10-03"],
         subject="Miami closing Sat 10/3",
         body=f"""Hi all,

$5.1K vs $21.8K plan. Saturday with 100 people in the store and 6 tickets. Vlogo Cardigan navy x3 and beanies.

I don't know what to say, people come in, touch everything, say "it's too hot for this" and leave. We have 60+ down jackets on the floor and the tees are almost finished in M and L. Please look at the October allocation for Miami.

Dani

{SIG_DR}"""),

    dict(key="1004", sent="2026-10-04 18:52", frm="vs", covers=["2026-10-04"],
         attach=[{"name": "MIA01_closing_1004.csv", "text": "store,date,net_sales,plan,trx,units,traffic,notes\nMIA01,10/04/2026,11105,15600,7,11,87,delivery 103 units\n"}],
         subject="closing 10/4",
         body="""see attached

Vale"""),

    dict(key="1004re1", sent="2026-10-04 19:30", frm="lm", reply_to="1004", suffix="_re1", covers=[],
         to=["Valentina Soto <valentina.soto@valentino-retail.example>"], cc=[DR],
         subject="RE: closing 10/4",
         body="""Hi Vale, thanks! I can't open attachments on my phone, can you paste the numbers in the body next time? And anything you missed today?

Lauren

Sent from my iPhone"""),

    dict(key="1004re2", sent="2026-10-04 19:58", frm="vs", reply_to="1004re1", suffix="_re2", covers=[],
         to=[LM], cc=[DR],
         subject="RE: closing 10/4",
         body="""Hi Lauren, sorry!!

- Sales 11.1K vs plan 15.6K
- 7 transactions, 11 units
- tees navy x2, beanies, caps
- delivery 103 units, no problems
- nothing missed today, nobody asked for anything we don't have

Vale

-----Original Message-----
From: Lauren Mitchell
Sent: Sunday, October 4, 2026 7:30 PM
Subject: RE: closing 10/4

Hi Vale, thanks! I can't open attachments on my phone"""),

    dict(key="1005", sent="2026-10-05 20:37", frm="kh", mailer="iphone", covers=["2026-10-05"],
         subject="eod 10/5",
         body="""5.5k vs 11.4. 3 trx

guy asked astra cape black in XXL (lol he was huge, it wouldnt fit him anyway its tiny) and mistral black 4

Sent from my iPhone"""),

    dict(key="1006", sent="2026-10-06 20:49", frm="dr", covers=["2026-10-06"],
         subject="Miami closing 10/6",
         body=f"""$5.4K vs $11.2K. 3 tickets (Aurea black, Liviana navy, belt bag + turtleneck).

Hoodie grey XS asked.

Quiet Tuesday. The king tides start this week, Biscayne was flooded at 9am.

Dani"""),

    dict(key="1007", sent="2026-10-07 20:42", frm="dr", covers=["2026-10-07"],
         subject="Miami closing 10/7",
         body=f"""Hola,

$13.7K vs $11.9K ✔️ 8 tickets. Nova black x3 (2 to a Mexican couple going to Vail), pink beanies x2, Mistral navy x2.

Mistral navy now out in 3.

Dani

{SIG_DR}"""),

    dict(key="1008", sent="2026-10-08 20:58", frm="dr", covers=["2026-10-08"],
         subject="Miami closing 10/8",
         body=f"""Hi all,

$19.5K vs $14.0K plan. 9 tickets. Cosimo black x2, Aurea cream x2.

Missed today:
- Cosimo black 7 (we only have up to 6)
- cable knit beige XL
- cashmere turtleneck navy L
- crewneck white XXL

Big guys today haha. Also Aurea cream 0 and 3 are out now.

Dani

{SIG_DR}"""),

    dict(key="1008wrong", sent="2026-10-08 21:14", frm="dr", covers=[],
         subject="Schedule week of 10/12",
         body="""Hi team,

Schedule for next week:
Mon 10/12 - Kevin open/close, Vale 12-8
Tue - Dani 11-8, Kevin 11-8
Wed - Dani, Vale
Thu - Dani, Kevin, Vale (VM change, come 10am pls)
Fri - Dani, Kevin
Sat - Kevin, Vale, Dani 2-8
Sun - Vale close, Kevin

Basel clienteling list due Friday, please add your clients.

Dani"""),

    dict(key="1008oops", sent="2026-10-08 21:19", frm="dr", covers=[],
         subject="RE: Schedule week of 10/12",
         reply_to="1008wrong",
         body="""Sorry, please ignore, wrong list 🙈

Dani

Sent from my iPhone""", mailer="iphone"),

    dict(key="1009", sent="2026-10-09 20:51", frm="dr", covers=["2026-10-09"],
         subject="Miami closing 10/9",
         body=f"""$7.0K vs $16.2K. 6 tickets.

Lost: Fiammetta navy 0, vlogo cardigan navy L.

Iridia 1 returned, she changed her mind, she says she saw the pink one on TikTok and now she wants that one. We never got pink here?

Dani

{SIG_DR}"""),

    dict(key="1010", sent="2026-10-10 21:16", frm="kh", mailer="iphone", covers=["2026-10-10"],
         subject="MIA EOD sat",
         body="""28.0k vs 21.6 plan 🏈💪 13 trx. artem black x2 to a mexican client going to toronto (sized down per the memo, fit perfect). tees, mistral navy x2, 1 astra balaclava

LOTS missed today:
cosimo black 1
logo cardi navy M, L and XL (all 3!! we literally have only S)
padded cardi black L
turtleneck black L

ettore 7 back for quality

Sent from my iPhone"""),

    dict(key="1010corr", sent="2026-10-11 11:02", frm="dr", reply_to="1010", suffix="_corr", covers=[],
         subject="RE: MIA EOD sat",
         body=f"""Correction for yesterday: sales were $20.8K, not 28.0. Kevin flipped the numbers. Slightly under plan ($21.6K).

Dani

{SIG_DR}"""),

    dict(key="1011", sent="2026-10-11 18:47", frm="vs", covers=["2026-10-11"],
         subject="closing miami sun 10/11",
         body="""Hi everyone,

- Sales 12.7K / plan 16.0K
- 11 transactions!
- caps black x3, hoodies black x3
- asked: Aurea black 1, Camilla cream 2
- delivery 62 pcs, but where are the tees? only outerwear and 2 boxes of beanies

Vale"""),

    dict(key="1012", sent="2026-10-12 20:31", frm="kh", mailer="iphone", covers=["2026-10-12"],
         subject="eod",
         body="""7.2k vs 12.4. 5 trx. columbus day nobody cared. korean couple bought vel navy

lost riviera olive 2

Sent from my iPhone"""),

    dict(key="1013", sent="2026-10-13 21:08", frm="dr", covers=["2026-10-13"], cc=[LM, MERCH],
         subject="Miami closing 10/13 + assortment",
         body=f"""Hi all,

$11.0K vs $12.2K. 8 tickets. Caps, sweatshirts, Nova olive. Vlogo Cardigan navy M asked again (4th time in a week).

Copying merch because I need to say it: in Miami we are selling caps, tees, hoodies, sneakers, cardigans and the occasional jacket for a trip. October so far we are around 40% under plan and almost all the gap is outerwear. Meanwhile the last 2 deliveries were 80% down jackets and zero logo tees in M/L. We are missing sales every day in knitwear and jersey sizes (vlogo cardigan navy M/L/XL, turtleneck black L, padded cardigan L, cable knit). Can we please rebalance? Even 20 tees and 10 logo cardigans would make a difference.

It's 89 degrees today. Nobody in Miami needs a Liviana in October 😅

Gracias,
Dani

{SIG_DR}"""),

    # 10/14 no own email (covered in 1015)

    dict(key="1015", sent="2026-10-15 21:01", frm="dr", covers=["2026-10-14", "2026-10-15"],
         subject="Miami closing 10/14 + 10/15",
         body=f"""Hi all, I didn't send last night, sorry, VM change took until 9pm.

Wed 10/14: $5.7K vs $13.2K, 5 tickets.
Thu 10/15: $7.6K vs $15.1K, 5 tickets. Lost Nova navy 1 and hoodie grey M.

New windows are up (FW26 with the campaign images) and they look beautiful.

Dani

{SIG_DR}"""),

    dict(key="1016", sent="2026-10-16 20:56", frm="dr", covers=["2026-10-16"],
         subject="Miami closing 10/16",
         body=f"""$7.6K vs $16.9K. 4 tickets, 2 of them Iridia black to the same girl (sizes 1 and 2, she will return one I'm sure).

Returns: Riviera 3 (colour) and Artem 4, too big. He took nothing in exchange because we don't have a 3.

Dani"""),

    dict(key="1017", sent="2026-10-17 21:18", frm="dr", covers=["2026-10-17"],
         subject="Miami closing Sat 10/17",
         body=f"""Hola team,

$19.6K vs $24.9K. 13 tickets. Beanies, Aurea navy x2, tees. A group of Chinese students in the afternoon.

Missed vlogo cardigan navy M (yes again) and hoodie grey M.

Dani

{SIG_DR}"""),

    dict(key="1018", sent="2026-10-18 18:56", frm="kh", mailer="iphone", covers=["2026-10-18"],
         subject="MIA sunday",
         body="""8.4k vs 16.3. 5 trx, nova black x2

lost mistral navy 1 and vel cream 5

delivery 88 pcs, some tees finally 🙌

Sent from my iPhone"""),

    dict(key="1019", sent="2026-10-19 20:39", frm="kh", mailer="iphone", covers=["2026-10-19"],
         subject="eod mon",
         body="""14k vs 12.7 ✅ tees black x3 already selling from the new delivery. aurea black 1 asked, out

Sent from my iPhone"""),

    dict(key="1020", sent="2026-10-20 20:44", frm="dr", covers=["2026-10-20"],
         subject="Miami closing 10/20",
         body=f"""$7.1K vs $12.4K. 5 tickets. Gloves (!), tee, hoodie, Nova black.

Aurea black now out in 0, 1 and 2. A Brazilian lady and a British lady looked for it.

Dani"""),

    dict(key="1021", sent="2026-10-21 21:03", frm="dr", covers=["2026-10-21"],
         subject="Miami closing 10/21",
         body=f"""Hi all,

$6.2K vs $13.6K. 5 tickets. Vel off-white x2.

Missed:
Aurea navy 4
logo tee navy M
women's Vtrack cream 37 and 39 (same client, for her and her daughter)

Nova 4 returned, changed her mind.

Basel is in 6 weeks, we need to start thinking about the allocation for December. Will send a separate email.

Dani

{SIG_DR}"""),
]
