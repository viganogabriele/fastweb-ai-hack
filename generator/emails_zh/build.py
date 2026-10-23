"""Wrap the hand-authored bodies (bodies_<STORE>.py) into RFC-822 .eml files.

Usage:  .venv/bin/python generator/emails_zh/build.py [STORE ...]
Output: generated/sources/store_emails/<STORE>/<YYYYMMDD>_<HHMM>_<STORE><suffix>.eml

Each bodies_<STORE>.py defines:
  STORE   = "SHA01"
  PEOPLE  = {key: (display_name, address), ...}     # store-local people + store mailbox
  DEFAULT_TO = [...]; DEFAULT_CC = [...]              # keys or addresses (see common.addr)
  EMAILS  = [dict(...), ...]

Email dict keys:
  send     "YYYY-MM-DD HH:MM" local time (all five stores are UTC+8) -> Date header + filename
  frm      persona key
  subject  str
  body     str (text/plain). Required unless html_only.
  to, cc   optional lists overriding defaults (cc=[] for none)
  id       optional local key, used by reply_to of later emails
  reply_to optional id of an earlier email -> In-Reply-To / References
  suffix   optional filename suffix ("_dup", "_re1", "_fwd", "_corr", "_ooo"...)
  html     optional HTML alternative (multipart/alternative with body as text part)
  html_only optional bool: send only the HTML part
  charset  optional body charset ("utf-8" default; "gb18030"/"big5" for some legacy mailers)
  attach   optional list of {"kind": "jpg"|"csv"|"xlsx", "name": str, "content": str (csv) | "rows": [[..]] (xlsx),
           "encoding": "utf-8"|"gbk"|"big5" (csv)}
  xmailer  optional X-Mailer header (falls back to PEOPLE_MAILER[frm] if defined)
  importance optional "high"
"""
import hashlib
import importlib
import io
import os
import sys
from datetime import datetime, timedelta, timezone
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import format_datetime, formataddr, parseaddr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from common import addr  # noqa: E402

TZ = timezone(timedelta(hours=8))
OUT = os.path.join(ROOT, "generated", "sources", "store_emails")
STORES = ["SHA01", "BJS01", "CDU01", "HKG01", "TPE01"]


def _fmt_addr(s: str, charset="utf-8") -> str:
    name, a = parseaddr(s)
    if not name:
        return a
    try:
        name.encode("ascii")
        return formataddr((name, a))
    except UnicodeEncodeError:
        return formataddr((str(Header(name, charset)), a))


def _msgid(store, key, frm_addr):
    h = hashlib.sha1(f"{store}|{key}".encode()).hexdigest().upper()
    a = parseaddr(frm_addr)[1]
    dom = a.split("@")[-1] if "@" in a else "valentino-retail.example"
    return f"<{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:28]}@{dom}>"


def _jpeg_bytes(seed: str) -> bytes:
    from PIL import Image
    h = hashlib.md5(seed.encode()).digest()
    img = Image.new("RGB", (64, 48), (h[0], h[1], h[2]))
    b = io.BytesIO()
    img.save(b, format="JPEG", quality=60)
    return b.getvalue()


def _xlsx_bytes(rows) -> bytes:
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    for r in rows:
        ws.append(r)
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


def build_store(store):
    mod = importlib.import_module(f"bodies_{store}")
    people = dict(mod.PEOPLE)
    mailers = getattr(mod, "PEOPLE_MAILER", {})
    out_dir = os.path.join(OUT, store)
    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        if f.endswith(".eml"):
            os.remove(os.path.join(out_dir, f))

    ids = {}
    refs = {}
    written = []
    for i, e in enumerate(mod.EMAILS):
        send = datetime.strptime(e["send"], "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
        # add deterministic seconds
        sec = int(hashlib.md5(f"{store}{i}".encode()).hexdigest()[:2], 16) % 60
        send = send.replace(second=sec)
        fname = f"{send:%Y%m%d_%H%M}_{store}{e.get('suffix', '')}.eml"
        if fname in written:
            raise SystemExit(f"{store}: duplicate filename {fname} (email #{i}); add a suffix or shift the minute")
        written.append(fname)

        charset = e.get("charset", "utf-8")
        frm = addr(people, e["frm"])
        to = [addr(people, x) for x in e.get("to", mod.DEFAULT_TO)]
        cc = [addr(people, x) for x in e.get("cc", mod.DEFAULT_CC)]

        text = e.get("body")
        html = e.get("html")
        atts = e.get("attach", [])
        if e.get("html_only"):
            core = MIMEText(html, "html", charset)
        elif html:
            core = MIMEMultipart("alternative")
            core.attach(MIMEText(text, "plain", charset))
            core.attach(MIMEText(html, "html", charset))
        else:
            core = MIMEText(text, "plain", charset)

        if atts:
            msg = MIMEMultipart("mixed")
            msg.attach(core)
            for a in atts:
                k = a["kind"]
                if k == "jpg":
                    part = MIMEImage(_jpeg_bytes(store + a["name"] + str(i)), "jpeg")
                elif k == "csv":
                    enc = a.get("encoding", "utf-8")
                    part = MIMEApplication(a["content"].encode(enc), "octet-stream")
                elif k == "xlsx":
                    part = MIMEApplication(_xlsx_bytes(a["rows"]),
                                           "vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else:
                    raise ValueError(k)
                part.add_header("Content-Disposition", "attachment", filename=("utf-8", "", a["name"]))
                msg.attach(part)
        else:
            msg = core

        msg["From"] = _fmt_addr(frm, charset if charset != "utf-8" else "utf-8")
        msg["To"] = ", ".join(_fmt_addr(x) for x in to)
        if cc:
            msg["Cc"] = ", ".join(_fmt_addr(x) for x in cc)
        msg["Subject"] = str(Header(e["subject"], "utf-8")) if any(ord(c) > 127 for c in e["subject"]) else e["subject"]
        msg["Date"] = format_datetime(send)
        mid = _msgid(store, fname, frm)
        msg["Message-ID"] = mid
        if e.get("reply_to"):
            parent = e["reply_to"]
            if parent not in ids:
                raise SystemExit(f"{store}: reply_to {parent!r} not found before email #{i}")
            msg["In-Reply-To"] = ids[parent]
            chain = refs.get(parent, []) + [ids[parent]]
            msg["References"] = " ".join(chain)
            if e.get("id"):
                refs[e["id"]] = chain
        if e.get("id"):
            ids[e["id"]] = mid
        xm = e.get("xmailer", mailers.get(e["frm"]))
        if xm:
            msg["X-Mailer"] = xm
        if e.get("importance") == "high":
            msg["Importance"] = "high"
            msg["X-Priority"] = "1"

        with open(os.path.join(out_dir, fname), "wb") as fh:
            fh.write(msg.as_bytes())
    return written


if __name__ == "__main__":
    todo = sys.argv[1:] or STORES
    for s in todo:
        w = build_store(s)
        print(s, len(w), "emails")
