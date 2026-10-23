"""RFC §7.3 gate tests 1 and 2 (TST-01, TST-02) on the real module graph.

One orchestrated pipeline over MIL01's real mailbox, ERP files and weather feed
(``generated/sources``): src.erp, src.email, src.external, ing.extract, int.link, int.dedup,
int.cases, int.context, fc.baseline, fc.overlay, out.reports. Only the LLM is replaced: a fake
answers ``ing.extract`` for three mails with candidates read off their text and nothing for the
others; ``int.link`` runs without LLM. Every run shares one database, as real replays do.

- T1 (2026-09-18 19:30Z) sees the 18/09 closing mail, not its correction sent 37 minutes later.
- T2 (2026-09-19 20:00Z) adds the correction (supersedes the turnover), the 19/09 mail (a new
  unmet-demand case) and the ERP and weather days that ended in between.

Test 1: T1 → T2 → T1 (new run ID) gives back the first T1 state, and nothing of T2 reaches the
second T1 run's reads, LLM requests, reports or module results.
Test 2: the same T2 with ``src.external`` switched off loses only the weather events and the
case versions ``int.context`` derived from them; everything else is unchanged and no case or
reference of the earlier run survives.
"""

import json
from datetime import UTC, datetime

import pytest

from tessera.core.contracts import (
    Case,
    ContextEvent,
    EvidenceRelation,
    ForecastAdjustment,
    ModuleSnapshot,
    Observation,
    Report,
    RunSpec,
    SourceDocument,
)
from tessera.core.db import connect
from tessera.core.orchestrator import run
from tessera.core.registry import Registry
from tessera.core.repo import KINDS
from tessera.core.run_repo import repo_session
from tessera.modules.sources import erp

T1 = datetime(2026, 9, 18, 19, 30, tzinfo=UTC)
T2 = datetime(2026, 9, 19, 20, 0, tzinfo=UTC)
ORIGINAL = "doc-20260918-2115-mil01"
CORRECTION = "doc-20260918-2207-mil01-corr"
NEXT_DAY = "doc-20260919-2152-mil01"
T2_ONLY = (CORRECTION, NEXT_DAY)

MODULES = (
    "src.erp", "src.email", "src.external", "ing.extract", "int.link", "int.dedup",
    "int.cases", "int.context", "fc.baseline", "fc.overlay", "out.reports",
)  # fmt: skip
PARAMS = {"src.erp": {"history_days": 7}, "int.link": {"llm": False}}

# What a model would propose for these mails; quotes and number words are verbatim.
ANSWERS = {
    ORIGINAL: [
        dict(quote="Fatturato: 58,0k", kind="sales_figure", quantity_kind="exact", value=58000,
             unit="money", currency="EUR", quantity_raw="58,0k", attribution="store_staff",
             period_start="2026-09-18", period_end="2026-09-18"),
        dict(quote="Maya nera 12 pezzi", kind="demand_up", product_mention="Maya nera",
             quantity_kind="exact", value=12, unit="units", quantity_raw="12 pezzi",
             direction="up", attribution="store_staff", period_start="2026-09-18",
             period_end="2026-09-18"),
    ],
    CORRECTION: [
        dict(quote="il fatturato di oggi e' 85,0k e non 58", kind="sales_figure",
             quantity_kind="exact", value=85000, unit="money", currency="EUR",
             quantity_raw="85,0k", attribution="store_staff", time_text="oggi",
             period_start="2026-09-18", period_end="2026-09-18"),
    ],
    NEXT_DAY: [
        dict(quote="Almeno 4 sono uscite senza perche' non c'era la taglia (2 e 3)",
             kind="unmet_demand", product_mention="Maire nera", direction="up",
             attribution="store_staff", period_start="2026-09-19", period_end="2026-09-19"),
    ],
}  # fmt: skip


class FakeLLM:
    """The ``extract`` surface of ``core.llm``; records every request it receives."""

    def __init__(self):
        self.requests = []

    def extract(self, model, messages, *, cache_context, temperature=0):
        self.requests.append({"messages": messages, "cache_context": cache_context})
        return model.model_validate({"observations": ANSWERS.get(cache_context["document"][0], [])})


REGISTRY = Registry.discover()
MANIFESTS = {m.id: m for m in REGISTRY.manifests()}


def spec(run_id, as_of, *, disabled=()):
    return RunSpec(
        run_id=run_id, scenario_id="historical", as_of=as_of, stores=("MIL01",),
        source_manifest_hash="sources", config_hash="config", code_version="test", mode="live",
        modules=tuple(
            ModuleSnapshot(
                manifest=MANIFESTS[m].model_copy(update={"enabled": m not in disabled}),
                params=PARAMS.get(m, {}),
            )
            for m in MODULES
        ),
        prompt_versions={}, model_versions={}, authorized_fixture_refs=(),
    )  # fmt: skip


class Replay:
    """One executed run: its published artifacts, module results and LLM requests."""

    def __init__(self, engine, run_spec):
        llm = FakeLLM()
        self.spec = run_spec
        self.modules = {
            m.module_id: m
            for m in run(run_spec, engine=engine, registry=REGISTRY, clients={"llm": llm})
        }
        self.requests = llm.requests
        with repo_session(engine, run_spec.run_id) as repo:
            self.state = repo.run_state()
            self.artifacts = {kind: repo.list(model) for kind, model in KINDS.items()}
            self.erp = {t: erp.read(repo, t) for t in ("sales", "stock", "forecast")}

    def of(self, model):
        return self.artifacts[model.__name__]

    def normalized(self):
        """Every artifact as JSON with this run's ID blanked: two runs compare field by field."""
        return {
            (kind, r.id, r.version): r.model_dump(mode="json") | {"run_id": "<run>"}
            for kind, records in self.artifacts.items()
            for r in records
        }

    def results(self):
        """Module results; src.erp's ``*_new`` counts say which run loaded a shared row first."""
        out = {}
        for module, status in self.modules.items():
            result = status.result and status.result.model_dump(mode="json")
            if module == "src.erp" and result:
                result["counts"] = {
                    k: v for k, v in result["counts"].items() if not k.endswith("_new")
                }
            out[module] = (status.status, result)
        return out

    def text(self) -> str:
        """Everything the run exposes: artifacts, module results and LLM requests."""
        return json.dumps(
            [sorted(self.normalized().items()), self.results(), self.requests],
            default=str,
            sort_keys=True,
        )


@pytest.fixture(scope="module")
def replays(tmp_path_factory):
    engine = connect(f"sqlite:///{tmp_path_factory.mktemp('gate') / 'replay.db'}")
    try:
        first = Replay(engine, spec("t1", T1))
        later = Replay(engine, spec("t2", T2))
        again = Replay(engine, spec("t1-again", T1))
        no_weather = Replay(engine, spec("t2-no-weather", T2, disabled=("src.external",)))
        yield {"t1": first, "t2": later, "t1-again": again, "t2-no-weather": no_weather}
    finally:
        engine.dispose()


def test_scenario_exercises_the_correction_cases_overlay_context_and_reports(replays):
    t1, t2 = replays["t1"], replays["t2"]
    for replay in (t1, t2):
        assert replay.state["published"], replay.results()
        assert {s.status for s in replay.modules.values()} <= {"succeeded", "degraded"}
        assert replay.of(Case) and replay.of(Report) and replay.of(ContextEvent)
        assert any(f.status == "computed" for f in replay.of(ForecastAdjustment))
    (supersedes,) = [r for r in t2.of(EvidenceRelation) if r.relation == "supersedes"]
    assert supersedes.from_ref.id.startswith("obs-20260918-2207")
    assert supersedes.to_ref.id.startswith("obs-20260918-2115")
    assert not t1.of(EvidenceRelation)
    assert {c.id for c in t1.of(Case)} < {c.id for c in t2.of(Case)}


def test_t1_t2_t1_restores_the_first_state_and_leaks_nothing_of_t2(replays):
    """RFC §7.3 test 1."""
    t1, t2, again = replays["t1"], replays["t2"], replays["t1-again"]
    # T2 really holds what T1 must not see, read through the same paths.
    assert {d.id for d in t2.of(SourceDocument)} >= set(T2_ONLY)
    assert any(set(T2_ONLY) & {r.id for r in o.input_refs} for o in t2.of(Observation))
    assert max(r.available_at for rows in t2.erp.values() for r in rows) > T1
    # The second T1 run is the first one again: artifacts, module results, LLM requests.
    assert again.normalized() == t1.normalized()
    assert again.results() == t1.results()
    assert again.requests == t1.requests
    # Nothing in it is later than T1 or names a T2 document, ERP rows included.
    for replay in (t1, again):
        assert all(
            r.available_at is not None and r.available_at <= T1
            for records in replay.artifacts.values()
            for r in records
        )
        assert all(r.available_at <= T1 for rows in replay.erp.values() for r in rows)
        text = replay.text()
        for doc in T2_ONLY:
            assert doc not in text
        assert "e non 58" not in text and "ragazze coreane" not in text
        assert all(rep.as_of == T1 for rep in replay.of(Report))
    assert len(again.requests) == len(t1.requests) < len(t2.requests)


def test_switching_a_source_off_removes_only_its_consequences(replays):
    """RFC §7.3 test 2: ``src.external`` off, same T2 otherwise."""
    on, off = replays["t2"], replays["t2-no-weather"]
    assert off.state["published"] and "src.external" not in off.modules
    assert off.modules["int.context"].status == "degraded"
    # The source's own evidence is gone, and so is every reference to it.
    assert on.of(ContextEvent) and not off.of(ContextEvent)
    assert "ContextEvent" not in off.text()
    # int.context's case versions are its consequence; the cases themselves are not.
    derived = {(c.id, c.version) for c in on.of(Case) if c.version.endswith(".ctx")}
    assert derived and all(
        any(r.kind == "ContextEvent" for r in c.context_refs)
        for c in on.of(Case)
        if (c.id, c.version) in derived
    )
    assert {c.id for c in off.of(Case)} == {c.id for c in on.of(Case)}
    before, after = on.normalized(), off.normalized()
    gone = {key for key in before if key not in after}
    assert gone == {("ContextEvent", r.id, r.version) for r in on.of(ContextEvent)} | {
        ("Case", *key) for key in derived
    }
    assert set(after) <= set(before)
    # What stays is identical field by field, except that downstream records cite the case
    # version without weather (and hash their inputs accordingly).
    changed = {key for key in after if after[key] != before[key]}
    assert {key[0] for key in changed} <= {"ForecastAdjustment", "Report"}
    for key in changed:
        assert without_context(after[key], derived) == without_context(before[key], derived)
    # Reports keep every section and number; nothing cites the weather any more.
    assert [r.id for r in off.of(Report)] == [r.id for r in on.of(Report)]
    for report in off.of(Report):
        assert not {(r.kind, r.id, r.version) for r in report.input_refs} & gone
    # The other modules saw the same inputs and reported the same results.
    for module in set(MODULES) - {"src.external", "int.context"}:
        assert off.results()[module] == on.results()[module], module


def without_context(value, derived):
    """``value`` with refs to ``int.context``'s case versions pointed back to the case."""
    if isinstance(value, list):
        return [without_context(v, derived) for v in value]
    if not isinstance(value, dict):
        return value
    if value.get("kind") == "Case" and (value.get("id"), value.get("version")) in derived:
        return value | {"version": value["version"].removesuffix(".ctx")}
    return {k: without_context(v, derived) for k, v in value.items() if k != "input_version_hash"}
