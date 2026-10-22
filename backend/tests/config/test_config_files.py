"""DATA-02: `config/eval_split.yaml`, `config/domain.yaml`, `config/aliases.yaml` stay consistent
with the catalog, the store list and the dev-only provenance rule (RFC §5.1)."""

import csv
import email
from email import policy
from functools import cache
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
CONFIG = ROOT / "config"
SOURCES = ROOT / "generated" / "sources"
MASTER = SOURCES / "erp" / "master_data"


def load(name: str) -> dict:
    return yaml.safe_load((CONFIG / name).read_text(encoding="utf-8"))


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


@cache
def body(rel: str) -> str:
    """Email body without quoted reply lines, casefolded."""
    msg = email.message_from_bytes((SOURCES / rel).read_bytes(), policy=policy.default)
    part = msg.get_body(("plain", "html"))
    assert part is not None, rel
    lines = part.get_content().splitlines()
    return "\n".join(line for line in lines if not line.lstrip().startswith(">")).casefold()


SPLIT = load("eval_split.yaml")
DOMAIN = load("domain.yaml")
ALIASES = load("aliases.yaml")
STORES = {r["store_id"]: r for r in rows("stores.csv")}
STYLES = {r["style_code"]: r for r in rows("styles.csv")}
COLOURS = {r["color_code"] for r in rows("sku_colour.csv")}


def test_every_file_is_versioned() -> None:
    for cfg in (SPLIT, DOMAIN, ALIASES):
        assert isinstance(cfg["version"], int)


def test_split_partitions_stores_csv() -> None:
    dev, holdout, other = (set(SPLIT[k]) for k in ("dev", "holdout", "unassigned"))
    assert len(dev) == len(SPLIT["dev"]) == 12
    assert len(holdout) == len(SPLIT["holdout"]) == 10
    assert not dev & holdout and not dev & other and not holdout & other
    assert dev | holdout | other == set(STORES)


def test_vague_quantifiers_cover_dev_languages_only() -> None:
    dev_langs = {STORES[s]["language"] for s in SPLIT["dev"]}
    assert set(DOMAIN["vague_quantifiers"]) == dev_langs


def test_policy_parameters_carry_units() -> None:
    for group, params in DOMAIN["policy"].items():
        for name, p in params.items():
            assert {"value", "unit"} <= set(p), f"{group}.{name}"


def alias_entries() -> list[tuple[str, dict]]:
    out = [(code, e) for code, es in ALIASES["styles"].items() for e in es]
    out += [(",".join(e["styles"]), e) for e in ALIASES["shared"]]
    out += [(code, e) for code, es in ALIASES["colours"].items() for e in es]
    return out


def test_alias_targets_exist_in_catalog() -> None:
    assert set(ALIASES["styles"]) <= set(STYLES)
    assert set(ALIASES["colours"]) <= COLOURS
    for e in ALIASES["shared"]:
        assert len(set(e["styles"])) >= 2, e["alias"]
        assert set(e["styles"]) <= set(STYLES), e["alias"]


def test_aliases_do_not_repeat_catalog_names_or_themselves() -> None:
    for code, es in ALIASES["styles"].items():
        names = [e["alias"].casefold() for e in es]
        assert len(names) == len(set(names)), code
        assert STYLES[code]["style_name"].casefold() not in names, code
    for code, es in ALIASES["colours"].items():
        names = [e["alias"].casefold() for e in es]
        assert len(names) == len(set(names)), code


@pytest.mark.parametrize(("target", "entry"), alias_entries(), ids=lambda v: str(v)[:40])
def test_alias_provenance_is_a_dev_email_that_contains_it(target: str, entry: dict) -> None:
    parts = entry["source"].split("/")
    assert parts[0] == "store_emails" and parts[2].endswith(".eml"), entry
    store = parts[1]
    assert store in SPLIT["dev"], f"{entry['alias']}: {store} is not a dev store"
    assert entry["lang"] == STORES[store]["language"], entry
    assert entry["alias"].casefold() in body(entry["source"]), entry
