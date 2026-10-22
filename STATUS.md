# STATUS

Live task board. Plan, owners and full dependencies: `docs/PLAN.md`. Update rules: `AGENTS.md`.
One line per task. Edit only the lines of your own task.

## Done

- PLT-01 (C) Scaffold: `backend/` FastAPI, `web/` React+Vite, `make setup/dev/check`, CI, `.env.example`

## In progress

- PLT-02 (C, Codex) MVP contracts, JSON Schema export and invariant tests implemented; review pending · branch `PLT-02-contracts`

## Ready (all hard dependencies merged)

- PLT-07 (A) Fastweb smoke test: chat, tool call, embeddings, ASR. Needs `FASTWEB_API_KEY` in `.env`
- DATA-02 (A) `config/eval_split.yaml`, `domain.yaml`, `aliases.yaml`
- ING-02 pure (A) `.eml` → canonical text + segments with offsets
- ACT-01 pure (B) Recursive daily stock simulation + RFC §7.3 test 5
- FC-01 pure (B) Weekly → daily forecast disaggregation
- INT-01 pure (B) Product mention → ranked candidates (alias + rapidfuzz)
- WEB-01 (D) App shell on hand-written JSON
- EVL-01 (D) `eval/` harness + "product cannot open ground truth" test
- DATA-03 (D) 2–3 voice recordings + sidecar JSON

## Blocked (waiting on)

- DATA-01a (A), ING-09 (A) ← PLT-02
- DATA-01b (B) ← DATA-01a
- PLT-03 (C) ← PLT-02
- PLT-05 (C) ← PLT-02, PLT-07
- PLT-04, PLT-06, ING-01, ACT-04 ← PLT-03
- Rest of Phase 1–2 ← PLT-04 / PLT-05 (see `docs/PLAN.md` §4)
