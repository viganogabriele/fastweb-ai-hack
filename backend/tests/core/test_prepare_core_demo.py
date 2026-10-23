"""Candidate preparation rejects unsafe inputs before ERP or model execution."""

import importlib

import pytest
from jsonschema.exceptions import ValidationError

from tessera.core.config import REPO_ROOT


@pytest.fixture
def prepare(monkeypatch):
    monkeypatch.syspath_prepend(str(REPO_ROOT / "scripts"))
    return importlib.import_module("prepare_core_demo")


@pytest.mark.parametrize("linked", ["stores", "split"])
def test_early_input_reads_reject_links_and_remove_partial_candidate(
    prepare, tmp_path, monkeypatch, linked
):
    sources, config, output = [tmp_path / name for name in ("sources", "config", "candidate")]
    stores = sources / "erp/master_data/stores.csv"
    split = config / "eval_split.yaml"
    stores.parent.mkdir(parents=True)
    config.mkdir()
    target = tmp_path / "unread-input"
    target.write_text("must not be opened")
    (stores if linked == "stores" else split).symlink_to(target)
    monkeypatch.setattr(
        prepare.erp, "window", lambda *_args, **_kw: pytest.fail("ERP read before path validation")
    )
    with pytest.raises(ValueError, match="symlink"):
        prepare.prepare(output, sources=sources, config=config, code_version="test")
    assert not output.exists()
    assert target.read_text() == "must not be opened"


def test_invalid_investigator_selection_fails_before_loading_data(prepare, tmp_path, monkeypatch):
    sources, config, output = [tmp_path / name for name in ("sources", "config", "candidate")]
    sources.mkdir()
    config.mkdir()
    monkeypatch.setattr(
        prepare.erp, "window", lambda *_args, **_kw: pytest.fail("invalid snapshot read data")
    )
    with pytest.raises(ValidationError):
        prepare.prepare(
            output, sources=sources, config=config, code_version="test", case_ids=("same", "same")
        )
    assert not output.exists()
