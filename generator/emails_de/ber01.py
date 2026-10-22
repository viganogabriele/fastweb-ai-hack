# -*- coding: utf-8 -*-
"""BER01 - Berlin KaDeWe (shop-in-shop). Hand-authored closing emails.

Writers: Jana Schulte (SM, direct, bullet lists, "Kd./Kdn.", references "das Haus"), Mehmet Aydın (ASM, formal,
Outlook HTML with KPI table incl. a KaDeWe house-frequency row, long corporate signature), Tobias "Tobi" Krüger
(SA, Saturdays, lowercase, iPhone).
"""
DOM = "moncler-retail.example"

PEOPLE = {
    "js": dict(name="Jana Schulte", addr=f"jana.schulte@{DOM}", mailer="outlook",
               footer="\n\nJana Schulte\nStore Manager\nMoncler @ KaDeWe | Tauentzienstraße 21-24 | 10789 Berlin"),
    "ma": dict(name="Mehmet Aydın", addr=f"mehmet.aydin@{DOM}", mailer="outlook",
               footer=("\n\nMit freundlichen Grüßen\n\nMehmet Aydın\nAssistant Store Manager\nMoncler @ KaDeWe Berlin\n"
                       "Tauentzienstraße 21-24, 10789 Berlin\nT +49 30 2190 4471\n\n"
                       "Diese E-Mail enthält vertrauliche und/oder rechtlich geschützte Informationen. Wenn Sie nicht "
                       "der richtige Adressat sind oder diese E-Mail irrtümlich erhalten haben, informieren Sie bitte "
                       "sofort den Absender und vernichten Sie diese Mail. Das unerlaubte Kopieren sowie die unbefugte "
                       "Weitergabe dieser Mail ist nicht gestattet.")),
    "tk": dict(name="Tobias Krüger", addr=f"tobias.krueger@{DOM}", mailer="iphone"),
    "store": dict(name="Moncler KaDeWe", addr=f"ber01.store@{DOM}", mailer="outlook"),
}

H = ["", "Ist", "Budget", "Abw."]

EMAILS = [
dict(id="0831", d="2026-08-31 20:38", w="js", subj="BER01 Abschluss 31.08.", body="""
Hallo zusammen,

Montag war tot. 3,0k bei 8,3k Budget, nur 4 Bons. Das ganze Haus war leer, selbst in der Feinkost kaum was los.

- Kd. fragt Montgenevre navy 1, haben wir nicht
- Flammette schwarz 2, Tib navy 5, Polo schwarz L sind auf null
- SS-Reste (Albenga, Marin) stehen noch rum, die kann man eigentlich zurückschicken

VG Jana
"""),

dict(id="0901", d="2026-09-01 20:44", w="js", subj="BER01 Abschluss 01.09.", body="""
Hallo zusammen,

8,7k vs. 7,7k Budget, also knapp drüber. Conversion fast 19 %, wenig Leute aber die richtigen.
Caps weiß 2x, dazu Maya navy und ein Tricot Cardigan.
Kd. wollte Tricot Cardigan schwarz in XL, nicht da.

VG Jana
"""),

dict(id="0902", d="2026-09-02 20:31", w="js", subj="BER01 Abschluss 02.09.", body="""
Hallo,

5,1k (Budget 8,3k). Fast nur Berliner im Shop.
- Gürteltasche zurück, Gurt zu kurz laut Kd. (im System als Größe gebucht)
- Maire beige 1 gefragt, nicht da
- Hoodie schwarz 2x

VG Jana
"""),

dict(id="0903", d="2026-09-03 21:02", w="ma", subj="Tagesabschluss BER01 KaDeWe – 03.09.2026", body="""
Liebe Kolleginnen und Kollegen,

anbei die Kennzahlen des heutigen Tages:

{TABLE}

Bemerkungen:
- Die Wochenlieferung ist pünktlich eingetroffen (78 Teile) und wurde vollständig über die Warenannahme des Hauses angenommen und verräumt.
- Verkauft wurden u. a. eine Peyre, eine Valbourg und zwei Cable Knit Sweater.
- Karakorum schwarz Gr. 5 und Montgenevre schwarz Gr. 5 sind weiterhin nicht verfügbar.
""", table=[H, ["Umsatz netto", "9.290 €", "11.030 €", "-15,8 %"], ["Bons", "5", "", ""], ["Frequenz Shop", "50", "", ""],
           ["Conversion", "10,0 %", "", ""], ["UPT", "1,4", "", ""], ["Frequenz Haus (lt. KaDeWe)", "31.870", "", ""]]),

dict(id="0904", d="2026-09-04 21:26", w="js", subj="BER01 Abschluss 04.09.", body="""
Hi zusammen,

9,1k bei 13,9k Budget, Freitag eher mau.
Kaschmirschals schwarz 3x verkauft (alle an eine österreichische Kundin), Maya schwarz 1x.
Cable Knit beige M gefragt, nicht vorhanden.

Schönes WE
Jana
"""),

dict(id="0905", d="2026-09-05 20:41", w="tk", subj="abschluss sa", body="""
hi,
14,8k heute (budget 18,6k). handschuhe 3x, rolli schwarz 2x, montgenevre navy 2x.
sonst ruhig, keine besonderen vorkommnisse.
lg tobi

Von meinem iPhone gesendet
"""),

dict(id="0907", d="2026-09-07 20:35", w="js", subj="BER01 Abschluss 07.09.", body="""
Hallo zusammen,

9,8k (Budget 10,3k), passt fast.
- Kd. fragt Montgenevre navy 6, schon wieder Montgenevre navy, die Randgrößen fehlen komplett
- Kdn. wollte Insolux 38, nicht da
- Maire schwarz 0 seit heute auf null

VG Jana
"""),

dict(id="0908", d="2026-09-08 20:29", w="js", subj="BER01 Abschluss 08.09.", body="""
Hallo,

9,2k vs 9,9k Budget. Hoodies grau 2x.
Rolli schwarz M gefragt, nicht da. Kaschmirschal schwarz ist jetzt komplett aus, bitte nachliefern, das ist ein Basic für uns.

VG Jana
"""),

dict(id="0909", d="2026-09-09 20:47", w="js", subj="BER01 Abschluss 09.09.", body="""
Hallo zusammen,

7,3k bei 11,1k Budget.
Im Haus waren heute zwei chinesische Reisegruppen, die waren aber fast nur in der Feinkost und bei den Taschen im EG. Bei uns nur ein paar Kunden, Gürteltasche und Polo verkauft.
Flammette schwarz 2 und Montcla schwarz 4 sind auf null.

VG Jana
"""),

dict(id="0910", d="2026-09-10 21:05", w="ma", subj="Tagesabschluss BER01 KaDeWe – 10.09.2026", body="""
Liebe Kolleginnen und Kollegen,

hier der Abschluss für heute:

{TABLE}

Bemerkungen:
- Lieferung pünktlich (88 Teile), die fehlenden Größen bei Karakorum und Montgenevre wurden aufgefüllt.
- Maya schwarz 2x verkauft.
- Keine Retouren.
""", table=[H, ["Umsatz netto", "10.070 €", "11.770 €", "-14,4 %"], ["Bons", "7", "", ""], ["Frequenz Shop", "62", "", ""],
           ["Conversion", "11,3 %", "", ""], ["UPT", "1,29", "", ""], ["Frequenz Haus (lt. KaDeWe)", "33.240", "", ""]]),

dict(id="0911", d="2026-09-11 21:31", w="js", subj="BER01 Abschluss 11.09.", body="""
Hallo,

10,2k (Budget 15,6k). Trailgrip GTX grau 2x, sonst Kleinteile. Freitag schwach, keine Anfragen ohne Ware.

VG Jana
"""),

dict(id="0912", d="2026-09-12 20:52", w="ma", subj="Tagesabschluss BER01 KaDeWe – 12.09.2026", body="""
Liebe Kolleginnen und Kollegen,

ein guter Samstag, Budget knapp erreicht:

{TABLE}

Bemerkungen:
- Bestseller: Polo schwarz (3), Logo Hoodie schwarz (3), Maya schwarz (2), Maire schwarz (2).
- Nicht verfügbar und nachgefragt: Montcla navy Gr. 7, Logo Hoodie schwarz Gr. S.
- Hoodie schwarz S, Polo schwarz S und Montgenevre navy 5 sind ausverkauft.
""", table=[H, ["Umsatz netto", "21.110 €", "20.890 €", "+1,1 %"], ["Bons", "18", "", ""], ["Frequenz Shop", "89", "", ""],
           ["Conversion", "20,2 %", "", ""], ["UPT", "1,28", "", ""], ["Frequenz Haus (lt. KaDeWe)", "58.100", "", ""]]),

dict(id="0914", d="2026-09-14 20:33", w="js", subj="BER01 Abschluss 14.09.", body="""
Hallo zusammen,

9,1k vs 11,4k Budget.

Drei Retouren Accessoires (2 Kaschmirschals, 1 Cap). Alles Geschenke von letzter Woche, die Kassenkollegin hat überall "Größe" als Grund gewählt, eigentlich war es Nichtgefallen. Nur damit ihr euch nicht wundert.
Hoodie grau M gefragt, nicht da.

VG Jana
"""),

dict(id="0916", d="2026-09-16 20:42", w="js", subj="BER01 Abschluss 16.09.", body="""
Hallo,

10,9k (Budget 11,8k).
- Saudische Familie mit 3 Damen, Insolux 2x gekauft, die 38 hätten sie auch noch genommen -> nicht da
- dazu Schal, Gürteltasche, Polo
- Montgenevre navy 5 ist immer noch auf null

Gestern hab ich den Abschluss nicht geschickt, war ein ruhiger Tag (ca. 8k), sorry.

VG Jana
"""),

dict(id="0917", d="2026-09-17 21:10", w="ma", subj="Tagesabschluss BER01 KaDeWe – 17.09.2026", body="""
Liebe Kolleginnen und Kollegen,

anbei der heutige Abschluss:

{TABLE}

Bemerkungen:
- Lieferung pünktlich, 89 Teile.
- Nachfragen ohne Bestand: Karakorum grau melange Gr. 4, Insolux schwarz 38 (erneut), Insolux offwhite 35.
- Flammette schwarz Gr. 0 ist ausverkauft.
""", table=[H, ["Umsatz netto", "10.805 €", "13.810 €", "-21,8 %"], ["Bons", "9", "", ""], ["Frequenz Shop", "58", "", ""],
           ["Conversion", "15,5 %", "", ""], ["UPT", "1,22", "", ""], ["Frequenz Haus (lt. KaDeWe)", "34.900", "", ""]]),

dict(id="0918", d="2026-09-18 21:40", w="js", subj="BER01 Abschluss 18.09. 🙂", body="""
Hallo zusammen,

endlich mal ein richtig guter Tag: 27,1k bei 16,2k Budget!

- Stammkunde Herr K. mit seinen zwei Söhnen, Montgenevre navy (3x) und Tricot Cardigan navy, das allein waren fast 9k
- Tricot navy insgesamt 4x, Polo schwarz 3x, Maire beige 2x
- Maire beige 2 und Montgenevre navy 3 jetzt auf null

Schönes Wochenende
Jana
"""),

dict(id="0919", d="2026-09-19 20:37", w="tk", subj="abschluss samstag 19.9.", body="""
hallo,
23,9k / budget 22,6k 👍
shirts navy 3x, montgenevre schwarz 2x, schals beige 2x
nicht da: montgenevre schwarz 2, peyre 7, polo weiss S
lg tobi

Von meinem iPhone gesendet
"""),

dict(id="0921", d="2026-09-21 20:30", w="js", subj="BER01 Abschluss 21.09.", body="""
Hallo,

7,4k (Budget 12,3k). Sehr ruhiger Montag.
Kdn. fragt Maire navy 3, Kd. Tricot schwarz XL (schon wieder XL, die Größe fehlt uns seit Wochen).
Karakorum schwarz 2x.

VG Jana
"""),

dict(id="0922", d="2026-09-22 20:39", w="js", subj="BER01 Abschluss 22.09.", body="""
Hallo zusammen,

14,0k bei 12,0k Budget.
- Maire beige 2x, Bady offwhite 2x
- Hoodie L zurück, Logo-Patch löst sich an der Ecke. Ist zur Seite gelegt, bitte Info wohin damit
- Maire schwarz 0 und Maire beige 0 sind jetzt auch aus

VG Jana
"""),

dict(id="0923", d="2026-09-23 20:41", w="js", subj="BER01 Abschluss 23.09.", body="""
Hallo,

6,2k vs 14,0k. Schlechter Tag, nur 5 Bons.
Peyre 3 und Polo schwarz XS gefragt, nicht da. Eine Polo XS-Retoure (Kd. hat es sich anders überlegt).

VG Jana
"""),

dict(id="0924", d="2026-09-24 20:48", w="js", subj="BER01 Abschluss 24.09.", body="""
Hallo zusammen,

17,9k bei 14,8k Budget, guter Donnerstag.

- Lieferung pünktlich (53 Teile)
- Hoodies schwarz 4x, Tricot schwarz 3x, Rosiere schwarz 2x, Handschuhe 2x
- Tricot grau XXL gefragt

Kunden fragen übrigens nach der Genius Polaris Kapsel, die online seit heute zu sehen ist. Haben wir nicht im Sortiment, die Kunden schicken wir nach München.

VG Jana
"""),

dict(id="0924c", d="2026-09-24 21:03", w="js", subj="AW: BER01 Abschluss 24.09.", reply="0924", body="""
Korrektur: Umsatz war 19,7k, nicht 17,9k. Zahlendreher, sorry.
Jana
"""),

dict(id="0925", d="2026-09-26 09:14", w="js", subj="BER01 Abschluss 25.09. (verspätet)", body="""
Guten Morgen,

gestern Abend ging im Lager das WLAN nicht, deshalb erst jetzt.

25.09.: 9,5k bei 18,0k Budget. Polo weiß 2x, Crewneck schwarz 2x, eine Peyre.
Rolli navy XL gefragt, nicht da.

VG Jana
"""),

dict(id="0926", d="2026-09-26 21:12", w="ma", subj="Tagesabschluss BER01 KaDeWe – 26.09.2026", body="""
Liebe Kolleginnen und Kollegen,

der Samstag lag deutlich unter Budget:

{TABLE}

Bemerkungen:
- Bestseller: Karakorum schwarz (2).
- Nicht verfügbar und nachgefragt: Maire schwarz Gr. 0, Cable Knit offwhite Gr. S und XL, Crewneck Sweatshirt grau Gr. XXL.
- Retouren: Montgenevre Gr. 5 (Größe), Crewneck Sweatshirt XL (Kunde hat es sich anders überlegt).
- Ausverkauft: Maya navy Gr. 3, Rosiere schwarz Gr. 4, Crewneck schwarz Gr. S.
- Im Haus war wegen des Marathon-Wochenendes deutlich weniger los als üblich.
""", table=[H, ["Umsatz netto", "15.120 €", "24.700 €", "-38,8 %"], ["Bons", "12", "", ""], ["Frequenz Shop", "94", "", ""],
           ["Conversion", "12,8 %", "", ""], ["UPT", "1,33", "", ""], ["Frequenz Haus (lt. KaDeWe)", "47.300", "", ""]]),

dict(id="0928", d="2026-09-28 20:45", w="js", subj="BER01 Abschluss 28.09. / Tib defekt", body="""
Hallo zusammen,

14,3k bei 14,0k Budget.

Reklamation: Tib navy Gr. 4 zurück, gekauft Anfang September. Der Reißverschluss-Schieber greift nicht mehr, die Weste geht beim Tragen von unten auf. Kd. wollte keinen Ersatz, Geld zurück. Teil liegt im Lager mit Zettel. Haben andere Stores das auch?

Sonst:
- Schals schwarz 2x, Gürteltaschen 2x, Flammette schwarz 2x, Tricot schwarz 2x
- Maire schwarz 0 gefragt, nicht da
- Tricot schwarz M und Kaschmirschal schwarz wieder auf null

VG Jana
"""),

dict(id="0929", d="2026-09-29 20:36", w="js", subj="BER01 Abschluss 29.09.", body="""
Hallo,

11,2k (Budget 13,2k), nur 4 Bons, Conversion 8 %.
Flammette schwarz 3x, damit ist die 1 jetzt weg.
Maya navy 2 gefragt.

VG Jana
"""),

dict(id="0930", d="2026-09-30 20:49", w="js", subj="BER01 Abschluss 30.09.", body="""
Hallo zusammen,

10,9k vs 15,0k.
- Kdn. Maire schwarz 0 (die dritte Anfrage in einer Woche in Gr. 0)
- Flammette schwarz 1 gefragt, gestern ausverkauft
- Rosiere schwarz 4 gefragt
- viele Österreicher heute

VG Jana
"""),

dict(id="1001", d="2026-10-01 21:19", w="ma", subj="Tagesabschluss BER01 KaDeWe – 01.10.2026", body="""
Liebe Kolleginnen und Kollegen,

siehe Anhang.
""", att=[dict(name="BER01_Tagesabschluss_01102026.xlsx", kind="xlsx", rows=[
    ["Store", "BER01 KaDeWe"], ["Datum", "01.10.2026"], [],
    ["Kennzahl", "Ist", "Budget", "Abw. %"],
    ["Umsatz netto EUR", 23746, 16710, 42.1], ["Bons", 12, None, None], ["Teile", 19, None, None],
    ["Frequenz Shop", 76, None, None], ["Conversion", 0.158, None, None], [],
    ["Lieferung", "SHP02600379 – 145 Teile – pünktlich"], [],
    ["Nicht verfügbar / Kundenanfragen", "Maire schwarz 0", "Maire schwarz 4", "Cable Knit offwhite XS"],
    ["Retouren", "Maire 1 (anders überlegt)"],
    ["Bestseller", "Maya navy 3", "Maya schwarz 2", "Rosiere schwarz 2", "Montcla schwarz 2"],
])]),

dict(id="1002", d="2026-10-02 21:22", w="js", subj="BER01 Abschluss 02.10.", body="""
Hallo zusammen,

14,3k bei 20,0k Budget.
- Maya navy 3x, Gürteltaschen 2x
- Trailgrip GTX 42 zurück, zu klein
- Maya navy 5 jetzt auf null

Morgen Feiertag, das Haus bleibt zu. Ich bin ab Montag eine Woche im Urlaub, Mehmet übernimmt die Abschlüsse.

VG Jana
"""),

dict(id="1005", d="2026-10-05 20:58", w="ma", subj="Tagesabschluss BER01 KaDeWe – 05.10.2026", body="""
Liebe Kolleginnen und Kollegen,

ein erfreulicher Start in die Woche:

{TABLE}

Bemerkungen:
- Maya schwarz 3x verkauft.
- Zwei Kundinnen haben nach der Maire schwarz in Gr. 4 gefragt, leider nicht verfügbar.
- Retoure: Peyre Gr. 5, Kunde wünschte eine andere Farbe (rot), die wir nicht führen.
""", table=[H, ["Umsatz netto", "17.415 €", "14.210 €", "+22,6 %"], ["Bons", "12", "", ""], ["Frequenz Shop", "67", "", ""],
           ["Conversion", "17,9 %", "", ""], ["UPT", "1,67", "", ""], ["Frequenz Haus (lt. KaDeWe)", "36.050", "", ""]]),

dict(id="1006q", d="2026-10-06 09:58", w="sw", subj="Maire schwarz Anfragen BER", to=["js"], cc=["store"], body="""
Hallo Jana,

kurze Frage: wie viele Anfragen Maire schwarz habt ihr ungefähr pro Woche, und in welchen Größen? Ich brauche bis Mittwoch eine Zahl für die Allokation der Nachlieferung (ab 16.10. wieder im DC).

Danke
Stefan
"""),

dict(id="1006a", d="2026-10-06 09:58", w="js", subj="Automatische Antwort: Maire schwarz Anfragen BER", reply="1006q", auto=True, nofooter=True,
     to=["sw"], cc=[], body="""
Vielen Dank für Ihre Nachricht. Ich bin bis einschließlich 11.10.2026 nicht im Büro. In dringenden Fällen wenden Sie sich bitte an Mehmet Aydın (mehmet.aydin@moncler-retail.example) oder an ber01.store@moncler-retail.example.

Thank you for your message. I am out of the office until 11 October 2026.

Jana Schulte
"""),

dict(id="1006r", d="2026-10-06 11:27", w="ma", subj="AW: Maire schwarz Anfragen BER", reply="1006q", quote="1006q", to=["sw"], cc=["js"], body="""
Hallo Stefan,

Jana ist im Urlaub, ich antworte für sie.

Laut unserer Liste hatten wir seit Ende September ca. 2–3 Anfragen pro Woche nach der Maire schwarz, überwiegend Gr. 0 und Gr. 4, vereinzelt Gr. 2. Die Gr. 0 und 2 sind seit dem 22.09. auf null.
Aus meiner Sicht wären 2x Gr. 0, 2x Gr. 4 und 1x Gr. 2 für uns ein guter Start.
""", nofooter=False),

dict(id="1006", d="2026-10-06 21:04", w="ma", subj="Tagesabschluss BER01 KaDeWe – 06.10.2026", body="""
Liebe Kolleginnen und Kollegen,

der heutige Abschluss:

{TABLE}

Bemerkungen:
- Auffallend viele amerikanische Kunden (ca. ein Viertel).
- Caps schwarz 3x, Tib navy 2x.
- Nachgefragt, aber nicht verfügbar: Karakorum navy Gr. 3, Logo T-Shirt weiß Gr. L.
- Montcla schwarz Gr. 5 ist ausverkauft.
""", table=[H, ["Umsatz netto", "14.389 €", "14.020 €", "+2,6 %"], ["Bons", "12", "", ""], ["Frequenz Shop", "74", "", ""],
           ["Conversion", "16,2 %", "", ""], ["UPT", "1,42", "", ""], ["Frequenz Haus (lt. KaDeWe)", "35.480", "", ""]]),

dict(id="1008", d="2026-10-08 21:15", w="ma", subj="Tagesabschluss BER01 KaDeWe – 08.10.2026", body="""
Liebe Kolleginnen und Kollegen,

entschuldigt bitte den fehlenden Abschluss von gestern, der Tag war unauffällig (ca. 13,7k, Budget 14,4k).

Heute:

{TABLE}

Bemerkungen:
- Lieferung pünktlich (84 Teile).
- Rosiere schwarz 2x, Peyre 1x.
- Montgenevre schwarz Gr. 5 nicht verfügbar.
""", table=[H, ["Umsatz netto", "23.590 €", "17.360 €", "+35,9 %"], ["Bons", "13", "", ""], ["Frequenz Shop", "70", "", ""],
           ["Conversion", "18,6 %", "", ""], ["UPT", "1,46", "", ""], ["Frequenz Haus (lt. KaDeWe)", "37.910", "", ""]]),

dict(id="1009", d="2026-10-09 21:47", w="ma", subj="Tagesabschluss BER01 KaDeWe – 09.10.2026", body="""
Liebe Kolleginnen und Kollegen,

der Freitag lag erfreulich über Budget:

{TABLE}

Bemerkungen:
- Karakorum schwarz 3x, Logo Hoodie schwarz 3x, Karakorum navy 2x, Flammette schwarz 2x.
- Nicht verfügbar: Flammette schwarz Gr. 4, Montgenevre schwarz Gr. 5.
- Die Kunden fragen vermehrt nach wärmeren Modellen, für nächste Woche ist ein deutlicher Temperaturrückgang angekündigt.
""", table=[H, ["Umsatz netto", "29.400 €", "20.780 €", "+41,5 %"], ["Bons", "13", "", ""], ["Frequenz Shop", "86", "", ""],
           ["Conversion", "15,1 %", "", ""], ["UPT", "2,0", "", ""], ["Frequenz Haus (lt. KaDeWe)", "44.620", "", ""]]),

dict(id="1010", d="2026-10-10 20:44", w="tk", subj="abschluss sa", body="""
30,1k / budget 28,8k
karakorum schwarz 4x!! dazu tricot navy, maya schwarz, crewneck je 2x
nicht da: maire schwarz 0, rosiere oliv 7, tricot navy M
tib navy 5 ist leer

lg tobi

Von meinem iPhone gesendet
"""),

dict(id="1012", d="2026-10-12 20:51", w="js", subj="BER01 Abschluss 12.10.", body="""
Hallo zusammen,

zurück aus dem Urlaub und Berlin hat über Nacht auf Winter umgeschaltet, 4 Grad und Wind.

28,1k bei 15,1k Budget (+86 %), Conversion 22 %.
- Rosiere schwarz 4x, Handschuhe 3x, Montgenevre navy 3x, Maya schwarz 2x
- nicht da: Rosiere schwarz 1, Tricot navy XS, Cable Knit beige M
- Rosiere schwarz 3 und 4 jetzt auf null, Karakorum schwarz 4 auch

Die Leute kommen gezielt wegen Daunen, nicht zum Bummeln.

VG Jana
"""),

dict(id="1012d", d="2026-10-12 20:52", w="js", sfx="_dup", subj="BER01 Abschluss 12.10.", body="""
Hallo zusammen,

zurück aus dem Urlaub und Berlin hat über Nacht auf Winter umgeschaltet, 4 Grad und Wind.

28,1k bei 15,1k Budget (+86 %), Conversion 22 %.
- Rosiere schwarz 4x, Handschuhe 3x, Montgenevre navy 3x, Maya schwarz 2x
- nicht da: Rosiere schwarz 1, Tricot navy XS, Cable Knit beige M
- Rosiere schwarz 3 und 4 jetzt auf null, Karakorum schwarz 4 auch

Die Leute kommen gezielt wegen Daunen, nicht zum Bummeln.

VG Jana
"""),

dict(id="1013", d="2026-10-13 20:47", w="js", subj="BER01 Abschluss 13.10.", body="""
Hallo,

17,3k (Budget 14,6k).

Viele Anfragen ohne Ware heute, ich zähle 7:
- Maire schwarz 00 und 4
- Maya navy 6
- Montcla navy 1
- Rosiere schwarz 3 und Rosiere oliv 7 (oliv 7 wurde jetzt schon zum zweiten Mal gefragt!)
- Tricot navy M

Polo schwarz L ist aus. Mehr Kunden aus den Emiraten als sonst.

VG Jana
"""),

dict(id="1014", d="2026-10-14 20:55", w="js", subj="BER01 Abschluss 14.10.", body="""
Hallo zusammen,

23,3k vs 17,1k Budget.

Mützen navy 5x, alle Kunden wollen warm. Montcla schwarz 2x, Beanie weiß 2x.

Nicht da:
- Karakorum schwarz 4 (2 Kunden) und 1
- Maya navy 6 (zweiter Tag hintereinander)
- Peyre 4
- Valbourg offwhite 00
- Rolli in braun M, Kd. hat ihn auf Insta gesehen, M ist bei uns weg

Flammette schwarz 0 und Montgenevre schwarz 3 jetzt auch weg.

VG Jana
"""),

dict(id="1015", d="2026-10-15 21:08", w="ma", subj="Tagesabschluss BER01 KaDeWe – 15.10.2026", body="""
Liebe Kolleginnen und Kollegen,

anbei der heutige Abschluss:

{TABLE}

Bemerkungen:
- Lieferung pünktlich (147 Teile), u. a. Beanies und Tib, die Maya schwarz wurde aufgefüllt.
- Beanies weiß und puderrosa je 2x, Montgenevre schwarz 2x, Ecrins 2x, Montcla schwarz 2x.
- Nachfrage Rosiere oliv Gr. 7 (erneut), nicht verfügbar.
""", table=[H, ["Umsatz netto", "19.920 €", "18.480 €", "+7,8 %"], ["Bons", "13", "", ""], ["Frequenz Shop", "81", "", ""],
           ["Conversion", "16,0 %", "", ""], ["UPT", "1,38", "", ""], ["Frequenz Haus (lt. KaDeWe)", "40.150", "", ""]]),

dict(id="1016", d="2026-10-16 21:36", w="js", subj="BER01 Abschluss 16.10.", body="""
Hallo zusammen,

33,4k bei 21,7k Budget!

Maya schwarz 8x (!!), die Ware von gestern ist fast schon wieder weg. Dazu Tib navy 3x, Beanies weiß 3x.
Nicht da: Bady offwhite 00, Maya schwarz 6, Polo schwarz L.

VG Jana
"""),

dict(id="1017", d="2026-10-17 20:58", w="ma", subj="Tagesabschluss BER01 KaDeWe – 17.10.2026", body="""
Liebe Kolleginnen und Kollegen,

ein außergewöhnlich starker Samstag:

{TABLE}

Bemerkungen:
- Bestseller: Maya navy (6), Maire beige (4), Karakorum navy (4), Maya schwarz (4), Beanie weiß (3).
- Beanie weiß ist seit dem Nachmittag ausverkauft, danach haben noch vier Kunden danach gefragt.
- Ebenfalls nicht verfügbar: Maire schwarz Gr. 2, Maya schwarz Gr. 7, Rosiere schwarz Gr. 6, Valbourg offwhite Gr. 4.
- Ausverkauft: Maire schwarz 0/1/2, Maya schwarz 5, Maya navy 5.
- Retoure: Flammette Gr. 3 (Größe).
""", table=[H, ["Umsatz netto", "53.836 €", "30.260 €", "+77,9 %"], ["Bons", "27", "", ""], ["Frequenz Shop", "139", "", ""],
           ["Conversion", "19,4 %", "", ""], ["UPT", "1,78", "", ""], ["Frequenz Haus (lt. KaDeWe)", "61.200", "", ""]]),

dict(id="1018q", d="2026-10-18 17:22", w="sw", subj="AW: Tagesabschluss BER01 KaDeWe – 17.10.2026", reply="1017", quote="1017", to=["ma", "js"], cc=["ops"], body="""
Klasse, danke euch!
Jana, kurze Frage für Montag: könntet ihr München mit ein paar Beanies aushelfen? Die haben dort auch kaum noch was.

Stefan
"""),

dict(id="1019r", d="2026-10-19 10:03", w="js", subj="AW: Tagesabschluss BER01 KaDeWe – 17.10.2026", reply="1018q", quote="1018q", to=["sw"], cc=["ma", "ops"], body="""
Hallo Stefan,

leider nein, Beanie weiß haben wir selbst seit Samstag 0, navy noch 3 Stück und puderrosa 2. Laut Avis kommen am Donnerstag 25 Beanies (10 navy, 11 weiß, 4 rosa), dann können wir gerne schauen.

VG Jana
"""),

dict(id="1019", d="2026-10-19 20:43", w="js", subj="BER01 Abschluss 19.10.", body="""
Hallo zusammen,

17,8k bei 16,3k Budget.

- Polo schwarz 2x, Flammette schwarz 2x
- nicht da: Maire schwarz 4, Maya schwarz 1 und 5, Rolli schwarz XL, Insolux offwhite 37 und 39
- Retouren: Karakorum 1 (Größe, viel zu klein), Beanie (Nichtgefallen), Schal (Größe?? steht so im System)

VG Jana
"""),

dict(id="1020", d="2026-10-20 20:37", w="js", subj="BER01 Abschluss 20.10.", body="""
Hallo,

6,5k bei 16,7k Budget. 15 Grad und Sonne, das Haus war leer.

Zweite Tib-Reklamation: Tib navy Gr. 3, Kauf Mitte September, gleiche Sache wie beim ersten Mal (Schieber greift nicht). Und eine Rosiere 6 zurück, zu groß.
Hoodie grau M gefragt.

VG Jana
"""),

dict(id="1021", d="2026-10-21 20:52", w="js", subj="BER01 Abschluss 21.10. / Tib", body="""
Hallo zusammen,

13,2k (Budget 18,2k).

Schon wieder eine Tib zurück, diesmal Gr. 5, gekauft im August. Das ist die dritte bei uns, alle mit dem gleichen Reißverschluss-Problem. Sollen wir die Tib aus dem Verkauf nehmen? Wir haben noch 6 Stück auf der Fläche.

Anfragen ohne Ware:
- Maire schwarz 0 (2 Kundinnen) und 4
- Ecrins 7
- Montgenevre schwarz 3
- Cable Knit beige L
- Insolux offwhite 39 (schon wieder)

Polo XL zurück (Größe). Morgen soll laut Avis die Maire schwarz kommen, 15 Stück, dann rufen wir die Kundinnen an.

VG Jana
"""),
]
