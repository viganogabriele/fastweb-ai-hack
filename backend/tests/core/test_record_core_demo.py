"""Recording guards fail before any client, credential lookup or network operation."""

import importlib

import pytest

from tessera.core.config import REPO_ROOT
from tests.core.test_replay_demo import snapshot


@pytest.fixture
def recorder(monkeypatch):
    monkeypatch.syspath_prepend(str(REPO_ROOT / "scripts"))
    module = importlib.import_module("record_core_demo")
    monkeypatch.setattr(
        module, "LLMClient", lambda *_args, **_kwargs: pytest.fail("client before validation")
    )
    return module


@pytest.mark.parametrize("problem", ["different_spec", "different_checkout", "dirty_code"])
def test_recording_requires_the_actual_committed_execution_sha(
    recorder, tmp_path, monkeypatch, problem
):
    spec = snapshot(mode="recorded")
    (tmp_path / "input-manifest.json").write_text("{}")
    (tmp_path / "run-spec.json").write_text(spec.model_dump_json())
    if problem == "different_spec":
        sha = "another"
        message = "candidate code_version"
    else:
        sha = spec.code_version
        message = "current checkout" if problem == "different_checkout" else "commit executable"

    def git(args, **kwargs):
        if args[1] == "rev-parse":
            return "another" if problem == "different_checkout" else sha
        return " M scripts/record_core_demo.py"

    monkeypatch.setattr(recorder.subprocess, "check_output", git)
    with pytest.raises(ValueError, match=message):
        recorder.record(tmp_path, execution_sha=sha)


def test_modified_inputs_fail_before_creating_recording_clients(recorder, tmp_path, monkeypatch):
    spec = snapshot(mode="recorded")
    (tmp_path / "input-manifest.json").write_text("{}")
    (tmp_path / "run-spec.json").write_text(spec.model_dump_json())
    (tmp_path / "sources").mkdir()
    (tmp_path / "sources/changed.txt").write_text("changed source")
    monkeypatch.setattr(
        recorder.subprocess,
        "check_output",
        lambda args, **_: spec.code_version if args[1] == "rev-parse" else "",
    )
    with pytest.raises(ValueError, match="candidate inputs changed"):
        recorder.record(tmp_path, execution_sha=spec.code_version)
    assert not (tmp_path / "runtime").exists()
