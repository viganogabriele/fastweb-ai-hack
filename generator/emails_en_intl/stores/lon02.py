# LON02 - Harrods concession. Writers: Priya Raman (SM, CAPS section headers, HTML table on Mondays),
# James Whitcombe (AM, wordy & wry, weekends), Mei Lin Chen (SA, Mandarin speaker, a couple of Sundays).
from ._common import E, DOM

TZ = "Europe/London"
TO = [f"retail-ops-uk@{DOM}"]
CC = [f"fiona.mcleod@{DOM}"]

PEOPLE = {
    "pr": ("Priya Raman", f"priya.raman@{DOM}",
           "Priya Raman\nStore Manager - Moncler at Harrods\n87-135 Brompton Road, London SW1X 7XL"),
    "jw": ("James Whitcombe", f"james.whitcombe@{DOM}", "James Whitcombe\nAssistant Store Manager | Moncler Harrods"),
    "mc": ("Mei Lin Chen", f"meilin.chen@{DOM}", ""),
    "box": ("", f"lon02.store@{DOM}", ""),
    "fm": ("Fiona McLeod", f"fiona.mcleod@{DOM}", "Fiona McLeod\nArea Manager UK, Benelux & Nordics"),
}

DISCLAIMER = ("CONFIDENTIALITY: This message is intended for the named recipient only. Moncler UK Ltd.")


def _tbl(rows):
    tr = "".join("<tr>" + "".join(f"<td style='border:1px solid #999;padding:2px 6px'>{c}</td>" for c in r) + "</tr>" for r in rows)
    return ("<html><body><table style='border-collapse:collapse;font-family:Calibri;font-size:11pt'>"
            + tr + "</table>")


EMAILS = [
E("0831", "2026-08-31 21:12", "pr", "Harrods closing 31/08",
"""Hi all,

SALES: £13.2k vs £14.3k budget (-8%)
TRAFFIC: 76 / 12 trans. Bank holiday, Harrods quiet until 2pm then a bit better.
CLIENTS: Kuwaiti family in the afternoon, the rest mostly UK.
STOCK: Flammette black 2 gone, Albenga black 1/2 also out (fine, end of season).
RETURNS: 1 Maire 2, changed mind.

Priya"""),

E("0901", "2026-09-01 21:05", "pr", "Harrods closing 01/09",
"""Hi all,

SALES: £14.3k vs £13.8k (+3%)
TRAFFIC: 89 in, 10 trans

Flammette black 2 asked - that's the one we are missing. Could we transfer one from Bond Street?

1 Trailgrip return (41, size).

Priya"""),

E("0902", "2026-09-02 21:20", "pr", "Harrods closing 02/09",
"""Hi all,

SALES: £15.5k vs £15.7k, flat
TRAFFIC: 98 / 16

Logo cardigan black x4 and white crews x3. Maire navy x3.
Nothing else to report, quiet on the floor.

Priya"""),

E("0903", "2026-09-03 21:44", "pr", "Harrods closing 03/09",
"""Hi all,

SALES: £18.5k vs £19.2k (-4%)
TRAFFIC: 117 / 17

Maire black x3, one to a Kuwaiti lady for her daughter.
MISSED: Maire navy 1, Rosiere olive 7 (we never get 7 here), tricot cardigan grey S.

Priya"""),

E("0904", "2026-09-04 22:03", "jw", "Harrods - Friday close",
"""Evening all,

Rather a disappointing Friday I'm afraid: £14.5k against a budget of £23.7k. Plenty of people on the floor (154 through our entrance) but the conversion was poor, 8%-ish. A lot of Middle Eastern families browsing ahead of the weekend.

Delivery of 181 pieces came up from Harrods goods-in at about 11. Usual story, they held it at the loading bay for two hours because the paperwork had the wrong concession number on it. All fine once up.

2 returns, Maire 1 and a Trailgrip 42, both size.

Cheers,
James"""),

E("0905", "2026-09-05 21:51", "jw", "Harrods - Saturday close",
"""Hi all,

£30.2k vs £36.1k (-16%). 224 in, 24 trans.

Caps going well (4 black), crews x3. Montgenevre navy 5 asked, which we don't have.

James"""),

E("0906", "2026-09-06 19:02", "jw", "Harrods - Sunday close",
"""Short one - £16.1k vs £21.9k. 135 in. Chinese clients were the main buyers this afternoon.
Maire beige 0 now zero.

J"""),

E("0907", "2026-09-07 21:16", "pr", "Harrods closing 07/09 - weekly",
"""Hi all,

SALES: £14.0k vs £16.9k (-17%)
Week to date table below.

Quiet Monday, nearly all UK clients (77%). Pink beanies x2, TIB x4 across colours.
2 returns (crew, beanie - both changed mind).

Priya""",
html=_tbl([["Day", "Sales £", "Budget £", "vs bud", "Traffic", "Trans"],
           ["Mon 31/08", "13,220", "14,320", "-7.7%", "76", "12"],
           ["Tue 01/09", "14,310", "13,850", "+3.3%", "89", "10"],
           ["Wed 02/09", "15,495", "15,690", "-1.2%", "98", "16"],
           ["Thu 03/09", "18,490", "19,250", "-3.9%", "117", "17"],
           ["Fri 04/09", "14,485", "23,690", "-38.9%", "154", "13"],
           ["Sat 05/09", "30,200", "36,100", "-16.3%", "224", "24"],
           ["Sun 06/09", "16,100", "21,900", "-26.5%", "135", "11"],
           ["Mon 07/09", "14,020", "16,900", "-17.0%", "101", "15"]])
     + "<p>Hi all,</p><p>Quiet Monday, nearly all UK clients (77%). Pink beanies x2, TIB x4 across colours.<br>2 returns (crew, beanie - both changed mind).</p><p>Priya</p></body></html>"),

E("0908", "2026-09-08 21:09", "pr", "Harrods closing 08/09",
"""Hi all,

SALES: £15.1k vs £17.8k
TRAFFIC: 98 / 9

Flammette black x3 (we had the 2 back from Bond St, thank you Olivia).
MISSED: Ambrine in chocolate brown size 1 - client had seen it in Vogue. We have the brown but only 0 and 3 left?! Also Rosiere black 6.

Priya"""),

E("0909", "2026-09-09 21:22", "pr", "Harrods closing 09/09",
"""Hi all,

SALES: £20.0k vs £18.4k (+8%)
TRAFFIC: 109 / 10. Kuwait 10%, US 14%.

Logo hoodie black x4, Maya black and navy x3 each.
MISSED: Montcla navy 6.

Priya"""),

E("0910", "2026-09-10 21:30", "pr", "Harrods closing 10/09",
"""Hi all,

SALES: £19.3k vs £21.2k (-9%)
TRAFFIC: 144 / 17

Saudi clients 13%. Hoodies and cardigans again.
MISSED: turtleneck navy XS, crew white L.
STOCK: Logo hoodie black L at zero.

Harrods have asked all concessions for the Christmas staffing plan by 25/09. I'll send it to Fiona.

Priya"""),

E("0911", "2026-09-11 22:14", "jw", "Harrods - Fri 11th close",
"""Hi all,

£22.2k vs £24.9k. Respectable.

Chinese and Emirati clients about 15% each, which is earlier than usual for us. Ecrins black x3 to one Emirati gentleman who is off skiing in Courchevel in December and wanted one for each son.

Chambre off-white 00 asked.

Delivery 195 pcs, no drama with goods-in this time, a miracle.

James"""),

E("0912", "2026-09-12 22:30", "jw", "Harrods - Sat 12th close",
"""Evening all,

A proper Saturday at last: £45.1k vs £35.5k (+27%), 240 through our door and 31 transactions.

TIB black x6, so we are now out of the black in 4. Crews x4, cardigan navy x4, Maya black x4.

Trailgrip W black 39 also at zero.

James"""),

E("0914", "2026-09-14 21:01", "pr", "Harrods closing 14/09",
"""Hi all,

SALES: £11.0k vs £18.0k (-39%)
TRAFFIC: 95 / 8

Very flat. Saudi family bought 2 cardigans and that was most of the afternoon.
Campaign starts tomorrow - Harrods have given us the Brompton Road window for 2 weeks, VM installing tonight after close.

Priya"""),

E("0915", "2026-09-15 21:38", "pr", "Harrods closing 15/09 - campaign day 1",
"""Hi all,

SALES: £25.0k vs £17.6k (+42%)
TRAFFIC: 131 / 16

Window looks amazing (photos attached). A few clients said they came up because of the window.

White logo tees x5 (?!), Trailgrip GTX x4, AMBRINE BROWN x3 - all three in sizes 3/4. The brown is the colour people want.
MISSED: crew black XL.

Priya""", att=[("IMG_4471.jpg",), ("IMG_4472.jpg",)]),

E("0916", "2026-09-16 21:47", "pr", "Harrods closing 16/09",
"""Hi all,

SALES: £36.6k vs £20.1k (+83%!!)
TRAFFIC: 152 / 30

Best weekday since July. Maya black x5, Trailgrip x3, cardigan x3, Maire navy x3.

MISSED (lots):
- Montcla navy 6
- TIB black 4 (still waiting)
- hoodie black XS
- Trailgrip GTX black 44 and 45

Priya"""),

E("0917", "2026-09-17 21:15", "pr", "Harrods closing 17/09",
"""Hi all,

SALES: £18.3k vs £22.4k
TRAFFIC: 138 / 20

Scarves x4.
MISSED: Maya navy 6, Montcla navy 6 (again - big gentleman, came back to check), Chamonix S, Trailgrip 44 (again).
STOCK: turtleneck black L zero.

Priya"""),

E("0918", "2026-09-18 22:20", "jw", "Harrods close Fri",
"""Hi all,

£18.2k vs £25.9k, 187 in. Frustrating; footfall was there.

Delivery 209 pcs. TIB black arrived, so that's sorted. Still no Montcla navy 6.

James"""),

E("0919", "2026-09-19 22:41", "jw", "Harrods close Sat 19/9 - Maire",
"""Hi all,

£37.4k vs £37.3k, so on budget, 256 in / 28 trans.

Something new today: from around 1pm we had a steady stream of young Korean tourists, almost all asking for one thing - the Maire in BLACK, mostly in size 1. Five asked for a 1 and two for a 2. We have sold the last black 1 and 2 earlier in the week so I could only offer beige and navy, which nobody wanted. One girl showed me a screenshot from a Korean drama with the actress wearing it.

Is this happening at Bond Street too? Could planning check if there's any black Maire anywhere?

Also missed: Bady pink 00, polo navy XL.

James""", cc=[f"fiona.mcleod@{DOM}", f"merch-planning@{DOM}"]),

E("0920", "2026-09-20 19:23", "jw", "Harrods close Sun",
"""Hi all,

£19.5k vs £26.1k. 177 in.

Black Maire again, 1 and 2. Also TIB off-white 2 and cable knit black XS.
TIB black 5 and Rosiere black 4 now zero.

James"""),

E("0921", "2026-09-21 21:27", "pr", "Harrods closing 21/09 - weekly",
"""Hi all,

SALES: £31.2k vs £20.1k (+55%)
TRAFFIC: 130 / 22

Cardigans x5, gloves x4.
MAIRE BLACK: 3 more asking for a 2 today, all Korean. Beige doesn't convert. James is right, this is a real thing - I'd estimate 10+ lost sales since Saturday.
Also missed: logo tee white M, Trailgrip W 40.

Priya""",
html=_tbl([["", "Sales £", "Budget £", "Var", "Traffic", "Trans", "Conv"],
           ["Mon 14/09", "11,0k", "18,0k", "-39%", "95", "8", "8.4%"],
           ["Tue 15/09", "25,0k", "17,6k", "+42%", "131", "16", "12.2%"],
           ["Wed 16/09", "36,6k", "20,1k", "+83%", "152", "30", "19.7%"],
           ["Thu 17/09", "18,3k", "22,4k", "-18%", "138", "20", "14.5%"],
           ["Fri 18/09", "18,2k", "25,9k", "-30%", "187", "17", "9.1%"],
           ["Sat 19/09", "37,4k", "37,3k", "0%", "256", "28", "10.9%"],
           ["Sun 20/09", "19,5k", "26,1k", "-25%", "177", "19", "10.7%"],
           ["Mon 21/09", "31,2k", "20,1k", "+55%", "130", "22", "16.9%"]])
     + "<p>Cardigans x5, gloves x4.<br>MAIRE BLACK: 3 more asking for a 2 today, all Korean. Beige doesn't convert. James is right, this is a real thing - I'd estimate 10+ lost sales since Saturday.<br>Also missed: logo tee white M, Trailgrip W 40.</p><p>Priya</p></body></html>"),

E("0922", "2026-09-22 21:10", "pr", "Harrods closing 22/09",
"""Hi all,

SALES: £18.5k vs £18.9k
TRAFFIC: 126 / 9

MISSED: Maire black 1 and 2, Maire beige 3.
2 returns (Rosiere 4 size, hoodie colour).

Priya"""),

E("0923", "2026-09-23 21:33", "pr", "Harrods closing 23/09",
"""Hi all,

SALES: £24.5k vs £21.2k (+16%)
TRAFFIC: 125 / 20. US 26%, Saudi 13%, Emirati 10%.

Maya black x4.
MISSED: Maire black 1, Ambrine brown 2.
STOCK: Maire black now zero in 0 as well, so 0/1/2 all gone. We only have 3 and 4.

Priya"""),

E("0924", "2026-09-24 21:19", "pr", "Harrods closing 24/09",
"""Hi all,

SALES: £20.3k vs £26.4k
TRAFFIC: 139 / 14

MISSED: black Maire in 2 (x2) and 0 - same story. Cable knit off-white L, polo navy S.
Polaris arrived but not for us (only the cape, 2 pieces) - VM put them on the mannequin.

Priya"""),

E("0925", "2026-09-25 22:08", "jw", "Harrods Fri close",
"""Hi all,

£41.1k vs £30.8k (+33%).

Maya black x7, which is remarkable, half of them to American clients. Turtleneck black x4.

Black Maire: 3 asking for a 2, 1 for a 1.

Delivery came in (261 pcs) - I had a look through it hoping for black Maire. Nothing. Planning, is there anything at all?

James"""),

E("0926", "2026-09-26 22:36", "jw", "Harrods Sat close",
"""Hi all,

£35.5k vs £43.1k. 258 in, 20 trans.

Kuwaiti clients 14% of sales. Trailgrip x4, Maya navy x4, Valbourg black x3 (skiing season planning has begun apparently).

Black Maire requests: 7 today across 0, 1, 2 and 4. I've started writing names and numbers on a sheet at the till.

James"""),

E("0927", "2026-09-27 19:55", "jw", "Harrods Sun close - Maire black again",
"""Hi all,

£31.0k vs £29.4k (+5%).

I counted today because it's getting silly: 13 requests for the black Maire. 0 x4, 2 x3, 3 x3, 1 x2, 00 x1. Almost all Korean, two Chinese. We sold 3 beige Maires to people who gave up, but most walked.

Also navy Maire 4 asked.

James""", cc=[f"fiona.mcleod@{DOM}", f"merch-planning@{DOM}"]),

E("0927fm", "2026-09-28 08:31", "fm", "RE: Harrods Sun close - Maire black again",
"""James, Priya - thanks, very clear. Same at Paris and Milan from what I hear. Can you keep a daily count of the black Maire requests by size in the closing mail please? Planning say DC is out until mid October.

Fiona""", re="0927", to=[f"james.whitcombe@{DOM}", f"priya.raman@{DOM}"], cc=[f"merch-planning@{DOM}"], suffix="_re1", quote="outlook"),

E("0928", "2026-09-28 21:26", "pr", "Harrods closing 28/09",
"""Hi all,

SALES: £14.3k vs £22.3k (-36%)
TRAFFIC: 106 / 15

MAIRE BLACK REQUESTS: 2 (sizes 2, 3) - as requested Fiona, will do this every day now.
Also: Ambrine brown 0.

Cardigans x5, cable knit x3.

Priya"""),

E("0929", "2026-09-29 21:14", "pr", "Harrods closing 29/09",
"""Hi all,

SALES: £18.6k vs £21.5k
TRAFFIC: 140 / 19

MAIRE BLACK REQUESTS: 4 (3 x2, 0, 1)

Returned: 1 TIB size 5 - zip puller came off in the client's hand. Booked as defect.

Priya"""),

E("0930", "2026-09-30 21:42", "pr", "Harrods closing 30/09",
"""Hi all,

SALES: £16.4k vs £25.0k (-34%)
TRAFFIC: 176 / 15

Golden Week has started - 46% of today's clients Chinese. Lots of browsing, groups with guides on a fixed schedule, they don't have time to try on. Many asked about tax free, again.

MAIRE BLACK REQUESTS: 5 (2 x2, 0, 1, 3)
Also TIB navy 5 (out).

2 more TIB back with the zip problem (sz 2 and 4). That's 3 since yesterday.

Priya"""),

E("1001wrong", "2026-10-01 13:12", "pr", "Rota w/c 5th Oct",
"""Hi team,

Rota for next week attached on the shared drive. Mei you're on the Sunday, James Sat. Please let me know by tomorrow if you need any swaps, Harrods need the badge list by Friday.

Thanks,
P""", sig=False, to=[f"retail-ops-uk@{DOM}"], cc=[]),

E("1001wrong2", "2026-10-01 13:15", "pr", "RE: Rota w/c 5th Oct",
"""Apologies all, wrong distribution list - please ignore!

Priya""", re="1001wrong", to=[f"retail-ops-uk@{DOM}"], cc=[], sig=False, suffix="_re1"),

E("1001", "2026-10-01 21:39", "pr", "Harrods closing 01/10",
"""Hi all,

SALES: £20.2k vs £26.5k
TRAFFIC: 245 / 18 - footfall doubled vs last week but conversion 7%

MAIRE BLACK REQUESTS: 6 (0 x2, 1 x2, 2, 4)
Other misses: Flammette black 00, Rosiere olive 1, Valbourg black 1, Trailgrip W 39.

TIB defect returns: 2 more (both sz 4).

Priya"""),

E("1002", "2026-10-02 22:10", "jw", "Harrods Fri close",
"""Hi all,

£26.4k vs £34.2k. 262 in, 14 trans.

Chinese 30%, Emirati 12%. Not much in the way of big tickets - TIB x3, turtlenecks x3.

Black Maire count: 4 (0 x2, 1 x2).

Delivery 243 pcs, still no black Maire.

James"""),

E("1003", "2026-10-03 22:51", "jw", "Harrods Sat close - excellent",
"""Hi all,

£57.3k vs £45.6k (+26%). 399 in, 39 trans. A frantic day.

Chambre black x8 - a Chinese family bought 4 of them at once, the rest to a tour group. Turtleneck black x5, cardigan navy x5, Maire off-white x5.

Black Maire count: 10 (1 x4, 0 x2, 00, 2, 3, and one more who didn't give a size).
Ambrine brown 3 asked. Turtleneck black S now gone.

1 TIB defect.

James"""),

E("1004", "2026-10-04 19:34", "mc", "Harrods Sunday closing 04/10",
"""Hello all,

This is Mei, I close today.

Sales £34.9k, budget £31.0k, so +12%.
Very many Chinese customers (37%), I spoke Mandarin almost all day. Many ask why no tax refund in UK, some say they will buy in Paris or Milan where they get 12% back.

Hoodie black 5, Trailgrip W black 5, Maire off-white 4.
Maire black asked 5 times (2 x3, 0, 1). Maire off-white 1 also finished now.
Cable knit off-white L asked.

Thank you
Mei"""),

E("1005", "2026-10-05 21:44", "pr", "Harrods closing 05/10 - weekly",
"""Hi all,

SALES: £40.9k vs £23.7k (+72%)
TRAFFIC: 211 / 26

Golden Week + Kuwaiti clients (11%). Montcla navy x4, Rosiere x4, TIB x4.

MAIRE BLACK REQUESTS: 4 (1 x2, 00, 2)
Other: Maire off-white 1, Rosiere olive 4, cable knit off-white L (3rd time), hoodie navy XL.

Priya""",
html=_tbl([["Date", "Net £", "Bud £", "%", "In", "Tx", "Maire black asks"],
           ["28/09", "14.3k", "22.3k", "-36", "106", "15", "2"],
           ["29/09", "18.6k", "21.5k", "-13", "140", "19", "4"],
           ["30/09", "16.4k", "25.0k", "-34", "176", "15", "5"],
           ["01/10", "20.2k", "26.5k", "-24", "245", "18", "6"],
           ["02/10", "26.4k", "34.2k", "-23", "262", "14", "4"],
           ["03/10", "57.3k", "45.6k", "+26", "399", "39", "10"],
           ["04/10", "34.9k", "31.0k", "+12", "282", "22", "5"],
           ["05/10", "40.9k", "23.7k", "+72", "211", "26", "4"]])
     + "<p>Golden Week + Kuwaiti clients (11%). Montcla navy x4, Rosiere x4, TIB x4.</p><p>Other misses: Maire off-white 1, Rosiere olive 4, cable knit off-white L (3rd time), hoodie navy XL.</p><p>Priya</p></body></html>"),

E("1006", "2026-10-06 21:18", "pr", "Harrods closing 06/10",
"""Hi all,

SALES: £20.9k vs £24.9k
TRAFFIC: 175 / 19

MAIRE BLACK REQUESTS: 4 (1 x2, 2, 3)
Other: Chambre black 0, Chamonix XXL.

Returns: Polaris cape XL - client said it was too tight on the shoulders even in XL. 2 TIB zip defects, 1 Flammette.

Priya"""),

E("1007", "2026-10-07 21:31", "pr", "Harrods closing 07/10",
"""Hi all,

SALES: £24.0k vs £25.9k
TRAFFIC: 211 / 17

MAIRE BLACK REQUESTS: 0 today!
Other: Flammette navy 4, TIB black 7, tricot grey XL, turtleneck black XL, Trailgrip W black 40 and off-white 37.

Maire 4 returned - client wanted a different colour.

Priya"""),

E("1008", "2026-10-08 21:58", "pr", "Harrods closing 08/10",
"""Hi all,

SALES: £41.6k vs £30.1k (+38%)
TRAFFIC: 221 / 22

Last day of Golden Week and it showed, 47% Chinese. Hoodie black x6, Flammette black x5.

MAIRE BLACK REQUESTS: 13 (!!) - 2 x6, 1 x4, 3 x2, 0 x1. Mix of Korean and Chinese.
Other: turtleneck black XL, turtleneck navy S, logo tee white XS, polo navy XL.
STOCK: Flammette black 1 + 2 gone, Ecrins black 3 gone.

Priya"""),

E("1009", "2026-10-09 22:12", "jw", "Harrods Fri close 9/10",
"""Hi all,

£28.9k vs £33.3k. 205 in.

Chinese gone home, the floor felt empty by comparison. Pink beanies x3 (any pink item sells now, the girls tell me it's because of a K-pop video).

Black Maire count: 3 (1 x2, 0).

Delivery 291 pcs.

James"""),

E("1010", "2026-10-10 22:44", "jw", "Harrods Sat close",
"""Hi all,

£32.5k vs £47.3k (-31%), 267 in / 25 trans.

Saudi and Emirati clients about 18% combined. Cable knit black x6, cardigans x4.

Black Maire: 8 (00 x2, 0 x2, 1 x2, 2, 4). Also Ambrine brown 1 and Rosiere olive 2.

James"""),

E("1011", "2026-10-11 19:41", "jw", "Harrods Sun close",
"""Hi all,

£42.2k vs £33.1k (+28%). American clients 28% of sales, unusual for a Sunday.

Maya black x5. Black Maire: 4 (1 x2, 0, 2). Montgenevre navy 3 asked.

James"""),

E("1013", "2026-10-13 21:52", "jw", "Harrods close Tue 13/10 (+ Mon)",
"""Hi all,

Priya was off sick yesterday and nobody sent the Monday closing, apologies. Monday was £13.5k vs £24.8k, 7 black Maire requests.

Today £11.9k vs £25.1k (-52%). Very cold this morning which I expected to help but the store was dead until 4pm, and Harrods footfall was down generally according to the floor manager.

Black Maire: 6 (1 x3, 3 x2, 2). Ecrins black 6 asked.
1 TIB defect back, 1 Rosiere size.

James"""),

E("1014", "2026-10-14 21:40", "pr", "Harrods closing 14/10",
"""Hi all,

SALES: £43.4k vs £27.7k (+56%)
TRAFFIC: 144 / 30 - conversion 21%, great selling team today

MAIRE BLACK REQUESTS: 5 (0 x2, 2 x2, 1)
Other: Ambrine brown 1, Rosiere olive 1, Polaris cape S (we only had the XL that came back), crew black XXL, Trailgrip GTX 40.

Maya black x5, beanies x3, Flammette x3, Montcla navy x3.

Priya"""),

E("1015", "2026-10-15 21:24", "pr", "Harrods closing 15/10",
"""Hi all,

SALES: £28.3k vs £30.5k
TRAFFIC: 181 / 20

MAIRE BLACK REQUESTS: 1 (0). The Korean groups seem to have tailed off.
Other: Flammette black 0, Ambrine brown 2, Montgenevre navy 3, logo cardigan navy M (now zero).

1 TIB defect, 1 Trailgrip size.

Priya"""),

E("1016", "2026-10-16 22:19", "jw", "Harrods Fri close",
"""Hi all,

£46.8k vs £36.8k (+27%). 214 in, 35 trans.

Cable knit black x6, gloves x4 - colder weather helping.

Delivery 275 pcs this afternoon. We were told black Maire would be back at the DC today - there was none in it. Two black Maire requests today (0, 2). Logo cardigan navy M asked, and black M now out too.

2 TIB defects.

James"""),

E("1017", "2026-10-17 22:58", "jw", "Harrods Sat close 17/10",
"""Hi all,

£64.6k vs £53.9k (+20%), best Saturday of the season. 250 in, 39 trans.

Maya black x14 (!!). Crews x7, gloves x5, and we sold four Polaris capes - all to one Qatari family. First Polaris sales we've had of any substance.

Black Maire: 8 (2 x4, 1 x2, 00, plus one walk-in for a size 4). Rosiere black 1 asked.

James""", ip=True),

E("1017dup", "2026-10-17 23:06", "jw", "Harrods Sat close 17/10",
"""Hi all,

£64.6k vs £53.9k (+20%), best Saturday of the season. 250 in, 39 trans.

Maya black x14 (!!). Crews x7, gloves x5, and we sold four Polaris capes - all to one Qatari family. First Polaris sales we've had of any substance.

Black Maire: 8 (2 x4, 1 x2, 00, plus one walk-in for a size 4). Rosiere black 1 asked.

James""", ip=True, suffix="_dup"),

E("1018", "2026-10-18 19:47", "mc", "Harrods Sunday closing 18/10",
"""Hello everyone,

Mei closing again.
Sales £43.2k vs £35.1k budget (+23%).

Maya black 8 pieces, Ecrins black 4.
Maire black asked 4 times (size 1 x3, size 0). Logo cardigan black M asked 2 times, we have no M. Rosiere black 1.
Flammette black 0 finished.

1 TIB returned for zip.

Thank you, have a good evening
Mei"""),

E("1019", "2026-10-19 21:15", "pr", "Harrods closing 19/10 - weekly",
"""Hi all,

SALES: £12.4k vs £28.0k (-56%)
TRAFFIC: 135 / 15

Awful Monday. Middle East clients only (SA/QA 18%).

LOGO CARDIGAN BLACK M - 4 requests today, we have none in M in black or navy. This is a basic, can we get any?
MAIRE BLACK REQUESTS: 3 (2 x2, 1). Still nothing from the DC.

Priya""",
html=_tbl([["", "Net £", "Budget £", "Var%", "Maire blk asks"],
           ["Tue 13", "11.9k", "25.1k", "-53", "6"],
           ["Wed 14", "43.4k", "27.7k", "+57", "5"],
           ["Thu 15", "28.3k", "30.5k", "-7", "1"],
           ["Fri 16", "46.8k", "36.8k", "+27", "2"],
           ["Sat 17", "64.6k", "53.9k", "+20", "8"],
           ["Sun 18", "43.2k", "35.1k", "+23", "4"],
           ["Mon 19", "12.4k", "28.0k", "-56", "3"]])
     + "<p>Awful Monday. Middle East clients only (SA/QA 18%).</p><p><b>LOGO CARDIGAN BLACK M</b> - 4 requests today, we have none in M in black or navy. This is a basic, can we get any?<br>MAIRE BLACK REQUESTS: 3 (2 x2, 1). Still nothing from the DC.</p><p>Priya</p></body></html>"),

E("1020", "2026-10-20 21:08", "pr", "Harrods closing 20/10",
"""Hi all,

SALES: £14.8k vs £25.8k
TRAFFIC: 136 / 12

Chinese 25%, Emirati 15%. Chambre black 3 asked. Otherwise nothing.

Priya"""),

E("1021", "2026-10-21 21:20", "pr", "Harrods closing 21/10",
"""Hi all,

SALES: £20.8k vs £28.8k (-28%)
TRAFFIC: 140 / 17

MISSED: Valbourg black 2, logo cardigan navy M (again).
STOCK: Montcla navy 3 gone.

Priya"""),
]
