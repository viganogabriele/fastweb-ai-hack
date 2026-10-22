# Ricerca: integrare evidenze eterogenee senza amplificare il rumore

_22 ottobre 2026. Approfondimento della [raccomandazione di progetto](research-recommendation.md). Fonti primarie; le applicazioni proposte sono nostre inferenze, non risultati già ottenuti sul dataset._

## Il problema corretto

«Dati non correlati» qui significa soprattutto dati **non ancora collegati**: una mail parla di un colore, il magazzino usa un codice materiale, il CRM un altro identificativo negozio, un report una diversa settimana commerciale. Prima di cercare correlazioni statistiche servono identità, tempo, granularità, definizione della metrica e provenienza comuni. Fonti realmente prive di relazione con la decisione possono restare fuori.

Una rappresentazione utile è una tabella di affermazioni atomiche: chi sostiene cosa, su quale entità, quando è successo, quando lo abbiamo saputo, con quale prova e quali conflitti. Non occorre trasformare tutto in un grafo generalista.

## Paper selezionati e scelta pratica

Le stime di sforzo riguardano un prototipo limitato, con API già funzionanti; non la riproduzione completa dei paper.

| Riferimento primario | Contributo effettivo | Applicazione proposta | Limite e scelta 24h |
|---|---|---|---|
| Dong, Berti-Equille, Srivastava, **Integrating Conflicting Data: The Role of Source Dependence**, PVLDB 2009 ([paper](https://www.vldb.org/pvldb/vol2/vldb09-pvldb47.pdf)) | Modella dipendenza e accuratezza delle fonti: informazioni copiate possono falsare il voto di maggioranza. | Conservare `origin_id`, thread, duplicati, `supports`/`contradicts`; contare origini distinte. | Una maggioranza non garantisce verità. Fare dedup e gruppi di provenienza, non stimare tutta la rete bayesiana. Circa 2–3h. |
| Ratner et al., **Snorkel: Rapid Training Data Creation with Weak Supervision**, PVLDB 2017 ([paper](https://arxiv.org/abs/1711.10160)) | Combina funzioni di etichettatura rumorose per costruire dati di training, modellando accuratezze e correlazioni. | Regole per negazioni, quantità esplicite, correzioni e disponibilità; loggare disaccordi con l'LLM. | Non è un sistema che scopre automaticamente la verità delle mail. In 24h usare regole esplicite e astensione; il label model è una roadmap. 1–2h per le regole. |
| Li et al., **Deep Entity Matching with Pre-Trained Language Models (Ditto)**, preprint 2020 / VLDB 2021 ([paper](https://arxiv.org/abs/2004.00584)) | Fine-tuning di transformer per classificare coppie di record, con conoscenza di dominio e augmentation. | Separare generazione dei candidati e verifica della corrispondenza; inserire attributi di catalogo. | Il matching di record dei benchmark non è identico a «quello nero lungo» in una mail. Non addestrare Ditto in hackathon. |
| Peeters, Steiner, Bizer, **Entity Matching using Large Language Models**, preprint 2023, revisione 2024 ([paper](https://arxiv.org/abs/2310.11244)) | Confronta matching zero/few-shot, sensibilità ai prompt e generalizzazione a entità nuove. | LLM sceglie fra pochi candidati, oppure dichiara ambiguità; prompt verificati per modello e lingua. | Nessun prompt universalmente migliore. Una spiegazione plausibile non certifica il link. Circa 2–4h con valutazione manuale. |
| Chen et al., **M3-Embedding**, preprint 2024, revisione 2025 ([paper](https://arxiv.org/abs/2402.03216)) | Retrieval multilingua con rappresentazioni dense, sparse e multi-vector. | Combinare alias/codici esatti e similarità semantica; usare la ricerca semantica per recuperare candidati. | Similarità non equivale a identità, accordo o rilevanza economica. Riferimento metodologico; usare l'endpoint embedding già fornito. |
| Li et al., **Qwen3-VL-Embedding and Qwen3-VL-Reranker**, technical report 2026 ([paper](https://arxiv.org/abs/2601.04720), [codice degli autori](https://github.com/QwenLM/Qwen3-VL-Embedding)) | Spazio di rappresentazione condiviso per testo e immagini; modelli embedding e reranker distinti, nelle taglie 2B/8B. | Recuperare prodotto/evidenza da una descrizione multilingua o da una foto; il 2B è nell'offerta hackathon. | Il reranker non risulta fra gli endpoint assegnati. Nessun trasferimento automatico dei risultati dell'8B al 2B. MVP testo; immagine solo come estensione dopo la demo base. |
| Edge et al., **From Local to Global: A Graph RAG Approach to Query-Focused Summarization**, preprint 2024, revisione 2025 ([paper](https://arxiv.org/abs/2404.16130)) | Grafo di entità e riassunti di comunità per rispondere a domande globali su corpora. | Ispirazione per collegare prove e casi e riassumere un portafoglio di problemi. | Misura qualità dei riassunti, non validità di trasferimenti o previsioni. Non implementare GraphRAG completo; bastano tabelle relazionali con riferimenti. |
| Yao et al., **ReAct: Synergizing Reasoning and Acting in Language Models**, preprint 2022 / ICLR 2023 ([paper](https://arxiv.org/abs/2210.03629)) | Alterna pianificazione e interazione con strumenti in task di QA e ambienti interattivi. | Un investigatore sceglie la prossima verifica: stock, disponibilità, lead time, chiarimento. | I benchmark non dimostrano sicurezza o redditività retail. Tool con schema, budget di chiamate e verifiche deterministiche. Circa 2–4h. |
| Steiner, Bizer, **Labeling Training Data for Entity Matching Using Large Language Models**, preprint giugno 2026, revisione 5 ottobre ([v2](https://arxiv.org/abs/2606.28823v2)) | Distillazione da LLM a matcher compatto; vantaggi di inferenza sui benchmark, ma difficoltà sugli articoli mai visti. | Dopo il prototipo usare correzioni umane e teacher LLM per addestrare un matcher economico; mantenere escalation per novità. | Non è un guadagno già misurato qui. La revisione riporta 34–459× meno tempo di inferenza in quei test, non una garanzia operativa. Roadmap. |
| Liu et al., **Lost in the Middle: How Language Models Use Long Contexts**, preprint 2023, TACL ([paper](https://arxiv.org/abs/2307.03172)) | Nei modelli testati, il recupero dell'informazione dipende anche dalla posizione nel contesto. | Inviare evidenze selezionate e strutturate, non l'intero archivio in un prompt. | Non prova che tutti i modelli del 2026 abbiano lo stesso difetto; motiva un test locale di sensibilità a rumore e posizione. |

## Come fondere le fonti

1. **Parser per formato.** CSV e XLSX con parser tabellari, EML con decoder MIME; vision solo per pagine raster o immagini. Salvare unità, formula della metrica, perimetro, valuta e date. Un embedding di tabella non sostituisce la lettura delle celle.
2. **Estrazione atomica.** Una mail può contenere arrivi, vendite, richieste, stockout e una previsione personale. Sono affermazioni distinte con diversi livelli di evidenza.
3. **Link al catalogo.** ID/alias → candidati semantici → verifica attributi. L'assortimento locale migliora il ranking ma non deve escludere tutto il catalogo: la domanda per un prodotto assente è centrale.
4. **Stato e provenienza.** Collegare ripetizioni, rettifiche e chiusure. Un forward non aggiunge una fonte indipendente; un nuovo evento uguale a quello di ieri può invece essere nuova evidenza.
5. **Conflitti espliciti.** Stock contabile di ieri e osservazione sullo scaffale di oggi possono descrivere tempi diversi. Prima di marcare un errore, allineare timestamp, prenotazioni, SKU-taglia, stock vendibile e arrivi.
6. **Priorità per decisione.** Il motore considera soltanto prove pertinenti alla specifica azione e al suo orizzonte. Un report di turismo vecchio non conferma da solo un picco questa sera.

## Tre innovazioni implementabili

**Prove indipendenti, non numero di menzioni.** Un post, cinque repost e il recap del manager possono essere una sola origine. Visualizzare «7 documenti, 1 origine» rende comprensibile la protezione contro il rumore. La dipendenza non sempre è osservabile: indicare «origine sconosciuta» invece di garantire indipendenza.

**Robustezza della decisione alla rimozione di una prova.** Ricalcolare le opzioni togliendo a turno ogni gruppo di origine. Se basta eliminare una mail dubbia per cambiare azione, chiedere verifica. È un test di sensibilità, non un'identificazione causale e non una probabilità di correttezza.

**Clustering dell'ignoto con budget.** Tenere le affermazioni non collegate in una coda a bassa priorità. Un piccolo cluster di richieste simili provenienti da negozi diversi può segnalare un bisogno fuori catalogo. La categoria `unknown` evita di forzare tutto nelle etichette esistenti; soglie, copertura e rumore vanno valutati. Estensione, non prerequisito della demo.

## Scalabilità concreta

- Una estrazione per documento nuovo o corretto; cache su hash + versione modello/prompt/schema.
- Alias e codici prima degli embedding; catalogo indicizzato una volta, aggiornato per delta.
- LLM su top-k candidati e casi selezionati, mai confronto di ogni documento con ogni prodotto.
- Dedup e raggruppamenti prima del ragionamento costoso; batch controllati e gestione 429.
- Conservare le evidenze originali insieme al risultato strutturato, così una correzione non richiede reinterpretare tutto.
- Per il catalogo del dataset, una matrice di embedding in memoria e SQLite possono bastare; non serve partire con un nuovo database a grafo o un cluster distribuito.

L'idea di usare 512 dimensioni invece di 2048 viene dalla guida Fastweb: riduce di 4× i byte dei soli vettori a parità di precisione numerica, **non** garantisce 4× velocità né qualità invariata. Misurare recall@k su menzioni etichettate prima di scegliere.
