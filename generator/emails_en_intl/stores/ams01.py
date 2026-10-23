# AMS01 - Amsterdam P.C. Hooftstraat. Writers: Sanne de Vries (SM, Dutch-English, euro with dot thousands
# "EUR 8.512"), Ruben Bakker (AM, lowercase, "ff", "top", Dutch words), Lotte Jansen (SA, emoji, some Sundays).
from ._common import E, DOM

TZ = "Europe/Amsterdam"
TO = [f"retail-ops-benelux@{DOM}"]
CC = [f"fiona.mcleod@{DOM}"]

PEOPLE = {
    "sv": ("Sanne de Vries", f"sanne.devries@{DOM}",
           "Met vriendelijke groet / Kind regards,\nSanne de Vries\nStore Manager Valentino Amsterdam\nP.C. Hooftstraat"),
    "rb": ("Ruben Bakker", f"ruben.bakker@{DOM}", ""),
    "lj": ("Lotte Jansen", f"lotte.jansen@{DOM}", ""),
    "box": ("Valentino Amsterdam PC Hooft", f"ams01.store@{DOM}", ""),
    "fm": ("Fiona McLeod", f"fiona.mcleod@{DOM}", "Fiona McLeod\nArea Manager UK, Benelux & Nordics"),
}
DISCLAIMER = ""

EMAILS = [
E("0831", "2026-08-31 18:52", "sv", "Closing AMS 31-08",
"""Hoi all,

Omzet EUR 8.465 vs budget 8.800. Almost there.
46 visitors, 6 tickets. Mostly Dutch clients, some English.

Vlogo Padded Cardigan black 2x, rest single pieces.
Vtrack Gtx 43 returned, too small, client will come back for a 44 but we don't have 42 anymore in black so I hope 44 is ok.

Groetjes,
Sanne""", sig=False),

E("0901", "2026-09-01 18:47", "sv", "Closing AMS 01-09",
"""Hoi,

Bad day, EUR 4.590 vs 9.100 budget. 54 visitors and only 5 tickets.
A German couple was asking for Monteluce navy in 3 and a man for VEL black 6, we don't have both.

It's still 21 degrees here, nobody thinks about jackets yet.

Groetjes, Sanne""", sig=False),

E("0902", "2026-09-02 18:58", "sv", "Closing AMS 02-09",
"""Hoi all,

EUR 5.790 / budget 9.700. Not good.
Hoodies navy + black 2x each, white t-shirts 2x. Hoodie navy S is finished.
Fiammetta 0 came back, client wanted it in navy and we only had black.

Sanne""", sig=False),

E("0903", "2026-09-03 19:10", "rb", "closing 3/9",
"""hi all

15,5k vs 13,5k budget, nice
artem black 2x already, first week. turtleneck black 2x
delivery 91 pcs in, all ok
nova 4 returned quality (seam open under the arm), send back to dc

ruben"""),

E("0904", "2026-09-04 18:49", "sv", "Closing AMS 04-09",
"""Hoi,

EUR 11.700 vs 16.200. 90 visitors, 7 tickets so conversion was low today, many tourists only looking.
Liviana black 4 asked, we don't have.
Vlogo T-Shirt navy S is finished.

Groetjes,
Sanne""", sig=False),

E("0905", "2026-09-05 19:25", "rb", "closing za 5/9",
"""hi

slecht.. 8,7k vs 22,5k budget. 137 people in the shop so the traffic was there but nobody buys, sunny and everybody on the terrace
vel black 3x, now no more black in 5
vtrack w black 36 asked
tricot cardigan L back for quality (button)

ruben"""),

E("0906", "2026-09-06 18:31", "lj", "Sunday closing ☀️",
"""Hi everyone!

Super nice Sunday 😊 EUR 23.000 vs 15.500 budget!!
Cable knit black 3x, caps, tricot cardigan, 2 Nova black.
Lots of Dutch families, very gezellig in the shop.

Lotte"""),

E("0908", "2026-09-08 18:55", "sv", "Closing AMS 08-09",
"""Hoi all,

Yesterday I forgot to send, sorry. Monday was very quiet, EUR 4.2 only.

Today EUR 10.300 vs 11.900. 65 visitors, 8 tickets.
VEL black 2x.
Asked: cable knit black M, and the cashmere turtleneck in brown XL (a nice colour, we have only S and M).
Nova black 5 and Mistral black 5 are finished now.

Sanne""", sig=False),

E("0909", "2026-09-09 19:03", "sv", "Closing AMS 09-09",
"""Hoi,

EUR 10.100 vs 13.200 budget.
White t-shirts 2x.
A client asked Iridia off white size 1, and one Nova black 5 (which is finished since yesterday).
Artem 2 returned - he says it is way too big. Funny because he took his normal size.

Groetjes, Sanne""", sig=False),

E("0910", "2026-09-10 19:14", "rb", "closing 10/9",
"""top day 21,4k vs 14,3k 💪
white crews 3x, aurea black 2x
asked riviera black 2 + jersey polo black XL
delivery 110 pcs
fyi also we have 2 guys today in the artem who need a size smaller then normal. we tell everybody now to take 1 size down

ruben"""),

E("0911", "2026-09-11 18:58", "sv", "Closing AMS 11-09",
"""Hoi all,

EUR 12.500 / 17.100. Aria black 2x.
Asked: cable knit off white XXL, vlogo t-shirt white XL.

Sanne""", sig=False),

E("0912", "2026-09-12 19:31", "rb", "closing za 12-9",
"""17,7k vs 25,4k
some chinese tourists in the afternoon (19%)
tricot navy 2x
asked vel navy 7, tricot cardigan black XXL, white tee XL. big guys today haha
liviana black 0 finished

r"""),

E("0913", "2026-09-13 18:36", "lj", "Sunday closing",
"""Hi all!

EUR 18.000 vs 17.300 😊 small plus!
Hoodies black 2x, Monteluce navy 2x, cardigans navy 2x, and a pink beanie.

Nothing special. Doei!
Lotte"""),

E("0914", "2026-09-14 18:52", "sv", "Closing AMS 14-09",
"""Hoi all,

Good Monday: EUR 18.400 vs 13.200 budget. Chinese and English clients.
Vtrack Gtx black 3x, Aurea black 2x - so now Aurea black 0 is finished, we only have few pieces in bigger sizes.
Riviera black 2 asked again (second time this week).

Sanne""", sig=False),

E("0915", "2026-09-15 18:44", "sv", "Closing AMS 15-09",
"""Hoi,

EUR 6.100 vs 12.900. Very quiet, nice weather and nobody thinks about jackets.
Nova navy 5 finished.

Groetjes, Sanne""", sig=False),

E("0916", "2026-09-16 18:59", "sv", "Closing AMS 16-09",
"""Hoi all,

EUR 8.100 / 14.300.
Jersey Polo white 3x and white crews 2x - people are still buying summer things.
Asked: Aurea black 0, cable knit beige M, turtleneck brown XXL.
Fiammetta black 2 finished.
Valdora returned, client changed her mind.

Sanne""", sig=False),

E("0917", "2026-09-17 19:08", "rb", "closing 17/9",
"""9,9k vs 16,4k
vlogo cardigan black 2x
cable knit black XL asked
delivery 127 pcs, nothing special in it, mostly knit

r"""),

E("0918", "2026-09-18 18:50", "sv", "Closing AMS 18-09",
"""Hoi all,

EUR 16.000 vs 19.400.
The brown turtleneck sold 2x today. Brown is popular, maybe we can get some more sizes? We had requests for XL and XXL last weeks.

Sanne""", sig=False),

E("0919", "2026-09-19 19:22", "rb", "closing za 19-9",
"""22,8k vs 27,4k
19 bonnen, 131 bezoekers
white tees 5x!! strange because it was raining like crazy with thunder in the afternoon
asked: turtleneck brown L, white tee M, jersey polo white S
white tee M + L finished now. summer basics are going, can we get some more white tees in M/L?

ruben"""),

E("0920", "2026-09-20 18:40", "lj", "Sunday closing 20/9",
"""Hi!

EUR 22.500 vs 19.000 🎉
Jersey Polo black 2x, Iridia off white 2x (so pretty!!), turtleneck black 2x, Aurea black 2x.
Almost all Dutch clients today.

Doei,
Lotte"""),

E("0921", "2026-09-21 18:48", "sv", "Closing AMS 21-09",
"""Hoi all,

EUR 5.900 vs 13.300. 77 visitors but only 6 tickets.
Many Spanish and Italian tourists today, only looking.
Asked: Aurea black 00, crew white M, Vtrack W off white 35.
3 returns: Liviana 0 (changed mind), hoodie S (quality - print), beanie (quality).
VEL black 3 finished.

Sanne""", sig=False),

E("0922", "2026-09-22 18:46", "sv", "Closing AMS 22-09",
"""Hoi,

EUR 8.300 vs 14.700.
VEL black 3 asked, the one that finished yesterday.
Tricot cardigan XL and a t-shirt L returned.

Groetjes, Sanne""", sig=False),

E("0923", "2026-09-23 18:57", "sv", "Closing AMS 23-09",
"""Hoi all,

EUR 10.900 vs 15.800.
Asked: cable knit beige M, jersey polo white S, Vtrack Gtx black 45.
Nothing else.

Sanne""", sig=False),

E("0924", "2026-09-24 19:11", "rb", "closing 24/9",
"""17,6k vs 19,3k
nova black 3x, aurea black 2x (in 3 and 4)
2 ladies asked aurea black 0. we have 0 in black since 2 weeks
delivery 123 pcs. astra also arrived for the launch, 1 cape + 2 oversized. put it in the window
r"""),

E("0925", "2026-09-25 18:53", "sv", "Closing AMS 25-09",
"""Hoi all,

EUR 12.700 vs 23.800. Not good.
Artem black 6 asked. Aurea black 2 now also finished.

Astra: some people come in to look at it because of instagram, but nobody try it on until now.

Sanne""", sig=False),

E("0926", "2026-09-26 19:40", "rb", "closing za 26/9",
"""32,4k vs 31,2k, plusje!
sold 1 astra oversized light blue, to a guy from london. first one
aurea black 2x + beige 2x
asked aurea black 0 2x, aurea black 2, tricot black XS
aurea black now 0/1/2 all finished. when do we get new?
2 returns cardigan L size, tee quality

ruben"""),

E("0927", "2026-09-27 18:39", "lj", "Sunday closing 27-9",
"""Hi all,

EUR 23.100 vs 21.200 👍
Tricot cardigan black 2x, 1 Astra Oversized black, Piero black.
Monteluce navy 7 asked (very tall man 😅).
Jersey Polo M and Vtrack 45 returned.

Doei!
Lotte"""),

E("0928", "2026-09-28 18:51", "sv", "Closing AMS 28-09",
"""Hoi all,

EUR 15.800 vs 16.100, almost.
Aria black 2x, white beanies 2x.
Asked: Aurea black 2, Vtrack Gtx grey 46.

Sanne""", sig=False),

E("0929", "2026-09-29 19:02", "sv", "Closing AMS 29-09",
"""Hoi all,

EUR 19.400 vs 16.500, +17%.
Scarves black 3x and we sold a Astra Cape black!! So we have now 2 Astra sold.
Asked: turtleneck brown M 2x (we have it in S only now), Aurea black 0.
Tricot cardigan black S finished.

Sanne""", sig=False),

E("0930", "2026-09-30 18:55", "sv", "Closing AMS 30-09",
"""Hoi,

EUR 11.000 vs 18.900.
Tricot black XS asked. Vtrack Gtx black 43 finished.

Returns: Nova 3 (changed mind) and 2x VEL, 6 and 4, both the zipper. The slider comes loose from the zipper. Is this known? I have put them apart for the DC.

Groetjes,
Sanne""", sig=False),

E("1001", "2026-10-01 19:17", "rb", "closing 1/10",
"""22,3k vs 21,1k
crews white 3x, aria black 3x
delivery 131 pcs
again 1 vel back with the zipper, size 3. that is 3 now. 2 aurea returns also (size + changed mind)
r"""),

E("1002", "2026-10-02 18:59", "sv", "Closing AMS 02-10",
"""Hoi all,

EUR 23.800 vs 24.100, close.
1 Astra Oversized light blue sold again.
Asked: Aria black 1, VEL navy 5, turtleneck brown XS, crew white L, Vtrack W off white 41. Aria black 1 and jersey polo black S are finished.
Artem 4 returned - too big, we did exchange to 3 but he wanted refund at the end.

Sanne""", sig=False),

E("1003", "2026-10-03 19:28", "rb", "closing za 3/10",
"""32,4k vs 35,3k
valdora off white 3x - ski season ppl
asked: aurea black 4, and a chinese girl asked for the iridia in PINK size 0, showing a picture of some kpop singer. we dont have the pink here
fiammetta 1 back quality
r"""),

E("1005", "2026-10-05 18:47", "sv", "Closing AMS 05-10 + weekend",
"""Hoi all,

Sorry, Sunday we had no closing because Lotte was alone in the end and forgot. Sunday was EUR 10.100 vs 23.400, very bad, sunny and everybody was outside.

Today EUR 17.000 vs 18.100.
1 Astra Cape sold.
Asked: Aurea black 0, Vtrack Gtx grey 41.
Aria 1 returned.

Sanne""", sig=False),

E("1006", "2026-10-06 18:53", "sv", "Closing AMS 06-10",
"""Hoi all,

Good day, EUR 23.700 vs 17.500.
Hoodie black 3x.
Mistral black 7 asked (we never have 7).
Nova navy 4 finished now.

Sanne""", sig=False),

E("1007", "2026-10-07 18:41", "sv", "Closing AMS 07-10",
"""Hoi,

EUR 9.400 vs 21.300. 75 visitors, 5 tickets.
Nothing to tell, very quiet on the PC Hooft today.

Sanne""", sig=False),

E("1008", "2026-10-08 19:05", "rb", "closing 8/10",
"""14,9k vs 21,7k
tricot cardigan black 2x, fiammetta navy 2x, 1 astra oversized black
delivery 146 pcs
r"""),

E("1009", "2026-10-09 19:01", "sv", "Closing AMS 09-10",
"""Hoi all,

EUR 21.000 vs 24.900.
Vlogo Padded Cardigan 6x (4 black 2 navy), people start to layer.
Asked: Aurea black 0, Amalia brown 00 (we don't have the brown at all, only black), Vtrack W off white 39.

Weather says next week it will be really cold, 3-4 degrees and frost in the night. I think we need more heavy jackets in the shop, we are low on Nova and Mistral black. Can someone check please?

Sanne""", sig=False, cc=[f"fiona.mcleod@{DOM}", f"merch-planning@{DOM}"]),

E("1010", "2026-10-10 19:35", "rb", "closing za 10/10",
"""19,4k vs 39,0k. -50% auw
197 ppl in the shop, 12 bonnen. lot of tourists only looking
vlogo cardigan black 4x + white crew 4x
asked: vel navy 2 (2x), liviana off white 3, monteluce navy 3, crew white XL
mistral black 5 + vlogo cardigan black L finished

r"""),

E("1011", "2026-10-11 18:42", "lj", "Sunday closing 11/10",
"""Hi all,

EUR 16.000 vs 25.300 😕
Vtrack Gtx black 2x, Riviera black 2x.
Monteluce navy 5 asked.
Vtrack Gtx black 42 finished.

Lotte"""),

E("1012", "2026-10-12 18:49", "sv", "Closing AMS 12-10",
"""Hoi all,

EUR 11.600 vs 20.100.
It is getting cold, this morning 4 degrees. People come in with their hands in the pockets 😉
Asked: Aurea black 1 2x, Vtrack Gtx 42.
Liviana 0 returned, size.

Sanne""", sig=False),

E("1013", "2026-10-13 19:04", "sv", "Closing AMS 13-10",
"""Hoi all,

EUR 22.400 vs 19.400, +15%.
Liviana black 2x, Iridia black 2x, scarves 2x, black t-shirts 2x.
Lots asked today:
- Aurea black 0
- Artem navy 4
- Valdora off white 0
- hoodie navy XXL
- hoodie grey L
- Vtrack Gtx black 42
Vlogo Cardigan black S finished, t-shirt black M also.

Sanne""", sig=False),

E("1014", "2026-10-14 19:09", "rb", "closing 14/10",
"""20,8k vs 21,8k
american tourists 21%
urban backpack 2x, nova navy 2x
asked aurea beige 00 2x, artem navy 5, riviera olive 5
riviera black 3 finished
koud!! -1 this morning on the bike 🥶
r"""),

E("1015", "2026-10-15 18:56", "sv", "Closing AMS 15-10",
"""Hoi all,

EUR 12.700 vs 24.900. Strange, it is so cold and still not busy. 131 visitors but 10 tickets.
Beanies 3x. 1 Astra Oversized black.

Many asked for the Aurea black: 1 (2x), 2, 4. We have nothing in black since September. When is it coming back?
Also Fiammetta navy 0, Piero black 2, vlogo cardigan navy S.

Riviera 4 returned, quality.

Sanne""", sig=False, cc=[f"fiona.mcleod@{DOM}", f"merch-planning@{DOM}"]),

E("1015fm", "2026-10-16 08:44", "fm", "RE: Closing AMS 15-10",
"""Hi Sanne,

Planning tells me black Aurea lands at the DC today but the first allocation goes to the stores with the biggest waitlists (Paris, Milan, Harrods). Amsterdam should get some in the following delivery. Will keep you posted.

Agree on the heavy outerwear - I've asked Tom to look at a top-up of Nova/Mistral for you and Copenhagen.

F""", re="1015", to=[f"sanne.devries@{DOM}"], cc=[f"ruben.bakker@{DOM}"], suffix="_re1", quote="outlook"),

E("1015sv", "2026-10-16 09:12", "sv", "RE: Closing AMS 15-10",
"""Hi Fiona,

Thank you! Ok, we wait. Can you ask Tom ff for Piero also, we have many questions for Piero black 2.

Groetjes,
Sanne""", re="1015fm", to=[f"fiona.mcleod@{DOM}"], cc=[f"ruben.bakker@{DOM}"], suffix="_re2", sig=False, ip=True),

E("1016", "2026-10-16 18:58", "sv", "Closing AMS 16-10",
"""Hoi all,

EUR 33.200 vs 30.400, finally!
Nova black 3x, Nova navy 2x, Iridia off white 2x, Iridia black 2x.
Asked: Aurea black 2, Piero black 2 (again), vlogo cardigan black S, white tee XS.
Aria black 0 finished, Riviera black 5 also.

The delivery that should come yesterday is still not here. Transporter said tomorrow.

Sanne""", sig=False),

E("1017", "2026-10-17 19:44", "rb", "closing za 17/10",
"""42,9k vs 41,4k 🔥
tricot black 4x, nova black 3x, aria black 3x
delivery came today finally, 136 pcs, 2 days late. no aurea black in it
asked amalia brown 1
busy day, cold + ADE in town, the city is full

ruben"""),

E("1018", "2026-10-18 18:44", "lj", "Sunday closing ❄️",
"""Hi all!

EUR 37.500 vs 27.500!! Best Sunday in a long time 🎉
Artem black 2x, Liviana black 2x, hoodies 2x, belt bags 2x.
Asked: Aurea black 0, Iridia black 2, Iridia off white 0, Nova navy 2, Piero black 2.
Fiammetta black 1 finished.
Nova 3 returned.

So cold today, everybody wanted a down jacket!
Lotte"""),

E("1019", "2026-10-19 18:51", "rb", "closing 19/10",
"""22,6k vs 21,8k
beanie navy 2x, vtrack gtx 2x, amalia black 2x
r""", ip=True),

E("1019nl", "2026-10-19 18:53", "rb", "Re: closing 19/10",
"""sorry vergeten: sanne vraagt of jij morgen de sleutel hebt voor de achterdeur, ik ben er pas om 11u

doei""", re="1019", quote=None, to=[f"retail-ops-benelux@{DOM}"], cc=[f"fiona.mcleod@{DOM}"], suffix="_re1", ip=True),

E("1020", "2026-10-20 18:57", "sv", "Closing AMS 20-10",
"""Hoi all,

EUR 15.400 vs 20.300. Weather is back to normal, 10 degrees and grey. Many tourists (Spanish, Italian, French) but they only look.

Asked: Aurea black 1, Amalia brown 1 (third request for brown this month, we don't have brown in our assortment), Riviera olive 7, Valdora off white 00, white tee S, Vtrack W off white 40.

PS sorry for Ruben's message yesterday, that was meant for me 🙈

Sanne""", sig=False),

E("1021", "2026-10-21 18:50", "sv", "Closing AMS 21-10",
"""Hoi all,

EUR 16.600 vs 23.300.
Cable knit beige 2x, vlogo cardigan black 2x.
Asked: Fiammetta black 1 (2x), Aurea black 2, Iridia off white 2.

Still no Aurea black from the DC.

Sanne""", sig=False),
]
