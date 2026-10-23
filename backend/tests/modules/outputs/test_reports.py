"""OUT-01: `out.reports` renders the brief from the run's facts, every number from a citation.

The smoke run loads the DATA-01a/b fixtures (and the DATA-01c options) into one fixture run and
checks the module's `by_office` brief against the hand-checked DATA-01b report fixture.
"""

import json
import re
from collections import Counter
from datetime import UTC, date, datetime, timedelta
from types import SimpleNamespace

import pytest

from tesseract.core.config import REPO_ROOT
from tesseract.core.contracts import (
    ArtifactRef,
    Case,
    Citation,
    Observation,
    ProductInsight,
    Report,
    RunSpec,
    Share,
)
from tesseract.core.db import connect
from tesseract.core.fixtures import read_fixtures
from tesseract.core.registry import Registry
from tesseract.core.repo import Repo, create_run, put_erp
from tesseract.modules.outputs import reports
from tesseract.modules.sources import erp

FIXTURES = REPO_ROOT / "data" / "fixtures"
SOURCES = REPO_ROOT / "generated" / "sources"
MARKER = re.compile(r" ?\[\d+\]")
NUMBER = re.compile(r"\d+(?:\.\d+)?")
INPUTS = (
    "SourceDocument",
    "Segment",
    "Observation",
    "EntityLink",
    "EvidenceRelation",
    "Case",
    "ForecastAdjustment",
)


def fixture_report() -> Report:
    (rec,) = json.loads((FIXTURES / "reports" / "report-by-office-20261009T0835.json").read_text())
    return Report.model_validate(rec["payload"])


AS_OF = fixture_report().as_of


def spec(as_of=AS_OF, stores=("MIL01", "NYC01")) -> RunSpec:
    return RunSpec(
        run_id="fixture", scenario_id="historical", as_of=as_of, stores=stores,
        source_manifest_hash="s", config_hash="c", code_version="0", mode="fixture", modules=(),
        prompt_versions={}, model_versions={}, authorized_fixture_refs=(),
    )  # fmt: skip


def load_master(engine, as_of) -> None:
    master = datetime.fromisoformat(erp.DEFAULT_MASTER_AVAILABLE_AT)
    for path, table in (
        ("master_data/stores.csv", "stores"),
        ("master_data/styles.csv", "styles"),
        ("master_data/sku_colour.csv", "sku_colour"),
        ("master_data/store_assortment.csv", "assortment"),
    ):
        put_erp(engine, erp.load_csv(
            path, table, sources_dir=SOURCES, as_of=as_of, store_timezones={},
            master_available_at=master,
        ))  # fmt: skip


def run_module(tmp_path, *, kinds=INPUTS, as_of=AS_OF, params=None, edit=lambda r: r, extra=()):
    engine = connect(f"sqlite:///{tmp_path / 'r.db'}")
    load_master(engine, as_of)
    _, records = read_fixtures(FIXTURES)
    run_spec = spec(as_of)
    create_run(engine, run_spec)
    repo = Repo(engine, run_spec)
    repo.put(*(
        edit(r) for r in records
        if type(r).__name__ in kinds and r.available_at is not None and r.available_at <= as_of
    ))  # fmt: skip
    if extra:
        repo.put(*extra)
    ctx = SimpleNamespace(spec=run_spec, repo=repo, params=params or {})
    result = reports.run(ctx)
    again = reports.run(ctx)
    return result, again, {r.view: r for r in repo.list(Report)}


def bare_lines(markdown: str) -> Counter[str]:
    return Counter(MARKER.sub("", line) for line in markdown.splitlines())


def key(c: Citation) -> str:
    return c.model_dump_json()


def segments(report: Report) -> dict[int, str]:
    """Citation number → the text it closes, from the bullet start or the previous marker."""
    out: dict[int, str] = {}
    for line in report.markdown.splitlines():
        line, prev = re.sub(r"^\s*- ", "", line), 0
        for m in re.finditer(r"\[(\d+)\]", line):
            out[int(m.group(1))] = line[prev : m.start()]
            prev = m.end()
    return out


def test_manifest_is_discovered_after_cases():
    (manifest,) = [m for m in Registry.discover().manifests() if m.id == "out.reports"]
    assert manifest.requires == ("int.cases",)
    assert manifest.layer == "outputs" and manifest.produces == ("Report",)


def test_fixture_run_renders_the_data01b_brief(tmp_path):
    result, again, built = run_module(tmp_path)
    assert result.status == "succeeded" and result.counts["reports_new"] == 2
    assert again.counts["reports_new"] == 0
    report, expected = built["by_office"], fixture_report()
    # Same facts, same sentences, same citations; only the order inside a case may differ.
    assert bare_lines(report.markdown) == bare_lines(expected.markdown)
    assert sorted(map(key, report.citations)) == sorted(map(key, expected.citations))
    assert report.id == expected.id and report.as_of == expected.as_of
    assert report.available_at == expected.available_at
    assert set(report.input_refs) == set(expected.input_refs)
    assert report.input_version_hash == expected.input_version_hash
    assert set(report.source_refs) == set(expected.source_refs)
    assert report.producer == "out.reports" and report.generated_by == reports.TEMPLATE
    # Each marker closes the same text as the fixture's marker for that citation.
    ours, theirs = segments(report), segments(expected)
    by_citation = {key(c): theirs[n] for n, c in enumerate(expected.citations, start=1)}
    for n, c in enumerate(report.citations, start=1):
        assert ours[n] == by_citation[key(c)]


def test_every_number_sits_in_a_cited_segment(tmp_path):
    _, _, built = run_module(tmp_path, kinds=(*INPUTS, "ActionOption"))
    for report in built.values():
        assert len(segments(report)) == len(report.citations)
        for line in report.markdown.splitlines():
            if line.startswith("  - open: "):
                continue
            if line.startswith(("- ", "  - ")):
                tail = re.split(r"\[\d+\]", line)[-1]
                assert not NUMBER.search(tail), line


def test_recommended_option_is_cited_without_numbers(tmp_path):
    _, _, built = run_module(tmp_path, kinds=(*INPUTS, "ActionOption"))
    report = built["by_office"]
    (line,) = [x for x in report.markdown.splitlines() if "recommended option" in x]
    assert line.startswith("  - recommended option: verify stock [")
    (c,) = [c for c in report.citations if c.ref.kind == "ActionOption"]
    assert c == Citation(ref=c.ref, field="recommended")
    assert c.ref.id == "opt-d1-mil01-verify-stock"
    # Only the recommended option is in the brief, so only it is an input.
    assert [r.id for r in report.input_refs if r.kind == "ActionOption"] == [c.ref.id]


def test_by_priority_groups_cases_highest_first(tmp_path):
    _, _, built = run_module(tmp_path)
    report = built["by_priority"]
    assert report.id == "report-by-priority-20261009T0835"
    headings = [x for x in report.markdown.splitlines() if x.startswith("## ")]
    assert headings == ["## high", "## medium", "## low"]
    assert bare_lines(report.markdown) - bare_lines(fixture_report().markdown) == Counter(
        {"# Brief by priority, as of 2026-10-09 08:35 UTC": 1, "": 2, **dict.fromkeys(headings, 1)}
    )


def test_changed_inputs_write_the_next_version(tmp_path):
    engine = connect(f"sqlite:///{tmp_path / 'v.db'}")
    load_master(engine, AS_OF)
    _, records = read_fixtures(FIXTURES)
    create_run(engine, spec())
    repo = Repo(engine, spec())
    repo.put(*(r for r in records if type(r).__name__ in INPUTS))
    ctx = SimpleNamespace(spec=repo.spec, repo=repo, params={"views": ["by_office"]})
    reports.run(ctx)
    repo.put(*(r for r in records if type(r).__name__ in ("StockFact", "ActionOption")))
    assert reports.run(ctx).counts["reports_new"] == 1
    first, second = repo.list(Report)
    assert (first.id, first.version, second.version) == (second.id, "v1", "v2")
    assert "recommended option" in second.markdown and "recommended option" not in first.markdown
    assert repo.get(Report, first.id) == second


def test_views_param_and_empty_run(tmp_path):
    result, _, built = run_module(tmp_path, kinds=(), params={"views": ["by_office"]})
    assert set(built) == {"by_office"} and result.counts["cases"] == 0
    report = built["by_office"]
    assert "No open case at this time." in report.markdown
    assert report.citations == () and report.available_at == AS_OF


def test_no_look_ahead_earlier_as_of_sees_fewer_cases(tmp_path):
    as_of = datetime(2026, 10, 3, tzinfo=UTC)
    _, _, built = run_module(tmp_path, as_of=as_of)
    report = built["by_office"]
    cited = {c.ref.id for c in report.citations}
    assert "case-mil01-i10919b00011-20261008" not in cited
    assert report.available_at <= as_of and report.as_of == as_of


def test_case_without_own_forecast_uses_the_store_baseline(tmp_path):
    """A real run: `fc.baseline` writes forecasts without case ids; the brief finds the baseline
    of every colour the store carries in the case's scope."""
    _, records = read_fixtures(FIXTURES)
    case = next(r for r in records if isinstance(r, Case) and r.scope_level == "sku")
    fc = next(
        r for r in records if type(r).__name__ == "ForecastAdjustment" and case.id in r.case_ids
    )
    plain = fc.model_copy(update={"case_ids": (), "id": fc.id + "-base"})
    facts = reports.Facts(
        cases=[case], observations={}, links={}, copies=frozenset(),
        forecasts={case.id: [plain]}, options={}, zones={"MIL01": "Europe/Rome"},
    )  # fmt: skip
    report = reports.build_report("by_office", facts, spec())
    (c,) = [c for c in report.citations if c.ref.kind == "ForecastAdjustment"]
    assert c.ref.id == plain.id and c.period_start == datetime(2026, 10, 9, 22, tzinfo=UTC)
    assert c.period_end == datetime(2026, 10, 16, 22, tzinfo=UTC) - timedelta(seconds=1)


def test_store_baselines_without_case_ids_are_found_by_scope(tmp_path):
    """`fc.baseline` writes no case ids: the style case gets the baseline of each colour the
    store carries, and the brief cites the same values as the fixture."""

    def plain(r):
        if type(r).__name__ == "ForecastAdjustment":
            return r.model_copy(update={"case_ids": ()})
        return r

    _, _, built = run_module(tmp_path, edit=plain)
    report = built["by_office"]
    assert bare_lines(report.markdown) == bare_lines(fixture_report().markdown)


def test_not_estimable_baseline_says_so_without_a_number(tmp_path):
    _, records = read_fixtures(FIXTURES)
    case = next(r for r in records if isinstance(r, Case) and r.scope_level == "sku")
    fc = next(
        r for r in records if type(r).__name__ == "ForecastAdjustment" and case.id in r.case_ids
    )
    missing = fc.model_copy(update={"status": "not_estimable", "reason": "no vintage"})
    facts = reports.Facts(
        cases=[case], observations={}, links={}, copies=frozenset(),
        forecasts={case.id: [missing]}, options={},
    )  # fmt: skip
    report = reports.build_report("by_office", facts, spec())
    assert re.search(rf"^  - baseline {fc.sku} not estimable \[\d+\]$", report.markdown, re.M)


def test_unknown_view_is_rejected():
    with pytest.raises(ValueError, match="unknown report view"):
        reports.build_report("by_moon", reports.Facts((), {}, {}, frozenset(), {}, {}), spec())


def shares(counts, total):
    return tuple(Share(key=k, count=c, of=total) for k, c in counts)


def insight(product_id, *, sold, returned, lines=(), reported=(), n=0):
    refs = tuple(ArtifactRef(kind="Observation", id=f"obs-{i}", version="v1") for i in range(n))
    n_lines = sum(c for _, c in lines)
    kinds = shares((("product_feedback", n),), n) if n else ()
    return ProductInsight(
        id=f"insight-sku-{product_id.lower()}", version="v1",
        available_at=AS_OF - timedelta(hours=1), availability_basis="max_input_available_at",
        source_refs=(), run_id="fixture", scenario_id="historical", computed_at=AS_OF,
        input_refs=refs, producer="ins.product", producer_version="1", as_of=AS_OF, level="sku",
        product_id=product_id, stores=("MIL01", "NYC01"), period_first=date(2026, 9, 11),
        period_last=date(2026, 10, 7), units_sold=sold, units_returned=returned,
        return_rate=returned / sold if sold else None, return_lines=n_lines,
        return_reasons=shares(lines, n_lines), n_observations=n, n_documents=n,
        reported_kinds=kinds, reported_reasons=shares(reported, n), observation_refs=refs,
    )  # fmt: skip


INSIGHTS = (
    insight("J10911A00305-742", sold=20, returned=5, lines=(("DEF", 4), ("SIZE", 1)),
            reported=(("quality_defect", 1),), n=1),
    insight("J20931A00144-999", sold=0, returned=2, lines=(("SIZE", 2),)),
)  # fmt: skip


def test_product_feedback_section_sets_reasons_beside_returns(tmp_path):
    _, _, built = run_module(tmp_path, extra=INSIGHTS)
    for report in built.values():
        section = report.markdown.split("## Product feedback\n\n")[1]
        lines = [MARKER.sub("", x) for x in section.splitlines() if x]
        assert (
            lines[0].startswith("- **")
            and "(J10911A00305-742)**, MIL01, NYC01, 09-11..10-07" in lines[0]
        )
        assert lines[1:4] == [
            ("  - reported: product feedback 1 of 1 observations, reasons: quality defect 1 of 1"),
            "  - sold 20 units, returned 5 units, return rate 25.0%",
            "  - POS return reasons: DEF 4, SIZE 1 of 5 lines",
        ]
        # No sale, no rate: the denominator is not there.
        assert lines[5:] == [
            "  - sold 0 units, returned 2 units",
            "  - POS return reasons: SIZE 2 of 2 lines",
        ]
        cited = {
            (c.ref.id, c.field, c.unit) for c in report.citations if c.ref.kind == "ProductInsight"
        }
        assert ("insight-sku-j10911a00305-742", "return_rate", "percent") in cited
        assert ("insight-sku-j20931a00144-999", "return_rate", "percent") not in cited
        assert {"insight-sku-j10911a00305-742", "insight-sku-j20931a00144-999"} <= {
            r.id for r in report.input_refs
        }
        assert len(segments(report)) == len(report.citations)
        for line in section.splitlines():
            if line.startswith(("- ", "  - ")):
                assert not NUMBER.search(re.split(r"\[\d+\]", line)[-1]), line


def test_product_feedback_shows_reported_reasons_first_and_stays_thin(tmp_path):
    many = [insight(f"S{i}-999", sold=10, returned=i, lines=(("DEF", i),)) for i in range(1, 8)]
    _, _, built = run_module(tmp_path, extra=(*many, INSIGHTS[0]))
    section = built["by_office"].markdown.split("## Product feedback")[1]
    heads = [x for x in section.splitlines() if x.startswith("- **")]
    assert len(heads) == reports.PRODUCTS_SHOWN
    assert "J10911A00305-742" in heads[0] and "S7-999" in heads[1] and "S4-999" in heads[-1]


@pytest.fixture
def pinned_observation():
    _, records = read_fixtures(FIXTURES)
    observations = {
        (r.id, r.version): r
        for r in records
        if isinstance(r, Observation) and r.quantity.kind == "exact" and r.available_at <= AS_OF
    }
    for case in records:
        if isinstance(case, Case) and case.available_at <= AS_OF:
            for pinned in case.supporting:
                if observation := observations.get((pinned.id, pinned.version)):
                    return case, observation
    raise AssertionError("fixture must contain a case with a pinned numeric observation")


def test_later_observation_version_does_not_change_pinned_report(tmp_path, pinned_observation):
    _, observation = pinned_observation
    later = observation.model_copy(
        update={
            "version": "v2",
            "quantity": observation.quantity.model_copy(update={"value": 987.0}),
        }
    )
    original_path, changed_path = tmp_path / "original", tmp_path / "changed"
    original_path.mkdir()
    changed_path.mkdir()
    _, _, original = run_module(original_path)
    _, _, changed = run_module(changed_path, extra=(later,))

    for view in original:
        assert changed[view] == original[view]
        assert reports.ref(observation) in changed[view].input_refs
        assert reports.ref(later) not in changed[view].input_refs


@pytest.mark.parametrize("missing_kind", ["Observation", "MetricFact"])
def test_unresolved_supporting_ref_does_not_use_same_id_observation(
    tmp_path, pinned_observation, missing_kind
):
    _, observation = pinned_observation

    def missing_ref(record):
        if isinstance(record, Case):
            supporting = tuple(
                ref.model_copy(update={"kind": missing_kind, "version": "missing"})
                if ref.id == observation.id
                else ref
                for ref in record.supporting
            )
            return record.model_copy(update={"supporting": supporting})
        return record

    _, _, built = run_module(tmp_path, edit=missing_ref)

    for report in built.values():
        assert not any(c.ref.id == observation.id for c in report.citations)
        assert reports.ref(observation) not in report.input_refs


def test_different_cases_can_cite_different_versions_of_one_observation(
    tmp_path, pinned_observation
):
    case, observation = pinned_observation
    later = observation.model_copy(
        update={
            "version": "v2",
            "quantity": observation.quantity.model_copy(update={"value": 987.0}),
        }
    )
    second_case = case.model_copy(
        update={"id": "case-second-version", "supporting": (reports.ref(later),)}
    )

    _, _, built = run_module(tmp_path, extra=(later, second_case))

    for report in built.values():
        cited = {c.ref for c in report.citations if c.ref.kind == "Observation"}
        assert reports.ref(observation) in cited
        assert reports.ref(later) in cited
        assert reports.ref(observation) in report.input_refs
        assert reports.ref(later) in report.input_refs
        assert "987 " in report.markdown
