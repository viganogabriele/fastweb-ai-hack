# AMS01 - Amsterdam P.C. Hooftstraat. Writers: Sanne de Vries (SM, Dutch-English, euro with dot thousands
# "EUR 8.512"), Ruben Bakker (AM, lowercase, "ff", "top", Dutch words), Lotte Jansen (SA, emoji, some Sundays).
from ._common import E, DOM

TZ = "Europe/Amsterdam"
TO = [f"retail-ops-benelux@{DOM}"]
CC = [f"fiona.mcleod@{DOM}"]

PEOPLE = {
    "sv": ("Sanne de Vries", f"sanne.devries@{DOM}",
           "Met vriendelijke groet / Kind regards,\nSanne de Vries\nStore Manager Moncler Amsterdam\nP.C. Hooftstraat"),
    "rb": ("Ruben Bakker", f"ruben.bakker@{DOM}", ""),
    "lj": ("Lotte Jansen", f"lotte.jansen@{DOM}", ""),
    "box": ("Moncler Amsterdam PC Hooft", f"ams01.store@{DOM}", ""),
    "fm": ("Fiona McLeod", f"fiona.mcleod@{DOM}", "Fiona McLeod\nArea Manager UK, Benelux & Nordics"),
}
DISCLAIMER = ""

EMAILS = [
E("0831", "2026-08-31 18:52", "sv", "Closing AMS 31-08",
"""Hoi all,

Omzet EUR 8.465 vs budget 8.800. Almost there.
46 visitors, 6 tickets. Mostly Dutch clients, some English.

Tricot padded cardigan black 2x, rest single pieces.
Trailgrip GTX 43 returned, too small, client will come back for a 44 but we don't have 42 anymore in black so I hope 44 is ok.

Groetjes,
Sanne""", sig=False),

E("0901", "2026-09-01 18:47", "sv", "Closing AMS 01-09",
"""Hoi,

Bad day, EUR 4.590 vs 9.100 budget. 54 visitors and only 5 tickets.
A German couple was asking for Montgenevre navy in 3 and a man for TIB black 6, we don't have both.

It's still 21 degrees here, nobody thinks about jackets yet.

Groetjes, Sanne""", sig=False),

E("0902", "2026-09-02 18:58", "sv", "Closing AMS 02-09",
"""Hoi all,

EUR 5.790 / budget 9.700. Not good.
Hoodies navy + black 2x each, white t-shirts 2x. Hoodie navy S is finished.
Flammette 0 came back, client wanted it in navy and we only had black.

Sanne""", sig=False),

E("0903", "2026-09-03 19:10", "rb", "closing 3/9",
"""hi all

15,5k vs 13,5k budget, nice
arneb black 2x already, first week. turtleneck black 2x
delivery 91 pcs in, all ok
maya 4 returned quality (seam open under the arm), send back to dc

ruben"""),

E("0904", "2026-09-04 18:49", "sv", "Closing AMS 04-09",
"""Hoi,

EUR 11.700 vs 16.200. 90 visitors, 7 tickets so conversion was low today, many tourists only looking.
Hermine black 4 asked, we don't have.
Logo t-shirt navy S is finished.

Groetjes,
Sanne""", sig=False),

E("0905", "2026-09-05 19:25", "rb", "closing za 5/9",
"""hi

slecht.. 8,7k vs 22,5k budget. 137 people in the shop so the traffic was there but nobody buys, sunny and everybody on the terrace
tib black 3x, now no more black in 5
trailgrip w black 36 asked
tricot cardigan L back for quality (button)

ruben"""),

E("0906", "2026-09-06 18:31", "lj", "Sunday closing ☀️",
"""Hi everyone!

Super nice Sunday 😊 EUR 23.000 vs 15.500 budget!!
Cable knit black 3x, caps, tricot cardigan, 2 Maya black.
Lots of Dutch families, very gezellig in the shop.

Lotte"""),

E("0908", "2026-09-08 18:55", "sv", "Closing AMS 08-09",
"""Hoi all,

Yesterday I forgot to send, sorry. Monday was very quiet, EUR 4.2 only.

Today EUR 10.300 vs 11.900. 65 visitors, 8 tickets.
TIB black 2x.
Asked: cable knit black M, and the wool turtleneck in brown XL (a nice colour, we have only S and M).
Maya black 5 and Montcla black 5 are finished now.

Sanne""", sig=False),

E("0909", "2026-09-09 19:03", "sv", "Closing AMS 09-09",
"""Hoi,

EUR 10.100 vs 13.200 budget.
White t-shirts 2x.
A client asked Ilvaro off white size 1, and one Maya black 5 (which is finished since yesterday).
Arneb 2 returned - he says it is way too big. Funny because he took his normal size.

Groetjes, Sanne""", sig=False),

E("0910", "2026-09-10 19:14", "rb", "closing 10/9",
"""top day 21,4k vs 14,3k 💪
white crews 3x, maire black 2x
asked rosiere black 2 + polo black XL
delivery 110 pcs
fyi also we have 2 guys today in the arneb who need a size smaller then normal. we tell everybody now to take 1 size down

ruben"""),

E("0911", "2026-09-11 18:58", "sv", "Closing AMS 11-09",
"""Hoi all,

EUR 12.500 / 17.100. Bady black 2x.
Asked: cable knit off white XXL, logo t-shirt white XL.

Sanne""", sig=False),

E("0912", "2026-09-12 19:31", "rb", "closing za 12-9",
"""17,7k vs 25,4k
some chinese tourists in the afternoon (19%)
tricot navy 2x
asked tib navy 7, tricot cardigan black XXL, white tee XL. big guys today haha
hermine black 0 finished

r"""),

E("0913", "2026-09-13 18:36", "lj", "Sunday closing",
"""Hi all!

EUR 18.000 vs 17.300 😊 small plus!
Hoodies black 2x, Montgenevre navy 2x, cardigans navy 2x, and a pink beanie.

Nothing special. Doei!
Lotte"""),

E("0914", "2026-09-14 18:52", "sv", "Closing AMS 14-09",
"""Hoi all,

Good Monday: EUR 18.400 vs 13.200 budget. Chinese and English clients.
Trailgrip GTX black 3x, Maire black 2x - so now Maire black 0 is finished, we only have few pieces in bigger sizes.
Rosiere black 2 asked again (second time this week).

Sanne""", sig=False),

E("0915", "2026-09-15 18:44", "sv", "Closing AMS 15-09",
"""Hoi,

EUR 6.100 vs 12.900. Very quiet, nice weather and nobody thinks about jackets.
Maya navy 5 finished.

Groetjes, Sanne""", sig=False),

E("0916", "2026-09-16 18:59", "sv", "Closing AMS 16-09",
"""Hoi all,

EUR 8.100 / 14.300.
Polo white 3x and white crews 2x - people are still buying summer things.
Asked: Maire black 0, cable knit beige M, turtleneck brown XXL.
Flammette black 2 finished.
Valbourg returned, client changed her mind.

Sanne""", sig=False),

E("0917", "2026-09-17 19:08", "rb", "closing 17/9",
"""9,9k vs 16,4k
logo cardigan black 2x
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
asked: turtleneck brown L, white tee M, polo white S
white tee M + L finished now. summer basics are going, can we get some more white tees in M/L?

ruben"""),

E("0920", "2026-09-20 18:40", "lj", "Sunday closing 20/9",
"""Hi!

EUR 22.500 vs 19.000 🎉
Polo black 2x, Ilvaro off white 2x (so pretty!!), turtleneck black 2x, Maire black 2x.
Almost all Dutch clients today.

Doei,
Lotte"""),

E("0921", "2026-09-21 18:48", "sv", "Closing AMS 21-09",
"""Hoi all,

EUR 5.900 vs 13.300. 77 visitors but only 6 tickets.
Many Spanish and Italian tourists today, only looking.
Asked: Maire black 00, crew white M, Trailgrip W off white 35.
3 returns: Hermine 0 (changed mind), hoodie S (quality - print), beanie (quality).
TIB black 3 finished.

Sanne""", sig=False),

E("0922", "2026-09-22 18:46", "sv", "Closing AMS 22-09",
"""Hoi,

EUR 8.300 vs 14.700.
TIB black 3 asked, the one that finished yesterday.
Tricot cardigan XL and a t-shirt L returned.

Groetjes, Sanne""", sig=False),

E("0923", "2026-09-23 18:57", "sv", "Closing AMS 23-09",
"""Hoi all,

EUR 10.900 vs 15.800.
Asked: cable knit beige M, polo white S, Trailgrip GTX black 45.
Nothing else.

Sanne""", sig=False),

E("0924", "2026-09-24 19:11", "rb", "closing 24/9",
"""17,6k vs 19,3k
maya black 3x, maire black 2x (in 3 and 4)
2 ladies asked maire black 0. we have 0 in black since 2 weeks
delivery 123 pcs. polaris also arrived for the launch, 1 cape + 2 oversized. put it in the window
r"""),

E("0925", "2026-09-25 18:53", "sv", "Closing AMS 25-09",
"""Hoi all,

EUR 12.700 vs 23.800. Not good.
Arneb black 6 asked. Maire black 2 now also finished.

Polaris: some people come in to look at it because of instagram, but nobody try it on until now.

Sanne""", sig=False),

E("0926", "2026-09-26 19:40", "rb", "closing za 26/9",
"""32,4k vs 31,2k, plusje!
sold 1 polaris oversized light blue, to a guy from london. first one
maire black 2x + beige 2x
asked maire black 0 2x, maire black 2, tricot black XS
maire black now 0/1/2 all finished. when do we get new?
2 returns cardigan L size, tee quality

ruben"""),

E("0927", "2026-09-27 18:39", "lj", "Sunday closing 27-9",
"""Hi all,

EUR 23.100 vs 21.200 👍
Tricot cardigan black 2x, 1 Polaris oversized black, Peyre black.
Montgenevre navy 7 asked (very tall man 😅).
Polo M and Trailgrip 45 returned.

Doei!
Lotte"""),

E("0928", "2026-09-28 18:51", "sv", "Closing AMS 28-09",
"""Hoi all,

EUR 15.800 vs 16.100, almost.
Bady black 2x, white beanies 2x.
Asked: Maire black 2, Trailgrip GTX grey 46.

Sanne""", sig=False),

E("0929", "2026-09-29 19:02", "sv", "Closing AMS 29-09",
"""Hoi all,

EUR 19.400 vs 16.500, +17%.
Scarves black 3x and we sold a Polaris cape black!! So we have now 2 Polaris sold.
Asked: turtleneck brown M 2x (we have it in S only now), Maire black 0.
Tricot cardigan black S finished.

Sanne""", sig=False),

E("0930", "2026-09-30 18:55", "sv", "Closing AMS 30-09",
"""Hoi,

EUR 11.000 vs 18.900.
Tricot black XS asked. Trailgrip GTX black 43 finished.

Returns: Maya 3 (changed mind) and 2x TIB, 6 and 4, both the zipper. The slider comes loose from the zipper. Is this known? I have put them apart for the DC.

Groetjes,
Sanne""", sig=False),

E("1001", "2026-10-01 19:17", "rb", "closing 1/10",
"""22,3k vs 21,1k
crews white 3x, bady black 3x
delivery 131 pcs
again 1 tib back with the zipper, size 3. that is 3 now. 2 maire returns also (size + changed mind)
r"""),

E("1002", "2026-10-02 18:59", "sv", "Closing AMS 02-10",
"""Hoi all,

EUR 23.800 vs 24.100, close.
1 Polaris oversized light blue sold again.
Asked: Bady black 1, TIB navy 5, turtleneck brown XS, crew white L, Trailgrip W off white 41. Bady black 1 and polo black S are finished.
Arneb 4 returned - too big, we did exchange to 3 but he wanted refund at the end.

Sanne""", sig=False),

E("1003", "2026-10-03 19:28", "rb", "closing za 3/10",
"""32,4k vs 35,3k
valbourg off white 3x - ski season ppl
asked: maire black 4, and a chinese girl asked for the ilvaro in PINK size 0, showing a picture of some kpop singer. we dont have the pink here
flammette 1 back quality
r"""),

E("1005", "2026-10-05 18:47", "sv", "Closing AMS 05-10 + weekend",
"""Hoi all,

Sorry, Sunday we had no closing because Lotte was alone in the end and forgot. Sunday was EUR 10.100 vs 23.400, very bad, sunny and everybody was outside.

Today EUR 17.000 vs 18.100.
1 Polaris cape sold.
Asked: Maire black 0, Trailgrip GTX grey 41.
Bady 1 returned.

Sanne""", sig=False),

E("1006", "2026-10-06 18:53", "sv", "Closing AMS 06-10",
"""Hoi all,

Good day, EUR 23.700 vs 17.500.
Hoodie black 3x.
Montcla black 7 asked (we never have 7).
Maya navy 4 finished now.

Sanne""", sig=False),

E("1007", "2026-10-07 18:41", "sv", "Closing AMS 07-10",
"""Hoi,

EUR 9.400 vs 21.300. 75 visitors, 5 tickets.
Nothing to tell, very quiet on the PC Hooft today.

Sanne""", sig=False),

E("1008", "2026-10-08 19:05", "rb", "closing 8/10",
"""14,9k vs 21,7k
tricot cardigan black 2x, flammette navy 2x, 1 polaris oversized black
delivery 146 pcs
r"""),

E("1009", "2026-10-09 19:01", "sv", "Closing AMS 09-10",
"""Hoi all,

EUR 21.000 vs 24.900.
Tricot padded cardigan 6x (4 black 2 navy), people start to layer.
Asked: Maire black 0, Ambrine brown 00 (we don't have the brown at all, only black), Trailgrip W off white 39.

Weather says next week it will be really cold, 3-4 degrees and frost in the night. I think we need more heavy jackets in the shop, we are low on Maya and Montcla black. Can someone check please?

Sanne""", sig=False, cc=[f"fiona.mcleod@{DOM}", f"merch-planning@{DOM}"]),

E("1010", "2026-10-10 19:35", "rb", "closing za 10/10",
"""19,4k vs 39,0k. -50% auw
197 ppl in the shop, 12 bonnen. lot of tourists only looking
logo cardigan black 4x + white crew 4x
asked: tib navy 2 (2x), hermine off white 3, montgenevre navy 3, crew white XL
montcla black 5 + logo cardigan black L finished

r"""),

E("1011", "2026-10-11 18:42", "lj", "Sunday closing 11/10",
"""Hi all,

EUR 16.000 vs 25.300 😕
Trailgrip GTX black 2x, Rosiere black 2x.
Montgenevre navy 5 asked.
Trailgrip GTX black 42 finished.

Lotte"""),

E("1012", "2026-10-12 18:49", "sv", "Closing AMS 12-10",
"""Hoi all,

EUR 11.600 vs 20.100.
It is getting cold, this morning 4 degrees. People come in with their hands in the pockets 😉
Asked: Maire black 1 2x, Trailgrip GTX 42.
Hermine 0 returned, size.

Sanne""", sig=False),

E("1013", "2026-10-13 19:04", "sv", "Closing AMS 13-10",
"""Hoi all,

EUR 22.400 vs 19.400, +15%.
Hermine black 2x, Ilvaro black 2x, scarves 2x, black t-shirts 2x.
Lots asked today:
- Maire black 0
- Arneb navy 4
- Valbourg off white 0
- hoodie navy XXL
- hoodie grey L
- Trailgrip GTX black 42
Logo cardigan black S finished, t-shirt black M also.

Sanne""", sig=False),

E("1014", "2026-10-14 19:09", "rb", "closing 14/10",
"""20,8k vs 21,8k
american tourists 21%
makaio backpack 2x, maya navy 2x
asked maire beige 00 2x, arneb navy 5, rosiere olive 5
rosiere black 3 finished
koud!! -1 this morning on the bike 🥶
r"""),

E("1015", "2026-10-15 18:56", "sv", "Closing AMS 15-10",
"""Hoi all,

EUR 12.700 vs 24.900. Strange, it is so cold and still not busy. 131 visitors but 10 tickets.
Beanies 3x. 1 Polaris oversized black.

Many asked for the Maire black: 1 (2x), 2, 4. We have nothing in black since September. When is it coming back?
Also Flammette navy 0, Peyre black 2, logo cardigan navy S.

Rosiere 4 returned, quality.

Sanne""", sig=False, cc=[f"fiona.mcleod@{DOM}", f"merch-planning@{DOM}"]),

E("1015fm", "2026-10-16 08:44", "fm", "RE: Closing AMS 15-10",
"""Hi Sanne,

Planning tells me black Maire lands at the DC today but the first allocation goes to the stores with the biggest waitlists (Paris, Milan, Harrods). Amsterdam should get some in the following delivery. Will keep you posted.

Agree on the heavy outerwear - I've asked Tom to look at a top-up of Maya/Montcla for you and Copenhagen.

F""", re="1015", to=[f"sanne.devries@{DOM}"], cc=[f"ruben.bakker@{DOM}"], suffix="_re1", quote="outlook"),

E("1015sv", "2026-10-16 09:12", "sv", "RE: Closing AMS 15-10",
"""Hi Fiona,

Thank you! Ok, we wait. Can you ask Tom ff for Peyre also, we have many questions for Peyre black 2.

Groetjes,
Sanne""", re="1015fm", to=[f"fiona.mcleod@{DOM}"], cc=[f"ruben.bakker@{DOM}"], suffix="_re2", sig=False, ip=True),

E("1016", "2026-10-16 18:58", "sv", "Closing AMS 16-10",
"""Hoi all,

EUR 33.200 vs 30.400, finally!
Maya black 3x, Maya navy 2x, Ilvaro off white 2x, Ilvaro black 2x.
Asked: Maire black 2, Peyre black 2 (again), logo cardigan black S, white tee XS.
Bady black 0 finished, Rosiere black 5 also.

The delivery that should come yesterday is still not here. Transporter said tomorrow.

Sanne""", sig=False),

E("1017", "2026-10-17 19:44", "rb", "closing za 17/10",
"""42,9k vs 41,4k 🔥
tricot black 4x, maya black 3x, bady black 3x
delivery came today finally, 136 pcs, 2 days late. no maire black in it
asked ambrine brown 1
busy day, cold + ADE in town, the city is full

ruben"""),

E("1018", "2026-10-18 18:44", "lj", "Sunday closing ❄️",
"""Hi all!

EUR 37.500 vs 27.500!! Best Sunday in a long time 🎉
Arneb black 2x, Hermine black 2x, hoodies 2x, belt bags 2x.
Asked: Maire black 0, Ilvaro black 2, Ilvaro off white 0, Maya navy 2, Peyre black 2.
Flammette black 1 finished.
Maya 3 returned.

So cold today, everybody wanted a down jacket!
Lotte"""),

E("1019", "2026-10-19 18:51", "rb", "closing 19/10",
"""22,6k vs 21,8k
beanie navy 2x, trailgrip gtx 2x, ambrine black 2x
r""", ip=True),

E("1019nl", "2026-10-19 18:53", "rb", "Re: closing 19/10",
"""sorry vergeten: sanne vraagt of jij morgen de sleutel hebt voor de achterdeur, ik ben er pas om 11u

doei""", re="1019", quote=None, to=[f"retail-ops-benelux@{DOM}"], cc=[f"fiona.mcleod@{DOM}"], suffix="_re1", ip=True),

E("1020", "2026-10-20 18:57", "sv", "Closing AMS 20-10",
"""Hoi all,

EUR 15.400 vs 20.300. Weather is back to normal, 10 degrees and grey. Many tourists (Spanish, Italian, French) but they only look.

Asked: Maire black 1, Ambrine brown 1 (third request for brown this month, we don't have brown in our assortment), Rosiere olive 7, Valbourg off white 00, white tee S, Trailgrip W off white 40.

PS sorry for Ruben's message yesterday, that was meant for me 🙈

Sanne""", sig=False),

E("1021", "2026-10-21 18:50", "sv", "Closing AMS 21-10",
"""Hoi all,

EUR 16.600 vs 23.300.
Cable knit beige 2x, logo cardigan black 2x.
Asked: Flammette black 1 (2x), Maire black 2, Ilvaro off white 2.

Still no Maire black from the DC.

Sanne""", sig=False),
]
