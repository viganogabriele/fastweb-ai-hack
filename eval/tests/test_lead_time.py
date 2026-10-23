"""EVL-04 on synthetic sources and events only: CI never opens the real answer key."""

import tempfile
import unittest
from datetime import UTC, date, datetime
from pathlib import Path

from eval.baselines import Alert, certified, sales_alerts, stock_alerts
from eval.lead_time import case_alerts, email_group, event_units, matches, noise, score

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
            "pipeline", "MIL01", datetime(2026, 10, 5, 19, tzinfo=UTC), "sku", frozenset({SKU})
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
        self.assertEqual(summary["stock"]["false_alerts"], 1)
        self.assertEqual(summary["stock"]["false_alerts_per_store_day"], 0.1)

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
        self.assertEqual(email_group("store_emails/MIL01/x_MIL01_corr.eml", {}), "correction")
        kinds = {"store_emails/MIL01/20261005_2100_MIL01.eml": "misdirected"}
        result = noise(alerts, [self.unit()], kinds, [case])
        self.assertEqual(
            result["cases_citing_group"], {"duplicate": {"matched": 1}, "noise": {"matched": 1}}
        )
        self.assertEqual(result["copies_folded_cases"], 1)


if __name__ == "__main__":
    unittest.main()
