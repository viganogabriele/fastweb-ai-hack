"""Snapshot orchestration tests using fake modules and the real artifact repository."""

from datetime import UTC, datetime

import pytest

from tesseract.core.contracts import (
    ModuleManifest,
    ModuleResult,
    ModuleSnapshot,
    RunSpec,
    SourceDocument,
)
from tesseract.core.db import connect
from tesseract.core.orchestrator import run
from tesseract.core.registry import RegisteredModule, Registry
from tesseract.core.run_repo import repo_session


def manifest(module_id, *, requires=(), optional=(), enabled=True, mode="live", params_schema=None):
    return ModuleManifest(
        id=module_id,
        version="1",
        layer="sources",
        description="test module",
        requires=requires,
        optional_inputs=optional,
        produces=("SourceDocument",),
        enabled=enabled,
        mode=mode,
        params_schema=params_schema or {},
    )


def spec(*manifests, run_id="test-run", mode="live"):
    return RunSpec(
        run_id=run_id,
        scenario_id="historical",
        as_of=datetime(2026, 10, 22, tzinfo=UTC),
        stores=("MIL01",),
        source_manifest_hash="sources",
        config_hash="config",
        code_version="test",
        mode=mode,
        modules=tuple(ModuleSnapshot(manifest=m, params={}) for m in manifests),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )


def result(ctx, status="succeeded"):
    return ModuleResult(
        module_id=ctx.manifest.id,
        module_version=ctx.manifest.version,
        status=status,
        counts={},
        errors=(),
        abstentions=(),
    )


@pytest.fixture
def engine(tmp_path):
    engine = connect(f"sqlite:///{tmp_path / 'pipeline.db'}")
    yield engine
    engine.dispose()


def test_selection_adds_required_modules_and_publishes_only_after_last(engine):
    source, consumer = manifest("source"), manifest("consumer", requires=("source",))
    seen = []

    def execute(ctx):
        assert not ctx.repo.run_state()["published"]
        seen.append(ctx.manifest.id)
        return result(ctx)

    registry = Registry(RegisteredModule(m, execute) for m in (consumer, source))
    request = spec(consumer, source)
    statuses = run(request, engine=engine, registry=registry, modules=("consumer",))
    assert seen == ["source", "consumer"]
    assert [s.status for s in statuses] == ["succeeded", "succeeded"]
    with repo_session(engine, request) as repo:
        assert repo.run_state()["published"]
        assert len(repo.module_runs()) == 2
    with pytest.raises(ValueError, match="already been executed"):
        run(request, engine=engine, registry=registry)


def test_failed_module_rolls_back_its_artifacts_and_blocks_dependents(engine):
    source, consumer = manifest("source"), manifest("consumer", requires=("source",))
    called = []

    def failing(ctx):
        ctx.repo.put(
            SourceDocument(
                id="partial",
                version="1",
                available_at=ctx.spec.as_of,
                availability_basis="test",
                source_refs=(),
                source_type="email",
                connector="source",
                uri="test://partial",
                content_hash="partial",
                origin=None,
                text="incomplete",
                text_version="1",
                meta={},
            ),
        )
        raise RuntimeError("failed after writing")

    def forbidden(ctx):
        called.append(ctx.manifest.id)
        return result(ctx)

    request = spec(source, consumer)
    statuses = run(
        request,
        engine=engine,
        registry=Registry(
            (
                RegisteredModule(source, failing),
                RegisteredModule(consumer, forbidden),
            )
        ),
    )
    assert [s.status for s in statuses] == ["failed", "blocked"]
    assert called == []
    with repo_session(engine, request) as repo:
        assert repo.list(SourceDocument) == []
        assert not repo.run_state()["published"]
        assert repo.run_state()["status"] == "failed"


def test_disabled_required_dependency_blocks_and_optional_dependency_degrades(engine):
    disabled = manifest("disabled", enabled=False)
    required = manifest("required", requires=("disabled",))
    optional = manifest("optional", optional=("disabled", "not-installed"))
    called = []

    def execute(ctx):
        called.append((ctx.manifest.id, ctx.missing_optional_inputs))
        return result(ctx)

    statuses = run(
        spec(required, optional, disabled),
        engine=engine,
        registry=Registry(RegisteredModule(m, execute) for m in (required, optional, disabled)),
    )
    assert {s.module_id: s.status for s in statuses} == {
        "disabled": "blocked",
        "required": "blocked",
        "optional": "degraded",
    }
    assert called == [("optional", ("disabled", "not-installed"))]


def test_optional_absence_allows_degraded_publication(engine):
    module = manifest("consumer", optional=("missing",))
    request = spec(module)
    statuses = run(request, engine=engine, registry=Registry((RegisteredModule(module, result),)))
    assert statuses[0].status == "degraded"
    assert "missing" in statuses[0].result.abstentions[0]
    with repo_session(engine, request) as repo:
        assert repo.run_state()["published"]
        assert repo.run_state()["status"] == "degraded"


def test_rejects_cycles_changed_snapshots_and_live_fixture_injection(engine):
    a, b = manifest("a", requires=("b",)), manifest("b", requires=("a",))
    with pytest.raises(ValueError, match="cyclic"):
        run(
            spec(a, b),
            engine=engine,
            registry=Registry((RegisteredModule(a, result), RegisteredModule(b, result))),
        )
    with pytest.raises(ValueError, match="manifest changed"):
        run(
            spec(manifest("a").model_copy(update={"version": "different"})),
            modules=("a",),
            engine=engine,
            registry=Registry((RegisteredModule(manifest("a"), result),)),
        )
    fixture = manifest("fixture", mode="fixture")
    with pytest.raises(ValueError, match="fixture modules require"):
        run(spec(fixture), engine=engine, registry=Registry((RegisteredModule(fixture, result),)))


def test_missing_required_module_blocks_without_reusing_old_artifacts(engine):
    module = manifest("consumer", requires=("not-installed",))
    statuses = run(
        spec(module), engine=engine, registry=Registry((RegisteredModule(module, result),))
    )
    assert statuses[0].status == "blocked"


def test_unsuccessful_return_rolls_back_and_wrong_result_identity_fails(engine):
    module = manifest("producer")

    def wrong(ctx):
        return result(ctx).model_copy(update={"module_id": "someone-else"})

    statuses = run(
        spec(module), engine=engine, registry=Registry((RegisteredModule(module, wrong),))
    )
    assert statuses[0].status == "failed"
    statuses = run(
        spec(module, run_id="blocked-result"),
        engine=engine,
        registry=Registry((RegisteredModule(module, lambda ctx: result(ctx, "blocked")),)),
    )
    assert statuses[0].status == "blocked"


def test_registry_validates_params_duplicates_and_discovers_package(tmp_path, monkeypatch):
    from jsonschema import ValidationError

    module = manifest("producer", params_schema={"type": "object", "required": ["limit"]})
    registry = Registry((RegisteredModule(module, result),))
    with pytest.raises(ValidationError):
        registry.resolve(ModuleSnapshot(manifest=module, params={}))
    with pytest.raises(ValueError, match="duplicate"):
        Registry((RegisteredModule(module, result), RegisteredModule(module, result)))
    package = tmp_path / "fake_pipeline"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "pure.py").write_text("def helper(): return 42\n")
    (package / "entry.py").write_text(
        "from tesseract.core.contracts import ModuleManifest\n"
        f"MANIFEST = ModuleManifest.model_validate_json({module.model_dump_json()!r})\n"
        "def run(ctx): pass\n"
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    assert Registry.discover("fake_pipeline").manifests() == (module,)


def test_disabled_optional_connector_degrades_without_preventing_publish(engine):
    disabled = manifest("disabled", enabled=False)
    consumer = manifest("consumer", optional=("disabled",))
    request = spec(disabled, consumer)
    statuses = run(request, engine=engine, registry=Registry((RegisteredModule(consumer, result),)))
    assert [entry.module_id for entry in statuses] == ["consumer"]
    assert statuses[0].status == "degraded"
    with repo_session(engine, request) as repo:
        assert repo.run_state()["published"]


def test_only_optional_failure_degrades_but_explicit_selection_prevents_publish(engine):
    optional = manifest("optional")
    consumer = manifest("consumer", optional=("optional",))
    registry = Registry(
        (
            RegisteredModule(optional, lambda ctx: result(ctx, "failed")),
            RegisteredModule(consumer, result),
        )
    )
    request = spec(optional, consumer)
    statuses = run(request, engine=engine, registry=registry, modules=("consumer",))
    assert [entry.status for entry in statuses] == ["failed", "degraded"]
    with repo_session(engine, request) as repo:
        assert repo.run_state()["published"]
        assert repo.run_state()["status"] == "degraded"
    explicit = spec(optional, consumer, run_id="explicit")
    run(explicit, engine=engine, registry=registry, modules=("consumer", "optional"))
    with repo_session(engine, explicit) as repo:
        assert not repo.run_state()["published"]


def test_per_run_enabled_switch_preserves_implementation_identity(engine):
    installed = manifest("source")
    disabled = installed.model_copy(update={"enabled": False})
    consumer = manifest("consumer", requires=("source",))
    statuses = run(
        spec(disabled, consumer),
        engine=engine,
        registry=Registry(
            (RegisteredModule(installed, result), RegisteredModule(consumer, result))
        ),
    )
    assert [entry.status for entry in statuses] == ["blocked", "blocked"]


def test_transactional_adapter_preserves_snapshot_scope_and_outer_rollback(engine):
    from tesseract.core.repo import Repo as CanonicalRepo
    from tesseract.core.repo import RunNotFound

    request = spec()
    with pytest.raises(RuntimeError):
        with repo_session(engine, request) as repo:
            request.model_versions["mutated"] = "bad"
            assert repo.spec.model_versions == {}
            raise RuntimeError("rollback job")
    with pytest.raises(RunNotFound):
        CanonicalRepo.open(engine, request.run_id)

    request = spec()
    with repo_session(engine, request) as repo:
        with pytest.raises(ValueError, match="outside"):
            repo.list(SourceDocument, store_id="NYC01")
        document = SourceDocument(
            id="scope-doc",
            version="1",
            available_at=request.as_of,
            availability_basis="test",
            source_refs=(),
            source_type="email",
            connector="test",
            uri="test://scope-doc",
            content_hash="hash",
            origin=None,
            text="hello",
            text_version="1",
            meta={"store_id": "NYC01"},
        )
        with pytest.raises(ValueError, match="outside"):
            repo.put(document)
        valid = document.model_copy(update={"meta": {"store_id": "MIL01"}})
        repo.put(valid)
        assert repo.list(SourceDocument, store_id="MIL01") == [valid]
    with pytest.raises(ValueError, match="immutable"):
        with repo_session(engine, request.model_copy(update={"config_hash": "different"})):
            pass


def test_existing_pending_run_savepoint_does_not_commit_before_outer_job(engine):
    request = spec()
    with repo_session(engine, request):
        pass
    with pytest.raises(RuntimeError):
        with repo_session(engine, request) as repo:
            repo.put(
                SourceDocument(
                    id="rolled-back",
                    version="1",
                    available_at=request.as_of,
                    availability_basis="test",
                    source_refs=(),
                    source_type="email",
                    connector="test",
                    uri="test://rollback",
                    content_hash="hash",
                    origin=None,
                    text="hello",
                    text_version="1",
                    meta={},
                )
            )
            raise RuntimeError("job fails after nested successful put")
    with repo_session(engine, request) as repo:
        assert repo.get(SourceDocument, "rolled-back") is None


def test_module_cannot_mutate_frozen_snapshot(engine):
    module = manifest("source")
    request = spec(module)

    def execute(ctx):
        ctx.spec.model_versions["changed"] = "bad"
        ctx.params["changed"] = "bad"
        ctx.manifest.params_schema["changed"] = "bad"
        return result(ctx)

    run(request, engine=engine, registry=Registry((RegisteredModule(module, execute),)))
    with repo_session(engine, request) as repo:
        assert repo.spec == request
    assert request.model_versions == {}
    assert request.modules[0].params == {}
    assert request.modules[0].manifest.params_schema == {}


def test_cli_executes_snapshot_and_as_of_override_creates_fresh_run(tmp_path, monkeypatch, capsys):
    import json

    from tesseract.cli import main
    from tesseract.core.config import Settings

    module = manifest("source")
    request = spec(module)
    path = tmp_path / "run.json"
    path.write_text(request.model_dump_json())
    settings = Settings(_env_file=None, data_dir=tmp_path)
    registry = Registry((RegisteredModule(module, result),))
    monkeypatch.setattr("tesseract.cli.get_settings", lambda: settings)
    monkeypatch.setattr(Registry, "discover", lambda: registry)
    main(["run", "--run-spec", str(path), "--modules", "source"])
    first = json.loads(capsys.readouterr().out)
    assert first["run_id"] == request.run_id and first["status"] == "succeeded"
    main(["run", "--run-spec", str(path), "--as-of", "2026-10-21T18:00:00+02:00"])
    second = json.loads(capsys.readouterr().out)
    assert second["run_id"] != request.run_id and second["status"] == "succeeded"


def test_default_llm_client_is_bound_to_run_and_fixture_cannot_call_live(engine, tmp_path):
    from tesseract.core.config import Settings

    module = manifest("fixture-source", mode="fixture")
    request = spec(module, mode="fixture")

    def execute(ctx):
        assert ctx.clients["llm"].settings.llm_mode == "replay"
        context = ctx.clients["llm"]._context({})
        assert context["run"]["as_of"] == request.model_dump(mode="json")["as_of"]
        assert context["run"]["stores"] == ["MIL01"]
        return result(ctx)

    settings = Settings(_env_file=None, data_dir=tmp_path, llm_mode="live")
    statuses = run(
        request,
        engine=engine,
        registry=Registry((RegisteredModule(module, execute),)),
        settings=settings,
    )
    assert statuses[0].status == "succeeded"


def test_parent_child_batch_put_is_atomic_and_resolves_earlier_parent(engine):
    from tesseract.core.contracts import Segment

    request = spec(manifest("source"))
    document = SourceDocument(
        id="batch-doc",
        version="v1",
        available_at=request.as_of,
        availability_basis="test",
        source_refs=(),
        source_type="email",
        connector="source",
        uri="synthetic://batch",
        content_hash="batch",
        origin=None,
        text="hello",
        text_version="text-v1",
        meta={"store_id": "MIL01"},
    )
    segment = Segment(
        id="batch-segment",
        version="v1",
        available_at=request.as_of,
        availability_basis="document",
        source_refs=(),
        document_id=document.id,
        text_version=document.text_version,
        idx=0,
        text="hello",
        char_start=0,
        char_end=5,
        is_quoted=False,
    )
    with repo_session(engine, request) as repo:
        assert repo.put(document, segment, document) == 2
        assert repo.get(Segment, segment.id) == segment
        other = document.model_copy(update={"id": "rollback-doc"})
        invalid = segment.model_copy(update={"id": "invalid", "document_id": "absent"})
        with pytest.raises(ValueError, match="unavailable"):
            repo.put(other, invalid)
        assert repo.get(SourceDocument, other.id) is None


def test_uninstalled_disabled_required_dependency_blocks_instead_of_crashing(engine):
    missing = manifest("missing", enabled=False, mode="unavailable")
    consumer = manifest("consumer", requires=("missing",))
    request = spec(missing, consumer)
    statuses = run(request, engine=engine, registry=Registry((RegisteredModule(consumer, result),)))
    assert [s.status for s in statuses] == ["blocked", "blocked"]
    with repo_session(engine, request) as repo:
        assert repo.run_state()["status"] == "blocked"


def test_progress_is_committed_while_a_module_runs(engine, tmp_path):
    from sqlalchemy import create_engine

    from tesseract.core.repo import Repo as CanonicalRepo
    from tesseract.core.repo import list_module_runs

    seen = {}

    def execute(ctx):
        # Read-only observer: connect() would also migrate, i.e. write.
        other = create_engine(f"sqlite:///{tmp_path / 'pipeline.db'}")
        try:
            observer = CanonicalRepo.open(other, ctx.spec.run_id)
            seen["status"] = observer.status()
            seen["modules"] = {
                m.module_id: m.status for m in list_module_runs(other, ctx.spec.run_id)
            }
        finally:
            other.dispose()
        return result(ctx)

    source, later = manifest("source"), manifest("later", requires=("source",))
    run(
        spec(source, later),
        engine=engine,
        registry=Registry((RegisteredModule(source, execute), RegisteredModule(later, result))),
    )
    assert seen == {"status": "running", "modules": {"source": "running", "later": "pending"}}


def test_module_cannot_publish_or_change_lifecycle(engine):
    def sneaky(ctx):
        ctx.repo.publish()
        return result(ctx)

    request = spec(manifest("source"))
    statuses = run(
        request, engine=engine, registry=Registry((RegisteredModule(manifest("source"), sneaky),))
    )
    assert statuses[0].status == "failed"
    assert statuses[0].result.errors == ("module raised PermissionError",)
    with repo_session(engine, request) as repo:
        assert repo.run_state()["status"] == "failed"


def test_failed_run_discards_outputs_of_earlier_successful_modules(engine):
    def writer(ctx):
        ctx.repo.put(
            SourceDocument(
                id="kept-until-failure",
                version="1",
                available_at=ctx.spec.as_of,
                availability_basis="test",
                source_refs=(),
                source_type="email",
                connector="source",
                uri="test://doc",
                content_hash="doc",
                origin=None,
                text="hello",
                text_version="1",
                meta={},
            )
        )
        return result(ctx)

    source, consumer = manifest("source"), manifest("consumer", requires=("source",))
    request = spec(source, consumer)
    statuses = run(
        request,
        engine=engine,
        registry=Registry(
            (
                RegisteredModule(source, writer),
                RegisteredModule(consumer, lambda c: result(c, "failed")),
            )
        ),
    )
    assert [s.status for s in statuses] == ["succeeded", "failed"]
    with repo_session(engine, request) as repo:
        assert repo.list(SourceDocument) == []
