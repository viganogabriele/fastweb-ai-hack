"""Reports stay frozen and citation pins resolve only inside the selected run."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert

from tessera.api.main import create_app
from tessera.core.config import Settings
from tessera.core.contracts import ArtifactRef, Case, Citation, Report, RunSpec, SourceDocument
from tessera.core.db import artifacts, connect
from tessera.core.registry import Registry
from tessera.core.run_repo import repo_session


def body(mode="recorded"):
    return dict(
        scenario_id="historical",
        as_of="2026-10-22T20:00:00Z",
        stores=["MIL01"],
        source_manifest_hash="sources",
        config_hash="config",
        code_version="test",
        mode=mode,
        modules=[],
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=[],
    )


def document(at="2026-10-22T19:00:00Z", store="MIL01"):
    return SourceDocument(
        id="doc-1",
        version="v1",
        available_at=at,
        availability_basis="test",
        source_refs=(),
        source_type="email",
        connector="src.email",
        uri="test://mail",
        content_hash="hash",
        origin=None,
        text="Hi 🧥 店",
        text_version="v1",
        meta={"store_id": store},
    )


@pytest.fixture
def service(tmp_path):
    engine = connect(f"sqlite:///{tmp_path / 'reports.db'}")
    app = create_app(
        engine=engine,
        fixture_engine=engine,
        registry=Registry(),
        settings=Settings(_env_file=None, fixture_mode=True),
    )
    with TestClient(app) as client:
        yield client, engine, app
    engine.dispose()


def case(spec, *, version="v1", owner="allocation"):
    return Case(
        id="case-1",
        version=version,
        available_at="2026-10-22T19:00:00Z",
        availability_basis="test",
        source_refs=(),
        run_id=spec.run_id,
        scenario_id=spec.scenario_id,
        computed_at=spec.as_of,
        input_refs=(),
        producer="test",
        producer_version="1",
        case_type="unmet_demand",
        store_id="MIL01",
        scope_level="sku",
        scope_id="SKU-999",
        window_start=spec.as_of,
        window_end=spec.as_of,
        status="open",
        owner=owner,
        priority="medium",
        priority_reason="test",
        first_available_at=spec.as_of,
        last_received_at=spec.as_of,
        supporting=(),
        contradicting=(),
        n_documents=1,
        n_origin_groups=1,
        n_unknown_origins=0,
        blocking_uncertainties=(),
        context_refs=(),
    )


def report(spec, *, version="v1", view="by_office", citations=None):
    pins = (
        citations
        if citations is not None
        else (
            Citation(ref=ArtifactRef(kind="Case", id="case-1", version="v1"), field="owner"),
            Citation(ref=ArtifactRef(kind="SourceDocument", id="doc-1", version="v1")),
        )
    )
    return Report(
        id=f"report-{view}",
        version=version,
        available_at=spec.as_of,
        availability_basis="test",
        source_refs=(),
        run_id=spec.run_id,
        scenario_id=spec.scenario_id,
        computed_at=spec.as_of,
        input_refs=tuple(c.ref for c in pins),
        producer="out.reports",
        producer_version="1",
        as_of=spec.as_of,
        view=view,
        markdown=f"Frozen brief {version} [1] [2]",
        citations=pins,
        generated_by="template:test",
        input_version_hash="hash",
    )


def seed(engine, run_id="one", *, mode="recorded", published=True, versions=False):
    spec = RunSpec(run_id=run_id, **body(mode))
    with repo_session(engine, spec, fixture_mode=mode == "fixture") as repo:
        repo.put(document(), case(spec), report(spec))
        if versions:
            repo.put(case(spec, version="v2", owner="marketing"))
            repo.put(report(spec, version="v2"), report(spec, version="v10"))
            repo.put(report(spec, view="by_priority"))
        if published:
            repo.publish()
    return spec


def test_list_filters_views_and_selects_latest_publication_not_lexical_version(service):
    client, engine, _ = service
    seed(engine, versions=True)
    items = client.get("/api/runs/one/reports").json()
    assert [(r["view"], r["version"]) for r in items] == [
        ("by_office", "v10"),
        ("by_priority", "v1"),
    ]
    assert client.get("/api/runs/one/reports?view=by_priority").json() == [items[1]]
    assert client.get("/api/runs/one/reports?view=missing").json() == []


def test_owner_uses_exact_case_version_and_resolves_full_original_citations(service):
    client, engine, _ = service
    seed(engine, versions=True)
    response = client.get("/api/runs/one/reports/allocation?view=by_office")
    assert response.status_code == 200
    (detail,) = response.json()
    assert detail["report"]["markdown"] == "Frozen brief v10 [1] [2]"
    assert detail["citations"][0]["artifact"]["version"] == "v1"
    assert detail["citations"][0]["artifact"]["owner"] == "allocation"
    assert detail["citations"][1]["artifact"]["text"] == "Hi 🧥 店"
    assert detail["citations"][0]["citation"] == detail["report"]["citations"][0]
    assert client.get("/api/runs/one/reports/marketing").status_code == 404
    assert client.get("/api/runs/one/reports/missing").status_code == 404


@pytest.mark.parametrize("suffix", ["reports", "reports/allocation"])
def test_publication_missing_run_and_fixture_namespace_apply_to_all_report_reads(service, suffix):
    client, engine, app = service
    seed(engine)
    seed(engine, "pending", published=False)
    seed(engine, "fixture", mode="fixture")
    assert client.get(f"/api/runs/one/{suffix}").status_code == 200
    assert client.get(f"/api/runs/pending/{suffix}").status_code == 409
    assert client.get(f"/api/runs/missing/{suffix}").status_code == 404
    assert client.get(f"/api/runs/fixture/{suffix}").status_code == 404
    assert client.get(f"/api/runs/fixture/{suffix}?fixture=true").status_code == 200
    app.state.settings = Settings(_env_file=None, fixture_mode=False)
    assert client.get(f"/api/runs/fixture/{suffix}?fixture=true").status_code == 403


@pytest.mark.parametrize("target", ["missing", "foreign", "future", "unknown-kind"])
def test_citations_cannot_resolve_from_another_run_store_clock_or_kind(service, target):
    client, engine, _ = service
    seed(engine, "other-run")
    spec = RunSpec(run_id="one", **body())
    with repo_session(engine, spec) as repo:
        repo.put(case(spec))
        doc = document(
            at="2026-10-23T00:00:00Z" if target == "future" else "2026-10-22T19:00:00Z",
            store="NYC01" if target == "foreign" else "MIL01",
        )
        if target in ("foreign", "future"):
            repo.session.execute(
                insert(artifacts).values(
                    run_id="one",
                    kind="SourceDocument",
                    id=doc.id,
                    version=doc.version,
                    store_id=doc.meta["store_id"],
                    available_at=doc.available_at,
                    payload=doc.model_dump(mode="json"),
                    input_refs=[],
                )
            )
        item = report(spec)
        if target == "unknown-kind":
            item = item.model_copy(
                update={
                    "citations": (
                        *item.citations[:1],
                        Citation(ref=ArtifactRef(kind="Unsupported", id="doc-1", version="v1")),
                    )
                }
            )
        # Corrupt persisted reports independently of the normal write checks.
        repo.session.execute(
            insert(artifacts).values(
                run_id="one",
                kind="Report",
                id=item.id,
                version=item.version,
                available_at=item.available_at,
                payload=item.model_dump(mode="json"),
                input_refs=[],
            )
        )
        repo.publish()
    for path in ("reports", "reports/allocation"):
        response = client.get(f"/api/runs/one/{path}")
        assert response.status_code == 409
        assert "doc-1" not in response.text


def test_empty_run_has_no_reports_and_gets_do_not_regenerate_artifacts(service):
    client, engine, _ = service
    spec = RunSpec(run_id="empty", **body())
    with repo_session(engine, spec) as repo:
        repo.publish()
    assert client.get("/api/runs/empty/reports").json() == []
    assert client.get("/api/runs/empty/reports/allocation").status_code == 404
    with repo_session(engine, "empty") as repo:
        assert repo.list(Report) == []
