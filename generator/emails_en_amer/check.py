"""Sanity checks on authored bodies. Usage: .venv/bin/python generator/emails_en_amer/check.py [STORE ...]

- forbidden strings (event codes, 'synthetic', AI-isms)
- em-dash density
- coverage: which business days have no email (should be ~5% on purpose)
- repeated 9-word sequences across all emails of the group (except lines listed in HABIT_LINES of the module)
"""
import importlib.util
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STORES = ["NYC01", "NYC02", "MIA01", "BHS01", "ASP01", "TOR01"]
FORBID = [r"\bE\d\d\b", r"synthetic", r"ground.truth", r"\bOverall,", r"In summary", r"hope this (e-?mail|message) finds",
          r"\bdelve", r"\bE0\d"]


def load(s):
    p = HERE / f"bodies_{s}.py"
    spec = importlib.util.spec_from_file_location(p.stem, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def words(t):
    return re.findall(r"[a-z0-9']+", t.lower())


def main(stores):
    grams = defaultdict(set)
    for s in [x for x in STORES if (HERE / f"bodies_{x}.py").exists()]:
        m = load(s)
        habit = [h.lower() for h in getattr(m, "HABIT_LINES", [])]
        for e in m.EMAILS:
            if e.get("suffix", "").startswith("_dup"):
                continue
            text = e["body"].split("-----Original Message-----")[0].split("---------- Forwarded message")[0]
            text = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith(">"))
            for h in habit:
                text = text.lower().replace(h, " ")
            w = words(text)
            for i in range(len(w) - 8):
                grams[" ".join(w[i:i + 9])].add(f"{s}:{e['key']}")
    for s in stores:
        m = load(s)
        print(f"== {s}: {len(m.EMAILS)} emails")
        for e in m.EMAILS:
            for f in FORBID:
                if re.search(f, e["body"] + e["subject"]):
                    print("  FORBIDDEN", f, "in", e["key"])
            if e["body"].count("—") > 1:
                print("  em-dashes:", e["key"], e["body"].count("—"))
        ctx = json.load(open(ROOT / f"generated/ground_truth/writer_inputs/email_context/{s}.json"))["days"]
        covered = set()
        for e in m.EMAILS:
            for d in e.get("covers", []):
                covered.add(d)
        missing = [d["date"] for d in ctx if d["open"] and d["date"] not in covered]
        print("  days without own email (check 'covers'):", missing)
        dup = {g: k for g, k in grams.items() if len(k) > 1 and any(x.startswith(s + ":") for x in k)}
        # collapse overlapping grams
        seen = set()
        for g, k in sorted(dup.items(), key=lambda x: sorted(x[1])):
            kk = tuple(sorted(k))
            if kk in seen:
                continue
            seen.add(kk)
            print("  REPEATED:", kk, "->", g)


if __name__ == "__main__":
    main(sys.argv[1:] or [s for s in STORES if (HERE / f"bodies_{s}.py").exists()])
