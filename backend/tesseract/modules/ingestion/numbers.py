"""Span text → physical quantity with unit (RFC §4.5 "Numeri", `ing.numbers`, ING-09 pure).

The extractor (ING-04) hands over the span that states how many: "7 richieste", "tre clienti",
"8 to 10 clients", "un paio di signore". Code, not the LLM, turns it into a `Quantity`:

- `exact`: one count next to a unit noun
  ("Aurea nera: 6 richieste", "un cliente", "201pcs").
- `range`: two ascending counts ("25-30 pezzi", "3 or 4 people", "tra 5 e 8 clienti").
- `vague`: a vague quantifier from `config/domain.yaml` ("qualche cliente", "a few clients"), or
  a hedged count ("around 28 clients", "una sessantina di pezzi", "at least 3", "5 units or
  more", "not more than 5"). A hedged count is not a count: the `Quantity` carries no value and
  the number as written is kept apart in `ParsedQuantity.stated` with its `qualifier`.
- `unknown`: anything else. A wrong number is worse than no number.

The grammar is an allowlist. A count comes out only when its whole phrase has one of the shapes

    [hedge] number-expression [hedge] [modifier...] unit-noun [hedge]    "almeno 3 pezzi"
    unit-noun (":" | "=") [hedge] number-expression [hedge]              "richieste: 7"
    [hedge] article [modifier...] unit-noun [hedge]                      "un cliente"
    [hedge] [article] approximate-number [modifier...] unit-noun [hedge] "una decina di clienti"

and it sits cleanly in the text:

- Nothing is glued to it but brackets, quotes and closing punctuation. "A123 units", "-5 units",
  "#5 units", "almeno3 pezzi" and "5 units_" are not counts.
- Spaced punctuation next to it is a clause mark, a bracket, a bullet or a slash, never "&",
  "%", "+" or "=". A connector to another number ("one or no requests", "3 & 4") continues it.
- The word before it does not make it a size, date, time, id or amount ("tg 2", "alle 10",
  "style 123"), a fraction, multiple or change ("half a unit", "x 3", "by 5", "rather than 5"),
  or part of a larger quantity ("3 out of 5 units", "3 su 5 pezzi"; "a total of 32 units"
  names the whole and is fine). A number one word before it continues it ("10 through 20
  clients") unless that word is a known link ("in 1 da 2 signore").
- No negation and no hedge that does not touch the number sit in the WINDOW words before it
  ("not exactly 5 units", "at least another 5 units", "almeno altri 3 pezzi").
- The words after it do not continue it or make it a proportion ("3 clienti su 10", "3 clienti
  o 4"), money or a percentage ("requests: 100 %"), and hedge it only in a form we read ("5
  units or so"; not "5 units (approx)", "5 pezzi forse").

A number expression is read whole (numbers joined by a connector, a list separator or a plain
space) and must be one plain integer or an ascending range of two: lists, compound spelled
numbers ("one hundred"), decimals ("2,5", "10.00"), fractions, dates and times ("1/2", "10:05"),
leading zeros and values above MAX_COUNT are unreadable. A hedge on a range ("almeno 25-30",
"3-5 or more") is not understood either: `ParsedQuantity.stated` holds one number, and dropping
the hedge would change the meaning. Any unreadable or unclean count next to a unit noun makes the
whole span `unknown`, with a note that says why; it is never reduced to one of its numbers.
Dashes, hyphens and minus signs are read as "-" first. Two counts in one span are never summed.

The unit comes only from the noun: clients, requests, pieces and visitors stay distinct units
("cinque clienti" never becomes five pieces). Spelled numbers, unit nouns and decimal separators
exist for Italian and English; other languages get digits and vague quantifiers only, so their
counts come out `unknown` until their nouns are added. Money and percentages are out of scope
(RFC §6.5 ING-09: extended notations are S).

Pure code: text and vague quantifiers in, `Quantity` out. `load_vague_quantifiers` is the only
function that reads a file, and only the config file it is given.
"""

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, replace
from functools import cache
from pathlib import Path
from typing import Literal, cast

import yaml

from tesseract.core.contracts.observations import Quantity

PARSER_VERSION = "numbers-v3"

Qualifier = Literal["approx", "at_least", "at_most"]
CountUnit = Literal["units", "customers", "requests", "visitors"]

MAX_GAP = 3  # modifiers allowed between a number and its noun: "3 of our regular clients"
MAX_COUNT = 10_000_000  # a larger "count" is an id, a total or a typo
WINDOW = 3  # words before a count where a negation or a loose hedge makes it unknown

# Dashes, hyphens and minus signs, read as "-". One character for one: offsets do not move.
DASHES = str.maketrans(dict.fromkeys("‐‑‒–—―⁃−⸺⸻﹘﹣－", "-"))
CURRENCY_SYMBOLS = frozenset("€$£¥₩")
# Words next to a number that make it money or a percentage, never a count.
NON_COUNT_WORDS = frozenset(
    "eur euro euros usd dollars gbp pounds chf jpy yen krw cny rmb hkd aud sgd aed dkk k grand "
    "percent pct percento".split()
)
# Separators that only ever group thousands: apostrophes (Swiss) and non-breaking spaces.
GROUPING = "'’   "
# Punctuation that may touch a count phrase with no space: "(5 units)", "5 units,", "units—".
GLUED_BEFORE = frozenset('(["“«„')
GLUED_AFTER = frozenset(',.;:!?)]"”»…-')
# ... and that may stand next to it, spaced: clause marks, brackets, bullets, "trans / 32 units".
SPACED = frozenset(',.;:!?()[]"“”«»„…-/•*|')
# Marks that end the clause scanned for loose hedges and negations.
CLAUSE_END = frozenset(".;:!?")
# "No. 5 units", "n. 5 pezzi": a number, not a count.
ID_ABBREVIATIONS = frozenset("no n nr num".split())

LONGER = "part of a longer numeric expression"
PART = "a part, a multiple or a proportion of the count"
NOT_A_COUNT = "a size, date, time, id or amount, not a count"


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
    connectors: frozenset[str] = frozenset({"-"})  # ranges: "25-30", "3 o 4"
    joiners: frozenset[str] = frozenset({",", "/"})  # lists: "3, 4", "3 e 4", "3 / 4"
    between: Mapping[str, str] = field(default_factory=dict)  # "tra" → "e": "tra 5 e 8"
    decimal: str | None = None  # decimal separator; the other of "." and "," groups thousands
    not_before: frozenset[str] = frozenset()  # "tg 2", "(x3)", "October 22", "alle 10"
    stop_before: frozenset[str] = frozenset()  # "half a unit", "x 3", "by 5", "rather than 5"
    links: frozenset[str] = frozenset()  # may join a number and a count: "in 1 da 2 signore"
    partitive: frozenset[str] = frozenset()  # "3 out of 5 units", "3 su 5 pezzi" ...
    whole: frozenset[str] = frozenset()  # ... unless the word names the whole: "a total of 32"
    determiners: frozenset[str] = frozenset()  # skipped after a partitive: "half of the 8 units"
    negations: frozenset[str] = frozenset()
    adverbs: frozenset[str] = frozenset()  # hedges after a count we do not read: "5 pezzi forse"
    people: frozenset[str] = frozenset()  # nouns that mean visitors when they enter the store
    entered: re.Pattern[str] | None = None
    before: tuple[tuple[str, Qualifier], ...] = ()  # hedges before the number, longest first
    after: Mapping[tuple[str, ...], Qualifier] = field(default_factory=dict)  # ... and after


def _numbers(words: str, first: int = 0, step: int = 1) -> dict[str, int]:
    return {w: first + i * step for i, w in enumerate(words.split())}


def _nouns(**by_unit: str) -> dict[str, CountUnit]:
    return {w: cast(CountUnit, unit) for unit, words in by_unit.items() for w in words.split()}


def _words(words: str) -> frozenset[str]:
    return frozenset(words.split())


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
        compound=_words("cento mille mila milione milioni"),
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
        modifiers=_words(
            "altri altre altro altra nuovi nuove nuovo nuova ulteriori vari varie di dei degli "
            "delle nostri nostre nostro nostra"
        ),
        connectors=frozenset({"-", "o", "a"}),
        joiners=frozenset({",", "/", "e"}),
        between={"tra": "e", "fra": "e"},
        decimal=",",
        not_before=_words(
            "tg taglia taglie misura mis x gennaio febbraio marzo aprile maggio giugno luglio "
            "agosto settembre ottobre novembre dicembre gen feb mar apr mag giu lug ago set ott "
            "nov dic alle dalle ore h nr num numero rif sku stile codice cod modello art id"
        ),
        stop_before=_words(
            "metà meta mezzo mezza terzo terzi quarto quarti volte ogni x più piu meno contro "
            "invece anziché"
        ),
        links=_words("da in con per"),
        partitive=_words("di del dello della dei degli delle su sul sullo sulla sui sugli sulle"),
        whole=_words("totale gruppo gruppi comitiva famiglia lotto consegna ordine"),
        determiners=_words("il lo la l i gli le questi queste quei quegli quelle nostri nostre"),
        negations=_words("non mai nemmeno neanche neppure senza né"),
        adverbs=_words("forse probabilmente pressappoco all'incirca"),
        people=frozenset({"persona", "persone"}),
        entered=re.compile(r"\s*(?:sono\s+)?entrat[eio]\b", re.IGNORECASE),
        before=_hedges(
            approx="più o meno|piu' o meno|all'incirca|circa|quasi|intorno ai|intorno alle|"
            "intorno a|sui|sulle|tipo|forse",
            at_least="almeno|non meno di|più di|piu' di|oltre|un minimo di|minimo di|minimo",
            at_most="non più di|non piu' di|non oltre|meno di|al massimo|un massimo di|"
            "massimo di|massimo|fino a",
        ),
        after=_after(
            at_least="+|o più|o piu'|e più|e piu'",
            at_most="o meno",
            approx="circa|più o meno|piu' o meno",
        ),
    ),
    "en": _Lexicon(
        numbers=_numbers(
            "zero one two three four five six seven eight nine ten eleven twelve thirteen "
            "fourteen fifteen sixteen seventeen eighteen nineteen twenty"
        )
        | _numbers("thirty forty fifty sixty seventy eighty ninety", 30, 10),
        compound=_words("hundred hundreds thousand thousands million millions"),
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
        modifiers=_words(
            "more other new different additional extra separate regular returning repeat loyal "
            "vip local foreign international potential possible individual young older elderly "
            "male female of the our asian european american canadian british english french "
            "german italian spanish swiss dutch danish chinese japanese korean taiwanese "
            "singaporean australian saudi arab emirati russian indian brazilian mexican"
        ),
        connectors=frozenset({"-", "to", "or"}),
        joiners=frozenset({",", "/", "and"}),
        between={"between": "and"},
        decimal=".",
        not_before=_words(
            "size sizes sz x january february march april may june july august september "
            "october november december jan feb mar apr jun jul aug sep sept oct nov dec at h "
            "nr num ref sku style code model ticket room page line row id"
        ),
        stop_before=_words(
            "out half halves quarter quarters third thirds times every each x than vs versus "
            "instead plus minus by up down"
        ),
        links=_words("from in with for"),
        partitive=frozenset({"of"}),
        whole=_words("total group groups party family batch delivery shipment order"),
        determiners=_words("the these those our my your their its his her"),
        negations=_words(
            "not never without neither nor none nobody nothing hardly barely dont didnt doesnt "
            "isnt wasnt arent werent cant cannot wont havent hasnt hadnt couldnt wouldnt"
        ),
        adverbs=_words("approximately approx roughly maybe perhaps probably possibly"),
        people=frozenset({"people", "person", "persons"}),
        entered=re.compile(
            r"\s*(?:came\s+)?(?:in\s+)?(?:thru|through)\s+the\s+doors?\b|\s+in\s*(?:[,;.)]|$)",
            re.IGNORECASE,
        ),
        before=_hedges(
            approx="approximately|approx.|approx|roughly|around|about|nearly|almost|close to|"
            "some|maybe|perhaps|probably|more or less|give or take",
            at_least="at least|more than|no fewer than|no less than|not fewer than|"
            "not less than|not under|not below|upwards of|a minimum of|minimum of|over|above",
            at_most="no more than|not more than|not over|not above|fewer than|less than|at most|"
            "up to|a maximum of|maximum of|under|below",
        ),
        after=_after(
            at_least="+|or more",
            at_most="or fewer|or less",
            approx="or so|ish|- ish|more or less|give or take",
        ),
    ),
}
_EMPTY = _Lexicon()

_TOKEN = re.compile(
    # ASCII digits with whatever joins them, read later as one number or rejected whole:
    # "1.200", "1 200" (NBSP), "10:05", "10/22", "1/2". Other digits ("３", "٣") are punctuation.
    rf"(?P<num>[0-9]+(?:[.,:/{GROUPING}][0-9]+)*)(?P<suffix>[^\W\d_]+|[%+€$£¥₩])?"
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
class _Expr:
    """Numbers written as one expression: "7", "25-30", "tra 5 e 8", "two hundred and five"."""

    first: int  # token index where it starts ("tra" included)
    last: int  # token index of its last number
    low: int | None = None
    high: int | None = None
    why: str | None = None  # set when it cannot be read as one count or range


@dataclass(frozen=True)
class _Count:
    first: int  # token index where the phrase starts, hedge or noun-first noun included
    last: int  # token index where it ends, trailing hedge included
    unit: CountUnit | None
    low: int | None = None
    high: int | None = None
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
    text = span.translate(DASHES)
    tokens = _tokenize(text, _vague_pattern(tuple(vague)))
    counts = _counts(tokens, text, lex)
    if unreadable := next((c for c in counts if c.why is not None), None):
        return _unknown(span, unreadable.unit, unreadable.why)
    if len(counts) > 1:
        return _unknown(span, None, "several counts in one span")
    if counts:
        return _from_count(counts[0], tokens, span)
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
            unit, end = _unit(tokens[noun], text, lex), tokens[noun].end
        q = Quantity(kind="vague", unit=unit, raw=span[t.start : end])
        return ParsedQuantity(q, note="vague quantifier")
    has_number = any(t.kind == "num" or t.key in lex.numbers for t in tokens)
    return _unknown(
        span, _only_unit(tokens, lex), "no count next to a unit noun" if has_number else "no count"
    )


def _unknown(span: str, unit: CountUnit | None, note: str) -> ParsedQuantity:
    return ParsedQuantity(Quantity(kind="unknown", unit=unit, raw=span.strip() or None), note=note)


def _from_count(c: _Count, tokens: list[_Token], span: str) -> ParsedQuantity:
    assert c.low is not None and c.high is not None and c.unit is not None
    raw = span[tokens[c.first].start : tokens[c.last].end]
    if c.qualifier is not None:
        q = Quantity(kind="vague", unit=c.unit, raw=raw)
        return ParsedQuantity(q, c.qualifier, float(c.low), f"hedged number ({c.qualifier})")
    if c.low == c.high:
        return ParsedQuantity(Quantity(kind="exact", value=float(c.low), unit=c.unit, raw=raw))
    q = Quantity(kind="range", low=float(c.low), high=float(c.high), unit=c.unit, raw=raw)
    return ParsedQuantity(q)


@cache
def _vague_pattern(words: tuple[str, ...]) -> re.Pattern[str] | None:
    alts = []
    for w in sorted({w.strip() for w in words if w.strip()}, key=len, reverse=True):
        body = r"\s+".join(re.escape(part) for part in w.split())
        # Latin-script words match whole words; CJK words have no spaces around them.
        alts.append(rf"(?<!\w){body}(?!\w)" if all(ord(c) < 0x2E80 for c in w) else body)
    return re.compile("|".join(alts), re.IGNORECASE) if alts else None


def _tokenize(text: str, vague: re.Pattern[str] | None) -> list[_Token]:
    masked = [(m.start(), m.end()) for m in vague.finditer(text)] if vague else []
    tokens = [_Token("vague", text[s:e], s, e) for s, e in masked]
    for m in _TOKEN.finditer(text):
        if any(s <= m.start() < e for s, e in masked):
            continue
        if m["num"] is not None:
            tokens.append(_Token("num", m["num"], m.start(), m.end(), m["suffix"] or ""))
        else:
            kind = "word" if m["word"] is not None else "punct"
            tokens.append(_Token(kind, m[0], m.start(), m.end()))
    return sorted(tokens, key=lambda t: t.start)


@cache
def _keys(phrase: str) -> tuple[str, ...]:
    """Word keys of a hedge phrase, as tokens of a span would have them."""
    return tuple(_Token("word", m[0], 0, 0).key for m in _TOKEN.finditer(phrase) if m["word"])


def _number(text: str, decimal: str | None) -> int | None:
    """Digits as one count, else None: a date, time, fraction or decimal, a leading zero, a
    separator that groups thousands in one locale and not in another, or more than MAX_COUNT."""
    group = re.escape(GROUPING + {",": ".", ".": ","}.get(decimal or "", ""))
    plain = re.fullmatch(r"0|[1-9][0-9]*", text)
    grouped = re.fullmatch(rf"[1-9][0-9]{{0,2}}([{group}])[0-9]{{3}}(?:\1[0-9]{{3}})*", text)
    digits = re.sub(r"[^0-9]", "", text)
    if not (plain or grouped) or len(digits) > len(str(MAX_COUNT)) or int(digits) > MAX_COUNT:
        return None
    return int(digits)


def _is_number(t: _Token, lex: _Lexicon) -> bool:
    """Token that writes a number, readable or not. Not money, percent, "4pm", "2nd"."""
    if t.kind == "word":
        return t.key in lex.numbers or t.key in lex.compound
    suffix = t.suffix.casefold()
    return t.kind == "num" and (not suffix or suffix in lex.nouns or (suffix,) in lex.after)


def _numberish(t: _Token, lex: _Lexicon) -> bool:
    """Token that writes or stands for any number: "5%", "A1"'s digits, "one", "a", "molti"."""
    return t.kind in ("num", "vague") or any(
        t.key in words for words in (lex.numbers, lex.compound, lex.strict, lex.approx)
    )


def _writes_number(t: _Token, lex: _Lexicon) -> bool:
    """Digits of any kind ("5", "5pm", "38k") or a spelled number, not an article."""
    return t.kind == "num" or any(t.key in w for w in (lex.numbers, lex.compound, lex.approx))


def _value(t: _Token, lex: _Lexicon) -> int | None:
    if t.kind == "word":
        return lex.numbers.get(t.key)
    return _number(t.text, lex.decimal)


def _expression(tokens: list[_Token], i: int, text: str, lex: _Lexicon) -> _Expr | None:
    """The numeric expression starting at token i, read whole, else None."""
    t = tokens[i]
    article = t.kind == "word" and t.key in lex.strict  # "uno o due clienti"
    if not (article or _is_number(t, lex)):
        return None
    at, joins, unclear = [i], [], False
    while not tokens[at[-1]].suffix:  # "201pcs", "10+" end it
        j = at[-1]
        if j + 1 < len(tokens) and _is_number(tokens[j + 1], lex):
            if "\n" in text[tokens[j].end : tokens[j + 1].start]:
                break
            at.append(j + 1)
            joins.append("")  # "1 200", "one hundred", "twenty one"
        elif (
            j + 2 < len(tokens)
            and tokens[j + 1].key in lex.connectors | lex.joiners | set(lex.between.values())
            and _is_number(tokens[j + 2], lex)
        ):
            c, glued_left = tokens[j + 1], tokens[j].end == tokens[j + 1].start
            # "3 -5", "3- 5": a sign or a range, we cannot tell.
            unclear |= c.text == "-" and glued_left != (c.end == tokens[j + 2].start)
            at.append(j + 2)
            joins.append(c.key)
        else:
            break
    if article and not (len(at) == 2 and joins[0] in lex.connectors):
        return None

    values = [lex.strict[t.key] if article else _value(t, lex)]
    values += [_value(tokens[j], lex) for j in at[1:]]
    if unclear:
        return _Expr(i, at[-1], why="sign or range unclear")
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


def _hedge_before(prefix: str, lex: _Lexicon) -> tuple[Qualifier | None, int]:
    """Hedge that ends `prefix` ("almeno ", "at least ", "~") and where the hedged text starts."""
    stripped = prefix.rstrip()
    if stripped.endswith("~"):
        return "approx", len(stripped) - 1
    for phrase, q in lex.before:
        s = len(stripped) - len(phrase)
        tail = stripped[s:].casefold().replace("’", "'")
        if s >= 0 and tail == phrase and (s == 0 or not stripped[s - 1].isalnum()):
            return q, s
    return None, len(prefix)


def _token_at(tokens: list[_Token], pos: int) -> int:
    return next(j for j, t in enumerate(tokens) if t.start >= pos)


def _counts(tokens: list[_Token], text: str, lex: _Lexicon) -> list[_Count]:
    out, i = [], 0
    while i < len(tokens):
        e = _expression(tokens, i, text, lex)
        if e is not None:
            count = _expression_count(tokens, e, text, lex)
            i = e.last + 1
        else:
            count = _article_count(tokens, i, text, lex) or _approx_count(tokens, i, text, lex)
            i += 1
        if count is not None:
            if count.why is None and (why := _context_problem(tokens, count, text, lex)):
                count = replace(count, low=None, high=None, qualifier=None, why=why)
            out.append(count)
            i = max(i, count.last + 1)
    return out


def _expression_count(tokens: list[_Token], e: _Expr, text: str, lex: _Lexicon) -> _Count | None:
    last = tokens[e.last]
    suffix = last.suffix.casefold()
    after, k = lex.after.get((suffix,)), e.last + 1  # "10+", "20ish"
    if suffix in lex.nouns:  # "201pcs", "3pz"
        noun: int | None = e.last
    else:
        q, k = _hedge_after(tokens, k, lex)
        after = after or q
        noun = _noun_after(tokens, k, lex)
    hedge, lead = _hedge_before(text[: tokens[e.first].start], lex)
    first = _token_at(tokens, lead)

    if noun is not None:  # "7 richieste", "5 units or more"
        q, k = _hedge_after(tokens, noun + 1, lex)
        unit, after = _unit(tokens[noun], text, lex), after or q
    else:  # "richieste: 7", "units: about 3 or more"
        p = first - 1
        if p < 1 or tokens[p].text not in ":=" or tokens[p - 1].key not in lex.nouns:
            return _numbers_before_noun(tokens, e, k, lex)
        first, unit = p - 1, lex.nouns[tokens[p - 1].key]

    if e.why is not None:
        return _Count(first, k - 1, unit, why=e.why)
    if hedge is not None and after is not None and hedge != after:
        return _Count(first, k - 1, unit, why="conflicting hedges")
    if e.low != e.high:  # a range states its own uncertainty; a hedge on it is not understood
        if hedge is not None or after is not None:
            return _Count(first, k - 1, unit, why="hedged range")
        return _Count(first, k - 1, unit, e.low, e.high)
    return _Count(first, k - 1, unit, e.low, e.high, after or hedge)


def _numbers_before_noun(tokens: list[_Token], e: _Expr, k: int, lex: _Lexicon) -> _Count | None:
    """ "5 of the 8 units": two numbers for one noun cannot be told apart."""
    j = k
    while j < len(tokens) and j - k < MAX_GAP and tokens[j].key in lex.modifiers:
        j += 1
    if j > k and j < len(tokens) and _is_number(tokens[j], lex):
        return _Count(e.first, j, None, why="two numbers for one noun")
    return None


def _article_count(tokens: list[_Token], i: int, text: str, lex: _Lexicon) -> _Count | None:
    """ "un cliente", "a new client", "almeno un pezzo", "no requests"."""
    t = tokens[i]
    if t.kind != "word" or t.key not in lex.strict:
        return None
    noun = _noun_after(tokens, i + 1, lex)
    if noun is None:
        return None
    return _hedged(tokens, i, noun, lex.strict[t.key], None, text, lex)


def _approx_count(tokens: list[_Token], i: int, text: str, lex: _Lexicon) -> _Count | None:
    """ "una sessantina di pezzi", "a dozen clients", "half a dozen clients"."""
    t = tokens[i]
    if t.kind != "word" or t.key not in lex.approx:
        return None
    noun = _noun_after(tokens, i + 1, lex)
    if noun is None:
        return None
    stated, start = lex.approx[t.key], i
    keys = [p.key for p in tokens[max(0, i - 2) : i]]
    if keys == ["half", "a"]:
        stated, start = stated // 2, i - 2
    elif keys and keys[-1] in lex.strict:
        start = i - 1
    if start > 0 and _is_number(tokens[start - 1], lex):  # "2 dozen clients"
        n = tokens[noun]
        return _Count(start - 1, noun, _unit(n, text, lex), why="multiplied number")
    return _hedged(tokens, start, noun, stated, "approx", text, lex)


def _hedged(
    tokens: list[_Token],
    start: int,
    noun: int,
    value: int,
    default: Qualifier | None,
    text: str,
    lex: _Lexicon,
) -> _Count:
    """Count from token `start` to the noun, with the hedges before it and after the noun."""
    unit = _unit(tokens[noun], text, lex)
    hedge, lead = _hedge_before(text[: tokens[start].start], lex)
    after, k = _hedge_after(tokens, noun + 1, lex)
    if hedge is not None and after is not None and hedge != after:
        return _Count(start, k - 1, unit, why="conflicting hedges")
    return _Count(_token_at(tokens, lead), k - 1, unit, value, value, hedge or after or default)


def _context_problem(tokens: list[_Token], c: _Count, text: str, lex: _Lexicon) -> str | None:
    """Why the text glued inside a count phrase, or around it, makes it something else."""
    inner = tokens[c.first : c.last + 1]
    for a, b in zip(inner, inner[1:], strict=False):
        if a.end == b.start and {a.kind, b.kind} == {"word", "num"}:
            return "number glued to a word"  # "almeno3 pezzi"
    return (
        _before_problem(tokens, c.first, lex)
        or _loose_problem(tokens, c.first, text, lex)
        or _after_problem(tokens, c.last, lex)
    )


def _before_problem(tokens: list[_Token], first: int, lex: _Lexicon) -> str | None:
    """The token right before the phrase, and what it says about the number."""
    if first == 0:
        return None
    j = first - 1
    p = tokens[j]
    glued = p.end == tokens[first].start
    if _numberish(p, lex):
        return LONGER  # "A123 units", "one or no requests"
    if p.kind == "punct":
        if glued and p.text in "-+":
            return "signed number"
        if p.text not in (GLUED_BEFORE if glued else SPACED):
            return f"{p.text!r} next to the count"
        if j > 0 and p.text in ",/-" and _numberish(tokens[j - 1], lex):
            return LONGER
        if j > 0 and p.text in ".:" and _names_no_count(tokens[j - 1], lex):
            return NOT_A_COUNT  # "size: 2 units"
        if j > 0 and p.text == "." and tokens[j - 1].key in ID_ABBREVIATIONS:
            return NOT_A_COUNT  # "No. 5 units"
        return None
    if glued:
        return "number glued to a word"
    if _names_no_count(p, lex):
        return NOT_A_COUNT
    if p.key in lex.stop_before:
        return PART
    if p.key in lex.connectors | lex.joiners and j > 0 and _numberish(tokens[j - 1], lex):
        return LONGER
    if j > 0 and _writes_number(tokens[j - 1], lex) and p.key not in lex.links:
        return LONGER  # "10 through 20 clients", "dal 10 al 20 clienti"; not "in 1 da 2 signore"
    # "3 out of 5 units", "metà dei 10 pezzi", "half of the 8 units"; not "a total of 32 units".
    while j > 0 and p.key in lex.determiners and first - j <= 2:
        j -= 1
        p = tokens[j]
    if p.key in lex.partitive and not (j > 0 and tokens[j - 1].key in lex.whole):
        return PART
    return None


def _names_no_count(t: _Token, lex: _Lexicon) -> bool:
    return t.key in lex.not_before or t.key in NON_COUNT_WORDS or t.text in CURRENCY_SYMBOLS


def _loose_problem(tokens: list[_Token], first: int, text: str, lex: _Lexicon) -> str | None:
    """A negation or a hedge in the WINDOW words before the phrase, not touching it: "not
    exactly 5 units", "at least another 5 units", "almeno altri 3 pezzi"."""
    longest = max((len(_keys(p)) for p, _ in lex.before), default=0)
    keys: list[str] = []  # nearest first
    for j in range(first - 1, -1, -1):
        t = tokens[j]
        if t.text in CLAUSE_END or "\n" in text[t.end : tokens[j + 1].start]:
            break
        if t.kind != "punct":
            keys.append(t.key)
        if len(keys) >= WINDOW + longest:
            break
    if any(k in lex.negations or k.endswith("n't") for k in keys[:WINDOW]):
        return "negated count"
    for phrase, _ in lex.before:
        words = _keys(phrase)
        for g in range(WINDOW):
            if words and tuple(reversed(keys[g : g + len(words)])) == words:
                return "hedge not next to the number"
    return None


def _after_problem(tokens: list[_Token], last: int, lex: _Lexicon) -> str | None:
    """The tokens right after the phrase: "3 clienti su 10", "3 clienti o 4", "100 %"."""
    if last + 1 == len(tokens):
        return None
    n = tokens[last + 1]
    glued = tokens[last].end == n.start
    nxt = tokens[last + 2] if last + 2 < len(tokens) else None
    continues = nxt is not None and _numberish(nxt, lex)
    if n.kind == "punct":
        if n.text not in (GLUED_AFTER if glued else SPACED):
            return f"{n.text!r} next to the count"
        if n.text in "-/" and continues:
            return LONGER
        return "hedge after the count" if _hedge_follows(tokens, last + 1, lex) else None
    if glued:
        return "count glued to a number"  # "units5"
    if n.key in lex.adverbs:
        return "hedge after the count"  # "5 pezzi forse", "5 units approximately"
    if n.key in NON_COUNT_WORDS:
        return NOT_A_COUNT
    if n.key in lex.connectors | lex.joiners and continues:
        return LONGER
    j, part = last + 1, False
    skip = lex.partitive | lex.determiners | lex.stop_before
    while j < len(tokens) and j - last <= 3 and tokens[j].key in skip:
        part = part or tokens[j].key not in lex.determiners
        j += 1
    if part and j < len(tokens) and _numberish(tokens[j], lex):
        return PART
    return None


def _hedge_follows(tokens: list[_Token], k: int, lex: _Lexicon) -> bool:
    """A hedge behind the punctuation at token k: "5 units (approx)", "5 pezzi, più o meno",
    "5 units, at least", "5 units (about)"; not "3 clients, about the Aurea"."""
    while k < len(tokens) and tokens[k].text in "(,-" and tokens[k].kind == "punct":
        k += 1
    keys = [t.key for t in tokens[k : k + 4]]
    if keys and keys[0] in lex.adverbs:
        return True
    if any(tuple(keys[: len(p)]) == p for p in lex.after):
        return True
    for phrase, _ in lex.before:
        words = _keys(phrase)
        if not words or tuple(keys[: len(words)]) != words:
            continue
        end = k + len(words)
        if len(words) > 1 or end == len(tokens) or tokens[end].text in CLAUSE_END | {")"}:
            return True
    return False


def _unit(noun: _Token, text: str, lex: _Lexicon) -> CountUnit:
    key = noun.key if noun.kind == "word" else noun.suffix.casefold()
    if key in lex.people and lex.entered is not None and lex.entered.match(text, noun.end):
        return "visitors"  # "142 people thru the door", "300 persone entrate"
    return lex.nouns[key]


def _only_unit(tokens: list[_Token], lex: _Lexicon) -> CountUnit | None:
    units = {lex.nouns[t.key] for t in tokens if t.kind == "word" and t.key in lex.nouns}
    return units.pop() if len(units) == 1 else None
