"""PLT-03 integration tests use real temporary SQLite databases and synthetic facts."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from tessera.cli import main
from tessera.core.contracts import (
    ArtifactRef,
    Decision,
    EvidenceRelation,
    Observation,
    RunSpec,
    Segment,
    SourceDocument,
)
from tessera.core.contracts.common import SourceRef
from tessera.core.db import RunRow, create_schema, make_engine
from tessera.core.fixtures import load_fixtures
from tessera.core.repo import ERPRecord, repo_session

T1 = datetime(2026, 10, 8, 18, tzinfo=UTC)
T2 = T1 + timedelta(days=1)
SOURCE = SourceRef(uri="synthetic://doc", content_hash="h1")


def spec(id="run-1", *, at=T1, mode="recorded", stores=("MIL01",), refs=()):
    return RunSpec(
        run_id=id,
        scenario_id="historical",
        as_of=at,
        stores=stores,
        source_manifest_hash="sources-v1",
        config_hash="config-v1",
        code_version="v1",
        mode=mode,
        modules=(),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=refs,
    )


def document(id="doc-1", *, at=T1, store="MIL01", text="Five requests."):
    return SourceDocument(
        id=id,
        version="v1",
        available_at=at,
        availability_basis="email_date",
        source_refs=(SOURCE,),
        source_type="email",
        connector="src.email",
        uri=SOURCE.uri,
        content_hash=SOURCE.content_hash,
        origin=None,
        text=text,
        text_version="text-v1",
        meta={"store_id": store},
    )


def observation(doc, run="run-1", *, id="obs-1", at=None):
    return Observation(
        id=id,
        version="v1",
        available_at=at or doc.available_at,
        availability_basis="input_max",
        source_refs=doc.source_refs,
        run_id=run,
        scenario_id="historical",
        computed_at=datetime.now(UTC),
        input_refs=(
            ArtifactRef(kind="SourceDocument", id=doc.id, version=doc.version),
            ArtifactRef(kind="Segment", id=f"{doc.id}-segment", version="v1"),
        ),
        producer="test.extract",
        producer_version="v1",
        extractor_version="v1",
        document_id=doc.id,
        store_id="MIL01",
        kind="unmet_demand",
        quantity={"kind": "unknown"},
        direction="up",
        attribution="staff",
        negated=False,
        evidence=(
            {
                "document_id": doc.id,
                "document_version": doc.version,
                "segment_id": f"{doc.id}-segment",
                "quote": "Five",
                "char_start": 0,
                "char_end": 4,
            },
        ),
    )


def put_document(repo, doc):
    repo.put(doc)
    repo.put(
        Segment(
            id=f"{doc.id}-segment",
            version="v1",
            available_at=doc.available_at,
            availability_basis="document",
            source_refs=doc.source_refs,
            document_id=doc.id,
            text_version=doc.text_version,
            idx=0,
            text=doc.text,
            char_start=0,
            char_end=len(doc.text),
            is_quoted=False,
        )
    )


@pytest.fixture
def engine(tmp_path):
    result = make_engine(f"sqlite:///{tmp_path / 'test.db'}")
    create_schema(result)
    yield result
    result.dispose()


def test_roundtrip_idempotence_and_immutable_versions(engine):
    doc = document()
    obs = observation(doc)
    with repo_session(engine, spec()) as repo:
        put_document(repo, doc)
        put_document(repo, doc)
        repo.put(obs)
        assert repo.get(SourceDocument, doc.id) == doc
        assert repo.list(Observation) == (obs,)
        with pytest.raises(ValueError, match="immutable"):
            repo.put(doc.model_copy(update={"text": "Changed"}))
        second = doc.model_copy(update={"version": "v2", "text": "New version"})
        repo.put(second)
        assert len(repo.list(SourceDocument)) == 2
        assert repo.get(SourceDocument, doc.id, "v1") == doc
        assert repo.get(SourceDocument, doc.id).version == "v2"
    with repo_session(engine, spec()) as repo:
        assert repo.get(Observation, obs.id) == obs


def test_future_unknown_sources_and_timezone_boundary(engine):
    exact = document(at=T1.astimezone(__import__("zoneinfo").ZoneInfo("Asia/Tokyo")))
    with repo_session(engine, spec()) as repo:
        repo.put(exact)
        repo.put(document("future", at=T1 + timedelta(microseconds=1)))
        repo.put(document("unknown", at=None))
        assert repo.list(SourceDocument) == (exact,)
        assert repo.get(SourceDocument, "future") is None
        assert repo.get(SourceDocument, "unknown") is None


def test_t1_t2_correction_t1_and_run_isolation(engine):
    early = document()
    late = document("doc-2", at=T2)
    with repo_session(engine, spec()) as repo:
        put_document(repo, early)
        repo.put(observation(early))
        original = repo.list(Observation)
    with repo_session(engine, spec("run-2", at=T2)) as repo:
        put_document(repo, early)
        put_document(repo, late)
        old = observation(early, "run-2")
        corrected = observation(late, "run-2", id="corrected")
        repo.put(old)
        repo.put(corrected)
        relation = EvidenceRelation(
            **{
                k: v
                for k, v in corrected.model_dump().items()
                if k
                in {
                    "version",
                    "available_at",
                    "availability_basis",
                    "source_refs",
                    "run_id",
                    "scenario_id",
                    "computed_at",
                    "producer",
                    "producer_version",
                }
            },
            id="correction",
            input_refs=(
                ArtifactRef(kind="Observation", id=old.id, version="v1"),
                ArtifactRef(kind="Observation", id=corrected.id, version="v1"),
            ),
            from_ref=ArtifactRef(kind="Observation", id=corrected.id, version="v1"),
            to_ref=ArtifactRef(kind="Observation", id=old.id, version="v1"),
            relation="supersedes",
            basis="later correction",
            evidence_refs=(),
        )
        repo.put(relation)
        assert len(repo.list(Observation)) == 2
        assert repo.list(EvidenceRelation) == (relation,)
    with repo_session(engine, spec()) as repo:
        assert repo.list(Observation) == original
        assert repo.list(EvidenceRelation) == ()
        assert repo.get(SourceDocument, late.id) is None


def test_snapshot_cannot_change_or_be_mutated_by_caller(engine):
    snapshot = spec()
    with repo_session(engine, snapshot) as repo:
        snapshot.model_versions["new"] = "bad"
        repo.spec.model_versions["new"] = "also bad"
        assert repo.spec.model_versions == {}
    with pytest.raises(ValueError, match="immutable"):
        with repo_session(engine, spec(at=T2)):
            pass


def test_store_filters_inherit_source_and_input_scope(engine):
    mil = document()
    nyc = document("nyc", store="NYC01")
    with repo_session(engine, spec(stores=("MIL01", "NYC01"))) as repo:
        repo.put(mil)
        repo.put(nyc)
        segment = Segment(
            id="segment-1",
            version="v1",
            available_at=T1,
            availability_basis="doc",
            source_refs=(SOURCE,),
            document_id=mil.id,
            text_version=mil.text_version,
            idx=0,
            text=mil.text,
            char_start=0,
            char_end=len(mil.text),
            is_quoted=False,
        )
        repo.put(segment)
        assert repo.list(SourceDocument, store_id="MIL01") == (mil,)
        assert repo.list(Segment, store_id="NYC01") == ()
        with pytest.raises(ValueError, match="outside"):
            repo.list(SourceDocument, store_id="ROM01")
    with repo_session(engine, spec("other")) as repo:
        with pytest.raises(ValueError, match="outside"):
            repo.put(nyc)
        with pytest.raises(ValueError, match="contradicts"):
            repo.put(mil, store_id="NYC01")


@pytest.mark.parametrize(
    "change",
    [
        {"run_id": "other"},
        {"scenario_id": "other"},
        {"available_at": T2},
        {"available_at": T1 - timedelta(seconds=1)},
        {"input_refs": (ArtifactRef(kind="SourceDocument", id="missing", version="v1"),)},
    ],
)
def test_invalid_derived_provenance_rejected(engine, change):
    doc = document()
    with repo_session(engine, spec()) as repo:
        put_document(repo, doc)
        with pytest.raises(ValueError):
            repo.put(observation(doc).model_copy(update=change))


def test_job_rollback_and_savepoint_rollback(engine):
    with pytest.raises(RuntimeError):
        with repo_session(engine, spec()) as repo:
            repo.put(document())
            raise RuntimeError("fail")
    with Session(engine) as session:
        assert session.get(RunRow, ("product", "run-1")) is None
    with repo_session(engine, spec()) as repo:
        repo.put(document())
        with pytest.raises(RuntimeError):
            with repo.session.begin_nested():
                repo.put(document("rolled-back"))
                raise RuntimeError("module fails")
        assert repo.get(SourceDocument, "rolled-back") is None
        assert repo.get(SourceDocument, "doc-1") is not None


def test_namespace_collision_and_fixture_guard(engine, tmp_path):
    with repo_session(engine, spec()) as repo:
        repo.put(document())
        with pytest.raises(ValueError, match="fixture namespace"):
            load_fixtures(repo, [], root=tmp_path)
    with repo_session(engine, spec(mode="fixture"), fixture_mode=True) as repo:
        assert repo.list(SourceDocument) == ()
    with pytest.raises(ValueError, match="fixture namespace"):
        with repo_session(engine, spec(mode="fixture")):
            pass


def test_publication_and_reset_preserve_sources_and_human_decisions(engine):
    doc = document()
    with repo_session(engine, spec()) as repo:
        put_document(repo, doc)
        repo.put(observation(doc))
        repo.publish()
        with pytest.raises(ValueError, match="immutable"):
            repo.put(document("late-insertion"))
        decision = Decision(
            id="decision",
            version="v1",
            available_at=T1,
            availability_basis="user",
            source_refs=(),
            run_id="run-1",
            scenario_id="historical",
            computed_at=datetime.now(UTC),
            input_refs=(),
            producer="human",
            producer_version="1",
            option_id="option-1",
            input_version_hash="inputs",
            decision="rejected",
            by="user",
            at=T1,
            idempotency_key="unique",
            dispatch_status="draft",
        )
        repo.put(decision)
        assert repo.reset_projections() == 1
        assert repo.list(Observation) == ()
        assert repo.get(SourceDocument, doc.id) == doc
        assert repo.list(Decision) == (decision,)
        assert repo.run_state()["published"] is False


def test_erp_rows_are_temporal_scoped_immutable_and_available_as_inputs(engine):
    fact = ERPRecord(
        id="sale",
        version="v1",
        available_at=T1,
        availability_basis="next_day",
        source_refs=(SOURCE,),
        table="sales",
        store_id="MIL01",
        sku="STYLE-001",
        data={"net_sales_lc": "12.30", "units_sold": 1, "currency": "EUR"},
    )
    with repo_session(engine, spec()) as repo:
        repo.put_erp(fact)
        repo.put_erp(fact)
        repo.put_erp(fact.model_copy(update={"id": "future", "available_at": T2}))
        assert repo.list_erp("sales") == (fact,)
        assert repo.list_erp("sales", sku="missing") == ()
        with pytest.raises(ValueError, match="immutable"):
            repo.put_erp(fact.model_copy(update={"data": {"units_sold": 99}}))
        doc = document()
        put_document(repo, doc)
        obs = observation(doc)
        obs = obs.model_copy(
            update={
                "input_refs": (
                    *obs.input_refs,
                    ArtifactRef(kind="erp.sales", id="sale", version="v1"),
                )
            }
        )
        repo.put(obs)
        assert repo.list(Observation) == (obs,)


def test_fixture_import_is_atomic_and_requires_authorized_paths(engine, tmp_path):
    path = tmp_path / "records.json"
    path.write_text(
        json.dumps(
            [
                {"kind": "SourceDocument", "payload": document().model_dump(mode="json")},
                {
                    "kind": "SourceDocument",
                    "payload": document("wrong", store="NYC01").model_dump(mode="json"),
                },
            ]
        )
    )
    with repo_session(engine, spec(mode="fixture", refs=(path.name,)), fixture_mode=True) as repo:
        with pytest.raises(ValueError, match="outside"):
            load_fixtures(repo, [path.name], root=tmp_path)
        assert repo.list(SourceDocument) == ()
        with pytest.raises(ValueError, match="not authorized"):
            load_fixtures(repo, ["../secret.json"], root=tmp_path)


def test_real_dev_fixtures_roundtrip_and_cli_reset(engine, tmp_path, capsys):
    root = Path(__file__).resolve().parents[3] / "data/fixtures"
    files = tuple(
        p.relative_to(root).as_posix()
        for directory in ("documents", "observations")
        for p in sorted((root / directory).glob("*.json"))
    )
    snapshot = spec(
        at=datetime(2026, 10, 10, tzinfo=UTC), mode="fixture", stores=("MIL01", "NYC01"), refs=files
    )
    runfile = tmp_path / "run.json"
    runfile.write_text(snapshot.model_dump_json())
    url = str(engine.url)
    main(["fixtures", "load", "--fixture-mode", "--run-spec", str(runfile), "--db-url", url])
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["loaded"] > 0 and receipt["excluded"] == 0
    with repo_session(engine, snapshot, fixture_mode=True) as repo:
        assert len(repo.list(SourceDocument)) == 7
        assert len(repo.list(Observation)) >= 7
        assert all(row.run_id == snapshot.run_id for row in repo.list(Observation))
    main(["reset", "--run", snapshot.run_id, "--fixture-mode", "--db-url", url])
    assert json.loads(capsys.readouterr().out)["removed"] >= 7
    with repo_session(engine, snapshot, fixture_mode=True) as repo:
        assert len(repo.list(SourceDocument)) == 7
        assert repo.list(Observation) == ()


def test_sqlite_foreign_keys_are_enabled(engine):
    with engine.connect() as connection:
        assert connection.scalar(text("PRAGMA foreign_keys")) == 1


def test_segment_resolves_historical_canonical_text_instead_of_latest_document(engine):
    old = document()
    newer = old.model_copy(update={"version": "v2", "text_version": "text-v2", "text": "Changed"})
    with repo_session(engine, spec()) as repo:
        repo.put(old)
        repo.put(newer)
        segment = Segment(
            id="old-segment",
            version="v1",
            available_at=T1,
            availability_basis="document",
            source_refs=(SOURCE,),
            document_id=old.id,
            text_version=old.text_version,
            idx=0,
            text=old.text,
            char_start=0,
            char_end=len(old.text),
            is_quoted=False,
        )
        repo.put(segment)
        assert repo.get(Segment, segment.id) == segment


def test_observation_cannot_hide_future_or_missing_evidence_by_omitting_inputs(engine):
    doc = document()
    with repo_session(engine, spec()) as repo:
        repo.put(doc)
        with pytest.raises(ValueError, match="evidence is unavailable"):
            repo.put(observation(doc).model_copy(update={"input_refs": ()}))
        put_document(repo, doc)
        wrong = observation(doc).model_dump(mode="json")
        wrong["evidence"][0]["quote"] = "Fake"
        with pytest.raises(ValueError, match="canonical document slice"):
            repo.put(Observation.model_validate(wrong))
        missing = observation(document("absent"))
        with pytest.raises(ValueError, match="evidence is unavailable"):
            repo.put(missing)
