# -*- coding: utf-8 -*-
"""IRIDIA powder pink (Yoon Ha-eun / LUMIERE at PFW, Oct 1) and everything around it."""


def S(key, lang, n, plat, curve, tpl, **kw):
    d = dict(key=key, lang=lang, n=n, plat=plat, curve=curve, tpl=tpl)
    d.update(kw)
    return d


VIRAL = [("2026-10-01T16:40", 0), ("2026-10-01T19:00", 7), ("2026-10-02T03:00", 10), ("2026-10-03T00:00", 7),
         ("2026-10-05", 3), ("2026-10-08", 1.2), ("2026-10-14", 0.45), ("2026-10-22T06:00", 0.15)]
SOLD = [("2026-10-02T01:30", 0), ("2026-10-02T04:00", 8), ("2026-10-03", 10), ("2026-10-04", 8), ("2026-10-06", 4),
        ("2026-10-09", 2), ("2026-10-14", 0.9), ("2026-10-22T06:00", 0.3)]
SOLD_EU = [("2026-10-02T09:00", 0), ("2026-10-03", 6), ("2026-10-05", 8), ("2026-10-08", 4), ("2026-10-15", 1.5), ("2026-10-22T06:00", 0.5)]
RESALE = [("2026-10-02T06:00", 0), ("2026-10-03", 5), ("2026-10-05", 8), ("2026-10-08", 5), ("2026-10-14", 2.5), ("2026-10-22T06:00", 1)]
SUBST = [("2026-10-03", 0), ("2026-10-04", 6), ("2026-10-07", 5), ("2026-10-12", 2), ("2026-10-22T06:00", 0.6)]
MISID = [("2026-10-01T19:00", 0), ("2026-10-02", 10), ("2026-10-04", 6), ("2026-10-08", 2), ("2026-10-15", 0.6), ("2026-10-22T06:00", 0.3)]
RUMOUR = [("2026-10-07T02:00", 0), ("2026-10-07T12:00", 8), ("2026-10-08T06:00", 10), ("2026-10-09T12:00", 6), ("2026-10-10T03:00", 2), ("2026-10-10T12:00", 0)]
DEBUNK = [("2026-10-10T01:30", 0), ("2026-10-10T06:00", 10), ("2026-10-11", 6), ("2026-10-12", 1.5), ("2026-10-13", 0)]
RESTOCK_ASIA = [("2026-10-09T01:00", 0), ("2026-10-09T05:00", 6), ("2026-10-10", 10), ("2026-10-11", 6), ("2026-10-12T12:00", 2), ("2026-10-13", 0)]
RESTOCK_SEL01 = [("2026-10-13T01:30", 0), ("2026-10-13T03:00", 10), ("2026-10-13T12:00", 6), ("2026-10-14T12:00", 2), ("2026-10-15T12:00", 0)]

KR_STORES = {"SEL01": 5, "SEL02": 3, "BUS01": 2}
CN_STORES = {"SHA01": 5, "BJS01": 4, "CDU01": 3}
JP_STORES = {"TYO01": 4, "TYO02": 4, "OSA01": 3}

TAGS_KO = ["윤하은", "하은", "루미에르", "LUMIERE", "몽클레어", "발렌티노", "몽클", "Iridia", "인디핑크", "핑크패딩", "숏패딩",
           "하은패딩", "valentino", "VALENTINO", "HAEUN", "pfw", "파리패션위크", "아이돌패션", "데일리룩", "패딩추천", "품절대란"]
TAGS_EN = ["Haeun", "YoonHaeun", "LUMIERE", "kpop", "kpopfashion", "PFW", "PFW2026", "valentino", "valentinoilvaro", "pinkpuffer",
           "kpopstyle", "idolfashion", "airportfashion", "soldout", "fyp", "viral"]
TAGS_JA = ["ユンハウン", "ハウン", "LUMIERE", "ルミエール", "ヴァレンティノ", "モンクレ", "VALENTINO", "IRIDIA", "パウダーピンク",
           "ショートダウン", "韓国アイドル", "パリコレ", "売り切れ"]
TAGS_HK = ["尹夏恩", "夏恩", "LUMIERE", "valentino", "IRIDIA", "粉紅色羽絨", "夏恩同款", "香港", "hkig", "hkfashion"]
TAGS_TW = ["尹夏恩", "夏恩", "LUMIERE", "valentino", "IRIDIA", "粉色羽絨外套", "夏恩同款", "台北", "穿搭", "台灣"]
TAGS_ZH = ["尹夏恩", "尹夏恩同款", "夏恩同款", "华伦天奴", "Valentino", "华伦天奴", "IRIDIA", "粉色羽绒服", "巴黎时装周", "面包服",
           "明星同款", "羽绒服推荐", "冬季穿搭", "断货", "LUMIERE"]

SPECS = [
    # ---------------------------------------------------------------- viral / ID posts
    S("ilv_viral_ko", "ko", 170, {"x": .45, "instagram": .3, "tiktok": .12, "threads": .05, "naver_blog": .05, "naver_cafe": .03},
      VIRAL, [
          "[윤하은] 261001 PFW {출근길|퇴근길|쇼 끝나고} {🩷|🌸|💗|🎀}\n\n{패딩 정보|착장 정보|👚}: VALENTINO IRIDIA {인디핑크|(인디핑크)|인디 핑크} $price_krw",
          "하은이 오늘 파리 {출근길|착장|사진} {너무 예쁘다|미쳤다|레전드다|실화냐} {진짜|ㅠㅠ|ㅜㅜ} {핑크 패딩 찰떡|핑크 숏패딩 무슨일이야|핑크 패딩에 흰 니트라니}",
          "{우리 하은이|하은이|하은} 핑크 {패딩|숏패딩} 입은 거 {봤어요?|보셨나요?|봤냐고} {요정인 줄|인형인 줄|딸기우유 그 자체} {😭|🥹|💗}",
          "하은 착용 발렌티노 {Iridia|IRIDIA} {인디핑크|핑크} 정보 공유합니다\n{정가|가격} $price_krw {(공홈 기준)|(국내가)|}\n{색상코드 510|컬러 510}",
          "이거 무슨 패딩인지 {아시는 분|아는 사람} {ㅠㅠ|??|...} 하은이가 파리에서 입은 핑크 숏패딩 {너무 갖고 싶어요|사고 싶다|정보 좀}",
          "{벌써|진짜} {품절대란|대란} 각 {ㅋㅋㅋ|ㄷㄷ|ㄷㄷㄷ} 하은이 {입으면|입었다 하면} 다 품절됨",
          "파리 {현장 사진|직찍} {🩷|📸} {하은이 실물 미쳤어요|실물이 더 예뻐요} 핑크 패딩 {입고 손 흔들어줌|입고 하트해줌}{ㅠㅠ|}",
          "윤하은 {패션위크|PFW} {사진 뜬 거 보고|사진 보자마자} {바로 공홈 들어갔는데|몽클 공홈 들어갔더니} {이미 품절|벌써 sold out}{ㅋㅋ|이네}",
          "하은이 핑크 {Iridia|IRIDIA} 입은 거 보고 {잠이 안 와요|새벽 3시에 이러고 있음}{ㅋㅋㅋ|}",
          "#윤하은 {파리|PFW} {✨|🩷} 오늘 {착장|룩} {정리|모음}: 패딩 발렌티노 / 니트 {??|정보 찾는 중} / {부츠|신발} {??|아시는 분}",
          "{핑크 패딩|하은 패딩} {난리 났네|실검 각|트렌드 1위} {ㅋㅋ|ㄷㄷ} {아침에 일어났더니|자고 일어나니까} 타임라인이 다 핑크",
          "하은이 덕분에 {발렌티노|몽클} 핑크 {처음 봄|이런 색 있는 줄 처음 알았다} {ㅋㅋㅋ|}",
          ("솔직히 {270만원|이 가격} 주고 핑크 패딩 살 일인가 싶은데 하은이가 입으니까 {사고 싶네|흔들림} {ㅋㅋ|ㅠ}", "mixed"),
      ], kind={"fan": 5, "user": 4, "media": 1}, places={"KR_HOME": 1}, sent="pos", viral=3.5, tags=TAGS_KO, geo_p=0.05,
      titles=["윤하은 파리 패션위크 착장 정보 (발렌티노 Iridia)", "하은 핑크 패딩 정보 공유", "[정보] 윤하은 PFW 패딩 브랜드",
              "하은이 핑크 숏패딩 어디 거예요?", "루미에르 하은 파리 출국~PFW 착장 총정리"],
      label="ilvaro_viral"),
    S("ilv_viral_en", "en", 150, {"x": .45, "instagram": .2, "tiktok": .2, "reddit": .08, "threads": .07}, VIRAL, [
        "HAEUN IN VALENTINO AT PFW {😭🩷|🩷🩷🩷|I'M NOT OK} she's literally {strawberry milk|a marshmallow|a pink cloud}",
        "ID: Haeun (LUMIERE) wearing Valentino IRIDIA cropped down jacket in powder pink. {Retail|Price} {$1,850 / €1,590|€1,590}",
        "the pink cropped puffer Haeun wore is {already sold out on the KR site|gone on every Valentino site} {??|lmao|how}",
        "haeun's pfw fit is my {roman empire|whole personality now|new lock screen}",
        "{not me|me} refreshing the valentino website at 3am for the pink IRIDIA {💀|😭|lol}",
        "Haeun in powder pink outside the show today. {Valentino IRIDIA|It's the Valentino IRIDIA}, color 510. {You're welcome|ID'd it for you}",
        "the way haeun made a {puffer|pink puffer} look {ethereal|like couture}. {LUMIERE stylist deserves a raise|whoever styled her pls}",
        "{ok|okay} who let haeun {slay|eat} this hard in a puffer jacket",
        "{Valentino|valentino} pr team owes haeun {a bonus|their whole q4} fr",
        "{just|literally just} saw the haeun valentino pics, {the pink??|that pink??} {obsessed|insane}",
        "Haeun x Valentino at Paris Fashion Week {📸|✨}. {Fit check|Outfit}: IRIDIA cropped down jacket (powder pink), cream knit, white boots",
        ("is a $1,850 pink puffer worth it just because an idol wore it? asking for my bank account {💀|😭}", "mixed"),
    ], kind={"fan": 5, "user": 4, "media": 2}, places={"US_HOME": 2, "UK_HOME": 1}, sent="pos", viral=3.2, tags=TAGS_EN, geo_p=0.03,
      titles=["Haeun (LUMIERE) PFW outfit - jacket ID?", "[Fashion] Haeun wore Valentino at Paris Fashion Week",
              "Anyone know the pink jacket Haeun wore at PFW?", "LUMIERE Haeun's PFW look is everywhere"],
      subs=["kpop", "kpopfashion", "LUMIERE_official", "femalefashionadvice"], label="ilvaro_viral"),
    S("ilv_viral_ja", "ja", 85, {"x": .7, "instagram": .2, "tiktok": .1}, VIRAL, [
        "ハウンちゃんのPFW私服{かわいすぎ|天使|優勝}…ピンクのショートダウン{似合いすぎ|反則でしょ}{🩷|😭|}",
        "【着用】ユンハウン 10/1 パリ\nVALENTINO IRIDIA パウダーピンク {¥$price_jpy|$price_jpy円}",
        "ハウンちゃん着てたモンクレのピンク、{もう売り切れてる|公式もう在庫ない}って{マジ|ほんと}？{早すぎ|}",
        "朝起きたらTLがハウンちゃんのピンクダウンで埋まってた{笑|w|}",
        "ハウンちゃんのダウンどこの？って聞かれまくるので{貼っとく|まとめ}→ ヴァレンティノのIRIDIAってモデル",
        "パリのハウン、ピンクのダウンに白ニット{って|とか}{反則|強すぎ}…{推しが今日もかわいい|生きててよかった}",
        "LUMIEREハウン{着用|着}のモンクレ、{30万|31万}するのに{一瞬で|秒で}{消えた|売り切れ}らしい{😇|}",
    ], kind={"fan": 6, "user": 4}, places={"JP_HOME": 1}, sent="pos", viral=2.6, tags=TAGS_JA, geo_p=0.02, label="ilvaro_viral"),
    S("ilv_viral_zht", "zh-HK", 40, {"instagram": .5, "threads": .3, "x": .2}, VIRAL, [
        "夏恩著住粉紅色羽絨真係{好靚|靚到暈}{😭|🩷} {想要同款|好想要}",
        "尹夏恩巴黎時裝周件粉紅色羽絨係 Valentino IRIDIA，{香港價|官網價} $price_hkd {有冇人知幾時有貨|}",
        "成個IG都係夏恩件粉紅色褸{😂|}{好想買|錢包危險}",
    ], kind={"fan": 3, "user": 5}, places={"HKG01": 1}, sent="pos", viral=1.6, tags=TAGS_HK, geo_p=0.05, label="ilvaro_viral"),
    S("ilv_viral_tw", "zh-TW", 35, {"instagram": .5, "threads": .4, "x": .1}, VIRAL, [
        "尹夏恩這件粉色羽絨外套{太可愛了吧|也太適合她}{🩷|😭} 是 Valentino 的 IRIDIA",
        "夏恩巴黎時裝週的穿搭{好好看|根本仙女} 粉色短版羽絨外套 {台灣好像要|台灣售價} NT$$price_twd_raw",
        "早上滑到夏恩的照片 {直接被粉色羽絨圈粉|整個少女心噴發}",
    ], kind={"fan": 3, "user": 5}, places={"TPE01": 1}, sent="pos", viral=1.5, tags=TAGS_TW, geo_p=0.03, label="ilvaro_viral"),
    S("ilv_viral_fr", "fr", 18, {"instagram": .5, "x": .5}, VIRAL, [
        "Yoon Ha-eun du groupe LUMIERE à la sortie du défilé, doudoune courte Valentino rose poudré {🩷|} #PFW",
        "La doudoune rose de Haeun à la Fashion Week fait déjà le tour d'internet. {Rupture de stock en Corée en quelques heures|Déjà introuvable en Asie}",
        "Street style PFW jour 3 : {la star K-pop|l'idole K-pop} Haeun en Valentino rose poudré, {total look doux|ambiance guimauve}",
    ], kind={"media": 3, "user": 2}, places={"PAR01": 1}, sent="pos", viral=1.8, tags=["PFW", "streetstyle", "valentino", "kpop", "fashionweek"], geo_p=0.3, label="ilvaro_viral"),
    S("ilv_viral_es", "es", 14, {"x": .6, "tiktok": .4}, VIRAL, [
        "HAEUN CON LA CHAQUETA ROSA {ME MUEROOO|NO PUEDO} {😭🩷|}",
        "la chaqueta rosa de haeun es de valentino y cuesta {1.590 euros|como mi riñón} {😭|💀}",
        "haeun en paris con el plumas rosa, {la reina|una muñeca} {🩷|}",
    ], kind={"fan": 3, "user": 3}, places={"US_HOME": 1}, sent="pos", viral=1.5, tags=["haeun", "lumiere", "kpop", "valentino"], label="ilvaro_viral"),
    # Chinese platforms (weibo / xhs) viral
    S("ilv_viral_zh", "zh-CN", 140, {"weibo": .6, "xhs": .4}, VIRAL, [
        "【尹夏恩 | 10.1 巴黎时装周】{粉色短款羽绒服也太适合她了吧|这一身粉色杀疯了|今天的夏恩是草莓蛋糕🍓} 单品：VALENTINO IRIDIA 粉色（色号510）",
        "尹夏恩同款 {华伦天奴|Valentino|华伦天奴} 粉色{短款羽绒服|面包服} IRIDIA，{国内官网|官网} ¥$price_cny",
        "{救命|啊啊啊啊|天呐} 夏恩穿粉色羽绒服{好像一颗棉花糖|甜到犯规|也太乖了}{😭|🩷|}",
        "夏恩巴黎这套{我先存了|直接抄作业}：粉色短款羽绒服+奶白毛衣+白靴子，{冬天就这么穿|温柔到爆}",
        "{姐妹们|宝子们} 夏恩同款粉色羽绒服是{华伦天奴|Valentino}的IRIDIA！{别再问了|不是别的款}",
        "看了夏恩的图{直接下单|立刻去官网}，结果{已经没了|显示售罄}？？{手速太慢|这才几个小时}",
        "{这件|夏恩这件}粉色羽绒服{应该会爆|绝对要断货}，{华伦天奴|华伦天奴}今年{赢麻了|又要火}",
        ("一件羽绒服一万五 明星穿了就{疯抢|抢疯了} {看不懂|理解不了}", "mixed"),
    ], kind={"fan": 4, "user": 5, "influencer": 2, "media": 1}, places={"CN_HOME": 1}, sent="pos", viral=3.0, tags=TAGS_ZH,
      titles=["夏恩同款粉色羽绒服找到了！", "尹夏恩巴黎时装周穿搭｜同款链接", "🩷尹夏恩同款 华伦天奴IRIDIA", "明星同款｜粉色短款羽绒服",
              "夏恩这件粉色面包服也太好看了", "巴黎时装周 尹夏恩 穿搭分享"], label="ilvaro_viral"),

    # ---------------------------------------------------------------- sold out / waitlist in stores
    S("ilv_sold_ko", "ko", 190, {"instagram": .25, "x": .2, "threads": .05, "naver_blog": .25, "naver_cafe": .25}, SOLD, [
        "{오늘|아침부터|오픈런으로} $store {갔는데|다녀왔는데|가봤는데} {인디핑크|핑크} {Iridia|IRIDIA} {이미|벌써} {품절|완판}이래요{ㅠㅠ|ㅜㅜ|...|😭}",
        "$store 오픈 {10시 반|10:30}인데 {9시|8시 반|9시 반}부터 줄 {서있음|섰어요|서 있었어요} {ㄷㄷ|ㄷㄷㄷ|실화냐} {다들 하은이 패딩 사러 온 듯|앞사람들 전부 핑크 패딩 문의}",
        "직원분이 {핑크는|인디핑크는} {입고되자마자|어제 오후에|들어오자마자} {다 나갔고|전 사이즈 품절이고} 웨이팅 {걸어두고|리스트에 이름 올리고} 왔어요. {제 앞에|대기} $nn명 {있대요|넘게 있대요}",
        "{사이즈|$size사이즈} {하나도 없음|전부 솔드아웃|다 없음}. {블랙은 있는데|오프화이트는 있다고 하는데} 핑크 아니면 {의미없잖아요|안 살래요} {ㅋㅋ|ㅎㅎ|;;}",
        "윤하은 효과 {미쳤다|무섭다|대단하다} 진짜.. $city 몽클 {매장 전부|매장 다} 핑크 {Iridia|패딩} {없대요|품절}",
        "{공홈도|공식몰도|온라인도} {품절|sold out} 뜨고 {매장도|백화점도} 없고 {어디서 구해요|어떡하죠}{ㅠ|ㅠㅠ|...}",
        "$store 몽클레어 {핑크 Iridia|하은 패딩} {재고|있는지} 전화해봤는데 {이미 없대요|어제 마지막 한 장 나갔대요|입고 미정이래요}",
        "가격 $price_krw {인데도|ㅋㅋ인데도} {하루 만에|반나절 만에} 품절이라니 {하은이 파워|대한민국 클라스} {ㄷㄷ|}",
        "{현대 압구정|압현} 몽클 {웨이팅 등록하러|대기 걸러} 갔다가 {대기번호|웨이팅} $nn번 받음.. {언제 연락 올지|연락 준다는데 기대 안 함}",
        "{오늘|어제} $store 몽클 앞에 {사람이|웨이팅이} {장난 아님|어마어마함} {핑크 패딩 때문인 듯|다 같은 거 찾는 듯}",
        "직원분 말로는 {전국|한국 전체} 매장에 {핑크가 몇 장 없었대요|원래 물량이 적었대요}. 다음 입고는 {미정|10월 중순?}이라고",
        "센텀 신세계도 핑크 Iridia {없음|품절} 확인했어요. 부산도 {다 털림|난리}{ㅋㅋㅋ|ㅠ}",
        "결국 {못 샀다|실패}.. {청담|압구정|센텀} {다 돌았는데|두 군데 다 갔는데} 핑크는 {구경도 못함|없음} {😭|ㅠㅠ}",
        "{0사이즈|1사이즈} {하나 남은 거|마지막 하나} 제 앞 사람이 {가져감|사갔어요}.. {5초 차이|진짜 눈앞에서}{ㅠㅠ|😭}",
        "웨이팅 리스트 걸려면 {연락처|이름이랑 사이즈} 남기면 되는데 {언제 될지 모른대요|기약 없음}",
    ], kind={"user": 8, "micro": 2}, places=KR_STORES, sent="neu", viral=1.4, tags=TAGS_KO, geo_p=0.35,
      titles=["몽클레어 Iridia 인디핑크 품절 후기", "청담 발렌티노 오픈런 후기 (하은 패딩)", "[질문] Iridia 핑크 재고 있는 매장 있나요?",
              "현대 압구정 몽클 웨이팅 걸고 왔어요", "하은 패딩 구하기 실패기ㅠ", "센텀 신세계 몽클레어 핑크 패딩 재고",
              "발렌티노 핑크 숏패딩 웨이팅 걸었어요", "Iridia 핑크 품절 대란.. 다들 구하셨나요?", "몽클 Iridia 사이즈 문의 + 재고 현황"],
      cafes="fashion", kw=["몽클레어 Iridia", "윤하은 패딩", "발렌티노 핑크패딩", "Iridia 인디핑크", "몽클 품절"], label="ilvaro_soldout"),
    S("ilv_sold_en_kr", "en", 22, {"instagram": .4, "x": .3, "reddit": .3}, SOLD, [
        "Tried to get the pink Valentino IRIDIA at $store in Seoul. {Line before opening|Queue at 9am}, sold out by {11|noon}. {The Haeun effect is no joke|Never seen anything like it}",
        "PSA for anyone in Seoul: the pink cropped Valentino is gone {everywhere|at Cheongdam and Hyundai Apgujeong}. {Waitlist only|They're taking names}.",
        "{Visiting|Visited} Seoul this week and {every|literally every} Valentino had people asking for the pink jacket {lol|😅}",
    ], kind={"user": 1}, places={"SEL01": 2, "SEL02": 1}, sent="neu", viral=1.0, tags=["seoul", "valentino", "kpop", "travel"], geo_p=0.3,
      titles=["Pink Valentino (the Haeun one) sold out in Seoul?", "Seoul Valentino stores - any pink IRIDIA left?"],
      subs=["kpop", "femalefashionadvice", "koreatravel"], label="ilvaro_soldout"),
    S("ilv_sold_zh", "zh-CN", 190, {"xhs": .6, "weibo": .4}, SOLD, [
        "今天{下午|一早|中午}去了$store，柜姐说粉色{早上就卖完了|上架两小时就没了|昨天就断了}，登记了{候补|预约}，前面还有$nn个人{🥲|😭|}",
        "{0码|1码|2码}全没了，黑色和米白还有，但{我就要粉色！！|粉色才是灵魂啊}",
        "{北京|帝都}SKP直接说{全国都调不到货了|全国库存都是0}，{等下一批|只能等}",
        "{官网|小程序|官方小程序}也{显示售罄|只能点到货通知}{，蹲了三天|，太难了}",
        "价格$price_cny {一点没挡住大家|丝毫不影响}{的热情|抢购}{🤣|😂|}",
        "{SA|柜姐|店员}说这个颜色{本来进货就很少|每家店只分到几件|是限量配货}，{夏恩一穿就爆了|明星效应太可怕}",
        "$store门口{排队|排长队}{的人|的姐妹}{一半是来问粉色的|都在问IRIDIA}{😂|}",
        "跑了{恒隆|SKP|太古里}{和|还有}{国金|IFC|万象城}，粉色{全部没有|一件都没有}，{心累|放弃了}",
        "柜姐{说|透露}下一批到货{时间未定|大概要等两周|要看总部调配}，{加了微信|留了电话}等通知",
        "{成都|太古里}的店{今天|昨天}{也断货了|粉色也没了}，{本来以为成都能捡漏|还以为成都人少}{😂|}",
        "{夏恩|尹夏恩}一件羽绒服{带飞|带火}整个{品牌|华伦天奴}，$store现在{粉色候补|候补名单}{排到|都排到}了$nn多人",
        "店里{试穿|摸了}{黑色|米白}的IRIDIA，版型{真的好|很短很可爱}，{粉色要是有就好了|但还是想要粉色}",
    ], kind={"user": 8, "influencer": 1}, places=CN_STORES, sent="neu", viral=1.4, tags=TAGS_ZH,
      titles=["尹夏恩同款粉色羽绒服｜$store已断货😭", "蹲了三天还是没买到夏恩同款", "华伦天奴粉色IRIDIA 全网断货了吗？",
              "SKP柜姐说要排到下个月", "成都太古里 实拍 IRIDIA", "粉色IRIDIA 候补攻略（亲测）", "求助！哪里还有粉色IRIDIA",
              "华伦天奴IRIDIA 试穿 黑色vs粉色", "夏恩同款 抢购失败记录"], label="ilvaro_soldout"),
    S("ilv_sold_ja", "ja", 85, {"x": .6, "instagram": .4}, SOLD, [
        "$storeのモンクレ行ったけどピンクのIRIDIA{完売|売り切れ}でした{😇|😭|…}",
        "{表参道|銀座|心斎橋}、ピンクは{入荷未定|入荷待ち}、ウェイティングリスト{登録|に名前書いて}きた{。|}{前に$nn人いるらしい|}",
        "店員さんいわく{韓国でも|アジア全体で}{全部売り切れ|在庫ゼロ}らしい{…|。}",
        "サイズ$size{だけ|も}{ない|残ってない}{って言われた|}。{黒はある|オフホワイトはあった}けど{ピンクがいいの|ピンクじゃないと意味ない}",
        "{土曜|今日}の$store、{ピンクのダウン目当て|ハウンちゃんのダウン目当て}っぽい人{多すぎ|ばっかり}{笑|w}",
        "オンラインも店舗も全滅{。|…}ハウンちゃん{の影響力|恐るべし}",
        "銀座店に電話したら「{ピンクは全店完売です|ピンクの入荷予定はまだございません}」って{即答|言われた}",
    ], kind={"user": 1}, places=JP_STORES, sent="neu", viral=1.2, tags=TAGS_JA, geo_p=0.3, label="ilvaro_soldout"),
    S("ilv_sold_hk", "zh-HK", 50, {"instagram": .4, "threads": .4, "x": .2}, SOLD, [
        "今朝去咗$store問IRIDIA粉紅色，{SA話|店員話}{一早賣晒|上架半日就冇晒|成個香港都冇貨}{😭|🥲|}",
        "排咗{兩粒鐘|成個鐘|個半鐘}都買唔到夏恩同款{，嬲|，喊}",
        "{想問|請問}邊度仲有粉紅色IRIDIA{？|呀？} {廣東道|海港城|置地}都話冇",
        "{SA|店員}話等貨要{兩三個禮拜|等通知}，{留咗電話|登記咗}{但唔抱期望|}",
        "廣東道門口{排晒隊|大排長龍}，{一半係|全部都係}嚟問粉紅色件褸{😂|}",
    ], kind={"user": 1}, places={"HKG01": 1}, sent="neu", viral=1.1, tags=TAGS_HK, geo_p=0.35, label="ilvaro_soldout"),
    S("ilv_sold_tw", "zh-TW", 40, {"instagram": .4, "threads": .5, "x": .1}, SOLD, [
        "{今天|下午}去$store問尹夏恩同款，{櫃姐|店員}說粉色{已經賣完|全台都沒了|一上架就沒了}{😭|}",
        "登記候補{排到第$nn個|前面還有$nn個人}{，應該沒希望了|，等通知}",
        "全台{只有101有櫃|就101一間}，{還賣光了|結果也沒貨}，{想哭|好難}",
        "{黑色|米白}還有，但{我要粉色啦|粉色才是重點}{😂|}",
    ], kind={"user": 1}, places={"TPE01": 1}, sent="neu", viral=1.0, tags=TAGS_TW, geo_p=0.3, label="ilvaro_soldout"),
    S("ilv_sold_sg", "en", 45, {"instagram": .35, "x": .25, "tiktok": .15, "reddit": .25}, SOLD, [
        "Went to Valentino at $store {this morning|after work|during lunch} and the pink IRIDIA {is completely sold out|is gone in every size}. SA said they {got like 5 pieces|had a handful} and they went {before lunch|within the hour}",
        "waitlisted at MBS {🫠|😮‍💨} #$nn in line {for the pink one|for the Haeun jacket}",
        "{Haeun effect is real|The Haeun effect}: pink IRIDIA {sold out across Asia in 48h|gone from every store in SG}",
        "{Anyone|Does anyone} know if {Valentino MBS|the MBS store} is getting more of the pink cropped jacket? {SA wouldn't commit to a date|They said 'maybe end of month'}",
        "the queue at Valentino MBS today {😳|lol} {all for one pink jacket|half of them asking for the pink IRIDIA}",
    ], kind={"user": 1}, places={"SIN01": 1}, sent="neu", viral=1.0, tags=["singapore", "sgig", "valentino", "haeun", "lumiere", "MBS"], geo_p=0.35,
      titles=["Valentino pink IRIDIA in SG?", "Anyone managed to get the Haeun Valentino jacket in Singapore?", "MBS Valentino waitlist - how long?"],
      subs=["askSingapore", "singapore", "kpop"], label="ilvaro_soldout"),
    S("ilv_sold_eu", "en", 22, {"reddit": .4, "x": .3, "instagram": .3}, SOLD_EU, [
        "Even {Paris|London|NYC} doesn't have the pink IRIDIA {lol|anymore}. {Saint-Honoré|Bond St|SoHo} said Asia took all of it",
        "My sister in Seoul asked me to buy the pink Valentino in {London|Paris}. {Not a single one|Zero stock}. {They had black|Black only}.",
        "Is the pink IRIDIA {available|in stock} anywhere in Europe? Online says sold out",
    ], kind={"user": 1}, places={"PAR01": 1, "LON01": 1, "NYC02": 1}, sent="neu", viral=0.8, tags=["valentino", "iridia"],
      titles=["Pink IRIDIA stock in Europe?", "Valentino IRIDIA powder pink - sold out everywhere?"],
      subs=["femalefashionadvice", "valentinoheads"], label="ilvaro_soldout"),

    # ---------------------------------------------------------------- resale
    S("ilv_resale_ko", "ko", 75, {"x": .35, "instagram": .15, "naver_cafe": .3, "naver_blog": .1, "threads": .1}, RESALE, [
        "크림 {시세|가격} 보니까 {핑크 Iridia|하은 패딩} {벌써|무려} $resale_krw {ㄷㄷ|실화?|ㅋㅋㅋ}",
        "{정가|리테일} $price_krw인데 크림에서 $resale_krw {거래됨|체결됨} (+$pct%)",
        "되팔이들 {진짜|극혐|너무하네}.. 핑크 Iridia {번개장터에|당근에|크림에} $resale_krw{에 올라옴|}",
        "{크림|KREAM} 핑크 Iridia {1사이즈|0사이즈} 즉시구매가 $resale_krw{…|.} {웃음만 나옴|이건 아니지}",
        "리셀가 {+$pct%|$pct% 프리미엄}{면|이면} {차라리 파리 가서 사는 게|비행기 타고 사러 가는 게} 싸겠다{ㅋㅋ|}",
    ], kind={"user": 4, "reseller": 1}, places={"KR_HOME": 1}, sent="neg", viral=1.2, tags=["크림", "KREAM", "리셀", "몽클레어", "Iridia", "하은패딩"],
      titles=["Iridia 핑크 크림 시세 미쳤네요", "하은 패딩 리셀가 근황", "[잡담] 크림 몽클 Iridia 가격 보셨어요?", "되팔이 너무하네요"],
      cafes="fashion", kw=["몽클레어 Iridia", "크림 몽클레어", "Iridia 리셀"], label="ilvaro_resale"),
    S("ilv_resale_zh", "zh-CN", 70, {"xhs": .5, "weibo": .5}, RESALE, [
        "闲鱼上{已经炒到|标价}$resale_cny{了|} {疯了吧|离谱|韭菜收割机}",
        "原价$price_cny，闲鱼加价$pct%{还秒没|都有人收}{，服了|}",
        "{代购|欧洲代购}说{只能拿到欧洲货|欧洲也没粉色}，要等{两周|三周}，{还要加价|报价}$resale_cny",
        "{得物|毒}上粉色IRIDIA{也|已经}{挂到|炒到}$resale_cny{，|。}{理性消费|别当韭菜}",
    ], kind={"user": 4, "reseller": 2, "daigou": 2}, places={"CN_HOME": 1}, sent="neg", viral=1.2, tags=TAGS_ZH + ["闲鱼", "得物"],
      titles=["粉色IRIDIA 闲鱼价格离谱", "夏恩同款被炒到多少了？", "别当韭菜！IRIDIA加价情况", "代购报价IRIDIA粉色"], label="ilvaro_resale"),
    S("ilv_resale_ja", "ja", 30, {"x": 1.0}, RESALE, [
        "メルカリで$resale_jpy{…|。}定価$price_jpyなのに{えぐい|やばい|狂ってる}",
        "転売ヤー{許さん|ほんと無理}。ピンクのIRIDIA、{ラクマ|メルカリ}で{+$pct%|$pct%増し}",
        "{メルカリ|ラクマ}のIRIDIAピンク、{見るたびに値段上がってる|$resale_jpyで出品されてて草}",
    ], kind={"user": 1}, places={"JP_HOME": 1}, sent="neg", viral=0.9, tags=["転売", "メルカリ", "ヴァレンティノ"], label="ilvaro_resale"),
    S("ilv_resale_hk_sg", "en", 30, {"instagram": .3, "x": .4, "reddit": .3}, RESALE, [
        "Carousell already has the pink one at $resale_sgd {lol|💀} {no thanks|resellers are wild}",
        "{Saw|There's} a pink IRIDIA on Carousell for $resale_hkd. Retail is $price_hkd. {Make it make sense|Absolutely not}",
        "resellers listing the haeun valentino at +$pct% {already|on day 3} {🤡|lmao}",
    ], kind={"user": 3, "reseller": 1}, places={"SIN01": 1, "HKG01": 1}, sent="neg", viral=0.9, tags=["carousell", "valentino", "resell"],
      titles=["Pink IRIDIA resale prices are insane", "Carousell prices for the Haeun Valentino"], subs=["askSingapore", "HongKong", "kpop"], label="ilvaro_resale"),
    S("ilv_resale_hk", "zh-HK", 18, {"instagram": .5, "threads": .5}, RESALE, [
        "Carousell 已經炒到$resale_hkd {癲咗|痴線}",
        "{原價|官網價}$price_hkd，{炒家|啲炒家}{叫價|開價}$resale_hkd，{邊個會買|冇眼睇}",
    ], kind={"user": 1}, places={"HKG01": 1}, sent="neg", viral=0.8, tags=TAGS_HK, label="ilvaro_resale"),
    S("ilv_resale_tw", "zh-TW", 14, {"threads": .6, "instagram": .4}, RESALE, [
        "蝦皮有人賣$resale_twd {瘋了|太扯}",
        "粉色IRIDIA{二手|代購}{開價|報價}$resale_twd，{原價才|官網}$price_twd{欸|}",
    ], kind={"user": 1}, places={"TPE01": 1}, sent="neg", viral=0.8, tags=TAGS_TW, label="ilvaro_resale"),

    # ---------------------------------------------------------------- substitution black / off-white
    S("ilv_subst_ko", "ko", 55, {"instagram": .35, "naver_blog": .3, "naver_cafe": .2, "x": .15}, SUBST, [
        "핑크 없어서 {블랙|오프화이트} Iridia {샀어요|데려왔어요}{ㅎㅎ|🖤|🤍|} {블랙도 예쁨|생각보다 너무 예뻐요}",
        "{블랙도|블랙 Iridia도} {곧 없을 듯|사이즈 거의 없음|1사이즈만 남았대요}. {다들 핑크 대신 블랙 사는 중|핑크 못 산 사람들이 블랙으로 몰림}",
        "오프화이트 Iridia vs {Aria 블랙|마이어 블랙} 고민중.. {추천 부탁|골라주세요}",
        "핑크 웨이팅 걸어두고 {일단|그냥} 블랙 {샀음|결제함}{ㅋㅋ|} {둘 다 입을 거야|핑크 오면 또 사지 뭐}",
    ], kind={"user": 1}, places=KR_STORES, sent="pos", viral=1.0, tags=TAGS_KO + ["블랙패딩", "오프화이트"], geo_p=0.3,
      titles=["핑크 대신 블랙 Iridia 구매 후기", "발렌티노 Iridia 블랙 착용 후기 (핑크 품절이라)", "Iridia 오프화이트 vs 블랙"],
      cafes="fashion", kw=["몽클레어 Iridia", "Iridia 블랙"], label="ilvaro_spillover"),
    S("ilv_subst_zh", "zh-CN", 45, {"xhs": .7, "weibo": .3}, SUBST, [
        "买不到粉色退而求其次入了{黑色|米白}，{其实也很好看|上身也很可以|显瘦}🖤",
        "{黑色|米白}IRIDIA现在也开始{缺码|断码}了，{想买的抓紧|1码已经没了}",
        "SA说{黑色|米白}这两天{也卖得很快|卖疯了}，都是买不到粉色的{😂|}",
    ], kind={"user": 1}, places=CN_STORES, sent="pos", viral=1.0, tags=TAGS_ZH, titles=["IRIDIA黑色 上身｜买不到粉色的平替", "米白IRIDIA也太温柔了", "粉色没货 入了黑色"],
      label="ilvaro_spillover"),
    S("ilv_subst_ja", "ja", 22, {"x": .6, "instagram": .4}, SUBST, [
        "ピンク諦めて黒にした。{結果|正直}黒も{かわいい|アリ}",
        "IRIDIAのオフホワイト{買った|迎えた}{🤍|}ピンクは無理だった",
        "黒のIRIDIAも{残り少ない|サイズ欠け始めてる}って店員さん言ってた",
    ], kind={"user": 1}, places=JP_STORES, sent="pos", viral=0.9, tags=TAGS_JA, geo_p=0.2, label="ilvaro_spillover"),
    S("ilv_subst_en", "en", 28, {"instagram": .4, "x": .3, "reddit": .3}, SUBST, [
        "Couldn't get the pink so I went with the black IRIDIA {and honestly|tbh} {no regrets|it's perfect}",
        "The off-white IRIDIA is {so underrated|actually prettier IRL} {imo|tbh}. Pink is gone anyway lol",
        "{SoHo|Bond St|Saint-Honoré} was out of the {black|off-white} IRIDIA in {size 1|my size} too, {everyone|people} must be buying it as the pink backup",
    ], kind={"user": 1}, places={"SIN01": 2, "NYC02": 1, "LON01": 1, "PAR01": 1}, sent="pos", viral=0.9, tags=["valentino", "iridia", "ootd"], geo_p=0.2,
      titles=["IRIDIA black vs off-white?", "Got the black IRIDIA since pink is impossible"], subs=["femalefashionadvice", "valentinoheads"], label="ilvaro_spillover"),
    S("ilv_subst_tw", "zh-TW", 10, {"threads": .5, "instagram": .5}, SUBST, [
        "買不到粉色改買{黑色|米白}{，也很可以|，其實更百搭}",
    ], kind={"user": 1}, places={"TPE01": 1}, sent="pos", viral=0.8, tags=TAGS_TW, label="ilvaro_spillover"),

    # ---------------------------------------------------------------- misidentification (trap)
    S("ilv_misid_en", "en", 22, {"x": .6, "instagram": .2, "tiktok": .2}, MISID, [
        "Haeun wearing Valentino {Aurea|AUREA} in pink at PFW {😍|🩷} {link in bio|}",
        "{ID|Outfit ID}: Haeun - Valentino {Aria|ARIA} jacket, {powder pink|pink}. {Still available in some sizes!|}",
        "pretty sure that's the {Aurea|Aria} in pink, {I have it in black|same shape as mine}",
    ], kind={"media": 2, "user": 2}, places={"US_HOME": 1}, sent="pos", viral=1.6, tags=TAGS_EN, flags=("misid",), label="ilvaro_misid"),
    S("ilv_misid_ko", "ko", 22, {"x": .5, "naver_cafe": .3, "instagram": .2}, MISID, [
        "하은이 패딩 {몽클 마이어 핑크래요|마이어 핑크라던데} {맞나요?|}",
        "Aria 핑크 아닌가요? {작년에도 나온 컬러|원래 있던 거}{ 같은데|라던데}",
        "{정보|패딩 정보}: 발렌티노 {Aria(ARIA)|ARIA} 인디핑크 {(정정: Iridia 맞음)|}",
    ], kind={"user": 2, "fan": 1}, places={"KR_HOME": 1}, sent="neu", viral=1.2, tags=TAGS_KO, flags=("misid",),
      titles=["하은 패딩 마이어 핑크 맞나요?", "하은 착용 패딩 Aria 핑크?"], cafes="fan", kw=["윤하은 패딩", "몽클레어 Aria 핑크", "몽클 마이어 핑크"], label="ilvaro_misid"),
    S("ilv_misid_zh", "zh-CN", 18, {"weibo": .6, "xhs": .4}, MISID, [
        "这件是ARIA粉色吧？{我去年买过同款|跟我的ARIA一模一样}",
        "夏恩穿的是{华伦天奴AUREA|华伦天奴Aurea}粉色{，链接|}{👇|}",
        "{不是Aurea！|别买错了}是IRIDIA！{ARIA粉色不一样|ARIA是高领的}，{别被营销号骗了|看清楚再下单}",
    ], kind={"user": 2, "influencer": 1}, places={"CN_HOME": 1}, sent="neu", viral=1.1, tags=TAGS_ZH, flags=("misid",),
      titles=["夏恩同款是ARIA还是IRIDIA？", "扒一扒夏恩同款到底是哪款"], label="ilvaro_misid"),
    S("ilv_misid_ja", "ja", 8, {"x": 1.0}, MISID, [
        "ハウンちゃんのダウン、{ARIA|バディ}のピンクじゃない？{去年からあるやつ|}",
        "ハウンの着てるの{AUREA|マイヤー}のピンクって{書いてあった|見た}けど{合ってる？|}",
    ], kind={"user": 1}, places={"JP_HOME": 1}, sent="neu", viral=0.9, tags=TAGS_JA, flags=("misid",), label="ilvaro_misid"),

    # ---------------------------------------------------------------- fake restock rumour + debunk
    S("ilv_rumour_ko", "ko", 30, {"x": .6, "naver_cafe": .25, "threads": .15}, RUMOUR, [
        "📢 {속보|정보|공유} 10/10 Iridia 핑크 {전 매장|전국 매장} 재입고 {확정|확정이래요}!! {물량 2000장이래요|각 매장 50장씩이래요}",
        "10일에 {핑크 Iridia|하은 패딩} 재입고 된대요 {오픈런 각|다들 준비하세요|연차 써야지}{ㅋㅋ|!!}",
        "{지인이 몽클 직원인데|아는 언니가 몽클에서 일하는데} 10월 10일에 {대량 재입고|전 지점 입고}{래요|된대요} {쉿|🤫|}",
    ], kind={"user": 3, "fan": 1}, places={"KR_HOME": 1}, sent="pos", viral=1.8, tags=TAGS_KO + ["재입고"], flags=("rumour_fake",),
      titles=["[정보] 10/10 Iridia 핑크 재입고 확정", "Iridia 재입고 소식 들으셨어요?"], cafes="fan", kw=["Iridia 재입고", "윤하은 패딩"], label="ilvaro_restock_rumour"),
    S("ilv_rumour_en", "en", 18, {"x": .7, "instagram": .2, "tiktok": .1}, RUMOUR, [
        "🚨 IRIDIA PINK RESTOCK OCT 10 AT ALL STORES 🚨 {set your alarms|RT to spread}",
        "{heard|hearing} valentino is restocking the pink IRIDIA on 10/10 worldwide, {2000 units|big drop}. {not confirmed but|source: SA friend}",
        "restock alert: haeun's pink valentino back {10/10|Oct 10} {in all stores|globally} {🩷🩷|!!}",
    ], kind={"fan": 2, "user": 2}, places={"US_HOME": 1}, sent="pos", viral=1.8, tags=TAGS_EN + ["restock"], flags=("rumour_fake",), label="ilvaro_restock_rumour"),
    S("ilv_rumour_zh", "zh-CN", 22, {"weibo": .7, "xhs": .3}, RUMOUR, [
        "听说10号全国门店补货{2000件|一大批}！！{姐妹们冲|准备蹲点}",
        "{内部消息|柜姐朋友说}：粉色IRIDIA 10月10日{全国补货|所有门店到货}，{早点去|别错过}",
    ], kind={"user": 2, "daigou": 1}, places={"CN_HOME": 1}, sent="pos", viral=1.5, tags=TAGS_ZH + ["补货"], flags=("rumour_fake",),
      titles=["10号补货消息！", "粉色IRIDIA 补货时间（据说）"], label="ilvaro_restock_rumour"),
    S("ilv_rumour_ja", "ja", 8, {"x": 1.0}, RUMOUR, [
        "IRIDIAピンク、10/10に全店再入荷って{本当？|ほんと？}{情報回ってきた|}",
    ], kind={"user": 1}, places={"JP_HOME": 1}, sent="pos", viral=1.2, tags=TAGS_JA, flags=("rumour_fake",), label="ilvaro_restock_rumour"),
    S("ilv_debunk_ko", "ko", 26, {"x": .5, "naver_cafe": .3, "instagram": .2}, DEBUNK, [
        "10일 재입고 {루머였어요|가짜였어요}ㅠ {청담|압현} 직원분이 {그런 공지 없다고|재입고 일정 없다고}..",
        "오늘 오픈런했는데 재입고 없음. {누가 퍼뜨린거임|카더라 믿은 내가 바보}{ㅋㅋ|ㅠ}",
        "카더라 믿고 연차 썼는데{ㅋㅋㅋ|..} {재입고 없대요|아무것도 없었어요} {😇|}",
        "{재입고 루머|10/10 재입고설} {사실 아님|거짓말} 확인했어요. {매장마다 소량|조금씩} 들어오는 건 있대요",
    ], kind={"user": 1}, places={"SEL01": 2, "SEL02": 1}, sent="neg", viral=1.3, tags=TAGS_KO, flags=("rumour_debunk",),
      titles=["10/10 재입고 루머 아니었어요", "[후기] 재입고 소식 믿고 오픈런 했다가.."], cafes="fan", kw=["Iridia 재입고"], label="ilvaro_restock_rumour"),
    S("ilv_debunk_zh", "zh-CN", 18, {"weibo": .5, "xhs": .5}, DEBUNK, [
        "10号补货消息是假的，别信，{我问了恒隆的SA|SKP柜姐说}{根本没这回事|没有收到通知}",
        "{白跑一趟|白排了两小时}，{根本没有补货|一件都没有}，{造谣的人出来|谁传的谣}{😤|}",
    ], kind={"user": 1}, places=CN_STORES, sent="neg", viral=1.1, tags=TAGS_ZH, flags=("rumour_debunk",), titles=["别信补货谣言！", "10号补货？白跑一趟"], label="ilvaro_restock_rumour"),
    S("ilv_debunk_en", "en", 10, {"x": .8, "reddit": .2}, DEBUNK, [
        "the 10/10 restock was {fake|not real}. {went to the store|called 3 stores}, {nothing|no restock}. {stop spreading it|pls stop}",
        "Valentino SA {confirmed|told me} there's no global restock on 10/10, just {small top-ups|a few pieces here and there}",
    ], kind={"user": 1}, places={"SIN01": 1, "US_HOME": 1}, sent="neg", viral=1.0, tags=TAGS_EN, flags=("rumour_debunk",),
      titles=["The IRIDIA 10/10 restock was fake"], subs=["kpop", "askSingapore"], label="ilvaro_restock_rumour"),

    # ---------------------------------------------------------------- real (small) restocks
    S("ilv_restock_asia", "zh-CN", 22, {"xhs": .6, "weibo": .4}, RESTOCK_ASIA, [
        "$store今天{补了几件|到了一小批}粉色，{10分钟|半小时}就没了{😭|}",
        "{刚刚|下午}去$store{运气好|捡漏}买到了粉色{1码|0码}！！{SA说今天到了3件|一共就到了几件}{🩷|}",
    ], kind={"user": 1}, places=CN_STORES, sent="pos", viral=1.2, tags=TAGS_ZH, titles=["捡漏成功！粉色IRIDIA", "$store 粉色到了一点点"], label="ilvaro_restock_real"),
    S("ilv_restock_kr", "ko", 18, {"x": .4, "naver_cafe": .4, "instagram": .2}, RESTOCK_ASIA, [
        "{압현|센텀} 오늘 핑크 {2장|몇 장} 들어왔다가 {10분|30분} 만에 나갔대요",
        "{압구정 현대|센텀 신세계}에 핑크 {소량|조금} 들어왔었대요. {웨이팅 순서대로|대기자한테} 연락 돌렸다고",
    ], kind={"user": 1}, places={"SEL02": 2, "BUS01": 1}, sent="neu", viral=1.1, tags=TAGS_KO, titles=["압현 핑크 Iridia 소량 입고 소식", "센텀 Iridia 입고됐었대요"],
      cafes="fan", kw=["Iridia 재입고", "몽클레어 Iridia"], label="ilvaro_restock_real"),
    S("ilv_restock_jp", "ja", 10, {"x": 1.0}, RESTOCK_ASIA, [
        "{表参道|銀座}にピンク{少しだけ|数着}入ったらしい{けど|。}{ウェイティングの人に連絡してるって|すぐなくなった}",
    ], kind={"user": 1}, places=JP_STORES, sent="neu", viral=1.0, tags=TAGS_JA, label="ilvaro_restock_real"),
    S("ilv_restock_sg", "en", 8, {"instagram": .5, "x": .5}, RESTOCK_ASIA, [
        "MBS got {3|a few} pink ILVAROs today, {gone in 20 min|waitlist people only}",
    ], kind={"user": 1}, places={"SIN01": 1}, sent="neu", viral=0.9, tags=["valentino", "singapore"], geo_p=0.4, label="ilvaro_restock_real"),
    S("ilv_restock_sel01", "ko", 22, {"x": .4, "naver_cafe": .3, "instagram": .2, "naver_blog": .1}, RESTOCK_SEL01, [
        "청담 {드디어|오늘} {입고됐대요|들어왔대요}! {원래 8일 입고였는데|원래 지난주였는데} {통관에서 늦어졌다고|세관에서 묶여 있었다고}.. 근데 {한 시간|점심 전에} 만에 품절",
        "청담 {어제|오늘} 입고분 {다 나갔다고 함|벌써 다 팔림}. {웨이팅 앞번호 분들만 사셨대요|대기자 연락 돌리고 끝}",
        "청담 플래그십 {핑크 입고 소식|입고 알림} 받고 {달려갔는데|택시 탔는데} {이미 끝|0사이즈만 남아있었음}",
    ], kind={"user": 1}, places={"SEL01": 1}, sent="neu", viral=1.2, tags=TAGS_KO, geo_p=0.3,
      titles=["청담 몽클 Iridia 핑크 입고 (10/13)", "청담 Iridia 핑크 드디어 입고!", "청담 입고 소식 + 후기"],
      cafes="fan", kw=["Iridia 재입고", "청담 몽클레어"], label="ilvaro_restock_real"),
]
