"""Freeze the overview's business series from source rows known at the run cutoff.

KPI amounts use the source's net_sales_eur_bud. Budget and SKU amounts use the
same store-day's implied budget FX; a median of already available observations
is used only on zero-sales days. Social is global context, never a demand input.
"""

import calendar
import csv
import hashlib
import json
import re
from collections import defaultdict
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from statistics import median
from zoneinfo import ZoneInfo

from tesseract.core.config import get_settings
from tesseract.core.contracts import BusinessSnapshot, ModuleManifest, ModuleResult, SourceRef
from tesseract.core.contracts.business import KpiDay, MarketSeries, SocialSeries

REGIONS = ("EMEA", "AMERICAS", "APAC")
KPI = "erp/kpi/store_daily_kpi.csv"
SOCIAL = "external/social/pulsewire"
SALES = "erp/sales/daily_store_sku"
MANIFEST = ModuleManifest(
    id="src.business",
    version="1",
    layer="sources",
    description="Frozen KPI, regional/category sales and deduplicated global social context",
    requires=("src.erp",),
    optional_inputs=(),
    produces=("BusinessSnapshot",),
    enabled=True,
    mode="live",
    params_schema={"type": "object", "properties": {}, "additionalProperties": False},
)


def csv_rows(root, relative, refs):
    path = root / relative
    refs[relative] = SourceRef(
        uri="dataset://" + relative,
        content_hash="sha256:" + hashlib.sha256(path.read_bytes()).hexdigest(),
    )
    with path.open(encoding="utf-8", newline="") as stream:
        yield from csv.DictReader(stream)


def available(row, zone):
    day = date.fromisoformat(row["business_date"])
    result = datetime.combine(day + timedelta(days=1), time(6), ZoneInfo(zone))
    for key in ("posted_at", "available_at"):
        if row.get(key):
            instant = datetime.fromisoformat(row[key])
            if instant.utcoffset() is None:
                raise ValueError(f"naive {key}")
            result = max(result, instant)
    if row.get("posting_date"):
        result = max(
            result,
            datetime.combine(date.fromisoformat(row["posting_date"]), time(6), ZoneInfo(zone)),
        )
    return result.astimezone(UTC)


def unique(rows, key):
    found = {}
    for row in rows:
        identity = tuple(row[field] for field in key)
        if identity in found and found[identity] != row:
            raise ValueError(f"conflicting source rows: {identity}")
        found[identity] = row
    return list(found.values())


def social_series(root, as_of, end, refs):
    posts, malformed, duplicates = {}, 0, 0
    for path in sorted((root / SOCIAL).glob("*.jsonl")):
        raw = path.read_bytes()
        relative = path.relative_to(root).as_posix()
        refs[relative] = SourceRef(
            uri="dataset://" + relative, content_hash="sha256:" + hashlib.sha256(raw).hexdigest()
        )
        for chunk in re.split(r'(?=\{"doc_id"\s*:)', raw.decode("utf-8")):
            if not chunk.strip():
                continue
            try:
                post = json.loads(chunk, strict=False)
                published = datetime.fromisoformat(post["published_at"])
                collected = datetime.fromisoformat(post["collected_at"])
                if published.utcoffset() is None or collected.utcoffset() is None:
                    raise ValueError("naive social timestamp")
                identity = post["doc_id"]
                if max(published, collected) > as_of or published.date() > end:
                    continue
                label = post["sentiment"]
                label = label["label"] if isinstance(label, dict) else label
                sentiment = {"positive": "pos", "negative": "neg", "neutral": "neu"}.get(
                    label, label
                )
                if sentiment not in {"pos", "neu", "neg"}:
                    raise ValueError("unknown sentiment")
                tags = {str(tag).casefold().removeprefix("#") for tag in post["hashtags"]}
            except (ValueError, KeyError, TypeError):
                malformed += 1
                continue
            if identity in posts:
                duplicates += 1
                if collected <= posts[identity][0]:
                    continue
            posts[identity] = (collected, published.date(), sentiment, tags)
    weeks, tags = {}, {}
    for _, day, sentiment, hashtags in posts.values():
        monday = (day - timedelta(days=day.weekday())).isoformat()
        weeks.setdefault(monday, dict(week=monday, pos=0, neu=0, neg=0))[sentiment] += 1
        age = (end - day).days
        bucket = "now" if 0 <= age < 14 else "before" if 14 <= age < 28 else None
        if bucket:
            for tag in hashtags:
                tags.setdefault(tag, dict(tag=tag, now=0, before=0))[bucket] += 1
    return SocialSeries(
        weeks=tuple(weeks[key] for key in sorted(weeks)),
        hashtags=tuple(
            sorted(tags.values(), key=lambda r: (-(r["now"] - r["before"]), r["tag"]))[:10]
        ),
        posts=len(posts),
        malformed_records=malformed,
        duplicates_removed=duplicates,
    )


def project(root: Path, stores: tuple[str, ...], as_of: datetime):
    refs = {}
    master = {
        r["store_id"]: r
        for r in csv_rows(root, "erp/master_data/stores.csv", refs)
        if r["store_id"] in stores
    }
    if master.keys() != set(stores):
        raise ValueError("unknown store in business snapshot")
    rows = unique(
        (
            r
            for r in csv_rows(root, KPI, refs)
            if r["store_id"] in master and available(r, master[r["store_id"]]["timezone"]) <= as_of
        ),
        ("store_id", "business_date"),
    )
    if not rows:
        raise ValueError("no available KPI rows")
    # Compare the same business days across all stores, including opposite time zones.
    latest = {
        store: max(r["business_date"] for r in rows if r["store_id"] == store) for store in stores
    }
    end = date.fromisoformat(min(latest.values()))
    rows = [r for r in rows if r["business_date"] <= end.isoformat()]
    rates = defaultdict(list)
    for row in rows:
        if Decimal(row["net_sales_lc"]):
            rates[row["currency"]].append(
                Decimal(row["net_sales_eur_bud"]) / Decimal(row["net_sales_lc"])
            )
    rates = {currency: median(values) for currency, values in rates.items()}

    def rate(row):
        local = Decimal(row["net_sales_lc"])
        return Decimal(row["net_sales_eur_bud"]) / local if local else rates[row["currency"]]

    kpi = tuple(
        KpiDay(
            date=row["business_date"],
            store_id=row["store_id"],
            available_at=available(row, master[row["store_id"]]["timezone"]),
            sales_eur=float(row["net_sales_eur_bud"]),
            budget_eur=round(Decimal(row["budget_lc"]) * rate(row), 2),
            receipts=int(row["receipts"]),
            visitors=float(row["visitors_in"]) if row["visitors_in"] else None,
            units=int(row["units"]),
            returns_units=int(row["returns_units"]),
        )
        for row in sorted(rows, key=lambda r: (r["business_date"], r["store_id"]))
        if date.fromisoformat(row["business_date"]) >= end - timedelta(days=119)
    )
    months = []
    for offset in range(11, -1, -1):
        number = end.year * 12 + end.month - 1 - offset
        year, month = divmod(number, 12)
        month += 1
        current = f"{year:04d}-{month:02d}"
        previous = f"{year - 1:04d}-{month:02d}"
        partial = end.day if offset == 0 and end.day < calendar.monthrange(year, month)[1] else None
        values = {r: {k: Decimal(0) for k in ("sales", "ly", "budget")} for r in REGIONS}
        for row in rows:
            day = row["business_date"]
            if partial and int(day[-2:]) > partial:
                continue
            value = values[master[row["store_id"]]["region"]]
            if day.startswith(current):
                value["sales"] += Decimal(row["net_sales_eur_bud"])
                value["budget"] += Decimal(row["budget_lc"]) * rate(row)
            elif day.startswith(previous):
                value["ly"] += Decimal(row["net_sales_eur_bud"])
        months.append(
            dict(
                month=current,
                partial_until=partial,
                regions={
                    r: {k: round(v, 2) for k, v in amounts.items()} for r, amounts in values.items()
                },
            )
        )

    def bucket(day):
        age = (end - day).days
        return (
            "sales"
            if 0 <= age < 28
            else "before"
            if 28 <= age < 56
            else "ly"
            if 364 <= age < 392
            else None
        )

    regions = {
        r: dict(region=r, sales=Decimal(0), before=Decimal(0), ly=Decimal(0)) for r in REGIONS
    }
    by_day = {(r["store_id"], r["business_date"]): r for r in rows}
    for row in rows:
        slot = bucket(date.fromisoformat(row["business_date"]))
        if slot:
            regions[master[row["store_id"]]["region"]][slot] += Decimal(row["net_sales_eur_bud"])
    category_of = {
        r["sku"]: r["category"] for r in csv_rows(root, "erp/master_data/sku_colour.csv", refs)
    }
    categories = {}
    for path in sorted((root / SALES).glob("sales_daily_*.csv")):
        year, month = map(int, path.stem.removeprefix("sales_daily_").split("_"))
        first = date(year, month, 1)
        last = date(year, month, calendar.monthrange(year, month)[1])
        windows = (
            (end - timedelta(days=55), end),
            (end - timedelta(days=391), end - timedelta(days=364)),
        )
        if not any(first <= b and last >= a for a, b in windows):
            continue
        selected = unique(
            (
                r
                for r in csv_rows(root, path.relative_to(root).as_posix(), refs)
                if r["store_id"] in master
                and bucket(date.fromisoformat(r["business_date"]))
                and available(r, master[r["store_id"]]["timezone"]) <= as_of
            ),
            ("store_id", "business_date", "sku"),
        )
        for row in selected:
            slot = bucket(date.fromisoformat(row["business_date"]))
            category = category_of[row["sku"]]
            value = categories.setdefault(
                category,
                dict(
                    category=category, sales=Decimal(0), before=Decimal(0), ly=Decimal(0), units=0
                ),
            )
            day_kpi = by_day.get((row["store_id"], row["business_date"]))
            fx = rate(day_kpi) if day_kpi else rates[row["currency"]]
            value[slot] += Decimal(row["net_sales_lc"]) * fx
            if slot == "sales":
                value["units"] += int(row["units_sold"])

    def rounded(record):
        return {k: round(v, 2) if isinstance(v, Decimal) else v for k, v in record.items()}

    market = MarketSeries(
        last_day=end,
        available_at=max(day.available_at for day in kpi),
        monthly=tuple(months),
        regions=tuple(rounded(r) for r in regions.values()),
        categories=tuple(
            rounded(r)
            for r in sorted(categories.values(), key=lambda r: (-r["sales"], r["category"]))
        ),
        social=social_series(root, as_of, end, refs),
        stores=stores,
        notes=(
            "Net EUR sales at budget FX; budget and categories use the store-day implied FX "
            "(median known FX on zero-sales days).",
            "28-day comparisons: previous 28 days and matching weekdays 364 days earlier; "
            "monthly LY uses matching calendar days.",
            "Social is global, machine-labelled context; malformed records are excluded "
            "and latest known collections deduplicated by doc_id.",
            "KPI and SKU exports are distinct source series; discrepancies are retained, "
            "never scaled to force reconciliation.",
        ),
    )
    return kpi, market, tuple(refs[key] for key in sorted(refs))


def run(ctx):
    kpi, market, refs = project(get_settings().sources_dir, ctx.spec.stores, ctx.spec.as_of)
    payload = dict(kpi=kpi, market=market)
    fingerprint = hashlib.sha256(market.model_dump_json().encode()).hexdigest()[:16]
    ctx.repo.put(
        BusinessSnapshot(
            id="business",
            version=fingerprint,
            available_at=ctx.spec.as_of,
            availability_basis="filtered_source_rows_at_run_cutoff",
            source_refs=refs,
            run_id=ctx.spec.run_id,
            scenario_id=ctx.spec.scenario_id,
            computed_at=ctx.spec.as_of,
            input_refs=(),
            producer=MANIFEST.id,
            producer_version=MANIFEST.version,
            **payload,
        )
    )
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="succeeded",
        counts={
            "kpi_days": len(kpi),
            "social_posts": market.social.posts,
            "social_duplicates_removed": market.social.duplicates_removed,
            "social_malformed_excluded": market.social.malformed_records,
        },
        errors=(),
        abstentions=(),
    )
