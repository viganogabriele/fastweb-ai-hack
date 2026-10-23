"""EVL-02 scorer on synthetic labels and exports; no real label, email or answer key."""

import unittest

from eval.harness import validate_protocol
from eval.reading import reading_protocol, score

TEXT = "Sales 10k vs 12k. Asked: widget black S, none. Widget returned, too small."


def document(name="AAA01/x.eml", doc_id="doc-x", text=TEXT):
    return {
        "kind": "SourceDocument",
        "payload": {"id": doc_id, "uri": f"dataset://store_emails/{name}", "text": text},
    }


def observation(obs_id, quote, kind, *, doc_id="doc-x", text=TEXT, negated=False):
    start = text.index(quote)
    evidence = {"quote": quote, "char_start": start, "char_end": start + len(quote)}
    payload = {"id": obs_id, "document_id": doc_id, "kind": kind, "negated": negated}
    payload |= {"product_mention": None, "evidence": [evidence]}
    return {"kind": "Observation", "payload": payload}


def link(obs_id, status, target=None, level=None):
    payload = {"observation_id": obs_id, "status": status, "target_id": target, "level": level}
    return {"kind": "EntityLink", "payload": payload}


def labels(files=None):
    return {
        "sample": {"split": "dev", "criterion": "synthetic sample"},
        "files": files
        or {
            "AAA01/x.eml": {
                "language": "en",
                "labels": [
                    {"id": "sales", "anchor": "Sales 10k vs 12k", "kinds": ["sales_figure"],
                     "required": True},
                    {"id": "unmet", "anchor": "widget black S", "kinds": ["unmet_demand"],
                     "required": True, "product": "W1-999-S"},
                    {"id": "fit", "anchor": "Widget returned, too small", "required": False,
                     "kinds": ["product_feedback"], "product": "W1", "level": "style"},
                ],
            },
            "AAA01/wrong-list.eml": {"language": "en", "labels": []},
        },
    }  # fmt: skip


class ReadingScoreTests(unittest.TestCase):
    def test_precision_recall_and_false_positive_reasons(self):
        records = [
            document(),
            observation("o1", "Sales 10k", "sales_figure"),
            observation("o2", "Sales 10k vs 12k", "sales_figure"),  # redundant, not an FP
            observation("o3", "widget black S", "stockout"),  # right span, wrong kind
            observation("o4", "none", "other"),  # outside every anchor
        ]
        result = score(labels(), records)
        overall = result["overall"]
        self.assertEqual((overall["observations"], overall["true_positives"]), (4, 2))
        self.assertEqual(overall["precision"], 0.5)
        self.assertEqual(overall["recall_required"], 0.5)
        self.assertEqual(result["redundant_matches"], 1)
        reasons = {fp["observation"]: fp["reason"] for fp in result["false_positives"]}
        self.assertEqual(reasons, {"o3": "kind_mismatch", "o4": "unlabelled"})
        self.assertEqual([m["label"] for m in result["missed_required"]], ["unmet"])
        # The wrong-list mail is in the sample but has no document: reported, not dropped.
        self.assertEqual(result["exclusions"][0]["file"], "AAA01/wrong-list.eml")

    def test_optional_labels_neither_count_as_misses_nor_as_false_positives(self):
        records = [document(), observation("o1", "too small", "product_feedback")]
        result = score(labels(), records)
        self.assertEqual(result["overall"]["precision"], 1.0)
        self.assertEqual(result["overall"]["recall_required"], 0.0)
        self.assertEqual(result["overall"]["recall_all_labels"], round(1 / 3, 4))

    def test_links_errors_among_accepted_and_abstention(self):
        records = [
            document(),
            observation("o1", "widget black S", "unmet_demand"),
            observation("o2", "Widget returned", "product_feedback"),
            link("o1", "linked", "W1-999", "sku"),  # coarser than the label: correct
            link("o2", "linked", "W1-742", "sku"),  # style-only label: any colour is an error
        ]
        result = score(labels(), records)["links"]
        self.assertEqual((result["accepted"], result["errors"], result["coarser"]), (2, 1, 1))
        self.assertEqual(result["error_rate_among_accepted"], 0.5)
        records[-2:] = [link("o1", "ambiguous"), link("o2", "linked", "W2", "style")]
        result = score(labels(), records)["links"]
        self.assertEqual((result["accepted"], result["errors"], result["ambiguous"]), (1, 1, 1))
        self.assertEqual(result["abstention_rate"], 0.5)

    def test_negation_mismatch_is_reported(self):
        records = [document(), observation("o1", "Sales 10k", "sales_figure", negated=True)]
        self.assertEqual(score(labels(), records)["negation_errors"], ["o1"])

    def test_unread_documents_are_excluded_explicitly(self):
        run = {"module_id": "ing.extract", "status": "degraded", "result": {
            "status": "degraded", "counts": {}, "abstentions": (),
            "errors": ("doc-x: ReplayMiss",)}}  # fmt: skip
        result = score(labels(), [document(), {"kind": "ModuleRun", "payload": run}])
        self.assertIn({"file": "AAA01/x.eml", "reason": "not read: ReplayMiss"},
                      result["exclusions"])  # fmt: skip

    def test_invalid_labels_fail_loudly(self):
        files = labels()["files"]
        files["AAA01/x.eml"]["labels"][0]["anchor"] = "not in the text"
        with self.assertRaisesRegex(ValueError, "anchor not found"):
            score(labels(files), [document()])
        files = labels()["files"]
        files["AAA01/x.eml"]["labels"][1]["product"] = "W9-999"
        with self.assertRaisesRegex(ValueError, "not in the catalog"):
            score(labels(files), [document()], catalog={"W1", "W1-999", "W1-999-S"})

    def test_protocol_is_accepted_by_the_harness(self):
        spec = {
            "run_id": "r", "as_of": "2026-10-09T04:00:00Z", "model_versions": {"chat": "m"},
            "prompt_versions": {"extract": "p"}, "source_manifest_hash": "s",
            "config_hash": "c", "code_version": "v",
            "modules": [{"manifest": {"id": "src.email"}, "params": {"files": ["MIL01/x.eml"]}}],
        }  # fmt: skip
        sample = labels({"MIL01/x.eml": {"language": "it", "labels": []}})
        validate_protocol(reading_protocol(sample, spec))


if __name__ == "__main__":
    unittest.main()
