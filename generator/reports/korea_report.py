"""Korea department-store weekly report (XLSX, Korean).

Definitions (한국법인 리테일팀):
- 매출 = 순매출 (net of returns), VAT 포함 (x1.10), 단위 백만원 in summary / 천원 in detail
- 주차 = Mon-Sun, numbered within the calendar month (10월 3주차 = 10/12-10/18)
- 백화점 월 (dept-store fiscal month) = 26th of previous month -> 25th (9월 = 8/26-9/25, 10월 = 9/26-10/25)
- 전년 동주 = same weekdays LY (-364 days)
"""
import datetime as dt

import numpy as np
import pandas as pd
import xlsxwriter

from common import D, GT, Facts, daily, kpi, outdir, pos

OUTD = outdir("apac", "korea")
facts = Facts("korea")
VAT = 1.10
DEPT = ["SEL02", "BUS01"]
ALL = ["SEL02", "BUS01", "SEL01"]
KNAME = {"SEL02": "현대 압구정본점", "BUS01": "신세계 센텀시티점", "SEL01": "청담 플래그십(직영)"}
STYLE_KO = {"ILVARO": "일바로", "MAIRE": "마이레", "MAYA": "마야", "BADY": "바디", "LOGO HOODIE": "로고 후디",
            "HERMINE": "에르민", "TIB": "티브", "AMBRINE": "앰브린", "ARNEB": "아르넵", "MONTCLA": "몽클라"}
COL_KO = {"999": "블랙", "510": "인디 핑크", "20D": "오프화이트", "742": "네이비", "034": "베이지", "90X": "그레이",
          "001": "화이트", "23R": "브라운", "82D": "올리브", "73A": "라이트블루", "41F": "레드"}


def per(store_ids, d0, d1):
    k = kpi()
    x = k[k.store_id.isin(store_ids) & (k.date >= d0) & (k.date <= d1)]
    g = x.groupby("store_id").agg(net=("net_sales_lc", "sum"), bud=("budget_lc", "sum"), rec=("receipts", "sum"),
                                  vis=("visitors_in", "sum"), units=("units", "sum"))
    g = g.reindex(store_ids).fillna(0)
    g["vat"] = g.net * VAT
    g["bud_vat"] = g.bud * VAT
    return g


def dept_month(y, m):
    """dept-store fiscal month m: 26th of m-1 to 25th of m"""
    pm = (dt.date(y, m, 1) - dt.timedelta(days=1))
    return dt.date(pm.year, pm.month, 26), dt.date(y, m, 25)


def month_table():
    a0, a1 = dept_month(2026, 9)
    b0, b1 = dept_month(2025, 9)
    return per(DEPT, a0, a1), per(DEPT, b0, b1), (a0, a1, b0, b1)


def weeks():
    out = []
    d0 = D(2026, 8, 31)
    while d0 <= D(2026, 10, 12):
        d1 = d0 + dt.timedelta(days=6)
        # week number within month of its Monday... Korean practice: week belongs to the month containing Thursday
        th = d0 + dt.timedelta(days=3)
        n = (th.day - 1) // 7 + 1
        out.append((f"{th.month}월 {n}주차", d0, d1))
        d0 += dt.timedelta(days=7)
    return out


def main():
    wb = xlsxwriter.Workbook(OUTD / "[주간] 백화점 매출 보고_10월 3주차(10.12~10.18).xlsx")
    wb.set_properties({"title": "백화점 주간 매출 보고", "author": "리테일팀 정다은", "company": "몽클레르 코리아"})
    F = lambda **kw: wb.add_format({"font_name": "맑은 고딕", "font_size": 9, **kw})
    title = F(bold=True, font_size=13)
    sub = F(font_color="#666666")
    hdr = F(bold=True, bg_color="#D9E1F2", border=1, align="center", valign="vcenter", text_wrap=True)
    hdr2 = F(bold=True, bg_color="#FCE4D6", border=1, align="center", valign="vcenter", text_wrap=True)
    txt, txtb = F(border=1), F(border=1, bold=True, bg_color="#F2F2F2")
    mil = F(border=1, num_format="#,##0.0")
    milb = F(border=1, num_format="#,##0.0", bold=True, bg_color="#F2F2F2")
    th_ = F(border=1, num_format="#,##0")
    pc = F(border=1, num_format='0.0%;[Red]-0.0%')
    pcb = F(border=1, num_format='0.0%;[Red]-0.0%', bold=True, bg_color="#F2F2F2")
    wrap = F(text_wrap=True, valign="top")
    note = F(font_size=8, font_color="#808080")

    w0, w1 = D(2026, 10, 12), D(2026, 10, 18)
    m0, m1 = dept_month(2026, 10)
    # ---- 주간요약
    ws = wb.add_worksheet("주간요약")
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 22)
    ws.set_column(1, 12, 11)
    ws.write(0, 0, "백화점 주간 매출 보고 - 10월 3주차 (10/12 월 ~ 10/18 일)", title)
    ws.write(1, 0, "단위: 백만원, VAT 포함, 순매출(반품 차감) / 월누계는 백화점 마감 기준 (9/26 ~ 10/18)", sub)
    ws.merge_range(3, 0, 4, 0, "매장", hdr)
    ws.merge_range(3, 1, 3, 5, "금주 (10/12~10/18)", hdr)
    ws.merge_range(3, 6, 3, 9, "월누계 (백화점 10월: 9/26~)", hdr2)
    for c, h in enumerate(["실적", "전년 동주", "신장률", "목표", "달성률"]):
        ws.write(4, 1 + c, h, hdr)
    for c, h in enumerate(["실적", "전년", "신장률", "달성률"]):
        ws.write(4, 6 + c, h, hdr2)
    cw, lw = per(ALL, w0, w1), per(ALL, w0 - dt.timedelta(days=364), w1 - dt.timedelta(days=364))
    cm, lm = per(ALL, m0, w1), per(ALL, m0 - dt.timedelta(days=364), w1 - dt.timedelta(days=364))
    r = 5

    def row(label, a, b, c, d, bold=False):
        nonlocal r
        fm, fp, ft = (milb, pcb, txtb) if bold else (mil, pc, txt)
        ws.write(r, 0, label, ft)
        vals = [a.vat / 1e6, b.vat / 1e6, a.vat / b.vat - 1, a.bud_vat / 1e6, a.vat / a.bud_vat,
                c.vat / 1e6, d.vat / 1e6, c.vat / d.vat - 1, c.vat / c.bud_vat]
        for i, v in enumerate(vals):
            ws.write(r, 1 + i, v, fp if i in (2, 4, 7, 8) else fm)
        r += 1

    for s in DEPT:
        row(KNAME[s], cw.loc[s], lw.loc[s], cm.loc[s], lm.loc[s])
    row("백화점 소계", cw.loc[DEPT].sum(), lw.loc[DEPT].sum(), cm.loc[DEPT].sum(), lm.loc[DEPT].sum(), True)
    row(KNAME["SEL01"], cw.loc["SEL01"], lw.loc["SEL01"], cm.loc["SEL01"], lm.loc["SEL01"])
    row("한국 합계", cw.sum(), lw.sum(), cm.sum(), lm.sum(), True)
    ws.write(r + 1, 0, "※ 청담 플래그십은 직영 매장으로 참고용 표기 (백화점 마감 기준 아님 - 동일 기간 합산)", note)
    ws.write(r + 2, 0, "※ 목표는 본사 예산(원화)에 VAT 10% 가산", note)
    facts["week"] = dict(dept_growth=round((cw.loc[DEPT].vat.sum() / lw.loc[DEPT].vat.sum() - 1) * 100, 1),
                         sel01_growth=round((cw.loc["SEL01"].vat / lw.loc["SEL01"].vat - 1) * 100, 1),
                         total_vat_mil=round(cw.vat.sum() / 1e6, 1))

    # ---- 주차별 추이
    ws = wb.add_worksheet("주차별 추이")
    ws.write(0, 0, "주차별 매출 추이 (백만원, VAT 포함)", title)
    heads = ["주차", "기간"] + [KNAME[s] for s in ALL] + ["합계", "전년 합계", "신장률"]
    for c, h in enumerate(heads):
        ws.write(2, c, h, hdr)
    ws.set_column(0, 1, 16)
    ws.set_column(2, 7, 14)
    wl = weeks()
    for i, (lab, a0, a1) in enumerate(wl):
        c_, l_ = per(ALL, a0, a1), per(ALL, a0 - dt.timedelta(days=364), a1 - dt.timedelta(days=364))
        ws.write(3 + i, 0, lab, txt)
        ws.write(3 + i, 1, f"{a0.month}/{a0.day}~{a1.month}/{a1.day}", txt)
        for j, s in enumerate(ALL):
            ws.write(3 + i, 2 + j, c_.vat[s] / 1e6, mil)
        ws.write(3 + i, 5, c_.vat.sum() / 1e6, milb)
        ws.write(3 + i, 6, l_.vat.sum() / 1e6, mil)
        ws.write(3 + i, 7, c_.vat.sum() / l_.vat.sum() - 1, pc)
    ch = wb.add_chart({"type": "column", "subtype": "stacked"})
    for j, s in enumerate(ALL):
        ch.add_series({"name": KNAME[s], "categories": ["주차별 추이", 3, 0, 2 + len(wl), 0],
                       "values": ["주차별 추이", 3, 2 + j, 2 + len(wl), 2 + j],
                       "fill": {"color": ["#203864", "#8FAADC", "#C55A11"][j]}})
    ch.set_title({"name": "주차별 매출 (백만원)", "name_font": {"size": 10}})
    ch.set_size({"width": 620, "height": 280})
    ws.insert_chart(4 + len(wl), 1, ch)

    # ---- 9월 마감 (dept fiscal)
    cy, ly, (a0, a1, b0, b1) = month_table()
    ws = wb.add_worksheet("9월 마감(백화점 기준)")
    ws.write(0, 0, f"9월 마감 실적 - 백화점 마감 기준 ({a0.month}/{a0.day} ~ {a1.month}/{a1.day})", title)
    ws.write(1, 0, "단위: 천원, VAT 포함", sub)
    for c, h in enumerate(["매장", "실적", "전년", "신장률", "목표", "달성률", "객수", "객단가(천원)"]):
        ws.write(3, c, h, hdr)
    ws.set_column(0, 0, 22)
    ws.set_column(1, 7, 13)
    for i, s in enumerate(DEPT):
        a, b = cy.loc[s], ly.loc[s]
        vals = [a.vat / 1e3, b.vat / 1e3, a.vat / b.vat - 1, a.bud_vat / 1e3, a.vat / a.bud_vat, a.rec, a.vat / a.rec / 1e3]
        ws.write(4 + i, 0, KNAME[s], txt)
        for c, v in enumerate(vals):
            ws.write(4 + i, 1 + c, v, pc if c in (2, 4) else th_)
    A, B = cy.sum(), ly.sum()
    ws.write(6, 0, "합계", txtb)
    for c, v in enumerate([A.vat / 1e3, B.vat / 1e3, A.vat / B.vat - 1, A.bud_vat / 1e3, A.vat / A.bud_vat, A.rec,
                           A.vat / A.rec / 1e3]):
        ws.write(6, 1 + c, v, pcb if c in (2, 4) else milb)
    facts["dept_sep"] = dict(period=f"{a0}..{a1}", vat_krw=round(A.vat), ex_vat_krw=round(A.net),
                             growth=round((A.vat / B.vat - 1) * 100, 1),
                             stores={s: round(cy.loc[s].vat) for s in DEPT})

    # ---- 일별
    ws = wb.add_worksheet("일별")
    k = kpi()
    ws.write(0, 0, "일별 매출 (천원, VAT 포함) 10/12~10/18", title)
    days = [w0 + dt.timedelta(days=i) for i in range(7)]
    yo = "월화수목금토일"
    for c, h in enumerate(["매장"] + [f"{d.month}/{d.day}({yo[i]})" for i, d in enumerate(days)] + ["합계"]):
        ws.write(2, c, h, hdr)
    ws.set_column(0, 0, 22)
    ws.set_column(1, 8, 11)
    for i, s in enumerate(ALL):
        ws.write(3 + i, 0, KNAME[s], txt)
        tot = 0
        for j, d in enumerate(days):
            v = k[(k.store_id == s) & (k.date == d)].net_sales_lc.sum() * VAT / 1e3
            tot += v
            ws.write(3 + i, 1 + j, v, th_)
        ws.write(3 + i, 8, tot, milb)

    # ---- 베스트
    dd = daily()
    x = dd[dd.store_id.isin(ALL) & (dd.date >= w0) & (dd.date <= w1)]
    g = x.groupby(["style_name", "color_code"]).agg(u=("units_sold", "sum"), v=("net_sales_lc", "sum")).sort_values(
        "u", ascending=False).head(12)
    ws = wb.add_worksheet("베스트 상품")
    ws.write(0, 0, "금주 베스트 상품 (3개점 합산)", title)
    for c, h in enumerate(["순위", "스타일", "컬러", "판매수량", "매출(천원, VAT포함)"]):
        ws.write(2, c, h, hdr)
    ws.set_column(1, 4, 16)
    for i, ((sn, cc), v) in enumerate(g.iterrows()):
        ws.write(3 + i, 0, i + 1, txt)
        ws.write(3 + i, 1, f"{sn} ({STYLE_KO.get(sn, '')})" if sn in STYLE_KO else sn, txt)
        ws.write(3 + i, 2, COL_KO.get(cc, cc), txt)
        ws.write(3 + i, 3, v.u, th_)
        ws.write(3 + i, 4, v.v * VAT / 1e3, th_)

    # ---- 이슈
    lost = pd.read_csv(GT / "demand" / "lost_sales_daily.csv")
    lw_ = lost[lost.store_id.isin(ALL) & lost.sku.str.startswith("J20931A00618-510") & (lost.date >= "2026-10-02") &
               (lost.date <= "2026-10-18")]
    wait = {s: int(round(lw_[lw_.store_id == s].lost.sum() * 0.55)) for s in ALL}
    facts["ilvaro_waiting"] = wait
    p = pos()
    q = p[p.store_id.isin(ALL) & (p.date >= w0) & (p.date <= w1) & (p.line_type == "SALE")]
    cn_share = q[q.customer_nationality == "CN"].net_amount.sum() / q.net_amount.sum() * 100
    ws = wb.add_worksheet("이슈 및 특이사항")
    ws.set_column(0, 0, 125)
    ws.write(0, 0, "이슈 및 특이사항 (10월 3주차)", title)
    text = [
        "1. 일바로(ILVARO) 인디 핑크: 10/2 이후 전 매장 품절 지속. LUMIERE 윤하은 착용 사진 이후 문의 폭주. 대기 고객 리스트 - "
        f"청담 {wait['SEL01']}명, 압구정 {wait['SEL02']}명, 센텀 {wait['BUS01']}명 (중복 포함 가능).",
        "2. 청담 일바로 리오더 물량: 인천세관 KC 인증서류 미비로 통관 지연, 10/8 입고 예정 -> 10/13 입고. 입고 당일 대부분 대기 고객에게 판매.",
        "3. 블랙/오프화이트 일바로도 사이즈 1, 2 결품. 본사 추가 배분 요청 중.",
        "4. 10/15부터 청담 플래그십 맞은편에 캐나다 아웃도어 브랜드 팝업 오픈 (대기줄, 사은품 증정). 금주 플래그십 아우터 매출 영향 있음.",
        "5. 부산국제영화제(10/1~10/10) 기간 센텀시티 유동인구 증가, 10월 1~2주차 실적 견인.",
        f"6. 중국 고객 매출 비중 금주 {cn_share:.0f}% (POS 국적 기준).",
        "7. 파리/밀라노 출장 고객으로부터 블랙 마이레(MAIRE) 현지 품절 문의 다수 - 국내 재고 문의 증가.",
        "8. 티브(TIB) 베스트 지퍼 불량 교환 건 발생, 본사 품질팀 공유 완료.",
    ]
    for i, t_ in enumerate(text):
        ws.write(2 + i, 0, t_, wrap)
        ws.set_row(2 + i, 28)
    ws.write(12, 0, "작성: 리테일팀 정다은 / 검토: 리테일팀장 오승훈 / 2026.10.19 - 대외비", note)
    wb.close()
    facts.save()


if __name__ == "__main__":
    main()
