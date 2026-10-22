"""Span text → physical quantity with unit (RFC §4.5 "Numeri", `ing.numbers`, ING-09 pure).

The extractor (ING-04) hands over the span that states how many: "7 richieste", "tre clienti",
"8 to 10 clients", "un paio di signore". Code, not the LLM, turns it into a `Quantity`:

- `exact`: one count next to a unit noun ("Maire nera: 6 richieste", "un cliente", "201pcs").
- `range`: two ascending counts ("25-30 pezzi", "3 or 4 people", "tra 5 e 8 clienti").
- `vague`: a vague quantifier from `config/domain.yaml` ("qualche cliente", "a few clients"), or
  a hedged count ("around 28 clients", "una sessantina di pezzi", "at least 3", "5 units or
  more", "not more than 5"). A hedged count is not a count: the `Quantity` carries no value and
  the number as written is kept apart in `ParsedQuantity.stated` with its `qualifier`.
- `unknown`: anything else. A wrong number is worse than no number, so the parser abstains on
  money and percentages ("38k", "15% dei clienti"), sizes ("tg 2"), dates and times ("10/22",
  "10:05"), fractions and decimals ("1/2", "2,5 pezzi", "0.500"), signed numbers ("-5"),
  compound spelled numbers ("one hundred", "twenty-one"), numbers it cannot split ("1 200",
  "3 e 4 pezzi", "between 8 and 5"), and two counts in one span (never summed: the span must be
  narrower).

The parser first reads each numeric expression whole (numbers joined by a connector, a list
separator or a plain space), then classifies it, then binds it to a unit noun: right after it,
across known modifiers only ("12 more requests", "2 Korean clients", "3 dei nostri clienti"),
or before it after a colon ("richieste: 7"). Any other word in between means the number counts
something else ("3 days without customers", "3 boxes of items").

The unit comes only from that noun: clients, requests, pieces and visitors stay distinct units
("cinque clienti" never becomes five pieces). Spelled numbers, unit nouns and decimal separators
exist for Italian and English; other languages get digits and vague quantifiers only, so their
counts come out `unknown` until their nouns are added. Money and percentages are out of scope
(RFC §6.5 ING-09: extended notations are S).

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

PARSER_VERSION = "numbers-v2"

Qualifier = Literal["approx", "at_least", "at_most"]
CountUnit = Literal["units", "customers", "requests", "visitors"]

# Modifiers allowed between a number and its noun: "3 of our regular clients".
MAX_GAP = 3

CURRENCY_SYMBOLS = frozenset("€$£¥₩")
# Words next to a number that make it money or a percentage, never a count.
NON_COUNT_WORDS = frozenset(
    "eur euro euros usd dollars gbp pounds chf jpy yen krw cny rmb hkd aud sgd aed dkk k grand "
    "percent pct percento".split()
)
# Separators that only ever group thousands: apostrophes (Swiss) and non-breaking spaces.
GROUPING = "'’   "


@dataclass(frozen=True)
class ParsedQuantity:
    quantity: Quantity
    qualifier: Qualifier | None = None  # set for hedged numbers; the quantity is then vague
    stated: float | None = None  # the hedged number as written ("around 28" → 28), not a count
    note: str | None = None  # why the result is vague/unknown, for abstention logs


@dataclass(frozen=True)
class _Lexicon:
    numbers: Mapping[str, int] = field(default_factory=dict)  # spelled numbers
    compound: frozenset[str] = frozenset()  # "hundred", "mila": a number we do not compose
    strict: Mapping[str, int] = field(default_factory=dict)  # articles: count only before a noun
    approx: Mapping[str, int] = field(default_factory=dict)  # "sessantina", "dozen"
    nouns: Mapping[str, CountUnit] = field(default_factory=dict)
    modifiers: frozenset[str] = frozenset()  # words allowed between a number and its noun
    connectors: frozenset[str] = frozenset({"-", "–", "—"})  # ranges: "25-30", "3 o 4"
    joiners: frozenset[str] = frozenset({",", "/"})  # lists: "3, 4", "3 e 4", "3 / 4"
    between: Mapping[str, str] = field(default_factory=dict)  # "tra" → "e": "tra 5 e 8"
    decimal: str | None = None  # decimal separator; the other of "." and "," groups thousands
    not_before: frozenset[str] = frozenset()  # "tg 2", "(x3)", "October 22": not counts
    negations: frozenset[str] = frozenset()  # "not more than": a hedge we must not reverse
    people: frozenset[str] = frozenset()  # nouns that mean visitors when they enter the store
    entered: re.Pattern[str] | None = None
    before: tuple[tuple[str, Qualifier], ...] = ()  # hedges before the number, longest first
    after: Mapping[tuple[str, ...], Qualifier] = field(default_factory=dict)  # ... and after


def _numbers(words: str, first: int = 0, step: int = 1) -> dict[str, int]:
    return {w: first + i * step for i, w in enumerate(words.split())}


def _nouns(**by_unit: str) -> dict[str, CountUnit]:
    return {w: cast(CountUnit, unit) for unit, words in by_unit.items() for w in words.split()}


def _hedges(**by_qualifier: str) -> tuple[tuple[str, Qualifier], ...]:
    """Phrases separated by `|`, longest first so "non più di" wins over "più di"."""
    pairs = [(p, cast(Qualifier, q)) for q, ps in by_qualifier.items() for p in ps.split("|")]
    return tuple(sorted(pairs, key=lambda pq: len(pq[0]), reverse=True))


def _after(**by_qualifier: str) -> dict[tuple[str, ...], Qualifier]:
    return {tuple(w.rstrip("'") for w in p.split()): q for p, q in _hedges(**by_qualifier)}


_LEXICONS: dict[str, _Lexicon] = {
    "it": _Lexicon(
        numbers={"zero": 0}
        | _numbers(
            "due tre quattro cinque sei sette otto nove dieci undici dodici tredici quattordici "
            "quindici sedici diciassette diciotto diciannove venti",
            first=2,
        )
        | _numbers("trenta quaranta cinquanta sessanta settanta ottanta novanta", 30, 10),
        compound=frozenset("cento mille mila milione milioni".split()),
        strict={"un": 1, "una": 1, "uno": 1, "nessun": 0, "nessuna": 0, "nessuno": 0},
        approx={"decina": 10, "dozzina": 12, "centinaio": 100}
        | _numbers(
            "ventina trentina quarantina cinquantina sessantina settantina ottantina novantina",
            20,
            10,
        ),
        nouns=_nouns(
            customers="cliente clienti persona persone signora signore signori signorina "
            "ragazza ragazze ragazzo ragazzi turista turisti",
            requests="richiesta richieste",
            units="pezzo pezzi pz capo capi articolo articoli unità",
            visitors="visitatore visitatori ingresso ingressi",
        ),
        modifiers=frozenset(
            "altri altre altro altra nuovi nuove nuovo nuova ulteriori vari varie di dei degli "
            "delle nostri nostre nostro nostra".split()
        ),
        connectors=frozenset({"-", "–", "—", "o", "a"}),
        joiners=frozenset({",", "/", "e"}),
        between={"tra": "e", "fra": "e"},
        decimal=",",
        not_before=frozenset(
            "tg taglia taglie misura mis x gennaio febbraio marzo aprile maggio giugno luglio "
            "agosto settembre ottobre novembre dicembre gen feb mar apr mag giu lug ago set ott "
            "nov dic".split()
        ),
        negations=frozenset({"non"}),
        people=frozenset({"persona", "persone"}),
        entered=re.compile(r"\s*(?:sono\s+)?entrat[eio]\b", re.IGNORECASE),
        before=_hedges(
            approx="più o meno|piu' o meno|all'incirca|circa|quasi|intorno ai|intorno alle|"
            "intorno a|sui|sulle|tipo|forse",
            at_least="almeno|non meno di|più di|piu' di|oltre|minimo",
            at_most="non più di|non piu' di|non oltre|meno di|al massimo|massimo|fino a",
        ),
        after=_after(at_least="+|o più|o piu'|e più|e piu'", at_most="o meno", approx="circa"),
    ),
    "en": _Lexicon(
        numbers=_numbers(
            "zero one two three four five six seven eight nine ten eleven twelve thirteen "
            "fourteen fifteen sixteen seventeen eighteen nineteen twenty"
        )
        | _numbers("thirty forty fifty sixty seventy eighty ninety", 30, 10),
        compound=frozenset("hundred hundreds thousand thousands million millions".split()),
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
        modifiers=frozenset(
            "more other new different additional extra separate regular returning repeat loyal "
            "vip local foreign international potential possible individual young older elderly "
            "male female of the our asian european american canadian british english french "
            "german italian spanish swiss dutch danish chinese japanese korean taiwanese "
            "singaporean australian saudi arab emirati russian indian brazilian mexican".split()
        ),
        connectors=frozenset({"-", "–", "—", "to", "or"}),
        joiners=frozenset({",", "/", "and"}),
        between={"between": "and"},
        decimal=".",
        not_before=frozenset(
            "size sizes sz x january february march april may june july august september "
            "october november december jan feb mar apr jun jul aug sep sept oct nov dec".split()
        ),
        negations=frozenset({"not", "never"}),
        people=frozenset({"people", "person", "persons"}),
        entered=re.compile(
            r"\s*(?:came\s+)?(?:in\s+)?(?:thru|through)\s+the\s+doors?\b|\s+in\s*(?:[,;.)]|$)",
            re.IGNORECASE,
        ),
        before=_hedges(
            approx="approximately|approx.|approx|roughly|around|about|nearly|almost|close to|"
            "some|maybe|perhaps|probably",
            at_least="at least|more than|no fewer than|no less than|not fewer than|"
            "not less than|not under|not below|upwards of|over|above",
            at_most="no more than|not more than|not over|not above|fewer than|less than|at most|"
            "up to|under|below",
        ),
        after=_after(at_least="+|or more", at_most="or fewer|or less", approx="or so|ish|- ish"),
    ),
}
_EMPTY = _Lexicon()

_TOKEN = re.compile(
    # A sign glued to the digits and not to a word or number before it: "-5", "(−5", not "25-30".
    rf"(?P<sign>(?<![\w.,{GROUPING}])[-−–—+](?=\d))?"
    # Digits with whatever joins them, read later as one number or rejected whole: "1.200",
    # "1 200" (NBSP), "10:05", "10/22", "1/2".
    rf"(?P<num>\d+(?:[.,:/{GROUPING}]\d+)*)(?P<suffix>[^\W\d_]+|[%+€$£¥₩])?"
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
    signed: bool = False

    @property
    def key(self) -> str:
        if self.kind != "word":
            return self.text
        return self.text.casefold().replace("’", "'").rstrip("'")


@dataclass(frozen=True)
class _Expr:
    """Numbers written as one expression: "7", "25-30", "tra 5 e 8", "two hundred and five"."""

    first: int  # token index where it starts ("tra" included)
    last: int  # token index of its last number
    low: float | None = None
    high: float | None = None
    why: str | None = None  # set when it cannot be read as one count or range


@dataclass(frozen=True)
class _Count:
    start: int
    end: int
    unit: CountUnit | None
    low: float | None = None
    high: float | None = None
    qualifier: Qualifier | None = None
    why: str | None = None  # a count of the noun we cannot read: the span is then unknown


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
    if unreadable := next((c for c in counts if c.why is not None), None):
        return _unknown(span, unreadable.unit, unreadable.why)
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
    assert c.low is not None and c.high is not None and c.unit is not None
    raw = span[c.start : c.end]
    if c.qualifier is not None:
        q = Quantity(kind="vague", unit=c.unit, raw=raw)
        return ParsedQuantity(q, c.qualifier, c.low, f"hedged number ({c.qualifier})")
    if not (c.low.is_integer() and c.high.is_integer()):
        return _unknown(span, c.unit, "fractional count")
    if c.low == c.high:
        return ParsedQuantity(Quantity(kind="exact", value=c.low, unit=c.unit, raw=raw))
    return ParsedQuantity(Quantity(kind="range", low=c.low, high=c.high, unit=c.unit, raw=raw))


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
            signed = m["sign"] is not None
            tokens.append(_Token("num", m["num"], m.start(), m.end(), m["suffix"] or "", signed))
        else:
            kind = "word" if m["word"] is not None else "punct"
            tokens.append(_Token(kind, m[0], m.start(), m.end()))
    return sorted(tokens, key=lambda t: t.start)


def _number(text: str, decimal: str | None) -> float | None:
    """Digits as written, or None when they are not one plain number (date, time, fraction,
    or a separator that is a decimal point in one locale and a thousands mark in another)."""
    if text.isdigit():
        return float(text)
    group = re.escape(GROUPING + {",": ".", ".": ","}.get(decimal or "", ""))
    if re.fullmatch(rf"[1-9]\d{{0,2}}([{group}])\d{{3}}(?:\1\d{{3}})*", text):
        return float(re.sub(r"\D", "", text))
    if decimal is not None and re.fullmatch(rf"\d+{re.escape(decimal)}\d+", text):
        return float(text.replace(decimal, "."))
    return None


def _is_number(t: _Token, lex: _Lexicon) -> bool:
    """Token that writes a number, readable or not. Not money, percent, "4pm", "2nd"."""
    if t.kind == "word":
        return t.key in lex.numbers or t.key in lex.compound
    suffix = t.suffix.casefold()
    return t.kind == "num" and (not suffix or suffix in lex.nouns or (suffix,) in lex.after)


def _value(t: _Token, lex: _Lexicon) -> float | None:
    if t.kind == "word":
        return float(lex.numbers[t.key]) if t.key in lex.numbers else None
    return None if t.signed else _number(t.text, lex.decimal)


def _expression(tokens: list[_Token], i: int, span: str, lex: _Lexicon) -> _Expr | None:
    """The numeric expression starting at token i, read whole, else None."""
    t = tokens[i]
    article = t.kind == "word" and t.key in lex.strict  # "uno o due clienti"
    if not (article or _is_number(t, lex)):
        return None
    at, joins = [i], []
    while not tokens[at[-1]].suffix:  # "201pcs", "10+" end it
        j = at[-1]
        if j + 1 < len(tokens) and _is_number(tokens[j + 1], lex):
            if "\n" in span[tokens[j].end : tokens[j + 1].start]:
                break
            at.append(j + 1)
            joins.append("")  # "1 200", "one hundred", "twenty one"
        elif (
            j + 2 < len(tokens)
            and tokens[j + 1].key in lex.connectors | lex.joiners | set(lex.between.values())
            and _is_number(tokens[j + 2], lex)
        ):
            at.append(j + 2)
            joins.append(tokens[j + 1].key)
        else:
            break
    if article and not (len(at) == 2 and joins[0] in lex.connectors):
        return None

    values = [float(lex.strict[t.key]) if article else _value(t, lex)]
    values += [_value(tokens[j], lex) for j in at[1:]]
    if any(tokens[j].signed for j in at):
        return _Expr(i, at[-1], why="signed number")
    if any(v is None for v in values):
        return _Expr(i, at[-1], why="number not readable as a count")
    if len(at) == 1:
        return _Expr(i, i, values[0], values[0])
    between = i > 0 and len(at) == 2 and lex.between.get(tokens[i - 1].key) == joins[0]
    if len(at) > 2 or not (joins[0] in lex.connectors or between):
        return _Expr(i, at[-1], why="several numbers in one expression")
    low, high = values
    assert low is not None and high is not None
    if low >= high:
        return _Expr(i, at[-1], why="not an ascending range")
    return _Expr(i - 1 if between else i, at[-1], low, high)


def _noun_after(tokens: list[_Token], k: int, lex: _Lexicon) -> int | None:
    """Index of the unit noun from token k, across up to MAX_GAP modifiers, else None."""
    for j in range(k, min(k + MAX_GAP + 1, len(tokens))):
        t = tokens[j]
        if t.kind == "word" and t.key in lex.nouns:
            return j
        if t.kind != "word" or t.key not in lex.modifiers:
            return None
    return None


def _hedge_after(tokens: list[_Token], k: int, lex: _Lexicon) -> tuple[Qualifier | None, int]:
    """Hedge starting at token k ("o più", "or so") and the index after it."""
    for phrase, q in lex.after.items():
        if tuple(p.key for p in tokens[k : k + len(phrase)]) == phrase:
            return q, k + len(phrase)
    return None, k


def _hedge_before(prefix: str, lex: _Lexicon) -> tuple[Qualifier | None, int, bool]:
    """Hedge that ends `prefix` ("almeno ", "at least ", "~"), where the hedged text starts,
    and whether a negation we do not understand precedes it ("not over", "non almeno")."""
    stripped = prefix.rstrip()
    qualifier, start = None, len(prefix)
    if stripped.endswith("~"):
        qualifier, start = "approx", len(stripped) - 1
    for phrase, q in lex.before if qualifier is None else ():
        s = len(stripped) - len(phrase)
        tail = stripped[s:].casefold().replace("’", "'")
        if s >= 0 and tail == phrase and (s == 0 or not stripped[s - 1].isalnum()):
            qualifier, start = q, s
            break
    word = re.search(r"([^\W\d_]+)\s*$", prefix[:start])
    return qualifier, start, word is not None and word[1].casefold() in lex.negations


def _counts(tokens: list[_Token], span: str, lex: _Lexicon) -> list[_Count]:
    out, i = [], 0
    while i < len(tokens):
        e = _expression(tokens, i, span, lex)
        if e is not None:
            count = _expression_count(tokens, e, span, lex)
            i = e.last + 1
        else:
            count = _article_count(tokens, i, span, lex) or _approx_count(tokens, i, span, lex)
            i += 1
        if count is not None:
            out.append(count)
            i = max(i, next(j for j, t in enumerate(tokens) if t.end == count.end) + 1)
    return out


def _counts_something_else(tokens: list[_Token], e: _Expr, lex: _Lexicon) -> bool:
    """Money, a size, a date: "€ 2", "tg 2", "(x3)", "October 22", "100 EUR"."""
    prev = [p for p in tokens[max(0, e.first - 2) : e.first] if p.text not in (".", ":")][-1:]
    if prev and (
        prev[0].key in lex.not_before
        or prev[0].key in NON_COUNT_WORDS
        or prev[0].text in CURRENCY_SYMBOLS
    ):
        return True
    nxt = tokens[e.last + 1] if e.last + 1 < len(tokens) else None
    return nxt is not None and (nxt.key in NON_COUNT_WORDS or nxt.text in CURRENCY_SYMBOLS)


def _expression_count(tokens: list[_Token], e: _Expr, span: str, lex: _Lexicon) -> _Count | None:
    if _counts_something_else(tokens, e, lex):
        return None
    last = tokens[e.last]
    suffix = last.suffix.casefold()
    after, k = lex.after.get((suffix,)), e.last + 1  # "10+", "20ish"
    if suffix in lex.nouns:  # "201pcs", "3pz"
        noun: int | None = e.last
    else:
        q, k = _hedge_after(tokens, k, lex)
        after = after or q
        noun = _noun_after(tokens, k, lex)
    hedge, lead, negated = _hedge_before(span[: tokens[e.first].start], lex)

    if noun is not None:  # "7 richieste", "5 units or more"
        q, k = _hedge_after(tokens, noun + 1, lex)
        start, end, unit = tokens[e.first].start, tokens[k - 1].end, _unit(tokens[noun], span, lex)
        after = after or q
    else:  # "richieste: 7", "units: about 3 or more"
        p = max((j for j, t in enumerate(tokens) if t.end <= lead), default=-1)
        if p < 1 or tokens[p].text not in ":=" or tokens[p - 1].key not in lex.nouns:
            return _numbers_before_noun(tokens, e, k, lex)
        start, end, unit = tokens[p - 1].start, tokens[k - 1].end, lex.nouns[tokens[p - 1].key]

    if e.why is not None:
        return _Count(start, end, unit, why=e.why)
    if negated:
        return _Count(start, end, unit, why="negated number")
    if e.low != e.high:  # a range states its own uncertainty; a hedge on it is not understood
        if after is not None:
            return _Count(start, end, unit, why="hedged range")
        return _Count(start, end, unit, e.low, e.high)
    if hedge is not None and noun is not None:
        start = lead
    return _Count(start, end, unit, e.low, e.high, after or hedge)


def _numbers_before_noun(tokens: list[_Token], e: _Expr, k: int, lex: _Lexicon) -> _Count | None:
    """ "5 of the 8 units": two numbers for one noun cannot be told apart."""
    j = k
    while j < len(tokens) and j - k < MAX_GAP and tokens[j].key in lex.modifiers:
        j += 1
    if j > k and j < len(tokens) and _is_number(tokens[j], lex):
        return _Count(tokens[e.first].start, tokens[j].end, None, why="two numbers for one noun")
    return None


def _article_count(tokens: list[_Token], i: int, span: str, lex: _Lexicon) -> _Count | None:
    """ "un cliente", "a new client", "almeno un pezzo", "no requests"."""
    t = tokens[i]
    if t.kind != "word" or t.key not in lex.strict:
        return None
    noun = _noun_after(tokens, i + 1, lex)
    if noun is None:
        return None
    return _hedged(tokens, t.start, noun, float(lex.strict[t.key]), None, span, lex)


def _approx_count(tokens: list[_Token], i: int, span: str, lex: _Lexicon) -> _Count | None:
    """ "una sessantina di pezzi", "a dozen clients", "half a dozen clients"."""
    t = tokens[i]
    if t.kind != "word" or t.key not in lex.approx:
        return None
    noun = _noun_after(tokens, i + 1, lex)
    if noun is None:
        return None
    stated, start, before = float(lex.approx[t.key]), t.start, i - 1
    keys = [p.key for p in tokens[max(0, i - 2) : i]]
    if keys == ["half", "a"]:
        stated, start, before = stated / 2, tokens[i - 2].start, i - 3
    elif keys and keys[-1] in lex.strict:
        start, before = tokens[i - 1].start, i - 2
    if before >= 0 and _is_number(tokens[before], lex):  # "2 dozen clients"
        n = tokens[noun]
        return _Count(tokens[before].start, n.end, _unit(n, span, lex), why="multiplied number")
    return _hedged(tokens, start, noun, stated, "approx", span, lex)


def _hedged(
    tokens: list[_Token],
    start: int,
    noun: int,
    value: float,
    default: Qualifier | None,
    span: str,
    lex: _Lexicon,
) -> _Count:
    """Count from `start` to the noun, with the hedges before it and after the noun."""
    n = tokens[noun]
    unit = _unit(n, span, lex)
    hedge, lead, negated = _hedge_before(span[:start], lex)
    after, k = _hedge_after(tokens, noun + 1, lex)
    if negated:
        return _Count(start, n.end, unit, why="negated number")
    return _Count(lead, tokens[k - 1].end, unit, value, value, hedge or after or default)


def _unit(noun: _Token, span: str, lex: _Lexicon) -> CountUnit:
    key = noun.key if noun.kind == "word" else noun.suffix.casefold()
    if key in lex.people and lex.entered is not None and lex.entered.match(span, noun.end):
        return "visitors"  # "142 people thru the door", "300 persone entrate"
    return lex.nouns[key]


def _only_unit(tokens: list[_Token], lex: _Lexicon) -> CountUnit | None:
    units = {lex.nouns[t.key] for t in tokens if t.kind == "word" and t.key in lex.nouns}
    return units.pop() if len(units) == 1 else None
