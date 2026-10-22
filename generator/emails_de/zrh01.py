# -*- coding: utf-8 -*-
"""ZRH01 - Zürich Bahnhofstrasse. Hand-authored closing emails in Swiss Standard German (no ß, CHF with
apostrophes, Helvetismen).

Writers: Reto Ammann (SM, fixed "Tagesrapport" form, formal, "Freundliche Grüsse"), Lea Baumgartner (ASM, warm,
"Hoi zäme", "Liebi Grüess", iPhone on Saturdays), Ying Zhang (Sales Advisor, Mandarin speaker, non-native German,
writes during Golden Week).
"""
DOM = "moncler-retail.example"

PEOPLE = {
    "ra": dict(name="Reto Ammann", addr=f"reto.ammann@{DOM}", mailer="outlook",
               footer="\n\nReto Ammann\nStore Manager\nMoncler Zürich | Bahnhofstrasse\nTel. +41 44 211 07 30"),
    "lb": dict(name="Lea Baumgartner", addr=f"lea.baumgartner@{DOM}", mailer="outlook"),
    "yz": dict(name="Ying Zhang", addr=f"ying.zhang@{DOM}", mailer="outlook"),
    "store": dict(name="Moncler Zürich", addr=f"zrh01.store@{DOM}", mailer="outlook"),
}

EMAILS = [
dict(id="0831", d="2026-08-31 19:37", w="ra", subj="Tagesrapport ZRH01 – 31.08.2026", body="""
Guten Abend zusammen

Umsatz: CHF 7'421 (Budget CHF 11'100)
Frequenz: 99 / Bons: 7

Bemerkungen:
- Zwei Retouren: Maya Gr. 2 (Qualität, Druckknopf am Kragen ausgerissen) und Trailgrip W 37 (Kundin hat es sich anders überlegt)
- Nicht an Lager und nachgefragt: Maya navy 4, Ecrins 4
- Kundschaft: viele Schweizer, ein paar Amerikaner, eine russische Familie

Freundliche Grüsse
Reto Ammann
"""),

dict(id="0901", d="2026-09-01 19:41", w="ra", subj="Tagesrapport ZRH01 – 01.09.2026", body="""
Guten Abend zusammen

Umsatz: CHF 6'430 (Budget CHF 10'870)
Frequenz: 77 / Bons: 10

Bemerkungen:
- Ruhiger Tag, fast nur Kleinteile (Schal, Beanie, Polo, T-Shirt)
- Montgenevre navy 7 nachgefragt, nicht vorhanden

Freundliche Grüsse
Reto Ammann
"""),

dict(id="0902", d="2026-09-02 19:52", w="lb", subj="Abschluss Bahnhofstrasse 2.9.", body="""
Hoi zäme

Heute CHF 8'540, Budget wäre 11'060 gewesen. Rucksack, Schal, Polo, zwei Shirts.

Eine Kundin aus Dubai wollte die Trailgrip W in offwhite, 36 und 38 – beides nicht da. Schade, sie hätte beide Grössen probiert.
Maire schwarz 0 und Tib schwarz 5 sind jetzt auf null.

Liebi Grüess
Lea
"""),

dict(id="0903", d="2026-09-03 19:40", w="ra", subj="Tagesrapport ZRH01 – 03.09.2026", body="""
Guten Abend zusammen

Umsatz: CHF 13'001 (Budget CHF 16'120)
Frequenz: 117 / Bons: 9

Bemerkungen:
- Mehrere indische Familien im Laden (Ferien in der Schweiz), zwei davon haben eingekauft
- Nachgefragt: Tib schwarz 2, Tricot Cardigan grau S
- Retoure Bady Gr. 1 (Geschenk)

Freundliche Grüsse
Reto Ammann
"""),

dict(id="0904", d="2026-09-04 19:45", w="ra", subj="Tagesrapport ZRH01 – 04.09.2026", body="""
Guten Abend zusammen

Umsatz: CHF 9'700 (Budget CHF 19'110)
Frequenz: 150 / Bons: 5

Bemerkungen:
- Sehr viel Laufkundschaft, aber Conversion nur gut 3 %. Viele Touristen, die nur fotografieren.
- Lieferung pünktlich eingetroffen (98 Teile), Ware ist verräumt
- Bady schwarz 2x verkauft

Freundliche Grüsse
Reto Ammann
"""),

dict(id="0905", d="2026-09-05 18:42", w="lb", subj="Abschluss Samstag 5.9.", mailer="iphone", body="""
Hoi zäme

CHF 23'622 heute, Budget 25'520. Ganz ok für einen Samstag mit Wetter wie im Juli.

Hoodies navy 4x, Beanies navy 3x, Polo schwarz 3x. Beanie navy ist jetzt aus, und eine Kundin hat genau die noch gewollt. Montgenevre navy 3 auch gefragt.
Tricot Cardigan M zurück (anders überlegt).

Schöne Sonntag
Lea

Von meinem iPhone gesendet
"""),

dict(id="0907", d="2026-09-07 19:33", w="ra", subj="Tagesrapport ZRH01 – 07.09.2026", body="""
Guten Abend zusammen

Umsatz: CHF 5'890 (Budget CHF 13'530)
Frequenz: 84 / Bons: 7

Bemerkungen:
- Schwacher Montag, ein Viertel der Kunden aus Indien, wenig Kaufkraft
- Beanie navy wieder gefragt (zweite Anfrage seit Samstag), bitte nachliefern
- Hermine schwarz 0 und Bady schwarz 0 sind auf null

Freundliche Grüsse
Reto Ammann
"""),

dict(id="0909", d="2026-09-09 19:55", w="lb", subj="Abschluss Bahnhofstrasse 9.9.", body="""
Hoi zäme

Gestern ist kein Rapport rausgegangen, Reto war an der Schulung in Bern und ich habs vergessen, sorry.

Heute CHF 10'310 (Budget 16'320).
Trailgrip GTX schwarz 3x, Trailgrip W 2x, Polo schwarz 2x.

Drei Retouren, alle Grösse: Maya 3, Cable Knit S, Trailgrip GTX 40.
Nachgefragt und nicht da: Bady offwhite 4, Ilvaro offwhite 2 und – zum dritten Mal – Beanie navy.

Liebi Grüess
Lea
"""),

dict(id="0910", d="2026-09-10 19:38", w="ra", subj="Tagesrapport ZRH01 – 10.09.2026", body="""
Guten Abend zusammen

Umsatz: CHF 15'610 (Budget CHF 17'710)
Frequenz: 110 / Bons: 12

Bemerkungen:
- Beanie schwarz 4x, Logo Cardigan schwarz 2x
- Nachgefragt: Arneb schwarz 7 (die grösste Grösse ist bei uns gar nicht im Sortiment), Logo Cardigan navy XS, Trailgrip GTX 46
- Trailgrip GTX schwarz 42 und 43 auf null

Freundliche Grüsse
Reto Ammann
"""),

dict(id="0911", d="2026-09-11 19:44", w="ra", subj="Tagesrapport ZRH01 – 11.09.2026", body="""
Guten Abend zusammen

Umsatz: CHF 14'460 (Budget CHF 21'140)
Frequenz: 174 / Bons: 9

Bemerkungen:
- Lieferung pünktlich (114 Teile)
- Hohe Frequenz, aber sehr tiefe Conversion (gut 5 %)
- Rosiere schwarz 2x verkauft, die neue Jacke wird gut angenommen
- Retouren: Cable Knit XXL und T-Shirt XL, beide zu gross

Freundliche Grüsse
Reto Ammann
"""),

dict(id="0912", d="2026-09-12 18:39", w="lb", subj="Abschluss Sa 12.9.", mailer="iphone", body="""
Hoi zäme

Super Samstag! CHF 34'690, Budget 30'190.

Beanies schwarz 3x, T-Shirts weiss 3x, Schals, Gürteltaschen, Crewneck. Viele Chinesen und Amerikaner.
Nicht da: Ecrins 7, Tib offwhite 2, Tricot Cardigan navy M.
Ein Polo M zurück (zu gross).

Liebi Grüess
Lea

Von meinem iPhone gesendet
"""),

dict(id="0914", d="2026-09-14 19:31", w="ra", subj="Tagesrapport ZRH01 – 14.09.2026", body="""
Guten Abend zusammen

Umsatz: CHF 4'660 (Budget CHF 15'240)
Frequenz: 91 / Bons: 5

Bemerkungen:
- Sehr schwacher Tag, zusätzlich vier Retouren, die den Umsatz drücken:
  Crewneck M (anders überlegt), Beanie (Grösse), Schal (Farbe) und Arneb Gr. 4, getauscht gegen Gr. 3. Der Arneb fällt deutlich gross aus, wir empfehlen ab sofort eine Nummer kleiner.
- Nachgefragt: Polo schwarz L, Polo weiss M

Freundliche Grüsse
Reto Ammann
"""),

dict(id="0915", d="2026-09-15 19:46", w="ra", subj="Tagesrapport ZRH01 – 15.09.2026", body="""
Guten Abend zusammen

Umsatz: CHF 17'590 (Budget CHF 15'580)
Frequenz: 106 / Bons: 10

Bemerkungen:
- Gäste aus Saudi-Arabien und den Emiraten, Tib offwhite 2x und Rollkragen braun
- Polo schwarz L schon wieder gefragt (zweiter Tag), dazu Crewneck schwarz XXL und Trailgrip GTX 42
- Hermine schwarz 1/2 und Karakorum schwarz 4 sind ausverkauft

Freundliche Grüsse
Reto Ammann
"""),

dict(id="0916", d="2026-09-16 19:49", w="lb", subj="Abschluss Bahnhofstrasse 16.9.", body="""
Hoi zäme

CHF 19'830 (Budget 16'280), schöner Mittwoch.

Tib 4x (2 schwarz, 2 navy), Logo Cardigan 2x, Maya navy 2x.
Nicht da: Arneb schwarz 5, Tricot Cardigan navy M (ist jetzt schon die zweite Anfrage).
Arneb schwarz 3 und 5 sind auf null.

Liebi Grüess
Lea
"""),

dict(id="0917", d="2026-09-17 19:42", w="ra", subj="Tagesrapport ZRH01 – 17.09.2026", body="""
Guten Abend zusammen

Umsatz: CHF 20'040 (Budget CHF 19'630)
Frequenz: 126 / Bons: 13

Bemerkungen:
- Budget erreicht. Hoodies schwarz 3x, T-Shirts weiss 3x, Karakorum schwarz 2x
- Nachgefragt: Montgenevre grau 6, Polo schwarz L (dritte Anfrage diese Woche!)
- Maya navy 4 und Karakorum schwarz 3 auf null

Freundliche Grüsse
Reto Ammann
"""),

dict(id="0918", d="2026-09-18 19:39", w="ra", subj="Tagesrapport ZRH01 – 18.09.2026", body="""
Guten Abend zusammen

Umsatz: CHF 24'820 (Budget CHF 23'180)
Frequenz: 167 / Bons: 18

Bemerkungen:
- Lieferung pünktlich (134 Teile), die Polos und Beanies sind wieder da
- Beanie schwarz 5x (!), Handschuhe 2x, Karakorum navy 2x
- Nachgefragt: Montgenevre navy 3

Freundliche Grüsse
Reto Ammann
"""),

dict(id="0919", d="2026-09-19 18:51", w="lb", subj="Abschluss Sa 19.9.", mailer="iphone", body="""
Hoi zäme

CHF 29'073, Budget 33'400. Viel los, viele Gäste aus den Emiraten, aber eher geschaut als gekauft.

Tricot Cardigan schwarz 3x, Hoodie navy 3x, Tib schwarz 2x, Chambre 2x.
Nicht da: Hermine offwhite 0, Ambrine schwarz 2, Trailgrip W offwhite 35.

En schöne Sunntig
Lea

Von meinem iPhone gesendet
"""),

dict(id="0921", d="2026-09-21 19:35", w="ra", subj="Tagesrapport ZRH01 – 21.09.2026", body="""
Guten Abend zusammen

Umsatz: CHF 11'280 (Budget CHF 17'760)
Frequenz: 98 / Bons: 10

Bemerkungen:
- Drei Retouren: Karakorum 3 (anders überlegt), Tib 1 (Grösse) und ein Beanie
- Maya navy 4 erneut nachgefragt, nicht vorhanden
- Maya schwarz 2x verkauft

Freundliche Grüsse
Reto Ammann
"""),

dict(id="0923", d="2026-09-23 19:58", w="lb", subj="Abschluss Bahnhofstrasse 23.9.", body="""
Hoi zäme

CHF 13'835 (Budget 18'180).

Heute viele chinesische Gäste (ca. 20 %), Gürteltaschen 3x, Bady offwhite 2x, Maire navy 2x.
Maya 3 zurück, zu gross.
Nicht da: Karakorum schwarz 3, Crewneck weiss XL.

Gestern hatten wir übrigens CHF 18'533, der Rapport ist offenbar nicht rausgegangen (lag im Postausgang).

Liebi Grüess
Lea
"""),

dict(id="0924", d="2026-09-24 19:44", w="ra", subj="Tagesrapport ZRH01 – 24.09.2026", body="""
Guten Abend zusammen

Umsatz: CHF 20'510 (Budget CHF 21'260)
Frequenz: 137 / Bons: 13

Bemerkungen:
- Genius Polaris heute im Laden: 1x Polaris Oversized schwarz verkauft (Kunde aus Dubai), die Balaclava wurde oft probiert
- Maya schwarz 3x, Handschuhe 2x
- Karakorum 3 zurück (Grösse)
- Nachgefragt: Maya navy 3, Trailgrip GTX grau 43

Freundliche Grüsse
Reto Ammann
"""),

dict(id="0925", d="2026-09-25 19:50", w="ra", subj="Tagesrapport ZRH01 – 25.09.2026", body="""
Guten Abend zusammen

Umsatz: CHF 29'390 (Budget CHF 27'400)
Frequenz: 194 / Bons: 18

Bemerkungen:
- Die Lieferung von heute ist NICHT gekommen. BRT sagt Montag. Das merken wir bereits, viele Grössen fehlen.
- Nachgefragt und nicht vorhanden (7 Anfragen): Maire beige 1, Hermine offwhite 0, Ambrine braun 4, Maya navy 3, Tricot Cardigan schwarz L, Hoodie grau XXL, T-Shirt weiss L
- Hermine offwhite 0 wurde jetzt zum dritten Mal gefragt

Freundliche Grüsse
Reto Ammann
"""),

dict(id="0926", d="2026-09-26 18:47", w="lb", subj="Abschluss Sa 26.9.", body="""
Hoi zäme

Leider nur CHF 25'330 bei Budget 38'210. Ohne die Lieferung fehlen uns überall Grössen und das hat man heute brutal gemerkt.

Nicht bedienen konnten wir:
- Maire schwarz 1 (2 Kundinnen)
- Hoodie schwarz M (2x)
- Ilvaro rosa 00
- Maya navy 3 und 4
- Montgenevre grau 1
- Rosiere 3
- Logo Cardigan schwarz XS

Verkauft: Valbourg schwarz 2x, Beanies, Logo Cardigan, Tib schwarz 2x.

Liebi Grüess
Lea
"""),

dict(id="0928", d="2026-09-28 19:47", w="ra", subj="Tagesrapport ZRH01 – 28.09.2026", body="""
Guten Abend zusammen

Umsatz: CHF 18'060 (Budget CHF 20'300)
Frequenz: 148 / Bons: 10

Bemerkungen:
- Lieferung mit 3 Tagen Verspätung heute Morgen eingetroffen (149 Teile)
- Rollkragen braun 2x verkauft, XS nachgefragt und nicht vorhanden
- Maire schwarz 2x, Bady schwarz 2x
- Bady offwhite 0/1 und Valbourg schwarz 0 weiterhin auf null

Freundliche Grüsse
Reto Ammann
"""),

dict(id="0929", d="2026-09-29 19:53", w="ra", subj="Tagesrapport ZRH01 – 29.09.2026 / Tib Reklamationen", body="""
Guten Abend zusammen

Umsatz: CHF 16'660 (Budget CHF 19'130)
Frequenz: 108 / Bons: 13

Bemerkungen:
- Zwei Tib-Gilets retour, beide mit defektem Reissverschluss: der Schieber rastet nicht mehr ein, das Gilet geht beim Tragen auf. Gr. 5 und Gr. 3, beide in den letzten Wochen gekauft. Wir haben beide zurückerstattet.
  Gibt es dazu bereits eine Info von der Qualitätssicherung?
- Ilvaro schwarz 2x, Polaris Balaclava 1x
- Chamonix XXL zurück (Grösse)
- Nachgefragt: Ilvaro schwarz 00

Freundliche Grüsse
Reto Ammann
"""),

dict(id="0930", d="2026-09-30 19:48", w="ra", subj="Tagesrapport ZRH01 – 30.10.2026", body="""
Guten Abend zusammen

Umsatz: CHF 16'120 (Budget CHF 20'830)
Frequenz: 181 / Bons: 12

Bemerkungen:
- Golden Week hat begonnen: über ein Drittel der Kunden heute aus China, mehrere Reisecars von Luzern
- Dritte Tib-Retoure wegen Reissverschluss (Gr. 4, navy, gekauft im August)
- Logo Cardigan XL zurück (anders überlegt)
- Nachgefragt: Maire offwhite 2, Bady offwhite 0, Polaris Oversized schwarz S, Rollkragen schwarz L, Polo schwarz XL
- Maire schwarz 0/1, Maire navy 1, Cap navy auf null

Freundliche Grüsse
Reto Ammann
"""),

dict(id="1001q", d="2026-10-01 08:12", w="sw", subj="AW: Tagesrapport ZRH01 – 30.10.2026", reply="0930", quote="0930", to=["ra"], cc=["quality", "ops"], body="""
Hallo Reto,

danke. Zu den Tib: bitte schick mir eine Liste mit Grösse/Farbe/Kaufdatum der zurückgegebenen Gilets, ich leite das an Quality weiter. München und Berlin haben auch je einen Fall.
Bis auf Weiteres normal weiterverkaufen, aber beim Verkauf bitte den Reissverschluss kurz prüfen.

Gruss
Stefan
"""),

dict(id="1001r", d="2026-10-01 12:44", w="ra", subj="AW: Tagesrapport ZRH01 – 30.10.2026", reply="1001q", quote="1001q", to=["sw"], cc=["quality", "ops"], body="""
Hallo Stefan

Hier die Liste (Stand heute Mittag):

29.09. – Tib schwarz Gr. 5 – Kauf 11.08.
29.09. – Tib Gr. 3 – Kauf 16.09. (Farbe auf dem Bon nicht ersichtlich, vermutlich schwarz)
30.09. – Tib navy Gr. 4 – Kauf 10.08.
01.10. – Tib offwhite Gr. 4 – Kauf 05.08.

Alle mit dem gleichen Fehler am Schieber. Die Teile liegen im Lager, wir schicken sie gerne an Quality, wenn ihr uns eine Adresse gebt.

PS: Im Rapport von gestern steht im Betreff fälschlicherweise 30.10., gemeint ist natürlich der 30.09.

Freundliche Grüsse
Reto
"""),

dict(id="1001", d="2026-10-01 19:58", w="yz", subj="Abschluss 01.10. Zürich", body="""
Hallo alle

Reto und Lea sind heute beide Nachmittag weg, deshalb schreibe ich den Abschluss.

Umsatz CHF 21'141, Budget 24'950.
Heute sehr viel Kunden aus China (fast die Hälfte), viele Gruppe mit Reisecar. Ich habe den ganzen Tag übersetzt. Viele Tax-free Formular.

Kunden fragen viel, aber wir haben nicht:
- Bady schwarz 0 (2 Kundin)
- Rollkragen schwarz XXL (2 Kunden) und L
- Hermine navy 1
- Montgenevre navy 4
- T-Shirt navy M, Cap navy

Noch zwei Tib zurück wegen Reissverschluss (Gr. 3 und 4). Reto weiss Bescheid.

Freundliche Grüssen
Ying Zhang
Sales Advisor
"""),

dict(id="1002", d="2026-10-02 19:49", w="ra", subj="Tagesrapport ZRH01 – 02.10.2026", body="""
Guten Abend zusammen

Umsatz: CHF 33'422 (Budget CHF 29'040)
Frequenz: 273 / Bons: 19

Bemerkungen:
- Golden Week spürbar, ein Drittel der Kunden aus China. Ying hat sehr viel geholfen.
- Lieferung pünktlich (98 Teile)
- Arneb schwarz 3x, Trailgrip GTX grau 3x, Beanie weiss 3x
- Nachgefragt: Maire schwarz 1, Ilvaro schwarz 1, Montgenevre grau 3, Crewneck weiss XL
- Ilvaro schwarz 0/1 auf null

Freundliche Grüsse
Reto Ammann
"""),

dict(id="1003", d="2026-10-05 08:23", w="lb", subj="Nachtrag Samstag 3.10. – Rekordtag", body="""
Guten Morgen zäme

Am Samstag bin ich nicht mehr zum Schreiben gekommen, deshalb der Nachtrag:

CHF 61'273 (Budget 38'980) – bester Tag seit letzten Dezember! 338 Leute im Laden, 34 Bons.
Mehr als ein Drittel Chinesen, mehrere Cars direkt vor dem Laden, dazu die Schweizer Samstagskundschaft. Ying hatte keine Minute Pause, wir haben am Abend einen Stapel Tax-free Formulare von ca. 2 cm gehabt.

Bestseller: Beanie schwarz 6x, Tib schwarz 4x, Maya schwarz 4x, Hoodie schwarz 4x, Schal schwarz 3x.

Was wir nicht hatten:
- Rosiere schwarz 3 (2 Kunden)
- Maire offwhite 0
- Flammette navy 1
- Ilvaro schwarz 0
- Montgenevre navy 7
- Hoodie navy M, Crewneck schwarz M, T-Shirt weiss M

Und noch zwei Tib-Retouren wegen Reissverschluss (Gr. 2 und 4). Irgendwie verrückt, wir verkaufen 4 und kriegen 2 zurück.

Liebi Grüess
Lea
"""),

dict(id="1005", d="2026-10-05 19:37", w="ra", subj="Tagesrapport ZRH01 – 05.10.2026", body="""
Guten Abend zusammen

Umsatz: CHF 16'338 (Budget CHF 20'740)
Frequenz: 177 / Bons: 13

Bemerkungen:
- Ruhiger nach dem Rekord-Samstag, weniger Chinesen (ca. 17 %), dafür einige russische Gäste
- Arneb Gr. 1 zum Umtausch zurück, auch die 1 war dem Kunden zu weit, kleiner gibt es nicht. Er nimmt jetzt evtl. einen Montgenevre.
- Nachgefragt: Rosiere schwarz 3 (wie am Samstag)

Freundliche Grüsse
Reto Ammann
"""),

dict(id="1006", d="2026-10-06 19:55", w="ra", subj="Tagesrapport ZRH01 – 06.10.2026", body="""
Guten Abend zusammen

Umsatz: CHF 33'000 (Budget CHF 21'250)
Frequenz: 177 / Bons: 17

Bemerkungen:
- Sehr guter Dienstag, wieder viele Gäste aus China (fast 40 %)
- Schals, Beanies weiss, Polo navy, Karakorum navy, Montgenevre navy je 2x
- Viele Anfragen ohne Ware:
  Cap navy (3 Kunden), Maire schwarz 00 und 0, Maire beige 2, Maire offwhite 2, Maya schwarz 5, Karakorum navy 5, Hoodie navy XXL
- Maya schwarz 4/5 auf null

Freundliche Grüsse
Reto Ammann
"""),

dict(id="1007", d="2026-10-07 19:51", w="yz", subj="Abschluss Mittwoch 07.10.", body="""
Hallo alle

Umsatz heute CHF 18'660, Budget 23'110.

Mehr als die Hälfte Kunden aus China, Golden Week ist morgen fertig. Viele Kunden haben nur Fotos gemacht und gefragt nach Grössen die wir nicht haben:
Maire beige 2, Hermine schwarz 4, Bady schwarz 00, Arneb schwarz 2, Peyre 6, Chamonix XL, Cable Knit schwarz XL, Hoodie navy M

Logo Cardigan, Bady schwarz und Tib schwarz je 2x verkauft.

Freundliche Grüssen
Ying
"""),

dict(id="1008", d="2026-10-08 19:46", w="lb", subj="Abschluss Bahnhofstrasse 8.10.", body="""
Hoi zäme

CHF 25'222 (Budget 26'860). Letzter Golden-Week-Tag, immer noch fast die Hälfte Chinesen.

Maire beige 2x, Rosiere schwarz 2x, Flammette navy 2x.

Die Liste mit nicht vorhandener Ware wird leider immer länger:
Hermine schwarz 4, Montgenevre navy 3, Tib navy 2 und 4, Rosiere 3 (das ist jetzt die 4. Anfrage seit Samstag!), Rollkragen braun L, Beanie schwarz, Schal schwarz

Morgen kommt die Lieferung, hoffentlich mit Rosiere 3.

Liebi Grüess
Lea
"""),

dict(id="1009", d="2026-10-09 19:40", w="ra", subj="Tagesrapport ZRH01 – 09.10.2026", body="""
Rapport im Anhang.

Freundliche Grüsse
Reto Ammann
""", att=[dict(name="Tagesrapport_ZRH01_09.10.2026.xlsx", kind="xlsx", sheet="Rapport", rows=[
    ["Tagesrapport ZRH01 Bahnhofstrasse"], ["Datum", "09.10.2026"], [],
    ["Umsatz CHF", 30880], ["Budget CHF", 30330], ["Abweichung", "1.8%"], ["Frequenz", 202], ["Bons", 18], ["Teile", 28], [],
    ["Lieferung", "260 Teile, pünktlich (u.a. Hermine, Tib, 35 Beanies)"],
    ["Bestseller", "Hermine navy 3x, Beanie schwarz 2x, Tricot navy 2x, Trailgrip W 2x, Bady offwhite 2x"],
    ["Nachgefragt / nicht an Lager", "Polo navy S"],
    ["Retouren", "Logo Cardigan M (anders überlegt)"],
    ["Bemerkungen", "Indische Gäste ca. 10%. Golden Week vorbei, Chinesen deutlich weniger."],
])]),

dict(id="1010", d="2026-10-10 18:44", w="lb", subj="Abschluss Sa 10.10.", mailer="iphone", body="""
Hoi zäme

CHF 33'390 (Budget 42'040). Viel los aber nicht genug Bons.

Polo schwarz 3x, Chamonix 2x, Cable Knit schwarz 2x, Maya navy 2x, Rosiere 2x.
Nicht da: Maire schwarz 1 (2 Kundinnen!), Hermine navy 0, Trailgrip W 35.

Wetterbericht sagt ab Montag Schnee bis 1000 m 🥶

Liebi Grüess
Lea

Von meinem iPhone gesendet
"""),

dict(id="1012", d="2026-10-12 19:34", w="ra", subj="Tagesrapport ZRH01 – 12.10.2026", body="""
Guten Abend zusammen

Umsatz: CHF 4'010 (Budget CHF 23'620)
Frequenz: 133 / Bons: 4

Bemerkungen:
- Sehr schlechter Tag. Schneeregen und 3 Grad, die Leute kamen rein, um sich aufzuwärmen, und sind wieder gegangen. Keine konkreten Anfragen notiert.
- Zusätzlich wieder eine Tib-Retoure (Reissverschluss, Gr. 3, gekauft im August)
- Verkauft nur Handschuhe, Logo Cardigan, Bady, Chambre, Ilvaro je 1x

Freundliche Grüsse
Reto Ammann
"""),

dict(id="1013", d="2026-10-13 19:47", w="ra", subj="Tagesrapport ZRH01 – 13.10.2026", body="""
Guten Abend zusammen

Umsatz: CHF 46'832 inkl. MWST (Budget CHF 21'800)
Frequenz: 152 / Bons: 18

Bemerkungen:
- Heute ging es los: Maire navy 5x (!), Insolux 4x, Tricot Cardigan schwarz 3x
- Nachgefragt: Montgenevre navy 6, Chamonix L
- Retouren: Rollkragen M (Grösse), Trailgrip GTX 45 (Farbe)

Freundliche Grüsse
Reto Ammann
"""),

dict(id="1013x", d="2026-10-13 19:59", w="ra", subj="Rückruf: Tagesrapport ZRH01 – 13.10.2026", nofooter=True, body="""
Reto Ammann möchte die Nachricht "Tagesrapport ZRH01 – 13.10.2026" zurückrufen.
"""),

dict(id="1013c", d="2026-10-13 20:03", w="ra", subj="Tagesrapport ZRH01 – 13.10.2026 (korrigiert)", body="""
Guten Abend zusammen

Korrektur, ich hatte den Bruttobetrag kopiert. Netto:

Umsatz: CHF 43'323 (Budget CHF 21'800)
Frequenz: 152 / Bons: 18

Rest wie gehabt.

Freundliche Grüsse
Reto Ammann
"""),

dict(id="1014", d="2026-10-14 19:58", w="lb", subj="Abschluss Bahnhofstrasse 14.10. ❄️", body="""
Hoi zäme

Was für ein Tag! CHF 59'730, Budget 25'210 – mehr als doppelt so viel. Schnee bis 1000 m, auf dem Uetliberg liegt alles weiss und die Zürcher haben gemerkt, dass der Winter kommt.

Cable Knit schwarz 5x, Maya schwarz 3x, Polaris Oversized 2x, Valbourg schwarz 2x, Beanies weiss 2x.

Alles will lang und warm. Nicht da:
- Hermine schwarz 3, Hermine navy 0
- Maire navy 3
- Bady offwhite 2
- Maya navy 3
- Valbourg schwarz 0
- Ambrine braun 1
- Ilvaro rosa 1 (die Kundin hat uns ein Foto von der koreanischen Sängerin gezeigt)

Valbourg schwarz 0, Cable Knit schwarz S, Tricot Cardigan schwarz L jetzt auch aus.

Liebi Grüess
Lea
"""),

dict(id="1015m", d="2026-10-15 11:20", w="ra", subj="ZRH01 – Nachschubanfrage Kälteeinbruch", to=["merch"], cc=["sw", "ops"], body="""
Liebes Merch-Team

Wegen des Kälteeinbruchs haben wir seit Dienstag deutlich mehr Nachfrage nach langen und warmen Modellen. Folgendes fehlt uns aktuell und wurde in den letzten Tagen konkret nachgefragt:

Hermine schwarz 3, 4
Hermine navy 0, 1
Maire schwarz 0, 1
Maire navy 3
Bady offwhite 2
Maya navy 3, 5
Montgenevre navy 3, 6
Chamonix L
Valbourg schwarz 0

Wäre es möglich, mit der Lieferung vom Freitag noch etwas davon nachzuschieben? Allenfalls auch per Umlagerung aus St. Moritz, die schliessen ja am Sonntag.

Besten Dank und freundliche Grüsse
Reto Ammann
"""),

dict(id="1015", d="2026-10-15 19:42", w="ra", subj="Tagesrapport ZRH01 – 15.10.2026", body="""
Guten Abend zusammen

Umsatz: CHF 25'910 (Budget CHF 27'680)
Frequenz: 199 / Bons: 19

Bemerkungen:
- Etwas ruhiger als gestern, viele Gäste aus den Emiraten
- Polaris Balaclava 2x, Hoodies schwarz 3x, Schal grau 2x
- Nachgefragt (7): Maire schwarz 1, Hermine navy 1, Bady offwhite 2, Montgenevre navy 5 und 6, Chamonix L, T-Shirt weiss L
- Maire schwarz 2 jetzt auch auf null, also 0/1/2 komplett weg

Freundliche Grüsse
Reto Ammann
"""),

dict(id="1016", d="2026-10-16 19:51", w="ra", subj="Tagesrapport ZRH01 – 16.10.2026", body="""
Guten Abend zusammen

Umsatz: CHF 49'080 (Budget CHF 32'950)
Frequenz: 238 / Bons: 28

Bemerkungen:
- Lieferung pünktlich (165 Teile), u.a. 3x Ilvaro rosa, Hermine, 17 Beanies
- Polaris Balaclava 5x (!) – bei Kälte plötzlich gefragt
- Beanie schwarz 3x, Logo Cardigan 3x, Maya schwarz 3x, Maire navy 3x
- Nachgefragt: Maire schwarz 2 (2 Kundinnen) und 3, Trailgrip GTX 42
- Arneb schwarz 3 und Logo Cardigan schwarz M auf null

Freundliche Grüsse
Reto Ammann
"""),

dict(id="1016d", d="2026-10-16 19:51", w="ra", sfx="_dup", subj="Tagesrapport ZRH01 – 16.10.2026", body="""
Guten Abend zusammen

Umsatz: CHF 49'080 (Budget CHF 32'950)
Frequenz: 238 / Bons: 28

Bemerkungen:
- Lieferung pünktlich (165 Teile), u.a. 3x Ilvaro rosa, Hermine, 17 Beanies
- Polaris Balaclava 5x (!) – bei Kälte plötzlich gefragt
- Beanie schwarz 3x, Logo Cardigan 3x, Maya schwarz 3x, Maire navy 3x
- Nachgefragt: Maire schwarz 2 (2 Kundinnen) und 3, Trailgrip GTX 42
- Arneb schwarz 3 und Logo Cardigan schwarz M auf null

Freundliche Grüsse
Reto Ammann
"""),

dict(id="1017", d="2026-10-17 18:49", w="lb", subj="Abschluss Sa 17.10.", body="""
Hoi zäme

CHF 66'603 bei Budget 45'200, neuer Rekord für dieses Jahr! 348 Kunden, wir waren zu sechst.

Maya schwarz 4x, Hoodie schwarz 4x, Flammette navy 4x, Bady offwhite 3x, Karakorum schwarz 3x.
Die Ilvaro rosa wurden oft probiert, verkauft aber noch keine.

Nicht da:
- Maire schwarz 00, 2, 3
- Ilvaro schwarz 1
- Karakorum navy 2
- T-Shirt weiss L
- Insolux 39 und 40

Rosiere Gr. 4 zurück, war ein Geschenk.

Liebi Grüess und schöne Sonntag
Lea
"""),

dict(id="1019", d="2026-10-19 19:38", w="ra", subj="Tagesrapport ZRH01 – 19.10.2026", body="""
Guten Abend zusammen

Umsatz: CHF 20'575 (Budget CHF 25'580)
Frequenz: 198 / Bons: 12

Bemerkungen:
- Wetter wieder milder, die Nachfrage flacht ab
- Bady schwarz 5x, Maya schwarz 3x
- Nachgefragt: Montgenevre navy 3, Arneb schwarz 3, Insolux 39
- Crewneck XL zurück (Grösse)

Freundliche Grüsse
Reto Ammann
"""),

dict(id="1020", d="2026-10-20 19:43", w="ra", subj="Tagesrapport ZRH01 – 20.10.2026", body="""
Guten Abend zusammen

Umsatz: CHF 16'890 (Budget CHF 22'230)
Frequenz: 159 / Bons: 15

Bemerkungen:
- Föhn, 16 Grad
- Beanie schwarz 3x, Logo Cardigan, Rollkragen, Hoodie navy je 2x
- Retouren: Maire 00 und Insolux 37, beide Grösse
- Nachgefragt: Maire navy 2, Hermine schwarz 00, Ilvaro schwarz 1, Montgenevre navy 3 (dritte Anfrage in 2 Tagen), Polaris Balaclava

Freundliche Grüsse
Reto Ammann
"""),

dict(id="1021", d="2026-10-21 19:45", w="lb", subj="Abschluss Bahnhofstrasse 21.10.", body="""
Hoi zäme

CHF 15'543 (Budget 27'440). Ruhiger Mittwoch, viele Gäste aus den Emiraten.

Tib 4x (2 schwarz, 2 offwhite), Schal grau 2x, Chambre 2x.
Maya schwarz 4 zweimal gefragt, nicht da. Insolux 39 und 40 auch wieder.

Laut Avis kommt am Freitag die Maire schwarz, 20 Stück in allen Grössen. Ich rufe morgen die Kundinnen auf der Warteliste an.

Liebi Grüess
Lea
"""),
]
