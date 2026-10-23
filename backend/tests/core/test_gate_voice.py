"""RFC §7.3 gate test 2 for the literal voice source (release-gate-audit §2).

The same orchestrated MIL01 pipeline as ``test_gate_temporal`` (real mailbox, ERP files and
weather feed), plus ``src.voice`` over the committed DATA-03 notes in ``data/fixtures/voice``.
The notes publish their declared manual transcripts (``mode: fixture``): the explicitly declared
fallback, so no ASR recording is needed. Only the LLM is replaced: a fake answers ``ing.extract``
for one closing mail and the two MIL01 notes with quotes copied from their text; the product
mentions name catalog styles, so the notes open SKU-level cases rather than verify requests.

Voice off, same clock otherwise: the notes' documents, the observations read from them and every
artifact that cites them (links, cases, overlays, reports) disappear or are recomputed without
them. Every other artifact stays identical field by field, and nothing of
the voice notes survives anywhere in the run.
"""

import json
from datetime import UTC, datetime

import pytest

from tesseract.core.config import REPO_ROOT
from tesseract.core.contracts import Case, ModuleSnapshot, Observation, RunSpec, SourceDocument
from tesseract.core.db import connect
from tesseract.core.orchestrator import run
from tesseract.core.registry import RegisteredModule, Registry
from tesseract.core.repo import KINDS
from tesseract.core.run_repo import repo_session
from tesseract.modules.sources import voice

AS_OF = datetime(2026, 10, 22, 18, 0, tzinfo=UTC)  # after both MIL01 notes (17:05Z, 17:40Z)
VOICE_DIR = REPO_ROOT / "data" / "fixtures" / "voice"
MAIL = "doc-20261021-2125-mil01"
SCARF = "doc-voice-mil01-cashmere-scarf-vest-size"
COAT = "doc-voice-mil01-melange-touch-belted-coat-fit"
MARK = "voice-mil0"  # every identifier derived from a note carries its slug

MODULES = (
    "src.erp", "src.email", "src.external", "src.voice", "ing.extract", "int.link", "int.dedup",
    "int.cases", "int.context", "fc.baseline", "fc.overlay", "out.reports",
)  # fmt: skip
PARAMS = {
    "src.erp": {"history_days": 7},
    "int.link": {"llm": False},
    "src.voice": {"mode": "fixture"},
}

ANSWERS = {
    MAIL: [
        dict(quote="Domani ne vengono a ritirare altre, almeno 6 hanno confermato",
             kind="demand_up", product_mention="Aurea nera", quantity_kind="exact", value=6,
             unit="customers", quantity_raw="6", direction="up", attribution="store_staff",
             period_start="2026-10-22", period_end="2026-10-22"),
    ],
    SCARF: [
        dict(quote="due clienti, che vestirebbero taglia 3, hanno guardato a lungo il gilet in "
                   "piumino blu notte, ma in negozio avevamo solo la 2 e la 4",
             kind="unmet_demand", product_mention="Vel blu notte taglia 3",
             quantity_kind="exact", value=2, unit="customers", quantity_raw="due",
             direction="up", attribution="store_staff", period_start="2026-10-22",
             period_end="2026-10-22"),
    ],
    COAT: [
        dict(quote="3 clienti hanno provato il cappotto lungo in piumino con cintura, quello "
                   "marrone cioccolato, in taglia 2, ma lo sentivano troppo stretto in vita",
             kind="product_feedback", reason="fit", product_mention="Amalia marrone cioccolato",
             quantity_kind="exact", value=3, unit="customers", quantity_raw="3",
             attribution="store_staff", period_start="2026-10-22", period_end="2026-10-22"),
    ],
}  # fmt: skip


class FakeLLM:
    """The ``extract`` surface of ``core.llm``; records every request it receives."""

    def __init__(self):
        self.requests = []

    def extract(self, model, messages, *, cache_context, temperature=0):
        self.requests.append({"messages": messages, "cache_context": cache_context})
        return model.model_validate({"observations": ANSWERS.get(cache_context["document"][0], [])})


def registry():
    """The installed modules, with ``src.voice`` reading the committed notes explicitly."""
    found = Registry.discover()._entries.values()
    return Registry(
        RegisteredModule(e.manifest, lambda ctx: voice.run(ctx, voice_dir=VOICE_DIR))
        if e.manifest.id == "src.voice"
        else e
        for e in found
    )


REGISTRY = registry()
MANIFESTS = {m.id: m for m in REGISTRY.manifests()}


def spec(run_id, *, disabled=()):
    return RunSpec(
        run_id=run_id, scenario_id="historical", as_of=AS_OF, stores=("MIL01",),
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
        self.modules = {
            m.module_id: m
            for m in run(run_spec, engine=engine, registry=REGISTRY, clients={"llm": llm})
        }
        self.requests = llm.requests
        with repo_session(engine, run_spec.run_id) as repo:
            self.state = repo.run_state()
            self.artifacts = {kind: repo.list(model) for kind, model in KINDS.items()}

    def of(self, model):
        return self.artifacts[model.__name__]

    def normalized(self):
        """Every artifact as JSON with this run's ID blanked: two runs compare field by field."""
        return {
            (kind, r.id, r.version): r.model_dump(mode="json") | {"run_id": "<run>"}
            for kind, records in self.artifacts.items()
            for r in records
        }

    def result(self, module):
        """src.erp's ``*_new`` counts say which run loaded a shared row first."""
        status = self.modules[module]
        result = status.result and status.result.model_dump(mode="json")
        if module == "src.erp" and result:
            result["counts"] = {k: v for k, v in result["counts"].items() if not k.endswith("_new")}
        return status.status, result

    def text(self) -> str:
        return json.dumps(
            [sorted(self.normalized().items()), list(self.modules), self.requests],
            default=str,
            sort_keys=True,
        )


def refs(value):
    """Every ``{kind, id, version}`` reference nested in an artifact's JSON."""
    if isinstance(value, list):
        for item in value:
            yield from refs(item)
    elif isinstance(value, dict):
        if {"kind", "id", "version"} <= value.keys():
            yield value["kind"], value["id"], value["version"]
        for item in value.values():
            yield from refs(item)


def voice_consequences(records):
    """Artifacts derived from a note: its own records, then anything citing one, to a fixpoint."""
    tainted = {key for key, value in records.items() if MARK in json.dumps(value)}
    while True:
        more = {key for key, value in records.items() if set(refs(value)) & tainted} - tainted
        if not more:
            return tainted
        tainted |= more


@pytest.fixture(scope="module")
def replays(tmp_path_factory):
    engine = connect(f"sqlite:///{tmp_path_factory.mktemp('gate-voice') / 'replay.db'}")
    try:
        yield (
            Replay(engine, spec("voice-on")),
            Replay(engine, spec("voice-off", disabled=("src.voice",))),
        )
    finally:
        engine.dispose()


def test_voice_notes_feed_the_pipeline(replays):
    on, _ = replays
    assert on.state["published"], {m: on.result(m) for m in on.modules}
    status, result = on.result("src.voice")
    assert status == "succeeded"
    assert {k: result["counts"][k] for k in ("documents", "declared", "not_in_run")} == {
        "documents": 2,
        "declared": 2,
        "not_in_run": 1,
    }
    notes = {d.id for d in on.of(SourceDocument) if d.connector == "src.voice"}
    assert notes == {SCARF, COAT}
    assert {o.document_id for o in on.of(Observation)} >= {MAIL, SCARF, COAT}
    # The notes reach resolved-scope cases and a forecast overlay, not only a verify queue.
    cited = {c.scope_level for c in on.of(Case) if MARK in c.model_dump_json()}
    assert cited == {"sku", "sku_size"}
    assert any(key[0] == "ForecastAdjustment" for key in voice_consequences(on.normalized()))


def test_switching_voice_off_removes_only_its_consequences(replays):
    """RFC §7.3 test 2 for ``src.voice``: off, same clock otherwise."""
    on, off = replays
    assert off.state["published"] and "src.voice" not in off.modules
    # Nothing of the notes survives: documents, quotes, references, LLM requests.
    text = off.text()
    assert MARK not in text
    for quotes in (ANSWERS[SCARF], ANSWERS[COAT]):
        assert all(q["quote"] not in text for q in quotes)
    before, after = on.normalized(), off.normalized()
    tainted = voice_consequences(before)
    assert {k[1] for k in tainted if k[0] == "SourceDocument"} == {SCARF, COAT}
    # Every artifact that does not derive from a note is identical with voice off.
    for key in set(before) - tainted:
        assert after.get(key) == before[key], key
    # What voice off adds or changes is a recomputation of something voice had affected.
    touched = {(kind, record_id) for kind, record_id, _ in tainted}
    for key in set(after):
        if after[key] != before.get(key):
            assert key[:2] in touched, key
    # The mail's case is still there; cases opened only by a note are gone, not renamed.
    assert {c.id for c in off.of(Case)} <= {c.id for c in on.of(Case)}
    assert any(MAIL in c.model_dump_json() for c in off.of(Case))
    # Sources other than voice read the same inputs and report the same results.
    for module in ("src.erp", "src.email", "src.external"):
        assert off.result(module) == on.result(module), module
    assert off.requests == [r for r in on.requests if MARK not in json.dumps(r["cache_context"])]
