"""Wrap the hand-authored closing emails (bodies_<STORE>.py) into RFC-822 .eml files.

Usage: .venv/bin/python generator/emails_en_amer/build.py [STORE ...]

Each bodies_<STORE>.py defines:
    STORE = "NYC01"
    WRITERS = {"rs": "Rebecca Stein <rebecca.stein@moncler-retail.example>", ...}
    DEFAULT_TO = ["retail-ops-usa@moncler-retail.example"]
    DEFAULT_CC = ["Lauren Mitchell <lauren.mitchell@moncler-retail.example>"]
    EMAILS = [dict(...), ...]

Email dict keys:
    key      unique id inside the store (used for threading)            [required]
    sent     local send time "YYYY-MM-DD HH:MM" (store timezone)         [required]
    frm      writer key from WRITERS, or a full "Name <addr>" string     [required]
    subject                                                             [required]
    body     text/plain body (authored by hand)                          [required]
    to, cc   lists overriding the defaults (cc=[] for none)
    suffix   filename suffix e.g. "_re1", "_fwd", "_dup", "_corr"
    reply_to key of the email this one answers (sets In-Reply-To/References)
    html     optional HTML alternative (multipart/alternative)
    attach   list of {"name": "IMG_4471.jpg"} | {"name": "x.csv", "text": "..."} |
             {"name": "x.xlsx", "rows": [[...], ...]}
    mailer   "iphone" | "outlook" | "android" | None  (adds X-Mailer header)
    tz       override timezone (e.g. writer travelling / area manager in another tz)
    extra_headers  dict of additional headers (e.g. Auto-Submitted for OOO)
"""
import hashlib
import importlib.util
import io
import sys
from datetime import datetime
from email.message import EmailMessage
from email.utils import format_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "generated" / "sources" / "store_emails"

TZ = {
    "NYC01": "America/New_York", "NYC02": "America/New_York", "MIA01": "America/New_York",
    "BHS01": "America/Los_Angeles", "ASP01": "America/Denver", "TOR01": "America/Toronto",
}
MAILERS = {
    "iphone": "iPhone Mail (23A341)",
    "outlook": "Microsoft Outlook 16.0",
    "android": "Outlook for Android",
}

# smallest valid JPEG-ish placeholder (1x1 px grey)
_JPEG = bytes.fromhex(
    "ffd8ffe000104a46494600010100000100010000ffdb004300080606070605080707070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720"
    "222c231c1c2837292c30313434341f27393d38323c2e333432ffc0000b080001000101011100ffc4001f0000010501010101010100000000000000000102030405"
    "060708090a0bffc400b5100002010303020403050504040000017d01020300041105122131410613516107227114328191a1082342b1c11552d1f02433627282090a"
    "161718191a25262728292a3435363738393a434445464748494a535455565758595a636465666768696a737475767778797a838485868788898a92939495969798999a"
    "a2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9faffda0008010100003f00"
    "fbd3ffd9"
)


def _msgid(store, key):
    h = hashlib.sha1(f"{store}|{key}".encode()).hexdigest().upper()
    n = int(h[:2], 16) % 9 + 1
    return f"<{['BN', 'CY4', 'SJ0', 'MN2'][int(h[2], 16) % 4]}PR{n}1MB{h[3:7]}{h[7:19]}@moncler-retail.example>"


def _load(store):
    p = HERE / f"bodies_{store}.py"
    spec = importlib.util.spec_from_file_location(f"bodies_{store}", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _xlsx(rows):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    for r in rows:
        ws.append(r)
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


def build(store):
    m = _load(store)
    out = OUT / store
    out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*.eml"):
        f.unlink()
    byk = {e["key"]: e for e in m.EMAILS}
    assert len(byk) == len(m.EMAILS), f"{store}: duplicate keys"
    used = set()
    for e in m.EMAILS:
        tz = ZoneInfo(e.get("tz") or TZ[store])
        dt = datetime.strptime(e["sent"], "%Y-%m-%d %H:%M").replace(tzinfo=tz)
        sec = int(hashlib.md5(e["key"].encode()).hexdigest()[:2], 16) % 60
        dt = dt.replace(second=sec)
        msg = EmailMessage()
        frm = m.WRITERS.get(e["frm"], e["frm"])
        msg["From"] = frm
        msg["To"] = ", ".join(e.get("to", m.DEFAULT_TO))
        cc = e.get("cc", m.DEFAULT_CC)
        if cc:
            msg["Cc"] = ", ".join(cc)
        msg["Subject"] = e["subject"]
        msg["Date"] = format_datetime(dt)
        msg["Message-ID"] = _msgid(store, e["key"])
        if e.get("reply_to"):
            parent = byk[e["reply_to"]]
            refs = []
            p = parent
            while p is not None:
                refs.insert(0, _msgid(store, p["key"]))
                p = byk.get(p.get("reply_to")) if p.get("reply_to") else None
            msg["In-Reply-To"] = _msgid(store, parent["key"])
            msg["References"] = " ".join(refs)
        if e.get("mailer"):
            msg["X-Mailer"] = MAILERS.get(e["mailer"], e["mailer"])
        for k, v in (e.get("extra_headers") or {}).items():
            msg[k] = v
        msg["Content-Language"] = "en-US" if store != "TOR01" else "en-CA"
        msg.set_content(e["body"].strip("\n") + "\n")
        if e.get("html"):
            msg.add_alternative(e["html"], subtype="html")
        for a in e.get("attach", []):
            name = a["name"]
            if name.lower().endswith((".jpg", ".jpeg")):
                msg.add_attachment(_JPEG, maintype="image", subtype="jpeg", filename=name)
            elif name.lower().endswith(".csv"):
                msg.add_attachment(a["text"].encode("utf-8"), maintype="text", subtype="csv", filename=name)
            elif name.lower().endswith(".xlsx"):
                msg.add_attachment(_xlsx(a["rows"]), maintype="application",
                                   subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=name)
            elif name.lower().endswith(".pdf") or name.lower().endswith(".txt"):
                msg.add_attachment(a.get("text", "").encode(), maintype="application", subtype="octet-stream", filename=name)
            else:
                raise ValueError(name)
        local = dt.strftime("%Y%m%d_%H%M")
        fname = f"{local}_{store}{e.get('suffix', '')}"
        i = 2
        base = fname
        while fname in used:
            fname = f"{base}_{i}"
            i += 1
        used.add(fname)
        (out / f"{fname}.eml").write_bytes(bytes(msg))
    return len(m.EMAILS)


if __name__ == "__main__":
    stores = sys.argv[1:] or list(TZ)
    for s in stores:
        if not (HERE / f"bodies_{s}.py").exists():
            print(s, "no bodies file yet")
            continue
        print(s, build(s), "emails")
