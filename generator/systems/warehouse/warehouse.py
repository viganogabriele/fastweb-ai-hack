"""Warehouse / WMS sources for the 3 DCs.

DC-IT-CSG (plant IT10) and DC-US-NJ (US20) run SAP EWM/ERP -> SAP-style extractions.
DC-HK-TKO (HK30) is operated by a 3PL (Pacific Crest Logistics) -> 3PL portal CSVs, HKT timestamps, own item codes.

The DC stock is reconstructed so that it is consistent with:
  - internal shipments_dc_to_store.jsonl (goods issues by ship_date),
  - launch allocations (store stock on launch day + launch-day sales; not in the shipments file),
  - e-commerce web reserve transfers / sales (generator/systems/_cache from ecommerce.py),
  - DC_CONSTRAINTS (zero stock windows) and the KEY_POS receipts in common.py,
  - VEL defective batch + store/online defect returns into quality stock.
"""
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
from events import DC_CONSTRAINTS  # noqa: E402

R = C.rng("warehouse")
OUT = C.OUT / "warehouse"
for sub in ["sap_stock_IT10", "sap_stock_US20", "pcl_tko_inventory", "atp", "api_samples"]:
    (OUT / sub).mkdir(parents=True, exist_ok=True)

DAYS = list(C.daterange("2026-08-01", "2026-10-21"))
DI = {x: i for i, x in enumerate(DAYS)}
ND = len(DAYS)
DCW = {"DC-IT-CSG": "IT10", "DC-US-NJ": "US20", "DC-HK-TKO": "HK30"}
W2DC = {v: k for k, v in DCW.items()}
REG_W = {"EMEA": "IT10", "AMERICAS": "US20", "APAC": "HK30"}

st = C.stores().set_index("store_id")
sk = C.skus().set_index("sku")
ean = C.sku_sizes().set_index(["sku", "size"]).ean
RUN = {s: config.SIZE_RUNS[sk.size_run[s]] for s in sk.index}
CURVE = {s: np.array(config.SIZE_CURVES[sk.size_run[s]]) for s in sk.index}
SN = {s: C.STYLE_NAME[s.split("-")[0]] for s in sk.index}
LAUNCH = {s: (C.d(sk.launch_date[s]) if isinstance(sk.launch_date[s], str) else None) for s in sk.index}


def zeros():
    return np.zeros(ND, dtype=np.int64)


# ------------------------------------------------------------------------------------ flows
gi_store = defaultdict(zeros)      # (werks, sku, size) -> per day
gi_launch = defaultdict(zeros)
web_xfer = defaultdict(zeros)
def_ret_in = defaultdict(zeros)    # defective returns into QM01
onl_ret_in = defaultdict(zeros)    # online returns into RT01
ss26_ret_in = defaultdict(zeros)   # SS26 returns from stores into RT01
open_orders = defaultdict(zeros)   # qty ordered on day d not yet shipped (shipped d+1/d+2) -> allocated at EOD d

SH = C.shipments()
for s in SH:
    w = DCW[s["origin"]]
    i = DI.get(C.d(s["ship_date"]))
    io = DI.get(C.d(s["order_date"]))
    for ln in s["lines"]:
        key = (w, ln["sku"], ln["size"])
        if i is not None:
            gi_store[key][i] += ln["qty_shipped"]
        if io is not None and i is not None:
            for j in range(io, i):
                open_orders[key][j] += ln["qty_ordered"]

# launch allocations: stock EOD on launch day + launch-day sales
pos = C.pos_lines()
sales_pos = pos[pos.line_type == "SALE"].groupby(["business_date", "store_id", "sku", "size"]).qty.sum()
launch_alloc_rows = []
for ldate in sorted({v for v in LAUNCH.values() if v and v >= dt.date(2026, 8, 1)}):
    lskus = [s for s, v in LAUNCH.items() if v == ldate]
    stk = C.store_stock(ldate)
    stk = stk[stk.sku.isin(lskus)]
    for r in stk.itertuples():
        q = int(r.on_hand)
        try:
            q += int(sales_pos.loc[(ldate.isoformat(), r.store_id, r.sku, r.size)])
        except KeyError:
            pass
        if q > 0:
            launch_alloc_rows.append((ldate, r.store_id, r.sku, r.size, q))
la = pd.DataFrame(launch_alloc_rows, columns=["launch_date", "store_id", "sku", "size", "qty"])
la["region"] = la.store_id.map(st.region)
LEAD_GI = {"EMEA": 2, "AMERICAS": 6, "APAC": 7}      # days before launch the allocation leaves the DC
la["gi_date"] = la.apply(lambda r: r.launch_date - dt.timedelta(days=LEAD_GI[r.region] + (1 if r.store_id in ("SYD01", "CDU01", "BJS01", "SHA01") else 0)), axis=1)
for r in la.itertuples():
    gi_launch[(REG_W[r.region], r.sku, r.size)][DI[r.gi_date]] += r.qty
la.to_csv(C.CACHE / "launch_allocations.csv", index=False)
print("launch alloc units", la.qty.sum(), la.groupby(la.sku.map(SN)).qty.sum().to_dict())

# e-commerce
wx = pd.read_csv(C.CACHE / "ecom_web_transfers.csv", dtype={"size": str}, parse_dates=["date"])
for r in wx.itertuples():
    web_xfer[(r.werks, r.sku, r.size)][DI[r.date.date()]] += r.qty
wse = pd.read_csv(C.CACHE / "ecom_web_stock_eod.csv", dtype={"size": str}, parse_dates=["date"])
web_eod = defaultdict(zeros)
for r in wse.itertuples():
    web_eod[(r.werks, r.sku, r.size)][DI[r.date.date()]] = r.qty
NODEW = {"EMEA": "IT10", "AMERICAS": "US20", "APAC": "HK30"}
CC_NODE = {"IT": "EMEA", "FR": "EMEA", "CH": "EMEA", "GB": "EMEA", "DE": "EMEA", "ES": "EMEA", "NL": "EMEA", "DK": "EMEA",
           "AE": "EMEA", "BE": "EMEA", "AT": "EMEA", "SE": "EMEA", "US": "AMERICAS", "CA": "AMERICAS"}
er = pd.read_csv(C.CACHE / "ecom_returns_units.csv", dtype={"size": str}, parse_dates=["date"])
for r in er.itertuples():
    w = NODEW[CC_NODE.get(r.country, "APAC")]
    lag = 4 if w != "HK30" else 6
    x = r.date.date() + dt.timedelta(days=lag)
    if x > C.LAST_DAY:
        continue
    if r.reason == "DEFECTIVE":
        def_ret_in[(w, r.sku, r.size)][DI[x]] += r.qty
    else:
        onl_ret_in[(w, r.sku, r.size)][DI[x]] += r.qty

# store defective returns (POS reason DEF) -> DC quality hold
RET_LAG = {"EMEA": (5, 10), "AMERICAS": (7, 12), "APAC": (8, 15)}
store_def = pos[(pos.line_type == "RETURN") & (pos.return_reason == "DEF")]
store_def_rows = []
for r in store_def.itertuples():
    reg = st.region[r.store_id]
    lag = int(R.integers(*RET_LAG[reg]))
    x = C.d(r.business_date) + dt.timedelta(days=lag)
    # stores consolidate returns on their next DC delivery day: shift to weekday
    while x.weekday() >= 5:
        x += dt.timedelta(days=1)
    store_def_rows.append(dict(store_id=r.store_id, return_date=r.business_date, receipt_id=r.receipt_id, sku=r.sku,
                               size=r.size, qty=-int(r.qty), dc_receipt=x if x <= C.LAST_DAY else None, werks=REG_W[reg]))
    if x <= C.LAST_DAY:
        def_ret_in[(REG_W[reg], r.sku, r.size)][DI[x]] += -int(r.qty)
store_def_df = pd.DataFrame(store_def_rows)

# SS26 returned by stores on Sep 1 -> DC RT01
ss26 = [s for s in sk.index if sk.season[s] == "SS26"]
stk31 = C.store_stock("2026-08-31")
stk31 = stk31[stk31.sku.isin(ss26) & (stk31.on_hand > 0)]
for r in stk31.itertuples():
    reg = st.region[r.store_id]
    x = dt.date(2026, 9, 1) + dt.timedelta(days={"EMEA": 3, "AMERICAS": 7, "APAC": 9}[reg] + int(R.integers(0, 3)))
    while x.weekday() >= 5:
        x += dt.timedelta(days=1)
    ss26_ret_in[(REG_W[reg], r.sku, r.size)][DI[x]] += int(r.on_hand)

# ------------------------------------------------------------------------------------ blocks
BLOCKS = []
for style, color, szs, a, b, note in DC_CONSTRAINTS:
    for s in sk.index:
        if SN[s] == style and (color is None or s.endswith("-" + color)):
            for z in RUN[s]:
                if szs is None or z in szs:
                    BLOCKS.append((s, z, C.d(a), C.d(b), note))
BLOCK = {(s, z): (a, b) for s, z, a, b, n in BLOCKS}

# key PO receipts per (werks, sku) with fixed totals
KEY_GR = defaultdict(list)    # (werks, sku) -> [(date, qty, ebeln, ebelp)]
for po in C.KEY_POS:
    for ln in po["lines"]:
        if ln.get("gr"):
            KEY_GR[(ln["werks"], ln.get("sku", po["sku"]))].append((C.d(ln["gr"]), ln["qty"], po["ebeln"], ln["ebelp"]))

# ------------------------------------------------------------------------------------ stock engine
keys = set(gi_store) | set(gi_launch) | set(web_xfer) | set(ss26_ret_in) | set(def_ret_in)
skus_by_w = defaultdict(set)
for (w, s, z) in keys:
    skus_by_w[w].add(s)

# net demand on main storage location 0001
def net(w, s, z):
    k = (w, s, z)
    return gi_store[k] + gi_launch[k] + web_xfer[k]


receipts = []          # dict(werks, sku, size, date, qty, ebeln, ebelp, batch, kind)
stock0 = {}            # (w,s,z) -> opening stock 0001
main_eod = {}          # (w,s,z) -> array 0001 EOD (unrestricted, before VEL block)
tib_blocked = {}       # (w,s,z) -> array blocked (SPEME) VEL bad batch at 0001
tib_batch_eod = {}     # (w,s,z) -> dict batch -> array
po_counter = [4500212000]


def new_po():
    po_counter[0] += int(R.integers(3, 40))
    return str(po_counter[0])


VENDOR_BY_CAT = {"Outerwear": ["V100231", "V100502", "V100418"], "Knitwear": ["V100077"], "Jersey": ["V100389"],
                 "Footwear": ["V100125"], "Accessories": ["V100389"], "Bottoms": ["V100502"]}


def fwd(arr, i, h):
    return arr[i:min(ND, i + h)].sum()


for w in ("IT10", "US20", "HK30"):
    for s in sorted(skus_by_w[w]):
        sizes = RUN[s]
        N = {z: net(w, s, z) for z in sizes}
        launch = LAUNCH[s]
        is_tib = SN[s] == "VEL"
        stock = {z: 0 for z in sizes}
        rc = {z: zeros() for z in sizes}          # receipts into 0001
        fixed = {z: False for z in sizes}
        # ---- key PO receipts (fixed totals): split by size
        kl = sorted(KEY_GR.get((w, s), []))
        if kl:
            first_gr = kl[0][0]
            # demand after first GR by size
            dpost = np.array([N[z][DI[first_gr]:].sum() for z in sizes], dtype=float)
            total = sum(q for _, q, _, _ in kl)
            need = dpost.copy()
            spare = total - need.sum()
            assert spare >= 0, (w, s, total, need.sum())
            alloc_tot = need + spare * CURVE[s]
            # split across lines in order: earlier lines take first
            fl = np.floor(alloc_tot).astype(int)
            rem = total - fl.sum()
            for j in np.argsort(-(alloc_tot - fl))[:rem]:
                fl[j] += 1
            left = fl.copy()
            for li, (gr, qty, ebeln, ebelp) in enumerate(kl):
                if li == len(kl) - 1:
                    part = left.copy()
                else:
                    # earliest line: demand until next GR first, rest by curve
                    nxt = kl[li + 1][0]
                    dd = np.array([N[z][DI[gr]:DI[nxt]].sum() for z in sizes], dtype=float)
                    base_ = np.minimum(dd, left)
                    sp = qty - base_.sum()
                    assert sp >= 0, (w, s, ebeln, ebelp)
                    want = base_ + sp * np.maximum(left - base_, 0) / max((left - base_).sum(), 1)
                    part = np.floor(want).astype(int)
                    r_ = qty - part.sum()
                    for j in np.argsort(-(want - part))[:r_]:
                        part[j] += 1
                    part = np.minimum(part, left)
                    # fix rounding
                    while part.sum() < qty:
                        j = int(np.argmax(left - part)); part[j] += 1
                left = left - part
                for j, z in enumerate(sizes):
                    if part[j]:
                        rc[z][DI[gr]] += part[j]
                        receipts.append(dict(werks=w, sku=s, size=z, date=gr, qty=int(part[j]), ebeln=ebeln, ebelp=ebelp,
                                             batch="", kind="KEY_PO"))
        # ---- opening stock & generic receipts
        lead_po = []  # pending generic receipt days for style-colour (to group sizes)
        blocked_sizes = {z for z in sizes if (s, z) in BLOCK}
        # opening stock
        for z in sizes:
            if launch and launch > dt.date(2026, 8, 1):
                stock0[(w, s, z)] = 0
            elif (s, z) in BLOCK:
                a, b = BLOCK[(s, z)]
                ia = DI.get(a, ND - 1)
                # exactly what is needed until the block (DC sold through)
                stock0[(w, s, z)] = int(N[z][:ia + 1].sum())
            elif sk.season[s] == "SS26":
                stock0[(w, s, z)] = int(N[z].sum()) + int(R.integers(0, 6))
            elif is_tib:
                stock0[(w, s, z)] = int(N[z][:DI[dt.date(2026, 8, 15)]].sum())
            else:
                f = fwd(N[z], 0, 35)
                stock0[(w, s, z)] = int(round(f * R.uniform(1.0, 1.6))) + (int(R.integers(1, 4)) if f > 0 else int(R.integers(0, 3)))
        # launch receipt (FW26 new styles): launch qty for the whole pre-block / first weeks
        if launch and launch > dt.date(2026, 8, 1):
            gr = launch - dt.timedelta(days=int(R.integers(12, 20)))
            while gr.weekday() >= 5:
                gr -= dt.timedelta(days=1)
            ebeln = new_po()
            for z in sizes:
                if (s, z) in BLOCK:
                    a, b = BLOCK[(s, z)]
                    q = int(N[z][:DI.get(a, ND - 1) + 1].sum())   # launch qty covers exactly until the DC runs dry
                else:
                    q = int(math.ceil(fwd(N[z], 0, DI[launch] + 28) * R.uniform(1.05, 1.3))) + 1
                if q:
                    rc[z][DI[gr]] += q
                    receipts.append(dict(werks=w, sku=s, size=z, date=gr, qty=q, ebeln=ebeln, ebelp="00010", batch="", kind="LAUNCH_BUY"))
        # VEL batches
        if is_tib:
            e1, e2 = new_po(), new_po()
            for z in sizes:
                gr1 = C.d(C.VALENTINO_V17["bad_batch_gr"][w]); gr2 = C.d(C.VALENTINO_V17["good_batch_gr"][w])
                q1 = int(math.ceil(N[z][DI[dt.date(2026, 8, 15)]:DI[dt.date(2026, 10, 3)]].sum() * 1.35)) + 2
                q2 = int(math.ceil(N[z][DI[dt.date(2026, 10, 3)]:].sum() * 1.6)) + 3
                rc[z][DI[gr1]] += q1; rc[z][DI[gr2]] += q2
                receipts.append(dict(werks=w, sku=s, size=z, date=gr1, qty=q1, ebeln=e1, ebelp="00010", batch=C.VALENTINO_V17["bad_batch"], kind="REGULAR"))
                receipts.append(dict(werks=w, sku=s, size=z, date=gr2, qty=q2, ebeln=e2, ebelp="00010", batch=C.VALENTINO_V17["good_batch"], kind="REGULAR"))
        # generic replenishment simulation (skip VEL, skip launch skus before launch receipt handled above)
        cur = {z: stock0[(w, s, z)] for z in sizes}
        eod = {z: zeros() for z in sizes}
        for i, x in enumerate(DAYS):
            if not is_tib and sk.season[s] not in ("SS26",):
                # check projected shortfall next 9 days on non-blocked, non-key sizes
                short = False
                for z in sizes:
                    if (s, z) in BLOCK:
                        a, b = BLOCK[(s, z)]
                        if x < b:        # inside or before block: no generic receipts
                            continue
                        if kl:
                            continue
                    if kl and x >= kl[0][0] - dt.timedelta(days=9):
                        continue
                    proj = cur[z] + rc[z][i:min(ND, i + 9)].sum() - fwd(N[z], i, 9)
                    if proj < 0:
                        short = True
                if short and x.weekday() < 6:
                    ebeln = new_po()
                    for z in sizes:
                        if (s, z) in BLOCK and (x < BLOCK[(s, z)][1] or kl):
                            continue
                        if kl and x >= kl[0][0] - dt.timedelta(days=9):
                            continue
                        want = fwd(N[z], i, 42) * R.uniform(1.1, 1.45) - (cur[z] + rc[z][i:min(ND, i + 9)].sum() - fwd(N[z], i, 9)) * 0
                        q = int(math.ceil(max(0, fwd(N[z], i, 42) * R.uniform(1.1, 1.45) - cur[z]
                                              - rc[z][i + 1:min(ND, i + 9)].sum())))
                        if fwd(N[z], i, 42) > 0 and q < 2:
                            q = 2 if cur[z] + rc[z][i:min(ND, i + 9)].sum() < fwd(N[z], i, 9) + 1 else q
                        if q:
                            rc[z][i] += q
                            receipts.append(dict(werks=w, sku=s, size=z, date=x, qty=q, ebeln=ebeln, ebelp="00010", batch="", kind="REGULAR"))
            for z in sizes:
                cur[z] += rc[z][i] - N[z][i]
                eod[z][i] = cur[z]
        for z in sizes:
            if eod[z].min() < 0:
                # fallback: should not happen; patch with an extra receipt on the first negative day
                i0 = int(np.argmax(eod[z] < 0))
                q = int(-eod[z].min()) + 1
                rc[z][i0] += q
                eod[z][i0:] += q
                receipts.append(dict(werks=w, sku=s, size=z, date=DAYS[i0], qty=q, ebeln=new_po(), ebelp="00010", batch="", kind="REGULAR"))
            main_eod[(w, s, z)] = eod[z]

# MAD01 mis-pick: book stock vs physical. Book: 999 issued (as per delivery), physically 742 left.
# Cycle count on Oct 6 finds +N black / -N navy -> inventory difference postings (701/702).
mis_qty = defaultdict(int)
for s in SH:
    if s["shipment_id"] in C.MISPICK["shipments"]:
        for ln in s["lines"]:
            if ln.get("sku_received") and ln["sku_received"] != ln["sku"]:
                mis_qty[ln["size"]] += ln["qty_shipped"]
ADJ_DAY = dt.date(2026, 10, 6)
adjustments = []
for z, q in mis_qty.items():
    k9, k7 = ("IT10", C.MISPICK["sku_ordered"], z), ("IT10", C.MISPICK["sku_received"], z)
    main_eod[k9][DI[ADJ_DAY]:] += q
    main_eod[k7][DI[ADJ_DAY]:] -= q
    adjustments.append((ADJ_DAY, "IT10", C.MISPICK["sku_ordered"], z, q, "701"))
    adjustments.append((ADJ_DAY, "IT10", C.MISPICK["sku_received"], z, -q, "702"))
    if main_eod[k7].min() < 0:
        i0 = int(np.argmax(main_eod[k7] < 0))
        add = int(-main_eod[k7].min()) + 2
        main_eod[k7][DI[dt.date(2026, 9, 28)]:] += add
        receipts.append(dict(werks="IT10", sku=C.MISPICK["sku_received"], size=z, date=dt.date(2026, 9, 28), qty=add,
                             ebeln=new_po(), ebelp="00010", batch="", kind="REGULAR"))

# VEL: FIFO batches & block on usage decision
UD = DI[C.d(C.VALENTINO_V17["usage_decision"])]
for (w, s, z), arr in list(main_eod.items()):
    if SN[s] != "VEL":
        continue
    N = net(w, s, z)
    b_old = stock0[(w, s, z)]
    r1 = [r for r in receipts if r["werks"] == w and r["sku"] == s and r["size"] == z and r["batch"] == C.VALENTINO_V17["bad_batch"]][0]
    r2 = [r for r in receipts if r["werks"] == w and r["sku"] == s and r["size"] == z and r["batch"] == C.VALENTINO_V17["good_batch"]][0]
    bo, bb, bg, blk = zeros(), zeros(), zeros(), zeros()
    o, b_, g, k = b_old, 0, 0, 0
    for i, x in enumerate(DAYS):
        if x == r1["date"]:
            b_ += r1["qty"]
        if x == r2["date"]:
            g += r2["qty"]
        if i == UD:
            k += b_; b_ = 0
        q = N[i]
        t = min(o, q); o -= t; q -= t
        t = min(b_, q); b_ -= t; q -= t
        t = min(g, q); g -= t; q -= t
        assert q == 0, (w, s, z, x)
        bo[i], bb[i], bg[i], blk[i] = o, b_, g, k
    tib_batch_eod[(w, s, z)] = {C.VALENTINO_V17["old_batch"]: bo, C.VALENTINO_V17["bad_batch"]: bb, C.VALENTINO_V17["good_batch"]: bg}
    tib_blocked[(w, s, z)] = blk
    main_eod[(w, s, z)] = bo + bb + bg

# ASTRA inter-DC STO IT10 -> HK30
sto_rows = []
STO_GI, STO_GR = dt.date(2026, 10, 15), dt.date(2026, 10, 21)
sto_in = defaultdict(zeros)
for (w, s, z), arr in list(main_eod.items()):
    if w == "IT10" and SN[s].startswith("ASTRA") and s.endswith("-999"):
        avail = int(arr[DI[STO_GI] - 1]) - int(net(w, s, z)[DI[STO_GI]:].sum())
        q = int(max(0, avail) * 0.45)
        if q > 0:
            arr[DI[STO_GI]:] -= q
            sto_rows.append(dict(sku=s, size=z, qty=q))
            sto_in[("HK30", s, z)][DI[STO_GR]] += q
for (w, s, z), arr in sto_in.items():
    if (w, s, z) in main_eod:
        main_eod[(w, s, z)] += np.cumsum(arr)
    else:
        main_eod[(w, s, z)] = np.cumsum(arr)

# returns stocks: QM01 (defective), RT01 (online returns + SS26 store returns, graded monthly)
qm_eod, rt_eod, out1_eod = {}, {}, {}
grading = []   # (date, werks, sku, size, to_0001, to_out1)
GRADE_DAYS = [dt.date(2026, 9, 1), dt.date(2026, 10, 1)]
for k in set(def_ret_in) | set(onl_ret_in) | set(ss26_ret_in):
    w, s, z = k
    qm_eod[k] = np.cumsum(def_ret_in[k])
    rt = zeros(); o1 = zeros(); to_main = zeros()
    cur = 0; cur_o = 0
    for i, x in enumerate(DAYS):
        cur += onl_ret_in[k][i] + ss26_ret_in[k][i]
        if x in GRADE_DAYS and cur > 0:
            # returns of items under DC constraint stay in RT01 (grading backlog - nobody released them)
            blocked_now = (s, z) in BLOCK
            if not blocked_now and sk.season[s] != "SS26":
                a_ = int(round(cur * 0.8)); b_ = cur - a_
                to_main[i] += a_; cur_o += b_
                grading.append((x, w, s, z, a_, b_))
                cur = 0
        if x == dt.date(2026, 9, 15):
            ss = int(ss26_ret_in[k][:i + 1].sum())
            if ss and sk.season[s] == "SS26":
                cur -= ss; cur_o += ss
                grading.append((x, w, s, z, 0, ss))
        rt[i] = cur; o1[i] = cur_o
    rt_eod[k] = rt; out1_eod[k] = o1
    if to_main.sum():
        if k in main_eod:
            main_eod[k] = main_eod[k] + np.cumsum(to_main)
        else:
            main_eod[k] = np.cumsum(to_main)

# sanity
neg = [(k, int(v.min())) for k, v in main_eod.items() if v.min() < 0]
print("negative keys:", neg[:10], len(neg))
for (s, z), (a, b) in BLOCK.items():
    for w in ("IT10", "US20", "HK30"):
        k = (w, s, z)
        if k in main_eod:
            ia, ib = DI.get(a + dt.timedelta(days=1), ND), DI.get(b, ND)
            if main_eod[k][ia:ib].max() > 0:
                print("BLOCK VIOLATION", k, main_eod[k][ia:ib].max())

all_keys = sorted(set(main_eod) | set(qm_eod) | set(web_eod))
pd.to_pickle(dict(main_eod=main_eod, qm_eod=qm_eod, rt_eod=rt_eod, out1_eod=out1_eod, web_eod=dict(web_eod),
                  tib_blocked=tib_blocked, tib_batch_eod=tib_batch_eod, receipts=receipts, open_orders=dict(open_orders),
                  stock0=stock0, sto_rows=sto_rows, adjustments=adjustments, grading=grading,
                  store_def=store_def_df), C.CACHE / "wms_state.pkl")
print("receipts", len(receipts), "keys", len(all_keys))
