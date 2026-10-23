# Offline evaluation (EVL-01)

This package is the only code allowed to read `generated/ground_truth/` (RFC §7.1).
The backend never imports it. It consumes a **frozen product export**, not a running
pipeline or database. `verify` records input hashes and artifact counts, with an
empty `metrics` object. These are not results. EVL-03 adds the optional `forecast`
scorer described below; it never runs a product module or selects a scenario from outcomes.

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

## 4. Forecast errors (EVL-03)

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
