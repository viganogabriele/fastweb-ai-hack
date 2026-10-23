"""EVL-04 on synthetic sources and events only: CI never opens the real answer key."""

import json
import tempfile
import unittest
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

from eval.baselines import Alert, certified, sales_alerts, stock_alerts
from eval.lead_time import (
    breadth,
    calibrate,
    case_alerts,
    chance_check,
    email_group,
    event_units,
    lead_time_report,
    matches,
    noise,
    placebo_units,
    score,
)

ERP = "generated/sources/erp"
SKU = "STYLEA-999"


def event(**overrides):
    base = {
        "id": "E1",
        "type": "demand_color_unmet",
        "stores": ["MIL01"],
        "start": "2026-10-05",
        "end": "2026-10-10",
        "demand_mult": 2.0,
        "filter": {"styles": ["ALPHA"], "colors": ["999"]},
    }
    return base | overrides


class LeadTimeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        master = self.root / ERP / "master_data"
        master.mkdir(parents=True)
        (master / "stores.csv").write_text(
            "store_id,timezone\nMIL01,Europe/Rome\nTYO01,Asia/Tokyo\n"
        )
        (master / "sku_colour.csv").write_text(
            "sku,style_code,style_name,color_code,line,category,season,season_group\n"
            f"{SKU},STYLEA,ALPHA,999,Collection,Outerwear,CO,HEAVY\n"
            "STYLEA-742,STYLEA,ALPHA,742,Collection,Outerwear,CO,HEAVY\n"
            "STYLEB-999,STYLEB,BETA,999,Collection,Knitwear,CO,LIGHT\n"
        )

    def write_stock(self, day: str, rows: list[tuple[str, str, int]]):
        folder = self.root / ERP / "inventory/store_stock_daily"
        folder.mkdir(parents=True, exist_ok=True)
        lines = ["snapshot_date,store_id,sku,size,on_hand,in_transit"]
        lines += [f"{day},MIL01,{sku},{size},{qty},0" for sku, size, qty in rows]
        (folder / f"stock_eod_{day}.csv").write_text("\n".join(lines) + "\n")

    def write_sales(self, units: dict[str, int]):
        folder = self.root / ERP / "sales/daily_store_sku"
        folder.mkdir(parents=True, exist_ok=True)
        lines = ["business_date,store_id,sku,units_sold"]
        lines += [f"{day},MIL01,{SKU},{qty}" for day, qty in units.items()]
        by_month = {}
        for line in lines[1:]:
            by_month.setdefault(line[:7].replace("-", "_"), []).append(line)
        for month, rows in by_month.items():
            (folder / f"sales_daily_{month}.csv").write_text("\n".join([lines[0], *rows]) + "\n")

    def unit(self, **overrides):
        stores = frozenset({"MIL01"})
        return event_units(
            [event(**overrides)], stores, date(2026, 9, 1), date(2026, 10, 21), self.root
        )[0]

    def test_certified_is_next_evening_local(self):
        self.assertEqual(
            certified(self.root, "MIL01", date(2026, 10, 8)),
            datetime(2026, 10, 9, 18, tzinfo=UTC),
        )
        self.assertEqual(
            certified(self.root, "TYO01", date(2026, 10, 8)),
            datetime(2026, 10, 9, 11, tzinfo=UTC),
        )

    def test_stock_alert_on_crossing_only_and_rearms_after_restock(self):
        self.write_stock("2026-10-04", [(SKU, "1", 2), (SKU, "2", 0)])
        self.write_stock("2026-10-05", [(SKU, "1", 0), (SKU, "2", 0)])
        self.write_stock("2026-10-06", [(SKU, "1", 0), (SKU, "2", 0)])
        self.write_stock("2026-10-07", [(SKU, "1", 3), (SKU, "2", 0)])
        self.write_stock("2026-10-08", [(SKU, "1", 0), (SKU, "2", 0)])
        alerts = stock_alerts(self.root, frozenset({"MIL01"}), date(2026, 10, 5), date(2026, 10, 8))
        self.assertEqual(
            [(a.at, a.sizes) for a in alerts],
            [
                (certified(self.root, "MIL01", date(2026, 10, 5)), frozenset({"1"})),
                (certified(self.root, "MIL01", date(2026, 10, 8)), frozenset({"1"})),
            ],
        )

    def test_sales_detector_has_no_look_ahead(self):
        quiet = {f"2026-09-{d:02d}": 1 for d in range(1, 31)}
        self.write_sales(quiet | {"2026-10-01": 12, "2026-10-02": 6})
        stores = frozenset({"MIL01"})
        before = sales_alerts(self.root, stores, date(2026, 10, 1), date(2026, 10, 3))
        self.write_sales(quiet | {"2026-10-01": 12, "2026-10-02": 6, "2026-10-03": 40})
        after = sales_alerts(self.root, stores, date(2026, 10, 1), date(2026, 10, 3))
        sku_alerts = [a for a in before if a.scope_level == "sku"]
        self.assertEqual(sku_alerts[0].at, certified(self.root, "MIL01", date(2026, 10, 1)))
        self.assertEqual(sku_alerts[0].direction, "up")
        # A later day's sales cannot change alerts computed for earlier days.
        cutoff = certified(self.root, "MIL01", date(2026, 10, 2))
        self.assertEqual(
            [a for a in before if a.at <= cutoff], [a for a in after if a.at <= cutoff]
        )

    def test_matching_scope_direction_and_window(self):
        unit = self.unit(filter={"styles": ["ALPHA"], "sizes": ["1"]})
        at = datetime(2026, 10, 6, 18, tzinfo=UTC)
        alert = Alert(
            "stock", "MIL01", at, "sku_size", frozenset({SKU}), frozenset({"1"}), "stockout"
        )
        self.assertTrue(matches(alert, unit))
        self.assertFalse(
            matches(Alert("x", "MIL01", at, "sku_size", frozenset({SKU}), frozenset({"2"})), unit)
        )
        self.assertFalse(matches(Alert("x", "MIL01", at, "sku", frozenset({"STYLEB-999"})), unit))
        self.assertFalse(
            matches(Alert("x", "MIL01", at, "sku", frozenset({SKU}), direction="down"), unit)
        )
        late = datetime(2026, 10, 12, 0, tzinfo=UTC)
        self.assertFalse(matches(Alert("x", "MIL01", late, "sku", frozenset({SKU})), unit))
        store_wide = self.unit(filter={}, demand_mult=0.5)
        self.assertFalse(matches(Alert("x", "MIL01", at, "sku", frozenset({SKU})), store_wide))
        self.assertTrue(matches(Alert("x", "MIL01", at, "store", direction="down"), store_wide))
        self.assertFalse(
            matches(Alert("x", "MIL01", at, "store", direction="stockout"), store_wide)
        )

    def test_lead_lower_bound_and_not_detected(self):
        units = [self.unit(), self.unit(id="E2", filter={"styles": ["BETA"]})]
        pipe = Alert(
            "pipeline",
            "MIL01",
            datetime(2026, 10, 5, 19, tzinfo=UTC),
            "sku",
            frozenset({SKU}),
            decision_due_at=datetime(2026, 10, 5, 19, tzinfo=UTC),
        )
        stock = Alert(
            "stock", "MIL01", datetime(2026, 10, 7, 7, tzinfo=UTC), "sku", frozenset({SKU})
        )
        stray = Alert(
            "stock",
            "MIL01",
            datetime(2026, 10, 7, 7, tzinfo=UTC),
            "sku",
            frozenset({"STYLEA-742"}),
            direction="down",
        )
        result = score({"pipeline": [pipe], "stock": [stock, stray], "sales": []}, units, 10)
        summary = result["summary"]
        self.assertEqual(result["units"][0]["lead_vs_stock_days"], 1.5)
        self.assertEqual(summary["lead_vs_stock"]["both_detected_days"]["median"], 1.5)
        bound = result["units"][0]["lead_vs_sales_lower_bound_days"]
        self.assertEqual(bound, round((units[0].t_end - pipe.at).total_seconds() / 86400, 2))
        self.assertEqual(summary["pipeline"]["not_detected_by_t_end"], 1)
        self.assertEqual(summary["decision_margin_days"]["n"], 1)
        self.assertEqual(summary["decision_margin_days"]["median"], 0)
        self.assertEqual(summary["stock"]["false_alerts"], 1)
        self.assertEqual(summary["stock"]["false_alerts_per_store_day"], 0.1)

    def test_calibration_chooses_sensitivity_order_not_event_outcomes(self):
        unit = self.unit()
        matching = Alert("stock", "MIL01", unit.start, "sku", frozenset({SKU}))
        result = calibrate(
            {"threshold=0": [matching], "threshold=2": []},
            pipeline_false_alerts=0,
            units=[unit],
            store_days=1,
            sensitivity_order=("threshold=2", "threshold=0"),
        )
        self.assertEqual(result["chosen"], "threshold=2")
        stray = Alert("sales", "MIL01", unit.start, "sku", frozenset({"OTHER-999"}))
        strict = calibrate(
            {"z=2": [stray], "z=6": [stray]},
            pipeline_false_alerts=0,
            units=[unit],
            store_days=1,
            sensitivity_order=("z=2", "z=6"),
        )
        self.assertEqual(strict["chosen"], "z=6")

    def test_cases_scope_verify_and_noise(self):
        case = {
            "id": "case-1",
            "case_type": "unmet_demand",
            "status": "open",
            "store_id": "MIL01",
            "scope_level": "sku_size",
            "scope_id": f"{SKU}-1",
            "first_available_at": "2026-10-05T21:00:00+02:00",
            "decision_due_at": None,
            "n_documents": 2,
            "n_origin_groups": 1,
            "source_refs": [
                {"uri": "dataset://store_emails/MIL01/20261005_2100_MIL01.eml"},
                {"uri": "dataset://store_emails/MIL01/20261005_2101_MIL01_dup.eml"},
                {"uri": "dataset://erp/master_data/sku_colour.csv"},
            ],
        }
        unknown = case | {"id": "case-2", "scope_level": "unknown", "scope_id": None}
        profile = case | {"id": "case-3", "case_type": "customer_profile", "scope_level": "store"}
        records = [{"kind": "Case", "payload": case}, unknown, profile]
        alerts, others = case_alerts(records, self.root)
        self.assertEqual(
            others,
            [
                {"case": "case-2", "status": "open", "as": "verify"},
                {"case": "case-3", "status": "open", "as": "context"},
            ],
        )
        (alert,) = alerts
        self.assertEqual(
            (alert.skus, alert.sizes, alert.direction),
            (frozenset({SKU}), frozenset({"1"}), "stockout"),
        )
        self.assertEqual(alert.at, datetime(2026, 10, 5, 19, tzinfo=UTC))
        out_of_window_alerts, out_of_window = case_alerts(
            [case, unknown, profile], self.root, date(2026, 10, 6), date(2026, 10, 21)
        )
        self.assertEqual(out_of_window_alerts, [])
        self.assertEqual(out_of_window, [])
        self.assertEqual(email_group("store_emails/MIL01/x_MIL01_corr.eml", {}), "correction")
        kinds = {"store_emails/MIL01/20261005_2100_MIL01.eml": "misdirected"}
        result = noise(alerts, [self.unit()], kinds, [case])
        self.assertEqual(
            result["cases_citing_group"], {"duplicate": {"matched": 1}, "noise": {"matched": 1}}
        )
        self.assertEqual(result["copies_folded_cases"], 1)

    def test_placebo_windows_avoid_the_event_and_expose_chance_matches(self):
        unit = self.unit(start="2026-09-20", end="2026-09-25")
        fakes = placebo_units([unit], date(2026, 9, 1), date(2026, 10, 21), self.root)
        self.assertEqual(len(fakes), 3)  # -21 days would start before the period
        self.assertTrue(all(f.t_end < unit.start or f.start > unit.t_end for f in fakes))
        always = [
            Alert("pipeline", "MIL01", datetime(2026, 9, 1, 12, tzinfo=UTC) + timedelta(days=d),
                  "sku", frozenset({SKU}))
            for d in range(52)
        ]  # fmt: skip
        result = chance_check({"pipeline": always}, [unit], fakes)
        method = result["specific"]["pipeline"]
        self.assertEqual(method["real"], [1, 1])
        self.assertEqual(method["placebo"], [3, 3])
        self.assertEqual(method["paired"]["real"], [1, 1])
        self.assertEqual(method["paired"]["placebo_rate"], 1.0)

    def test_breadth_boundary_and_store_scope(self):
        unit = self.unit()
        self.assertEqual(breadth(replace(unit, skus=frozenset(map(str, range(10))))), "specific")
        self.assertEqual(breadth(replace(unit, skus=frozenset(map(str, range(11))))), "broad")
        self.assertEqual(breadth(replace(unit, store_wide=True)), "store_wide")

    def test_chance_pairs_units_and_weights_each_unit_equally(self):
        units = [self.unit(id=f"E{i}") for i in range(3)]
        units[1] = replace(units[1], skus=frozenset({"NO-HIT"}))
        # E0 has three successful controls; E1 has one failed control; E2 has none.
        controls = [
            replace(
                units[0],
                start=units[0].start + timedelta(days=d),
                t_end=units[0].t_end + timedelta(days=d),
            )
            for d in (-21, -14, 14)
        ]
        controls.append(replace(controls[0], event_id="E1", skus=frozenset({"NO-HIT"})))
        alerts = [Alert("pipeline", "MIL01", u.start, "sku", u.skus) for u in controls[:3]]
        alerts.append(Alert("pipeline", "MIL01", units[0].start, "sku", frozenset({SKU})))
        result = chance_check({"pipeline": alerts}, units, controls)["specific"]["pipeline"]
        self.assertEqual(result["real"], [2, 3])
        self.assertEqual(result["placebo"], [3, 4])
        self.assertEqual(result["paired"]["real"], [1, 2])
        self.assertEqual(result["paired"]["placebo_rate"], 0.5)  # pooled would be 0.75
        self.assertEqual(result["excluded_no_placebo"], [{"event_id": "E2", "store_id": "MIL01"}])
        self.assertEqual([r["placebo"] for r in result["paired"]["units"]], [[3, 3], [0, 1]])

    def test_no_candidate_windows_and_empty_groups_are_explicit(self):
        # Too short a scoring period, and a long event overlapping every proposed shift.
        for unit, start, end in (
            (self.unit(), date(2026, 10, 1), date(2026, 10, 12)),
            (self.unit(start="2026-09-01", end="2026-10-20"), date(2026, 8, 1), date(2026, 12, 1)),
        ):
            with self.subTest(start=start, end=end):
                controls = placebo_units([unit], start, end, self.root)
                self.assertEqual(controls, [])
                result = chance_check({"stock": []}, [unit], controls)["specific"]["stock"]
                self.assertEqual(
                    result["paired"], {"real": [0, 0], "placebo_rate": None, "units": []}
                )
                self.assertEqual(len(result["excluded_no_placebo"]), 1)
        empty = chance_check({"sales": []}, [], [])
        for group in ("store_wide", "broad", "specific"):
            self.assertIsNone(empty[group]["sales"]["paired"]["placebo_rate"])
            self.assertEqual(empty[group]["sales"]["excluded_no_placebo"], [])

    def test_controls_exclude_other_same_store_events_even_for_different_products(self):
        unit = self.unit(start="2026-09-20", end="2026-09-25")
        other = self.unit(
            id="E2", start="2026-10-04", end="2026-10-10", filter={"styles": ["BETA"]}
        )
        start, end = date(2026, 9, 1), date(2026, 10, 21)
        own = [u for u in placebo_units([unit, other], start, end, self.root) if u.event_id == "E1"]
        self.assertEqual(len(own), 1)  # +14 and +21 touch E2, -21 is outside
        self.assertLess(own[0].t_end, unit.start)
        # Another store does not contaminate this store's control windows.
        elsewhere = replace(other, store_id="TYO01")
        own = [
            u for u in placebo_units([unit, elsewhere], start, end, self.root) if u.event_id == "E1"
        ]
        self.assertEqual(len(own), 3)

    def test_control_cannot_use_extra_erp_grace_day(self):
        unit = self.unit(start="2026-09-01", end="2026-09-05")
        # The +14 control ends on Sep 20; the requested period ends on Sep 19.
        controls = placebo_units([unit], date(2026, 9, 1), date(2026, 9, 19), self.root)
        self.assertEqual(controls, [])

    def test_report_controls_exclude_unscored_events_observed_in_period(self):
        # Aug 31 is not a scored event, but its ERP observation window lasts through
        # Sep 1. E1's -14 control (Sep 1-4) must not count an alert in that window.
        oracle = self.root / "generated/ground_truth/scenario"
        oracle.mkdir(parents=True)
        current = event(start="2026-09-15", end="2026-09-17")
        previous = event(
            id="PREVIOUS", start="2026-08-31", end="2026-08-31", filter={"styles": ["BETA"]}
        )
        alert = Alert(
            "stock", "MIL01", datetime(2026, 9, 1, 18, tzinfo=UTC), "sku", frozenset({SKU})
        )
        for blocker, end, controls, hits in (
            (None, date(2026, 10, 21), 3, 1),
            (previous, date(2026, 10, 21), 2, 0),
            (previous | {"stores": ["ALL"]}, date(2026, 10, 21), 2, 0),
            (previous | {"stores": ["TYO01"]}, date(2026, 10, 21), 3, 1),
            (
                previous | {"end": "2026-08-30", "start": "2026-08-30"},
                date(2026, 10, 21),
                3,
                1,
            ),
            (previous, date(2026, 9, 18), 0, 0),
        ):
            with self.subTest(blocker=blocker, end=end):
                (oracle / "events.json").write_text(
                    json.dumps({"events": [current, blocker] if blocker else [current]})
                )
                with (
                    patch(
                        "eval.lead_time.split_stores", return_value={"dev": frozenset({"MIL01"})}
                    ),
                    patch("eval.lead_time.stock_alerts", return_value=[alert]),
                ):
                    report = lead_time_report(self.root, None, "dev", date(2026, 9, 1), end)
                self.assertEqual(report["summary"]["n_units"], 1)
                self.assertEqual(report["excluded_events"], ["PREVIOUS"] if blocker else [])
                result = report["chance_check"]["specific"]["stock"]
                self.assertEqual(result["real"], [0, 1])
                self.assertEqual(result["placebo"], [hits, controls])
                if controls:
                    self.assertEqual(result["paired"]["units"][0]["placebo"], [hits, controls])
                else:
                    self.assertEqual(
                        result["paired"], {"real": [0, 0], "placebo_rate": None, "units": []}
                    )
                    self.assertEqual(
                        result["excluded_no_placebo"], [{"event_id": "E1", "store_id": "MIL01"}]
                    )

    def test_shift_preserves_local_midnight_and_end_across_dst(self):
        unit = self.unit(start="2026-10-10", end="2026-10-12")
        controls = placebo_units([unit], date(2026, 9, 1), date(2026, 11, 10), self.root)
        moved = next(u for u in controls if u.start.astimezone(ZoneInfo("Europe/Rome")).day == 31)
        self.assertEqual(moved.start, datetime(2026, 10, 30, 23, tzinfo=UTC))
        self.assertEqual(moved.t_end, datetime(2026, 11, 3, 22, 59, 59, tzinfo=UTC))
        self.assertEqual(moved.skus, unit.skus)
        self.assertEqual(moved.sizes, unit.sizes)
        self.assertEqual(moved.direction, unit.direction)

    def test_report_chance_caps_real_windows_without_changing_main_score(self):
        # Synthetic oracle only: no real answer keys are opened by this test.
        oracle = self.root / "generated/ground_truth/scenario"
        oracle.mkdir(parents=True)
        (oracle / "events.json").write_text(
            json.dumps({"events": [event(start="2026-10-21", end="2026-10-21")]})
        )
        self.write_stock("2026-10-20", [(SKU, "1", 2)])
        self.write_stock("2026-10-21", [(SKU, "1", 0)])
        with patch("eval.lead_time.split_stores", return_value={"dev": frozenset({"MIL01"})}):
            report = lead_time_report(
                self.root, None, "dev", date(2026, 10, 20), date(2026, 10, 21)
            )
        self.assertEqual(report["summary"]["stock"]["units_detected"], 1)  # next evening
        self.assertEqual(report["chance_check"]["specific"]["stock"]["real"], [0, 1])
        self.assertEqual(report["units"][0]["breadth"], "specific")


if __name__ == "__main__":
    unittest.main()
