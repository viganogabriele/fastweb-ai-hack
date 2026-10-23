# -*- coding: utf-8 -*-
"""CAN01 - Cannes La Croisette (boutique, arrière-saison, fermé le dimanche). Hand-authored closing emails.

Writers: Laetitia Rossi (SM, longer, southern, a bit lyrical/venting about the off-season and the budget),
Julien Pastor (ASM, telegraphic, "RAS", Android phone). Laetitia on leave Oct 5-10 (and Oct 12-13).
"""
STORE = "CAN01"
D = "valentino-retail.example"
TO = [f"retail-ops-france@{D}"]
CC = [f"isabelle.moreau@{D}"]
CC_MERCH = [f"isabelle.moreau@{D}", f"merch-planning@{D}"]

PEOPLE = {
    "laetitia": dict(name="Laetitia Rossi", email=f"laetitia.rossi@{D}",
                     sig="Laetitia\n\n--\nLaetitia Rossi\nResponsable Boutique Valentino Cannes\n58 bd de la Croisette, 06400 Cannes",
                     mailer="Microsoft Outlook 16.0", outlook=True),
    "julien": dict(name="Julien Pastor", email=f"julien.pastor@{D}", sig="Julien\nEnvoyé depuis mon Galaxy",
                   mailer="Samsung Email"),
    "isabelle": dict(name="Isabelle Moreau", email=f"isabelle.moreau@{D}", sig="Isabelle", outlook=True,
                     mailer="iPhone Mail (21H16)"),
}

EMAILS = [
dict(id="0831", d="2026-08-31", t="19:52", who="julien", subj="Cloture 31/08", body="""
CA 6,7k / bud 6,0k. 7 tickets.
Aurea noire T4 demandée, Adela noir 1 (plus en stock, fin SS), jersey polo marine M.
RAS
"""),

dict(id="0901", d="2026-09-01", t="19:47", who="julien", subj="Cloture 01/09", body="""
4,5k / 5,3k. Calme.
Surtout des locaux + 1 couple coréen.
Retour Fiammetta T3 qualité (bouton pression arraché).
Cardi matelassé marine M demandé.
"""),

dict(id="0902", d="2026-09-02", t="20:18", who="laetitia", subj="Clôture boutique Cannes - 02/09", cc=CC_MERCH, body="""
Bonsoir à tous,

Journée très calme sur la Croisette : 2,9k pour 6,4k de budget, 3 tickets. La rentrée scolaire se sent, les résidents secondaires sont repartis et il fait encore 28°, personne ne pense aux doudounes.

3 demandes non servies : Nova olive 3, torsade blanche XS, Alpina 40.
Surtout, le stock est très cassé avant l'automne : Aria noir 0, Fiammetta noir 1, Cosimo noir 4, Montgenèvre noir 4, Vtrack homme 41, Vtrack femme 39, Aurea noire et marine en 1... Est-ce qu'on peut prévoir un réassort avant les vacances de la Toussaint ? Notre clientèle locale revient début octobre.

Bonne soirée,
"""),

dict(id="0903", d="2026-09-03", t="19:31", who="laetitia", subj="Clôture Cannes 03/09", body="""
Bonsoir,

2 tickets aujourd'hui, 1,6k. Je n'ai pas grand-chose à ajouter.
Un Vel blanc en 1 demandé.

Bonne soirée,
"""),

dict(id="0904", d="2026-09-04", t="19:58", who="laetitia", subj="Clôture Cannes 04/09", body="""
Bonsoir à tous,

6,0k / 10,2k.
Le jersey polo noir n'existe plus en S et en L : 3 clients aujourd'hui (L x2, XS). C'est bête, avec la chaleur c'est ce qui se vend. Aussi cardigan logo marine M et dolcevita noir M.
Quelques Coréens de passage.

Laetitia
""", sig=None),

dict(id="0905", d="2026-09-05", t="19:44", who="laetitia", subj="Clôture Cannes samedi 05/09", body="""
Bonsoir,

8,5k / 14,8k.
La livraison attendue jeudi est arrivée ce matin seulement (2 jours de retard, 50 pièces). Pas de jersey polo dedans.
Quelques Anglais. Vtrack femme noir x2.

Bon dimanche,
"""),

dict(id="0907", d="2026-09-07", t="19:36", who="julien", subj="Cloture 07/09", body="""
3,3k / 8,1k
Vtrack Gtx noir 46 demandé.
Retour jersey polo XL couleur.
"""),

dict(id="0908", d="2026-09-08", t="19:50", who="julien", subj="Cloture 08/09", body="""
7,7k / 7,9k
Festival de la Plaisance au Vieux-Port depuis aujourd'hui, un peu de passage étranger (chinois, allemands, émiratis).
Jersey Polo noir L demandé encore.
"""),

dict(id="0909", d="2026-09-09", t="20:06", who="laetitia", subj="Clôture Cannes 09/09", body="""
Bonsoir à tous,

5,9k / 8,6k.
Le festival du yachting attire beaucoup de monde côté port mais personne ne remonte jusqu'à la Croisette, ou alors pour regarder.
2 sacs Urban Backpack noirs vendus. 1 Aurea noire en 0 demandée.

Laetitia
""", sig=None),

dict(id="0910", d="2026-09-10", t="20:11", who="laetitia", subj="Clôture Cannes 10/09", body="""
Bonsoir,

10,7k / 10,8k, enfin une journée au budget.
Livraison reçue (46 pièces) dont les premières Artem. Très belle parka, mais elle taille grand : un client qui fait du 5 était parfait en 4. On va le dire à tout le monde.

Bonne soirée,
"""),

dict(id="0911", d="2026-09-11", t="19:55", who="laetitia", subj="Clôture Cannes 11/09", body="""
Bonsoir,

11,7k / 11,3k.
2 Liviana noires vendues à une cliente fidèle de Mougins et sa fille.
Demandes : Liviana blanche 4, Aria noire 1.
Liviana noire T2 et Aria noire 1 à zéro maintenant.

Laetitia
""", sig=None),

dict(id="0912", d="2026-09-12", t="19:40", who="laetitia", subj="Clôture Cannes samedi 12/09", body="""
Bonsoir à tous,

4,6k pour 16,7k de budget, 5 tickets. Samedi raté.
Du passage (77 entrées) mais pas les bonnes tailles : Liviana noire 2, Aria noire 1 (deuxième fois cette semaine), cardigan marine XL, dolcevita noir M. 4 ventes perdues sur des clients qui étaient prêts à acheter.

Laetitia
"""),

dict(id="0912f", d="2026-09-12", t="20:02", who="laetitia", suffix="_fwd", subj="TR: Liviana noire",
     cc=[f"isabelle.moreau@{D}", f"merch-planning@{D}"], body="""
Pour appuyer ma demande de réassort Liviana noire : message d'une cliente ce soir. Si une boutique a une T2 noire, on la prend.
""", fwd="""
-------- Message d'origine --------
De : Valérie M. <valerie.m***@orange.fr>
Envoyé : samedi 12 septembre 2026 18:51
À : can01.store@valentino-retail.example
Objet : Liviana noire

Bonsoir Laetitia,
Je suis passée cet après-midi, vous n'aviez pas l'Liviana noire en 2. Pouvez-vous me la commander ? Je pars à Megève fin octobre.
Merci, à bientôt
Valérie M.
"""),

dict(id="0914i", d="2026-09-14", t="09:12", who="isabelle", reply_to="0912", suffix="_re1",
     to=[f"laetitia.rossi@{D}"], cc=[], body="""
Laetitia, samedi à -72%, un souci particulier ? Le trafic était pourtant là.
"""),

dict(id="0914r", d="2026-09-14", t="12:47", who="laetitia", reply_to="0914i", suffix="_re2",
     to=[f"isabelle.moreau@{D}"], cc=[], body="""
Bonjour Isabelle,

Pas de souci particulier en boutique, l'équipe était complète. Les entrées samedi étaient surtout des touristes japonais et anglais qui regardent. Les 4 clients qui voulaient acheter n'ont pas trouvé leur taille (Liviana noire 2, Aria noire 1...). On a demandé le réassort depuis le 2 septembre.

Et franchement le budget de septembre/octobre est calé trop haut pour l'arrière-saison : on a l'impression qu'il ne tient pas compte du fait que Cannes se vide après la mi-septembre. On fait ce qu'on peut avec la clientèle locale.

Bonne journée,
"""),

dict(id="0914", d="2026-09-14", t="19:41", who="julien", subj="Cloture 14/09", body="""
8,3k / 8,8k
Cosimo marine 6 et cardigan logo marine XS demandés.
RAS
"""),

dict(id="0915", d="2026-09-15", t="19:39", who="julien", subj="Cloture 15/09", body="""
8,2k / 8,3k. Anglais et Américains (bateaux).
Jersey Polo noir XS, Alpina 36.
"""),

# 16/09 pas de mail

dict(id="0917", d="2026-09-17", t="20:03", who="laetitia", subj="Clôture Cannes 17/09", body="""
Bonsoir,

6,3k / 11,0k.
Réassort reçu (55 pièces) : Aria noire et Liviana noire enfin, mais trop tard pour samedi. J'ai rappelé Mme M. pour l'Liviana.
Un Cosimo noir en 2 demandé.

Laetitia
""", sig=None),

dict(id="0918", d="2026-09-18", t="19:54", who="laetitia", subj="Clôture Cannes 18/09", body="""
Bonsoir à tous,

7,6k / 12,8k.
Aurea marine 4 et Nova olive 7 demandés.

Bonne soirée,
"""),

dict(id="0919", d="2026-09-19", t="19:48", who="laetitia", subj="Clôture Cannes samedi 19/09", body="""
Bonsoir,

11,0k / 18,3k, 12 tickets, beaucoup de petits paniers (polos, bonnets).
Clientèle américaine des bateaux qui partent bientôt.
Amalia noire 4 et cardi matelassé marine XS demandés.

Bon dimanche à tous,
"""),

dict(id="0921", d="2026-09-21", t="19:38", who="julien", subj="Cloture 21/09", body="""
12,3k / 9,4k :)
Ceintures Vita Belt Bag x2.
Demandes : Fiammetta marine 1, Vel marine 4, Vtrack Gtx 39 et 46.
Monteluce noir 3 a zero.
"""),

dict(id="0922", d="2026-09-22", t="19:30", who="julien", subj="Cloture 22/09", body="""
7,8k / 9,7k
RAS
"""),

dict(id="0923", d="2026-09-23", t="19:59", who="laetitia", subj="Clôture Cannes 23/09", body="""
Bonsoir,

6,1k / 10,2k. 4 tickets.
Hoodie marine M demandé, il est à zéro.

Laetitia
""", sig=None),

dict(id="0924", d="2026-09-24", t="20:15", who="laetitia", subj="Clôture Cannes 24/09", body="""
Bonsoir à tous,

15,3k / 12,4k (+23%) grâce à un groupe chinois arrivé en bus de Nice vers 15h. Casquettes, hoodies, cardigans.
Livraison de 62 pièces reçue.
Lancement Astra aujourd'hui : une cape noire vendue à une cliente monégasque + une cagoule. Les autres trouvent la cape très chère.

Laetitia
"""),

dict(id="0925", d="2026-09-25", t="19:52", who="laetitia", subj="Clôture Cannes 25/09", body="""
Bonsoir,

8,9k / 14,8k.
Demandes : Ettore 3, Vel blanc 3, cardigan marine L.

Bonne soirée,
"""),

dict(id="0926", d="2026-09-26", t="20:22", who="laetitia", subj="Clôture Cannes samedi 26/09", body="""
Bonsoir à tous,

Très belle journée : 28,1k pour 21,7k de budget.
Une famille cliente de longue date (villa à Super-Cannes) est venue faire sa garde-robe d'hiver avant de partir à la montagne : torsades beiges x3, 2 Nova marine, 2 Artem noires (prises une taille en dessous sur nos conseils), ceintures.
Le père voulait l'Artem en 7 pour son fils, on n'avait pas, j'ai pris la commande.
Fiammetta marine 2 et Nova olive 7 demandés aussi.
1 retour Valdora 2 (taille).

Bon dimanche,
"""),

dict(id="0928", d="2026-09-28", t="19:43", who="julien", subj="Cloture 28/09", body="""
6,7k / 10,5k
Aria noire x2.
Fiammetta marine 00 x2 (meme cliente, pour elle et sa soeur), Nova marine 5, Vtrack 46.
"""),

dict(id="0929", d="2026-09-29", t="19:35", who="julien", subj="Cloture 28/09", body="""
8,7k / 10,4k
Clients brésiliens. RAS.
"""),

dict(id="0930", d="2026-09-30", t="20:09", who="laetitia", subj="Clôture Cannes 30/09", body="""
Bonsoir,

6,9k / 12,3k.
2 Amalia noires vendues. 1 Aria noire 3 demandée.
Les derniers grands yachts quittent le port Canto, la saison est vraiment terminée. Il reste nos clients locaux et quelques retraités étrangers.

Laetitia
""", sig=None),

dict(id="1001", d="2026-10-01", t="20:01", who="laetitia", subj="Clôture Cannes 01/10", body="""
Bonsoir à tous,

10,2k / 13,4k.
Livraison 79 pièces dont des Astra supplémentaires. Une deuxième cape noire vendue (cliente taïwanaise).
Une cliente voulait l'Amalia en marron chocolat taille 4, on ne l'a qu'en 2.

Bonne soirée,
"""),

dict(id="1002", d="2026-10-02", t="19:46", who="laetitia", subj="Clôture Cannes 02/10", body="""
Bonsoir,

6,0k / 16,7k.
4 demandes non servies : Aurea blanche 4, Cosimo marine 1, Artem marine 7, Vtrack gris 45.
2 retours en taille (torsade L, jersey polo XL).

Laetitia
""", sig=None),

dict(id="1003", d="2026-10-03", t="19:58", who="laetitia", subj="Clôture Cannes samedi 03/10", body="""
Bonsoir à tous,

18,1k / 23,6k.
Encore une cape Astra (noire) + une oversize. Ici la Astra plaît à notre clientèle aisée, je trouve.
Un client nous a ramené son Vel T5 : la tirette de la fermeture s'est cassée après 1 mois. Échangé.
Demandes : Aurea blanche 1, Liviana noire 3, Cosimo marine 1.

Je suis en congés la semaine prochaine, Julien envoie les clôtures.

Bonne soirée,
"""),

dict(id="1005", d="2026-10-05", t="19:33", who="julien", subj="Cloture 05/10", body="""
2,6k / 11,7k. 3 tickets.
3 demandes hoodie (marine L, gris XS, gris M).
"""),

dict(id="1006", d="2026-10-06", t="19:51", who="julien", subj="cloture 06/10", attach=[("xlsx", "Cloture_CAN01_06-10.xlsx", [
    ["Boutique", "CAN01 Cannes"],
    ["Date", "06/10/2026"],
    ["CA HT", 16050],
    ["Budget", 11350],
    ["Ecart %", "41%"],
    ["Tickets", 11],
    ["Entrees", 57],
    ["Top ventes", "Cardi matelasse marine x3, Nova marine x2, cardigan logo marine x2"],
    ["Demandes", "Hoodie marine XL"],
    ["Commentaire", "bonne journee clientele locale"],
])], body="""
Ci-joint la clôture.
"""),

# 07/10 pas de mail

dict(id="1008", d="2026-10-08", t="19:39", who="julien", subj="Cloture 08/10", body="""
10,3k / 14,9k
Livraison recue (68 pcs), encore du Astra (3 pieces).
Cosimo noir 7 demandé.
"""),

dict(id="1009", d="2026-10-09", t="19:42", who="julien", subj="Cloture 09/10", body="""
8,5k / 17,0k
1 cape Astra noire vendue. Aurea noire 3 demandée.
Semaine prochaine MIPCOM au Palais.
"""),

dict(id="1010", d="2026-10-10", t="19:57", who="julien", subj="Cloture 10/10", body="""
16,2k / 24,2k
155 entrées (installation MIPCOM + 1 groupe chinois) mais peu d'achats.
Monteluce noir x2, Astra Cape x1.
Cosimo gris 1 demandé.
"""),

# 12/10 pas de mail séparé (récap lun+mar)

dict(id="1013", d="2026-10-13", t="19:49", who="julien", subj="Cloture lundi + mardi", body="""
Pas envoye hier, desole.

Lundi 12 : 1,9k / 13,0k. 3 tickets. Retour d'une cape Astra (cadeau, taille).
Mardi 13 : 6,6k / 13,1k. Cagoule Astra blanche vendue, Artem noir.
Demandes : Ettore 7, cagoule Astra blanche (on avait vendu la derniere le matin).

MIPCOM : beaucoup de badges sur la Croisette mais ils n'ont pas le temps.
"""),

dict(id="1014", d="2026-10-14", t="20:07", who="laetitia", subj="Clôture Cannes 14/10", body="""
Bonsoir à tous,

De retour. 9,2k / 14,1k.
Le Palais est plein pour le MIPCOM mais les festivaliers enchaînent les rendez-vous, peu de shopping.
Une Astra oversize vendue, Aria noire x2.
Demandes : Nova marine 2, torsade beige L.

Laetitia
""", sig=None),

dict(id="1015", d="2026-10-15", t="20:18", who="laetitia", subj="Clôture Cannes 15/10", body="""
Bonsoir,

20,5k / 15,8k (+30%).
Deux producteurs coréens du MIPCOM sont venus avec leurs assistantes : Mistral marine x2, Aria noire, bonnets.
Livraison 56 pièces reçue.
Jersey Polo noir XXL demandé.

Bonne soirée,
"""),

dict(id="1016", d="2026-10-16", t="19:55", who="laetitia", subj="Clôture Cannes 16/10", body="""
Bonsoir,

15,2k / 19,3k.
Demandes : Montgenèvre gris 1, Artem marine 7 (le client fait du 7 d'habitude, on lui a fait essayer le 6 mais trop juste aux épaules, il voulait vraiment le 7).

Laetitia
""", sig=None),

dict(id="1017", d="2026-10-17", t="19:47", who="laetitia", subj="Clôture Cannes samedi 17/10", body="""
Bonsoir à tous,

Samedi frustrant : 7,6k pour 26,4k de budget, alors qu'on a eu du passage (125 entrées). Fin du MIPCOM, beaucoup de lèche-vitrine.
Camilla blanc 4 demandé. Retour Aurea T0 (taille).
Encore 23° cet après-midi, la doudoune n'est pas une urgence pour les Cannois...

Bon dimanche,
"""),

dict(id="1019", d="2026-10-19", t="19:41", who="julien", subj="Cloture 19/10", body="""
9,4k / 14,3k
Aurea marine x2, cardigans.
Retours : Nova T7 qualite (couture col), jersey polo XL, Vel T3 fermeture cassee (2e Vel depuis debut octobre).
Iridia noir 0 demande.
"""),

dict(id="1020", d="2026-10-20", t="19:36", who="julien", subj="Cloture 20/10", body="""
4,7k / 13,7k
Aurea blanche 0 x2, Aurea noire 1. Plus de Aurea noire en 0 et 1 en stock.
"""),

dict(id="1021", d="2026-10-21", t="20:24", who="laetitia", subj="Clôture Cannes 21/10", cc=CC_MERCH, body="""
Bonsoir à tous,

18,8k / 14,9k (+26%), 14 tickets. Clientèle américaine en croisière (escale), Aria noire x3, Montgenèvre noir x2.

Demandes : Aurea blanche 0 (3e demande en 2 jours), Aria noire 1, Ettore 2.

Pour la suite d'octobre, mes besoins en réassort avant la Toussaint et le retour des clients locaux :
- Aurea noire 0 et 1, Aurea blanche 0
- Aria noire 1
- Iridia noir et blanc (plus rien du tout)
- Vtrack femme noir 39 (à zéro depuis septembre)
- Rosière noir 5

Merci et bonne soirée,
"""),
]
