# COU01 Courmayeur - hand-authored closing emails (see notes/COU01.md)

PERSONAS = {
    "paolo": "Paolo Bertholin <paolo.bertholin@valentino-retail.example>",
    "elisa": "Elisa Vuillermoz <elisa.vuillermoz@valentino-retail.example>",
    "store": "Valentino Courmayeur <cou01.store@valentino-retail.example>",
    "roberto": "Roberto Galli <roberto.galli@valentino-retail.example>",
}

DEFAULT_TO = ["retail-ops-italy@valentino-retail.example"]
DEFAULT_CC = ["roberto"]

EMAILS = [
    dict(id="u0831", sent="2026-08-31 20:30", frm="paolo", subject="COU01 - Chiusura 31.08",
         business_date="2026-08-31", body="""Bon, prima chiusura di settembre.
1) Fatturato 10.660 € vs budget 6.970 (+53%)
2) 47 ingressi, 8 scontrini
3) Clienti: svizzeri (Ginevra/Vallese), americani, qualche italiano, una coppia turca.
2 Nova nere, pantalone Cortina, cappellino bianco, felpa nera.
Richieste non evase: Fiammetta nero 4, Vtrack donna nera 38.
Ricordo a tutti che chiudiamo per fine stagione sabato 12/9 sera, riapertura fine novembre.
Allora ciao
Paolo

--
Paolo Bertholin
Store Manager | Valentino Courmayeur
Messaggio riservato: se lo avete ricevuto per errore cancellatelo e avvisate il mittente."""),

    dict(id="u0901", sent="2026-09-01 20:10", frm="elisa", subject="chiusura cou 1/9",
         business_date="2026-09-01", body="""ciao raga
4k oggi, 3 scontrini su 38 ingressi
guanti tech, doposci Alpina nero, una Aurea navy e un Aria nero (signora indiana, un amore)
tempo bellissimo, tutti su con la Skyway e poi giu dritti a cena, in Via Roma pochi
Eli"""),

    dict(id="u0902", sent="2026-09-02 20:45", frm="paolo", subject="COU01 - Chiusura 02.09",
         business_date="2026-09-02", body="""Bon,
fatturato 3.610 (bdg 7.200), 41 ingressi, 5 scontrini.
Arrivati 30 pezzi da CSG stamattina, tutto corretto. Domanda: a 10 giorni dalla chiusura stagionale ha senso ricevere ancora merce? Una parte la rimetteremo nei cartoni tra due settimane. Se si può, bloccate i riassortimenti dopo il 9.
Vendite: cappellino bianco, Vtrack grigia, t-shirt navy, cable knit bianco. Clienti italiani, coreani, tedeschi, un cinese.
Paolo"""),

    dict(id="u0903", sent="2026-09-03 20:20", frm="elisa", subject="chiusura cou 3/9",
         business_date="2026-09-03", body="""ciao!
10,2k oggi, quasi in budget (10,6). 53 ingressi, 8 scontrini
volati 2 Vel bianchi (padre e figlio brasiliani) e 2 Aria bianchi, + felpa nera e una Nova nera
il Vel bianco adesso e finito in 4 e 5, rimaste le altre taglie
reso un cappellino logo, taglia unica ma alla signora stava piccolo (??)
cinesi e brasiliani, giornata strana ma bella
Eli"""),

    dict(id="u0904", sent="2026-09-04 20:35", frm="paolo", subject="COU01 - Chiusura 04.09",
         business_date="2026-09-04", body="""1) 5.160 € (bdg 11.900) -57%
2) 54 ingressi / 8 scontrini, tutti piccoli
3) quasi solo italiani, i torinesi del weekend arrivano già il venerdì
Persi: Vel bianco 4 (proprio la taglia finita ieri), Artem navy 6, Vtrack donna 36.
Vendute 2 Vtrack, guanti, cappellino bianco: ormai il cappellino bianco lo comprano tutti, ne restano 2.
Paolo

--
Paolo Bertholin
Store Manager | Valentino Courmayeur
Messaggio riservato: se lo avete ricevuto per errore cancellatelo e avvisate il mittente."""),

    dict(id="u0905", sent="2026-09-05 21:00", frm="elisa", subject="chiusura sabato 5/9 cou",
         business_date="2026-09-05", body="""sabato: 9,5k (budget 15,9 pero eh..)
85 ingressi, 9 scontrini. americani tanti (gruppo golf? boh), francesi da Cortina col tunnel, italiani
2 t-shirt nere, 2 felpe nere, una Valdora bianca (!!), crewneck bianca
mancati: Amalia marrone tg 3 (la cliente francese l'aveva vista a Parigi, noi nn l'abbiamo mai avuta), cable knit bianco L
domani Paolo
Eli"""),

    dict(id="u0906", sent="2026-09-06 20:25", frm="paolo", subject="COU01 - Chiusura 06.09",
         business_date="2026-09-06", body="""Bon. Domenica fiacca: 4.190 €, 44 ingressi, 2 scontrini.
Una famiglia giapponese che tornava dal Monte Bianco ha preso dolcevita navy, Artem nero e un Aria bianco. Poi niente.
Volevano anche: Iridia nero in 2, Amalia marrone 2 (seconda richiesta di marrone in due giorni, mai ricevuto), t-shirt nera XXL.
Paolo"""),

    dict(id="u0907", sent="2026-09-07 20:15", frm="elisa", subject="chiusura cou 7/9",
         business_date="2026-09-07", body="""6,2k, 48 ingressi, 6 scontrini
beanie bianco, zaino Urban Backpack nero, jersey polo navy, t-shirt nera
CAPPELLINO BIANCO FINITO. una ragazza coreana lo voleva oggi pomeriggio, l'ultimo l'avevo venduto stamattina. se CSG ne ha 3-4 li prendiamo anche x una settimana sola, vanno via subito
Eli"""),

    dict(id="u0909", sent="2026-09-09 20:40", frm="paolo", subject="COU01 - Chiusura 08.09",
         business_date="2026-09-09", body="""1) 1.279 € su 8.250 di budget
2) 39 ingressi, 2 scontrini
3) americani e una coppia saudita
Arrivati altri 8 pezzi da CSG nonostante la mail. Dentro c'era un cappellino bianco che è andato via in un'ora, il resto lo lasciamo nel cartone tanto torna indietro.
Vendite: il cappellino, Vtrack donna nera, Nova nera.
Richieste: Iridia bianco 4, dolcevita nero XS, jersey polo navy M.
Reso tricot cardigan M, cambio idea.
Bref, settimana finale molto molle.
Paolo"""),

    dict(id="u0910", sent="2026-09-10 21:10", frm="paolo", subject="COU01 - Chiusura 10.09 + organizzazione fine stagione",
         business_date="2026-09-10",
         cc=["roberto", "dc-replenishment@valentino-retail.example", "merch-planning@valentino-retail.example"],
         body="""Bon,
1) 10.290 € (bdg 8.800) +17%, ultimo bel giorno credo
2) 56 ingressi / 8 scontrini, cinesi, sauditi, svizzeri, italiani
Sciarpa cashmere nera, cappellino nero, jersey polo bianca, felpa nera. Chiesto felpa navy XXL, no.

Organizzazione chiusura:
- sabato 12 ultimo giorno aperto, chiusura alle 19.30
- dopo la chiusura iniziamo l'inventario di fine stagione con la pistola (Elisa + io), domenica mattina finiamo e ricontiamo le differenze
- arrivati oggi 10 cartoni vuoti + etichette reso da CSG. Rendiamo tutto il leggero/mezza stagione (jersey, maglieria, jersey polo, sneakers, cappellini, gilet) e lasciamo in magazzino chiuso i piumini pesanti e i doposci per la riapertura, come concordato con merch planning
- ritiro corriere lunedì 14 mattina, vi mando il numero DDT appena fatto
- chiusura POS e cassa domenica dopo l'inventario
Se c'è qualcosa di diverso ditemelo entro venerdì.
Paolo

--
Paolo Bertholin
Store Manager | Valentino Courmayeur
Messaggio riservato: se lo avete ricevuto per errore cancellatelo e avvisate il mittente."""),

    dict(id="u0911", sent="2026-09-11 20:00", frm="store", subject="Chiusura Courmayeur 11/09",
         business_date="2026-09-11", body="""Buonasera,
oggi 1.860 euro, 2 scontrini (cappellino nero e un Iridia nero) su 49 ingressi. Italiani e tedeschi.
Richieste: Aria nero 0, Iridia nero 00, cappellino bianco (terza volta questa settimana).
Abbiamo cominciato a preparare i cartoni per il reso e a togliere le placche antitaccheggio dai capi leggeri.
Elisa e Paolo sono stati in magazzino tutto il pomeriggio.
Sophie Glarey
Valentino Courmayeur"""),

    dict(id="u0912", sent="2026-09-12 22:35", frm="paolo", subject="COU01 - Ultima chiusura stagione estiva 12.09",
         business_date="2026-09-12", body="""Bon, voilà, ultima chiusura dell'estate.
1) 2.900 € (bdg 14.520, lo sapevamo)
2) 63 ingressi, 4 scontrini
3) coreani, italiani, americani
Ultima cliente alle 19.20, una signora di Aosta cliente storica, sciarpa cashmere beige. Prima cappellino navy, Vtrack nera, jersey polo nera.
Fino all'ultimo ci hanno chiesto cose che non avevamo: 2 jersey polo bianche M (due ragazzi coreani), Fiammetta navy 00, Iridia nero 00, Artem nero 7, e il solito cappellino bianco.
Per la riapertura invernale il cappellino bianco e le taglie piccole donna vanno riviste, quest'estate abbiamo perso parecchio così.
Staff: Sophie finisce il contratto stagionale domani. Elisa dal 21/9 va a dare una mano a Milano Montenapoleone (fashion week + cinesi di ottobre), fino a metà ottobre circa. Io dopo il reso sono in ferie fino al 5/10.
Iniziato l'inventario stasera, fatto donna e accessori, domani il resto.
Merci a tutti per la stagione
Paolo

--
Paolo Bertholin
Store Manager | Valentino Courmayeur
Messaggio riservato: se lo avete ricevuto per errore cancellatelo e avvisate il mittente."""),

    dict(id="u0913_inv", sent="2026-09-13 16:50", frm="paolo", kind="misc",
         cc=["roberto", "it-helpdesk@valentino-retail.example"],
         subject="COU01 - Inventario fine stagione + chiusura POS", body="""Bon,
inventario finito alle 15, contato tutto con la pistola e ripassato due volte le differenze.
A sistema 216 pz, contati 214. Differenze: mancano un cappellino navy, una t-shirt bianca e una sciarpa grigia, c'è un beanie bianco in più (probabilmente un reso di luglio non caricato). Mando il dettaglio domani con il DDT.
Reso: 9 colli pronti in negozio per lunedì.
POS: fatta la chiusura Z, cassa a zero, fondo cassa versato. Terminale e stampante spenti e staccati, ticket a it-helpdesk per sospendere la linea fino a novembre.
Allarme inserito, chiavi una a me e una a Elisa.
Paolo"""),

    dict(id="u0914_reso", sent="2026-09-14 12:10", frm="paolo", kind="misc",
         to=["dc-replenishment@valentino-retail.example"], cc=["retail-ops-italy@valentino-retail.example", "roberto"],
         subject="COU01 - Reso fine stagione a CSG - DDT 0058/26", body="""Buongiorno,
stamattina alle 11.20 BRT ha ritirato il reso di fine stagione di Courmayeur.
DDT n. 0058/26 del 14/09/2026
Colli: 9
Pezzi: 121 (jersey, maglieria, jersey polo, sneakers, cappellini/accessori leggeri, gilet e capispalla mezza stagione)
Destinazione: CSG - resi negozi
In negozio restano in magazzino 93 pz (piumini pesanti + doposci Alpina) per la riapertura.
Vi prego di confermare la ricezione e di avvisarmi se trovate differenze sul conteggio.
Grazie
Paolo

--
Paolo Bertholin
Store Manager | Valentino Courmayeur
Messaggio riservato: se lo avete ricevuto per errore cancellatelo e avvisate il mittente."""),

    dict(id="u0915_re", sent="2026-09-15 09:12", frm="roberto", to=["paolo"],
         cc=["retail-ops-italy@valentino-retail.example"], reply_to_id="u0914_reso", kind="reply", suffix="_re1",
         subject="Re: COU01 - Reso fine stagione a CSG - DDT 0058/26", body="""Paolo, CSG mi dice che nella prenotazione ritiro risultano 8 colli e non 9. Mi mandi il dettaglio delle differenze inventario e una foto del DDT firmato? Così chiudiamo la pratica prima che vai in ferie.
R.

Inviato da iPhone"""),

    dict(id="u0915_re2", sent="2026-09-15 11:30", frm="paolo", to=["roberto"],
         cc=["dc-replenishment@valentino-retail.example", "retail-ops-italy@valentino-retail.example"],
         reply_to_id="u0915_re", kind="reply", suffix="_re2",
         subject="Re: COU01 - Reso fine stagione a CSG - DDT 0058/26", body="""Ciao Roberto,
i colli sono 9: 8 di merce + 1 con grucce, antitaccheggi e materiale vetrina (sul DDT è scritto in fondo, forse in prenotazione l'hanno contato a parte). I pezzi di merce sono 121 in ogni caso.
In allegato le differenze dell'inventario e la foto del DDT firmato dall'autista.
Riepilogo: sistema 216, contati 214, tre pezzi in meno e uno in più.
Allora ciao, ci sentiamo a ottobre
Paolo""",
         attachments=[
             {"name": "COU01_inventario_fine_stagione_differenze.xlsx", "rows": [
                 ["Negozio", "COU01 Courmayeur", "", "", "", ""],
                 ["Data inventario", "13/09/2026", "", "", "", ""],
                 ["", "", "", "", "", ""],
                 ["Articolo", "Colore", "Taglia", "Qta sistema", "Qta contata", "Diff"],
                 ["VLOGO CAP", "blu notte", "TU", 5, 4, -1],
                 ["VLOGO T-SHIRT", "bianco", "M", 2, 1, -1],
                 ["VALENTINO SCARF", "grigio melange", "TU", 2, 1, -1],
                 ["VLOGO BEANIE", "bianco", "TU", 3, 4, 1],
                 ["", "", "", "", "Totale diff", -2],
                 ["", "", "", "", "", ""],
                 ["Tot. pezzi sistema", 216, "", "", "", ""],
                 ["Tot. pezzi contati", 214, "", "", "", ""],
                 ["di cui a reso CSG (DDT 0058/26)", 121, "", "", "", ""],
                 ["di cui in magazzino negozio", 93, "", "", "", ""],
             ]},
             {"name": "IMG_2291.jpg"},
         ]),

    dict(id="u1006", sent="2026-10-06 18:20", frm="paolo", kind="misc",
         to=["merch-planning@valentino-retail.example"],
         cc=["roberto", "retail-ops-italy@valentino-retail.example", "facility-italy@valentino-retail.example"],
         subject="COU01 riapertura inverno - proposta assortimento + lavori", body="""Ciao a tutti,
rientrato dalle ferie, qualche punto per la riapertura di Courmayeur di venerdì 27 novembre.

1) Assortimento / allocazione, vi mando la nostra proposta prima che chiudiate le allocazioni inverno:
- Aurea nera: più profondità sulle taglie 0-1-2, l'anno scorso a Natale eravamo già scoperti
- Alpina (doposci) nero e bianco, tutte le taglie 36-40
- linea Atelier: Piero e Valdora, qui la gente scia davvero, almeno 2 pz per taglia
- cappellino logo bianco e beanie: quest'estate il cappellino bianco l'abbiamo perso 4-5 volte, per l'inverno almeno il doppio dei beanie
- donna taglie piccole (00/0): richieste continue da clienti asiatiche, Iridia e Fiammetta 00 mai avuti
- marrone (Amalia): chiesto 2 volte a inizio settembre e noi zero pezzi. Se c'è qualcosa anche per noi ha senso.
- Vel: ho letto dei problemi con la zip, i nostri 7 Vel bianchi sono nel reso del 14/9 a CSG, controllateli prima di rimandarli in negozio.

2) Lavori: imbianchino dal 2 al 6 novembre (pareti + camerini), facility mi confermate la ditta? Da sistemare anche la porta del magazzino che non chiude bene.

3) Personale: cerco 2 stagionali da metà novembre, possibilmente con il francese (clienti da Cortina e svizzeri). Colloqui la settimana prossima.

4) POS e linea da riattivare entro il 23/11, apro il ticket a novembre.

Allora ciao
Paolo

--
Paolo Bertholin
Store Manager | Valentino Courmayeur
Messaggio riservato: se lo avete ricevuto per errore cancellatelo e avvisate il mittente."""),

    dict(id="u1019", sent="2026-10-19 19:05", frm="paolo", kind="misc",
         cc=["roberto", "merch-planning@valentino-retail.example", "facility-italy@valentino-retail.example"],
         subject="COU01 aggiornamento riapertura 27/11", body="""Bon, aggiornamento veloce da Courmayeur.
- la settimana scorsa ha nevicato sopra i 1800, in paese vuoto totale, aperti solo un paio di bar
- imbianchino confermato 2-6/11, merci facility
- personale: presa una ragazza di Pré-Saint-Didier con francese e inglese, parte il 16/11. Il secondo stagionale ancora da trovare, se qualche negozio ha qualcuno che vuole fare la stagione in montagna...
- Elisa rientra da Milano il 2/11, le hanno chiesto di restare per i cinesi
- allocazione inverno: da merch planning ancora nessuna risposta alla mail del 6. Mi serve sapere almeno le quantità di Aurea e Alpina per organizzare il magazzino, adesso abbiamo i piumini rimasti dall'estate e basta
- apertura confermata venerdì 27/11
Paolo"""),
]
