# Proposta rivista: rendere utilizzabile ciò che osservano i negozi

_22 ottobre 2026. Revisione della proposta del team; perimetro consigliato, da validare. Le trascrizioni sono evidenze qualitative, non una validazione di mercato._

**Proposta:** affiancare alla reportistica esistente una raccolta guidata di osservazioni dal negozio, anche vocali. Collegare queste osservazioni a prodotti, vendite, disponibilità e report, conservandone le prove. Produrre schede leggibili che mostrino cosa sta succedendo, quali spiegazioni sono supportate e quale decisione o verifica richiede attenzione. La scelta resta al manager.

**Sell-point:** «A parità di vendite, problemi diversi richiedono decisioni diverse. Rendiamo visibili le ragioni riportate dai negozi e le colleghiamo ai numeri».

## Cosa emerge dalle interviste

In [needfinding.md](sources/transcripts/needfinding.md), l'intervistato individua un bisogno preciso: interesse per il capo, prova, problemi di vestibilità o tessuto e motivi del mancato acquisto sfuggono ai sistemi transazionali. Racconta anche piloti con vocali WhatsApp e 3–4 domande guida: il bisogno è credibile, ma la raccolta audio ha già precedenti. Il differenziale da dimostrare è la qualità con cui colleghiamo feedback, fonti e decisioni.

La stessa intervista mette in discussione due assunti dei docs: nei negozi diretti descritti i dati quantitativi sono già centralizzati; le operazioni logistiche restano lente anche con informazioni immediate. Distingue inoltre diretti, franchising e multimarca. Non possiamo generalizzare una sola situazione a tutte le reti: il primo contesto proposto è una rete di boutique dirette, con catalogo e dati quantitativi disponibili.

Nel [Q&A con il referente](sources/transcripts/Poke%20House%202.md), la challenge resta aperta: è ammesso concentrarsi su un blocco e supportare le decisioni spiegando ciò che accade, preservando sistemi e consuntivi. Il [brief](sources/track/track.html) richiede comunque un'indicazione concreta ottenuta unendo più fonti. Quindi la demo deve arrivare oltre la trascrizione e la classificazione.

## La raccolta: poco attrito e fatti distinguibili

Terrei la possibilità di contribuire per ogni dipendente, ma renderei **facoltativo il contributo individuale**. Cinque minuti obbligatori per cinque persone significano 25 minuti-persona al giorno per negozio, oltre al lavoro esistente. Come ipotesi iniziale: un riepilogo guidato per negozio o turno, arricchito da brevi contributi individuali quando c'è qualcosa da segnalare. Durata e partecipazione vanno validate sul campo.

Le domande guida possono essere:

1. Quali prodotti hanno suscitato interesse o sono stati provati senza acquisto?
2. Quale motivo ha espresso il cliente? Quale invece è una tua interpretazione?
3. Quali taglie, colori o prodotti sono stati richiesti ma non erano disponibili?
4. C'è un episodio nuovo, una correzione o un problema operativo da segnalare?

Chiedere prodotto, periodo e quantità solo se noti. «Tanti» resta una quantità sconosciuta. L'AI struttura ciò che viene raccontato; i fatti mai comunicati restano sconosciuti.

L'incrocio iniziale per negozio e giornata è corretto, ma cinque dipendenti possono riferire lo stesso cliente. Conservare contributi separati e possibili sovrapposizioni: tre segnalazioni non equivalgono a tre clienti. Se l'identità dell'episodio è incerta, mostrare il numero di segnalazioni senza sommarne automaticamente i conteggi. Non servono nomi dei clienti per raccogliere il feedback. Il riepilogo del manager e la mail che lo ripete possono avere un'unica origine. Accordo fra colleghi non certifica il fatto; eventuali disaccordi restano visibili.

## Ingestion comune, significato configurabile

Confermo il layer intermedio: **documenti originali → affermazioni strutturate → casi aggregati → viste personalizzate**. Non condensare tutto in un unico riassunto prima di salvare le prove.

Per ogni affermazione conservare almeno: fonte e riferimento al passaggio originale, negozio, data del fatto e della ricezione, prodotto o candidati, tipo di osservazione, quantità esplicita oppure ignota, stato e relazioni con ripetizioni, rettifiche o contraddizioni. Nell'audio il riferimento include il segmento temporale; un nome prodotto trascritto in modo dubbio può richiedere conferma. Distinguere sempre dato di sistema, dichiarazione del cliente riportata dal dipendente, osservazione del dipendente e ipotesi del sistema.

Parser per formato e trascrizione audio alimentano questo contratto comune; un LLM estrae i fatti e aiuta a collegarli al catalogo. Per il prototipo bastano parser, un modello di trascrizione disponibile e un modello linguistico con validazione: non serve un modello diverso per ogni formato. SQLite e riferimenti alle fonti bastano per la knowledge base; nuovi documenti vengono elaborati una volta e aggiornano i casi interessati.

**La personalizzazione riguarda anche l'ingresso:** catalogo, alias, definizioni delle metriche, categorie e destinatari cambiano fra aziende. Possiamo riusare pipeline e struttura delle evidenze, con una configurazione di dominio. «Tutti i business, automaticamente» è una promessa prematura. Il primo dominio resta il retail moda.

Le viste per ufficio, priorità, prodotto e stagionalità sono filtri e aggregazioni della stessa base. Mantengono gli stessi fatti e citazioni, senza richiedere motori indipendenti.

## Output: spiegazioni supportate e una decisione aperta

Ogni scheda mostra cosa emerge, rispetto a quale periodo e prodotto, le prove a favore e contro, ciò che manca, il destinatario e il motivo della priorità. Urgenza e solidità dell'evidenza restano distinte. «Tre clienti hanno dichiarato che il tessuto pizzica» è un motivo riportato; «la qualità causa il calo delle vendite» richiede altre prove. Non dedurre tassi di conversione senza conteggi confrontabili di interesse, prove e acquisti.

Esempio sintetico: due prodotti vendono cinque pezzi ciascuno. Per A emergono rinunce dopo la prova per vestibilità; per B richieste non soddisfatte della taglia M, da confrontare con lo stock. La scheda distingue i due casi e pone domande concrete: per A, quali taglie o negozi riportano il problema? Per B, c'è disponibilità vendibile per riassortire? Una verifica motivata è già un output utile; non occorre prescrivere modifiche al prodotto.

## La porzione da costruire nelle 24 ore

Primo lettore: responsabile merchandising HQ. Costruire un percorso funzionante con contributi vocali di esempio, una mail esistente e un file CSV/XLSX di catalogo, vendite, stock e forecast. Aggiungere un breve report testuale e una fonte esterna già acquisita per mostrare l'incrocio richiesto dal brief. L'upload nella UI è sufficiente: distinguere lettura del formato da integrazione con Drive, email o WhatsApp.

Il cuore tecnico è estrazione con prove, collegamento prodotto, gestione di duplicati/conflitti e una scheda consultabile per prodotto e ufficio. Un agente può scegliere di consultare il catalogo o lo stock, oppure formulare una domanda di chiarimento simulata nella UI. L'audio rende centrale la trascrizione: verificare subito l'accesso all'endpoint citato negli [asset Fastweb](research-fastweb-assets.md), tuttora non confermato nei documenti. Se manca, usare una trascrizione preparata dichiarando il passaggio simulato.

Rinviare telefonate automatiche, connettori reali, parsing universale PDF/slides, scraping continuo, analisi settoriali multiple e nuovo forecasting. Il forecast esistente resta un confronto; i segnali possono evidenziarne limiti o scostamenti senza modificarlo numericamente.

La demo deve mostrare: stesso venduto con motivi riportati diversi; una ripetizione che non moltiplica i clienti; un prodotto ambiguo che richiede chiarimento; una contraddizione conservata nella scheda. Su pochi casi sintetici separati dagli esempi di sviluppo, confrontare report esistenti, report più vocali, e risultato integrato: quali informazioni erano già presenti, quali aggiunge la raccolta, e quanto correttamente il sistema le rende utilizzabili. Misurare errori di estrazione e collegamento, doppioni, tracciabilità e tempo necessario per capire il caso.

Questa revisione sposta il focus di [project-design.md](project-design.md) dalla correzione numerica obbligatoria del forecast alla raccolta e integrazione delle evidenze qualitative. Aggiorna anche l'assunto «stores change nothing»: introduciamo un nuovo gesto, quindi l'adozione è un'ipotesi da verificare. Mantiene dalla [ricerca precedente](research-recommendation.md) provenienza, astensione, gestione del rumore e responsabilità umana.
