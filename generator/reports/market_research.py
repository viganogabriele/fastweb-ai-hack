"""Market research PDF: 'Luxury Outerwear Pulse Q3 2026' by Castellane Advisory (fictional).

Generic syndicated study, fieldwork Jul 20 - Aug 10 2026, published Sep 30 2026. Numbers are NOT derived from internal
data (market-level, synthetic). Several claims contradict what internal data and stores show (see notes).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, Image, PageBreak, PageTemplate, Paragraph, Spacer)

from common import Facts, outdir
from pdfkit import register_fonts, savefig, style, table

register_fonts()
OUTD = outdir("market_research")
TMP = Path(__file__).parent / "_tmp"
facts = Facts("market_research")
TEAL = colors.HexColor("#0F5257")
SAND = colors.HexColor("#E9E3D6")
INK = colors.HexColor("#202020")


def charts():
    fig, ax = plt.subplots(figsize=(6, 2.8))
    regs = ["Europe", "North America", "Greater China", "Japan", "Korea", "RoW"]
    v25 = [5.1, 4.3, 3.9, 1.6, 1.2, 1.6]
    v26 = [5.25, 4.4, 4.2, 1.64, 1.18, 1.73]
    x = np.arange(len(regs))
    ax.bar(x - 0.2, v25, 0.4, color="#9DB8B5", label="2025")
    ax.bar(x + 0.2, v26, 0.4, color="#0F5257", label="2026E")
    ax.set_xticks(x, regs, fontsize=7.5, rotation=15)
    ax.set_ylabel("EUR bn", fontsize=8)
    ax.legend(frameon=False, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=8)
    f1 = savefig(fig, TMP / "mr_size.png")

    fig, ax = plt.subplots(figsize=(6, 2.6))
    segs = ["Long down coats", "Ski / performance", "Knit & hybrid", "Down vests", "Short down jackets", "Cropped puffers"]
    g = [6.2, 7.1, 5.0, 2.4, 1.1, -2.3]
    ax.barh(segs[::-1], g[::-1], color=["#C0504D" if v < 0 else "#0F5257" for v in g[::-1]])
    for i, v in enumerate(g[::-1]):
        ax.text(v + 0.2 if v >= 0 else 0.2, i, f"{v:+.1f}%", va="center", fontsize=8)
    ax.axvline(0, color="black", lw=0.6)
    ax.set_xlabel("Value growth 2026E vs 2025, %", fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=8)
    f2 = savefig(fig, TMP / "mr_seg.png")

    fig, ax = plt.subplots(figsize=(6, 2.6))
    nat = ["China", "USA", "Korea", "Japan", "Italy", "France", "Germany", "UK"]
    q2 = [61, 43, 49, 37, 33, 31, 35, 36]
    q3 = [62, 44, 41, 38, 34, 30, 36, 35]
    x = np.arange(len(nat))
    ax.plot(x, q2, "o--", color="#9DB8B5", label="Q2 2026")
    ax.plot(x, q3, "o-", color="#0F5257", label="Q3 2026")
    ax.set_xticks(x, nat, fontsize=8)
    ax.set_ylabel("% intending to buy (3 m)", fontsize=8)
    ax.annotate("-8 pp", (2, 41), (2.3, 30), fontsize=8, color="#C0504D", arrowprops=dict(arrowstyle="->", color="#C0504D"))
    ax.legend(frameon=False, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=8)
    f3 = savefig(fig, TMP / "mr_intent.png")

    fig, ax = plt.subplots(figsize=(4.5, 2.6))
    cols = ["Black", "Beige / camel", "Navy", "Off-white", "Grey", "Brown", "Pink", "Other"]
    sh = [46, 14, 9, 8, 7, 4, 2, 10]
    ax.bar(cols, sh, color=["#202020", "#C8B59A", "#1F3A5F", "#EDE8DF", "#9A9A9A", "#5A3A22", "#E7B7C0", "#BBBBBB"],
           edgecolor="#555555", linewidth=0.4)
    for i, v in enumerate(sh):
        ax.text(i, v + 1, f"{v}%", ha="center", fontsize=7)
    ax.set_xticks(range(len(cols)), cols, rotation=30, fontsize=7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=7)
    ax.set_title("Preferred colour, next outerwear purchase", fontsize=8, loc="left")
    f4 = savefig(fig, TMP / "mr_col.png")
    return f1, f2, f3, f4


def main():
    f1, f2, f3, f4 = charts()
    S = dict(h1=style("h1", "NSerif-B", 18, color=TEAL, spaceAfter=6), h2=style("h2", "NSans-B", 11, color=INK, spaceBefore=8, spaceAfter=3),
             body=style("b", "NSans", 9, leading=13, color=INK, spaceAfter=5), small=style("s", "NSans-I", 7, color=colors.grey),
             call=style("c", "NSerif-I", 12, leading=16, color=TEAL, spaceBefore=6, spaceAfter=6, leftIndent=10))

    def on_page(c, doc):
        w, h = A4
        c.saveState()
        c.setFont("NSans-B", 8)
        c.setFillColor(TEAL)
        c.drawString(18 * mm, h - 12 * mm, "CASTELLANE ADVISORY")
        c.setFont("NSans", 7)
        c.setFillColor(colors.grey)
        c.drawRightString(w - 18 * mm, h - 12 * mm, "Luxury Outerwear Pulse  |  Q3 2026")
        c.drawString(18 * mm, 10 * mm, "© 2026 Castellane Advisory. Licensed to subscriber - redistribution prohibited.")
        c.drawRightString(w - 18 * mm, 10 * mm, str(doc.page))
        c.restoreState()

    def on_cover(c, doc):
        w, h = A4
        c.saveState()
        c.setFillColor(TEAL)
        c.rect(0, h * 0.42, w, h * 0.58, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("NSans-B", 11)
        c.drawString(20 * mm, h - 25 * mm, "CASTELLANE ADVISORY")
        c.setFont("NSerif-B", 34)
        c.drawString(20 * mm, h - 95 * mm, "Luxury Outerwear")
        c.drawString(20 * mm, h - 110 * mm, "Pulse")
        c.setFont("NSerif-L", 18)
        c.drawString(20 * mm, h - 125 * mm, "Q3 2026 - Market, consumers, outlook")
        c.setFillColor(INK)
        c.setFont("NSans", 9)
        c.drawString(20 * mm, 60 * mm, "Syndicated study - published 30 September 2026")
        c.drawString(20 * mm, 54 * mm, "Consumer fieldwork: 20 July - 10 August 2026, n = 4,212 HNW / aspirational luxury consumers")
        c.drawString(20 * mm, 48 * mm, "Markets: CN, KR, JP, US, IT, FR, DE, UK")
        c.drawString(20 * mm, 30 * mm, "Licensed to: Valentino S.p.A. - Strategy & Consumer Insights")
        c.restoreState()

    path = OUTD / "Castellane_Luxury_Outerwear_Pulse_Q3-2026.pdf"
    doc = BaseDocTemplate(str(path), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=20 * mm,
                          bottomMargin=16 * mm, title="Luxury Outerwear Pulse Q3 2026", author="Castellane Advisory")
    fr = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height)
    doc.addPageTemplates([PageTemplate("cover", [fr], onPage=on_cover), PageTemplate("p", [fr], onPage=on_page)])
    from reportlab.platypus import NextPageTemplate as NPT
    E = [NPT("p"), Spacer(1, 1), PageBreak()]

    E.append(Paragraph("Key takeaways", S["h1"]))
    for t in [
        "The global luxury outerwear market is set to reach <b>EUR 18.4 bn in 2026</b> (+4.1% at constant FX), a normalisation after the post-pandemic boom.",
        "<b>Long down coats</b> and <b>ski/performance</b> lead growth; <b>cropped puffers are losing share</b> (-2.3%) as the silhouette cycle turns to longer lengths.",
        "<b>Korean demand is cooling</b>: purchase intent down 8 pp quarter-on-quarter, with younger consumers trading down and travelling less to Europe.",
        "Chinese outbound travel to Europe still at ~72% of 2019 levels; we expect <b>Golden Week 2026 to favour domestic and short-haul destinations</b> (Japan, Korea, Thailand) over Europe.",
        "Colour: black remains dominant (46%); <b>brown remains a niche</b> (4%) despite runway visibility.",
        "Japan: weak yen and announced price increases by several houses should pull forward Q4 demand.",
        "Weather: seasonal models point to a <b>mild start of autumn in Central Europe</b>; heavy outerwear sell-through likely back-loaded to November-December.",
        "Designer collaborations / capsules show signs of fatigue among Chinese consumers (-5 pp in 'very interested').",
    ]:
        E.append(Paragraph(t, S["body"], bulletText="•"))
    E.append(Paragraph("“Q4 will be a game of patience: inventory discipline over chasing early-season volume.”", S["call"]))
    E.append(PageBreak())

    E.append(Paragraph("1. Market size", S["h1"]))
    E.append(Paragraph("Personal luxury outerwear (down jackets and coats, technical/ski outerwear, outerwear-adjacent knit) at retail value, "
                       "constant 2025 FX. Includes DTC, wholesale and e-commerce of the 14 brands in our panel plus long tail estimate.", S["body"]))
    E.append(Image(f1, width=165 * mm, height=77 * mm))
    rows = [["Region", "2025 (EUR bn)", "2026E (EUR bn)", "Growth"],
            ["Europe", "5.10", "5.25", "+2.9%"], ["North America", "4.30", "4.40", "+2.3%"], ["Greater China", "3.90", "4.20", "+7.7%"],
            ["Japan", "1.60", "1.64", "+2.5%"], ["Korea", "1.20", "1.18", "-1.7%"], ["RoW", "1.60", "1.73", "+8.1%"],
            ["Total", "17.70", "18.40", "+4.0%"]]
    E.append(table(rows, [55 * mm, 35 * mm, 35 * mm, 30 * mm], TEAL, font="NSans", zebra=SAND, bold_last=True))
    E.append(Paragraph("Totals may not add up due to rounding. Growth 4.1% in the text refers to unrounded values.", S["small"]))
    E.append(PageBreak())

    E.append(Paragraph("2. Segments", S["h1"]))
    E.append(Image(f2, width=165 * mm, height=71 * mm))
    E.append(Paragraph("Longer silhouettes are taking over. After three seasons of growth, <b>cropped and boxy puffers</b> are now the weakest "
                       "segment: our retail panel shows full-price sell-through on cropped styles 6 points below last year in July-August. "
                       "We would be cautious on re-orders of cropped styles for FW26.", S["body"]))
    E.append(Paragraph("Down vests are stable; we note sporadic social-media complaints on zipper quality across several brands "
                       "(not brand specific).", S["body"]))
    E.append(PageBreak())

    E.append(Paragraph("3. Consumer survey", S["h1"]))
    E.append(Paragraph("Intent to purchase luxury outerwear in the next 3 months (top-2 box), by nationality.", S["body"]))
    E.append(Image(f3, width=165 * mm, height=71 * mm))
    E.append(Paragraph("<b>Korea</b> is the only market with a significant drop (-8 pp). Drivers: higher household debt service, "
                       "a strong dollar, and a shift of the 25-34 cohort towards contemporary brands. We expect Korean spending "
                       "in European luxury stores to slow in H2.", S["body"]))
    E.append(Image(f4, width=120 * mm, height=69 * mm))
    E.append(Paragraph("Brown/chocolate is very visible on runways but remains a niche at purchase (4%); pink at 2%. "
                       "We recommend keeping colour bets on core neutrals.", S["body"]))
    E.append(PageBreak())

    E.append(Paragraph("4. Travel retail & tourism", S["h1"]))
    rows = [["Flow", "2026 vs 2019", "Q4 view"], ["China -> Europe", "72%", "Recovery slow; GW favours domestic/short-haul"],
            ["China -> Japan", "118%", "Strong, weak yen"], ["Korea -> Europe", "96%", "Slowing in H2"],
            ["US -> Europe", "131%", "Peak passed in summer"], ["Middle East -> Europe", "104%", "Stable"],
            ["Japan outbound", "68%", "Weak yen limits travel"]]
    E.append(table(rows, [45 * mm, 30 * mm, 90 * mm], TEAL, font="NSans", zebra=SAND, align_right_from=1))
    E.append(Spacer(1, 6))
    E.append(Paragraph("Tax-free spend data from refund operators (issued forms) confirm a soft summer for Chinese spending in Europe "
                       "(-6% YoY in August). New direct routes (e.g. Chengdu-Milan) are positive but small in volume.", S["body"]))
    E.append(PageBreak())

    E.append(Paragraph("5. Brand health (panel)", S["h1"]))
    rows = [["Brand (anonymised where requested)", "Awareness", "Consideration", "Δ consid. QoQ"],
            ["Valentino", "78%", "41%", "+1 pp"], ["Canadian outerwear brand", "71%", "33%", "+3 pp"],
            ["French heritage ski brand", "44%", "19%", "0 pp"], ["Italian luxury house A (outerwear line)", "82%", "27%", "-1 pp"],
            ["Scandinavian technical brand", "39%", "17%", "+2 pp"]]
    E.append(table(rows, [80 * mm, 25 * mm, 30 * mm, 30 * mm], TEAL, font="NSans", zebra=SAND))
    E.append(Spacer(1, 6))
    E.append(Paragraph("Capsule / designer collaborations: 'very interested' among Chinese respondents fell from 38% to 33%. "
                       "We read this as early fatigue; capsule launches in Q4 may underperform in China.", S["body"]))
    E.append(PageBreak())

    E.append(Paragraph("6. Q4 2026 outlook", S["h1"]))
    for t in ["<b>Weather</b>: seasonal ensemble (ECMWF SEAS5 / C3S multi-system, August run) indicates above-normal temperatures in "
              "Central Europe for October; first cold spell more likely in mid-November.",
              "<b>Japan</b>: price increases announced for November by at least four houses; expect pull-forward in October.",
              "<b>China</b>: Double 11 pre-sales expected to start around 20 October, earlier than 2025; store traffic may soften.",
              "<b>US</b>: holiday season expected flat in real terms; brand campaigns should focus on incrementality measurement.",
              "<b>Korea</b>: cautious; we would not plan growth above +2%."]:
        E.append(Paragraph(t, S["body"], bulletText="•"))
    E.append(Spacer(1, 10))
    E.append(Paragraph("Methodology", S["h2"]))
    E.append(Paragraph("Market sizing triangulated from company reports, retail panel (312 doors, 14 brands) and expert interviews. "
                       "Consumer survey online, quota sampled; margin of error ±2-3 pp per market. Fieldwork closed on 10 August 2026: "
                       "events after that date are not reflected. Not investment advice.", S["small"]))
    doc.build(E)
    facts.update(dict(claims=["Korean demand cooling -8pp", "cropped losing share", "brown niche 4%", "GW favours domestic",
                              "mild October Central Europe", "capsule fatigue China"], fieldwork="2026-07-20..2026-08-10"))
    facts.save()


if __name__ == "__main__":
    main()
