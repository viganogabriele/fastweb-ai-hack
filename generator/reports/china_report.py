"""China monthly business report (PPTX, Simplified Chinese) - September 2026.

Author: 中国区零售运营部 (Shanghai). Definitions:
- 含税 (VAT 13% added to store net sales), RMB
- 全渠道 = 3 stores + online (天猫旗舰店 from TP partner report, not in our systems + 微信小程序 from systems/ecommerce)
- 门店 calendar month, net of returns
- 售罄率 (POLARIS) = units sold / (units sold + EOP stock units), store level
- online 同比 compares Tmall+WeChat 2026 vs Tmall only 2025 (mini program launched Nov 2025) -> inflated
"""
import datetime as dt

import numpy as np
import pandas as pd

from common import BUDGET_RATE, D, ROOT, Facts, daily, kpi, outdir, stock
from pptkit import XL_CHART_TYPE, Deck, PP_ALIGN

OUTD = outdir("apac", "china")
facts = Facts("china")
CN = ["SHA01", "BJS01", "CDU01"]
CNAME = {"SHA01": "上海恒隆广场店", "BJS01": "北京SKP店", "CDU01": "成都太古里店"}
VAT = 1.13
M0, M1 = D(2026, 9, 1), D(2026, 9, 30)
L0, L1 = D(2025, 9, 1), D(2025, 9, 30)
TH = dict(font="Microsoft YaHei", fg="1F1F1F", accent="9E1B32", muted="7F7F7F", light="F6F1F1")
# Tmall flagship (TP partner monthly statement, incl. VAT, net of refunds) - not available in any other source
TMALL = {"2026-09": 11_870_000, "2025-09": 10_940_000, "2026-10-01..07": 3_215_000, "2025-10-01..07": 2_480_000}


def wechat(d0, d1):
    e = pd.read_csv(ROOT / "generated" / "sources" / "systems" / "ecommerce" / "shopify_sales_by_variant_daily.csv")
    e = e[(e.billing_country == "CN") & (e.sales_channel == "WeChat Mini Program")]
    e = e[(e.day >= d0.isoformat()) & (e.day <= d1.isoformat())]
    return float(e.net_sales.sum())


def stores_tbl(d0, d1):
    k = kpi()
    x = k[k.store_id.isin(CN) & (k.date >= d0) & (k.date <= d1)]
    g = x.groupby("store_id").agg(net=("net_sales_lc", "sum"), bud=("budget_lc", "sum"), vis=("visitors_in", "sum"),
                                  rec=("receipts", "sum"), units=("units", "sum"))
    g["tax"] = g.net * VAT
    g["bud_tax"] = g.bud * VAT
    return g.reindex(CN)


def main():
    cy, ly = stores_tbl(M0, M1), stores_tbl(L0, L1)
    wc = wechat(M0, M1)
    online_cy = TMALL["2026-09"] + wc
    online_ly = TMALL["2025-09"]
    st_cy, st_ly = cy.tax.sum(), ly.tax.sum()
    tot_cy, tot_ly = st_cy + online_cy, st_ly + online_ly
    d = Deck(TH)

    def header(s, title, sub=None):
        d.text(s, 0.6, 0.3, 12, 0.7, title, size=26, bold=True, color=TH["accent"])
        if sub:
            d.text(s, 0.6, 0.95, 12, 0.4, sub, size=12, color=TH["muted"])
        d.text(s, 0.6, 7.0, 9, 0.3, "中国区零售运营部 | 内部资料 严禁外传", size=8, color=TH["muted"])
        d.text(s, 12.0, 7.0, 0.8, 0.3, str(d.n), size=8, color=TH["muted"], align=PP_ALIGN.RIGHT)

    s = d.slide(bg="FFFFFF")
    d.rect(s, 0, 0, 5.2, 7.5, TH["accent"])
    d.text(s, 0.6, 2.4, 4.4, 1.2, "MONCLER\n中国区", size=30, bold=True, color="FFFFFF")
    d.text(s, 5.8, 2.6, 7, 0.8, "2026年9月 经营月报", size=34, bold=True, color=TH["accent"])
    d.text(s, 5.8, 3.5, 7, 0.5, "全渠道（门店 + 天猫旗舰店 + 微信小程序）", size=16, color=TH["muted"])
    d.text(s, 5.8, 5.6, 7, 0.9, ["中国区零售运营部", "2026年10月12日  v2"], size=12, color=TH["muted"])

    s = d.slide()
    header(s, "核心摘要", "金额单位：人民币，含税")
    msgs = [
        f"9月全渠道销售 {tot_cy / 1e4:,.0f} 万元，同比 {(tot_cy / tot_ly - 1) * 100:+.1f}%；其中门店 {st_cy / 1e4:,.0f} 万元，同比 {(st_cy / st_ly - 1) * 100:+.1f}%，预算达成 {st_cy / cy.bud_tax.sum() * 100:.0f}%。",
        f"线上（天猫旗舰店+微信小程序）{online_cy / 1e4:,.0f} 万元，同比 {(online_cy / online_ly - 1) * 100:+.0f}%。",
        "Genius POLARIS 系列 9月24日上市，首周表现超预期，北京SKP 斗篷款（CAPE）黑色 XXL 已断码。",
        "国庆前两周本地客流稳定，成都太古里外地游客明显增加。",
        "10月初 小红书 上 ILVARO 粉色 话题爆发（LUMIERE 成员 尹夏恩 巴黎时装周同款），门店到货即售罄，大量顾客登记预订。",
        "风险：双11 预售（10月20日开始）期间门店客流可能分流，顾客询问门店是否与天猫同价。",
    ]
    d.text(s, 0.8, 1.5, 11.8, 5.2, msgs, size=15, bullets=True, spacing=10)

    s = d.slide()
    header(s, "全渠道业绩", "9月，含税，万元")
    rows = [["渠道", "2026年9月", "2025年9月", "同比", "预算", "达成率"]]
    for sid in CN:
        a, b = cy.loc[sid], ly.loc[sid]
        rows.append([CNAME[sid], f"{a.tax / 1e4:,.0f}", f"{b.tax / 1e4:,.0f}", f"{(a.tax / b.tax - 1) * 100:+.1f}%",
                     f"{a.bud_tax / 1e4:,.0f}", f"{a.tax / a.bud_tax * 100:.0f}%"])
    rows.append(["门店合计", f"{st_cy / 1e4:,.0f}", f"{st_ly / 1e4:,.0f}", f"{(st_cy / st_ly - 1) * 100:+.1f}%",
                 f"{cy.bud_tax.sum() / 1e4:,.0f}", f"{st_cy / cy.bud_tax.sum() * 100:.0f}%"])
    rows.append(["天猫旗舰店", f"{TMALL['2026-09'] / 1e4:,.0f}", f"{TMALL['2025-09'] / 1e4:,.0f}",
                 f"{(TMALL['2026-09'] / TMALL['2025-09'] - 1) * 100:+.1f}%", "-", "-"])
    rows.append(["微信小程序", f"{wc / 1e4:,.0f}", "-", "新渠道", "-", "-"])
    rows.append(["线上合计", f"{online_cy / 1e4:,.0f}", f"{online_ly / 1e4:,.0f}", f"{(online_cy / online_ly - 1) * 100:+.1f}%", "-", "-"])
    rows.append(["全渠道合计", f"{tot_cy / 1e4:,.0f}", f"{tot_ly / 1e4:,.0f}", f"{(tot_cy / tot_ly - 1) * 100:+.1f}%", "-", "-"])
    d.table(s, 0.6, 1.5, 8.2, rows, col_w=[2.2, 1.3, 1.3, 1.1, 1.2, 1.1], size=12, zebra=TH["light"], row_h=0.42, bold_last=True)
    d.text(s, 9.1, 1.5, 3.8, 4.8, ["门店数据来源：BI 系统净销售（扣除退货）× 1.13 增值税。",
                                   "天猫数据来源：TP 服务商月结单（含税，扣除退款）。",
                                   "微信小程序于2025年11月上线，无去年同期，线上同比按天猫去年同期计算。",
                                   "预算仅含门店。"], size=11, color=TH["muted"], bullets=True, spacing=6)

    s = d.slide()
    header(s, "门店业绩与客流", "9月")
    d.chart(s, 0.6, 1.4, 6.3, 5.0, XL_CHART_TYPE.COLUMN_CLUSTERED, [CNAME[x] for x in CN],
            [("2026年9月", [round(cy.loc[x].tax / 1e4) for x in CN]), ("2025年9月", [round(ly.loc[x].tax / 1e4) for x in CN])],
            colors=[TH["accent"], "C9B8B8"], title="门店销售（万元，含税）", labels=True)
    rows = [["门店", "客流", "同比", "转化率", "客单价(元)"]]
    for sid in CN:
        a, b = cy.loc[sid], ly.loc[sid]
        rows.append([CNAME[sid], f"{a.vis:,.0f}", f"{(a.vis / b.vis - 1) * 100:+.1f}%", f"{a.rec / a.vis * 100:.1f}%",
                     f"{a.tax / a.rec:,.0f}"])
    d.table(s, 7.2, 1.6, 5.6, rows, col_w=[1.8, 0.9, 0.9, 0.9, 1.1], size=11, zebra=TH["light"], row_h=0.42)
    d.text(s, 7.2, 3.6, 5.6, 2.5, ["成都太古里客流增长主要来自外地游客（川渝周边及西北）。",
                                   "北京SKP 转化率较高，VIC 预约到店增加。"], size=12, bullets=True, spacing=6)

    # POLARIS
    dd = daily()
    pol = dd[dd.store_id.isin(CN) & dd.style_name.str.startswith("POLARIS") & (dd.date >= D(2026, 9, 24)) & (dd.date <= M1)]
    sold = pol.groupby(["style_name", "store_id"]).units_sold.sum()
    stk = stock(M1)
    stk = stk[stk.store_id.isin(CN) & stk.style_name.str.startswith("POLARIS")].groupby(["style_name", "store_id"]).on_hand.sum()
    s = d.slide()
    header(s, "Genius POLARIS 上市表现", "9月24日-30日，售罄率 = 销售件数 /（销售件数 + 期末库存件数）")
    rows = [["款式", "门店", "销售件数", "期末库存", "售罄率"]]
    st_out = {}
    for sty in ["POLARIS CAPE", "POLARIS OVERSIZED", "POLARIS BALACLAVA"]:
        for sid in CN:
            u = int(sold.get((sty, sid), 0))
            o = int(stk.get((sty, sid), 0))
            str_ = u / (u + o) * 100 if u + o else 0
            st_out[f"{sty}|{sid}"] = round(str_, 1)
            rows.append([sty.title(), CNAME[sid], u, o, f"{str_:.0f}%"])
    d.table(s, 0.6, 1.5, 7.6, rows, col_w=[2.2, 2.0, 1.1, 1.1, 1.2], size=11, zebra=TH["light"], row_h=0.38)
    d.text(s, 8.6, 1.6, 4.3, 5.0, ["北京SKP 斗篷款（CAPE）黑色 XXL 首周断码，上海 M 码库存充足。",
                                   "顾客反馈：廓形好看，价格可以接受，多为连带购买。",
                                   "建议：申请从欧洲调拨 POLARIS 库存（欧洲销售较弱）。"], size=13, bullets=True, spacing=8)

    # Social
    s = d.slide()
    header(s, "社交媒体热度：小红书 / 抖音", "10月1日-11日，第三方舆情监测（品牌相关笔记）")
    days = [D(2026, 10, 1) + dt.timedelta(days=i) for i in range(11)]
    base = np.array([120, 2850, 4620, 3980, 3010, 2380, 1890, 1700, 1490, 1260, 1105])
    d.chart(s, 0.6, 1.4, 7.4, 5.0, XL_CHART_TYPE.LINE_MARKERS, [f"10/{x.day}" for x in days],
            [("ILVARO 粉色 相关笔记数（小红书）", [int(v) for v in base]),
             ("POLARIS 相关笔记数", [int(v) for v in np.array([310, 290, 340, 300, 280, 260, 240, 230, 220, 210, 190])])],
            colors=[TH["accent"], "7F7F7F"], title="每日新增笔记数")
    d.text(s, 8.3, 1.5, 4.6, 5.0, [
        "10月1日 LUMIERE 成员 尹夏恩（Yoon Ha-eun）在巴黎时装周场外穿着 ILVARO 粉色，10月2日起小红书相关笔记激增，“同款”搜索量排名第一。",
        "三家门店 ILVARO 粉色 10月2-3日核心尺码全部售罄，10月8日补货当天售完。",
        "黑色、米白色 ILVARO 询问量同步上升。",
        "POLARIS 讨论热度平稳，以穿搭分享为主。",
        "数据说明：第三方监测平台口径，含转发，未去重。"], size=12, bullets=True, spacing=6)

    # Golden week
    k = kpi()
    gw = k[k.store_id.isin(CN) & (k.date >= D(2026, 10, 1)) & (k.date <= D(2026, 10, 7))]
    gwl = k[k.store_id.isin(CN) & (k.date >= D(2025, 10, 1)) & (k.date <= D(2025, 10, 7))]
    gw_st, gw_stl = gw.net_sales_lc.sum() * VAT, gwl.net_sales_lc.sum() * VAT
    gw_on = TMALL["2026-10-01..07"] + wechat(D(2026, 10, 1), D(2026, 10, 7))
    s = d.slide()
    header(s, "国庆黄金周快报（10月1日-7日）", "含税，万元，同比为去年同日期")
    rows = [["渠道", "2026", "2025", "同比"],
            ["门店", f"{gw_st / 1e4:,.0f}", f"{gw_stl / 1e4:,.0f}", f"{(gw_st / gw_stl - 1) * 100:+.1f}%"],
            ["线上", f"{gw_on / 1e4:,.0f}", f"{TMALL['2025-10-01..07'] / 1e4:,.0f}", f"{(gw_on / TMALL['2025-10-01..07'] - 1) * 100:+.1f}%"],
            ["合计", f"{(gw_st + gw_on) / 1e4:,.0f}", f"{(gw_stl + TMALL['2025-10-01..07']) / 1e4:,.0f}",
             f"{((gw_st + gw_on) / (gw_stl + TMALL['2025-10-01..07']) - 1) * 100:+.1f}%"]]
    d.table(s, 0.6, 1.6, 6.0, rows, col_w=[1.8, 1.4, 1.4, 1.4], size=13, zebra=TH["light"], row_h=0.5, bold_last=True)
    d.text(s, 7.0, 1.6, 5.8, 4.8, ["外地游客占比提升，成都表现最好。", "客流增幅高于销售增幅，较多浏览型客户。",
                                   "ILVARO 粉色无货，登记预订顾客超过百名（三店合计）。"], size=14, bullets=True, spacing=8)

    s = d.slide()
    header(s, "10月展望与需求")
    d.text(s, 0.8, 1.5, 11.8, 5.2, [
        "双11 预售 10月20日开始：预计门店客流下降 10-15%，需总部明确门店是否价格保护/同价政策。",
        "ILVARO 粉色：申请紧急追单，优先分配中国区；目前登记顾客名单持续增加。",
        "POLARIS：申请从欧洲/美国调拨库存。",
        "TIB 马甲 拉链质量问题：北京SKP 已有退货，等待总部质检结论。",
        "天气：北方 10月下旬降温，羽绒服进入旺季。"], size=16, bullets=True, spacing=12)

    d.save(OUTD / "中国区9月经营月报_2026_v2.pptx")
    facts.update(dict(stores_tax=round(st_cy), stores_ex_vat=round(cy.net.sum()), stores_growth=round((st_cy / st_ly - 1) * 100, 1),
                      tmall=TMALL, wechat_sep=round(wc), online_cy=round(online_cy), online_growth_shown=round((online_cy / online_ly - 1) * 100, 1),
                      online_growth_like_for_like_tmall=round((TMALL["2026-09"] / TMALL["2025-09"] - 1) * 100, 1),
                      total_cy=round(tot_cy), total_growth=round((tot_cy / tot_ly - 1) * 100, 1),
                      polaris_sellthrough_units=st_out, gw_store_growth=round((gw_st / gw_stl - 1) * 100, 1)))
    facts.save()


if __name__ == "__main__":
    main()
