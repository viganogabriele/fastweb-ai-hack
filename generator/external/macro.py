"""Macro: consumer confidence (monthly, mixed scales), fictional luxury equity index (daily), China retail sales (monthly)."""
import numpy as np
import pandas as pd

from common import OUT, mkdir, rng_for

M = mkdir(OUT / "macro")
r = rng_for("macro")
months = pd.period_range("2024-09", "2026-09", freq="M")

CC = {  # level, sd, scale description
    "EA": (-14.0, 0.9, "balance of opinion (DG ECFIN-style, SA)"), "IT": (-15.5, 1.1, "balance"), "FR": (-19.0, 1.3, "balance"),
    "DE": (-21.0, 1.2, "balance"), "ES": (-12.0, 1.2, "balance"), "NL": (-28.0, 1.5, "balance"), "DK": (-11.0, 1.5, "balance"),
    "US": (98.0, 3.0, "index 1985=100"), "JP": (34.5, 0.7, "index (Cabinet Office-style)"), "KR": (101.0, 2.5, "CCSI, long-run avg=100"),
    "CN": (88.0, 1.0, "index (NBS-style), 100=neutral"), "GB": (-21.0, 2.0, "balance (GfK-style)"), "AU": (88.0, 3.0, "index (Westpac-MI-style)")}
SHOCK = {"2025-04": -3.0, "2025-05": -2.0, "2024-12": -1.5}
rows = []
for c, (lvl, sd, desc) in CC.items():
    x = lvl
    for p in months:
        x = lvl + 0.8 * (x - lvl) + r.normal(0, sd)
        v = x + SHOCK.get(str(p), 0) * (sd if c not in ("EA", "IT", "FR", "DE", "ES", "NL", "DK", "GB") else 1)
        if c == "KR" and str(p) == "2024-12":
            v -= 12  # political turmoil
        if c == "JP" and p >= pd.Period("2026-08", "M"):
            v += 0.6
        rows.append([c, str(p), round(v, 1), desc, "final" if p < pd.Period("2026-09", "M") else "first release"])
rows.append(["EA", "2026-10", -13.6, "balance of opinion (DG ECFIN-style, SA)", "flash"])
pd.DataFrame(rows, columns=["geo", "month", "value", "scale", "release"]).to_csv(M / "consumer_confidence_monthly.csv", index=False)

# fictional luxury equity index
bd = pd.bdate_range("2024-09-02", "2026-10-21")
ret = r.normal(0.0002, 0.012, len(bd))
for day, shock in (("2025-04-03", -0.055), ("2025-04-04", -0.04), ("2025-04-07", -0.03), ("2025-04-10", 0.06), ("2024-09-24", 0.045),
                   ("2024-09-26", 0.03), ("2025-10-15", 0.035), ("2026-07-24", -0.028), ("2026-10-14", 0.021)):
    ret[bd.get_loc(pd.Timestamp(day))] += shock
lvl = 1000 * np.exp(np.cumsum(ret))
df = pd.DataFrame({"date": bd.strftime("%Y-%m-%d"), "close": lvl.round(2), "volume_mn_eur": (r.lognormal(6.5, 0.3, len(bd))).round(1)})
df = df[~df.date.isin(["2024-12-25", "2024-12-26", "2025-01-01", "2025-04-18", "2025-04-21", "2025-12-25", "2025-12-26", "2026-01-01", "2026-04-03", "2026-04-06"])]
df.to_csv(M / "lux_leaders_25_index_daily.csv", index=False)
(M / "README.txt").write_text("consumer_confidence_monthly.csv: national sources, NOT on a common scale (see 'scale').\n"
                              "lux_leaders_25_index_daily.csv: price index of 25 listed luxury-goods companies (base 2024-09-02 = 1000, EUR).\n"
                              "china_retail_sales_monthly.csv: yoy % nominal; Jan-Feb published combined.\n", encoding="utf-8")

# China retail sales
rows = []
for p in months:
    if p.month == 1:
        continue
    tot = 3.5 + r.normal(0, 1.0) + (1.5 if p.month == 10 else 0)
    cloth = tot - 1.0 + r.normal(0, 2.2) + (2.0 if str(p) in ("2025-11", "2024-11") else 0)
    jew = tot + 2 + r.normal(0, 4)
    rows.append([("%d-01/02" % p.year) if p.month == 2 else str(p), round(tot, 1), round(cloth, 1), round(jew, 1)])
pd.DataFrame(rows, columns=["period", "total_retail_sales_yoy_pct", "garments_footwear_hats_textiles_yoy_pct", "gold_silver_jewellery_yoy_pct"]).to_csv(
    M / "china_retail_sales_monthly.csv", index=False)
print("macro done")
