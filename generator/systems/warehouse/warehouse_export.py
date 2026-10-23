"""Exports of the warehouse systems (reads _cache/wms_state.pkl produced by warehouse.py)."""
import datetime as dt
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402
import config  # noqa: E402

R = C.rng("warehouse_export")
OUT = C.OUT / "warehouse"
S = pd.read_pickle(C.CACHE / "wms_state.pkl")
DAYS = list(C.daterange("2026-08-01", "2026-10-21"))
DI = {x: i for i, x in enumerate(DAYS)}
ND = len(DAYS)
sk = C.skus().set_index("sku")
st = C.stores().set_index("store_id")
ean = C.sku_sizes().set_index(["sku", "size"]).ean
SN = {s: C.STYLE_NAME[s.split("-")[0]] for s in sk.index}
RUN = {s: config.SIZE_RUNS[sk.size_run[s]] for s in sk.index}
W_TZ = {"IT10": "Europe/Rome", "US20": "America/New_York", "HK30": "Asia/Hong_Kong"}
REG_W = {"EMEA": "IT10", "AMERICAS": "US20", "APAC": "HK30"}
DCW = {"DC-IT-CSG": "IT10", "DC-US-NJ": "US20", "DC-HK-TKO": "HK30"}

main_eod, qm_eod, rt_eod, out1_eod = S["main_eod"], S["qm_eod"], S["rt_eod"], S["out1_eod"]
web_eod, tib_blocked, tib_batch_eod = S["web_eod"], S["tib_blocked"], S["tib_batch_eod"]
receipts, open_orders = S["receipts"], S["open_orders"]

SUBCAT_IT = {"Short down jacket": "GIUBB.CORTO PIUMINO", "Long down jacket": "PIUMINO LUNGO", "Cropped down jacket": "PIUMINO CROPPED",
             "Long down coat": "CAPPOTTO PIUMINO", "Rain jacket": "GIACCA ANTIPIOGGIA", "Down vest": "GILET PIUMINO",
             "Long parka": "PARKA LUNGO", "Wool down jacket": "PIUMINO LANA", "Windbreaker": "GIACCA A VENTO",
             "Ski jacket": "GIACCA SCI", "Ski trousers": "PANTALONE SCI", "Down cape": "MANTELLA PIUMINO",
             "Oversized down jacket": "PIUMINO OVERSIZE", "Knit balaclava": "PASSAMONTAGNA", "Cardigan": "CARDIGAN",
             "Padded cardigan": "CARDIGAN IMBOTTITO", "Sweater": "MAGLIONE", "Turtleneck": "DOLCEVITA", "Hoodie": "FELPA CAPPUCCIO",
             "Sweatshirt": "FELPA", "T-shirt": "T-SHIRT", "Jersey Polo": "JERSEY POLO", "Sneakers": "SNEAKERS", "Après-ski boots": "DOPOSCI APRÈS-SKI",
             "Beanie": "BERRETTO", "Scarf": "SCIARPA", "Gloves": "GUANTI", "Baseball cap": "CAPPELLINO", "Belt bag": "MARSUPIO",
             "Backpack": "ZAINO"}


def maktx(s):
    return f"{SN[s]} {SUBCAT_IT.get(sk.subcategory[s], '')} {config.COLORS[s.split('-')[1]][0].upper()}"[:40]


def it_num(q):
    """SAP IT user format: 1.234,000"""
    s_ = f"{abs(q):,.3f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-" if q < 0 else "") + s_


def us_num(q):
    return f"{q:,.3f}"


# =============================================================================== 1. SAP stock (IT10 / US20)
def stock_rows(w, i):
    x = DAYS[i]
    rows = []
    keys = sorted({k for k in list(main_eod) + list(qm_eod) + list(web_eod) if k[0] == w})
    for k in keys:
        _, s, z = k
        m = int(main_eod[k][i]) if k in main_eod else 0
        tb = int(tib_blocked[k][i]) if k in tib_blocked else 0
        # rows only if the material ever had stock at the plant up to this date
        hist = (main_eod[k][:i + 1].max() if k in main_eod else 0) + (tb > 0)
        if hist == 0 and not (k in web_eod and web_eod[k][:i + 1].max() > 0) and not (k in qm_eod and qm_eod[k][i] > 0):
            continue
        if k in tib_batch_eod:
            for b, arr in tib_batch_eod[k].items():
                if arr[:i + 1].max() > 0:
                    rows.append((x, w, "0001", s, z, b, int(arr[i]), 0, 0, 0))
            if tb:
                rows.append((x, w, "0001", s, z, C.VALENTINO_V17["bad_batch"], 0, 0, tb, 0))
        else:
            rows.append((x, w, "0001", s, z, "", m, 0, 0, 0))
        if k in web_eod and web_eod[k][:i + 1].max() > 0:
            rows.append((x, w, "W100", s, z, "", int(web_eod[k][i]), 0, 0, 0))
        if k in qm_eod and qm_eod[k][i] > 0:
            rows.append((x, w, "QM01", s, z, C.VALENTINO_V17["bad_batch"] if SN[s] == "VEL" else "", 0, 0, int(qm_eod[k][i]), 0))
        if k in rt_eod and rt_eod[k][i] > 0:
            rows.append((x, w, "RT01", s, z, "", 0, 0, 0, int(rt_eod[k][i])))
        if k in out1_eod and out1_eod[k][i] > 0:
            rows.append((x, w, "OUT1", s, z, "", int(out1_eod[k][i]), 0, 0, 0))
    return rows


COLS = ["STICHTAG", "WERKS", "LGORT", "MATNR", "MAKTX", "J_3ASIZE", "CHARG", "MEINS", "LABST", "INSME", "SPEME", "RETME", "UMLME", "EAN11"]
for w in ("IT10", "US20"):
    by_month = defaultdict(list)
    for i, x in enumerate(DAYS):
        if w == "IT10" and x.weekday() == 6:
            continue      # IT extraction job does not run on Sundays
        for r in stock_rows(w, i):
            x_, w_, lg, s, z, b, lab, insme, speme, retme = r
            if w == "IT10":
                row = [x_.strftime("%d.%m.%Y"), w_, lg, C.matnr(s), maktx(s), z, b, "ST", it_num(lab), it_num(insme),
                       it_num(speme), it_num(retme), it_num(0), ean[(s, z)]]
            else:
                row = [x_.strftime("%m/%d/%Y"), w_, lg, C.matnr(s), maktx(s), z, b, "PC", us_num(lab), us_num(insme),
                       us_num(speme), us_num(retme), us_num(0), ean[(s, z)]]
            by_month[x_.strftime("%Y%m")].append(row)
    for ym, rows in by_month.items():
        df = pd.DataFrame(rows, columns=COLS)
        if w == "IT10" and ym == "202609":
            # quirk: the 30.09 extraction ran twice and both outputs were concatenated (W100 block duplicated)
            dup = df[(df.STICHTAG == "30.09.2026") & (df.LGORT == "W100")]
            df = pd.concat([df, dup], ignore_index=True)
        p = OUT / f"sap_stock_{w}" / f"MARD_AFS_{w}_{ym}.csv"
        if w == "IT10":
            df.to_csv(p, sep=";", index=False, encoding="utf-8")
        else:
            # US export downloaded by a user with Windows code page -> cp1252 encoding
            df.to_csv(p, sep=",", index=False, encoding="cp1252")
    print(w, "stock files", len(by_month))

# =============================================================================== 2. HK 3PL daily snapshots
oo = defaultdict(lambda: np.zeros(ND, dtype=np.int64), open_orders)
TKO = OUT / "pcl_tko_inventory"


def tko_rows(i):
    x = DAYS[i]
    rows = []
    snap = dt.datetime.combine(x + dt.timedelta(days=1), dt.time(6, 5)) + dt.timedelta(minutes=int(R.integers(0, 20)))
    keys = sorted({k for k in list(main_eod) + list(qm_eod) + list(web_eod) if k[0] == "HK30"})
    for k in keys:
        _, s, z = k
        hist = main_eod[k][:i + 1].max() if k in main_eod else 0
        if hist == 0 and not (k in web_eod and web_eod[k][:i + 1].max() > 0) and not (k in qm_eod and qm_eod[k][i] > 0):
            continue
        item = C.pcl_item_code(s, z)
        desc = f"{SN[s]} {sk.subcategory[s]} {config.COLORS[s.split('-')[1]][1]} SZ {z}".upper()
        if k in tib_batch_eod:
            parts = [(b, int(a[i])) for b, a in tib_batch_eod[k].items() if a[:i + 1].max() > 0]
        else:
            parts = [("", int(main_eod[k][i]) if k in main_eod else 0)]
        alloc_left = int(oo[k][i]) if k in oo else 0
        for lot, q in parts:
            pick = int(round(q * 0.3)) if q > 6 else q
            res = q - pick
            for lt, qq in (("PICK", pick), ("RESERVE", res)):
                if qq == 0 and lt == "RESERVE":
                    continue
                al = min(alloc_left, qq)
                alloc_left -= al
                rows.append([snap.strftime("%Y-%m-%d %H:%M"), "TKO-3", "MONC01", item, ean[(s, z)], desc, lot, lt, qq, al, qq - al, 0, "PCS"])
        if k in tib_blocked and tib_blocked[k][i] > 0:
            q = int(tib_blocked[k][i])
            rows.append([snap.strftime("%Y-%m-%d %H:%M"), "TKO-3", "MONC01", item, ean[(s, z)], desc, C.VALENTINO_V17["bad_batch"], "QC-HOLD", q, 0, 0, q, "PCS"])
        if k in web_eod and web_eod[k][:i + 1].max() > 0:
            q = int(web_eod[k][i])
            rows.append([snap.strftime("%Y-%m-%d %H:%M"), "TKO-3", "MONC01", item, ean[(s, z)], desc, "", "ECOM", q, 0, q, 0, "PCS"])
        if k in qm_eod and qm_eod[k][i] > 0:
            q = int(qm_eod[k][i])
            rows.append([snap.strftime("%Y-%m-%d %H:%M"), "TKO-3", "MONC01", item, ean[(s, z)], desc,
                         C.VALENTINO_V17["bad_batch"] if SN[s] == "VEL" else "", "QC-HOLD", q, 0, 0, q, "PCS"])
        if k in rt_eod and rt_eod[k][i] > 0:
            q = int(rt_eod[k][i])
            rows.append([snap.strftime("%Y-%m-%d %H:%M"), "TKO-3", "MONC01", item, ean[(s, z)], desc, "", "RETURNS", q, 0, 0, q, "PCS"])
        if k in out1_eod and out1_eod[k][i] > 0:
            q = int(out1_eod[k][i])
            rows.append([snap.strftime("%Y-%m-%d %H:%M"), "TKO-3", "MONC01", item, ean[(s, z)], desc, "", "B-GRADE", q, 0, 0, q, "PCS"])
    return rows


TKO_COLS = ["Snapshot Time (HKT)", "Site", "Client Code", "Item Code", "Barcode", "Item Description", "Lot No", "Location Type",
            "On Hand Qty", "Allocated Qty", "Available Qty", "Hold Qty", "UOM"]
prev = None
for i, x in enumerate(DAYS):
    if x == dt.date(2026, 10, 1):
        prev = tko_rows(i)
        continue      # National Day: no export generated
    rows = tko_rows(i)
    if x == dt.date(2026, 10, 18):
        rows = prev   # stale: interface re-sent the Oct 17 snapshot (timestamps and quantities of Oct 17)
    df = pd.DataFrame(rows, columns=TKO_COLS)
    if x == dt.date(2026, 9, 21):
        # ASTRA items not yet mapped in 3PL item master on first days -> item code UNMAPPED
        pass
    df.to_csv(TKO / f"TKO_INV_SNAPSHOT_{x:%Y%m%d}.csv", index=False, encoding="utf-8-sig")
    prev = rows
print("TKO snapshots done")

# =============================================================================== 3. outbound deliveries + goods movements
SH = C.shipments()
la = pd.read_csv(C.CACHE / "launch_allocations.csv", dtype={"size": str}, parse_dates=["launch_date", "gi_date"])
CARRIER_TDLNR = {"DHL Express": "V900011", "BRT": "V900015", "GEODIS": "V900019", "FedEx": "V900031", "UPS": "V900033",
                 "SF Express": "V900052", "Kerry Logistics": "V900055", "Nippon Express": "V900058"}
DEFAULT_CARRIER = {"EMEA": "DHL Express", "AMERICAS": "FedEx", "APAC": "DHL Express"}
dlv = []
launch_ship = []
for s in SH:
    w = DCW[s["origin"]]
    lines = s["lines"]
    units = sum(l["qty_shipped"] for l in lines)
    dlv.append(dict(VBELN=C.delivery_no(s["shipment_id"]), LFART="ZRPL", VSTEL=w, KUNNR=C.TMS_SHIPTO[s["store_id"]],
                    ERDAT=s["order_date"], WADAT=s["ship_date"], WADAT_IST=s["ship_date"], LFDAT=s["planned_arrival"],
                    XABLN=s["shipment_id"], BOLNR=C.awb(s["shipment_id"], s["carrier"]), TDLNR=CARRIER_TDLNR[s["carrier"]],
                    CARRIER=s["carrier"], ANZPK=max(1, math.ceil(units / 6)), POSNR_CNT=len(lines), LFIMG_SUM=units,
                    BTGEW_KG=round(units * R.uniform(1.1, 1.6), 1)))
lseq = 0
for (gd, sid), g in la.groupby(["gi_date", "store_id"]):
    lseq += 1
    reg = st.region[sid]
    w = REG_W[reg]
    car = DEFAULT_CARRIER[reg]
    ref = f"LAU{gd:%y%m%d}{sid}"
    vb = f"0081{lseq + 200:06d}"
    units = int(g.qty.sum())
    lead = {"EMEA": 1, "AMERICAS": 5, "APAC": 6}[reg]
    dlv.append(dict(VBELN=vb, LFART="ZLAU", VSTEL=w, KUNNR=C.TMS_SHIPTO[sid], ERDAT=(gd - dt.timedelta(days=3)).date().isoformat(),
                    WADAT=gd.date().isoformat(), WADAT_IST=gd.date().isoformat(), LFDAT=(gd + dt.timedelta(days=lead)).date().isoformat(),
                    XABLN=ref, BOLNR=C.awb(ref + "00000"[:0] + f"{lseq:05d}", car), TDLNR=CARRIER_TDLNR[car], CARRIER=car,
                    ANZPK=max(1, math.ceil(units / 6)), POSNR_CNT=len(g), LFIMG_SUM=units, BTGEW_KG=round(units * R.uniform(1.2, 1.6), 1)))
    launch_ship.append(dict(ref=ref, vbeln=vb, store_id=sid, werks=w, gi_date=gd.date().isoformat(),
                            launch_date=g.launch_date.iloc[0].date().isoformat(), carrier=car, awb=dlv[-1]["BOLNR"], units=units,
                            lines=[dict(sku=r.sku, size=r.size, qty=int(r.qty)) for r in g.itertuples()]))
dlv_df = pd.DataFrame(dlv).sort_values(["WADAT", "VBELN"])
# quirk: BOLNR missing on a handful of deliveries (carrier label printed from carrier portal, not interfaced)
miss = R.choice(len(dlv_df), 9, replace=False)
dlv_df.iloc[miss, dlv_df.columns.get_loc("BOLNR")] = ""
(OUT / "outbound").mkdir(exist_ok=True)
dlv_df.to_csv(OUT / "outbound" / "LIKP_outbound_deliveries_2026-08_10.csv", index=False)
with open(C.CACHE / "launch_shipments.json", "w") as f:
    json.dump(launch_ship, f)

# goods movements MSEG-like (IT10 + US20 SAP; HK30 via 3PL transaction log)
mv = []
mblnr = [4900350000]


def mb():
    mblnr[0] += 1
    return str(mblnr[0])


for s in SH:
    w = DCW[s["origin"]]
    m = mb()
    for zi, ln in enumerate(s["lines"], 1):
        mv.append((s["ship_date"], w, "601", "0001", ln["sku"], ln["size"], "", -ln["qty_shipped"], "", "", C.delivery_no(s["shipment_id"]),
                   C.TMS_SHIPTO[s["store_id"]], "", m, zi, ""))
for d_ in dlv:
    if d_["LFART"] == "ZLAU":
        pass
for ls in launch_ship:
    m = mb()
    for zi, ln in enumerate(ls["lines"], 1):
        mv.append((ls["gi_date"], ls["werks"], "601", "0001", ln["sku"], ln["size"], "", -ln["qty"], "", "", ls["vbeln"],
                   C.TMS_SHIPTO[ls["store_id"]], "", m, zi, "LANCIO FW26"))
for r in receipts:
    mv.append((r["date"].isoformat(), r["werks"], "101", "0001", r["sku"], r["size"], r["batch"], r["qty"], r["ebeln"], r["ebelp"], "",
               "", "", None, None, ""))
wx = pd.read_csv(C.CACHE / "ecom_web_transfers.csv", dtype={"size": str})
for r in wx.itertuples():
    mv.append((r.date, r.werks, "311", "0001", r.sku, r.size, "", -r.qty, "", "", "", "", "W100", None, None, "RIFORN. WEB" if r.werks == "IT10" else "WEB REPLEN"))
    mv.append((r.date, r.werks, "311", "W100", r.sku, r.size, "", r.qty, "", "", "", "", "0001", None, None, ""))
es = pd.read_csv(C.CACHE / "ecom_sales_units.csv", dtype={"size": str})
NODEW = {"EMEA": "IT10", "AMERICAS": "US20", "APAC": "HK30"}
CC_NODE = {"US": "AMERICAS", "CA": "AMERICAS", "JP": "APAC", "KR": "APAC", "CN": "APAC", "HK": "APAC", "TW": "APAC", "SG": "APAC", "AU": "APAC"}
es["werks"] = es.country.map(lambda c: NODEW[CC_NODE.get(c, "EMEA")])
for (d_, w, s, z), q in es.groupby(["date", "werks", "sku", "size"]).qty.sum().items():
    mv.append((d_, w, "601", "W100", s, z, "", -int(q), "", "", "ECOMCOLL", "", "", None, None, "ECOM COLLECTIVE GI"))
for (x, w, s, z, q, bw) in S["adjustments"]:
    mv.append((x.isoformat(), w, bw, "0001", s, z, "", q, "", "", "", "", "", None, None, "INVENTARIO ROTATIVO 06/10 - DIFF"))
for r in S["sto_rows"]:
    mv.append(("2026-10-15", "IT10", "641", "0001", r["sku"], r["size"], "", -r["qty"], "4700001288", "00010", "0080499120", "", "", None, None, "STO IT10>HK30 COUTURE"))
UD = C.VALENTINO_V17["usage_decision"]
for k, arr in tib_blocked.items():
    q = int(arr[-1])
    if q and k[0] != "HK30":
        mv.append((UD, k[0], "344", "0001", k[1], k[2], C.VALENTINO_V17["bad_batch"], q, "", "", "", "", "", None, None, f"BLOCCO QN {C.VALENTINO_V17['qn']}"))
sd = S["store_def"]
for r in sd.itertuples():
    if r.dc_receipt is not None and r.werks != "HK30" and isinstance(r.dc_receipt, dt.date):
        mv.append((r.dc_receipt.isoformat(), r.werks, "653", "QM01", r.sku, r.size, C.VALENTINO_V17["bad_batch"], r.qty, "", "", "",
                   C.TMS_SHIPTO[r.store_id], "", None, None, f"RESO DIFETTOSO {r.receipt_id}"))
for (x, w, s, z, a_, b_) in S["grading"]:
    if w == "HK30":
        continue
    if a_:
        mv.append((x.isoformat(), w, "311", "RT01", s, z, "", -a_, "", "", "", "", "0001", None, None, "GRADING A"))
        mv.append((x.isoformat(), w, "311", "0001", s, z, "", a_, "", "", "", "", "RT01", None, None, "GRADING A"))
    if b_:
        mv.append((x.isoformat(), w, "311", "RT01", s, z, "", -b_, "", "", "", "", "OUT1", None, None, "GRADING B / STOCK LOT"))
        mv.append((x.isoformat(), w, "311", "OUT1", s, z, "", b_, "", "", "", "", "RT01", None, None, "GRADING B / STOCK LOT"))
mvdf = pd.DataFrame(mv, columns=["BUDAT", "WERKS", "BWART", "LGORT", "SKU", "J_3ASIZE", "CHARG", "MENGE", "EBELN", "EBELP", "VBELN_VL",
                                 "KUNNR", "UMLGO", "MBLNR", "ZEILE", "SGTXT"])
mvdf = mvdf[mvdf.WERKS.isin(["IT10", "US20"])].copy()
mvdf["MATNR"] = mvdf.SKU.map(C.matnr)
mvdf["SHKZG"] = np.where(mvdf.MENGE < 0, "H", "S")
mvdf["MENGE"] = mvdf.MENGE.abs()
mvdf["MEINS"] = np.where(mvdf.WERKS == "IT10", "ST", "PC")
mvdf = mvdf.sort_values(["BUDAT", "WERKS", "BWART"], kind="stable")
mvdf["MBLNR"] = mvdf.MBLNR.fillna(pd.Series([str(4900400000 + i) for i in range(len(mvdf))], index=mvdf.index))
mvdf["ZEILE"] = mvdf.groupby("MBLNR").cumcount() + 1
mvdf["BUDAT"] = pd.to_datetime(mvdf.BUDAT).dt.strftime("%Y%m%d")
mvdf[["MBLNR", "ZEILE", "BUDAT", "BWART", "WERKS", "LGORT", "MATNR", "J_3ASIZE", "CHARG", "MENGE", "MEINS", "SHKZG", "EBELN", "EBELP",
      "VBELN_VL", "KUNNR", "UMLGO", "SGTXT"]].to_csv(OUT / "outbound" / "MSEG_goods_movements_IT10_US20.csv", index=False)
print("MSEG rows", len(mvdf))

# HK 3PL transaction log
tx = []
for s in SH:
    if s["origin"] != "DC-HK-TKO":
        continue
    so = f"SO-TKO-{int(s['shipment_id'][-5:]) + 70000}"
    for ln in s["lines"]:
        tx.append((s["ship_date"], "SHP", so, s["shipment_id"], ln["sku"], ln["size"], -ln["qty_shipped"], "PICK", s["store_id"]))
for ls in launch_ship:
    if ls["werks"] == "HK30":
        for ln in ls["lines"]:
            tx.append((ls["gi_date"], "SHP", f"SO-TKO-L{ls['vbeln'][-4:]}", ls["ref"], ln["sku"], ln["size"], -ln["qty"], "PICK", ls["store_id"]))
for r in receipts:
    if r["werks"] == "HK30":
        tx.append((r["date"].isoformat(), "RCV", f"ASN-{r['ebeln'][-6:]}", r["ebeln"], r["sku"], r["size"], r["qty"], "RESERVE", ""))
for r in wx[wx.werks == "HK30"].itertuples():
    tx.append((r.date, "XFER", "WEB-REPL", "", r.sku, r.size, r.qty, "ECOM", ""))
for r in S["sto_rows"]:
    tx.append(("2026-10-21", "RCV", "ASN-STO1288", "4700001288", r["sku"], r["size"], r["qty"], "RESERVE", ""))
for k, arr in tib_blocked.items():
    if k[0] == "HK30" and arr[-1]:
        tx.append(("2026-10-03", "HOLD", f"QN{C.VALENTINO_V17['qn']}", "CLIENT INSTRUCTION", k[1], k[2], int(arr[-1]), "QC-HOLD", ""))
for r in sd.itertuples():
    if r.werks == "HK30" and isinstance(r.dc_receipt, dt.date):
        tx.append((r.dc_receipt.isoformat(), "RTN", f"RMA-{r.receipt_id[-9:]}", r.receipt_id, r.sku, r.size, r.qty, "QC-HOLD", r.store_id))
txdf = pd.DataFrame(tx, columns=["txn_date", "txn_type", "ref_no", "client_ref", "sku", "size", "qty", "location_type", "consignee"])
txdf["Txn Time (HKT)"] = pd.to_datetime(txdf.txn_date) + pd.to_timedelta(R.integers(8 * 60, 21 * 60, len(txdf)), unit="m")
txdf["Item Code"] = [C.pcl_item_code(s, z) for s, z in zip(txdf.sku, txdf["size"])]
txdf["Barcode"] = [ean[(s, z)] for s, z in zip(txdf.sku, txdf["size"])]
txdf = txdf.sort_values("Txn Time (HKT)")
txdf["Txn Time (HKT)"] = txdf["Txn Time (HKT)"].dt.strftime("%d/%m/%Y %H:%M")
txdf.rename(columns={"txn_type": "Txn Type", "ref_no": "Ref No", "client_ref": "Client Ref", "qty": "Qty",
                     "location_type": "Location Type", "consignee": "Consignee"})[
    ["Txn Time (HKT)", "Txn Type", "Ref No", "Client Ref", "Item Code", "Barcode", "Qty", "Location Type", "Consignee"]
].to_csv(OUT / "pcl_tko_inventory" / "TKO_TRANSACTIONS_202608-202610.csv", index=False, encoding="utf-8-sig")

# =============================================================================== 4. purchase orders + revisions + ASN
VENDOR_BY_CAT = {"Outerwear": ["V100231", "V100502", "V100418"], "Knitwear": ["V100077"], "Jersey": ["V100389"],
                 "Footwear": ["V100125"], "Accessories": ["V100389"], "Bottoms": ["V100502"]}
po_head = {}
po_rows = []
chg = []
chg_no = [70012000]
key_ebeln = {p["ebeln"] for p in C.KEY_POS}
rec = pd.DataFrame(receipts)
rec["date"] = pd.to_datetime(rec.date)
for (eb, w, s), g in rec.groupby(["ebeln", "werks", "sku"]):
    if eb in key_ebeln:
        continue
    gr = g.date.min().date()
    if eb not in po_head:
        cat = sk.category[s]
        vend = str(R.choice(VENDOR_BY_CAT[cat])) if not SN[s].startswith("ASTRA") else "V100610"
        kind = g.kind.iloc[0]
        created = gr - dt.timedelta(days=int(R.integers(50, 110)))
        po_head[eb] = dict(vendor=vend, created=created, bsart="ZLA" if kind == "LAUNCH_BUY" else "NB")
    h = po_head[eb]
    orig = gr + dt.timedelta(days=int(R.choice([-7, -5, -3, -2, 0, 0, 0, 0, 1, 2, 4, 6])))
    for r in g.itertuples():
        ordered = r.qty if R.random() > 0.08 else int(round(r.qty * R.uniform(1.02, 1.12)))  # under-delivery sometimes
        po_rows.append(dict(EBELN=eb, BSART=h["bsart"], LIFNR=h["vendor"], NAME1=C.VENDORS[h["vendor"]], BEDAT=h["created"].isoformat(),
                            EBELP="00010", WERKS=w, MATNR=C.matnr(s), MAKTX=maktx(s), J_3ASIZE=r.size, MENGE=ordered, MEINS="ST",
                            EINDT_ORIG=orig.isoformat(), EINDT=gr.isoformat(), WEMNG=r.qty, LAST_GR=gr.isoformat(),
                            ELIKZ="X", STATUS="RECEIVED" if ordered == r.qty else "RECEIVED_SHORT_CLOSED", BATCH=r.batch))
    if orig != gr:
        chg_no[0] += int(R.integers(1, 9))
        chg.append(dict(OBJECTID=eb, CHANGENR=str(chg_no[0]), UDATE=(gr - dt.timedelta(days=int(R.integers(3, 15)))).isoformat(),
                        USERNAME=str(R.choice(["PURCH_GBELLI", "PURCH_LMARINI", "EDI_ORDRSP", "EDI_ORDRSP", "PURCH_HKLEE"])),
                        TABNAME="EKET", FNAME="EINDT", WERKS=w, MATNR=C.matnr(s), VALUE_OLD=orig.strftime("%Y%m%d"),
                        VALUE_NEW=gr.strftime("%Y%m%d"), NOTE="vendor confirmation (ORDRSP)" if R.random() < 0.6 else ""))
# key POs
for po in C.KEY_POS:
    created = C.d(po["created"])
    first_eta = C.d(po["revisions"][0][1])
    skus_ = po["sku"].split("|")
    for ln in po["lines"]:
        s = ln.get("sku", skus_[0])
        sizes = [po["size"]] if po.get("size") else (po.get("sizes") or RUN[s])
        recd = rec[(rec.ebeln == po["ebeln"]) & (rec.ebelp == ln["ebelp"])]
        if len(recd):
            qty_by = recd.groupby("size").qty.sum().to_dict()
        else:
            cur = np.array([config.SIZE_CURVES[sk.size_run[s]][RUN[s].index(z)] for z in sizes])
            cur = cur / cur.sum()
            q = np.floor(cur * ln["qty"]).astype(int)
            for j in np.argsort(-(cur * ln["qty"] - q))[: ln["qty"] - q.sum()]:
                q[j] += 1
            qty_by = dict(zip(sizes, q))
        eta_now = ln.get("gr") or ln.get("eta")
        for z, q in qty_by.items():
            po_rows.append(dict(EBELN=po["ebeln"], BSART="ZRE", LIFNR=po["vendor"], NAME1=C.VENDORS[po["vendor"]], BEDAT=created.isoformat(),
                                EBELP=ln["ebelp"], WERKS=ln["werks"], MATNR=C.matnr(s), MAKTX=maktx(s), J_3ASIZE=z, MENGE=int(q), MEINS="ST",
                                EINDT_ORIG=first_eta.isoformat() if ln["ebelp"] != "00040" else "2026-10-30", EINDT=eta_now,
                                WEMNG=int(q) if ln.get("gr") else 0, LAST_GR=ln.get("gr") or "", ELIKZ="X" if ln.get("gr") else "",
                                STATUS="RECEIVED" if ln.get("gr") else "OPEN", BATCH=""))
    for (udate, new_eta, note) in po["revisions"][1:]:
        chg_no[0] += int(R.integers(1, 9))
        old = None
        for (u2, e2, n2) in po["revisions"]:
            if u2 < udate:
                old = e2
        chg.append(dict(OBJECTID=po["ebeln"], CHANGENR=str(chg_no[0]), UDATE=udate, USERNAME="PURCH_GBELLI" if "IT" in note or True else "",
                        TABNAME="EKET", FNAME="EINDT", WERKS="*", MATNR=C.matnr(skus_[0]), VALUE_OLD=C.d(old).strftime("%Y%m%d"),
                        VALUE_NEW=C.d(new_eta).strftime("%Y%m%d"), NOTE=note))

# open regular POs for the coming weeks (ATP buckets): items with healthy flow
open_rows = []
for (w, s, z), arr in main_eod.items():
    if (s, z) in {(a, b) for a, b, *_ in []}:
        continue
    if sk.season[s] in ("SS26", "FW24", "FW25", "SS25"):
        continue
    if SN[s] in ("AUREA", "IRIDIA", "VLOGO CARDIGAN", "AMALIA", "VEL") and s.split("-")[1] in ("999", "510", "23R", "742", "20D"):
        if not (SN[s] == "VEL" or (SN[s] == "VLOGO CARDIGAN" and z != "M")):
            continue
    last = int(arr[-1])
    out28 = 0
    if last < 25 and R.random() < 0.55:
        open_rows.append((w, s, z))
open_po = {}
for (w, s, z) in open_rows:
    keyp = (w, s)
    if keyp not in open_po:
        eta = C.TODAY + dt.timedelta(days=int(R.integers(4, 45)))
        while eta.weekday() >= 5:
            eta += dt.timedelta(days=1)
        open_po[keyp] = (str(4500223000 + len(open_po) * 7 + int(R.integers(0, 6))), eta)
    eb, eta = open_po[keyp]
    q = int(R.integers(3, 30))
    vend = str(R.choice(VENDOR_BY_CAT[sk.category[s]]))
    po_rows.append(dict(EBELN=eb, BSART="NB", LIFNR=vend, NAME1=C.VENDORS[vend], BEDAT=(eta - dt.timedelta(days=int(R.integers(40, 90)))).isoformat(),
                        EBELP="00010", WERKS=w, MATNR=C.matnr(s), MAKTX=maktx(s), J_3ASIZE=z, MENGE=q, MEINS="ST",
                        EINDT_ORIG=(eta - dt.timedelta(days=int(R.choice([0, 0, 0, 3, 7, -2])))).isoformat(), EINDT=eta.isoformat(),
                        WEMNG=0, LAST_GR="", ELIKZ="", STATUS="OPEN", BATCH=""))
pod = pd.DataFrame(po_rows)
(OUT / "inbound").mkdir(exist_ok=True)
pod = pod.sort_values(["BEDAT", "EBELN", "WERKS", "MATNR"])
pod["NETPR_EUR"] = pod.MATNR.map(lambda m: round(float(sk.price_eur[C.sku_from_matnr(m)]) * R.uniform(0.21, 0.27), 2))
pod.to_csv(OUT / "inbound" / "EKPO_EKET_purchase_orders_FW26.csv", index=False)
pd.DataFrame(chg).sort_values("UDATE").to_csv(OUT / "inbound" / "CDPOS_po_delivery_date_changes.csv", index=False)

# HK 3PL ASN list
asn = []
for (eb, w, s), g in rec[rec.werks == "HK30"].groupby(["ebeln", "werks", "sku"]):
    gr = g.date.min()
    eta = gr - pd.Timedelta(days=int(R.choice([0, 0, 0, 1, -1, 2])))
    asn.append(dict(asn_no=f"ASN-{eb[-6:]}", client_ref=eb, item_count=len(g), total_qty=int(g.qty.sum()), style=SN[s],
                    eta_hkt=(eta + pd.Timedelta(hours=int(R.integers(9, 17)))).strftime("%Y-%m-%d %H:%M"),
                    received_hkt=(gr + pd.Timedelta(hours=int(R.integers(10, 20)))).strftime("%Y-%m-%d %H:%M"),
                    status="RECEIVED", remarks=""))
for po in C.KEY_POS:
    for ln in po["lines"]:
        if ln["werks"] == "HK30" and not ln.get("gr"):
            asn.append(dict(asn_no=f"ASN-{po['ebeln'][-6:]}-{ln['ebelp'][-2:]}", client_ref=po["ebeln"], item_count=0, total_qty=ln["qty"],
                            style=C.STYLE_NAME[ln.get("sku", po["sku"]).split("|")[0].split("-")[0]],
                            eta_hkt=ln.get("eta", "") + " 00:00", received_hkt="", status="PRE-ADVISED",
                            remarks="ETA from client PO, no carrier booking yet"))
asn.append(dict(asn_no="ASN-STO1288", client_ref="4700001288", item_count=len(S["sto_rows"]), total_qty=int(sum(r["qty"] for r in S["sto_rows"])),
                style="ASTRA", eta_hkt="2026-10-20 14:00", received_hkt="2026-10-21 11:40", status="RECEIVED",
                remarks="Inter-DC transfer from IT10; 1 day late (flight offload FRA)"))
pd.DataFrame(asn).sort_values("eta_hkt").to_csv(OUT / "pcl_tko_inventory" / "TKO_ASN_INBOUND.csv", index=False, encoding="utf-8-sig")
print("PO rows", len(pod), "changes", len(chg))

# =============================================================================== 5. ATP snapshots
SNAPS = [dt.date(2026, 9, 7), dt.date(2026, 9, 14), dt.date(2026, 9, 21), dt.date(2026, 9, 28), dt.date(2026, 10, 5),
         dt.date(2026, 10, 12), dt.date(2026, 10, 19), dt.date(2026, 10, 22)]
# known ETA at date t
key_rev = {}
for po in C.KEY_POS:
    key_rev[po["ebeln"]] = po["revisions"]


def eta_known(row, t):
    if row["EBELN"] in key_rev:
        po = [p for p in C.KEY_POS if p["ebeln"] == row["EBELN"]][0]
        ln = [l for l in po["lines"] if l["ebelp"] == row["EBELP"]][0]
        return C.po_line_eta_known(po, ln, t)
    if C.d(row["BEDAT"]) > t:
        return None
    final = C.d(row["EINDT"])
    return final if t >= final - dt.timedelta(days=7) else C.d(row["EINDT_ORIG"])


pod_l = pod.to_dict("records")
po_by_key = defaultdict(list)
for r in pod_l:
    po_by_key[(r["WERKS"], C.sku_from_matnr(r["MATNR"]), r["J_3ASIZE"])].append(r)
(OUT / "atp").mkdir(exist_ok=True)
for t in SNAPS:
    i = DI[t - dt.timedelta(days=1)]
    wk0 = t.isocalendar()[1]
    rows = []
    for k in sorted(main_eod):
        w, s, z = k
        data_i = i
        if w == "HK30" and t == dt.date(2026, 10, 19):
            data_i = DI[dt.date(2026, 10, 17)]     # SAP consumed the stale 3PL feed
        lab = int(main_eod[k][data_i])
        if k in tib_blocked:
            lab = int(sum(a[data_i] for a in tib_batch_eod[k].values()))
        blk = int(tib_blocked[k][data_i]) if k in tib_blocked else 0
        qm = int(qm_eod[k][data_i]) if k in qm_eod else 0
        web = int(web_eod[k][data_i]) if k in web_eod else 0
        od = int(open_orders[k][data_i]) if k in open_orders else 0
        if main_eod[k][:i + 1].max() == 0 and not po_by_key.get(k):
            continue
        rc = defaultdict(int)
        nxt = None
        for r in po_by_key.get(k, []):
            if r["LAST_GR"] and C.d(r["LAST_GR"]) < t:
                continue
            e = eta_known(r, t)
            if e is None:
                continue
            e = max(e, t)
            wk = e.isocalendar()[1]
            qty = r["MENGE"] - (r["WEMNG"] if r["LAST_GR"] and C.d(r["LAST_GR"]) < t else 0)
            rc[wk] += qty
            if nxt is None or e < nxt[0]:
                nxt = (e, qty, r["EBELN"])
        atp_now = max(0, lab - od)
        row = dict(SNAPSHOT=f"{t.isoformat()} 06:00:00", WERKS=w, MATNR=C.matnr(s), J_3ASIZE=z, LABST_0001=lab, OPEN_DLV=od,
                   ECOM_RESERVE_W100=web, BLOCKED_QI=blk + qm, ATP_NOW=atp_now)
        cum = atp_now
        for j in range(6):
            wk = wk0 + j
            cum += rc.get(wk, 0)
            row[f"RCPT_W{wk}"] = rc.get(wk, 0)
            row[f"ATP_CUM_W{wk}"] = cum
        later = sum(v for wk, v in rc.items() if wk >= wk0 + 6)
        row["RCPT_LATER"] = later
        row["NEXT_RCPT_DATE"] = nxt[0].isoformat() if nxt else ""
        row["NEXT_RCPT_QTY"] = nxt[1] if nxt else ""
        row["NEXT_RCPT_PO"] = nxt[2] if nxt else ""
        rows.append(row)
    pd.DataFrame(rows).to_csv(OUT / "atp" / f"ATP_projection_{t:%Y%m%d}.csv", index=False)
print("ATP done")

# =============================================================================== 6. quality + reservations
(OUT / "quality").mkdir(exist_ok=True)
qn = [
    dict(QMNUM=C.VALENTINO_V17["qn"], QMART="Q2", QMTXT="VEL gilet - cursore zip si stacca / non blocca", MATNR="J10911A00305*",
         CHARG=C.VALENTINO_V17["bad_batch"], LIFNR="V100231", ERDAT=C.VALENTINO_V17["qn_created"], PRIOK="1-Very high", STATUS="OSNO ATCO",
         USAGE_DECISION_DATE=C.VALENTINO_V17["usage_decision"], UD_CODE="R-BLK (rejected - block batch)",
         QTY_AFFECTED=int(sum(int(a[-1]) for a in tib_blocked.values())),
         LONGTEXT=f"{C.VALENTINO_V17['defect']}. Rising store returns (reason DEF) since end of September, mostly units delivered from mid-August. "
                  f"Batch {C.VALENTINO_V17['bad_batch']} blocked in all DCs on {C.VALENTINO_V17['usage_decision']}; good batch {C.VALENTINO_V17['good_batch']} released. "
                  "Vendor 8D requested, RTV pending. Store returns to be sent to QM01 (IT10/US20) or QC-HOLD (TKO)."),
    dict(QMNUM="300004571", QMART="Q3", QMTXT="ARTEM - verifica taglie vs scheda tecnica (veste grande)", MATNR="J10911A00577*",
         CHARG="", LIFNR="V100502", ERDAT="2026-09-22", PRIOK="3-Medium", STATUS="NOCO",
         USAGE_DECISION_DATE="2026-10-01", UD_CODE="A (accepted - within tolerance)", QTY_AFFECTED=0,
         LONGTEXT="Stores report ARTEM runs large. Measured 5 pcs/size: chest +1.5 cm vs tech pack, within +/-2 cm tolerance. "
                  "Closed, recommendation to retail: advise one size down. No stock action."),
    dict(QMNUM="300004590", QMART="Q3", QMTXT="NOVA 999 vs 742 mispick MAD01 - verifica ubicazioni", MATNR="J10911A00034999",
         CHARG="", LIFNR="", ERDAT="2026-10-02", PRIOK="2-High", STATUS="NOCO", USAGE_DECISION_DATE="2026-10-06",
         UD_CODE="Internal - bin relabel", QTY_AFFECTED=int(sum(abs(a[4]) for a in S["adjustments"]) // 2),
         LONGTEXT="Bins 03-14-B (NOVA 999) and 03-14-C (NOVA 742) labels swapped after re-slotting on Sep 21. Two deliveries to "
                  "Madrid Serrano (store 1501) picked navy instead of black. Cycle count 06/10 posted differences 701/702. "
                  "Store keeps navy until next delivery; credit/return to be agreed with retail ops."),
    dict(QMNUM="300004602", QMART="F2", QMTXT="ASTRA - customer feedback fit small (EU)", MATNR="G20921A0090*",
         CHARG="", LIFNR="V100610", ERDAT="2026-10-07", PRIOK="3-Medium", STATUS="OSNO", USAGE_DECISION_DATE="",
         UD_CODE="", QTY_AFFECTED=0,
         LONGTEXT="Retail EU/US: clients find Astra Oversized jacket smaller than expected. Fit check requested. Asia not complaining."),
    dict(QMNUM="300004611", QMART="Q3", QMTXT="Cartone danneggiato in ricevimento - CAMILLA 20D", MATNR="J20931A00560020D",
         CHARG="", LIFNR="V100502", ERDAT="2026-10-09", PRIOK="4-Low", STATUS="NOCO", USAGE_DECISION_DATE="2026-10-12",
         UD_CODE="A (accepted)", QTY_AFFECTED=3, LONGTEXT="Outer carton crushed, garments ok after inspection."),
]
pd.DataFrame(qn).to_csv(OUT / "quality" / "QMEL_quality_notifications.csv", index=False)

qrows = []
rma = 610000
for r in sd.itertuples():
    rma += 1
    qrows.append(dict(RMA=f"RMA{rma}", SOURCE="STORE", SOURCE_ID=C.SAP_WERKS[r.store_id], POS_RECEIPT=r.receipt_id, RETURN_DATE=r.return_date,
                      DC=r.werks, DC_RECEIPT_DATE=r.dc_receipt.isoformat() if isinstance(r.dc_receipt, dt.date) else "",
                      STATUS="IN_QM01" if isinstance(r.dc_receipt, dt.date) else "IN_TRANSIT_TO_DC",
                      MATNR=C.matnr(r.sku), J_3ASIZE=r.size, CHARG=C.VALENTINO_V17["bad_batch"], QTY=int(r.qty), DEFECT_CODE="ZIP-SLD-01",
                      DISPOSITION="RTV_PENDING_8D"))
er = pd.read_csv(C.CACHE / "ecom_returns_units.csv", dtype={"size": str})
for r in er[er.reason == "DEFECTIVE"].itertuples():
    rma += 1
    w = NODEW[CC_NODE.get(r.country, "EMEA")]
    lag = 4 if w != "HK30" else 6
    rd = C.d(r.date) + dt.timedelta(days=lag)
    qrows.append(dict(RMA=f"RMA{rma}", SOURCE="ECOM", SOURCE_ID=f"WEB-{r.country}", POS_RECEIPT="", RETURN_DATE=r.date, DC=w,
                      DC_RECEIPT_DATE=rd.isoformat() if rd <= C.LAST_DAY else "", STATUS="IN_QM01" if rd <= C.LAST_DAY else "IN_TRANSIT_TO_DC",
                      MATNR=C.matnr(r.sku), J_3ASIZE=r.size, CHARG="", QTY=int(r.qty), DEFECT_CODE="ZIP-SLD-01" if R.random() < 0.8 else "",
                      DISPOSITION="RTV_PENDING_8D"))
pd.DataFrame(qrows).to_csv(OUT / "quality" / "quarantine_returns_detail.csv", index=False)

# reservations (RESB-like, custom Z table export)
res = []
rs = [1004410]


def addres(**kw):
    rs[0] += int(R.integers(1, 6))
    res.append(dict(RSNUM=str(rs[0]), **kw))


addres(RTYPE="PR_SAMPLE", WERKS="HK30", MATNR="J20931A00618510", J_3ASIZE="0", QTY=1, CREATED="2026-10-05", NEEDED="2026-10-09",
       REQUESTER="PR APAC (Seoul)", STATUS="REJECTED_NO_STOCK", STATUS_DATE="2026-10-05",
       TEXT="Gifting for LUMIERE / Yoon Ha-eun agency - rejected, ATP 0 at HK30. Not re-submitted.")
addres(RTYPE="PR_SAMPLE", WERKS="IT10", MATNR="J20931A00618510", J_3ASIZE="00", QTY=2, CREATED="2026-10-12", NEEDED="2026-10-15",
       REQUESTER="PR Milano", STATUS="ISSUED", STATUS_DATE="2026-10-14", TEXT="Press samples Vogue Italia / editorial pull")
for sid, sku_, z, q in [("LON01", "J20931A00622999", "1", 2), ("LON01", "J20931A00622023R" if False else "J20931A0062223R", "2", 1),
                        ("LON01", "J20931A00087999", "1", 2), ("LON01", "J10911A00577999", "4", 2), ("LON01", "G20921A00901999", "M", 1),
                        ("LON01", "J20931A00618510", "1", 1), ("LON01", "J10911A00034999", "3", 2)]:
    addres(RTYPE="EVENT", WERKS="IT10", MATNR=sku_, J_3ASIZE=z, QTY=q, CREATED="2026-09-25", NEEDED="2026-10-06",
           REQUESTER=f"Retail UK - {C.SAP_WERKS[sid]} client evening 08/10", STATUS="ISSUED" if sku_ != "J20931A00618510" else "CANCELLED",
           STATUS_DATE="2026-10-02", TEXT="Event stock, return to DC by 16/10 if unsold" if sku_ != "J20931A00618510" else "no ATP")
for sid in ["PAR01", "MIL01", "LON02", "PAR02"]:
    for z in ["0", "1", "2"]:
        created = dt.date(2026, 9, 19) + dt.timedelta(days=int(R.integers(0, 9)))
        addres(RTYPE="STORE_BACKORDER", WERKS="IT10", MATNR="J20931A00012999", J_3ASIZE=z, QTY=int(R.integers(2, 7)),
               CREATED=created.isoformat(), NEEDED=(created + dt.timedelta(days=3)).isoformat(),
               REQUESTER=f"Store {C.SAP_WERKS[sid]}", STATUS="OPEN" if sid != "MIL01" or z != "1" else "OPEN",
               STATUS_DATE=created.isoformat(), TEXT="manual request - clients asking black Aurea")
for sid in ["SEL01", "SEL02", "TYO01", "SHA01", "HKG01"]:
    for z in ["0", "1"]:
        created = dt.date(2026, 10, 2) + dt.timedelta(days=int(R.integers(0, 4)))
        addres(RTYPE="STORE_BACKORDER", WERKS="HK30", MATNR="J20931A00618510", J_3ASIZE=z, QTY=int(R.integers(5, 16)),
               CREATED=created.isoformat(), NEEDED=(created + dt.timedelta(days=4)).isoformat(), REQUESTER=f"Store {C.SAP_WERKS[sid]}",
               STATUS="PARTIALLY_CONFIRMED" if R.random() < 0.6 else "OPEN", STATUS_DATE="2026-10-09", TEXT="pink IRIDIA waitlist")
addres(RTYPE="STORE_BACKORDER", WERKS="IT10", MATNR="I10919B00011999", J_3ASIZE="M", QTY=4, CREATED="2026-10-09", NEEDED="2026-10-12",
       REQUESTER=f"Store {C.SAP_WERKS['MIL01']}", STATUS="OPEN", STATUS_DATE="2026-10-09", TEXT="cardigan logo M - clienti in attesa")
addres(RTYPE="VIC_HOLD", WERKS="IT10", MATNR="J20931A0062223R", J_3ASIZE="1", QTY=1, CREATED="2026-09-24", NEEDED="2026-09-26",
       REQUESTER=f"Store {C.SAP_WERKS['MIL01']}", STATUS="REJECTED_NO_STOCK", STATUS_DATE="2026-09-25", TEXT="VIC - Amalia marrone tg 1")
addres(RTYPE="ECOM_RESERVE", WERKS="HK30", MATNR="J20931A00618510", J_3ASIZE="*", QTY=C.ILVARO_TOPUP_ECOM_RESERVE["HK30"],
       CREATED="2026-10-06", NEEDED="2026-10-09", REQUESTER="E-commerce APAC", STATUS="ISSUED", STATUS_DATE="2026-10-09", TEXT="top-up share web")
addres(RTYPE="ECOM_RESERVE", WERKS="IT10", MATNR="J20931A00618510", J_3ASIZE="*", QTY=C.ILVARO_TOPUP_ECOM_RESERVE["IT10"],
       CREATED="2026-10-06", NEEDED="2026-10-09", REQUESTER="E-commerce EU", STATUS="ISSUED", STATUS_DATE="2026-10-09", TEXT="")
addres(RTYPE="ECOM_RESERVE", WERKS="US20", MATNR="J20931A00618510", J_3ASIZE="*", QTY=C.ILVARO_TOPUP_ECOM_RESERVE["US20"],
       CREATED="2026-10-06", NEEDED="2026-10-09", REQUESTER="E-commerce US", STATUS="ISSUED", STATUS_DATE="2026-10-09", TEXT="")
(OUT / "reservations").mkdir(exist_ok=True)
pd.DataFrame(res).to_csv(OUT / "reservations" / "ZRESV_reservations_export.csv", index=False)

# store / plant master for WMS
pm = []
for w, dcname in (("IT10", "DC-IT-CSG"), ("US20", "DC-US-NJ"), ("HK30", "DC-HK-TKO")):
    for lg, txt in (("0001", "Magazzino principale / Main"), ("W100", "Riserva e-commerce"), ("QM01", "Blocco qualita"),
                    ("RT01", "Resi da grading"), ("OUT1", "Stock lot / outlet")):
        pm.append(dict(WERKS=w, NAME1=C.DCS[dcname]["name"], LGORT=lg, LGOBE=txt, OPERATOR=C.DCS[dcname]["operator"]))
pd.DataFrame(pm).to_csv(OUT / "T001L_plants_storage_locations.csv", index=False)
print("quality/reservations done")
