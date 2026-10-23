# -*- coding: utf-8 -*-
"""MUN01 - München Maximilianstraße. Hand-authored closing emails.

Writers: Katharina Huber (SM, structured, proper Umlaute, "LG Katharina"), Florian Brandl (ASM, telegraphic,
ae/oe/ue, Denglisch, "VG Flo"), Veronika "Vroni" Maier (Senior SA, Saturdays, chatty, Bavarian, emoji).
"""
DOM = "valentino-retail.example"

PEOPLE = {
    "kh": dict(name="Katharina Huber", addr=f"katharina.huber@{DOM}", mailer="outlook",
               footer="\n\n--\nKatharina Huber\nStore Manager | Valentino München Maximilianstraße\nT +49 89 2421 8830"),
    "fb": dict(name="Florian Brandl", addr=f"florian.brandl@{DOM}", mailer="outlook"),
    "vm": dict(name="Veronika Maier", addr=f"veronika.maier@{DOM}", mailer="iphone"),
    "store": dict(name="Valentino München", addr=f"mun01.store@{DOM}", mailer="outlook"),
}

EMAILS = [
dict(id="0831", d="2026-08-31 19:41", w="fb", subj="Abschluss Maxi 31.08.", body="""
Hallo zusammen,

kurz von heute: Umsatz 10,9k vs Budget 14,7k. Ruhiger Montag, 83 Leute im Laden.

- 2x Vel navy raus, sonst nur Kleinkram (Handschuhe, Rucksack, Cap)
- 2 Retouren Vlogo Cardigan (S und M), beide wegen Groesse
- Kd. wollte Mario navy in 3, ist aus. SS-Ware halt
- Vtrack Gtx schwarz 41 + 44 fehlen immer noch

VG Flo
"""),

dict(id="0901", d="2026-09-01 19:58", w="kh", subj="MUN01 Tagesabschluss 01.09.2026", body="""
Liebe Alle,

der Abschluss von heute:

Umsatz: 11,5k (Budget 14,2k)
Frequenz: 83 / 11 Bons
Gut gelaufen: Logo Caps (4 Stück), 2x Nova navy
Nachfragen ohne Ware: Cable Knit offwhite L, Jersey Polo navy L, Vtrack Gtx 44 (zum x-ten Mal, bitte Nachschub!)

Kundschaft gemischt, ein paar Amerikaner und Chinesen, sonst Stammkunden aus der Umgebung.

LG Katharina
"""),

dict(id="0902", d="2026-09-02 19:47", w="kh", subj="MUN01 Tagesabschluss 02.09.2026", body="""
Servus zusammen,

endlich mal über Budget: 16,6k bei 15,8k Budget.

Die schwarzen Logo-Shirts laufen noch erstaunlich gut (4 Stück), eine Kundin wollte XS, haben wir nicht. Eine amerikanische Familie aus dem Vier Jahreszeiten hat Cardigan und Alpina mitgenommen.
Aurea offwhite Gr. 2 und Aria offwhite Gr. 2 sind jetzt auf null.

LG Katharina
"""),

dict(id="0903", d="2026-09-03 20:05", w="kh", subj="MUN01 Tagesabschluss 03.09.2026", body="""
Liebe Alle,

zäher Tag, 14,2k gegen 20,5k Budget.

Erstaunlich viele Gäste aus Saudi-Arabien und den Emiraten, obwohl die Sommerferien dort eigentlich durch sind. Wurde viel probiert, gekauft eher wenig: 2x Nova navy, dazu Beanie, Schal, Jersey Polo. Nova navy Gr. 3 ist jetzt auch ausverkauft.
Eine Shirt-Retoure (S, Kundin hat es sich anders überlegt).
Wieder Anfrage Logo-Shirt in XS, diesmal navy.

LG Katharina
"""),

dict(id="0904", d="2026-09-04 19:52", w="kh", subj="MUN01 Tagesabschluss 04.09.", body="""
Hallo zusammen,

Freitag gut: 29,3k (Budget 24,6k), 144 Besucher, 17 Bons.

Die Lieferung, die gestern hätte kommen sollen, ist immer noch nicht da. GEODIS sagt morgen früh. Dadurch fehlen uns einige Größen, heute vier Kunden nicht bedient:
- Nova navy 2
- Cosimo grau 1
- Vel navy 2
- Vtrack Gtx 41 (schon wieder)

Positiv: 2x Aurea schwarz und 2x Artem. Den Artem nehmen die Herren gut an, er fällt aber ziemlich groß aus, das sollten wir im Auge behalten.

Schönes Wochenende
Katharina
"""),

dict(id="0905", d="2026-09-05 19:36", w="fb", subj="Abschluss Sa 05.09.", body="""
Umsatz 24,5 / Bud 33,5 -> deutlich drunter. Frequenz 177 aber Conversion mau (12%).

Lieferung heute frueh gekommen, 2 Tage zu spaet. 135 Teile, soweit komplett. Haben bis Mittag eingeraeumt, Flaeche war vormittags halb leer, das hat uns bestimmt was gekostet.

Artem Gr. 3 zurueck, Kunde sagt viel zu weit an den Schultern. Hab ihm die 2 angeboten, wollte dann nicht mehr.
Liviana Gr. 2 Retoure (anders ueberlegt).
Bestseller heute Vlogo Padded Cardigan schwarz 4x.

VG Flo
"""),

dict(id="0907", d="2026-09-07 19:29", w="fb", subj="Abschluss Maxi 7.9.", body="""
Montag ok, 16,9k (Bud 17,7). Wenig Leute aber ein paar gute Bons, u.a. saudische Kundin mit Schal und Beanie.
Monteluce grau 3 gefragt -> nicht da. Shirt schwarz XS schon wieder gefragt, gibts das ueberhaupt noch im DC??

Flo
"""),

dict(id="0908", d="2026-09-08 19:55", w="kh", subj="MUN01 Tagesabschluss 08.09.2026", body="""
Liebe Alle,

Umsatz 14,6k (Budget 17,8k), 107 Besucher.

Heute viele Österreicher und Schweizer, Hoodies schwarz 3x und Caps 3x. Jersey Polo navy XL wurde gefragt, haben wir nicht mehr.
Eine Hoodie-Retoure XL wegen Größe.

LG Katharina
"""),

dict(id="0909", d="2026-09-10 08:47", w="kh", subj="MUN01 Tagesabschluss 09.09. (Nachtrag)", body="""
Guten Morgen,

sorry, gestern Abend ist der Laptop im Büro nicht mehr hochgefahren, deshalb erst jetzt.

09.09.: 17,2k bei 20,1k Budget.
Caps navy 5x (!), Vlogo Cardigan schwarz 3x, Aurea offwhite 2x.
Nicht bedienen konnten wir: Aurea offwhite 2 (die Kundin hätte sofort gekauft), Fiammetta schwarz 0 und Chamonix-Hose in L.
Viele türkische Kunden gestern, eine Familie hat fast nur geschaut.

LG Katharina
"""),

dict(id="0910", d="2026-09-10 19:44", w="kh", subj="MUN01 Tagesabschluss 10.09.2026", body="""
Hallo zusammen,

schwacher Donnerstag: 14,0k vs 21,4k. 118 Leute im Laden, aber nur 7 Bons, Conversion unter 6 %. Sehr viel Laufkundschaft, die nur schauen.

Verkauft fast nur Accessoires (Beanies weiß + puderrosa, Handschuhe) und eine Piero.
Gefragt: Nova navy 5 und Valdora offwhite 3, beides nicht da.

LG Katharina
"""),

dict(id="0911", d="2026-09-11 19:50", w="kh", subj="MUN01 Tagesabschluss 11.09.2026", body="""
Liebe Alle,

21,3k (Budget 26,3k).

Abends wird es schon frisch, Rollkragen schwarz 4x verkauft. Leider sieben Anfragen, die wir nicht erfüllen konnten:
Aurea schwarz 4, Camilla schwarz 1, Mistral navy 2, Hoodie grau XXL, Logo-Shirt schwarz XS und L, Jersey Polo navy XL.

Bei den Shirts und Polos sind wir in den Randgrößen einfach leer. Gibt es da noch Nachschub oder ist SS durch?

Viele Grüße
Katharina
"""),

dict(id="0912", d="2026-09-12 19:33", w="fb", subj="Abschluss Sa 12.9.", body="""
Hi,

24,8k vs 36,8k Budget, Traffic eigentlich gut (203) aber Conversion nur 9%.

Lieferung schon wieder 2 Tage zu spaet (Do geplant, heute 10:30 gekommen, DHL diesmal). Zweite Woche hintereinander, bitte mal mit der Logistik reden. 155 Teile, alles da.
Fiammetta 0 zurueck, zu gross.
Kd. fragt Vel navy 4 und Cortina S, beides nix.

VG Flo
"""),

dict(id="0914", d="2026-09-14 19:21", w="fb", subj="Abschluss Mo", body="""
Ruhig. 16,5k / Bud 20,5k.
Vtrack Gtx 2x, Tricot navy 2x.
Alpina 36 gefragt, haben wir nicht.

Flo
"""),

dict(id="0915", d="2026-09-15 19:49", w="kh", subj="MUN01 Tagesabschluss 15.09.2026", body="""
Hallo zusammen,

schöner Dienstag, 22,2k bei 20,4k Budget, Conversion fast 15 %.

Jersey läuft: 7 Logo-Shirts, 2 Hoodies. Dazu 2x Aurea schwarz.
Hoodie schwarz M und Shirt schwarz S sind jetzt weg.
Mistral navy 2 gefragt, nicht da.

LG Katharina
"""),

dict(id="0916", d="2026-09-16 19:57", w="kh", subj="MUN01 Tagesabschluss 16.09.2026", body="""
Liebe Alle,

18,5k (Budget 21,8k). Heute auffallend viele Österreicher, fast ein Viertel der Kunden.

Amalia schwarz 2x verkauft, die neue Silhouette kommt gut an. Vtrack W schwarz 2x.
Eine Aurea Gr. 1 zurück (war ein Geschenk, Umtausch nicht gewünscht).
Gefragt: Aurea offwhite 0 und Vel navy 4.

LG Katharina
"""),

dict(id="0917", d="2026-09-17 20:02", w="kh", subj="MUN01 Tagesabschluss 17.09.2026", body="""
Servus zusammen,

super Tag: 34,5k gegen 25,1k Budget!

Lieferung heute pünktlich, und die Aria schwarz ist direkt 4x weg. Vlogo Padded Cardigan schwarz 5x, Liviana navy 2x.
Ab Samstag ist Wiesn, die Hotels sind laut Concierge vom Bayerischen Hof komplett voll. Wir rechnen mit viel Laufkundschaft, haben die Fenster schon umgestellt.

LG Katharina
"""),

dict(id="0918", d="2026-09-18 19:46", w="kh", subj="MUN01 Tagesabschluss 18.09.2026", body="""
Liebe Alle,

22,9k (Budget 30,9k). Eher ruhig, man merkt, dass alle auf morgen warten.
Rollkragen S zurück, Kundin sagt, er kratzt und hat nach einmal Tragen Knötchen. Habe ihn zur Seite gelegt.
Morgen O'zapft is, wir sind voll besetzt.

Schönes Wochenende
Katharina
"""),

dict(id="0919", d="2026-09-19 19:24", w="fb", subj="Wiesn-Samstag Abschluss 19.09.", body="""
Servus,

Wiesn-Anstich!! Stadt komplett voll, ab 11 Uhr Leute in Tracht ueberall.

Umsatz 67,3k (brutto) vs Budget 42,3k -> +59% !!!
Traffic 248, Kasse durchgehend besetzt.

- Cable Knit beige 4x, Aurea schwarz 4x, Mistral navy 3x, Aria schwarz 3x
- viele Deutsche aus dem Umland, die eh in der Stadt waren
- Aria offwhite 2 immer noch null

Grosses Danke ans Team, alle sind durch.

VG Flo
"""),

dict(id="0919d", d="2026-09-19 19:25", w="fb", sfx="_dup", subj="Wiesn-Samstag Abschluss 19.09.", body="""
Servus,

Wiesn-Anstich!! Stadt komplett voll, ab 11 Uhr Leute in Tracht ueberall.

Umsatz 67,3k (brutto) vs Budget 42,3k -> +59% !!!
Traffic 248, Kasse durchgehend besetzt.

- Cable Knit beige 4x, Aurea schwarz 4x, Mistral navy 3x, Aria schwarz 3x
- viele Deutsche aus dem Umland, die eh in der Stadt waren
- Aria offwhite 2 immer noch null

Grosses Danke ans Team, alle sind durch.

VG Flo
"""),

dict(id="0921", d="2026-09-21 19:38", w="fb", subj="Abschluss Mo 21.9.", body="""
Wiesn-Montag. Stadt voll, aber die Leute wollen Lederhosen und Dirndl, keine Daunen :)
17,0k vs Bud 23,1k.

Saudis + Amis + Chinesen im Laden, gekauft eher Caps und Cosimo navy (2x).
Cosimo navy 6 gefragt, nicht da.
Retouren: Cortina S und Vtrack W 40, beides Groesse.

Flo
"""),

dict(id="0923", d="2026-09-23 19:51", w="kh", subj="MUN01 Tagesabschluss 23.09.2026", body="""
Liebe Alle,

gestern habe ich im Wiesn-Trubel den Abschluss vergessen, sorry: 22.09. waren es 16,1k bei 22,6k Budget, ruhig, eine Anfrage Vlogo Cardigan navy M.

Heute deutlich besser: 28,8k (Budget 24,4k), Conversion 17 %.
2x Vel navy, 2x Aria offwhite, Rollkragen und Vlogo Cardigan je 2x.
Eine Kundin wollte die Aurea schwarz in 00 – haben wir leider nicht.

LG Katharina
"""),

dict(id="0924", d="2026-09-24 20:08", w="kh", subj="MUN01 Tagesabschluss 24.09. / Launch Couture Astra", body="""
Hallo zusammen,

heute leider nur 15,7k bei 30,5k Budget.

Launch Couture Astra: viel Interesse, viele Anproben, verkauft hat sich aber nur eine Balaclava. Rückmeldungen der Kunden:
- Oversized fällt trotz Name eher klein aus, ein Herr mit normal L kam in L nicht rein
- Cape für 2.900 € ist vielen zu teuer, "schön, aber nicht für den Preis"
- Farbe hellblau wird gemocht, aber eher von jüngeren Kunden, die dann nicht kaufen

Dazu 2x Artem schwarz. Lieferung pünktlich, 106 Teile.
Wiesn-Publikum kauft halt keine Daunenjacken bei 20 Grad.

LG Katharina
"""),

dict(id="0925", d="2026-09-25 19:43", w="kh", subj="MUN01 Tagesabschluss 25.09.2026", body="""
Liebe Alle,

27,8k (Budget 35,2k), 179 Besucher.

Hoodies schwarz 4x, Monteluce schwarz 2x, Camilla 2x. Mehr Chinesen als sonst (ca. 15 %).
Monteluce schwarz 6 und navy 3 gefragt, nicht vorhanden.

Morgen ist das Italiener-Wochenende auf der Wiesn, Vroni macht den Samstag.

LG Katharina
"""),

dict(id="0926", d="2026-09-26 19:52", w="vm", subj="Samstag", body="""
Servus beinand,

i schreib heut, Flo ist schon weg 😅

Italiener-Wochenende, die ganze Maximilianstraße voll mit Italienern in Lederhosen, dazu viele Chinesen.
Umsatz 43,1k, Budget war 49,4k, also knapp drunter, aber es war a Wahnsinn.

Aurea schwarz 3x verkauft, jetzt ist die 2 auch weg. Eine Dame wollte die Aurea schwarz in 00, die haben wir eh nie gehabt.
Nova navy 3x, Vtrack W 2x, Artem 2x.
Riviera schwarz 3 und Alpina 40 gefragt, nix da.

Pfiat eich
Vroni

Von meinem iPhone gesendet
"""),

dict(id="0928", d="2026-09-28 19:40", w="fb", subj="Abschluss Mo 28.09.", body="""
Hallo,

29,1k vs Bud 25,3k, guter Montag.

Astra: endlich 2 Teile verkauft (1 Oversized, 1 Cape), an einen Stammkunden. Er hat das Oversized eine Nummer groesser genommen.
Vlogo Cardigan schwarz 4x, Ettore 2x, Aurea offwhite 2x.

Viele Anfragen ohne Ware, ich liste mal:
Piero schwarz 4 (2 Kunden!), Vlogo Cap weiss (2x), Liviana navy 3, Iridia offwhite 2, Cosimo navy 6, Valdora offwhite 00, Alpina 36

Retouren:
- Aria 2 (anders ueberlegt)
- Cosimo 5 (Farbe)
- Artem 2 gegen 1 getauscht. Der faellt einfach eine Nummer groesser aus, wir sagen das jetzt jedem Kunden vorher und empfehlen eine Groesse kleiner

VG Flo
"""),

dict(id="0929", d="2026-09-29 19:48", w="kh", subj="MUN01 Tagesabschluss 29.09.2026", body="""
Liebe Alle,

19,5k (Budget 24,5k). Conversion schwach, knapp 7 %.

Astra Oversized wieder 2x verkauft, beide Kunden haben auch hier eine Größe größer gebraucht. Die Kapsel fällt wirklich klein aus, bitte an Merchandising weitergeben.
Liviana offwhite 3x.

Nicht bedient:
- Aurea schwarz 1
- Liviana navy 00 und 3
- Piero schwarz 4 (dritte Anfrage seit gestern)
- Logo-Shirt navy XL

Viele türkische Gäste heute.

LG Katharina
"""),

dict(id="0930", d="2026-09-30 19:55", w="kh", subj="MUN01 Tagesabschluss 30.09.2026", body="""
Hallo zusammen,

25,5k bei 28,1k Budget.

Aurea schwarz ist jetzt in 0, 1 und 2 komplett weg, also genau in den Größen, die am meisten gefragt werden. Laut DC gibt es vor Mitte Oktober nichts. Das tut weh.

Weitere Anfragen ohne Ware: Vtrack Gtx 44 (2 Kunden), Amalia schwarz 0, Artem schwarz 4, Cable Knit offwhite XL, Hoodie navy S.
Iridia Gr. 1 zurück, zu klein.

LG Katharina
"""),

dict(id="1001", d="2026-10-01 20:11", w="kh", subj="MUN01 Tagesabschluss 01.10.2026", body="""
Liebe Alle,

36,1k (Budget 31,8k), gut!

Große Lieferung heute, 283 Teile, viel Liviana, Beanies, Vel – aber keine einzige schwarze Aurea. Vier Kundinnen heute nach der Aurea schwarz gefragt (2x Gr. 1, 2x Gr. 2), alle weg ohne Kauf.

Verkauft: Hoodies 4x, Artem 3x, Iridia schwarz 3x.
Eine Beanie-Retoure, Kunde fand sie zu eng.

LG Katharina
"""),

dict(id="1002", d="2026-10-02 19:39", w="kh", subj="MUN01 Tagesabschluss 02.10.2026 + Vel Reklamation", body="""
Hallo zusammen,

31,0k (Budget 37,4k).

Reklamation: Vel navy Gr. 4 zurück, Reißverschluss defekt. Der Schieber ist abgebrochen, nach knapp drei Wochen Tragen. Kunde war ziemlich verärgert, wir haben das Geld zurückerstattet. Fotos im Anhang. Gibt es bei den anderen Stores ähnliche Fälle?

Sonst: Schal schwarz 3x, Nova oliv 2x, Aurea offwhite 2x. Wieder Aurea schwarz 0 gefragt.

Morgen ist Feiertag (Tag der Deutschen Einheit), wir haben geschlossen. Nächste Woche bin ich im Urlaub, Florian übernimmt.

LG Katharina
""", att=[dict(name="IMG_4471.JPG", kind="jpg"), dict(name="IMG_4472.JPG", kind="jpg")]),

dict(id="1005", d="2026-10-05 19:31", w="fb", subj="Abschluss Mo 05.10.", body="""
Hi,

Wiesn vorbei, Stadt wie leergefegt. 14,4k vs Bud 29,0 (-50%).

Aurea schwarz 2x verkauft (Gr. 3 und 4, die letzten), danach direkt wieder Kundin mit Wunsch Gr. 4 -> weg.
Retouren: Aurea 0 (Qualitaet, Naht am Aermel offen) und Hoodie XL.

VG Flo
"""),

dict(id="1006", d="2026-10-06 19:26", w="fb", subj="Abschluss Di 6.10.", body="""
18,0k / Bud 28,9k

Fast nur Deutsche heute, viele Stammkunden.
Amalia schwarz 2x, Nova navy 2x, Beanies.
Aurea schwarz 2 + 4 gefragt -> nix.
Aurea 1 Retoure (Geschenk).

Flo
"""),

dict(id="1007", d="2026-10-07 19:35", w="fb", subj="Abschluss Mi", body="""
Hallo,

26,2k vs 30,7k Bud. Astra Oversized 1x, Alpina 2x, Mistral navy 2x.
Riviera 5 zurueck (Qualitaet, Druckknopf locker).
Sonst nix Besonderes.

VG Flo
"""),

dict(id="1008s", d="2026-10-08 17:12", w="fb", subj="Schichtplan KW 42 - bitte checken", body="""
Hi Leute,

anbei der Plan fuer naechste Woche. Vroni Sa frei getauscht mit Lukas, Mo frueh bin ich da wegen Lieferung.
Wer was aendern will bis Freitag bei mir melden!!

Mo: Flo, Lukas, Selin, Ana
Di: Katharina, Vroni, Selin, Ana
Mi: Katharina, Flo, Lukas, Vroni
Do: Katharina, Flo, Selin, Ana
Fr: Katharina, Vroni, Lukas, Selin, Ana
Sa: Flo, Lukas, Selin, Ana, Aushilfe Max

Flo
""", cc=[]),

dict(id="1008x", d="2026-10-08 17:20", w="fb", subj="AW: Schichtplan KW 42 - bitte checken", reply="1008s", body="""
Sorry, falscher Verteiler, bitte ignorieren!
Flo
""", cc=[]),

dict(id="1008", d="2026-10-08 19:48", w="fb", subj="Abschluss Do 08.10.", body="""
Hallo zusammen,

starker Tag: 43,5k vs Bud 34,1k (+27%), Traffic 212.

Lieferung puenktlich (151 Teile), die Beanies navy sind direkt raus (4x), dazu Caps 3x, Hoodies 3x, Fiammetta 3x.
Aurea schwarz 0/1/2 weiterhin null, heute keine Anfrage, aber nur weil wir den Kunden schon an der Tuer sagen dass sie fehlt.

VG Flo
"""),

dict(id="1009f", d="2026-10-09 11:05", w="fb", sfx="_fwd", subj="WG: Reklamation Weste", to=["ops"], cc=["sw", "quality"], body="""
Zur Info, kam heute ueber das Store-Postfach. Zweiter Tib-Fall bei uns (nach dem vom 2.10.). Hab ihn angerufen, er kommt naechste Woche vorbei, Retoure ist also noch nicht im System.
Flo

-----Ursprüngliche Nachricht-----
Von: Dr. Markus Rehm <m.rehm@posteo.example>
Gesendet: Donnerstag, 8. Oktober 2026 22:47
An: mun01.store@valentino-retail.example
Betreff: Reklamation Weste

Sehr geehrte Damen und Herren,

ich habe am 18. September in Ihrer Filiale in der Maximilianstraße eine Daunenweste (Modell Vel, dunkelblau, Größe 5) gekauft. Bereits nach wenigen Wochen lässt sich der Reißverschluss nicht mehr schließen, der Zipper rutscht einfach über die Zähne und die Weste geht wieder auf.
Für ein Produkt in dieser Preisklasse finde ich das inakzeptabel. Ich bitte um Rückmeldung, ob ich die Weste umtauschen oder zurückgeben kann. Kassenbon liegt vor.

Mit freundlichen Grüßen
Markus Rehm
"""),

dict(id="1009", d="2026-10-09 19:44", w="fb", subj="Abschluss Fr 9.10.", body="""
28,5k vs Bud 41,9k. Freitag schwach, Traffic ok (181), Conversion 8%.

Beanies weiss 3x, Nova navy 3x.
Artem 3 zurueck, wieder zu gross. Das ist jetzt die 4. Arneb-Retoure/Umtausch wegen Groesse seit Launch.
Valdora offwhite 2 gefragt.

VG Flo
"""),

dict(id="1010", d="2026-10-10 19:57", w="vm", subj="Samstag 10.10.", body="""
Servus,

34k heute, Budget war 58k... des war eh utopisch, ohne Wiesn.

Viele Gäste aus den Emiraten (Herbstferien?), die kaufen aber eher Kleinzeug, Caps, Beanies, Hoodies. 3x Tricot Cardigan schwarz, 2x Vel.
Hoodie grau XXL gefragt.

Ab Montag soll's kalt werden, laut Wetter-App Schnee am Mittwoch!! ❄️

LG Vroni

Von meinem iPhone gesendet
"""),

dict(id="1012", d="2026-10-12 19:53", w="kh", subj="MUN01 Tagesabschluss 12.10.2026", body="""
Liebe Alle,

zurück aus dem Urlaub und direkt Temperatursturz: heute 5 Grad und Dauerregen.

30,8k (Budget 32,9k). 190 Besucher, aber nur 11 Bons. Die Leute kommen rein, probieren viel, fragen fast nur nach langen, warmen Sachen, und dann fehlt die Größe oder die Farbe.

Vlogo Cardigan 4x, Monteluce schwarz 3x, Liviana schwarz 2x, Astra Oversized 2x.
Aurea schwarz: 3 Anfragen (1, 2, 4). Wann kommt die Ware aus dem DC?

LG Katharina
"""),

dict(id="1013", d="2026-10-13 19:49", w="kh", subj="MUN01 Tagesabschluss 12.10.2026", body="""
Hallo zusammen,

35,7k bei 31,9k Budget, Conversion wieder normal (12 %).

Mützen und Hoodies sind gerannt: Beanie navy 4x, Hoodie schwarz 4x, Shirts 3x, Vlogo Cardigan 3x.
Aria offwhite 00 gefragt, haben wir nicht.
Shirt schwarz L ist aus.

Für morgen ist Schnee angesagt, wir haben die Mützen- und Handschuh-Wand vorne aufgefüllt mit allem, was im Lager war.

LG Katharina
"""),

dict(id="1014", d="2026-10-14 20:16", w="kh", subj="MUN01 Tagesabschluss 14.10. - ERSTER SCHNEE", importance="high", body="""
Liebe Alle,

erster Schnee in München und der Laden war ab 10:30 voll.

Umsatz 56,6k, Budget 32,8k (+72 %). 204 Besucher, 23 Bons.

Verkauft: Liviana schwarz 4x, Cosimo navy 3x, Monteluce schwarz 3x, Vtrack Gtx 3x, Beanies.

Was fehlt (alles heute konkret gefragt):
- Beanie navy: ab ca. 15 Uhr ausverkauft, danach noch 3 Kunden
- Liviana navy 2 (2 Kundinnen) und 3
- Liviana schwarz 0 ist jetzt auch weg
- Monteluce grau 5 (2x)
- Aurea schwarz 0 und 4
- Nova navy 4
- Crewneck weiß M
- Vtrack Gtx 42 und 43 sind leer, Ettore 5 auch

Die Kunden wollen lang und warm, egal welches Modell. Bitte prüft dringend, ob wir aus der Donnerstag-Lieferung mehr Liviana und Mützen bekommen können.

LG Katharina
"""),

dict(id="1014r", d="2026-10-14 21:32", w="sw", subj="AW: MUN01 Tagesabschluss 14.10. - ERSTER SCHNEE", reply="1014", quote="1014",
     to=["kh"], cc=["ops", "merch"], body="""
Hallo Katharina,

super Tag, danke. Damit ich bei Merch Druck machen kann: wie viele Liviana (Farbe/Größe) und Mützen bräuchtet ihr realistisch bis Ende nächster Woche? Und habt ihr noch Ware, die nicht dreht und die wir nach Berlin oder Zürich geben könnten?

Gruß
Stefan
"""),

dict(id="1015r", d="2026-10-15 09:41", w="kh", subj="AW: MUN01 Tagesabschluss 14.10. - ERSTER SCHNEE", reply="1014r", quote="1014r",
     to=["sw"], cc=["ops", "merch"], body="""
Hallo Stefan,

grob geschätzt bis Ende nächster Woche:
- Liviana navy: 2x Gr. 2, 2x Gr. 3, 1x Gr. 1
- Liviana schwarz: 2x Gr. 0, 2x Gr. 1
- Beanie navy: 15 Stück, weiß 10
- Aurea schwarz 0-2: mindestens 10, eher mehr (wir haben seit Ende September täglich Anfragen)
- Monteluce grau 5: 2

Abgeben könnten wir: Astra Cape (steht seit Launch, 1 verkauft) und ein paar Mario/Eliano aus SS, die eh niemand mehr will. Astra Oversized hellblau bewegt sich auch kaum.

Heute kommt die Lieferung, ich melde mich heute Abend, was davon schon drin war.

Viele Grüße
Katharina
"""),

dict(id="1015", d="2026-10-15 19:58", w="fb", subj="Abschluss Do 15.10.", body="""
Hallo,

50,7k vs Bud 36,3k. Traffic 263 (!), Conversion 12,5%.

Lieferung puenktlich, 208 Teile: Liviana schwarz + navy in fast allen Groessen, 14 Beanies navy, 8 weiss. Danke an wen auch immer!
Schals schwarz 4x, Artem 3x, Beanies navy 2x (rest liegt noch).
Aurea schwarz 1 gefragt -> nix. Wieder keine Aurea schwarz in der Lieferung.
Fiammetta 0 Retoure, Reissverschluss Tasche kaputt.

Schnee taut schon wieder, morgen soll es aber nochmal kalt werden.

VG Flo
"""),

dict(id="1016", d="2026-10-16 19:42", w="fb", subj="Abschluss Fr 16.10.", body="""
Hi,

Umsatz 16,2k vs Bud 45,7k -> +34%, super Tag

Liviana schwarz 5x (!!), Crewneck weiss 3x, Alpina 3x, Hoodies 3x, Amalia schwarz 3x.
Aurea schwarz 0, 1 (2x), 2 gefragt. Laut DC ist die Aurea schwarz seit heute wieder verfuegbar - wann bekommen wir was???
Monteluce navy 6 gefragt.

VG Flo
"""),

dict(id="1016c", d="2026-10-16 20:09", w="fb", subj="Korrektur Abschluss Fr 16.10.", reply="1016", body="""
Sorry, Tippfehler: Umsatz war natuerlich 61,2k, nicht 16,2k.
Flo
"""),

dict(id="1017", d="2026-10-17 19:49", w="vm", subj="Sa 17.10. Abschluss", body="""
Servus zusammen,

was für ein Samstag! 69,4k, Budget 62k, 331 Leute im Laden, wir waren zu fünft und es hat trotzdem nicht gereicht.

Beanies weiß 5x, Nova navy 5x, Hoodies 4x, Liviana schwarz 3x, Iridia schwarz 3x.

Was wir NICHT hatten:
- Aurea schwarz Gr. 1 → 3 Kundinnen!! + 1x Gr. 2
- Iridia offwhite Gr. 1 → auch 3x gefragt, mei
- Nova oliv 3, Monteluce grau 4, Shirt schwarz L
- Alpina 36 und 37

Liviana schwarz 0 schon wieder weg, Iridia schwarz 2 auch.

Retoure Vel Gr. 3, Kunde sagt der Reißverschluss geht immer wieder auf. Im System hab i "Qualität" ausgewählt, gibt ja keinen eigenen Grund dafür. Plus ein Hoodie M.

Pfiat eich, schönen Sonntag
Vroni

Von meinem iPhone gesendet
"""),

dict(id="1019", d="2026-10-19 19:37", w="kh", subj="MUN01 Tagesabschluss 19.10.2026", body="""
Liebe Alle,

33,8k (Budget 33,1k). Die Kälte lässt nach, Frequenz wieder normal (159).

Rucksäcke 3x, Astra Balaclava 2x (das einzige Teil aus der Kapsel, das wirklich läuft), Nova navy und oliv je 2x.
Nicht bedient: Aurea schwarz 0, Iridia offwhite 3, Ettore 7, Valdora offwhite 1.
Alpina 38 zurück, zu klein.

Vroni hat mir von Samstag erzählt, Iridia offwhite fehlt uns in 1 und 3. Könnt ihr prüfen, ob es eine Umlagerung aus einem anderen Store gibt?

LG Katharina
"""),

dict(id="1020", d="2026-10-20 19:51", w="kh", subj="MUN01 Tagesabschluss 20.10.2026", body="""
Hallo zusammen,

Föhn, 15 Grad, und es ist wie abgeschaltet: 26,0k bei 33,6k Budget.

Viele Kunden aus den Emiraten und der Schweiz. Cortina 2x, Handschuhe 2x, Vtrack 2x.
Gefragt und nicht da: Aurea schwarz 2, Iridia schwarz 2, Nova oliv 5, Cosimo navy 7, Shirt schwarz L.

Gute Nachricht: Laut Avis kommt die Lieferung am Donnerstag mit Aurea schwarz in allen Größen, insgesamt 35 Stück. Endlich! Wir werden die Kundinnen von der Warteliste anrufen.

LG Katharina
"""),

dict(id="1021", d="2026-10-21 19:46", w="kh", subj="MUN01 Tagesabschluss 21.10.2026", body="""
Liebe Alle,

schwacher Mittwoch: 16,9k bei 34,1k Budget, Conversion 5,5 %. 163 Besucher, viele Amerikaner (ca. ein Viertel), die meisten nur schauen.

Anfragen ohne Ware:
- Aurea beige 1
- Fiammetta navy 0
- Iridia schwarz 2
- Artem schwarz 7
- Astra Oversized hellblau XS (die kleinste Größe haben wir bei Astra gar nicht bekommen)
- Shirt navy M

Warteliste Aurea schwarz steht bei 11 Kundinnen, morgen kommt hoffentlich die Ware.

LG Katharina
"""),
]
