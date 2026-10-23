"""EVL-05 sample selection and write-once outputs on synthetic names; no real email or label."""

import tempfile
import unittest
from pathlib import Path

from eval import holdout


class SelectionTest(unittest.TestCase):
    def test_selection_is_deterministic_capped_and_seeded(self):
        eligible = {
            "AAA01": [f"AAA01/202609{d:02d}_2100_AAA01.eml" for d in range(1, 30)],
            "BBB01": ["BBB01/20260901_2100_BBB01.eml", "BBB01/20260902_2100_BBB01_dup.eml"],
        }
        first = holdout.select(eligible, per_store=11)
        self.assertEqual(first, holdout.select(dict(reversed(eligible.items())), per_store=11))
        self.assertEqual(len(first["AAA01"]), 11)
        self.assertEqual(first["BBB01"], sorted(eligible["BBB01"]))
        self.assertTrue(set(first["AAA01"]) <= set(eligible["AAA01"]))
        ranked = sorted(eligible["AAA01"], key=holdout.rank)[:11]
        self.assertEqual(first["AAA01"], sorted(ranked))
        self.assertNotEqual(first, holdout.select(eligible, per_store=11, seed="other"))

    def test_header_date_reads_only_headers(self):
        with tempfile.TemporaryDirectory() as tmp:
            mail = Path(tmp) / "x.eml"
            mail.write_bytes(b"Date: Mon, 31 Aug 2026 21:05:00 +0200\n\nDate: not a header\n")
            self.assertEqual(holdout.header_date(mail).isoformat(), "2026-08-31T21:05:00+02:00")
            mail.write_bytes(b"Subject: undated\n\nbody\n")
            self.assertIsNone(holdout.header_date(mail))


class WriteOnceTest(unittest.TestCase):
    def test_outputs_are_exclusive_and_under_data(self):
        with tempfile.TemporaryDirectory(dir=holdout.ROOT / "data") as tmp:
            target = Path(tmp) / "e1" / "reading.json"
            holdout._write_new(target, {"status": "synthetic"})
            with self.assertRaises(FileExistsError):
                holdout._write_new(target, {"status": "again"})
        with self.assertRaises(SystemExit):
            holdout._write_new(holdout.ROOT / "eval" / "outside.json", {})

    def test_forecast_unavailable_record(self):
        with tempfile.TemporaryDirectory(dir=holdout.ROOT / "data") as tmp:
            holdout.forecast_unavailable(["synthetic reason"], Path(tmp))
            text = (Path(tmp) / "forecast-errors.json").read_text(encoding="utf-8")
            self.assertIn('"status": "unavailable"', text)


if __name__ == "__main__":
    unittest.main()
