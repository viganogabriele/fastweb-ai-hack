# STATUS

Live task board. Plan, owners and full dependencies: `docs/PLAN.md`. Update rules: `AGENTS.md`.
One line per task. Edit only the lines of your own task.

## Done

- PLT-01 (C) Scaffold: `backend/` FastAPI, `web/` React+Vite, `make setup/dev/check`, CI, `.env.example`
- ACT-01 pure (E, done by Bianca) `modules/actions/simulation.py`: recursive daily stock simulation per scenario, RFC §7.3 test 5
- FC-01 pure (B, Bianca) `modules/intelligence/disaggregation.py`: weekly → daily baseline, `not_estimable` on missing/incoherent weeks, vintage at `as_of`

## In progress

- PLT-02 (C, Codex) MVP contracts, JSON Schema export and invariant tests; Opus 5.5 review passed, A/B/D G0 review and merge pending · branch `PLT-02-contracts`

## Ready (all hard dependencies merged)

- PLT-07 (A) Fastweb smoke test: chat, tool call, embeddings, ASR. Needs `FASTWEB_API_KEY` in `.env`
- DATA-02 (A) `config/eval_split.yaml`, `domain.yaml`, `aliases.yaml`
- ING-02 pure (A) `.eml` → canonical text + segments with offsets
- DATA-03 (A) 2–3 voice recordings + sidecar JSON
- ING-01 pure (B) ERP loaders with `available_at`
- INT-01 pure (B) Product mention → ranked candidates (alias + rapidfuzz)
- ACT-04 pure (E) Systems client (stock/ATP, lanes/ETA) against `make mocks`
- AG-01 pure (E) Agent loop with budget, trace, fallback; fake model
- WEB-01 (D) App shell on hand-written JSON
- EVL-01 (D) `eval/` harness + "product cannot open ground truth" test

## Blocked (waiting on)

- DATA-01a (A), ING-09 (A) ← PLT-02
- DATA-01b (B) ← DATA-01a
- DATA-01c (E) ← DATA-01b
- PLT-03 (C) ← PLT-02
- PLT-05 (C) ← PLT-02, PLT-07
- PLT-04, PLT-06 (C), ING-01 module (B), ACT-04 module (E) ← PLT-03
- Rest of Phase 1–2 ← PLT-04 / PLT-05 (see `docs/PLAN.md` §4)
