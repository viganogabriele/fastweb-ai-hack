# HKG01 Hong Kong Canton Road - hand-authored closing emails, part 2 (2026-10-01 .. 2026-10-21)
from hkg01_p1 import outlook, kpi_text, DISCLAIMER

_K1001 = [("Sales", "HK$354,100"), ("Budget", "HK$232,500"), ("Ach%", "152%"), ("Traffic", "209"), ("Txn", "16"), ("ATV", "HK$22,131"), ("Mainland %", "~70%")]
_T1001 = """Hi Vivian, all,

國慶第一日，廣東道成條街都係內地旅行團同自由行，我哋門口都要排隊，10 個 10 個咁放入嚟。
Maya navy x3，Logo T navy x2，Cable knit 白/黑各 2。Maya navy 4 冇晒。
Maire black 0 一早已經冇，Rosiere black 1 有人問冇貨。

Tib 又退一件 size 4，都係 zip 頭。由 28 號到今日已經 4 件，aftersales 仲未覆。

Karen"""

_K1017 = [("Sales", "HK$413,600"), ("Budget", "HK$466,700"), ("Ach%", "89%"), ("Traffic", "300"), ("Txn", "28"), ("CR", "9.3%"), ("UPT", "1.57")]
_T1017 = """Hi all,

星期六本地客多返 (五成半)，好多係嚟睇冬天衫準備去日本韓國旅行。
Tricot black x3，Chambre black x3，Tib black x3 (新批次，賣之前我哋逐件 check 過 zip)。
Missed: Bady black 1，粉紅 Ilvaro 2，Chambre black 0。
Cable knit S 退一件，size 問題。

Karen"""

E2 = [
dict(day="2026-10-01", send="2026-10-01 23:12", frm="karen", subject="HKG01 closing 1/10 - National Day", body=_T1001 + "\n\n" + kpi_text(_K1001),
     html=outlook(_T1001, _K1001)),

dict(day="2026-10-02", send="2026-10-02 23:25", frm="karen", subject="HKG01 closing 2/10 !!!",
body="""Hi Vivian, all,

Sales HK$558.0k, ach 193%!!! Traffic 294, 32 txn. 開舖以嚟最好嘅 Friday 之一。

1. Ilvaro black 賣咗 7 件！！中午開始一個接一個內地女仔拎住部電話嚟問，show 張相俾我睇，係韓國 LUMIERE 個尹夏恩喺巴黎 fashion week 着住嗰件粉紅色 Ilvaro (小紅書、IG 都係呢張相)。粉紅色我哋得返一件 size 2，size 0 嘅客冇得買，就買咗黑色。黑色 size 0 而家都冇晒。
2. Polo black x7 (同一個 group 嘅男仔)，cap 白 x5，beanie black x4。
3. Missed: Bady black 3，Polaris oversize black M，Cable knit 白 S。
4. Montcla black 3、Maya navy 4 冇晒。

聽日星期六估計仲多人，已經安排全部同事返工。

Karen"""),

# 2026-10-03 Sat: no own email (covered on 10/4)

dict(day=["2026-10-03", "2026-10-04"], send="2026-10-04 23:31", frm="ming", subject="HKG01 closing 3/10 + 4/10",
body="""Hi all, sorry 琴日太忙冇 send，2 日一齊:

3/10 Sat
Sales 582.8k / 144%
Traffic 330, 22 txn (ATV 好高, 2萬6)
Hermine black x6 (mainland ladies), Polaris cape white x2, GTX black x2
Missed: Maire black 0, Bady black 3, pink Ilvaro 00

4/10 Sun
Sales 287.9k / 73%
Traffic 353 but only 19 txn, CR 5.4%. Tour groups come in, take photos, leave.
Hermine black x3, Cable knit black x3, hoodie black x3
Pink Ilvaro: size 0 x2, 1, 3 asked. Only size 2 left
Missed: Maire black 0, Flammette black 3, Rosiere black 2, Tricot navy XS & XXL
Returns: Tib 2 (gift, not zip), Arneb 3 exchanged

Hermine black 2, Maire black 2 now sold out

Ming
Sent from my iPhone"""),

dict(day="2026-10-05", send="2026-10-05 22:49", frm="karen", subject="HKG01 closing 5/10",
body="""Hi all,

Sales 304.0k, ach 140%, 14 txn.
Ambrine black x3，Ilvaro black x2，hoodie black x4。有個客買咗粉紅色 beanie 話襯 Ilvaro，但係 Ilvaro 粉紅冇佢個 size。
收貨 239 件，冇粉紅 Ilvaro，冇 Maire black。
Maire size 4 退一件，太大。
Ilvaro off-white 00 有人問。

Karen"""),

dict(day="2026-10-06", send="2026-10-06 22:58", frm="karen", subject="HKG01 closing 6/10",
body="""Hi all,

Sales 298.8k, ach 137%, 18 txn. 內地客 64%。
Maire off-white x4，hoodie black x4，turtleneck navy x2。
最後一件粉紅 Ilvaro (size 2) 今日賣咗，而家全部粉紅 sold out。
Rosiere black 2 有人問冇貨。

Karen"""),

dict(id="hkg_1007", day="2026-10-07", send="2026-10-07 22:44", frm="karen", subject="HKG01 closing 7/10",
body="""Hi Vivian, all,

Sales 278.5k, ach 119%, 15 txn.
Cardigan black x4，hoodie black x3，Maya navy x2，Maire black x2 (最後兩件 size 3)。
而家 Maire black 0/1/2 全部冇晒。
粉紅 Ilvaro size 1 又有人問，我哋開咗 waitlist。Logo T navy XL 冇。

Karen"""),

dict(id="hkg_1008_q", reply_to="hkg_1007", suffix="_re1", send="2026-10-08 10:06", frm="vivian",
to=["karen"], cc=["merch_hktw"], subject="RE: HKG01 closing 7/10",
body="""Hi Karen,

How many clients on the pink Ilvaro waitlist now, by size? Merch is asking for a number for the next allocation. Also - have you checked with TPE01 if they have any pink left for a transfer?

Thanks,
Vivian

From: Karen Chan
Sent: Wednesday, October 7, 2026 22:44
Subject: HKG01 closing 7/10
..."""),

dict(id="hkg_1008_a", reply_to="hkg_1008_q", suffix="_re2", send="2026-10-08 12:37", frm="karen",
to=["vivian"], cc=["merch_hktw"], subject="RE: RE: HKG01 closing 7/10",
body="""Hi Vivian,

Waitlist 而家有 15 個客：size 0 最多 (6 個)，size 1 x4，00 x2，2 x2，3 x1。大部分係內地客，留咗微信。
TPE 我問咗 Jenny，佢話台北都冇粉紅，所以冇得 transfer。

Thanks
Karen

Sent from my iPhone"""),

dict(day="2026-10-08", send="2026-10-08 22:37", frm="ming", subject="HKG01 closing 8/10",
body="""Sales 328.8k / 135%
Traffic 197, 20 txn, mainland 72%
GTX black x3, Ilvaro black x3, Logo T white x2, Hermine black x2
3 clients asked for 粉紅 Bady size 0 / 1 / 2 - none
Cardigan navy XL missed
Bady off-white 2, Ilvaro black 0 sold out

Last day of mainland holiday, should be quieter from tmr

Ming
Sent from my iPhone"""),

dict(suffix="_fwd", send="2026-10-09 15:42", frm="karen", to=["vivian"], cc=["merch_hktw"], subject="FW: 预留粉色Ilvaro 1码",
body="""Hi Vivian,

FYI 內地 VIC 客 (上海，年消費 HK$30萬+) email 嚟想留粉紅 Ilvaro size 1，佢 24/10 嚟香港。我哋而家冇貨，如果下批有貨可唔可以幫佢留一件？

Karen

---------- Forwarded message ---------
From: Zhou Yuqing <yuqing.zhou88@example.cn>
Date: Fri, Oct 9, 2026 at 13:20
Subject: 预留粉色Ilvaro 1码
To: <hkg01.store@moncler-retail.example>

Karen你好，

我是上次在你们店买Hermine的周小姐。我想要那件粉色的Ilvaro（就是尹夏恩穿的那件），1码。上海北京都说没货，我10月24号会去香港，可以帮我留一件吗？可以先付定金。

谢谢！
周雨晴
发自我的iPhone"""),

dict(day="2026-10-09", send="2026-10-09 22:28", frm="karen", subject="HKG01 closing 9/10",
body="""Hi all,

Sales 197.9k, ach 66%, 14 txn. 國慶假期完咗，內地客即刻少咗一半。
Hoodie navy x3，cap black x3，Tib black x2，Tricot navy x2。
粉紅 Ilvaro size 1、2 都有人問；Maire black 3、Tricot grey S 冇貨。
Tib black 4 冇晒。

Karen"""),

dict(day="2026-10-10", send="2026-10-10 23:02", frm="ming", subject="HKG01 closing 10/10",
body="""Sales HK$50.1k, ach 118%
Traffic 299, 27 txn
Montcla black x4, Bady black x4, Logo T black x4, GTX black x3
Missed (lots): Maire black 0 & 2, Ilvaro black 0, Montcla black 1, Montgenevre black 1, Montgenevre grey 7, turtleneck navy S
1 Tib zip return, size 4

Ming"""),

dict(day="2026-10-11", send="2026-10-11 22:46", frm="karen", subject="HKG01 closing 11/10",
body="""Hi all,

Sales 304.2k, ach 75%, 19 txn。本地客返返嚟 (五成)。
Maya navy x3，Legere belt bag x2，Tricot navy x2，Cable knit 白 x2。
Turtleneck navy S 兩個客問；Maire black 0、Maire beige 00、Ilvaro black 1、粉紅 Ilvaro 0 同 1 都冇。
Maire off-white 1 都冇埋。

Karen"""),

dict(day="2026-10-12", send="2026-10-12 22:33", frm="karen", subject="HKG01 closing 12/10",
body="""Hi all,

Sales 166.2k, ach 75%, 11 txn.
收貨 308 件，仍然冇 Ilvaro (粉紅或者黑都冇)。
Bady black x5 (好多人買唔到 Ilvaro 就揀 Bady)。
今日問 Ilvaro 嘅特別多：黑色 00 x2、0、1；粉紅 0、1。Maire black 2 都有人問。
Cable knit L 退咗，唔鍾意。

Karen"""),

dict(day="2026-10-13", send="2026-10-13 22:41", frm="ming", subject="HKG01 closing 13/10",
body="""Sales 325.0k / 140%
Traffic 166, 20 txn
Logo T black x7 (one Korean group), crewneck black x2, Tib black x2, Chambre black x2
Missed: Ilvaro black 0, pink Ilvaro 1
Returns: Maire 1 (gift), Tib 4 (change mind, not zip)

Ming
Sent from my iPhone"""),

dict(day="2026-10-14", send="2026-10-14 22:19", frm="karen", subject="HKG01 closing 14/10",
body="""Hi all,

Sales 128.9k, ach 56%, 9 txn. 落咗成日雨，好靜。
Polo black x3。
Ilvaro black 00、GTX black 39 有人問。
Cable knit M 換色冇貨退咗；Arneb 6 換 5。

Karen"""),

dict(day="2026-10-15", send="2026-10-15 22:52", frm="karen", subject="HKG01 closing 15/10",
body="""Hi all,

Sales 271.7k, ach 104%, 17 txn.
Montcla black x4，Legere belt bag x3，Bady black x3。
Maire black 1、Ecrins black 6、Polaris oversize 淺藍 XL 有人問。
Tib size 6 又係 zip，退咗。到今日我哋總共退咗 6-7 件 Tib 都係 zip 頭問題。

Karen"""),

dict(day="2026-10-16", send="2026-10-16 22:37", frm="sammi", subject="HKG01 closing 16/10 (Sammi)",
body="""Hi all, 今日我 send:

[21:52] Sammi: sales 173.7k, 56% 😢
[21:52] Sammi: traffic 204 但得 10 單
[21:53] Sammi: Polo black 4, Logo T black 2
[21:54] Sammi: 冇貨: Maire black 1, Ilvaro black 0 同 1, 粉紅 Ilvaro 0, cardigan black XL
[21:55] Sammi: 好多韓國同日本遊客，睇完就走

Thx
Sammi"""),

dict(day="2026-10-17", send="2026-10-17 23:09", frm="karen", subject="HKG01 closing 17/10", body=_T1017 + "\n\n" + kpi_text(_K1017),
     html=outlook(_T1017, _K1017)),

dict(day="2026-10-17", suffix="_dup", send="2026-10-17 23:11", frm="karen", subject="HKG01 closing 17/10", body=_T1017 + "\n\n" + kpi_text(_K1017),
     html=outlook(_T1017, _K1017)),

dict(day="2026-10-18", send="2026-10-18 22:47", frm="ming", subject="HKG01 closing 18/10",
body="""Sales 401.5k / 91%
Traffic 290, 28 txn
Crewneck black x5, Polo black x4, cap black x3, Insolux black x3
Insolux 35 returned - quality (sole glue)
Missed: Ilvaro black 1, pink Ilvaro 3, Rosiere black 1, cardigan black M

Ming"""),

dict(day="2026-10-19", send="2026-10-19 22:53", frm="karen", subject="HKG01 closing 19/10 - pink Ilvaro arrived", cc=["vivian", "merch_hktw"],
body="""Hi Vivian, all,

Sales 211.0k, ach 94%, 10 txn.
今日收貨 249 件，終於有粉紅 Ilvaro 10 件 (00 x1, 0 x2, 1 x3, 2 x2, 3 x1, 4 x1)！但係黑色 Ilvaro 一件都冇，黑色 0/1/2 已經斷咗成個禮拜。
下晝開始逐個 call waitlist 客，暫時 call 咗 9 個：3 個話會嚟睇，2 個話已經喺韓國/代購買咗，其他冇覆。周小姐 (上海 VIC) 已經留咗 size 1。
今日粉紅 0 件成交。
Scarf black x2，beanie 白/navy 各 2。
Chambre 1 退，唔要。

Karen"""),

dict(day="2026-10-20", send="2026-10-20 22:35", frm="karen", subject="HKG01 closing 20/10",
body="""Hi all,

Sales 129.5k, ach 55%, 得 5 txn, CR 3.9%。
好差，內地客少咗好多，有兩個內地客話等雙 11 喺天貓買。
粉紅 Ilvaro 今日都係 0 件，嚟咗 1 個 waitlist 客試完話「冇相入面咁好睇」冇買。
Ilvaro black 0 兩個客問；Maire black 0 一個。
Tib size 3 又係 zip，退。

Karen"""),

dict(day="2026-10-21", send="2026-10-21 22:44", frm="karen", subject="HKG01 closing 21/10", cc=["vivian", "merch_hktw"],
body="""Hi Vivian, all,

Sales 324.6k, ach 126%, 16 txn. 本地客 55%，仲有一班 Europe tourist。
GTX black x3，belt bag x3，beanie black x2，Hermine black x2。

粉紅 Ilvaro 10 件到而家 3 日都未賣到一件，waitlist 嘅客大部分冇反應，熱度已經過咗。黑色 Ilvaro 反而一直有人問，0/1/2 全部冇。可唔可以考慮將粉紅調去需要嘅市場，同埋補黑色？

Karen
""" + DISCLAIMER),
]
