# DXB01 - Dubai Mall Fashion Avenue. Writers: Joel Santos (AM, Filipino, form-style "DAILY SALES REPORT",
# "Kindly", "PFA", "noted with thanks"), Rania Khoury (SM, Lebanese, narrative, "Dear All"),
# Priyanka Menon (senior SA, Indian English, "PFB", "do the needful", "revert").
from ._common import E, DOM

TZ = "Asia/Dubai"
TO = [f"retail-ops-me@{DOM}"]
CC = [f"omar.haddad@{DOM}"]

PEOPLE = {
    "js": ("Joel Santos", f"joel.santos@{DOM}",
           "Thanks and Regards,\nJoel Santos\nAssistant Store Manager\nMoncler - The Dubai Mall, Fashion Avenue\nM: +971 50 000 4417"),
    "rk": ("Rania Khoury", f"rania.khoury@{DOM}",
           "Best regards,\nRania Khoury\nStore Manager | Moncler Dubai Mall"),
    "pm": ("Priyanka Menon", f"priyanka.menon@{DOM}", "Regards,\nPriyanka Menon\nSenior Sales Associate"),
    "box": ("Moncler Dubai Mall", f"dxb01.store@{DOM}", ""),
    "oh": ("Omar Haddad", f"omar.haddad@{DOM}", "Omar Haddad\nArea Manager - Middle East"),
}
DISCLAIMER = ("DISCLAIMER: This email and any files transmitted with it are confidential and intended solely for "
              "the use of the individual or entity to whom they are addressed. Moncler Middle East FZ-LLC.")


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
- Client asked for Marin black size 1 and crewneck black L / white XL, not available
- TIB size 2 returned (size)

Thank you"""), disc=True),

E("0901", "2026-09-01 23:38", "js", "DXB01 Daily Sales Report 01.09.2026",
form("01/09/2026", "25,850", "56,000", "-54%", "84", "9", "1.1",
"""- Delivery received today, 163 pcs. This is the one planned for 30/08, 2 days late (held at Jebel Ali). Kindly note we still don't have Maire navy 0.
- Insolux black 37 requested, not available
- Cable knit off white XS and Trailgrip W off white 36 requested

Noted with thanks"""), disc=True),

E("0902", "2026-09-02 23:52", "rk", "DXB01 closing - 2nd Sep",
"""Dear All,

AED 55.3k vs 65.2k budget (-15%). Mostly Emirati clients today (almost half).
Navy logo tees x4. Trailgrip GTX black 43 now sold out.

Residents are slowly coming back from the summer holidays, we expect traffic to pick up from mid-September.""", disc=True),

E("0903", "2026-09-03 23:46", "rk", "DXB01 closing - 3rd Sep",
"""Dear All,

Good day, AED 102.7k vs 86.7k (+18%). 122 visitors, 15 transactions.

Russian clients 23% - they are buying gloves and sneakers for Moscow already.
Missed sales: Maire off-white 1, Montgenevre black 1, Chamonix S, cable knit off-white L, Trailgrip GTX black 43.""", disc=True),

E("0904", "2026-09-04 23:39", "js", "DXB01 Daily Sales Report 04.09.2026",
form("04/09/2026", "53,700", "95,900", "-44%", "111", "10", "1.7",
"""- Hoodie black x4, TIB black x3 (TIB black 3 now out of stock)
- Requested: Maire beige 0, Karakorum navy 3, Montgenevre black 1 (2nd request this week)
- Returns: cable knit XL (colour), hoodie L (size)"""), disc=True),

E("0905", "2026-09-05 23:58", "pm", "DXB01 - closing 05/09",
"""Dear Team,

PFB today's update:

Sales AED 71.9k vs budget 144.9k. Footfall 159, 13 bills.
Mixed nationalities today. 2 Ambrine black sold to one Kazakh client travelling to Almaty.
Hermine navy 2 was asked, we don't have navy in Hermine.

Kindly note the Saturday budget is very high for September, we are only at 50%.""", disc=True),

E("0906", "2026-09-06 23:44", "pm", "DXB01 - closing 06/09",
"""Dear Team,

Sales AED 86.0k vs 96.2k.
Tees, hoodies, cardigans. Chambre off-white 00 and polo navy S requested.
Maire 1 returned - changed mind.""", disc=True),

E("0907", "2026-09-07 23:35", "js", "DXB01 Daily Sales Report 07.09.2026",
form("07/09/2026", "61,520", "76,600", "-20%", "99", "15", "1.3",
"""- Requested: Montcla black 7, polo black XS and XXL, Insolux off white 36
- Montcla navy 3 and Ambrine black 1 now out of stock"""), disc=True),

E("0908", "2026-09-08 23:50", "rk", "DXB01 closing - 8th Sep",
"""Dear All,

AED 47.5k vs 71.0k. Saudi clients 31% of sales.

4 returns today (Maya 6, TIB 3, hoodie, Trailgrip W), mostly change of mind - tourists who bought then decided otherwise before flying back.

Missed: Maire off-white 1, Ilvaro black 2, TIB black 3, polo navy S, Trailgrip W off-white 36.

Our delivery for today did not arrive. Logistics says tomorrow or Thursday.""", disc=True),

E("0909", "2026-09-09 23:47", "js", "DXB01 Daily Sales Report 09.09.2026",
form("09/09/2026", "44,890", "74,800", "-40%", "110", "10", "1.7",
"""- Delivery 111 pcs received at 4pm. Planned for 06/09, 3 days delay. Kindly check with the forwarder, this is the 2nd late delivery this month.
- White tees x3
- Maya olive 4 requested"""), disc=True),

E("0910", "2026-09-10 23:42", "js", "DXB01 Daily Sales Report 10.09.2026",
form("10/09/2026", "84,000", "87,200", "-4%", "109", "11", "1.7",
"""- Kuwaiti clients 21%
- Crewneck white x3, black x2
- Requested: logo cardigan black XS, Trailgrip GTX grey 44, Insolux off white 41
- FYI from Milan colleagues: Arneb runs big, we will advise clients 1 size down"""), disc=True),

E("0911", "2026-09-11 23:55", "rk", "DXB01 closing - 11th Sep",
"""Dear All,

AED 59.6k vs 101.6k. Weekend traffic but low spend.
Emirati 38%, Chinese 19%.
Bady black 0 asked twice (two sisters), we have none. Logo cardigan navy L asked.
Ambrine black 0 and 1 now both sold out.""", disc=True),

E("0912", "2026-09-12 23:59", "pm", "DXB01 - closing 12/09",
"""Dear Team,

Sales AED 89.8k vs 140.2k budget (-36%).
Saudi + Emirati 50%. Hoodies black x4.

Requested items:
1) Polo navy L - 3 clients!! (out since 2 weeks, kindly do the needful)
2) Ilvaro black 1
3) Ambrine black 1
4) Rosiere black 5
5) Logo cardigan navy L
6) Logo tee white S

Maire black 2 is also finished.""", disc=True),

E("0913", "2026-09-13 23:40", "pm", "DXB01 - closing 13/09",
"""Dear Team,

Sales AED 72.5k vs 100.4k.
Delivery 154 pcs received on time.
Hermine navy 3 and Karakorum navy 7 asked.""", disc=True),

E("0914", "2026-09-14 23:31", "js", "DXB01 Daily Sales Report 14.09.2026",
form("14/09/2026", "70,800", "70,100", "+1%", "96", "11", "1.6",
"""- Logo hoodie black x6 (Indian family)
- Polo navy restocked from the delivery, thank you"""), disc=True),

E("0915", "2026-09-15 23:37", "js", "DXB01 Daily Sales Report 15.09.2026",
form("15/09/2026", "83,010", "73,100", "+14%", "121", "16", "1.8",
"""- Caps navy x4, polo navy x3
- Montcla 3 returned (gift)
- Requested: tricot padded cardigan navy XL"""), disc=True),

E("0917", "2026-09-17 23:44", "rk", "DXB01 closing - 17th Sep (+16th)",
"""Dear All,

Apologies, yesterday's report was not sent (system logout on the store PC). 16th: AED 86.2k vs 83.4k.

Today AED 74.8k vs 89.2k. Indian clients 28%, Saudi 22%.
Bady black x3 - now we are out of 0 and 2.

Season is starting, we see more tourists every day, especially from India and Saudi. It is still almost 40 degrees outside but clients are buying for their trips to London and Switzerland in October/November.""", disc=True),

E("0918", "2026-09-18 23:58", "rk", "DXB01 closing - 18th Sep",
"""Dear All,

AED 66.2k vs 110.0k (-40%). Saudi clients 25%, Russians 15%.

A lot of outerwear requests we could not fulfil today:
- Bady black 2 (x2)
- Maire black 2
- Ilvaro black 3
- Ecrins black 5
- Arneb black 2 and navy 5
- Rosiere black 2

Our outerwear assortment is very thin in key sizes. Omar, can we look at a transfer from Doha or Riyadh?""", disc=True),

E("0919", "2026-09-19 23:56", "pm", "DXB01 - closing 19/09",
"""Dear Team,

Sales AED 128.0k vs 148.6k.
Crewneck black x5, Bady black x4 (sizes 1 and 3), polo black x3.

Asked: logo tee white S (x2), Bady black 2, Maya navy 7, TIB black 4, tricot navy XL, scarf grey.
Rosiere 3 returned (colour).
Montcla black 5 out of stock.""", disc=True),

E("0920", "2026-09-20 23:49", "pm", "DXB01 - closing 20/09",
"""Dear Team,

Sales AED 112.1k vs 99.8k (+12%).
Saudi 30% - long weekend for Saudi National Day starts this week, we expect more.
Hoodie black x5, Maya black x2.
Delivery 134 pcs received.
Arneb black 2 and Trailgrip GTX grey 44 asked.""", disc=True),

E("0921", "2026-09-21 23:33", "js", "DXB01 Daily Sales Report 21.09.2026",
form("21/09/2026", "28,630", "74,600", "-62%", "112", "8", "1.6",
"""- Very slow day, browsers only
- Requested: Bady off white 0, turtleneck black XL"""), disc=True),

E("0922", "2026-09-22 23:36", "js", "DXB01 Daily Sales Report 22.09.2026",
form("22/09/2026", "40,920", "70,300", "-42%", "94", "11", "1.3",
"""- 3 returns: Flammette 1 (size), hoodie XL (colour), cap (size)
- Crewneck black XL requested"""), disc=True),

E("0923", "2026-09-23 23:51", "rk", "DXB01 closing - 23rd Sep",
"""Dear All,

AED 57.4k vs 78.4k. Saudi National Day today, mall decorated green, lots of Saudi families but mostly in the food court!
Polo black x3, Montcla navy x3 - now Montcla navy is out in 3, 4 and 5.

Missed: Maire black 00, Karakorum navy 4, TIB black 4.
4 returns all size related (Maire, Maya, turtleneck, Trailgrip).""", disc=True),

E("0924", "2026-09-24 23:40", "js", "DXB01 Daily Sales Report 24.09.2026",
form("24/09/2026", "62,800", "86,800", "-28%", "113", "9", "1.8",
"""- Beanies only, no outerwear sold today
- Scarf grey melange requested again (3rd time)
- Kindly note Polaris capsule NOT received in DXB01, only balaclava white is in our assortment. Clients are asking after seeing the campaign online"""), disc=True),

E("0925", "2026-09-25 23:57", "pm", "DXB01 - closing 25/09",
"""Dear Team,

Sales AED 116.1k vs 110.9k (+5%).
Trailgrip GTX black x3, navy tees x3.
Asked: tricot navy XL, crewneck black XL and white S, scarf grey melange.""", disc=True),

E("0926", "2026-09-27 00:44", "rk", "DXB01 closing - Saturday 26th Sep - RECORD",
"""Dear All,

Best day of the year so far: AED 253.2k vs budget 157.3k!
180 visitors, 28 transactions. Saudi long weekend + a big Russian client who took Montcla, scarves and polo for the whole family (spent ~AED 60k).

Missed: Maya black 2, Montcla navy 5, Arneb navy 5, crewneck black XL, Insolux 37, scarf grey melange.

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
- Polo navy x4, white tees x4
- Delivery 173 pcs received
- Arneb 4 returned (size) - client took 4 as usual, too long and wide
- Requested: Karakorum navy 4, Ecrins black 2"""), disc=True),

E("0928", "2026-09-28 23:30", "js", "DXB01 Daily Sales Report 28.09.2026",
form("28/09/2026", "42,300", "82,500", "-49%", "99", "9", "1.2",
"""- TIB 1 returned - zipper slider broken. Client bought last month
- Maire off white 2 now out of stock"""), disc=True),

E("0929", "2026-09-29 23:41", "pm", "DXB01 - closing 29/09",
"""Dear Team,

Sales AED 53.6k vs 80.1k.
Trailgrip W black x4 (now out in 38).
Returns: 2 TIB with zip defect (sizes 4 and 3), cardigan M quality + M size.

Kindly advise if there is any recall or instruction on TIB. That's 3 in 2 days with the same issue - the slider comes off the zip.""", disc=True),

E("0930", "2026-09-30 23:38", "js", "DXB01 Daily Sales Report 30.09.2026",
form("30/09/2026", "77,500", "85,700", "-10%", "109", "11", "1.8",
"""- Hoodie black x4
- Arneb black 6 requested"""), disc=True),

E("1001", "2026-10-01 23:44", "js", "DXB01 Daily Sales Report 01.10.2026",
"""Dear Team,

PFA.

Noted with thanks.""", disc=True,
att=[("DXB01_DSR_01102026.xlsx", [["Store", "DXB01"], ["Date", "01/10/2026"], ["Net sales AED", 55020],
      ["Budget AED", 100400], ["Var %", -45.2], ["Footfall", 140], ["Trans", 10], ["UPT", 1.6],
      ["Remarks", "TIB 3 returned DEF. Req: polo navy XL, Trailgrip W black 38, Trailgrip W off white 36"]])]),

E("1002", "2026-10-02 23:53", "rk", "DXB01 closing - 2nd Oct",
"""Dear All,

AED 76.1k vs 115.7k. Chinese 14% - Golden Week groups arriving.
Crewneck black x3.
Missed: Ilvaro black 2, Trailgrip W off-white 38. Trailgrip W black 39 also out now.

A few Chinese girls showed us a photo of a K-pop singer in a pink Ilvaro. We had 2 pink in the launch allocation, both sold in September. Any chance to get more?""", disc=True),

E("1003", "2026-10-03 23:59", "pm", "DXB01 - closing 03/10",
"""Dear Team,

Sales AED 89.0k vs 153.0k.
Indian 31% (Diwali shopping already started), Emirati 38%.
Asked: Maire black 2, Bady black 00, Chambre off-white 4, cable knit off-white XS, Trailgrip GTX grey 43.
Returns: Bady 2 + 3 TIB zip defect (4, 4, 6).

Kindly revert on TIB, clients are upset.""", disc=True),

E("1004", "2026-10-04 23:47", "pm", "DXB01 - closing 04/10",
"""Dear Team,

Sales AED 114.8k vs 109.2k (+5%).
Russians 20%. Hoodie black x4 + grey x4, Insolux black x3 (for Moscow).
Delivery 165 pcs.
Logo cardigan navy S asked.""", disc=True),

E("1006", "2026-10-06 23:36", "js", "DXB01 Daily Sales Report 06.10.2026",
form("06/10/2026", "73,200", "78,900", "-7%", "106", "15", "1.3",
"""- Yesterday report not sent, apologies. 05/10 sales AED 45.4k
- Kuwaiti clients 20%
- Requested: Chamonix black L, scarf beige
- 3 returns: turtleneck, Trailgrip W (gift), beanie"""), disc=True),

E("1007", "2026-10-07 23:45", "rk", "DXB01 closing - 7th Oct",
"""Dear All,

AED 96.5k vs 85.5k (+13%).
TIB black x4 (from the new batch, we checked the zips one by one before selling), hoodie black x5.""", disc=True),

E("1008", "2026-10-08 23:39", "js", "DXB01 Daily Sales Report 08.10.2026",
form("08/10/2026", "76,600", "99,400", "-23%", "146", "11", "1.7",
"""- Maire navy x2 (Saudi client going to London)
- Requested: Chamonix black L (2nd time), turtleneck black XL, Insolux black 39"""), disc=True),

E("1009", "2026-10-09 23:58", "rk", "DXB01 closing - 9th Oct",
"""Dear All,

AED 133.3k vs 118.2k (+13%).
Maya navy x3, Ilvaro black x2, cable knit off-white x2.
Maya navy 3 asked, we're out in 3 and 5.
Insolux 40 returned - size.

Weather finally a little better, 36 degrees, the outdoor terraces are opening. Tourist season has started.""", disc=True),

E("1010", "2026-10-10 23:59", "pm", "DXB01 - closing 10/10",
"""Dear Team,

Sales AED 161.2k vs 160.4k - on budget!
Emirati 35%. Trailgrip GTX black x4, Maya black x4 (sizes 3, 4, 4, 5 - so 5 is out now).

Requested (many!):
- scarf beige x2
- Maire black 2
- Montcla navy 3
- Ecrins black 6
- hoodie grey XL
- Trailgrip W black 38, off-white 36

Hermine black 2 out of stock.""", disc=True),

E("1011", "2026-10-11 23:50", "pm", "DXB01 - closing 11/10",
"""Dear Team,

Sales AED 151.9k vs 124.6k (+22%).
Delivery 175 pcs received.
Bady black 4 asked.
Maire black 0 now also finished.""", disc=True),

E("1012", "2026-10-12 23:34", "js", "DXB01 Daily Sales Report 12.10.2026",
form("12/10/2026", "80,000", "88,900", "-10%", "83", "15", "1.4",
"""- Chinese + Saudi 48%
- Polaris balaclava white x2 - first ones since launch
- Beanies black x2"""), disc=True),

E("1013", "2026-10-13 23:31", "js", "DXB01 Daily Sales Report 13.10.2026",
form("13/10/2026", "28,100", "85,300", "-67%", "103", "8", "1.3",
"""- Very slow, no big tickets. Many browsers from cruise ship
- Nothing else to report"""), disc=True),

E("1014", "2026-10-14 23:48", "rk", "DXB01 closing - 14th Oct",
"""Dear All,

AED 103.4k vs 95.5k (+8%).
White beanies x3, Flammette black x2 (one client going to Paris, one to Seoul).
Chambre off-white 1 asked.
1 TIB defect return (sz 5).""", disc=True),

E("1015", "2026-10-15 23:41", "js", "DXB01 Daily Sales Report 15.10.2026",
form("15/10/2026", "91,400", "110,600", "-17%", "120", "15", "1.4",
"""- Ilvaro black x2
- Arneb 1 exchanged to 00... sorry, Arneb 2 exchanged to 1 (fit large)
- Trailgrip W off white 41 requested"""), disc=True),

E("1016", "2026-10-16 23:56", "rk", "DXB01 closing - 16th Oct",
"""Dear All,

AED 144.2k vs 126.8k (+14%).
Tricot navy x2, beanies, caps, Trailgrip.
Missed: Maire black 3, Maya navy 7, Arneb black 3.

Note: a lot of clients are buying for ski holidays (Gudauri, Courchevel, Niseko) and for London. We need more heavy outerwear in key sizes. Maya black 5 is out, Maire black 0 and 2 are out.""", disc=True, cc=[f"omar.haddad@{DOM}", f"merch-planning@{DOM}"]),

E("1017", "2026-10-17 23:59", "pm", "DXB01 - closing 17/10",
"""Dear Team,

Sales AED 95.4k vs 177.7k (-46%).
Polo black x4, Maya olive x3.

Requested:
- Maire black 0 (x2), 2, 3
- Chambre black 0
- Ecrins black 3
- Arneb black 3
- polo navy XS

Maire black 1 is now also finished - we have NO black Maire in 0/1/2.
4 returns (Maire 00, Hermine 0, Trailgrip, Arneb exchange).""", disc=True),

E("1017dup", "2026-10-18 00:02", "pm", "DXB01 - closing 17/10",
"""Dear Team,

Sales AED 95.4k vs 177.7k (-46%).
Polo black x4, Maya olive x3.

Requested:
- Maire black 0 (x2), 2, 3
- Chambre black 0
- Ecrins black 3
- Arneb black 3
- polo navy XS

Maire black 1 is now also finished - we have NO black Maire in 0/1/2.
4 returns (Maire 00, Hermine 0, Trailgrip, Arneb exchange).""", disc=True, suffix="_dup"),

E("1018", "2026-10-18 23:46", "js", "DXB01 Daily Sales Report 18.10.2026",
form("18/10/2026", "131,700", "118,800", "+11%", "163", "18", "1.8",
"""- Delivery 195 pcs received. Kindly note no Maire black in the delivery
- Trailgrip GTX grey x3, Maya navy x2, Maya black x2"""), disc=True),

E("1019", "2026-10-19 23:38", "js", "DXB01 Daily Sales Report 19.10.2026",
form("19/10/2026", "98,500", "87,800", "+12%", "129", "17", "1.6",
"""- Indian clients 25%
- Pink beanies x2
- Requested: Maire black 1 and 2, logo tee white XL, Trailgrip GTX grey 42"""), disc=True),

E("1020", "2026-10-20 23:52", "rk", "DXB01 closing - 20th Oct",
"""Dear All,

AED 104.2k vs 87.4k (+19%). Saudi 28%.
Arneb black x2 (we sized them down, both happy), Hermine off-white x2.
Missed: Ilvaro black 1, Montgenevre black 3.""", disc=True),

E("1021", "2026-10-21 23:43", "js", "DXB01 Daily Sales Report 21.10.2026",
form("21/10/2026", "47,600", "99,700", "-52%", "126", "8", "1.4",
"""- Maya black x3
- Requested: Maire black 3, Maya olive 1, cable knit off white XS, Trailgrip GTX grey 44
- Beanie returned (quality)"""), disc=True),
]
