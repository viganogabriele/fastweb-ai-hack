import csv

import pytest

from tessera.core.config import REPO_ROOT
from tessera.modules.integration.candidates import (
    Catalog,
    LinkParams,
    _inflects,
    link_mention,
    normalize,
)

W_SIZES = ["00", "0", "1", "2", "3", "4"]
ALPHA = ["XS", "S", "M", "L", "XL", "XXL"]


def colour_row(style_code, style_name, colour, it, en):
    return {
        "sku": f"{style_code}-{colour}",
        "style_code": style_code,
        "style_name": style_name,
        "color_code": colour,
        "color_name_it": it,
        "color_name_en": en,
    }


ROWS = [
    colour_row("MAI", "AUREA", "999", "nero", "black"),
    colour_row("MAI", "AUREA", "034", "beige", "beige"),
    colour_row("MAY", "NOVA", "999", "nero", "black"),
    colour_row("MAY", "NOVA", "742", "blu notte", "navy"),
    colour_row("ILV", "IRIDIA", "999", "nero", "black"),
    colour_row("ILV", "IRIDIA", "510", "rosa cipria", "powder pink"),
    colour_row("CAR", "VLOGO CARDIGAN", "999", "nero", "black"),
    colour_row("TRI", "VLOGO PADDED CARDIGAN", "001", "bianco", "white"),
]
SIZES = (
    [{"sku": f"{s}-{c}", "size": z} for s, c in [("MAI", "999"), ("MAI", "034")] for z in W_SIZES]
    + [{"sku": "MAY-999", "size": z} for z in W_SIZES]
    + [{"sku": "MAY-742", "size": z} for z in W_SIZES]
    + [{"sku": "ILV-510", "size": z} for z in W_SIZES]
    + [{"sku": "CAR-999", "size": z} for z in ALPHA]
    + [{"sku": "TRI-001", "size": z} for z in ALPHA]
)
CATALOG = Catalog.from_rows(
    ROWS,
    SIZES,
    style_aliases={"ILV": ["イリディア"]},
    colour_aliases={"999": ["nera", "noir"], "510": ["粉色", "pink", "rosa"]},
)


def test_normalize_strips_latin_accents_but_keeps_kana() -> None:
    assert normalize("  La AÚREA, noire!") == "la aurea noire"
    assert normalize("イリディア") == "イリディア"
    assert normalize("Ａｕｒｅａ") == "aurea"


def test_style_and_colour_link_to_sku() -> None:
    r = link_mention("la Aurea nera", CATALOG)
    assert (r.status, r.target_id, r.level) == ("linked", "MAI-999", "sku")
    assert r.candidates[0].method == "exact"


def test_size_in_size_run_links_to_sku_size() -> None:
    r = link_mention("Aurea nero", CATALOG, size="taglia 2")
    assert (r.status, r.target_id, r.level) == ("linked", "MAI-999-2", "sku_size")


def test_size_outside_size_run_blocks_link() -> None:
    r = link_mention("Aurea nero", CATALOG, size="M")
    assert r.status == "ambiguous"
    assert "size_not_in_size_run" in r.reasons
    assert r.candidates[0].target_id == "MAI-999"


def test_style_without_colour_links_at_style_level() -> None:
    r = link_mention("abbiamo venduto tutte le Aurea", CATALOG)
    assert (r.status, r.target_id, r.level) == ("linked", "MAI", "style")


def test_single_colour_style_implies_sku() -> None:
    r = link_mention("Vlogo Cardigan", CATALOG, size="M")
    assert (r.status, r.target_id) == ("linked", "CAR-999-M")


def test_colour_the_style_does_not_come_in_is_ambiguous() -> None:
    r = link_mention("Aurea pink", CATALOG)
    assert r.status == "ambiguous"
    assert "colour_not_in_style" in r.reasons


def test_a_second_colour_the_style_does_not_come_in_blocks_the_link() -> None:
    r = link_mention("Aurea nera e pink", CATALOG)
    assert r.status == "ambiguous"
    assert "colour_not_in_style" in r.reasons
    # The same word naming an in-style and an out-of-style code is not a second colour.
    assert link_mention("Nova nera", CATALOG).status == "linked"


def test_two_styles_named_is_ambiguous() -> None:
    r = link_mention("Aurea o Nova nera", CATALOG)
    assert r.status == "ambiguous"
    assert "close_runner_up" in r.reasons
    assert {c.target_id for c in r.candidates[:2]} == {"MAI-999", "MAY-999"}


def test_cjk_alias_exact_match() -> None:
    r = link_mention("粉色イリディア断码了", CATALOG)
    assert (r.status, r.target_id) == ("linked", "ILV-510")


def test_typo_is_fuzzy_candidate_not_auto_link() -> None:
    r = link_mention("la Aurrea nera", CATALOG)
    assert r.candidates[0].target_id == "MAI-999"
    assert r.candidates[0].method == "fuzzy"
    assert r.status == "linked"  # One extra letter stays within the default fuzzy threshold.
    r = link_mention("la Aure nera", CATALOG, params=LinkParams(link_min=95))
    assert r.status == "ambiguous" and "low_score" in r.reasons


def test_partial_multiword_name_is_ambiguous() -> None:
    r = link_mention("cardigan", CATALOG)
    assert r.status == "ambiguous"
    assert [c.target_id for c in r.candidates] == ["CAR-999", "TRI-001"]
    assert r.candidates[0].score == r.candidates[1].score < 90


@pytest.mark.parametrize(
    ("mention", "target", "level"),
    [
        (
            "ieri notte la Nova è andata a ruba",
            "MAY",
            "style",
        ),  # "notte" alone is not navy
        ("zero Aurea rimaste", "MAI", "style"),  # "zero" is not a typo of "nero"
        ("due Nova nere", "MAY-999", "sku"),  # inflection of "nero"
        ("Nova blu notte", "MAY-742", "sku"),
    ],
)
def test_colour_words_match_whole_names_or_inflections_only(mention, target, level) -> None:
    r = link_mention(mention, CATALOG)
    assert (r.status, r.target_id, r.level) == ("linked", target, level)


@pytest.mark.parametrize(
    ("word", "name", "expected"),
    [
        ("nera", "nero", True),
        ("neri", "nero", True),
        ("bianchi", "bianco", True),
        ("rossa", "rosso", True),
        ("zero", "nero", False),
        ("nervo", "nero", False),
        ("rosa", "rosso", False),
        ("blue", "blu", False),
    ],
)
def test_inflects(word, name, expected) -> None:
    assert _inflects(word, name) is expected


def test_colour_only_and_unknown_are_unlinked() -> None:
    assert link_mention("the long black one", CATALOG).reasons == ("colour_only",)
    assert link_mention("una borsa", CATALOG).reasons == ("no_candidate",)
    assert link_mention("  ", CATALOG).reasons == ("empty_mention",)


def test_store_assortment_preferred_then_global_fallback() -> None:
    r = link_mention("Aurea o Nova nera", CATALOG, store_skus={"MAY-999"})
    assert (r.status, r.target_id) == ("linked", "MAY-999")
    assert all(c.in_assortment for c in r.candidates)
    r = link_mention("Aurea nera", CATALOG, store_skus={"MAY-742"})
    assert (r.status, r.target_id) == ("linked", "MAI-999")
    assert r.reasons == ("global_fallback",)
    assert r.candidates[0].in_assortment is False


def test_top_k_limits_candidates() -> None:
    r = link_mention("Aurea Nova Iridia nero", CATALOG, params=LinkParams(top_k=2))
    assert len(r.candidates) == 2


MASTER = REPO_ROOT / "generated" / "sources" / "erp" / "master_data"


@pytest.mark.skipif(not MASTER.exists(), reason="dataset not checked out")
@pytest.mark.parametrize(
    ("mention", "size", "target"),
    [
        ("la Aurea nera", None, "J20931A00012-999"),
        ("Aurea black", "2", "J20931A00012-999-2"),
        ("IRIDIA powder pink", None, None),  # resolved below from the catalog
        ("ieri notte la Nova", None, "J10911A00034"),  # style level, not the navy SKU
        ("zero Aurea rimaste", None, "J20931A00012"),  # style level, not the black SKU
    ],
)
def test_real_catalog(mention, size, target) -> None:
    with open(MASTER / "sku_colour.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    with open(MASTER / "sku_size_ean.csv", newline="") as f:
        sizes = list(csv.DictReader(f))
    catalog = Catalog.from_rows(rows, sizes)
    if target is None:
        target = next(
            r["sku"] for r in rows if r["style_name"] == "IRIDIA" and r["color_code"] == "510"
        )
    r = link_mention(mention, catalog, size=size)
    assert (r.status, r.target_id) == ("linked", target)
