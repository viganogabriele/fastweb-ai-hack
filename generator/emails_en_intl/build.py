"""Wrap the hand-authored closing emails (generator/emails_en_intl/stores/*.py) into RFC-822 .eml files.

Bodies are written by hand in the store modules; this script only adds headers, quoting of parent
messages for replies/forwards, signatures/footers and attachments.

usage: .venv/bin/python generator/emails_en_intl/build.py [STORE ...]
"""
import hashlib
import importlib
import io
import os
import shutil
import sys
from datetime import datetime
from email.message import EmailMessage
from email.utils import format_datetime, formataddr
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "generated", "sources", "store_emails")
sys.path.insert(0, HERE)

ALL = ["LON01", "LON02", "AMS01", "CPH01", "DXB01", "SIN01", "SYD01"]


def tiny_jpeg(seed: str) -> bytes:
    from PIL import Image, ImageDraw
    h = int(hashlib.md5(seed.encode()).hexdigest()[:6], 16)
    img = Image.new("RGB", (96, 72), ((h >> 16) & 0xFF, (h >> 8) & 0x7F, h & 0x9F))
    d = ImageDraw.Draw(img)
    d.rectangle([20, 15, 70, 60], outline=(230, 230, 230))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=40)
    return buf.getvalue()


def tiny_xlsx(rows) -> bytes:
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Closing"
    for r in rows:
        ws.append(list(r))
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def msgid(store, eid, host):
    h = hashlib.sha1(f"{store}|{eid}".encode()).hexdigest()
    return f"<{h[:12].upper()}.{h[12:20]}@{host}>"


def quote_block(parent, style, tz):
    p_dt = parent["_dt"]
    name, addr = parent["_from"]
    body = parent["_fullbody"]
    if style == "outlook":
        hdr = (f"From: {name} <{addr}>\nSent: {p_dt.strftime('%A, %B %-d, %Y %-I:%M %p')}\n"
               f"To: {parent['_to_str']}\n")
        if parent.get("_cc_str"):
            hdr += f"Cc: {parent['_cc_str']}\n"
        hdr += f"Subject: {parent['subj']}\n\n"
        return "\n\n________________________________\n" + hdr + body
    if style == "fwd":
        hdr = (f"---------- Forwarded message ---------\nFrom: {name} <{addr}>\n"
               f"Date: {p_dt.strftime('%a, %-d %b %Y at %H:%M')}\nSubject: {parent['subj']}\n"
               f"To: {parent['_to_str']}\n\n")
        return "\n\n" + hdr + body
    # iphone / gmail style
    q = "\n".join(("> " + l) if l.strip() else ">" for l in body.splitlines())
    return f"\n\n> On {p_dt.strftime('%-d %b %Y, at %H:%M')}, {name} <{addr}> wrote:\n>\n" + q


def _kind(sid, e, dt):
    from index_overrides import OVR
    from datetime import timedelta
    if (sid, e["id"]) in OVR:
        return OVR[(sid, e["id"])]
    suf = e.get("suffix", "")
    kind = "closing"
    if suf.startswith("_dup"):
        kind = "duplicate"
    elif suf.startswith("_re"):
        kind = "reply"
    elif suf.startswith("_fwd"):
        kind = "forward"
    bd = dt.date() if dt.hour >= 12 else (dt - timedelta(days=1)).date()
    return kind, bd.isoformat()


def build_store(sid, index_rows=None):
    mod = importlib.import_module(f"stores.{sid.lower()}")
    tz = ZoneInfo(mod.TZ)
    outdir = os.path.join(OUT, sid)
    if os.path.isdir(outdir):
        shutil.rmtree(outdir)
    os.makedirs(outdir)
    by_id = {}
    n = 0
    for e in mod.EMAILS:
        eid = e["id"]
        dt = datetime.strptime(e["dt"], "%Y-%m-%d %H:%M").replace(tzinfo=tz)
        if e.get("tz"):
            dt = datetime.strptime(e["dt"], "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo(e["tz"]))
        who = mod.PEOPLE[e["frm"]]
        name, addr = who[0], who[1]
        to = e.get("to", mod.TO)
        cc = e.get("cc", mod.CC)
        body = e["body"].strip("\n")
        # signature / footers
        if e.get("sig", True) and len(who) > 2 and who[2]:
            body += "\n\n" + who[2]
        if e.get("ip"):
            body += "\n\n" + e.get("ip_text", "Sent from my iPhone")
        if e.get("disc"):
            body += "\n\n" + mod.DISCLAIMER
        if e.get("tail"):
            body += "\n\n" + e["tail"]
        parent = by_id.get(e.get("re")) if e.get("re") else None
        full = body
        if parent is not None and e.get("quote", "iphone"):
            full = body + quote_block(parent, e.get("quote", "iphone"), tz)
        msg = EmailMessage()
        msg["From"] = formataddr((name, addr)) if name else addr
        msg["To"] = ", ".join(to)
        if cc:
            msg["Cc"] = ", ".join(cc)
        msg["Subject"] = e["subj"]
        msg["Date"] = format_datetime(dt)
        mid = msgid(sid, eid, e.get("host", "moncler-retail.example"))
        if e.get("dup_of") and e["dup_of"] in by_id and e.get("same_mid"):
            mid = by_id[e["dup_of"]]["_mid"]
        msg["Message-ID"] = mid
        if parent is not None:
            msg["In-Reply-To"] = parent["_mid"]
            refs = (parent.get("_refs", "") + " " + parent["_mid"]).strip()
            msg["References"] = refs
            e["_refs"] = refs
        for k, v in e.get("headers", {}).items():
            msg[k] = v
        msg["MIME-Version"] = "1.0"
        # corporate Outlook clients (with disclaimer) send quoted-printable, phones/webmail send 8bit
        msg.set_content(full, cte=e.get("cte", "quoted-printable" if e.get("disc") else "8bit"))
        if e.get("html"):
            msg.add_alternative(e["html"], subtype="html")
        for att in e.get("att", []):
            fn = att[0]
            if fn.lower().endswith(".jpg"):
                msg.add_attachment(tiny_jpeg(sid + fn), maintype="image", subtype="jpeg", filename=fn)
            elif fn.lower().endswith(".csv"):
                msg.add_attachment(att[1].encode("utf-8"), maintype="text", subtype="csv", filename=fn)
            elif fn.lower().endswith(".xlsx"):
                msg.add_attachment(tiny_xlsx(att[1]), maintype="application",
                                   subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=fn)
            elif fn.lower().endswith(".txt"):
                msg.add_attachment(att[1], filename=fn)
        e["_dt"], e["_from"], e["_fullbody"], e["_mid"] = dt, (name or addr, addr), full, mid
        e["_to_str"] = ", ".join(to)
        e["_cc_str"] = ", ".join(cc) if cc else ""
        by_id[eid] = e
        fname = f"{dt.strftime('%Y%m%d_%H%M')}_{sid}{e.get('suffix', '')}.eml"
        path = os.path.join(outdir, fname)
        if os.path.exists(path):
            raise SystemExit(f"duplicate filename {path}")
        with open(path, "wb") as f:
            f.write(bytes(msg))
        if index_rows is not None:
            kind, bd = _kind(sid, e, dt)
            index_rows.append([sid, fname, eid, dt.strftime("%Y-%m-%d %H:%M"), bd, kind,
                               formataddr((name, addr)) if name else addr, e["subj"]])
        n += 1
    return n


if __name__ == "__main__":
    import csv
    stores = sys.argv[1:] or ALL
    rows = []
    for s in stores:
        print(s, build_store(s, rows))
    if stores == ALL:
        with open(os.path.join(ROOT, "generated", "ground_truth", "answer_keys", "emails", "emails_en_intl_index.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["store", "file", "id", "sent", "business_date", "kind", "frm", "subject"])
            w.writerows(rows)
