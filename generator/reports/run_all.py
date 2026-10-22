"""Regenerate every report under generated/sources/reports/ and the answer key.

usage: .venv/bin/python generator/reports/run_all.py
"""
import importlib
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

MODULES = ["flash", "emea_mbr", "japan_report", "korea_report", "apac_review", "china_report", "americas_report",
           "merch_sellthrough", "agency_campaign", "market_research", "taxfree", "quality_report", "board_q3",
           "digital_weekly", "build_notes"]

if __name__ == "__main__":
    out = HERE.parents[1] / "generated" / "sources" / "reports"
    if "--clean" in sys.argv and out.exists():
        shutil.rmtree(out)
    for m in MODULES:
        print("->", m, flush=True)
        importlib.import_module(m).main()
    shutil.rmtree(HERE / "_tmp", ignore_errors=True)
