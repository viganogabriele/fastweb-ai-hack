# STATUS

Live task board. Plan, owners and full dependencies: `docs/PLAN.md`. Update rules: `AGENTS.md`.
One line per task. Edit only the lines of your own task.

## Done

- PLT-01 (C) Scaffold: `backend/` FastAPI, `web/` React+Vite, `make setup/dev/check`, CI, `.env.example`
- INT-01 pure (B, Bianca) `modules/integration/candidates.py`: mention → ranked candidates, size vs size run, linked/ambiguous/unlinked

## In progress

<!-- - ID (lane, person) one-line goal · branch `ID-slug` -->

## Ready (all hard dependencies merged)

- PLT-02 (C) Contracts in `core/contracts/`. **Gates G0**: everyone reviews within 30 min
- PLT-07 (A) Fastweb smoke test: chat, tool call, embeddings, ASR. Needs `FASTWEB_API_KEY` in `.env`
- DATA-02 (A) `config/eval_split.yaml`, `domain.yaml`, `aliases.yaml`
- ING-02 pure (A) `.eml` → canonical text + segments with offsets
- DATA-03 (A) 2–3 voice recordings + sidecar JSON
- ING-01 pure (B) ERP loaders with `available_at`
- FC-01 pure (B) Weekly → daily forecast disaggregation
- ACT-01 pure (E) Recursive daily stock simulation + RFC §7.3 test 5
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
