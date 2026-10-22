"""PLT-03: run-scoped artifact store with the `as_of` filter inside the repo (RFC §4.3)."""

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import text

from tessera.core.contracts import ModuleResult, ModuleRun, Observation, RunSpec, SourceDocument
from tessera.core.contracts.common import SourceRef
from tessera.core.db import SCHEMA_VERSION, SchemaMismatch, connect
from tessera.core.fixtures import read_fixtures
from tessera.core.repo import (
    ImmutableArtifact,
    LookAhead,
    Repo,
    RunClosed,
    RunNotFound,
    create_run,
    list_module_runs,
    list_runs,
    put_erp,
    put_module_run,
    reset_run,
    run_status,
    set_run_status,
)

FIXTURES = Path(__file__).resolve().parents[3] / "data" / "fixtures"
ORIGINAL = "doc-20260918-2115-mil01"
CORRECTION = "doc-20260918-2207-mil01-corr"


@pytest.fixture
def engine(tmp_path):
    return connect(f"sqlite:///{tmp_path / 'test.db'}")


@pytest.fixture(scope="module")
def records():
    return read_fixtures(FIXTURES)[1]


def spec(run_id: str, as_of: datetime, scenario_id: str = "historical") -> RunSpec:
    return RunSpec(
        run_id=run_id,
        scenario_id=scenario_id,
        as_of=as_of,
        stores=("MIL01",),
        source_manifest_hash="sha256:test",
        config_hash="sha256:test",
        code_version="test",
        mode="live",
        modules=(),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )


def open_run(engine, run_id: str, as_of: datetime) -> Repo:
    s = spec(run_id, as_of)
    create_run(engine, s)
    return Repo(engine, s)


def of_document(records, document_id: str, run_id: str) -> list:
    """Fixture records of one document, derived ones re-stamped for `run_id`."""
    out = []
    for r in records:
        if r.id == document_id or getattr(r, "document_id", None) == document_id:
            out.append(r.model_copy(update={"run_id": run_id}) if hasattr(r, "run_id") else r)
    return out


def available(records, document_id: str) -> datetime:
    return next(r.available_at for r in records if r.id == document_id)


def test_t1_t2_t1_correction_does_not_leak(engine, records) -> None:
    """RFC §7.3 test 1: T1 → T2 with a correction → T1 returns the original state."""
    t1 = available(records, ORIGINAL) + timedelta(minutes=1)
    t2 = available(records, CORRECTION) + timedelta(minutes=1)

    run1 = open_run(engine, "t1", t1)
    run1.put(*of_document(records, ORIGINAL, "t1"))
    with pytest.raises(LookAhead):
        run1.put(*of_document(records, CORRECTION, "t1"))
    set_run_status(engine, "t1", "published")
    before = (run1.list(SourceDocument), run1.list(Observation, store_id="MIL01"))

    run2 = open_run(engine, "t2", t2)
    run2.put(*of_document(records, ORIGINAL, "t2"), *of_document(records, CORRECTION, "t2"))
    set_run_status(engine, "t2", "published")
    assert {d.id for d in run2.list(SourceDocument)} == {ORIGINAL, CORRECTION}

    again = Repo.open(engine, "t1")
    assert (again.list(SourceDocument), again.list(Observation, store_id="MIL01")) == before
    assert {d.id for d in again.list(SourceDocument)} == {ORIGINAL}
    assert all(o.run_id == "t1" for o in again.list(Observation))
    assert again.get(SourceDocument, CORRECTION) is None


def test_as_of_filters_inside_a_run(engine, records) -> None:
    """A record stored in the run but later than a narrower view is not returned."""
    doc = next(r for r in records if r.id == ORIGINAL)
    run = open_run(engine, "r", doc.available_at)
    run.put(doc)
    earlier = Repo(engine, spec("r", doc.available_at - timedelta(seconds=1)))
    assert earlier.list(SourceDocument) == []
    assert earlier.get(SourceDocument, ORIGINAL) is None
    assert run.get(SourceDocument, ORIGINAL) == doc


def test_unknown_availability_excluded_unless_asked(engine, records) -> None:
    doc = next(r for r in records if r.id == ORIGINAL)
    unknown = doc.model_copy(
        update={"id": "doc-unknown", "available_at": None, "availability_basis": "unknown"}
    )
    run = open_run(engine, "r", doc.available_at)
    run.put(doc, unknown)
    assert [d.id for d in run.list(SourceDocument)] == [ORIGINAL]
    assert [d.id for d in run.list(SourceDocument, include_unknown=True)] == [
        ORIGINAL,
        "doc-unknown",
    ]


def test_filters_by_column_and_payload(engine, records) -> None:
    run = open_run(engine, "r", datetime(2026, 10, 22, tzinfo=UTC))
    run.put(*(r.model_copy(update={"run_id": "r"}) if hasattr(r, "run_id") else r for r in records))
    assert {o.store_id for o in run.list(Observation, store_id="NYC01")} == {"NYC01"}
    emails = run.list(SourceDocument, where={"source_type": "email"})
    assert len(emails) == 7
    assert run.list(Observation, where={"document_id": ORIGINAL})
    assert all(
        o.document_id == ORIGINAL for o in run.list(Observation, where={"document_id": ORIGINAL})
    )


def test_put_is_idempotent_and_immutable(engine, records) -> None:
    doc = next(r for r in records if r.id == ORIGINAL)
    run = open_run(engine, "r", doc.available_at)
    assert run.put(doc) == 1
    assert run.put(doc) == 0
    with pytest.raises(ImmutableArtifact):
        run.put(doc.model_copy(update={"text": "changed"}))
    assert run.put(doc.model_copy(update={"version": "v2", "text": "changed"})) == 1
    assert run.get(SourceDocument, ORIGINAL).version == "v2"
    assert run.get(SourceDocument, ORIGINAL, version="v1") == doc


def test_put_same_record_twice_in_one_call(engine, records) -> None:
    doc = next(r for r in records if r.id == ORIGINAL)
    run = open_run(engine, "r", doc.available_at)
    assert run.put(doc, doc) == 1
    assert len(run.list(SourceDocument)) == 1
    other = doc.model_copy(update={"id": "doc-other"})
    with pytest.raises(ImmutableArtifact):
        run.put(other, other.model_copy(update={"text": "changed"}))
    assert [d.id for d in run.list(SourceDocument)] == [ORIGINAL]


def test_put_is_all_or_nothing(engine, records) -> None:
    doc = next(r for r in records if r.id == ORIGINAL)
    late = next(r for r in records if r.id == CORRECTION)
    run = open_run(engine, "r", doc.available_at)
    with pytest.raises(LookAhead):
        run.put(doc, late)
    assert run.list(SourceDocument) == []


def test_derived_record_must_belong_to_the_run(engine, records) -> None:
    obs = next(r for r in records if isinstance(r, Observation))
    run = open_run(engine, "r", datetime(2026, 10, 22, tzinfo=UTC))
    with pytest.raises(ValueError, match="belongs to run"):
        run.put(obs)  # fixture run_id
    with pytest.raises(ValueError, match="belongs to run"):
        run.put(obs.model_copy(update={"run_id": "r", "scenario_id": "what-if"}))


def test_only_contract_records_are_storable(engine) -> None:
    run = open_run(engine, "r", datetime(2026, 10, 22, tzinfo=UTC))
    with pytest.raises(TypeError):
        run.put(spec("x", datetime(2026, 10, 22, tzinfo=UTC)))  # type: ignore[arg-type]


def test_closed_runs_reject_writes(engine, records) -> None:
    doc = next(r for r in records if r.id == ORIGINAL)
    run = open_run(engine, "r", doc.available_at)
    assert run_status(engine, "r") == "pending"
    set_run_status(engine, "r", "running")
    set_run_status(engine, "r", "published")
    with pytest.raises(RunClosed):
        run.put(doc)
    with pytest.raises(RunClosed):
        set_run_status(engine, "r", "failed")


def test_run_lifecycle(engine) -> None:
    open_run(engine, "a", datetime(2026, 10, 1, tzinfo=UTC))
    open_run(engine, "b", datetime(2026, 10, 2, tzinfo=UTC))
    set_run_status(engine, "b", "published")
    with pytest.raises(ValueError, match="already exists"):
        create_run(engine, spec("a", datetime(2026, 10, 1, tzinfo=UTC)))
    assert [(s.run_id, st) for s, st in list_runs(engine)] == [("b", "published"), ("a", "pending")]
    assert [s.run_id for s, _ in list_runs(engine, status="published")] == ["b"]
    with pytest.raises(RunNotFound):
        Repo.open(engine, "missing")
    assert Repo.open(engine, "a").spec == spec("a", datetime(2026, 10, 1, tzinfo=UTC))


def test_module_runs(engine) -> None:
    open_run(engine, "r", datetime(2026, 10, 1, tzinfo=UTC))
    put_module_run(
        engine, ModuleRun(run_id="r", module_id="src.email", mode="live", status="running")
    )
    result = ModuleResult(
        module_id="src.email",
        module_version="1",
        status="succeeded",
        counts={"documents": 3},
        errors=(),
        abstentions=(),
    )
    done = ModuleRun(
        run_id="r", module_id="src.email", mode="live", status="succeeded", result=result
    )
    put_module_run(engine, done)
    assert list_module_runs(engine, "r") == [done]


def test_reset_deletes_only_that_run(engine, records) -> None:
    doc = next(r for r in records if r.id == ORIGINAL)
    for run_id in ("a", "b"):
        open_run(engine, run_id, doc.available_at).put(doc)
    put_module_run(engine, ModuleRun(run_id="a", module_id="m", mode="live", status="pending"))
    put_erp(engine, [Row(available_at=doc.available_at)])
    assert reset_run(engine, "a") == 1
    with pytest.raises(RunNotFound):
        run_status(engine, "a")
    assert Repo.open(engine, "b").list(SourceDocument) == [doc]
    assert len(Repo.open(engine, "b").erp("sales")) == 1
    with pytest.raises(RunNotFound):
        reset_run(engine, "a")


@dataclass(frozen=True)
class Row:
    """Same shape as `modules.sources.erp.ERPRow`."""

    table: str = "sales"
    id: str = "sales-1"
    version: str = "v1"
    available_at: datetime | None = datetime(2026, 10, 10, 4, tzinfo=UTC)
    availability_basis: str = "next_day_0600_local"
    source_refs: tuple[SourceRef, ...] = (
        SourceRef(uri="erp/sales.csv", content_hash="sha256:x", locator="row=2"),
    )
    data: dict[str, Any] = field(
        default_factory=lambda: {
            "store_id": "MIL01",
            "sku": "ABC-999",
            "business_date": date(2026, 10, 9),
            "posted_at": datetime(2026, 10, 9, 21, tzinfo=UTC),
            "net_sales_lc": Decimal("1250.50"),
            "units_sold": 3,
            "note": None,
        }
    )


def test_erp_rows_round_trip_and_as_of(engine) -> None:
    row = Row()
    unknown = Row(id="sales-unknown", available_at=None, availability_basis="unknown")
    later = Row(id="sales-2", available_at=datetime(2026, 10, 11, 4, tzinfo=UTC))
    other = Row(id="sales-3", data={**Row().data, "store_id": "NYC01"})
    assert put_erp(engine, [row, unknown, later, other, row]) == 4
    assert put_erp(engine, [row]) == 0

    open_run(engine, "r", datetime(2026, 10, 10, 12, tzinfo=UTC))
    repo = Repo.open(engine, "r")
    got = repo.erp("sales", store_id="MIL01")
    assert [r.id for r in got] == ["sales-1"]
    assert dict(got[0].data) == row.data
    assert type(got[0].data["net_sales_lc"]) is Decimal
    assert got[0].source_refs == row.source_refs
    assert got[0].available_at == row.available_at
    assert [r.id for r in repo.erp("sales", sku="ABC-999")] == ["sales-1", "sales-3"]
    assert repo.erp("stock") == []


def test_schema_mismatch_is_refused(tmp_path) -> None:
    url = f"sqlite:///{tmp_path / 'old.db'}"
    engine = connect(url)
    with engine.begin() as conn:
        conn.execute(text(f"PRAGMA user_version={SCHEMA_VERSION + 1}"))
    with pytest.raises(SchemaMismatch):
        connect(url)


def test_naive_datetimes_never_reach_the_db(engine) -> None:
    with pytest.raises(Exception, match="naive"):
        put_erp(engine, [Row(available_at=datetime(2026, 10, 10))])
