"""Search trends: Google-Trends-like CSV exports (relative 0-100 per file), Naver-DataLab-like JSON (KR),
Baidu-index-like absolute daily index (CN)."""
import datetime as dt
import json
import math

import numpy as np
import pandas as pd

from common import OUT, d, drange, mkdir, monthly_interp, rng_for, write_json

TR = mkdir(OUT / "trends")
DAYS = pd.date_range("2024-09-01", "2026-10-21", freq="D")
t_idx = {x.date(): i for i, x in enumerate(DAYS)}
N = len(DAYS)
PUFF_N = [1.3, 0.8, 0.45, 0.25, 0.15, 0.12, 0.15, 0.3, 0.6, 1.1, 1.7, 1.9]
PUFF_S = PUFF_N[6:] + PUFF_N[:6]
PUFF_T = [1.2, 1.0, 0.8, 0.7, 0.7, 0.7, 0.75, 0.8, 0.9, 1.1, 1.3, 1.4]


def seas(curve, power=1.0):
    return np.array([monthly_interp(curve, x.date()) for x in DAYS]) ** power


S_N, S_S, S_T = seas(PUFF_N), seas(PUFF_S), seas(PUFF_T)
S_BRAND = 0.55 + 0.45 * S_N / S_N.mean()
dow = np.array([[1.08, 1.02, 0.98, 0.97, 0.95, 0.96, 1.04][x.weekday()] for x in DAYS])


def pulse(t0, peak, hl, floor=0.0, ramp=0, end=None):
    """multiplicative pulse: 1 + peak*decay, starting at t0 (date string)."""
    out = np.ones(N)
    i0 = t_idx[d(t0)]
    for i in range(max(0, i0 - ramp), N):
        if end and DAYS[i].date() > d(end):
            break
        if i < i0:
            out[i] += peak * (1 - (i0 - i) / (ramp + 1)) * 0.5
        else:
            k = (i - i0)
            out[i] += peak * (math.exp(-math.log(2) * k / hl)) + floor * (1 - math.exp(-k / 2))
    return out


def window(a, b, mult):
    out = np.ones(N)
    for i, x in enumerate(DAYS):
        if d(a) <= x.date() <= d(b):
            out[i] = mult
    return out


def launched(day):
    return np.array([1.0 if x.date() >= d(day) else 0.0 for x in DAYS])


ILV_GEO_PEAK = {"KR": 140, "JP": 120, "TW": 90, "HK": 90, "SG": 60, "CN": 90, "US": 6, "GB": 5, "FR": 7, "IT": 5, "DE": 2.5, "CH": 2, "ES": 2,
                "AU": 3, "CA": 3, "AE": 3, "NL": 2, "DK": 1.5}


def valentino_v05(geo, scale):
    base = launched("2026-09-03") * 0.02
    t0 = "2026-10-01" if geo in ("FR", "GB", "IT", "ES", "DE", "CH", "NL", "DK", "US", "CA") else "2026-10-02"
    p = pulse(t0, ILV_GEO_PEAK[geo], 3.2, floor=ILV_GEO_PEAK[geo] * 0.08)
    return scale * (base + 0.02 * (p - 1) * launched("2026-10-01"))


def series(geo, term):
    """daily 'true' search volume (arbitrary units) for geo x term."""
    r = rng_for(f"tr-{geo}-{term}")
    hemi = S_S if geo == "AU" else S_T if geo in ("SG", "AE") else S_N
    t = term.lower()
    brand = {"US": 100, "GB": 60, "IT": 45, "FR": 50, "DE": 40, "CH": 8, "ES": 20, "NL": 12, "DK": 5, "AE": 8, "CA": 18, "JP": 30, "KR": 50,
             "HK": 6, "TW": 5, "SG": 5, "AU": 8, "CN": 60}[geo]
    v = None
    if t in ("valentino", "ヴァレンティノ", "발렌티노", "华伦天奴"):
        v = brand * S_BRAND * pulse("2026-10-02", 0.35 if geo in ("KR", "JP", "TW", "HK", "SG", "CN") else 0.08, 4)
        if geo in ("US", "GB"):
            v *= window("2026-09-15", "2026-10-21", 1.07)
        if geo == "JP":
            v *= pulse("2026-10-09", 0.25, 5)
    elif "iridia" in t or "Iridia" in t or "Iridia" in t or "粉色" in t or "윤하은" in t:
        v = valentino_v05(geo, brand * 3)
        if "윤하은" in t:
            v = brand * 0.4 * (0.05 + pulse("2026-10-01", 30, 2.0) - 1) + brand * 0.6 * window("2026-08-01", "2026-12-31", 0.05)
    elif "nova" in t or "Nova" in t:
        v = brand * 0.22 * S_N
    elif "aurea" in t or "마이어" in t:
        v = brand * 0.08 * S_BRAND
        if geo == "KR":
            v *= pulse("2026-09-10", 1.6, 30, floor=1.0)
    elif "astra" in t:
        v = brand * 0.04 * launched("2026-09-10") * pulse("2026-09-24", 6 if geo == "CN" else 2.5, 6, floor=1.2 if geo == "CN" else 0.3)
    elif "vel" in t or "zipper" in t:
        v = brand * 0.03 * S_N + brand * 0.025 * launched("2026-09-27") * np.clip((np.arange(N) - t_idx[d("2026-09-27")]) / 10, 0, 1.5)
    elif "値上げ" in t:
        v = brand * 0.02 + brand * 0.4 * launched("2026-10-08") * pulse("2026-10-09", 3.0, 3.5, floor=0.6)
        v *= np.where(np.array([x.date() for x in DAYS]) < d("2026-10-08"), 1, 1)
        # past price increases (2025-03, 2025-10)
        v = v + brand * 0.25 * (pulse("2025-02-20", 1.0, 4) - 1) + brand * 0.18 * (pulse("2025-09-25", 1.0, 4) - 1)
    elif t in ("northpeak", "노스피크"):
        v = 6 * S_N * (1.4 if geo == "KR" else 1)
        if geo == "KR":
            v *= pulse("2026-10-12", 2.5, 8, floor=0.8, ramp=3)
    elif t in ("jersey polo shirt", "linen shirt"):
        v = 120 * (1.0 / (S_S if geo == "AU" else S_N) ** 0.35) * (0.9 if t == "linen shirt" else 1)
    elif "双十一" in t:
        v = 40 * S_N * (pulse("2024-10-14", 3, 10) * pulse("2025-10-20", 3, 10) * pulse("2026-10-20", 3.5, 10))
        v *= np.array([1.0 if (x.month, x.day) <= (11, 12) or x.month < 10 else 0.4 for x in DAYS])
    else:  # generic category terms (puffer etc.)
        gen = {"puffer jacket": 400, "down jacket": 150, "piumino": 300, "piumino donna": 120, "piumino uomo": 80, "parka": 60, "doudoune": 350,
               "doudoune femme": 140, "doudoune valentino": 40, "daunenjacke": 300, "winterjacke": 420, "daunenmantel": 90, "plumas": 180,
               "abrigo plumas": 70, "donsjas": 120, "winterjas": 140, "dunjakke": 90, "vinterjakke": 110, "ダウンジャケット": 380, "ダウンコート": 120,
               "패딩": 500, "롱패딩": 200, "羽絨服": 60, "羽绒服": 900, "luxury puffer": 15}.get(t, 50)
        v = gen * hemi ** 1.15
        # cold snap echo in daily signals
        if t in ("daunenjacke", "winterjacke", "daunenmantel") and geo in ("DE", "CH"):
            v *= pulse("2026-10-12", 1.6, 4.5, ramp=2) * window("2026-10-14", "2026-10-16", 1.15)
        if t in ("dunjakke", "vinterjakke") and geo == "DK":
            v *= pulse("2026-10-12", 1.2, 4.5, ramp=2)
        if t in ("donsjas", "winterjas") and geo == "NL":
            v *= pulse("2026-10-12", 1.1, 4.5, ramp=2)
        if t in ("doudoune", "doudoune femme") and geo in ("FR", "CH"):
            v *= pulse("2026-10-13", 0.35 if geo == "FR" else 1.3, 4)
        if t.startswith("piumino") and geo == "IT":
            v *= pulse("2026-10-13", 0.3, 4)
        if t == "puffer jacket" and geo == "GB":
            v *= pulse("2026-10-13", 0.25, 4)
        if t in ("ダウンジャケット", "ダウンコート"):
            v *= window("2026-09-28", "2026-10-11", 0.72) * pulse("2026-10-13", 0.35, 6)
        if t in ("패딩", "롱패딩"):
            v *= pulse("2025-10-27", 0.3, 5) * pulse("2024-11-26", 0.5, 4)
        if t == "羽绒服":
            v *= pulse("2026-10-20", 0.45, 7) * pulse("2025-10-20", 0.4, 7)
        # Black Friday bumps on generic terms
        for bf in ("2024-11-29", "2025-11-28"):
            if geo in ("US", "GB", "CA", "DE", "FR", "IT", "ES", "NL", "AU"):
                v *= pulse(bf, 0.4, 3, ramp=4)
    v = v * dow * r.lognormal(0, 0.06, N)
    return np.clip(v, 0, None)


def gt_scale(df, rng, noise=True):
    """scale to 0-100 relative to max in this export + sampling noise for small volumes; '<1' for tiny values."""
    m = df.values.max()
    out = df / m * 100
    if noise:
        out = out * rng.lognormal(0, 1, out.shape) ** (0.12 / np.sqrt(np.clip(out.values, 1, None) / 10))
    out = out.clip(upper=100)
    res = out.round(0).astype(int).astype(object)
    res[(out < 0.5) & (df > 0)] = "<1"
    return res


def week_sum(s):
    # GT weeks start on Sunday
    w = s.copy()
    w.index = [x - pd.Timedelta(days=(x.weekday() + 1) % 7) for x in s.index]
    return w.groupby(level=0).sum()


GEO_NAME = {"IT": "Italy", "FR": "France", "DE": "Germany", "CH": "Switzerland", "GB": "United Kingdom", "ES": "Spain", "NL": "Netherlands",
            "DK": "Denmark", "US": "United States", "CA": "Canada", "AE": "United Arab Emirates", "JP": "Japan", "KR": "South Korea",
            "HK": "Hong Kong", "TW": "Taiwan", "SG": "Singapore", "AU": "Australia"}
QUERIES = {
    "IT": [["valentino", "valentino nova", "valentino aurea", "valentino iridia", "valentino astra"], ["piumino", "piumino donna", "piumino uomo", "parka", "valentino"]],
    "FR": [["valentino", "valentino aurea", "valentino iridia", "valentino astra", "doudoune valentino"], ["doudoune", "doudoune femme", "parka", "valentino"]],
    "DE": [["valentino", "valentino nova", "valentino iridia", "daunenjacke", "winterjacke"], ["daunenjacke", "winterjacke", "daunenmantel", "parka"]],
    "CH": [["daunenjacke", "doudoune", "winterjacke", "valentino"]],
    "GB": [["valentino", "puffer jacket", "valentino nova", "valentino iridia", "valentino vel"], ["puffer jacket", "down jacket", "parka", "luxury puffer"]],
    "ES": [["plumas", "abrigo plumas", "valentino", "valentino nova"]],
    "NL": [["donsjas", "winterjas", "valentino"]],
    "DK": [["dunjakke", "vinterjakke", "valentino"]],
    "US": [["valentino", "puffer jacket", "valentino nova", "valentino iridia", "valentino astra"], ["valentino vest zipper", "valentino vel", "valentino iridia"]],
    "CA": [["valentino", "puffer jacket", "parka", "northpeak"]],
    "AE": [["valentino", "puffer jacket"]],
    "JP": [["ヴァレンティノ", "ヴァレンティノ Iridia", "ダウンジャケット", "ヴァレンティノ 値上げ", "ヴァレンティノ Nova"], ["ダウンジャケット", "ダウンコート", "ヴァレンティノ"]],
    "KR": [["valentino", "발렌티노", "발렌티노 Iridia", "패딩"]],
    "HK": [["羽絨服", "valentino", "valentino iridia", "华伦天奴"]],
    "TW": [["羽絨服", "valentino", "valentino iridia"]],
    "SG": [["valentino", "valentino iridia", "puffer jacket"]],
    "AU": [["puffer jacket", "valentino", "jersey polo shirt", "linen shirt"]],
}
TRUE = {}
for geo, qs in QUERIES.items():
    for q in qs:
        for term in q:
            if (geo, term) not in TRUE:
                TRUE[(geo, term)] = pd.Series(series(geo, term), index=DAYS)

W = mkdir(TR / "google_trends_like" / "weekly")
DD = mkdir(TR / "google_trends_like" / "daily_90d")
manifest = []
for geo, qs in QUERIES.items():
    for qi, q in enumerate(qs):
        r = rng_for(f"gt-{geo}-{qi}")
        dfw = pd.DataFrame({term: week_sum(TRUE[(geo, term)]) for term in q})
        dfw = dfw[dfw.index >= pd.Timestamp("2024-09-01")]
        sc = gt_scale(dfw, r)
        cols = [f"{term}: ({GEO_NAME[geo]})" for term in q]
        lines = ["Category: All categories", "", "Week," + ",".join(cols)]
        for ts, row in sc.iterrows():
            lines.append(ts.strftime("%Y-%m-%d") + "," + ",".join(str(v) for v in row.values))
        fn = f"multiTimeline_{geo}_{qi + 1}_weekly.csv"
        (W / fn).write_text("\n".join(lines) + "\n", encoding="utf-8")
        manifest.append(dict(file=f"weekly/{fn}", geo=geo, terms=" | ".join(q), timeframe="2024-09-01 2026-10-21", pulled="2026-10-22"))
        # daily last 90 days
        dfd = pd.DataFrame({term: TRUE[(geo, term)] for term in q})
        dfd = dfd[dfd.index >= pd.Timestamp("2026-07-24")]
        for pull, seed in (("2026-10-22", 0), ("2026-10-20", 1)) if geo == "DE" and qi == 0 else (("2026-10-22", 0),):
            dsub = dfd if pull == "2026-10-22" else dfd[dfd.index <= pd.Timestamp("2026-10-19")]
            if pull == "2026-10-20":
                dsub = dsub[dsub.index >= pd.Timestamp("2026-07-22") - pd.Timedelta(days=0)]
            sc = gt_scale(dsub, rng_for(f"gtd-{geo}-{qi}-{seed}"))
            lines = ["Category: All categories", "", "Day," + ",".join(cols)]
            for ts, row in sc.iterrows():
                lines.append(ts.strftime("%Y-%m-%d") + "," + ",".join(str(v) for v in row.values))
            fn = f"multiTimeline_{geo}_{qi + 1}_daily_pulled{pull.replace('-', '')}.csv"
            (DD / fn).write_text("\n".join(lines) + "\n", encoding="utf-8")
            manifest.append(dict(file=f"daily_90d/{fn}", geo=geo, terms=" | ".join(q), timeframe=f"{dsub.index.min().date()} {dsub.index.max().date()}", pulled=pull))
pd.DataFrame(manifest).to_csv(TR / "google_trends_like" / "pulls_log.csv", index=False)
(TR / "google_trends_like" / "README.txt").write_text(
    "Exports from the search-interest explorer (web UI, 'Download CSV').\n"
    "Values are relative: 100 = peak popularity within THAT export (all terms, whole timeframe, that geo). Not comparable across files.\n"
    "Weekly exports: weeks start on Sunday. Daily exports: last 90 days. '<1' = some interest but below 1.\n"
    "Values are computed on a sample of searches and change slightly between pulls.\n", encoding="utf-8")

# ---------------------------------------------------------------------------------------------- Naver DataLab-like (KR)
groups = [("발렌티노", ["발렌티노", "몽클레어", "valentino"]), ("발렌티노 Iridia", ["Iridia", "발렌티노 Iridia", "발렌티노 핑크패딩"]),
          ("발렌티노 마이어", ["마이어", "발렌티노 마이어", "마이어 블랙"]), ("패딩", ["패딩", "롱패딩", "숏패딩"]), ("노스피크", ["노스피크", "노스피크 팝업"])]
gvals = {"발렌티노": series("KR", "발렌티노") * 1.1, "발렌티노 Iridia": series("KR", "발렌티노 Iridia") + series("KR", "윤하은 패딩") * 0.3,
         "발렌티노 마이어": series("KR", "발렌티노 마이어"), "패딩": series("KR", "패딩") + series("KR", "롱패딩"), "노스피크": series("KR", "노스피크")}
for unit, start in (("week", "2024-09-01"), ("date", "2026-08-01")):
    idx = DAYS[DAYS >= pd.Timestamp(start)]
    data = {}
    for name, vals in gvals.items():
        s = pd.Series(vals, index=DAYS)[idx]
        if unit == "week":  # Naver weeks start Monday
            s.index = [x - pd.Timedelta(days=x.weekday()) for x in s.index]
            s = s.groupby(level=0).sum()
        data[name] = s
    mx = max(s.max() for s in data.values())
    results = []
    for name, kws in groups:
        s = data[name]
        results.append({"title": name, "keywords": kws, "data": [{"period": p.strftime("%Y-%m-%d"), "ratio": round(float(v / mx * 100), 5)} for p, v in s.items()]})
    obj = {"startDate": idx.min().strftime("%Y-%m-%d"), "endDate": "2026-10-21", "timeUnit": unit, "results": results}
    write_json(mkdir(TR / "naver_datalab_like") / f"search_trend_{unit}_{start.replace('-', '')}_20261021.json", obj, indent=1)
(TR / "naver_datalab_like" / "README.txt").write_text(
    "통합검색어 트렌드 API 응답 (PC+모바일, 전체 성별/연령). ratio: 조회 기간 내 최대 검색량을 100으로 한 상대값 (요청 단위로 산출).\n"
    "주간 단위는 월요일 시작.\n", encoding="utf-8")

# ---------------------------------------------------------------------------------------------- Baidu-index-like (CN), absolute
cn_terms = ["华伦天奴", "valentino", "华伦天奴 粉色 羽绒服", "华伦天奴 astra", "羽绒服", "双十一 羽绒服"]
rows = ["日期,关键词,整体日均值,PC端,移动端"]
r = rng_for("baidu")
for term in cn_terms:
    if term == "华伦天奴 粉色 羽绒服":
        v = series("CN", "华伦天奴 粉色 羽绒服") * 9 + 60
    elif term == "华伦天奴 astra":
        v = series("CN", "华伦天奴 astra") * 40
    elif term == "valentino":
        v = series("CN", "valentino") * 25
    elif term == "华伦天奴":
        v = series("CN", "华伦天奴") * 45
    elif term == "羽绒服":
        v = series("CN", "羽绒服") * 30
    else:
        v = series("CN", "双十一 羽绒服") * 20
    for x, val in zip(DAYS, v):
        if d("2025-06-03") <= x.date() <= d("2025-06-09"):
            continue  # index outage
        tot = int(val)
        pc = int(tot * r.uniform(0.12, 0.2))
        rows.append(f"{x.strftime('%Y-%m-%d')},{term},{tot},{pc},{tot - pc}")
mkdir(TR / "baidu_index_like")
(TR / "baidu_index_like" / "搜索指数_daily_20240901_20261021.csv").write_text("﻿" + "\n".join(rows) + "\n", encoding="utf-8")
(TR / "baidu_index_like" / "说明.txt").write_text("搜索指数：以网民搜索量为基础的加权和（绝对值，非0-100归一化）。PC端+移动端=整体。2025-06-03至06-09数据缺失。\n",
                                                  encoding="utf-8")
print("trends done", len(manifest))
