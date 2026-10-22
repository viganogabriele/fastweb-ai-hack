# -*- coding: utf-8 -*-
"""Build the social-listening dataset under generated/sources/external/social/.

Three fictional vendors with different schemas:
  pulsewire/   global listening vendor (IG, TikTok, X, Threads, Reddit) - monthly JSONL exports, schema change mid-Sep
  cn_yunting/  China crawler (Weibo + Xiaohongshu) - CSV with Chinese headers, Beijing-time strings, "1.2万" counts
  kr_socialeye/ Korean buzz monitor (Naver blog/cafe + Instagram KR) - CSV, KST "2026.10.02. 21:14" dates

Run:  .venv/bin/python generator/external/social/make_social.py
"""
import csv
import datetime as dt
import html
import json
import os
import re
import sys
from collections import Counter, defaultdict
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "generated", "sources", "external", "social")

import engine as E  # noqa: E402
from engine import R, UTC, PLACES, T_CUTOFF  # noqa: E402
import topics_ilvaro, topics_scenario, topics_context, topics_noise  # noqa: E402
from seeds import SEEDS  # noqa: E402

SIGNAL_SCALE = 0.6
KST = ZoneInfo("Asia/Seoul")
BJT = ZoneInfo("Asia/Shanghai")

# ---------------------------------------------------------------------------
# prices from the internal price list (read-only)
# ---------------------------------------------------------------------------
STYLE_CODES = {"J20931A00618": "ILVARO", "J20931A00012": "MAIRE", "J10911A00034": "MAYA", "G20921A00901": "POLARIS CAPE",
               "G20921A00903": "POLARIS BALACLAVA", "G20921A00902": "POLARIS OVERSIZED"}


def load_prices():
    p = {}
    with open(os.path.join(ROOT, "generated", "sources", "erp", "master_data", "price_list_FW26.csv")) as f:
        for row in csv.DictReader(f):
            st = STYLE_CODES.get(row["sku"][:12])
            if st:
                p[(st, row["currency"])] = float(row["retail_price"])
    return p


PRICES = load_prices()


def fmt_int(n, sep=","):
    return f"{int(round(n)):,}".replace(",", sep)


RESALE_RANGE = {"KR": (40, 69), "CN": (45, 90), "JP": (40, 85), "HK": (40, 100), "TW": (40, 100), "SG": (40, 100)}


def resale_pct(rng, t, place):
    """Resale premium over retail: peaks ~Oct 5-7, decays through Oct 21. KREAM ~3.8-4.6M KRW, Xianyu ~22-29k CNY."""
    d = (t - E.ts("2026-10-02")).total_seconds() / 86400
    if d <= 4:
        g = 0.35 + 0.65 * max(0.0, d) / 4
    else:
        g = 1 - (d - 4) * 0.05
    g = max(0.12, min(1.0, g)) * rng.uniform(0.8, 1.1)
    lo, hi = RESALE_RANGE.get(PLACES[place]["cc"], (40, 90))
    return int(round(max(lo, min(hi, lo + (hi - lo) * g))))


def make_slots(rng, lang, place, t):
    memo = {}

    def m(name, fn):
        def g():
            if name not in memo:
                memo[name] = fn()
            return memo[name]
        return g

    pr = lambda st, c: PRICES[(st, c)]  # noqa: E731
    pct = m("pct", lambda: resale_pct(rng, t, place))
    rs = lambda c, rnd: round(pr("ILVARO", c) * (1 + pct() / 100) / rnd) * rnd  # noqa: E731

    def resale_krw():
        v = rs("KRW", 10000)
        return rng.choice([fmt_int(v) + "원", f"{int(v / 10000)}만원", f"{int(v / 10000)}만"])

    def resale_cny():
        v = rs("CNY", 100)
        return rng.choice([f"¥{int(v)}", f"{int(v)}", f"{v / 10000:.2f}w".replace("0w", "w"), f"{fmt_int(v)}元"])

    def resale_jpy():
        v = rs("JPY", 1000)
        return rng.choice([f"¥{fmt_int(v)}", f"{fmt_int(v)}円", f"{v / 10000:.0f}万"])

    slots = dict(
        city=m("city", lambda: E.place_name(place, "city", lang, rng)),
        store=m("store", lambda: E.place_name(place, "store", lang, rng)),
        pct=pct,
        price_krw=m("pk", lambda: rng.choice(["2,720,000원", "272만원", "272만"])),
        price_cny=m("pc", lambda: rng.choice(["¥15200", "15200", "1.52w", "15,200元"])),
        price_jpy=m("pj", lambda: "313,000"),
        price_hkd=m("ph", lambda: rng.choice(["HK$14,800", "$14,800", "$14800"])),
        price_twd=m("pt", lambda: rng.choice(["63,000", "6萬3", "NT$63,000"])),
        price_twd_raw=m("ptr", lambda: "63,000"),
        price_sgd=m("ps", lambda: rng.choice(["S$2,500", "$2,500"])),
        resale_krw=m("rk", resale_krw),
        resale_cny=m("rc", resale_cny),
        resale_jpy=m("rj", resale_jpy),
        resale_hkd=m("rh", lambda: rng.choice(["HK$", "$"]) + fmt_int(rs("HKD", 500))),
        resale_twd=m("rt", lambda: rng.choice([fmt_int(rs("TWD", 1000)), f"{rs('TWD', 1000) / 10000:.0f}萬"])),
        resale_sgd=m("rsg", lambda: "S$" + fmt_int(rs("SGD", 50))),
        p_maire_krw=m("pmk", lambda: rng.choice(["248만원", "2,480,000원"])),
        p_cape_cny=m("pcc", lambda: rng.choice(["¥27700", "27700", "2.77w"])),
        p_bala_cny_raw=m("pbc", lambda: fmt_int(pr("POLARIS BALACLAVA", "CNY"))),
        p_maya_jpy_raw=m("pmj", lambda: fmt_int(pr("MAYA", "JPY"))),
        p_maya_jpy_new=m("pmjn", lambda: fmt_int(round(pr("MAYA", "JPY") * 1.08 / 1000) * 1000)),
        p_ilvaro_jpy_new=m("pijn", lambda: fmt_int(round(pr("ILVARO", "JPY") * 1.08 / 1000) * 1000)),
        size=m("size", lambda: rng.choices(["0", "1", "2", "00", "3"], [3, 4, 3, 1, 1])[0]),
        msize=m("msize", lambda: rng.choice(["2", "3", "4", "5"])),
        n=m("n", lambda: rng.randint(2, 9)),
        nn=m("nn", lambda: rng.randint(12, 140)),
        rhandle=m("rh2", lambda: rng.choice(E.NAMES["en"][0]) + rng.choice(["_", ".", ""]) + str(rng.randint(10, 999))),
        rstr=m("rstr", lambda: E.rand_str(rng, 6, "abcdefghijkmnpqrstuvwxyz23456789")),
        rnum=m("rnum", lambda: str(rng.randint(1000000, 9999999))),
        rwx=m("rwx", lambda: rng.choice(["mk", "lux", "yy", "vip", "hh"]) + str(rng.randint(1000, 99999)) + rng.choice(["a", "x", "", "_"])),
    )
    return slots


# ---------------------------------------------------------------------------
# platform helpers
# ---------------------------------------------------------------------------
FAMILY = {"instagram": "global", "tiktok": "global", "x": "global", "threads": "global", "reddit": "reddit", "weibo": "weibo",
          "xhs": "xhs", "naver_blog": "naver", "naver_cafe": "naver"}
HOME = {"ko": "KR_HOME", "ja": "JP_HOME", "zh-CN": "CN_HOME", "zh-HK": "HKG01", "zh-TW": "TPE01", "en": "US_HOME", "it": "MIL01",
        "fr": "PAR01", "de": "MUN01", "es": "MAD01", "nl": "AMS01", "da": "CPH01"}
GENERIC_TAGS = {"ko": ["몽클레어", "몽클레르", "moncler"], "ja": ["モンクレール", "moncler"], "en": ["moncler"], "it": ["moncler"],
                "fr": ["moncler"], "de": ["moncler"], "es": ["moncler"], "nl": ["moncler"], "da": ["moncler"], "zh-HK": ["moncler"],
                "zh-TW": ["moncler"], "zh-CN": ["盟可睐"]}
TAIL = {"ko": ["ㅠㅠ", "ㅋㅋ", "..", "!!", "🥲", "ㅎㅎ", "하..", "😭", "🤔"], "en": ["lol", "tbh", "!!", "😅", "ugh", "honestly", "fr", "😭"],
        "ja": ["笑", "…", "w", "😇", "！", "泣"], "zh-CN": ["😭", "哈哈哈", "～", "！！", "🥲", "绝了"], "zh-HK": ["😭", "🥲", "！", "哈哈"],
        "zh-TW": ["😭", "🥲", "！", "哈哈"], "it": ["😅", "!!", "boh", "🙃", "mah"], "fr": ["😅", "!!", "bref", "🙃"],
        "de": ["😅", "!!", "naja", "🙃"], "es": ["😅", "!!", "jaja", "🙃"], "nl": ["😅", "!!", "haha"], "da": ["😅", "!!", "haha"]}
BLOG_INTRO = ["안녕하세요 {nick}입니다 :) ", "안녕하세요~ ", "오랜만에 포스팅해요! ", "", "", "이웃님들 안녕하세요🙌 ", "오늘은 짧게 기록! "]
BLOG_OUTRO = [" 다음 포스팅에서 또 만나요~", " 도움이 되셨다면 공감 꾹 부탁드려요♡", "", "", " 궁금한 점은 댓글 주세요!", " 이상 후기였습니다."]
CAFE_PRE = ["", "", "질문 있어요~ ", "정보 공유합니다. ", "", "급해요ㅠ "]
CAFES = {
    "travel": [("유럽여행 정보공유 '유로트립'", "eurotripinfo", ["쇼핑 정보", "파리", "자유게시판", "질문 게시판"]),
               ("파리 한인 생활 커뮤니티", "parislife", ["사고팔고", "쇼핑", "질문"]),
               ("명품 직구·해외쇼핑 카페", "luxuryshopper", ["해외 매장 재고", "쇼핑 후기", "질문"])],
    "fashion": [("명품 정보 카페 '럭셔리라운지'", "luxlounge", ["브랜드 질문", "구매 후기", "자유게시판", "재고 정보"]),
                ("패션 피플 모여라", "fashionpeople", ["코디 질문", "쇼핑 후기"]),
                ("강남맘 생활정보", "gangnammom", ["쇼핑", "수다방"])],
    "fan": [("루미에르 팬카페 LUMINOUS", "lumiere0505", ["하은 게시판", "정보 공유", "잡담"]),
            ("아이돌 패션 정보방", "idolfashioninfo", ["착장 정보", "질문"])],
}
CAFES["mixed"] = CAFES["travel"] + CAFES["fashion"]
MEDIA = {"instagram": (["image", "carousel", "reel"], [.45, .35, .2]), "tiktok": (["video"], [1]), "x": (["text", "image", "video"], [.45, .45, .1]),
         "threads": (["text", "image"], [.6, .4]), "reddit": (["text", "image", "link"], [.65, .3, .05]), "weibo": (["image", "text", "video"], [.6, .3, .1]),
         "xhs": (["image", "video"], [.8, .2]), "naver_blog": (["image"], [1]), "naver_cafe": (["image", "text"], [.5, .5])}


def wchoice(rng, d):
    keys = list(d)
    return rng.choices(keys, weights=[d[k] for k in keys])[0]


def decorate(rng, plat, lang, text, tags, generic=True):
    pool = list(dict.fromkeys(list(tags) + (GENERIC_TAGS.get(lang, []) if generic else [])))
    if plat == "instagram":
        k = min(len(pool), rng.randint(2, 11))
        ht = rng.sample(pool, k) if pool else []
        if not ht:
            return text, []
        sep = rng.choice(["\n\n", " ", "\n.\n.\n.\n", "\n"])
        return text + sep + " ".join("#" + h.replace(" ", "") for h in ht), ht
    if plat == "tiktok":
        ht = rng.sample(pool, min(len(pool), rng.randint(2, 5))) + rng.sample(["fyp", "foryou", "viral", "foryoupage", "xyzbca"], rng.randint(1, 3))
        return text + " " + " ".join("#" + h for h in ht), ht
    if plat == "x":
        if pool and rng.random() < 0.35:
            ht = rng.sample(pool, min(len(pool), rng.randint(1, 2)))
            return text + " " + " ".join("#" + h for h in ht), ht
        return text, []
    if plat == "threads":
        if pool and rng.random() < 0.2:
            h = rng.choice(pool)
            return text + " #" + h, [h]
        return text, []
    if plat == "weibo":
        if pool and rng.random() < 0.65 and not text.startswith("#"):
            ht = rng.sample(pool, min(len(pool), rng.randint(1, 2)))
            return "".join("#%s#" % h for h in ht) + " " + text, ht
        return text, []
    if plat == "xhs":
        if pool:
            ht = rng.sample(pool, min(len(pool), rng.randint(2, 6)))
            return text + "\n" + " ".join("#%s[话题]#" % h for h in ht), ht
        return text, []
    return text, []


def hashtags_in(text):
    return list(dict.fromkeys(re.findall(r"#([^\s#\[\]]+)", text)))


# ---------------------------------------------------------------------------
# generation
# ---------------------------------------------------------------------------
def generate():
    pool = E.AuthorPool()
    posts = []
    all_specs = ([(s, True) for s in topics_ilvaro.SPECS + topics_scenario.SPECS + topics_context.SPECS] +
                 [(s, False) for s in topics_noise.SPECS])
    for spec, is_signal in all_specs:
        n = spec["n"]
        if is_signal and n > 6:
            n = max(5, int(round(n * SIGNAL_SCALE)))
        curve = E.curve_fn(spec["curve"])
        seen = set()
        lang = spec["lang"]
        for i in range(n):
            r = R(spec["key"], i)
            plat = wchoice(r, spec["plat"])
            place = wchoice(r, spec["places"]) if spec.get("places") else HOME[lang]
            tz = PLACES[place]["tz"]
            t = E.sample_time(r, curve, tz)
            kind = spec.get("kind", "user")
            kind = wchoice(r, kind) if isinstance(kind, dict) else kind
            fam = FAMILY[plat]
            if fam in ("weibo", "xhs") and kind == "fan" and r.random() < 0.5:
                kind = "user"
            author = pool.get(r, lang, kind, fam, n)
            slots = make_slots(r, lang, place, t)
            sent = spec.get("sent", "neu")
            for attempt in range(8):
                tpl = r.choice(spec["tpl"])
                if isinstance(tpl, tuple):
                    tpl, s2 = tpl
                else:
                    s2 = None
                text = E.expand(r, tpl, slots)
                if spec.get("dup_ok") or (plat, text) not in seen:
                    break
            if (plat, text) in seen and not spec.get("dup_ok"):
                text = text + " " + r.choice(TAIL.get(lang, TAIL["en"]))
            seen.add((plat, text))
            sent = s2 or sent
            title = None
            if plat in ("reddit", "xhs", "naver_blog", "naver_cafe"):
                if spec.get("titles") and r.random() < 0.85:
                    title = E.expand(r, r.choice(spec["titles"]), slots)
                else:
                    first = re.split(r"(?<=[.!?。！？\n])", text)[0].strip()
                    title = first[:38] + ("…" if len(first) > 38 else "")
            # Korean blog/cafe padding
            if plat == "naver_blog":
                intro = r.choice(BLOG_INTRO).replace("{nick}", (author["display"] or "").rstrip("♡★_0123456789")); text = intro + text + r.choice(BLOG_OUTRO)
            elif plat == "naver_cafe":
                text = r.choice(CAFE_PRE) + text
            doc_type = "post"
            if plat == "instagram" and r.random() < spec.get("comment_p", 0) * 2:
                doc_type = "comment"
            if doc_type == "post":
                generic = not (spec.get("label", "").startswith("ctx_") or spec.get("label") in ("noise_fan", "noise_travel") or spec.get("flags"))
                text_full, tags = decorate(r, plat, lang, text, spec.get("tags", ()), generic)
            else:
                text_full, tags = text, []
            mt_opts, mt_w = MEDIA[plat]
            media = r.choices(mt_opts, mt_w)[0] if doc_type == "post" else "text"
            mcount = {"carousel": r.randint(2, 10), "image": r.randint(1, 4) if plat in ("x", "weibo", "naver_cafe") else 1,
                      "text": 0, "video": 1, "reel": 1, "link": 0}[media]
            if plat in ("xhs",) and media == "image":
                mcount = r.randint(1, 9)
            if plat == "naver_blog":
                mcount = r.randint(3, 25)
            # engagement boost near the topic's peak
            f, a, b, fmax = curve
            boost = 0.5 + (f(t) / fmax) ** 0.5
            viral = spec.get("viral", 1.0) * boost
            metrics = E.gen_metrics(r, plat, author.get("followers"), viral, media)
            if doc_type == "comment":
                metrics = dict(likes=int(r.lognormvariate(1.5, 1.3)), comments=None, shares=None, views=None, saves=None)
            geo = None
            if plat in ("instagram", "threads", "x", "tiktok") and doc_type == "post" and PLACES[place]["geo"]:
                gp = spec.get("geo_p", 0.12)
                if plat == "x":
                    gp *= 0.3
                if plat == "tiktok":
                    gp *= 0.4
                if r.random() < gp:
                    g = r.choice(PLACES[place]["geo"])
                    geo = (g[0], g[1], g[2])
            cafe = None
            if plat == "naver_cafe":
                cname, curl, boards = r.choice(CAFES[spec.get("cafes") or "mixed"])
                cafe = dict(name=cname, url=curl, board=r.choice(boards))
            posts.append(dict(
                key=f"{spec['key']}#{i}", label=spec.get("label", spec["key"]), flags=tuple(spec.get("flags", ())),
                signal=is_signal, lang=lang, platform=plat, ts=t, tz=tz, place=place, author=author, kind=kind,
                text=text_full, title=title, tags=tags, media=media, media_count=mcount, metrics=metrics, geo=geo,
                sent=sent, doc_type=doc_type, sub=r.choice(spec["subs"]) if (plat == "reddit" and spec.get("subs")) else
                ("monclerheads" if plat == "reddit" else None), cafe=cafe, kw=spec.get("kw"), seed=False))
    # hand-written seeds
    for j, s in enumerate(SEEDS):
        r = R("seed", j)
        cafe = None
        if s["platform"] == "naver_cafe":
            cname, curl, boards = CAFES[s.get("cafe", "mixed")][0]
            cafe = dict(name=cname, url=curl, board=boards[1] if len(boards) > 1 else boards[0])
        tags = hashtags_in(s["text"])
        posts.append(dict(
            key=f"seed#{j}", label=s["label"], flags=tuple(s.get("flags", ())), signal=not s["label"].startswith("noise"),
            lang=s["lang"], platform=s["platform"], ts=E.ts(s["ts"]), tz=PLACES[s["place"]]["tz"], place=s["place"],
            author=dict(s["author"]), kind="seed", text=s["text"], title=s.get("title"), tags=tags, media=s.get("media", "image"),
            media_count=s.get("media_count", 1), metrics=dict(s["metrics"]), geo=s.get("geo"), sent=s["sent"], doc_type="post",
            sub=s.get("sub"), cafe=cafe, kw=None, seed=True))
    posts = [p for p in posts if E.T_START <= p["ts"] <= T_CUTOFF]
    posts.sort(key=lambda p: p["ts"])
    return posts


# ---------------------------------------------------------------------------
# routing
# ---------------------------------------------------------------------------
def route(posts):
    va, cn, kr = [], [], []
    for p in posts:
        r = R("route", p["key"])
        if p["platform"] in ("weibo", "xhs"):
            cn.append(p)
        elif p["platform"] in ("naver_blog", "naver_cafe"):
            kr.append(p)
        elif p["platform"] == "instagram" and p["lang"] == "ko":
            x = r.random()
            if x < 0.62:
                va.append(p)
            elif x < 0.80:
                kr.append(p)
            else:
                va.append(p)
                kr.append(p)
                p["cross_vendor"] = True
        else:
            va.append(p)
    return va, cn, kr


# ---------------------------------------------------------------------------
# Vendor A: Pulsewire
# ---------------------------------------------------------------------------
KW_LIST = ["moncler", "몽클", "モンクレ", "盟可睐", "蒙口", "ilvaro", "일바로", "maire", "마이어", "tib", "티브", "polaris", "genius",
           "arneb", "ambrine", "haeun", "하은", "lumiere", "루미에르", "ハウン", "夏恩", "maya", "마야"]
SCHEMA_SWITCH = E.ts("2026-09-15")


def z(t):
    return t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def pw_record(p, collected, metrics, r, variant=None):
    v2 = collected >= SCHEMA_SWITCH
    a = p["author"]
    plat = p["platform"]
    text = p["text"]
    if plat == "x":
        lim = 140 if p["lang"] in ("ko", "ja", "zh-CN", "zh-HK", "zh-TW") else 280
        if len(text) > lim:
            text = text[:lim - 1] + "…"
    lang = E.detect_lang(r, p["lang"], text)
    lab, score = E.vendor_sentiment(r, p["sent"], text)
    low = text.lower() + " " + (p.get("title") or "").lower()
    kws = [k for k in KW_LIST if k in low]
    if kws:
        match_type = "keyword"
    elif p["label"].startswith("ctx_") and (p["geo"] or R("geof", p["key"]).random() < 0.7):
        match_type = "geofence"
    else:
        match_type = "hashtag" if p["tags"] else "logo_detection"
    if not kws and match_type != "geofence":
        kws = ["moncler"]
    # text quirks
    if plat in ("instagram", "threads") and r.random() < 0.04:
        text = html.escape(text, quote=False).replace("'", "&#39;")
    if r.random() < 0.02:
        text = text.replace("\n", "\\n")
    if p["lang"] in ("de", "fr", "da", "es", "it") and collected < E.ts("2026-09-01") and r.random() < 0.08:
        try:
            text = text.encode("utf-8").decode("latin-1")
        except UnicodeError:
            pass
    pid, url = p["_pid"], p["_url"]
    published = z(p["ts"])
    created_utc = None
    if plat == "threads":
        published = p["ts"].astimezone(ZoneInfo(p["tz"])).isoformat()
    if plat == "reddit":
        created_utc = int(p["ts"].timestamp())
        published = None
    if variant == "naive":
        published = p["ts"].strftime("%Y-%m-%d %H:%M:%S") if published else None
    src = plat
    if plat == "x" and not v2:
        src = "twitter"
    geo = None
    if p["geo"]:
        name, lat, lon = p["geo"]
        city = E.PLACES[p["place"]]["city"].get("en", [None])[0]
        cc = E.PLACES[p["place"]]["cc"]
        if v2:
            geo = dict(place_name=name, city=city, country_code=cc, lat=round(lat, 4), lon=round(lon, 4))
        else:
            geo = dict(name=name, city=city, country=cc, coordinates=[round(lat, 4), round(lon, 4)])
    followers = a.get("followers") if p["doc_type"] == "post" else None
    handle = a["handle"]
    rec = {}
    rec["doc_id"] = p["_docid"]
    rec["doc_type"] = p["doc_type"]
    rec["source"] = src
    rec["post_id"] = pid
    rec["url"] = url
    rec["published_at"] = published
    if created_utc is not None:
        rec["created_utc"] = created_utc
    rec["collected_at"] = z(collected)
    loc = p.get("_bio_loc")
    if v2:
        rec["author"] = dict(handle=handle, display_name=a.get("display"), follower_count=followers, verified=a.get("verified", False))
        if loc:
            rec["author"]["location"] = loc
        rec["language"] = lang
    else:
        rec["author"] = dict(handle="@" + handle if plat != "reddit" else "u/" + handle, name=a.get("display"), followers=followers,
                             verified=a.get("verified", False))
        if loc:
            rec["author"]["location"] = loc
        rec["lang"] = lang
    if plat == "reddit":
        rec["subreddit"] = "r/" + (p["sub"] or "monclerheads")
        rec["title"] = p["title"]
    rec["text"] = text
    rec["hashtags"] = [h for h in hashtags_in(text)] if p["doc_type"] == "post" else []
    if p["doc_type"] == "comment":
        rec["parent_url"] = p["_parent"]
    m = metrics
    if v2:
        rec["media"] = dict(type=p["media"], count=p["media_count"])
        eng = sum(v or 0 for v in (m["likes"], m["comments"], m["shares"]))
        er = round(eng / followers, 4) if followers else None
        rec["metrics"] = dict(like_count=m["likes"], comment_count=m["comments"], share_count=m["shares"], view_count=m["views"],
                              save_count=m["saves"], engagement_rate=er)
    else:
        rec["media_type"] = p["media"]
        rec["metrics"] = dict(likes=m["likes"], comments=m["comments"], shares=m["shares"], views=m["views"])
    rec["geo"] = geo
    if v2:
        rec["sentiment"] = dict(label={"positive": "pos", "negative": "neg", "neutral": "neu"}[lab], score=score)
    else:
        rec["sentiment"] = lab
        rec["sentiment_score"] = score
    rec["keywords_matched"] = kws
    rec["match_type"] = match_type
    rec["project"] = "MCL-GLOBAL-SOCIAL" if not v2 else "mcl_global_social"
    if v2:
        rec["schema_version"] = "2.0"
    return rec


BIO_LOC = {"ko": ["Seoul 🇰🇷", "서울", "Busan", "KR", "Seoul | Paris"], "ja": ["Tokyo", "東京", "大阪", "JP"], "en": ["NYC", "London", "LA", "Singapore", "Toronto", "Sydney", "Dubai", "she/her"],
           "it": ["Milano", "Roma", "Milano | Paris", "Italia 🇮🇹"], "fr": ["Paris", "Paris 🇫🇷", "Genève"], "de": ["München", "Berlin", "Zürich"],
           "es": ["Madrid"], "nl": ["Amsterdam"], "da": ["København", "CPH"], "zh-HK": ["Hong Kong", "HK 🇭🇰", "香港"], "zh-TW": ["Taipei", "台北"], "zh-CN": ["Shanghai"]}


def write_pulsewire(posts):
    d = os.path.join(OUT, "pulsewire")
    os.makedirs(d, exist_ok=True)
    # stable ids
    for p in posts:
        r = R("pwid", p["key"])
        p["_docid"] = "pw-" + E.rand_str(r, 16, "0123456789abcdef")
        p["_pid"], p["_url"] = E.make_url(r, p["platform"], p["author"]["handle"], p["media"], sub=p.get("sub") or "monclerheads",
                                          title=p.get("title") or "")
        if p["doc_type"] == "comment":
            p["_parent"] = "https://www.instagram.com/p/D" + E.rand_str(r, 10) + "/"
            p["_url"] = p["_parent"] + "c/" + "".join(r.choice("0123456789") for _ in range(17)) + "/"
            p["_pid"] = p["_url"].rstrip("/").split("/")[-1]
        if p["platform"] != "reddit" and r.random() < 0.18:
            p["_bio_loc"] = r.choice(BIO_LOC.get(p["lang"], BIO_LOC["en"]))
    months = {"2026-08": [], "2026-09": [], "2026-10": []}
    counts = Counter()
    for p in posts:
        r = R("pwcol", p["key"])
        lag = dt.timedelta(hours=min(70, r.lognormvariate(2.0, 0.9)))
        col = min(p["ts"] + lag, T_CUTOFF - dt.timedelta(minutes=r.randint(3, 50)))
        if col < p["ts"]:
            col = p["ts"] + dt.timedelta(minutes=2)
        mkey = p["ts"].strftime("%Y-%m")
        months[mkey].append((col, pw_record(p, col, p["metrics"], r)))
        counts["base"] += 1
        # month-boundary re-export (overlap)
        if (p["ts"] >= E.ts("2026-08-30") and p["ts"] < E.ts("2026-09-01")) or (p["ts"] >= E.ts("2026-09-28") and p["ts"] < E.ts("2026-10-01")):
            nxt = "2026-09" if mkey == "2026-08" else "2026-10"
            col2 = E.ts(nxt + "-01") + dt.timedelta(hours=r.uniform(1, 30))
            col2 = max(col2, col + dt.timedelta(hours=2))
            months[nxt].append((col2, pw_record(p, col2, E.grow_metrics(r, p["metrics"], (1.0, 1.25)), r)))
            counts["overlap_dup"] += 1
    # re-crawl duplicates inside the October file for the hottest early-October posts
    hot = [p for p in posts if E.ts("2026-10-01T16:00") <= p["ts"] < E.ts("2026-10-06") and p["metrics"].get("likes")]
    hot.sort(key=lambda p: -(p["metrics"]["likes"] or 0))
    for p in hot[:45]:
        r = R("pwre", p["key"])
        col = p["ts"] + dt.timedelta(hours=r.uniform(30, 120))
        months["2026-10"].append((col, pw_record(p, col, E.grow_metrics(r, p["metrics"], (1.1, 2.2)), r,
                                                 variant="naive" if r.random() < 0.5 else None)))
        counts["recrawl_dup"] += 1
    rows_written = {}
    for mkey, rows in months.items():
        rows.sort(key=lambda x: x[0])
        fn = os.path.join(d, f"listening_pulsewire_export_{mkey}.jsonl")
        r = R("pwbroken", mkey)
        broken = {"2026-08": 0, "2026-09": 1, "2026-10": 2}[mkey]
        broken_idx = set(r.sample(range(len(rows)), broken))
        with open(fn, "w", encoding="utf-8") as f:
            for i, (_, rec) in enumerate(rows):
                line = json.dumps(rec, ensure_ascii=False)
                if i in broken_idx:
                    line = line[: int(len(line) * r.uniform(0.4, 0.8))]
                f.write(line + "\n")
        rows_written[os.path.relpath(fn, OUT)] = len(rows)
    with open(os.path.join(d, "README_pulsewire.txt"), "w", encoding="utf-8") as f:
        f.write(PW_README)
    return rows_written, counts


PW_README = """PULSEWIRE Social Listening - Data Export
Project: MCL-GLOBAL-SOCIAL      Delivery: monthly JSONL (one document per line, UTF-8)
Doc version 1.3 (2026-06-02)

Coverage: Instagram (posts + comments), TikTok, Twitter, Threads, Reddit.
Query: brand + product keywords, brand hashtags, logo detection on images,
       geofences around monitored retail addresses.
Timestamps are UTC (ISO 8601, "Z").

FIELDS
  doc_id            Pulsewire unique document id
  doc_type          post | comment
  source            instagram | tiktok | twitter | threads | reddit
  post_id, url      native id / permalink
  published_at      publication time, UTC
  collected_at      crawl time, UTC
  author.handle     "@handle" (reddit: "u/name")
  author.name       display name
  author.followers  follower count at crawl time (null for comments / reddit)
  author.verified   bool
  lang              ISO 639-1 detected language (auto)
  title             reddit only
  text              full text
  hashtags          list, without '#'
  media_type        image | carousel | video | reel | text | link
  metrics.likes / metrics.comments / metrics.shares / metrics.views
                    snapshot at collected_at; null = not exposed by platform
  geo               place tag if present, else null
                    {name, city, country, coordinates:[lat, lon]}
  sentiment         positive | negative | neutral (Pulsewire NLP v4)
  sentiment_score   0-1 confidence
  keywords_matched  list of query terms found
  match_type        keyword | hashtag | logo_detection | geofence
  subreddit         reddit only
  parent_url        comments only

NOTES
  - Monthly files may contain documents re-collected in the following export; use doc_id + latest collected_at.
  - Metrics are snapshots and keep growing after publication.
  - Sentiment is automatic and not validated for sarcasm or slang.
  - Contact: support@pulsewire.example
"""


# ---------------------------------------------------------------------------
# Vendor B: China crawler (Weibo + XHS)
# ---------------------------------------------------------------------------
PROV = {"SHA01": [("上海", 8), ("江苏", 1.5), ("浙江", 1.5)], "BJS01": [("北京", 8), ("河北", 1), ("天津", 1)], "CDU01": [("四川", 8), ("重庆", 2)],
        "CN_HOME": [("广东", 4), ("上海", 4), ("北京", 3), ("浙江", 3), ("江苏", 3), ("四川", 2), ("湖北", 1.5), ("山东", 1.5), ("福建", 1), ("辽宁", 1), ("陕西", 1), ("河南", 1), ("海外", 0.5)],
        "MIL01": [("意大利", 6), ("上海", 1), ("四川", 1)], "PAR01": [("法国", 6), ("上海", 1)], "PAR02": [("法国", 6), ("北京", 1)], "LON02": [("英国", 6)],
        "TYO01": [("日本", 6), ("上海", 1)], "HKG01": [("香港", 1)]}
CN_COLS = ["序号", "平台", "帖子ID", "链接", "标题", "正文", "发布时间", "作者昵称", "作者ID", "粉丝数", "认证类型", "IP属地", "点赞数", "评论数",
           "转发数", "收藏数", "阅读数", "内容类型", "话题", "命中关键词", "情感倾向", "抓取时间"]
CN_KW = ["盟可睐", "蒙口", "moncler", "ilvaro", "尹夏恩", "夏恩", "maire", "bady", "polaris", "genius", "双十一", "maya", "羽绒服"]


def cn_time_str(r, plat, pub_l, crawl_l):
    delta = crawl_l - pub_l
    if delta < dt.timedelta(hours=24) and r.random() < 0.16:
        if delta < dt.timedelta(hours=1):
            return f"{max(1, int(delta.total_seconds() // 60))}分钟前"
        if pub_l.date() == crawl_l.date() or r.random() < 0.5:
            return f"{int(delta.total_seconds() // 3600)}小时前"
        return "昨天 " + pub_l.strftime("%H:%M")
    x = r.random()
    if plat == "weibo" and x < 0.1:
        return f"{pub_l.month}月{pub_l.day}日 {pub_l:%H:%M}"
    if plat == "xhs" and x < 0.1:
        return pub_l.strftime("%m-%d")
    if plat == "xhs" and x < 0.14:
        return "编辑于 " + pub_l.strftime("%m-%d")
    return pub_l.strftime("%Y-%m-%d %H:%M")


def cn_sent(r, s, text):
    lab = {"pos": "正面", "neg": "负面", "neu": "中性", "mixed": "中性"}[s]
    if any(k in text for k in ("哭", "疯", "救命", "离谱")) and r.random() < 0.5:
        lab = "负面"
    elif r.random() < 0.2:
        lab = r.choice(["正面", "负面", "中性"])
    return lab


def write_cn(posts):
    d = os.path.join(OUT, "cn_yunting")
    os.makedirs(d, exist_ok=True)
    rows_b1, rows_b2 = [], []
    reposts = []
    # weibo reposts of the most liked weibo posts (quasi-duplicates)
    wb = sorted([p for p in posts if p["platform"] == "weibo" and p["signal"]], key=lambda p: -(p["metrics"]["likes"] or 0))[:30]
    pool = E.AuthorPool()
    for k, p in enumerate(wb):
        r = R("wbrepost", p["key"])
        for j in range(r.randint(1, 3)):
            a = pool.get(r, "zh-CN", "user", "weibo", 60)
            reason = r.choice(["转发微博", "啊啊啊啊好看", "求同款", "夏恩宝贝🩷", "买不到哭了", "马住", "冲", "//", "同问哪里有货", "已经断货了吧"])
            q = dict(p)
            q.update(key=p["key"] + f"/rp{j}", author=a, ts=p["ts"] + dt.timedelta(minutes=r.randint(5, 2000)),
                     text=f"{reason}//@{p['author']['handle']}: {p['text']}", metrics=E.gen_metrics(r, "weibo", a["followers"], 0.6, "text"),
                     media="text", repost=True)
            if q["ts"] <= T_CUTOFF:
                reposts.append(q)
    allp = sorted(posts + reposts, key=lambda p: p["ts"])
    b1_end = dt.datetime(2026, 9, 15, 23, 59, tzinfo=BJT)
    b2_start = dt.datetime(2026, 9, 10, 0, 0, tzinfo=BJT)
    pid_cache = {}
    for p in allp:
        r = R("cn", p["key"])
        a = p["author"]
        uid = a.get("uid") or str(r.randint(1000000000, 7999999999))
        if p["key"] not in pid_cache:
            pid_cache[p["key"]] = E.make_url(r, p["platform"], a["handle"], p["media"], uid=uid)
        pid, url = pid_cache[p["key"]]
        pub_l = p["ts"].astimezone(BJT)
        prov_opts = PROV.get(p["place"], PROV["CN_HOME"])
        if p["kind"] == "daigou":
            prov_opts = [("法国", 2), ("意大利", 2), ("香港", 1), ("日本", 1), ("上海", 1)]
        ip = r.choices([x for x, _ in prov_opts], [w for _, w in prov_opts])[0]
        verified = {True: r.choice(["微博认证", "蓝V", "黄V", "金V"]) if p["platform"] == "weibo" else "专业号", False: ""}[bool(a.get("verified"))]
        topics = " ".join(f"#{h}#" for h in p["tags"]) if p["platform"] == "weibo" else " ".join(p["tags"])
        low = (p["text"] + (p["title"] or "")).lower()
        kw = "|".join(k for k in CN_KW if k in low) or "盟可睐"
        text = p["text"]
        ctype = ("转发" if p.get("repost") else "原创") if p["platform"] == "weibo" else ("视频" if p["media"] == "video" else "图文")

        def row(crawl_l, metrics, batch):
            m = metrics
            return {"平台": "微博" if p["platform"] == "weibo" else "小红书", "帖子ID": pid, "链接": url,
                    "标题": (p["title"] or "") if p["platform"] == "xhs" else "", "正文": text,
                    "发布时间": cn_time_str(r, p["platform"], pub_l, crawl_l), "作者昵称": a["handle"], "作者ID": uid,
                    "粉丝数": E.zh_count(a.get("followers")), "认证类型": verified, "IP属地": ip,
                    "点赞数": E.zh_count(m["likes"]), "评论数": E.zh_count(m["comments"]),
                    "转发数": E.zh_count(m["shares"]) if p["platform"] == "weibo" else "",
                    "收藏数": E.zh_count(m["saves"]) if p["platform"] == "xhs" else "",
                    "阅读数": E.zh_count(m["views"]) if p["platform"] == "weibo" else "",
                    "内容类型": ctype, "话题": topics, "命中关键词": kw, "情感倾向": cn_sent(r, p["sent"], text),
                    "抓取时间": crawl_l.strftime("%Y-%m-%d %H:%M:%S")}

        def crawl_after(t_l, shift_days=0):
            c = (t_l + dt.timedelta(days=shift_days)).replace(hour=6, minute=r.randint(0, 59), second=r.randint(0, 59))
            if c <= t_l:
                c += dt.timedelta(days=1)
            cutoff_l = T_CUTOFF.astimezone(BJT) - dt.timedelta(minutes=r.randint(5, 40))
            if c > cutoff_l:
                c = max(t_l + dt.timedelta(minutes=r.randint(10, 120)), cutoff_l) if t_l < cutoff_l else t_l + dt.timedelta(minutes=5)
            return c
        if pub_l <= b1_end:
            rows_b1.append(row(crawl_after(pub_l), p["metrics"], 1))
        if pub_l >= b2_start:
            if pub_l <= b1_end:
                c2 = dt.datetime(2026, 9, 16, 6, 0, tzinfo=BJT) + dt.timedelta(days=r.randint(0, 2), minutes=r.randint(0, 59))
                rows_b2.append(row(c2, E.grow_metrics(r, p["metrics"], (1.0, 1.4)), 2))
            else:
                rows_b2.append(row(crawl_after(pub_l), p["metrics"], 2))
    out = {}
    for name, rows in (("cn_yunting_weibo_xhs_20260801_20260915.csv", rows_b1), ("cn_yunting_weibo_xhs_20260910_20261022.csv", rows_b2)):
        fn = os.path.join(d, name)
        with open(fn, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=CN_COLS)
            w.writeheader()
            for i, rw in enumerate(rows, 1):
                rw["序号"] = i
                w.writerow(rw)
        out[os.path.relpath(fn, OUT)] = len(rows)
    with open(os.path.join(d, "README_字段说明.txt"), "w", encoding="utf-8") as f:
        f.write(CN_README)
    return out, len(reposts)


CN_README = """云听舆情 · 社媒数据导出说明 (v2.3)
客户: MCL 品牌监测项目        渠道: 新浪微博、小红书
导出格式: CSV (UTF-8 BOM), 每批次一个文件

字段说明
  序号        行号(每个文件独立编号)
  平台        微博 / 小红书
  帖子ID      平台原生ID (微博mid / 小红书笔记ID)
  链接        帖子链接
  标题        小红书笔记标题 (微博为空)
  正文        帖子全文, 微博转发包含 //@原作者
  发布时间    北京时间, 格式 YYYY-MM-DD HH:MM:SS
  作者昵称 / 作者ID
  粉丝数      抓取时粉丝数
  认证类型    微博认证 / 蓝V / 黄V / 金V / 专业号 / 空
  IP属地      平台显示的IP属地(省份或国家/地区)
  点赞数 评论数 转发数 收藏数 阅读数
              抓取时的互动数据(平台不显示的字段为空)
  内容类型    微博: 原创/转发   小红书: 图文/视频
  话题        帖子带的话题
  命中关键词  命中的监测关键词, 多个用 | 分隔
  情感倾向    正面 / 中性 / 负面 (系统自动判断)
  抓取时间    北京时间

备注
  1. 各批次之间时间范围可能有重叠, 同一帖子以最新抓取时间的数据为准。
  2. 互动数为抓取时快照。
"""


# ---------------------------------------------------------------------------
# Vendor C: Korea (Naver blog / cafe + Instagram KR)
# ---------------------------------------------------------------------------
KR_COLS = ["no", "channel", "cafe_name", "board_name", "blog_name", "title", "body_snippet", "writer_nick", "insta_id", "follower_cnt",
           "post_date", "view_cnt", "comment_cnt", "like_cnt", "url", "search_kw", "crawl_dt"]
KR_HL = ["몽클레어", "몽클레르", "몽클", "일바로", "마이어", "윤하은", "하은", "노스피크", "티브", "마야", "아르네브", "청담"]


def kr_highlight(s, kw):
    terms = [t for t in kw.split() if t in s] or [t for t in KR_HL if t in s][:1]
    for t in terms[:2]:
        s = s.replace(t, f"<b>{t}</b>", 1)
    return s


def kr_entities(r, s):
    if r.random() < 0.5:
        s = s.replace('"', "&quot;").replace("&quot;&quot;", "&quot;")
    return s.replace("&", "&amp;").replace("&amp;quot;", "&quot;") if r.random() < 0.15 else s


def write_kr(posts):
    d = os.path.join(OUT, "kr_socialeye")
    os.makedirs(d, exist_ok=True)
    rows = []
    dups = 0
    for p in posts:
        r = R("kr", p["key"])
        a = p["author"]
        pub_k = p["ts"].astimezone(KST)
        crawl = pub_k.replace(hour=9, minute=r.randint(0, 40), second=r.randint(0, 59))
        if crawl <= pub_k:
            crawl += dt.timedelta(days=1)
        if p["platform"] != "instagram" and r.random() < 0.35:
            crawl += dt.timedelta(days=r.randint(1, 6))
        cutoff_k = T_CUTOFF.astimezone(KST) - dt.timedelta(minutes=r.randint(5, 30))
        if crawl > cutoff_k:
            crawl = cutoff_k if cutoff_k > pub_k else pub_k + dt.timedelta(minutes=10)
        kws = p.get("kw") or ["몽클레어", "몽클레르"]
        kw = r.choice(kws)
        plat = p["platform"]
        if plat == "instagram":
            if p.get("cross_vendor"):
                url = p["_url"]
            else:
                url = E.make_url(r, "instagram", a["handle"], p["media"])[1]
            row = dict(channel="인스타그램", cafe_name="", board_name="", blog_name="", title="", body_snippet=p["text"], writer_nick=a.get("display") or "",
                       insta_id=a["handle"], follower_cnt=a.get("followers") or "",
                       post_date=p["ts"].astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z"), view_cnt="",
                       comment_cnt=p["metrics"]["comments"] if p["metrics"]["comments"] is not None else "", like_cnt=p["metrics"]["likes"] or 0,
                       url=url, search_kw=kw, crawl_dt=crawl.strftime("%Y-%m-%d %H:%M"))
            rows.append((crawl, row))
            continue
        nick = a.get("display") or a["handle"]
        if plat == "naver_blog":
            pid, url = E.make_url(r, "naver_blog", a["handle"], "image")
        else:
            pid, url = E.make_url(r, "naver_cafe", a["handle"], "image", cafe=p["cafe"]["url"])
        delta = crawl - pub_k
        if delta < dt.timedelta(hours=24) and r.random() < 0.38:
            h = int(delta.total_seconds() // 3600)
            pdate = f"{h}시간 전" if h >= 1 else f"{max(1, int(delta.total_seconds() // 60))}분 전"
        elif plat == "naver_cafe" and delta > dt.timedelta(days=2) and r.random() < 0.6:
            pdate = pub_k.strftime("%Y.%m.%d.")
        elif r.random() < 0.08:
            pdate = f"{pub_k.year}. {pub_k.month}. {pub_k.day}. {pub_k:%H:%M}"
        else:
            pdate = pub_k.strftime("%Y.%m.%d. %H:%M")
        body = re.sub(r"\s+", " ", p["text"]).strip()
        cut = r.randint(70, 140)
        snippet = body if len(body) <= cut else body[:cut].rstrip() + "..."
        title = p["title"] or body[:30]
        m = p["metrics"]
        row = dict(channel="블로그" if plat == "naver_blog" else "카페",
                   cafe_name=p["cafe"]["name"] if plat == "naver_cafe" else "", board_name=p["cafe"]["board"] if plat == "naver_cafe" else "",
                   blog_name=(nick + r.choice(["의 일상", "의 여행일기", "의 쇼핑기록", " 블로그", "의 하루", "'s log"])) if plat == "naver_blog" else "",
                   title=kr_entities(r, kr_highlight(title, kw)), body_snippet=kr_entities(r, kr_highlight(snippet, kw)),
                   writer_nick=nick if plat == "naver_cafe" or r.random() < 0.5 else "", insta_id="", follower_cnt="", post_date=pdate,
                   view_cnt=fmt_int(m["views"]) if plat == "naver_cafe" and m["views"] is not None else "",
                   comment_cnt=m["comments"] if m["comments"] is not None else "", like_cnt=m["likes"] if m["likes"] is not None else "",
                   url=url, search_kw=kw, crawl_dt=crawl.strftime("%Y-%m-%d %H:%M"))
        rows.append((crawl, row))
        # same post captured under a second keyword
        if len(kws) > 1 and r.random() < 0.09:
            row2 = dict(row)
            row2["search_kw"] = r.choice([k for k in kws if k != kw])
            c2 = crawl + dt.timedelta(days=r.randint(0, 2), minutes=r.randint(1, 50))
            if c2 <= cutoff_k:
                row2["crawl_dt"] = c2.strftime("%Y-%m-%d %H:%M")
                if plat == "naver_cafe" and m["views"] is not None:
                    row2["view_cnt"] = fmt_int(int(m["views"] * r.uniform(1.0, 1.5)))
                rows.append((c2, row2))
                dups += 1
    rows.sort(key=lambda x: x[0])
    fn = os.path.join(d, "kr_socialeye_buzz_20260801_20261022.csv")
    with open(fn, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=KR_COLS)
        w.writeheader()
        for i, (_, row) in enumerate(rows, 1):
            row["no"] = i
            w.writerow(row)
    with open(os.path.join(d, "README_kr_socialeye.txt"), "w", encoding="utf-8") as f:
        f.write(KR_README)
    return {os.path.relpath(fn, OUT): len(rows)}, dups


KR_README = """SocialEye 소셜 버즈 모니터링 - 원천 데이터 (Raw)
고객사: MCL 코리아            수집 채널: 네이버 블로그, 네이버 카페, 인스타그램
파일: CSV (UTF-8, Excel에서 열 때 BOM 포함)

컬럼 설명
  no             일련번호
  channel        블로그 / 카페 / 인스타그램
  cafe_name      카페명 (카페만)
  board_name     게시판명 (카페만)
  blog_name      블로그명 (블로그만)
  title          게시글 제목 (검색 키워드 <b> 강조 포함)
  body_snippet   본문 요약 (검색 API 제공 요약문)
  writer_nick    작성자 닉네임 (비공개 시 공란)
  post_date      작성일시 (KST) - YYYY.MM.DD. HH:MM
  view_cnt       조회수 (카페만)
  comment_cnt    댓글수
  like_cnt       공감수 / 좋아요수
  url            원문 URL
  search_kw      수집 키워드
  crawl_dt       수집일시 (KST)

※ 동일 게시글이 여러 키워드로 수집될 수 있음.
※ 문의: ops@socialeye.example
"""


# ---------------------------------------------------------------------------
def main():
    posts = generate()
    va, cn, kr = route(posts)
    pw_rows, pw_counts = write_pulsewire(va)
    cn_rows, n_reposts = write_cn(cn)
    kr_rows, kr_dups = write_kr(kr)
    # ---- summary (stdout only)
    print("canonical posts:", len(posts), " signal:", sum(p["signal"] for p in posts), " noise:", sum(not p["signal"] for p in posts))
    print("vendor A posts:", len(va), dict(pw_counts))
    print("CN posts:", len(cn), "weibo reposts:", n_reposts)
    print("KR posts:", len(kr), "keyword dups:", kr_dups, "cross-vendor IG:", sum(1 for p in kr if p.get("cross_vendor")))
    for k, v in {**pw_rows, **cn_rows, **kr_rows}.items():
        print(f"  {k}: {v} rows")
    lab = Counter(p["label"] for p in posts)
    for k, v in sorted(lab.items()):
        print(f"    {k:32s} {v}")
    byday = Counter(p["ts"].strftime("%m-%d") for p in posts)
    print(" ".join(f"{d}:{byday[d]}" for d in sorted(byday)))
    print("platforms:", Counter(p["platform"] for p in posts))
    print("langs:", Counter(p["lang"] for p in posts))


if __name__ == "__main__":
    main()
