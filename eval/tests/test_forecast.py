"""EVL-03 regressions use only temporary synthetic demand, never the real oracle."""

import copy
import csv
import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

from eval.forecast import KEY, score_forecasts
from eval.harness import ARTIFACTS, FrozenRun, freeze

ORIGIN = "2026-10-08T20:00:00+02:00"
START = date(2026, 10, 9)


def record(sku="A", producer="fc.baseline", status="unchanged"):
    return {
        "as_of": ORIGIN,
        "payload": {
            "producer": producer,
            "store_id": "MIL01",
            "sku": sku,
            "scenario_id": "historical",
            "available_at": ORIGIN,
            "status": status,
            "baseline_ref": {"id": "vintage"},
            "series": [
                {
                    "date": (START + timedelta(days=i)).isoformat(),
                    "baseline": 2,
                    "latent": {"low": 0, "base": 3, "high": 9},
                }
                for i in range(7)
            ],
        },
    }


class ForecastTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = self.root / "generated/sources/synthetic.csv"
        source.parent.mkdir(parents=True)
        source.write_text("synthetic source\n")
        config = self.root / "config/synthetic.json"
        config.parent.mkdir()
        config.write_text("{}")
        self.source, self.config = source, config
        self.oracle = self.root / "generated/ground_truth"
        (self.oracle / KEY).parent.mkdir(parents=True)
        self.protocol = {
            "run_id": "synthetic",
            "split": "dev",
            "stores": ["MIL01"],
            "origins": [ORIGIN],
            "universe": [
                {"store_id": "MIL01", "sku": sku, "timezone": "Europe/Rome"}
                for sku in ("A", "DECOY")
            ],
            "sampling_criterion": "All two preselected synthetic products, including no alerts",
            "models": {"extract": "fake"},
            "parameters": {"frozen": True},
            "forecast": {"scenario": "base", "scenario_id": "historical"},
        }
        self.records = [record(), record(producer="fc.overlay", status="computed"), record("DECOY")]
        self.actual = [
            [(START + timedelta(days=i)).isoformat(), "MIL01", sku, 4 if sku == "A" else 2]
            for sku in ("A", "DECOY")
            for i in range(7)
        ]
        self.bundle_number = 0

    def frozen(self):
        self.bundle_number += 1
        artifacts = {}
        for kind in ARTIFACTS:
            path = self.root / "data" / f"{kind}.json"
            path.parent.mkdir(exist_ok=True)
            path.write_text(json.dumps(self.records if kind == "predictions" else []))
            artifacts[kind] = path
        bundle = self.root / "data" / f"frozen-{self.bundle_number}"
        checksum = freeze(
            bundle, self.protocol, artifacts, [self.source], [self.config], root=self.root
        )
        return FrozenRun(bundle, checksum)

    def score(self, run=None):
        with (self.oracle / KEY).open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["date", "store_id", "sku", "demand_units"])
            writer.writerows(self.actual)
        return score_forecasts(run or self.frozen(), self.oracle)

    def test_same_universe_and_daily_errors_for_all_horizons(self):
        report = self.score()
        self.assertEqual(report["scenario"], "base")
        for horizon in (1, 3, 7):
            result = report["horizons"][str(horizon)]
            self.assertEqual(result["scored_origins"], 2)
            self.assertEqual(result["no_alert_origins"], 1)
            self.assertEqual(result["baseline"]["n_days"], 2 * horizon)
            self.assertEqual(result["baseline"]["actual_units"], 6 * horizon)
            self.assertAlmostEqual(result["baseline"]["wape"], 1 / 3)
            self.assertEqual(result["baseline"]["mae"], 1)
            self.assertAlmostEqual(result["selected"]["wape"], 1 / 6)
            self.assertEqual(result["selected"]["mae"], 0.5)
            self.assertEqual(result["adjustment_coverage"], 0.5)
        self.assertEqual(len(report["answer_key"]["sha256"]), 64)

    def test_abstentions_use_baseline_and_remain_in_comparison(self):
        for status in ("unchanged", "not_estimable"):
            with self.subTest(status=status):
                self.records[1]["payload"]["status"] = status
                result = self.score()["horizons"]["7"]
                self.assertEqual(result["selected"], result["baseline"])
                self.assertEqual(result["abstained_origins"], 1)
                self.assertEqual(result["adjustment_coverage"], 0)

    def test_wape_is_volume_weighted_and_daily_errors_do_not_cancel(self):
        self.actual[7][3] = 1  # Decoy's first day; weighting differs from mean of percentages.
        result = self.score()["horizons"]["1"]
        self.assertAlmostEqual(result["baseline"]["wape"], 3 / 5)
        self.assertAlmostEqual(result["selected"]["wape"], 2 / 5)
        self.actual[7][3] = 2
        self.actual[1][3] = 0
        self.actual[2][3] = 2
        result = self.score()["horizons"]["3"]
        self.assertEqual(result["selected"]["absolute_error_units"], 5)
        self.assertAlmostEqual(result["selected"]["wape"], 5 / 12)
        self.assertAlmostEqual(result["selected"]["mae"], 5 / 6)

    def test_multiple_preselected_origins_keep_final_horizons_pending(self):
        later = "2026-10-14T20:00:00+02:00"
        self.protocol["origins"].append(later)
        additions = copy.deepcopy(self.records)
        for row in additions:
            row["as_of"] = later
        self.records.extend(additions)
        result = self.score()["horizons"]
        self.assertEqual(result["1"]["eligible_origins"], 4)
        self.assertEqual(result["1"]["scored_origins"], 4)
        for horizon in ("3", "7"):
            self.assertEqual(result[horizon]["pending_origins"], 2)
            self.assertEqual(result[horizon]["scored_origins"], 2)

    def test_incomplete_final_horizons_are_pending(self):
        self.actual = [row for row in self.actual if row[0] <= "2026-10-11"]
        result = self.score()["horizons"]
        self.assertEqual(result["1"]["scored_origins"], 2)
        self.assertEqual(result["3"]["scored_origins"], 2)
        self.assertEqual(result["7"]["pending_origins"], 2)
        self.assertEqual(result["7"]["baseline"]["n_days"], 0)
        self.assertIsNone(result["7"]["selected"]["mae"])

    def test_missing_interior_target_or_blank_is_not_zero(self):
        for missing in (None, ""):
            with self.subTest(missing=missing):
                self.actual = [row for row in self.actual if row[0] != "2026-10-10"]
                if missing == "":
                    self.actual.append(["2026-10-10", "MIL01", "A", ""])
                result = self.score()["horizons"]["3"]
                self.assertEqual(result["pending_origins"], 2)
                self.assertEqual(result["scored_origins"], 0)

    def test_zero_volume_has_undefined_wape_but_mae_and_counts(self):
        for row in self.actual:
            row[3] = 0
        result = self.score()["horizons"]["1"]
        self.assertIsNone(result["baseline"]["wape"])
        self.assertEqual(result["baseline"]["mae"], 2)
        self.assertEqual(result["baseline"]["actual_units"], 0)
        self.assertEqual(result["baseline"]["n_days"], 2)

    def test_missing_baseline_and_partial_overlay_report_exclusions(self):
        self.records = self.records[:2]  # Missing decoy baseline stays in eligible universe.
        self.records[1]["payload"]["series"] = self.records[1]["payload"]["series"][:1]
        result = self.score()["horizons"]
        self.assertEqual(result["1"]["scored_origins"], 1)
        self.assertEqual(result["1"]["prediction_coverage"], 0.5)
        self.assertEqual(result["3"]["eligible_origins"], 2)
        self.assertEqual(result["3"]["unscorable_origins"], 2)
        self.assertEqual(
            {item["reason"] for item in result["3"]["details"]},
            {"missing_baseline", "incomplete_overlay"},
        )

    def test_scenario_choice_is_frozen_not_best_matching(self):
        self.protocol["forecast"]["scenario"] = "high"
        result = self.score()["horizons"]["1"]
        self.assertEqual(result["selected"]["mae"], 2.5)
        self.assertGreater(result["selected"]["mae"], result["baseline"]["mae"])

    def test_timezone_controls_next_day_and_utc_equivalent_origins_match(self):
        self.protocol["origins"] = ["2026-10-08T23:30:00Z"]
        for row in self.records:
            row["as_of"] = "2026-10-09T01:30:00+02:00"
        self.actual = [row for row in self.actual if row[0] != "2026-10-09"]
        result = self.score()["horizons"]["1"]
        self.assertEqual(result["scored_origins"], 2)  # Next local day is October 10.

    def test_reject_ambiguous_overlays_duplicates_and_future_input_before_oracle(self):
        original = copy.deepcopy(self.records)
        variants = [
            original + [copy.deepcopy(original[0])],
            original + [copy.deepcopy(original[1])],
        ]
        future = copy.deepcopy(original)
        future[0]["payload"]["available_at"] = "2026-10-10T00:00:00Z"
        variants.append(future)
        extension = copy.deepcopy(original)
        extension[0]["payload"]["scenario_id"] = "synthetic_extension"
        variants.append(extension)
        for records in variants:
            with self.subTest(records=records):
                self.records = records
                run = self.frozen()
                with patch.object(
                    run, "read_answer_key", side_effect=AssertionError("oracle read")
                ):
                    with self.assertRaises(ValueError):
                        score_forecasts(run, self.oracle)

    def test_frozen_choices_are_required_before_oracle_access(self):
        del self.protocol["forecast"]
        run = self.frozen()
        with patch.object(run, "read_answer_key", side_effect=AssertionError("oracle read")):
            with self.assertRaisesRegex(ValueError, "scenario"):
                score_forecasts(run, self.oracle)

    def test_duplicate_universe_origins_or_missing_timezone_fail_before_oracle(self):
        original = copy.deepcopy(self.protocol)
        for change in ("universe", "origins", "timezone"):
            self.protocol = copy.deepcopy(original)
            if change == "timezone":
                del self.protocol["universe"][0]["timezone"]
            else:
                self.protocol[change].append(copy.deepcopy(self.protocol[change][0]))
            run = self.frozen()
            with patch.object(run, "read_answer_key", side_effect=AssertionError("oracle read")):
                with self.subTest(change=change), self.assertRaises(ValueError):
                    score_forecasts(run, self.oracle)

    def test_invalid_values_and_duplicate_targets_are_rejected(self):
        original = copy.deepcopy(self.actual)
        for value in ("nan", "inf", -1):
            self.actual = copy.deepcopy(original)
            self.actual[0][3] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.score()
        self.actual = original + [original[0]]
        with self.assertRaisesRegex(ValueError, "Duplicate daily"):
            self.score()

    def test_mismatched_overlay_baseline_is_rejected(self):
        self.records[1]["payload"]["series"][0]["baseline"] = 100
        with self.assertRaisesRegex(ValueError, "baseline disagree"):
            self.score()

    def test_invalid_predictions_fail_before_oracle_even_when_targets_are_pending(self):
        original = copy.deepcopy(self.records)
        variants = []
        for field, value in (("baseline", -1), ("baseline", "nan"), ("latent", "inf")):
            records = copy.deepcopy(original)
            point = records[1]["payload"]["series"][-1]
            if field == "latent":
                point[field]["base"] = value
            else:
                point[field] = value
            variants.append(records)
        mismatch = copy.deepcopy(original)
        mismatch[1]["payload"]["baseline_ref"] = {"id": "other-vintage"}
        variants.append(mismatch)
        mismatch = copy.deepcopy(original)
        mismatch[1]["payload"]["series"][-1]["baseline"] = 100
        variants.append(mismatch)
        missing_refs = copy.deepcopy(original)
        for row in missing_refs[:2]:
            row["payload"]["baseline_ref"] = None
        variants.append(missing_refs)
        for index, records in enumerate(variants):
            with self.subTest(variant=index):
                self.records = records
                run = self.frozen()
                with patch.object(
                    run, "read_answer_key", side_effect=AssertionError("oracle read")
                ):
                    with self.assertRaises(ValueError):
                        score_forecasts(run, self.oracle)

    def test_raw_dto_export_and_unselected_records(self):
        for row in self.records:
            row["payload"]["computed_at"] = row["as_of"]
        self.records = [row["payload"] for row in self.records]
        self.records.append({"producer": "ing.extract"})
        self.records.append(record("OUTSIDE"))
        result = self.score()
        self.assertEqual(result["ignored_prediction_records"], 2)
        self.assertEqual(result["horizons"]["1"]["scored_origins"], 2)

    def test_cli_writes_receipt_exclusively_under_data(self):
        from eval.__main__ import main

        run = self.frozen()
        self.score(run)  # Materialize synthetic oracle.
        output = self.root / "data/result.json"
        argv = [
            "eval",
            "forecast",
            str(run.bundle),
            "--sha256",
            run.manifest_sha256,
            "--output",
            str(output),
        ]
        with (
            patch("eval.__main__.__file__", str(self.root / "eval/__main__.py")),
            patch("sys.argv", argv),
        ):
            main()
            self.assertEqual(json.loads(output.read_text())["horizons"]["1"]["scored_origins"], 2)
            with self.assertRaises(FileExistsError):
                main()
