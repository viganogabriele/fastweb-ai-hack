"""EVL-04: lead time of the pipeline vs the stock and sales baselines (RFC §7.2).

Unit of analysis: one planted event × one evaluated store (`scenario/events.json`). For each
unit and method, the first valid alert is the earliest alert of that method that matches the
unit: same store, available inside `[event start 00:00 local, T_end]`, compatible product scope
and direction. `T_end` is 23:59:59 local of the day after the event's last day (capped at the
evaluation period), so a baseline reading the last event day still has its evening.

Lead time is `t_baseline - t_pipeline` in days, UTC. When only the pipeline detects, the lead is
reported as a lower bound `T_end - t_pipeline`, never as infinity or folded into a mean. Zero
and negative leads are reported as they are. Alerts that match no unit are false alerts with
respect to the planted events; real but unplanned stock-outs therefore count against the
stock baseline, a stated limit. Matching rules:

- store-wide events (empty filter) match only store-scope alerts;
- product events match alerts whose resolved SKU set intersects the event's, and the event's
  sizes when both sides name sizes; `unknown` scope never matches (it is a verify request);
- an alert with a direction must agree with the event (`demand_mult` above or below 1);
  `stockout` agrees with any event that is not a demand decrease.

Pipeline alerts are exported `Case`s, at `first_available_at`. Noise checks read the cited
store emails' kinds from the answer-key indexes, falling back to the source file suffix.
"""

import csv
import io
import json
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path

from .baselines import ERP, Alert, local_instant, sales_alerts, stock_alerts, store_zones
from .harness import split_stores

EVENTS_KEY = "scenario/events.json"
EMAIL_INDEXES = tuple(
    f"answer_keys/emails/emails_{lang}_index.csv" for lang in ("en_intl", "fr", "it", "ko")
)
SUFFIX_KINDS = {
    "dup": "duplicate",
    "corr": "correction",
    "fwd": "forward",
    "ooo": "noise",
}
KIND_GROUPS = {
    "dup": "duplicate",
    "duplicate": "duplicate",
    "correction": "correction",
    "closing+correction": "correction",
    "fwd": "forward",
    "forward": "forward",
    "forward_client": "forward",
    "ooo": "noise",
    "auto_reply": "noise",
    "misdirected": "noise",
    "misdirected_retraction": "noise",
    "closing_wrong_list": "noise",
}
CASE_DIRECTIONS = {"unmet_demand": "stockout"}
# Fixed before scoring: marketing context is not a demand/stock alert; `unknown` asks to verify.
CONTEXT_CASE_TYPES = frozenset({"customer_profile"})
SECONDS_PER_DAY = 86400


@dataclass(frozen=True)
class Unit:
    event_id: str
    event_type: str
    store_id: str
    start: datetime
    t_end: datetime
    store_wide: bool
    skus: frozenset[str]
    sizes: frozenset[str]
    direction: str | None


def catalog(root: Path) -> list[dict[str, str]]:
    with (root / ERP / "master_data/sku_colour.csv").open(encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


FILTER_FIELDS = {
    "styles": "style_name",
    "colors": "color_code",
    "lines": "line",
    "sgroups": "season_group",
    "seasons": "season",
}


def event_units(
    events: list[dict], stores: frozenset[str], start: date, end: date, root: Path
) -> list[Unit]:
    rows = catalog(root)
    units = []
    for event in events:
        first, last = (
            date.fromisoformat(event["start"]),
            date.fromisoformat(event["end"]),
        )
        if last < start or first > end:
            continue
        product = {k: set(v) for k, v in event["filter"].items() if k in FILTER_FIELDS}
        unknown = set(event["filter"]) - set(FILTER_FIELDS) - {"sizes"}
        if unknown:
            raise ValueError(f"Unsupported event filter in {event['id']}: {sorted(unknown)}")
        skus = frozenset(
            row["sku"]
            for row in rows
            if all(row[FILTER_FIELDS[k]] in values for k, values in product.items())
        )
        mult = event["demand_mult"]
        direction = "up" if mult > 1 else "down" if mult < 1 else None
        targets = stores if event["stores"] == ["ALL"] else stores & set(event["stores"])
        for store_id in sorted(targets):
            units.append(
                Unit(
                    event_id=event["id"],
                    event_type=event["type"],
                    store_id=store_id,
                    start=local_instant(root, store_id, max(first, start), time.min),
                    t_end=local_instant(
                        root,
                        store_id,
                        min(last, end) + timedelta(days=1),
                        time(23, 59, 59),
                    ),
                    store_wide=not product,
                    skus=skus,
                    sizes=frozenset(event["filter"].get("sizes", ())),
                    direction=direction,
                )
            )
    return units


def matches(alert: Alert, unit: Unit) -> bool:
    if alert.store_id != unit.store_id or not unit.start <= alert.at <= unit.t_end:
        return False
    if alert.direction and unit.direction and alert.direction != unit.direction:
        if not (alert.direction == "stockout" and unit.direction == "up"):
            return False
    if unit.store_wide:
        return alert.scope_level == "store"
    if not alert.skus & unit.skus:
        return False
    return not (alert.sizes and unit.sizes and not alert.sizes & unit.sizes)


def _instant(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value).astimezone(UTC) if value else None


def case_alerts(
    cases: list[dict], root: Path, start: date | None = None, end: date | None = None
) -> tuple[list[Alert], list[dict]]:
    """Exported cases (raw or fixture-wrapped) → pipeline alerts plus non-alert cases.

    Any status counts: a `verify` case with resolved scope is still in a human's queue.
    """
    rows = catalog(root)
    alerts, verify = [], []
    for record in cases:
        case = record.get("payload", record)
        store_id = case.get("store_id")
        if start is not None and end is not None and store_id:
            available_at = _instant(case.get("first_available_at"))
            if available_at is not None:
                period_start = local_instant(root, store_id, start, time.min)
                period_end = local_instant(root, store_id, end, time.max)
                if not period_start <= available_at <= period_end:
                    continue
        level, scope = case["scope_level"], case.get("scope_id")
        skus: frozenset[str] = frozenset()
        sizes: frozenset[str] = frozenset()
        if level in ("sku", "sku_size"):
            parts = scope.split("-")
            skus = frozenset({"-".join(parts[:2])})
            sizes = frozenset({"-".join(parts[2:])}) if level == "sku_size" else frozenset()
        elif level in ("style", "category"):
            field_name = "style_code" if level == "style" else "category"
            skus = frozenset(row["sku"] for row in rows if row[field_name] == scope)
        sources = tuple(
            ref["uri"].removeprefix("dataset://")
            for ref in case.get("source_refs", ())
            if ref["uri"].startswith("dataset://store_emails/")
        )
        alert = Alert(
            method="pipeline",
            store_id=case.get("store_id") or "",
            at=_instant(case["first_available_at"]),
            scope_level=level,
            skus=skus,
            sizes=sizes,
            direction=CASE_DIRECTIONS.get(case["case_type"]),
            ref=case["id"],
            decision_due_at=_instant(case.get("decision_due_at")),
            sources=sources,
        )
        if case["case_type"] in CONTEXT_CASE_TYPES:
            verify.append({"case": case["id"], "status": case["status"], "as": "context"})
        elif level == "unknown" or not alert.store_id or case["case_type"] == "unknown":
            verify.append({"case": case["id"], "status": case["status"], "as": "verify"})
        else:
            alerts.append(alert)
    return alerts, verify


def email_kinds(indexes: list[bytes]) -> dict[str, str]:
    """`store_emails/<STORE>/<file>` → answer-key kind, from the per-language indexes."""
    kinds = {}
    for data in indexes:
        for row in csv.DictReader(io.StringIO(data.decode("utf-8"))):
            kinds[f"store_emails/{row['store']}/{row['file']}"] = row["kind"]
    return kinds


def email_group(path: str, kinds: dict[str, str]) -> str:
    if path in kinds:
        return KIND_GROUPS.get(kinds[path], "original")
    suffix = Path(path).stem.rsplit("_", 1)[-1]
    return SUFFIX_KINDS.get(suffix, "original")


def _days(seconds: float) -> float:
    return round(seconds / SECONDS_PER_DAY, 2)


def _distribution(values: list[float]) -> dict:
    if not values:
        return {"n": 0}
    return {
        "n": len(values),
        "median": round(statistics.median(values), 2),
        "min": min(values),
        "max": max(values),
        "positive": sum(v > 0 for v in values),
        "zero": sum(v == 0 for v in values),
        "negative": sum(v < 0 for v in values),
    }


def false_alerts(alerts: list[Alert], units: list[Unit]) -> list[Alert]:
    by_store = defaultdict(list)
    for unit in units:
        by_store[unit.store_id].append(unit)
    return [a for a in alerts if not any(matches(a, u) for u in by_store[a.store_id])]


def score(alerts: dict[str, list[Alert]], units: list[Unit], store_days: int) -> dict:
    """Per-unit first alerts and the comparisons of the pipeline with each baseline."""
    rows = []
    for unit in units:
        row = {
            "event_id": unit.event_id,
            "event_type": unit.event_type,
            "store_id": unit.store_id,
            "t_end": unit.t_end.isoformat(),
        }
        for method, method_alerts in alerts.items():
            matched = sorted((a for a in method_alerts if matches(a, unit)), key=lambda a: a.at)
            row[method] = (
                {
                    "at": matched[0].at.isoformat(),
                    "ref": matched[0].ref,
                    "n_alerts": len(matched),
                }
                if matched
                else None
            )
            if method == "pipeline" and matched:
                due = matched[0].decision_due_at
                row["decision_margin_days"] = (
                    _days((due - matched[0].at).total_seconds()) if due else None
                )
        rows.append(row)
    summary = {"n_units": len(units), "n_events": len({u.event_id for u in units})}
    for method, method_alerts in alerts.items():
        wrong = false_alerts(method_alerts, units)
        summary[method] = {
            "units_detected": sum(row[method] is not None for row in rows),
            "not_detected_by_t_end": sum(row[method] is None for row in rows),
            "alerts": len(method_alerts),
            "false_alerts": len(wrong),
            "false_alerts_per_store_day": round(len(wrong) / store_days, 4) if store_days else None,
        }
    if "pipeline" in alerts:
        for baseline in (m for m in alerts if m != "pipeline"):
            leads, bounds, missed = [], [], 0
            for row in rows:
                pipe, base = row["pipeline"], row[baseline]
                if pipe is None:
                    missed += base is not None
                    continue
                t_pipe = datetime.fromisoformat(pipe["at"])
                if base is None:
                    bound = _days((datetime.fromisoformat(row["t_end"]) - t_pipe).total_seconds())
                    row[f"lead_vs_{baseline}_lower_bound_days"] = bound
                    bounds.append(bound)
                else:
                    lead = _days((datetime.fromisoformat(base["at"]) - t_pipe).total_seconds())
                    row[f"lead_vs_{baseline}_days"] = lead
                    leads.append(lead)
            summary[f"lead_vs_{baseline}"] = {
                "both_detected_days": _distribution(leads),
                "baseline_not_detected_lower_bound_days": _distribution(bounds),
                "only_baseline_detected": missed,
            }
        margins = [
            r["decision_margin_days"] for r in rows if r.get("decision_margin_days") is not None
        ]
        summary["decision_margin_days"] = _distribution(margins)
    return {"summary": summary, "units": rows}


def noise(pipeline: list[Alert], units: list[Unit], kinds: dict[str, str], cases: list[dict]):
    """Duplicates, corrections, forwards and noise mails behind the pipeline's cases."""
    wrong = {a.ref for a in false_alerts(pipeline, units)}
    by_group: dict[str, Counter] = defaultdict(Counter)
    only: Counter = Counter()
    for alert in pipeline:
        groups = {email_group(path, kinds) for path in alert.sources}
        outcome = "false" if alert.ref in wrong else "matched"
        for group in groups:
            by_group[group][outcome] += 1
        if len(groups) == 1:
            only[f"{groups.pop()}_{outcome}"] += 1
    fragmented = Counter()
    for unit in units:
        refs = {a.ref for a in pipeline if matches(a, unit)}
        if len(refs) > 1:
            fragmented[f"{unit.event_id}/{unit.store_id}"] = len(refs) - 1
    pipeline_refs = {alert.ref for alert in pipeline}
    payloads = [
        payload
        for record in cases
        if (payload := record.get("payload", record))["id"] in pipeline_refs
    ]
    return {
        "cases_citing_group": {g: dict(c) for g, c in sorted(by_group.items())},
        "cases_citing_only_group": dict(sorted(only.items())),
        "copies_folded_cases": sum(c["n_documents"] > c["n_origin_groups"] for c in payloads),
        "fragmented_units": dict(fragmented),
    }


PLACEBO_SHIFTS = (-21, -14, 14, 21)
BROAD_SKUS = 10


def breadth(unit: Unit) -> str:
    if unit.store_wide:
        return "store_wide"
    return "broad" if len(unit.skus) > BROAD_SKUS else "specific"


def placebo_units(units: list[Unit], start: date, end: date, root: Path) -> list[Unit]:
    """Move by local calendar weeks, inside the period and clear of all real store windows.

    Excluding every same-store event is conservative: a broad alert may span products from
    otherwise disjoint events. Controls can overlap each other; they are not replicates.
    """
    out = []
    for unit in units:
        zone = store_zones(root)[unit.store_id]
        low = local_instant(root, unit.store_id, start, time.min)
        high = local_instant(root, unit.store_id, end, time.max)
        for days in PLACEBO_SHIFTS:
            shift = timedelta(days=days)
            moved = replace(
                unit,
                start=(unit.start.astimezone(zone) + shift).astimezone(UTC),
                t_end=(unit.t_end.astimezone(zone) + shift).astimezone(UTC),
            )
            inside = low <= moved.start and moved.t_end <= high
            overlaps_real = any(
                real.store_id == unit.store_id
                and moved.start <= real.t_end
                and real.start <= moved.t_end
                for real in units
            )
            if inside and not overlaps_real:
                out.append(moved)
    return out


def chance_check(alerts: dict[str, list[Alert]], units: list[Unit], placebo: list[Unit]) -> dict:
    """Detection on real windows vs the same events at shifted windows, by event breadth.

    Raw counts are retained for auditing, but compare the paired real rate with the mean
    per-unit control rate. Otherwise ineligible units and unequal numbers of valid shifts
    change the event mix. This is descriptive, not a significance test or a causal null.
    """
    by_unit = defaultdict(list)
    for unit in placebo:
        by_unit[(unit.event_id, unit.store_id)].append(unit)
    result = {}
    for group in ("store_wide", "broad", "specific"):
        real = [u for u in units if breadth(u) == group]
        fake = [u for u in placebo if breadth(u) == group]
        result[group] = {}
        for method, found in alerts.items():
            paired, excluded = [], []
            for unit in real:
                key = {"event_id": unit.event_id, "store_id": unit.store_id}
                controls = by_unit[(unit.event_id, unit.store_id)]
                if not controls:
                    excluded.append(key)
                    continue
                paired.append(
                    key
                    | {
                        "real": any(matches(a, unit) for a in found),
                        "placebo": [
                            sum(any(matches(a, u) for a in found) for u in controls),
                            len(controls),
                        ],
                    }
                )
            result[group][method] = {
                "real": [sum(any(matches(a, u) for a in found) for u in real), len(real)],
                "placebo": [sum(any(matches(a, u) for a in found) for u in fake), len(fake)],
                "paired": {
                    "real": [sum(row["real"] for row in paired), len(paired)],
                    "placebo_rate": (
                        statistics.mean(row["placebo"][0] / row["placebo"][1] for row in paired)
                        if paired
                        else None
                    ),
                    "units": paired,
                },
                "excluded_no_placebo": excluded,
            }
    return result


def calibrate(
    grid: dict,
    pipeline_false_alerts: int,
    units: list[Unit],
    store_days: int,
    sensitivity_order: tuple[str, ...],
) -> dict:
    """Pick, per baseline, the most sensitive setting whose false-alert load ≤ the pipeline's."""
    table = []
    for setting, alerts in grid.items():
        wrong = len(false_alerts(alerts, units))
        detected = sum(any(matches(a, u) for a in alerts) for u in units)
        table.append(
            {
                "setting": setting,
                "alerts": len(alerts),
                "false_alerts": wrong,
                "false_alerts_per_store_day": round(wrong / store_days, 4),
                "units_detected": detected,
            }
        )
    eligible = [row for row in table if row["false_alerts"] <= pipeline_false_alerts]
    pick = next(
        (row for setting in sensitivity_order for row in eligible if row["setting"] == setting),
        None,
    )
    if pick is None:
        min_false_alerts = min(row["false_alerts"] for row in table)
        pick = next(
            row
            for setting in reversed(sensitivity_order)
            for row in table
            if row["setting"] == setting and row["false_alerts"] == min_false_alerts
        )
    return {
        "grid": table,
        "chosen": pick["setting"],
        "within_pipeline_load": bool(eligible),
    }


def load_events(data: bytes) -> list[dict]:
    return json.loads(data)["events"]


STOCK_GRID = (0, 1, 2)
SALES_GRID = (2.0, 3.0, 4.0, 5.0, 6.0)
DEFAULTS = {"stock": "threshold=0", "sales": "z=3.0"}


def lead_time_report(root: Path, run, split: str, start: date, end: date) -> dict:
    """Score a verified frozen run (or the baselines alone) on the run's stores."""
    oracle = root / "generated/ground_truth"

    def read(
        key: str,
    ) -> bytes:  # fixed keys only, through the run's checks when there is one
        return run.read_answer_key(oracle, key) if run else (oracle / key).read_bytes()

    if run is None:
        stores, cases = split_stores()[split], []
    else:
        protocol = run.manifest["protocol"]
        split, stores = protocol["split"], frozenset(protocol["stores"])
        cases = run.artifacts["cases"]
    events = load_events(read(EVENTS_KEY))
    units = event_units(events, stores, start, end, root)
    store_days = len(stores) * ((end - start).days + 1)
    grids = {
        "stock": {f"threshold={k}": stock_alerts(root, stores, start, end, k) for k in STOCK_GRID},
        "sales": {f"z={z}": sales_alerts(root, stores, start, end, z) for z in SALES_GRID},
    }
    alerts: dict[str, list[Alert]] = {}
    verify: list[dict] = []
    pipeline_false_alerts = None
    if run is not None:
        alerts["pipeline"], verify = case_alerts(cases, root, start, end)
        pipeline_false_alerts = len(false_alerts(alerts["pipeline"], units))
    calibration = {}
    for method, grid in grids.items():
        if run is not None and split == "dev":
            sensitivity_order = (
                tuple(f"threshold={value}" for value in sorted(STOCK_GRID, reverse=True))
                if method == "stock"
                else tuple(f"z={value}" for value in sorted(SALES_GRID))
            )
            calibration[method] = calibrate(
                grid, pipeline_false_alerts, units, store_days, sensitivity_order
            )
            calibration[method]["selection"] = "dev_false_alert_load"
        else:
            calibration[method] = {
                "chosen": DEFAULTS[method],
                "within_pipeline_load": None,
                "selection": "fixed_default",
            }
        alerts[method] = grid[calibration[method]["chosen"]]
    scored = score(alerts, units, store_days)
    for row, unit in zip(scored["units"], units, strict=True):
        row["breadth"] = breadth(unit)
    # The main score retains its existing next-evening ERP grace day. For the chance
    # comparison all methods must share the pipeline's within-period observation limit.
    chance_units = [
        replace(u, t_end=min(u.t_end, local_instant(root, u.store_id, end, time.max)))
        for u in units
    ]
    covered = {u.event_id for u in units}
    alert_refs = {a.ref for a in alerts.get("pipeline", [])}
    payloads = [record.get("payload", record) for record in cases]
    alert_types = [c["case_type"] for c in payloads if c["id"] in alert_refs]
    report = {
        "task": "EVL-04",
        "split": split,
        "stores": sorted(stores),
        "period": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "store_days": store_days,
        },
        "manifest_sha256": run.manifest_sha256 if run else None,
        "pipeline": "frozen_run" if run else "not_scored",
        "calibration": calibration,
        "summary": scored["summary"],
        "chance_check": chance_check(
            alerts, chance_units, placebo_units(chance_units, start, end, root)
        ),
        "non_alert_cases": dict(Counter(row["as"] for row in verify)),
        "pipeline_alerts_by_case_type": dict(Counter(alert_types)),
        "excluded_events": sorted(e["id"] for e in events if e["id"] not in covered),
        "units": scored["units"],
        "limits": [
            "False alerts are relative to planted events: real unplanned stock-outs and "
            "sales swings count as false.",
            "Pipeline time is the case's first_available_at as exported; a case whose scope "
            "was resolved later is credited from its first evidence.",
            "Units overlap in time and stores; they are not independent replicates.",
            "Chance check is descriptive: compare paired rates, not pooled raw counts. "
            "Similar rates do not prove coincidence; a gap does not establish significance. "
            "Calendar shifts may change seasonality, alert coverage and event context; "
            "excluded units may differ systematically from eligible ones.",
        ],
    }
    if run is not None:
        indexes = [read(key) for key in EMAIL_INDEXES]
        report["noise"] = noise(alerts["pipeline"], units, email_kinds(indexes), cases)
    return report
