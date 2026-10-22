"""Wrap hand-authored Korean closing-email bodies (generator/emails_ko/bodies/<STORE>.py) into .eml files.

Usage: .venv/bin/python generator/emails_ko/build_eml.py [STORE ...]   (default: SEL01 SEL02 BUS01)

Each bodies module defines:
  PERSONAS     dict key -> "Display Name <addr>"
  DEFAULT_TO   list of persona keys / literal addresses
  DEFAULT_CC   list of persona keys / literal addresses
  EMAILS       list of dicts, keys:
      id            unique key (Message-ID + threading)
      sent          "YYYY-MM-DD HH:MM" local time (Asia/Seoul, +09:00)
      frm           persona key or literal "Name <addr>"
      subject       str
      body          str (text/plain) -- hand written, never generated from data
      to, cc        optional lists (override defaults)
      reply_to_id   optional id of the email this one answers (In-Reply-To / References)
      suffix        optional filename suffix: "_re1", "_dup", "_fwd", "_corr", "_ooo" ...
      html          optional str: HTML alternative (multipart/alternative)
      charset       optional body charset (default utf-8; some PCs send euc-kr)
      attachments   optional list of {"name": "IMG_4471.jpg"} (placeholder jpeg) |
                    {"name": "x.csv", "content": "...", "encoding": "cp949"} | {"name": "x.xlsx", "rows": [[...]]}
      business_date optional "YYYY-MM-DD" (or comma list) reported day(s) -- answer key only, not in the .eml
      kind          optional label for the index (closing, reply, dup, correction, ooo, fwd, misc)
      headers       optional dict of extra headers
      mailer        optional X-Mailer override
"""
import csv
import hashlib
import importlib.util
import io
import sys
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import format_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BODIES = Path(__file__).resolve().parent / "bodies"
OUT = ROOT / "generated" / "sources" / "store_emails"
INDEX = ROOT / "generated" / "ground_truth" / "answer_keys" / "emails" / "emails_ko_index.csv"
GROUP = ["SEL01", "SEL02", "BUS01"]
TZ = timezone(timedelta(hours=9))  # KST, no DST
DOMAIN = "moncler-retail.example"


def load(store):
    spec = importlib.util.spec_from_file_location(f"bodies_{store}", BODIES / f"{store}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def msgid(store, key, mailer):
    h = hashlib.sha1(f"ko:{store}:{key}".encode()).hexdigest().upper()
    if "iPhone" in mailer:
        return f"<{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}@{DOMAIN}>"
    if "Samsung" in mailer:
        return f"<{h[:20].lower()}.sm@{DOMAIN}>"
    return f"<SL2P216MB{h[:4]}{h[4:20]}@SL2P216MB{h[:4]}.KORP216.PROD.OUTLOOK.COM>"


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
    ws.title = "Sheet1"
    for r in rows:
        ws.append(list(r))
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


def addr(mod, x):
    return mod.PERSONAS.get(x, x)


def pick_mailer(e):
    if e.get("mailer"):
        return e["mailer"]
    b = e["body"]
    if "iPhone에서 보냄" in b or "Sent from my iPhone" in b:
        return "iPhone Mail (22A3354)"
    if "Galaxy" in b:
        return "Samsung Mail"
    return "Microsoft Outlook 16.0"


def build_store(store):
    mod = load(store)
    out = OUT / store
    out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*.eml"):
        f.unlink()
    ids = {e["id"]: e for e in mod.EMAILS}
    assert len(ids) == len(mod.EMAILS), f"duplicate ids in {store}"
    rows, names = [], set()
    for e in mod.EMAILS:
        mailer = pick_mailer(e)
        m = EmailMessage()
        dt = datetime.strptime(e["sent"], "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
        dt = dt.replace(second=int(hashlib.md5(e["id"].encode()).hexdigest()[:4], 16) % 60)
        m["From"] = addr(mod, e["frm"])
        m["To"] = ", ".join(addr(mod, x) for x in e.get("to", mod.DEFAULT_TO))
        cc = e.get("cc", mod.DEFAULT_CC)
        if cc:
            m["Cc"] = ", ".join(addr(mod, x) for x in cc)
        m["Subject"] = e["subject"]
        m["Date"] = format_datetime(dt)
        m["Message-ID"] = msgid(store, e["id"], mailer)
        if e.get("reply_to_id"):
            chain, p = [], e["reply_to_id"]
            while p:
                chain.append(msgid(store, p, pick_mailer(ids[p])) if p in ids else f"<{p}@{DOMAIN}>")
                p = ids[p].get("reply_to_id") if p in ids else None
            m["In-Reply-To"] = chain[0]
            m["References"] = " ".join(reversed(chain))
        for k, v in (e.get("headers") or {}).items():
            m[k] = v
        m["X-Mailer"] = mailer
        m.set_content(e["body"], charset=e.get("charset", "utf-8"))
        if e.get("html"):
            m.add_alternative(e["html"], subtype="html", charset=e.get("charset", "utf-8"))
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
