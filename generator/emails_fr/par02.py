# -*- coding: utf-8 -*-
"""PAR02 - Paris Galeries Lafayette Haussmann (shop-in-shop, ouvert le dimanche). Hand-authored closing emails.

Writers: Sophie Marchand (SM, chatty, warm, a few emoticons), Karim Benali (ASM, short, CAPS when angry,
weekends), store mailbox par02.store@ used for the "FICHE DE CLOTURE" form (habit: amounts TTC = incl. VAT!),
usually filled by Lucie Park (SA, Korean-speaking) on Sundays.
"""
STORE = "PAR02"
D = "valentino-retail.example"
TO = [f"retail-ops-france@{D}"]
CC = [f"isabelle.moreau@{D}"]
CC_MERCH = [f"isabelle.moreau@{D}", f"merch-planning@{D}"]

SOPHIE_SIG = """Sophie

Sophie Marchand
Store Manager – Valentino Galeries Lafayette Paris Haussmann
40 bd Haussmann, 75009 Paris – Coupole, 1er étage"""

PEOPLE = {
    "sophie": dict(name="Sophie Marchand", email=f"sophie.marchand@{D}", sig=SOPHIE_SIG,
                   mailer="Microsoft Outlook 16.0", outlook=True),
    "karim": dict(name="Karim Benali", email=f"karim.benali@{D}", sig="K.\n\nEnvoyé de mon iPhone",
                  mailer="iPhone Mail (21H16)"),
    "box": dict(name="Valentino GL Haussmann", email=f"par02.store@{D}", sig=None, mailer="Microsoft Outlook 16.0"),
    "isabelle": dict(name="Isabelle Moreau", email=f"isabelle.moreau@{D}", sig=None, outlook=True),
    "merch": dict(name="Marco Bellini", email=f"marco.bellini@{D}",
                  sig="Marco Bellini\nMerchandise Planning – EMEA Retail", mailer="Microsoft Outlook 16.0", outlook=True),
}

FORM_HEAD = "FICHE DE CLOTURE - CORNER VALENTINO GL HAUSSMANN"


def form(date, ca_ttc, tickets, entrees, remarques, ventes, ruptures, retours, signe):
    """The store's fixed closing form (deliberate habit). Amounts are TTC (VAT incl.)."""
    pm = round(ca_ttc / tickets) if tickets else 0
    n = lambda x: f"{x:,.0f}".replace(",", " ")
    return f"""{FORM_HEAD}
Date : {date}
CA TTC : {n(ca_ttc)} €
Nb tickets : {tickets}
Panier moyen TTC : {n(pm)} €
Entrées (compteur GL) : {entrees}
Meilleures ventes : {ventes}
Ruptures / demandes non servies : {ruptures}
Retours : {retours}
Remarques : {remarques}
Rempli par : {signe}"""


EMAILS = [
dict(id="0831", d="2026-08-31", t="21:18", who="sophie", subj="Clôture GL 31/08", body="""
Bonsoir à tous,

Reprise douce : 16,5k HT pour 22,6k de budget.
Le grand magasin est encore en mode rentrée scolaire, beaucoup de familles au rayon enfants mais pas trop chez nous. Clientèle très mélangée (Brésiliens, Chinois, quelques Français).
Tee logo noir x4, casquettes.
Les Mario noir sont cassés en 3 et 5 mais c'est la fin de l'été, pas de réassort à prévoir je pense.

Bonne soirée !
"""),

dict(id="0901", d="2026-09-01", t="21:02", who="karim", subj="cloture 01/09", body="""
16,3k / 22,2k. 10 tickets.
RAS, 2 belles ventes a une famille saoudienne (Cosimo).
"""),

dict(id="0902", d="2026-09-02", t="21:26", who="sophie", subj="Clôture GL 02/09", body="""
Bonsoir,

23,4k / 24,0k, quasi au budget. Transfo 16% (101 entrées), très bonne journée de vente sur peu de passage.
Clientes coréennes et chinoises l'après-midi. Fiammetta noir 0 à zéro.

Belle soirée,
"""),

dict(id="0903", d="2026-09-03", t="21:40", who="sophie", subj="Clôture GL 03/09", body="""
Bonsoir à tous,

26,4k vs 32,4k.
Livraison 212 pcs réceptionnée au quai des Galeries à 7h, mise en rayon terminée à midi, merci à l'équipe !
Tee logo noir x4, Aria noir x3, jersey polo noir x3.

Sophie
""", sig=None),

dict(id="0904", d="2026-09-04", t="21:35", who="box", subj="Fiche de clôture 04/09", body=form(
    "04/09/2026", 38016, 19, 141,
    "Bonne journee chaussures homme.", "Vtrack Gtx noir x6, Mistral noir x3",
    "-", "1 Alpina 37 (taille)", "Karim")),

dict(id="0905", d="2026-09-05", t="21:52", who="karim", subj="cloture samedi", body="""
48,3k vs 52,9k
CN 20% / KR 11%. Les coreennes prennent la Aurea noire (4 vendues).
1 client pour Cosimo noir en 1, pas dispo.
"""),

dict(id="0906", d="2026-09-06", t="20:44", who="karim", subj="cloture dimanche 06/09", body="""
37,7k / 37,1k ok
dimanche correct, cardi matelasse noir x5, torsade noir x5.
Vtrack noir 39 demande.
"""),

dict(id="0907", d="2026-09-07", t="21:20", who="sophie", subj="Clôture GL 07/09", body="""
Bonsoir à tous,

26,1k pour 30,7k de budget.
4 demandes non servies aujourd'hui : Liviana blanc 2, Montgenèvre marine 6, Valdora noir 00, pantalon Cortina XL.
1 retour Liviana T1 (taille).

Isabelle, as-tu pu regarder mon mail sur le planning de la Fashion Week ? On aimerait une personne en renfort du 29/09 au 07/10 (+ Golden Week).

Bonne soirée,
"""),

dict(id="0907ooo", d="2026-09-07", t="21:20", who="isabelle", suffix="_auto", reply_to="0907", quote=False,
     subj="Réponse automatique : Clôture GL 07/09", to=[f"sophie.marchand@{D}"], cc=[], auto=True, body="""
Bonjour,

Je suis absente du bureau jusqu'au vendredi 11 septembre inclus avec un accès limité à mes mails.
Pour toute urgence boutique, merci de contacter retail-ops-france@valentino-retail.example.

Cordialement,
Isabelle Moreau
"""),

dict(id="0908", d="2026-09-08", t="21:12", who="sophie", subj="Clôture GL 08/09", body="""
Bonsoir,

Très belle journée : 34,0k pour 28,5k de budget (+19%) et 18% de transfo !
Les clientes coréennes adorent la Aurea : 5 vendues (3 noires, 2 blanches).
1 retour Montgenèvre 7 taille.

Sophie
""", sig=None),

dict(id="0909", d="2026-09-09", t="21:44", who="karim", subj="cloture 09/09", body="""
27,5k / 33,2k
Ettore x3. Valdora noir 00 encore demande (2e fois). 1 retour Aurea qualite (T1).
"""),

dict(id="0910", d="2026-09-10", t="21:30", who="sophie", subj="Clôture GL 10/09", body="""
Bonsoir à tous,

46,0k / 35,0k (+31%) :)
Nova marine x5 (des Chinois, une famille a pris 3 Nova d'un coup).
Livraison 282 pcs reçue, dont 3 Amalia marron et les premières Artem.
1 sweat blanc XL demandé.

Bonne soirée,
"""),

dict(id="0911", d="2026-09-11", t="21:16", who="sophie", subj="Clôture GL 11/09", body="""
Bonsoir,

35,2k / 44,5k.
La couleur chocolat est demandée partout, même en maille : une cliente voulait le dolcevita marron en M, on n'en a pas au corner.
3 retours changement d'avis (Nova, Cosimo, cardi matelassé).

Sophie
""", sig=None),

dict(id="0912", d="2026-09-12", t="21:58", who="karim", subj="cloture samedi 12", body="""
49,3k / 63,0k (-22%)
bonnets noirs x5, Artem noir x3.
ATTENTION ARTEM : taille grand, on conseille une taille en dessous a tout le monde. 2 clients sur 3 ont pris -1.
"""),

dict(id="0913", d="2026-09-13", t="20:41", who="box", subj="Fiche de clôture dim 13/09", body=form(
    "13/09/2026", 44208, 24, 175,
    "7 Aurea noires vendues dont 5 a des clientes coreennes !!", "Aurea noir x7, tee noir x3, hoodie marine x3",
    "-", "-", "Lucie")),

dict(id="0914", d="2026-09-14", t="21:09", who="sophie", subj="Clôture GL 14/09", body="""
Bonsoir à tous,

40,2k / 32,3k (+24%), très bon lundi.
Clientèle chinoise et US. Hoodie marine, cardi matelassé noir, Cosimo noir.
Une demande Aria blanc 4.

Sophie
""", sig=None),

dict(id="0915", d="2026-09-15", t="21:22", who="sophie", subj="Clôture GL 15/09", body="""
Bonsoir,

23,2k pour 33,3k, journée molle.
Plus de Aurea noire en 1 (1 cliente aujourd'hui). Il reste 0, 2 et 3 je crois.
Bonnet rose poudré : premier vendu !

Bonne soirée,
"""),

dict(id="0916", d="2026-09-16", t="21:49", who="karim", subj="cloture 16/09", body="""
31,4k / 34,5k
Aurea noire : plus de 0 ni de 1. Jersey Polo noir S et L a zero (1 client L).
3 bonnets rose poudre vendus, ca marche bien chez les jeunes chinoises.
"""),

dict(id="0917", d="2026-09-17", t="21:14", who="sophie", subj="Clôture GL 17/09", cc=CC_MERCH, body="""
Bonsoir à tous,

37,8k / 39,1k.
Livraison 294 pcs reçue, mais pas de Aurea noire alors qu'on l'avait demandée la semaine dernière. Il ne nous reste quasiment plus rien en noir de 00 à 2.
Alpina noir x4, cardigan logo noir x5.
1 retour Aurea T3 (taille).

Merci au merch de nous dire ce qui est prévu sur la Aurea noire,
"""),

# 18/09 : pas de mail

dict(id="0919", d="2026-09-19", t="22:05", who="karim", subj="cloture samedi 19/09", body="""
52,5k / 66,4k
cardigan logo noir x9 !!
3 coreennes pour la Aurea noire T1, on n'a plus que du 3 en noir.
retours Mistral 3 + Cosimo 4 taille.
"""),

dict(id="0920", d="2026-09-20", t="20:37", who="box", subj="Fiche de clôture 20/09", body=form(
    "20/09/2026", 58645, 24, 191,
    "4 demandes Aurea noire (1, 1, 00, 2) de clientes coreennes. Elles parlent toutes de la serie du samedi soir sur tvN : l'actrice principale porte la Aurea noire. Je pense qu'on va en avoir beaucoup.",
    "cardigan logo noir x3, Aurea blanc x3, Aria blanc x3", "Aurea noir 00/0/1/2",
    "Vel 1 (chgt avis), tee XL", "Lucie")),

dict(id="0921", d="2026-09-21", t="21:11", who="sophie", subj="Clôture GL 21/09", body="""
Bonsoir à tous,

26,7k / 34,7k.
Aurea noire : 4 demandes (00, 0, 1, 2), plus rien en stock dans ces tailles. Lucie avait raison hier, les Coréennes arrivent avec la photo de l'actrice.
Cosimo marine 2 demandé. Aria noir 2 à zéro.

Bonne soirée,
"""),

dict(id="0922", d="2026-09-22", t="21:27", who="sophie", subj="Clôture GL 22/09 - Aurea noire", cc=CC_MERCH, body="""
Bonsoir,

33,6k / 34,1k. Beaucoup d'Américains et d'Allemands aujourd'hui.

Aurea noire : 5 demandes (00, 0, 1, 2, 4). On est à zéro en 00/0/1/2.
Est-ce qu'un transfert depuis une autre boutique est possible ? Saint-Honoré a le même problème d'après Camille.
Aria noir 3 demandé.

Sophie
""", sig=None),

dict(id="0923", d="2026-09-23", t="21:41", who="karim", subj="cloture 23/09", body="""
35,3k / 39,4k
On ecoule la Aurea marine (5 vendues) mais pas aux coreennes, elles veulent la noire, aucune n'a pris la marine.
Jersey Polo noir S zero.
"""),

dict(id="0924", d="2026-09-24", t="21:19", who="sophie", subj="Clôture GL 24/09", body="""
Bonsoir à tous,

42,7k / 47,1k.
Livraison 325 pcs, toujours pas de Aurea noire.
8 demandes aujourd'hui !! (0 x2, 1 x2, 2 x2, 3, 4)
Aurea marine x5, beige x2, Aria blanc x4.

Bonne soirée,
"""),

dict(id="0925m", d="2026-09-25", t="10:12", who="merch", reply_to="0922", suffix="_re1",
     to=[f"sophie.marchand@{D}"], cc=[f"isabelle.moreau@{D}", f"camille.lefevre@{D}"], body="""
Bonjour Sophie,

La Aurea noire est en rupture au dépôt (retard fournisseur sur le nylon laqué). Réassort prévu semaine 42, autour du 16/10.
Transfert pas possible pour l'instant : PAR01, MIL01 et LON02 sont aussi à zéro dans les tailles 0-2.
On vous priorise dès réception.

Cordialement,
"""),

dict(id="0925", d="2026-09-25", t="21:07", who="sophie", subj="Clôture GL 25/09", body="""
Bonsoir,

40,5k / 49,4k.
Merci Marco pour le retour. On a commencé une liste d'attente Aurea noire avec les numéros (13 noms ce soir).
4 demandes aujourd'hui (1 x2, 2, 3).
Retours : Aurea T3 chgt d'avis, Mistral 4 qualité (bouton pression), 2 tees.

Sophie
""", sig=None),

dict(id="0926", d="2026-09-26", t="22:08", who="karim", subj="CLOTURE SAMEDI 26/09", body="""
61,6k / 73,2k

AUREA NOIRE : 12 DEMANDES AUJOURD'HUI, DONT 7 EN TAILLE 1. On perd des ventes tous les jours.
+ 1 Amalia marron T1.
Vel marine x5, cardigan logo noir x4.
"""),

dict(id="0927", d="2026-09-27", t="20:52", who="karim", subj="cloture dim 27/09", body="""
62,9k / 49,2k (+28%)
Nova marine x4, Mistral noir x4, Aria noir x4. Pas mal de clients des Emirats.
Vel marine 5 a zero. 1 seule Aurea noire demandee aujourd'hui (enfin...).
retour Cosimo T5 qualite.
"""),

dict(id="0928", d="2026-09-28", t="21:05", who="sophie", subj="Clôture GL 28/09", body="""
Bonsoir à tous,

26,6k / 39,0k. Lundi très calme dans le grand magasin.
Aurea noire : 6 demandes (2 x2, 4 x2, 1, 3).

Bonne soirée,
"""),

dict(id="0929", d="2026-09-29", t="21:33", who="sophie", subj="Clôture GL 29/09", body="""
Bonsoir,

22,4k / 37,4k (-40%).
Début de la Fashion Week mais ça ne se ressent pas aux Galeries, c'est plutôt rue Saint-Honoré et dans le Marais.
Aurea noire : 9 demandes (dont 4 en 0).
2 Vel retournés pour la fermeture éclair défectueuse (tirette cassée), achetés en septembre.

Sophie
""", sig=None),

dict(id="0930", d="2026-09-30", t="22:11", who="karim", subj="cloture 30/09 golden week", body="""
41,5k / 42,3k
LES CHINOIS SONT ARRIVES : 49% des clients. Queue a la detaxe du grand magasin 45 min a 17h, des clients sont revenus au corner enerves.
Mistral noir x7 (plus de 5), 2 cagoules Astra.
Aurea noire : 15 demandes dont 10 en T1 !!
1 Vel zip.
"""),

dict(id="1001", d="2026-10-01", t="21:38", who="sophie", subj="Clôture GL 01/10", body="""
Bonsoir à tous,

60,1k / 46,8k (+29%).
Livraison 327 pcs reçue ce matin.
Iridia blanc cassé x4, Vtrack femme noir x3, Montgenèvre noir x3.
La détaxe des Galeries est saturée : plus d'1h d'attente au comptoir du rez-de-chaussée en fin de journée. Beaucoup de clients chinois hésitent à acheter à cause de ça. Est-ce qu'on peut voir avec la direction GL pour un comptoir détaxe dédié pendant la Golden Week ?
Aurea noire : 6 demandes. 2 Vel zip encore.

Sophie
""", sig=None),

dict(id="1002", d="2026-10-02", t="22:02", who="sophie", subj="Clôture GL 02/10 – journée de folie", body="""
Bonsoir à tous,

97,7k HT pour 56,2k de budget (+74%) !!

Les clientes chinoises ont pris la Aurea marine en masse : 16 vendues. Aria noir x7.
Plusieurs clientes asiatiques nous montrent la photo de Yoon Ha-eun (LUMIERE) prise hier à la Fashion Week en Iridia rose poudré. On n'a jamais eu le rose au corner, seulement le blanc cassé, on propose le blanc, ça marche à moitié.
Aurea noire : 5 demandes. Amalia marron 1. Tee blanc S.
3 Vel zip, ça commence à faire beaucoup.

Bonne nuit !
"""),

dict(id="1003", d="2026-10-03", t="22:34", who="karim", subj="cloture samedi 03/10", body="""
126,9k / 78,2k
573 entrees, le corner etait plein toute la journee, Lucie en coreen non stop.

AUREA NOIRE : on a arrete de compter, PLUS DE 40 DEMANDES aujourd'hui. Taille 1 surtout, puis 2 et 0.
7 VEL RETOURNES POUR LA FERMETURE. C'est quoi ce lot ??
tees blanc S x3, Aurea blanche 00.
retours aussi Aurea 3 + Cosimo 7 en taille.
"""),

dict(id="1004", d="2026-10-04", t="20:58", who="box", subj="Clôture dimanche 04/10", attach=[("csv", "cloture_PAR02_04102026.csv", [
    ["Champ", "Valeur"],
    ["Date", "04/10/2026"],
    ["CA TTC", "97 820"],
    ["Nb tickets", "39"],
    ["Entrees compteur GL", "424"],
    ["Meilleures ventes", "Vtrack Gtx noir x6, bonnet noir x5, torsade blanc x5, Cosimo noir x5"],
    ["Demandes non servies", "Aurea noire x9 (1 x5, 00, 0, 2), Aurea blanche 00, tee noir XL, Vtrack 45"],
    ["Liste d'attente Aurea noire", "31 noms"],
    ["Retours", "Artem T1 taille"],
    ["Rempli par", "Lucie"],
])], body="""
Bonsoir, fiche de clôture en PJ.
Lucie
"""),

dict(id="1005", d="2026-10-05", t="21:13", who="sophie", subj="Clôture GL 05/10", body="""
Bonsoir à tous,

56,4k / 43,2k (+31%).
Encore 34% de Chinois. Cardi matelassé noir, torsade noir, Rosière noir.
Aurea noire : 3 demandes. Mistral noir 7, Vtrack 39.
Cosimo noir 5 et jersey polo noir S à zéro.

Bonne soirée,
"""),

dict(id="1006", d="2026-10-06", t="21:29", who="sophie", subj="Clôture GL 06/10", body="""
Bonsoir,

63,0k / 42,1k (+50%).
Vtrack femme noir x7, cardi matelassé noir x5.
Aurea noire : 10 demandes (1 x5, 3 x2, 0, 2, 4). Liviana blanc 1.
Stock qui se vide : Vel marine 3, torsade noir S, jersey polo noir S, Cosimo noir 5.

Sophie
""", sig=None),

dict(id="1007", d="2026-10-07", t="21:55", who="karim", subj="cloture 07/10", body="""
47,9k / 46,2k
Le stock est a sec sur pas mal de refs : Vel marine 3 (2 clients), Aurea marine 00 et 1, Iridia blanc 0, Cosimo noir 3 et 5, cardi matelasse noir M...
Aurea noire 8 demandes.
4 retours (Aurea 2 taille, Liviana, Monteluce qualite, bonnet).
"""),

dict(id="1008", d="2026-10-08", t="21:24", who="sophie", subj="Clôture GL 08/10", body="""
Bonsoir à tous,

67,8k / 51,0k (+33%), dernier jour de Golden Week.
Énorme livraison (536 pcs) dont 14 cagoules Astra... on en vend 2-3 par semaine, je ne sais pas où les mettre. Toujours pas de Aurea noire.
Aurea noire : 3 demandes, Amalia marron 2.
Aurea marine x4, Iridia blanc x3.

Bonne soirée,
"""),

dict(id="1009", d="2026-10-09", t="21:08", who="sophie", subj="Clôture GL 09/10", body="""
Bonsoir,

42,4k / 62,6k. Fin de la Golden Week, retour au calme.
Aurea noire : 8 demandes (2 x4, 1 x2, 00, 3). Jersey Polo marine XL.

Sophie
""", sig=None),

# 10/10 pas de mail séparé -> récap sam + dim envoyé le dimanche

dict(id="1011", d="2026-10-11", t="21:03", who="karim", subj="cloture samedi + dimanche", body="""
Desole pas de mail hier, grosse journee + fermeture caisse longue.

SAMEDI 10/10 : 90,5k / 90,0k
Vtrack Gtx x8, Mistral noir x7, Aurea beige x6, casquettes x6
Aurea noire : 10 demandes

DIMANCHE 11/10 : 47,6k / 59,0k
cardigan logo noir x6, Vtrack x6, bonnets
Aurea noire : 6 demandes. Mistral marine 6, tee blanc XS.
2 Aurea retournees (taille + chgt avis).
"""),

dict(id="1012f", d="2026-10-12", t="17:46", who="sophie", suffix="_fwd", subj="TR: [GL Haussmann] Information mouvement social mardi 13 octobre",
     body="""
Pour info, note de la direction des Galeries pour demain. Karim et Lucie viennent en ligne 9, on va sûrement ouvrir en retard.
""", fwd="""
-------- Message d'origine --------
De : Direction Exploitation GL Haussmann <exploitation.haussmann@galerieslafayette.example>
Envoyé : lundi 12 octobre 2026 16:30
À : Liste Marques Coupole
Objet : [GL Haussmann] Information mouvement social mardi 13 octobre

Madame, Monsieur,

En raison du mouvement social annoncé dans les transports (RATP/SNCF) le mardi 13 octobre, le magasin ouvrira aux horaires habituels. Les marques sont invitées à adapter leur présence en fonction des possibilités de leurs équipes et à prévenir le PC sécurité de toute ouverture différée de leur stand.
Le service de navettes n'est pas assuré.

La Direction de l'Exploitation
"""),

dict(id="1012", d="2026-10-12", t="21:15", who="sophie", subj="Clôture GL 12/10", body="""
Bonsoir à tous,

46,7k / 44,4k (+5%).
Aurea beige x4, Montgenèvre noir x3. Encore quelques Coréennes.
Vtrack femme noir 40 demandé.

Bonne soirée,
"""),

dict(id="1013", d="2026-10-13", t="20:49", who="sophie", subj="Clôture GL 13/10 – grève", body="""
Bonsoir,

Grève : les Galeries quasi vides, 99 entrées sur la journée au corner. Beaucoup de collègues du grand magasin absentes.
Ouverture du corner à 10h45 au lieu de 10h (Karim bloqué ligne 9).
29,5k / 44,6k. Transfo à 19% quand même, les clientes présentes étaient là pour acheter.
Pas mal de Coréennes (19%) : 4 demandes Aurea noire en 0.
Retours : Aurea T1 taille, Vel zip, Artem T3 taille.

Sophie
""", sig=None),

dict(id="1014", d="2026-10-14", t="21:47", who="karim", subj="cloture 14/10", body="""
48,6k / 51,5k
Mistral noir x7 (le froid).
Aurea noire 6 demandes. Cardigan logo noir M a zero (1 client). Iridia blanc 00, Artem noir 6.
5 retours dont 1 Vel zip.
"""),

dict(id="1015", d="2026-10-15", t="21:36", who="sophie", subj="Clôture GL 15/10 – très grosse journée", body="""
Bonsoir à tous,

91,7k pour 51,3k de budget (+79%) !
Explication : une très grosse vente via le Personal Shopping des Galeries, une famille française (clients VIC du grand magasin) a pris 6 Aria noires + 2 Aurea blanches + des bonnets. Sans ça on était autour de 50k.
Livraison 457 pcs reçue, toujours pas de Aurea noire.
Aurea noire : 5 demandes (1 x3, 0, 4).

Bonne soirée,
"""),

# 16/10 : pas de mail

dict(id="1017", d="2026-10-17", t="22:12", who="karim", subj="cloture samedi 17/10", body="""
97,7k / 97,2k ok
Hier pas de mail desole (Sophie en rdv) : vendredi 54,3k / 64,5k, Mistral noir x8.

Aujourd'hui Aria blanc x8, Monteluce noir x5, Aria noir x5. Le froid fait vendre les doudounes.
Aurea noire 12 demandes, cardigan logo noir M encore.
7 retours dont Artem T5 (trop grand, il a pris le 4).
"""),

dict(id="1018", d="2026-10-18", t="20:46", who="box", subj="Fiche de clôture 18/10", body=form(
    "18/10/2026", 62256, 25, 242,
    "Cardigan logo noir M : 2 demandes, a zero depuis le 14. Aurea noire : 2 demandes, liste d'attente 34 noms.",
    "Vtrack femme noir x5, Cosimo marine x4, Aurea beige x4", "Cardigan logo noir M x2, Aurea noire 0 et 1",
    "bonnet (taille), Artem T3 echange taille", "Lucie")),

dict(id="1019", d="2026-10-19", t="21:20", who="sophie", subj="Clôture GL 19/10", cc=CC_MERCH, body="""
Bonsoir à tous,

53,0k / 48,6k.
Rosière noir x4.
Aurea noire : d'après le merch le dépôt est réapprovisionné depuis vendredi, quand est-ce qu'on est livrés ? 34 clientes en liste d'attente, on aimerait les rappeler avec une date.
Amalia marron 2 demandé. 1 Vel zip.

Sophie
""", sig=None),

dict(id="1020", d="2026-10-20", t="21:04", who="sophie", subj="Clôture GL 20/10", body="""
Bonsoir,

44,0k / 49,0k. Clientèle saoudienne et chinoise.
Cardi matelassé noir x4. Iridia blanc 2 demandé.

Bonne soirée,
"""),

dict(id="1021", d="2026-10-21", t="21:51", who="karim", subj="cloture 21/10", body="""
41,1k / 54,4k
Les japonais sont de retour (15%).
Vtrack Gtx noir x7, Mistral noir x5.
1 Aurea noire T1. Retour Liviana 00 taille + 1 Vel zip.
"""),
]
