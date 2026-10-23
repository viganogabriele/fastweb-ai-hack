# Durable clarification answers (OUT-02b)

`answer_registry` is the lane E service boundary for the lane C HTTP adapter and
lane D answer UI in parent #134. It adds no HTTP route, frontend state or outbound
messaging. The existing read-only clarification API remains the source of published
questions. This task does not close #134 or implement #135.

## Platform handoff

The proposed POST path is
`/api/runs/{run_id}/cases/{case_id}/clarifications/{clarification_id}/answers`.
The adapter should construct `AnswerRequest` using the path IDs plus these body
fields (not allow contradictory duplicate IDs):

```json
{
  "scenario_id": "historical",
  "case_version": "1",
  "clarification_version": "1",
  "text": "La taglia richiesta è M.",
  "received_at": "2026-10-22T23:00:00+02:00",
  "language": "it",
  "follow_up_scenario_id": "simulated-size-M",
  "as_of": "2026-10-22T23:00:00+02:00",
  "idempotency_key": "operator-retry-key"
}
```

1. Resolve and authorize the namespace with the existing platform dependency.
   Fixture access needs `FIXTURE_MODE`; never derive `fixture_mode` from the body.
2. Call `submit_answer(engine, request, fixture_mode=..., registry=...)`. The
   immutable parent determines live/recorded/fixture mode. The service checks
   publication, scenario, current published run, exact latest case/question versions,
   membership, source lineage, event time, and enabled pipeline prerequisites.
3. After commit, schedule `execute_follow_up(engine, job.run.run_id, ...)` with
   the same engine/namespace, registry and settings. Return 202 and the `AnswerJob`
   (`run`, `document`, `fingerprint`, `simulated: true`); navigate to the actual
   returned run, whose normal RunView supplies pending/failure/publication state.
   Do not route this job through the generic `runs.execute`: it needs durable
   lineage restoration and the historical-evidence filter.
4. Map `InvalidAnswer` / Pydantic validation to 422, `AnswerConflict` to 409,
   `UnrecordedAnswer` / `AnswerUnavailable` to 503 with an explicit unavailable
   reason, and SQLite busy/locked errors to retryable 503. No network fallback.
5. On startup, `pending_follow_ups(engine, fixture_mode=...)` enumerates accepted
   jobs that may not yet have reached the background worker. Queue their run IDs.
   Repeated submission returns the same job and can safely queue it again.

The same retry key with a changed payload is a conflict. A different retry key
for the same deterministic answer/scenario/clock also returns the existing job,
and reserves that key against subsequent conflicting reuse. Alias retries resolve
the durable job before reopening the parent, so they survive a parent projection
reset. Concurrent acceptance is serialized by `BEGIN IMMEDIATE`; worker claiming
uses the same database lock.
An already published worker retry returns its job without re-executing modules;
an in-progress duplicate raises `AnswerConflict`.

## Persistence and replay

The additive `clarification_answer_events`, `clarification_answer_jobs` and
`clarification_answer_receipts` tables use separate metadata and no run foreign
keys, following the action ledger pattern. The database must be backed up with
these tables. They retain canonical answer input, prepared source/segment,
answered clarification, frozen child RunSpec, exact transitive parent artifacts,
and idempotency receipts even if both parent and child projections are reset.
There is no schema-version change to the reconstructible artifact tables.

Offline submission requires the exact fingerprint in the durable allowlist.
`register_recorded_answer` is exclusively a trusted recording importer seam:
call it only after accepting the event and recording all required model/tool
responses. Never expose it as a free-text HTTP registration endpoint. Computing a
fingerprint is insufficient. Live submission persists an event with
`replay_ready=no`; neither execution success nor retry makes it replayable.
A registered event may be scheduled at a different scenario/clock, but each
snapshot still needs its own required recordings; pipeline cache misses stay
explicit and leave the follow-up unpublished. The worker observes typed replay
misses and corrupt recordings at the LLM boundary even when extraction or linking
catches the error and returns a degraded module result.

A failed run can be retried after explicitly resetting its projection with
`reset_run`. The durable job then recreates the same frozen snapshot and sources,
without needing the original parent projections. After a process crash, first
stop the old worker before resetting a running projection. Workers never steal
running jobs automatically. Historical run publication remains immutable.

## Seeding and execution

The follow-up clock must reach the answer's receipt time, strictly after the
parent clock. No extraction or other module executes during acceptance. The
worker seeds exact transitive dependencies, checks segment/document versions,
then runs the frozen DAG with the normal orchestrator. Extraction, linking,
forecast overlay and options must be enabled; missing required prerequisites
are rejected during acceptance.

Source documents and segments keep their exact identities. Historical derived
records retain their IDs and original computation times but receive a
`parent:<fingerprint>:<original version>` version in the child's run/scenario.
All typed artifact references in derived records are remapped to those versions;
original payloads and versions remain in the durable registry. ERP references
resolve through the normal availability-filtered shared source view.

The worker supplies a repository view that excludes historical derived versions
from module `list` calls and unversioned `get` calls while keeping exact versioned
`get` references resolvable. This
prevents old observations from being counted twice and old case/observation
versions from colliding with recomputation. The answered clarification links the
new simulated source to that preserved lineage. Fresh observations, product
links, cases, forecasts and options are produced by the frozen pipeline, never
inferred by the answer service. Normal published API reads can still inspect
historical versions and their citations.

When wiring the write endpoint, lane C should also exclude `parent:` derived
versions from operational collection responses (queue, counts, options inputs),
while preserving exact-version reads for citations. The worker already applies
this distinction to all pipeline module reads; it is not a frontend-local
answered state or a forecast adjustment.

## Contextual reconciliation (OUT-02d)

During the child's `ing.extract` execution, the lane-E adapter
`contextual_answers.ContextualExtraction` asks the existing structured LLM client
for a product mention using the exact remapped original observation, answered
clarification (including the question), answer document and child RunSpec. These
inputs and the versioned instruction text are part of the cache context. This is
an additional recording: registering an answer fingerprint alone does not make
its interpretation replayable. A missing/corrupt contextual recording fails the
child without publication or network fallback in replay mode.

Code retains the original observation ID, quantity, period, attribution, kind,
negation and original document evidence. The child has its own current version in
its isolated run; its inputs pin the historical original observation, answered
question and answer document. Its availability is the answer receipt time. A
`supersedes` EvidenceRelation explicitly connects this current fact to the exact
historical version. Linking, cases, forecast and options consume this single
current observation. The answer document remains inspectable as a source but is
excluded from independent extraction, so it cannot create duplicate demand.
Re-extracted original candidates with the same evidence span are replaced;
ambiguous/changed spans of the same kind fail closed instead of being added.

This supports product/size/colour clarification. It deliberately preserves the
original count and episode dates: the model cannot manufacture quantitative
uplift, reset decay to the answer time or replace quantities. Null interpretation
retains the original product mention, with explicit answer provenance; it does
not promise resolution. Multiple exact original observations are read separately;
ambiguous fact alignment requires a new reviewed recording/extraction, not a
heuristic match. New count corrections and unrelated demand in an answer need a
separate ingestion feature. Existing source, store, namespace, frozen pipeline
and answer-clock checks remain in force.

Tests use synthetic structured model responses and synthetic ERP/system inputs;
they verify deterministic reconciliation and production downstream math, not
real-model comprehension. A real replay-client test additionally proves that an
accepted registered answer with an empty context cache fails without networking.
The HTTP regression now expects corrected original links and supersession rather
than the previously documented broken behavior; lane C should review that focused
test update. No production API/UI, lane A/B module or PR220 path changes are needed.
