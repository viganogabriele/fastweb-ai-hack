# -*- coding: utf-8 -*-
from common import person

LANG = "en"
F = "AMER_Mitchell_US_Canada"
TZ = "America/New_York"
L = person("mitchell")
TO = [person("davidson")]

MSGS = [
dict(key="l36", folder=F, file="2026-09-06_2041_weekly_wk36_Mitchell", frm=L, to=TO, cc=None, tz=TZ, sent="2026-09-06 20:41",
     subj="Weekly recap - Northeast/South/West/Canada - wk 36",
     body="""Mark,

Week ending 9/6. Net sales vs plan:

NYC01 Madison   $301k   +4%
NYC02 SoHo      $167k   -2%
MIA01           $55k    -30%
BHS01           $85k    -23%
ASP01           $25k    -40%
TOR01           C$143k  -26%

Net-net a soft week outside Madison. Miami lost most of Thu-Sat to the AC failure (unit replaced Saturday afternoon, store was at 84F inside, clients walking out). BHS still in summer mode. Aspen is between seasons, expected.
Holiday Monday tomorrow, all stores open regular hours.

Lauren
"""),

dict(key="l37", folder=F, file="2026-09-14_0722_weekly_wk37_Mitchell", frm=L, to=TO, cc=None, tz=TZ, sent="2026-09-14 07:22",
     subj="Weekly recap wk 37",
     body="""Mark - wk 37:

NYC01 $302k -11%
NYC02 $170k -13%
MIA01 $70k -16%
BHS01 $91k -30%
ASP01 $12k -64%
TOR01 C$255k +18%

Highlights / lowlights
- TIFF is a big lift for Yorkville: celebrities, stylists, a lot of walk-in traffic, Émilie's team sold 3 Arnebs to a production crew. +18%.
- Beverly Hills heat wave Tue-Sat, 104F on Thursday. Nobody tries on a down jacket in that. Jersey ok.
- New York soft. Fashion week crowd but not shopping with us.
- Campaign goes live tomorrow (OOH + digital). Agency kickoff call Wednesday, I'll join.

L.
"""),

dict(key="l38", folder=F, file="2026-09-21_0705_weekly_wk38_Mitchell", frm=L, to=TO, cc=None, tz=TZ, sent="2026-09-21 07:05",
     subj="Weekly recap wk 38",
     body="""Mark,

NYC01 $315k  -15%
NYC02 $187k  -13%
MIA01 $69k   -18%
BHS01 $129k  -10%
ASP01 $24k   -32%
TOR01 C$185k -22%

Campaign week 1. The billboards on Houston St and the Madison bus shelters look great, store teams say traffic feels slightly better, maybe a few more "I saw the ad" comments. Comp still negative though. I'd be careful with any big uplift numbers this early.
UNGA starts tomorrow: the Upper East Side will be locked down, expect Madison to suffer most of the week (motorcades, frozen zones on Park and Madison).
TIFF wrapped Sunday, Toronto back to normal.

Lauren
"""),

dict(key="l39", folder=F, file="2026-09-28_0640_weekly_wk39_Mitchell", frm=L, to=TO, cc=None, tz=TZ, sent="2026-09-28 06:40",
     subj="Weekly recap wk 39 + Polaris first read",
     body="""Mark,

NYC01 $263k -36%   (UNGA)
NYC02 $226k -7%
MIA01 $99k  +7%
BHS01 $135k -18%
ASP01 $35k  -9%
TOR01 C$280k +5%

- Madison: as expected, UNGA killed the week. Mon-Thu clients simply could not reach the store, several appointments cancelled. Rebecca rebooked most of them for this week.
- POLARIS launched Thursday in NYC01, NYC02, MIA01, BHS01, TOR01. First read is not great: lots of try-ons, very few sales. The oversized jacket runs small (our clients size up and we don't have XL/XXL depth), and $3,375 for the cape is a hard sell outside of collectors. 4 pieces sold across 5 doors.
- Miami positive for the first time this season, Brazilian clients.

Lauren
"""),

dict(key="l39_md", folder=F, file="2026-09-29_1012_RE_weekly_wk39_Davidson", frm=person("davidson"), to=[L], cc=None, tz=TZ, sent="2026-09-29 10:12",
     subj="RE: Weekly recap wk 39 + Polaris first read", reply_to="l39",
     body="""Lauren - thanks. The agency deck circulating says +22% attributed uplift for the US/UK campaign so far. Does that match what you see in the stores? I need a sense check before the global call.
Mark
"""),

dict(key="l39_lm", folder=F, file="2026-09-29_1155_RE_weekly_wk39_Mitchell", frm=L, to=[person("davidson")], cc=None, tz=TZ, sent="2026-09-29 11:55",
     subj="RE: Weekly recap wk 39 + Polaris first read", reply_to="l39_md",
     body="""Honestly, no. Door counts at NYC02 and BHS01 are up a few points vs the weeks before launch, and store teams mention the ads occasionally. If I had to put a number on it, mid single digits at best. "Attributed" in their model means anyone who saw a digital ad and later bought, which in our client base is basically everyone who was going to buy anyway.
Happy to walk you through the door count data.
L.
"""),

dict(key="l4041", folder=F, file="2026-10-13_0730_weekly_wk40-41_Mitchell", frm=L, to=TO, cc=None, tz=TZ, sent="2026-10-13 07:30",
     subj="Weekly recap wk 40 + 41 (combined, sorry)",
     body="""Mark,

Apologies for missing last week's recap, I was in Toronto and Aspen. Two weeks together:

           wk40           wk41
NYC01   $380k -16%    $491k  -1%
NYC02   $286k  +9%    $246k -12%
MIA01   $71k  -28%    $84k  -17%
BHS01   $192k  +9%    $188k  -3%
ASP01   $20k  -45%    $34k  -24%
TOR01   C$194k -36%   C$227k -29%

Key points:
1. TIB zipper defect. Returns started the week of 9/28 (NYC01 10, NYC02 8, Toronto 5 in wk40). The QA alert came on 10/5, procedure now in place. Clients are annoyed but the exchange is easy when we have the size.
2. NYC02 POS outage on Monday (registers down ~2-5:30pm). Team sold on manual slips and keyed them the next morning, so the day-level numbers are off: Monday understated, Tuesday overstated. Week total is right.
3. ILVARO: since the K-pop photos at Paris fashion week we get requests for the black and off-white in SoHo and Madison, a few for pink (we have none in SoHo, and NYC01 has 11 pink in transit for this week, not sure who asked for them). Small numbers but new.
4. Toronto is the concern: three weeks in a row at -30% or worse. Émilie says it's the competition at home (the Canadian brands are everywhere this fall) and the weather is still mild. Visiting again in November.
5. Columbus Day today, normal hours.

Lauren
"""),

dict(key="l42", folder=F, file="2026-10-19_0652_weekly_wk42_Mitchell", frm=L, to=TO, cc=None, tz=TZ, sent="2026-10-19 06:52",
     subj="Weekly recap wk 42",
     body="""Mark,

NYC01 $531k  +1%
NYC02 $235k  -21%
MIA01 $67k   -40%
BHS01 $174k  -17%
ASP01 $54k   +14%
TOR01 C$247k -28%

- Madison back on plan with the first cool days, Maya and Montcla driving it.
- Black Maire is now the most requested item we don't have: 7 in SoHo, 11 in Toronto, a few in BHS. Mostly younger clients, some Korean students in Toronto. We have beige/navy, they don't want it.
- Aspen waking up, pre-season locals and second-home owners.
- Miami very soft, -40. Daniela says the tourists haven't arrived yet; it's early.
- POLARIS: 9 pieces sold total across 5 doors in 4 weeks. I'd support moving the remaining stock to Asia where I hear it's selling.

Lauren
"""),
]
