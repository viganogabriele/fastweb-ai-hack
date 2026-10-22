# MIL02 Milano Rinascente Duomo - hand-authored closing emails (shop-in-shop inside la Rinascente)
# Writers: Stefano Rocchi (SM), Ilaria Mancuso (AM), Matteo Brambilla (SA, from the shared store iPad mailbox)

PERSONAS = {
    "stefano": "Stefano Rocchi <stefano.rocchi@moncler-retail.example>",
    "ilaria": "Ilaria Mancuso <ilaria.mancuso@moncler-retail.example>",
    "store": "Moncler Rinascente Duomo <mil02.store@moncler-retail.example>",
    "roberto": "Roberto Galli <roberto.galli@moncler-retail.example>",
    "giulia": "Giulia Ferrandi <giulia.ferrandi@moncler-retail.example>",
    "rops": "retail-ops-italy@moncler-retail.example",
    "merch": "merch-planning@moncler-retail.example",
    "vm": "vm-team@moncler-retail.example",
    "dc": "dc-replenishment@moncler-retail.example",
    "facility": "facility-italy@moncler-retail.example",
    "mil01": "mil01.store@moncler-retail.example",
}

DEFAULT_TO = ["rops"]
DEFAULT_CC = ["roberto"]

SIG_S = """--
Stefano Rocchi
Store Manager | Moncler c/o la Rinascente Milano Duomo
Riservato: se non siete i destinatari cancellate questa mail."""

EMAILS = [
    # ---------------------------------------------------------------- week 1
    dict(id="c0831", sent="2026-08-31 21:52", frm="stefano", business_date="2026-08-31",
         subject="MIL02 Rinascente - chiusura 31/08",
         body="""Buonasera,

INCASSO: 9.430
BDG: 13,0 (-27%)
INGRESSI (feed Rina): 54
SCONTRINI: 6
NOTE: ultimo lunedi di agosto e si vede, il piano e' stato un deserto fino alle 5. Nel pomeriggio un paio di famiglie saudite e qualche cinese, 2 Maya nere. Montgenevre nero tg 5 finito.
Rinascente ha transennato il corridoio lato scale mobili per rifare il pavimento (fino a mercoledi dicono) quindi chi sale gira dal lato Herno e davanti a noi non passa nessuno. Nessuno ci aveva avvisato, l'ho scoperto stamattina alle 9:50.

""" + SIG_S),

    dict(id="ooo0831", sent="2026-08-31 21:52", frm="roberto", kind="ooo",
         to=["stefano"], cc=[], reply_to_id="c0831",
         subject="Risposta automatica: MIL02 Rinascente - chiusura 31/08",
         headers={"Auto-Submitted": "auto-replied"},
         body="""Sono fuori ufficio con accesso limitato alla posta fino a venerdì 4 settembre. Per urgenze contattare retail-ops-italy@moncler-retail.example.

I am out of office until Friday 4 September with limited access to email. For urgent matters please contact retail-ops-italy@moncler-retail.example.

Roberto Galli"""),

    dict(id="c0901", sent="2026-09-01 21:38", frm="ilaria", business_date="2026-09-01",
         subject="Chiusura Rinascente 1/9",
         body="""Ciao a tutti!
giornata mortissima 😴
5k su 12 di budget...
55 ingressi ma 90% giro turistico
vendute 2 t-shirt logo bianche e 2 cardigan tricot neri, il resto niente
1 reso t-shirt L (ha cambiato idea)
corridoio ancora chiuso 🚧
domani andra meglio 🙏
Ila"""),

    dict(id="c0902", sent="2026-09-02 22:05", frm="stefano", business_date="2026-09-02",
         subject="MIL02 Rinascente - chiusura 02/09",
         body="""Ciao,

INCASSO: 10,9k
BDG: 13,7
INGRESSI: 46 (si, 46)
SCONTRINI: 13
NOTE: arrivata la consegna da CSG, 131 pz, sistemata in back-office che come sapete sono 12 mq divisi con il corner accanto. Mezza consegna e' ancora negli scatoloni sotto il bancone. Pochi ingressi ma chi entrava comprava, t-shirt e cardigan tricot, 2 Trailgrip GTX nere.
Il pavimento davanti e' finito, da domani dovremmo tornare visibili.

""" + SIG_S),

    dict(id="c0903", sent="2026-09-03 21:44", frm="store", business_date="2026-09-03",
         subject="chiusura rinascente 03/09",
         body="""ciao, chiudo io stasera (Stefano in riunione con la direzione Rina)
17,3k, budget preso giusto giusto
2 cardigan logo blu, 2 dolcevita neri, Maya e Hermine nere
1 reso Trailgrip donna 38 per qualita, la cliente dice che si scolla sul tallone, l'ho messa da parte x la foto
buona serata
Matteo

Inviato da iPad"""),

    dict(id="c0904", sent="2026-09-04 22:47", frm="stefano", business_date="2026-09-04",
         subject="MIL02 Rinascente - chiusura 04/09",
         body="""Buonasera,
venerdi finalmente con un po' di vita: 23,8k vs 20,7 di budget, 116 ingressi.
Vendute le prime 2 Ilvaro panna, piace molto la forma corta. Bene anche marsupio Legere e polo blu.
Si vede che i milanesi sono rientrati, il piano era pieno dalle 18 in poi.

Riunione di ieri con Rinascente: vogliono che da ottobre anche noi partecipiamo agli eventi Rinascente Card. Ho detto che non decido io. Ne parliamo lunedi Roberto?

Stefano"""),

    dict(id="c0905", sent="2026-09-05 23:02", frm="ilaria", business_date="2026-09-05",
         subject="Chiusura Rinascente 5/9 🔥",
         body="""SABATO TOP 🔥🔥
35,9k (+21%)
141 ingressi, 24 scontrini
4 Bady nere + 4 cardigan logo neri!!
richieste che nn avevamo:
- Ilvaro nero tg 3 (2 clienti diverse 😩)
- Maire nera 4
- dolcevita marrone XS
pausa pranzo saltata xke Rina ci ha messo i turni pausa tutti alle 13 insieme a quelli di Woolrich 🙄
notte 🌙
Ila"""),

    dict(id="c0906", sent="2026-09-06 21:33", frm="ilaria", business_date="2026-09-06",
         subject="Chiusura Rinascente 6/9",
         body="""domenica tranquilla, 17,7
tanti americani e un gruppetto di coreani
reso 1 Maire tg 1 (cambio idea)
Trailgrip donna nera 37 finita, una cliente la voleva 🤷‍♀️
ciao ❤️"""),

    dict(id="c0907", sent="2026-09-07 21:59", frm="stefano", business_date="2026-09-07",
         subject="MIL02 Rinascente - chiusura 07/09",
         body="""Bentornato Roberto.

INCASSO: 18.990
BDG: 15,8 (+20%)
INGRESSI (feed Rina): 65
SCONTRINI: 13
NOTE: lunedi meglio del previsto. 2 Maire nere, 2 Hermine blu, 2 Montgenevre neri. La Hermine blu tg 0 e' finita, il Montgenevre nero ora manca anche in 4.
Coreani e cinesi in aumento da sabato, chiedono tutti il tax free e il desk Rinascente al -1 alle 18 aveva 40 minuti di coda. Due clienti hanno lasciato il capo alla cassa e sono andati a fare la pratica prima, uno non e' tornato.

""" + SIG_S),

    # 09-08 deliberately missing
    dict(id="c0909", sent="2026-09-09 22:20", frm="stefano", business_date="2026-09-09",
         subject="MIL02 Rinascente - chiusura 09/09",
         body="""Ciao a tutti,
ieri sera non ho mandato niente, scusate, la chiusura cassa Rina si e' bloccata e sono uscito alle 22 passate.

INCASSO: 26,2k
BDG: 16,8 (+55%)
INGRESSI: 71
SCONTRINI: 15
NOTE: giornata fortunata, tanti americani (crociera?) e qualche giapponese. 2 Maya verde oliva, 2 Rosiere nere, beanie e t-shirt.
Consegna CSG arrivata, 173 pz, tutto ok.
Un signore ha chiesto il Montgenevre blu in 7, non c'e'.
1 reso Trailgrip donna 36, cambio idea.

Stefano"""),

    dict(id="r0909", sent="2026-09-09 23:31", frm="roberto", kind="reply", reply_to_id="c0909",
         to=["stefano"], cc=["rops"], business_date="",
         subject="Re: MIL02 Rinascente - chiusura 09/09",
         body="""Bene oggi. Ma 71 ingressi con +55%? Qualcosa non torna sulla conversion, la settimana scorsa avevate 46.
Mi mandi traffico Rinascente ultima settimana vs il vostro?
R.

Inviato da iPhone"""),

    dict(id="s0910", sent="2026-09-10 10:42", frm="stefano", kind="reply", reply_to_id="r0909",
         to=["roberto"], cc=["rops"],
         subject="Re: Re: MIL02 Rinascente - chiusura 09/09",
         body="""Roberto,
ho chiesto stamattina alla capo piano. Il dato totale palazzo ce lo danno solo a voce, quello del piano no ("e' un dato riservato della direzione").
A voce: lunedi circa 18 mila ingressi Rinascente, martedi 17-18, ieri sopra i 19.
Il nostro conta persone non e' nostro: e' il sensore Rinascente sul varco lato scale mobili, ci arriva come feed il giorno dopo. Chi entra dal lato del corner Herno non viene contato, e da quando hanno fatto i lavori al pavimento la gente gira di li'. Secondo me perdiamo un 30% di ingressi nel conteggio.
Quindi conversion vera piu bassa di quello che vedi: martedi era 6%, ieri 21% ma con il sensore che conta la meta' non vuol dire niente.
Ho chiesto se possono mettere un secondo sensore, risposta: serve approvazione direzione + offerta del fornitore. Tempi biblici come sempre.

Stefano

""" + SIG_S),

    dict(id="c0910", sent="2026-09-10 21:41", frm="ilaria", business_date="2026-09-10",
         subject="Chiusura Rinascente 10/9",
         body="""ciao!
19,1k ✅ (budget 18,5)
prima cliente che chiede l'Ambrine marrone 🤎 l'aveva vista su IG, il cappotto lungo con la cintura
noi qui non ce l'abbiamo proprio in assortimento... l'ho mandata in via Monte
1 reso Maire tg 1 x taglia
Ila"""),

    dict(id="fwd0911", sent="2026-09-11 14:36", frm="stefano", kind="fwd",
         to=["rops"], cc=["roberto", "facility"],
         subject="I: Comunicazione Rinascente - prova evacuazione 15/09 e orari Fashion Week",
         body="""Vi giro la comunicazione arrivata stamattina dalla capo piano.
Due cose: martedi prova di evacuazione prima dell'apertura (dobbiamo essere tutti dentro alle 9:00), e durante la fashion week Rina allunga fino alle 22 anche il giovedi. Sono 3 ore extra di copertura che con 5 persone non ho. Chi le paga? Roberto sentiamoci.

Stefano

-------- Messaggio inoltrato --------
Da: Francesca Liverani <francesca.liverani@rinascente.example>
Data: 11 settembre 2026 09:12
A: concessioni2piano@rinascente.example
Oggetto: Comunicazione Rinascente - prova evacuazione 15/09 e orari Fashion Week

Gentili partner,
si comunica che martedì 15 settembre alle ore 9:15 si svolgerà la prova di evacuazione semestrale dell'edificio di Piazza Duomo. La presenza di tutto il personale dei corner è obbligatoria dalle ore 9:00. L'apertura al pubblico resta confermata alle ore 10:00.

In occasione della Milano Fashion Week (22-28 settembre) l'orario di apertura sarà esteso fino alle ore 22:00 da giovedì a sabato. Il 24 settembre è previsto un evento su invito sulla Terrazza al 7° piano: eventuali attività dei corner andranno concordate con il Visual Rinascente entro il 16/09.

Si ricorda che le pause del personale vanno registrate sul tablet all'ingresso di servizio.

Cordiali saluti
Francesca Liverani
Floor Manager 2° piano
la Rinascente Milano Duomo"""),

    dict(id="c0911", sent="2026-09-11 22:51", frm="stefano", business_date="2026-09-11",
         subject="MIL02 Rinascente - chiusura 11/09",
         body="""Ciao,
19,2k, sotto budget di un 10%. Cinesi, giapponesi e tedeschi, pochi italiani stasera.
Finiti Tib panna in 4 e t-shirt logo blu M.
2 resi: cable knit S (dice che fa i pallini dopo un lavaggio... a mano) e una t-shirt XL.
Stefano"""),

    dict(id="c0912", sent="2026-09-12 23:10", frm="ilaria", business_date="2026-09-12",
         subject="Chiusura Rinascente 12/9 ✨",
         body="""sabato ok ma nn esaltante
29,6k (-6%)
132 ingressi
3 Maya blu 💙 e tante t-shirt
mi hanno chiesto Hermine bianca/panna tg 0 e t-shirt blu M, finite entrambe
Rina stasera ha fatto la serata per la card al rooftop e alle 21 il piano si e' svuotato di colpo, tutti su a bere 🥂🙄
Ila"""),

    dict(id="c0913", sent="2026-09-13 21:28", frm="store", business_date="2026-09-13",
         subject="chiusura rinascente 13/9",
         body="""domenica fiacca, 12k
tanti svizzeri, ticinesi, guardano e basta
2 volte chiesta l'ambrine marrone, nn l'abbiamo, mandati a monte napo
uè la t-shirt nera S e' finita anche quella
matteo"""),

    dict(id="c0914", sent="2026-09-14 22:16", frm="stefano", business_date="2026-09-14", cc=["roberto", "vm"],
         subject="MIL02 Rinascente - chiusura 14/09",
         body="""Buonasera,

INCASSO: 13,4
BDG: 16,9
INGRESSI: 66
NOTE: lunedi lento, tedeschi e qualche francese. Buono lo zaino Makaio (2).
Metto in copia VM: stamattina il Visual di Rinascente ha spostato il nostro manichino della testata scale mobili per far spazio al pop-up di un marchio di borse "solo per 2 settimane". Nessuna mail, nessun preavviso, l'abbiamo trovato girato verso il muro. La capo piano dice che e' una decisione della direzione. Per noi quel manichino e' l'unico punto visibile da chi sale. Se vm-team puo' scrivere ufficialmente a Rinascente forse ci ascoltano, io ormai sono quello che si lamenta sempre.
Una cliente ha chiesto la t-shirt nera S, finita.

""" + SIG_S),

    dict(id="c0915", sent="2026-09-15 21:47", frm="stefano", business_date="2026-09-15",
         subject="MIL02 Rinascente - chiusura 15/09",
         body="""Prova evacuazione stamattina: tutti in piazza dalle 9:15 alle 9:55, aperto alle 10 ma i primi due ore piano vuoto.
12,4k vs 17,4 bdg, 60 ingressi.
Karakorum grigio in 7 chiesto, non c'e'. Hermine blu 0 ancora a zero.
S."""),

    dict(id="c0916", sent="2026-09-16 21:36", frm="ilaria", business_date="2026-09-16",
         subject="Chiusura Rinascente 16/9",
         body="""ciao a tutti
consegna arrivata ✅ 150 pz, gia' tutto fuori
niente Ambrine (ovviamente 😅) e oggi altre 2 clienti l'hanno chiesta, una milanese voleva proprio il marrone in 1
incasso 12,8k, sotto budget di 5k e passa
americani e un paio di brasiliani
Ila 💫"""),

    dict(id="c0917", sent="2026-09-17 21:55", frm="stefano", business_date="2026-09-17",
         subject="MIL02 Rinascente - chiusura 17/09",
         body="""inc 12,6 / bdg 21,5 / ingr 93
giovedi pessimo. Molta gente al piano per gli sconti di fine stagione degli altri corner, da noi solo giro.
Bene il tricot imbottito blu e il cardigan logo blu, 2+2.
Stefano"""),

    dict(id="c0918", sent="2026-09-18 23:05", frm="ilaria", business_date="2026-09-18",
         subject="Chiusura Rinascente 18/9 🎉",
         body="""venerdi bello!! 31,5k (+23%) 🎉
4 marsupi Legere neri, 4 Trailgrip donna panna, 3 Maire nere, 3 Karakorum neri
manca la Trailgrip panna 36, una ragazza la voleva x forza
e ancora il dolcevita marrone XS (sempre lui 🤎)
la Maire nera sta andando via veloce, ne restano pochissime in 0 e 2 👀
notte
Ila"""),

    dict(id="c0920", sent="2026-09-20 22:14", frm="ilaria", business_date="2026-09-19,2026-09-20",
         subject="chiusura sab + dom 19-20/9",
         body="""ciao scusate ieri sera nn ho mandato, crollata sul divano 😵

SABATO 19
37,9k ✅ (+9%)
165 ingressi
3 Maire nere + 3 cardigan logo neri, 2 Montcla blu
finita Maire nera tg 0 ❌
chiesto Rosiere verde oliva tg 7

DOMENICA 20
14,5k ❌ (-40%)
125 ingressi ma conversione bassissima, tutti turisti con la borsa di Rina e basta
ora mancano Maire nera 0 E 2
ancora 1 richiesta dolcevita marrone XS

da martedi fashion week 👗 speriamo
Ila"""),

    # ---------------------------------------------------------------- fashion week
    dict(id="c0921", sent="2026-09-21 22:02", frm="stefano", business_date="2026-09-21",
         subject="MIL02 Rinascente - chiusura 21/09",
         body="""Buonasera,
17,3k vs 19,5. Cinesi, inglesi, tedeschi. 2 Maya blu, 2 Chambre.
Richiesto Montgenevre blu tg 5 (gia' il secondo questo mese). Karakorum nero tg 4 finito.

Domani parte la fashion week. Rinascente ha montato l'allestimento al piano terra e alla terrazza, il nostro corner non e' coinvolto in niente nonostante avessimo proposto la vetrina interna con le Maire. "Non c'era piu' spazio nel piano eventi". Giovedi-sabato chiudiamo alle 22, i turni li ho coperti io con gli straordinari di Matteo.

""" + SIG_S),

    dict(id="c0922", sent="2026-09-22 21:49", frm="stefano", business_date="2026-09-22",
         subject="MIL02 Rinascente - chiusura 22/09",
         body="""Primo giorno di fashion week e noi facciamo -40. 10,9k.
Piazza Duomo piena di gente col pass al collo ma in Rinascente vanno solo al rooftop a farsi le foto e scendono con le scale mobili senza fermarsi. Qualche cliente emiratino nel pomeriggio.
2 resi: Hermine tg 1 per taglia e una t-shirt M.
Stefano

Inviato da iPhone"""),

    dict(id="c0923", sent="2026-09-23 22:31", frm="stefano", business_date="2026-09-23",
         subject="MIL02 Rinascente - chiusura 23/09",
         body="""Ciao a tutti,
giornata pazzesca, finalmente.

INCASSO: 47,1k
BDG: 20,1
INGRESSI: 126
SCONTRINI: 20
NOTE: 4 Maya nere, 4 Bady nere, guanti tech. Tanti buyer stranieri e un paio di stylist che hanno comprato per uno shooting (spero non tornino a rendere lunedi...). Coreane alla ricerca della Maire nera, tg 0, che non abbiamo piu'. Anche Karakorum nero 4, cardigan logo blu XL e il tricot nero XS: tutti chiesti e tutti mancanti.
2 resi, uno per qualita (tricot XS, cucitura aperta sulla spalla).

""" + SIG_S),

    dict(id="corr0923", sent="2026-09-23 23:18", frm="stefano", kind="correction", business_date="2026-09-23",
         subject="CORREZIONE chiusura 23/09",
         body="""scusate, ho scritto 47,1k ma era il lordo prima dei resi e degli sconti dipendenti, preso dalla stampa Rina sbagliata.
netto 40,7k. comunque +100% sul budget.
S."""),

    dict(id="c0924", sent="2026-09-24 23:12", frm="ilaria", business_date="2026-09-24",
         subject="Chiusura Rinascente 24/9 👗",
         body="""ciao!!
altro giorno fortissimo 💪 38,6k (+62%)
146 ingressi
Bady nere x3, Maya nere x3, 3 Tib blu, Hermine nere
MA quante richieste perse 😭
- Maire nera 0 e 2 (coreane + una milanese)
- Maya nera tg 7 (uomo grosso 😅)
- Karakorum grigio 3
- Montgenevre nero 6
- Ambrine marrone di nuovo, ormai la chiedono tutti i giorni 🤎
Hermine nera 2 e Hermine blu 0 finite
evento Rina in terrazza stasera, musica fino a tardi, noi chiusi alle 22 e via
Roberto per la Maire nera c'e' qualche speranza?? 🙏
Ila"""),

    dict(id="c0925", sent="2026-09-25 22:58", frm="stefano", business_date="2026-09-25",
         subject="MIL02 Rinascente - chiusura 25/09",
         body="""Ciao,
26,5k, -5% sul budget nonostante 145 ingressi. Si vendeva bene fino alle 19 poi la terrazza Rina ha aperto il cocktail e il piano si e' svuotato.
Ho sentito Roberto al telefono per la Maire nera: dal magazzino niente prima di meta' ottobre. Abbiamo aperto una lista d'attesa, siamo a 7 nomi (2 tg 0, 3 tg 1, 2 tg 2). Oggi altra richiesta in 1.
Mancano anche Hermine blu 0 e Bady nera 2.
La consegna di mercoledi non e' ancora arrivata. CSG dice "in consegna".
Stefano"""),

    dict(id="c0926", sent="2026-09-26 23:24", frm="ilaria", business_date="2026-09-26",
         subject="Chiusura Rinascente 26/9",
         body="""sabato 43,2k 🚀 (+11%)
213 ingressi record dell'anno credo
4 beanie blu, 4 beanie nere, Hermine panna x3, Tib panna x3
tanti cinesi gia' 🇨🇳
la consegna che doveva arrivare mercoledi e' arrivata OGGI alle 11 in pieno sabato di fashion week 🙄 3 giorni di ritardo, 146 pz da sistemare mentre c'era la fila
chieste: Bady panna 0, felpa grigia S
Ila"""),

    dict(id="c0927", sent="2026-09-27 21:41", frm="store", business_date="2026-09-27",
         subject="chiusura rinascente 27/09",
         body="""ultimo giorno sfilate, tanta gente poco scontrino
18,2 su 26 di budget
150 ingressi conversione 10%
3 t-shirt nere, 2 cardigan logo neri, 2 Bady panna, 2 Ilvaro nere
chiesti Montgenevre grigio 3 e felpa grigia S (di nuovo)
2 resi regalo (Hermine 1, Montcla 6)
matteo"""),

    dict(id="c0928", sent="2026-09-28 22:09", frm="stefano", business_date="2026-09-28",
         subject="MIL02 Rinascente - chiusura 28/09",
         body="""Buonasera,

INCASSO: 33k
BDG: 20,7
INGRESSI: 110
NOTE: lunedi post sfilate inaspettato, 4 Maya nere, Hermine nere, 3 Flammette. Due clienti per l'Ilvaro panna in 2, finita. Maire nera chiesta in 0 e 2 (lista d'attesa ora 9). Maya blu 1 e Montgenevre blu 5 (il solito).
Primo reso Tib per difetto: Tib blu tg 3, il cursore della zip si e' sfilato dopo una settimana. Il cliente era gentile ma ha detto "per 1000 euro". Messo in quarantena in back-office, foto in arrivo.

""" + SIG_S),

    dict(id="c0929", sent="2026-09-29 21:42", frm="ilaria", business_date="2026-09-29",
         subject="Chiusura Rinascente 29/9",
         body="""ciao
18,3k (-10%)
gia tanti cinesi, sono quasi piu dei milanesi 🇨🇳
UN ALTRO Tib rientrato col cursore della zip partito!! 😤 tg 3 anche questo, secondo in 2 giorni
e intanto un cliente voleva il Tib blu in 1 e nn c'e'
chieste anche Hermine nera 00 e polo blu XXL
Ila"""),

    # ---------------------------------------------------------------- golden week
    dict(id="c0930", sent="2026-09-30 22:03", frm="stefano", business_date="2026-09-30",
         subject="MIL02 Rinascente - chiusura 30/09",
         body="""Ciao a tutti,
18,4k vs 23,1. Dal pomeriggio sono arrivati i primi gruppi cinesi della settimana d'oro, con le guide. Problema: la guida li porta al piano terra cosmetica e al -1 per il tax free, al 2° piano salgono in pochi. Rinascente ha messo un desk cinese all'ingresso ma da' i volantini con i brand Rinascente partner, noi non ci siamo.
Consegna CSG di 208 pz arrivata stamattina, puntuale.
1 Tib tg 2 reso per cambio idea, questo almeno funziona.
Ambrine marrone chiesta 2 volte.
Stefano"""),

    dict(id="c1001", sent="2026-10-01 22:17", frm="ilaria", business_date="2026-10-01",
         subject="Chiusura Rinascente 1/10 🇨🇳",
         body="""ciao!
26,3k (+8%)
145 ingressi, quasi meta' cinesi 🇨🇳🇨🇳
3 Montgenevre blu, 3 Trailgrip donna nere, 2 zaini Makaio
altri 2 Tib rientrati difettosi 😡 tg 3 e tg 5, sempre il cursore della zip
ho tirato fuori dal magazzino tutti i Tib che abbiamo e provato le zip una per una, 2 su 6 hanno il cursore che balla. Li ho tolti dalla vendita, Stefano decide domani
chiesta Maire nera tg 1 (lista!)
Ila"""),

    dict(id="c1002", sent="2026-10-02 23:26", frm="stefano", business_date="2026-10-02",
         subject="MIL02 Rinascente - chiusura 02/10",
         body="""Buonasera,
giornata record: 56,1k netto, budget 29,8. 191 ingressi, 31 scontrini.
Cinesi tutto il giorno, molte coppie giovani che sanno gia' cosa vogliono, foto sul telefono. Maya nere, Maire blu (la nera non c'e' e la prendono blu, non tutte), 3 polo blu, beanie nere.
Persa ancora la Maire nera in 0 e 2, e un cable knit beige M.
Il tax free Rinascente e' andato in tilt alle 16, coda fino alle scale mobili per un'ora. Tre clienti ci hanno chiesto se potevamo fare noi il tax free, ovviamente no: dentro Rinascente passa tutto da loro.
Tib: Ilaria ha tolto 2 pezzi con zip difettosa dal banco. Li rimandiamo a CSG con il reso difettosi, chi ci da' il numero di autorizzazione?

""" + SIG_S),

    dict(id="dup1002", sent="2026-10-02 23:28", frm="stefano", kind="dup", business_date="2026-10-02",
         subject="MIL02 Rinascente - chiusura 02/10",
         body="""Buonasera,
giornata record: 56,1k netto, budget 29,8. 191 ingressi, 31 scontrini.
Cinesi tutto il giorno, molte coppie giovani che sanno gia' cosa vogliono, foto sul telefono. Maya nere, Maire blu (la nera non c'e' e la prendono blu, non tutte), 3 polo blu, beanie nere.
Persa ancora la Maire nera in 0 e 2, e un cable knit beige M.
Il tax free Rinascente e' andato in tilt alle 16, coda fino alle scale mobili per un'ora. Tre clienti ci hanno chiesto se potevamo fare noi il tax free, ovviamente no: dentro Rinascente passa tutto da loro.
Tib: Ilaria ha tolto 2 pezzi con zip difettosa dal banco. Li rimandiamo a CSG con il reso difettosi, chi ci da' il numero di autorizzazione?

""" + SIG_S),

    dict(id="c1003", sent="2026-10-03 23:19", frm="ilaria", business_date="2026-10-03",
         to=["vm"], cc=[],
         subject="Chiusura Rina 3/10 🇨🇳🇨🇳",
         body="""SABATO DI FUOCO 🔥🔥🔥
53k (+31%)
216 ingressi, piu della meta cinesi
5 cardigan logo neri!!! 4 Trailgrip donna nere, beanie, tricot
chieste e perse:
❌ Maire blu tg 3 (x2)
❌ Montgenevre grigio 7
❌ polo blu XL
Trailgrip GTX uomo 44 finita
ancora 1 Tib reso x zip (tg 4) 😤 siamo a 6??
siamo stanchissimi, pausa di 15 min a testa, Rina non ci ha dato il cambio della ragazza jolly perche serviva al corner di fianco
Ila 💤"""),

    dict(id="c1004", sent="2026-10-05 09:14", frm="store", business_date="2026-10-04",
         subject="chiusura rinascente domenica 4/10",
         body="""buongiorno, ieri sera il wifi di Rina era giu' e la mail e' rimasta in uscita, la rimando adesso

domenica 41k, budget era 27,8
196 ingressi tantissimi cinesi
3 Karakorum neri, 3 Rosiere nere, 2 Montcla blu, 2 Maire nere?? no scusate Maire BLU
chieste Maire nera 0 (2 sciure diverse, una cinese una milanese), Maire blu 3, Montgenevre blu 6
finite Karakorum nero 4 e Trailgrip GTX 42 e 44
la chiusura Rina dice 41,8 ma loro contano lordo con la card, il nostro e' 41,07
matteo"""),

    dict(id="c1005", sent="2026-10-05 22:08", frm="stefano", business_date="2026-10-05",
         subject="MIL02 Rinascente - chiusura 05/10",
         body="""Ciao,
30,4k (+34%). Cinesi ancora tantissimi, piu' degli italiani.
Perse: Hermine nera 4, Ilvaro panna 0, Tib blu 3 (non lo abbiamo e quelli rimasti li abbiamo bloccati per la zip), Trailgrip GTX 42.
Ambrine: oggi ho chiamato via Monte per mandare una cliente, mi dicono che anche loro nel marrone non hanno 0, 1 e 2. Quindi la cliente l'abbiamo persa tutti e due.
2 resi: Hermine 0 regalo, Maya tg 5 per taglia.
Stefano"""),

    dict(id="c1006", sent="2026-10-06 22:12", frm="ilaria", business_date="2026-10-06",
         subject="Chiusura Rinascente 6/10",
         body="""ciao!
33,6k 💪 (+52%)
5 tricot imbottiti blu!!! 💙 adesso mancano M e XXL, li hanno chiesti subito dopo
Karakorum nero tg 4 chiesto 2 volte, Karakorum grigio 2, Flammette blu 0
Maire blu tg 2 finita, la nera non ne parliamo
storia del giorno: una ragazza coreana mi ha fatto vedere la foto della cantante delle LUMIERE con un piumino corto ROSA 🩷 voleva quello. noi il rosa non l'abbiamo mai avuto. le ho fatto vedere l'Ilvaro nero, niente
Ila"""),

    dict(id="c1007", sent="2026-10-07 22:26", frm="stefano", business_date="2026-10-07",
         subject="MIL02 Rinascente - chiusura 07/10",
         body="""Buonasera,

INCASSO: 33,5
BDG: 23,3
INGRESSI: 140
NOTE: 4 Ilvaro nere, oggi le chiedevano tutte le coreane (secondo me per la storia del rosa che raccontava Ilaria). Maya nere, beanie.
Perse: Maire nera 1 e 3, Montgenevre nero 1, Trailgrip GTX 44.
Ancora un Tib difettoso reso, tg 1.
La consegna prevista oggi non e' arrivata. DHL dice venerdi. Proprio adesso che ci servivano i Karakorum.

""" + SIG_S),

    dict(id="c1008", sent="2026-10-08 21:39", frm="store", business_date="2026-10-08",
         subject="chiusura rinascente 08/10",
         body="""ultimo giorno della settimana cinese, si sente gia meno
21k, -24 sul budget
3 beanie nere, 2 felpe blu, 2 Karakorum neri
chieste t-shirt blu XXL, Trailgrip GTX 44 (sempre), Trailgrip donna panna 37
1 reso Chambre 3 qualita, piuma che esce dalla cucitura
matteo"""),

    # ---------------------------------------------------------------- after golden week
    dict(id="s1009card", sent="2026-10-09 15:47", frm="stefano", kind="reply",
         to=["giulia"], cc=["roberto", "mil01"],
         subject="Re: URGENTE - cardigan logo M per Monte Napo",
         body="""Ciao Giulia,
mi spiace ma no. Di cardigan logo in M ne ho una sola, nera, e la tengo: da noi il cardigan e' il best seller del sabato e la M e' la taglia che va di piu'. Anche la blu M qui e' gia' finita.
Se Roberto decide diversamente ovviamente mi adeguo.
Stefano

Il giorno 9 ott 2026, alle ore 12:03, Giulia Ferrandi <giulia.ferrandi@moncler-retail.example> ha scritto:
> Ciao Stefano,
> abbiamo finito la M del cardigan logo da ieri e ho 3 clienti in attesa (uno VIC). Il magazzino non ne ha fino a fine mese.
> Mi passi tutte le M che hai, nero e blu? Mando io il fattorino stasera.
> Grazie
> Giulia
> Store Manager Milano Montenapoleone"""),

    dict(id="r1009card", sent="2026-10-09 18:11", frm="roberto", kind="reply", reply_to_id="s1009card",
         to=["giulia", "stefano"], cc=["mil01"],
         subject="Re: URGENTE - cardigan logo M per Monte Napo",
         body="""Giulia, niente transfer, MIL02 ha un pezzo solo. Prendi i nominativi e aspettiamo CSG, la M rientra fine mese. Ho gia' chiesto a merch di dare priorita' a Monte.
R.

Inviato da iPhone"""),

    dict(id="c1009", sent="2026-10-09 22:44", frm="stefano", business_date="2026-10-09",
         subject="MIL02 Rinascente - chiusura 09/10",
         body="""Ciao,
venerdi debole, 22,7k contro 32,4. Finita la settimana cinese e si sente: oggi soprattutto emiratini e italiani.
Trailgrip GTX nera chiesta in 42 (2 volte) e 44 (2 volte), quattro paia perse, che per una scarpa e' tanto. Anche cable knit nero L e felpa blu M.
Hermine blu x3.
La consegna DHL non e' arrivata nemmeno oggi.
Stefano"""),

    dict(id="c1010", sent="2026-10-10 23:21", frm="ilaria", business_date="2026-10-10",
         subject="Chiusura Rinascente 10/10",
         body="""sabato 39,6k (budget era 45 😬)
207 ingressi
5 cardigan logo neri 🖤 la mia teoria e' che lo regalano tutti
3 Hermine nere, 2 Chambre, 2 Maire blu
ARRIVATA la consegna 📦 257 pz con 3 giorni di ritardo, di sabato, di nuovo. Back-office esploso
cliente voleva cardigan logo BLU M, finito
e cmq il cardigan M non lo diamo, come sempre Monte Napo pensa che siamo il loro magazzino 🙃
Ila"""),

    dict(id="c1011", sent="2026-10-11 21:51", frm="store", business_date="2026-10-11",
         subject="chiusura rinascente 11/10",
         body="""domenica bella, 39,9k, sopra budget
coreani e sauditi
4 Hermine nere, 3 Maya nere, 2 Maire blu
3 resi: 2 Tib (uno taglia 5 x misura, uno taglia 3 con la zip rotta, il solito), 1 beanie
chiesto dolcevita marrone L
una sciura voleva l'ambrine marrone in 0, le ho detto che neanche monte napo ce l'ha
matteo"""),

    # 10-12 deliberately missing
    dict(id="c1013", sent="2026-10-13 22:07", frm="stefano", business_date="2026-10-13",
         subject="MIL02 Rinascente - chiusura 13/10",
         body="""Buonasera,
ieri sera non ho mandato, chiedo scusa, lunedi normale niente da segnalare.

Oggi primo freddo vero, 8 gradi stamattina in piazza e la gente col piumino. 26,1k (+9%) con solo 76 ingressi: chi entrava sapeva cosa voleva. Hermine nere x3, Maya blu, cardigan logo blu.
Tanti americani.
Perse: Karakorum nero 5, cable knit nero XXL.
2 resi: Hermine 00 regalo, Karakorum 5 per taglia (voleva il 4, non c'era).

""" + SIG_S),

    dict(id="m1014", sent="2026-10-14 13:22", frm="store", kind="misc",
         subject="domani",
         body="""Ila domani mi copri tu l'apertura? ho il dentista alle 9 e arrivo per le 11. se nn puoi chiedo a Stefano
grazie
matte"""),

    dict(id="c1014", sent="2026-10-14 22:19", frm="ilaria", business_date="2026-10-14",
         subject="Chiusura Rinascente 14/10 🥶",
         body="""ciao!
34,2k ✅ (+35%)
il freddo aiuta 🥶 tutti vogliono il piumino
3 beanie nere, 2 blu, 2 Montcla blu, 2 Maya nere
consegna arrivata stamattina 206 pz ✅ ... e niente Maire nera nemmeno stavolta 😭😭 la lista ormai e' lunga
oggi chieste Maire nera 1 e 2 + polo blu XS
Ila"""),

    dict(id="c1015", sent="2026-10-15 22:31", frm="stefano", business_date="2026-10-15",
         subject="MIL02 Rinascente - chiusura 15/09",
         body="""Ciao,
24,1k (-13%). Clientela quasi tutta italiana oggi.
Da oggi Rinascente Card Days fino a domenica: -10% sui corner aderenti, noi non aderiamo (giustamente) ma metà dei clienti al banco chiede lo sconto e quando diciamo di no vanno da Woolrich di fianco che aderisce. Due li ho visti uscire col sacchetto loro.
Perse: Maire nera 3, polo blu L. Reso Montcla 4 per colore.
Domani sciopero generale, metro ferme. Per noi vuol dire che non arriva nessuno da Duomo e che meta' dello staff Rina non c'e'. Ci organizziamo.
Stefano"""),

    dict(id="c1016", sent="2026-10-16 22:48", frm="stefano", business_date="2026-10-16",
         subject="MIL02 Rinascente - chiusura 16/10 (sciopero)",
         body="""Buonasera a tutti,
come previsto giornata persa: 24,4k contro un budget di 37,2 (-35%). 96 ingressi.

Metro ferma da mattina fino al pomeriggio, la fermata Duomo era chiusa e qui dentro arriva tutto da li': senza M1 e M3 il piano e' vuoto. In piazza solo il corteo e qualche turista svizzero con la macchina.
Matteo e' arrivato a piedi da Lambrate alle 11:20, la ragazza di Rina che ci copre le pause non e' venuta e quindi pause saltate di nuovo. Alle 14 la capo piano ci ha detto che "forse" chiudevano un'ora prima, poi alle 18 hanno deciso di no. Così, a voce, come sempre. Io non dico niente, ma con loro non si riesce mai a programmare niente.

Vendite: 4 Flammette nere (freddo), 3 Bady nere, beanie blu. Persa la Maire nera in 1 e il cardigan logo blu M.
Card Days in corso, altri due clienti persi per lo sconto.
Spero domani si recuperi qualcosa, ma con budget 50k sara' dura.

""" + SIG_S),

    dict(id="c1017", sent="2026-10-17 23:14", frm="ilaria", business_date="2026-10-17",
         subject="Chiusura Rinascente 17/10",
         body="""sabato 35,9k ma budget 50 😩 (-29%)
187 ingressi, pieno di gente x i Card Days ma comprano da chi fa lo sconto
5 cardigan logo neri e ora... e' finita anche la M nera 😬 (ironia della sorte)
3 Maire blu
chiesti Montcla blu 6 e cardigan blu M (ancora)
Ila 😴"""),

    dict(id="c1018", sent="2026-10-18 21:46", frm="store", business_date="2026-10-18",
         subject="chiusura rinascente 18/10",
         body="""29,2k su 33,5
quasi tutti italiani, la domenica dei milanesi col freddo
3 Bady nere, 2 Maya verde, 2 Montgenevre neri, Trailgrip donna
Maire nera chiesta in 0, 1 e 3: tre clienti, tre no. ci guardano come se fossimo noi a nasconderla
Ilvaro nera tg 3 chiesta
ambrine marrone x2, ormai rispondo in automatico
reso Montcla 6 taglia
matteo

Inviato da iPad"""),

    dict(id="c1019", sent="2026-10-19 22:04", frm="stefano", business_date="2026-10-19",
         subject="chiusura MIL02 19/10",
         body="""Ciao,
32k (+24%). Finiti i Card Days e si respira. Molti emiratini e sauditi, e milanesi che col freddo finalmente comprano. Maya blu x3, beanie.
Chiesta Hermine panna 3, non c'e'.
Episodio: un signore ha comprato l'Arneb in via Monte, gli sta enorme, e' venuto qui per cambiarlo di una taglia. L'Arneb noi non lo teniamo, l'ho rimandato a Monte Napo. Era furioso. Mi dicono che anche li' ne stanno cambiando parecchi, veste molto grande.
Stefano"""),

    dict(id="c1020", sent="2026-10-20 21:58", frm="ilaria", business_date="2026-10-20",
         subject="Chiusura Rinascente 20/10",
         body="""ciao
24,4k (-10%)
giornata italiana, poco turismo
3 Maya blu, 2 marsupi
perse: Maire nera 1 e 2 (lista d'attesa ormai 14 nomi 📋), Maya blu 7
Ilvaro nera tg 1 finita
ultima: ancora Ambrine marrone 🤎 ce la mandate mai qui?
Ila"""),

    dict(id="c1021", sent="2026-10-21 22:36", frm="stefano", business_date="2026-10-21",
         subject="chiusura MIL02 21/10",
         body="""Buonasera,
FINALMENTE arrivata la Maire nera con la consegna di oggi (249 pz totali). Chiamate le clienti della lista d'attesa da mezzogiorno: 3 vendute oggi stesso, altre passano domani e venerdi. Non tutte rispondono, due l'hanno gia' comprata da un'altra parte.
30,2k (+13%), 102 ingressi.
4 beanie nere, Trailgrip donna, Montgenevre neri.
Ilvaro nera ora finita in 1 e 2.
E l'ennesimo Tib tornato indietro con lo zip difettoso, taglia 3. Il Tib in pratica non lo vendiamo piu', lo propongo solo se il cliente insiste.

""" + SIG_S),
]
