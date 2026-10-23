#!/usr/bin/env sh
# Rebuild the recorded production demo offline. Preserve older snapshots and ledgers.
set -eu

assets="$PWD/data/fixtures/runs/production-demo-20261022"
demo_root="$PWD/data/demo"
py="$PWD/backend/.venv/bin/python"
identity=$("$py" -c 'import hashlib, sys; print(hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest()[:16])' "$assets/run-spec.json")
demo="$demo_root/production-$identity"

if [ ! -e "$demo/current/data/tesseract.db" ]; then
  mkdir -p "$demo/tmp"
  export TMPDIR="$demo/tmp"
  if [ ! -f "$demo/candidate/run-spec.json" ]; then
    code_version=$("$py" -c 'import json, sys; print(json.load(open(sys.argv[1]))["code_version"])' "$assets/run-spec.json")
    "$py" scripts/production_demo.py prepare \
      --candidate "$demo/candidate" --profile "$assets/profile.yaml" \
      --code-version "$code_version" >"$demo/prepare.json"
  fi
  cmp "$demo/candidate/run-spec.json" "$assets/run-spec.json"
  "$py" scripts/replay_demo.py \
    --run-spec "$assets/run-spec.json" \
    --sources "$demo/candidate/sources" --config "$demo/candidate/config" \
    --cache "$assets/llm_cache" --systems-cache "$assets/systems_cache" \
    --workspace "$demo/replay" >"$demo/replay.json"
  attempt=$("$py" -c 'import json, sys; print(json.load(sys.stdin)["attempt_id"])' <"$demo/replay.json")
  ln -s "replay/$attempt" "$demo/current"
fi

"$py" - "$demo_root/current" "production-$identity/current" <<'PY'
import pathlib
import sys
link = pathlib.Path(sys.argv[1])
if link.exists() and not link.is_symlink():
    raise SystemExit("data/demo/current is a directory; move it before selecting the demo")
if link.is_symlink():
    link.unlink()
link.symlink_to(sys.argv[2], target_is_directory=True)
PY
echo "demo data ready: $demo_root/current"
