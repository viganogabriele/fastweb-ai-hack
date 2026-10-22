"""Sanity checks on authored Korean bodies.

.venv/bin/python generator/emails_ko/check.py [STORE ...]
- coverage: open days without an email whose business_date covers them
- repeated 6-token shingles across different bodies (Korean eojeol are long, so n=6), within and across stores
- forbidden strings (event codes, 'synthetic', 'ground truth')
- euc-kr encodability for emails flagged with a legacy charset
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_eml import GROUP, BODIES, ROOT, load  # noqa: E402

FORBID = re.compile(r"\bE\d{2}b?\b|synthetic|ground.truth|합성|시뮬레이", re.I)


def shingles(text, n=6):
    w = re.findall(r"\w+", text.lower())
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def main():
    stores = sys.argv[1:] or [s for s in GROUP if (BODIES / f"{s}.py").exists()]
    owner = defaultdict(set)
    for s in stores:
        mod = load(s)
        ctx = json.load(open(ROOT / f"generated/ground_truth/writer_inputs/email_context/{s}.json"))
        open_days = [d["date"] for d in ctx["days"] if d["open"]]
        covered = set()
        for e in mod.EMAILS:
            for bd in (e.get("business_date") or "").split(","):
                if bd.strip():
                    covered.add(bd.strip())
            txt = e["body"] + e["subject"]
            if FORBID.search(txt):
                print(f"[{s}] FORBIDDEN in {e['id']}: {FORBID.search(txt).group(0)}")
            if e.get("charset"):
                try:
                    e["body"].encode(e["charset"])
                except UnicodeEncodeError as x:
                    print(f"[{s}] CHARSET {e['id']}: {x}")
            if e.get("kind") in ("dup",):
                continue
            for sh in shingles(e["body"]):
                owner[sh].add(f"{s}:{e['id']}")
        miss = [d for d in open_days if d not in covered]
        print(f"[{s}] emails={len(mod.EMAILS)} open_days={len(open_days)} uncovered={len(miss)} {miss}")
    rep = {k: v for k, v in owner.items() if len(v) > 1}
    by_pair = defaultdict(list)
    for k, v in rep.items():
        by_pair[tuple(sorted(v))].append(k)
    for pair, shs in sorted(by_pair.items(), key=lambda x: -len(x[1]))[:40]:
        print(f"REPEAT x{len(shs)} {pair}: '{shs[0]}'")


if __name__ == "__main__":
    main()
