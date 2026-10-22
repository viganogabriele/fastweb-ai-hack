"""Wrap the hand-authored Japanese store emails (tyo01.py / tyo02.py / osa01.py) into .eml files.

Run: .venv/bin/python generator/emails_ja/build.py
Output: generated/sources/store_emails/<STORE>/<YYYYMMDD>_<HHMM>_<STORE>[_suffix].eml
The bodies are data (one dict per email); this script only handles headers / MIME / encodings.
"""
import hashlib
import io
import sys
from datetime import datetime, timedelta, timezone
from email.headerregistry import Address
from email.message import EmailMessage
from email.utils import format_datetime
from email.header import Header
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = ROOT / "generated" / "sources" / "store_emails"
sys.path.insert(0, str(HERE))

from people import PEOPLE, LISTS  # noqa: E402
import tyo01, tyo02, osa01  # noqa: E402

JST = timezone(timedelta(hours=9))
DOMAIN = "moncler-retail.example"


def msgid(store, key):
    h = hashlib.sha1(f"{store}|{key}".encode()).hexdigest()
    return f"<{h[:12]}.{h[12:20]}@{'mail.' + DOMAIN}>"


def addr(person_key):
    name, email = PEOPLE[person_key]
    user, dom = email.split("@")
    return Address(display_name=name, username=user, domain=dom)


def addr_str_jis(person_key):
    name, email = PEOPLE[person_key]
    return f"{Header(name, 'iso-2022-jp').encode()} <{email}>"


def tiny_jpeg(seed):
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (160, 120), (90 + seed % 60, 90, 95))
    d = ImageDraw.Draw(img)
    d.rectangle([60, 10, 100, 110], fill=(30, 30, 35))
    d.line([80, 10, 80, 110], fill=(180, 180, 170), width=3)
    d.rectangle([72, 50, 88, 66], fill=(200, 200, 190))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=60)
    return buf.getvalue()


def tiny_xlsx(rows):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "日報"
    for r in rows:
        ws.append(r)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def build_jis(store, e, all_ids, send):
    """Old Japanese mailer style: ISO-2022-JP 7bit body, B-encoded ISO-2022-JP headers (compat32)."""
    from email.mime.text import MIMEText
    body = e["body"].strip("\n") + "\n"
    msg = MIMEText(body, "plain", "iso-2022-jp")
    who = e["from"]
    to = e.get("to", [LISTS["ops"]])
    cc = e.get("cc", [LISTS["suzuki"]])
    msg["From"] = addr_str_jis(who)
    msg["To"] = ", ".join(t if "@" in t else addr_str_jis(t) for t in to)
    if cc:
        msg["Cc"] = ", ".join(c if "@" in c else addr_str_jis(c) for c in cc)
    msg["Subject"] = Header(e["subject"], "iso-2022-jp")
    msg["Date"] = format_datetime(send)
    key = e.get("key", e["send"] + e.get("suffix", ""))
    mid = msgid(store, key)
    all_ids[key] = mid
    msg["Message-ID"] = mid
    if e.get("reply_to"):
        msg["In-Reply-To"] = all_ids[e["reply_to"]]
        msg["References"] = all_ids[e["reply_to"]]
    msg["X-Mailer"] = e.get("mailer", PEOPLE_MAILER.get(who, "Microsoft Outlook 16.0"))
    return msg


def build_one(store, e, all_ids):
    send = datetime.strptime(e["send"], "%Y-%m-%d %H:%M").replace(tzinfo=JST)
    charset = e.get("charset", "utf-8")
    if charset == "iso-2022-jp":
        msg = build_jis(store, e, all_ids, send)
        suffix = e.get("suffix", "")
        return f"{send:%Y%m%d_%H%M}_{store}{suffix}.eml", msg.as_bytes()
    msg = EmailMessage()
    who = e["from"]
    to = e.get("to", [LISTS["ops"]])
    cc = e.get("cc", [LISTS["suzuki"]])
    msg["From"] = addr(who)
    msg["To"] = [Address(addr_spec=t) if "@" in t else addr(t) for t in to]
    if cc:
        msg["Cc"] = [Address(addr_spec=c) if "@" in c else addr(c) for c in cc]
    msg["Subject"] = e["subject"]
    msg["Date"] = format_datetime(send)
    key = e.get("key", e["send"] + e.get("suffix", ""))
    mid = msgid(store, key)
    all_ids[key] = mid
    msg["Message-ID"] = mid
    if e.get("reply_to"):
        parent = all_ids[e["reply_to"]]
        msg["In-Reply-To"] = parent
        msg["References"] = parent
    msg["MIME-Version"] = "1.0"
    msg["X-Mailer"] = e.get("mailer", PEOPLE_MAILER.get(who, "Microsoft Outlook 16.0"))

    body = e["body"].strip("\n") + "\n"
    msg.set_content(body, charset="utf-8", cte=e.get("cte", "base64"))
    if e.get("html"):
        msg.add_alternative(e["html"], subtype="html", charset="utf-8", cte="base64")
    for att in e.get("attach", []):
        kind, fname = att[0], att[1]
        if kind == "jpg":
            msg.add_attachment(tiny_jpeg(len(fname)), maintype="image", subtype="jpeg", filename=fname)
        elif kind == "xlsx":
            msg.add_attachment(tiny_xlsx(att[2]), maintype="application",
                               subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=fname)
        elif kind == "csv":
            msg.add_attachment(att[2].encode(att[3] if len(att) > 3 else "utf-8"), maintype="text",
                               subtype="csv", filename=fname)
    suffix = e.get("suffix", "")
    fname = f"{send:%Y%m%d_%H%M}_{store}{suffix}.eml"
    return fname, bytes(msg)


PEOPLE_MAILER = {
    "tanaka": "Microsoft Outlook 16.0",
    "sato": "iPhone Mail (22A3354)",
    "kimura": "iPhone Mail (22A3354)",
    "tyo01": "Becky! ver. 2.81.04",
    "ito": "Microsoft Outlook 16.0",
    "takahashi": "Microsoft Outlook 16.0",
    "park": "Gmail for iOS",
    "tyo02": "Microsoft Outlook 16.0",
    "nakamura": "iPhone Mail (22A3354)",
    "yamamoto": "Microsoft Outlook 16.0",
    "matsui": "Android Mail",
    "osa01": "Microsoft Outlook 16.0",
    "suzuki": "Microsoft Outlook 16.0",
}


def main():
    total = 0
    for store, mod in (("TYO01", tyo01), ("TYO02", tyo02), ("OSA01", osa01)):
        d = OUT / store
        d.mkdir(parents=True, exist_ok=True)
        for old in d.glob("*.eml"):
            old.unlink()
        ids = {}
        seen = set()
        for e in sorted(mod.EMAILS, key=lambda x: x["send"]):
            fname, raw = build_one(store, e, ids)
            assert fname not in seen, fname
            seen.add(fname)
            (d / fname).write_bytes(raw)
        print(store, len(mod.EMAILS))
        total += len(mod.EMAILS)
    print("total", total)


if __name__ == "__main__":
    main()
