"""Durable answer events, atomic submission and isolated follow-up execution."""

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, inspect, select

from tessera.core.contracts import (
    ArtifactRef,
    Case,
    Clarification,
    Evidence,
    ModuleManifest,
    ModuleResult,
    ModuleSnapshot,
    Observation,
    Quantity,
    RunSpec,
    Segment,
    SourceDocument,
)
from tessera.core.db import connect, runs
from tessera.core.registry import RegisteredModule, Registry
from tessera.core.repo import reset_run
from tessera.core.run_repo import repo_session
from tessera.modules.agents.answer_registry import (
    AnswerConflict,
    AnswerRequest,
    AnswerUnavailable,
    events,
    execute_follow_up,
    jobs,
    register_recorded_answer,
    submit_answer,
)
from tessera.modules.agents.clarifications import InvalidAnswer, UnrecordedAnswer
from tessera.modules.agents.contextual_answers import ContextualMention

NOW = datetime(2026, 10, 22, 20, tzinfo=UTC)


def ref(record):
    return ArtifactRef(kind=type(record).__name__, id=record.id, version=record.version)


class ContextReading:
    """Synthetic external response; no claim of provider comprehension."""

    def extract(self, schema, messages, **kwargs):
        import json

        assert schema is ContextualMention
        context = json.loads(messages[-1]["content"])
        mention = context["original"]["product_mention"]
        return ContextualMention(
            product_mention=mention if "taglia M" in mention else f"{mention} taglia M"
        )


@pytest.fixture
def setup(tmp_path, monkeypatch):
    from tessera.core.llm import RunLLMClient

    monkeypatch.setattr(RunLLMClient, "extract", ContextReading().extract)
    engine = connect(f"sqlite:///{tmp_path / 'answers.db'}")
    manifests = tuple(
        ModuleManifest(
            id=id,
            version="1",
            layer="ingestion",
            description="test",
            requires=requires,
            optional_inputs=(),
            produces=(),
            enabled=True,
            mode="live",
            params_schema={},
        )
        for id, requires in (
            ("ing.extract", ()),
            ("int.link", ("ing.extract",)),
            ("fc.overlay", ("int.link",)),
            ("act.options", ("fc.overlay",)),
        )
    )
    spec = RunSpec(
        run_id="parent",
        scenario_id="historical",
        as_of=NOW,
        stores=("MIL01",),
        source_manifest_hash="sources",
        config_hash="config",
        code_version="test",
        mode="live",
        modules=tuple(ModuleSnapshot(manifest=m, params={}) for m in manifests),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )
    source = SourceDocument(
        id="mail",
        version="1",
        available_at=NOW,
        availability_basis="test",
        source_refs=(),
        source_type="email",
        connector="src.email",
        uri="test://mail",
        content_hash="test",
        origin="episode",
        text="Una felpa",
        text_version="1",
        meta={"store_id": "MIL01"},
    )
    segment = Segment(
        id="segment",
        version="1",
        available_at=NOW,
        availability_basis="test",
        source_refs=(),
        document_id=source.id,
        text_version="1",
        idx=0,
        text=source.text,
        char_start=0,
        char_end=len(source.text),
        is_quoted=False,
    )
    common = dict(
        version="1",
        available_at=NOW,
        availability_basis="test",
        source_refs=(),
        run_id=spec.run_id,
        scenario_id=spec.scenario_id,
        computed_at=NOW,
        producer="test",
        producer_version="1",
    )
    observation = Observation(
        id="obs-mail-1",
        input_refs=(ref(source), ref(segment)),
        document_id=source.id,
        store_id="MIL01",
        kind="unmet_demand",
        product_mention="felpa",
        quantity=Quantity(kind="unknown"),
        direction="unknown",
        attribution="store",
        negated=False,
        evidence=(
            Evidence(
                document_id=source.id,
                document_version="1",
                segment_id=segment.id,
                quote="felpa",
                char_start=4,
                char_end=9,
            ),
        ),
        extractor_version="1",
        **common,
    )
    case = Case(
        id="case",
        input_refs=(ref(observation),),
        case_type="unmet_demand",
        store_id="MIL01",
        scope_level="unknown",
        window_start=NOW,
        window_end=NOW,
        status="verify",
        owner="allocation",
        priority="high",
        priority_reason="ambiguous",
        first_available_at=NOW,
        last_received_at=NOW,
        supporting=(ref(observation),),
        contradicting=(),
        n_documents=1,
        n_origin_groups=1,
        n_unknown_origins=0,
        blocking_uncertainties=("Product",),
        context_refs=(),
        **common,
    )
    question = Clarification(
        id="question",
        input_refs=(ref(case), ref(observation)),
        case_id=case.id,
        observation_refs=(ref(observation),),
        question="Quale taglia?",
        asked_at=NOW,
        status="draft",
        **common,
    )
    seen = []

    def execute(ctx):
        assert ctx.spec.as_of >= NOW + timedelta(hours=1)
        assert ctx.spec.run_id != "parent"
        assert not any(r.version.startswith("parent:") for r in ctx.repo.list(Observation))
        if ctx.manifest.id == "ing.extract":
            assert any(d.source_type == "email" for d in ctx.repo.list(SourceDocument))
            # Same historical observation identity must not cause an immutable-artifact collision.
            fresh = observation.model_copy(
                update={
                    "run_id": ctx.spec.run_id,
                    "scenario_id": ctx.spec.scenario_id,
                    "computed_at": ctx.spec.as_of,
                }
            )
            ctx.repo.put(fresh)
        else:
            assert len(ctx.repo.list(Observation)) == 1
            assert ctx.repo.list(Observation)[0].computed_at == ctx.spec.as_of
        seen.append(ctx.manifest.id)
        return ModuleResult(
            module_id=ctx.manifest.id,
            module_version="1",
            status="succeeded",
            counts={},
            errors=(),
            abstentions=(),
        )

    registry = Registry(RegisteredModule(m, execute) for m in manifests)
    request = AnswerRequest(
        run_id=spec.run_id,
        scenario_id=spec.scenario_id,
        case_id=case.id,
        case_version="1",
        clarification_id=question.id,
        clarification_version="1",
        text="Taglia M 🧥",
        received_at=NOW + timedelta(hours=1),
        follow_up_scenario_id="simulated",
        as_of=NOW + timedelta(hours=1),
        idempotency_key="retry-1",
    )

    def seed(mode="live", published=True, extra=(), modules=None, records=None):
        changes = {"mode": mode}
        if modules is not None:
            changes["modules"] = modules
        current = spec.model_copy(update=changes)
        with repo_session(engine, current, fixture_mode=mode == "fixture", write=True) as repo:
            repo.put(*(records or (source, segment, observation, case, question)), *extra)
            if published:
                repo.publish()
        return current

    yield engine, request, registry, seed, seen, (source, segment, observation, case, question)
    engine.dispose()


def count(engine, table):
    with engine.connect() as conn:
        if not inspect(conn).has_table(table.name):
            return 0
        return conn.execute(select(func.count()).select_from(table)).scalar_one()


def test_submit_retry_execute_and_parent_immutability(setup):
    engine, request, registry, seed, seen, originals = setup
    seed()
    job = submit_answer(engine, request, registry=registry)
    assert submit_answer(engine, request, registry=registry) == job
    assert job.simulated and job.document.meta["simulated"]
    assert count(engine, jobs) == count(engine, events) == 1
    with repo_session(engine, job.run.run_id) as repo:
        assert repo.run_state()["status"] == "pending"
        assert repo.list(SourceDocument) == []  # no pipeline has run during acceptance
    assert (
        execute_follow_up(
            engine, job.run.run_id, registry=registry, clients={"llm": ContextReading()}
        )
        == job
    )
    assert (
        execute_follow_up(
            engine, job.run.run_id, registry=registry, clients={"llm": ContextReading()}
        )
        == job
    )
    assert seen == ["ing.extract", "int.link", "fc.overlay", "act.options"]
    with repo_session(engine, "parent") as repo:
        for original in originals:
            assert repo.get(type(original), original.id, original.version) == original
    with repo_session(engine, job.run.run_id) as repo:
        assert repo.run_state()["published"]
        answered = repo.get(Clarification, "question")
        assert answered.status == "answered" and answered.answer_document_id == job.document.id
        for reference in answered.input_refs:
            from tessera.core.repo import KINDS

            assert repo.get(KINDS[reference.kind], reference.id, reference.version) is not None
        historical = repo.get(Case, "case")
        assert historical.run_id == job.run.run_id and historical.version.startswith("parent:")
        for reference in historical.input_refs:
            assert repo.get(KINDS[reference.kind], reference.id, reference.version) is not None


def test_events_lineage_and_retries_survive_both_projection_resets(setup):
    engine, request, registry, seed, seen, _ = setup
    seed()
    job = submit_answer(engine, request, registry=registry)
    execute_follow_up(engine, job.run.run_id, registry=registry, clients={"llm": ContextReading()})
    reset_run(engine, "parent")
    reset_run(engine, job.run.run_id)
    assert submit_answer(engine, request, registry=registry) == job
    execute_follow_up(engine, job.run.run_id, registry=registry, clients={"llm": ContextReading()})
    assert len(seen) == 8
    assert count(engine, events) == count(engine, jobs) == 1


def test_alias_retry_survives_parent_reset_and_reserves_its_key(setup):
    engine, request, registry, seed, _, _ = setup
    seed()
    job = submit_answer(engine, request, registry=registry)
    reset_run(engine, "parent")
    alias = request.model_copy(update={"idempotency_key": "new-retry-key"})
    assert submit_answer(engine, alias, registry=registry) == job
    with pytest.raises(AnswerConflict, match="Idempotency"):
        submit_answer(engine, alias.model_copy(update={"text": "changed"}), registry=registry)
    assert count(engine, jobs) == count(engine, events) == 1


def test_investigator_cannot_act_on_seeded_historical_case(setup):
    from tessera.modules.agents.investigator import visible_case
    from tessera.modules.agents.runtime import ToolError

    engine, request, registry, seed, seen, _ = setup
    seed()
    job = submit_answer(engine, request, registry=registry)
    checked = []

    def protect(entry):
        def execute(ctx):
            # Frozen parent case_ids can point at a case that recomputation no
            # longer produces. Its historical copy is lineage, never actionable.
            with pytest.raises(ToolError, match="unavailable"):
                visible_case(ctx.repo, "case")
            historical = ctx.repo.get(Case, "case", f"parent:{job.fingerprint}:1")
            assert historical is not None
            assert historical.run_id == ctx.spec.run_id
            checked.append(ctx.manifest.id)
            return entry.run(ctx)

        return RegisteredModule(entry.manifest, execute)

    protected = Registry(
        protect(registry.resolve(ModuleSnapshot(manifest=m, params={})))
        for m in registry.manifests()
    )
    execute_follow_up(engine, job.run.run_id, registry=protected, clients={"llm": ContextReading()})
    assert checked == seen == ["ing.extract", "int.link", "fc.overlay", "act.options"]
    with repo_session(engine, job.run.run_id) as repo:
        assert repo.run_state()["published"]


@pytest.mark.parametrize("missing_at", ["context", "original"])
def test_production_extraction_replay_miss_cannot_publish_partial_answer(
    setup, monkeypatch, missing_at
):
    from tessera.core.cache import ReplayMiss
    from tessera.core.config import Settings
    from tessera.modules.ingestion import extract
    from tessera.modules.sources.emails import Store

    engine, request, registry, seed, seen, _ = setup
    source = ModuleManifest(
        id="src.email",
        version="1",
        layer="sources",
        description="Already seeded test mail",
        requires=(),
        optional_inputs=(),
        produces=(),
        enabled=True,
        mode="live",
        params_schema={},
    )

    def seeded_source(ctx):
        return ModuleResult(
            module_id=source.id,
            module_version=source.version,
            status="succeeded",
            counts={},
            errors=(),
            abstentions=(),
        )

    entries = [
        RegisteredModule(source, seeded_source),
        RegisteredModule(extract.MANIFEST, extract.run),
        *(
            registry.resolve(ModuleSnapshot(manifest=m, params={}))
            for m in registry.manifests()
            if m.id != "ing.extract"
        ),
    ]
    registry = Registry(entries)
    seed("recorded", modules=tuple(ModuleSnapshot(manifest=e.manifest, params={}) for e in entries))
    monkeypatch.setattr(extract, "get_settings", lambda: Settings(_env_file=None))
    monkeypatch.setattr(extract, "load_stores", lambda _: {"MIL01": Store("it", "Europe/Rome")})
    monkeypatch.setattr(extract, "vague_quantifiers", lambda _: ())

    class MissingReplyRecording:
        def extract(self, schema, messages, *, cache_context, **kwargs):
            if schema is ContextualMention:
                if missing_at == "context":
                    raise ReplayMiss("Missing simulated reply recording")
                return ContextReading().extract(
                    schema, messages, cache_context=cache_context, **kwargs
                )
            if missing_at == "original":
                # Production extraction catches this and reports degraded;
                # the answer worker must still refuse publication.
                raise ReplayMiss("Missing original extraction recording")
            return extract.Candidates(
                observations=[extract.Candidate(quote="felpa", kind="unmet_demand")]
            )

    register_recorded_answer(engine, request)
    job = submit_answer(engine, request, registry=registry)
    execute_follow_up(
        engine, job.run.run_id, registry=registry, clients={"llm": MissingReplyRecording()}
    )
    with repo_session(engine, job.run.run_id) as repo:
        assert not repo.run_state()["published"]
        assert repo.run_state()["status"] in {"failed", "blocked"}
        assert repo.list(SourceDocument) == repo.list(Observation) == []
        extraction = next(m for m in repo.module_runs() if m.module_id == "ing.extract")
        assert extraction.status == "failed"
        assert any("ReplayMiss" in e for e in extraction.result.errors)
    assert seen == []
    assert count(engine, jobs) == count(engine, events) == 1


def production_pipeline(setup, monkeypatch, *, quantitative=False):
    """Synthetic external boundaries shared by service and HTTP pipeline regressions."""
    from datetime import date

    import httpx

    from tessera.core.config import Settings
    from tessera.core.contracts import SourceRef
    from tessera.core.repo import put_erp
    from tessera.modules.actions import options
    from tessera.modules.ingestion import extract
    from tessera.modules.integration import cases, dedup, link
    from tessera.modules.intelligence import baseline, overlay
    from tessera.modules.sources import emails, erp
    from tessera.modules.sources.systems_client import Crosswalk, SystemsClient, SystemsReader

    engine, request, _, seed, _, originals = setup
    source, segment, observation, case, question = originals
    text = "Una felpa Luminara"
    source = source.model_copy(update={"text": text})
    segment = segment.model_copy(update={"text": text, "char_end": len(text)})
    observation = observation.model_copy(update={"product_mention": "Luminara"})
    originals = (source, segment, observation, case, question)
    parent_links = ()
    sku = "TEST-001"
    if quantitative:
        source, segment, observation, case, question = originals
        text = "4 felpe Luminara"
        source = source.model_copy(update={"text": text})
        segment = segment.model_copy(update={"text": text, "char_end": len(text)})
        observation = observation.model_copy(
            update={
                "product_mention": "Luminara",
                "direction": "up",
                "quantity": Quantity(kind="exact", value=4, unit="units", raw="4"),
                "period_start": NOW - timedelta(hours=12),
                "period_end": NOW,
                "evidence": (
                    observation.evidence[0].model_copy(
                        update={
                            "quote": text,
                            "char_start": 0,
                            "char_end": len(text),
                        }
                    ),
                ),
            }
        )
        from tessera.core.contracts import EntityLink

        parent_link = EntityLink(
            **{
                k: getattr(observation, k)
                for k in (
                    "version",
                    "available_at",
                    "availability_basis",
                    "source_refs",
                    "run_id",
                    "scenario_id",
                    "computed_at",
                    "producer",
                    "producer_version",
                )
            },
            id="parent-unresolved-link",
            input_refs=(ref(observation),),
            observation_id=observation.id,
            status="unlinked",
            level=None,
            candidates=(),
            decided_by="synthetic",
            rationale="Unresolved original mention",
        )
        parent_links = (parent_link,)
        case = case.model_copy(update={"input_refs": (*case.input_refs, ref(parent_link))})
        originals = (source, segment, observation, case, question)
    request = request.model_copy(update={"text": "Richiesta Luminara taglia M."})
    rows = [
        (
            "stores",
            {
                "store_id": "MIL01",
                "timezone": "Europe/Rome",
                "country_code": "IT",
                "closed_dow": "",
            },
        ),
        (
            "sku_colour",
            {"sku": sku, "style_code": "TEST", "style_name": "Luminara", "color_code": "001"},
        ),
        ("sku_size_ean", {"sku": sku, "size": "M", "sku_size": f"{sku}-M", "ean": "001"}),
        ("assortment", {"store_id": "MIL01", "sku": sku}),
        *(
            (
                "forecast",
                {
                    "store_id": "MIL01",
                    "sku": sku,
                    "run_date": date(2026, 10, 19),
                    "week_start": date(2026, 10, day),
                    "fcst_units": 7.0,
                },
            )
            for day in (19, 26)
        ),
    ]

    if quantitative:
        rows.append(
            (
                "stock",
                {
                    "store_id": "MIL01",
                    "sku": sku,
                    "size": "M",
                    "snapshot_date": date(2026, 10, 21),
                    "on_hand": 0,
                    "in_transit": 0,
                },
            )
        )

    def source(ctx):
        if ctx.manifest.id == "src.erp":
            put_erp(
                ctx.repo.engine,
                [
                    erp.ERPRow(
                        table,
                        f"test-{table}-{i}",
                        "1",
                        NOW,
                        "test",
                        (SourceRef(uri="test://erp.csv", content_hash="test"),),
                        data,
                    )
                    for i, (table, data) in enumerate(rows)
                ],
            )
            if quantitative:
                # Synthetic source boundary supplies resolvable stock citations.
                reader = open_reader(ctx.repo, None)
                ctx.repo.put(*reader.stock(sku, "M", ["MIL01"])["MIL01"])
                reader.client.close()
        return ModuleResult(
            module_id=ctx.manifest.id,
            module_version=ctx.manifest.version,
            status="succeeded",
            counts={},
            errors=(),
            abstentions=(),
        )

    entries = [RegisteredModule(emails.MANIFEST, source), RegisteredModule(erp.MANIFEST, source)]
    entries += [
        RegisteredModule(m.MANIFEST, m.run)
        for m in (extract, link, dedup, cases, baseline, overlay, options)
    ]
    registry = Registry(entries)
    snapshots = tuple(ModuleSnapshot(manifest=e.manifest, params={}) for e in entries)
    seed("recorded", modules=snapshots, records=(*originals[:3], *parent_links, *originals[3:]))
    monkeypatch.setattr(extract, "get_settings", lambda: Settings(_env_file=None))
    monkeypatch.setattr(
        extract, "load_stores", lambda _: {"MIL01": emails.Store("it", "Europe/Rome")}
    )
    monkeypatch.setattr(extract, "vague_quantifiers", lambda _: ())

    def no_network(request):
        pytest.fail(f"Unexpected systems request: {request.url.path}")

    def open_reader(repo, factory):
        crosswalk = Crosswalk(
            store_plant={"MIL01": "1001"},
            timezones={"MIL01": "Europe/Rome"},
            sku_matnr={sku: "TEST001"},
            ean_sku_size={"001": (sku, "M")},
        )
        return SystemsReader(
            repo, SystemsClient(crosswalk, transport=httpx.MockTransport(no_network))
        )

    monkeypatch.setattr(SystemsReader, "open", staticmethod(open_reader))

    class RecordedReading(ContextReading):
        def extract(self, schema, messages, *, cache_context, **kwargs):
            if schema is ContextualMention:
                return super().extract(schema, messages, cache_context=cache_context, **kwargs)
            assert schema is extract.Candidates  # This slice needs no LLM link tie-break.
            reply = cache_context["document"][0].startswith("clarification-answer:")
            return extract.Candidates(
                observations=[
                    extract.Candidate(
                        quote=request.text if reply else originals[2].evidence[0].quote,
                        kind="unmet_demand",
                        product_mention="Luminara taglia M" if reply else None,
                    )
                ]
            )

    return engine, request, registry, originals, RecordedReading


def test_follow_up_runs_production_extract_link_cases_forecast_and_options(setup, monkeypatch):
    from tessera.core.contracts import ActionOption, EntityLink, ForecastAdjustment

    engine, request, registry, originals, RecordedReading = production_pipeline(setup, monkeypatch)
    register_recorded_answer(engine, request)
    job = submit_answer(engine, request, registry=registry)
    execute_follow_up(engine, job.run.run_id, registry=registry, clients={"llm": RecordedReading()})
    with repo_session(engine, job.run.run_id) as repo:
        assert repo.run_state()["published"], [
            (m.module_id, m.status, m.result.errors) for m in repo.module_runs()
        ]
        fresh = [o for o in repo.list(Observation) if o.producer == "ag.contextual_answer"]
        assert len(fresh) == 1 and fresh[0].available_at == request.received_at
        links = [lk for lk in repo.list(EntityLink) if lk.observation_id == fresh[0].id]
        assert len(links) == 1 and links[0].status == "linked"
        linked_cases = [c for c in repo.list(Case) if ref(fresh[0]) in c.supporting]
        assert len(linked_cases) == 1
        assert repo.list(ForecastAdjustment)
        assert repo.list(ActionOption, case_id=linked_cases[0].id)
        assert all(m.status in {"succeeded", "degraded"} for m in repo.module_runs())
    with repo_session(engine, "parent") as repo:
        assert all(repo.get(type(r), r.id, r.version) == r for r in originals)


def test_concurrent_submit_and_alias_idempotency_keys(setup):
    engine, request, registry, seed, _, _ = setup
    seed()
    with ThreadPoolExecutor(max_workers=4) as pool:
        result = list(
            pool.map(lambda _: submit_answer(engine, request, registry=registry), range(4))
        )
    assert all(job == result[0] for job in result)
    alias = request.model_copy(update={"idempotency_key": "alias"})
    assert submit_answer(engine, alias, registry=registry) == result[0]
    for req in (request, alias):
        with pytest.raises(AnswerConflict, match="Idempotency"):
            submit_answer(engine, req.model_copy(update={"text": "changed"}), registry=registry)
    assert count(engine, jobs) == 1


def test_offline_fails_closed_and_only_trusted_registration_authorizes_exact_event(setup):
    engine, request, registry, seed, _, _ = setup
    seed("recorded")
    with pytest.raises(UnrecordedAnswer):
        submit_answer(engine, request, registry=registry)
    assert count(engine, runs) == 1
    fingerprint = register_recorded_answer(engine, request)
    assert register_recorded_answer(engine, request) == fingerprint
    assert submit_answer(engine, request, registry=registry).fingerprint == fingerprint
    for change in (
        {"text": "different"},
        {"received_at": NOW + timedelta(minutes=30)},
        {"language": "fr"},
    ):
        with pytest.raises(UnrecordedAnswer):
            submit_answer(
                engine,
                request.model_copy(update={**change, "idempotency_key": "miss"}),
                registry=registry,
            )
    assert count(engine, events) == count(engine, jobs) == 1


@pytest.mark.parametrize(
    "change,error",
    [
        ({"scenario_id": "other"}, InvalidAnswer),
        ({"case_version": "stale"}, AnswerConflict),
        ({"clarification_version": "stale"}, AnswerConflict),
        ({"case_id": "missing"}, AnswerUnavailable),
        ({"as_of": NOW}, InvalidAnswer),
        ({"received_at": NOW}, InvalidAnswer),
        ({"follow_up_scenario_id": "historical"}, InvalidAnswer),
    ],
)
def test_invalid_requests_are_atomic(setup, change, error):
    engine, request, registry, seed, _, _ = setup
    seed()
    with pytest.raises(error):
        submit_answer(engine, request.model_copy(update=change), registry=registry)
    assert count(engine, runs) == 1
    assert count(engine, events) == count(engine, jobs) == 0


def test_namespace_isolation_and_fixture_registration(setup):
    engine, request, registry, seed, _, _ = setup
    seed("fixture")
    with pytest.raises(AnswerUnavailable):
        register_recorded_answer(engine, request)
    register_recorded_answer(engine, request, fixture_mode=True)
    job = submit_answer(engine, request, registry=registry, fixture_mode=True)
    with pytest.raises(AnswerUnavailable):
        execute_follow_up(engine, job.run.run_id, registry=registry)
    execute_follow_up(
        engine,
        job.run.run_id,
        registry=registry,
        clients={"llm": ContextReading()},
        fixture_mode=True,
    )


def test_missing_lineage_and_unpublished_parents_reject_input(setup):
    engine, request, registry, seed, _, originals = setup
    seed(published=False)
    with pytest.raises(AnswerConflict, match="published"):
        submit_answer(engine, request, registry=registry)
    with repo_session(engine, "parent", write=True) as repo:
        repo.publish()
    # Broken historical lineage must fail closed, even though the source quote matches.
    from sqlalchemy import delete

    from tessera.core.db import artifacts

    with engine.begin() as conn:
        conn.execute(delete(artifacts).where(artifacts.c.kind == "Segment"))
    with pytest.raises(AnswerUnavailable, match="Segment"):
        submit_answer(engine, request, registry=registry)
    assert count(engine, runs) == 1


def test_worker_failure_preserves_durable_input_and_explicit_reset_retries(setup):
    engine, request, registry, seed, seen, _ = setup
    seed()
    job = submit_answer(engine, request, registry=registry)

    def broken(ctx):
        raise RuntimeError("missing recording")

    bad = Registry(RegisteredModule(m, broken) for m in registry.manifests())
    execute_follow_up(engine, job.run.run_id, registry=bad, clients={"llm": ContextReading()})
    with repo_session(engine, job.run.run_id) as repo:
        assert not repo.run_state()["published"] and repo.list(SourceDocument) == []
    assert count(engine, events) == 1
    with pytest.raises(AnswerConflict):
        execute_follow_up(
            engine, job.run.run_id, registry=registry, clients={"llm": ContextReading()}
        )
    reset_run(engine, job.run.run_id)
    execute_follow_up(engine, job.run.run_id, registry=registry, clients={"llm": ContextReading()})
    assert len(seen) == 4


def test_worker_setup_failure_is_visible_in_run_state_and_reset_recovers(setup):
    engine, request, registry, seed, seen, _ = setup
    seed()
    job = submit_answer(engine, request, registry=registry)
    with pytest.raises(ValueError, match="module not installed"):
        execute_follow_up(
            engine, job.run.run_id, registry=Registry(), clients={"llm": ContextReading()}
        )
    with repo_session(engine, job.run.run_id) as repo:
        assert repo.run_state()["status"] == "failed"
        assert not repo.run_state()["published"]
        assert repo.list(SourceDocument) == []
    with pytest.raises(AnswerConflict, match="reset"):
        execute_follow_up(
            engine, job.run.run_id, registry=registry, clients={"llm": ContextReading()}
        )
    reset_run(engine, job.run.run_id)
    execute_follow_up(engine, job.run.run_id, registry=registry, clients={"llm": ContextReading()})
    assert len(seen) == 4


def test_pending_recovery_and_live_events_never_become_replayable(setup):
    from tessera.modules.agents.answer_registry import pending_follow_ups

    engine, request, registry, seed, _, _ = setup
    assert pending_follow_ups(engine) == ()
    seed()
    job = submit_answer(engine, request, registry=registry)
    assert pending_follow_ups(engine) == (job,)
    assert pending_follow_ups(engine, fixture_mode=True) == ()
    execute_follow_up(engine, job.run.run_id, registry=registry, clients={"llm": ContextReading()})
    assert pending_follow_ups(engine) == ()
    with engine.connect() as conn:
        assert conn.execute(select(events.c.replay_ready)).scalar_one() == "no"


def test_concurrent_workers_do_not_execute_a_job_twice(setup):
    from threading import Event

    engine, request, registry, seed, _, _ = setup
    seed()
    job = submit_answer(engine, request, registry=registry)
    started, release = Event(), Event()

    def block(ctx):
        started.set()
        assert release.wait(5)
        return ModuleResult(
            module_id=ctx.manifest.id,
            module_version="1",
            status="succeeded",
            counts={},
            errors=(),
            abstentions=(),
        )

    blocking = Registry(RegisteredModule(m, block) for m in registry.manifests())
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(
            execute_follow_up,
            engine,
            job.run.run_id,
            registry=blocking,
            clients={"llm": ContextReading()},
        )
        assert started.wait(5)
        try:
            # Module writes hold the SQLite lock; release it while the second
            # worker waits, then it observes the existing running job.
            release.set()
            second = pool.submit(
                execute_follow_up,
                engine,
                job.run.run_id,
                registry=blocking,
                clients={"llm": ContextReading()},
            )
            try:
                assert second.result() == job  # already completed is an idempotent success
            except AnswerConflict:
                pass  # still running is a conflict, never a second execution
        finally:
            release.set()
        assert first.result() == job


def test_newer_question_version_cannot_reuse_an_old_answer(setup):
    engine, request, registry, seed, _, originals = setup
    newer = originals[-1].model_copy(update={"version": "2", "status": "cancelled"})
    seed(extra=(newer,))
    with pytest.raises(AnswerConflict, match="version changed"):
        submit_answer(engine, request, registry=registry)
    with pytest.raises(InvalidAnswer, match="cancelled"):
        submit_answer(
            engine, request.model_copy(update={"clarification_version": "2"}), registry=registry
        )


def test_unsupported_pipeline_is_rejected_before_persisting(setup):
    engine, request, registry, seed, _, _ = setup
    seed()
    from sqlalchemy import update

    with engine.begin() as conn:
        spec = dict(conn.execute(select(runs.c.spec)).scalar_one())
        spec["modules"] = spec["modules"][:-1]
        conn.execute(update(runs).values(spec=spec))
    with pytest.raises(AnswerUnavailable, match="requires extraction"):
        submit_answer(engine, request, registry=registry)
    assert count(engine, jobs) == count(engine, events) == 0


def test_transitive_supporting_refs_outside_input_refs_are_seeded(setup):
    engine, request, registry, seed, _, originals = setup
    source, segment, observation, case, question = originals
    extra = observation.model_copy(update={"id": "other-observation"})
    case = case.model_copy(update={"supporting": (*case.supporting, ref(extra))})
    seed(published=False)
    from sqlalchemy import delete

    from tessera.core.db import artifacts

    with engine.begin() as conn:
        conn.execute(delete(artifacts).where(artifacts.c.kind.in_(("Case", "Clarification"))))
    with repo_session(engine, "parent", write=True) as repo:
        repo.put(extra, case, question)
        repo.publish()
    job = submit_answer(engine, request, registry=registry)
    execute_follow_up(engine, job.run.run_id, registry=registry, clients={"llm": ContextReading()})
    with repo_session(engine, job.run.run_id) as repo:
        historical = repo.get(Case, case.id)
        assert len(historical.supporting) == 2
        for reference in historical.supporting:
            resolved = repo.get(Observation, reference.id, reference.version)
            assert resolved is not None and resolved.run_id == job.run.run_id


@pytest.mark.parametrize("answer_text", ["Taglia M", "M"])
def test_elliptical_reply_corrects_original_demand_once_with_quantitative_effects(
    setup, monkeypatch, answer_text
):
    import json

    from tessera.core.contracts import (
        ActionOption,
        EntityLink,
        EvidenceRelation,
        ForecastAdjustment,
    )

    engine, request, registry, originals, RecordedReading = production_pipeline(
        setup, monkeypatch, quantitative=True
    )
    request = request.model_copy(update={"text": answer_text})
    calls = []

    class Reading(RecordedReading):
        def extract(self, schema, messages, *, cache_context, **kwargs):
            if schema is ContextualMention:
                context = json.loads(messages[-1]["content"])
                assert context["question"]["question"] == originals[-1].question
                assert context["original"]["id"] == originals[2].id
                assert (
                    context["original"]["version"]
                    == f"parent:{job.fingerprint}:{originals[2].version}"
                )
                assert (
                    context["original"]["evidence"]
                    == originals[2].model_dump(mode="json")["evidence"]
                )
                assert context["answer"]["text"] == answer_text
                assert context["answer"] == job.document.model_dump(mode="json")
                assert context["question"]["version"] == f"answer:{job.fingerprint}"
                assert context["question"]["observation_refs"] == [
                    {
                        "kind": "Observation",
                        "id": context["original"]["id"],
                        "version": context["original"]["version"],
                    }
                ]
                assert cache_context["contextual_answer"] == context
                assert cache_context["instructions"] == messages[0]["content"]
                calls.append(cache_context)
            return super().extract(schema, messages, cache_context=cache_context, **kwargs)

    # Receipt clock is an admission gate, even for an otherwise registered answer.
    with pytest.raises(InvalidAnswer):
        register_recorded_answer(
            engine,
            request.model_copy(
                update={
                    "as_of": request.received_at - timedelta(microseconds=1),
                }
            ),
        )
    register_recorded_answer(engine, request)
    job = submit_answer(engine, request, registry=registry)
    with repo_session(engine, job.run.run_id) as repo:
        assert not repo.list(Observation)
        assert not repo.list(ForecastAdjustment)
        assert not repo.list(ActionOption)
    execute_follow_up(engine, job.run.run_id, registry=registry, clients={"llm": Reading()})
    assert len(calls) == 1
    with repo_session(engine, job.run.run_id) as repo:
        assert repo.run_state()["published"], [
            (m.module_id, m.result.errors) for m in repo.module_runs()
        ]
        current = [o for o in repo.list(Observation) if not o.version.startswith("parent:")]
        assert len(current) == 1
        corrected = current[0]
        assert corrected.id == originals[2].id
        assert corrected.quantity == originals[2].quantity
        assert corrected.period_start == originals[2].period_start
        assert corrected.period_end == originals[2].period_end
        assert corrected.available_at == request.received_at
        assert corrected.document_id == originals[0].id
        assert ref(job.document) in corrected.input_refs
        assert any(r.kind == "Clarification" for r in corrected.input_refs)
        (relation,) = repo.list(EvidenceRelation)
        assert relation.relation == "supersedes" and relation.from_ref == ref(corrected)
        assert relation.to_ref in corrected.input_refs
        (link,) = [r for r in repo.list(EntityLink) if not r.version.startswith("parent:")]
        assert link.observation_id == corrected.id
        assert (link.status, link.target_id) == ("linked", "TEST-001-M")
        (overlay,) = [f for f in repo.list(ForecastAdjustment) if f.case_ids]
        assert overlay.status == "computed", overlay.reason
        assert overlay.available_at == request.received_at
        assert len([c for c in overlay.components if c.type == "incremental_episode"]) == 1
        assert overlay.components[0].episode_refs == (ref(corrected),)
        assert overlay.components[0].reference_time == originals[2].period_end
        assert sum(p.latent.base for p in overlay.series) > sum(p.baseline for p in overlay.series)
        (hold,) = [o for o in repo.list(ActionOption) if o.kind == "hold"]
        assert hold.available_at == request.received_at
        assert hold.forecast_ref == ref(overlay)
        assert hold.outcomes
        for outcome in hold.outcomes:
            expected = sum(getattr(p.latent, outcome.scenario_id) for p in overlay.series)
            assert outcome.lost_units_dest == pytest.approx(expected)
        base_outcome = next(o for o in hold.outcomes if o.scenario_id == "base")
        assert base_outcome.lost_units_dest > sum(p.baseline for p in overlay.series)
    with repo_session(engine, "parent") as repo:
        assert all(repo.get(type(r), r.id, r.version) == r for r in originals)
        assert not repo.list(ForecastAdjustment) and not repo.list(ActionOption)
        assert repo.get(EntityLink, "parent-unresolved-link").status == "unlinked"


def test_registered_answer_without_actual_context_cache_fails_without_network(setup, tmp_path):
    from tessera.core.config import Settings
    from tessera.core.llm import LLMClient

    engine, request, registry, seed, _, originals = setup
    seed("recorded")
    register_recorded_answer(engine, request)
    job = submit_answer(engine, request, registry=registry)
    llm = LLMClient(
        Settings(_env_file=None, data_dir=tmp_path / "empty-cache", llm_mode="replay"),
        client_factory=lambda **kwargs: pytest.fail("Replay must never create a network client"),
    )
    execute_follow_up(engine, job.run.run_id, registry=registry, clients={"llm": llm})
    with repo_session(engine, job.run.run_id) as repo:
        assert repo.run_state()["status"] == "failed" and not repo.run_state()["published"]
        assert repo.list(Observation) == repo.list(SourceDocument) == []
        extraction = next(m for m in repo.module_runs() if m.module_id == "ing.extract")
        assert "ReplayMiss" in " ".join(extraction.result.errors)
    with repo_session(engine, "parent") as repo:
        assert all(repo.get(type(r), r.id, r.version) == r for r in originals)


@pytest.mark.parametrize(
    "mention",
    ["InventedProduct taglia M", "Luminara taglia XXL", "Luminara taglia M 99", "", "!!!"],
)
def test_contextual_mention_cannot_introduce_unsupported_product_tokens(
    setup, monkeypatch, mention
):
    engine, request, registry, _, RecordedReading = production_pipeline(setup, monkeypatch)

    class Reading(RecordedReading):
        def extract(self, schema, messages, **kwargs):
            if schema is ContextualMention:
                return ContextualMention(product_mention=mention)
            return super().extract(schema, messages, **kwargs)

    register_recorded_answer(engine, request)
    job = submit_answer(engine, request, registry=registry)
    execute_follow_up(engine, job.run.run_id, registry=registry, clients={"llm": Reading()})
    with repo_session(engine, job.run.run_id) as repo:
        assert not repo.run_state()["published"]
        assert repo.list(Observation) == []


@pytest.mark.parametrize("collision", [False, True])
def test_reconciliation_preserves_other_fact_kinds_or_refuses_identity_collision(
    setup, monkeypatch, collision
):
    from tessera.modules.ingestion import extract

    engine, request, registry, _, RecordedReading = production_pipeline(setup, monkeypatch)

    class Reading(RecordedReading):
        def extract(self, schema, messages, **kwargs):
            result = super().extract(schema, messages, **kwargs)
            if schema is extract.Candidates:
                result.observations.insert(
                    1 if collision else 0,
                    result.observations[0].model_copy(update={"kind": "product_feedback"}),
                )
            return result

    register_recorded_answer(engine, request)
    job = submit_answer(engine, request, registry=registry)
    execute_follow_up(engine, job.run.run_id, registry=registry, clients={"llm": Reading()})
    with repo_session(engine, job.run.run_id) as repo:
        if collision:
            assert not repo.run_state()["published"] and repo.list(Observation) == []
            return
        assert repo.run_state()["published"]
        current = [o for o in repo.list(Observation) if not o.version.startswith("parent:")]
        assert {o.kind for o in current} == {"unmet_demand", "product_feedback"}


@pytest.mark.parametrize("target", ["same", "other"])
def test_sequential_question_preserves_prior_corrections_without_answer_demand(
    setup, monkeypatch, target
):
    from tessera.modules.ingestion import extract

    engine, request, registry, originals, RecordedReading = production_pipeline(
        setup, monkeypatch, quantitative=True
    )

    class Reading(RecordedReading):
        def extract(self, schema, messages, **kwargs):
            if (
                schema is extract.Candidates
                and kwargs["cache_context"]["document"][0] == "mail-other"
            ):
                return extract.Candidates(
                    observations=[
                        extract.Candidate(
                            quote="Un vestito Arcobaleno",
                            kind="unmet_demand",
                            product_mention="Arcobaleno",
                        )
                    ]
                )
            return super().extract(schema, messages, **kwargs)

    entries = []
    for manifest in registry.manifests():
        entry = registry.resolve(ModuleSnapshot(manifest=manifest, params={}))
        if manifest.id == "src.email":
            source_run = entry.run

            def sources(ctx, source_run=source_run):
                result = source_run(ctx)
                if target == "other":
                    document = originals[0].model_copy(
                        update={"id": "mail-other", "text": "Un vestito Arcobaleno"}
                    )
                    segment = originals[1].model_copy(
                        update={
                            "id": "segment-other",
                            "document_id": document.id,
                            "text": document.text,
                            "char_end": len(document.text),
                        }
                    )
                    ctx.repo.put(document, segment)
                # The guard must hold even when prior reply segments are present.
                for doc in ctx.repo.list(SourceDocument):
                    if doc.source_type == "clarification_reply":
                        ctx.repo.put(
                            Segment(
                                id=f"{doc.id}:segment:0",
                                version="1",
                                available_at=doc.available_at,
                                availability_basis=doc.availability_basis,
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
                return result

            entry = RegisteredModule(manifest, sources)
        if manifest.id == "act.options":
            options_run = entry.run

            def ask_again(ctx, options_run=options_run):
                result = options_run(ctx)
                observation = next(
                    o
                    for o in ctx.repo.list(Observation)
                    if o.document_id == ("mail-other" if target == "other" else originals[0].id)
                )
                case = next(c for c in ctx.repo.list(Case) if ref(observation) in c.supporting)
                ctx.repo.put(
                    Clarification(
                        **{
                            key: getattr(observation, key)
                            for key in (
                                "available_at",
                                "availability_basis",
                                "source_refs",
                                "run_id",
                                "scenario_id",
                                "computed_at",
                                "producer",
                                "producer_version",
                            )
                        },
                        id="next-question",
                        version="1",
                        input_refs=(ref(case), ref(observation)),
                        case_id=case.id,
                        observation_refs=(ref(observation),),
                        question="Confermi la taglia?",
                        asked_at=ctx.spec.as_of,
                        status="draft",
                    )
                )
                return result

            entry = RegisteredModule(manifest, ask_again)
        entries.append(entry)
    registry = Registry(entries)
    register_recorded_answer(engine, request)
    first = submit_answer(engine, request, registry=registry)
    execute_follow_up(engine, first.run.run_id, registry=registry, clients={"llm": Reading()})
    with repo_session(engine, first.run.run_id) as repo:
        assert repo.run_state()["published"]
        question = repo.get(Clarification, "next-question")
        case = repo.get(Case, question.case_id)
        first_observations = repo.list(Observation)
    later = request.model_copy(
        update={
            "run_id": first.run.run_id,
            "scenario_id": first.run.scenario_id,
            "case_id": case.id,
            "case_version": case.version,
            "clarification_id": question.id,
            "clarification_version": question.version,
            "text": "Taglia M",
            "received_at": request.received_at + timedelta(hours=1),
            "as_of": request.as_of + timedelta(hours=1),
            "follow_up_scenario_id": "second-answer",
            "idempotency_key": "second-answer",
        }
    )
    register_recorded_answer(engine, later)
    second = submit_answer(engine, later, registry=registry)
    execute_follow_up(engine, second.run.run_id, registry=registry, clients={"llm": Reading()})
    with repo_session(engine, second.run.run_id) as repo:
        assert repo.run_state()["published"], [
            (m.module_id, m.result.errors) for m in repo.module_runs()
        ]
        current = [o for o in repo.list(Observation) if not o.version.startswith("parent:")]
        assert len(current) == (2 if target == "other" else 1)
        assert all(o.document_id not in {first.document.id, second.document.id} for o in current)
        retained = next(o for o in current if o.document_id == originals[0].id)
        assert retained.product_mention == "Luminara taglia M"
        assert retained.quantity == originals[2].quantity
        assert retained.period_end == originals[2].period_end
        assert retained.available_at == (
            request.received_at if target == "other" else later.received_at
        )
        for o in current:
            for r in o.input_refs:
                if r.kind == "Observation":
                    assert repo.get(Observation, r.id, r.version) is not None
    with repo_session(engine, first.run.run_id) as repo:
        assert repo.list(Observation) == first_observations


@pytest.mark.parametrize("behavior", ["abstain", "changed_spans"])
def test_contextual_reconciliation_abstains_or_fails_closed_on_ambiguous_spans(
    setup, monkeypatch, behavior
):
    engine, request, registry, originals, RecordedReading = production_pipeline(setup, monkeypatch)

    class Reading(RecordedReading):
        def extract(self, schema, messages, *, cache_context, **kwargs):
            if schema is ContextualMention:
                return ContextualMention(product_mention=None)
            result = super().extract(schema, messages, cache_context=cache_context, **kwargs)
            if behavior == "changed_spans":
                result.observations[0].quote = "Una felpa"
            return result

    register_recorded_answer(engine, request)
    job = submit_answer(engine, request, registry=registry)
    execute_follow_up(engine, job.run.run_id, registry=registry, clients={"llm": Reading()})
    with repo_session(engine, job.run.run_id) as repo:
        if behavior == "changed_spans":
            assert repo.run_state()["status"] == "failed"
            assert not repo.run_state()["published"] and not repo.list(Observation)
        else:
            assert repo.run_state()["published"]
            current = [o for o in repo.list(Observation) if not o.version.startswith("parent:")]
            assert len(current) == 1
            assert current[0].product_mention == originals[2].product_mention
            assert current[0].quantity == originals[2].quantity
