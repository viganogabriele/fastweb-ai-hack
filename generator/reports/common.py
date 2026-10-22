"""Shared helpers for the 'reports' area: data loading from internal sources, FX tables, calendars, aliases.

Every report script derives its numbers from generated/sources/erp/ and then applies the author's own
definitions (perimeter, FX, calendar, tax, returns treatment). Key computed figures are written to
generator/reports/_facts/<report>.json so that build_notes.py can write the answer key with exact numbers.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INT = ROOT / "generated" / "sources" / "erp"
OUT = ROOT / "generated" / "sources" / "reports"
GT = ROOT / "generated" / "ground_truth"
FACTS = Path(__file__).resolve().parent / "_facts"
FACTS.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / "generator"))

D = dt.date
TODAY = D(2026, 10, 22)
LAST = D(2026, 10, 21)

# ----------------------------------------------------------------------------------------------- FX
# local currency per 1 EUR
BUDGET_RATE = {"EUR": 1, "CHF": 0.95, "GBP": 0.85, "DKK": 7.46, "AED": 4.0, "USD": 1.08, "CAD": 1.48, "JPY": 162.0,
               "KRW": 1480.0, "CNY": 7.8, "HKD": 8.45, "TWD": 34.8, "SGD": 1.45, "AUD": 1.65}
# Actual rates are derived from the external FX sources (ECB reference rates; TWD/AED, which the ECB does not
# publish, from the USD-based commercial feed crossed via EUR). Monthly average = mean of available fixings.
EXT_FX = ROOT / "generated" / "sources" / "external" / "fx"
_CCY = ["USD", "JPY", "GBP", "CHF", "DKK", "CAD", "CNY", "HKD", "KRW", "SGD", "AUD"]


@lru_cache(None)
def _fx_daily() -> pd.DataFrame:
    e = pd.read_csv(EXT_FX / "ecb_reference" / "eurofxref-hist.csv")
    e["Date"] = pd.to_datetime(e.Date)
    e[_CCY] = e[_CCY].apply(pd.to_numeric, errors="coerce")
    e = e.set_index("Date")[_CCY]
    rows = []
    with open(EXT_FX / "fxfeed_usd_base" / "daily_snapshots.jsonl") as f:
        for line in f:
            j = json.loads(line)
            r = j["rates"]
            rows.append((pd.Timestamp(j["timestamp"][:10]), r["TWD"] / r["EUR"], r["AED"] / r["EUR"]))
    u = pd.DataFrame(rows, columns=["Date", "TWD", "AED"]).set_index("Date")
    u = u[u.index.dayofweek < 5]
    return e.join(u, how="outer")


def fx_avg(d0: dt.date, d1: dt.date) -> dict:
    x = _fx_daily()
    x = x[(x.index >= pd.Timestamp(d0)) & (x.index <= pd.Timestamp(d1))].mean()
    out = {c: round(float(x[c]), 4 if x[c] < 10 else 2) for c in x.index}
    out["EUR"] = 1.0
    return out


def fx_month(y: int, m: int, upto: dt.date | None = None) -> dict:
    d0 = dt.date(y, m, 1)
    d1 = (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1))
    if upto:
        d1 = min(d1, upto)
    return fx_avg(d0, d1)


FX_MONTHLY = {f"{y}-{m:02d}": fx_month(y, m) for y in (2025, 2026) for m in range(6, 11) if not (y == 2026 and m > 10)}
# full-year 2025 average ("constant FX" used by APAC and by the Board deck)
FX_AVG_2025 = fx_avg(dt.date(2025, 1, 1), dt.date(2025, 12, 31))

VAT = {"IT": .22, "FR": .20, "DE": .19, "CH": .081, "ES": .21, "NL": .21, "DK": .25, "GB": .20, "AE": .05, "JP": .10,
       "KR": .10, "CN": .13, "HK": 0.0, "TW": .05, "SG": .09, "AU": .10, "US": 0.0, "CA": 0.0}

# ----------------------------------------------------------------------------------------------- aliases
SAP_PLANT = {  # Retail Controlling uses SAP plant codes
    "MIL01": "1001", "MIL02": "1002", "ROM01": "1004", "VEN01": "1006", "COU01": "1011", "CRT01": "1012",
    "PAR01": "1101", "PAR02": "1102", "CAN01": "1105", "GVA01": "1201", "ZRH01": "1202", "STM01": "1205",
    "LON01": "1301", "LON02": "1302", "MUN01": "1401", "BER01": "1402", "MAD01": "1501", "AMS01": "1601",
    "CPH01": "1701", "DXB01": "1801", "NYC01": "2001", "NYC02": "2002", "MIA01": "2003", "BHS01": "2005",
    "ASP01": "2007", "TOR01": "2101", "TYO01": "3001", "TYO02": "3002", "OSA01": "3003", "SEL01": "3101",
    "SEL02": "3102", "BUS01": "3103", "SHA01": "3201", "BJS01": "3202", "CDU01": "3203", "HKG01": "3301",
    "TPE01": "3401", "SIN01": "3501", "SYD01": "3601"}
SHOP_IN_SHOP = ["MIL02", "PAR02", "LON02", "BER01", "SEL02", "BUS01"]
RESORT = ["COU01", "CRT01", "STM01", "ASP01"]
FW26_NEW = ["ILVARO", "AMBRINE", "ARNEB", "ROSIERE", "WOOL TURTLENECK", "POLARIS CAPE", "POLARIS OVERSIZED", "POLARIS BALACLAVA"]


# ----------------------------------------------------------------------------------------------- loading
@lru_cache(None)
def stores() -> pd.DataFrame:
    return pd.read_csv(INT / "master_data" / "stores.csv", keep_default_na=False)


@lru_cache(None)
def skus() -> pd.DataFrame:
    return pd.read_csv(INT / "master_data" / "sku_colour.csv", dtype={"color_code": str}, keep_default_na=False)


@lru_cache(None)
def prices() -> pd.DataFrame:
    return pd.read_csv(INT / "master_data" / "price_list_FW26.csv")


@lru_cache(None)
def daily() -> pd.DataFrame:
    """daily store x sku sales for Jun-Nov 2025 and Jun-Oct 2026, enriched."""
    fs = []
    for y, ms in ((2025, range(6, 12)), (2026, range(6, 11))):
        for m in ms:
            fs.append(pd.read_csv(INT / "sales" / "daily_store_sku" / f"sales_daily_{y}_{m:02d}.csv"))
    df = pd.concat(fs, ignore_index=True)
    df["date"] = pd.to_datetime(df.business_date).dt.date
    df["sales_before_returns_lc"] = df.gross_sales_lc - df.discount_lc
    df = df.merge(skus()[["sku", "style_name", "color_code", "color_name_en", "category", "subcategory", "line",
                          "season", "gender", "season_group"]], on="sku", how="left")
    st = stores()[["store_id", "region", "subregion", "country", "country_code", "store_type"]]
    return df.merge(st, on="store_id", how="left")


@lru_cache(None)
def kpi() -> pd.DataFrame:
    k = pd.read_csv(INT / "kpi" / "store_daily_kpi.csv")
    k["date"] = pd.to_datetime(k.business_date).dt.date
    st = stores()[["store_id", "region", "subregion", "country", "country_code", "store_type", "store_name"]]
    return k.merge(st, on="store_id", how="left")


@lru_cache(None)
def pos() -> pd.DataFrame:
    fs = sorted((INT / "sales" / "pos_lines").glob("pos_lines_2026-W*.csv"))
    p = pd.concat([pd.read_csv(f, dtype={"size": str, "customer_nationality": str}, keep_default_na=False) for f in fs],
                  ignore_index=True)
    p["date"] = pd.to_datetime(p.business_date).dt.date
    p = p.merge(skus()[["sku", "style_name", "color_code", "category"]], on="sku", how="left")
    st = stores()[["store_id", "region", "subregion", "country", "country_code"]]
    return p.merge(st, on="store_id", how="left")


@lru_cache(None)
def stock(day: dt.date) -> pd.DataFrame:
    s = pd.read_csv(INT / "inventory" / "store_stock_daily" / f"stock_eod_{day.isoformat()}.csv", dtype={"size": str})
    return s.merge(skus()[["sku", "style_name", "color_code", "category"]], on="sku", how="left")


@lru_cache(None)
def shipments() -> pd.DataFrame:
    rows = []
    with open(INT / "logistics" / "shipments_dc_to_store.jsonl") as f:
        for line in f:
            s = json.loads(line)
            for ln in s["lines"]:
                rows.append(dict(shipment_id=s["shipment_id"], store_id=s["store_id"], ship_date=s["ship_date"],
                                 planned=s["planned_arrival"], arrival=s["actual_arrival"], status=s["status"],
                                 sku=ln.get("sku_received", ln["sku"]), sku_ordered=ln["sku"],
                                 size=ln.get("size_received", ln["size"]), qty=ln["qty_shipped"]))
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------------------------- calc helpers
def sel(df, d0, d1, stores_=None, col="date"):
    m = (df[col] >= d0) & (df[col] <= d1)
    if stores_ is not None:
        m &= df.store_id.isin(list(stores_))
    return df[m]


def ly(d: dt.date) -> dt.date:
    """same weekday last year (364 days)"""
    return d - dt.timedelta(days=364)


def iso_week_range(year, week):
    d0 = dt.date.fromisocalendar(year, week, 1)
    return d0, d0 + dt.timedelta(days=6)


def ccy_of(store_id):
    return stores().set_index("store_id").currency[store_id]


def to_eur(df, value_col, rate: dict, ccy_col="currency"):
    return df[value_col] / df[ccy_col].map(rate)


def fx_month_rate(d: dt.date):
    return FX_MONTHLY[f"{d.year}-{d.month:02d}"]


def to_eur_monthly(df, value_col, date_col="date", ccy_col="currency"):
    keys = df[date_col].map(lambda x: f"{x.year}-{x.month:02d}")
    r = [FX_MONTHLY[k][c] for k, c in zip(keys, df[ccy_col])]
    return df[value_col] / np.array(r, dtype=float)


def pct(a, b):
    if b is None or b == 0 or pd.isna(b):
        return np.nan
    return (a / b - 1) * 100


def open_days(store_id, d0, d1):
    k = kpi()
    return int(((k.store_id == store_id) & (k.date >= d0) & (k.date <= d1)).sum())


# ----------------------------------------------------------------------------------------------- calendars
def nrf_month(fy_month_start: dt.date, weeks: int):
    return fy_month_start, fy_month_start + dt.timedelta(days=7 * weeks - 1)


# NRF 4-5-4: FY2026 starts Sun 2026-02-01, FY2025 starts Sun 2025-02-02
NRF_2026 = {"P07 Aug": (D(2026, 8, 2), D(2026, 8, 29)), "P08 Sep": (D(2026, 8, 30), D(2026, 10, 3)),
            "P09 Oct": (D(2026, 10, 4), D(2026, 10, 31))}
NRF_2025 = {"P07 Aug": (D(2025, 8, 3), D(2025, 8, 30)), "P08 Sep": (D(2025, 8, 31), D(2025, 10, 4)),
            "P09 Oct": (D(2025, 10, 5), D(2025, 11, 1))}


# ----------------------------------------------------------------------------------------------- facts
class Facts(dict):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def save(self):
        def conv(o):
            if isinstance(o, (np.integer,)):
                return int(o)
            if isinstance(o, (np.floating,)):
                return float(o)
            if isinstance(o, (dt.date,)):
                return o.isoformat()
            if isinstance(o, pd.Series):
                return o.to_dict()
            raise TypeError(type(o))
        (FACTS / f"{self.name}.json").write_text(json.dumps(self, indent=1, ensure_ascii=False, default=conv))


def outdir(*parts) -> Path:
    p = OUT.joinpath(*parts)
    p.mkdir(parents=True, exist_ok=True)
    return p


def r1(x):
    return None if x is None or pd.isna(x) else round(float(x), 1)
