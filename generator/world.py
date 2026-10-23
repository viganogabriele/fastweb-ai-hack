"""Synthetic world simulator: demand -> sales, size-level inventory, shipments, POS lines, traffic, KPI, forecast.

Run:  .venv/bin/python generator/world.py
Writes internal sources under generated/sources/erp and ground truth under generated/ground_truth.
"""
import datetime as dt
import json
import math
import os
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from config import *  # noqa
from events import EVENTS, DC_CONSTRAINTS, STOCK_CAPS, CLOSURES

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "generated" / "sources"
INT = SRC / "erp"
GT = ROOT / "generated" / "ground_truth"
rng = np.random.default_rng(20261022)

D_END_BASE = dt.date(2026, 12, 31)  # baseline lambda horizon (for forecasts)


def d(s):
    return dt.date.fromisoformat(s) if isinstance(s, str) else s


def mkdir(p):
    p.mkdir(parents=True, exist_ok=True)
    return p


# ---------------------------------------------------------------- master data
stores = pd.DataFrame(STORES, columns=STORE_COLS)
S = len(stores)
sid = {s: i for i, s in enumerate(stores.store_id)}
styles = pd.DataFrame(STYLES, columns=STYLE_COLS)

sku_rows = []
for _, st in styles.iterrows():
    for c in st.colors:
        sku_rows.append(dict(sku=f"{st.style_code}-{c}", style_code=st.style_code, style_name=st.style_name,
                             color_code=c, color_name_it=COLORS[c][0], color_name_en=COLORS[c][1], line=st.line,
                             category=st.category, subcategory=st.subcategory, gender=st.gender, season=st.season,
                             launch_date=st.launch_date if isinstance(st.launch_date, str) else "",
                             end_date=st.end_date if isinstance(st.end_date, str) else "", price_eur=st.price_eur,
                             size_run=st.size_run, popularity=st.popularity, season_group=st.season_group))
skus = pd.DataFrame(sku_rows)
K = len(skus)
kid = {k: i for i, k in enumerate(skus.sku)}
# colour popularity tweaks
COLOR_POP = {"999": 1.6, "742": 1.0, "20D": 0.8, "034": 0.75, "510": 0.55, "82D": 0.55, "90X": 0.6, "23R": 0.6,
             "41F": 0.4, "73A": 0.45, "001": 0.8}
sku_pop = np.array([r.popularity * COLOR_POP[r.color_code] for r in skus.itertuples()])

dates_all = pd.date_range(START, D_END_BASE).date
DA = len(dates_all)
dates = pd.date_range(START, END).date
D = len(dates)
didx = {x: i for i, x in enumerate(dates_all)}
W0 = didx[WINDOW_START]

# ---------------------------------------------------------------- seasonality
CURVES = {
    "N": {"HEAVY": [1.25, .85, .45, .22, .12, .10, .12, .30, .65, 1.05, 1.55, 1.95],
          "MID": [1.05, .85, .80, .75, .65, .55, .55, .70, .95, 1.10, 1.25, 1.55],
          "LIGHT": [.40, .45, .85, 1.15, 1.40, 1.55, 1.45, 1.05, .75, .55, .45, .60]},
    "T": {"HEAVY": [.75, .55, .45, .35, .30, .35, .45, .45, .55, .75, .95, 1.05],
          "MID": [1.0, .9, .9, .85, .85, .85, .9, .9, .95, 1.0, 1.05, 1.15],
          "LIGHT": [1.0, 1.0, 1.05, 1.05, 1.05, 1.05, 1.05, 1.0, 1.0, 1.0, .95, 1.0]},
}
CURVES["S"] = {g: v[6:] + v[:6] for g, v in CURVES["N"].items()}
RESORT_CURVE = [2.2, 2.4, 1.8, .6, .2, .5, .9, .9, .4, .4, .7, 2.6]
GROUPS = ["HEAVY", "MID", "LIGHT"]
HEMIS = ["N", "S", "T"]


def interp_curve(vals, day):
    pos = (day.timetuple().tm_yday - 15.2) / 30.44
    i0 = math.floor(pos) % 12
    f = pos - math.floor(pos)
    return vals[i0] * (1 - f) + vals[(i0 + 1) % 12] * f


season_arr = np.zeros((DA, 3, 3), dtype=np.float32)
resort_arr = np.zeros(DA, dtype=np.float32)
for i, x in enumerate(dates_all):
    for h, hemi in enumerate(HEMIS):
        for g, grp in enumerate(GROUPS):
            season_arr[i, h, g] = interp_curve(CURVES[hemi][grp], x)
    resort_arr[i] = interp_curve(RESORT_CURVE, x)

hemi_idx = np.array([HEMIS.index(h) for h in stores.hemi])
grp_idx = np.array([GROUPS.index(g) for g in skus.season_group])

# ---------------------------------------------------------------- lifecycle
life = np.zeros((DA, K), dtype=np.float32)
for k, r in enumerate(skus.itertuples()):
    ld = d(r.launch_date) if r.launch_date else None
    ed = d(r.end_date) if r.end_date else None
    for i, x in enumerate(dates_all):
        if ld and x < ld:
            continue
        if ed and x > ed:
            continue
        v = 1.0
        if ld:
            age = (x - ld).days
            v *= 1.0 + 0.35 * math.exp(-age / 12)  # novelty
        if ed:
            left = (ed - x).days
            if left < 21:
                v *= 0.5 + 0.5 * left / 21
        life[i, k] = v

# ---------------------------------------------------------------- assortment & affinity
aff = np.ones((S, K), dtype=np.float32)
assort = np.zeros((S, K), dtype=np.float32)
MUST_HAVE = {("PAR01", "AUREA"), ("PAR02", "AUREA"), ("MIL01", "AUREA"), ("LON02", "AUREA"), ("MIL01", "VLOGO CARDIGAN"),
             ("MAD01", "NOVA")}
for s, st in enumerate(stores.itertuples()):
    rules = AFFINITY.get(st.subregion, {})
    for k, r in enumerate(skus.itertuples()):
        a = rules.get(r.style_name, 1.0) * rules.get("cat:" + r.category, 1.0) * rules.get("line:" + r.line, 1.0)
        if st.store_type == "Resort":
            a *= RESORT_AFFINITY.get(r.style_name, 1.0) * RESORT_AFFINITY.get("cat:" + r.category, 1.0) * \
                 RESORT_AFFINITY.get("line:" + r.line, 1.0)
        aff[s, k] = a * rng.lognormal(0, 0.18)
        p_keep = {"Flagship": 1.0, "Boutique": 0.86, "Shop-in-shop": 0.62, "Resort": 0.7}[st.store_type]
        if r.line == "Couture" and st.store_type in ("Shop-in-shop", "Resort"):
            p_keep = 0.15
        if r.line == "Atelier" and st.hemi == "T":
            p_keep = 0.1
        keep = rng.random() < p_keep * min(1.0, 0.55 + sku_pop[k] / 2.5)
        if (st.store_id, r.style_name) in MUST_HAVE:
            keep = True
        if r.style_name == "IRIDIA" and st.subregion in ("Korea", "Japan", "Mainland China", "HK/Macau/TW", "South-East Asia"):
            keep = True
        assort[s, k] = 1.0 if keep else 0.0

w_sk = assort * aff * sku_pop[None, :]
activity = life[:D].mean(axis=0)
share = w_sk / (w_sk * activity[None, :]).sum(axis=1, keepdims=True)
base = stores.scale.values[:, None].astype(np.float32) * share  # (S,K)

# ---------------------------------------------------------------- store-day multipliers & open flags
open_frac = np.ones((DA, S), dtype=np.float32)
store_mult = np.ones((DA, S), dtype=np.float32)
traffic_cal = np.ones((DA, S), dtype=np.float32)  # calendar effects on traffic (same as store_mult mostly)

DOW_EU = [0.80, 0.78, 0.85, 0.95, 1.12, 1.55, 1.05]
DOW_AS = [0.78, 0.78, 0.82, 0.88, 1.05, 1.50, 1.40]
DOW_US = [0.80, 0.80, 0.85, 0.95, 1.10, 1.50, 1.10]

GROWTH = {"Italy": 0.02, "France": 0.03, "Switzerland": 0.01, "UK": -0.02, "Germany": 0.0, "Spain": 0.05,
          "Benelux": 0.03, "Nordics": 0.02, "Middle East": 0.08, "USA": -0.03, "Canada": 0.0, "Japan": 0.12,
          "Korea": 0.06, "Mainland China": 0.07, "HK/Macau/TW": 0.03, "South-East Asia": 0.05, "Oceania": 0.02}

CNY = [dt.date(2025, 1, 29), dt.date(2026, 2, 17)]
CHUSEOK = [dt.date(2024, 9, 17), dt.date(2025, 10, 6), dt.date(2026, 9, 25)]
THANKSGIVING = [dt.date(2024, 11, 28), dt.date(2025, 11, 26) + dt.timedelta(days=1)]
EID = [dt.date(2025, 3, 30), dt.date(2026, 3, 20)]
EASTER = [dt.date(2025, 4, 20), dt.date(2026, 4, 5)]
HOLIDAY_CLOSED = {
    "DE": ["01-01", "05-01", "10-03", "12-25", "12-26", "2025-04-18", "2025-04-21", "2025-05-29", "2025-06-09",
           "2026-04-03", "2026-04-06", "2026-05-14", "2026-05-25"],
    "CH": ["01-01", "01-02", "08-01", "12-25", "12-26", "2025-04-18", "2025-04-21", "2025-05-29", "2025-06-09",
           "2026-04-03", "2026-04-06", "2026-05-14", "2026-05-25"],
    "DK": ["01-01", "12-24", "12-25", "12-26", "2025-04-17", "2025-04-18", "2025-04-21", "2025-05-29", "2025-06-09",
           "2026-04-02", "2026-04-03", "2026-04-06", "2026-05-14", "2026-05-25"],
    "FR": ["01-01", "05-01", "12-25"], "IT": ["01-01", "12-25"], "ES": ["01-01", "12-25", "01-06"],
    "GB": ["12-25"], "NL": ["01-01", "12-25"], "US": ["12-25"], "CA": ["12-25", "01-01"], "AE": [],
    "JP": ["01-01"], "KR": [], "CN": [], "HK": [], "TW": [], "SG": [], "AU": ["12-25", "04-25"],
}
SALE_PERIODS = [(dt.date(2025, 1, 4), dt.date(2025, 2, 16)), (dt.date(2025, 6, 28), dt.date(2025, 8, 10)),
                (dt.date(2026, 1, 7), dt.date(2026, 2, 15)), (dt.date(2026, 6, 27), dt.date(2026, 8, 9))]


def in_sale(x):
    return any(a <= x <= b for a, b in SALE_PERIODS)


store_drift = np.ones((DA, S), dtype=np.float32)
for s in range(S):
    walk = np.cumsum(rng.normal(0, 0.012, DA // 7 + 2))
    store_drift[:, s] = np.exp(np.repeat(walk, 7)[:DA] - walk.mean())

for i, x in enumerate(dates_all):
    for s, st in enumerate(stores.itertuples()):
        cc = st.country_code
        asia = st.region == "APAC" and cc not in ("AU", "SG")
        dow = (DOW_AS if asia else DOW_US if st.region == "AMERICAS" else DOW_EU)[x.weekday()]
        m = dow
        g = GROWTH[st.subregion]
        m *= (1 + g) ** ((x - dt.date(2025, 9, 1)).days / 365)
        if st.store_type == "Resort":
            m *= resort_arr[i]
        # closures
        if x.weekday() in st.closed_dow:
            open_frac[i, s] = 0
        hol = HOLIDAY_CLOSED.get(cc, [])
        if x.strftime("%m-%d") in hol or x.isoformat() in hol:
            open_frac[i, s] = 0
        if st.store_id == "MUN01" and x.strftime("%m-%d") == "11-01":
            open_frac[i, s] = 0
        for a, b in SEASONAL_CLOSURES.get(st.store_id, []):
            if d(a) <= x <= d(b):
                open_frac[i, s] = 0
        if st.store_id == "CRT01" and dt.date(2026, 10, 1) <= x <= dt.date(2026, 11, 27) and x.weekday() < 4:
            open_frac[i, s] = 0
        if st.store_id == "STM01" and x >= dt.date(2026, 10, 19) and x <= dt.date(2026, 12, 3):
            open_frac[i, s] = 0
        if (st.store_id, x.isoformat()) in CLOSURES:
            open_frac[i, s] = CLOSURES[(st.store_id, x.isoformat())]
        # Christmas & year end
        md = (x.month, x.day)
        if x.month == 12 and 8 <= x.day <= 23:
            m *= 1.0 + 0.6 * (x.day - 7) / 16 if st.hemi != "T" else 1.0 + 0.35 * (x.day - 7) / 16
        if md == (12, 24):
            m *= 0.75
        if x.month == 12 and x.day >= 27:
            m *= 1.15
        if md == (12, 26) and cc == "GB":
            m *= 1.35
        if cc == "JP" and md == (1, 2):
            m *= 1.9
        if in_sale(x):
            m *= 1.08
        # US
        if cc == "US":
            if x in THANKSGIVING:
                open_frac[i, s] = 0
            if any(x == t + dt.timedelta(days=1) for t in THANKSGIVING):
                m *= 1.55
        # CNY
        for c in CNY:
            delta = (x - c).days
            if cc == "CN":
                if -16 <= delta <= -2:
                    m *= 1.4
                elif -1 <= delta <= 2:
                    m *= 0.55
            elif cc in ("HK", "TW", "SG", "JP", "KR") or st.store_id in ("MIL01", "PAR01", "PAR02", "LON02", "DXB01"):
                if 0 <= delta <= 7:
                    m *= 1.22 if cc != "TW" else 0.8
            if cc == "KR" and -1 <= delta <= 1:
                pass
        # Golden week (2024/2025 recurring; 2026 is in events)
        if x.year < 2026 and x.month == 10 and 1 <= x.day <= 7:
            if cc == "CN":
                m *= 1.25
            elif st.store_id in ("MIL01", "MIL02", "PAR01", "PAR02", "LON02", "TYO01", "OSA01", "SEL01", "HKG01", "ZRH01", "VEN01"):
                m *= 1.15
        # Chuseok
        for c in CHUSEOK:
            delta = (x - c).days
            if cc == "KR":
                if delta == 0 and st.store_type == "Shop-in-shop":
                    open_frac[i, s] = 0
                elif -1 <= delta <= 1:
                    m *= 0.75
        # Japan golden week
        if cc == "JP" and (x.month, x.day) >= (4, 29) and (x.month, x.day) <= (5, 5):
            m *= 1.2
        if cc == "AE":
            for e in EID:
                if 0 <= (x - e).days <= 3:
                    m *= 1.5
                if -30 <= (x - e).days < 0:
                    m *= 0.85
            if x.month in (6, 7, 8):
                m *= 0.8
        if cc in ("DE", "CH", "DK", "AT") and x in EASTER:
            open_frac[i, s] = 0
        if cc == "CN" and x.month == 11 and 1 <= x.day <= 11:
            m *= 0.85
        if x.month == 11 and 25 <= x.day <= 30 and cc in ("GB", "FR", "IT", "ES", "DE", "NL"):
            m *= 1.1  # black-week spillover
        store_mult[i, s] = m
store_mult *= store_drift

# noise (store-day)
day_noise = rng.lognormal(0, 0.13, (DA, S)).astype(np.float32)

# ---------------------------------------------------------------- events
ev_mult = np.ones((DA, S, K), dtype=np.float32)
ev_traffic = np.ones((DA, S), dtype=np.float32)
ev_nat = []  # (event, d_idx range, stores idx, sku mask, mult array per day, nationality)
size_filter_events = []


def sku_mask_for(f):
    m = np.ones(K, dtype=bool)
    if "styles" in f:
        m &= skus.style_name.isin(f["styles"]).values
    if "colors" in f:
        m &= skus.color_code.isin(f["colors"]).values
    if "cats" in f:
        m &= skus.category.isin(f["cats"]).values
    if "sgroups" in f:
        m &= skus.season_group.isin(f["sgroups"]).values
    if "lines" in f:
        m &= skus.line.isin(f["lines"]).values
    if "seasons" in f:
        m &= skus.season.isin(f["seasons"]).values
    return m


DEMAND_NEUTRAL = {"E03", "E11", "E14", "E14b", "E16", "E40", "E44", "E45", "E42", "E09"}
for ev in EVENTS:
    a, b = didx[d(ev["start"])], didx[min(d(ev["end"]), D_END_BASE)]
    sidx = list(range(S)) if ev["stores"] == ["ALL"] else [sid[x] for x in ev["stores"]]
    mask = sku_mask_for(ev["filter"])
    n = b - a + 1
    t = np.arange(n)
    mm = ev["demand_mult"]
    if ev["shape"] == "spike_decay":
        prof = 1 + (mm - 1) * np.exp(-t / 9.0)
    elif ev["shape"] == "ramp_up":
        prof = 1 + (mm - 1) * np.minimum(1, (t + 1) / 3)
    else:
        prof = np.full(n, mm)
    tm = ev["traffic_mult"]
    if ev["id"] in DEMAND_NEUTRAL:
        continue
    for s in sidx:
        ev_mult[a:b + 1, s, :][:, mask] *= prof[:, None]
        if not ev["filter"]:
            ev_traffic[a:b + 1, s] *= tm if ev["shape"] != "ramp_up" else (1 + (tm - 1) * np.minimum(1, (t + 1) / 3))
        elif tm != 1.0:
            ev_traffic[a:b + 1, s] *= tm
    ev_nat.append((ev, a, b, sidx, mask, prof))

# ---------------------------------------------------------------- lambdas
print("building lambdas", DA, S, K)
seas = season_arr[:, hemi_idx][:, :, grp_idx]  # (DA,S,K)
lam_base = base[None] * seas * life[:, None, :] * store_mult[:, :, None] * (open_frac[:, :, None] > 0)
# sale-period markdown boost on seasonal items
seasonal_mask = (skus.season != "CO").values
for i, x in enumerate(dates_all):
    if in_sale(x):
        lam_base[i][:, seasonal_mask] *= 1.7
lam_base = lam_base.astype(np.float32)
lam = lam_base * ev_mult * day_noise[:, :, None] * np.clip(open_frac, 0, 1)[:, :, None]

# demand draw (gamma-poisson)
lam_obs = lam[:D]
mix = rng.gamma(3.0, 1 / 3.0, lam_obs.shape).astype(np.float32)
demand = rng.poisson(lam_obs * mix).astype(np.int32)  # (D,S,K)
print("total demand units", demand.sum(), "per store-day", demand.sum() / D / S)

# ---------------------------------------------------------------- size curves
size_runs = {k: SIZE_RUNS[r] for k, r in enumerate(skus.size_run)}
curve_cache = {}


def store_curve(s, run):
    key = (s, run)
    if key in curve_cache:
        return curve_cache[key]
    c = np.array(SIZE_CURVES[run], dtype=float)
    st = stores.iloc[s]
    if len(c) > 1:
        x = np.arange(len(c)) - (len(c) - 1) / 2
        shift = {"APAC": -0.22, "AMERICAS": 0.18}.get(st.region, 0.0)
        if st.subregion in ("Oceania", "South-East Asia"):
            shift = -0.05
        c = c * np.exp(shift * x)
        c = c * rng.lognormal(0, 0.05, len(c))
        c /= c.sum()
    curve_cache[key] = c
    return c


# flat sku-size index
kz_rows = []
for k, r in enumerate(skus.itertuples()):
    for j, sz in enumerate(size_runs[k]):
        kz_rows.append((k, j, sz))
KZ = len(kz_rows)
kz_k = np.array([r[0] for r in kz_rows])
kz_j = np.array([r[1] for r in kz_rows])
kz_size = [r[2] for r in kz_rows]
kz_start = {}
for z, (k, j, sz) in enumerate(kz_rows):
    kz_start.setdefault(k, z)
curve_kz = np.zeros((S, KZ), dtype=np.float32)
for s in range(S):
    for k in range(K):
        c = store_curve(s, skus.size_run[k])
        z0 = kz_start[k]
        curve_kz[s, z0:z0 + len(c)] = c

# ---------------------------------------------------------------- window: size-level demand
WD = D - W0
wdates = dates[W0:]
dem_kz = np.zeros((WD, S, KZ), dtype=np.int32)
for s in range(S):
    for k in range(K):
        if assort[s, k] == 0:
            continue
        c = curve_kz[s, kz_start[k]:kz_start[k] + len(size_runs[k])]
        n = demand[W0:, s, k]
        if n.sum() == 0:
            continue
        dem_kz[:, s, kz_start[k]:kz_start[k] + len(c)] = rng.multinomial(n, c)
# forced demand for E03 (at least one ask for size M on Oct 8)
lc_m = [z for z, (k, j, sz) in enumerate(kz_rows) if skus.style_name[k] == "VLOGO CARDIGAN" and sz == "M"]

# ---------------------------------------------------------------- inventory simulation
LEAD = {"Italy": 1, "France": 2, "Switzerland": 3, "UK": 3, "Germany": 2, "Spain": 2, "Benelux": 2, "Nordics": 3,
        "Middle East": 5, "USA": 5, "Canada": 6, "Japan": 6, "Korea": 5, "Mainland China": 8, "HK/Macau/TW": 5,
        "South-East Asia": 6, "Oceania": 7}
ORIGIN = {"EMEA": "DC-IT-CSG", "AMERICAS": "DC-US-NJ", "APAC": "DC-HK-TKO"}
ORDER_DAYS = {s: ([0, 3] if stores.store_type[s] == "Flagship" else [0]) for s in range(S)}
for s in range(S):
    if stores.region[s] == "APAC":
        ORDER_DAYS[s] = [1] if stores.store_type[s] != "Flagship" else [1, 4]
COVER = {"EMEA": 21, "AMERICAS": 28, "APAC": 28}

lam_base_kz_daily = None  # computed per day on the fly
stock = np.zeros((S, KZ), dtype=np.int32)
intransit = np.zeros((S, KZ), dtype=np.int32)
arrivals = np.zeros((WD + 40, S, KZ), dtype=np.int32)
sales_kz = np.zeros((WD, S, KZ), dtype=np.int32)
stock_eod = np.zeros((WD, S, KZ), dtype=np.int32)
lost_kz = np.zeros((WD, S, KZ), dtype=np.int32)
shipments = []
ship_counter = 1

assort_kz = assort[:, kz_k]
min_pres = np.zeros((S, KZ), dtype=np.int32)
for s in range(S):
    if stores.store_type[s] in ("Flagship", "Boutique"):
        min_pres[s] = (curve_kz[s] >= 0.12).astype(np.int32)
min_pres = min_pres * (assort_kz > 0)

# DC constraints -> boolean (WD, KZ) blocked
dc_block = np.zeros((WD + 40, KZ), dtype=bool)
for style, color, sizes, a, b, note in DC_CONSTRAINTS:
    for z, (k, j, sz) in enumerate(kz_rows):
        if skus.style_name[k] == style and (color is None or skus.color_code[k] == color) and (sizes is None or sz in sizes):
            ia, ib = (d(a) - WINDOW_START).days, (d(b) - WINDOW_START).days
            dc_block[max(ia, 0):ib, z] = True


def target_stock(w):
    """order-up-to level based on baseline (event-free) expected demand"""
    i = W0 + w
    cover = np.array([COVER[r] for r in stores.region])
    horizon = np.zeros((S, K), dtype=np.float32)
    for h in range(0, 28, 4):
        horizon += lam_base[min(i + h, DA - 1)] * 4
    daily = horizon / 28
    exp = daily[:, kz_k] * curve_kz * cover[:, None]
    t = np.round(exp * 1.15 + 0.25).astype(np.int32)
    t = np.maximum(t, min_pres * (life[min(i + 7, DA - 1), kz_k] > 0)[None, :] * (exp > 0.05))
    return t * (assort_kz > 0)


# initial stock
t0 = target_stock(0)
stock = np.round(t0 * rng.uniform(0.7, 1.3, t0.shape)).astype(np.int32)
not_launched = np.array([bool(skus.launch_date[k]) and d(skus.launch_date[k]) > WINDOW_START for k in kz_k])
stock[:, not_launched] = 0
kz_launch = np.array([d(skus.launch_date[k]) if skus.launch_date[k] else dt.date(2000, 1, 1) for k in kz_k])
ss26_kz = np.array([skus.season[k] == "SS26" for k in kz_k])
launch_kz = {}
for z, (k, j, sz) in enumerate(kz_rows):
    if skus.launch_date[k] and d(skus.launch_date[k]) > WINDOW_START:
        launch_kz.setdefault(d(skus.launch_date[k]), []).append(z)
ALLOC_FACTOR = {"IRIDIA": 0.55, "ASTRA CAPE": 1.0, "ASTRA OVERSIZED": 1.0, "ASTRA BALACLAVA": 1.0, "AMALIA": 0.8}

CARRIERS = {"EMEA": ["BRT", "DHL Express", "GEODIS", "DHL Express"], "AMERICAS": ["FedEx", "UPS", "FedEx"],
            "APAC": ["DHL Express", "Kerry Logistics", "SF Express", "Nippon Express"]}
returns_sched = np.zeros((WD + 30, S, KZ), dtype=np.int32)
returns_defect = np.zeros((WD + 30, S, KZ), dtype=np.int32)
returns_size = np.zeros((WD + 30, S, KZ), dtype=np.int32)
tib_kz = np.array([skus.style_name[k] == "VEL" for k in kz_k])
arneb_kz = np.array([skus.style_name[k] == "ARTEM" for k in kz_k])
RET_RATE = {"EMEA": 0.035, "AMERICAS": 0.065, "APAC": 0.015}
ret_rate_s = np.array([RET_RATE[r] for r in stores.region])
def_start = (dt.date(2026, 9, 28) - WINDOW_START).days
tib_def_sold = np.zeros((S, KZ), dtype=np.int32)  # defective units sold since Aug 15 not yet returned

for w in range(WD):
    x = wdates[w]
    i = W0 + w
    stock += arrivals[w]
    # launches: allocation lands on launch date
    for z in launch_kz.get(x, []):
        k = kz_k[z]
        fac = ALLOC_FACTOR.get(skus.style_name[k], 1.0)
        tz = target_stock(w)[:, z]
        alloc = np.round(tz * fac).astype(np.int32)
        stock[:, z] += alloc
    if x == dt.date(2026, 9, 1):
        stock[:, ss26_kz] = 0  # SS26 returned to DC
    # one-shot caps
    for cap in STOCK_CAPS:
        style, color, st_list, day, val = cap[:5]
        sizes = cap[5] if len(cap) > 5 else None
        if x == d(day):
            for z, (k, j, sz) in enumerate(kz_rows):
                if skus.style_name[k] == style and (color is None or skus.color_code[k] == color) and (sizes is None or sz in sizes):
                    for stid in st_list:
                        stock[sid[stid], z] = min(stock[sid[stid], z], val)
    dem = dem_kz[w]
    if x == dt.date(2026, 10, 8):
        for z in lc_m:
            dem[sid["MIL01"], z] = max(dem[sid["MIL01"], z], 2)
    sold = np.minimum(dem, stock)
    stock -= sold
    sales_kz[w] = sold
    lost_kz[w] = dem - sold
    # returns scheduling
    nz = np.argwhere(sold > 0)
    for s, z in nz:
        q = sold[s, z]
        r = rng.binomial(q, ret_rate_s[s])
        if arneb_kz[z]:
            rs = rng.binomial(q - r, 0.10)
            if rs:
                returns_size[w + rng.integers(1, 9), s, z] += rs
        if tib_kz[z] and x >= dt.date(2026, 8, 15):
            rd = rng.binomial(q - r, 0.16)
            if rd:
                lag = rng.integers(3, 25)
                ww = max(w + lag, def_start + rng.integers(0, 6))
                if ww < WD + 30:
                    returns_defect[ww, s, z] += rd
        if r:
            returns_sched[w + rng.integers(1, 15), s, z] += r
    # returned units back to stock (non-defective)
    stock += returns_sched[w] + returns_size[w]
    # replenishment orders
    tgt = None
    for s in range(S):
        if x.weekday() not in ORDER_DAYS[s]:
            continue
        if tgt is None:
            tgt = target_stock(w)
        need = tgt[s] - stock[s] - intransit[s]
        need[dc_block[w]] = 0
        need[ss26_kz] = 0
        need[kz_launch > x] = 0
        need = np.maximum(need, 0)
        if need.sum() == 0:
            continue
        st = stores.iloc[s]
        lead = LEAD[st.subregion]
        ship_date = x + dt.timedelta(days=1)
        planned = ship_date + dt.timedelta(days=lead)
        delay = 0
        if rng.random() < 0.08:
            delay = int(rng.integers(1, 4))
        # E14: SEL01 shipment held in customs
        if st.store_id == "SEL01" and dt.date(2026, 10, 5) <= ship_date <= dt.date(2026, 10, 7):
            delay = (dt.date(2026, 10, 13) - planned).days
        actual = planned + dt.timedelta(days=delay)
        # E14b: MAD01 wrong colour
        lines = []
        swapped = []
        for z in np.nonzero(need)[0]:
            q = int(need[z])
            k = kz_k[z]
            z_recv = z
            if st.store_id == "MAD01" and skus.style_name[k] == "NOVA" and skus.color_code[k] == "999" and \
                    dt.date(2026, 9, 17) <= ship_date <= dt.date(2026, 10, 2):
                # picking error: navy shipped instead of black
                z_recv = kid[skus.sku[k].replace("-999", "-742")]
                z_recv = kz_start[z_recv] + kz_j[z]
                swapped.append((kz_rows[z], q))
            lines.append(dict(sku=skus.sku[k], size=kz_size[z], qty_ordered=q,
                              qty_shipped=q, sku_received=skus.sku[kz_k[z_recv]], size_received=kz_size[z_recv]))
            wi = (actual - WINDOW_START).days
            arrivals[wi, s, z_recv] += q
            intransit[s, z] += q
        shipments.append(dict(shipment_id=f"SHP{26 * 100000 + ship_counter:08d}", store_id=st.store_id,
                              origin=ORIGIN[st.region], order_date=x.isoformat(), ship_date=ship_date.isoformat(),
                              planned_arrival=planned.isoformat(), actual_arrival=actual.isoformat(),
                              carrier=str(rng.choice(CARRIERS[st.region])), delay_days=delay, lines=lines,
                              _swapped=bool(swapped)))
        ship_counter += 1
    # in-transit bookkeeping: subtract arrivals (by ordered sku) - approximate by clearing arrivals of today
    for sh in shipments:
        if sh["actual_arrival"] == x.isoformat():
            s = sid[sh["store_id"]]
            for ln in sh["lines"]:
                z = kz_start[kid[ln["sku"]]] + SIZE_RUNS[skus.size_run[kid[ln["sku"]]]].index(ln["size"])
                intransit[s, z] -= ln["qty_ordered"]
    stock_eod[w] = stock
print("window sales", sales_kz.sum(), "lost", lost_kz.sum(), "shipments", len(shipments))

# ---------------------------------------------------------------- prices
price_local = np.zeros((S, K))
for s, st in enumerate(stores.itertuples()):
    ccy = st.currency
    for k in range(K):
        p = skus.price_eur[k] * FX_EUR[ccy] * PRICE_PREMIUM[ccy]
        r = ROUNDING[ccy]
        price_local[s, k] = round(p / r) * r
# Japan price increase Nov 1 (not in window, for price list file)

# ---------------------------------------------------------------- outputs: master data
mkdir(INT / "master_data")
st_out = stores.drop(columns=["scale", "hemi"]).copy()
st_out["closed_dow"] = st_out.closed_dow.apply(lambda v: "|".join(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][i] for i in v))
st_out["email"] = st_out.store_id.str.lower() + ".store@valentino-retail.example"
st_out.to_csv(INT / "master_data" / "stores.csv", index=False)
styles_out = styles.copy()
styles_out["colors"] = styles_out.colors.apply(lambda v: "|".join(v))
styles_out.drop(columns=["popularity"]).to_csv(INT / "master_data" / "styles.csv", index=False)
skus.drop(columns=["popularity"]).to_csv(INT / "master_data" / "sku_colour.csv", index=False)
ean_rows = []
for z, (k, j, sz) in enumerate(kz_rows):
    ean = f"80{int(skus.style_code[k][-5:]):05d}{int(abs(hash(skus.sku[k])) % 1000):03d}{j:02d}"
    ean_rows.append(dict(sku=skus.sku[k], size=sz, sku_size=f"{skus.sku[k]}-{sz}", ean=ean[:13]))
pd.DataFrame(ean_rows).to_csv(INT / "master_data" / "sku_size_ean.csv", index=False)
pl = []
for s, st in enumerate(stores.itertuples()):
    for k in range(K):
        pl.append(dict(store_id=st.store_id, sku=skus.sku[k], currency=st.currency, retail_price=price_local[s, k],
                       valid_from="2026-02-01"))
pd.DataFrame(pl).to_csv(INT / "master_data" / "price_list_FW26.csv", index=False)
asr = [dict(store_id=stores.store_id[s], sku=skus.sku[k], in_assortment=int(assort[s, k])) for s in range(S) for k in range(K)]
pd.DataFrame(asr).query("in_assortment==1").drop(columns="in_assortment").to_csv(INT / "master_data" / "store_assortment.csv", index=False)

# ---------------------------------------------------------------- POS lines (window) + returns
print("POS lines")
NAT_MIX = {
    "Italy": [("IT", .38), ("CN", .12), ("US", .10), ("KR", .05), ("JP", .04), ("SA", .03), ("AE", .03), ("DE", .04), ("FR", .03), ("GB", .03), ("CH", .03), ("BR", .02), ("TR", .02), ("IN", .02), ("OTHER", .06)],
    "France": [("FR", .30), ("CN", .14), ("US", .12), ("KR", .06), ("JP", .04), ("SA", .03), ("AE", .03), ("GB", .04), ("IT", .03), ("DE", .03), ("BR", .03), ("TW", .02), ("OTHER", .13)],
    "UK": [("GB", .45), ("US", .12), ("CN", .08), ("SA", .06), ("AE", .05), ("KW", .03), ("QA", .03), ("NG", .03), ("IN", .03), ("OTHER", .12)],
    "Germany": [("DE", .62), ("US", .05), ("CN", .06), ("AE", .03), ("SA", .03), ("CH", .04), ("AT", .04), ("TR", .03), ("OTHER", .10)],
    "Switzerland": [("CH", .50), ("CN", .08), ("US", .07), ("DE", .06), ("SA", .05), ("AE", .05), ("IN", .04), ("RU", .03), ("OTHER", .12)],
    "Spain": [("ES", .50), ("MX", .08), ("US", .08), ("CN", .05), ("CO", .04), ("AR", .03), ("OTHER", .22)],
    "Benelux": [("NL", .58), ("US", .07), ("DE", .06), ("GB", .05), ("CN", .04), ("OTHER", .20)],
    "Nordics": [("DK", .60), ("SE", .10), ("NO", .08), ("US", .05), ("DE", .05), ("CN", .03), ("OTHER", .09)],
    "Middle East": [("AE", .22), ("SA", .14), ("IN", .14), ("RU", .10), ("CN", .08), ("KW", .05), ("GB", .05), ("OTHER", .22)],
    "USA": [("US", .78), ("CN", .04), ("BR", .03), ("MX", .03), ("GB", .02), ("KR", .02), ("OTHER", .08)],
    "Canada": [("CA", .80), ("US", .06), ("CN", .05), ("OTHER", .09)],
    "Japan": [("JP", .55), ("CN", .16), ("TW", .07), ("KR", .06), ("HK", .04), ("US", .04), ("TH", .03), ("OTHER", .05)],
    "Korea": [("KR", .80), ("CN", .09), ("JP", .03), ("TW", .02), ("US", .02), ("OTHER", .04)],
    "Mainland China": [("CN", .98), ("OTHER", .02)],
    "HK/Macau/TW": [("HK", .45), ("CN", .45), ("OTHER", .10)],
    "South-East Asia": [("SG", .45), ("CN", .15), ("ID", .12), ("MY", .08), ("IN", .06), ("AU", .04), ("OTHER", .10)],
    "Oceania": [("AU", .72), ("CN", .10), ("NZ", .04), ("US", .04), ("OTHER", .10)],
}
NAT_MIX["HK/Macau/TW_TPE"] = [("TW", .80), ("JP", .06), ("HK", .04), ("CN", .03), ("OTHER", .07)]
TAXFREE_COUNTRIES = {"IT", "FR", "DE", "CH", "ES", "NL", "DK", "JP", "KR", "SG", "AE", "AU"}  # UK no tax-free since 2021
EU = {"IT", "FR", "DE", "ES", "NL", "DK", "AT", "SE", "BE", "PT", "IE"}
PAY = {"EMEA": [("VISA", .30), ("MASTERCARD", .25), ("AMEX", .20), ("CASH", .05), ("APPLE_PAY", .12), ("ALIPAY", .04), ("UNIONPAY", .04)],
       "AMERICAS": [("VISA", .30), ("AMEX", .32), ("MASTERCARD", .18), ("APPLE_PAY", .17), ("CASH", .03)],
       "APAC": [("VISA", .22), ("MASTERCARD", .14), ("AMEX", .08), ("UNIONPAY", .12), ("ALIPAY", .14), ("WECHAT_PAY", .14), ("CASH", .04), ("JCB", .06), ("KAKAO_PAY", .06)]}
HOURS = {"default": (10, 19), "US": (10, 18), "CN": (10, 22), "KR": (10, 20), "JP": (11, 20), "AE": (10, 23), "HK": (11, 21), "SG": (10, 22), "TW": (11, 21.5)}
staff_ids = {stores.store_id[s]: [f"{stores.store_id[s]}-SA{n:02d}" for n in range(1, int(6 + stores.scale[s] / 6))] for s in range(S)}
client_pool = {stores.store_id[s]: [f"CL{rng.integers(10**7, 9 * 10**7)}" for _ in range(int(stores.scale[s] * 40))] for s in range(S)}


def pick(lst):
    names, ps = zip(*lst)
    ps = np.array(ps) / sum(ps)
    return names[rng.choice(len(names), p=ps)]


# event nationality uplift per (w,s,k)
nat_uplift = {}
for ev, a, b, sidx, mask, prof in ev_nat:
    if not ev["nationality"]:
        continue
    for ii in range(max(a, W0), min(b, D - 1) + 1):
        for s in sidx:
            nat_uplift.setdefault((ii - W0, s), []).append((ev["nationality"], mask, prof[ii - a]))

pos_lines = []
rcpt_counter = defaultdict(int)
sales_receipt_index = defaultdict(list)  # (s,z) -> list of (receipt_id, date, price) for returns referencing
for w in range(WD):
    x = wdates[w]
    for s in range(S):
        st = stores.iloc[s]
        z_sold = np.nonzero(sales_kz[w, s])[0]
        units = []
        for z in z_sold:
            units += [z] * int(sales_kz[w, s, z])
        if not units:
            continue
        mixkey = "HK/Macau/TW_TPE" if st.store_id == "TPE01" else st.subregion
        upl = nat_uplift.get((w, s), [])
        nats = []
        for z in units:
            k = kz_k[z]
            nat = None
            for nat_e, mask, m in upl:
                if mask[k] and rng.random() < (m - 1) / m:
                    nat = nat_e
                    break
            if nat is None:
                nat = pick(NAT_MIX[mixkey])
            nats.append(nat)
        order = rng.permutation(len(units))
        by_nat = defaultdict(list)
        for o in order:
            by_nat[nats[o]].append(units[o])
        h0, h1 = HOURS.get(st.country_code, HOURS["default"])
        for nat, us in by_nat.items():
            p = 0
            while p < len(us):
                n = int(rng.choice([1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 4])) if nat == st.country_code else int(rng.choice([1, 1, 1, 2, 2, 3, 3, 4, 5]))
                basket = us[p:p + n]
                p += n
                rcpt_counter[(st.store_id, x)] += 1
                rid = f"{st.store_id}-{x.strftime('%y%m%d')}-{rcpt_counter[(st.store_id, x)]:04d}"
                hr = rng.triangular(h0, h0 + (h1 - h0) * 0.62, h1)
                ts = dt.datetime.combine(x, dt.time(0)) + dt.timedelta(hours=float(hr))
                bizdate = x
                if st.store_id == "NYC02" and x == dt.date(2026, 10, 6) and 14.1 < hr < 17.7:
                    bizdate = x + dt.timedelta(days=1)
                    ts = dt.datetime.combine(bizdate, dt.time(9, 40)) + dt.timedelta(minutes=int(rng.integers(0, 50)))
                foreign = nat != st.country_code and not (nat in EU and st.country_code in EU)
                tf = foreign and st.country_code in TAXFREE_COUNTRIES and rng.random() < 0.82
                pay = pick(PAY[st.region])
                if nat == "CN" and rng.random() < 0.6:
                    pay = rng.choice(["ALIPAY", "WECHAT_PAY", "UNIONPAY"])
                client = rng.choice(client_pool[st.store_id]) if (not foreign and rng.random() < 0.55) or rng.random() < 0.12 else ""
                sa = rng.choice(staff_ids[st.store_id])
                for z in basket:
                    k = kz_k[z]
                    price = price_local[s, k]
                    disc = 0.0
                    if skus.season[k] == "SS26" and x <= dt.date(2026, 8, 9):
                        disc = price * rng.choice([0.3, 0.3, 0.4, 0.5])
                    elif rng.random() < 0.006:
                        disc = price * 0.3  # staff
                    elif client and rng.random() < 0.02:
                        disc = price * 0.1
                    pos_lines.append(dict(business_date=bizdate.isoformat(), store_id=st.store_id, receipt_id=rid,
                                          ts_local=ts.strftime("%Y-%m-%d %H:%M:%S"), line_type="SALE", sku=skus.sku[k],
                                          size=kz_size[z], qty=1, unit_price=price, discount=round(disc, 2),
                                          net_amount=round(price - disc, 2), currency=st.currency, customer_id=client,
                                          customer_nationality=nat, tax_free=int(tf), payment_method=pay,
                                          sales_associate=sa, return_reason="", original_receipt_id=""))
                    sales_receipt_index[(s, z)].append((rid, x, price - disc))
    # returns of the day (closed stores: roll to next day)
    for arr, reason in ((returns_sched, None), (returns_defect, "DEF"), (returns_size, "SIZE")):
        for s in range(S):
            if open_frac[W0 + w, s] == 0 and w + 1 < arr.shape[0]:
                arr[w + 1, s] += arr[w, s]
                arr[w, s] = 0
        nz = np.argwhere(arr[w] > 0)
        for s, z in nz:
            st = stores.iloc[s]
            for _ in range(int(arr[w, s, z])):
                k = kz_k[z]
                hist = sales_receipt_index.get((s, z))
                if hist and rng.random() < 0.9:
                    orig, od, amt = hist[rng.integers(len(hist))]
                else:
                    orig, amt = "", price_local[s, k]
                rcpt_counter[(st.store_id, x)] += 1
                rid = f"{st.store_id}-{x.strftime('%y%m%d')}-{rcpt_counter[(st.store_id, x)]:04d}"
                rr = reason or pick([("SIZE", .35), ("CHANGE_MIND", .35), ("GIFT", .1), ("COLOUR", .1), ("QUALITY", .1)])
                if reason == "SIZE" and rng.random() < 0.6:
                    rr = "EXCHANGE_SIZE"
                h0, h1 = HOURS.get(st.country_code, HOURS["default"])
                ts = dt.datetime.combine(x, dt.time(0)) + dt.timedelta(hours=float(rng.uniform(h0, h1)))
                pos_lines.append(dict(business_date=x.isoformat(), store_id=st.store_id, receipt_id=rid,
                                      ts_local=ts.strftime("%Y-%m-%d %H:%M:%S"), line_type="RETURN", sku=skus.sku[k],
                                      size=kz_size[z], qty=-1, unit_price=price_local[s, k], discount=0.0,
                                      net_amount=-round(amt, 2), currency=st.currency, customer_id="",
                                      customer_nationality="", tax_free=0, payment_method="REFUND",
                                      sales_associate=rng.choice(staff_ids[st.store_id]), return_reason=rr,
                                      original_receipt_id=orig))
                if reason is None or reason == "SIZE":
                    pass
pos = pd.DataFrame(pos_lines)
pos = pos[pos.business_date <= END.isoformat()]
print("pos lines", len(pos))
pdir = mkdir(INT / "sales" / "pos_lines")
pos["_wk"] = pd.to_datetime(pos.business_date).dt.isocalendar().week
for wk, g in pos.groupby("_wk"):
    g.drop(columns="_wk").sort_values(["business_date", "store_id", "ts_local"]).to_csv(pdir / f"pos_lines_2026-W{wk:02d}.csv", index=False)
pos = pos.drop(columns="_wk")

# ---------------------------------------------------------------- daily sales aggregate (history + window)
print("daily aggregates")
sdir = mkdir(INT / "sales" / "daily_store_sku")
rows = []
# pre-window from draws
ret_rate_k = np.array([RET_RATE[r] for r in stores.region])
sold_hist = demand[:W0] * (assort[None] > 0)
ret_hist = rng.binomial(sold_hist, ret_rate_k[None, :, None] * 1.0)
ret_hist = np.roll(ret_hist, 5, axis=0)
ret_hist[:5] = 0
for i in range(W0):
    x = dates[i]
    nz = np.argwhere((sold_hist[i] > 0) | (ret_hist[i] > 0))
    sale = in_sale(x)
    for s, k in nz:
        u, r = int(sold_hist[i, s, k]), int(ret_hist[i, s, k])
        p = price_local[s, k]
        disc_rate = 0.0
        if sale and skus.season[k] != "CO":
            disc_rate = 0.3 if (x.month in (1, 7) and x.day < 20) else 0.5
        gross = u * p
        disc = gross * disc_rate
        rows.append((x.isoformat(), stores.store_id[s], skus.sku[k], u, r, round(gross, 2), round(disc, 2),
                     round(r * p * (1 - disc_rate), 2), round(gross - disc - r * p * (1 - disc_rate), 2), stores.currency[s]))
hist_df = pd.DataFrame(rows, columns=["business_date", "store_id", "sku", "units_sold", "units_returned", "gross_sales_lc",
                                      "discount_lc", "returns_lc", "net_sales_lc", "currency"])
pos["_units_s"] = np.where(pos.qty > 0, pos.qty, 0)
pos["_units_r"] = np.where(pos.qty < 0, -pos.qty, 0)
pos["_gross"] = np.where(pos.qty > 0, pos.unit_price, 0)
pos["_disc"] = np.where(pos.qty > 0, pos.discount, 0)
pos["_ret"] = np.where(pos.qty < 0, -pos.net_amount, 0)
win_df = pos.groupby(["business_date", "store_id", "sku", "currency"], as_index=False).agg(
    units_sold=("_units_s", "sum"), units_returned=("_units_r", "sum"), gross_sales_lc=("_gross", "sum"),
    discount_lc=("_disc", "sum"), returns_lc=("_ret", "sum"))
win_df["net_sales_lc"] = (win_df.gross_sales_lc - win_df.discount_lc - win_df.returns_lc).round(2)
win_df = win_df[hist_df.columns]
daily = pd.concat([hist_df, win_df], ignore_index=True)
daily["_m"] = daily.business_date.str[:7]
for m, g in daily.groupby("_m"):
    g.drop(columns="_m").sort_values(["business_date", "store_id", "sku"]).to_csv(sdir / f"sales_daily_{m.replace('-', '_')}.csv", index=False)
daily = daily.drop(columns="_m")
pos = pos.drop(columns=["_units_s", "_units_r", "_gross", "_disc", "_ret"])
print("daily rows", len(daily))

# ---------------------------------------------------------------- traffic & KPI
print("traffic / kpi")
CONV = {"Flagship": 0.105, "Boutique": 0.13, "Shop-in-shop": 0.16, "Resort": 0.14}
UPT = 1.35
base_units = (lam_base[:D] * (assort[None] > 0)).sum(axis=2) * np.clip(open_frac[:D], 0, 1)  # event-free expected units
traffic = np.zeros((D, S))
for s in range(S):
    conv = CONV[stores.store_type[s]] * rng.uniform(0.85, 1.15)
    traffic[:, s] = base_units[:, s] / UPT / conv * ev_traffic[:D, s] * day_noise[:D, s] ** 0.7 * rng.lognormal(0, 0.06, D)
traffic = np.round(traffic).astype(int)
receipts_by = pos[pos.line_type == "SALE"].groupby(["business_date", "store_id"]).receipt_id.nunique()
tr_rows = []
for i, x in enumerate(dates):
    for s in range(S):
        stid = stores.store_id[s]
        t = int(traffic[i, s])
        if open_frac[i, s] == 0:
            continue
        if stid == "MAD01" and dt.date(2026, 10, 1) <= x <= dt.date(2026, 10, 7):
            t = 0
        if rng.random() < 0.004:
            continue  # missing feed
        tr_rows.append((x.isoformat(), stid, t, "Xovis 3D" if stores.store_type[s] != "Shop-in-shop" else "dept-store feed"))
traffic_df = pd.DataFrame(tr_rows, columns=["date", "store_id", "visitors_in", "sensor_source"])
mkdir(INT / "traffic")
traffic_df.to_csv(INT / "traffic" / "door_counter_daily.csv", index=False)

# KPI (BI export) - EUR at budget rate
BUDGET_RATE = {"EUR": 1, "CHF": 0.95, "GBP": 0.85, "DKK": 7.46, "AED": 4.0, "USD": 1.08, "CAD": 1.48, "JPY": 162.0,
               "KRW": 1480.0, "CNY": 7.8, "HKD": 8.45, "TWD": 34.8, "SGD": 1.45, "AUD": 1.65}
kpi = daily.groupby(["business_date", "store_id", "currency"], as_index=False).agg(
    units=("units_sold", "sum"), returns_units=("units_returned", "sum"), net_sales_lc=("net_sales_lc", "sum"))
rc_hist = {}
kpi["receipts"] = [int(receipts_by.get((r.business_date, r.store_id), round(r.units / UPT))) for r in kpi.itertuples()]
kpi = kpi.merge(traffic_df.rename(columns={"date": "business_date"})[["business_date", "store_id", "visitors_in"]],
                on=["business_date", "store_id"], how="left")
kpi["net_sales_eur_bud"] = (kpi.net_sales_lc / kpi.currency.map(BUDGET_RATE)).round(0)
# budget: event-free expectation * plan uplift
bud = {}
for i, x in enumerate(dates):
    for s in range(S):
        bud[(x.isoformat(), stores.store_id[s])] = float((lam_base[i, s] * price_local[s]).sum()) * 1.04 * 0.97
kpi = kpi[[open_frac[didx[dt.date.fromisoformat(r.business_date)], sid[r.store_id]] > 0 for r in kpi.itertuples()]].copy()
kpi["budget_lc"] = [round(bud[(r.business_date, r.store_id)] * rng.lognormal(0, 0.03), -1) for r in kpi.itertuples()]
kpi["conversion"] = (kpi.receipts / kpi.visitors_in.replace(0, np.nan)).round(4)
kpi["upt"] = (kpi.units / kpi.receipts.replace(0, np.nan)).round(2)
kpi["atv_lc"] = (kpi.net_sales_lc / kpi.receipts.replace(0, np.nan)).round(0)
kpi["vs_budget_pct"] = ((kpi.net_sales_lc / kpi.budget_lc - 1) * 100).round(1)
mkdir(INT / "kpi")
kpi.sort_values(["business_date", "store_id"]).to_csv(INT / "kpi" / "store_daily_kpi.csv", index=False)

# ---------------------------------------------------------------- inventory snapshots (daily, window)
print("stock snapshots")
idir = mkdir(INT / "inventory" / "store_stock_daily")
for w in range(WD):
    x = wdates[w]
    nz = np.argwhere((stock_eod[w] > 0) | ((assort_kz > 0) & (life[W0 + w, kz_k][None, :] > 0)))
    df = pd.DataFrame({"snapshot_date": x.isoformat(), "store_id": stores.store_id.values[nz[:, 0]],
                       "sku": skus.sku.values[kz_k[nz[:, 1]]], "size": np.array(kz_size)[nz[:, 1]],
                       "on_hand": stock_eod[w][nz[:, 0], nz[:, 1]],
                       "in_transit": 0})
    df.to_csv(idir / f"stock_eod_{x.isoformat()}.csv", index=False)

# shipments
ldir = mkdir(INT / "logistics")
with open(ldir / "shipments_dc_to_store.jsonl", "w") as f:
    for sh in shipments:
        sh2 = {k: v for k, v in sh.items() if not k.startswith("_")}
        sh2["status"] = "DELIVERED" if d(sh["actual_arrival"]) <= END else "IN_TRANSIT"
        if d(sh["actual_arrival"]) > END:
            sh2["actual_arrival"] = None
        for ln in sh2["lines"]:
            if d(sh["actual_arrival"]) > END:
                ln.pop("sku_received"); ln.pop("size_received")
        f.write(json.dumps(sh2, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------- forecast (statistical, event-blind)
print("forecast")
fdir = mkdir(INT / "forecast")
runs = [WINDOW_START + dt.timedelta(days=(7 - WINDOW_START.weekday()) % 7 + 7 * n) for n in range(12)]
runs = [r for r in runs if r <= END]
# event-blind lambda; SYD uses northern seasonality; new items via analog
lam_fc = lam_base.copy()
s_syd = sid["SYD01"]
seas_n = season_arr[:, 0][:, grp_idx]
lam_fc[:, s_syd, :] = base[s_syd][None] * seas_n * life * store_mult[:, s_syd][:, None] * (open_frac[:, s_syd][:, None] > 0)
ANALOG = {"IRIDIA": ("ARIA", 0.6), "AMALIA": ("LIVIANA", 0.7), "ARTEM": ("MISTRAL", 0.8), "RIVIERA": ("NOVA", 0.5),
          "CASHMERE TURTLENECK": ("VLOGO CARDIGAN", 0.6)}
for k in range(K):
    nm = skus.style_name[k]
    if nm in ANALOG:
        an, fac = ANALOG[nm]
        ks = [kk for kk in range(K) if skus.style_name[kk] == an]
        an_l = lam_base[:, :, ks].mean(axis=2)
        lam_fc[:, :, k] = an_l * fac * (life[:, k] > 0)[:, None] * assort[:, k][None]
# LY golden week memory
gw = [sid[x] for x in EVENTS[0]["stores"]] + [sid[x] for x in ("SHA01", "BJS01", "CDU01")]
for i in range(didx[dt.date(2026, 10, 1)], didx[dt.date(2026, 10, 7)] + 1):
    lam_fc[i, gw] *= 1.12
err = np.exp(rng.normal(0, 0.22, (S, K))).astype(np.float32)
fc_rows = []
for r in runs:
    err = (err ** 0.8 * np.exp(rng.normal(0, 0.1, (S, K)))).astype(np.float32)
    for h in range(1, 9):
        ws = r + dt.timedelta(days=7 * (h - 1))
        a = didx[ws]
        wk = lam_fc[a:a + 7].sum(axis=0) * err
        iso = ws.isocalendar()
        nz = np.argwhere((wk > 0.05) & (assort > 0))
        for s, k in nz:
            fc_rows.append((r.isoformat(), f"{iso[0]}-W{iso[1]:02d}", ws.isoformat(), stores.store_id[s], skus.sku[k],
                            round(float(wk[s, k]), 2)))
fc = pd.DataFrame(fc_rows, columns=["run_date", "target_week", "week_start", "store_id", "sku", "fcst_units"])
fdd = mkdir(fdir / "sku_store_weekly")
for r, g in fc.groupby("run_date"):
    g.to_csv(fdd / f"fcst_sku_store_run_{r}.csv", index=False)
# store-level top-down value forecast (different engine, does not reconcile)
fc["value_lc"] = [f * price_local[sid[s], kid[k]] for f, s, k in zip(fc.fcst_units, fc.store_id, fc.sku)]
st_fc = fc.groupby(["run_date", "target_week", "week_start", "store_id"], as_index=False).value_lc.sum()
st_fc["fcst_net_sales_lc"] = (st_fc.value_lc * rng.lognormal(-0.03, 0.07, len(st_fc))).round(-2)
st_fc = st_fc.merge(stores[["store_id", "currency", "region"]], on="store_id")
st_fc["fcst_net_sales_eur"] = (st_fc.fcst_net_sales_lc / st_fc.currency.map(BUDGET_RATE)).round(-2)
st_fc.drop(columns="value_lc").to_csv(fdir / "store_weekly_value_forecast.csv", index=False)
reg = st_fc[st_fc.run_date == runs[-1].isoformat()].groupby(["region", "target_week"], as_index=False).fcst_net_sales_eur.sum()
reg["fcst_net_sales_eur"] = (reg.fcst_net_sales_eur * rng.lognormal(0.02, 0.04, len(reg))).round(-3)
with pd.ExcelWriter(fdir / "region_forecast_latest.xlsx") as xw:
    reg.pivot(index="target_week", columns="region", values="fcst_net_sales_eur").to_excel(xw, sheet_name="Region x Week (EUR)")
    pd.DataFrame({"note": ["Top-down regional forecast, EUR at budget rate 2026.", f"Run {runs[-1].isoformat()}",
                           "Includes retail DOS only. Excludes e-commerce and wholesale.",
                           "Not reconciled with SKU x store forecast (different engine)."]}).to_excel(xw, sheet_name="README", index=False)

# ---------------------------------------------------------------- ground truth
print("ground truth")
mkdir(GT)
ev_out = []
for ev in EVENTS:
    e = dict(ev)
    a, b = d(ev["start"]), min(d(ev["end"]), END)
    mask = sku_mask_for(ev["filter"])
    sidx = list(range(S)) if ev["stores"] == ["ALL"] else [sid[x] for x in ev["stores"]]
    if a >= WINDOW_START and a <= END:
        wa, wb = (a - WINDOW_START).days, (b - WINDOW_START).days
        kzm = mask[kz_k]
        e["window_demand_units"] = int(dem_kz[wa:wb + 1][:, sidx][:, :, kzm].sum())
        e["window_sales_units"] = int(sales_kz[wa:wb + 1][:, sidx][:, :, kzm].sum())
        e["window_lost_units"] = int(lost_kz[wa:wb + 1][:, sidx][:, :, kzm].sum())
    ev_out.append(e)
json.dump(dict(events=ev_out, dc_constraints=DC_CONSTRAINTS, stock_caps=STOCK_CAPS,
               closures={f"{k[0]}|{k[1]}": v for k, v in CLOSURES.items()}),
          open(GT / "scenario" / "events.json", "w"), ensure_ascii=False, indent=1, default=str)
lr = np.argwhere(lost_kz > 0)
lost_df = pd.DataFrame({"date": [wdates[w].isoformat() for w in lr[:, 0]], "store_id": stores.store_id.values[lr[:, 1]],
                        "sku": skus.sku.values[kz_k[lr[:, 2]]], "size": np.array(kz_size)[lr[:, 2]],
                        "demand": dem_kz[lr[:, 0], lr[:, 1], lr[:, 2]], "sold": sales_kz[lr[:, 0], lr[:, 1], lr[:, 2]],
                        "lost": lost_kz[lr[:, 0], lr[:, 1], lr[:, 2]]})
lost_df.to_csv(GT / "demand" / "lost_sales_daily.csv", index=False)
true_dem = []
for w in range(WD):
    true_dem.append(pd.DataFrame({"date": wdates[w].isoformat(), "store_id": np.repeat(stores.store_id.values, K),
                                  "sku": np.tile(skus.sku.values, S), "demand_units": demand[W0 + w].reshape(-1),
                                  "expected_units_event_free": lam_base[W0 + w].reshape(-1).round(3),
                                  "expected_units_true": lam[W0 + w].reshape(-1).round(3)}).query("demand_units>0 or expected_units_true>0.05"))
pd.concat(true_dem).to_csv(GT / "demand" / "true_demand_window.csv", index=False)

# ---------------------------------------------------------------- email context for writers
print("email context")
cdir = mkdir(GT / "writer_inputs" / "email_context")
pos_s = pos[pos.line_type == "SALE"]
pos_r = pos[pos.line_type == "RETURN"]
kpi_i = kpi.set_index(["business_date", "store_id"])
ship_by = defaultdict(list)
for sh in shipments:
    ship_by[(sh["store_id"], sh["actual_arrival"])].append(sh)
for s in range(S):
    st = stores.iloc[s]
    days = []
    for w in range(WD):
        x = wdates[w]
        if x < EMAIL_START:
            continue
        i = W0 + w
        key = (x.isoformat(), st.store_id)
        dd = dict(date=x.isoformat(), weekday=x.strftime("%A"), open=float(open_frac[i, s]))
        if key in kpi_i.index:
            r = kpi_i.loc[key]
            dd.update(net_sales_lc=float(r.net_sales_lc), budget_lc=float(r.budget_lc), vs_budget_pct=float(r.vs_budget_pct),
                      units=int(r.units), receipts=int(r.receipts), visitors=None if pd.isna(r.visitors_in) else int(r.visitors_in),
                      conversion=None if pd.isna(r.conversion) else float(r.conversion))
        ps = pos_s[(pos_s.business_date == x.isoformat()) & (pos_s.store_id == st.store_id)]
        top = ps.groupby("sku").qty.sum().sort_values(ascending=False).head(5)
        dd["top_sellers"] = [f"{skus.style_name[kid[k]]} {COLORS[skus.color_code[kid[k]]][1]} x{int(q)}" for k, q in top.items()]
        nat = ps.customer_nationality.value_counts(normalize=True).head(4)
        dd["customer_mix"] = {k: round(v, 2) for k, v in nat.items()}
        # unmet demand (customers asking for things not available)
        lostd = [(z, int(lost_kz[w, s, z])) for z in np.nonzero(lost_kz[w, s])[0]]
        lostd.sort(key=lambda t: -t[1])
        dd["unmet_requests"] = [f"{skus.style_name[kz_k[z]]} {COLORS[skus.color_code[kz_k[z]]][1]} size {kz_size[z]} x{q}" for z, q in lostd[:8]]
        # notable stockouts: assorted, active, popular, on-hand 0 at EOD
        so = [z for z in np.nonzero((stock_eod[w, s] == 0) & (assort_kz[s] > 0) & (curve_kz[s] >= 0.15))[0]
              if life[i, kz_k[z]] > 0 and sku_pop[kz_k[z]] * aff[s, kz_k[z]] > 1.2]
        dd["zero_stock_key_sizes"] = [f"{skus.style_name[kz_k[z]]} {COLORS[skus.color_code[kz_k[z]]][1]} {kz_size[z]}" for z in so[:10]]
        rr = pos_r[(pos_r.business_date == x.isoformat()) & (pos_r.store_id == st.store_id)]
        dd["returns"] = [f"{skus.style_name[kid[r.sku]]} {r.size} reason={r.return_reason}" for r in rr.itertuples()]
        dd["deliveries_received"] = [dict(shipment=sh["shipment_id"], lines=len(sh["lines"]), units=sum(l["qty_shipped"] for l in sh["lines"]),
                                          planned=sh["planned_arrival"], delay_days=sh["delay_days"], wrong_items=sh["_swapped"])
                                     for sh in ship_by.get((st.store_id, x.isoformat()), [])]
        dd["active_events"] = [f"{ev['id']}: {ev['title']}" for ev in EVENTS if (ev["stores"] == ["ALL"] or st.store_id in ev["stores"])
                               and d(ev["start"]) <= x <= d(ev["end"])]
        days.append(dd)
    json.dump(dict(store=st.drop(["scale"]).to_dict(), days=days), open(cdir / f"{st.store_id}.json", "w"),
              ensure_ascii=False, indent=1, default=str)
print("done")
