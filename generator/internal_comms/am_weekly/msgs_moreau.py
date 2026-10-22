# -*- coding: utf-8 -*-
from common import person

LANG = "fr"
F = "EMEA_Moreau_France_Geneve"
TZ = "Europe/Paris"
I = person("moreau")
TO = [person("valli")]
CC = [person("dubois")]

W39_HTML = """<html><body style="font-family:Calibri,sans-serif;font-size:11pt">
<p>Bonsoir Francesca,</p>
<p>Voici le bilan de la semaine 39 (du 21 au 27/09).</p>
<table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse;font-size:10pt">
<tr style="background:#dde4ee"><th>Boutique</th><th>CA net</th><th>vs budget</th><th>Commentaire</th></tr>
<tr><td>PAR01 St-Honoré</td><td>334 k€</td><td>-11 %</td><td>Maire noire en rupture</td></tr>
<tr><td>PAR02 Galeries Lafayette</td><td>303 k€</td><td>-7 %</td><td>idem, très forte demande coréenne</td></tr>
<tr><td>CAN01 Cannes</td><td>78 k€</td><td>0 %</td><td>bonne surprise, clientèle chinoise</td></tr>
<tr><td>GVA01 Genève</td><td>CHF 94 k</td><td>-12 %</td><td>&nbsp;</td></tr>
</table>
<p>(le texte complet est en dessous, désolée pour la mise en forme, Outlook sur iPad...)</p>
</body></html>"""

MSGS = [
dict(key="m36", folder=F, file="2026-09-07_0805_bilan_S36_Moreau", frm=I, to=TO, cc=CC, tz=TZ, sent="2026-09-07 08:05",
     subj="Bilan semaine 36 – France / Genève",
     body="""Bonjour Francesca,

Rentrée assez calme sur l'ensemble du périmètre, comme prévu.

PAR01 : 251 k€, -6 % vs budget. Clientèle locale qui revient doucement, touristes américains encore présents.
PAR02 : 200 k€, -13 %. Galeries très calmes en semaine, le samedi a sauvé la semaine.
CAN01 : 30 k€, -41 %. Fin de saison sur la Croisette (les yachts sont partis), rien d'anormal.
GVA01 : CHF 54 k, -26 %. Nathalie signale que les clients du Moyen-Orient sont partis plus tôt cette année.

Un retard de livraison à PAR01 (arrivée le 2 au lieu du 30/08), sans conséquence.

Je passe à Genève jeudi.

Bien à toi,
Isabelle
"""),

dict(key="m37", folder=F, file="2026-09-13_2030_bilan_S37_Moreau", frm=I, to=TO, cc=CC, tz=TZ, sent="2026-09-13 20:30",
     subj="Bilan S37 France & Genève",
     body="""Bonsoir Francesca,

Semaine 37 :
- PAR01 257 k€ (-16 %)
- PAR02 255 k€ (-8 %)
- CAN01 44 k€ (-31 %)
- GVA01 CHF 58 k (-32 %)

Les nouveautés sont bien installées. L'Ambrine marron fait un vrai effet en boutique (on l'a mise en vitrine à St-Honoré, plusieurs clientes sont entrées pour elle), par contre les tailles 1 et 2 partent très vite et on n'a pas de profondeur. Je trouve dommage que l'allocation soit si déséquilibrée vers le noir (je l'avais dit au moment des achats d'ailleurs).
L'Ilvaro plaît aux plus jeunes, surtout en noir. Le rose, on n'en a qu'une pièce par boutique, personne n'en parle.

Genève : visite jeudi, boutique impeccable, mais trafic faible. Nathalie voudrait organiser un petit événement clientes fin octobre, je t'en reparle.

Bien à toi,
Isabelle
"""),

dict(key="m38", folder=F, file="2026-09-21_0750_bilan_S38_Moreau", frm=I, to=TO, cc=CC, tz=TZ, sent="2026-09-21 07:50",
     subj="Bilan S38",
     body="""Bonjour Francesca,

PAR01 298 k€ -13 %
PAR02 280 k€ -7 %
CAN01 47 k€ -31 %
GVA01 CHF 67 k -28 %

Point important : depuis vendredi/samedi, beaucoup de clientes coréennes (souvent jeunes, en petits groupes) aux Galeries et à St-Honoré qui demandent toutes la Maire noire, photo sur le téléphone. D'après Sophie c'est lié à une série télé coréenne. A PAR02 on est déjà à zéro sur le noir, à PAR01 il reste quelques pièces dans les petites tailles. Il faudrait voir avec Chiara s'il reste du stock au dépôt (je crains que non).

Le reste est sans surprise. Septembre reste en dessous du budget mais la tendance s'améliore semaine après semaine.

Isabelle
"""),

dict(key="m39", folder=F, file="2026-09-27_2110_bilan_S39_Moreau", frm=I, to=TO, cc=CC, tz=TZ, sent="2026-09-27 21:10",
     subj="Bilan semaine 39 – France / Genève (tableau)", html=W39_HTML,
     body="""Bonsoir Francesca,

Voici le bilan de la semaine 39 (du 21 au 27/09).

PAR01 334 k€ (-11 %) / PAR02 303 k€ (-7 %) / CAN01 78 k€ (0 %) / GVA01 CHF 94 k (-12 %)

1) Maire noire : rupture totale sur les deux boutiques parisiennes (PAR01 depuis cette semaine). Les équipes ont compté une vingtaine de demandes à St-Honoré et plus de 30 aux Galeries, presque uniquement des clientes coréennes (nombreuses depuis la fin de leur fête nationale, si j'ai bien compris). Le dépôt n'a rien avant mi-octobre.
En attendant, j'ai demandé aux équipes de proposer systématiquement la Maire beige et la marine : c'est la même coupe, et la beige est vraiment très jolie portée. Je pense qu'on peut récupérer une bonne partie des ventes si les conseillères y croient.

2) Ambrine marron : toujours les petites tailles manquantes.

3) Cannes : très bonne surprise, des groupes chinois en avance sur les vacances d'octobre, à budget.

4) Polaris lancé jeudi à St-Honoré et Cannes : accueil poli. La cape est très belle en vitrine, mais les clients trouvent le blouson petit et cher. Une seule vente à ce jour.

5) Fashion Week à partir de mardi : renfort prévu à PAR01 (2 personnes des Galeries le jeudi et le vendredi).

(désolée pour la mise en forme, Outlook sur iPad...)

Bien à toi,
Isabelle
"""),

dict(key="m40", folder=F, file="2026-10-05_0830_bilan_S40_Moreau", frm=I, to=TO, cc=CC, tz=TZ, sent="2026-10-05 08:30",
     subj="Bilan S40 – très belle semaine",
     body="""Bonjour Francesca,

Très belle semaine sur Paris :

PAR01 : 622 k€, +41 % vs budget (!)
PAR02 : 457 k€, +28 %
CAN01 : 57 k€, -35 %
GVA01 : CHF 86 k, -26 %

St-Honoré a fait sa meilleure semaine depuis l'ouverture de la saison, portée par la Fashion Week : beaucoup de clients internationaux, de la presse, des invités des défilés qui passent entre deux shows, plusieurs grosses factures. Il y avait aussi les vacances chinoises, mais pour moi c'est vraiment l'effet défilés qui a fait la différence à St-Honoré.
Aux Galeries, clientèle chinoise très présente (Sophie estime 30 %).

Maire noire : la liste d'attente aux Galeries a explosé, Karim me parle de presque 100 demandes sur la semaine. Je demande formellement que PAR01 et PAR02 soient servis en priorité sur l'arrivage du 16 octobre.

TIB : nous avons des retours pour fermeture éclair défectueuse depuis lundi dernier, une quinzaine aux Galeries et autant à St-Honoré. Aucune consigne reçue de la qualité, les boutiques stockent les pièces en réserve. Est-ce que quelqu'un peut nous dire quoi faire ?

Genève et Cannes calmes, rien de particulier.

Bien à toi,
Isabelle
"""),

dict(key="m41", folder=F, file="2026-10-11_2200_bilan_S41_Moreau", frm=I, to=TO, cc=CC, tz=TZ, sent="2026-10-11 22:00",
     subj="Bilan S41",
     body="""Bonsoir Francesca,

PAR01 553 k€ (+18 %)
PAR02 415 k€ (+5 %)
CAN01 60 k€ (-35 %)
GVA01 CHF 117 k (-7 %)

- Fin de la Fashion Week et des vacances chinoises jeudi, la fréquentation redescend mais reste bonne.
- Maire noire : toujours la première demande, une cinquantaine à St-Honoré, autant aux Galeries. Les ventes de beige restent modestes, honnêtement.
- Ambrine marron : 8 demandes à PAR01 sur des tailles absentes.
- Nous avons reçu samedi à St-Honoré 12 Ilvaro rose poudré, sans l'avoir demandé. Je ne vois pas trop qui va les acheter ici, les clientes asiatiques qui le cherchaient début octobre sont reparties. Si ça peut servir ailleurs...
- TIB : merci pour l'alerte qualité, procédure appliquée.
- Mardi grève RATP annoncée, Camille réorganise les horaires.

Bien à toi,
Isabelle
"""),

dict(key="m41_fv", folder=F, file="2026-10-12_0904_RE_bilan_S41_Valli", frm=person("valli"), to=[I], cc=None, tz=TZ, sent="2026-10-12 09:04",
     subj="RE: Bilan S41", reply_to="m41",
     body="""Merci Isabelle. Sulla Maire beige come alternativa: hai qualche numero? Quante vendute alle clienti che chiedevano la nera?
F.
"""),

dict(key="m41_im", folder=F, file="2026-10-12_1127_RE_bilan_S41_Moreau", frm=I, to=[person("valli")], cc=None, tz=TZ, sent="2026-10-12 11:27",
     subj="RE: RE: Bilan S41", reply_to="m41_fv",
     body="""Pas de chiffres précis, les équipes ne notent pas la demande d'origine sur le ticket. D'après Camille, peut-être 3 ou 4 beiges vendues à des clientes qui voulaient la noire sur deux semaines. Je reconnais que c'est peu par rapport à la liste.
Isabelle
"""),

dict(key="m42", folder=F, file="2026-10-19_0820_bilan_S42_Moreau", frm=I, to=TO, cc=CC, tz=TZ, sent="2026-10-19 08:20",
     subj="Bilan semaine 42 – grève + froid",
     body="""Bonjour Francesca,

PAR01 : 359 k€, -28 %
PAR02 : 420 k€, à budget
CAN01 : 61 k€, -40 %
GVA01 : CHF 169 k, +26 %

Mardi la grève a vraiment fait mal à St-Honoré (journée à -40 % environ, deux vendeuses arrivées à midi). Le reste de la semaine PAR01 a souffert de l'absence de Maire noire, toujours une vingtaine de demandes. Aux Galeries c'est encore pire, 38 demandes notées.
Genève : le froid est arrivé (neige sur le Salève jeudi), très bonnes ventes de doudounes et de bonnets, +26 %.
Cannes reste faible, on est en basse saison.

J'ai vu que le dépôt a reçu les Maire noires vendredi. J'espère sincèrement que Paris sera servi en premier cette fois, après trois semaines de clientes perdues.

Bien à toi,
Isabelle
"""),
]
