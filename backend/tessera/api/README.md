# Run API (PLT-06)

`create_app(engine=..., registry=..., settings=...)` supports isolated tests and
service configuration; the default application opens its database lazily.
`/docs` describes the HTTP contracts, also exported by `make types`.

POST `/api/runs` accepts the frozen RunSpec fields except `run_id` (server UUID),
validates installed module declarations and schedules the actual orchestrator.
GET `/api/runs` and `/api/runs/{run_id}` expose snapshots and module status.
Documents and cases are readable only after successful/degraded publication.
Document detail includes matching canonical segments, observations and entity
links. Store filters cannot widen the run's declared scope; IDs never become
filesystem paths.

Run lookup, publication status and artifact reads share one database transaction.
A concurrent reset cannot recreate a deleted run or mix its old configuration
with new results. The run list skips entries deleted after enumeration. Pending,
running, blocked and failed runs keep their metadata visible, but all document
and case endpoints return 409 until publication. Successful and degraded runs
are readable; starting a new run or demo scenario leaves older complete runs
available with their original snapshot and timestamp.

Fixture access requires both `FIXTURE_MODE=1` and `?fixture=true`. Product requests
cannot authorize fixtures, and neither submission path automatically loads them.
Production module tasks still need to provide MANIFEST/run entry points: an empty
or uninstalled graph is rejected instead of being presented as a successful run.

The MVP worker runs in process with one orchestrator lock. Queued work does not
survive a server restart; start a fresh run after an interrupted job. Published
artifacts and run metadata are durable in SQLite. Durable job recovery is outside
PLT-06. Use a single API worker process, as specified by the prototype architecture.

## Reports (PLT-11)

- `GET /api/runs/{run_id}/reports?view=by_office` lists the latest persisted
  version of each report ID; omit `view` to include all views. No report returns
  an empty list. Version selection follows repository insertion order, not
  lexical version ordering (`v10` follows `v2`).
- `GET /api/runs/{run_id}/reports/{owner}?view=by_office` returns report details
  for briefs citing a `Case` owned by that exact owner. Each detail contains the
  original `report` and an ordered `citations` array, whose entries pair the
  original `citation` with the complete JSON `artifact` it references. The kind
  is `citation.ref.kind`. Case ownership uses the cited version, not a newer one.
  No matching brief returns 404.

OUT-01 stores grouped briefs (`by_office` and `by_priority`), not separate
artifacts for individual owners. The owner endpoint selects relevant complete
briefs; it preserves their other sections and citation numbering. This is a
navigation filter, not an authorization boundary. GET requests never regenerate
or persist reports. To change their contents, execute a new run.

Every citation is resolved by kind, ID and exact version through the same
published run repository and transaction. An unknown kind, missing version,
future record or out-of-scope store causes 409 rather than returning a brief
with an unresolvable citation. No cross-run or latest-version fallback is used.
Both routes inherit publication checks (409), missing-run/namespace checks
(404), `as_of` filtering and explicit fixture access (`?fixture=true` plus
`FIXTURE_MODE=1`). The API does not interpret citation field paths or recompute
numbers; nested and array fields remain available in the resolved artifact.

## Agent trace reads (PLT-12a)

`GET /api/runs/{run_id}/cases/{case_id}/traces` returns the latest visible version
of each `AgentTrace` ID belonging to the case, sorted by ID. Latest selection
uses repository publication order (not lexical version order) before filtering
by case, so an older version cannot silently reappear if a trace changes case.
An existing case with no traces returns an empty array.

`GET /api/runs/{run_id}/cases/{case_id}/traces/{trace_id}?version=...` returns the
exact requested version; omit `version` for the latest visible one. Missing cases,
missing trace versions and traces belonging to a different case return 404.
Both endpoints require a published succeeded/degraded run (409 otherwise) and
inherit the same transaction, store scope, `as_of` and namespace protections as
other artifact reads. Fixtures require explicit `?fixture=true` and enabled
fixture access. Agent steps, errors, mode, token counts and fallback status are
returned unchanged from the stored contract.

These GETs perform no model calls and write no artifacts. They can read existing
contract fixtures without importing or waiting for AG-03. The POST investigate
service remains separate work in parent issue #113; this read-side implementation
does not establish that real-model investigation has been recorded or verified.
