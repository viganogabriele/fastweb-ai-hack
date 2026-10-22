"""E-commerce channel weekly report (summary XLSX) - Digital team, weeks W40-W42.

Summarises generated/sources/systems/ecommerce (raw). Definitions:
- 'Demand' = gross ordered value incl. VAT before returns (Shopify gross_sales - discounts), EUR at monthly ECB avg
- 'Net' = after returns booked that day
- day = UTC calendar day (raw export), weeks Mon-Sun on UTC days
- notify-me = back-in-stock REQUESTS created (not unique customers; same email can request several sizes)
"""
import datetime as dt

import pandas as pd
import xlsxwriter

from common import D, FX_MONTHLY, ROOT, Facts, outdir

OUTD = outdir("digital")
facts = Facts("digital")
EC = ROOT / "generated" / "sources" / "systems" / "ecommerce"


def main():
    e = pd.read_csv(EC / "shopify_sales_by_variant_daily.csv")
    e["date"] = pd.to_datetime(e.day).dt.date
    e["rate"] = [FX_MONTHLY[f"{d.year}-{d.month:02d}"][c] for d, c in zip(e.date, e.currency)]
    e["demand_eur"] = (e.gross_sales + e.discounts) / e.rate
    e["net_eur"] = e.net_sales / e.rate
    e["wk"] = e.date.map(lambda d: d.isocalendar()[1])
    b = pd.read_csv(EC / "back_in_stock_requests.csv")
    b["date"] = pd.to_datetime(b.created_at).dt.date
    b["wk"] = b.date.map(lambda d: d.isocalendar()[1])
    weeks = [40, 41, 42]
    wb = xlsxwriter.Workbook(OUTD / "Digital_Weekly_Channel_Report_W42_2026.xlsx")
    wb.set_properties({"title": "Digital weekly W42", "author": "Digital Analytics - E. Conti"})
    F = lambda **kw: wb.add_format({"font_name": "Helvetica", "font_size": 9, **kw})
    hdr = F(bold=True, bg_color="#111111", font_color="white", border=1)
    txt, n0, e0, pc = F(border=1), F(border=1, num_format="#,##0"), F(border=1, num_format="€#,##0"), F(border=1, num_format="+0.0%;-0.0%")
    ws = wb.add_worksheet("Country")
    ws.write(0, 0, "Online demand by billing country (EUR, incl. VAT, before returns)", F(bold=True, font_size=12))
    heads = ["Country"] + [f"W{w} demand" for w in weeks] + ["W42 net", "WoW %"]
    for c, h in enumerate(heads):
        ws.write(2, c, h, hdr)
    pv = e[e.wk.isin(weeks)].pivot_table(index="billing_country", columns="wk", values="demand_eur", aggfunc="sum").fillna(0)
    nt = e[e.wk == 42].groupby("billing_country").net_eur.sum()
    pv = pv.sort_values(42, ascending=False)
    ws.set_column(0, 6, 13)
    for i, (cc, x) in enumerate(pv.iterrows()):
        ws.write(3 + i, 0, cc, txt)
        for j, w in enumerate(weeks):
            ws.write(3 + i, 1 + j, x[w], e0)
        ws.write(3 + i, 4, nt.get(cc, 0), e0)
        ws.write(3 + i, 5, x[42] / x[41] - 1 if x[41] else "", pc)
    r = 3 + len(pv)
    ws.write(r, 0, "TOTAL", hdr)
    for j, w in enumerate(weeks):
        ws.write(r, 1 + j, pv[w].sum(), e0)
    ws.write(r + 2, 0, "Days are UTC (Shopify export). WeChat Mini Program included in CN. Tmall not included (partner-operated).", F(italic=True, font_color="#888888"))

    ws = wb.add_worksheet("Notify me")
    ws.write(0, 0, "Back-in-stock requests ('notify me') created per week", F(bold=True, font_size=12))
    top = b.groupby("product_id").size().sort_values(ascending=False).head(8).index
    for c, h in enumerate(["Product", "Variant colour"] + [f"W{w}" for w in [38, 39, 40, 41, 42]] + ["Total since 08/08", "Pending"]):
        ws.write(2, c, h, hdr)
    ws.set_column(0, 1, 18)
    names = {"J20931A00618-510": ("ILVARO", "powder pink"), "J20931A00012-999": ("MAIRE", "black"),
             "J20931A00622-23R": ("AMBRINE", "chocolate"), "J20931A00618-999": ("ILVARO", "black")}
    out = {}
    for i, pid in enumerate(top):
        g = b[b.product_id == pid]
        nm = names.get(pid, (pid, ""))
        ws.write(3 + i, 0, nm[0], txt)
        ws.write(3 + i, 1, nm[1], txt)
        for j, w in enumerate([38, 39, 40, 41, 42]):
            ws.write(3 + i, 2 + j, int((g.wk == w).sum()), n0)
        ws.write(3 + i, 7, len(g), n0)
        ws.write(3 + i, 8, int((g.status == "PENDING").sum()), n0)
        out[pid] = dict(requests=len(g), unique_emails=int(g.email_sha1_10.nunique()))
    ws2 = wb.add_worksheet("Comments")
    ws2.set_column(0, 0, 120)
    for i, t in enumerate([
            "ILVARO powder pink: notify-me requests exploded from 02/10 (celebrity photos), KR and CN sites first, then US/GB/FR.",
            "MAIRE black: steady requests since late September, mostly from KR and GB sites; back in stock online from 17/10.",
            "Demand is gross ordered value; Finance reports online net sales after returns and ex VAT - expect ~25-30% difference.",
            "Notify-me counts are requests, a customer requesting 2 sizes counts twice."]):
        ws2.write(i, 0, t)
    wb.close()
    facts.update(dict(notify=out, w42_demand=round(pv[42].sum()), w42_net=round(nt.sum())))
    facts.save()


if __name__ == "__main__":
    main()
