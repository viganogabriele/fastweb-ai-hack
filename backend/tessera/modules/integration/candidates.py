"""Product mention → ranked catalog candidates, with abstention (RFC §4.5 EntityLink, INT-01 pure).

Staff never write codes: "la Maire nera", "イルバロ", "the long black one". This step finds
catalog candidates from style/colour names and aliases (exact, then `rapidfuzz` on word n-grams),
checks the size against the style's size run, and decides `linked`, `ambiguous` or `unlinked`.
It never guesses: two close candidates, a colour the style doesn't come in, or a size outside
the size run all leave the mention `ambiguous` for the constrained LLM choice or a human.

Scores are on a 0–100 similarity scale. They are not probabilities.

Pure code: catalog rows and aliases come from the caller (`erp/master_data/*.csv`,
`config/aliases.yaml`). No DB, no LLM.
"""

import re
import unicodedata
from collections.abc import Collection, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Literal

from rapidfuzz import fuzz

Level = Literal["sku_size", "sku", "style"]
LinkStatus = Literal["linked", "ambiguous", "unlinked"]
Method = Literal["exact", "fuzzy"]

# SKU score = weighted mean of style and colour match. The style name carries the identity;
# colour names are often inflected ("nera" for "nero", "noire" for "noir").
STYLE_WEIGHT = 0.75

# One word of a multi-word name: a candidate, never enough to link on its own.
PARTIAL_NAME_SCORE = 80.0

# Flags that keep a candidate from being linked automatically.
BLOCKING_FLAGS = frozenset({"colour_not_in_style", "size_not_in_size_run"})


@dataclass(frozen=True)
class LinkParams:
    candidate_min: float = 75.0  # below this a name match is not a candidate
    link_min: float = 90.0  # top candidate needs at least this to be linked
    min_margin: float = 10.0  # ...and this lead over the runner-up
    top_k: int = 8
    max_ngram: int = 4


@dataclass(frozen=True)
class Style:
    code: str
    name: str
    colours: tuple[str, ...]  # colour codes the style comes in
    sizes: tuple[str, ...]  # size run, e.g. ("00", "0", "1", ...)


@dataclass(frozen=True)
class Catalog:
    styles: Mapping[str, Style]
    colour_names: Mapping[str, tuple[str, ...]]  # colour code → names (it, en, aliases)
    style_aliases: Mapping[str, tuple[str, ...]] = field(default_factory=dict)

    @classmethod
    def from_rows(
        cls,
        sku_colour_rows: Iterable[Mapping[str, str]],
        sku_size_rows: Iterable[Mapping[str, str]],
        style_aliases: Mapping[str, Sequence[str]] | None = None,
        colour_aliases: Mapping[str, Sequence[str]] | None = None,
    ) -> "Catalog":
        """Build from `sku_colour.csv` and `sku_size_ean.csv` rows plus optional aliases
        (style code → names, colour code → names)."""
        names: dict[str, str] = {}
        colours: dict[str, list[str]] = {}
        colour_names: dict[str, list[str]] = {}
        sku_style: dict[str, str] = {}
        for r in sku_colour_rows:
            code = r["style_code"]
            names[code] = r["style_name"]
            colours.setdefault(code, []).append(r["color_code"])
            sku_style[r["sku"]] = code
            for n in (r.get("color_name_it"), r.get("color_name_en")):
                _add_unique(colour_names.setdefault(r["color_code"], []), n)
        sizes: dict[str, list[str]] = {}
        for r in sku_size_rows:
            code = sku_style.get(r["sku"])
            if code is not None:
                _add_unique(sizes.setdefault(code, []), r["size"])
        for code, extra in (colour_aliases or {}).items():
            for n in extra:
                _add_unique(colour_names.setdefault(code, []), n)
        styles = {
            code: Style(code, name, tuple(colours[code]), tuple(sizes.get(code, ())))
            for code, name in names.items()
        }
        return cls(
            styles=styles,
            colour_names={c: tuple(n) for c, n in colour_names.items()},
            style_aliases={c: tuple(a) for c, a in (style_aliases or {}).items()},
        )


@dataclass(frozen=True)
class Candidate:
    target_id: str  # style code, SKU (`<style>-<colour>`) or SKU-size
    level: Level
    score: float
    method: Method
    matched: str  # catalog name or alias that matched
    flags: tuple[str, ...] = ()
    in_assortment: bool | None = None  # None when no assortment was given


@dataclass(frozen=True)
class LinkResult:
    status: LinkStatus
    target_id: str | None
    level: Level | None
    candidates: tuple[Candidate, ...]
    reasons: tuple[str, ...] = ()


def link_mention(
    mention: str,
    catalog: Catalog,
    size: str | None = None,
    store_skus: Collection[str] | None = None,
    params: LinkParams | None = None,
) -> LinkResult:
    """Rank candidates for one product mention and decide whether it can be linked.

    `store_skus` is the store assortment: candidates in it are preferred, and the global
    catalog is used only when none qualifies (reason `global_fallback`).
    """
    p = params or LinkParams()
    text = normalize(mention)
    if not text:
        return LinkResult("unlinked", None, None, (), ("empty_mention",))

    style_hits: dict[str, tuple[float, Method, str]] = {}
    for code, style in catalog.styles.items():
        hit = _best_match(text, (style.name, *catalog.style_aliases.get(code, ())), p)
        if hit:
            style_hits[code] = hit
    colour_hits: dict[str, tuple[float, Method, str]] = {}
    for code, names in catalog.colour_names.items():
        hit = _best_match(text, names, p)
        if hit:
            colour_hits[code] = hit

    if not style_hits:
        reason = "colour_only" if colour_hits else "no_candidate"
        return LinkResult("unlinked", None, None, (), (reason,))

    size_norm = _normalize_size(size) if size else None
    cands: list[Candidate] = []
    for code, (s_score, s_method, s_name) in style_hits.items():
        style = catalog.styles[code]
        colours = [c for c in style.colours if c in colour_hits]
        if not colours and len(style.colours) == 1 and not colour_hits:
            colours = list(style.colours)  # single-colour style: the SKU is implied
        flags: list[str] = []
        if colour_hits and not colours:
            flags.append("colour_not_in_style")
        size_ok = size_norm is None or size_norm in style.sizes
        if not size_ok:
            flags.append("size_not_in_size_run")
        if not colours:
            cands.append(
                _candidate(code, "style", s_score, s_method, s_name, flags, style, store_skus)
            )
            continue
        for colour in colours:
            c_score, c_method, _ = colour_hits.get(colour, (100.0, "exact", ""))
            sku = f"{code}-{colour}"
            target, level = (sku, "sku")
            if size_norm is not None and size_ok:
                target, level = f"{sku}-{size_norm}", "sku_size"
            method: Method = "exact" if s_method == c_method == "exact" else "fuzzy"
            score = STYLE_WEIGHT * s_score + (1 - STYLE_WEIGHT) * c_score
            cands.append(
                _candidate(target, level, score, method, s_name, flags, style, store_skus, sku)
            )

    cands.sort(key=lambda c: (-c.score, c.target_id))
    reasons: list[str] = []
    pool = cands
    if store_skus is not None:
        in_store = [c for c in cands if c.in_assortment]
        if in_store:
            pool = in_store
        else:
            reasons.append("global_fallback")
    ranked = tuple(pool[: p.top_k])
    return _decide(ranked, p, reasons)


def normalize(text: str) -> str:
    """NFKC, casefold, accents stripped from Latin letters only (kana voicing marks are kept),
    punctuation → spaces."""
    text = unicodedata.normalize("NFKC", text).casefold()
    out: list[str] = []
    for ch in text:
        decomposed = unicodedata.normalize("NFD", ch)
        out.append(decomposed[0] if decomposed[0].isascii() else ch)
    return " ".join(re.findall(r"\w+", "".join(out)))


def _decide(ranked: tuple[Candidate, ...], p: LinkParams, reasons: list[str]) -> LinkResult:
    if not ranked:
        return LinkResult("unlinked", None, None, (), (*reasons, "no_candidate"))
    top = ranked[0]
    if top.score < p.link_min:
        reasons.append("low_score")
    if len(ranked) > 1 and top.score - ranked[1].score < p.min_margin:
        reasons.append("close_runner_up")
    reasons.extend(f for f in top.flags if f in BLOCKING_FLAGS)
    blocking = [r for r in reasons if r != "global_fallback"]
    if blocking:
        return LinkResult("ambiguous", None, None, ranked, tuple(reasons))
    return LinkResult("linked", top.target_id, top.level, ranked, tuple(reasons))


def _candidate(
    target: str,
    level: Level,
    score: float,
    method: Method,
    matched: str,
    flags: list[str],
    style: Style,
    store_skus: Collection[str] | None,
    sku: str | None = None,
) -> Candidate:
    in_assortment = None
    if store_skus is not None:
        skus = [sku] if sku else [f"{style.code}-{c}" for c in style.colours]
        in_assortment = any(s in store_skus for s in skus)
    return Candidate(target, level, round(score, 1), method, matched, tuple(flags), in_assortment)


def _best_match(text: str, names: Iterable[str], p: LinkParams) -> tuple[float, Method, str] | None:
    """Exact match of a name in the text (word-bounded for ASCII names, substring otherwise),
    else the best `fuzz.ratio` of the name against word n-grams of the text. A word that is
    part of a multi-word name ("polaris" for "POLARIS CAPE") scores PARTIAL_NAME_SCORE."""
    words = text.split()
    text_words = set(words)
    best: tuple[float, Method, str] | None = None
    for name in names:
        n = normalize(name)
        if not n:
            continue
        if n.isascii():
            exact = re.search(rf"(?<!\w){re.escape(n)}(?!\w)", text) is not None
        else:
            exact = n in text.replace(" ", "") or n in text
        if exact:
            return (100.0, "exact", name)
        if not n.isascii():
            continue  # no fuzzy matching on unsegmented scripts
        name_words = n.split()
        k = len(name_words)
        if (
            k > 1
            and PARTIAL_NAME_SCORE >= p.candidate_min
            and any(len(w) >= 4 and w in text_words for w in name_words)
        ):
            if best is None or PARTIAL_NAME_SCORE > best[0]:
                best = (PARTIAL_NAME_SCORE, "fuzzy", name)
        for size in {max(1, k - 1), k, min(p.max_ngram, k + 1)}:
            for i in range(len(words) - size + 1):
                score = fuzz.ratio(n, " ".join(words[i : i + size]))
                if score >= p.candidate_min and (best is None or score > best[0]):
                    best = (score, "fuzzy", name)
    return best


def _normalize_size(size: str) -> str:
    s = unicodedata.normalize("NFKC", size).strip().upper()
    s = re.sub(r"^(TAGLIA|TG\.?|SIZE|TAILLE|TALLA|GRÖSSE|GROESSE|EU)\s*", "", s)
    return s.strip()


def _add_unique(items: list[str], value: str | None) -> None:
    if value and value not in items:
        items.append(value)
