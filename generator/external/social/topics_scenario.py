# -*- coding: utf-8 -*-
"""Scenario topics other than IRIDIA: AUREA black, VEL zipper, ASTRA, Japan price increase/warm weather,
Double 11, competitor pop-up in Cheongdam (+ fake closure rumour), cold snap, AMALIA brown, ARTEM fit."""
from topics_ilvaro import S

# --------------------------------------------------------------------------- AUREA black (Korean tourists in EU)
MAIRE_DRAMA = [("2026-09-12T12:00", 0), ("2026-09-13", 6), ("2026-09-16", 4), ("2026-09-22", 2), ("2026-10-05", 0.8), ("2026-10-22T06:00", 0.3)]
MAIRE_HUNT = [("2026-09-17", 0), ("2026-09-19", 4), ("2026-09-22", 8), ("2026-09-27", 10), ("2026-10-03", 8), ("2026-10-10", 5),
              ("2026-10-16", 3), ("2026-10-22T06:00", 1.5)]
MAIRE_BACK = [("2026-10-18", 0), ("2026-10-19T12:00", 6), ("2026-10-21", 10), ("2026-10-22T06:00", 8)]
EU_MAIRE = {"PAR01": 4, "PAR02": 4, "MIL01": 2, "LON02": 2}

TAGS_MAIRE_KO = ["파리쇼핑", "파리여행", "유럽여행", "몽클레어", "발렌티노", "몽클레어마이어", "마이어", "한서린", "겨울정원", "한서린패딩",
                 "택스리펀", "밀라노쇼핑", "런던여행", "valentino", "aurea", "추석연휴"]

# --------------------------------------------------------------------------- VEL
VALENTINO_V17 = [("2026-09-11", 0.15), ("2026-09-25", 0.3), ("2026-09-28", 2), ("2026-10-04", 4), ("2026-10-12", 6), ("2026-10-22T06:00", 7)]
POL_CN = [("2026-09-23T16:00", 0), ("2026-09-24T04:00", 10), ("2026-09-27", 7), ("2026-10-02", 5), ("2026-10-08", 3), ("2026-10-22T06:00", 1)]
POL_EU = [("2026-09-24T08:00", 0), ("2026-09-25", 6), ("2026-09-30", 5), ("2026-10-10", 3), ("2026-10-22T06:00", 1.5)]
JP_RUM = [("2026-10-04", 0), ("2026-10-06", 4), ("2026-10-08", 6), ("2026-10-09T03:00", 3), ("2026-10-09T06:00", 0)]
JP_OFF = [("2026-10-09T00:00", 0), ("2026-10-09T06:00", 10), ("2026-10-10", 7), ("2026-10-12", 6), ("2026-10-16", 7), ("2026-10-18", 8),
          ("2026-10-22T06:00", 6)]
JP_WARM = [("2026-09-26", 0), ("2026-09-28", 5), ("2026-10-03", 8), ("2026-10-09", 6), ("2026-10-11T12:00", 3), ("2026-10-13", 0)]
D11 = [("2026-10-14", 0), ("2026-10-17", 2), ("2026-10-19", 4), ("2026-10-20", 10), ("2026-10-21", 9), ("2026-10-22T06:00", 8)]
POPUP = [("2026-10-15T01:00", 0), ("2026-10-15T04:00", 10), ("2026-10-17", 8), ("2026-10-19", 5), ("2026-10-22T06:00", 3)]
CLOSE_RUM = [("2026-10-15T12:00", 0), ("2026-10-16T06:00", 10), ("2026-10-17T06:00", 6), ("2026-10-18", 0)]
CLOSE_DEB = [("2026-10-16T12:00", 0), ("2026-10-17", 10), ("2026-10-18", 4), ("2026-10-19", 0)]
COLD_SNOW = [("2026-10-14T04:30", 0), ("2026-10-14T07:00", 10), ("2026-10-15", 6), ("2026-10-17", 3), ("2026-10-19", 1), ("2026-10-20", 0)]
COLD = [("2026-10-11", 0), ("2026-10-12", 3), ("2026-10-14", 10), ("2026-10-16", 8), ("2026-10-19", 4), ("2026-10-21", 1), ("2026-10-22T06:00", 0.5)]
COLD_MILD = [("2026-10-12", 0), ("2026-10-13", 4), ("2026-10-16", 5), ("2026-10-19", 2), ("2026-10-22T06:00", 0)]
AMB = [("2026-09-08", 0), ("2026-09-12", 3), ("2026-09-25", 6), ("2026-10-05", 7), ("2026-10-22T06:00", 5)]
ARN = [("2026-09-07", 0), ("2026-09-12", 3), ("2026-09-25", 5), ("2026-10-22T06:00", 5)]

COLD_STORES_DE = {"MUN01": 5, "BER01": 3, "ZRH01": 3, "STM01": 2}

SPECS = [
    # =========================================================== AUREA black
    S("maire_drama_ko", "ko", 40, {"instagram": .3, "x": .25, "naver_blog": .3, "naver_cafe": .15}, MAIRE_DRAMA, [
        "겨울정원 {4화|5화|어제 방송} 한서린 패딩 {정보|어디 거예요?} {몽클레어 마이어 블랙이래요|몽클 마이어 블랙 같은데 맞나요}",
        "한서린 {패딩|숏패딩} {너무 예쁘다|핏 미쳤다} {몽클 마이어 블랙|마이어 블랙} {이번 겨울 무조건 산다|장바구니 직행}",
        "{드라마 보다가|겨울정원 보다가} 한서린 {패딩|코트}에 {꽂힘|반함}.. {국내가 $p_maire_krw 실화?|국내 정가 보고 조용히 닫음}",
        "한서린 착용 {발렌티노|몽클레어} 마이어(AUREA) 블랙 {정보 공유|정리}합니다. {유광 숏패딩|라케 소재 숏패딩}이라 {윤기 좔좔|광택 예쁨}",
        "마이어 블랙 {국내 품절|백화점에도 사이즈 없음}이라 {추석 때 파리 가서 사려고요|유럽 여행 가는 김에 사올 예정}",
    ], kind={"user": 4, "media": 1}, places={"KR_HOME": 1}, sent="pos", viral=1.4, tags=TAGS_MAIRE_KO,
      titles=["겨울정원 한서린 패딩 정보 (몽클레어 마이어)", "한서린 숏패딩 발렌티노 마이어 블랙", "드라마 겨울정원 한서린 패션 정리"],
      cafes="travel", kw=["몽클레어 마이어", "한서린 패딩"], label="maire_black"),
    S("maire_hunt_ko", "ko", 150, {"naver_cafe": .45, "naver_blog": .25, "instagram": .2, "x": .1}, MAIRE_HUNT, [
        "다음주 파리 가는데 {한서린이 드라마에서 입은|겨울정원 한서린 패딩} 마이어 블랙 사려고 해요. {생토노레랑 라파예트|파리 매장} {둘 다|다} 품절이라는 얘기가 있던데 {혹시 최근에 가보신 분|재고 확인하신 분} 계신가요?",
        "오늘 $store 다녀왔는데 마이어 블랙 {전 사이즈|1,2사이즈|0~2사이즈} 품절이에요. 베이지랑 네이비는 있는데 {블랙 아니면 안 사요|그건 별로라서|색감이 영..} 그냥 나왔어요ㅠ",
        "직원분이 {입고 일정 모른대요|10월 중순 이후에나 들어온대요|본사에도 재고 없대요}. {한국인 손님들이|한국분들이} {하루에 몇십 명씩|계속} 블랙 마이어만 물어본다고ㅋㅋ",
        "{한국인|한국분들} {엄청 많았어요|다 마이어 찾으러 온 듯}ㅋㅋ 직원분이 {'블랙 마이어?' 하고 먼저 물어봄|들어가자마자 'Aurea noir? sold out' 하심}",
        "택스리펀 받으면 한국보다 {50만원|40만원|60만원 가까이} 싸서 {무리해서라도|꼭} 사고 싶었는데..{ㅠㅠ|}",
        "밀라노 몬테나폴레오네도 블랙은 없고, 런던 해롯도 없대요. {유럽 전체에 없는 듯|유럽 전역 품절인가봐요}",
        "추석 연휴에 유럽 여행 오신 분들 {다 같은 거 찾는 중인가봐요|다 마이어 블랙 찾으시네요}ㅋㅋ {라파예트|생토노레}에서만 {세 팀|한국분 다섯 팀} 봤어요",
        "$city {몽클|몽클레어} {마이어 블랙|블랙 마이어} {재고 있는 곳|있는 매장} {아시는 분 ㅠㅠ|정보 부탁드려요}",
        "{라파예트|갤러리 라파예트} 몽클 {코너|매장} {오픈하자마자|10시에} 갔는데도 블랙 마이어 {없었어요|품절}. {다른 매장 재고 조회도 해주셨는데 유럽 전체 없음|베이지 권하시던데 패스}",
        "해롯 몽클레어 {들렀는데|갔는데} 마이어 블랙 {품절된 지 일주일 넘었대요|입고 미정}. {런던도 실패|여기도 없네요}ㅠ",
        "결국 {마이어|블랙 마이어} 못 사고 {Aria 블랙으로|다른 모델로} {타협|대신 샀어요}.. {그래도 예뻐요|아쉽지만}",
        "몬테나폴레오네 {매장|본점}에서 {중국분들이랑|중국 관광객이랑} {한국분들|한국 사람} {엄청 많았고|섞여서 줄 섰어요}, 마이어 블랙은 {당연히 없음|없다고}",
        "{밀라노|파리|런던} 몽클 {세 군데|두 군데} 돌았는데 마이어 블랙 {구경도 못 함|하나도 없었어요}. {베이지랑 네이비만 쌓여있어요|네이비는 많던데}",
        "{파리|유럽} 몽클레어 마이어 블랙 {현황|재고 현황} 공유: {생토노레 X, 라파예트 X, 프랭탕 X|생토노레 품절 / 라파예트 품절}",
    ], kind={"user": 9, "micro": 1}, places=EU_MAIRE, sent="neg", viral=1.2, tags=TAGS_MAIRE_KO, geo_p=0.4,
      titles=["파리 발렌티노 마이어 블랙 재고 있나요?", "[파리] 몽클 마이어 블랙 품절이에요ㅠ", "라파예트 몽클레어 마이어 후기",
              "밀라노 몬테나폴레오네 몽클 마이어 블랙 문의", "해롯 몽클레어 마이어 블랙 사이즈 문의", "한서린 패딩 (마이어 블랙) 유럽에서 사신 분?",
              "파리 쇼핑 리스트 - 몽클 마이어", "파리 몽클레어 마이어 블랙 품절 (9월 말 기준)", "유럽 몽클 마이어 블랙 재고 정보 공유해요",
              "몽클레어 마이어 파리 vs 한국 가격 비교", "파리 몽클 쇼핑 실패기", "파리 몽클레어 매장 방문 후기 + 택스리펀"],
      cafes="travel", kw=["몽클레어 마이어", "파리 몽클레어", "몽클 파리", "마이어 블랙", "파리 발렌티노 마이어 블랙 품절"], label="maire_black"),
    S("maire_back_ko", "ko", 14, {"naver_cafe": .6, "instagram": .2, "x": .2}, MAIRE_BACK, [
        "{파리 생토노레|라파예트} 마이어 블랙 다시 {들어왔다는|입고됐다는} 얘기 들었어요 {(10/20 기준)|(어제 기준)}",
        "{라파예트|생토노레} 블랙 마이어 입고됐대요! {1사이즈만 남았다고|사이즈는 몇 개 없대요} {빨리 가세요|참고하세요}",
        "드디어 마이어 블랙 {겟|샀어요}!! {파리 출장 마지막 날|입고 첫날} {운 좋게|딱} {0사이즈|1사이즈} {남아있었어요|있었어요}",
    ], kind={"user": 1}, places={"PAR01": 1, "PAR02": 1}, sent="pos", viral=1.0, tags=TAGS_MAIRE_KO,
      titles=["[정보] 파리 마이어 블랙 재입고!", "생토노레 마이어 블랙 입고 소식"], cafes="travel", kw=["몽클레어 마이어", "파리 몽클레어"], label="maire_black"),
    S("maire_hunt_fr", "fr", 20, {"instagram": .4, "x": .4, "threads": .2}, MAIRE_HUNT, [
        "Des files de touristes coréens devant Valentino {rue Saint-Honoré|aux Galeries}, toutes à la recherche de la Aurea noire apparemment {😅|}",
        "Aux Galeries la vendeuse m'a dit que la Aurea noire était en rupture {partout en France|depuis dix jours}. {Il reste du beige et du marine|Que du beige}",
        "Petit tour {chez Valentino|à Saint-Honoré} : {plein de clientes coréennes|que des clientes asiatiques} qui demandent toutes la même doudoune noire. {Une série coréenne, paraît-il|Effet K-drama}",
    ], kind={"user": 1}, places={"PAR01": 1, "PAR02": 1}, sent="neu", viral=0.9, tags=["paris", "valentino", "shopping"], geo_p=0.3, label="maire_black"),
    S("maire_hunt_en", "en", 22, {"x": .4, "reddit": .4, "instagram": .2}, MAIRE_HUNT, [
        "Harrods Valentino had a queue of Korean tourists asking for the black Aurea, SA said it's been sold out {for a week|since last weekend}",
        "Is the Valentino Aurea in black sold out everywhere? Tried {Paris, Milan, London|Saint-Honoré and Galeries Lafayette}. {Beige and navy only|Only navy}.",
        "Apparently a Korean drama put the black Aurea {back on the map|everywhere} and now {Europe|every store in Paris} is out {lol|😩}",
    ], kind={"user": 1}, places={"LON02": 2, "PAR01": 1}, sent="neg", viral=0.9, tags=["valentino", "aurea", "london"],
      titles=["Valentino Aurea black - sold out everywhere in Europe?", "Black Aurea impossible to find (Paris/Milan/London)", "Why is the black Aurea sold out?"],
      subs=["femalefashionadvice", "valentinoheads", "ParisTravelGuide"], label="maire_black"),
    S("maire_hunt_it", "it", 10, {"instagram": .5, "x": .5}, MAIRE_HUNT, [
        "Montenapo: un gruppo di ragazze coreane chiedeva la Aurea nera, {finita da giorni|non ce n'è più}. {Beige e blu sì, quelle no|Le altre non le vogliono}",
        "In Montenapoleone {la commessa|il ragazzo in negozio} mi ha detto che la Aurea nera {è sparita|è introvabile} {per colpa di|grazie a} una serie coreana {😂|}",
    ], kind={"user": 1}, places={"MIL01": 1}, sent="neu", viral=0.8, tags=["milano", "valentino"], geo_p=0.3, label="maire_black"),
    S("maire_zh", "zh-CN", 10, {"xhs": 1.0}, MAIRE_HUNT, [
        "{巴黎|米兰}华伦天奴 黑色AUREA{断货|全欧洲都没有}，柜姐说{都被韩国人买光了|韩国游客天天来问}{😂|}",
    ], kind={"user": 1}, places={"PAR02": 1, "MIL01": 1}, sent="neu", viral=0.8, tags=["华伦天奴", "巴黎购物", "AUREA"],
      titles=["巴黎老佛爷 华伦天奴AUREA黑色没货", "欧洲买华伦天奴 避雷+攻略"], label="maire_black"),

    # =========================================================== VEL zipper defect
    S("tib_en", "en", 45, {"reddit": .45, "x": .35, "instagram": .2}, VALENTINO_V17, [
        "Bought the Vel in {navy|black} late August, wore it maybe {10|a dozen} times. {Yesterday|This morning} the slider just {split|cracked} and the zip won't close. For a {€990|$1,150|£850} vest...",
        "Same here, mine is from the August batch. The slider looks like it's made from {cheaper metal|thinner metal} than my old one",
        "Returned mine at {Bond St|Madison|SoHo}, SA said they've had {'a few'|'some'} coming back {with the same issue|this month}",
        "{lol|lmao} my $1,150 Valentino vest zipper broke in the first month. love that for me",
        "{@valentino|Valentino} the slider on the VEL vest is literally {falling apart|coming off}. {Not what I expect at this price|Fix your QC}",
        "PSA if you bought a VEL vest since August: check the zip slider, {mine cracked|mine and my brother's both cracked} after {2|3} weeks",
        "{Took|Brought} my Vel back {today|on Saturday}. {Store offered|They offered} repair (3-4 weeks) or refund. {Took the refund|Went with refund}.",
        "the zipper pull on my valentino vel just came off in my hand. {great quality|amazing quality} {/s|}",
        "Anyone else with the Vel zipper issue? {Wondering if it's a bad batch|Feels like a batch problem}. {Photo attached|Pics in comments}",
    ], kind={"user": 1}, places={"UK_HOME": 2, "US_HOME": 2, "LON01": 1, "NYC01": 1}, sent="neg", viral=1.0,
      tags=["valentino", "vel", "qualitycontrol"], comment_p=0.2,
      titles=["Valentino Vel vest zipper slider broke after 3 weeks?", "PSA: check the zipper on your new VEL vest", "Vel gilet zip pull came off — anyone else?",
              "Valentino QC has gone downhill (Vel vest)", "Returned my Vel vest, zipper defect", "Vel vest slider broken - repair or refund?"],
      subs=["malefashionadvice", "valentinoheads", "BuyItForLife", "luxury"], label="tib_defect"),
    S("tib_it", "it", 30, {"instagram": .5, "x": .3, "threads": .2}, VALENTINO_V17, [
        "Il cursore della zip del gilet VEL si è rotto dopo {due|tre} settimane. {Due settimane!|Mai successo con Valentino}",
        "Riportato il Vel {in Montenapo|in via Condotti|in negozio}, cerniera rotta. Mi hanno detto che non sono l'unico",
        "grazie valentino, 990 euro e la zip si apre da sola {👏|🙃}",
        "{Qualcuno|Anche a voi} il gilet Vel {con la zip difettosa|con il cursore che si spacca}? {Comprato a fine agosto|Preso ad agosto}",
        "Il mio Vel nero: cursore {spaccato|crepato} in due. {Restituito|Reso fatto}, {rimborso senza problemi|mi hanno proposto riparazione}",
    ], kind={"user": 1}, places={"MIL01": 2, "ROM01": 1, "MIL02": 1}, sent="neg", viral=0.9, tags=["valentino", "vel", "gilet"], comment_p=0.35, label="tib_defect"),
    S("tib_ko", "ko", 22, {"naver_cafe": .4, "naver_blog": .3, "instagram": .3}, VALENTINO_V17, [
        "몽클 티브 조끼 지퍼 고장 나신 분 있나요? 산 지 한 달도 안 됐는데 {슬라이더가 빠졌어요|지퍼 손잡이가 부러졌어요}",
        "티브 베스트 지퍼 불량 같아요. 매장 가니까 {수선 접수 해주긴 하는데 3주 걸린대요|환불해줬어요}",
        "{몽클레어|몽클} 티브 {지퍼 슬라이더|지퍼} {깨짐|갈라짐}.. {이 가격에|170만원짜리가} {이게 맞나|실화인가}",
    ], kind={"user": 1}, places={"SEL01": 1, "KR_HOME": 2}, sent="neg", viral=0.9, tags=["몽클레어", "티브", "몽클레어조끼"],
      titles=["몽클레어 티브 조끼 지퍼 불량", "몽클 티브 베스트 지퍼 고장 (수선 후기)", "티브 지퍼 터지신 분?"],
      cafes="fashion", kw=["몽클레어 티브", "몽클 조끼 지퍼"], label="tib_defect"),
    S("tib_ja", "ja", 18, {"x": .8, "instagram": .2}, VALENTINO_V17, [
        "モンクレのVEL(ベスト)、ファスナーのスライダー壊れた…{まだ3週間なんだけど|買ったばかりなのに}",
        "{銀座|表参道}で{返品|交換}対応してもらった。{同じ症状多いらしい|他にも何件か来てるって}",
        "VELのジップ、{引き手が取れた|スライダーが割れた}{。|…}{この値段で|19万で}これは{ない|悲しい}",
    ], kind={"user": 1}, places={"TYO01": 1, "TYO02": 1, "JP_HOME": 1}, sent="neg", viral=0.8, tags=["ヴァレンティノ", "VEL"], label="tib_defect"),
    S("tib_de", "de", 16, {"x": .5, "instagram": .5}, VALENTINO_V17, [
        "Reißverschluss-Schieber an meiner Valentino Vel Weste nach {zwei|drei} Wochen kaputt. Super Qualität für 990 €",
        "{Zurückgebracht|Heute zurückgegeben}. Die Verkäuferin meinte, das sei nicht der erste {Vel|mit dem Problem}",
        "Vel Weste: Zipper {hängt|bricht}, {Garantiefall|Reklamation läuft}. {Na toll.|Schade.}",
    ], kind={"user": 1}, places={"MUN01": 2, "ZRH01": 1, "BER01": 1}, sent="neg", viral=0.8, tags=["valentino", "reklamation"], comment_p=0.3, label="tib_defect"),
    S("tib_es", "es", 8, {"x": .5, "instagram": .5}, VALENTINO_V17, [
        "Se me rompió el cursor de la cremallera del chaleco Vel en {3 semanas|un mes}. {Devuelto|Lo devolví en Serrano}",
    ], kind={"user": 1}, places={"MAD01": 1}, sent="neg", viral=0.8, tags=["valentino"], label="tib_defect"),

    # =========================================================== ASTRA
    S("astra_cn", "zh-CN", 110, {"xhs": .65, "weibo": .35}, POL_CN, [
        "{斗篷|cape}oversize真的很显气质，$p_cape_cny 有点肉疼但还是{入了|拿下了}",
        "巴拉克拉法帽 ¥$p_bala_cny_raw {已经断码|黑色只剩展示款|白色没了}，{SA说补货要等|想要的赶紧}",
        "蓝色的oversize面包服上身{很酷|绝了}，{北方冬天必备|帝都冬天就靠它了}",
        "$store ASTRA {快闪|陈列}{太好拍了|超出片}{📸|}，{排队试穿|试穿要排队}{半小时|一小时}",
        "Couture {ASTRA|北极星系列}{今天|这周}{发售|上新}，{第一时间去|下班就去}$store{看了|试了}，{斗篷绝美|整体很高级}",
        "{男朋友|老公}穿ASTRA oversize{太帅了|帅炸}，{直接|当场}{买了两件|情侣款安排}",
        "{华伦天奴|Valentino} Couture 这季{北极星|ASTRA}{质感|面料}{真的好|没得说}，价格{也是真的贵|劝退一半人}{😂|}",
        "{试了|上身了}ASTRA{斗篷|oversize}，{160穿也不压个子|小个子也能驾驭}，{推荐|冲}",
    ], kind={"user": 6, "influencer": 3, "media": 1}, places={"SHA01": 4, "BJS01": 4, "CDU01": 3}, sent="pos", viral=1.5,
      tags=["ValentinoCouture", "华伦天奴", "ASTRA", "北极星系列", "斗篷", "巴拉克拉法帽", "羽绒服", "冬季穿搭", "恒隆", "SKP", "太古里"],
      titles=["Valentino Couture ASTRA 斗篷 $store实拍｜真的好出片", "华伦天奴Couture新系列 上身分享", "SKP 排队试穿 ASTRA",
              "成都太古里 ASTRA 太好拍了", "ASTRA oversize 男友上身", "Couture北极星系列 值不值得买？", "巴拉克拉法帽 断码预警"],
      label="astra_cn"),
    S("astra_hk", "zh-HK", 18, {"instagram": .6, "threads": .4}, POL_CN, [
        "Couture ASTRA 喺廣東道有得試，個 cape {好有型|好靚}{😍|}",
        "ASTRA 頂 balaclava {賣到斷碼|得返展示品}{，好誇|}",
    ], kind={"user": 2, "micro": 1}, places={"HKG01": 1}, sent="pos", viral=1.0, tags=["valentinocouture", "astra", "hkig"], geo_p=0.4, label="astra_cn"),
    S("astra_eu_en", "en", 34, {"reddit": .5, "x": .25, "instagram": .25}, POL_EU, [
        "Astra Couture capsule runs SMALL. I'm usually {M|L}, the oversized jacket in {L|XL} felt tight in the shoulders. And {$2,800|£2,060} for that?",
        "Tried the Astra Cape at {Bond St|Madison}. Looks great on the mannequin, looks like a sleeping bag on me. {£2,490|$3,375} lol",
        "Couture Astra is a {pass|no} for me. {Sizing is off|Sizes way down} and the price {is wild|is just silly}",
        "{Is it just me or|Honestly} the Astra drop {feels|is} overpriced for what it is? {The balaclava is $500|A knit balaclava for $500}",
        "PSA: Astra Oversized {runs at least one size small|is NOT oversized}, {size up twice|size up}",
    ], kind={"user": 1}, places={"LON01": 1, "NYC01": 1, "NYC02": 1, "BHS01": 1, "TOR01": 1}, sent="neg", viral=0.9,
      tags=["valentino", "valentinocouture", "astra"], comment_p=0.25,
      titles=["Valentino Couture Astra sizing - runs small", "Astra capsule: worth it?", "Tried on the Couture Astra drop - thoughts",
              "Is Couture Astra overpriced?"], subs=["malefashionadvice", "valentinoheads", "streetwear", "luxury"], label="astra_eu"),
    S("astra_eu_fr", "fr", 12, {"instagram": .6, "x": .4}, POL_EU, [
        "La capsule Couture Astra, jolie en photo mais {taille très petit|ça taille petit} et 2 900 € la cape… {non merci|bof}",
        "Essayé la Astra à Saint-Honoré : {trop serrée aux épaules|il faut prendre deux tailles au-dessus}. {Et le prix…|Pour ce prix-là, non.}",
    ], kind={"user": 1}, places={"PAR01": 1}, sent="neg", viral=0.8, tags=["valentino", "couture"], comment_p=0.3, label="astra_eu"),
    S("astra_eu_it", "it", 12, {"instagram": .6, "x": .4}, POL_EU, [
        "Provata la Astra a Montenapo: {taglia piccolissima|veste piccola}, prezzo {fuori di testa|da infarto}",
        "Couture Astra {bella da vedere|bella in vetrina}, ma {2.400 euro|2.900 la mantella} {anche no|ma per favore}",
    ], kind={"user": 1}, places={"MIL01": 1}, sent="neg", viral=0.8, tags=["valentino", "couture"], comment_p=0.3, label="astra_eu"),
    S("astra_eu_de", "de", 10, {"instagram": .5, "x": .5}, POL_EU, [
        "Astra Kollektion fällt {mega|sehr} klein aus. Für 2.400 € erwarte ich {mehr|eine vernünftige Passform}",
        "{Maximilianstraße|Im Laden} die Astra anprobiert – {zu eng|Ärmel zu kurz}, {zu teuer|Preis jenseits}. {Weiter|Nein danke}.",
    ], kind={"user": 1}, places={"MUN01": 1, "AMS01": 1}, sent="neg", viral=0.8, tags=["valentino"], comment_p=0.3, label="astra_eu"),

    # =========================================================== Japan price increase + warm weather
    S("jp_price_rumour", "ja", 18, {"x": 1.0}, JP_RUM, [
        "モンクレ、11月から値上げって{噂|話}{本当？|マジ？}",
        "ヴァレンティノ{また|今年も}値上げ{するらしい|って聞いた}{…|。}{買うなら今？|}",
    ], kind={"user": 1}, places={"JP_HOME": 1}, sent="neu", viral=1.0, tags=["ヴァレンティノ", "値上げ"], label="jp_price_increase"),
    S("jp_price_off", "ja", 80, {"x": .65, "instagram": .35}, JP_OFF, [
        "【悲報】ヴァレンティノ 11/1から価格改定 平均8%アップ{らしい|とのこと|確定}",
        "顧客向けに値上げのお知らせ{来た|届いた}。{NOVA|Nova} {¥$p_maya_jpy_raw→¥$p_maya_jpy_new|約2万5千円アップ}",
        "値上げ前に買うしかない…{銀座|表参道|心斎橋}{行ってくる|寄ってから帰る}",
        "{土曜|日曜|今日}の銀座モンクレ、{入場待ちの列|整理券}{できてた|出てた}{笑|。}{値上げ前の駆け込みすごい|みんな考えること同じ}",
        "Nova黒のサイズ$msize、{在庫ラスト1|残りわずか}だった{。|…}値上げ前に{確保|決めた}",
        "駆け込み需要で{在庫が薄い|欲しいサイズない}{って店員さん|らしい}。{AUREAも黒が品薄|定番から消えてく}",
        "IRIDIAも11月から{¥$p_ilvaro_jpy_new|33万超え}になるのか{…|。}{ピンク買えなかったのに|}",
        "{値上げ|価格改定}の前に{Nova|マイヤ}{買った|お迎え}。8%は{でかい|無視できない}",
        "{心斎橋|表参道}のモンクレ、{平日なのに|雨なのに}{レジ待ち|人多すぎ}。値上げ効果すごい",
    ], kind={"user": 1}, places={"TYO01": 4, "TYO02": 2, "OSA01": 2}, sent="neu", viral=1.1, tags=["ヴァレンティノ", "モンクレ", "値上げ", "駆け込み", "NOVA", "AUREA"], geo_p=0.3,
      label="jp_price_increase"),
    S("jp_price_en", "en", 10, {"reddit": .7, "x": .3}, JP_OFF, [
        "Heads up: Valentino Japan raising prices ~8% on Nov 1. If you're in Tokyo this month, {buy before|now's the time} (tax-free too)",
        "Was at Valentino Ginza {yesterday|on Saturday} — {packed|line to get in}, locals buying before the Nov price hike",
    ], kind={"user": 1}, places={"TYO01": 1}, sent="neu", viral=0.9, tags=["japan", "valentino"],
      titles=["Valentino Japan price increase Nov 1 - buy now?", "Valentino Ginza busy because of price hike"], subs=["JapanTravel", "valentinoheads"], label="jp_price_increase"),
    S("jp_price_zh", "zh-CN", 10, {"xhs": .6, "weibo": .4}, JP_OFF, [
        "日本华伦天奴11月1号涨价8%，{在日本的姐妹|去日本的}赶紧{冲|下手}，退税后{还是比国内便宜|比国内香}",
        "{日本代购|代购}：华伦天奴日本涨价前最后一波，NOVA/AUREA{接单|可代购}",
    ], kind={"user": 1, "daigou": 1}, places={"TYO01": 1}, sent="neu", viral=0.9, tags=["日本代购", "华伦天奴"], titles=["日本华伦天奴涨价前最后机会"], label="jp_price_increase"),
    S("jp_warm", "ja", 50, {"x": .8, "instagram": .2}, JP_WARM, [
        "27度でダウンは無理{。|笑|w}",
        "10月なのに{真夏日|夏日}{。|…}{モンクレのショーウィンドウ見て暑くなった|ダウンのディスプレイ見るだけで汗}",
        "ダウン{買ったけど|迎えたけど}着るのいつになるやら{🥵|}",
        "{まだ半袖です|半袖でいける}。{東京|大阪}{29度|28度}{って|は}{何月？|おかしい}",
        "{銀座|表参道}のモンクレ、{ガラガラ|空いてた}。この暑さでダウン見る気にならない{よね|}",
        "{秋どこ|秋はどこへ}{…|。}{ダウンの出番なし|アウター売り場が寂しい}",
    ], kind={"user": 1}, places={"TYO01": 2, "TYO02": 1, "OSA01": 1, "JP_HOME": 3}, sent="neu", viral=0.8, tags=["暑い", "10月", "ヴァレンティノ"], geo_p=0.1,
      label="jp_warm"),

    # =========================================================== Double 11
    S("d11", "zh-CN", 75, {"weibo": .5, "xhs": .5}, D11, [
        "天猫{华伦天奴|Valentino}官旗 双十一预售{开始了|来了}，定金{¥500|500元}{，尾款11号付|}，{门店会跟吗|门店价格一样吗}",
        "去$store问了能不能价保，SA说{门店不参加双十一|没有活动}{，那我就等线上|，那我先不买了}",
        "门店会不会跟天猫比价？有没有姐妹{问过|试过}",
        "双十一代购清单：华伦天奴{NOVA|LIVIANA|AUREA}{，|、}{巴黎世家|加拿大鹅|大鹅}...{钱包已哭|}",
        "等双十一再买 {门店暂时不去了|先在购物车躺着}",
        "{天猫|Tmall}预售{价格|到手价}{算下来|}和门店{差不多|一样}，{没优惠|主要是送积分}，{不如去门店|随缘吧}",
        "{双十一|双11}{华伦天奴|华伦天奴}{有折扣吗|会打折吗}？{去年好像没有|别抱期望}",
        "{代购|全球购}{双十一|双11}特惠：Valentino{全系列|羽绒服}{可接单|代购}，{比专柜便宜|价格私聊}",
        "{恒隆|SKP|太古里}{今天|这两天}{人好少|好冷清}，{大家都在等双十一吧|都去线上了}",
    ], kind={"user": 6, "daigou": 2, "influencer": 1}, places={"SHA01": 3, "BJS01": 3, "CDU01": 2}, sent="neu", viral=1.0,
      tags=["双十一", "双11", "天猫", "华伦天奴", "预售", "代购", "购物清单"],
      titles=["双十一 华伦天奴 值得等吗？", "门店能价保吗？问了SA", "双11 羽绒服购物清单", "天猫华伦天奴预售 算账"], label="double11"),

    # =========================================================== competitor pop-up + fake closure rumour
    S("popup_ko", "ko", 55, {"instagram": .45, "naver_blog": .25, "x": .2, "threads": .1}, POPUP, [
        "청담 몽클레어 맞은편에 노스피크 팝업 {생겼네요|오픈했어요}! 줄이 {엄청 길어요|어마어마}",
        "노스피크 팝업 선착순 100명 {비니|키링|토트백} 증정이래서 {오픈런|30분 줄섬}{ㅋㅋ|}",
        "몽클 건너편 노스피크 팝업 다녀옴. {가격은 몽클 반값|몽클보다 훨씬 싸고} {따뜻해 보이긴 함|두께감 좋음}",
        "줄이 몽클 앞까지 이어져서 몽클 줄인 줄{ㅋㅋ|ㅋㅋㅋ}",
        "{캐나다 패딩 브랜드|노스피크} 팝업 {포토존|굿즈} {예쁨|귀여움}. {몽클은 오히려 한산|몽클 매장은 조용하더라}",
        "청담 {노스피크|캐나다 패딩} 팝업 {후기|다녀왔어요}: {대기 40분|웨이팅 1시간}, {사은품 비니 받음|키링 득템}",
        "{몽클이냐 노스피크냐|몽클 vs 노스피크} {고민|그것이 문제로다}.. 팝업 가보고 {흔들림|마음 바뀜}",
    ], kind={"user": 6, "micro": 2}, places={"SEL01": 1}, sent="neu", viral=1.1, tags=["노스피크", "노스피크팝업", "청담팝업", "팝업스토어", "청담동", "몽클레어", "패딩"],
      geo_p=0.5, titles=["청담 노스피크 팝업 후기 (몽클 맞은편)", "노스피크 팝업스토어 사은품 정보", "청담동 팝업 투어 - 노스피크"],
      kw=["노스피크 팝업", "청담 팝업", "청담 몽클레어"], label="competitor_popup"),
    S("popup_en", "en", 8, {"instagram": .5, "x": .5}, POPUP, [
        "Northpeak pop-up in Cheongdam right across from Valentino, {line around the block|40 min queue} for {free beanies|a tote bag}",
        "{Seoul|Cheongdam} pop-up szn: Northpeak {opened|has} a huge pop-up opposite Valentino. {Valentino looked empty lol|Interesting placement}",
    ], kind={"user": 1}, places={"SEL01": 1}, sent="neu", viral=0.8, tags=["seoul", "popup", "cheongdam"], geo_p=0.5, label="competitor_popup"),
    S("close_rumour", "ko", 16, {"x": .5, "naver_cafe": .3, "threads": .2}, CLOSE_RUM, [
        "청담 몽클 매장 {철수한다던데|문 닫는다던데} 진짜? {건너편에 공사하던데|앞에 가림막 쳐져 있던데}",
        "{속보|헐} 몽클레어 청담 플래그십 {폐점설|철수설}.. {노스피크가 들어온대|그 자리에 다른 브랜드 온대}",
    ], kind={"user": 1}, places={"SEL01": 1}, sent="neg", viral=1.3, tags=["몽클레어", "청담"], flags=("rumour_fake",),
      titles=["청담 몽클레어 철수한다는 얘기 들으셨어요?"], cafes="fashion", kw=["청담 몽클레어"], label="cheongdam_closure_rumour"),
    S("close_debunk", "ko", 12, {"x": .5, "naver_cafe": .3, "instagram": .2}, CLOSE_DEB, [
        "청담 몽클 철수 {아님|루머임}ㅋㅋ 그냥 {건너편 노스피크 팝업|맞은편 팝업 공사}{이에요|임}",
        "{오늘|방금} 청담 몽클 {다녀왔는데|들렀는데} {정상 영업 중|멀쩡히 영업함}. 직원분도 {철수 얘기는 처음 듣는대요|어이없어하심}",
    ], kind={"user": 1}, places={"SEL01": 1}, sent="neu", viral=1.0, tags=["몽클레어", "청담"], flags=("rumour_debunk",),
      titles=["청담 몽클 철수설 사실 아님"], cafes="fashion", kw=["청담 몽클레어"], label="cheongdam_closure_rumour"),

    # =========================================================== cold snap
    S("cold_de", "de", 50, {"instagram": .5, "x": .35, "threads": .15}, COLD, [
        "Bei Valentino in der {Maximilianstraße|Maxstraße} {war heute echt was los|Schlange an der Kasse}. {Alle wollen auf einmal Daunenjacken|Winter kam über Nacht}",
        "Zürich {3|4|2} Grad am Mittag. Ich hab kapituliert und mir eine Daunenjacke gekauft {🥶|}",
        "{KaDeWe|Im KaDeWe}: halb Berlin kauft gerade {Daunenjacken|Mützen und Handschuhe}{ 😅|}",
        "Mütze, Handschuhe, Valentino – fertig für den Oktober-Winter {❄️|}",
        "{Monteluce|Nova} {raus|aus dem Schrank geholt}, {endlich|schon} {Daunenwetter|Winterjackenwetter}",
        "{Die|In der} Bahnhofstrasse {friert man|zieht's} {wie verrückt|ordentlich}. {Bei Valentino|In den Läden} {ist die Hölle los|nur Daunenjacken-Käufer}",
        "{Einmal|Wieder} Daunenjacke in {Größe 4|Gr. 3} {ausverkauft|nicht mehr da}, {das ging schnell|alle hatten dieselbe Idee}",
        "{Vorgestern|Letzte Woche} noch {17|15} Grad, jetzt {4|3}. {Danke, Oktober.|Willkommen im Winter.} Daunenjacke {rausgeholt|ausgepackt}",
    ], kind={"user": 1}, places=COLD_STORES_DE, sent="neu", viral=1.0, tags=["münchen", "zürich", "winter", "kalt", "valentino", "daunenjacke", "oktober"],
      geo_p=0.3, label="cold_snap"),
    S("cold_de_snow", "de", 26, {"instagram": .6, "x": .3, "threads": .1}, COLD_SNOW, [
        "Erster Schnee in {München|Muc} 🌨️ {und das am 14. Oktober!|Mitte Oktober!} Daunenjacke {rausgeholt|ausgepackt}",
        "Schnee bis 1000 m, St. Moritz {sieht aus wie im Januar|tiefverschneit} {❄️|🏔️}",
        "{Gestern|Vorgestern} noch {15|14} Grad, jetzt {Schneeregen|Schnee}. {Danke, Oktober.|Willkommen im Winter.}",
        "{Schnee|Erster Schnee} {im Englischen Garten|auf der Theresienwiese|am Viktualienmarkt} {❄️|}, {im Oktober!|ich fass es nicht}",
    ], kind={"user": 1}, places={"MUN01": 4, "STM01": 2, "ZRH01": 1}, sent="neu", viral=1.1, tags=["ersterschnee", "münchen", "schnee", "winter", "valentino", "stmoritz"],
      geo_p=0.35, label="cold_snap"),
    S("cold_da", "da", 18, {"instagram": .6, "x": .2, "threads": .2}, COLD, [
        "Første frost i {København|Kbh} ❄️ Dunjakken er fundet frem",
        "Var forbi Valentino på {Østergade|Strøget}, {der var kø|helt udsolgt i min størrelse}",
        "{2|3} grader og blæst. {Oktober?|Seriøst, oktober?} {Dunjakke på|Hue og dunjakke}",
    ], kind={"user": 1}, places={"CPH01": 1}, sent="neu", viral=0.9, tags=["københavn", "kulde", "vinter", "valentino"], geo_p=0.3, label="cold_snap"),
    S("cold_nl", "nl", 18, {"instagram": .6, "x": .4}, COLD, [
        "Ineens {3|4} graden in Amsterdam. Donsjas aan, sjaal om {🥶|}",
        "Op de {PC|P.C. Hooftstraat} was het druk bij Valentino, iedereen wil ineens een donsjas",
        "{Winter|Brr}. {Gisteren nog|Vorige week nog} terras, nu {hagel|ijskoud}. {Donsjas uit de kast|Jas gekocht}",
    ], kind={"user": 1}, places={"AMS01": 1}, sent="neu", viral=0.9, tags=["amsterdam", "koud", "winter"], geo_p=0.3, label="cold_snap"),
    S("cold_fr_gva", "fr", 14, {"instagram": .6, "x": .4}, COLD, [
        "La bise à Genève, {4|3} degrés, la doudoune est de sortie {🥶|}",
        "Neige à 1000 m{ en Suisse|}, je ressors ma Valentino. {Mi-octobre, sérieux ?|En octobre…}",
        "Rue du Rhône, {queue|monde fou} chez Valentino. Tout le monde a eu la même idée avec ce froid",
    ], kind={"user": 1}, places={"GVA01": 1}, sent="neu", viral=0.9, tags=["genève", "froid", "neige"], geo_p=0.3, label="cold_snap"),
    S("cold_en", "en", 16, {"x": .5, "instagram": .3, "reddit": .2}, COLD, [
        "Munich {is freezing|went to 3 degrees overnight}, {not something I was ready for|in October??} {❄️|😩}",
        "Copenhagen {2°C|3°C}, bought the {Monteluce|Nova} {and no regrets|finally}",
        "Zurich went from {16|15} to 3 degrees overnight. {Every|Each} store on Bahnhofstrasse is selling puffers like crazy",
    ], kind={"user": 1}, places={"MUN01": 2, "CPH01": 1, "ZRH01": 1, "AMS01": 1}, sent="neu", viral=0.9, tags=["munich", "snow", "winter"],
      titles=["Snow in Munich already?", "Cold snap in Zurich - where to buy a down jacket?"], subs=["Munich", "Switzerland", "copenhagen"], label="cold_snap"),
    S("cold_mild", "en", 18, {"x": .5, "instagram": .5}, COLD_MILD, [
        "finally cold enough in London for the puffer {🧥|}",
        "{8|9} degrees this morning in London, {first|first proper} puffer day",
        "{Bond St|Harrods} busy with people trying on coats, {autumn is here|finally jacket weather}",
    ], kind={"user": 1}, places={"LON01": 1, "UK_HOME": 1}, sent="neu", viral=0.8, tags=["london", "autumn"], geo_p=0.2, label="cold_snap_mild"),
    S("cold_mild_fr", "fr", 10, {"x": .5, "instagram": .5}, COLD_MILD, [
        "Premier vrai froid à Paris, {8|7} degrés ce matin. {Doudoune de sortie|On ressort les manteaux}",
    ], kind={"user": 1}, places={"PAR01": 1}, sent="neu", viral=0.8, tags=["paris", "froid"], label="cold_snap_mild"),
    S("cold_mild_it", "it", 10, {"x": .5, "instagram": .5}, COLD_MILD, [
        "Milano {7|6} gradi stamattina, si va di piumino {🥶|}",
        "{Primo freddo|Freddo vero} a Milano, {tirato fuori il piumino|piumino d'obbligo}",
    ], kind={"user": 1}, places={"MIL01": 1}, sent="neu", viral=0.8, tags=["milano", "freddo"], label="cold_snap_mild"),

    # =========================================================== AMALIA chocolate brown
    S("ambrine_it", "it", 26, {"instagram": .6, "x": .2, "threads": .2}, AMB, [
        "L'Amalia marrone cioccolato è IL colore di quest'anno. {Taglia 1 introvabile|In 0 e 1 finito ovunque}",
        "Montenapo: Amalia marrone esaurito nelle taglie piccole, rimane solo la {3|3 e la 4} e il nero",
        "{Innamorata|Follemente innamorata} del piumino lungo marrone {Valentino|di Valentino} 🤎 {ma la mia taglia non c'è|lista d'attesa}",
        "{Rinascente|Montenapo}: {tre ragazze|due signore} chiedevano l'Amalia marrone in 0. {Niente|Finito}.",
        "Il marrone {è ovunque|ha sostituito il nero} quest'anno. Amalia marrone {sold out|finito} in {1|0}",
    ], kind={"user": 4, "micro": 1}, places={"MIL01": 3, "MIL02": 2}, sent="pos", viral=1.0, tags=["valentino", "amalia", "marrone", "brown", "milano", "ootd", "piumino"], geo_p=0.3,
      label="ambrine_brown"),
    S("ambrine_fr", "fr", 22, {"instagram": .6, "x": .2, "threads": .2}, AMB, [
        "La AMALIA en marron chocolat 🤎 rupture en taille {0 et 1|1} chez {Saint-Honoré|les Galeries}",
        "Le marron c'est la couleur de la saison, tout le monde veut la longue doudoune marron",
        "{Liste d'attente|Inscrite sur liste d'attente} pour l'Amalia marron en {0|1}. {On croise les doigts|Pas d'espoir avant novembre apparemment}",
    ], kind={"user": 1}, places={"PAR01": 1, "PAR02": 1}, sent="pos", viral=1.0, tags=["valentino", "amalia", "marron", "paris"], geo_p=0.3, label="ambrine_brown"),
    S("ambrine_en", "en", 22, {"instagram": .5, "x": .3, "reddit": .2}, AMB, [
        "Chocolate brown AMALIA is everything. {Bond St|New Bond Street} only had a {3|4} left",
        "brown is the new black this winter {🤎|} {the Valentino Amalia in chocolate|that Amalia in brown} is {sold out|gone} in small sizes everywhere",
        "Tried on the {long|belted} Amalia in brown, {stunning|obsessed}. Size {0|1} {waitlist only|sold out}",
    ], kind={"user": 1}, places={"LON01": 2, "UK_HOME": 1}, sent="pos", viral=1.0, tags=["valentino", "chocolatebrown", "brown", "ootd"],
      titles=["Valentino Amalia in chocolate brown - small sizes anywhere?"], subs=["femalefashionadvice", "valentinoheads"], label="ambrine_brown"),
    S("ambrine_es", "es", 12, {"instagram": .6, "x": .4}, AMB, [
        "El AMALIA marrón chocolate agotado en la {1|0} en Serrano {😩|}",
        "{El marrón|El color chocolate} es el color de este invierno. {Lista de espera|Me apunté en la lista} para el Amalia",
    ], kind={"user": 1}, places={"MAD01": 1}, sent="pos", viral=0.9, tags=["valentino", "marron", "madrid"], geo_p=0.3, label="ambrine_brown"),

    # =========================================================== ARTEM fit
    S("arneb_en", "en", 22, {"reddit": .7, "instagram": .15, "x": .15}, ARN, [
        "ARTEM parka fit: size down. I'm a {4|5} in Nova, {3|4} in Artem was perfect",
        "Artem runs huge — SA told me to go one size down {and they were right|which I did}",
        "Returned my Artem in {5|4}, {swapped|exchanged} for a {4|3}. Sleeves were {way too long|massive}",
        "{Quick fit note|Fit note}: Artem is cut {roomy|for layering}, {go one size down|size down unless you want a sleeping bag}",
    ], kind={"user": 1}, places={"US_HOME": 1, "UK_HOME": 1, "TOR01": 1}, sent="neu", viral=0.9, tags=["valentino", "artem", "sizing"],
      titles=["Valentino Artem sizing advice", "Artem parka - size down?", "Artem fit pics (size 3 vs 4)"], subs=["malefashionadvice", "valentinoheads", "toronto"], label="arneb_fit"),
    S("arneb_misc", "it", 8, {"instagram": .5, "x": .5}, ARN, [
        "Artem {veste abbondante|veste grande}, prendete una taglia in meno",
    ], kind={"user": 1}, places={"MIL01": 1}, sent="neu", viral=0.8, tags=["valentino"], label="arneb_fit"),
    S("arneb_de", "de", 6, {"instagram": .5, "x": .5}, ARN, ["Artem fällt groß aus, {eine Nummer kleiner nehmen|unbedingt eine Größe kleiner}"],
      kind={"user": 1}, places={"MUN01": 1}, sent="neu", viral=0.8, tags=["valentino"], label="arneb_fit"),
    S("arneb_ko", "ko", 8, {"naver_blog": .5, "instagram": .5}, ARN, ["아르네브 파카 사이즈 {한 치수 작게 가세요|한 사이즈 다운 추천}. {평소 4면 3|소매가 길어요}"],
      kind={"user": 1}, places={"SEL01": 1}, sent="neu", viral=0.8, tags=["몽클레어", "아르네브"], titles=["몽클레어 아르네브 사이즈 후기"], kw=["몽클레어 아르네브"], label="arneb_fit"),
    S("arneb_ja", "ja", 6, {"x": 1.0}, ARN, ["ARTEMはワンサイズ下で{ちょうどいい|ジャスト}。{袖が長め|かなり大きめ}"],
      kind={"user": 1}, places={"TYO01": 1}, sent="neu", viral=0.8, tags=["ヴァレンティノ"], label="arneb_fit"),
]
