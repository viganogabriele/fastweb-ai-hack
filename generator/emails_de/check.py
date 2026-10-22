"""Sanity checks: long sentences repeated across different email bodies (except deliberate duplicates)."""
import re, sys, os
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mun01, ber01, zrh01, stm01

seen = defaultdict(list)
for mod in (mun01, ber01, zrh01, stm01):
    for e in mod.EMAILS:
        if e.get("sfx", "").startswith("_dup"):
            continue
        for s in re.split(r"[.!?\n]", e["body"]):
            s = s.strip()
            if len(s) >= 40:
                seen[s].append(f"{mod.__name__}:{e['id']}")
bad = {k: v for k, v in seen.items() if len(v) > 1}
for k, v in bad.items():
    print(v, k)
print("repeated long sentences:", len(bad))
