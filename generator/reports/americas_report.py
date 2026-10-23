"""Americas monthly retail report (XLSX) - FY2026 P08 (September, NRF 4-5-4).

Author: Valentino USA Inc. - Retail Finance (New York). Definitions:
- 4-5-4 retail calendar: P08 Sep = Sun 2026-08-30 -> Sat 2026-10-03 (5 weeks); LY P08 = 2025-08-31 -> 2025-10-04
- Net sales USD, net of returns, ex sales tax; CAD converted at PLAN rate 1.37 CAD/USD (both years)
- Plan = HQ budget in local currency (CAD plan converted at 1.37)
- Multi-row merged headers, district subtotals; some LY cells stored as text; hidden helper column
"""
import datetime as dt

import numpy as np
import xlsxwriter

from common import D, NRF_2025, NRF_2026, Facts, kpi, outdir, stores

OUTD = outdir("americas")
facts = Facts("americas")
CAD_USD = 1.37
DISTRICTS = [("Northeast", ["NYC01", "NYC02"]), ("Southeast", ["MIA01"]), ("West & Mountain", ["BHS01", "ASP01"]),
             ("Canada", ["TOR01"])]
SNAME = {"NYC01": "Madison Ave", "NYC02": "SoHo (Greene St)", "MIA01": "Miami Design District", "BHS01": "Rodeo Drive",
         "ASP01": "Aspen", "TOR01": "Toronto Yorkville"}
STORE_NO = {"NYC01": "US-101", "NYC02": "US-102", "MIA01": "US-201", "BHS01": "US-301", "ASP01": "US-302", "TOR01": "CA-401"}


def agg(sids, d0, d1):
    k = kpi()
    x = k[k.store_id.isin(sids) & (k.date >= d0) & (k.date <= d1)].copy()
    rate = np.where(x.currency == "CAD", CAD_USD, 1.0)
    x["usd"] = x.net_sales_lc / rate
    x["plan"] = x.budget_lc / rate
    g = x.groupby("store_id").agg(usd=("usd", "sum"), plan=("plan", "sum"), vis=("visitors_in", "sum"),
                                  rec=("receipts", "sum"), units=("units", "sum"))
    return g.reindex(sids).fillna(0)


def main():
    a0, a1 = NRF_2026["P08 Sep"]
    b0, b1 = NRF_2025["P08 Sep"]
    sids = [s for _, ss in DISTRICTS for s in ss]
    cy, ly = agg(sids, a0, a1), agg(sids, b0, b1)

    wb = xlsxwriter.Workbook(OUTD / "AMER_Retail_Monthly_FY26_P08_Sep.xlsx")
    wb.set_properties({"title": "Americas Retail Monthly P08 FY26", "author": "Retail Finance NY - J. Morales",
                       "company": "Valentino USA Inc."})
    F = lambda **kw: wb.add_format({"font_name": "Calibri", "font_size": 10, **kw})
    ttl = F(bold=True, font_size=14, align="center", valign="vcenter", bg_color="#000000", font_color="#FFFFFF")
    sub = F(italic=True, align="center", bg_color="#F2F2F2")
    g1 = F(bold=True, align="center", valign="vcenter", border=1, bg_color="#404040", font_color="#FFFFFF", text_wrap=True)
    g2 = F(bold=True, align="center", valign="vcenter", border=1, bg_color="#BFBFBF", text_wrap=True)
    txt = F(border=1)
    dist = F(bold=True, border=1, bg_color="#DDEBF7")
    usd = F(border=1, num_format='$#,##0;[Red]($#,##0)')
    usdb = F(border=1, num_format='$#,##0;[Red]($#,##0)', bold=True, bg_color="#DDEBF7")
    usdt = F(border=1, num_format='$#,##0;[Red]($#,##0)', bold=True, bg_color="#FFE699", top=2)
    pct = F(border=1, num_format='0.0%;[Red]-0.0%')
    pctb = F(border=1, num_format='0.0%;[Red]-0.0%', bold=True, bg_color="#DDEBF7")
    pctt = F(border=1, num_format='0.0%;[Red]-0.0%', bold=True, bg_color="#FFE699", top=2)
    num = F(border=1, num_format='#,##0')
    numb = F(border=1, num_format='#,##0', bold=True, bg_color="#DDEBF7")
    numt = F(border=1, num_format='#,##0', bold=True, bg_color="#FFE699", top=2)
    txt_right = F(border=1, align="right")
    note = F(italic=True, font_size=8, font_color="#7F7F7F")

    ws = wb.add_worksheet("P08 Sep")
    ws.set_column(0, 0, 9)
    ws.set_column(1, 1, 24)
    ws.set_column(2, 17, 11)
    ws.set_column(18, 18, 10, None, {"hidden": True})
    ws.merge_range(0, 0, 0, 17, "VALENTINO USA INC.  -  RETAIL MONTHLY SALES REPORT", ttl)
    ws.set_row(0, 26)
    ws.merge_range(1, 0, 1, 17, f"FY2026  P08 (SEPTEMBER)  |  {a0:%m/%d/%Y} - {a1:%m/%d/%Y}  (5 wks, 4-5-4)  |  LY: {b0:%m/%d/%Y} - {b1:%m/%d/%Y}  |  USD, CAD @ plan rate {CAD_USD}", sub)
    # two header rows
    ws.merge_range(3, 0, 4, 0, "Store #", g1)
    ws.merge_range(3, 1, 4, 1, "Store", g1)
    ws.merge_range(3, 2, 3, 5, "NET SALES (USD)", g1)
    ws.merge_range(3, 6, 3, 7, "PLAN", g1)
    ws.merge_range(3, 8, 3, 10, "TRAFFIC", g1)
    ws.merge_range(3, 11, 3, 12, "CONVERSION", g1)
    ws.merge_range(3, 13, 3, 14, "ATV (USD)", g1)
    ws.merge_range(3, 15, 3, 16, "UPT", g1)
    ws.merge_range(3, 17, 4, 17, "% to Total", g1)
    for c, h in enumerate(["TY", "LY", "Var $", "Var %", "Plan $", "Var % to Plan", "TY", "LY", "Var %", "TY", "LY",
                           "TY", "LY", "TY", "LY"]):
        ws.write(4, 2 + c, h, g2)
    ws.write(4, 18, "chk", g2)
    ws.set_row(4, 28)
    ws.freeze_panes(5, 2)
    r = 5
    tot_cy = cy.usd.sum()

    def line(label, no, a, b, fm_u, fm_p, fm_n, fm_t, text_ly=False):
        nonlocal r
        ws.write(r, 0, no, fm_t)
        ws.write(r, 1, label, fm_t)
        ws.write(r, 2, a.usd, fm_u)
        if text_ly:
            ws.write_string(r, 3, f"{b.usd:,.0f}", txt_right)  # stored as text (manual paste)
        else:
            ws.write(r, 3, b.usd, fm_u)
        ws.write(r, 4, a.usd - b.usd, fm_u)
        ws.write(r, 5, a.usd / b.usd - 1 if b.usd else "", fm_p)
        ws.write(r, 6, a.plan, fm_u)
        ws.write(r, 7, a.usd / a.plan - 1 if a.plan else "", fm_p)
        ws.write(r, 8, a.vis, fm_n)
        ws.write(r, 9, b.vis, fm_n)
        ws.write(r, 10, a.vis / b.vis - 1 if b.vis else "", fm_p)
        ws.write(r, 11, a.rec / a.vis if a.vis else "", fm_p)
        ws.write(r, 12, b.rec / b.vis if b.vis else "", fm_p)
        ws.write(r, 13, a.usd / a.rec if a.rec else "", fm_u)
        ws.write(r, 14, b.usd / b.rec if b.rec else "", fm_u)
        ws.write(r, 15, round(a.units / a.rec, 2) if a.rec else "", fm_n if False else F(border=1, num_format="0.00"))
        ws.write(r, 16, round(b.units / b.rec, 2) if b.rec else "", F(border=1, num_format="0.00"))
        ws.write(r, 17, a.usd / tot_cy, fm_p)
        ws.write(r, 18, a.usd - a.plan, fm_u)
        r += 1

    for dname, ss in DISTRICTS:
        ws.merge_range(r, 0, r, 17, dname.upper(), dist)
        r += 1
        for s in ss:
            line(SNAME[s], STORE_NO[s], cy.loc[s], ly.loc[s], usd, pct, num, txt, text_ly=(s == "ASP01"))
        if len(ss) > 1:
            line(f"Total {dname}", "", cy.loc[ss].sum(), ly.loc[ss].sum(), usdb, pctb, numb, dist)
    line("TOTAL AMERICAS", "", cy.sum(), ly.sum(), usdt, pctt, numt, F(bold=True, border=1, bg_color="#FFE699", top=2))
    ws.write(r + 1, 0, "Net sales = gross - discounts - returns, excl. sales tax. Traffic: ShopperTrak/Xovis. LY receipts partially estimated (legacy POS).", note)
    ws.write(r + 2, 0, "Aspen LY pasted from FY25 book (text). Toronto in USD at plan rate - local CAD performance may differ.", note)
    ws.write(r + 3, 0, "CONFIDENTIAL - FOR INTERNAL USE ONLY", F(bold=True, font_size=8, font_color="#C00000"))

    # weekly sheet
    ws2 = wb.add_worksheet("Weekly P08")
    ws2.merge_range(0, 0, 0, 12, "P08 WEEKLY NET SALES (USD) - week ending Saturday", ttl)
    ws2.merge_range(2, 0, 3, 0, "Store", g1)
    weeks = [(a0 + dt.timedelta(days=7 * i), a0 + dt.timedelta(days=7 * i + 6)) for i in range(5)]
    for i, (w0, w1) in enumerate(weeks):
        ws2.merge_range(2, 1 + 2 * i, 2, 2 + 2 * i, f"Wk {i + 1}  (w/e {w1:%m/%d})", g1)
        ws2.write(3, 1 + 2 * i, "TY", g2)
        ws2.write(3, 2 + 2 * i, "LY", g2)
    ws2.set_column(0, 0, 24)
    ws2.set_column(1, 10, 11)
    for j, s in enumerate(sids):
        ws2.write(4 + j, 0, SNAME[s], txt)
        for i, (w0, w1) in enumerate(weeks):
            ws2.write(4 + j, 1 + 2 * i, agg([s], w0, w1).usd.sum(), usd)
            ws2.write(4 + j, 2 + 2 * i, agg([s], w0 - dt.timedelta(days=364), w1 - dt.timedelta(days=364)).usd.sum(), usd)

    # P09 MTD
    c0, c1 = D(2026, 10, 4), D(2026, 10, 17)
    m_cy, m_ly = agg(sids, c0, c1), agg(sids, c0 - dt.timedelta(days=364), c1 - dt.timedelta(days=364))
    k = kpi()
    ws3 = wb.add_worksheet("P09 MTD")
    ws3.merge_range(0, 0, 0, 7, f"FY26 P09 (OCTOBER) MONTH-TO-DATE  {c0:%m/%d} - {c1:%m/%d}/2026 (2 of 4 wks)", ttl)
    ws3.merge_range(2, 0, 3, 0, "Store", g1)
    ws3.merge_range(2, 1, 2, 4, "NET SALES (USD)", g1)
    ws3.merge_range(2, 5, 2, 6, "PLAN", g1)
    ws3.merge_range(2, 7, 3, 7, "Comment", g1)
    for c, h in enumerate(["TY", "LY", "Var $", "Var %", "Plan $", "Var %"]):
        ws3.write(3, 1 + c, h, g2)
    ws3.set_column(0, 0, 24)
    ws3.set_column(1, 6, 12)
    ws3.set_column(7, 7, 70)
    cmt = {"NYC02": "POS down 10/6 2:10-5:40pm; manual tickets keyed 10/7 -> 10/6 understated, 10/7 overstated",
           "NYC01": "Campaign windows; IRIDIA black/off-white requests (celebrity effect)",
           "TOR01": "ARTEM strong but many size exchanges (runs large)",
           "BHS01": "Warm weather, outerwear slow",
           "MIA01": "", "ASP01": "Pre-season, low traffic until Thanksgiving"}
    for j, s in enumerate(sids):
        a, b = m_cy.loc[s], m_ly.loc[s]
        ws3.write(4 + j, 0, SNAME[s], txt)
        ws3.write(4 + j, 1, a.usd, usd)
        ws3.write(4 + j, 2, b.usd, usd)
        ws3.write(4 + j, 3, a.usd - b.usd, usd)
        ws3.write(4 + j, 4, a.usd / b.usd - 1, pct)
        ws3.write(4 + j, 5, a.plan, usd)
        ws3.write(4 + j, 6, a.usd / a.plan - 1, pct)
        ws3.write(4 + j, 7, cmt[s], txt)
    A, B = m_cy.sum(), m_ly.sum()
    ws3.write(4 + len(sids), 0, "TOTAL", F(bold=True, border=1, top=2))
    for c, v in enumerate([A.usd, B.usd, A.usd - B.usd, A.usd / B.usd - 1, A.plan, A.usd / A.plan - 1]):
        ws3.write(4 + len(sids), 1 + c, v, usdt if c in (0, 1, 2, 4) else pctt)
    n6 = k[(k.store_id == "NYC02") & (k.date == D(2026, 10, 6))].net_sales_lc.sum()
    n7 = k[(k.store_id == "NYC02") & (k.date == D(2026, 10, 7))].net_sales_lc.sum()
    ws3.write(6 + len(sids), 0, f"NYC02 daily: 10/6 ${n6:,.0f} | 10/7 ${n7:,.0f} (not restated)", note)

    # commentary
    ws4 = wb.add_worksheet("Commentary")
    ws4.set_column(0, 0, 130)
    ws4.write(0, 0, "P08 COMMENTARY - Retail Finance / Regional Retail Director Americas", F(bold=True, font_size=12))
    tc = cy.sum()
    tl = ly.sum()
    lines = [
        f"Americas P08 net sales ${tc.usd / 1e6:,.2f}M, {(tc.usd / tl.usd - 1) * 100:+.1f}% vs LY and {(tc.usd / tc.plan - 1) * 100:+.1f}% vs plan.",
        "FW26 brand campaign (OOH + digital) live in NY, LA and Miami since 9/15. Agency reports strong attributed uplift; our read on comp stores is more modest - see Marketing for the agency deck.",
        f"Madison Ave {(cy.loc['NYC01'].usd / ly.loc['NYC01'].usd - 1) * 100:+.1f}%: UNGA week 9/21-9/26 with frozen zones on Madison/Park, traffic down sharply that week.",
        "Rodeo Drive: heat wave 9/8-9/12 (100F+), outerwear not moving; jersey and sneakers carried the week.",
        "Miami: A/C failure 9/3-9/5 (store open, clients left quickly). Repaired by vendor on 9/5.",
        "Toronto: TIFF 9/10-9/20 drove traffic in Yorkville; ARTEM parka the best FW26 style in Canada but exchanges for size (fits large).",
        "Couture ASTRA (launched 9/24) slow in US: fit runs small and price point; clients compare with the regular collection.",
        "P09 to date: NYC02 POS outage on 10/6 (see P09 MTD tab). Aspen opens full schedule from Thanksgiving.",
        "Note: P08 includes the first 3 days of October; HQ calendar-month reports (September) will not tie to this report.",
    ]
    for i, l_ in enumerate(lines):
        ws4.write(2 + i, 0, l_, F(text_wrap=True))
    wb.close()

    facts.update(dict(period=f"{a0}..{a1}", total_usd=round(cy.usd.sum()), ly_usd=round(ly.usd.sum()),
                      growth=round((cy.usd.sum() / ly.usd.sum() - 1) * 100, 1),
                      vs_plan=round((cy.usd.sum() / cy.plan.sum() - 1) * 100, 1),
                      stores_usd={s: round(cy.loc[s].usd) for s in sids},
                      tor01_cad=round(cy.loc["TOR01"].usd * CAD_USD), nyc02_oct6=round(n6), nyc02_oct7=round(n7),
                      p09_mtd_usd=round(A.usd), p09_mtd_growth=round((A.usd / B.usd - 1) * 100, 1)))
    facts.save()


if __name__ == "__main__":
    main()
