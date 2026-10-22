# STATUS

Live task board. Plan, owners and full dependencies: `docs/PLAN.md`. Update rules: `AGENTS.md`.
One line per task. Edit only the lines of your own task.

## Done

- PLT-01 (C) Scaffold: `backend/` FastAPI, `web/` React+Vite, `make setup/dev/check`, CI, `.env.example`
- DATA-02 (A) `config/eval_split.yaml` (12 dev / 10 hold-out / 17 unassigned), `domain.yaml` (+ §4.9 policy with units), `aliases.yaml` (dev-email provenance, tested)
- ACT-01 pure (E, done by Bianca) `modules/actions/simulation.py`: recursive daily stock simulation per scenario, RFC §7.3 test 5
- FC-01 pure (B, Bianca) `modules/intelligence/disaggregation.py`: weekly → daily baseline, `not_estimable` on missing/incoherent weeks, vintage at `as_of`
- INT-01 pure (B, Bianca) `modules/integration/candidates.py`: mention → ranked candidates, size vs size run, linked/ambiguous/unlinked
- PLT-02 (C) `tessera/core/contracts/`: MVP DTO contracts, JSON Schema export, invariant tests
- EVL-01 (D, done by Bianca) `eval/`: frozen-export harness (manifest hashes before any answer key), Linux Landlock launcher denying product reads of answer keys/generator/eval
- ING-02 pure (A, done by Bianca) `modules/ingestion/email_parser.py`: `.eml` → canonical text, segments with code-point offsets, quotes and attachments flagged
- ACT-04 pure (E, done by Bianca) `modules/sources/systems_client.py`: DC stock/ATP → `StockFact`, lanes with crosswalk, ETA from cut-off and pickup days, `Unknown` instead of zero
- ING-01 pure (B, Bianca) `modules/sources/erp.py`: typed ERP rows with provenance, `available_at` (next-day 06:00 local), latest forecast vintage per store
- PLT-07 (A) `scripts/smoke_fastweb.py` + `docs/smoke-fastweb.md`: key per model, tool calls on 5 chat models, Gemma chosen, embeddings OK, no ASR (OQ-2 closed)

## In progress

## Ready (all hard dependencies merged)

- PLT-05 (C) `core/llm.py` + `core/cache.py`: `chat/extract/embed`, recipe in `docs/smoke-fastweb.md`
- DATA-03 (A) 2–3 voice recordings + sidecar JSON + manual transcript
- AG-01 pure (E) Agent loop with budget, trace, fallback; fake model
- WEB-01 (D) App shell on hand-written JSON
- DATA-01a (A) Fixtures: D1 positive doc + observation, ambiguous mention, forward/duplicate, correction
- ING-09 (A) Physical quantities (exact/range/vague/unknown) with units, from span text
- PLT-03 (C) `core/db.py`, `core/repo.py`: SQLite artifact store, `as_of` filter, fixtures load

## Blocked (waiting on)

- DATA-01b (B) ← DATA-01a
- DATA-01c (E) ← DATA-01b
- PLT-04, PLT-06 (C), ING-01 module (B), ACT-04 module (E) ← PLT-03
- Rest of Phase 1–2 ← PLT-04 / PLT-05 (see `docs/PLAN.md` §4)
- ASR-01 (A) real transcription, deferred to the reserve pool ← G2 (see `docs/PLAN.md` §4 "Deferred: ASR")
