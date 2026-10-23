"""EVL-02 reading eval: observations and product links against hand-written dev labels.

Labels live in ``eval/labels/`` (never readable by the product). Each label is one fact of a
sampled email: an ``anchor`` substring of the canonical document text, the acceptable kinds,
whether recall counts it (``required``) and the catalog product the store means.

Matching, fixed before the first run:

- an observation matches a label when its evidence span overlaps the label's anchor span in
  the same document and its kind is one of the label's kinds. One observation may match several
  labels (a coarser reading of one line); several observations may match one label (counted as
  redundant, not as false positives);
- precision = matching observations / observations on the sampled documents;
  recall = required labels matched by at least one observation / required labels;
- links are scored on matched observations whose label names a product: ``linked`` is
  accepted, and an error when its target disagrees with the label on any level both state
  (``level: style`` labels accept only style links); ``ambiguous``/``unlinked`` abstain;
  ``not_product`` means the mention was not kept. A coarser correct link is not an error.

Span overlap does not prove the semantics right; quantities and periods are not scored here.
"""

import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

import yaml

LABELS = Path(__file__).resolve().parent / "labels" / "reading_dev_v1.yaml"
URI_PREFIX = "dataset://store_emails/"


def load_labels(path: Path = LABELS) -> tuple[dict, str]:
    data = path.read_bytes()
    return yaml.safe_load(data), hashlib.sha256(data).hexdigest()


def reading_protocol(labels: dict, spec: dict) -> dict:
    """The harness protocol of a reading run, from the label sample and the frozen RunSpec."""
    stores = sorted({name.split("/")[0] for name in labels["files"]})
    return {
        "run_id": spec["run_id"],
        "split": labels["sample"]["split"],
        "stores": stores,
        "origins": [spec["as_of"]],
        # Reading is scored per document: every catalog SKU of each store is in scope.
        "universe": [{"store_id": store, "sku": "*"} for store in stores],
        "sampling_criterion": labels["sample"]["criterion"],
        "models": spec["model_versions"],
        "parameters": {
            "prompts": spec["prompt_versions"],
            "modules": {m["manifest"]["id"]: m["params"] for m in spec["modules"]},
            "source_manifest_hash": spec["source_manifest_hash"],
            "config_hash": spec["config_hash"],
            "code_version": spec["code_version"],
        },
    }


def catalog_ids(master_dir: Path) -> set[str]:
    """Style codes, SKUs and SKU-sizes of the master data (a source, not the oracle)."""
    ids: set[str] = set()
    with (master_dir / "sku_size_ean.csv").open(encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            ids |= {row["sku_size"], row["sku"], row["sku"].split("-")[0]}
    return ids


def _anchor_span(text: str, anchor: str, label_id: str) -> tuple[int, int]:
    start = text.find(anchor)
    if start == -1 or text.find(anchor, start + 1) != -1:
        problem = "not found" if start == -1 else "not unique"
        raise ValueError(f"label {label_id}: anchor {problem} in the document text")
    return start, start + len(anchor)


def _compatible(target: str, level: str, expected: str, expected_level: str | None) -> bool:
    if expected_level == "style" and level != "style":
        return False
    got, want = target.split("-"), expected.split("-")
    depth = min(len(got), len(want))
    return got[:depth] == want[:depth]


def _ratio(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else round(numerator / denominator, 4)


def score(labels: dict, records: list[dict], catalog: set[str] | None = None) -> dict:
    """Score exported ``{"kind", "payload"}`` records against ``labels``."""
    by_kind: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        by_kind[record["kind"]].append(record["payload"])
    documents = {
        d["uri"].removeprefix(URI_PREFIX): d
        for d in by_kind["SourceDocument"]
        if d["uri"].startswith(URI_PREFIX)
    }
    observations: dict[str, list[dict]] = defaultdict(list)
    for observation in by_kind["Observation"]:
        observations[observation["document_id"]].append(observation)
    links = {lk["observation_id"]: lk for lk in by_kind["EntityLink"]}
    modules = {m["module_id"]: m.get("result") or {} for m in by_kind["ModuleRun"]}
    extract = modules.get("ing.extract", {})
    # "<doc id>: <reason>" for documents the extractor abstained on or could not read.
    unread = {
        message.split(": ", 1)[0]: message.split(": ", 1)[1]
        for message in [*extract.get("errors", ()), *extract.get("abstentions", ())]
        if ": " in message and " rejected (" not in message
    }

    files = labels["files"]
    exclusions, label_errors = [], []
    per_language: dict[str, Counter] = defaultdict(Counter)
    link_counts: Counter = Counter()
    false_positives, misses, link_errors, negation_errors = [], [], [], []
    redundant = 0
    for name, entry in sorted(files.items()):
        language = entry["language"]
        stats = per_language[language]
        stats["files"] += 1
        items = entry.get("labels") or []
        stats["labels"] += len(items)
        stats["required"] += sum(1 for item in items if item["required"])
        for item in items:
            product = item.get("product")
            if catalog is not None and product is not None and product not in catalog:
                label_errors.append(f"label {item['id']}: product {product} not in the catalog")
        document = documents.get(name)
        if document is None:
            exclusions.append({"file": name, "reason": "no SourceDocument in the export"})
            stats["excluded_files"] += 1
            misses += [
                {"label": item["id"], "file": name, "reason": "document not exported"}
                for item in items
                if item["required"]
            ]
            continue
        if document["id"] in unread:
            exclusions.append({"file": name, "reason": f"not read: {unread[document['id']]}"})
            stats["unread_files"] += 1
        spans = {}
        for item in items:
            try:
                spans[item["id"]] = _anchor_span(document["text"], item["anchor"], item["id"])
            except ValueError as error:
                label_errors.append(str(error))
        matched: dict[str, list[dict]] = defaultdict(list)
        for observation in observations.get(document["id"], []):
            stats["observations"] += 1
            evidence = observation["evidence"][0]
            start, end = evidence["char_start"], evidence["char_end"]
            overlapping = [
                item
                for item in items
                if item["id"] in spans
                and start < spans[item["id"]][1]
                and spans[item["id"]][0] < end
            ]
            hits = [item for item in overlapping if observation["kind"] in item["kinds"]]
            if not hits:
                false_positives.append(
                    {
                        "file": name,
                        "observation": observation["id"],
                        "kind": observation["kind"],
                        "quote": evidence["quote"],
                        "reason": "kind_mismatch" if overlapping else "unlabelled",
                    }
                )
                continue
            stats["true_positives"] += 1
            for item in hits:
                matched[item["id"]].append(observation)
            if any(observation["negated"] != item.get("negated", False) for item in hits):
                negation_errors.append(observation["id"])
            # The label the evidence overlaps most decides the expected product.
            best = max(
                hits,
                key=lambda item: min(end, spans[item["id"]][1]) - max(start, spans[item["id"]][0]),
            )
            expected = best.get("product")
            if expected is None:
                continue
            link = links.get(observation["id"])
            if link is None:
                link_counts["no_link"] += 1
            elif link["status"] == "linked":
                link_counts["accepted"] += 1
                if _compatible(link["target_id"], link["level"], expected, best.get("level")):
                    if len(link["target_id"].split("-")) < len(expected.split("-")):
                        link_counts["coarser"] += 1
                else:
                    link_counts["errors"] += 1
                    link_errors.append(
                        {
                            "observation": observation["id"],
                            "label": best["id"],
                            "mention": observation.get("product_mention"),
                            "linked": link["target_id"],
                            "expected": expected,
                        }
                    )
            else:
                link_counts[link["status"]] += 1
            link_counts["product_labels"] += 1
        for item in items:
            hit = item["id"] in matched
            redundant += max(0, len(matched.get(item["id"], [])) - 1)
            if item["required"]:
                stats["required_matched"] += hit
                if not hit:
                    misses.append({"label": item["id"], "file": name, "anchor": item["anchor"]})
            stats["labels_matched"] += hit
    if label_errors:
        raise ValueError("Invalid labels: " + "; ".join(label_errors))

    def metrics(stats: Counter) -> dict:
        return {
            **{key: stats[key] for key in sorted(stats)},
            "precision": _ratio(stats["true_positives"], stats["observations"]),
            "recall_required": _ratio(stats["required_matched"], stats["required"]),
            "recall_all_labels": _ratio(stats["labels_matched"], stats["labels"]),
        }

    total: Counter = sum(per_language.values(), Counter())
    abstained = link_counts["ambiguous"] + link_counts["unlinked"]
    return {
        "status": "scored",
        "sample": labels["sample"],
        "overall": metrics(total),
        "per_language": {
            language: metrics(per_language[language]) for language in sorted(per_language)
        },
        "module_status": {k: v.get("status") for k, v in sorted(modules.items())},
        "extract_counts": extract.get("counts", {}),
        "redundant_matches": redundant,
        "negation_errors": negation_errors,
        "links": {
            **{key: link_counts[key] for key in sorted(link_counts)},
            "error_rate_among_accepted": _ratio(link_counts["errors"], link_counts["accepted"]),
            "accepted_rate": _ratio(link_counts["accepted"], link_counts["product_labels"]),
            "abstention_rate": _ratio(abstained, link_counts["product_labels"]),
            "not_product_rate": _ratio(link_counts["not_product"], link_counts["product_labels"]),
        },
        "exclusions": exclusions,
        "false_positives": false_positives,
        "missed_required": misses,
        "link_errors": link_errors,
    }
