# Production pipeline demo

Run `make demo` from this branch. It rebuilds the recorded nine-store run offline,
then serves the real API on port 8000 and the redesign UI on port 5173. The first
build takes about a minute. Later starts reuse the database. No Fastweb key or
systems server is needed for replay.

`data/demo/current` selects the snapshot. Rebuilding a different snapshot preserves
older databases and their local decision ledgers. The recorded package is
`data/fixtures/runs/production-demo-20261022/`; its input profile is
`config/production_demo.yaml`.

## What the run contains

This is a synthetic dev rehearsal at `2026-10-22T20:00:00Z`, executed through the
installed production modules. It covers MIL01, MIL02, MUN01, PAR01, LON01, NYC01,
TYO01, SEL01 and SYD01. It is not a hold-out evaluation.

The input selection includes 18 existing emails in six languages, the W42
controlling workbook, ERP history, weather and Pulsewire exports. Two additional
emails state confirmed unfulfilled orders in units. A synthetic logistics calendar
supplies a planned departure cutoff for the London order. The profile declares
these additions; preparation writes them into the isolated source snapshot and
hashes them alongside the original files. Nothing changes `generated/sources/`.
No observation, case, forecast, option, trace or model response is preloaded.

The checked output contains:

- 21 documents and 125 observations with 125 exact, validated evidence spans.
- 63 current cases, 10 certain duplicate relations and one applied correction.
  Six cases show fewer origins than received documents.
- 850 baselines and 45 overlays. One overlay computes low/base/high demand for
  the supplemental London order; its cutoff is 23 October at 08:00 UTC. Other
  overlays retain their quantitative abstention reasons.
- 54 product insights, two investigator traces, one clarification draft and
  two reports. One investigator reaches its tool budget and exposes a verify
  fallback. No decision is preapproved.
- 1,045 daily store KPIs, 12 monthly points, three regions, six categories and
  3,288 social documents. The social reader removes 166 duplicate collections
  and excludes 238 malformed records.
- The API joins all 46 display products to the run's ERP stock and case scopes.
  Official catalog images remain illustrative and never enter demand inference.

The model recording made 32 Fastweb calls. Warehouse and logistics responses came
from the dataset's simulated systems through the ordinary adapter, with its stock,
availability and lane checks. The committed replay consumes those real response
envelopes without running the simulated server.

## Dashboard click path

1. Open Panoramica. Check the case counts, the London deadline, office filters
   and the sales series. All dates are relative to the selected run.
2. Switch to Mercato for monthly sales, same-period annual comparisons, regional
   and category momentum, sentiment and hashtags. Sales cover the run's nine
   stores; social is explicitly global listening context.
3. Open Prodotti, then a product. Stock comes from the latest comparable ERP
   snapshot known at the cutoff. Cases join by exact style, SKU or SKU-size.
4. Open the London AUREA black size 2 case dated 21 October for the calculated
   forecast and logistics deadline. Open the MIL01 unknown-product case dated
   9 October for the recorded clarification path.
5. Read Fonti, Report and Pipeline for evidence, citations and module outcomes.
   The operator can inspect proposals and choose a decision in the local ledger.

## Data quality and limits

Daily sales use the source's `net_sales_eur_bud`. Budget and category amounts use
the same store-day's implied budget FX, with the median of already available
currency observations when that day has no usable rate. Daily rows become
available at 06:00 the next morning in each store's timezone, or later if an
explicit posting timestamp says so. Comparisons end on the last common available
business day. Missing visitor counters stay null, including in conversion totals.

Current category sales reconcile with regional KPI sales exactly. The previous
28-day period differs by one cent after rounding. Last year's category series is
EUR 10,260.01 below the KPI series: four Paris Sundays contain return-only SKU
rows but no daily KPI row, plus a cent of rounding. Those returns remain in the
category totals. `data-quality.json` lists the dates and amounts.

Pulsewire records use the latest collection known at the cutoff, keyed by
`doc_id`. Both publication and collection timestamps must be available. The
sentiment labels are the vendor's automatic labels. Malformed records are
excluded rather than reconstructed from fragments.

The London weather export echoes GMT during British Summer Time. The connector
bounds calendar dates with the store's authoritative timezone and keeps a visible
diagnostic. Other feeds without coverage remain explicit abstentions. The overall
run is `degraded`, with no module errors. Forecast uplift is a policy scenario,
not a measured improvement in predictive accuracy.

## Reproduce or record a new run

`make demo-data` verifies the frozen input snapshot before replay. Its output hash
is compared with the recording in `replay-comparison.json`. The archived evidence
also includes API checks, source/config inventories and cache envelope hashes.

To record a changed input profile, use a new candidate directory and commit
executable changes first. Fastweb credentials are resolved by `Settings`; never
print the keys file.

```sh
backend/.venv/bin/python scripts/production_demo.py prepare \
  --candidate data/production_demo/new-candidate
backend/.venv/bin/python scripts/production_demo.py record \
  --candidate data/production_demo/new-candidate
backend/.venv/bin/python scripts/check_core_demo.py \
  --candidate data/production_demo/new-candidate
backend/.venv/bin/python scripts/production_demo.py replay \
  --candidate data/production_demo/new-candidate \
  --workspace data/production_demo/new-replay
```

Recording requires the dataset systems server (`make mocks`). `--keys-file` can
point to an existing private keys file when running from a worktree. A changed
snapshot receives new request identities; old recordings are never rewritten to
pretend they came from new requests.
