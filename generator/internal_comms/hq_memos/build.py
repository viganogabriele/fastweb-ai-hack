"""HQ memos to stores. All prose below is hand-written; code only lays it out.
Run: .venv/bin/python generator/internal_comms/hq_memos/build.py
"""
import io
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import OUT, person, make_eml, write_eml, check_texts  # noqa: E402

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor, Cm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak)

D = OUT / "hq_memos"
D.mkdir(parents=True, exist_ok=True)
TEXTS = {}

# ---------------------------------------------------------------------------------------------
# 1. FW26 launch brief (PDF, reportlab)
# ---------------------------------------------------------------------------------------------
LB_INTRO = (
    "This brief covers the four FW26 newness drivers landing in boutiques from <b>Thursday 3 September</b> "
    "(IRIDIA, AMALIA, ARTEM) and the Couture <b>ASTRA</b> capsule launching on <b>Thursday 24 September</b> in "
    "selected doors. Please share with the full team at the morning briefing and keep a printed copy in the "
    "back office. Sizing guidance comes from the fit sessions in Milan (July) and may be updated after the first "
    "weeks of sell-through. Questions to your Area Manager or directly to merchandising."
)
LB_STYLES = [
    ["Style", "Code", "Colours", "Sizes", "Retail EUR", "Fit guidance"],
    ["IRIDIA", "J20931A00618", "999 black / 20D off-white / 510 powder pink", "00-4", "1.590", "True to size, boxy"],
    ["AMALIA", "J20931A00622", "999 black / 23R chocolate brown", "00-4", "2.290", "True to size, belted"],
    ["ARTEM", "J10911A00577", "999 black / 742 navy", "1-7", "2.190", "Regular fit"],
    ["ASTRA CAPE", "G20921A00901", "999 black / 001 white", "XS-XXL", "2.900", "True to size (oversized by design)"],
    ["ASTRA OVERSIZED", "G20921A00902", "999 black / 73A light blue", "XS-XXL", "2.400", "True to size"],
    ["ASTRA BALACLAVA", "G20921A00903", "999 black / 001 white", "TU", "450", "One size"],
]
LB_SECTIONS = [
    ("IRIDIA – cropped down jacket",
     "The new cropped silhouette of the season: boxy volume, matte nylon, funnel neck, no hood. Aimed at a younger "
     "client who already owns a Aurea or a Aria and wants something more fashion. "
     "<b>Core colour is black</b>, off-white as second option for EU/US resort clients. "
     "Powder pink (510) is a <b>limited regional colour</b> with a small buy, mainly for Asia windows and social content; "
     "we expect it to be a secondary option and do not recommend building client outreach around it. "
     "<i>Nota prodotto: piumino cropped boxy, nylon opaco, collo a imbuto, imbottitura 90/10.</i>",
     ["Matte nylon: no laqué shine, easier to style with tailoring",
      "Funnel neck replaces the hood, pairs with the Vlogo Beanie",
      "Cropped length works with high-waist trousers and long knits",
      "Analog for planning: Aria (short down jacket)"]),
    ("AMALIA – long belted down coat",
     "The coat for clients who do not want to look like they wear a down jacket. Long, belted, tailored shoulder. "
     "Black is the volume colour and carries most of the allocation. Chocolate brown is on trend this season but the buy "
     "is limited, so present it as a statement piece and steer to black when sizes are missing. "
     "<i>Nota prodotto: cappotto lungo in piumino con cintura, colletto a revers, tasche a filetto.</i>",
     ["Belt can be removed: two looks in one coat",
      "Brown pairs with the Cashmere Turtleneck in chocolate (same dye lot)",
      "Long length: check sleeve length on petite clients, alterations not possible on down"]),
    ("ARTEM – long parka, men",
     "Technical long parka with faux fur trim on the hood and two-way zip. "
     "Fit is <b>regular</b>: offer the client his usual Valentino size. "
     "Good substitute for clients asking for longer Monteluce or for the Atelier look in the city. "
     "<i>Nota prodotto: parka lungo, cappuccio con bordo in pelliccia sintetica staccabile, zip a doppio cursore.</i>",
     ["Detachable faux fur trim (no animal fur, important for some markets)",
      "Two-way zip: comfortable when sitting / driving",
      "Inner storm cuffs, water-repellent shell"]),
    ("Valentino Couture ASTRA – capsule (launch 24/09)",
     "Polar-inspired capsule: an oversized down cape, an oversized jacket and a knit balaclava. "
     "Limited quantities, selected doors only (see list). Sizing is <b>true to size</b>: the volume is part of the design, "
     "do not suggest sizing down. Launch moment on social on 24/09 at 10:00 CET; no early sales, no holds before launch day. "
     "<i>Nota prodotto: mantella in piumino oversize, giacca oversize, passamontagna in maglia a coste.</i>",
     ["Strong storytelling: make sure the team has watched the capsule video before 24/09",
      "Price positioning: statement / collector piece, do not justify the price, explain the design",
      "Balaclava is the entry point for younger clients and gifting"]),
]
LB_DOORS = ("ASTRA doors: MIL01, ROM01, VEN01, PAR01, CAN01, GVA01, LON01, LON02, MUN01, STM01, MAD01, AMS01, CPH01, "
            "NYC01, NYC02, MIA01, BHS01, TOR01, TYO01, OSA01, SEL01, SEL02, SHA01, BJS01, CDU01, HKG01, TPE01, SIN01, SYD01.")
LB_FAQ = [
    ("Can we reserve IRIDIA powder pink for clients?", "Yes, standard 48h hold rule. Quantities are small, do not open waitlists."),
    ("A client wants AMALIA brown in a size we don't have", "Check the stock lookup for other doors in your country, then propose black. "
     "No re-order planned on brown in season."),
    ("Will there be a second ASTRA drop?", "Not planned. The capsule is a one-shot."),
    ("Price questions from tourists", "Prices are aligned with the FW26 price list; tax-free rules as usual."),
]


def lb_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1.2 * cm, "INTERNAL USE ONLY – not for distribution to clients or press. Ref. MER-FW26-LB-004 v2 – 27.08.2026")
    canvas.drawRightString(19 * cm, 1.2 * cm, f"page {doc.page}")
    canvas.restoreState()


def build_launch_brief():
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=18, alignment=0, spaceAfter=4)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=12, spaceBefore=10)
    body = ParagraphStyle("b", parent=ss["BodyText"], fontName="Helvetica", fontSize=9.5, leading=12.5)
    small = ParagraphStyle("s", parent=body, fontSize=8, textColor=colors.grey)
    st = []
    st.append(Paragraph("FW26 IN-STORE LAUNCH BRIEF", h1))
    st.append(Paragraph("IRIDIA · AMALIA · ARTEM · Couture ASTRA", ParagraphStyle("sub", parent=body, fontSize=11)))
    st.append(Spacer(1, 6))
    st.append(Paragraph("From: Merchandising &amp; Product Marketing (C. Bassi, D. Longo) &nbsp;&nbsp; To: All boutiques, Area Managers, "
                        "Retail Excellence &nbsp;&nbsp; Date: 27 August 2026", small))
    st.append(Spacer(1, 10))
    st.append(Paragraph(LB_INTRO, body))
    st.append(Spacer(1, 8))
    t = Table(LB_STYLES, colWidths=[3.1 * cm, 2.6 * cm, 5.0 * cm, 1.5 * cm, 1.8 * cm, 3.6 * cm])
    t.setStyle(TableStyle([("FONT", (0, 0), (-1, -1), "Helvetica", 7.8), ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 7.8),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d2b44")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                           ("GRID", (0, 0), (-1, -1), 0.3, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    st.append(t)
    st.append(Paragraph("Retail prices EUR (Italy list). Local prices: see FW26 price list in the retail portal.", small))
    for title, txt, bullets in LB_SECTIONS:
        st.append(Paragraph(title, h2))
        st.append(Paragraph(txt, body))
        for b in bullets:
            st.append(Paragraph("• " + b, body))
    st.append(PageBreak())
    st.append(Paragraph("Calendar", h2))
    cal = [["Date", "What", "Who"],
           ["Thu 03/09", "Floor set FW26 newness (IRIDIA, AMALIA, ARTEM, RIVIERA, Cashmere Turtleneck)", "All doors"],
           ["Mon 14/09", "Window change W2 (VM pack sent 07/09)", "Flagships + boutiques"],
           ["Thu 24/09", "ASTRA launch 10:00 CET (local opening time in APAC/US)", "ASTRA doors"],
           ["w/c 05/10", "First sell-through review with Area Managers", "Merch + AM"]]
    t2 = Table(cal, colWidths=[2.4 * cm, 11 * cm, 4 * cm])
    t2.setStyle(TableStyle([("FONT", (0, 0), (-1, -1), "Helvetica", 8.5), ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 8.5),
                            ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.black), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white])]))
    st.append(t2)
    st.append(Paragraph("ASTRA doors", h2))
    st.append(Paragraph(LB_DOORS, body))
    st.append(Paragraph("FAQ", h2))
    for q, a in LB_FAQ:
        st.append(Paragraph(f"<b>{q}</b><br/>{a}", body))
        st.append(Spacer(1, 3))
    st.append(Spacer(1, 12))
    st.append(Paragraph("v2: corrected ASTRA launch time (v1 said 09:00) and added Cashmere Turtleneck to floor set.", small))
    p = D / "FW26_Launch_Brief_ILVARO_AMBRINE_ARNEB_ASTRA_v2.pdf"
    SimpleDocTemplate(str(p), pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.6 * cm, bottomMargin=1.8 * cm,
                      title="FW26 Launch Brief", author="Merchandising").build(st, onFirstPage=lb_footer, onLaterPages=lb_footer)
    TEXTS["launch_brief"] = LB_INTRO + " ".join(s[1] + " ".join(s[2]) for s in LB_SECTIONS) + " ".join(q + a for q, a in LB_FAQ)


# ---------------------------------------------------------------------------------------------
# 2. VEL quality alert (EML + PDF attachment) and follow-up
# ---------------------------------------------------------------------------------------------
TIB_MAIL = """Dear all,

please find attached the quality alert QA-26-017 regarding the VEL men's down vest (style J10911A00305, all colours).

We have received a few reports from boutiques about the zipper slider detaching from the chain or not closing
properly after some days of wear. The issue is linked to a supplier batch of sliders and concerns units delivered to
stores from 1 September 2026. Return rate on the affected units is currently below 3%, so there is no reason to
remove the style from the floor.

What we need from you, starting today:
1. Accept the return or exchange of affected VEL vests, also without receipt if the client is in the CRM.
2. Use return reason DEF in the POS (not QUALITY, not CHANGE_MIND).
3. Do NOT repair in store. Put the piece in the quarantine box with the attached form filled in.
4. Every Friday ship the quarantine box back to your DC (CSG for EMEA, TKO for APAC, NJ for Americas) with the
   return label "QA-26-017".
5. Check the VEL on the floor: if the slider is loose, take the piece off sale and treat it as point 3.

Please do not communicate anything to clients beyond "we will exchange it immediately". No posts, no comments on
social media. Press questions go to Corporate Communications.

Thank you for your cooperation,
Elena Rinaldi
Product Quality & After-Sales
"""
TIB_PDF_LINES = [
    ("QUALITY ALERT QA-26-017", "title"),
    ("Product: VEL – men's down vest – style J10911A00305 – colours 999 / 742 / 20D – all sizes", "p"),
    ("Issued: 05/10/2026 – Product Quality & After-Sales, Milano – Distribution: all boutiques, Area Managers, DCs", "p"),
    ("Description of the issue", "h"),
    ("Zipper slider (supplier lot ZS-0726) can detach from the chain or fail to lock. Detected through store reports. "
     "Affected scope: units delivered to stores from 01/09/2026. Units in DC stock have been checked and released.", "p"),
    ("Return procedure", "h"),
    ("a) accept return/exchange – b) POS reason code DEF – c) no in-store repair – d) quarantine box + form below – "
     "e) weekly shipment to DC with label QA-26-017 – f) floor check of displayed pieces", "p"),
    ("Store form (one line per piece)", "h"),
]


def build_tib():
    ss = getSampleStyleSheet()
    buf = io.BytesIO()
    st = []
    for txt, kind in TIB_PDF_LINES:
        if kind == "title":
            st.append(Paragraph(txt, ParagraphStyle("t", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=15, textColor=colors.HexColor("#a00000"))))
        elif kind == "h":
            st.append(Paragraph(txt, ss["Heading3"]))
        else:
            st.append(Paragraph(txt, ParagraphStyle("p", parent=ss["BodyText"], fontSize=9.5)))
    form = [["Store", "Date", "POS receipt", "Colour", "Size", "Defect (slider / chain / other)", "SA"]] + [[""] * 7 for _ in range(10)]
    t = Table(form, colWidths=[1.6 * cm, 1.8 * cm, 2.6 * cm, 1.6 * cm, 1.2 * cm, 5.0 * cm, 2.0 * cm], rowHeights=0.7 * cm)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.black), ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 7.5)]))
    st.append(t)
    st.append(Spacer(1, 8))
    st.append(Paragraph("Internal document – do not forward outside the company.", ParagraphStyle("f", parent=ss["BodyText"], fontSize=7, textColor=colors.grey)))
    SimpleDocTemplate(buf, pagesize=A4, title="QA-26-017 VEL").build(st)
    pdf = buf.getvalue()
    (D / "QA-26-017_TIB_zipper_return_procedure.pdf").write_bytes(pdf)
    m = make_eml(person("rinaldi"), ["all-stores@valentino-retail.example"],
                 "QUALITY ALERT QA-26-017 – VEL vest zipper – return procedure (action required)", TIB_MAIL,
                 sent="2026-10-05 17:42", cc=[person("valli"), "quality-claims@valentino-retail.example", person("ferrari")],
                 attachments=[("QA-26-017_TIB_zipper_return_procedure.pdf", pdf, "application", "pdf")],
                 extra_headers={"Importance": "High", "X-Priority": "1"}, msgid_seed="tib-alert-1")
    write_eml(m, D / "2026-10-05_QUALITY_ALERT_QA-26-017_TIB.eml")
    TEXTS["tib_mail"] = TIB_MAIL
    TEXTS["tib_pdf"] = " ".join(t for t, _ in TIB_PDF_LINES)

    follow = """Dear all,

short update on QA-26-017 (VEL vest).

After checking the store returns of the last days with the supplier, the affected slider lot was already used on
production delivered from mid-August, not only from 1 September as written in the first alert. Please apply the
same procedure also to pieces sold in the second half of August.

A few stores asked whether to stop selling VEL. Not at this stage: check each piece on the floor and in stock room
(open and close the zip 3 times, if the slider moves sideways take it out). Clean pieces can be sold.

Thanks to the stores that sent the counts last week, it helped.

Elena

> From: Elena Rinaldi
> Sent: Monday, 5 October 2026 17:42
> Subject: QUALITY ALERT QA-26-017 - VEL vest zipper - return procedure (action required)
> ...units delivered to stores from 1 September 2026. Return rate on the affected units is currently below 3%...
"""
    m2 = make_eml(person("rinaldi"), ["all-stores@valentino-retail.example"],
                  "RE: QUALITY ALERT QA-26-017 – VEL vest zipper – UPDATE scope", follow, sent="2026-10-09 11:05",
                  cc=["quality-claims@valentino-retail.example"], in_reply_to=m["Message-ID"], msgid_seed="tib-alert-2")
    write_eml(m2, D / "2026-10-09_RE_QUALITY_ALERT_QA-26-017_TIB_update.eml")
    TEXTS["tib_follow"] = follow.split(">")[0]


# ---------------------------------------------------------------------------------------------
# 3. Japan price increase (DOCX, Japanese)
# ---------------------------------------------------------------------------------------------
JP_TITLE = "【社外秘】2026年11月1日付 価格改定のお知らせ（継続品番）"
JP_PARAS = [
    "宛先：日本国内全店（銀座・表参道・心斎橋）店長、副店長、各位",
    "発信：MD部 山口 真理　　承認：リテール本部 森田 健二",
    "発信日：2026年9月30日",
    "いつもお疲れ様です。",
    "標記の件、本社（ミラノ）との協議の結果、継続品番（キャリーオーバー）につきまして2026年11月1日（日）より販売価格を改定いたします。"
    "為替および原材料費の上昇によるもので、平均改定率は約8％となります。FW26新作（IRIDIA、AMALIA、ARTEM、RIVIERA等）およびCouture ASTRAは対象外です。",
    "■ お客様へのご案内について",
    "・お客様へのご案内は10月9日（金）以降とし、それ以前は一切口外しないでください。SNS等で問い合わせがあった場合も「現時点ではお答えできません」とご対応ください。",
    "・VIC、ゴールド会員のお客様には10月9日以降、担当スタイリストより個別にご連絡をお願いします（電話またはLINE）。トークスクリプトは別途共有します。",
    "・10月31日（土）までのご購入は現行価格となります。お取り置きは通常通り最長7日間、価格は購入日の価格を適用します。",
    "■ 店舗作業",
    "・10月31日閉店後にプライスタグの差し替え作業を行います。新タグは10月26日の週に各店へ納品予定です。",
    "・POSの価格マスタは11月1日 0:00に自動で切り替わります。",
    "■ 主な品番の新価格（税込）",
    "※全品番の一覧は添付のExcel（別送）をご確認ください。",
    "ご不明な点はMD部 山口までご連絡ください。よろしくお願いいたします。",
]
JP_TABLE = [["品番", "スタイル", "現行価格", "新価格", "改定率"],
            ["J10911A00034", "NOVA", "¥305,000", "¥335,000", "+8%"],
            ["J20931A00012", "AUREA", "¥285,000", "¥308,000", "+8%"],
            ["J20931A00087", "LIVIANA", "¥403,000", "¥435,000", "+8%"],
            ["J10911A00088", "MISTRAL", "¥324,000", "¥350,000", "+8%"],
            ["J20931A00144", "ARIA", "¥265,000", "¥286,000", "+8%"],
            ["J10911A00305", "VEL", "¥195,000", "¥210,000", "+8%"],
            ["I10919B00011", "VLOGO CARDIGAN", "¥155,000", "¥167,000", "+8%"],
            ["I10918G00031", "VLOGO HOODIE", "¥116,000", "¥125,000", "+8%"]]


def build_japan():
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "MS Gothic"
    st.font.size = Pt(10.5)
    p = doc.add_paragraph()
    r = p.add_run(JP_TITLE)
    r.bold = True
    r.font.size = Pt(14)
    for para in JP_PARAS[:-2]:
        q = doc.add_paragraph(para)
        if para.startswith("■"):
            q.runs[0].bold = True
    t = doc.add_table(rows=len(JP_TABLE), cols=5)
    t.style = "Table Grid"
    for i, row in enumerate(JP_TABLE):
        for j, v in enumerate(row):
            t.cell(i, j).text = v
    for para in JP_PARAS[-2:]:
        doc.add_paragraph(para)
    doc.add_paragraph("以上")
    sec = doc.sections[0]
    sec.footer.paragraphs[0].text = "社外秘／Valentino Japan リテール本部　MD-JP-2026-031"
    doc.core_properties.author = "山口 真理"
    doc.core_properties.title = "価格改定のお知らせ"
    doc.save(D / "2026-09-30_価格改定のお知らせ_11月1日_継続品番.docx")
    TEXTS["japan"] = JP_TITLE + "".join(JP_PARAS)


# ---------------------------------------------------------------------------------------------
# 4. Golden Week staffing memo (EML)
# ---------------------------------------------------------------------------------------------
GW_MAIL = """Hi all,

as every year, Chinese National Day holidays are coming. This year we expect a stronger flow than 2025 in Europe
(new direct flights Chengdu-Milano, faster Schengen visas) and in Tokyo/Osaka/Seoul/Hong Kong.

Period: from Wednesday 30 September to Thursday 8 October (peak 1-7 October).

1) Mandarin speaking support
We have secured temporary Mandarin speaking staff (agency Lingo Retail / our Shanghai trainees) for:
- MIL01 Montenapoleone: 2 people, 30/09 - 08/10
- MIL02 Rinascente: 1 person, 1/10 - 7/10 (shared with the department store team)
- PAR01 Saint-Honore: 2 people, 30/09 - 08/10
- PAR02 Galeries Lafayette: 1 person + GL host desk
- VEN01 San Marco: 1 person, weekend days only
- TYO01, OSA01: managed locally by Japan HR
- SEL01: managed locally (Korea team already has 3 Mandarin speakers)
- HKG01: n/a
Please plan breaks and make sure they are introduced to the team on day 1. They are NOT authorised to process
tax-free or payments alone.

2) Payments
Check that Alipay+/WeChat Pay and UnionPay terminals are working BEFORE 30/09. Open an IT ticket now if not.
Daily limits on some UnionPay cards: suggest split payment, never "manual" card entry.

3) Tax-free
Global Blue / Planet: printed forms in stock, staff trained on the new digital validation (Italy and France).
Remember passport check at the moment of the sale, no copies of passports kept in store.

4) Stock
Merchandising has not planned extra allocation for these days. Please check your heavy outerwear in black (Nova,
Aurea, Liviana) and send transfer requests early through the usual channel, not on the last day.

5) Reporting
Please add "CN %" to your closing email during the period (estimate is fine).

Thank you and good luck, it will be a busy one.

Matteo Colombo
Retail Excellence EMEA & APAC Projects
"""


def build_gw():
    m = make_eml(person("colombo"), ["all-stores-emea@valentino-retail.example", "tyo01.store@valentino-retail.example",
                                     "osa01.store@valentino-retail.example", "sel01.store@valentino-retail.example",
                                     "hkg01.store@valentino-retail.example"],
                 "Golden Week 30/09-08/10: staffing, payments, tax free", GW_MAIL, sent="2026-09-22 10:12",
                 cc=[person("valli"), person("leung"), person("galli"), person("moreau"), person("mcleod"), person("wagner")],
                 msgid_seed="gw-memo")
    write_eml(m, D / "2026-09-22_Golden_Week_staffing_payments_taxfree.eml")
    TEXTS["gw"] = GW_MAIL


# ---------------------------------------------------------------------------------------------
# 5. Double 11 price-match policy (DOCX, Chinese)
# ---------------------------------------------------------------------------------------------
CN_TITLE = "关于“双十一”期间门店价格政策及客户沟通的执行说明"
CN_PARAS = [
    "文件编号：GC-RT-2026-1019　　密级：内部",
    "发送：华东、华北、西南区各门店店长、副店长；区域经理 赵磊",
    "抄送：周雪（大中华区零售总监）、CRM团队、电商团队",
    "发布日期：2026年10月19日",
    "各位同事：",
    "天猫官方旗舰店“双十一”预售将于10月20日20:00开始。根据往年经验，预售开始后会有部分客户到店或通过微信询问门店是否可以按照线上活动价格（含满减、跨店津贴、定金膨胀等）购买。现就门店执行口径统一说明如下：",
    "一、门店不做价格匹配。门店零售价格以FW26价格表为准，不参与任何线上平台的价格活动，不接受截图比价。",
    "二、不得私下给予折扣、赠品或以“积分”“礼品卡”等形式变相补差。如发现违规，按公司规定处理。",
    "三、建议话术：“非常理解您的想法。门店的价格和服务是全国统一的，我们可以为您提供专属的试穿、修改建议和售后服务。如果您需要的款式和尺码，我可以先帮您确认库存/预留。”请勿评价电商平台价格或活动。",
    "四、对于VIC客户，如客户坚持，可登记需求并上报区域经理，由CRM团队统一评估是否提供生日礼遇或活动邀请，门店不得自行承诺。",
    "五、线上活动包含的款式以电商团队通知为准。目前已知ASTRA系列、IRIDIA不参加线上活动。",
    "六、请各门店在每日闭店邮件中记录“比价询问”次数（大概数字即可），便于总部评估影响。",
    "如有问题请联系孙怡雯（商品）或CRM团队。谢谢大家配合！",
]


def build_cn():
    doc = Document()
    doc.styles["Normal"].font.name = "SimSun"
    doc.styles["Normal"].font.size = Pt(11)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(CN_TITLE)
    r.bold = True
    r.font.size = Pt(15)
    for para in CN_PARAS:
        q = doc.add_paragraph(para)
        if para[:2] in ("一、", "二、"):
            q.runs[0].bold = True
    q = doc.add_paragraph("大中华区零售运营部\n2026年10月19日")
    q.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    doc.core_properties.author = "孙怡雯"
    doc.save(D / "2026-10-19_双十一期间门店价格政策执行说明.docx")
    TEXTS["cn"] = CN_TITLE + "".join(CN_PARAS)


# ---------------------------------------------------------------------------------------------
# 6. Cold weather selling tips (EML, HTML + text) — sent Tue Oct 13
# ---------------------------------------------------------------------------------------------
COLD_TXT = """Ciao a tutti / Hello everyone,

the weather forecasts for the next 10 days show a strong drop of temperatures in Central and Northern Europe:
max 2-6 degrees in Munich, Zurich, Berlin, Copenhagen, Amsterdam, Geneva, a bit milder in Paris, London and Milan.
First snow in Munich is expected around 20 October, snow down to 1,000 m in Switzerland.

This is the moment we wait for all year. A few reminders from Retail Excellence and Merchandising:

HEAVY DOWN FIRST
- Bring the iconic jackets to the front table and the first rail: NOVA, MISTRAL, MONTELUCE for men; AUREA,
  LIVIANA, FIAMMETTA for women. Where black AUREA is missing, show beige and off-white.
- Remind the client of the warmth rating: the Monteluce wool shell is the warmest city jacket we have.
- ARTEM: our feedback from the first weeks is that it fits generous. Let the client try his usual size AND one
  size down, most of them leave with the smaller one.

LAYERING
- Vlogo Cardigan / Vlogo Padded Cardigan under the down jacket: the easiest UPT driver.
- Beanie + Valentino Scarf + Winter Gloves at the cash desk.

STOCK
- Check your depth on beanies and gloves today, not on Saturday. Send replenishment requests to Luca Ferrari's team
  by Wednesday noon for Friday delivery.
- No extra allocation of heavy down is planned before end of October, transfers between stores only.

CLIENTELING
- Call the clients who looked at a down jacket in September without buying.

Buone vendite!
Matteo & Chiara
"""
COLD_HTML = "<html><body style=\"font-family:Calibri,Arial;font-size:11pt\">" + "".join(
    f"<p>{line}</p>" if line and not line.startswith("-") else (f"<li>{line[2:]}</li>" if line else "<br>")
    for line in COLD_TXT.splitlines()) + "<p style=\"color:#888;font-size:8pt\">Internal communication - do not forward</p></body></html>"


def build_cold():
    m = make_eml(person("colombo"), ["all-stores-emea@valentino-retail.example"], "Freddo in arrivo / Cold weather is here: selling tips",
                 COLD_TXT, sent="2026-10-13 09:37", cc=[person("bassi"), person("valli"), person("wagner"), person("mcleod"),
                                                         person("moreau"), person("galli")], html=COLD_HTML, msgid_seed="cold-tips")
    write_eml(m, D / "2026-10-13_Cold_weather_selling_tips.eml")
    TEXTS["cold"] = COLD_TXT


# ---------------------------------------------------------------------------------------------
# 7. Short ARTEM fit note (EML, Oct 2) from Davide Longo
# ---------------------------------------------------------------------------------------------
ARNEB_TXT = """Hi all,

quick one on ARTEM. A handful of stores told us clients find it "big". We checked with the product team: the pattern is
unchanged vs the fit sample, the faux fur hood and the down volume make it look larger on the hanger.

Please keep advising the usual size. If the client is between two sizes, the smaller one is fine.
Exchanges for size: as usual, reason SIZE in the POS.

Thanks
Davide

Davide Longo
Merchandiser Men & Knitwear - EMEA
"""


def build_arneb():
    m = make_eml(person("longo"), ["all-stores-emea@valentino-retail.example"], "ARTEM sizing", ARNEB_TXT,
                 sent="2026-10-02 16:20", cc=[person("bassi")], msgid_seed="arneb-note")
    write_eml(m, D / "2026-10-02_ARNEB_sizing_note.eml")
    TEXTS["artem"] = ARNEB_TXT


if __name__ == "__main__":
    build_launch_brief()
    build_tib()
    build_japan()
    build_gw()
    build_cn()
    build_cold()
    build_arneb()
    check_texts(TEXTS)
    for p in sorted(D.iterdir()):
        print(p.name, p.stat().st_size)
