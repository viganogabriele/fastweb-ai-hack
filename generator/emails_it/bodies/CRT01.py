# CRT01 Cortina d'Ampezzo - hand-authored closing emails (see notes/CRT01.md)

PERSONAS = {
    "martina": "Martina Menardi <martina.menardi@moncler-retail.example>",
    "davide": "Davide Dibona <davide.dibona@moncler-retail.example>",
    "store": "Moncler Cortina <crt01.store@moncler-retail.example>",
    "roberto": "Roberto Galli <roberto.galli@moncler-retail.example>",
}

DEFAULT_TO = ["retail-ops-italy@moncler-retail.example"]
DEFAULT_CC = ["roberto"]

EMAILS = [
    dict(id="c0831", sent="2026-08-31 20:25", frm="martina", subject="CRT01 chiusura 31/08",
         business_date="2026-08-31", body="""CRT01 - chiusura 31/08
Fatt: 4.750 EUR (bdg 6.000)
Ingressi: 38
Scontrini: 8
Note: lunedi tranquillo, finita l'onda di agosto e si sente. qlc italiano rimasto, un paio di cinesi e due coppie americane dall'hotel qui davanti.
Richieste: Bady rosa cipria tg 4 (nn c'e'), Marin navy 6 (nn c'e')
Resi: 1 Bady (taglia) e una Trailgrip 45 tornata indietro, si stacca la suola in punta dopo 2 settimane. messa da parte x il reso qualita.

Buona serata
Martina"""),

    dict(id="c0901", sent="2026-09-01 21:05", frm="davide", subject="chiusura crt 1/9",
         business_date="2026-09-01", body="""bondi a tutti
4,4k oggi, 4 scontrini su 34 ingressi. tedeschi inglesi e qlc italiano, niente di che.
venduto una t-shirt bianca, cardigan logo nero, una Maya nera e un Montgenevre nero, tutti scontrini singoli.
martina riposo, domani rientra lei.
dav"""),

    dict(id="c0901_ooo", sent="2026-09-01 21:06", frm="roberto", to=["davide"], cc=[],
         subject="Risposta automatica: chiusura crt 1/9", reply_to_id="c0901", kind="ooo", suffix="_ooo",
         headers={"Auto-Submitted": "auto-replied"},
         body="""Sono fuori ufficio con accesso limitato alla posta fino a venerdì 4 settembre. Per urgenze contattare retail-ops-italy@moncler-retail.example.

I am out of office with limited access to email until Friday 4 September. For urgent matters please contact retail-ops-italy@moncler-retail.example.

Roberto Galli"""),

    dict(id="c0902", sent="2026-09-02 20:40", frm="martina", subject="CRT01 chiusura 02/09",
         business_date="2026-09-02", body="""CRT01 - chiusura 02/09
Fatt: 8.720 (bdg 6.080) +43%
Ingressi: 44 / Scontr: 9
Arrivata la consegna di CSG stamattina, 34 pz, tutto ok, controllata con Davide e gia' messa giu.
Bene i tedeschi oggi, coppie in giro x le Dolomiti in moto, entrano bagnati di pioggia e comprano cappellino e hoodie :) venduto anche una Trailgrip grigia e una nera.
Richieste: Ecrins nero tg 7, Tib navy tg 7 (le 7 qui nn arrivano mai), Peyre nero 6.
Un reso: Chambre, la signora ci ha ripensato.
Martina"""),

    dict(id="c0904", sent="2026-09-04 20:15", frm="martina", subject="CRT01 chiusura 04/09",
         business_date="2026-09-04", body="""CRT01 - chiusura 04/09
Fatt: 8.470 / bdg 10,5k
Ingressi 57, scontrini 6
Scusate ieri sera nn ho mandato niente, giornata morta e poi sono scappata, non c'era molto da raccontare comunque.
Oggi meglio, primi milanesi del weekend gia dal pomeriggio + 2 famiglie giapponesi che facevano il giro Cinque Torri/Falzarego. Guanti tech, t-shirt navy, cable knit bianco e una Maya navy.
Mancano: pantalone Chamonix nero in XS (ragazza giapponese, l'XS da noi non c'e' proprio) e polo bianca XS.
M."""),

    dict(id="c0905", sent="2026-09-05 21:10", frm="martina", subject="CRT01 chiusura 05/09",
         business_date="2026-09-05", body="""CRT01 - chiusura sabato 05/09
Fatt: 14.670 (bdg 13.130) +12%
Ingressi: 93 !!
Scontrini: 11
Finalmente un sabato vero. Corso Italia pieno fino alle 7, meteo bellissimo, tutti su a Faloria e poi giu a passeggiare. Italiani soprattutto (milanesi e padovani), americani dagli hotel. 2 cappellini logo neri, 2 cardigan logo, un pantalone Chamonix, polo navy.
Chiesto ancora il Chamonix nero, stavolta in S: finito, avevamo l'unico S e l'ha preso stamattina una signora. Se CSG ne ha due tre in S/XS ci servono, qualche settimana di montagna d'estate c'e' ancora.
Martina"""),

    dict(id="c0906", sent="2026-09-06 20:35", frm="davide", subject="chiusura dom 6/9",
         business_date="2026-09-06", body="""58 ingressi e 1 scontrino. UNO.
3,2k grazie a un signore di Padova che ha preso Karakorum navy e polo nera + Hermine nera x la moglie, tutto sullo stesso scontrino.
tutti italiani, giro in centro dopo pranzo, guardano e vanno. il Karakorum lo voleva anche un altro in tg 3, finita. chiesto anche Rosiere verde oliva 5 e cable knit bianco XXL, niente.
reso un cardigan logo S, cambiato idea.
dav"""),

    dict(id="c0907", sent="2026-09-07 20:05", frm="martina", subject="CRT01 chiusura 07/09",
         business_date="2026-09-07", body="""CRT01 - chiusura 07/09
Fatt 4.670 / bdg 6.950
Ingressi 43 - scontrini 4
Lunedi lento. 2 Ecrins neri venduti a due fratelli giapponesi (uno ha preso la 4 xke la 3 e' finita, gli stava bene lo stesso). Per il resto t-shirt, hoodie navy e un cable knit nero.
Il pomeriggio e' venuta pioggia, Corso vuoto.
Martina"""),

    dict(id="c0908", sent="2026-09-08 20:50", frm="davide", to=["retail-ops-spain@moncler-retail.example"],
         subject="chiusura crt 8/9", business_date="2026-09-08", body="""7,5k +7% su bdg, 5 scontrini, 38 ingressi.
venduto 2 Maire nere (una a una signora svizzera di Lugano, una a una ragazza indiana), il beanie, zaino Makaio navy e una Maya navy.
attenzione Maire nera: ora siamo corti, rimaste poche taglie. se c'e' da riassortire meglio prima del weekend.
dav"""),

    dict(id="c0909", sent="2026-09-09 20:30", frm="martina", subject="CRT01 chiusura 09/09",
         business_date="2026-09-09", body="""CRT01 - chiusura 09/09
Fatt: 11.170 (bdg 7.050) +58%
Ingressi: 42 / Scontrini: 11
Arrivati 33 pz da CSG, tutto giusto.
Giornata stranissima x essere mercoledi: coppia di Dubai che ha preso 2 Maire nere (mamma e figlia), poi americani, inglesi. 2 beanie, 2 trailgrip nere, 2 t-shirt navy.
Adesso la Maire nera ce l'abbiamo solo in 1 e 3, la 0 e la 2 sono finite. Davide ieri ve l'aveva scritto, qualcuno puo' verificare se arriva qlc?
Richieste nn soddisfatte: Karakorum navy 2, Tib bianco tg 1, cable knit nero XS.
Reso cable knit S (cambio idea).
Martina"""),

    dict(id="c0910", sent="2026-09-10 20:10", frm="store", subject="Chiusura Cortina 10.09",
         business_date="2026-09-10", body="""Buonasera,
di seguito la chiusura di oggi giovedì 10 settembre.
Incasso 2.570 euro, 3 scontrini, 33 ingressi.
Venduti un berretto logo nero, una felpa con cappuccio nera e un Rosiere nero.
Giornata con pioggia quasi tutto il giorno, pochissimo passaggio sul Corso. Un cliente ha chiesto quando arriva la collezione sci Grenoble completa.
Martina oggi era in ferie, Davide di riposo.
Cordiali saluti
Silvia Lacedelli
Moncler Cortina d'Ampezzo - Corso Italia"""),

    dict(id="c0911", sent="2026-09-11 20:45", frm="martina", subject="CRT01 chiusura 11/09",
         business_date="2026-09-11", body="""Fatt. 8.780 vs 9.080 bdg, quasi in pari
60 ingressi, 5 scontrini
pantalone Chamonix nero (in M, l'S nn c'e' piu), cappellino navy, polo nera, hoodie nero.
una signora milanese voleva la Maire nera in 2, ovviamente niente. le ho proposto la navy ma lei voleva il nero e basta. ha lasciato il numero, se arriva la chiamo io.
cmq tanti ciclisti in giro, il weekend promette bene.
M."""),

    dict(id="c0912", sent="2026-09-12 21:00", frm="martina", subject="CRT01 chiusura 12/09",
         business_date="2026-09-12", body="""CRT01 - sabato 12/09
Fatt 11.530 (bdg 12.790) -10%
Ingressi 80, scontrini 7
Molta gente ma tanti giri di prova e poi "ci pensiamo". 2 Hermine nere a due amiche di Treviso, beanie, Chamonix, tricot cardigan navy.
Emiratini e francesi oltre agli italiani.
Reso felpa logo XL, la voleva grigia invece che nera.
Domani sono di riposo, chiude Davide.
Martina"""),

    dict(id="c0913", sent="2026-09-13 20:40", frm="davide", subject="chiusura domenica 13",
         business_date="2026-09-13", body="""ciao a tt
domenica incredibile, 15k (bdg 8,4) con 47 ingressi soltanto. inglesi (un gruppo di amici di Londra in giro x le Dolomiti, hanno preso 2 Rosiere nere e 2 Maire navy x le mogli), qlc indiano e italiani.
+ cappellino nero e polo nera.
oggi tutti ingressi buoni, conversione altissima, 10 scontrini.
Maire nera sempre zero nelle taglie piccole, la navy invece va.
dav"""),

    dict(id="c0913_dup", sent="2026-09-13 20:44", frm="davide", subject="chiusura domenica 13",
         business_date="2026-09-13", kind="dup", suffix="_dup", body="""ciao a tt
domenica incredibile, 15k (bdg 8,4) con 47 ingressi soltanto. inglesi (un gruppo di amici di Londra in giro x le Dolomiti, hanno preso 2 Rosiere nere e 2 Maire navy x le mogli), qlc indiano e italiani.
+ cappellino nero e polo nera.
oggi tutti ingressi buoni, conversione altissima, 10 scontrini.
Maire nera sempre zero nelle taglie piccole, la navy invece va.
dav"""),

    dict(id="c0914", sent="2026-09-14 20:10", frm="martina", subject="CRT01 chiusura 14/09",
         business_date="2026-09-14", body="""Fatt 5.170 / 6.420 bdg
Ingressi 35, 4 scontrini
guanti, hoodie nero, dolcevita nero, e un Arneb nero a un signore cinese: gli ho fatto provare la sua taglia e quella sotto, ha preso la sotto. l'Arneb veste abbondante, lo dico a tutti.
Settimana che si annuncia lunga, alcuni hotel chiudono gia domenica prossima.
M."""),

    dict(id="c0915", sent="2026-09-16 08:40", frm="davide", subject="chiusura ieri 15/9",
         business_date="2026-09-15", body="""scusate ieri sera mi si e' spento il tel e nn ho mandato.
ieri 590 euro. un hoodie nero. fine.
38 ingressi, nessuno con intenzione di comprare, qlc anziano a guardare le vetrine e due ragazzi a chiedere se cerchiamo personale x l'inverno (ho dato la mail di Martina).
dav"""),

    dict(id="c0916", sent="2026-09-16 20:35", frm="martina", subject="CRT01 chiusura 16/09",
         business_date="2026-09-16", body="""CRT01 - 16/09
Fatt: 7.550 (+25% su bdg)
Ingressi 38 / scontrini 7
Arrivati 43 pz da CSG, controllati, ok. Dentro anche qlc Tib e infatti 2 Tib navy venduti oggi, piu guanti, Peyre nero e hoodie navy.
Reso felpa M x taglia (presa la L).
Martina"""),

    dict(id="c0917", sent="2026-09-17 20:20", frm="martina", subject="CRT01 chiusura 17/09",
         business_date="2026-09-17", body="""Fatt. 4.880 su 7.270
40 ingressi, 4 scontrini
2 Montcla navy a una coppia coreana (lui e il suocero, carinissimi), Trailgrip nera, hoodie nero e un gilet Chambre.
Il terzo Montcla lo volevano in 7, non c'e'.
Passata anche una signora milanese che ha casa a Pocol, cercava l'Ambrine marrone in 2, l'aveva vista su instagram. Noi l'Ambrine marrone non l'abbiamo mai avuta. Si puo' sapere se ne arriva qualcuna anche qui o e' solo x Milano?
Ennesimo reso felpa (S, taglia). Le felpe vestono piccole o e' una mia impressione?
Martina"""),

    dict(id="c0918", sent="2026-09-18 20:15", frm="store", subject="Chiusura Cortina 18.09",
         business_date="2026-09-18", body="""Buonasera,
chiusura di venerdì 18 settembre.
Incasso 8.520 euro su un budget di 8.240, 4 scontrini, 45 ingressi.
Nel pomeriggio è passato un gruppo di turisti cinesi con la guida (tour Venezia-Dolomiti, sosta di due ore a Cortina con visita alla pista da bob olimpica). Hanno acquistato soprattutto accessori: berretti, cappellini, una Trailgrip grigia e una polo navy.
Richieste che non abbiamo potuto soddisfare:
- Maire nera taglia 00
- Maire beige taglia 3
- t-shirt logo navy XL
Cordiali saluti
Silvia Lacedelli
Moncler Cortina d'Ampezzo - Corso Italia"""),

    dict(id="c0920_wk", sent="2026-09-20 20:50", frm="davide", subject="weekend 19-20 crt",
         business_date="2026-09-19,2026-09-20", body="""ciao, faccio un'unica mail x sabato e domenica che ieri ho chiuso tardi.

SAB 19: 7,9k (bdg 11,1) 59 ingressi 7 scontrini. tantissimi americani, una comitiva da un hotel di lusso a Pocol, 2 beanie bianchi, polo bianca, t-shirt bianca, crewneck nera. tutti pezzi piccoli.
2 clienti diversi hanno chiesto il Peyre nero in 4 (giacca da sci), finito. e Maire nera in 3, finita anche quella ormai.

DOM 20: 5,6k, 42 ingressi, 5 scontrini. beanie navy, cable knit bianco, un Tib bianco e un Arneb nero (anche qui una taglia sotto). chiesto cable knit bianco XL e Trailgrip nera 44, no.

cielo limpido, gente su alle Tofane e al Lagazuoi, ma poi in negozio pochi.
dav"""),

    dict(id="c0921", sent="2026-09-21 19:55", frm="martina", subject="CRT01 chiusura 21/09",
         business_date="2026-09-21", body="""Giornata morta.
2.180 euro, 2 scontrini (beanie navy e un Flammette nero a una signora inglese), 28 ingressi in tutto il giorno.
Hanno chiuso un paio di hotel grossi da ieri, sul Corso le serrande cominciano ad abbassarsi.
M."""),

    dict(id="c0922", sent="2026-09-22 20:30", frm="davide", subject="chiusura crt 22/9",
         business_date="2026-09-22", body="""6,7k, 8 scontrini su 35 ingressi, meglio del bdg.
una famiglia turca (4 persone) che si e' fatta un giro completo: beanie, polo navy, polo nera, crewneck nera ecc.
chiesto: Flammette navy tg 3, Chambre nero tg 1, hoodie nero L. tutte e tre nn ci sono, la signora turca al Flammette ci teneva.
dav"""),

    dict(id="c0923", sent="2026-09-23 20:40", frm="martina", subject="CRT01 chiusura 23/09",
         business_date="2026-09-23", body="""CRT01 - 23/09
Fatt: 3.290 (bdg 6.640)
Ingressi: 37 / Scontr: 3
Arrivati 25 pz (consegna piu piccola delle altre, ok).
Una coppia di francesi, una di americani e due ragazzi tedeschi, ognuno un pezzo: polo nera, tricot cardigan nero, Rosiere nero.
Mancati: Hermine nera 4 (signora tedesca, la voleva davvero), Bady nero 1, Montcla navy 6.
Mi sembra che a Cortina le taglie "estreme" arrivino sempre per ultime. Si puo' rivedere il size split x l'inverno?
Martina"""),

    dict(id="c0925", sent="2026-09-25 20:15", frm="martina", subject="CRT01 chiusura 25/09",
         business_date="2026-09-25", body="""Fatt 5.483 / bdg 8.810
53 ingressi, 7 scontrini
Gli Ilvaro neri finiti (ieri 2 venduti, erano gli ultimi in 0 e 1). Oggi Trailgrip nera, t-shirt navy, cardigan logo nero e cable knit bianco.
Reso cardigan logo S per taglia, ha preso la M.
Il venerdi sera ora e' il momento migliore, arrivano i milanesi dopo le 5.
M."""),

    dict(id="c0926", sent="2026-09-26 21:05", frm="martina", subject="CRT01 chiusura 25/09",
         business_date="2026-09-26", body="""Sabato discreto ma niente di che: 11.670 (bdg 12.600), 79 ingressi, 8 scontrini.
Tanti italiani (milanesi del weekend, come sempre), un paio di arabi e americani.
Pantalone Chamonix, cappellino navy, guanti, zaino Makaio navy...
Persi: felpa crewneck nera S, polo navy L.
Domani chiude Davide, io lunedi.
Martina"""),

    dict(id="c0927", sent="2026-09-27 20:25", frm="davide", subject="chiusura dom 27/9",
         business_date="2026-09-27", body="""4,9k su 8,9 bdg. 44 ingressi 4 scontrini.
coppia di tedeschi (Monaco) + italiani. beanie navy, cardigan logo, tricot cardigan nero e un Montgenevre navy.
un ragazzo cercava la Maya nera in 2, finita.
i larici stanno girando, la gente va a camminare verso Tre Croci e non entra in negozio
dav"""),

    dict(id="c0928_orari", sent="2026-09-28 15:20", frm="martina",
         cc=["roberto", "dc-replenishment@moncler-retail.example", "facility-italy@moncler-retail.example"],
         subject="CRT01 - orari ottobre (solo ven/sab/dom)", kind="misc", body="""Ciao a tutti,
come da accordi con Roberto vi confermo che da giovedì 1 ottobre il negozio di Cortina sarà aperto solo venerdì, sabato e domenica (10-12.30 / 15.30-19.30) fino alla riapertura invernale. Da lunedì a giovedì chiuso.
Quindi:
- giovedì 1/10 chiuso, primo weekend ven 2 / sab 3 / dom 4
- le consegne del mercoledì da CSG da ottobre vanno sospese oppure spostate al venerdì mattina, altrimenti il corriere trova chiuso. Mercoledì 30 l'ultima consegna normale va bene.
- le mail di chiusura arriveranno solo per i giorni aperti (a volte una sola per sab+dom)
- telefono del negozio deviato sul cellulare aziendale, per clienti e VIC rispondiamo io o Davide
- Alessio finisce il contratto stagionale il 30/9, nei weekend siamo io, Davide e Silvia a rotazione
Per facility: l'allarme va inserito anche nei giorni di chiusura, se serve riprogrammarlo ditemi.
Grazie
Martina Menardi
Store Manager | Moncler Cortina d'Ampezzo"""),

    dict(id="c0928", sent="2026-09-28 20:10", frm="martina", subject="CRT01 chiusura 28/09",
         business_date="2026-09-28", body="""Fatt 6.330 vs 6.960
35 ingressi, 4 scontrini
Gente da Dubai, giapponesi e un paio di italiani. Ecrins nero, Montcla navy, tricot cardigan, beanie.
Una ragazza giapponese voleva l'Ilvaro nero in 0, finito da giovedi, le ho fatto vedere il bianco ma niente.
Per gli orari di ottobre vedi mia mail di oggi pomeriggio.
M."""),

    dict(id="c0929_re", sent="2026-09-29 07:52", frm="roberto", to=["martina"],
         cc=["retail-ops-italy@moncler-retail.example"], reply_to_id="c0928_orari", kind="reply", suffix="_re1",
         subject="Re: CRT01 - orari ottobre (solo ven/sab/dom)", body="""Ok Martina grazie. Per le consegne chiedo io a CSG di spostarle al venerdi.
Nei giorni di chiusura se un VIC chiede un appuntamento apri pure, basta che mi avvisi.
R.

Inviato da iPhone"""),

    dict(id="c0929", sent="2026-09-29 20:00", frm="davide", subject="chiusura 29/9 crt",
         business_date="2026-09-29", body="""1,7k. 33 ingressi, 3 scontrini (zaino Makaio, felpa grigia, un Bady nero).
reso un Chambre, cambiato idea.
chiesto Hermine nera 4 (di nuovo, e' la seconda volta in una settimana) e polo nera M.
fuori i larici sono gialli, Cortina vuota, solo pensionati e qlc cinese / giapponese di passaggio.
ultimo martedi aperto, da giovedi si va col nuovo orario.
dav"""),

    dict(id="c0930", sent="2026-09-30 20:45", frm="martina", subject="CRT01 chiusura 30/09 (ultimo giorno orario pieno)",
         business_date="2026-09-30", body="""CRT01 - 30/09
Fatt: 4.680 (bdg 7.070)
Ingressi: 33 / Scontr.: 3
Ultima consegna da CSG arrivata, 34 pz, controllati e sistemati. Ultimo giorno di Alessio, gli abbiamo fatto la torta :)
Venduto polo nera, felpa navy, cardigan logo e una Maya oliva.
Da segnalare: un signore di Treviso ha riportato un Tib navy (tg 4) comprato a fine agosto, il cursore della zip si e' rotto, non chiude piu. Fatto il reso come difettoso. Non so se e' un caso o se e' capitato anche ad altri negozi.
Domani chiuso, ci sentiamo venerdi.
Martina"""),

    dict(id="c1002", sent="2026-10-02 21:15", frm="martina", subject="CRT01 chiusura 02/10",
         business_date="2026-10-02", body="""Primo venerdi con l'orario nuovo e... bomba!
Fatt 15.8k (bdg 10.070), 61 ingressi, 12 scontrini.
Una famiglia saudita in giro x le Dolomiti: papa' e figlio 2 Arneb neri (presa a tutti e due una taglia sotto, l'Arneb veste grande), pantaloni Chamonix x la figlia. Poi americani, una coppia cinese in viaggio di nozze x la Golden Week e i soliti milanesi.
cappellino nero, felpa crewneck bianca.
L'Arneb nero adesso e' corto in 3.
Martina"""),

    dict(id="c1002_corr", sent="2026-10-03 09:05", frm="martina", subject="Re: CRT01 chiusura 02/10 - correzione",
         reply_to_id="c1002", kind="correction", suffix="_corr", business_date="2026-10-02",
         body="""Scusate, ieri sera ho invertito le cifre: il fatturato di venerdì è 18.470 non 15,8k. +83% sul budget.
M.

Inviato da iPhone"""),

    dict(id="c1005_wk", sent="2026-10-05 10:20", frm="martina", subject="CRT01 chiusura weekend 3-4/10",
         business_date="2026-10-03,2026-10-04", body="""Buongiorno, mail del weekend in ritardo, ieri sera ero distrutta.

Sabato 3/10: 6.390 euro (bdg 13.890), 74 ingressi ma solo 4 scontrini. Tanto giro e poca vendita, molti italiani che guardano e basta. 2 Tib navy, Chamonix, Trailgrip nera, felpa navy.
Richieste perse: Maire nera 2 (sempre lei), Ambrine nera 1 e 4.

Domenica 4/10: 4.730, 56 ingressi, 7 scontrini. 2 Trailgrip donna nere, 2 cardigan logo, guanti, cappellino navy. Un gruppo di coreani, francesi.
Chiesto Montgenevre navy in 1.
Secondo Tib navy riportato con la zip rotta (tg 4 anche questo, comprato a settembre). Inizio a pensare che sia un problema di lotto. Li tengo da parte tutti e due in back-office, ditemi se vanno a CSG o al fornitore.

Martina"""),

    dict(id="c1005_re", sent="2026-10-05 12:48", frm="roberto", to=["martina"],
         cc=["retail-ops-italy@moncler-retail.example"], reply_to_id="c1005_wk", kind="reply", suffix="_re1",
         subject="Re: CRT01 chiusura weekend 3-4/10", body="""Martina non sei l'unica, i Tib con la zip rotta li stanno segnalando anche altri negozi. Tienili da parte con scontrino e foto della zip, ti dico io dove mandarli.
Intanto quando un cliente lo prova fagli controllare il cursore.
Roberto"""),

    dict(id="c1009", sent="2026-10-09 20:35", frm="davide", subject="chiusura venerdi 9/10",
         business_date="2026-10-09", body="""6,2k, 52 ingressi, 5 scontrini.
2 felpe navy, beanie, una Maya navy e una Maya nera. italiani quasi tutti, qlc cinese.
chiesto il Bady rosa in 00, una ragazzina con la mamma, noi il rosa nn l'abbiamo proprio.
reso Arneb nero tg 3, il cliente ha detto che ci ha ripensato ma secondo me gli stava largo, l'aveva preso nella sua taglia ad agosto (prima che dicessimo a tutti di prendere una in meno).
dav"""),

    dict(id="c1010", sent="2026-10-10 21:00", frm="martina", subject="chiusura cortina 10/10",
         business_date="2026-10-10", body="""Fatt 11.010 / bdg 14.940
79 ingressi, 7 scontrini
Gruppo di tedeschi e austriaci (un club di auto d'epoca, giro dei passi) + cinesi + italiani. 2 Maire navy, Trailgrip nera, crewneck grigia, tricot cardigan nero.
Persi: Maire beige 4, Rosiere oliva 5.
Reso dolcevita L x taglia.
Davide domani apre, io chiudo.
M."""),

    dict(id="c1011", sent="2026-10-11 20:40", frm="martina", subject="chiusura cortina 11/10",
         business_date="2026-10-11", body="""Domenica 7.250 euro, 44 ingressi, 4 scontrini.
Tanti cinesi oggi (pullman), emiratini. 2 Trailgrip nere + una grigia + una Trailgrip donna e una Maire beige.
Peyre nero 6 e Trailgrip nera 43 richieste ma niente.
Temperature scese parecchio, stamattina -1 a Pocol, dicono neve in quota a meta settimana.
M."""),

    dict(id="c1014", sent="2026-10-14 17:40", frm="davide",
         cc=["roberto", "vm-team@moncler-retail.example", "dc-replenishment@moncler-retail.example"],
         subject="CRT01 - negozio chiuso, giro stock + vetrine inverno", kind="misc", body="""ciao,
oggi negozio chiuso al pubblico ma sono passato con Silvia x:
1) conta stock a campione (piumini + accessori): torna tutto tranne 1 beanie navy in meno, probabile errore di scarico, controllo con il report vendite di domenica.
2) arrivato il kit vetrina inverno da vm-team (3 colli), montiamo giovedi sera cosi venerdi siamo pronti. manca il fondale grande, nel collo 2 c'erano solo i supporti. vm-team me lo mandate?
3) da CSG nessuna consegna da fine settembre. va bene x ora ma x l'inverno ci servono: Maire nera (0 e 2 a zero da inizio settembre), Peyre nero in tutte le taglie, Hermine nera 1 e 4, Ilvaro nero. se arrivano a dicembre perdiamo le vendite vere.
4) stanotte prima neve sulle Tofane, finalmente.
dav"""),

    dict(id="c1016", sent="2026-10-16 21:00", frm="martina", subject="chiusura cortina 16/10",
         business_date="2026-10-16", body="""Fatt: 10.030 (bdg 11.900)
Ingressi 55 / scontrini 10
Neve sulle cime e subito si vede: gente che sale a vedere la prima neve, cinesi (2 gruppi), tedeschi, americani. 2 Maya nere, beanie in tutti i colori (bianco, nero, navy), guanti.
Un signore cercava il dolcevita marrone in XL, il marrone in maglieria qui non l'abbiamo mai avuto.
2 resi: Ilvaro (la cliente voleva il bianco invece del nero, ma il bianco nella sua taglia nn c'era -> rimborso) e una Trailgrip donna 37, la suola si sta staccando in punta dopo un mese, come quella da uomo di fine agosto.
Martina"""),

    dict(id="c1018_wk", sent="2026-10-18 20:30", frm="davide", subject="crt weekend 17+18",
         business_date="2026-10-17,2026-10-18", body="""sabato 17: 12,5k (bdg 16,8) 71 ingressi 10 scontrini
domenica 18: 8k, 64 ingressi, 5 scontrini
sabato bella giornata, italiani + cinesi + qlc giapponese. 2 Maya nere ancora (col freddo vanno), 2 Trailgrip nere, beanie, crewneck bianca. polo navy L chiesta, finita.
domenica svizzeri (gruppo da Zurigo venuto a vedere lo sliding centre olimpico) e italiani. zaino Makaio, 2 felpe. un signore voleva il Peyre in 1 (!?) nn c'era.
i milanesi del weekend sono tornati con la neve, il prossimo weekend dovrebbe andare meglio.
dav"""),
]
