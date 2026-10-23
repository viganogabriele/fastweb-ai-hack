"""Shared helpers for the internal_comms generators (wrapping only: NO prose generation here).

Usage from a part script:
    import sys; sys.path.insert(0, "generator/internal_comms")
    from common import ROOT, OUT, person, make_eml, write_eml, check_texts
"""
import datetime as dt
import email.utils
import hashlib
import pathlib
import re
import unicodedata
from email.message import EmailMessage
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "generated" / "sources" / "internal_comms"
NOTES = ROOT / "generated" / "ground_truth" / "answer_keys" / "internal_comms_parts"
DOMAIN = "valentino-retail.example"

PEOPLE = {
    # area managers
    "galli": "Roberto Galli", "moreau": "Isabelle Moreau", "wagner": "Stefan Wagner", "mcleod": "Fiona McLeod",
    "haddad": "Omar Haddad", "mitchell": "Lauren Mitchell", "suzuki": ("鈴木 拓也", "takuya.suzuki"),
    "yoon": ("윤성호", "sungho.yoon"), "zhao": ("赵磊", "lei.zhao"), "lau": "Vivian Lau", "lim": "Daniel Lim",
    # directors / country managers
    "valli": "Francesca Valli", "ruggeri": "Carlo Ruggeri", "dubois": ("Hélène Dubois-Rey", "helene.dubois-rey"),
    "engel": "Markus Engel", "ashby": "Richard Ashby", "davidson": "Mark Davidson", "morita": ("森田 健二", "kenji.morita"),
    "kang": ("강민정", "minjung.kang"), "zhou": ("周雪", "xue.zhou"), "leung": "Andrew Leung",
    # HQ functions
    "bassi": "Chiara Bassi", "longo": "Davide Longo", "ferrari": "Luca Ferrari", "rinaldi": "Elena Rinaldi",
    "marchetti": "Sofia Marchetti", "colombo": "Matteo Colombo", "sala": "Giorgia Sala", "park_n": "Nicole Park",
    "sun": ("孙怡雯", "yiwen.sun"), "tsang": "Jason Tsang", "yamaguchi": ("山口 真理", "mari.yamaguchi"),
    "oh": ("오지은", "jieun.oh"), "nair": "Priya Nair",
}


def _ascii(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z.\-]", "", s.lower())


def person(key_or_name, addr_local=None):
    """Return 'Display Name <addr>' for a PEOPLE key or for an arbitrary 'First Last' name."""
    v = PEOPLE.get(key_or_name, key_or_name)
    if isinstance(v, tuple):
        name, local = v
    else:
        name = v
        parts = name.split()
        local = addr_local or (_ascii(parts[0]) + "." + _ascii("".join(parts[1:])) if len(parts) > 1 else _ascii(name))
    if addr_local:
        local = addr_local
    return f"{name} <{local}@{DOMAIN}>"


def make_eml(frm, to, subject, body, sent, tz="Europe/Rome", cc=None, html=None, attachments=None,
             in_reply_to=None, references=None, msgid_seed=None, extra_headers=None):
    """sent: 'YYYY-MM-DD HH:MM' local time in tz. attachments: list of (filename, bytes, maintype, subtype)."""
    m = EmailMessage()
    m["From"] = frm
    m["To"] = to if isinstance(to, str) else ", ".join(to)
    if cc:
        m["Cc"] = cc if isinstance(cc, str) else ", ".join(cc)
    m["Subject"] = subject
    t = dt.datetime.strptime(sent, "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo(tz))
    m["Date"] = email.utils.format_datetime(t)
    seed = msgid_seed or (frm + subject + sent)
    h = hashlib.md5(seed.encode()).hexdigest()
    m["Message-ID"] = f"<{h[:12]}.{h[12:20]}@{DOMAIN}>"
    if in_reply_to:
        m["In-Reply-To"] = in_reply_to
        m["References"] = references or in_reply_to
    for k, v in (extra_headers or {}).items():
        m[k] = v
    m.set_content(body)
    if html:
        m.add_alternative(html, subtype="html")
    for fn, data, mt, st in attachments or []:
        m.add_attachment(data, maintype=mt, subtype=st, filename=fn)
    return m


def msgid_of(m):
    return m["Message-ID"]


def write_eml(m, path):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes(m))
    return path


FORBIDDEN = [r"\bE\d\d[b]?\b", "ground truth", "synthetic", "simulat", "scenario", "I hope this", "In summary",
             "Overall,", "hope this email finds"]


def check_texts(named_texts, shingle=8, allow=()):
    """named_texts: dict name -> text. Prints forbidden-string hits and repeated 8-word shingles across texts."""
    problems = 0
    for n, t in named_texts.items():
        for pat in FORBIDDEN:
            if re.search(pat, t, flags=re.I if not pat.startswith("\\bE") else 0):
                print(f"FORBIDDEN {pat!r} in {n}")
                problems += 1
    seen = {}
    for n, t in named_texts.items():
        w = re.findall(r"\w+", t.lower())
        if len(w) < shingle:
            # CJK text has few spaces: use character n-grams instead
            w = list(re.sub(r"\s+", "", t))
            k = 20
        else:
            k = shingle
        for i in range(len(w) - k + 1):
            sh = " ".join(w[i:i + k])
            if any(a in sh for a in allow):
                continue
            if sh in seen and seen[sh] != n:
                print(f"REPEAT [{sh[:80]}] in {seen[sh]} and {n}")
                problems += 1
            seen.setdefault(sh, n)
    print(f"check_texts: {len(named_texts)} texts, {problems} problems")
    return problems
