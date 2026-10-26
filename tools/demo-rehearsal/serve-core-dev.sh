#!/usr/bin/env sh
# Serve the frozen core-dev-20261023 run for the DEMO-03 walkthrough: a fresh replay attempt
# (offline, no keys) on every call, backend on $API_PORT, web on $WEB_PORT. Run from the repo
# root after `make setup`. `make demo` serves the later production-demo run instead.
#
#   tools/demo-rehearsal/serve-core-dev.sh                 # synthetic scripted decision
#   tools/demo-rehearsal/serve-core-dev.sh decisions-operator.json
#
# Each call stops the backend it started before, so the decision beat starts undecided.
set -eu

decisions=${1:-decisions.json}
api_port=${API_PORT:-8000}
web_port=${WEB_PORT:-5173}
assets="$PWD/data/fixtures/runs/core-dev-20261023"
work="$PWD/data/core_demo/rehearsal"
py="$PWD/backend/.venv/bin/python"

# The [u] keeps pgrep from matching this script's own command line.
for pid in $(pgrep -f "[u]vicorn tesseract.api.main:app --app-dir backend --port $api_port" || true); do
  kill "$pid"
done

mkdir -p "$work/tmp"
export TMPDIR="$work/tmp"
if [ ! -f "$work/candidate/run-spec.json" ]; then
  "$py" scripts/prepare_core_demo.py --output "$work/candidate" \
    --code-version 38fe618a91a9d4f573e96fc2ec3cde2ee6ec8ebe \
    --case-id case-mil01-i10919b00011-20261008 --case-id case-mil01-unknown-20261009 >/dev/null
fi
cmp "$work/candidate/run-spec.json" "$assets/run-spec.json"
"$py" scripts/replay_demo.py --run-spec "$assets/run-spec.json" \
  --sources "$work/candidate/sources" --config "$work/candidate/config" \
  --cache "$assets/llm_cache" --systems-cache "$assets/systems_cache" \
  --decisions "$assets/$decisions" --workspace "$work/replay" >"$work/replay.json"
attempt=$("$py" -c 'import json, sys; print(json.load(sys.stdin)["attempt_id"])' <"$work/replay.json")
run="$work/replay/$attempt"

LLM_MODE=replay DATA_DIR="$run/data" SOURCES_DIR="$run/inputs/sources" CONFIG_DIR="$run/inputs/config" \
  nohup "$PWD/backend/.venv/bin/uvicorn" tesseract.api.main:app --app-dir backend --port "$api_port" \
  >"$work/backend.log" 2>&1 &
if ! curl -sf "http://localhost:$web_port" >/dev/null; then
  (cd web && TESSERACT_API_TARGET="http://127.0.0.1:$api_port" \
    nohup npx vite --port "$web_port" --strictPort >"$work/web.log" 2>&1 &)
fi
for _ in $(seq 60); do
  curl -sf "http://localhost:$web_port/api/health" >/dev/null && break
  sleep 1
done
"$py" -c 'import json, sys
d = json.load(open(sys.argv[1]))
print(d["attempt_id"], "output", d["output_sha256"][:16], "network", d["network_attempts"],
      "misses", len(d["cache_misses"]))' \
  "$work/replay.json"
echo "open http://localhost:$web_port/#/panoramica"
