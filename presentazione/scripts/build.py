#!/usr/bin/env python3
"""Build the Tesseract deck as one self-contained, offline HTML file.

Adapted from the polinetwork-slides skill; its layout and presentation engine
are retained, with Tesseract identity, local fonts and no background image assets.

Uso:
    python3 scripts/build.py percorso/assemblea.slides.html [-o out.html] [--no-embed-images]
    python3 scripts/build.py --extract assemblea.html [-o cartella]   # ricava il sorgente

Il sorgente contiene solo le <section class="slide">, preceduto da un commento
con i metadati:

    <!--
    title: Tesseract: Il forecast ascolta i negozi
    lang: it
    mode: lettura        (facoltativo: versione autoesplicativa)
    crumb: no            (facoltativo: niente nome della sezione in alto a destra)
    -->

Il risultato include tema, motore, font, logo, le sole icone
usate e (di default) le immagini locali, quindi funziona offline e si può
mandare come singolo file. Solo libreria standard di Python.
"""

from __future__ import annotations

import argparse
import base64
import difflib
import html
import mimetypes
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
ASSETS = SKILL / "assets"

FONTS = [
    ("Inter", "100 900", "inter"),
    ("Bodoni Moda", "400 900", "bodoni-moda"),
]
ARROW = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 6l6 6-6 6"/></svg>'
ICON_TAG = re.compile(r'<i\b([^>]*?)\bdata-icon="([a-z0-9-]+)"([^>]*)>\s*</i>')
META = re.compile(r"\A\s*<!--(.*?)-->", re.S)


def b64(path: Path, mime: str | None = None) -> str:
    mime = mime or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def svg_uri(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def font_css() -> str:
    return "\n".join(
        f'@font-face{{font-family:"{family}";font-style:normal;font-weight:{weight};'
        f'font-display:block;src:url({b64(ASSETS / "fonts" / (stem + ".woff2"), "font/woff2")}) format("woff2");}}'
        for family, weight, stem in FONTS
    )


def vars_css() -> str:
    return (
        ":root{"
        f'--logo:url("{b64(ASSETS / "logo.svg", "image/svg+xml")}");'
        f'--arrow:url("{svg_uri(ARROW)}");'
        "--bg-print:#f5f4f1;--bg-frost:#fbfaf8;}"
    )


def icon_symbols(names: list[str]) -> str:
    out = []
    for name in names:
        f = ASSETS / "icons" / f"{name}.svg"
        svg = re.sub(r"<!--.*?-->", "", f.read_text(), flags=re.S)
        vb = re.search(r'viewBox="([^"]+)"', svg).group(1)
        inner = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1)
        inner = re.sub(r"<title>.*?</title>", "", inner, flags=re.S).strip()
        if name.startswith("brand-"):
            attrs = 'fill="currentColor" stroke="none"'
        else:
            attrs = 'fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"'
            # lunghezza normalizzata: l'animazione che disegna l'icona fa finire tutti i tratti insieme
            inner = re.sub(r"<(path|line|polyline|polygon|circle|rect|ellipse)\b", r'<\1 pathLength="1"', inner)
        out.append(f'<symbol id="i-{name}" viewBox="{vb}" {attrs}>{inner}</symbol>')
    return "".join(out)


SRC_TAG = re.compile(r'<script type="application/x-polinetwork-source">(.*?)</script>', re.S)
SRC_ATTR = re.compile(r'\bsrc="([^"]+)"')


def extract(built: Path, out_dir: Path | None) -> int:
    """Ricava il sorgente .slides.html (e le immagini incorporate) da un HTML compilato."""
    doc = built.read_text(encoding="utf-8")
    m = SRC_TAG.search(doc)
    if not m:
        print("ERRORE: il file non contiene il sorgente (non è stato creato da build.py?)", file=sys.stderr)
        return 1
    source = base64.b64decode(m.group(1)).decode("utf-8")
    out_dir = (out_dir or built.parent).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / (re.sub(r"\.html?$", "", built.name) + ".slides.html")
    if target.exists():
        print(f"ERRORE: {target} esiste già", file=sys.stderr)
        return 1
    target.write_text(source, encoding="utf-8")
    # le immagini sono state sostituite una a una, nello stesso ordine
    main_html = doc[doc.find('<main class="stage"'):doc.find("</main>")]
    body = META.sub("", source, count=1)
    written = 0
    for rel, uri in zip(SRC_ATTR.findall(body), SRC_ATTR.findall(main_html)):
        if not uri.startswith("data:") or re.match(r"^(data:|https?:|//|#)", rel):
            continue
        dest = (out_dir / html.unescape(rel)).resolve()
        if out_dir not in dest.parents or dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(base64.b64decode(uri.split(",", 1)[1]))
        written += 1
    print(f"OK {target}  ({written} immagini estratte)")
    return 0


def available_icons() -> list[str]:
    return sorted(p.stem for p in (ASSETS / "icons").glob("*.svg"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", type=Path)
    ap.add_argument("-o", "--out", type=Path)
    ap.add_argument("--no-embed-images", action="store_true", help="lascia le immagini come link relativi")
    ap.add_argument("--list-icons", action="store_true", help="elenca le icone disponibili ed esce")
    ap.add_argument("--extract", action="store_true", help="ricava il sorgente da un HTML compilato")
    if "--list-icons" in sys.argv:
        print("\n".join(available_icons()))
        return 0
    args = ap.parse_args()
    if args.extract:
        return extract(args.source.resolve(), args.out)

    warnings: list[str] = []
    errors: list[str] = []
    src: Path = args.source.resolve()
    text = src.read_text(encoding="utf-8")
    original = text
    meta: dict[str, str] = {}
    m = META.match(text)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip().lower()] = v.strip()
        text = text[m.end():]
    title = meta.get("title", "Tesseract")
    lang = meta.get("lang", "it")
    mode = meta.get("mode", "").lower()
    if mode not in ("", "presentazione", "lettura"):
        errors.append(f'mode "{mode}" non valido: usa "presentazione" (default) o "lettura"')
    html_class = ' class="read"' if mode == "lettura" else ""
    crumb = meta.get("crumb", "").lower()
    if crumb not in ("", "si", "sì", "yes", "no"):
        errors.append(f'crumb "{crumb}" non valido: usa "sì" (default) o "no"')
    if crumb == "no":
        html_class += ' data-crumb="off"'

    # icone: <i data-icon="nome"></i> → <svg><use/></svg>
    known = set(available_icons())
    used: list[str] = ["camera"]

    def repl_icon(mo: re.Match) -> str:
        name = mo.group(2)
        if name not in known:
            hint = difflib.get_close_matches(name, known, n=3)
            errors.append(f'icona sconosciuta "{name}"' + (f" (forse: {', '.join(hint)})" if hint else ""))
            return mo.group(0)
        if name not in used:
            used.append(name)
        cls = re.search(r'class="([^"]*)"', mo.group(1) + mo.group(3))
        extra = f" {cls.group(1)}" if cls else ""
        return f'<svg class="ico{extra}" aria-hidden="true"><use href="#i-{name}"/></svg>'

    text = ICON_TAG.sub(repl_icon, text)

    # immagini locali → data URI
    missing: list[str] = []

    def repl_src(mo: re.Match) -> str:
        attr, val = mo.group(1), mo.group(2)
        if re.match(r"^(data:|https?:|//|#)", val):
            return mo.group(0)
        p = (src.parent / html.unescape(val)).resolve()
        if not p.is_file():
            missing.append(val)
            return mo.group(0)
        if args.no_embed_images:
            return mo.group(0)
        size = p.stat().st_size
        if size > 1_500_000:
            warnings.append(f"immagine pesante ({size // 1024} KB): {val}: meglio ridimensionarla")
        return f'{attr}="{b64(p)}"'

    text = re.sub(r'\b(src)="([^"]+)"', repl_src, text)
    for v in missing:
        warnings.append(f"immagine non trovata (resta un segnaposto): {v}")

    n_slides = len(re.findall(r'<section\b[^>]*class="[^"]*\bslide\b', text))
    if n_slides == 0:
        errors.append('nessuna <section class="slide"> trovata')
    n_todo = len(re.findall(r'class="todo"', text)) + len(re.findall(r'data-(?:section|sub)="\[', text))
    if n_todo:
        warnings.append(f"{n_todo} segnaposto .todo ancora da completare")

    if errors:
        for e in errors:
            print("ERRORE:", e, file=sys.stderr)
        return 1

    css = (ASSETS / "theme.css").read_text(encoding="utf-8") + "\n" + (ASSETS / "brand.css").read_text(encoding="utf-8")
    js = (ASSETS / "deck.js").read_text(encoding="utf-8") + "\n" + (ASSETS / "scenes.js").read_text(encoding="utf-8")
    doc = f"""<!doctype html>
<html lang="{html.escape(lang)}"{html_class}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="polinetwork-slides">
<title>{html.escape(title)}</title>
<link rel="icon" href="{b64(ASSETS / 'logo.svg', 'image/svg+xml')}">
<style>
{font_css()}
{vars_css()}
{css}
</style>
</head>
<body>
<div class="bg" aria-hidden="true"></div>
<main class="stage" id="stage">
{text.strip()}
</main>
<svg width="0" height="0" style="position:absolute" aria-hidden="true">{icon_symbols(used)}</svg>
<script type="application/x-polinetwork-source">{base64.b64encode(original.encode()).decode()}</script>
<script>
{js}
</script>
</body>
</html>
"""
    out: Path = args.out.resolve() if args.out else src.with_name(re.sub(r"(\.slides)?\.html?$", "", src.name) + ".html")
    if out == src:
        print("ERRORE: l'output sovrascriverebbe il sorgente; usa -o", file=sys.stderr)
        return 1
    out.write_text(doc, encoding="utf-8")
    for w in warnings:
        print("ATTENZIONE:", w)
    print(f"OK {out}  ({n_slides} slide, {len(doc.encode()) // 1024} KB, icone: {len(used)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
