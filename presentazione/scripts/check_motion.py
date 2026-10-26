#!/usr/bin/env python3
"""Check motion startup and pause/resume in Firefox or Chromium with Playwright.

uv run --no-project --with playwright python presentazione/scripts/check_motion.py
Pass --browser chromium or --executable /path/to/browser as needed.
"""

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

ERRORS = """(() => {
  window.motionErrors = [];
  addEventListener('error', event => window.motionErrors.push(event.message));
})()"""

# Firefox can deliver the previous frame's timestamp to a newly registered callback.
EARLY_FRAME = """(() => {
  const nativeFrame = requestAnimationFrame.bind(window);
  let first = true;
  window.requestAnimationFrame = callback => {
    if (!first) return nativeFrame(callback);
    first = false;
    const previousFrame = Math.max(0, performance.now() - 20);
    return nativeFrame(() => callback(previousFrame));
  };
})()"""


def assert_moving(page, scene):
    selector = f"#{scene} [data-particles] circle"
    page.wait_for_function(
        "scene => document.querySelector('.scene.active')?.id === scene",
        arg=scene,
    )
    initial = page.locator(selector).first.get_attribute("cx")
    page.wait_for_function(
        """({selector, initial}) => {
          if (window.motionErrors.length) return true;
          const dot = document.querySelector(selector);
          const x = dot?.getAttribute('cx');
          return x !== null && x !== initial && Number.isFinite(Number(x));
        }""",
        arg={"selector": selector, "initial": initial},
    )
    errors = page.evaluate("window.motionErrors")
    assert not errors, f"{scene}: {errors}"
    assert page.locator(selector).first.evaluate(
        "dot => getComputedStyle(dot.parentElement).display !== 'none'"
    ), f"{scene}: moving particles are hidden"


def check(browser, url, early_frame):
    context = browser.new_context(
        viewport={"width": 1600, "height": 900}, reduced_motion="no-preference"
    )
    context.add_init_script(ERRORS)
    if early_frame:
        context.add_init_script(EARLY_FRAME)
    page = context.new_page()
    page.set_default_timeout(5000)
    try:
        page.goto(url + "#4")
        assert_moving(page, "percorso")
        page.goto(url)
        page.keyboard.press("ArrowRight")
        assert_moving(page, "il-negozio-sa")
        page.keyboard.press("ArrowRight")
        page.keyboard.press("ArrowRight")
        assert_moving(page, "percorso")
        page.evaluate("location.hash = '#9'")
        assert_moving(page, "agenti")

        page.keyboard.press("m")
        page.wait_for_function("document.documentElement.classList.contains('static')")
        frozen = page.locator("#agenti [data-particles] circle").first.get_attribute(
            "cx"
        )
        page.evaluate(
            "new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))"
        )
        assert (
            page.locator("#agenti [data-particles] circle").first.get_attribute("cx")
            == frozen
        )
        page.keyboard.press("m")
        assert_moving(page, "agenti")

        page.emulate_media(reduced_motion="reduce")
        page.wait_for_function(
            "getComputedStyle(document.querySelector('#agenti [data-particles]')).display === 'none'"
        )
        page.emulate_media(reduced_motion="no-preference")
        assert_moving(page, "agenti")

        page.goto(url + "?static#4")
        assert page.locator("#percorso [data-particles]").evaluate(
            "layer => getComputedStyle(layer).display === 'none'"
        )
        assert not page.evaluate("window.motionErrors")
        mode = "previous-frame timestamp" if early_frame else "native timestamps"
        print(
            f"PASS: {mode}, automatic startup, navigation, pause/resume, reduced motion, static mode"
        )
    finally:
        context.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", choices=["firefox", "chromium"], default="firefox")
    parser.add_argument("--executable", type=Path)
    args = parser.parse_args()
    url = (Path(__file__).resolve().parent.parent / "index.html").as_uri()
    with sync_playwright() as playwright:
        browser = getattr(playwright, args.browser).launch(
            headless=True, executable_path=args.executable
        )
        try:
            check(browser, url, early_frame=True)
            check(browser, url, early_frame=False)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
