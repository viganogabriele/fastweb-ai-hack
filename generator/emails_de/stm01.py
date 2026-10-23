# -*- coding: utf-8 -*-
"""STM01 - St. Moritz Via Serlas (resort, open 7/7 until Zwischensaison from Oct 19). Hand-authored closing emails.

Writers: Gian-Andrea Caviezel (SM, Engadiner, calm, Romansh greetings "Allegra"/"Cordials salüds", CHF with '.–'),
Sabrina Gredig (ASM, practical, lists, logistics of the closure), Nicola Tognina (SA from the Bergell, weekends,
German with Italian words and small errors, iPhone).
"""
DOM = "valentino-retail.example"

PEOPLE = {
    "gc": dict(name="Gian-Andrea Caviezel", addr=f"gian-andrea.caviezel@{DOM}", mailer="outlook",
               footer="\n\nGian-Andrea Caviezel\nStore Manager | Valentino St. Moritz\nVia Serlas, 7500 St. Moritz\n+41 81 833 41 90"),
    "sg": dict(name="Sabrina Gredig", addr=f"sabrina.gredig@{DOM}", mailer="outlook"),
    "nt": dict(name="Nicola Tognina", addr=f"nicola.tognina@{DOM}", mailer="iphone"),
    "store": dict(name="Valentino St. Moritz", addr=f"stm01.store@{DOM}", mailer="outlook"),
}

EMAILS = [
dict(id="0831", d="2026-08-31 18:52", w="gc", subj="STM01 Tagesabschluss 31.8.", body="""
Allegra

Umsatz CHF 3'520.– (Budget 5'220.–), 2 Bons.

Die Sommersaison ist durch, im Dorf sind nur noch wenige Gäste. Trotzdem 7 Anfragen, die wir nicht bedienen konnten:
Aurea offwhite 00, Vel schwarz 4, Mario schwarz 5 und weiss 3, Piero 3, Tricot Cardigan schwarz L, Jersey Polo navy XXL.

Cordials salüds
Gian-Andrea
"""),

dict(id="0901", d="2026-09-01 18:47", w="gc", subj="STM01 Tagesabschluss 1.9.", body="""
Allegra

Heute leider negativ: CHF -60.– (ein Beanie verkauft, ein T-Shirt L zurückgenommen).
27 Leute im Laden, fast nur Einheimische und Zweitwohnungsbesitzer.

Gefragt: Aurea offwhite 4, Monteluce schwarz 4 und grau 5, Cortina S.

Cordials salüds
Gian-Andrea
"""),

dict(id="0902", d="2026-09-02 18:41", w="sg", subj="St. Moritz – Abschluss 2.9.", body="""
Hoi zusammen

Heute kein Verkauf, CHF 0.–

Drei Kunden mit konkreten Wünschen, alles nicht an Lager: Vel schwarz 4, Tricot Cardigan navy M, Urban Backpack Rucksack schwarz.

Gruess
Sabrina
"""),

dict(id="0903", d="2026-09-03 18:55", w="gc", subj="STM01 Tagesabschluss 3.9.", body="""
Allegra

CHF 4'020.– (Budget 6'330.–). Ein Paar aus Riad und ein Amerikaner, Iridia offwhite, Cosimo schwarz, Rollkragen und ein Shirt.
Cosimo schwarz 5 ist jetzt auf null.

Cordials salüds
Gian-Andrea
"""),

dict(id="0904", d="2026-09-04 18:49", w="sg", subj="St. Moritz – Abschluss 4.9.", body="""
Hoi zusammen

CHF 3'750.– (Budget 7'680.–), 6 Bons, nur Kleinteile.
Lieferung pünktlich, 51 Teile, alles verräumt.
Vtrack Gtx 39 gefragt.

Gruess
Sabrina
"""),

dict(id="0906", d="2026-09-06 18:58", w="nt", subj="Abschluss Sa + So", body="""
Ciao a tutti

Wochenende zusammen:

Samstag CHF 14'290.– (budget 11'020) bene!! Eine arabische Familie, wohnen in Champfèr, 2x Piero und 2x Cortina, plus Caps und Shirts.
Nicht da: Aurea navy 4, Tricot Cardigan schwarz L
Retour Cosimo 5, Kunde hat sich umentscheidet.

Sonntag CHF 3'430.– (budget 7'310). Ruhig. Iridia rosa verkauft an eine Dame aus Zürich, Alpina, Rucksack, Cap.

Cortina M und Cap weiss sind jetzt fertig.

Saluti
Nicola

Von meinem iPhone gesendet
"""),

dict(id="0907", d="2026-09-07 18:44", w="gc", subj="STM01 Tagesabschluss 7.9.", body="""
Allegra

CHF 5'420.– (Budget 5'010.–), knapp über Budget mit 3 Bons. Nova schwarz, Monteluce grau, Tricot, Vel.
Wieder Aurea offwhite 00 gefragt, die haben wir schon im August nicht gehabt.

Cordials salüds
Gian-Andrea
"""),

dict(id="0908", d="2026-09-08 18:50", w="gc", subj="STM01 Tagesabschluss 8.9.", body="""
Allegra

CHF 3'880.–. Zwei Vtrack Gtx, ein Tricot und eine Aria rosa an eine chinesische Kundin.

Cordials salüds
Gian-Andrea
"""),

dict(id="0909", d="2026-09-09 18:46", w="sg", subj="St. Moritz – Abschluss 9.9.", body="""
Hoi zusammen

CHF 1'320.– netto. Eigentlich 6 Teile verkauft, aber eine Nova Gr. 5 kam zurück (Qualität, Daunen treten an der Naht aus), das drückt den Tag.
Vtrack Gtx 41 und 43 jetzt auf null.

Gruess
Sabrina
"""),

dict(id="0910", d="2026-09-10 18:53", w="gc", subj="STM01 Tagesabschluss 10.9.", body="""
Allegra

CHF 5'700.– (Budget 5'890.–). Piero, Vel, Camilla und eine Iridia schwarz.
Camilla schwarz und Piero 3 sind ausverkauft.

Cordials salüds
Gian-Andrea
"""),

dict(id="0911", d="2026-09-11 18:58", w="sg", subj="St. Moritz – Abschluss 11.9.", body="""
Hoi zusammen

Super Freitag für uns: CHF 12'590.–, Budget 6'520.–.
2x Piero an zwei Herren, die schon für den Winter einkaufen, dazu Handschuhe, Hoodie, Crewneck, Cosimo.
Lieferung pünktlich (30 Teile).
Vtrack Gtx 43 gefragt, haben wir immer noch nicht.

Gruess
Sabrina
"""),

dict(id="0912", d="2026-09-12 18:39", w="nt", subj="Abschluss Samstag", body="""
Ciao

CHF 9'820.– heute, budget 9'050, va bene.
Crewneck schwarz 2x, Piero, Beanie, Schal, Cap.
Gefragt aber nicht da: Amalia braun 3, Jersey Polo navy M, Alpina offwhite 35.

Piero 5 auch fertig jetzt.

Nicola

Von meinem iPhone gesendet
"""),

dict(id="0913", d="2026-09-13 18:33", w="nt", subj="So 13.9.", body="""
Ciao,
oggi quasi niente... CHF 169.– netto. 2 Caps verkauft, ein Beanie zurück (Farbe).
Fiammetta schwarz 3 gefragt.
Nicola

Von meinem iPhone gesendet
"""),

dict(id="0914", d="2026-09-14 18:48", w="gc", subj="STM01 Tagesabschluss 14.9.", body="""
Allegra

CHF 2'530.–, Nova schwarz und Vel schwarz. Sehr ruhig.

Cordials salüds
Gian-Andrea
"""),

dict(id="0916", d="2026-09-16 18:51", w="sg", subj="St. Moritz – Abschluss 16.9.", body="""
Hoi zusammen

Gestern ist der Abschluss bei mir untergegangen, sorry: 15.9. CHF 1'895.–, Crewneck schwarz L gefragt.

Heute CHF 4'120.– (Budget 4'750.–). Hoodie schwarz 2x, Rollkragen, Cable Knit, Nova schwarz.
Gefragt: Cosimo schwarz 6, Crewneck schwarz S.
Vel schwarz 3 jetzt auf null.

Gruess
Sabrina
"""),

dict(id="0917", d="2026-09-17 18:42", w="gc", subj="STM01 Tagesabschluss 17.9.", body="""
Allegra

CHF 390.– (ein Paar Handschuhe). 20 Leute im Laden.
Eine Kundin hat nach der Amalia in braun gefragt, Gr. 0. Die zweite Anfrage nach dem Braun in einer Woche.

Cordials salüds
Gian-Andrea
"""),

dict(id="0918", d="2026-09-18 18:57", w="sg", subj="St. Moritz – Abschluss 18.9.", body="""
Hoi zusammen

CHF 5'960.– (Budget 6'000.–). Schals schwarz 2x, Alpina 2x, Cortina, Crewneck, Tricot.
Lieferung pünktlich (38 Teile).

Gruess
Sabrina
"""),

dict(id="0920", d="2026-09-20 18:44", w="nt", subj="Abschluss weekend 19-20.9.", body="""
Ciao a tutti

Sa: CHF 6'850.– (budget 8'850). Piero, Cortina, Liviana offwhite, Iridia schwarz. Hoodie schwarz L gefragt, nicht da.
So: CHF 1'930.– (budget 5'820). Rucksack, Shirt, Alpina. Ein Kunde wollte Iridia offwhite 3.

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

CHF 3'910.– (Budget 4'850.–). Eine russische Familie, Cortina und Monteluce schwarz, dazu Beanie und Alpina.
Monteluce schwarz 5 und Cortina M auf null.

Cordials salüds
Gian-Andrea
"""),

dict(id="0923", d="2026-09-23 18:52", w="sg", subj="St. Moritz – Abschluss 23.9.", body="""
Hoi zusammen

CHF 6'650.–, Budget 5'000.–. Aurea navy, Nova schwarz, Mistral, Monteluce schwarz, Beanie weiss.
Aurea navy 1 jetzt aus.

Gruess
Sabrina
"""),

dict(id="0924", d="2026-09-24 18:55", w="gc", subj="STM01 Tagesabschluss 24.9.", body="""
Allegra

Leider negativ: CHF -2'540.– netto.
Zwei Alpina (38 und 40) kamen zurück, waren Geschenke, dazu ein Monteluce Gr. 5 (zu gross). Verkauft nur Beanie und Vtrack.
Und wieder Aurea offwhite 00 gefragt, das ist jetzt die dritte Anfrage seit Ende August.

Cordials salüds
Gian-Andrea
"""),

dict(id="0925", d="2026-09-25 18:48", w="sg", subj="St. Moritz – Abschluss 25.9.", body="""
Hoi zusammen

CHF 4'110.–. Crewneck, Alpina, Monteluce navy, Vel.
Lieferung pünktlich (33 Teile).

Gruess
Sabrina
"""),

dict(id="0926", d="2026-09-26 18:37", w="nt", subj="Abschluss Sa 26.9.", body="""
Ciao

CHF 4'700.–, budget 10'330, niente da fare. Halbe Kunden aus Dubai, aber haben fast nur geschaut. 2 Beanie weiss, Piero, Fiammetta navy.
Shirt weiss XXL gefragt.

Nicola

Von meinem iPhone gesendet
"""),

dict(id="0927", d="2026-09-27 18:31", w="nt", subj="So", body="""
CHF 1'830.– Beanie + Nova schwarz. Basta.
Nicola

Von meinem iPhone gesendet
"""),

dict(id="0928", d="2026-09-28 18:56", w="gc", subj="STM01 Tagesabschluss 28.9. – 2x Vel defekt", body="""
Allegra

CHF 2'960.– (Budget 4'860.–), aber es sind zwei Reklamationen dabei, die ich melden möchte:

Zwei Stammkunden haben ihre Vel schwarz zurückgebracht (Gr. 4 und Gr. 6, beide Ende August gekauft). Bei beiden schliesst der Reissverschluss nicht mehr richtig, der Schieber rutscht über die Zähne. Wir haben beide zurückerstattet, die Gilets liegen im Lager.
Ist das bekannt? Bei zwei Fällen am gleichen Tag glaube ich nicht an Zufall.

Sonst: Rucksack 2x, Cortina, Cap, Tricot, Mistral. Crewneck S zurück (Grösse).
Gefragt: Mistral schwarz 1, Monteluce grau 2, Crewneck schwarz S.

Cordials salüds
Gian-Andrea
""", att=[dict(name="Tib_Reissverschluss_1.jpg", kind="jpg")]),

dict(id="0929", d="2026-09-29 18:43", w="gc", subj="STM01 Tagesabschluss 29.9.", body="""
Allegra

CHF 4'350.–. Fiammetta, Camilla, Iridia offwhite.
Gefragt: Aurea navy 1 und die Iridia rosa in Gr. 1, beides nicht da.

Cordials salüds
Gian-Andrea
"""),

dict(id="1001", d="2026-10-01 18:49", w="gc", subj="STM01 Tagesabschluss 1.10.", body="""
Allegra

Nachtrag 30.9. (ist gestern nicht rausgegangen): CHF 5'910.–, Budget 5'650.–. Gefragt: Astra Cape weiss XL, Tricot schwarz L, Vtrack Gtx 44 und grau 40.

Heute CHF 2'520.–. Schal, Beanie, Alpina, Camilla.
Camilla schwarz 1 jetzt aus.

Cordials salüds
Gian-Andrea
"""),

dict(id="1002", d="2026-10-02 18:51", w="sg", subj="St. Moritz – Abschluss 2.10.", body="""
Hoi zusammen

CHF 6'050.– (Budget 7'590.–). Vtrack, Alpina, Vel, Aurea navy, Liviana offwhite.
Lieferung pünktlich (22 Teile).

Gefragt und nicht da: Aurea beige 3, Iridia schwarz 4, Amalia braun 0 (die dritte Anfrage nach der braunen Amalia!).

Gruess
Sabrina
"""),

dict(id="1004", d="2026-10-04 18:47", w="nt", subj="Abschluss Sa+So 3-4.10.", body="""
Ciao a tutti

Sabato CHF 7'110.– (budget 10'450). 2x Piero, 2x Shirt weiss, Crewneck, Aurea offwhite. Gefragt Shirt weiss XS und Alpina offwhite 37.
Domenica CHF 7'370.– (budget 7'110) 👍 nochmal 2x Piero, 2x Beanie schwarz, Cap, Tricot, Alpina.

Die Piero geht gut, ma Gr. 3 ist jetzt fertig. Viele Leute aus Mailand am Wochenende, Ferienwohnungen aufmachen für den Winter.

Saluti
Nicola

Von meinem iPhone gesendet
"""),

dict(id="1005", d="2026-10-05 18:39", w="gc", subj="STM01 Tagesabschluss 5.10.", body="""
Allegra

CHF 1'830.–. Piero, Handschuhe und eine Aurea beige verkauft, aber eine Piero Gr. 4 vom Wochenende kam zurück (Kunde hat es sich anders überlegt).
Piero 3 erneut gefragt.

Cordials salüds
Gian-Andrea
"""),

dict(id="1006", d="2026-10-06 18:44", w="gc", subj="STM01 Tagesabschluss 6.10.", body="""
Allegra

CHF 2'920.–. Crewneck grau, Nova schwarz, Camilla. Ruhig.

Cordials salüds
Gian-Andrea
"""),

dict(id="1007", d="2026-10-07 18:50", w="sg", subj="St. Moritz – Abschluss 7.10.", body="""
Hoi zusammen

CHF 7'190.–, Budget 6'190.–. Piero 2x, Schal beige, Beanies, Rucksack.
Monteluce grau 5 gefragt. Piero 4 jetzt auch auf null.

Gruess
Sabrina
"""),

dict(id="1008", d="2026-10-08 18:45", w="gc", subj="STM01 Tagesabschluss 8.10.", body="""
Allegra

CHF 3'570.– (Budget 6'860.–). Handschuhe, Monteluce grau, Aurea navy.

Die Piero fehlt uns jetzt richtig: heute zwei Herren mit Wunsch Gr. 2 und Gr. 4, beide ohne Kauf weg. Dazu Astra Cape schwarz L gefragt.
Bitte prüfen, ob für die letzte Lieferung vor der Zwischensaison noch Piero 2/3/4 möglich sind.

Cordials salüds
Gian-Andrea
"""),

dict(id="1009", d="2026-10-09 18:52", w="sg", subj="St. Moritz – Abschluss 9.10.", body="""
Hoi zusammen

CHF 7'260.– (Budget 7'980.–). Piero, Cortina, Handschuhe, Tricot navy, Cable Knit.
Lieferung pünktlich, 17 Teile, immerhin 3 Piero (Gr. 2 und 3), aber keine 4.

Gruess
Sabrina
"""),

dict(id="1010", d="2026-10-10 18:41", w="nt", subj="Abschluss Sabato 10.10.", body="""
Ciao

CHF 9'930.– (budget 11'430). Schal grau 2x, Cortina, Handschuhe, Jersey Polo, Crewneck.
Handschuhe sind jetzt fertig (letzte verkauft).

Am Montag soll Schnee kommen bis ins Dorf!

Nicola

Von meinem iPhone gesendet
"""),

dict(id="1011", d="2026-10-11 18:36", w="nt", subj="Abschluss So 11.10.", body="""
Ciao a tutti

CHF 9'330.–, budget 7'800, bene. Gäste aus Abu Dhabi und eine russische Familie. Mistral, Monteluce, Hoodie, Crewneck, Shirt.
Aria rosa 4 gefragt, haben wir nicht.

Mistral schwarz 3 und Vel schwarz 3 jetzt fertig.

Nicola

Von meinem iPhone gesendet
"""),

dict(id="1012", d="2026-10-12 18:48", w="gc", subj="STM01 Tagesabschluss 12.10.", body="""
Allegra

Es schneit seit Mittag. CHF 2'660.– (Budget 6'570.–), nur Einheimische unterwegs.

Gefragt und nicht vorhanden: Fiammetta navy 3, Mistral schwarz 3, Artem schwarz 3, Cap weiss.

Cordials salüds
Gian-Andrea
"""),

dict(id="1013", d="2026-10-13 18:51", w="gc", subj="STM01 Tagesabschluss 13.10.", body="""
Allegra

20 cm Neuschnee im Dorf, Julier nur mit Ketten. CHF 5'590.– (Budget 5'920.–).
Beanie weiss 2x, Cortina, Monteluce schwarz, Amalia schwarz.
Gefragt: Fiammetta schwarz 3, Cortina S, Alpina 35.

Cordials salüds
Gian-Andrea
"""),

dict(id="1014", d="2026-10-14 18:46", w="sg", subj="St. Moritz – Abschluss 14.10.", body="""
Hoi zusammen

CHF 2'530.–, Piero und Beanie. Strassen schlecht, kaum jemand unterwegs.
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
Nova schwarz 3x (eine kam am Nachmittag wieder zurück, Gr. 3, Kunde hat es sich anders überlegt), Tricot schwarz 2x, Alpina 2x.
Crewneck grau XL gefragt.

Cordials salüds
Gian-Andrea
"""),

dict(id="1016", d="2026-10-16 18:58", w="sg", subj="St. Moritz – Abschluss 16.10.", body="""
Hoi zusammen

CHF 9'950.– (Budget 9'250.–).
Letzte Lieferung vor der Pause angekommen, nur 12 Teile (2 Piero, Mistral, Cortina, Handschuhe usw.). Die eine Piero 4 war nach einer Stunde verkauft.

Nicht bedient:
- Piero 4 (2 Kunden)
- Iridia schwarz 0
- Tricot Cardigan schwarz L
- Rollkragen navy XL
- Alpina 39

Beanie weiss ist ausverkauft.

Gruess
Sabrina
"""),

dict(id="1017", d="2026-10-17 18:42", w="nt", subj="Abschluss Sa 17.10. 🎿", body="""
Ciao a tutti

Sabato pazzesco per noi: CHF 16'870.–, budget 12'800! 72 Leute im Laden, die Hälfte Wochenendgäste wegen Schnee.

Rollkragen schwarz 2x, Piero, Beanie, Vtrack, Rucksack...

Aber viele Sachen nicht da, peccato:
- Piero 4 (2x!!)
- Liviana offwhite 3
- Fiammetta 00
- Mistral 7
- Monteluce grau 3
- Astra Cape weiss XL
- Rollkragen XXL
- Beanie schwarz

Morgen letzter Tag, dann Ferien 🙌

Nicola

Von meinem iPhone gesendet
"""),

dict(id="1017d", d="2026-10-17 18:42", w="nt", sfx="_dup", subj="Abschluss Sa 17.10. 🎿", body="""
Ciao a tutti

Sabato pazzesco per noi: CHF 16'870.–, budget 12'800! 72 Leute im Laden, die Hälfte Wochenendgäste wegen Schnee.

Rollkragen schwarz 2x, Piero, Beanie, Vtrack, Rucksack...

Aber viele Sachen nicht da, peccato:
- Piero 4 (2x!!)
- Liviana offwhite 3
- Fiammetta 00
- Mistral 7
- Monteluce grau 3
- Astra Cape weiss XL
- Rollkragen XXL
- Beanie schwarz

Morgen letzter Tag, dann Ferien 🙌

Nicola

Von meinem iPhone gesendet
"""),

dict(id="1018", d="2026-10-18 19:24", w="gc", subj="STM01 letzter Tagesabschluss vor Zwischensaison – 18.10.", importance="high", body="""
Allegra zusammen

Letzter Verkaufstag der Sommer-/Herbstsaison: CHF 9'170.– (Budget 8'990.–), 13 Teile.
Cortina 2x, Schals schwarz 2x, Piero, Handschuhe, Vtrack grau.
Eine Piero 4 kam zurück (Kunde hat es sich anders überlegt), die geht jetzt mit ans DC.

Auch heute noch Anfragen, die wir nicht bedienen konnten:
Cortina L (2x), Nova schwarz 6, Rollkragen braun XL, Crewneck schwarz S und M, Beanie weiss, Urban Backpack Rucksack.

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
- 2 Vel schwarz mit defektem Reissverschluss (Retouren vom 28.9.) separat verpackt und markiert "Quality"
- Differenzen Inventur: 1x Beanie schwarz fehlt, 1x Cap weiss zu viel (wurde wohl falsch gescannt)
- Ausstellungsware (Puppen) bleibt im Laden

Gruess
Sabrina
""", att=[dict(name="STM01_Inventur_19102026.csv", kind="csv", enc="cp1252", text=(
    "Store;Datum;Kartons;Teile;Bemerkung\r\n"
    "STM01;19.10.2026;21;310;Rücksendung DC, Abholung 20.10. GEODIS\r\n"
    "STM01;19.10.2026;1;2;Vel schwarz DEFEKT (Quality)\r\n"))]),

dict(id="1020", d="2026-10-20 13:05", w="sg", subj="AW: STM01 – Inventur + Rücksendung DC", reply="1019", quote="1019", to=["ops"], cc=["sw", "merch"], body="""
Ware ist um 11:40 abgeholt worden, 21 Kartons + 1 Karton Quality. Lieferschein im Anhang (Foto).
Laden ist zu, Alarm aktiviert, Schlüssel hat Gian-Andrea.
Ich bin ab morgen in den Ferien bis 15.11.

Gruess
Sabrina
""", att=[dict(name="IMG_8812.jpg", kind="jpg")]),

dict(id="1021q", d="2026-10-21 09:15", w="sw", subj="Piero/Cortina von STM nach ZRH?", to=["sg", "store"], cc=["gc"], body="""
Hallo Sabrina,

Zürich fragt nach Piero und Cortina in L. Könnt ihr von eurem Restbestand noch etwas direkt nach Zürich schicken statt ins DC?

Danke
Stefan
"""),

dict(id="1021a", d="2026-10-21 09:15", w="sg", subj="Automatische Antwort: Piero/Cortina von STM nach ZRH?", reply="1021q", auto=True, to=["sw"], cc=[], body="""
Ich bin bis 15.11.2026 in den Ferien und habe keinen Zugriff auf meine E-Mails. Ihre Nachricht wird nicht weitergeleitet.
Für dringende Anliegen wenden Sie sich bitte an retail-ops-dach@valentino-retail.example.

Sabrina Gredig
"""),

dict(id="1021b", d="2026-10-21 09:15", w="store", subj="Automatische Antwort: Piero/Cortina von STM nach ZRH?", reply="1021q", auto=True, to=["sw"], cc=[], body="""
Allegra! Unsere Boutique in St. Moritz ist vom 19. Oktober bis 3. Dezember 2026 geschlossen. Ab dem 4. Dezember sind wir gerne wieder für Sie da.
Gentile cliente, la boutique è chiusa dal 19 ottobre al 3 dicembre 2026.
Dear client, our boutique is closed from 19 October to 3 December 2026.

Valentino St. Moritz
"""),
]
