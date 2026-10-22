"""Sanity checks: parse all .eml, coverage of open days, repeated long sentences across emails."""
import email, glob, json, os, re, collections
from email import policy
ROOT = "generated/sources/store_emails"
STORES = ["LON01", "LON02", "AMS01", "CPH01", "DXB01", "SIN01", "SYD01"]
sent = collections.defaultdict(list)
for s in STORES:
    files = sorted(glob.glob(f"{ROOT}/{s}/*.eml"))
    days = set()
    for f in files:
        m = email.message_from_bytes(open(f, "rb").read(), policy=policy.default)
        b = m.get_body(preferencelist=("plain",)).get_content()
        b = b.split("\n> On ")[0].split("________________________________")[0]
        name = os.path.basename(f)
        if "_dup" not in name:
            for line in re.split(r"[\n.!?]", b):
                line = line.strip().lower()
                if len(line) > 45:
                    sent[line].append(name)
        days.add(name[:8])
    ctx = json.load(open(f"generated/ground_truth/writer_inputs/email_context/{s}.json"))
    open_days = {d["date"].replace("-", "") for d in ctx["days"] if d["open"]}
    print(s, len(files), "files; open days", len(open_days), "; open days w/o any email that day:", sorted(open_days - days))
rep = {k: v for k, v in sent.items() if len(v) > 1}
print("repeated long lines:", len(rep))
for k, v in list(rep.items())[:30]:
    print(" ", repr(k[:90]), v[:3])
