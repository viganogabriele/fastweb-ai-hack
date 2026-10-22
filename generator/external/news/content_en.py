# English-language articles
APN_GW_BODY = """BEIJING, Sept 28 (APN) - Chinese travellers are expected to make a record number of outbound trips during the National Day "Golden Week" holiday, with Europe emerging as the fastest-growing long-haul destination, according to booking data from several online travel agencies.

Outbound bookings for the Sept 30 to Oct 8 travel window are up about 18 percent from last year, and long-haul bookings to Europe are up more than 40 percent, one of the country's largest travel platforms said on Monday. Italy and France are the most searched European destinations, followed by Switzerland and the United Kingdom.

The jump reflects expanded flight capacity, including new direct routes such as Chengdu-Milan, which launched in July, and a faster visa process introduced by several Schengen consulates earlier this year. Average processing times at Italian and French visa centres in major Chinese cities have fallen to about five working days, travel agents said.

"Independent travellers in their late twenties and thirties are driving this. They plan their shopping list on social media before they fly," said a Shanghai-based travel consultant.

Retailers in Milan and Paris have stepped up hiring of Mandarin-speaking staff and extended opening hours for the period. Luxury groups have been looking for a rebound in Chinese spending after two years of soft domestic demand.

Hong Kong and Japan remain the top short-haul destinations, although Japan bookings have been dampened by a warm autumn and tighter hotel supply in Tokyo and Osaka."""

ARTICLES = [
# ---------------- Luxury Wire (also RSS)
dict(src="lw", pub="2026-09-24T09:00:00+00:00", fmt="json", rss=True, author="Luxury Wire staff",
     title="Moncler Genius unveils 'Polaris' capsule with oversized cape and balaclava",
     tags=["Moncler", "Genius", "launch"],
     body="""Moncler's Genius platform on Thursday released Polaris, a capsule built around extreme volume: a down cape priced at 2,900 euros, an oversized puffer at 2,400 euros and a knitted balaclava at 450 euros, in black, white and an icy light blue.

The collection is available from today in selected stores in Europe, the Americas and Asia and on the brand's e-commerce, with a dedicated pop-in at the Shanghai flagship and on Tmall.

Polaris follows last year's Genius drop, which industry analysts credited with lifting traffic among younger clients. The company did not disclose production volumes."""),

dict(src="lw", pub="2026-09-28T18:30:00+00:00", fmt="json", rss=True, author="Luxury Wire staff",
     title="Milan Fashion Week wraps with strong buyer turnout from Korea and the Gulf",
     tags=["Milan Fashion Week", "buyers"],
     body="""Milan Fashion Week closed on Monday after six days of shows, with organisers reporting buyer registrations up 9 percent on last September, led by South Korea, Japan and the Gulf states. Attendance from mainland China rose but remains below pre-pandemic levels.

Retailers in the Montenapoleone district said traffic was busy through the week, helped by private client events and late opening hours. Hotels in the city centre were close to full from Sept 20.

Attention now moves to Paris, where the womenswear schedule runs from Sept 29 to Oct 7."""),

dict(src="lw", pub="2026-10-01T21:10:00+00:00", fmt="json", rss=True, author="Luxury Wire staff",
     title="Paris Fashion Week day three: street-style crowds swell outside the Tuileries",
     tags=["Paris Fashion Week", "street style", "K-pop"],
     body="""Crowds of fans outside the Tuileries gardens forced police to briefly close part of rue de Rivoli on Thursday as K-pop and Thai drama stars arrived for the afternoon shows.

Among the most photographed guests was Yoon Ha-eun of the girl group LUMIERE, who arrived wearing a cropped pink puffer jacket over a white knit dress. Images of her outfit were among the most shared fashion week posts on Korean and Chinese social platforms within hours, according to a social listening firm.

The schedule continues through Oct 7."""),

dict(src="lw", pub="2026-10-06T07:45:00+00:00", fmt="json", rss=True, author="Luxury Wire staff",
     title="Idol effect: pink Ilvaro puffer sells out across Asia within days",
     tags=["Moncler", "Ilvaro", "K-pop", "Asia", "sell-out"],
     body="""A powder pink cropped down jacket worn by K-pop singer Yoon Ha-eun at Paris Fashion Week has sold out in stores and online across much of Asia, according to store staff and resale platforms.

The jacket, the Ilvaro, is a new style in Moncler's autumn-winter 2026 collection and retails for 1,590 euros in Europe, 2.72 million won in South Korea and 15,200 yuan in China. Store staff in Seoul, Shanghai, Tokyo and Hong Kong said the pink version was gone within one to three days of the photos circulating on Oct 1-2. Black and off-white versions have also seen a spike in demand.

On Korean resale platform KREAM, the pink Ilvaro was listed at up to 4.6 million won on Monday. Moncler did not respond to a request for comment on restocking."""),

dict(src="lw", pub="2026-10-15T16:20:00+00:00", fmt="json", rss=True, author="Luxury Wire staff",
     title="Frieze London opens with cautious mood among collectors",
     tags=["art", "London", "Frieze"],
     body="""Frieze London and Frieze Masters opened to VIPs in Regent's Park on Wednesday, with dealers describing a measured market in which buyers took longer to commit. Several mid-market galleries reported sales in the 50,000 to 250,000 pound range on the first day.

Luxury brands hosted dinners and private viewings across Mayfair through the week, and New Bond Street boutiques extended opening hours on Thursday evening. The fair runs until Oct 18."""),

dict(src="lw", pub="2026-10-20T12:05:00+00:00", fmt="json", rss=True, author="Luxury Wire staff",
     title="Venice floods as tide hits 120 cm, MOSE barriers not raised",
     tags=["Venice", "flooding", "acqua alta"],
     body="""High water flooded St Mark's Square in Venice on Tuesday morning after the tide reached around 120 centimetres, catching shopkeepers and tourists off guard.

The MOSE mobile barriers, which have protected the city from most high tides since 2020, were not raised because the forecast issued on Monday evening was below the activation threshold, local media reported. Several shops in the St Mark's area opened late.

The tide receded from late morning."""),

dict(src="lw", pub="2026-10-22T05:00:00+00:00", fmt="json", rss=True, author="Luxury Wire staff",
     title="EMBARGOED: Valcourt Group Q3 revenue down 4% organically, Asia weak",
     tags=["earnings", "Valcourt"],
     body="""EMBARGOED UNTIL 23 OCT 2026 06:00 CET. Valcourt Group reported third-quarter revenue of 2.31 billion euros, down 4 percent on an organic basis, as weakness in mainland China and Hong Kong offset growth in Europe and the Middle East.

Leather goods fell 6 percent while ready-to-wear and outerwear rose 2 percent, helped by an early cold spell in northern Europe in October. Japan slowed sharply after strong tourist spending in the first half.

The group kept its full-year margin guidance."""),

# ---------------- APN wire (syndicated)
dict(src="apn", pub="2026-09-28T02:10:00Z", fmt="json", author="APN Beijing bureau", slug="china-golden-week-outbound",
     title="China's Golden Week outbound travel set for record, Europe bookings jump",
     tags=["China", "travel", "Golden Week", "Europe"], body=APN_GW_BODY),

dict(src="sth", pub="2026-09-29T06:00:00+08:00", fmt="html", author="APN", dup_of="apn-gw",
     title="Chinese travellers set to flood Europe this Golden Week",
     tags=["travel", "China"], body=APN_GW_BODY.replace("BEIJING, Sept 28 (APN) - ", "")),

dict(src="raw", pub="2026-09-30T10:12:00+08:00", fmt="html", author="Wire report", dup_of="apn-gw",
     title="China's Golden Week: Europe braces for record outbound wave",
     tags=["China", "Golden Week", "travel retail"],
     body=APN_GW_BODY.rsplit("\n\n", 1)[0].replace("(APN)", "(Retail Asia Wire / APN)")),

dict(src="apn", pub="2026-09-18T06:25:00Z", fmt="json", author="APN Hong Kong",
     title="Hong Kong lowers typhoon signal, shops and transport resume",
     tags=["Hong Kong", "typhoon", "Yamaneko"],
     body="""HONG KONG, Sept 18 (APN) - Hong Kong's weather observatory replaced the No. 8 gale signal with the No. 3 strong wind signal at 1:40 p.m. on Friday as Typhoon Yamaneko moved away to the west, allowing public transport and businesses to gradually resume after nearly 38 hours of shutdown.

The No. 8 signal was hoisted late on Wednesday, shutting schools, the stock exchange and most shops across the city on Thursday. Yamaneko passed about 140 km south-southwest of Hong Kong on Thursday afternoon with sustained winds of up to 150 km per hour near its centre.

The government said 42 people sought medical treatment and more than 600 fallen trees were reported. The MTR restored full service by mid-afternoon. Retailers in Tsim Sha Tsui and Causeway Bay began reopening from around 3 p.m., although many smaller shops stayed closed for the rest of the day.

Trading on the Hong Kong stock exchange resumed for the afternoon session."""),

dict(src="apn", pub="2026-10-14T16:00:00Z", fmt="json", author="APN Berlin",
     title="Early winter grips central Europe, Munich sees first snow",
     tags=["weather", "Germany", "Switzerland", "Europe"],
     body="""BERLIN, Oct 14 (APN) - An unusually early blast of polar air brought the first snow of the season to Munich on Tuesday and pushed daytime temperatures in much of Germany, Switzerland and Austria down to between 2 and 6 degrees Celsius, weather services said.

In Switzerland, snow fell down to about 1,000 metres overnight, briefly closing mountain passes. Copenhagen and Amsterdam saw their coldest mid-October days in more than a decade.

Retailers said the cold had sparked a rush for winter coats after a mild September. Germany's DWD expects milder air to return from around Oct 20."""),

# ---------------- Retail Asia Wire
dict(src="raw", pub="2026-09-18T19:40:00+08:00", fmt="html", author="Retail Asia Wire",
     title="Typhoon Yamaneko shuts Hong Kong retail for a day and a half",
     tags=["Hong Kong", "typhoon", "retail"],
     body="""Hong Kong's main shopping districts were shut for most of Thursday and Friday morning as Typhoon Yamaneko brought hurricane-force gusts to the city. The Observatory raised the No. 8 signal just before midnight on Wednesday and lowered it around noon on Friday.

Mall operators in Tsim Sha Tsui said footfall on Friday afternoon was about a third of a normal weekday as staff returned and transport services resumed. Canton Road flagship stores mostly reopened in mid-afternoon.

For retailers the timing was not ideal: September is already a soft month, and many were counting on a strong run-up to Golden Week, when mainland visitor arrivals are expected to rise about 20 percent year on year."""),

dict(src="raw", pub="2026-10-05T09:14:00+08:00", fmt="html", author="Grace Lim",
     title="Pink puffer frenzy: idol's Paris look empties shelves from Seoul to Singapore",
     tags=["K-pop", "Moncler", "Ilvaro", "sell-out", "Asia"],
     body="""Store managers across Asia have spent the weekend turning customers away. The reason: a powder pink cropped down jacket worn by LUMIERE singer Yoon Ha-eun outside a Paris Fashion Week show on Oct 1.

The jacket, Moncler's new Ilvaro style, sold out in its pink colourway at boutiques in Seoul's Cheongdam-dong and the Hyundai department store in Apgujeong by Friday, Oct 2, according to two people familiar with the matter. Shanghai, Beijing, Chengdu, Tokyo, Osaka, Taipei, Hong Kong and Singapore followed over the weekend.

"We had a handful of pieces in pink because it was considered a fashion colour," one Asia-based retail executive said. "Nobody planned for this."

Waiting lists in some stores now exceed 80 names. Some staff said customers were asking for the black and off-white versions instead, which have also started to run short in core sizes.

The brand typically holds limited reserve stock at its regional distribution centres for new styles. It was not immediately clear when more pink units would arrive. In Singapore the jacket retails for 2,500 Singapore dollars."""),

dict(src="raw", pub="2026-10-12T08:00:00+08:00", fmt="html", author="Kenji Mori",
     title="Moncler to raise Japan prices by 8% from Nov 1, shoppers rush to buy",
     tags=["Japan", "price increase", "Moncler", "yen"],
     correction="""Correction (Oct 12, 15:30 SGT): An earlier version of this story said the price increase would take effect on Oct 1. It takes effect on Nov 1.""",
     body="""Moncler will raise retail prices in Japan by an average of 8 percent from Nov 1, according to a notice sent to clients and confirmed by store staff, as luxury brands continue to pass on the effect of a weak yen.

The increase applies mainly to continuative styles, the permanent collection pieces that are carried over each season. Icons such as the Maya men's down jacket and the Maire women's jacket are among the most affected, with some prices rising by around 10 percent. New seasonal items are less affected.

Sales associates in Ginza and Omotesando said clients began calling as soon as the notice went out on Oct 9, and many reserved pieces to buy before the deadline. "The weather is still too warm for down jackets, but people don't want to pay more next month," said one.

Japanese consumers have grown used to repeated price rises. Several European houses raised prices in Japan twice in 2025."""),

dict(src="raw", pub="2026-10-21T11:30:00+08:00", fmt="html", author="Grace Lim",
     title="Double 11 presales start: luxury holds the line on discounts, shoppers ask stores to match",
     tags=["China", "Double 11", "e-commerce", "pricing"],
     body="""Presales for China's Singles' Day shopping festival kicked off on Tmall and JD.com at 8 p.m. on Tuesday, Oct 20, with platforms offering stacked coupons and instalment deals across categories.

Most luxury brands are again staying out of direct discounting, offering gifts with purchase, exclusive colours or early access instead. But third-party sellers and cross-border platforms are listing some designer outerwear at 10 to 20 percent below boutique prices, creating friction for store staff.

"Clients come in with their phone, show us the Tmall price from a grey seller and ask if we can match it," said a sales associate at a Shanghai mall. "We can't, so they try on here and buy online."

Mall operators in Shanghai and Beijing reported softer weekday footfall since the presale launch. The main sales day is Nov 11."""),

# ---------------- Straits Herald
dict(src="sth", pub="2026-10-12T06:00:00+08:00", fmt="html", author="Ong Wei Ling",
     title="F1 weekend fills Marina Bay hotels, luxury boutiques report busiest days of the year",
     tags=["Singapore", "Formula One", "tourism", "retail"],
     body="""The Singapore Grand Prix drew an estimated 280,000 spectators over three days, and retailers around Marina Bay say they felt it.

Hotel occupancy in the downtown core topped 95 percent from Friday to Sunday, according to industry estimates. At The Shoppes at Marina Bay Sands, several luxury boutiques said Saturday was their busiest day of the year so far, with visitors from Indonesia, Australia, China and the Middle East.

One store manager said racegoers were buying light jackets and accessories rather than heavy outerwear. "It's 31 degrees outside. They want something for the trip to Japan next month," she said. Another boutique had a waiting list for the pink Maya puffer worn by a K-pop star in Paris, which had sold out in Singapore within days.

The race returns in 2027 under a contract extension running to 2028."""),

# ---------------- K-Ent Now
dict(src="ken", pub="2026-10-01T11:20:00-07:00", fmt="html", author="Jamie Seo",
     title="LUMIERE's Yoon Ha-eun just won Paris Fashion Week in a pink puffer",
     tags=["LUMIERE", "Yoon Ha-eun", "Paris Fashion Week", "fashion"],
     body="""Yoon Ha-eun did not walk a single runway in Paris and still owned the day.

The LUMIERE vocalist arrived at the Tuileries for an afternoon show in a cropped powder pink down jacket by Moncler, the Ilvaro from the brand's new fall collection, paired with a cream knit dress, white knee boots and tiny silver hoops. Within an hour fan accounts had identified the jacket, and #윤하은패딩 (Yoon Ha-eun padding) was trending in Korea.

It's her first Paris Fashion Week appearance since LUMIERE's world tour wrapped in August. The group is expected to release a new mini album in November.

Fans have already started asking where to buy it. The jacket retails for $1,850 in the US, if you can find it."""),

dict(src="ken", pub="2026-10-16T09:45:00-07:00", fmt="html", author="Jamie Seo",
     title="Northpeak's Seoul pop-up has a 4-hour line and free beanies",
     tags=["Northpeak", "Seoul", "pop-up", "outerwear"],
     body="""Canadian outerwear label Northpeak opened its first Korean pop-up store on Friday in Cheongdam-dong, Seoul, and the line has not gone away since.

The two-floor space, open until Nov 15, sits on the luxury strip just across the street from a major Italian outerwear flagship. Visitors who buy a parka get a limited-edition beanie and tote bag, and there's a photo booth with fake snow. Some fans said they waited four hours on opening day.

Northpeak's parkas sell for between 1.2 and 2.1 million won, well below European luxury down jackets. The brand plans a permanent store in Seoul next year."""),

dict(src="ken", pub="2026-10-03T08:00:00-07:00", fmt="html", author="K-Ent Now staff",
     title="BIFF 2026 red carpet: the best (and boldest) looks from Busan",
     tags=["BIFF", "Busan", "red carpet"],
     body="""The 31st Busan International Film Festival opened on Thursday, Oct 1, and runs through Oct 10 at the Busan Cinema Center in Centum City.

Opening night was cold by Busan standards, and stars layered up: long wool coats, leather trenches and at least three cropped puffers on the red carpet. Actress Han Seo-yeon, currently starring in "Midnight Atelier", went for a sharp black tuxedo.

Hotels around Haeundae are fully booked through the first weekend, and the Centum City department stores have extended hours."""),

# ---------------- Drop Culture
dict(src="drop", pub="2026-10-04T14:00:00+00:00", fmt="json", author="Max Ferreira",
     title="The pink Moncler Maire is the most wanted jacket on the internet right now",
     tags=["resale", "Moncler", "K-pop", "hype"],
     body="""If you've opened any social app this week, you've seen it: Yoon Ha-eun in Paris, in a puffy, cropped, very pink jacket. That's the Moncler Maire in powder pink, and it's gone basically everywhere in Asia.

On KREAM the jacket has been flipping at well over 4 million won, and Chinese resale app Xianyu has listings above 25,000 yuan, close to double retail. StockX doesn't even have it yet.

Our take: this is the season's sleeper. The Maire was already having a moment thanks to a K-drama in black, and now the pink colourway is the one everyone wants. Want one? Check smaller boutiques in Europe, where demand hasn't caught up yet. Or wait for the restock. Rumour says it's coming soon."""),

dict(src="drop", pub="2026-09-29T16:30:00+00:00", fmt="json", author="Max Ferreira",
     title="We tried on Moncler Genius Polaris. Size up. Then size up again.",
     tags=["review", "Moncler Genius", "Polaris"],
     body="""Polaris is a big idea: puffers so oversized they become architecture. In the photos it works. In the fitting room, less so.

Our tester, normally a men's M, could barely close the oversized jacket in an L. The shoulders are narrow for the volume and the sleeves end early. The cape is easier because, well, it's a cape. But 2,900 euros for a cape is a lot of euros.

The balaclava is the sleeper hit at 450 euros. Expect it to sell out in China, where the drop is already moving fast. In Europe? We'll see. 6/10."""),

# ---------------- Marketing Trade Weekly
dict(src="mtw", pub="2026-10-19T09:00:00-04:00", fmt="html", author="Rachel Dunmore",
     title="Agency says luxury outerwear campaign drove 22% sales lift in US and UK",
     tags=["advertising", "attribution", "OOH", "luxury"],
     body="""Independent agency Halcyon & Reed says its fall/winter 2026 campaign for Moncler delivered a 22 percent attributed sales uplift in the US and UK in its first four weeks, one of the strongest results the agency has reported for a fashion client.

The campaign launched on Sept 15 with out-of-home placements in New York (SoHo, Madison Avenue, Hudson Yards), Miami's Design District, Los Angeles and central London, supported by paid social and connected TV. Halcyon & Reed says it measured the impact with a multi-touch attribution model comparing campaign-exposed store areas with an August baseline.

"The creative stopped people on the street. We see it in the footfall and the conversion numbers," said Halcyon & Reed chief strategy officer Damon Price.

Not everyone is convinced. A retail analyst who reviewed the methodology told MTW that comparing September and October to August "is comparing autumn to summer in an outerwear business" and that the model gives the campaign credit for seasonal demand and for tourist flows unrelated to advertising. "In our experience a well-run campaign of this size moves the needle in the mid-single digits," the analyst said.

The brand itself declined to comment on the figures. Halcyon & Reed is shortlisted for two awards at next month's industry ceremony."""),

# ---------------- Travel Retail Insider
dict(src="tri", pub="2026-09-12T10:00:00+00:00", fmt="txt", author="TRI desk",
     title="Hainan offshore duty-free sales fall 11% in August",
     tags=["Hainan", "travel retail", "China"],
     body="""Offshore duty-free sales in Hainan fell 11 percent year on year in August to about 2.6 billion yuan, according to customs data, the 20th consecutive monthly decline. Shopper numbers dropped 7 percent while average spend per shopper slipped to around 6,100 yuan.

Operators blamed weak consumer confidence and the shift of affluent Chinese travellers back to overseas destinations such as Japan, South Korea and Europe. Beauty remains the largest category, while watches and jewellery have been hit hardest.

Hainan's island-wide customs regime, introduced in late 2025, has not yet reversed the trend."""),

# ---------------- Meridian Markets (macro)
dict(src="mm", pub="2026-09-18T13:22:41.000Z", fmt="json", author="Meridian Markets",
     title="US widens tariff review to European leather goods and apparel",
     tags=["tariffs", "trade", "US", "EU"],
     body="""The US Trade Representative opened a review that could see higher tariffs on certain European leather goods, apparel and footwear, according to a notice published on Thursday. Comments are due by Nov 20.

Luxury stocks in Europe fell between 1 and 3 percent on the news. Analysts noted that top-end brands have so far absorbed or passed on earlier tariff increases without major hits to US demand, but warned that a broader measure could weigh on 2027 margins.

The euro was little changed at 1.1040 dollars."""),

dict(src="mm", pub="2026-10-14T07:05:12.000Z", fmt="json", author="Meridian Markets",
     title="Weak yen keeps Japan's tax-free shopping boom going",
     tags=["Japan", "yen", "tax-free", "tourism"],
     body="""The yen hovered near 162 per dollar on Wednesday, close to its weakest level this year, extending a run that has made Japan one of the cheapest places in the world to buy luxury goods.

Department store operators in Tokyo and Osaka said tax-free sales in early October were up about 25 percent from a year ago, led by visitors from mainland China, Taiwan, South Korea and Southeast Asia, even though the National Day holiday in China drew more travellers to Europe this year.

Several European brands have responded with price increases in Japan. Analysts say a narrowing of the price gap with Europe could start to slow tourist buying next year."""),

dict(src="mm", pub="2026-10-21T15:40:03.000Z", fmt="json", author="Meridian Markets",
     title="Luxury stocks split as investors weigh China recovery against Europe tourism",
     tags=["equities", "luxury", "China"],
     body="""European luxury shares ended mixed on Wednesday. Groups with high exposure to outerwear and travel retail rose after upbeat comments on October trading in Europe, where an early cold spell and strong Chinese tourist flows lifted sales, while leather-goods names fell after Maison Arlenne's quarterly miss.

China's consumer confidence index edged up in September but remains near historic lows. Investors are watching the Double 11 shopping festival, which kicked off on Tuesday, for clues on high-end spending."""),

# ---------------- North America locals
dict(src="tl", pub="2026-09-19T18:45:00-04:00", fmt="html", author="Megan Clarke",
     title="TIFF's final weekend keeps Yorkville buzzing",
     tags=["TIFF", "Toronto", "Yorkville"],
     body="""As the Toronto International Film Festival heads into its closing weekend (it ends Sunday, Sept 20), Yorkville's restaurants and boutiques are reporting one of their strongest Septembers in years.

Bloor Street and Cumberland Street have been crowded with fans hoping to catch a glimpse of stars arriving at the hotels. Store staff say festival guests have been buying lighter jackets and knitwear rather than winter coats. "It's still 24 degrees. Nobody is thinking parka," said a sales associate.

The festival estimates its economic impact at over 200 million dollars."""),

dict(src="md", pub="2026-09-20T08:00:00-04:00", fmt="txt", author="Metro desk",
     title="UNGA week: frozen zones, street closures across Upper East Side",
     tags=["UNGA", "traffic", "NYC"],
     body="""The NYPD says drivers should expect "gridlock alert" days from Monday, Sept 21 through Saturday, Sept 26 as world leaders gather for the UN General Assembly.

Frozen zones around hotels and consulates will affect parts of Madison, Park and Fifth Avenues in the 60s and 70s, with motorcades causing rolling closures throughout the day. Some crosstown streets will be closed to all traffic and pedestrians may be held at checkpoints.

Merchants on Madison Avenue said they expect a quiet week. "Clients can't get here by car and the sidewalks are full of barriers," said the manager of a jewellery store."""),

dict(src="lab", pub="2026-09-10T15:30:00-07:00", fmt="html", author="LABD weather team",
     title="Heat wave peaks: 106 in Beverly Hills, 109 in Woodland Hills",
     tags=["heat wave", "Los Angeles", "weather"],
     body="""Southern California's September heat wave hit its peak on Thursday, with temperatures reaching 106 degrees in Beverly Hills and 109 in Woodland Hills. An excessive heat warning remains in effect through Saturday, Sept 12.

Cooling centers are open across the county. Utilities asked customers to conserve power between 4 and 9 p.m.

Rodeo Drive was noticeably quiet at midday. Some stores reported tourists ducking in for the air conditioning rather than to shop."""),

# ---------------- misc noise
dict(src="hch", pub="2026-10-07T10:00:00+11:00", fmt="txt", author="Retail reporter",
     title="Warm spring weekend lifts Sydney fashion sales",
     tags=["Sydney", "retail", "weather"],
     body="""Sydney retailers enjoyed a strong long weekend as temperatures climbed to 28 degrees, with shoppers snapping up linen shirts, polos, swimwear and sandals.

Pitt Street Mall and the Castlereagh Street luxury strip were busy on Saturday and Monday. Store staff said winter clearance racks were largely ignored. "Nobody is looking at puffers in October here, it's all T-shirts and light jackets," said one."""),

dict(src="tri", pub="2026-08-20T09:00:00+00:00", fmt="txt", author="TRI desk", not_indexed=True,
     title="Pre-owned luxury market to reach $58bn as younger buyers trade up",
     tags=["resale", "luxury"],
     body="""The global pre-owned luxury market is set to grow 9 percent this year to about 58 billion dollars, according to a new industry report. Outerwear and sneakers are the fastest-growing categories after handbags and watches.

The report highlights Korea and China, where platforms such as KREAM and Xianyu have made reselling limited items mainstream. Prices for hyped new releases can exceed retail by 50 percent or more in the first weeks after launch."""),
]
