"""INT-01 module: `int.link` writes one `EntityLink` per observation, never a guessed link.

Real catalog master rows (ERP CSVs) and the DATA-01a document/observation fixtures, written
through PLT-04's `RunRepo` so parent and store-scope checks apply. The LLM is a fake.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from tessera.core.config import REPO_ROOT
from tessera.core.contracts import EntityLink, Observation, RunSpec
from tessera.core.db import connect
from tessera.core.fixtures import read_fixtures
from tessera.core.registry import Registry
from tessera.core.repo import put_erp
from tessera.core.run_repo import repo_session
from tessera.modules.integration import link
from tessera.modules.integration.link import LinkChoice
from tessera.modules.sources import erp

SOURCES = REPO_ROOT / "generated" / "sources"
FIXTURES = REPO_ROOT / "data" / "fixtures"
AS_OF = datetime(2026, 10, 22, 20, tzinfo=UTC)
MASTER_AT = datetime(2026, 8, 1, tzinfo=UTC)
SWEATSHIRT = "obs-20260906-1837-nyc01-sweatshirt-return"


class FakeLLM:
    def __init__(self, answer=None, error: Exception | None = None) -> None:
        self.answer, self.error, self.calls = answer, error, []

    def extract(self, schema, messages, *, cache_context=None, **generation):
        self.calls.append({"schema": schema, "messages": messages, "context": cache_context,
                           "generation": generation})  # fmt: skip
        if self.error is not None:
            raise self.error
        return (
            self.answer(json.loads(messages[-1]["content"]))
            if callable(self.answer)
            else (self.answer)
        )


def spec() -> RunSpec:
    return RunSpec(
        run_id="fixture", scenario_id="historical", as_of=AS_OF, stores=("MIL01", "NYC01"),
        source_manifest_hash="s", config_hash="c", code_version="0", mode="fixture", modules=(),
        prompt_versions={}, model_versions={}, authorized_fixture_refs=(),
    )  # fmt: skip


@pytest.fixture
def engine(tmp_path: Path):
    engine = connect(f"sqlite:///{tmp_path / 't.db'}")
    stores = erp.load_csv("master_data/stores.csv", "stores", sources_dir=SOURCES, as_of=AS_OF,
                          store_timezones={}, master_available_at=MASTER_AT)  # fmt: skip
    zones = {r.data["store_id"]: r.data["timezone"] for r in stores}
    rows = list(stores)
    for relative, table in (
        ("master_data/sku_colour.csv", "sku_colour"),
        ("master_data/sku_size_ean.csv", "sku_size_ean"),
        ("master_data/store_assortment.csv", "assortment"),
    ):
        rows += erp.load_csv(relative, table, sources_dir=SOURCES, as_of=AS_OF,
                             store_timezones=zones, master_available_at=MASTER_AT)  # fmt: skip
    put_erp(engine, rows)
    _, records = read_fixtures(FIXTURES)
    kinds = ("SourceDocument", "Segment", "Observation")
    inputs = [r for r in records if type(r).__name__ in kinds]
    with repo_session(engine, spec(), fixture_mode=True, write=True) as repo:
        repo.put(*inputs)
    return engine


def run(engine, params=None, llm=None, observations=None):
    with repo_session(engine, spec(), fixture_mode=True, write=True) as repo:
        if observations is not None:
            repo.put(*observations)
        ctx = SimpleNamespace(spec=repo.spec, repo=repo, params=params or {},
                              clients={} if llm is None else {"llm": llm})  # fmt: skip
        result = link.run(ctx)
        links = {lk.observation_id: lk for lk in repo.list(EntityLink)}
    return result, links


def observation(engine, obs_id: str) -> Observation:
    with repo_session(engine, spec(), fixture_mode=True) as repo:
        return next(o for o in repo.list(Observation) if o.id == obs_id)


def test_manifest_is_discovered_and_valid() -> None:
    manifests = {m.id: m for m in Registry.discover().manifests()}
    assert manifests["int.link"] == link.MANIFEST
    assert link.MANIFEST.requires == ("src.erp",)
    assert link.MANIFEST.optional_inputs == ("ing.extract",)


def test_fixture_observations_match_the_data01b_link_fixtures(engine) -> None:
    result, links = run(engine)
    assert result.status == "succeeded", result
    expected = {
        p["observation_id"]: (p["status"], p["level"], p["target_id"])
        for f in sorted((FIXTURES / "links").glob("*.json"))
        for p in (r["payload"] for r in json.loads(f.read_text()) if r["kind"] == "EntityLink")
    }
    assert {k: (v.status, v.level, v.target_id) for k, v in links.items()} == expected
    assert result.counts == {"observations": 8, "links_new": 8, "llm_linked": 0, "linked": 5,
                             "ambiguous": 1, "unlinked": 0, "not_product": 2}  # fmt: skip


def test_links_keep_candidates_scale_and_provenance(engine) -> None:
    _, links = run(engine)
    maire = links["obs-20261002-2112-mil01-maire-requests"]
    assert maire.input_refs[0].kind == "Observation"
    assert maire.available_at == observation(engine, maire.observation_id).available_at
    assert any(r.uri.endswith("erp/master_data/sku_colour.csv") for r in maire.source_refs)
    assert all((c.score_min, c.score_max) == (0.0, 100.0) for c in maire.candidates)
    cardigan = links["obs-20261009-1035-mil01-stockout"]  # "sia nero che blu"
    assert (cardigan.level, cardigan.decided_by) == ("style", "rule:same_style")
    assert {c.target_id for c in cardigan.candidates} >= {"I10919B00011-999", "I10919B00011-742"}
    ambiguous = links[SWEATSHIRT]
    assert ambiguous.target_id is None and len(ambiguous.candidates) >= 2


def test_llm_breaks_a_tie_only_among_offered_candidates(engine) -> None:
    llm = FakeLLM(lambda p: LinkChoice(target_id=p["candidates"][0]["target_id"], rationale="r"))
    result, links = run(engine, llm=llm)
    (call,) = llm.calls  # only the ambiguous observation reaches the LLM
    payload = json.loads(call["messages"][-1]["content"])
    assert payload["mention"] == "a sweatshirt"
    offered = [c["target_id"] for c in payload["candidates"]]
    assert set(offered) <= {c.target_id for c in links[SWEATSHIRT].candidates}
    assert call["messages"][0]["content"] == link.PROMPT_PATH.read_text(encoding="utf-8")
    assert call["context"]["prompt_version"] == "link_choice.v1"
    assert call["generation"] == {"temperature": 0}
    chosen = links[SWEATSHIRT]
    assert (chosen.status, chosen.target_id, chosen.decided_by) == (
        "linked", offered[0], "llm:link_choice.v1",
    )  # fmt: skip
    assert result.counts["llm_linked"] == 1


@pytest.mark.parametrize("answer", [None, "J20931A00012-999"])  # null, or an id not offered
def test_llm_without_a_valid_choice_keeps_the_link_ambiguous(engine, answer) -> None:
    result, links = run(engine, llm=FakeLLM(LinkChoice(target_id=answer, rationale="r")))
    assert links[SWEATSHIRT].status == "ambiguous"
    assert links[SWEATSHIRT].decided_by == "llm:link_choice.v1"
    assert result.status == "succeeded"


def test_llm_failure_keeps_ambiguous_and_degrades(engine) -> None:
    result, links = run(engine, llm=FakeLLM(error=RuntimeError("replay miss")))
    assert links[SWEATSHIRT].status == "ambiguous"
    assert result.status == "degraded"
    assert result.errors == (f"{SWEATSHIRT}: llm RuntimeError",)


def test_llm_can_be_switched_off(engine) -> None:
    llm = FakeLLM(LinkChoice(target_id=None, rationale="r"))
    _, links = run(engine, params={"llm": False}, llm=llm)
    assert llm.calls == [] and links[SWEATSHIRT].decided_by == "rule:link_mention"


def test_size_outside_the_size_run_never_reaches_the_llm(engine) -> None:
    base = observation(engine, "obs-20261002-2112-mil01-maire-requests")
    mention = "Maire nera taglia 9"
    odd = base.model_copy(update={"id": "obs-maire-size-9", "product_mention": mention})
    llm = FakeLLM(LinkChoice(target_id="J20931A00012-999", rationale="r"))
    _, links = run(engine, llm=llm, observations=[odd])
    assert links["obs-maire-size-9"].status == "ambiguous"
    assert any("size_not_in_size_run" in c.method for c in links["obs-maire-size-9"].candidates)
    assert all(c["messages"][-1]["content"].find("Maire nera taglia 9") < 0 for c in llm.calls)


def test_missing_catalog_blocks(tmp_path) -> None:
    engine = connect(f"sqlite:///{tmp_path / 'empty.db'}")
    with repo_session(engine, spec(), fixture_mode=True, write=True) as repo:
        ctx = SimpleNamespace(spec=repo.spec, repo=repo, params={}, clients={})
        assert link.run(ctx).status == "blocked"


@pytest.mark.parametrize(
    ("mention", "size"),
    [("gilet Tib blu taglia 4", "4"), ("Maire tg. 3", "3"), ("size M please", "M"),
     ("cardigan logo in M", None), ("Maire nera", None)],
)  # fmt: skip
def test_size_in_mention_needs_an_explicit_size_word(mention, size) -> None:
    assert link.size_in(mention) == size


def test_shared_aliases_go_to_every_style_they_name() -> None:
    styles, colours = link.load_aliases(REPO_ROOT / "config" / "aliases.yaml")
    assert "sweat" in styles["I10918G00031"] and "sweat" in styles["I10918G00045"]
    assert "nera" in colours["999"]
