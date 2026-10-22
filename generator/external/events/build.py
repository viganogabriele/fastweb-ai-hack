"""Build city / disruption event documents under generated/sources/external/events/.
Run: .venv/bin/python generator/external/events/build.py
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import disruptions  # noqa: E402
import hongkong  # noqa: E402
import rome  # noqa: E402
import venice  # noqa: E402

OUT = HERE.parents[2] / "generated" / "sources" / "external" / "events"

if __name__ == "__main__":
    for sub in ("municipal", "disruptions", "venice", "hongkong"):
        if (OUT / sub).exists():
            shutil.rmtree(OUT / sub)
    OUT.mkdir(parents=True, exist_ok=True)
    rome.build(OUT)
    disruptions.build(OUT)
    venice.build(OUT)
    hongkong.build(OUT)
    for p in sorted(OUT.rglob("*")):
        if p.is_file() and any(s in p.parts for s in ("municipal", "disruptions", "venice", "hongkong")):
            print(p.relative_to(OUT), p.stat().st_size)
