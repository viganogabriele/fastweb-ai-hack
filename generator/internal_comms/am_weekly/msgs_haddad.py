# -*- coding: utf-8 -*-
from common import person

LANG = "en"
F = "EMEA_Haddad_MiddleEast"
TZ = "Asia/Dubai"
O = person("haddad")
TO = [person("valli")]

MSGS = [
dict(key="o36", folder=F, file="2026-09-07_0915_DXB_weekly_wk36_Haddad", frm=O, to=TO, cc=None, tz=TZ, sent="2026-09-07 09:15",
     subj="DXB01 weekly wk36",
     body="""Dear Francesca,

Dubai Mall wk36: AED 423k, -29% vs budget.

Still summer, 44 degrees, the mall is full in the evenings but mostly families and tourists from India and Europe, low spend. Local clients come back after school starts. Jersey, sneakers and caps are what sells. Delivery of 30 Aug arrived 1 Sep.

Regards,
Omar Haddad
Area Manager Middle East
"""),

dict(key="o37", folder=F, file="2026-09-14_0902_DXB_weekly_wk37_Haddad", frm=O, to=TO, cc=None, tz=TZ, sent="2026-09-14 09:02",
     subj="DXB01 weekly wk37",
     body="""Dear Francesca,

AED 460k, -29%.
Saudi clients started to arrive for the weekend. Many requests for polos in navy and black that we don't have in M/L. Another delivery late (3 days), Rania escalated with the forwarder.

Regards,
Omar
"""),

dict(key="o38", folder=F, file="2026-09-21_0848_DXB_weekly_wk38_Haddad", frm=O, to=TO, cc=None, tz=TZ, sent="2026-09-21 08:48",
     subj="DXB01 weekly wk38",
     body="""Dear Francesca,

Better week: AED 621k, -8% vs budget. Saudi National Day is on the 23rd so we expect a strong week also next week.
Knitwear not interesting for our clients, but we sold well the Bady and some Maya for clients travelling to Europe and London for the winter.
I will be on annual leave from 24/09 to 04/10, Rania will send the closing reports as usual.

Regards,
Omar
"""),

dict(key="o40", folder=F, file="2026-10-05_1010_DXB_weekly_wk39-40_Haddad", frm=O, to=TO, cc=None, tz=TZ, sent="2026-10-05 10:10",
     subj="DXB01 weekly wk40 (wk39 incl.)",
     body="""Dear Francesca,

back from leave. Wk39 AED 632k -8%, wk40 AED 508k -30%.

Wk40 was weak after the Saudi holiday. 7 returns of the TIB vest for the zipper in one week, clients were not happy, one of them is a VIC. Rania kept the pieces in the back. Please advise the procedure.

Regards,
Omar
"""),

dict(key="o41", folder=F, file="2026-10-12_0830_DXB_wk41_Haddad", frm=O, to=TO, cc=None, tz=TZ, sent="2026-10-12 08:30",
     subj="DXB01 wk41",
     body="""Francesca, wk41 AED 738k, -1%. Good week, temperature finally below 35 and the locals are back in the mall. TIB procedure received, thanks.
Omar

Sent from my iPhone
"""),

dict(key="o42", folder=F, file="2026-10-19_0905_DXB_weekly_wk42_Haddad", frm=O, to=TO, cc=None, tz=TZ, sent="2026-10-19 09:05",
     subj="DXB01 weekly wk42",
     body="""Dear Francesca,

AED 674k, -16%.

Interesting this week: several clients asking for the black Maire (5 that Rania noted), a few of them Korean tourists and a Saudi lady who saw it in a Korean series. We have none in black, only beige and white.
Also 2 Arneb exchanges for a smaller size.
Winter travel season starting, clients buying for London and Switzerland holidays.

Regards,
Omar
"""),
]
