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

Fixture access requires both `FIXTURE_MODE=1` and `?fixture=true`. Product requests
cannot authorize fixtures, and neither submission path automatically loads them.
Production module tasks still need to provide MANIFEST/run entry points: an empty
or uninstalled graph is rejected instead of being presented as a successful run.

The MVP worker runs in process with one orchestrator lock. Queued work does not
survive a server restart; start a fresh run after an interrupted job. Published
artifacts and run metadata are durable in SQLite. Durable job recovery is outside
PLT-06. Use a single API worker process, as specified by the prototype architecture.
