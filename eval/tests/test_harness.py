"""Synthetic tests only: CI never opens the real answer key or holdout sources."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from eval.harness import ARTIFACTS, FrozenRun, freeze


class FrozenRunTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = self.root / "generated/sources/example.eml"
        source.parent.mkdir(parents=True)
        source.write_text("Synthetic source")
        config = self.root / "config/pipeline.json"
        config.parent.mkdir()
        config.write_text('{"threshold": 0.8}')
        self.oracle = self.root / "generated/ground_truth"
        self.oracle.mkdir()
        (self.oracle / "key.csv").write_text("id,label\nsynthetic,positive\n")
        self.protocol = {
            "run_id": "synthetic-dev",
            "split": "dev",
            "stores": ["MIL01"],
            "origins": ["2026-10-08T20:00:00+02:00"],
            "universe": [{"store_id": "MIL01", "sku": "SYNTHETIC-999"}],
            "sampling_criterion": "Entire preselected synthetic store/day, including no alerts",
            "models": {"extract": "fake-v1"},
            "parameters": {"threshold": 0.8},
        }
        self.artifacts = {}
        for kind in ARTIFACTS:
            path = self.root / "data" / f"{kind}.json"
            path.parent.mkdir(exist_ok=True)
            path.write_text("[]")
            self.artifacts[kind] = path
        self.sources = [source]
        self.configuration = [config]
        self.bundle = self.root / "data/frozen"

    def freeze(self):
        return freeze(
            self.bundle,
            self.protocol,
            self.artifacts,
            self.sources,
            self.configuration,
            root=self.root,
        )

    def test_roundtrip_does_not_depend_on_mutable_product_files(self):
        sha256 = self.freeze()
        self.artifacts["predictions"].write_text('[{"id": "later"}]')
        self.configuration[0].unlink()
        run = FrozenRun(self.bundle, sha256)
        receipt = run.receipt(self.oracle, ["key.csv"])
        self.assertEqual(receipt["counts"], dict.fromkeys(ARTIFACTS, 0))
        self.assertEqual(receipt["metrics"], {})
        self.assertEqual(receipt["status"], "inputs_verified")
        self.assertEqual(receipt["manifest_sha256"], sha256)
        self.assertEqual(len(receipt["answer_keys"][0]["sha256"]), 64)
        with self.assertRaises(FileExistsError):
            # Restore config so the failure specifically concerns bundle reuse.
            self.configuration[0].write_text("{}")
            self.freeze()

    def test_corrupt_manifest_or_export_rejected_before_oracle_access(self):
        sha256 = self.freeze()
        export = self.bundle / "predictions.json"
        export.write_text('[{"id":"tampered"}]')
        with patch.object(FrozenRun, "read_answer_key", side_effect=AssertionError("Oracle read")):
            with self.assertRaisesRegex(ValueError, "file hash mismatch"):
                FrozenRun(self.bundle, sha256)
            export.write_text("[]")
            (self.bundle / "manifest.json").write_text("{}")
            with self.assertRaisesRegex(ValueError, "manifest hash mismatch"):
                FrozenRun(self.bundle, sha256)

    def test_freeze_never_opens_oracle(self):
        original = Path.read_bytes

        def guarded(path):
            if path.is_relative_to(self.oracle):
                raise AssertionError("Oracle opened before freeze")
            return original(path)

        with patch.object(Path, "read_bytes", guarded):
            self.freeze()

    def test_wrong_split_or_naive_origin_rejected(self):
        self.protocol["stores"] = ["ROM01"]
        with self.assertRaisesRegex(ValueError, "split"):
            self.freeze()
        self.protocol["stores"] = ["MIL01"]
        self.protocol["origins"] = ["2026-10-08T20:00:00"]
        with self.assertRaisesRegex(ValueError, "time zone"):
            self.freeze()

    def test_oracle_cannot_become_a_source_even_through_symlink(self):
        link = self.sources[0].parent / "leak.csv"
        link.symlink_to(self.oracle / "key.csv")
        self.sources = [link]
        with self.assertRaisesRegex(ValueError, "only generated/sources"):
            self.freeze()

    def test_oracle_path_traversal_and_symlink_rejected(self):
        run = FrozenRun(self.bundle, self.freeze())
        (self.oracle / "escape").symlink_to(self.configuration[0])
        for name in ["../../config/pipeline.json", "escape", str(self.configuration[0])]:
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "escapes"):
                run.read_answer_key(self.oracle, name)

    def test_bundle_symlink_cannot_escape(self):
        sha256 = self.freeze()
        path = self.bundle / "predictions.json"
        path.unlink()
        path.symlink_to(self.artifacts["predictions"])
        with self.assertRaisesRegex(ValueError, "escapes"):
            FrozenRun(self.bundle, sha256)

    def test_configuration_snapshot_is_verified(self):
        sha256 = self.freeze()
        (self.bundle / "configuration/0-pipeline.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "file hash mismatch"):
            FrozenRun(self.bundle, sha256)

    def test_artifacts_must_be_arrays_of_objects(self):
        self.artifacts["cases"].write_text(json.dumps({"cases": []}))
        with self.assertRaisesRegex(ValueError, "array"):
            self.freeze()

    def test_export_cannot_read_oracle_or_write_sources(self):
        original = self.artifacts["predictions"]
        original.unlink()
        original.symlink_to(self.oracle / "key.csv")
        with self.assertRaisesRegex(ValueError, "exports must come from data"):
            self.freeze()
        self.bundle = self.sources[0].parent / "frozen"
        with self.assertRaisesRegex(ValueError, "bundles must be written under data"):
            self.freeze()
