"""Artifact store bound to one run (PLAN §2 rule 4, RFC §4.3).

`Repo(engine, spec)` is the only read/write path for modules, tools and the API. Every read is
scoped to `spec.run_id` and filtered by `available_at <= spec.as_of` inside the query, so a
caller can't forget it. Records with unknown availability are excluded unless asked for.
Artifacts are immutable: re-putting an identical record is a no-op, a different payload under
the same `(kind, id, version)` is an error. Each call opens its own short session.
"""

import builtins
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from types import MappingProxyType
from typing import Any, Protocol, TypeVar

from sqlalchemy import Engine, delete, insert, select, update

from tessera.core import contracts
from tessera.core.contracts import ModuleRun, RunSpec, SourceRef
from tessera.core.contracts.common import DerivedRecord, SourceRecord
from tessera.core.db import artifacts, erp_rows, module_runs, runs

# DTO kinds storable as artifacts: every public contract with id, version and availability.
KINDS: dict[str, type[SourceRecord]] = {
    name: model
    for name in contracts.__all__
    if isinstance(model := getattr(contracts, name), type) and issubclass(model, SourceRecord)
}
RUN_STATUSES = ("pending", "running", "published", "failed")
WRITABLE = ("pending", "running")

T = TypeVar("T", bound=SourceRecord)


class RunNotFound(LookupError):
    pass


class RunClosed(RuntimeError):
    """The run is published or failed: its artifacts can't change any more."""


class LookAhead(ValueError):
    """A record not yet available at the run's `as_of` (RFC §4.3, `generated/README.md` §4)."""


class ImmutableArtifact(ValueError):
    """Same `(kind, id, version)` already stored in this run with a different payload."""


class ErpRowLike(Protocol):
    """Shape of `modules.sources.erp.ERPRow`; core never imports a module."""

    table: str
    id: str
    version: str
    available_at: datetime | None
    availability_basis: str
    source_refs: tuple[SourceRef, ...]
    data: Mapping[str, Any]


@dataclass(frozen=True)
class ErpRecord:
    table: str
    id: str
    version: str
    available_at: datetime | None
    availability_basis: str
    source_refs: tuple[SourceRef, ...]
    data: Mapping[str, Any]


def _encode(value: Any) -> Any:
    # Tagged so Decimal money and dates come back with their type, not as float/str.
    if isinstance(value, Decimal):
        return {"$decimal": str(value)}
    if isinstance(value, datetime):
        return {"$datetime": value.isoformat()}
    if isinstance(value, date):
        return {"$date": value.isoformat()}
    return value


def _decode(value: Any) -> Any:
    if isinstance(value, dict) and len(value) == 1:
        ((tag, raw),) = value.items()
        if tag == "$decimal":
            return Decimal(raw)
        if tag == "$datetime":
            return datetime.fromisoformat(raw)
        if tag == "$date":
            return date.fromisoformat(raw)
    return value


def _now() -> datetime:
    return datetime.now(UTC)


# Run lifecycle (the orchestrator drives it; PLT-04).


def create_run(engine: Engine, spec: RunSpec) -> None:
    with engine.begin() as conn:
        if conn.execute(select(runs.c.run_id).where(runs.c.run_id == spec.run_id)).first():
            raise ValueError(f"run {spec.run_id!r} already exists")
        conn.execute(
            insert(runs).values(
                run_id=spec.run_id,
                scenario_id=spec.scenario_id,
                as_of=spec.as_of,
                status="pending",
                spec=spec.model_dump(mode="json"),
                created_at=_now(),
            )
        )


def run_status(engine: Engine, run_id: str) -> str:
    with engine.connect() as conn:
        status = conn.execute(select(runs.c.status).where(runs.c.run_id == run_id)).scalar()
    if status is None:
        raise RunNotFound(run_id)
    return status


def set_run_status(engine: Engine, run_id: str, status: str) -> None:
    """Move a writable run forward. `published` and `failed` are final."""
    if status not in RUN_STATUSES:
        raise ValueError(f"unknown run status {status!r}")
    current = run_status(engine, run_id)
    if current not in WRITABLE:
        raise RunClosed(f"run {run_id!r} is {current}")
    finished = _now() if status in ("published", "failed") else None
    with engine.begin() as conn:
        conn.execute(
            update(runs).where(runs.c.run_id == run_id).values(status=status, finished_at=finished)
        )


def list_runs(engine: Engine, status: str | None = None) -> list[tuple[RunSpec, str]]:
    """Runs with their status, newest first."""
    query = select(runs.c.spec, runs.c.status).order_by(runs.c.created_at.desc())
    if status is not None:
        query = query.where(runs.c.status == status)
    with engine.connect() as conn:
        return [(RunSpec.model_validate(s), st) for s, st in conn.execute(query)]


def reset_run(engine: Engine, run_id: str) -> int:
    """Delete one run's projections (artifacts, module runs, the run). ERP rows stay.

    Returns the number of artifacts deleted. Durable data (decisions, ledger) will need its own
    export before this is used on a run that holds any (RFC §4.3).
    """
    run_status(engine, run_id)
    with engine.begin() as conn:
        n = conn.execute(delete(artifacts).where(artifacts.c.run_id == run_id)).rowcount
        conn.execute(delete(module_runs).where(module_runs.c.run_id == run_id))
        conn.execute(delete(runs).where(runs.c.run_id == run_id))
    return n


def put_module_run(engine: Engine, module_run: ModuleRun) -> None:
    """Insert or replace the state of one module in a writable run."""
    current = run_status(engine, module_run.run_id)
    if current not in WRITABLE:
        raise RunClosed(f"run {module_run.run_id!r} is {current}")
    key = (module_runs.c.run_id == module_run.run_id) & (
        module_runs.c.module_id == module_run.module_id
    )
    with engine.begin() as conn:
        conn.execute(delete(module_runs).where(key))
        conn.execute(
            insert(module_runs).values(
                run_id=module_run.run_id,
                module_id=module_run.module_id,
                payload=module_run.model_dump(mode="json"),
            )
        )


def list_module_runs(engine: Engine, run_id: str) -> list[ModuleRun]:
    query = select(module_runs.c.payload).where(module_runs.c.run_id == run_id)
    with engine.connect() as conn:
        return [ModuleRun.model_validate(p) for (p,) in conn.execute(query)]


def latest[R: SourceRecord](records: Iterable[R]) -> builtins.list[R]:
    """The last version of each id, in first-seen order (`Repo.list` returns every version).

    A later module may write a new version of a record (`int.context` re-versions a `Case`):
    consumers that want one record per id read through this.
    """
    by_id: dict[str, R] = {}
    for record in records:
        by_id[record.id] = record
    return builtins.list(by_id.values())


# ERP rows: shared source data, not partitioned by run.


def put_erp(engine: Engine, rows: Iterable[ErpRowLike]) -> int:
    """Store ERP rows once per `(table, id, version)`; returns how many were new."""
    with engine.begin() as conn:
        seen = set(conn.execute(select(erp_rows.c.tbl, erp_rows.c.id, erp_rows.c.version)))
        values = []
        for row in rows:
            key = (row.table, row.id, row.version)
            if key in seen:
                continue
            seen.add(key)
            values.append(
                {
                    "tbl": row.table,
                    "id": row.id,
                    "version": row.version,
                    "store_id": row.data.get("store_id"),
                    "sku": row.data.get("sku"),
                    "available_at": row.available_at,
                    "availability_basis": row.availability_basis,
                    "source_refs": [r.model_dump(mode="json") for r in row.source_refs],
                    "data": {k: _encode(v) for k, v in row.data.items()},
                }
            )
        if values:
            conn.execute(insert(erp_rows), values)
    return len(values)


class Repo:
    """All reads and writes of one run, as seen at its `as_of`."""

    def __init__(self, engine: Engine, spec: RunSpec) -> None:
        self.engine = engine
        self.spec = spec

    @classmethod
    def open(cls, engine: Engine, run_id: str) -> "Repo":
        with engine.connect() as conn:
            spec = conn.execute(select(runs.c.spec).where(runs.c.run_id == run_id)).scalar()
        if spec is None:
            raise RunNotFound(run_id)
        return cls(engine, RunSpec.model_validate(spec))

    def _spec(self) -> RunSpec:
        """The run's own spec for internal reads of immutable fields, without copying."""
        return self.spec

    @property
    def run_id(self) -> str:
        return self._spec().run_id

    def status(self) -> str:
        return run_status(self.engine, self.run_id)

    def put(self, *records: SourceRecord) -> int:
        """Store records in this run, all or none; returns how many were new."""
        if (current := self.status()) not in WRITABLE:
            raise RunClosed(f"run {self.run_id!r} is {current}")
        rows = [self._row(record) for record in records]
        with self.engine.begin() as conn:
            new = []
            batch: dict[tuple[str, str, str], Any] = {}
            for row in rows:
                key = (row["kind"], row["id"], row["version"])
                if key in batch:  # same record twice in one call: identical is a no-op
                    if batch[key] != row["payload"]:
                        raise ImmutableArtifact(f"{row['kind']} {row['id']}@{row['version']}")
                    continue
                batch[key] = row["payload"]
                stored = conn.execute(
                    select(artifacts.c.payload).where(
                        artifacts.c.run_id == row["run_id"],
                        artifacts.c.kind == row["kind"],
                        artifacts.c.id == row["id"],
                        artifacts.c.version == row["version"],
                    )
                ).scalar()
                if stored is None:
                    new.append(row)
                elif stored != row["payload"]:
                    raise ImmutableArtifact(f"{row['kind']} {row['id']}@{row['version']}")
            if new:
                conn.execute(insert(artifacts), new)
        return len(new)

    def _row(self, record: SourceRecord) -> dict[str, Any]:
        kind = type(record).__name__
        if KINDS.get(kind) is not type(record):
            raise TypeError(f"{kind} is not a storable contract")
        if isinstance(record, DerivedRecord) and (
            record.run_id != self.run_id or record.scenario_id != self._spec().scenario_id
        ):
            raise ValueError(
                f"{kind} {record.id} belongs to run {record.run_id!r}/{record.scenario_id!r}"
            )
        if record.available_at is not None and record.available_at > self._spec().as_of:
            raise LookAhead(f"{kind} {record.id} available at {record.available_at.isoformat()}")
        payload = record.model_dump(mode="json")
        derived = isinstance(record, DerivedRecord)
        return {
            "run_id": self.run_id,
            "kind": kind,
            "id": record.id,
            "version": record.version,
            "store_id": getattr(record, "store_id", None) or getattr(record, "location_id", None),
            "sku": getattr(record, "sku", None),
            "case_id": record.id if kind == "Case" else getattr(record, "case_id", None),
            "available_at": record.available_at,
            "payload": payload,
            "input_refs": payload.get("input_refs", []),
            "producer": record.producer if derived else None,
            "computed_at": record.computed_at if derived else None,
        }

    def list(
        self,
        kind: type[T],
        *,
        store_id: str | None = None,
        sku: str | None = None,
        case_id: str | None = None,
        where: Mapping[str, str] | None = None,
        include_unknown: bool = False,
    ) -> list[T]:
        """Records of one kind in this run, available at `as_of`, in insertion order.

        `where` matches top-level string payload fields exactly (e.g. `{"document_id": ...}`).
        `include_unknown` adds records whose availability is unknown (`available_at=None`).
        """
        c = artifacts.c
        query = select(c.payload).where(c.run_id == self.run_id, c.kind == kind.__name__)
        visible = c.available_at <= self._spec().as_of
        query = query.where(visible | c.available_at.is_(None) if include_unknown else visible)
        for column, value in (("store_id", store_id), ("sku", sku), ("case_id", case_id)):
            if value is not None:
                query = query.where(c[column] == value)
        for field, value in (where or {}).items():
            query = query.where(c.payload[field].as_string() == value)
        with self.engine.connect() as conn:
            return [kind.model_validate(p) for (p,) in conn.execute(query.order_by(c.seq))]

    def get(self, kind: type[T], id: str, version: str | None = None) -> T | None:
        """One record by id (latest stored version unless given), if visible at `as_of`."""
        c = artifacts.c
        query = select(c.payload).where(
            c.run_id == self.run_id,
            c.kind == kind.__name__,
            c.id == id,
            c.available_at <= self._spec().as_of,
        )
        if version is not None:
            query = query.where(c.version == version)
        with self.engine.connect() as conn:
            payload = conn.execute(query.order_by(c.seq.desc()).limit(1)).scalar()
        return None if payload is None else kind.model_validate(payload)

    def erp(
        self, table: str, *, store_id: str | None = None, sku: str | None = None
    ) -> builtins.list[ErpRecord]:
        """ERP rows of one table known at `as_of`. Unknown availability is never visible."""
        c = erp_rows.c
        query = select(erp_rows).where(c.tbl == table, c.available_at <= self._spec().as_of)
        if self._spec().erp_max_seq is not None:
            query = query.where(c.seq <= self._spec().erp_max_seq)
        if store_id is not None:
            query = query.where(c.store_id == store_id)
        if sku is not None:
            query = query.where(c.sku == sku)
        with self.engine.connect() as conn:
            return [
                ErpRecord(
                    table=row.tbl,
                    id=row.id,
                    version=row.version,
                    available_at=row.available_at,
                    availability_basis=row.availability_basis,
                    source_refs=tuple(SourceRef.model_validate(r) for r in row.source_refs),
                    data=MappingProxyType({k: _decode(v) for k, v in row.data.items()}),
                )
                for row in conn.execute(query.order_by(c.seq))
            ]
