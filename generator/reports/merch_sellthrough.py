"""Merchandising Planning - FW26 new-in sell-through report (XLSX), cut-off W42 (Sun 18/10/2026).

Definitions:
- ST% = cumulative units SOLD (gross, returns NOT netted) / cumulative units RECEIVED by the store
  (launch allocation + DC replenishments arrived), since launch date
- received reconstructed as on_hand(t) + sold_cum(t) - restocked_returns_cum(t)
Planted mistake: in 'Region summary' the region ST% is the simple (unweighted) average of store ST% instead of
sum(sold)/sum(received).
"""
import numpy as np
import pandas as pd
import xlsxwriter

from common import D, FW26_NEW, Facts, daily, outdir, pos, skus, stock, stores

OUTD = outdir("merchandising")
facts = Facts("merch")
CUTS = {"W40": D(2026, 10, 4), "W41": D(2026, 10, 11), "W42": D(2026, 10, 18)}
COLN = {"999": "BLACK", "510": "POWDER PINK", "20D": "OFF-WHITE", "23R": "CHOCOLATE", "742": "NAVY", "82D": "OLIVE",
        "001": "WHITE", "73A": "LIGHT BLUE"}


def st_at(d1):
    dd = daily()
    p = pos()
    x = dd[dd.style_name.isin(FW26_NEW) & (dd.date <= d1)]
    sold = x.groupby(["store_id", "sku"]).units_sold.sum()
    ret = p[(p.line_type == "RETURN") & p.style_name.isin(FW26_NEW) & (p.date <= d1) & (p.return_reason != "DEF")]
    ret = ret.groupby(["store_id", "sku"]).qty.sum().abs()
    s = stock(d1)
    oh = s[s.style_name.isin(FW26_NEW)].groupby(["store_id", "sku"]).on_hand.sum()
    t = pd.DataFrame({"sold": sold, "ret": ret, "oh": oh}).fillna(0)
    t["rec"] = t.oh + t.sold - t.ret
    t = t.reset_index().merge(skus()[["sku", "style_name", "color_code"]]).merge(
        stores()[["store_id", "store_name", "region", "subregion"]])
    t["st"] = np.where(t.rec > 0, t.sold / t.rec, np.nan)
    return t


def main():
    tabs = {k: st_at(v) for k, v in CUTS.items()}
    t = tabs["W42"]
    wb = xlsxwriter.Workbook(OUTD / "FW26_NewIn_SellThrough_wk42_final.xlsx")
    wb.set_properties({"title": "FW26 New-in sell-through wk42", "author": "Merchandising Planning - S. Bianchi"})
    F = lambda **kw: wb.add_format({"font_name": "Arial", "font_size": 9, **kw})
    hdr = F(bold=True, bg_color="#2E2E2E", font_color="white", border=1, align="center", text_wrap=True)
    txt = F(border=1)
    n0 = F(border=1, num_format="#,##0")
    pc = F(border=1, num_format="0%")
    title = F(bold=True, font_size=13)
    note = F(italic=True, font_color="#808080", font_size=8)

    ws = wb.add_worksheet("Read me")
    ws.set_column(0, 0, 120)
    rows = ["FW26 NEW-IN SELL-THROUGH - week 42 (cut-off Sunday 18/10/2026)", "",
            "Sell-through % = cumulative units sold since launch / cumulative units received in store (initial allocation + replenishments).",
            "Units sold = gross units sold at POS (customer returns are not deducted; exchanges count as a new sale).",
            "Units received = allocation at launch + DC replenishments with goods receipt posted.",
            "Launch dates: Collection FW26 03/09/2026; Couture ASTRA 24/09/2026.",
            "Not comparable with Finance/Regional sell-through on value (sales / sales + stock at retail).",
            "Colour conditional formatting: >=85% red (risk of stock-out), <=30% grey (slow).",
            "", "Merchandising Planning - Milano. Confidential - internal use only."]
    for i, r in enumerate(rows):
        ws.write(i, 0, r, title if i == 0 else F())

    # Style x region (correct weighted) with WoW
    ws = wb.add_worksheet("Style x Region")
    heads = ["Style", "Colour", "Region", "Received", "Sold", "On hand", "ST% W40", "ST% W41", "ST% W42", "Δ WoW pp"]
    for c, h in enumerate(heads):
        ws.write(0, c, h, hdr)
    ws.set_column(0, 0, 20)
    ws.set_column(1, 2, 13)
    ws.set_column(3, 9, 9)
    r = 1
    out = {}
    for (sty, col, reg), g in t.groupby(["style_name", "color_code", "region"]):
        sts = {}
        for k_, tt in tabs.items():
            h = tt[(tt.style_name == sty) & (tt.color_code == col) & (tt.region == reg)]
            sts[k_] = h.sold.sum() / h.rec.sum() if h.rec.sum() else np.nan
        ws.write(r, 0, sty, txt)
        ws.write(r, 1, COLN.get(col, col), txt)
        ws.write(r, 2, reg, txt)
        ws.write(r, 3, g.rec.sum(), n0)
        ws.write(r, 4, g.sold.sum(), n0)
        ws.write(r, 5, g.oh.sum(), n0)
        for j, k_ in enumerate(["W40", "W41", "W42"]):
            v = sts[k_]
            ws.write(r, 6 + j, "" if pd.isna(v) else v, pc)
        ws.write(r, 9, "" if pd.isna(sts["W41"]) else (sts["W42"] - sts["W41"]) * 100, F(border=1, num_format="+0;-0;0"))
        out[f"{sty}|{col}|{reg}"] = {k_: (None if pd.isna(v) else round(v * 100, 1)) for k_, v in sts.items()}
        r += 1
    ws.conditional_format(1, 6, r - 1, 8, {"type": "cell", "criteria": ">=", "value": 0.85, "format": F(bg_color="#F8CBAD")})
    ws.conditional_format(1, 6, r - 1, 8, {"type": "cell", "criteria": "<=", "value": 0.30, "format": F(bg_color="#D9D9D9")})
    ws.autofilter(0, 0, r - 1, 9)

    # Asia focus IRIDIA 510
    ws = wb.add_worksheet("IRIDIA pink Asia")
    w40 = tabs["W40"]
    ws.write(0, 0, "IRIDIA 510 POWDER PINK - Asian stores", title)
    heads = ["Store", "Received to W40", "Sold to W40", "ST% W40", "Received to W42", "Sold to W42", "ST% W42", "On hand 18/10"]
    for c, h in enumerate(heads):
        ws.write(2, c, h, hdr)
    ws.set_column(0, 0, 30)
    ws.set_column(1, 7, 12)
    asia = ["SEL01", "SEL02", "BUS01", "SHA01", "BJS01", "CDU01", "TYO01", "TYO02", "OSA01", "HKG01", "TPE01", "SIN01"]
    il = {}
    for i, sid in enumerate(asia):
        a = w40[(w40.store_id == sid) & (w40.style_name == "IRIDIA") & (w40.color_code == "510")]
        b = t[(t.store_id == sid) & (t.style_name == "IRIDIA") & (t.color_code == "510")]
        ws.write(3 + i, 0, f"{sid} {stores().set_index('store_id').store_name[sid]}", txt)
        vals = [a.rec.sum(), a.sold.sum(), a.sold.sum() / a.rec.sum() if a.rec.sum() else 0, b.rec.sum(), b.sold.sum(),
                b.sold.sum() / b.rec.sum() if b.rec.sum() else 0, b.oh.sum()]
        for c, v in enumerate(vals):
            ws.write(3 + i, 1 + c, v, pc if c in (2, 5) else n0)
        il[sid] = dict(st_w40=round(vals[2] * 100), st_w42=round(vals[5] * 100), oh=int(vals[6]))
    A = w40[w40.store_id.isin(asia) & (w40.style_name == "IRIDIA") & (w40.color_code == "510")]
    ws.write(4 + len(asia), 0, "Note: 600-unit production top-up landed at DC 08/10 and was allocated to Asia + Paris/London; "
             "Seoul Cheongdam replenishment cleared customs 13/10.", note)
    ws.conditional_format(3, 3, 3 + len(asia), 3, {"type": "cell", "criteria": ">=", "value": 0.85, "format": F(bg_color="#F8CBAD")})
    ws.conditional_format(3, 6, 3 + len(asia), 6, {"type": "cell", "criteria": ">=", "value": 0.85, "format": F(bg_color="#F8CBAD")})

    # Region summary (planted unweighted mean)
    ws = wb.add_worksheet("Region summary")
    ws.write(0, 0, "Region summary W42 - ST% by style (all colours)", title)
    regs = ["EMEA", "AMERICAS", "APAC"]
    for c, h in enumerate(["Style"] + [f"ST% {x}" for x in regs] + ["ST% TOTAL"]):
        ws.write(2, c, h, hdr)
    ws.set_column(0, 0, 22)
    ws.set_column(1, 4, 12)
    summ = {}
    for i, sty in enumerate(FW26_NEW):
        ws.write(3 + i, 0, sty, txt)
        g = t[t.style_name == sty]
        row = {}
        for j, reg in enumerate(regs):
            st_store = g[g.region == reg].groupby("store_id").apply(lambda x: x.sold.sum() / x.rec.sum() if x.rec.sum() else np.nan,
                                                                   include_groups=False)
            v = st_store.mean()  # <-- unweighted mean of store ST%
            w = g[g.region == reg].sold.sum() / g[g.region == reg].rec.sum()
            row[reg] = dict(shown=round(v * 100, 1), weighted=round(w * 100, 1))
            ws.write(3 + i, 1 + j, v, pc)
        tot = g.groupby("store_id").apply(lambda x: x.sold.sum() / x.rec.sum() if x.rec.sum() else np.nan, include_groups=False).mean()
        ws.write(3 + i, 4, tot, pc)
        row["TOTAL"] = dict(shown=round(tot * 100, 1), weighted=round(g.sold.sum() / g.rec.sum() * 100, 1))
        summ[sty] = row
    ws.write(4 + len(FW26_NEW), 0, "Region ST% = average of store sell-through.", note)

    # ASTRA by region chart
    ws = wb.add_worksheet("ASTRA")
    ws.write(0, 0, "Couture ASTRA - sell-through by sub-region (weighted), cut-off 18/10", title)
    pol = t[t.style_name.str.startswith("ASTRA")].groupby("subregion")[["rec", "sold"]].sum()
    pol["st"] = pol.sold / pol.rec
    pol = pol.sort_values("st", ascending=False)
    for c, h in enumerate(["Sub-region", "Received", "Sold", "ST%"]):
        ws.write(2, c, h, hdr)
    ws.set_column(0, 0, 18)
    for i, (sr, x) in enumerate(pol.iterrows()):
        ws.write(3 + i, 0, sr, txt)
        ws.write(3 + i, 1, x.rec, n0)
        ws.write(3 + i, 2, x.sold, n0)
        ws.write(3 + i, 3, x.st, pc)
    ch = wb.add_chart({"type": "bar"})
    ch.add_series({"name": "ST%", "categories": ["ASTRA", 3, 0, 2 + len(pol), 0], "values": ["ASTRA", 3, 3, 2 + len(pol), 3],
                   "fill": {"color": "#2E2E2E"}, "data_labels": {"value": True, "num_format": "0%"}})
    ch.set_legend({"none": True})
    ch.set_title({"name": "ASTRA ST% by sub-region"})
    ch.set_size({"width": 520, "height": 320})
    ws.insert_chart(3, 6, ch)

    # Store detail
    ws = wb.add_worksheet("Store detail")
    heads = ["Store", "Region", "Style", "Colour", "Received", "Sold", "Returned (restocked)", "On hand", "ST%"]
    for c, h in enumerate(heads):
        ws.write(0, c, h, hdr)
    ws.set_column(0, 0, 8)
    ws.set_column(2, 3, 18)
    for i, x in enumerate(t.groupby(["store_id", "region", "style_name", "color_code"])[["rec", "sold", "ret", "oh"]].sum().reset_index().itertuples()):
        ws.write(1 + i, 0, x.store_id, txt)
        ws.write(1 + i, 1, x.region, txt)
        ws.write(1 + i, 2, x.style_name, txt)
        ws.write(1 + i, 3, COLN.get(x.color_code, x.color_code), txt)
        ws.write(1 + i, 4, x.rec, n0)
        ws.write(1 + i, 5, x.sold, n0)
        ws.write(1 + i, 6, x.ret, n0)
        ws.write(1 + i, 7, x.oh, n0)
        ws.write(1 + i, 8, x.sold / x.rec if x.rec else "", pc)
    ws.autofilter(0, 0, len(t), 8)
    ws.freeze_panes(1, 0)

    # Highlights
    ws = wb.add_worksheet("Highlights")
    ws.set_column(0, 0, 130)
    a_il = A.sold.sum() / A.rec.sum()
    amb = t[(t.style_name == "AMALIA") & (t.color_code == "23R") & (t.region == "EMEA")]
    hl = [f"IRIDIA powder pink: Asian stores at {a_il * 100:.0f}% sell-through at W40 (core sizes sold out in 1-3 days after 02/10, only single pieces in fringe sizes 00/3/4 left). "
          "Top-up of 08/10 sold immediately in Asia; some EU/US stores still hold pink (Paris, Milano, New York).",
          f"AMALIA chocolate: EMEA sell-through {amb.sold.sum() / amb.rec.sum() * 100:.0f}% vs black {t[(t.style_name == 'AMALIA') & (t.color_code == '999') & (t.region == 'EMEA')].sold.sum() / t[(t.style_name == 'AMALIA') & (t.color_code == '999') & (t.region == 'EMEA')].rec.sum() * 100:.0f}%; sizes 0-1-2 broken, DC no stock until 10/11.",
          "ASTRA: Greater China well ahead of Europe and Americas - candidate for inter-region transfer.",
          "ARTEM: ST inflated by size exchanges (exchange = return + new sale); net sell-through lower.",
          "CASHMERE TURTLENECK chocolate performing in line with black - brown trend confirmed."]
    for i, h in enumerate(hl):
        ws.write(i, 0, h, F(text_wrap=True))
    wb.close()
    facts.update(dict(style_region=out, region_summary=summ, ilvaro_510_asia=il, ilvaro_510_asia_w40=round(a_il * 100, 1)))
    facts.save()


if __name__ == "__main__":
    main()
