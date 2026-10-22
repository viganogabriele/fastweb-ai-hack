"""Hong Kong Observatory-style tropical cyclone warning records for Typhoon Yamaneko (山貓), Sep 2026."""
import csv
import datetime as dt
import io
import math
import random
from pathlib import Path

SIGNALS = [
    # seq, code, desc_en, desc_zh, issued, ended, end_type
    (1, "TC1", "Standby Signal No. 1", "一號戒備信號", "2026-09-15 21:40", "2026-09-16 10:20", "replaced"),
    (2, "TC3", "Strong Wind Signal No. 3", "三號強風信號", "2026-09-16 10:20", "2026-09-16 23:40", "replaced"),
    (3, "TC8NE", "No. 8 Northeast Gale or Storm Signal", "八號東北烈風或暴風信號", "2026-09-16 23:40", "2026-09-17 16:15", "replaced"),
    (4, "TC8SE", "No. 8 Southeast Gale or Storm Signal", "八號東南烈風或暴風信號", "2026-09-17 16:15", "2026-09-18 13:40", "replaced"),
    (5, "TC3", "Strong Wind Signal No. 3", "三號強風信號", "2026-09-18 13:40", "2026-09-18 19:20", "replaced"),
    (6, "TC1", "Standby Signal No. 1", "一號戒備信號", "2026-09-18 19:20", "2026-09-19 07:45", "cancelled"),
]
OTHER = [
    ("RAIN_AMBER", "Amber Rainstorm Warning Signal", "黃色暴雨警告信號", "2026-09-17 05:10", "2026-09-17 11:30", "cancelled"),
    ("RAIN_AMBER", "Amber Rainstorm Warning Signal", "黃色暴雨警告信號", "2026-09-17 19:55", "2026-09-17 23:05", "cancelled"),
    ("SURGE", "Storm surge advisory (low-lying areas, Tai O / Lei Yue Mun)", "風暴潮提示", "2026-09-17 09:00", "2026-09-17 18:00", "cancelled"),
]


def fmt_dur(a, b):
    d = dt.datetime.fromisoformat(b) - dt.datetime.fromisoformat(a)
    m = int(d.total_seconds() // 60)
    return f"{m // 60}:{m % 60:02d}"


def signals_csv():
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["tc_name_en", "tc_name_zh", "seq", "signal_code", "signal_desc_en", "signal_desc_zh", "issued_hkt",
                "ended_hkt", "end_type", "duration_hhmm", "remarks"])
    remarks = {3: "Typhoon Yamaneko ~180 km SE of HK at issuance; schools/exchange closed 17 Sep",
               4: "Wind direction change as Yamaneko passed ~140 km SSW of HK (closest approach ~14:00 17 Sep)",
               5: "No. 8 replaced by No. 3; public transport resuming progressively",
               6: "All signals cancelled 07:45 19 Sep"}
    for seq, code, en, zh, a, b, typ in SIGNALS:
        w.writerow(["YAMANEKO", "山貓", seq, code, en, zh, a, b, typ, fmt_dur(a, b), remarks.get(seq, "")])
    for code, en, zh, a, b, typ in OTHER:
        w.writerow(["YAMANEKO", "山貓", "", code, en, zh, a, b, typ, fmt_dur(a, b), "warning in force during TC"])
    return buf.getvalue()


def obs_csv():
    """Hourly 10-min mean wind / gust (km/h) and hourly rainfall, 16 Sep 18:00 - 18 Sep 18:00 HKT."""
    rnd = random.Random(26)
    t0 = dt.datetime(2026, 9, 16, 18)
    close = dt.datetime(2026, 9, 17, 14)
    stations = {"WGL Waglan Island": 1.2, "SE Kai Tak": 0.7, "CCH Cheung Chau": 1.0, "TC Tate's Cairn": 1.15}
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["datetime_hkt", "station", "wind_dir", "mean_wind_kmh", "max_gust_kmh", "rainfall_mm_hkohq"])
    for h in range(49):
        t = t0 + dt.timedelta(hours=h)
        dh = (t - close).total_seconds() / 3600
        base = 85 * math.exp(-((dh / (14.0 if dh < 0 else 24.0)) ** 2)) + 12
        direction = "NE" if dh < -3 else ("E" if dh < 1 else ("SE" if dh < 14 else "S"))
        rain = max(0.0, 28 * math.exp(-(((dh + 4) / 7.0) ** 2)) + rnd.uniform(-2, 3))
        for name, k in stations.items():
            mean = base * k * rnd.uniform(0.94, 1.05)
            gust = mean * rnd.uniform(1.35, 1.6)
            if name.startswith("WGL") and t == dt.datetime(2026, 9, 17, 14):
                w.writerow([t.strftime("%Y-%m-%d %H:%M"), name, "", "", "", f"{rain:.1f}"])  # data gap
                continue
            w.writerow([t.strftime("%Y-%m-%d %H:%M"), name, direction, round(mean), round(gust), f"{rain:.1f}"])
    return buf.getvalue()


BUL_EN = """HONG KONG OBSERVATORY
TROPICAL CYCLONE WARNING BULLETIN
Bulletin issued at 09:45 HKT 17/Sep/2026

The No. 8 Northeast Gale or Storm Signal is in force.
This means that winds with mean speeds of 63 km/h or more are expected from the northeast quarter.

At 9 a.m., Typhoon Yamaneko was centred about 160 kilometres south-southeast of Hong Kong (near 20.9 degrees north,
114.6 degrees east) and is forecast to move west-northwest at about 16 kilometres per hour, skirting about 140
kilometres south-southwest of Hong Kong this afternoon. Maximum sustained winds near its centre are about 150 km/h.

In the past hour the maximum sustained winds recorded at Waglan Island and Cheung Chau were 104 and 88 km/h,
with maximum gusts of 151 and 126 km/h respectively.

As Yamaneko moves to the west of Hong Kong, local winds will gradually veer to southeasterly this afternoon.
The Observatory will consider replacing the No. 8 Northeast Gale or Storm Signal by the No. 8 Southeast Gale
or Storm Signal between 3 p.m. and 5 p.m. today. Under the present forecast track, the No. 8 Signal is expected
to remain in force for most of today and tonight.

Under the influence of Yamaneko's outer rainbands, there will be heavy squally showers. The Amber Rainstorm
Warning Signal is in force. Seas will be very rough with swells. There will be flooding in low-lying coastal
areas, and the water level may rise by about 1 metre above normal at around noon today.

Precautions:
Members of the public should stay indoors and away from exposed windows and doors. Do not stay near the shoreline
or engage in water sports. Please make sure that all loose objects are secured.

Next bulletin will be issued at around 10:45 HKT.
"""

BUL_ZH = """香港天文台
熱帶氣旋警告
二〇二六年九月十七日上午九時四十五分發出

八號東北烈風或暴風信號現正生效。
這表示香港近海平面處現正或預料會普遍吹東北方烈風或暴風，持續風力每小時63公里或以上。

在上午9時，颱風山貓集結在香港之東南偏南約160公里，即北緯20.9度，東經114.6度附近，預料向西北偏西移動，時速約16公里，今日下午在香港之西南偏南約140公里掠過。山貓中心附近最高持續風速估計為每小時150公里。

過去一小時，橫瀾島及長洲錄得的最高持續風速分別為每小時104及88公里，最高陣風分別超過每小時151及126公里。

隨著山貓移至香港以西，本港風向會在今日下午逐漸轉為東南。天文台會在今日下午3時至5時考慮以八號東南烈風或暴風信號取代八號東北烈風或暴風信號。

受山貓外圍雨帶影響，本港有狂風大驟雨。黃色暴雨警告信號現正生效。海面風高浪急，有湧浪。低窪沿岸地區會出現水浸，今日中午前後水位可能較正常高出約1米。

注意事項：
市民應留在室內，遠離當風門窗。切勿在海灘逗留或進行水上活動。請確保所有易被吹走的物件已經妥為綁緊。

下一次熱帶氣旋警告將於上午10時45分左右發出。
"""

BUL_EN_0818 = """HONG KONG OBSERVATORY
TROPICAL CYCLONE WARNING BULLETIN
Bulletin issued at 10:45 HKT 18/Sep/2026

The No. 8 Southeast Gale or Storm Signal is in force.

At 10 a.m., Severe Tropical Storm Yamaneko (weakened from typhoon) was centred about 260 kilometres west-southwest
of Hong Kong and is forecast to move west at about 18 km/h across the coast of western Guangdong.

Local winds are gradually moderating. In the past hour the maximum sustained winds recorded at Waglan Island and
Cheung Chau were 66 and 58 km/h, with maximum gusts of 95 and 84 km/h respectively.

The Observatory will consider replacing the No. 8 Southeast Gale or Storm Signal with the Strong Wind Signal No. 3
between noon and 2 p.m. today. Members of the public should take note that winds may remain strong offshore and on
high ground for some time after the No. 8 Signal is lowered.

Next bulletin will be issued at around 11:45 HKT.
"""

PRESS = """Press Release - 18 September 2026 (13:42 HKT)

Observatory replaces No. 8 Signal with Strong Wind Signal No. 3

The Hong Kong Observatory replaced the No. 8 Southeast Gale or Storm Signal with the Strong Wind Signal No. 3 at
1.40 pm today, as Yamaneko continued to move away from Hong Kong. Strong winds are still affecting offshore waters
and high ground.

The No. 8 Signal had been in force for 38 hours since 11.40 pm on 16 September.

The Transport Department said that MTR services are being restored progressively, with normal frequencies expected
by mid-afternoon. Franchised bus and ferry services will resume gradually subject to road and sea conditions.
Members of the public are advised to allow extra travelling time. Kindergartens and schools remain closed for the
rest of the day.

Employers are reminded to be flexible regarding the arrangements for staff to return to work, taking into account
the time needed for public transport services to resume.

政府新聞處 / Information Services Department (mirror)
"""

PRESS_ZH = """新聞公報　二〇二六年九月十八日（下午1時42分）

天文台以三號強風信號取代八號烈風或暴風信號

天文台於今日下午1時40分以三號強風信號取代八號東南烈風或暴風信號。山貓逐漸遠離本港，但離岸及高地仍吹強風。

八號信號自九月十六日晚上11時40分起生效，歷時38小時。

運輸署表示，港鐵服務正逐步恢復，預計下午較後時間回復正常班次；專營巴士及渡輪服務將視乎路面及海面情況陸續恢復。僱主應考慮員工返回工作地點所需時間，靈活處理上班安排。
"""


def build(out_dir: Path):
    d = out_dir / "hongkong"
    d.mkdir(parents=True, exist_ok=True)
    (d / "hko_tc_signals_YAMANEKO_2026.csv").write_text(signals_csv(), encoding="utf-8")
    (d / "hko_station_obs_2026-09-16_18.csv").write_text(obs_csv(), encoding="utf-8")
    (d / "tcwb_2026-09-17_0945_en.txt").write_text(BUL_EN, encoding="utf-8")
    (d / "tcwb_2026-09-17_0945_zh-hk.txt").write_text(BUL_ZH, encoding="utf-8")
    (d / "tcwb_2026-09-18_1045_en.txt").write_text(BUL_EN_0818, encoding="utf-8")
    (d / "press_release_2026-09-18_signal3_en.txt").write_text(PRESS, encoding="utf-8")
    (d / "press_release_2026-09-18_signal3_zh-hk.txt").write_text(PRESS_ZH, encoding="utf-8")
