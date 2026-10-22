"""Japan country reports (XLSX, Japanese).

Definitions (日本支社 営業企画部):
- 純売上 = 売上 - 値引 - 返品, 税込 (consumption tax 10% added to ALL sales, incl. tax-free which are refunded at counter)
- 9月度 = week-based month Sun 2026-08-30 -> Sat 2026-10-03 (5 weeks); LY = Sun 2025-08-31 -> Sat 2025-10-04
- weeks Sun-Sat; 前年比 expressed as RATIO (e.g. 108.3% = +8.3%)
"""
import datetime as dt

import numpy as np
import pandas as pd
import xlsxwriter

from common import D, Facts, daily, kpi, outdir, pos

OUTD = outdir("apac", "japan")
facts = Facts("japan")
JP = ["TYO01", "TYO02", "OSA01"]
JNAME = {"TYO01": "銀座店", "TYO02": "表参道店", "OSA01": "心斎橋店"}
TAX = 1.10
M0, M1 = D(2026, 8, 30), D(2026, 10, 3)
L0, L1 = D(2025, 8, 31), D(2025, 10, 4)
CAT_JA = {"Outerwear": "アウター", "Knitwear": "ニット", "Jersey": "カットソー・スウェット", "Footwear": "シューズ",
          "Accessories": "アクセサリー", "Bottoms": "ボトムス"}
NAT_JA = {"JP": "日本", "CN": "中国", "TW": "台湾", "KR": "韓国", "HK": "香港", "US": "米国", "TH": "タイ", "OTHER": "その他"}


def period(store_ids, d0, d1):
    k = kpi()
    x = k[k.store_id.isin(store_ids) & (k.date >= d0) & (k.date <= d1)]
    g = x.groupby("store_id").agg(net=("net_sales_lc", "sum"), bud=("budget_lc", "sum"), rec=("receipts", "sum"),
                                  vis=("visitors_in", "sum"), units=("units", "sum"), ret=("returns_units", "sum"))
    g["net_tax"] = (g.net * TAX).round(0)
    g["bud_tax"] = (g.bud * TAX).round(0)
    return g


def month_table():
    """9月度 table used also by the APAC deck"""
    cy, ly = period(JP, M0, M1), period(JP, L0, L1)
    return cy, ly


def sunday_weeks(d0, n):
    return [(d0 + dt.timedelta(days=7 * i), d0 + dt.timedelta(days=7 * i + 6)) for i in range(n)]


def fmts(wb):
    F = lambda **kw: wb.add_format({"font_name": "Meiryo UI", "font_size": 9, **kw})
    return dict(
        title=F(bold=True, font_size=13), sub=F(font_color="#666666"),
        hdr=F(bold=True, bg_color="#DDEBF7", border=1, align="center", valign="vcenter", text_wrap=True),
        txt=F(border=1), txtb=F(border=1, bold=True, bg_color="#FFF2CC"),
        yen=F(border=1, num_format="#,##0"), yenb=F(border=1, num_format="#,##0", bold=True, bg_color="#FFF2CC"),
        ratio=F(border=1, num_format="0.0%"), ratiob=F(border=1, num_format="0.0%", bold=True, bg_color="#FFF2CC"),
        ratio_red=F(border=1, num_format="0.0%", font_color="#C00000"),
        wrap=F(text_wrap=True, valign="top"), note=F(font_size=8, font_color="#7F7F7F"))


def write_month():
    cy, ly = month_table()
    wb = xlsxwriter.Workbook(OUTD / "国内直営店_月次売上報告_2026年9月度_確定.xlsx")
    wb.set_properties({"title": "2026年9月度 月次売上報告", "author": "日本支社 営業企画部 小林", "company": "モンクレール ジャパン"})
    f = fmts(wb)
    # ---- summary
    ws = wb.add_worksheet("月次サマリー")
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 14)
    ws.set_column(1, 12, 13)
    ws.write(0, 0, "2026年9月度　直営店 売上報告（確定）", f["title"])
    ws.write(1, 0, "対象期間：2026/8/30(日)〜2026/10/3(土)　5週　／　前年：2025/8/31(日)〜2025/10/4(土)", f["sub"])
    ws.write(2, 0, "単位：円（税込）　純売上＝売上−値引−返品", f["sub"])
    heads = ["店舗", "純売上(税込)", "前年実績(税込)", "前年比", "予算(税込)", "予算比", "客数", "客単価(税込)",
             "入店客数", "購買率", "点数", "返品点数"]
    for c, h in enumerate(heads):
        ws.write(4, c, h, f["hdr"])
    ws.set_row(4, 30)
    r = 5
    for s in JP:
        a, b = cy.loc[s], ly.loc[s]
        vals = [a.net_tax, b.net_tax, a.net_tax / b.net_tax, a.bud_tax, a.net_tax / a.bud_tax, a.rec,
                a.net_tax / a.rec, a.vis, a.rec / a.vis, a.units, a.ret]
        ws.write(r, 0, JNAME[s], f["txt"])
        for c, (v, fm) in enumerate(zip(vals, ["yen", "yen", "ratio", "yen", "ratio", "yen", "yen", "yen", "ratio", "yen", "yen"])):
            ws.write(r, c + 1, v, f[fm] if not (fm == "ratio" and v < 1) else f["ratio_red"])
        r += 1
    A, B = cy.sum(), ly.sum()
    ws.write(r, 0, "合計", f["txtb"])
    vals = [A.net_tax, B.net_tax, A.net_tax / B.net_tax, A.bud_tax, A.net_tax / A.bud_tax, A.rec, A.net_tax / A.rec,
            A.vis, A.rec / A.vis, A.units, A.ret]
    for c, (v, fm) in enumerate(zip(vals, ["yenb", "yenb", "ratiob", "yenb", "ratiob", "yenb", "yenb", "yenb", "ratiob", "yenb", "yenb"])):
        ws.write(r, c + 1, v, f[fm])
    ws.write(r + 2, 0, "※免税売上も税込価格で計上（免税カウンターにて返金）。前年客数は旧POSからの推計値を含む。", f["note"])
    ws.write(r + 3, 0, "※社外秘", f["note"])
    facts["month"] = dict(period=f"{M0}..{M1}", net_tax_total=round(A.net_tax), ly_tax_total=round(B.net_tax),
                          ratio=round(A.net_tax / B.net_tax * 100, 1), bud_ratio=round(A.net_tax / A.bud_tax * 100, 1),
                          stores={s: round(cy.loc[s].net_tax) for s in JP}, net_ex_tax_total=round(A.net))
    # ---- weekly
    ws = wb.add_worksheet("週次推移")
    ws.write(0, 0, "週次推移（日〜土、税込、円）", f["title"])
    weeks = sunday_weeks(D(2026, 8, 30), 5)
    heads = ["週", "期間"] + [JNAME[s] for s in JP] + ["合計", "前年合計", "前年比"]
    for c, h in enumerate(heads):
        ws.write(2, c, h, f["hdr"])
    ws.set_column(0, 0, 6)
    ws.set_column(1, 1, 20)
    ws.set_column(2, 7, 13)
    for i, (a0, a1) in enumerate(weeks):
        c_ = period(JP, a0, a1)
        l_ = period(JP, a0 - dt.timedelta(days=364), a1 - dt.timedelta(days=364))
        ws.write(3 + i, 0, f"第{i + 1}週", f["txt"])
        ws.write(3 + i, 1, f"{a0.month}/{a0.day}(日)〜{a1.month}/{a1.day}(土)", f["txt"])
        for j, s in enumerate(JP):
            ws.write(3 + i, 2 + j, c_.net_tax.get(s, 0), f["yen"])
        ws.write(3 + i, 5, c_.net_tax.sum(), f["yenb"])
        ws.write(3 + i, 6, l_.net_tax.sum(), f["yen"])
        rr = c_.net_tax.sum() / l_.net_tax.sum()
        ws.write(3 + i, 7, rr, f["ratio"] if rr >= 1 else f["ratio_red"])
    ch = wb.add_chart({"type": "line"})
    ch.add_series({"name": "今年", "categories": ["週次推移", 3, 0, 7, 0], "values": ["週次推移", 3, 5, 7, 5],
                   "line": {"color": "#1F4E79", "width": 2.25}})
    ch.add_series({"name": "前年", "categories": ["週次推移", 3, 0, 7, 0], "values": ["週次推移", 3, 6, 7, 6],
                   "line": {"color": "#A6A6A6", "dash_type": "dash"}})
    ch.set_title({"name": "週次売上推移（税込）", "name_font": {"size": 10}})
    ch.set_size({"width": 560, "height": 260})
    ws.insert_chart(10, 1, ch)
    # ---- category
    dd = daily()
    x = dd[dd.store_id.isin(JP) & (dd.date >= M0) & (dd.date <= M1)]
    y = dd[dd.store_id.isin(JP) & (dd.date >= L0) & (dd.date <= L1)]
    gc = (x.groupby("category").net_sales_lc.sum() * TAX)
    gl = (y.groupby("category").net_sales_lc.sum() * TAX)
    ws = wb.add_worksheet("カテゴリー別")
    ws.write(0, 0, "カテゴリー別　9月度（税込、円）", f["title"])
    for c, h in enumerate(["カテゴリー", "純売上", "構成比", "前年", "前年比"]):
        ws.write(2, c, h, f["hdr"])
    ws.set_column(0, 0, 22)
    ws.set_column(1, 4, 14)
    for i, (c_, v) in enumerate(gc.sort_values(ascending=False).items()):
        ws.write(3 + i, 0, CAT_JA.get(c_, c_), f["txt"])
        ws.write(3 + i, 1, round(v), f["yen"])
        ws.write(3 + i, 2, v / gc.sum(), f["ratio"])
        ws.write(3 + i, 3, round(gl.get(c_, 0)), f["yen"])
        ws.write(3 + i, 4, v / gl.get(c_, np.nan) if gl.get(c_, 0) else "-", f["ratio"])
    # ---- top styles
    ws = wb.add_worksheet("品番別TOP20")
    g = x.groupby(["style_name", "color_name_en", "sku"]).agg(u=("units_sold", "sum"), r=("units_returned", "sum"),
                                                               v=("net_sales_lc", "sum")).sort_values("v", ascending=False).head(20)
    ws.write(0, 0, "品番別売上TOP20　9月度（3店舗計）", f["title"])
    for c, h in enumerate(["順位", "品番", "品名", "カラー", "販売点数", "返品点数", "純売上(税込)"]):
        ws.write(2, c, h, f["hdr"])
    ws.set_column(1, 1, 18)
    ws.set_column(2, 3, 18)
    ws.set_column(4, 6, 12)
    for i, ((sn, col, sku), v) in enumerate(g.iterrows()):
        ws.write(3 + i, 0, i + 1, f["txt"])
        ws.write(3 + i, 1, sku, f["txt"])
        ws.write(3 + i, 2, sn, f["txt"])
        ws.write(3 + i, 3, col, f["txt"])
        ws.write(3 + i, 4, v.u, f["yen"])
        ws.write(3 + i, 5, v.r, f["yen"])
        ws.write(3 + i, 6, round(v.v * TAX), f["yen"])
    # ---- inbound
    p = pos()
    q = p[p.store_id.isin(JP) & (p.date >= M0) & (p.date <= M1) & (p.line_type == "SALE")]
    nat = q.groupby(q.customer_nationality.where(q.customer_nationality.isin(list(NAT_JA)), "OTHER")).net_amount.sum()
    tf = q[q.tax_free == 1].net_amount.sum() / q.net_amount.sum()
    ws = wb.add_worksheet("インバウンド")
    ws.write(0, 0, "顧客国籍別構成比（POS登録ベース）・免税比率", f["title"])
    for c, h in enumerate(["国籍", "売上構成比"]):
        ws.write(2, c, h, f["hdr"])
    ws.set_column(0, 1, 14)
    for i, (n_, v) in enumerate(nat.sort_values(ascending=False).items()):
        ws.write(3 + i, 0, NAT_JA.get(n_, n_), f["txt"])
        ws.write(3 + i, 1, v / nat.sum(), f["ratio"])
    ws.write(3 + len(nat) + 1, 0, "免税売上比率", f["txtb"])
    ws.write(3 + len(nat) + 1, 1, tf, f["ratiob"])
    facts["month"]["tax_free_share"] = round(tf * 100, 1)
    facts["month"]["nat_share"] = {k_: round(v / nat.sum() * 100, 1) for k_, v in nat.items()}
    # ---- comments
    ws = wb.add_worksheet("所感")
    ws.set_column(0, 0, 120)
    ws.write(0, 0, "9月度　所感・トピックス", f["title"])
    text = [
        "【全体】9月度は前年比{:.1f}%、予算比{:.1f}%で着地。第5週（9/27〜10/3）は国慶節の中国人観光客が銀座・心斎橋で増加し、月末にかけて回復。".format(
            A.net_tax / B.net_tax * 100, A.net_tax / A.bud_tax * 100),
        "【気温】9月末〜10月初旬にかけて最高気温27〜29℃の日が続き、ダウンジャケットの動きが鈍い。ニット・カットソー・スニーカーは堅調。",
        "【新作】ILVARO（クロップド）は入荷数が少なく、ブラックは銀座で早期に欠品サイズあり。パウダーピンクは問い合わせ多数。",
        "【価格改定】11/1付の価格改定（平均+8%）について、10/9に顧客への告知予定。告知後の駆け込み需要を見込み、MAYA・MAIREの在庫確保をMDへ依頼済み。",
        "【品質】TIBベストのファスナー（スライダー）不具合による返品が9月末より発生。本社品質管理部へ報告済み。",
        "【POLARIS】Genius POLARISは中国のお客様中心に動きあり、日本人顧客の反応は限定的。",
        "※本資料の数値は税込。アジア太平洋本部向けレポート（ユーロ換算）とは定義が異なるためご注意ください。",
    ]
    for i, t_ in enumerate(text):
        ws.write(2 + i, 0, t_, f["wrap"])
        ws.set_row(2 + i, 30)
    ws.write(11, 0, "作成：営業企画部　小林　／　承認：リテール本部長　佐々木　（2026/10/6）", f["note"])
    wb.close()


def write_weekly():
    a0, a1 = D(2026, 10, 11), D(2026, 10, 17)
    wb = xlsxwriter.Workbook(OUTD / "【週次速報】国内店舗_2026年10月第3週(10.11-10.17).xlsx")
    wb.set_properties({"title": "週次速報 10月第3週", "author": "日本支社 営業企画部"})
    f = fmts(wb)
    ws = wb.add_worksheet("週次速報")
    ws.hide_gridlines(2)
    ws.write(0, 0, "週次速報　2026年10月第3週　10/11(日)〜10/17(土)", f["title"])
    ws.write(1, 0, "税込・円　前年同週：2025/10/12(日)〜10/18(土)", f["sub"])
    k = kpi()
    days = [a0 + dt.timedelta(days=i) for i in range(7)]
    wd = "日月火水木金土"
    heads = ["店舗"] + [f"{d.month}/{d.day}({wd[i]})" for i, d in enumerate(days)] + ["週計", "前年同週", "前年比", "予算比"]
    for c, h in enumerate(heads):
        ws.write(3, c, h, f["hdr"])
    ws.set_column(0, 0, 12)
    ws.set_column(1, 11, 12)
    tot = np.zeros(7)
    out = {}
    for i, s in enumerate(JP):
        ws.write(4 + i, 0, JNAME[s], f["txt"])
        for j, d in enumerate(days):
            v = k[(k.store_id == s) & (k.date == d)].net_sales_lc.sum() * TAX
            tot[j] += v
            ws.write(4 + i, 1 + j, round(v), f["yen"])
        c_ = period([s], a0, a1).loc[s]
        l_ = period([s], a0 - dt.timedelta(days=364), a1 - dt.timedelta(days=364)).loc[s]
        ws.write(4 + i, 8, c_.net_tax, f["yen"])
        ws.write(4 + i, 9, l_.net_tax, f["yen"])
        ws.write(4 + i, 10, c_.net_tax / l_.net_tax, f["ratio"])
        ws.write(4 + i, 11, c_.net_tax / c_.bud_tax, f["ratio"])
        out[s] = round(c_.net_tax / l_.net_tax * 100, 1)
    c_ = period(JP, a0, a1).sum()
    l_ = period(JP, a0 - dt.timedelta(days=364), a1 - dt.timedelta(days=364)).sum()
    ws.write(7, 0, "合計", f["txtb"])
    for j in range(7):
        ws.write(7, 1 + j, round(tot[j]), f["yenb"])
    ws.write(7, 8, c_.net_tax, f["yenb"])
    ws.write(7, 9, l_.net_tax, f["yenb"])
    ws.write(7, 10, c_.net_tax / l_.net_tax, f["ratiob"])
    ws.write(7, 11, c_.net_tax / c_.bud_tax, f["ratiob"])
    facts["week_oct11_17"] = dict(ratio_total=round(c_.net_tax / l_.net_tax * 100, 1), ratio_by_store=out)
    # top items in week
    dd = daily()
    x = dd[dd.store_id.isin(JP) & (dd.date >= a0) & (dd.date <= a1)]
    g = x.groupby(["style_name", "color_name_en"]).units_sold.sum().sort_values(ascending=False).head(10)
    ws.write(10, 0, "販売点数TOP10（3店舗計）", f["title"])
    for i, ((sn, col), u) in enumerate(g.items()):
        ws.write(11 + i, 0, i + 1, f["txt"])
        ws.write(11 + i, 1, f"{sn} {col}", f["txt"])
        ws.write(11 + i, 2, u, f["yen"])
    # ILVARO pink waiting list (approx from unmet demand)
    lost = pd.read_csv(__import__("common").GT / "demand" / "lost_sales_daily.csv")
    lost = lost[lost.store_id.isin(JP) & lost.sku.str.startswith("J20931A00618-510") &
                (lost.date >= "2026-10-02") & (lost.date <= "2026-10-17")]
    wl = {s: int(round(lost[lost.store_id == s].lost.sum() * 0.6)) for s in JP}
    facts["ilvaro_waiting_list"] = wl
    ws.write(23, 0, "所感", f["title"])
    text = [
        "・10/9の価格改定告知以降、MAYA・MAIRE・HERMINEを中心に駆け込み購入が本格化。銀座は前年比{:.0f}%。".format(out["TYO01"]),
        "・10/12以降気温が下がり、ようやくダウンが動き始めた。",
        "・ILVARO パウダーピンクは全店完売継続。10/8入荷分も即日完売。お取り置き・入荷待ちリスト：銀座{}名、表参道{}名、心斎橋{}名（概数）。".format(
            wl["TYO01"], wl["TYO02"], wl["OSA01"]),
        "・ブラック・オフホワイトのILVAROも問い合わせ増、サイズ1・2が欠品。",
        "・TIBのファスナー不良返品は継続（交換対応）。",
        "・価格改定前の在庫が不足する見込み。MAYAブラック サイズ3・4の追加配分を要請中。",
    ]
    for i, t_ in enumerate(text):
        ws.write(24 + i, 0, t_)
    ws.write(31, 0, "社外秘　速報値のため確定値と異なる場合があります", f["note"])
    wb.close()


def main():
    write_month()
    write_weekly()
    facts.save()


if __name__ == "__main__":
    main()
