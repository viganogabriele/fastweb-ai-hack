# -*- coding: utf-8 -*-
"""PAR01 - Paris Saint-Honoré (flagship, fermé le dimanche). Hand-authored closing emails.

Writers: Camille Lefèvre (SM, structured, laptop, corporate footer), Thomas Nguyen (ASM, phone, no accents,
abbreviations, writes Mondays + covers Camille's leave Oct 12-17), Inès Haddad (senior SA, once/twice).
"""
STORE = "PAR01"
D = "moncler-retail.example"
TO = [f"retail-ops-france@{D}"]
CC = [f"isabelle.moreau@{D}"]
CC_MERCH = [f"isabelle.moreau@{D}", f"merch-planning@{D}"]

LEGAL = """--
Camille Lefèvre
Store Manager | Moncler Paris Saint-Honoré
372 rue Saint-Honoré, 75001 Paris
T. +33 1 44 xx xx 10

Ce message et toutes les pièces jointes sont confidentiels et établis à l'intention exclusive de ses destinataires. Toute utilisation non conforme à sa destination est interdite. Si vous avez reçu ce message par erreur, merci de le détruire et d'en avertir l'expéditeur."""

PEOPLE = {
    "camille": dict(name="Camille Lefèvre", email=f"camille.lefevre@{D}", sig=LEGAL,
                    mailer="Microsoft Outlook 16.0", outlook=True),
    "thomas": dict(name="Thomas Nguyen", email=f"thomas.nguyen@{D}", sig="Envoyé de mon iPhone",
                   mailer="iPhone Mail (21H16)"),
    "ines": dict(name="Inès Haddad", email=f"ines.haddad@{D}",
                 sig="Inès Haddad\nSenior Sales Associate – Moncler Saint-Honoré"),
    "isabelle": dict(name="Isabelle Moreau", email=f"isabelle.moreau@{D}",
                     sig="Isabelle\n\nIsabelle Moreau\nArea Manager France & Genève", mailer="Microsoft Outlook 16.0",
                     outlook=True),
    "store": dict(name="Moncler Paris Saint-Honoré", email=f"par01.store@{D}", sig=None),
}

EMAILS = [
dict(id="0831", d="2026-08-31", t="20:12", who="thomas", subj="closing lundi 31/08", body="""
Bonsoir a tous,

Reprise tranquille, 12,7k vs 30,2 de bud. 241 entrees pour 15 tickets, ca pique.
Clientele: francais qui rentrent de vacances, pas mal d'anglais et de taiwanais.

Demandes non servies : karakorum gris T2, tib blanc T7, marin marine T1 (plus rien en SS de toute facon), valbourg blanc T4.
Retours : 1 montgenevre (cadeau) + 1 cardi matelasse chgt d'avis.

Bonne soiree
Thomas
"""),

dict(id="0901", d="2026-09-01", t="20:34", who="camille", subj="PAR01 - Closing 01/09", body="""
Bonsoir à tous,

CA net : 35,0 k€ / bud 31,7 k€ (+10%)
Entrées : 277 / tickets 22 / transfo 7,9%
Top : Tib noir, hoodie logo noir, Trailgrip femme blanc

Belle journée pour un mardi, surtout l'après-midi avec des clients chinois et US.
Le hoodie logo noir est cassé en S et M depuis la semaine dernière, est-ce qu'on peut avoir un réassort ? Maire beige T1 à zéro aussi.

Bonne soirée,
Camille
"""),

dict(id="0902", d="2026-09-02", t="20:51", who="camille", subj="PAR01 - Closing 02/09", body="""
Bonsoir,

CA net : 32,8 k€ / bud 32,1 (+2%)
Entrées 290 / transfo 7,9%

Livraison reçue ce matin avec 3 jours de retard (63 pièces), mise en stock faite dans la journée.
Demandes : Maya noir en 6 (plus de 6 depuis samedi), Trailgrip gris en 45.
Les bonnets marine partent bien, on sent les Parisiennes qui rentrent.

Camille
"""),

dict(id="0903", d="2026-09-03", t="21:05", who="camille", subj="PAR01 - Closing 03/09", body="""
Bonsoir,

CA 40,9 k€ / bud 45,5 (-10%)
343 entrées, transfo 6,7%

Grosse livraison (244 pcs) arrivée à l'heure, une partie de l'équipe a passé l'après-midi en réserve donc moins de monde en surface, ça se voit sur la transfo.
Bonne journée maille : torsades noir, Montgenèvre marine, dolcevita noir.
Valbourg blanc T4 encore demandé (2e fois cette semaine) + cardi matelassé marine XL.

Camille
"""),

dict(id="0904", d="2026-09-04", t="20:40", who="camille", subj="PAR01 - Closing 04/09", body="""
Bonsoir à tous,

CA 57,4 k€ / bud 53,4 (+8%)
477 entrées / 32 tickets
Top : Tib marine + noir (9 au total), tee logo marine x5

Montgenèvre noir 5 à zéro, 2 clients ce soir pour cette taille. Hermine marine 0 demandé aussi.
3 retours dont 2 casquettes (1 couleur, 1 changement d'avis), rien de grave.

Bon week-end à ceux qui ne travaillent pas !
Camille
"""),

dict(id="0905", d="2026-09-05", t="21:20", who="camille", subj="PAR01 - Closing samedi 05/09", cc=CC_MERCH, body="""
Bonsoir,

CA 71,7 k€ / bud 72,6 (-1%)
629 entrées, transfo 6,4%

Samedi correct, clientèle surtout française + quelques US/Italiens. Sweat col rond blanc x5, Trailgrip homme noir x4, cardigan logo noir x4.
Manques : cardi matelassé marine XXL x2, hoodie gris XXL x2 → les grandes tailles en maille homme partent très vite, est-ce que le merch peut regarder la répartition des tailles ?
Chambre noir T4 demandé aussi.

Camille
"""),

dict(id="0907", d="2026-09-07", t="20:05", who="thomas", subj="closing 07.09", body="""
Bonsoir,
44,4k pour 41,1 de bud, journee sympa. Presque la moitie de francais, chinois l'aprem.
Dolcevita noir x5, bonnet marine x3, torsade noir x3, Ambrine noir x3 (le nouveau long commence a partir).
Retours : 1 Maire T1 qualite (couture qui file sur la manche, piece mise de cote pr le SAV), 1 Tib T6 taille, 1 casquette qualite.
Demande flammette noir T4.
Thomas
"""),

dict(id="0908", d="2026-09-08", t="20:47", who="camille", subj="PAR01 - Closing 08/09", attach=[("jpg", "IMG_2231.jpg"), ("jpg", "IMG_2232.jpg")], body="""
Bonsoir,

CA 34,0 k€ / bud 36,2 (-6%) – 259 entrées.

Encore un retour Maire pour qualité aujourd'hui (T2), même souci de couture que celui d'hier. Deux en deux jours, je préfère le signaler. Photos en PJ.
Ventes : Trailgrip noir, Maire noir x3, sac à dos Makaio marine.
Valbourg blanc 4 : 3e demande en 8 jours, on n'en a jamais reçu.

Camille
"""),

dict(id="0909", d="2026-09-09", t="21:31", who="thomas", subj="closing mercredi", body="""
journee pourrie : 22,5k vs 44 de bud.
351 entrees mais 14 tickets, transfo 4%... bcp de gens qui regardent / photos, peu d'achat.
TPE 2 en panne entre 15h et 16h, on a tout fait passer sur le 1, 2 clients sont partis sans attendre.
1 client sweat blanc en L, plus de L.
Retour Bady T1 taille.
Camille en repos demain matin, je fais l'ouverture.
"""),

dict(id="0910", d="2026-09-10", t="20:38", who="camille", subj="PAR01 - Closing 10/09", body="""
Bonsoir à tous,

CA 43,6 k€ / bud 46,9 (-7%)
419 entrées, transfo 7,4%

Livraison de 280 pièces reçue, dont les premières Arneb. Très belle parka mais attention elle taille grand : on a déjà conseillé à deux clients de prendre une taille en dessous. A faire passer aux autres boutiques si ce n'est pas déjà fait.
Bady noir x4 et Bady rose poudré x2, contente de voir partir le rose.
Tee logo marine S toujours à zéro.

Camille
"""),

dict(id="0911", d="2026-09-11", t="20:55", who="camille", subj="PAR01 - Closing 11/09", body="""
Bonsoir,

CA 30,4 k€ / bud 56,2 (-46%)
376 entrées, 20 tickets

Vendredi décevant. Du monde mais beaucoup de "je reviendrai". Pas de grosse pièce, que de la maille et des tee-shirts.
Plusieurs clientes demandent déjà l'Ambrine en marron chocolat (vue sur Instagram), on n'en a que 6 pièces toutes tailles confondues, il va falloir en recevoir plus si ça continue.
Demandes : tee marine S, Trailgrip noir 39.

Camille
"""),

dict(id="0912", d="2026-09-12", t="21:12", who="camille", subj="PAR01 - Closing samedi 12/09", body="""
Bonsoir à tous,

CA 82,5 k€ / bud 82,0 – pile au budget
660 entrées / 37 tickets / transfo 5,6%

Top : dolcevita noir x7, casquette noir x5, Maire noir x4, Flammette noir x4.
Montgenèvre noir 5 toujours à zéro (depuis le 4 !), tee marine S idem. Une cliente pour la Rosière olive 2.
3 retours (cardigan, hoodie taille, Trailgrip cadeau).

Bon dimanche,
Camille
"""),

dict(id="0914", d="2026-09-14", t="20:09", who="thomas", subj="closing lundi 14/09", body="""
Bonsoir

49,5k / bud 43,9 → +13%
pas mal de coreens aujourd'hui (couples + 1 petit groupe), ils ont pris surtout Maya noir et Ilvaro blanc (x3).
1 demande flammette noir 00.
retours : tib T5 taille, chamonix M taille, 1 tee couleur.

Thomas
"""),

dict(id="0915", d="2026-09-15", t="20:44", who="camille", subj="PAR01 - Closing 15/09", body="""
Bonsoir,

CA 37,9 k€ / bud 41,5 (-9%) – 365 entrées

Cardigan logo noir x6, très bonne journée maille homme.
Le dolcevita noir est cassé en M : 2 clients aujourd'hui. Tee blanc S x2 demandés aussi.
1 retour Trailgrip 44 taille.

Camille
"""),

# 16/09: pas de mail (oubli, voir 17/09)

dict(id="0917", d="2026-09-17", t="20:58", who="camille", subj="PAR01 - Closing 17/09", body="""
Bonsoir à tous,

Désolée pour l'absence de mail hier soir, souci de connexion à la maison. Hier : 38,3 k€ pour 46,4 de budget, rien de spécial à part une demande d'Ambrine marron en 2 et une Maire marine 00.

Aujourd'hui :
CA 49,6 k€ / bud 55,3 (-10%)
351 entrées, transfo 8,6%
Tib noir x4, Maire marine x3, casquette blanche x3.
Encore une cliente pour la Maire marine 00.

Camille
"""),

dict(id="0918", d="2026-09-18", t="21:02", who="camille", subj="PAR01 - Closing 18/09", body="""
Bonsoir,

CA 43,0 k€ / bud 62,8 (-32%)
531 entrées mais transfo 4,3%

La livraison prévue hier n'est arrivée que ce matin, l'équipe a passé la matinée en réserve. Beaucoup de passage l'après-midi, peu de conversion.
Cardigan logo marine x4, noir x3, Montgenèvre marine x3.

Camille
"""),

dict(id="0919", d="2026-09-19", t="21:25", who="camille", subj="PAR01 - Closing samedi 19/09", body="""
Bonsoir à tous,

CA 79,6 k€ / bud 92,4 (-14%)
619 entrées / 39 tickets

Deux clientes coréennes cet après-midi nous ont montré la photo d'une actrice dans une série avec la Maire noire : on n'avait plus de T1. En noir il ne nous reste quasiment que du 00 et du 3. Maire marine 2 à zéro également.
Autres demandes : Tib noir T1, cardigan logo noir XXL, sweat blanc XS.
Top : bonnets blanc et marine (8), sweat blanc x4, Ecrins x4, Bady noir x4.

Camille
"""),

dict(id="0921", d="2026-09-21", t="20:16", who="thomas", subj="closing 21/09", body="""
Bonsoir,
45,2k / 46,8 bud, ok.
encore bcp de coreennes (17% des clients d'apres la detaxe). elles demandent toutes la meme chose : maire noire en 1 ou 2. on n'a plus rien en noir de 0 a 2. 2 demandes T1 aujourd'hui, j'ai pris les numeros.
Hoodie noir x5, Bady noir x5, gants tech x4.
5 retours dont un echange Arneb 3 -> 2, trop grand. Maya T3 taille aussi.
Thomas
"""),

dict(id="0922", d="2026-09-22", t="20:50", who="ines", subj="Clôture Saint-Honoré mardi 22 septembre", body="""
Bonsoir à toutes et à tous,

Je me permets d'envoyer la clôture ce soir car Camille est en formation et Thomas en repos.

Chiffre d'affaires : 38 680 € pour un budget de 46 670 €.
Nous avons eu 324 entrées et 22 tickets.
Clientèle assez internationale (américains, quelques japonais).
Meilleures ventes : Hermine noir (4 pièces !), cardigan logo noir, polo blanc.

Une cliente voulait la Maire noire en taille 1, nous n'en avons plus. Un client pour le pantalon Chamonix en XL.
Un retour d'Arneb en taille 3, le client la trouvait trop grande.

Bonne soirée à tous,
"""),

dict(id="0923", d="2026-09-23", t="20:41", who="camille", subj="PAR01 - Closing 23/09", cc=CC_MERCH, body="""
Bonsoir à tous,

CA 51,9 k€ / bud 48,2 (+8%)
417 entrées / transfo 8,2%

Gros sujet Maire noire : 5 demandes aujourd'hui (1, 1, 0, 2, 4), quasi toutes des clientes coréennes. Le noir est à zéro de 0 à 2 depuis le week-end. Est-ce qu'on a une date de réassort ? Le dépôt n'affiche rien côté noir.
Aussi : Bady noir 4, Ambrine marron 0 (encore le marron...).
Ventes : bonnet blanc x5, cardigan logo marine x5, Maya marine x3.

Camille
"""),

dict(id="0924", d="2026-09-24", t="21:03", who="camille", subj="PAR01 - Closing 24/09", body="""
Bonsoir,

CA 47,3 k€ / bud 62,3 (-24%)
404 entrées, 22 tickets

Livraison reçue (225 pcs), à l'heure, mais toujours pas de Maire noire dedans.
On essaie de basculer sur la Maire marine et blanche : 4 marine + 2 blanches vendues aujourd'hui, ça marche avec certaines clientes chinoises mais pas avec les Coréennes, elles veulent la noire et c'est tout. 2 demandes T1 encore.

Lancement Genius Polaris ce matin : une cagoule vendue, beaucoup d'essayages sur la cape et la doudoune oversize. Retour des clients pour l'instant : ça taille petit et le prix (2 900 € la cape) fait reculer.

Camille
"""),

dict(id="0925", d="2026-09-25", t="20:37", who="camille", subj="PAR01 - Closing 25/09", body="""
Bonsoir à tous,

CA 65,0 k€ / bud 73,6 (-12%)
508 entrées

Cardi matelassé noir x7 (!), bonnet marine x6, cardigan logo noir x3.
Maire noire : 3 demandes (2 en T2, 1 en T1).
Cape Polaris blanche demandée en XS, on ne l'a pas reçue en XS.
Torsade beige XL demandée.

Camille
"""),

dict(id="0925r", d="2026-09-25", t="22:14", who="isabelle", reply_to="0925", suffix="_re1", cc=[f"camille.lefevre@{D}"], to=[f"par01.store@{D}"], body="""
Camille,

Merci. Peux-tu me chiffrer les demandes de Maire noire non servies depuis vendredi dernier, à peu près, et la part de clientes coréennes ? Je fais remonter au merch demain matin, MIL01 et LON02 ont le même souci.
"""),

dict(id="0926r", d="2026-09-26", t="09:48", who="camille", reply_to="0925r", suffix="_re2", to=[f"isabelle.moreau@{D}"], cc=[f"thomas.nguyen@{D}"], sig="Camille", body="""
Bonjour Isabelle,

De mémoire et avec la liste d'attente : une quinzaine de demandes depuis samedi 19, dont au moins 2/3 de clientes coréennes (le reste chinoises et 1 ou 2 Françaises). Surtout en 1 et 2, quelques 0.
On a 9 noms sur la liste d'attente avec numéro.
Elles parlent toutes de la même série / actrice. Je te tiens au courant ce soir.

Bonne journée
"""),

dict(id="0926", d="2026-09-26", t="21:18", who="camille", subj="PAR01 - Closing samedi 26/09", body="""
Bonsoir à tous,

CA 86,4 k€ / bud 99,0 (-13%)
636 entrées / 38 tickets

Samedi chargé mais sous le budget et il manque clairement la Maire noire : 7 demandes aujourd'hui (3 en T2, 2 en T1, une 0, une 4). Isabelle, j'ai complété la liste.
D'après les guides, beaucoup de groupes coréens après Chuseok la semaine prochaine.
Top : Flammette noir x5, cardi matelassé noir x5, cardigan logo marine x4.

Camille
"""),

dict(id="0928", d="2026-09-28", t="20:22", who="thomas", subj="closing lundi 28/09", body="""
Bonsoir a tous,

61,3k pr 55,4 de bud, bien.
qq clients saoudiens + chinois, Karakorum noir x4.

maire noire : 8 demandes !! 5 en 0 et 3 en 2. bcp de coreennes encore, on leur propose le marine elles disent non.

2 Tib T4 retournes pour la fermeture eclair : le curseur se bloque puis se casse. Meme probleme sur les deux, achetes fin aout. Mis de cote pour le SAV, si qqn sait s'il y a une procedure...

cardi matelasse noir L a zero.

Thomas
"""),

dict(id="0929", d="2026-09-29", t="21:09", who="camille", subj="PAR01 - Closing 29/09 – début FW", body="""
Bonsoir à tous,

CA 90,1 k€ / bud 57,7 (+56%)
531 entrées / 42 tickets / transfo 7,9%

Début de la Fashion Week : beaucoup de passage (stylistes, acheteurs, influenceurs, quelques VIC qui passent entre deux défilés). Très belle journée Maya noir + marine (8), Hermine blanc x4, Trailgrip x4.

Demandes non servies : Maire noire x8 (T1 x3, T2 x3, 3, 4), Ambrine marron 2, Ilvaro rose poudré 2, cardi matelassé marine XXL, tee marine XXL.
1 Tib de plus en retour pour la fermeture.

Camille
"""),

dict(id="0930", d="2026-09-30", t="21:22", who="camille", subj="PAR01 - Closing 30/09 – FW + Golden Week", body="""
Bonsoir à tous,

CA 84,7 k€ / bud 60,4 (+40%)
751 entrées / 43 tickets / transfo 5,7%

Début de la Golden Week : les clients chinois sont là, presque la moitié des tickets aujourd'hui. Les bordereaux de détaxe nous prennent un temps fou, il nous faudrait clairement une personne de plus le week-end.
Sweat col rond noir x9, Maya olive x6 (!), cardigan logo noir x5.

Manques : Maire noire (3 demandes), Bady rose 4, Ilvaro rose 0, Ilvaro blanc 3, cardi matelassé noir L, hoodie marine XS, tee noir XXL.
2 Tib retournés (zip).

Camille
"""),

dict(id="1001", d="2026-10-01", t="21:15", who="camille", subj="PAR01 - Closing 01/10", body="""
Bonsoir,

CA 75,1 k€ / bud 68,6 (+9%)
728 entrées, transfo 5,2%
45% de clientèle chinoise.

Livraison de 312 pièces reçue ce matin.
Tib : 3 retours aujourd'hui pour la fermeture, ça devient un vrai sujet (8 depuis lundi dernier). Toutes des pièces reçues mi-août d'après les étiquettes. On arrête de mettre le Tib noir en avant en attendant une réponse ?
Maire noire : 8 demandes (T1 x3, T2 x3, 0 x2).
Top : écharpe cachemire noir x6, Peyre x5, hoodie noir x5, dolcevita chocolat x4.

Camille
"""),

dict(id="1002", d="2026-10-02", t="21:40", who="camille", subj="PAR01 - Closing 02/10", body="""
Bonsoir à tous,

CA 153,6 k€ / bud 81,7
1 174 entrées / 69 tickets

Journée énorme. Maya noir x12, tee noir x7, dolcevita noir x6.

Depuis ce matin des clientes asiatiques (coréennes surtout, quelques Chinoises et Japonaises) nous montrent sur leur téléphone la photo de la chanteuse de LUMIERE, Yoon Ha-eun, prise hier devant un défilé avec une doudoune courte rose : c'est l'Ilvaro rose poudré. On n'en a plus depuis fin septembre (le 0 et le 3 sont partis). Deux demandes "officielles" (0 et 2) mais beaucoup plus de questions. On a proposé l'Ilvaro noir/blanc à quelques-unes.

Maire noire : 7 demandes dont 3 en 00. Ambrine marron T1, Peyre 7.
5 Tib retournés pour la fermeture aujourd'hui...

Camille
"""),

dict(id="1002c", d="2026-10-02", t="22:06", who="camille", reply_to="1002", suffix="_corr", subj="RE: PAR01 - Closing 02/10 - correction CA", quote=False, body="""
Correction : le CA de la journée est de 135,6 k€ et non 153,6. Inversion de chiffres, désolée.
"""),

dict(id="1003", d="2026-10-03", t="21:48", who="camille", subj="PAR01 - Closing samedi 03/10", body="""
Bonsoir à tous,

CA 175,7 k€ / bud 117,6 (+49%) – meilleur samedi de l'année je pense
1 667 entrées / 93 tickets

Bonnet marine x11, Tib noir x8 (malgré tout), Montgenèvre noir x7, cardigan logo noir x7.
Golden Week + fin de semaine Fashion Week, file à la détaxe tout l'après-midi.

Maire noire : 14 demandes aujourd'hui (00 à 3), on ne prend plus les noms à partir de 30 sur la liste. Ambrine marron 2 (x2), Karakorum noir 6 (x2), tee noir L (x2).
Ilvaro rose : encore des clientes avec la photo de la chanteuse, toujours rien en stock.
Polaris : 2 pièces vendues à des clients chinois (cape blanche + oversize noire). Les clients européens essaient et reposent.

Camille
"""),

dict(id="1003d", d="2026-10-03", t="21:50", who="camille", suffix="_dup", subj="PAR01 - Closing samedi 03/10", body="""
Bonsoir à tous,

CA 175,7 k€ / bud 117,6 (+49%) – meilleur samedi de l'année je pense
1 667 entrées / 93 tickets

Bonnet marine x11, Tib noir x8 (malgré tout), Montgenèvre noir x7, cardigan logo noir x7.
Golden Week + fin de semaine Fashion Week, file à la détaxe tout l'après-midi.

Maire noire : 14 demandes aujourd'hui (00 à 3), on ne prend plus les noms à partir de 30 sur la liste. Ambrine marron 2 (x2), Karakorum noir 6 (x2), tee noir L (x2).
Ilvaro rose : encore des clientes avec la photo de la chanteuse, toujours rien en stock.
Polaris : 2 pièces vendues à des clients chinois (cape blanche + oversize noire). Les clients européens essaient et reposent.

Camille
"""),

dict(id="1005", d="2026-10-05", t="20:31", who="thomas", subj="closing lundi 05/10", body="""
Bonsoir

91,4k vs 61,3 de bud, +49%
toujours bcp de chinois (38%), qq taiwanais.
Sweat noir x6, Tib noir x4, Rosiere noir x4, Maya marine x4, ceintures Legere x4.

MAIRE NOIRE T1 : j'ai arrete de compter apres 10. un groupe de coreennes avec une guide, toutes en 1. + 00 x2, 0 x2, 2, 3. et 1 Maire blanche en 2 qu'on n'a plus.
polo noir XL x2.
Ilvaro rose 0 : 1 demande, toujours avec la photo de la chanteuse sur le tel.

7 retours (tailles surtout, 1 chambre qualite).

Thomas
"""),

dict(id="1006", d="2026-10-06", t="21:11", who="camille", subj="PAR01 - Closing 06/10", body="""
Bonsoir à tous,

CA 75,6 k€ / bud 61,0 (+24%)
805 entrées / 40 tickets / transfo 5,0%

Ambrine marron : 4 demandes aujourd'hui (0, 1, 2 x2). C'est la couleur que tout le monde veut, on n'a plus que le 3 et le 4 en marron. Le noir ne remplace pas.
Maire noire : 5 demandes. Hermine blanc 2, Ilvaro rose 0.
Retours : 2 Tib (zip), 2 Montcla en taille (à suivre), 1 Ilvaro couleur, 1 Ambrine noir changement d'avis.
Stock cassé aussi : Maire marine 0, Karakorum noir 4, tee noir L.

Camille
"""),

dict(id="1007", d="2026-10-08", t="08:42", who="camille", subj="PAR01 - Closing 07/10 (envoi tardif)", body="""
Bonjour à tous,

Désolée, hier soir inventaire tournant jusqu'à 22h, je n'ai pas eu le temps.

Mercredi 07/10 :
CA 78,2 k€ / bud 66,2 (+18%)
626 entrées

Fin de la Fashion Week.
On a vendu 5 Maire beige, mais à des clientes chinoises : les Coréennes n'en veulent pas, elles attendent la noire (3 demandes T3 + T2 hier).
Karakorum noir 4 (x2) et 6, Arneb noir 6, torsade blanc L (x2), Hermine marine 00.
Encore 3 Tib zip.

Camille
"""),

dict(id="1008", d="2026-10-08", t="21:19", who="camille", subj="PAR01 - Closing 08/10", body="""
Bonsoir à tous,

CA 108,0 k€ / bud 73,1 (+48%)
751 entrées / 53 tickets

Dernier jour de Golden Week, encore 45% de Chinois.
Énorme livraison (576 pièces), toujours pas de Maire noire. 8 demandes aujourd'hui (1 x3, 0 x2, 2 x2, 00).
Polaris : 4 pièces parties (3 capes noires + 1 oversize) – uniquement à des clients chinois.
Ilvaro rose 0 : 1 demande.
2 Tib zip.

Camille
"""),

dict(id="1009f", d="2026-10-09", t="11:05", who="camille", suffix="_fwd", subj="TR: Doudoune Tib - fermeture cassée", cc=[f"isabelle.moreau@{D}", f"quality-customer-care@{D}"], body="""
Pour info, mail reçu d'un client fidèle ce matin. Même problème que les retours en boutique. Je lui ai proposé un échange dès réception d'une pièce saine, mais il veut un remboursement. Comment on gère ?
""", fwd="""
-------- Message transféré --------
De : Arnaud D. <a.delc***@gmail.com>
Date : jeu. 8 oct. 2026 à 23:12
Objet : Doudoune Tib - fermeture cassée
À : par01.store@moncler-retail.example

Bonjour,

J'ai acheté chez vous fin août un gilet Tib noir (taille 4). Après 3 semaines la tirette de la fermeture éclair s'est bloquée puis cassée en deux. Pour un article à ce prix je suis franchement déçu.
Je passe samedi, merci de me dire ce que vous pouvez faire.

Cordialement,
Arnaud D.
"""),

dict(id="1009", d="2026-10-09", t="20:44", who="camille", subj="PAR01 - Closing 09/10", body="""
Bonsoir,

CA 76,9 k€ / bud 88,5 (-13%)
691 entrées

La vague chinoise retombe (19% aujourd'hui). Bady noir x6, cardi matelassé noir x6.
Maire noire : 11 demandes (0 x3, 1 x3, 00 x2, 2 x2, 3). On a dépassé 40 noms sur la liste.
Ilvaro rose 0 et Ilvaro blanc 00 demandés.

Camille
"""),

dict(id="1010", d="2026-10-10", t="21:16", who="camille", subj="PAR01 - Closing samedi 10/10", body="""
Bonsoir à tous,

CA 123,1 k€ / bud 117,6 (+5%)
1 039 entrées / 62 tickets

4 clientes pour l'Ambrine marron en 1 aujourd'hui, on n'a plus que 00, 3 et 4. Si une autre boutique a du 1 et du 2 en marron, on prend.
Maire noire : 10 demandes. Montcla marine 4 (x2), Peyre 3, Ilvaro blanc 2.
Top : sac Makaio noir x5, cardigans logo x10, bonnet marine x5, Maya noir x5.

Je suis en congés du 12 au 17, Thomas prend le relais pour les mails.

Bonne soirée,
Camille
"""),

dict(id="1012", d="2026-10-12", t="20:28", who="thomas", subj="closing lundi 12/10", body="""
Bonsoir,

30,2k / 63,9 bud. -53%. dur.
542 entrees, 23 tickets. les touristes sont repartis.
13 retours aujourd'hui (!!) : tailles et cadeaux surtout, post golden week. 1 Ilvaro, 1 Maya, tees, sweats, Trailgrip...

Bonne nouvelle : on a recu les Ilvaro rose (12 pieces du 00 au 4), la livraison DHL est arrivee dimanche, deposee au gardien. 1 vendue aujourd'hui.
Mauvaise nouvelle : la demande etait surtout pdt la fashion week...

Maire noire : 9 demandes (0 x3, 4 x3, 1, 2, 3). Ambrine marron 0. Peyre 1 et 3.

Thomas
"""),

dict(id="1013", d="2026-10-13", t="20:02", who="thomas", subj="closing mardi 13/10 - greve", body="""
Bonsoir a tous,

Greve RATP : lignes 1, 8 et 9 a l'arret ou presque. 2 vendeuses arrivees a 12h, ouverture a 4 personnes. Rue St Honore quasi vide le matin, un peu mieux apres 16h.
32,9k vs 64,5 de bud. 266 entrees seulement, 22 tickets (transfo 8% quand meme).

Il commence a faire frais, qq clients pour les doudounes l'aprem.
Maire noire : 6 demandes. torsade beige L.
Ilvaro rose : 0 vente aujourd'hui. On a vendu 1 bonnet rose poudre lol.
3 Tib zip encore.

Thomas
"""),

dict(id="1014", d="2026-10-14", t="20:19", who="thomas", subj="closing 13/10", body="""
53,6k / bud 69,0
450 entrees. Retour des metros, ca va mieux.
le froid aide : Maire marine x4, bonnets blanc et noir x7, hoodies.
maire marine 0 a zero (1 demande).
8 retours divers.
"""),

dict(id="1015", d="2026-10-15", t="20:47", who="thomas", subj="closing jeudi 15/10", cc=CC_MERCH, body="""
Bonsoir,

55,4k pr 82,6 de bud (-33%)
540 entrees, 30 tickets
Hermine marine x4, hoodie noir x5.

Livraison 450 pcs ce matin. Pas de Maire noire dedans, on nous avait dit semaine du 16 ?
Par contre on recoit encore du Polaris (capes + oversize L/XL). Depuis la fin de la golden week on n'en vend plus du tout. Les clients (europeens) trouvent ca petit et trop cher pour ce que c'est. Est-ce qu'on peut arreter les envois / renvoyer ?

Thomas
"""),

dict(id="1016", d="2026-10-16", t="20:36", who="thomas", subj="closing ven 16/10", body="""
Bonsoir

73,5k / 92,0 bud
635 entrees
Trailgrip femme noir x6, Legere x5, Bady noir x5.

Ambrine marron : 4 demandes (0, 1, 2, 3), on n'a plus que du 00 et du 4.
Maire noire : 3 demandes. D'apres le merch elle est dispo au depot a partir d'aujourd'hui, on devrait etre livres la semaine prochaine.
2 Tib zip + 1 Maire T0 taille.

Thomas
"""),

dict(id="1017", d="2026-10-17", t="21:04", who="thomas", subj="closing samedi 17/10", body="""
Bonsoir a tous

113,6k vs 126,5 bud (-10%)
878 entrees / 64 tickets

le froid = bonnets : bonnet blanc x12 (!), Bady blanc x7, cardigan logo marine x5, Karakorum noir x5.
Maire noire : 0 x3, 2. polo blanc L, Trailgrip femme noir 40.
Ilvaro rose : on en a encore une douzaine en stock (recu 2 de plus jeudi), quasi aucune vente.

Thomas
"""),

dict(id="1019", d="2026-10-19", t="21:22", who="camille", subj="PAR01 - Closing 19/10 + points en suspens", cc=CC_MERCH, body="""
Bonsoir à tous,

De retour, merci Thomas pour la semaine.

CA 79,9 k€ / bud 69,2 (+15%)
437 entrées / 37 tickets / transfo 8,5%
Maya noir x7, Karakorum marine x6, bonnet rose poudré x3. 27% de clients chinois aujourd'hui, pas mal de couples.
9 retours (tailles, cadeaux, 1 Maire qualité).

Points en suspens :
1) Maire noire : toujours rien. Plus de 40 clientes sur la liste d'attente, encore une demande en 0 aujourd'hui. On nous annonce le dépôt réapprovisionné depuis vendredi : merci de nous donner une date de livraison, il faut qu'on rappelle les clientes.
2) Ilvaro rose poudré : on a 12 pièces en stock (00 à 4) qui ne tournent pas, 2 ventes en une semaine. La demande ici était liée à la Fashion Week et aux touristes asiatiques. D'après le groupe WhatsApp des SM, c'est en rupture partout en Asie. Est-ce qu'on ne devrait pas les transférer ?
3) Tib : on approche les 30 retours zip depuis fin septembre. Toujours pas de note officielle ?
4) Ambrine marron : une demande en 1 aujourd'hui, il ne nous reste que 00 / 3 / 4.
5) Cardigan logo marine M à zéro.

Camille
"""),

dict(id="1019r", d="2026-10-19", t="22:31", who="isabelle", reply_to="1019", suffix="_re1", cc=[f"merch-planning@{D}"], to=[f"camille.lefevre@{D}"], body="""
Merci Camille, très clair.
Point 2 : bonne remarque, je vois demain avec le merch et Vivian (HK/TW) s'il y a un intérêt à transférer.
Point 3 : une note qualité doit sortir cette semaine, en attendant échange ou remboursement, pièces au SAV avec le code DEF.
"""),

dict(id="1020", d="2026-10-20", t="20:39", who="camille", subj="PAR01 - Closing 20/10", body="""
Bonsoir,

CA 41,3 k€ / bud 66,9 (-38%)
381 entrées

Mardi très calme, le froid est passé et les touristes aussi.
Maya noir x4, casquette marine x3.
Maire noire T2 et T3, cardigan logo marine M. Polo noir L à zéro.
Retour Arneb T5 pour la taille (encore).

Camille
"""),

dict(id="1021", d="2026-10-21", t="20:53", who="camille", subj="PAR01 - Closing 21/10", body="""
Bonsoir à tous,

CA 74,4 k€ / bud 73,6 (+1%)
496 entrées / 35 tickets

Trailgrip noir x4, Karakorum marine x4, Tib marine x4, hoodie noir x4.
Maire noire : 5 demandes (2 x2, 00, 0, 1). Toujours pas de date de livraison malgré le retour au dépôt.
Hermine marine 3, Bady blanc 4, Karakorum gris 2.
Cardigan logo M à zéro en noir et en marine, il nous faut du M.

Camille
"""),
]
