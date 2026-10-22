# -*- coding: utf-8 -*-
"""STM01 - St. Moritz Via Serlas (resort, open 7/7 until Zwischensaison from Oct 19). Hand-authored closing emails.

Writers: Gian-Andrea Caviezel (SM, Engadiner, calm, Romansh greetings "Allegra"/"Cordials salüds", CHF with '.–'),
Sabrina Gredig (ASM, practical, lists, logistics of the closure), Nicola Tognina (SA from the Bergell, weekends,
German with Italian words and small errors, iPhone).
"""
DOM = "moncler-retail.example"

PEOPLE = {
    "gc": dict(name="Gian-Andrea Caviezel", addr=f"gian-andrea.caviezel@{DOM}", mailer="outlook",
               footer="\n\nGian-Andrea Caviezel\nStore Manager | Moncler St. Moritz\nVia Serlas, 7500 St. Moritz\n+41 81 833 41 90"),
    "sg": dict(name="Sabrina Gredig", addr=f"sabrina.gredig@{DOM}", mailer="outlook"),
    "nt": dict(name="Nicola Tognina", addr=f"nicola.tognina@{DOM}", mailer="iphone"),
    "store": dict(name="Moncler St. Moritz", addr=f"stm01.store@{DOM}", mailer="outlook"),
}

EMAILS = [
dict(id="0831", d="2026-08-31 18:52", w="gc", subj="STM01 Tagesabschluss 31.8.", body="""
Allegra

Umsatz CHF 3'520.– (Budget 5'220.–), 2 Bons.

Die Sommersaison ist durch, im Dorf sind nur noch wenige Gäste. Trotzdem 7 Anfragen, die wir nicht bedienen konnten:
Maire offwhite 00, Tib schwarz 4, Marin schwarz 5 und weiss 3, Peyre 3, Tricot Cardigan schwarz L, Polo navy XXL.

Cordials salüds
Gian-Andrea
"""),

dict(id="0901", d="2026-09-01 18:47", w="gc", subj="STM01 Tagesabschluss 1.9.", body="""
Allegra

Heute leider negativ: CHF -60.– (ein Beanie verkauft, ein T-Shirt L zurückgenommen).
27 Leute im Laden, fast nur Einheimische und Zweitwohnungsbesitzer.

Gefragt: Maire offwhite 4, Montgenevre schwarz 4 und grau 5, Chamonix S.

Cordials salüds
Gian-Andrea
"""),

dict(id="0902", d="2026-09-02 18:41", w="sg", subj="St. Moritz – Abschluss 2.9.", body="""
Hoi zusammen

Heute kein Verkauf, CHF 0.–

Drei Kunden mit konkreten Wünschen, alles nicht an Lager: Tib schwarz 4, Tricot Cardigan navy M, Makaio Rucksack schwarz.

Gruess
Sabrina
"""),

dict(id="0903", d="2026-09-03 18:55", w="gc", subj="STM01 Tagesabschluss 3.9.", body="""
Allegra

CHF 4'020.– (Budget 6'330.–). Ein Paar aus Riad und ein Amerikaner, Ilvaro offwhite, Karakorum schwarz, Rollkragen und ein Shirt.
Karakorum schwarz 5 ist jetzt auf null.

Cordials salüds
Gian-Andrea
"""),

dict(id="0904", d="2026-09-04 18:49", w="sg", subj="St. Moritz – Abschluss 4.9.", body="""
Hoi zusammen

CHF 3'750.– (Budget 7'680.–), 6 Bons, nur Kleinteile.
Lieferung pünktlich, 51 Teile, alles verräumt.
Trailgrip GTX 39 gefragt.

Gruess
Sabrina
"""),

dict(id="0906", d="2026-09-06 18:58", w="nt", subj="Abschluss Sa + So", body="""
Ciao a tutti

Wochenende zusammen:

Samstag CHF 14'290.– (budget 11'020) bene!! Eine arabische Familie, wohnen in Champfèr, 2x Peyre und 2x Chamonix, plus Caps und Shirts.
Nicht da: Maire navy 4, Tricot Cardigan schwarz L
Retour Karakorum 5, Kunde hat sich umentscheidet.

Sonntag CHF 3'430.– (budget 7'310). Ruhig. Ilvaro rosa verkauft an eine Dame aus Zürich, Insolux, Rucksack, Cap.

Chamonix M und Cap weiss sind jetzt fertig.

Saluti
Nicola

Von meinem iPhone gesendet
"""),

dict(id="0907", d="2026-09-07 18:44", w="gc", subj="STM01 Tagesabschluss 7.9.", body="""
Allegra

CHF 5'420.– (Budget 5'010.–), knapp über Budget mit 3 Bons. Maya schwarz, Montgenevre grau, Tricot, Tib.
Wieder Maire offwhite 00 gefragt, die haben wir schon im August nicht gehabt.

Cordials salüds
Gian-Andrea
"""),

dict(id="0908", d="2026-09-08 18:50", w="gc", subj="STM01 Tagesabschluss 8.9.", body="""
Allegra

CHF 3'880.–. Zwei Trailgrip GTX, ein Tricot und eine Bady rosa an eine chinesische Kundin.

Cordials salüds
Gian-Andrea
"""),

dict(id="0909", d="2026-09-09 18:46", w="sg", subj="St. Moritz – Abschluss 9.9.", body="""
Hoi zusammen

CHF 1'320.– netto. Eigentlich 6 Teile verkauft, aber eine Maya Gr. 5 kam zurück (Qualität, Daunen treten an der Naht aus), das drückt den Tag.
Trailgrip GTX 41 und 43 jetzt auf null.

Gruess
Sabrina
"""),

dict(id="0910", d="2026-09-10 18:53", w="gc", subj="STM01 Tagesabschluss 10.9.", body="""
Allegra

CHF 5'700.– (Budget 5'890.–). Peyre, Tib, Chambre und eine Ilvaro schwarz.
Chambre schwarz und Peyre 3 sind ausverkauft.

Cordials salüds
Gian-Andrea
"""),

dict(id="0911", d="2026-09-11 18:58", w="sg", subj="St. Moritz – Abschluss 11.9.", body="""
Hoi zusammen

Super Freitag für uns: CHF 12'590.–, Budget 6'520.–.
2x Peyre an zwei Herren, die schon für den Winter einkaufen, dazu Handschuhe, Hoodie, Crewneck, Karakorum.
Lieferung pünktlich (30 Teile).
Trailgrip GTX 43 gefragt, haben wir immer noch nicht.

Gruess
Sabrina
"""),

dict(id="0912", d="2026-09-12 18:39", w="nt", subj="Abschluss Samstag", body="""
Ciao

CHF 9'820.– heute, budget 9'050, va bene.
Crewneck schwarz 2x, Peyre, Beanie, Schal, Cap.
Gefragt aber nicht da: Ambrine braun 3, Polo navy M, Insolux offwhite 35.

Peyre 5 auch fertig jetzt.

Nicola

Von meinem iPhone gesendet
"""),

dict(id="0913", d="2026-09-13 18:33", w="nt", subj="So 13.9.", body="""
Ciao,
oggi quasi niente... CHF 169.– netto. 2 Caps verkauft, ein Beanie zurück (Farbe).
Flammette schwarz 3 gefragt.
Nicola

Von meinem iPhone gesendet
"""),

dict(id="0914", d="2026-09-14 18:48", w="gc", subj="STM01 Tagesabschluss 14.9.", body="""
Allegra

CHF 2'530.–, Maya schwarz und Tib schwarz. Sehr ruhig.

Cordials salüds
Gian-Andrea
"""),

dict(id="0916", d="2026-09-16 18:51", w="sg", subj="St. Moritz – Abschluss 16.9.", body="""
Hoi zusammen

Gestern ist der Abschluss bei mir untergegangen, sorry: 15.9. CHF 1'895.–, Crewneck schwarz L gefragt.

Heute CHF 4'120.– (Budget 4'750.–). Hoodie schwarz 2x, Rollkragen, Cable Knit, Maya schwarz.
Gefragt: Karakorum schwarz 6, Crewneck schwarz S.
Tib schwarz 3 jetzt auf null.

Gruess
Sabrina
"""),

dict(id="0917", d="2026-09-17 18:42", w="gc", subj="STM01 Tagesabschluss 17.9.", body="""
Allegra

CHF 390.– (ein Paar Handschuhe). 20 Leute im Laden.
Eine Kundin hat nach der Ambrine in braun gefragt, Gr. 0. Die zweite Anfrage nach dem Braun in einer Woche.

Cordials salüds
Gian-Andrea
"""),

dict(id="0918", d="2026-09-18 18:57", w="sg", subj="St. Moritz – Abschluss 18.9.", body="""
Hoi zusammen

CHF 5'960.– (Budget 6'000.–). Schals schwarz 2x, Insolux 2x, Chamonix, Crewneck, Tricot.
Lieferung pünktlich (38 Teile).

Gruess
Sabrina
"""),

dict(id="0920", d="2026-09-20 18:44", w="nt", subj="Abschluss weekend 19-20.9.", body="""
Ciao a tutti

Sa: CHF 6'850.– (budget 8'850). Peyre, Chamonix, Hermine offwhite, Ilvaro schwarz. Hoodie schwarz L gefragt, nicht da.
So: CHF 1'930.– (budget 5'820). Rucksack, Shirt, Insolux. Ein Kunde wollte Ilvaro offwhite 3.

Ruhig, i turisti sono finiti. Am Abend schon 4 Grad.

Saluti
Nicola

Von meinem iPhone gesendet
"""),

dict(id="0921", d="2026-09-21 18:40", w="gc", subj="STM01 Tagesabschluss 21.9.", body="""
Allegra

CHF 1'310.–, drei Kleinteile.

Cordials salüds
Gian-Andrea
"""),

dict(id="0922", d="2026-09-22 18:46", w="gc", subj="STM01 Tagesabschluss 22.9.", body="""
Allegra

CHF 3'910.– (Budget 4'850.–). Eine russische Familie, Chamonix und Montgenevre schwarz, dazu Beanie und Insolux.
Montgenevre schwarz 5 und Chamonix M auf null.

Cordials salüds
Gian-Andrea
"""),

dict(id="0923", d="2026-09-23 18:52", w="sg", subj="St. Moritz – Abschluss 23.9.", body="""
Hoi zusammen

CHF 6'650.–, Budget 5'000.–. Maire navy, Maya schwarz, Montcla, Montgenevre schwarz, Beanie weiss.
Maire navy 1 jetzt aus.

Gruess
Sabrina
"""),

dict(id="0924", d="2026-09-24 18:55", w="gc", subj="STM01 Tagesabschluss 24.9.", body="""
Allegra

Leider negativ: CHF -2'540.– netto.
Zwei Insolux (38 und 40) kamen zurück, waren Geschenke, dazu ein Montgenevre Gr. 5 (zu gross). Verkauft nur Beanie und Trailgrip.
Und wieder Maire offwhite 00 gefragt, das ist jetzt die dritte Anfrage seit Ende August.

Cordials salüds
Gian-Andrea
"""),

dict(id="0925", d="2026-09-25 18:48", w="sg", subj="St. Moritz – Abschluss 25.9.", body="""
Hoi zusammen

CHF 4'110.–. Crewneck, Insolux, Montgenevre navy, Tib.
Lieferung pünktlich (33 Teile).

Gruess
Sabrina
"""),

dict(id="0926", d="2026-09-26 18:37", w="nt", subj="Abschluss Sa 26.9.", body="""
Ciao

CHF 4'700.–, budget 10'330, niente da fare. Halbe Kunden aus Dubai, aber haben fast nur geschaut. 2 Beanie weiss, Peyre, Flammette navy.
Shirt weiss XXL gefragt.

Nicola

Von meinem iPhone gesendet
"""),

dict(id="0927", d="2026-09-27 18:31", w="nt", subj="So", body="""
CHF 1'830.– Beanie + Maya schwarz. Basta.
Nicola

Von meinem iPhone gesendet
"""),

dict(id="0928", d="2026-09-28 18:56", w="gc", subj="STM01 Tagesabschluss 28.9. – 2x Tib defekt", body="""
Allegra

CHF 2'960.– (Budget 4'860.–), aber es sind zwei Reklamationen dabei, die ich melden möchte:

Zwei Stammkunden haben ihre Tib schwarz zurückgebracht (Gr. 4 und Gr. 6, beide Ende August gekauft). Bei beiden schliesst der Reissverschluss nicht mehr richtig, der Schieber rutscht über die Zähne. Wir haben beide zurückerstattet, die Gilets liegen im Lager.
Ist das bekannt? Bei zwei Fällen am gleichen Tag glaube ich nicht an Zufall.

Sonst: Rucksack 2x, Chamonix, Cap, Tricot, Montcla. Crewneck S zurück (Grösse).
Gefragt: Montcla schwarz 1, Montgenevre grau 2, Crewneck schwarz S.

Cordials salüds
Gian-Andrea
""", att=[dict(name="Tib_Reissverschluss_1.jpg", kind="jpg")]),

dict(id="0929", d="2026-09-29 18:43", w="gc", subj="STM01 Tagesabschluss 29.9.", body="""
Allegra

CHF 4'350.–. Flammette, Chambre, Ilvaro offwhite.
Gefragt: Maire navy 1 und die Ilvaro rosa in Gr. 1, beides nicht da.

Cordials salüds
Gian-Andrea
"""),

dict(id="1001", d="2026-10-01 18:49", w="gc", subj="STM01 Tagesabschluss 1.10.", body="""
Allegra

Nachtrag 30.9. (ist gestern nicht rausgegangen): CHF 5'910.–, Budget 5'650.–. Gefragt: Polaris Cape weiss XL, Tricot schwarz L, Trailgrip GTX 44 und grau 40.

Heute CHF 2'520.–. Schal, Beanie, Insolux, Chambre.
Chambre schwarz 1 jetzt aus.

Cordials salüds
Gian-Andrea
"""),

dict(id="1002", d="2026-10-02 18:51", w="sg", subj="St. Moritz – Abschluss 2.10.", body="""
Hoi zusammen

CHF 6'050.– (Budget 7'590.–). Trailgrip, Insolux, Tib, Maire navy, Hermine offwhite.
Lieferung pünktlich (22 Teile).

Gefragt und nicht da: Maire beige 3, Ilvaro schwarz 4, Ambrine braun 0 (die dritte Anfrage nach der braunen Ambrine!).

Gruess
Sabrina
"""),

dict(id="1004", d="2026-10-04 18:47", w="nt", subj="Abschluss Sa+So 3-4.10.", body="""
Ciao a tutti

Sabato CHF 7'110.– (budget 10'450). 2x Peyre, 2x Shirt weiss, Crewneck, Maire offwhite. Gefragt Shirt weiss XS und Insolux offwhite 37.
Domenica CHF 7'370.– (budget 7'110) 👍 nochmal 2x Peyre, 2x Beanie schwarz, Cap, Tricot, Insolux.

Die Peyre geht gut, ma Gr. 3 ist jetzt fertig. Viele Leute aus Mailand am Wochenende, Ferienwohnungen aufmachen für den Winter.

Saluti
Nicola

Von meinem iPhone gesendet
"""),

dict(id="1005", d="2026-10-05 18:39", w="gc", subj="STM01 Tagesabschluss 5.10.", body="""
Allegra

CHF 1'830.–. Peyre, Handschuhe und eine Maire beige verkauft, aber eine Peyre Gr. 4 vom Wochenende kam zurück (Kunde hat es sich anders überlegt).
Peyre 3 erneut gefragt.

Cordials salüds
Gian-Andrea
"""),

dict(id="1006", d="2026-10-06 18:44", w="gc", subj="STM01 Tagesabschluss 6.10.", body="""
Allegra

CHF 2'920.–. Crewneck grau, Maya schwarz, Chambre. Ruhig.

Cordials salüds
Gian-Andrea
"""),

dict(id="1007", d="2026-10-07 18:50", w="sg", subj="St. Moritz – Abschluss 7.10.", body="""
Hoi zusammen

CHF 7'190.–, Budget 6'190.–. Peyre 2x, Schal beige, Beanies, Rucksack.
Montgenevre grau 5 gefragt. Peyre 4 jetzt auch auf null.

Gruess
Sabrina
"""),

dict(id="1008", d="2026-10-08 18:45", w="gc", subj="STM01 Tagesabschluss 8.10.", body="""
Allegra

CHF 3'570.– (Budget 6'860.–). Handschuhe, Montgenevre grau, Maire navy.

Die Peyre fehlt uns jetzt richtig: heute zwei Herren mit Wunsch Gr. 2 und Gr. 4, beide ohne Kauf weg. Dazu Polaris Cape schwarz L gefragt.
Bitte prüfen, ob für die letzte Lieferung vor der Zwischensaison noch Peyre 2/3/4 möglich sind.

Cordials salüds
Gian-Andrea
"""),

dict(id="1009", d="2026-10-09 18:52", w="sg", subj="St. Moritz – Abschluss 9.10.", body="""
Hoi zusammen

CHF 7'260.– (Budget 7'980.–). Peyre, Chamonix, Handschuhe, Tricot navy, Cable Knit.
Lieferung pünktlich, 17 Teile, immerhin 3 Peyre (Gr. 2 und 3), aber keine 4.

Gruess
Sabrina
"""),

dict(id="1010", d="2026-10-10 18:41", w="nt", subj="Abschluss Sabato 10.10.", body="""
Ciao

CHF 9'930.– (budget 11'430). Schal grau 2x, Chamonix, Handschuhe, Polo, Crewneck.
Handschuhe sind jetzt fertig (letzte verkauft).

Am Montag soll Schnee kommen bis ins Dorf!

Nicola

Von meinem iPhone gesendet
"""),

dict(id="1011", d="2026-10-11 18:36", w="nt", subj="Abschluss So 11.10.", body="""
Ciao a tutti

CHF 9'330.–, budget 7'800, bene. Gäste aus Abu Dhabi und eine russische Familie. Montcla, Montgenevre, Hoodie, Crewneck, Shirt.
Bady rosa 4 gefragt, haben wir nicht.

Montcla schwarz 3 und Tib schwarz 3 jetzt fertig.

Nicola

Von meinem iPhone gesendet
"""),

dict(id="1012", d="2026-10-12 18:48", w="gc", subj="STM01 Tagesabschluss 12.10.", body="""
Allegra

Es schneit seit Mittag. CHF 2'660.– (Budget 6'570.–), nur Einheimische unterwegs.

Gefragt und nicht vorhanden: Flammette navy 3, Montcla schwarz 3, Arneb schwarz 3, Cap weiss.

Cordials salüds
Gian-Andrea
"""),

dict(id="1013", d="2026-10-13 18:51", w="gc", subj="STM01 Tagesabschluss 13.10.", body="""
Allegra

20 cm Neuschnee im Dorf, Julier nur mit Ketten. CHF 5'590.– (Budget 5'920.–).
Beanie weiss 2x, Chamonix, Montgenevre schwarz, Ambrine schwarz.
Gefragt: Flammette schwarz 3, Chamonix S, Insolux 35.

Cordials salüds
Gian-Andrea
"""),

dict(id="1014", d="2026-10-14 18:46", w="sg", subj="St. Moritz – Abschluss 14.10.", body="""
Hoi zusammen

CHF 2'530.–, Peyre und Beanie. Strassen schlecht, kaum jemand unterwegs.
Hoodie schwarz M gefragt.

Ab nächster Woche ist ja Zwischensaison, ich bereite morgen die Rücksendung ans DC vor (Kartons und Lieferscheine bestellt).

Gruess
Sabrina
"""),

dict(id="1014q", d="2026-10-14 20:10", w="sw", subj="STM01 – länger offen wegen Schnee?", to=["gc"], cc=["sg", "ops"], body="""
Hallo Gian-Andrea,

bei euch liegt ja jetzt richtig Schnee. Macht es Sinn, dass ihr noch bis 25.10. offen bleibt und erst dann schliesst? Die Nachfrage nach warmen Sachen ist überall in der Region stark.

Gruss
Stefan
"""),

dict(id="1015r", d="2026-10-15 08:37", w="gc", subj="AW: STM01 – länger offen wegen Schnee?", reply="1014q", quote="1014q", to=["sw"], cc=["sg", "ops"], body="""
Allegra Stefan

Ich verstehe die Idee, aber ich würde es nicht machen:
- Die Ferien vom Team sind seit dem Sommer gebucht (Sabrina ab 21.10., Nicola ab 19.10., ich ab 22.10.)
- Die meisten Hotels sind bereits zu, die Bergbahnen öffnen erst Ende November
- Die Kunden, die jetzt wegen dem Schnee hochkommen, sind Wochenendgäste, das sehen wir dieses Wochenende sowieso noch

Wir nutzen das Wochenende voll und schliessen wie geplant am Sonntagabend. Die Restware geht am Dienstag ans DC zurück, dann kann Zürich oder München davon profitieren.

Cordials salüds
Gian-Andrea
"""),

dict(id="1015", d="2026-10-15 18:54", w="gc", subj="STM01 Tagesabschluss 15.10.", body="""
Allegra

Die ersten Schnee-Gäste aus Zürich und Mailand sind da: CHF 10'180.– (Budget 7'240.–).
Maya schwarz 3x (eine kam am Nachmittag wieder zurück, Gr. 3, Kunde hat es sich anders überlegt), Tricot schwarz 2x, Insolux 2x.
Crewneck grau XL gefragt.

Cordials salüds
Gian-Andrea
"""),

dict(id="1016", d="2026-10-16 18:58", w="sg", subj="St. Moritz – Abschluss 16.10.", body="""
Hoi zusammen

CHF 9'950.– (Budget 9'250.–).
Letzte Lieferung vor der Pause angekommen, nur 12 Teile (2 Peyre, Montcla, Chamonix, Handschuhe usw.). Die eine Peyre 4 war nach einer Stunde verkauft.

Nicht bedient:
- Peyre 4 (2 Kunden)
- Ilvaro schwarz 0
- Tricot Cardigan schwarz L
- Rollkragen navy XL
- Insolux 39

Beanie weiss ist ausverkauft.

Gruess
Sabrina
"""),

dict(id="1017", d="2026-10-17 18:42", w="nt", subj="Abschluss Sa 17.10. 🎿", body="""
Ciao a tutti

Sabato pazzesco per noi: CHF 16'870.–, budget 12'800! 72 Leute im Laden, die Hälfte Wochenendgäste wegen Schnee.

Rollkragen schwarz 2x, Peyre, Beanie, Trailgrip, Rucksack...

Aber viele Sachen nicht da, peccato:
- Peyre 4 (2x!!)
- Hermine offwhite 3
- Flammette 00
- Montcla 7
- Montgenevre grau 3
- Polaris Cape weiss XL
- Rollkragen XXL
- Beanie schwarz

Morgen letzter Tag, dann Ferien 🙌

Nicola

Von meinem iPhone gesendet
"""),

dict(id="1017d", d="2026-10-17 18:42", w="nt", sfx="_dup", subj="Abschluss Sa 17.10. 🎿", body="""
Ciao a tutti

Sabato pazzesco per noi: CHF 16'870.–, budget 12'800! 72 Leute im Laden, die Hälfte Wochenendgäste wegen Schnee.

Rollkragen schwarz 2x, Peyre, Beanie, Trailgrip, Rucksack...

Aber viele Sachen nicht da, peccato:
- Peyre 4 (2x!!)
- Hermine offwhite 3
- Flammette 00
- Montcla 7
- Montgenevre grau 3
- Polaris Cape weiss XL
- Rollkragen XXL
- Beanie schwarz

Morgen letzter Tag, dann Ferien 🙌

Nicola

Von meinem iPhone gesendet
"""),

dict(id="1018", d="2026-10-18 19:24", w="gc", subj="STM01 letzter Tagesabschluss vor Zwischensaison – 18.10.", importance="high", body="""
Allegra zusammen

Letzter Verkaufstag der Sommer-/Herbstsaison: CHF 9'170.– (Budget 8'990.–), 13 Teile.
Chamonix 2x, Schals schwarz 2x, Peyre, Handschuhe, Trailgrip grau.
Eine Peyre 4 kam zurück (Kunde hat es sich anders überlegt), die geht jetzt mit ans DC.

Auch heute noch Anfragen, die wir nicht bedienen konnten:
Chamonix L (2x), Maya schwarz 6, Rollkragen braun XL, Crewneck schwarz S und M, Beanie weiss, Makaio Rucksack.

Zur Schliessung:
- Ab morgen, 19.10., ist die Boutique für die Zwischensaison geschlossen.
- Montag Inventur, Dienstag 20.10. Abholung der gesamten Ware durch GEODIS zurück ins DC.
- Das Team ist ab dieser Woche in den Ferien. Wiedereröffnung am Freitag, 4. Dezember 2026.
- Dringende Anfragen bis dahin bitte an Stefan bzw. an Zürich.

Grazcha fich an alle für die Unterstützung in dieser Saison!

Cordials salüds
Gian-Andrea
"""),

dict(id="1019", d="2026-10-19 17:12", w="sg", subj="STM01 – Inventur + Rücksendung DC", to=["ops"], cc=["sw", "merch"], body="""
Hoi zusammen

Inventur ist abgeschlossen. Kurz die Eckdaten:

- 21 Kartons gepackt, ca. 310 Teile (Lieferschein-Nr. kommt morgen vom Fahrer)
- Abholung GEODIS morgen, Dienstag 20.10., zwischen 9 und 12 Uhr
- 2 Tib schwarz mit defektem Reissverschluss (Retouren vom 28.9.) separat verpackt und markiert "Quality"
- Differenzen Inventur: 1x Beanie schwarz fehlt, 1x Cap weiss zu viel (wurde wohl falsch gescannt)
- Ausstellungsware (Puppen) bleibt im Laden

Gruess
Sabrina
""", att=[dict(name="STM01_Inventur_19102026.csv", kind="csv", enc="cp1252", text=(
    "Store;Datum;Kartons;Teile;Bemerkung\r\n"
    "STM01;19.10.2026;21;310;Rücksendung DC, Abholung 20.10. GEODIS\r\n"
    "STM01;19.10.2026;1;2;Tib schwarz DEFEKT (Quality)\r\n"))]),

dict(id="1020", d="2026-10-20 13:05", w="sg", subj="AW: STM01 – Inventur + Rücksendung DC", reply="1019", quote="1019", to=["ops"], cc=["sw", "merch"], body="""
Ware ist um 11:40 abgeholt worden, 21 Kartons + 1 Karton Quality. Lieferschein im Anhang (Foto).
Laden ist zu, Alarm aktiviert, Schlüssel hat Gian-Andrea.
Ich bin ab morgen in den Ferien bis 15.11.

Gruess
Sabrina
""", att=[dict(name="IMG_8812.jpg", kind="jpg")]),

dict(id="1021q", d="2026-10-21 09:15", w="sw", subj="Peyre/Chamonix von STM nach ZRH?", to=["sg", "store"], cc=["gc"], body="""
Hallo Sabrina,

Zürich fragt nach Peyre und Chamonix in L. Könnt ihr von eurem Restbestand noch etwas direkt nach Zürich schicken statt ins DC?

Danke
Stefan
"""),

dict(id="1021a", d="2026-10-21 09:15", w="sg", subj="Automatische Antwort: Peyre/Chamonix von STM nach ZRH?", reply="1021q", auto=True, to=["sw"], cc=[], body="""
Ich bin bis 15.11.2026 in den Ferien und habe keinen Zugriff auf meine E-Mails. Ihre Nachricht wird nicht weitergeleitet.
Für dringende Anliegen wenden Sie sich bitte an retail-ops-dach@moncler-retail.example.

Sabrina Gredig
"""),

dict(id="1021b", d="2026-10-21 09:15", w="store", subj="Automatische Antwort: Peyre/Chamonix von STM nach ZRH?", reply="1021q", auto=True, to=["sw"], cc=[], body="""
Allegra! Unsere Boutique in St. Moritz ist vom 19. Oktober bis 3. Dezember 2026 geschlossen. Ab dem 4. Dezember sind wir gerne wieder für Sie da.
Gentile cliente, la boutique è chiusa dal 19 ottobre al 3 dicembre 2026.
Dear client, our boutique is closed from 19 October to 3 December 2026.

Moncler St. Moritz
"""),
]
