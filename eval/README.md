# Offline evaluation (EVL-01)

This package is the only code allowed to read `generated/ground_truth/` (RFC §7.1).
The backend never imports it. It consumes a **frozen product export**, not a running
pipeline or database. `verify` records input hashes and artifact counts, with an empty
`metrics` object; scoring lives in the task commands below (EVL-02: §4, EVL-04: §5,
EVL-03: §6).

Run commands below from the repository root with `backend/.venv/bin/python`.
There are no additional dependencies and no answer-key access during tests.

## 1. Run the product with isolated inputs

```sh
backend/.venv/bin/python -m eval product -- -m tessera.cli --version
# API, when needed:
backend/.venv/bin/python -m eval product -- -m uvicorn tessera.api.main:app --port 8000
```

The launcher installs Linux Landlock restrictions **before Python starts**. It
allows reads from `backend/`, `generated/sources/`, `config/`, `data/`, `.env`, and
the interpreter/system runtime. Reads of `generated/ground_truth/`, `generator/`,
`eval/` and other repository paths are denied by the kernel, including `open()`,
native reads, symlinks and child processes. The mock server remains a separate
process, launched with `make mocks`; do not import its code.

Requires Linux with Landlock enabled, on x86_64 or aarch64; unsupported hosts fail
closed. This is read isolation, not a complete security sandbox: it does not
restrict network or writes. Use a fresh `data/` namespace, free of oracle material,
for product runs. `make dev` remains a development command and does not install
these restrictions; use this launcher for evaluated product runs.

## 2. Preselect the protocol, then freeze the run

Before running holdout, fix the source sample, model versions, prompts, aliases,
parameters, temporal origins and store/SKU universe, including no-alert examples.
Split membership follows RFC §5.1; unlisted stores are not implicitly dev stores.
Create `data/protocol.json`, for example:

```json
{
  "run_id": "synthetic-example",
  "split": "dev",
  "stores": ["MIL01"],
  "origins": ["2026-10-08T20:00:00+02:00"],
  "universe": [{"store_id": "MIL01", "sku": "SYNTHETIC-999"}],
  "sampling_criterion": "All documents in a preselected store/day, including no alerts",
  "models": {"extract": "record-the-exact-model-version"},
  "parameters": {"threshold": 0.8}
}
```

The SKU above is a synthetic example, not a dataset label. Export predictions,
cases and options as three JSON arrays of objects under `data/`. Empty arrays
are valid. Records remain opaque until PLT-02 and the scoring tasks define DTOs.

```sh
backend/.venv/bin/python -m eval freeze data/frozen/run-001 \
  --protocol data/protocol.json \
  --predictions data/exports/predictions.json \
  --cases data/exports/cases.json \
  --options data/exports/options.json \
  --source generated/sources/erp/master_data/stores.csv \
  --configuration config/pipeline.yaml
```

Use existing configuration paths; the scaffold may not yet contain
`config/pipeline.yaml`. Repeat `--source` for **every selected input file**, and
`--configuration` for every config, prompt, alias and split file used in the run.
Configuration paths must be under `config/` or `backend/`. Source files must be
under `generated/sources/`, checked after resolving symlinks. No directory crawl
or oracle discovery is performed. Row-level availability remains the product's
responsibility; a file hash does not establish no look-ahead.

The bundle copies artifacts and configuration snapshots and records source paths
and SHA-256 hashes in `manifest.json`. Existing bundles are never overwritten.
Save the printed **manifest SHA-256 outside the bundle before oracle access**
(for example, in the frozen experiment record). The harness checks integrity
against that digest; it cannot prove when a researcher selected or ran inputs.

## 3. Verify, then read explicitly selected answer keys

```sh
backend/.venv/bin/python -m eval verify data/frozen/run-001 \
  --sha256 '<previously recorded manifest SHA-256>' \
  --key scenario/events.json \
  --output data/run-001-evaluation-inputs.json
```

`verify` checks the manifest and all snapshots before opening an answer key. It
reads only the requested key paths, hashes them and writes a receipt using
exclusive creation, so previous records are preserved. No oracle contents appear
in the receipt. For future scorers, `FrozenRun.read_answer_key()` returns bytes;
callers parse their chosen CSV/JSON format. Traversal and symlink escapes from the
oracle root or bundle are rejected. Scorers must stay in `eval/`, never provide
product inputs, and report exclusions and limits required by RFC §7.2.

## 4. EVL-02: reading eval on labelled dev files

`eval/labels/reading_dev_v1.yaml` holds hand-written claim-level labels for a dev sample
fixed before labelling: every mail of the 12 dev stores sent on 2026-09-20 or 2026-10-08
(26 files, it/fr/es/en/de/ja/ko/zh). Labels come from the email text and the answer keys
(misnamed products resolved to what the store meant), so this file is answer material:
product code, prompts and fixtures never read it. Matching rules and metrics are in the
docstring of `eval/reading.py`. Hold-out (EVL-02H) needs its own labels, written once and
scored once after the freeze.

```sh
P=backend/.venv/bin/python
D=data/eval/evl02
# 1. Sample list only (file names, no labels) for the product, then the frozen RunSpec.
$P -m eval reading-sample --files-out $D/files.txt
(cd backend && .venv/bin/python -m tessera.modules.ingestion.reading_export spec \
  --files ../$D/files.txt --as-of 2026-10-09T04:00:00+00:00 --run-id evl02-dev-spec \
  --code-version "$(git rev-parse --short HEAD)" --out ../$D/run_spec.json)
# 2. Record once (Fastweb keys; outside the launcher, which cannot read .secrets/).
(cd backend && LLM_MODE=record .venv/bin/python -m tessera.modules.ingestion.reading_export \
  run --run-spec ../$D/run_spec.json --run-id evl02-dev-record --out ../data/exports/evl02-record)
# 3. Evaluated export: replay under kernel read isolation.
$P -m eval product -- -m tessera.modules.ingestion.reading_export run \
  --run-spec ../$D/run_spec.json --run-id evl02-dev-replay --out ../data/exports/evl02-dev
# 4. Freeze, keep the printed SHA-256 outside the bundle, then score.
$P -m eval reading-sample --run-spec $D/run_spec.json --protocol-out $D/protocol.json
$P -m eval freeze data/frozen/evl02-dev --protocol $D/protocol.json \
  --predictions data/exports/evl02-dev/predictions.json \
  --cases data/exports/evl02-dev/cases.json --options data/exports/evl02-dev/options.json \
  $(sed 's#^#--source generated/sources/store_emails/#' $D/files.txt) \
  --configuration config/aliases.yaml --configuration config/domain.yaml \
  --configuration backend/prompts/extract_observations.v1.md \
  --configuration backend/prompts/link_choice.v1.md
$P -m eval reading data/frozen/evl02-dev --sha256 '<recorded SHA-256>' \
  --output data/evl02-dev-reading.json
```

The result lists N per language, precision, recall on required labels (and on all labels),
redundant matches, negation mismatches, link errors among accepted links with accepted,
abstention and not-product rates, every false positive, missed label and link error, and the
excluded or unread files. Quantities and periods are not scored.

## 5. Lead time vs baselines (EVL-04)

```sh
# Baselines only, all dev stores (no product run needed):
backend/.venv/bin/python -m eval lead-time --split dev --output data/evl04-baselines.json
# A verified frozen run: its protocol fixes the stores, its cases are the pipeline alerts.
backend/.venv/bin/python -m eval lead-time --bundle data/frozen/run-001 \
  --sha256 '<recorded manifest SHA-256>' --output data/run-001-lead-time.json
```

Defaults: period 2026-08-31 → 2026-10-21 (`--start/--end`). It reads `scenario/events.json`
and, for noise, the email answer-key indexes; nothing else from the oracle.

- **Unit**: planted event × evaluated store overlapping the period. Store-wide events match only
  store-scope alerts; product events match alerts whose SKUs (and sizes, when both name them)
  intersect the event's; alert and event directions must agree. Rules: `eval/lead_time.py`.
- **Pipeline**: each exported `Case` with a resolved store and scope, any status, at
  `first_available_at`. `unknown` type or scope = verify request; `customer_profile` =
  marketing context. Both are counted, not scored as alerts.
- **Baselines** (`eval/baselines.py`, sources only): stock policy (on-hand of a SKU-size falls
  to ≤ threshold) and sales detector (3-day Poisson surprise vs the previous 28 days, per SKU
  upward and per store both ways). ERP data of day B is used from B + 1 20:00 local.
- **Thresholds**: only a dev bundle calibrates each baseline to the most sensitive grid setting
  whose false alerts per store-day do not exceed the pipeline's (RFC §7.2); if none qualifies,
  the strictest setting is flagged `within_pipeline_load: false`. Baseline-only and hold-out runs
  use the fixed defaults and do not inspect hold-out grid outcomes for tuning.
- **Output**: per unit the first alert of each method; `t_baseline - t_pipeline` in days when
  both detect, a lower bound `T_end - t_pipeline` when only the pipeline does, and "not
  detected by T_end" counts; false alerts per store-day; `decision_due_at - t_pipeline`;
  duplicate/correction/forward/noise mails behind cases, folded copies and fragmented units.

False alerts are relative to planted events, so real unplanned stock-outs count against the
stock baseline; broad events (a season group, a style everywhere) can be matched by chance.
Units overlap in time and are not independent replicates. Hold-out is EVL-04H.

## 6. Forecast errors (EVL-03)

Before freezing, add the store's IANA timezone to **each** universe entry and fix
the scenario in the protocol. For example:

```json
{
  "universe": [
    {"store_id": "MIL01", "sku": "SYNTHETIC-999", "timezone": "Europe/Rome"}
  ],
  "forecast": {"scenario": "base", "scenario_id": "historical"}
}
```

These fields supplement the complete protocol in section 2. The universe must
include no-alert and decoy products before oracle access. The scorer does not
derive its sample from cases or labels. Duplicate universe entries/origins fail.

Export `ForecastAdjustment` objects into `predictions.json`: `fc.baseline` for
every selected origin × store × SKU-colour, plus the stored `fc.overlay` records.
Native DTOs use `computed_at` as their temporal origin, matching the current
producers' use of the run's `as_of`. When export computation time differs, wrap
each DTO as `{"as_of": "<aware run origin>", "payload": {"producer": "fc.baseline", ...}}`.
The explicit origin must be the run's historical clock, not the export time.
Freeze these exports with the existing `freeze` command before opening the oracle.

```sh
backend/.venv/bin/python -m eval forecast data/frozen/run-001 \
  --sha256 '<previously recorded manifest SHA-256>' \
  --output data/run-001-forecast-errors.json
```

The scorer verifies all bundle hashes, validates frozen choices and predictions,
then reads only `demand/true_demand_window.csv` through `FrozenRun.read_answer_key`.
`--key` can specify another CSV with the same schema: `date,store_id,sku,demand_units`.
The output records the manifest hash, full frozen protocol and oracle file hash.
It uses exclusive creation; previous evaluation records cannot be overwritten.
No actual holdout metrics have been produced as part of this implementation.

- H=1, 3 and 7 are reported separately, starting the next **store-local** day after
  each origin. Every target day must be present and nonblank. An incomplete target
  horizon is `pending`; missing days never become zero or a shorter horizon.
- Target is realised `demand_units` at daily SKU-colour grain, compared with the
  overlay's **latent** demand. Expected demand columns and recorded sales are not
  substituted. Scenarios are conditional hypotheses, not calibrated forecasts.
- The frozen `low`, `base` or `high` scenario is used for every scored point.
  More than one computed overlay for the same origin/store/SKU is rejected.
  An overlay must agree with the baseline's vintage and daily baseline values.
  Nonhistorical scenarios (including synthetic extensions) are rejected.
- No overlay, or an overlay marked `unchanged`/`not_estimable`, uses the baseline.
  Those products remain in the comparison. Missing daily baselines or incomplete
  computed overlays are explicitly `unscorable`; both comparator metrics use the
  same remaining sample, with exclusions and coverage visible in the report.
- WAPE is `sum(abs(actual - forecast)) / sum(actual)` across all scored daily
  points, expressed as a ratio. MAE uses the same pointwise errors divided by
  `n_days`; opposite daily errors do not cancel. Zero actual volume gives
  `wape: null`, with MAE, volumes and counts still reported. An empty sample also
  has `mae: null`. Negative/nonfinite quantities and duplicate oracle days fail.
- Each horizon reports eligible, mature, pending, unscorable and scored origin
  counts; adjusted, abstained and no-alert counts; prediction coverage
  (`scored / mature`) and adjustment coverage (`adjusted / scored`). Undefined
  coverage is `null`. Forecast records outside the frozen universe/origins are
  ignored and counted; future/unknown input availability inside the sample fails.

Temporal origins and their horizons can overlap; their daily observations are not
independent replications. Incomplete prediction coverage limits any comparison
claim. Keep evaluation outputs away from subsequent product inputs and do not
tune prompts/policy against holdout results.


## Checks

```sh
backend/.venv/bin/python -m unittest discover -s eval/tests -v
backend/.venv/bin/ruff check --config backend/pyproject.toml eval
backend/.venv/bin/ruff format --check --config backend/pyproject.toml eval
make check
```

`backend/tests/eval/test_suite.py` also runs these oracle-free regressions in a
separate process during `make check` and CI. All answer material in tests is
temporary synthetic sentinel data. No actual holdout evaluation has been run.
