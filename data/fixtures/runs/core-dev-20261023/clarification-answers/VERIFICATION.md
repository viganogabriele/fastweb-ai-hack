# OUT-02e verification: real-model contextual answers on the dev Core question

Status on 2026-10-23: **recorded with real models and replayed offline through the
answer API with zero cache misses and zero network attempts.** Part of #134. These
are recorded (`mode: recorded`, `product` namespace) envelopes, not DTO fixtures,
and are not loaded by `fixtures load`.

## What was answered

Parent: the published DEMO-02 Core run `core-dev-candidate` (dev stores only,
clock `2026-10-22T20:00:00Z`), rebuilt offline from `../llm_cache` and
`../systems_cache`. Its single investigator-drafted, explicitly simulated
clarification `clarification:1a60b187…` (version `1`) belongs to case
`case-mil01-unknown-20261009` (`v1`, MIL01, `verify`). It asks for the full name of
the product the store called "M" (observation `obs-20261009-1035-mil01-1`, evidence
"ce lo chiedono in continuazione", quantity vague). `answers.json` holds the three
allowed simulated answers, all received at `2026-10-22T22:20:00+02:00`, language
`it`, follow-up clock `2026-10-22T20:30:00Z`, each in its own declared scenario:

| Key | Answer text | Real-model contextual reading | Child outcome |
|---|---|---|---|
| `self-contained` | È il cardigan logo in taglia M, sia nero che blu. | `cardigan logo taglia M nero e blu` | linked to style `I10919B00011`; case `case-mil01-i10919b00011-20261022` `open` |
| `elliptical` | Cardigan logo. | `Cardigan logo M` | linked to style `I10919B00011`; same new case, `open` |
| `abstain` | Non saprei, chiedo alla collega e vi faccio sapere. | `null` (abstains) | original `M` retained, `unlinked`; case `case-mil01-unknown-20261022` stays `verify` |

In every child the corrected observation keeps its ID, the vague quantity
"in continuazione" and its evidence; it becomes available at the answer receipt
(20:20Z). The answer document yields no observation, no observation ID has two
current versions, and three `supersedes` relations exist: the target plus the
answered email's two other facts, which are carried exactly. The linker, cases,
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

- Session 1 (`recording-evidence-initial.json`, code `b1252b5`): self-contained and
  elliptical complete; abstain's investigator fell back at its second GLM turn
  because one LLM client deadline was shared by all three follow-ups. Fixed in
  `4e247a0` (one client per follow-up).
- Session 2 (`recording-evidence.json`, code `4e247a0`) is seeded with session 1's
  envelopes. Self-contained and elliptical reproduce bit-for-bit as cache hits
  (same child artifact hashes); abstain made 3 new GLM calls and 2 new systems reads.
  `complete: true`.

Totals: **58 LLM envelopes, 36 systems envelopes**. Each has a real HTTP-200
provider trace in one of the two evidence files, and each is used by the final
recording (checked by `tests/core/test_clarification_answers_replay.py`).
`asset-manifest.json` hashes every file. The child RunSpec keeps the parent's
frozen `code_version` (`f1d7923…`); the executing SHAs are the ones above.

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
  `72344004ec7fafc09d53e6add68c8eb3457a90e41916e46c0de64693b86dab23`;
- child artifact SHA-256 equal to the recording:
  - self-contained `49174e52de360388bc1477523fed0e65111b69b0e849dfe7f0a921b8855ce976`
  - elliptical `25bb719a6711183df2c31f5efafa3cc0d514a7e713079c2250840eabae2a5926`
  - abstain `da21c85ff6c66fb654ad87a2d7315dd9e53e267ef816eff4c24baf166d1856c2`
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
  outside the answer: 79/82/75 current observations against the parent's 81.
  Compare a child with its own recording, not observation-by-observation with the
  parent.
- The case anchors move to the answer receipt day (`…-20261022`) because the
  corrected observation's availability is the receipt time; the original quantity
  and evidence are unchanged. No quantitative uplift is claimed: the answer's
  colours and the old "1 o 2 pezzi" are not new counts.
- Any other answer text, receipt time, scenario or clock needs its own recording;
  free text in a recorded parent is refused (424).
