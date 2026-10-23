# Isolated offline replay (DEMO-02a)

Run from the repository root with the installed backend environment:

```sh
backend/.venv/bin/python scripts/replay_demo.py \
  --run-spec /absolute/path/to/frozen-run-spec.json \
  --sources /absolute/path/to/authorized/sources \
  --config /absolute/path/to/authorized/config \
  --cache /absolute/path/to/recorded/llm_cache \
  --workspace /absolute/path/to/dedicated-demo-workspace
```

The RunSpec is the contract object, not the API RunView envelope. All five
arguments are explicit. An empty cache directory is valid for a graph that makes
no model calls. Reuse the same public provider/model settings as the recording;
LLM replay keys include those settings and the run's source/config/model/prompt
identity. No API key is required or read by the replay client.

For snapshots enabling `src.voice`, also pass `--voice /absolute/path/to/voice`.
This explicit source tree contains the note folders, audio and transcript sidecars;
it is staged into the attempt's `data/fixtures/voice` and hashed in the manifest.
Omitting it fails with the `voice_inputs` prerequisite, rather than silently
replaying zero notes. The same overlap, symlink and forbidden-path rules apply.

Each invocation creates a new `attempt-<id>` below an empty or previously owned
workspace. It copies the authorized source/config/cache trees and executes the
existing orchestrator against a newly created database in that attempt. It never
copies a projection database into place, deletes old attempts, resets a shared
run, or rewrites the source trees/cache. A nonempty unowned workspace, overlapping
input/output roots, symlinks, nonregular files, secrets and hidden-answer paths
are refused. Private attempt directories have mode 0700. Do not point the
workspace at the application's data directory.

Symlink checks include parent directories; `eval/labels` is a forbidden input.
Module settings use the isolated environment without reading the repository dotenv.

The input RunSpec remains unchanged, including run/scenario IDs, clock, module
modes and namespace. The runtime client and module settings force `LLM_MODE=replay`.
A process-local audit hook denies socket networking (including local mock HTTP
calls) and spawning subprocesses during execution. The command stages fresh mock
input files and cannot mutate an existing mock server through HTTP. Modules that
need unavailable network-backed prerequisites must fail rather than fall back to
a live service. The tool is a dedicated command, not a server-side concurrent API.

Missing/corrupt cache entries and denied operations cause a nonzero exit even if
a module catches the error and publishes a degraded/fallback artifact. Module
errors and unsuccessful publication also fail. Tracebacks, module logs and prints
are suppressed; the output includes safe status/count/identity metadata only.
Original messages, prompts, responses and credentials are not emitted.

One JSON manifest is printed to stdout and written to
`<workspace>/<attempt_id>/manifest.json`. It contains format version, attempt/run/
scenario/clock/namespace, snapshot hash, actual staged tree hashes and file counts,
public provider-identity hash, module modes/status/counts, output-artifact hash,
missing prerequisites, missing/corrupt recording keys and network-attempt count.
Exit status is zero only for succeeded/degraded runs without replay prerequisites
missing. Compare input/output hashes across attempts for a fixed snapshot. The
actual copied tree hashes are recorded separately from the RunSpec's declared
source/config identities; arbitrary historical hash schemes are not rewritten.

Fixture snapshots remain in `data/tessera_fixture.db` inside their attempt and
are labelled `fixture_demo_only: true`; product snapshots use `data/tessera.db`.
A fixture demonstration can use source fixtures (for example a minimal stores.csv
and one timestamped .eml with only `src.email` enabled). The regression tests rebuild
that snapshot twice and compare output hashes, exercise the command directly,
and also replay a synthetic cached chat response. Preloading derived fixture artifacts via authorized_fixture_refs
is deliberately refused: it would not demonstrate rebuilding projections.

This command does not establish real-model investigator tool selection, G2/G3
completion, cache coverage for the final demo, or the full offline rehearsal.
Those recordings and integration remain in parent issue #115. It does not build
the public bundle (DEMO-03a). The bundle builder may consume this versioned
manifest, but must sanitize any separately exported artifact content itself.
