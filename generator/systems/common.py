"""Shared helpers + cross-system facts for the `systems` sources (warehouse, logistics, marketing,
planning, ecommerce, customer_care, agents).

Every generator in generator/systems/ imports this module so that IDs, PO numbers, ETAs and quantities
agree across systems. Run scripts with `.venv/bin/python generator/systems/<script>.py` from repo root.
"""
from __future__ import annotations

import datetime as dt
import glob
import json
import os
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / "generator"
sys.path.insert(0, str(GEN))
import config  # noqa: E402
import events  # noqa: E402

INTERNAL = ROOT / "generated" / "sources" / "erp"
OUT = ROOT / "generated" / "sources" / "systems"
GT = ROOT / "generated" / "ground_truth"
CACHE = GEN / "systems" / "_cache"
NOTES = GEN / "systems" / "notes"   # per-area notes, merged into ground_truth/answer_keys/systems_notes.md
for p in (OUT, CACHE, NOTES):
    p.mkdir(parents=True, exist_ok=True)

TODAY = dt.date(2026, 10, 22)
LAST_DAY = dt.date(2026, 10, 21)
WIN_START = dt.date(2026, 8, 1)


def rng(seed_name: str) -> np.random.Generator:
    """Deterministic RNG per generator/area."""
    import zlib
    seed = zlib.crc32(seed_name.encode())
    return np.random.default_rng(seed)


def stable_hash(obj) -> int:
    import zlib
    return zlib.crc32(repr(obj).encode("utf-8"))


def d(s) -> dt.date:
    return s if isinstance(s, dt.date) else dt.date.fromisoformat(str(s)[:10])


def daterange(a, b):
    a, b = d(a), d(b)
    for i in range((b - a).days + 1):
        yield a + dt.timedelta(days=i)


# ----------------------------------------------------------------------------- master data
@lru_cache
def stores() -> pd.DataFrame:
    return pd.read_csv(INTERNAL / "master_data" / "stores.csv")


@lru_cache
def skus() -> pd.DataFrame:
    return pd.read_csv(INTERNAL / "master_data" / "sku_colour.csv", dtype={"color_code": str})


@lru_cache
def sku_sizes() -> pd.DataFrame:
    return pd.read_csv(INTERNAL / "master_data" / "sku_size_ean.csv", dtype={"size": str, "ean": str})


@lru_cache
def assortment() -> pd.DataFrame:
    return pd.read_csv(INTERNAL / "master_data" / "store_assortment.csv")


@lru_cache
def shipments() -> list[dict]:
    with open(INTERNAL / "logistics" / "shipments_dc_to_store.jsonl") as f:
        return [json.loads(l) for l in f]


@lru_cache
def pos_lines() -> pd.DataFrame:
    fs = sorted(glob.glob(str(INTERNAL / "sales" / "pos_lines" / "*.csv")))
    return pd.concat([pd.read_csv(f, dtype={"size": str, "customer_id": str}) for f in fs], ignore_index=True)


def store_stock(day) -> pd.DataFrame:
    return pd.read_csv(INTERNAL / "inventory" / "store_stock_daily" / f"stock_eod_{d(day).isoformat()}.csv",
                       dtype={"size": str})


@lru_cache
def lost_sales() -> pd.DataFrame:
    """Hidden truth (unmet demand by store/sku/size/day) - use ONLY to make sources consistent, never copy it."""
    return pd.read_csv(GT / "demand" / "lost_sales_daily.csv", dtype={"size": str})


STYLE_BY_CODE = {s[0]: s for s in config.STYLES}
STYLE_CODE = {s[1]: s[0] for s in config.STYLES}          # name -> code
STYLE_NAME = {s[0]: s[1] for s in config.STYLES}          # code -> name


def sku_of(style_name: str, color: str) -> str:
    return f"{STYLE_CODE[style_name]}-{color}"


def color_name(code: str, lang: str = "en") -> str:
    idx = {"it": 0, "en": 1, "fr": 2, "de": 3, "es": 4, "ja": 5, "ko": 6, "zh": 7}[lang]
    return config.COLORS[code][idx]


# ----------------------------------------------------------------------------- DCs
DCS = {
    "DC-IT-CSG": dict(werks="IT10", name="DC Castel San Giovanni (PC)", tz="Europe/Rome", region="EMEA",
                      operator="in-house (SAP EWM)", wms="SAP EWM 9.5", city="Castel San Giovanni", cc="IT"),
    "DC-US-NJ": dict(werks="US20", name="DC Secaucus NJ", tz="America/New_York", region="AMERICAS",
                     operator="in-house (SAP EWM)", wms="SAP EWM 9.5", city="Secaucus", cc="US"),
    "DC-HK-TKO": dict(werks="HK30", name="DC Tseung Kwan O (3PL)", tz="Asia/Hong_Kong", region="APAC",
                      operator="3PL - Pacific Crest Logistics", wms="PCL iWMS (3PL portal)", city="Tseung Kwan O", cc="HK",
                      site_3pl="TKO-3"),
}
REGION_DC = {"EMEA": "DC-IT-CSG", "AMERICAS": "DC-US-NJ", "APAC": "DC-HK-TKO"}

# ----------------------------------------------------------------------------- store ID crosswalk
# SAP plant (WERKS) used by ERP/WMS/planning; CRM (Salesforce) store code; TMS ship-to (SAP KUNNR)
_SAP_PREFIX = {"IT": 10, "FR": 11, "CH": 12, "GB": 13, "DE": 14, "ES": 15, "NL": 16, "DK": 17, "AE": 18, "US": 20,
               "CA": 21, "JP": 30, "KR": 31, "CN": 32, "HK": 33, "TW": 34, "SG": 35, "AU": 36}
# CRM codes follow CRM go-live order per country, NOT the internal order (trap for naive mapping)
_CRM_ORDER = {
    "IT": ["MIL01", "ROM01", "MIL02", "VEN01", "CRT01", "COU01"],
    "FR": ["PAR01", "CAN01", "PAR02"], "CH": ["GVA01", "ZRH01", "STM01"], "GB": ["LON01", "LON02"],
    "DE": ["MUN01", "BER01"], "ES": ["MAD01"], "NL": ["AMS01"], "DK": ["CPH01"], "AE": ["DXB01"],
    "US": ["NYC01", "BHS01", "NYC02", "MIA01", "ASP01"], "CA": ["TOR01"], "JP": ["TYO01", "OSA01", "TYO02"],
    "KR": ["SEL02", "SEL01", "BUS01"], "CN": ["SHA01", "BJS01", "CDU01"], "HK": ["HKG01"], "TW": ["TPE01"],
    "SG": ["SIN01"], "AU": ["SYD01"],
}
SAP_WERKS, CRM_CODE, TMS_SHIPTO = {}, {}, {}
for _cc, _lst in _CRM_ORDER.items():
    for _i, _sid in enumerate(_lst, 1):
        CRM_CODE[_sid] = f"{_cc}{_i:02d}"
_seq = {}
_st = pd.read_csv(INTERNAL / "master_data" / "stores.csv")
for _sid, _cc in zip(_st.store_id, _st.country_code):
    _seq[_cc] = _seq.get(_cc, 0) + 1
    SAP_WERKS[_sid] = f"{_SAP_PREFIX[_cc]}{_seq[_cc]:02d}"
    TMS_SHIPTO[_sid] = f"00000{70000 + int(SAP_WERKS[_sid])}"   # e.g. 0000071001
WERKS_TO_STORE = {v: k for k, v in SAP_WERKS.items()}
CRM_TO_STORE = {v: k for k, v in CRM_CODE.items()}

# colloquial / system names for stores (used in free text, planning sheets, CRM)
STORE_ALIASES = {
    "MIL01": ["Monte Napo", "Montenapoleone", "MI-MN", "Milano Flagship"], "MIL02": ["Rinascente", "MI-RIN", "Rina Duomo"],
    "ROM01": ["Condotti", "RM-CON", "Roma"], "VEN01": ["San Marco", "VE-SM"], "COU01": ["Courma", "Courmayeur"],
    "CRT01": ["Cortina"], "PAR01": ["Saint-Honoré", "St Honoré", "PA-SH", "Paris Flagship"], "PAR02": ["Galeries Lafayette", "GL Haussmann", "PA-GL"],
    "CAN01": ["Cannes", "Croisette"], "GVA01": ["Genève", "Geneva", "Rue du Rhône"], "LON01": ["New Bond St", "Bond Street", "LDN-NBS"],
    "LON02": ["Harrods", "LDN-HAR"], "MUN01": ["München", "Munich", "Maximilianstrasse"], "BER01": ["KaDeWe", "Berlin"],
    "ZRH01": ["Zürich", "Zurich", "Bahnhofstrasse"], "STM01": ["St. Moritz", "St Moritz"], "MAD01": ["Serrano", "Madrid"],
    "AMS01": ["PC Hooft", "Amsterdam"], "CPH01": ["Copenhagen", "Østergade"], "DXB01": ["Dubai Mall", "DXB"],
    "NYC01": ["Madison", "Madison Ave"], "NYC02": ["SoHo", "Soho"], "MIA01": ["Design District", "Miami"],
    "BHS01": ["Rodeo", "Beverly Hills"], "ASP01": ["Aspen"], "TOR01": ["Yorkville", "Toronto"],
    "TYO01": ["Ginza", "銀座"], "TYO02": ["Omotesando", "表参道"], "OSA01": ["Shinsaibashi", "心斎橋"],
    "SEL01": ["Cheongdam", "청담", "Seoul Flagship"], "SEL02": ["Hyundai Apgujeong", "압구정 현대"], "BUS01": ["Centum", "센텀"],
    "SHA01": ["Plaza 66", "恒隆"], "BJS01": ["SKP", "北京SKP"], "CDU01": ["Taikoo Li", "太古里"], "HKG01": ["Canton Road", "廣東道"],
    "TPE01": ["Taipei 101", "台北101"], "SIN01": ["MBS", "Marina Bay Sands"], "SYD01": ["Castlereagh", "Sydney"],
}


def matnr(sku: str) -> str:
    """SAP material number = style + colour without separator (AFS generic article)."""
    s, c = sku.split("-")
    return f"{s}{c}"


def sku_from_matnr(m: str) -> str:
    return f"{m[:12]}-{m[12:]}"


SIZE_IDX = {}
for _run, _sizes in config.SIZE_RUNS.items():
    for _i, _s in enumerate(_sizes):
        SIZE_IDX[(_run, _s)] = _i


def pcl_item_code(sku: str, size: str) -> str:
    """3PL (DC-HK-TKO) item code: MC + last 8 of style + colour + 2-digit size index (1-based)."""
    style, color = sku.split("-")
    run = skus().set_index("sku").size_run[sku]
    return f"MC{style[-8:]}{color}{SIZE_IDX[(run, size)] + 1:02d}"


# ----------------------------------------------------------------------------- cross-system FACTS
# Purchase orders with ETAs/revisions. Quantities per DC (werks) are totals; size split done in warehouse.py.
VENDORS = {
    "V100231": "Atelier Nistru SRL (Chisinau, MD) - outerwear CMT",
    "V100418": "Hanoi Down Garment Co., Ltd. (VN)",
    "V100077": "Maglificio Val Seriana S.p.A. (BG, IT) - knitwear",
    "V100502": "Romarta Confectii SA (Timisoara, RO) - outerwear",
    "V100610": "Guangdong Polar Apparel Mfg (Dongguan, CN) - Couture capsule",
    "V100125": "Calzaturificio Brenta S.r.l. (VE, IT) - footwear",
    "V100389": "Lanificio Alto Biellese S.p.A. (BI, IT) - accessories knit",
}

KEY_POS = [
    # AUREA black re-order: laqué nylon delay at the mill. Revisions are what systems knew at each date.
    dict(ebeln="4500218734", vendor="V100231", sku="J20931A00012-999", created="2026-08-24",
         lines=[dict(ebelp="00010", werks="IT10", qty=420, gr="2026-10-16"),
                dict(ebelp="00020", werks="US20", qty=220, gr="2026-10-19"),
                dict(ebelp="00030", werks="HK30", qty=1040, gr="2026-10-16"),
                dict(ebelp="00040", werks="IT10", qty=300, gr="2026-10-19")],
         revisions=[("2026-08-24", "2026-09-25", "PO created, confirmed by vendor"),
                    ("2026-09-10", "2026-10-02", "Vendor: laqué nylon from mill delayed (dyeing lot rejected)"),
                    ("2026-09-24", "2026-10-09", "Vendor: fabric arrived, cutting started; new ex-works Oct 5"),
                    ("2026-10-01", "2026-10-16", "Vendor: final ETA, air freight booked for IT/HK; US +3 days"),
                    ("2026-10-14", "2026-10-19", "Line 00040 (balance 300 pcs IT10) pulled in from 2026-10-30")],
         note="Line 00010 = the '420 units on Oct 16' everybody in EMEA talks about."),
    dict(ebeln="4500219960", vendor="V100418", sku="J20931A00618-510", created="2026-07-20",
         lines=[dict(ebelp="00010", werks="HK30", qty=330, gr="2026-10-08"),
                dict(ebelp="00020", werks="IT10", qty=190, gr="2026-10-08"),
                dict(ebelp="00030", werks="US20", qty=80, gr="2026-10-08")],
         revisions=[("2026-07-20", "2026-10-08", "Second delivery of launch buy (top-up 600 pcs)"),
                    ("2026-10-02", "2026-10-08", "Merch asked to expedite: vendor says no earlier than Oct 8 (already on water/air)")],
         note="IRIDIA powder pink top-up 600 pcs. Split HK/IT/US decided at S&OP before the K-pop spike."),
    dict(ebeln="4500222417", vendor="V100418", sku="J20931A00618-510", created="2026-10-05",
         lines=[dict(ebelp="00010", werks="HK30", qty=800, gr=None, eta="2026-11-20"),
                dict(ebelp="00020", werks="IT10", qty=300, gr=None, eta="2026-11-20"),
                dict(ebelp="00030", werks="US20", qty=100, gr=None, eta="2026-11-24")],
         revisions=[("2026-10-05", "2026-11-27", "Emergency re-order after social spike, vendor capacity limited"),
                    ("2026-10-16", "2026-11-20", "Vendor confirmed earlier slot; fabric in stock")],
         note="Next IRIDIA pink receipt ~Nov 20: nothing before that."),
    dict(ebeln="4500221188", vendor="V100418", sku="J20931A00618-999", created="2026-09-28",
         lines=[dict(ebelp="00010", werks="HK30", qty=450, gr="2026-10-20"),
                dict(ebelp="00020", werks="IT10", qty=300, gr="2026-10-20"),
                dict(ebelp="00030", werks="US20", qty=100, gr="2026-10-20")],
         revisions=[("2026-09-28", "2026-10-23", "Re-order black (spill-over)"),
                    ("2026-10-09", "2026-10-20", "Expedited by air")],
         note="IRIDIA black back at all DCs Oct 20; EMEA/US stores not yet replenished as of Oct 21."),
    dict(ebeln="4500221905", vendor="V100077", sku="I10919B00011-999|I10919B00011-742", size="M", created="2026-10-02",
         lines=[dict(ebelp="00010", werks="IT10", qty=120, gr=None, eta="2026-10-30", sku="I10919B00011-999"),
                dict(ebelp="00020", werks="IT10", qty=60, gr=None, eta="2026-10-30", sku="I10919B00011-742"),
                dict(ebelp="00030", werks="US20", qty=30, gr=None, eta="2026-11-03", sku="I10919B00011-999"),
                dict(ebelp="00040", werks="HK30", qty=90, gr=None, eta="2026-11-04", sku="I10919B00011-999"),
                dict(ebelp="00050", werks="HK30", qty=50, gr=None, eta="2026-11-04", sku="I10919B00011-742")],
         revisions=[("2026-10-02", "2026-10-30", "Knit re-order size M only, wk44"),
                    ("2026-10-20", "2026-10-30", "Vendor: 60% Oct 30, balance Nov 6 (yarn)")],
         note="VLOGO CARDIGAN size M re-order; DC has no M until Oct 30 (IT)."),
    dict(ebeln="4500222090", vendor="V100502", sku="J20931A00622-23R", sizes=["0", "1", "2"], created="2026-09-29",
         lines=[dict(ebelp="00010", werks="IT10", qty=150, gr=None, eta="2026-11-10"),
                dict(ebelp="00020", werks="HK30", qty=60, gr=None, eta="2026-11-12"),
                dict(ebelp="00030", werks="US20", qty=20, gr=None, eta="2026-11-13")],
         revisions=[("2026-09-29", "2026-11-10", "Re-order brown small sizes (0/1/2)"),
                    ("2026-10-15", "2026-11-10", "Confirmed; vendor asks to accept 2% over-delivery")],
         note="AMALIA chocolate brown sizes 0-2 out at DC until Nov 10."),
]

def po_line_eta_known(po: dict, line: dict, t) -> "dt.date | None":
    """ETA of a KEY_POS line as visible in the systems on date t (None if PO not yet created)."""
    t = d(t)
    if d(po["created"]) > t:
        return None
    revs = [(d(u), d(e), n) for u, e, n in po["revisions"]]
    final = line.get("gr") or line.get("eta")
    if po["ebeln"] == "4500218734":           # AUREA black: line-specific history
        if line["ebelp"] == "00040":
            return d("2026-10-30") if t < d("2026-10-14") else d("2026-10-19")
        eta = [e for u, e, n in revs if u <= t and e != d("2026-10-19")][-1]
        if line["ebelp"] == "00020" and t >= d("2026-10-01"):
            eta = eta + dt.timedelta(days=3)
        return eta
    eta = [e for u, e, n in revs if u <= t][-1]
    po_final = revs[-1][1]
    if final:
        eta = eta + (d(final) - po_final)
    return eta


ILVARO_TOPUP_ECOM_RESERVE = {"HK30": 70, "IT10": 40, "US20": 15}

VALENTINO_V17 = dict(sku_prefix="J10911A00305", bad_batch="2607-A114", good_batch="2609-B027", old_batch="2604-A031",
           bad_batch_gr={"IT10": "2026-08-11", "US20": "2026-08-12", "HK30": "2026-08-12"},
           good_batch_gr={"IT10": "2026-09-18", "US20": "2026-09-21", "HK30": "2026-09-19"},
           qn="300004587", qn_created="2026-09-30", usage_decision="2026-10-02",
           defect="Zipper slider (YKK-compatible #5 slider, supplier lot SL-0726) detaches / does not lock")

def awb(shipment_id: str, carrier: str) -> str:
    """Deterministic carrier tracking number (format depends on carrier)."""
    import zlib
    h = zlib.crc32((shipment_id + carrier).encode())
    n = int(shipment_id[-5:])
    if carrier == "DHL Express":
        return f"{(h % 9000000000) + 1000000000}"
    if carrier == "FedEx":
        return f"7{(h % 90000000000) + 10000000000:011d}"
    if carrier == "UPS":
        return f"1Z{h % 0xFFFFFF:06X}0{n:05d}{h % 9973:04d}"
    if carrier == "BRT":
        return f"0{(h % 900000000000) + 100000000000}"[:13]
    if carrier == "GEODIS":
        return f"GEO{(h % 900000000) + 100000000}"
    if carrier == "SF Express":
        return f"SF{(h % 9000000000000) + 1000000000000}"
    if carrier == "Kerry Logistics":
        return f"KLHK{(h % 900000000) + 100000000}"
    if carrier == "Nippon Express":
        return f"NX{(h % 9000000000) + 1000000000}"
    return f"X{h}"


CUSTOMS_HOLD = dict(shipment_id="SHP02600440", store="SEL01", awb=None, carrier="Nippon Express",
                    held_from="2026-10-08", released="2026-10-12", delivered="2026-10-13",
                    reason="KC certificate (KC conformity / labelling declaration for down-filled garments) missing "
                    "from the import docs; broker requested the KC 적합성 certificate copy")
CUSTOMS_HOLD["awb"] = awb(CUSTOMS_HOLD["shipment_id"], CUSTOMS_HOLD["carrier"])
MISPICK = dict(shipments=["SHP02600337", "SHP02600382"], store="MAD01", sku_ordered="J10911A00034-999",
               sku_received="J10911A00034-742")

LON01_EVENT = dict(date="2026-10-08", invited=45, rsvp_yes=39, attended=36, plus_ones=9, purchasers=23,
                   transactions=27, crm_campaign_id="7015g00000Q8LnBAAV")

# e-commerce order number formats (used by customer care tickets)
ECOM_ORDER_PREFIX = {"EMEA": "EU", "AMERICAS": "US", "APAC": "AP"}   # e.g. MC-EU-26-0412345


def delivery_no(shipment_id: str) -> str:
    """SAP outbound delivery number (VBELN) for an internal shipment id SHP026xxxxx."""
    return f"0080{int(shipment_id[-5:]) + 412000:06d}"


def write_note(area: str, text: str):
    (NOTES / f"{area}.md").write_text(text.strip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    print(pd.DataFrame({"store": list(SAP_WERKS), "werks": list(SAP_WERKS.values()),
                        "crm": [CRM_CODE[s] for s in SAP_WERKS], "tms": [TMS_SHIPTO[s] for s in SAP_WERKS]}).to_string())
