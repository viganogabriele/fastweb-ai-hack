"""Tax-free shopping insights from a refund operator (Aurelia Tax Free, fictional): XLSX merchant extract + PDF insights.

Definitions (operator):
- unit = tax-free form ISSUED at the merchant outlet (one per receipt with tax_free=1) - NOT validated at customs
- spend = purchase amount INCL. VAT (net_amount x (1+VAT of destination country)), EUR at monthly ECB average
- nationality = passport country as keyed at issue (POS customer_nationality)
- weeks Mon-Sun (ISO); W43 partial (to 21/10)
- 'validated' column: forms stamped at departure so far (lags 1-3 weeks; recent weeks incomplete)
Planted: W41 Italy rows duplicated in the 'Forms by week' sheet (batch re-sent); UK not covered.
"""
import datetime as dt
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xlsxwriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Frame, Image, PageBreak, PageTemplate, Paragraph, Spacer

from common import D, FX_MONTHLY, VAT, Facts, outdir, pos, stores
from pdfkit import register_fonts, savefig, style, table

register_fonts()
OUTD = outdir("tax_free")
TMP = Path(__file__).parent / "_tmp"
facts = Facts("taxfree")
NAT = {"CN": "China", "KR": "South Korea", "US": "United States", "JP": "Japan", "TW": "Taiwan", "HK": "Hong Kong",
       "SA": "Saudi Arabia", "AE": "UAE", "IN": "India", "BR": "Brazil", "TR": "Türkiye", "GB": "United Kingdom",
       "CH": "Switzerland", "MX": "Mexico", "KW": "Kuwait", "QA": "Qatar", "RU": "Russia", "TH": "Thailand",
       "ID": "Indonesia", "MY": "Malaysia", "AU": "Australia", "SG": "Singapore", "NZ": "New Zealand", "CO": "Colombia",
       "AR": "Argentina", "NO": "Norway", "SE": "Sweden", "OTHER": "Other", "NG": "Nigeria"}
DEST = {"IT": "Italy", "FR": "France", "CH": "Switzerland", "DE": "Germany", "ES": "Spain", "NL": "Netherlands",
        "DK": "Denmark", "AE": "UAE", "JP": "Japan", "KR": "South Korea", "SG": "Singapore", "AU": "Australia"}
OUTLET = {"MIL01": "IT-MI-00231", "MIL02": "IT-MI-00487", "ROM01": "IT-RM-00112", "VEN01": "IT-VE-00058",
          "CRT01": "IT-BL-00019", "PAR01": "FR-75-01923", "PAR02": "FR-75-00412", "CAN01": "FR-06-00377",
          "GVA01": "CH-GE-0091", "ZRH01": "CH-ZH-0144", "STM01": "CH-GR-0032", "MUN01": "DE-BY-02210",
          "BER01": "DE-BE-01008", "MAD01": "ES-MD-00671", "AMS01": "NL-NH-00230", "CPH01": "DK-HS-00045",
          "DXB01": "AE-DU-00702", "TYO01": "JP-13-10021", "TYO02": "JP-13-10388", "OSA01": "JP-27-20114",
          "SEL01": "KR-11-00953", "SEL02": "KR-11-00211", "BUS01": "KR-26-00140", "SIN01": "SG-01-00561",
          "SYD01": "AU-NSW-0219", "COU01": "IT-AO-00011"}


def build():
    p = pos()
    t = p[(p.tax_free == 1) & (p.line_type == "SALE") & (p.date >= D(2026, 8, 31))].copy()
    t["vat"] = t.country_code.map(VAT)
    t["spend_lc"] = t.net_amount * (1 + t.vat)
    t["rate"] = [FX_MONTHLY[f"{d.year}-{d.month:02d}"][c] for d, c in zip(t.date, t.currency)]
    t["spend_eur"] = t.spend_lc / t.rate
    t["week"] = t.date.map(lambda d: d.isocalendar()[1])
    forms = t.groupby(["week", "country_code", "store_id", "customer_nationality", "receipt_id"], as_index=False).agg(
        spend_eur=("spend_eur", "sum"), date=("date", "first"))
    # validation: deterministic pseudo-random by receipt; recent weeks less validated
    h = forms.receipt_id.map(lambda r: (hash(r) % 1000) / 1000.0) if False else \
        forms.receipt_id.map(lambda r: (sum(ord(ch) * (i + 1) for i, ch in enumerate(r)) % 997) / 997.0)
    days_since = forms.date.map(lambda d: (D(2026, 10, 21) - d).days)
    p_val = np.clip(0.88 * (1 - np.exp(-days_since / 9.0)), 0, 0.9)
    forms["validated"] = (h < p_val).astype(int)
    return forms


def main():
    f = build()
    g = f.groupby(["week", "country_code", "customer_nationality"]).agg(forms=("receipt_id", "count"),
                                                                        spend=("spend_eur", "sum"),
                                                                        validated=("validated", "sum")).reset_index()
    # ---------------- XLSX
    wb = xlsxwriter.Workbook(OUTD / "Aurelia_TFS_merchant_extract_VALENTINO_W36-W43_2026.xlsx")
    wb.set_properties({"title": "Merchant extract - issued tax free forms", "author": "Aurelia Tax Free - Merchant Analytics"})
    F = lambda **kw: wb.add_format({"font_name": "Segoe UI", "font_size": 9, **kw})
    hdr = F(bold=True, bg_color="#5B2C6F", font_color="white", border=1)
    txt, n0, e0 = F(border=1), F(border=1, num_format="#,##0"), F(border=1, num_format="€ #,##0")
    ws = wb.add_worksheet("Info")
    ws.set_column(0, 0, 120)
    for i, l in enumerate([
            "AURELIA TAX FREE - Merchant Insight extract", "Merchant group: VALENTINO (all participating outlets)",
            "Period: ISO weeks 36-43 2026 (31/08/2026 - 21/10/2026, week 43 partial)",
            "Unit of measure: tax free forms ISSUED at outlet. Spend = gross purchase amount incl. VAT, converted to EUR at monthly ECB average.",
            "Validated = forms stamped by customs/export validation so far. Recent weeks incomplete (validation lag 1-3 weeks).",
            "Nationality = passport country entered at issue. United Kingdom not covered (no VAT refund scheme since 2021).",
            "Extract generated 22/10/2026 06:12 CET. Figures may be restated."]):
        ws.write(i, 0, l, F(bold=(i == 0), font_size=11 if i == 0 else 9))
    ws = wb.add_worksheet("Forms by week")
    heads = ["ISO week", "Destination country", "Passport nationality", "Forms issued", "Spend incl. VAT (EUR)",
             "Avg spend / form (EUR)", "Forms validated"]
    for c, h in enumerate(heads):
        ws.write(0, c, h, hdr)
    ws.set_column(0, 6, 18)
    rows = g.sort_values(["week", "country_code", "forms"], ascending=[True, True, False])
    dup = rows[(rows.week == 41) & (rows.country_code == "IT")]
    rows = pd.concat([rows, dup]).sort_values(["week", "country_code"], kind="stable")
    for i, x in enumerate(rows.itertuples()):
        ws.write(1 + i, 0, f"2026-W{x.week:02d}", txt)
        ws.write(1 + i, 1, DEST[x.country_code], txt)
        ws.write(1 + i, 2, NAT.get(x.customer_nationality, x.customer_nationality), txt)
        ws.write(1 + i, 3, x.forms, n0)
        ws.write(1 + i, 4, round(x.spend, 2), e0)
        ws.write(1 + i, 5, round(x.spend / x.forms, 2), e0)
        ws.write(1 + i, 6, x.validated, n0)
    ws.autofilter(0, 0, len(rows), 6)
    ws.freeze_panes(1, 0)
    ws = wb.add_worksheet("By outlet")
    o = f.groupby(["store_id", "week"]).agg(forms=("receipt_id", "count"), spend=("spend_eur", "sum")).reset_index()
    for c, h in enumerate(["Outlet ID", "Outlet name", "ISO week", "Forms issued", "Spend incl. VAT (EUR)"]):
        ws.write(0, c, h, hdr)
    ws.set_column(0, 4, 20)
    sn = stores().set_index("store_id").store_name
    for i, x in enumerate(o.itertuples()):
        ws.write(1 + i, 0, OUTLET.get(x.store_id, x.store_id), txt)
        ws.write(1 + i, 1, f"VALENTINO {sn[x.store_id].upper()}", txt)
        ws.write(1 + i, 2, f"2026-W{x.week:02d}", txt)
        ws.write(1 + i, 3, x.forms, n0)
        ws.write(1 + i, 4, round(x.spend, 2), e0)
    wb.close()

    # ---------------- PDF insights
    kr_eu = g[(g.customer_nationality == "KR") & g.country_code.isin(["FR", "IT"])].groupby("week").spend.sum()
    cn_eu = g[(g.customer_nationality == "CN") & g.country_code.isin(["FR", "IT", "CH", "DE", "ES", "NL", "DK"])].groupby("week").spend.sum()
    cn_jp = g[(g.customer_nationality == "CN") & (g.country_code == "JP")].groupby("week").spend.sum()
    weeks = list(range(36, 43))
    fig, ax = plt.subplots(figsize=(6.5, 2.6))
    ax.plot(weeks, [cn_eu.get(w, 0) / 1e3 for w in weeks], "o-", color="#5B2C6F", label="Chinese passport - Europe")
    ax.plot(weeks, [kr_eu.get(w, 0) / 1e3 for w in weeks], "o-", color="#E67E22", label="Korean passport - France & Italy")
    ax.plot(weeks, [cn_jp.get(w, 0) / 1e3 for w in weeks], "o--", color="#7F8C8D", label="Chinese passport - Japan")
    ax.set_xticks(weeks, [f"W{w}" for w in weeks], fontsize=8)
    ax.set_ylabel("EUR k (incl. VAT)", fontsize=8)
    ax.legend(frameon=False, fontsize=7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=8)
    f1 = savefig(fig, TMP / "tf_trend.png")

    W40 = g[g.week == 40]
    top = W40.groupby("customer_nationality").spend.sum().sort_values(ascending=False).head(8)
    kr_aug = kr_eu.loc[[36, 37]].mean()
    kr_late = kr_eu.loc[[39, 40]].mean()
    cn_pre = cn_eu.loc[[38, 39]].mean()
    cn_gw = cn_eu.loc[[40, 41]].mean()
    S = dict(h1=style("h1", "NSans-B", 16, color=colors.HexColor("#5B2C6F"), spaceAfter=6),
             body=style("b", "NSans", 9, leading=13, spaceAfter=5), small=style("s", "NSans-I", 7, color=colors.grey),
             big=style("g", "NSans-B", 22, leading=26, color=colors.HexColor("#E67E22")))

    def on_page(c, doc):
        w, h = A4
        c.saveState()
        c.setFillColor(colors.HexColor("#5B2C6F"))
        c.rect(0, h - 14 * mm, w, 14 * mm, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("NSans-B", 10)
        c.drawString(15 * mm, h - 9 * mm, "aurelia  TAX FREE")
        c.setFont("NSans", 8)
        c.drawRightString(w - 15 * mm, h - 9 * mm, "Merchant Insights  |  VALENTINO  |  October 2026")
        c.setFillColor(colors.grey)
        c.setFont("NSans", 7)
        c.drawString(15 * mm, 9 * mm, "Confidential - prepared for the merchant. Based on issued tax free forms. Not an audited figure.")
        c.drawRightString(w - 15 * mm, 9 * mm, str(doc.page))
        c.restoreState()

    doc = BaseDocTemplate(str(OUTD / "Aurelia_Merchant_Insights_Valentino_Sep-Oct2026.pdf"), pagesize=A4, leftMargin=15 * mm,
                          rightMargin=15 * mm, topMargin=22 * mm, bottomMargin=16 * mm, title="Aurelia Merchant Insights")
    doc.addPageTemplates([PageTemplate("p", [Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height)], onPage=on_page)])
    E = [Paragraph("Tax free shopping at Valentino: September - mid October 2026", S["h1"]),
         Paragraph(f"+{(kr_late / kr_aug - 1) * 100:.0f}%", S["big"]),
         Paragraph("Korean shoppers' tax free spend at Valentino in France and Italy, weeks 39-40 vs weeks 36-37 (issued forms). "
                   "After Chuseok (24-26 September) Korean travellers flocked to Paris and Milan.", S["body"]),
         Paragraph(f"+{(cn_gw / cn_pre - 1) * 100:.0f}%", S["big"]),
         Paragraph("Chinese shoppers' spend at Valentino in Europe during Golden Week (weeks 40-41) vs the two previous weeks. "
                   "New direct flights from Chengdu and visa fast-track supported the strongest Golden Week since 2019.", S["body"]),
         Image(f1, width=175 * mm, height=70 * mm),
         Paragraph("Issued forms, spend incl. VAT, EUR. Week 43 excluded (partial).", S["small"]), Spacer(1, 6)]
    rows = [["Nationality (W40)", "Forms", "Spend EUR k", "Share"]]
    w40s = W40.spend.sum()
    for n_, v in top.items():
        rows.append([NAT.get(n_, n_), f"{W40[W40.customer_nationality == n_].forms.sum():,}", f"{v / 1e3:,.0f}", f"{v / w40s * 100:.0f}%"])
    E.append(table(rows, [60 * mm, 30 * mm, 35 * mm, 25 * mm], colors.HexColor("#5B2C6F"), font="NSans", zebra=colors.HexColor("#F3EEF6")))
    E.append(PageBreak())
    E.append(Paragraph("Market context (all luxury merchants, Aurelia network)", S["h1"]))
    rows = [["Destination", "Nationality", "Spend YoY Sep 26", "Spend YoY 1-18 Oct 26"],
            ["France", "South Korea", "+18%", "+11%"], ["Italy", "South Korea", "+14%", "+9%"],
            ["Italy", "China", "+6%", "+31%"], ["France", "China", "+4%", "+24%"], ["Switzerland", "China", "-3%", "+12%"],
            ["Japan", "China", "+21%", "+17%"], ["Japan", "Taiwan", "+9%", "+12%"], ["Germany", "Gulf (GCC)", "+2%", "-4%"],
            ["Spain", "Latin America", "+7%", "+5%"]]
    E.append(table(rows, [40 * mm, 40 * mm, 40 * mm, 45 * mm], colors.HexColor("#5B2C6F"), font="NSans", zebra=colors.HexColor("#F3EEF6")))
    E.append(Spacer(1, 6))
    for t_ in ["Korean spend in Europe accelerated after Chuseok; fashion & outerwear the fastest-growing category for Korean travellers.",
               "Chinese Golden Week 2026 spend in Europe was the highest since 2019 in our network (Milan and Paris leading).",
               "In Japan the weak yen keeps Chinese and Taiwanese spend elevated; we expect a peak before the 1 November price increases announced by several luxury houses.",
               "Average spend per form for Chinese shoppers in Italy: EUR 2,650 (luxury fashion), up 8% YoY.",
               "The UK is not covered (no VAT refund scheme for tourists since 2021)."]:
        E.append(Paragraph(t_, S["body"], bulletText="•"))
    E.append(Spacer(1, 8))
    E.append(Paragraph("Methodology: issued forms at the time of purchase; customs validation typically 70-85% of issued forms and lags "
                       "1-3 weeks. Spend includes VAT and is not net of refunds or cancellations. Week = Monday-Sunday. EUR at monthly ECB average.",
                       S["small"]))
    doc.build(E)
    facts.update(dict(kr_fr_it_w39_40_vs_w36_37=round((kr_late / kr_aug - 1) * 100, 1),
                      cn_eu_w40_41_vs_w38_39=round((cn_gw / cn_pre - 1) * 100, 1),
                      total_forms=int(f.shape[0]), validated_share=round(f.validated.mean() * 100, 1),
                      w41_it_dup_rows=int(len(dup)), w41_it_dup_forms=int(dup.forms.sum())))
    facts.save()


if __name__ == "__main__":
    main()
