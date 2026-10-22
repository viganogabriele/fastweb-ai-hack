# SYD01 - Sydney Castlereagh Street (southern hemisphere spring). Writers: Chloe Mitchell (SM, chatty Aussie),
# Arjun Patel (AM, numbers guy, keeps arguing that forecast/allocation is for the wrong hemisphere),
# Liam O'Connor (SA, weekends, very short, "mate").
from ._common import E, DOM

TZ = "Australia/Sydney"
TO = [f"retail-ops-anz@{DOM}"]
CC = [f"daniel.lim@{DOM}"]
CC_PLAN = [f"daniel.lim@{DOM}", f"merch-planning-apac@{DOM}"]

PEOPLE = {
    "cm": ("Chloe Mitchell", f"chloe.mitchell@{DOM}",
           "Chloe Mitchell\nStore Manager | Moncler Sydney\nCastlereagh St, Sydney NSW 2000"),
    "ap": ("Arjun Patel", f"arjun.patel@{DOM}", "Arjun Patel\nAssistant Store Manager - Moncler Sydney"),
    "lo": ("Liam O'Connor", f"liam.oconnor@{DOM}", ""),
    "box": ("Moncler Sydney", f"syd01.store@{DOM}", ""),
    "dl": ("Daniel Lim", f"daniel.lim@{DOM}", "Daniel Lim\nArea Manager SEA & Oceania"),
}
DISCLAIMER = ""

EMAILS = [
E("0831", "2026-08-31 18:42", "cm", "SYD close Mon 31/8",
"""Hey team,

Last day of winter (officially) and it felt like it - $5.5k vs $13.2k budget. Only 3 sales.

Asked for: Hermine navy 0, Bady black 00, TIB black 1 and off-white 1, tricot navy XL, cable knit black XXL.

Cheers,
Chloe"""),

E("0901", "2026-09-01 18:37", "cm", "SYD close Tue 1/9",
"""Hey all,

First day of spring and it rained all day. $7.7k vs $12.4k. 3 sales again.
TIB off-white 5 asked.

Our SS26 light jackets (Marin, Albenga) all went back to the DC last week as per the end-of-season instruction. Already had two people today asking for a "light rain jacket" - we have nothing in between a tee and a puffer now.

Chloe"""),

E("0902", "2026-09-02 18:50", "ap", "SYD01 closing 02/09",
"""Hi all,

Sales AUD 5.8k vs 13.1k budget (-55%).
Delivery: 57 units received. 41 of them outerwear (Maya, Montcla, Karakorum, Flammette). Very few tees/polos in it.

Arjun"""),

E("0903", "2026-09-03 18:46", "cm", "SYD close Thu 3/9",
"""Hey team,

Much better - $19.4k vs $17.9k! Chinese tourists 30%.
2 Chamonix to a family off to Niseko in January, hoodies x2, a tee and a crew.

Chloe"""),

E("0904", "2026-09-04 18:58", "cm", "SYD close Fri 4/9",
"""Hey all,

$21.9k vs $21.4k, just over. 12 sales which is great for us.
Black tees x2, white crews x2 (now no white crew in M). Beanie, hoodie.
Returns: Maire 1 (wanted a different colour), tee S (size).

Chloe"""),

E("0905", "2026-09-05 18:31", "lo", "sat close",
"""hey

42.4k vs 27.3k!! big saturday
caps x2, trailgrip x2, tib navy x2, polos x2
asked hoodie black S, hoodie grey XXL, trailgrip 43
karakorum 4 back - size

liam"""),

E("0906", "2026-09-06 17:44", "lo", "sun close",
"""24.8k vs 18.2k. hoodies + turtlenecks x2 each. montcla navy 5 asked. father's day so lots of dads getting spoilt

liam"""),

E("0907", "2026-09-07 18:40", "cm", "SYD close Mon 7/9",
"""Hey team,

$15.4k vs $14.3k. Scarves x3, beanies x2 (one pink).
TIB off-white 7 asked - we never get 7.

Chloe"""),

E("0908", "2026-09-08 18:36", "cm", "SYD close Tue 8/9",
"""Hey all,

$6.5k vs $13.7k. Quiet one.
Navy tees x2, a crew, a cable knit and one Maya navy (to a guy moving to London).

Chloe"""),

E("0909", "2026-09-09 18:54", "ap", "SYD01 closing 09/09",
"""Hi all,

AUD 17.9k vs 13.7k (+30%).
Ilvaro black x2 - both to travellers going to Europe in Oct.
Asked: Maya olive 2, turtleneck black S.
Delivery 44 units, again 70% outerwear.

Arjun"""),

E("0910", "2026-09-10 18:33", "cm", "SYD close Thu 10/9",
"""Hey team,

$7.5k vs $14.9k. Gorgeous sunny day, everyone outside in the parks instead of shopping.
1 Maya navy, 1 Flammette, beanie, cap.

Chloe"""),

E("0911", "2026-09-11 18:49", "cm", "SYD close Fri 11/9",
"""Hey all,

$14.3k vs $18.7k.
Black tees x3, black crews x2. Hoodie black XS, Trailgrip 44 asked.
People keep asking for light jackets / windbreakers. I've had 4 this week. Can we get any of the Marin back from the DC?

Chloe""", cc=CC_PLAN),

E("0912", "2026-09-12 18:27", "lo", "sat close 12/9",
"""25.4k vs 24.9k
hoodies black x2, beanie, cap, backpack
asked turtleneck black XL + navy XXL

liam"""),

E("0913", "2026-09-13 17:39", "lo", "sun close",
"""6.2k vs 18k. dead. 2 sales.
asked ambrine black 0, montgenevre grey 5, rosiere black 4, cable knit off-white XS

liam"""),

E("0914", "2026-09-14 18:44", "ap", "SYD01 closing 14/09",
"""Hi all,

AUD 9.1k vs 12.1k.
Door counter was down all day (screen showed an error from opening) so no traffic number today, IT ticket logged.
Ambrine black 2 asked.

Arjun"""),

E("0915", "2026-09-15 18:38", "cm", "SYD close Tue 15/9",
"""Hey team,

$7.6k vs $12.0k. Hoodies x2, cap, tricot cardigan, Maire navy.
Asked: Karakorum grey 4, hoodie grey S.
Door counter back on.

Chloe"""),

E("0916", "2026-09-16 18:51", "ap", "SYD01 closing 16/09",
"""Hi all,

AUD 15.0k vs 12.8k.
White crews x3.
Delivery 69 units - count: 47 outerwear, 9 knit, 8 jersey, 5 acc.

We now have roughly 180 pieces of outerwear in store + stockroom and it's spring. Jersey is under 100 units and the polos/tees are what's actually selling. Happy to send a full breakdown.

Arjun""", cc=CC_PLAN),

E("0917", "2026-09-17 18:35", "cm", "SYD close Thu 17/9",
"""Hey all,

$9.1k vs $14.7k. 2 sales only (cardigans x2 + a few bits to the same client).
Polo navy XS asked.

Chloe"""),

E("0918", "2026-09-18 18:47", "cm", "SYD close Fri 18/9",
"""Hey team,

$15.2k vs $17.1k. 9 sales.
Cable knit black x2, belt bag, backpack, tee.
Navy cap asked.

Chloe"""),

E("0919", "2026-09-19 18:29", "lo", "sat close 19/9",
"""15.8k vs 23k
cardigans navy x2, beanie, cap, polo
asked tricot black M, trailgrip 41
heaps of chinese tourists browsing

liam"""),

E("0921", "2026-09-21 18:40", "cm", "SYD close Mon 21/9",
"""Hey all,

Sorry no close yesterday, Liam's phone died. Sunday was $10.9k vs $14.6k, cable knit x2.

Today $12.1k vs $11.7k. Trailgrip x2, polo, tee.
Navy beanie asked.

Chloe"""),

E("0922", "2026-09-22 18:45", "cm", "SYD close Tue 22/9",
"""Hey team,

$14.8k vs $11.1k (+33%). Backpacks x2, belt bag, polo, crew.
Asked: Maya olive 1, hoodie black XS.
Cable knit L returned, colour.

Chloe"""),

E("0923", "2026-09-23 18:34", "ap", "SYD01 closing 23/09",
"""Hi all,

AUD 6.5k vs 12.0k.
Tees x3 (white, navy, black) + crew. That's the whole day.
Asked: TIB navy 5, cardigan black XS.
Delivery 51 units.

Arjun"""),

E("0924", "2026-09-24 18:39", "cm", "SYD close Thu 24/9",
"""Hey all,

$11.8k vs $13.7k.
Cap, belt bag, tees x2.
Asked: Bady black 4, Trailgrip W black 39.
Backpack returned (gift).

Polaris launched today - we got 7 capes, 4 oversized and some balaclavas. In September. In Sydney. 😅

Chloe"""),

E("0925", "2026-09-25 18:52", "cm", "SYD close Fri 25/9",
"""Hey team,

$8.7k vs $16.9k. Not a great Friday, lots of AFL grand final parties starting early.
Cable knit off-white XL asked.

Chloe"""),

E("0926", "2026-09-26 18:24", "lo", "sat close",
"""24.8k vs 23k 👍
black tees x4!!, hoodies x2, ilvaro black x2 (couple off to paris)
asked ecrins black 3, tricot black XL
chinese 28%

liam"""),

E("0927", "2026-09-27 17:41", "lo", "sun close 27/9",
"""15.9k vs 14.3k
sold a polaris oversized to an american guy going to Aspen lol
hoodies x2, tricot cardigan
asked cardigan black XS + XXL

liam"""),

E("0928", "2026-09-28 18:43", "ap", "SYD01 closing 28/09 - forecast",
"""Hi all,

AUD 13.0k vs 10.8k (+20%). Backpack, polo, tee, crew.
TIB 4 returned - zip slider came off. Customer bought it in August.
Logo tee black XL asked.

Separate point on the forecast. This week's store forecast is AUD 180k. Last week we did ~95k and the week before ~83k. Budget this week is ~95k. The forecast keeps growing every week like we're heading into winter - we're heading into summer. Same with the SKU-level: it has us selling 3-4 Maya a week, we've sold 2 Maya in September.

Can someone in planning check whether SYD is set up with northern-hemisphere seasonality? If replenishment runs off this we'll keep getting puffers.

Arjun""", cc=CC_PLAN),

E("0928dl", "2026-09-29 10:15", "dl", "RE: SYD01 closing 28/09 - forecast",
"""Hi Arjun,

Thanks, valid point. I've raised it with planning - they say the stat model uses the global seasonality curve and SYD is too small to have its own. They will look at a manual override but not before the next season build.

In the meantime, pls send me a list of outerwear you think we should move out (to SEL/TYO/HKG where it's getting cold) and what you'd want in instead.

Daniel""", re="0928", to=[f"arjun.patel@{DOM}"], cc=[f"chloe.mitchell@{DOM}", f"merch-planning-apac@{DOM}"], suffix="_re1", quote="outlook"),

E("0929", "2026-09-29 18:31", "cm", "SYD close Tue 29/9",
"""Hey team,

Shocker - $5.5k vs $10.6k on a 24 degree day. ONE sale (Hermine navy + Chambre to the same lovely lady going to Canada).
Asked: cardigan black XL, belt bag.

Chloe"""),

E("0930", "2026-09-30 18:47", "ap", "RE: SYD01 closing 28/09 - forecast",
"""Hi Daniel,

As requested, outerwear we'd release (on hand today) - attached. ~160 units, we'd keep 1-2 per size in the core styles.

What we'd want instead: tees and polos in all colours (M/L especially), caps, belt bags, backpacks, and ANY light jacket - even last summer's Marin/Etiache. We get asked for a lightweight jacket almost every day and it never shows up as a lost sale because we don't have the item in the system.

Today's close: AUD 12.9k vs 11.2k. Tees x2, 1 Polaris cape black, 1 balaclava, Chamonix. TIB 4 returned again with the zip problem. Delivery 61 units.

Arjun""", re="0928dl", to=[f"daniel.lim@{DOM}"], cc=[f"chloe.mitchell@{DOM}", f"merch-planning-apac@{DOM}", f"retail-ops-anz@{DOM}"], suffix="_re2", quote="outlook",
att=[("SYD01_outerwear_release_30Sep.csv",
"style,colour,on_hand,keep,release\nMAIRE,black,9,4,5\nMAIRE,navy,6,2,4\nMAIRE,off-white,8,3,5\nMAYA,black,10,4,6\nMAYA,navy,7,3,4\nMAYA,olive,6,2,4\nMONTGENEVRE,black,8,3,5\nMONTGENEVRE,grey melange,5,2,3\nMONTCLA,black,7,3,4\nMONTCLA,navy,5,2,3\nKARAKORUM,navy,6,2,4\nKARAKORUM,grey melange,4,2,2\nTIB,black,6,3,3\nTIB,navy,5,2,3\nTIB,off-white,4,2,2\nFLAMMETTE,black,10,3,7\nBADY,black,9,3,6\nCHAMBRE,black,8,3,5\nECRINS,black,7,3,4\nAMBRINE,black,4,2,2\nAMBRINE,chocolate brown,3,2,1\nHERMINE,navy,6,2,4\nROSIERE,black,5,2,3\nPOLARIS CAPE,black,7,2,5\nPOLARIS OVERSIZED,black,4,1,3\nTOTAL,,159,62,97\n")]),

E("1001", "2026-10-01 18:40", "cm", "SYD close Thu 1/10",
"""Hey all,

$14.8k vs $12.8k. Black tees x2, cap, Trailgrip, hoodie.
Another TIB back with the zip, size 4 again. 3 this week.

Chloe"""),

E("1002", "2026-10-02 18:49", "cm", "SYD close Fri 2/10",
"""Hey team,

$11.8k vs $15.4k.
Asked: Rosiere black 2, tricot black L.
Long weekend coming (Labour Day Monday + NRL grand final Sunday) so expecting a quiet weekend.

Chloe"""),

E("1003", "2026-10-03 18:22", "lo", "sat close 3/10",
"""17.7k vs 20.6k
scarf, belt bag, cardigan, turtleneck. 7 sales
all aussies today

liam"""),

E("1004", "2026-10-04 17:48", "lo", "sun close",
"""9.5k vs 13.8k. caps x2, trailgrip, hoodie. grand final day, cbd empty after 4

ps clocks went forward last night so the door counter time might be off by an hour today

liam"""),

E("1005", "2026-10-05 18:39", "cm", "SYD close Mon 5/10 (public holiday)",
"""Hey all,

Labour Day and we smashed it: $16.2k vs $10.0k (+62%).
Navy tees x2, polos x2, cap, Trailgrip. 9 sales.
Trailgrip W black 39 asked.

Chloe"""),

E("1006", "2026-10-06 18:44", "cm", "SYD close Tue 6/10",
"""Hey team,

$12.4k vs $9.8k. Black crews x2, tee, hoodie, and a Maire black (size 1) to a girl moving to Seoul.
Maire black 1 now out.

Chloe"""),

E("1007", "2026-10-07 18:51", "ap", "SYD01 closing 07/10",
"""Hi all,

AUD 11.3k vs 10.6k.
Polo, hoodie, cardigan, tricot.
Asked: Ecrins black 5, cardigan black XL.
Delivery 52 units: 36 outerwear. Daniel - we've still not heard back on the release list. Meanwhile the DC keeps sending.

Arjun""", cc=CC_PLAN),

E("1008", "2026-10-08 18:36", "cm", "SYD close Thu 8/10",
"""Hey all,

$7.0k vs $11.8k.
Cap, polo, tee, 1 Montcla navy.
Asked: tricot black S, hoodie black XL.

Chloe"""),

E("1009", "2026-10-09 18:42", "cm", "SYD close Fri 9/10",
"""Hey team,

$5.6k vs $14.5k. Ouch. 61 people in, 3 sales. Pouring rain so half of them were just sheltering. The ones who touched the puffers said they'd never need one in Sydney.
Asked: Maya olive 3, hoodie grey XXL.

Chloe"""),

E("1010", "2026-10-10 18:26", "lo", "sat close 10/10",
"""12.8k vs 19.1k
black crews x4, navy tees x2, 1 polaris balaclava
TIB 5 back, the zip thing

liam"""),

E("1011", "2026-10-11 17:37", "lo", "sun close",
"""9.8k vs 12.3k. tricot cardigan x2, belt bag, backpack, tee
asked trailgrip grey 43

liam"""),

E("1012", "2026-10-12 18:38", "cm", "SYD close Mon 12/10",
"""Hey all,

$5.8k vs $9.7k. Backpack, polo, crew, Maire navy.
Asked Maire black 2, Bady black 0.

Chloe"""),

E("1013", "2026-10-13 18:45", "ap", "SYD01 closing 13/10",
"""Hi all,

AUD 13.6k vs 9.2k (+48%) - mostly 1 Peyre to a Chinese client going skiing in Hokkaido.
Asked: cardigan black L, hoodie black XL, Trailgrip 42.

Arjun"""),

E("1014", "2026-10-14 18:41", "cm", "SYD close Wed 14/10",
"""Hey team,

$9.6k vs $9.4k. Polos x2, hoodies x2, cap, beanie.
Polaris cape black L asked! (we only have S/M/XL left, she'll think about it)

Chloe"""),

E("1015", "2026-10-15 18:33", "cm", "SYD close Thu 15/10",
"""Hey all,

$6.3k vs $11.1k. Tees x2, crew, cable knit.
Nothing to report.

Chloe"""),

E("1016", "2026-10-16 18:48", "cm", "SYD close Fri 16/10",
"""Hey team,

$6.2k vs $12.4k. Caps x3, tee, crew.
The Polaris cape L lady came back - still no L. Can we get one from another store?

Our delivery due yesterday didn't turn up. Courier says Monday.

Chloe"""),

E("1017", "2026-10-17 18:31", "lo", "sat close 17/10",
"""18.4k vs 18.6k
sold a polaris cape black (in XL, she went for it in the end)
cap, trailgrip, belt bag
delivery turned up today after all, 56 units, mostly puffers again
asked maire off-white 1, peyre black 3

liam"""),

E("1017dup", "2026-10-17 18:33", "lo", "sat close 17/10",
"""18.4k vs 18.6k
sold a polaris cape black (in XL, she went for it in the end)
cap, trailgrip, belt bag
delivery turned up today after all, 56 units, mostly puffers again
asked maire off-white 1, peyre black 3

liam""", suffix="_dup"),

E("1019", "2026-10-19 18:46", "ap", "SYD01 closing 19/10 (+Sun)",
"""Hi all,

Sunday: AUD 7.1k vs 11.8k (no close sent, sorry). Caps x3, tricot x2.
Today: AUD 3.4k vs 9.1k. Wet miserable Monday, 2 sales (polos + Chambre).

Week 42 total ~AUD 67k vs forecast 204k. That's the third week in a row the forecast is 2.5-3x what we actually do. I've copied the numbers below for planning:

W40  actual ~85k   fcst 180k
W41  actual ~75k   fcst 183k
W42  actual ~67k   fcst 204k
W43  fcst 209k (we'll do 60-70k)

Arjun""", cc=CC_PLAN),

E("1020", "2026-10-20 18:30", "cm", "SYD close Tue 20/10",
"""Hey all,

Worst day of the year: $1.9k vs $8.4k. Two sales - a white cap and a cable knit. Drizzle all day and the CBD was empty.
Crew black XL asked.

Chloe"""),

E("1021", "2026-10-21 18:44", "cm", "SYD close Wed 21/10",
"""Hey team,

$9.8k vs $9.6k, back on budget.
Navy tees x2, Trailgrip, Montgenevre black (to a guy going to Japan for snow), Hermine off-white.
Delivery 43 units.

The jacarandas are out, tees and polos are what people want. Any update on the swap list?

Chloe"""),
]
