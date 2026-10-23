"""Build the external news feed (aggregator-style dump) from the content_* modules.

Output: generated/sources/external/news/
  feed_index.json          aggregator index (mixed date formats, as delivered by each source)
  rss_luxury_wire.xml      RSS 2.0 export of one wire
  articles/YYYY-MM/...     articles stored by month (txt / html / json)
  by_source/<source>/...   some sources are stored by source (wire feeds, Korean press)
Run: .venv/bin/python generator/external/news/build.py
"""
import datetime as dt
import hashlib
import html
import json
import re
import shutil
import sys
import unicodedata
from email.utils import format_datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from content_it import ARTICLES as A_IT  # noqa: E402
from content_eu import ARTICLES as A_EU  # noqa: E402
from content_en import ARTICLES as A_EN  # noqa: E402
from content_asia import ARTICLES as A_AS  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "generated" / "sources" / "external" / "news"

FR_MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
             "novembre", "décembre"]
IT_MONTHS = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre",
             "ottobre", "novembre", "dicembre"]
IT_MON3 = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]
EN_MON = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


def ampm(d, lower=False, dots=False):
    h = d.hour % 12 or 12
    suf = "AM" if d.hour < 12 else "PM"
    if lower:
        suf = suf.lower()
    if dots:
        suf = "a.m." if d.hour < 12 else "p.m."
    return f"{h}:{d.minute:02d} {suf}"


# source key -> name, lang, domain, published formatter (receives aware datetime in the source's own tz)
SOURCES = {
    "qdm": ("Il Quotidiano della Moda", "it", "www.quotidianodellamoda.example",
            lambda d: d.strftime("%d/%m/%Y %H:%M")),
    "gazeco": ("Gazzetta Economica", "it", "www.gazzettaeconomica.example", lambda d: d.isoformat()),
    "cdr": ("Cronache di Roma", "it", "cronachediroma.example", lambda d: d.strftime("%Y-%m-%d")),
    "mcn": ("MilanoCity News", "it", "www.milanocitynews.example",
            lambda d: f"{d.day} {IT_MON3[d.month-1]} {d.year} {d:%H:%M}"),
    "gzl": ("Il Gazzettino Lagunare", "it", "www.gazzettinolagunare.example",
            lambda d: f"{d.day} {IT_MONTHS[d.month-1]} {d.year}, ore {d:%H:%M}"),
    "s24": ("Sportivo 24", "it", "sportivo24.example", lambda d: d.strftime("%d/%m/%Y")),
    "jdl": ("Le Journal du Luxe", "fr", "www.journalduluxe.example",
            lambda d: f"{d.day} {FR_MONTHS[d.month-1]} {d.year} à {d.hour}h{d.minute:02d}"),
    "pm": ("Paris Matin", "fr", "www.parismatin.example", lambda d: d.strftime("%d/%m/%Y %H:%M")),
    "obl": ("El Observador del Lujo", "es", "observadordellujo.example",
            lambda d: d.strftime("%d/%m/%Y - %H:%M ") + "CEST"),
    "wk": ("Wirtschaftskurier", "de", "www.wirtschaftskurier.example",
           lambda d: d.strftime("%d.%m.%Y, %H:%M Uhr")),
    "zap": ("Zürcher Abendpost", "de", "www.zuercher-abendpost.example", lambda d: d.strftime("%d.%m.%Y %H:%M")),
    "lw": ("Luxury Wire", "en", "luxurywire.example",
           lambda d: format_datetime(d.astimezone(dt.timezone.utc), usegmt=True)),
    "apn": ("APN Asia Pacific Newswire", "en", "apn-newswire.example",
            lambda d: d.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")),
    "raw": ("Retail Asia Wire", "en", "www.retailasiawire.example", lambda d: format_datetime(d)),
    "sth": ("The Straits Herald", "en", "www.straitsherald.example",
            lambda d: f"{d:%b} {d.day}, {d.year}, {ampm(d, lower=True)} SGT"),
    "ken": ("K-Ent Now", "en", "kentnow.example", lambda d: d.isoformat()),
    "drop": ("Drop Culture", "en", "dropculture.example", lambda d: str(int(d.timestamp()))),
    "mtw": ("Marketing Trade Weekly", "en", "www.mktradeweekly.example", lambda d: f"{d:%b} {d.day}, {d.year}"),
    "tri": ("Travel Retail Insider", "en", "travelretailinsider.example", lambda d: f"{d:%b} {d.day} {d.year}"),
    "mm": ("Meridian Markets", "en", "meridianmarkets.example",
           lambda d: d.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")),
    "tl": ("The Toronto Ledger", "en", "torontoledger.example",
           lambda d: f"{EN_MON[d.month-1]} {d.day}, {d.year} {ampm(d, dots=True)} ET"),
    "md": ("Manhattan Dispatch", "en", "manhattandispatch.example", lambda d: d.strftime("%m/%d/%Y ") + ampm(d)),
    "lab": ("LA Basin Daily", "en", "labasindaily.example", lambda d: f"{d:%b} {d.day}, {d.year}"),
    "hch": ("Harbour City Herald", "en", "harbourcityherald.example",
            lambda d: f"{d.day} {EN_MON[d.month-1]} {d.year} {d:%H:%M} AEDT"),
    "sfd": ("서울패션데일리 Seoul Fashion Daily", "ko", "www.seoulfashiondaily.example",
            lambda d: d.strftime("%Y.%m.%d %H:%M")),
    "tbt": ("東京ビジネスタイムズ Tokyo Business Times", "ja", "www.tokyobiztimes.example",
            lambda d: f"{d.year}年{d.month}月{d.day}日 {d.hour}:{d.minute:02d}"),
    "fsd": ("ファッション通信デイリー", "ja", "fashiontsushin.example", lambda d: d.strftime("%Y/%m/%d %H:%M JST")),
    "cjgc": ("财经观察", "zh-CN", "www.caijingguancha.example", lambda d: d.strftime("%Y-%m-%d %H:%M:%S")),
    "hkdp": ("港聞快訊 HK Daily Pulse", "zh-HK", "hkdailypulse.example",
             lambda d: f"{d.year}年{d.month}月{d.day}日 {d:%H:%M}"),
}

BY_SOURCE = {"lw": "luxury_wire", "apn": "apn_newswire", "sfd": "seoul_fashion_daily"}

COOKIE = {
    "it": "Questo sito utilizza cookie tecnici e di profilazione, anche di terze parti. Chiudendo questo banner acconsenti all'uso dei cookie. [Accetta] [Rifiuta] [Personalizza]",
    "fr": "Nous et nos partenaires utilisons des cookies pour mesurer l'audience et personnaliser les publicités. [Tout accepter] [Continuer sans accepter]",
    "es": "Utilizamos cookies propias y de terceros. Si continúa navegando, consideramos que acepta su uso. [Aceptar] [Configurar]",
    "de": "Wir verwenden Cookies und ähnliche Technologien. Mit Klick auf \"Akzeptieren\" stimmen Sie der Verarbeitung zu. [Akzeptieren] [Einstellungen]",
    "en": "We use cookies to improve your experience and for advertising. By continuing you agree to our Cookie Policy. [Accept all] [Manage]",
    "ko": "본 사이트는 쿠키를 사용합니다. 계속 이용하시면 쿠키 사용에 동의하는 것으로 간주됩니다. [동의] [거부]",
    "ja": "当サイトではCookieを使用しています。閲覧を続けることでCookieの使用に同意したものとみなします。[同意する]",
    "zh-CN": "本网站使用Cookie以提升浏览体验。继续浏览即表示您同意我们的Cookie政策。[同意]",
    "zh-HK": "本網站使用Cookies以改善瀏覽體驗。繼續瀏覽即表示你同意我們的私隱政策。[接受]",
}
NAV = {
    "it": ["Home", "Moda", "Economia", "Lusso", "Retail", "Lifestyle", "Abbonati"],
    "fr": ["Accueil", "Mode", "Luxe", "Business", "Beauté", "Newsletter", "S'abonner"],
    "es": ["Portada", "Moda", "Lujo", "Negocios", "Estilo de vida"],
    "de": ["Startseite", "Wirtschaft", "Handel", "Börse", "Wetter", "Abo"],
    "en": ["Home", "News", "Business", "Retail", "Fashion", "Markets", "Subscribe"],
    "ko": ["홈", "패션", "뷰티", "리테일", "연예", "구독"],
    "ja": ["トップ", "経済", "企業", "マーケット", "流通", "会員登録"],
    "zh-CN": ["首页", "宏观", "消费", "公司", "时尚", "订阅"],
    "zh-HK": ["首頁", "港聞", "財經", "地產", "生活", "娛樂"],
}
READ_ALSO = {"it": "Leggi anche", "fr": "À lire aussi", "es": "Te puede interesar", "de": "Mehr zum Thema",
             "en": "Related", "ko": "관련 기사", "ja": "関連記事", "zh-CN": "相关阅读", "zh-HK": "相關新聞"}
PAYWALL = {"ja": "この記事は有料会員限定です。続きは会員登録（初月無料）でお読みいただけます。"}


def slugify(s, maxlen=60):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:maxlen].rstrip("-")


def first_sentence(body, n=220):
    p = body.strip().split("\n\n")[0]
    m = re.split(r"(?<=[.!?。])\s*", p, maxsplit=1)
    s = m[0] if m and len(m[0]) > 25 else p
    return s if len(s) <= n else s[: n - 3].rstrip() + "..."


def prep(articles):
    out = []
    for a in articles:
        a = dict(a)
        name, lang, domain, fmt_pub = SOURCES[a["src"]]
        a["source"], a["lang"], a["domain"] = name, a.get("lang", lang), domain
        d = dt.datetime.fromisoformat(a["pub"].replace("Z", "+00:00"))
        if d.tzinfo is None:
            d = d.replace(tzinfo=dt.timezone(dt.timedelta(hours=2)))
        a["dt"] = d
        a["published_str"] = fmt_pub(d)
        h = hashlib.md5((a["src"] + a["title"]).encode()).hexdigest()
        a["hash"] = h
        a["agg_id"] = "nw-" + h[:8]
        latin = slugify(a["title"])
        a["slug"] = a.get("slug") or (latin if len(latin) > 15 else "a" + h[:10])
        out.append(a)
    return out


# ---------------------------------------------------------------- renderers
def render_txt(a):
    body = a["body"].strip()
    if a.get("update"):
        body += "\n\n" + a["update"]
    if a.get("correction"):
        body += "\n\n" + a["correction"]
    src, d = a["src"], a["dt"]
    if src == "jdl":
        head = f"{a['source'].upper()}\n{a['title']}\nPar {a['author']} - Publié le {a['published_str']}\n\n"
    elif src == "zap":
        head = f"{a['title']}\n\n{a['published_str']} | {a['author']}\n\n"
    elif src == "mcn":
        head = f"MilanoCity News > Cronaca > Trasporti\n\n{a['title']}\n{a['published_str']}\n\n"
    elif src == "tri":
        head = f"TRAVEL RETAIL INSIDER | {a['published_str']}\n\n{a['title'].upper()}\n\nBy {a['author']}\n\n"
    elif src == "md":
        head = f"{a['title']}\n{a['author']} - {a['published_str']}\n" + "-" * 60 + "\n"
    elif src == "tbt":
        head = f"{a['title']}\n{a['source']}  {a['published_str']}\n\n"
    elif src == "hkdp":
        head = f"【{a['source'].split()[0]}】{a['title']}\n{a['published_str']}\n\n"
    elif src == "s24":
        head = f"{a['title']}\n({a['published_str']})\n\n"
    elif src == "hch":
        head = f"{a['source']} | Business | {a['published_str']}\n{a['title']}\n\n"
    elif src == "sfd":
        head = f"[{a['source']}] {a['title']}\n입력 {a['published_str']} | {a['author']}\n\n"
    else:
        head = f"{a['title']}\n{a['source']} - {a['published_str']}\n\n"
    tail = ""
    if src == "jdl":
        tail = "\n\n(c) Le Journal du Luxe - Reproduction interdite"
    elif src == "tri":
        tail = "\n\n--\nTravel Retail Insider is published by TRI Media Ltd. Subscribe for daily briefings."
    elif src == "sfd":
        tail = "\n\n<저작권자 © 서울패션데일리 무단전재 및 재배포 금지>"
    return head + body + tail + "\n"


def render_html(a):
    lang = a["lang"]
    paras = a["body"].strip().split("\n\n")
    paywalled = a.get("paywall")
    if paywalled:
        paras = paras[:2]
    ptags = "\n".join(f"      <p>{html.escape(p)}</p>" for p in paras)
    if paywalled:
        ptags += f'\n      <div class="paywall"><p>{html.escape(PAYWALL.get(lang, "Subscribe to continue reading."))}</p><a href="/subscribe">会員登録</a></div>'
    extra = ""
    if a.get("update"):
        extra += f'\n      <p class="update"><strong>{html.escape(a["update"])}</strong></p>'
    if a.get("correction"):
        extra += f'\n      <p class="correction"><em>{html.escape(a["correction"])}</em></p>'
    nav = " | ".join(f'<a href="/{slugify(x) or "s"}">{html.escape(x)}</a>' for x in NAV.get(lang, NAV["en"]))
    tags = ", ".join(html.escape(t) for t in a.get("tags", []))
    rel = READ_ALSO.get(lang, "Related")
    author = html.escape(a.get("author") or "")
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<title>{html.escape(a['title'])} | {html.escape(a['source'])}</title>
<meta name="description" content="{html.escape(first_sentence(a['body']))}">
<meta property="og:site_name" content="{html.escape(a['source'])}">
<meta property="article:published_time" content="{a['dt'].isoformat()}">
<meta name="keywords" content="{tags}">
<script>window.dataLayer=window.dataLayer||[];</script>
</head>
<body>
<div id="cookie-banner" class="cmp">{html.escape(COOKIE.get(lang, COOKIE['en']))}</div>
<header><div class="logo">{html.escape(a['source'])}</div>
<nav>{nav}</nav></header>
<main>
  <article>
    <h1>{html.escape(a['title'])}</h1>
    <div class="byline"><span class="author">{author}</span> <time datetime="{a['dt'].isoformat()}">{html.escape(a['published_str'])}</time></div>
    <div class="share">Facebook · X · LinkedIn · WhatsApp · Email</div>
    <div class="article-body">
{ptags}{extra}
    </div>
    <div class="tags">{tags}</div>
  </article>
  <aside class="related"><h3>{rel}</h3><ul><li><a href="#">...</a></li><li><a href="#">...</a></li></ul></aside>
  <div class="ad-slot" data-slot="mpu-1">ADVERTISEMENT</div>
</main>
<footer>© {a['dt'].year} {html.escape(a['source'])} · Privacy · Cookie policy · Contact</footer>
</body>
</html>
"""


def render_json(a):
    src = a["src"]
    body = a["body"].strip()
    if a.get("correction"):
        body += "\n\n" + a["correction"]
    if src == "apn":
        obj = {"guid": f"APN-{a['hash'][:12].upper()}", "slug": a["slug"], "version": 1,
               "headline": a["title"], "byline": a.get("author"), "dateline": a["published_str"],
               "urgency": 3, "keywords": a.get("tags", []), "body_text": body, "language": "en"}
    elif src == "lw":
        obj = {"id": int(a["hash"][:7], 16), "type": "story", "headline": a["title"],
               "firstCreated": a["dt"].astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "credit": a.get("author"), "subjects": a.get("tags", []),
               "content": {"format": "text/plain", "text": body}}
    elif src == "cjgc":
        obj = {"code": 0, "msg": "success", "data": {"title": a["title"], "pub_time": a["published_str"],
               "source": "财经观察", "author": a.get("author"), "content": body.replace("\n\n", "\n"),
               "keywords": ",".join(a.get("tags", [])), "editor": "责任编辑：王蕾"}}
    elif src == "drop":
        obj = {"post_id": int(a["hash"][:6], 16), "title": {"rendered": a["title"]},
               "date_gmt": a["dt"].astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
               "author_name": a.get("author"), "tags": a.get("tags", []),
               "content": {"rendered": "".join(f"<p>{html.escape(p)}</p>" for p in body.split("\n\n"))}}
    elif src == "mm":
        obj = {"storyId": a["hash"][:16], "headline": a["title"], "publishedAt": a["published_str"],
               "provider": "Meridian Markets", "topics": a.get("tags", []), "body": body, "wordCount": len(body.split())}
    else:
        obj = {"id": a["agg_id"], "source": a["source"], "headline": a["title"], "author": a.get("author"),
               "published_at": a["published_str"], "lang": a["lang"], "section": (a.get("tags") or [""])[0],
               "tags": a.get("tags", []), "body": body, "url": a["url"]}
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def mojibake(s):
    # UTF-8 bytes read back as Windows-1252 (classic double-encoding)
    return s.encode("utf-8").decode("cp1252", errors="replace")


# ---------------------------------------------------------------- main
def main():
    arts = prep(A_IT + A_EU + A_EN + A_AS)
    arts.sort(key=lambda a: a["dt"])
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    for a in arts:
        src, d = a["src"], a["dt"]
        ext = a["fmt"]
        if src in BY_SOURCE:
            folder = Path("by_source") / BY_SOURCE[src]
        else:
            folder = Path("articles") / d.strftime("%Y-%m")
        if src == "lw":
            fname = f"lw-{d.astimezone(dt.timezone.utc):%Y%m%d}-{int(a['hash'][:4], 16):05d}.{ext}"
        elif src == "apn":
            fname = f"APN_{d.astimezone(dt.timezone.utc):%Y%m%d%H%M}_{a['slug'][:40]}.{ext}"
        elif src in ("cjgc", "hkdp", "tbt", "fsd", "sfd"):
            fname = f"{src}_{d:%Y%m%d}_{int(a['hash'][:6], 16)}.{ext}"
        else:
            fname = f"{src}_{d:%Y-%m-%d}_{a['slug'][:50]}.{ext}"
        a["file"] = str(folder / fname)
        # URL shapes vary per source
        if src in ("cjgc",):
            a["url"] = f"https://{a['domain']}/news/{d:%Y%m%d}/{int(a['hash'][:8], 16)}.html"
        elif src in ("sfd",):
            a["url"] = f"https://{a['domain']}/news/articleView.html?idxno={int(a['hash'][:5], 16)}"
        elif src in ("tbt",):
            a["url"] = f"https://{a['domain']}/article/DGXZQO{a['hash'][:12].upper()}/"
        elif src == "drop":
            a["url"] = f"https://{a['domain']}/{d:%Y/%m}/{a['slug']}/"
        else:
            a["url"] = f"https://{a['domain']}/{d:%Y/%m/%d}/{a['slug']}"

    for a in arts:
        if a["fmt"] == "txt":
            text = render_txt(a)
        elif a["fmt"] == "html":
            text = render_html(a)
        else:
            text = render_json(a)
        if a.get("mojibake"):
            text = mojibake(text)
        p = OUT / a["file"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    # ---------------- feed index
    items = []
    for a in arts:
        if a.get("not_indexed"):
            continue
        tags = a.get("tags", [])
        item = {"id": a["agg_id"], "source": a["source"], "lang": a["lang"], "published": a["published_str"],
                "title": a["title"], "url": a["url"], "summary": first_sentence(a["body"]),
                "tags": ", ".join(tags) if a["src"] in ("wk", "zap", "hkdp") else tags, "file": a["file"]}
        if a["src"] in ("s24", "md"):
            item["summary"] = None
        if a.get("paywall"):
            item["paywalled"] = True
        items.append(item)
        if a.get("update"):  # re-crawled after the update: same url, new id/published
            upd = dict(item)
            upd["id"] = "nw-" + hashlib.md5((a["hash"] + "u").encode()).hexdigest()[:8]
            m = re.search(r"ore (\d{1,2}:\d{2})", a["update"])
            upd["published"] = a["published_str"].split(", ore")[0] + f", ore {m.group(1).replace(':', ':')}" if m else upd["published"]
            upd["title"] = "AGGIORNATO - " + a["title"]
            items.append(upd)
    # index-only item: paywalled, body never fetched
    items.append({"id": "nw-7c1e0a92", "source": SOURCES["tbt"][0], "lang": "ja",
                  "published": "2026年10月16日 6:00",
                  "title": "高級ブランド、相次ぐ日本値上げ　内外価格差は1割未満に",
                  "url": "https://www.tokyobiztimes.example/article/DGXZQO7C1E0A92F3B1/",
                  "summary": "欧州の高級ブランドが日本での値上げを相次ぎ実施している。円安で拡大した欧州との価格差は",
                  "tags": ["値上げ", "円安"], "file": None, "paywalled": True, "fetch_status": "403"})
    # aggregator order: crawler order (not chronological)
    items.sort(key=lambda x: x["id"][3:5])
    feed = {"feed": "luxury-retail-monitor", "provider": "NewsHarvester v2.3", "query": "luxury OR valentino OR outerwear OR tourism OR strike OR weather (custom watchlist #12)",
            "generated_at": "2026-10-22T05:12:44Z", "count": len(items), "items": items}
    (OUT / "feed_index.json").write_text(json.dumps(feed, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------------- RSS for Luxury Wire
    rss_items = []
    for a in sorted([x for x in arts if x.get("rss")], key=lambda x: x["dt"], reverse=True):
        cats = "".join(f"\n      <category>{html.escape(t)}</category>" for t in a.get("tags", []))
        desc = a["body"].strip().split("\n\n")[0]
        rss_items.append(f"""    <item>
      <title>{html.escape(a['title'])}</title>
      <link>{a['url']}</link>
      <guid isPermaLink="false">lw:{int(a['hash'][:7], 16)}</guid>
      <pubDate>{format_datetime(a['dt'].astimezone(dt.timezone.utc), usegmt=True)}</pubDate>
      <dc:creator>{html.escape(a.get('author') or '')}</dc:creator>{cats}
      <description><![CDATA[{desc}]]></description>
    </item>""")
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Luxury Wire - Top Stories</title>
    <link>https://luxurywire.example/</link>
    <atom:link href="https://luxurywire.example/rss/top.xml" rel="self" type="application/rss+xml"/>
    <description>Breaking news on the global luxury industry</description>
    <language>en-gb</language>
    <lastBuildDate>Thu, 22 Oct 2026 05:00:41 GMT</lastBuildDate>
    <ttl>15</ttl>
{chr(10).join(rss_items)}
  </channel>
</rss>
"""
    (OUT / "rss_luxury_wire.xml").write_text(rss, encoding="utf-8")
    n_files = len(list(OUT.rglob("*.*")))
    print(f"articles: {len(arts)}, index items: {len(items)}, files: {n_files}")


if __name__ == "__main__":
    main()
