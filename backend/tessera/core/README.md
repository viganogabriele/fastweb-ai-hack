# Persistence and replay

`db.make_engine()` creates a SQLite engine with foreign keys and non-legacy
transactions. `create_schema()` initializes a new database; it does not migrate an
existing schema. Give each job its own `Session` through `repo_session()`:

```python
with repo_session(engine, run_spec) as repo:
    repo.put(document)
    repo.put(observation)
    documents = repo.list(SourceDocument, store_id="MIL01")
```

The context commits together or rolls back together. Producers must insert inputs
before their outputs. Input references resolve only inside the same namespace and
run, with known availability at the run clock. Derived records must match the run
and scenario and cannot predate their inputs. Source records with unknown/future
availability may be stored, but reads exclude them. Store scopes propagate from
documents and input references. Explicit indexes cannot contradict DTO fields.

`list()` preserves all eligible versions; `get(kind, id, version)` resolves an exact
reference, and omitting `version` returns the latest eligible version ordered by
availability then version string. Version strings are a deterministic tie-breaker,
not semantic version ordering. Deduplication and corrections remain module logic.

Run specifications and artifact versions are immutable. Changing the replay clock,
modules, inputs or settings requires a new run ID. `Repo.spec` returns a defensive
copy. After publication, only human decisions, reservations and clarifications can
be appended; projection changes require an explicit reset or a new run.

`ERPRecord` is an internal storage envelope for the source lane: convert parsed
dates to ISO strings and Decimal money to decimal strings in its JSON `data`.
`put_erp()`/`list_erp()` use a separate `erp_facts` table with the same run/scope/time
filtering. References use `kind="erp.sales"` (or another declared ERP table name).
The persistence layer does not infer money conversion, availability or demand.

## Fixtures and reset

Prepare a fixture-mode `RunSpec` JSON with `authorized_fixture_refs` containing
explicit file paths **relative to `data/fixtures/`**, for example
`documents/doc-20261009-1035-mil01.json`. Include both documents and observations
needed by their input references. Then run from `backend/`:

```sh
uv run tessera fixtures load --run-spec ../data/my-fixture-run.json --fixture-mode
uv run tessera reset --run fixture-run-id --fixture-mode
```

`--file` may be repeated to select a subset of the authorized files. `FIXTURE_MODE=1`
also selects the isolated namespace. No fixture discovery or injection takes place
in product runs. Derived fixture run/scenario IDs are rebound to the selected
fixture snapshot; availability and original fixture producer labels remain intact.
Unknown/future rows are reported as excluded. Invalid or incomplete imports roll
back together. Use a new fixture run ID if the selected sample changes.

`reset --run` deletes only that namespace/run's derived projections and module
statuses, and unpublishes it for recomputation. Source documents/segments, ERP
facts, stock facts, decisions, reservations and clarification history remain.
Other runs, the durable LLM cache and source files are untouched. Use a new
`scenario_id` for a fresh demo session; reset is not an undo of human decisions.
