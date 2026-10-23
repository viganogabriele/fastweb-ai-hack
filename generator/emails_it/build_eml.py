"""Wrap hand-authored email bodies (generator/emails_it/bodies/<STORE>.py) into .eml files.

Usage: .venv/bin/python generator/emails_it/build_eml.py [STORE ...]   (default: all stores in the group)

Each bodies module defines:
  PERSONAS     dict key -> "Display Name <addr>"
  DEFAULT_TO   list of addresses
  DEFAULT_CC   list of addresses
  EMAILS       list of dicts, keys:
      id            unique key (used for Message-ID + threading)
      sent          "YYYY-MM-DD HH:MM" local time (Europe/Rome or Europe/Madrid, CEST +02:00 in the whole window)
      frm           persona key or literal "Name <addr>"
      subject       str
      body          str (text/plain)
      to, cc        optional lists (override defaults); to may be persona keys or literals
      reply_to_id   optional id of the email this one answers (In-Reply-To / References)
      suffix        optional filename suffix: "_re1", "_dup", "_fwd", "_corr", ...
      html          optional str: HTML alternative (multipart/alternative)
      attachments   optional list of {"name": "IMG_4471.jpg"} (placeholder jpeg) |
                    {"name": "x.csv", "content": "..."} | {"name": "x.xlsx", "rows": [[...], ...]}
      business_date optional "YYYY-MM-DD" reported day(s) (answer key only, NOT written in the .eml)
      kind          optional label for the index (closing, reply, dup, correction, ooo, fwd, misc)
      headers       optional dict of extra headers (e.g. {"Auto-Submitted": "auto-replied"})
"""
import csv
import hashlib
import importlib.util
import io
import sys
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import format_datetime, make_msgid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BODIES = Path(__file__).resolve().parent / "bodies"
OUT = ROOT / "generated" / "sources" / "store_emails"
INDEX = ROOT / "generated" / "ground_truth" / "answer_keys" / "emails" / "emails_it_index.csv"
GROUP = ["MIL01", "MIL02", "ROM01", "VEN01", "CRT01", "COU01", "MAD01"]
TZ = timezone(timedelta(hours=2))  # CEST, valid for both Rome and Madrid until Oct 25 2026
DOMAIN = "valentino-retail.example"


def load(store):
    spec = importlib.util.spec_from_file_location(f"bodies_{store}", BODIES / f"{store}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def msgid(store, key):
    h = hashlib.sha1(f"{store}:{key}".encode()).hexdigest()
    return f"<{h[:12]}.{h[12:20]}@{DOMAIN}>" if not key.startswith("ext:") else f"<{h[:16]}@mail.example>"


_JPEG = None


def placeholder_jpeg(name):
    from PIL import Image, ImageDraw
    seed = int(hashlib.md5(name.encode()).hexdigest()[:6], 16)
    img = Image.new("RGB", (160, 120), (90 + seed % 60, 90 + (seed >> 6) % 60, 90 + (seed >> 12) % 60))
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, 150, 110], outline=(200, 200, 200))
    d.text((20, 50), name[:20], fill=(240, 240, 240))
    b = io.BytesIO()
    img.save(b, "JPEG", quality=60)
    return b.getvalue()


def xlsx_bytes(rows):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Foglio1"
    for r in rows:
        ws.append(list(r))
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


def addr(mod, x):
    return mod.PERSONAS.get(x, x)


def build_store(store):
    mod = load(store)
    out = OUT / store
    out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*.eml"):
        f.unlink()
    ids = {e["id"]: e for e in mod.EMAILS}
    assert len(ids) == len(mod.EMAILS), f"duplicate ids in {store}"
    rows = []
    names = set()
    for e in mod.EMAILS:
        m = EmailMessage()
        dt = datetime.strptime(e["sent"], "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
        sec = int(hashlib.md5(e["id"].encode()).hexdigest()[:4], 16) % 60
        dt = dt.replace(second=sec)
        m["From"] = addr(mod, e["frm"])
        m["To"] = ", ".join(addr(mod, x) for x in e.get("to", mod.DEFAULT_TO))
        cc = e.get("cc", mod.DEFAULT_CC)
        if cc:
            m["Cc"] = ", ".join(addr(mod, x) for x in cc)
        m["Subject"] = e["subject"]
        m["Date"] = format_datetime(dt)
        m["Message-ID"] = msgid(store, e["id"])
        if e.get("reply_to_id"):
            chain = []
            p = e["reply_to_id"]
            while p:
                chain.append(msgid(store, p))
                p = ids[p].get("reply_to_id") if p in ids else None
            m["In-Reply-To"] = chain[0]
            m["References"] = " ".join(reversed(chain))
        for k, v in (e.get("headers") or {}).items():
            m[k] = v
        m["X-Mailer"] = e.get("mailer", "iPhone Mail (21G93)" if "iPhone" in e["body"] else "Microsoft Outlook 16.0")
        m.set_content(e["body"], charset="utf-8")
        if e.get("html"):
            m.add_alternative(e["html"], subtype="html", charset="utf-8")
        for a in e.get("attachments", []):
            n = a["name"]
            if n.lower().endswith((".jpg", ".jpeg")):
                m.add_attachment(placeholder_jpeg(n), maintype="image", subtype="jpeg", filename=n)
            elif n.lower().endswith(".csv"):
                m.add_attachment(a["content"].encode(a.get("encoding", "utf-8")), maintype="text", subtype="csv",
                                 filename=n)
            elif n.lower().endswith(".xlsx"):
                m.add_attachment(xlsx_bytes(a["rows"]), maintype="application",
                                 subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=n)
            elif n.lower().endswith(".pdf"):
                m.add_attachment(a.get("bytes", b"%PDF-1.4\n%placeholder\n"), maintype="application",
                                 subtype="pdf", filename=n)
            else:
                m.add_attachment(a.get("content", "").encode(), maintype="application", subtype="octet-stream",
                                 filename=n)
        fname = f"{dt:%Y%m%d}_{dt:%H%M}_{store}{e.get('suffix', '')}.eml"
        i = 2
        while fname in names:
            fname = f"{dt:%Y%m%d}_{dt:%H%M}_{store}{e.get('suffix', '')}_{i}.eml"
            i += 1
        names.add(fname)
        (out / fname).write_bytes(bytes(m))
        rows.append(dict(store=store, file=fname, id=e["id"], sent=e["sent"], business_date=e.get("business_date", ""),
                         kind=e.get("kind", "closing"), frm=m["From"], subject=e["subject"]))
    return rows


def main():
    stores = sys.argv[1:] or [s for s in GROUP if (BODIES / f"{s}.py").exists()]
    allrows = []
    if INDEX.exists():
        with open(INDEX, newline="", encoding="utf-8") as f:
            allrows = [r for r in csv.DictReader(f) if r["store"] not in stores]
    for s in stores:
        r = build_store(s)
        print(s, len(r), "emails")
        allrows += r
    allrows.sort(key=lambda r: (r["store"], r["sent"]))
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["store", "file", "id", "sent", "business_date", "kind", "frm", "subject"])
        w.writeheader()
        w.writerows(allrows)


if __name__ == "__main__":
    main()
