"""Run-bound dashboard series; money is EUR at the dataset's budget FX convention."""

from datetime import date
from typing import Literal

from .common import Contract, Count, DerivedRecord, Instant, NonNegative

Region = Literal["EMEA", "AMERICAS", "APAC"]


class KpiDay(Contract):
    date: date
    store_id: str
    available_at: Instant
    sales_eur: float
    budget_eur: NonNegative
    receipts: Count
    visitors: NonNegative | None
    units: Count
    returns_units: Count


class MonthlyValue(Contract):
    sales: float
    ly: float
    budget: NonNegative


class MarketMonth(Contract):
    month: str
    partial_until: int | None
    regions: dict[Region, MonthlyValue]


class RegionSales(Contract):
    region: Region
    sales: float
    before: float
    ly: float


class CategorySales(Contract):
    category: str
    sales: float
    before: float
    ly: float
    units: Count


class SocialWeek(Contract):
    week: date
    pos: Count
    neu: Count
    neg: Count


class Hashtag(Contract):
    tag: str
    now: Count
    before: Count


class SocialSeries(Contract):
    weeks: tuple[SocialWeek, ...]
    hashtags: tuple[Hashtag, ...]
    posts: Count
    scope: Literal["global_listening"] = "global_listening"
    malformed_records: Count
    duplicates_removed: Count


class MarketSeries(Contract):
    last_day: date
    available_at: Instant
    monthly: tuple[MarketMonth, ...]
    regions: tuple[RegionSales, ...]
    categories: tuple[CategorySales, ...]
    social: SocialSeries
    stores: tuple[str, ...]
    notes: tuple[str, ...]


class BusinessSnapshot(DerivedRecord):
    kpi: tuple[KpiDay, ...]
    market: MarketSeries
