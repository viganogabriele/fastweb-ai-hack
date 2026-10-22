# Fixtures

Hand-labelled artifacts for the seams in `docs/PLAN.md` §3. Consumers build against them until
the real producer lands; `tessera fixtures load` (PLT-03) loads them in `FIXTURE_MODE`.

Each JSON file is a list of records `{"kind": "<contract class>", "payload": {...}}`, where
`payload` validates against `tessera.core.contracts.<kind>`. Fixtures use only dev stores and
`generated/sources/`.

## DATA-01a: documents and observations (lane A)

`documents/<doc_id>.json` holds one `SourceDocument` and its `Segment`s; `observations/<doc_id>.json`
the `Observation`s read from that document. Documents come from real dev `.eml` files through the
ING-02 parser; observations are written by hand in `build_data01a.py`. Rebuild from the repo root:

```sh
backend/.venv/bin/python data/fixtures/build_data01a.py
```

| Case (`meta.fixture_case`) | Source email | What it exercises |
|---|---|---|
| `d1_positive` | `MIL01/20261009_1035_MIL01.eml` | D1: cardigan logo M out of stock (exact 0) + vague unmet demand |
| `duplicate` | `MIL01/20261002_2112_MIL01.eml`, `..._2113_MIL01_dup.eml` | Same text sent twice, different hash and Message-ID: 7 Maire requests must count once |
| `correction` | `MIL01/20260918_2115_MIL01.eml`, `..._2207_MIL01_corr.eml` | Reply corrects net sales 58,0k → 85,0k; `parent_document_id` links them |
| `forward` | `MIL01/20261001_1124_MIL01_fwd.eml` | Evidence in the quoted (forwarded) customer mail, `attribution=customer` |
| `ambiguous_mention` | `NYC01/20260906_1837_NYC01.eml` | "a sweatshirt": hoodie or crewneck, colour unknown (EN) |

Labels are **partial**: each email holds more facts than the ones labelled (traffic, top
sellers, customer profile...). Use these files to build and test seams, never as recall labels
for extraction (EVL-02 has its own annotations). A fact restated in the same email is one
observation with several evidences, not several observations.

Dedup, supersedes and linking are not encoded here: both copies and both sides of the correction
keep their own observation. Relations and links are DATA-01b (lane B).
