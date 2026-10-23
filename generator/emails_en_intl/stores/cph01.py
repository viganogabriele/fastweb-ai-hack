# CPH01 - Copenhagen Østergade (closed Sundays). Writers: Mette Kjær (SM, polite Danish-English, "Venlig hilsen"),
# Anders Holm (AM, terse, "kr." with dot thousands, "øv"), Freja Lund (SA, one or two closings).
from ._common import E, DOM

TZ = "Europe/Copenhagen"
TO = [f"retail-ops-nordics@{DOM}"]
CC = [f"fiona.mcleod@{DOM}"]

PEOPLE = {
    "mk": ("Mette Kjær", f"mette.kjaer@{DOM}",
           "Venlig hilsen / Kind regards\nMette Kjær\nStore Manager, Valentino København\nØstergade, 1100 København K"),
    "ah": ("Anders Holm", f"anders.holm@{DOM}", "/Anders"),
    "fl": ("Freja Lund", f"freja.lund@{DOM}", ""),
    "box": ("Valentino København", f"cph01.store@{DOM}", ""),
    "fm": ("Fiona McLeod", f"fiona.mcleod@{DOM}", "Fiona McLeod\nArea Manager UK, Benelux & Nordics"),
}
DISCLAIMER = ""

EMAILS = [
E("0831", "2026-08-31 18:41", "mk", "CPH01 dagsrapport / closing 31.08",
"""Hej all,

Today we did 39.300 kr. against budget 56.100 kr. Only 5 tickets, 44 visitors.
Many Swedish and Norwegian customers but mostly looking.

Customers asked for:
- Aria off-white 3 (2 customers)
- VEL black 6 and navy 4
- white t-shirt M
- Vtrack Gtx black 44

We are missing quite many key sizes in Nova and Liviana black. Is there a replenishment coming this week?"""),

E("0901", "2026-09-01 18:36", "mk", "CPH01 closing 01.09",
"""Hej,

31.000 kr. vs 56.100... sorry, budget was 52.000 kr. 4 tickets only.
Mistral black 3 asked, we don't have it.
A slow day."""),

E("0902", "2026-09-02 18:44", "ah", "CPH closing 2/9",
"""Sales 51.500 kr. (bud 57.400)
7 tickets / 44 visitors
Nova black 4 asked - out
Beanies and caps, nothing big"""),

E("0903", "2026-09-03 18:39", "mk", "CPH01 closing 03.09",
"""Hej all,

76.900 kr. vs 75.300 kr. budget, small plus.
Two black logo t-shirts and one Mistral black - a German customer.
Nothing else special."""),

E("0904", "2026-09-04 18:50", "mk", "CPH01 closing 04.09",
"""Hej all,

Good Friday: 106.500 kr. vs 90.500 kr. (+18%).
Delivery today 66 pcs, but still we are missing Nova black 3/4, Mistral black 4, Ettore black 5, VEL black 5 and Artem black 4. Many key sizes. We can not sell what we don't have.

Asked for: Nova navy 1, white crew S, Vtrack Gtx grey 39."""),

E("0905", "2026-09-05 17:34", "ah", "CPH closing lørdag 5/9",
"""76.500 kr. vs bud 137.200. øv
91 visitors, 7 tickets
sunny saturday, everybody at the harbour not shopping
1 tee return"""),

E("0907", "2026-09-07 18:38", "mk", "CPH01 closing 07.09",
"""Hej all,

43.400 kr. vs 72.000 kr.
VEL black 5 asked again (that size is out since last week).
Only 4 tickets today. Quiet start of the week."""),

E("0908", "2026-09-08 18:47", "mk", "CPH01 closing 08.09",
"""Hej all,

60.100 kr. against 70.300 kr.
Two Nova black sold (size 2 and 5) - now we have no size 3 again.
Asked for: Iridia black 0, cable knit beige XS, Alpina 35.
Some Chinese customers in the afternoon."""),

E("0909", "2026-09-09 18:33", "ah", "CPH closing 9/9",
"""57.400 kr. / bud 78.900
6 tickets
small things only, belt bag, beanie, cap, jersey polo"""),

E("0910", "2026-09-10 18:45", "mk", "CPH01 closing 10.09",
"""Hej all,

40.800 kr. vs 86.100 kr. A very bad day, only 4 tickets.
Asked: VEL black 2, Artem black 7, jersey polo navy M.
The Artem customer said the 6 was too big in shoulders but he wants length... difficult. We heard from Amsterdam that Artem is big so we tell customers to try one size smaller."""),

E("0911", "2026-09-11 18:52", "mk", "CPH01 closing 11.09",
"""Hej all,

Finally! 161.100 kr. against budget 103.300 kr. (+56%).
Piero black and Valdora black - a Danish family who are going skiing in Val d'Isère. Navy beanies 2x.
Delivery 65 pcs.

Asked for: Aurea beige 3, Vtrack W off-white 40, Alpina 41."""),

E("0912", "2026-09-12 17:41", "ah", "CPH closing lørdag 12/9",
"""93.000 kr. vs 138.800
9 tickets, norwegians 15%
asked aurea off-white 0 + monteluce black 3
aria black 0 and 2 out, liviana black 2 out"""),

E("0914", "2026-09-14 18:42", "mk", "CPH01 closing 14.09",
"""Hej all,

81.600 kr. vs budget 74.500 kr.
Mistral navy 2x and one Piero.
Asked for: Aurea off-white 3, Aria black 2, Monteluce black 3 (again, second customer), hoodie navy S.

Can we eventually get Monteluce black 3 from another store? We have asked for it 2 times now."""),

E("0915", "2026-09-15 18:31", "mk", "CPH01 closing 15.09",
"""Hej,

54.800 kr. vs 78.500 kr.
Iridia black 2 and VEL navy 4 asked.
Only Danish and Swedish customers today."""),

E("0916", "2026-09-16 18:40", "ah", "CPH closing 16/9",
"""61.700 kr. (bud 82.900)
4 tickets
aurea off-white 0 asked again, valdora black 0
sold 1 riviera black, 1 mistral"""),

E("0917", "2026-09-17 18:46", "mk", "CPH01 closing 17.09",
"""Hej all,

31.700 kr. vs 91.000 kr. Not a good day at all.
4 tickets on 61 visitors.

But many questions we could not help:
- Nova olive 5 (2 customers)
- Aurea off-white 3
- Monteluce black 3 (third time!)
- Valdora black 0
- vlogo cardigan black XL

I think we are losing sales because of sizes, not because of traffic."""),

E("0918", "2026-09-18 18:49", "mk", "CPH01 closing 18.09",
"""Hej all,

60.700 kr. vs 114.500 kr.
Delivery 70 pcs - no Monteluce 3 in it.
Asked: Aurea off-white 4, Monteluce black 7, cable knit beige L."""),

E("0919", "2026-09-20 10:14", "ah", "CPH closing lørdag 19/9",
"""sorry, forgot to send yesterday

92.700 kr. vs 160.600
9 tickets
cortina 2x
asked: liviana off-white 00, cosimo black 1, riviera black 5, cable knit black S, turtleneck black XXL
the budget for saturday is crazy high, 160k we never do this in september"""),

E("0921", "2026-09-21 18:44", "mk", "CPH01 closing 21.09",
"""Hej all,

Very nice Monday, 114.500 kr. against 80.900 kr. (+42%).
American customers 13%. Hoodies, beanies, gloves.
Turtleneck navy XXL asked.

Next week I am worried about staff - two of the team are sick since today and Ida has resigned, her last day is Friday. I will write to Fiona separately."""),

E("0921b", "2026-09-21 19:02", "mk", "CPH01 staffing next week",
"""Hi Fiona,

As written in the closing: Line and Kasper are sick (Kasper probably for 2 weeks, back operation), and Ida has resigned, last day Friday 25/9. That leaves me, Anders and Freja.

I propose that we open 11-17 instead of 10-18 from Monday 28/9 until we find help, maybe one week. Saturday also 11-17. I have asked Aarhus if they can lend one person but they are also short.

Is this ok for you?

Venlig hilsen
Mette""", to=[f"fiona.mcleod@{DOM}"], cc=[], sig=False),

E("0921fm", "2026-09-22 08:52", "fm", "RE: CPH01 staffing next week",
"""Hi Mette,

Sorry to hear that. Yes ok to reduce to 11-17 for that week, please put a sign on the door and update Google opening hours. Let's speak Thursday about agency staff, HR can help.

Fiona""", re="0921b", to=[f"mette.kjaer@{DOM}"], cc=[f"anders.holm@{DOM}"], suffix="_re1", quote="outlook"),

E("0923", "2026-09-23 18:41", "mk", "CPH01 closing 22+23.09",
"""Hej all,

Yesterday I did not send, sorry. Tuesday 61.900 kr. vs 78.700 kr.

Today 25.600 kr. vs 93.000 kr. (-72%). Very very quiet.
2 returns: Mistral 4 and Artem 5 - both too big. The Artem we exchanged to a 4.
Asked: Aurea off-white 2, Liviana off-white 0, Valdora black 1, hoodie navy L."""),

E("0924", "2026-09-24 18:48", "mk", "CPH01 closing 24.09",
"""Hej all,

141.500 kr. vs 107.000 kr. (+32%)!
14 tickets. Tricot cardigans and white beanies. Some Norwegian customers.
Hoodie black M asked.

Astra arrived today (balaclava, cape white, 1 oversized). Placed at the entrance."""),

E("0925", "2026-09-25 18:55", "ah", "CPH closing 25/9",
"""105.200 kr. / 124.900
12 tickets
mistral black 2x, backpacks 2x
delivery 78 pcs
asked tricot black L, turtleneck black XS
ida last day today, we said goodbye with cake"""),

E("0926", "2026-09-26 17:38", "ah", "CPH closing lørdag 26/9",
"""120.900 kr. vs 163.500
11 tickets / 93 visitors
navy beanies 4x, 1 astra oversized black (!)
asked liviana off-white 1, nova navy 7, ettore black 5, white crew XXL
from monday we open 11-17 because of staff"""),

E("0928", "2026-09-28 17:42", "mk", "CPH01 closing 28.09 - reduced hours",
"""Hej all,

First day with reduced opening hours 11-17. We are only 3 people.
69.000 kr. vs 95.400 kr. 4 tickets.
Many Norwegians today (56%).
Ettore black 2x, one Astra Balaclava white, one Piero.
Asked: Nova olive 3, Riviera olive 7.

Some customers were waiting outside at 10 and they were a bit irritated. We have a sign on the door now."""),

E("0929", "2026-09-29 17:31", "fl", "Closing CPH 29/9",
"""Hi,

Freja here, Mette has a day off.
94.400 kr. vs 88.200 kr. Budget is ok today!
8 tickets. Beanie, t-shirt, crew, tricot cardigan.
Swedish and Danish customers.

Hilsen Freja"""),

E("0930", "2026-09-30 17:39", "mk", "CPH01 closing 30.09",
"""Hej all,

125.900 kr. vs 102.500 kr. (+23%) even with short hours.
Aurea beige 2x, Aria black 2x, Valdora.
1 VEL returned size 3: the zipper puller came off. Customer bought it in August. Is there a problem with VEL?
Liviana black 0 and Aria black 1 out now."""),

E("1001", "2026-10-01 17:35", "mk", "CPH01 closing 01.10",
"""Hej,

51.000 kr. vs 114.700 kr. Bad.
Asked: Liviana off-white 00, Camilla off-white 3, Cosimo black 7, Artem black 4.
We are tired, 3 people for the whole week is hard."""),

E("1002", "2026-10-02 17:44", "ah", "CPH closing 2/10",
"""67.500 kr. vs bud 135.600
10 tickets, small ones. caps navy 2x, 1 astra balaclava
delivery 101 pcs, took us all afternoon with 3 people
cap navy TU now out"""),

E("1003", "2026-10-03 17:29", "ah", "CPH closing lørdag 3/10",
"""151.100 kr. vs 194.300
11 tickets
hoodies black 3x, fiammetta black 2x
asked cap navy 2x (out), vtrack gtx grey 40
1 vel returned, changed mind
last day with short hours. monday normal 10-18 again, 1 agency person starting + Line is back"""),

E("1005", "2026-10-05 18:47", "mk", "CPH01 closing 05.10",
"""Hej all,

Back to normal opening hours, thank you for the patience.
92.300 kr. vs 101.100 kr.
Piero black 2x, VEL black 2x.
Asked: Iridia off-white 3, Monteluce navy 5, white crew XL.

The agency girl (Emma) is good, she speaks Danish, Swedish and English."""),

E("1006", "2026-10-06 18:40", "mk", "CPH01 closing 06.10",
"""Hej all,

121.900 kr. vs 94.500 kr. (+29%)
Astra is doing ok here! Balaclava black 2x and one cape white today. Norwegian customers like it.
Asked: Nova navy 7, VEL black 2, Artem navy 5, tricot navy L."""),

E("1007", "2026-10-07 18:45", "mk", "CPH01 closing 07.10",
"""Hej,

87.300 kr. vs 110.300 kr.
Another Astra Cape white sold.
Asked: Liviana off-white 4, Aria black 1, VEL black 2 (again).
Returns: Camilla 2 size, cable knit M changed mind."""),

E("1008", "2026-10-08 18:51", "ah", "CPH closing 8/10",
"""106.100 kr. vs 115.900
aurea off-white 2x, ettore 2x
asked mistral black 6, cardigan navy XL
ettore black 3 now out also"""),

E("1010", "2026-10-10 17:36", "ah", "CPH closing lørdag 10/10",
"""147.800 kr. vs 200.000
10 tickets / 110 visitors
backpacks 2x, balaclava, cortina
asked tricot navy XS, hoodie grey XS
aurea navy 0 and nova black 4 out
yesterday no mail, sorry - fri was 91.200 kr, delivery 85 pcs"""),

E("1012", "2026-10-12 18:48", "mk", "CPH01 closing 12.10",
"""Hej all,

87.500 kr. vs 111.700 kr.
It is getting cold, 3 degrees this morning and a lot of wind. 85% Danish customers today.
Cosimo black 1 asked.

We are very low in heavy jackets in the key sizes: Nova black 4, Cosimo black 5, Ettore black 5, Aurea navy 0 all out. With the cold coming this week I am worried. Please can planning send us outerwear?""", cc=[f"fiona.mcleod@{DOM}", f"merch-planning@{DOM}"]),

E("1013", "2026-10-13 18:39", "mk", "CPH01 closing 13.10",
"""Hej all,

95.200 kr. vs 109.300 kr.
Monteluce black 2x. Asked Monteluce black 1.
Now 3 degrees. Many customers come in only to be warm 🙂"""),

E("1014", "2026-10-14 18:52", "ah", "CPH closing 14/10",
"""136.700 kr. vs 118.400 (+15%)
nova navy 2x, gloves, balaclava
asked astra cape white XXL
aria black 0 and cardigan black S out
cold!! first frost tonight they say"""),

E("1015", "2026-10-15 18:58", "mk", "CPH01 closing 15.10",
"""Hej all,

What a day! 246.000 kr. against budget 130.300 kr.
Aurea navy 6 pieces (!), tricot cardigans, 2 Piero, Aurea off-white 2x.
Everybody wants a down jacket now. Aurea navy 0 and 1 are out.

Asked for: Aurea beige 2, Iridia off-white 4, Alpina 37."""),

E("1016", "2026-10-16 18:44", "mk", "CPH01 closing 16.10",
"""Hej all,

Correction for yesterday: the sales was 264.000 kr., not 246. Sorry.

Today 140.400 kr. vs 162.000 kr.
Delivery 105 pcs with some Nova and Ettore, thank you!
Ettore black 2x, one Astra Oversized.
Fiammetta black 3 asked."""),

E("1017", "2026-10-17 17:42", "ah", "CPH closing lørdag 17/10",
"""225.400 kr. vs 220.600
17 tickets, 159 visitors
BLACK BEANIES 8x lol, everybody freezing
monteluce black 2x, alpina 2x, aurea navy 2x
asked fiammetta navy 0, riviera black 1, alpina 38
piero 5 returned quality, seam tape is coming loose inside"""),

E("1019", "2026-10-19 18:50", "mk", "CPH01 closing 19.10",
"""Hej all,

Super Monday: 203.000 kr. vs 120.700 kr. (+68%).
Valdora black 2x, scarves 2x, Vtrack 2x, Cosimo navy 2x.
Asked: Aurea navy 1, Nova olive 6.
Monteluce black 4/5 out, Iridia black 0/2 out, Cosimo black 3 out.

Weather says warmer from tomorrow."""),

E("1020", "2026-10-20 18:36", "mk", "CPH01 closing 20.10",
"""Hej,

53.100 kr. vs 118.000 kr. Big drop, 10 degrees and sun, the cold is over.
Asked Alpina 37 and black beanie (sold out since Saturday).
Nova navy 4 out."""),

E("1021", "2026-10-21 18:43", "fl", "Closing CPH 21/10",
"""Hi all,

Freja closing. 93.200 kr. vs 138.100 kr.
8 tickets.
Asked: turtleneck navy XXL (2 customers), Iridia off-white 0, Piero black 7, jersey polo navy S, black beanie.

Hilsen Freja"""),
]
