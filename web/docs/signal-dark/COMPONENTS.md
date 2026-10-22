# Components — Signal Dark

## Copertura

**Frame visivamente osservato:** [NexaDash, modulo 1444161303](https://www.behance.net/gallery/249341499/NexaDash-Cyber-Security-Admin-Dashboard/modules/1444161303). **Descrizione testuale correlata:** [AI Runtime Security Dashboard, Dribbble](https://dribbble.com/shots/27772302-AI-Runtime-Security-Dashboard). **Non accessibile:** [AI CFO](https://www.behance.net/gallery/257402813/AI-CFO-Platform-Fintech-SaaS-Dashboard-Investor-App-UI). L'accesso diretto alle tre gallery Behance ha restituito HTTP 403; un singolo modulo immagine NexaDash è stato comunque recuperato. Nessun comportamento dinamico è stato verificato.

| Source ID | Tipo | Uso consentito |
|---|---|---|
| `behance:runtime` | Behance, pagina non apribile; metadati indicizzati | Intento e titolarità, non CSS/visuale |
| `dribbble:runtime-related` | Pubblicazione dello stesso autore/titolo | Descrizione del network graph e palette esposta dalla pagina |
| `behance:cfo` | Link non apribile; nessuna immagine verificata | Nessuna deduzione visuale |
| `behance:nexa` | Gallery non apribile; metadati indicizzati | Identità progetto |
| `behance:nexa-frame01` | Immagine Behance effettivamente visibile | Struttura, tono colore, componenti visibili |

**Convenzione:** ogni API, variante e dimensione proposta ma non osservata è segnata `proposta` e non va attribuita agli autori. I nomi token si riferiscono a [`design-tokens.json`](../../src/design/tokens.json). Il criterio di sintesi è definito in [`DESIGN.md`](DESIGN.md).

## AppShell

- **Scopo:** garantire continuità di sidebar, header e contenuto.
- **Evidenza:** `observed` · high · `behance:nexa-frame01`.
- **Anatomia:** sidebar sinistra con voci, barra azioni/identità in alto, area dashboard con card.
- **Varianti:** nessuna variante originale verificata; proporre desktop persistente e drawer su schermi stretti.
- **Dimensioni:** nessuna larghezza originale verificata. Il layout a 12 colonne e gap da `semantic.space.page-gap` sono proposte.
- **Stati:** scroll e drawer non osservati; implementare apertura/chiusura e gestione focus.
- **Token:** `semantic.color.surface.canvas`, `semantic.color.surface.sidebar`, `semantic.space.page-gap`.
- **Responsive:** scegliere il punto di passaggio quando navigazione e tabelle non entrano più: **nessun breakpoint di fonte**.
- **Accessibilità:** landmark `nav` e `main`, intestazione gerarchica, skip link.

## SidebarNav

- **Scopo:** navigazione persistente tra viste.
- **Evidenza:** `observed` · high · `behance:nexa-frame01`.
- **Anatomia:** intestazione/brand, gruppi di voci, icona, testo e selezione attiva; alcune voci mostrano un chevron.
- **Varianti:** attiva vs neutra; non è verificata l'apertura dei gruppi.
- **Dimensioni:** densità compatta visibile, px originali ignoti.
- **Stati:** default e selezione distinguibili (`observed`, medium). Hover/focus/expanded (`unknown`).
- **Token:** `semantic.color.text.secondary`, `semantic.color.action.primary`, `semantic.color.surface.sidebar`, `semantic.radius.control`.
- **Responsive:** drawer proposto su spazi stretti, non dedotto dal frame.
- **Accessibilità:** `aria-current="page"`, labels delle icone, disclosure con `aria-expanded` se applicabile.
- **Implementazione:** usare l'accento ciano **su una sola voce attiva**, non su ogni icona.

## PageHeader / FilterBar

- **Scopo:** titolare la pagina e fornire ricerca, filtro periodo e azioni globali.
- **Evidenza:** `observed` · medium · `behance:nexa-frame01` (barra superiore compatta con affordance).
- **Anatomia:** titolo, possibile sottotitolo, campo di ricerca e azioni a icona/utente. I dettagli testuali del mockup non sono completi.
- **Varianti:** `PageHeader` normale e compatta = proposta; nessun set ufficiale verificato.
- **Dimensioni:** input con `semantic.radius.control`, scala `primitive.font.size.body-sm`.
- **Stati:** focus, disabled, clear, menu aperto non osservati.
- **Token:** `semantic.color.surface.canvas`, `semantic.color.text.primary`, `semantic.color.border.subtle`.
- **Responsive:** avvolgere i filtri su più righe prima di ridurre il testo.
- **Accessibilità:** `label` persistente, nome dei pulsanti icon-only, ordine tab logico.

## KpiCard

- **Scopo:** visione rapida della metrica, trend, confronto temporale.
- **Evidenza:** `observed` · high · `behance:nexa-frame01`.
- **Anatomia:** titolo breve, valore prominente, etichetta/cambio periodo e opzionale sparkline.
- **Varianti:** con/ senza sparkline (`proposta` basata su più card simili), non specifica originale.
- **Dimensioni:** padding proposto `semantic.space.card-padding` = 20px; altezza determinata dal contenuto.
- **Stati:** default osservato; skeleton, errore e hover non osservati.
- **Token:** `semantic.color.surface.card`, `semantic.color.text.primary`, `semantic.color.text.secondary`, `semantic.radius.card`, `semantic.color.border.subtle`.
- **Responsive:** scorrimento logico e ricomposizione; non tagliare valore o unità.
- **Accessibilità:** valore letto insieme a nome, unità e intervallo; cifre tabulari.
- **Implementazione:** non usare trend color-only; accompagnare con icona/delta testuale.

## ChartCard

- **Scopo:** confronto e andamento nel tempo.
- **Evidenza:** `observed` · high · `behance:nexa-frame01`.
- **Anatomia:** titolo, azioni e/o legenda, regione grafico (barre, linee, punti, distribuzione per dispositivo); alcuni grafici presentano i colori ciano e tonalità tenui.
- **Varianti:** `line`, `bar`, `dot-matrix`, `distribution` rappresentano **forme viste nel frame**, non un'API ufficiale.
- **Dimensioni:** area grafico fluida, padding proposto 20px.
- **Stati:** hover tooltip, zoom, selezione e filtraggio **non osservati**.
- **Token:** `semantic.color.surface.card`, `semantic.color.action.primary`, `semantic.color.text.secondary`, `semantic.radius.card`.
- **Responsive:** preservare leggibilità assi, passare a scrolling orizzontale/aggregazioni ove necessario.
- **Accessibilità:** etichette in testo, `figure`/`figcaption`, descrizione sintetica dei trend e dati tabellari alternativi quando necessari.
- **Implementazione:** evitare di dare a tutte le serie lo stesso ciano. Colori semantici per anomalie, altra forma di differenziazione per serie multiple.

## StatProgress / MiniBar

- **Scopo:** graduatorie, confronti percentuali e segnali di avanzamento.
- **Evidenza:** `observed` · medium · `behance:nexa-frame01` (barre e piccoli indicatori).
- **Anatomia:** label, valore, track, fill colorato.
- **Varianti:** compatta e standard = proposta.
- **Dimensioni:** non verificabili; usare scala spaziatura esistente.
- **Stati:** statico osservato; indeterminate/animated non osservati.
- **Token:** `semantic.color.action.primary`, `semantic.color.surface.elevated`, `semantic.color.text.secondary`.
- **Responsive:** valore sempre leggibile fuori dalla barra.
- **Accessibilità:** `progressbar` soltanto per vero avanzamento, altrimenti testo/grafico con aria label; mai percentuali senza numeri.

## DataTable

- **Scopo:** accesso ai dettagli ordinabili/filtrabili dei dati.
- **Evidenza:** `observed` · low-to-medium · `behance:nexa-frame01` (righe/testo denso nell'interfaccia; colonnato completo non leggibile). **La presenza di una tabella interattiva non è verificata.**
- **Anatomia proposta:** intestazioni, righe, cella numerica, stato, azioni riga.
- **Varianti:** plain e dense = proposta.
- **Dimensioni:** `primitive.font.size.body-sm`, separatori `semantic.color.border.subtle`.
- **Stati:** sort/filter, bulk selection, pagination, empty, loading non osservati.
- **Token:** `semantic.color.surface.card`, `semantic.color.text.primary`, `semantic.color.text.muted`, `semantic.color.border.subtle`.
- **Responsive:** overflow orizzontale dichiarato o row detail, evitare troncamenti senza accesso al valore.
- **Accessibilità:** tabella HTML semantica, intestazioni `scope="col"`, ordinamento con `aria-sort`, focus per azioni riga.

## StatusBadge

- **Scopo:** differenziare stato, rischio o gravità.
- **Evidenza:** `inferred` · low · `dribbble:runtime-related` (testo sulla severity e glows) e `behance:nexa-frame01` (accenti sui dati).
- **Anatomia proposta:** puntino/icona + label testuale + eventuale numero.
- **Varianti proposte:** success, warning, danger, info.
- **Dimensioni:** usarle compatte senza micro-testo illeggibile; CSS da testare, non da copiare.
- **Stati:** nessuna interazione osservata; trattare come testo, salvo filtro esplicito.
- **Token:** `semantic.color.state.success`, `.warning`, `.danger`, `.info`.
- **Responsive:** etichetta sempre visibile oppure accessibile tramite nome completo.
- **Accessibilità:** ogni colore ha anche testo o icona distinta.

## NetworkGraph (opzionale, non osservato visivamente)

- **Scopo:** rappresentare relazioni fra entità AI / utenti / modelli e i loro stati.
- **Evidenza:** `exact` **solo come descrizione scritta** · medium · `dribbble:runtime-related`. Non è stato ispezionato il frame originale.
- **Anatomia dichiarata:** nodi, collegamenti e cluster Users / Datasets / Models / Plug-ins / Internet; descrizione di glow ciano/magenta/lime/arancione.
- **Varianti:** non note. Qualsiasi API è **proposta**.
- **Stati:** l'autore definisce la mappa «interactive», ma gesture, zoom/pan e focus **non verificati**.
- **Token:** `semantic.color.surface.card`, `semantic.color.action.primary`, `semantic.color.state.*`.
- **Responsive:** in contesti stretti favorire lista gerarchica delle entità, non ridurre indiscriminatamente il canvas.
- **Accessibilità:** alternativa ad albero/tabella navigabile da tastiera, descrizione delle relazioni, nodi con nome e stato.
- **Implementazione:** non introdurre questo componente nella dashboard base finché i dati di relazione non ne giustificano l'uso.

## Button / Input (primitivi di prodotto)

- **Scopo:** azioni e filtri implementabili nel nuovo prodotto.
- **Evidenza:** `inferred` · low · `behance:nexa-frame01`; anatomie originali non osservabili con sufficiente precisione.
- **Anatomia proposta:** label, icona opzionale, superficie/bordo, focus ring.
- **Varianti proposte:** primary ciano (testo scuro) e secondary scura; input con label e hint.
- **Dimensioni:** token `semantic.radius.control`, `primitive.space.2/3/4`; altezze da testare.
- **Stati:** default/hover/focus/active/disabled/loading devono essere creati; **nessuno verificato**.
- **Token:** `semantic.color.action.primary`, `semantic.color.action.secondary`, `semantic.color.text.on-accent`, `semantic.color.action.focus`.
- **Responsive:** controllo adattato allo spazio, label non persa.
- **Accessibilità:** semantica `button`/`input` nativa, focus evidente, target adeguato, gestione di errore testuale.

## Unobserved and uncertain behavior

**Non osservati:** interazioni realmente funzionanti, breakpoint, responsive in altri viewport, dark/light toggle, hover, focus, loading, empty, error, skeleton, dialog, modali, menu espansi, paginazione, esportazioni, audio e motion. Costruire questi stati da requisiti UX, senza attribuirli ai designer dei riferimenti. Per completare le misure servono screenshot non deformati e a risoluzione nativa, o sorgenti Figma/CSS.
