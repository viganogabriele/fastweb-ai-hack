"""Sanity checks for bodies_<STORE>.py (authoring aid).

- which open business days have no closing email (uses optional `day` key: "YYYY-MM-DD" or list of them)
- long identical character runs shared by 2+ bodies (possible template smell), excluding lines listed in
  the module-level ALLOWED_REPEATS (deliberate store habits such as a fixed form header / signature)
Usage: .venv/bin/python generator/emails_zh/check.py STORE [ngram_len]
"""
import importlib
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

store = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 16
mod = importlib.import_module(f"bodies_{store}")
ctx = json.load(open(os.path.join(ROOT, "generated", "ground_truth", "writer_inputs", "email_context", f"{store}.json")))
open_days = [d["date"] for d in ctx["days"] if d["open"]]

covered = set()
for e in mod.EMAILS:
    d = e.get("day")
    if d:
        covered.update([d] if isinstance(d, str) else d)
missing = [d for d in open_days if d not in covered]
print(f"{store}: {len(mod.EMAILS)} emails, {len(covered & set(open_days))}/{len(open_days)} open days covered")
print("  days without a closing email:", missing)

allowed = set(getattr(mod, "ALLOWED_REPEATS", []))


def clean(t):
    lines = [l for l in t.splitlines() if l.strip() and l.strip() not in allowed and not l.startswith(">")]
    return re.sub(r"\s+", "", "\n".join(lines))


grams = defaultdict(set)
for i, e in enumerate(mod.EMAILS):
    if e.get("suffix", "").startswith("_dup"):
        continue
    t = clean(e.get("body") or "")
    for k in range(0, max(0, len(t) - N + 1)):
        grams[t[k:k + N]].add(i)
rep = defaultdict(set)
for g, s in grams.items():
    if len(s) > 1:
        rep[frozenset(s)].add(g)
shown = 0
for s, gs in sorted(rep.items(), key=lambda x: -len(x[1])):
    print("  repeated", sorted(s), "e.g.", sorted(gs)[0])
    shown += 1
    if shown > 25:
        break
