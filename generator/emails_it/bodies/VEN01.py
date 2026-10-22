# Hand-authored closing emails - VEN01 Venezia San Marco
# Writers: Chiara Zennaro (SM), Luca Boscolo (AM), Marta Tagliapietra (SA, Sundays, from the store mailbox)

PERSONAS = {
    "chiara": "Chiara Zennaro <chiara.zennaro@moncler-retail.example>",
    "luca": "Luca Boscolo <luca.boscolo@moncler-retail.example>",
    "marta": "Marta Tagliapietra <marta.tagliapietra@moncler-retail.example>",
    "store": "Moncler Venezia San Marco <ven01.store@moncler-retail.example>",
    "roberto": "Roberto Galli <roberto.galli@moncler-retail.example>",
    "dl": "retail-ops-italy@moncler-retail.example",
    "facility": "facility-italy@moncler-retail.example",
    "vm": "vm-team@moncler-retail.example",
}

DEFAULT_TO = ["dl"]
DEFAULT_CC = ["roberto"]

EMAILS = []

# ---------------------------------------------------------------- week 1 (31/8 - 6/9)
EMAILS += [
    dict(id="c0831", sent="2026-08-31 20:14", frm="chiara", business_date="2026-08-31",
         subject="Chiusura VEN01 31/08",
         body="""Buonasera a tutti,

VEN01 - chiusura lunedi 31/08
Fatturato: 11,9k (budget 12,3)
Ingressi: 66
Scontrini: 12

Rientro dalle ferie tranquillo. In calle ancora tanti turisti estivi, piu a guardare che a comprare. Il Lido e' pieno per la Mostra del Cinema ma qui non arriva niente, quelli restano la.
Venduti tre cardigan tricot neri (con 29 gradi fuori, ciò) e un paio di marsupi Legere. Qualche coreano nel pomeriggio.

Buona serata
Chiara"""),

    dict(id="ooo0831", sent="2026-08-31 20:14", frm="roberto", to=["chiara"], cc=[], kind="ooo",
         reply_to_id="c0831", suffix="_ooo", headers={"Auto-Submitted": "auto-replied"},
         subject="Risposta automatica: Chiusura VEN01 31/08",
         body="""Sono fuori ufficio con accesso limitato alla posta fino a venerdì 4 settembre. Per urgenze contattare retail-ops-italy@moncler-retail.example.

I am out of office with limited access to email until Friday 4 September. For urgent matters please contact retail-ops-italy@moncler-retail.example.

Roberto Galli"""),

    dict(id="c0901", sent="2026-09-01 20:41", frm="luca", business_date="2026-09-01",
         subject="chiusura VEN 1/9",
         body="""ciao a tt
13,1k vs 11,9 di budget, +10, bene x essere martedi. 63 ingressi 11 scontrini
chiesti e nn avevamo: cardigan tricot grigio XXL, felpa girocollo bianca L, t-shirt logo bianca XL. sempre le taglie grandi che mancano
1 reso t-shirt M x taglia, cambiata con la L
bon, a domani
Luca

Inviato da iPhone"""),

    dict(id="c0903", sent="2026-09-03 20:05", frm="chiara", business_date="2026-09-03",
         subject="Chiusura VEN01 03/09",
         body="""Ciao,
ieri sera me so dimenticata de mandar la chiusura, scusate. Giornata piatta comunque, sotto budget.

Oggi 12,9k su 19,1 di budget. 79 ingressi.
La consegna che aspettavamo per mercoledi e' arrivata stamattina: ieri la barca del corriere non si e' vista, il facchino dice che il camion era arrivato tardi al Tronchetto. 121 pz, controllati, tutto giusto. Pomeriggio passato a sistemare il magazzino.
Gruppo di cinesi con la guida verso le 4, hanno guardato le felpe logo, due navy vendute.
Chiara"""),

    dict(id="c0904", sent="2026-09-04 20:22", frm="chiara", business_date="2026-09-04",
         subject="Chiusura VEN01 04/09",
         body="""VEN01 - venerdi 4/9
Fatturato: 11,6k
Budget: 23,5 (?!)
Ingressi: 91, conversion sotto il 9%

Mi chiedo chi abbia fatto il budget di settembre, siamo a -50 con un venerdi normalissimo. Clienti misti: cinesi, arabi, francesi, coreani, pochissimi italiani. Comprato poco, polo navy, due cardigan tricot neri, una sciarpa cashmere grigia.
Domenica c'e' la Regata Storica, vediamo se porta gente o se la toglie (di solito la toglie, Canal Grande chiuso e tutti sulle rive).
Chiara"""),

    dict(id="c0905", sent="2026-09-05 20:50", frm="luca", business_date="2026-09-05",
         subject="chiusura sabato 5.9",
         body="""13,4k. budget 31. lasciamo stare
134 ingressi ma conversion al 7, gente che entra x l'aria condizionata e basta
venduti 3 tib bianchi (off white) e 2 trailgrip donna neri, una cliente voleva la trailgrip nera in 38 e nn c'era
domani regata, ACTV deviata dal primo pomeriggio
L."""),

    dict(id="c0906", sent="2026-09-06 20:35", frm="store", business_date="2026-09-06",
         subject="Chiusura negozio Venezia domenica 6 settembre",
         body="""Buonasera,
sono Marta, chiudo io oggi perche' Chiara e' di riposo.
Fatturato 12.340 euro, 7 scontrini. Tanti coreani (una coppia ha preso due t-shirt logo nere e il cardigan imbottito) e americani.
Dalle 15 il Canal Grande era chiuso per la Regata e qui in zona San Marco sono rimasti in pochi, erano tutti sulle rive a vedere le barche.
Domani arriva il nuovo calendario turni, lo appendo in back office.
Grazie e buona serata
Marta Tagliapietra
Sales Associate - Venezia San Marco"""),
]

# ---------------------------------------------------------------- week 2 (7/9 - 13/9)
EMAILS += [
    dict(id="c0907", sent="2026-09-07 20:08", frm="chiara", business_date="2026-09-07",
         subject="Chiusura VEN01 07/09",
         body="""Ciao a tutti, bentornato Roberto!

VEN01 - lunedi 7/9
Fatturato: 17,5k (+4% vs budget)
Ingressi: 74
Scontrini: 12

Finalmente un lunedi decente. Vendute 2 Maire nere, 2 Maya neri, 2 Tib off-white e un Ambrine, quello cioccolato, a una signora milanese.
Chiesto il cardigan tricot grigio in XS, non c'e'.
Chiara"""),

    dict(id="c0908", sent="2026-09-08 21:02", frm="luca", business_date="2026-09-08",
         subject="VEN chiusura 8/9",
         body="""12,1 vs 17 budget, -29
91 ingressi
di nuovo la trailgrip nera 38!! seconda volta in 3 giorni, e in + una cliente ha reso la sua 38 x il colore (voleva la bianca, nn l'abbiamo). se al magazzino ce n'e' una nera in 38 mandatecela
le t-shirt logo vanno, 3 oggi
ciao
L"""),

    dict(id="c0909", sent="2026-09-09 20:47", frm="luca", business_date="2026-09-09",
         subject="VEN chiusura 9.9",
         body="""ciao
13,8k, -26 su budget. 95 ingressi 9 scontrini
consegna di oggi NON arrivata, il corriere dice domani o venerdi
1 reso karakorum tg 3 xke stretto, cambiato nn c'era la 4 quindi rimborso
venduto un ilvaro rosa tg 3 a una ragazza coreana, prima volta che vendiamo il rosa
un ragazzo ha chiesto il tib off white in 6, credo nn l'abbiamo mai avuto
Luca
Inviato da iPhone"""),

    dict(id="c0910", sent="2026-09-10 20:19", frm="chiara", business_date="2026-09-10",
         subject="Chiusura VEN01 10/09",
         body="""Ciao,
22,7k vs 21,1 di budget, bene. 107 ingressi.
Due Maire beige e 2 Arneb navy. Sull'Arneb attenzione: veste grande, il cliente provava la sua solita 4 e gli ballava addosso, alla fine ha preso il 3. Da oggi diciamo a tutti di provare una taglia sotto.
Richieste senza stock: Maire nera in 4, pantalone da sci Chamonix nero L, maglione a trecce beige XS, girocollo grigio XL, polo bianca M. Tante cosette diverse.
Maire nera in 1 finita.
La consegna di ieri ancora niente, ho sollecitato il DC.
Chiara"""),

    dict(id="c0911", sent="2026-09-11 20:31", frm="chiara", business_date="2026-09-11",
         subject="Chiusura VEN01 11/09",
         body="""VEN01 - venerdi 11/9
Fatturato: 24,7k (budget 23,6)
Ingressi: 116
Scontrini: 14

Consegna arrivata stamattina, due giorni di ritardo, 129 pz. Il facchino col carrello e' entrato alle 10 e mezza, in piena apertura, e abbiamo fatto il controllo colli in back office lasciando un ragazzo solo in negozio. Chiedo al DC, se possibile, di non farci arrivare le consegne a ridosso dell'apertura.
Dentro altri Ilvaro (nero e bianco) e un Ambrine nero.
Maya nero sempre il piu venduto, 2 oggi. Due Rosiere neri, quello nuovo col velluto piace tanto agli italiani.
Chiara"""),

    dict(id="c0912", sent="2026-09-12 21:10", frm="luca", business_date="2026-09-12",
         subject="chiusura sab 12/9",
         body="""ostrega che sabato
48,2k!! +31 sul budget, 181 ingressi, 30 scontrini
4 maya neri, 4 tib bianchi, 3 dolcevita navy, 3 doposci insolux neri (si, doposci a settembre: famiglia brasiliana che dopo va sulle Dolomiti)
mancati: cardigan tricot grigio L, dolcevita navy M (finita dopo i 3 venduti), polo navy XL
tib navy in 3 finito
biennale + crocieristi arrivati col lancione da fusina tutti insieme verso le 11, x un'ora nn si respirava
bravi tutti, dai che domani si replica
L."""),

    dict(id="c0913", sent="2026-09-13 20:12", frm="store", business_date="2026-09-13",
         subject="Chiusura domenica 13/9 Venezia",
         body="""Ciao a tutti,
domenica buona, 25k circa (+6% sul budget), 136 ingressi.
Il Maya nero continua ad andare, 3 oggi e adesso il 3 e' a zero. Due Hermine navy vendute; una signora americana la voleva anche in 2 per la figlia ma avevamo solo 1 e 3. Poi una ragazza ha chiesto la Valbourg nera in 0 per la settimana bianca, non c'era.
Tanti coreani e americani nel pomeriggio.
Marta"""),
]

# ---------------------------------------------------------------- week 3 (14/9 - 20/9)
EMAILS += [
    dict(id="c0914", sent="2026-09-14 20:03", frm="chiara", business_date="2026-09-14",
         subject="Chiusura VEN01 14.09",
         body="""Ciao,
16,8k, budget 18,3, -8%. 93 ingressi.
Due Bady nere vendute. Chieste e mancanti: polo nera XL (2 clienti diversi!), Bady off-white in 0, gilet Chambre nero in 0.
Reso di una Maire tg 4, era un regalo e la signora ha preferito un credito.
Il Maya nero 3 e' finito ieri, se il magazzino ne ha ce lo mandate? Lo chiedono di continuo.
Chiara"""),

    dict(id="c0915", sent="2026-09-15 20:38", frm="luca", business_date="2026-09-15",
         subject="VEN chiusura 15/9",
         body="""11,6k, -36
97 entrati, tanti cinesi in gruppo con la guida, guardano e vanno. vendute 2 polo bianche e 2 montcla neri
reso 1 bady tg 3, ha cambiato idea
chiesto maglione a trecce nero in L, nn c'e'
umidita' al 90 oggi, il deumidificatore del magazzino fa un rumore strano, scrivo a facility
L"""),

    dict(id="c0916", sent="2026-09-16 20:26", frm="chiara", business_date="2026-09-16",
         subject="Chiusura VEN01 16/09",
         body="""Buonasera,

VEN01 - mercoledi 16/9
Fatturato: 33,5k (+73% !!)
Ingressi: 115
Scontrini: 21

Giornata particolare: il concierge del Gritti ci ha mandato una famiglia americana numerosa, hanno preso 4 Tib neri e 4 cappellini logo neri tutti uguali, padre e figli, piu 2 Maya. Una scena.
Consegna puntuale stamattina, 159 pz.
Una cliente asiatica ha chiesto l'Ilvaro rosa in 3: il 3 l'abbiamo venduto settimana scorsa, in rosa ci restano solo 0, 1 e 2.
Maire nera tg 1 sempre a zero.
Chiara"""),

    dict(id="c0918", sent="2026-09-18 20:15", frm="chiara", business_date="2026-09-18",
         subject="Chiusura VEN01 18/09",
         body="""Ciao,
scusate per ieri, non ho mandato niente: giornata morta, sui 10k, nessuna nave a Fusina e pioggia dalle 3.
Oggi meglio: 29,9k su 26,4 di budget. 151 ingressi.
3 Maya navy, 2 Ilvaro neri, felpe e hoodie nere. Stamattina un gruppo di signore arabe dal Danieli.
Chiesta la Maire nera in 1, sempre lei. Ormai la chiedono una o due volte a settimana e da noi e' finita da una settimana abbondante.
Reso t-shirt S per taglia.
Chiara"""),

    dict(id="c0919", sent="2026-09-19 21:05", frm="luca", business_date="2026-09-19",
         subject="chiusura sabato 19/9",
         body="""52k sabato, +38 sul budget
202 ingressi, 25 scontrini, upt sopra 1,6
maya nero x3, maya oliva x2, zaini makaio neri x2, cardigan tricot navy x2
mancati: hermine nero tg 0 (finita) e karakorum navy tg 2
1 reso felpa L x colore
tanti cinesi e giapponesi, giornata lunga, siamo distrutti
L.

Inviato da iPhone"""),

    dict(id="c0919dup", sent="2026-09-19 21:07", frm="luca", business_date="2026-09-19", kind="dup", suffix="_dup",
         subject="chiusura sabato 19/9",
         body="""52k sabato, +38 sul budget
202 ingressi, 25 scontrini, upt sopra 1,6
maya nero x3, maya oliva x2, zaini makaio neri x2, cardigan tricot navy x2
mancati: hermine nero tg 0 (finita) e karakorum navy tg 2
1 reso felpa L x colore
tanti cinesi e giapponesi, giornata lunga, siamo distrutti
L.

Inviato da iPhone"""),

    dict(id="c0920", sent="2026-09-20 20:20", frm="store", business_date="2026-09-20",
         subject="Chiusura domenica 20/09",
         body="""Buonasera a tutti,
oggi 29k e qualcosa, sopra budget del 13%. 146 ingressi.
Vanno i Maya navy (3 oggi, il 5 e' finito), poi t-shirt e felpe. Una signora svizzera voleva la Maire beige in 0, mi ha lasciato il numero se arriva.
In magazzino a zero anche il Karakorum nero 5.
Buona serata
Marta"""),
]

# ---------------------------------------------------------------- week 4 (21/9 - 27/9)
EMAILS += [
    dict(id="c0921", sent="2026-09-21 20:00", frm="chiara", business_date="2026-09-21",
         subject="Chiusura VEN01 21/09",
         body="""VEN01 - lunedi 21/9
Fatturato: 8,3k (budget 20,9)
Ingressi: 107
Note: lunedi da dimenticare, nessuna nave e pioggia, pochi italiani. Tre resi (gilet Chambre 0, un Montcla 3 per colore, un Tib 3 che ha cambiato idea) che ci hanno mangiato mezza giornata.
Di nuovo chiesto l'Ilvaro rosa in 3, stavolta una ragazza cinese con la foto sul telefono. Poi trecce nero XS, girocollo nero XXL, t-shirt navy XL.
Chiara"""),

    dict(id="c0922", sent="2026-09-22 20:44", frm="luca", business_date="2026-09-22",
         subject="VEN chiusura 22/9",
         body="""24,4k +22, ottimo x un martedi
cinesi 40% abbondante
lista dei mancati oggi lunga, la metto:
- maire nera 1 (ancora)
- hermine off white 4
- bady nera 00
- montcla nero 5
- trecce off white XS
- insolux bianchi 35
venduti 2 tib off white, 2 maya oliva e l'ilvaro rosa in 0
L"""),

    dict(id="c0923", sent="2026-09-23 20:17", frm="chiara", business_date="2026-09-23",
         subject="Chiusura VEN01 23/9",
         body="""Ciao a tutti,
15,3k vs 22,5. 132 ingressi ma conversione al 7,6%, gente che gira e basta.
Consegna di 199 pezzi alle 9, prima dell'apertura come avevo chiesto, grazie DC. Altri Ilvaro e due Ambrine neri: domani con Luca facciamo la vetrina sull'Ambrine come da linee VM.
Vendute 2 Tib navy, 2 Trailgrip donna e 2 maglioni a trecce neri.
Chiara"""),

    dict(id="c0924", sent="2026-09-24 20:55", frm="luca", to=["vm"], cc=[], business_date="2026-09-24",
         subject="Re: vetrine W39 - Ambrine",
         body="""ciao
chiusura di oggi: 19k, -27. 132 ingressi
2 hermine navy, 2 cardigan logo neri, 2 hoodie navy
reso ilvaro tg 0 era un regalo, credito
vetrina ambrine fatta stamattina, viene bene, foto domani
L."""),

    dict(id="c0925", sent="2026-09-25 20:09", frm="chiara", business_date="2026-09-25",
         subject="Chiusura VEN01 25/09",
         body="""Ciao,
Luca ieri ha mandato la chiusura solo al VM (ha risposto alla mail delle vetrine...), ve la riassumo: 19k, -27%, niente di particolare.
Oggi 20,5k su 31,7 di budget, 133 ingressi. Tre berretti logo bianchi, 2 Hermine nere, 2 Bady nere, 2 cardigan logo navy. Tanti coreani in mattinata.
Chiesta t-shirt logo nera XS.
Tib off-white 3 a zero.
Chiara"""),

    dict(id="c0926", sent="2026-09-26 21:20", frm="luca", business_date="2026-09-26",
         subject="chiusura sabato 26.9",
         body="""53,8k, +28. 197 ingressi 27 scontrini
ambrine nero x3!! la vetrina funziona. ilvaro bianco x3, arneb nero x2 (uno ha preso il 4 invece del suo 5, gia' gli stava largo)
richieste nn soddisfatte, tante:
flammette nera 3, ilvaro rosa 3 (terza volta, ma il rosa lo abbiamo mai avuto in negozio??), montgenevre grigio 3, cardigan logo nero L (finito), hoodie navy XL, insolux bianchi 39
2 resi x taglia: tib 1 e cardigan tricot XL
maire nera 0 e 1 e maire navy 0 tutte finite
L"""),

    dict(id="c0927", sent="2026-09-28 09:05", frm="store", business_date="2026-09-27",
         subject="Chiusura domenica 27/9 (scusate il ritardo)",
         body="""Buongiorno,
ieri sera il wifi del negozio e' caduto proprio alla chiusura e non sono riuscita a inviare, mando ora.
Domenica 27/9: 24,8k, budget 30,6. 180 ingressi ma pochi acquisti, tanta gente di passaggio dalle Mercerie.
4 Tib neri, un Polaris oversized nero (il primo!).
Chieste: Flammette nera in 3 da due signore diverse, Tib off-white in 3 sempre da due clienti, Tib navy 4, dolcevita navy L.
Grazie
Marta"""),
]

# ---------------------------------------------------------------- week 5 (28/9 - 4/10) Golden Week starts
EMAILS += [
    dict(id="c0928", sent="2026-09-28 20:11", frm="chiara", business_date="2026-09-28",
         subject="Chiusura VEN01 28/09",
         body="""VEN01 - lunedi 28/9
Fatturato: 23,1k (in linea col budget)
Ingressi: 116
Scontrini: 21, tanti piccoli

Molti americani oggi, sbarcati stamattina da una nave a Fusina. T-shirt, Insolux neri, 2 Arneb neri.
Chiesti: Maire nera 0, dolcevita navy L, t-shirt navy XL.
Un Maya 3 reso per taglia, cambiato col 4.
Da mercoledi parte la settimana d'oro cinese: Luca sta rivedendo i turni per avere Andrea (quello che parla mandarino) tutti i pomeriggi.
Chiara"""),

    dict(id="c0929", sent="2026-09-29 20:50", frm="luca", business_date="2026-09-29",
         subject="VEN chiusura 29.9",
         body="""18,5k -22
reso un tib tg 3 con la zip rotta: il cursore si blocca a meta' e nn sale piu. il cliente l'aveva preso a fine agosto. fatto reso, il capo l'ho messo da parte in back office, nn rimesso in vendita
altro reso maire tg 0 x qualita' (cucitura della tasca aperta)
mancati: arneb navy 5, valbourg nera 1, felpa grigia M
arneb nero 3 finito
L."""),

    dict(id="c0930", sent="2026-09-30 20:24", frm="chiara", business_date="2026-09-30",
         subject="Chiusura VEN01 30/09",
         body="""Ciao a tutti,
primo giorno di Golden Week e si sente gia': un terzo di clienti cinesi, 167 ingressi. Fatturato 28,3k (+6%).
Consegna da 207 pz puntuale.
Due resi: una Flammette tg 1 per qualita' (piuma che usciva dalla cucitura) e un Maya 1 regalo.
Venduto un altro Polaris oversized. Marsupi Legere e hoodie neri sempre.
Chiara"""),

    dict(id="c1001", sent="2026-10-01 20:32", frm="chiara", business_date="2026-10-01",
         subject="Chiusura VEN01 01/10",
         body="""VEN01 - giovedi 1/10
Fatturato: 39k (+31%)
Ingressi: 146
Scontrini: 18

Golden Week piena, quasi meta' clienti cinesi. Tre cardigan logo neri, 3 Bady nere, 2 Maya oliva e un Ambrine cioccolato.
Mancati: Bady nera in 4, e una ragazza ha chiesto l'Ilvaro rosa, in 0 stavolta (l'ultimo 0 l'abbiamo venduto la settimana scorsa).
Altri 2 Tib resi per la zip (tg 3 e 4), stesso difetto di martedi, il cursore che si incastra. Sono gia' 3, comincia a essere strano.
Chiara"""),

    dict(id="c1002", sent="2026-10-02 21:01", frm="chiara", business_date="2026-10-02",
         subject="Chiusura VEN01 02/10",
         body="""Ciao,
40,2k, +16% sul budget. 213 ingressi, il massimo da inizio settembre. Cinesi oltre il 40%.
4 hoodie navy, 3 berretti bianchi, 3 Tib neri, 2 Polaris oversized (il Genius si muove, ma solo coi cinesi).
Ancora la Maire nera: 0 e 1, due clienti. E cardigan logo nero XL.
Tib: oggi TRE resi per la zip (tg 2, 3 e 5). Siamo a 6 da martedi, tutti con lo stesso problema del cursore. Li teniamo da parte. Roberto, chi devo avvisare? Li rimandiamo al DC?
Ah, la storia del rosa: Marta mi ha fatto vedere su Instagram che ieri a Parigi una cantante k-pop aveva l'Ilvaro rosa. Prepariamoci che lo chiederanno ancora di piu.
Chiara"""),

    dict(id="r1002", sent="2026-10-02 22:16", frm="roberto", to=["chiara"], cc=["luca"], kind="reply",
         reply_to_id="c1002", suffix="_re1",
         subject="Re: Chiusura VEN01 02/10",
         body="""Chiara mandami foto della zip e taglie/date di acquisto se le hai. Lo giro a qualita' e merch, mi sa che non siete i soli.
Per ora non rimettete in vendita e non spedite niente finche non vi dico io.
Bravi per la settimana!
R.

Inviato da iPhone"""),

    dict(id="a1003", sent="2026-10-03 10:12", frm="chiara", to=["roberto"], cc=["luca"], kind="reply",
         reply_to_id="r1002", suffix="_re2",
         attachments=[{"name": "IMG_5521.jpg"}, {"name": "IMG_5522.jpg"}, {"name": "IMG_5524.jpg"}],
         subject="Re: Chiusura VEN01 02/10",
         body="""Ciao Roberto,
in allegato le foto. Resi per la zip fino a ieri:
29/9 tg 3
1/10 tg 3 e 4
2/10 tg 2, 3 e 5
Comprati tra fine agosto e meta' settembre, credo stessa consegna di agosto. Il cursore si apre a meta' e poi la zip si separa sotto.
Abbiamo controllato i Tib in negozio: un paio hanno il cursore duro, tolti dalla vendita anche quelli.
Chiara"""),

    dict(id="c1003", sent="2026-10-03 21:30", frm="luca", business_date="2026-10-03",
         subject="chiusura sab 3/10",
         body="""SABATO DA PAZZI
76,4k, +37 sul budget. 315 ingressi, 38 scontrini
cinesi dappertutto, guide con la bandierina in calle, nel pomeriggio fila fuori x un'ora, li facevamo entrare a gruppi di 10
4 sciarpe cashmere nere, 4 cappellini neri, 4 trecce neri, 4 girocollo neri
mancati: hermine nero 00, hermine off white 2, chambre nero 3, polaris oversized nero M, trecce nero L (finito)
1 tib reso zip tg 4, lo aggiungo alla lista di chiara
resi anche un maya 3 x taglia e un cardigan logo XL
grazie a tt, domani si ricomincia
L.
Inviato da iPhone"""),

    dict(id="k1003", sent="2026-10-03 22:05", frm="luca", kind="correction", suffix="_corr",
         reply_to_id="c1003", business_date="2026-10-03",
         subject="R: chiusura sab 3/10 - CORREZIONE",
         body="""scusate ho girato i numeri, oggi abbiamo fatto 67,4k e non 76,4. il +37 sul budget e' giusto
L."""),

    dict(id="c1004", sent="2026-10-04 20:40", frm="store", business_date="2026-10-04",
         subject="Chiusura domenica 4 ottobre",
         body="""Buonasera,
altra domenica piena: 43,5k, +35%. 192 ingressi, 41% cinesi.
4 Maya neri, 2 cardigan logo navy, 2 girocollo neri, 2 cardigan tricot navy.
Chieste: Hermine navy in 0 da due clienti (una cinese e una italiana), Hermine off-white 2, trecce nero L, t-shirt bianca XL.
Una guida cinese ci ha chiesto se la settimana prossima possiamo restare aperti fino alle 20 per i suoi gruppi che rientrano tardi da Burano, lo giro a Chiara.
Marta"""),
]

# ---------------------------------------------------------------- week 6 (5/10 - 11/10)
EMAILS += [
    dict(id="c1005", sent="2026-10-05 20:13", frm="chiara", business_date="2026-10-05",
         subject="Chiusura VEN01 5/10",
         body="""Ciao,
33k, +37% sul budget, un lunedi cosi non me lo ricordo. 172 ingressi, piu di meta' cinesi.
Mancato il gilet Chambre nero in 0, due volte, poi t-shirt navy S e Insolux off-white 38.
Finiti Ilvaro nero 2 e Maya oliva 4.
Per la richiesta della guida di cui scriveva Marta ieri (restare aperti fino alle 20): Roberto, si puo'? Io farei mercoledi e giovedi, con Andrea che parla mandarino.
Chiara"""),

    dict(id="r1005", sent="2026-10-05 22:01", frm="roberto", to=["chiara"], cc=["luca"], kind="reply",
         reply_to_id="c1005", suffix="_re1",
         subject="Re: Chiusura VEN01 5/10",
         body="""ok mer e gio fino alle 20, avvisa HR per gli straordinari e mettilo sulla porta. poi mi dici quanto fate nell'ultima mezz'ora
R."""),

    dict(id="c1006", sent="2026-10-06 20:52", frm="luca", business_date="2026-10-06",
         subject="chiusura 6/10",
         body="""27k, +12
136 ingressi
5 maya neri!! maya nero 5 finito
mancati: ilvaro off white 0, chambre nero 2, polo nera XL, trailgrip donna nera 35
resi: montcla 7 cambio idea, tib 2 zip (e siamo a 8)
L"""),

    dict(id="c1007", sent="2026-10-07 21:12", frm="chiara", business_date="2026-10-07",
         subject="Chiusura VEN01 07/10",
         body="""VEN01 - mercoledi 7/10
Fatturato: 27,6k (in linea)
Ingressi: 153
Scontrini: 15
Note: due clienti su tre erano cinesi. Prima sera aperti fino alle 20, nell'ultima mezz'ora sono entrati due gruppi ma hanno fatto solo 2 scontrini piccoli.
Consegna grossa, 269 pz, fatica a sistemarla col negozio pieno. Venduti 3 Tib neri e 3 cardigan tricot neri.
Un altro Tib reso per la zip, tg 4. Nove.
Maire nera in 0 chiesta ancora, nella consegna di Maire nere neanche l'ombra.
Chiara"""),

    dict(id="c1008", sent="2026-10-08 21:08", frm="chiara", business_date="2026-10-08",
         subject="Chiusura VEN01 08/09",
         body="""Ciao a tutti,
ultimo giorno di Golden Week, 30,8k (+6%), 185 ingressi ma conversione sotto il 9%: gruppi che entrano tutti insieme, girano e ripartono.
Ancora Maire nera in 0, e una Flammette nera in 00.
Venduto un altro Ambrine marrone. Reso Insolux 38, cambio idea.
Dal weekend torniamo a numeri normali credo. Bel lavoro della squadra in queste due settimane, sono orgogliosa.
Chiara"""),

    dict(id="c1009", sent="2026-10-09 21:00", frm="luca", business_date="2026-10-09",
         subject="chiusura ven 9/10",
         body="""44k +29, nn me l'aspettavo dopo la golden week
tanti americani, 3 passamontagna polaris bianchi (!), 3 tib navy, 2 dolcevita neri
1 tib reso zip tg 5, 10 in tutto
conversion 17%, ci voleva
L."""),

    dict(id="c1011", sent="2026-10-11 21:15", frm="luca", business_date="2026-10-10,2026-10-11",
         subject="chiusura weekend 10-11/10",
         body="""ciao, mando sabato e domenica insieme che ieri sera sono uscito tardi

SAB 10: 26,8k, budget 49 (!). 213 ingressi, conv 9. pioggia tutto il giorno, gente che entrava x ripararsi. 4 karakorum neri
DOM 11: 24,2k, -33. 141 ingressi. 3 arneb neri, 2 hermine navy

mancati nel weekend: karakorum nero 3 (due clienti, adesso finito), ilvaro nero 3, rosiere nero 2, chamonix nero XL, cardigan tricot grigio XXL
resi: arneb tg 1 cambiato x taglia (troppo grande, come sempre), maya 3 regalo, arneb 3 regalo

L."""),
]

# ---------------------------------------------------------------- week 7 (12/10 - 18/10)
EMAILS += [
    dict(id="c1012", sent="2026-10-12 20:06", frm="chiara", business_date="2026-10-12",
         subject="Chiusura VEN01 12/10",
         body="""8,5k. 116 ingressi, 9 scontrini.
Dopo la Golden Week il vuoto: niente navi, pochi italiani, pioggia a tratti. Solo cose piccole, 2 Karakorum navy e accessori.
Chiara"""),

    dict(id="c1013", sent="2026-10-13 20:40", frm="luca", business_date="2026-10-13",
         subject="chiusura 13/10",
         body="""12,6k, -51
121 ingressi
3 resi: hermine 0 x taglia, karakorum 2 x qualita' (bottone automatico staccato), tib 3 zip. il tib e' l'undicesimo
dolcevita nero L chiesto e nn c'e
da qualita' ancora niente sui tib? li abbiamo tutti in un sacco in back office che occupano mezzo scaffale
L"""),

    dict(id="c1014", sent="2026-10-14 20:21", frm="chiara", business_date="2026-10-14",
         subject="Chiusura VEN01 14/10",
         body="""Ciao,

VEN01 - mercoledi 14/10
Fatturato: 15,8k
Budget: 29,7
Ingressi: 123

Consegna 222 pz ok. Dentro finalmente 2 Ilvaro rosa, in 0 e in 3, proprio le taglie che ci chiedevano. Li ho messi subito in vetrina interna. Venduti 4 hoodie neri e 2 berretti rosa (chissa' se c'entra la cantante).
Un Arneb tg 4 reso, troppo grande, il cliente non ha voluto il 3 e ha preso il rimborso. Un Tib tg 2 reso per qualita' (questa volta non e' la zip, e' una macchia sul laqué).
Chiara"""),

    dict(id="c1015", sent="2026-10-15 20:48", frm="chiara", business_date="2026-10-15",
         subject="Chiusura VEN01 15/10 !!",
         body="""Buonasera!

VEN01 - giovedi 15/10
Fatturato: 50,2k (+50%)
Ingressi: 150
Scontrini: 25, conversione quasi 17%

Giornata pazzesca e inaspettata. Una VIC di Treviso del mio client book e' venuta con figli e nipoti: 5 berretti bianchi, felpe, 2 Polaris cape nere. Nel pomeriggio tanti italiani in giro per la Biennale.
Due clienti diverse volevano gli Insolux off-white in 38, niente.
Maire nera adesso a zero anche in 2.
Domani sciopero generale, ACTV a servizio ridotto e treni a rischio. Marta e Andrea vengono da Mestre, vediamo. Apriamo comunque.
Chiara"""),

    dict(id="c1016", sent="2026-10-16 21:05", frm="luca", business_date="2026-10-16",
         subject="chiusura 16/10 sciopero",
         body="""19,2k, -50. sciopero
vaporetti a singhiozzo, linee 1 e 2 quasi ferme la mattina, in calle meta' gente del solito. 103 ingressi
marta arrivata alle 11 (treno soppresso, bus fino a piazzale roma e poi a piedi), andrea a mezzogiorno
resi: maya 4 regalo, tib 5 cambio idea, tib 3 zip (12)
ilvaro nero 0 finito
L."""),

    dict(id="c1017", sent="2026-10-17 21:15", frm="luca", business_date="2026-10-17",
         subject="chiusura sab 17/10",
         body="""56,5k, +5. 267 ingressi
5 cardigan logo neri, 5 montcla neri, 4 polaris cape nere (il genius qui va solo con la cape, l'oversized poco)
mancati: maire nera 0, cardigan logo nero XL, hoodie nera XL
1 reso zaino makaio
sabato ok ma tanti ingressi e conv al 10, troppa gente x 4 persone in negozio. se a novembre ci date un rinforzo il sabato...
L"""),

    dict(id="c1018", sent="2026-10-18 20:25", frm="store", business_date="2026-10-18",
         subject="Chiusura domenica 18/10",
         body="""Buonasera,
21k, sotto budget (-38%). 115 ingressi. Domenica tranquilla, tanti brasiliani e francesi.
2 Rosiere neri, 2 Hermine navy, 2 Bady nere. Un signore voleva il Rosiere oliva in 3, non c'era.
Il Centro Maree da' acqua alta per martedi mattina, domani ne parliamo con Chiara.
Marta"""),
]

# ---------------------------------------------------------------- 19/10 - 21/10 acqua alta
EMAILS += [
    dict(id="c1019", sent="2026-10-19 20:10", frm="chiara", business_date="2026-10-19",
         subject="Chiusura VEN01 19/10",
         body="""VEN01 - lunedi 19/10
Fatturato: 8k
Ingressi: 104
Note: lunedi vuoto, -70%. In calle si parla solo della marea di domani. Stamattina la previsione era 105, adesso dicono 115-120 verso le 9 e 45. Il MOSE in teoria lo alzano sopra i 110, ma conferma ancora non c'e'.
Abbiamo gia' sollevato i cartoni del magazzino sui bancali e preparato la paratia per la porta. Domattina vi aggiorno presto.
Resi: Arneb 4 cambiato col 3 (il solito), una felpa e un paio di guanti.
Chieste hoodie nere XXL (due clienti) e polo navy XXL.
Chiara"""),

    dict(id="f1019", sent="2026-10-19 22:40", frm="chiara", to=["dl", "facility"], cc=["roberto", "luca"], kind="fwd",
         suffix="_fwd", business_date="2026-10-19",
         subject="I: AVVISO MAREA - aggiornamento ore 22:00",
         body="""Vi giro l'ultimo aggiornamento del Centro Maree, ora danno 118 per domattina. Domani alle 7.30 vi scrivo se apriamo regolarmente o no.
Chiara

---------- Messaggio inoltrato ----------
Da: Comune di Venezia - Centro Previsioni e Segnalazioni Maree <avvisi.maree@comune.venezia.example>
Data: lun 19 ott 2026 alle ore 22:12
Oggetto: AVVISO MAREA - aggiornamento ore 22:00
A: <chiara.zennaro@moncler-retail.example>

CENTRO PREVISIONI E SEGNALAZIONI MAREE
Aggiornamento del 19/10/2026 ore 22:00

Previsione massimi di marea (rif. Punta della Salute):
mar 20/10 ore 09:45  cm 118
mar 20/10 ore 22:20  cm 80

Stato: MAREA MOLTO SOSTENUTA (110-139 cm)
Segnalazione acustica prevista nelle prime ore del mattino.
Sistema MOSE: valutazione sollevamento in corso, seguiranno aggiornamenti.

Messaggio automatico, non rispondere."""),

    dict(id="m1020", sent="2026-10-20 07:42", frm="chiara", to=["dl"], cc=["roberto", "facility"], kind="misc",
         suffix="_alert", business_date="2026-10-20",
         subject="VEN01 - oggi apriamo alle 12 (acqua alta)",
         body="""Buongiorno,
la marea e' salita piu del previsto, il MOSE l'hanno alzato tardi e la piazza e' gia' sotto. In calle davanti al negozio saranno 30-40 cm, passerelle montate solo in parte. La paratia regge, dentro per ora asciutto.
Alle 10 non riusciamo ad aprire: io sono qui con gli stivali, Luca e Marta bloccati coi vaporetti deviati. Apriamo alle 12 se l'acqua cala come dicono.
Vi aggiorno.
Chiara

Inviato da iPhone"""),

    dict(id="c1020", sent="2026-10-20 20:30", frm="chiara", business_date="2026-10-20",
         subject="Chiusura VEN01 20/10 - acqua alta",
         body="""Ciao a tutti,
giornata da dimenticare, vi riassumo:
- aperto alle 12:00. L'acqua in calle e' scesa verso le 11 e mezza, abbiamo tolto la paratia e asciugato l'ingresso
- merce nessun danno, avevamo alzato tutto ieri sera. Un po' d'acqua e' risalita dai tombini nel vestibolo, lo zerbino e' da buttare
- Luca arrivato alle 11:40, Marta alle 12:30
- 38 ingressi, 4 scontrini, quasi 4k (budget 27,9). Qualche italiano e due tedeschi con gli stivali di plastica comprati in piazza
- venduti 2 Maya neri, un maglione a trecce, una Bady, un gilet Chambre
- resi: cardigan tricot L cambio idea, un Tib 5 per la zip (siamo a 13)
Domani la previsione e' sui 90, dovremmo aprire normalmente.
Chiara"""),

    dict(id="r1020", sent="2026-10-20 21:48", frm="roberto", to=["chiara"], cc=["luca"], kind="reply",
         reply_to_id="c1020", suffix="_re1",
         subject="Re: Chiusura VEN01 20/10 - acqua alta",
         body="""Chiara grazie, brava a tutti.
Due cose: danni a struttura/impianti? quadro elettrico, magazzino, vetrine. E apri la segnalazione a facility per l'assicurazione anche se e' solo lo zerbino, con foto, serve per lo storico.
Domani mi dici.
R."""),

    dict(id="a1021", sent="2026-10-21 09:25", frm="chiara", to=["roberto"], cc=["facility", "luca"], kind="reply",
         reply_to_id="r1020", suffix="_re2",
         attachments=[{"name": "IMG_6038.jpg"}, {"name": "IMG_6039.jpg"}, {"name": "IMG_6041.jpg"}, {"name": "IMG_6044.jpg"}],
         subject="Re: Chiusura VEN01 20/10 - acqua alta",
         body="""Ciao Roberto,
stamattina abbiamo controllato tutto con calma.
Quadro elettrico ok, e' in alto. Magazzino asciutto, i cartoni erano tutti sui bancali. Vetrine ok.
L'unico danno vero e' il pavimento del vestibolo: la pietra ha l'alone bianco del sale e lo zerbino e' da cambiare. Il bordo della moquette nel camerino 1 ha preso un fia' di umido, la teniamo d'occhio.
Ho aperto la segnalazione con facility (in copia) con le foto in allegato. Per l'assicurazione aspetto indicazioni da loro.
Chiara"""),

    dict(id="c1021", sent="2026-10-21 20:50", frm="luca", business_date="2026-10-21",
         subject="chiusura 21/10",
         body="""ciao
18k, -42. 130 ingressi, tornato qualche turista, francesi e cinesi, pochi
consegna 233 pz arrivata col corriere nonostante tutto, sistemata nel pomeriggio. DENTRO 25 MAIRE NERE, finalmente, dalla 00 alla 4. e altri 2 ilvaro rosa
chiesto ilvaro nero 2, finito (anche lo 0)
reso un gilet chambre 0 x taglia
dopo ieri ci voleva un fia' di respiro, bon
L."""),
]
