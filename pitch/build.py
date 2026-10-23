"""Render pitch/src/*.html to dark-mode PDFs in pitch/ with headless Chrome.

Usage: python3 pitch/build.py [name ...]   (no args = every document)
Set CHROME=/path/to/chrome if it is not found automatically.
"""

import glob
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "src"


def find_chrome() -> str:
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        if path := shutil.which(name):
            return path
    cache = Path.home() / ".cache/ms-playwright"
    for pattern in ("chromium_headless_shell-*/*/chrome-headless-shell", "chromium-*/*/chrome"):
        if hits := sorted(glob.glob(str(cache / pattern))):
            return hits[-1]
    mac = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if Path(mac).exists():
        return mac
    sys.exit("Chrome not found: set CHROME=/path/to/chrome")


def run(chrome: str, *args: str) -> str:
    cmd = [chrome, "--headless", "--disable-gpu", "--virtual-time-budget=5000", *args]
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def main() -> None:
    chrome = find_chrome()
    wanted = set(sys.argv[1:])
    failed = False
    for html in sorted(SRC.glob("[0-9]*.html")):
        if wanted and html.stem not in wanted:
            continue
        url = html.as_uri()
        dom = run(chrome, "--dump-dom", url)
        overflow = re.search(r'data-overflow="([^"]*)"', dom)
        if overflow is None or 'data-ready="1"' not in dom:
            print(f"{html.name}: page script did not finish")
            failed = True
        elif overflow.group(1):
            print(f"{html.name}: content overflows on page(s) {overflow.group(1)}")
            failed = True
        out = HERE / f"{html.stem}.pdf"
        run(chrome, "--no-pdf-header-footer", f"--print-to-pdf={out}", url)
        print(f"wrote {out.relative_to(HERE.parent)}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
