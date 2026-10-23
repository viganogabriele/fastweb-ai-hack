"""INT-03: `int.cases` keeps unlinked cases, counts documents vs origins, never looks ahead.

Synthetic observations, links and relations for the rules, then one smoke run on the DATA-01a
inputs of the dev stores (MIL01, NYC01) through `int.dedup` and `int.cases`, checked against the
hand-written DATA-01b case fixtures.
"""

import json
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from tessera.core.config import REPO_ROOT
from tessera.core.contracts import (
    ArtifactRef,
    Case,
    EntityLink,
    Evidence,
    EvidenceRelation,
    LinkCandidate,
    Observation,
    Quantity,
    RunSpec,
    Segment,
    SourceDocument,
)
from tessera.core.db import connect
from tessera.core.fixtures import read_fixtures
from tessera.core.registry import Registry
from tessera.core.repo import put_erp
from tessera.core.run_repo import repo_session
from tessera.modules.integration import cases, dedup
from tessera.modules.sources import erp

T1 = datetime(2026, 10, 2, 18, tzinfo=UTC)
T2 = T1 + timedelta(hours=1)
T3 = T2 + timedelta(hours=1)
DAY = (T1.replace(hour=0), T1.replace(hour=23))
OWNERS, VALIDITY_DAYS = cases.load_domain(REPO_ROOT / "config")
VALIDITY = timedelta(days=VALIDITY_DAYS)
FIXTURES = REPO_ROOT / "data" / "fixtures"
SOURCES = REPO_ROOT / "generated" / "sources"


def spec(as_of=T3, run_id="test", stores=("MIL01",), mode="fixture"):
    return RunSpec(
        run_id=run_id, scenario_id="historical", as_of=as_of, stores=stores,
        source_manifest_hash="s", config_hash="c", code_version="0", mode=mode, modules=(),
        prompt_versions={}, model_versions={}, authorized_fixture_refs=(),
    )  # fmt: skip


def fact(name, *, at=T1, kind="unmet_demand", value=7, unit="requests", period=DAY,
         origin="store@example.test", negated=False, mention="Aurea nera", reason=None,
         doc=None):  # fmt: skip
    text = f"{mention}: {value} {unit}."
    common = dict(version="v1", available_at=at, availability_basis="test", source_refs=())
    document = doc or SourceDocument(
        id=f"doc-{name}", **common, source_type="email", connector="test", uri=f"test://{name}",
        content_hash=f"raw-{name}", origin=origin, business_date=at.date(), text=text,
        text_version="t1", meta={"store_id": "MIL01"},
    )  # fmt: skip
    segment = Segment(
        id=f"seg-{name}", **common, document_id=document.id, text_version="t1", idx=0,
        text=document.text, char_start=0, char_end=len(document.text), is_quoted=False,
    )  # fmt: skip
    obs = Observation(
        id=f"obs-{name}", **common, run_id="test", scenario_id="historical", computed_at=at,
        input_refs=(cases.ref(document), cases.ref(segment)), producer="test",
        producer_version="1", document_id=document.id, kind=kind, store_id="MIL01",
        period_start=period[0] if period else None, period_end=period[1] if period else None,
        product_mention=mention,
        quantity=Quantity(kind="exact", value=value, unit=unit) if value is not None
        else Quantity(kind="vague", unit=unit),
        direction="up", reason=reason, attribution="store_staff", negated=negated,
        extractor_version="test",
        evidence=(Evidence(document_id=document.id, document_version="v1",
                           segment_id=segment.id, quote=document.text, char_start=0,
                           char_end=len(document.text)),),
    )  # fmt: skip
    return document, segment, obs


def link(obs, status="linked", target="J20931A00012-999", level="sku", candidates=()):
    resolved = status == "linked"
    return EntityLink(
        id=f"link-{obs.id}", version="v1", available_at=obs.available_at,
        availability_basis="test", source_refs=(), run_id="test", scenario_id="historical",
        computed_at=obs.available_at, input_refs=(cases.ref(obs),), producer="test",
        producer_version="1", observation_id=obs.id, status=status,
        level=level if resolved else None, target_id=target if resolved else None,
        candidates=tuple(
            LinkCandidate(target_id=c, level="style", method="t", score=0.5, score_min=0.0,
                          score_max=1.0)
            for c in candidates
        ),
        decided_by="test", rationale="test",
    )  # fmt: skip


def relation(name, new, old, kind):
    at = max(new.available_at, old.available_at)
    return EvidenceRelation(
        id=f"rel-{name}", version="v1", available_at=at, availability_basis="test",
        source_refs=(), run_id="test", scenario_id="historical", computed_at=at,
        input_refs=(cases.ref(new), cases.ref(old)), producer="test", producer_version="1",
        from_ref=cases.ref(new), to_ref=cases.ref(old), relation=kind, basis="test",
        evidence_refs=(),
    )  # fmt: skip


def build(facts, links=(), relations=(), as_of=T3, **kwargs):
    return cases.build_cases(
        [f[2] for f in facts], [f[0] for f in facts], links, relations, spec(as_of),
        owners=OWNERS, validity=VALIDITY, zones={"MIL01": "Europe/Rome"}, **kwargs,
    )  # fmt: skip


def test_manifest_is_discovered_after_dedup():
    (manifest,) = [m for m in Registry.discover().manifests() if m.id == "int.cases"]
    assert manifest == cases.MANIFEST
    assert manifest.requires == ("int.dedup",) and manifest.produces == ("Case",)


def test_every_case_type_has_an_owner_and_a_missing_one_fails(tmp_path):
    assert set(cases.KIND_CASE_TYPE.values()) <= set(OWNERS)
    (tmp_path / "domain.yaml").write_text(
        "owners: {unmet_demand: allocation}\npolicy: {decay: {max_validity: {value: 7}}}\n"
    )
    with pytest.raises(ValueError, match="owners missing"):
        cases.load_domain(tmp_path)


@pytest.mark.parametrize(
    ("status", "candidates", "problem"),
    [("ambiguous", ("STYLE-A", "STYLE-B"), "fits STYLE-A, STYLE-B"),
     ("unlinked", (), "not found in the catalog"),
     (None, (), "No entity link")],
)  # fmt: skip
def test_unresolved_links_keep_a_verify_case_with_unknown_scope(status, candidates, problem):
    a = fact("a", kind="product_feedback", mention="a sweatshirt", value=1, unit="units")
    links = [link(a[2], status, candidates=candidates)] if status else []
    built = build([a], links)
    (case,) = built.cases
    assert (case.scope_level, case.scope_id, case.status) == ("unknown", None, "verify")
    assert case.id == "case-mil01-unknown-20261002"
    assert case.owner == OWNERS["product_feedback"]
    assert case.priority == "low" and "Product not identified" in case.priority_reason
    assert any(problem in u for u in case.blocking_uncertainties)
    assert [cases.ref(lk) for lk in links] == list(case.context_refs)
    assert bool(built.abstentions) == (status is None)


def test_two_unknown_reports_are_never_merged_and_get_distinct_ids():
    a = fact("a", kind="product_feedback", value=1, unit="units")
    b = fact("b", at=T2, kind="product_feedback", value=1, unit="units")
    built = build([a, b], [link(a[2], "unlinked"), link(b[2], "unlinked")])
    assert [c.supporting for c in built.cases] == [(cases.ref(a[2]),), (cases.ref(b[2]),)]
    assert len({c.id for c in built.cases}) == 2


def test_certain_copy_is_one_origin_and_does_not_refresh_age():
    a, b = fact("a"), fact("b", at=T2)
    built = build([a, b], [link(a[2]), link(b[2])], [relation("dup", b[2], a[2], "duplicates")])
    (case,) = built.cases
    assert (case.n_documents, case.n_origin_groups, case.n_unknown_origins) == (2, 1, 0)
    assert case.first_available_at == T1 and case.last_received_at == T2
    assert case.last_independent_evidence_at == T1
    assert case.valid_until == T1 + VALIDITY
    assert case.supporting == (cases.ref(a[2]), cases.ref(b[2]))
    assert (case.scope_level, case.scope_id, case.status) == ("sku", "J20931A00012-999", "open")
    assert case.id == "case-mil01-j20931a00012-999-20261002"
    assert cases.ref(relation("dup", b[2], a[2], "duplicates")) in case.context_refs
    assert "Requests are not units" in " ".join(case.blocking_uncertainties)


def test_independent_reports_are_two_origins_and_possible_overlap_is_not_additive():
    a, b = fact("a"), fact("b", at=T2, value=5)
    rel = relation("same", b[2], a[2], "possibly_same_episode")
    (case,) = build([a, b], [link(a[2]), link(b[2])], [rel]).cases
    assert (case.n_documents, case.n_origin_groups) == (2, 2)
    assert case.last_independent_evidence_at == T2
    assert any("do not add" in u for u in case.blocking_uncertainties)


def test_unknown_sender_is_an_unknown_origin():
    a, b = fact("a"), fact("b", at=T2, origin=None)
    (case,) = build([a, b], [link(a[2]), link(b[2])]).cases
    assert (case.n_documents, case.n_origin_groups, case.n_unknown_origins) == (2, 1, 1)


def test_two_facts_in_one_document_count_one_document_and_one_origin():
    d, _, stock = fact("stock", kind="stockout", value=0, unit="units", period=(DAY[0], None))
    _, _, ask = fact("ask", value=None, period=(DAY[0], None), doc=d)
    facts = [(d, None, stock), (d, None, ask)]
    (case,) = build(facts, [link(stock), link(ask)]).cases
    assert (case.n_documents, case.n_origin_groups) == (1, 1)
    assert case.priority == "high" and case.case_type == "unmet_demand"
    assert case.window_start == DAY[0] and case.window_end == T1


def test_a_report_after_the_validity_opens_a_new_case_and_keeps_the_first_id():
    later = T1 + VALIDITY + timedelta(hours=1)
    a, b = fact("a"), fact("b", at=later, period=(later, later))
    first = build([a], [link(a[2])], as_of=T1).cases
    built = build([a, b], [link(a[2]), link(b[2])], as_of=later)
    assert len(built.cases) == 2
    assert built.cases[0] == first[0].model_copy(update={"computed_at": later})


def test_supersedes_drops_the_old_fact_and_retracts_drop_both():
    a, b = fact("a"), fact("b", at=T2, value=9)
    sup = relation("sup", b[2], a[2], "supersedes")
    (case,) = build([a, b], [link(a[2]), link(b[2])], [sup]).cases
    assert case.supporting == (cases.ref(b[2]),)
    assert cases.ref(sup) in case.context_refs
    ret = relation("ret", b[2], a[2], "retracts")
    built = build([a, b], [link(a[2]), link(b[2])], [ret])
    assert built.cases == () and built.counts["inactive_facts"] == 2


def test_negated_report_contradicts_and_never_opens_a_case():
    a, b = fact("a"), fact("b", at=T2, negated=True)
    (case,) = build([a, b], [link(a[2]), link(b[2])]).cases
    assert case.contradicting == (cases.ref(b[2]),)
    assert build([b], [link(b[2])]).counts["negated_unattached"] == 1
    assert build([b], [link(b[2])]).cases == ()


@pytest.mark.parametrize(
    ("kind", "case_type"),
    [("demand_down", "demand_shift"), ("low_stock", "unmet_demand"), ("other", "unknown"),
     ("customer_profile", "customer_profile")],
)  # fmt: skip
def test_kinds_map_to_an_owned_case_type(kind, case_type):
    a = fact("a", kind=kind)
    (case,) = build([a], [link(a[2])]).cases
    assert case.case_type == case_type and case.owner == OWNERS[case_type]
    assert (case.status == "verify") == (case_type == "unknown")


def test_metrics_and_store_level_facts():
    sales = fact("s", kind="sales_figure", value=12, unit="units", mention=None)
    traffic = fact("t", kind="traffic_change", value=None, unit="visitors", mention=None)
    links = [link(sales[2], "not_product"), link(traffic[2], "not_product")]
    built = build([sales, traffic], links)
    (case,) = built.cases
    assert built.counts["no_case_kind"] == 1
    assert (case.scope_level, case.scope_id, case.case_type) == ("store", "MIL01", "traffic_change")


def test_no_look_ahead_and_availability_is_the_latest_input():
    a, b = fact("a"), fact("b", at=T2)
    links = [link(a[2]), link(b[2])]
    dup = relation("dup", b[2], a[2], "duplicates")
    (early,) = build([a, b], links, [dup], as_of=T1).cases
    assert early.supporting == (cases.ref(a[2]),) and early.available_at == T1
    (late,) = build([a, b], links, [dup], as_of=T3).cases
    assert late.available_at == T2 and late.id == early.id


def test_module_writes_cases_once(tmp_path):
    a, b = fact("a"), fact("b", at=T2)
    engine = connect(f"sqlite:///{tmp_path / 'c.db'}")
    for _ in range(2):
        with repo_session(engine, spec(), fixture_mode=True, write=True) as repo:
            repo.put(a[0], b[0], a[1], b[1], a[2], b[2], link(a[2]), link(b[2]))
            result = cases.run(SimpleNamespace(spec=repo.spec, repo=repo, params={}))
            stored = repo.list(Case)
    assert result.status == "succeeded" and result.counts["cases_new"] == 0
    assert len(stored) == 1 and stored[0].producer == "int.cases"


def test_dev_store_smoke_matches_the_data01b_case_fixtures(tmp_path):
    as_of = datetime(2026, 10, 22, 20, tzinfo=UTC)
    run_spec = spec(as_of, run_id="fixture", stores=("MIL01", "NYC01"))
    engine = connect(f"sqlite:///{tmp_path / 's.db'}")
    put_erp(engine, erp.load_csv(
        "master_data/stores.csv", "stores", sources_dir=SOURCES, as_of=as_of,
        store_timezones={}, master_available_at=datetime(2026, 8, 1, tzinfo=UTC),
    ))  # fmt: skip
    _, records = read_fixtures(FIXTURES)
    inputs = ("SourceDocument", "Segment", "Observation", "EntityLink")
    with repo_session(engine, run_spec, fixture_mode=True, write=True) as repo:
        repo.put(*sorted(
            (r for r in records if type(r).__name__ in inputs),
            key=lambda r: inputs.index(type(r).__name__),
        ))  # fmt: skip
        ctx = SimpleNamespace(spec=repo.spec, repo=repo, params={})
        assert dedup.run(ctx).status == "succeeded"
        result = cases.run(ctx)
        built = {c.id: c for c in repo.list(Case)}
    expected = {}
    for path in sorted((FIXTURES / "cases").glob("*.json")):
        (rec,) = json.loads(path.read_text(encoding="utf-8"))
        expected[rec["payload"]["id"]] = Case.model_validate(rec["payload"])
    assert result.status == "succeeded", result
    assert set(built) == set(expected)
    same = (
        "case_type", "store_id", "scope_level", "scope_id", "status", "owner", "priority",
        "window_start", "window_end", "first_available_at", "last_received_at",
        "last_independent_evidence_at", "valid_until", "supporting", "contradicting",
        "n_documents", "n_origin_groups", "n_unknown_origins",
    )  # fmt: skip
    for case_id, want in expected.items():
        got = built[case_id]
        assert {f: getattr(got, f) for f in same} == {f: getattr(want, f) for f in same}, case_id
        links = {r for r in want.context_refs if r.kind == "EntityLink"}
        assert links <= set(got.context_refs)
    assert result.counts["no_case_kind"] == 1 and result.counts["inactive_facts"] == 1
    assert all(isinstance(r, ArtifactRef) for c in built.values() for r in c.input_refs)


# INT-04: all inputs below are synthetic, with explicit event and knowledge times.
def stock_fact(**changes):
    from tessera.core.contracts import SourceRef, StockFact

    source = SourceRef(uri="test://stock", content_hash="sha256:synthetic")
    return StockFact.model_validate(
        dict(
            id="stock",
            version="v1",
            available_at=T2,
            availability_basis="test",
            source_refs=(source,),
            source_ref=source,
            location_id="MIL01",
            sku="J20931A00012-999",
            size="2",
            snapshot_at=T1,
            qty=4,
            basis="on_hand",
            reservations_included=False,
            quality_holds_included=False,
        )
        | changes
    )


def test_matching_stock_conflict_is_visible_without_resolving_or_changing_demand():
    a = fact("stockout", kind="stockout", value=0, unit="units", period=(T1, T2))
    stock = stock_fact()
    (case,) = build([a], [link(a[2])], stocks=[stock]).cases
    assert case.status == "verify"
    assert case.supporting == (cases.ref(a[2]),)
    assert case.contradicting == (cases.ref(stock),)
    assert cases.ref(stock) in case.context_refs and cases.ref(stock) in case.input_refs
    assert stock.source_ref in case.source_refs and case.available_at == T2
    assert case.n_documents == 1 and case.n_origin_groups == 1
    assert case.last_independent_evidence_at == T1
    assert "does not disprove unmet demand" in " ".join(case.blocking_uncertainties)
    assert "ERP stock not checked yet" not in " ".join(case.blocking_uncertainties)


@pytest.mark.parametrize(
    "changes",
    [
        {"snapshot_at": T1 - timedelta(days=1)},
        {"snapshot_at": T3 + timedelta(hours=1)},
        {"available_at": T3 + timedelta(hours=1)},
        {"available_at": None},
        {"location_id": "NYC01"},
        {"sku": "OTHER-999"},
        {"qty": None},
    ],
)
def test_unavailable_stale_and_unrelated_stock_does_not_contradict(changes):
    a = fact("stockout", kind="stockout", period=(T1, T2))
    (case,) = build([a], [link(a[2])], stocks=[stock_fact(**changes)]).cases
    assert case.status == "open" and case.contradicting == ()
    assert all(r.kind != "StockFact" for r in case.input_refs)


@pytest.mark.parametrize("kind", ["unmet_demand", "low_stock", "demand_up"])
def test_stock_is_not_a_measure_of_unmet_demand_or_a_low_stock_threshold(kind):
    a = fact("a", kind=kind, period=(T1, T2))
    (case,) = build([a], [link(a[2])], stocks=[stock_fact()]).cases
    assert case.status == "open" and case.contradicting == ()


def test_exact_size_and_stock_basis_are_preserved():
    a = fact("a", kind="stockout", period=(T1, T2))
    lk = link(a[2], target="J20931A00012-999-2", level="sku_size")
    for stock in [stock_fact(size="3"), stock_fact(qty=0, basis="atp")]:
        (case,) = build([a], [lk], stocks=[stock]).cases
        assert case.supporting == (cases.ref(a[2]),) and case.contradicting == ()
    stock = stock_fact(qty=0)
    (case,) = build([a], [lk], stocks=[stock]).cases
    assert case.supporting == (cases.ref(a[2]), cases.ref(stock))
    assert case.status == "open"


def test_silence_and_expiry_do_not_close_a_case():
    a = fact("a", kind="stockout", period=(T1, T2))
    (case,) = build(
        [a],
        [link(a[2])],
        as_of=T3 + timedelta(days=30),
        stocks=[stock_fact(snapshot_at=T1 - timedelta(days=1))],
    ).cases
    assert case.status == "open" and case.valid_until < case.computed_at
    assert case.decision_due_at is None
    assert any("deadline not estimable" in u for u in case.blocking_uncertainties)


def calendar(target_case_id, **changes):
    from tessera.modules.integration.reconciliation import DecisionCalendar

    return DecisionCalendar.model_validate(
        dict(
            case_id=target_case_id,
            available_at=T1,
            required_by=T3 + timedelta(days=3),
            source_refs=[dict(uri="test://verified-calendar", content_hash="calendar-v1")],
            slots=[
                dict(cutoff_at=T3, sellable_at=T3 + timedelta(days=1)),
                dict(cutoff_at=T3 + timedelta(days=1), sellable_at=T3 + timedelta(days=2)),
            ],
        )
        | changes
    )


def test_deadline_uses_first_feasible_sellable_arrival_and_rechecks_after_cutoff():
    a = fact("a")
    (base,) = build([a], [link(a[2])]).cases
    cal = calendar(base.id)
    (on_time,) = build([a], [link(a[2])], decision_calendars=[cal]).cases
    assert on_time.decision_due_at == T3
    assert cal.source_refs[0] in on_time.source_refs
    (missed,) = build(
        [a], [link(a[2])], as_of=T3 + timedelta(seconds=1), decision_calendars=[cal]
    ).cases
    assert missed.decision_due_at == T3 + timedelta(days=1)
    (late,) = build([a], [link(a[2])], as_of=T3 + timedelta(days=2), decision_calendars=[cal]).cases
    assert late.decision_due_at is None and late.status == "open"
    assert any("No remaining calendar slot" in u for u in late.blocking_uncertainties)


@pytest.mark.parametrize(
    "changes",
    [
        {"case_id": "another-case"},
        {"available_at": T3 + timedelta(seconds=1)},
        {"required_by": T3 + timedelta(hours=1)},
        {"slots": []},
    ],
)
def test_deadlines_abstain_for_unknown_future_or_infeasible_calendars(changes):
    a = fact("a")
    (base,) = build([a], [link(a[2])]).cases
    (case,) = build([a], [link(a[2])], decision_calendars=[calendar(base.id, **changes)]).cases
    assert case.decision_due_at is None and case.status == "open"


def test_conflicting_calendars_abstain_and_aware_ordered_source_backed_slots_required():
    from pydantic import ValidationError

    a = fact("a")
    (base,) = build([a], [link(a[2])]).cases
    cal = calendar(base.id)
    (case,) = build([a], [link(a[2])], decision_calendars=[cal, cal]).cases
    assert case.decision_due_at is None
    for changes in [
        {"available_at": "2026-10-02T18:00:00"},
        {"source_refs": []},
        {"slots": [dict(cutoff_at=T3, sellable_at=T2)]},
    ]:
        with pytest.raises(ValidationError):
            calendar(base.id, **changes)


def erp_stock_row(day, **changes):
    from tessera.core.contracts import SourceRef
    from tessera.core.repo import ErpRecord

    return ErpRecord(
        table="stock",
        id="erp-stock",
        version="1",
        available_at=T3 + timedelta(days=1),
        availability_basis="test",
        source_refs=(SourceRef(uri="test://erp", content_hash="s"),),
        data=dict(store_id="MIL01", sku="J20931A00012-999", size="2", snapshot_date=day, on_hand=4)
        | changes,
    )


def test_erp_eod_only_compares_to_a_whole_local_day_and_keeps_versioned_refs():
    start = T1.replace(hour=22) - timedelta(days=1)  # Rome midnight (UTC+2)
    end = start + timedelta(days=1, seconds=-1)
    a = fact("a", kind="stockout", period=(start, end))
    stock = erp_stock_row(T1.date())
    (case,) = build([a], [link(a[2])], erp_stock=[stock], as_of=T3 + timedelta(days=1)).cases
    ref = ArtifactRef(kind="erp.stock", id="erp-stock", version="1")
    assert case.contradicting == (ref,) and ref in case.input_refs
    assert case.available_at == T3 + timedelta(days=1) and stock.source_refs[0] in case.source_refs
    for period in [(T1, T2), (start, end - timedelta(minutes=1)), (None, None)]:
        b = fact("b", kind="stockout", period=period)
        (other,) = build([b], [link(b[2])], erp_stock=[stock], as_of=T3 + timedelta(days=1)).cases
        assert other.contradicting == () and other.status == "open"


def test_module_wires_structured_stock_and_calendar_and_repeats_idempotently(tmp_path):
    a = fact("a", kind="stockout", period=(T1, T2))
    (base,) = build([a], [link(a[2])]).cases
    cal = calendar(base.id, available_at=T2)
    stock = stock_fact()
    engine = connect(f"sqlite:///{tmp_path / 'reconcile.db'}")
    from tessera.core.repo import ErpRecord

    put_erp(
        engine,
        [
            ErpRecord(
                table="stores",
                id="MIL01",
                version="1",
                available_at=T1,
                availability_basis="test",
                source_refs=(),
                data={"store_id": "MIL01", "timezone": "Europe/Rome"},
            )
        ],
    )
    for _ in range(2):
        with repo_session(engine, spec(), fixture_mode=True, write=True) as repo:
            repo.put(a[0], a[1], a[2], link(a[2]), stock)
            result = cases.run(
                SimpleNamespace(
                    spec=repo.spec,
                    repo=repo,
                    params={"decision_calendars": [cal.model_dump(mode="json")]},
                )
            )
            (stored,) = repo.list(Case)
    assert stored.status == "verify" and stored.decision_due_at == T3
    assert stored.contradicting == (cases.ref(stock),)
    assert result.counts["cases_new"] == 0


def test_replay_t1_t2_t1_keeps_future_conflict_and_calendar_out_of_early_snapshot():
    a = fact("a", kind="stockout", period=(T1, T2))
    stock = stock_fact(available_at=T2)
    (base,) = build([a], [link(a[2])], as_of=T1).cases
    cal = calendar(base.id, available_at=T2)
    results = [
        build([a], [link(a[2])], as_of=at, stocks=[stock], decision_calendars=[cal]).cases[0]
        for at in (T1, T2, T1)
    ]
    assert results[0] == results[2] == base
    assert results[1].status == "verify" and results[1].decision_due_at == T3
    assert results[0].available_at == T1 and results[1].available_at == T2


def test_calendar_prefers_earliest_sellable_arrival_not_earliest_departure():
    a = fact("a")
    (base,) = build([a], [link(a[2])]).cases
    cal = calendar(
        base.id,
        slots=[
            dict(cutoff_at=T3, sellable_at=T3 + timedelta(days=3)),
            dict(cutoff_at=T3 + timedelta(hours=1), sellable_at=T3 + timedelta(days=1)),
        ],
    )
    (case,) = build([a], [link(a[2])], decision_calendars=[cal]).cases
    assert case.decision_due_at == T3 + timedelta(hours=1)


def test_unknown_scope_cannot_get_a_logistics_deadline():
    a = fact("a")
    lk = link(a[2], status="ambiguous", candidates=("STYLE-A", "STYLE-B"))
    (base,) = build([a], [lk]).cases
    (case,) = build([a], [lk], decision_calendars=[calendar(base.id)]).cases
    assert case.scope_level == "unknown" and case.status == "verify"
    assert case.decision_due_at is None


def test_module_persists_erp_conflict_refs_with_knowledge_time(tmp_path):
    start = T1.replace(hour=22) - timedelta(days=1)
    a = fact("a", kind="stockout", period=(start, start + timedelta(days=1, seconds=-1)))
    stock = erp_stock_row(T1.date())
    from tessera.core.repo import ErpRecord

    engine = connect(f"sqlite:///{tmp_path / 'erp-conflict.db'}")
    put_erp(
        engine,
        [
            stock,
            ErpRecord(
                table="stores",
                id="MIL01",
                version="1",
                available_at=T1,
                availability_basis="test",
                source_refs=(),
                data={"store_id": "MIL01", "timezone": "Europe/Rome"},
            ),
        ],
    )
    with repo_session(
        engine, spec(as_of=T3 + timedelta(days=1)), fixture_mode=True, write=True
    ) as repo:
        repo.put(a[0], a[1], a[2], link(a[2]))
        cases.run(SimpleNamespace(spec=repo.spec, repo=repo, params={}))
        (case,) = repo.list(Case)
    assert case.status == "verify" and case.available_at == T3 + timedelta(days=1)
    assert case.contradicting == (
        ArtifactRef(kind="erp.stock", id=stock.id, version=stock.version),
    )
