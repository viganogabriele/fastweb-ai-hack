"""E-commerce (brand.com on a Shopify-Plus-like platform + WeChat mini program for CN).

Outputs (generated/sources/systems/ecommerce/):
  - shopify_sales_by_variant_daily.csv      daily online sales by storefront country x variant (Aug 1 -> Oct 21 2026)
  - back_in_stock_requests.csv               'notify me' requests (request level)
  - site_search_queries_daily.csv            site-search log aggregated per day x site x query
  - inventory_availability_log.csv           OOS / back-in-stock transitions per web node x variant (UTC)
Cache for the WMS (generator/systems/_cache/): ecom_web_transfers.csv, ecom_web_stock_eod.csv
"""
import datetime as dt
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402
import config  # noqa: E402
from events import DC_CONSTRAINTS  # noqa: E402

R = C.rng("ecommerce")
OUT = C.OUT / "ecommerce"
OUT.mkdir(parents=True, exist_ok=True)

DAYS = list(C.daterange("2026-08-01", "2026-10-21"))
DI = {x: i for i, x in enumerate(DAYS)}
ND = len(DAYS)

stores = C.stores()
sk = C.skus().set_index("sku")
sizes_df = C.sku_sizes()

# ------------------------------------------------------------------ countries / web nodes
# country: (region/web node, online ratio vs local stores, proxy stores, proxy factor, currency, price store)
COUNTRIES = {
    "IT": ("EMEA", 0.10, None, 1, "EUR", "MIL01"), "FR": ("EMEA", 0.12, None, 1, "EUR", "PAR01"),
    "CH": ("EMEA", 0.09, None, 1, "CHF", "ZRH01"), "GB": ("EMEA", 0.22, None, 1, "GBP", "LON01"),
    "DE": ("EMEA", 0.32, None, 1, "EUR", "MUN01"), "ES": ("EMEA", 0.18, None, 1, "EUR", "MAD01"),
    "NL": ("EMEA", 0.26, None, 1, "EUR", "AMS01"), "DK": ("EMEA", 0.25, None, 1, "DKK", "CPH01"),
    "AE": ("EMEA", 0.08, None, 1, "AED", "DXB01"), "BE": ("EMEA", 0.26, "NL", 0.55, "EUR", "AMS01"),
    "AT": ("EMEA", 0.32, "DE", 0.35, "EUR", "MUN01"), "SE": ("EMEA", 0.25, "DK", 0.7, "EUR", "CPH01"),
    "US": ("AMERICAS", 0.30, None, 1, "USD", "NYC01"), "CA": ("AMERICAS", 0.30, None, 1, "CAD", "TOR01"),
    "JP": ("APAC", 0.12, None, 1, "JPY", "TYO01"), "KR": ("APAC", 0.20, None, 1, "KRW", "SEL01"),
    "CN": ("APAC", 0.14, None, 1, "CNY", "SHA01"), "HK": ("APAC", 0.07, None, 1, "HKD", "HKG01"),
    "TW": ("APAC", 0.10, None, 1, "TWD", "TPE01"), "SG": ("APAC", 0.09, None, 1, "SGD", "SIN01"),
    "AU": ("APAC", 0.26, None, 1, "AUD", "SYD01"),
}
NODE_WERKS = {"EMEA": "IT10", "AMERICAS": "US20", "APAC": "HK30"}
CC = list(COUNTRIES)

# ------------------------------------------------------------------ baseline demand (event-free) per country x sku x day
td = pd.read_csv(C.GT / "demand" / "true_demand_window.csv", usecols=["date", "store_id", "sku", "expected_units_event_free"])
td = td.merge(stores[["store_id", "country_code"]], on="store_id")
base_cc = td.groupby(["country_code", "date", "sku"]).expected_units_event_free.sum()
SKUS = sorted(td.sku.unique())
KI = {s: i for i, s in enumerate(SKUS)}
NK = len(SKUS)
base = np.zeros((len(CC), ND, NK), dtype=np.float64)
for ci, c in enumerate(CC):
    reg, ratio, proxy, pf, ccy, pst = COUNTRIES[c]
    src = proxy or c
    sub = base_cc.loc[src].reset_index()
    sub = sub[sub.date <= "2026-10-21"]
    di = sub.date.map(lambda x: DI[C.d(x)]).values
    ki = sub.sku.map(KI).values
    np.add.at(base[ci], (di, ki), sub.expected_units_event_free.values * ratio * pf)

# store resort closures inflate nothing online; country without open stores still sells online:
# floor the baseline with a small share of the region mix to avoid zero rows when resort stores close
style_of = np.array([s.split("-")[0] for s in SKUS])
color_of = np.array([s.split("-")[1] for s in SKUS])
name_of = np.array([C.STYLE_NAME[s] for s in style_of])
sgroup = np.array([sk.season_group[s] for s in SKUS])
season = np.array([sk.season[s] for s in SKUS])
line = np.array([sk.line[s] for s in SKUS])
launch = np.array([C.d(sk.launch_date[s]) if isinstance(sk.launch_date[s], str) else dt.date(2000, 1, 1) for s in SKUS])
end = np.array([C.d(sk.end_date[s]) if isinstance(sk.end_date[s], str) else dt.date(2100, 1, 1) for s in SKUS])

# ------------------------------------------------------------------ online event multipliers
mult = np.ones_like(base)


def apply(countries, mask, a, b, m, shape="flat", hl=5.0):
    for x in C.daterange(a, b):
        t = (x - C.d(a)).days
        if shape == "flat":
            f = m
        elif shape == "spike":
            f = 1 + (m - 1) * (0.5 ** (t / hl))
        elif shape == "ramp":
            n = (C.d(b) - C.d(a)).days + 1
            f = 1 + (m - 1) * min(1.0, (t + 1) / max(n * 0.6, 1))
        for c in countries:
            mult[CC.index(c), DI[x], mask] *= f


ASIA_CELEB = ["KR", "CN", "JP", "HK", "TW", "SG"]
ilv510 = (name_of == "IRIDIA") & (color_of == "510")
ilv_oth = (name_of == "IRIDIA") & np.isin(color_of, ["999", "20D"])
apply(ASIA_CELEB, ilv510, "2026-10-02", "2026-10-21", 38.0, "spike", hl=3.5)
apply(["KR"], ilv510, "2026-10-02", "2026-10-21", 1.8)
apply([c for c in CC if c not in ASIA_CELEB], ilv510, "2026-10-02", "2026-10-21", 5.0, "spike", hl=4)
apply(ASIA_CELEB, ilv_oth, "2026-10-03", "2026-10-21", 3.0, "spike", hl=6)
maire_blk = (name_of == "AUREA") & (color_of == "999")
apply(["KR"], maire_blk, "2026-09-17", "2026-10-21", 3.2)
apply(["FR", "IT", "GB"], maire_blk, "2026-09-19", "2026-10-21", 1.4)
heavy = sgroup == "HEAVY"
apply(["DE", "AT", "CH", "DK", "SE", "NL", "BE"], heavy, "2026-10-12", "2026-10-19", 1.9, "ramp")
apply(["FR", "GB", "IT"], heavy, "2026-10-13", "2026-10-19", 1.2)
apply(["JP"], heavy, "2026-09-28", "2026-10-11", 0.65)
apply(["JP"], season == "CO", "2026-10-10", "2026-10-21", 1.5, "ramp")
apply(["CN"], np.ones(NK, bool), "2026-10-20", "2026-10-21", 1.35)     # D11 presales online
couture = line == "Couture"
apply(["CN", "HK"], couture, "2026-09-24", "2026-10-21", 1.7, "spike", hl=12)
apply(["IT", "FR", "GB", "DE", "ES", "NL", "US", "CA", "CH"], couture, "2026-09-24", "2026-10-21", 0.45)
valentino_v17 = name_of == "VEL"
apply(CC, valentino_v17, "2026-09-28", "2026-10-21", 0.8)
amb_brown = (name_of == "AMALIA") & (color_of == "23R")
apply(["IT", "FR", "GB", "ES"], amb_brown, "2026-09-10", "2026-10-21", 2.2)
apply(["US", "GB"], np.ones(NK, bool), "2026-09-15", "2026-10-21", 1.07)   # brand campaign (real effect)
apply(["CN"], np.ones(NK, bool), "2026-10-01", "2026-10-07", 0.85)          # Golden week: people travel

lam = base * mult
for k in range(NK):
    lam[:, [DI[x] for x in DAYS if x < launch[k]], k] = 0
    lam[:, [DI[x] for x in DAYS if x > end[k]], k] = 0
# SS26 leaves the site Sep 1 (returned to DC with stores)
lam[:, DI[dt.date(2026, 9, 1)]:, season == "SS26"] = 0
# celebrity spike: absolute extra demand on top (no history -> multiplicative model is not enough)
CELEB_ABS = {"KR": 140, "CN": 90, "JP": 50, "HK": 18, "TW": 16, "SG": 9, "US": 4, "GB": 3, "FR": 3, "IT": 2, "AU": 3}
k510 = int(np.nonzero(ilv510)[0][0])
for x in C.daterange("2026-10-02", "2026-10-21"):
    t = (x - dt.date(2026, 10, 2)).days
    for c, a0 in CELEB_ABS.items():
        lam[CC.index(c), DI[x], k510] += a0 * (0.5 ** (t / 3.0)) + a0 * 0.06
dem = R.poisson(lam)

# ------------------------------------------------------------------ size split
size_runs = {s: config.SIZE_RUNS[sk.size_run[s]] for s in SKUS}
ASIA_SMALL = {"KR", "CN", "JP", "HK", "TW", "SG"}


def size_curve(s, c):
    run = sk.size_run[s]
    cur = np.array(config.SIZE_CURVES[run], dtype=float)
    if c in ASIA_SMALL and len(cur) > 1:
        cur = cur * np.linspace(1.35, 0.6, len(cur))
    elif c in ("US", "CA", "DE", "NL", "DK", "SE") and len(cur) > 1:
        cur = cur * np.linspace(0.75, 1.3, len(cur))
    return cur / cur.sum()


# ------------------------------------------------------------------ web stock simulation per node
# DC blocks
blocks = []
for style, color, szs, a, b, note in DC_CONSTRAINTS:
    blocks.append((style, color, szs, C.d(a), C.d(b)))


def dc_blocked(s, size, x):
    for style, color, szs, a, b in blocks:
        if C.STYLE_NAME[s.split("-")[0]] == style and (color is None or s.endswith("-" + color)) and \
                (szs is None or size in szs) and a <= x < b:
            return True
    return False


NODES = ["EMEA", "AMERICAS", "APAC"]
node_cc = {n: [c for c in CC if COUNTRIES[c][0] == n] for n in NODES}
web_stock = {n: {} for n in NODES}          # (sku,size) -> qty
transfers = []                               # (date, node, sku, size, qty, reason)
stock_eod_rows = []
avail_log = []
sales_rows = []                              # (date, country, sku, size, qty, ts)
lost_rows = []                               # (date, country, sku, size, qty, ts)
oos_state = {n: {} for n in NODES}

# expected (event-free) daily demand per node x sku x size for cover targets
def node_exp(n, i):
    idx = [CC.index(c) for c in node_cc[n]]
    lo, hi = max(0, i - 3), min(ND, i + 11)
    return base[idx, lo:hi, :].sum(axis=0).mean(axis=0)   # per sku


ILV510 = "J20931A00618-510"
ILV510_LAUNCH_WEB = {"EMEA": 30, "AMERICAS": 12, "APAC": 70}
ILV510_TOPUP = {"APAC": C.ILVARO_TOPUP_ECOM_RESERVE["HK30"], "EMEA": C.ILVARO_TOPUP_ECOM_RESERVE["IT10"],
                "AMERICAS": C.ILVARO_TOPUP_ECOM_RESERVE["US20"]}
EXTRA_TOPUP_DAYS = {dt.date(2026, 10, 9), dt.date(2026, 10, 17), dt.date(2026, 10, 20), dt.date(2026, 10, 21)}
COVER_DAYS = 14


def split_by_curve(total, s, curve_cc):
    cur = size_curve(s, curve_cc)
    q = np.floor(cur * total).astype(int)
    rem = total - q.sum()
    order = np.argsort(-(cur * total - q))
    for j in order[:rem]:
        q[j] += 1
    return dict(zip(size_runs[s], q))


def ts_for(x, c, frac):
    """Order timestamp (UTC) for a local day fraction (customer local evening heavy)."""
    tzoff = {"IT": 2, "FR": 2, "CH": 2, "GB": 1, "DE": 2, "ES": 2, "NL": 2, "DK": 2, "AE": 4, "BE": 2, "AT": 2, "SE": 2,
             "US": -4, "CA": -4, "JP": 9, "KR": 9, "CN": 8, "HK": 8, "TW": 8, "SG": 8, "AU": 10}[c]
    if x >= dt.date(2026, 10, 25) and c in ("IT", "FR", "CH", "DE", "ES", "NL", "DK", "BE", "AT", "SE", "GB"):
        tzoff -= 1
    if c == "AU" and x >= dt.date(2026, 10, 4):
        tzoff = 11
    local = dt.datetime.combine(x, dt.time(0)) + dt.timedelta(hours=7 + 17 * frac)
    return local - dt.timedelta(hours=tzoff)


for i, x in enumerate(DAYS):
    for n in NODES:
        ws = web_stock[n]
        # replenishment (Mondays + special days)
        if i == 0 or x.weekday() == 0 or x in EXTRA_TOPUP_DAYS or any(x == launch[k] for k in range(NK)):
            e = node_exp(n, i)
            for k, s in enumerate(SKUS):
                if lam[[CC.index(c) for c in node_cc[n]], i:min(ND, i + 7), k].sum() == 0 and launch[k] != x:
                    continue
                if x < launch[k]:
                    continue
                tgt_tot = e[k] * COVER_DAYS * 1.2
                if s == ILV510:
                    if x == launch[k]:
                        add = split_by_curve(ILV510_LAUNCH_WEB[n], s, node_cc[n][0])
                        for z, q in add.items():
                            if q:
                                ws[(s, z)] = ws.get((s, z), 0) + q
                                transfers.append((x, n, s, z, q, "LAUNCH_WEB_ALLOC"))
                    elif x == dt.date(2026, 10, 9):
                        add = split_by_curve(ILV510_TOPUP[n], s, node_cc[n][0])
                        for z, q in add.items():
                            if q:
                                ws[(s, z)] = ws.get((s, z), 0) + q
                                transfers.append((x, n, s, z, q, "TOPUP_RESERVE_ECOM"))
                    continue
                if x in EXTRA_TOPUP_DAYS and x.weekday() != 0 and not (
                        (C.STYLE_NAME[s.split('-')[0]] in ("AUREA", "IRIDIA")) and x >= dt.date(2026, 10, 17)):
                    continue
                cur = size_curve(s, node_cc[n][0])
                for j, z in enumerate(size_runs[s]):
                    if dc_blocked(s, z, x):
                        continue
                    tq = int(math.ceil(tgt_tot * cur[j] + (0.6 if tgt_tot * cur[j] > 0.15 else 0)))
                    have = ws.get((s, z), 0)
                    if tq > have:
                        q = tq - have
                        ws[(s, z)] = have + q
                        transfers.append((x, n, s, z, q, "WEB_REPLEN" if x != launch[k] else "LAUNCH_WEB_ALLOC"))
        # back-in-stock events right after the morning web replenishment (before first local orders)
        bis_base = {"EMEA": dt.datetime.combine(x, dt.time(4, 20)), "AMERICAS": dt.datetime.combine(x, dt.time(9, 5)),
                    "APAC": dt.datetime.combine(x, dt.time(0, 0)) - dt.timedelta(hours=2, minutes=40)}[n]
        for (dd, nn, s, z, q, why) in [t for t in transfers if t[0] == x and t[1] == n]:
            if oos_state[n].get((s, z)):
                oos_state[n][(s, z)] = False
                avail_log.append((bis_base + dt.timedelta(minutes=int(R.integers(0, 45))), n, s, z, "BACK_IN_STOCK",
                                  web_stock[n][(s, z)]))
        # demand of the day, random arrival order across countries
        units = []
        for c in node_cc[n]:
            ci = CC.index(c)
            for k in np.nonzero(dem[ci, i])[0]:
                s = SKUS[k]
                q = int(dem[ci, i, k])
                szq = R.multinomial(q, size_curve(s, c))
                for z, qq in zip(size_runs[s], szq):
                    for _ in range(qq):
                        # celebrity day: pink demand arrives in the first hours (morning Asia)
                        frac = R.beta(1.2, 6) if (s == ILV510 and x == dt.date(2026, 10, 2)) else R.beta(2.2, 2.0)
                        units.append((ts_for(x, c, frac), c, s, z))
        units.sort()
        for ts, c, s, z in units:
            have = web_stock[n].get((s, z), 0)
            if have > 0:
                web_stock[n][(s, z)] = have - 1
                sales_rows.append((x, c, s, z, 1, ts))
                if have - 1 == 0:
                    avail_log.append((ts, n, s, z, "OUT_OF_STOCK", 0))
                    oos_state[n][(s, z)] = True
            else:
                lost_rows.append((x, c, s, z, 1, ts))
    for n in NODES:
        for (s, z), q in web_stock[n].items():
            if q:
                stock_eod_rows.append((x, n, s, z, q))

sales = pd.DataFrame(sales_rows, columns=["date", "country", "sku", "size", "qty", "ts"])
lost = pd.DataFrame(lost_rows, columns=["date", "country", "sku", "size", "qty", "ts"])
print("online units", sales.qty.sum(), "lost", lost.qty.sum())
print(sales[sales.sku == ILV510].groupby(["date"]).qty.sum().tail(25).to_string())
print(lost[lost.sku == ILV510].groupby(["country"]).qty.sum())
_al = pd.DataFrame(avail_log, columns=["ts", "node", "sku", "size", "event", "qty"])
for _s in [ILV510]:
    print(_s); print(_al[_al.sku == _s].sort_values("ts").head(30).to_string(max_rows=60))
print(lost.groupby("sku").qty.sum().sort_values().tail(8))
_ws = pd.DataFrame(stock_eod_rows, columns=["date", "node", "sku", "size", "qty"])
print(_ws[(_ws.date == dt.date(2026, 10, 21)) & (_ws.sku.str.startswith("I10919B00011")) & (_ws["size"] == "M")])

# cache for WMS
pd.DataFrame(transfers, columns=["date", "node", "sku", "size", "qty", "reason"]).assign(
    werks=lambda d_: d_.node.map(NODE_WERKS)).to_csv(C.CACHE / "ecom_web_transfers.csv", index=False)
pd.DataFrame(stock_eod_rows, columns=["date", "node", "sku", "size", "qty"]).assign(
    werks=lambda d_: d_.node.map(NODE_WERKS)).to_csv(C.CACHE / "ecom_web_stock_eod.csv", index=False)
sales.to_csv(C.CACHE / "ecom_sales_units.csv", index=False)
lost.to_csv(C.CACHE / "ecom_lost_units.csv", index=False)

# ------------------------------------------------------------------ returns
ret_rows = []
for r in sales.itertuples():
    name = C.STYLE_NAME[r.sku.split("-")[0]]
    p = 0.09 if COUNTRIES[r.country][0] != "APAC" else 0.04
    reason = "OTHER"
    if name == "VEL" and r.date >= dt.date(2026, 8, 15) and R.random() < 0.17:
        lag = int(R.integers(6, 26))
        rd = max(r.date + dt.timedelta(days=lag), dt.date(2026, 9, 27) + dt.timedelta(days=int(R.integers(0, 7))))
        ret_rows.append((rd, r.country, r.sku, r.size, 1, "DEFECTIVE"))
        continue
    if name == "ARTEM" and R.random() < 0.14:
        ret_rows.append((r.date + dt.timedelta(days=int(R.integers(4, 14))), r.country, r.sku, r.size, 1, "SIZE_TOO_LARGE"))
        continue
    if name.startswith("ASTRA") and COUNTRIES[r.country][0] != "APAC" and R.random() < 0.18:
        ret_rows.append((r.date + dt.timedelta(days=int(R.integers(4, 14))), r.country, r.sku, r.size, 1, "SIZE_TOO_SMALL"))
        continue
    if R.random() < p:
        ret_rows.append((r.date + dt.timedelta(days=int(R.integers(5, 20))), r.country, r.sku, r.size, 1,
                         str(R.choice(["CHANGED_MIND", "SIZE_TOO_SMALL", "SIZE_TOO_LARGE", "NOT_AS_DESCRIBED", "OTHER"]))))
rets = pd.DataFrame(ret_rows, columns=["date", "country", "sku", "size", "qty", "reason"])
rets = rets[rets.date <= C.LAST_DAY]
rets.to_csv(C.CACHE / "ecom_returns_units.csv", index=False)

# ------------------------------------------------------------------ export 1: Shopify-like sales report
price = pd.read_csv(C.INTERNAL / "master_data" / "price_list_FW26.csv")
price = price.set_index(["store_id", "sku"]).retail_price
COLOR_EN = {k: v[1].title() for k, v in config.COLORS.items()}
COLOR_EN["20D"] = "Off-White"
TITLES = {}
for s in SKUS:
    st = C.STYLE_BY_CODE[s.split("-")[0]]
    TITLES[s] = (f"{st[1].title()} {st[4]}", st[3])
ean = sizes_df.set_index(["sku", "size"]).ean

agg_s = sales.groupby(["date", "country", "sku", "size"]).agg(ordered=("qty", "sum")).reset_index()
# orders ~ units / 1.15
agg_r = rets.groupby(["date", "country", "sku", "size"]).agg(returned=("qty", "sum")).reset_index()
rep = agg_s.merge(agg_r, how="outer", on=["date", "country", "sku", "size"]).fillna(0)
rows = []
for r in rep.itertuples():
    reg, ratio, proxy, pf, ccy, pst = COUNTRIES[r.country]
    try:
        p = float(price[(pst, r.sku)])
    except KeyError:
        p = float(sk.price_eur[r.sku]) * config.FX_EUR[ccy] * config.PRICE_PREMIUM[ccy]
        p = round(p / config.ROUNDING[ccy]) * config.ROUNDING[ccy]
    ordered, returned = int(r.ordered), int(r.returned)
    gross = ordered * p
    # few promo/employee/appeasement discounts
    disc = 0.0
    if ordered and R.random() < 0.03:
        disc = round(gross * float(R.choice([0.1, 0.15, 0.3])), 2)
    ret_amt = -returned * p
    channel = "WeChat Mini Program" if r.country == "CN" else "Online Store"
    variant_sku = f"{r.sku}-{r.size}"
    if r.size == "TU" and R.random() < 0.85:
        variant_sku = r.sku                       # one-size variants were created without size suffix
    if channel == "WeChat Mini Program":
        variant_sku = ean[(r.sku, r.size)]       # partner integration maps by barcode
    col = COLOR_EN[r.sku.split("-")[1]]
    rows.append(dict(day=r.date.isoformat(), sales_channel=channel, billing_country=r.country,
                     product_title=TITLES[r.sku][0], product_type=TITLES[r.sku][1], variant_title=f"{col} / {r.size}",
                     variant_sku=variant_sku, orders=int(math.ceil(ordered / 1.12)) if ordered else 0,
                     ordered_item_quantity=ordered, returned_item_quantity=returned, net_quantity=ordered - returned,
                     gross_sales=round(gross, 2), discounts=-disc, returns=round(ret_amt, 2),
                     net_sales=round(gross - disc + ret_amt, 2), currency=ccy))
rep = pd.DataFrame(rows).sort_values(["day", "billing_country", "product_title", "variant_title"])
# quirk: Sep 30 export appended twice by the BI job (exact duplicate rows)
dup = rep[rep.day == "2026-09-30"]
rep = pd.concat([rep, dup]).sort_values(["day", "billing_country", "product_title"], kind="stable")
rep.to_csv(OUT / "shopify_sales_by_variant_daily.csv", index=False)
print("sales rows", len(rep))

# ------------------------------------------------------------------ export 2: back in stock / notify me
LOCALE = {"IT": "it-IT", "FR": "fr-FR", "CH": "de-CH", "GB": "en-GB", "DE": "de-DE", "ES": "es-ES", "NL": "nl-NL",
          "DK": "da-DK", "AE": "en-AE", "BE": "fr-BE", "AT": "de-AT", "SE": "sv-SE", "US": "en-US", "CA": "en-CA",
          "JP": "ja-JP", "KR": "ko-KR", "CN": "zh-CN", "HK": "zh-HK", "TW": "zh-TW", "SG": "en-SG", "AU": "en-AU"}
bis = []
rid = 880000
restock = pd.DataFrame(avail_log, columns=["ts", "node", "sku", "size", "event", "qty"])
back = restock[restock.event == "BACK_IN_STOCK"]
for r in lost.itertuples():
    p = 0.33
    if r.sku == ILV510:
        p = 0.75
    elif r.sku in ("J20931A00012-999", "J20931A00622-23R"):
        p = 0.5
    if R.random() > p:
        continue
    reps = 1 + (R.random() < 0.06)   # some customers subscribe twice (different email / same email)
    node = COUNTRIES[r.country][0]
    b = back[(back.node == node) & (back.sku == r.sku) & (back["size"] == r.size) & (back.ts > r.ts)]
    sent = b.ts.min() if len(b) else None
    for _ in range(reps):
        rid += int(R.integers(1, 4))
        email_hash = f"{abs(C.stable_hash((r.country, r.ts, r.sku, rid // 7))) % 16**10:010x}"
        status, conv = "PENDING", ""
        if sent is not None:
            status = "SENT"
            if R.random() < 0.18:
                status, conv = "CONVERTED", f"MC-{C.ECOM_ORDER_PREFIX[node]}-26-0{int(R.integers(400000, 499999))}"
        elif R.random() < 0.03:
            status = "UNSUBSCRIBED"
        bis.append(dict(request_id=f"BIS-{rid}", created_at=(r.ts + dt.timedelta(minutes=int(R.integers(0, 9)))).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        site=f"valentino-{r.country.lower()}", locale=LOCALE[r.country], country=r.country,
                        product_id=r.sku, variant_sku=f"{r.sku}-{r.size}", size=r.size, email_sha1_10=email_hash,
                        marketing_optin=bool(R.random() < 0.41), status=status,
                        notified_at=sent.strftime("%Y-%m-%dT%H:%M:%SZ") if sent is not None else "",
                        converted_order=conv))
# extra notify-me from people who never tried to buy (view-only) on hot OOS items
bis = pd.DataFrame(bis)
bis.to_csv(OUT / "back_in_stock_requests.csv", index=False)
print("bis", len(bis), bis[bis.product_id == ILV510].groupby("country").size().to_dict())

# ------------------------------------------------------------------ export 3: availability log
al = restock.copy()
al["ts"] = al.ts.map(lambda t: t.strftime("%Y-%m-%d %H:%M:%S"))
al["inventory_location"] = al.node.map({"EMEA": "WEB-EU (IT10/W100)", "AMERICAS": "WEB-US (US20/W100)", "APAC": "WEB-APAC (HK30/W100)"})
al["variant_sku"] = al.sku + "-" + al["size"]
al = al.rename(columns={"ts": "changed_at_utc", "event": "availability_event", "qty": "available_after"})
al[["changed_at_utc", "inventory_location", "variant_sku", "availability_event", "available_after"]].sort_values(
    "changed_at_utc").to_csv(OUT / "inventory_availability_log.csv", index=False)

# ------------------------------------------------------------------ export 4: site search log
style_queries = {
    "NOVA": ["nova", "nova jacket", "valentino nova", "nova piumino", "Nova", "Nova", "nova 999"],
    "AUREA": ["aurea", "aurea jacket", "aurea short down jacket"],
    "IRIDIA": ["iridia", "iridia jacket", "iridia cropped"],
    "AMALIA": ["amalia", "amalia coat", "amalia long"],
    "LIVIANA": ["liviana", "liviana long"], "ARIA": ["aria"], "ARTEM": ["artem", "artem parka"],
    "VEL": ["vel", "vel gilet", "vel vest"], "VLOGO CARDIGAN": ["cardigan", "vlogo cardigan", "cardigan uomo"],
    "MISTRAL": ["mistral"], "COSIMO": ["cosimo"], "VTRACK GTX": ["vtrack", "vtrack gtx"],
    "ASTRA CAPE": ["astra", "couture astra", "astra cape"], "ASTRA OVERSIZED": ["astra oversized"],
    "VLOGO HOODIE": ["hoodie", "felpa"], "VLOGO BEANIE": ["beanie", "berretto"], "VLOGO T-SHIRT": ["t-shirt", "t shirt"],
    "JERSEY POLO": ["jersey polo"], "CAMILLA": ["gilet donna", "camilla"], "FIAMMETTA": ["fiammetta"], "MONTELUCE": ["monteluce"],
}
generic = {"*": ["down jacket", "women jacket", "men jacket", "vest", "sale", "gift card", "kids", "store locator",
                 "black jacket", "long down jacket", "short down jacket", "sneakers", "scarf", "gloves"],
           "IT": ["piumino", "piumino donna", "piumino uomo", "piumino lungo", "gilet", "saldi", "giubbotto"],
           "FR": ["doudoune", "doudoune femme", "doudoune homme", "doudoune longue", "gilet sans manches"],
           "DE": ["daunenjacke", "daunenjacke damen", "daunenweste", "mütze"], "ES": ["plumífero", "chaqueta mujer"],
           "JP": ["ダウン", "ダウンジャケット", "レディース ダウン", "値上げ"], "KR": ["패딩", "여성 패딩", "숏패딩", "롱패딩"],
           "CN": ["羽绒服", "女款羽绒服", "短款羽绒服", "双十一"], "HK": ["羽絨", "down jacket"], "TW": ["羽絨外套"]}
event_q = [
    # (countries, query, start, end, base/day, decay hl, results)
    (["KR"], "iridia pink", "2026-10-01", "2026-10-21", 260, 4, 3), (["KR"], "Iridia 핑크", "2026-10-02", "2026-10-21", 140, 4, 0),
    (["KR"], "윤하은 발렌티노", "2026-10-02", "2026-10-21", 180, 3, 0), (["KR"], "윤하은 패딩", "2026-10-02", "2026-10-21", 90, 3, 0),
    (["KR"], "발렌티노 핑크 패딩", "2026-10-02", "2026-10-21", 70, 5, 4),
    (["CN"], "尹夏恩同款", "2026-10-02", "2026-10-21", 150, 3, 0), (["CN"], "iridia 粉色", "2026-10-02", "2026-10-21", 110, 4, 3),
    (["CN"], "粉色羽绒服", "2026-10-02", "2026-10-21", 60, 5, 6), (["JP"], "イルヴァロ ピンク", "2026-10-02", "2026-10-21", 70, 4, 0),
    (["JP"], "iridia pink", "2026-10-02", "2026-10-21", 55, 4, 3), (["HK", "TW", "SG"], "iridia pink", "2026-10-02", "2026-10-21", 35, 4, 3),
    (["HK", "TW"], "尹夏恩", "2026-10-02", "2026-10-21", 25, 3, 0), (["SG", "US", "GB", "FR"], "yoon ha eun", "2026-10-02", "2026-10-21", 9, 4, 0),
    (["US", "GB", "FR", "IT", "DE"], "iridia pink", "2026-10-02", "2026-10-21", 14, 5, 3),
    (["KR"], "iridia pnk", "2026-10-02", "2026-10-14", 6, 6, 0), (["IT"], "iridia rosa", "2026-10-02", "2026-10-21", 9, 6, 0),
    (["FR"], "iridia rose", "2026-10-02", "2026-10-21", 8, 6, 0),
    (["KR"], "aurea black", "2026-09-17", "2026-10-21", 55, 30, 1), (["KR"], "Aurea 블랙", "2026-09-17", "2026-10-21", 30, 30, 0),
    (["KR"], "발렌티노 Aurea", "2026-09-17", "2026-10-21", 40, 30, 4), (["FR"], "aurea noir", "2026-09-19", "2026-10-21", 12, 40, 1),
    (["IT"], "aurea nero", "2026-09-19", "2026-10-21", 10, 40, 1), (["GB", "US"], "aurea black", "2026-09-19", "2026-10-21", 9, 40, 1),
    (["IT", "FR", "GB"], "aurea blak", "2026-09-20", "2026-10-15", 1.2, 99, 0),
    (["IT"], "amalia marrone", "2026-09-12", "2026-10-21", 9, 99, 1), (["FR"], "amalia marron", "2026-09-12", "2026-10-21", 8, 99, 1),
    (["GB", "ES"], "amalia brown", "2026-09-12", "2026-10-21", 6, 99, 1), (["IT", "FR", "GB"], "brown down coat", "2026-09-15", "2026-10-21", 5, 99, 4),
    (["IT", "FR", "DE", "GB"], "vel zip", "2026-09-29", "2026-10-21", 3, 20, 0), (["IT", "FR", "ES"], "vel zipper", "2026-09-29", "2026-10-21", 2, 20, 0),
    (["IT"], "cerniera gilet", "2026-09-30", "2026-10-21", 2, 20, 0), (["JP"], "価格改定", "2026-10-09", "2026-10-21", 25, 8, 0),
    (["CN"], "双11 价格", "2026-10-18", "2026-10-21", 40, 99, 0), (["DE", "AT", "CH"], "daunenjacke damen lang", "2026-10-12", "2026-10-19", 25, 99, 18),
    (["CN", "HK"], "astra", "2026-09-22", "2026-10-21", 45, 10, 6), (["AU"], "jersey polo", "2026-09-01", "2026-10-21", 12, 99, 9),
    (["AU"], "t-shirt", "2026-09-01", "2026-10-21", 15, 99, 11), (["AU"], "light jacket", "2026-09-10", "2026-10-21", 8, 99, 3),
]
srows = []
style_dem = pd.Series(dtype=float)
lost_style = lost.assign(style=lost.sku.str.split("-").str[0]).groupby(["date", "country", "style"]).qty.sum()
sale_style = sales.assign(style=sales.sku.str.split("-").str[0]).groupby(["date", "country", "style"]).qty.sum()
for x in DAYS:
    for c in CC:
        site = f"valentino-{c.lower()}"
        sc = 1.0 + (0.25 if x.weekday() >= 5 else 0)
        size_c = {"US": 3, "GB": 1.6, "DE": 1.5, "KR": 1.6, "CN": 1.8, "JP": 1.5, "FR": 1.2, "IT": 1.1}.get(c, 0.6)
        for q in generic["*"] + generic.get(c, []):
            n = R.poisson(6 * size_c * sc * R.uniform(0.3, 1.5))
            if n:
                srows.append((x, site, c, q, n, int(R.integers(8, 120))))
        for stname, qs in style_queries.items():
            code = C.STYLE_CODE.get(stname)
            interest = 0.0
            for src in (sale_style, lost_style):
                try:
                    interest += src.loc[(x, c, code)]
                except KeyError:
                    pass
            base_q = 1.2 * size_c + 3.0 * interest
            for qi, q in enumerate(qs):
                n = R.poisson(base_q / (1 + qi))
                if n:
                    srows.append((x, site, c, q, n, int(R.integers(2, 12))))
        for cs, q, a, b, b0, hl, res in event_q:
            if c in cs and C.d(a) <= x <= C.d(b):
                t = (x - C.d(a)).days
                lamq = b0 * (0.5 ** (t / hl)) + b0 * 0.08
                if C.d(a) == dt.date(2026, 10, 1) and t == 0:
                    lamq = b0 * 0.15    # first posts late evening KST on Oct 1
                n = R.poisson(lamq)
                if n:
                    srows.append((x, site, c, q, n, res))
srch = pd.DataFrame(srows, columns=["date_utc", "site_id", "country", "search_term", "searches", "results_count"])
srch["searches_with_click"] = (srch.searches * np.where(srch.results_count > 0, R.uniform(0.35, 0.75, len(srch)), 0)).round().astype(int)
srch["search_exits"] = (srch.searches * np.where(srch.results_count > 0, R.uniform(0.05, 0.2, len(srch)), R.uniform(0.4, 0.8, len(srch)))).round().astype(int)
srch["zero_result"] = (srch.results_count == 0).map({True: "Y", False: "N"})
# quirk: search terms are logged raw (case/whitespace variants)
m = R.random(len(srch)) < 0.07
srch.loc[m, "search_term"] = srch.loc[m, "search_term"].map(lambda s: s.upper() if R.random() < 0.5 else " " + s.title() + " ")
srch = srch.sort_values(["date_utc", "site_id", "searches"], ascending=[True, True, False])
srch.to_csv(OUT / "site_search_queries_daily.csv", index=False)
print("search rows", len(srch))
