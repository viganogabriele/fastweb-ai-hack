# Offline evaluation (EVL-01)

This package is the only code allowed to read `generated/ground_truth/` (RFC §7.1).
The backend never imports it. It consumes a **frozen product export**, not a running
pipeline or database. `verify` records input hashes and artifact counts, with an empty
`metrics` object; scoring lives in the per-task commands below (EVL-04: §4).

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

## 4. Lead time vs baselines (EVL-04)

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
