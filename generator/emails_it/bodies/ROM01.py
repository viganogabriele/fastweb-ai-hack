# ROM01 Roma Via Condotti - hand-authored closing emails (Aug 31 -> Oct 21 2026)
# Writers: Alessandra De Santis (SM), Fabio Cardarelli (assistant manager), Giorgia Proietti (SA, shared iPad / store mailbox)

PERSONAS = {
    "ale": "Alessandra De Santis <alessandra.desantis@valentino-retail.example>",
    "fabio": "Fabio Cardarelli <fabio.cardarelli@valentino-retail.example>",
    "giorgia": "Giorgia Proietti <giorgia.proietti@valentino-retail.example>",
    "store": "Valentino Roma Condotti <rom01.store@valentino-retail.example>",
    "roberto": "Roberto Galli <roberto.galli@valentino-retail.example>",
    "ops": "retail-ops-italy@valentino-retail.example",
    "facility": "facility-italy@valentino-retail.example",
    "merch": "merch-planning@valentino-retail.example",
}

DEFAULT_TO = ["ops"]
DEFAULT_CC = ["roberto"]

EMAILS = []

# ---------------------------------------------------------------- week 1 (pre-cantiere)
EMAILS += [
    dict(
        id="c0831", sent="2026-08-31 20:12", frm="ale", business_date="2026-08-31",
        subject="[ROM01] Report serale 31/08",
        body="""Buonasera a tutti,

Fatturato: 16,0k (budget 17,2k, -7%)
Ingressi: 104 | Scontrini: 13 | Conv. 12,5%
Note: lunedi tranquillo, ancora tanti italiani di rientro dalle ferie. Bene le t-shirt logo nere e l'hoodie grigio, 2 tricot cardigan neri a un signore svizzero. Una cliente ha chiesto la Aria rosa cipria in 2, non l'abbiamo mai ricevuta in quella taglia. Nova blu tg 5 a zero, segnalo.

Buona serata
Alessandra De Santis
Store Manager | Valentino Roma Via Condotti
Le informazioni contenute in questa e-mail sono riservate.""",
    ),
    dict(
        id="ooo0831", suffix="_ooo", sent="2026-08-31 20:12", frm="roberto", kind="ooo", reply_to_id="c0831",
        to=["ale"], cc=[],
        subject="Risposta automatica: [ROM01] Report serale 31/08",
        headers={"Auto-Submitted": "auto-replied"},
        body="""Sono fuori ufficio con accesso limitato alla posta fino a venerdì 4 settembre. Per urgenze contattare retail-ops-italy@valentino-retail.example.

I am out of office with limited access to email until Friday 4 September. For urgent matters please contact retail-ops-italy@valentino-retail.example.

Roberto Galli""",
    ),
    dict(
        id="c0902", sent="2026-09-02 20:05", frm="ale", business_date="2026-09-02",
        subject="[ROM01] Report serale 02/09",
        body="""Ciao,

Fatturato: 21,1k (budget 19,0k, +12%)
Ingressi: 138 | Scontrini: 11
Note: arrivata stamattina la consegna da CSG, 163 pz, tutto ok, sistemata entro le 13. Bella giornata con gli americani, 3 Fiammetta nere vendute (una coppia di Boston ne ha prese 2). Ieri sera non sono riuscita a mandare il report, scusate, ieri eravamo sotto i 10k comunque.

Alessandra""",
    ),
    dict(
        id="c0903", sent="2026-09-03 20:31", frm="fabio", business_date="2026-09-03",
        subject="chiusura roma 3/9",
        body="""ciao a tutti
22,6k su 25,8 di budget, -12%. 140 ingressi
vendute 2 Nova nere e 2 Vel neri, un signore ha chiesto il Cosimo nero in 6 ma nun c'e'.
tanti italiani oggi, qlc turco.
Fabio

Inviato da iPhone""",
    ),
    dict(
        id="c0904", sent="2026-09-04 20:18", frm="ale", business_date="2026-09-04",
        subject="[ROM01] Report serale 04/09",
        body="""Buonasera,

Fatturato: 29,3k (budget 29,9k, -2%)
Ingressi: 159 | Scontrini: 20 | Conv. 12,6%
Note: venerdi quasi a budget. Il Vel nero va fortissimo, 4 pezzi oggi, se continua cosi la tg 4 la finiamo entro la settimana prossima. Due clienti diversi hanno chiesto il Monteluce grigio in 4, ne abbiamo zero, possiamo chiedere qualcosa al magazzino? Un reso di una Vtrack donna 39, ripensamento.

Alessandra De Santis
Store Manager | Valentino Roma Via Condotti
Le informazioni contenute in questa e-mail sono riservate.""",
    ),
    dict(
        id="c0905", sent="2026-09-05 20:47", frm="ale", business_date="2026-09-05",
        subject="[ROM01] Report serale 05/09",
        body="""Sabato pieno, 251 ingressi, tanti italiani e un po' di tedeschi e americani.
Fatturato 38k contro 42,3 di budget, -10%. Ha girato molto l'accessorio (berretti e cappellini navy, t-shirt) ma pochi capi importanti, scontrino medio basso.
Una ragazza voleva la Nova verde oliva in 1, mancante.

Ale""",
    ),
    dict(
        id="c0906", sent="2026-09-06 20:02", frm="fabio", business_date="2026-09-06",
        subject="chiusura domenica",
        body="""domenica moscia, 19,8k vs 31 di budget (-37%). entrati 152 ma tanti giravano e basta, caldo
5 t-shirt logo nere e 4 jersey polo nere, quello si vende
reso di un tricot cardigan L, ha cambiato idea
1 cliente hoodie grigio XL che nn abbiamo

F.

Inviato da iPhone""",
    ),
    dict(
        id="c0907", sent="2026-09-07 20:24", frm="fabio", business_date="2026-09-07",
        subject="chiusura roma 7/9",
        body="""Ciao Roberto ciao a tutti, bentornato!
oggi 17,1k, budget 22,8. 138 ingressi
tanti americani, 4 Nova nere vendute tutte a americane. Una signora cercava l'Amalia marrone in 2, l'ha vista su instagram, nun ce l'abbiamo proprio, le ho preso il numero.
Ale e' di riposo, domani torna lei.
Fabio""",
    ),
    dict(
        id="c0908", sent="2026-09-08 20:15", frm="ale", business_date="2026-09-08",
        subject="[ROM01] Report serale 08/09",
        body="""Buonasera,

Fatturato: 26,4k (budget 22,1k, +20%)
Ingressi: 134 | Scontrini: 15
Note: ottimo martedi grazie a 4 Mistral neri e 3 Vtrack Gtx nere. Finita la Fiammetta nera tg 0, da riassortire se possibile. Clientela mista, italiani, tedeschi, qualche cinese.

Alessandra""",
    ),
    dict(
        id="c0909", sent="2026-09-09 20:09", frm="ale", business_date="2026-09-09",
        subject="[ROM01] Report serale 09/09",
        body="""Ciao,
giornata sotto, 17,5k vs 24,7 (-29%), 134 ingressi ma conversione bassa.
Come temevo il Vel nero in 4 e' finito e oggi un cliente lo cercava proprio in 4. Anche un Monteluce grigio in 5 richiesto e non disponibile. Vendute 2 Aurea nere.
Alessandra""",
    ),
    dict(
        id="c0910", sent="2026-09-10 20:40", frm="ale", business_date="2026-09-10",
        subject="[ROM01] Report serale 10/09",
        body="""Buonasera,

Fatturato: 27,5k (budget 26,7k, +3%)
Ingressi: 167 | Scontrini: 20 | Conv. 12%
Richieste non soddisfatte (tante oggi):
Aurea blu 00, Liviana bianca in 2, Nova oliva in 6, Cosimo nero 6 (di nuovo!), Vlogo Cardigan blu XXL
Note: 3 Aurea nere e 3 Vtrack nere vendute. Un gruppo di sauditi molto interessati al capospalla. Un cliente ha provato l'Artem in 5 e gli stava enorme, ha preso il 4. Finite Vtrack nere 44 e jersey polo nera S.

Alessandra De Santis
Store Manager | Valentino Roma Via Condotti
Le informazioni contenute in questa e-mail sono riservate.""",
    ),
    dict(
        id="c0911", sent="2026-09-11 20:55", frm="store", business_date="2026-09-11",
        subject="Chiusura ROM01 11/09",
        body="""Buonasera,
oggi fatturato 38,3k, budget 34,7k quindi +10%. Ingressi 214.
E' arrivata la consegna del magazzino (218 pezzi), doveva arrivare mercoledi, e' arrivata oggi. Abbiamo sistemato in back-office fino alle 15.
Venduti 3 tricot cardigan neri e tante t-shirt. Richiesti Fiammetta blu 3 e tricot cardigan grigio XL che non abbiamo.
Buona serata
Giorgia - ROM01""",
    ),
    dict(
        id="c0912", sent="2026-09-12 21:03", frm="ale", business_date="2026-09-12",
        subject="[ROM01] Report serale 12/09",
        body="""Buonasera,

Fatturato: 35,9k (budget 47,9k, -25%)
Ingressi: 219 | Scontrini: 23
Note: sabato con buon passaggio ma non abbiamo chiuso i capi grossi. Bene Vtrack nere e Mistral (3 neri + 2 blu). A zero ora: Mistral nero 3, vlogo cardigan blu S, jersey polo nera S, Vtrack nere 41 e 44. Le sneakers ci servono, ce le chiedono tutti i giorni.

Ale""",
    ),
    dict(
        id="c0913", sent="2026-09-13 20:10", frm="fabio", business_date="2026-09-13",
        subject="chiusura 13/9",
        body="""29,4k (budget 31,6) -7%, 171 ingressi
6 t-shirt nere, 4 Vel neri (il 4 e' rientrato con la consegna di venerdi)
1 signora cercava la Valdora nera in 00
domenica tranquilla, daje
Fabio

Inviato da iPhone""",
    ),
]

# ---------------------------------------------------------------- cantiere starts
EMAILS += [
    dict(
        id="c0914", sent="2026-09-14 20:38", frm="ale", business_date="2026-09-14",
        cc=["roberto", "facility"],
        subject="[ROM01] Report serale 14/09 - CANTIERE DAVANTI AL NEGOZIO",
        attachments=[{"name": "IMG_2231.jpg"}, {"name": "IMG_2232.jpg"}, {"name": "IMG_2234.jpg"}],
        body="""Buonasera a tutti,

devo segnalare una situazione molto seria. Stamattina alle 9:30 arrivando abbiamo trovato davanti al negozio un cantiere: transenne su tutto il marciapiede e parte della strada, operai che rompevano la pavimentazione e in piu' stanno montando un ponteggio su tutta la facciata del palazzo. Due vetrine su tre sono coperte da pannelli bianchi, l'ingresso si vede solo se ci passi esattamente davanti, chi arriva da Piazza di Spagna vede solo la recinzione.
Nessuno ci ha avvisato. Ne' il condominio ne' il Comune, niente. Ho chiamato il portiere che dice che "e' arrivata una lettera all'amministratore", a noi zero.

Fatturato: 11,5k (budget 24,3k, -53%)
Ingressi: 74 (lunedi scorso 138)
Scontrini: 13
Note: piu' della meta' della gente in meno, si vede a occhio. Chi e' entrato ha comprato (felpe nere, cappellini, hoodie) quindi la conversione e' alta ma i numeri sono questi. Rumore di martello pneumatico tutta la mattina, alcuni clienti sono usciti subito.
Richiesti vlogo cardigan blu S e Vtrack nera 41, entrambi a zero.

Allego 3 foto dell'ingresso e delle vetrine. Chiedo a facility se si puo' fare qualcosa per segnalare che siamo aperti. Domani provo a chiamare il Municipio.

Alessandra De Santis
Store Manager | Valentino Roma Via Condotti
Le informazioni contenute in questa e-mail sono riservate.""",
    ),
    dict(
        id="r0915a", suffix="_re1", sent="2026-09-15 08:14", frm="roberto", kind="reply", reply_to_id="c0914",
        to=["ale"], cc=["facility", "ops"],
        subject="Re: [ROM01] Report serale 14/09 - CANTIERE DAVANTI AL NEGOZIO",
        body="""Ale ho visto le foto, brutta storia.
Mi servono: ingressi di oggi e dei prossimi giorni confrontati con le stesse giornate della settimana scorsa, e una foto dell'ingresso presa da Piazza di Spagna, cosi' si capisce cosa vede il cliente.
E soprattutto quanto dura. Facility in copia, vedete voi se si puo' mettere un pannello o un totem.
R.

Inviato da iPhone""",
    ),
    dict(
        id="r0915b", suffix="_re2", sent="2026-09-15 12:47", frm="ale", kind="reply", reply_to_id="r0915a",
        to=["roberto"], cc=["facility", "ops"],
        subject="Re: [ROM01] Report serale 14/09 - CANTIERE DAVANTI AL NEGOZIO",
        attachments=[{"name": "IMG_2240.jpg"}, {"name": "IMG_2241.jpg"}],
        body="""Ciao Roberto,
ti allego due foto fatte stamattina dall'angolo con la piazza, come vedi del negozio si vede solo l'insegna in alto, e nemmeno tutta per via del ponteggio.

Ingressi: lunedi 14 74 contro 138 del lunedi prima. Ti mando ogni sera il confronto.

Durata: nessuno sa niente di preciso. Ho chiamato il Municipio I, mi hanno passato tre uffici e alla fine mi hanno detto che sono lavori di rifacimento della pavimentazione e dei sottoservizi, "fine ottobre" ma di scriverlo via PEC per avere info. Il ponteggio invece e' del condominio (rifanno la facciata), il capocantiere dice anche lui fine ottobre. Ho chiesto ai vigili se almeno si puo' lasciare un passaggio piu' largo davanti alla porta, mi hanno detto che passano a vedere.

Per facility: ci servirebbe con urgenza un pannello "siamo aperti / we are open" da attaccare alla recinzione, e se possibile un totem all'angolo con Piazza di Spagna. Possiamo anche pensare a una persona all'angolo nei weekend?

Grazie
Alessandra""",
    ),
    dict(
        id="c0915", sent="2026-09-15 20:21", frm="fabio", business_date="2026-09-15",
        subject="chiusura roma 15/9",
        body="""aho oggi 'na desolazione.
8,5k su 23,9 di budget, -64%. 68 ingressi, martedi scorso erano 134
il cantiere e' sempre la, oggi pure col trapano che faceva tremare i vetri. i clienti passano, vedono le transenne e tirano dritto verso piazza di spagna
venduti solo berretti, 1 belt bag, 1 felpa. 1 cliente cercava la Valdora nera 00 (la stessa di domenica? boh)
mo' vediamo domani
Fabio

Inviato da iPhone""",
    ),
    dict(
        id="fwd0916", suffix="_fwd", sent="2026-09-16 11:08", frm="ale", kind="fwd",
        to=["roberto", "facility"], cc=["ops"],
        subject="I: Condominio Via Condotti - avvio lavori facciata e comunicazione cantiere comunale",
        body="""Roberto, facility,
vi giro quello che mi ha mandato STAMATTINA l'amministratore del condominio, dopo che ieri gli ho telefonato. Notate la data: 10 settembre. Era stata mandata solo alla proprieta' dei muri e nessuno l'ha girata a noi.
Quindi fine prevista "fine ottobre" per il Comune e 7 settimane per il ponteggio. Vedremo.

Ale

---------- Messaggio inoltrato ----------
Da: Studio Ferrante Amministrazioni <segreteria@studioferrante-amm.example>
Data: gio 10 set 2026 alle ore 17:42
Oggetto: Condominio Via Condotti - avvio lavori facciata e comunicazione cantiere comunale
A: <condomini-condotti@studioferrante-amm.example>

Gentili Condomini,

con la presente si comunica che lunedi 14 settembre 2026 avranno inizio i lavori di manutenzione straordinaria della facciata dello stabile deliberati nell'assemblea del 22 giugno u.s., con installazione di ponteggio su tutto il fronte strada. Durata stimata dei lavori: 7 settimane circa, salvo condizioni meteo avverse.

Si informa inoltre che, come comunicato da Roma Capitale - Municipio I, nello stesso periodo e' previsto il cantiere comunale per il rifacimento della pavimentazione e dei sottoservizi nel tratto di Via Condotti antistante lo stabile, con delimitazione dell'area mediante transenne e recinzioni. Fine lavori comunicata: fine ottobre 2026.

Durante i lavori l'accesso pedonale agli esercizi commerciali sara' garantito. Si prega di non sostare in prossimita' del ponteggio.

Cordiali saluti
Rag. Stefano Ferrante
Studio Ferrante Amministrazioni""",
    ),
    dict(
        id="c0916", sent="2026-09-16 20:26", frm="ale", business_date="2026-09-16",
        subject="[ROM01] Report serale 16/09",
        body="""Buonasera,

Fatturato: 13,3k (budget 26,1k, -49%)
Ingressi: 70 | Scontrini: 15 | Conv. 21%
Cantiere: giorno 3. Polvere ovunque, abbiamo pulito le vetrine dentro due volte e passato i capi esposti vicino alla porta. Il corriere della consegna CSG (243 pz, puntuale almeno) non poteva arrivare con il furgone davanti, hanno scaricato su Via Belsiana e abbiamo portato i colli a mano con i carrelli.
Note: 4 Iridia neri venduti, bene. Un reso Artem 4 e un reso Vtrack 44 per taglia. La conversione e' altissima perche' entra solo chi ci cerca apposta.

Alessandra""",
    ),
    dict(
        id="c0917", sent="2026-09-17 20:08", frm="fabio", business_date="2026-09-17",
        subject="chiusura 17/9",
        body="""16,1k vs 30,5 (-47%), 83 ingressi
vendute 2 Aurea blu e 2 vlogo cardigan blu
polvere sui capi in vetrina, pure sulle borse, ce stanno a sotterra'. gli operai iniziano alle 7:30, quando arriviamo e' gia' tutto bianco
facility ancora niente x il cartello
F.

Inviato da iPhone""",
    ),
    dict(
        id="c0918", sent="2026-09-18 20:44", frm="ale", business_date="2026-09-18",
        subject="[ROM01] Report serale 18/09",
        body="""Buonasera,

Fatturato: 28,7k (budget 36,2k, -21%)
Ingressi: 94 (venerdi scorso 214)
Cantiere: invariato. Oggi due clienti al telefono non trovavano l'ingresso, uno ha girato intorno al palazzo da Via Mario de' Fiori. Abbiamo stampato noi un foglio A3 "Valentino e' aperto - entrata qui" e l'abbiamo attaccato alla transenna con lo scotch, ma i vigili ci hanno detto di toglierlo perche' non autorizzato.
Note: giornata salvata da un cliente svizzero (3 hoodie neri + 2 tricot cardigan). Per il resto poco.

Facility, avete novita' sul pannello? Ho scritto martedi.

Alessandra De Santis
Store Manager | Valentino Roma Via Condotti
Le informazioni contenute in questa e-mail sono riservate.""",
    ),
    dict(
        id="c0919", sent="2026-09-19 21:06", frm="ale", business_date="2026-09-19",
        subject="[ROM01] Report serale 19/09",
        body="""Ciao,
sabato 35,4k contro 54,1 di budget (-35%). Ingressi 146, sabato scorso 219 e di solito in settembre stiamo sopra i 230.
Cantiere: il sabato gli operai non ci sono ma le transenne e i pannelli restano, quindi cambia poco.
Vendute 3 Nova blu e 2 nere, 2 Valdora nere. Emiratini e tedeschi.
Ale""",
    ),
    dict(
        id="c0920", sent="2026-09-20 20:19", frm="fabio", business_date="2026-09-20",
        subject="chiusura domenica 20",
        body="""14,5k, budget 37,5 -> -61%
92 ingressi, 'na cifra di americani pero' guardano e se ne vanno
3 Iridia neri, 2 cable knit
reso Aria 3 per difetto (cucitura scucita sulla tasca) e reso Fiammetta 4 regalo
mo' basta, a domani
F.

Inviato da iPhone""",
    ),
    dict(
        id="c0921", sent="2026-09-21 20:33", frm="store", business_date="2026-09-21",
        subject="Chiusura ROM01 21/09",
        body="""Buonasera,
oggi fatturato 25,4k, budget 27,6k. Ingressi solo 61.
Per fortuna e' arrivato un gruppo di clienti cinesi mandati dal concierge dell'hotel, hanno comprato 2 Aurea blu e 2 Liviana bianche. Anche qualche coreano.
Il cantiere sempre uguale, oggi hanno chiuso con le transenne anche meta' dell'ingresso per un'ora.
Giorgia - ROM01""",
    ),
]

# ---------------------------------------------------------------- end of September
EMAILS += [
    dict(
        id="c0923", sent="2026-09-23 21:12", frm="ale", business_date="2026-09-23",
        cc=["roberto", "merch"],
        subject="ROM01 report 23/09 + richiesta revisione budget",
        body="""Buonasera,

fatturato 18,3k su 29,5k di budget (-38%), ingressi 76. E' il settimo giorno di fila sotto del 40-60% di traffico, non e' piu' un caso.

Riassumo la situazione perche' ieri non sono riuscita a scrivere (giornata pessima, 15k e 70 ingressi):
- il cantiere comunale e il ponteggio coprono ancora 2 vetrine su 3. Il contapersone dice che entriamo circa la meta' delle persone rispetto a prima del 14.
- facility ha risposto solo "stiamo valutando" per il pannello e il totem. Intanto i vigili ci hanno fatto togliere il cartello fatto da noi.
- sono andata personalmente da Hassler, de Russie e d'Inghilterra a parlare con i concierge e lasciare il biglietto con le indicazioni per arrivare all'ingresso. Ci mandano gente ma non basta.
- i negozi da Piazza di Spagna in giu e quelli dall'altro lato della via lavorano normalmente, ci ho fatto un giro in pausa: pieni. E' solo il nostro tratto.

Chiedo formalmente che il budget di settembre e ottobre venga rivisto o almeno che si tenga conto di questo nei risultati del team. I ragazzi stanno lavorando il doppio per vendere la meta'.

Richieste di oggi che non abbiamo: Nova blu 1, Artem nero 6, t-shirt logo bianca S e blu XXL.

Alessandra De Santis
Store Manager | Valentino Roma Via Condotti
Le informazioni contenute in questa e-mail sono riservate.""",
    ),
    dict(
        id="r0924", suffix="_re1", sent="2026-09-24 09:02", frm="roberto", kind="reply", reply_to_id="c0923",
        to=["ale"], cc=["merch", "ops"],
        subject="Re: ROM01 report 23/09 + richiesta revisione budget",
        body="""Ale capito. Il budget non lo cambio io, ho girato a merch-planning con i tuoi numeri di traffico. Per il team ne parliamo io e te, tranquilla.
Sollecito facility oggi. Settimana prossima passo a vedere.
Tieni duro
Roberto

Inviato da iPhone""",
    ),
    dict(
        id="c0924", sent="2026-09-24 20:17", frm="fabio", business_date="2026-09-24",
        subject="chiusura 24/9",
        body="""oh finalmente 'na giornata decente: 32,9k su 36,1, -9%
115 ingressi
4 Aria nere, 3 Mistral neri, 2 Vtrack donna. sauditi e americani
finita la t-shirt logo blu in L, un cliente la voleva
il trapano oggi ha smesso alle 3, s'e' sentito
Fabio

Inviato da iPhone""",
    ),
    dict(
        id="c0925", sent="2026-09-25 20:52", frm="ale", business_date="2026-09-25",
        subject="ROM01 report 25/09",
        body="""Buonasera,

venerdi da dimenticare: 15,4k contro 44,1k di budget (-65%). Ingressi 113 ma tanti erano gente che entrava a chiedere dov'era il bagno o la strada per Trinita' dei Monti perche' il percorso era deviato.
Cantiere: oggi carotatrice tutto il giorno, abbiamo dovuto alzare la musica e comunque non si parlava. Una cliente americana e' uscita dicendo che non riusciva a provare con quel rumore.

Due cambi taglia sull'Artem, da 5 a 4 e da 6 a 5: veste grande, ormai consigliamo sempre una taglia in meno. Vendute 2 balaclava Astra nere e 2 vlogo cardigan blu.
Richieste: Nova oliva 6, Alpina nera 35.

Alessandra""",
    ),
    dict(
        id="c0926", sent="2026-09-26 21:15", frm="fabio", business_date="2026-09-26",
        subject="chiusura sabato 26/9",
        body="""ciao
sabato 31,5k su 62 di budget, -49%. 146 ingressi, nun e' un sabato.
consegna CSG arrivata oggi, doveva essere mercoledi. il corriere BRT dice che mercoledi e' passato ma non trovava dove fermarsi per le transenne e se n'e' andato senza chiamarci. 176 pz, tt sistemato in serata
venduto poco di importante, jersey polo, t-shirt, cappellini
F.

Inviato da iPhone""",
    ),
    dict(
        id="c0927", sent="2026-09-27 20:04", frm="fabio", business_date="2026-09-27",
        subject="chiusura domenica 27",
        body="""17,9k (budget 43,7) -59%, 97 ingressi
3 jersey polo nere, 2 tricot cardigan, qualche brasiliano
oggi niente operai ma i pannelli stanno sempre la. 2 signore mi hanno detto che pensavano fossimo chiusi x ristrutturazione
F.

Inviato da iPhone""",
    ),
    dict(
        id="c0927dup", sent="2026-09-27 20:06", frm="fabio", business_date="2026-09-27", kind="dup", suffix="_dup",
        subject="chiusura domenica 27",
        body="""17,9k (budget 43,7) -59%, 97 ingressi
3 jersey polo nere, 2 tricot cardigan, qualche brasiliano
oggi niente operai ma i pannelli stanno sempre la. 2 signore mi hanno detto che pensavano fossimo chiusi x ristrutturazione
F.

Inviato da iPhone""",
    ),
    dict(
        id="c0928", sent="2026-09-28 20:29", frm="ale", business_date="2026-09-28",
        subject="ROM01 report 28/09",
        body="""Ciao,
14,5k vs 33,8 (-57%), ingressi 87.
Segnalo un reso di un Vel (tg 4): il cursore della zip si e' staccato dopo due settimane. Il cliente era gentile ma non contento, abbiamo fatto il reso pieno. Teniamo d'occhio.
Per il resto berretti blu e t-shirt, poco altro. Totem/pannello ancora niente.
Alessandra""",
    ),
    dict(
        id="c0929", sent="2026-09-30 08:47", frm="fabio", business_date="2026-09-29",
        subject="chiusura 29/9 (ieri)",
        body="""scusate ieri sera mi si e' scaricato il telefono e il pc del back-office era gia' spento
29/9: 7,4k su 31,9 di budget, -77%. peggior giornata da quando sto qua. 78 ingressi, quasi tutti italiani
2 resi Vel per la zip rotta, tg 3 e tg 2, stessa cosa di lunedi: il cursore si sfila. con quello di Ale sono 3 in due giorni, c'e' qualcosa che nun va col lotto
pure reso Riviera 5 per qualita' e Nova 4 per taglia
venduti 2 Astra Cape, bianca e nera
Fabio

Inviato da iPhone""",
    ),
    dict(
        id="c0930", sent="2026-09-30 20:41", frm="ale", business_date="2026-09-30",
        subject="ROM01 report 30/09",
        body="""Buonasera,

Fatturato: 24,0k (budget 36,6k, -34%)
Ingressi: 86
Cantiere: oggi ho parlato con il capocantiere del Comune. Mi ha detto che "fine ottobre e' difficile, diciamo novembre" perche' hanno trovato un problema con le tubature sotto il selciato. Il ponteggio del condominio resta finche' non finiscono loro. Quindi altro mese cosi.
Note: consegna CSG 204 pz arrivata puntuale (questa volta il corriere ci ha chiamato prima, grazie). Un altro Vel con la zip rotta (tg 3), siamo a 4. Chiedo se qualcuno puo' dirci se e' un problema noto e se dobbiamo togliere i Vel dalla vendita.
2 Liviana bianche vendute.

Alessandra De Santis
Store Manager | Valentino Roma Via Condotti
Le informazioni contenute in questa e-mail sono riservate.""",
    ),
]

# ---------------------------------------------------------------- early October
EMAILS += [
    dict(
        id="c1001", sent="2026-10-01 20:23", frm="ale", business_date="2026-10-01",
        subject="ROM01 report 01/10",
        body="""Ciao,
32,0k su 41,1 di budget (-22%), 97 ingressi, conversione sopra il 20%, chi entra e' motivato.
3 Iridia neri, 3 Vtrack donna bianco latte, 2 Aurea blu. Tedeschi.
Ennesimo Vel reso per la zip (tg 4).
Domani viene Roberto, almeno vede con i suoi occhi.
Ale""",
    ),
    dict(
        id="c1002", sent="2026-10-02 21:01", frm="ale", business_date="2026-10-02",
        subject="ROM01 report 02/10",
        body="""Buonasera,

oggi visita di Roberto nel pomeriggio, grazie per essere passato. Abbiamo fatto insieme il giro da Piazza di Spagna e credo sia stato chiaro a tutti che dall'angolo il negozio non esiste.

Fatturato 29,6k (budget 44,4k, -33%). Ingressi 150, il venerdi un po' meglio.
Finita la Aurea nera in 1, e' una delle taglie che vendiamo di piu'. Il magazzino ne ha?
Scontrini 18, bene sciarpe e cappellini, 2 Iridia neri, 2 Mistral.

Alessandra""",
    ),
    dict(
        id="r1002", suffix="_re1", sent="2026-10-02 22:18", frm="roberto", kind="reply", reply_to_id="c1002",
        to=["ale"], cc=["facility", "merch", "ops"],
        subject="Re: ROM01 report 02/10",
        body="""Grazie Ale e grazie ai ragazzi.
Visto di persona e' peggio di come sembra dalle foto. Chi arriva da piazza di Spagna non capisce che siamo aperti.
Facility: entro la settimana prossima totem "aperti" all'angolo e pannello sulla recinzione, permessi li gestite voi col Municipio. Per i weekend fino a fine lavori mettiamo una hostess all'angolo, Ale mi mandi gli orari.
Merch-planning: ROM01 sta facendo -50% di traffico da tre settimane per cause esterne, fine lavori non prima di novembre. Vi chiedo di tenerne conto nel budget di ottobre e nella previsione, ne parliamo lunedi.
R.""",
    ),
    dict(
        id="c1003", sent="2026-10-03 21:22", frm="fabio", business_date="2026-10-03",
        subject="chiusura sabato 3/10",
        body="""sabato: 34,7k su 68,1 di budget, 168 ingressi
4 Nova nere, 3 zaini Urban Backpack, 3 Vel bianchi (quelli bianchi nun si rompono? speriamo)
reso Vel 4 zip, e reso Aria 0 per taglia
1 cliente chiedeva l'Artem nero in 7, gli ho detto che veste grande e che il 6 gli andava bene, nun s'e' convinto
F.

Inviato da iPhone""",
    ),
    dict(
        id="corr1003", sent="2026-10-03 21:40", frm="fabio", business_date="2026-10-03", kind="correction",
        suffix="_corr", reply_to_id="c1003",
        subject="Re: chiusura sabato 3/10",
        body="""scusate ho invertito i numeri, il fatturato era 43,7k non 34,7. quindi -36% sul budget
F.

Inviato da iPhone""",
    ),
    dict(
        id="c1004", sent="2026-10-04 20:13", frm="fabio", business_date="2026-10-04",
        subject="chiusura dom 4/10",
        body="""24,9k budget 46,4 (-46%), 106 ingressi
4 Vtrack donna nere, 3 tricot cardigan, 2 Artem neri (preso uno piu' piccolo come sempre)
reso Mistral 4 per taglia
richiesto Cortina XL, niente
Aurea nera ormai finita pure in 0, restano 5 pezzi sparsi
Fabio""",
    ),
    dict(
        id="c1005", sent="2026-10-05 20:37", frm="store", business_date="2026-10-05",
        subject="Chiusura ROM01 05/10",
        body="""Buonasera,
fatturato 14,6k (budget 33,5k). Ingressi 79.
Tanti giapponesi oggi, piu' di un quarto dei clienti, hanno comprato soprattutto accessori e 2 Cosimo neri.
Il cantiere oggi ha ricominciato a scavare proprio davanti alla porta, per due ore siamo entrati da una passerella di legno.
Giorgia - ROM01""",
    ),
    dict(
        id="c1006", sent="2026-10-06 20:49", frm="ale", business_date="2026-10-06",
        subject="ROM01 report 06/10",
        body="""Ciao,
18,7k vs 35,9k (-48%), 91 ingressi.
Una cliente coreana voleva la Aurea nera in 1, in nero ci restano solo pezzi singoli in 00, 2, 3 e 4. Ho chiamato CSG: zero in nero 0 e 1, "forse meta' mese". Le ho proposto la blu, niente, voleva quella nera.
Venduti 3 marsupi Vita Belt Bag e 2 berretti rosa cipria. Reso Vtrack donna 38 per taglia.
Facility mi ha confermato il totem per domani. Speriamo.
Alessandra""",
    ),
    dict(
        id="c1007", sent="2026-10-07 20:31", frm="ale", business_date="2026-10-07",
        subject="ROM01 report 07/10",
        body="""Buonasera,

Fatturato: 29,4k (budget 37,7k, -22%)
Ingressi: 101 | Conv. 19%
Cantiere: e' arrivato il totem "Valentino - siamo aperti / we are open" all'angolo con Piazza di Spagna e un pannello stampato sulla recinzione davanti alle vetrine. Finalmente. Vediamo nei prossimi giorni se cambia qualcosa sugli ingressi.
Note: consegna 222 pz ok, ma niente Aurea nere. Altra richiesta oggi Aurea nera tg 1. 2 Alpina nere vendute.

Alessandra De Santis
Store Manager | Valentino Roma Via Condotti
Le informazioni contenute in questa e-mail sono riservate.""",
    ),
    dict(
        id="c1008", sent="2026-10-08 20:16", frm="fabio", business_date="2026-10-08",
        subject="chiusura 8/10",
        body="""28k su 43,1, -35%. 125 ingressi, col totem qlc in piu' forse
4 Aurea beige vendute, la gente vuole la nera ma se non c'e' qualcuna si accontenta
a Milano hanno i cinesi della golden week, qua col cantiere nemmeno quelli
F.

Inviato da iPhone""",
    ),
    dict(
        id="c1009", sent="2026-10-09 20:58", frm="ale", business_date="2026-10-09",
        subject="ROM01 report 09/10",
        body="""Buonasera,
36,2k contro 51,2k di budget (-29%), 110 ingressi ma conversione al 20%. 4 Iridia neri, 2 vlogo cardigan blu, americani e inglesi.
Ancora una richiesta di Aurea nera in 1. E ancora un Vel reso per la zip (tg 3).

Oggi mi ha chiamato Milano Montenapoleone: cercano il vlogo cardigan in M, loro l'hanno finito ieri e il magazzino non ne ha. Noi in blu M ne abbiamo 5, ma con la situazione che abbiamo li vendiamo anche noi e comunque senza l'ok di Roberto non spedisco niente. Gli ho detto di sentire lui. Roberto, se mi dici di mandarne 1 o 2 lo faccio.

Alessandra""",
    ),
]

# ---------------------------------------------------------------- mid October
EMAILS += [
    dict(
        id="c1011", sent="2026-10-11 20:44", frm="fabio", business_date="2026-10-10,2026-10-11",
        subject="chiusura sabato + domenica",
        body="""ciao a tutti, ieri sera ho chiuso tardi e nun ho mandato niente, faccio tutto insieme

sabato 10: 56,4k su 69,4 (-19%), 192 ingressi! miglior giornata da quando c'e' il cantiere. c'era la hostess all'angolo con l'ombrello e il volantino, e il totem. funziona daje
6 Nova nere, 4 Aria nere, 3 Aurea blu, 3 hoodie neri. tanti americani
1 Aurea nera tg1 richiesta, sempre quella
2 resi Iridia tg 2 (uno taglia, uno ripensamento)

domenica 11: 23,3k su 51,9, -55%. 123 ingressi. hostess c'era pure oggi ma la domenica mattina sta via e' 'n deserto
richiesto Mistral blu 3, finito
reso 1 Vel 5, ha cambiato idea, zip a posto

Fabio

Inviato da iPhone""",
    ),
    dict(
        id="c1012", sent="2026-10-12 20:27", frm="ale", business_date="2026-10-12",
        subject="ROM01 report 12/10",
        body="""Ciao,
15,3k vs 38,0k (-60%). Ingressi 104, il lunedi senza hostess si torna giu'.
Altro Vel per la zip, tg 4. Ho perso il conto, credo 8 dall'inizio. Nessuno ci ha ancora detto niente, li continuiamo a vendere?
Qualche coreano e un paio di clienti degli Emirati, comprato poco.
Roberto, sul cardigan per Milano non mi hai risposto, per ora non ho mandato niente.
Ale""",
    ),
    dict(
        id="c1013", sent="2026-10-13 20:35", frm="store", business_date="2026-10-13",
        subject="Chiusura ROM01 13/09",
        body="""Buonasera,
fatturato 12,7k, budget 37,9k. Ingressi 79.
Giornata molto lenta, rumore forte fino alle 17 (stanno tagliando le pietre).
Una cliente francese ha chiesto la Aurea nera taglia 1, non c'e'. Vendute 2 Nova blu e 2 Liviana.
Giorgia - ROM01""",
    ),
    dict(
        id="c1014", sent="2026-10-14 21:05", frm="ale", business_date="2026-10-14",
        subject="ROM01 report 14/10",
        body="""Buonasera,

Fatturato: 28,5k (budget 39,9k, -29%)
Ingressi: 98
Cantiere: nuova data. Il capocantiere oggi mi ha detto "6 novembre" per togliere le transenne, poi una settimana per smontare il ponteggio. Siamo passati da fine ottobre a novembre a 6 novembre, non so piu' a cosa credere. Facility, la hostess si puo' prolungare almeno fino al weekend dell'8?
Note: consegna 252 pz, di nuovo zero Aurea nere. Oggi una cliente la voleva in 0. Bene la Astra (2 balaclava, oversized, cape bianca), clientela cinese ed emiratina.

Alessandra De Santis
Store Manager | Valentino Roma Via Condotti""",
    ),
    dict(
        id="c1015", sent="2026-10-15 20:11", frm="fabio", business_date="2026-10-15",
        subject="chiusura 15/10",
        body="""21,8k su 44,8 -51%, 93 ingressi
3 Nova blu, 2 hoodie neri, 2 Cosimo
reso Mistral 5 qualita' (piuma che esce dalla cucitura)
domani sciopero generale, metro e bus fermi. vediamo chi arriva, io vengo in motorino
F.

Inviato da iPhone""",
    ),
    dict(
        id="c1016", sent="2026-10-16 20:39", frm="ale", business_date="2026-10-16",
        subject="ROM01 report 16/10 - sciopero",
        body="""Buonasera,

giornata difficile. Sciopero generale: ATAC ha fermato metro e bus dopo le 8:45, Giorgia e' arrivata alle 11 a piedi da San Giovanni e un'altra collega non e' proprio riuscita a venire. Abbiamo aperto alle 10 in due.

Fatturato 17,2k contro 55,9k di budget (-69%). Ingressi 97, pochi romani, qualche turista cinese e coreano a piedi.
Ancora Aurea nera in 1 richiesta. Reso di una Aurea tg 1 per taglia, le stava stretta.
4 Aria nere vendute.

Tra cantiere e sciopero non ci manca niente.
Alessandra""",
    ),
    dict(
        id="c1017", sent="2026-10-17 21:34", frm="ale", business_date="2026-10-17",
        cc=["roberto", "merch"],
        subject="ROM01 report 17/10",
        body="""Buonasera,

sabato 32,8k contro 75,2k di budget, -56%. Ingressi 202 grazie alla hostess, ma la conversione e' sotto il 10%: entrano, chiedono la Aurea nera e se ne vanno.

Oggi 3 clienti diverse ci hanno chiesto la Aurea nera in 1 e una in 3. Abbiamo nero solo in 2 e 4. Le ho messe in lista d'attesa. Sono settimane che la chiedono, CSG continua a dire "in arrivo".

Vedo che il budget di ottobre sul sistema e' ancora quello originale. Dopo la visita di Roberto ci era stato detto che merch-planning lo avrebbe considerato. Siamo a -45/50% da 5 settimane per un cantiere che non dipende da noi e il team lo vede tutte le mattine sul report. Vorrei una risposta, anche negativa.

Vendute 3 Ettore nere e 2 Aurea beige. Resi: Nova 4 taglia, Vel 6 ripensamento, un cable knit regalo, un Vita Belt Bag.

Alessandra De Santis
Store Manager | Valentino Roma Via Condotti
Le informazioni contenute in questa e-mail sono riservate.""",
    ),
    dict(
        id="c1018", sent="2026-10-18 20:22", frm="fabio", business_date="2026-10-18",
        subject="chiusura dom 18/10",
        body="""37k su 54,2, -32%, 147 ingressi. hostess + domenica = gente
4 Aria nere, 4 Nova nere, 3 Aurea beige
Aurea nera: chiesta in 2 e in 3, mo' abbiamo finito pure la 2, ci resta solo qlc 4
1 cliente chiedeva l'Amalia cioccolato in 0, mai vista qui
daje che ce la famo
Fabio

Inviato da iPhone""",
    ),
    dict(
        id="c1019", sent="2026-10-19 20:46", frm="store", business_date="2026-10-19",
        to=["retail-ops-spain@valentino-retail.example"],
        subject="Chiusura ROM01 19/10",
        body="""Buonasera,
fatturato 20,7k, budget 41,9k. Ingressi 108.
Venduti 2 Vel bianchi, 2 cape Astra (nera e bianca), berretti bianchi. Clienti americani e coreani.
Oggi gli operai hanno messo nuove transenne anche sul lato di Via Mario de' Fiori.
Giorgia - ROM01""",
    ),
    dict(
        id="c1020", sent="2026-10-20 20:18", frm="ale", business_date="2026-10-20",
        subject="report roma 20/10",
        body="""9,9k. Budget 41,2k. 77 ingressi.
Martello pneumatico dalle 8 alle 18 proprio sotto la vetrina centrale. 3 resi (Aria 0 taglia, cable knit colore, Vtrack 42) quindi il netto e' ancora piu' basso.
Non ho altro da aggiungere.
A.

Inviato da iPhone""",
    ),
    dict(
        id="c1021", sent="2026-10-21 20:57", frm="ale", business_date="2026-10-21",
        subject="ROM01 report 21/10",
        body="""Buonasera,

finalmente una buona notizia: nella consegna di oggi (254 pz) sono arrivate le Aurea nere, tutta la scala dal 00 al 4, 12 pezzi in tg 1. Ho gia' chiamato le clienti in lista d'attesa, 3 passano domani.

Fatturato 30,7k (budget 43,1k, -29%), 110 ingressi. 3 Nova nere, 2 jersey polo, 2 Riviera nere.

Cantiere: confermato 6 novembre per le transenne. Totem e hostess restano, grazie facility.
Roberto, per Milano poi non e' stato mandato nessun cardigan, giusto per chiudere il punto.

Alessandra""",
    ),
]
