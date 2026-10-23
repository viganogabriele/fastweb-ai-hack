"""EVL-05: pre-registered hold-out reading sample and append-only scoring wrappers.

Run from the repository root: ``backend/.venv/bin/python -m eval.holdout --help``.

Reading sample (EVL-02H, #126), fixed before the ``freeze-g3`` tag and before any hold-out
email body was read. Eligible files: every ``store_emails/<STORE>/*.eml`` of the hold-out
stores (``config/eval_split.yaml``) whose ``Date:`` header falls on a store-local calendar day
in [START, END], the same rule as the rolling runner's reading pass (``reading_files``).
Per store, eligible files are ordered by ``sha256(SEED + "|" + "<STORE>/<file>")`` and the
first ``PER_STORE`` are taken (all of them if fewer). Only file names and Date headers are
read; no claim, answer key, subject line or product output takes part in the choice, so
duplicates, forwards, corrections and no-signal mails enter in their natural proportion.

Scoring wrappers implement ``docs/holdout-evaluation-protocol.md`` §5.2-§5.4. Each writes one
new file into an experiment directory under ``data/`` with exclusive creation: a rerun needs
a new directory, earlier results are never overwritten.
"""

import argparse
import csv
import hashlib
import json
from datetime import date, datetime
from email.parser import BytesHeaderParser
from email.policy import default as email_policy
from pathlib import Path

from .baselines import store_zones
from .forecast import KEY as FORECAST_KEY
from .forecast import score_forecasts
from .harness import FrozenRun, split_stores
from .lead_time import EMAIL_INDEXES, EVENTS_KEY, lead_time_report
from .reading import catalog_ids, load_labels, score

ROOT = Path(__file__).resolve().parent.parent
SOURCES = Path("generated/sources")
SEED = "EVL-02H/reading-holdout/v1"
PER_STORE = 11
START, END = date(2026, 8, 31), date(2026, 10, 21)
LABELS = Path("eval/labels/reading_holdout_v1.yaml")
LEAD_KEYS = (EVENTS_KEY, *EMAIL_INDEXES)
KINDS = frozenset(
    "unmet_demand demand_up demand_down stockout low_stock stock_discrepancy product_feedback "
    "traffic_change customer_profile operational_issue sales_figure local_event other".split()
)


def header_date(path: Path) -> datetime | None:
    """The aware ``Date:`` header of an .eml file; the body is not read."""
    with path.open("rb") as stream:
        lines = []
        for line in stream:
            if line in (b"\n", b"\r\n"):
                break
            lines.append(line)
    header = BytesHeaderParser(policy=email_policy).parsebytes(b"".join(lines)).get("date")
    try:
        value = header.datetime if header is not None else None
    except (AttributeError, TypeError, ValueError):
        return None
    return value if value is not None and value.tzinfo is not None else None


def eligible_files(root: Path, start: date = START, end: date = END) -> dict[str, list[str]]:
    """Hold-out mail files dated (store-local) inside the period, per store."""
    zones = store_zones(root)
    eligible = {}
    for store in sorted(split_stores()["holdout"]):
        names = []
        for path in sorted((root / SOURCES / "store_emails" / store).glob("*.eml")):
            sent = header_date(path)
            if sent is not None and start <= sent.astimezone(zones[store]).date() <= end:
                names.append(f"{store}/{path.name}")
        eligible[store] = names
    return eligible


def rank(name: str, seed: str = SEED) -> str:
    return hashlib.sha256(f"{seed}|{name}".encode()).hexdigest()


def select(eligible: dict[str, list[str]], per_store: int = PER_STORE, seed: str = SEED):
    """The pre-registered sample: the ``per_store`` lowest hash ranks of each store."""
    return {
        store: sorted(sorted(names, key=lambda n: rank(n, seed))[:per_store])
        for store, names in sorted(eligible.items())
    }


def sample_record(root: Path) -> dict:
    eligible = eligible_files(root)
    chosen = select(eligible)
    files = [name for names in chosen.values() for name in names]
    return {
        "seed": SEED,
        "per_store": PER_STORE,
        "period": [START.isoformat(), END.isoformat()],
        "rule": " ".join(__doc__.split("\n\n")[2].split()),
        "eligible_per_store": {store: len(names) for store, names in eligible.items()},
        "eligible_sha256": hashlib.sha256(
            "".join(f"{n}\n" for names in eligible.values() for n in names).encode()
        ).hexdigest(),
        "selected_per_store": {store: len(names) for store, names in chosen.items()},
        "files": files,
        "files_sha256": hashlib.sha256("".join(f"{n}\n" for n in files).encode()).hexdigest(),
    }


def store_languages(root: Path) -> dict[str, str]:
    with (root / SOURCES / "erp/master_data/stores.csv").open(encoding="utf-8") as stream:
        return {row["store_id"]: row["language"] for row in csv.DictReader(stream)}


def canonical_text(root: Path, name: str) -> dict:
    """The document text the product scores against (ING-02 parser), for annotation."""
    from tesseract.modules.ingestion.email_parser import parse_eml  # sources-only parser

    parsed = parse_eml((root / SOURCES / "store_emails" / name).read_bytes())
    return {
        "file": name,
        "subject": parsed.subject,
        "is_reply": parsed.is_reply,
        "is_forward": parsed.is_forward,
        "attachments": [a.filename for a in parsed.attachments],
        "quoted_spans": [[s.char_start, s.char_end] for s in parsed.segments if s.is_quoted],
        "text": parsed.text,
    }


def annotation_pack(root: Path, out_dir: Path) -> None:
    """One JSON per store with the canonical text of the sampled files, nothing else."""
    languages = store_languages(root)
    for store, names in select(eligible_files(root)).items():
        pack = {
            "store_id": store,
            "language": languages[store],
            "documents": [canonical_text(root, name) for name in names],
        }
        _write_new(out_dir / f"{store}.json", pack)


def check_labels(root: Path, labels: dict) -> list[str]:
    """Schema problems of a hold-out label file (anchors, kinds, products, sample, ids)."""
    problems = []
    catalog = catalog_ids(root / SOURCES / "erp/master_data")
    languages = store_languages(root)
    expected = [n for names in select(eligible_files(root)).values() for n in names]
    if sorted(labels.get("files", {})) != sorted(expected):
        problems.append("files differ from the pre-registered sample")
    if labels.get("sample", {}).get("split") != "holdout":
        problems.append("sample.split must be holdout")
    seen: set[str] = set()
    for name, entry in sorted(labels.get("files", {}).items()):
        if entry.get("language") != languages.get(name.split("/")[0]):
            problems.append(f"{name}: language must be the store language")
        text = (
            canonical_text(root, name)["text"]
            if (root / SOURCES / "store_emails" / name).exists()
            else ""
        )
        for item in entry.get("labels") or []:
            label = item.get("id", "?")
            if label in seen:
                problems.append(f"{label}: duplicate id")
            seen.add(label)
            if not isinstance(item.get("required"), bool):
                problems.append(f"{label}: required must be true or false")
            kinds = item.get("kinds") or []
            if not kinds or not set(kinds) <= KINDS:
                problems.append(f"{label}: kinds {kinds} outside the taxonomy")
            anchor = item.get("anchor") or ""
            if not anchor or text.count(anchor) != 1:
                problems.append(
                    f"{label}: anchor found {text.count(anchor) if anchor else 0} times"
                )
            product = item.get("product")
            if product is not None and product not in catalog:
                problems.append(f"{label}: product {product} not in the catalog")
            if item.get("level") not in (None, "style"):
                problems.append(f"{label}: level must be style or absent")
            if item.get("level") == "style" and (product is None or "-" in product):
                problems.append(f"{label}: level style needs a style code")
            if not isinstance(item.get("negated", False), bool):
                problems.append(f"{label}: negated must be true or false")
    return problems


def _write_new(path: Path, data: object) -> Path:
    """Exclusive creation under data/: previous records are never overwritten."""
    if not path.resolve().is_relative_to(ROOT / "data"):
        raise SystemExit(f"{path}: evaluation outputs must be written under data/")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(f"{path} sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")
    return path


def reading(bundle: Path, sha256: str, labels_path: Path, label_sha: str, experiment: Path):
    """Protocol §5.2 with the explicit hold-out label path; the sample is a subset of the
    frozen ``reading_files`` and must equal the pre-registered selection over them."""
    run = FrozenRun(bundle, sha256)
    protocol = run.manifest["protocol"]
    labels, labels_sha256 = load_labels(labels_path)
    if labels_sha256 != label_sha:
        raise SystemExit("label fingerprint mismatch")
    if not protocol["split"] == labels["sample"]["split"] == "holdout":
        raise SystemExit("protocol and labels must both be the hold-out split")
    frozen = protocol.get("reading_files")
    if not frozen:
        raise SystemExit("the frozen protocol has no reading_files")
    labelled = sorted(labels["files"])
    if not set(labelled) <= set(frozen):
        raise SystemExit("labelled files outside the frozen reading_files")
    if not {name.split("/")[0] for name in labelled} <= set(protocol["stores"]):
        raise SystemExit("labelled stores outside the frozen protocol")
    by_store: dict[str, list[str]] = {}
    for name in frozen:
        by_store.setdefault(name.split("/")[0], []).append(name)
    expected = sorted(n for names in select(by_store).values() for n in names)
    if labelled != expected:
        raise SystemExit("labelled files differ from the pre-registered selection")
    result = score(
        labels, run.artifacts["predictions"], catalog_ids(ROOT / SOURCES / "erp/master_data")
    )
    result.update(
        manifest_sha256=run.manifest_sha256,
        labels_path=str(labels_path),
        labels_sha256=labels_sha256,
        sample={**result["sample"], "seed": SEED, "per_store": PER_STORE},
        frozen_reading_files=len(frozen),
        protocol=protocol,
    )
    _write_new(experiment / "reading.json", result)


def lead_time(bundle: Path, sha256: str, start: date, end: date, experiment: Path):
    """Protocol §5.3: oracle-key receipt, then the lead-time report on the frozen cases."""
    run = FrozenRun(bundle, sha256)
    _write_new(
        experiment / "lead-time-inputs.json",
        run.receipt(ROOT / "generated/ground_truth", list(LEAD_KEYS)),
    )
    _write_new(experiment / "lead-time.json", lead_time_report(ROOT, run, "holdout", start, end))


def forecast(bundles: list[tuple[Path, str]], experiment: Path):
    """Protocol §5.4, one scored record per frozen forecast bundle (store group)."""
    results = []
    for bundle, sha256 in bundles:
        run = FrozenRun(bundle, sha256)
        results.append(
            {
                "bundle": str(bundle),
                **score_forecasts(run, ROOT / "generated/ground_truth", FORECAST_KEY),
            }
        )
    _write_new(experiment / "forecast-errors.json", {"status": "scored", "bundles": results})


def forecast_unavailable(reasons: list[str], experiment: Path):
    _write_new(
        experiment / "forecast-errors.json",
        {"status": "unavailable", "measure": "forecast WAPE/MAE (EVL-03)", "reasons": reasons},
    )


def inventory(experiment: Path, extra: list[Path]):
    """SHA-256 and size of every result file (and of the given inputs), as a new file."""
    files = sorted(p for p in experiment.iterdir() if p.is_file()) + extra
    _write_new(
        experiment / f"inventory-{datetime.now().strftime('%Y%m%dT%H%M%S')}.json",
        {
            str(p): {
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                "bytes": p.stat().st_size,
            }
            for p in files
        },
    )


def _bundle_arg(value: str) -> tuple[Path, str]:
    path, _, digest = value.rpartition("=")
    if not path or len(digest) != 64:
        raise argparse.ArgumentTypeError("expected PATH=SHA256")
    return Path(path), digest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sample = sub.add_parser("sample", help="Print (or write) the pre-registered reading sample")
    sample.add_argument("--output", type=Path)
    for name in ("reading", "lead-time"):
        p = sub.add_parser(name)
        p.add_argument("--bundle", type=Path, required=True)
        p.add_argument("--sha256", required=True)
        p.add_argument("--experiment", type=Path, required=True)
    sub.choices["reading"].add_argument("--labels", type=Path, default=LABELS)
    sub.choices["reading"].add_argument("--label-sha", required=True)
    sub.choices["lead-time"].add_argument("--start", type=date.fromisoformat, default=START)
    sub.choices["lead-time"].add_argument("--end", type=date.fromisoformat, default=END)
    fc = sub.add_parser("forecast", help="Score frozen forecast bundles (PATH=SHA256 each)")
    fc.add_argument("--bundle", type=_bundle_arg, action="append", required=True)
    fc.add_argument("--experiment", type=Path, required=True)
    na = sub.add_parser("forecast-unavailable", help="Record why WAPE/MAE are not scored")
    na.add_argument("--reason", action="append", required=True)
    na.add_argument("--experiment", type=Path, required=True)
    pack = sub.add_parser("annotation-pack", help="Canonical text of the sample, per store")
    pack.add_argument("--output-dir", type=Path, required=True)
    chk = sub.add_parser("check-labels", help="Validate a hold-out label file, print its SHA-256")
    chk.add_argument("--labels", type=Path, default=LABELS)
    inv = sub.add_parser("inventory", help="Hash every file of the experiment directory")
    inv.add_argument("--experiment", type=Path, required=True)
    inv.add_argument("--file", type=Path, action="append", default=[])
    args = parser.parse_args()
    if args.command == "sample":
        record = sample_record(ROOT)
        if args.output:
            _write_new(args.output, record)
        else:
            print(json.dumps(record, indent=2))
    elif args.command == "annotation-pack":
        annotation_pack(ROOT, args.output_dir)
    elif args.command == "check-labels":
        labels, digest = load_labels(args.labels)
        problems = check_labels(ROOT, labels)
        print("\n".join(problems) or f"ok {args.labels} sha256={digest}")
        raise SystemExit(1 if problems else 0)
    elif args.command == "reading":
        reading(args.bundle, args.sha256, args.labels, args.label_sha, args.experiment)
    elif args.command == "lead-time":
        lead_time(args.bundle, args.sha256, args.start, args.end, args.experiment)
    elif args.command == "forecast":
        forecast(args.bundle, args.experiment)
    elif args.command == "forecast-unavailable":
        forecast_unavailable(args.reason, args.experiment)
    else:
        inventory(args.experiment, args.file)


if __name__ == "__main__":
    main()
