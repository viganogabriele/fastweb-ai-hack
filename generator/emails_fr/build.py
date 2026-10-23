"""Wrap the hand-authored French closing emails (par01.py, par02.py, can01.py, gva01.py) into .eml files.

Bodies are authored one by one in the store modules; this script only adds headers, signatures, quoting,
attachments and writes RFC-822 files to generated/sources/store_emails/<STORE>/.

Run:  .venv/bin/python generator/emails_fr/build.py
"""
import csv
import datetime as dt
import hashlib
import importlib
import io
import shutil
import sys
from email import policy as _policy
from email.message import EmailMessage
from email.utils import format_datetime, formataddr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "generated" / "sources" / "store_emails"
sys.path.insert(0, str(Path(__file__).resolve().parent))

DOMAIN = "valentino-retail.example"
TZ = dt.timezone(dt.timedelta(hours=2))  # CEST for Paris/Cannes/Genève over the whole window (DST ends Oct 25)

POLICY = _policy.default.clone(max_line_length=998)
INDEX = ROOT / "generated" / "ground_truth" / "answer_keys" / "emails" / "emails_fr_index.csv"

# business date(s) covered when different from the sending date (late sends, recaps, corrections)
BD_OVERRIDE = {
    ("PAR01", "0917"): "2026-09-17;2026-09-16", ("PAR01", "0926r"): "2026-09-19..2026-09-25",
    ("PAR01", "1007"): "2026-10-07", ("PAR01", "1009f"): "", ("PAR01", "1002c"): "2026-10-02",
    ("PAR02", "1011"): "2026-10-10;2026-10-11", ("PAR02", "1017"): "2026-10-17;2026-10-16", ("PAR02", "1012f"): "2026-10-13",
    ("PAR02", "0925m"): "",
    ("CAN01", "1013"): "2026-10-12;2026-10-13", ("CAN01", "0914i"): "2026-09-12", ("CAN01", "0914r"): "2026-09-12",
    ("CAN01", "0912f"): "",
    ("GVA01", "0926c"): "2026-09-25", ("GVA01", "1017f"): "2026-10-16", ("GVA01", "0918"): "2026-09-18",
    ("GVA01", "1007i"): "",
}
KIND = {"": "closing", "_re1": "reply", "_re2": "reply", "_dup": "duplicate", "_corr": "correction",
        "_fwd": "forward", "_auto": "auto_reply"}
INDEX_ROWS = []
STORE_MODULES = ["par01", "par02", "can01", "gva01"]


def placeholder_jpeg(seed: str) -> bytes:
    from PIL import Image
    h = hashlib.md5(seed.encode()).digest()
    img = Image.new("RGB", (64, 48), (h[0], h[1], h[2]))
    for x in range(0, 64, 8):
        for y in range(48):
            img.putpixel((x, y), (h[3], h[4], h[5]))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=60)
    return buf.getvalue()


def make_xlsx(rows) -> bytes:
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Cloture"
    for r in rows:
        ws.append(list(r))
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def make_csv(rows, sep=";") -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=sep, lineterminator="\r\n")
    for r in rows:
        w.writerow(r)
    return buf.getvalue().encode("cp1252", errors="replace")


def msgid(store, key):
    h = hashlib.sha1(f"{store}-{key}".encode()).hexdigest()[:20].upper()
    return f"<{h}.{store.lower()}@{DOMAIN}>"


def quote(parent_body, who_line):
    lines = parent_body.rstrip("\n").split("\n")
    return "\n\n" + who_line + "\n" + "\n".join("> " + l if l else ">" for l in lines)


def fr_when(d: dt.datetime):
    jours = ["lun.", "mar.", "mer.", "jeu.", "ven.", "sam.", "dim."]
    mois = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
    return f"{jours[d.weekday()]} {d.day} {mois[d.month-1]} {d.year} à {d.strftime('%H:%M')}"


def build_store(modname):
    mod = importlib.import_module(modname)
    store = mod.STORE
    people = mod.PEOPLE
    outdir = OUT / store
    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True)
    by_id = {}
    n = 0
    for e in mod.EMAILS:
        p = people[e["who"]]
        when = dt.datetime.strptime(f"{e['d']} {e['t']}", "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
        sec = int(hashlib.md5((store + e["id"]).encode()).hexdigest(), 16) % 60
        when = when.replace(second=sec)
        mid = msgid(store, e["id"])
        subj = e.get("subj")
        parent = by_id.get(e.get("reply_to")) if e.get("reply_to") else None
        if subj is None and parent is not None:
            base = parent["subj"]
            if base.lower().startswith(("re:", "tr:", "fwd:")):
                subj = base
            else:
                subj = ("RE: " if p.get("outlook") else "Re: ") + base
        body = e["body"].strip("\n") + "\n"
        sig = e.get("sig", p.get("sig"))
        if sig:
            body += "\n" + sig.strip("\n") + "\n"
        if parent is not None and e.get("quote", True):
            pp = people[parent["who"]]
            body += quote(parent["full_body"], f"Le {fr_when(parent['when'])}, {pp['name']} <{pp['email']}> a écrit :")
        if e.get("fwd"):
            body += "\n\n" + e["fwd"].strip("\n") + "\n"
        msg = EmailMessage(policy=POLICY)
        msg["From"] = formataddr((p["name"], p["email"])) if p.get("name") else p["email"]
        msg["To"] = ", ".join(e.get("to", mod.TO))
        cc = e.get("cc", mod.CC)
        if cc:
            msg["Cc"] = ", ".join(cc)
        msg["Subject"] = subj
        msg["Date"] = format_datetime(when)
        msg["Message-ID"] = mid
        if parent is not None:
            msg["In-Reply-To"] = parent["mid"]
            msg["References"] = (parent.get("refs", "") + " " + parent["mid"]).strip()
        if p.get("mailer"):
            msg["X-Mailer"] = p["mailer"]
        if e.get("auto"):
            msg["Auto-Submitted"] = "auto-replied"
            msg["X-Auto-Response-Suppress"] = "All"
        msg["Content-Language"] = e.get("lang", "fr-FR" if store != "GVA01" else "fr-CH")
        msg.set_content(body)
        if e.get("html"):
            msg.add_alternative(e["html"], subtype="html")
        for att in e.get("attach", []):
            kind, fname = att[0], att[1]
            if kind == "jpg":
                msg.add_attachment(placeholder_jpeg(store + fname), maintype="image", subtype="jpeg", filename=fname)
            elif kind == "csv":
                msg.add_attachment(make_csv(att[2]), maintype="text", subtype="csv", filename=fname)
            elif kind == "xlsx":
                msg.add_attachment(make_xlsx(att[2]), maintype="application",
                                   subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=fname)
        fname = f"{when.strftime('%Y%m%d_%H%M')}_{store}{e.get('suffix', '')}.eml"
        assert not (outdir / fname).exists(), fname
        (outdir / fname).write_bytes(bytes(msg))
        suf = e.get("suffix", "")
        kind = KIND.get(suf, "other")
        if store == "GVA01" and e["id"] == "1016":
            kind = "closing_wrong_list"
        INDEX_ROWS.append([store, fname, e["id"], when.strftime("%Y-%m-%d %H:%M"),
                           BD_OVERRIDE.get((store, e["id"]), e["d"] if kind == "closing" or kind == "closing_wrong_list" else ""),
                           kind, msg["From"], subj])
        by_id[e["id"]] = dict(subj=subj, mid=mid, when=when, who=e["who"], full_body=body,
                              refs=(msg["References"] or ""))
        n += 1
    return store, n


if __name__ == "__main__":
    for m in STORE_MODULES:
        s, n = build_store(m)
        print(s, n)
    with open(INDEX, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["store", "file", "id", "sent", "business_date", "kind", "frm", "subject"])
        w.writerows(INDEX_ROWS)
