"""Record or replay the two real-model `ag.investigator` dev traces (AG-03b).

Run from the repo root. Recording calls the Fastweb chat model and needs its key in
`.secrets/fastweb_keys.json`; replay is offline and reads only the committed recordings:

    LLM_MODE=record backend/.venv/bin/python data/fixtures/build_ag03b.py
    LLM_MODE=replay backend/.venv/bin/python data/fixtures/build_ag03b.py

What it is. The real `investigate` service and LLM adapter, with the pinned model
(`investigator.MODEL`), on two DATA-01b dev cases whose evidence calls for different checks
(RFC §4.8.2):

- `case-mil01-i10919b00011-20261008` (D1, stock): cardigan M out of stock at MIL01; the model has
  to read destination and donor stock, lanes and the deterministic options;
- `case-nyc01-unknown-20260906` (ambiguous identity): "a sweatshirt" with tied candidates; the
  model has to draft a clarification in English and stop at `verify`.

Inputs are fixture-backed and frozen in `traces/recorded/inputs.json` (a snapshot of the fixture
records at recording time), so later fixture edits do not invalidate the recordings. Stock is read
from those `StockFact`s; lanes come back `unknown` (no lane store in the fixtures): the model sees
that and the options engine keeps the movement checks unknown. The run's `as_of` is the latest
fixture `available_at`, as `tesseract fixtures load` sets it.

Outputs, under `data/fixtures/traces/recorded/` (two levels deep, so `tesseract fixtures load` does
not load them as fixture records):

- `llm_cache/`: the provider responses, content-addressed exactly as `data/llm_cache/` is;
- `<case_id>.json`: the resulting `AgentTrace` (with `mode=fixture`), plus the model id.

Replay rebuilds both traces from `llm_cache/` alone and fails on any miss. The trace id holds a
random suffix, so replay compares everything but `id`.
"""

import json
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from tesseract.core.cache import ResponseCache
from tesseract.core.config import Settings
from tesseract.core.contracts import RunSpec, StockFact
from tesseract.core.db import connect
from tesseract.core.fixtures import FIXTURE_RUN_ID, FIXTURE_SCENARIO_ID, read_fixtures
from tesseract.core.llm import LLMClient
from tesseract.core.repo import KINDS, ErpRecord, Repo, create_run, put_erp
from tesseract.core.run_repo import repo_session
from tesseract.modules.actions.options import load_policy
from tesseract.modules.agents import investigator as agent
from tesseract.modules.agents.chat_model import model_for_run
from tesseract.modules.sources.systems_client import Unknown

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "data" / "fixtures"
OUT = FIXTURES / "traces" / "recorded"
CASES = ("case-mil01-i10919b00011-20261008", "case-nyc01-unknown-20260906")
STORES = (
    ("MIL01", "IT", "it", "Europe/Rome"),
    ("MIL02", "IT", "it", "Europe/Rome"),
    ("NYC01", "US", "en", "America/New_York"),
)
SKUS = ("I10919B00011-999", "I10919B00011-742")


class FixtureReader:
    """Stock from the frozen `StockFact`s; no lane data, so every lane is unknown."""

    def __init__(self, repo: Repo):
        self.repo = repo

    def stock(self, sku, size, locations):
        return {
            location: tuple(
                f
                for f in self.repo.list(StockFact, sku=sku)
                if f.location_id == location and f.size == size
            )
            or Unknown("unavailable", "no stock snapshot in the fixture inputs")
            for location in locations
        }

    def lane_and_eta(self, origin, dest, requested_at, required_by=None):
        return Unknown("unavailable", "no lane data in the fixture inputs")


def snapshot_inputs() -> None:
    _, records = read_fixtures(FIXTURES)
    rows = [{"kind": type(r).__name__, "payload": r.model_dump(mode="json")} for r in records]
    (OUT / "inputs.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")


def load_inputs():
    rows = json.loads((OUT / "inputs.json").read_text(encoding="utf-8"))
    return [KINDS[r["kind"]].model_validate(r["payload"]) for r in rows]


def run_spec(records) -> RunSpec:
    return RunSpec(
        run_id=FIXTURE_RUN_ID,
        scenario_id=FIXTURE_SCENARIO_ID,
        as_of=max(r.available_at for r in records if r.available_at is not None),
        stores=tuple(s for s, *_ in STORES),
        source_manifest_hash="fixtures:ag03b/inputs.json",
        config_hash="config:domain.yaml",
        code_version="ag03b",
        mode="fixture",
        modules=(),
        prompt_versions={agent.MANIFEST.id: agent.PROMPT_VERSION},
        model_versions={},
        authorized_fixture_refs=("traces/recorded/inputs.json",),
    )


def erp_rows() -> list[ErpRecord]:
    at = datetime(2026, 8, 1, tzinfo=UTC)
    rows = []

    def row(table, id, data):
        rows.append(ErpRecord(table, id, "1", at, "ag03b", (), data))

    for store, country, language, timezone in STORES:
        row(
            "stores",
            store,
            dict(store_id=store, country_code=country, language=language, timezone=timezone),
        )
    for sku in SKUS:
        row("sku_colour", sku, dict(sku=sku, style_code=sku.split("-")[0]))
        row("sku_size_ean", f"{sku}-M", dict(sku=sku, size="M", ean="fixture-ean"))
        for store in ("MIL01", "MIL02"):
            row("assortment", f"{store}-{sku}", dict(store_id=store, sku=sku))
    return rows


def investigate_all(settings: Settings, workdir: Path, **llm_options) -> dict[str, dict]:
    """Run both cases; `llm_options` go to `LLMClient` (tests pass a client factory that fails)."""
    records = load_inputs()
    spec = run_spec(records)
    engine = connect(f"sqlite:///{workdir / 'ag03b.db'}")
    try:
        create_run(engine, spec)
        Repo(engine, spec).put(*records)
        put_erp(engine, erp_rows())
        llm = LLMClient(settings, cache=ResponseCache(OUT / "llm_cache"), **llm_options).for_run(
            spec
        )
        policy = load_policy(settings.config_dir)
        out = {}
        for case_id in CASES:
            with repo_session(engine, spec, fixture_mode=True) as repo:
                case = agent.visible_case(repo, case_id)
                model = model_for_run(
                    llm,
                    prompt_version=agent.PROMPT_VERSION,
                    model=agent.MODEL,
                    cache_context={"case": case.model_dump(mode="json")},
                )
                result = agent.investigate(
                    repo, case_id, model=model, reader=FixtureReader(repo), policy=policy
                )
            out[case_id] = {
                "model": agent.MODEL,
                "trace": result.trace.model_dump(mode="json"),
            }
        return out
    finally:
        engine.dispose()


def comparable(entry: dict) -> dict:
    trace = {k: v for k, v in entry["trace"].items() if k != "id"}
    trace["steps"] = [{k: v for k, v in s.items() if k != "duration_ms"} for s in trace["steps"]]
    return {**entry, "trace": trace}


def main() -> int:
    settings = Settings()
    if settings.llm_mode == "live":
        print(
            "Use LLM_MODE=record or replay: live calls do not save the responses needed "
            "to replay these traces.",
            file=sys.stderr,
        )
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    if settings.llm_mode == "record" and not (OUT / "inputs.json").exists():
        snapshot_inputs()
    with tempfile.TemporaryDirectory() as tmp:
        traces = investigate_all(settings, Path(tmp))
    for case_id, entry in traces.items():
        path = OUT / f"{case_id}.json"
        steps = [s["tool"] for s in entry["trace"]["steps"]]
        print(
            case_id, entry["trace"]["outcome"], steps, "fallback" * entry["trace"]["fallback_used"]
        )
        if settings.llm_mode == "replay":
            if comparable(json.loads(path.read_text())) != comparable(entry):
                print(f"{path.name}: replay differs from the recorded trace", file=sys.stderr)
                return 1
        else:
            path.write_text(json.dumps(entry, indent=1, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
