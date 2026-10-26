# Demo script: 4 minutes on the recorded dev run

**Track:** FastwebAI Hackathon 2026, luxury-retail challenge. **Status:** DEMO-03 (#129), aligned
with the recorded dev run `core-dev-20261023`. Result claims wait for the frozen hold-out
evaluation (#128) and are marked `[PENDING #128]`.

**Rule of the demo:** AI reads, code counts, humans decide. Every number on screen comes from a
stored artifact. The LLM cites artifact ids and cannot approve, book or override a check.
**Offline:** the run is replayed from recorded model and simulated-system responses (`recorded`,
network denied); no keys, no mock server. **No transfer, uplift, accuracy or ROI is claimed**
beyond the measured results.

Owner: lane D. Click path: [docs/frontend/demo-walkthrough-ui.md](frontend/demo-walkthrough-ui.md).
Recorded run: [scripts/core_demo.md](../scripts/core_demo.md). Public bundle:
[docs/demo_bundle/public-bundle.md](demo_bundle/public-bundle.md).

## Candidate

| Item | Value |
|---|---|
| Frozen candidate (G3, bound in [freeze-g3-handoff.md](freeze-g3-handoff.md); tag `freeze-g3` pending) | `1f7f35590782520d362c532c1e8159c4262703d7` |
| Demo build | current `main` (UI redesign #253/#262, AG-03d fix #261) on the same recorded run; see Rehearsals for the exact SHA |
| Recording of the dev run | code `38fe618a91a9d4f573e96fc2ec3cde2ee6ec8ebe`, assets `data/fixtures/runs/core-dev-20261023/` |
| Run | `core-dev-candidate`, scenario `historical`, `as_of` 2026-10-22 20:00 UTC (22:00 Rome), `mode: recorded`, status `degraded`, namespace `product` |
| Stores | MIL01, MIL02, MUN01, NYC01 (all dev; no hold-out store is shown) |
| Replay hashes | output `20a7a75b…f338` (`9346b85e…a56f` before #261), ledger `7b4f494a…230e`, snapshot `c5227036…6edb` (`replay-comparison.json`) |
| Hold-out results | `docs/holdout-results.md` `[PENDING #128]` |

## Prerequisites

- `make setup` (uv, Node ≥ 22). No `.env` keys are needed: `LLM_MODE=replay` is the default.
- Chrome/Chromium for the rehearsal tool (`cd tools/demo-rehearsal && npm ci`; Playwright uses its
  own browser cache, `npx playwright install chromium` if missing) and `ffmpeg` on `PATH` for the
  mp4 copy and the playback check (`ffprobe` is used when installed).
- **Decision clock is wall time.** Options of this run are valid until
  **2026-10-29 23:00 UTC** (the MIL02 transfers until 2026-10-23 13:30 UTC). After that the server
  refuses approvals as `option expired`, and the decision beat must be skipped (fallback below).

## Run, reset, replay

`make demo` now serves the later nine-store `production-demo-20261022` run (#257, not part of
the freeze or the evaluation). The walkthrough uses the frozen `core-dev-20261023` run:

```sh
tools/demo-rehearsal/serve-core-dev.sh   # fresh replay attempt, backend :8000, web :5173
# open http://localhost:5173/#/panoramica (light theme, window ≥ 1280×800)
```

- **Reset before every rehearsal or take:** run the script again. Each call replays the
  committed recordings into a new attempt under `data/core_demo/rehearsal/` and restarts the
  backend on it, so the decision beat starts undecided. `API_PORT`/`WEB_PORT` change the ports.
- The default replays the scripted synthetic decision (`decisions.json`, NYC01). Passing
  `decisions-operator.json` replays Lorenzo's genuine rejection of the D1 transfer instead
  (`scripts/core_demo.md`, "Genuine operator decision"); the UI does not show saved decisions
  yet, so the walkthrough does not rely on it.
- **Replay proof** (two cold attempts, compared hashes, negative rehearsals):
  [scripts/core_demo.md](../scripts/core_demo.md) "Rebuild without credentials".
- **Timed rehearsal and video:** [tools/demo-rehearsal/README.md](../tools/demo-rehearsal/README.md).

## The 4 minutes

Times are targets; the measured duration of each take is in the rehearsal table below.

### 0:00–0:20 · Thursday evening (Panoramica)

**Screen:** Panoramica, tab "Decisioni operative". Expand **Mostra decisioni**; the list
starts collapsed. Header: run `historical · 22/10/2026, 22:00 ·
core-dev · degraded`, badge `recorded`. 38 open decisions, 2 critical or high, the decision table
sorted by priority, the store map.

> "Tonight is Thursday. Today's certified sales arrive tomorrow, and the sale that did not happen
> because size M ran out never arrives at all. But at closing time the store wrote it down. This
> is a recorded run replayed offline, and it says it is `degraded`: some things still need
> checking, and we show them."

### 0:20–0:50 · The receipt (Fonti)

**Screen:** Fonti, search `1035`, open MIL01's email of 09/10 10:35 (Italian). Two highlighted
spans: "da ieri siamo a zero cardigan logo in M, sia nero che blu" and "Anche 1 o 2 pezzi per
colore, ce lo chiedono in continuazione". Hover shows the linked case.

> "The model extracts two facts: a stockout with an exact zero, and demand it cannot count.
> 'In continuazione' stays vague; no number is invented. Each fact keeps its quote and code-point
> offsets in the canonical text."

### 0:50–1:40 · The case (D1, cardigan logo M, MIL01)

**Screen:** case `case-mil01-i10919b00011-20261008` (title "VLOGO CARDIGAN" from the catalogue
display name): unmet demand, high priority, Allocazione, no deadline. "Cosa dicono i negozi": three
quotes from two emails. "Prima di decidere, verifica": five checks (style-level link, vague
quantity, stock is the store's statement, a possible duplicate pair not to be added, deadline not
estimable). 2 documents from 2 independent origins. Then the forecast: baseline about 1.4 and 1.6
units/day for the two colours, `invariata`, "Baseline only: no overlay applied".

> "The case links the note to the style in the catalogue, but the colour is not identified, so it
> stays a style-level case with its open checks listed. The forecast is not touched: no count, no
> uplift. The reply from MIL02 is a second origin, not a second count."

### 1:40–2:10 · The investigator (trace)

**Screen:** Tracce, open the trace: `recorded`, **fallback sì**, outcome `verify`, six steps:
`get_case_evidence`, `get_available_stock` ×2 (both colours), `get_lane_and_eta` MUN01→MIL01 and
NYC01→MIL01, `evaluate_options` with candidate donors MUN01 and NYC01.

> "This is the agent part, a real recording from GLM on Fastweb. It reads evidence, stock and
> lanes; it cannot approve. Here it used its six-tool budget, so the system publishes a visible
> fallback and the case ends in `verify`. That is a valid outcome, and we show it as one."

### 2:10–2:40 · Options, computed by code

**Screen:** "Opzioni di stock": hold (Consigliata), verify stock, ask the store, notify the owner,
transfer. Open "Trasferisci da un altro negozio": 1 unit size L MIL02→MIL01, arrival 23 Oct,
lost sales 0 in every scenario, transport €15.6, every mandatory check `ok`, "Not recommended:
the move does not reduce total unserved units against hold".

> "The options and their checks are computed by code, not written by the model. The transfer is
> feasible and still not recommended: it moves a size L, and the store is out of M. It saves
> nothing."

### 2:40–3:00 · A person decides

**Screen:** open "Avvisa il responsabile", type a reviewer name, Approva, "Conferma approvazione".
The case journal shows "Decisione salvata sul server: approvata · … · stato draft · bozza locale
simulata, nessun invio esterno".

> "Only a person approves. The server re-checks the option against its inputs and saves a local
> draft. No message goes out and no stock moves: in this demo every execution is simulated."

On this candidate Lorenzo also rejected the transfer for real (size L does not fix an M
stockout); that decision is in the ledger of the operator replay, not on screen.

### 3:00–3:25 · Not sure? Ask (MIL01 unknown product)

**Screen:** case `case-mil01-unknown-20261009`, "Prodotto da identificare", `Da verificare`
("Product 'M' not found in the catalog"). Trace without fallback. Clarification: `Bozza`,
`Simulato: sì`, the Italian question quoting the store's sentence, answer "Non disponibile".

> "The same email also says 'Avete qualche M?'. M of what? The system does not guess: the case
> stays `verify` and the agent drafts a question to the store in its language. It is a draft;
> nothing is sent."

Say aloud: answering it live is not part of this walkthrough (#134/#135 optional).

### 3:25–3:45 · Corrections are not added up (#237)

**Screen:** Fonti, search `20260918`: MIL01's closing email "Fatturato: 58,0k" and, about 50 minutes
later, "il fatturato di oggi e' 85,0k e non 58".

> "Stores correct themselves. The correction names the old figure and replies to the original
> mail, so 85k supersedes 58k: one active fact, never summed. An identical resend of another
> closing email was proven a duplicate and counted once."

Honesty: the `supersedes` relation and the 10 duplicates are stored artifacts
(`scripts/core_demo.md`, "Source-backed resend and correction"); the UI does not draw relations
yet. NYC01's "correction, sales were 45.1k not 54.1k" is **not** applied (no reply parent):
both figures stay a possible overlap.

### 3:45–4:00 · Results and buyer

**Screen:** results slide (`tools/demo-rehearsal/results-slide.html`), not the app.

> "Measured once on the hold-out stores we never tuned on: `[PENDING #128]`. Synthetic data,
> built with decoys and noise. The buyer is HQ allocation; a pilot would measure the value on
> real numbers."

Only numbers from `docs/holdout-results.md`, with denominators and limits. No ROI, no uplift.

## Fallbacks

| If | Do |
|---|---|
| The approval fails (`option expired`, 409, network) | Read the error aloud; show the stored draft of the frozen run instead: `GET /api/runs/core-dev-candidate/decisions` (NYC01 scripted synthetic reviewer, `dispatch_status: draft`). Never claim a decision that is not on screen. |
| A second take on the same attempt | Re-run `serve-core-dev.sh` first: an option decided once in a scenario is refused (PLT-15). |
| The backend or UI does not start | Play the rehearsal video (`data/demo/video/…/rehearsal.mp4`) and narrate over it. |
| Replay is in doubt | Check `data/core_demo/rehearsal/replay.json` (written by `serve-core-dev.sh`): `output_sha256` `20a7a75b…f338`, `ledger_sha256` `7b4f494a…230e`, `snapshot_sha256` `c5227036…6edb`, `network_attempts` 0, empty `cache_misses`. |
| Time runs short | Drop the correction beat (3:25–3:45), keep results. |
| Asked about live voice / clarification answers | Not shown: optional (#191, #134) and not verified on this build. |

## Rehearsals

Measured with `tools/demo-rehearsal` on a fresh attempt, 1280×800, light theme, captions on.

| Date (UTC) | Build | Pace | Measured | Notes |
|---|---|---|---|---|
| 2026-10-23 07:58 | main `1f7f355` (pre-#253 UI), dev run `core-dev-20261023` | 1 | **4:01.1** (241.08 s, 6,027 frames) | Phase 1 proof. All 9 beats, 0 console errors, 0 deny hits, decision saved as `draft`. Trace beat 41 s vs 30 s target: hold trimmed by 6 s afterwards. Video `data/demo/video/phase1-main-1f7f355/rehearsal.mp4` (sha256 `270673c0…c91d`), not final. |
| 2026-10-23 10:20 | main `bb37a2d` (UI redesign #253/#262, #261) + this branch, `core-dev-20261023`, synthetic `decisions.json` | 1 | **3:42.1** walkthrough (raw webm 237.04 s incl. a 15 s static tail before the browser closed) | Selectors rewritten for the redesign; D1 `notify_owner` approved as a draft. 1 console error (`/kpi` 404: this run has no KPI export). Deny hits on D1: catalogue name "VLOGO CARDIGAN" and the quote "Rinascente ne ha pochi anche loro". Holds lengthened afterwards (+12 s) and the mp4 is now cut at the last beat. |
| `[PENDING]` final | frozen bundle/run after #128, current UI | 1 | | Final video under `data/demo/video/`. |

## Do not show

- Hold-out stores (ROM01, PAR02, …): the old ROM01 scaffolding beat is removed.
- The what-if panel: it does not exist.
- Prodotti and "Dove va la piattaforma" (catalogue photos are commercial reference material), the
  Mercato tab (this run has no KPI export: `/kpi` returns 404) and the W42 workbook header.
- MUN01 queue: one event splits into many cases.

## Privacy

The video records the real UI on the synthetic dev run, not the public bundle. It shows synthetic
first names, store names (Milano Montenapoleone), a real department store in a quote
("Rinascente"), the catalogue display name "VLOGO CARDIGAN" and source URIs
(`dataset://store_emails/…`). It is cleared for
the jury session only; public use needs Lorenzo's separate approval
([public-bundle.md](demo_bundle/public-bundle.md) §Release). The rehearsal tool scans every beat
for brand names, email addresses, hold-out store ids and tokens and records hits in
`rehearsal.json`.
