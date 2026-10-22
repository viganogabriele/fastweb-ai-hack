"""Weather: daily observations for every store city from heterogeneous 'providers', Venice tide gauge, 10-day forecast.

Run: .venv/bin/python generator/external/weather.py
"""
import csv
import datetime as dt
import io
import json
import math

import numpy as np
import pandas as pd

from common import CITIES, HIST_START, LAST_DAY, OUT, TODAY, d, drange, mkdir, monthly_interp, rng_for, write_json

W = mkdir(OUT / "weather")
DATES = drange(HIST_START, LAST_DAY)
N = len(DATES)
DIDX = {x: i for i, x in enumerate(DATES)}

TSD = {"SEU": 2.3, "ALPS": 3.0, "WEU": 2.6, "CEU": 3.2, "IBE": 2.4, "NEU": 2.8, "ME": 1.4, "USE": 3.6, "USS": 1.4,
       "USW": 2.2, "USM": 4.0, "JPN": 2.0, "KOR": 2.6, "CHE": 2.4, "CHN": 3.0, "CHW": 2.0, "SCN": 1.4, "SEA": 0.7, "AUS": 2.6}
SUPER = {"SEU": "EU", "ALPS": "EU", "WEU": "EU", "CEU": "EU", "IBE": "EU", "NEU": "EU", "ME": "ME", "USE": "NA", "USS": "NA",
         "USW": "NAW", "USM": "NAW", "JPN": "EA", "KOR": "EA", "CHE": "EA", "CHN": "EA", "CHW": "EA", "SCN": "EA", "SEA": "SEA", "AUS": "AUS"}


def ar1(rng, n, phi, sd):
    x = np.zeros(n)
    e = rng.normal(0, sd * math.sqrt(1 - phi ** 2), n)
    x[0] = rng.normal(0, sd)
    for i in range(1, n):
        x[i] = phi * x[i - 1] + e[i]
    return x


def daylength(lat, day):
    decl = 23.44 * math.sin(math.radians(360 / 365 * (day.timetuple().tm_yday - 81)))
    c = -math.tan(math.radians(lat)) * math.tan(math.radians(decl))
    c = max(-1, min(1, c))
    return 2 * math.degrees(math.acos(c)) / 15


# ---------------------------------------------------------------------------------------------- truth model
rg = rng_for("weather-latent")
SUPER_SERIES = {k: ar1(rg, N, 0.8, 1.0) for k in set(SUPER.values())}
REG_SERIES = {k: ar1(rg, N, 0.75, 1.0) for k in TSD}


def simulate_city(key, c):
    rng = rng_for("wx-" + key)
    reg = c["region"]
    sd = TSD[reg]
    local = ar1(rng, N, 0.6, 1.0)
    anom = sd * (0.55 * SUPER_SERIES[SUPER[reg]] + 0.6 * REG_SERIES[reg] + 0.45 * local)
    rows = []
    wet_prev = False
    depth = 0.0
    for i, x in enumerate(DATES):
        m = x.month - 1
        tx = monthly_interp(c["tmax"], x)
        tn = monthly_interp(c["tmin"], x)
        P = monthly_interp(c["pr"], x)
        p = min(0.62, max(0.02, 0.05 + 0.0032 * P))
        if reg in ("SEA",):
            p = min(0.7, 0.3 + 0.001 * P)
        p11 = p + 0.35 * (1 - p)
        p01 = p * (1 - p11) / (1 - p)
        wet = rng.random() < (p11 if wet_prev else p01)
        wet_prev = wet
        mean_amt = P / (30.4 * p)
        prcp = float(rng.gamma(0.75, mean_amt / 0.75)) if wet else 0.0
        if wet and prcp < 0.2:
            prcp = 0.2
        a = anom[i]
        tmax = tx + a - (1.6 if wet else -0.3) + rng.normal(0, 0.7)
        tmin = tn + 0.8 * a + (0.6 if wet else -0.2) + rng.normal(0, 0.7)
        if tmin > tmax - 1.5:
            tmin = tmax - 1.5 - abs(rng.normal(0, 0.5))
        rh = monthly_interp(c["rh"], x) + (9 if wet else -2) + rng.normal(0, 5)
        wind = monthly_interp(c["wind"], x) * float(rng.lognormal(0, 0.28)) * (1.12 if wet else 0.95)
        cloud = min(100, max(0, (78 if wet else 35) + rng.normal(0, 22)))
        rows.append([x, tmax, tmin, prcp, rh, wind, cloud])
    df = pd.DataFrame(rows, columns=["date", "tmax", "tmin", "prcp", "rh", "wind", "cloud"])
    df["wind_dir"] = (rng.normal(240 if c["lat"] > 30 else 90, 70, N) % 360).round(0)
    df["press"] = 1015 + rng.normal(0, 7, N) - df.prcp.clip(0, 30) * 0.25 - (c["elev"] / 8.5 if c["elev"] > 1000 else 0) * 0
    return df


def finish(df, c):
    """Derive snow, depth, gust, sunshine, condition after scenario overrides."""
    tmean = (df.tmax + df.tmin) / 2
    snow = np.where((df.prcp > 0) & (tmean <= 0.8), df.prcp * 1.0, np.where((df.prcp > 0) & (tmean < 2.2), df.prcp * 0.35, 0.0))
    if "snow_override" in df:
        so = pd.to_numeric(df.snow_override)
        snow = np.where(so.notna(), so, snow).astype(float)
    df["snow"] = np.round(snow, 1)
    depth, dep = 0.0, []
    for s, tx, pr in zip(df.snow, df.tmax, df.prcp):
        depth = max(0.0, depth + s - max(0.0, tx) * 0.9 - (pr * 0.3 if s == 0 else 0))
        dep.append(round(depth))
    df["snow_depth"] = dep
    rng = rng_for("finish-" + c["name"])
    df["gust"] = (df.wind * rng.uniform(1.8, 2.6, len(df)) + rng.normal(4, 3, len(df))).clip(lower=8)
    if "gust_override" in df:
        go = pd.to_numeric(df.gust_override)
        df["gust"] = np.where(go.notna(), go, df.gust).astype(float)
    df["wind_max"] = df.wind * rng.uniform(1.35, 1.7, len(df))
    df["rh"] = df.rh.clip(18, 99)
    df["sun"] = [max(0.0, daylength(c["lat"], x) * (1 - cl / 100) * 0.92) for x, cl in zip(df.date, df.cloud)]
    conds = []
    for r in df.itertuples():
        summer = (r.date.month in (5, 6, 7, 8, 9)) if c["lat"] > 0 else (r.date.month in (11, 12, 1, 2, 3))
        if getattr(r, "cond_override", None) and isinstance(r.cond_override, str):
            conds.append(r.cond_override)
        elif r.snow > 0 and r.snow >= r.prcp * 0.9:
            conds.append("heavy_snow" if r.snow > 8 else "snow" if r.snow > 1.5 else "light_snow")
        elif r.snow > 0:
            conds.append("sleet")
        elif r.prcp >= 25 and summer:
            conds.append("thunder")
        elif r.prcp >= 15:
            conds.append("heavy_rain")
        elif r.prcp >= 3:
            conds.append("showers" if summer and rng.random() < 0.5 else "rain")
        elif r.prcp > 0:
            conds.append("drizzle" if r.prcp < 1 else "light_rain")
        elif r.rh > 92 and r.wind < 7 and r.date.month in (10, 11, 12, 1, 2):
            conds.append("fog")
        elif c["cc"] == "AE" and rng.random() < 0.06:
            conds.append("dust")
        elif c["cc"] == "CN" and r.date.month in (10, 11, 12, 1, 2, 3) and rng.random() < 0.15:
            conds.append("haze")
        elif r.cloud < 20:
            conds.append("clear")
        elif r.cloud < 45:
            conds.append("mainly_clear")
        elif r.cloud < 75:
            conds.append("partly_cloudy")
        else:
            conds.append("overcast")
    df["cond"] = conds
    return df


def set_day(df, day, **kw):
    i = DIDX[d(day)]
    for k, v in kw.items():
        if k not in df:
            df[k] = None if k.endswith("override") else np.nan
            df[k] = df[k].astype(object) if k == "cond_override" else df[k]
        df.at[i, k] = v


TRUTH = {k: simulate_city(k, c) for k, c in CITIES.items()}

# ------------------------------------------------------------------ scenario: cold snap Central/Northern Europe
COLD = {  # day -> base tmax for a "lowland" cold-snap city
    "2026-10-10": 13.5, "2026-10-11": 10.5, "2026-10-12": 7.5, "2026-10-13": 5.0, "2026-10-14": 3.0, "2026-10-15": 2.4,
    "2026-10-16": 3.4, "2026-10-17": 4.2, "2026-10-18": 5.0, "2026-10-19": 5.8, "2026-10-20": 8.6, "2026-10-21": 10.8}
COLD_OFF = {"MUENCHEN": 0.0, "BERLIN": 1.0, "ZUERICH": 0.5, "STMORITZ": -5.5, "KOBENHAVN": 1.3, "AMSTERDAM": 1.6, "GENEVE": 0.9,
            "COURMAYEUR": -3.0, "CORTINA": -3.5}
for key, off in COLD_OFF.items():
    df = TRUTH[key]
    r = rng_for("cold-" + key)
    for day, base in COLD.items():
        tx = base + off + r.normal(0, 0.5)
        tn = tx - r.uniform(3.5, 6.0)
        set_day(df, day, tmax=round(tx, 1), tmin=round(tn, 1), rh=float(r.uniform(72, 92)), cloud=float(r.uniform(55, 95)))
        df.at[DIDX[d(day)], "prcp"] = 0.0 if r.random() < 0.45 else round(float(r.gamma(1.2, 2.0)), 1)
    # cold front passage
    set_day(df, "2026-10-11", prcp=round(float(r.uniform(6, 14)), 1), wind=float(r.uniform(18, 26)), cloud=95.0)
    set_day(df, "2026-10-12", wind=float(r.uniform(20, 30)))
munich = TRUTH["MUENCHEN"]
set_day(munich, "2026-10-13", prcp=7.8, tmax=4.6, tmin=0.9, snow_override=0.0, cond_override="rain")
set_day(munich, "2026-10-14", prcp=6.9, tmax=2.1, tmin=-0.8, snow_override=7.0, cond_override="snow")
set_day(munich, "2026-10-15", prcp=2.2, tmax=2.6, tmin=-2.9, snow_override=2.4, cond_override="light_snow")
set_day(munich, "2026-10-16", prcp=0.0, tmax=3.8, tmin=-3.4, cloud=30.0)
stm = TRUTH["STMORITZ"]
for day, pr, sn in [("2026-10-13", 17.0, 18.0), ("2026-10-14", 21.5, 23.0), ("2026-10-15", 5.4, 6.0), ("2026-10-16", 0.0, 0.0)]:
    set_day(stm, day, prcp=pr, snow_override=sn)
zrh = TRUTH["ZUERICH"]
set_day(zrh, "2026-10-13", prcp=9.4, tmax=4.9, tmin=1.6, snow_override=0.0, cond_override="rain")
set_day(zrh, "2026-10-14", prcp=12.2, tmax=2.9, tmin=0.4, snow_override=0.6, cond_override="sleet")
set_day(zrh, "2026-10-15", prcp=1.1, tmax=3.1, tmin=-0.6, snow_override=0.0, cond_override="overcast")
gva = TRUTH["GENEVE"]
set_day(gva, "2026-10-13", prcp=14.8, tmax=5.6, tmin=2.4, snow_override=0.0, cond_override="rain")
set_day(gva, "2026-10-14", prcp=4.0, tmax=3.9, tmin=0.6, snow_override=0.0)
for day in ("2026-10-15", "2026-10-16", "2026-10-17"):
    set_day(gva, day, prcp=0.0, wind=float(rng_for(day).uniform(26, 34)), gust_override=float(rng_for(day + "g").uniform(62, 78)), cloud=40.0)
ber = TRUTH["BERLIN"]
set_day(ber, "2026-10-15", prcp=1.4, tmax=3.1, tmin=-0.9, snow_override=0.5, cond_override="light_snow")
ams = TRUTH["AMSTERDAM"]
set_day(ams, "2026-10-13", prcp=11.6, wind=34.0, gust_override=78.0, cond_override="heavy_rain")
cph = TRUTH["KOBENHAVN"]
set_day(cph, "2026-10-14", prcp=3.2, wind=31.0, gust_override=69.0, snow_override=0.0, cond_override="showers")
for key in ("COURMAYEUR", "CORTINA"):
    set_day(TRUTH[key], "2026-10-14", prcp=14.0, snow_override=12.0)
    set_day(TRUTH[key], "2026-10-15", prcp=5.0, snow_override=5.0)
# no snow in Munich before Oct 14 in autumn 2026
for x in drange("2026-09-01", "2026-10-13"):
    i = DIDX[x]
    munich.at[i, "tmin"] = max(munich.at[i, "tmin"], 1.5) if munich.at[i, "prcp"] > 0 else munich.at[i, "tmin"]

# milder echo Paris/London/Milan Oct 13-19 (+ small for Venice/Rome)
ECHO = {"PARIS": (11.2, 2.2), "LONDON": (11.0, 2.0), "MILANO": (12.0, 2.0), "VENEZIA": (13.0, 1.5), "ROMA": (17.5, 1.5)}
for key, (base, sd) in ECHO.items():
    df = TRUTH[key]
    r = rng_for("echo-" + key)
    for x in drange("2026-10-13", "2026-10-19"):
        prof = 1.0 if x.day in (14, 15, 16, 17) else 0.6
        tx = base + (1 - prof) * 4 + r.normal(0, 0.8)
        set_day(df, x.isoformat(), tmax=round(tx, 1), tmin=round(tx - r.uniform(5, 7.5), 1))

# Japan unusually warm Sep 28 - Oct 11
for key, lo, hi in (("TOKYO", 27.0, 29.0), ("OSAKA", 27.5, 29.6)):
    df = TRUTH[key]
    r = rng_for("warm-" + key)
    for x in drange("2026-09-28", "2026-10-11"):
        tx = r.uniform(lo, hi)
        pr = 0.0 if r.random() < 0.8 else round(float(r.uniform(0.5, 6)), 1)
        set_day(df, x.isoformat(), tmax=round(tx, 1), tmin=round(tx - r.uniform(6.5, 8.5), 1), prcp=pr,
                cloud=float(r.uniform(5, 50)) if pr == 0 else 80.0, rh=float(r.uniform(58, 72)))
    for x, tx in zip(drange("2026-10-12", "2026-10-21"), [23.5, 21.0, 20.4, 19.8, 21.1, 20.2, 18.9, 19.6, 18.2, 17.6]):
        set_day(df, x.isoformat(), tmax=round(tx + r.normal(0, 0.6) + (0.6 if key == "OSAKA" else 0), 1),
                tmin=round(tx - r.uniform(6, 8), 1))

# Hong Kong typhoon Sep 16-18
hk = TRUTH["HONGKONG"]
for day, pr, tx, tn, wind, gust, rh, cond in [
        ("2026-09-15", 4.1, 32.4, 27.6, 18, 41, 74, "partly_cloudy"),
        ("2026-09-16", 22.4, 30.1, 26.0, 30, 68, 86, "heavy_rain"),
        ("2026-09-17", 361.0, 26.8, 24.3, 46, 146, 96, "typhoon"),
        ("2026-09-18", 16.2, 28.6, 24.9, 32, 88, 90, "showers"),
        ("2026-09-19", 12.0, 30.6, 25.8, 20, 44, 84, "showers")]:
    set_day(hk, day, prcp=pr, tmax=tx, tmin=tn, wind=float(wind), gust_override=float(gust), rh=float(rh), cloud=100.0 if pr > 10 else 60.0,
            cond_override=cond)
hk.loc[DIDX[d("2026-09-17")], "press"] = 978.6
hk.loc[DIDX[d("2026-09-16")], "press"] = 997.2
hk.loc[DIDX[d("2026-09-18")], "press"] = 994.9

# LA heat wave Sep 8-12 (Beverly Hills)
bh = TRUTH["BEVERLYHILLS"]
for day, tx, tn in [("2026-09-07", 33.4, 19.8), ("2026-09-08", 38.2, 22.1), ("2026-09-09", 40.3, 23.6), ("2026-09-10", 41.1, 24.4),
                    ("2026-09-11", 39.4, 23.0), ("2026-09-12", 38.0, 21.7), ("2026-09-13", 33.1, 19.2)]:
    set_day(bh, day, tmax=tx, tmin=tn, prcp=0.0, rh=float(rng_for(day).uniform(14, 24)), cloud=5.0, cond_override="clear")

# Venice: scirocco + rain Oct 19-20
ven = TRUTH["VENEZIA"]
set_day(ven, "2026-10-19", prcp=9.6, wind=24.0, gust_override=49.0, wind_dir=135.0)
set_day(ven, "2026-10-20", prcp=17.8, wind=31.0, gust_override=63.0, wind_dir=140.0, cond_override="heavy_rain")

for k, c in CITIES.items():
    TRUTH[k] = finish(TRUTH[k], c)
    TRUTH[k]["tmean"] = ((TRUTH[k].tmax + TRUTH[k].tmin) / 2)

# ---------------------------------------------------------------------------------------------- code maps
WMO = {"clear": 0, "mainly_clear": 1, "partly_cloudy": 2, "overcast": 3, "fog": 45, "drizzle": 51, "light_rain": 61, "rain": 63,
       "heavy_rain": 65, "showers": 80, "thunder": 95, "light_snow": 71, "snow": 73, "heavy_snow": 75, "sleet": 68, "dust": 6,
       "haze": 5, "typhoon": 65}
JMA = {"clear": "晴", "mainly_clear": "晴", "partly_cloudy": "晴時々曇", "overcast": "曇", "fog": "霧", "drizzle": "曇一時雨",
       "light_rain": "曇時々雨", "rain": "雨", "heavy_rain": "大雨", "showers": "曇一時雨", "thunder": "雨、雷を伴う",
       "light_snow": "曇一時雪", "snow": "雪", "heavy_snow": "大雪", "sleet": "みぞれ", "dust": "晴", "haze": "薄曇", "typhoon": "暴風雨"}
KMA = {"clear": "맑음", "mainly_clear": "맑음", "partly_cloudy": "구름조금", "overcast": "흐림", "fog": "안개", "drizzle": "약한비",
       "light_rain": "비", "rain": "비", "heavy_rain": "강한비", "showers": "소나기", "thunder": "뇌전", "light_snow": "눈",
       "snow": "눈", "heavy_snow": "강한눈", "sleet": "진눈깨비", "dust": "황사", "haze": "박무", "typhoon": "강한비"}
CNW = {"clear": "晴", "mainly_clear": "晴", "partly_cloudy": "多云", "overcast": "阴", "fog": "雾", "drizzle": "小雨",
       "light_rain": "小雨", "rain": "中雨", "heavy_rain": "大雨", "showers": "阵雨", "thunder": "雷阵雨", "light_snow": "小雪",
       "snow": "中雪", "heavy_snow": "大雪", "sleet": "雨夹雪", "dust": "浮尘", "haze": "霾", "typhoon": "暴雨"}
API = {"clear": (1000, "Sunny"), "mainly_clear": (1000, "Sunny"), "partly_cloudy": (1003, "Partly cloudy"), "overcast": (1009, "Overcast"),
       "fog": (1135, "Fog"), "drizzle": (1153, "Light drizzle"), "light_rain": (1183, "Light rain"), "rain": (1189, "Moderate rain"),
       "heavy_rain": (1195, "Heavy rain"), "showers": (1240, "Light rain shower"), "thunder": (1276, "Moderate or heavy rain with thunder"),
       "light_snow": (1213, "Light snow"), "snow": (1219, "Moderate snow"), "heavy_snow": (1225, "Heavy snow"), "sleet": (1069, "Patchy sleet possible"),
       "dust": (1030, "Mist"), "haze": (1030, "Mist"), "typhoon": (1195, "Heavy rain")}


def f1(x):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), 1)


# ---------------------------------------------------------------------------------------------- A. EU JSON (Open-Meteo-like)
EU_KEYS = ["MILANO", "ROMA", "VENEZIA", "COURMAYEUR", "CORTINA", "PARIS", "CANNES", "GENEVE", "LONDON", "MUENCHEN", "BERLIN",
           "ZUERICH", "STMORITZ", "MADRID", "AMSTERDAM", "KOBENHAVN"]
SLUG = {"MILANO": "milano", "ROMA": "roma", "VENEZIA": "venezia", "COURMAYEUR": "courmayeur", "CORTINA": "cortina_d_ampezzo",
        "PARIS": "paris", "CANNES": "cannes", "GENEVE": "geneve", "LONDON": "london", "MUENCHEN": "muenchen", "BERLIN": "berlin",
        "ZUERICH": "zuerich", "STMORITZ": "st_moritz", "MADRID": "madrid", "AMSTERDAM": "amsterdam", "KOBENHAVN": "kobenhavn"}
eu_dir = mkdir(W / "eu_meteoarchive")
SPLIT = d("2026-03-01")
for k in EU_KEYS:
    c = CITIES[k]
    df = TRUTH[k].copy()
    rr = rng_for("eu-" + k)
    grid_elev = c["elev"] + int(rr.integers(-30, 60))
    bias = 0.0
    if k == "STMORITZ":   # grid cell much higher than the village
        grid_elev = 2163
        bias = -2.1
    df["tmax_o"] = df.tmax + bias + rr.normal(0, 0.35, len(df))
    df["tmin_o"] = df.tmin + bias + rr.normal(0, 0.35, len(df))
    end = LAST_DAY if k != "PARIS" else d("2026-10-20")
    for part, (a, b) in enumerate([(HIST_START, SPLIT - dt.timedelta(days=1)), (SPLIT, end)]):
        sub = df[(df.date >= a) & (df.date <= b)].reset_index(drop=True)
        times = [x.isoformat() for x in sub.date]
        tz = c["tz"]
        off = int(pd.Timestamp("2026-01-15", tz=tz).utcoffset().total_seconds()) if part == 0 else int(pd.Timestamp("2026-07-15", tz=tz).utcoffset().total_seconds())
        if k == "LONDON" and part == 1:
            tz, off = "GMT", 0
        rain = [f1(p - s * 0.9) if s > 0 else f1(p) for p, s in zip(sub.prcp, sub.snow)]
        rain = [max(0.0, x) for x in rain]
        if part == 0:
            daily = {"time": times, "weathercode": [WMO[x] for x in sub.cond],
                     "temperature_2m_max": [f1(x) for x in sub.tmax_o], "temperature_2m_min": [f1(x) for x in sub.tmin_o],
                     "precipitation_sum": [f1(x) for x in sub.prcp], "rain_sum": rain, "snowfall_sum": [f1(x * 0.7) for x in sub.snow],
                     "windspeed_10m_max": [f1(x) for x in sub.wind_max], "windgusts_10m_max": [f1(x) for x in sub.gust],
                     "winddirection_10m_dominant": [int(x) for x in sub.wind_dir],
                     "relative_humidity_2m_mean": [int(round(x)) for x in sub.rh]}
            units = {"time": "iso8601", "weathercode": "wmo code", "temperature_2m_max": "°C", "temperature_2m_min": "°C",
                     "precipitation_sum": "mm", "rain_sum": "mm", "snowfall_sum": "cm", "windspeed_10m_max": "km/h",
                     "windgusts_10m_max": "km/h", "winddirection_10m_dominant": "°", "relative_humidity_2m_mean": "%"}
        else:
            daily = {"time": times, "weather_code": [WMO[x] for x in sub.cond],
                     "temperature_2m_max": [f1(x) for x in sub.tmax_o], "temperature_2m_min": [f1(x) for x in sub.tmin_o],
                     "temperature_2m_mean": [f1((a_ + b_) / 2) for a_, b_ in zip(sub.tmax_o, sub.tmin_o)],
                     "precipitation_sum": [f1(x) for x in sub.prcp], "rain_sum": rain, "snowfall_sum": [f1(x * 0.7) for x in sub.snow],
                     "precipitation_hours": [float(min(24, round(p / 1.3))) if p > 0 else 0.0 for p in sub.prcp],
                     "wind_speed_10m_max": [f1(x / 3.6) for x in sub.wind_max], "wind_gusts_10m_max": [f1(x / 3.6) for x in sub.gust],
                     "wind_direction_10m_dominant": [int(x) for x in sub.wind_dir],
                     "relative_humidity_2m_mean": [int(round(x)) for x in sub.rh],
                     "sunshine_duration": [round(x * 3600, 2) for x in sub.sun]}
            units = {"time": "iso8601", "weather_code": "wmo code", "temperature_2m_max": "°C", "temperature_2m_min": "°C",
                     "temperature_2m_mean": "°C", "precipitation_sum": "mm", "rain_sum": "mm", "snowfall_sum": "cm",
                     "precipitation_hours": "h", "wind_speed_10m_max": "m/s", "wind_gusts_10m_max": "m/s",
                     "wind_direction_10m_dominant": "°", "relative_humidity_2m_mean": "%", "sunshine_duration": "s"}
        if k == "KOBENHAVN" and part == 1:  # outage
            for j, t in enumerate(times):
                if "2026-07-14" <= t <= "2026-07-18":
                    for v in daily:
                        if v != "time":
                            daily[v][j] = None
        if k == "MILANO" and part == 0:  # missing day entirely (gap in time axis)
            j = times.index("2025-06-03")
            for v in daily:
                daily[v].pop(j)
        obj = {"latitude": round(c["lat"] + rr.uniform(-0.03, 0.03), 6), "longitude": round(c["lon"] + rr.uniform(-0.03, 0.03), 6),
               "generationtime_ms": round(float(rr.uniform(0.3, 9.0)), 3), "utc_offset_seconds": off, "timezone": tz,
               "timezone_abbreviation": {"Europe/London": "GMT"}.get(tz, "GMT" if tz == "GMT" else ("CET" if part == 0 else "CEST")),
               "elevation": float(grid_elev), "api_version": "v1" if part == 0 else "v2",
               "daily_units": units, "daily": daily}
        fn = f"{SLUG[k]}_{a.isoformat()}_{b.isoformat()}.json"
        write_json(eu_dir / fn, obj, indent=None)
(eu_dir / "README.txt").write_text("""MeteoArchive Historical API - bulk export (daily aggregation, reanalysis + station blend)
Query: /v1/archive?latitude=..&longitude=..&daily=...&timezone=auto  (v2 endpoint from 2026-03-01)
One JSON per location and request window. Values are model grid-cell values (see 'elevation'), not station observations.
API v2 changelog (2026-03-01): variable names now snake_case with underscores between words
(weathercode -> weather_code, windspeed_10m_max -> wind_speed_10m_max, ...); wind speed default unit is now m/s;
new variables temperature_2m_mean, precipitation_hours, sunshine_duration (seconds).
weather code: WMO 4677 interpretation codes (0 clear .. 99 thunderstorm with hail).
Data for the last 1-2 days may be missing (ERA5T latency).
""", encoding="utf-8")

# ---------------------------------------------------------------------------------------------- B. US NOAA-like CSV
US = {"NEWYORK": ("USW00094728", "NY CITY CENTRAL PARK, NY US"), "MIAMI": ("USW00012839", "MIAMI INTERNATIONAL AIRPORT, FL US"),
      "BEVERLYHILLS": ("USW00093134", "LOS ANGELES DOWNTOWN USC, CA US"), "ASPEN": ("USW00093073", "ASPEN PITKIN CO AIRPORT SARDY FIELD, CO US")}
us_dir = mkdir(W / "us_ncei_ghcnd")
for k, (sid, name) in US.items():
    df = TRUTH[k]
    rr = rng_for("us-" + k)
    buf = io.StringIO()
    wr = csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator="\n")
    wr.writerow(["STATION", "NAME", "DATE", "AWND", "PRCP", "RHAV", "SNOW", "SNWD", "TAVG", "TMAX", "TMIN", "WSF2", "WT01", "WT02", "WT03", "WT08", "WT16", "WT18"])
    for r in df.itertuples():
        if k == "ASPEN" and d("2025-02-09") <= r.date <= d("2025-02-15"):
            continue
        if k == "BEVERLYHILLS" and r.date == d("2026-09-10"):
            continue  # missing day in the middle of the heat wave
        tx = round(r.tmax * 9 / 5 + 32 + (1.2 if k == "BEVERLYHILLS" else 0))
        tn = round(r.tmin * 9 / 5 + 32 + (0.8 if k == "BEVERLYHILLS" else 0))
        tavg = "" if rr.random() < 0.08 else str(round((tx + tn) / 2 + rr.normal(0, 1)))
        prcp = f"{r.prcp / 25.4:.2f}"
        snow = f"{r.snow / 2.54:.1f}" if k in ("ASPEN", "NEWYORK") else ""
        snwd = f"{r.snow_depth / 2.54:.0f}" if k in ("ASPEN", "NEWYORK") else ""
        rhav = "" if k == "ASPEN" or rr.random() < 0.05 else str(int(round(r.rh)))
        cond = r.cond
        wt = ["1" if cond == "fog" else "", "1" if cond == "fog" and rr.random() < 0.3 else "", "1" if cond == "thunder" else "",
              "1" if cond in ("haze", "dust") or (k == "BEVERLYHILLS" and rr.random() < 0.12) else "",
              "1" if cond in ("rain", "light_rain", "heavy_rain", "showers", "drizzle", "thunder", "typhoon") else "",
              "1" if "snow" in cond or cond == "sleet" else ""]
        wr.writerow([sid, name, r.date.isoformat(), f"{r.wind / 1.609:.2f}", prcp, rhav, snow, snwd, tavg, str(tx), str(tn),
                     f"{r.gust * 0.62:.1f}"] + wt)
    (us_dir / f"{sid}_daily_20240901_20261021.csv").write_text(buf.getvalue(), encoding="utf-8")
(us_dir / "README.txt").write_text("""GHCN-Daily style extract (CDO bulk order #4412093, units = STANDARD)
TMAX/TMIN/TAVG degrees Fahrenheit; PRCP/SNOW inches; SNWD inches; AWND/WSF2 mph; RHAV percent.
WT01 fog, WT02 heavy fog, WT03 thunder, WT08 smoke/haze, WT16 rain, WT18 snow (1 = observed, blank = not reported).
Station for Beverly Hills store: LOS ANGELES DOWNTOWN USC (approx. 13 km east, urban).
Days with no report are omitted (no row). TAVG not always computed.
""", encoding="utf-8")

# ---------------------------------------------------------------------------------------------- C. Toronto ECCC-like CSV
tor = TRUTH["TORONTO"]
tor_dir = mkdir(W / "ca_eccc_climate")
cols = ["Longitude (x)", "Latitude (y)", "Station Name", "Climate ID", "Date/Time", "Year", "Month", "Day", "Data Quality",
        "Max Temp (°C)", "Max Temp Flag", "Min Temp (°C)", "Min Temp Flag", "Mean Temp (°C)", "Mean Temp Flag", "Heat Deg Days (°C)",
        "Heat Deg Days Flag", "Cool Deg Days (°C)", "Cool Deg Days Flag", "Total Rain (mm)", "Total Rain Flag", "Total Snow (cm)",
        "Total Snow Flag", "Total Precip (mm)", "Total Precip Flag", "Snow on Grnd (cm)", "Snow on Grnd Flag", "Dir of Max Gust (10s deg)",
        "Dir of Max Gust Flag", "Spd of Max Gust (km/h)", "Spd of Max Gust Flag"]
rr = rng_for("eccc")
for yr in (2024, 2025, 2026):
    buf = io.StringIO()
    wr = csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator="\n")
    wr.writerow(cols)
    for r in tor[[x.year == yr for x in tor.date]].itertuples():
        mt = round((r.tmax + r.tmin) / 2, 1)
        miss = rr.random() < 0.012
        gust = "" if r.gust < 31 else f"{r.gust:.0f}"
        gustf = "<31" if r.gust < 31 else ""
        wr.writerow(["-79.40", "43.67", "TORONTO CITY", "6158355", r.date.isoformat(), yr, f"{r.date.month:02d}", f"{r.date.day:02d}", "",
                     "" if miss else f"{r.tmax:.1f}", "M" if miss else "", "" if miss else f"{r.tmin:.1f}", "M" if miss else "",
                     "" if miss else f"{mt:.1f}", "M" if miss else "", f"{max(0, 18 - mt):.1f}", "", f"{max(0, mt - 18):.1f}", "",
                     f"{max(0, r.prcp - r.snow):.1f}", "T" if 0 < r.prcp < 0.3 else "", f"{r.snow:.1f}", "",
                     f"{r.prcp:.1f}", "", "" if r.snow_depth == 0 else str(int(r.snow_depth)), "",
                     "" if not gust else str(int(r.wind_dir // 10)), "", gust, gustf])
    (tor_dir / f"en_climate_daily_ON_6158355_{yr}_P1D.csv").write_text("﻿" + buf.getvalue(), encoding="utf-8")

# ---------------------------------------------------------------------------------------------- D. JMA-like (cp932)
jma_dir = mkdir(W / "jp_jma")
for k, st in (("TOKYO", "東京"), ("OSAKA", "大阪")):
    df = TRUTH[k]
    rr = rng_for("jma-" + k)
    for a, b in ((HIST_START, d("2025-08-31")), (d("2025-09-01"), LAST_DAY)):
        lines = [f"ダウンロードした時刻：2026/10/22 09:{rr.integers(10, 59)}:{rr.integers(10, 59)}", "",
                 "," + ",".join([st] * 27),
                 "年月日,平均気温(℃),平均気温(℃),平均気温(℃),最高気温(℃),最高気温(℃),最高気温(℃),最低気温(℃),最低気温(℃),最低気温(℃),"
                 "降水量の合計(mm),降水量の合計(mm),降水量の合計(mm),降水量の合計(mm),日照時間(時間),日照時間(時間),日照時間(時間),"
                 "平均風速(m/s),平均風速(m/s),平均風速(m/s),平均湿度(％),平均湿度(％),平均湿度(％),天気概況(昼：06時～18時),天気概況(昼：06時～18時),天気概況(昼：06時～18時),降雪量合計(cm)",
                 ",,品質情報,均質番号,,品質情報,均質番号,,品質情報,均質番号,,現象なし情報,品質情報,均質番号,,品質情報,均質番号,,品質情報,均質番号,,品質情報,均質番号,,品質情報,均質番号,"]
        for r in df[(df.date >= a) & (df.date <= b)].itertuples():
            q = "8" if r.date < d("2026-10-01") else "5"  # recent values provisional
            no_pr = "1" if r.prcp == 0 else "0"
            lines.append(f"{r.date.year}/{r.date.month}/{r.date.day},{r.tmean:.1f},,{q},1,{r.tmax:.1f},,{q},1,{r.tmin:.1f},,{q},1,"
                         f"{r.prcp:.1f},{no_pr},{q},1,{r.sun:.1f},{q},1,{r.wind / 3.6:.1f},{q},1,{int(round(r.rh))},{q},1,"
                         f"{JMA[r.cond]},{q},1,{'--' if r.snow == 0 else f'{r.snow:.0f}'}")
        fn = f"data_{k.lower()}_{a.strftime('%Y%m%d')}_{b.strftime('%Y%m%d')}.csv"
        (jma_dir / fn).write_bytes(("\r\n".join(lines) + "\r\n").encode("cp932"))

# ---------------------------------------------------------------------------------------------- E. KMA ASOS-like (cp949)
kma_dir = mkdir(W / "kr_kma_asos")
lines = ["지점,지점명,일시,평균기온(°C),최저기온(°C),최고기온(°C),일강수량(mm),최대 순간 풍속(m/s),평균 풍속(m/s),평균 상대습도(%),합계 일조시간(hr),일 최심신적설(cm),일기현상"]
for k, (stn, nm) in (("SEOUL", (108, "서울")), ("BUSAN", (159, "부산"))):
    df = TRUTH[k]
    for r in df.itertuples():
        pr = "" if r.prcp == 0 else f"{r.prcp:.1f}"
        sn = "" if r.snow == 0 else f"{r.snow:.1f}"
        lines.append(f"{stn},{nm},{r.date.isoformat()},{r.tmean:.1f},{r.tmin:.1f},{r.tmax:.1f},{pr},{r.gust / 3.6:.1f},{r.wind / 3.6:.1f},"
                     f"{r.rh:.1f},{r.sun:.1f},{sn},{KMA[r.cond] if r.cond not in ('clear', 'mainly_clear', 'partly_cloudy', 'overcast') else ''}")
(kma_dir / "OBS_ASOS_DD_20261022091533.csv").write_bytes(("\r\n".join(lines) + "\r\n").encode("cp949"))

# ---------------------------------------------------------------------------------------------- F. China weather portal scrape
cn_dir = mkdir(W / "cn_tianqi_portal")
WK = "一二三四五六日"
DIRS = ["北风", "东北风", "东风", "东南风", "南风", "西南风", "西风", "西北风"]
for k, py in (("SHANGHAI", "shanghai"), ("BEIJING", "beijing"), ("CHENGDU", "chengdu")):
    df = TRUTH[k]
    rr = rng_for("cn-" + k)
    rows = ["日期,星期,最高气温,最低气温,天气,风向,风力,空气质量指数,空气质量等级"]
    am_cond = None
    for r in df.itertuples():
        if d("2024-12-09") <= r.date <= d("2024-12-14") and k == "CHENGDU":
            continue  # scraper gap
        prev = am_cond or r.cond
        txt = CNW[r.cond] if CNW[prev] == CNW[r.cond] or rr.random() < 0.4 else f"{CNW[prev]}转{CNW[r.cond]}"
        am_cond = r.cond
        level = min(6, max(1, int(r.wind / 6) + 1))
        dirn = DIRS[int(((r.wind_dir + 22.5) % 360) // 45)]
        fl = f"{level}级" if level > 2 else ("<3级" if rr.random() < 0.6 else "微风")
        base_aqi = {"BEIJING": 85, "CHENGDU": 75, "SHANGHAI": 60}[k] * (1.5 if r.date.month in (11, 12, 1, 2) else 1.0)
        aqi = int(max(15, rr.lognormal(math.log(base_aqi), 0.45) * (0.6 if r.prcp > 3 else 1)))
        lv = "优" if aqi <= 50 else "良" if aqi <= 100 else "轻度污染" if aqi <= 150 else "中度污染" if aqi <= 200 else "重度污染"
        rows.append(f"{r.date.isoformat()},星期{WK[r.date.weekday()]},{round(r.tmax)}℃,{round(r.tmin)}℃,{txt},{dirn},{fl},{aqi},{lv}")
    (cn_dir / f"lishi_tianqi_{py}_201409_202610.csv").write_text("﻿" + "\n".join(rows) + "\n", encoding="utf-8")
(cn_dir / "说明.txt").write_text("历史天气数据（网页抓取）。气温为当日最高/最低（整数，℃）。天气为白天/夜间描述，\"A转B\"表示天气变化。风力为蒲福风级。\n"
                                  "不含降水量、湿度。空气质量指数为城市日均AQI。部分日期缺失（抓取失败）。\n", encoding="utf-8")

# ---------------------------------------------------------------------------------------------- G. Hong Kong HKO-like
hk_dir = mkdir(W / "hk_hko")
hdr = ["年/Year", "月/Month", "日/Day", "平均氣壓(百帕斯卡)/Mean Pressure (hPa)", "絕對最高氣溫(攝氏)/Absolute Daily Max (deg. C)",
       "平均氣溫(攝氏)/Mean (deg. C)", "絕對最低氣溫(攝氏)/Absolute Daily Min (deg. C)", "平均露點溫度(攝氏)/Mean Dew Point (deg. C)",
       "平均相對濕度(百分比)/Mean Relative Humidity (%)", "平均雲量(百分比)/Mean Amount of Cloud (%)", "總雨量(毫米)/Total Rainfall (mm)",
       "總日照(小時)/Total Bright Sunshine (hours)", "盛行風向(度)/Prevailing Wind Direction (degrees)", "平均風速(公里/小時)/Mean Wind Speed (km/h)"]
rows = [",".join(['"' + h + '"' for h in hdr])]
for r in TRUTH["HONGKONG"].itertuples():
    tm = (r.tmax + r.tmin) / 2
    dew = tm - (100 - r.rh) / 5
    rain = "微量/Trace" if 0 < r.prcp < 0.1 else f"{r.prcp:.1f}"
    if r.prcp > 0 and r.prcp < 0.5:
        rain = "微量/Trace"
    miss = r.date == d("2025-08-22")
    rows.append(f"{r.date.year},{r.date.month},{r.date.day},{r.press:.1f},{r.tmax:.1f},{tm:.1f},{r.tmin:.1f},{dew:.1f},{int(r.rh)},"
                f"{int(r.cloud)},{'***' if miss else rain},{r.sun:.1f},{int(r.wind_dir // 10 * 10)},{r.wind:.1f}")
(hk_dir / "daily_HKO_ALL_ELEMENTS_202409_202610.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
(hk_dir / "README.txt").write_text("Daily extract, Hong Kong Observatory Headquarters (Tsim Sha Tsui). Trace = rainfall < 0.05 mm.\n"
                                    "*** = unavailable. Mean wind speed measured at King's Park. Data after 2026-08-31 are provisional.\n"
                                    "Tropical cyclone warning signal history: see ../../events/hongkong/\n", encoding="utf-8")

# ---------------------------------------------------------------------------------------------- H. Taipei CWA-like monthly CSVs
tw_dir = mkdir(W / "tw_cwa_466920")
df = TRUTH["TAIPEI"]
rr = rng_for("cwa")
for (yr, mo), g in df.groupby([df.date.map(lambda x: x.year), df.date.map(lambda x: x.month)]):
    lines = ["觀測時間(day),測站氣壓(hPa),氣溫(℃),最高氣溫(℃),最低氣溫(℃),相對溼度(%),風速(m/s),最大陣風(m/s),降水量(mm),日照時數(hr)",
             "ObsTime,StnPres,Temperature,T Max,T Min,RH,WS,WSGust,Precp,SunShine"]
    for r in g.itertuples():
        pr = "T" if 0 < r.prcp < 0.5 else f"{r.prcp:.1f}"
        bad = rr.random() < 0.01
        lines.append(f"{r.date.day:02d},{r.press - 6:.1f},{r.tmean:.1f},{'X' if bad else f'{r.tmax:.1f}'},{r.tmin:.1f},{int(r.rh)},"
                     f"{r.wind / 3.6:.1f},{r.gust / 3.6:.1f},{pr},{'/' if rr.random() < 0.03 else f'{r.sun:.1f}'}")
    (tw_dir / f"466920-{yr}-{mo:02d}.csv").write_text("﻿" + "\n".join(lines) + "\n", encoding="utf-8")

# ---------------------------------------------------------------------------------------------- I. Singapore MSS-like
sg = TRUTH["SINGAPORE"]
rr = rng_for("mss")
lines = ["Station,Year,Month,Day,Daily Rainfall Total (mm),Highest 30 Min Rainfall (mm),Highest 60 Min Rainfall (mm),Highest 120 Min Rainfall (mm),"
         "Mean Temperature (°C),Maximum Temperature (°C),Minimum Temperature (°C),Mean Wind Speed (km/h),Max Wind Speed (km/h)"]
for r in sg.itertuples():
    p = r.prcp
    h30, h60, h120 = (p * 0.55, p * 0.75, p * 0.9) if p > 0 else (0, 0, 0)
    t = "—" if rr.random() < 0.015 else f"{r.tmean:.1f}"
    lines.append(f"Changi,{r.date.year},{r.date.month},{r.date.day},{p:.1f},{h30:.1f},{h60:.1f},{h120:.1f},{t},{r.tmax:.1f},{r.tmin:.1f},{r.wind:.1f},{r.gust * 0.8:.1f}")
mkdir(W / "sg_mss")
(W / "sg_mss" / "DAILYDATA_S24_202409_202610.csv").write_text("\n".join(lines) + "\n", encoding="cp1252", errors="replace")

# ---------------------------------------------------------------------------------------------- J. Sydney BoM-like (3 files)
syd = TRUTH["SYDNEY"]
bom = mkdir(W / "au_bom_066214")
for code, name, col, unit in (("IDCJAC0010", "max", "tmax", "Maximum temperature (Degree C)"),
                              ("IDCJAC0011", "min", "tmin", "Minimum temperature (Degree C)"),
                              ("IDCJAC0009", "rain", "prcp", "Rainfall amount (millimetres)")):
    hdr2 = "Days of accumulation of maximum temperature" if name == "max" else "Days of accumulation of minimum temperature" if name == "min" else "Period over which rainfall was measured (days)"
    lines = [f"Product code,Bureau of Meteorology station number,Year,Month,Day,{unit},{hdr2},Quality"]
    for r in syd.itertuples():
        q = "Y" if r.date < d("2026-08-15") else "N"
        v = getattr(r, col)
        if name == "rain" and r.date.weekday() == 0 and r.date > d("2026-09-30") and r.prcp > 0:
            lines.append(f"{code},066214,{r.date.year},{r.date.month:02d},{r.date.day:02d},{v:.1f},1,{q}")
            continue
        lines.append(f"{code},066214,{r.date.year},{r.date.month:02d},{r.date.day:02d},{v:.1f},1,{q}")
    (bom / f"{code}_066214_2024_2026_Data.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
(bom / "README.txt").write_text("Bureau-style climate data online extract, Sydney (Observatory Hill) 066214.\n"
                                 "Rainfall: 24h to 9am local time, attributed to the day of measurement (i.e. mostly rain of the previous day).\n"
                                 "Quality N = not yet quality controlled.\n", encoding="utf-8")

# ---------------------------------------------------------------------------------------------- K. Global commercial API (Dubai full + overlaps)
api_dir = mkdir(W / "global_weatherhub_api")
for k, a in (("DUBAI", HIST_START), ("TORONTO", d("2026-08-01")), ("SYDNEY", d("2026-08-01")), ("SINGAPORE", d("2026-08-01")),
             ("TAIPEI", d("2026-08-01")), ("SHANGHAI", d("2026-08-01")), ("BEIJING", d("2026-08-01")), ("CHENGDU", d("2026-08-01"))):
    c = CITIES[k]
    df = TRUTH[k]
    rr = rng_for("api-" + k)
    out = []
    for r in df[df.date >= a].itertuples():
        # model-ish values: slightly smoothed / biased vs station
        tx = r.tmax + rr.normal(-0.4, 0.9)
        tn = r.tmin + rr.normal(0.3, 0.9)
        local_mid = pd.Timestamp(r.date.isoformat(), tz=c["tz"])
        code, text = API[r.cond]
        out.append({"date": r.date.isoformat(), "date_epoch": int(local_mid.tz_convert("UTC").timestamp()),
                    "day": {"maxtemp_c": round(tx, 1), "maxtemp_f": round(tx * 1.8 + 32, 1), "mintemp_c": round(tn, 1),
                            "mintemp_f": round(tn * 1.8 + 32, 1), "avgtemp_c": round((tx + tn) / 2, 1),
                            "maxwind_kph": round(r.wind_max, 1), "maxwind_mph": round(r.wind_max / 1.609, 1),
                            "totalprecip_mm": round(r.prcp * float(rr.uniform(0.6, 1.3)), 1), "totalsnow_cm": round(r.snow, 1),
                            "avghumidity": int(r.rh), "daily_chance_of_rain": 100 if r.prcp > 1 else int(rr.uniform(0, 40)),
                            "condition": {"text": text, "code": code}, "uv": round(float(rr.uniform(3, 11)), 1)}})
    obj = {"location": {"name": c["name"], "country": c["cc"], "lat": c["lat"], "lon": c["lon"], "tz_id": c["tz"]},
           "history": {"forecastday": out}}
    write_json(api_dir / f"history_{k.lower()}_{a.isoformat()}_2026-10-21.json", obj, indent=None)
(api_dir / "README.txt").write_text("WeatherHub REST API /v1/history.json responses (paginated pages merged by ops script).\n"
                                     "Daily values from a global NWP model blended with nearby METAR. date_epoch = unix time.\n", encoding="utf-8")

# ---------------------------------------------------------------------------------------------- Venice tide gauge
ven_dir = mkdir(W / "venezia_maree")
hours = pd.date_range("2024-09-01 00:00", "2026-10-21 23:00", freq="h")
tt = (hours - pd.Timestamp("2024-09-01")).total_seconds().values / 3600.0
rr = rng_for("tide")
astro = (23 * np.cos(2 * np.pi * tt / 12.4206 + 0.3) + 13 * np.cos(2 * np.pi * tt / 12.0 + 1.1) +
         16 * np.cos(2 * np.pi * tt / 23.9345 + 2.0) + 5 * np.cos(2 * np.pi * tt / 25.8193 + 0.7))
seasonal = 8 * np.cos(2 * np.pi * (hours.day_of_year.values - 320) / 365.25)
surge = np.zeros(len(hours))
e = rr.normal(0, 1.6, len(hours))
for i in range(1, len(hours)):
    surge[i] = 0.985 * surge[i - 1] + e[i]
level = 30 + astro + seasonal + surge
# notable surge events (sea level); MOSE raised when forecast >= 110 -> lagoon (Punta Salute) stays ~ 60-80
EVENTS_T = [("2024-11-22 09:00", 112, True), ("2025-01-07 22:00", 104, False), ("2025-11-14 10:00", 128, True), ("2025-12-03 08:00", 121, True),
            ("2026-02-11 23:00", 99, False), ("2026-10-07 08:50", 92, False), ("2026-10-20 09:40", 118, False)]
sea = level.copy()
for ts, peak, mose in EVENTS_T:
    t0 = pd.Timestamp(ts)
    dh = (hours - t0).total_seconds().values / 3600
    bump = np.exp(-(dh / 9.0) ** 2)
    base_at = np.interp(0, dh, level)
    sea = sea + bump * max(0, peak - base_at)
lagoon = sea.copy()
for ts, peak, mose in EVENTS_T:
    if mose:
        t0 = pd.Timestamp(ts)
        m = (hours >= t0 - pd.Timedelta(hours=8)) & (hours <= t0 + pd.Timedelta(hours=8))
        lagoon[m] = np.minimum(lagoon[m], 64 + rr.normal(0, 3, m.sum()))
oct20 = (hours >= pd.Timestamp("2026-10-19 18:00")) & (hours <= pd.Timestamp("2026-10-20 18:00"))
mose_auto = (sea > 108) & ~oct20
lagoon[mose_auto] = 62 + rr.normal(0, 3, mose_auto.sum())
lagoon = lagoon + rr.normal(0, 1.2, len(hours))
tide = pd.DataFrame({"Data": hours.strftime("%d/%m/%Y"), "Ora solare": hours.strftime("%H:%M"),
                     "Punta della Salute (cm)": np.round(lagoon).astype(int), "Piattaforma CNR (cm)": np.round(sea + rr.normal(0, 1.5, len(hours))).astype(int)})
tide.loc[rr.random(len(tide)) < 0.002, "Piattaforma CNR (cm)"] = -999
tide.to_csv(ven_dir / "livelli_orari_PuntaSalute_CNR_2024-2026.csv", sep=";", index=False)
# 10-minute data for the last week
mins = pd.date_range("2026-10-15 00:00", "2026-10-21 23:50", freq="10min")
lag10 = np.interp(mins.astype("int64"), hours.astype("int64"), lagoon) + rr.normal(0, 0.8, len(mins))
pk = pd.Timestamp("2026-10-20 09:40")
lag10 = np.where(np.abs((mins - pk).total_seconds()) < 3 * 3600, lag10, lag10)
i_pk = int(np.where(mins == pk)[0][0])
lag10 = lag10 + (118 - lag10[i_pk]) * np.exp(-(((mins - pk).total_seconds().values / 3600) / 2.2) ** 2)
# align Oct 19-21 with the tide centre's published hourly readings (07:00 Oct 20 filled after validation)
PUB = [36, 25, 20, 23, 33, 47, 63, 76, 84, 84, 77, 64, 48, 34, 24, 21, 26, 37, 51, 64, 74, 77, 73, 63,
       49, 36, 27, 24, 31, 45, 65, 88, 105, 116, 117, 109, 92, 72, 53, 38, 31, 36, 45, 58, 70, 78, 80, 75,
       64, 50, 37, 28, 25, 30, 41, 56, 71, 83, 88, 85, 72, 57, 41, 28, 21, 20, 28, 40, 55, 68, 76, 77]
i19 = int(np.where(hours == pd.Timestamp("2026-10-19 00:00"))[0][0])
lagoon[i19:i19 + 72] = PUB
sea[i19:i19 + 72] = np.array(PUB) - 4 + rr.normal(0, 1.5, 72)
sea[i19 + 32:i19 + 35] = [104, 108, 103]
i07 = int(np.where(hours == pd.Timestamp("2026-10-07 06:00"))[0][0])
lagoon[i07:i07 + 7] = [58, 72, 86, 91, 85, 72, 56]
sea[i07:i07 + 7] = [55, 69, 84, 88, 83, 70, 55]
tide["Punta della Salute (cm)"] = np.round(lagoon).astype(int)
tide["Piattaforma CNR (cm)"] = np.round(sea + rr.normal(0, 1.0, len(hours))).astype(int)
tide.loc[rr.random(len(tide)) < 0.002, "Piattaforma CNR (cm)"] = -999
m10 = mins >= pd.Timestamp("2026-10-19 00:00")
lag10[m10] = np.interp(mins[m10].astype("int64"), hours[i19:i19 + 72].astype("int64"), np.array(PUB, dtype=float)) + rr.normal(0, 0.7, m10.sum())
for ts_, v_ in (("2026-10-20 09:20", 116.6), ("2026-10-20 09:30", 117.4), ("2026-10-20 09:40", 118.0), ("2026-10-20 09:50", 117.3), ("2026-10-20 10:00", 117.0)):
    lag10[mins == pd.Timestamp(ts_)] = v_
sel = tide.index[(hours >= mins[0]) & (hours < pd.Timestamp("2026-10-19 00:00"))]
tide.loc[sel, "Punta della Salute (cm)"] = np.round(lag10[::6][:len(sel)]).astype(int)
tide.to_csv(ven_dir / "livelli_orari_PuntaSalute_CNR_2024-2026.csv", sep=";", index=False)
pd.DataFrame({"data_ora_solare": mins.strftime("%Y-%m-%d %H:%M"), "livello_cm": np.round(lag10).astype(int)}).to_csv(
    ven_dir / "punta_salute_10min_2026-10-15_2026-10-21.csv", index=False)
(ven_dir / "LEGGIMI.txt").write_text("Livelli di marea osservati. Quote in cm riferite allo Zero Mareografico di Punta della Salute (ZMPS, 1897).\n"
                                     "Orari espressi in ora solare (UTC+1) per tutto l'anno, anche durante l'ora legale.\n"
                                     "Punta della Salute = interno laguna (risente delle chiusure MOSE). Piattaforma CNR = mare aperto, 15 km al largo.\n"
                                     "-999 = dato mancante. Soglie: 80 cm prime aree allagate; 110 cm marea sostenuta (12% della città); 140 cm eccezionale.\n", encoding="utf-8")

# ---------------------------------------------------------------------------------------------- 10-day forecast issued 2026-10-22
FC_DAYS = drange("2026-10-22", "2026-10-31")
# scenario for the forecast (anomaly vs climatology in degrees, per day index 0..9) - documented in notes
FC_ANOM = {
    "CEU": [0, 1, 1, 0, -1, -3, -5, -6, -6, -5], "ALPS": [0, 1, 1, 0, -1, -3, -5, -6, -6, -5], "NEU": [0, 0, 1, -1, -2, -3, -4, -5, -4, -4],
    "WEU": [1, 1, 0, 0, -1, -2, -3, -3, -3, -2], "SEU": [1, 1, 1, 0, 0, -1, -2, -2, -2, -1], "IBE": [1, 1, 1, 1, 0, 0, -1, -1, 0, 0],
    "JPN": [0, -1, -2, -3, -4, -4, -3, -3, -2, -2], "KOR": [-1, -3, -5, -4, -2, -1, -1, -2, -2, -1], "CHN": [0, 0, -1, -2, -5, -6, -4, -3, -2, -2],
    "CHE": [0, 0, 0, -1, -2, -3, -3, -2, -1, -1], "CHW": [0, 0, 0, 0, -1, -1, -1, 0, 0, 0], "USE": [2, 1, 0, -1, -2, -2, -1, 0, -3, -4],
    "USS": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "USW": [2, 2, 1, 0, 0, 0, 0, 0, 0, 0], "USM": [1, 0, -2, -4, -3, -1, 0, 0, -2, -3],
    "ME": [1, 1, 1, 1, 1, 0, 0, 0, 0, 0], "SCN": [0, 0, 0, 0, -1, -1, -1, 0, 0, 0], "SEA": [0] * 10, "AUS": [1, 2, 3, 1, 0, 0, 1, 2, 1, 0]}
fc_out = []
for k, c in CITIES.items():
    rr = rng_for("fc-" + k)
    last = TRUTH[k].iloc[-1]
    days = []
    for j, x in enumerate(FC_DAYS):
        tx = monthly_interp(c["tmax"], x) + FC_ANOM[c["region"]][j] + rr.normal(0, 0.6 + 0.15 * j)
        if j == 0:
            tx = 0.5 * tx + 0.5 * (last.tmax + 1.5)
        tn = monthly_interp(c["tmin"], x) + 0.8 * FC_ANOM[c["region"]][j] + rr.normal(0, 0.6)
        P = monthly_interp(c["pr"], x)
        pop = int(min(95, max(0, 100 * (0.05 + 0.003 * P) + rr.normal(0, 18))))
        if c["region"] in ("CEU", "ALPS") and j in (5, 6):
            pop = max(pop, 70)
        if k == "SEOUL" and j in (1, 2):
            pop = 20
        qpf = round(float(rr.gamma(0.9, P / 30 / 0.9) * (pop / 60)), 1) if pop > 25 else 0.0
        tmean = (tx + tn) / 2
        snow = round(qpf * (1.0 if tmean < 1 else 0.4 if tmean < 2.5 else 0), 1)
        if k == "STMORITZ" and j in (5, 6, 7):
            snow = max(snow, round(float(rr.uniform(6, 15)), 1))
        days.append({"date": x.isoformat(), "tmax_c": round(tx, 1), "tmin_c": round(min(tn, tx - 1.5), 1), "pop_pct": pop,
                     "precip_mm": qpf, "snow_cm": snow, "wind_kph": round(monthly_interp(c["wind"], x) * float(rr.lognormal(0, 0.25)), 0),
                     "condition": "snow" if snow > 0.5 else "rain" if qpf > 2 else "showers" if qpf > 0 else ("cloudy" if pop > 20 else "sunny"),
                     "confidence": "high" if j < 3 else "medium" if j < 6 else "low"})
    fc_out.append({"location_id": k.lower(), "name": c["name"], "country": c["cc"], "tz": c["tz"], "days": days})
write_json(mkdir(W / "forecast") / "forecast_10d_issued_2026-10-22T00Z.json",
           {"provider": "WeatherHub", "model_run": "2026-10-22T00:00:00Z", "issued": "2026-10-22T03:41:12Z",
            "units": {"temp": "C", "precip": "mm", "snow": "cm", "wind": "km/h"}, "note": "dates are local calendar dates",
            "locations": fc_out})

# coverage manifest
cov = [{"city": c["name"], "stores": " ".join(c["stores"]), "primary_provider_folder":
        ("eu_meteoarchive" if k in EU_KEYS else "us_ncei_ghcnd" if k in US else "ca_eccc_climate" if k == "TORONTO" else "jp_jma" if c["cc"] == "JP"
         else "kr_kma_asos" if c["cc"] == "KR" else "cn_tianqi_portal" if c["cc"] == "CN" else "hk_hko" if k == "HONGKONG" else
         "tw_cwa_466920" if k == "TAIPEI" else "sg_mss" if k == "SINGAPORE" else "au_bom_066214" if k == "SYDNEY" else "global_weatherhub_api")}
       for k, c in CITIES.items()]
pd.DataFrame(cov).to_csv(W / "coverage_by_city.csv", index=False)

# private truth (for testers) - canonical metric daily table
truth_all = pd.concat([TRUTH[k].assign(city=c["name"])[["city", "date", "tmax", "tmin", "prcp", "snow", "rh", "wind", "gust", "cond"]]
                       for k, c in CITIES.items()])
truth_all.round(1).to_csv(OUT.parents[1] / "ground_truth" / "canonical" / "external_weather_truth.csv", index=False)
print("weather done", len(truth_all))
