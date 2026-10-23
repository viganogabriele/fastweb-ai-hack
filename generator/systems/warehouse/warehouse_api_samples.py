"""Sample API responses of the warehouse systems (SAP OData gateway, internal WMS REST gateway, 3PL portal API)."""
import datetime as dt
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402
import config  # noqa: E402

OUT = C.OUT / "warehouse" / "api_samples"
OUT.mkdir(parents=True, exist_ok=True)
S = pd.read_pickle(C.CACHE / "wms_state.pkl")
DAYS = list(C.daterange("2026-08-01", "2026-10-21"))
DI = {x: i for i, x in enumerate(DAYS)}
sk = C.skus().set_index("sku")
RUN = {s: config.SIZE_RUNS[sk.size_run[s]] for s in sk.index}
ean = C.sku_sizes().set_index(["sku", "size"]).ean
main_eod, web_eod, qm_eod, tib_blocked, rt_eod = S["main_eod"], S["web_eod"], S["qm_eod"], S["tib_blocked"], S["rt_eod"]
oo = S["open_orders"]


def v(store, k, i):
    return int(store[k][i]) if k in store else 0


def dump(name, obj, meta=None):
    with open(OUT / name, "w", encoding="utf-8") as f:
        if meta:
            obj = {"_request": meta, **obj} if isinstance(obj, dict) else obj
        json.dump(obj, f, ensure_ascii=False, indent=2)


def odata_stock(w, sku, day, req_ts):
    i = DI[day]
    res = []
    for z in RUN[sku]:
        k = (w, sku, z)
        for lg, store, typ in (("0001", main_eod, "01"), ("W100", web_eod, "01"), ("RT01", rt_eod, "03"), ("QM01", qm_eod, "07")):
            q = v(store, k, i)
            if q or lg == "0001":
                res.append({"__metadata": {"id": f"https://sapgw.valentino-int.example/sap/opu/odata/sap/API_MATERIAL_STOCK_SRV/A_MatlStkInAcctMod(Material='{C.matnr(sku)}',Plant='{w}',StorageLocation='{lg}',Batch='',Supplier='',Customer='',WBSElementInternalID='00000000',SDDocument='',SDDocumentItem='000000',InventorySpecialStockType='',InventoryStockType='{typ}')",
                                          "type": "API_MATERIAL_STOCK_SRV.A_MatlStkInAcctModType"},
                            "Material": C.matnr(sku), "Plant": w, "StorageLocation": lg, "Batch": "", "Supplier": "", "Customer": "",
                            "WBSElementInternalID": "00000000", "SDDocument": "", "SDDocumentItem": "000000",
                            "InventorySpecialStockType": "", "InventoryStockType": typ, "J_3ASIZE": z,
                            "MatlWrhsStkQtyInMatlBaseUnit": f"{q:.3f}", "MaterialBaseUnit": "ST"})
    return {"d": {"results": res}}


# 1-2 SAP OData stock for AUREA black at IT10 before / after the receipt
for day, ts in ((dt.date(2026, 10, 15), "2026-10-15T07:02:11+02:00"), (dt.date(2026, 10, 16), "2026-10-17T07:01:40+02:00"),
                (dt.date(2026, 10, 20), "2026-10-21T08:15:03+02:00")):
    dump(f"sap_odata_A_MatlStkInAcctMod_IT10_J20931A00012999_{ts[:10].replace('-', '')}.json",
         odata_stock("IT10", "J20931A00012-999", day, ts),
         {"method": "GET", "ts": ts, "url": "/sap/opu/odata/sap/API_MATERIAL_STOCK_SRV/A_MatlStkInAcctMod?$filter=Material eq 'J20931A00012999' and Plant eq 'IT10'&$format=json"})
dump("sap_odata_A_MatlStkInAcctMod_IT10_I10919B00011999_20261009.json", odata_stock("IT10", "I10919B00011-999", dt.date(2026, 10, 8), ""),
     {"method": "GET", "ts": "2026-10-09T09:12:55+02:00",
      "url": "/sap/opu/odata/sap/API_MATERIAL_STOCK_SRV/A_MatlStkInAcctMod?$filter=Material eq 'I10919B00011999' and Plant eq 'IT10'&$format=json"})


# 3 internal WMS gateway ATP
def gw_atp(w, sku, t):
    i = DI[t - dt.timedelta(days=1)]
    sizes = []
    for z in RUN[sku]:
        k = (w, sku, z)
        lab = v(main_eod, k, i)
        od = v(oo, k, i)
        nxt = []
        for po in C.KEY_POS:
            for ln in po["lines"]:
                lsku = ln.get("sku", po["sku"])
                if ln["werks"] == w and lsku == sku and (not po.get("size") or po["size"] == z) and \
                        (not po.get("sizes") or z in po["sizes"]):
                    if ln.get("gr") and C.d(ln["gr"]) < t:
                        continue
                    e = C.po_line_eta_known(po, ln, t)
                    if e:
                        nxt.append({"purchaseOrder": po["ebeln"], "item": ln["ebelp"], "eta": e.isoformat(),
                                    "qtyAllSizes": ln["qty"], "confirmation": "VENDOR_CONFIRMED" if len(po["revisions"]) > 1 else "PO_DATE"})
        sizes.append({"size": z, "ean": ean[(sku, z)], "onHandUnrestricted": lab, "openDeliveries": od,
                      "ecomReserve": v(web_eod, k, i), "blocked": v(tib_blocked, k, i) + v(qm_eod, k, i),
                      "returnsUngraded": v(rt_eod, k, i), "atp": max(0, lab - od), "nextReceipts": nxt})
    return {"plant": w, "material": C.matnr(sku), "sku": sku, "styleName": C.STYLE_NAME[sku.split('-')[0]],
            "asOf": f"{t.isoformat()}T06:00:00" + {"IT10": "+02:00", "US20": "-04:00", "HK30": "+08:00"}[w],
            "uom": "PC", "sizes": sizes, "source": "wms-gateway/v1 (SAP + PCL feed)"}


for w, sku, t in (("HK30", "J20931A00618-510", dt.date(2026, 10, 22)), ("IT10", "J20931A00618-510", dt.date(2026, 10, 22)),
                  ("IT10", "J20931A00012-999", dt.date(2026, 9, 21)), ("IT10", "J20931A00012-999", dt.date(2026, 10, 5)),
                  ("IT10", "J20931A00622-23R", dt.date(2026, 10, 12)), ("IT10", "J20931A00618-999", dt.date(2026, 10, 22)),
                  ("HK30", "J20931A00618-510", dt.date(2026, 10, 5))):
    dump(f"wmsgw_GET_atp_{w}_{C.matnr(sku)}_{t:%Y%m%d}.json", gw_atp(w, sku, t),
         {"method": "GET", "url": f"https://wms-gw.valentino-int.example/v1/atp?plant={w}&material={C.matnr(sku)}", "ts": f"{t.isoformat()}T06:30:00Z"})

# 4 3PL portal API (camelCase, HKT)
def pcl_inv(sku, i, gen_ts, as_of):
    items = []
    for z in RUN[sku]:
        k = ("HK30", sku, z)
        q = v(main_eod, k, i)
        items.append({"itemCode": C.pcl_item_code(sku, z), "barcode": ean[(sku, z)], "lotNo": None,
                      "locations": [{"locType": "PICK", "onHand": q if q <= 6 else round(q * 0.3)},
                                    {"locType": "RESERVE", "onHand": 0 if q <= 6 else q - round(q * 0.3)},
                                    {"locType": "ECOM", "onHand": v(web_eod, k, i)}],
                      "allocated": v(oo, k, i), "available": max(0, q - v(oo, k, i))})
    return {"status": "OK", "site": "TKO-3", "client": "MONC01", "generatedAt": gen_ts, "dataAsOf": as_of, "items": items}


dump("pcl_api_v2_inventory_MC1A00618510_20261022.json",
     pcl_inv("J20931A00618-510", DI[dt.date(2026, 10, 21)], "2026-10-22T06:11:42+08:00", "2026-10-21T23:59:59+08:00"),
     {"method": "GET", "url": "https://portal.pacificcrest-3pl.example/api/v2/inventory?client=MONC01&style=1A00618&color=510"})
stale = pcl_inv("J20931A00012-999", DI[dt.date(2026, 10, 17)], "2026-10-18T06:09:12+08:00", "2026-10-17T23:59:59+08:00")
stale["warnings"] = ["SNAPSHOT_NOT_REFRESHED: last successful WMS extract 2026-10-17 23:59 HKT"]
dump("pcl_api_v2_inventory_MC1A00012999_20261018_STALE.json", stale,
     {"method": "GET", "url": "https://portal.pacificcrest-3pl.example/api/v2/inventory?client=MONC01&style=1A00012&color=999"})
dump("pcl_api_v2_error_429.json", {"status": "ERROR", "code": 429, "message": "Too many requests - limit 60/min per client key",
                                   "retryAfterSec": 37, "traceId": "pcl-7f3a-22c1"},
     {"method": "GET", "ts": "2026-10-19T09:00:41+08:00", "url": "/api/v2/inventory?client=MONC01"})
dump("sap_gateway_error_503.json", {"error": {"code": "/IWFND/CM_BEC/026", "message": {"lang": "en", "value":
      "SAP backend system maintenance window (Sun 02:00-05:00 CET). Retry later."},
      "innererror": {"transactionid": "7A1C3E99F0E10000E00611AB2D0F2C11", "timestamp": "20261018013012.4410000"}}},
     {"method": "GET", "ts": "2026-10-18T03:30:12+02:00", "url": "/sap/opu/odata/sap/API_MATERIAL_STOCK_SRV/A_MatlStkInAcctMod"})

# 5 inbound PO with change history
for po in C.KEY_POS:
    lines = []
    for ln in po["lines"]:
        lines.append({"item": ln["ebelp"], "plant": ln["werks"], "material": C.matnr(ln.get("sku", po["sku"].split("|")[0])),
                      "sizes": po.get("sizes") or ([po["size"]] if po.get("size") else "ALL"), "qty": ln["qty"],
                      "currentDeliveryDate": (C.po_line_eta_known(po, ln, C.TODAY) or "").__str__(),
                      "goodsReceiptDate": ln.get("gr"), "status": "RECEIVED" if ln.get("gr") else "OPEN"})
    dump(f"wmsgw_GET_inbound_po_{po['ebeln']}.json",
         {"purchaseOrder": po["ebeln"], "vendor": {"id": po["vendor"], "name": C.VENDORS[po["vendor"]]}, "createdOn": po["created"],
          "lines": lines, "deliveryDateHistory": [{"changedOn": u, "newDate": e, "comment": n} for u, e, n in po["revisions"]]},
         {"method": "GET", "url": f"https://wms-gw.valentino-int.example/v1/inbound/purchase-orders/{po['ebeln']}", "ts": "2026-10-22T07:05:00Z"})

# 6 quality stock VEL
i = DI[dt.date(2026, 10, 21)]
qs = []
for k in sorted(set(tib_blocked) | {k for k in qm_eod if k[1].startswith(C.VALENTINO_V17["sku_prefix"])}):
    w, s, z = k
    b = v(tib_blocked, k, i)
    q = v(qm_eod, k, i)
    if b or q:
        qs.append({"plant": w, "material": C.matnr(s), "size": z, "batch": C.VALENTINO_V17["bad_batch"], "blockedDcStock": b,
                   "returnsInQuality": q, "notification": C.VALENTINO_V17["qn"]})
dump("wmsgw_GET_quality_stock_TIB_20261022.json",
     {"asOf": "2026-10-22T06:00:00+02:00", "notification": {"id": C.VALENTINO_V17["qn"], "createdOn": C.VALENTINO_V17["qn_created"],
                                                             "usageDecisionOn": C.VALENTINO_V17["usage_decision"], "defect": C.VALENTINO_V17["defect"]},
      "positions": qs, "totals": {"blockedDcStock": sum(p["blockedDcStock"] for p in qs), "returnsInQuality": sum(p["returnsInQuality"] for p in qs)}},
     {"method": "GET", "url": "https://wms-gw.valentino-int.example/v1/quality-stock?materialPrefix=J10911A00305", "ts": "2026-10-22T07:06:00Z"})
print("api samples:", len(list(OUT.iterdir())))
