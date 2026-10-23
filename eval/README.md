# Offline evaluation (EVL-01)

This package is the only code allowed to read `generated/ground_truth/` (RFC §7.1).
The backend never imports it. It consumes a **frozen product export**, not a running
pipeline or database. `verify` records input hashes and artifact counts, with an empty
`metrics` object; scoring is done by the task scorers (EVL-02 reading, §4).

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
