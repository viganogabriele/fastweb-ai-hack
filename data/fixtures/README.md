# Fixtures

Hand-labelled artifacts for the seams in `docs/PLAN.md` §3. Consumers build against them until
the real producer lands; `tessera fixtures load` (PLT-03) loads them in `FIXTURE_MODE`.

Each JSON file is a list of records `{"kind": "<contract class>", "payload": {...}}`, where
`payload` validates against `tessera.core.contracts.<kind>`. Fixtures use only dev stores and
`generated/sources/`.

`voice/` is the exception: it holds audio and its sidecars, not stored contract records, and each
note is a folder (`voice/<note_id>/`) so this loader never reads its JSON. Layout and sidecar in
`voice/README.md`; `src.voice` reads it.

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

## DATA-01b: links, relations, cases, forecast, report (lane B)

Built on the DATA-01a records above by `build_data01b.py` (hand labels for links, relations and
cases; baselines computed with FC-01 `disaggregate`). Rebuild from the repo root after DATA-01a:

```sh
backend/.venv/bin/python data/fixtures/build_data01b.py
```

| Folder | Records | What it exercises |
|---|---|---|
| `links/link-*.json` | one `EntityLink` per DATA-01a observation | `linked` at style (cardigan logo, both colours), SKU (Maire nera) and SKU-size (Tib blu 4); `ambiguous` "a sweatshirt" with tied candidates (crewneck, hoodie); `not_product` for the net sales figures. Scores are 0–1 string-match scores, not probabilities |
| `links/relations.json` | `EvidenceRelation`s | `duplicates`: the copy's Maire requests → the original (count once). `supersedes`: corrected net sales → the original fact, not the whole email |
| `cases/` | 4 `Case`s | D1 cardigan M (style scope, `open`, high); Maire black from two copies (`n_documents=2`, `n_origin_groups=1`); Tib quality defect (SKU-size); NYC01 ambiguous return (`scope=unknown`, `verify`). Owner from `config/domain.yaml` |
| `forecast/` | 3 `ForecastAdjustment`s, `unchanged` | D+1..D+7 daily baseline of the fixture run: D is the run's `as_of` in the store's time zone, the vintage is the latest one out by `as_of` (run date + 1 day 06:00 local), and `available_at` includes the vintage's publication; vague demand, a stock-out and a request count give no numeric uplift, so every scenario equals the baseline |
| `reports/` | 1 `Report`, view `by_office` | Brief per owner at the fixture run's `as_of` (latest fixture `available_at`); every number is rendered from a citation `(ref, field, unit, scope, period)` and the tests check the rendered value against the cited record and the sources; `input_version_hash` is the SHA-256 of the sorted input refs |

Every derived record is available at the latest `available_at` of its inputs and carries their
`source_refs`. The baseline is referenced as `ForecastVintage` (`<file stem>/<store>/<sku>`,
version = run date): a source row, not a stored artifact.
