# Freeze runbook: how #211 produces the experiment record (REL-01d)

`scripts/freeze_record.py` computes every §3 binding in
[`holdout-evaluation-protocol.md`](holdout-evaluation-protocol.md) that can be computed
mechanically. It also closes the gap the protocol names: `FrozenRun` does not rehash
live sources, and the harness has no place for cache, code or lockfile fingerprints.
The script only takes paths and writes JSON. Each output is created exclusively under
`data/` and is never overwritten.

| Subcommand | Writes | Binds |
|---|---|---|
| `record` | the experiment record | candidate SHA/tree, clean-tree check (or recorded `--allow-dirty`), evaluator SHA and `eval/` tree, protocol hash, `freeze-g3` target if present; lockfiles, Python/uv/Node/npm versions; model ids and endpoints from `Settings` (allowlisted, never keys); RunSpec identities (run id, mode, models, prompt versions and file hashes, module ids/versions/enabled/params hash) and whether their `source_manifest_hash`/`config_hash` equal the recorded inputs; prompts and configs; consumed sources, source lists and input manifests; the scorers' live split/catalog/stock/sales inputs for `--window` (with warm-up), including the expected files that are *absent*; validated LLM/ASR/systems cache envelopes with per-entry hashes, aggregate digests, counts and recorded/fixture/unavailable status; exports with SHA-256 and counts per kind/origin/store; `make check` log, gate audit and other evidence files; reviewer and approval time |
| `append` | an addendum chained to the previous file by SHA-256 | harness bundle manifest digests, after `FrozenRun` has verified them; cross-checks that bundle exports are recorded exports and bundle sources are recorded sources; approval; post-freeze label/answer hash receipts **as values** |
| `verify` | an integrity log (optional) | rehashes every bound file in the chain, flags new cache entries, flags expected-absent inputs that have appeared, re-verifies bundles; exits 1 on drift |

The script refuses `.env`, `.secrets/`, `generated/ground_truth/`, `generator/`,
`eval/labels/`, `email_context` and `*_notes.md`, before and after resolving links. It
never opens labels. Lane A computes label hashes with `eval.reading.load_labels` after
annotation, and #211 appends them with `--label-sha NAME=SHA256`. A RunSpec mismatch
(`matches_recorded_inputs: false`) is reported rather than refused: the record binds
whatever was consumed, and the reviewer decides. Runtime, HEAD and dirty-tree
differences at `verify` time are warnings, not drift.

## Command sequence

Run from the repository root after `make setup`. `$C` is the reviewed, merged commit.
`$E` is a new experiment directory. Each name below is used once; never reuse one to
retry.

```sh
set -o pipefail
P=backend/.venv/bin/python
E=data/experiments/freeze-g3-r1
export PATH=/home/dev/.cache/ffmpeg-bin:$PATH   # only where no system ffmpeg exists

# 1. Candidate SHA: reviewed main commit, clean tree.
git fetch origin && git checkout --detach "$C"
test -z "$(git status --porcelain --untracked-files=all)"

# 2. make check log on exactly that commit.
mkdir -p "$E" data/core_demo/check-tmp
TMPDIR="$PWD/data/core_demo/check-tmp" make check 2>&1 | tee "$E/make-check.log"

# 3. Exports: REL-01c `scripts/run_holdout.py` (owned by that task) writes per-bundle
#    directories with predictions.json, cases.json, options.json and the
#    newline-separated repository-relative source list it consumed.
#    X_READING / X_LEAD / SOURCE_LIST / RUN_SPEC below are its outputs.

# 4. Experiment record (fails if HEAD != $C, the tree is dirty or a cache entry is invalid).
$P scripts/freeze_record.py record --output "$E/freeze-record.json" \
  --candidate-sha "$C" \
  --source-list "$SOURCE_LIST" --run-spec "$RUN_SPEC" \
  --window 2026-08-31 2026-10-21 \
  --cache llm=data/llm_cache --cache systems=data/systems_cache \
  --component asr=unavailable:"<reason, or pass --cache asr=DIR>" \
  --exports reading="$X_READING" --exports lead="$X_LEAD" \
  --make-check-log "$E/make-check.log" --gate-audit docs/release-gate-audit.md \
  --evidence core_replay=<#115 evidence path> --evidence safety=<#123 evidence path> \
  | tee "$E/freeze-record.stdout.json"

# 5. Harness bundles (protocol §5.1 wrapper or `python -m eval freeze`), one fresh
#    path per bundle; save each printed manifest digest.
#    B_READING, SHA_READING, B_LEAD, SHA_LEAD

# 6. Bind the bundles in an addendum (re-verifies them and cross-checks the record).
$P scripts/freeze_record.py append --record "$E/freeze-record.json" \
  --output "$E/freeze-record.001-bundles.json" \
  --bundle "$B_READING=$SHA_READING" --bundle "$B_LEAD=$SHA_LEAD"

# 7. Integrity check of every bound file against the live tree.
$P scripts/freeze_record.py verify \
  --record "$E/freeze-record.json" "$E/freeze-record.001-bundles.json" \
  --output "$E/integrity-001.json"

# 8. Human review in #211 (record SHA-256 from step 4 stdout, bundle digests, integrity
#    log). After approval, append it, then tag the reviewed commit, never a branch.
$P scripts/freeze_record.py append \
  --record "$E/freeze-record.json" "$E/freeze-record.001-bundles.json" \
  --output "$E/freeze-record.002-approval.json" \
  --reviewer "<name>" --approved-at "<aware ISO timestamp>"
git tag -a freeze-g3 "$C" -m "G3 freeze, record $E/freeze-record.json" && git push origin freeze-g3
```

After the freeze: before each scoring run (#126/#127/#128), repeat step 7 with a new
`--output` name, and append label receipts once lane A has written the annotations:
`append --record <whole chain> --output "$E/freeze-record.003-labels.json"
--label-sha reading_holdout=<sha256 from load_labels>`. Keep the record chain outside
the bundles, link it from #211, and preserve failed outputs (protocol §8).

## What the record cannot certify

The record proves file identity at recording time, not row-level availability, the
time a producer chose its inputs, or that a component behaved correctly. Component
status comes from the supplied caches and RunSpec mode. An explicit `--component`
declaration overrides it and is marked `declared: true`. The DEMO-02 dev candidate
under `data/fixtures/runs/core-dev-20261023/` is a smoke target only. It has no
predictions/cases/options exports, and recording it is not a freeze.
