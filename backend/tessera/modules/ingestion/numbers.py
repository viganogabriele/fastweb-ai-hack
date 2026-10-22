"""Span text → physical quantity with unit (RFC §4.5 "Numeri", `ing.numbers`, ING-09 pure).

The extractor (ING-04) hands over the span that states how many: "7 richieste", "tre clienti",
"8 to 10 clients", "un paio di signore". Code, not the LLM, turns it into a `Quantity`:

- `exact`: one count next to a unit noun ("Maire nera: 6 richieste", "un cliente", "201pcs").
- `range`: two ordered counts ("25-30 pezzi", "3 or 4 people", "tra 5 e 8 clienti").
- `vague`: a vague quantifier from `config/domain.yaml` ("qualche cliente", "a few clients"), or
  a hedged number ("around 28 clients", "una sessantina di pezzi", "at least 3", "under 100
  units"). A hedged number is not a count: the `Quantity` carries no value and the number as
  written is kept apart in `ParsedQuantity.stated` with its `qualifier`.
- `unknown`: anything else. A number with no unit noun, money or percentages ("38k", "15% dei
  clienti"), sizes ("tg 2"), fractional counts, or two counts in one span (never summed: the span
  must be narrower).

The unit comes only from a noun next to the number: clients, requests, pieces and visitors stay
distinct units ("cinque clienti" never becomes five pieces). Spelled numbers and unit nouns exist
for Italian and English; other languages get digits and vague quantifiers only, so their counts
come out `unknown` until their nouns are added. Money and percentages are out of scope (RFC §6.5
ING-09: extended notations are S).

Pure code: text and vague quantifiers in, `Quantity` out. `load_vague_quantifiers` is the only
function that reads a file, and only the config file it is given.
"""

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path
from typing import Literal, cast

import yaml

from tessera.core.contracts.observations import Quantity

PARSER_VERSION = "numbers-v1"

Qualifier = Literal["approx", "at_least", "at_most"]
CountUnit = Literal["units", "customers", "requests", "visitors"]

# Words allowed between a number and its noun: "12 more requests", "2 korean clients", "una
# decina di clienti". More than this and the number most likely counts something else.
MAX_GAP = 2

CURRENCY_SYMBOLS = frozenset("€$£¥₩")
# Words that make the number next to them money or a percentage, never a count.
NON_COUNT_WORDS = frozenset(
    "eur euro euros usd dollars gbp pounds chf jpy yen krw cny rmb hkd aud sgd aed dkk k mila "
    "grand percent pct percento cento".split()
)


@dataclass(frozen=True)
class ParsedQuantity:
    quantity: Quantity
    qualifier: Qualifier | None = None  # set for hedged numbers; the quantity is then vague
    stated: float | None = None  # the hedged number as written ("around 28" → 28), not a count
    note: str | None = None  # why the result is vague/unknown, for abstention logs


@dataclass(frozen=True)
class _Lexicon:
    numbers: Mapping[str, int] = field(default_factory=dict)  # may sit a few words before the noun
    strict: Mapping[str, int] = field(default_factory=dict)  # count only right before the noun
    approx: Mapping[str, int] = field(default_factory=dict)  # "sessantina", "dozen"
    nouns: Mapping[str, CountUnit] = field(default_factory=dict)
    connectors: frozenset[str] = frozenset({"-", "–", "—", "/"})  # "25-30", "3 o 4"
    between: Mapping[str, str] = field(default_factory=dict)  # "tra" → "e": "tra 5 e 8"
    size_markers: frozenset[str] = frozenset()  # "tg 2", "sz 0", "(x3)": not counts
    people: frozenset[str] = frozenset()  # nouns that mean visitors when they enter the store
    entered: re.Pattern[str] | None = None
    before: tuple[tuple[str, Qualifier], ...] = ()  # hedges before the number, longest first
    after: Mapping[tuple[str, ...], Qualifier] = field(default_factory=dict)  # ... and after


def _numbers(words: str, first: int = 0) -> dict[str, int]:
    return {w: i for i, w in enumerate(words.split(), start=first)}


def _nouns(**by_unit: str) -> dict[str, CountUnit]:
    return {w: cast(CountUnit, unit) for unit, words in by_unit.items() for w in words.split()}


def _hedges(**by_qualifier: str) -> tuple[tuple[str, Qualifier], ...]:
    """Phrases separated by `|`, longest first so "non più di" wins over "più di"."""
    pairs = [(p, cast(Qualifier, q)) for q, ps in by_qualifier.items() for p in ps.split("|")]
    return tuple(sorted(pairs, key=lambda pq: len(pq[0]), reverse=True))


def _after(**by_qualifier: str) -> dict[tuple[str, ...], Qualifier]:
    return {tuple(p.split()): q for p, q in _hedges(**by_qualifier)}


_LEXICONS: dict[str, _Lexicon] = {
    "it": _Lexicon(
        numbers={
            "zero": 0,
            **_numbers(
                "due tre quattro cinque sei sette otto nove dieci undici dodici tredici "
                "quattordici quindici sedici diciassette diciotto diciannove venti",
                first=2,
            ),
        },
        strict={"un": 1, "una": 1, "uno": 1, "nessun": 0, "nessuna": 0, "nessuno": 0},
        approx={"decina": 10, "dozzina": 12, "centinaio": 100}
        | {
            w: 10 * n
            for w, n in _numbers(
                "ventina trentina quarantina cinquantina sessantina settantina ottantina novantina",
                first=2,
            ).items()
        },
        nouns=_nouns(
            customers="cliente clienti persona persone signora signore signori signorina "
            "ragazza ragazze ragazzo ragazzi turista turisti",
            requests="richiesta richieste",
            units="pezzo pezzi pz capo capi articolo articoli unità",
            visitors="visitatore visitatori ingresso ingressi",
        ),
        connectors=frozenset({"-", "–", "—", "/", "o", "a"}),
        between={"tra": "e", "fra": "e"},
        size_markers=frozenset({"tg", "taglia", "taglie", "misura", "mis", "x"}),
        people=frozenset({"persona", "persone"}),
        entered=re.compile(r"\s*(?:sono\s+)?entrat[eio]\b", re.IGNORECASE),
        before=_hedges(
            approx="più o meno|piu' o meno|all'incirca|circa|quasi|intorno ai|intorno alle|"
            "intorno a|sui|sulle|tipo|forse",
            at_least="almeno|non meno di|più di|piu' di|oltre|minimo",
            at_most="non più di|non piu' di|meno di|al massimo|massimo|fino a",
        ),
        after=_after(at_least="+|o più|o piu'|e più|e piu'", at_most="o meno", approx="circa"),
    ),
    "en": _Lexicon(
        numbers=_numbers(
            "zero one two three four five six seven eight nine ten eleven twelve thirteen "
            "fourteen fifteen sixteen seventeen eighteen nineteen twenty"
        ),
        strict={"a": 1, "an": 1, "no": 0},
        approx={"dozen": 12},
        nouns=_nouns(
            customers="customer customers client clients person persons people lady ladies "
            "gentleman gentlemen man men woman women tourist tourists shopper shoppers guest "
            "guests",
            requests="request requests enquiry enquiries inquiry inquiries",
            units="unit units piece pieces pc pcs item items",
            visitors="visitor visitors",
        ),
        connectors=frozenset({"-", "–", "—", "/", "to", "or"}),
        between={"between": "and"},
        size_markers=frozenset({"size", "sizes", "sz", "x"}),
        people=frozenset({"people", "person", "persons"}),
        entered=re.compile(
            r"\s*(?:came\s+)?(?:in\s+)?(?:thru|through)\s+the\s+doors?\b|\s+in\s*(?:[,;.)]|$)",
            re.IGNORECASE,
        ),
        before=_hedges(
            approx="approximately|approx.|approx|roughly|around|about|nearly|almost|close to|"
            "some|maybe|perhaps|probably",
            at_least="at least|more than|no fewer than|no less than|upwards of|over",
            at_most="no more than|fewer than|less than|at most|up to|under|below",
        ),
        after=_after(at_least="+|or more", at_most="or fewer|or less", approx="or so|ish|- ish"),
    ),
}
_EMPTY = _Lexicon()

_TOKEN = re.compile(
    r"(?P<num>\d+(?:[.,'’]\d+)*)(?P<suffix>[^\W\d_]+|[%+€$£¥₩])?"
    r"|(?P<word>[^\W\d_]+(?:['’][^\W\d_]+)*['’]?)"
    r"|(?P<punct>\S)"
)


@dataclass(frozen=True)
class _Token:
    kind: Literal["num", "word", "punct", "vague"]
    text: str
    start: int
    end: int
    suffix: str = ""

    @property
    def key(self) -> str:
        if self.kind != "word":
            return self.text
        return self.text.casefold().replace("’", "'").rstrip("'")


@dataclass(frozen=True)
class _Count:
    start: int
    end: int
    low: float
    high: float
    unit: CountUnit
    qualifier: Qualifier | None = None


def load_vague_quantifiers(domain_yaml: Path) -> dict[str, tuple[str, ...]]:
    """`vague_quantifiers` from `config/domain.yaml`, keyed by `stores.csv` language."""
    domain = yaml.safe_load(domain_yaml.read_text(encoding="utf-8"))
    return {
        lang: tuple(str(w) for w in words) for lang, words in domain["vague_quantifiers"].items()
    }


def parse_quantity(span: str, lang: str, vague: Iterable[str] = ()) -> ParsedQuantity:
    """Quantity stated by `span`, in the store language `lang` ("it", "en", ...).

    `vague` is the vague-quantifier list for that language (`load_vague_quantifiers(...)[lang]`).
    The result never holds a number that is not written in the span.
    """
    lex = _LEXICONS.get(lang.split("-")[0].casefold(), _EMPTY)
    tokens = _tokenize(span, _vague_pattern(tuple(vague)))
    counts = _counts(tokens, span, lex)
    if len(counts) > 1:
        return _unknown(span, None, "several counts in one span")
    if counts:
        return _from_count(counts[0], span)
    # A quantifier that qualifies a unit noun wins over a loose one ("molte coreane, tante
    # richieste"); a loose one takes the span's unit only if the span names just one.
    vague_at = [
        (i, _noun_after(tokens, i + 1, lex)) for i, t in enumerate(tokens) if t.kind == "vague"
    ]
    if vague_at:
        i, noun = next(((i, n) for i, n in vague_at if n is not None), vague_at[0])
        t = tokens[i]
        if noun is None:
            unit, end = _only_unit(tokens, lex), t.end
        else:
            unit, end = _unit(tokens[noun], span, lex), tokens[noun].end
        q = Quantity(kind="vague", unit=unit, raw=span[t.start : end])
        return ParsedQuantity(q, note="vague quantifier")
    has_number = any(t.kind == "num" or t.key in lex.numbers for t in tokens)
    return _unknown(
        span, _only_unit(tokens, lex), "no count next to a unit noun" if has_number else "no count"
    )


def _unknown(span: str, unit: CountUnit | None, note: str) -> ParsedQuantity:
    return ParsedQuantity(Quantity(kind="unknown", unit=unit, raw=span.strip() or None), note=note)


def _from_count(c: _Count, span: str) -> ParsedQuantity:
    raw = span[c.start : c.end]
    unit = c.unit
    if c.qualifier is not None:
        q = Quantity(kind="vague", unit=unit, raw=raw)
        return ParsedQuantity(q, c.qualifier, c.low, f"hedged number ({c.qualifier})")
    if not (c.low.is_integer() and c.high.is_integer()):
        return _unknown(span, unit, "fractional count")
    if c.low == c.high:
        return ParsedQuantity(Quantity(kind="exact", value=c.low, unit=unit, raw=raw))
    return ParsedQuantity(Quantity(kind="range", low=c.low, high=c.high, unit=unit, raw=raw))


@cache
def _vague_pattern(words: tuple[str, ...]) -> re.Pattern[str] | None:
    alts = []
    for w in sorted({w.strip() for w in words if w.strip()}, key=len, reverse=True):
        body = r"\s+".join(re.escape(part) for part in w.split())
        # Latin-script words match whole words; CJK words have no spaces around them.
        alts.append(rf"(?<!\w){body}(?!\w)" if all(ord(c) < 0x2E80 for c in w) else body)
    return re.compile("|".join(alts), re.IGNORECASE) if alts else None


def _tokenize(span: str, vague: re.Pattern[str] | None) -> list[_Token]:
    masked = [(m.start(), m.end()) for m in vague.finditer(span)] if vague else []
    tokens = [_Token("vague", span[s:e], s, e) for s, e in masked]
    for m in _TOKEN.finditer(span):
        if any(s <= m.start() < e for s, e in masked):
            continue
        if m["num"] is not None:
            tokens.append(_Token("num", m["num"], m.start(), m.end(), m["suffix"] or ""))
        else:
            kind = "word" if m["word"] is not None else "punct"
            tokens.append(_Token(kind, m[0], m.start(), m.end()))
    return sorted(tokens, key=lambda t: t.start)


def _number(text: str) -> float | None:
    """Digits as written. Grouped thousands ("1.200", "1,200", "24'620") or a decimal."""
    if text.isdigit():
        return float(text)
    if re.fullmatch(r"\d{1,3}([.,'’])\d{3}(?:\1\d{3})*", text):
        return float(re.sub(r"\D", "", text))
    if re.fullmatch(r"\d+[.,]\d+", text):
        return float(text.replace(",", "."))
    return None


def _value(tokens: list[_Token], i: int, lex: _Lexicon) -> float | None:
    """Count written at token i, if it can be a count at all (not money, a size, a time...)."""
    t = tokens[i]
    if t.kind == "word":
        return float(lex.numbers[t.key]) if t.key in lex.numbers else None
    if t.kind != "num":
        return None
    suffix = t.suffix.casefold()
    if suffix and suffix not in ("+", "ish") and suffix not in lex.nouns:
        return None  # "15%", "38k", "4pm", "2nd", "100€"
    prev = [p for p in tokens[max(0, i - 2) : i] if p.text not in (".", ":")][-1:]
    if prev and (
        prev[0].key in lex.size_markers
        or prev[0].key in NON_COUNT_WORDS
        or prev[0].text in CURRENCY_SYMBOLS
    ):
        return None
    return _number(t.text)


def _noun_after(tokens: list[_Token], k: int, lex: _Lexicon) -> int | None:
    """Index of the unit noun within MAX_GAP plain words from token k, else None."""
    for j in range(k, min(k + MAX_GAP + 1, len(tokens))):
        t = tokens[j]
        if t.kind != "word" or t.key in lex.numbers or t.key in lex.strict:
            return None
        if t.key in lex.nouns:
            return j
        if t.key in NON_COUNT_WORDS:
            return None
    return None


def _count_at(tokens: list[_Token], i: int, span: str, lex: _Lexicon) -> tuple[_Count, int] | None:
    """Count starting at token i and the index after it, else None."""
    t = tokens[i]
    nxt = tokens[i + 1] if i + 1 < len(tokens) else None
    if t.kind == "word" and t.key in lex.strict:  # "un cliente", "no requests"
        if nxt is not None and nxt.kind == "word" and nxt.key in lex.nouns:
            v = float(lex.strict[t.key])
            return _Count(t.start, nxt.end, v, v, _unit(nxt, span, lex)), i + 2
        return None
    if t.kind == "word" and t.key in lex.approx:  # "una sessantina di pezzi", "half a dozen"
        noun = _noun_after(tokens, i + 1, lex)
        if noun is None:
            return None
        stated, start = float(lex.approx[t.key]), t.start
        keys = [p.key for p in tokens[max(0, i - 2) : i]]
        if keys == ["half", "a"]:
            stated, start = stated / 2, tokens[i - 2].start
        elif keys and keys[-1] in lex.strict:
            start = tokens[i - 1].start
        n = tokens[noun]
        return _Count(start, n.end, stated, stated, _unit(n, span, lex), "approx"), noun + 1

    low = _value(tokens, i, lex)
    if low is None:
        return None
    high, j, qualifier, start = low, i, None, t.start
    if (
        nxt is not None
        and not t.suffix
        and i + 2 < len(tokens)
        and (nxt.key in lex.connectors or (i > 0 and lex.between.get(tokens[i - 1].key) == nxt.key))
        and (v2 := _value(tokens, i + 2, lex)) is not None
        and v2 > low
    ):
        high, j = v2, i + 2
        if nxt.key not in lex.connectors:  # "tra 5 e 8"
            start = tokens[i - 1].start

    end_tok = tokens[j]
    suffix = end_tok.suffix.casefold()
    if suffix in lex.nouns:  # "201pcs"
        count = _Count(t.start, end_tok.end, low, high, _unit(end_tok, span, lex))
        return count, j + 1
    if suffix:
        qualifier = lex.after.get((suffix,))
    k = j + 1
    for phrase, q in lex.after.items():
        if tuple(p.key for p in tokens[k : k + len(phrase)]) == phrase:
            qualifier, k = qualifier or q, k + len(phrase)
            break
    noun = _noun_after(tokens, k, lex)
    if noun is None:
        return None
    if high != low:
        qualifier = None  # a range already states its uncertainty
    elif qualifier is None and (hedge := _hedge_before(span[: t.start], lex)):
        qualifier, start = hedge
    n = tokens[noun]
    return _Count(start, n.end, low, high, _unit(n, span, lex), qualifier), noun + 1


def _count_after_noun(tokens: list[_Token], i: int, lex: _Lexicon) -> tuple[_Count, int] | None:
    """ "richieste: 7", "visitors = 481"."""
    if i + 2 >= len(tokens) or tokens[i].key not in lex.nouns or tokens[i + 1].text not in ":=":
        return None
    num = tokens[i + 2]
    if num.kind != "num" or num.suffix:
        return None
    v = _value(tokens, i + 2, lex)
    if v is None:
        return None
    return _Count(tokens[i].start, num.end, v, v, lex.nouns[tokens[i].key]), i + 3


def _counts(tokens: list[_Token], span: str, lex: _Lexicon) -> list[_Count]:
    out, i = [], 0
    while i < len(tokens):
        hit = _count_at(tokens, i, span, lex) or _count_after_noun(tokens, i, lex)
        if hit is None:
            i += 1
        else:
            out.append(hit[0])
            i = hit[1]
    return out


def _unit(noun: _Token, span: str, lex: _Lexicon) -> CountUnit:
    key = noun.key if noun.kind == "word" else noun.suffix.casefold()
    if key in lex.people and lex.entered is not None and lex.entered.match(span, noun.end):
        return "visitors"  # "142 people thru the door", "300 persone entrate"
    return lex.nouns[key]


def _only_unit(tokens: list[_Token], lex: _Lexicon) -> CountUnit | None:
    units = {lex.nouns[t.key] for t in tokens if t.kind == "word" and t.key in lex.nouns}
    return units.pop() if len(units) == 1 else None


def _hedge_before(prefix: str, lex: _Lexicon) -> tuple[Qualifier, int] | None:
    """Hedge that ends `prefix` ("almeno ", "at least ", "~") and where it starts."""
    stripped = prefix.rstrip()
    if stripped.endswith("~"):
        return "approx", len(stripped) - 1
    for phrase, q in lex.before:
        start = len(stripped) - len(phrase)
        tail = stripped[start:].casefold().replace("’", "'")
        if start >= 0 and tail == phrase and (start == 0 or not stripped[start - 1].isalnum()):
            return q, start
    return None
