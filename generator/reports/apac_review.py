"""APAC Monthly Business Review - September 2026 (PPTX).

Author: APAC Business Analytics, Hong Kong. Definitions:
- constant FX = 2025 average rates (FX_AVG_2025) for CY and LY
- "Sales" = GROSS of returns (gross - discounts, returns not deducted) from BI, calendar September
- Japan: pasted from the Japan country file -> tax-inclusive (x1.10), NET of returns, 9月度 = 5 weeks Aug 30-Oct 3
- Korea dept stores (SEL02, BUS01): from the Korea file, dept-store fiscal month Aug 26-Sep 25, VAT removed (/1.10), net
- Budget at budget rates (different FX basis than actuals)
Planted mistake: Singapore value left in SGD (not converted) in market table/chart.
"""
import datetime as dt

import numpy as np
import pandas as pd

import japan_report as jr
import korea_report as kr
from common import (BUDGET_RATE, D, FX_AVG_2025, FX_MONTHLY, Facts, daily, kpi, outdir, pos, stores)
from pptkit import XL_CHART_TYPE, Deck, MSO_ANCHOR, PP_ALIGN

OUTD = outdir("apac")
facts = Facts("apac_review")
M0, M1 = D(2026, 9, 1), D(2026, 9, 30)
L0, L1 = D(2025, 9, 1), D(2025, 9, 30)
MARKETS = {"Japan": ["TYO01", "TYO02", "OSA01"], "Korea": ["SEL01", "SEL02", "BUS01"],
           "Mainland China": ["SHA01", "BJS01", "CDU01"], "HK & Taiwan": ["HKG01", "TPE01"],
           "South-East Asia": ["SIN01"], "Oceania": ["SYD01"]}
TH = dict(font="Arial", fg="222222", accent="0E4D64", accent2="E07A5F", muted="7A869A", light="EEF3F5")


def bi_gross(store_ids, d0, d1, rate):
    dd = daily()
    x = dd[dd.store_id.isin(store_ids) & (dd.date >= d0) & (dd.date <= d1)]
    return (x.sales_before_returns_lc / x.currency.map(rate)).sum()


def bi_net_month_fx(store_ids, d0, d1):
    k = kpi()
    x = k[k.store_id.isin(store_ids) & (k.date >= d0) & (k.date <= d1)]
    return (x.net_sales_lc / x.currency.map(FX_MONTHLY["2026-09"])).sum()


def compute():
    jcy, jly = jr.month_table()
    kcy, kly, _ = kr.month_table()
    k = kpi()
    res = {}
    for m, ss in MARKETS.items():
        if m == "Japan":
            cy = jcy.net_tax.sum() / FX_AVG_2025["JPY"]
            ly = jly.net_tax.sum() / FX_AVG_2025["JPY"]
        elif m == "Korea":
            cy = kcy.vat.sum() / 1.10 / FX_AVG_2025["KRW"] + bi_gross(["SEL01"], M0, M1, FX_AVG_2025)
            ly = kly.vat.sum() / 1.10 / FX_AVG_2025["KRW"] + bi_gross(["SEL01"], L0, L1, FX_AVG_2025)
        else:
            cy = bi_gross(ss, M0, M1, FX_AVG_2025)
            ly = bi_gross(ss, L0, L1, FX_AVG_2025)
        x = k[k.store_id.isin(ss) & (k.date >= M0) & (k.date <= M1)]
        xl = k[k.store_id.isin(ss) & (k.date >= L0) & (k.date <= L1)]
        bud = (x.budget_lc / x.currency.map(BUDGET_RATE)).sum()
        true_net = bi_net_month_fx(ss, M0, M1)
        res[m] = dict(cy=cy, ly=ly, bud=bud, vis=x.visitors_in.sum(), rec=x.receipts.sum(), vis_ly=xl.visitors_in.sum(),
                      rec_ly=xl.receipts.sum(), true_net_flashfx=true_net,
                      bi_eur_bud=x.net_sales_eur_bud.sum())
    # planted: SIN01 value shown in SGD (constant-FX conversion skipped)
    sin_sgd = daily()
    s = sin_sgd[(sin_sgd.store_id == "SIN01") & (sin_sgd.date >= M0) & (sin_sgd.date <= M1)].sales_before_returns_lc.sum()
    sl = sin_sgd[(sin_sgd.store_id == "SIN01") & (sin_sgd.date >= L0) & (sin_sgd.date <= L1)].sales_before_returns_lc.sum()
    res["South-East Asia"]["cy_correct"] = res["South-East Asia"]["cy"]
    res["South-East Asia"]["cy"] = s  # wrong: SGD
    res["South-East Asia"]["ly"] = sl  # LY also SGD -> growth % still right
    return pd.DataFrame(res).T


def main():
    t = compute()
    tot_cy, tot_ly, tot_bud = t.cy.sum(), t.ly.sum(), t.bud.sum()
    g = (tot_cy / tot_ly - 1) * 100
    vb = (tot_cy / tot_bud - 1) * 100
    d = Deck(TH)

    def header(s, title, kicker=None):
        d.text(s, 0.6, 0.35, 11.5, 0.7, title, size=26, bold=True, color=TH["accent"])
        if kicker:
            d.text(s, 0.6, 1.0, 12, 0.5, kicker, size=13, color=TH["muted"])
        d.text(s, 0.6, 7.0, 9, 0.3, "APAC Business Analytics  |  Confidential - Internal use only", size=8, color=TH["muted"])
        d.text(s, 12.0, 7.0, 0.8, 0.3, str(d.n), size=8, color=TH["muted"], align=PP_ALIGN.RIGHT)

    # 1 title
    s = d.slide(bg=TH["accent"])
    d.text(s, 0.8, 2.3, 11, 1.0, "APAC Monthly Business Review", size=40, bold=True, color="FFFFFF")
    d.text(s, 0.8, 3.3, 11, 0.6, "September 2026", size=24, color="F2CC8F")
    d.text(s, 0.8, 5.6, 11, 1.0, ["APAC Business Analytics - Hong Kong", "Distribution: APAC MD, Country GMs, HQ Retail & Finance",
                                   "v1.1 - 13 October 2026"], size=12, color="DDE7EA")

    # 2 key messages
    s = d.slide()
    header(s, "Key messages", "September at constant FX (2025 average rates)")
    msgs = [
        f"APAC September sales EUR {tot_cy / 1e6:.1f} m at constant FX, {g:+.1f}% vs LY and {vb:+.1f}% vs budget.",
        "Greater China leads: POLARIS (Genius) launch on 24/9 sold through fast in Shanghai, Beijing and Chengdu; strong local clientele before Golden Week.",
        "Japan held back by an unusually warm end of September (27-29°C): outerwear slow, knit and sneakers fine. Inbound (CN/TW) recovering in the last week.",
        f"Korea {(t.loc['Korea'].cy / t.loc['Korea'].ly - 1) * 100:+.1f}%: Cheongdam flagship ahead of the department stores. Chuseok holidays (24-26/9) moved part of local demand abroad.",
        "Hong Kong lost 1.5 days to typhoon signal 8 (17-18/9).",
        "Early October: ILVARO powder pink sold out across Asia within 1-3 days after the LUMIERE / Yoon Ha-eun photos (1/10). We need replenishment.",
        "Sydney: spring season, clients ask for T-shirts/polos/light jackets; the statistical forecast still pushes down jackets.",
    ]
    d.text(s, 0.8, 1.6, 11.8, 5.0, msgs, size=15, bullets=True, spacing=9)

    # 3 KPI tiles
    s = d.slide()
    header(s, "September at a glance", "Constant FX; Japan incl. consumption tax; Korea dept stores on dept-store month")
    vis, vis_ly = t.vis.sum(), t.vis_ly.sum()
    conv, conv_ly = t.rec.sum() / vis * 100, t.rec_ly.sum() / vis_ly * 100
    tiles = [("Sales", f"EUR {tot_cy / 1e6:.1f} m", f"{g:+.1f}% vs LY"), ("vs Budget", f"{vb:+.1f}%", f"Budget EUR {tot_bud / 1e6:.1f} m"),
             ("Traffic", f"{vis / 1e3:,.0f} k", f"{(vis / vis_ly - 1) * 100:+.1f}% vs LY"),
             ("Conversion", f"{conv:.1f}%", f"LY {conv_ly:.1f}%")]
    for i, (a, b, c) in enumerate(tiles):
        x = 0.7 + i * 3.1
        d.rect(s, x, 1.9, 2.8, 2.2, TH["light"])
        d.text(s, x + 0.2, 2.0, 2.4, 0.4, a, size=13, color=TH["muted"])
        d.text(s, x + 0.2, 2.5, 2.5, 0.8, b, size=28, bold=True, color=TH["accent"])
        d.text(s, x + 0.2, 3.4, 2.5, 0.4, c, size=12, color=TH["accent2"] if "-" in c[:2] else TH["fg"])
    d.text(s, 0.7, 4.6, 12, 1.8, [
        "Sales before returns (returns are tracked separately by the Quality team).",
        "Traffic = door counters; department-store corners use the dept-store feed. LY receipts partially estimated from legacy POS.",
        "Budget converted at budget 2026 rates (HQ standard)."], size=11, color=TH["muted"], bullets=True)

    # 4 market table + chart
    s = d.slide()
    header(s, "Sales by market", "EUR k, constant FX")
    rows = [["Market", "Sep 26", "Sep 25", "vs LY", "Budget", "vs Bud"]]
    for m, x in t.iterrows():
        rows.append([m, f"{x.cy / 1e3:,.0f}", f"{x.ly / 1e3:,.0f}", f"{(x.cy / x.ly - 1) * 100:+.1f}%", f"{x.bud / 1e3:,.0f}",
                     f"{(x.cy / x.bud - 1) * 100:+.1f}%"])
    rows.append(["APAC", f"{tot_cy / 1e3:,.0f}", f"{tot_ly / 1e3:,.0f}", f"{g:+.1f}%", f"{tot_bud / 1e3:,.0f}", f"{vb:+.1f}%"])
    d.table(s, 0.6, 1.6, 6.2, rows, col_w=[1.7, 0.95, 0.95, 0.85, 0.95, 0.8], size=11, zebra=TH["light"], bold_last=True,
            row_h=0.36)
    d.chart(s, 7.1, 1.5, 5.8, 4.9, XL_CHART_TYPE.BAR_CLUSTERED, list(t.index)[::-1],
            [("Sep 26", [round(v / 1e3) for v in t.cy[::-1]]), ("Sep 25", [round(v / 1e3) for v in t.ly[::-1]])],
            colors=[TH["accent"], "B8C4CC"], title="EUR k", labels=False)
    d.text(s, 0.6, 5.4, 6.3, 1.2, ["Japan: from Japan country report (9月度 30/8-3/10, tax incl.).",
                                   "Korea: Hyundai Apgujeong + Shinsegae Centum on dept-store month (26/8-25/9), VAT excl.; Cheongdam calendar month.",
                                   "Other markets: BI, calendar month."], size=9, color=TH["muted"])

    # 5 Japan
    jcy, jly = jr.month_table()
    s = d.slide()
    header(s, "Japan - warm weather delayed outerwear", "Source: Japan country monthly report (tax incl., JPY m)")
    weeks = jr.sunday_weeks(D(2026, 8, 30), 5)
    cyw, lyw = [], []
    for a0, a1 in weeks:
        cyw.append(round(jr.period(jr.JP, a0, a1).net_tax.sum() / 1e6))
        lyw.append(round(jr.period(jr.JP, a0 - dt.timedelta(days=364), a1 - dt.timedelta(days=364)).net_tax.sum() / 1e6))
    d.chart(s, 0.6, 1.5, 6.6, 4.6, XL_CHART_TYPE.COLUMN_CLUSTERED, [f"{a.month}/{a.day}" for a, _ in weeks],
            [("2026", cyw), ("2025", lyw)], colors=[TH["accent"], "B8C4CC"], title="Weekly sales Sun-Sat, JPY m (tax incl.)")
    jr_ratio = jcy.net_tax.sum() / jly.net_tax.sum() * 100
    d.text(s, 7.6, 1.6, 5.2, 4.8, [
        [(f"9月度 前年比 {jr_ratio:.1f}%", {"bold": True, "size": 16, "color": TH["accent"]})],
        "Ginza and Shinsaibashi recovered in the last week with Golden Week inbound (CN, TW).",
        "Max temperatures 27-29°C until 11/10: down jackets slow, knit and Trailgrip OK.",
        "Price increase 1 November (+8% avg on carry-over) to be announced to clients on 9/10: we expect pre-buying.",
        [("「残暑の影響でダウンの動きが鈍い。価格改定の告知後に駆け込み需要を見込む」 - 日本支社 営業企画部", {"italic": True, "size": 12, "color": TH["muted"]})],
    ], size=13, spacing=8)

    # 6 Korea
    kcy, kly, (a0, a1, b0, b1) = kr.month_table()
    s = d.slide()
    header(s, "Korea - Cheongdam leads, department stores steady", "Dept stores on dept-store month 26/8-25/9; Cheongdam calendar month")
    k = kpi()
    sel01 = bi_gross(["SEL01"], M0, M1, FX_AVG_2025)
    sel01_ly = bi_gross(["SEL01"], L0, L1, FX_AVG_2025)
    rows = [["Store", "Sep 26 EUR k", "Sep 25 EUR k", "vs LY"]]
    for sid, nm in (("SEL02", "Hyundai Apgujeong"), ("BUS01", "Shinsegae Centum City")):
        a = kcy.loc[sid].vat / 1.1 / FX_AVG_2025["KRW"]
        b = kly.loc[sid].vat / 1.1 / FX_AVG_2025["KRW"]
        rows.append([nm, f"{a / 1e3:,.0f}", f"{b / 1e3:,.0f}", f"{(a / b - 1) * 100:+.1f}%"])
    rows.append(["Cheongdam Flagship", f"{sel01 / 1e3:,.0f}", f"{sel01_ly / 1e3:,.0f}", f"{(sel01 / sel01_ly - 1) * 100:+.1f}%"])
    d.table(s, 0.6, 1.7, 6.0, rows, col_w=[2.4, 1.2, 1.2, 1.2], size=12, zebra=TH["light"], row_h=0.42)
    d.text(s, 7.0, 1.6, 5.8, 4.8, [
        "Chuseok (24-26/9): many Korean clients travelling to Europe; strong demand for black MAIRE reported by Paris and Milan (Korean shoppers).",
        "BADY and ILVARO best sellers in women; LOGO HOODIE strong with younger clients.",
        "Busan Film Festival from 1/10 will support Centum City in October.",
        [("\"추석 연휴 해외 출국 고객 증가로 9월 하순 국내 매장 방문 감소\" - Korea Retail team", {"italic": True, "size": 12, "color": TH["muted"]})],
    ], size=13, bullets=False, spacing=8)

    # 7 Greater China
    s = d.slide()
    header(s, "Greater China - POLARIS is a hit", "Mainland China and HK & Taiwan, constant FX, sales before returns")
    dd = daily()
    pol = dd[dd.style_name.str.startswith("POLARIS") & (dd.date >= D(2026, 9, 24)) & (dd.date <= M1)]
    polm = pol.groupby("region").units_sold.sum()
    polap = pol[pol.region == "APAC"].groupby("subregion").units_sold.sum()
    d.chart(s, 0.6, 1.5, 6.0, 4.6, XL_CHART_TYPE.COLUMN_CLUSTERED, list(polap.index), [("Units 24-30/9", [int(v) for v in polap.values])],
            colors=[TH["accent2"]], title="POLARIS units sold 24-30/9 by APAC market", legend=False, labels=True)
    hk = t.loc["HK & Taiwan"]
    cn = t.loc["Mainland China"]
    d.text(s, 7.0, 1.6, 5.8, 4.8, [
        f"Mainland China {(cn.cy / cn.ly - 1) * 100:+.1f}% vs LY. POLARIS: {int(polap.get('Mainland China', 0))} units in the first 7 days "
        f"(vs {int(polm.get('EMEA', 0))} in all of EMEA).",
        "Clients from Shanghai and Beijing travelling domestically for Golden Week from 1/10 (Chengdu Taikoo Li very busy).",
        f"HK & Taiwan {(hk.cy / hk.ly - 1) * 100:+.1f}%: Canton Road closed on 17/9 (typhoon signal 8), reopened 18/9 15:00.",
        [("「POLARIS 系列上市首周表现超预期，斗篷款多个门店断码」 - 中国区零售团队", {"italic": True, "size": 12, "color": TH["muted"]})],
    ], size=13, spacing=8)

    # 8 SEA & Oceania
    s = d.slide()
    header(s, "South-East Asia & Oceania", "Singapore Marina Bay Sands, Sydney Castlereagh St")
    se, oc = t.loc["South-East Asia"], t.loc["Oceania"]
    dd = daily()
    syd = dd[(dd.store_id == "SYD01") & (dd.date >= M0) & (dd.date <= M1)]
    mix = syd.groupby("season_group").sales_before_returns_lc.sum()
    mix = (mix / mix.sum() * 100).round(0)
    d.text(s, 0.6, 1.6, 6.0, 4.8, [
        [("Singapore", {"bold": True, "size": 16, "color": TH["accent"]})],
        f"Sales {se.cy / 1e3:,.0f} k, {(se.cy / se.ly - 1) * 100:+.1f}% vs LY. Jersey and footwear drive the store; F1 Grand Prix 9-11/10 ahead.",
        [("Sydney", {"bold": True, "size": 16, "color": TH["accent"]})],
        f"Sales {oc.cy / 1e3:,.0f} k, {(oc.cy / oc.ly - 1) * 100:+.1f}% vs LY. It is spring: clients ask for T-shirts, polos and light jackets.",
        "The central forecast still allocates heavy down jackets to Sydney (northern-hemisphere seasonality). We asked Planning to review.",
    ], size=13, spacing=8)
    d.chart(s, 7.0, 1.6, 5.6, 4.4, XL_CHART_TYPE.PIE, list(mix.index), [("SYD01 mix %", [float(v) for v in mix.values])],
            colors=None, title="SYD01 September sales mix by season group (%)", legend=True, labels=True, number_format='0"%"')

    # 9 tourism
    s = d.slide()
    header(s, "Clientele - inbound share by market", "Share of sales lines by customer nationality at POS, September")
    p = pos()
    q = p[(p.region == "APAC") & (p.line_type == "SALE") & (p.date >= M0) & (p.date <= M1)]
    rows = [["Market", "Domestic", "Mainland CN", "Taiwan", "Korea", "Japan", "Other", "Tax-free share"]]
    dom = {"Japan": "JP", "Korea": "KR", "Mainland China": "CN", "HK & Taiwan": "HK", "South-East Asia": "SG", "Oceania": "AU"}
    for m, ss in MARKETS.items():
        y = q[q.store_id.isin(ss)]
        tot = y.net_amount.sum()
        sh = y.groupby("customer_nationality").net_amount.sum() / tot * 100
        dm = dom[m]
        other = 100 - sh.get(dm, 0) - (sh.get("CN", 0) if dm != "CN" else 0) - sh.get("TW", 0) - (sh.get("KR", 0) if dm != "KR" else 0) - (sh.get("JP", 0) if dm != "JP" else 0)
        rows.append([m, f"{sh.get(dm, 0):.0f}%", "-" if dm == "CN" else f"{sh.get('CN', 0):.0f}%", f"{sh.get('TW', 0):.0f}%",
                     "-" if dm == "KR" else f"{sh.get('KR', 0):.0f}%", "-" if dm == "JP" else f"{sh.get('JP', 0):.0f}%",
                     f"{other:.0f}%", f"{y[y.tax_free == 1].net_amount.sum() / tot * 100:.0f}%"])
    d.table(s, 0.6, 1.7, 12.0, rows, col_w=[2.4, 1.3, 1.4, 1.3, 1.3, 1.3, 1.3, 1.7], size=12, zebra=TH["light"], row_h=0.42)
    d.text(s, 0.6, 5.0, 12, 1.2, "Hong Kong 'domestic' = HK residents. Nationality is mandatory only for tax-free transactions; "
           "domestic share may be overstated.", size=10, color=TH["muted"])

    # 10 FW26
    s = d.slide()
    header(s, "FW26 new-in performance", "Units sold since launch to 30/9, APAC stores")
    x = dd[(dd.region == "APAC") & dd.style_name.isin(["ILVARO", "AMBRINE", "ARNEB", "ROSIERE", "WOOL TURTLENECK"]) & (dd.date <= M1)]
    u = x.groupby(["style_name", "subregion"]).units_sold.sum().unstack().fillna(0)
    cols = [c for c in ["Japan", "Korea", "Mainland China", "HK/Macau/TW", "South-East Asia", "Oceania"] if c in u.columns]
    d.chart(s, 0.6, 1.5, 8.0, 5.0, XL_CHART_TYPE.COLUMN_STACKED, list(u.index), [(c, [int(v) for v in u[c]]) for c in cols],
            colors=["0E4D64", "3D7EA6", "E07A5F", "F2CC8F", "81B29A", "B8C4CC"], title="Units sold by style and market")
    d.text(s, 8.9, 1.6, 4.0, 4.8, ["AMBRINE strongest in Mainland China (long coat silhouette).",
                                   "ILVARO launch quantity was small (allocation at 55% of model); black broken early in Seoul.",
                                   "ARNEB size feedback: fits large.",
                                   "Ask HQ: ILVARO re-order for Asia before the celebrity effect fades."], size=12, bullets=True, spacing=8)

    # 11 early October
    s = d.slide()
    header(s, "Early October update (1-11/10)", "Flash, BI daily data - not closed")
    il = dd[(dd.region == "APAC") & (dd.style_name == "ILVARO") & (dd.color_code == "510") & (dd.date >= D(2026, 10, 1)) &
            (dd.date <= D(2026, 10, 11))]
    il_by = il.groupby("date").units_sold.sum()
    days = [D(2026, 10, 1) + dt.timedelta(days=i) for i in range(11)]
    d.chart(s, 0.6, 1.5, 6.4, 4.4, XL_CHART_TYPE.COLUMN_CLUSTERED, [f"{x_.day}/10" for x_ in days],
            [("ILVARO powder pink units", [int(il_by.get(x_, 0)) for x_ in days])], colors=["E07A5F"],
            title="ILVARO powder pink - APAC daily units", legend=False, labels=True)
    gw = k[k.store_id.isin(MARKETS["Mainland China"]) & (k.date >= D(2026, 10, 1)) & (k.date <= D(2026, 10, 7))].net_sales_lc.sum()
    gw_ly = k[k.store_id.isin(MARKETS["Mainland China"]) & (k.date >= D(2025, 10, 1)) & (k.date <= D(2025, 10, 7))].net_sales_lc.sum()
    d.text(s, 7.3, 1.6, 5.6, 4.8, [
        "Yoon Ha-eun (LUMIERE) photographed in ILVARO powder pink at Paris Fashion Week on 1/10: pink sold out in all Asian stores in 1-3 days.",
        "DC top-up landed 8/10 - gone the same day. Seoul Cheongdam re-order held at Incheon customs (KC certificate), now expected 13/10.",
        f"Golden Week Mainland China 1-7/10: {(gw / gw_ly - 1) * 100:+.0f}% vs same dates LY (local currency).",
        "Japan: price increase announced 9/10, first signs of pre-buying.",
    ], size=13, bullets=True, spacing=8)

    # 12 risks & asks
    s = d.slide()
    header(s, "Risks & asks to HQ")
    rows = [["#", "Topic", "Ask", "Owner"],
            ["1", "ILVARO pink", "Emergency re-order + allocate 100% of next top-up to Asia", "Merchandising HQ"],
            ["2", "Japan price increase", "Extra MAYA/MAIRE stock for TYO01/OSA01 before 1/11", "Planning"],
            ["3", "Sydney", "Override forecast: shift to SS/light items until December", "Demand Planning"],
            ["4", "POLARIS", "Re-allocate EU/US POLARIS stock to Greater China", "Merchandising HQ"],
            ["5", "TIB vest", "Clarify defect scope (batch) - first returns in Japan", "Quality"],
            ["6", "Double 11", "Price-match policy for stores vs Tmall pre-sales from 20/10", "China Retail / E-com"]]
    d.table(s, 0.6, 1.5, 12.1, rows, col_w=[0.5, 2.4, 6.6, 2.6], size=12, zebra=TH["light"], row_h=0.5)

    # 13 appendix
    s = d.slide()
    header(s, "Appendix - definitions")
    d.text(s, 0.6, 1.4, 12.2, 5.4, [
        "Constant FX: all currencies converted at 2025 average rates (JPY 166.6, KRW 1,598, CNY 8.13, HKD 8.80, TWD 35.95, SGD 1.465, AUD 1.738 per EUR) for both years.",
        "Sales: gross sales less discounts, before customer returns (APAC standard). HQ flash reports net of returns.",
        "Japan: figures taken from the Japan country report: tax inclusive (consumption tax 10%), net of returns, fiscal month 9月度 = 30/8-3/10 (5 weeks Sun-Sat). LY on the same basis.",
        "Korea: Hyundai Apgujeong and Shinsegae Centum City from the Korea weekly report on department-store month (26/8-25/9), VAT removed; Cheongdam flagship calendar month from BI.",
        "Budget: HQ budget at budget 2026 FX rates.",
        "Traffic and conversion: BI KPI table, calendar month, all stores.",
    ], size=13, bullets=True, spacing=10)

    path = OUTD / "APAC_Monthly_Review_SEP2026_v1.1.pptx"
    d.save(path)

    se_true = t.loc["South-East Asia", "cy_correct"]
    facts.update(dict(
        total_cy=round(tot_cy), total_ly=round(tot_ly), growth=round(g, 1), vs_bud=round(vb, 1),
        markets={m: dict(cy=round(x.cy), ly=round(x.ly), growth=round((x.cy / x.ly - 1) * 100, 1),
                         true_net_sep_monthly_fx=round(x.true_net_flashfx), bi_eur_budget_rate=round(x.bi_eur_bud))
                 for m, x in t.iterrows()},
        sin_shown_sgd=round(t.loc["South-East Asia", "cy"]), sin_correct_eur_constfx=round(se_true),
        total_if_sin_correct=round(tot_cy - t.loc["South-East Asia", "cy"] + se_true),
        apac_true_net_sep_monthly_fx=round(t.true_net_flashfx.sum()), apac_bi_eur_budget_rate=round(t.bi_eur_bud.sum()),
        polaris_units_24_30sep=dict(polap.astype(int)), polaris_units_emea=int(polm.get("EMEA", 0)),
        gw_cn_growth_lc=round((gw / gw_ly - 1) * 100, 1)))
    facts.save()


if __name__ == "__main__":
    main()
