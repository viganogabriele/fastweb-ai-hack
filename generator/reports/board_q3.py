"""Board of Directors - Q3 2026 trading update (PPTX, draft v5).

Author: Group Finance / Investor Relations prep. Definitions:
- Q3 = calendar Jul 1 - Sep 30; DOS (retail stores) net sales; 'organic growth' = constant FX (2025 average rates)
- Reported EUR at actual monthly average rates
- Rounded to EUR m; region numbers rounded independently (do not add up)
- Digital and Wholesale figures from Group consolidation (not available in store data; synthetic)
- Quotes the agency '+22%' campaign uplift as fact; October QTD = Oct 1-18
"""
import datetime as dt

from common import D, FX_AVG_2025, FX_MONTHLY, Facts, kpi, outdir
from pptkit import XL_CHART_TYPE, Deck, PP_ALIGN

OUTD = outdir("board")
facts = Facts("board")
TH = dict(font="Calibri", fg="1A1A1A", accent="1A1A1A", muted="8A8A8A", gold="A88B5A", light="F3F1EC")


def dos(d0, d1, fx="const"):
    k = kpi()
    x = k[(k.date >= d0) & (k.date <= d1)].copy()
    if fx == "const":
        x["eur"] = x.net_sales_lc / x.currency.map(FX_AVG_2025)
    else:
        x["eur"] = [v / FX_MONTHLY[f"{d.year}-{d.month:02d}"][c] for v, d, c in zip(x.net_sales_lc, x.date, x.currency)]
    return x.groupby("region").eur.sum()


def main():
    q_cy_c, q_ly_c = dos(D(2026, 7, 1), D(2026, 9, 30)), dos(D(2025, 7, 1), D(2025, 9, 30))
    q_cy_r, q_ly_r = dos(D(2026, 7, 1), D(2026, 9, 30), "rep"), dos(D(2025, 7, 1), D(2025, 9, 30), "rep")
    o_cy, o_ly = dos(D(2026, 10, 1), D(2026, 10, 18)), dos(D(2025, 10, 1), D(2025, 10, 18))
    org = (q_cy_c.sum() / q_ly_c.sum() - 1) * 100
    rep = (q_cy_r.sum() / q_ly_r.sum() - 1) * 100
    octg = (o_cy.sum() / o_ly.sum() - 1) * 100
    dig_cy, dig_ly, wh_cy, wh_ly = 21.4e6, 18.6e6, 38.9e6, 41.2e6
    grp_cy = q_cy_r.sum() + dig_cy + wh_cy
    grp_ly = q_ly_r.sum() + dig_ly + wh_ly

    d = Deck(TH)

    def header(s, title):
        d.text(s, 0.7, 0.4, 12, 0.8, title, size=28, bold=False, color=TH["accent"], font="Cambria")
        d.text(s, 0.7, 7.0, 10, 0.3, "Board of Directors - 28 October 2026 - DRAFT v5 - Strictly confidential", size=8, color=TH["muted"])
        d.text(s, 12.0, 7.0, 0.8, 0.3, str(d.n), size=8, color=TH["muted"], align=PP_ALIGN.RIGHT)

    s = d.slide(bg="1A1A1A")
    d.text(s, 0.9, 2.5, 11, 1.0, "MONCLER", size=40, color="FFFFFF", font="Cambria", bold=True)
    d.text(s, 0.9, 3.5, 11, 0.8, "Q3 2026 Trading Update", size=28, color="D9C7A3", font="Cambria")
    d.text(s, 0.9, 5.6, 11, 0.9, ["Board of Directors - 28 October 2026", "DRAFT v5 - for discussion - figures subject to closing"],
           size=13, color="BBBBBB")

    s = d.slide()
    header(s, "Q3 highlights")
    tiles = [(f"€{round(q_cy_r.sum() / 1e6)}m", "DOS revenue Q3 (reported)"), (f"{org:+.0f}%", "DOS organic growth (const. FX)"),
             (f"{rep:+.0f}%", "DOS growth reported"), (f"{octg:+.0f}%", "October QTD organic (to 18/10)")]
    for i, (a, b) in enumerate(tiles):
        x = 0.7 + i * 3.1
        d.rect(s, x, 1.7, 2.8, 2.0, TH["light"])
        d.text(s, x + 0.2, 1.9, 2.5, 1.0, a, size=34, color=TH["accent"], font="Cambria")
        d.text(s, x + 0.2, 2.9, 2.5, 0.6, b, size=12, color=TH["muted"])
    d.text(s, 0.7, 4.2, 12, 2.6, [
        "APAC the engine of growth (Greater China, Korea); EMEA solid with strong tourist flows in September; Americas flat.",
        "FW26 new-in well received; Genius POLARIS a success in China. FW26 US/UK campaign delivered +22% attributed sales uplift.",
        "Watch-outs: TIB vest quality issue (slider), stock-outs on hero items (MAIRE black, ILVARO pink), Rome store works."],
        size=15, bullets=True, spacing=10)

    s = d.slide()
    header(s, "Revenue by channel")
    rows = [["€m", "Q3 2026", "Q3 2025", "Reported", "Organic"],
            ["Retail DOS", f"{q_cy_r.sum() / 1e6:.0f}", f"{q_ly_r.sum() / 1e6:.0f}", f"{rep:+.0f}%", f"{org:+.0f}%"],
            ["Digital", f"{dig_cy / 1e6:.0f}", f"{dig_ly / 1e6:.0f}", f"{(dig_cy / dig_ly - 1) * 100:+.0f}%", "+17%"],
            ["Wholesale", f"{wh_cy / 1e6:.0f}", f"{wh_ly / 1e6:.0f}", f"{(wh_cy / wh_ly - 1) * 100:+.0f}%", "-4%"],
            ["Group", f"{grp_cy / 1e6:.0f}", f"{grp_ly / 1e6:.0f}", f"{(grp_cy / grp_ly - 1) * 100:+.0f}%", "+7%"]]
    d.table(s, 0.7, 1.6, 8.0, rows, col_w=[2.4, 1.4, 1.4, 1.4, 1.4], size=15, header_fill="1A1A1A", zebra=TH["light"], row_h=0.55,
            bold_last=True, font="Calibri")
    d.text(s, 9.0, 1.6, 3.9, 4.5, ["Organic = constant FX at 2025 average rates.", "Retail DOS = 39 directly operated stores; "
                                   "e-commerce reported in Digital.", "Wholesale timing: FW26 deliveries anticipated into Q2."],
           size=12, color=TH["muted"], bullets=True, spacing=8)

    s = d.slide()
    header(s, "Retail DOS by region (€m, constant FX)")
    regs = ["EMEA", "AMERICAS", "APAC"]
    d.chart(s, 0.7, 1.4, 7.0, 5.2, XL_CHART_TYPE.COLUMN_CLUSTERED, regs,
            [("Q3 2025", [round(q_ly_c[r] / 1e6) for r in regs]), ("Q3 2026", [round(q_cy_c[r] / 1e6) for r in regs])],
            colors=["C9C1B1", "1A1A1A"], labels=True, title=None, font_size=12)
    rows = [["Region", "Q3 26", "Organic"]] + [[{"EMEA": "EMEA", "AMERICAS": "Americas", "APAC": "APAC"}[r], f"€{round(q_cy_c[r] / 1e6)}m",
                                                  f"{(q_cy_c[r] / q_ly_c[r] - 1) * 100:+.0f}%"] for r in regs]
    rows.append(["Total", f"€{round(q_cy_c.sum() / 1e6)}m", f"{org:+.0f}%"])
    d.table(s, 8.2, 1.8, 4.4, rows, col_w=[1.8, 1.3, 1.3], size=14, header_fill="1A1A1A", zebra=TH["light"], row_h=0.5, bold_last=True)

    s = d.slide()
    header(s, "October trading and Q4 outlook")
    d.text(s, 0.7, 1.5, 6.0, 5.0, [
        [(f"October QTD (1-18/10): {octg:+.0f}% organic", {"bold": True, "size": 17})],
        "Golden Week: Chinese clients in Milan, Paris and domestic China very strong.",
        "Cold snap in Central Europe from 12/10 accelerated outerwear in Germany, Switzerland, Nordics.",
        "Japan: pre-buying ahead of 1 November price increase.",
        "ILVARO powder pink: celebrity-driven sell-out in Asia; re-order under evaluation.",
    ], size=14, bullets=False, spacing=10)
    d.text(s, 7.0, 1.5, 5.8, 5.0, [
        [("Risks", {"bold": True, "size": 17})],
        "TIB vest slider defect: potential stop-sale of July batch; provision under assessment (€1-2m).",
        "Stock availability on hero items (MAIRE black DC re-supply only from 16/10).",
        "Double 11 pre-sales may cannibalise China store traffic in late October.",
        "Market research (Castellane) flags cooling Korean demand - not visible in our numbers so far.",
    ], size=14, spacing=10)

    s = d.slide()
    header(s, "Appendix - definitions and reconciliation notes")
    d.text(s, 0.7, 1.5, 12, 5.2, [
        "Quarter = calendar months July-September. Weekly flash (ISO weeks 27-39, 29/06-27/09) is not directly comparable.",
        "Organic growth = both years at 2025 average FX rates (EUR/USD 1.125, EUR/JPY 167.9, EUR/CNY 8.08, EUR/KRW 1,593).",
        "Reported = actual monthly average rates; regional MBRs use budget rates (EMEA) or other conventions (APAC: constant FX, sales before returns).",
        "Figures rounded to the nearest €m; regional figures rounded independently and may not add to the total.",
        "Digital and wholesale from Group consolidation (preliminary).",
        "Campaign uplift as reported by the media agency (Halden & Rowe), not validated by Finance.",
    ], size=14, bullets=True, spacing=10)
    d.save(OUTD / "Q3_2026_Trading_Update_BoD_draft_v5.pptx")
    facts.update(dict(dos_q3_rep=round(q_cy_r.sum()), dos_q3_ly_rep=round(q_ly_r.sum()), dos_q3_const=round(q_cy_c.sum()),
                      organic=round(org, 1), reported=round(rep, 1), oct_qtd_organic=round(octg, 1),
                      regions_const={r: round(q_cy_c[r]) for r in q_cy_c.index},
                      regions_growth={r: round((q_cy_c[r] / q_ly_c[r] - 1) * 100, 1) for r in q_cy_c.index},
                      digital=dig_cy, wholesale=wh_cy))
    facts.save()


if __name__ == "__main__":
    main()
