# HKG01 Hong Kong Canton Road - hand-authored closing emails, part 1 (2026-08-31 .. 2026-09-30)
# karen = 陳嘉欣 Karen Chan (SM, Canto-English, Outlook HTML sometimes), ming = 黃志明 Ming Wong (ASM, short English, iPhone),
# sammi = 李心怡 Sammi Lee (SA, WhatsApp copy-paste), box = store mailbox
import html as _h

DISCLAIMER = """
This e-mail and any attachments are confidential and may be privileged. If you are not the intended recipient, please notify the sender immediately and delete it. Valentino Hong Kong Limited"""


def outlook(text, kpi):
    """Render an Outlook-style HTML body: KPI table (kpi = list of (label, value)) + the authored text paragraphs."""
    rows = "".join(f"<tr><td style='border:1px solid #999;padding:2px 6px;background:#f2f2f2'>{_h.escape(k)}</td>"
                   f"<td style='border:1px solid #999;padding:2px 6px;text-align:right'>{_h.escape(v)}</td></tr>" for k, v in kpi)
    paras = "".join(f"<p class=MsoNormal style='margin:0'>{_h.escape(l) if l.strip() else '&nbsp;'}</p>" for l in text.split("\n"))
    return ("<html><head><meta http-equiv=Content-Type content='text/html; charset=utf-8'><style>p.MsoNormal{font-family:Calibri,"
            "'Microsoft JhengHei',sans-serif;font-size:11pt}</style></head><body lang=ZH-HK><div class=WordSection1>"
            f"<table style='border-collapse:collapse;font-family:Calibri;font-size:10pt'>{rows}</table><p>&nbsp;</p>{paras}</div></body></html>")


def kpi_text(kpi):
    return "\n".join(f"{k}\t{v}" for k, v in kpi)


_K0902 = [("Sales", "HK$194,400"), ("Budget", "HK$147,500"), ("Ach%", "132%"), ("Traffic", "110"), ("Txn", "15"), ("CR", "13.6%"), ("ATV", "HK$12,960")]
_T0902 = """Hi Vivian, all,

今日有個內地 VIC 太太嚟，一次過買咗 Aurea navy 同兩件 cardigan 俾老公，所以 ach 好靚 :)
Jersey Polo navy x2, Crewneck 白 x2 都有出。
Vlogo Hoodie navy XS 有人問，冇 size。

Karen"""

_K0912 = [("Sales", "HK$409,500"), ("Budget", "HK$322,300"), ("Ach%", "127%"), ("Traffic", "168"), ("Txn", "23"), ("CR", "13.7%"), ("UPT", "2.0")]
_T0912 = """Hi all,

Very good Saturday! 新到嘅 Artem black 今日賣咗 5 件，d 客話長身好有型，不過全部都係試平時 size 嫌大，要落一個碼先啱。Artem black size 4 已經 sold out，size 1 有個好瘦嘅客問都冇。
Iridia black size 0、Monteluce black 7、GTX grey 42 都有人問，冇貨。
Aurea black size 2 冇晒，Amalia black 0 都冇。

Karen"""

_K0925 = [("Sales", "HK$320,700"), ("Budget", "HK$262,300"), ("Ach%", "122%"), ("Traffic", "183"), ("Txn", "16"), ("ATV", "HK$20,042")]
_T0925 = """Hi Vivian,

Astra 第二日，今日賣咗 3 件 oversize black，全部係內地客，佢哋話上海北京要排隊，香港唔使排仲平啲。本地客就麻麻，試完話太大件、太貴。
Amalia black x2，Winter Gloves x2。
Monteluce grey 7 有人問；Monteluce black size 2 冇晒。

Karen"""

E1 = [
dict(day="2026-08-31", send="2026-08-31 22:41", frm="karen", subject="HKG01 closing 31/8",
body="""Hi all,

Sales HK$104.8k, ach 70%, traffic 93, 10 txn.
月尾好靜，主要係 cap 同 T-shirt。今日收咗 172 件貨，大部分係 FW 嘅 knit 同 accessories，已經上晒。
Aria size 1 退咗一件，客話太大。

Karen
""" + DISCLAIMER),

dict(day="2026-09-01", send="2026-09-01 22:19", frm="ming", subject="HKG01 closing 1 Sep",
body="""Sales 77.3k / 53%
Traffic 90, 6 txn
Very quiet, raining whole afternoon. Vlogo Cardigan black x2.

Ming

Sent from my iPhone"""),

dict(day="2026-09-02", send="2026-09-02 22:48", frm="karen", subject="HKG01 closing 2/9", body=_T0902 + "\n\n" + kpi_text(_K0902),
     html=outlook(_T0902, _K0902)),

dict(day="2026-09-03", send="2026-09-03 22:36", frm="karen", subject="HKG01 closing 3/9",
body="""Hi all,

Sales HK$178.1k, ach 92%, traffic 131, 12 txn.
今日多咗 d 外國遊客，有幾個 tourist group from Middle East 經過入嚟睇。
Jersey Polo black, Vel black, Logo T black, Tricot cardigan black 各 2。

Karen"""),

dict(day="2026-09-04", send="2026-09-04 22:52", frm="karen", subject="HKG01 daily closing 4 Sep",
body="""Hi all,

Sales 180.1k, ach 74%. Traffic 161 但係得 9 txn, CR 5.6% 好低。
今日好多本地人行街，但係 33 度，冇人想試 down jacket。
Liviana off-white size 2 有人問冇貨。Aurea off-white 2 都 sold out 咗。
Alpina black 賣咗 2 對，客人去日本 ski trip。

Karen"""),

dict(day="2026-09-05", send="2026-09-05 23:03", frm="karen", subject="HKG01 closing 5/9 (Sat)",
body="""Hi Vivian, all,

Sat sales HK$290.9k, ach 84%, traffic 216, 22 txn.
內地客同本地客大概一半一半。Beanie navy/black 各 3，Jersey Polo black 3。
Aurea off-white 00 同 Mistral navy 6 有人問，冇貨。

Karen"""),

dict(day="2026-09-06", send="2026-09-06 22:44", frm="ming", subject="HKG01 closing 6 Sep",
body="""Sales 242.2k, ach 79%
Traffic 167, 14 txn
Tricot cardigan black x3, Jersey Polo black x3, scarf x2
Missed: Nova navy 1, Hoodie navy XS (again)

Ming
Sent from my iPhone"""),

dict(day="2026-09-07", send="2026-09-07 22:31", frm="karen", subject="HKG01 closing 7/9",
body="""Hi all,

Sales 152.8k, ach 85%, 11 txn.
收咗 79 件貨。Aurea black 2 件、Vel black 2 件、Logo T black 2 件。
星期一正常。

Karen"""),

dict(day="2026-09-08", send="2026-09-08 22:27", frm="ming", subject="HKG01 closing 8/9",
body="""Sales 175.1k, 100% 👍
Traffic 100, 12 txn
Fiammetta black x2 (both mainland clients)
1 beanie returned - quality, logo patch 甩線

Ming"""),

dict(day="2026-09-09", send="2026-09-09 22:39", frm="karen", subject="HKG01 closing 9/9",
body="""Hi all,

Sales 173.5k, ach 98%, 9 txn.
Cap 白 x2, Logo T black x2, cardigan black x2。
Iridia black size 0 已經 sold out，新貨嚟咗一個禮拜就冇咗細碼。

Karen"""),

dict(day="2026-09-10", send="2026-09-10 22:45", frm="karen", subject="HKG01 closing 10/9",
body="""Hi all,

Sales HK$210.3k, ach 104%, 12 txn.
Logo T black 4 件，Aurea black 3 件，crewneck black 2，Urban Backpack 2。
冇乜特別。

Karen"""),

dict(day="2026-09-11", send="2026-09-11 22:51", frm="karen", subject="HKG01 closing 11/9",
body="""Hi all,

Sales 224.1k, ach 92%, traffic 134.
Vlogo Hoodie black x4，Monteluce navy x2，Logo T 黑同 navy 各 2。
聽日星期六，Harbour City 有活動，希望多 d 人。

Karen"""),

dict(day="2026-09-12", send="2026-09-12 23:08", frm="karen", subject="HKG01 closing 12/9", body=_T0912 + "\n\n" + kpi_text(_K0912),
     html=outlook(_T0912, _K0912)),

dict(day="2026-09-13", send="2026-09-13 22:58", frm="ming", subject="HKG01 closing 13 Sep",
body="""Sales 295.2k / 94%
Traffic 194, 20 txn
Hoodie black x4, Logo T black x3, navy x3, Iridia off-white x3 (white 都開始有人買)
Missed: cashmere turtleneck brown L, hoodie black XL, Logo T navy XL
Riviera black 4 & Vlogo Cardigan black L sold out

Ming
Sent from my iPhone"""),

dict(day="2026-09-14", send="2026-09-14 22:24", frm="karen", subject="HKG01 closing 14/9",
body="""Hi all,

Sales 117.3k, ach 66%, 6 txn. 好靜。
收貨 268 件，Artem black 補咗 size 4。
Camilla black x2。

Karen"""),

# 2026-09-15 Tue: no email

dict(day="2026-09-16", send="2026-09-16 22:12", frm="karen", subject="HKG01 closing 16/9 + typhoon arrangement", cc=["vivian"],
importance="high",
body="""Hi Vivian, all,

Sales HK$166.0k, ach 87%, 11 txn. Logo T black x3, hoodie black x2, Aurea black x2.

Typhoon: 天文台今晚 9:40 已經改咗 3 號波，話聽朝 6 點前好大機會改 8 號波。如果聽朝 8 號波，按公司 policy 我哋唔開舖，所有同事留喺屋企，唔使返工。我已經喺 WhatsApp group 通知晒同事，等天文台消息再 update。
今晚已經將門口 display 全部收入舖，防水沙包放好。

Karen"""),

dict(day="2026-09-17", send="2026-09-17 19:35", frm="karen", subject="HKG01 17/9 - store closed (T8)",
body="""Hi Vivian, all,

FYI 今日 8 號波全日冇開舖，sales 0。所有同事 safe。
Harbour City 全場關咗，廣東道好多樹倒咗。天文台話聽朝可能落 3 號波，如果改波我哋會喺除下 8 號波之後 2 個鐘內開舖，Ming 負責開舖。

Karen

Sent from my iPhone"""),

dict(day="2026-09-18", send="2026-09-18 22:21", frm="ming", subject="HKG01 closing 18 Sep (opened 3pm)",
body="""Hi all,

8 號波 12:40 先除，我哋 3pm 開舖。
Sales 41.0k only, traffic 52, 6 txn
街上好少人，Canton Rd 仲有好多樹枝冇清。內地客反而多過本地客，酒店困咗兩日出嚟行。
Riviera black x2
3 returns: Aurea size 2 (quality - 袖口車線甩咗), Riviera 4 (change mind), hoodie XL (gift)
Cosimo navy 3 missed

Ming
Sent from my iPhone"""),

dict(day="2026-09-19", send="2026-09-19 22:54", frm="karen", subject="HKG01 closing 19/9",
body="""Hi all,

Sales 321.5k, ach 91%, traffic 225。風球之後第一個週末，人流返晒嚟。
Jersey Polo black x3，hoodie navy x2，cap navy x2。
Cosimo navy 3 又有人問 (琴日都有一個)。

Karen"""),

dict(day="2026-09-20", send="2026-09-20 23:01", frm="karen", subject="HKG01 closing 20/9",
body="""Hi Vivian, all,

Sales HK$225.3k, ach 73%, traffic 223 但係得 12 txn，CR 5.4%。內地客多 (六成幾)，好多都係睇睇吓。
Vel black x3，crewneck black x3。
Artem 3 換咗 2，又係話大。
另外前日 2 點幾已經開返舖，所以風球嗰日 sales 唔算太差，問題係冇人。

Karen"""),

dict(day="2026-09-21", send="2026-09-21 22:33", frm="ming", subject="HKG01 closing 21/9",
body="""Sales 119.5k / 66%, 11 txn
Riviera black size 4 - 2 clients asked, sold out since last week, pls check replen
Iridia off-white 3 missed
Returns: Amalia 0 (change mind), cardigan L (size)
Shipment for today not arrived, DHL said Wed. pls advise

Ming"""),

dict(day="2026-09-22", send="2026-09-22 22:29", frm="karen", subject="HKG01 closing 22/9",
body="""Hi all,

Sales 193.6k, ach 107%, 10 txn.
GTX black x2, Logo T black x2, Jersey Polo black x2.
Vel black size 1 有個女仔問，冇；GTX grey 39 都冇。
Logo T navy M 冇晒。
上個禮拜嘅貨仲未到，logistics 話聽日。

Karen"""),

dict(day="2026-09-23", send="2026-09-23 22:47", frm="karen", subject="HKG01 closing 23/9", cc=["vivian", "logistics_apac"],
body="""Hi Vivian, logistics team,

Sales HK$219.3k, ach 113%, 14 txn.
Logo T black x4，Cable knit beige x2，Tricot navy x2，Monteluce black x2。

Delivery: 本來 21/9 (Mon) 到嘅 198 件今日下晝先到，遲咗 2 日，入面有 Astra launch 嘅貨，好彩趕得切聽日。今晚同事要留低開箱、貼 tag。希望下次 launch 貨可以早 d 送，唔好咁 last minute。

Karen"""),

dict(day="2026-09-24", send="2026-09-24 22:38", frm="karen", subject="HKG01 closing 24/9 - Astra launch",
body="""Hi Vivian, all,

Sales 217.6k, ach 96%, 9 txn.
Astra 第一日：冇排隊，早上得幾個預約嘅客，試咗冇買，話太大件同埋太貴 (cape HK$2萬幾)。今日 Astra 0 件。
反而 Alpina black x2，Jersey Polo navy x2，Vel black x2。

Karen"""),

dict(day="2026-09-25", send="2026-09-25 22:51", frm="karen", subject="HKG01 closing 25/9", body=_T0925 + "\n\n" + kpi_text(_K0925),
     html=outlook(_T0925, _K0925)),

dict(day="2026-09-26", send="2026-09-26 23:06", frm="ming", subject="HKG01 closing 26 Sep",
body="""Sales 359.2k / 94%
Traffic 195, 21 txn
Mistral black x3, Tricot grey x2, beanie white x2, Jersey Polo navy x2
Ettore black 5 missed
Artem 3 exchanged to 2 (again too big)

Ming
Sent from my iPhone"""),

dict(day="2026-09-27", send="2026-09-27 22:59", frm="sammi", subject="HKG01 closing 27/9 (Sammi)",
body="""Hi all, Karen 同 Ming 今日 off，我代 send closing:

[21:48] Sammi: 今日 sales 301.6k, 81%
[21:48] Sammi: traffic 255, 16 單
[21:49] Sammi: Logo T black 3, cashmere turtleneck 啡色 3 (好多人鍾意隻色), cap 白 2
[21:50] Sammi: Mistral navy 3 冇貨
[21:50] Sammi: Jersey Polo M 退咗一件，唔要

Thx
Sammi"""),

dict(day="2026-09-28", send="2026-09-28 22:43", frm="karen", subject="HKG01 closing 28/9",
body="""Hi all,

Sales 228.9k, ach 110%, 14 txn.
Jersey Polo black x4，hoodie black x3，Tricot black x3。
收貨 153 件。
Mistral navy 3 (同上禮拜嗰個客)、Astra oversize black M 有人問，冇。

Vel size 3 退咗一件，客話 zip 頭拉到一半卡住，用力拉 zip 頭直頭甩咗出嚟。佢 8 月尾買嘅。我哋已經寄返 aftersales。

Karen"""),

dict(day="2026-09-29", send="2026-09-29 22:31", frm="ming", subject="HKG01 closing 29/9",
body="""Sales 139.6k / 69%
Traffic 139, 10 txn, 67% mainland
GTX black x5 (one client bought for family)
Alpina black 35 missed
Another Vel zip return, size 4. Same problem as yesterday, slider stuck then came off. 2 in 2 days - batch issue? pls check with aftersales

Ming
Sent from my iPhone"""),

dict(day="2026-09-30", send="2026-09-30 22:55", frm="karen", subject="HKG01 closing 30/9 - Golden Week starts",
body="""Hi Vivian, all,

Sales HK$244.7k, ach 108%, traffic 183, 18 txn.
今日開始內地國慶假期，下晝已經見到多咗旅行團喺廣東道排隊入其他品牌。
Vlogo Hoodie black 9 件！好多內地後生仔一買就幾件。hoodie navy 3，cardigan black 3。
Aurea black 0 sold out。

Vel 又退一件 size 3，zip 頭。3 日 3 件，請 aftersales 盡快回覆係咪 batch 問題，我哋 floor 仲有十幾件 Vel。

Karen"""),
]
