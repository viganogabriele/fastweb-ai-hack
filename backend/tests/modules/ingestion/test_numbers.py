"""ING-09: span text → Quantity. Phrasings are taken from dev-store closing emails
(MIL01, MIL02 in Italian; LON01, NYC01, SYD01 in English), see config/eval_split.yaml."""

import pytest

from tessera.core.config import REPO_ROOT
from tessera.modules.ingestion.numbers import load_vague_quantifiers, parse_quantity

VAGUE = load_vague_quantifiers(REPO_ROOT / "config" / "domain.yaml")


def parse(span: str, lang: str):
    return parse_quantity(span, lang, VAGUE[lang])


@pytest.mark.parametrize(
    ("lang", "span", "value", "unit", "raw"),
    [
        ("it", "Maire nera: 6 richieste, 5 in tg 2", 6, "requests", "6 richieste"),
        ("it", "Maire nera: 8 richieste (1, 1, 1, 2, 2, 4, 4, 3)", 8, "requests", "8 richieste"),
        ("it", "SETTE richieste di Maire nera oggi", 7, "requests", "SETTE richieste"),
        ("it", "Tre clienti ci hanno chiesto se potevamo", 3, "customers", "Tre clienti"),
        ("it", "Ambrine marrone: chiesta da 3 clienti, venduta una in 1", 3, "customers", None),
        ("it", "Ambrine marrone chiesta in 1 da 2 signore, niente", 2, "customers", "2 signore"),
        ("it", "Ho 2 persone in lista per la 0 e la 2", 2, "customers", "2 persone"),
        ("it", "Card Days in corso, altri due clienti persi per lo sconto", 2, "customers", None),
        ("it", "Maire nera chiesta in 0, 1 e 3: tre clienti, tre no", 3, "customers", None),
        ("it", "La Bady nera vola, 13 pezzi oggi!", 13, "units", "13 pezzi"),
        ("it", "Beanie rosa 5 pezzi, Arneb blu 5, cardigan logo nero", 5, "units", "5 pezzi"),
        ("it", "da sabato 19 a ieri sera abbiamo contato 14 richieste", 14, "requests", None),
        ("it", "un cliente cercava il cardigan logo nero", 1, "customers", "un cliente"),
        ("it", "Una signora cercava la polo bianca", 1, "customers", "Una signora"),
        ("it", "nessuna richiesta per la Maire oggi", 0, "requests", "nessuna richiesta"),
        ("it", "Maire nera, richieste: 7", 7, "requests", "richieste: 7"),
        ("it", "1.200 visitatori", 1200, "visitors", None),
        ("it", "300 persone entrate oggi", 300, "visitors", "300 persone"),
        (
            "en",
            "Black Maire - I had 7 people ask today, sizes 0 (x3), 2 (x1)",
            7,
            "customers",
            None,
        ),
        ("en", "Logo tee black in S - we had 3 people ask and we have NONE", 3, "customers", None),
        ("en", "Two clients said it runs small", 2, "customers", "Two clients"),
        ("en", "2 ladies asked for the cable knit in black", 2, "customers", "2 ladies"),
        ("en", "ambrine: 3 clients today asking for the brown one", 3, "customers", None),
        ("en", "Product: Maire black 7 units today", 7, "units", "7 units"),
        ("en", "- 18 trans / 32 units", 32, "units", "32 units"),
        ("en", "Delivery 201pcs", 201, "units", "201pcs"),
        ("en", "Traffic & Conv: 414 visitors, 11%", 414, "visitors", "414 visitors"),
        ("en", "142 people thru the door all day", 142, "visitors", "142 people"),
        ("en", "61 people in, 3 sales", 61, "visitors", "61 people"),
        ("en", "1,200 visitors", 1200, "visitors", None),
        ("en", "a client asked for the black Maire", 1, "customers", "a client"),
        ("en", "no requests for it today", 0, "requests", "no requests"),
        # Known modifiers between the number and its noun.
        ("en", "3 Korean clients", 3, "customers", "3 Korean clients"),
        ("en", "3 of our regular clients", 3, "customers", "3 of our regular clients"),
        ("it", "3 dei nostri clienti", 3, "customers", "3 dei nostri clienti"),
        ("en", "a new client", 1, "customers", "a new client"),
        ("en", "thirty clients", 30, "customers", "thirty clients"),
        # Locale-aware separators; non-breaking spaces only ever group thousands.
        ("en", "1\u00a0200 visitors", 1200, "visitors", None),
        ("en", "1\u202f200 visitors", 1200, "visitors", None),
        ("en", "1\u2009200 visitors", 1200, "visitors", None),
        ("en", "24'620 visitors", 24620, "visitors", None),
        ("it", "1.234.567 visitatori", 1234567, "visitors", None),
        ("en", "requests = 1,200", 1200, "requests", "requests = 1,200"),
        # A bullet is not a sign; a count after a date or time still counts.
        ("en", "- 5 units", 5, "units", "5 units"),
        ("en", "on 10/22: 3 clients asked", 3, "customers", "3 clients"),
        ("en", "3 clients at 5pm", 3, "customers", "3 clients"),
    ],
)
def test_exact(lang: str, span: str, value: int, unit: str, raw: str | None) -> None:
    r = parse(span, lang)
    assert (r.quantity.kind, r.quantity.value, r.quantity.unit) == ("exact", value, unit)
    assert r.qualifier is None and r.stated is None
    assert r.quantity.raw is not None and r.quantity.raw in span
    if raw is not None:
        assert r.quantity.raw == raw


@pytest.mark.parametrize(
    ("lang", "span", "low", "high", "unit", "raw"),
    [
        ("it", "gruppi da 4-6 persone", 4, 6, "customers", "4-6 persone"),
        ("it", "3 o 4 clienti l'hanno chiesta", 3, 4, "customers", "3 o 4 clienti"),
        ("it", "tra 5 e 8 clienti", 5, 8, "customers", "tra 5 e 8 clienti"),
        ("it", "Se riuscite a riservarci almeno 25-30 pezzi", 25, 30, "units", "25-30 pezzi"),
        ("en", "Maybe 8 to 10 clients tried pieces", 8, 10, "customers", "8 to 10 clients"),
        ("en", "3 or 4 people today said they saw the ads", 3, 4, "customers", "3 or 4 people"),
        ("en", "people buying 2-3 pieces", 2, 3, "units", "2-3 pieces"),
        ("en", "between 5 and 8 requests", 5, 8, "requests", "between 5 and 8 requests"),
        ("it", "richieste: 3-5", 3, 5, "requests", "richieste: 3-5"),
        ("it", "richieste: 3 o 4", 3, 4, "requests", "richieste: 3 o 4"),
        ("it", "uno o due clienti", 1, 2, "customers", "uno o due clienti"),
        ("it", "da 3 a 5 pezzi", 3, 5, "units", "3 a 5 pezzi"),
        ("en", "five-six clients", 5, 6, "customers", "five-six clients"),
    ],
)
def test_range(lang: str, span: str, low: int, high: int, unit: str, raw: str) -> None:
    q = parse(span, lang).quantity
    assert (q.kind, q.low, q.high, q.unit, q.raw) == ("range", low, high, unit, raw)


@pytest.mark.parametrize(
    ("lang", "span", "unit", "raw"),
    [
        ("it", "finalmente qualche cliente del client book", "customers", "qualche cliente"),
        ("it", "un paio di clienti per la Maire", "customers", "un paio di clienti"),
        ("it", "molte coreane, tante richieste", "requests", "tante richieste"),
        ("it", "oggi tanti", None, "tanti"),
        ("en", "A couple of people mentioned the ads", "customers", "A couple of people"),
        ("en", "A few Canadian clients in town", "customers", "A few Canadian clients"),
        ("en", "quite a few requests for the Maire", "requests", "quite a few requests"),
        ("en", "lots of tourists today", "customers", "lots of tourists"),
    ],
)
def test_vague_quantifier(lang: str, span: str, unit: str | None, raw: str) -> None:
    r = parse(span, lang)
    q = r.quantity
    assert (q.kind, q.value, q.low, q.high, q.unit, q.raw) == ("vague", None, None, None, unit, raw)
    assert r.qualifier is None and r.stated is None


@pytest.mark.parametrize(
    ("lang", "span", "qualifier", "stated", "unit", "raw"),
    [
        ("it", "arrivate le Maire nere, una sessantina di pezzi", "approx", 60, "units", None),
        ("it", "una decina di clienti", "approx", 10, "customers", "una decina di clienti"),
        ("it", "circa 20 clienti", "approx", 20, "customers", "circa 20 clienti"),
        ("it", "più di 10 clienti", "at_least", 10, "customers", "più di 10 clienti"),
        ("it", "piu' di 10 clienti", "at_least", 10, "customers", "piu' di 10 clienti"),
        ("it", "10 o più richieste", "at_least", 10, "requests", "10 o più richieste"),
        ("it", "non più di 5 pezzi", "at_most", 5, "units", "non più di 5 pezzi"),
        ("en", "around 28 clients purchased on the night", "approx", 28, "customers", None),
        ("en", "We now have roughly 180 pieces of outerwear", "approx", 180, "units", None),
        ("en", "~160 units", "approx", 160, "units", "~160 units"),
        ("en", "20 or so clients", "approx", 20, "customers", "20 or so clients"),
        ("en", "20-ish clients", "approx", 20, "customers", "20-ish clients"),
        ("en", "half a dozen clients", "approx", 6, "customers", "half a dozen clients"),
        ("en", "at least 3 clients we know of turned back", "at_least", 3, "customers", None),
        ("en", "we had at least 12 more requests", "at_least", 12, "requests", None),
        ("en", "10+ requests", "at_least", 10, "requests", "10+ requests"),
        ("en", "Jersey is under 100 units", "at_most", 100, "units", "under 100 units"),
        # Every count form takes the hedges around it.
        ("it", "circa 3pz", "approx", 3, "units", "circa 3pz"),
        ("it", "almeno 3pz", "at_least", 3, "units", "almeno 3pz"),
        ("it", "almeno un pezzo", "at_least", 1, "units", "almeno un pezzo"),
        ("en", "at least a client", "at_least", 1, "customers", "at least a client"),
        ("en", "5 units or more", "at_least", 5, "units", "5 units or more"),
        ("en", "5 clients or fewer", "at_most", 5, "customers", "5 clients or fewer"),
        ("en", "5 units or so", "approx", 5, "units", "5 units or so"),
        ("it", "5 pezzi o più", "at_least", 5, "units", "5 pezzi o più"),
        ("en", "units: 3 or more", "at_least", 3, "units", "units: 3 or more"),
        ("en", "units: about 3", "approx", 3, "units", "units: about 3"),
        ("en", "more than a dozen clients", "at_least", 12, "customers", None),
        # Negated comparisons are read whole, never reversed.
        ("en", "not more than 5 units", "at_most", 5, "units", "not more than 5 units"),
        ("en", "not less than 5 units", "at_least", 5, "units", "not less than 5 units"),
        ("en", "not fewer than 5 units", "at_least", 5, "units", "not fewer than 5 units"),
        ("en", "not over 5 units", "at_most", 5, "units", "not over 5 units"),
        ("en", "no more than 5 units", "at_most", 5, "units", "no more than 5 units"),
        ("it", "non meno di 5 pezzi", "at_least", 5, "units", "non meno di 5 pezzi"),
    ],
)
def test_hedged_number_is_vague_with_stated_value(
    lang: str, span: str, qualifier: str, stated: int, unit: str, raw: str | None
) -> None:
    r = parse(span, lang)
    q = r.quantity
    assert (q.kind, q.value, q.low, q.high, q.unit) == ("vague", None, None, None, unit)
    assert (r.qualifier, r.stated) == (qualifier, stated)
    if raw is not None:
        assert q.raw == raw


@pytest.mark.parametrize(
    ("lang", "span", "unit"),
    [
        ("it", "Maire nera 3 richieste, Ilvaro 2 richieste", None),  # never summed
        ("it", "15% dei clienti erano coreani", "customers"),
        ("it", "fatturato 38k, sopra budget", None),
        ("it", "2,5 pezzi", "units"),
        ("it", "Ilvaro rosa in 0", None),
        ("it", "Arneb blu 5", None),
        ("en", "Saudi clients about 15% of sales today", "customers"),
        ("en", "One Bady powder pink sz 0 request", "requests"),
        ("en", "a lot of people", "customers"),  # "a lot" is not in config/domain.yaml
        ("en", "61 trans, € 2 clients", "customers"),
        ("en", "", None),
    ],
)
def test_unknown(lang: str, span: str, unit: str | None) -> None:
    r = parse(span, lang)
    q = r.quantity
    assert (q.kind, q.value, q.low, q.high, q.unit) == ("unknown", None, None, None, unit)
    assert r.note


@pytest.mark.parametrize(
    ("lang", "span", "unit"),
    [
        # A noun that is not a known modifier sits between the number and the unit noun.
        ("en", "3 days without customers", "customers"),
        ("it", "3 ore senza clienti", "customers"),
        ("en", "3 boxes of items", "units"),
        ("en", "2 hours waiting for clients", "customers"),
        ("it", "3 scatole di pezzi", "units"),
        # Compound spelled numbers are not composed, and never read as their last word.
        ("en", "one hundred units", "units"),
        ("en", "twenty-one units", "units"),
        ("en", "twenty one clients", "customers"),
        ("en", "two hundred and five units", "units"),
        ("en", "a hundred clients", "customers"),
        ("it", "cento clienti", "customers"),
        ("en", "2 dozen clients", "customers"),
        # Decimal separators follow the locale; ambiguous ones abstain.
        ("en", "0.500 units", "units"),
        ("en", "2.500 units", "units"),
        ("en", "1.200 visitors", "visitors"),
        ("it", "2,500 pezzi", "units"),
        ("it", "1,200 visitatori", "visitors"),
        ("it", "0.500 pezzi", "units"),
        ("it", "1.234,5 pezzi", "units"),
        # Noun-first counts get the same checks as number-first ones.
        ("en", "requests: 100 EUR", "requests"),
        ("it", "richieste: 3, 4", "requests"),
        # Dates, times, fractions and sizes are read whole.
        ("en", "at 10:05 clients asked", "customers"),
        ("en", "at 10.05 clients asked", "customers"),
        ("it", "alle 10.05 clienti", "customers"),
        ("en", "on 10/22 clients asked", "customers"),
        ("en", "on 10/22, 3 clients asked", "customers"),  # a list with a date in it
        ("en", "October 22 clients asked", "customers"),
        ("en", "size 0/2 units requested", "units"),
        ("en", "Sizes: 0/2/4 units", "units"),
        ("en", "1/2 units", "units"),
        ("en", "3/4 units", "units"),
        ("en", "3 / 4 units", "units"),
        # Signed numbers are changes, not counts.
        ("en", "-5 units", "units"),
        ("it", "−5 pezzi", "units"),
        ("en", "(-5 units)", "units"),
        ("en", "–5 units", "units"),
        ("en", "+5 clients vs yesterday", "customers"),
        # Numbers split by a plain space, lists and invalid ranges.
        ("en", "1 200 visitors", "visitors"),
        ("it", "3 e 4 pezzi", "units"),
        ("it", "3, 4 pezzi", "units"),
        ("en", "3, 4 or 5 units", "units"),
        ("en", "between 8 and 5 units", "units"),
        ("en", "between 5 and 5 units", "units"),
        ("en", "5-5 units", "units"),
        ("en", "5 of the 8 units sold", None),
        # Hedges we cannot read.
        ("en", "not 5 units", "units"),
        ("it", "non almeno 3 clienti", "customers"),
        ("en", "3-5 or more units", "units"),
        ("en", "3-5+ units", "units"),
    ],
)
def test_abstains_rather_than_guess(lang: str, span: str, unit: str | None) -> None:
    r = parse(span, lang)
    q = r.quantity
    assert (q.kind, q.value, q.low, q.high, q.unit) == ("unknown", None, None, None, unit)
    assert r.qualifier is None and r.stated is None
    assert r.note


def test_vague_quantifiers_come_from_config() -> None:
    assert parse_quantity("tanti clienti", "it", ()).quantity.kind == "unknown"
    assert parse_quantity("tanti clienti", "it", ["tanti"]).quantity.kind == "vague"
    assert parse_quantity("a bunch of clients", "en", ["a bunch"]).quantity.raw == (
        "a bunch of clients"
    )


@pytest.mark.parametrize("lang", ["it", "en"])
def test_every_configured_quantifier_is_vague(lang: str) -> None:
    noun = {"it": "clienti", "en": "clients"}[lang]
    for word in VAGUE[lang]:
        q = parse(f"{word} {noun}", lang).quantity
        assert (q.kind, q.unit) == ("vague", "customers"), word


def test_cjk_quantifier_matches_without_spaces() -> None:
    q = parse_quantity("今日は多くのお客様", "ja", VAGUE["ja"]).quantity
    assert (q.kind, q.raw) == ("vague", "多く")


def test_unsupported_language_never_invents_a_unit() -> None:
    q = parse_quantity("7 Anfragen", "de", VAGUE["de"]).quantity
    assert (q.kind, q.unit) == ("unknown", None)
