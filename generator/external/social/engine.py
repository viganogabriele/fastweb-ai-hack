"""Engine for the social-listening dataset: templating, places, authors, timing, metrics.

Everything is deterministic: every topic gets its own random.Random seeded from a stable hash of its key.
"""
import datetime as dt
import hashlib
import math
import random
import re
import string
from zoneinfo import ZoneInfo

UTC = dt.timezone.utc
T_START = dt.datetime(2026, 8, 1, 0, 0, tzinfo=UTC)
T_CUTOFF = dt.datetime(2026, 10, 22, 6, 0, tzinfo=UTC)   # = 08:00 CEST, last pull of all vendors


def stable_seed(*parts):
    h = hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()
    return int(h[:15], 16)


def R(*parts):
    return random.Random(stable_seed("social-v1", *parts))


def ts(s):
    """'2026-10-01' or '2026-10-01T17:30' (UTC) -> aware datetime."""
    if "T" in s:
        return dt.datetime.fromisoformat(s).replace(tzinfo=UTC)
    return dt.datetime.fromisoformat(s + "T00:00").replace(tzinfo=UTC)


# ---------------------------------------------------------------------------
# language groups
# ---------------------------------------------------------------------------
def lg(lang):
    return {"zh-CN": "zh", "zh-TW": "zht", "zh-HK": "zht"}.get(lang, lang)


# ---------------------------------------------------------------------------
# Places (stores + a few generic places).  names: lang-group -> list
# ---------------------------------------------------------------------------
def P(tz, city, store, geo, cc):
    return dict(tz=tz, city=city, store=store, geo=geo, cc=cc)


PLACES = {
    "SEL01": P("Asia/Seoul", dict(ko=["서울"], en=["Seoul"], zh=["首尔"], zht=["首爾"], ja=["ソウル"]),
               dict(ko=["청담 플래그십", "청담 매장", "청담점", "청담 몽클", "청담동 플래그십", "청담 본점"],
                    en=["the Cheongdam flagship", "Cheongdam store", "Cheongdam"], zh=["首尔清潭旗舰店", "清潭洞店"],
                    zht=["清潭洞旗艦店"], ja=["清潭洞の旗艦店", "清潭の路面店"]),
               [("Moncler Cheongdam", 37.5245, 127.047), ("청담동 Cheongdam-dong", 37.5251, 127.0478),
                ("Gangnam-gu, Seoul", 37.5172, 127.0473)], "KR"),
    "SEL02": P("Asia/Seoul", dict(ko=["서울"], en=["Seoul"], zh=["首尔"], zht=["首爾"], ja=["ソウル"]),
               dict(ko=["현대 압구정", "압구정 현대", "압현", "현대백화점 압구정본점", "압구정 현대백화점"],
                    en=["Hyundai Apgujeong", "the Hyundai dept store in Apgujeong"], zh=["狎鸥亭现代百货"],
                    zht=["狎鷗亭現代百貨"], ja=["現代百貨店狎鴎亭"]),
               [("현대백화점 압구정본점", 37.5272, 127.028), ("Apgujeong", 37.527, 127.028)], "KR"),
    "BUS01": P("Asia/Seoul", dict(ko=["부산"], en=["Busan"], zh=["釜山"], zht=["釜山"], ja=["釜山"]),
               dict(ko=["센텀 신세계", "신세계 센텀시티", "센텀", "부산 신세계"], en=["Shinsegae Centum City"],
                    zh=["釜山新世界"], zht=["釜山新世界"], ja=["新世界センタムシティ"]),
               [("신세계 센텀시티 Shinsegae Centum City", 35.169, 129.129), ("Haeundae, Busan", 35.163, 129.163)], "KR"),
    "SHA01": P("Asia/Shanghai", dict(zh=["上海", "魔都"], zht=["上海"], en=["Shanghai"], ko=["상하이"], ja=["上海"]),
               dict(zh=["恒隆", "恒隆广场", "恒隆店", "Plaza66", "南京西路恒隆", "66"], zht=["恆隆廣場"], en=["Plaza 66"],
                    ko=["상하이 플라자66"], ja=["上海の恒隆広場"]),
               [("上海恒隆广场 Plaza 66", 31.229, 121.455)], "CN"),
    "BJS01": P("Asia/Shanghai", dict(zh=["北京", "帝都"], zht=["北京"], en=["Beijing"], ko=["베이징"], ja=["北京"]),
               dict(zh=["SKP", "北京SKP", "大望路SKP", "skp"], zht=["北京SKP"], en=["SKP Beijing"], ko=["베이징 SKP"], ja=["北京SKP"]),
               [("北京SKP", 39.909, 116.481)], "CN"),
    "CDU01": P("Asia/Shanghai", dict(zh=["成都"], zht=["成都"], en=["Chengdu"], ko=["청두"], ja=["成都"]),
               dict(zh=["太古里", "成都太古里", "远洋太古里", "太古里店"], zht=["成都太古里"], en=["Taikoo Li Chengdu"],
                    ko=["청두 타이쿠리"], ja=["成都太古里"]),
               [("成都远洋太古里", 30.653, 104.082)], "CN"),
    "HKG01": P("Asia/Hong_Kong", dict(zht=["香港"], zh=["香港"], en=["Hong Kong", "HK"], ko=["홍콩"], ja=["香港"]),
               dict(zht=["廣東道", "尖沙咀廣東道", "廣東道舖", "海港城對面間"], zh=["广东道", "尖沙咀广东道店"],
                    en=["Canton Road", "the Canton Rd store"], ko=["홍콩 캔톤로드"], ja=["香港の廣東道"]),
               [("Canton Road, Tsim Sha Tsui", 22.296, 114.169), ("尖沙咀 Tsim Sha Tsui", 22.2988, 114.1722)], "HK"),
    "TPE01": P("Asia/Taipei", dict(zht=["台北"], zh=["台北"], en=["Taipei"], ko=["타이베이"], ja=["台北"]),
               dict(zht=["101", "台北101", "101的櫃", "101那間"], zh=["台北101"], en=["Taipei 101"], ko=["타이베이 101"],
                    ja=["台北101"]),
               [("台北101 Taipei 101", 25.034, 121.5645), ("信義區 Xinyi District", 25.033, 121.567)], "TW"),
    "SIN01": P("Asia/Singapore", dict(en=["Singapore", "SG"], zh=["新加坡"], zht=["新加坡"], ko=["싱가포르"], ja=["シンガポール"]),
               dict(en=["MBS", "Marina Bay Sands", "The Shoppes at MBS", "the MBS boutique"], zh=["金沙"], zht=["金沙"],
                    ko=["마리나베이샌즈"], ja=["マリーナベイ・サンズ"]),
               [("The Shoppes at Marina Bay Sands", 1.2834, 103.8607), ("Marina Bay, Singapore", 1.2823, 103.8585)], "SG"),
    "TYO01": P("Asia/Tokyo", dict(ja=["東京"], en=["Tokyo"], ko=["도쿄"], zh=["东京"], zht=["東京"]),
               dict(ja=["銀座", "銀座店", "銀座の旗艦店", "銀座のモンクレ"], en=["Ginza"], ko=["긴자"], zh=["银座"], zht=["銀座"]),
               [("銀座 Ginza", 35.6717, 139.765), ("Ginza, Tokyo", 35.6712, 139.7665)], "JP"),
    "TYO02": P("Asia/Tokyo", dict(ja=["東京"], en=["Tokyo"], ko=["도쿄"], zh=["东京"], zht=["東京"]),
               dict(ja=["表参道", "表参道店", "表参道のお店"], en=["Omotesando"], ko=["오모테산도"], zh=["表参道"], zht=["表參道"]),
               [("表参道 Omotesando", 35.6655, 139.712)], "JP"),
    "OSA01": P("Asia/Tokyo", dict(ja=["大阪"], en=["Osaka"], ko=["오사카"], zh=["大阪"], zht=["大阪"]),
               dict(ja=["心斎橋", "心斎橋店", "心斎橋のモンクレ"], en=["Shinsaibashi"], ko=["신사이바시"], zh=["心斋桥"], zht=["心齋橋"]),
               [("心斎橋 Shinsaibashi", 34.674, 135.501)], "JP"),
    "PAR01": P("Europe/Paris", dict(fr=["Paris"], en=["Paris"], ko=["파리"], zh=["巴黎"], zht=["巴黎"], ja=["パリ"], it=["Parigi"], de=["Paris"], es=["París"]),
               dict(fr=["Saint-Honoré", "la boutique Saint-Honoré", "rue Saint-Honoré"], en=["Saint-Honoré", "the Saint-Honoré flagship"],
                    ko=["생토노레 매장", "생토노레 본점", "생토노레", "포부르 생토노레 매장"], zh=["圣奥诺雷街店", "圣奥诺雷"],
                    zht=["聖奧諾雷街"], ja=["サントノーレ店"], it=["Saint-Honoré"], es=["Saint-Honoré"]),
               [("Rue du Faubourg Saint-Honoré", 48.8686, 2.3224), ("Paris, France", 48.8566, 2.3522)], "FR"),
    "PAR02": P("Europe/Paris", dict(fr=["Paris"], en=["Paris"], ko=["파리"], zh=["巴黎"], zht=["巴黎"], ja=["パリ"], it=["Parigi"], de=["Paris"], es=["París"]),
               dict(fr=["les Galeries Lafayette", "Galeries Laf", "les Galeries", "GL Haussmann"], en=["Galeries Lafayette"],
                    ko=["라파예트", "갤러리 라파예트", "라파예트 백화점"], zh=["老佛爷", "老佛爷百货", "老佛爷本店"],
                    zht=["老佛爺"], ja=["ギャラリー・ラファイエット", "ラファイエット"], it=["Galeries Lafayette"], es=["Galeries Lafayette"]),
               [("Galeries Lafayette Paris Haussmann", 48.8738, 2.332), ("Paris, France", 48.8566, 2.3522)], "FR"),
    "MIL01": P("Europe/Rome", dict(it=["Milano"], en=["Milan"], ko=["밀라노"], zh=["米兰"], zht=["米蘭"], ja=["ミラノ"], fr=["Milan"], de=["Mailand"], es=["Milán"]),
               dict(it=["Montenapoleone", "Monte Napo", "via Montenapoleone", "Montenapo"], en=["Montenapoleone", "Via Monte Napoleone"],
                    ko=["몬테나폴레오네 매장", "몬테나폴레오네", "몬테 나폴레오네 본점"], zh=["蒙特拿破仑大街店", "蒙特街", "蒙特拿破仑"],
                    zht=["蒙特拿破崙大街"], ja=["モンテナポレオーネ店"], fr=["Montenapoleone"], de=["Montenapoleone"], es=["Montenapoleone"]),
               [("Via Monte Napoleone", 45.4685, 9.1955), ("Milano, Italia", 45.4642, 9.19)], "IT"),
    "MIL02": P("Europe/Rome", dict(it=["Milano"], en=["Milan"], ko=["밀라노"], zh=["米兰"], zht=["米蘭"], ja=["ミラノ"]),
               dict(it=["Rinascente", "la Rinascente", "Rinascente Duomo"], en=["Rinascente"], ko=["두오모 리나센테", "리나센테"],
                    zh=["文艺复兴百货", "Rinascente百货"], zht=["文藝復興百貨"], ja=["リナシェンテ"]),
               [("La Rinascente Milano", 45.4655, 9.1912), ("Duomo di Milano", 45.4641, 9.1919)], "IT"),
    "LON01": P("Europe/London", dict(en=["London"], ko=["런던"], zh=["伦敦"], zht=["倫敦"], ja=["ロンドン"]),
               dict(en=["New Bond Street", "Bond St", "the Bond Street flagship"], ko=["뉴본드스트리트"], zh=["新邦德街店"],
                    zht=["新龐德街"], ja=["ニューボンドストリート店"]),
               [("New Bond Street", 51.5122, -0.145), ("Mayfair, London", 51.511, -0.147)], "GB"),
    "LON02": P("Europe/London", dict(en=["London"], ko=["런던"], zh=["伦敦"], zht=["倫敦"], ja=["ロンドン"]),
               dict(en=["Harrods", "Harrods Knightsbridge"], ko=["해롯", "해롯백화점", "해롯 백화점"], zh=["哈罗德", "哈罗德百货"],
                    zht=["哈洛德"], ja=["ハロッズ"]),
               [("Harrods", 51.4994, -0.1632), ("Knightsbridge, London", 51.5015, -0.1607)], "GB"),
    "ROM01": P("Europe/Rome", dict(it=["Roma"], en=["Rome"], zh=["罗马"]), dict(it=["via Condotti", "Condotti"], en=["Via Condotti"], zh=["孔多蒂大街"]),
               [("Via dei Condotti", 41.9055, 12.48), ("Piazza di Spagna", 41.9058, 12.4823)], "IT"),
    "VEN01": P("Europe/Rome", dict(it=["Venezia"], en=["Venice"], zh=["威尼斯"]), dict(it=["San Marco", "Piazza San Marco"], en=["San Marco"]),
               [("Piazza San Marco", 45.4341, 12.3388), ("Venezia, Italia", 45.4408, 12.3155)], "IT"),
    "MUN01": P("Europe/Berlin", dict(de=["München", "Muc"], en=["Munich"], it=["Monaco"]), dict(de=["Maximilianstraße", "Maxstraße", "Maximilianstr."], en=["Maximilianstrasse"]),
               [("Maximilianstraße München", 48.1394, 11.5823), ("München, Germany", 48.1374, 11.5755)], "DE"),
    "BER01": P("Europe/Berlin", dict(de=["Berlin"], en=["Berlin"]), dict(de=["KaDeWe", "im KaDeWe"], en=["KaDeWe"]),
               [("KaDeWe", 52.5016, 13.3411), ("Berlin, Germany", 52.52, 13.405)], "DE"),
    "ZRH01": P("Europe/Zurich", dict(de=["Zürich", "Züri"], en=["Zurich"]), dict(de=["Bahnhofstrasse"], en=["Bahnhofstrasse"]),
               [("Bahnhofstrasse Zürich", 47.37, 8.539), ("Zürich, Switzerland", 47.3769, 8.5417)], "CH"),
    "STM01": P("Europe/Zurich", dict(de=["St. Moritz"], en=["St. Moritz"], it=["St. Moritz"]), dict(de=["Via Serlas"], en=["St. Moritz"]),
               [("St. Moritz", 46.4983, 9.839), ("Corviglia", 46.509, 9.811)], "CH"),
    "GVA01": P("Europe/Zurich", dict(fr=["Genève"], en=["Geneva"]), dict(fr=["rue du Rhône"], en=["Rue du Rhône"]),
               [("Rue du Rhône Genève", 46.2033, 6.1478), ("Genève, Suisse", 46.2044, 6.1432)], "CH"),
    "CPH01": P("Europe/Copenhagen", dict(da=["København", "Kbh"], en=["Copenhagen", "CPH"]), dict(da=["Østergade", "Strøget"], en=["Østergade"]),
               [("Strøget København", 55.679, 12.58), ("Copenhagen, Denmark", 55.6761, 12.5683)], "DK"),
    "AMS01": P("Europe/Amsterdam", dict(nl=["Amsterdam", "A'dam"], en=["Amsterdam"]), dict(nl=["P.C. Hooftstraat", "de PC", "PC Hooft"], en=["PC Hooftstraat"]),
               [("P.C. Hooftstraat", 52.359, 4.878), ("Amsterdam, Netherlands", 52.3676, 4.9041)], "NL"),
    "MAD01": P("Europe/Madrid", dict(es=["Madrid"], en=["Madrid"]), dict(es=["Serrano", "calle Serrano"], en=["Serrano"]),
               [("Calle de Serrano", 40.426, -3.687), ("Madrid, España", 40.4168, -3.7038)], "ES"),
    "NYC01": P("America/New_York", dict(en=["NYC", "New York"]), dict(en=["Madison Ave", "Madison"]),
               [("Madison Avenue", 40.768, -73.966), ("Upper East Side, Manhattan", 40.7736, -73.9566)], "US"),
    "NYC02": P("America/New_York", dict(en=["NYC", "New York"]), dict(en=["SoHo", "the SoHo store"]),
               [("SoHo, New York", 40.724, -74.001)], "US"),
    "BHS01": P("America/Los_Angeles", dict(en=["LA", "Beverly Hills"]), dict(en=["Rodeo Drive", "Rodeo"]),
               [("Rodeo Drive", 34.068, -118.401), ("Beverly Hills, California", 34.0736, -118.4004)], "US"),
    "MIA01": P("America/New_York", dict(en=["Miami"]), dict(en=["Design District"]), [("Miami Design District", 25.813, -80.193)], "US"),
    "TOR01": P("America/Toronto", dict(en=["Toronto"]), dict(en=["Yorkville"]), [("Yorkville, Toronto", 43.671, -79.393)], "CA"),
    "SYD01": P("Australia/Sydney", dict(en=["Sydney"]), dict(en=["Castlereagh St"]), [("Sydney, New South Wales", -33.869, 151.208)], "AU"),
    "DXB01": P("Asia/Dubai", dict(en=["Dubai"]), dict(en=["Dubai Mall"]), [("The Dubai Mall", 25.1985, 55.2796)], "AE"),
    "ASP01": P("America/Denver", dict(en=["Aspen"]), dict(en=["Aspen"]), [("Aspen, Colorado", 39.189, -106.818)], "US"),
    "CRT01": P("Europe/Rome", dict(it=["Cortina"], en=["Cortina"]), dict(it=["Cortina", "corso Italia"]), [("Cortina d'Ampezzo", 46.5405, 12.1357)], "IT"),
    "CAN01": P("Europe/Paris", dict(fr=["Cannes"], en=["Cannes"]), dict(fr=["la Croisette"]), [("La Croisette, Cannes", 43.5503, 7.0225)], "FR"),
    # non-store places
    "KR_HOME": P("Asia/Seoul", dict(ko=["서울"], en=["Seoul"]), dict(ko=[""]), [("Seoul, South Korea", 37.5665, 126.978), ("Seongsu-dong", 37.5446, 127.0557), ("Hongdae", 37.5563, 126.9236)], "KR"),
    "CN_HOME": P("Asia/Shanghai", dict(zh=["上海"], en=["Shanghai"]), dict(zh=[""]), [], "CN"),
    "JP_HOME": P("Asia/Tokyo", dict(ja=["東京"], en=["Tokyo"]), dict(ja=[""]), [("Shibuya, Tokyo", 35.658, 139.7016), ("Tokyo, Japan", 35.6762, 139.6503)], "JP"),
    "US_HOME": P("America/New_York", dict(en=["NYC"]), dict(en=[""]), [("Brooklyn, New York", 40.6782, -73.9442), ("Los Angeles, California", 34.0522, -118.2437), ("Chicago, Illinois", 41.8781, -87.6298)], "US"),
    "UK_HOME": P("Europe/London", dict(en=["London"]), dict(en=[""]), [("London, United Kingdom", 51.5072, -0.1276), ("Manchester, United Kingdom", 53.4808, -2.2426)], "GB"),
    "MONESTIER": P("Europe/Paris", dict(fr=["Monestier-de-Clermont"]), dict(fr=[""]), [("Monestier-de-Clermont", 44.9156, 5.6342), ("Vercors", 44.95, 5.5)], "FR"),
    "COU01": P("Europe/Rome", dict(it=["Courmayeur"]), dict(it=["Courmayeur"]), [("Courmayeur", 45.7969, 6.969)], "IT"),
}
DEFAULT_TZ = {"ko": "Asia/Seoul", "ja": "Asia/Tokyo", "zh-CN": "Asia/Shanghai", "zh-HK": "Asia/Hong_Kong", "zh-TW": "Asia/Taipei",
              "en": "Europe/London", "it": "Europe/Rome", "fr": "Europe/Paris", "de": "Europe/Berlin", "es": "Europe/Madrid",
              "nl": "Europe/Amsterdam", "da": "Europe/Copenhagen"}


def place_name(place, field, lang, rng):
    d = PLACES[place][field]
    g = lg(lang)
    opts = d.get(g) or d.get("en") or next(iter(d.values()))
    return rng.choice(opts)


# ---------------------------------------------------------------------------
# Template expansion: {a|b|c} alternatives (nestable), $slot substitution
# ---------------------------------------------------------------------------
ALT = re.compile(r"\{([^{}]*)\}")
SLOT = re.compile(r"\$([a-z][a-z_0-9]*)")


def expand(rng, s, slots):
    def rep(m):
        k = m.group(1)
        if k not in slots:
            return m.group(0)
        v = slots[k]
        v = v() if callable(v) else v
        return str(v)
    s = SLOT.sub(rep, s)
    while True:
        m = ALT.search(s)
        if not m:
            break
        s = s[:m.start()] + rng.choice(m.group(1).split("|")) + s[m.end():]
    s = re.sub(r"[ \t]{2,}", " ", s)
    s = re.sub(r" +([,.!?;:，。！？、])", r"\1", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


# ---------------------------------------------------------------------------
# Time sampling
# ---------------------------------------------------------------------------
DIURNAL = [0.35, 0.25, 0.15, 0.1, 0.08, 0.1, 0.2, 0.4, 0.6, 0.72, 0.8, 0.9, 1.0, 0.95, 0.85, 0.8, 0.8, 0.85,
           0.95, 1.0, 1.0, 1.0, 0.9, 0.6]


def curve_fn(points):
    pts = [(ts(a), float(w)) for a, w in points]

    def f(t):
        if t < pts[0][0] or t > pts[-1][0]:
            return 0.0
        for (t0, w0), (t1, w1) in zip(pts, pts[1:]):
            if t0 <= t <= t1:
                span = (t1 - t0).total_seconds() or 1
                return w0 + (w1 - w0) * (t - t0).total_seconds() / span
        return pts[-1][1]
    return f, pts[0][0], min(pts[-1][0], T_CUTOFF), max(w for _, w in pts)


def sample_time(rng, curve, tz, diurnal=True):
    f, a, b, fmax = curve
    span = (b - a).total_seconds()
    z = ZoneInfo(tz)
    for _ in range(5000):
        t = a + dt.timedelta(seconds=rng.random() * span)
        w = f(t) / fmax
        if diurnal:
            w *= DIURNAL[t.astimezone(z).hour]
        if rng.random() < w:
            return t.replace(microsecond=0)
    return (a + dt.timedelta(seconds=rng.random() * span)).replace(microsecond=0)


# ---------------------------------------------------------------------------
# Authors
# ---------------------------------------------------------------------------
NAMES = {
    "ko": (["jiyeon", "minji", "seoyeon", "hyejin", "sooah", "yuna", "daeun", "hana", "jisoo", "eunbi", "sora", "yerin",
            "chaewon", "minseo", "haneul", "dahye", "jiwoo", "seojin", "nayeon", "hyunwoo", "minho", "junho", "dohyun",
            "sungmin", "jaehyun", "yoonji", "sujin", "bora", "gaeun", "seulgi"],
           ["지연", "민지", "서연", "혜진", "수아", "유나", "다은", "하나", "지수", "은비", "소라", "예린", "채원", "민서", "하늘",
            "다혜", "지우", "서진", "나연", "현우", "민호", "준호", "도현", "성민", "재현", "윤지", "수진", "보라", "가은", "슬기"]),
    "ja": (["miyu", "haruka", "saki", "yui", "rina", "aoi", "mei", "kana", "nana", "riko", "mao", "shiori", "yuki",
            "sora", "takumi", "ren", "kaito", "misaki", "ayaka", "honoka"],
           ["みゆ", "はるか", "さき", "ゆい", "りな", "あおい", "めい", "かな", "なな", "りこ", "まお", "しおり", "ゆき", "そら",
            "たくみ", "れん", "かいと", "みさき", "あやか", "ほのか"]),
    "zh-HK": (["kaying", "wingyan", "hiutung", "chloe.hk", "natalie", "cherry", "tsz", "hoiyan", "kelvin", "jason"],
              ["嘉欣", "詠欣", "曉彤", "Chloe", "Natalie", "Cherry", "芷晴", "凱欣", "Kelvin", "Jason"]),
    "zh-TW": (["yuchen", "yating", "peishan", "yijun", "tingyu", "weiting", "hsinyi", "chiahui", "kevin.tw", "annie"],
              ["宇晨", "雅婷", "佩珊", "怡君", "庭妤", "瑋婷", "欣怡", "佳慧", "Kevin", "Annie"]),
    "zh-CN": (["vivi", "cici", "lulu", "xiaoyu", "mengmeng", "echo", "momo", "yoyo", "kiki", "jojo"],
              ["Vivi", "Cici", "Lulu", "小雨", "萌萌", "Echo", "Momo", "Yoyo", "Kiki", "Jojo"]),
    "en": (["emma", "olivia", "jake", "liam", "sophie", "maddie", "chris", "noah", "ava", "harry", "ellie", "sam",
            "megan", "ryan", "zoe", "nina", "dan", "tash", "priya", "marcus", "grace", "ethan", "jess", "tom"],
           ["Emma", "Olivia", "Jake", "Liam", "Sophie", "Maddie", "Chris", "Noah", "Ava", "Harry", "Ellie", "Sam",
            "Megan", "Ryan", "Zoe", "Nina", "Dan", "Tash", "Priya", "Marcus", "Grace", "Ethan", "Jess", "Tom"]),
    "it": (["giulia", "francesca", "chiara", "marco", "luca", "ale", "fede", "martina", "sara", "matteo", "giorgia",
            "lorenzo", "bea", "vale", "simo"],
           ["Giulia", "Francesca", "Chiara", "Marco", "Luca", "Ale", "Fede", "Martina", "Sara", "Matteo", "Giorgia",
            "Lorenzo", "Bea", "Vale", "Simo"]),
    "fr": (["camille", "lea", "chloe", "manon", "ines", "hugo", "theo", "lucas", "clem", "margaux", "julien", "pauline"],
           ["Camille", "Léa", "Chloé", "Manon", "Inès", "Hugo", "Théo", "Lucas", "Clém", "Margaux", "Julien", "Pauline"]),
    "de": (["lena", "anna", "lisa", "leonie", "max", "felix", "jonas", "lukas", "flo", "kathi", "basti", "nina"],
           ["Lena", "Anna", "Lisa", "Leonie", "Max", "Felix", "Jonas", "Lukas", "Flo", "Kathi", "Basti", "Nina"]),
    "es": (["lucia", "paula", "marta", "alba", "javi", "pablo", "carlos", "irene", "nacho", "bea"],
           ["Lucía", "Paula", "Marta", "Alba", "Javi", "Pablo", "Carlos", "Irene", "Nacho", "Bea"]),
    "nl": (["sanne", "lotte", "fleur", "daan", "bram", "sem", "noor", "jesse"],
           ["Sanne", "Lotte", "Fleur", "Daan", "Bram", "Sem", "Noor", "Jesse"]),
    "da": (["mette", "freja", "ida", "emma", "mads", "frederik", "oliver", "sofie"],
           ["Mette", "Freja", "Ida", "Emma", "Mads", "Frederik", "Oliver", "Sofie"]),
}
CITY_SUFFIX = {"ko": ["seoul", "busan", "kr"], "ja": ["tokyo", "jp", "osaka"], "zh-HK": ["hk", "852"], "zh-TW": ["tw", "tpe"],
               "zh-CN": ["sh", "bj"], "en": ["ldn", "nyc", "sg", "la", "uk"], "it": ["mi", "milano", "roma"],
               "fr": ["paris", "pls"], "de": ["muc", "ber", "zh"], "es": ["mad"], "nl": ["ams", "nl"], "da": ["cph", "dk"]}
HANDLE_PAT = ["{n}_daily", "{n}.ootd", "{n}_{yy}", "{n}{mmdd}", "_{n}_", "{n}_{city}", "{n}log", "{n}.zip", "dear.{n}",
              "{n}_closet", "{n}.travels", "its{n}", "{n}__{n2}", "{n}.{city}", "the.{n}", "{n}{yy}{n2}", "{n}_wears", "{n}.k"]

FOLLOWERS = {  # kind: (mu, sigma) of lognormal
    "user": (6.3, 1.2), "micro": (9.4, 0.8), "influencer": (11.6, 0.9), "fan": (9.8, 1.4), "media": (12.4, 1.0),
    "reseller": (7.6, 1.0), "bot": (3.2, 1.0), "scam": (5.5, 1.3), "brand_store": (8.5, 0.6), "daigou": (8.6, 1.0),
}

REDDIT_W1 = ["quiet", "Throwaway", "puffer", "Salty", "lazy", "cold", "Big", "tiny", "Seoul", "nordic", "Urban", "late",
             "random", "Pale", "oddly", "Grumpy", "sunny", "Fuzzy", "Retired", "Mild"]
REDDIT_W2 = ["cartographer", "Down", "enjoyer", "Penguin", "Duvet", "goose", "Parka", "Searching", "Walrus", "lurker",
             "Owl", "Commuter", "Vest", "Zipper", "Hiker", "Badger", "Trench", "Otter", "Ferret", "Pigeon"]

WB_PRE = ["是", "一只", "今天也要", "爱吃", "想去", "不想上班的", "上海", "北京", "成都", "小", "", "", "momo家的", "胖胖的"]
WB_CORE = ["小鹿", "芋圆", "奶茶", "橘子", "Vivi", "Cici", "鱼丸", "糯米", "团子", "阿狸", "momo", "小鱼干", "桃子", "柚子",
           "Lulu", "Echo", "芒果", "布丁", "可乐", "汤圆", "栗子", "饭团", "雪糕", "椰子"]
WB_SUF = ["呀", "酱", "_", "的衣橱", "在上海", "不加糖", "同学", "2026", "嘻嘻", "", "", "", "本人", "w", "Official"]
NV_NICK = ["파리지앵", "여행가고싶다", "쇼핑요정", "청담댁", "부산갈매기", "유럽러버", "몽클러버", "럭셔리맘", "하은사랑해", "루미너스",
           "지니", "제제맘", "단풍잎", "빵순이", "꿀벌", "오늘도맑음", "여행하는곰", "파리댁", "런던살이", "밀라노유학생", "봄날의곰",
           "명품초보", "직구왕", "블링블링", "은하수", "코코넛", "치즈냥", "라떼한잔", "가을타는중", "노랑나비", "센텀주민",
           "해운대언니", "성수동러", "강남엄마", "하은이최고", "LUMI사랑", "패딩요정", "겨울왕국", "트래블러", "베이글"]


class AuthorPool:
    def __init__(self):
        self.pools = {}
        self.used_handles = set()

    def _make(self, rng, lang, kind, family):
        if family == "reddit":
            for _ in range(50):
                h = rng.choice(REDDIT_W1) + rng.choice(["_", "", "-"]) + rng.choice(REDDIT_W2) + rng.choice(["", str(rng.randint(1, 99)), str(rng.randint(1000, 9999))])
                if h not in self.used_handles:
                    break
            self.used_handles.add(h)
            return dict(handle=h, display=None, followers=None, verified=False, karma=int(rng.lognormvariate(8, 1.5)))
        if family in ("weibo", "xhs"):
            for _ in range(50):
                if family == "xhs" and rng.random() < 0.12:
                    h = "小红薯" + "".join(rng.choice("0123456789ABCDEF") for _ in range(7))
                elif kind == "daigou":
                    h = rng.choice(["欧洲代购", "日韩代购", "法国代购", "意大利代购", "香港代购", "全球购"]) + rng.choice(["-", "", "_"]) + rng.choice(WB_CORE)
                elif kind == "reseller":
                    h = rng.choice(["二手奢品", "闲置好物", "潮奢", "正品寄卖", "国内现货"]) + rng.choice(WB_CORE)
                elif kind == "scam":
                    h = rng.choice(["顶级复刻", "原单尾货", "一比一", "工厂直出"]) + rng.choice(["小店", "-阿杰", "专卖", "2026", "v"])
                else:
                    h = rng.choice(WB_PRE) + rng.choice(WB_CORE) + rng.choice(WB_SUF)
                if h not in self.used_handles:
                    break
            self.used_handles.add(h)
            mu, sg = FOLLOWERS[kind]
            if family == "xhs":
                mu -= 0.8
            return dict(handle=h, display=h, followers=int(rng.lognormvariate(mu, sg)) + rng.randint(0, 30),
                        verified=(kind in ("influencer", "media") and rng.random() < 0.6),
                        uid=str(rng.randint(1000000000, 7999999999)))
        if family == "naver":
            nick = rng.choice(NV_NICK) + rng.choice(["", "", str(rng.randint(1, 99)), "_", "♡", "★"])
            bid = rng.choice(NAMES["ko"][0]) + rng.choice(["", "_", "0"]) + str(rng.randint(10, 9999))
            return dict(handle=bid, display=nick, followers=None, verified=False)
        # global platforms
        names, disp = NAMES.get(lang, NAMES["en"])
        for _ in range(80):
            i = rng.randrange(len(names))
            n = names[i]
            if kind == "bot":
                h = rng.choice(["moncler", "monc", "lux", "puffer", "jacket", "outlet", "designer"]) + rng.choice(["_outlet", ".deals", "_shop", "sale", "_store", "4u", ".official"]) + rng.choice(["", str(rng.randint(1, 999)), "_" + rng.choice(["it", "us", "eu", "uk", "de", "es"])])
            elif kind == "scam":
                h = rng.choice(["moncler", "luxury", "brand", "designer", "vip"]) + rng.choice([".giveaway", "_giveaways", ".gifts", "_winner", ".promo"]) + rng.choice(["", "2026", ".official", "_team", str(rng.randint(1, 99))])
            elif kind == "reseller":
                h = rng.choice(["resell", "kicks", "lux", "archive", "vault", "plug"]) + rng.choice(["_", ".", ""]) + n + rng.choice(["", "_kr", "_hk", "_jp", "_sg", "store"])
            elif kind == "fan":
                base = rng.choice(["haeun", "lumiere", "haeunie", "lumi", "yoonhaeun", "hae_un"])
                h = rng.choice([base + "_" + n, n + "_" + base, base + ".archive", base + "_pics", "for" + base, base + "_daily" + str(rng.randint(1, 99)), base + "_" + rng.choice(["moon", "sunrain", "petal", "blossom", "star", "film"])])
            elif kind == "media":
                h = rng.choice(["style", "fashion", "kfashion", "luxe", "street", "runway", "idol"]) + rng.choice(["_daily", "news", ".id", "closet", "watch", "_wire", "insider"]) + rng.choice(["", "_" + lang.split("-")[0]])
            elif kind == "brand_store":
                h = rng.choice(["boutique", "luxe", "maison", "atelier"]) + "_" + n
            else:
                pat = rng.choice(HANDLE_PAT)
                h = pat.format(n=n, n2=rng.choice(names), yy=rng.randint(88, 99) if rng.random() < .5 else rng.randint(0, 9),
                               mmdd=f"{rng.randint(1, 12):02d}{rng.randint(1, 28):02d}", city=rng.choice(CITY_SUFFIX.get(lang, ["x"])))
            h = h.lower()
            if h not in self.used_handles:
                break
        self.used_handles.add(h)
        d = disp[i]
        if kind == "fan":
            d = rng.choice(["하은 아카이브", "HAEUN ✦", "윤하은 홈마", "LUMIERE updates", "ハウン🌸", "夏恩的小太阳", d + " | LUMI"]) if lang in ("ko", "en", "ja", "zh-HK", "zh-TW") else d
        elif rng.random() < 0.3:
            d = d + rng.choice([" 🌸", " ✨", " | " + rng.choice(CITY_SUFFIX.get(lang, ["x"])), "🤍", " ☁️"])
        mu, sg = FOLLOWERS[kind]
        f = int(rng.lognormvariate(mu, sg)) + rng.randint(0, 40)
        return dict(handle=h, display=d, followers=f, verified=(kind in ("media", "influencer") and rng.random() < 0.45))

    def get(self, rng, lang, kind, family, expected_n):
        key = (lang, kind, family)
        pool = self.pools.setdefault(key, [])
        size_target = max(3, int(expected_n * (0.35 if kind in ("bot", "scam") else 0.75))) + 2
        if len(pool) < size_target and (not pool or rng.random() < 0.8):
            pool.append(self._make(rng, lang, kind, family))
            return pool[-1]
        # zipf-ish reuse
        w = [1.0 / (i + 1) ** 0.8 for i in range(len(pool))]
        return rng.choices(pool, weights=w)[0]


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def gen_metrics(rng, platform, followers, viral, media_type):
    v = viral * rng.lognormvariate(0, 0.9)
    f = followers or 0
    m = dict(likes=None, comments=None, shares=None, views=None, saves=None)
    if platform == "instagram":
        likes = f * 0.022 * v + rng.expovariate(1 / 9)
        m["likes"] = int(likes)
        m["comments"] = int(likes * rng.uniform(0.01, 0.06) + rng.random() * 2)
        if media_type in ("reel", "video"):
            m["views"] = int(likes * rng.uniform(9, 30) + 50)
    elif platform == "tiktok":
        views = f * rng.uniform(0.3, 3) * v + rng.uniform(150, 2500) * v
        m["views"] = int(views)
        m["likes"] = int(views * rng.uniform(0.03, 0.12))
        m["comments"] = int(m["likes"] * rng.uniform(0.005, 0.03))
        m["shares"] = int(m["likes"] * rng.uniform(0.01, 0.08))
        m["saves"] = int(m["likes"] * rng.uniform(0.02, 0.1))
    elif platform == "x":
        imp = f * rng.uniform(0.05, 0.5) * v + rng.uniform(20, 300)
        m["views"] = int(imp)
        m["likes"] = int(imp * rng.uniform(0.004, 0.04))
        m["shares"] = int(m["likes"] * rng.uniform(0.05, 0.4))
        m["comments"] = int(m["likes"] * rng.uniform(0.02, 0.12) + rng.random() * 1.5)
    elif platform == "threads":
        m["likes"] = int(f * 0.015 * v + rng.expovariate(1 / 4))
        m["comments"] = int(m["likes"] * rng.uniform(0.03, 0.15))
        m["shares"] = int(m["likes"] * rng.uniform(0.0, 0.1))
    elif platform == "reddit":
        m["likes"] = int(rng.lognormvariate(2.4, 1.4) * viral)
        m["comments"] = int(m["likes"] * rng.uniform(0.1, 0.9) + rng.random() * 3)
    elif platform == "weibo":
        m["likes"] = int(f * 0.004 * v + rng.expovariate(1 / 3))
        m["comments"] = int(m["likes"] * rng.uniform(0.05, 0.4))
        m["shares"] = int(m["likes"] * rng.uniform(0.05, 0.6))
        m["views"] = int(f * rng.uniform(0.05, 0.8) * v + rng.uniform(10, 500)) if rng.random() < 0.7 else None
    elif platform == "xhs":
        m["likes"] = int(rng.lognormvariate(3.3, 1.6) * viral * rng.uniform(0.6, 1.4) + f * 0.01)
        m["saves"] = int(m["likes"] * rng.uniform(0.15, 0.9))
        m["comments"] = int(m["likes"] * rng.uniform(0.03, 0.18) + rng.random() * 2)
        m["shares"] = int(m["likes"] * rng.uniform(0.01, 0.08))
    elif platform == "naver_blog":
        m["likes"] = int(rng.lognormvariate(1.6, 1.0) * min(viral, 4))
        m["comments"] = int(rng.lognormvariate(1.0, 1.0) * min(viral, 4))
    elif platform == "naver_cafe":
        m["views"] = int(rng.lognormvariate(5.2, 0.9) * viral)
        m["comments"] = int(m["views"] * rng.uniform(0.005, 0.05) + rng.random() * 3)
        m["likes"] = int(m["comments"] * rng.uniform(0.2, 1.2))
    return m


def grow_metrics(rng, m, factor_range=(1.02, 1.6)):
    g = rng.uniform(*factor_range)
    out = {}
    for k, v in m.items():
        out[k] = None if v is None else int(v * g * rng.uniform(0.97, 1.05) + (1 if v and rng.random() < .5 else 0))
    return out


# ---------------------------------------------------------------------------
# Language detection simulation (vendor A) and sentiment model errors
# ---------------------------------------------------------------------------
def latin_ratio(text):
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 1.0
    return sum(1 for c in letters if c in string.ascii_letters) / len(letters)


def detect_lang(rng, true_lang, text):
    body = re.sub(r"[#@]\S+", "", text)
    if len(body.strip()) < 12:
        return rng.choice(["und", None, "und", "en"])
    lr = latin_ratio(body)
    if true_lang in ("ko", "ja", "zh-CN", "zh-TW", "zh-HK") and lr > 0.45 and rng.random() < 0.6:
        return "en"
    r = rng.random()
    if true_lang == "zh-CN":
        return "zh" if r < 0.85 else "zh-Hans"
    if true_lang == "zh-TW":
        return "zh" if r < 0.6 else ("zh-Hant" if r < 0.95 else "ja")
    if true_lang == "zh-HK":
        return "zh" if r < 0.55 else ("zh-Hant" if r < 0.85 else ("yue" if r < 0.95 else "ja"))
    if true_lang == "ja":
        kana = sum(1 for c in body if "぀" <= c <= "ヿ")
        if kana < 3:
            return "zh"
        return "ja"
    if true_lang == "da":
        return "da" if r < 0.72 else ("no" if r < 0.95 else "sv")
    if true_lang == "nl":
        return "nl" if r < 0.88 else ("af" if r < 0.95 else "de")
    if true_lang in ("it", "es") and r < 0.03:
        return "pt"
    if r < 0.015:
        return None
    return true_lang


SARCASM = ["love that for me", "great quality", "amazing quality", "thanks moncler", "10/10", "luxury they said",
           "che qualità", "grazie moncler", "bravo moncler", "super qualität", "na toll", "top qualité", "bravo à",
           "sooo worth it", "worth every penny lol", "classic", "/s"]
POS_SLANG_AS_NEG = ["미쳤", "미친", "대란", "품절", "やばい", "ヤバい", "insane", "sick", "obsessed", "绝了", "杀疯了", "哭了",
                    "killer", "dead", "crying", "破防", "疯了", "죽겠", "ㅠㅠ", "爆冷"]


def vendor_sentiment(rng, true_sent, text):
    t = text.lower()
    if true_sent == "neg" and any(s in t for s in SARCASM) and rng.random() < 0.8:
        return "positive", round(rng.uniform(0.55, 0.93), 2)
    if true_sent == "pos" and any(s in t for s in POS_SLANG_AS_NEG) and rng.random() < 0.6:
        return "negative", round(rng.uniform(0.51, 0.88), 2)
    lab = {"pos": "positive", "neg": "negative", "neu": "neutral", "mixed": "neutral"}[true_sent]
    if rng.random() < 0.14:
        lab = rng.choice(["positive", "negative", "neutral"])
    return lab, round(rng.uniform(0.5, 0.97), 2)


# ---------------------------------------------------------------------------
# IDs / URLs
# ---------------------------------------------------------------------------
B64 = string.ascii_letters + string.digits + "_-"


def rand_str(rng, n, alphabet=B64):
    return "".join(rng.choice(alphabet) for _ in range(n))


def make_url(rng, platform, handle, media_type, sub=None, title="", cafe=None, uid=None):
    if platform == "instagram":
        code = "D" + rand_str(rng, 10)
        return code, f"https://www.instagram.com/{'reel' if media_type in ('reel', 'video') else 'p'}/{code}/"
    if platform == "tiktok":
        pid = "75" + "".join(rng.choice(string.digits) for _ in range(17))
        return pid, f"https://www.tiktok.com/@{handle}/video/{pid}"
    if platform == "x":
        pid = "19" + "".join(rng.choice(string.digits) for _ in range(17))
        return pid, f"https://x.com/{handle}/status/{pid}"
    if platform == "threads":
        code = "D" + rand_str(rng, 10)
        return code, f"https://www.threads.net/@{handle}/post/{code}"
    if platform == "reddit":
        pid = rand_str(rng, 7, string.ascii_lowercase + string.digits)
        slug = re.sub(r"[^a-z0-9]+", "_", title.lower())[:50].strip("_") or "post"
        return "t3_" + pid, f"https://www.reddit.com/r/{sub}/comments/{pid}/{slug}/"
    if platform == "weibo":
        mid = rand_str(rng, 9, string.ascii_letters + string.digits)
        return mid, f"https://weibo.com/{uid}/{mid}"
    if platform == "xhs":
        nid = rand_str(rng, 24, "0123456789abcdef")
        return nid, f"https://www.xiaohongshu.com/explore/{nid}"
    if platform == "naver_blog":
        pid = "22" + "".join(rng.choice(string.digits) for _ in range(10))
        return pid, f"https://blog.naver.com/{handle}/{pid}"
    if platform == "naver_cafe":
        pid = str(rng.randint(100000, 2999999))
        return pid, f"https://cafe.naver.com/{cafe}/{pid}"
    raise ValueError(platform)


def zh_count(n):
    """Chinese platform count string: 1.2万 / 10万+ / plain."""
    if n is None:
        return ""
    if n >= 100000 and n < 1000000 and n % 3 == 0:
        return "10万+"
    if n >= 10000:
        return f"{n / 10000:.1f}万".replace(".0万", "万")
    return str(n)
