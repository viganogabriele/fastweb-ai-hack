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

`tesseract mcp` exposes the existing read routes and versioned canonical documents
through MCP stdio. See [MCP setup and scope](MCP.md) for client configuration,
namespace selection and the explicit read-only tool allowlist.

## Agent trace reads (PLT-12a)

`GET /api/runs/{run_id}/cases/{case_id}/traces` returns the latest visible version
of each `AgentTrace` ID belonging to the case, sorted by ID. Latest selection
uses repository publication order (not lexical version order) before filtering
by case, so an older version cannot silently reappear if a trace changes case.
An existing case with no traces returns an empty array.

`GET /api/runs/{run_id}/cases/{case_id}/traces/{trace_id}?version=...` returns the
exact requested version; omit `version` for the latest current one. Missing current
cases, missing trace versions and traces belonging to a different case return 404.
An exact trace version remains readable when its case exists only as historical support.
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
manifest, prompt text, model, crosswalk and domain policy are captured at submission.
An optional `RunSpec.erp_max_seq` also freezes the ERP insertion boundary, in
addition to the existing time and store filters; rows loaded while a job waits
cannot enter it. Nested investigations inherit this boundary. Scenario ledger
reservations are captured for evaluation and included in the job identity;
human approval still revalidates against the current ledger. A job uses
the same single worker as pipeline runs. All new artifacts become readable
together when the job publishes. A failure discards the copied snapshot and any
partial outputs; metadata and the failed module result remain readable.

Identical submissions reuse a deterministic job ID, including while pending or
after failure. Its identity includes the parent snapshot, selected case, module
configuration, domain policy, prompt content, crosswalk and ledger reservations.
Execution mode does not change
that identity. Reset a failed/interrupted job before retrying the same inputs;
resetting and rebuilding also allows verification against its LLM recordings.
In-process background jobs are not durable across an API restart. A queued task
from before a reset cannot execute or fail a recreated job with the same ID.

Recorded and fixture parents force LLM replay even when the server is configured
for live calls. A live parent follows `LLM_MODE`; `record` records the new job's
conversation and `replay` never constructs a provider client. A cache miss fails
explicitly with `Missing LLM recording (replay miss)` in the module result. A new
job's conversation needs its own recording: the two AG-03 dev recordings do not
guarantee coverage for arbitrary snapshots. Stock and lanes use the existing
time-filtered systems adapter (including the local mock HTTP service); unavailable
systems remain unknown and may produce a degraded result.

The investigator retains its tool/turn budget and caps the LLM client's overall
deadline at 90 seconds (or the stricter configured limit). Existing runs without
the optional ERP boundary and their LLM recordings remain compatible.

Missing runs/cases and foreign namespaces return 404; unpublished parents,
closed cases and cases with a durable decision in any run of the scenario
(including the parent of a job) return 409. SQLite
write contention returns 503 with
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
Collections and unversioned reads require an existing current case; an exact
question version remains readable when its case is historical. Both require a published run. Missing
run/case/question/version or a question belonging to another case returns 404;
unpublished runs return 409. Fixture access, store scope and as_of filtering
use the same repository transaction as the other run artifact endpoints.

Questions, observation references, simulated flag, status and answer references
are returned unchanged from the contract. An existing case without questions
returns an empty list. These GETs never invoke an agent, send messages, submit
answers or create runs. The endpoints are navigation within a run, not an
additional user authorization mechanism.

## Decision reads (PLT-14)

GET `/api/runs/{run_id}/decisions` lists the local drafts saved for the run by
the decision endpoints (PLT-10) or restored by `replay_demo.py --decisions`, in
decision-clock order; `?case_id=...` keeps one case's drafts and requires that
case to be visible. GET `/api/runs/{run_id}/decisions/{decision_id}` returns one.
Each item is the persisted `LocalDraft` unchanged: the decision's id, version,
`at` clock, `by`, `decision`, `dispatch_status: draft` and the option ref in
`input_refs`, the decided option at its exact version, held reservations and
`simulated: true`.

The rows come from the scenario ledger in the selected namespace, filtered to
this run's scenario and ID, in the same transaction as the publication check.
The ledger survives run resets, so a draft is listed only while the run still
publishes the decided option at that exact version and its case is visible. An
idempotent retry appears once; a rejected (409) attempt saves nothing and is
never listed. Reads never revalidate, refresh, synthesize or dispatch a decision.

Drafts are run-scoped: an empty list means no decision saved *in this run*.
Investigation job runs share the parent's scenario and copy its options but not
its decisions; read the parent run for those. An empty list therefore does not
make an option decidable: the decision endpoints refuse an option version (id,
version, input hash) that already has a draft in any run of the scenario with
409 `option already decided in another run of this scenario` and save
nothing (PLT-15); a case decided in any run of the scenario cannot be
investigated again either. An exact retry of the original command on its own run still
returns the saved draft. Missing runs, unknown decision IDs and foreign
namespaces return 404 (fixture access as for other reads); unpublished runs
return 409.

## Simulated clarification answers (OUT-02)

POST `/api/runs/{run_id}/cases/{case_id}/clarifications/{clarification_id}/answer`
accepts `AnswerRequest` and returns 202 with an immutable `AnswerJob`. The body
must repeat the three URL IDs exactly and supply the parent scenario, exact case
and clarification versions, answer text, timezone-aware receipt timestamp,
optional language, distinct follow-up scenario, follow-up clock and idempotency
key. The new clock must reach the receipt timestamp, strictly after the parent
clock. Mode, store and fixture authorization are determined by the server and
published parent; the client cannot override them.

The adapter commits the durable answer job before queuing its worker. The
response identifies the simulated source document and the actual new run; it
does not assert that execution has completed. Read `/api/runs/{job.run.run_id}`
for publication, module errors and pending/running/failed/degraded status. The
original run, question and source versions remain unchanged. All fixture writes
and subsequent navigation need `?fixture=true` and enabled fixture access.

Malformed input or mismatched scope returns 422; stale versions, an unpublished
or superseded parent and conflicting idempotency-key reuse return 409. An exact
answer with no trusted offline recording returns 424 without a network fallback.
Missing source lineage, unavailable frozen code or invalid frozen module
parameters return 503. A locked database returns 503 with `Retry-After: 5`.
Retry an uncertain submission with its original payload and key; an accepted
retry returns the same job without repeating completed execution. Background
failure does not turn a committed submission into a failed HTTP response.

On startup the API queues accepted pending answer jobs from existing databases,
including the fixture database only when fixture access is enabled. It does not
create new databases during recovery or replay completed jobs. A running job
left by a crashed worker, or a failed projection, requires stopping the old
worker and explicitly resetting the projection before retrying the durable job.
This recovery applies to clarification jobs; generic PLT-06 run jobs retain the
in-process lifecycle described above.

Operational reads exclude historical derived support versions (`parent:...`) from
queues, document observations/links, forecasts, reports, traces and options. Queue
counts computed from these collections therefore describe current outputs only.
Unversioned reads cannot revive a disappeared parent case or option; approval
input gathering and investigation submission/execution apply the same filter.
Investigation snapshots retain historical records for exact citations.
Source documents/segments remain visible,
and exact derived version pins still resolve inside report citations and versioned
case/trace/question reads. An answered receipt whose original case disappeared can
be read with `?version=answer:{fingerprint}`.

GET `/api/runs/{run_id}/cases/{case_id}/clarifications/{clarification_id}/registered-answers`
lists the trusted recorded answers for that exact parent question as `RegisteredAnswer`
bodies: the complete `AnswerRequest` fields except `idempotency_key`, plus the
answer `fingerprint`. An offline (recorded/fixture) parent accepts only these
bodies; a client adds its own idempotency key and posts them unchanged. The list
is read-only: it never registers, authorizes or submits an answer, and a failed
free-text submission never appears in it. Registration remains the trusted
importer seam (`register_recorded_answer`, e.g. `scripts/clarification_answers_demo.py`).
Missing run/case/question returns 404, unpublished runs 409, and fixture access
follows the other artifact reads. A live parent accepts free text and may list none.

HTTP tests cover controlled graphs and the production extraction/linking/dedup/
cases/baseline/overlay/options pipeline with synthetic ERP and fake model/systems
boundaries, plus concurrent/repeated submission, scope/version isolation and a
parent-projection hash before/after. A missing recording leaves the child failed
and unpublished. Contextual reconciliation (OUT-02d/e) corrects the original
observation in the child: the answer document creates no second demand, and the
answered document's exact parent observations are carried rather than re-read.
Real-model evidence for the dev Core demo question is in
`data/fixtures/runs/core-dev-20261022/clarification-answers/VERIFICATION.md`;
its replay test submits the recorded answers through this endpoint offline.
