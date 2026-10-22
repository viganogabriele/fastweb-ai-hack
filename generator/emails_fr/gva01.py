# -*- coding: utf-8 -*-
"""GVA01 - Genève Rue du Rhône (boutique, CHF, fermé le dimanche). Hand-authored closing emails, Swiss French.

Writers: Nathalie Favre (SM, polite Swiss French, "septante/nonante", CHF 24'620.-, sometimes HTML table from Outlook),
Bruno Monnier (ASM, older, telegraphic, iPhone), Elodie Rochat (SA, once).
Geneva: late opening Thursday (until 21:00), Saturday closes 18:00.
"""
STORE = "GVA01"
D = "moncler-retail.example"
TO = [f"retail-ops-france@{D}"]
CC = [f"isabelle.moreau@{D}"]
CC_MERCH = [f"isabelle.moreau@{D}", f"merch-planning@{D}"]

DISCLAIMER = """Moncler Suisse SA – Rue du Rhône, 1204 Genève
Ce message est confidentiel et destiné exclusivement à son destinataire. / This e-mail is confidential and intended solely for the addressee."""

PEOPLE = {
    "nathalie": dict(name="Nathalie Favre", email=f"nathalie.favre@{D}",
                     sig="Meilleures salutations,\nNathalie Favre\nStore Manager | Moncler Genève – Rue du Rhône\n\n" + DISCLAIMER,
                     mailer="Microsoft Outlook 16.0", outlook=True),
    "bruno": dict(name="Bruno Monnier", email=f"bruno.monnier@{D}", sig="Bruno M.\n\nEnvoyé de mon iPhone",
                  mailer="iPhone Mail (21H16)"),
    "elodie": dict(name="Elodie Rochat", email=f"elodie.rochat@{D}",
                   sig="Elodie Rochat\nSales Associate – Moncler Genève\n\n" + DISCLAIMER),
    "isabelle": dict(name="Isabelle Moreau", email=f"isabelle.moreau@{D}",
                     sig="Isabelle Moreau\nArea Manager France & Genève", outlook=True, mailer="Microsoft Outlook 16.0"),
}


def html_table(intro, rows, outro):
    trs = "\n".join(
        f'<tr><td style="border:1px solid #999;padding:2px 6px">{a}</td>'
        f'<td style="border:1px solid #999;padding:2px 6px;text-align:right">{b}</td></tr>' for a, b in rows)
    return f"""<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head>
<body style="font-family:Calibri,Arial,sans-serif;font-size:11pt">
<p>{intro}</p>
<table style="border-collapse:collapse">
{trs}
</table>
<p>{outro}</p>
<p>Meilleures salutations,<br>Nathalie Favre<br><span style="color:#777">Store Manager | Moncler Genève – Rue du Rhône</span></p>
</body></html>"""


EMAILS = [
dict(id="0831", d="2026-08-31", t="19:46", who="nathalie", subj="GVA01 – Clôture du 31.08.2026", cc=CC_MERCH, body="""
Bonsoir Isabelle, bonsoir à tous,

CA : CHF 5'300.– pour un budget de CHF 8'650.–
Fin des vacances, la Rue du Rhône est encore calme, clientèle très internationale.
Demande : Marin marine 3 (plus disponible, fin de saison).

En vue de la rentrée, notre stock femme est très cassé : Maire beige 1 et 2, Maire blanche 1 et 2, Maire noire 2, Bady noire 1 et 2. Serait-il possible d'avoir un réassort Maire/Bady avant fin septembre ?
"""),

dict(id="0901", d="2026-09-01", t="19:38", who="bruno", subj="Clôture GVA 01.09", body="""
CHF 7'810 / bud 7'840. Ok.
Septante-cinq pour cent de clientèle suisse.
Demandes : Bady noire 1, Montcla noir 1.
"""),

dict(id="0902", d="2026-09-02", t="19:51", who="nathalie", subj="GVA01 – Clôture du 02.09.2026", body="""
Bonsoir à tous,

Belle journée : CHF 11'691.– (budget CHF 8'410.–), 10 tickets.
Cardigan logo noir x3, casquettes.

Bonne soirée,
""", sig="Nathalie"),

dict(id="0903", d="2026-09-03", t="21:44", who="nathalie", subj="GVA01 – Clôture du 03.09.2026", body="""
Bonsoir,

Nocturne du jeudi assez décevante : CHF 5'320.– / budget CHF 12'600.–, 3 tickets, uniquement de la clientèle locale.
4 demandes : Ilvaro blanc 4, Montcla noir 1 (deuxième fois cette semaine), polo marine L, bonnet marine.
"""),

dict(id="0904", d="2026-09-04", t="19:42", who="bruno", subj="Clôture GVA 04.09", body="""
CHF 14'090 / 14'950
Livraison 71 pcs ok.
Montcla noir : plus de 4 ni de 5, 3 demandes cette semaine. Trailgrip femme blanc 40 demandé.
"""),

dict(id="0905", d="2026-09-05", t="18:39", who="bruno", subj="Clôture samedi GVA", body="""
CHF 10'116 / 20'760 (-51%)
Quelques Saoudiens encore là, mais ils regardent.
Casquettes noires x3.
"""),

dict(id="0907", d="2026-09-07", t="19:33", who="nathalie", subj="GVA01 – Clôture du 07.09.2026", body="""
Bonsoir à tous,

CA : CHF 5'204.– / budget CHF 11'280.–
Clientèle allemande et chinoise, peu de Suisses.
Demande : cardigan logo noir S.
Retours : Rosière 5 (taille), bonnet (taille).
"""),

dict(id="0908", d="2026-09-08", t="19:40", who="nathalie", subj="GVA01 – Clôture du 08.09.2026", body="""
Bonsoir,

CHF 5'910.– / CHF 10'760.–. Quelques clients des Emirats et d'Inde.
Demandes : Valbourg noir 4, cardigan logo marine S.

Bonne soirée,
""", sig="Nathalie"),

dict(id="0909", d="2026-09-09", t="19:37", who="bruno", subj="Clôture GVA 09.09", body="""
CHF 7'906 / 11'590
Montcla noir 5 : 2 demandes encore !!
Echange Arneb 3 contre un 2 : la parka taille grand, le client flottait dedans.
"""),

dict(id="0910", d="2026-09-10", t="19:55", who="nathalie", subj="GVA01 – Clôture du 10.09.2026 (Jeûne genevois)", body="""
Bonsoir à tous,

Jeûne genevois aujourd'hui : ville très calme, beaucoup de commerces fermés, nous étions ouverts avec une équipe réduite.
CA : CHF 8'390.– / budget CHF 13'600.–
Clientèle du Golfe et chinoise.

6 demandes non servies : Maire blanche 0, Flammette noire 1 et 2, Tib marine 3, cardigan logo marine S (encore), Trailgrip GTX 43.
"""),

dict(id="0911", d="2026-09-11", t="19:48", who="nathalie", subj="GVA01 – Clôture du 11.09.2026", body="""
Bonsoir,

CHF 11'470.– / CHF 16'560.–
Livraison de 79 pièces reçue ce matin, sans le cardigan marine S.
Demandes : Hermine marine 00, Chambre noir 2, cardi matelassé gris XXL.
Un quart de clientèle américaine.
"""),

dict(id="0912", d="2026-09-12", t="18:44", who="bruno", subj="Clôture samedi 12.09", body="""
CHF 19'471 / 22'520
Pas mal de demandes : Tib noir 2 (x2), Flammette noire 2, Flammette marine 0, Karakorum noir 3, tee blanc M.
"""),

dict(id="0914", d="2026-09-14", t="19:31", who="nathalie", subj="GVA01 – Clôture du 14.09.2026", body="""
Bonsoir à tous,

CHF 6'460.– / CHF 11'790.–. Beaucoup de clients allemands, petites ventes (ceintures, cardigans).
Rien de particulier.
""", sig="Nathalie"),

dict(id="0915", d="2026-09-15", t="19:44", who="bruno", subj="Clôture GVA 15.09", body="""
CHF 8'300 / 11'900
Clients russes et indiens. 1 Peyre vendue.
5 demandes : Maire beige 4, Maire blanche 1, Montgenevre noir 7, Peyre 3, tee blanc S.
"""),

dict(id="0916", d="2026-09-16", t="19:39", who="nathalie", subj="GVA01 – Clôture du 16.09.2026", body="""
Bonsoir,

CA : CHF 11'600.– / CHF 13'190.–, clientèle presque exclusivement suisse (septante-neuf pour cent).
Demandes : Bady noire 0, Montgenèvre noir 7 (deuxième demande), Rosière noir 1.
"""),

# 17.09 pas de mail

dict(id="0918", d="2026-09-18", t="19:52", who="nathalie", subj="GVA01 – Clôture du 18.09.2026", body="""
Bonsoir à tous,

Toutes mes excuses pour l'absence de clôture hier, nocturne chargée et j'ai oublié.

Aujourd'hui : CHF 19'683.– / CHF 17'850.– (+10%)
Un groupe de clients chinois en fin d'après-midi. Torsades noires x3, Maire beige x2.
Livraison 85 pièces.
Demandes : Tib blanc 1, Peyre 1, torsade noire M.
"""),

dict(id="0919", d="2026-09-19", t="18:36", who="bruno", subj="Clôture samedi 19.09", body="""
CHF 11'540 / 24'640 (-53%)
Grand beau, tout le monde au bord du lac.
1 Maire noire 0 demandée.
"""),

dict(id="0921", d="2026-09-21", t="19:35", who="nathalie", subj="GVA01 – Clôture du 21.09.2026", cc=CC_MERCH, body="""
Bonsoir,

CHF 6'890.– / CHF 13'830.–
Cardigan logo marine S : troisième demande en dix jours, toujours pas reçu. Pouvez-vous vérifier s'il y en a au dépôt ?
Torsade noire XXL demandée aussi.
"""),

dict(id="0922", d="2026-09-22", t="19:41", who="bruno", subj="Clôture GVA 22.09", body="""
CHF 7'330 / 13'140
Chambre blanc 4, dolcevita marine XXL demandés.
"""),

dict(id="0923", d="2026-09-23", t="19:47", who="nathalie", subj="GVA01 – Clôture du 23.09.2026", body="""
Bonsoir à tous,

CHF 9'690.– / CHF 14'890.–
Des clients émiratis, 2 Karakorum noirs.
Ilvaro blanc 4 demandé (deuxième fois ce mois).
""", sig="Nathalie"),

dict(id="0924", d="2026-09-24", t="21:38", who="nathalie", subj="GVA01 – Clôture du 24.09.2026", body="""
Bonsoir,

CA : CHF 6'800.– / budget CHF 16'480.–
Lancement Genius Polaris : une cagoule noire vendue. La cape et l'oversize suscitent de la curiosité, peu d'essayages.
Ilvaro noir 0 demandé deux fois (même taille, deux clientes différentes).
"""),

dict(id="0925", d="2026-09-25", t="19:43", who="bruno", subj="Clôture GVA 25.09", body="""
CHF 32'790 / 19'480
Livraison 93 pcs.
Rosiere noir x3 (1 demande en 2 en plus), Tib blanc x2, Insolux blanc x2.
"""),

dict(id="0926c", d="2026-09-26", t="08:57", who="bruno", reply_to="0925", suffix="_corr", subj="Re: Clôture GVA 25.09 - correction", quote=False, body="""
Correction, hier c'etait CHF 23'790 et pas 32'790. Faute de frappe sur le natel. Desole.
"""),

dict(id="0926", d="2026-09-26", t="18:48", who="nathalie", subj="GVA01 – Clôture du samedi 26.09.2026", body="""
Bonsoir à tous,

Très belle surprise : CHF 39'280.– pour un budget de CHF 28'250.–, 21 tickets.
Une cliente saoudienne et sa fille ont pris deux capes Polaris blanches, plus une cagoule. Bady noires x3.
Demandes : Hermine blanche 00, Ambrine noire 1.
"""),

dict(id="0928", d="2026-09-28", t="19:36", who="bruno", subj="Clôture GVA 28.09", body="""
CHF 13'975 / 15'000
Ilvaro noir x2, Maya noir x2.
Trailgrip GTX 41 demandé.
Encore un echange Arneb 3 (trop grand).
"""),

dict(id="0929", d="2026-09-29", t="19:42", who="nathalie", subj="GVA01 – Clôture du 29.09.2026", body="""
Bonsoir,

CHF 6'410.– / CHF 14'410.–
Une Maire noire 3 demandée. 1 cagoule Polaris noire vendue.
""", sig="Nathalie"),

dict(id="0930", d="2026-09-30", t="19:49", who="nathalie", subj="GVA01 – Clôture du 30.09.2026", body="""
Bonsoir à tous,

CHF 7'740.– / CHF 15'920.–
Clientèle du Moyen-Orient (Saoudiens, Emiratis) et américaine, aucun Suisse aujourd'hui ou presque.
Demandes : Hermine blanche 4, Flammette marine 2, Karakorum gris 6, Rosière noir 3.
Retour d'une écharpe (taille ?!).
"""),

dict(id="1001", d="2026-10-01", t="21:29", who="bruno", subj="Clôture GVA 01.10", body="""
CHF 9'200 / 18'770 (-51%)
2 cagoules Polaris blanches.
5 demandes : Bady noire 1, Chambre blanc 4, Montcla marine 1, Rosiere noir 3 (encore), cardi matelasse gris S.
"""),

dict(id="1002", d="2026-10-02", t="19:54", who="nathalie", subj="GVA01 – Clôture du 02.10.2026", body="""
Bonsoir à tous,

CA : CHF 25'661.– / budget CHF 22'930.–
Livraison de 112 pièces, dont les capes Polaris blanches (M et XL) et des Ilvaro noirs.
Valbourg noir x2, bonnets blancs, écharpes beige.
Un retour de Tib T5 : la tirette de la fermeture éclair s'est cassée. Échangé.
Demandes : Maya olive 4, hoodie marine XL, sweat gris XL.
"""),

dict(id="1003", d="2026-10-03", t="18:41", who="bruno", subj="Clôture samedi 03.10", body="""
CHF 23'275 / 30'190
Bonnets noirs x5, il commence a faire frais le matin.
6 demandes : Maire noire 2, Chambre noir 4, Karakorum gris 1, Valbourg noir 2, cape Polaris blanche XXL, dolcevita marine L.
Encore un Tib retourne, fermeture.
"""),

dict(id="1005", d="2026-10-05", t="19:32", who="nathalie", subj="GVA01 – Clôture du 05.10.2026", body="""
Bonsoir,

CHF 10'870.– / CHF 16'040.–
Une cliente chinoise voulait la Bady rose poudré en 2 : nous ne l'avons pas en assortiment. Trailgrip femme blanc 41 demandé aussi.
Retour Flammette 2 (taille).
"""),

dict(id="1006", d="2026-10-06", t="19:45", who="nathalie", subj="GVA01 – Clôture du 06.10.2026 – Tib", body="""
Bonsoir à tous,

CHF 15'850.– / CHF 15'880.–, au budget.
Une Peyre rouge vendue, bonnets noirs.
Demandes : Montcla marine 4, torsade blanche XS, torsade noire XS.

Troisième Tib retourné pour la même raison en une semaine (fermeture éclair, le curseur casse). Est-ce un problème connu ? Faut-il retirer les pièces de la vente ?
"""),

dict(id="1007i", d="2026-10-07", t="08:31", who="isabelle", reply_to="1006", suffix="_re1", to=[f"nathalie.favre@{D}"],
     cc=[f"bruno.monnier@{D}"], body="""
Bonjour Nathalie,

Oui, problème connu sur le lot livré à partir de mi-août (curseur de la fermeture). Paris a le même souci. Pas de retrait de la vente pour l'instant mais contrôlez la tirette avant de vendre. Échange ou remboursement, pièces renvoyées au SAV avec le motif DEF.
Une note qualité suit.

Bonne journée
"""),

dict(id="1007", d="2026-10-07", t="19:39", who="bruno", subj="Clôture GVA 07.10", body="""
CHF 7'410 / 18'590 (-60%)
Mercredi tres calme.
Maire noire : 2 en 1, 1 en 2. Montgenevre gris 5, Rosiere olive 3, polo marine M.
"""),

dict(id="1008", d="2026-10-08", t="21:41", who="nathalie", subj="GVA01 – Clôture du 08.10.2026",
     html=html_table("Bonsoir à tous,<br>voici la clôture de la nocturne :", [
         ("CA (CHF)", "28'775.–"), ("Budget (CHF)", "19'870.–"), ("Ecart", "+45%"), ("Tickets", "18"), ("Entrées", "145"),
         ("Top", "Cardigan logo noir x5, Montcla noir x2, Ambrine noire x2"),
     ], "Clientèle saoudienne et suisse. 6 demandes : Maire noire 1, Montcla noir 1, Tib marine 7, Tib blanc 7, sweat gris L, Trailgrip femme noir 36.<br>Retour dolcevita S (taille)."),
     body="""
Bonsoir à tous,
voici la clôture de la nocturne :

CA (CHF)        28'775.–
Budget (CHF)    19'870.–
Ecart           +45%
Tickets         18
Entrées         145
Top             Cardigan logo noir x5, Montcla noir x2, Ambrine noire x2

Clientèle saoudienne et suisse. 6 demandes : Maire noire 1, Montcla noir 1, Tib marine 7, Tib blanc 7, sweat gris L, Trailgrip femme noir 36.
Retour dolcevita S (taille).
"""),

dict(id="1009", d="2026-10-09", t="19:37", who="bruno", subj="Clôture GVA 09.10", body="""
CHF 27'750 / 22'760
Livraison 107 pcs.
Ecrins noir x3, Chamonix x2 (les skieurs se preparent).
"""),

dict(id="1010", d="2026-10-10", t="18:46", who="nathalie", subj="GVA01 – Clôture du samedi 10.10.2026", body="""
Bonsoir à tous,

CHF 26'470.– / CHF 28'760.–
Maya noir x4, Trailgrip femme noir x3.
6 demandes : Maire noire 1, Karakorum gris 5, Ecrins noir 5, Peyre 1, cardigan noir XXL, hoodie marine M.
On annonce un coup de froid dès lundi, j'espère qu'on aura le stock.
"""),

dict(id="1012", d="2026-10-12", t="19:44", who="bruno", subj="Clôture GVA 12.10", body="""
CHF 15'225 / 17'200
La bise s'est levee, 6 degres ce matin, les gens ressortent les doudounes.
Maire noire 0, 1 et 2 demandees (on n'a plus rien en noir), Maire marine 4, Ecrins 1.
Retour Arneb 5 en taille.
"""),

dict(id="1013", d="2026-10-13", t="19:58", who="nathalie", subj="GVA01 – Clôture du 13.10.2026",
     html=html_table("Bonsoir à tous,", [
         ("CA (CHF)", "24'620.–"), ("Budget (CHF)", "17'370.–"), ("Ecart", "+42%"), ("Tickets", "15"),
         ("Top", "Bonnets noirs x3, Legere x3, Rosière x2"),
     ], "Le froid est là : neige annoncée jusqu'à 1000 m, le Salève est blanc ce matin. Les clients achètent bonnets, gants et doudounes.<br>"
        "8 demandes non servies : Maire noire 0, Hermine blanche 4, Ambrine noire 3, Montgenèvre noir 5, Montgenèvre marine 6, Peyre 1, Valbourg blanc 0, dolcevita marine XXL.<br>"
        "Nous manquons de doudounes noires dans les tailles courantes, merci de prioriser Genève sur les prochains envois."),
     cc=CC_MERCH, body="""
Bonsoir à tous,

CA (CHF)       24'620.–
Budget (CHF)   17'370.–
Ecart          +42%
Tickets        15
Top            Bonnets noirs x3, Legere x3, Rosière x2

Le froid est là : neige annoncée jusqu'à 1000 m, le Salève est blanc ce matin. Les clients achètent bonnets, gants et doudounes.
8 demandes non servies : Maire noire 0, Hermine blanche 4, Ambrine noire 3, Montgenèvre noir 5, Montgenèvre marine 6, Peyre 1, Valbourg blanc 0, dolcevita marine XXL.
Nous manquons de doudounes noires dans les tailles courantes, merci de prioriser Genève sur les prochains envois.
"""),

dict(id="1014", d="2026-10-14", t="19:47", who="bruno", subj="Clôture GVA 14.10", body="""
CHF 18'700 / 18'830
Il caille. Bonnets noirs x3, bonnets rose x2.
7 demandes : Maya noir 6, Montcla marine 5, Karakorum gris 2, Montgenevre noir 5 + gris 6, torsade blanche XXL, hoodie marine M.
"""),

dict(id="1015", d="2026-10-15", t="21:46", who="nathalie", subj="GVA01 – Clôture du 15.10.2026", body="""
Bonsoir à tous,

Excellente nocturne : CHF 38'080.– pour un budget de CHF 21'230.– (+79%).
Les clients sortent du bureau et achètent pour le froid : Tib noir x4, Rosière x3, Valbourg x2, Ecrins x2.
7 demandes : Maire blanche 2, Maya noir 2, Arneb noir 1, Valbourg noir 00 et 2, Valbourg blanc 4, dolcevita marine XXL (troisième fois).
Montgenèvre noir 3 et 5 à zéro.
"""),

dict(id="1016", d="2026-10-16", t="19:58", who="bruno", subj="Clôture GVA 16.10", to=[f"retail-ops-dach@{D}"], cc=[f"stefan.wagner@{D}"], body="""
CHF 49'840 / 25'610 → record de l'annee je crois
Echarpes cachemire noires x3, Montcla noir x3, dolcevita noir x2, bonnets...
Livraison 129 pcs.
Montcla noir 6 demande. Ilvaro noir 0 et 1 a zero, Ambrine noire 2 aussi.
"""),

dict(id="1017f", d="2026-10-17", t="08:22", who="bruno", reply_to="1016", suffix="_fwd", subj="TR: Clôture GVA 16.10",
     to=[f"retail-ops-france@{D}"], cc=[f"isabelle.moreau@{D}"], body="""
Bonjour, envoye a la mauvaise liste hier soir (DACH), voici la cloture de vendredi.
"""),

dict(id="1017", d="2026-10-17", t="18:52", who="nathalie", subj="GVA01 – Clôture du samedi 17.10.2026", cc=CC_MERCH, body="""
Bonsoir à tous,

CHF 22'700.– / CHF 34'360.– (-34%)
Froid mais grand soleil, beaucoup de monde en ville. Nous aurions pu faire bien plus : le stock de doudounes noires est cassé partout (Maire noire 0-1-2, Maya noir 4, Ilvaro noir 0-1, Ambrine noire 2, Hermine noire 1, Rosière 5).
4 demandes : Maire noire 1, Hermine blanche 2, Arneb marine 4, cape Polaris blanche M.
Retour Ambrine 0 (taille).

Merci de regarder en urgence un réassort doudounes pour la semaine prochaine.
"""),

dict(id="1019", d="2026-10-19", t="19:39", who="bruno", subj="Clôture GVA 19.10", body="""
CHF 21'476 / 18'150
Dernier jour de froid d'apres MeteoSuisse.
Maire blanche x3, echarpes noires x3.
Maire noire 0 x3 + 1, dolcevita marine L.
Retours : Tib (fermeture), Arneb 6 (taille), Karakorum, Trailgrip.
"""),

dict(id="1020", d="2026-10-20", t="19:34", who="nathalie", subj="GVA01 – Clôture du 20.10.2026", body="""
Bonsoir à tous,

CHF 9'840.– / CHF 17'720.–
Redoux, 14 degrés et la bise est tombée. Retour au calme.
Demandes : Rosière olive 3, Peyre 1, cardi matelassé marine L, sweat gris L.
""", sig="Nathalie"),

dict(id="1021", d="2026-10-21", t="19:41", who="elodie", subj="Clôture Genève 21.10", body="""
Bonsoir,

Nathalie est en réunion à Zurich aujourd'hui, je fais la clôture.
CA : CHF 4'980.– pour CHF 19'950.– de budget, 5 tickets. Journée très calme, nonante entrées le matin mais peu d'achats.
Demandes : Maire noire 1, Ilvaro noir 1, Montcla marine 7, polo noir M.

Bonne soirée,
"""),
]
