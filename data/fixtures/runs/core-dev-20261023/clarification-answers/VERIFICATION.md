# OUT-02e verification: real-model contextual answers on the dev Core question

Status on 2026-10-23: **recorded with real models and replayed offline through the
answer API with zero cache misses and zero network attempts.** Part of #134. These
are recorded (`mode: recorded`, `product` namespace) envelopes, not DTO fixtures,
and are not loaded by `fixtures load`.

## What was answered

Parent: the published DEMO-02b Core run `core-dev-candidate` (recorded at
`38fe618`, dev stores only, clock `2026-10-22T20:00:00Z`), rebuilt offline from
`../llm_cache` and `../systems_cache` (artifact SHA-256 `4a111a0d…`). Its single
investigator-drafted, explicitly simulated clarification
`clarification:fadee7bd…` (version `1`) belongs to case
`case-mil01-unknown-20261009` (`v1`, MIL01, `verify`). It asks for the model,
colour and size of the product the store called "M" (observation
`obs-20261009-1035-mil01-1`, evidence "Anche 1 o 2 pezzi per colore, ce lo chiedono
in continuazione", quantity "1 o 2 pezzi per colore"). `answers.json` holds the three
allowed simulated answers, all received at `2026-10-22T22:20:00+02:00`, language
`it`, follow-up clock `2026-10-22T20:30:00Z`, each in its own declared scenario:

| Key | Answer text | Real-model contextual reading | Child outcome |
|---|---|---|---|
| `self-contained` | È il cardigan logo in taglia M, sia nero che blu. | `cardigan logo taglia M nero e blu` | linked to style `I10919B00011`; case `case-mil01-i10919b00011-20261022` `open` |
| `elliptical` | Cardigan logo. | `Cardigan logo M` | linked to style `I10919B00011`; same new case, `open` |
| `abstain` | Non saprei, chiedo alla collega e vi faccio sapere. | `null` (abstains) | original `M` retained, `unlinked`; case `case-mil01-unknown-20261022` stays `verify` |

In every child the corrected observation keeps its ID, its quantity
"1 o 2 pezzi per colore" and its evidence; it becomes available at the answer receipt
(20:20Z). The answer document yields no observation, no observation ID has two
current versions, and four `supersedes` relations exist: the target plus the
answered email's three other facts, which are carried exactly. The linker, cases,
forecast and options ran unchanged in the child. The D1 investigator reaches
the same six-tool budget fallback disclosed for the parent, and the old
unknown-case ID is absent in children. So all three children are honestly
`degraded`. No message is sent.

## Recording

`scripts/clarification_answers_demo.py record` is the trusted importer. It rebuilds
the parent offline, then registers each answer only in that private database.
It submits the answer and executes the follow-up with `LLM_MODE=record`. Models:
Gemma (`google/gemma-4-26B-A4B-it`) for extraction, linking and the contextual
reading; GLM (`glm-5.3-flash`) for the investigator. Systems reads came from the
dataset mock server (`make mocks`). Keys were read only through `Settings`, and
the envelopes contain no credentials or request headers.

One session (`recording-evidence.json`, executing `9d50277`, LLM concurrency 4,
one client per follow-up), `complete: true`, parent hash unchanged. Totals:
**53 LLM envelopes, 36 systems envelopes**, each produced by a real HTTP-200 call
and each used (checked by `tests/core/test_clarification_answers_replay.py`).
`asset-manifest.json` hashes every file. The child RunSpec keeps the parent's
frozen `code_version` (`38fe618…`); the executing SHA is the one above. The same
three answers had first been recorded against the superseded `f1d7923` candidate
with the same readings; those envelopes were discarded when DEMO-02b replaced it.

An earlier attempt on the pre-fix code is the evidence for two OUT-02e changes in
`modules/agents/contextual_answers.py`. The prompt and the cache key are unchanged:

1. The real reading `cardigan logo taglia M nero e blu` failed lexical support only
   because of the connective `e`. Bare connectives (`e ed and und et y`) are now
   accepted; they cannot introduce a product, size or number.
2. A fresh child read of the answered email widened the demand span under the
   same positional ID, and the guard refused it. Answered documents are now carried
   from the parent instead of being re-read (see `answer_registry.md`).

## Offline replay (no credentials, no mock server, networking denied)

```sh
mkdir -p data/core_demo/check-tmp
TMPDIR="$PWD/data/core_demo/check-tmp" backend/.venv/bin/python \
  scripts/clarification_answers_demo.py replay --workspace "$PWD/data/core_demo/answers-replay"
```

It prepares the DEMO-02 inputs from `generated/sources`, rebuilds the parent, and
merges these envelopes into the attempt. It registers only answers whose
recording completed. Then, through the real HTTP API, it lists
`GET …/registered-answers` and posts each preset with a new idempotency key, then
retries it. `replay-evidence.json` is one such run:

- status `passed`, network attempts 0, LLM and systems cache misses `[]`, 3 presets;
- parent artifact SHA-256 before = after = recorded =
  `4a111a0d0255ba4aac6ae95adcbf87200b2a58ed4f044a871bb7822ff9e28bfe`;
- child artifact SHA-256 equal to the recording:
  - self-contained `e4d549fe60c78a1a284e9356a4320ac051bb58133d8a2f240c13fc3c175ebeaa`
  - elliptical `16be1eb19e58501792c6aeb2883b16d1ff29c5a7c9e867b21a76aed921a806a6`
  - abstain `e3b7b44558b2f89ac9917ad6898c186402c6074af7ab4dc3721e9926b002a36e`
- each retry returns the identical job; free text returns 424. A registered answer
  at an unrecorded clock is accepted (202), but its child fails unpublished, with
  explicit misses.

`--register-only` stops after trusted registration and prints the attempt's
`data_dir`. Serve that directory for the UI with `LLM_MODE=replay DATA_DIR=<data_dir>
SOURCES_DIR=<attempt>/inputs/sources CONFIG_DIR=<attempt>/inputs/config
backend/.venv/bin/uvicorn tesseract.api.main:app`. Then submit the listed presets.

## Limits

- Dev synthetic stores only, one question, three answers. This is not a hold-out
  metric or a statistical comprehension score. Lexical support does not prove
  negation handling.
- Only the answered email is carried. The other 11 emails are re-read by the
  frozen pipeline with fresh model calls, so a child can differ from its parent
  outside the answer: 68/84/78 observation records against the parent's 82.
  Compare a child with its own recording, not observation-by-observation with the
  parent.
- The case anchors move to the answer receipt day (`…-20261022`) because the
  corrected observation's availability is the receipt time; the original quantity
  and evidence are unchanged. No quantitative uplift is claimed: the answer's
  colours are not new counts.
- Any other answer text, receipt time, scenario or clock needs its own recording;
  free text in a recorded parent is refused (424).
