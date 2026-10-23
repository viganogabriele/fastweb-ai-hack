"""Only fictional inline DTOs and temporary files; never read real source emails."""

import copy
import hashlib
import json
import stat
import tempfile
import unittest
from pathlib import Path

from build_public_demo import Builder, build_bundle


def sample():
    text = "🧥 店 PrivateHouse unavailable. Again: 🧥 店 PrivateHouse unavailable."
    quote = "🧥 店 PrivateHouse unavailable."
    start = text.rindex(quote)
    return {
        "version": 1,
        "approved": True,
        "split": "dev",
        "stores": ["MIL01"],
        "reference_key": "synthetic-example-reference-key-only",
        "replacements": {"PrivateHouse": "Loom"},
        "artifacts": [
            {
                "kind": "SourceDocument",
                "payload": {
                    "id": "private-document",
                    "version": "original-v7",
                    "text": text,
                    "text_version": "original-text",
                    "source_type": "email",
                    "uri": "/private/raw.eml",
                    "author_ref": "someone@private.test",
                    "meta": {
                        "store_id": "MIL01",
                        "headers": "SECRET HEADER",
                        "attachments": ["private.xlsx"],
                    },
                },
            },
            {
                "kind": "Segment",
                "payload": {
                    "id": "private-segment",
                    "version": "v1",
                    "document_id": "private-document",
                    "text_version": "original-text",
                    "text": text,
                    "char_start": 0,
                    "char_end": len(text),
                    "locator": "private.xlsx#A1",
                },
            },
            {
                "kind": "Observation",
                "payload": {
                    "id": "private-observation",
                    "version": "v1",
                    "document_id": "private-document",
                    "store_id": "MIL01",
                    "kind": "unmet_demand",
                    "product_mention": "PrivateHouse",
                    "quantity": {"kind": "unknown"},
                    "evidence": [
                        {
                            "document_id": "private-document",
                            "document_version": "original-v7",
                            "segment_id": "private-segment",
                            "quote": quote,
                            "char_start": start,
                            "char_end": start + len(quote),
                            "t_start_s": 99,
                        }
                    ],
                },
            },
            {
                "kind": "Case",
                "payload": {
                    "id": "private-case",
                    "version": "v1",
                    "store_id": "MIL01",
                    "case_type": "unmet_demand",
                    "status": "verify",
                    "priority": "medium",
                    "priority_reason": "Confirm PrivateHouse stock",
                    "owner": "private-person",
                    "supporting": [
                        {"kind": "Observation", "id": "private-observation", "version": "v1"}
                    ],
                },
            },
            {
                "kind": "Report",
                "payload": {
                    "id": "private-report",
                    "version": "v1",
                    "markdown": "Confirm PrivateHouse stock [1].",
                    "raw_response": "PRIVATE MODEL RECORDING",
                    "citations": [
                        {
                            "ref": {
                                "kind": "Observation",
                                "id": "private-observation",
                                "version": "v1",
                            },
                            "field": "quantity.kind",
                            "scope": {"store_id": "MIL01"},
                        }
                    ],
                },
            },
        ],
    }


class PublicDemoTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "config").mkdir()
        (self.root / "config/eval_split.yaml").write_text("dev: [MIL01]\nholdout: [ROM01]\n")
        (self.root / "data").mkdir()
        self.source = self.root / "data/approved.json"
        self.output = self.root / "data/public"
        self.mapping = self.root / "data/private/map.json"
        self.manifest = sample()

    def build(self):
        self.source.write_text(json.dumps(self.manifest))
        before = self.source.read_bytes()
        build_bundle(self.root, self.source, self.output, self.mapping)
        self.assertEqual(self.source.read_bytes(), before)
        return json.loads((self.output / "artifacts.json").read_bytes())

    def test_unicode_repeated_quote_and_all_references_survive_sanitisation(self):
        artifacts = self.build()
        kinds = {a["kind"]: a["payload"] for a in artifacts}
        self.assertEqual(set(kinds), {"SourceDocument", "Segment", "Observation", "Case", "Report"})
        document, segment = kinds["SourceDocument"], kinds["Segment"]
        evidence = kinds["Observation"]["evidence"][0]
        self.assertEqual(evidence["char_start"], document["text"].rindex(evidence["quote"]))
        self.assertNotEqual(evidence["char_start"], document["text"].index(evidence["quote"]))
        self.assertEqual(
            document["text"][evidence["char_start"] : evidence["char_end"]], evidence["quote"]
        )
        self.assertEqual(segment["text"], document["text"])
        self.assertEqual(segment["text_version"], document["text_version"])
        refs = [
            evidence["document_ref"],
            evidence["segment_ref"],
            *kinds["Case"]["supporting"],
            kinds["Report"]["citations"][0]["ref"],
        ]
        identities = {(a["kind"], a["payload"]["id"], a["payload"]["version"]) for a in artifacts}
        self.assertTrue(all((r["kind"], r["id"], r["version"]) in identities for r in refs))

    def test_private_metadata_identifiers_media_and_mapping_never_enter_public_files(self):
        self.build()
        public = b"".join(p.read_bytes() for p in self.output.iterdir()).decode()
        for secret in (
            "PrivateHouse",
            "private-document",
            "original-v7",
            "original-text",
            "MIL01",
            "SECRET HEADER",
            "private.xlsx",
            "someone@",
            "PRIVATE MODEL RECORDING",
            self.manifest["reference_key"],
            "private-person",
            "t_start_s",
        ):
            self.assertNotIn(secret, public)
        self.assertNotEqual(self.mapping.parent, self.output)
        self.assertEqual(stat.S_IMODE(self.mapping.stat().st_mode), 0o600)
        self.assertIn("private-document", self.mapping.read_text())

    def test_deterministic_files_and_hashes(self):
        self.build()
        contents = {p.name: p.read_bytes() for p in self.output.iterdir()}
        build_bundle(
            self.root,
            self.source,
            self.root / "data/second",
            self.root / "data/private/second.json",
        )
        self.assertEqual(
            contents, {p.name: p.read_bytes() for p in (self.root / "data/second").iterdir()}
        )
        manifest = json.loads(contents["manifest.json"])
        self.assertTrue(manifest["synthetic"])
        self.assertEqual(
            manifest["files"][0]["sha256"], hashlib.sha256(contents["artifacts.json"]).hexdigest()
        )
        self.assertEqual(manifest["excluded"], [])

    def test_mismatched_quote_drops_observation_and_dependent_citations(self):
        self.manifest["artifacts"][2]["payload"]["evidence"][0]["quote"] = "Not the source quote"
        artifacts = self.build()
        self.assertEqual({a["kind"] for a in artifacts}, {"SourceDocument", "Segment"})
        manifest = json.loads((self.output / "manifest.json").read_bytes())
        self.assertEqual(
            {a["kind"] for a in manifest["excluded"]}, {"Observation", "Case", "Report"}
        )
        self.assertTrue(all(len(item["descriptor_sha256"]) == 64 for item in manifest["excluded"]))

    def test_boundary_inside_replacement_does_not_invent_a_span(self):
        e = self.manifest["artifacts"][2]["payload"]["evidence"][0]
        text = self.manifest["artifacts"][0]["payload"]["text"]
        e["char_start"] = text.index("PrivateHouse") + 2
        e["char_end"] = e["char_start"] + 4
        e["quote"] = text[e["char_start"] : e["char_end"]]
        artifacts = self.build()
        self.assertNotIn("Observation", {a["kind"] for a in artifacts})
        self.assertIn("boundary_inside_replacement", (self.output / "manifest.json").read_text())

    def test_voice_and_raw_recordings_are_excluded(self):
        self.manifest["artifacts"][0]["payload"]["source_type"] = "voice_note"
        self.manifest["artifacts"].append(
            {
                "kind": "AgentTrace",
                "payload": {"id": "private-trace", "version": "v1", "raw": "secret recording"},
            }
        )
        self.assertEqual(self.build(), [])
        self.assertNotIn("secret recording", (self.output / "manifest.json").read_text())

    def test_unresolved_sensitive_text_is_not_published(self):
        for text in (
            "Email person@example.test",
            "Open https://private.test/a",
            "From: private person",
            "Read /home/user/secret.txt",
            "Read original.pdf",
            "<script>unsafe</script>",
            "Bearer private-secret-value",
            "api_key=private-secret-value",
            "Read original.pptx",
        ):
            with self.subTest(text=text):
                manifest = sample()
                manifest["artifacts"][0]["payload"]["text"] = text
                files, _ = Builder(manifest, ["MIL01"]).build()
                self.assertEqual(json.loads(files["artifacts.json"]), [])
                self.assertNotIn(text, files["manifest.json"].decode())

    def test_holdout_unapproved_and_duplicates_fail_before_writing(self):
        original = copy.deepcopy(self.manifest)
        for change in ("holdout", "not_approved", "duplicate"):
            self.manifest = copy.deepcopy(original)
            if change == "holdout":
                self.manifest["stores"] = ["ROM01"]
            elif change == "not_approved":
                self.manifest["approved"] = False
            else:
                self.manifest["artifacts"].append(copy.deepcopy(self.manifest["artifacts"][0]))
            self.source.write_text(json.dumps(self.manifest))
            with self.subTest(change=change), self.assertRaises(ValueError):
                build_bundle(self.root, self.source, self.output, self.mapping)
            self.assertFalse(self.output.exists())
            self.assertFalse(self.mapping.exists())

    def test_output_mapping_and_originals_cannot_be_overwritten_or_overlap(self):
        self.build()
        before = {p.name: p.read_bytes() for p in self.output.iterdir()}
        with self.assertRaises(FileExistsError):
            build_bundle(self.root, self.source, self.output, self.mapping)
        fresh_map = self.root / "data/private/fresh.json"
        with self.assertRaises(FileExistsError):
            build_bundle(self.root, self.source, self.output, fresh_map)
        self.assertFalse(fresh_map.exists())
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.output.iterdir()})
        for output, private in (
            (self.root / "outside", fresh_map),
            (self.root / "data/new", self.root / "data/new/map.json"),
        ):
            with self.assertRaises(ValueError):
                build_bundle(self.root, self.source, output, private)

    def test_missing_citation_field_or_reference_excludes_report(self):
        for field in ("meta.headers", "quantity.secret"):
            manifest = sample()
            manifest["artifacts"][-1]["payload"]["citations"][0]["field"] = field
            files, _ = Builder(manifest, ["MIL01"]).build()
            self.assertNotIn("Report", {a["kind"] for a in json.loads(files["artifacts.json"])})

    def test_conflicting_store_metadata_cannot_hide_holdout_input(self):
        self.manifest["artifacts"][0]["payload"]["store_id"] = "MIL01"
        self.manifest["artifacts"][0]["payload"]["meta"]["store_id"] = "ROM01"
        with self.assertRaisesRegex(ValueError, "approved dev"):
            Builder(self.manifest, ["MIL01"])

    def test_bad_citation_number_or_reference_is_reported_without_invented_evidence(self):
        for change in ("number", "reference"):
            manifest = sample()
            report = manifest["artifacts"][-1]["payload"]
            if change == "number":
                report["markdown"] = "Confirm stock [2]"
            else:
                report["citations"][0]["ref"]["version"] = "unavailable-version"
            files, _ = Builder(manifest, ["MIL01"]).build()
            self.assertNotIn("Report", {a["kind"] for a in json.loads(files["artifacts.json"])})
            self.assertIn(
                "Report", {a["kind"] for a in json.loads(files["manifest.json"])["excluded"]}
            )

    def test_obfuscated_names_and_multilingual_metadata_exclude_the_document(self):
        variants = [
            "Ｐｒｉｖａｔｅ\uff28ouse here",  # full-width
            "Private\u200bHouse here",  # zero-width space
            "Private\u00adHouse here",  # soft hyphen
            "Private-\nHouse here",  # line-break hyphen
            "Oggetto: chiusura\nBetreff: x",
            "see portal.privatecorp.local now",
            "share \\\\fileserver\\share\\x",
            "open ~/secrets now",
            "key AKIAIOSFODNN7EXAMPLE",
            "foto_negozio.heic attached",
            "Compare with ROM01 today",
        ]
        for text in variants:
            manifest = sample()
            document = manifest["artifacts"][0]["payload"]
            document["text"] = text
            manifest["artifacts"] = manifest["artifacts"][:1]
            files, _ = Builder(manifest, ["MIL01"]).build()
            with self.subTest(text=text):
                self.assertEqual(json.loads(files["artifacts.json"]), [])
                (excluded,) = json.loads(files["manifest.json"])["excluded"]
                self.assertIn(
                    excluded["reason"],
                    {"unresolved_sensitive_text", "store_outside_approved_split"},
                )

    def test_report_with_holdout_scope_or_text_is_excluded(self):
        for change in ("scope", "markdown"):
            manifest = sample()
            report = manifest["artifacts"][-1]["payload"]
            if change == "scope":
                report["citations"][0]["scope"] = {"store_id": "ROM01"}
            else:
                report["markdown"] = "ROM01 is out of stock too [1]."
            files, _ = Builder(manifest, ["MIL01"]).build()
            with self.subTest(change=change):
                kinds = {a["kind"] for a in json.loads(files["artifacts.json"])}
                self.assertNotIn("Report", kinds)

    def test_outputs_cannot_go_to_versioned_data_folders(self):
        (self.root / ".gitignore").write_text("data/*\n!data/fixtures/\n")
        self.source.write_text(json.dumps(self.manifest))
        for output, private in (
            (self.root / "data/fixtures/public", self.mapping),
            (self.output, self.root / "data/fixtures/map.json"),
        ):
            with self.subTest(output=output, private=private), self.assertRaises(ValueError):
                build_bundle(self.root, self.source, output, private)
            self.assertFalse(private.exists())

    def test_case_to_case_references_do_not_depend_on_id_order(self):
        for first in ("aa-case", "zz-case"):
            manifest = sample()
            case = copy.deepcopy(manifest["artifacts"][3])
            case["payload"]["id"] = first
            case["payload"]["context_refs"] = [
                {"kind": "Case", "id": "private-case", "version": "v1"}
            ]
            manifest["artifacts"].append(case)
            files, _ = Builder(manifest, ["MIL01"]).build()
            with self.subTest(first=first):
                cases = [a for a in json.loads(files["artifacts.json"]) if a["kind"] == "Case"]
                self.assertEqual(len(cases), 2)

    def test_malformed_artifact_is_excluded_not_fatal(self):
        manifest = sample()
        del manifest["artifacts"][0]["payload"]["text"]
        files, _ = Builder(manifest, ["MIL01"]).build()
        reasons = {e["reason"] for e in json.loads(files["manifest.json"])["excluded"]}
        self.assertIn("malformed_artifact", reasons)


if __name__ == "__main__":
    unittest.main()
