"""Wrap the hand-authored German closing emails (mun01.py, ber01.py, zrh01.py, stm01.py) into .eml files.

Bodies are authored individually in the per-store modules; this script only adds headers, quoting,
HTML alternatives, attachments and writes the files.

Run:  .venv/bin/python generator/emails_de/build.py
"""
import hashlib
import io
import os
import sys
import uuid
from datetime import datetime
from email.message import EmailMessage
from email.utils import format_datetime, formataddr
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import mun01, ber01, zrh01, stm01  # noqa: E402

DOM = "moncler-retail.example"
OUT = os.path.join(ROOT, "generated", "sources", "store_emails")

SHARED = {
    "sw": dict(name="Stefan Wagner", addr=f"stefan.wagner@{DOM}", mailer="outlook",
               footer="\n\nStefan Wagner\nArea Manager DACH\nMoncler Retail\nM +49 151 2290 4417"),
    "ops": dict(name="Retail Ops DACH", addr=f"retail-ops-dach@{DOM}"),
    "merch": dict(name="Merch Planning", addr=f"merch-planning@{DOM}"),
    "vmteam": dict(name="VM Team", addr=f"vm-team@{DOM}"),
    "quality": dict(name="Quality Control", addr=f"quality.control@{DOM}"),
}

STORES = {"MUN01": mun01, "BER01": ber01, "ZRH01": zrh01, "STM01": stm01}
TZ = {"MUN01": "Europe/Berlin", "BER01": "Europe/Berlin", "ZRH01": "Europe/Zurich", "STM01": "Europe/Zurich"}

WD_DE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
MON_DE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober",
          "November", "Dezember"]


def h(s, n=12):
    return hashlib.sha1(s.encode()).hexdigest()[:n]


def people_for(mod):
    p = dict(SHARED)
    p.update(mod.PEOPLE)
    return p


def addr(p, key):
    x = p[key]
    return formataddr((x["name"], x["addr"]))


def msgid(store, e, w):
    seed = f"{store}-{e['id']}"
    if w.get("mailer") == "iphone":
        u = uuid.UUID(hashlib.md5(seed.encode()).hexdigest())
        return f"<{str(u).upper()}@{DOM}>"
    if w.get("mailer") == "outlook":
        a = h(seed, 20).upper()
        return f"<{a[:4]}PR0{int(a[4], 16) % 9 + 1}MB{a[5:9]}{a[9:20]}@{a[:4]}PR0{int(a[4], 16) % 9 + 1}MB{a[5:9]}.eurprd0{int(a[10], 16) % 7 + 1}.prod.outlook.com>"
    return f"<{h(seed, 16)}.{h(seed + 'x', 8)}@{DOM}>"


def de_long_date(dt):
    return f"{WD_DE[dt.weekday()]}, {dt.day}. {MON_DE[dt.month - 1]} {dt.year} {dt:%H:%M}"


def quote_block(orig, p, style, tzname):
    """Return quoted text of an earlier email (Outlook or Apple style)."""
    dt = datetime.strptime(orig["d"], "%Y-%m-%d %H:%M")
    body = orig["_text"]
    if style == "iphone":
        head = f"Am {dt:%d.%m.%Y} um {dt:%H:%M} schrieb {p[orig['w']]['name']} <{p[orig['w']]['addr']}>:\n\n"
        return "\n\n" + head + "\n".join("> " + l if l else ">" for l in body.split("\n"))
    to = "; ".join(f"{p[k]['name']} <{p[k]['addr']}>" for k in orig["_to"])
    cc = "; ".join(f"{p[k]['name']} <{p[k]['addr']}>" for k in orig["_cc"])
    head = ("\n\n-----Ursprüngliche Nachricht-----\n"
            f"Von: {p[orig['w']]['name']} <{p[orig['w']]['addr']}>\n"
            f"Gesendet: {de_long_date(dt)}\n"
            f"An: {to}\n" + (f"Cc: {cc}\n" if cc else "") +
            f"Betreff: {orig['subj']}\n\n")
    return head + body


def table_text(rows):
    w = [max(len(str(r[i])) for r in rows) for i in range(len(rows[0]))]
    return "\n".join("  ".join(str(c).ljust(w[i]) for i, c in enumerate(r)).rstrip() for r in rows)


def table_html(rows):
    out = ['<table border="1" cellspacing="0" cellpadding="3" style="border-collapse:collapse;font-family:Calibri,Arial;font-size:11pt">']
    for i, r in enumerate(rows):
        tag = "th" if i == 0 else "td"
        bg = ' style="background:#D9E1F2"' if i == 0 else ""
        out.append("<tr" + bg + ">" + "".join(f"<{tag}>{c}</{tag}>" for c in r) + "</tr>")
    out.append("</table>")
    return "\n".join(out)


def html_escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def body_html(text_before, rows, text_after):
    def paras(t):
        return "".join(f'<p class="MsoNormal">{html_escape(l) if l else "&nbsp;"}</p>\n' for l in t.split("\n"))
    return ('<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
            '<style>p.MsoNormal{margin:0;font-family:Calibri,sans-serif;font-size:11pt}</style></head>'
            '<body lang="DE" link="#0563C1">\n<div class="WordSection1">\n' + paras(text_before) +
            table_html(rows) + "\n" + paras(text_after) + "</div></body></html>")


def jpeg_bytes(seed):
    from PIL import Image, ImageDraw
    c = int(h(seed, 6), 16)
    img = Image.new("RGB", (160, 120), (((c >> 16) & 127) + 60, ((c >> 8) & 127) + 60, (c & 127) + 60))
    d = ImageDraw.Draw(img)
    for i in range(0, 160, 16):
        d.line([(i, 0), (160 - i, 120)], fill=(40, 40, 40), width=1)
    b = io.BytesIO()
    img.save(b, "JPEG", quality=60)
    return b.getvalue()


def xlsx_bytes(rows, sheet="Tagesabschluss"):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = sheet
    for r in rows:
        ws.append(r)
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


def build_store(store, mod):
    p = people_for(mod)
    tz = ZoneInfo(TZ[store])
    outdir = os.path.join(OUT, store)
    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir):
        if f.endswith(".eml"):
            os.remove(os.path.join(outdir, f))
    by_id = {}
    written = []
    for e in mod.EMAILS:
        w = dict(p[e["w"]])
        if "mailer" in e:
            w["mailer"] = e["mailer"]
        dt = datetime.strptime(e["d"], "%Y-%m-%d %H:%M").replace(tzinfo=tz)
        if not e.get("sfx", "").startswith("_dup"):
            dt = dt.replace(second=int(h(store + e["id"], 4), 16) % 60)
        to = e.get("to", ["ops"])
        cc = e.get("cc", ["sw"])
        e["_to"], e["_cc"] = to, cc
        text = e["body"].strip("\n")
        rows = e.get("table")
        if rows:
            before, after = text.split("{TABLE}")
            text_plain = before + table_text(rows) + after
        else:
            before = after = None
            text_plain = text
        if w.get("footer") and not e.get("nofooter"):
            text_plain += w["footer"]
            if rows:
                after += w["footer"]
        e["_text"] = text_plain
        if e.get("quote"):
            orig = by_id[e["quote"]]
            qb = quote_block(orig, p, w.get("mailer"), TZ[store])
            text_plain += qb
            if rows:
                after += qb
        msg = EmailMessage()
        msg["From"] = addr(p, e["w"])
        msg["To"] = ", ".join(addr(p, k) for k in to)
        if cc:
            msg["Cc"] = ", ".join(addr(p, k) for k in cc)
        msg["Subject"] = e["subj"]
        msg["Date"] = format_datetime(dt)
        mid = msgid(store, e, w)
        msg["Message-ID"] = mid
        e["_mid"] = mid
        if e.get("reply"):
            parent = by_id[e["reply"]]
            refs = parent.get("_refs", []) + [parent["_mid"]]
            e["_refs"] = refs
            msg["In-Reply-To"] = parent["_mid"]
            msg["References"] = " ".join(refs)
        msg["MIME-Version"] = "1.0"
        if w.get("mailer") == "iphone":
            msg["X-Mailer"] = "iPhone Mail (22A3370)"
        elif w.get("mailer") == "outlook":
            msg["X-MS-Has-Attach"] = "yes" if e.get("att") else ""
            msg["Content-Language"] = "de-CH" if store in ("ZRH01", "STM01") else "de-DE"
        if e.get("auto"):
            msg["Auto-Submitted"] = "auto-replied"
            msg["X-Auto-Response-Suppress"] = "All"
        if e.get("importance"):
            msg["Importance"] = e["importance"]
        msg.set_content(text_plain, charset="utf-8")
        if rows:
            msg.add_alternative(body_html(before, rows, after), subtype="html", charset="utf-8")
        for a in e.get("att", []):
            if a["kind"] == "jpg":
                msg.add_attachment(jpeg_bytes(a["name"] + store), maintype="image", subtype="jpeg", filename=a["name"])
            elif a["kind"] == "xlsx":
                msg.add_attachment(xlsx_bytes(a["rows"], a.get("sheet", "Tagesabschluss")), maintype="application",
                                   subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=a["name"])
            elif a["kind"] == "csv":
                msg.add_attachment(a["text"].encode(a.get("enc", "utf-8")), maintype="text", subtype="csv",
                                   filename=a["name"])
        sfx = e.get("sfx")
        if sfx is None:
            if e.get("auto"):
                sfx = "_ooo"
            elif e.get("reply"):
                depth, cur = 0, e
                while cur.get("reply"):
                    depth, cur = depth + 1, by_id[cur["reply"]]
                sfx = f"_re{depth}"
            elif e["w"] == "sw":
                sfx = "_am"
            else:
                sfx = ""
        fname = f"{dt:%Y%m%d_%H%M}_{store}{sfx}.eml"
        path = os.path.join(outdir, fname)
        k = 2
        while os.path.exists(path):
            fname = f"{dt:%Y%m%d_%H%M}_{store}{sfx}{k}.eml"
            path = os.path.join(outdir, fname)
            k += 1
        with open(path, "wb") as fh:
            fh.write(bytes(msg))
        by_id[e["id"]] = e
        written.append(fname)
    return written


def main():
    tot = 0
    for st, mod in STORES.items():
        w = build_store(st, mod)
        print(st, len(w))
        tot += len(w)
    print("total", tot)


if __name__ == "__main__":
    main()
