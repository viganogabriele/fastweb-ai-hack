# Frontend objectives (lane D handoff)

Audience: the people changing `web/` with a human in the loop. This folder says **what** the UI
must achieve for the demo and judging, what already exists, and what to build next. It does not
prescribe component code. Every claim about existing code cites `file:line` at commit
`baa2fc3` (after the Tesseract rename, #232).

| File | Workstream | Issue | Priority |
|---|---|---|---|
| [demo-walkthrough-ui.md](demo-walkthrough-ui.md) | Screens and clicks of the 4-minute demo, gaps, polish | #129 | **Must** |
| [clarification-answer-ui.md](clarification-answer-ui.md) | Submit a simulated clarification answer, follow the new run | #135 (WEB-09) | Should |
| [live-voice-ui.md](live-voice-ui.md) | Phone capture page, live labels, real-device dry run | #191 (DEMO-04) | Should (optional feature) |
| [holdout-results-ui.md](holdout-results-ui.md) | Showing frozen evaluation results without overclaiming | #128 | Could |

## 1. What the UI must demonstrate

Product rule: **AI reads, code counts, humans decide** (`docs/RFC-001-piattaforma.md:79`). Judges
give 40% to "completeness and feasibility": a narrow path that demonstrably works beats a broad,
half-mocked one (`docs/findings.md:85`), and 20% to an agent that *acts* (`docs/findings.md:86`).
The UI is the evidence for both. One click path must show, from the same published run:

1. **Source**: the store's own words (email or voice note), canonical text, highlighted span.
2. **Evidence**: the observation that quotes that span, with its kind, quantity (or "vague"), and link status.
3. **Case**: what changed, supporting vs contradicting evidence, "N documents, M origins",
   open uncertainties (`docs/RFC-001-piattaforma.md:216`).
4. **Baseline/scenario or abstention**: forecast baseline with low/base/high scenarios, or the
   explicit reason it was not estimable (`docs/RFC-001-piattaforma.md:64`).
5. **Investigator/tool checks**: the recorded agent trace (tools called, budget, fallback) and
   the deterministic option checks.
6. **Human decision**: Approve/Reject on a published option, saved as a **local draft**, never
   sent (`docs/RFC-001-piattaforma.md:489`).

Ambiguity is a feature: a `verify` case with candidates and a drafted clarification is a valid
outcome and must stay visible (`docs/RFC-001-piattaforma.md:713`).

## 2. Honesty rules (non-negotiable)

Every PR touching `web/` must keep these. Reviewers reject violations.

- [ ] **Never fake data.** Product screens render only API responses for the selected run. No
      hand-written numbers, no placeholder charts, no "example" values outside a declared fixture
      namespace. The existing fixture-only block must stay gated (`web/src/sections/CaseDetailAnalysis.tsx:16`).
- [ ] **Label provenance everywhere it matters.** `live`, `recorded`, `fixture`, `unavailable`
      (`docs/RFC-001-piattaforma.md:19`) plus `simulated` for store replies/executions and
      `degraded` run status. Synthetic data must be declared as synthetic (`docs/findings.md:140`).
- [ ] **No local fake "answered"/"approved"/"sent" state.** A state changes only after the server
      confirms it, and then shows what the server returned (e.g. `dispatch_status: draft`).
      Pattern to reuse: `web/src/sections/caseOptionsState.ts` (idempotency key, 409 review, retry
      of the same command).
- [ ] **No invented metrics.** No accuracy, uplift, ROI, "revenue recovered", lead-time or
      "decision margin" figure unless it comes from an approved evaluation output with its
      denominator (`docs/RFC-001-piattaforma.md:723`, #128).
- [ ] **Unknown stays unknown.** Missing values read "Non disponibile"; vague quantities stay
      vague or ranges (`docs/findings.md:126`); no guessed SKU, colour or size.
- [ ] **Uncertified store signals are visibly separate from actuals** (`docs/findings.md:116`).
- [ ] **One run per view**; never mix artifacts of two runs (`docs/RFC-001-piattaforma.md:274`).
- [ ] **Clock is the run cutoff, not wall-clock time** (`web/docs/atelier/DESIGN.md:39`), and
      every timestamp states its time zone.
- [ ] **Model text is data.** Render stored/model strings as text nodes, never as HTML
      (`web/src/sections/CaseTracePanel.tsx:54-55`).

## 3. Current state per screen

Verified on 2026-10-23 against an offline replay of `data/fixtures/runs/core-dev-20261022/`
(run `core-dev-candidate`, `recorded`, `degraded`, 41 cases, 13 documents). How to reproduce
this setup: [demo-walkthrough-ui.md §1](demo-walkthrough-ui.md#1-run-the-real-ui-offline).

| Screen (route) | State | Notes |
|---|---|---|
| Shell, run selector (`App.tsx`) | Partial | Run picker and `mode` badge exist (`web/src/App.tsx:208-229`). No synthetic-data disclosure, run status only inside the select label, brand is "Tesseract" with no demo branding (`web/src/i18n/it/shell.ts:8`), leftover "Moncler" strings (`web/src/i18n/it/shell.ts:9,40`). |
| Panoramica `#/panoramica` | Done | Counts derived from the run's cases (`web/src/sections/Overview.tsx:152-159`), deadlines from the cutoff. |
| Casi queue `#/casi` | Done | Filters, sort, uncertainty badges (`web/src/sections/CaseQueue.tsx:111-160`). |
| Case detail `#/casi/<id>/<version>` | Partial | All data is real, but evidence shows as raw `kind · id · version` codes with no quote or link to the source (`web/src/sections/CaseQueue.tsx:331-339`). The forecast is a raw table with up to 20 decimals (`web/src/sections/CaseForecastPanel.tsx:7`), not the chart the RFC asks for. The page is ~8,800 px tall. |
| Options + decision | Done (server) | Published options, checks, local-draft POST, 409 review, retry (`web/src/sections/CaseOptionsPanel.tsx`). **Gap:** existing decisions are not shown after a reload; only this tab's journal (`web/src/sections/CaseOptionsPanel.tsx:100-114`). The replay contains an approved draft, yet every case still reads "Aperto". |
| Investigator trace | Done (read-only) | Mode, fallback, steps, refs (`web/src/sections/CaseTracePanel.tsx`). No UI for `POST .../investigate` (`backend/tesseract/api/routers/investigations.py:243`). |
| Clarification panel (in case) | Done (read-only) | Draft question, `simulated`, timestamps (`web/src/sections/CaseClarificationsPanel.tsx:49-65`). No answer UI → #135. |
| Fonti `#/fonti` | Done | Canonical text with highlighted case evidence on hover (`web/src/sections/RunWorkspace.tsx:274-289`). No click-through from highlight to case, no audio player. |
| Report `#/report` | Done | Briefs with resolvable citations (`web/src/sections/ReportsPage.tsx`). |
| Pipeline `#/pipeline` | Done | Module list/graph and "new run with selection" (`web/docs/WEB-03.md`). |
| Prodotti `#/prodotti` | Done | Cases grouped by product, sales explicitly unavailable (`web/docs/WEB-08.md:15-21`). No catalog photos. |
| Chiarimenti `#/chiarimenti` | **Missing** | Placeholder `PendingSection` (`web/src/App.tsx:269-270`) advertising a non-existent endpoint `POST /api/clarifications/{id}/answer` (`web/src/i18n/it/sections.ts:46`). |
| Phone page `/store/record` | Done (code), unverified on device | `web/src/store/RecordPage.tsx`. Real-device dry run open (#191). |
| Voice process button | Partial | Works only while the URL fragment holds `voice-token`; the first sidebar click drops it (verified in browser, see [live-voice-ui.md](live-voice-ui.md)). |

## 4. Prioritized objectives

IDs are for reference in PRs and issues. Order within a class is the order to do them.

### Must (the demo depends on them)

- **M1 Disclosure frame.** A persistent strip in the shell: run id, `as_of` with time zone, `mode`,
  run status (`degraded` visible), namespace, and "dati sintetici". Fix "Moncler" leftovers.
  Apply the branding decision in §5.
- **M2 Evidence you can follow.** In case detail, show each supporting/contradicting observation
  as its quoted span (document, store, date, language), with a link that opens the source in
  Fonti with that span highlighted. Use `GET /api/runs/{id}/documents/{doc}` (`DocumentDetail`
  has observations, segments, links).
- **M3 Readable forecast.** A baseline vs low/base/high chart per SKU with rounded values and
  units, the overlay status and abstention reason as text; keep the table behind a disclosure.
- **M4 Decision card first.** Reorder case detail: summary → evidence → forecast/abstention →
  trace → options/decision. Collapse raw IDs, hashes and producer versions into "Dettagli
  tecnici". Hide the fixture-example block entirely in the product namespace
  (`web/src/sections/CaseDetailAnalysis.tsx:23-46`).
- **M5 Persisted decision state.** After reload, show existing local drafts for a case. This
  needs a read endpoint (none exists: `backend/tesseract/api/routers/options.py` has only
  GET options and POST decisions). Open a lane C issue; until it lands, the UI must not imply a
  case is undecided because of a missing read. Show "stato decisioni non disponibile".
- **M6 Walkthrough fit.** Do the click-path fixes in [demo-walkthrough-ui.md](demo-walkthrough-ui.md) §3.

### Should

- **S1 WEB-09 answer UI** (#135), only with a registered recording for offline use. See [clarification-answer-ui.md](clarification-answer-ui.md).
- **S2 Live voice hardening** (#191): keep the token across navigation, add live labels, then
  the device dry run. See [live-voice-ui.md](live-voice-ui.md).
- **S3 Chiarimenti page**: either list clarifications of the selected run (links to their
  cases) or remove the nav item. Never keep the placeholder text with a wrong endpoint.
- **S4 Error detail**: `readApi` drops status and `detail` (`web/src/api/client.ts:18-21`).
  Surface 409 "Run is not published", 403 fixture and 404 distinctly.
- **S5 Time zones**: the header uses the browser zone (`web/src/App.tsx:248`), the queue uses UTC
  (`web/src/sections/CaseQueue.tsx:40`). Pick one rule (UTC plus store-local where relevant)
  and label it.

### Could

- **C1** Hold-out results view ([holdout-results-ui.md](holdout-results-ui.md)).
- **C2** Catalog reference photos in Prodotti/case header, labelled "foto di riferimento, non
  l'articolo simulato" (`data/catalog/README.md:14-21`). Needs a static/authorized media route;
  there is none today (`data/catalog/README.md:41`).
- **C3** "Run investigator" button (`POST .../investigate`, 202 + `Location`) for recorded/live
  parents, with job polling, 409 "already decided"/"not actionable" states.
- **C4** Design polish from a fresh Memi audit (see demo-walkthrough §5).
- **C5** Audio player for voice sources (whole recording; no invented seek, `docs/RFC-001-piattaforma.md:529`).

## 5. Open decisions for Lorenzo

1. **Branding.** `AGENTS.md:3` says "Valentino demo branding", but `docs/findings.md:8` and
   RFC §4.12 (`docs/RFC-001-piattaforma.md:499-505`) require a neutral name and fictional brand
   in anything public (bundle, screenshots, video). Proposal: Valentino branding only in the
   private jury demo, if the organizers confirm it; public bundle/video stay neutral and are
   labelled «esempio sintetico, nomi sostituiti».
2. **Demo case set.** The script uses ROM01 (hold-out) and a live D5 reply
   (`docs/demo_script.md:72-100`). See the proposed replacements in demo-walkthrough §2.
3. **Decision read endpoint** (M5): lane C owner and timing.
4. **UI language.** Backend reasons/rationales are English while the UI is Italian (e.g. option
   rationale, uncertainty reasons). Keep source text verbatim; decide whether UI chrome stays
   Italian for the jury.

## 6. Working rules for UI PRs

- [ ] Stay in `web/` (lane D). Regenerate `web/src/api/schema.d.ts` with `make types`; never edit it.
- [ ] Use `npm run dev:mock` only for layout work; verify behaviour against a real replay (§1 of
      the walkthrough doc). Mock data never ships as product data (`web/mock-api/plugin.ts:6-8`).
- [ ] Add/extend `web/tests/*.test.mjs` for state logic (pure functions, as the existing panels do).
- [ ] Attach before/after screenshots from the real replay to the PR; keep them out of the repo
      unless small and clearly useful.
- [ ] `make check` passes; a human clicks through the relevant manual test script.
