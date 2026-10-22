# MIL01 Milano Montenapoleone - hand-written closing emails (Aug 31 -> Oct 21 2026)
# Writers: Giulia Ferrandi (SM), Marco Pellizzari (assistant mgr), Sara Kim (senior SA, Korean clients),
# shared iPad mailbox. Area manager replies: Roberto Galli.

PERSONAS = {
    "giulia": "Giulia Ferrandi <giulia.ferrandi@moncler-retail.example>",
    "marco": "Marco Pellizzari <marco.pellizzari@moncler-retail.example>",
    "sara": "Sara Kim <sara.kim@moncler-retail.example>",
    "store": "MIL01 Montenapoleone <mil01.store@moncler-retail.example>",
    "roberto": "Roberto Galli <roberto.galli@moncler-retail.example>",
    "ops": "retail-ops-italy@moncler-retail.example",
    "merch": "merch-planning@moncler-retail.example",
    "vm": "vm-team@moncler-retail.example",
    "mil02": "MIL02 Rinascente <mil02.store@moncler-retail.example>",
    "rom01": "ROM01 Roma <rom01.store@moncler-retail.example>",
}
DEFAULT_TO = ["ops"]
DEFAULT_CC = ["roberto"]

EMAILS = []

# ---------------------------------------------------------------- week 1
EMAILS += [
    dict(
        id="c0831", sent="2026-08-31 20:42", frm="marco", subject="chiusura 31/08",
        business_date="2026-08-31", kind="closing",
        body="""ciao a tutti,
chiusura ok. fatturato 38,2k vs bdg 32k, bene x essere un lunedi di fine agosto.
ancora tanti turisti, giapponesi e coreani soprattutto, italiani pochi che sono ancora al mare.
arrivata la consegna che aspettavamo sabato (165 pz), sistemata quasi tutta in back-office, domani finiamo noi del mattino.
un signore ha chiesto il Marin blu in 7, nn c'era.

buona serata
Marco
""",
    ),
    dict(
        id="ooo0831", sent="2026-08-31 20:42", frm="roberto", subject="Risposta automatica: chiusura 31/08",
        to=["marco"], cc=[], reply_to_id="c0831", kind="ooo", suffix="_ooo",
        headers={"Auto-Submitted": "auto-replied"},
        body="""Sono fuori ufficio con accesso limitato alla posta fino a venerdì 4 settembre.
Per urgenze contattare retail-ops-italy@moncler-retail.example.

I am out of office with limited email access until Friday 4 September.
For urgent matters please contact retail-ops-italy@moncler-retail.example.

Roberto Galli
""",
    ),
    dict(
        id="c0901", sent="2026-09-01 20:25", frm="giulia", subject="Chiusura MIL01 - 01/09",
        business_date="2026-09-01", kind="closing",
        body="""MIL01 MONTENAPOLEONE - CHIUSURA 01/09/2026

Fatturato netto: 33.978 EUR (bdg 30.140) +12,7%
Ingressi: 253 | Scontrini: 30 | Conv: 11,9% | UPT 1,3
Nazionalita': IT, CN, poi indiani e inglesi

Best: cardigan logo blu e nero (9 pz in tutto), t-shirt logo
Note: rientrato quasi tutto il team dalle ferie. Domattina briefing ore 9:30 sulla collezione nuova, giovedi sera cambio vetrina con VM.

Giulia Ferrandi
Store Manager - Moncler Milano Montenapoleone
Via Monte Napoleone 1, 20121 Milano
Le informazioni contenute in questa e-mail sono riservate e destinate esclusivamente al destinatario.
""",
    ),
    dict(
        id="c0902", sent="2026-09-02 20:58", frm="giulia", subject="Chiusura MIL01 - 02/09",
        business_date="2026-09-02", kind="closing",
        body="""MIL01 - CHIUSURA 02/09

Fatturato: 26,2k vs 32,7 (-20%)
Ingressi 301, scontrini 22

Giornata fiacca, tanta gente che entra a guardare e poi va. Ancora il cardigan logo che si vende da solo (4 blu).
Arrivata consegna 150 pz puntuale.
1 reso beanie (cambio idea).

Giulia
""",
    ),
    dict(
        id="c0904", sent="2026-09-04 21:10", frm="giulia", subject="Chiusura MIL01 - 04/09",
        business_date="2026-09-04", kind="closing",
        body="""Ciao,
ieri sera non sono riuscita a mandare la chiusura, scusate. Giovedi 30,8k, -34% sul budget, giornata morta: tanti americani a fare foto e basta.

Oggi meglio:
Fatturato: 62,6k vs 56k bdg (+12%)
Ingressi 488 / 35 scontrini / conv 7,2%

Venduto bene il Maire blu (4), Flammette nera 4. Tanti italiani rientrati, finalmente qualche cliente del client book che torna dalle vacanze.
Vetrina nuova montata ieri sera, viene bene, domani mando foto a VM.
Una signora cercava la polo bianca in L, finita.

Buon weekend
Giulia
""",
    ),
    dict(
        id="c0905", sent="2026-09-05 21:35", frm="giulia", subject="Chiusura MIL01 - sabato 05/09",
        business_date="2026-09-05", kind="closing",
        body="""Sabato pieno, finalmente!

Fatturato 87,4k (bdg 77,3) +13%
Ingressi 611, scontrini 51

Il Tib nero e' andato a ruba, 9 pezzi, quasi tutti uomini italiani. Bene anche le Trailgrip nere (6) e il Bady rosa.
Finito il cardigan logo blu in S.
Chiesta Trailgrip grigia in 46, non ce l'abbiamo mai avuta in quella misura.

Domani c'e' Marco.
G.

Inviato da iPhone
""",
    ),
    dict(
        id="c0906", sent="2026-09-06 20:15", frm="marco", subject="chiusura dom 6/9",
        business_date="2026-09-06", kind="closing",
        body="""ciao
50,6k vs 55,8 bdg, -9%. domenica cosi cosi, tanti cinesi (1 su 5 circa) ma comprano poco, guardano tanto la maglieria. cable knit nero 6 pz.
consegna arrivata con 1 giorno di ritardo, 241 pz, il ragazzo del corriere dice che venerdi avevano il camion pieno.
3 resi: una Maire tg 1 (ci ha ripensato), felpa hoodie M, trailgrip regalo.
ciao
Marco

Inviato da iPhone
""",
    ),
    dict(
        id="c0907", sent="2026-09-07 20:30", frm="marco", subject="chiusura 7/9",
        business_date="2026-09-07", kind="closing",
        body="""36,8k (bdg 42,2) -13%. lunedi lento.
qlc richiesta di taglie che nn abbiamo: Bady rosa 4, Maya verde oliva 6, Montcla blu 6, Valbourg bianco 2. tutte singole, niente di che.
reso un Arneb in 3, il cliente dice che gli stava enorme di spalle. lo segnalo xke' e' nuovo e nn so ancora come veste.
Marco
""",
    ),
    dict(
        id="c0908", sent="2026-09-09 08:52", frm="giulia", subject="Chiusura MIL01 - 08/09 (ieri)",
        business_date="2026-09-08", kind="closing",
        body="""Buongiorno, scusate ieri sera mi e' morto il telefono in metro e da casa non sono riuscita.

Martedi 8/9: 31,2k vs 42k bdg, -26%
321 ingressi, 24 scontrini

Poco da dire, giornata molle. Tre resi (Bady tg 1 per taglia, un cable knit S, hoodie M).
Polo nera ancora tra le piu' vendute.

Giulia
""",
    ),
    dict(
        id="c0909", sent="2026-09-09 20:48", frm="giulia", subject="Chiusura MIL01 - 09/09",
        business_date="2026-09-09", kind="closing",
        body="""MIL01 - CHIUSURA 09/09

Fatturato: 48,2k (bdg 45,7) +5%
Ingressi 348 | scontrini 28 | conv 8%

Maya nera 5 pz, Flammette 3. Si comincia a vendere capospalla, finalmente.
Arrivati 286 pz dal magazzino, tutto ok, quasi tutto capospalla donna.
Resi: Rosiere tg 2, cardigan logo XS (taglia).

Ben tornato Roberto!
Giulia
""",
    ),
    dict(
        id="c0910", sent="2026-09-10 21:05", frm="giulia", subject="Chiusura MIL01 - 10/09",
        business_date="2026-09-10", kind="closing",
        body="""Ciao,
36,3k contro un budget di 57k, -37%. Per essere un giovedi di settembre il budget mi sembra tirato, ma va bene.

La cosa che volevo segnalare: oggi tre clienti italiane (due del client book) sono entrate apposta per l'Ambrine marrone, quella della campagna. Ne abbiamo letteralmente una per taglia, due in 1. Il nero invece ce l'abbiamo in tutte le taglie e piu' pezzi. Il marrone e' IL colore della stagione, lo chiedono tutte, temo che finisca in una settimana.
Una l'ha prenotata in 0 per sabato.

Resi: Karakorum 6 (taglia), Trailgrip W 37, e un cardigan logo M con un buchino vicino al polsino (qualita', messo da parte per il reso al magazzino).

Giulia
""",
    ),
    dict(
        id="re0910", sent="2026-09-10 22:31", frm="roberto", subject="Re: Chiusura MIL01 - 10/09",
        to=["giulia"], cc=[], reply_to_id="c0910", kind="reply", suffix="_re1",
        body="""Giulia mandami quante Ambrine marroni avete x taglia e quante nere. Ne parlo con merch.
R.

Inviato da iPhone
""",
    ),
    dict(
        id="re0910b", sent="2026-09-11 09:40", frm="giulia", subject="Re: Chiusura MIL01 - 10/09",
        to=["roberto"], cc=[], reply_to_id="re0910", kind="reply", suffix="_re1",
        body="""Ciao Roberto,
marrone: 00 1, 0 1, 1 2, 2 1, 3 1, 4 1 -> 7 pezzi in tutto.
nero piu' o meno il triplo, non ho contato quello in vetrina.
Se si puo' avere qualche 0, 1 e 2 in piu' di marrone li vendiamo subito, ho gia' 2 clienti in attesa.
Grazie
G.
""",
    ),
    dict(
        id="c0911", sent="2026-09-11 20:55", frm="marco", subject="MIL01 chiusura 11.09",
        business_date="2026-09-11", kind="closing",
        body="""ciao a tutti
61,3k vs 63,7 -4%, ci siamo quasi.
tanti cinesi oggi (piu' degli italiani, strano x un venerdi di settembre), hanno preso hoodie nera e cardigan logo nero a raffica.
Maire blu 3 pz.
un cliente voleva la tshirt bianca in XXL, nn la facciamo arrivare mai.
Marco
""",
    ),
    dict(
        id="c0912", sent="2026-09-12 21:40", frm="giulia", subject="Chiusura MIL01 - sabato 12/09",
        business_date="2026-09-12", kind="closing",
        body="""Sabato 12/09
Fatturato 75,3k, bdg 87,7, -14%
Ingressi 622, scontrini 45

Tanto movimento ma meno conversione di sabato scorso. Crewneck nera 9 pz, Maire nera 6 (quasi tutte 1 e 0).
Ambrine marrone: chiesta da 3 clienti, venduta una in 1. Restano 6 pezzi su tutta la scala.
Mancava l'Hermine blu in 4.
Resi: Tib 3 (taglia), Chamonix, tricot padded cardigan M.
Consegna 164 pz ok.

Giulia
""",
    ),
]

# ---------------------------------------------------------------- week 2-3
EMAILS += [
    dict(
        id="c0914", sent="2026-09-14 20:20", frm="marco", subject="chiusura 14/9",
        business_date="2026-09-14", kind="closing",
        body="""ciao,
40,4 vs 48,4 bdg, -17%.
giornata dei resi: 5 in tutto. Maire 1 e Maya 5 per taglia, un Tib cambio idea, trailgrip regalo, e un'Ambrine in 3 (nera) che la cliente ha riportato dicendo che lei voleva il marrone e alla fine nn era convinta del nero. il marrone in 3 ce l'avevamo ma era gia' prenotato, giuro che nn ci si capisce piu'.
bady nera 5 pz.
Marco
""",
    ),
    dict(
        id="c0915", sent="2026-09-15 20:47", frm="giulia", subject="Chiusura MIL01 - 15/09",
        business_date="2026-09-15", kind="closing",
        body="""MIL01 - CHIUSURA 15/09

Fatturato: 33,9k (bdg 43,5) -22%
Ingressi 293 | scontrini 25

Tanti americani, pochi acquisti. Karakorum nero e crewneck i piu' venduti.
Resi: secondo Arneb rientrato per taglia in una settimana (tg 3). Il cliente era un 3 da sempre, con l'Arneb sarebbe un 2. Veste proprio largo, dal prossimo lo facciamo provare una taglia sotto.
Anche un'Ambrine 3 resa (regalo), una polo L e un cappellino.

Giulia
""",
    ),
    dict(
        id="c0916", sent="2026-09-16 21:02", frm="giulia", subject="Chiusura MIL01 - 16/09",
        business_date="2026-09-16", kind="closing",
        body="""Ciao,
39,9k vs 51,3k, -22%. Settimana lenta, e' la settimana prima della fashion week, si sente.

Arrivati 258 pz. Ambrine marrone: UNA in 1. Una. Nero invece altri pezzi. Roberto so che ci stai lavorando ma lo dico qui per tutti: le clienti non vogliono il nero, chiedono il cioccolato. Ho 2 persone in lista per la 0 e la 2.
Tib nero 5 pz, gli uomini lo adorano.

G.

Inviato da iPhone
""",
    ),
    dict(
        id="c0917", sent="2026-09-17 20:10", frm="marco", subject="chiusura 17.09",
        business_date="2026-09-17", kind="closing",
        body="""tutto ok. 57,7k vs 55,7 +3%. buono il tricot padded nero (4), karakorum nero 3.
2 resi x taglia (hoodie S e trailgrip 40).
ciao, Marco
""",
    ),
    dict(
        id="c0918", sent="2026-09-18 21:15", frm="giulia", subject="Chiusura MIL01 - 18/09",
        business_date="2026-09-18", kind="closing",
        body="""MIL01 - CHIUSURA 18/09

Fatturato: 58,0k (bdg 70,2) +21%
Ingressi 463 | scontrini 44 | conv 9,5%

Venerdi ottimo! Maya nera 12 pezzi, record della stagione per ora. Bene anche il cable knit bianco (5) e la hoodie grigia.
Parecchi giapponesi.
Un solo reso (hoodie S).

Giulia
""",
    ),
    dict(
        id="corr0918", sent="2026-09-18 22:07", frm="giulia", subject="R: Chiusura MIL01 - 18/09 - CORREZIONE",
        business_date="2026-09-18", kind="correction", suffix="_corr", reply_to_id="c0918",
        body="""Scusate, ho invertito le cifre: il fatturato di oggi e' 85,0k e non 58. Il +21% e' giusto.
G.
""",
    ),
    dict(
        id="c0919", sent="2026-09-19 21:52", frm="giulia", subject="Chiusura MIL01 - sabato 19/09",
        business_date="2026-09-19", kind="closing",
        body="""Sabato 19/09
103,9k vs 94,4 bdg, +10%. Primo sabato sopra i 100 della stagione.
745 ingressi, 59 scontrini.

Una cosa strana nel pomeriggio: verso le 16 sono entrate 4 ragazze coreane, poi altre 3, tutte col telefono in mano con la stessa foto, la Maire nera. Ne abbiamo vendute 6 nere oggi e sono finite la 2 e la 3. Almeno 4 sono uscite senza perche' non c'era la taglia (2 e 3). Sara dice che e' la giacca di un'attrice in una serie coreana che sta andando fortissimo adesso, domani le chiedo meglio.
Ci restano pochissime Maire nere: 00, 0, 1 una a testa e la 4.

Anche la beanie blu (6) e Maire blu (4).
Resi: Flammette 0, Maya 4 per taglia e una Maya 2 con una cucitura aperta sulla tasca.
Consegna 166 pz, nessuna Maire nera dentro.

Giulia
""",
    ),
    dict(
        id="c0920", sent="2026-09-20 20:38", frm="store", subject="Chiusura Montenapoleone 20.09",
        business_date="2026-09-20", kind="closing",
        body="""Ciao a tutti, scrivo io oggi (Sara) perche' Marco e' a casa e Giulia di riposo.

Fatturato 61,7k, budget 67k (-8%). 518 ingressi.

Sulla Maire nera: come ieri sono venute ragazze coreane, oggi 3 (2 in tg 0 e una in 3). Ho parlato con loro: la giacca e' quella che indossa l'attrice Han Yu-ri nel drama "Lettere d'inverno", in una scena alla stazione. Su Instagram e su Naver gira lo screenshot, lo hanno tutte sul telefono. Le turiste vengono a Milano e la cercano qui e a Parigi.
Abbiamo venduto ieri le ultime 0, 1 e 2, adesso abbiamo solo la 00 e la 4 in nero.
Ho fatto provare la Maire beige e quella blu, gentilissime ma no grazie, vogliono la nera, punto.
Cosa posso dire alle clienti? Si sa quando arriva? Tengo una lista con i loro numeri WhatsApp intanto.

Trailgrip grigia 4 pz oggi, cardigan nero 3.

Sara Kim
MIL01 - iPad negozio
""",
    ),
    dict(
        id="c0921", sent="2026-09-21 20:44", frm="marco", subject="chiusura 21/9 + MAIRE NERA",
        business_date="2026-09-21", kind="closing",
        body="""ciao,
60,1k vs 49,6 bdg +21%, lunedi molto buono.

pero' la notizia e' sempre quella: SETTE richieste di Maire nera oggi, tutte asiatiche, quasi tutte coreane (Sara ha contato con me). taglie 0, 1, 3 e 2. noi nn ne abbiamo piu' tranne 00 e 4.
qualcuno in sede sa dirci quando torna?? ci servirebbe una data da dare alle clienti, sennò vanno a Parigi.

venduto bene crewneck nera e ilvaro nero (3).
un cliente cercava il cardigan logo nero XS.

Marco
""",
    ),
    dict(
        id="re0921", sent="2026-09-21 22:18", frm="roberto", subject="Re: chiusura 21/9 + MAIRE NERA",
        to=["marco", "giulia"], cc=[], reply_to_id="c0921", kind="reply", suffix="_re1",
        body="""Quante richieste in tutto da sabato? Che taglie? Gli altri colori niente?
Chiedo a merch domani.
R.

Inviato da iPhone
""",
    ),
    dict(
        id="re0921b", sent="2026-09-22 10:12", frm="giulia", subject="Re: chiusura 21/9 + MAIRE NERA",
        to=["roberto"], cc=["marco", "sara"], reply_to_id="re0921", kind="reply", suffix="_re1",
        body="""Ciao Roberto,
da sabato 19 a ieri sera abbiamo contato 14 richieste che non abbiamo potuto servire:
tg 0: 4
tg 1: 2
tg 2: 3
tg 3: 5 (circa, sabato era un caos)
Beige e blu le facciamo provare sempre, nessuna le ha prese. Bianca idem.
In negozio rimangono 1 pz in 00 e 1 in 4.
Sara ha una lista WhatsApp con 9 nomi.
Grazie, G.
""",
    ),
    dict(
        id="c0922", sent="2026-09-22 21:28", frm="giulia", subject="Chiusura MIL01 - 22/09",
        business_date="2026-09-22", kind="closing",
        body="""MIL01 - CHIUSURA 22/09 (FW giorno 1)

Fatturato: 61,0k (bdg 48,4) +26%
Ingressi 425 | scontrini 33

Iniziata la fashion week, oggi ancora tranquillo, tanti buyer e stylist in giro, in via della Spiga gia' transenne.
Bady nera 7 pz, cardigan logo blu 4.
Maire nera: altre 4 richieste (2, 0, 1). Abbiamo provato a proporre la Maya nera come alternativa, no.
Domani l'ufficio stampa usa la saletta VIC per due appuntamenti, alle 11 e alle 15.

Giulia
""",
    ),
    dict(
        id="vm0923", sent="2026-09-23 13:05", frm="giulia", subject="foto vetrine montenapo FW",
        to=["vm"], cc=["roberto"], kind="misc",
        attachments=[{"name": "IMG_4471.jpg"}, {"name": "IMG_4473.jpg"}],
        body="""Ciao ragazzi,
vi mando le foto delle vetrine come sono oggi. Sulla destra abbiamo spostato l'Ambrine sul manichino davanti perche' tutti la chiedono, l'abbiamo messa nera perche' di marrone ne abbiamo troppo poche e non posso togliere un pezzo dalla vendita.
Ditemi se per voi va bene o se la rimettiamo come da planogramma.
Giulia
""",
    ),
    dict(
        id="c0923", sent="2026-09-23 21:50", frm="giulia", subject="Chiusura MIL01 - 23/09",
        business_date="2026-09-23", kind="closing",
        body="""Chiusura 23/09

63,6k vs 55,2k bdg (+15%)
583 ingressi ma conversione bassa (6%): tanta gente della moda che entra, gira e esce.

La Bady nera vola, 13 pezzi oggi!
Consegna 314 pz: zero Maire nere, in compenso altre beige e blu. Arrivate tre Ambrine marroni (2, 3, 4), due erano gia' prenotate.
Resi: cardigan S e una crewneck L.

G.
""",
    ),
    dict(
        id="c0924", sent="2026-09-24 22:05", frm="giulia", subject="Chiusura MIL01 - 24/09",
        business_date="2026-09-24", kind="closing",
        body="""Ciao,
giornata pazzesca.
Fatturato 87,2k su budget 69,7 (+25%)
693 ingressi, 47 scontrini

Fashion week nel pieno: alle 18 c'era la fila fuori perche' una cantante italiana e' entrata con lo stylist e i fotografi l'hanno seguita fin sulla porta. Ha preso due Bady. La vigilanza ha fatto entrare a gruppi per un'ora.
Insolux nere 6 paia, Maya verde 5.

Lancio Genius Polaris oggi: tanta curiosita', molti provano, ma vendute solo cose piccole. Il commento piu' frequente e' "veste piccolo per essere oversize" e "2.400 euro per questo?".

Maire nera: altre 3 richieste (0, 1, 3) piu' di coreane. Venduta l'ultima 4.
Mancava anche la Maya oliva in 2 e il Karakorum grigio in 3. Due ragazze chiedevano un Ilvaro rosa, che non abbiamo mai avuto in quelle taglie.

Giulia
""",
    ),
    dict(
        id="c0925", sent="2026-09-25 21:20", frm="marco", subject="chiusura ven 25/9",
        business_date="2026-09-25", kind="closing",
        body="""ciao
81,7k su 81,6 bdg, pari.
maya nera 6, dolcevita lana nero 5.
maire nera ormai finita in TUTTE le taglie (venduta la 00 stamattina). richieste oggi 4 (1, 1, 0, 4). le coreane fanno vedere la foto, gli diciamo che nn sappiamo quando arriva e se ne vanno. ci fa male.
il polaris lo provano tutti e se lo tolgono subito, dicono che tira sulle spalle. assurdo x un oversize.
Tib blu in 1 chiesto da un ragazzo, nn c'era.
Marco
""",
    ),
]

# ---------------------------------------------------------------- MFW end + Golden Week
EMAILS += [
    dict(
        id="c0927", sent="2026-09-27 21:48", frm="giulia", subject="chiusura sabato + domenica (26-27/09)",
        business_date="2026-09-26,2026-09-27", kind="closing",
        body="""Ciao a tutti, ieri sera non ce l'ho fatta, siamo usciti alle 21 passate. Vi mando tutto insieme.

SABATO 26
103,9k vs 109,3 bdg (-5%)
1.048 ingressi (!!) ma solo 56 scontrini, conversione al 5%. Ultimo weekend di fashion week: dalle 15 alle 18 la porta era bloccata, sfilata a due passi, fotografi e influencer davanti alla vetrina, la vigilanza faceva entrare 10 persone alla volta. Tanta gente che voleva solo la foto dentro. Abbiamo perso sicuramente clienti veri che si sono stufati di aspettare fuori.
Hoodie nera 8, beanie nera 7, Montcla nero 6. 6 Maire bianche, quasi tutte a clienti cinesi.
Maire nera chiesta 3 volte (0, 1, 2).
Consegna 247 pz, gestita lunedi mattina in pratica, il back-office era pieno.

DOMENICA 27
66,3k vs 77,8 (-15%)
Piu' calma, ci voleva. Maire blu 4, Rosiere nera 3.
Maire nera: 6 richieste, 4 solo in tg 1 (due amiche coreane + una mamma con la figlia), poi 00 e 0. Le coreane la bianca non la guardano proprio.
Resi: Bady 2 (2 regali sabato, uno oggi), un Montgenevre 5, un dolcevita XS e una crewneck S con un filo tirato.

Giulia
""",
    ),
    dict(
        id="c0928", sent="2026-09-28 20:35", frm="marco", subject="chiusura 28/9",
        business_date="2026-09-28", kind="closing",
        body="""ciao a tutti
62,7k vs 57,5 bdg +9%. fine fashion week, lunedi ancora movimentato, tanti giapponesi e tedeschi.
Maya nera 7, beanie nera 5.
finito Ilvaro nero in 0.
segnalo un reso strano: Tib tg 4 comprato a inizio mese, il cursore della zip si e' sfilato e nn si chiude piu'. nn era mai successo. fatto reso, il pezzo e' in back-office se lo vuole vedere qualcuno.
un cliente chiedeva l'Arneb nero in 2, nn c'era (e cmq gli avrei detto di provarlo).
Marco
""",
    ),
    dict(
        id="c0929", sent="2026-09-29 21:02", frm="giulia", subject="Chiusura MIL01 - 29/09",
        business_date="2026-09-29", kind="closing",
        body="""MIL01 - CHIUSURA 29/09

Fatturato: 46,5k (bdg 57,4) -19%
Ingressi 423 | scontrini 29

Giornata di calma prima della golden week.
TIB: altri 2 resi per la zip, stesso difetto di ieri (il cursore si stacca dal dente). Sono 3 in due giorni, tg 3 e 4. In piu' un Tib 6 cambio idea e un 3 per taglia. Mi sembra un lotto difettoso, qualcuno ne sa qualcosa? Dobbiamo rimborsare o cambiare?
Due Maya rese (una per taglia, una per colore).
Maire nera ancora richiesta in 0 e 1.

Giulia
""",
    ),
    dict(
        id="c0930", sent="2026-09-30 21:45", frm="giulia", subject="Chiusura MIL01 - 30/09 GOLDEN WEEK",
        business_date="2026-09-30", kind="closing",
        body="""Ciao,
golden week partita col botto.

Fatturato 94,8k, bdg 64k, +48%
525 ingressi, 44 scontrini
Quasi meta' dei clienti cinesi, gruppi da 4-6 persone che comprano per tutta la famiglia. Hoodie nera 10 pezzi, dolcevita nero 5.
Tax free: coda dalle 15 alle 18, una sola postazione non basta. Abbiamo solo Fei che parla mandarino, oggi era lei da sola su tutto il piano terra. CHIEDO di nuovo una risorsa in piu' che parli cinese fino all'8, anche dall'outlet o da Rinascente, va bene chiunque.

Resi TIB: CINQUE oggi per la zip (tg 2, 4, 4, 6, 7). Ormai e' un problema serio, i clienti sono arrabbiati, un signore ha detto che a 990 euro una zip cosi e' una vergogna. Li abbiamo rimborsati tutti, non avevamo pezzi del lotto nuovo per cambiarli.

Maire nera: 7 richieste (1 1 1, 2 2, 00, 3). Siamo a quota trenta e passa da quando e' iniziato.
Consegna 370 pz ok.

Giulia
""",
    ),
    dict(
        id="fwd1001", sent="2026-10-01 11:24", frm="giulia", subject="I: gilet Tib zip rotta",
        to=["ops", "merch"], cc=["roberto"], kind="fwd", suffix="_fwd",
        body="""Vi giro la mail di un cliente (signore italiano, cliente abituale). Stesso problema dei resi di questi giorni.
Giulia

-----Messaggio originale-----
Da: F. Colombo
Inviato: mercoledi 30 settembre 2026 23:10
A: mil01.store@moncler-retail.example
Oggetto: gilet Tib zip rotta

Buonasera,
ho acquistato da voi il 12 settembre un gilet Tib blu taglia 4. Dopo nemmeno tre settimane il cursore della zip si e' staccato da una parte e il gilet non si chiude piu'. Lo uso per andare in ufficio, non l'ho certo maltrattato.
Domani passo in negozio, vorrei sapere se lo sostituite o se devo mandarlo in riparazione. Sinceramente da Moncler non me lo aspettavo.
Cordiali saluti
F. Colombo
""",
    ),
    dict(
        id="c1001", sent="2026-10-01 21:30", frm="giulia", subject="Chiusura MIL01 - 01/10",
        business_date="2026-10-01", kind="closing",
        body="""MIL01 - CHIUSURA 01/10

Fatturato: 100,9k (bdg 72,9) +38%
Ingressi 576 | scontrini 42

Cinesi un terzo, poi italiani e americani. Arneb nero 6 pezzi: ormai lo facciamo provare a tutti una taglia sotto e cosi' funziona, non e' rientrato piu' niente per taglia da quando lo facciamo.
Maya oliva e blu 4+4, Flammette 4.

Tib: altri 2 zip rotte (6 e 2). Il signore della mail di stamattina e' passato, rimborsato.
Ambrine marrone: finite la 1 e la 2, ne restano 00, 0 e 3. Il magazzino dice che di marrone in 0-1-2 non ce n'e'. Il nero intanto e' fermo.
Maire nera 4 richieste (3, 3, 0, 4), Rosiere nera 1.
Resi anche cardigan L, hoodie XL, guanti.

G.
""",
    ),
]

_HTML_1002 = """<html><body style="font-family:Calibri,Arial,sans-serif;font-size:11pt">
<p>Ciao a tutti,<br>giornata record, vi incollo il riepilogo.</p>
<table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse">
<tr style="background:#1f3864;color:#fff"><td colspan="2"><b>MIL01 MONTENAPOLEONE - 02/10/2026</b></td></tr>
<tr><td>Fatturato netto</td><td>136.135 &euro;</td></tr>
<tr><td>Budget</td><td>83.080 &euro;</td></tr>
<tr><td>vs bdg</td><td>+63,9%</td></tr>
<tr><td>Ingressi</td><td>828</td></tr>
<tr><td>Scontrini</td><td>63</td></tr>
<tr><td>Conv.</td><td>7,6%</td></tr>
<tr><td>UPT</td><td>1,94</td></tr>
<tr><td>Top</td><td>Maya nera, Legere nero, Bady nera, Ilvaro bianco</td></tr>
<tr><td>Note</td><td>Golden week, 40% CN. Tax free in tilt 16-17. Maire nera 7 richieste.</td></tr>
</table>
<p>Il terminale del tax free si e' bloccato per quasi un'ora, coda fino all'ingresso, abbiamo fatto i moduli a mano e alcuni cinesi li abbiamo mandati a fare il rimborso in aeroporto. Fei sfinita.<br>
Maire nera: 7 richieste (2 2 2, 1 1, 0, 4). Anche un Ilvaro bianco 00.<br>
1 Tib zip.</p>
<p>Giulia</p>
</body></html>"""

_TXT_1002 = """Ciao a tutti,
giornata record, vi incollo il riepilogo.

MIL01 MONTENAPOLEONE - 02/10/2026
Fatturato netto	136.135 EUR
Budget	83.080 EUR
vs bdg	+63,9%
Ingressi	828
Scontrini	63
Conv.	7,6%
UPT	1,94
Top	Maya nera, Legere nero, Bady nera, Ilvaro bianco
Note	Golden week, 40% CN. Tax free in tilt 16-17. Maire nera 7 richieste.

Il terminale del tax free si e' bloccato per quasi un'ora, coda fino all'ingresso, abbiamo fatto i moduli a mano e alcuni cinesi li abbiamo mandati a fare il rimborso in aeroporto. Fei sfinita.
Maire nera: 7 richieste (2 2 2, 1 1, 0, 4). Anche un Ilvaro bianco 00.
1 Tib zip.

Giulia
"""

EMAILS += [
    dict(
        id="c1002", sent="2026-10-02 21:12", frm="giulia", subject="Chiusura MIL01 - 02/10",
        business_date="2026-10-02", kind="closing", body=_TXT_1002, html=_HTML_1002,
    ),
    dict(
        id="c1002dup", sent="2026-10-02 21:13", frm="giulia", subject="Chiusura MIL01 - 02/10",
        business_date="2026-10-02", kind="dup", suffix="_dup", body=_TXT_1002, html=_HTML_1002,
    ),
    dict(
        id="c1003", sent="2026-10-03 22:02", frm="giulia", subject="Chiusura MIL01 - sabato 03/10",
        business_date="2026-10-03", kind="closing",
        body="""Sabato 03/10

125,1k su budget 123,8 (+1%). Il budget di oggi era gia' alto, ci siamo stati dentro.
986 ingressi, 56 scontrini.
I cinesi hanno preso tutte le Maire chiare che avevamo: 6 bianche, 5 beige. Peccato che le coreane continuino a volere la nera.
Cardigan logo nero 5, Bady nera 5.
Due polo bianche M richieste, non ci sono.
Tib: 2 zip (3 e 4) + un 4 per taglia. Ho perso il conto, saremo a 12-13 da lunedi scorso.
Consegna 244 pz, sistemata stasera dopo chiusura.

Domani Sara, io e Marco a riposo.
Giulia
""",
    ),
    dict(
        id="c1004", sent="2026-10-04 20:52", frm="sara", subject="Chiusura Montenapoleone 04.10",
        business_date="2026-10-04", kind="closing",
        body="""Ciao a tutti,
domenica 86,5k (budget 81,5, +6%), 688 ingressi.

Maya blu 8 e Maya nera 7, sono andate soprattutto a clienti italiane, oggi il 33% erano italiani.
Una famiglia coreana (mamma e due figlie) chiedeva la Maire nera in 0 e 2, con la solita foto di Han Yu-ri. Gli ho fatto vedere la beige, la mamma era quasi convinta ma la figlia no. Aggiunte alla lista WhatsApp, siamo a 17 nomi.

Resi: 3 Tib per la zip (2, 6, 7), e un Arneb 5 cambiato con il 4. Ormai lo diciamo prima a tutti: una taglia in meno.
Mancavano anche crewneck grigia M e polo bianca M.

Sara Kim
""",
    ),
    dict(
        id="c1005", sent="2026-10-05 20:40", frm="marco", subject="chiusura 5/10",
        business_date="2026-10-05", kind="closing",
        body="""ciao
73,9k vs 62,4 bdg +18%.
ancora tantissimi cinesi (piu' di un terzo). cable knit nero 6 pz, karakorum 3.
novita': 2 ragazze cinesi mi hanno fatto vedere sul telefono una cantante k-pop col piumino corto rosa, l'Ilvaro rosa, in 1 e 2. noi del rosa abbiamo solo una 4. da quello che dicono in Asia e' gia' esaurito.
chiesta anche una trailgrip donna nera 36.
1 Maya 6 resa x cambio idea, 1 cable knit L.
Marco
""",
    ),
    dict(
        id="c1006", sent="2026-10-06 22:20", frm="giulia", subject="Chiusura MIL01 - 06/10 - Maire nera, serve una risposta",
        business_date="2026-10-06", kind="closing",
        body="""Ciao a tutti,
numeri prima: 115,5k vs 61,4k di budget, +88%. 691 ingressi, 54 scontrini. Grande giornata, la squadra e' stata fantastica.

Ma devo scrivere della Maire nera perche' oggi e' stato davvero troppo. Ho chiesto a Sara di tenere il conto con un foglio alla cassa: 22 richieste di Maire nera in un giorno. Nove in tg 1, sei in tg 2, tre in 0, due in 00, due in 3. Un gruppo di ragazze coreane in tour la mattina, poi nel pomeriggio anche clienti cinesi che la chiedevano con la stessa foto.
A ognuna abbiamo proposto beige, blu notte e bianca: niente, vogliono la nera e basta. Due sono uscite dicendo che andavano a cercarla a Parigi.
Sono quasi tre settimane che lo scriviamo. Non so se qualcuno in sede ha un'idea del numero di vendite che stiamo perdendo: a 1.450 euro l'una, oggi erano piu' di 30k di Maire nere solo da noi. Vorrei sapere:
1) se c'e' una data di arrivo dal magazzino
2) se possiamo bloccare dei pezzi per la nostra lista (Sara ha 17-18 nomi + quelli di oggi)
3) se ci sono negozi in Europa che ne hanno ancora qualche pezzo e possono mandarcele.

Altro: un'Ambrine marrone 4 chiesta (non l'abbiamo), Maya oliva 6, Peyre nero 2.
Beanie rosa 5 pezzi, Arneb blu 5, cardigan logo nero 5.
Resi: Ilvaro 0 per taglia, Maya 5, cardigan L, crewneck S.

Grazie
Giulia

Giulia Ferrandi
Store Manager - Moncler Milano Montenapoleone
Via Monte Napoleone 1, 20121 Milano
Le informazioni contenute in questa e-mail sono riservate e destinate esclusivamente al destinatario.
""",
    ),
    dict(
        id="re1006", sent="2026-10-07 08:06", frm="roberto", subject="Re: Chiusura MIL01 - 06/10 - Maire nera, serve una risposta",
        to=["giulia"], cc=["ops", "merch"], reply_to_id="c1006", kind="reply", suffix="_re1",
        body="""Giulia ho sentito merch ieri sera. La nera rientra in DC il 16, poi vi arriva con il primo giro. In Europa non ce n'e', anche Parigi e' a zero.
Mandate a merch la lista nomi/taglie cosi' teniamo i pezzi bloccati per voi.
Grazie a tutti x ieri, numeri fantastici.
R.

Inviato da iPhone
""",
    ),
    dict(
        id="wl1007", sent="2026-10-07 11:42", frm="giulia", subject="Lista attesa Maire nera - MIL01",
        to=["merch"], cc=["roberto", "sara"], reply_to_id="re1006", kind="misc",
        attachments=[{"name": "lista_attesa_maire_nera_MIL01.xlsx", "rows": [
            ["Data richiesta", "Cliente", "Naz.", "Taglia", "Contatto", "Note"],
            ["19/09", "J.Y.L.", "KR", "2", "WA", ""],
            ["19/09", "S.H.P.", "KR", "3", "WA", ""],
            ["20/09", "M.K.", "KR", "0", "WA", "torna a Milano a nov"],
            ["21/09", "H.J.C.", "KR", "1", "WA", ""],
            ["21/09", "Y.S.", "KR", "3", "mail", ""],
            ["22/09", "E.K.", "KR", "2", "WA", ""],
            ["24/09", "L.W.", "CN", "0", "WeChat", ""],
            ["25/09", "J.H.", "KR", "1", "WA", ""],
            ["27/09", "S.Y.K.", "KR", "1", "WA", "amica di J.H."],
            ["27/09", "D.Y.K.", "KR", "1", "WA", ""],
            ["30/09", "A.R.", "IT", "1", "tel", "cliente client book"],
            ["30/09", "Z.Q.", "CN", "2", "WeChat", ""],
            ["01/10", "H.N.", "KR", "3", "WA", ""],
            ["02/10", "M.J.S.", "KR", "2", "WA", ""],
            ["02/10", "C.W.", "KR", "2", "WA", ""],
            ["04/10", "S.B.", "KR", "0", "WA", "mamma"],
            ["04/10", "J.B.", "KR", "2", "WA", "figlia"],
            ["06/10", "Y.J.K.", "KR", "1", "WA", "gruppo tour"],
            ["06/10", "H.Y.O.", "KR", "1", "WA", "gruppo tour"],
            ["06/10", "S.L.", "KR", "1", "WA", "gruppo tour"],
            ["06/10", "M.C.", "KR", "2", "WA", ""],
            ["06/10", "X.L.", "CN", "00", "WeChat", ""],
            ["06/10", "G.T.", "IT", "3", "tel", ""],
        ]}],
        body="""Ciao,
come da indicazione di Roberto vi mando la lista d'attesa della Maire nera che teniamo in negozio (iniziali, taglia, contatto).
Sono 23 clienti che hanno lasciato il numero, le richieste totali sono molte di piu' (oltre 70 da meta' settembre, chi non lascia il numero non lo segniamo).
Taglie: soprattutto 1 e 2, poi 0 e 3.
Se riuscite a riservarci almeno 25-30 pezzi sul primo giro dal magazzino li vendiamo in pochi giorni.
Grazie
Giulia
""",
    ),
    dict(
        id="c1007", sent="2026-10-07 20:58", frm="marco", subject="chiusura 07/10",
        business_date="2026-10-07", kind="closing",
        body="""ciao a tutti
84,8k vs 66,5 +28%. ancora golden week, domani ultimo giorno.
legere belt bag nera 7, hoodie grigia 5.
consegna grossa (443 pz), un sacco di Maire... beige, bianche e blu. nere zero. le coreane oggi erano di meno ma 5 richieste ci sono state lo stesso.
Ilvaro rosa chiesto altre 2 volte (1 e 2).
Arneb 2 cambiato con l'1.
Marco
""",
    ),
]

_HTML_1008 = """<html><body style="font-family:Calibri,Arial,sans-serif;font-size:11pt">
<table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse">
<tr style="background:#1f3864;color:#fff"><td colspan="2"><b>MIL01 MONTENAPOLEONE - 08/10/2026</b></td></tr>
<tr><td>Fatturato netto</td><td>143.750 &euro;</td></tr>
<tr><td>Budget</td><td>75.860 &euro;</td></tr>
<tr><td>vs bdg</td><td>+89%</td></tr>
<tr><td>Ingressi</td><td>855</td></tr>
<tr><td>Scontrini</td><td>58</td></tr>
<tr><td>UPT</td><td>2,2</td></tr>
<tr><td>Top</td><td>Bady nera 10, Maya nera 9, Hermine nera 7, Rosiere 6</td></tr>
<tr><td>Rotture</td><td>CARDIGAN LOGO M nero e blu FINITO</td></tr>
</table>
<p>Record assoluto del negozio da quando ci sono io. Ultimo giorno di golden week, i cinesi hanno comprato come se fosse l'ultimo giorno davvero.<br>
Stamattina un gruppo ha preso il cardigan logo in M praticamente tutto, nero e blu, entro le 13 era finito. Nel pomeriggio due clienti lo cercavano in M e non avevamo niente. Il magazzino non ha M fino a fine mese, domani chiedo a Rinascente e Roma se ci girano qualcosa.<br>
Anche il dolcevita lana marrone in S chiesto due volte, finito.<br>
Maire nera: 3 richieste (1, 3, 4).<br>
Resi: Maya 5, hoodie M, 1 Tib zip, Arneb 3 cambiato in 2.</p>
<p>Grazie a tutto il team, siete stati incredibili questa settimana.<br>Giulia</p>
</body></html>"""

EMAILS += [
    dict(
        id="c1008", sent="2026-10-08 22:15", frm="giulia", subject="Chiusura MIL01 - 08/10 RECORD",
        business_date="2026-10-08", kind="closing", html=_HTML_1008,
        body="""MIL01 MONTENAPOLEONE - 08/10/2026
Fatturato netto	143.750 EUR
Budget	75.860 EUR
vs bdg	+89%
Ingressi	855
Scontrini	58
UPT	2,2
Top	Bady nera 10, Maya nera 9, Hermine nera 7, Rosiere 6
Rotture	CARDIGAN LOGO M nero e blu FINITO

Record assoluto del negozio da quando ci sono io. Ultimo giorno di golden week, i cinesi hanno comprato come se fosse l'ultimo giorno davvero.
Stamattina un gruppo ha preso il cardigan logo in M praticamente tutto, nero e blu, entro le 13 era finito. Nel pomeriggio due clienti lo cercavano in M e non avevamo niente. Il magazzino non ha M fino a fine mese, domani chiedo a Rinascente e Roma se ci girano qualcosa.
Anche il dolcevita lana marrone in S chiesto due volte, finito.
Maire nera: 3 richieste (1, 3, 4).
Resi: Maya 5, hoodie M, 1 Tib zip, Arneb 3 cambiato in 2.

Grazie a tutto il team, siete stati incredibili questa settimana.
Giulia
""",
    ),
    dict(
        id="tr1009", sent="2026-10-09 10:35", frm="giulia", subject="richiesta transfer cardigan logo M",
        to=["mil02", "rom01"], cc=["roberto"], kind="misc",
        body="""Ciao ragazzi,
da ieri siamo a zero cardigan logo in M, sia nero che blu (la golden week ci ha svuotato) e a Castel San Giovanni la M rientra solo a fine ottobre.
Avete qualche M da girarci? Anche 1 o 2 pezzi per colore, ce lo chiedono in continuazione. Se vi serve qualcosa da noi ditemi, ricambiamo volentieri.
Grazie mille
Giulia
MIL01 Montenapoleone
""",
    ),
    dict(
        id="re1009", sent="2026-10-09 18:47", frm="roberto", subject="Re: richiesta transfer cardigan logo M",
        to=["giulia"], cc=["mil02", "rom01"], reply_to_id="tr1009", kind="reply", suffix="_re1",
        body="""Giulia nn facciamo transfer per 1-2 pz adesso, Rinascente ne ha pochi anche loro e a Roma c'e' solo blu. Aspettiamo il DC, la M arriva a fine mese.
R.

Inviato da iPhone
""",
    ),
    dict(
        id="c1009", sent="2026-10-09 21:05", frm="giulia", subject="Chiusura MIL01 - 09/10",
        business_date="2026-10-09", kind="closing",
        body="""Chiusura 09/10

99,4k vs 89,6 (+11%), 602 ingressi.
Finita la golden week, oggi tornati gli italiani e qualche tedesco. Montcla nero 8, Maya blu 7.
Cardigan M: ok Roberto, aspettiamo. Intanto lo chiedono e mandiamo via la gente.
Maire nera 3 richieste (00, 0, 1), Ilvaro rosa in 0.
Arneb 2 cambiato con l'1, cable knit L reso.

G.

Inviato da iPhone
""",
    ),
    dict(
        id="c1010", sent="2026-10-10 21:40", frm="marco", subject="chiusura sab 10/10",
        business_date="2026-10-10", kind="closing",
        body="""ciao a tutti
sabato no. 83,6k contro un budget di 132k, -37%.
premetto che 132k di budget x un sabato senza golden week secondo me e' fuori dal mondo (sabato scorso coi cinesi abbiamo fatto 125). pero' anche noi ci abbiamo messo del nostro: Chiara e Davide a casa con la febbre, Fei a recupero dopo la settimana scorsa, eravamo in 7 su 3 piani con 744 ingressi. tanta gente e' uscita senza essere servita, conversione sotto il 6%.
Flammette nera 5, Ambrine nera 3.
Maire nera: 8 richieste (1, 1, 1, 2, 2, 4, 4, 3). sempre la stessa storia.
cardigan logo M blu chiesto, niente. ho chiamato Stefano della Rinascente, dice che ha un solo M nero e se lo tiene. ok.
consegna 370 pz, cardigan M zero (come previsto).
Arneb 4 cambiato.
Marco

Inviato da iPhone
""",
    ),
    dict(
        id="c1011", sent="2026-10-11 20:28", frm="marco", subject="chiusura dom 11/10",
        business_date="2026-10-11", kind="closing",
        body="""domenica 74,5k (bdg 88,6) -16%. oggi piu' di meta' italiani, i cinesi sono spariti di colpo.
Maire blu 4, Maya blu 4. le italiane la Maire blu la prendono, le coreane no: 4 richieste di nera (0, 0, 1, 1).
resi: Bady 0, Montcla 4 regalo, Arneb 4 (taglia, quello che si era rifiutato di provare il 3...).
Marco
""",
    ),
    dict(
        id="c1012", sent="2026-10-12 20:16", frm="marco", subject="chiusura 12/10",
        business_date="2026-10-12", kind="closing",
        body="""55,8k vs 67,7 bdg -18%. lunedi moscio, tanti americani.
Insolux nere 6 paia.
5 coreane x la maya nera, 3 in tg 1 e 2 in 3. sempre la foto sul telefono. gli abbiamo detto dopo il 16.
cardigan M blu chiesto 1 volta.
Arneb 3 cambiato, dolcevita L e trailgrip 44 resi.
M.
""",
    ),
    dict(
        id="c1013", sent="2026-10-13 21:10", frm="sara", subject="Chiusura Montenapoleone 13.10",
        business_date="2026-10-13", kind="closing",
        body="""Ciao a tutti, Giulia oggi era in sede, scrivo io.

83,8k su budget 67,6 (+24%), 512 ingressi, 41 scontrini.
Finalmente fa freddo, stamattina 8 gradi: Maya blu 6, Maire blu 5, beanie bianca 3. Gli italiani entrano per il piumino.

Maire nera: oggi 14 richieste, le ho segnate tutte. Tg 0 sei volte (!), tg 2 cinque, tg 3 due, tg 1 una. C'era un gruppo di studentesse coreane di Brera, sono venute in quattro e ognuna ha mandato la foto alle amiche. Do a tutte la stessa risposta: arriva in magazzino il 16, poi qualche giorno per arrivare da noi. Due mi hanno chiesto se la possono ordinare online, ho detto di provare ma che anche online e' esaurita.
Una ragazza cinese chiedeva l'Ilvaro rosa 00.
Reso un Tib 7 per difetto (cucitura, non zip questa volta), un Bady 4 e un cappellino.

Sara Kim
Senior Sales Associate
Moncler Milano Montenapoleone
""",
    ),
    dict(
        id="c1014", sent="2026-10-14 21:22", frm="giulia", subject="Chiusura MIL01 - 14/09",
        business_date="2026-10-14", kind="closing",
        body="""MIL01 - chiusura

76,9k vs 75,5 (+2%)
526 ingressi, 38 scontrini

Freddo vero, si vede: Insolux nere 6, Maya blu 5, Maya nera 4, cardigan logo blu 4 (S e L, M sempre a zero).
Maire nera: 6 richieste, 5 in tg 2.
Giornata pesante di resi, 8: Maire 1 per taglia, Bady 0, Montcla 3 (piuma che esce dalle cuciture), crewneck XXL, t-shirt M (lavaggio), Insolux 39 regalo, e altri 2 Tib per la zip.
Consegna 322 pz: ancora Maire beige, bianche e blu, una sola Ambrine marrone in 4. Ma lo sanno al magazzino cosa ci chiedono i clienti?

G.
""",
    ),
    dict(
        id="c1015", sent="2026-10-15 20:50", frm="marco", subject="chiusura 15/10",
        to=["retail-ops-spain@moncler-retail.example"], cc=["roberto"],
        business_date="2026-10-15", kind="closing",
        body="""ciao a tutti
72,2k vs 83,2 -13%.
il cardigan logo va fortissimo, 7 neri e 5 blu nelle altre taglie, peccato che manchi la M da venerdi: 2 clienti la volevano nera, uno ha preso la L e l'ha fatta stringere?? no scherzo, l'ha lasciata li.
coreane ancora tante (12%), Maire nera 3 richieste (0, 2, 3). domani dovrebbe entrare in magazzino, speriamo.
chiesti anche Ilvaro nero 4 e Rosiere 7.
resi: Tib 6 zip, Ilvaro 1 taglia, cardigan S.
domani sciopero generale, vediamo chi arriva.
Marco

Inviato da iPhone
""",
    ),
    dict(
        id="c1016", sent="2026-10-16 20:35", frm="giulia", subject="Chiusura MIL01 - 16/10 sciopero",
        business_date="2026-10-16", kind="closing",
        body="""Ciao,
giornata da dimenticare. Sciopero generale: metro ferme, tram a singhiozzo, mezza squadra arrivata tra le 11 e mezzogiorno. Abbiamo aperto alle 10 in quattro, piano -1 chiuso fino alle 12.
In citta' pochissima gente, solo turisti a piedi dagli hotel.

45,7k su 104,7 di budget (-56%). 434 ingressi.
Maire blu 4, e 3 passamontagna Polaris bianchi: l'unica cosa del Genius che si muove davvero, i capi Polaris restano sulle grucce.
Cardigan logo M nero chiesto 2 volte.
Maire nera 1 richiesta.
6 resi tra cui un Tib zip e un Arneb 7.

Roberto, oggi e' il 16: la Maire nera e' entrata in magazzino? Quando parte per noi?

Giulia
""",
    ),
    dict(
        id="c1017", sent="2026-10-17 21:58", frm="giulia", subject="Chiusura MIL01 - sabato 17/10",
        business_date="2026-10-17", kind="closing",
        body="""Sabato 17/10
133,8k = budget (133,8) preciso al centinaio!
808 ingressi, 77 scontrini, conversione 9,5%.

Il freddo ci ha salvato: Hermine nera 8, Rosiere 7, beanie blu 7, cable knit 5. Tanti milanesi e tanti americani.
Consegna 249 pz: Maire beige e blu, la nera ancora no. Il magazzino dice che parte all'inizio della settimana.
Cardigan M blu chiesto. Maire nera 1 richiesta (2).
Resi Tib zip 2 (tg 1 e 3), Maya 3, Karakorum 3, t-shirt XL, Trailgrip W.

Giulia

Giulia Ferrandi
Store Manager - Moncler Milano Montenapoleone
Via Monte Napoleone 1, 20121 Milano
Le informazioni contenute in questa e-mail sono riservate e destinate esclusivamente al destinatario.
""",
    ),
    dict(
        id="c1018", sent="2026-10-18 20:47", frm="store", subject="Chiusura Montenapoleone 18.10",
        business_date="2026-10-18", kind="closing",
        body="""Ciao, Sara qui dall'iPad.

Domenica 121,2k, budget 94,3k, +28%. 659 ingressi. Piu' della meta' clienti italiani, il freddo li ha fatti uscire tutti.
Beanie nera 8 e Ambrine NERA 8. Quasi tutte le signore entravano chiedendo l'Ambrine cioccolato: in 1 e 2 non c'e', le abbiamo convinte col nero. Almeno 4 delle 8 nere vendute erano clienti che volevano il marrone. Le altre 2-3 sono andate via a pensarci.
Hermine nera 5, Maya blu 6.
Chiesto l'Ilvaro nero in 0, finito.
Resi: un Tib zip (6) e una hoodie S.

Sara
""",
    ),
    dict(
        id="c1019", sent="2026-10-19 20:39", frm="marco", subject="chiusura 19/10",
        business_date="2026-10-19", kind="closing",
        body="""ciao
105,7k vs 75,2 +41%, lunedi da sabato. 60 scontrini, conversione oltre il 10%.
freddo ancora e tanti tedeschi (11%), comprano beanie (nera 8) e piumini: Maya nera 6, Bady 5, Hermine blu 5.
Ambrine marrone chiesta in 1 da 2 signore, niente. Maire nera tg 1 da 3 ragazze.
mancava anche Ilvaro nero 2 e trailgrip grigia 39.
resi: Flammette 1 (zip dura), cable knit XL (pilling), Ilvaro 0, zaino, Tib 3 zip.
Marco
""",
    ),
    dict(
        id="c1020", sent="2026-10-20 21:00", frm="giulia", subject="Chiusura MIL01 - 20/10",
        business_date="2026-10-20", kind="closing",
        body="""Chiusura 20/10
66,7k vs 69,5 (-4%). 466 ingressi, tanti americani.

Bella notizia: il magazzino ci ha confermato che domani arriva il giro con le Maire nere!! Sara ha gia' iniziato a scrivere alle clienti della lista.
Tib bianco 6 pezzi (gli uomini lo prendono lo stesso nonostante i resi...), un ragazzo lo voleva in 6, finito.
Chiesti: cardigan logo nero M (sempre), Ambrine marrone 1, Hermine nera 4, Insolux 40.
Resi: Arneb 3 per taglia, cardigan S regalo.

G.
""",
    ),
    dict(
        id="c1021", sent="2026-10-21 21:25", frm="giulia", subject="Chiusura MIL01 - 21/10 - ARRIVATE LE MAIRE NERE",
        business_date="2026-10-21", kind="closing",
        body="""Ciao a tutti!!
finalmente: stamattina sono arrivate le Maire nere, una sessantina di pezzi su tutta la scala (piu' 1 e 0, poche 00 e 4). Consegna da 467 pz, tutto il back-office sottosopra ma chi se ne importa.
Sara ha chiamato e scritto alla lista: 5 vendute oggi, tre erano clienti in attesa, due walk-in coreane che sono entrate con la foto e sono uscite con la giacca. Domani ne vengono a ritirare altre, almeno 6 hanno confermato.

Numeri: 68,7k su budget 81,1 (-15%), 488 ingressi. Maya nera 7, beanie nera 6, polo nera 4.
Ancora a zero: cardigan logo M nero e blu, Ilvaro nero 0 e 2.

Grazie a chi ci ha spinto in sede.
Giulia
""",
    ),
    dict(
        id="re1021", sent="2026-10-21 22:44", frm="roberto", subject="Re: Chiusura MIL01 - 21/10 - ARRIVATE LE MAIRE NERE",
        to=["giulia"], cc=["ops"], reply_to_id="c1021", kind="reply", suffix="_re1",
        body="""Grande. Venerdi mandami quante ne avete vendute della lista e quante walk-in.
Cardigan M confermato fine mese.
R.
""",
    ),
]
