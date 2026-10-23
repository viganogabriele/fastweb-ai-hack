"""Bind the canonical repository's short operations to one atomic worker job.

The public PLT-03 Repo remains unchanged. Its Engine-shaped dependency is adapted
so its begin/connect blocks reuse the worker connection without committing or
closing it. Per-module savepoints and the outer transaction own all boundaries.
Fixture separation remains physical: the caller chooses the fixture database.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import Connection, Engine, delete, select

from tessera.core.contracts import ModuleRun, RunSpec, Segment, SourceDocument
from tessera.core.contracts.common import DerivedRecord, SourceRecord
from tessera.core.db import artifacts, runs
from tessera.core.repo import (
    KINDS,
    Repo,
    RunNotFound,
    create_run,
    list_module_runs,
    put_module_run,
    run_status,
    set_run_status,
)


class _BoundEngine:
    def __init__(self, connection: Connection):
        self.connection = connection
        self.url = connection.engine.url

    @contextmanager
    def begin(self) -> Iterator[Connection]:
        yield self.connection

    @contextmanager
    def connect(self) -> Iterator[Connection]:
        yield self.connection


class RunRepo(Repo):
    """Canonical Repo with immutable spec and worker lifecycle conveniences."""

    def __init__(
        self,
        connection: Connection,
        spec: RunSpec,
        *,
        fixture_mode: bool = False,
        module_scope: bool = False,
    ):
        if (spec.mode == "fixture") != fixture_mode:
            raise ValueError("Fixture runs require an explicitly isolated fixture database")
        self.session = connection
        # Modules write artifacts only; run lifecycle belongs to the orchestrator.
        self._module_scope = module_scope
        self.namespace = "fixture" if fixture_mode else "product"
        bound = _BoundEngine(connection)
        snapshot = RunSpec.model_validate(spec.model_dump(mode="json"))
        existing = connection.execute(
            select(runs.c.spec).where(runs.c.run_id == snapshot.run_id)
        ).scalar()
        if existing is None:
            create_run(bound, snapshot)
        elif existing != snapshot.model_dump(mode="json"):
            raise ValueError("RunSpec is immutable; use a new run_id for a changed snapshot")
        super().__init__(bound, snapshot)

    @property
    def spec(self) -> RunSpec:
        return self._snapshot.model_copy(deep=True)

    def _spec(self) -> RunSpec:
        # Hot path (every put/get/list): callers only read immutable fields; `spec` still copies.
        return self._snapshot

    @spec.setter
    def spec(self, value: RunSpec) -> None:
        self._snapshot = RunSpec.model_validate(value.model_dump(mode="json"))

    def _scopes(self, record: SourceRecord) -> set[str]:
        scopes = set(getattr(record, "store_ids", ()))
        direct = getattr(record, "store_id", None)
        if isinstance(record, SourceDocument):
            direct = record.meta.get("store_id") or direct
        direct = direct or getattr(record, "scope", {}).get("store_id")
        if direct:
            scopes.add(direct)
        # Explicit indexes survive reopening even when the DTO has no store field.
        indexed = self.session.execute(
            select(artifacts.c.store_id).where(
                artifacts.c.run_id == self.run_id,
                artifacts.c.kind == type(record).__name__,
                artifacts.c.id == record.id,
                artifacts.c.version == record.version,
            )
        ).scalar()
        if indexed is not None and (
            type(record).__name__ != "StockFact" or indexed in self._spec().stores
        ):
            scopes.add(indexed)
        return scopes

    def _row(self, record: SourceRecord) -> dict:
        row = super()._row(record)
        scopes = self._scopes(record)
        overrides = getattr(self, "_put_indexes", {})
        supplied_store = overrides.get("store_id")
        if supplied_store:
            if scopes and supplied_store not in scopes:
                raise ValueError("Store index contradicts artifact content")
            scopes.add(supplied_store)
        if isinstance(record, DerivedRecord):
            for ref in record.input_refs:
                if ref.kind.startswith("erp."):
                    candidates = self.erp(ref.kind.removeprefix("erp."))
                    parent = next(
                        (r for r in candidates if r.id == ref.id and r.version == ref.version), None
                    )
                    parent_scopes = (
                        {parent.data["store_id"]}
                        if (parent and parent.data.get("store_id"))
                        else set()
                    )
                elif ref.kind == "ForecastVintage":
                    # fc.baseline cites the ERP forecast rows of one run date as
                    # "<file stem>/<store>/<sku>" @ run_date: resolve them like erp.* refs.
                    stem, store, sku = ref.id.rsplit("/", 2)
                    rows = [
                        r
                        for r in self.erp("forecast", store_id=store, sku=sku)
                        if str(r.data.get("run_date")) == ref.version
                        and any(Path(s.uri).stem == stem for s in r.source_refs)
                    ]
                    parent = max(rows, key=lambda r: r.available_at) if rows else None
                    parent_scopes = {store} if rows else set()
                else:
                    kind = KINDS.get(ref.kind)
                    parent = self.get(kind, ref.id, ref.version) if kind else None
                    parent_scopes = self._scopes(parent) if parent else set()
                if parent is None:
                    raise ValueError("Input is unavailable in this run")
                if record.available_at is None or record.available_at < parent.available_at:
                    raise ValueError("Derived availability must include every input")
                scopes.update(parent_scopes)
        if isinstance(record, Segment):
            documents = super().list(
                SourceDocument,
                where={"id": record.document_id, "text_version": record.text_version},
            )
            if not documents:
                raise ValueError("Segment document version is unavailable in this run")
            parent = documents[-1]
            record.validate_against(parent)
            if record.available_at is None or record.available_at < parent.available_at:
                raise ValueError("Segment cannot precede its document")
            scopes.update(self._scopes(parent))
        if not scopes <= set(self._spec().stores):
            raise ValueError("Artifact is outside this RunSpec's stores")
        if len(scopes) == 1:
            row["store_id"] = next(iter(scopes))
        for field in ("sku", "case_id"):
            supplied = overrides.get(field)
            if supplied is not None:
                if row[field] is not None and row[field] != supplied:
                    raise ValueError("Artifact index contradicts its content")
                row[field] = supplied
        return row

    def put(self, *records: SourceRecord, store_id=None, sku=None, case_id=None) -> int:
        self._put_indexes = {"store_id": store_id, "sku": sku, "case_id": case_id}
        try:
            with self.session.begin_nested():
                # The canonical Repo prepares an entire batch before inserting.
                # Insert in caller order inside our one savepoint so a child can
                # resolve an earlier parent while the batch remains all-or-none.
                return sum(super(RunRepo, self).put(record) for record in records)
        finally:
            self._put_indexes = {}

    def list(self, kind, *, store_id=None, **filters):
        if store_id is not None and store_id not in self._spec().stores:
            raise ValueError("Store is outside this RunSpec")
        records = super().list(kind, **filters)
        visible = []
        for record in records:
            scopes = self._scopes(record)
            if scopes <= set(self._spec().stores) and (
                store_id is None or not scopes or store_id in scopes
            ):
                visible.append(record)
        return visible

    def get(self, kind, id, version=None):
        record = super().get(kind, id, version)
        if record is not None and not self._scopes(record) <= set(self._spec().stores):
            return None
        return record

    def erp(self, table, *, store_id=None, sku=None):
        if store_id is not None and store_id not in self._spec().stores:
            raise ValueError("Store is outside this RunSpec")
        return [
            record
            for record in super().erp(table, store_id=store_id, sku=sku)
            if record.data.get("store_id") is None or record.data["store_id"] in self._spec().stores
        ]

    def run_state(self) -> dict:
        status = run_status(self.engine, self.run_id)
        modules = self.module_runs()
        if status == "published":
            status = "degraded" if any(m.status != "succeeded" for m in modules) else "succeeded"
        elif status == "failed" and any(m.status == "blocked" for m in modules):
            if not any(m.status == "failed" for m in modules):
                status = "blocked"
        return {"spec": self.spec, "status": status, "published": self.status() == "published"}

    def _lifecycle(self) -> None:
        if self._module_scope:
            raise PermissionError("modules cannot change run or module lifecycle state")

    def discard_artifacts(self) -> None:
        """Drop unpublished outputs of a run that will never be published."""
        self._lifecycle()
        self.session.execute(delete(artifacts).where(artifacts.c.run_id == self.run_id))

    def set_run_status(self, status: str, *, published: bool = False) -> None:
        self._lifecycle()
        if published:
            if status not in {"succeeded", "degraded"}:
                raise ValueError("Only successful/degraded complete runs can be published")
            status = "published"
        elif status in {"blocked", "failed"}:
            status = "failed"
        elif status not in {"pending", "running"}:
            raise ValueError("Invalid unpublished run status")
        set_run_status(self.engine, self.run_id, status)

    def publish(self, status: str = "succeeded") -> None:
        self.set_run_status(status, published=True)

    def save_module_run(self, module: ModuleRun) -> None:
        self._lifecycle()
        if module.run_id != self.run_id:
            raise ValueError("Module state belongs to another run")
        module = ModuleRun.model_validate(module.model_dump(mode="json"))
        put_module_run(self.engine, module)

    def module_runs(self) -> tuple[ModuleRun, ...]:
        return tuple(list_module_runs(self.engine, self.run_id))


@contextmanager
def repo_session(
    engine: Engine,
    spec: RunSpec | str,
    *,
    fixture_mode: bool = False,
    module_scope: bool = False,
    write: bool = False,
) -> Iterator[RunRepo]:
    """``write=True`` takes the SQLite write lock up front (BEGIN IMMEDIATE).

    A deferred read transaction that later writes fails at once if another writer
    committed meanwhile; an immediate one waits the busy timeout instead.

    Passing a run ID opens an existing run. Its spec, status and artifacts are
    read from the same transaction; missing or foreign-namespace runs never get
    created. Passing a RunSpec retains the worker's create-or-open behavior.
    """
    with engine.begin() as connection:
        # sqlite3 legacy transaction mode does not start BEGIN for reads or
        # SAVEPOINT. Force the outer transaction before a first module savepoint
        # so RELEASE can never commit writes beyond the worker boundary.
        if connection.dialect.name == "sqlite":
            driver = connection.connection.driver_connection
            if not driver.in_transaction:
                connection.exec_driver_sql("BEGIN IMMEDIATE" if write else "BEGIN")
        if isinstance(spec, str):
            run_id = spec
            spec = Repo.open(_BoundEngine(connection), run_id).spec
            if (spec.mode == "fixture") != fixture_mode:
                raise RunNotFound(run_id)
        yield RunRepo(connection, spec, fixture_mode=fixture_mode, module_scope=module_scope)
