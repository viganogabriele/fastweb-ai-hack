"""OUT-01: `out.reports` renders the brief from the run's facts, every number from a citation.

The smoke run loads the DATA-01a/b fixtures (and the DATA-01c options) into one fixture run and
checks the module's `by_office` brief against the hand-checked DATA-01b report fixture.
"""

import json
import re
from collections import Counter
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from tessera.core.config import REPO_ROOT
from tessera.core.contracts import Case, Citation, Report, RunSpec
from tessera.core.db import connect
from tessera.core.fixtures import read_fixtures
from tessera.core.registry import Registry
from tessera.core.repo import Repo, create_run, put_erp
from tessera.modules.outputs import reports
from tessera.modules.sources import erp

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


def run_module(tmp_path, *, kinds=INPUTS, as_of=AS_OF, params=None, edit=lambda r: r):
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
