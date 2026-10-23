# -*- coding: utf-8 -*-
from common import person

LANG = "it"
F = "EMEA_Galli_Italia_Spagna"
TZ = "Europe/Rome"
R = person("galli")
TO = [person("valli")]
CC = [person("ruggeri")]

MSGS = [
dict(key="g36", folder=F, file="2026-09-07_0852_recap_W36_Galli", frm=R, to=TO, cc=None, tz=TZ, sent="2026-09-07 08:52",
     subj="recap sett 36 (veloce)",
     body="""Ciao Francesca,
rientrato stamattina, la settimana scorsa ero in ferie fino a venerdi quindi recap veloce sui numeri che mi hanno girato i negozi, i commenti li approfondisco questa settimana.

MIL01 330k, in linea col budget
MIL02 120k, -5
ROM01 157k, -13
VEN01 85k, -37 (!!) nonostante la Mostra, Chiara dice pochissimi americani
COU01 47k, -33, ultima settimana piena prima della chiusura del 13
CRT01 48k, -20
MAD01 75k, -35, Madrid ancora vuota, rientro dalle vacanze lento

Totale area sotto budget di circa 15%. Jersey Polo e t-shirt ancora in testa nelle vendite, i piumini iniziano solo a Milano.

R.
"""),

dict(key="g37", folder=F, file="2026-09-13_2140_recap_W37_Galli", frm=R, to=TO, cc=CC, tz=TZ, sent="2026-09-13 21:40",
     subj="Recap W37 Italia + Spagna",
     body="""Ciao Fra,

numeri settimana (netto, k€, vs budget)
MIL01 340 / -14
MIL02 132 / -6
ROM01 192 / -9
VEN01 164 / +4
COU01 27 / -54
CRT01 61 / +3
MAD01 134 / 0

Note:
- novita FW26 in negozio da giovedi 3. Amalia piace molto ma quasi tutti chiedono il marrone cioccolato, il nero meno. A Milano e Madrid sul marrone ci sono gia buchi di taglia (1 e 2). Da tenere d'occhio.
- Artem: primi cambi taglia a MIL01, il team dice che veste abbondante. Pochi casi per ora.
- MIL01 sotto per colpa della settimana di mezzo, Giulia dice traffico buono ma tanti "giro e torno". Settimana prossima arrivano le sfilate.
- COU01 chiude oggi per fine stagione, riapre 27/11. Inventario fatto da Paolo ok, merce in reso a CSG martedi.
- MAD01 finalmente si muove, bene Vel e felpe.

Domani sono a Venezia.
R.
"""),

dict(key="g38", folder=F, file="2026-09-21_0815_recap_W38_Galli", frm=R, to=TO, cc=CC, tz=TZ, sent="2026-09-21 08:15",
     subj="Recap sett. 38",
     body="""Buongiorno Francesca,

MIL01 422 (-2%)
MIL02 135 (-15%)
ROM01 128 (-45%)
VEN01 183 (+9%)
CRT01 40 (-24%)
MAD01 134 (-10%)

ROM01: settimana pessima. Secondo Alessandra un mix di pochi americani (le crociere stanno finendo), ancora 30 gradi a Roma, e da lunedi hanno aperto un cantiere sul marciapiede davanti all'ingresso. Non credo che il cantiere da solo spieghi un -45, ci vado giovedi e vi dico.

MIL01: finita la Aurea nera, ultime taglie andate venerdi/sabato. La chiedono soprattutto ragazze coreane, alcune con la foto sul telefono. Abbiamo beige e blu, proviamo a spostarle su quelle.
VEN01 bene, tanta gente in giro per la Biennale e qualche gruppo cinese.
MAD01 ok, nulla da segnalare.

Settimana prossima fashion week, MIL01 ha chiesto 2 persone in piu di rinforzo da MIL02 nel weekend, ok per me se Stefano riesce a coprire.

Roberto
"""),

dict(key="g39", folder=F, file="2026-09-27_2205_recap_W39_Galli", frm=R, to=TO, cc=CC, tz=TZ, sent="2026-09-27 22:05",
     subj="Recap W39 + visita Roma",
     body="""Ciao Fra,
settimana sfilate, Milano bene.

MIL01 524k +7%
MIL02 195k +12%
ROM01 152k -44%
VEN01 166k -14%
CRT01 42k -27%
MAD01 141k -15%

ROMA. Sono stato giovedi. Il problema e' piu grosso di quanto pensassi: ponteggio su tutta la facciata + recinzione del Comune sul marciapiede, le vetrine laterali non si vedono, l'ingresso e' un corridoio tra le transenne. Il Comune parla di fine lavori a fine ottobre. Ho chiesto a facility un totem all'angolo con Bocca di Leone e a Sofia se possiamo brandizzare la recinzione. Report visita in allegato al prossimo giro, intanto vi giro le foto via whatsapp.

MILANO. Settimana moda ok, molta stampa e buyer in negozio, Astra lanciato giovedi: tanta curiosita poche vendite (2 pezzi a MIL01 in 4 giorni), la gente prova l'oversize e lo trova piccolo. Prezzo alto per il cliente italiano.
Sulla Aurea nera: Giulia mi dice che le richieste continuano. Secondo me il tema Aurea nera e' un po' sovrastimato, sono tante turiste coreane che girano tutti i negozi di via Montenapoleone e chiedono la stessa cosa ovunque, meta' non comprerebbe comunque. Non farei allocazioni straordinarie.

MADRID. Ieri e' arrivata una consegna con Nova BLU al posto della nera (errore di picking a CSG?). Lucia ha aperto ticket. La nera e' praticamente finita.

VENEZIA calo fisiologico dopo un buon inizio mese.
CRT01 dal 1 ottobre apre solo ven-sab-dom come da accordi.

Ciao
R.
"""),

dict(key="g39_fv", folder=F, file="2026-09-28_0931_RE_recap_W39_Valli", frm=person("valli"), to=[R], cc=None, tz=TZ, sent="2026-09-28 09:31",
     subj="R: Recap W39 + visita Roma", reply_to="g39",
     body="""Roberto, sulla Aurea nera non sono tanto d'accordo. Isabelle mi segnala lo stesso a Parigi e Fiona da Harrods, sono troppi segnali insieme.
Mi mandi quante richieste ha registrato MIL01 nella settimana?
Grazie per Roma, aspetto il report.
F.
"""),

dict(key="g39_rg", folder=F, file="2026-09-28_1248_RE_recap_W39_Galli", frm=R, to=[person("valli")], cc=None, tz=TZ, sent="2026-09-28 12:48",
     subj="R: R: Recap W39 + visita Roma", reply_to="g39_fv",
     body="""Giulia dice una ventina nella settimana, ma tante sono le stesse persone che tornano o chiamano. Ti giro il file appena me lo manda.
Comunque CSG dice niente nero prima del 16/10, quindi poco da fare.

Inviato da iPhone
"""),

dict(key="g40", folder=F, file="2026-10-05_0840_recap_W40_Galli", frm=R, to=TO, cc=CC, tz=TZ, sent="2026-10-05 08:40",
     subj="Recap W40 - Golden Week",
     body="""Ciao Francesca,

settimana forte grazie ai cinesi.

MIL01 653 +21
MIL02 246 +32
ROM01 176 -42
VEN01 260 +19
CRT01 42 -22 (aperto solo ven-dom)
MAD01 173 -6

MIL01/MIL02/VEN01: tantissimi gruppi cinesi da mercoledi, su MIL01 circa un terzo degli scontrini. I due ragazzi madrelingua mandati da Matteo sono stati fondamentali. Tax free in coda tutti i pomeriggi.

VEL: problema serio con la zip, il cursore si stacca. A MIL01 16 resi in una settimana, a MIL02 e VEN01 qualcuno. Nessuna comunicazione da Qualita, ogni negozio lo registra a modo suo. Chi lo segue?

MAD01: questione Nova nera risolta, CSG ha confermato la sostituzione. Attenzione che il contapersone di Madrid segna zero da giovedi, quindi la conversione di questa settimana non e' attendibile (ticket aperto).

ROM01 sempre giu, cantiere invariato.

Roberto
"""),

dict(key="g41", folder=F, file="2026-10-11_2115_recap_W41_Galli", frm=R, to=TO, cc=CC, tz=TZ, sent="2026-10-11 21:15",
     subj="recap W41",
     body="""Fra ciao,
MIL01 675k (+17)
MIL02 221k (+7)
ROM01 207k (-36)
VEN01 213k (-5)
CRT01 24k, 3 giorni
MAD01 176k (-14)

- MIL01: Aurea nera sempre la richiesta n.1, gli ultimi giorni della Golden Week la chiedevano anche i cinesi. Ok, ammetto che i numeri sono alti.
- Vlogo Cardigan taglia M finito a Monte Napo da martedi, nero e blu. CSG non ne ha fino a fine mese. ROM01 ha ancora qualche M blu, ho chiesto il trasferimento a Luca.
- Arrivate sabato 12 Iridia rosa a MIL01. Non so chi le abbia chieste, a Milano il rosa non lo chiede nessuno da quando e' passata la Golden Week. Le teniamo in vetrina.
- MAD01: Nova nera finalmente arrivata sabato, in tutte le taglie.
- Resi Vel: ricevuto lunedi sera l'alert di Elena, adesso tutti usano DEF.
- ROM01 leggermente meglio grazie ai clienti richiamati al telefono, ma sempre -36.

Venerdi 16 sciopero generale, ATM e ATAC a rischio. I negozi si organizzano con i turni.

R.
"""),

dict(key="g42", folder=F, file="2026-10-20_0910_recap_W42_Galli", frm=R, to=TO, cc=CC, tz=TZ, sent="2026-10-20 09:10",
     subj="Recap W42 Italia/Spagna + acqua alta VEN",
     body="""Buongiorno,
scusate il ritardo, ieri giornata in sede.

MIL01 589 -6%
MIL02 193 -13%
ROM01 165 -52%
VEN01 184 -24%
CRT01 31 (ven-dom)
MAD01 185 -13%

- Venerdi sciopero: mezza giornata persa su Milano e Roma, metro ferma dalle 9. Alcuni del team arrivati alle 11.
- Un po' di freddo da martedi, si sono mossi Nova e Liviana. Niente di paragonabile alla Germania.
- MIL01 Aurea nera: ancora 30 richieste registrate nella settimana. CSG ha ricevuto il 16, Luca mi dice prima tranche a MIL01 e ROM01 a inizio settimana. Ho chiesto io di dare un po' di nero anche a Roma, con il cantiere serve qualcosa di forte per i clienti che chiamiamo.
- MIL02 finito anche li il cardigan M nero (sabato). Trasferimento ROM01 -> MIL01 approvato ma non ancora partito, sollecito.
- Iridia rosa a MIL01: venduti 2-3 pezzi in una settimana su 13. Se servono in Asia io le mando.
- MAD01 tranquilla, Amalia marrone sempre richiesto in 1 e 2.

VEN01: stamattina acqua alta 118, San Marco allagata, Chiara apre alle 12. Vi aggiorno stasera.

R.
"""),
]
