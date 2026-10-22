# LON01 - London New Bond Street flagship. Writers: Olivia Hartley (SM, tidy British, KPI block),
# Daniel Okafor (AM, telegraphic, lowercase, iPhone), Harriet Lowe (senior SA / clienteling, chatty, Sundays).
from ._common import E, DOM

TZ = "Europe/London"
TO = [f"retail-ops-uk@{DOM}"]
CC = [f"fiona.mcleod@{DOM}"]
CC_MERCH = [f"fiona.mcleod@{DOM}", f"merch-planning@{DOM}"]

PEOPLE = {
    "oh": ("Olivia Hartley", f"olivia.hartley@{DOM}",
           "Olivia Hartley\nStore Manager | Moncler London New Bond Street\nT +44 20 7946 0412"),
    "do": ("Daniel Okafor", f"daniel.okafor@{DOM}", ""),
    "hl": ("Harriet Lowe", f"harriet.lowe@{DOM}", ""),
    "box": ("Moncler New Bond Street", f"lon01.store@{DOM}", ""),
    "fm": ("Fiona McLeod", f"fiona.mcleod@{DOM}",
           "Fiona McLeod\nArea Manager UK, Benelux & Nordics"),
    "mp": ("Tom Brennan", f"tom.brennan@{DOM}", "Tom Brennan\nMerchandise Planning - Northern Europe"),
}

DISCLAIMER = ("This e-mail and any attachments are confidential and intended solely for the addressee. "
              "If you have received it in error please notify the sender and delete it. Moncler UK Ltd, "
              "registered in England and Wales.")

# Forwarded client message body (quoted inside 1012fwd)
_CLIENT = """---------- Forwarded message ---------
From: Caroline Ashworth <c.ashworth.home@mailbox.example>
Date: Mon, 12 Oct 2026 at 14:03
Subject: Maire black - size 1
To: Olivia Hartley <olivia.hartley@moncler-retail.example>

Dear Olivia,

Lovely to see you on Thursday, thank you for a wonderful evening.

As discussed my daughter would very much like the Maire in black, size 1. She is going back to university on the 24th so if there is any way you could find one before then I would be so grateful. Happy to collect from another store if needed, or have it sent to the house.

Many thanks,
Caroline"""


EMAILS = [
E("0831", "2026-08-31 20:52", "oh", "LON01 Closing - Mon 31/08",
"""Hi all,

Bank holiday so a slow one as expected, lots of browsing and not much buying.

Sales £19.8k vs £23.6k bud (-16%)
Footfall 249 / conv 7.6% / ATV £1,042 / UPT 1.7

Bits:
- 2 clients after the Albenga rain jacket in black (1 and 2), we're out and it's end of season so not chasing
- Marin white sz 2 asked, also gone
- Delivery in this morning, 186 pcs, all checked in by 4pm, no issues
- 1 Maire return (gift, wrong size for the recipient, refunded)

Thanks,
Olivia""", disc=True),

E("0901", "2026-09-01 21:10", "oh", "LON01 Closing - Tue 01/09",
"""Hi all,

Quiet Tuesday. £16.6k vs £21.5k. Footfall 163, conv 9.2%.

Nothing major. Logo tee navy L asked for again, we have been out of it a while - is there any in the DC? It's a basic, shouldn't be missing.

TIB vest returned sz 3, client changed his mind.

Olivia""", disc=True),

E("0902", "2026-09-02 21:31", "oh", "LON01 Closing - Wed 02/09",
"""Evening all,

£24.3k vs £23.9k, just over budget. Footfall 235, conv 8.1%.
Hoodies doing the work today, 4 black logo hoodies + 3 navy cardigans. Maya navy x3 as well.

Missed sales: Maire beige 2 and TIB black 6.

O.""", disc=True),

E("0903", "2026-09-03 22:04", "do", "close thu",
"""olivia off today so me

- 20.4k vs 33.7 bud, not great
- footfall ok (261) but conv only 4.6%
- loads of americans + chinese in, the usual VAT refund chat. 2 US ladies walked out when told no tax free, said they'll buy it in Paris next week. this happens every day honestly
- maire beige 2 asked twice, bady pink 1 once
- 1 trailgrip back, size

D""", ip=True),

E("0904", "2026-09-04 21:18", "oh", "LON01 Closing - Fri 04/09",
"""Hi all,

Much better day. £46.5k vs £39.7k (+17%). Footfall 349, conv 9.5%, ATV £1,409.

Maya was the hero - 6 black and 4 navy. That leaves us very thin, I think we only have one or two black left in the big sizes. Can someone in planning check if there's a top-up coming next week?

Second delivery of the week arrived (103 pcs), mostly knitwear and accessories.

Thanks
Olivia""", disc=True, cc=CC_MERCH),

E("0905", "2026-09-05 21:47", "do", "LON01 close sat 05/09",
"""- 53.8k vs 55k (-2%)
- 438 through the door, 27 trans
- trailgrip gtx black x6, turtleneck black x5, maire black x4, montcla black x4
- saudi families in the afternoon, 2 big tickets
- MAYA BLACK SZ 4 AND NAVY 3 NOW ZERO. had to turn away at least 2 for the black. pls chase

D""", ip=True),

E("0907", "2026-09-07 21:02", "oh", "LON01 Closing - Mon 07/09 (+Sunday)",
"""Hi all,

Apologies, no closing went out yesterday - Sunday team forgot and I was off. Sunday was £28.3k vs £37.6k, they said it was quiet after 3pm.

Today: £22.2k vs £28.8k (-23%). Footfall 247, conv only 6%.

- One Maya in olive sz 2 requested, we don't have olive at all in this store
- Bady returned sz 3 - quality, small mark on the sleeve, sent back to RTV
- Big delivery today, 201 pcs. Did get 4 Maya black, thank you whoever pushed that

Olivia""", disc=True),

E("0908", "2026-09-08 21:15", "oh", "LON01 Closing - Tue 08/09",
"""Hi all,

£23.3k vs £29.8k. Footfall 243 / conv 7.8%.

T-shirts selling better than you'd think for September, 5 logo tees today (3 black, 2 navy).
Chambre off-white 00 asked - lady wanted it for her daughter, nothing in 00.
Trailgrip W black 39 also asked, gone.

Montcla sz 6 came back - client said it's too big. Exchanged? No, he took a refund, didn't want to wait for a 5.

Olivia""", disc=True),

E("0909", "2026-09-09 21:26", "oh", "LON01 Closing - Wed 09/09",
"""Evening,

Good one: £36.9k vs £33.4k (+10%). Footfall 321, 25 transactions.
Sweatshirts x4, Trailgrip GTX x3, and two pink logo beanies (first pink sold in a while!).

Returns: 1 cardigan XL, 1 cap (colour).

O""", disc=True),

E("0910", "2026-09-10 21:58", "do", "close thurs 10/9",
"""- 45.8k vs bud 36.4 (+26%)
- conv 8.7, footfall 321
- hoodie black x4, tee black x4, cap x3
- couple of nigerian clients, one bought 9 pieces for the family
- logo tee black S zero now
- maya navy 5 zero

fyi arneb: 2 guys tried it on in their usual size and it was huge on both. sold one a size down. think we need to tell the team to go one down by default, the sz 3 on sunday came back for the same reason

d""", ip=True),

E("0911", "2026-09-11 21:20", "oh", "LON01 Closing - Fri 11/09",
"""Hi all,

Strong Friday. £56.4k vs £44.7k (+26%). Footfall 375, conv 8.8%, ATV £1,709.

Saudi clients about 15% of sales today, one family spent ~£9k between Peyre and cardigans. Peyre black x5 which is unusual this early.

Returns:
- Maya 3 - quality (stitching on the pocket). Photos to RTV.
- 2 hoodies XS (gift + changed mind)

Delivery: 122 pcs, fine.

Also agree with Daniel on Arneb - we've briefed the team this morning, size down.

Olivia""", disc=True),

E("0912", "2026-09-12 22:11", "do", "LON01 close sat 12/9",
"""54.5k vs 61.2 (-11%)
466 ftfl / 37 trans
tricot cardigan navy x4, trailgrip w x4, crew white x4

- maire off white 4 asked, none
- a girl asked for ilvaro pink in sz 1, we only have black + off white out on the floor

thats it, knackered""", ip=True),

E("0913", "2026-09-13 19:40", "hl", "Sunday closing NBS",
"""Hi everyone!

Harriet here closing today :)

We did £43.8k against £41k so a nice +7%. Ilvaro black was the star, 5 sold!! It looks amazing on.

Logo tee black in S - we had 3 people ask and we have NONE. Also navy M missing. Maire off-white 4 and navy 4 asked by the same lady. Insolux 40 asked.

2 Maya returns (4 and 5), both changed mind.

Have a lovely evening
Harriet x"""),

E("0914", "2026-09-14 21:05", "oh", "LON01 Closing - Mon 14/09",
"""Hi all,

£26.5k vs £31.4k (-16%). Footfall 234, conv 7.3%.

Delivery of 260 pcs today which took most of the afternoon - still had about 40 units in the back at close, will finish tomorrow morning.

3 returns: Bady 00 (changed mind), hoodie L (quality - small pull), scarf (gift).

Can someone confirm the campaign go-live is still tomorrow? We have nothing from marketing on the windows.

Olivia""", disc=True),

E("0915", "2026-09-15 21:33", "oh", "LON01 Closing - Tue 15/09",
"""Hi all,

Tough one. £18.7k vs £32.4k (-42%). Footfall 229, conv 7%.

Campaign went live today - we've seen the bus sides on Oxford Street and the screen at Piccadilly. No impact in store today obviously, a couple of the team saw it on Instagram. Let's see over the next weeks.

Returns: Bady 1, Montgenevre 5 (both changed mind), hoodie M size.

Olivia""", disc=True),

E("0916", "2026-09-16 21:12", "oh", "LON01 Closing - Wed 16/09",
"""Evening all,

£33.5k vs £36.5k (-8%). 346 footfall.

Maire black x4, cable knit off-white x4, tech gloves x3 - first gloves of the season.
One Bady powder pink sz 0 requested, none.

Olivia""", disc=True),

E("0917", "2026-09-17 22:20", "do", "close 17/9",
"""33k vs 40.4. meh
trailgrip gtx black x7 (!!) and now 44 is gone. size 44 is the one we always run out of, can we get an extra run of 44/45 for the store pls
tib black x4
2 returns ecrins + hoodie
chambre 00 asked again
d""", ip=True),

E("0918", "2026-09-18 21:24", "oh", "LON01 Closing - Fri 18/09",
"""Hi all,

£33.7k vs £47.8k (-30%). Footfall 370 so people are in, conversion is the problem (7.3%). Lots of tourists browsing and asking about VAT refund - we explain the scheme was scrapped in 2021 and you can see them doing the maths on their phones. Some Saudi clients said straight out they will buy in Paris.

Delivery 138 pcs.

Olivia""", disc=True),

E("0919", "2026-09-19 22:37", "do", "LON01 close sat 19/09",
"""- 83.7k vs 65.3 bud!! +28%
- 634 through the door, 49 trans
- montcla black x7, logo cardigan navy x6 + black x6
- montcla black 5 now zero after the 7
- 2 people came in with the campaign pic on their phone asking for "the one from the advert" (montgenevre navy), sold 4 of those
- crew grey S asked

great team effort today

d""", ip=True),

E("0920", "2026-09-20 19:55", "hl", "Sunday close",
"""Hi all

£46.7k vs £47.1k, so pretty much on budget!

Maire black x4 and Karakorum black x3. 2 pink beanies again - pink is a thing with the young girls.

TIB navy 4 asked, didn't have it. Tricot cardigan black M sold out.

Bady sz 2 returned, too small.

Harriet"""),

E("0921", "2026-09-21 21:08", "oh", "LON01 Closing - Mon 21/09",
"""Hi all,

£26.9k vs £37.9k (-29%). Footfall 341 conv 4.7% - very low, lots of browsers.

Delivery 247 pcs.

Bady powder pink 2 requested. Indian family in at lunch, bought Bady off-white and an Ecrins.

Fiona - I'm off Thursday, Daniel in charge.

Olivia""", disc=True),

E("0921ooo", "2026-09-21 21:08", "fm", "Automatic reply: LON01 Closing - Mon 21/09",
"""I am out of the office until Monday 28th September with limited access to email.

For urgent store matters please contact retail-ops-uk@moncler-retail.example or call the ops line.

Kind regards,
Fiona""", to=[f"olivia.hartley@{DOM}"], cc=[], sig=False, suffix="_ooo",
headers={"Auto-Submitted": "auto-replied", "X-Auto-Response-Suppress": "All"}),

E("0922", "2026-09-22 21:19", "oh", "LON01 Closing - Tue 22/09",
"""Hi all,

£28.9k vs £34.0k. 303 / 24 trans.

Cable knit black XXL asked - we never get XXL in women's knit, worth flagging.
3 returns (Chambre, Peyre size, crew quality).

Olivia""", disc=True),

E("0923", "2026-09-23 21:41", "oh", "LON01 Closing - Wed 23/09",
"""Hi all,

Bang on budget, £39.8k. Conv 10.2% which is the best weekday in a while.

Maya black x4, turtleneck x3, Hermine off-white x3.
Karakorum black 7 asked (big chap, we don't do 7 in Karakorum here).
Ecrins black 5 sold out.

Polaris goes live tomorrow - VM team came in this afternoon to set the first floor table.

Olivia""", disc=True),

E("0924", "2026-09-24 22:09", "do", "close thu 24/9",
"""58.1k vs 44.3 (+31%) good day
trailgrip gtx black x7 again lol
polaris launch: lots of interest, lots of try ons, ZERO sold. cape comes up really small, the 2.9k price makes people laugh tbh. 1 VIC said "it's a lot of money for a blanket". will keep pushing
karakorum black 5, ecrins 5, tib black 5 all zero now
2 returns maya (quality) + crew
d""", ip=True),

E("0925", "2026-09-25 21:15", "oh", "LON01 Closing - Fri 25/09",
"""Hi all,

£45.5k vs £53.8k. Footfall 556 (!) but conv just 4.9%.

Ilvaro black x5, crews x4, tech gloves x3.
Polaris - still nothing through the till. Several try-ons, feedback is fit runs small and price.

Delivery 141 pcs.

Olivia""", disc=True),

E("0925c", "2026-09-25 21:29", "oh", "RE: LON01 Closing - Fri 25/09",
"""Sorry - typo, sales were £54.5k not 45.5k, so +1% vs budget. Long day.

O""", re="0925", quote="outlook", disc=True, suffix="_re1"),

E("0926", "2026-09-26 22:48", "do", "LON01 close sat 26/9",
"""- 93.1k vs 79.3 (+18%), best day of the season so far
- footfall 696, 59 trans
- cardigan black x5, maya black x5
- bady off white 0 asked 3 times, we have nothing in 0
- turtleneck in the brown XL asked, also cable knit off white M
- cards declined x2 on big tickets (bank fraud check) - both came back and paid
- chinese tour group around 4pm

D""", ip=True),

E("0927", "2026-09-27 19:31", "hl", "Sunday closing 27th",
"""Hiya,

£52.6k vs £58.3k today.

Logo tee black x6 (!), belt bags x4, pink beanies x4 again!!

Asked for and didn't have:
cable knit off-white M x2
Ilvaro powder pink 1 (a Chinese student, showed me a picture)
Chambre off-white 2
turtleneck brown XL
logo tee navy S

Returns Maire 2 + hoodie M (both size) + 1 scarf

Harriet x"""),

E("0928", "2026-09-28 21:22", "oh", "LON01 Closing - Mon 28/09",
"""Hi all,

£50.4k vs £43.7k (+15%). Footfall 359, conv 8.4%.

Maya navy x5, cardigan black x4.

IMPORTANT - TIB vest: 3 returned today with the same problem, the zip pull comes off the slider. Sizes 3, 6, 6. A fourth (sz 7) came back as quality but I think it's the same thing. All bought in the last 4-6 weeks. Can someone in quality/product let us know if it's a known batch issue? I have pulled the TIB stock to the back to check the zips before we sell any more.

Big delivery: 293 pcs.

Olivia""", disc=True),

E("0928fm", "2026-09-29 08:47", "fm", "RE: LON01 Closing - Mon 28/09",
"""Morning Olivia

Thanks for flagging the TIB. Can you send me style/colour/size and the purchase dates for each one? Quality team are asking stores. Paris mentioned something similar last week.

Also - welcome back to me, catching up on emails!!

F""", re="0928", quote="outlook", to=[f"olivia.hartley@{DOM}"], cc=[f"daniel.okafor@{DOM}"], suffix="_re1", disc=True),

E("0930", "2026-09-30 21:40", "oh", "LON01 Closing - Tue 29 + Wed 30/09",
"""Hi all,

Missed yesterday, sorry - we had a stock count running late and I left without sending.

Tue 29: £27.7k vs £38.8k
Wed 30: £39.6k vs £44.9k (-12%), footfall 376, 32 trans

TIB again: 3 more back Tuesday and 3 Wednesday, all zip slider. That's 10 since Monday. Fiona I've sent you the list separately. Checked the stock in the back - 4 out of 11 have a loose slider. I've taken those off sale.

Ilvaro powder pink 00 asked today, Chinese client. Maya olive asked again (sz 3).

Olivia""", disc=True),

E("1001", "2026-10-01 22:03", "do", "close 1/10",
"""- 50.5k vs 52.5 (-4%)
- hermine black x4, montcla x3, karakorum navy x3, arneb x3
- arneb: 2 back today (6 changed mind + 5 size). we're now telling everyone to go a size down
- valbourg 1 asked + trailgrip gtx 40
- 1 TIB returned, zip. i've lost count

d""", ip=True),

E("1002", "2026-10-02 21:36", "oh", "LON01 Closing - Fri 02/10",
"""Hi all,

£43.8k vs £60.4k (-28%). Footfall 527 / conv 6.3%.

Something to flag: from this morning we've had young Asian clients asking for the Ilvaro in pink - apparently a K-pop singer wore it at the Paris shows yesterday and it's all over Instagram. We had one in sz 1 asked for at the till, and a few more just looking for it on the floor. We have no pink left. Could planning check whether we'll be getting any?

Ilvaro black x4 today, I suspect related.

TIB x2 returned (zip), Ambrine 0 returned (changed mind), Maya 4 size.
Delivery 163 pcs.

Olivia""", disc=True, cc=CC_MERCH),

E("1003", "2026-10-03 22:25", "do", "LON01 close sat 3/10",
"""- 77.1k vs 86.1 (-10%)
- 696 footfall, 45 trans
- MAYA BLACK X10!! + navy x5
- maire black 4, chambre off-white 2, maya olive 5 asked
- ambrine: 3 clients today asking for the brown one. we only got black. paris/milan have it in brown? its the colour everyone wants this season
- 2 TIB back zip

d""", ip=True),

E("1003dup", "2026-10-03 22:27", "do", "LON01 close sat 3/10",
"""- 77.1k vs 86.1 (-10%)
- 696 footfall, 45 trans
- MAYA BLACK X10!! + navy x5
- maire black 4, chambre off-white 2, maya olive 5 asked
- ambrine: 3 clients today asking for the brown one. we only got black. paris/milan have it in brown? its the colour everyone wants this season
- 2 TIB back zip

d""", ip=True, suffix="_dup"),

E("1004", "2026-10-04 19:48", "hl", "Sunday close 4/10",
"""Hi all,

£41.3k today (budget 60.4k so quite a miss, sorry!). Felt busy but lots of looking.

Maire navy x4, Maya navy x3, Rosiere black x3.
Hermine off-white 3 asked.

2 returns (Valbourg 2, polo M).

Getting lots of questions about the event Thursday from clients who weren't invited - Olivia, do we have a few more spaces?

Harriet"""),

E("1005", "2026-10-05 21:30", "oh", "LON01 Closing - Mon 05/10",
"""Hi all,

£32.1k vs £43.8k (-27%). Footfall 353.

Heavy return day - 7 in total. TIB sz 7 (zip again), Arneb 4 exchanged for a 3, plus Maire, Bady (gift), Chamonix, polo, beanie.

Delivery 300 pcs, including stock for Thursday's event. All the FW26 preview pieces are in.

Client evening Thursday: 45 confirmed, Harriet has a waitlist of 8. Catering confirmed.

Olivia""", disc=True),

E("1006", "2026-10-06 21:43", "oh", "LON01 Closing - Tue 06/10",
"""Hi all,

On budget, £43.5k vs £42.9k. 425 / 38.

Beanies flying - 7 black today. Maire navy x4, crew grey x4.

8 returns (!) - mostly changed mind, 1 TIB zip, Arneb 6 colour, Montcla 3 size. Our return rate this week is awful, I'll do a breakdown for Fiona.

All set for Thursday.

Olivia""", disc=True),

E("1007", "2026-10-07 21:51", "oh", "LON01 Closing - Wed 07/10",
"""Hi all,

£58.9k vs £48.9k (+20%). Footfall 446.

Maire black x5 today and now we're out in size 1, very low in the rest. Asked for in 3 and 4 as well and couldn't find them. Planning - could we get any black Maire before tomorrow evening? I know it's a long shot.

Ilvaro pink 00 asked again. Logo tee black XXL asked.

Olivia""", disc=True, cc=CC_MERCH),

E("1008", "2026-10-09 00:41", "oh", "LON01 Closing - Thu 08/10 - CLIENT EVENING",
"""Hi all,

What a night. Thank you to the whole team, and to Fiona and the events team.

Sales £252.5k inc VAT vs £58.3k budget. Footfall 671 (door counter includes event guests), 130 transactions, 231 units.

Event:
- 45 VICs confirmed, 41 came + about 20 plus-ones
- around 28 clients purchased on the night, a few big tickets over £10k
- Montcla black x15 (!), hoodies and crews x10 each, cardigans x10

Black Maire was the big miss. Sold out across 0, 1, 2 by 7.30pm and we had at least 12 more requests (lots of mums buying for daughters). I've started a waitlist, currently 9 names with sizes. Also crew grey XXL x2 and Maire beige 3.

Logo cardigan navy M also gone.

Off to bed.
Olivia

Sent from my iPhone""", sig=False),

E("1008fm", "2026-10-09 07:58", "fm", "RE: LON01 Closing - Thu 08/10 - CLIENT EVENING",
"""Olivia this is fantastic, well done everyone!!

Quick one - the flash this morning shows £210k for you, not 252. Is the 252 incl VAT? Need to use the right one for the exec note.

And can you send me the Maire waitlist with sizes, I'll push Tom in planning.

F""", re="1008", to=[f"olivia.hartley@{DOM}"], cc=[f"daniel.okafor@{DOM}", f"tom.brennan@{DOM}"], suffix="_re1"),

E("1008re", "2026-10-09 10:22", "do", "RE: LON01 Closing - Thu 08/10 - CLIENT EVENING",
"""Hi Fiona, Olivia's in at 12 so answering for her.

Yes 252 is gross incl VAT, net is 210.4k so use the flash.

Maire black waitlist so far (has grown since last night):
size 0 - 3
size 1 - 4
size 2 - 1
size 3 - 2
size 00 - 1
size 4 - 1
= 12 names. plus about 5 walk-ins who didn't leave details

Dan""", re="1008fm", to=[f"fiona.mcleod@{DOM}"], cc=[f"olivia.hartley@{DOM}", f"tom.brennan@{DOM}"], suffix="_re2", quote="outlook"),

E("1009", "2026-10-09 22:16", "do", "close fri 9/10",
"""- 57.7k vs 64.8 bud
- hangover day lol, still decent
- hoodie black x7, insolux x4
- maire black asked AGAIN: 0 x2, 2 x2, 3, 4 - all on the waitlist now
- arneb black 5 asked (we only have 6 left - told him go down a size, didnt want to)
- delivery 109 pcs, no black maire in it
- 1 TIB zip back

d""", ip=True),

E("1010", "2026-10-10 22:40", "do", "LON01 close sat 10/10",
"""57k vs 87.8 bud -35%. ouch
712 in but 37 trans. tons of tourists, a lot of the vat conversation again
logo hoodie navy x10 tho
karakorum black 5 + cardigan black S zero now
6 returns, TIB again, hermine quality (feather coming through), cap quality, rest size
d""", ip=True),

E("1011", "2026-10-11 19:52", "hl", "Sunday 11/10",
"""Hi all,

£62.0k vs £65.5k.

Black Maire - I had 7 people ask today, sizes 0 (x3), 2 (x2), 1, 3. I've added the ones who left numbers to Dan's waitlist. People are coming in specifically for it, one lady came from Kent!

Also asked: Arneb 5, Peyre red 3, cable knit beige XS, hoodie XXL.

Returns: 2 Maire (quality + size), Bady 1, Montcla 1.

Harriet x"""),

E("1012", "2026-10-12 21:19", "oh", "LON01 Closing - Mon 12/10",
"""Hi all,

£27.9k vs £47.9k (-42%). Footfall 284. Very quiet Monday.

Big delivery 524 pcs - mostly heavy outerwear. No black Maire in it. Tom, any update?

Forwarding a client message separately for the waitlist.

Olivia""", disc=True, cc=CC_MERCH),

E("1012fwd", "2026-10-12 21:24", "oh", "FW: Maire black - size 1",
"""Tom, Fiona - one of our top clients, see below. She's spent over £40k with us this year. Anything you can do from another store or the DC would be great.

Olivia""", re=None, cc=[f"fiona.mcleod@{DOM}"], to=[f"tom.brennan@{DOM}"], suffix="_fwd", disc=True,
tail=_CLIENT),

E("1013", "2026-10-13 21:28", "oh", "LON01 Closing - Tue 13/10",
"""Hi all,

£48.5k vs £49.3k. 362 / 29.

Proper cold this morning (6 degrees on the way in!) and you could feel it - more people heading straight for outerwear. Hoodies and Maya black x3 each, Peyre red x2.

Logo hoodie navy M now zero, tee black S still zero.

Olivia""", disc=True),

E("1014", "2026-10-14 21:37", "oh", "LON01 Closing - Wed 14/10",
"""Hi all,

£80.3k vs £53.5k (+50%). Footfall 539, conv 8.7%.

Coat weather has arrived. Montcla black x6, Insolux x5, tech gloves x4, Maire off-white x4. People buying full looks.

Still turning away black Maire every day - today 0 x2, 00, 4. Hoodie navy M asked.

Olivia""", disc=True),

E("1015", "2026-10-15 22:12", "do", "close 14/10",
"""- 71.7k vs 58.5 (+23%)
- maire navy x7 and maya navy x6. selling navy maire to some of the black maire waitlist ladies, not all want it
- karakorum black x5
- maire black 1 + 2 asked, valbourg 4, hoodie navy M
- polaris oversized L returned, changed mind. still only sold a handful of polaris total since launch
- 2 TIB zip

d""", ip=True),

E("1016", "2026-10-16 21:25", "oh", "LON01 Closing - Fri 16/10",
"""Hi all,

£65.5k vs £73.0k (-10%). Footfall 523.

Ecrins black x6, Hermine black x4.

Delivery 111 pcs. I was told the DC would have black Maire again from today - nothing in our delivery. Please can someone confirm when we get our share, we have 14 names on the list now and they're ringing every day.

Maire black 00 and 2 asked again, cardigan navy M.

Olivia""", disc=True, cc=CC_MERCH),

E("1016mp", "2026-10-17 09:12", "mp", "RE: LON01 Closing - Fri 16/10",
"""Hi Olivia,

Black Maire landed at the DC yesterday. Allocation is being run today, priority is going to Paris/Milan/Harrods because of the Korean demand there. I've put LON01 down for a share - should be on Monday's or Wednesday's truck. Can't promise all sizes.

Tom""", re="1016", to=[f"olivia.hartley@{DOM}"], cc=[f"fiona.mcleod@{DOM}"], suffix="_re1", quote="outlook"),

E("1017", "2026-10-17 23:02", "do", "LON01 close sat 17/10 BIG ONE",
"""- 113.5k vs 104 bud (+9%)
- 982 footfall!!! door counter might be double counting the queue tho
- 69 trans, 119 units
- montgenevre black x6, cardigan black x6, ecrins black x5, peyre black x4
- cold + chucking it down all day and still madness. queue to the fitting rooms all afternoon
- 1 maire black 2 asked (the rest have given up asking lol)
- karakorum black 5 still zero

d""", ip=True),

E("1018", "2026-10-18 20:06", "hl", "Sunday close - wow",
"""Hi all!!

£104.3k today against £66.3k budget, best Sunday I've ever had here!

Ilvaro black x9, Maya black x8, turtleneck x5, Maire off-white x5. So cold outside, everyone wanted to wear it out of the store.

Missed: Hermine black 4, Maya olive 6, tricot cardigan grey M, Insolux 35 and 37. Cardigan black M now out too.

5 returns, 1 TIB with the zip.

Harriet x"""),

E("1019", "2026-10-19 21:14", "oh", "LON01 Closing - Mon 19/10",
"""Hi all,

£53.3k vs £52.3k. Footfall 396.

Delivery 408 pcs today - Tom, no black Maire in this one either. One client today for sz 3 and of course the list.

Bady black x3, Arneb x3 (sizing down works!), Ecrins x3.

Olivia""", disc=True),

E("1020", "2026-10-20 21:31", "oh", "LON01 Closing - Tue 20/10",
"""Hi all,

£35.6k vs £51.4k (-31%). Milder again today and it showed, footfall down to 354.

Montcla black x4, scarves x3.

Missed: Maire black 0, Peyre black 4, Chamonix XS, crew grey S, tee black S.

3 returns (Maire size, Montcla gift, hoodie colour).

Olivia""", disc=True),

E("1021", "2026-10-21 21:22", "oh", "LON01 Closing - Wed 21/10",
"""Hi all,

£42.0k vs £58.8k. Footfall 398 / 26 trans.

Brown turtleneck x4 - the chocolate is clearly the colour this year, people keep asking whether we'll get the Ambrine in brown.

Ilvaro black 00 now sold out, asked once. Cardigan navy M again (that's a week now). Black Maire 3.

Olivia""", disc=True),
]

