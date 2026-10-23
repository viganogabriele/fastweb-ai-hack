# Demo walkthrough UI (#129)

Goal: a reviewer watches a timed 4-minute walkthrough whose every screen is the real UI on a
frozen, offline replay, and whose claims match what the system actually did (#129 "Outcome").
This file lists the click path, what each screen must show, the gaps, and polish worth doing.
Priority: **Must**. Overview and honesty rules: [README.md](README.md).

## 1. Run the real UI offline

Use the committed recorded candidate; no keys, no network (`scripts/core_demo.md:39-63`).

```sh
make setup
demo_assets="$PWD/data/fixtures/runs/core-dev-20261022"
demo_candidate="$PWD/data/core_demo/ui-candidate"        # must not exist yet
backend/.venv/bin/python scripts/prepare_core_demo.py --output "$demo_candidate" \
  --code-version f1d7923c788bdc519fcab5460dfe4ad1b9de8af0 \
  --case-id case-mil01-i10919b00011-20261008 --case-id case-mil01-unknown-20261009
backend/.venv/bin/python scripts/replay_demo.py --run-spec "$demo_assets/run-spec.json" \
  --sources "$demo_candidate/sources" --config "$demo_candidate/config" \
  --cache "$demo_assets/llm_cache" --systems-cache "$demo_assets/systems_cache" \
  --decisions "$demo_assets/decisions.json" --workspace "$PWD/data/core_demo/ui-replay"
demo_attempt=$(ls -d "$PWD"/data/core_demo/ui-replay/attempt-* | tail -1)

# terminal 1
LLM_MODE=replay DATA_DIR="$demo_attempt/data" SOURCES_DIR="$demo_attempt/inputs/sources" \
  CONFIG_DIR="$demo_attempt/inputs/config" \
  backend/.venv/bin/uvicorn tesseract.api.main:app --port 8106
# terminal 2
cd web && TESSERACT_API_TARGET=http://127.0.0.1:8106 npm run dev -- --port 5186
```

Open `http://localhost:5186/#/panoramica`. Expected: one run `core-dev-candidate`, `recorded`,
`degraded`, 41 cases, 13 documents, 4 stores (`scripts/core_demo.md:89-100`). Decisions you make
are written to that attempt's DB; re-run `replay_demo.py` for a clean attempt before rehearsing.

## 2. The click path (proposed, aligned with the recorded run)

The draft script (`docs/demo_script.md`) predates the recorded candidate. Three beats cannot be
shown honestly as written:
- the what-if panel (`docs/demo_script.md:68-80`): no UI or API for it exists;
- ROM01 (`docs/demo_script.md:72-86`): a hold-out store (`docs/RFC-001-piattaforma.md:542`);
- the live D5 reply (`docs/demo_script.md:90-100`): it depends on #135 plus a registered recording.

The pitch playbook already says to swap them (`pitch/src/04-tackling-bleeds.html:215-227`).
Proposed path (Lorenzo to confirm, README §5):

| Time | Screen and clicks | Must show | Today |
|---|---|---|---|
| 0:00–0:20 | **Panoramica**. Point at the disclosure strip, then "Apri il caso più urgente" or **Casi** | Cutoff Thu 2026-10-22 22:00 (with time zone), `recorded`, `degraded`, "dati sintetici", 41 open, 7 to verify | Counts OK. Disclosure strip missing (M1) |
| 0:20–0:50 | **Fonti**. Open the MIL01 email `20261009_1035`, hover the highlighted span | Canonical text, highlighted quote, case reference | Works on hover (`web/src/sections/RunWorkspace.tsx:274-289`). No click-through to the case |
| 0:50–1:50 | **Casi → D1** `case-mil01-i10919b00011-20261008` | Header: store, product, status, "2 documenti / 2 origini", 5 open uncertainties. Evidence as quotes linked to Fonti. Forecast: baseline only, overlay `unchanged` with reason "scope_style: the evidence names the style, not this colour" | All data present. Evidence is raw IDs (M2). Forecast is a 20-decimal table (M3) |
| 1:50–2:30 | Same case: **Traccia** | `recorded`, fallback **sì**, outcome `verify`. Steps: evidence, stock ×2, lanes ×2, options; the six-tool budget was reached (`scripts/core_demo.md:104-108`) | Shown, but buried below the forecast (M4) |
| 2:30–3:10 | Same case: **Opzioni**. Read `hold` (recommended) and `transfer` (all checks pass, **not recommended**: zero benefit). Approve `notify_owner` with reviewer name, confirm | Checks list. "Bozza locale simulata, nessun invio". Server-returned `dispatch_status: draft` | Works (`web/src/sections/CaseOptionsPanel.tsx`). No persisted state after reload (M5) |
| 3:10–3:40 | **Casi → filter "Con incertezze bloccanti" → `case-mil01-unknown-20261009`** | `verify`, "Prodotto da identificare", the drafted Italian clarification marked `Simulato: sì`, status `Bozza`, never "sent" | Works (`web/src/sections/CaseClarificationsPanel.tsx:49-65`) |
| (optional) | Answer the clarification (#135) or a live phone note (#191) | Only if merged **and** verified. Otherwise say the limitation aloud | Not available |
| 3:40–4:00 | Metrics slide (not the app) | Only approved #128 numbers, with denominators and "synthetic, dev stores" | See [holdout-results-ui.md](holdout-results-ui.md) |

Avoid MUN01 in the live queue: one event splits into 24 cases there
(`pitch/src/04-tackling-bleeds.html:224`).

## 3. Gaps to fix (acceptance criteria)

Each item is done when a human following §4 sees the stated result on the real replay.

- [ ] **M1 Disclosure strip** in the shell, on every route: run id, `as_of` with zone, `mode`
      badge (`live|recorded|fixture|unavailable`), run status (`degraded` in warning tone),
      namespace, and "Dati sintetici · azioni simulate". Data: `RunView` from `GET /api/runs`
      (`spec.mode`, `status`, `published`, `namespace`). Today only `mode` is a badge
      (`web/src/App.tsx:224-229`) and status is inside the select label (`web/src/App.tsx:218`).
- [ ] **Branding**: replace "Moncler" leftovers (`web/src/i18n/it/shell.ts:9,40`); apply the
      branding decision (README §5.1). Nothing public shows real brand assets without approval.
- [ ] **M2 Evidence**: for each `Case.supporting` / `contradicting` `Observation` ref, show the
      quote, document id, store, date and language. Source: `GET /api/runs/{run}/documents/{doc}?version=`
      returns `DocumentDetail.observations[].evidence` (`backend/tesseract/api/models.py:44-48`).
      "Apri nella fonte" navigates to Fonti with the document open and the span highlighted.
      Unresolvable refs say so, with no substitute version (existing pattern:
      `web/src/sections/CaseClarificationsPanel.tsx:61`).
- [ ] **M3 Forecast chart**: one small chart per SKU, baseline line with a low–high band. Values
      are rounded to 1 decimal and labelled "unità/giorno". The `status` and `reason` appear as
      a sentence ("Nessun aggiustamento: …"). The table moves behind "Mostra valori". No
      chart when `series` is empty or the baseline is unresolved
      (`web/src/sections/CaseForecastPanel.tsx:42-47`).
- [ ] **M4 Layout**: case detail order is summary → evidence → forecast → trace → options →
      clarifications. Use in-page anchors or tabs so the decision is reachable in ≤ 2
      scrolls at 1280×800. IDs, hashes and producer versions go under "Dettagli tecnici".
      The "Nessun esempio sintetico" badge and fixture block do not render in the product
      namespace (`web/src/sections/CaseDetailAnalysis.tsx:23-46`).
- [ ] **M5 Decisions after reload**: blocked on a read endpoint (none in
      `backend/tesseract/api/routers/options.py`). Until then, show a note: "Le decisioni
      salvate in sessioni precedenti non sono ancora leggibili da questa vista." Never derive
      "decided" locally.
- [ ] **Error detail** (S4): show the API `detail` and status. `readApi` drops both
      (`web/src/api/client.ts:18-21`).

## 4. Manual test script (browser, real replay)

1. Start §1. Open `/#/panoramica`. Check: strip shows `core-dev-candidate`, `recorded`,
   `degraded`, cutoff with zone, "dati sintetici". KPI "Casi aperti" = 41, "Da verificare" = 7.
2. Click **Fonti**, search `1035`, expand the MIL01 email. Check: at least one highlighted span.
   Hover shows the case id. Click "apri caso" (after M2): it opens that case.
3. Open `/#/casi/case-mil01-i10919b00011-20261008/v1`. Check within 2 scrolls: 5 open
   uncertainties, 3 supporting observations shown as **quotes**, forecast chart with values
   ≈1.4 and ≈1.6 units/day, overlay reason `scope_style…`.
4. Open the trace. Check: `recorded`, fallback **sì**, outcome `verify`, 6 steps (or the
   recorded count), no step text invented ("Testo del risultato: non presente…" stays honest,
   `web/src/sections/CaseTracePanel.tsx:69`).
5. On option `notify_owner`, type a reviewer name, click Approve, confirm. Check: the journal
   shows "Decisione salvata sul server … stato draft … bozza locale simulata". Click Approve
   again with the same inputs: no second command. Reload: after M5 the draft is still shown;
   before M5 the "non ancora leggibili" note shows.
6. Stale path: run `scripts/check_core_demo.py` (it exercises a stale-hash 409,
   `scripts/core_demo.md:124-135`), or edit the option hash in devtools and submit. Check the
   409 banner, the reloaded options, and "Ho riesaminato…" before deciding again.
7. Open `/#/casi/case-mil01-unknown-20261009/v1`. Check: `Da verificare`, "Prodotto da
   identificare", the clarification shows `Bozza`, `Simulato: sì`, question timestamp in UTC,
   "Risposta: Non disponibile".
8. Stop the backend (terminal 1) and click **Aggiorna**/retry on any screen. Check: an error
   with a retry button. No blank screen, no stale data presented as current.
9. Run the walkthrough with a stopwatch; record the duration in #129.

## 5. Polish and design audit

**Memi.** `scripts/core_demo.md:173-175` records 50/100 but no report is committed. A rerun on
2026-10-23 (`cd web && npx -y @memi-design/cli@2.7.9 diagnose . --json --no-write --fail-on none`)
gives 50/100 with **0 issues**. Visual-system, components, accessibility and maintainability
score 100. Color, responsive, spacing and typography are *unassessed* (score 0, confidence
0.4). The number reflects what the static scan could measure, not defects. Do not chase it.

Observed in the browser pass, worth fixing (ordered by demo impact):

- [ ] Forecast numbers with up to 16 visible decimals (`web/src/sections/CaseForecastPanel.tsx:7`).
- [ ] Case detail ~8,800 px tall at 1280×800; raw IDs (`EntityLink · link-… · c3c88e63…`) dominate.
- [ ] Mixed languages: UI Italian, backend reasons and option rationales English. Keep source
      text verbatim; at least label UI chrome consistently.
- [ ] Time zones: header in browser zone (`web/src/App.tsx:248`), queue in UTC
      (`web/src/sections/CaseQueue.tsx:40`), clarifications in ISO UTC.
- [ ] Run select label shows raw English status and a truncated id (`web/src/App.tsx:218`).
- [ ] Chiarimenti nav item opens a placeholder with a wrong endpoint (`web/src/i18n/it/sections.ts:43-48`).
- [ ] Options with no checks say "Nessun blocco obbligatorio pubblicato" in neutral tone. That
      reads like a pass; say "nessun controllo applicabile" instead (`web/src/sections/CaseOptionsPanel.tsx:65,84`).
- [ ] Light mode is the presentation mode (`web/docs/atelier/DESIGN.md:8-10`); record the video in light mode at 1280×800 or larger.

Do not add motion, gradients or decorative charts that carry no data. The Atelier rules
(`web/docs/atelier/DESIGN.md:28-34`) stay authoritative.

## 6. Rehearsal and video checklist (#129)

- [ ] Fresh replay attempt; `make check` green on the candidate SHA.
- [ ] Network off during the run-through; no console errors.
- [ ] Every number said aloud is visible on screen or in an approved #128 output.
- [ ] Optional features (#135, #191) either verified on this exact build or declared as not shown.
- [ ] Screenshots/video reviewed for names, brands, URLs, tokens (`voice-token` fragments!) and
      hold-out data before anything is shared (`docs/RFC-001-piattaforma.md:499-505`).
- [ ] Record actual duration, SHA and artifact links in #129.
