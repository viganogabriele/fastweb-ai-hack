"""Retail Controlling weekly flash (XLSX), ISO weeks W36-W42 2026 + W40 v1 (wrong) / v2 corrected + CSV ranking.

Definitions (Retail Controlling, HQ Milano):
- Net sales = gross - discounts - returns (returns booked on the day they are processed), ex VAT
- EUR at the monthly average rate of the month containing the ISO-week Thursday (FX_MONTHLY); LY at LY monthly rate
- LFL: store trading >= 5 days in both CY week and LY ISO week, opened > 12 months; growth at constant (CY) FX
- Budget: EUR at budget rate (BI), actual for vs-budget also at budget rate
"""
import datetime as dt

import numpy as np
import pandas as pd
import xlsxwriter

from common import (D, FX_MONTHLY, fx_month, BUDGET_RATE, SAP_PLANT, Facts, daily, iso_week_range, kpi, outdir, pct, stores)

OUTD = outdir("retail_controlling", "weekly_flash")
facts = Facts("flash")

WEEK_NOTES = {
    36: ["FW26 new-in (IRIDIA, AMALIA, ARTEM, RIVIERA, Cashmere Turtleneck) on floor from Thu 03/09.",
         "MIA01: air-conditioning failure 3-5/09, store open but traffic down.",
         "SS26 residual stock returned to DC on 01/09 (no impact on sales, impact on stock KPIs)."],
    37: ["BHS01: heatwave Southern California, outerwear not moving (8-12/09).",
         "TOR01: TIFF from 10/09, good traffic.",
         "COU01 closed for the season from 13/09 -> out of LFL until reopening."],
    38: ["HKG01 closed Thu 17/09 (typhoon signal 8), reopened Fri 18/09 at 15:00. Kept in LFL.",
         "ROM01: works on Via Condotti pavement + scaffolding from 14/09, store reports footfall roughly halved.",
         "FW26 campaign US/UK live from 15/09 (OOH + digital)."],
    39: ["Milano Fashion Week 22-28/09: MIL01/MIL02 above budget.",
         "NYC01: UNGA week, Madison Ave frozen zones 21-26/09.",
         "AUREA black broken in sizes at PAR01, PAR02, MIL01, LON02; DC out of stock (supplier delay), ETA mid-October.",
         "Couture ASTRA capsule launched Thu 24/09 (China very good, Europe/US soft)."],
    40: ["Golden Week from 30/09: Chinese tourists in Milan/Paris/London; domestic travel in CN stores.",
         "Paris Fashion Week 29/09-07/10.",
         "CPH01: reduced opening hours 28/09-04/10 (staff shortage).",
         "VEL vest: first customer returns for zipper defect (reason code DEF) from 28/09 - see Quality."],
    41: ["NYC02: POS outage Tue 06/10 14:10-17:40; part of 06/10 receipts posted with business date 07/10. Not restated.",
         "MAD01: door counter down 01/10-07/10 (traffic = 0, conversion not meaningful).",
         "LON01: private client evening Thu 08/10.",
         "IRIDIA powder pink sold out in Asia within days (celebrity effect), DC top-up landed 08/10.",
         "SIN01: F1 GP weekend 09-11/10."],
    42: ["Cold snap Central/Northern Europe from 12/10: MUN01, ZRH01, BER01, GVA01, CPH01 strong on outerwear.",
         "Strikes: Paris transport Tue 13/10, Italy general strike Fri 16/10.",
         "Japan: clients buying ahead of 01/11 price increase (announced 09/10).",
         "SEL01: IRIDIA replenishment released by Incheon customs 13/10 (planned 08/10).",
         "Competitor pop-up opened in front of SEL01 on 15/10.",
         "AUREA black: DC re-supply received 16/10, store allocations shipping this week."],
}


def week_table(w, krw_override=None, dup_store=None, issued=None):
    d0, d1 = iso_week_range(2026, w)
    l0, l1 = iso_week_range(2025, w)
    thu, thu_ly = d0 + dt.timedelta(days=3), l0 + dt.timedelta(days=3)
    fx = dict(FX_MONTHLY[f"{thu.year}-{thu.month:02d}"])
    if issued and thu.month == 10 and thu.year == 2026:
        fx = fx_month(2026, 10, upto=issued - dt.timedelta(days=1))  # October = MTD average at issue date
    fx_ly = FX_MONTHLY[f"{thu_ly.year}-{thu_ly.month:02d}"]
    if krw_override:
        fx["KRW"] = krw_override
    k = kpi()
    st = stores().set_index("store_id")
    cy = k[(k.date >= d0) & (k.date <= d1)].groupby("store_id").agg(
        net_lc=("net_sales_lc", "sum"), units=("units", "sum"), ret_units=("returns_units", "sum"),
        receipts=("receipts", "sum"), visitors=("visitors_in", "sum"), budget_lc=("budget_lc", "sum"),
        net_eur_bud=("net_sales_eur_bud", "sum"), days=("date", "nunique"))
    lyk = k[(k.date >= l0) & (k.date <= l1)].groupby("store_id").agg(ly_lc=("net_sales_lc", "sum"),
                                                                       ly_days=("date", "nunique"))
    t = st[["store_name", "region", "subregion", "country", "currency", "store_type", "opening_date"]].join(cy).join(lyk)
    t = t.fillna({"net_lc": 0, "units": 0, "ret_units": 0, "receipts": 0, "visitors": 0, "budget_lc": 0,
                  "net_eur_bud": 0, "days": 0, "ly_lc": 0, "ly_days": 0})
    t["plant"] = [SAP_PLANT[s] for s in t.index]
    t["rate"] = t.currency.map(fx)
    t["net_eur"] = t.net_lc / t.rate
    t["ly_eur"] = t.ly_lc / t.currency.map(fx_ly)
    t["ly_eur_cfx"] = t.ly_lc / t.rate
    t["bud_eur"] = t.budget_lc / t.currency.map(BUDGET_RATE)
    t["lfl"] = (t.days >= 5) & (t.ly_days >= 5)
    t["conv"] = np.where(t.visitors > 0, t.receipts / t.visitors.replace(0, np.nan), np.nan)
    t["atv_eur"] = np.where(t.receipts > 0, t.net_eur / t.receipts.replace(0, np.nan), np.nan)
    t["upt"] = t.units / t.receipts.replace(0, np.nan)
    t["ret_rate"] = t.ret_units / t.units.replace(0, np.nan)
    t = t.reset_index().rename(columns={"index": "store_id"})
    if dup_store:
        t = pd.concat([t, t[t.store_id == dup_store]], ignore_index=True)
    region_order = {"EMEA": 0, "AMERICAS": 1, "APAC": 2}
    t["_r"] = t.region.map(region_order)
    t = t.sort_values(["_r", "plant"]).drop(columns="_r")
    return t, (d0, d1, l0, l1, thu, fx, fx_ly)


def summarise(t, by):
    g = t.groupby(by, sort=False).agg(net_eur=("net_eur", "sum"), ly_eur=("ly_eur", "sum"),
                                       net_eur_bud=("net_eur_bud", "sum"), bud_eur=("bud_eur", "sum"),
                                       units=("units", "sum"), ret_units=("ret_units", "sum"),
                                       receipts=("receipts", "sum"), visitors=("visitors", "sum"))
    lfl = t[t.lfl].groupby(by, sort=False).agg(lfl_cy=("net_eur", "sum"), lfl_ly=("ly_eur_cfx", "sum"))
    g = g.join(lfl)
    g["d_rep"] = (g.net_eur / g.ly_eur - 1) * 100
    g["d_lfl"] = (g.lfl_cy / g.lfl_ly - 1) * 100
    g["d_bud"] = (g.net_eur_bud / g.bud_eur - 1) * 100
    return g


def mtd(d1, fx):
    """month-to-date of the month of the week-end date, EUR at the same rates"""
    m0 = d1.replace(day=1)
    k = kpi()
    x = k[(k.date >= m0) & (k.date <= d1)].copy()
    x["eur"] = x.net_sales_lc / x.currency.map(fx)
    lyx = k[(k.date >= m0 - dt.timedelta(days=364)) & (k.date <= d1 - dt.timedelta(days=364))].copy()
    lyx["eur"] = lyx.net_sales_lc / lyx.currency.map(fx)
    a = x.groupby("region").eur.sum()
    b = lyx.groupby("region").eur.sum()
    return m0, a, b


def top_styles(d0, d1, fx):
    dd = daily()
    x = dd[(dd.date >= d0) & (dd.date <= d1)].copy()
    x["eur"] = x.net_sales_lc / x.currency.map(fx)
    g = x.groupby(["style_name", "category"]).agg(eur=("eur", "sum"), units=("units_sold", "sum"),
                                                   ret=("units_returned", "sum")).sort_values("eur", ascending=False)
    return g.head(15).reset_index()


def write_flash(w, fname, version, issued, krw_override=None, dup_store=None, changelog=None):
    t, (d0, d1, l0, l1, thu, fx, fx_ly) = week_table(w, krw_override, dup_store, issued)
    wb = xlsxwriter.Workbook(OUTD / fname)
    wb.set_properties({"title": f"Weekly Sales Flash W{w} 2026", "author": "Retail Controlling - M. Galli",
                       "company": "Valentino S.p.A.", "comments": f"version {version}"})
    F = lambda **kw: wb.add_format({"font_name": "Arial", "font_size": 9, **kw})
    title = F(bold=True, font_size=14, font_color="#1F2A44")
    sub = F(italic=True, font_color="#555555")
    hdr = F(bold=True, bg_color="#1F2A44", font_color="white", border=1, text_wrap=True, valign="vcenter", align="center")
    txt = F(border=1)
    txtb = F(border=1, bold=True, bg_color="#E7EBF3")
    k0 = F(border=1, num_format="#,##0")
    k0b = F(border=1, num_format="#,##0", bold=True, bg_color="#E7EBF3")
    k1 = F(border=1, num_format="#,##0.0")
    k1b = F(border=1, num_format="#,##0.0", bold=True, bg_color="#E7EBF3")
    p1 = F(border=1, num_format='+0.0%;[Red]-0.0%;0.0%')
    p1b = F(border=1, num_format='+0.0%;[Red]-0.0%;0.0%', bold=True, bg_color="#E7EBF3")
    pc = F(border=1, num_format="0.0%")
    rt = F(border=1, num_format="#,##0.000")
    foot = F(italic=True, font_size=8, font_color="#888888")
    conf = "Confidential - Internal use only. Source: SAP BW / POS (Xstore), store door counters. Retail Controlling."

    # ---------------- Cover
    ws = wb.add_worksheet("Cover")
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 3)
    ws.set_column(1, 1, 110)
    ws.write(1, 1, "VALENTINO  |  Retail Controlling", F(bold=True, font_size=10, font_color="#888888"))
    ws.write(3, 1, f"WEEKLY SALES FLASH - WEEK {w} / 2026", F(bold=True, font_size=20, font_color="#1F2A44"))
    ws.write(4, 1, f"Fiscal week {w}: {d0:%a %d/%m/%Y} - {d1:%a %d/%m/%Y}   |   LY comparable: wk {w} 2025 ({l0:%d/%m} - {l1:%d/%m/%Y})", sub)
    ws.write(5, 1, f"Version {version} - issued {issued:%d/%m/%Y} - distribution: ExCom, Regional MDs, Country Managers, Merchandising", sub)
    lines = ["Definitions",
             "Net sales = gross sales - discounts - returns (returns booked on the processing date), excluding VAT/sales taxes.",
             f"Reported EUR at average {thu:%B %Y} rates (month of the week's Thursday); LY at average {(l0 + dt.timedelta(days=3)):%B %Y} rates. See sheet FX.",
             "LFL = stores trading at least 5 days in both CY week and LY week; growth at constant FX (LY restated at CY rates).",
             "Budget comparison at budget FX rates (BI standard). Retail DOS only - e-commerce and wholesale excluded.",
             "Traffic from door counters (Xovis); shop-in-shops use department-store feed when available. Conversion = receipts / visitors."]
    for i, l in enumerate(lines):
        ws.write(7 + i, 1, l, F(bold=(i == 0), font_size=10 if i == 0 else 9))
    r = 15
    if changelog:
        ws.write(r, 1, "Change log", F(bold=True, font_size=10, font_color="#C00000"))
        for i, l in enumerate(changelog):
            ws.write(r + 1 + i, 1, l, F(font_color="#C00000"))
        r += len(changelog) + 2
    ws.write(r, 1, "Comments of the week", F(bold=True, font_size=10))
    for i, l in enumerate(WEEK_NOTES[w]):
        ws.write(r + 1 + i, 1, "- " + l)
    ws.write(r + 3 + len(WEEK_NOTES[w]), 1, conf, foot)

    # ---------------- Summary
    ws = wb.add_worksheet("Summary")
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 18)
    ws.set_column(1, 12, 11)
    ws.write(0, 0, f"Weekly flash W{w} 2026 - Summary by region (EUR k)", title)
    ws.write(1, 0, f"{d0:%d/%m} - {d1:%d/%m/%Y}  |  v{version}", sub)
    heads = ["Region", "Net Sales\nWk (EUR k)", "LY Wk\n(EUR k)", "Δ% rep.", "Δ% LFL\n(const. FX)", "Budget Wk\n(EUR k, bud FX)",
             "vs Bud %", "Units", "Returns\nunits", "Traffic", "Conv. %", "MTD (EUR k)", "MTD Δ%\nLY cFX"]
    ws.set_row(3, 30)
    for c, h in enumerate(heads):
        ws.write(3, c, h, hdr)
    g = summarise(t, "region")
    m0, mtd_cy, mtd_ly = mtd(d1, fx)
    row = 4
    for reg, x in g.iterrows():
        ws.write(row, 0, reg, txt)
        vals = [x.net_eur / 1e3, x.ly_eur / 1e3, x.d_rep / 100, x.d_lfl / 100, x.bud_eur / 1e3, x.d_bud / 100,
                x.units, x.ret_units, x.visitors, x.receipts / x.visitors, mtd_cy.get(reg, 0) / 1e3,
                mtd_cy.get(reg, 0) / mtd_ly.get(reg, 1) - 1]
        fm = [k1, k1, p1, p1, k1, p1, k0, k0, k0, pc, k1, p1]
        for c, (v, f_) in enumerate(zip(vals, fm)):
            ws.write(row, c + 1, v, f_)
        row += 1
    tot = summarise(t.assign(_all="TOTAL RETAIL"), "_all").iloc[0]
    ws.write(row, 0, "TOTAL RETAIL", txtb)
    vals = [tot.net_eur / 1e3, tot.ly_eur / 1e3, tot.d_rep / 100, tot.d_lfl / 100, tot.bud_eur / 1e3, tot.d_bud / 100,
            tot.units, tot.ret_units, tot.visitors, tot.receipts / tot.visitors, mtd_cy.sum() / 1e3, mtd_cy.sum() / mtd_ly.sum() - 1]
    for c, (v, f_) in enumerate(zip(vals, [k1b, k1b, p1b, p1b, k1b, p1b, k0b, k0b, k0b, pc, k1b, p1b])):
        ws.write(row, c + 1, v, f_)
    ws.write(row + 2, 0, f"MTD = {m0:%d/%m} to {d1:%d/%m}, EUR at the same rates as the week, LY = same days -364.", foot)
    ws.write(row + 3, 0, conf, foot)
    # chart
    ch = wb.add_chart({"type": "column"})
    n = len(g)
    ch.add_series({"name": "CY", "categories": ["Summary", 4, 0, 3 + n, 0], "values": ["Summary", 4, 1, 3 + n, 1],
                   "fill": {"color": "#1F2A44"}})
    ch.add_series({"name": "LY", "categories": ["Summary", 4, 0, 3 + n, 0], "values": ["Summary", 4, 2, 3 + n, 2],
                   "fill": {"color": "#A9B4C8"}})
    ch.set_title({"name": "Net sales by region, EUR k", "name_font": {"size": 10}})
    ch.set_legend({"position": "bottom"})
    ch.set_size({"width": 520, "height": 260})
    ws.insert_chart(row + 5, 0, ch)

    # ---------------- Stores
    ws = wb.add_worksheet("Stores")
    ws.freeze_panes(2, 3)
    heads = ["Plant", "Store", "Region", "Country", "Ccy", "Net Sales LC", "Net Sales EUR", "LY EUR", "Δ% rep.",
             "LFL", "Δ% LFL cFX", "Budget EUR (bud FX)", "vs Bud %", "Units", "Ret. units", "Ret. %", "Traffic",
             "Conv. %", "UPT", "ATV EUR", "Days open"]
    ws.write(0, 0, f"Store detail W{w} 2026", title)
    widths = [6, 30, 9, 16, 5, 12, 12, 12, 8, 5, 9, 12, 8, 7, 7, 7, 8, 7, 6, 8, 6]
    for c, (h, wd) in enumerate(zip(heads, widths)):
        ws.write(1, c, h, hdr)
        ws.set_column(c, c, wd)
    ws.set_row(1, 28)
    for i, x in enumerate(t.itertuples()):
        r = 2 + i
        ws.write_string(r, 0, x.plant, txt)
        ws.write(r, 1, x.store_name, txt)
        ws.write(r, 2, x.region, txt)
        ws.write(r, 3, x.country, txt)
        ws.write(r, 4, x.currency, txt)
        ws.write(r, 5, x.net_lc, k0)
        ws.write(r, 6, x.net_eur, k0)
        ws.write(r, 7, x.ly_eur, k0)
        ws.write(r, 8, x.net_eur / x.ly_eur - 1 if x.ly_eur else "n.a.", p1 if x.ly_eur else txt)
        ws.write(r, 9, "Y" if x.lfl else "N", txt)
        if x.lfl:
            ws.write(r, 10, x.net_eur / x.ly_eur_cfx - 1, p1)
        else:
            ws.write(r, 10, "", txt)
        ws.write(r, 11, x.bud_eur, k0)
        ws.write(r, 12, x.net_eur_bud / x.bud_eur - 1 if x.bud_eur else "", p1)
        ws.write(r, 13, x.units, k0)
        ws.write(r, 14, x.ret_units, k0)
        ws.write(r, 15, x.ret_rate if pd.notna(x.ret_rate) else "", pc)
        ws.write(r, 16, x.visitors, k0)
        if x.visitors > 0:
            ws.write(r, 17, x.receipts / x.visitors, pc)
        else:
            ws.write(r, 17, "n.m.", txt)
        ws.write(r, 18, x.upt if pd.notna(x.upt) else "", k1)
        ws.write(r, 19, x.atv_eur if pd.notna(x.atv_eur) else "", k0)
        ws.write(r, 20, x.days, k0)
    r = 2 + len(t)
    ws.write(r, 1, "TOTAL", txtb)
    for c, col in ((6, "net_eur"), (7, "ly_eur"), (11, "bud_eur"), (13, "units"), (14, "ret_units"), (16, "visitors")):
        ws.write(r, c, t[col].sum(), k0b)
    ws.write(r + 2, 1, conf, foot)

    # ---------------- Country
    ws = wb.add_worksheet("Country")
    gc = summarise(t, ["region", "country"])
    heads = ["Region", "Country", "Net Sales EUR k", "LY EUR k", "Δ% rep.", "Δ% LFL cFX", "vs Bud %", "Units"]
    ws.write(0, 0, f"Country view W{w} 2026", title)
    for c, h in enumerate(heads):
        ws.write(1, c, h, hdr)
    ws.set_column(0, 1, 18)
    ws.set_column(2, 7, 11)
    for i, ((reg, cty), x) in enumerate(gc.iterrows()):
        r = 2 + i
        ws.write(r, 0, reg, txt)
        ws.write(r, 1, cty, txt)
        ws.write(r, 2, x.net_eur / 1e3, k1)
        ws.write(r, 3, x.ly_eur / 1e3, k1)
        ws.write(r, 4, x.d_rep / 100, p1)
        ws.write(r, 5, x.d_lfl / 100 if pd.notna(x.d_lfl) else "", p1)
        ws.write(r, 6, x.d_bud / 100, p1)
        ws.write(r, 7, x.units, k0)

    # ---------------- Daily
    ws = wb.add_worksheet("Daily")
    k = kpi()
    x = k[(k.date >= d0) & (k.date <= d1)].copy()
    x["eur"] = x.net_sales_lc / x.currency.map(fx)
    pv = x.pivot_table(index="store_id", columns="date", values="eur", aggfunc="sum")
    ws.write(0, 0, f"Daily net sales EUR (current FX) - W{w}", title)
    days = [d0 + dt.timedelta(days=i) for i in range(7)]
    ws.write(1, 0, "Plant", hdr)
    ws.write(1, 1, "Store", hdr)
    for c, dd in enumerate(days):
        ws.write(1, 2 + c, dd.strftime("%a %d/%m"), hdr)
    ws.set_column(1, 1, 28)
    ws.set_column(2, 8, 10)
    for i, s in enumerate(t.store_id.drop_duplicates()):
        ws.write_string(2 + i, 0, SAP_PLANT[s], txt)
        ws.write(2 + i, 1, stores().set_index("store_id").store_name[s], txt)
        for c, dd in enumerate(days):
            v = pv.loc[s, dd] if (s in pv.index and dd in pv.columns) else np.nan
            ws.write(2 + i, 2 + c, "closed" if pd.isna(v) else v, txt if pd.isna(v) else k0)

    # ---------------- Top styles
    ws = wb.add_worksheet("Top styles")
    ts = top_styles(d0, d1, fx)
    ws.write(0, 0, f"Top 15 styles W{w} - net sales EUR (all stores)", title)
    for c, h in enumerate(["#", "Style", "Category", "Net sales EUR", "Units sold", "Units returned"]):
        ws.write(1, c, h, hdr)
    ws.set_column(1, 1, 26)
    ws.set_column(2, 5, 13)
    for i, x in enumerate(ts.itertuples()):
        ws.write(2 + i, 0, i + 1, txt)
        ws.write(2 + i, 1, x.style_name, txt)
        ws.write(2 + i, 2, x.category, txt)
        ws.write(2 + i, 3, x.eur, k0)
        ws.write(2 + i, 4, x.units, k0)
        ws.write(2 + i, 5, x.ret, k0)

    # ---------------- FX
    ws = wb.add_worksheet("FX")
    ws.write(0, 0, "Exchange rates used (local currency per 1 EUR)", title)
    for c, h in enumerate(["Ccy", f"CY avg {thu:%b-%y}", f"LY avg {(l0 + dt.timedelta(days=3)):%b-%y}", "Budget 2026"]):
        ws.write(1, c, h, hdr)
    ws.set_column(0, 3, 14)
    for i, c_ in enumerate(sorted(fx)):
        ws.write(2 + i, 0, c_, txt)
        ws.write(2 + i, 1, fx[c_], rt)
        ws.write(2 + i, 2, fx_ly[c_], rt)
        ws.write(2 + i, 3, BUDGET_RATE[c_], rt)
    ws.write(4 + len(fx), 0, "Source: Treasury, ECB reference rates monthly average. October = month-to-date average at issue date.", foot)
    wb.close()
    return t, g, tot


def main():
    issued = {36: D(2026, 9, 8), 37: D(2026, 9, 15), 38: D(2026, 9, 22), 39: D(2026, 9, 29), 40: D(2026, 10, 6),
              41: D(2026, 10, 13), 42: D(2026, 10, 20)}
    for w in range(36, 43):
        if w == 40:
            continue
        t, g, tot = write_flash(w, f"Flash_W{w}_2026.xlsx", "1.0", issued[w])
        facts[f"W{w}"] = dict(total_eur=round(tot.net_eur), ly_eur=round(tot.ly_eur), d_rep=round(tot.d_rep, 1),
                              d_lfl=round(tot.d_lfl, 1), d_bud=round(tot.d_bud, 1),
                              regions={r: dict(eur=round(x.net_eur), d_rep=round(x.d_rep, 1), d_lfl=round(x.d_lfl, 1))
                                       for r, x in g.iterrows()},
                              non_lfl=t[~t.lfl].store_id.tolist())
    # W40 v1 with errors: KRW digits transposed and DXB01 duplicated
    krw_ok = fx_month(2026, 10, upto=D(2026, 10, 5))["KRW"]
    ks = f"{krw_ok:.1f}"
    krw_bad = float(ks[0] + ks[2] + ks[1] + ks[3:])
    t1, g1, tot1 = write_flash(40, "Flash_W40_2026_v1.xlsx", "1.0", D(2026, 10, 6), krw_override=krw_bad, dup_store="DXB01")
    t2, g2, tot2 = write_flash(40, "Flash_W40_2026_v2_corrected.xlsx", "2.0", D(2026, 10, 6), changelog=[
        "v2 (07/10/2026) replaces v1 of 06/10/2026:",
        f"- KRW average rate corrected to {krw_ok:,.1f} (v1 used {krw_bad:,.1f} - typo in FX upload). Korea and APAC restated.",
        "- Dubai Mall (plant 1801) appeared twice in v1 store list (double feed load), EMEA total restated.",
        "Please discard v1."])
    facts["W40_fx_krw"] = dict(correct=krw_ok, wrong=krw_bad)
    facts["W40_v1"] = dict(total_eur=round(tot1.net_eur), regions={r: round(x.net_eur) for r, x in g1.iterrows()},
                           korea_eur=round(t1[t1.country == "South Korea"].net_eur.sum()))
    facts["W40_v2"] = dict(total_eur=round(tot2.net_eur), ly_eur=round(tot2.ly_eur), d_rep=round(tot2.d_rep, 1),
                           d_lfl=round(tot2.d_lfl, 1), d_bud=round(tot2.d_bud, 1), non_lfl=t2[~t2.lfl].store_id.tolist(),
                           regions={r: dict(eur=round(x.net_eur), d_rep=round(x.d_rep, 1))
                                                                for r, x in g2.iterrows()},
                           korea_eur=round(t2[t2.country == "South Korea"].net_eur.sum()),
                           dxb_eur=round(t2[t2.store_id == "DXB01"].net_eur.sum()))
    # CSV export of W42 store ranking from the Italian BI (semicolon, decimal comma, latin-1, dd.mm.yyyy)
    t, info = week_table(42, issued=D(2026, 10, 20))
    t = t.sort_values("net_eur", ascending=False)
    csv = pd.DataFrame({"Rank": range(1, len(t) + 1), "Cod. negozio": t.plant.values, "Negozio": t.store_name.values,
                        "Area": t.region.values, "Venduto netto EUR": t.net_eur.round(2).values,
                        "Var. % AP": ((t.net_eur / t.ly_eur - 1) * 100).round(1).values,
                        "Ingressi": t.visitors.astype(int).values,
                        "Conv. %": (t.receipts / t.visitors.replace(0, np.nan) * 100).round(1).values,
                        "Data estrazione": "19.10.2026"})
    csv.to_csv(OUTD / "export_classifica_negozi_sett42.csv", sep=";", decimal=",", index=False, encoding="latin-1",
               errors="replace")
    facts.save()


if __name__ == "__main__":
    main()
