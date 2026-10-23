"""TST-04, RFC §7.3 gate test 4: ambiguity and unknowns block moves and produce verification.

"Prodotto/taglia ambigui, stock assente e controllo sconosciuto bloccano movimenti e producono
verifica, non scompaiono dalla coda."

Each clause is one blocker on the otherwise admissible ACT-02 case of `test_options` (MAIRE black,
MIL02 → MIL01, recommended transfer). With the blocker in place:

- no movement option is recommended (a transfer, when shown, keeps a mandatory fail/unknown
  check and the contract refuses to mark it recommended);
- exactly one verification option is recommended: `ask_store` for product/size, `verify_stock`
  for stock and stock checks, `notify_owner` for an unknown policy check (the owner verifies it);
- the case keeps its full option set, so it stays in the queue. The case-queue side (`int.cases`
  keeps an ambiguous case as `verify`) is checked once, end to end through `act.options`.
"""

from dataclasses import replace

import httpx
import pytest

from tessera.core.config import REPO_ROOT
from tessera.core.contracts import ActionOption, Case, RunSpec
from tessera.core.db import connect
from tessera.core.repo import Repo, create_run
from tessera.modules.actions import options
from tessera.modules.actions.options import OptionsPolicy, evaluate_options
from tessera.modules.intelligence import baseline
from tessera.modules.sources import erp
from tessera.modules.sources.systems_client import Crosswalk, SystemsClient, SystemsReader, Unknown
from tests.modules.actions.test_options import (
    AS_OF,
    DEST_STOCK,
    DONOR_STOCK,
    POLICY,
    SKU,
    fixture_case,
    forecast,
    inputs,
    lanes,
    position,
    sources,  # noqa: F401  (pytest fixture)
)
from tests.modules.integration import test_cases as case_rules

INFORMATIONAL = {"hold", "verify_stock", "ask_store", "notify_owner"}
MOVEMENTS = {"replenish_dc", "transfer", "combo"}


def assert_blocked(opts, follow_up: str, check: str | None = None, status: str | None = None):
    """No move recommended, one verification recommended, and the case keeps every option."""
    by_kind = {o.kind: o for o in opts}
    assert INFORMATIONAL <= set(by_kind), "the case must not leave the queue"
    assert [o.kind for o in opts if o.recommended] == [follow_up]
    for o in opts:
        if o.kind in MOVEMENTS:
            assert not o.recommended
            blocking = [c for c in o.checks if c.mandatory and c.status in ("fail", "unknown")]
            assert blocking, "a shown move must carry the check that blocks it"
            # The contract itself refuses a recommended move with a blocking check.
            with pytest.raises(ValueError, match="block movement"):
                ActionOption.model_validate(o.model_dump() | {"recommended": True})
    if check is not None:
        transfer = by_kind["transfer"]
        assert {c.name: c.status for c in transfer.checks}[check] == status
        # The verification option names what has to be verified.
        verification = by_kind[follow_up]
        if follow_up != "notify_owner":
            assert check in {c.name for c in verification.checks}
    return by_kind


def test_admissible_reference_case_recommends_the_transfer():
    # Control: without any blocker the same inputs do recommend the move.
    opts = evaluate_options(inputs())
    assert [o.kind for o in opts if o.recommended] == ["transfer"]


# Product / size ambiguity


def test_ambiguous_product_blocks_moves_and_asks_the_store():
    case = fixture_case(scope_level="unknown", scope_id=None, status="verify")
    opts = evaluate_options(replace(inputs(case=case), sku=None, routes=()))
    by_kind = assert_blocked(opts, "ask_store")
    assert "transfer" not in by_kind
    assert "which product (scope unknown)" in by_kind["ask_store"].rationale


def test_ambiguous_style_without_a_carried_colour_asks_the_store():
    case = fixture_case(scope_level="style", scope_id="J20931A00012")
    opts = evaluate_options(replace(inputs(case=case), sku=None, routes=()))
    assert_blocked(opts, "ask_store")


def test_unidentified_size_blocks_moves_and_asks_the_store():
    # The case names a size the master does not have for this colour.
    case = fixture_case(scope_level="sku_size", scope_id=f"{SKU}-7")
    opts = evaluate_options(inputs(case=case, size="7"))
    assert_blocked(opts, "ask_store", "sku_identity", "fail")


def test_size_without_ean_is_unknown_not_identified():
    base = inputs(size="1")
    opts = evaluate_options(replace(base, eans=dict(base.eans) | {"1": None}))
    assert_blocked(opts, "ask_store", "sku_identity", "unknown")


def test_size_demand_unknown_blocks_moves_and_asks_the_store():
    # A SKU-level request names no size; without a verified curve no size can be moved.
    dest = position("MIL01", DEST_STOCK, forecast("MIL01", 2.0), curve=None)
    opts = evaluate_options(inputs(dest=dest))
    by_kind = assert_blocked(opts, "ask_store", "size_curve", "unknown")
    assert by_kind["transfer"].outcomes is None


# Missing stock


def test_missing_donor_stock_record_blocks_moves_and_asks_for_verification():
    donor = position("MIL02", DONOR_STOCK, forecast("MIL02", 1.0))
    donor = replace(donor, stock={s: f for s, f in donor.stock.items() if s != "1"})
    opts = evaluate_options(inputs(donor=donor, size="1"))
    by_kind = assert_blocked(opts, "verify_stock", "donor_stock", "unknown")
    assert "never read as zero" in by_kind["verify_stock"].rationale


def test_unavailable_destination_stock_blocks_moves_and_asks_for_verification():
    dest = position("MIL01", DEST_STOCK, forecast("MIL01", 2.0))
    dest = replace(dest, stock=dict(dest.stock) | {"1": Unknown("unavailable", "ERP down")})
    opts = evaluate_options(inputs(dest=dest))
    by_kind = assert_blocked(opts, "verify_stock", "dest_stock", "unknown")
    assert by_kind["transfer"].outcomes is None and by_kind["hold"].outcomes is None


# Unknown checks


def test_unknown_netting_check_blocks_moves_and_asks_for_verification():
    donor = position("MIL02", DONOR_STOCK, forecast("MIL02", 1.0), netted=None)
    opts = evaluate_options(inputs(donor=donor))
    assert_blocked(opts, "verify_stock", "reservations", "unknown")


def test_units_in_transit_with_unknown_timing_block_moves():
    dest = position("MIL01", DEST_STOCK, forecast("MIL01", 2.0), in_transit=None)
    opts = evaluate_options(inputs(dest=dest))
    assert_blocked(opts, "verify_stock", "dest_inbound", "unknown")


def test_undeclared_policy_is_unknown_and_goes_to_the_owner():
    policy = replace(POLICY, scarce_skus=None)
    opts = evaluate_options(inputs(policy=policy))
    assert_blocked(opts, "notify_owner", "scarcity_policy", "unknown")


def test_every_unknown_policy_entry_blocks_moves():
    # The first blocking check wins: stock_freshness (no age limit) asks to verify the stock.
    opts = evaluate_options(inputs(policy=OptionsPolicy()))
    by_kind = assert_blocked(opts, "verify_stock")
    status = {c.name: c.status for c in by_kind["transfer"].checks}
    for name in ("quantity_policy", "transport_cost", "scarcity_policy", "stock_freshness"):
        assert status[name] == "unknown", name


# End to end: int.cases keeps the ambiguous case, act.options keeps it in the queue


def test_ambiguous_case_stays_in_the_queue_through_cases_and_options(tmp_path, sources):  # noqa: F811
    obs = case_rules.fact("amb", kind="unmet_demand", mention="the black Maire")
    ambiguous = case_rules.link(
        obs[2], "ambiguous", candidates=("J20931A00012-999", "J20931A00012-742")
    )
    built = case_rules.build([obs], [ambiguous])
    (unknown,) = built.cases
    assert (unknown.scope_level, unknown.status) == ("unknown", "verify")

    spec = RunSpec(
        run_id="run-gate4",
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
    engine = connect(f"sqlite:///{tmp_path / 'gate4.db'}")
    create_run(engine, spec)
    erp.load_window(engine, spec, {}, sources_dir=sources)
    repo = Repo(engine, spec)
    baseline.write_baselines(repo, 7)
    unknown = unknown.model_copy(update={"run_id": spec.run_id})
    size_case = fixture_case(
        run_id=spec.run_id,
        id="case-mil01-size-7",
        scope_level="sku_size",
        scope_id=f"{SKU}-7",
    )
    repo.put(unknown, size_case)
    crosswalk = Crosswalk(
        store_plant={"MIL01": "1001", "MIL02": "1002"},
        timezones={"MIL01": "Europe/Rome", "MIL02": "Europe/Rome"},
        sku_matnr={SKU: SKU.replace("-", "")},
        ean_sku_size={},
    )
    client = SystemsClient(crosswalk, transport=httpx.MockTransport(lanes([])))

    result = options.build_options(
        repo, SystemsReader(repo, client), options.load_policy(REPO_ROOT / "config"), 7
    )

    assert result.status == "succeeded", result
    assert result.counts["cases"] == 2 and result.counts["transfers_recommended"] == 0
    assert {c.id for c in repo.list(Case)} == {unknown.id, size_case.id}
    for case_id, follow_up in ((unknown.id, "ask_store"), (size_case.id, "ask_store")):
        stored = repo.list(ActionOption, case_id=case_id)
        assert_blocked(stored, follow_up)
