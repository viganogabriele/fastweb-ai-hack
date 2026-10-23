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

## DATA-01c: stock facts, options, agent trace (lane E)

Built on the DATA-01b case above by `build_data01c.py`, for `act.options` (ACT-02), approval
(ACT-03), `ag.investigator` (AG-03) and the case detail (WEB-05). Rebuild from the repo root
after DATA-01b:

```sh
backend/.venv/bin/python data/fixtures/build_data01c.py
```

| Folder | Records | What it exercises |
|---|---|---|
| `stock/` | 12 `StockFact`s, all `basis` values | `I10919B00011` `999`/`742`, size `M`: `on_hand` from the EOD 2026-10-08 store export (MIL01 0, MIL02 3/0) and from the 2026-10-05 SAP projection for `IT10`; `atp` for the DC (0, receipt 2026-10-30); `sellable` with `qty=null` for the stores, because no store-level sellable/reservation export exists: unknown is not zero |
| `options/` | 4 `ActionOption`s on the D1 case | `hold` (ranking baseline), `verify_stock` (**recommended**), `replenish_dc` 4 units from `IT10` (**blocked**: ATP 0, sellable 2026-11-01) and the `transfer` MIL02→MIL01 of 2 units (**feasible**, not recommendable: two mandatory checks are `unknown`) |
| `traces/` | one `AgentTrace`, `mode=fixture` | The deterministic fallback path of RFC §4.8.1 on the RFC §4.8.2 tools, ending `finish(status=verify)` on the recommended option; `fallback_used=true`, no tokens |

The D1 numbers, all recomputed by the builder and re-derived by the test from the forecast fixture
and the size curve:

| Option | Unserved M at MIL01 | Unserved M at MIL02 | Leftover at MIL02 | Transport |
|---|---|---|---|---|
| `hold` | 2.49 units | 0.00 | 0.41 | – |
| `transfer` q=2 | 0.49 units | 1.59 | 0.00 | 16.21 EUR |

The transfer cuts the destination's unserved units by 2.00 and raises the donor's by 1.59: a net
gain of 0.41 units for 16.21 EUR, i.e. the whole donor surplus (3 units on hand against 2.59 units
of its own size-M demand). It is the **feasible isolated move** of the issue: every mandatory check
the sources can decide passes (identity, availability and freshness, the donor's minimum at
dispatch, lane/IBT, calendar, ETA before the case's due date, size curve, shared resources), so it
has legs, a lane, an ETA, a cost and simulated outcomes to render. It is **not recommendable**:
`reservations` and `quality_hold` are `unknown` because no store-level sellable, reservation or
quality export exists, and RFC §4.10 forbids recommending a movement with an unknown mandatory
control. The recommendation is the physical count: MIL01 dropped from 8 to 0 units of size M
between the two last snapshots with one recorded sale (`snapshot_bridge`), the donor count must be
confirmed and the DC projection is four days old.

**Donor protection, and the one reading to know.** `donor_protected` passes at dispatch (3 units
minus the 2 moved leave MIL02's minimum of 1) and the check states the horizon damage instead of
hiding it: the donor's own size-M demand is 2.59 units, so it sells out on 2026-10-12 and the
outcomes carry 1.59 lost units against 0.00 on hold. Read strictly as a floor over D+1..D+7, the
control could never pass here: 3 units against 2.59 of demand plus a minimum of 1 leave the donor
0.59 units short even with no transfer, so no integer quantity would qualify. The fixture therefore
records the floor the stock can keep and the additional damage RFC §4.10 asks to compare; a team
that prefers the strict reading flips this one status to `fail` and the movement becomes blocked
with no other change.

Conventions worth knowing when consuming these records:

- **Demand.** Colour `sales_baseline` of the vintage admissible at D, `/7` per open day of its ISO
  week (`series[].baseline` of the `forecast/` fixtures, identical to the ERP CSV). The D1 case has
  no numeric uplift, so `low`/`base`/`high` coincide, and `outcomes` repeats the same numbers.
- **Size curve.** Size M units over the colour units sold 2026-08-31..2026-10-04 on days size M
  opened in stock: MIL01 `13/58 = 0.2241`, MIL02 `12/38 = 0.3158` (RFC §4.9 "raccordo con la
  taglia"). POS `qty` is already signed, so `RETURN` lines are added as they come, and the export
  repeats some lines verbatim (`MIL02-260905-0006`): exact duplicates are counted once. The donor
  is judged with its own curve, and the check reports the window, the five POS files and a
  sensitivity: a flat 1/6 curve puts the destination's hold loss at 1.85 instead of 2.49 and
  changes no status.
- **Checks.** Names are stable (`identity_crosswalk`, `availability_freshness`/`availability_atp`,
  `reservations`, `quality_hold`, `min_presentation_safety`, `scarcity_assortment`,
  `donor_protected`, `lane_ibt`, `calendar_cutoff`, `eta_required_by`, `size_curve`,
  `shared_resources`); `mandatory=true` on every movement check, including the `unknown` ones.
  The transfer is the feasible path (no `fail`), the DC option the blocked one (`availability_atp`,
  `eta_required_by`), and `verify_stock` the only recommended option.
- **Check evidence.** `Check.source_refs` are `ArtifactRef`s. Where the evidence is a source file
  with no contract (lane matrix, minimum presentation, ATP columns, POS weeks) the ref is
  `kind="SourceFile"`, `id` = dataset uri plus the row locator (`.../lane_matrix_lead_time_cost.csv#lane_id=LN-1002-1001`),
  `version` = the file content hash: the same convention DATA-01b uses for `ForecastVintage` rows,
  with the locator kept so two rows of one file stay distinct.
- **Version hash.** `input_version_hash` covers the stored `input_refs` and the `source_refs`
  behind them, so an approval made against it is stale as soon as either changes (RFC §4.10).
- **Leg dates.** The transfer pickup is the lane's cutoff on D (MON-FRI, run at 10:35, same day),
  sellable at the next opening; arrival at 19:00 local is a stated assumption, not a lane field.
  The DC leg is dated from the sources: first `MON-SAT` loading day on or after the 2026-10-30
  receipt, at the 14:00 cutoff, plus the lane's 1 contract day, then the next opening.
- **Availability.** Store facts are known at the end of their local day, the DC projection at its
  `SNAPSHOT` instant; every record here is available at D 10:35 local or earlier. Later facts that
  confirm the story are *not* inputs: the IBT request of 2026-10-09 17:32 (created because the
  transfer happened anyway) and the 2026-10-12 ATP projection.
- **Stores.** Destination and donor are dev stores (`MIL01`, `MIL02`) plus the supplying DC
  `IT10`. `ROM01`, also addressed by the source email, is a hold-out store and has no record here
  (RFC §5.1).
