---
source:
  - behance:runtime
  - dribbble:runtime-related
  - behance:cfo
  - behance:nexa
  - behance:nexa-frame01
generated_at: "2026-10-22"
coverage: "parziale: un frame NexaDash visibile; pubblicazione Dribbble collegata ad AI Runtime; nessun frame fintech verificato"
evidence_summary: "1 immagine Behance osservata, 1 palette e descrizione della pubblicazione Dribbble degli stessi autori, 2 schede Behance indicizzate, 1 progetto non verificabile"
---

# Overview

**Obiettivo:** un unico linguaggio visivo per una dashboard SaaS desktop ad alta densità informativa, riconoscibile per *dark UI neutra + ciano operativo + visualizzazione dati leggibile*. Il sistema qui definito si chiama **Signal Dark** (nome di lavoro). **È una sintesi implementativa parziale**, non un'estrazione fedele del CSS originale.

## Fonti ed effettiva copertura

| ID | Fonte | Cosa è stato effettivamente verificato | Stato |
|---|---|---|---|
| `behance:runtime` | [AI Runtime Security Dashboard](https://www.behance.net/gallery/256351679/AI-Runtime-Security-Dashboard) | Titolo, autori e descrizione tramite indicizzazione. Pagina diretta: HTTP 403. | **Nessun frame Behance ispezionato** |
| `dribbble:runtime-related` | [AI Runtime Security Dashboard, Yeasin Islam](https://dribbble.com/shots/27772302-AI-Runtime-Security-Dashboard) | Pagina accessibile degli stessi autori con titolo corrispondente; testo su UI dark, network graph e telemetry; palette esadecimale esposta dalla pagina. | **Testo/palette, non immagine sorgente Behance** |
| `behance:cfo` | [AI CFO Platform — Fintech SaaS Dashboard & Investor App UI](https://www.behance.net/gallery/257402813/AI-CFO-Platform-Fintech-SaaS-Dashboard-Investor-App-UI) | Il link diretto restituisce HTTP 403; non sono state recuperate immagini o una scheda indicizzata inequivocabile. | **Non analizzabile** |
| `behance:nexa` | [NexaDash — Cyber Security Admin Dashboard](https://www.behance.net/gallery/249341499/NexaDash-Cyber-Security-Admin-Dashboard) | Titolo/autori indicizzati. Pagina progetto diretta: HTTP 403. | **Parziale** |
| `behance:nexa-frame01` | [NexaDash, modulo immagine 1444161303](https://www.behance.net/gallery/249341499/NexaDash-Cyber-Security-Admin-Dashboard/modules/1444161303) | **Immagine effettiva consultata**: dashboard nel mockup laptop e testo di presentazione. | **Osservato, singolo frame** |

**Legenda:** `exact` = dato esposto dalla fonte; `observed` = visibile; `estimated` = approssimazione visiva; `inferred` = decisione normalizzata; `unknown` = non determinabile. Confidence: `high / medium / low`. Valori numerici contrassegnati `estimated`/`inferred` sono proposte per l'implementazione, **non quote di CSS misurato**.

## 1. Analisi singola dei riferimenti

| Aspetto | AI Runtime Security (Behance + pubblicazione collegata Dribbble) | AI CFO Platform | NexaDash, frame 01 |
|---|---|---|---|
| Palette | La pagina Dribbble elenca `#020202`, `#58181B`, `#3D5950`, `#6C7553`, `#174CB0`, `#CFCDC7` (`exact`, high, **solo per Dribbble**). La descrizione menziona bagliori ciano, magenta, lime, arancio; distribuzione cromatica nei frame Behance ignota. | **Sconosciuta** | Quasi nero/antracite dominante e ciano/turchese brillante su dati e selezioni (`observed`, high). Esadecimali originali sconosciuti. |
| Tipografia | Famiglia, pesi e dimensioni **sconosciuti**. | **Sconosciuta** | Sans geometrico/neutro all'apparenza, KPI più evidenti e micro-label secondarie (`observed`, medium); famiglia/font size esatti ignoti. |
| Spaziature | **Sconosciute** nel progetto Behance. | **Sconosciute** | Card ravvicinate, griglia densa ma con gutter regolari (`observed`, medium); px non misurabili come CSS. |
| Raggi / ombre | **Sconosciuti** | **Sconosciuti** | Pannelli scuri con angoli moderatamente arrotondati, contorni tenui, elevazione poco marcata (`observed`, medium). |
| Layout | Secondo la descrizione Dribbble: diagramma di nodi, telemetria in pannello destro e severity breakdown. Solo descrizione, non un frame ispezionato (`exact` testo, non `observed` visuale). | **Sconosciuto** | Sidebar sinistra e mosaico di KPI/grafici e tabelle compatte dentro un pannello laptop (`observed`, high). |
| Componenti | Dichiarati nella descrizione Dribbble: network graph e telemetria rischi. Stati interattivi non osservati. | **Sconosciuti** | Sidebar con icone+etichette, card KPI, grafici a barre/linee, matrice di punti, indicatori e barre, filtri/header (`observed`, medium-high). |
| Mood | «Dark high-tech monitoring» secondo descrizione della pubblicazione collegata; non certificato per tutti i frame Behance. | **Sconosciuto** | Scuro, tecnico, compatto, fortemente data-driven, accento luminoso disciplinato. |

Nota su NexaDash: nel frame sono visibili anche metriche di analisi generica (es. ordini/visite), non soltanto telemetria di cybersecurity. Non trattare il titolo del progetto come prova dei dati mostrati.

## 2. Confronto

**In comune, con supporto limitato:** AI Runtime nella descrizione correlata e NexaDash nel frame convergono sul tema *dark dashboard con dati operativi*. Entrambi associano visualizzazioni a segnali cromatici. È il solo denominatore visuale sufficientemente difendibile per la sintesi.

**Differenze:** AI Runtime valorizza, nella descrizione collegata, un **network graph multicolore**; NexaDash documenta visivamente un **layout a pannelli con ciano dominante**. Per AI CFO non si può stabilire alcuna affinità o divergenza visuale: il riferimento non è stato visto.

**Scelta di sintesi:** adottare l'impianto a pannelli NexaDash per la dashboard generale, con **un solo accento principale ciano**; riservare magenta/lime/arancio ai significati di stato e ad eventuali visualizzazioni specialistiche. Non mescolare tre palette primarie concorrenti.

# Colors

## Palette di sistema: Signal Dark

Le seguenti sono **scelte operative proposte** a partire dal frame NexaDash e dalla descrizione collegata AI Runtime, non colori CSS estratti. I token sono definiti in [`design-tokens.json`](../../src/design/tokens.json).

| Ruolo | Token | Hex proposto | Evidenza · confidenza |
|---|---|---|---|
| Canvas | `semantic.color.surface.canvas` | `#080D0E` | estimated · medium · NexaDash |
| Sidebar | `semantic.color.surface.sidebar` | `#020202` | inferred · medium · NexaDash / Dribbble; valore esatto solo nella palette Dribbble |
| Card | `semantic.color.surface.card` | `#0F181A` | estimated · medium · NexaDash |
| Hover/elevated | `semantic.color.surface.elevated` | `#162326` | estimated · low · NexaDash |
| Testo | `semantic.color.text.primary` | `#ECF7F7` | estimated · medium · NexaDash |
| Testo secondario | `semantic.color.text.secondary` | `#AEC4C6` | estimated · low · NexaDash |
| Bordo tenue | `semantic.color.border.subtle` | `#263537` | estimated · low · NexaDash |
| Azione principale | `semantic.color.action.primary` | `#21E1DF` | estimated · medium · NexaDash |
| Success | `semantic.color.state.success` | `#A4E77C` | inferred · low · descrizione Dribbble (lime) |
| Warning | `semantic.color.state.warning` | `#F4B15C` | inferred · low · descrizione Dribbble (arancio) |
| Danger | `semantic.color.state.danger` | `#FF8CA7` | inferred · low · descrizione Dribbble (magenta) |
| Info | `semantic.color.state.info` | `#85B8FF` | inferred · low · blu nella palette Dribbble, sfumatura progettuale |

**Regole:** usare il ciano per azioni, selezione e serie grafica principale; 1–2 colori secondari soltanto per confronto o semantica. Non usare rosso/verde per codificare stati senza label e icone. Sui fondi scuri, mantenere le card distinguibili anche quando il display rende male i neri.

# Typography

L'originale **non espone il nome del font**. Si consiglia lo stack nativo `system-ui, sans-serif` (`primitive.font.family.ui`, inferred · low) per replicare una gerarchia sans neutra senza attribuire una famiglia ai designer originali.

| Ruolo | Token dimensione | Peso consigliato | Interlinea CSS consigliata | Provenienza |
|---|---|---|---|---|
| Titolo pagina | `primitive.font.size.page` = 28px | 600 | 1.2 | inferred · low |
| Titolo sezione | `primitive.font.size.section` = 20px | 600 | 1.3 | inferred · low |
| Corpo | `primitive.font.size.body` = 16px | 400 | 1.5 | inferred · low |
| Testo UI / tabella | `primitive.font.size.body-sm` = 14px | 400/500 | 1.45 | inferred · low |
| Caption / meta | `primitive.font.size.caption` = 12px | 500 | 1.4 | inferred · low |

**Numeri:** usare `font-variant-numeric: tabular-nums` nei KPI e nelle tabelle. Tracking: normale, salvo label molto piccole dove valutare `0.02em` come scelta progettuale. Evitare dimensioni inferiori a 12px. Nessuna famiglia, interlinea o spaziatura tra caratteri è stata misurata nella fonte.

# Layout

**Osservato:** nel frame NexaDash esiste una navigazione verticale a sinistra e uno spazio di lavoro a schede scure compatte con grafici di formati diversi; forte allineamento per righe/colonne. Non è stato possibile osservare altri viewport.

**Specifiche operative proposte (`inferred`, low; non misure dei frame):**

- App shell con sidebar persistente su schermi ampi, header delle azioni e `main` indipendente.
- Griglia desktop a **12 colonne fluide**, gutter da `semantic.space.page-gap` (24px), card a larghezze 3/4/6/8/12 colonne, con 20px di padding (`semantic.space.card-padding`).
- Ritmo 4/8/12/16/24/32/40px (`primitive.space.*`); sezioni separate da `semantic.space.section-gap` (32px).
- Gerarchia consigliata: titolo e filtri → metriche KPI → trend/comparazioni → tabelle/dettaglio.
- La sidebar resta ancorata mentre il contenuto è scrollabile; nei contesti stretti la sidebar diventa pannello apribile e le card si impilano. **I breakpoint numerici non sono ricavati dalle referenze**; determinarli mediante test del contenuto.
- Grafici con legenda, etichette e una tabella/summary testuale alternativa quando necessario.

# Elevation and Depth

**Osservato NexaDash (`observed`, medium):** separazione più affidata a tono superficie, bordi discreti e spazio che a ombre drammatiche; il mockup introduce un'illuminazione scenografica ma **non** va replicata come shadow CSS delle card.

**Decisione:** usare `semantic.color.surface.card` e `semantic.color.border.subtle`; eventuale shadow CSS solo se la sovrapposizione di popover/dialog lo richiede dopo un test. **Shadow originali, blur e opacità non verificabili; nessun token di ombra emesso.**

# Shapes

- Card: `semantic.radius.card` → 12px, `inferred`, low.
- Input, tab, button: `semantic.radius.control` → 8px, `inferred`, low.
- Micro-elementi (pill, progress indicator) possono essere arrotondati completamente in CSS quando il significato lo richiede; lo screenshot non consente di dedurre una scala originale.
- Iconografia regolare, elementi compatti e angoli morbidi; evitare eccesso di pill e superfici glassmorphism vistose.

# Components

Inventario e anatomia: [`COMPONENTS.md`](COMPONENTS.md).

Priorità di implementazione: `AppShell`, `SidebarNav`, `PageHeader`, `KpiCard`, `ChartCard`, `StatusBadge`, `DataTable`, `FilterControl`, `EmptyState`, `LoadingState`, `ErrorState`. I primi componenti hanno una corrispondenza visiva NexaDash; gli ultimi tre sono **aggiunte necessarie per un prodotto**, non stati visti. `NetworkGraph` è un'opzione specialistica giustificata **solo dalla descrizione** Dribbble, non da uno screenshot ispezionato.

# Do's and Don'ts

| Fare | Non fare |
|---|---|
| Trattare il ciano come unica firma visiva primaria. | Assegnare magenta/lime/arancio casualmente a ogni card. |
| Rendere la dashboard scansionabile in 3 livelli: KPI, andamento, dettaglio. | Dare a ogni visualizzazione la stessa enfasi. |
| Usare linee/bordi tenui per separare card. | Applicare glow ed ombre pesanti a tutte le superfici. |
| Usare testo, simbolo e colore per gli stati. | Affidare la severity al solo colore. |
| Collegare ogni valore di implementazione ai token. | Presentare proposte di spacing o font come misurazioni originali. |
| Sostituire i mockup con componenti realmente usabili. | Copiare logo, copy, composizione esatta o immagini di proprietari terzi. |

# Motion and Interaction

Le fonti disponibili sono statiche o testuali: **hover, focus, pressed, disabled, loading, animazioni, easing e durate non osservati** (`unknown`). Nessun token motion è emesso.

**Linee guida di prodotto, non estrazione:** tab e filtri accessibili da tastiera, tooltip anche tramite focus, focus ring con `semantic.color.action.focus`, transizioni ridotte e non indispensabili; disattivare le animazioni decorative con `prefers-reduced-motion: reduce`. Non animare i dati live in modo distraente.

# Imagery and Icons

**NexaDash frame (`observed`, medium):** icone piccole in sidebar e nei pannelli, visualizzazioni numeriche, grafici a barre/linee, matrice di punti e device distribution. Non è possibile identificare l'icon set originale.

**AI Runtime pagina Dribbble (`exact` come testo):** descrive un network graph con nodi e glows leggeri, categorie Users/Datasets/Models/Plug-ins/Internet. Nessun pixel originale del progetto Behance ispezionato.

**Scelta:** un unico set di icone lineari, dimensione ottica coerente; chart SVG/canvas responsivi con tooltip, legenda e fallback testuale. Niente fotografie/illustrazioni decorative nei pannelli di dati. Non riutilizzare illustrazioni o artwork proprietari.

# Accessibility

Non è stato possibile verificare WCAG sul prodotto originale: sono stati visti un frame statico e metadati. In particolare non sono stati verificati focus, zoom, tastiera o contrasto del progetto Behance.

**Criteri di implementazione da validare:** contrasto testo normale ≥ 4.5:1 e testo grande ≥ 3:1, focus indicator chiaramente distinto, hit area dei controlli preferibilmente ≥ 44×44 CSS px quando lo spazio lo consente, label accessibili per icon-only, `aria-current` sulla voce attiva, `th` nelle tabelle, grafici con alternativa testuale, stati loading/error annunciati appropriatamente. I colori proposti richiedono verifica nelle effettive combinazioni foreground/background: non equivalgono a un audit automatico.

# Voice and Content

Tono: concreto, tecnico, orientato alla lettura dei dati. Microcopy breve, etichette semanticamente precise («Attività», «Stato», «Periodo», «Eventi», «Esporta»). Usare unità di misura, periodo, delta e provenienza dei KPI; non introdurre dati artificiali spacciandoli per reali. Evitare termini come «AI-powered» ripetuti sulle singole card. La voce è una **scelta proposta**, non derivazione di un copy audit completo.

# Evidence, Conflicts, and Unknowns

## Registro di evidenza

| Segnale | Fonte | Classificazione | Confidenza | Decisione |
|---|---|---|---|---|
| Superfici quasi nere | `behance:nexa-frame01` | observed | high | Adottare dark-first |
| Accento ciano nelle chart | `behance:nexa-frame01` | observed | high | Usare `action.primary` ciano |
| Griglia con sidebar e card | `behance:nexa-frame01` | observed | high | Basare la shell sulla griglia |
| KPI e grafici differenziati | `behance:nexa-frame01` | observed | medium | KPI + ChartCard |
| Palette Dribbble `#020202` ecc. | `dribbble:runtime-related` | exact (pagina Dribbble) | high per quella pagina | Usare `#020202` solo come primitiva di riferimento |
| Network graph e quattro colori glow | `dribbble:runtime-related` | exact (descrizione), non observed (visivo) | medium per contenuto | Documentare componente opzionale |
| Font, radii, gap, colori CSS esatti | Fonti disponibili | unknown | — | Valori proposti, non estratti |
| Hover, focus, motion, responsive | Fonti disponibili | unknown | — | Implementare e testare ex novo |
| Aspetto AI CFO | `behance:cfo` | unknown | — | **Escluso dal confronto visuale** |

**Conflitti/limiti importanti:**

1. La pubblicazione Dribbble con lo stesso titolo e un autore comune al progetto Behance è **correlata**, ma non prova identità di ogni frame o variante.
2. I colori hex elencati su Dribbble sono dati esatti della **palette mostrata da Dribbble**, non del CSS Behance; non vanno imposti letteralmente a NexaDash.
3. Il mockup NexaDash è un'immagine composita: dimensioni apparenti nel laptop e illuminazione non sono misure in CSS.
4. Il progetto AI CFO è non verificabile. **Nessuna scelta qui è attribuita a quel progetto.**
5. Non sono stati analizzati mobile, tablet reali, schermate multiple e varianti di stato. La sintesi potrà cambiare se saranno caricati screenshot aggiuntivi.

**Per completare l'estrazione fedele:** acquisire screenshot a risoluzione nativa di tutte le schermate dei tre progetti e possibilmente un design file/token originale; misurare valori tramite campionamento e ripetere la verifica di accessibilità.

La guida per l'implementazione è [`IMPLEMENTATION_PROMPT.md`](IMPLEMENTATION_PROMPT.md).
