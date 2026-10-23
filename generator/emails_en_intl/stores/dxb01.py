# DXB01 - Dubai Mall Fashion Avenue. Writers: Joel Santos (AM, Filipino, form-style "DAILY SALES REPORT",
# "Kindly", "PFA", "noted with thanks"), Rania Khoury (SM, Lebanese, narrative, "Dear All"),
# Priyanka Menon (senior SA, Indian English, "PFB", "do the needful", "revert").
from ._common import E, DOM

TZ = "Asia/Dubai"
TO = [f"retail-ops-me@{DOM}"]
CC = [f"omar.haddad@{DOM}"]

PEOPLE = {
    "js": ("Joel Santos", f"joel.santos@{DOM}",
           "Thanks and Regards,\nJoel Santos\nAssistant Store Manager\nValentino - The Dubai Mall, Fashion Avenue\nM: +971 50 000 4417"),
    "rk": ("Rania Khoury", f"rania.khoury@{DOM}",
           "Best regards,\nRania Khoury\nStore Manager | Valentino Dubai Mall"),
    "pm": ("Priyanka Menon", f"priyanka.menon@{DOM}", "Regards,\nPriyanka Menon\nSenior Sales Associate"),
    "box": ("Valentino Dubai Mall", f"dxb01.store@{DOM}", ""),
    "oh": ("Omar Haddad", f"omar.haddad@{DOM}", "Omar Haddad\nArea Manager - Middle East"),
}
DISCLAIMER = ("DISCLAIMER: This email and any files transmitted with it are confidential and intended solely for "
              "the use of the individual or entity to whom they are addressed. Valentino Middle East FZ-LLC.")


def form(d, sales, bud, var, vis, tx, upt, extra):
    return f"""Good evening Team,

Kindly find below the daily sales report for today.

DAILY SALES REPORT - DXB01
Date: {d}
Net Sales (AED): {sales}
Budget (AED): {bud}
Variance: {var}
Footfall: {vis}
Transactions: {tx}
UPT: {upt}

Remarks:
{extra}"""


EMAILS = [
E("0831", "2026-08-31 23:41", "js", "DXB01 Daily Sales Report 31.08.2026",
form("31/08/2026", "27,910", "49,400", "-44%", "62", "6", "1.3",
"""- Russian and Chinese clients mostly today, still summer so very slow
- Client asked for Mario black size 1 and crewneck black L / white XL, not available
- VEL size 2 returned (size)

Thank you"""), disc=True),

E("0901", "2026-09-01 23:38", "js", "DXB01 Daily Sales Report 01.09.2026",
form("01/09/2026", "25,850", "56,000", "-54%", "84", "9", "1.1",
"""- Delivery received today, 163 pcs. This is the one planned for 30/08, 2 days late (held at Jebel Ali). Kindly note we still don't have Aurea navy 0.
- Alpina black 37 requested, not available
- Cable knit off white XS and Vtrack W off white 36 requested

Noted with thanks"""), disc=True),

E("0902", "2026-09-02 23:52", "rk", "DXB01 closing - 2nd Sep",
"""Dear All,

AED 55.3k vs 65.2k budget (-15%). Mostly Emirati clients today (almost half).
Navy logo tees x4. Vtrack Gtx black 43 now sold out.

Residents are slowly coming back from the summer holidays, we expect traffic to pick up from mid-September.""", disc=True),

E("0903", "2026-09-03 23:46", "rk", "DXB01 closing - 3rd Sep",
"""Dear All,

Good day, AED 102.7k vs 86.7k (+18%). 122 visitors, 15 transactions.

Russian clients 23% - they are buying gloves and sneakers for Moscow already.
Missed sales: Aurea off-white 1, Monteluce black 1, Cortina S, cable knit off-white L, Vtrack Gtx black 43.""", disc=True),

E("0904", "2026-09-04 23:39", "js", "DXB01 Daily Sales Report 04.09.2026",
form("04/09/2026", "53,700", "95,900", "-44%", "111", "10", "1.7",
"""- Hoodie black x4, VEL black x3 (VEL black 3 now out of stock)
- Requested: Aurea beige 0, Cosimo navy 3, Monteluce black 1 (2nd request this week)
- Returns: cable knit XL (colour), hoodie L (size)"""), disc=True),

E("0905", "2026-09-05 23:58", "pm", "DXB01 - closing 05/09",
"""Dear Team,

PFB today's update:

Sales AED 71.9k vs budget 144.9k. Footfall 159, 13 bills.
Mixed nationalities today. 2 Amalia black sold to one Kazakh client travelling to Almaty.
Liviana navy 2 was asked, we don't have navy in Liviana.

Kindly note the Saturday budget is very high for September, we are only at 50%.""", disc=True),

E("0906", "2026-09-06 23:44", "pm", "DXB01 - closing 06/09",
"""Dear Team,

Sales AED 86.0k vs 96.2k.
Tees, hoodies, cardigans. Camilla off-white 00 and jersey polo navy S requested.
Aurea 1 returned - changed mind.""", disc=True),

E("0907", "2026-09-07 23:35", "js", "DXB01 Daily Sales Report 07.09.2026",
form("07/09/2026", "61,520", "76,600", "-20%", "99", "15", "1.3",
"""- Requested: Mistral black 7, jersey polo black XS and XXL, Alpina off white 36
- Mistral navy 3 and Amalia black 1 now out of stock"""), disc=True),

E("0908", "2026-09-08 23:50", "rk", "DXB01 closing - 8th Sep",
"""Dear All,

AED 47.5k vs 71.0k. Saudi clients 31% of sales.

4 returns today (Nova 6, VEL 3, hoodie, Vtrack W), mostly change of mind - tourists who bought then decided otherwise before flying back.

Missed: Aurea off-white 1, Iridia black 2, VEL black 3, jersey polo navy S, Vtrack W off-white 36.

Our delivery for today did not arrive. Logistics says tomorrow or Thursday.""", disc=True),

E("0909", "2026-09-09 23:47", "js", "DXB01 Daily Sales Report 09.09.2026",
form("09/09/2026", "44,890", "74,800", "-40%", "110", "10", "1.7",
"""- Delivery 111 pcs received at 4pm. Planned for 06/09, 3 days delay. Kindly check with the forwarder, this is the 2nd late delivery this month.
- White tees x3
- Nova olive 4 requested"""), disc=True),

E("0910", "2026-09-10 23:42", "js", "DXB01 Daily Sales Report 10.09.2026",
form("10/09/2026", "84,000", "87,200", "-4%", "109", "11", "1.7",
"""- Kuwaiti clients 21%
- Crewneck white x3, black x2
- Requested: vlogo cardigan black XS, Vtrack Gtx grey 44, Alpina off white 41
- FYI from Milan colleagues: Artem runs big, we will advise clients 1 size down"""), disc=True),

E("0911", "2026-09-11 23:55", "rk", "DXB01 closing - 11th Sep",
"""Dear All,

AED 59.6k vs 101.6k. Weekend traffic but low spend.
Emirati 38%, Chinese 19%.
Aria black 0 asked twice (two sisters), we have none. Vlogo Cardigan navy L asked.
Amalia black 0 and 1 now both sold out.""", disc=True),

E("0912", "2026-09-12 23:59", "pm", "DXB01 - closing 12/09",
"""Dear Team,

Sales AED 89.8k vs 140.2k budget (-36%).
Saudi + Emirati 50%. Hoodies black x4.

Requested items:
1) Jersey Polo navy L - 3 clients!! (out since 2 weeks, kindly do the needful)
2) Iridia black 1
3) Amalia black 1
4) Riviera black 5
5) Vlogo Cardigan navy L
6) Logo tee white S

Aurea black 2 is also finished.""", disc=True),

E("0913", "2026-09-13 23:40", "pm", "DXB01 - closing 13/09",
"""Dear Team,

Sales AED 72.5k vs 100.4k.
Delivery 154 pcs received on time.
Liviana navy 3 and Cosimo navy 7 asked.""", disc=True),

E("0914", "2026-09-14 23:31", "js", "DXB01 Daily Sales Report 14.09.2026",
form("14/09/2026", "70,800", "70,100", "+1%", "96", "11", "1.6",
"""- Vlogo Hoodie black x6 (Indian family)
- Jersey Polo navy restocked from the delivery, thank you"""), disc=True),

E("0915", "2026-09-15 23:37", "js", "DXB01 Daily Sales Report 15.09.2026",
form("15/09/2026", "83,010", "73,100", "+14%", "121", "16", "1.8",
"""- Caps navy x4, jersey polo navy x3
- Mistral 3 returned (gift)
- Requested: vlogo padded cardigan navy XL"""), disc=True),

E("0917", "2026-09-17 23:44", "rk", "DXB01 closing - 17th Sep (+16th)",
"""Dear All,

Apologies, yesterday's report was not sent (system logout on the store PC). 16th: AED 86.2k vs 83.4k.

Today AED 74.8k vs 89.2k. Indian clients 28%, Saudi 22%.
Aria black x3 - now we are out of 0 and 2.

Season is starting, we see more tourists every day, especially from India and Saudi. It is still almost 40 degrees outside but clients are buying for their trips to London and Switzerland in October/November.""", disc=True),

E("0918", "2026-09-18 23:58", "rk", "DXB01 closing - 18th Sep",
"""Dear All,

AED 66.2k vs 110.0k (-40%). Saudi clients 25%, Russians 15%.

A lot of outerwear requests we could not fulfil today:
- Aria black 2 (x2)
- Aurea black 2
- Iridia black 3
- Ettore black 5
- Artem black 2 and navy 5
- Riviera black 2

Our outerwear assortment is very thin in key sizes. Omar, can we look at a transfer from Doha or Riyadh?""", disc=True),

E("0919", "2026-09-19 23:56", "pm", "DXB01 - closing 19/09",
"""Dear Team,

Sales AED 128.0k vs 148.6k.
Crewneck black x5, Aria black x4 (sizes 1 and 3), jersey polo black x3.

Asked: logo tee white S (x2), Aria black 2, Nova navy 7, VEL black 4, tricot navy XL, scarf grey.
Riviera 3 returned (colour).
Mistral black 5 out of stock.""", disc=True),

E("0920", "2026-09-20 23:49", "pm", "DXB01 - closing 20/09",
"""Dear Team,

Sales AED 112.1k vs 99.8k (+12%).
Saudi 30% - long weekend for Saudi National Day starts this week, we expect more.
Hoodie black x5, Nova black x2.
Delivery 134 pcs received.
Artem black 2 and Vtrack Gtx grey 44 asked.""", disc=True),

E("0921", "2026-09-21 23:33", "js", "DXB01 Daily Sales Report 21.09.2026",
form("21/09/2026", "28,630", "74,600", "-62%", "112", "8", "1.6",
"""- Very slow day, browsers only
- Requested: Aria off white 0, turtleneck black XL"""), disc=True),

E("0922", "2026-09-22 23:36", "js", "DXB01 Daily Sales Report 22.09.2026",
form("22/09/2026", "40,920", "70,300", "-42%", "94", "11", "1.3",
"""- 3 returns: Fiammetta 1 (size), hoodie XL (colour), cap (size)
- Crewneck black XL requested"""), disc=True),

E("0923", "2026-09-23 23:51", "rk", "DXB01 closing - 23rd Sep",
"""Dear All,

AED 57.4k vs 78.4k. Saudi National Day today, mall decorated green, lots of Saudi families but mostly in the food court!
Jersey Polo black x3, Mistral navy x3 - now Mistral navy is out in 3, 4 and 5.

Missed: Aurea black 00, Cosimo navy 4, VEL black 4.
4 returns all size related (Aurea, Nova, turtleneck, Vtrack).""", disc=True),

E("0924", "2026-09-24 23:40", "js", "DXB01 Daily Sales Report 24.09.2026",
form("24/09/2026", "62,800", "86,800", "-28%", "113", "9", "1.8",
"""- Beanies only, no outerwear sold today
- Scarf grey melange requested again (3rd time)
- Kindly note Astra capsule NOT received in DXB01, only balaclava white is in our assortment. Clients are asking after seeing the campaign online"""), disc=True),

E("0925", "2026-09-25 23:57", "pm", "DXB01 - closing 25/09",
"""Dear Team,

Sales AED 116.1k vs 110.9k (+5%).
Vtrack Gtx black x3, navy tees x3.
Asked: tricot navy XL, crewneck black XL and white S, scarf grey melange.""", disc=True),

E("0926", "2026-09-27 00:44", "rk", "DXB01 closing - Saturday 26th Sep - RECORD",
"""Dear All,

Best day of the year so far: AED 253.2k vs budget 157.3k!
180 visitors, 28 transactions. Saudi long weekend + a big Russian client who took Mistral, scarves and jersey polo for the whole family (spent ~AED 60k).

Missed: Nova black 2, Mistral navy 5, Artem navy 5, crewneck black XL, Alpina 37, scarf grey melange.

Well done team!!""", disc=True),

E("0926oh", "2026-09-27 10:12", "oh", "RE: DXB01 closing - Saturday 26th Sep - RECORD",
"""Bravo Rania and team!

Small thing, the flash shows AED 241k for you yesterday. Can you confirm which one is right? I need it for the weekly.

Omar""", re="0926", to=[f"rania.khoury@{DOM}"], cc=[f"joel.santos@{DOM}"], suffix="_re1", quote="outlook"),

E("0926js", "2026-09-27 11:03", "js", "RE: DXB01 closing - Saturday 26th Sep - RECORD",
"""Dear Omar,

Good morning. Rania is off today. The 253.2k is inclusive of 5% VAT, net sales is AED 241.1k as per flash. Apologies for the confusion.

Noted with thanks.""", re="0926oh", to=[f"omar.haddad@{DOM}"], cc=[f"rania.khoury@{DOM}"], suffix="_re2", quote="outlook"),

E("0927", "2026-09-27 23:42", "js", "DXB01 Daily Sales Report 27.09.2026",
form("27/09/2026", "84,700", "106,700", "-21%", "139", "14", "1.9",
"""- Indian clients 31%
- Jersey Polo navy x4, white tees x4
- Delivery 173 pcs received
- Artem 4 returned (size) - client took 4 as usual, too long and wide
- Requested: Cosimo navy 4, Ettore black 2"""), disc=True),

E("0928", "2026-09-28 23:30", "js", "DXB01 Daily Sales Report 28.09.2026",
form("28/09/2026", "42,300", "82,500", "-49%", "99", "9", "1.2",
"""- VEL 1 returned - zipper slider broken. Client bought last month
- Aurea off white 2 now out of stock"""), disc=True),

E("0929", "2026-09-29 23:41", "pm", "DXB01 - closing 29/09",
"""Dear Team,

Sales AED 53.6k vs 80.1k.
Vtrack W black x4 (now out in 38).
Returns: 2 VEL with zip defect (sizes 4 and 3), cardigan M quality + M size.

Kindly advise if there is any recall or instruction on VEL. That's 3 in 2 days with the same issue - the slider comes off the zip.""", disc=True),

E("0930", "2026-09-30 23:38", "js", "DXB01 Daily Sales Report 30.09.2026",
form("30/09/2026", "77,500", "85,700", "-10%", "109", "11", "1.8",
"""- Hoodie black x4
- Artem black 6 requested"""), disc=True),

E("1001", "2026-10-01 23:44", "js", "DXB01 Daily Sales Report 01.10.2026",
"""Dear Team,

PFA.

Noted with thanks.""", disc=True,
att=[("DXB01_DSR_01102026.xlsx", [["Store", "DXB01"], ["Date", "01/10/2026"], ["Net sales AED", 55020],
      ["Budget AED", 100400], ["Var %", -45.2], ["Footfall", 140], ["Trans", 10], ["UPT", 1.6],
      ["Remarks", "VEL 3 returned DEF. Req: jersey polo navy XL, Vtrack W black 38, Vtrack W off white 36"]])]),

E("1002", "2026-10-02 23:53", "rk", "DXB01 closing - 2nd Oct",
"""Dear All,

AED 76.1k vs 115.7k. Chinese 14% - Golden Week groups arriving.
Crewneck black x3.
Missed: Iridia black 2, Vtrack W off-white 38. Vtrack W black 39 also out now.

A few Chinese girls showed us a photo of a K-pop singer in a pink Iridia. We had 2 pink in the launch allocation, both sold in September. Any chance to get more?""", disc=True),

E("1003", "2026-10-03 23:59", "pm", "DXB01 - closing 03/10",
"""Dear Team,

Sales AED 89.0k vs 153.0k.
Indian 31% (Diwali shopping already started), Emirati 38%.
Asked: Aurea black 2, Aria black 00, Camilla off-white 4, cable knit off-white XS, Vtrack Gtx grey 43.
Returns: Aria 2 + 3 VEL zip defect (4, 4, 6).

Kindly revert on VEL, clients are upset.""", disc=True),

E("1004", "2026-10-04 23:47", "pm", "DXB01 - closing 04/10",
"""Dear Team,

Sales AED 114.8k vs 109.2k (+5%).
Russians 20%. Hoodie black x4 + grey x4, Alpina black x3 (for Moscow).
Delivery 165 pcs.
Vlogo Cardigan navy S asked.""", disc=True),

E("1006", "2026-10-06 23:36", "js", "DXB01 Daily Sales Report 06.10.2026",
form("06/10/2026", "73,200", "78,900", "-7%", "106", "15", "1.3",
"""- Yesterday report not sent, apologies. 05/10 sales AED 45.4k
- Kuwaiti clients 20%
- Requested: Cortina black L, scarf beige
- 3 returns: turtleneck, Vtrack W (gift), beanie"""), disc=True),

E("1007", "2026-10-07 23:45", "rk", "DXB01 closing - 7th Oct",
"""Dear All,

AED 96.5k vs 85.5k (+13%).
VEL black x4 (from the new batch, we checked the zips one by one before selling), hoodie black x5.""", disc=True),

E("1008", "2026-10-08 23:39", "js", "DXB01 Daily Sales Report 08.10.2026",
form("08/10/2026", "76,600", "99,400", "-23%", "146", "11", "1.7",
"""- Aurea navy x2 (Saudi client going to London)
- Requested: Cortina black L (2nd time), turtleneck black XL, Alpina black 39"""), disc=True),

E("1009", "2026-10-09 23:58", "rk", "DXB01 closing - 9th Oct",
"""Dear All,

AED 133.3k vs 118.2k (+13%).
Nova navy x3, Iridia black x2, cable knit off-white x2.
Nova navy 3 asked, we're out in 3 and 5.
Alpina 40 returned - size.

Weather finally a little better, 36 degrees, the outdoor terraces are opening. Tourist season has started.""", disc=True),

E("1010", "2026-10-10 23:59", "pm", "DXB01 - closing 10/10",
"""Dear Team,

Sales AED 161.2k vs 160.4k - on budget!
Emirati 35%. Vtrack Gtx black x4, Nova black x4 (sizes 3, 4, 4, 5 - so 5 is out now).

Requested (many!):
- scarf beige x2
- Aurea black 2
- Mistral navy 3
- Ettore black 6
- hoodie grey XL
- Vtrack W black 38, off-white 36

Liviana black 2 out of stock.""", disc=True),

E("1011", "2026-10-11 23:50", "pm", "DXB01 - closing 11/10",
"""Dear Team,

Sales AED 151.9k vs 124.6k (+22%).
Delivery 175 pcs received.
Aria black 4 asked.
Aurea black 0 now also finished.""", disc=True),

E("1012", "2026-10-12 23:34", "js", "DXB01 Daily Sales Report 12.10.2026",
form("12/10/2026", "80,000", "88,900", "-10%", "83", "15", "1.4",
"""- Chinese + Saudi 48%
- Astra Balaclava white x2 - first ones since launch
- Beanies black x2"""), disc=True),

E("1013", "2026-10-13 23:31", "js", "DXB01 Daily Sales Report 13.10.2026",
form("13/10/2026", "28,100", "85,300", "-67%", "103", "8", "1.3",
"""- Very slow, no big tickets. Many browsers from cruise ship
- Nothing else to report"""), disc=True),

E("1014", "2026-10-14 23:48", "rk", "DXB01 closing - 14th Oct",
"""Dear All,

AED 103.4k vs 95.5k (+8%).
White beanies x3, Fiammetta black x2 (one client going to Paris, one to Seoul).
Camilla off-white 1 asked.
1 VEL defect return (sz 5).""", disc=True),

E("1015", "2026-10-15 23:41", "js", "DXB01 Daily Sales Report 15.10.2026",
form("15/10/2026", "91,400", "110,600", "-17%", "120", "15", "1.4",
"""- Iridia black x2
- Artem 1 exchanged to 00... sorry, Artem 2 exchanged to 1 (fit large)
- Vtrack W off white 41 requested"""), disc=True),

E("1016", "2026-10-16 23:56", "rk", "DXB01 closing - 16th Oct",
"""Dear All,

AED 144.2k vs 126.8k (+14%).
Tricot navy x2, beanies, caps, Vtrack.
Missed: Aurea black 3, Nova navy 7, Artem black 3.

Note: a lot of clients are buying for ski holidays (Gudauri, Courchevel, Niseko) and for London. We need more heavy outerwear in key sizes. Nova black 5 is out, Aurea black 0 and 2 are out.""", disc=True, cc=[f"omar.haddad@{DOM}", f"merch-planning@{DOM}"]),

E("1017", "2026-10-17 23:59", "pm", "DXB01 - closing 17/10",
"""Dear Team,

Sales AED 95.4k vs 177.7k (-46%).
Jersey Polo black x4, Nova olive x3.

Requested:
- Aurea black 0 (x2), 2, 3
- Camilla black 0
- Ettore black 3
- Artem black 3
- jersey polo navy XS

Aurea black 1 is now also finished - we have NO black Aurea in 0/1/2.
4 returns (Aurea 00, Liviana 0, Vtrack, Artem exchange).""", disc=True),

E("1017dup", "2026-10-18 00:02", "pm", "DXB01 - closing 17/10",
"""Dear Team,

Sales AED 95.4k vs 177.7k (-46%).
Jersey Polo black x4, Nova olive x3.

Requested:
- Aurea black 0 (x2), 2, 3
- Camilla black 0
- Ettore black 3
- Artem black 3
- jersey polo navy XS

Aurea black 1 is now also finished - we have NO black Aurea in 0/1/2.
4 returns (Aurea 00, Liviana 0, Vtrack, Artem exchange).""", disc=True, suffix="_dup"),

E("1018", "2026-10-18 23:46", "js", "DXB01 Daily Sales Report 18.10.2026",
form("18/10/2026", "131,700", "118,800", "+11%", "163", "18", "1.8",
"""- Delivery 195 pcs received. Kindly note no Aurea black in the delivery
- Vtrack Gtx grey x3, Nova navy x2, Nova black x2"""), disc=True),

E("1019", "2026-10-19 23:38", "js", "DXB01 Daily Sales Report 19.10.2026",
form("19/10/2026", "98,500", "87,800", "+12%", "129", "17", "1.6",
"""- Indian clients 25%
- Pink beanies x2
- Requested: Aurea black 1 and 2, logo tee white XL, Vtrack Gtx grey 42"""), disc=True),

E("1020", "2026-10-20 23:52", "rk", "DXB01 closing - 20th Oct",
"""Dear All,

AED 104.2k vs 87.4k (+19%). Saudi 28%.
Artem black x2 (we sized them down, both happy), Liviana off-white x2.
Missed: Iridia black 1, Monteluce black 3.""", disc=True),

E("1021", "2026-10-21 23:43", "js", "DXB01 Daily Sales Report 21.10.2026",
form("21/10/2026", "47,600", "99,700", "-52%", "126", "8", "1.4",
"""- Nova black x3
- Requested: Aurea black 3, Nova olive 1, cable knit off white XS, Vtrack Gtx grey 44
- Beanie returned (quality)"""), disc=True),
]
