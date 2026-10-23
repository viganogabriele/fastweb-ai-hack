"""Marketing agency FW26 campaign performance report (PDF, glossy) - US/UK.

Agency: Halden & Rowe (fictional). 'Attributed sales uplift +22%' =
YoY growth of exposed stores (NYC01, NYC02, BHS01, LON01, LON02; MIA01 excluded) MINUS YoY growth of 'unexposed'
North-American stores (ASP01 pre-season, TOR01) over weeks 1-4 of flight (15/09-13/10). Confounds: LON01 VIC evening 08/10,
NYC01 Golden-Week/celebrity, Aspen off-season. True incremental effect ~ +6%.
"""
import datetime as dt
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch

from common import D, Facts, kpi, ly, outdir
from pdfkit import register_fonts, savefig

register_fonts()
OUTD = outdir("marketing")
TMP = Path(__file__).parent / "_tmp"
facts = Facts("agency")
NAVY, GOLD, CREAM = colors.HexColor("#0B1426"), colors.HexColor("#C8A464"), colors.HexColor("#F4F1EA")
EXPOSED = ["NYC01", "NYC02", "BHS01", "LON01", "LON02"]
CONTROL = ["ASP01", "TOR01"]
W0, W1 = D(2026, 9, 15), D(2026, 10, 13)


def yoy(st, a, b, col="net_sales_lc"):
    k = kpi()
    x = k[k.store_id.isin(st) & (k.date >= a) & (k.date <= b)][col].sum()
    y = k[k.store_id.isin(st) & (k.date >= ly(a)) & (k.date <= ly(b))][col].sum()
    return (x / y - 1) * 100


def main():
    exp_g, ctl_g = yoy(EXPOSED, W0, W1), yoy(CONTROL, W0, W1)
    uplift = exp_g - ctl_g
    exp_t, ctl_t = yoy(EXPOSED, W0, W1, "visitors_in"), yoy(CONTROL, W0, W1, "visitors_in")
    foot = exp_t - ctl_t
    per_store = {s: yoy([s], W0, W1) for s in EXPOSED + ["MIA01"] + CONTROL}
    all6_full = yoy(EXPOSED + ["MIA01"], W0, D(2026, 10, 21))

    # charts
    days = [W0 - dt.timedelta(days=14) + dt.timedelta(days=i) for i in range(14 + 29)]
    imp = np.array([0] * 14 + [18, 22, 21, 19, 17, 24, 26, 15, 14, 13, 12, 13, 16, 17, 12, 11, 11, 10, 10, 13, 14, 9, 9, 8, 9, 8, 11, 12, 8], float)
    fig, ax = plt.subplots(figsize=(7, 2.6), facecolor="#0B1426")
    ax.set_facecolor("#0B1426")
    ax.fill_between(range(len(days)), imp, color="#C8A464", alpha=0.85)
    ax.set_xticks(range(0, len(days), 7), [d.strftime("%b %d") for d in days[::7]], color="white", fontsize=7)
    ax.tick_params(colors="white", labelsize=7)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_ylabel("Impressions (M)", color="white", fontsize=7)
    ax.axvline(14, color="white", lw=0.6, ls=":")
    ax.text(14.3, imp.max() * 0.95, "Flight start Sep 15", color="white", fontsize=7)
    f_imp = savefig(fig, TMP / "ag_imp.png")

    fig, ax = plt.subplots(figsize=(4.2, 2.8), facecolor="white")
    vals = [exp_g, ctl_g]
    ax.bar(["Exposed stores", "Unexposed stores"], vals, color=["#C8A464", "#9AA3B2"], width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v + 1 if v >= 0 else v / 2, f"{v:+.1f}%", ha="center", fontsize=9, fontweight="bold", color="black" if v >= 0 else "white")
    ax.axhline(0, color="black", lw=0.6)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylabel("Sales YoY %", fontsize=8)
    ax.tick_params(labelsize=8)
    f_sales = savefig(fig, TMP / "ag_sales.png")

    path = OUTD / "HaldenRowe_Valentino_FW26_Campaign_Performance_US-UK_FINAL.pdf"
    from reportlab.pdfgen import canvas
    W, H = landscape(letter)
    c = canvas.Canvas(str(path), pagesize=(W, H))
    c.setTitle("FW26 Campaign Performance Report - US & UK")
    c.setAuthor("Halden & Rowe")

    def footer(dark=False, n=None):
        c.setFont("NSans", 7)
        c.setFillColor(colors.HexColor("#8C93A3") if dark else colors.HexColor("#7A7A7A"))
        c.drawString(0.6 * inch, 0.35 * inch, "HALDEN & ROWE  |  Prepared for Valentino Marketing  |  Confidential - Internal use only")
        if n:
            c.drawRightString(W - 0.6 * inch, 0.35 * inch, str(n))

    # cover
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.setFont("NSerif-L", 13)
    c.drawString(0.8 * inch, H - 1.0 * inch, "HALDEN & ROWE")
    c.setFillColor(colors.white)
    c.setFont("NSerif-B", 40)
    c.drawString(0.8 * inch, H - 3.0 * inch, "Into the Cold.")
    c.setFont("NSerif-L", 22)
    c.drawString(0.8 * inch, H - 3.6 * inch, "FW26 Campaign Performance Report")
    c.setFont("NSans-L", 13)
    c.drawString(0.8 * inch, H - 4.05 * inch, "United States & United Kingdom  |  Flight Sep 15 - Oct 21, 2026")
    c.setFillColor(GOLD)
    c.setFont("NSans", 10)
    c.drawString(0.8 * inch, 1.1 * inch, "FINAL  |  October 19, 2026")
    footer(True)
    c.showPage()

    # exec summary - hero numbers
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.setFont("NSerif-B", 26)
    c.drawString(0.8 * inch, H - 1.0 * inch, "A season-defining launch.")
    c.setFont("NSans-L", 11)
    c.drawString(0.8 * inch, H - 1.35 * inch, "Weeks 1-4 of flight delivered record reach and a measurable lift in store sales across exposed markets.")
    heroes = [(f"+{round(uplift):d}%", "Attributed sales uplift", "exposed vs. unexposed stores"),
              ("412M", "Impressions", "OOH + digital + social"),
              (f"+{round(foot):d}%", "Footfall uplift", "door counters, exposed stores"),
              ("4.8%", "Engagement rate", "Instagram + TikTok, organic + paid"),
              ("5.6x", "ROAS", "attributed revenue / media spend")]
    for i, (big, lab, sub) in enumerate(heroes):
        x = 0.8 * inch + i * 1.95 * inch
        c.setFillColor(NAVY)
        c.roundRect(x, H - 4.1 * inch, 1.8 * inch, 2.2 * inch, 8, stroke=0, fill=1)
        c.setFillColor(GOLD)
        c.setFont("NSerif-B", 30)
        c.drawCentredString(x + 0.9 * inch, H - 2.85 * inch, big)
        c.setFillColor(colors.white)
        c.setFont("NSans-B", 9)
        c.drawCentredString(x + 0.9 * inch, H - 3.35 * inch, lab)
        c.setFont("NSans-L", 7)
        c.drawCentredString(x + 0.9 * inch, H - 3.6 * inch, sub)
    c.setFillColor(NAVY)
    c.setFont("NSans", 10)
    y = H - 4.7 * inch
    for t in ["The 'Into the Cold' platform reached 38.6M unique users across the US and UK, 21% above plan.",
              "Hero film completion rate 71% (benchmark 54%); Madison Avenue and New Bond Street takeovers drove earned coverage.",
              "Store traffic and sales in exposed markets clearly outperformed unexposed markets during the flight.",
              "We recommend extending the flight into the holiday window and adding Toronto and Miami to the media plan."]:
        c.drawString(0.8 * inch, y, "—  " + t)
        y -= 0.3 * inch
    footer(False, 2)
    c.showPage()

    # media delivery
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("NSerif-B", 24)
    c.drawString(0.8 * inch, H - 1.0 * inch, "Media delivery")
    c.drawImage(f_imp, 0.6 * inch, H - 4.0 * inch, width=5.4 * inch, height=2.5 * inch)
    rows = [("Channel", "Impr. (M)", "Spend ($k)", "CPM ($)"), ("OOH (NYC, LA, MIA, LON)", "164.0", "1,920", "11.7"),
            ("Paid social (IG, TikTok)", "151.3", "1,310", "8.7"), ("Programmatic video", "58.2", "905", "15.5"),
            ("CTV", "21.9", "540", "24.7"), ("Search & Shopping", "16.6", "325", "19.6"), ("Total", "412.0", "5,000", "12.1")]
    yy = H - 1.6 * inch
    for i, r in enumerate(rows):
        c.setFont("NSans-B" if i in (0, len(rows) - 1) else "NSans", 9)
        c.setFillColor(GOLD if i == 0 else colors.white)
        c.drawString(6.3 * inch, yy, r[0])
        for j, v in enumerate(r[1:]):
            c.drawRightString(8.75 * inch + j * 0.8 * inch, yy, v)
        yy -= 0.3 * inch
    c.setFont("NSans-L", 8)
    c.setFillColor(colors.HexColor("#B8BFCC"))
    c.drawString(0.8 * inch, 1.0 * inch, "Source: ad servers (CM360), Meta/TikTok Ads Manager, OOH vendor proof-of-posting. Impressions not de-duplicated across channels.")
    footer(True, 3)
    c.showPage()

    # social
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.setFont("NSerif-B", 24)
    c.drawString(0.8 * inch, H - 1.0 * inch, "Social & earned")
    stats = [("38.6M", "unique reach"), ("4.8%", "engagement rate*"), ("71%", "video completion"), ("2,140", "earned articles"),
             ("+34%", "site sessions from US/UK"), ("0.92%", "CTR paid social")]
    for i, (a, b) in enumerate(stats):
        x = 0.8 * inch + (i % 3) * 3.0 * inch
        yv = H - 2.2 * inch - (i // 3) * 1.6 * inch
        c.setFont("NSerif-B", 28)
        c.setFillColor(NAVY)
        c.drawString(x, yv, a)
        c.setFont("NSans", 10)
        c.setFillColor(colors.HexColor("#555555"))
        c.drawString(x, yv - 0.3 * inch, b)
    c.setFont("NSans-L", 8)
    c.drawString(0.8 * inch, 1.2 * inch, "*Engagement rate = (likes + comments + shares + saves) / reach. Includes organic posts from brand ambassadors.")
    c.drawString(0.8 * inch, 1.0 * inch, "Note: the Paris Fashion Week celebrity moment (Oct 1) generated significant organic conversation; we include it in earned totals.")
    footer(False, 4)
    c.showPage()

    # store impact
    c.setFillColor(colors.white)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.setFont("NSerif-B", 24)
    c.drawString(0.8 * inch, H - 1.0 * inch, "Store impact")
    c.setFont("NSans-L", 11)
    c.drawString(0.8 * inch, H - 1.35 * inch, f"Weeks 1-4 of flight ({W0:%b %d} - {W1:%b %d}), sales year-over-year, local currency")
    c.drawImage(f_sales, 0.8 * inch, H - 5.2 * inch, width=4.3 * inch, height=2.9 * inch)
    rows = [("Store", "Market", "Sales YoY")] + [(s, m, f"{per_store[s]:+.1f}%") for s, m in
                                                 [("NYC01", "Exposed"), ("NYC02", "Exposed"), ("BHS01", "Exposed"), ("LON01", "Exposed"),
                                                  ("LON02", "Exposed"), ("ASP01", "Unexposed"), ("TOR01", "Unexposed")]]
    yy = H - 2.0 * inch
    for i, r in enumerate(rows):
        c.setFont("NSans-B" if i == 0 else "NSans", 9.5)
        c.setFillColor(NAVY)
        c.drawString(5.7 * inch, yy, r[0])
        c.drawString(6.6 * inch, yy, r[1])
        c.drawRightString(8.4 * inch, yy, r[2])
        yy -= 0.28 * inch
    c.setFillColor(GOLD)
    c.setFont("NSerif-B", 18)
    c.drawString(5.7 * inch, yy - 0.3 * inch, f"Attributed uplift: +{uplift:.1f} pts  ->  +{round(uplift)}%")
    c.setFillColor(colors.HexColor("#555555"))
    c.setFont("NSans-L", 7.5)
    c.drawString(0.8 * inch, 1.15 * inch, "Methodology: attributed uplift = YoY sales growth of exposed stores minus YoY sales growth of unexposed North American stores")
    c.drawString(0.8 * inch, 1.0 * inch, "(Aspen, Toronto) over the measurement window. Miami Design District excluded from the exposed group due to store operational")
    c.drawString(0.8 * inch, 0.85 * inch, "disruption in September. Store data provided by client (BI extract 14/10). Footfall uplift computed on the same basis using door counters.")
    footer(False, 5)
    c.showPage()

    # recommendations
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("NSerif-B", 24)
    c.drawString(0.8 * inch, H - 1.0 * inch, "What's next")
    c.setFont("NSans", 12)
    yy = H - 1.8 * inch
    for t in ["Extend the flight through December with a holiday creative rotation (+$2.1M).",
              "Add Toronto and Miami to the OOH plan - unexposed stores are clearly lagging.",
              "Retarget site visitors with IRIDIA and AUREA dynamic product ads.",
              "Build a store-level incrementality test with geo-holdouts for Q1 (we can design it)."]:
        c.setFillColor(GOLD)
        c.drawString(0.8 * inch, yy, "■")
        c.setFillColor(colors.white)
        c.drawString(1.1 * inch, yy, t)
        yy -= 0.45 * inch
    footer(True, 6)
    c.showPage()
    c.save()

    facts.update(dict(window=f"{W0}..{W1}", exposed_yoy=round(exp_g, 1), control_yoy=round(ctl_g, 1), uplift=round(uplift, 1),
                      footfall_uplift=round(foot, 1), per_store_yoy={k: round(v, 1) for k, v in per_store.items()},
                      all6_yoy_full_flight=round(all6_full, 1)))
    facts.save()


if __name__ == "__main__":
    main()
