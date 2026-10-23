"""Inter-store transfers (IBT) history from the retail ops tool + ServiceNow-like logistics incidents."""
import datetime as dt
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

R = C.rng("ibt_incidents")
OUT = C.OUT / "logistics"
(OUT / "incidents").mkdir(parents=True, exist_ok=True)
st = C.stores().set_index("store_id")
sk = C.skus().set_index("sku")
LS = pd.read_pickle(C.CACHE / "logistics_state.pkl")
lanes = LS["lanes"].set_index(["origin", "dest"])


def lane(src, dst):
    return lanes.loc[(C.SAP_WERKS[src], C.SAP_WERKS[dst])]


def cost(src, dst, q):
    l_ = lane(src, dst)
    return round(float(l_.cost_fixed_eur) + float(l_.cost_per_unit_eur) * q, 2)


def ts(day, hh, mm, store):
    return f"{C.d(day).isoformat()} {hh:02d}:{mm:02d}"


rows = []
seq = [1180]


def ibt(created, req, src, sku, size, qty, status, reason, approver="", approved=None, shipped=None, received=None,
        carrier="", rej="", comment="", hh=None):
    seq[0] += int(R.integers(1, 4))
    l_ = lane(src, req)
    created_d = C.d(created)
    lead = (C.d(received) - created_d).days if received else ""
    hh = hh if hh is not None else int(R.integers(10, 19))
    sku_str = f"{sku}-{size}" if R.random() > 0.12 else sku    # quirk: sometimes size only in its own column
    mm = int(R.integers(0, 60))
    c_dt = dt.datetime.combine(created_d, dt.time(hh, mm))
    if approved:
        a_dt = max(c_dt + dt.timedelta(minutes=int(R.integers(25, 300))), dt.datetime.combine(C.d(approved), dt.time(9, int(R.integers(0, 59)))))
    rows.append(dict(ibt_id=f"IBT-26-{seq[0]:05d}", created_at_local=f"{created_d} {hh:02d}:{mm:02d}",
                     requesting_store=req, source_store=src, sku=sku_str, style=C.STYLE_NAME[sku.split('-')[0]], colour=sku.split('-')[1],
                     size=size, qty=qty, reason_code=reason, status=status, approver=approver,
                     approved_at=a_dt.strftime("%Y-%m-%d %H:%M") if approved else "",
                     shipped_date=C.d(shipped).isoformat() if shipped else "", received_date=C.d(received).isoformat() if received else "",
                     carrier=carrier or (l_.default_carrier if shipped else ""), lane_mode=l_["mode"],
                     lead_time_days=lead, transport_cost_eur=cost(src, req, qty) if shipped else "",
                     rejection_reason=rej, comment=comment))


AM = {"Italy": "Roberto Galli", "Spain": "Roberto Galli", "France": "Isabelle Moreau", "Switzerland": "Stefan Wagner",
      "Germany": "Stefan Wagner", "UK": "Fiona McLeod", "Benelux": "Fiona McLeod", "Nordics": "Fiona McLeod", "Middle East": "Omar Haddad",
      "USA": "Lauren Mitchell", "Canada": "Lauren Mitchell", "Japan": "Takuya Suzuki", "Korea": "Yoon Sung-ho",
      "Mainland China": "Zhao Lei", "HK/Macau/TW": "Vivian Lau", "South-East Asia": "Daniel Lim", "Oceania": "Daniel Lim"}
VALENTINO_V01, ILV = "J20931A00012-999", "J20931A00618-510"
LC9, LC7 = "I10919B00011-999", "I10919B00011-742"
AMB, MAYA9 = "J20931A00622-23R", "J10911A00034-999"

# ------------------------------------------------------------- key (scenario) IBTs
ibt("2026-09-22", "MIL01", "ROM01", VALENTINO_V01, "1", 2, "RECEIVED", "CLIENT_REQUEST", "Roberto Galli", "2026-09-22", "2026-09-23",
    "2026-09-24", "BRT", comment="clienti coreane chiedono Aurea nera, urgente")
ibt("2026-09-22", "MIL01", "ROM01", VALENTINO_V01, "0", 1, "RECEIVED", "CLIENT_REQUEST", "Roberto Galli", "2026-09-22", "2026-09-23",
    "2026-09-24", "BRT", comment="")
ibt("2026-09-23", "PAR01", "CAN01", VALENTINO_V01, "0", 1, "REJECTED", "CLIENT_REQUEST", "Laetitia Rossi", rej="SOURCE_REFUSED",
    comment="Cannes: dernière pièce en 0, on la garde")
ibt("2026-09-23", "PAR01", "CAN01", VALENTINO_V01, "1", 1, "REJECTED", "CLIENT_REQUEST", "Laetitia Rossi", rej="SOURCE_REFUSED", comment="")
ibt("2026-09-24", "MIL01", "COU01", VALENTINO_V01, "1", 2, "REJECTED", "CLIENT_REQUEST", "Roberto Galli",
    rej="SOURCE_CLOSED", comment="Courmayeur chiuso per fine stagione, nessuno in negozio per il prelievo. Riapre 27/11")
ibt("2026-09-24", "MIL01", "COU01", VALENTINO_V01, "2", 2, "REJECTED", "CLIENT_REQUEST", "Roberto Galli", rej="SOURCE_CLOSED", comment="")
ibt("2026-09-25", "LON02", "LON01", VALENTINO_V01, "1", 2, "RECEIVED", "CLIENT_REQUEST", "Fiona McLeod", "2026-09-25", "2026-09-25",
    "2026-09-25", "Addison Lee", comment="Korean tourists asking, same-day courier")
ibt("2026-09-26", "PAR02", "GVA01", VALENTINO_V01, "0", 2, "REJECTED", "CLIENT_REQUEST", "Isabelle Moreau",
    rej="CROSS_BORDER_NOT_ALLOWED", comment="CH->FR export declaration needed, not for IBT")
ibt("2026-10-02", "PAR01", "BER01", VALENTINO_V01, "1", 1, "CANCELLED", "CLIENT_REQUEST", "Isabelle Moreau", "2026-10-02",
    rej="CUTOFF_MISSED", comment="demande envoyée après le cut-off 12h00 de vendredi, enlèvement lundi -> cliente repart à Séoul dimanche",
    hh=13)
ibt("2026-10-02", "SEL01", "SIN01", ILV, "0", 2, "REJECTED", "CLIENT_REQUEST", "Daniel Lim", rej="CROSS_BORDER_NOT_ALLOWED",
    comment="KR import for down garments needs KC doc - not via IBT")
ibt("2026-10-03", "SEL01", "BUS01", ILV, "0", 2, "REJECTED", "CLIENT_REQUEST", "Yoon Sung-ho", rej="NO_STOCK_AT_SOURCE",
    comment="센텀도 10/2 완판")
ibt("2026-10-03", "SEL01", "SEL02", ILV, "1", 1, "REJECTED", "CLIENT_REQUEST", "Yoon Sung-ho", rej="NO_STOCK_AT_SOURCE", comment="")
ibt("2026-10-04", "TYO01", "TYO02", ILV, "1", 1, "RECEIVED", "CLIENT_REQUEST", "Takuya Suzuki", "2026-10-04", "2026-10-05",
    "2026-10-05", "Yamato Charter", comment="VIC 予約分")
ibt("2026-10-05", "SHA01", "BJS01", ILV, "0", 1, "REJECTED", "CLIENT_REQUEST", "Zhao Lei", rej="NO_STOCK_AT_SOURCE", comment="北京也断货")
ibt("2026-10-09", "MIL01", "MIL02", LC9, "M", 2, "APPROVED", "CLIENT_REQUEST", "Roberto Galli", "2026-10-09",
    comment="Rinascente deve autorizzare uscita merce - in attesa del loro ricevimento/uscita")
ibt("2026-10-12", "MIL01", "ROM01", LC7, "M", 1, "REQUESTED", "CLIENT_REQUEST", comment="cardigan blu M, cliente torna sabato")
ibt("2026-10-20", "MIL01", "VEN01", LC9, "M", 1, "REQUESTED", "CLIENT_REQUEST", comment="")
ibt("2026-09-30", "MAD01", "MIL01", MAYA9, "3", 2, "RECEIVED", "STOCK_BALANCING", "Roberto Galli", "2026-09-30", "2026-10-01",
    "2026-10-03", "DHL Express", comment="nos mandaron azul marino en vez de negro, clientes esperando")
ibt("2026-09-30", "MAD01", "MIL01", MAYA9, "4", 2, "RECEIVED", "STOCK_BALANCING", "Roberto Galli", "2026-09-30", "2026-10-01",
    "2026-10-03", "DHL Express", comment="")
ibt("2026-09-27", "MIL01", "VEN01", AMB, "1", 1, "RECEIVED", "CLIENT_REQUEST", "Roberto Galli", "2026-09-28", "2026-09-28",
    "2026-09-29", "BRT", comment="Amalia marrone 1 per VIC")
ibt("2026-10-06", "PAR01", "PAR02", AMB, "1", 1, "REJECTED", "CLIENT_REQUEST", "Sophie Marchand", rej="SOURCE_REFUSED",
    comment="GL: stock concession, pas de sortie sans accord du grand magasin")
ibt("2026-10-14", "LON01", "LON02", AMB, "2", 1, "CANCELLED", "CLIENT_REQUEST", comment="client bought black instead")
ibt("2026-10-15", "MUN01", "BER01", "J10911A00213-999", "4", 2, "RECEIVED", "STOCK_BALANCING", "Stefan Wagner", "2026-10-15",
    "2026-10-16", "2026-10-19", "DHL Express", comment="Kälteeinbruch, Monteluce läuft")
ibt("2026-10-15", "MUN01", "BER01", "J10911A00213-999", "5", 1, "RECEIVED", "STOCK_BALANCING", "Stefan Wagner", "2026-10-15",
    "2026-10-16", "2026-10-19", "DHL Express", comment="")
ibt("2026-10-14", "ZRH01", "GVA01", MAYA9, "3", 1, "RECEIVED", "CLIENT_REQUEST", "Stefan Wagner", "2026-10-14", "2026-10-14",
    "2026-10-15", "Planzer", comment="")
ibt("2026-10-10", "SHA01", "HKG01", "G20921A00902-999", "M", 3, "REJECTED", "STOCK_BALANCING", "Zhao Lei",
    rej="CROSS_BORDER_NOT_ALLOWED", comment="CN import licence - use DC STO")
ibt("2026-09-18", "SYD01", "SIN01", "I10918A00034-742", "L", 4, "REJECTED", "STOCK_BALANCING", "Daniel Lim",
    rej="CROSS_BORDER_NOT_ALLOWED", comment="customers want polos + tees (spring!), we only get down jackets")
ibt("2026-10-07", "SYD01", "SIN01", "I10918C00012-001", "M", 5, "REJECTED", "STOCK_BALANCING", "Daniel Lim",
    rej="CROSS_BORDER_NOT_ALLOWED", comment="again - please fix the allocation instead")

# ------------------------------------------------------------- background balancing IBTs
days = list(C.daterange("2026-08-03", "2026-10-21"))
pairs = []
for a in st.index:
    for b in st.index:
        if a == b:
            continue
        try:
            l_ = lane(b, a)
        except KeyError:
            continue
        if str(l_.ibt_allowed).startswith("Y") and l_.distance_km < 1300:
            pairs.append((a, b))
stock_cache = {}
REASONS = ["STOCK_BALANCING", "CLIENT_REQUEST", "CLIENT_REQUEST", "SIZE_EXCHANGE", "VM_DISPLAY"]
REJ = ["NO_STOCK_AT_SOURCE", "SOURCE_REFUSED", "BELOW_MIN_PRESENTATION", "CUTOFF_MISSED"]
n = 0
while n < 175:
    x = days[int(R.integers(0, len(days)))]
    if x.weekday() == 6:
        continue
    req, src = pairs[int(R.integers(0, len(pairs)))]
    if src in ("COU01",) or (src == "STM01" and x >= dt.date(2026, 10, 19)):
        continue
    if x not in stock_cache:
        stock_cache[x] = C.store_stock(x)
    s_ = stock_cache[x]
    cand = s_[(s_.store_id == src) & (s_.on_hand >= 3)]
    if not len(cand):
        continue
    r = cand.iloc[int(R.integers(0, len(cand)))]
    if r.sku in (VALENTINO_V01, ILV, AMB, LC9, LC7):
        continue
    qty = int(R.integers(1, 3))
    u = R.random()
    l_ = lane(src, req)
    t50 = int(l_.transit_days_contract)
    if u < 0.72 and x <= dt.date(2026, 10, 17):
        ship = x + dt.timedelta(days=int(R.integers(0, 3)))
        while ship.weekday() >= 5:
            ship += dt.timedelta(days=1)
        rec = ship + dt.timedelta(days=t50 + int(R.choice([0, 0, 0, 1, 1, 2])))
        if rec > C.LAST_DAY:
            ibt(x, req, src, r.sku, r["size"], qty, "SHIPPED", str(R.choice(REASONS)), AM[st.subregion[req]], x, ship)
        else:
            ibt(x, req, src, r.sku, r["size"], qty, "RECEIVED", str(R.choice(REASONS)), AM[st.subregion[req]], x, ship, rec)
    elif u < 0.86:
        rj = str(R.choice(REJ))
        ibt(x, req, src, r.sku, r["size"], qty, "REJECTED", str(R.choice(REASONS)), AM[st.subregion[req]], rej=rj)
    elif u < 0.94:
        ibt(x, req, src, r.sku, r["size"], qty, "CANCELLED", str(R.choice(REASONS)))
    else:
        ibt(x, req, src, r.sku, r["size"], qty, "REQUESTED" if x > dt.date(2026, 10, 14) else "EXPIRED", str(R.choice(REASONS)))
    n += 1

ib = pd.DataFrame(rows).sort_values("created_at_local").reset_index(drop=True)
_ids = [1180]
for _i in range(len(ib)):
    _ids.append(_ids[-1] + int(R.integers(1, 4)))
ib["ibt_id"] = [f"IBT-26-{v:05d}" for v in _ids[1:]]
# quirk: one request exported twice (double-click in the tool)
ib = pd.concat([ib, ib[ib.ibt_id == ib.ibt_id.iloc[40]]]).sort_values("created_at_local", kind="stable")
ib.to_csv(OUT / "ibt_transfers_storelink_export.csv", index=False)
print("IBT rows", len(ib), ib.status.value_counts().to_dict())

# ------------------------------------------------------------- incidents (ServiceNow-like)
tms = LS["tms"].set_index("shipment_ref")


def awb(ref):
    return tms.awb[ref]


INC = [
    dict(number="INC0040912", opened_at="2026-09-17 08:55:21", caller_id="Vivian Lau", u_store="Hong Kong Canton Road",
         category="Logistics", subcategory="Delivery delay", priority="3 - Moderate", assignment_group="LOG-APAC-3PL-TKO",
         short_description="HKG01 delivery 0080412311 - typhoon signal 8, store closed",
         description="Store closed all day 17/9 (T8). Kerry booked slot for 21/9 - please re-book, mall loading bay backlog after typhoon.",
         u_shipment_ref=f"0080412311 / {awb('SHP02600311')}", state="Closed", resolved_at="2026-09-23 16:40:02",
         close_code="Solved (Work Around)", close_notes="Delivered 23/9 after re-booking. 2 days late."),
    dict(number="INC0041877", opened_at="2026-09-26 12:14:09", caller_id="Javier Molina", u_store="MAD01 Serrano",
         category="Logistics", subcategory="Wrong item received", priority="2 - High", assignment_group="LOG-EMEA-DC-CSG",
         short_description="MAD01 - recibido NOVA azul marino en lugar de negro / wrong colour NOVA",
         description="Albarán 0080412337. Pedido NOVA negro (999) tallas 1-7, 17 piezas. Llegaron 17 NOVA azul marino (742). "
                     "Tenemos clientes esperando el negro. Fotos en adjunto (IMG_2231.jpg, IMG_2232.jpg).",
         u_shipment_ref=f"0080412337 / {awb('SHP02600337')}", state="Resolved", resolved_at="2026-10-07 10:02:44",
         close_code="Solved (Permanently)",
         close_notes="Root cause: bin labels 03-14-B / 03-14-C swapped after re-slotting 21/09. Second delivery 0080412382 also affected "
                     "(see INC0042011). Cycle count 06/10, differences posted (701/702). Black NOVA shipped with 0080412427 (arrived 11/10). "
                     "Navy surplus (37 pcs) still at MAD01 - retail ops to decide return vs keep."),
    dict(number="INC0042011", opened_at="2026-10-01 18:47:55", caller_id="Lucía Fernández Ortega", u_store="Madrid Serrano",
         category="Logistics", subcategory="Wrong item received", priority="2 - High", assignment_group="LOG-EMEA-DC-CSG",
         short_description="OTRA VEZ NOVA azul en vez de negro!!! albaran 0080412382",
         description="Segunda vez. 20 piezas azul marino. Ya no tenemos NOVA negro en ninguna talla, perdemos ventas cada día.",
         u_shipment_ref=f"0080412382 / {awb('SHP02600382')}", state="Closed", resolved_at="2026-10-02 09:15:00",
         close_code="Duplicate", close_notes="Duplicate of INC0041877"),
    dict(number="INC0042230", opened_at="2026-10-08 10:31:40", caller_id="박민수", u_store="SEL01 Cheongdam",
         category="Logistics", subcategory="Customs", priority="2 - High", assignment_group="LOG-APAC-TRADE-COMPLIANCE",
         short_description="SEL01 shipment held at Incheon customs - KC certificate missing",
         description="입고 예정 10/8 물량이 인천세관에서 보류. 관세사: 다운 의류 KC 적합성 확인서 누락. Iridia 핑크 대기 고객 많음 - 언제 받을 수 있나요?",
         u_shipment_ref=f"0080412440 / {awb('SHP02600440')}", state="Resolved", resolved_at="2026-10-13 11:20:31",
         close_code="Solved (Permanently)",
         close_notes="KC certificate issued by testing lab and sent to broker 12/10, released 12/10 17:24 KST, delivered 13/10. "
                     "NB this load contained IRIDIA off-white (20D) only - pink top-up left TKO on 10/10 with 0080412455."),
    dict(number="INC0042398", opened_at="2026-10-14 09:02:13", caller_id="Vivian Lau", u_store="Seoul Cheongdam Flagship",
         category="Logistics", subcategory="Customs", priority="2 - High", assignment_group="LOG-APAC-TRADE-COMPLIANCE",
         short_description="Follow-up: 0080412455 (incl. IRIDIA pink) selected for inspection at ICN",
         description="After the KC document case customs selected the next down-garment import for physical inspection. "
                     "Store is chasing - 20 pcs IRIDIA 510 inside.",
         u_shipment_ref=f"0080412455 / {awb('SHP02600455')}", state="Resolved", resolved_at="2026-10-18 15:44:00",
         close_code="Solved (Work Around)", close_notes="Released 17/10, delivered 18/10 (planned 15/10)."),
    dict(number="INC0042126", opened_at="2026-10-07 16:20:48", caller_id="Ilaria Mancuso", u_store="Rinascente Duomo",
         category="Logistics", subcategory="Delivery delay", priority="4 - Low", assignment_group="LOG-EMEA-DC-CSG",
         short_description="Consegna Rinascente non accettata - slot ricevimento pieno",
         description="Il corriere si è presentato alle 15:30, ricevimento merci Rinascente accetta solo fino alle 14. Riprogrammare.",
         u_shipment_ref=f"0080412413 / {awb('SHP02600413')}", state="Closed", resolved_at="2026-10-10 12:00:00",
         close_code="Solved (Work Around)", close_notes="Consegnato 10/10. Chiesto a DHL di rispettare finestra 8-14."),
    dict(number="INC0042544", opened_at="2026-10-15 17:05:30", caller_id="logistics.emea", u_store="(multiple IT)",
         category="Logistics", subcategory="Carrier notice", priority="4 - Low", assignment_group="LOG-EMEA-TRANSPORT",
         short_description="Sciopero generale 16/10 - possibili ritardi consegne Italia",
         description="BRT/DHL comunicano possibili ritardi per sciopero trasporti venerdì 16/10. Consegne MIL/ROM/VEN a rischio.",
         u_shipment_ref="", state="Closed", resolved_at="2026-10-17 09:00:00", close_code="No impact",
         close_notes="Consegne del 16-17/10 regolari."),
    dict(number="INC0042701", opened_at="2026-10-20 07:48:12", caller_id="Luca Boscolo", u_store="Venezia San Marco",
         category="Logistics", subcategory="Delivery delay", priority="3 - Moderate", assignment_group="LOG-EMEA-TRANSPORT",
         short_description="Acqua alta 118cm - negozio apre alle 12, consegna?",
         description="Oggi apriamo a mezzogiorno, piazza allagata. Se arriva la consegna domani va fatta in barca dal lato canale.",
         u_shipment_ref=f"0080412505 / {awb('SHP02600505')}", state="Closed", resolved_at="2026-10-21 14:10:00",
         close_code="No impact", close_notes="Consegnato 21/10 regolarmente."),
    dict(number="INC0041555", opened_at="2026-09-28 09:30:00", caller_id="Reto Ammann", u_store="Zürich Bahnhofstrasse",
         category="Logistics", subcategory="Delivery delay", priority="4 - Low", assignment_group="LOG-EMEA-TRANSPORT",
         short_description="ZRH01 Lieferung 3 Tage zu spät, 1 Karton beschädigt",
         description="Sendung 0080412335 erst heute angekommen, ein Karton eingedrückt, Ware ok.",
         u_shipment_ref=f"0080412335 / {awb('SHP02600335')}", state="Closed", resolved_at="2026-09-30 11:00:00",
         close_code="Solved (Work Around)", close_notes="Claim opened with BRT, no garment damage."),
    dict(number="INC0042090", opened_at="2026-10-03 11:12:40", caller_id="Giulia Ferrandi", u_store="Milano Montenapoleone",
         category="Logistics", subcategory="Returns", priority="3 - Moderate", assignment_group="LOG-EMEA-DC-CSG",
         short_description="Resi VEL difettosi - quale RMA usare? scatola piena",
         description="Abbiamo 9 gilet VEL resi per cerniera rotta. Dove li mandiamo, con quale RMA? Il DC dice QM01 ma il modulo non lo prevede.",
         u_shipment_ref="", state="Resolved", resolved_at="2026-10-05 15:00:00", close_code="Solved (Permanently)",
         close_notes=f"Use RMA type DEF, ship to IT10 QM01 with next return pickup, reference QN {C.VALENTINO_V17['qn']}."),
    dict(number="INC0042777", opened_at="2026-10-21 10:40:00", caller_id="陈浩", u_store="Shanghai Plaza 66",
         category="Logistics", subcategory="Customs", priority="3 - Moderate", assignment_group="LOG-APAC-TRADE-COMPLIANCE",
         short_description="SHA01 货物海关查验 / shipment under CIQ inspection",
         description="10/17发货的那批还在浦东海关查验，预计到店延迟。双十一前需要到货。",
         u_shipment_ref=f"0080412501 / {awb('SHP02600501')}", state="In Progress", resolved_at="", close_code="", close_notes=""),
    dict(number="INC0041190", opened_at="2026-09-22 15:02:00", caller_id="Rebecca Stein", u_store="NYC01 Madison",
         category="Logistics", subcategory="Delivery delay", priority="4 - Low", assignment_group="LOG-AMER-DC-NJ",
         short_description="UNGA frozen zone - UPS couldn't reach Madison Ave entrance",
         description="Driver was stopped at 65th St, delivered through the Park Ave side with security escort, 2h late. Please warn carrier for rest of the week.",
         u_shipment_ref=f"0080412341 / {awb('SHP02600341')}", state="Closed", resolved_at="2026-09-28 10:00:00", close_code="No impact", close_notes=""),
    dict(number="INC0042302", opened_at="2026-10-09 13:30:18", caller_id="Chloe Mitchell", u_store="Sydney",
         category="Logistics", subcategory="Delivery delay", priority="4 - Low", assignment_group="LOG-APAC-3PL-TKO",
         short_description="SYD01 delivery late again + again only puffers",
         description="Shipment due 14/10 now showing 17/10 (flight offloaded). Honestly it's 24 degrees here, we need tees and polos not more Nova.",
         u_shipment_ref=f"0080412449 / {awb('SHP02600449')}", state="Closed", resolved_at="2026-10-17 18:00:00",
         close_code="Solved (Work Around)", close_notes="Delivered 17/10. Assortment comment forwarded to merch planning (no action)."),
]
pd.DataFrame(INC).to_csv(OUT / "incidents" / "servicenow_incidents_logistics.csv", index=False)

WORK = {
    "INC0041877": [
        ("2026-09-26 12:14:09", "Javier Molina", "Abrimos incidencia. 17 NOVA azul marino recibidos, pedido era negro. No vendemos el azul, nos sobra."),
        ("2026-09-26 15:40:31", "DC CSG - Outbound (M. Re)", "Presa in carico. Verifichiamo picking list consegna 0080412337."),
        ("2026-09-29 10:05:12", "DC CSG - Outbound (M. Re)", "WMS: prelievo confermato su materiale J10911A00034999, giacenza contabile coerente. "
         "Possibile errore di etichettatura lato negozio? Chiediamo foto etichette EAN."),
        ("2026-09-29 11:20:00", "Javier Molina", "Fotos enviadas. EAN en las etiquetas = 742 (navy). El problema es vuestro."),
        ("2026-10-01 18:52:10", "Lucía Fernández Ortega", "Ha vuelto a pasar con 0080412382. Ver INC0042011."),
        ("2026-10-02 09:20:44", "DC CSG - Inventory (S. Gatti)", "Trovato: etichette ubicazioni 03-14-B e 03-14-C invertite dopo re-slotting del 21/09. "
         "Aperta QN 300004590. Inventario rotativo previsto 06/10."),
        ("2026-10-02 10:02:00", "Roberto Galli", "Please prioritise black NOVA for Madrid in next delivery. Meanwhile IBT from MIL01 sizes 3-4 approved (IBT-26 ...)."),
        ("2026-10-06 17:45:00", "DC CSG - Inventory (S. Gatti)", "Inventario 06/10: +37 NOVA 999 / -37 NOVA 742 registrati (701/702)."),
        ("2026-10-07 10:02:44", "DC CSG - Outbound (M. Re)", "NOVA nero incluso nella consegna dell'08/10. Chiudo. Reso del blu da concordare con Retail Ops."),
    ],
    "INC0042230": [
        ("2026-10-08 10:31:40", "박민수", "인천세관 보류 통보 받음. 관세사 연락: KC 적합성 확인서 필요. 오늘 입고 예정이었음."),
        ("2026-10-08 11:15:02", "APAC Logistics (K. Leung)", "Broker confirms: import declaration for HS 6201/6202 down-filled garments requires KC conformity doc since the new "
         "labelling notice. Not in our document pack. Checking with trade compliance Milan."),
        ("2026-10-08 14:47:19", "Trade Compliance (F. Albertini)", "Il certificato KC non è mai stato richiesto prima per le spedizioni dal TKO; "
         "chiediamo al laboratorio. Tempi stimati 2-3 giorni lavorativi."),
        ("2026-10-09 09:10:00", "김지현", "VIC 고객 Iridia 핑크 대기중인데 이 박스에 핑크 있나요?"),
        ("2026-10-09 10:40:55", "APAC Logistics (K. Leung)", "Checked packing list: no pink in this load, only IRIDIA off-white 20D + other lines. "
         "Pink top-up ships Saturday 10/10 from TKO."),
        ("2026-10-12 09:30:00", "Trade Compliance (F. Albertini)", "Certificato ricevuto dal laboratorio, inviato al broker."),
        ("2026-10-12 17:30:12", "APAC Logistics (K. Leung)", "Released 17:24 KST. Delivery tomorrow morning."),
        ("2026-10-13 11:20:31", "박민수", "입고 완료. 감사합니다."),
    ],
    "INC0042398": [
        ("2026-10-14 09:02:13", "Vivian Lau", "Next SEL01 load (0080412455, IRIDIA pink 20 pcs) selected for physical inspection. Any way to expedite?"),
        ("2026-10-14 12:00:00", "APAC Logistics (K. Leung)", "Broker says inspection queue 2-4 days after the KC case. We cannot expedite."),
        ("2026-10-17 17:00:00", "APAC Logistics (K. Leung)", "Released. Delivery Sunday 18/10 morning."),
    ],
}
with open(OUT / "incidents" / "servicenow_worknotes.json", "w", encoding="utf-8") as f:
    json.dump({k: [dict(sys_created_on=a, sys_created_by=b, value=c, element="work_notes") for a, b, c in v] for k, v in WORK.items()},
              f, ensure_ascii=False, indent=1)
print("incidents", len(INC))
