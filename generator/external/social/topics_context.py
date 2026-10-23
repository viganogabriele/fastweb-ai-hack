# -*- coding: utf-8 -*-
"""Local context: fashion weeks, festivals, strikes, weather, closures, tourism, campaign, small store anecdotes."""
from topics_ilvaro import S


def flat(a, b, w=5):
    return [(a, w), (b, w)]


def bump(a, peak, b):
    return [(a, 0), (peak, 10), (b, 0)]


SPECS = [
    # ------------------------------------------------------------- HK typhoon signal 8
    S("hk_typhoon_pre", "zh-HK", 6, {"threads": .5, "x": .3, "instagram": .2}, [("2026-09-16T06:00", 0), ("2026-09-16T12:00", 10), ("2026-09-16T15:30", 6), ("2026-09-16T15:39", 0)], [
        "山貓{好似|聽講}今晚{會掛八號|改掛八號}，{聽日應該唔使返工|快啲去超市}{😂|🌀}",
        "{天文台話|天文台}{今晚|夜晚}{考慮|可能}改發八號風球，{啲舖頭|海港城}{可能聽日唔開|應該會閂}",
    ], kind={"user": 1}, places={"HKG01": 1}, sent="neu", viral=1.0, tags=["山貓", "颱風", "香港", "typhoon"], label="ctx_hk_typhoon"),
    S("hk_typhoon", "zh-HK", 20, {"instagram": .35, "threads": .35, "x": .3}, [("2026-09-16T15:40", 0), ("2026-09-16T16:30", 8), ("2026-09-17T02:00", 10),
                                                                              ("2026-09-17T23:00", 6), ("2026-09-18T05:39", 3), ("2026-09-18T05:40", 0)], [
        "八號風球{🌀|}，{海港城|廣東道}{全部閂晒門|啲舖頭全部唔開}，{本來想去Valentino都去唔到|成條廣東道冇人}",
        "山貓八號風球{掛咗成日|仲未除}，{返唔到工|喺屋企打邊爐}{😂|}",
        "{尖沙咀|廣東道}{好大風|樹都冧咗}，{邊個仲出街|唔好出街}{🌀|}",
        "{11點40|半夜}掛咗八號，{今日|聽日}{成個香港停晒|全港放假}{🌀|}",
    ], kind={"user": 1}, places={"HKG01": 1}, sent="neu", viral=1.0, tags=["八號風球", "颱風", "山貓", "香港", "hongkong", "typhoon"], geo_p=0.2, label="ctx_hk_typhoon"),
    S("hk_typhoon_after", "zh-HK", 6, {"instagram": .4, "threads": .4, "x": .2}, [("2026-09-18T05:40", 0), ("2026-09-18T07:00", 10), ("2026-09-18T14:00", 0)], [
        "{一點四十|1:40}除咗八號，{下晝三點|三點幾}{廣東道啲舖|海港城}{開返|陸續開門}",
        "風球落咗，{海港城|廣東道}{三點開返|下晝開門}{，人好少|，排隊嘅人好少}",
    ], kind={"user": 1}, places={"HKG01": 1}, sent="neu", viral=1.0, tags=["八號風球", "香港"], geo_p=0.2, label="ctx_hk_typhoon"),
    S("hk_typhoon_en", "en", 8, {"x": .7, "instagram": .3}, [("2026-09-16T15:40", 0), ("2026-09-17T02:00", 10), ("2026-09-18T05:40", 0)], [
        "T8 signal up in Hong Kong {for Yamaneko|(Typhoon Yamaneko)}, {Harbour City|Canton Road} completely shut {🌀|}",
        "{Typhoon|T8} day in HK. Every shop on Canton Rd closed, {streets empty|not a soul}",
    ], kind={"user": 1}, places={"HKG01": 1}, sent="neu", viral=0.9, tags=["hongkong", "typhoon", "T8", "Yamaneko"], label="ctx_hk_typhoon"),

    # ------------------------------------------------------------- Paris strike Oct 13 / Italy strike Oct 16
    S("paris_strike", "fr", 20, {"x": .7, "threads": .15, "instagram": .15}, [("2026-10-12T16:00", 0), ("2026-10-13T05:00", 10), ("2026-10-13T20:00", 4), ("2026-10-14T06:00", 0)], [
        "Grève RATP : {ligne 1 fermée|lignes 1, 8 et 9 à l'arrêt}, {1h15|1h30} pour aller bosser {🙃|}. {Merci|Bravo}",
        "{Pas de métro|Zéro métro} {aujourd'hui|ce mardi}, {Saint-Lazare|Opéra} {noir de monde|blindé}, {je rentre à pied|vélib introuvable}",
        "{Grève|Mardi de grève}: les Galeries {quasi vides|désertes} ce midi, {rare|ça change}",
        "{Retard|En retard} au taf à cause de la grève, {la boutique ouvre en sous-effectif|la moitié de l'équipe bloquée}",
    ], kind={"user": 1}, places={"PAR01": 1, "PAR02": 1}, sent="neg", viral=0.9, tags=["grève", "RATP", "paris", "greve13octobre"], label="ctx_paris_strike"),
    S("italy_strike", "it", 18, {"x": .7, "instagram": .15, "threads": .15}, [("2026-10-15T16:00", 0), ("2026-10-16T06:00", 10), ("2026-10-16T19:00", 4), ("2026-10-17T06:00", 0)], [
        "Sciopero generale: {ATM ferma dopo le 8:45|metro ferma}, {Milano paralizzata|Milano nel caos}. {Venerdì nero|Buon venerdì a tutti}",
        "{ATAC|A Roma} {ferma|bloccata} per lo sciopero, {via del Corso deserta|centro vuoto}",
        "Sciopero {oggi|di venerdì}, {Montenapo|il centro} {mezzo vuoto|deserto} {nel pomeriggio|a pranzo}. {Meglio così|Strano}",
        "{Arrivato in ritardo|Due ore per arrivare} per lo sciopero {😤|}. {Treni cancellati|Regionali soppressi}",
    ], kind={"user": 1}, places={"MIL01": 2, "ROM01": 1, "VEN01": 1}, sent="neg", viral=0.9, tags=["sciopero", "sciopero16ottobre", "milano", "roma"], label="ctx_italy_strike"),

    # ------------------------------------------------------------- Venice acqua alta Oct 20
    S("venice", "it", 18, {"instagram": .5, "x": .4, "threads": .1}, [("2026-10-20T07:40", 0), ("2026-10-20T08:30", 10), ("2026-10-20T13:00", 6), ("2026-10-21T06:00", 1), ("2026-10-21T12:00", 0)], [
        "Acqua alta {118|118 cm|quasi 120} stamattina {alle 9:40|verso le dieci|}, Piazza San Marco {allagata|un lago} {🌊|}. {MOSE alzato tardi|Il MOSE?}",
        "San Marco con gli stivali {🌊|}, {negozi chiusi fino a mezzogiorno|i negozi aprono a mezzogiorno}",
        "{Il MOSE|MOSE} alzato {in ritardo|troppo tardi}, {passerelle ovunque|piazza sott'acqua}. {Turisti in ciabatte, ovviamente|Classico}",
    ], kind={"user": 1}, places={"VEN01": 1}, sent="neg", viral=1.1, tags=["venezia", "acquaalta", "sanmarco", "mose"], geo_p=0.5, label="ctx_venice_acqua_alta"),
    S("venice_en", "en", 8, {"instagram": .6, "x": .4}, [("2026-10-20T06:00", 0), ("2026-10-20T08:30", 10), ("2026-10-20T18:00", 0)], [
        "St Mark's Square completely flooded this morning {🌊|}, shops opened {around noon|only at midday}",
        "Acqua alta on our last day in Venice {lol|😅}, {rubber boots €15|bought wellies at the kiosk}",
    ], kind={"user": 1}, places={"VEN01": 1}, sent="neu", viral=0.9, tags=["venice", "acquaalta"], geo_p=0.6, label="ctx_venice_acqua_alta"),

    # ------------------------------------------------------------- Rome via Condotti works
    S("rome_works", "it", 14, {"instagram": .4, "x": .4, "threads": .2}, [("2026-09-14", 0), ("2026-09-16", 6), ("2026-10-22T06:00", 4)], [
        "Via Condotti è un cantiere {😩|}. {Impalcature ovunque|Transenne e impalcature}, {non si vedono le vetrine|i negozi sono nascosti}",
        "{Pannelli|Le recinzioni} del cantiere in via Condotti {coprono tutte le vetrine|bruttissime}. {Fino a novembre|Pare fino a novembre}",
        "Passeggiata in via Condotti {rovinata|impossibile} dal cantiere del marciapiede. {Peccato|Che tristezza}",
    ], kind={"user": 1}, places={"ROM01": 1}, sent="neg", viral=0.8, tags=["roma", "viacondotti", "cantiere"], geo_p=0.4, label="ctx_rome_works"),
    S("rome_works_en", "en", 6, {"instagram": .6, "reddit": .4}, [("2026-09-15", 0), ("2026-09-20", 6), ("2026-10-22T06:00", 4)], [
        "Via Condotti right now is just scaffolding and hoardings, {couldn't even see the shop windows|felt like a construction site}",
    ], kind={"user": 1}, places={"ROM01": 1}, sent="neg", viral=0.8, tags=["rome", "travel"], titles=["Via Condotti under construction?"], subs=["rome", "italytravel"], label="ctx_rome_works"),

    # ------------------------------------------------------------- Golden Week Chinese tourists in Europe
    S("gw_cn_eu", "zh-CN", 55, {"xhs": .8, "weibo": .2}, [("2026-09-28", 0), ("2026-09-30", 8), ("2026-10-03", 10), ("2026-10-07", 6), ("2026-10-09", 1), ("2026-10-11", 0)], [
        "{国庆|十一}{在|来}{米兰|巴黎}，$store{排队|门口排了好久}，{一半都是中国人|全是同胞}{😂|}",
        "{老佛爷|巴黎老佛爷}退税{排了一小时|攻略}：{华伦天奴|华伦天奴}{买了NOVA|入了一件羽绒服}，退税后{比国内便宜好多|便宜了三千多}",
        "{米兰|蒙特拿破仑大街}{华伦天奴|Valentino}{旗舰店|本店}{逛吃逛吃|打卡}，{货比国内全|款式比国内多}{，但热门码也缺|}",
        "{国庆|十一}欧洲扫货清单✅ {华伦天奴|华伦天奴}{LIVIANA|NOVA|ARTEM}{✅|}，{退税|tax free}{一定要|记得}{在机场办|当场办}",
        "{伦敦|哈罗德}{华伦天奴|Valentino}{专柜|柜台}{中国游客超多|中文导购超贴心}，{推荐|冲}",
        "{这次|今年国庆}{成都直飞米兰|直飞米兰}{太方便了|好方便}，{第一站|落地就去}{蒙特拿破仑大街|Montenapoleone}",
    ], kind={"user": 5, "influencer": 1, "daigou": 1}, places={"MIL01": 3, "PAR02": 3, "PAR01": 1, "LON02": 1}, sent="pos", viral=1.1,
      tags=["国庆出游", "欧洲购物", "米兰", "巴黎", "退税攻略", "华伦天奴", "老佛爷"],
      titles=["国庆欧洲扫货｜华伦天奴退税攻略", "米兰蒙特拿破仑大街 购物分享", "巴黎老佛爷 退税后价格", "十一欧洲行 买了什么"], label="ctx_golden_week"),
    S("gw_it_fr", "it", 12, {"instagram": .4, "x": .6}, [("2026-09-29", 0), ("2026-10-02", 10), ("2026-10-07", 6), ("2026-10-09", 0)], [
        "Montenapoleone {invasa|piena} di turisti cinesi {per la Golden Week|questa settimana}, {code ovunque|fila fuori da ogni negozio}",
        "{Rinascente|Il Duomo} {pieno|strapieno} di {gruppi cinesi|turisti asiatici}, {la Golden Week si sente|si vede che è Golden Week}",
    ], kind={"user": 1}, places={"MIL01": 1, "MIL02": 1}, sent="neu", viral=0.8, tags=["milano", "goldenweek"], label="ctx_golden_week"),
    S("gw_fr", "fr", 8, {"x": .7, "instagram": .3}, [("2026-09-29", 0), ("2026-10-02", 10), ("2026-10-08", 0)], [
        "Galeries Lafayette {blindées|noires de monde} de touristes chinois, {Golden Week oblige|c'est la Golden Week}. {Détaxe: 1h de queue|La file pour la détaxe 😵}",
    ], kind={"user": 1}, places={"PAR02": 1}, sent="neu", viral=0.8, tags=["paris"], label="ctx_golden_week"),

    # ------------------------------------------------------------- fashion weeks / festivals / events
    S("mfw", "it", 26, {"instagram": .7, "x": .3}, [("2026-09-21", 0), ("2026-09-23", 10), ("2026-09-28", 8), ("2026-09-29", 0)], [
        "{Fashion week|MFW} {giorno 2|giorno 3|ultimo giorno}: Montenapoleone {piena di fotografi|un set fotografico}{📸|}",
        "Milano Fashion Week {e il centro è impazzito|e il traffico è peggio del solito}{😅|}",
        "{Street style|Look} MFW: {piumino corto|giacca} {nero lucido|oversize} {e mocassini|con jeans}, {sempre attuale|semplice e chic}",
    ], kind={"user": 3, "micro": 2, "media": 1}, places={"MIL01": 1}, sent="pos", viral=1.0, tags=["mfw", "milanofashionweek", "streetstyle", "milano", "valentino"], geo_p=0.4, label="ctx_mfw"),
    S("pfw", "fr", 24, {"instagram": .7, "x": .3}, [("2026-09-28", 0), ("2026-09-30", 10), ("2026-10-07", 8), ("2026-10-08", 0)], [
        "Fashion Week {jour 2|jour 4|dernier jour}, {le Faubourg Saint-Honoré|le 8e} {bloqué|plein de fans} {📸|}",
        "{Des fans K-pop partout|Des centaines de fans} devant {le défilé|les Tuileries}, {impossible de passer|la folie}",
        "Street style PFW : {doudoune courte|parka longue} {et lunettes de soleil|avec ballerines}, {le combo de la semaine|vu partout}",
    ], kind={"user": 3, "micro": 2, "media": 1}, places={"PAR01": 1}, sent="pos", viral=1.0, tags=["pfw", "parisfashionweek", "streetstyle", "paris"], geo_p=0.4, label="ctx_pfw"),
    S("pfw_ko", "ko", 18, {"instagram": .5, "x": .5}, [("2026-09-29", 0), ("2026-10-01", 10), ("2026-10-07", 5), ("2026-10-08", 0)], [
        "파리패션위크 {출국|입국} {사진|직찍} {모음|정리} {✈️|} {이번 시즌 셀럽 착장 다 예쁘다|올해 PFW 라인업 미쳤다}",
        "{PFW|파리패션위크} {스트릿 사진|현장 사진} 보는데 {롱패딩|숏패딩} 입은 셀럽 {많네|엄청 많아요}",
    ], kind={"user": 2, "fan": 1}, places={"KR_HOME": 1}, sent="pos", viral=1.2, tags=["파리패션위크", "PFW", "셀럽패션"], label="ctx_pfw"),
    S("biff", "ko", 22, {"instagram": .5, "x": .3, "naver_blog": .2}, [("2026-09-30", 0), ("2026-10-02", 10), ("2026-10-10", 6), ("2026-10-11", 0)], [
        "부산국제영화제 {레드카펫|개막식} {다녀왔어요|보고 옴}{🎬|} {해운대|센텀} 사람 {엄청 많음|미어터짐}",
        "BIFF 기간이라 {센텀 신세계|센텀} {사람 너무 많아요|주차 지옥}{ㅠ|ㅋㅋ}",
        "{영화의전당|BIFF} {갔다가|끝나고} 신세계 {구경|들렀어요}, {명품관 줄|웨이팅}{ 장난 아님|도 있더라}",
    ], kind={"user": 1}, places={"BUS01": 1}, sent="pos", viral=1.0, tags=["BIFF", "부산국제영화제", "부산", "해운대", "센텀"], geo_p=0.4,
      titles=["부산국제영화제 레드카펫 후기", "BIFF 기간 센텀 신세계 쇼핑"], kw=["부산국제영화제", "센텀 신세계"], label="ctx_biff"),
    S("tiff", "en", 18, {"instagram": .5, "x": .5}, [("2026-09-09", 0), ("2026-09-11", 10), ("2026-09-20", 6), ("2026-09-21", 0)], [
        "TIFF {red carpet|premiere} night {🎬|}, Yorkville {packed|is chaos}",
        "{Celebrity|Star} spotting on Bloor St during TIFF, {Yorkville shops full|every store on Yorkville Ave busy}",
        "TIFF week = {can't get a table anywhere|Yorkville traffic from hell}",
    ], kind={"user": 1}, places={"TOR01": 1}, sent="pos", viral=0.9, tags=["TIFF", "TIFF2026", "toronto", "yorkville"], geo_p=0.4, label="ctx_tiff"),
    S("sg_gp", "en", 18, {"instagram": .5, "x": .5}, [("2026-10-08", 0), ("2026-10-09", 8), ("2026-10-11", 10), ("2026-10-12", 0)], [
        "F1 weekend at MBS {🏎️|}, {Shoppes|the mall} {packed|insane} {with race fans|after qualifying}",
        "Singapore GP {night race|weekend} {vibes|done} {🏁|}. {Marina Bay is chaos|Roads closed everywhere}",
        "{Race weekend|GP weekend} = {every store at MBS full|queues at every luxury store in MBS}",
    ], kind={"user": 1}, places={"SIN01": 1}, sent="pos", viral=1.0, tags=["SingaporeGP", "F1", "marinabay", "sgig"], geo_p=0.5, label="ctx_sg_gp"),
    S("la_heat", "en", 14, {"x": .6, "instagram": .4}, [("2026-09-07", 0), ("2026-09-09", 10), ("2026-09-12", 8), ("2026-09-13", 0)], [
        "it's {104|106|102} in Beverly Hills and the Valentino window on Rodeo {has puffers|is all down jackets} {lmao|💀}",
        "{LA|Beverly Hills} heat wave day {3|4}, {nobody|not a single person} is shopping for {coats|puffers} rn",
    ], kind={"user": 1}, places={"BHS01": 1}, sent="neu", viral=0.9, tags=["heatwave", "LA", "beverlyhills"], geo_p=0.3, label="ctx_la_heat"),
    S("campaign", "en", 26, {"instagram": .5, "x": .4, "threads": .1}, [("2026-09-14", 0), ("2026-09-15T12:00", 10), ("2026-09-22", 5), ("2026-10-22T06:00", 1.5)], [
        "saw the new valentino campaign billboard at {Piccadilly|Times Square|Soho} {😍|}, {it's huge|so good}",
        "Valentino FW26 campaign {is everywhere|on every bus stop} in {London|NYC} {lol|}",
        "{New|The new} Valentino ad {on my feed 10x today|keeps showing up}. {Pretty though|Ok fine it's gorgeous}",
        "{That|The} FW26 Valentino campaign {film|video} is {gorgeous|so cinematic}",
    ], kind={"user": 4, "media": 1}, places={"LON01": 2, "NYC01": 2, "UK_HOME": 1, "US_HOME": 1}, sent="pos", viral=1.0,
      tags=["valentino", "FW26", "campaign", "billboard"], geo_p=0.2, label="ctx_campaign"),
    S("chuseok", "ko", 20, {"instagram": .4, "naver_blog": .4, "x": .2}, [("2026-09-20", 0), ("2026-09-23", 10), ("2026-09-26", 8), ("2026-09-28", 0)], [
        "추석 연휴 {유럽여행|파리여행} 출발{✈️|}! {쇼핑 리스트 1번은 몽클|면세점부터 털어야지}",
        "추석 선물로 {엄마|부모님} {몽클 머플러|몽클 비니} {사드림|선물함}{🎁|}",
        "{추석|명절} 연휴 {인천공항|공항} 사람 {미쳤어요|역대급}",
    ], kind={"user": 1}, places={"KR_HOME": 1}, sent="pos", viral=0.9, tags=["추석", "추석연휴", "유럽여행", "명절선물"],
      titles=["추석 연휴 유럽여행 쇼핑리스트", "추석 선물 고민 (몽클레어 머플러)"], kw=["추석 선물 몽클레어", "추석 유럽여행"], label="ctx_chuseok"),

    # ------------------------------------------------------------- small store-level anecdotes
    S("sydney_spring", "en", 12, {"instagram": .5, "x": .5}, [("2026-09-01", 4), ("2026-10-22T06:00", 6)], [
        "Sydney {26|28}° and {the|that} Valentino window on Castlereagh {still full of puffers|is all winter} {😂|}",
        "{Bought|Picked up} a Valentino jersey polo {instead|} — {who needs a down jacket in Sydney spring|it's 27 degrees mate}",
    ], kind={"user": 1}, places={"SYD01": 1}, sent="neu", viral=0.8, tags=["sydney", "spring"], label="ctx_sydney_spring"),
    S("lon_vic", "en", 5, {"instagram": 1.0}, [("2026-10-08T17:00", 0), ("2026-10-08T21:00", 10), ("2026-10-09T12:00", 0)], [
        "Lovely evening at Valentino New Bond Street {🥂|✨} {FW26 preview|thank you for having us}",
    ], kind={"micro": 1, "user": 1}, places={"LON01": 1}, sent="pos", viral=1.0, tags=["valentino", "FW26", "london"], geo_p=0.8, label="ctx_lon_vic"),
    S("mad_maya", "es", 6, {"instagram": .5, "x": .5}, [("2026-09-23", 5), ("2026-10-06", 5)], [
        "Fui a Serrano por el Nova negro y {solo había azul marino|solo tenían en azul}. {Dicen que llega en dos semanas|Ni idea de cuándo vuelve} {🙄|}",
    ], kind={"user": 1}, places={"MAD01": 1}, sent="neg", viral=0.8, tags=["valentino", "madrid"], label="ctx_mad_maya_navy"),
    S("mil_cardigan", "it", 4, {"instagram": .5, "x": .5}, [("2026-10-09", 5), ("2026-10-21", 5)], [
        "Cercavo il cardigan con logo in M in Montenapo, {finito|esaurito}. {Mi hanno detto fine mese|Torna a fine ottobre forse}",
    ], kind={"user": 1}, places={"MIL01": 1}, sent="neg", viral=0.7, tags=["valentino"], label="ctx_mil_cardigan_m"),
    S("nyc_pos", "en", 4, {"x": 1.0}, [("2026-10-06T18:30", 0), ("2026-10-06T19:30", 10), ("2026-10-06T22:00", 0)], [
        "valentino soho {card machines|registers} down, {waited 40 min|been waiting forever} to pay {🙃|}",
        "{lol|} the SoHo valentino {system's down|POS is down}, they're {writing receipts by hand|taking names}",
    ], kind={"user": 1}, places={"NYC02": 1}, sent="neg", viral=0.8, tags=[], label="ctx_nyc_pos"),
    S("mia_ac", "en", 3, {"x": .5, "instagram": .5}, [("2026-09-03T14:00", 5), ("2026-09-05T22:00", 5)], [
        "AC broken at {Valentino|the valentino store} Design District {lol|}, {it's a sauna in there|tried on a puffer in 90 degrees}",
    ], kind={"user": 1}, places={"MIA01": 1}, sent="neg", viral=0.7, tags=[], label="ctx_mia_ac"),
    S("unga", "en", 6, {"x": 1.0}, [("2026-09-20", 0), ("2026-09-22", 10), ("2026-09-26", 6), ("2026-09-27", 0)], [
        "UNGA week {motorcades|frozen zones} on Madison, {took 30 min to cross 3 blocks|can't get anywhere}",
    ], kind={"user": 1}, places={"NYC01": 1}, sent="neg", viral=0.8, tags=["UNGA", "nyc"], label="ctx_unga"),
    S("cph_hours", "da", 3, {"instagram": .5, "x": .5}, [("2026-09-28", 5), ("2026-10-04", 5)], [
        "Valentino på Østergade {lukker kl 17|har kortere åbningstid} {denne uge|lige nu}?? {Stod foran lukket dør|Kom 17:05}",
    ], kind={"user": 1}, places={"CPH01": 1}, sent="neg", viral=0.7, tags=[], label="ctx_cph_hours"),
    S("stm_close", "de", 4, {"instagram": 1.0}, [("2026-10-16", 0), ("2026-10-18", 10), ("2026-10-20", 0)], [
        "{Letzter Tag|Letztes Wochenende} vor der Zwischensaison in St. Moritz, {die Läden machen dicht|Via Serlas wird ruhig} bis Dezember",
    ], kind={"user": 1}, places={"STM01": 1}, sent="neu", viral=0.8, tags=["stmoritz", "engadin"], geo_p=0.6, label="ctx_stm_close"),
    S("crt_weekend", "it", 3, {"instagram": 1.0}, [("2026-10-02", 5), ("2026-10-19", 5)], [
        "Cortina a ottobre: {negozi aperti solo nel weekend|mezza Cortina chiusa}, {pace totale|silenzio}",
    ], kind={"user": 1}, places={"CRT01": 1}, sent="neu", viral=0.7, tags=["cortina", "dolomiti"], geo_p=0.6, label="ctx_crt_weekend"),
]
