"""PLT-03: `tesseract fixtures load` and `tesseract reset --run` on the fixture namespace."""

import json
import shutil
from pathlib import Path

import pytest

from tesseract import cli
from tesseract.core.config import Settings, get_settings
from tesseract.core.contracts import Observation, Segment, SourceDocument
from tesseract.core.db import connect
from tesseract.core.fixtures import FIXTURE_RUN_ID, load_fixtures, read_fixtures
from tesseract.core.repo import Repo, RunNotFound, list_runs, run_status

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "data" / "fixtures"


def test_loads_every_fixture_as_one_published_run(tmp_path) -> None:
    engine = connect(f"sqlite:///{tmp_path / 'f.db'}")
    paths, records = read_fixtures(FIXTURES)
    spec, n = load_fixtures(engine, FIXTURES, ROOT / "config")
    assert n == len(records) > 0
    assert run_status(engine, FIXTURE_RUN_ID) == "published"
    assert spec.mode == "fixture"
    assert spec.as_of == max(r.available_at for r in records if r.available_at)
    assert len(spec.authorized_fixture_refs) == len(paths)

    repo = Repo.open(engine, FIXTURE_RUN_ID)
    for kind in (SourceDocument, Segment, Observation):
        assert repo.list(kind) == [r for r in records if type(r) is kind]

    again, _ = load_fixtures(engine, FIXTURES, ROOT / "config")
    assert again == spec
    assert len(list_runs(engine)) == 1


def test_bad_fixture_fails_the_load(tmp_path) -> None:
    folder = tmp_path / "fixtures" / "documents"
    folder.mkdir(parents=True)
    (folder / "bad.json").write_text(json.dumps([{"kind": "RunSpec", "payload": {}}]))
    engine = connect(f"sqlite:///{tmp_path / 'f.db'}")
    with pytest.raises(ValueError, match="not a storable contract"):
        load_fixtures(engine, tmp_path / "fixtures", ROOT / "config")


def test_cli_loads_into_fixture_namespace_and_resets(tmp_path, monkeypatch, capsys) -> None:
    shutil.copytree(FIXTURES, tmp_path / "fixtures")
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.delenv("FIXTURE_MODE", raising=False)
    get_settings.cache_clear()
    try:
        cli.main(["fixtures", "load"])
        assert "run 'fixture'" in capsys.readouterr().out
        assert not (tmp_path / "tesseract.db").exists()
        fixture_db = Settings(data_dir=tmp_path, fixture_mode=True)
        engine = connect(fixture_db.db_url)
        assert run_status(engine, FIXTURE_RUN_ID) == "published"

        monkeypatch.setenv("FIXTURE_MODE", "1")
        get_settings.cache_clear()
        cli.main(["reset", "--run", FIXTURE_RUN_ID])
        with pytest.raises(RunNotFound):
            run_status(engine, FIXTURE_RUN_ID)
    finally:
        get_settings.cache_clear()
