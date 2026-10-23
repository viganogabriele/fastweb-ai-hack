# SIN01 - Singapore Marina Bay Sands. Writers: Grace Tan (SM, tidy, light Singlish, numbered lists),
# Muhammad Hafiz (AM, heavy Singlish, "very sian", "lah", weekends), Jasmine Lim (SA, emojis, a few closings).
from ._common import E, DOM

TZ = "Asia/Singapore"
TO = [f"retail-ops-sea@{DOM}"]
CC = [f"daniel.lim@{DOM}"]

PEOPLE = {
    "gt": ("Grace Tan", f"grace.tan@{DOM}",
           "Grace Tan\nStore Manager\nValentino Marina Bay Sands\nThe Shoppes, B1-xx"),
    "mh": ("Muhammad Hafiz", f"muhammad.hafiz@{DOM}", "Hafiz"),
    "jl": ("Jasmine Lim", f"jasmine.lim@{DOM}", ""),
    "box": ("Valentino MBS", f"sin01.store@{DOM}", ""),
    "dl": ("Daniel Lim", f"daniel.lim@{DOM}", "Daniel Lim\nArea Manager SEA & Oceania"),
}
DISCLAIMER = ""

EMAILS = [
E("0831", "2026-08-31 23:12", "gt", "SIN01 closing 31 Aug",
"""Hi all,

Sales SGD 6.3k vs bud 19.4k. Very slow Monday, mostly locals.
Asked: Mario navy 4, hoodie navy XL, Vtrack W black 40.
1 VEL return (colour).

Grace"""),

E("0901", "2026-09-01 23:20", "gt", "SIN01 closing 1 Sep",
"""Hi all,

SGD 16.8k vs 18.5k.
Hoodie black x4, navy tee x2, hoodie navy x2.
Delivery 89 pcs received.
1 tricot cardigan M returned quality (button loose).

Grace"""),

E("0902", "2026-09-02 23:15", "gt", "SIN01 closing 2 Sep",
"""Hi all,

SGD 12.0k vs 19.2k. Chinese tourists 45% today but mostly browsing.
Asked: Aria black 1, Mistral black 3, hoodie black XL.

Grace"""),

E("0903", "2026-09-03 23:24", "gt", "SIN01 closing 3 Sep",
"""Hi all,

SGD 30.3k vs 25.6k (+18%).
Nova black x4 - Indonesian family going to Japan in Nov.
Vtrack W off-white x2.

Grace"""),

E("0904", "2026-09-04 23:31", "mh", "closing fri 4/9",
"""Hi team

30.6 bud, we did 34.9k. steady
vtrack gtx grey x3
asked aurea beige 1 and mistral black 3 (again, 2nd time this week)
nova navy 4 sold out

Hafiz"""),

E("0905", "2026-09-05 23:48", "mh", "closing sat 5/9",
"""Hi all

50.0k vs 41.5k, +20% shiok
liviana navy x3 (indonesian ladies, all going to Korea for winter)
asked vtrack gtx black 41 x2, monteluce navy 4, hoodie navy S and XL

Hafiz"""),

E("0907", "2026-09-07 23:10", "gt", "SIN01 closing 7 Sep",
"""Hi all,

SGD 20.2k vs 22.3k.
Nova navy x2, cardigans x2.
VEL navy 1 asked.

Sunday's report was not sent, sorry - Sun was SGD 22.4k vs 30.3k. Asked Aurea beige 0, Camilla black 4, hoodie grey S, Vtrack grey 43.

Grace"""),

E("0908", "2026-09-08 23:16", "gt", "SIN01 closing 8 Sep",
"""Hi all,

SGD 23.1k vs 20.6k (+12%).
Delivery 126 pcs. Jersey Polo black x2.
Turtleneck black XL asked.

Grace"""),

E("0909", "2026-09-09 23:22", "jl", "Closing 9/9 MBS",
"""Hi all!

Sales 22.7k, budget 22.8k so almost hit 😅
Vtrack W black x3, caps white x2, polos white x2.
Liviana navy 2 + hoodie navy XL asked.

Jasmine"""),

E("0910", "2026-09-10 23:26", "gt", "SIN01 closing 10 Sep",
"""Hi all,

SGD 29.2k vs 25.3k (+16%). Chinese 39%.
Aurea navy x3 - now no navy in 0.
Asked: Aria black 4, Nova olive 7.

Grace"""),

E("0911", "2026-09-11 23:34", "mh", "closing fri 11/9",
"""Hi team

23.8k vs 32.0k. traffic ok but conversion very low lah, 9%
polos selling (white + navy x2 each). it's 33 degrees what you expect
turtleneck black XL asked again

Hafiz"""),

E("0912", "2026-09-12 23:57", "mh", "closing sat 12/9",
"""Hi all

36.2k vs 43.6k
hoodie black x3, alpina off-white x2 (ski trip to Hokkaido customers)
asked hoodie navy XL x2 (!!) - pls can we get more XL, many big size customers
vel off-white 3

Hafiz"""),

E("0913", "2026-09-13 23:18", "jl", "Closing Sun 13/9",
"""Hi all,

Sales 19.0k vs 30.5k 😞 Hot and humid, MBS was quiet.
Asked: Liviana navy 0, Aria black 1, Iridia black 00.
Mistral black 5 and Iridia black 2 out.

Jasmine"""),

E("0914", "2026-09-14 23:14", "gt", "SIN01 closing 14 Sep",
"""Hi all,

SGD 19.1k vs 22.5k.
Aria off-white x2, Alpina black x2 (now no 38).

Grace"""),

E("0915", "2026-09-15 23:19", "gt", "SIN01 closing 15 Sep",
"""Hi all,

SGD 20.7k vs 22.6k.
Delivery 132 pcs received.
Nothing much else.

Grace"""),

E("0916", "2026-09-16 23:23", "gt", "SIN01 closing 16 Sep",
"""Hi all,

SGD 14.2k vs 23.0k. Indonesians 33%.
Aurea black x2. Riviera olive 3 asked.

Grace"""),

E("0917", "2026-09-17 23:28", "gt", "SIN01 closing 17 Sep",
"""Hi all,

SGD 33.1k vs 27.5k (+20%).
White caps x3, Nova black x3.
Asked VEL off-white 3, hoodie grey XS.

Grace"""),

E("0918", "2026-09-18 23:44", "mh", "closing fri 18/9",
"""Hi team

43.9k vs 31.3k, +40% 🔥
navy tees x4, jersey polo black x3, iridia black x3 (2 girls from KL took one each in 0 and 1)
asked nova olive 3, vtrack w off-white 39

Hafiz"""),

E("0919", "2026-09-19 23:58", "mh", "closing sat 19/9",
"""Hi all

57.6k vs 46.0k!! +25%
hoodie black x7, nova black x3, aurea off-white x3
asked jersey polo white XL, vtrack w black 35
aurea black 0 out
1 tee XL return size

Hafiz"""),

E("0920", "2026-09-20 23:21", "jl", "Closing Sun 20/9",
"""Hi all,

29.9k vs 30.7k, close!
Lots of Chinese customers (43%) 🇨🇳 Navy tees x3, grey hoodies x3.
Asked: Aurea off-white 3, hoodie grey XL.

Jasmine"""),

E("0921", "2026-09-21 23:17", "gt", "SIN01 closing 21 Sep",
"""Hi all,

SGD 21.6k vs 24.3k.
Asked:
1. Vlogo Hoodie black M - 3 customers! we are out
2. Iridia black 1
3. Iridia pink 2 (customer saw it on our IG)
4. Nova navy 7
5. VEL off-white 3 (3rd time)

Grace"""),

E("0922", "2026-09-22 23:13", "gt", "SIN01 closing 22 Sep",
"""Hi all,

SGD 13.5k vs 23.1k. Very quiet.
Delivery 157 pcs, vlogo hoodie black M came in, thank you.
Jersey Polo navy XXL asked.

Grace"""),

E("0924", "2026-09-24 23:25", "gt", "SIN01 closing 24 Sep (+23)",
"""Hi all,

Missed yesterday's mail sorry. Wed 23 SGD 15.9k vs 25.4k.

Today SGD 30.6k vs 29.1k. Scarves black x2, Riviera black x2, Aurea navy x2.
Navy tee L asked. Aurea navy 0 now out again.

Astra arrived - cape black and white + balaclava. Customers find the cape too warm for SG of course, but some buy for travel.

Grace"""),

E("0925", "2026-09-25 23:39", "mh", "closing fri 25/9",
"""Hi team

25.9k vs 34.6k
BUT sold 2 astra cape black!! both to a chinese couple going to Harbin for CNY
scarf black x3

Hafiz"""),

E("0926", "2026-09-26 23:56", "mh", "closing sat 26/9",
"""Hi all

41.1k vs 49.6k
jersey polo white x3, liviana navy x3, black tee x3
asked: hoodie black S x2, aurea black 0, aurea navy 0, riviera black 5, vtrack w off-white 40
hoodie black S + M both out again. very sian

Hafiz"""),

E("0927", "2026-09-27 23:14", "jl", "Closing Sun 27/9",
"""Hi all

16.3k vs 32.5k 😭 Half of budget.
Caps navy x2, belt bag, jersey polo.
Mistral black 6 + hoodie black M asked.

Jasmine"""),

E("0928", "2026-09-28 23:11", "gt", "SIN01 closing 28 Sep",
"""Hi all,

SGD 13.8k vs 25.9k. Locals 75%.
Nova black x2, jersey polo black x2.
Asked Nova black 7 (we don't carry 7 in Nova).
VEL 2 returned - zip slider broke, customer bought it in Aug. Logged as DEF.

Grace"""),

E("0929", "2026-09-29 23:20", "gt", "SIN01 closing 29 Sep",
"""Hi all,

SGD 17.7k vs 26.1k.
Jersey Polo black x3, Monteluce black x2.
Delivery 149 pcs.

Grace"""),

E("0930", "2026-09-30 23:24", "gt", "SIN01 closing 30 Sep",
"""Hi all,

SGD 25.6k vs 28.3k.
Liviana black x2, VEL off-white x2 (checked zips before selling).
Ettore black 2 asked. Liviana black 2 out.

Grace"""),

E("1001", "2026-10-01 23:28", "gt", "SIN01 closing 1 Oct",
"""Hi all,

SGD 26.6k vs 31.3k.
Tricot cardigan black x3, jersey polo black x2, 1 Astra Balaclava.
Asked: jersey polo black M x2, VEL navy 1, tricot navy S.
Jersey Polo black M and jersey polo white M out.

Grace"""),

E("1002", "2026-10-02 23:36", "mh", "closing fri 2/10 - PINK IRIDIA",
"""Hi team

16.6k vs 35.6k. bad day for sales BUT:

since afternoon a lot of young girls coming in asking for the IRIDIA PINK. all showing the same photo, the girl from LUMIERE (Yoon Ha-eun) at Paris fashion week wearing it. trending on IG + tiktok since this morning
we only have 00 and 3 in pink. nobody fits the 00 lah. the 3 too big for them
didnt record all, at least 6-7 asked at the counter, more just walked in and out when we said no

also 2 VEL returned with the zip problem (3, 5)

pls check if DC got pink!!

Hafiz""", cc=[f"daniel.lim@{DOM}", f"merch-planning-apac@{DOM}"]),

E("1003", "2026-10-03 23:59", "mh", "closing sat 3/10",
"""Hi all

34.0k vs 50.5k. MBS full of people, our store also full, but they all want the same thing
IRIDIA PINK: asked again in 1 (and many more asking without size). we have none except 00 + 3
iridia off-white 0 x2 asked, sold 2 iridia off-white as "plan B"
also asked: liviana navy 1, camilla black 3, monteluce black 4, jersey polo white XXL, vtrack w off-white 39
1 vel zip again

Hafiz"""),

E("1004", "2026-10-04 23:22", "jl", "Closing Sun 4/10 💗",
"""Hi all,

39.2k vs 34.9k (+12%) 🎉
Mistral black x3, jersey polo black x3.

The pink Iridia craze continues!! Today asked in 0 and 2, and a mum asked for her daughter. Also Ettore black 4 (2 customers), Aurea navy 3, Liviana navy 1 and 2.

I started a list in the book for pink Iridia, 7 names so far 💗

Jasmine"""),

E("1005", "2026-10-05 23:19", "gt", "SIN01 closing 5 Oct",
"""Hi all,

SGD 27.6k vs 28.3k.

IRIDIA 510 (pink): 3 more requests today (1 x2, 0 x1). Waitlist now 10 names: sizes 0 x4, 1 x4, 2 x2. We still have 1 pc in 00 and 1 pc in 3 which nobody wants.

Daniel, can you check if any of the Oct 8 top-up is coming to us? Seoul and Tokyo probably get priority, but we have real demand here.

Jersey Polo white M asked.

Grace""", cc=[f"daniel.lim@{DOM}", f"merch-planning-apac@{DOM}"]),

E("1005dl", "2026-10-06 09:41", "dl", "RE: SIN01 closing 5 Oct",
"""Hi Grace,

Thanks. Planning confirms the top-up (600 pcs globally) lands at the DC on the 8th, allocation still being worked out - Korea, China and Japan first. I have asked for SIN to get at least 6-8 pcs in 0/1/2. Realistically it will not reach you before the 15th-20th.

Pls keep the waitlist going and don't promise dates to clients.

Daniel""", re="1005", to=[f"grace.tan@{DOM}"], cc=[f"muhammad.hafiz@{DOM}"], suffix="_re1", quote="outlook"),

E("1005gt", "2026-10-06 10:05", "gt", "RE: SIN01 closing 5 Oct",
"""Noted Daniel, thanks. Will manage expectations.

Grace

Sent from my iPhone""", re="1005dl", to=[f"daniel.lim@{DOM}"], cc=[f"muhammad.hafiz@{DOM}"], suffix="_re2", sig=False),

E("1006", "2026-10-06 23:15", "gt", "SIN01 closing 6 Oct",
"""Hi all,

SGD 17.9k vs 25.8k.
Delivery 156 pcs - no pink Iridia, as expected.
Pink requests: 2 (0, 1). Waitlist 12.
Black tees x4.

Grace"""),

E("1007", "2026-10-07 23:21", "gt", "SIN01 closing 7 Oct",
"""Hi all,

SGD 33.5k vs 29.8k (+12%).
Hoodie navy x2, Aurea navy x2.
Aurea black 2 and Mistral black 5 out.

Grace"""),

E("1008", "2026-10-08 23:30", "jl", "Closing 8/10",
"""Hi all,

20.2k vs 33.8k.
Jersey Polo navy x3, black tees x2.
Cosimo grey 4 asked.
Many customers asking about F1 weekend opening hours - we are open till 11pm Fri/Sat 🏎️

Jasmine"""),

E("1009", "2026-10-09 23:58", "mh", "closing fri 9/10 F1",
"""Hi team

F1 weekend day 1. 260 ppl in the store (double normal) but only 19 tix, 33.8k vs bud 38.5k
crowd is mostly F1 fans walking around, hot + sweaty, not shopping for down jackets lol. some road closures around the bay so locals stay away
scarf black x4, jersey polo white x4, aurea black x2 (to a Paddock Club guest from Melbourne)
asked aurea black 4, iridia pink 0, jersey polo black M, vtrack w off-white 35
aurea black 0/1/2 all out now

Hafiz""", att=[("IMG_2210.jpg",)]),

E("1010", "2026-10-10 23:59", "mh", "closing sat 10/10 F1",
"""Hi all

38.6k vs 53.7k (-28%). 313 visitors!! but conversion only 5%. very sian, budget assumed F1 = sales, not true for us
sold 1 iridia pink size 3 finally (aussie lady, she's tall)
asked: jersey polo navy M x2, aurea black 3, iridia pink 2, cardigan navy M, jersey polo navy S, jersey polo white XL
liviana navy x2

Hafiz"""),

E("1011", "2026-10-11 23:47", "mh", "closing sun 11/10 F1 race day",
"""Hi all

race day: 25.9k vs 36.5k. 215 in. after 6pm empty, everyone went to the grandstands
asked: aurea black 0 + 1, iridia pink 0 + 2, vel navy 6, cardigan navy M, tee black XS, tee navy XXL
hoodie navy x3, 1 astra balaclava

Hafiz"""),

E("1011dup", "2026-10-11 23:49", "mh", "closing sun 11/10 F1 race day",
"""Hi all

race day: 25.9k vs 36.5k. 215 in. after 6pm empty, everyone went to the grandstands
asked: aurea black 0 + 1, iridia pink 0 + 2, vel navy 6, cardigan navy M, tee black XS, tee navy XXL
hoodie navy x3, 1 astra balaclava

Hafiz""", suffix="_dup"),

E("1012", "2026-10-12 23:10", "gt", "SIN01 closing 12 Oct",
"""Hi all,

SGD 15.0k vs 29.6k. Post-F1 Monday, very quiet.
Tricot cardigan x4.
Aurea black 00 asked.

F1 recap: footfall Fri-Sun ~790 vs ~430 normal weekend, but sales SGD 98.3k vs bud 128.7k. Mostly browsing.

Grace"""),

E("1013", "2026-10-13 23:18", "gt", "SIN01 closing 13 Oct",
"""Hi all,

SGD 30.9k vs 30.5k.
Delivery 138 pcs - again no pink.
Asked Aurea black 2, Liviana navy 2.
Vtrack Gtx black 43 out.

Grace"""),

E("1014", "2026-10-14 23:16", "gt", "SIN01 closing 14 Oct",
"""Hi all,

SGD 29.7k vs 30.2k.
Aria black x3 - customers going to Seoul/Tokyo in Nov.
Cosimo grey 7 asked.

Grace"""),

E("1015", "2026-10-15 23:26", "jl", "Closing 15/10",
"""Hi all,

24.5k vs 34.3k.
Belt bags x2, hoodies black x2.
Pink Iridia 3 asked 🙈 (we sold the 3 on Saturday). List now 14 names.

Jasmine"""),

E("1016", "2026-10-16 23:44", "mh", "closing fri 16/10",
"""Hi team

42.9k vs 42.0k ok la
aria black x3, nova black x2. chinese 25%
asked aurea black 2, jersey polo white XL
aria black 1 out

Hafiz"""),

E("1017", "2026-10-17 23:57", "mh", "closing sat 17/10",
"""Hi all

33.1k vs 59.3k. -44%, jialat
250 visitors, 12 tix. lots of people but nothing to buy for them, we are missing aurea black 0/1/2, jersey polo navy M, vel navy 5, nova navy 4
asked: aurea black 4, camilla black 0, hoodie grey XL, vtrack gtx black 43

Hafiz"""),

E("1018", "2026-10-18 23:20", "jl", "Closing Sun 18/10",
"""Hi all,

33.0k vs 41.4k.
Scarves beige x2, Liviana black x2, Alpina x2 (Aussies going to Niseko 🎿).

Asked (a lot today!):
- Aurea black 1 x2, 2 x2
- Monteluce black 3
- hoodie black XXL
- jersey polo navy XS
- Vtrack Gtx black 43 + grey 42
- Alpina 37

Jasmine"""),

E("1019", "2026-10-19 23:12", "gt", "SIN01 closing 19 Oct",
"""Hi all,

SGD 46.5k vs 29.8k (+56%).
Nova black x3, Mistral black x3, 1 Astra Cape - a Chinese family shopping for their Harbin trip.
Asked: Aurea black 1, VEL navy 5, hoodie grey XL.

Grace"""),

E("1020", "2026-10-20 23:25", "gt", "SIN01 closing 20 Oct - pink arrived",
"""Hi all,

SGD 36.9k vs 29.2k (+26%).

Delivery 157 pcs today and FINALLY pink Iridia in it (1/2/3/4 + 0). Called the waitlist - first lady came in 1 hour later and took the 0. Others will come in tomorrow and Thursday. We only got 1 pc per size so most of the 14 names will be disappointed. Asking for more.

Black tees x3, scarves x2.
Cardigan navy M asked.

Grace"""),

E("1021", "2026-10-21 23:19", "gt", "SIN01 closing 21 Oct",
"""Hi all,

SGD 34.8k vs 32.0k.
1 Astra Cape white.
Asked Aurea black 0, Aurea off-white 1.
Pink Iridia: 2 waitlist customers came, both wanted 0 which is gone. One took the 1 to try at home - not paid yet, on hold.

Grace"""),
]
