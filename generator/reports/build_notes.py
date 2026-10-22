"""Writes generated/ground_truth/answer_keys/reports_notes.md (answer key) from the facts saved by each report script."""
import json

import pandas as pd

from common import (BUDGET_RATE, D, FACTS, FX_AVG_2025, FX_MONTHLY, GT, NRF_2026, daily, kpi, ly, pos)


def F(name):
    return json.loads((FACTS / f"{name}.json").read_text())


def eur(x, d=2):
    return f"EUR {x / 1e6:,.{d}f} m"


def main():
    fl, em, jp, kr, ap, cn, am, me, ag, tf, q, bo, dg = (F(n) for n in [
        "flash", "emea_mbr", "japan", "korea", "apac_review", "china", "americas", "merch", "agency", "taxfree", "quality",
        "board", "digital"])
    k = kpi()
    M0, M1 = D(2026, 9, 1), D(2026, 9, 30)
    x = k[(k.date >= M0) & (k.date <= M1)].copy()
    x["eur_m"] = x.net_sales_lc / x.currency.map(FX_MONTHLY["2026-09"])
    reg_m = x.groupby("region").eur_m.sum()
    reg_b = x.groupby("region").net_sales_eur_bud.sum()
    jp_cal = x[x.store_id.isin(["TYO01", "TYO02", "OSA01"])].net_sales_lc.sum()
    kr_cal = x[x.store_id.isin(["SEL02", "BUS01"])].net_sales_lc.sum()
    lon01_gbp = x[x.store_id == "LON01"].net_sales_lc.sum()
    am_cal = (x[x.region == "AMERICAS"].net_sales_lc / x[x.region == "AMERICAS"].currency.map({"USD": 1, "CAD": 1.37})).sum()
    dd = daily()
    y = dd[(dd.date >= M0) & (dd.date <= M1) & (dd.region == "APAC")]
    apac_ret_share = y.returns_lc.sum() / y.sales_before_returns_lc.sum() * 100

    def yoy(st, a, b):
        c = k[k.store_id.isin(st) & (k.date >= a) & (k.date <= b)].net_sales_lc.sum()
        l_ = k[k.store_id.isin(st) & (k.date >= ly(a)) & (k.date <= ly(b))].net_sales_lc.sum()
        return (c / l_ - 1) * 100
    exp6 = ["NYC01", "NYC02", "BHS01", "MIA01", "LON01", "LON02"]
    ctl = ["TOR01", "MIL01", "PAR01", "PAR02", "MUN01", "MAD01", "AMS01", "ZRH01", "GVA01", "BER01", "CPH01", "MIL02", "DXB01",
           "CAN01", "VEN01"]
    e_full, c_full = yoy(exp6, D(2026, 9, 15), D(2026, 10, 21)), yoy(ctl, D(2026, 9, 15), D(2026, 10, 21))
    lon_wo_event = yoy(["LON01"], D(2026, 9, 15), D(2026, 10, 7))

    fx9 = FX_MONTHLY["2026-09"]
    w = fl
    md = []
    A = md.append
    A("# Reports area - answer key (heterogeneous reports, definitions, contradictions)\n")
    A("Scope: everything under `generated/sources/reports/`. Generator: `generator/reports/` "
      "(`.venv/bin/python generator/reports/run_all.py`). All numbers below are recomputed by `build_notes.py` from the same data.\n")
    A("## 0. Reference truth used to judge the reports\n")
    A("- **Internal BI (`generated/sources/erp/kpi/store_daily_kpi.csv`, `sales/daily_store_sku`)** is the reference: "
      "net sales = gross - discounts - returns (returns booked on the processing day), **excluding VAT / consumption tax**, local currency. "
      "`net_sales_eur_bud` is at **budget rates** (`BUDGET_RATE`). Every report number is a transformation of these tables "
      "(plus POS lines, stock snapshots, shipments).")
    A("- Actual FX = monthly averages of `generated/sources/external/fx/ecb_reference` (TWD and AED crossed from `fxfeed_usd_base`). "
      f"Sep-2026 avg: USD {fx9['USD']}, GBP {fx9['GBP']}, CHF {fx9['CHF']}, JPY {fx9['JPY']}, KRW {fx9['KRW']}, CNY {fx9['CNY']}. "
      f"'Constant FX' = 2025 full-year average: USD {FX_AVG_2025['USD']}, JPY {FX_AVG_2025['JPY']}, KRW {FX_AVG_2025['KRW']}, CNY {FX_AVG_2025['CNY']}, SGD {FX_AVG_2025['SGD']}.")
    A("- 2025 receipts in BI are partly estimated (units/1.35) by the simulator's legacy POS, so **LY conversion/ATV/UPT are not reliable** "
      "(EMEA MBR shows conversion down in almost every store mostly because of this).")
    A(f"- Calendar September 2026 retail net sales: EMEA {eur(reg_m['EMEA'])} at Sep actual FX / {eur(reg_b['EMEA'])} at budget FX; "
      f"APAC {eur(reg_m['APAC'])} / {eur(reg_b['APAC'])}; Americas {eur(reg_m['AMERICAS'])} / {eur(reg_b['AMERICAS'])}.\n")

    A("## 1. Inventory\n")
    A("| File | Author (fictional) | Format / language | Period & calendar | Key definitions |")
    A("|---|---|---|---|---|")
    rows = [
        ("retail_controlling/weekly_flash/Flash_W36..W42_2026.xlsx (+ W40 v1 and v2_corrected)", "Retail Controlling HQ (M. Galli)", "XLSX, EN", "ISO weeks Mon-Sun", "net of returns, ex VAT, EUR at monthly avg FX of the month of the week's Thursday (October = MTD avg at issue date), LY at LY monthly FX, LFL at constant CY FX for stores trading >=5 days both weeks; vs budget at budget FX; SAP plant codes (1001=MIL01 ...)"),
        ("retail_controlling/weekly_flash/export_classifica_negozi_sett42.csv", "BI Italia export", "CSV `;`, decimal comma, latin-1, IT headers", "W42", "same as W42 flash; date dd.mm.yyyy"),
        ("emea/EMEA_MBR_Sep26_v3_FINAL.pdf", "EMEA Retail Excellence + F. Arrighi (EMEA Retail Director)", "PDF 10 p., EN", "calendar Sep 1-30", "EUR at BUDGET FX both years, net of returns, LFL = standalone DOS only (excl. MIL02, PAR02, LON02, BER01, COU01, CRT01, STM01), sell-through on VALUE"),
        ("apac/APAC_Monthly_Review_SEP2026_v1.1.pptx", "APAC Business Analytics HK", "PPTX 13 slides, EN + JA/KO/ZH quotes", "mixed (see 2.3)", "constant FX 2025 avg, sales GROSS of returns, Japan tax-incl from country file, Korea dept stores on dept-store month"),
        ("apac/japan/国内直営店_月次売上報告_2026年9月度_確定.xlsx", "日本支社 営業企画部 (小林)", "XLSX, JA", "9月度 = Sun 30/8 - Sat 3/10 (5 weeks)", "税込 x1.10 on all sales (also tax-free), net of returns, JPY, 前年比 as ratio (116.4% = +16.4%)"),
        ("apac/japan/【週次速報】国内店舗_2026年10月第3週(10.11-10.17).xlsx", "日本支社 営業企画部", "XLSX, JA", "week Sun 11/10 - Sat 17/10", "税込, 前年比 ratio, waiting-list counts approximate"),
        ("apac/korea/[주간] 백화점 매출 보고_10월 3주차(10.12~10.18).xlsx", "몽클레르 코리아 리테일팀 (정다은)", "XLSX, KO", "weeks Mon-Sun numbered by month of Thursday; MTD on dept-store month (26th-25th)", "VAT incl. x1.10, net of returns, 백만원 in summary / 천원 in detail; SEL01 shown 'for reference'"),
        ("apac/china/中国区9月经营月报_2026_v2.pptx", "中国区零售运营部", "PPTX 9 slides, ZH", "calendar Sep", "含税 x1.13 on stores, stores + 天猫 + 微信小程序, 售罄率 = sold/(sold+EOP stock) units"),
        ("americas/AMER_Retail_Monthly_FY26_P08_Sep.xlsx", "Moncler USA Retail Finance (J. Morales)", "XLSX merged multi-row headers, EN", "NRF 4-5-4: P08 = Sun 30/8 - Sat 3/10 (5 wks); P09 MTD 4/10-17/10", "USD, net of returns, CAD at plan rate 1.37 CAD/USD; Aspen LY stored as text; hidden 'chk' column"),
        ("merchandising/FW26_NewIn_SellThrough_wk42_final.xlsx", "Merchandising Planning (S. Bianchi)", "XLSX, EN", "cumulative since launch to Sun 18/10 (W40/W41/W42 snapshots)", "ST% = units SOLD (gross, returns not netted) / units RECEIVED"),
        ("marketing/HaldenRowe_Moncler_FW26_Campaign_Performance_US-UK_FINAL.pdf", "Halden & Rowe (media agency)", "PDF glossy 6 p., EN", "weeks 1-4 of flight 15/9-13/10", "'attributed uplift' = YoY exposed stores minus YoY 'unexposed' (ASP01, TOR01)"),
        ("market_research/Castellane_Luxury_Outerwear_Pulse_Q3-2026.pdf", "Castellane Advisory (syndicated)", "PDF 8 p., EN", "fieldwork 20/7-10/8, published 30/9", "market-level, not derived from internal data"),
        ("tax_free/Aurelia_TFS_merchant_extract_MONCLER_W36-W43_2026.xlsx + Aurelia_Merchant_Insights_Moncler_Sep-Oct2026.pdf", "Aurelia Tax Free (refund operator)", "XLSX + PDF, EN", "ISO weeks; W43 partial", "forms ISSUED (not validated), spend incl. VAT, EUR at monthly ECB avg; nationality = passport keyed at POS"),
        ("customer_care_quality/CCQ_Monthly_Report_2026-09_rev1.2.docx (+ .pdf export)", "QA & Customer Care (L. Moretti, C. Rinaldi)", "DOCX/PDF, IT+EN", "Sep + early warning to 11/10", "defect rate on same-period sales; ARNEB rate on receipts"),
        ("board/Q3_2026_Trading_Update_BoD_draft_v5.pptx", "Group Finance / IR prep", "PPTX 6 slides, EN", "calendar Q3 (Jul-Sep), Oct QTD 1-18/10", "organic = constant 2025 FX; rounded EUR m; digital/wholesale from consolidation"),
        ("digital/Digital_Weekly_Channel_Report_W42_2026.xlsx", "Digital Analytics (E. Conti)", "XLSX, EN", "ISO weeks on UTC days", "demand = gross ordered value incl. VAT; notify-me = requests (not unique customers)"),
    ]
    for r in rows:
        A("| " + " | ".join(r) + " |")
    A("")

    A("## 2. Report by report: what was done to the numbers, and what is wrong\n")
    A("### 2.1 Weekly flash (Retail Controlling)\n")
    A("| Week | Net sales EUR (current FX) | Δ% reported | Δ% LFL cFX | vs budget | non-LFL stores |")
    A("|---|---|---|---|---|---|")
    for wk in ["W36", "W37", "W38", "W39", "W40_v2", "W41", "W42"]:
        v = w[wk]
        A(f"| {wk} | {v['total_eur']:,} | {v['d_rep']:+.1f}% | {v['d_lfl']:+.1f}% | {v.get('d_bud', float('nan')):+.1f}% | {', '.join(v.get('non_lfl', [])) or '-'} |")
    A("")
    A(f"- **W40 v1 is wrong (genuine mistakes, corrected in v2)**: KRW rate {w['W40_fx_krw']['wrong']:,} used instead of "
      f"{w['W40_fx_krw']['correct']:,} (digits transposed) -> South Korea {w['W40_v1']['korea_eur']:,} EUR in v1 vs {w['W40_v2']['korea_eur']:,} in v2; "
      f"DXB01 (plant 1801) listed twice -> EMEA overstated by {w['W40_v2']['dxb_eur']:,} EUR. Totals: v1 {w['W40_v1']['total_eur']:,} vs v2 {w['W40_v2']['total_eur']:,}. "
      "Use v2. Note v2 still displays 'issued 06/10' on the cover while the change log says 07/10.")
    A("- W41 daily sheet: NYC02 06/10 low and 07/10 high because of the POS outage (receipts 14:10-17:40 posted with business date 07/10); "
      "weekly total is right, daily split is not. Not restated anywhere.")
    A("- W40/W41 MAD01 traffic = 0 for 01-07/10 (door counter broken) -> conversion shown 'n.m.'; the CSV ranking of W42 is fine but "
      "W41 conversion for MAD01 is not meaningful.")
    A("- CRT01 drops out of LFL from W40 (open Fri-Sun in Oct 2026, closed from 06/10 in 2025); COU01 out from W38. "
      "The October FX is the month-to-date average at issue date, so W40-W42 use slightly different October rates.")
    A("- Summing W36-W39 flashes does NOT give September: W36 starts 31/08 and W40 contains 28-30/09.\n")

    A("### 2.2 EMEA MBR September (PDF)\n")
    A(f"- Net sales {eur(em['net_eur_budfx'])} at **budget FX** ({em['rep_g']:+.1f}% vs LY, {em['vs_bud']:+.1f}% vs budget). "
      f"At actual Sep FX (flash convention) EMEA calendar September = {eur(reg_m['EMEA'])}. Differences come from GBP/CHF/DKK/AED: "
      f"e.g. LON01 = GBP {lon01_gbp:,.0f} -> {eur(em['lon01_net_budfx'], 3)} at 0.85 (budget) vs {eur(lon01_gbp / fx9['GBP'], 3)} at {fx9['GBP']} (Sep avg).")
    A(f"- **Mistake 1 (stale number)**: executive summary says LFL **{em['lfl_quoted_exec_summary']:+.1f}%**, the KPI table says **{em['lfl_true']:+.1f}%**. "
      "The text kept the v2 figure (ROM01 excluded from LFL); v3 reinstated ROM01 (see appendix version history). Correct (per the MBR's own definition): "
      f"{em['lfl_true']:+.1f}%.")
    A(f"- **Mistake 2**: country table 'TOTAL EMEA' = {em['country_total_shown']:,} EUR = sum of European countries only; Middle East (DXB01, "
      f"{em['dxb_net']:,} EUR) is listed but not summed. Correct total {em['net_eur_budfx']:,}.")
    A(f"- **Mistake 3 (overstatement in commentary)**: director writes 'Korean clients are now more than 10% of the sales in Saint-Honoré'. "
      f"POS nationality for PAR01 in September gives **{em['kr_share_par01_pos']:.1f}%**. What is true: Korean demand for black MAIRE was "
      "largely UNMET (sold out ~21-24/9, DC out until 16/10), so it does not show up in sales - see lost sales and store emails.")
    A(f"- ROM01: {em['rom_month_g']:+.1f}% in the month, visitors {em['rom_traffic_since']:+.1f}% vs LY since works began 14/09 (correct, consistent with 'footfall halved').")
    A("- Sell-through on VALUE (sales / (sales + EOP stock at full retail), EMEA, cut-off 30/09): " +
      ", ".join(f"{k_} {v:.0f}%" for k_, v in em["sellthrough_value"].items()) +
      ". Not comparable with Merchandising unit ST (see 2.8). AMBRINE value ST mixes black and brown; brown alone sells much faster.")
    A("- Conversion LY is inflated by estimated 2025 receipts (see section 0); do not conclude that conversion collapsed.\n")

    A("### 2.3 APAC Monthly Review September (PPTX)\n")
    A(f"Total shown {eur(ap['total_cy'])} ({ap['growth']:+.1f}% vs LY, {ap['vs_bud']:+.1f}% vs budget). Reference: APAC calendar September net sales = "
      f"{eur(ap['apac_true_net_sep_monthly_fx'])} at Sep actual FX, {eur(ap['apac_bi_eur_budget_rate'])} at budget FX. Reasons for the gap:")
    A(f"- **Japan** pasted from the Japan country file: tax-inclusive (x1.10) AND 5-week 9月度 30/8-3/10 (includes Golden Week 1-3/10). "
      f"Japan file = JPY {jp['month']['net_tax_total']:,} vs BI calendar Sep ex-tax JPY {jp_cal:,.0f} (x{jp['month']['net_tax_total'] / jp_cal:.3f}). "
      f"APAC Japan {ap['markets']['Japan']['cy']:,} EUR vs {ap['markets']['Japan']['true_net_sep_monthly_fx']:,} at flash definitions. "
      "Growth (116.4% ratio = +16.4%) is internally consistent because LY was taken on the same basis.")
    A(f"- **Korea**: SEL02+BUS01 on department-store month 26/8-25/9 (VAT removed), SEL01 calendar month gross of returns. Korea file dept Sep = "
      f"KRW {kr['dept_sep']['vat_krw']:,} incl. VAT (= {kr['dept_sep']['ex_vat_krw']:,} ex VAT) vs BI calendar Sep KRW {kr_cal:,.0f}.")
    A(f"- **Sales before returns** for all non-Japan markets (APAC returns are only ~{apac_ret_share:.1f}% of sales, small effect) and constant FX "
      "(2025 avg rates are stronger for JPY/KRW/CNY than Sep-2026 actual -> higher EUR). Budget is at budget rates -> 'vs budget' mixes two FX bases.")
    A(f"- **Mistake (genuine)**: South-East Asia (SIN01) left in SGD: shown {ap['sin_shown_sgd']:,} 'EUR k' while the constant-FX value is "
      f"{ap['sin_correct_eur_constfx']:,} EUR. Growth % for SEA is still right (both years in SGD). APAC total with the fix = {ap['total_if_sin_correct']:,}.")
    A(f"- POLARIS units 24-30/9: Mainland China {ap['polaris_units_24_30sep'].get('Mainland China')} vs all EMEA {ap['polaris_units_emea']} (consistent with "
      "strong China / weak Europe). Golden Week Mainland China stores 1-7/10 " + f"{ap['gw_cn_growth_lc']:+.1f}% (local currency, same dates LY).")
    A("- Korea slide quotes a Korean-language comment that Chuseok reduced domestic visits; the numbers show Korea still growing (flagship strongest). "
      "Sydney slide correctly states the southern-hemisphere seasonality problem of the statistical forecast.\n")

    A("### 2.4 Japan country files (JA)\n")
    A(f"- 9月度 (5 weeks) 税込 JPY {jp['month']['net_tax_total']:,}, 前年比 {jp['month']['ratio']}%, 予算比 {jp['month']['bud_ratio']}%. "
      f"Ex-tax equivalent JPY {jp['month']['net_ex_tax_total']:,}. Tax-free share of sales {jp['month']['tax_free_share']}% "
      "(still grossed up by 10%: the file treats tax-free as tax-inclusive sales refunded at the counter - an overstatement of ~3.8% of the total).")
    A(f"- Weekly 速報 10/11-10/17: 前年比 {jp['week_oct11_17']['ratio_total']}% (Ginza {jp['week_oct11_17']['ratio_by_store']['TYO01']}%) = pre-buying before "
      "the 1/11 price increase (announced 9/10) + cold from 12/10. Waiting-list counts for ILVARO pink "
      f"({jp['ilvaro_waiting_list']}) are approximations (≈60% of true unmet demand).")
    A("- Ratio convention: 前年比 116.4% means +16.4%; readers converting it as +116% are wrong.\n")

    A("### 2.5 Korea dept-store weekly (KO)\n")
    A(f"- Week 10/12-10/18: department stores {kr['week']['dept_growth']:+.1f}% vs LY (ILVARO frenzy, BIFF tail), Cheongdam flagship {kr['week']['sel01_growth']:+.1f}% "
      "(competitor pop-up from 15/10 hits outerwear; ILVARO stock arrived 13/10 after customs). Units: 백만원 in summary, 천원 in detail - mixing them is a 1,000x error.")
    A(f"- Waiting lists ILVARO 인디 핑크 ({kr['ilvaro_waiting']}) approximate (≈55% of unmet demand, duplicates possible).")
    A("- The '9월 마감' sheet is on dept-store month 26/8-25/9 - this is what APAC used.\n")

    A("### 2.6 China monthly (ZH)\n")
    A(f"- Stores 含税 RMB {cn['stores_tax']:,} = BI net ex-VAT RMB {cn['stores_ex_vat']:,} x 1.13; stores {cn['stores_growth']:+.1f}% vs LY.")
    A(f"- Online = Tmall (RMB {cn['tmall']['2026-09']:,}, from TP partner statement - **not available in any other source**, treat as unverifiable) "
      f"+ WeChat mini program (RMB {cn['wechat_sep']:,}, = CN 'WeChat Mini Program' rows in `systems/ecommerce/shopify_sales_by_variant_daily.csv`).")
    A(f"- **Perimeter trap**: online growth shown {cn['online_growth_shown']:+.1f}% compares Tmall+WeChat 2026 with Tmall-only 2025 (mini program 'launched Nov 2025'); "
      f"like-for-like Tmall growth is {cn['online_growth_like_for_like_tmall']:+.1f}%. Omnichannel total {cn['total_growth']:+.1f}% is inflated for the same reason.")
    A("- POLARIS 售罄率 is units sold / (sold + EOP stock) per store 24-30/9 - a third sell-through definition. 小红书 note counts are third-party, synthetic, not cross-checkable.")
    A(f"- Golden Week stores {cn['gw_store_growth']:+.1f}% (same as APAC deck, local currency).")
    A("- Overstatements: 'ILVARO 粉色 登记预订顾客超过百名' - true unmet demand in the 3 CN stores was ~36 units to 7/10 (~62 to 21/10); "
      "'核心尺码全部售罄' is right (SHA01 kept single pieces in sizes 3/4). The APAC deck's 'sold out in all Asian stores' is likewise true only for core sizes.\n")

    A("### 2.7 Americas monthly (P08, 4-5-4)\n")
    A(f"- P08 = 30/8-3/10 (5 weeks): USD {am['total_usd']:,} ({am['growth']:+.1f}% vs P08 LY, {am['vs_plan']:+.1f}% vs plan). Calendar September with the same "
      f"conventions = USD {am_cal:,.0f}. Flash/EMEA-style EUR figures will not tie (calendar + FX + CAD at plan rate 1.37 instead of market ~{fx9['CAD'] / fx9['USD']:.3f}).")
    A(f"- Aspen LY stored as text (sums in Excel will skip it). Hidden column 'chk' = sales minus plan. TOR01 CAD {am['tor01_cad']:,}.")
    A(f"- P09 MTD tab: NYC02 10/6 USD {am['nyc02_oct6']:,} vs 10/7 USD {am['nyc02_oct7']:,} (POS outage shift).")
    A("- Commentary: 'Agency reports strong attributed uplift; our read on comp stores is more modest' - the US team is right (see 2.9).\n")

    A("### 2.8 Merchandising FW26 sell-through\n")
    A("- ST% = gross units sold / units received (allocation + replenishments). Received is reconstructed as on hand + sold - restocked returns.")
    A(f"- ILVARO 510 Asian stores at W40: {me['ilvaro_510_asia_w40']}% (core sizes sold out; the remaining units are single pieces in fringe sizes 00/3/4); by W42 some stores show stock again "
      "(DC top-up 08/10, SEL01 customs release 13/10) so ST falls - this is NOT a demand drop.")
    A("- Store ST above 100% (e.g. " + ", ".join(f"{s} {v['st_w42']}%" for s, v in me["ilvaro_510_asia"].items() if v["st_w42"] > 100) +
      ") because returned units are restocked and resold (gross sold counts them twice).")
    A("- **Mistake (genuine)**: 'Region summary' ST% = unweighted average of store ST%, not sum(sold)/sum(received). Examples: " +
      "; ".join(f"{s} {r_}: shown {v[r_]['shown']}% vs weighted {v[r_]['weighted']}%" for s, v in me["region_summary"].items()
                for r_ in ["APAC", "TOTAL"] if s.startswith("POLARIS C")) + ". The 'Style x Region' sheet is weighted and correct.")
    A("- ARNEB unit ST inflated by size exchanges (exchange = return + new sale).\n")

    A("### 2.9 Agency campaign report (US/UK)\n")
    A(f"- Claim '+22% attributed sales uplift' = exposed YoY {ag['exposed_yoy']:+.1f}% minus 'unexposed' YoY {ag['control_yoy']:+.1f}% over 15/9-13/10 = {ag['uplift']:+.1f} pp. "
      "Problems: (1) control = Aspen (off-season, small) + Toronto only; (2) MIA01 excluded ('operational disruption' = AC failure 3-5/9, before the flight) although Miami is in the OOH plan "
      "(the media table lists 'OOH (NYC, LA, MIA, LON)') - and the recommendation slide says to 'add Miami'; (3) cherry-picked window ends 13/10 after LON01's private client "
      f"evening (08/10, VIC event unrelated to media); LON01 YoY 15/9-7/10 = {lon_wo_event:+.1f}%; (4) NYC01 benefits from Golden Week/celebrity spill-over; (5) YoY difference is not a sales uplift.")
    A(f"- Footfall '+16%' built the same way ({ag['footfall_uplift']:+.1f} pp). Media KPIs (412M impressions, 4.8% ER, ROAS 5.6x) are agency-only, not verifiable.")
    A(f"- Correct reading: true incremental effect ≈ **+6%** (scenario). Over the whole flight 15/9-21/10 the six campaign stores are {e_full:+.1f}% YoY vs "
      f"{c_full:+.1f}% for comparable non-campaign EMEA/Americas stores, i.e. a single-digit gap. The Board deck repeats +22% as fact (wrong).\n")

    A("### 2.10 Market research (Castellane)\n")
    A("Generic, lagging (fieldwork closed 10/8). Claims contradicted by internal data / stores:")
    A(f"- 'Korean demand cooling (-8 pp)', 'Korean spend in Europe slowing': Korea stores {ap['markets']['Korea']['growth']:+.1f}% in September (APAC deck), dept stores {kr['week']['dept_growth']:+.0f}% week 12-18/10, Korean tourists "
      "chasing black MAIRE in Paris/Milan/London, ILVARO frenzy; even the tax-free operator says Korean spend in France +18% YoY.")
    A("- 'Cropped puffers losing share' vs ILVARO (cropped) best sell-through and sold out in Asia. 'Brown niche 4%' vs AMBRINE chocolate highest ST in EMEA and DC out of brown.")
    A("- 'Golden Week favours domestic/short-haul over Europe' vs Chinese tax-free spend at Moncler Europe x3 in W40-41 and strong MIL/PAR.")
    A("- 'Mild October in Central Europe' vs the cold snap 12-19/10 (first snow Munich 14/10). 'Capsule fatigue in China' vs POLARIS success in China.")
    A("- Right: Japan pull-forward before price increases; Double 11 pre-sales ~20/10 softening store traffic.\n")

    A("### 2.11 Tax-free operator (Aurelia)\n")
    A(f"- Forms ISSUED, spend incl. VAT, nationality as keyed. Only {tf['validated_share']}% of forms validated so far (recent weeks incomplete) - "
      "issued-based growth overstates realised tourist spend; spend incl. VAT >> our ex-VAT net sales (IT x1.22, FR x1.20 ...).")
    A(f"- Headlines: Korean spend at Moncler France+Italy W39-40 vs W36-37 {tf['kr_fr_it_w39_40_vs_w36_37']:+.1f}% (modest - because black MAIRE was out of stock), "
      f"Chinese spend at Moncler Europe W40-41 vs W38-39 {tf['cn_eu_w40_41_vs_w38_39']:+.0f}% (Golden Week). 'Korean travellers flocked' overstates the merchant data.")
    A(f"- **Data-quality issue**: in 'Forms by week' the W41 Italy rows are duplicated ({tf['w41_it_dup_rows']} rows, {tf['w41_it_dup_forms']} forms double-counted).")
    A("- UK not covered (no tourist VAT refund); market-context YoY table is operator-network-wide and synthetic.\n")

    A("### 2.12 Customer Care & Quality (DOCX/PDF)\n")
    A(f"- TIB 'tasso di difettosità' {q['tib_rate_shown']}% = {q['tib_def_win']} DEF returns 28/9-11/10 / {q['tib_sold_win']} TIB units sold in the SAME window. "
      f"Wrong denominator: the defect concerns units sold since 15/08 ({q['tib_sold_since_aug15']} units) -> {q['tib_rate_since']}% so far "
      f"(or {q['tib_def_win'] / q['tib_delivered'] * 100:.1f}% of {q['tib_delivered']} units delivered to stores since 15/08). Scenario truth: ~15-16% of affected units will come back.")
    A(f"- ARNEB exchange rate {q['arneb_rate_shown']}% on receipts (September) vs {q['arneb_rate_units']}% of units sold to 11/10 (scenario ~10%); {q['arneb_exchange_share']}% end as size exchange.")
    A(f"- Return rates by region (Sep, units, POS): {q['return_rate_by_region']}. Contact-centre volumes are synthetic (no other source).\n")

    A("### 2.13 Board Q3 trading update (PPTX)\n")
    A(f"- DOS Q3 reported EUR {bo['dos_q3_rep'] / 1e6:.1f} m ({bo['reported']:+.1f}%), constant FX EUR {bo['dos_q3_const'] / 1e6:.1f} m ({bo['organic']:+.1f}% organic). "
      f"Region chart in constant FX rounds to {', '.join(f'{k_} {round(v / 1e6)}' for k_, v in bo['regions_const'].items())} -> sums to "
      f"{sum(round(v / 1e6) for v in bo['regions_const'].values())} while the channel table shows {round(bo['dos_q3_rep'] / 1e6)} (reported FX) - not an error, two FX bases + rounding.")
    A("- **Mistake**: Group 'Organic +7%' in the channel table is not consistent with its components (DOS ~+6%, Digital +17% on 21m, Wholesale -4% on 39m) "
      "-> weighted ≈ +4%.")
    A(f"- October QTD (1-18/10) {bo['oct_qtd_organic']:+.1f}% organic. Quotes the agency '+22%' uplift as fact (wrong, see 2.9). Digital/wholesale figures are synthetic.\n")

    A("### 2.14 Digital weekly (XLSX)\n")
    A(f"- Demand = gross ordered value incl. VAT (W42 EUR {dg['w42_demand']:,}) vs net after returns (EUR {dg['w42_net']:,}); UTC days. "
      f"Notify-me ILVARO 510: {dg['notify']['J20931A00618-510']['requests']} requests = {dg['notify']['J20931A00618-510']['unique_emails']} unique e-mails; "
      f"MAIRE black {dg['notify']['J20931A00012-999']['requests']} / {dg['notify']['J20931A00012-999']['unique_emails']}.\n")

    A("## 3. Contradiction matrix (same topic, different numbers)\n")
    A("| Topic | Source A | Source B | Why different | Right reading |")
    A("|---|---|---|---|---|")
    mtx = [
        ("EMEA September sales", f"MBR {eur(em['net_eur_budfx'])}", f"Flash-convention {eur(reg_m['EMEA'])}", "budget vs actual FX", "both arithmetically right; for actual performance use actual FX, for budget comparison budget FX"),
        ("EMEA LFL September", f"MBR text {em['lfl_quoted_exec_summary']:+.1f}%", f"MBR table {em['lfl_true']:+.1f}%", "stale v2 text (ROM01 excluded)", f"{em['lfl_true']:+.1f}% (standalone DOS)"),
        ("EMEA total", f"MBR country table {em['country_total_shown']:,}", f"MBR KPI table {em['net_eur_budfx']:,}", "Middle East not summed", "KPI table"),
        ("Korea W40", f"Flash v1 EUR {w['W40_v1']['korea_eur']:,}", f"Flash v2 EUR {w['W40_v2']['korea_eur']:,}", "KRW typo", "v2"),
        ("Japan September", f"JP file JPY {jp['month']['net_tax_total']:,}", f"BI JPY {jp_cal:,.0f}", "tax incl. + 5-week 9月度", "BI for HQ; JP file internally consistent"),
        ("APAC September", f"APAC deck {eur(ap['total_cy'])}", f"BI {eur(ap['apac_true_net_sep_monthly_fx'])} (actual FX)", "const FX, gross of returns, JP tax/5wks, KR dept month, SGD error", "BI / flash"),
        ("Korea dept Sep", f"KR file KRW {kr['dept_sep']['vat_krw']:,}", f"BI calendar KRW {kr_cal:,.0f}", "VAT + 26-25 month", "BI calendar for HQ"),
        ("China online growth", f"China deck {cn['online_growth_shown']:+.1f}%", f"Tmall LFL {cn['online_growth_like_for_like_tmall']:+.1f}%", "new channel in CY only", "LFL"),
        ("Americas 'September'", f"P08 USD {am['total_usd']:,}", f"calendar Sep USD {am_cal:,.0f}", "4-5-4 (5 weeks incl. 1-3/10)", "depends on calendar"),
        ("FW26 sell-through", "EMEA value ST (AMBRINE " + f"{em['sellthrough_value'].get('AMBRINE', 0):.0f}%)", "Merch unit ST / China 售罄率", "value vs units vs (sold+stock)", "state definition; Merch weighted sheet for units"),
        ("Campaign effect", "Agency/Board +22%", "Americas finance 'more modest'; data single-digit", "control choice, perimeter, window, confounds", "≈ +6%"),
        ("TIB defect rate", f"CCQ {q['tib_rate_shown']}%", f"{q['tib_rate_since']}% of units sold since 15/08", "denominator", "~12% to date, ~15-16% expected"),
        ("Korean demand", "Castellane 'cooling -8pp'", "stores, KR file, tax-free +18% FR", "lagging survey (fieldwork Jul-Aug)", "Korean demand strong"),
        ("Korean share Saint-Honoré", "MBR commentary >10%", f"POS {em['kr_share_par01_pos']}%", "anecdote vs data; unmet demand invisible in sales", "~5% of sales, but large lost sales on black MAIRE"),
        ("Golden Week Europe", "Castellane: favours domestic", f"Aurelia: CN spend Moncler Europe {tf['cn_eu_w40_41_vs_w38_39']:+.0f}% vs prior 2 wks", "forecast vs actual", "GW strong in Milan/Paris"),
        ("October weather", "Castellane: mild October", "flash W42, board: cold snap 12/10", "seasonal forecast vs actual", "cold snap happened"),
    ]
    for r in mtx:
        A("| " + " | ".join(r) + " |")
    A("")
    A("## 4. Genuine mistakes planted (checklist)\n")
    for i, t in enumerate([
        "Flash W40 v1: KRW rate transposed + DXB01 duplicated (fixed in v2).",
        "EMEA MBR: exec-summary LFL stale (v2 number); country TOTAL excludes Middle East; 'Korean >10% of Saint-Honoré' unsupported.",
        "APAC deck: Singapore not converted from SGD.",
        "Merchandising: region ST% = unweighted mean of store ST%.",
        "China deck: online/omnichannel growth on non-comparable perimeter (WeChat mini program only in CY).",
        "Quality report: TIB defect rate on same-period sales (42%).",
        "Board deck: Group organic +7% inconsistent with components; repeats agency +22%.",
        "Tax-free XLSX: W41 Italy rows duplicated.",
        "Japan file: tax-free sales also grossed up by 10%.",
        "Americas: Aspen LY stored as text (Excel totals ignore it if recomputed with SUM).",
    ], 1):
        A(f"{i}. {t}")
    A("")
    A("## 5. Scenario signals and where they surface in reports\n")
    for t in [
        "Golden Week (CN tourists Europe/Japan, domestic China): flash W40 notes, EMEA outlook, APAC early-Oct slide, China GW slide, tax-free PDF, Japan 9月度 week 5.",
        "Black MAIRE unmet Korean demand (PAR01/PAR02/MIL01/LON02): flash W39/W42 notes, EMEA commentary + actions, Korea issues sheet, digital notify-me (KR/GB).",
        "LOGO CARDIGAN size M at MIL01 (from 8/10): NOT in reports (only emails/stock) - by design.",
        "ROM01 works: flash W38, EMEA (chart + commentary).",
        "Cold snap 12-19/10: flash W42, board outlook; contradicted by Castellane forecast.",
        "ILVARO powder pink (Yoon Ha-eun / LUMIERE): APAC early-Oct slide, Japan weekly, Korea issues, China social slide, merch ILVARO sheet, digital notify-me, CCQ contacts.",
        "POLARIS strong China / weak EU-US: APAC, China, EMEA, Americas commentary, merch POLARIS sheet, flash W39; contradicted by Castellane 'capsule fatigue'.",
        "TIB zipper defect: flash W40, EMEA, CCQ report, Japan/Korea comments, board risks.",
        "HKG01 typhoon 17-18/9: flash W38, APAC Greater China slide.",
        "Paris strike 13/10, Italy strike 16/10: flash W42 notes only.",
        "NYC02 POS outage 6/10: flash W41, Americas P09 tab.",
        "Japan price increase / warm weather: Japan files, APAC, board, Castellane (correct).",
        "SEL01 customs delay + competitor pop-up: flash W42, Korea issues, APAC early-Oct slide.",
        "US/UK campaign: agency report, Americas commentary, board; true effect ~+6%.",
        "Sydney seasonality / forecast: APAC SEA & Oceania slide and asks.",
        "AMBRINE brown: EMEA (value ST, commentary, actions), merch highlights, Castellane contradicts.",
        "ARNEB fit: CCQ, Americas commentary (Toronto), merch, APAC.",
        "MAD01 door counter, CPH01 staffing, MIA01 AC, BHS01 heat, UNGA, TIFF, LON01 VIC evening, SIN GP, BIFF: flash notes / Americas / Korea.",
    ]:
        A(f"- {t}")
    A("")
    A("## 6. Non-derivable (synthetic) content\n")
    A("Tmall figures (China deck), all agency media KPIs, Castellane market sizes/survey, Aurelia market-context table, contact-centre volumes (CCQ), "
      "Board digital & wholesale revenue, Xiaohongshu note counts, lab test '21 of 24' (CCQ). Waiting-list counts in JA/KO files are derived from hidden "
      "lost-sales truth x 0.55-0.6 (noisy proxy). Everything else is computable from internal data + external FX.")
    (GT / "answer_keys" / "reports_notes.md").write_text("\n".join(md), encoding="utf-8")


if __name__ == "__main__":
    main()
