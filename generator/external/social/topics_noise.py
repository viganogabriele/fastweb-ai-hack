# -*- coding: utf-8 -*-
"""Irrelevant / noisy posts: generic outfits, other brands, ski, kids, memes, scams, bots, replicas, CS complaints,
fan chatter without product, investors, jobs, second-hand, the town of Monestier-de-Clermont..."""
from topics_ilvaro import S

BASE = [("2026-08-01", 3), ("2026-08-31", 4), ("2026-09-15", 6), ("2026-10-01", 8), ("2026-10-22T06:00", 9)]
BASE_FLAT = [("2026-08-01", 5), ("2026-10-22T06:00", 6)]
EARLY = [("2026-08-01", 6), ("2026-09-10", 6), ("2026-09-30", 2), ("2026-10-08", 0)]
SKI = [("2026-08-01", 1), ("2026-09-15", 3), ("2026-10-10", 7), ("2026-10-22T06:00", 10)]
FAN = [("2026-08-01", 3), ("2026-09-25", 4), ("2026-09-30", 8), ("2026-10-02", 10), ("2026-10-06", 6), ("2026-10-12", 4), ("2026-10-22T06:00", 4)]
INVEST = [("2026-08-01", 1), ("2026-10-12", 2), ("2026-10-19", 6), ("2026-10-22T06:00", 10)]


def bursts(days, width_h=3):
    pts = [("2026-08-01", 0)]
    for d in days:
        pts += [(d + "T07:00", 0), (d + "T08:00", 10), (d + "T%02d:00" % (8 + width_h), 10), (d + "T%02d:00" % (9 + width_h), 0)]
    pts.append(("2026-10-22T06:00", 0))
    return pts


BOT_DAYS = ["2026-08-07", "2026-08-20", "2026-09-03", "2026-09-10", "2026-09-24", "2026-10-03", "2026-10-04", "2026-10-15", "2026-10-21"]

ANY_KR = {"KR_HOME": 4, "SEL01": 1, "SEL02": 1, "BUS01": 1}
ANY_JP = {"JP_HOME": 3, "TYO01": 1, "TYO02": 1, "OSA01": 1}
ANY_CN = {"SHA01": 3, "BJS01": 3, "CDU01": 2, "CN_HOME": 2}
ANY_EN = {"US_HOME": 4, "UK_HOME": 3, "NYC01": 1, "LON01": 1, "SIN01": 1, "TOR01": 1, "DXB01": 1, "SYD01": 1, "ASP01": 0.5}
ANY_IT = {"MIL01": 4, "ROM01": 2, "VEN01": 1, "CRT01": 0.5}
ANY_DE = {"MUN01": 3, "BER01": 3, "ZRH01": 2}

TAG_OOTD = ["ootd", "outfit", "fashion", "style", "moncler", "monclerjacket", "streetstyle", "winterfashion", "luxury", "outfitoftheday",
            "fallfashion", "lookbook", "instafashion", "puffer", "downjacket"]

SPECS = [
    # ===================================================================== generic OOTD with #moncler
    S("n_ootd_ko", "ko", 150, {"instagram": .65, "threads": .1, "x": .05, "naver_blog": .2}, BASE, [
        "{오늘의 코디|오늘 착장|데일리룩} {🖤|🤍|☁️|} {날씨 선선해서|아침저녁 쌀쌀해서} {가디건 꺼냄|자켓 개시}",
        "{주말|토요일} {성수|한남|가로수길} {나들이|카페 투어} {☕️|🍂|}",
        "{가을|환절기} {코디|룩} 기록 {📸|} {#ootd 는 어렵다|매일 고민}",
        "{드디어|오늘} {패딩 조끼|경량 패딩} {개시|꺼냄}{ㅎㅎ|} 아침 {12도|10도} 실화?",
        "{몽클|몽클레어} {비니|볼캡} 하나로 {꾸안꾸|완성}{ㅎㅎ|} {#데일리룩|}",
        "{남친|남편|친구}랑 {커플룩|시밀러룩} {🤎|🖤|} {날씨 너무 좋다|가을 하늘}",
        "출근룩 {👔|} {블랙 앤 화이트|무채색} {최고|국룰}",
        "{작년에 산|3년째 입는} {몽클 패딩|몽클레어 마야} {올해도|아직도} {잘 입어요|현역}",
    ], kind={"user": 6, "micro": 2, "influencer": 1}, places=ANY_KR, sent="pos", viral=1.0,
      tags=["데일리룩", "오오티디", "ootd", "코디", "가을코디", "패션", "일상", "몽클레어", "moncler", "패션스타그램", "옷스타그램", "출근룩", "남자코디", "여자코디"],
      geo_p=0.25, titles=["오늘의 데일리룩 기록", "가을 코디 모음", "주말 나들이 착장", "몽클레어 패딩 3년 착용 후기"], kw=["몽클레어 코디", "몽클레어"], label="noise_ootd"),
    S("n_ootd_en", "en", 170, {"instagram": .55, "tiktok": .2, "threads": .1, "x": .15}, BASE, [
        "{fit check|Fit check|outfit of the day} {🖤|🤍|✨|} {fall is here|sweater weather|cozy season}",
        "{Sunday|Saturday} {coffee run|errands|brunch} fit {☕️|🍂|}",
        "{Black on black|All black everything|Monochrome} {again|as always} {lol|🖤|}",
        "{Weekend in|Back in|48h in} $city {✈️|} {outfit dump|photo dump}",
        "{finally|officially} {vest|gilet} season {🙌|} {layering is back|layers on layers}",
        "{this|my} moncler {is 6 years old|from 2019} and still {going strong|my favorite}",
        "{Airport|Travel day} outfit {✈️|}: {hoodie, joggers, puffer|comfy but cute}",
        "GRWM {for|:} {a cold morning|brunch with the girls|date night} {🫶|}",
        "{Ski trip|Mountain} {mood|vibes} {already|} {🏔️|} {can't wait for winter|counting the days}",
        "{New|Got a new} {beanie|cap} {lol|} {small treat|little treat for me}",
    ], kind={"user": 6, "micro": 3, "influencer": 1}, places=ANY_EN, sent="pos", viral=1.0, tags=TAG_OOTD + ["fyp", "grwm", "fitcheck"],
      geo_p=0.2, label="noise_ootd"),
    S("n_ootd_it", "it", 90, {"instagram": .7, "threads": .15, "x": .15}, BASE, [
        "{Domenica|Sabato} a $city {☀️|🍂|} {passeggiata in centro|giro in centro}",
        "{Outfit del giorno|Look di oggi} {🖤|}: {jeans, mocassini e gilet|total black e occhiali}",
        "{Primo|Finalmente il primo} {fresco|freschino} {della stagione|} {🍂|}, {fuori il gilet|via con la giacca}",
        "{Aperitivo|Apericena} {in Brera|sui Navigli|a Trastevere} {🥂|} {#ootd|}",
        "{Il mio|Questo} Moncler {ha 8 anni|è del 2018}: {non lo cambio|ancora perfetto}",
        "{Weekend|Fine settimana} in montagna {⛰️|}, {aria frizzante|già freschino la sera}",
    ], kind={"user": 6, "micro": 2}, places=ANY_IT, sent="pos", viral=1.0, tags=TAG_OOTD + ["milano", "roma", "outfititaliano", "lookdelgiorno"],
      geo_p=0.3, label="noise_ootd"),
    S("n_ootd_fr", "fr", 60, {"instagram": .7, "threads": .15, "x": .15}, BASE, [
        "{Dimanche|Samedi} à Paris {☕️|🍂|}, {balade au Marais|café en terrasse}",
        "{Tenue du jour|Look du jour} : {jean, mocassins et doudoune sans manches|total look noir}",
        "{Premier|Le premier} {matin frais|vrai matin d'automne}, {pull et gilet|on ressort la maille}",
        "Ma {vieille|fidèle} Moncler {de 2017|a 7 ans} et {toujours au top|elle ne bouge pas}",
    ], kind={"user": 6, "micro": 2}, places={"PAR01": 3, "CAN01": 1, "GVA01": 1}, sent="pos", viral=1.0, tags=TAG_OOTD + ["paris", "lookdujour", "tenuedujour"],
      geo_p=0.3, label="noise_ootd"),
    S("n_ootd_de", "de", 55, {"instagram": .7, "threads": .15, "x": .15}, BASE, [
        "{Sonntagsspaziergang|Samstagsrunde} {🍂|☕️|} {Herbst kann kommen|Herbstlaune}",
        "{Outfit|Look} heute: {Jeans, Sneaker, Weste|alles in Schwarz} {🖤|}",
        "{Kaffee|Cappuccino} {am Viktualienmarkt|in Schwabing|in Prenzlauer Berg} {☕️|}",
        "Meine Moncler {ist 10 Jahre alt|hält seit 2016} und {sieht aus wie neu|ist unkaputtbar}",
    ], kind={"user": 6, "micro": 2}, places=ANY_DE, sent="pos", viral=1.0, tags=TAG_OOTD + ["münchen", "berlin", "herbst", "outfitinspo"],
      geo_p=0.3, label="noise_ootd"),
    S("n_ootd_ja", "ja", 80, {"instagram": .5, "x": .4, "threads": .1}, BASE, [
        "{今日のコーデ|本日のコーデ}{🖤|☁️|} {まだ暑いけど|朝晩は涼しくなってきた}",
        "{週末|休日}は{代官山|中目黒|清澄白河}{でカフェ巡り|をお散歩}{☕️|}",
        "{モンクレ|モンクレール}のキャップ{お気に入り|ヘビロテ中}",
        "{秋服|秋冬物}{そろそろ|やっと}出した{笑|}",
        "{10年前|昔}に買ったモンクレ、{まだ現役|今年も着る}",
    ], kind={"user": 6, "micro": 2}, places=ANY_JP, sent="pos", viral=1.0, tags=["今日のコーデ", "コーデ", "ootd", "大人カジュアル", "モンクレール", "秋コーデ", "fashion"],
      geo_p=0.2, label="noise_ootd"),
    S("n_ootd_zh", "zh-CN", 120, {"xhs": .8, "weibo": .2}, BASE, [
        "{今日穿搭|今日ootd|日常穿搭}{🖤|☁️|}｜{一周不重样|通勤也要好看}",
        "{秋天|初秋}{第一件|第一套}{外套|穿搭}，{温柔|慵懒}{风|系}{🍂|}",
        "{周末|假期}{去|在}{武康路|三里屯|太古里}{citywalk|逛街}{📸|}",
        "{男友|老公}{穿搭|日常}{分享|记录}：{简单|基础款}{也能很帅|最耐看}",
        "{几年前|五年前}买的{盟可睐|蒙口}{还在穿|依然能打}，{真的耐穿|质量没得说}",
        "{小个子|155}{秋冬|冬季}{显高|显瘦}穿搭{合集|分享}",
        "{一衣多穿|一件外套三种穿法}｜{黑色|米色}{基础款|外套}",
    ], kind={"user": 6, "influencer": 2, "micro": 2}, places=ANY_CN, sent="pos", viral=1.0,
      tags=["今日穿搭", "ootd", "穿搭分享", "秋冬穿搭", "通勤穿搭", "小个子穿搭", "盟可睐", "citywalk", "男友穿搭"],
      titles=["秋天第一套穿搭🍂", "一周通勤穿搭不重样", "小个子冬季显高穿搭", "男友日常穿搭分享", "盟可睐穿了5年的真实感受", "周末citywalk穿搭"], label="noise_ootd"),
    S("n_ootd_zht", "zh-HK", 25, {"instagram": .7, "threads": .3}, BASE, [
        "{今日著咩|今日OOTD}{🖤|} {香港仲係好熱|終於有少少涼}",
        "{週末|放假}{去|喺}{中環|銅鑼灣}{行街|飲嘢}{☕️|}",
    ], kind={"user": 1}, places={"HKG01": 1}, sent="pos", viral=1.0, tags=["hkig", "ootd", "hkfashion", "香港"], geo_p=0.2, label="noise_ootd"),
    S("n_ootd_tw", "zh-TW", 20, {"instagram": .6, "threads": .4}, BASE, [
        "{今天的穿搭|今日穿搭}{🖤|} {台北還是好熱|終於有點涼了}",
        "{週末|假日}{在|去}{信義區|東區}{逛街|喝咖啡}{☕️|}",
    ], kind={"user": 1}, places={"TPE01": 1}, sent="pos", viral=1.0, tags=["穿搭", "ootd", "台北"], geo_p=0.2, label="noise_ootd"),
    S("n_ootd_es", "es", 30, {"instagram": .7, "x": .3}, BASE, [
        "{Domingo|Sábado} por {el Retiro|Malasaña|Salamanca} {☀️|🍂|}",
        "{Look|Outfit} de hoy: {vaqueros, mocasines y chaleco|todo negro} {🖤|}",
    ], kind={"user": 1}, places={"MAD01": 1}, sent="pos", viral=1.0, tags=TAG_OOTD + ["madrid", "lookdeldia"], geo_p=0.3, label="noise_ootd"),
    S("n_ootd_nl", "nl", 20, {"instagram": .8, "x": .2}, BASE, [
        "{Zondag|Zaterdag} {in de Jordaan|op de grachten} {🍂|☕️|}",
        "{Outfit|Look} van vandaag: {jeans, sneakers en bodywarmer|alles zwart}",
    ], kind={"user": 1}, places={"AMS01": 1}, sent="pos", viral=1.0, tags=TAG_OOTD + ["amsterdam"], geo_p=0.3, label="noise_ootd"),
    S("n_ootd_da", "da", 18, {"instagram": .8, "x": .2}, BASE, [
        "{Søndag|Lørdag} i {Kødbyen|Nyhavn|Frederiksberg} {🍂|☕️|}",
        "{Dagens outfit|Dagens look}: {jeans, sneakers og vest|sort i sort}",
    ], kind={"user": 1}, places={"CPH01": 1}, sent="pos", viral=1.0, tags=TAG_OOTD + ["københavn", "dagensoutfit"], geo_p=0.3, label="noise_ootd"),

    # ===================================================================== MAYA classic reviews
    S("n_maya_en", "en", 50, {"reddit": .5, "instagram": .3, "x": .2}, BASE, [
        "{6|8|10} years with my Maya and it still looks {new|great}. {Best purchase I've made|Worth every penny}",
        "Maya vs Montcla — {went with Maya|chose the Maya}, {the shine|the laqué finish} {just looks better|is iconic}",
        "{Black|Navy} Maya {size 3|size 4} fit pic, {5'10 165lbs|180cm 75kg}, {true to size|fits TTS} {imo|for me}",
        "Is the Maya {still worth it|worth it} {in 2026|at this price}? {Mine is from 2019 and|Honestly} {yes|still my warmest jacket}",
    ], kind={"user": 1}, places=ANY_EN, sent="pos", viral=1.0, tags=["moncler", "maya", "monclermaya"],
      titles=["Moncler Maya 6 years later", "Maya vs Montcla?", "Maya sizing - fit pic", "Is the Moncler Maya still worth it?", "My Maya after 8 winters"],
      subs=["malefashionadvice", "monclerheads", "BuyItForLife"], label="noise_maya_review"),
    S("n_maya_it", "it", 25, {"instagram": .7, "x": .3}, BASE, [
        "Il Maya {nero|blu} {resta il migliore|non tradisce mai}. {10 inverni|8 anni} e {zero problemi|come nuovo}",
        "{Ho riportato fuori|Rimesso} il Maya {per la prima sera fredda|stasera}, {sempre lui|un classico}",
    ], kind={"user": 1}, places=ANY_IT, sent="pos", viral=1.0, tags=["moncler", "maya", "piumino"], label="noise_maya_review"),
    S("n_maya_ja", "ja", 22, {"x": .6, "instagram": .4}, BASE, [
        "マヤ{5年目|7年目}、{まだまだ現役|全然へたらない}。{結局これが一番|定番最強}",
        "{マヤ|MAYA}のサイズ{1|2}、{170cm|175cm}でジャスト",
    ], kind={"user": 1}, places=ANY_JP, sent="pos", viral=1.0, tags=["モンクレール", "マヤ", "MAYA"], label="noise_maya_review"),
    S("n_maya_ko", "ko", 22, {"instagram": .5, "naver_blog": .5}, BASE, [
        "몽클레어 마야 {5년|7년} 착용 후기. {아직도 새 거 같아요|여전히 따뜻함}",
        "마야 {블랙|네이비} {3사이즈|2사이즈} {175/70|180/75} {정사이즈 추천|딱 맞아요}",
    ], kind={"user": 1}, places=ANY_KR, sent="pos", viral=1.0, tags=["몽클레어", "마야", "남자패딩"], titles=["몽클레어 마야 5년 착용 후기", "몽클레르 마야 사이즈 후기"],
      kw=["몽클레어 마야"], label="noise_maya_review"),
    S("n_maya_de", "de", 14, {"instagram": .6, "x": .4}, BASE, ["Meine Maya {seit 2017|seit acht Jahren}, {noch immer top|kein einziges Problem}"],
      kind={"user": 1}, places=ANY_DE, sent="pos", viral=1.0, tags=["moncler"], label="noise_maya_review"),
    S("n_maya_zh", "zh-CN", 20, {"xhs": 1.0}, BASE, [
        "{盟可睐|蒙口}MAYA{真实测评|穿了五年}：{保暖|质量}{没得说|一流}，{就是贵|价格劝退}",
        "MAYA {2码|3码} {175|180}{穿着刚好|正好}，{附上身图|看图}",
    ], kind={"user": 1}, places=ANY_CN, sent="pos", viral=1.0, tags=["盟可睐", "MAYA", "男士羽绒服"], titles=["MAYA 五年真实测评", "盟可睐MAYA尺码参考"], label="noise_maya_review"),

    # ===================================================================== ski / Grenoble / mountains
    S("n_ski_it", "it", 28, {"instagram": .8, "x": .2}, SKI, [
        "{-45|-40|-30} giorni all'apertura {degli impianti|della stagione} {⛷️|🏔️}",
        "Prima neve sulle {Dolomiti|cime} {❄️|}! {Ci siamo quasi|Il countdown è iniziato}",
        "{Sci|Scarponi} {pronti|preparati}, manca solo la neve {⛷️|}",
    ], kind={"user": 1}, places={"CRT01": 2, "COU01": 1, "MIL01": 1}, sent="pos", viral=1.0, tags=["sci", "dolomiti", "skiseason", "montagna", "grenoble"], geo_p=0.3, label="noise_ski"),
    S("n_ski_fr", "fr", 22, {"instagram": .8, "x": .2}, SKI, [
        "{J-45|J-40|J-30} avant l'ouverture {des pistes|de la station} {⛷️|🏔️}",
        "{Les skis sont farté|Skis prêts}, {plus qu'à attendre la neige|vivement décembre}",
    ], kind={"user": 1}, places={"GVA01": 1, "MONESTIER": 1}, sent="pos", viral=1.0, tags=["ski", "montagne", "hiver"], label="noise_ski"),
    S("n_ski_de", "de", 28, {"instagram": .8, "x": .2}, SKI, [
        "Noch {40|35|30} Tage bis {zum Saisonstart|die Lifte laufen} {⛷️|🏔️}",
        "{Skischuhe|Ski} {aus dem Keller geholt|gewachst}, {kann losgehen|Vorfreude}",
        "Engadin {im Herbstlicht|im Oktober} {😍|🏔️}, {Lärchen gold|Ruhe pur}",
    ], kind={"user": 1}, places={"STM01": 2, "ZRH01": 1, "MUN01": 1}, sent="pos", viral=1.0, tags=["ski", "skiing", "engadin", "alpen", "winteriscoming"], geo_p=0.3, label="noise_ski"),
    S("n_ski_en", "en", 22, {"instagram": .7, "tiktok": .3}, SKI, [
        "{45|40|30} days till {Aspen|the lifts} open {⛷️|🏔️} {not that I'm counting|counting down}",
        "{Ski|Snow} season {countdown|prep}: {new goggles|boots fitted} {✔️|}",
    ], kind={"user": 1}, places={"ASP01": 2, "US_HOME": 1, "UK_HOME": 1}, sent="pos", viral=1.0, tags=["ski", "skiseason", "aspen", "snow"], label="noise_ski"),

    # ===================================================================== kids
    S("n_kids_it", "it", 20, {"instagram": 1.0}, BASE, [
        "Il {piccolo|mio piccolo|bimbo} {col suo primo piumino|pronto per l'inverno} {🥹|💙}",
        "{Piumino bimba|Piumino bambino}: {taglia 4 anni|taglia 6 anni} {quanto vestono?|vestono grandi?}",
    ], kind={"user": 1}, places=ANY_IT, sent="pos", viral=1.0, tags=["bambini", "mamma", "moncler"], label="noise_kids"),
    S("n_kids_en", "en", 20, {"instagram": .6, "reddit": .4}, BASE, [
        "{Tiny|Little} human in his first puffer {🥹|💙}",
        "Kids Moncler sizing — {do they run big?|how much room to grow?} {Looking at 6Y for my 5yo|Thinking 8Y}",
    ], kind={"user": 1}, places=ANY_EN, sent="pos", viral=1.0, tags=["toddlerstyle", "kidsfashion", "moncler"],
      titles=["Moncler kids sizing question"], subs=["BabyBumps", "Parenting"], label="noise_kids"),
    S("n_kids_ko", "ko", 20, {"instagram": .6, "naver_blog": .4}, BASE, [
        "{우리 딸|우리 아들|조카} 첫 {몽클|패딩} {🥹|💗} {너무 귀여워요|선물 받았어요}",
        "몽클레어 키즈 {사이즈 추천|사이즈 문의}: {6살|8살}{은 몇 사이즈?|이면 8A?}",
    ], kind={"user": 1}, places=ANY_KR, sent="pos", viral=1.0, tags=["몽클레어키즈", "아기패딩", "육아"], titles=["몽클레어 키즈 패딩 사이즈 후기", "조카 선물 몽클 키즈"], kw=["몽클레어 키즈"], label="noise_kids"),
    S("n_kids_zh", "zh-CN", 18, {"xhs": 1.0}, BASE, [
        "{宝宝|儿子|女儿}{第一件|今年的}羽绒服｜{盟可睐|Moncler}童装{尺码分享|上身}",
        "{盟可睐|Moncler}童装{偏大还是偏小|尺码怎么选}？{4岁|6岁}{选几码|穿几码}",
    ], kind={"user": 1}, places=ANY_CN, sent="pos", viral=1.0, tags=["童装", "宝宝穿搭", "盟可睐童装"], titles=["盟可睐童装尺码", "宝宝羽绒服分享"], label="noise_kids"),
    S("n_kids_fr", "fr", 12, {"instagram": 1.0}, BASE, ["{Mon petit|Ma puce} {prêt pour l'hiver|avec sa première doudoune} {🥹|}"],
      kind={"user": 1}, places={"PAR01": 1}, sent="pos", viral=1.0, tags=["maman", "enfant"], label="noise_kids"),

    # ===================================================================== Monestier-de-Clermont ("Moncler")
    S("n_town", "fr", 16, {"instagram": .7, "x": .3}, BASE_FLAT, [
        "{Rando|Randonnée} {au départ de|autour de} Monestier-de-Clermont {🥾|}, {vue sur le Vercors|le Mont Aiguille au fond}",
        "{Fête du village|Marché} à Monestier-de-Clermont {ce week-end|dimanche} {☀️|}",
        "{Arrêt|Pause café} à Monestier-de-Clermont {sur la route de|en descendant vers} {Sisteron|la Provence}",
        "Petit rappel : Moncler vient de Monestier-de-Clermont {😉|}, {le village est toujours aussi joli|on est passés devant}",
    ], kind={"user": 1}, places={"MONESTIER": 1}, sent="pos", viral=0.8, tags=["monestierdeclermont", "vercors", "trieves", "isere", "rando", "moncler"], geo_p=0.6,
      label="noise_town"),

    # ===================================================================== memes / humour
    S("n_meme_en", "en", 50, {"x": .5, "tiktok": .3, "reddit": .2}, BASE, [
        "my moncler jacket costs more than my rent and {i'm fine|i'm thriving} {💀|}",
        "{me|Me} in my {$1,800|1800 dollar} puffer {waiting for the bus|at the bus stop} {lmao|}",
        "{puffer season|Puffer szn} {is upon us|starts now} and {my wallet is scared|i'm ready}",
        "{when the|POV: the} moncler sales associate {asks if I need help|looks at my shoes} {😭|}",
        "{rich people|Old money} {starter pack|uniform}: moncler vest, quarter zip, {loafers|boat shoes}",
        "{no thoughts|brain empty} just {puffer|down jacket} {🧥|}",
    ], kind={"user": 1}, places=ANY_EN, sent="neu", viral=1.2, tags=["meme", "fyp", "funny", "moncler"],
      titles=["The Moncler vest finance bro uniform", "Who actually pays full price for Moncler?"], subs=["memes", "malefashionadvice", "FinanceMemes"], label="noise_meme"),
    S("n_meme_es", "es", 14, {"x": .6, "tiktok": .4}, BASE, ["{yo|Yo} con mi plumas de {Moncler|marca} {en el metro|esperando el bus} {💀|😂}",
                                                             "el chaleco de moncler es el uniforme {oficial|} de {los de finanzas|Salamanca} {😂|}"],
      kind={"user": 1}, places={"MAD01": 1}, sent="neu", viral=1.0, tags=["humor"], label="noise_meme"),
    S("n_meme_it", "it", 14, {"x": .7, "instagram": .3}, BASE, ["{Milanese|Il milanese} {imbruttito|medio} a ottobre: {gilet|smanicato} Moncler e {via|vai} {😂|}",
                                                                "{Lo smanicato|Il gilet} Moncler {è un'identità|non è un capo, è un'appartenenza}"],
      kind={"user": 1}, places=ANY_IT, sent="neu", viral=1.0, tags=["milanoimbruttito", "humor"], label="noise_meme"),
    S("n_meme_ko", "ko", 10, {"x": .7, "threads": .3}, BASE, ["{몽클|패딩} 하나 {살까|사면} {한 달 라면|두 달 편의점 도시락}{ㅋㅋㅋ|}",
                                                             "{겨울 되면|겨울엔} 강남역 {몽클|검은 패딩} {반, 나머지 반|국룰}{ㅋㅋ|}"],
      kind={"user": 1}, places=ANY_KR, sent="neu", viral=1.0, tags=[], label="noise_meme"),

    # ===================================================================== giveaway scams
    S("n_scam_giveaway", "en", 40, {"instagram": .8, "threads": .2}, bursts(["2026-08-12", "2026-09-05", "2026-09-19", "2026-10-02", "2026-10-03", "2026-10-09", "2026-10-17"], 6), [
        "🎁 GIVEAWAY 🎁 We're giving away {5|10|3} Moncler {Maya|Maire|ILVARO} jackets! 1. Follow us 2. Like this post 3. Tag 3 friends 4. DM us your {address|details} {🔥|}",
        "🎉 {CONGRATS|Congratulations} @$rhandle you WON a Moncler jacket! {DM us to claim|Click the link in bio to claim} {within 24h|before it expires} 🎉",
        "{FREE|Win a FREE} Moncler {puffer|jacket} 🤑 {just pay shipping|only shipping fee $9.99} 👉 link in bio",
        "OFFICIAL MONCLER GIVEAWAY {2026|🎁} {celebrating 1M followers|for our loyal fans}: {share|repost} to {win|enter}! {Winners announced Friday|Ends Sunday}",
    ], kind={"scam": 1}, places={"US_HOME": 1}, sent="pos", viral=0.4, tags=["giveaway", "moncler", "free", "win", "contest", "giveawayalert"], flags=("scam",), dup_ok=True,
      label="noise_scam"),
    S("n_scam_giveaway_ko", "ko", 10, {"instagram": 1.0}, bursts(["2026-09-08", "2026-10-03", "2026-10-04"], 5), [
        "🎁 이벤트 🎁 몽클레어 {일바로 핑크|패딩} {3명|5명} 추첨 증정! 팔로우+좋아요+친구 3명 태그 {후 DM|하고 DM 주세요}",
        "당첨 축하드립니다🎉 @$rhandle 님 몽클레어 {패딩|일바로} 당첨! 프로필 링크에서 {배송비 결제|본인인증} 후 수령",
    ], kind={"scam": 1}, places={"KR_HOME": 1}, sent="pos", viral=0.4, tags=["이벤트", "경품", "몽클레어", "무료나눔"], flags=("scam",), dup_ok=True, label="noise_scam"),
    S("n_scam_es_it", "es", 8, {"instagram": 1.0}, bursts(["2026-09-12", "2026-10-10"], 4), [
        "🎁 SORTEO 🎁 {Regalamos|Sorteamos} una chaqueta Moncler! Sigue, da like y etiqueta a 3 amigos {🔥|}",
    ], kind={"scam": 1}, places={"MAD01": 1}, sent="pos", viral=0.4, tags=["sorteo", "moncler", "gratis"], flags=("scam",), dup_ok=True, label="noise_scam"),

    # ===================================================================== crypto / unrelated spam
    S("n_crypto", "en", 30, {"x": .8, "threads": .2}, bursts(["2026-08-15", "2026-09-01", "2026-09-22", "2026-10-02", "2026-10-13", "2026-10-20"], 8), [
        "$PUFF token {🚀🚀|🚀} {100x|1000x} incoming, {don't miss|last chance} {#moncler #fashion #crypto|#crypto #altcoin #moncler}",
        "{Make $5k/week|Earn $3000 daily} from home {💸|} {DM me|link in bio} {#moncler #luxury #money|#luxurylifestyle #moncler #passiveincome}",
        "{🔥|} {Airdrop|Free airdrop} live {now|} {claim|connect wallet} 👉 {bit.ly/|t.co/}$rstr {#moncler #nft|#nft #moncler #kpop}",
        "{Bought|Buying} {my|a} moncler with {crypto|my $PUFF gains} {😎|} {#wagmi #moncler|#moncler #crypto}",
    ], kind={"bot": 1}, places={"US_HOME": 1}, sent="pos", viral=0.3, tags=[], flags=("spam",), dup_ok=True, label="noise_spam"),

    # ===================================================================== replica / counterfeit sellers
    S("n_replica_en", "en", 50, {"instagram": .6, "x": .3, "threads": .1}, [("2026-08-01", 3), ("2026-09-20", 4), ("2026-10-02", 4), ("2026-10-03", 10), ("2026-10-10", 8), ("2026-10-22T06:00", 6)], [
        "Moncler 1:1 {quality|top quality} {available|in stock} 📩 DM {for prices|now} {worldwide shipping|ship worldwide} ✈️",
        "{NEW|🔥 NEW} pink ILVARO {1:1|best version} {in stock|ready to ship} {all sizes|00-3} {DM|WhatsApp} 📲",
        "{Best|Top} quality Moncler {Maya|Maire|Ilvaro} {same as retail|indistinguishable} 💯 {real down|90% goose down} {DM to order|link in bio}",
        "{Haeun|idol} pink jacket {available|in stock} 🩷 {cheap price|only $289} {DM|whatsapp +852 5$rnum}",
    ], kind={"scam": 1}, places={"US_HOME": 1, "HKG01": 1}, sent="pos", viral=0.4, tags=["moncler", "monclerjacket", "replica", "1to1", "reps", "ilvaro", "fashion"],
      flags=("replica",), dup_ok=True, label="noise_replica"),
    S("n_replica_zh", "zh-CN", 50, {"weibo": .5, "xhs": .5}, [("2026-08-01", 3), ("2026-09-20", 4), ("2026-10-02", 4), ("2026-10-03", 10), ("2026-10-10", 8), ("2026-10-22T06:00", 6)], [
        "{夏恩同款|尹夏恩同款}粉色ILVARO {顶级版本|原单品质|1:1}{现货|到货}，{全码|0-3码}{，v:|，vx:}$rwx",
        "{盟可睐|蒙口}{原单|专柜品质}羽绒服{清仓|特价}{🔥|}{私信|看主页}{，支持验货|，包邮}",
        "{工厂直出|源头工厂}{盟可睐|蒙口}{MAYA|MAIRE|ILVARO}，{90白鹅绒|鹅绒}，{专柜同步|对版}，{私|滴滴}",
    ], kind={"scam": 1}, places={"CN_HOME": 1}, sent="pos", viral=0.4, tags=["夏恩同款", "羽绒服", "盟可睐"], flags=("replica",), dup_ok=True,
      titles=["夏恩同款到货啦", "盟可睐同款 平价版", "专柜品质羽绒服"], label="noise_replica"),
    S("n_replica_ko", "ko", 20, {"instagram": .7, "x": .3}, [("2026-08-01", 2), ("2026-10-03", 10), ("2026-10-22T06:00", 5)], [
        "미러급 몽클 {일바로 핑크|마야|마이어} 입고 {✨|} {카톡 문의|프로필 링크} {정품과 동일|퀄리티 보장}",
        "{하은 패딩|핑크 숏패딩} {당일 발송|빠른 배송} {가능|} {문의는 DM|카톡 ID 프로필 참고}",
    ], kind={"scam": 1}, places={"KR_HOME": 1}, sent="pos", viral=0.4, tags=["몽클레어", "하은패딩", "미러급"], flags=("replica",), dup_ok=True, label="noise_replica"),

    # ===================================================================== bot network (outlet)
    S("n_bot_en", "en", 60, {"instagram": .5, "x": .4, "threads": .1}, bursts(BOT_DAYS, 2), [
        "🔥 MONCLER OUTLET {-70%|-80%|UP TO 80% OFF} 🔥 Shop now 👉 link in bio {#moncler #monclerjacket #sale|#moncler #sale #outlet}",
        "🔥MONCLER OUTLET {-70%|-80%}🔥 {Shop now|Order now} 👉 {monc-outlet-sale.shop|moncler-outletstore.top} {#moncler #sale|}",
        "{🔥|⚡} Moncler {jackets|down jackets} {80% OFF|-75%} {today only|limited time} 👉 {link in bio|monc-outlet-sale.shop} {#moncler|}",
    ], kind={"bot": 1}, places={"US_HOME": 1}, sent="pos", viral=0.25, tags=[], flags=("bot",), dup_ok=True, label="noise_bot"),
    S("n_bot_es", "es", 20, {"instagram": .6, "x": .4}, bursts(BOT_DAYS, 2), [
        "🔥 MONCLER OUTLET {-70%|-80%} 🔥 Compra ahora 👉 link en bio {#moncler #rebajas|#moncler #oferta}",
    ], kind={"bot": 1}, places={"MAD01": 1}, sent="pos", viral=0.25, tags=[], flags=("bot",), dup_ok=True, label="noise_bot"),
    S("n_bot_it", "it", 20, {"instagram": .6, "x": .4}, bursts(BOT_DAYS, 2), [
        "🔥 MONCLER OUTLET {-70%|-80%} 🔥 Acquista ora 👉 link in bio {#moncler #saldi|#moncler #offerta}",
    ], kind={"bot": 1}, places={"MIL01": 1}, sent="pos", viral=0.25, tags=[], flags=("bot",), dup_ok=True, label="noise_bot"),
    S("n_bot_de", "de", 20, {"instagram": .6, "x": .4}, bursts(BOT_DAYS, 2), [
        "🔥 MONCLER OUTLET {-70%|-80%} 🔥 Jetzt shoppen 👉 Link in Bio {#moncler #sale|#moncler #angebot}",
    ], kind={"bot": 1}, places={"BER01": 1}, sent="pos", viral=0.25, tags=[], flags=("bot",), dup_ok=True, label="noise_bot"),

    # ===================================================================== customer-service complaints (unrelated to scenario)
    S("n_cs_en", "en", 40, {"x": .5, "reddit": .3, "instagram": .2}, BASE, [
        "{@moncler|Moncler} my online order {has been 'processing' for 9 days|still hasn't shipped after 2 weeks}. {Any update?|No reply to 3 emails.}",
        "Refund for my {return|online return} {still not processed|taking 4 weeks}, {customer service useless|chat just loops}",
        "{Ordered|Bought} a beanie online, {received the wrong colour|got navy instead of black}. {Great.|Now I have to return it.}",
        "{Tried|Trying} to book {a repair|an appointment} for my {10 year old|old} jacket, {6 week wait|no slots until December}",
        "{Website|The app} {keeps crashing|logs me out} at checkout {🙃|}",
    ], kind={"user": 1}, places=ANY_EN, sent="neg", viral=0.8, tags=[], titles=["Moncler online order stuck in processing", "Moncler repair wait times?", "Wrong item from Moncler online"],
      subs=["monclerheads", "CustomerService"], label="noise_cs"),
    S("n_cs_it", "it", 20, {"x": .6, "instagram": .4}, BASE, [
        "{Ordine online|Ordine sul sito} {fermo da 10 giorni|mai arrivato}, {il servizio clienti non risponde|nessuna risposta}",
        "{Rimborso|Il reso} {ancora non arrivato|dopo un mese}. {Delusa|Che pazienza}",
    ], kind={"user": 1}, places=ANY_IT, sent="neg", viral=0.8, tags=[], label="noise_cs"),
    S("n_cs_fr", "fr", 15, {"x": .7, "instagram": .3}, BASE, ["{Commande en ligne|Ma commande} {bloquée depuis 10 jours|toujours pas expédiée}, {service client injoignable|aucune réponse}"],
      kind={"user": 1}, places={"PAR01": 1}, sent="neg", viral=0.8, tags=[], label="noise_cs"),
    S("n_cs_de", "de", 15, {"x": .7, "instagram": .3}, BASE, ["{Online-Bestellung|Meine Bestellung} {seit 10 Tagen in Bearbeitung|noch nicht verschickt}. {Kundenservice?|Keine Antwort.}"],
      kind={"user": 1}, places=ANY_DE, sent="neg", viral=0.8, tags=[], label="noise_cs"),
    S("n_cs_zh", "zh-CN", 18, {"weibo": .7, "xhs": .3}, BASE, [
        "{盟可睐|Moncler}{官网|小程序}{下单|买的}{十天了还没发货|物流一直不动}，{客服|在线客服}{回复太慢|一直排队}",
        "{退货|退款}{一个月了|拖了很久}{还没到账|没消息}，{@盟可睐Moncler|求助}",
    ], kind={"user": 1}, places=ANY_CN, sent="neg", viral=0.8, tags=["盟可睐"], titles=["官网下单不发货", "退款一个月没到账"], label="noise_cs"),
    S("n_cs_ko", "ko", 14, {"naver_cafe": .5, "x": .5}, BASE, [
        "몽클레어 {공홈|공식 온라인} 주문 {열흘째|2주째} 배송 준비중.. {고객센터 연결도 안 돼요|문의 답변 없음}",
    ], kind={"user": 1}, places=ANY_KR, sent="neg", viral=0.8, tags=[], titles=["몽클레어 공홈 배송 너무 느려요"], cafes="fashion", kw=["몽클레어 공홈 배송"], label="noise_cs"),
    S("n_cs_ja", "ja", 10, {"x": 1.0}, BASE, ["モンクレの{オンライン|公式通販}、{注文から10日|2週間}経っても{発送されない|音沙汰なし}"],
      kind={"user": 1}, places=ANY_JP, sent="neg", viral=0.8, tags=[], label="noise_cs"),

    # ===================================================================== LUMIERE fan chatter (no product)
    S("n_fan_ko", "ko", 70, {"x": .7, "instagram": .2, "threads": .1}, FAN, [
        "{하은이|우리 하은} {오늘|어제} {머리|헤어} {미쳤다|너무 예쁘다} {😭|🥹|💗}",
        "루미에르 {컴백|신곡} {언제|언제 해요}{ㅠㅠ|!!}",
        "{하은|LUMIERE} {콘서트|팬미팅|음방} {영상|직캠} {보고|보는데} {울었다|심장 떨어짐}",
        "{오늘 음방|라이브} {하은 파트|하은이 고음} {미쳤음|레전드}",
        "{공항|출국길} {하은이|루미에르} {손 흔들어줌|팬들한테 인사함} {ㅠㅠ|🥹}",
        "{하은|루미에르} {버블|위버스} {왔다|떴다}!! {귀여워|너무 다정해}",
    ], kind={"fan": 6, "user": 4}, places={"KR_HOME": 1}, sent="pos", viral=1.5, tags=["윤하은", "LUMIERE", "루미에르", "HAEUN", "하은"], label="noise_fan"),
    S("n_fan_en", "en", 55, {"x": .7, "tiktok": .2, "instagram": .1}, FAN, [
        "haeun's {hair|smile|laugh} {today|in this fancam} {😭|🥹} {I'm not ok|protect her}",
        "LUMIERE {comeback|new album} {when|when pls} {😩|}",
        "{the way|how} haeun {waved at fans|said thank you in 5 languages} {💗|😭}",
        "{haeun|lumiere} {fancam|airport video} {is everything|on repeat}",
        "{new|} LUMIERE {teaser|photo} {just dropped|is out}!! {🚨|}",
    ], kind={"fan": 6, "user": 4}, places={"US_HOME": 2, "UK_HOME": 1, "SIN01": 1}, sent="pos", viral=1.4, tags=["LUMIERE", "Haeun", "kpop", "YoonHaeun"],
      label="noise_fan"),
    S("n_fan_ja", "ja", 30, {"x": 1.0}, FAN, ["ハウンちゃん{今日も|音楽番組でも}{かわいい|天使}{🥹|💗}", "LUMIERE{カムバ|新曲}{まだ？|楽しみ}", "ハウンの{日本語|笑顔}{かわいすぎ|反則}"],
      kind={"fan": 1, "user": 1}, places={"JP_HOME": 1}, sent="pos", viral=1.2, tags=["LUMIERE", "ハウン"], label="noise_fan"),
    S("n_fan_zh", "zh-CN", 40, {"weibo": 1.0}, FAN, [
        "{尹夏恩|夏恩}{今天|打歌舞台}{的发型|的笑容}{也太好看了|绝了}{😭|}",
        "LUMIERE{回归|新专辑}{什么时候|定档了吗}{！|？}",
        "{夏恩|尹夏恩}{机场|出发}{饭拍|直拍}{来了|好可爱}",
    ], kind={"fan": 2, "user": 2}, places={"CN_HOME": 1}, sent="pos", viral=1.3, tags=["尹夏恩", "LUMIERE"], label="noise_fan"),

    # LUMIERE world tour announced Oct 6 (Seoul KSPO Dome Nov 14-15, Tokyo Dome Nov 28-29)
    S("n_fan_tour", "ko", 22, {"x": .7, "instagram": .2, "threads": .1}, [("2026-10-06T09:00", 0), ("2026-10-06T11:00", 10), ("2026-10-08", 4), ("2026-10-22T06:00", 1)], [
        "루미에르 월드투어 {떴다|확정}!! 서울 KSPO돔 11/14-15 {ㅠㅠ|🥹|!!} {티켓팅 어떡해|광클 준비}",
        "{KSPO돔|체조경기장} {이틀|11월 14일 15일} {실화냐|미쳤다} {하은이 보러 간다|무조건 간다}",
    ], kind={"fan": 2, "user": 2}, places={"KR_HOME": 1}, sent="pos", viral=1.4, tags=["LUMIERE", "루미에르", "월드투어"], label="noise_fan"),
    S("n_fan_tour_ja", "ja", 14, {"x": 1.0}, [("2026-10-06T09:00", 0), ("2026-10-06T12:00", 10), ("2026-10-09", 3), ("2026-10-22T06:00", 1)], [
        "LUMIERE東京ドーム{決定|きた}{！！|😭} 11/28・29 {絶対行く|有給取る}",
        "{東京ドーム|ドーム公演}{2days|二日間}{とか|って}{夢みたい|泣く}…ハウンちゃんに会える",
    ], kind={"fan": 1, "user": 1}, places={"JP_HOME": 1}, sent="pos", viral=1.2, tags=["LUMIERE", "東京ドーム"], label="noise_fan"),
    S("n_fan_tour_en", "en", 12, {"x": 1.0}, [("2026-10-06T09:00", 0), ("2026-10-06T12:00", 10), ("2026-10-09", 3), ("2026-10-22T06:00", 1)], [
        "LUMIERE WORLD TOUR {IS REAL|ANNOUNCED} {😭|🚨} Seoul KSPO Dome Nov 14-15, Tokyo Dome Nov 28-29 {and more TBA|more dates soon}",
    ], kind={"fan": 1, "user": 1}, places={"US_HOME": 1}, sent="pos", viral=1.3, tags=["LUMIERE", "LUMIEREworldtour"], label="noise_fan"),
    # ===================================================================== investors
    S("n_invest_en", "en", 25, {"x": .6, "reddit": .4}, INVEST, [
        "$MONC {Q3|third quarter} revenue {next week|on the 22nd}. {Asia is the swing factor|Watching Korea/China closely}",
        "Luxury stocks {sold off again|down 3%} today, Moncler {held up better|outperformed}. {Asia demand?|K-pop effect?}",
        "Moncler {trading|at} {28x|25x} earnings, {not cheap|still reasonable} {for the quality|given the brand}",
        "{Sell-side|Analysts} {expect|guiding} {mid-single digit|+5-7%} growth for Moncler {Q3|this quarter}",
    ], kind={"user": 3, "media": 1}, places={"UK_HOME": 1, "US_HOME": 1}, sent="neu", viral=0.8, tags=["luxury", "stocks"],
      titles=["Moncler Q3 preview", "Luxury sector sell-off - Moncler holding up?"], subs=["stocks", "EuropeFIRE", "investing"], label="noise_investor"),
    S("n_invest_it", "it", 15, {"x": 1.0}, INVEST, [
        "Moncler {in rialzo|in calo} {a Piazza Affari|oggi}, {lusso sotto pressione|attesa per i ricavi del terzo trimestre}",
    ], kind={"user": 2, "media": 1}, places={"MIL01": 1}, sent="neu", viral=0.8, tags=["borsa", "piazzaaffari"], label="noise_investor"),

    # ===================================================================== other celebs / athletes
    S("n_celeb_en", "en", 20, {"instagram": .5, "x": .5}, BASE, [
        "{that|the} {striker|quarterback|F1 driver} {arriving at training|at the airport} in a {Moncler vest|black Maya} {is so on brand|lol}",
        "{Every|Every single} {footballer|NBA player} {in October|this week}: {Moncler|puffer} + {tracksuit|sliders}",
    ], kind={"user": 1, "media": 1}, places=ANY_EN, sent="neu", viral=1.0, tags=["airportstyle", "moncler"], label="noise_celeb"),
    S("n_celeb_it", "it", 18, {"instagram": .5, "x": .5}, BASE, ["{Il capitano|Mezza squadra} {all'arrivo a Linate|in aeroporto} col {piumino|gilet} Moncler"],
      kind={"user": 1, "media": 1}, places={"MIL01": 1}, sent="neu", viral=1.0, tags=["calcio"], label="noise_celeb"),
    S("n_celeb_ko", "ko", 14, {"x": .6, "instagram": .4}, BASE, ["{배우|가수} {공항패션|출국길} {몽클 패딩|블랙 패딩} {정보|어디 거?}"],
      kind={"user": 1, "media": 1}, places={"KR_HOME": 1}, sent="neu", viral=1.0, tags=["공항패션"], label="noise_celeb"),
    S("n_celeb_zh", "zh-CN", 14, {"weibo": 1.0}, BASE, ["{某顶流|男明星}{机场|街拍}{同款|穿搭}{羽绒服|外套}{扒到了|链接}"],
      kind={"user": 1, "media": 1}, places={"CN_HOME": 1}, sent="neu", viral=1.0, tags=["明星同款", "机场穿搭"], label="noise_celeb"),

    # ===================================================================== jobs
    S("n_jobs", "en", 8, {"x": 1.0}, BASE_FLAT, ["{We're hiring|Hiring}: {Client Advisor|Sales Associate} – {luxury outerwear|luxury fashion} – {London|NYC|Dubai}. {Apply via link|DM for details}"],
      kind={"user": 1}, places=ANY_EN, sent="neu", viral=0.5, tags=["hiring", "luxuryjobs", "retailjobs"], label="noise_jobs"),
    S("n_jobs_it", "it", 8, {"x": 1.0}, BASE_FLAT, ["{Cerchiamo|Ricerchiamo} {Sales Assistant|addetto vendite} {settore lusso|abbigliamento luxury} {Milano|Roma}, {inviare CV|candidature in DM}"],
      kind={"user": 1}, places=ANY_IT, sent="neu", viral=0.5, tags=["lavoro", "offertadilavoro"], label="noise_jobs"),

    # ===================================================================== second-hand
    S("n_2h_it", "it", 18, {"instagram": .6, "x": .4}, BASE, ["{Vendo|Vendesi} Moncler {Maya|gilet|piumino} {taglia 2|taglia 3} {usato pochissimo|come nuovo}, {prezzo in DM|su Vinted}"],
      kind={"user": 1}, places=ANY_IT, sent="neu", viral=0.6, tags=["vinted", "usato"], label="noise_secondhand"),
    S("n_2h_fr", "fr", 16, {"instagram": .6, "x": .4}, BASE, ["{Je vends|Vends} {ma|une} doudoune Moncler {taille 1|taille 2} {sur Vinted|portée deux fois}, {prix en MP|lien en bio}"],
      kind={"user": 1}, places={"PAR01": 1}, sent="neu", viral=0.6, tags=["vinted", "secondemain"], label="noise_secondhand"),
    S("n_2h_de", "de", 14, {"instagram": .6, "x": .4}, BASE, ["{Verkaufe|Biete} Moncler {Weste|Jacke} Gr. {3|4}, {kaum getragen|wie neu}, {bei Kleinanzeigen|Preis per DM}"],
      kind={"user": 1}, places=ANY_DE, sent="neu", viral=0.6, tags=["secondhand"], label="noise_secondhand"),
    S("n_2h_nl", "nl", 10, {"instagram": 1.0}, BASE, ["{Te koop|Verkoop}: Moncler {bodywarmer|jas} maat {2|3}, {nauwelijks gedragen|als nieuw}, {DM|via Vinted}"],
      kind={"user": 1}, places={"AMS01": 1}, sent="neu", viral=0.6, tags=["vinted"], label="noise_secondhand"),
    S("n_2h_da", "da", 10, {"instagram": 1.0}, BASE, ["{Sælger|Til salg}: Moncler {vest|dunjakke} str. {2|3}, {næsten ny|brugt få gange}, {skriv for pris|DM}"],
      kind={"user": 1}, places={"CPH01": 1}, sent="neu", viral=0.6, tags=["genbrug", "trendsales"], label="noise_secondhand"),
    S("n_2h_ko", "ko", 14, {"naver_cafe": .6, "instagram": .4}, BASE, ["몽클레어 {마야|조끼|패딩} {3사이즈|2사이즈} {판매합니다|팝니다}. {몇 번 안 입었어요|상태 좋아요} {당근에도 올렸어요|댓글 주세요}"],
      kind={"user": 1}, places=ANY_KR, sent="neu", viral=0.6, tags=[], titles=["[판매] 몽클레어 패딩", "몽클 마야 중고 판매"], cafes="fashion", kw=["몽클레어 중고"], label="noise_secondhand"),
    S("n_2h_ja", "ja", 10, {"x": 1.0}, BASE, ["モンクレの{ベスト|ダウン}{メルカリに出した|売ります}。{サイズ2|サイズ1}、{美品|数回着用}"],
      kind={"user": 1}, places=ANY_JP, sent="neu", viral=0.6, tags=["メルカリ"], label="noise_secondhand"),

    # ===================================================================== pets
    S("n_pets", "en", 10, {"instagram": 1.0}, BASE, ["{Biscuit|Milo|Luna} {in his|in her} {new|first} puffer {🐶|🐾} {winter ready|too cute}"],
      kind={"user": 1}, places=ANY_EN, sent="pos", viral=1.0, tags=["dogsofinstagram", "dogfashion"], label="noise_pets"),
    S("n_pets_ko", "ko", 8, {"instagram": 1.0}, BASE, ["{우리 강아지|우리 콩이|우리 보리} {패딩|겨울옷} {개시|입혔어요} {🐶|🐾}"],
      kind={"user": 1}, places=ANY_KR, sent="pos", viral=1.0, tags=["강아지옷", "멍스타그램"], label="noise_pets"),

    # ===================================================================== too early for a puffer (Aug-Sep)
    S("n_early_en", "en", 20, {"x": .7, "threads": .3}, EARLY, [
        "{stores|shops} already full of puffers and it's {32 degrees|still summer} {💀|}",
        "{who|Who} is buying a down jacket in {August|September} {genuinely asking|lol}",
    ], kind={"user": 1}, places=ANY_EN, sent="neu", viral=0.8, tags=[], label="noise_early"),
    S("n_early_it", "it", 15, {"x": .7, "instagram": .3}, EARLY, ["{Vetrine|Le vetrine} già piene di piumini e fuori ci sono {33|34} gradi {🥵|}"],
      kind={"user": 1}, places=ANY_IT, sent="neu", viral=0.8, tags=[], label="noise_early"),
    S("n_early_ko", "ko", 10, {"x": .7, "threads": .3}, EARLY, ["{백화점|매장}에 벌써 패딩 {깔렸네|나왔네}.. 밖은 {33도|34도}{ㅋㅋ|}"],
      kind={"user": 1}, places=ANY_KR, sent="neu", viral=0.8, tags=[], label="noise_early"),

    # ===================================================================== reddit general questions / authenticity
    S("n_reddit_q", "en", 50, {"reddit": 1.0}, BASE, [
        "{Is Moncler worth it|Moncler worth the money}? {Torn between it and a cheaper brand|First 'luxury' jacket, need advice}",
        "{Legit check|LC} please — {bought|found} a Moncler on {Vinted|eBay|Depop} for {€300|$350}. {Label pics attached|Pics in comments}",
        "{How warm|How warm actually} is a Moncler {for Chicago winters|at -15C}? {Thinking about the Montgenevre|Considering the Maya}",
        "{Moncler|Down jacket} {care|washing} — {can I machine wash|dry cleaning} {mine|a 10 year old jacket}?",
        "{Best|Where's the best} place to buy Moncler {tax-free|in Europe}? {Going to Paris in November|Trip to Milan soon}",
    ], kind={"user": 1}, places=ANY_EN, sent="neu", viral=0.9, tags=[],
      titles=["Is Moncler worth it?", "Legit check please", "How warm is a Moncler really?", "Washing a Moncler jacket?", "Cheapest place to buy Moncler in Europe?",
              "First luxury jacket - advice?", "Moncler sizing in general - TTS?"],
      subs=["malefashionadvice", "femalefashionadvice", "monclerheads", "Repladies", "BuyItForLife"], label="noise_reddit_q"),

    # ===================================================================== hashtag hijack / travel
    S("n_travel_en", "en", 20, {"instagram": .8, "tiktok": .2}, BASE, [
        "{Sunset|Golden hour} in {Santorini|Bali|Lisbon} {🌅|} {#moncler #travel #wanderlust|}",
        "{Brunch|Coffee} {with a view|by the sea} {☕️|🌊}",
    ], kind={"user": 1, "micro": 1}, places=ANY_EN, sent="pos", viral=0.9, tags=["travel", "wanderlust", "moncler", "luxurylifestyle"], label="noise_travel"),
    S("n_travel_es", "es", 10, {"instagram": 1.0}, BASE, ["{Atardecer|Puesta de sol} en {Ibiza|Tenerife} {🌅|}"],
      kind={"user": 1}, places={"MAD01": 1}, sent="pos", viral=0.9, tags=["viajes", "moncler", "lujo"], label="noise_travel"),

    # ===================================================================== China: daigou / other-brand 种草
    S("n_cn_daigou", "zh-CN", 35, {"weibo": .6, "xhs": .4}, BASE, [
        "{欧洲|意大利|法国}代购{本周|今日}{接单|开团}：{盟可睐|蒙口}/{Max Mara|Prada}{羽绒服|大衣}{，价格私聊|，可小票}",
        "{秋冬|今年冬天}{羽绒服|外套}{种草|清单}：{盟可睐|Moncler}、{Max Mara|Loro Piana}、{Prada|Miu Miu}{，你选哪个|}",
    ], kind={"daigou": 2, "user": 1}, places=ANY_CN, sent="neu", viral=0.8, tags=["代购", "种草", "羽绒服"], titles=["欧洲代购 本周接单", "秋冬外套种草清单"], label="noise_cn_misc"),
    S("n_cn_misc", "zh-CN", 25, {"weibo": 1.0}, BASE, [
        "{今天|周末}{降温|变天}了，{羽绒服|外套}{该拿出来了|准备好了吗}",
        "{双十一|年底}{攒钱|存钱}{计划|中}{😭|}",
    ], kind={"user": 1}, places=ANY_CN, sent="neu", viral=0.8, tags=["降温"], label="noise_cn_misc"),

    # ===================================================================== Korea naver: general shopping blogs
    S("n_kr_shopping", "ko", 55, {"naver_blog": .6, "naver_cafe": .4}, BASE, [
        "{면세점|인천공항 면세점}에서 {몽클레어|몽클} {카드지갑|머플러|비니} {샀어요|득템}. {가격 비교|국내가 대비} {정리해봤어요|공유합니다}",
        "{백화점|더현대} {몽클레어|몽클} 매장 {구경|방문} 후기. {올해 신상|FW26 신상} {많이 들어왔더라구요|예뻐요}",
        "{몽클레어|몽클} {국내 가격 인상|가격 인상} {언제|소식 있나요}? {작년엔 3월에 올랐던 것 같은데|미리 사야 하나 고민}",
        "{유럽 여행|이탈리아 여행} {쇼핑 리스트|쇼핑 후기}: {몽클|몽클레어}, {막스마라|프라다}, {택스리펀|면세} {꿀팁|정리}",
        "{롱패딩|숏패딩} {고르는 법|추천} {2026|올겨울} - {몽클레어|여러 브랜드} {비교|정리}",
    ], kind={"user": 1}, places=ANY_KR, sent="neu", viral=0.9, tags=[],
      titles=["인천공항 면세점 몽클레어 쇼핑 후기", "더현대 몽클레어 FW26 신상 구경", "몽클레어 가격 인상 정보", "이탈리아 여행 쇼핑리스트 + 택스리펀 꿀팁",
              "올겨울 패딩 추천 (몽클레어 포함)", "백화점 명품관 쇼핑 브이로그"],
      cafes="mixed", kw=["몽클레어", "몽클레어 가격", "몽클레어 면세점", "명품 패딩 추천"], label="noise_kr_shopping"),
]
