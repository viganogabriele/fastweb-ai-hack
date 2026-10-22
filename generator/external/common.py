"""Shared helpers for the external-data generators (weather, calendars, events, tourism, trends, fx, macro)."""
import datetime as dt
import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "generated" / "sources" / "external"
GT = ROOT / "generated" / "ground_truth"
STORES = pd.read_csv(ROOT / "generated" / "sources" / "erp" / "master_data" / "stores.csv")

HIST_START = dt.date(2024, 9, 1)
LAST_DAY = dt.date(2026, 10, 21)   # last closed day
TODAY = dt.date(2026, 10, 22)


def d(s):
    return dt.date.fromisoformat(s)


def drange(a, b):
    a = d(a) if isinstance(a, str) else a
    b = d(b) if isinstance(b, str) else b
    return [a + dt.timedelta(days=i) for i in range((b - a).days + 1)]


def mkdir(p):
    Path(p).mkdir(parents=True, exist_ok=True)
    return Path(p)


def rng_for(name, base=20261022):
    h = sum((i + 1) * ord(c) for i, c in enumerate(name))
    return np.random.default_rng(base + h)


def write_json(path, obj, indent=1, ensure_ascii=False):
    mkdir(Path(path).parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=indent, ensure_ascii=ensure_ascii)


# ---------------------------------------------------------------------------
# Cities (one entry per distinct store city). key -> attributes
# climate normals per month: tmax, tmin (C), precip (mm), rh (%), wind (km/h mean)
# ---------------------------------------------------------------------------
CITIES = {
    "MILANO":     dict(name="Milano", cc="IT", tz="Europe/Rome", lat=45.4642, lon=9.19, elev=122, region="SEU", stores=["MIL01", "MIL02"],
                       tmax=[6, 9, 14, 18, 23, 27, 30, 29, 24, 18, 11, 7], tmin=[-1, 0, 4, 8, 12, 16, 19, 18, 15, 10, 5, 0],
                       pr=[60, 55, 75, 80, 95, 65, 65, 80, 90, 115, 105, 65], rh=[82, 76, 70, 72, 70, 68, 65, 67, 72, 80, 84, 84], wind=[6, 7, 8, 8, 8, 8, 7, 7, 7, 6, 6, 6]),
    "ROMA":       dict(name="Roma", cc="IT", tz="Europe/Rome", lat=41.9028, lon=12.4964, elev=37, region="SEU", stores=["ROM01"],
                       tmax=[12, 13, 16, 19, 23, 28, 31, 31, 27, 22, 17, 13], tmin=[3, 4, 6, 8, 12, 16, 18, 18, 15, 12, 8, 4],
                       pr=[70, 70, 60, 65, 45, 30, 20, 30, 70, 110, 110, 80], rh=[77, 75, 72, 72, 70, 66, 63, 65, 70, 75, 78, 78], wind=[9, 10, 11, 11, 10, 10, 10, 10, 9, 8, 9, 9]),
    "VENEZIA":    dict(name="Venezia", cc="IT", tz="Europe/Rome", lat=45.4408, lon=12.3155, elev=2, region="SEU", stores=["VEN01"],
                       tmax=[6, 8, 12, 17, 22, 26, 28, 28, 24, 18, 12, 7], tmin=[0, 1, 5, 9, 13, 17, 19, 19, 15, 11, 6, 1],
                       pr=[55, 55, 60, 75, 70, 75, 60, 70, 75, 75, 80, 60], rh=[82, 78, 74, 74, 72, 70, 68, 70, 74, 79, 82, 83], wind=[10, 11, 12, 12, 11, 10, 10, 10, 10, 10, 11, 10]),
    "COURMAYEUR": dict(name="Courmayeur", cc="IT", tz="Europe/Rome", lat=45.7969, lon=6.969, elev=1224, region="ALPS", stores=["COU01"],
                       tmax=[1, 3, 7, 11, 16, 20, 23, 22, 18, 12, 6, 2], tmin=[-8, -7, -4, 0, 4, 8, 10, 10, 6, 2, -3, -7],
                       pr=[70, 60, 65, 75, 95, 85, 75, 85, 80, 100, 100, 75], rh=[72, 70, 68, 68, 70, 70, 68, 70, 72, 74, 75, 74], wind=[7, 8, 9, 9, 8, 8, 8, 8, 7, 7, 7, 7]),
    "CORTINA":    dict(name="Cortina d'Ampezzo", cc="IT", tz="Europe/Rome", lat=46.5405, lon=12.1357, elev=1224, region="ALPS", stores=["CRT01"],
                       tmax=[1, 3, 7, 11, 16, 20, 23, 22, 18, 13, 6, 2], tmin=[-9, -8, -4, 0, 4, 8, 10, 10, 6, 2, -3, -8],
                       pr=[45, 45, 60, 85, 120, 135, 130, 125, 95, 95, 95, 55], rh=[74, 71, 69, 70, 72, 73, 72, 74, 75, 76, 77, 76], wind=[6, 7, 8, 8, 8, 7, 7, 7, 6, 6, 6, 6]),
    "PARIS":      dict(name="Paris", cc="FR", tz="Europe/Paris", lat=48.8566, lon=2.3522, elev=35, region="WEU", stores=["PAR01", "PAR02"],
                       tmax=[7, 9, 13, 16, 20, 23, 26, 25, 21, 16, 11, 8], tmin=[3, 3, 5, 7, 11, 14, 16, 16, 13, 10, 6, 4],
                       pr=[50, 45, 45, 45, 60, 50, 60, 55, 45, 60, 50, 55], rh=[85, 80, 74, 70, 71, 70, 68, 70, 75, 81, 85, 86], wind=[14, 14, 14, 13, 12, 11, 11, 11, 11, 12, 13, 14]),
    "CANNES":     dict(name="Cannes", cc="FR", tz="Europe/Paris", lat=43.5528, lon=7.0174, elev=4, region="SEU", stores=["CAN01"],
                       tmax=[13, 13, 15, 17, 21, 25, 28, 28, 25, 21, 16, 13], tmin=[5, 5, 7, 10, 14, 17, 20, 20, 17, 13, 9, 6],
                       pr=[70, 55, 45, 60, 45, 30, 10, 20, 70, 110, 110, 85], rh=[70, 69, 70, 72, 74, 73, 70, 71, 72, 73, 71, 70], wind=[12, 13, 14, 13, 12, 11, 11, 11, 11, 12, 12, 12]),
    "GENEVE":     dict(name="Genève", cc="CH", tz="Europe/Zurich", lat=46.2044, lon=6.1432, elev=375, region="ALPS", stores=["GVA01"],
                       tmax=[5, 7, 12, 16, 20, 24, 27, 26, 21, 15, 9, 5], tmin=[-1, -1, 2, 5, 9, 13, 15, 15, 11, 8, 3, 0],
                       pr=[75, 65, 65, 70, 85, 85, 75, 80, 95, 100, 90, 90], rh=[84, 79, 72, 69, 70, 68, 65, 68, 75, 82, 85, 86], wind=[11, 12, 12, 11, 10, 9, 9, 9, 9, 10, 11, 11]),
    "LONDON":     dict(name="London", cc="GB", tz="Europe/London", lat=51.5074, lon=-0.1278, elev=11, region="WEU", stores=["LON01", "LON02"],
                       tmax=[8, 9, 12, 15, 18, 21, 24, 23, 20, 16, 11, 9], tmin=[3, 3, 4, 6, 9, 12, 14, 14, 12, 9, 6, 3],
                       pr=[55, 40, 40, 45, 50, 45, 45, 50, 50, 70, 65, 55], rh=[85, 81, 76, 71, 70, 69, 68, 71, 75, 80, 84, 86], wind=[17, 17, 16, 15, 14, 13, 13, 13, 14, 15, 16, 17]),
    "MUENCHEN":   dict(name="München", cc="DE", tz="Europe/Berlin", lat=48.1351, lon=11.582, elev=519, region="CEU", stores=["MUN01"],
                       tmax=[3, 5, 10, 14, 19, 22, 24, 24, 19, 14, 8, 4], tmin=[-4, -3, 0, 3, 8, 11, 13, 13, 9, 5, 1, -3],
                       pr=[50, 45, 60, 65, 105, 125, 130, 115, 85, 65, 60, 60], rh=[84, 80, 74, 70, 70, 71, 70, 72, 77, 82, 86, 86], wind=[11, 12, 12, 11, 10, 9, 9, 9, 9, 9, 10, 11]),
    "BERLIN":     dict(name="Berlin", cc="DE", tz="Europe/Berlin", lat=52.52, lon=13.405, elev=34, region="CEU", stores=["BER01"],
                       tmax=[3, 5, 9, 14, 19, 22, 24, 24, 19, 13, 7, 4], tmin=[-2, -2, 1, 4, 8, 12, 14, 14, 10, 6, 2, -1],
                       pr=[45, 35, 40, 35, 55, 60, 55, 60, 45, 35, 45, 45], rh=[86, 82, 76, 68, 67, 67, 67, 69, 75, 82, 87, 88], wind=[14, 14, 14, 13, 12, 11, 11, 11, 12, 12, 13, 14]),
    "ZUERICH":    dict(name="Zürich", cc="CH", tz="Europe/Zurich", lat=47.3769, lon=8.5417, elev=408, region="ALPS", stores=["ZRH01"],
                       tmax=[3, 5, 10, 14, 19, 22, 24, 24, 19, 14, 8, 4], tmin=[-2, -2, 1, 4, 8, 12, 14, 14, 10, 7, 2, -1],
                       pr=[65, 60, 70, 85, 110, 125, 120, 125, 90, 80, 75, 80], rh=[85, 80, 74, 71, 72, 72, 71, 74, 79, 84, 86, 86], wind=[9, 10, 10, 9, 9, 8, 8, 8, 8, 8, 9, 9]),
    "STMORITZ":   dict(name="St. Moritz", cc="CH", tz="Europe/Zurich", lat=46.4908, lon=9.8355, elev=1822, region="ALPS", stores=["STM01"],
                       tmax=[-2, -1, 3, 6, 11, 16, 19, 18, 14, 9, 2, -2], tmin=[-15, -14, -9, -4, 0, 4, 6, 6, 2, -2, -8, -13],
                       pr=[40, 35, 50, 60, 85, 100, 110, 110, 85, 80, 75, 50], rh=[76, 72, 70, 70, 70, 71, 72, 74, 75, 76, 78, 78], wind=[8, 9, 10, 10, 10, 10, 10, 9, 9, 8, 8, 8]),
    "MADRID":     dict(name="Madrid", cc="ES", tz="Europe/Madrid", lat=40.4168, lon=-3.7038, elev=667, region="IBE", stores=["MAD01"],
                       tmax=[10, 12, 16, 18, 22, 28, 32, 31, 26, 19, 13, 10], tmin=[3, 3, 5, 7, 11, 16, 19, 19, 15, 11, 6, 3],
                       pr=[35, 35, 25, 45, 50, 20, 10, 10, 25, 60, 55, 45], rh=[74, 68, 58, 56, 52, 44, 37, 39, 49, 62, 71, 76], wind=[9, 10, 11, 11, 10, 10, 10, 9, 9, 9, 9, 9]),
    "AMSTERDAM":  dict(name="Amsterdam", cc="NL", tz="Europe/Amsterdam", lat=52.3676, lon=4.9041, elev=-2, region="WEU", stores=["AMS01"],
                       tmax=[6, 7, 10, 14, 18, 20, 22, 22, 19, 15, 10, 7], tmin=[1, 1, 2, 5, 8, 11, 13, 13, 11, 8, 4, 2],
                       pr=[70, 55, 60, 45, 55, 65, 80, 85, 85, 90, 85, 80], rh=[88, 85, 81, 75, 74, 76, 77, 78, 82, 85, 88, 89], wind=[20, 19, 19, 17, 16, 15, 15, 15, 16, 18, 19, 20]),
    "KOBENHAVN":  dict(name="København", cc="DK", tz="Europe/Copenhagen", lat=55.6761, lon=12.5683, elev=5, region="NEU", stores=["CPH01"],
                       tmax=[3, 3, 6, 11, 16, 19, 22, 21, 17, 12, 7, 4], tmin=[-1, -1, 0, 3, 8, 11, 14, 14, 11, 7, 3, 0],
                       pr=[45, 30, 40, 35, 45, 55, 65, 65, 60, 55, 55, 50], rh=[88, 86, 83, 76, 72, 73, 74, 77, 80, 84, 87, 89], wind=[20, 19, 18, 17, 16, 15, 15, 15, 16, 18, 19, 20]),
    "DUBAI":      dict(name="Dubai", cc="AE", tz="Asia/Dubai", lat=25.2048, lon=55.2708, elev=5, region="ME", stores=["DXB01"],
                       tmax=[24, 25, 28, 33, 38, 40, 41, 41, 39, 35, 30, 26], tmin=[14, 15, 18, 21, 25, 27, 30, 30, 27, 23, 19, 16],
                       pr=[15, 25, 20, 7, 0.5, 0, 0, 0, 0, 1, 3, 15], rh=[65, 65, 63, 55, 53, 58, 57, 58, 62, 62, 63, 65], wind=[13, 14, 15, 15, 15, 15, 15, 15, 14, 12, 12, 12]),
    "NEWYORK":    dict(name="New York", cc="US", tz="America/New_York", lat=40.7128, lon=-74.006, elev=40, region="USE", stores=["NYC01", "NYC02"],
                       tmax=[4, 5, 10, 17, 22, 27, 29, 29, 25, 18, 12, 6], tmin=[-3, -2, 2, 7, 12, 18, 21, 20, 16, 10, 5, 0],
                       pr=[90, 80, 105, 100, 95, 105, 115, 105, 100, 95, 90, 100], rh=[63, 61, 59, 58, 64, 66, 66, 68, 69, 67, 65, 65], wind=[16, 16, 16, 15, 13, 12, 12, 12, 12, 13, 14, 15]),
    "MIAMI":      dict(name="Miami", cc="US", tz="America/New_York", lat=25.7617, lon=-80.1918, elev=2, region="USS", stores=["MIA01"],
                       tmax=[24, 25, 26, 28, 30, 31, 32, 32, 31, 29, 27, 25], tmin=[16, 17, 18, 21, 23, 25, 26, 26, 25, 23, 20, 17],
                       pr=[50, 55, 65, 80, 155, 240, 165, 220, 240, 170, 80, 60], rh=[72, 70, 69, 67, 72, 76, 75, 76, 78, 75, 74, 72], wind=[14, 15, 15, 15, 14, 12, 12, 12, 12, 14, 15, 14]),
    "BEVERLYHILLS": dict(name="Beverly Hills", cc="US", tz="America/Los_Angeles", lat=34.0736, lon=-118.4004, elev=78, region="USW", stores=["BHS01"],
                       tmax=[20, 20, 21, 22, 23, 25, 28, 29, 28, 26, 23, 20], tmin=[9, 10, 11, 12, 14, 16, 18, 18, 17, 15, 11, 9],
                       pr=[80, 90, 60, 20, 8, 2, 1, 1, 5, 15, 25, 60], rh=[62, 66, 69, 70, 73, 74, 73, 72, 70, 67, 62, 61], wind=[9, 10, 11, 11, 11, 10, 10, 10, 9, 9, 9, 9]),
    "ASPEN":      dict(name="Aspen", cc="US", tz="America/Denver", lat=39.1911, lon=-106.8175, elev=2405, region="USM", stores=["ASP01"],
                       tmax=[0, 2, 6, 11, 17, 23, 27, 25, 21, 14, 6, 0], tmin=[-16, -14, -9, -4, 0, 4, 7, 6, 2, -3, -10, -15],
                       pr=[40, 40, 45, 45, 40, 30, 40, 45, 40, 40, 45, 45], rh=[68, 65, 60, 52, 45, 38, 42, 46, 46, 50, 62, 68], wind=[9, 10, 11, 12, 12, 11, 10, 10, 10, 10, 9, 9]),
    "TORONTO":    dict(name="Toronto", cc="CA", tz="America/Toronto", lat=43.6532, lon=-79.3832, elev=76, region="USE", stores=["TOR01"],
                       tmax=[-1, 0, 5, 12, 19, 24, 27, 26, 21, 14, 7, 1], tmin=[-7, -7, -3, 3, 9, 14, 17, 17, 13, 6, 1, -4],
                       pr=[60, 55, 55, 70, 75, 70, 75, 75, 80, 65, 75, 60], rh=[76, 73, 70, 66, 67, 69, 70, 73, 75, 74, 76, 78], wind=[18, 17, 17, 16, 14, 13, 12, 12, 13, 15, 17, 18]),
    "TOKYO":      dict(name="Tokyo", cc="JP", tz="Asia/Tokyo", lat=35.6895, lon=139.6917, elev=25, region="JPN", stores=["TYO01", "TYO02"],
                       tmax=[10, 11, 14, 19, 23, 26, 30, 31, 27, 22, 17, 12], tmin=[1, 2, 5, 10, 15, 19, 23, 24, 21, 15, 9, 4],
                       pr=[55, 55, 115, 130, 140, 165, 155, 155, 225, 235, 95, 55], rh=[51, 53, 59, 64, 69, 76, 77, 74, 75, 71, 64, 56], wind=[11, 12, 12, 12, 11, 10, 11, 11, 11, 10, 10, 10]),
    "OSAKA":      dict(name="Osaka", cc="JP", tz="Asia/Tokyo", lat=34.6937, lon=135.5023, elev=23, region="JPN", stores=["OSA01"],
                       tmax=[10, 10, 14, 20, 25, 28, 32, 33, 29, 23, 17, 12], tmin=[3, 3, 5, 10, 15, 20, 24, 25, 21, 15, 9, 5],
                       pr=[50, 60, 105, 105, 145, 185, 155, 90, 160, 110, 70, 45], rh=[61, 60, 59, 59, 62, 69, 70, 67, 67, 64, 63, 62], wind=[10, 10, 11, 11, 10, 10, 10, 10, 10, 9, 9, 10]),
    "SEOUL":      dict(name="Seoul", cc="KR", tz="Asia/Seoul", lat=37.5665, lon=126.978, elev=86, region="KOR", stores=["SEL01", "SEL02"],
                       tmax=[2, 5, 11, 18, 23, 28, 29, 30, 26, 20, 12, 4], tmin=[-6, -4, 1, 7, 13, 18, 22, 22, 17, 10, 3, -4],
                       pr=[15, 25, 45, 70, 100, 130, 410, 350, 140, 50, 50, 20], rh=[57, 56, 57, 58, 63, 69, 79, 77, 70, 65, 62, 59], wind=[9, 10, 10, 10, 9, 8, 8, 8, 7, 7, 8, 9]),
    "BUSAN":      dict(name="Busan", cc="KR", tz="Asia/Seoul", lat=35.1796, lon=129.0756, elev=70, region="KOR", stores=["BUS01"],
                       tmax=[8, 10, 14, 19, 23, 26, 28, 30, 27, 22, 16, 10], tmin=[-1, 1, 5, 10, 15, 19, 23, 24, 20, 14, 8, 2],
                       pr=[35, 45, 90, 140, 155, 195, 280, 250, 160, 65, 45, 25], rh=[45, 50, 56, 63, 70, 79, 85, 81, 74, 63, 56, 48], wind=[14, 14, 14, 13, 12, 12, 13, 13, 12, 12, 13, 14]),
    "SHANGHAI":   dict(name="Shanghai", cc="CN", tz="Asia/Shanghai", lat=31.2304, lon=121.4737, elev=4, region="CHE", stores=["SHA01"],
                       tmax=[8, 10, 14, 20, 25, 28, 32, 32, 28, 23, 17, 11], tmin=[1, 3, 6, 11, 17, 21, 26, 26, 22, 16, 10, 3],
                       pr=[75, 60, 90, 80, 95, 190, 150, 210, 110, 60, 50, 40], rh=[74, 74, 74, 74, 75, 81, 80, 80, 77, 72, 72, 71], wind=[11, 12, 12, 12, 11, 11, 11, 11, 11, 10, 10, 10]),
    "BEIJING":    dict(name="Beijing", cc="CN", tz="Asia/Shanghai", lat=39.9042, lon=116.4074, elev=44, region="CHN", stores=["BJS01"],
                       tmax=[2, 6, 13, 21, 27, 30, 31, 30, 26, 19, 10, 3], tmin=[-9, -6, 0, 7, 13, 18, 22, 21, 15, 8, 0, -6],
                       pr=[3, 5, 8, 20, 35, 80, 185, 160, 45, 22, 10, 2], rh=[43, 44, 44, 46, 53, 61, 75, 77, 68, 61, 57, 49], wind=[10, 11, 12, 13, 12, 10, 9, 8, 8, 9, 10, 10]),
    "CHENGDU":    dict(name="Chengdu", cc="CN", tz="Asia/Shanghai", lat=30.5728, lon=104.0668, elev=500, region="CHW", stores=["CDU01"],
                       tmax=[10, 12, 17, 22, 26, 28, 30, 30, 26, 21, 16, 11], tmin=[3, 5, 9, 13, 18, 21, 23, 22, 19, 15, 10, 4],
                       pr=[10, 12, 25, 50, 90, 115, 230, 215, 130, 40, 15, 6], rh=[80, 78, 75, 74, 72, 78, 84, 83, 83, 83, 81, 81], wind=[5, 6, 6, 7, 7, 6, 6, 6, 5, 5, 5, 5]),
    "HONGKONG":   dict(name="Hong Kong", cc="HK", tz="Asia/Hong_Kong", lat=22.3193, lon=114.1694, elev=32, region="SCN", stores=["HKG01"],
                       tmax=[19, 19, 22, 26, 29, 31, 32, 32, 31, 28, 25, 21], tmin=[14, 15, 17, 21, 24, 26, 27, 26, 26, 24, 20, 16],
                       pr=[30, 40, 70, 140, 280, 450, 370, 430, 290, 100, 40, 25], rh=[72, 79, 82, 83, 83, 83, 81, 81, 78, 73, 70, 68], wind=[24, 24, 22, 20, 19, 22, 22, 18, 20, 24, 26, 24]),
    "TAIPEI":     dict(name="Taipei", cc="TW", tz="Asia/Taipei", lat=25.033, lon=121.5654, elev=9, region="SCN", stores=["TPE01"],
                       tmax=[19, 20, 22, 26, 29, 33, 34, 34, 31, 28, 25, 21], tmin=[13, 14, 15, 19, 22, 25, 26, 26, 24, 22, 19, 15],
                       pr=[85, 165, 180, 180, 250, 325, 245, 320, 360, 150, 85, 75], rh=[78, 80, 80, 78, 77, 78, 74, 75, 76, 76, 76, 75], wind=[11, 11, 10, 9, 9, 9, 9, 9, 10, 11, 11, 11]),
    "SINGAPORE":  dict(name="Singapore", cc="SG", tz="Asia/Singapore", lat=1.3521, lon=103.8198, elev=15, region="SEA", stores=["SIN01"],
                       tmax=[30, 31, 32, 32, 32, 31, 31, 31, 31, 31, 31, 30], tmin=[23, 24, 24, 25, 25, 25, 25, 25, 25, 25, 24, 24],
                       pr=[240, 115, 170, 160, 160, 135, 155, 170, 140, 170, 255, 320], rh=[84, 81, 83, 84, 84, 82, 82, 82, 83, 84, 87, 87], wind=[9, 10, 9, 7, 7, 8, 9, 9, 8, 7, 6, 8]),
    "SYDNEY":     dict(name="Sydney", cc="AU", tz="Australia/Sydney", lat=-33.8688, lon=151.2093, elev=39, region="AUS", stores=["SYD01"],
                       tmax=[26, 26, 25, 23, 20, 17, 17, 18, 20, 22, 24, 25], tmin=[19, 19, 18, 15, 12, 9, 8, 9, 11, 14, 16, 18],
                       pr=[90, 120, 130, 110, 100, 130, 70, 80, 60, 75, 85, 75], rh=[70, 72, 71, 70, 70, 69, 64, 60, 59, 62, 65, 68], wind=[13, 13, 12, 11, 11, 12, 12, 13, 14, 14, 14, 14]),
}

STORE_CITY = {s: k for k, c in CITIES.items() for s in c["stores"]}

COUNTRIES = ["IT", "FR", "CH", "GB", "DE", "ES", "NL", "DK", "AE", "US", "CA", "JP", "KR", "CN", "HK", "TW", "SG", "AU"]


def monthly_interp(vals, day):
    """Smooth interpolation of 12 monthly normals (centred mid-month)."""
    pos = (day.timetuple().tm_yday - 15.2) / 30.44
    i0 = math.floor(pos) % 12
    f = pos - math.floor(pos)
    return vals[i0] * (1 - f) + vals[(i0 + 1) % 12] * f


def iso_week_monday(x):
    return x - dt.timedelta(days=x.weekday())
