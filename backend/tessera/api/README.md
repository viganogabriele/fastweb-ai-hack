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

## MCP reads (AG-04)

`tessera mcp` exposes the existing read routes and versioned canonical documents
through MCP stdio. See [MCP setup and scope](MCP.md) for client configuration,
namespace selection and the explicit read-only tool allowlist.

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

These GETs perform no model calls and write no artifacts.

## Investigator jobs (PLT-12)

`POST /api/runs/{run_id}/cases/{case_id}/investigate` takes no body. It returns
202 with a `RunView` for a **separate run** and a `Location` header pointing at
`/api/runs/{job_run_id}`. Poll that location for module status. After successful
or degraded publication, read the resulting case, traces, options and simulated
clarification drafts under `/api/runs/{job_run_id}/cases/{case_id}/...`. The
original run and case remain unchanged; investigation never approves or sends.

The job copies the complete visible snapshot, including exact artifact versions,
insertion order, indexes and prior module results. It keeps the parent's clock,
stores and scenario. Only the investigator runs; ingestion and the rest of the
pipeline are not executed again. The selected case and the investigator's current
manifest, prompt, model and domain policy are captured at submission. A job uses
the same single worker as pipeline runs. All new artifacts become readable
together when the job publishes. A failure discards the copied snapshot and any
partial outputs; metadata and the failed module result remain readable.

Identical submissions reuse a deterministic job ID, including while pending or
after failure. Its identity includes the parent snapshot, selected case, module
configuration, domain policy and prompt content. Execution mode does not change
that identity. Reset a failed/interrupted job before retrying the same inputs;
resetting and rebuilding also allows verification against its LLM recordings.
In-process background jobs are not durable across an API restart.

Recorded and fixture parents force LLM replay even when the server is configured
for live calls. A live parent follows `LLM_MODE`; `record` records the new job's
conversation and `replay` never constructs a provider client. A cache miss fails
explicitly with `Missing LLM recording (replay miss)` in the module result. A new
job's conversation needs its own recording: the two AG-03 dev recordings do not
guarantee coverage for arbitrary snapshots. Stock and lanes use the existing
time-filtered systems adapter (including the local mock HTTP service); unavailable
systems remain unknown and may produce a degraded result.

Missing runs/cases and foreign namespaces return 404; unpublished parents and
closed/decided cases return 409. SQLite write contention returns 503 with
`Retry-After: 5`. Fixture submission and all subsequent job reads require both
`FIXTURE_MODE=1` and `?fixture=true`; the Location header preserves this selector.

## Clarification reads (PLT-13)

GET `/api/runs/{run_id}/cases/{case_id}/clarifications` lists the latest visible
version of each persisted clarification belonging to the case, in ID order.
Optional `status=draft|asked|answered|cancelled` filters after version selection:
a superseded draft cannot reappear when filtering for drafts. The latest version
is selected across the run before case filtering, using repository publication
order rather than lexical version order.

GET `/api/runs/{run_id}/cases/{case_id}/clarifications/{clarification_id}` reads
the latest visible version; `?version=...` selects an exact historical version.
Both endpoints require an existing visible case and a published run. Missing
run/case/question/version or a question belonging to another case returns 404;
unpublished runs return 409. Fixture access, store scope and as_of filtering
use the same repository transaction as the other run artifact endpoints.

Questions, observation references, simulated flag, status and answer references
are returned unchanged from the contract. An existing case without questions
returns an empty list. These GETs never invoke an agent, send messages, submit
answers or create runs. Durable answers and follow-up scheduling remain the
separate OUT-02b task; this API reads its available artifacts without importing
that service or depending on model recordings. The endpoints are navigation
within a run, not an additional user authorization mechanism.
