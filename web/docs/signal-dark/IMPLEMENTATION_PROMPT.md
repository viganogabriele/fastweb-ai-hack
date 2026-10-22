# IMPLEMENTATION_PROMPT — Signal Dark

Sei un frontend engineer senior. Costruisci **una dashboard SaaS generica di monitoraggio/analytics** usando il design system Signal Dark descritto in questi file:

- [`DESIGN.md`](DESIGN.md): principi, analisi, limiti e regole di composizione.
- [`design-tokens.json`](../../src/design/tokens.json): **fonte di verità dei valori**. Converti i DTCG token in CSS custom properties o variabili del tuo framework, risolvendo gli alias.
- [`COMPONENTS.md`](COMPONENTS.md): componenti, anatomia, evidenza e stati da realizzare.

Non stai copiando un prodotto originale, ma implementando **una sintesi coerente e dichiaratamente parziale** di riferimenti visuali.

## Orchestrazione con subagent Codex Sol 6.1

Spawna subagent per eseguire il lavoro in parallelo. **Ogni subagent deve usare Codex Sol 6.1 (model ID: `gpt-6.1-sol`)**, comprese eventuali deleghe successive. Specifica il modello nella chiamata al tool, non soltanto nel testo dell'incarico.

- In T3 Code, consulta `orchestrator_capabilities` per individuare l'istanza provider Codex e verificare la disponibilità di `gpt-6.1-sol`. Usa `delegate_task` con `target.providerInstanceId` e `target.model: "gpt-6.1-sol"`; se il modello eredita opzioni runtime, applicale in `target.options`. Conserva ogni `taskId` per seguirne lo stato e raccogliere i risultati.
- Fuori da T3 Code, usa il tool nativo per i subagent impostando esplicitamente `model: "gpt-6.1-sol"`, se supportato. Se il modello richiesto non è disponibile, segnala il limite senza sostituirlo silenziosamente.
- Crea task figli della conversazione corrente; non aprire conversazioni top-level per simulare subagent.
- Prima di delegare, leggi le istruzioni del repository e i tre file del design system, definisci contratti condivisi e assegna percorsi di proprietà distinti. Trasmetti a ogni subagent obiettivo, file consentiti, dipendenze, criteri di accettazione e vincolo sul modello.

Ripartizione consigliata, entro i limiti di concorrenza disponibili:

1. **Token e componenti base**: conversione DTCG, tema, `Button`, `Input`, `StatusBadge` e stati accessibili.
2. **Shell e navigazione**: `AppShell`, `SidebarNav`, `PageHeader`, responsive e drawer, usando il contratto dei token e dei componenti condivisi.
3. **Dati e widget**: dati demo coerenti, `FilterBar`, `KpiCard`, `ChartCard` e `DataTable`, usando gli stessi contratti.

L'agente principale coordina dipendenze e integrazione, risolve eventuali conflitti e verifica il risultato completo. Avvia i task dipendenti quando i contratti necessari sono definiti. Dopo l'integrazione, delega una revisione di accessibilità, responsive e criteri di accettazione a un subagent **sempre `gpt-6.1-sol`**, quindi correggi i problemi rilevati prima della consegna.

## Riferimenti e grado di prova

| ID | Link | Cosa puoi dedurre |
|---|---|---|
| `behance:runtime` | https://www.behance.net/gallery/256351679/AI-Runtime-Security-Dashboard | La pagina Behance restituisce HTTP 403; solo metadati indicizzati. |
| `dribbble:runtime-related` | https://dribbble.com/shots/27772302-AI-Runtime-Security-Dashboard | Pubblicazione degli stessi autori/titolo: descrive network graph, severity e un'interfaccia dark; mostra una palette esplicita nella pagina. **Non provare a replicare frame Behance non visibili**. |
| `behance:cfo` | https://www.behance.net/gallery/257402813/AI-CFO-Platform-Fintech-SaaS-Dashboard-Investor-App-UI | **Nessuna immagine verificata**. Non attribuire scelte visuali a questo progetto. |
| `behance:nexa` | https://www.behance.net/gallery/249341499/NexaDash-Cyber-Security-Admin-Dashboard | La gallery diretta restituisce HTTP 403. |
| `behance:nexa-frame01` | https://www.behance.net/gallery/249341499/NexaDash-Cyber-Security-Admin-Dashboard/modules/1444161303 | **Il solo frame Behance visivamente ispezionato**. Principale riferimento per composizione e proporzioni relative. |

## Target da implementare

Dashboard web **dark-first**, data-dense ma leggibile, responsiva, accessibile, con sidebar sinistra e area card. L'intento è una UI SaaS di monitoraggio/analytics, non necessariamente una dashboard cybersecurity. **Non ricreare grafiche, marchi, loghi, copy o fotografie proprietarie**; usa nomi e dati demo etichettati.

Priorità della pagina:

1. `AppShell` con sidebar, titolo e azioni in header.
2. Riga KPI di 3–4 card; valori, periodo, delta, eventuali sparkline.
3. Griglia di ChartCard con andamento temporale, distribuzione e confronto a barre.
4. Sezione di dettaglio con tabella o elenco ordinabile, stato e filtri.
5. Stati empty, loading, error e selezione, separati dai dati simulati.
6. Il `NetworkGraph` è **opzionale** e solo se il dominio dati presenta relazioni pertinenti.

## Linguaggio visivo

- Canvas quasi nero, sidebar leggermente distinta, card antracite separate da bordi tenui.
- Un solo accento principale ciano (`semantic.color.action.primary`) per selezioni, serie primaria e CTA.
- Colori success/warning/danger/info solo come semantica o serie secondarie con legenda.
- Gerarchia tipografica sobria con numeri più evidenti e testo descrittivo ridotto.
- Raggi moderati: `semantic.radius.card` e `semantic.radius.control`; non applicare glow e ombre profonde sistematicamente.
- Usa le dimensioni **proposte** (`semantic.space.*`, `primitive.space.*`, `primitive.font.size.*`) invece di inventare valori ad hoc.
- Famiglia font non identificata: usa `primitive.font.family.ui` come scelta implementativa. Non dichiararla come font originale.
- Nessuna shadow o motion originale verificata. Aggiungi solo ciò che migliora un uso reale e documenta la deviazione.

## Componenti e stati

Usa e riutilizza i componenti di `COMPONENTS.md`. Prevedi API consistenti per:
`AppShell`, `SidebarNav`, `PageHeader`, `FilterBar`, `KpiCard`, `ChartCard`, `StatusBadge`, `DataTable`, `Button`, `Input`.

Ogni componente interattivo deve avere stato `default`, `hover`, `focus-visible`, `disabled` e, se applicabile, `pressed`, `loading`, `error`, `empty`. **Questi stati non sono visibili nelle fonti e vanno progettati ex novo**, non imitati immaginariamente.

Dati reali o mock etichettati; evitare numeri privi di unità e periodo. I grafici devono presentare labels, legenda, tooltip accessibili e almeno un riepilogo testuale dei trend.

## Responsive

Nessun breakpoint originale è visibile. Non impostare numeri dichiarandoli fedeli alla reference.

- Wide: sidebar persistente, card in griglia multicolonna e chart affiancati.
- Narrow: sidebar a drawer accessibile; griglia progressivamente in una colonna, controlli a capo, grafici che riducono la densità senza troncare contenuti.
- Per tabelle larghe usa scrolling intenzionale o pattern detail row con intestazioni preservate.
- Scegli i breakpoint eseguendo test pratici della composizione, e annotali come decisione di implementazione.

## Accessibilità, feedback e motion

- HTML semantico (`header`, `nav`, `main`, heading, `button`, `table`, label form).
- `aria-current` sulla pagina corrente; annuncia errori e loading pertinenti.
- Testa i contrasti delle **combinazioni finali**, con riferimento a WCAG AA (4.5:1 testo normale, 3:1 testo grande).
- Focus ring chiaramente visibile, navigazione a tastiera completa, nome accessibile per icon-only, stato non comunicato col solo colore.
- `prefers-reduced-motion: reduce`, transizioni essenziali e senza animazioni decorative compulsive.
- Rispetta localizzazione delle unità e formattazione tabellare dei numeri.

## Contenuto, grafici e immagini

Usa etichette brevi in italiano, periodi espliciti, unità e chiara gerarchia: **KPI → Trend → Dettaglio**. Renderizza grafici nativi/Viz library con alta leggibilità sulle superfici scure; evita immagini statiche dei grafici per la UI funzionante. Non importare le immagini originali Behance o Dribbble nella UI finale.

## Gestione dell'incertezza

1. Tutto ciò che è `estimated` e `inferred` in `design-tokens.json` è una **proposta**, non un dato originale. Non asserire «pixel-perfect».
2. Non inventare font, stati, breakpoint, CSS o palette del progetto AI CFO.
3. Se scegli un parametro non documentato (es. transizione, sidebar width, comportamento del tooltip), annotalo in un breve file di scelte implementative come decisione locale.
4. Se vengono forniti screenshot migliori in seguito, aggiorna prima i token e poi componenti e layout; non aggiungere override scollegati.
5. Tratta il titolo «cybersecurity» di NexaDash come contesto, senza forzare dati non mostrati.

## Acceptance criteria

- [ ] Tutti i valori cromatici, raggi e spacing condivisi provengono dai token DTCG convertiti; nessun hard-code ripetuto.
- [ ] La struttura richiamata da `behance:nexa-frame01` è riconoscibile **nel rapporto tra sidebar, card, grafici e gerarchia**, non come copia di artwork.
- [ ] Sidebar, filtri, widget, tabelle e feedback sono funzionanti o chiaramente indicati come demo.
- [ ] Nessun componente esce dalla viewport nei layout testati e non ci sono etichette illeggibili.
- [ ] Contrast checks per coppie reali; navigation test da tastiera, `focus-visible`, reduced motion.
- [ ] KPI e grafici mantengono valori e unità coerenti; niente serie indistinguibili solo dal colore.
- [ ] Gli stati non osservati sono implementati come scelte di prodotto, non descritti come fatti del design originale.
- [ ] Confronto visivo manuale con **l'unico frame NexaDash realmente disponibile**; nessuna promessa di corrispondenza totale con le 3 gallery.
- [ ] Documentare le deviazioni necessarie per responsive, accessibilità e funzionalità.

**Output atteso:** codice componentizzato e documentato, pronta sostituzione dei dati demo, nessuna dipendenza da asset proprietari. Prima di consegnare, effettua controlli manuali su desktop e viewport ridotto e segnala i limiti residui.
