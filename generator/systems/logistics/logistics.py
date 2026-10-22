"""Logistics sources: TMS shipment register, carrier tracking events (visibility platform feed, UTC),
customs declarations, incident tickets (ServiceNow-like), inter-store transfers (IBT) and lane lead-time/cost matrix."""
import datetime as dt
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

R = C.rng("logistics")
OUT = C.OUT / "logistics"
OUT.mkdir(parents=True, exist_ok=True)
UTC = ZoneInfo("UTC")
NOW_UTC = dt.datetime(2026, 10, 22, 6, 0, tzinfo=UTC)

st = C.stores().set_index("store_id")
sk = C.skus().set_index("sku")
SH = C.shipments()
LAUNCH = json.load(open(C.CACHE / "launch_shipments.json"))
DCW = {"DC-IT-CSG": "IT10", "DC-US-NJ": "US20", "DC-HK-TKO": "HK30"}
W_TZ = {"IT10": "Europe/Rome", "US20": "America/New_York", "HK30": "Asia/Hong_Kong"}
W_CITY = {"IT10": ("Castel San Giovanni", "IT"), "US20": ("Secaucus NJ", "US"), "HK30": ("Tseung Kwan O", "HK")}
W_LL = {"IT10": (45.06, 9.43), "US20": (40.79, -74.06), "HK30": (22.31, 114.26)}
EU = {"IT", "FR", "DE", "ES", "NL", "DK"}
GW = {"IT": ("Milano Malpensa", "MXP"), "FR": ("Paris Roissy", "CDG"), "DE": ("Leipzig Hub", "LEJ"), "GB": ("East Midlands", "EMA"),
      "ES": ("Madrid", "MAD"), "NL": ("Amsterdam", "AMS"), "DK": ("Copenhagen", "CPH"), "CH": ("Basel", "BSL"), "AE": ("Dubai", "DXB"),
      "US": ("Memphis Hub", "MEM"), "CA": ("Toronto", "YYZ"), "JP": ("Tokyo Narita", "NRT"), "KR": ("Incheon", "ICN"),
      "CN": ("Shanghai Pudong", "PVG"), "HK": ("Hong Kong", "HKG"), "TW": ("Taipei Taoyuan", "TPE"), "SG": ("Singapore Changi", "SIN"),
      "AU": ("Sydney", "SYD")}
CN_GW = {"SHA01": ("Shanghai Pudong", "PVG"), "BJS01": ("Beijing Capital", "PEK"), "CDU01": ("Chengdu Tianfu", "TFU")}
JP_GW = {"OSA01": ("Osaka Kansai", "KIX")}
DEPT_STORE = {"MIL02": "RINASCENTE RICEVIMENTO MERCI", "PAR02": "GALERIES LAFAYETTE QUAI 3", "LON02": "HARRODS GOODS IN",
              "BER01": "KADEWE WARENANNAHME", "SEL02": "HYUNDAI 물류 검수", "BUS01": "SHINSEGAE 검수실"}


def store_tz(s):
    return ZoneInfo(st.timezone[s])


def loc(city, cc, code=None):
    return {"city": city, "country": cc, "code": code}


def at(day, hh, mm, tz):
    return dt.datetime.combine(C.d(day), dt.time(hh % 24, mm), tzinfo=ZoneInfo(tz) if isinstance(tz, str) else tz) + \
        dt.timedelta(days=hh // 24)


# ------------------------------------------------------------------------------- carrier vocabularies
VOC = {
    "DHL Express": {"PICKED_UP": ("PU", "Shipment picked up"), "ARRIVED_HUB": ("AF", "Arrived at DHL Sort Facility {city}"),
                    "DEPARTED": ("DF", "Departed Facility in {city}"), "PROCESSED": ("PL", "Processed at {city}"),
                    "CUSTOMS_PENDING": ("CR", "Customs status updated"), "CUSTOMS_HOLD": ("OH", "Shipment on hold"),
                    "CUSTOMS_CLEARED": ("CC", "Clearance processing complete at {city}"),
                    "ARRIVED_DELIVERY": ("AR", "Arrived at Delivery Facility in {city}"), "OUT_FOR_DELIVERY": ("WC", "With delivery courier"),
                    "DELIVERED": ("OK", "Delivered - Signed for by: {sig}"), "EXCEPTION": ("MS", "{reason}")},
    "FedEx": {"PICKED_UP": ("PU", "Picked up"), "ARRIVED_HUB": ("AR", "Arrived at FedEx location"), "DEPARTED": ("DP", "Departed FedEx location"),
              "PROCESSED": ("IT", "In transit"), "CUSTOMS_PENDING": ("CD", "Clearance delay - Import"),
              "CUSTOMS_HOLD": ("CD", "Clearance delay - Import"), "CUSTOMS_CLEARED": ("CC", "International shipment release - Import"),
              "ARRIVED_DELIVERY": ("AR", "At local FedEx facility"), "OUT_FOR_DELIVERY": ("OD", "On FedEx vehicle for delivery"),
              "DELIVERED": ("DL", "Delivered"), "EXCEPTION": ("DE", "Delivery exception - {reason}")},
    "UPS": {"PICKED_UP": ("OR", "Origin Scan"), "ARRIVED_HUB": ("AR", "Arrived at Facility"), "DEPARTED": ("DP", "Departed from Facility"),
            "PROCESSED": ("IP", "Processing at UPS Facility"), "CUSTOMS_PENDING": ("I", "Import Scan"), "CUSTOMS_HOLD": ("X", "Exception: held in customs"),
            "CUSTOMS_CLEARED": ("CR", "Your package was released by the clearing agency"), "ARRIVED_DELIVERY": ("AR", "Arrived at Facility"),
            "OUT_FOR_DELIVERY": ("OT", "Out For Delivery Today"), "DELIVERED": ("D", "Delivered"), "EXCEPTION": ("X", "Exception: {reason}")},
    "BRT": {"PICKED_UP": ("RIT", "RITIRATA"), "ARRIVED_HUB": ("ARR", "ARRIVATA IN FILIALE {city}"), "DEPARTED": ("PAR", "PARTITA DA {city}"),
            "PROCESSED": ("TRA", "IN TRANSITO"), "CUSTOMS_PENDING": ("DOG", "IN DOGANA"), "CUSTOMS_HOLD": ("GIA", "GIACENZA DOGANALE"),
            "CUSTOMS_CLEARED": ("SDO", "SDOGANATA"), "ARRIVED_DELIVERY": ("ARR", "ARRIVATA IN FILIALE DI CONSEGNA {city}"),
            "OUT_FOR_DELIVERY": ("INC", "IN CONSEGNA"), "DELIVERED": ("CON", "CONSEGNATA"), "EXCEPTION": ("MCO", "MANCATA CONSEGNA - {reason}")},
    "GEODIS": {"PICKED_UP": ("PEC", "Prise en charge"), "ARRIVED_HUB": ("ARP", "Arrivée plateforme {city}"), "DEPARTED": ("DEP", "Départ plateforme {city}"),
               "PROCESSED": ("TRA", "En transit"), "CUSTOMS_PENDING": ("DOU", "En cours de dédouanement"), "CUSTOMS_HOLD": ("BLQ", "Bloqué en douane"),
               "CUSTOMS_CLEARED": ("DDN", "Dédouané"), "ARRIVED_DELIVERY": ("ARA", "Arrivée agence {city}"),
               "OUT_FOR_DELIVERY": ("ECL", "En cours de livraison"), "DELIVERED": ("LIV", "Livré"), "EXCEPTION": ("INC", "Incident - {reason}")},
    "SF Express": {"PICKED_UP": ("50", "顺丰速运 已收取快件 / Picked up"), "ARRIVED_HUB": ("30", "快件到达 {city} / Arrived"),
                   "DEPARTED": ("31", "快件已发车 {city} / Departed"), "PROCESSED": ("36", "运输中 / In transit"),
                   "CUSTOMS_PENDING": ("70", "清关中 / Customs clearance in progress"), "CUSTOMS_HOLD": ("71", "海关查验 / Customs inspection"),
                   "CUSTOMS_CLEARED": ("72", "清关完成 / Customs cleared"), "ARRIVED_DELIVERY": ("30", "快件到达 {city}营业点 / Arrived at outlet"),
                   "OUT_FOR_DELIVERY": ("44", "派送中 / Out for delivery"), "DELIVERED": ("80", "已签收 / Delivered, signed by {sig}"),
                   "EXCEPTION": ("33", "快件延误 / Delay - {reason}")},
    "Kerry Logistics": {"PICKED_UP": ("PUP", "Shipment picked up"), "ARRIVED_HUB": ("AHB", "Arrived at hub {city}"), "DEPARTED": ("DHB", "Departed hub {city}"),
                        "PROCESSED": ("ITR", "In transit"), "CUSTOMS_PENDING": ("CCP", "Customs clearance in progress"),
                        "CUSTOMS_HOLD": ("CCH", "Customs hold"), "CUSTOMS_CLEARED": ("CCC", "Customs cleared"),
                        "ARRIVED_DELIVERY": ("ADC", "Arrived at delivery centre {city}"), "OUT_FOR_DELIVERY": ("OFD", "Out for delivery"),
                        "DELIVERED": ("POD", "Delivered"), "EXCEPTION": ("EXC", "Exception: {reason}")},
    "Nippon Express": {"PICKED_UP": ("RCV", "Cargo received / 貨物受付"), "ARRIVED_HUB": ("ARR", "Arrived {city}"), "DEPARTED": ("DEP", "Departed {city}"),
                       "PROCESSED": ("TRS", "In transit"), "CUSTOMS_PENDING": ("CUS", "Import customs declaration filed"),
                       "CUSTOMS_HOLD": ("HLD", "Customs hold - {reason}"), "CUSTOMS_CLEARED": ("CLR", "Import customs cleared"),
                       "ARRIVED_DELIVERY": ("ARR", "Arrived delivery depot {city}"), "OUT_FOR_DELIVERY": ("OFD", "Out for delivery"),
                       "DELIVERED": ("POD", "Delivered (POD: {sig})"), "EXCEPTION": ("EXC", "Exception - {reason}")},
}
NORM = {"PICKED_UP": "PICKED_UP", "ARRIVED_HUB": "IN_TRANSIT", "DEPARTED": "IN_TRANSIT", "PROCESSED": "IN_TRANSIT",
        "CUSTOMS_PENDING": "CUSTOMS", "CUSTOMS_HOLD": "CUSTOMS_HOLD", "CUSTOMS_CLEARED": "CUSTOMS",
        "ARRIVED_DELIVERY": "IN_TRANSIT", "OUT_FOR_DELIVERY": "OUT_FOR_DELIVERY", "DELIVERED": "DELIVERED", "EXCEPTION": "EXCEPTION"}

# ------------------------------------------------------------------------------- delay reasons
DELAY_REASON = {
    "SHP02600311": "Adverse weather - typhoon signal no. 8, operations suspended",
    "SHP02600440": "KC certificate missing - import declaration incomplete",
    "SHP02600455": "Selected for customs inspection",
    "SHP02600337": "Recipient requested later delivery slot",
    "SHP02600427": "Missed connection at hub",
    "SHP02600501": "Customs inspection (CIQ) - random check",
    "SHP02600413": "Department store goods-in slot not available",
    "SHP02600323": "Department store goods-in slot not available",
    "SHP02600352": "Department store receiving closed (inventory)",
    "SHP02600351": "Department store goods-in slot not available",
    "SHP02600449": "Missed connection - flight offloaded",
}
GENERIC_DELAYS = ["Missed connection at hub", "Adverse weather", "Vehicle breakdown", "Recipient business closed - reattempt next day",
                  "Address information incomplete", "Volume backlog at hub", "Flight offloaded - capacity", "Customs clearance delay"]


def signer(store_id):
    if store_id in DEPT_STORE:
        return DEPT_STORE[store_id]
    names = [st.store_manager[store_id], st.assistant_manager[store_id]]
    n = str(R.choice(names + ["STORE", "RECEPTION"]))
    if n in ("STORE", "RECEPTION"):
        return n
    parts = n.replace("陳嘉欣 ", "").replace("黃志明 ", "").split()
    if store_id[:3] in ("SEL", "BUS", "TYO", "OSA", "SHA", "BJS", "CDU", "TPE"):
        return n
    return f"{parts[-1].upper()} {parts[0][0]}." if len(parts) > 1 else n.upper()


def timeline(ship_id, w, store, carrier, ship_date, arrive, planned):
    """Returns list of (dt_utc, step, location, extra) for a DC->store shipment."""
    tz_o, tz_d = W_TZ[w], store_tz(store)
    cc = st.country_code[store]
    city = st.city[store]
    pu = at(ship_date, int(R.integers(16, 19)), int(R.integers(0, 60)), tz_o)
    ev = [(pu - dt.timedelta(hours=int(R.integers(3, 7))), "INFO", loc(*W_CITY[w]), None), (pu, "PICKED_UP", loc(*W_CITY[w]), None)]
    end_day = C.d(arrive) if arrive else None
    if end_day:
        dl = at(end_day, int(R.integers(9, 15)), int(R.integers(0, 60)), tz_d)
        ofd = dl - dt.timedelta(minutes=int(R.integers(70, 240)))
    else:
        dl = None
        ofd = at(C.d(planned), 8, int(R.integers(0, 50)), tz_d)
    reason = DELAY_REASON.get(ship_id)
    delayed = arrive and C.d(arrive) > C.d(planned)
    if delayed and not reason:
        reason = str(R.choice(GENERIC_DELAYS))
    o_gw = {"IT10": ("Milano Malpensa", "IT", "MXP"), "US20": ("Newark", "US", "EWR"), "HK30": ("Hong Kong", "HK", "HKG")}[w]
    if w == "IT10" and cc == "IT":
        hub = ("Piacenza" if carrier == "BRT" else "Milano Malpensa", "IT", None)
        ev += [(pu + dt.timedelta(hours=3), "ARRIVED_HUB", loc(*hub), None), (pu + dt.timedelta(hours=6), "DEPARTED", loc(*hub), None)]
        mid = []
    elif store == "HKG01":
        ev += [(pu + dt.timedelta(hours=2), "ARRIVED_HUB", loc("Kwai Chung", "HK"), None)]
        mid = [("PROCESSED", loc("Kwai Chung", "HK"), "Delivery appointment booked (Harbour City loading bay)")]
    else:
        ev += [(pu + dt.timedelta(hours=3, minutes=int(R.integers(0, 50))), "ARRIVED_HUB", loc(*o_gw), None),
               (pu + dt.timedelta(hours=7, minutes=int(R.integers(0, 50))), "DEPARTED", loc(*o_gw), None)]
        if w == "US20" and cc == "US":
            hub = ("Memphis", "US", "MEM") if carrier == "FedEx" else ("Louisville", "US", "SDF")
            mid = [("ARRIVED_HUB", loc(*hub), None), ("DEPARTED", loc(*hub), None), ("PROCESSED", loc("", "US"), None)]
        else:
            g = CN_GW.get(store) or JP_GW.get(store) or GW[cc]
            mid = [("ARRIVED_HUB", loc(g[0], cc, g[1]), None)]
            if cc not in EU or w != "IT10":
                mid += [("CUSTOMS_PENDING", loc(g[0], cc, g[1]), None), ("CUSTOMS_CLEARED", loc(g[0], cc, g[1]), None)]
            if cc in EU and w == "IT10":
                mid = [("PROCESSED", loc("", "IT"), None)] + mid
    # place mid events evenly between last ev and ofd
    t0 = ev[-1][0]
    t_end = ofd - dt.timedelta(hours=2)
    n = len(mid)
    for j, (step, l, extra) in enumerate(mid):
        tj = t0 + (t_end - t0) * (j + 1) / (n + 1)
        ev.append((tj, step, l, extra))
    ev.append((ofd - dt.timedelta(hours=int(R.integers(1, 3))), "ARRIVED_DELIVERY", loc(city, cc), None))
    # delay exception
    if delayed or ship_id in DELAY_REASON:
        if ship_id == "SHP02600440":
            seo, hkt = ZoneInfo("Asia/Seoul"), ZoneInfo("Asia/Hong_Kong")
            ev = ev[:2] + [(dt.datetime(2026, 10, 7, 20, 40, tzinfo=hkt), "ARRIVED_HUB", loc("Hong Kong", "HK", "HKG"), None),
                           (dt.datetime(2026, 10, 7, 23, 5, tzinfo=hkt), "DEPARTED", loc("Hong Kong", "HK", "HKG"), None)]
            ev += [(dt.datetime(2026, 10, 8, 3, 20, tzinfo=seo), "ARRIVED_HUB", loc("Incheon", "KR", "ICN"), None),
                   (dt.datetime(2026, 10, 8, 9, 35, tzinfo=seo), "CUSTOMS_PENDING", loc("Incheon", "KR", "ICN"), None),
                   (dt.datetime(2026, 10, 8, 14, 12, tzinfo=seo), "CUSTOMS_HOLD", loc("Incheon", "KR", "ICN"), "KC certificate missing"),
                   (dt.datetime(2026, 10, 9, 10, 2, tzinfo=seo), "EXCEPTION", loc("Incheon", "KR", "ICN"), "Awaiting documents from shipper (KC 적합성 확인서)"),
                   (dt.datetime(2026, 10, 12, 17, 24, tzinfo=seo), "CUSTOMS_CLEARED", loc("Incheon", "KR", "ICN"), None),
                   (dt.datetime(2026, 10, 13, 7, 5, tzinfo=seo), "ARRIVED_DELIVERY", loc("Seoul Gangnam", "KR"), None)]
        elif ship_id == "SHP02600455":
            seo, hkt = ZoneInfo("Asia/Seoul"), ZoneInfo("Asia/Hong_Kong")
            ev = ev[:2] + [(dt.datetime(2026, 10, 10, 21, 15, tzinfo=hkt), "ARRIVED_HUB", loc("Hong Kong", "HK", "HKG"), None),
                           (dt.datetime(2026, 10, 10, 23, 50, tzinfo=hkt), "DEPARTED", loc("Hong Kong", "HK", "HKG"), None)]
            ev += [(dt.datetime(2026, 10, 11, 4, 10, tzinfo=seo), "ARRIVED_HUB", loc("Incheon", "KR", "ICN"), None),
                   (dt.datetime(2026, 10, 12, 10, 40, tzinfo=seo), "CUSTOMS_PENDING", loc("Incheon", "KR", "ICN"), None),
                   (dt.datetime(2026, 10, 14, 11, 5, tzinfo=seo), "CUSTOMS_HOLD", loc("Incheon", "KR", "ICN"), "Selected for physical inspection"),
                   (dt.datetime(2026, 10, 17, 16, 30, tzinfo=seo), "CUSTOMS_CLEARED", loc("Incheon", "KR", "ICN"), None),
                   (dt.datetime(2026, 10, 18, 7, 30, tzinfo=seo), "ARRIVED_DELIVERY", loc("Seoul Gangnam", "KR"), None)]
        else:
            planned_dt = at(C.d(planned), 11, 0, tz_d)
            ex_t = min(planned_dt, (dl or NOW_UTC) - dt.timedelta(hours=6))
            step = "CUSTOMS_HOLD" if "ustoms" in (reason or "") or "CIQ" in (reason or "") else "EXCEPTION"
            ev.append((ex_t, step, loc(city, cc), reason))
    if end_day:
        ev += [(ofd, "OUT_FOR_DELIVERY", loc(city, cc), None), (dl, "DELIVERED", loc(city, cc), signer(store))]
    else:
        if ofd < NOW_UTC:
            ev.append((ofd, "OUT_FOR_DELIVERY", loc(city, cc), None))
        ev = [e for e in ev if e[0] <= NOW_UTC]
    ev.sort(key=lambda e: e[0])
    return ev


def render(ev, carrier, ref, awb, store, ship_id):
    out = []
    voc = VOC[carrier]
    for (t, step, l, extra) in ev:
        if step == "INFO":
            code, desc, norm = "INF", "Shipment information received", "INFO_RECEIVED"
        else:
            code, desc = voc[step]
            norm = NORM[step]
            desc = desc.format(city=l["city"] or l["country"], sig=extra or "", reason=extra or "")
            if extra and step in ("PROCESSED", "CUSTOMS_HOLD") and "{reason}" not in voc[step][1]:
                desc = f"{desc} - {extra}"
        ts = t.astimezone(UTC)
        ts_str = ts.strftime("%Y-%m-%dT%H:%M:%SZ")
        if carrier == "BRT":
            # BRT feed sends Italian local time but the platform labels it Z
            ts_str = t.astimezone(ZoneInfo("Europe/Rome")).strftime("%Y-%m-%dT%H:%M:%SZ")
        out.append(dict(tracking_number=awb, carrier=carrier, carrier_event_code=code, carrier_event_desc=desc,
                        normalized_status=norm, event_time_utc=ts_str, location_city=l["city"], location_country=l["country"],
                        location_iata=l.get("code"), shipper_reference=ref, consignee_id=C.TMS_SHIPTO[store],
                        _sort=ts, _ship=ship_id))
    return out


# ------------------------------------------------------------------------------- TMS register + tracking
events = []
tms = []
seq = 0
SERVICE = {"DHL Express": "EXPRESS WORLDWIDE", "FedEx": "FEDEX 2DAY / INTL ECONOMY", "UPS": "UPS GROUND / STANDARD",
           "BRT": "BRT EXPRESS", "GEODIS": "GEODIS EUROPE ROAD", "SF Express": "SF INTERNATIONAL STANDARD",
           "Kerry Logistics": "KERRY EXPRESS", "Nippon Express": "NX AIR CONSOL"}


def haversine(a, b):
    la1, lo1 = map(math.radians, a); la2, lo2 = map(math.radians, b)
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def freight_cost(w, store, units):
    dist = haversine(W_LL[w], (st.lat[store], st.lon[store]))
    cc = st.country_code[store]
    fixed = 35 + 0.012 * dist
    per = 0.9 + 0.0009 * dist
    if cc not in EU and not (w == "US20" and cc == "US") and not (w == "HK30" and cc == "HK"):
        fixed += 85
    return round(fixed + per * units, 2)


all_ship = []
for s in SH:
    w = DCW[s["origin"]]
    all_ship.append(dict(ref=s["shipment_id"], vbeln=C.delivery_no(s["shipment_id"]), w=w, store=s["store_id"], carrier=s["carrier"],
                         ship=s["ship_date"], planned=s["planned_arrival"], actual=s["actual_arrival"],
                         units=sum(l["qty_shipped"] for l in s["lines"]), lines=len(s["lines"]), kind="REPLENISHMENT"))
for ls in LAUNCH:
    lead = {"IT10": 1 if st.country_code[ls["store_id"]] == "IT" else 2, "US20": 5, "HK30": 6}[ls["werks"]]
    arr = (C.d(ls["gi_date"]) + dt.timedelta(days=lead)).isoformat()
    all_ship.append(dict(ref=ls["ref"], vbeln=ls["vbeln"], w=ls["werks"], store=ls["store_id"], carrier=ls["carrier"], ship=ls["gi_date"],
                         planned=arr, actual=arr, units=ls["units"], lines=len(ls["lines"]), kind="LAUNCH_ALLOCATION"))

for sh in all_ship:
    seq += 1
    awb = C.awb(sh["ref"] if sh["kind"] == "REPLENISHMENT" else sh["ref"] + f"{seq:05d}", sh["carrier"])
    if sh["kind"] == "LAUNCH_ALLOCATION":
        awb = [l for l in LAUNCH if l["ref"] == sh["ref"]][0]["awb"]
    ev = timeline(sh["ref"], sh["w"], sh["store"], sh["carrier"], sh["ship"], sh["actual"], sh["planned"])
    # shipper reference: some carriers carry the SAP delivery number, others the internal shipment id
    ref = sh["vbeln"] if sh["carrier"] in ("DHL Express", "FedEx", "UPS", "Nippon Express") else sh["ref"]
    if sh["carrier"] == "BRT":
        ref = f"RIF.MITT. {sh['vbeln'][-6:]}"
    rend = render(ev, sh["carrier"], ref, awb, sh["store"], sh["ref"])
    events += rend
    cc = st.country_code[sh["store"]]
    customs = not ((sh["w"] == "IT10" and cc in EU) or (sh["w"] == "US20" and cc == "US") or (sh["w"] == "HK30" and cc == "HK"))
    edd = sh["planned"]
    if sh["ref"] == "SHP02600440":
        edd = "2026-10-08"
    last = rend[-1]
    tms.append(dict(tms_load_id=f"TMS-26-{40000 + seq:06d}", delivery_vbeln=sh["vbeln"], shipment_ref=sh["ref"], load_type=sh["kind"],
                    origin_plant=sh["w"], ship_to=C.TMS_SHIPTO[sh["store"]], dest_plant=C.SAP_WERKS[sh["store"]],
                    dest_city=st.city[sh["store"]], dest_country=cc, carrier=sh["carrier"], service=SERVICE[sh["carrier"]], awb=awb,
                    pickup_date=sh["ship"], planned_delivery=sh["planned"], carrier_edd=edd, delivered_date=sh["actual"] or "",
                    last_status=last["normalized_status"], last_event_utc=last["event_time_utc"], parcels=max(1, math.ceil(sh["units"] / 6)),
                    units=sh["units"], gross_kg=round(sh["units"] * R.uniform(1.1, 1.6), 1), customs_required="Y" if customs else "N",
                    incoterm="DAP" if customs else "", freight_cost_eur=freight_cost(sh["w"], sh["store"], sh["units"])))

# data quality: duplicate webhook deliveries (same event re-sent), a few events with missing location
ev_df = pd.DataFrame(events)
dups = ev_df.sample(frac=0.015, random_state=7)
ev_df = pd.concat([ev_df, dups]).sort_values("_sort", kind="stable")
ev_df["received_at_utc"] = (pd.to_datetime(ev_df._sort) + pd.to_timedelta(R.integers(1, 240, len(ev_df)), unit="m")).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
# out-of-order arrival into the platform: sort by received time (as the platform stores them)
ev_df = ev_df.sort_values("received_at_utc", kind="stable")
ev_df["event_id"] = [f"evt_{abs(C.stable_hash((a, b, c))) % 16**12:012x}" for a, b, c in zip(ev_df.tracking_number, ev_df.carrier_event_code, ev_df.event_time_utc)]
m = R.random(len(ev_df)) < 0.01
ev_df.loc[m, "location_city"] = None
with open(OUT / "carrier_tracking_events.jsonl", "w", encoding="utf-8") as f:
    for r in ev_df.drop(columns=["_sort", "_ship"]).to_dict("records"):
        f.write(json.dumps({k: (None if (isinstance(v, float) and math.isnan(v)) else v) for k, v in r.items()}, ensure_ascii=False) + "\n")
tms_df = pd.DataFrame(tms).sort_values(["pickup_date", "tms_load_id"])
tms_df.to_csv(OUT / "tms_shipments.csv", index=False)
print("tracking events", len(ev_df), "tms", len(tms_df))

# ------------------------------------------------------------------------------- customs declarations
cust = []
BROKER = {"KR": "Hanmi Customs Service (licensed broker)", "JP": "Nippon Express Customs Brokerage", "CN": "Shanghai Waigaoqiao Customs Agency",
          "TW": "Kerry TW Customs", "SG": "SATS Customs Services", "AU": "Nippon Express AU Customs", "CH": "DHL Zollagentur Basel",
          "GB": "DHL UK Customs", "AE": "Dubai Trade Broker LLC", "CA": "FedEx Trade Networks"}
for t in tms:
    if t["customs_required"] != "Y":
        continue
    cc = t["dest_country"]
    sh_ref = t["shipment_ref"]
    lodged = C.d(t["pickup_date"]) + dt.timedelta(days=1)
    status, hold, released = "CLEARED", "", None
    if t["delivered_date"]:
        released = C.d(t["delivered_date"]) - dt.timedelta(days=1 if cc not in ("CN",) else 2)
    if sh_ref == "SHP02600440":
        lodged, status, hold, released = dt.date(2026, 10, 8), "RELEASED_AFTER_HOLD", "Document missing: KC certificate (KC 적합성 확인서) for down-filled garments", dt.date(2026, 10, 12)
    elif sh_ref == "SHP02600455":
        status, hold, released = "RELEASED_AFTER_INSPECTION", "Physical inspection selected (follow-up on KC document case)", dt.date(2026, 10, 17)
    elif sh_ref == "SHP02600501":
        status, hold, released = "UNDER_INSPECTION", "CIQ random inspection", None
    elif not t["delivered_date"]:
        status = "LODGED" if lodged <= C.LAST_DAY else "PRE-ALERT"
        released = None
    value = round(t["units"] * R.uniform(260, 380), 2)
    cust.append(dict(declaration_no=f"{cc}{lodged:%y%m%d}{int(R.integers(100000, 999999))}", tms_load_id=t["tms_load_id"], awb=t["awb"],
                     shipment_ref=sh_ref if R.random() > 0.3 else "", dest_country=cc, broker=BROKER.get(cc, "carrier broker"),
                     lodged_date=lodged.isoformat(), status=status, hold_reason=hold, released_date=released.isoformat() if released else "",
                     hs_codes="6201.40|6202.40|6110.11|6505.00", customs_value_eur=value,
                     duties_taxes_local=round(value * {"KR": 0.23, "JP": 0.19, "CN": 0.29, "TW": 0.17, "SG": 0.09, "AU": 0.15, "CH": 0.081,
                                                       "GB": 0.32, "AE": 0.10, "CA": 0.31}.get(cc, 0.1) *
                                              {"KR": 1530, "JP": 168, "CN": 7.95, "TW": 35.4, "SG": 1.47, "AU": 1.68, "CH": 0.94, "GB": 0.86,
                                               "AE": 4.05, "CA": 1.51}.get(cc, 1), 0)))
pd.DataFrame(cust).to_csv(OUT / "customs_declarations.csv", index=False)

# ------------------------------------------------------------------------------- lanes
NODES = [("IT10", "DC", "DC Castel San Giovanni", W_LL["IT10"], "IT", "Europe/Rome"),
         ("US20", "DC", "DC Secaucus NJ", W_LL["US20"], "US", "America/New_York"),
         ("HK30", "DC", "DC Tseung Kwan O (3PL)", W_LL["HK30"], "HK", "Asia/Hong_Kong")]
for sid in st.index:
    NODES.append((C.SAP_WERKS[sid], "STORE", st.store_name[sid], (st.lat[sid], st.lon[sid]), st.country_code[sid], st.timezone[sid]))
REGION_CC = {"EMEA": {"IT", "FR", "CH", "GB", "DE", "ES", "NL", "DK", "AE"}, "AMERICAS": {"US", "CA"},
             "APAC": {"JP", "KR", "CN", "HK", "TW", "SG", "AU"}}


def region_of(cc):
    return [r for r, s in REGION_CC.items() if cc in s][0]


obs = pd.DataFrame([dict(w=DCW[s["origin"]], store=s["store_id"], tr=(C.d(s["actual_arrival"]) - C.d(s["ship_date"])).days)
                    for s in SH if s["actual_arrival"]])
obs_p = obs.groupby(["w", "store"]).tr.agg(lambda x: (np.percentile(x, 50), np.percentile(x, 90), len(x)))
LEAD_PLAN = {"Italy": 1, "France": 2, "Switzerland": 3, "UK": 3, "Germany": 2, "Spain": 2, "Benelux": 2, "Nordics": 3,
             "Middle East": 5, "USA": 5, "Canada": 6, "Japan": 6, "Korea": 5, "Mainland China": 8, "HK/Macau/TW": 5,
             "South-East Asia": 6, "Oceania": 7}
lanes = []
for o in NODES:
    for dd in NODES:
        if dd[1] != "STORE" or o[0] == dd[0]:
            continue
        dist = haversine(o[3], dd[3])
        occ, dcc = o[4], dd[4]
        same_city = dist < 12
        domestic = occ == dcc
        eu_eu = occ in EU and dcc in EU
        cross_region = region_of(occ) != region_of(dcc)
        customs = not (domestic or eu_eu)
        dstore = C.WERKS_TO_STORE[dd[0]]
        if same_city:
            mode, carrier, t50, t90 = "COURIER_SAME_DAY", {"IT": "Milkman", "FR": "Stuart", "GB": "Addison Lee", "KR": "Kakao T Quick",
                                                            "JP": "Yamato Charter", "US": "Uber Direct"}.get(occ, "local courier"), 0, 1
        elif domestic:
            mode = "ROAD_EXPRESS" if dist < 900 else "AIR_DOMESTIC"
            carrier = {"IT": "BRT", "FR": "GEODIS", "US": "FedEx", "JP": "Yamato", "KR": "CJ Logistics", "CN": "SF Express",
                       "CH": "Planzer", "GB": "DHL Express", "DE": "DHL Express"}.get(occ, "DHL Express")
            t50, t90 = (1, 2) if dist < 700 else (2, 3)
        elif eu_eu:
            mode, carrier, t50, t90 = "ROAD_EXPRESS", "DHL Express", 2 if dist < 1100 else 3, 4
        elif not cross_region:
            mode, carrier, t50, t90 = "AIR_EXPRESS", "DHL Express", 3 if dist < 2500 else 4, 6
        else:
            mode, carrier, t50, t90 = "AIR_EXPRESS", "DHL Express", 5, 8
        if o[1] == "DC":
            sub = st.subregion[dstore]
            t_plan = LEAD_PLAN[sub]
            try:
                p50, p90, n = obs_p.loc[(o[0], dstore)]
            except KeyError:
                p50, p90, n = (np.nan, np.nan, 0)
            if region_of(occ) != region_of(dcc):
                p50, p90, n = (np.nan, np.nan, 0)
            cutoff = {"IT10": "14:00", "US20": "15:00", "HK30": "16:00"}[o[0]]
            allowed = "Y" if not cross_region else "N (route via regional DC)"
        else:
            t_plan, p50, p90, n = t50, np.nan, np.nan, 0
            cutoff = "12:00" if not same_city else "15:30"
            allowed = "Y"
            if cross_region:
                allowed = "N - cross-region IBT not permitted"
            elif dcc == "CN" or (occ == "CN" and dcc != "CN"):
                allowed = "N - CN bonded/import licence"
            elif customs:
                allowed = "EXCEPTION ONLY (area manager + customs approval)"
        fixed = 15 + 0.03 * dist if same_city else 28 + 0.022 * dist
        if customs:
            fixed += 70
        per = 0.6 + 0.0011 * dist
        docs = ""
        if customs:
            docs = "commercial invoice; packing list"
            if dcc in ("CH", "GB") and occ in EU:
                docs += "; REX origin statement"
            if dcc == "CN":
                docs += "; CN import licence; Chinese label"
            if dcc == "JP":
                docs += "; JP quality label"
            # NB: KR lanes do not list the KC certificate required for down-filled garments (master data gap)
        lanes.append(dict(lane_id=f"LN-{o[0]}-{dd[0]}", origin=o[0], origin_type=o[1], origin_name=o[2], dest=dd[0], dest_name=dd[2],
                          dest_country=dcc, distance_km=round(dist), mode=mode, default_carrier=carrier,
                          transit_days_contract=t_plan if o[1] == "DC" else t50, transit_days_p90_contract=t90 if o[1] != "DC" else t_plan + 2,
                          observed_p50_days=p50, observed_p90_days=p90, observed_n=n,
                          pickup_cutoff_local=cutoff, pickup_days="MON-FRI" if o[1] == "STORE" else "MON-SAT",
                          customs_required="Y" if customs else "N", documents=docs, ibt_allowed=allowed,
                          cost_fixed_eur=round(fixed, 2), cost_per_unit_eur=round(per, 2),
                          co2_kg_per_parcel=round((0.11 if mode.startswith("ROAD") or mode.startswith("COURIER") else 1.9) * dist / 100, 2),
                          last_reviewed="2026-07-15"))
ln = pd.DataFrame(lanes)
# stale lanes / master data quirks
ln.loc[ln.dest == C.SAP_WERKS["MAD01"], "last_reviewed"] = "2024-03-02"
ln.loc[(ln.origin == "IT10") & (ln.dest == C.SAP_WERKS["MAD01"]), ["transit_days_contract", "transit_days_p90_contract"]] = [1, 2]
ln.loc[ln.dest == C.SAP_WERKS["SYD01"], "last_reviewed"] = "2025-01-20"
ln.loc[(ln.origin == C.SAP_WERKS["COU01"]), "ibt_allowed"] = "N - store closed for season (no pick staff)"
ln.to_csv(OUT / "lane_matrix_lead_time_cost.csv", index=False)
print("lanes", len(ln))
pd.to_pickle(dict(tms=tms_df, lanes=ln), C.CACHE / "logistics_state.pkl")
