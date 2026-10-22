"""Regenerate all external sources (deterministic). Usage: .venv/bin/python generator/external/run_all.py
news/ and events documents and social/ have their own scripts in generator/external/news/build.py, events/build.py, social/make_social.py."""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
for mod in ("weather", "fx", "calendars", "events_feed", "tourism", "trends", "macro"):
    print("==>", mod)
    runpy.run_path(str(HERE / f"{mod}.py"), run_name="__main__")
