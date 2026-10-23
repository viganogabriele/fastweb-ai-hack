#!/usr/bin/env sh
# Rebuild the committed DEMO-02 candidate (data/fixtures/runs/core-dev-20261023) into a
# fresh database, offline: no keys, no mock server, networking denied (~30 s).
# Run from the repo root. `data/demo/current` then points at the replay attempt;
# `make demo` serves it. Delete data/demo/ to rebuild after code changes.
set -eu

assets="$PWD/data/fixtures/runs/core-dev-20261023"
demo="$PWD/data/demo"
py="$PWD/backend/.venv/bin/python"

if [ -e "$demo/current/data/tesseract.db" ]; then
  echo "demo data ready: $demo/current (rm -rf data/demo to rebuild)"
  exit 0
fi

rm -rf "$demo"
mkdir -p "$demo/tmp"
# The shared /tmp can run out of quota during replay (scripts/core_demo.md).
export TMPDIR="$demo/tmp"

"$py" scripts/prepare_core_demo.py \
  --output "$demo/candidate" \
  --code-version 38fe618a91a9d4f573e96fc2ec3cde2ee6ec8ebe \
  --case-id case-mil01-i10919b00011-20261008 \
  --case-id case-mil01-unknown-20261009 >/dev/null
cmp "$demo/candidate/run-spec.json" "$assets/run-spec.json"

"$py" scripts/replay_demo.py \
  --run-spec "$assets/run-spec.json" \
  --sources "$demo/candidate/sources" \
  --config "$demo/candidate/config" \
  --cache "$assets/llm_cache" \
  --systems-cache "$assets/systems_cache" \
  --decisions "$assets/decisions.json" \
  --workspace "$demo/replay" >"$demo/replay.json"

attempt=$("$py" -c 'import json, sys; print(json.load(sys.stdin)["attempt_id"])' <"$demo/replay.json")
ln -s "replay/$attempt" "$demo/current"
echo "demo data ready: $demo/current"
