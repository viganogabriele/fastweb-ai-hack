"""EVL-03: fixed-universe daily forecast errors from verified frozen exports only.

No product imports. Actual demand is read only after validating frozen choices and
predictions; missing targets never become zeros or selectively shorter horizons.
"""

import csv
import io
import math
from collections import Counter, defaultdict
from datetime import date, timedelta
from zoneinfo import ZoneInfo

from .harness import FrozenRun, _timestamp, digest

HORIZONS = (1, 3, 7)
KEY = "demand/true_demand_window.csv"


def number(value):
    if isinstance(value, bool):
        raise ValueError("Demand and forecast values must be finite nonnegative numbers")
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise ValueError("Demand and forecast values must be finite nonnegative numbers") from None
    if not math.isfinite(result) or result < 0:
        raise ValueError("Demand and forecast values must be finite nonnegative numbers")
    return result


def metrics(actual, predicted):
    errors = [abs(y - f) for y, f in zip(actual, predicted, strict=True)]
    volume, error = math.fsum(actual), math.fsum(errors)
    return {
        "n_days": len(actual),
        "actual_units": volume,
        "forecast_units": math.fsum(predicted),
        "absolute_error_units": error,
        "mae": error / len(actual) if actual else None,
        "wape": error / volume if volume else None,
    }


def choices(protocol):
    config = protocol.get("forecast", {})
    if config.get("scenario") not in {"low", "base", "high"}:
        raise ValueError("Freeze forecast.scenario as low, base or high before scoring")
    if config.get("scenario_id") != "historical":
        raise ValueError("Forecast scoring requires forecast.scenario_id=historical")
    origins = [_timestamp(origin) for origin in protocol["origins"]]
    if len(set(origins)) != len(origins):
        raise ValueError("Duplicate temporal origins")
    universe = {}
    for item in protocol["universe"]:
        key = (item["store_id"], item["sku"])
        if key in universe:
            raise ValueError("Duplicate store/SKU in preselected universe")
        if not item.get("timezone"):
            raise ValueError("Freeze a timezone for every universe item")
        universe[key] = ZoneInfo(item["timezone"])
    return config["scenario"], origins, universe


def predictions(rows, origins, universe):
    baselines, overlays = {}, defaultdict(list)
    ignored = 0
    for row in rows:
        payload = row.get("payload", row)
        producer = payload.get("producer")
        if producer not in {"fc.baseline", "fc.overlay"}:
            ignored += 1
            continue
        origin = _timestamp(row.get("as_of", payload.get("computed_at", "")))
        pair = (payload["store_id"], payload["sku"])
        if origin not in origins or pair not in universe:
            ignored += 1
            continue
        if payload.get("scenario_id") != "historical":
            raise ValueError("Synthetic extensions and nonhistorical scenarios cannot enter WAPE")
        if not payload.get("available_at") or _timestamp(payload["available_at"]) > origin:
            raise ValueError(
                "Forecast input availability exceeds its temporal origin or is unknown"
            )
        if payload.get("status") not in {"computed", "unchanged", "not_estimable"}:
            raise ValueError("Unknown forecast status")
        points = {}
        for point in payload["series"]:
            day = date.fromisoformat(point["date"])
            if day in points:
                raise ValueError("Duplicate forecast day")
            points[day] = point
        value = {**payload, "points": points}
        key = (origin, *pair)
        if producer == "fc.baseline":
            if key in baselines:
                raise ValueError("Duplicate baseline for a fixed origin/store/SKU")
            baselines[key] = value
        else:
            overlays[key].append(value)
    if any(sum(p["status"] == "computed" for p in group) > 1 for group in overlays.values()):
        raise ValueError("Multiple computed overlays: freeze one information-consistent forecast")
    return baselines, overlays, ignored


def targets(data, universe):
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig")))
    if not {"date", "store_id", "sku", "demand_units"} <= set(reader.fieldnames or ()):
        raise ValueError("Demand oracle requires date, store_id, sku and demand_units")
    found, seen = {}, set()
    for row in reader:
        pair = (row["store_id"], row["sku"])
        if pair not in universe:
            continue
        key = (*pair, date.fromisoformat(row["date"]))
        if key in seen:
            raise ValueError("Duplicate daily store/SKU target")
        seen.add(key)
        if row["demand_units"].strip():
            found[key] = number(row["demand_units"])
    return found


def score_forecasts(run: FrozenRun, oracle_root, key=KEY):
    """H=1/3/7 daily MAE/WAPE on the identical mature, baseline-estimable sample.

    Unchanged/not-estimable overlays and no-alert products use the baseline; missing
    baselines or incomplete computed overlays are explicitly unscorable. Coverage
    and all missing predictions/targets are reported without shrinking the universe.
    """
    scenario, origins, universe = choices(run.manifest["protocol"])
    baselines, overlays, ignored = predictions(run.artifacts["predictions"], origins, universe)
    data = run.read_answer_key(oracle_root, key)
    actuals = targets(data, universe)
    report = {}
    for horizon in HORIZONS:
        actual, baseline_values, selected = [], [], []
        counts = Counter(eligible_origins=len(origins) * len(universe))
        details = []
        for origin in origins:
            for (store, sku), timezone in universe.items():
                start = origin.astimezone(timezone).date() + timedelta(days=1)
                days = [start + timedelta(days=i) for i in range(horizon)]
                missing = [day.isoformat() for day in days if (store, sku, day) not in actuals]
                context = {"origin": origin.isoformat(), "store_id": store, "sku": sku}
                if missing:
                    counts["pending_origins"] += 1
                    details.append({**context, "status": "pending", "missing_dates": missing})
                    continue
                counts["mature_origins"] += 1
                identity = (origin, store, sku)
                base = baselines.get(identity, {}).get("points", {})
                if any(base.get(day, {}).get("baseline") is None for day in days):
                    counts["unscorable_origins"] += 1
                    details.append(
                        {**context, "status": "unscorable", "reason": "missing_baseline"}
                    )
                    continue
                base_values = [number(base[day]["baseline"]) for day in days]
                group = overlays.get(identity, [])
                computed = next((p for p in group if p["status"] == "computed"), None)
                if computed:
                    if computed.get("baseline_ref") != baselines[identity].get("baseline_ref"):
                        raise ValueError("Overlay and frozen baseline vintage disagree")
                    points = computed["points"]
                    if any(
                        (points.get(day, {}).get("latent") or {}).get(scenario) is None
                        for day in days
                    ):
                        counts["unscorable_origins"] += 1
                        details.append(
                            {**context, "status": "unscorable", "reason": "incomplete_overlay"}
                        )
                        continue
                    corrected = [number(points[day]["latent"][scenario]) for day in days]
                    # The comparison must use the baseline the overlay actually references.
                    if any(points[day].get("baseline") != base[day]["baseline"] for day in days):
                        raise ValueError("Overlay and frozen baseline disagree")
                    counts["adjusted_origins"] += 1
                else:
                    corrected = base_values
                    counts["abstained_origins" if group else "no_alert_origins"] += 1
                counts["scored_origins"] += 1
                actual.extend(actuals[(store, sku, day)] for day in days)
                baseline_values.extend(base_values)
                selected.extend(corrected)
        summary = {
            name: counts[name]
            for name in (
                "eligible_origins",
                "mature_origins",
                "pending_origins",
                "unscorable_origins",
                "scored_origins",
                "adjusted_origins",
                "abstained_origins",
                "no_alert_origins",
            )
        }
        report[str(horizon)] = {
            **summary,
            "prediction_coverage": counts["scored_origins"] / counts["mature_origins"]
            if counts["mature_origins"]
            else None,
            "adjustment_coverage": counts["adjusted_origins"] / counts["scored_origins"]
            if counts["scored_origins"]
            else None,
            "baseline": metrics(actual, baseline_values),
            "selected": metrics(actual, selected),
            "details": details,
        }
    return {
        "status": "scored",
        "manifest_sha256": run.manifest_sha256,
        "protocol": run.manifest["protocol"],
        "answer_key": {"path": key, "sha256": digest(data)},
        "target": "demand_units",
        "forecast_quantity": "latent",
        "scenario": scenario,
        "ignored_prediction_records": ignored,
        "horizons": report,
    }
