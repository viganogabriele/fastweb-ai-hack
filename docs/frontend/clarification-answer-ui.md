# Clarification answer UI (#135, WEB-09)

Goal: an operator submits an **explicitly simulated** store answer to a published clarification,
then follows the backend's new follow-up run, which links the product in a new scenario. The
original published run never changes, and no real message is sent (#134 "Outcome";
`docs/RFC-001-piattaforma.md:657`). Priority: **Should**. It is optional for the demo and must
not delay #129 (#134 "Dependencies and delivery").

Owner: #135 is assigned to `viganogabriele`; coordinate before coding. API handoff: the
OUT-02e worker is posting the exact handoff as a comment on #135. If it disagrees with this
file, the backend code wins; update this file in the same PR.

## 1. What exists

- Read-only panel inside case detail: lists clarifications of the exact case version, opens one,
  shows `Bozza/asked/answered/cancelled`, `Simulato`, question, stored timestamps, the answer
  document link (`web/src/sections/CaseClarificationsPanel.tsx:9-65`,
  `web/src/api/caseClarifications.ts:12-66`).
- Generated DTOs already include `AnswerRequest` and `AnswerJob` (`web/src/api/schema.d.ts`,
  search `AnswerRequest`). Regenerate with `make types` if the backend changes.
- Backend route: `POST /api/runs/{run_id}/cases/{case_id}/clarifications/{clarification_id}/answer`
  (`backend/tesseract/api/routers/clarifications.py:39-77`).
- Not built: the answer form, submission states, follow-up tracking, the Chiarimenti page
  (placeholder at `web/src/App.tsx:269-270`, with a wrong endpoint in
  `web/src/i18n/it/sections.ts:46`).

## 2. API contract (as implemented)

**Request**: `POST /api/runs/{run_id}/cases/{case_id}/clarifications/{clarification_id}/answer?fixture=<bool>`

Body `AnswerRequest` (`backend/tesseract/modules/agents/answer_registry.py:94-106`). All fields
are required except `language`. The three IDs **must equal the URL**, or the API returns 422
(`backend/tesseract/api/routers/clarifications.py:49-50`).

| Field | Value from the UI |
|---|---|
| `run_id`, `scenario_id` | Selected `RunView.spec` (the parent; must be the current published run of its scenario) |
| `case_id`, `case_version` | The case shown (exact version) |
| `clarification_id`, `clarification_version` | The clarification shown (exact version) |
| `text` | Operator input (the simulated reply) |
| `received_at` | ISO instant with offset. Must be **strictly after** `asked_at` and the parent `as_of` (`backend/tesseract/modules/agents/clarifications.md:9-10`) |
| `language` | Store language (e.g. `it`); `null` allowed |
| `follow_up_scenario_id` | New, declared scenario id, distinct from the parent's (e.g. `simulated-answer-<clarification short id>`) |
| `as_of` | Follow-up clock, ≥ `received_at` |
| `idempotency_key` | `crypto.randomUUID()` created **once per intent**, reused on every retry of that same payload |

The namespace comes from the parent; never from the body. Send `fixture=true` only when
`RunView.namespace === 'fixture'` (403 without `FIXTURE_MODE`,
`backend/tesseract/api/routers/runs.py:58-63`).

**202 response**: `AnswerJob { fingerprint, run: RunSpec, document: SourceDocument, simulated: true }`
(`backend/tesseract/modules/agents/answer_registry.py:109-113`). `run.run_id` is the follow-up
run. Its lifecycle comes from the normal `GET /api/runs/{run_id}` (`RunView.status`:
`pending → running → succeeded|degraded`, or `failed|blocked`; `published`).

**Errors** (`backend/tesseract/api/routers/clarifications.py:49-68`):

| Status | Cause | UI behaviour |
|---|---|---|
| 422 | Scope mismatch, invalid answer (time order, closed case, answered/cancelled question, wrong store/scenario) | Inline form error with the `detail`; keep the text; no retry button |
| 409 | `AnswerConflict`: parent no longer the current published run, case/clarification version changed, idempotency key reused with a different payload, parent unpublished (`answer_registry.py:205-223,333`) | "Contesto cambiato": reload runs/case/clarification, ask the human to re-read, require a new confirm (new idempotency key) |
| 424 | `UnrecordedAnswer`: offline/recorded parent and no registered recording for this exact event (`answer_registry.py:362`) | "Risposta non registrata per il replay offline: questa risposta non può essere elaborata senza rete". No retry; keep the text |
| 503 | Unavailable parent/pipeline, or DB busy (`Retry-After: 5`) | "Servizio occupato/non disponibile"; retry **with the same key** |
| network/timeout | Unknown outcome | "Esito sconosciuto"; retry with the same key (the server deduplicates, `answer_registry.py:313-345`) |

Note: `answer_registry.md` still documents a `/answers` path, body without IDs, and 503 for
unrecorded answers. The router above is what runs: `/answer`, IDs in body, 424.

**Offline constraint.** In `recorded`/`fixture` parents, only answers whose exact fingerprint
(parent snapshot, question version, text, receipt time, language) was registered by trusted
recording code are accepted (`backend/tesseract/modules/agents/answer_registry.md:67-78`). No
API lists registered answers, and the frontend must not invent one. For an offline demo the
operator needs the exact registered values. Get them from the OUT-02e handoff on #135 and
prefill them from a reviewed, versioned source, labelled "risposta registrata". Free text in an
offline parent will return 424, and that is correct behaviour. Live parents accept free text
but the event is never replayable.

## 3. UX states and acceptance criteria

Place the form inside the clarification detail (`ClarificationRecord`,
`web/src/sections/CaseClarificationsPanel.tsx:49-65`). Optionally list it on the Chiarimenti page.

- [ ] **Eligibility.** The form shows only when the selected run is published, the case is not
      `closed`/`decided`, and the clarification is `draft` or `asked`. Otherwise show why.
- [ ] **Declared simulation.** The header reads "Risposta simulata del negozio · nessun messaggio
      reale". The parent mode badge (`recorded`/`fixture`/`live`) is visible next to it.
- [ ] **Inputs.** Text (required). `received_at` with an explicit time zone: default the parent
      `as_of` + 1 min, shown in UTC and store-local. Language from the store. Follow-up
      scenario id is prefilled and editable. Validate time order client-side before submit;
      the server stays authoritative.
- [ ] **Confirm step** restating text, receipt time, new scenario and "il run originale non cambia".
- [ ] **Submitting**: button disabled, one request in flight (synchronous lock, as in
      `web/src/sections/caseOptionsState.ts:53-62`).
- [ ] **Accepted (202)**: show "Risposta accettata come evento simulato", the follow-up `run_id`,
      the new scenario and the answer document id. Then poll `GET /api/runs/{run_id}` (2 s, with
      a limit, abortable on unmount; reuse the polling shape of
      `web/src/store/VoiceProcessButton.tsx:44-69`).
- [ ] **Running**: show the live `RunView.status` and module progress if available. The parent
      clarification still reads `Bozza`/`asked`. **Never** show "answered" locally.
- [ ] **Published (`succeeded`/`degraded`)**: offer "Apri il run di follow-up". Add the run via
      `runs.acceptRun(view, originRunId)` (`web/src/api/useRuns.ts:43-52`), select it, and open
      the same `case_id` from `GET /api/runs/{new}/cases/{case_id}`. Show the version the API
      returns; do not reuse the parent's version. That run shows the clarification as
      `answered` with `answer_document_id`.
- [ ] **Failed/blocked/timeout**: show the status and that the answer event is stored but not
      processed. No local forecast or link change. A rerun needs an operator `reset_run`
      (`answer_registry.md:79-83`), so no UI retry button for this case.
- [ ] **Errors** per the table in §2. Each message includes the API `detail` and status.
- [ ] **Revisit.** Leaving and returning to the case keeps the pending/uncertain submission and
      its key for this tab (pattern: `retainedSessions`, `web/src/sections/CaseOptionsPanel.tsx:11-27`).
- [ ] **Follow-up view honesty.** In the follow-up run, the queue/case/forecast are whatever the
      API returns. Historical `parent:` versions are already excluded from current lists
      (`backend/tesseract/api/artifacts.py:6-34`). The UI never merges parent and child artifacts.
- [ ] **Tests**: pure state module with `web/tests/*.test.mjs` covering 202, 409, 422, 424, 503,
      network retry with the same key, double click, unmount during poll.

## 4. Manual test script

Prerequisite: the real replay from [demo-walkthrough-ui.md §1](demo-walkthrough-ui.md#1-run-the-real-ui-offline).
It contains exactly one clarification: `case-mil01-unknown-20261009` v1, status `draft`, asked
`2026-10-22T20:00:00Z`.

1. Open `/#/casi/case-mil01-unknown-20261009/v1` → Chiarimenti → open the clarification.
   Check: "Risposta simulata…" form visible, mode badge `recorded`, original status `Bozza`.
2. Type any free text, keep the default receipt time, confirm. Check: **424** message ("non
   registrata per il replay offline"), text kept, status still `Bozza`, no new run in the selector.
3. Set `received_at` before `2026-10-22T20:00Z` and submit. Check: client-side or 422 error;
   nothing changes.
4. Double-click confirm quickly. Check in devtools Network: one POST only.
5. Stop the backend, submit. Check: "esito sconosciuto" with retry. Restart and retry. Check:
   the same `idempotency_key` in both request bodies.
6. **Accepted path** (needs a registered answer from the OUT-02e handoff, or a `live` parent with
   keys before 2026-10-25 00:00 UTC). Submit the registered values. Check: 202 → follow-up
   run id shown → status advances → "Apri il run di follow-up" → the run selector shows the new
   scenario → the case opens in the new run with the clarification `answered`, the answer
   document readable, and a new product link if the pipeline produced one. Then switch back to
   `core-dev-candidate`. Check: the original clarification is still `Bozza` and the case is unchanged.
7. Submit the same values again with a new confirm. Check: the same follow-up run id is
   returned (server dedup); no second run.
8. While the follow-up exists, answer again from the **parent** with a different text. Check:
   expected 409 or 424 per backend rules, shown as such. No local overwrite.
