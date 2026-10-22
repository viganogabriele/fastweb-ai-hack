# WEB-03: modules and next-run selection

The Pipeline page reads module manifests from the selected `RunView.spec.modules`
and execution status, mode, counts, errors and abstentions from that same run's
`module_runs`. Zero counts remain zero; absent results are explicitly unavailable.
Without a run, `GET /api/modules` provides a read-only installed catalog, including
an explicit empty state. Refresh reloads both runs and the catalog in this case.

## Supported write flow

1. Select an existing product run. Switches edit a local selection, not the
   historical snapshot. Switching run or leaving Pipeline discards local edits.
2. Review the existing stores and `as_of`. Required dependencies must remain
   enabled, and at least one enabled module must be available. Unavailable modules
   cannot be activated. Mode is read-only.
3. Choose **Avvia nuovo run con la selezione**. The browser posts the complete
   snapshot to the existing `POST /api/runs`, omitting `run_id`, preserving all
   parameters, source/code provenance, versions, scope and clock. Only `enabled`
   flags and `config_hash` change. The latter is SHA-256 of recursively key-sorted
   JSON for the submitted `CreateRun` excluding `config_hash`. This identifies
   submitted content independently of prior toggle history; it does not claim to
   hash current server files or create a new source manifest.
4. The server validates installed manifests and parameters, creates a new UUID and
   schedules execution. After acceptance the new run appears in the list; it is
   auto-selected only while the originating Pipeline view/run is still active.
   Use **Aggiorna stato** to read execution progress and published results.

## API limits

There is no endpoint for saving global pipeline defaults or a draft configuration,
preparing a fresh source/config/code snapshot, or retrieving defaults for module
parameters. Therefore the UI cannot bootstrap a first run from the catalog, add
newly installed modules to historical snapshots, change parameters/modes, select a
new date/store scope, or edit fixture runs. It can only resubmit the selected
complete product snapshot with changed enabled flags. The installed registry may
have changed since that snapshot: the server remains authoritative and can reject
the submission. Replay recordings require the resulting configuration identity;
recordings keyed to another configuration/hash are not silently reused.

The POST starts execution immediately; there is no separate "save for later" API.
Local edits are saved only on successful submission. A network failure may leave
submission outcome unknown: inspect the run list before retrying. There is no
automatic POST retry or promise of server-side idempotency. Run progress refresh
is manual. Disabling a module preserves its manifest in the next snapshot; it
contributes no output, and may have no execution record.

## Validation

- `node --test web/tests/moduleSelection.test.mjs`: immutability, scope/provenance,
  submission/rejection, required dependencies and history-independent hash.
- `PYTHONHASHSEED=0 make check`: full repository checks. The local default command
  encountered the existing Landlock child-Python startup error
  `_Py_HashRandomization_Init: failed to get random numbers`; fixed hash seeding
  avoids random-device initialization without changing the read isolation policy.
- `npm --prefix web run build`.
- Browser flow against the real FastAPI/orchestrator with an isolated temporary
  SQLite database and inline synthetic test modules, without reading the dataset.
