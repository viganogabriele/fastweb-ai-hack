"""TST-08, RFC §7.3 gate test 8: cutoffs, `required_by`, and no future costs in a replay.

"Cutoff con pickup successivo fattibile e cutoff con `required_by` mancata hanno esiti diversi;
costi/ritardi futuri non vengono letti dal replay passato."

Clause 1, at the three places a cutoff is decided:

- `SystemsReader.lane_and_eta`: a missed cutoff rolls to the next pickup; that pickup is on time
  for one `required_by` and late for an earlier one;
- `evaluate_options`: a missed cutoff whose next pickup still sells within the horizon keeps the
  transfer; one whose next pickup sells after it fails `eta_in_time` and blocks the move;
- INT-04 decision calendars: the same slots give a decision deadline (the next feasible cutoff)
  or none with a stated uncertainty, depending only on `required_by`.

Clause 2: a past replay (run evening Wed 2026-10-14) does not read what is published later: ERP
stock and forecast rows of a later run, observed lane delays, a lane cost reviewed after `as_of`,
a decision calendar published after `as_of`.

Lane MIL02 → MIL01 (as in `test_options`): pickup Mon-Fri 12:00 Milan, one transit day, sellable
the day after the ETA. The run is at 20:00 Milan, after that day's cutoff.
"""

import json
from dataclasses import replace
from datetime import UTC, date, datetime, time, timedelta
from types import SimpleNamespace

import httpx

from tesseract.core.config import REPO_ROOT
from tesseract.core.contracts import ActionOption, RunSpec, SourceRef
from tesseract.core.db import connect
from tesseract.core.repo import Repo, create_run
from tesseract.modules.actions import options
from tesseract.modules.actions.options import evaluate_options
from tesseract.modules.integration.reconciliation import ArrivalSlot, DecisionCalendar, reconcile
from tesseract.modules.intelligence import baseline
from tesseract.modules.sources import erp
from tesseract.modules.sources.systems_client import (
    Crosswalk,
    LaneEta,
    SystemsClient,
    SystemsReader,
    Unknown,
    eta,
)
from tests.modules.actions.test_options import (
    AS_OF,
    DEST_STOCK,
    FORECAST,
    ROME,
    SIZES,
    SKU,
    STOCK,
    fixture_case,
    inputs,
    lane,
    sources,  # noqa: F401  (pytest fixture)
    write,
)

WED, THU, FRI, SAT = (date(2026, 10, 14) + timedelta(days=i) for i in range(4))
CROSSWALK = Crosswalk(
    store_plant={"MIL01": "1001", "MIL02": "1002"},
    timezones={"MIL01": "Europe/Rome", "MIL02": "Europe/Rome"},
    sku_matnr={SKU: SKU.replace("-", "")},
    ean_sku_size={},
)
TEMPLATE = json.loads(
    (
        REPO_ROOT / "generated/sources/systems/agents/examples/logistics_get_lane_MIL02_MIL01.json"
    ).read_text()
)["response"]


def milan(day: date, hour: int) -> datetime:
    return datetime.combine(day, time(hour), ROME)


def lane_server(seen: list | None = None, **update):
    """Mock logistics service: the MIL02 → MIL01 lane with ``update`` applied."""

    def handler(request: httpx.Request) -> httpx.Response:
        if seen is not None:
            seen.append(request.url.params["origin"])
        origin, dest = request.url.params["origin"], request.url.params["dest"]
        body = TEMPLATE | {
            "lane_id": f"LN-{origin}-{dest}",
            "origin": origin,
            "dest": dest,
            "mode": "ROAD_EXPRESS",
            "transit_days_contract": 1,
            "transit_days_p90_contract": 2,
            "pickup_cutoff_local": "12:00",
        }
        return httpx.Response(200, json=body | update)

    return SystemsClient(CROSSWALK, transport=httpx.MockTransport(handler))


def reader_at(as_of: datetime, client: SystemsClient) -> SystemsReader:
    return SystemsReader(SimpleNamespace(spec=SimpleNamespace(as_of=as_of)), client)


def recommended(opts) -> list[str]:
    return [o.kind for o in opts if o.recommended]


# Clause 1: missed cutoff with a feasible later pickup vs missed required_by


def test_lane_missed_cutoff_rolls_to_next_pickup_and_required_by_decides():
    reader = reader_at(AS_OF, lane_server())
    feasible = reader.lane_and_eta("MIL02", "MIL01", AS_OF, required_by=milan(SAT, 10))
    late = reader.lane_and_eta("MIL02", "MIL01", AS_OF, required_by=milan(THU, 18))

    for got in (feasible, late):
        assert isinstance(got, LaneEta)
        assert got.eta.missed_cutoff  # 20:00 is after Wednesday's 12:00 cutoff
        assert got.eta.pickup_at == milan(THU, 12) and got.eta.eta_date == FRI
    assert feasible.on_time is True
    assert late.on_time is False


def test_lane_cannot_pick_up_before_the_decision():
    # Asking for an earlier pickup than the run's evening is clamped to the run's as_of.
    reader = reader_at(AS_OF, lane_server())
    got = reader.lane_and_eta("MIL02", "MIL01", milan(WED, 9), required_by=milan(THU, 18))
    assert isinstance(got, LaneEta) and got.eta.pickup_at == milan(THU, 12)
    assert got.on_time is False


def test_options_keep_a_move_whose_next_pickup_is_still_in_time():
    opts = evaluate_options(inputs())  # missed Wed cutoff, Thu pickup, sellable Sat 17

    t = {o.kind: o for o in opts}["transfer"]
    detail = {c.name: c.detail for c in t.checks}
    assert "cut-off missed: next pickup" in detail["pickup_calendar"]
    assert {c.name: c.status for c in t.checks}["eta_in_time"] == "pass"
    assert t.legs[0].pickup_at == milan(THU, 12)
    assert recommended(opts) == ["transfer"]


def test_options_block_a_move_whose_next_pickup_misses_the_horizon():
    # Same missed cutoff, but the lane only picks up on Wednesdays: next pickup Wed 21,
    # sellable Fri 23, after the horizon (Thu 15 .. Wed 21).
    weekly_lane = replace(lane().lane, pickup_days=frozenset({2}))
    got = eta(weekly_lane, AS_OF)
    assert not isinstance(got, Unknown) and got.missed_cutoff
    opts = evaluate_options(inputs(route_lane=LaneEta(weekly_lane, got, None, None)))

    t = {o.kind: o for o in opts}["transfer"]
    assert {c.name: c.status for c in t.checks}["eta_in_time"] == "fail"
    assert t.legs[0].pickup_at == milan(date(2026, 10, 21), 12)
    assert not t.recommended
    (follow_up,) = recommended(opts)
    assert follow_up in {"hold", "verify_stock", "ask_store", "notify_owner"}
    assert "eta_in_time" in {o.kind: o for o in opts}["hold"].rationale


def calendar(required_by: datetime, *, available_at: datetime = AS_OF - timedelta(days=1)):
    return DecisionCalendar(
        case_id=fixture_case().id,
        available_at=available_at,
        required_by=required_by,
        source_refs=(SourceRef(uri="test://calendar", content_hash="sha256:calendar"),),
        slots=(
            ArrivalSlot(cutoff_at=milan(WED, 12), sellable_at=milan(FRI, 0)),  # cutoff passed
            ArrivalSlot(cutoff_at=milan(THU, 12), sellable_at=milan(SAT, 0)),
        ),
    )


def reconciled(*calendars: DecisionCalendar):
    return reconcile(fixture_case(), (), (), (), calendars, as_of=AS_OF, timezone="Europe/Rome")


def test_calendar_missed_cutoff_with_feasible_later_slot_sets_the_deadline():
    case = reconciled(calendar(milan(SAT, 10)))
    assert case.decision_due_at == milan(THU, 12)
    assert not any("required_by" in u for u in case.blocking_uncertainties)


def test_calendar_with_required_by_missed_has_no_deadline_and_says_why():
    # Only the passed Wednesday slot met Friday; the Thursday slot sells on Saturday.
    case = reconciled(calendar(milan(FRI, 10)))
    assert case.decision_due_at is None
    assert "No remaining calendar slot delivers sellable stock by required_by." in (
        case.blocking_uncertainties
    )


# Clause 2: no future costs or delays in a past replay


def test_calendar_published_after_as_of_is_not_read():
    future = calendar(milan(SAT, 10), available_at=AS_OF + timedelta(minutes=1))
    case = reconciled(future)
    assert case.decision_due_at is None
    assert any("Decision deadline not estimable" in u for u in case.blocking_uncertainties)
    assert future.source_refs[0] not in case.source_refs


def test_lane_cost_reviewed_after_as_of_is_not_read():
    # The lane was repriced on Oct 20: the Oct 14 replay must not see the new cost.
    client = lane_server(last_reviewed="2026-10-20", cost_fixed_eur=999.0)
    got = reader_at(AS_OF, client).lane_and_eta("MIL02", "MIL01", AS_OF)
    assert isinstance(got, Unknown) and got.reason == "lane_reviewed_after_as_of"
    # A later replay, after the review, does read it.
    later = reader_at(datetime(2026, 10, 21, 18, tzinfo=UTC), client)
    got = later.lane_and_eta("MIL02", "MIL01", later.as_of)
    assert isinstance(got, LaneEta) and got.lane.cost_fixed_eur == 999.0


def test_observed_delays_are_not_read():
    # Observed P50/P90 cover the whole dataset period, so they are not knowable at as_of.
    plain = reader_at(AS_OF, lane_server()).lane_and_eta("MIL02", "MIL01", AS_OF)
    observed = reader_at(
        AS_OF, lane_server(observed_p50_days=6, observed_p90_days=9, observed_n=40)
    ).lane_and_eta("MIL02", "MIL01", AS_OF)
    assert isinstance(plain, LaneEta) and isinstance(observed, LaneEta)
    assert observed.eta == plain.eta and observed.lane == plain.lane


def past_run(engine, sources_dir, run_id: str, client: SystemsClient) -> list[ActionOption]:
    """The Oct 14 run, replayed from scratch with its own run id."""
    spec = RunSpec(
        run_id=run_id,
        scenario_id="historical",
        as_of=AS_OF,
        stores=("MIL01", "MIL02"),
        source_manifest_hash="sha256:test",
        config_hash="sha256:test",
        code_version="test",
        mode="live",
        modules=(),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )
    create_run(engine, spec)
    erp.load_window(engine, spec, {}, sources_dir=sources_dir)
    repo = Repo(engine, spec)
    baseline.write_baselines(repo, 7)
    repo.put(fixture_case(run_id=run_id))
    result = options.build_options(
        repo, SystemsReader(repo, client), options.load_policy(REPO_ROOT / "config"), 7
    )
    assert result.status == "succeeded", result
    return sorted(repo.list(ActionOption), key=lambda o: o.kind)


def first_spec(engine, run_id: str) -> RunSpec:
    return Repo.open(engine, run_id).spec


def comparable(opts: list[ActionOption]) -> list[dict]:
    return [o.model_dump(mode="json", exclude={"run_id"}) for o in opts]


def test_past_replay_is_unchanged_by_data_published_later(tmp_path, sources):  # noqa: F811
    engine = connect(f"sqlite:///{tmp_path / 'gate8.db'}")
    first = past_run(engine, sources, "run-1014-a", lane_server())
    assert recommended(first) == ["transfer"]

    # A later run (Fri 16) loads what was published after Oct 14: stock of Wed 14 and Thu 15
    # where the destination is now full, and a new forecast run that triples demand.
    erp_dir = sources / "erp"
    for day in (WED, THU):
        write(
            erp_dir / "inventory" / "store_stock_daily" / f"stock_eod_{day}.csv",
            STOCK,
            [(str(day), "MIL01", SKU, s, 9, 0) for s in SIZES]
            + [(str(day), "MIL02", SKU, s, 0, 0) for s in SIZES],
        )
    write(
        erp_dir / "forecast" / "sku_store_weekly" / "fcst_sku_store_run_2026-10-15.csv",
        FORECAST,
        [
            ("2026-10-15", date.fromisoformat(ws).strftime("%G-W%V"), ws, store, SKU, "42")
            for store in ("MIL01", "MIL02")
            for ws in ("2026-10-19", "2026-10-26")
        ],
    )
    later = RunSpec.model_validate(
        first_spec(engine, "run-1014-a").model_dump()
        | {"run_id": "run-1016", "as_of": datetime(2026, 10, 16, 18, tzinfo=UTC)}
    )
    create_run(engine, later)
    counts = erp.load_window(engine, later, {}, sources_dir=sources)
    assert counts["stock_new"] > 0 and counts["forecast_new"] > 0  # the future is in the store
    later_repo = Repo(engine, later)
    assert any(r.data["on_hand"] == 9 for r in later_repo.erp("stock", store_id="MIL01"))

    # Replaying Oct 14 again, with observed lane delays now published, gives the same options.
    delayed = lane_server(observed_p50_days=6, observed_p90_days=9, observed_n=40)
    again = past_run(engine, sources, "run-1014-b", delayed)
    assert comparable(again) == comparable(first)
    assert {o.input_version_hash for o in again} == {o.input_version_hash for o in first}
    past = Repo(engine, first_spec(engine, "run-1014-b"))
    assert all(r.data["snapshot_date"] < WED for r in past.erp("stock", store_id="MIL01"))
    assert DEST_STOCK["1"] == 0  # the destination is still short of size 1 on Oct 14

    # A lane repriced after Oct 14 is not read: the replay abstains instead of using the new cost.
    repriced = lane_server(last_reviewed="2026-10-15", cost_fixed_eur=999.0)
    blind = past_run(engine, sources, "run-1014-c", repriced)
    assert "transfer" not in {o.kind for o in blind}
    assert not any(leg.cost_eur for o in blind for leg in o.legs)
    notify = {o.kind: o for o in blind}["notify_owner"]
    assert notify.recommended and "lane_reviewed_after_as_of" in notify.rationale
