# Dal rumore alla prossima decisione: raccomandazione per le 24 ore

_22 ottobre 2026. Proposta da discutere; non sostituisce automaticamente il design. Analisi di docs, dataset sintetico, allegati Fastweb e ricerca su fonti primarie. Non sono stati eseguiti benchmark né misurati miglioramenti del prodotto._

## La scelta in due minuti

**Costruire un agente che individua le poche decisioni operative da prendere ora, raccoglie le prove necessarie e propone opzioni fattibili con limiti espliciti.** Primo utente: responsabile allocation/merchandising HQ. Orizzonte: prossime 24–72 ore per agire, 7 giorni per confrontare gli effetti; eventuale estensione a 14 giorni. Questi orizzonti sono una scelta di prototipo, da allineare ai lead time.

**Sell-point:** «Trasformiamo ciò che i negozi vedono oggi nelle decisioni verificabili che la sede deve prendere domani, compresa la domanda che non arriva mai agli scontrini».

Il tratto su cui andare in profondità è **affermazione → prodotto/tempo corretti → prove indipendenti e conflitti → verifica mirata → opzioni operative**. Il forecast esistente è un input e un termine di confronto. Il successo è anticipare o migliorare una decisione, compresa la scelta di verificare lo stock prima di trasferirlo.

Tre elementi da mostrare:

1. **Una domanda invisibile alle vendite.** L'articolo richiesto è finito o non è in assortimento; il sistema collega note, catalogo e disponibilità.
2. **Un'indagine che cambia percorso.** Scoperto un conflitto sullo stock, l'agente interroga la disponibilità vendibile o chiede chiarimento; decide poi se trasferire, monitorare o fermarsi.
3. **Una decisione che resiste al rumore.** Aggiungere forward o notizie irrilevanti non deve moltiplicare domanda e priorità. Togliere una prova decisiva deve cambiare lo stato in «da verificare».

Leggere [asset Fastweb](research-fastweb-assets.md) per scegliere i servizi, [data fusion](research-data-fusion.md) per la letteratura su fonti e matching, [metodi quantitativi](research-methods.md) per forecasting breve, incertezza e valutazione.

## 1. Cosa è già forte e cosa cambierei nei docs

Il [brief ricostruito](findings.md) e il [design](project-design.md) hanno già buone fondamenta: fonti originali, lingue, product linking, domanda censurata, opzioni vincolate, responsabilità umana e un dataset con replay temporale. La proposta C è sensata; restringerei però il cuore tecnico di C ad A più un decisore semplice.

| Punto attuale | Valutazione e modifica proposta |
|---|---|
| «AI reads, code counts, humans decide» | Da mantenere. Rendere visibile cosa è osservato, inferito, ipotizzato e approvato. |
| M9 correzione forecast come passaggio obbligato | Renderlo uno **scenario quantitativo opzionale**. Uno stock contraddittorio può richiedere un controllo senza inventare un uplift. |
| 15+ moduli, 4 schermate, 3 ruoli agentici | Troppo ampio per il nucleo di 24h. Un investigatore, una coda di casi e una scheda dettaglio. |
| Candidati limitati all'assortimento | Usare l'assortimento come priorità, con recupero dal catalogo globale. Le richieste fuori assortimento sono parte del valore. |
| «tanti» → [4,8], strength → +50% | Assunzioni non apprese. Preferire quantità sconosciuta e verifica; eventuali range sono scenari dichiarati, non stime calibrate. |
| Forecast × somma uplift | Sovrapposizioni, duplicati e cause comuni possono sommare più volte lo stesso fenomeno. Un caso aggregato per prodotto/periodo, con contributi verificabili. |
| Meteo concorde aumenta automaticamente strength | Affinità narrativa non basta. Separare contesto da conferma osservazionale; nessun boost numerico automatico senza validazione. |
| Note che «vedono tutto» e unmet demand come «unica fonte» | Ridimensionare: le note sono selettive e possono omettere fenomeni; waitlist, ricerche ecommerce e customer care possono confermare domanda non soddisfatta. |
| Zero menzioni per alcuni giorni → decadimento | Distinguere assenza di segnalazioni da assenza di report. Un negozio che non invia mail non è un segnale di risoluzione. |
| Stock ERP positivo → chiusura stockout | Confrontare disponibilità vendibile, timestamp, prenotazioni e taglia. Uno snapshot vecchio non risolve una nota nuova. |
| Q da interpolazione low/high chiamato service quantile | È una politica sotto ipotesi uniforme, non un quantile empiricamente calibrato. Mostrare sensibilità a scenari/costi. |
| Scoring «allineamento tecnologico» = bisogno di mercato | Il kickoff allegato specifica infrastruttura Fastweb. Conservare l'interpretazione orale come evidenza separata e dimostrare entrambi. |

Anche il framing sul forecast va circoscritto: «il loro sistema attuale usa soprattutto lo storico» è coerente con il Q&A; «i forecast non possono usare informazioni recenti» sarebbe una generalizzazione scorretta. La letteratura sul nowcasting e sui modelli dinamici esiste già; la differenza progettuale è collegare nuove evidenze a decisioni verificabili.

## 2. Quale novità vale davvero la pena costruire

**Informazioni utili in funzione dell'azione.** Un picco social può essere interessante ma non cambiare alcuna scelta. Una sola rettifica sull'ETA può rendere inutile un trasferimento. Il ranking dovrebbe privilegiare la possibilità di intervenire, la scadenza e la solidità della prova, non il volume dei documenti.

**Verifiche scelte per il loro valore.** Se l'azione cambia a seconda che lo stock reale sia 0 oppure 3, verificare lo stock ha valore. Se due interpretazioni del colore producono comunque «nessuna disponibilità prima dell'evento», chiedere il colore non è necessariamente la prossima verifica migliore. In 24h bastano scenari discreti e regole; il value of information probabilistico è un'evoluzione. Il fondamento e i limiti sono nei [metodi quantitativi](research-methods.md).

**Una memoria delle prove, non dei riassunti soltanto.** Conservare affermazioni, citazioni, origine, rettifiche e stato. Dal lavoro di [Dong et al. sulla dipendenza delle fonti](https://www.vldb.org/pvldb/vol2/vldb09-pvldb47.pdf) prendiamo il principio che dieci copie non sono dieci conferme; non pretendiamo di implementarne l'intero modello probabilistico.

**Robustezza dell'azione prima della precisione apparente.** Mostrare se la stessa opzione è ragionevole con domanda bassa/centrale/alta e con tempi di consegna diversi. Se l'esito cambia, il manager vede quale ipotesi deve verificare. Questo è più credibile che mostrare un +37% senza una base empirica. La letteratura [Smart Predict, then Optimize](https://arxiv.org/abs/1710.08005) motiva la centralità dell'errore decisionale; qui ne adottiamo il criterio di valutazione, senza addestrare un modello SPO.

## 3. Mappa delle tecniche: scegliere senza inseguire la complessità

| Problema | Metodo classico | Variante recente | Scelta per questo hackathon |
|---|---|---|---|
| Schemi e metriche diversi | Mapping, unità canoniche, record linkage, provenienza | LLM propone mapping e interpreta testo | Parser deterministici + un contratto di evidenza; una sola coppia di metriche in conflitto se c'è tempo. |
| Nomi prodotto multilingua | Alias/fuzzy matching e attributi | LLM matching; embedding multimodali Qwen 2026 | Retrieval di candidati + reranking vincolato + astensione. [Fonti](research-data-fusion.md). |
| Rumore e fonti dipendenti | Dedup, regole, data fusion | Weak supervision / teacher-student | Dedup di origine e regole trasparenti; Snorkel e distillazione come roadmap. |
| Cambio recente rispetto al piano | Residui, EWMA/CUSUM, modello di stato | Change-point bayesiano, nowcasting aggiornabile | Baseline immutata; piccolo rilevatore sui dati osservabili e scenari di correzione solo con evidenze sufficienti. [Fonti](research-methods.md). |
| Incertezza | Scenari e analisi di sensibilità | Conformal adattivo, selective prediction | Astensione e scenari espliciti ora; intervalli calibrati dopo disponibilità di feedback adeguato. |
| Prossima indagine | Regole di costo/beneficio | Agente con tools e value of information | Un ciclo limitato, che sceglie fra 3–4 verifiche e sa fermarsi. [ReAct](https://arxiv.org/abs/2210.03629). |
| Riassunto cross-fonte | Join/aggregazioni per prodotto, negozio, periodo | GraphRAG | Relazioni in SQLite e schede con citazioni; GraphRAG completo aggiunge poco al primo caso operativo. |

Non addestrare un foundation model di serie temporali né un modello causale generale. [Chronos](https://arxiv.org/abs/2403.07815) è un riferimento rilevante per forecasting preaddestrato anche a breve, ma confrontarlo qui sottrarrebbe tempo al problema distintivo: rendere osservabile e utilizzabile l'evidenza non tabellare.

## 4. Pipeline minima, concreta e scalabile

```text
EML/testo + CSV stock/forecast/catalogo + 1 fonte esterna contestuale
  → parser e normalizzazione temporale
  → LLM: affermazioni atomiche con citazioni
  → alias + embedding: candidati prodotto; link o astensione
  → registro: dedup, correzioni, conflitti, stato e scadenza
  → selezione casi: impatto potenziale, urgenza, evidenza
  → investigatore: verifica disponibilità/ETA o chiede chiarimento
  → codice: opzioni + simulazione giornaliera + controlli
  → scheda manager: agisci / verifica / monitora / archivia
```

**Campi da aggiungere ai contratti attuali:** `event_time`, `available_at`, `valid_until`, `origin_group_id`, `supersedes`, `metric_definition`, `unit`, `observation_status`, `decision_deadline`, `blocking_uncertainties`. `available_at` governa ciò che l'agente può sapere durante il replay; un documento datato ieri può essere disponibile soltanto oggi.

**Tool minimi:** `get_available_stock`, `get_lane_and_eta`, `evaluate_options`, `request_clarification`. L'agente accede alle prove del caso già selezionate; budget iniziale di 4 chiamate, con soglia configurabile. Mostrare chiamate, esiti e motivazione breve. La richiesta al negozio è simulata nell'interfaccia, non inviata a persone reali.

**Asset consigliati:** Gemma come primo candidato chat da misurare; Qwen3-VL-Embedding-2B per matching; Qwen 3.6 come alternativa sui dati sintetici. La guida indica Gemma/embedding EU e Qwen 3.6 extra-EU. Il 397B è opzionale. Dettagli e discrepanze in [asset Fastweb](research-fastweb-assets.md).

**Persistenza:** SQLite con tabelle `documents`, `claims`, `entities`, `evidence_links`, `cases`, `options`, `decisions`. Embedding del catalogo precalcolati. Cache per documento nuovo e versione di estrazione. LLM solo su nuovi input e casi selezionati: il costo cresce con il lavoro incrementale, senza rileggere tutto l'archivio a ogni domanda.

I mock esistenti hanno contratti REST/OpenAPI e agent cards: riutilizzarli senza promettere un'integrazione reale A2A/MCP. Il POST logistico documenta validazione/prenotazione: per la demo creare una **bozza locale** o un wrapper esplicitamente simulato, senza chiamarlo «draft» se l'endpoint sottostante prenota davvero.

## 5. Come selezionare le informazioni utili

Separare **rilevanza**, **solidità dell'evidenza** e **priorità operativa**. Non comprimerle in una percentuale di confidenza inventata dall'LLM.

1. **Gate di ammissibilità:** fonte disponibile al tempo di replay; citazione valida; entità e periodo sufficientemente risolti; niente duplicate contribution. Un caso ambiguo resta lavorabile come «verifica», non come trasferimento.
2. **Gate di fattibilità:** esiste un'azione che arriva in tempo e rispetta i vincoli? Altrimenti routing a monitoraggio, customer care o marketing senza promettere stock impossibile.
3. **Ordinamento:** prima scadenza decisionale, poi livello di impatto, poi solidità delle prove. Mostrare le tre dimensioni e un motivo leggibile. Nessun punteggio economico se mancano costi e margini.
4. **Budget di attenzione:** top 3 casi per la demo, coda separata di richieste di verifica, un caso unico condiviso fra funzioni. Un'anomalia bassa probabilità/alto impatto può meritare verifica urgente, non un'azione automatica.
5. **Stop:** fermare l'indagine quando ulteriori informazioni non cambiano le opzioni nel set di scenari considerato, o il budget è esaurito; nel secondo caso dichiarare cosa resta ignoto.

Per una valutazione economica futura: `beneficio(a) = margine salvato(a) − costo trasferimento(a) − perdita al donatore(a) − altri costi(a)`. Il confronto va fatto rispetto a `hold`. Margine unitario non è prezzo retail; il danno reputazionale non va monetizzato arbitrariamente. In assenza di dati, usare unità potenzialmente non servite e costi documentati, con sensibilità.

## 6. Forecast breve senza falsa precisione

**Tre prodotti distinti:** nowcast dello stato presente (stock vendibile/domanda non soddisfatta), scenario sui prossimi 7 giorni, scelta dell'azione. Non tutti i casi richiedono tutti e tre.

- Se la nota contiene un conteggio esplicito di richieste uniche perse e la finestra è coerente, può integrare l'evidenza. Vendite + richieste non equivale sempre a domanda: clienti ripetuti, sostituzioni, prenotazioni e acquisti successivi richiedono dedup.
- Se c'è solo «tanti», estrarre direzione e motivazione; niente conteggio ricavato automaticamente da una tabella universale.
- Se la nota segnala solo stockout, le vendite sono un dato censurato. Non inventare la domanda latente e non aggiornare al ribasso sulla base di zero vendite.
- Se ci sono domanda sufficiente e osservazioni confrontabili, provare aggiornamento dei residui o shrinkage conservativo verso la baseline; descrivere assunzioni e confrontarlo con baseline immutata.
- Per la demo usare tre scenari espliciti. Chiamarli «scenari», non «intervallo all'80%», salvo calibrazione reale documentata.

Nel decisore simulare **giorno per giorno**, perché un arrivo al giorno 7 non evita vendite perse al giorno 2. Un'unità del donatore non può essere promessa a due destinazioni: anche con poche schede serve una disponibilità condivisa e una prenotazione simulata dopo approvazione.

La domanda sottostante e la domanda servibile dal negozio sono diverse: un cantiere può ridurre passaggio e vendite senza dimostrare perdita di interesse nel prodotto. Produrre un caso retail ops e una stima condizionata della domanda servibile, non una conclusione causale generale sul brand.

## 7. La porzione da sviluppare davvero

**Allocazione dello sforzo proposta:** circa 50% evidenze/linking/stato, 25% verifica agentica e opzioni, 25% valutazione e presentazione. Il sistema deve comunque arrivare fino a una decisione concreta.

| Costruire bene | Tenere semplice | Rinviare |
|---|---|---|
| Claim con citazioni; entità; dedup/correzioni; conflitti | Parser EML + CSV; una fonte esterna | Parsing universale PDF/PPTX/immagini |
| Un investigatore con scelta reale del prossimo tool | Un caso di stock, 2–3 opzioni e hold | Coordinamento autonomo di molti agenti |
| Controlli stock, donatore, ETA e prenotazioni | Scenari quantitativi dichiarati | Nuovo forecast, conformal senza dati, training SPO |
| Scheda con prova, scadenza, owner e incertezza | Una coda casi e dettaglio | Mappa mondiale, 4 viste, GraphRAG completo |
| Eval con rumore e hold-out | Replay locale e mock dei sistemi aziendali | Integrazioni enterprise reali |

**Estensione ad alto appeal, solo dopo:** una foto allegata alla nota viene usata per restringere i candidati prodotto con embedding/vision Fastweb; la taglia resta da testo o chiarimento. Ha una ragione operativa quando il cliente mostra una foto, ma non giustifica costruire tutta l'ingestion multimodale.

## 8. Piano 24h con punti di arresto

Ipotesi: quattro persone, attività in parallelo. I numeri sono ore trascorse dall'avvio; se parte della finestra è già passata, comprimere lo scope, non la verifica finale.

| Finestra | Risultato verificabile |
|---|---|
| 0–2h | Un caso, contratti minimi, set dev, chiamata Fastweb e tool round-trip. Se accesso instabile, attivare cache/replay e segnalarlo. |
| 2–6h | Parser + estrazione + candidati prodotto; scheda end-to-end già attraversabile. |
| 6–11h | Dedup, correzioni e conflitti; investigatore sceglie una verifica; decisore valuta trasferimento/hold. |
| 11–15h | Simulazione giornaliera; rumore, caso ambiguo, modifica live di ETA/stock; fonte esterna di contesto. |
| 15–18h | Valutazione su dati separati, ablation, revisione delle prove; freeze funzionalità. |
| 18–24h | Correzioni, replay deterministico, pitch, prova generale e registrazione backup. |

P1: estrazione/linking. P2: stato/provenienza e decisore. P3: schede/UI. P4: tools, eval e pitch con supporto del team. Nessuno sviluppa un secondo prodotto indipendente.

**Se restano circa 12 ore:** input testuale/EML, 2 lingue, una coppia donatore-destinazione, stock/forecast CSV, un tool di verifica reale e tre opzioni. Tagliare prima immagini, clustering cross-store e riconciliazione report; preservare caso dubbio, caso senza azione, citazioni e test temporale.

## 9. Demo di 4–5 minuti

1. **30s — La decisione bloccata.** Il piano dice una cosa, il negozio segnala domanda che le vendite non registrano. Mostrare istante di conoscenza e dati sintetici.
2. **60s — Dalle fonti al caso.** Nota in lingua → estratto → prodotto/taglia → un solo caso, anche se la mail è inoltrata tre volte.
3. **60s — L'agente indaga.** Stock contabile e nota divergono; verifica disponibilità/ETA. Un fatto smentisce l'opzione iniziale e l'agente cambia proposta.
4. **60s — La decisione.** Trasferimento/riassortimento/hold, vincoli e conseguenze sotto scenari. Modificare live ETA o domanda del donatore produce un ricalcolo.
5. **30s — Sa fermarsi.** Un nome prodotto ambiguo produce chiarimento; un trend social senza riscontro resta monitoraggio.
6. **30–60s — Evidenza del valore.** Metriche calcolate, limiti, asset Fastweb usati e bozza approvabile. Nessun ROI inventato.

Scheda minima: **cosa è cambiato · perché conta ora · scadenza · owner · opzioni · evidenze a favore/contro · cosa potrebbe cambiare la raccomandazione**. L'HQ vede anche implicazioni coordinate: allocation controlla disponibilità, logistica verifica arrivo, marketing evita una comunicazione su prodotti indisponibili. Non servono tre motori separati.

## 10. Come dimostrare valore e non soltanto una bella storia

Usare [le regole del dataset](../generated/README.md): input solo da `sources`, oracolo solo nell'eval, split dev/hold-out, timestamp di disponibilità. Il generatore non è stato letto per questa ricerca. Gli esempi nel README sono scenari noti al team, non una validazione indipendente.

Confrontare tre versioni sullo stesso tempo di osservazione e sugli stessi casi:

| Variante | Cosa misura |
|---|---|
| **B0: dati strutturati disponibili + regole stock/forecast** | Baseline operativa onesta; non privarla di inventario o informazioni che avrebbe davvero. |
| **B1: B0 + estrazione LLM senza gestione di prove/conflitti** | Se aggiungere testo ingenuamente aumenta anche falsi allarmi. |
| **B2: pipeline proposta** | Valore aggiunto di dedup, verifiche mirate, astensione e vincoli. |

Metriche prioritarie: precisione delle schede azionabili, recall dei casi utili, link errati accettati **insieme alla quota di astensioni**, violazioni dei vincoli, alert per manager/giorno, tempo fino a una raccomandazione valida, chiamate/token per caso. Lead time = `tempo primo alert valido baseline − tempo primo alert valido sistema`; usare lo stesso budget di falsi allarmi quando possibile.

Quando la baseline non rileva il fenomeno entro il replay, riportare «non rilevato entro la finestra», non anticipo infinito. Per unmet demand distinguere rilevare lo stockout da stimare il volume di domanda persa. L'anticipo non è necessariamente di settimane: dipende dal caso e dai timestamp effettivi.

**Ablation minima:** duplicare le fonti, aggiungere rumore, rimuovere la prova più importante, inserire una rettifica e ritardare un report. Verificare che il caso reagisca coerentemente. WAPE della previsione è secondaria; quando valutabile, affiancarla al costo delle decisioni o alle unità non servite sotto ipotesi comuni. Non equiparare simulazione a fatturato recuperato realmente.

Target per demo: nessuna violazione dei vincoli implementati e citazioni verificabili; sono obiettivi di accettazione, **non risultati già raggiunti**. Mostrare il numero di esempi e gli errori, non solo una percentuale.

## 11. Decisioni da prendere adesso

1. **Confermare allocation HQ come primo buyer**, con retail ops come percorso di verifica e marketing come conseguenza dello stesso caso.
2. **Scegliere un caso di domanda non soddisfatta + conflitto di disponibilità**, preferibilmente domestico per ridurre vincoli logistici nel primo percorso.
3. **Congelare un modello chat e l'endpoint embedding** dopo un confronto piccolo e reale; una sola escalation opzionale.
4. **Accettare scenari espliciti al posto di un forecast “corretto” a tutti i costi.** La qualità della decisione è il criterio principale.
5. **Riservare almeno un quarto del tempo alla verifica e alla demo.** Il kickoff premia soprattutto fattibilità (40%) e innovazione agentica (20%).

Il differenziale sostenibile, da validare dopo l'hackathon, è il collegamento fra evidenze locali e vincoli operativi, con feedback sulle decisioni. Non è dimostrato che nessun concorrente lo faccia: evitare claim di unicità di mercato senza un'analisi competitiva dedicata.
