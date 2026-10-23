"""EMEA Monthly Business Review - September 2026 (PDF, v3 FINAL).

Author definitions: calendar month; EUR at BUDGET rates; net of returns; LFL = standalone DOS only (excludes
shop-in-shops and seasonal resort stores); sell-through on VALUE = sales at retail / (sales + EOP stock at retail).
Planted issues: exec summary quotes LFL from v2 (ROM01 excluded); country table TOTAL excludes Middle East;
director claims Korean clients >10% of Saint-Honoré sales (POS says ~5%).
"""
import datetime as dt
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate, Paragraph,
                                Spacer)

from common import BUDGET_RATE, D, FW26_NEW, SHOP_IN_SHOP, Facts, daily, kpi, outdir, pos, prices, stock, stores
from pdfkit import fmt_pct, register_fonts, savefig, style, table

register_fonts()
OUTD = outdir("emea")
TMP = Path(__file__).parent / "_tmp"
TMP.mkdir(exist_ok=True)
facts = Facts("emea_mbr")

INK = colors.HexColor("#1A1A1A")
ACC = colors.HexColor("#8C1D2C")  # bordeaux
GREY = colors.HexColor("#6E6E6E")
LIGHT = colors.HexColor("#F2EFEA")
M0, M1 = D(2026, 9, 1), D(2026, 9, 30)
L0, L1 = D(2025, 9, 1), D(2025, 9, 30)
SEASONAL = ["COU01", "CRT01", "STM01"]
COUNTRY_GROUP = {"Italy": "Italy", "France": "France", "United Kingdom": "UK", "Germany": "Germany",
                 "Switzerland": "Switzerland", "Spain": "Spain", "Netherlands": "Benelux", "Denmark": "Nordics",
                 "United Arab Emirates": "Middle East"}


def store_table():
    k = kpi()
    e = k[k.region == "EMEA"]
    agg = dict(net=("net_sales_eur_bud", "sum"), lc=("net_sales_lc", "sum"), vis=("visitors_in", "sum"),
               rec=("receipts", "sum"), units=("units", "sum"), bud_lc=("budget_lc", "sum"), ret=("returns_units", "sum"))
    cy = e[(e.date >= M0) & (e.date <= M1)].groupby("store_id").agg(**agg)
    ly = e[(e.date >= L0) & (e.date <= L1)].groupby("store_id").agg(**agg).add_suffix("_ly")
    st = stores().set_index("store_id")
    t = cy.join(ly).join(st[["store_name", "country", "store_type", "currency"]])
    t["bud"] = t.bud_lc / t.currency.map(BUDGET_RATE)
    t["grp"] = t.country.map(COUNTRY_GROUP)
    t["lfl"] = ~t.index.isin(SHOP_IN_SHOP + SEASONAL)
    return t


def sellthrough_value():
    dd = daily()
    e = dd[(dd.region == "EMEA") & (dd.style_name.isin(FW26_NEW)) & (dd.date <= M1) & (dd.date >= D(2026, 9, 3))].copy()
    e["eur"] = e.net_sales_lc / e.currency.map(BUDGET_RATE)
    sales = e.groupby("style_name").eur.sum()
    units = e.groupby("style_name").units_sold.sum()
    s = stock(M1)
    s = s[s.style_name.isin(FW26_NEW)]
    s = s.merge(stores()[["store_id", "region", "currency"]], on="store_id")
    s = s[s.region == "EMEA"].merge(prices()[["store_id", "sku", "retail_price"]], on=["store_id", "sku"], how="left")
    s["val"] = s.on_hand * s.retail_price / s.currency.map(BUDGET_RATE)
    stockv = s.groupby("style_name").val.sum()
    stocku = s.groupby("style_name").on_hand.sum()
    t = pd.DataFrame({"sales_eur": sales, "stock_eur": stockv, "units": units, "stock_units": stocku}).fillna(0)
    t["st_value"] = t.sales_eur / (t.sales_eur + t.stock_eur) * 100
    return t.sort_values("st_value", ascending=False)


def nationality():
    p = pos()
    x = p[(p.region == "EMEA") & (p.line_type == "SALE")]
    out = {}
    for lab, a, b in (("Aug", D(2026, 8, 1), D(2026, 8, 31)), ("Sep", M0, M1)):
        y = x[(x.date >= a) & (x.date <= b)]
        sh = y.groupby("customer_nationality").net_amount.sum()
        # mixed currencies -> use budget EUR
        y = y.assign(eur=y.net_amount / y.currency.map(BUDGET_RATE))
        sh = y.groupby("customer_nationality").eur.sum()
        out[lab] = sh / sh.sum() * 100
    par = x[(x.store_id == "PAR01") & (x.date >= M0) & (x.date <= M1)]
    kr_par = par[par.customer_nationality == "KR"].net_amount.sum() / par.net_amount.sum() * 100
    return pd.DataFrame(out).fillna(0), kr_par


def charts(t, st):
    k = kpi()
    e = k[k.region == "EMEA"]
    cy = e[(e.date >= M0) & (e.date <= M1)].groupby("date").net_sales_eur_bud.sum()
    ly = e[(e.date >= M0 - dt.timedelta(days=364)) & (e.date <= M1 - dt.timedelta(days=364))].groupby("date").net_sales_eur_bud.sum()
    fig, ax = plt.subplots(figsize=(7.5, 2.6))
    ax.plot(range(1, 31), cy.values / 1e3, color="#8C1D2C", lw=2, label="2026")
    ax.plot(range(1, 31), ly.values / 1e3, color="#9C9C9C", lw=1.4, ls="--", label="2025 (same weekday)")
    ax.set_xticks(range(1, 31, 2))
    ax.set_ylabel("EUR k")
    ax.set_title("EMEA daily net sales, September", fontsize=9, loc="left")
    ax.legend(frameon=False, fontsize=7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=7)
    f1 = savefig(fig, TMP / "emea_daily.png")

    g = t.groupby("grp")[["net", "net_ly"]].sum().sort_values("net", ascending=True)
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    y = np.arange(len(g))
    ax.barh(y + 0.2, g.net / 1e3, height=0.38, color="#8C1D2C", label="Sep 26")
    ax.barh(y - 0.2, g.net_ly / 1e3, height=0.38, color="#C9C1B6", label="Sep 25")
    ax.set_yticks(y, g.index, fontsize=7)
    ax.tick_params(labelsize=7)
    ax.set_xlabel("EUR k (budget FX)", fontsize=7)
    ax.legend(frameon=False, fontsize=7, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    f2 = savefig(fig, TMP / "emea_country.png")

    fig, ax = plt.subplots(figsize=(7.5, 2.6))
    tt = t.sort_values("net", ascending=False)
    conv = tt.rec / tt.vis * 100
    conv_ly = tt.rec_ly / tt.vis_ly * 100
    x = np.arange(len(tt))
    ax.bar(x - 0.2, conv, 0.4, color="#1A1A1A", label="Conv. % Sep 26")
    ax.bar(x + 0.2, conv_ly, 0.4, color="#C9C1B6", label="Conv. % Sep 25")
    ax.set_xticks(x, tt.index, rotation=60, fontsize=6.5)
    ax.tick_params(labelsize=7)
    ax.legend(frameon=False, fontsize=7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("Conversion by store (receipts / visitors)", fontsize=9, loc="left")
    f3 = savefig(fig, TMP / "emea_conv.png")

    fig, ax = plt.subplots(figsize=(4.0, 2.8))
    ax.barh(st.index[::-1], st.st_value[::-1], color="#8C1D2C")
    for i, v in enumerate(st.st_value[::-1]):
        ax.text(v + 0.5, i, f"{v:.0f}%", va="center", fontsize=7)
    ax.set_xlim(0, max(60, st.st_value.max() + 10))
    ax.tick_params(labelsize=7)
    ax.set_title("FW26 new-in sell-through (value), 30/09", fontsize=8, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    f4 = savefig(fig, TMP / "emea_st.png")

    r = k[(k.store_id == "ROM01") & (k.date >= D(2026, 8, 24)) & (k.date <= M1)].set_index("date").visitors_in
    rl = k[(k.store_id == "ROM01") & (k.date >= D(2026, 8, 24) - dt.timedelta(days=364)) &
           (k.date <= M1 - dt.timedelta(days=364))].set_index("date").visitors_in
    fig, ax = plt.subplots(figsize=(4.0, 2.4))
    ax.plot(range(len(r)), r.values, color="#8C1D2C", lw=1.8, label="2026")
    ax.plot(range(len(rl)), rl.values, color="#9C9C9C", lw=1.2, ls="--", label="2025")
    i14 = list(r.index).index(D(2026, 9, 14))
    ax.axvline(i14, color="black", lw=0.8)
    ax.text(i14 + 0.5, max(r.max(), rl.max()) * 0.95, "works start 14/09", fontsize=6.5)
    ax.set_xticks(range(0, len(r), 7), [d.strftime("%d/%m") for d in list(r.index)[::7]], fontsize=6.5)
    ax.tick_params(labelsize=7)
    ax.legend(frameon=False, fontsize=6.5)
    ax.set_title("ROM01 Via Condotti - daily visitors", fontsize=8, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    f5 = savefig(fig, TMP / "emea_rom.png")
    return f1, f2, f3, f4, f5


def main():
    t = store_table()
    st = sellthrough_value()
    nat, kr_par = nationality()
    f1, f2, f3, f4, f5 = charts(t, st)

    tot_net, tot_ly, tot_bud = t.net.sum(), t.net_ly.sum(), t.bud.sum()
    lfl = t[t.lfl]
    lfl_g = (lfl.net.sum() / lfl.net_ly.sum() - 1) * 100
    lfl_v2 = lfl.drop(index="ROM01")
    lfl_g_v2 = (lfl_v2.net.sum() / lfl_v2.net_ly.sum() - 1) * 100
    vs_bud = (tot_net / tot_bud - 1) * 100
    rep_g = (tot_net / tot_ly - 1) * 100
    traffic_g = (t.vis.sum() / t.vis_ly.sum() - 1) * 100
    conv, conv_ly = t.rec.sum() / t.vis.sum() * 100, t.rec_ly.sum() / t.vis_ly.sum() * 100
    rom = t.loc["ROM01"]
    k = kpi()
    rom_since = k[(k.store_id == "ROM01") & (k.date >= D(2026, 9, 14)) & (k.date <= M1)].visitors_in.sum()
    rom_since_ly = k[(k.store_id == "ROM01") & (k.date >= D(2026, 9, 14) - dt.timedelta(days=364)) &
                     (k.date <= M1 - dt.timedelta(days=364))].visitors_in.sum()
    rom_traffic_since = (rom_since / rom_since_ly - 1) * 100

    S = dict(
        h1=style("h1", "NSerif-B", 17, color=INK, spaceAfter=4),
        h2=style("h2", "NSerif-B", 12, color=ACC, spaceBefore=6, spaceAfter=4),
        body=style("body", "LibSans", 8.8, leading=12, color=INK, spaceAfter=4),
        small=style("small", "LibSans-I", 7, color=GREY),
        quote=style("quote", "NSerif-I", 9.2, leading=13.5, color=INK, leftIndent=8, spaceAfter=6),
        bul=style("bul", "LibSans", 8.8, leading=12, color=INK, leftIndent=10, bulletIndent=2, spaceAfter=2),
    )

    def on_page(c, doc):
        c.saveState()
        w, h = landscape(A4)
        c.setFont("NSerif-B", 9)
        c.setFillColor(INK)
        c.drawString(15 * mm, h - 11 * mm, "VALENTINO")
        c.setFont("LibSans", 7)
        c.setFillColor(GREY)
        c.drawString(38 * mm, h - 11 * mm, "EMEA Retail  |  Monthly Business Review  |  September 2026")
        c.drawRightString(w - 15 * mm, h - 11 * mm, "v3 FINAL - 09/10/2026")
        c.setStrokeColor(colors.HexColor("#D8D2C8"))
        c.line(15 * mm, h - 13 * mm, w - 15 * mm, h - 13 * mm)
        c.drawString(15 * mm, 8 * mm, "Confidential - Internal use only. Do not forward outside the EMEA leadership team.")
        c.drawRightString(w - 15 * mm, 8 * mm, f"{doc.page}")
        c.restoreState()

    def on_cover(c, doc):
        c.saveState()
        w, h = landscape(A4)
        c.setFillColor(INK)
        c.rect(0, 0, w, h, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("NSerif-B", 30)
        c.drawString(25 * mm, h - 60 * mm, "VALENTINO")
        c.setFont("NSerif-L", 22)
        c.drawString(25 * mm, h - 85 * mm, "EMEA Monthly Business Review")
        c.setFont("NSerif", 16)
        c.setFillColor(colors.HexColor("#C9A96E"))
        c.drawString(25 * mm, h - 97 * mm, "September 2026")
        c.setFillColor(colors.HexColor("#BBBBBB"))
        c.setFont("LibSans", 9)
        c.drawString(25 * mm, 40 * mm, "Prepared by: EMEA Retail Excellence & Planning (Milano)")
        c.drawString(25 * mm, 34 * mm, "Commentary: F. Arrighi, EMEA Retail Director")
        c.drawString(25 * mm, 28 * mm, "Version 3 FINAL - 9 October 2026 - supersedes v2 of 7 October")
        c.drawString(25 * mm, 16 * mm, "Confidential - Internal use only")
        c.restoreState()

    path = OUTD / "EMEA_MBR_Sep26_v3_FINAL.pdf"
    doc = BaseDocTemplate(str(path), pagesize=landscape(A4), leftMargin=15 * mm, rightMargin=15 * mm,
                          topMargin=18 * mm, bottomMargin=14 * mm, title="EMEA MBR September 2026",
                          author="EMEA Retail Excellence & Planning")
    fr = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
    w2 = (doc.width - 8 * mm) / 2
    frl = Frame(doc.leftMargin, doc.bottomMargin, w2, doc.height, id="l")
    frr = Frame(doc.leftMargin + w2 + 8 * mm, doc.bottomMargin, w2, doc.height, id="r")
    doc.addPageTemplates([PageTemplate("cover", [fr], onPage=on_cover), PageTemplate("full", [fr], onPage=on_page),
                          PageTemplate("two", [frl, frr], onPage=on_page)])
    from reportlab.platypus import NextPageTemplate as NPT
    E = []
    E += [NPT("full"), Spacer(1, 1), PageBreak()]

    # ---- p2 exec summary
    E.append(Paragraph("1. Executive summary", S["h1"]))
    bullets = [
        f"September closed at <b>EUR {tot_net / 1e6:.2f} m</b> net sales (budget FX), <b>{fmt_pct(rep_g)}</b> vs LY and "
        f"<b>{fmt_pct(vs_bud)}</b> vs budget.",
        f"Like-for-like (standalone DOS) <b>{fmt_pct(lfl_g_v2)}</b>, driven by Milano Montenapoleone, Saint-Honoré, "
        "New Bond Street and Venezia. Traffic " + fmt_pct(traffic_g) + ", conversion " + f"{conv:.1f}% (LY {conv_ly:.1f}%).",
        "Fashion weeks (Milano 22-28/09, Paris from 29/09) and the first days of Golden Week gave a strong last 10 days.",
        f"Roma Via Condotti {fmt_pct((rom.net / rom.net_ly - 1) * 100)}: pavement works and scaffolding since 14/09 "
        f"(visitors {fmt_pct(rom_traffic_since, 0)} vs LY since the start of the works).",
        "Lost sales on black AUREA in Paris, Milano and Harrods (Korean demand) - no stock at DC until mid-October.",
        "FW26 new-in: AMALIA (brown) leads outerwear sell-through on value; Couture ASTRA slow in EMEA (fit/price).",
        "First VEL vest returns for zipper defect at the end of the month - Quality investigation open.",
    ]
    for b in bullets:
        E.append(Paragraph(b, S["bul"], bulletText="■"))
    E.append(Spacer(1, 6))
    rows = [["KPI", "Sep 2026", "Sep 2025", "Δ", "Budget", "vs Bud"],
            ["Net sales (EUR k)", f"{tot_net / 1e3:,.0f}", f"{tot_ly / 1e3:,.0f}", fmt_pct(rep_g), f"{tot_bud / 1e3:,.0f}", fmt_pct(vs_bud)],
            ["Net sales LFL (EUR k)", f"{lfl.net.sum() / 1e3:,.0f}", f"{lfl.net_ly.sum() / 1e3:,.0f}", fmt_pct(lfl_g), "", ""],
            ["Visitors", f"{t.vis.sum():,.0f}", f"{t.vis_ly.sum():,.0f}", fmt_pct(traffic_g), "", ""],
            ["Conversion", f"{conv:.1f}%", f"{conv_ly:.1f}%", f"{conv - conv_ly:+.1f} pp", "", ""],
            ["Units", f"{t.units.sum():,.0f}", f"{t.units_ly.sum():,.0f}", fmt_pct((t.units.sum() / t.units_ly.sum() - 1) * 100), "", ""],
            ["ATV (EUR)", f"{tot_net / t.rec.sum():,.0f}", f"{tot_ly / t.rec_ly.sum():,.0f}",
             fmt_pct(((tot_net / t.rec.sum()) / (tot_ly / t.rec_ly.sum()) - 1) * 100), "", ""],
            ["Return rate (units)", f"{t.ret.sum() / t.units.sum() * 100:.1f}%", f"{t.ret_ly.sum() / t.units_ly.sum() * 100:.1f}%", "", "", ""]]
    E.append(table(rows, [60 * mm, 32 * mm, 32 * mm, 26 * mm, 32 * mm, 26 * mm], ACC, zebra=LIGHT))
    E.append(Spacer(1, 4))
    E.append(Paragraph("EUR at budget rates 2026. Net of returns, excluding VAT. LFL perimeter: standalone directly operated stores "
                       "open in both periods (excludes shop-in-shops MIL02, PAR02, LON02, BER01 and seasonal stores COU01, CRT01, STM01).",
                       S["small"]))
    E.append(Spacer(1, 6))
    E.append(Image(f1, width=200 * mm, height=69 * mm))
    E += [NPT("two"), PageBreak()]

    # ---- p3 countries
    E.append(Paragraph("2. Performance by country", S["h1"]))
    gc = t.groupby("grp").agg(net=("net", "sum"), net_ly=("net_ly", "sum"), bud=("bud", "sum"), vis=("vis", "sum"),
                              vis_ly=("vis_ly", "sum"))
    order = ["Italy", "France", "UK", "Germany", "Switzerland", "Spain", "Benelux", "Nordics", "Middle East"]
    gc = gc.loc[order]
    rows = [["Country", "Net sales EUR k", "LY EUR k", "Δ% LY", "vs Bud", "Traffic Δ%"]]
    for c_, x in gc.iterrows():
        rows.append([c_, f"{x.net / 1e3:,.0f}", f"{x.net_ly / 1e3:,.0f}", fmt_pct((x.net / x.net_ly - 1) * 100),
                     fmt_pct((x.net / x.bud - 1) * 100), fmt_pct((x.vis / x.vis_ly - 1) * 100)])
    eu = gc.drop(index="Middle East")  # <-- planted: TOTAL excludes Middle East
    rows.append(["TOTAL EMEA", f"{eu.net.sum() / 1e3:,.0f}", f"{eu.net_ly.sum() / 1e3:,.0f}",
                 fmt_pct((eu.net.sum() / eu.net_ly.sum() - 1) * 100), fmt_pct((eu.net.sum() / eu.bud.sum() - 1) * 100),
                 fmt_pct((eu.vis.sum() / eu.vis_ly.sum() - 1) * 100)])
    E.append(table(rows, [28 * mm, 26 * mm, 22 * mm, 18 * mm, 18 * mm, 18 * mm], ACC, zebra=LIGHT, bold_last=True))
    E.append(Spacer(1, 6))
    it = t[t.grp == "Italy"]
    fr_ = t[t.grp == "France"]
    E.append(Paragraph(
        f"<b>Italy</b> {fmt_pct((it.net.sum() / it.net_ly.sum() - 1) * 100)}: Venezia exceptional "
        f"({fmt_pct((t.loc['VEN01'].net / t.loc['VEN01'].net_ly - 1) * 100)}), Montenapoleone strong during fashion week, "
        "Rinascente flat. Roma heavily penalised by the works on Via Condotti. Courmayeur closed from 13/09 as planned.", S["body"]))
    E.append(Paragraph(
        f"<b>France</b> {fmt_pct((fr_.net.sum() / fr_.net_ly.sum() - 1) * 100)}: Saint-Honoré "
        f"{fmt_pct((t.loc['PAR01'].net / t.loc['PAR01'].net_ly - 1) * 100)} with Korean and Chinese clientele, Galeries Lafayette "
        "flat on traffic up double digit (conversion issue at the corner, staffing on weekends).", S["body"]))
    E.append(Paragraph(
        f"<b>UK</b>: New Bond Street {fmt_pct((t.loc['LON01'].net / t.loc['LON01'].net_ly - 1) * 100)} supported by the FW26 campaign; "
        f"Harrods {fmt_pct((t.loc['LON02'].net / t.loc['LON02'].net_ly - 1) * 100)} - black AUREA out of stock from the 3rd week.",
        S["body"]))
    E.append(Paragraph(
        f"<b>Switzerland</b>: Genève {fmt_pct((t.loc['GVA01'].net / t.loc['GVA01'].net_ly - 1) * 100)} (fewer Middle East clients), "
        f"Zürich {fmt_pct((t.loc['ZRH01'].net / t.loc['ZRH01'].net_ly - 1) * 100)}. <b>Middle East</b>: Dubai Mall "
        f"{fmt_pct((t.loc['DXB01'].net / t.loc['DXB01'].net_ly - 1) * 100)}, summer season still hot.", S["body"]))
    from reportlab.platypus import FrameBreak
    E.append(FrameBreak())
    E.append(Spacer(1, 22))
    E.append(Image(f2, width=125 * mm, height=89 * mm))
    E += [NPT("full"), PageBreak()]

    # ---- p4 stores
    E.append(Paragraph("3. Store ranking", S["h1"]))
    rows = [["Store", "Type", "Net sales EUR k", "LY EUR k", "Δ% LY", "LFL", "vs Bud", "Visitors", "Traffic Δ%",
             "Conv.", "ATV EUR", "UPT", "Ret. %"]]
    for sid, x in t.sort_values("net", ascending=False).iterrows():
        rows.append([f"{sid} {x.store_name}", x.store_type, f"{x.net / 1e3:,.0f}", f"{x.net_ly / 1e3:,.0f}",
                     fmt_pct((x.net / x.net_ly - 1) * 100), "Y" if x.lfl else "-", fmt_pct((x.net / x.bud - 1) * 100),
                     f"{x.vis:,.0f}", fmt_pct((x.vis / x.vis_ly - 1) * 100), f"{x.rec / x.vis * 100:.1f}%",
                     f"{x.net / x.rec:,.0f}", f"{x.units / x.rec:.2f}", f"{x.ret / x.units * 100:.1f}%"])
    E.append(table(rows, [62 * mm, 20 * mm, 22 * mm, 18 * mm, 16 * mm, 9 * mm, 16 * mm, 16 * mm, 16 * mm, 13 * mm,
                          15 * mm, 11 * mm, 12 * mm], INK, size=7, zebra=LIGHT))
    E.append(Spacer(1, 4))
    E.append(Paragraph("ATV and UPT on receipts; LY receipts for 2025 come from the legacy POS and are partially estimated (units/1.35) "
                       "for some stores. Return % = returned units / sold units in the month.", S["small"]))
    E.append(PageBreak())

    # ---- p5 traffic/conversion
    E.append(Paragraph("4. Traffic & conversion", S["h1"]))
    E.append(Image(f3, width=200 * mm, height=69 * mm))
    E.append(Spacer(1, 4))
    E.append(Paragraph(
        f"EMEA visitors {fmt_pct(traffic_g)} vs LY, conversion {conv:.1f}% vs {conv_ly:.1f}% LY. The gap is concentrated in shop-in-shops "
        "(Galeries Lafayette, Harrods, Rinascente) where department-store traffic counts all passers-by of the corner and in the "
        "flagships during fashion weeks (many visits from industry and press, low intent). Venezia and Saint-Honoré convert well "
        "with tourists.", S["body"]))
    E.append(KeepTogether([Image(f5, width=105 * mm, height=63 * mm),
                           Paragraph(f"ROM01: visitors {fmt_pct((rom.vis / rom.vis_ly - 1) * 100)} in the month, "
                                     f"{fmt_pct(rom_traffic_since, 0)} since 14/09. Hoarding covers both windows; temporary "
                                     "signage requested to the Comune (pending).", S["small"])]))
    E += [NPT("two"), PageBreak()]

    # ---- p6 FW26
    E.append(Paragraph("5. FW26 new-in", S["h1"]))
    rows = [["Style", "Sales EUR k", "EOP stock EUR k", "ST % (value)", "Units sold"]]
    for s_, x in st.iterrows():
        rows.append([s_, f"{x.sales_eur / 1e3:,.0f}", f"{x.stock_eur / 1e3:,.0f}", f"{x.st_value:.0f}%", f"{x.units:,.0f}"])
    E.append(table(rows, [40 * mm, 22 * mm, 26 * mm, 22 * mm, 18 * mm], ACC, zebra=LIGHT))
    E.append(Spacer(1, 4))
    E.append(Paragraph("Sell-through on value = net sales at retail since launch / (net sales + end-of-period stock valued at full retail "
                       "price), EMEA stores only, cut-off 30/09/2026. Not comparable with the Merchandising unit sell-through "
                       "(units sold / units received).", S["small"]))
    E.append(Spacer(1, 6))
    E.append(Paragraph(
        "AMALIA chocolate brown is the stand-out of the drop in Milano, Paris, London and Madrid: sizes 0-2 broken by the last week of "
        "September and DC cannot replenish brown before November. Black AMALIA sells at a normal pace. IRIDIA (cropped) good in all "
        "colours; ARTEM parka sells but generates size exchanges (fits large, staff now advise one size down). ASTRA (Couture) is slow "
        "in EMEA: clients find the fit small and the price high, consistent with the feedback from the Paris and Milan teams.",
        S["body"]))
    E.append(FrameBreak())
    E.append(Spacer(1, 22))
    E.append(Image(f4, width=120 * mm, height=84 * mm))
    E += [NPT("full"), PageBreak()]

    # ---- p7 category
    E.append(Paragraph("6. Category mix", S["h1"]))
    dd = daily()
    e = dd[dd.region == "EMEA"].copy()
    e["eur"] = e.net_sales_lc / e.currency.map(BUDGET_RATE)
    c_cy = e[(e.date >= M0) & (e.date <= M1)].groupby("category").eur.sum()
    c_ly = e[(e.date >= L0) & (e.date <= L1)].groupby("category").eur.sum()
    rows = [["Category", "Sep 26 EUR k", "Mix %", "Sep 25 EUR k", "Mix % LY", "Δ%"]]
    for c_ in c_cy.sort_values(ascending=False).index:
        rows.append([c_, f"{c_cy[c_] / 1e3:,.0f}", f"{c_cy[c_] / c_cy.sum() * 100:.1f}%", f"{c_ly.get(c_, 0) / 1e3:,.0f}",
                     f"{c_ly.get(c_, 0) / c_ly.sum() * 100:.1f}%", fmt_pct((c_cy[c_] / c_ly.get(c_, np.nan) - 1) * 100)])
    E.append(table(rows, [45 * mm, 28 * mm, 20 * mm, 28 * mm, 20 * mm, 20 * mm], INK, zebra=LIGHT))
    E.append(Spacer(1, 8))
    E.append(Paragraph(
        "Outerwear weight in line with seasonality; knitwear supported by the vlogo cardigan and the new cashmere turtleneck. "
        "Footwear soft (Vtrack sizes 42-43 broken in several stores). Accessories flat - beanies will start with the cold.",
        S["body"]))
    E.append(Spacer(1, 8))
    E.append(Paragraph("7. Clientele & tourism", S["h1"]))
    top = nat.sort_values("Sep", ascending=False).head(10)
    rows = [["Nationality (POS)", "Share Aug 26", "Share Sep 26", "Δ pp"]]
    for n_, x in top.iterrows():
        rows.append([n_ or "n.d.", f"{x.Aug:.1f}%", f"{x.Sep:.1f}%", f"{x.Sep - x.Aug:+.1f}"])
    E.append(table(rows, [45 * mm, 28 * mm, 28 * mm, 20 * mm], INK, zebra=LIGHT))
    E.append(Spacer(1, 4))
    E.append(Paragraph("Share of EMEA net sales (sales lines only) by customer nationality as captured at POS. "
                       "Nationality is mandatory only for tax-free sales; domestic clients often recorded by default.", S["small"]))
    E.append(PageBreak())

    # ---- p8 commentary
    E.append(Paragraph("8. Regional Director's commentary", S["h1"]))
    E.append(Paragraph("Federico Arrighi - EMEA Retail Director", S["small"]))
    E.append(Spacer(1, 6))
    com = [
        "A good month, better in the second half. The fashion weeks did what we expected in Montenapoleone and in Saint-Honoré, "
        "and Venezia keeps surprising us with the long-haul tourists. We are still below budget, mostly because of Roma and of the "
        "German/Swiss business that only woke up with the first cold days (which arrived in October, not September).",
        "Roma: the Comune opened the cantiere on Via Condotti on 14 September and the building put scaffolding on top of it. From the "
        "street you cannot see our windows. Footfall is roughly half of normal and the team is doing appointments and clienteling by "
        "WhatsApp to compensate. Works should end at the beginning of November. I asked Legal to verify a rent abatement and Visual "
        "to produce a branded hoarding.",
        "Korean clients: since Chuseok we have a constant flow of Korean tourists in Paris, Milano and at Harrods asking for the black "
        "AUREA (seen on a Korean actress). Korean clients are now more than 10% of the sales in Saint-Honoré. The problem is the "
        "lack of stock: black is finished in the three cities and the DC has nothing until mid-October; beige and navy do not "
        "replace it, the clients want only black. I consider this the biggest lost opportunity of the month. Please prioritise "
        "PAR01, PAR02, MIL01 and LON02 when the 420 units arrive.",
        "AMALIA brown: same story at smaller scale. We bought brown too thin. I would move brown sizes 0-2 from Munich, Berlin and "
        "Copenhagen (where they ask black) to Milano and Paris.",
        "VEL: in the last days of September we started receiving vests back with the zipper slider breaking. Quality is on it; stores "
        "have been told to check the slider at the till and to offer exchange. If confirmed on the whole July batch we need a "
        "decision on stop-sale before the cold season.",
        "ASTRA: honestly a disappointment in Europe. Clients try it, it is small and they find the price too high for a capsule. "
        "I would not re-order for EMEA.",
        "Outlook October: Golden Week started very well with Chinese clients in Milano and Paris, and the forecast announces a cold "
        "spell in Central Europe. I expect to recover part of the gap to budget in Q4.",
    ]
    for p in com:
        E.append(Paragraph(p, S["quote"]))
    E.append(PageBreak())

    # ---- p9 actions
    E.append(Paragraph("9. Actions & requests", S["h1"]))
    rows = [["#", "Topic", "Action", "Owner", "Due"],
            ["1", "AUREA black", "Allocate DC re-supply (ETA 16/10) first to PAR01, PAR02, MIL01, LON02", "Merch. Planning", "16/10"],
            ["2", "AMALIA brown", "Inter-store transfer sizes 0-2 MUN01/BER01/CPH01 -> MIL01/PAR01", "EMEA Retail Ops", "12/10"],
            ["3", "ROM01", "Branded hoarding + rent abatement request", "Visual / Legal", "20/10"],
            ["4", "VEL vest", "Check slider at till, exchange policy, stop-sale decision", "Quality / Retail", "15/10"],
            ["5", "ASTRA", "No re-order EMEA, move units to Greater China?", "Merch. / APAC", "31/10"],
            ["6", "CPH01", "Temporary staff from Stockholm agency", "HR EMEA", "done"]]
    E.append(table(rows, [8 * mm, 32 * mm, 140 * mm, 38 * mm, 18 * mm], ACC, zebra=LIGHT, align_right_from=99))
    E.append(PageBreak())

    # ---- p10 appendix
    E.append(Paragraph("Appendix - definitions, perimeter, FX", S["h1"]))
    app = [
        "<b>Period</b>: calendar month 01/09/2026-30/09/2026 vs 01/09/2025-30/09/2025 (the daily chart aligns LY by weekday).",
        "<b>Net sales</b>: gross sales - discounts - returns, excluding VAT. Source BI store KPI table.",
        "<b>FX</b>: all non-EUR stores converted at <b>budget 2026 rates</b> (GBP 0.85, CHF 0.95, DKK 7.46, AED 4.00 per EUR), "
        "both years. Figures therefore differ from the weekly flash of Retail Controlling, which uses actual monthly average rates.",
        "<b>LFL</b>: standalone DOS open in both periods. Excluded: shop-in-shops (MIL02, PAR02, LON02, BER01) and seasonal stores "
        "(COU01, CRT01, STM01).",
        "<b>Sell-through (value)</b>: net sales at retail / (net sales + EOP stock at full retail), EMEA only.",
        "<b>Conversion</b>: receipts / door-counter visitors. Shop-in-shops use department-store feeds.",
        "<b>Version history</b>: v1 05/10 (preliminary, w/o last weekend returns); v2 07/10 (ROM01 excluded from LFL as "
        "non-comparable); v3 09/10 FINAL (ROM01 reinstated in LFL per Controlling guidance, commentary added).",
    ]
    for a in app:
        E.append(Paragraph(a, S["body"]))
    doc.build(E)

    facts.update(dict(
        net_eur_budfx=round(tot_net), ly_eur_budfx=round(tot_ly), rep_g=round(rep_g, 1), vs_bud=round(vs_bud, 1),
        lfl_true=round(lfl_g, 1), lfl_quoted_exec_summary=round(lfl_g_v2, 1),
        country_total_shown=round(eu.net.sum()), dxb_net=round(t.loc["DXB01"].net),
        kr_share_par01_pos=round(kr_par, 1), rom_month_g=round((rom.net / rom.net_ly - 1) * 100, 1),
        rom_traffic_since=round(rom_traffic_since, 1),
        sellthrough_value={s_: round(x.st_value, 1) for s_, x in st.iterrows()},
        stores={s_: round(x.net) for s_, x in t.iterrows()},
        lon01_net_budfx=round(t.loc["LON01"].net), lon01_lc=round(t.loc["LON01"].lc),
    ))
    facts.save()


if __name__ == "__main__":
    main()
