"""Run-bound repository. All reads filter namespace/run/scope/time in SQL.

``with repo_session(engine, spec) as repo`` is one atomic job. A successful
context commits; exceptions roll back. Sources and human decisions survive
``reset_projections``; derived views and module statuses are reconstructible.
Lists preserve versions; get without a version returns the latest known version.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import TypeVar

from pydantic import JsonValue
from sqlalchemy import and_, delete, exists, or_, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from tessera.core import contracts
from tessera.core.contracts import (
    ArtifactRef,
    Clarification,
    Decision,
    EntityLink,
    EvidenceRelation,
    ModuleRun,
    Observation,
    Reservation,
    RunSpec,
    Segment,
    SourceDocument,
)
from tessera.core.contracts.common import DerivedRecord, SourceRecord
from tessera.core.db import ArtifactRow, ArtifactScopeRow, ERPRow, ModuleRunRow, RunRow

T = TypeVar("T", bound=SourceRecord)
ARTIFACT_TYPES = {
    name: cls
    for name in contracts.__all__
    if isinstance(cls := getattr(contracts, name), type) and issubclass(cls, SourceRecord)
}
DURABLE_KINDS = {
    "SourceDocument",
    "Segment",
    "StockFact",
    "Decision",
    "Reservation",
    "Clarification",
}
ERP_TABLES = {
    "stores",
    "styles",
    "sku_colour",
    "sku_size_ean",
    "assortment",
    "prices",
    "sales",
    "stock",
    "forecast",
}


def instant(value: datetime) -> str:
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError("An aware datetime is required")
    return value.astimezone(UTC).isoformat(timespec="microseconds")


class ERPRecord(SourceRecord):
    """Internal persistence envelope, independent of any source module.

    ING-01 converts its parsed dates/Decimal money into explicit JSON values.
    Consumers reference a fact with ArtifactRef(kind='erp.sales', id=..., version=...).
    """

    table: str
    store_id: str | None = None
    sku: str | None = None
    data: dict[str, JsonValue]


class Repo:
    def __init__(self, spec: RunSpec, session: Session, *, fixture_mode: bool = False):
        self._spec = RunSpec.model_validate(spec.model_dump(mode="json"))
        if (self._spec.mode == "fixture") != fixture_mode:
            raise ValueError("Fixture runs require an explicitly isolated fixture namespace")
        self.namespace = "fixture" if fixture_mode else "product"
        self.session = session
        key = (self.namespace, self._spec.run_id)
        existing = session.get(RunRow, key)
        payload = self._spec.model_dump(mode="json")
        if existing is None:
            session.add(
                RunRow(
                    namespace=self.namespace,
                    run_id=self._spec.run_id,
                    spec=payload,
                    status="pending",
                    published=False,
                )
            )
            session.flush()
        elif existing.spec != payload:
            raise ValueError("RunSpec is immutable; use a new run_id for a changed snapshot")

    @property
    def spec(self) -> RunSpec:
        return self._spec.model_copy(deep=True)

    def _run(self) -> RunRow:
        return self.session.get(RunRow, (self.namespace, self._spec.run_id))

    def run_state(self) -> dict:
        row = self._run()
        return {"spec": self.spec, "status": row.status, "published": row.published}

    def set_run_status(self, status: str, *, published: bool = False) -> None:
        if status not in {"pending", "running", "succeeded", "degraded", "blocked", "failed"}:
            raise ValueError("Invalid run status")
        if published and status not in {"succeeded", "degraded"}:
            raise ValueError("Only successful/degraded complete runs can be published")
        row = self._run()
        if row.published:
            raise ValueError("Published run is immutable; reset projections or use a new run")
        row.status, row.published = status, published
        self.session.flush()

    def publish(self, status: str = "succeeded") -> None:
        self.set_run_status(status, published=True)

    def _query(self, kind: type[T], *, store_id=None, sku=None, case_id=None):
        if ARTIFACT_TYPES.get(kind.__name__) is not kind:
            raise ValueError("Only registered artifact contracts can be read")
        if store_id is not None and store_id not in self._spec.stores:
            raise ValueError("Store is outside this RunSpec")
        query = select(ArtifactRow).where(
            ArtifactRow.namespace == self.namespace,
            ArtifactRow.run_id == self._spec.run_id,
            ArtifactRow.kind == kind.__name__,
            ArtifactRow.available_at.is_not(None),
            ArtifactRow.available_at <= instant(self._spec.as_of),
        )
        if store_id is not None:
            scope = and_(
                ArtifactScopeRow.namespace == ArtifactRow.namespace,
                ArtifactScopeRow.run_id == ArtifactRow.run_id,
                ArtifactScopeRow.kind == ArtifactRow.kind,
                ArtifactScopeRow.id == ArtifactRow.id,
                ArtifactScopeRow.version == ArtifactRow.version,
            )
            query = query.where(
                or_(
                    exists().where(scope, ArtifactScopeRow.store_id == store_id),
                    ~exists().where(scope),
                )
            )
        for column, value in ((ArtifactRow.sku, sku), (ArtifactRow.case_id, case_id)):
            if value is not None:
                query = query.where(column == value)
        return query

    def list(self, kind: type[T], *, store_id=None, sku=None, case_id=None) -> tuple[T, ...]:
        rows = self.session.scalars(
            self._query(kind, store_id=store_id, sku=sku, case_id=case_id).order_by(
                ArtifactRow.id, ArtifactRow.available_at, ArtifactRow.version
            )
        )
        return tuple(kind.model_validate(row.payload) for row in rows)

    def get(self, kind: type[T], id: str, version: str | None = None) -> T | None:
        query = self._query(kind).where(ArtifactRow.id == id)
        if version is not None:
            query = query.where(ArtifactRow.version == version)
        row = self.session.scalar(
            query.order_by(ArtifactRow.available_at.desc(), ArtifactRow.version.desc()).limit(1)
        )
        return None if row is None else kind.model_validate(row.payload)

    def _scopes(self, kind: str, id: str, version: str) -> set[str]:
        return set(
            self.session.scalars(
                select(ArtifactScopeRow.store_id).where(
                    ArtifactScopeRow.namespace == self.namespace,
                    ArtifactScopeRow.run_id == self._spec.run_id,
                    ArtifactScopeRow.kind == kind,
                    ArtifactScopeRow.id == id,
                    ArtifactScopeRow.version == version,
                )
            )
        )

    def _input(self, ref: ArtifactRef) -> tuple[SourceRecord, set[str]]:
        if ref.kind.startswith("erp."):
            table = ref.kind.removeprefix("erp.")
            row = self.session.scalar(
                self._erp_query(table).where(ERPRow.id == ref.id, ERPRow.version == ref.version)
            )
            item = ERPRecord.model_validate(row.payload) if row else None
            scopes = {item.store_id} if item and item.store_id else set()
        else:
            kind = ARTIFACT_TYPES.get(ref.kind)
            item = self.get(kind, ref.id, ref.version) if kind else None
            scopes = self._scopes(ref.kind, ref.id, ref.version) if item else set()
        if item is None:
            raise ValueError(f"Input is unavailable in this run: {ref.kind}/{ref.id}/{ref.version}")
        return item, scopes

    def put(
        self,
        dto: T,
        *,
        store_id: str | None = None,
        sku: str | None = None,
        case_id: str | None = None,
    ) -> None:
        kind = type(dto).__name__
        if ARTIFACT_TYPES.get(kind) is not type(dto):
            raise ValueError("Only registered artifact contracts can be written")
        dto = type(dto).model_validate(dto.model_dump(mode="json"))
        if self._run().published and not isinstance(dto, (Decision, Reservation, Clarification)):
            raise ValueError("Published run artifacts are immutable")
        scopes = set()
        direct_store = getattr(dto, "store_id", None)
        if isinstance(dto, SourceDocument):
            direct_store = dto.meta.get("store_id")
        direct_store = direct_store or getattr(dto, "scope", {}).get("store_id")
        scopes.update(getattr(dto, "store_ids", ()))
        if direct_store:
            scopes.add(direct_store)
        if store_id:
            if direct_store and direct_store != store_id:
                raise ValueError("Store index contradicts artifact content")
            scopes.add(store_id)
        if isinstance(dto, DerivedRecord):
            if dto.run_id != self._spec.run_id or dto.scenario_id != self._spec.scenario_id:
                raise ValueError("Derived artifact belongs to another run/scenario")
            if dto.available_at is not None and dto.available_at > self._spec.as_of:
                raise ValueError("Derived artifact is from the future")
            required_refs = []
            if isinstance(dto, Observation):
                for evidence in dto.evidence:
                    document = self.get(
                        SourceDocument, evidence.document_id, evidence.document_version
                    )
                    segment_ref = next(
                        (
                            ref
                            for ref in dto.input_refs
                            if ref.kind == "Segment" and ref.id == evidence.segment_id
                        ),
                        None,
                    )
                    segment = (
                        self.get(Segment, segment_ref.id, segment_ref.version)
                        if segment_ref
                        else None
                    )
                    if document is None or segment is None:
                        raise ValueError("Observation evidence is unavailable in this run")
                    evidence.validate_against(document, segment)
                    required_refs.extend(
                        (
                            ArtifactRef(
                                kind="SourceDocument", id=document.id, version=document.version
                            ),
                            ArtifactRef(kind="Segment", id=segment.id, version=segment.version),
                        )
                    )
            if isinstance(dto, EntityLink):
                observation_ref = next(
                    (
                        ref
                        for ref in dto.input_refs
                        if ref.kind == "Observation" and ref.id == dto.observation_id
                    ),
                    None,
                )
                observation = (
                    self.get(Observation, observation_ref.id, observation_ref.version)
                    if observation_ref
                    else None
                )
                if observation is None:
                    raise ValueError("Linked observation is unavailable in this run")
                required_refs.append(
                    ArtifactRef(kind="Observation", id=observation.id, version=observation.version)
                )
            if isinstance(dto, EvidenceRelation):
                required_refs.extend((dto.from_ref, dto.to_ref, *dto.evidence_refs))
            if any(ref not in dto.input_refs for ref in required_refs):
                raise ValueError("Derived input_refs must declare its referenced evidence/facts")
            for ref in dto.input_refs:
                item, input_scopes = self._input(ref)
                scopes.update(input_scopes)
                if dto.available_at is None or dto.available_at < item.available_at:
                    raise ValueError("Derived availability must include every input's availability")
        if isinstance(dto, Segment):
            candidates = self.session.scalars(
                self._query(SourceDocument)
                .where(
                    ArtifactRow.id == dto.document_id,
                    ArtifactRow.payload["text_version"].as_string() == dto.text_version,
                )
                .order_by(ArtifactRow.available_at, ArtifactRow.version)
            )
            document = None
            for candidate in candidates:
                parent = SourceDocument.model_validate(candidate.payload)
                try:
                    dto.validate_against(parent)
                except ValueError:
                    continue
                if dto.available_at is not None and dto.available_at >= parent.available_at:
                    document = parent
                    break
            if document is None:
                raise ValueError("Segment document is unavailable in this run")
            scopes.update(self._scopes("SourceDocument", document.id, document.version))
        if not scopes <= set(self._spec.stores):
            raise ValueError("Artifact inputs/content are outside this RunSpec's stores")
        direct_sku = getattr(dto, "sku", None)
        direct_case = getattr(dto, "case_id", None)
        for supplied, direct in ((sku, direct_sku), (case_id, direct_case)):
            if supplied and direct and supplied != direct:
                raise ValueError("Artifact index contradicts its content")
        payload = dto.model_dump(mode="json")
        key = (self.namespace, self._spec.run_id, kind, dto.id, dto.version)
        values = dict(
            namespace=self.namespace,
            run_id=self._spec.run_id,
            kind=kind,
            id=dto.id,
            version=dto.version,
            store_id=next(iter(scopes)) if len(scopes) == 1 else None,
            sku=sku or direct_sku,
            case_id=case_id or direct_case,
            available_at=instant(dto.available_at) if dto.available_at else None,
            computed_at=instant(dto.computed_at) if isinstance(dto, DerivedRecord) else None,
            producer=getattr(dto, "producer", None),
            input_refs=payload.get("input_refs", []),
            payload=payload,
        )
        old = self.session.get(ArtifactRow, key)
        if old is not None:
            if (
                any(getattr(old, k) != v for k, v in values.items())
                or self._scopes(kind, dto.id, dto.version) != scopes
            ):
                raise ValueError("Artifact version is immutable")
            return
        self.session.add(ArtifactRow(**values))
        self.session.flush()
        for scope in scopes:
            self.session.add(
                ArtifactScopeRow(
                    namespace=self.namespace,
                    run_id=self._spec.run_id,
                    kind=kind,
                    id=dto.id,
                    version=dto.version,
                    store_id=scope,
                )
            )
        self.session.flush()

    def save_module_run(self, module: ModuleRun) -> None:
        module = ModuleRun.model_validate(module.model_dump(mode="json"))
        if module.run_id != self._spec.run_id or self._run().published:
            raise ValueError("Invalid run or already published module state")
        self.session.merge(
            ModuleRunRow(
                namespace=self.namespace,
                run_id=self._spec.run_id,
                module_id=module.module_id,
                payload=module.model_dump(mode="json"),
            )
        )
        self.session.flush()

    def module_runs(self) -> tuple[ModuleRun, ...]:
        rows = self.session.scalars(
            select(ModuleRunRow)
            .where(
                ModuleRunRow.namespace == self.namespace,
                ModuleRunRow.run_id == self._spec.run_id,
            )
            .order_by(ModuleRunRow.module_id)
        )
        return tuple(ModuleRun.model_validate(row.payload) for row in rows)

    def reset_projections(self) -> int:
        query = delete(ArtifactRow).where(
            ArtifactRow.namespace == self.namespace,
            ArtifactRow.run_id == self._spec.run_id,
            ArtifactRow.kind.not_in(DURABLE_KINDS),
        )
        count = self.session.execute(query).rowcount
        self.session.execute(
            delete(ModuleRunRow).where(
                ModuleRunRow.namespace == self.namespace, ModuleRunRow.run_id == self._spec.run_id
            )
        )
        row = self._run()
        row.published, row.status = False, "pending"
        self.session.flush()
        return count

    def _erp_query(self, table: str, *, store_id: str | None = None, sku: str | None = None):
        if table not in ERP_TABLES:
            raise ValueError("Unknown ERP table")
        if store_id is not None and store_id not in self._spec.stores:
            raise ValueError("Store is outside this RunSpec")
        query = select(ERPRow).where(
            ERPRow.namespace == self.namespace,
            ERPRow.run_id == self._spec.run_id,
            ERPRow.table_name == table,
            ERPRow.available_at.is_not(None),
            ERPRow.available_at <= instant(self._spec.as_of),
            or_(ERPRow.store_id.is_(None), ERPRow.store_id.in_(self._spec.stores)),
        )
        if store_id is not None:
            query = query.where(or_(ERPRow.store_id == store_id, ERPRow.store_id.is_(None)))
        if sku is not None:
            query = query.where(ERPRow.sku == sku)
        return query

    def put_erp(self, fact: ERPRecord) -> None:
        fact = ERPRecord.model_validate(fact.model_dump(mode="json"))
        if fact.table not in ERP_TABLES or self._run().published:
            raise ValueError("Invalid ERP table or published run")
        if fact.store_id is not None and fact.store_id not in self._spec.stores:
            raise ValueError("ERP store is outside this RunSpec")
        if fact.data.get("store_id", fact.store_id) != fact.store_id:
            raise ValueError("ERP store index contradicts payload")
        if fact.data.get("sku", fact.sku) != fact.sku:
            raise ValueError("ERP SKU index contradicts payload")
        key = (self.namespace, self._spec.run_id, fact.table, fact.id, fact.version)
        payload = fact.model_dump(mode="json")
        old = self.session.get(ERPRow, key)
        if old is not None:
            if old.payload != payload:
                raise ValueError("ERP fact version is immutable")
            return
        self.session.add(
            ERPRow(
                namespace=self.namespace,
                run_id=self._spec.run_id,
                table_name=fact.table,
                id=fact.id,
                version=fact.version,
                store_id=fact.store_id,
                sku=fact.sku,
                available_at=instant(fact.available_at) if fact.available_at else None,
                payload=payload,
            )
        )
        self.session.flush()

    def list_erp(self, table: str, *, store_id=None, sku=None) -> tuple[ERPRecord, ...]:
        rows = self.session.scalars(
            self._erp_query(table, store_id=store_id, sku=sku).order_by(ERPRow.id, ERPRow.version)
        )
        return tuple(ERPRecord.model_validate(row.payload) for row in rows)


@contextmanager
def repo_session(engine: Engine, spec: RunSpec, *, fixture_mode: bool = False) -> Iterator[Repo]:
    with Session(engine) as session, session.begin():
        yield Repo(spec, session, fixture_mode=fixture_mode)
