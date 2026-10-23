"""Tourism: monthly arrivals by nationality (official-statistics look-alikes with publication lags), weekly air seat
capacity, weekly hotel KPIs, weekly tax-free spend index (raw refund-operator feed), HK daily immigration,
CN Golden Week border statistics."""
import csv
import datetime as dt
import io
import json
import math

import numpy as np
import pandas as pd

from common import CITIES, OUT, d, drange, mkdir, rng_for, write_json

T = mkdir(OUT / "tourism")
TD = dt.timedelta
MONTHS = pd.period_range("2024-09", "2026-10", freq="M")

# ---------------------------------------------------------------------------------------------- monthly model
SEAS = {
    "CN": [0.85, 1.0, 0.8, 0.9, 0.95, 0.85, 1.15, 1.25, 0.95, 1.35, 0.9, 0.85],
    "HK": [0.95, 1.0, 0.9, 1.1, 0.9, 0.85, 1.1, 1.15, 0.9, 1.05, 0.95, 1.15],
    "TW": [0.95, 1.05, 0.9, 1.0, 0.95, 0.9, 1.15, 1.15, 0.9, 1.0, 0.95, 1.1],
    "KR": [1.15, 1.0, 0.8, 0.85, 0.95, 0.9, 1.1, 1.2, 1.0, 1.05, 0.9, 1.1],
    "JP": [0.9, 0.85, 1.1, 0.85, 1.05, 0.85, 0.95, 1.3, 1.1, 1.0, 0.95, 1.1],
    "US": [0.65, 0.65, 0.85, 1.0, 1.2, 1.35, 1.35, 1.2, 1.1, 0.95, 0.8, 0.8],
    "EU": [0.7, 0.75, 0.9, 1.05, 1.1, 1.15, 1.25, 1.25, 1.1, 1.0, 0.8, 0.85],
    "GCC": [0.6, 0.6, 0.75, 0.9, 0.9, 1.4, 1.8, 1.6, 0.9, 0.8, 0.75, 0.8],
    "IN": [0.8, 0.75, 0.8, 1.0, 1.4, 1.4, 1.0, 1.0, 0.9, 1.05, 1.0, 0.9],
    "AU": [0.9, 0.7, 0.85, 1.05, 1.0, 1.2, 1.25, 1.0, 1.15, 1.0, 0.9, 0.95],
    "SEA": [1.0, 0.95, 0.95, 1.0, 0.95, 1.1, 1.0, 0.95, 0.9, 0.95, 1.0, 1.25],
    "LATAM": [1.2, 1.0, 0.9, 0.9, 0.85, 0.95, 1.25, 1.05, 0.85, 0.9, 0.95, 1.15],
    "NA_SNOW": [1.3, 1.3, 1.2, 0.9, 0.8, 0.9, 1.0, 1.0, 0.9, 0.85, 0.85, 1.0],
}
NATGRP = {"CN": "CN", "HK": "HK", "TW": "TW", "KR": "KR", "JP": "JP", "US": "US", "CA": "US", "GB": "EU", "DE": "EU", "FR": "EU", "IT": "EU",
          "ES": "EU", "NL": "EU", "CH": "EU", "AT": "EU", "DK": "EU", "SE": "EU", "BE": "EU", "GCC": "GCC", "SA": "GCC", "AE": "GCC", "IN": "IN",
          "AU": "AU", "NZ": "AU", "SG": "SEA", "TH": "SEA", "ID": "SEA", "MY": "SEA", "PH": "SEA", "VN": "SEA", "BR": "LATAM", "MX": "LATAM",
          "AR": "LATAM", "CO": "LATAM", "RU": "EU", "TR": "EU", "PL": "EU", "IL": "EU", "OTH": "EU"}
DEST_SEAS = {  # destination climate/season factor
    "IT-MI": [0.8, 0.9, 1.0, 1.05, 1.1, 1.05, 0.95, 0.8, 1.15, 1.1, 1.0, 0.9], "IT-RM": [0.65, 0.7, 0.95, 1.15, 1.2, 1.15, 1.05, 1.0, 1.15, 1.15, 0.85, 0.85],
    "IT-VE": [0.5, 0.7, 0.9, 1.15, 1.25, 1.2, 1.2, 1.2, 1.25, 1.05, 0.65, 0.75], "IT-CO": [2.0, 2.1, 1.6, 0.8, 0.2, 0.4, 1.0, 1.3, 0.5, 0.2, 0.2, 1.5],
    "SKI": [2.0, 2.1, 1.6, 0.6, 0.15, 0.5, 1.1, 1.2, 0.5, 0.2, 0.3, 1.6], "FR-PA": [0.75, 0.8, 0.95, 1.05, 1.1, 1.15, 1.1, 1.0, 1.1, 1.05, 0.9, 0.95],
    "FR-CA": [0.5, 0.6, 0.75, 1.0, 1.25, 1.35, 1.5, 1.5, 1.2, 0.85, 0.6, 0.6], "CITY": [0.8, 0.85, 0.95, 1.05, 1.1, 1.1, 1.1, 1.05, 1.05, 1.05, 0.9, 0.95],
    "AE-DU": [1.25, 1.2, 1.15, 1.0, 0.8, 0.65, 0.65, 0.7, 0.8, 1.05, 1.25, 1.35], "SUN": [1.0] * 12, "AU": [1.1, 0.95, 1.0, 0.9, 0.85, 0.95, 1.05, 0.95, 0.95, 1.0, 1.05, 1.25],
}
# annual base (thousands) per destination and nationality
DEST = {
    "IT-MI": dict(seas="IT-MI", base={"US": 520, "CN": 380, "DE": 330, "FR": 300, "GB": 290, "ES": 200, "CH": 190, "KR": 120, "JP": 115, "GCC": 105, "IN": 95, "BR": 90, "OTH": 1600}),
    "IT-RM": dict(seas="IT-RM", base={"US": 1350, "DE": 420, "GB": 480, "FR": 430, "ES": 420, "CN": 210, "KR": 175, "JP": 150, "GCC": 70, "IN": 80, "BR": 160, "OTH": 2300}),
    "IT-VE": dict(seas="IT-VE", base={"US": 690, "FR": 360, "DE": 400, "GB": 320, "CN": 190, "KR": 140, "JP": 95, "ES": 210, "GCC": 30, "IN": 40, "BR": 60, "OTH": 1500}),
    "IT-CO": dict(seas="IT-CO", base={"DE": 30, "GB": 18, "US": 14, "CH": 12, "FR": 10, "OTH": 40}),
    "FR-PA": dict(seas="FR-PA", base={"US": 1700, "GB": 850, "DE": 640, "IT": 620, "ES": 600, "CN": 520, "JP": 330, "KR": 270, "GCC": 310, "IN": 160, "BR": 230, "OTH": 3300}),
    "FR-CA": dict(seas="FR-CA", base={"GB": 420, "US": 380, "IT": 330, "DE": 260, "GCC": 140, "CH": 150, "OTH": 900}),
    "GB-LO": dict(seas="CITY", base={"US": 2400, "FR": 1700, "DE": 1350, "ES": 1000, "IT": 950, "NL": 800, "IN": 700, "GCC": 750, "CN": 520, "AU": 550, "JP": 260, "KR": 210, "OTH": 7500}),
    "DE-MU": dict(seas="CITY", base={"US": 470, "IT": 330, "AT": 290, "CH": 280, "GB": 280, "CN": 190, "GCC": 190, "FR": 150, "ES": 140, "JP": 70, "KR": 60, "OTH": 1900}),
    "DE-BE": dict(seas="CITY", base={"US": 450, "GB": 440, "NL": 330, "IT": 330, "ES": 280, "DK": 210, "FR": 200, "CN": 120, "KR": 70, "JP": 60, "OTH": 2400}),
    "CH-ZH": dict(seas="CITY", base={"DE": 450, "US": 330, "GB": 150, "CN": 100, "IN": 100, "GCC": 75, "FR": 110, "IT": 90, "KR": 35, "JP": 45, "OTH": 1000}),
    "CH-GE": dict(seas="CITY", base={"US": 150, "FR": 150, "GB": 120, "DE": 90, "GCC": 90, "CN": 45, "IN": 40, "IT": 60, "JP": 15, "KR": 10, "OTH": 700}),
    "CH-SM": dict(seas="SKI", base={"DE": 62, "IT": 45, "GB": 20, "US": 15, "FR": 8, "GCC": 6, "OTH": 94}),
    "ES-MD": dict(seas="CITY", base={"US": 1100, "MX": 450, "CO": 330, "AR": 300, "FR": 400, "IT": 380, "GB": 350, "DE": 260, "CN": 180, "KR": 110, "JP": 90, "OTH": 2600}),
    "NL": dict(seas="CITY", base={"DE": 5200, "GB": 2400, "BE": 2100, "US": 1900, "FR": 900, "IT": 700, "ES": 700, "CN": 300, "KR": 90, "JP": 140, "OTH": 6500}),
    "DK": dict(seas="CITY", base={"DE": 3200, "SE": 1200, "NL": 900, "GB": 500, "US": 450, "IT": 250, "FR": 200, "CN": 120, "OTH": 3000}),
    "AE-DU": dict(seas="AE-DU", base={"IN": 2100, "SA": 1550, "GB": 1300, "RU": 1250, "CN": 750, "US": 880, "DE": 600, "FR": 420, "IT": 300, "KR": 120, "OTH": 9500}),
    "US": dict(seas="CITY", base={"GB": 4000, "JP": 2400, "DE": 2000, "IN": 2100, "BR": 1800, "FR": 1700, "KR": 1600, "CN": 1250, "AU": 1300, "IT": 1100, "ES": 950, "OTH": 20000}),
    "CA": dict(seas="CITY", base={"US": 15000, "GB": 780, "FR": 610, "IN": 400, "CN": 380, "DE": 360, "MX": 400, "AU": 260, "JP": 210, "KR": 200, "OTH": 2400}),
    "JP": dict(seas="CITY", base={"KR": 9600, "CN": 9300, "TW": 6600, "US": 3100, "HK": 2600, "TH": 1250, "AU": 1050, "PH": 880, "SG": 720, "VN": 700, "IN": 280, "GB": 470, "FR": 360, "OTH": 4500}),
    "KR": dict(seas="CITY", base={"CN": 6100, "JP": 3500, "TW": 1800, "US": 1450, "HK": 650, "VN": 560, "TH": 450, "PH": 520, "SG": 300, "OTH": 3300}),
    "HK": dict(seas="SUN", base={"CN": 35000, "PH": 900, "TW": 800, "US": 600, "KR": 750, "JP": 520, "TH": 650, "SG": 450, "AU": 400, "GB": 380, "OTH": 3500}),
    "TW": dict(seas="SUN", base={"JP": 1450, "KR": 1150, "HK": 1500, "US": 640, "CN": 300, "MY": 500, "SG": 480, "PH": 450, "TH": 420, "VN": 450, "OTH": 1300}),
    "SG": dict(seas="SUN", base={"CN": 3100, "ID": 2400, "IN": 1250, "AU": 1200, "MY": 1200, "PH": 750, "US": 700, "KR": 600, "JP": 580, "GB": 650, "OTH": 4500}),
    "AU": dict(seas="AU", base={"NZ": 1400, "CN": 900, "US": 820, "GB": 640, "IN": 520, "SG": 420, "JP": 380, "KR": 320, "MY": 330, "HK": 240, "OTH": 2600}),
}
TREND = {"CN": 0.13, "KR": 0.07, "JP": -0.03, "US": 0.02, "GCC": 0.06, "IN": 0.09, "TW": 0.05, "HK": 0.03}
CNY_MONTH = {2025: 1, 2026: 2}
CHUSEOK_MONTH = {2024: 9, 2025: 10, 2026: 9}


def monthly(dest, nat):
    r = rng_for(f"tour-{dest}-{nat}")
    cfg = DEST[dest]
    base = cfg["base"][nat] * 1000 / 12
    grp = NATGRP.get(nat, "EU")
    out = []
    for p in MONTHS:
        m = p.month - 1
        nat_s = SEAS[grp][m]
        if grp in ("CN", "HK", "TW", "KR", "SEA") and m in (0, 1):  # CNY timing
            nat_s = SEAS[grp][m] * (1.18 if CNY_MONTH.get(p.year) == p.month else 0.92)
        if grp == "KR" and p.month in (9, 10):
            nat_s *= 1.12 if CHUSEOK_MONTH.get(p.year) == p.month else 0.95
        v = base * nat_s * DEST_SEAS[cfg["seas"]][m]
        yrs = (p.start_time - pd.Timestamp("2025-09-01")).days / 365
        v *= (1 + TREND.get(grp, 0.02)) ** yrs
        # destination/period specifics
        if dest == "IT-RM" and p.year == 2025:
            v *= 1.10  # Jubilee
        if dest in ("IT-MI", "IT-CO") and str(p) == "2026-02":
            v *= 1.28  # Winter Olympics
        if dest == "JP" and "2025-04" <= str(p) <= "2025-10":
            v *= 1.05  # Expo Osaka
        if dest in ("IT-MI", "FR-PA") and nat == "CN" and p.year == 2026 and p.month >= 7:
            v *= 1.14  # new direct flights / visa fast track
        if dest in ("IT-MI", "FR-PA", "GB-LO") and nat == "KR" and str(p) in ("2026-09", "2026-10"):
            v *= 1.22  # post-Chuseok K-tourists
        if dest == "HK" and str(p) == "2026-09":
            v *= 0.95  # typhoon
        if dest in ("US", "CA") and str(p) in ("2026-06", "2026-07"):
            v *= 1.12  # FIFA World Cup
        if dest == "AE-DU" and nat in ("SA", "GCC") and str(p) in ("2025-03", "2026-03"):
            v *= 0.7  # Ramadan
        v *= float(r.lognormal(0, 0.035))
        out.append(v)
    return pd.Series(out, index=MONTHS)


MODEL = {dest: {nat: monthly(dest, nat) for nat in cfg["base"]} for dest, cfg in DEST.items()}


def upto(series, last):
    return series[series.index <= pd.Period(last, "M")]


A = mkdir(T / "arrivals_official")

# 1. IT ISTAT-like (latest 2026-07, provisional for 2026)
IT_N = {"US": "Stati Uniti d'America", "CN": "Cina", "DE": "Germania", "FR": "Francia", "GB": "Regno Unito", "ES": "Spagna", "CH": "Svizzera e Liechtenstein",
        "KR": "Corea del Sud", "JP": "Giappone", "GCC": "Paesi del Golfo", "IN": "India", "BR": "Brasile", "OTH": "Altri paesi esteri"}
COMUNE = {"IT-MI": "Milano", "IT-RM": "Roma", "IT-VE": "Venezia", "IT-CO": "Cortina d'Ampezzo"}
rows = ["Comune;Anno;Mese;Paese di residenza;Arrivi;Presenze;Stato del dato"]
for dest, com in COMUNE.items():
    for nat, s in MODEL[dest].items():
        for p, v in upto(s, "2026-07").items():
            arr = int(round(v))
            pres = int(round(arr * {"US": 2.6, "CN": 1.8, "KR": 2.0, "JP": 2.1}.get(nat, 2.4) * (1.3 if dest == "IT-CO" else 1)))
            st = "provvisorio" if p.year == 2026 else "definitivo"
            fmt_a = f"{arr:,}".replace(",", ".") if dest == "IT-VE" else str(arr)  # Venezia uses thousand separators
            rows.append(f"{com};{p.year};{p.month};{IT_N[nat]};{fmt_a};{pres};{st}")
    # total foreign
mkdir(A / "IT")
(A / "IT" / "movimento_clienti_esercizi_ricettivi_comuni_2024-2026.csv").write_text("\n".join(rows) + "\n", encoding="latin-1", errors="replace")

# 2. FR - Paris (IDF hotels) + Alpes-Maritimes, wide months, thousands with decimal comma (latest 2026-08)
FR_N = {"US": "États-Unis", "GB": "Royaume-Uni", "DE": "Allemagne", "IT": "Italie", "ES": "Espagne", "CN": "Chine", "JP": "Japon", "KR": "Corée du Sud",
        "GCC": "Pays du Golfe", "IN": "Inde", "BR": "Brésil", "CH": "Suisse", "OTH": "Autres pays étrangers"}
for dest, lab in (("FR-PA", "Paris (75) - hôtellerie"), ("FR-CA", "Alpes-Maritimes (06) - hôtellerie")):
    months = [p for p in MONTHS if p <= pd.Period("2026-08", "M")]
    buf = [f"Arrivées hôtelières de la clientèle non résidente - {lab}", "Unité : milliers d'arrivées. Source : enquête de fréquentation hôtelière. (p) provisoire", "",
           "Nationalité;" + ";".join(f"{p.year}-{p.month:02d}" + (" (p)" if p >= pd.Period("2026-06", "M") else "") for p in months)]
    for nat, s in MODEL[dest].items():
        buf.append(FR_N[nat] + ";" + ";".join(f"{s[p] / 1000:.1f}".replace(".", ",") for p in months))
    mkdir(A / "FR")
    (A / "FR" / f"frequentation_hoteliere_{'paris' if dest == 'FR-PA' else 'alpes_maritimes'}_2024-2026.csv").write_text("\n".join(buf) + "\n", encoding="utf-8")

# 3. GB quarterly (latest 2026 Q2)
rows = ["year,quarter,area,country_of_residence,visits_000,nights_000,spend_gbp_m"]
for nat, s in MODEL["GB-LO"].items():
    q = s.groupby(lambda p: (p.year, (p.month - 1) // 3 + 1)).sum()
    for (y, qq), v in q.items():
        if (y, qq) > (2026, 2) or (y, qq) < (2024, 4):
            continue
        spend = v / 1000 * {"US": 1.15, "GCC": 2.4, "CN": 1.6, "IN": 0.9, "KR": 1.1, "JP": 1.0}.get(nat, 0.65)
        rows.append(f"{y},Q{qq},London,{nat if nat != 'OTH' else 'Other countries'},{v / 1000:.0f},{v / 1000 * 5.8:.0f},{spend:.1f}")
mkdir(A / "GB")
(A / "GB" / "inbound_visits_london_quarterly.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

# 4. DE Destatis-like (latest 2026-08)
DE_N = {"US": "Vereinigte Staaten", "IT": "Italien", "AT": "Österreich", "CH": "Schweiz", "GB": "Vereinigtes Königreich", "CN": "China (einschl. Hongkong)",
        "GCC": "Arabische Golfstaaten", "FR": "Frankreich", "ES": "Spanien", "JP": "Japan", "KR": "Korea, Republik", "NL": "Niederlande", "DK": "Dänemark",
        "OTH": "Übrige Länder"}
buf = ["GENESIS-Tabelle: 45412-0035 (Auszug)", "Ankünfte und Übernachtungen in Beherbergungsbetrieben: Gemeinden, Monate, Herkunftsländer", "Stand: 15.10.2026",
       "", "Gemeinde;Jahr;Monat;Herkunftsland;Ankünfte;Übernachtungen"]
MON_DE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
for dest, gem in (("DE-MU", "München, Landeshauptstadt"), ("DE-BE", "Berlin")):
    for nat, s in MODEL[dest].items():
        for p, v in upto(s, "2026-08").items():
            a = int(round(v))
            ub = "." if (dest == "DE-BE" and str(p) == "2026-08" and nat == "OTH") else str(int(a * 2.2))
            buf.append(f"{gem};{p.year};{MON_DE[p.month - 1]};{DE_N[nat]};{a};{ub}")
buf += ["", "__________", "Zeichenerklärung: . = Zahlenwert unbekannt oder geheimzuhalten; - = nichts vorhanden", "(C) Statistisches Bundesamt-Mirror, 2026"]
mkdir(A / "DE")
(A / "DE" / "45412-0035_beherbergung_muenchen_berlin.csv").write_text("\n".join(buf) + "\n", encoding="cp1252", errors="replace")

# 5. CH HESTA-like (latest 2026-08), multilingual headers
CH_N = {"DE": "Deutschland / Allemagne", "US": "Vereinigte Staaten / États-Unis", "GB": "Vereinigtes Königreich / Royaume-Uni", "CN": "China / Chine",
        "IN": "Indien / Inde", "GCC": "Golfstaaten / États du Golfe", "FR": "Frankreich / France", "IT": "Italien / Italie", "KR": "Korea (Süd) / Corée (Sud)",
        "JP": "Japan / Japon", "OTH": "Übrige / Autres"}
rows = ["Gemeinde/Commune,Jahr/Année,Monat/Mois,Herkunftsland/Pays de provenance,Ankünfte/Arrivées,Logiernächte/Nuitées"]
for dest, gem in (("CH-ZH", "Zürich"), ("CH-GE", "Genève"), ("CH-SM", "St. Moritz")):
    for nat, s in MODEL[dest].items():
        for p, v in upto(s, "2026-08").items():
            rows.append(f"{gem},{p.year},{p.month},{CH_N[nat]},{int(round(v))},{int(round(v * (2.1 if dest != 'CH-SM' else 3.4)))}")
mkdir(A / "CH")
(A / "CH" / "hesta_communes_provenance.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

# 6. ES FRONTUR-like Madrid (latest 2026-08)
ES_N = {"US": "Estados Unidos de América", "MX": "México", "CO": "Colombia", "AR": "Argentina", "FR": "Francia", "IT": "Italia", "GB": "Reino Unido",
        "DE": "Alemania", "CN": "China", "KR": "Corea del Sur", "JP": "Japón", "OTH": "Resto del mundo"}
rows = ["Comunidad autónoma de destino\tPaís de residencia\tPeriodo\tTotal"]
for nat, s in MODEL["ES-MD"].items():
    for p, v in upto(s, "2026-08").items():
        rows.append(f"Madrid, Comunidad de\t{ES_N[nat]}\t{p.year}M{p.month:02d}\t{int(round(v)):,}".replace(",", "."))
mkdir(A / "ES")
(A / "ES" / "frontur_turistas_madrid_pais_residencia.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")

# 7. Eurostat-like TSV for NL & DK (+ national totals), latest 2026-07 with flags
months = [p for p in MONTHS if p <= pd.Period("2026-07", "M")]
hdr = "freq,c_resid,unit,nace_r2,geo\\TIME_PERIOD\t" + "\t".join(f"{p.year}-{p.month:02d} " for p in months)
lines = [hdr]
for geo in ("NL", "DK"):
    for nat, s in MODEL[geo].items():
        code = {"OTH": "NOT_EU27_2020_X"}.get(nat, nat)
        vals = []
        for p in months:
            v = int(round(s[p]))
            flag = " p" if p >= pd.Period("2026-05", "M") else ""
            if geo == "DK" and str(p) == "2025-12" and nat in ("CN", "IT"):
                vals.append(": c")
            else:
                vals.append(f"{v}{flag}")
        lines.append(f"M,{code},NR,I551-I553,{geo}\t" + "\t".join(vals))
mkdir(A / "EU")
(A / "EU" / "estat_tour_occ_arnat_NL_DK.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")

# 8. Dubai - YTD cumulative by source (latest Jan-Aug 2026)
rows = ["period,source_market,international_overnight_visitors_ytd_mn"]
for nat, s in MODEL["AE-DU"].items():
    for y in (2025, 2026):
        cum = 0
        for p, v in s.items():
            if p.year != y or p > pd.Period("2026-08", "M"):
                continue
            cum += v
            rows.append(f"{['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][p.month - 1]}-{y} YTD,{nat},{cum / 1e6:.2f}")
mkdir(A / "AE")
(A / "AE" / "dubai_visitors_ytd_by_source.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

# 9. US NTTO-like (latest 2026-07)
rows = ["Country of Residence,Year,Month,Arrivals (Overseas + Canada + Mexico air),of which Port of Entry New York (JFK/EWR),of which Port Miami,of which Port Los Angeles"]
for nat, s in MODEL["US"].items():
    for p, v in upto(s, "2026-07").items():
        ny = {"GB": 0.28, "CN": 0.18, "KR": 0.14, "JP": 0.12, "IT": 0.30, "FR": 0.27, "BR": 0.10, "IN": 0.20}.get(nat, 0.2)
        rows.append(f"{nat},{p.year},{p.month},{int(round(v))},{int(round(v * ny))},{int(round(v * 0.08))},{int(round(v * 0.13))}")
mkdir(A / "US")
(A / "US" / "i94_arrivals_by_residence.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

# 10. CA StatCan-like (latest 2026-08)
rows = ["REF_DATE,GEO,Traveller characteristics,Country of residence,UOM,VALUE,STATUS"]
for nat, s in MODEL["CA"].items():
    for p, v in upto(s, "2026-08").items():
        rows.append(f"{p.year}-{p.month:02d},Ontario,Non-resident visitors entering Canada,{nat},Number,{int(round(v * 0.38))},{'A' if p.year < 2026 else 'E'}")
mkdir(A / "CA")
(A / "CA" / "24100053_international_travellers_ontario.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

# 11. JP JNTO-like (latest 2026-09 estimate)
JP_N = {"KR": "韓国", "CN": "中国", "TW": "台湾", "US": "米国", "HK": "香港", "TH": "タイ", "AU": "豪州", "PH": "フィリピン", "SG": "シンガポール",
        "VN": "ベトナム", "IN": "インド", "GB": "英国", "FR": "フランス", "OTH": "その他"}
months = [p for p in MONTHS if p <= pd.Period("2026-09", "M")]
lines = ["国・地域," + ",".join(f"{p.year}年{p.month}月" for p in months), "," + ",".join("推計値" if p == months[-1] else "暫定値" if p >= pd.Period("2026-01", "M") else "確定値" for p in months)]
for nat, s in MODEL["JP"].items():
    lines.append(JP_N[nat] + "," + ",".join(str(int(round(s[p]))) for p in months))
tot = sum(MODEL["JP"][n] for n in MODEL["JP"])
lines.append("総数," + ",".join(str(int(round(tot[p]))) for p in months))
mkdir(A / "JP")
(A / "JP" / "訪日外客数_国籍別_2024-2026.csv").write_text("﻿" + "\n".join(lines) + "\n", encoding="utf-8")

# 12. KR KTO-like inbound + Korean outbound departures (latest 2026-09)
KR_N = {"CN": "중국", "JP": "일본", "TW": "대만", "US": "미국", "HK": "홍콩", "VN": "베트남", "TH": "태국", "PH": "필리핀", "SG": "싱가포르", "OTH": "기타"}
rows = ["기준년월,국적,입국자수"]
for nat, s in MODEL["KR"].items():
    for p, v in upto(s, "2026-09").items():
        rows.append(f"{p.year}{p.month:02d},{KR_N[nat]},{int(round(v))}")
r = rng_for("kr-out")
out_rows = ["기준년월,국민해외관광객(명),전년동월대비(%),주요 목적지 비중 - 일본(%),중국(%),동남아(%),유럽(%),미주(%)"]
prev = {}
for p in MONTHS:
    if p > pd.Period("2026-09", "M"):
        continue
    base = 2_350_000 * SEAS["KR"][p.month - 1] * (1.06 ** ((p.start_time - pd.Timestamp("2025-01-01")).days / 365))
    if CHUSEOK_MONTH.get(p.year) == p.month:
        base *= 1.08
    v = int(base * r.lognormal(0, 0.02))
    eu = 6.8 + (1.6 if str(p) in ("2026-09",) else 0) + r.normal(0, 0.3)
    prev[str(p)] = v
    ly = prev.get(f"{p.year - 1}-{p.month:02d}")
    yoy = f"{(v / ly - 1) * 100:.1f}" if ly else ""
    out_rows.append(f"{p.year}-{p.month:02d},{v},{yoy},{38 + r.normal(0, 1.2):.1f},{11 + r.normal(0, 0.8):.1f},{27 + r.normal(0, 1):.1f},{eu:.1f},{8 + r.normal(0, 0.5):.1f}")
mkdir(A / "KR")
(A / "KR" / "외래관광객_국적별_입국.csv").write_bytes(("\n".join(rows) + "\n").encode("cp949"))
(A / "KR" / "국민해외관광객_월별.csv").write_text("\n".join(out_rows) + "\n", encoding="utf-8")

# 13. TW (latest 2026-08)
rows = ["年月,居住地,人次"]
for nat, s in MODEL["TW"].items():
    for p, v in upto(s, "2026-08").items():
        rows.append(f"{p.year - 1911}年{p.month}月,{ {'JP': '日本', 'KR': '韓國', 'HK': '香港', 'US': '美國', 'CN': '大陸', 'MY': '馬來西亞', 'SG': '新加坡', 'PH': '菲律賓', 'TH': '泰國', 'VN': '越南', 'OTH': '其他'}[nat]},{int(round(v))}")
mkdir(A / "TW")
(A / "TW" / "來臺旅客_居住地_月報.csv").write_text("﻿" + "\n".join(rows) + "\n", encoding="utf-8")

# 14. SG (latest 2026-09)
rows = ["month,country_of_residence,visitor_arrivals"]
for nat, s in MODEL["SG"].items():
    for p, v in upto(s, "2026-09").items():
        mult = 1.07 if str(p) == "2026-10" else 1.0
        rows.append(f"{p.strftime('%Y %b')},{ {'CN': 'China', 'ID': 'Indonesia', 'IN': 'India', 'AU': 'Australia', 'MY': 'Malaysia', 'PH': 'Philippines', 'US': 'USA', 'KR': 'South Korea', 'JP': 'Japan', 'GB': 'UK', 'OTH': 'Others'}[nat]},{int(round(v * mult))}")
mkdir(A / "SG")
(A / "SG" / "visitor_arrivals_by_country_of_residence.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

# 15. AU ABS-like (latest 2026-08), in '000 with one decimal
rows = ["Series ID,Month,Country of residence,Short-term visitor arrivals ('000),Series type"]
for nat, s in MODEL["AU"].items():
    for p, v in upto(s, "2026-08").items():
        rows.append(f"A8540{abs(hash(nat)) % 1000:03d}X,{p.strftime('%b-%Y')},{nat},{v / 1000:.1f},Original")
mkdir(A / "AU")
(A / "AU" / "340101_short_term_visitor_arrivals.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
(A / "README.txt").write_text(
    "Monthly international arrivals by nationality/residence, as downloaded from the respective official-statistics portals.\n"
    "Coverage and publication lags differ: IT to Jul-2026 (provisional 2026), FR/DE/CH/ES/CA/TW/AU/AE to Aug-2026, NL/DK (Eurostat) to Jul-2026,\n"
    "GB quarterly to 2026-Q2, US to Jul-2026, JP/KR/SG to Sep-2026 (JP last month = estimate).\n"
    "Definitions differ (hotel arrivals vs border arrivals vs visitors; residence vs nationality); do not add up across sources.\n", encoding="utf-8")

# ---------------------------------------------------------------------------------------------- HK daily immigration
r = rng_for("hk-immd")
rows = ["Date,Control Point,Arrival / Departure,Hong Kong Residents,Mainland Visitors,Other Visitors,Total"]
mon_vis = {p: sum(v[p] for n, v in MODEL["HK"].items() if n != "CN") / p.days_in_month for p in MODEL["HK"]["CN"].index}
mon_cn = {p: MODEL["HK"]["CN"][p] / p.days_in_month for p in MODEL["HK"]["CN"].index}
for x in drange("2024-09-01", "2026-10-21"):
    p = pd.Period(x, "M")
    wk = [0.9, 0.88, 0.9, 0.95, 1.05, 1.25, 1.1][x.weekday()]
    gw = 1.0
    if x.month == 10 and 1 <= x.day <= 7:
        gw = 1.55 if x.year == 2026 else 1.45
    cnv = mon_cn[p] * wk * gw * r.lognormal(0, 0.05)
    oth = mon_vis[p] * (0.95 + 0.1 * (x.weekday() >= 5)) * r.lognormal(0, 0.05)
    hkr = 310000 * (1.25 if x.weekday() >= 4 else 0.95) * r.lognormal(0, 0.04)
    if x == d("2026-09-17"):
        cnv, oth, hkr = cnv * 0.22, oth * 0.4, hkr * 0.25
    if x == d("2026-09-18"):
        cnv, oth, hkr = cnv * 0.65, oth * 0.75, hkr * 0.7
    if x == d("2026-09-16"):
        cnv, oth = cnv * 0.85, oth * 0.9
    if x == d("2025-03-14"):
        continue  # missing day in the published series
    a = [int(hkr * 0.5), int(cnv), int(oth)]
    dd = [int(hkr * 0.5 * r.lognormal(0, 0.03)), int(cnv * r.lognormal(0, 0.03)), int(oth * r.lognormal(0, 0.03))]
    ds = x.strftime("%d-%m-%Y")
    rows.append(f"{ds},All control points,Arrival,{a[0]},{a[1]},{a[2]},{sum(a)}")
    rows.append(f"{ds},All control points,Departure,{dd[0]},{dd[1]},{dd[2]},{sum(dd)}")
mkdir(T / "hk_immigration")
(T / "hk_immigration" / "statistics_on_daily_passenger_traffic.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

# ---------------------------------------------------------------------------------------------- CN Golden Week border stats
r = rng_for("nia")
rows = ["年份,日期,出入境人次(万),其中内地居民(万),港澳台居民(万),外国人(万),备注"]
for y, base, days in ((2024, 180, drange("2024-10-01", "2024-10-07")), (2025, 215, drange("2025-10-01", "2025-10-08")), (2026, 236, drange("2026-10-01", "2026-10-07"))):
    for i, x in enumerate(days):
        prof = [1.05, 1.12, 1.08, 1.0, 0.96, 0.95, 1.02, 1.0][i]
        tot = base * prof * r.lognormal(0, 0.02)
        mn = tot * 0.47
        hk = tot * 0.38
        fo = tot - mn - hk
        rows.append(f"{y},{x.month}月{x.day}日,{tot:.1f},{mn:.1f},{hk:.1f},{fo:.1f},{'国庆中秋假期' if y == 2025 else '国庆假期'}")
mkdir(T / "cn_border")
(T / "cn_border" / "国庆假期_全国边检_日均出入境.csv").write_text("﻿" + "\n".join(rows) + "\n", encoding="utf-8")

# ---------------------------------------------------------------------------------------------- weekly air seat capacity
ROUTES = [  # origin, dest, base flights/week, seats/flight, start, notes
    ("ICN", "CDG", 14, 305, None), ("ICN", "MXP", 5, 290, None), ("ICN", "FCO", 7, 300, None), ("ICN", "LHR", 10, 320, None),
    ("ICN", "ZRH", 3, 275, None), ("PVG", "MXP", 7, 300, None), ("PEK", "MXP", 4, 290, None), ("TFU", "MXP", 0, 300, "2026-06-29"),
    ("PVG", "CDG", 14, 310, None), ("PEK", "CDG", 10, 300, None), ("CAN", "CDG", 7, 300, None), ("PVG", "LHR", 10, 320, None),
    ("PEK", "LHR", 7, 310, None), ("PVG", "ZRH", 3, 270, "2025-03-30"), ("HKG", "MXP", 4, 300, None), ("HKG", "CDG", 10, 320, None),
    ("HKG", "LHR", 28, 340, None), ("HND", "CDG", 14, 260, None), ("NRT", "CDG", 7, 270, None), ("HND", "LHR", 21, 270, None),
    ("HND", "FCO", 7, 290, None), ("NRT", "MXP", 3, 280, "2025-04-01"), ("PVG", "NRT", 49, 230, None), ("PVG", "HND", 28, 250, None),
    ("PEK", "HND", 21, 250, None), ("ICN", "NRT", 84, 210, None), ("ICN", "HND", 56, 230, None), ("ICN", "KIX", 90, 190, None),
    ("TPE", "NRT", 70, 250, None), ("HKG", "NRT", 49, 280, None), ("PVG", "ICN", 63, 220, None), ("HKG", "PVG", 70, 260, None),
    ("SIN", "PVG", 28, 290, None), ("ICN", "SIN", 21, 280, None), ("JFK", "LHR", 126, 280, None), ("JFK", "CDG", 49, 290, None),
    ("JFK", "MXP", 21, 290, None), ("DXB", "LHR", 70, 480, None), ("DXB", "MXP", 14, 400, None), ("ICN", "JFK", 21, 330, None),
    ("PVG", "HKG", 70, 260, None), ("HND", "ICN", 56, 230, None)]
GROW = {"ICN": 0.10, "PVG": 0.14, "PEK": 0.12, "TFU": 0.0, "CAN": 0.10, "HKG": 0.06, "HND": 0.04, "NRT": 0.0, "TPE": 0.05, "SIN": 0.05, "JFK": 0.02, "DXB": 0.05}
r = rng_for("seats")
weeks = pd.date_range("2024-09-02", "2026-12-28", freq="W-MON")
rows = []
for o, dst, f0, spf, start in ROUTES:
    hist = {}
    for w in weeks:
        wd = w.date()
        if start and wd < d(start):
            continue
        yrs = (wd - d("2024-09-02")).days / 365
        f = f0 * (1 + GROW[o]) ** yrs
        if o == "TFU":
            f = 3 if wd < d("2026-09-28") else 4
        if dst in ("CDG", "MXP", "FCO", "LHR", "ZRH") and wd.month in (6, 7, 8):
            f *= 1.12
        if dst in ("CDG", "MXP", "FCO", "LHR", "ZRH") and wd.month in (1, 2) and o not in ("PVG", "PEK", "CAN", "HKG"):
            f *= 0.88
        if o == "ICN" and dst == "ZRH" and wd.month in (11, 12, 1, 2, 3):
            f = 0
        if o in ("PVG", "PEK", "CAN", "TFU", "HKG") and (d("2025-09-29") <= wd <= d("2025-10-06") or d("2026-09-28") <= wd <= d("2026-10-05")):
            f *= 1.15 if o != "TFU" else 1.0  # Golden Week extra sections
        if o == "ICN" and dst in ("CDG", "MXP", "FCO") and (d("2026-09-21") <= wd <= d("2026-10-05") or d("2025-09-29") <= wd <= d("2025-10-06")):
            f += 3  # Chuseok extra sections
        if o == "ICN" and dst == "CDG" and wd >= d("2026-03-30"):
            f += 3  # additional carrier from summer 2026
        flights = int(round(f + r.normal(0, 0.25)))
        if f == 0:
            flights = 0
        seats = int(flights * spf * r.uniform(0.97, 1.03))
        ly = hist.get((wd - TD(weeks=52)).isoformat())
        yoy = "" if not ly else f"{(seats / ly - 1) * 100:.1f}"
        hist[wd.isoformat()] = seats if seats else None
        status = "operated" if wd <= d("2026-10-12") else "filed"
        rows.append([wd.isoformat(), o, dst, flights, seats, yoy, status])
air = pd.DataFrame(rows, columns=["week_start", "origin", "destination", "flights", "seats", "seats_yoy_pct", "status"])
air = air[air.flights > 0]
# extract quirk: filed schedule beyond Jan 2026 for PEK-MXP shows a pending cancellation
air.loc[(air.origin == "PEK") & (air.destination == "MXP") & (air.week_start >= "2026-11-30"), "status"] = "filed (subject to change)"
mkdir(T / "air_capacity")
air.to_csv(T / "air_capacity" / "skeddata_weekly_seats_by_route_extract_20261020.csv", index=False)
(T / "air_capacity" / "README.txt").write_text(
    "Weekly scheduled capacity by airport pair (one direction only: origin -> destination), all marketing carriers combined, codeshares removed.\n"
    "week_start = Monday. status 'operated' up to the last completed week; 'filed' = future schedules as filed with the provider (subject to change).\n"
    "Airport codes are IATA (TFU = Chengdu Tianfu, PVG = Shanghai Pudong, PEK = Beijing Capital, HND/NRT = Tokyo, ICN = Seoul Incheon, KIX = Osaka).\n",
    encoding="utf-8")

# ---------------------------------------------------------------------------------------------- weekly hotel KPIs (Sun-Sat, week ending Saturday)
HOTEL = {  # city key: base occ %, adr local, currency, seasonality key
    "MILANO": (74, 260, "EUR", "IT-MI"), "ROMA": (76, 240, "EUR", "IT-RM"), "VENEZIA": (72, 330, "EUR", "IT-VE"), "COURMAYEUR": (52, 280, "EUR", "SKI"),
    "CORTINA": (50, 330, "EUR", "SKI"), "PARIS": (79, 310, "EUR", "FR-PA"), "CANNES": (64, 290, "EUR", "FR-CA"), "GENEVE": (70, 330, "CHF", "CITY"),
    "LONDON": (82, 230, "GBP", "CITY"), "MUENCHEN": (72, 165, "EUR", "CITY"), "BERLIN": (71, 125, "EUR", "CITY"), "ZUERICH": (75, 280, "CHF", "CITY"),
    "STMORITZ": (55, 520, "CHF", "SKI"), "MADRID": (75, 165, "EUR", "CITY"), "AMSTERDAM": (81, 230, "EUR", "CITY"), "KOBENHAVN": (76, 1550, "DKK", "CITY"),
    "DUBAI": (78, 780, "AED", "AE-DU"), "NEWYORK": (85, 330, "USD", "CITY"), "MIAMI": (73, 260, "USD", "AE-DU"), "BEVERLYHILLS": (78, 290, "USD", "SUN"),
    "ASPEN": (55, 650, "USD", "SKI"), "TORONTO": (72, 270, "CAD", "CITY"), "TOKYO": (82, 26500, "JPY", "CITY"), "OSAKA": (80, 18500, "JPY", "CITY"),
    "SEOUL": (76, 235000, "KRW", "CITY"), "BUSAN": (70, 165000, "KRW", "CITY"), "SHANGHAI": (70, 980, "CNY", "CITY"), "BEIJING": (68, 880, "CNY", "CITY"),
    "CHENGDU": (66, 620, "CNY", "CITY"), "HONGKONG": (84, 1450, "HKD", "SUN"), "TAIPEI": (73, 4500, "TWD", "SUN"), "SINGAPORE": (83, 340, "SGD", "SUN"),
    "SYDNEY": (82, 290, "AUD", "AU")}
BUMPS = [  # city, start, end, occ points, adr pct
    ("MILANO", "2024-09-17", "2024-09-23", 12, 45), ("MILANO", "2025-09-23", "2025-09-29", 12, 48), ("MILANO", "2026-09-22", "2026-09-28", 13, 52),
    ("MILANO", "2025-02-25", "2025-03-03", 9, 30), ("MILANO", "2026-02-24", "2026-03-02", 9, 32), ("MILANO", "2025-04-08", "2025-04-13", 16, 90),
    ("MILANO", "2026-04-21", "2026-04-26", 16, 92), ("MILANO", "2026-02-06", "2026-02-22", 14, 70), ("CORTINA", "2026-02-06", "2026-02-22", 35, 140),
    ("MILANO", "2025-11-04", "2025-11-09", 9, 25), ("MILANO", "2024-11-05", "2024-11-10", 9, 25), ("ROMA", "2025-01-01", "2025-12-31", 4, 12),
    ("PARIS", "2024-09-23", "2024-10-01", 9, 35), ("PARIS", "2025-09-29", "2025-10-07", 10, 38), ("PARIS", "2026-09-29", "2026-10-07", 11, 42),
    ("PARIS", "2025-10-22", "2025-10-26", 5, 18), ("PARIS", "2026-10-13", "2026-10-18", 4, 8), ("MUENCHEN", "2024-09-21", "2024-10-06", 18, 110),
    ("MUENCHEN", "2025-09-20", "2025-10-05", 18, 115), ("MUENCHEN", "2026-09-19", "2026-10-04", 18, 118), ("LONDON", "2026-10-14", "2026-10-18", 4, 12),
    ("LONDON", "2025-10-15", "2025-10-19", 4, 12), ("AMSTERDAM", "2026-10-14", "2026-10-18", 9, 38), ("AMSTERDAM", "2025-10-22", "2025-10-26", 9, 36),
    ("NEWYORK", "2025-09-22", "2025-09-27", 7, 40), ("NEWYORK", "2026-09-21", "2026-09-26", 7, 42), ("NEWYORK", "2026-06-13", "2026-07-19", 5, 25),
    ("TORONTO", "2025-09-04", "2025-09-14", 9, 30), ("TORONTO", "2026-09-10", "2026-09-20", 10, 32), ("BUSAN", "2025-09-17", "2025-09-26", 10, 25),
    ("BUSAN", "2026-10-01", "2026-10-10", 11, 28), ("SINGAPORE", "2024-09-20", "2024-09-22", 9, 85), ("SINGAPORE", "2025-10-03", "2025-10-05", 9, 90),
    ("SINGAPORE", "2026-10-09", "2026-10-11", 10, 95), ("DUBAI", "2026-10-12", "2026-10-16", 6, 25), ("DUBAI", "2025-11-17", "2025-11-21", 6, 30),
    ("OSAKA", "2025-04-13", "2025-10-13", 8, 30), ("CHENGDU", "2025-08-07", "2025-08-17", 12, 40), ("SHANGHAI", "2026-10-01", "2026-10-07", 12, 35),
    ("BEIJING", "2026-10-01", "2026-10-07", 14, 40), ("CHENGDU", "2026-10-01", "2026-10-07", 16, 45), ("SHANGHAI", "2025-10-01", "2025-10-08", 11, 30),
    ("BEIJING", "2025-10-01", "2025-10-08", 13, 35), ("CHENGDU", "2025-10-01", "2025-10-08", 14, 40), ("HONGKONG", "2026-10-01", "2026-10-07", 9, 22),
    ("HONGKONG", "2025-10-01", "2025-10-07", 8, 18), ("TOKYO", "2026-09-30", "2026-10-08", 5, 12), ("SEOUL", "2026-09-30", "2026-10-08", 5, 10),
    ("MILANO", "2026-09-30", "2026-10-08", 4, 10), ("PARIS", "2026-09-30", "2026-10-08", 2, 5), ("HONGKONG", "2026-09-16", "2026-09-18", -30, -10),
    ("VENEZIA", "2026-10-20", "2026-10-20", -6, 0), ("VENEZIA", "2026-09-02", "2026-09-12", 6, 30), ("ZUERICH", "2026-09-24", "2026-10-04", 3, 8),
    ("BEVERLYHILLS", "2026-09-08", "2026-09-12", -4, -3), ("SYDNEY", "2026-08-30", "2026-08-30", 6, 20), ("GENEVE", "2026-04-14", "2026-04-20", 14, 60),
    ("LONDON", "2026-06-29", "2026-07-12", 5, 20), ("MIAMI", "2025-12-05", "2025-12-07", 14, 120), ("MIAMI", "2024-12-06", "2024-12-08", 14, 115),
    ("ASPEN", "2025-12-20", "2026-01-04", 30, 120), ("ASPEN", "2024-12-20", "2025-01-04", 30, 115), ("STMORITZ", "2025-12-20", "2026-01-04", 35, 130),
    ("STMORITZ", "2024-12-20", "2025-01-04", 35, 125), ("CANNES", "2026-05-12", "2026-05-23", 22, 160), ("CANNES", "2025-05-13", "2025-05-24", 22, 155),
]
CLOSED_WEEKS = {"STMORITZ": [("2025-04-14", "2025-06-19"), ("2025-10-20", "2025-12-04"), ("2026-04-13", "2026-06-18"), ("2026-10-19", "2026-12-03"), ("2024-10-21", "2024-12-05")],
                "COURMAYEUR": [("2025-04-21", "2025-06-26"), ("2025-09-14", "2025-11-27"), ("2026-04-13", "2026-06-25"), ("2026-09-13", "2026-11-26"), ("2024-09-15", "2024-11-28")]}
FXA = {"AED": 3.6725}
r = rng_for("hotels")
days = drange("2024-09-01", "2026-10-17")
rows = []
for ck, (occ0, adr0, ccy, sk) in HOTEL.items():
    c = CITIES[ck]
    daily = []
    for x in days:
        s = DEST_SEAS[sk][x.month - 1]
        occ = occ0 * (0.82 + 0.18 * s) if sk != "SKI" else occ0 * (0.25 + 0.55 * s)
        wkd = [0.93, 0.98, 1.02, 1.03, 1.03, 1.06, 0.95][x.weekday()]
        occ *= wkd
        adr = adr0 * (0.85 + 0.15 * s) if sk != "SKI" else adr0 * (0.6 + 0.35 * s)
        for bc, a, b, op, ap in BUMPS:
            if bc == ck and d(a) <= x <= d(b):
                occ += op
                adr *= 1 + ap / 100
        occ = min(98.5, max(8, occ + r.normal(0, 2.2)))
        adr *= (1.035 ** ((x - d("2025-09-01")).days / 365)) * r.lognormal(0, 0.02)
        daily.append((x, occ, adr))
    dfh = pd.DataFrame(daily, columns=["date", "occ", "adr"])
    dfh["we"] = [x + TD(days=(5 - x.weekday()) % 7) for x in dfh.date]
    g = dfh.groupby("we").agg(occ=("occ", "mean"), adr=("adr", "mean"), n=("occ", "size"))
    g = g[g.n == 7]
    prev = {}
    for we, rr in g.iterrows():
        closed = any(d(a) <= we <= d(b) for a, b in CLOSED_WEEKS.get(ck, []))
        cur = ccy
        adr = rr.adr
        if ck == "DUBAI" and we >= d("2026-03-07"):
            cur, adr = "USD", adr / FXA["AED"]
        ly = prev.get(we - TD(weeks=52))
        sample = int(r.integers(25, 140)) if ck not in ("STMORITZ", "COURMAYEUR", "CORTINA", "ASPEN") else int(r.integers(6, 18))
        if closed:
            rows.append([we.isoformat(), c["name"], ck[:3] + "-MKT", "", "", cur, "", "", "", 3, "insufficient sample (seasonal closures)"])
            continue
        occ_yoy = "" if not ly else f"{rr.occ - ly[0]:.1f}"
        adr_yoy = "" if not ly or ly[2] != cur else f"{(adr / ly[1] - 1) * 100:.1f}"
        prev[we] = (rr.occ, adr, cur)
        rows.append([we.isoformat(), c["name"], ck[:3] + "-MKT", f"{rr.occ:.1f}", f"{adr:.0f}" if cur in ("JPY", "KRW", "TWD", "DKK") else f"{adr:.2f}",
                     cur, f"{rr.occ / 100 * adr:.2f}", occ_yoy, adr_yoy, sample, ""])
hot = pd.DataFrame(rows, columns=["week_ending", "market", "market_code", "occupancy_pct", "adr", "currency", "revpar", "occ_chg_yoy_pts", "adr_chg_yoy_pct",
                                  "hotels_in_sample", "comment"])
# restated week: Paris week ending 2026-10-10 appears twice (original + restated)
dup = hot[(hot.market == "Paris") & (hot.week_ending == "2026-10-10")].copy()
dup["occupancy_pct"] = (dup.occupancy_pct.astype(float) + 1.4).map(lambda v: f"{v:.1f}")
dup["comment"] = "restated 2026-10-21"
hot = pd.concat([hot, dup]).sort_values(["market", "week_ending"])
mkdir(T / "hotels")
hot.to_csv(T / "hotels" / "hotelbench_weekly_market_kpis.csv", index=False)
(T / "hotels" / "README.txt").write_text(
    "HotelBench weekly market performance (sample of participating hotels, upscale+luxury class). Week = Sunday-Saturday, labelled by week ending (Saturday).\n"
    "ADR and RevPAR in local currency unless stated in 'currency'. YoY vs same week last year (52 weeks back). Data published Wednesday after week end.\n"
    "Venezia market includes Mestre/Lido. Resort markets have small samples.\n", encoding="utf-8")

# ---------------------------------------------------------------------------------------------- weekly tax-free spend (raw refund operator feed)
DESTS = ["IT", "FR", "DE", "CH", "ES", "NL", "DK", "JP", "KR", "SG", "AE"]
NATS = ["CN", "US", "KR", "JP", "TW", "HK", "SG", "TH", "ID", "IN", "GCC", "GB", "TR", "BR", "MX", "AU"]
ELIG = {"JP": {"JP"}, "KR": {"KR"}, "SG": {"SG"}, "AE": {"GCC"}}  # residents not eligible at home
BASE_SHARE = {  # rough relative weekly spend (EUR k) in a normal week
    "IT": {"CN": 900, "US": 1300, "KR": 260, "JP": 200, "TW": 120, "HK": 140, "SG": 90, "TH": 80, "ID": 60, "IN": 110, "GCC": 520, "GB": 380, "TR": 140, "BR": 160, "MX": 120, "AU": 110},
    "FR": {"CN": 1400, "US": 1600, "KR": 380, "JP": 360, "TW": 160, "HK": 220, "SG": 120, "TH": 110, "ID": 70, "IN": 120, "GCC": 900, "GB": 420, "TR": 110, "BR": 180, "MX": 110, "AU": 120},
    "DE": {"CN": 380, "US": 420, "KR": 90, "JP": 70, "TW": 40, "HK": 50, "SG": 30, "TH": 40, "ID": 20, "IN": 60, "GCC": 380, "GB": 120, "TR": 160, "BR": 40, "MX": 30, "AU": 40},
    "CH": {"CN": 520, "US": 380, "KR": 80, "JP": 90, "TW": 50, "HK": 70, "SG": 60, "TH": 50, "ID": 30, "IN": 160, "GCC": 520, "GB": 160, "TR": 40, "BR": 40, "MX": 30, "AU": 50},
    "ES": {"CN": 260, "US": 520, "KR": 90, "JP": 60, "TW": 30, "HK": 30, "SG": 20, "TH": 20, "ID": 10, "IN": 30, "GCC": 160, "GB": 210, "TR": 30, "BR": 90, "MX": 260, "AU": 50},
    "NL": {"CN": 160, "US": 260, "KR": 40, "JP": 40, "TW": 20, "HK": 20, "SG": 20, "TH": 10, "ID": 30, "IN": 40, "GCC": 60, "GB": 110, "TR": 30, "BR": 20, "MX": 10, "AU": 30},
    "DK": {"CN": 60, "US": 110, "KR": 20, "JP": 25, "TW": 10, "HK": 10, "SG": 10, "TH": 10, "ID": 5, "IN": 15, "GCC": 20, "GB": 60, "TR": 10, "BR": 10, "MX": 5, "AU": 15},
    "JP": {"CN": 2600, "US": 600, "KR": 900, "TW": 1100, "HK": 800, "SG": 300, "TH": 380, "ID": 120, "IN": 60, "GCC": 80, "GB": 140, "TR": 10, "BR": 20, "MX": 30, "AU": 260},
    "KR": {"CN": 1500, "US": 200, "JP": 450, "TW": 260, "HK": 150, "SG": 110, "TH": 120, "ID": 60, "IN": 20, "GCC": 40, "GB": 30, "TR": 5, "BR": 5, "MX": 5, "AU": 40},
    "SG": {"CN": 500, "US": 140, "KR": 90, "JP": 80, "TW": 40, "HK": 60, "TH": 50, "ID": 260, "IN": 180, "GCC": 40, "GB": 60, "TR": 5, "BR": 5, "MX": 5, "AU": 130},
    "AE": {"CN": 280, "US": 160, "KR": 40, "JP": 30, "TW": 10, "HK": 20, "SG": 30, "TH": 20, "ID": 30, "IN": 520, "GB": 220, "TR": 60, "BR": 20, "MX": 10, "AU": 50},
}
TICKET = {"CN": 1350, "US": 980, "KR": 1150, "JP": 900, "TW": 900, "HK": 1250, "SG": 950, "TH": 800, "ID": 850, "IN": 700, "GCC": 1900, "GB": 650, "TR": 600,
          "BR": 820, "MX": 760, "AU": 780}
r = rng_for("taxfree")
wks = pd.date_range("2024-09-02", "2026-10-19", freq="W-MON")


def week_mult(dest, nat, w):
    m = 1.0
    wd = w.date()
    mo = wd.month
    g = NATGRP.get(nat, "EU")
    m *= SEAS.get(g, SEAS["EU"])[mo - 1] ** 0.8
    if dest in ("IT", "FR", "DE", "CH", "ES", "NL", "DK"):
        m *= [0.8, 0.75, 0.9, 1.0, 1.05, 1.15, 1.2, 1.1, 1.05, 1.0, 1.05, 1.35][mo - 1]
    if mo == 12 and wd.day >= 1:
        m *= 1.15
    # Golden week weeks (Mon containing Oct 1..8)
    for y, wk_list, strength in ((2024, ["2024-09-30", "2024-10-07"], 1.45), (2025, ["2025-09-29", "2025-10-06"], 1.5), (2026, ["2026-09-28", "2026-10-05"], 1.5)):
        if nat == "CN" and w.strftime("%Y-%m-%d") in wk_list:
            k = strength
            if y == 2026 and dest in ("IT", "FR"):
                k *= 1.32  # stronger than 2025 in Milan/Paris
            if y == 2026 and dest == "CH":
                k *= 1.1
            m *= k
    # CNY
    for c in ("2025-01-27", "2025-02-03", "2026-02-16", "2026-02-23"):
        if nat in ("CN", "TW", "HK", "SG") and w.strftime("%Y-%m-%d") == c:
            m *= 1.35
    # Koreans in FR/IT after Chuseok 2026 (+ black Aurea hunt)
    if nat == "KR" and dest in ("FR", "IT") and d("2026-09-14") <= wd <= d("2026-10-12"):
        m *= 1.45 if dest == "FR" else 1.3
    if nat == "KR" and dest in ("FR", "IT") and d("2025-09-29") <= wd <= d("2025-10-13"):
        m *= 1.2
    # GCC summer & Eid
    if nat == "GCC" and dest in ("FR", "IT", "CH", "DE", "ES") and mo in (7, 8):
        m *= 1.5
    # Japan: weak yen boom + warm early Oct (fewer outerwear purchases) + pre-price-increase week
    if dest == "JP":
        m *= 1.06 ** ((wd - d("2025-01-01")).days / 365)
        if d("2026-09-28") <= wd <= d("2026-10-05"):
            m *= 0.9
        if wd == d("2026-10-12"):
            m *= 1.18
    # cold snap: DACH/Nordics/NL week of Oct 12 2026
    if dest in ("DE", "CH", "DK", "NL") and wd == d("2026-10-12"):
        m *= 1.16
    # Double 11 presales: Chinese spending abroad slightly softer in partial week
    return m


rows = []
for dest in DESTS:
    for nat in NATS:
        if nat in ELIG.get(dest, set()) or nat not in BASE_SHARE[dest]:
            continue
        base = BASE_SHARE[dest][nat]
        hist = {}
        vals = []
        for w in wks:
            m = week_mult(dest, nat, w)
            growth = {"CN": 1.12, "KR": 1.06, "GCC": 1.05, "US": 1.0, "JP": 0.97}.get(nat, 1.03) ** ((w - pd.Timestamp("2025-01-01")).days / 365)
            spend = base * m * growth * r.lognormal(0, 0.07)
            trx = spend * 1000 / TICKET[nat] * r.lognormal(0, 0.04)
            vals.append((w, spend, trx))
        df = pd.DataFrame(vals, columns=["w", "spend", "trx"])
        ref = df[(df.w >= "2025-01-01") & (df.w <= "2025-12-31")]
        for row in df.itertuples():
            wd = row.w.date()
            iso = wd.isocalendar()
            partial = wd == d("2026-10-19")
            sp = row.spend * (3 / 7 * 0.92 if partial else 1)
            tx = row.trx * (3 / 7 * 0.92 if partial else 1)
            status = "PARTIAL_WTD" if partial else ("PRELIM" if wd >= d("2026-10-05") else "FINAL")
            ly = hist.get((iso[0] - 1, iso[1]))
            hist[(iso[0], iso[1])] = sp
            rows.append(dict(yr_wk=f"{iso[0]}{iso[1]:02d}", wk_start=wd.isoformat(), dest_ctry=dest, nat_grp=nat,
                             spend_idx=round(sp / ref.spend.mean() * 100, 1), trx_idx=round(tx / ref.trx.mean() * 100, 1),
                             avg_tkt_eur=round(sp * 1000 / tx, 0) if tx else None,
                             yoy_spend=round((sp / ly - 1) * 100, 1) if ly and not partial else None,
                             share_dest_spend=None, status=status, rev=0))
tf = pd.DataFrame(rows)
tot = tf.groupby(["yr_wk", "dest_ctry"]).spend_idx.transform("sum")  # placeholder, real share computed from raw spend below
# share of destination spend (from raw EUR spend reconstructed)
raw = []
for rrow in tf.itertuples():
    base = BASE_SHARE[rrow.dest_ctry][rrow.nat_grp]
    raw.append(rrow.spend_idx * base)
tf["_raw"] = raw
tf["share_dest_spend"] = (tf._raw / tf.groupby(["yr_wk", "dest_ctry"])._raw.transform("sum") * 100).round(2)
tf = tf.drop(columns="_raw")
# revisions: PRELIM rows for wk 202641 re-sent with rev=1 and slightly different values
rev = tf[tf.yr_wk == "202641"].copy()
rev["spend_idx"] = (rev.spend_idx * rng_for("rev").uniform(0.97, 1.05, len(rev))).round(1)
rev["rev"] = 1
tf = pd.concat([tf, rev]).sort_values(["dest_ctry", "nat_grp", "yr_wk", "rev"])
mkdir(T / "tax_free")
tf.to_csv(T / "tax_free" / "refundia_weekly_spend_feed_raw.csv", index=False, sep="|")
(T / "tax_free" / "FEED_SPEC.txt").write_text(
    "Refundia data feed - weekly tax-free shopping (issued refund cheques, all categories)\n"
    "delimiter: |   week: ISO week Mon-Sun (yr_wk = ISO year + week)\n"
    "spend_idx / trx_idx: index, base = average week of calendar 2025 = 100, computed separately for each dest_ctry x nat_grp pair\n"
    "avg_tkt_eur: average refund-cheque purchase value in EUR (gross of VAT)\n"
    "yoy_spend: % vs same ISO week previous year\n"
    "share_dest_spend: % of total tax-free spend in dest_ctry in that week (covered nationalities only)\n"
    "status: FINAL / PRELIM (may be revised, see rev) / PARTIAL_WTD (week-to-date, incomplete)\n"
    "nat_grp GCC = SA+AE+KW+QA+BH+OM. UK is not covered (no VAT refund scheme). Residents are not eligible in their own country.\n",
    encoding="utf-8")
print("tourism done", len(air), len(hot), len(tf))
