"""FX: ECB-like reference rates (XML + CSV), TWD fixing (ROC dates), commercial USD-base feed incl. AED/TWD."""
import datetime as dt
import json

import numpy as np
import pandas as pd
from dateutil.easter import easter

from common import HIST_START, LAST_DAY, OUT, d, drange, mkdir, rng_for, write_json

F = mkdir(OUT / "fx")
DAYS = drange(HIST_START, dt.date(2026, 10, 22))

# anchors: local currency per 1 EUR (TWD/AED handled via USD)
ANCH = {
    "USD": [("2024-09-01", 1.105), ("2024-10-01", 1.112), ("2024-11-01", 1.087), ("2024-12-02", 1.052), ("2025-01-13", 1.024),
            ("2025-02-03", 1.032), ("2025-03-03", 1.048), ("2025-04-01", 1.081), ("2025-05-02", 1.131), ("2025-06-02", 1.138),
            ("2025-07-01", 1.179), ("2025-08-01", 1.152), ("2025-09-01", 1.168), ("2025-10-01", 1.172), ("2025-11-03", 1.154),
            ("2025-12-01", 1.161), ("2026-01-02", 1.172), ("2026-03-02", 1.158), ("2026-05-04", 1.139), ("2026-07-01", 1.167),
            ("2026-09-01", 1.174), ("2026-10-22", 1.161)],
    "JPY": [("2024-09-01", 159.5), ("2024-10-01", 160.2), ("2024-11-01", 165.4), ("2024-12-02", 158.6), ("2025-01-13", 161.0),
            ("2025-03-03", 157.4), ("2025-04-01", 161.8), ("2025-05-02", 163.9), ("2025-06-02", 163.0), ("2025-07-01", 169.4),
            ("2025-08-01", 171.2), ("2025-09-01", 172.0), ("2025-10-01", 173.6), ("2025-11-03", 174.9), ("2025-12-01", 173.8),
            ("2026-01-02", 172.5), ("2026-03-02", 170.1), ("2026-05-04", 168.8), ("2026-07-01", 171.9), ("2026-09-01", 173.4),
            ("2026-10-22", 174.6)],
    "KRW": [("2024-09-01", 1478), ("2024-10-01", 1462), ("2024-11-01", 1498), ("2024-12-02", 1474), ("2024-12-09", 1531), ("2025-01-13", 1508),
            ("2025-03-03", 1521), ("2025-04-09", 1641), ("2025-05-02", 1591), ("2025-06-02", 1556), ("2025-07-01", 1598),
            ("2025-08-01", 1604), ("2025-09-01", 1625), ("2025-10-01", 1638), ("2025-11-03", 1646), ("2025-12-01", 1641),
            ("2026-01-02", 1622), ("2026-03-02", 1606), ("2026-05-04", 1588), ("2026-07-01", 1611), ("2026-09-01", 1629), ("2026-10-22", 1643)],
    "CNY": [("2024-09-01", 7.86), ("2024-10-01", 7.82), ("2024-11-01", 7.74), ("2024-12-02", 7.64), ("2025-01-13", 7.51 + 0.1),
            ("2025-03-03", 7.63), ("2025-04-01", 7.86), ("2025-05-02", 8.17), ("2025-06-02", 8.18), ("2025-07-01", 8.27),
            ("2025-08-01", 8.24), ("2025-09-01", 8.26), ("2025-10-01", 8.28), ("2025-11-03", 8.21), ("2026-01-02", 8.19),
            ("2026-03-02", 8.12), ("2026-05-04", 8.05), ("2026-07-01", 8.17), ("2026-09-01", 8.22), ("2026-10-22", 8.21)],
    "GBP": [("2024-09-01", 0.842), ("2024-11-01", 0.838), ("2025-01-13", 0.838), ("2025-03-03", 0.826), ("2025-04-14", 0.862),
            ("2025-06-02", 0.843), ("2025-08-01", 0.867), ("2025-10-01", 0.873), ("2025-12-01", 0.879), ("2026-03-02", 0.868),
            ("2026-06-01", 0.861), ("2026-09-01", 0.869), ("2026-10-22", 0.874)],
    "CHF": [("2024-09-01", 0.941), ("2024-11-01", 0.939), ("2025-01-13", 0.937), ("2025-04-14", 0.927), ("2025-07-01", 0.934),
            ("2025-10-01", 0.932), ("2026-01-02", 0.929), ("2026-04-01", 0.936), ("2026-07-01", 0.931), ("2026-10-22", 0.925)],
    "DKK": [("2024-09-01", 7.4589), ("2025-06-01", 7.4602), ("2026-10-22", 7.4651)],
    "CAD": [("2024-09-01", 1.493), ("2024-12-02", 1.476), ("2025-02-03", 1.495), ("2025-03-10", 1.563), ("2025-05-02", 1.565),
            ("2025-07-01", 1.603), ("2025-10-01", 1.633), ("2026-01-02", 1.611), ("2026-05-04", 1.589), ("2026-09-01", 1.618), ("2026-10-22", 1.612)],
    "SGD": [("2024-09-01", 1.443), ("2024-12-02", 1.412), ("2025-02-03", 1.405), ("2025-05-02", 1.468), ("2025-07-01", 1.497),
            ("2025-10-01", 1.511), ("2026-01-02", 1.503), ("2026-05-04", 1.486), ("2026-09-01", 1.507), ("2026-10-22", 1.499)],
    "AUD": [("2024-09-01", 1.633), ("2024-12-02", 1.618), ("2025-02-03", 1.665), ("2025-04-09", 1.789), ("2025-06-02", 1.761),
            ("2025-08-01", 1.787), ("2025-10-01", 1.771), ("2026-01-02", 1.753), ("2026-05-04", 1.741), ("2026-09-01", 1.768), ("2026-10-22", 1.776)],
}
VOL = {"USD": 0.0042, "JPY": 0.0058, "KRW": 0.0050, "CNY": 0.0036, "GBP": 0.0030, "CHF": 0.0028, "DKK": 0.00006, "CAD": 0.0040,
       "SGD": 0.0026, "AUD": 0.0052}
USD_TWD = [("2024-09-01", 31.95), ("2024-11-01", 32.10), ("2025-01-13", 33.05), ("2025-04-01", 33.18), ("2025-05-05", 29.95),
           ("2025-07-01", 29.25), ("2025-09-01", 30.55), ("2025-11-03", 30.80), ("2026-01-02", 31.10), ("2026-05-04", 30.40),
           ("2026-09-01", 30.65), ("2026-10-22", 30.92)]
USD_HKD = [("2024-09-01", 7.797), ("2024-12-02", 7.781), ("2025-04-01", 7.776), ("2025-05-02", 7.752), ("2025-06-16", 7.848),
           ("2025-08-15", 7.849), ("2025-10-01", 7.781), ("2026-02-02", 7.802), ("2026-06-01", 7.823), ("2026-10-22", 7.789)]


def bridge(anchors, vol, name, days=DAYS):
    rng = rng_for("fx-" + name)
    t = np.array([(x - days[0]).days for x in days], dtype=float)
    at = np.array([(d(a) - days[0]).days for a, _ in anchors], dtype=float)
    av = np.log([v for _, v in anchors])
    base = np.interp(t, at, av)
    # brownian bridge noise between anchors
    noise = np.zeros(len(days))
    for j in range(len(at) - 1):
        m = (t >= at[j]) & (t <= at[j + 1])
        n = m.sum()
        w = np.cumsum(rng.normal(0, vol * 0.55, n))
        lin = np.linspace(0, w[-1], n)
        noise[m] = w - lin
    return np.exp(base + noise)


series = {c: bridge(a, VOL[c], c) for c, a in ANCH.items()}
twd = bridge(USD_TWD, 0.0028, "TWD")
hkd = bridge(USD_HKD, 0.0006, "HKD")
series["HKD"] = series["USD"] * hkd
series["TWD"] = series["USD"] * twd
series["AED"] = series["USD"] * 3.6725
df = pd.DataFrame(series, index=pd.to_datetime(DAYS))


def target_closed(x):
    e = easter(x.year)
    return x.weekday() >= 5 or (x.month, x.day) in ((1, 1), (5, 1), (12, 25), (12, 26)) or x in (e - dt.timedelta(days=2), e + dt.timedelta(days=1))


ECB_CCY = ["USD", "JPY", "BGN", "CZK", "DKK", "GBP", "HUF", "PLN", "RON", "SEK", "CHF", "ISK", "NOK", "TRY", "AUD", "BRL", "CAD", "CNY",
           "HKD", "IDR", "ILS", "INR", "KRW", "MXN", "MYR", "NZD", "PHP", "SGD", "THB", "ZAR"]
EXTRA = {"BGN": (1.9558, 0.0), "CZK": (25.1, 0.002), "HUF": (398.0, 0.004), "PLN": (4.27, 0.003), "RON": (4.98, 0.0015), "SEK": (11.3, 0.004),
         "ISK": (148.0, 0.003), "NOK": (11.6, 0.005), "TRY": (39.0, 0.003), "BRL": (6.2, 0.007), "IDR": (18200.0, 0.004), "ILS": (4.05, 0.005),
         "INR": (95.0, 0.003), "MXN": (21.0, 0.006), "MYR": (4.95, 0.003), "NZD": (1.90, 0.005), "PHP": (64.0, 0.003), "THB": (38.5, 0.004),
         "ZAR": (20.4, 0.008)}
for c, (lvl, v) in EXTRA.items():
    df[c] = bridge([("2024-09-01", lvl), ("2026-10-22", lvl * (1.15 if c == "TRY" else 1.0) * (1.0 if c != "TRY" else 1.0))], v, c)
df["TRY"] = df["TRY"] * np.linspace(1.0, 1.42, len(df))  # lira depreciation
DEC = {"JPY": 2, "KRW": 2, "HUF": 2, "ISK": 1, "IDR": 2, "INR": 4, "PHP": 3, "THB": 3, "CZK": 3}
ecb = df[[not target_closed(x.date()) for x in df.index]]
ecb = ecb[ecb.index <= pd.Timestamp(LAST_DAY)]
# missing publication day (data glitch)
ecb = ecb.drop(pd.Timestamp("2025-08-14"))


def fmt(c, v):
    if c == "BGN":
        return "1.9558"
    return f"{v:.{DEC.get(c, 4)}f}"


# XML (newest first)
lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<gesmes:Envelope xmlns:gesmes="http://www.gesmes.org/xml/2002-08-01" xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref">',
         "\t<gesmes:subject>Reference rates</gesmes:subject>", "\t<gesmes:Sender>", "\t\t<gesmes:name>Euro area reference rates (mirror)</gesmes:name>",
         "\t</gesmes:Sender>", "\t<Cube>"]
for ts, r in ecb.iloc[::-1].iterrows():
    lines.append(f"\t\t<Cube time=\"{ts.date().isoformat()}\">")
    for c in ECB_CCY:
        if c == "BGN" and ts.year >= 2026:
            continue  # Bulgaria joined the euro area on 1 Jan 2026
        lines.append(f"\t\t\t<Cube currency=\"{c}\" rate=\"{fmt(c, r[c])}\"/>")
    lines.append("\t\t</Cube>")
lines += ["\t</Cube>", "</gesmes:Envelope>"]
mkdir(F / "ecb_reference")
(F / "ecb_reference" / "eurofxref-hist-20240901-20261021.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
# CSV (ECB style, newest first, trailing comma, N/A columns for discontinued ccys)
hdr = ["Date"] + ECB_CCY[:2] + ["CYP"] + ECB_CCY[2:]
rows = [",".join(hdr) + ","]
for ts, r in ecb.iloc[::-1].iterrows():
    vals = [ts.date().isoformat()] + [fmt(c, r[c]) for c in ECB_CCY[:2]] + ["N/A"] + [("N/A" if c == "BGN" and ts.year >= 2026 else fmt(c, r[c])) for c in ECB_CCY[2:]]
    rows.append(",".join(vals) + ",")
(F / "ecb_reference" / "eurofxref-hist.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
(F / "ecb_reference" / "README.txt").write_text(
    "Euro foreign exchange reference rates (mirror of the official daily publication, ~16:00 CET).\n"
    "Quoted as units of currency per 1 EUR. Published on TARGET business days only (no weekends, 1 Jan, Good Friday,\n"
    "Easter Monday, 1 May, 25-26 Dec). TWD and AED are not part of the reference basket.\n", encoding="utf-8")

# TWD fixing - Taipei interbank close, USD/TWD, ROC calendar dates, Taiwan holidays missing
TW_HOL = {"2024-10-10", "2025-01-01", "2025-01-27", "2025-01-28", "2025-01-29", "2025-01-30", "2025-01-31", "2025-02-28", "2025-04-03", "2025-04-04",
          "2025-05-01", "2025-05-30", "2025-10-06", "2025-10-10", "2025-10-24", "2025-12-25", "2026-01-01", "2026-02-16", "2026-02-17", "2026-02-18",
          "2026-02-19", "2026-02-20", "2026-02-27", "2026-04-03", "2026-04-06", "2026-05-01", "2026-06-19", "2026-09-25", "2026-09-28", "2026-10-09",
          "2026-10-26", "2024-09-17"}
rows = ["日期,美元/新台幣 收盤匯率,交易量(億美元)"]
rr = rng_for("twd")
for ts, v in zip(df.index, twd):
    x = ts.date()
    if x.weekday() >= 5 or x.isoformat() in TW_HOL or x > LAST_DAY:
        continue
    rows.append(f"{x.year - 1911}/{x.month:02d}/{x.day:02d},{v:.3f},{rr.uniform(6, 22):.2f}")
mkdir(F / "twd_fixing")
(F / "twd_fixing" / "USDTWD_close_113-115.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

# commercial feed: USD base, daily incl. weekends, UTC 23:59 snapshot, includes "today" partial
rr = rng_for("comm")
out = []
for ts, r in df.iterrows():
    x = ts.date()
    q = {c: round(r[c] / r["USD"] * float(rr.normal(1, 0.0004)), 6 if c not in ("JPY", "KRW", "IDR") else 3)
         for c in ["EUR", "JPY", "KRW", "CNY", "GBP", "CHF", "DKK", "CAD", "HKD", "TWD", "SGD", "AUD", "AED"] if c != "EUR"}
    q["EUR"] = round(1 / r["USD"] * float(rr.normal(1, 0.0003)), 6)
    q["AED"] = 3.6725
    snap = f"{x.isoformat()}T23:59:59Z" if x < dt.date(2026, 10, 22) else "2026-10-22T07:15:02Z"
    out.append({"timestamp": snap, "base": "USD", "rates": q})
with open(mkdir(F / "fxfeed_usd_base") / "daily_snapshots.jsonl", "w") as f:
    for o in out:
        f.write(json.dumps(o) + "\n")
(F / "fxfeed_usd_base" / "README.txt").write_text("Commercial mid-market snapshot feed. Base USD (units of currency per 1 USD). One snapshot/day at 23:59:59 UTC,\n"
                                                  "weekends included. Last record is intraday.\n", encoding="utf-8")
# truth for testers
df.round(5).to_csv(OUT.parents[1] / "ground_truth" / "canonical" / "external_fx_truth_per_EUR.csv", index_label="date")
print("fx done", len(ecb))
