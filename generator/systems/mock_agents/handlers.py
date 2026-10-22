"""Business logic of the mock agents (warehouse / logistics / marketing / planning).

Only reads files under generated/sources/ (what hackathon teams receive). Every handler accepts an `as_of`
date so that past behaviour can be replayed (the conversation log was produced with these functions).
"""
from __future__ import annotations

import datetime as dt
import glob
import json
import math
import zlib
import os
from functools import lru_cache
from pathlib import Path

import pandas as pd

ROOT = Path(os.environ.get("DATA_ROOT", Path(__file__).resolve().parents[3] / "generated" / "sources"))
SYS = ROOT / "systems"
INT = ROOT / "erp"
TODAY = dt.date(2026, 10, 22)


def _d(x):
    if x is None:
        return TODAY
    return x if isinstance(x, dt.date) and not isinstance(x, dt.datetime) else dt.date.fromisoformat(str(x)[:10])


# ------------------------------------------------------------------ shared master data / id mapping
@lru_cache
def stores():
    return pd.read_csv(INT / "master_data" / "stores.csv").set_index("store_id")


@lru_cache
def werks_map():
    p = pd.read_csv(SYS / "planning" / "replenishment_parameters_stores.csv", sep=";", dtype=str)
    return dict(zip(p.STORE_ID, p.WERKS)), dict(zip(p.WERKS, p.STORE_ID))


def to_store(code: str) -> str:
    """Accepts internal id (MIL01), SAP plant (1001) or TMS ship-to (0000071001)."""
    s2w, w2s = werks_map()
    code = str(code).strip()
    if code in s2w:
        return code
    if code in w2s:
        return w2s[code]
    if code.startswith("00000") and code[-4:] in w2s:
        return w2s[code[-4:]]
    raise KeyError(f"unknown store code {code}")


def to_werks(code: str) -> str:
    if code in ("IT10", "US20", "HK30"):
        return code
    return werks_map()[0][to_store(code)]


def norm_material(m: str) -> str:
    """J20931A00012-999 / J20931A00012999 / J20931A00012-999-1 -> J20931A00012999"""
    m = m.replace("-", "")
    return m[:15]


# ------------------------------------------------------------------ WAREHOUSE
@lru_cache
def _atp_files():
    out = {}
    for f in glob.glob(str(SYS / "warehouse" / "atp" / "ATP_projection_*.csv")):
        out[dt.datetime.strptime(Path(f).stem[-8:], "%Y%m%d").date()] = f
    return dict(sorted(out.items()))


@lru_cache
def _atp(snap):
    return pd.read_csv(_atp_files()[snap], dtype={"J_3ASIZE": str, "MATNR": str, "NEXT_RCPT_PO": str})


def wh_atp(plant: str, material: str, as_of=None, size: str | None = None, include_blocked_bug: bool = False):
    as_of = _d(as_of)
    snaps = [s for s in _atp_files() if s <= as_of]
    if not snaps:
        return {"error": "NO_SNAPSHOT", "message": f"no ATP snapshot available on or before {as_of}"}
    snap = snaps[-1]
    df = _atp(snap)
    mat = norm_material(material)
    plants = ["IT10", "US20", "HK30"] if plant in (None, "", "*", "ALL") else [plant]
    rows = df[(df.MATNR == mat) & (df.WERKS.isin(plants))]
    if size:
        rows = rows[rows.J_3ASIZE == size]
    res = []
    for r in rows.itertuples():
        atp = int(r.ATP_NOW) + (int(r.BLOCKED_QI) if include_blocked_bug else 0)
        res.append({"plant": r.WERKS, "material": r.MATNR, "size": r.J_3ASIZE, "unrestricted": int(r.LABST_0001),
                    "openDeliveries": int(r.OPEN_DLV), "ecomReserve": int(r.ECOM_RESERVE_W100), "blocked": int(r.BLOCKED_QI),
                    "atp": atp, "nextReceipt": ({"date": r.NEXT_RCPT_DATE, "qty": int(r.NEXT_RCPT_QTY), "po": r.NEXT_RCPT_PO}
                                                if isinstance(r.NEXT_RCPT_DATE, str) and r.NEXT_RCPT_DATE else None)})
    return {"snapshot": f"{snap}T06:00:00", "asOf": str(as_of), "stale": (as_of - snap).days > 1, "positions": res,
            "totalAtp": sum(p["atp"] for p in res)}


@lru_cache
def _po():
    return pd.read_csv(SYS / "warehouse" / "inbound" / "EKPO_EKET_purchase_orders_FW26.csv", dtype=str)


@lru_cache
def _cdpos():
    return pd.read_csv(SYS / "warehouse" / "inbound" / "CDPOS_po_delivery_date_changes.csv", dtype=str)


def wh_po(ebeln: str, as_of=None):
    as_of = _d(as_of)
    po = _po()
    rows = po[po.EBELN == ebeln]
    if rows.empty:
        return {"error": "NOT_FOUND"}
    ch = _cdpos()
    ch = ch[(ch.OBJECTID == ebeln) & (ch.UDATE <= str(as_of))].sort_values("UDATE")
    eta = rows.EINDT_ORIG.iloc[0]
    for r in ch.itertuples():
        if r.WERKS in ("*",):
            eta = f"{r.VALUE_NEW[:4]}-{r.VALUE_NEW[4:6]}-{r.VALUE_NEW[6:]}"
    lines = rows.groupby(["EBELP", "WERKS", "MATNR"]).agg(qty=("MENGE", lambda x: sum(int(v) for v in x)),
                                                           gr=("LAST_GR", "first")).reset_index()
    out = []
    for r in lines.itertuples():
        received = isinstance(r.gr, str) and r.gr and r.gr <= str(as_of)
        out.append({"item": r.EBELP, "plant": r.WERKS, "material": r.MATNR, "qty": r.qty, "status": "RECEIVED" if received else "OPEN",
                    "goodsReceipt": r.gr if received else None})
    return {"purchaseOrder": ebeln, "vendor": rows.NAME1.iloc[0], "createdOn": rows.BEDAT.iloc[0], "headerEta": eta, "asOf": str(as_of),
            "lines": out, "changes": [{"date": r.UDATE, "old": r.VALUE_OLD, "new": r.VALUE_NEW, "note": r.NOTE if isinstance(r.NOTE, str) else ""}
                                      for r in ch.itertuples()]}


def wh_reservation(plant, material, size, qty, purpose, as_of=None):
    a = wh_atp(plant, material, as_of, size)
    avail = a.get("totalAtp", 0)
    if avail >= qty:
        return {"status": "CONFIRMED", "reservation": f"10044{zlib.crc32(repr((plant, material, size, str(as_of))).encode()) % 100000:05d}", "qty": qty,
                "atpBefore": avail, "purpose": purpose}
    return {"status": "REJECTED_NO_STOCK", "atp": avail, "purpose": purpose,
            "nextReceipt": (a["positions"][0]["nextReceipt"] if a.get("positions") else None)}


# ------------------------------------------------------------------ LOGISTICS
@lru_cache
def _lanes():
    return pd.read_csv(SYS / "logistics" / "lane_matrix_lead_time_cost.csv", dtype={"origin": str, "dest": str})


@lru_cache
def _tracking():
    rows = [json.loads(l) for l in open(SYS / "logistics" / "carrier_tracking_events.jsonl", encoding="utf-8")]
    return pd.DataFrame(rows)


@lru_cache
def _tms():
    return pd.read_csv(SYS / "logistics" / "tms_shipments.csv", dtype=str)


def lg_tracking(ref: str, as_of_utc: str | None = None):
    tms = _tms()
    m = tms[(tms.awb == ref) | (tms.shipment_ref == ref) | (tms.delivery_vbeln == ref)]
    if m.empty:
        return {"error": "NOT_FOUND", "reference": ref}
    awb = m.awb.iloc[0]
    ev = _tracking()
    ev = ev[ev.tracking_number == awb].drop_duplicates(subset=["carrier_event_code", "event_time_utc"]).sort_values("event_time_utc")
    if as_of_utc:
        ev = ev[ev.event_time_utc <= as_of_utc]
    return {"awb": awb, "carrier": m.carrier.iloc[0], "shipmentRef": m.shipment_ref.iloc[0], "delivery": m.delivery_vbeln.iloc[0],
            "plannedDelivery": m.planned_delivery.iloc[0], "carrierEdd": m.carrier_edd.iloc[0],
            "status": ev.normalized_status.iloc[-1] if len(ev) else "UNKNOWN",
            "events": ev[["event_time_utc", "normalized_status", "carrier_event_code", "carrier_event_desc", "location_city"]].to_dict("records")}


def lg_lane(origin: str, dest: str):
    lanes = _lanes()
    o = origin if origin in ("IT10", "US20", "HK30") else to_werks(origin)
    d_ = to_werks(dest)
    r = lanes[(lanes.origin == o) & (lanes.dest == d_)]
    if r.empty:
        return {"error": "NO_LANE"}
    return {k: (None if (isinstance(v, float) and math.isnan(v)) else v) for k, v in r.iloc[0].to_dict().items()}


def _store_stock(store, sku, size, day):
    f = INT / "inventory" / "store_stock_daily" / f"stock_eod_{day}.csv"
    if not f.exists():
        return None
    s = pd.read_csv(f, dtype={"size": str})
    r = s[(s.store_id == store) & (s.sku == sku) & (s["size"] == size)]
    return int(r.on_hand.iloc[0]) if len(r) else 0


def _closed(store, day):
    if store == "COU01" and dt.date(2026, 9, 13) <= day <= dt.date(2026, 11, 26):
        return "store closed for the season"
    if store == "STM01" and day >= dt.date(2026, 10, 19):
        return "store closed (Zwischensaison)"
    if store == "CRT01" and day.month == 10 and day.weekday() < 4:
        return "store open Fri-Sun only in October"
    return None


def lg_transfer_request(source: str, dest: str, sku: str, size: str, qty: int, requested_at_local: str, required_by: str | None = None):
    """IBT feasibility. requested_at_local: ISO datetime in the SOURCE store local time."""
    src, dst = to_store(source), to_store(dest)
    t = dt.datetime.fromisoformat(requested_at_local)
    lane = lg_lane(src, dst)
    if "error" in lane:
        return {"status": "REJECTED", "reason": "NO_LANE"}
    allowed = str(lane["ibt_allowed"])
    if not allowed.startswith("Y"):
        return {"status": "REJECTED", "reason": "IBT_NOT_ALLOWED", "detail": allowed}
    c = _closed(src, t.date())
    if c:
        return {"status": "REJECTED", "reason": "SOURCE_CLOSED", "detail": c}
    stock_day = (t.date() - dt.timedelta(days=1)).isoformat()
    sku_c = sku if sku.count("-") == 1 else "-".join(sku.split("-")[:2])
    on_hand = _store_stock(src, sku_c, size, stock_day)
    if on_hand is not None and on_hand < qty:
        return {"status": "REJECTED", "reason": "NO_STOCK_AT_SOURCE", "sourceOnHand": on_hand, "stockSnapshot": stock_day}
    hh, mm = map(int, str(lane["pickup_cutoff_local"]).split(":"))
    pickup = t.date()
    late = (t.hour, t.minute) > (hh, mm)
    if late or pickup.weekday() >= 5:
        pickup = pickup + dt.timedelta(days=1)
        while pickup.weekday() >= 5:
            pickup += dt.timedelta(days=1)
    transit = int(lane["transit_days_contract"])
    eta = pickup + dt.timedelta(days=transit)
    while eta.weekday() == 6:
        eta += dt.timedelta(days=1)
    cost = round(float(lane["cost_fixed_eur"]) + float(lane["cost_per_unit_eur"]) * qty, 2)
    res = {"status": "ACCEPTED" if not late else "ACCEPTED_NEXT_PICKUP", "lane": lane["lane_id"], "mode": lane["mode"],
           "carrier": lane["default_carrier"], "pickupDate": str(pickup), "eta": str(eta), "transportCostEur": cost,
           "cutoffLocal": lane["pickup_cutoff_local"], "customsRequired": lane["customs_required"]}
    if late:
        res["note"] = f"request at {t:%H:%M} after pickup cut-off {lane['pickup_cutoff_local']}; first pickup {pickup}"
    if required_by and eta > _d(required_by):
        res.update(status="REJECTED", reason="CUTOFF_MISSED" if late else "CANNOT_MEET_DATE",
                   detail=f"earliest delivery {eta} is after required date {required_by}")
    return res


# ------------------------------------------------------------------ MARKETING
@lru_cache
def _calendar():
    return pd.read_excel(SYS / "marketing" / "campaign_calendar_FW26.xlsx", sheet_name="List").dropna(subset=["ID"])


def mk_calendar(market: str | None = None, date_from=None, date_to=None):
    c = _calendar()
    if market:
        c = c[c.Market.str.contains(market, case=False, na=False) | c.Market.str.contains("Global", na=False)]
    if date_from:
        c = c[c.End >= str(date_from)]
    if date_to:
        c = c[c.Start <= str(date_to)]
    return {"activities": c.fillna("").to_dict("records")}


@lru_cache
def _waitlist():
    return pd.read_csv(SYS / "marketing" / "store_waitlist_reservations.csv", dtype=str)


def mk_waitlist(store_crm_code: str | None = None, item: str | None = None, status: str | None = None):
    w = _waitlist()
    if store_crm_code:
        w = w[w.store_code == store_crm_code]
    if item:
        w = w[w["item"].str.contains(item, case=False, na=False)]
    if status:
        w = w[w.status == status]
    return {"count": len(w), "entries": w.fillna("").to_dict("records")[:200]}


DRAFTS = {
    "it": "Gentile {name}, la contattiamo da {store}: {item} taglia {size} {avail}. Saremo lieti di riservarlo per lei {hold}. A presto.",
    "fr": "Chère/Cher {name}, votre boutique {store} vous informe que {item} en taille {size} {avail}. Nous pouvons le réserver {hold}.",
    "en": "Dear {name}, this is {store}: {item} in size {size} {avail}. We would be happy to hold it for you {hold}.",
    "ko": "{name} 고객님, {store}입니다. 문의하신 {item} {size} 사이즈 {avail}. {hold} 보관해 드릴 수 있습니다.",
    "ja": "{name}様 {store}でございます。お問い合わせの{item}（サイズ{size}）{avail}。{hold}お取り置きいたします。",
    "zh": "{name}您好，这里是{store}。您关注的{item} {size}码 {avail}。我们可以为您保留{hold}。",
}
AVAIL = {"it": ("è di nuovo disponibile", "è previsto in arrivo intorno al {eta}"), "fr": ("est de nouveau disponible", "est attendu vers le {eta}"),
         "en": ("is available again", "is expected around {eta}"), "ko": ("재입고되었습니다", "{eta} 경 입고 예정입니다"),
         "ja": ("再入荷いたしました", "{eta}頃入荷予定でございます"), "zh": ("已到货", "预计{eta}左右到货")}
HOLD = {"it": "fino a sabato", "fr": "jusqu'à samedi", "en": "until Saturday", "ko": "토요일까지", "ja": "土曜日まで", "zh": "至本周六"}


def mk_message_draft(client_name: str, store_name: str, language: str, item: str, size: str, available: bool, eta: str | None = None):
    lg = language[:2] if language[:2] in DRAFTS else "en"
    a, b = AVAIL[lg]
    txt = DRAFTS[lg].format(name=client_name, store=store_name, item=item, size=size,
                            avail=a if available else b.format(eta=eta or "?"), hold=HOLD[lg])
    flags = []
    if not available and not eta:
        flags.append("ETA_MISSING: ask warehouse-agent / planning-agent before sending")
    if not available:
        flags.append("NO_STOCK_PROMISE: do not confirm reservation until goods are received in store")
    return {"language": lg, "draft": txt, "complianceFlags": flags, "requiresApproval": True}


# ------------------------------------------------------------------ PLANNING
@lru_cache
def _params():
    return pd.read_csv(SYS / "planning" / "replenishment_parameters_stores.csv", sep=";", dtype=str, decimal=",")


def pl_params(store):
    p = _params()
    r = p[p.WERKS == to_werks(store)]
    return r.iloc[0].fillna("").to_dict() if len(r) else {"error": "NOT_FOUND"}


@lru_cache
def _fcst(run):
    return pd.read_csv(INT / "forecast" / "sku_store_weekly" / f"fcst_sku_store_run_{run}.csv")


def pl_replenishment_proposal(store: str, sku: str, as_of=None, demand_multiplier: float = 1.0, sizes: list | None = None):
    """Order-up-to proposal: target = forecast daily * cover days * safety, minus on hand/in transit, capped by DC ATP."""
    as_of = _d(as_of)
    sid = to_store(store)
    p = pl_params(sid)
    runs = sorted(Path(f).stem[-10:] for f in glob.glob(str(INT / "forecast" / "sku_store_weekly" / "*.csv")))
    run = [r for r in runs if r <= str(as_of)][-1]
    f = _fcst(run)
    f = f[(f.store_id == sid) & (f.sku == sku)]
    cover = int(p["REICHWEITE_TAGE"])
    daily = f.fcst_units.head(max(1, math.ceil(cover / 7))).mean() / 7 if len(f) else 0.0
    stock_day = (as_of - dt.timedelta(days=1)).isoformat()
    s = pd.read_csv(INT / "inventory" / "store_stock_daily" / f"stock_eod_{stock_day}.csv", dtype={"size": str})
    s = s[(s.store_id == sid) & (s.sku == sku)]
    curve = s.set_index("size")
    dc = p["LIEF_WERK"]
    atp = wh_atp(dc, sku, as_of)
    atp_by = {x["size"]: x["atp"] for x in atp.get("positions", [])}
    lines = []
    n = max(len(curve), 1)
    for size, r in curve.iterrows():
        if sizes and size not in sizes:
            continue
        tgt = math.ceil(daily * cover * float(str(p["SAFETY_FACTOR"]).replace(",", ".")) * demand_multiplier / n + 0.25)
        need = max(0, tgt - int(r.on_hand) - int(r.in_transit))
        conf = min(need, atp_by.get(size, 0))
        lines.append({"size": size, "onHand": int(r.on_hand), "inTransit": int(r.in_transit), "target": tgt, "proposed": need,
                      "confirmedByDc": conf, "shortfall": need - conf})
    lead = int(p["WBZ_TAGE"])
    return {"store": sid, "werks": p["WERKS"], "sku": sku, "asOf": str(as_of), "forecastRun": run, "coverDays": cover,
            "demandMultiplier": demand_multiplier, "supplyingDc": dc, "atpSnapshot": atp.get("snapshot"),
            "expectedArrival": str(as_of + dt.timedelta(days=1 + lead)), "lines": lines,
            "note": "forecast is statistical (event-blind); pass demand_multiplier to reflect known events"}


@lru_cache
def _alloc():
    a = pd.read_excel(SYS / "planning" / "allocation_plan_FW26_new_products.xlsx", sheet_name="Wave1_0309", dtype={"size": str})
    return a


def pl_allocation(sku: str):
    a = _alloc()
    a = a[a.sku == sku]
    return {"sku": sku, "rows": a.fillna("").to_dict("records")}
