# Metodi scientifici per passare dai segnali alle decisioni retail

_Ricerca al 22 ottobre 2026. Orizzonte operativo: 1–14 giorni. Budget: hackathon di 24 ore._

**Raccomandazione:** costruire un triage verificabile di casi, seguito da confronto fra poche azioni logistiche fattibili. Mantenere il forecast esistente come baseline versionata; aggiungere diagnostica dei residui, evidenze testuali e scenari temporanei. L’uscita utile è «verificare lo stock / chiedere quale prodotto / proporre un trasferimento entro una scadenza / monitorare», anche quando non è possibile stimare un nuovo numero di domanda.

Questa nota usa come contesto esclusivamente `docs/findings.md`, `docs/project-design.md` e `generated/README.md`. Non sono stati aperti `generated/ground_truth/`, `generator/` o hidden answers. Il README contiene già anticipazioni dei casi: non vanno trasformate in regole del prodotto, esempi di prompt o evidenza sperimentale. Non sono stati eseguiti esperimenti sul dataset: costi, architettura e soglie proposti qui sono valutazioni progettuali, non risultati misurati.

## 1. Le distinzioni che devono comparire nella demo

| Oggetto | Significato corretto | Cosa non promettere |
|---|---|---|
| Regola euristica | Mapping esplicito, ad esempio «molti» → scenario di intensità, decadimento a sette giorni, soglia di alert | Che i parametri siano appresi o che il punteggio sia una probabilità |
| Stima statistica | Parametri ricavati da osservazioni: mediana dei residui, regressione robusta, posterior Gamma-Poisson | Che l’esecuzione deterministica significhi «nessun modello» |
| Modello addestrato | Parametri ottimizzati su un training set con obiettivo dichiarato | Che un LLM preaddestrato sia stato addestrato sui dati retail del team |
| Scenario low/base/high | Esito condizionato a ipotesi diverse, anche non probabilistiche | «Intervallo all’80%», confidenza o frequenza di copertura |
| Intervallo predittivo bayesiano | Distribuzione della futura osservazione sotto prior e likelihood specificate | Calibrazione empirica automatica, soprattutto con censura e misspecificazione |
| Intervallo conformal | Insieme predittivo costruito da score e dati di calibrazione, con garanzie precise sotto ipotesi precise | Copertura per ogni negozio, sotto qualsiasi drift, o della domanda latente usando solo vendite |
| Priorità | Ordine di lavorazione basato su conseguenze, urgenza e fattibilità | Probabilità dell’evento, effetto causale o ROI dimostrato |

**Due diverse coverage:** nella selective prediction è la quota di casi su cui si risponde; nella previsione intervallare è la quota di esiti contenuti nell’intervallo. Servono nomi distinti nei risultati. Le qualifiche scientifiche sono motivate da R4–R7; le etichette di prodotto sono una nostra proposta.

## 2. Dodici riferimenti selezionati e loro uso concreto

Solo lavori originali, pagine degli autori/istituzioni, editori o proceedings. Dove il testo integrale non era accessibile, il risultato riportato resta al livello dell’abstract primario. Le ore sono stime per una persona con input già normalizzati, comprendono verifica essenziale ma non ingestione e UI; **non si sommano in un piano di implementazione di tutti i metodi**.

### R1 — Huber, 1964: robustezza rispetto a osservazioni anomale

[Robust Estimation of a Location Parameter, Annals of Mathematical Statistics](https://doi.org/10.1214/aoms/1177703732); [riedizione dell’originale con abstract verificato, Springer 1992](https://link.springer.com/chapter/10.1007/978-1-4612-4380-9_35).

- **Risultato:** sviluppa stimatori di posizione intermedi fra media e mediana con proprietà di robustezza asintotica per normali contaminate.
- **Non dimostra:** robustezza a ogni drift, correzione della censura o validità dei testi dei negozi. Un cambiamento reale persistente non è necessariamente un outlier da eliminare.
- **Qui:** stimare il bias dei residui del forecast su periodi comparabili e non censurati; limitare l’effetto di errori numerici isolati.
- **24h:** fit Huber e controllo dei residui, 2–4h; **alternativa:** mediana e MAD, 1–2h. Sono stime dai dati; clipping e soglie rimangono scelte euristiche.

### R2 — Adams e MacKay, 2007: cambiamenti online

[Bayesian Online Changepoint Detection, preprint originale](https://arxiv.org/abs/0710.3742), [testo](https://arxiv.org/pdf/0710.3742).

- **Risultato:** inferenza ricorsiva della distribuzione del tempo dall’ultimo cambiamento, sotto un modello a segmenti con osservazioni i.i.d. entro segmento e parametri indipendenti fra segmenti.
- **Non dimostra:** causa del cambiamento, calibrazione sotto un modello errato o superiorità su domanda luxury intermittente.
- **Qui:** applicazione opzionale ai residui aggregati, separando bias stabile e rottura recente; non alle menzioni duplicate trattate come osservazioni indipendenti.
- **24h:** 4–8h con hazard e likelihood da validare; **alternativa:** accumulatore CUSUM o EWMA con soglie fissate sul dev, 1–2h. La variante troncata della ricorsione è un’approssimazione, non l’inferenza esatta del paper.

### R3 — Giannone, Reichlin e Small, 2008: nowcasting e calendario delle pubblicazioni

[Nowcasting: The real-time informational content of macroeconomic data, pubblicazione verificata dall’autore](https://sites.krieger.jhu.edu/domenico-giannone/publications/); [working paper originale BCE, 2006](https://www.ecb.europa.eu/pub/pdf/scpwps/ecbwp633.pdf).

- **Risultato:** aggiornamento del nowcast macroeconomico e valutazione del contributo marginale delle nuove pubblicazioni, gestendo molte serie con date di rilascio sfalsate.
- **Non dimostra:** trasferibilità quantitativa dal PIL a SKU/taglie o capacità delle email di anticipare qualsiasi shock.
- **Qui:** adottare il principio dei vintage e dell’aggiornamento quando una fonte diventa disponibile. La domanda odierna non ancora certificata è un nowcast; i successivi 1–14 giorni sono una previsione operativa.
- **24h:** un modello fattoriale completo non è prioritario, >1 giornata; **alternativa:** replay temporale e overlay sul forecast, 2–4h. L’overlay è un adattamento progettuale, non una replica del paper.

### R4 — Chow, 1970: classificare oppure astenersi

[On Optimum Recognition Error and Reject Tradeoff, IEEE Transactions on Information Theory; scheda primaria IBM](https://research.ibm.com/publications/on-optimum-recognition-error-and-reject-tradeoff), [paper DOI](https://doi.org/10.1109/TIT.1970.1054406).

- **Risultato:** caratterizza la regola ottima di rifiuto e il compromesso fra errori e rifiuti nel riconoscimento probabilistico.
- **Non dimostra:** che score fuzzy, margini di reranking o confidence dichiarata da un LLM siano posterior affidabili.
- **Qui:** un collegamento prodotto errato costa più di una richiesta di chiarimento; misurare errore sui casi accettati e quota accettata, includendo prodotti fuori catalogo/assortimento.
- **24h:** policy di astensione e valutazione, 2–3h; **alternativa:** chiedere sempre quando due candidati restano plausibili. Addestrare/calibrare un classificatore selettivo richiede etichette adeguate; una soglia manuale è una policy euristica.

### R5 — Gibbs e Candès, 2021: adaptive conformal inference

[Adaptive Conformal Inference Under Distribution Shift, NeurIPS](https://proceedings.neurips.cc/paper_files/paper/2021/hash/0d441de75945e5acbc865406fc9a2559-Abstract.html), [testo, proposizione 4.1](https://papers.nips.cc/paper/2021/file/0d441de75945e5acbc865406fc9a2559-Paper.pdf).

- **Risultato:** un aggiornamento online del livello nominale controlla la frequenza empirica degli errori sul lungo periodo anche con distribuzione variabile.
- **Non dimostra:** copertura condizionale domani per questo SKU, intervalli stretti o affidabilità dopo pochi esempi. La formalizzazione ammette insiemi estremi, anche non informativi.
- **Qui:** possibile wrapper futuro del forecast, con aggiornamenti solo quando arriva l’esito; i target a 14 giorni non sono disponibili domani.
- **24h:** prototipo 3–5h con feedback semplice; ritardi e censura richiedono lavoro ulteriore. **Alternativa:** scenari dichiarati e monitoraggio degli errori, senza percentuali di copertura promesse.

### R6 — Barber, Candès, Ramdas e Tibshirani, 2023: oltre l’exchangeability

[Conformal prediction beyond exchangeability, Annals of Statistics](https://doi.org/10.1214/23-AOS2276), [manoscritto originale, preprint 2022](https://arxiv.org/abs/2202.13415).

- **Risultato:** conformal pesato e randomizzazione con limiti alla perdita di copertura legati alla non-exchangeability, espressa mediante distanze fra distribuzioni.
- **Non dimostra:** che assegnare più peso ai dati recenti dia automaticamente copertura nominale sotto drift arbitrario; il bound può essere poco informativo.
- **Qui:** giustifica distinguere calibrazione marginale, drift e segmenti operativi. Pooling fra paesi/stagioni richiede verifica, non soltanto più righe.
- **24h:** score e quantili pesati 3–5h, validazione sostanziale oltre il budget; **alternativa:** quantili storici descrittivi con numerosità e finestra esposte. Non chiamarli garantiti.

### R7 — Gibbs e Candès, 2024: adattamento locale più recente

[Conformal Inference for Online Prediction with Arbitrary Distribution Shifts, JMLR 25(162)](https://www.jmlr.org/papers/v25/22-1218.html), [testo](https://www.jmlr.org/papers/volume25/22-1218/22-1218.pdf).

- **Risultato:** DtACI adatta il passo di aggiornamento; il lavoro fornisce garanzie di regret su intervalli locali e sperimentazioni sotto cambiamento di distribuzione.
- **Non dimostra:** copertura esatta su ciascun periodo di 1–14 giorni, né risolve feedback censurato o prodotto nuovo senza etichette. Regret e copertura condizionale sono proprietà diverse.
- **Qui:** roadmap dopo aver costruito feedback temporale e benchmark; nessun vantaggio del paper va riportato come risultato del prototipo.
- **24h:** integrazione/validazione 6–10h o più; **alternativa:** nessun adattamento sofisticato, ma indicatore di errore recente e astensione quando i dati non sostengono una stima.

### R8 — Howard, 1966: valore dell’informazione

[Information Value Theory, IEEE Transactions on Systems Science and Cybernetics](https://ieeexplore.ieee.org/document/4082064/), [DOI](https://doi.org/10.1109/TSSC.1966.300074). Verificato l’abstract dell’editore indicizzato; accesso diretto integrale limitato.

- **Risultato:** il valore di ridurre l’incertezza dipende congiuntamente da probabilità e conseguenze economiche; i valori delle informazioni non sono necessariamente additivi.
- **Non dimostra:** che una domanda al negozio sia utile solo perché riduce l’entropia, né fornisce probabilità/costi per questo caso.
- **Qui:** chiedere «quale taglia?» o «stock fisico confermato?» se la risposta può cambiare un’azione ancora eseguibile prima del cutoff.
- **24h:** EVSI su pochi stati con probabilità esplicite, 2–4h; **alternativa:** confrontare le decisioni nei diversi scenari e chiedere quando cambiano. Quest’ultimo è triage per sensibilità, non EVSI stimato.

### R9 — Elmachtoub e Grigas, 2022: apprendere per la decisione

[Smart “Predict, then Optimize”, Management Science 68(1)](https://doi.org/10.1287/mnsc.2020.3922), [manoscritto degli autori](https://arxiv.org/abs/1710.08005), [versione pubblicata nel repository NSF](https://par.nsf.gov/servlets/purl/10339524).

- **Risultato:** propone una loss sull’errore decisionale e il surrogato convesso SPO+, con risultati di consistenza sotto ipotesi e confronti sperimentali su cammini e portafogli.
- **Non dimostra:** miglioramento universale per logistica retail, né equivalenza fra minimizzare WAPE e minimizzare danno operativo.
- **Qui:** usare costi e vincoli per valutare le opzioni; eventualmente in futuro apprendere l’overlay sui residui usando una loss decisionale.
- **24h:** training SPO+ con ottimizzatore e dati appropriati, >1 giornata; **alternativa:** enumerare azioni e confrontare costi per scenario, 2–4h. Un solver deterministico senza training non è decision-focused learning.

### R10 — Besbes e Muharremoglu, 2013: il valore di sapere che la domanda è censurata

[On Implications of Demand Censoring in the Newsvendor Problem, Management Science; fonte degli autori Columbia](https://business.columbia.edu/faculty/research/implications-demand-censoring-newsvendor-problem).

- **Risultato:** nel loro newsvendor ripetuto con domanda discreta, confrontano domanda osservata, sole vendite e vendite con indicatore di lost sales. Nei setting analizzati il miglior regret passa da crescita logaritmica con sole vendite a limitato con informazione aggiuntiva.
- **Non dimostra:** che basti qualsiasi email rumorosa, o che i risultati valgano senza ipotesi in un sistema multi-negozio non stazionario.
- **Qui:** trattare il flag di censura come informazione utile anche senza inventare quante unità siano state perse.
- **24h:** flag, provenienza e policy conservativa 1–2h; algoritmo di apprendimento del paper non prioritario. **Alternativa:** non aggiornare verso il basso la domanda usando giorni sicuramente censurati.

### R11 — Sachs e Minner, 2014: stimare lost sales usando tempi di vendita

[The data-driven newsvendor with censored demand observations, International Journal of Production Economics 149](https://www.sciencedirect.com/science/article/abs/pii/S092552731300203X).

- **Risultato:** combina pattern intragiornalieri, variabili esogene e programmazione lineare per stimare vendite perse e livelli di scorta; riporta vantaggi nei confronti numerici e su dati retail studiati.
- **Non dimostra:** identificazione della domanda da soli saldi serali, né validità dei pattern intraday nel luxury a basso volume.
- **Qui:** estensione possibile se POS orario e momento dello stockout sono affidabili. «Esaurito da mezzogiorno» informa il tempo di esposizione, non un moltiplicatore universale.
- **24h:** 6–10h con dati adeguati, altrimenti da rimandare; **alternativa:** annotare la censura e mostrare scenari, mantenendo separati i conteggi espliciti delle richieste.

### R12 — Tashman, 2000: valutazione fuori campione temporale

[Out-of-sample tests of forecasting accuracy: an analysis and review, International Journal of Forecasting 16(4)](https://www.sciencedirect.com/science/article/pii/S0169207000000650).

- **Risultato:** analizza scelte di valutazione fuori campione e raccomanda origini mobili e più periodi per ridurre la dipendenza da una singola origine; distingue aggiornamento, ricalibrazione e selezione del metodo.
- **Non dimostra:** che un generico split temporale elimini leakage da revisioni, report pubblicati tardi o tuning sul test.
- **Qui:** replay a timestamp fissati, target per orizzonte e separazione di sviluppo, calibrazione e test; aggiungere la separazione per negozio prevista dal README.
- **24h:** harness minimo 3–5h; **alternativa:** poche origini congelate e auditabile selezione delle fonti. È un test limitato, non una stima della performance in produzione.

## 3. Fronte 1 — residui e nowcasting senza sostituire il forecast

### Baseline e granularità

Il dataset documenta forecast **SKU-colore × negozio × settimana**, mentre il design calcola per giorno e taglia. Prima di qualsiasi correzione fissare: vintage disponibile, unità fisiche o valore, settimana di riferimento, calendario di apertura e granularità. Non sommare livelli regione/store/SKU che il README dichiara non riconciliati.

Per una disaggregazione dimostrativa, usare pesi giornalieri non negativi `p_d` che sommano a 1 nella settimana e pesi taglia `p_size` che sommano a 1 per articolo-colore. Stimare questi pesi solo sul passato disponibile e in condizioni di disponibilità adeguata; in alternativa usare una policy uniforme sui giorni aperti e dichiarare l’assunzione. Senza curva taglie credibile, lasciare la previsione al livello colore e proporre azioni di taglia solo su evidenze specifiche. Non moltiplicare la quantità totale per ciascuna taglia.

### Diagnostica minima proposta

Per osservazioni con vendite di unità non censurate, complete e disponibili, confrontare `e_t = y_t − f_{v(t),t}`: il forecast deve essere quello utilizzabile al momento della decisione, non l’ultimo file del repository. Per confrontare serie con scale diverse:

```text
m = mediana dei residui nel passato ammissibile
s = max(epsilon, 1.4826 * mediana(|e - m|))
z_t = (e_t - m) / s
C_t = max(0, C_(t-1) + clip(z_t, -c, c) - k)
alert se C_t > h
```

È un **CUSUM robustificato proposto per il prototipo**, non una garanzia statistica derivata da R1/R2. `epsilon`, `c`, `k`, `h`, finestra e reset vanno fissati sul dev. Conservare separatamente `m`: centrare i residui nasconde al detector un bias stabile, che è comunque informazione utile. Con molte serie quasi sempre zero, MAD può essere zero e i giorni pochi: aggregare a colore/store o a una finestra più lunga; non usare z-score come probabilità o p-value. Su dati mancanti non inserire uno zero; su dati censurati sospendere l’aggiornamento e mantenere l’età dello stato.

Per un overlay quantitativo minimo, usare un solo offset robusto smorzato, stimato dal passato non censurato, oppure un unico fattore scenario per caso; non sommare correzioni diverse derivate dagli stessi fatti. Ad esempio `f_scenario(T+h) = max(0, f_base(T+h) + b_scenario * decay(h))`, con `b` in unità/giorno e scadenza esplicita. Una nota qualitativa senza quantità può aprire un caso e modificarne la priorità senza cambiare il forecast.

La nota arriva prima della certificazione, quindi può produrre un nowcast informativo anche senza un residuo odierno. Non fabbricare `y_D` usando il dato di domani. Un’affermazione di fatturato nella mail è una misura provvisoria distinta, non la vendita certificata e non necessariamente una quantità di SKU.

## 4. Fronte 2 — incertezza, astensione e valore delle verifiche

### Quattro incertezze separate

Conservare distintamente: identità del prodotto; attendibilità e completezza della fonte; variabilità della domanda; stato e tempi logistici. Tre mail che citano lo stesso messaggio originario non sono tre conferme indipendenti. Il meteo coerente con una nota può essere contesto utile, ma alzare automaticamente la confidence di un livello resta un’euristica, non un aggiornamento bayesiano.

Per M4: usare candidati dal catalogo con priorità all’assortimento, ma mantenere un fallback fuori assortimento e l’opzione «nessuno dei candidati». Il README documenta richieste per prodotti non venduti dal negozio: restringere rigidamente all’assortimento impedisce il match corretto. Separare assenza di prodotto, prodotto ignoto e ambiguità. Nessuna soglia del reranker va presentata come «90% sicuro» senza verifica indipendente. R4 motiva l’astensione, non certifica questi score.

### Quando avrebbe senso conformal

Per un predictor congelato e score assoluti di calibrazione, lo split conformal usa l’ordine `ceil((n+1)*(1-alpha))` degli `n` errori; se l’indice supera `n`, il caso formale non si risolve tagliandolo arbitrariamente all’ultimo elemento. La copertura marginale standard richiede exchangeability. R6 descrive sia questo quadro sia i limiti oltre tale ipotesi.

**Qui manca spesso il target:** se calibrato su vendite censurate, l’intervallo riguarda vendite, non domanda latente. Se si selezionano solo giorni in-stock, cambia la popolazione di calibrazione. Inoltre gli orizzonti sovrapposti sono dipendenti: sommare intervalli giornalieri all’80% non produce un intervallo all’80% per il totale settimanale. Calibrare direttamente il target dell’orizzonte e registrare numerosità, periodo, gruppi ed errori; sotto drift esporre copertura empirica e ampiezza, senza promessa nominale automatica. Per la demo è preferibile una banda di scenario onesta a una calibrazione non sostenuta dai dati. R5–R7 sono roadmap, non requisito della vertical slice.

### Priorità operativa e domanda al negozio

Proposta euristica leggibile: prima casi con rischio di violare una policy o stock non verificato; poi casi con finestra d’azione in chiusura e beneficio plausibile; infine monitoraggio. Dentro ogni classe ordinare per conseguenza stimata, mostrando ipotesi e dati mancanti. Non inventare un unico score probabilistico da fattori non calibrati.

Una scadenza operativa è `decision_due_at = required_arrival_at − lead_time − handling_buffer`, corretta per cutoff, weekend e dogane. Una domanda che riceverà risposta dopo questa scadenza non ha lo stesso valore di una verifica immediata.

Se esistono probabilità e costi difendibili, la riduzione attesa di perdita prima del costo della verifica è:

```text
EVSI = min_a E[L(a, theta)]
       - E_z[min_a E[L(a, theta) | z]]
valore netto = EVSI - costo_verifica - costo_ritardo
```

È una specializzazione decisionale coerente con R8. Il ritardo può anche cambiare l’insieme delle azioni fattibili: in tal caso va modellato dentro la seconda ottimizzazione, evitando un doppio conteggio. Senza probabilità, valutare se l’azione migliore cambia fra scenari plausibili: se cambia per identità della taglia, stock fisico o ETA, chiedere quel dato. Se non cambia, la verifica può avere bassa priorità. Chiamarlo **sensibilità della decisione**, non valore atteso misurato.

## 5. Fronte 3 — censura e simulazione delle azioni

### Domanda, vendite e richieste non sono lo stesso oggetto

Nel modello semplificato `Y = min(D, A)`, `A` è disponibilità vendibile durante il periodo, non saldo ERP serale. Se si esauriscono le scorte, si osserva un vincolo sulla domanda, non il suo valore. Arrivi intraday, prenotazioni, resi, sostituzioni e inventario fantasma rendono la situazione più complessa. I resi vanno separati dalle vendite lorde di unità: il net sales economico può essere negativo e non è un conteggio Poisson.

Una richiesta insoddisfatta documentata può essere utile come limite inferiore **solo** se corrisponde a intenzione di acquisto, quantità e periodo definiti, senza duplicati o successiva conversione già contata. Un generico «molti chiedono il nero» non è tale limite e non dà un limite superiore finito. Assenza di note non equivale ad assenza di domanda. R10–R11 sostengono l’importanza dell’osservazione della censura; non autorizzano a imputare automaticamente tutte le vendite perse.

Per una futura likelihood censurata discreta, una vendita non censurata `y` contribuisce `P(D=y | theta)`; una vendita al limite `A` contribuisce `P(D>=A | theta)` quando si sa solo che l’inventario è esaurito. Un indicatore affidabile di domanda persa strettamente positiva implica invece `P(D>A | theta)`. Con `A=0`, il primo evento non informa sulla quantità. Sostituire tutto con `P(D=A)` sottostima la coda. Questa è una derivazione dal modello semplificato, non un algoritmo validato sul dataset.

### Confronto fattibile delle opzioni

Per ciascuno scenario `s`, destinazione e donatore, simulare una **sequenza giornaliera** di domanda `d_(s,h)` e arrivi, non soltanto un totale:

```text
available_(s,h) = ending_stock_(s,h-1) + sellable_arrivals_(s,h) - outbound_(s,h)
served_(s,h)    = min(demand_(s,h), max(0, available_(s,h)))
lost_(s,h)      = demand_(s,h) - served_(s,h)
ending_stock   = max(0, available_(s,h) - served_(s,h))
```

Le quantità iniziali sono già al netto delle prenotazioni non disponibili; non sottrarle due volte. Definire l’ordine intraday: nello schema gli arrivi precedono le vendite; un arrivo a chiusura va al giorno seguente. Per lost sales la domanda non servita non si accumula come backlog, salvo un modello separato di waitlist confermata.

Controllare stock fisico/ATP, quality hold, taglia ed EAN, ID cross-system, lead time della lane, cutoff, dogana, ricevimenti parziali, riserve e policy di scarsità. Il donatore va protetto lungo tutto il periodo, non solo tramite il saldo finale. Riservare le unità anche fra più proposte contemporanee: ogni card isolata può essere fattibile e l’insieme impossibile.

Enumerare `hold`, verifica, DC, trasferimento e combinazione. Per ogni scenario confrontare perdita da mancato servizio, costo trasporto, rischio imposto al donatore ed eccedenza. Senza probabilità riportare «unità non servite nello scenario s»; con probabilità esplicite si può calcolare un’attesa. Una scelta robusta può minimizzare il peggior costo o regret sul piccolo insieme di scenari, ma resta robusta **rispetto a quell’insieme**, non rispetto a qualsiasi futuro. Il punto di R9 è l’obiettivo decisionale; qui non si addestra SPO.

## 6. Audit di `project-design.md`

Le seguenti sono osservazioni sul design letto, non modifiche al file.

| Punto | Diagnosi | Correzione minima proposta |
|---|---|---|
| §5.1, esempio del decadimento | **Aritmetica corretta:** somma per t=1…7 = 4.803557845; estremi 8.601185948 e 10.202371897. Q con peso 0.8 = 9.882134707, arrotondato a 10; con SS=1 il fabbisogno illustrato è 11. | Conservare i conti; chiarire che sono scenari sotto assunzioni. |
| §5.1, `D = sales + reported unmet` | «Realized demand» è troppo forte: richieste incomplete, vague o duplicate; finestre delle note e delle vendite possono differire. Il dato odierno certificato non esiste ancora. | Chiamare proxy/scenario; allineare periodo, granularità e disponibilità. Se impossibile, niente rapporto numerico. |
| §5.1, prior `alpha = F` | Se F=0, denominatore nullo. Con F>0, `r=(D/F+1)/2`: dà sempre metà peso al rapporto osservato, non una shrinkage progressivamente minore al crescere dei conteggi. | Caso cold-start separato; pseudo-esposizione fissa positiva oppure dichiarare esplicitamente il blending al 50%. |
| §5.1, somma degli uplift | Il clamp dei singoli ratio non limita la somma: più segnali negativi possono rendere `1+sum(u)<0`; duplicati o fattori correlati gonfiano l’aumento. | Fusione per caso/fatto, una correzione per informazione; vincolo finale di non negatività e cap di policy sul totale. |
| §5.1, `last_seen` | Forward e ripetizioni possono ringiovanire indefinitamente un segnale. | Separare ultima ricezione, nuova conferma indipendente e validità del fatto; dedup prima del decadimento. |
| §5.1, traffico | Se le vendite già ridotte producono ratio <1 e si moltiplica anche per 0.5, il danno viene contato due volte. Assumere vendite proporzionali al traffico ignora conversione e mix. | Separare opportunità di vendita locale e domanda/preferenza latente; usare il 50% come scenario di esposizione. |
| §5.1, «exclude from learning» | Escludere ogni disruption è una policy forte; in futuro si potrebbe imparare a prevederne l’effetto tramite covariate. | Annotare e mascherare nel fit semplice attuale, senza affermare che l’esclusione sia universalmente ottima. |
| §5.2, quantile uniforme | `low + CR*(high-low)` è il quantile di una **uniforme assunta**. Un range qualitativo non definisce una distribuzione; un intervallo all’80% non è il supporto completo di una uniforme. | Chiamare il peso «prudenza» e fare analisi di scenario; usare «service quantile» solo con una distribuzione giustificata. |
| §5.2, critical ratio e SS | CR è la soluzione newsvendor con specifici costi marginali e ipotesi; non prova ottimalità multi-periodo/con trasporti. Un SS aggiuntivo può contare due volte il buffer di rischio. | Separare costo sottoscorta, sovrascorta e trasporto; SS come vincolo di policy, con effetto visibile. CR non equivale al fill rate. |
| §5.2, «stock + arrivals − Q per day» | Q nel contratto è un totale su H: sottrarlo ogni giorno moltiplica il consumo per H. | Definire `q_h` o traiettorie di domanda e garantire che sommino al totale H. |
| §5.2, inbound entro H | Un arrivo il giorno H non soddisfa la domanda persa il giorno 1. Perdita attesa non si ottiene da una sola traiettoria di quantili. | Simulazione giornaliera, semantica lost sales/backorder, etichette per scenario. |
| §5.2, donatori e raccomandazione | La formula finale non prova fattibilità temporale; minimizzare sole unità perse ignora costo trasporto e danno agli altri negozi. | Controllare intera traiettoria, stock condiviso e costi; mostrare trade-off anche quando non monetizzabile. |
| §5.3, Gamma-Poisson | `Gamma(2,4)` → `Gamma(11,11)` dopo 9 osservazioni in 7 giorni è corretto **per conteggi Poisson completi**. Conteggi inventati da testo/censurati violano il modello. | Solo dimostrazione condizionata al modello; non presentare l’inviluppo dei posterior low/high come intervallo calibrato. |
| §5.3, distribuzione predittiva | Per un futuro totale di H giorni: NB con shape a', parametro p=b'/(b'+H), media H*a'/b'. Quantili di lambda e di domanda futura non sono intercambiabili. | Dichiarare parametrizzazione, orizzonte e likelihood; evitare una banda sulla sola intensità etichettata come domanda. |
| §3.2 M4/M5 | Candidate set ristretto esclude richieste fuori assortimento; dedup senza taglia/episodio può fondere eventi distinti. Stock ERP vecchio positivo non prova phantom inventory attuale. | Fallback catalogo, dedup per fatto/taglia/periodo; «possibile discrepanza» con timestamp e verifica fisica. |
| §1.1 e §7 | «Le note vedono tutto» e «il forecast non vede nulla di nuovo» sono generalizzazioni. «Mai rilevato» non è osservabile da un test finito. | Trattarle come ipotesi locali; riportare omissioni e «non rilevato entro la fine del replay». |
| §7.2, baseline sales-only | Tre giorni >1.5× forecast possono essere un comparatore arbitrariamente lento. Zero vendite non prova stockout, e stockout non rivela la sua domanda persa. | Aggiungere un comparatore robusto e uno operativo con stock, a pari budget di falsi alert; distinguere tipo di informazione. |

Un ulteriore limite: substring valida al 100% verifica la provenienza testuale, **non** la correttezza dell’interpretazione o del collegamento. Zero errori osservati su venti note non dimostra rischio zero in produzione.

## 7. Vertical slice raccomandata per 24 ore

**Percorso:** email multilingue rumorosa + tabella ERP + un report con definizione esplicita + contesto esterno disponibile → claim con prove → caso deduplicato → priorità e scadenza → interrogazione di stock/logistica → confronto di scenari → card di decisione 1–14 giorni.

1. **Intake ristretto ma eterogeneo.** Supportare davvero `.eml` e un formato strutturato CSV/XLSX. Per il report, conservare periodo, definizione, valuta/IVA e data di pubblicazione; se incompatibile, mostrare il conflitto senza fondere i numeri. Una fonte esterna serve come contesto versionato. Dichiarare eventuali adapter mocked.
2. **Estrazione e astensione.** LLM estrae span, tipo, periodo e attributi; codice valida. Collegamento con candidati e possibilità di domanda. Fonti ripetute non aumentano automaticamente la forza.
3. **Caso operativo.** Un episodio con stato, autore/fonte, fatti indipendenti, prima conoscibilità, stock da verificare, deadline. Separare domanda, impedimento operativo e qualità del dato.
4. **Baseline e scenari.** Forecast dato in ingresso, nessun retraining long-term. Diagnostica robusta se il passato è osservabile; assenza di dati produce astensione, non precisione fittizia.
5. **Agente investigatore.** Sceglie quale verifica è utile fra identità, stock, ETA e policy; tool deterministici restituiscono dati filtrati `as_of`. Massimo di chiamate, trace e fallback a flusso fisso. La domanda al negozio è simulata nella demo, nessuna comunicazione reale.
6. **Azioni.** Verifica/monitoraggio/hold hanno dignità di risultati. Trasferimento e DC compaiono solo dopo controlli; output draft sottoposto a decisione umana.

**Card minima:** cosa sappiamo; cosa è incerto; da quando lo sappiamo; baseline e ipotesi dei tre scenari; azioni ammesse; quantità/arrivo e unità perse per scenario; danno possibile al donatore; prossima verifica; termine utile; evidenze e timestamp. Evitare termini implementativi nell’esperienza del planner.

**Ordine di lavoro consigliato:** ore 0–3 contratti temporali e un flusso completo; 3–8 parsing/claim/linking; 8–12 casi e residui/scenari; 12–16 disponibilità/ETA e simulazione; 16–18 replay e ablation; 18–24 verifica, congelamento e demo. È un piano indicativo per il team, con attività in parallelo, non una promessa di completare tutti i moduli del design. Tagliare prima BOCPD, training SPO, conformal adattivo, cold start bayesiano e riconciliazione universale. Conservare ingestione eterogenea minima, astensione, disponibilità temporale, fattibilità e audit.

## 8. Protocollo temporale senza leakage

### Due date, più la scadenza operativa

Ogni fatto deve avere almeno **quando vale/è accaduto** (`event_time` o intervallo e `business_date`) e **quando il sistema poteva conoscerlo** (`available_at`, UTC). Per evitare equivoci, `decision_due_at` è una terza nozione: scadenza dell’azione, non pubblicazione del dato.

Campi aggiuntivi utili: `issued_at`, `received_at`, `version`, `supersedes`, `availability_basis`, `source_id`, `as_of`. Una previsione meteo per domani è ammissibile se emessa oggi: il target futuro non la rende leakage. Un report su settembre uscito il 6 ottobre non è ammissibile il 30 settembre.

Regola del replay: filtrare prima del retrieval e dei tool, non solo nella UI, per `available_at <= T`. Scegliere fra le versioni ammissibili la più recente. Una rettifica arrivata dopo T non cancella retroattivamente il dato che vedeva il decisore a T. Dati derivati hanno disponibilità almeno pari al massimo dei loro input e all’effettivo tempo di elaborazione. Un chiarimento simulato deve essere disponibile dopo la domanda, non recuperato dal futuro.

Applicazione alle fonti documentate nel README:

- Vendite, KPI, traffico e inventario: rispettare almeno il ritardo D−1 indicato; un posting più tardivo prevale. Per dati di fine giornata la data non basta a rappresentare un cutoff intraday.
- Email: data di ricezione se affidabile; nel dataset usare il proxy `Date:` prescritto dal README, conservando questa limitazione. Non usare mtime del filesystem come pubblicazione storica.
- Forecast: run/vintage già emesso, con ipotesi conservativa se manca l’ora. Mai applicare un run futuro a un’origine passata.
- Turismo e report: data di pubblicazione, non mese di riferimento. Per social/news distinguere pubblicazione e raccolta: se il sistema raccoglie dopo, non era disponibile prima.
- Sistemi/logistica: distinguere pianificato, previsto e realizzato. Un ETA noto allora è utilizzabile; l’actual arrival conosciuto dopo non è una feature retroattiva.
- Quando la disponibilità è ignota, escludere dal replay rigoroso oppure dichiarare una convenzione conservativa. Non retrodatare la fonte per completare la demo.

### Split, origini e confronti

Il protocollo seguente è una nostra applicazione al repository dei principi di R3/R12, non una procedura già eseguita.

1. Congelare gli store dev/hold-out del README. Lo split per negozio non basta: fissare anche finestre temporali di sviluppo, eventuale calibrazione e test. Nessuna consultazione delle risposte nascoste da parte di prompt, agenti o prodotto.
2. Congelare mapping dei quantificatori, soglie, prompt e costi prima del test. I casi nel README sono materiale di progettazione, non scoperta cieca. Aggiungere note indipendenti scritte senza conoscere eventi/piantature e dichiarare comunque il limite sintetico.
3. A ogni origine T calcolare solo feature conoscibili a T. Per training/calibrazione usare target di H giorni solo quando l’intero target e il relativo ritardo di certificazione sono maturati. Un gap fisso di 14 giorni non sostituisce questa verifica.
4. Valutare H=1, 3, 7, 14 separatamente; le ultime origini con target incompleto restano pending. Origini sovrapposte non sono repliche indipendenti: non produrre error bar i.i.d. aggregando tutte le righe.
5. Confrontare: forecast invariato + policy stock; numeri con detector robusto; numeri + note; numeri + note + contesto/report; pipeline con chiarimento. Mantenere identici disponibilità, vincoli e costi, salvo la fonte aggiunta. Il confronto con stock va chiamato baseline operativa, non sales-only.
6. Per il tempo di anticipo, confrontare detector sullo **stesso evento/obiettivo** e a carico di falsi alert comparabile sul dev. Riportare `t_baseline_detect - t_pipeline_detect` in tempo UTC e il tempo residuo per agire; separare conoscenza dell’esaurimento e quantificazione di domanda persa.
7. Se un evento non viene rilevato entro T_end, riportare «non rilevato entro T_end» e, se pertinente, un limite inferiore all’anticipo, senza assegnargli infinito o inserirlo come numero in una media.
8. Solo il valutatore separato M14 può confrontare output congelati con ground truth. Per stimare l’esito di una diversa azione serve una simulazione controfattuale coerente: non si possono cambiare trasferimenti e contemporaneamente riutilizzare come immutabili gli stock storici. Se manca il simulatore, limitarsi a fattibilità e ranking su scenari.

### Metriche che rispondono alla challenge

- **Lettura e linking:** precision/recall claim, validità span, errore fra link accettati, quota accettata, quota e latenza dei chiarimenti; conteggi e risultati per lingua/tipo di ambiguità.
- **Triage:** precisione dei primi K casi, eventi mancati, falsi alert per store-day, tempo umano necessario, quota di verifiche che cambiano la decisione.
- **Anticipo utile:** tempo di rilevazione e margine prima della deadline logistica; arrivare prima ma dopo il cutoff può non produrre beneficio.
- **Previsione:** WAPE `sum(abs(D-f))/sum(D)` sullo stesso target/unità, separato per scenario e orizzonte, solo con domanda disponibile al valutatore. Se il denominatore è zero, WAPE è indefinito: riportare MAE e quantità. Distinguere domanda realizzata e intensità media, e non selezionare post hoc il punto migliore dentro la banda.
- **Incertezza:** se gli intervalli sono davvero implementati, copertura e ampiezza per orizzonte e segmento, numerosità ed esiti esclusi. Per scenari: sensibilità della decisione, senza coverage nominale.
- **Decisioni:** vincoli violati, costo e unità perse in simulazione per destinatario **e donatore**, confronto con hold/baseline; eventuale regret rispetto a un oracle con gli stessi vincoli e informazioni future dichiarate come privilegio del solo valutatore.
- **No harm:** frequenza di azioni errate sui decoy, spostamenti inutili e costo incrementale. Forecast invariato da solo non dimostra assenza di danno.

**Claim sostenibile al pitch:** «Su replay sintetici con fonti disponibili al momento della decisione, colleghiamo evidenze eterogenee a casi prioritizzati e confrontiamo opzioni fattibili per i prossimi 1–14 giorni. Misuriamo anticipo utile, errori e astensioni; i range manuali restano scenari. Non abbiamo addestrato un nuovo forecast long-term né dimostrato un ROI reale». I risultati numerici vanno aggiunti soltanto dopo l’esecuzione del valutatore.
