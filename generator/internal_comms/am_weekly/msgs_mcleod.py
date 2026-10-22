# -*- coding: utf-8 -*-
from common import person

LANG = "en"
F = "EMEA_McLeod_UK_North"
TZ = "Europe/London"
FM = person("mcleod")
TO = [person("valli")]
CC = [person("ashby")]

MSGS = [
dict(key="f36", folder=F, file="2026-09-06_1922_weekly_wk36_McLeod", frm=FM, to=TO, cc=CC, tz=TZ, sent="2026-09-06 19:22",
     subj="Weekly UK & North - wk36",
     body="""Hi Francesca,

wk36 in brief:

LON01  £210k  -11% vs bud
LON02  £122k  -16%
AMS01  €78k   -18%
CPH01  DKK 382k  -19%

- Back to school week, London quiet midweek, Saturday decent.
- Harrods: footfall in the store down on LY according to their own numbers, not just us.
- AMS/CPH: nothing to report, tees and polos still the top sellers, which tells you everything about the weather.

Cheers, F
"""),

dict(key="f37", folder=F, file="2026-09-13_2012_weekly_wk37_McLeod", frm=FM, to=TO, cc=CC, tz=TZ, sent="2026-09-13 20:12",
     subj="Weekly UK & North - wk37",
     body="""Hi F,

LON01 £283k +3%
LON02 £147k -7%
AMS01 €94k -16%
CPH01 DKK 456k -17%

Bond St had a good week with the new collection, Ambrine in brown is the piece everyone photographs (we have 2 sizes, naturally). Olivia asked if we can get more brown 1-2, I said I'd ask but not to hold her breath.
First Arneb exchange in Amsterdam for size.
Campaign goes live on Tuesday, OOH on Bond St and Sloane St, the agency is very excited.

F
"""),

dict(key="f38", folder=F, file="2026-09-21_0758_weekly_wk38_McLeod", frm=FM, to=TO, cc=CC, tz=TZ, sent="2026-09-21 07:58",
     subj="Weekly UK & North - wk38",
     body="""Morning Francesca,

LON01 £276k  -8%
LON02 £166k  -1%
AMS01 €104k -15%
CPH01 DKK 383k -36% (ouch)

- Campaign live since Tuesday. Bond St window + the buses look great. Too early for numbers.
- LON02: from Friday a wave of young Korean women asking for the black Maire, all with the same photo from a TV drama. Priya says 9 or 10 asked over the weekend. We're running out of black, maybe 4-5 pieces left.
- CPH: a bad week, Mette had 2 people off sick and the weather was lovely, nobody thinking about coats. Not worried yet.

F
"""),

dict(key="f39", folder=F, file="2026-09-28_0812_weekly_wk39_McLeod", frm=FM, to=TO, cc=CC, tz=TZ, sent="2026-09-28 08:12",
     subj="Weekly UK & North - wk39 (+ campaign results)",
     body="""Hi Francesca,

numbers:
LON01 £354k +2%
LON02 £202k +6%
AMS01 €111k -20%
CPH01 DKK 570k -12%

1. Campaign: great news, the agency's first readout came in Friday, +22% uplift on attributed sales in the UK in the first 10 days. Richard is presenting it Thursday. Footfall at Bond St is clearly up, so it's working.
2. Black Maire at Harrods: sold out since Thursday-ish. 30+ requests logged by Priya in the week, almost all Korean tourists (Chuseok holidays I'm told). It's real, it's every day, and they don't want beige. Please, please push for Harrods on the next delivery.
3. Golden Week next week, Harrods expecting big Chinese numbers. We are not on Matteo's list for Mandarin support, can we fix that? Harrods will lend us someone a few hours a day but that's it.
4. AMS still behind, Sanne thinks the shop is too "summer" still, VM change planned.

Cheers, F
"""),

dict(key="f39_fv", folder=F, file="2026-09-28_1340_RE_weekly_wk39_Valli", frm=person("valli"), to=[FM], cc=CC, tz=TZ, sent="2026-09-28 13:40",
     subj="RE: Weekly UK & North - wk39 (+ campaign results)", reply_to="f39",
     body="""Fiona, thanks. On the 22%: is that net of what we would have done anyway? LON01 is +2% vs budget for the week, I struggle to see +22% in our numbers. Can you ask Richard how the agency calculates it?
Mandarin support for LON02: I'll speak to Matteo.
F.
"""),

dict(key="f39_fm", folder=F, file="2026-09-28_1612_RE_weekly_wk39_McLeod", frm=FM, to=[person("valli")], cc=CC, tz=TZ, sent="2026-09-28 16:12",
     subj="RE: RE: Weekly UK & North - wk39 (+ campaign results)", reply_to="f39_fv",
     body="""Fair point. It's the agency's model (attributed = clients who were "exposed" to the digital campaign and then bought), not a like-for-like. Richard will ask them for the methodology. My gut feeling is footfall is up a bit, not 22% though.
F
"""),

dict(key="f40", folder=F, file="2026-10-05_0745_weekly_wk40_McLeod", frm=FM, to=TO, cc=CC, tz=TZ, sent="2026-10-05 07:45",
     subj="Weekly UK & North - wk40",
     body="""Hi Francesca,

LON01 £330k -15%
LON02 £188k -9%
AMS01 €135k -13%
CPH01 DKK 559k -24%

- Golden Week: Harrods very busy with Chinese clients (Priya reckons over a quarter of tickets), but without black Maire and with no Mandarin speaker of our own we lost a lot. 35-ish black Maire requests logged again.
- TIB zipper returns: 13 at Bond St this week, 6 at Harrods. The slider just comes off. Nobody from quality has told us anything, we're putting them aside. Looks like a batch issue to me.
- CPH: Mette is down to a skeleton team (2 sick, 1 resigned), store running on reduced hours 11-17 for two weeks. Recruitment open.
- Bond St private client evening on Thursday 8th, 45 confirmed. Olivia is on it.

F
"""),

dict(key="f41", folder=F, file="2026-10-12_0802_weekly_wk41_McLeod", frm=FM, to=TO, cc=CC, tz=TZ, sent="2026-10-12 08:02",
     subj="Weekly UK & North wk41",
     body="""Hi Francesca

LON01 £522k +27%  <- client evening
LON02 £231k +6%
AMS01 €121k -28%
CPH01 DKK 647k -16%

Thursday's private evening at Bond St was a big success: 45 guests, about 25 bought, several £5k+ tickets, two Polaris capes (the only ones we've sold!). Olivia and Daniel did an amazing job. Thank you for the champagne budget.
Bond St has now also run out of black Maire (last ones went at the event) and Olivia logged almost 30 requests this week. So now we have the problem in both London stores.
Harrods still strong on Chinese until Thursday.
CPH back to normal hours, the new SA started.
AMS weak, the VM change didn't do much. Rain all week.

On the campaign, Richard's slide for the global call says +22% uplift, I'll leave the methodology debate to the clever people.

F
"""),

dict(key="f42", folder=F, file="2026-10-19_0731_weekly_wk42_McLeod", frm=FM, to=TO, cc=CC, tz=TZ, sent="2026-10-19 07:31",
     subj="Weekly UK & North wk42 - the cold is here",
     body="""Morning,

LON01 £512k +13%
LON02 £252k +8%
AMS01 €181k -2%
CPH01 DKK 949k +11%

- Finally proper weather: CPH and AMS had 3-5 degrees from Tuesday, CPH best week of the season. Beanies and gloves gone in CPH, Mette has asked for a transfer from LON01.
- London milder but the heavy down moved, Maya and Montcla mostly.
- Black Maire: still zero in both London stores, LON02 logged 32 requests, LON01 10. I heard the DC received stock on Friday. Harrods needs to be in the first wave, they have been asking for a month.
- LON01 received 12 pink Ilvaro last Monday. Sold 3. Nobody asks for pink in London, I'm sure Seoul would take them tomorrow.
- TIB returns slowing down now.

F
"""),
]
