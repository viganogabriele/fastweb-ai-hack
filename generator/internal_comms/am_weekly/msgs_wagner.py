# -*- coding: utf-8 -*-
from common import person

LANG = "de"
F = "EMEA_Wagner_DACH"
TZ = "Europe/Berlin"
S = person("wagner")
TO = [person("valli")]
CC = [person("engel")]

MSGS = [
dict(key="w36", folder=F, file="2026-09-07_0731_KW36_DACH_Wagner", frm=S, to=TO, cc=CC, tz=TZ, sent="2026-09-07 07:31",
     subj="KW 36 DACH",
     body="""Hallo Francesca,

anbei der Wochenrückblick KW36.

Ampel:
MUN01  gelb   107 T€ / -13 %
BER01  rot     50 T€ / -26 %
ZRH01  rot     CHF 69 T / -27 %
STM01  rot     CHF 29 T / -31 %

Kommentar: Spätsommer, 25 Grad in München, Kunden kaufen Polos und Sneaker, Daunen bewegen sich kaum. KaDeWe insgesamt schwach laut Abteilungsleitung (Haus -9 %). In St. Moritz Nebensaison, normal.
Lieferung MUN01 vom 03.09. kam erst am 05.09. (Spedition), Neuheiten deshalb erst Samstag auf der Fläche.

VG Stefan
"""),

dict(key="w37", folder=F, file="2026-09-14_0745_KW37_DACH_Wagner", frm=S, to=TO, cc=CC, tz=TZ, sent="2026-09-14 07:45",
     subj="Wochenbericht KW37 DACH",
     body="""Hallo Francesca,

Wochenbericht KW37 im Anhang (Word).
Kurz: alle Filialen unter Budget, Wetter zu warm. ZRH etwas besser.

Grüße
Stefan
""",
     docx=dict(name="Wochenbericht_DACH_KW37.docx", title="Wochenbericht DACH – KW 37 (07.–13.09.2026)", author="Stefan Wagner",
               table=[["Filiale", "Umsatz netto", "vs Budget", "Ampel", "Bemerkung"],
                      ["MUN01 München", "109 T€", "-22 %", "rot", "Lieferung 12.09. verspätet (2 Tage)"],
                      ["BER01 KaDeWe", "68 T€", "-15 %", "gelb", "-"],
                      ["ZRH01 Zürich", "CHF 98 T", "-13 %", "gelb", "Neuheiten gut angenommen"],
                      ["STM01 St. Moritz", "CHF 39 T", "-9 %", "gelb", "Wochenendgäste"]],
               paras=["Neuheiten: AMALIA und IRIDIA werden viel anprobiert, Verkäufe noch zurückhaltend. ARTEM: erster Umtausch wegen Größe in Zürich.",
                      "Personal: BER01 eine Kollegin in Elternzeit ab Oktober, Ersatz wird gesucht.",
                      "Nächste Woche: Besuch MUN01 und Wiesn-Start Samstag (viel Publikum in der Stadt)."])),

dict(key="w38", folder=F, file="2026-09-21_0712_KW38_DACH_Wagner", frm=S, to=TO, cc=CC, tz=TZ, sent="2026-09-21 07:12",
     subj="KW 38 DACH",
     body="""Hallo Francesca,

MUN01 grün 171 T€ / +6 %
BER01 grün  90 T€ / +4 %
ZRH01 gelb  CHF 116 T / -6 %
STM01 rot   CHF 24 T / -40 %

Gute Woche in München und Berlin. Wiesn-Start am Samstag: viele Touristen in der Maximilianstraße, eher Trachten als Daunen, aber die Logo-Hoodies und Mützen laufen. In Berlin hat das KaDeWe eine Hausaktion gemacht (Late Night Shopping Freitag), hat geholfen.
St. Moritz: sehr ruhig, Sabrina bereitet schon die Zwischensaison vor (Schließung ab 19.10.).

VG Stefan
"""),

dict(key="w38_fv", folder=F, file="2026-09-22_1018_RE_KW38_Valli", frm=person("valli"), to=[S], cc=CC, tz=TZ, sent="2026-09-22 10:18",
     subj="RE: KW 38 DACH", reply_to="w38",
     body="""Hi Stefan,
thanks. Small request: from now on could you send the weekly in English, or at least add a short English summary? From October the recaps are shared in the global retail call and Mark and Andrew's teams read them too.
Thank you!
Francesca
"""),

dict(key="w38_sw", folder=F, file="2026-09-22_1102_RE_KW38_Wagner", frm=S, to=[person("valli")], cc=CC, tz=TZ, sent="2026-09-22 11:02",
     subj="RE: RE: KW 38 DACH", reply_to="w38_fv", quote=False,
     body="""Hi Francesca,
of course, no problem, from next week in English.
Best regards
Stefan
"""),

dict(key="w39", folder=F, file="2026-09-28_0805_weekly_DACH_wk39_Wagner", frm=S, to=TO, cc=CC, tz=TZ, sent="2026-09-28 08:05",
     subj="Weekly DACH week 39",
     body="""Hello Francesca,

here the weekly for week 39.

MUN01 148 T€, -20% (red)
BER01 72 T€, -25% (red)
ZRH01 CHF 119 T, -15% (yellow)
STM01 CHF 20 T, -55% (red)

Comments:
- Weather still too warm for the season, 20 degrees in Munich, the clients are not in the mood for down jackets.
- ASTRA launched Thursday in MUN01 and STM01. The reaction is not good: the clients try it and find it too small and too expensive. Until now 1 balaclava sold in Munich, nothing in St. Moritz.
- MUN01: black AUREA is missing since one week, some requests (not many).
- Oktoberfest: many people in the city but not our clients.

Best regards
Stefan
"""),

dict(key="w40", folder=F, file="2026-10-05_0738_KW40_DACH_Wagner", frm=S, to=TO, cc=CC, tz=TZ, sent="2026-10-05 07:38",
     subj="KW 40 DACH (sorry, auf Deutsch)",
     body="""Hallo Francesca,

sorry, diese Woche wieder auf Deutsch, auf Englisch brauche ich doppelt so lange. Bericht hängt an, Kurzfassung:

MUN01 141 T€ -4 %, BER01 74 T€ -6 %, ZRH01 CHF 167 T +9 %, STM01 CHF 36 T -23 %.

Zürich profitiert von den chinesischen Feiertagen (Gruppen aus Luzern / Jungfraujoch auf der Bahnhofstrasse). Leider waren wir nicht auf der Liste für die Mandarin-Unterstützung, Reto hat mit einer Studentin aus dem eigenen Netzwerk improvisiert.
VEL Reißverschluss: in Zürich 7 Retouren, in München 1, Berlin 1. Keine Info von der Qualität, wir sammeln die Teile.
BER01: Tag der Deutschen Einheit am Samstag, Haus voll, aber wenig Umsatz bei uns.

VG Stefan
""",
     docx=dict(name="Wochenbericht_DACH_KW40.docx", title="Wochenbericht DACH – KW 40 (28.09.–04.10.2026)", author="Stefan Wagner",
               table=[["Filiale", "Umsatz netto", "vs Budget", "Ampel"],
                      ["MUN01", "141 T€", "-4 %", "gelb"], ["BER01", "74 T€", "-6 %", "gelb"],
                      ["ZRH01", "CHF 167 T", "+9 %", "grün"], ["STM01", "CHF 36 T", "-23 %", "rot"]],
               paras=["Ware: AUREA schwarz in MUN01 fast leer, Nachlieferung laut Replenishment erst nach dem 16.10.",
                      "ASTRA: weiterhin kaum Abverkauf in MUN01 (2 Teile seit Launch). Ich würde die Ware gerne an Filialen mit Nachfrage abgeben.",
                      "VEL: Retouren wegen Reißverschluss (Schieber löst sich). Teile liegen im Lager, Rücksendung offen."])),

dict(key="w41", folder=F, file="2026-10-12_0745_KW41_DACH_Wagner", frm=S, to=TO, cc=CC, tz=TZ, sent="2026-10-12 07:45",
     subj="KW 41 DACH + Wetter",
     body="""Hallo Francesca,

MUN01 165 T€ -26 % rot
BER01 129 T€ +17 % grün
ZRH01 CHF 157 T -4 % gelb
STM01 CHF 42 T -18 % rot

Wichtig für diese Woche: der Wetterdienst meldet ab heute einen massiven Kälteeinbruch, in München Höchstwerte 2–5 Grad und Schnee möglich ab Mittwoch, in der Schweiz Schnee bis 1000 m. Das ist genau der Moment, auf den wir warten. Bitte Replenishment Heavy Down (NOVA, MONTELUCE, AUREA, LIVIANA), Mützen und Handschuhe für MUN01, BER01 und ZRH01 priorisieren. Die Filialen haben jeweils nur 1–2 Teile pro Größe bei den Ikonen.

VEL: Qualitätsalarm erhalten, wird umgesetzt.
ARTEM: das Team empfiehlt inzwischen eine Nummer kleiner, das funktioniert.

VG Stefan
"""),

dict(key="w42", folder=F, file="2026-10-19_0702_KW42_DACH_Wagner", frm=S, to=TO, cc=CC, tz=TZ, sent="2026-10-19 07:02",
     subj="KW 42 DACH – Wintereinbruch",
     body="""Hallo Francesca,

was für eine Woche.

MUN01 304 T€ / +26 % grün
BER01 176 T€ / +50 % grün
ZRH01 CHF 294 T / +41 % grün
STM01 CHF 57 T / -1 % gelb

Am Mittwoch der erste Schnee in München, Kunden standen um 10 Uhr vor der Tür. Ausverkauft u.a. Vlogo Beanie (schwarz, navy, weiß), Winter Gloves, NOVA schwarz Gr. 3/4, MONTELUCE grau in mehreren Größen. AUREA schwarz fehlt weiterhin überall, 14 Anfragen in MUN01 notiert.

Berlin +50 %: neben dem Wetter hat sicher auch das neue Schaufenster geholfen, das Jana am Dienstag umgebaut hat (Schneelandschaft mit NOVA und Beanies), die Kunden sind gezielt deswegen reingekommen. Würde das gerne auf andere Häuser übertragen.

St. Moritz ist seit heute für die Zwischensaison geschlossen. Die Restware Heavy Down und Accessoires geht nach Absprache mit Luca Ferrari diese Woche an MUN01 und ZRH01.

ASTRA: unverändert schwach in MUN01 (zu klein, zu teuer).

VG Stefan
"""),

dict(key="w42c", folder=F, file="2026-10-19_1144_Korrektur_KW42_Wagner", frm=S, to=TO, cc=CC, tz=TZ, sent="2026-10-19 11:44",
     subj="Korrektur: KW 42 DACH", reply_to="w42", quote=False,
     body="""Korrektur: ZRH01 KW42 waren CHF 249 T, nicht 294 T (Zahlendreher). Prozent (+41 %) stimmt.
Sorry
Stefan
"""),
]
