import json

import pytest

from tesseract.core.config import MissingApiKey, Settings


def test_api_key_per_model(tmp_path) -> None:
    keys = tmp_path / "keys.json"
    keys.write_text(json.dumps({"m/a": "secret-a", "m/b": "secret-b"}))
    s = Settings(fastweb_keys_file=keys)
    assert s.api_key_for("m/b").get_secret_value() == "secret-b"
    assert "secret" not in repr(s.fastweb_keys())


def test_missing_key_names_model_only(tmp_path) -> None:
    keys = tmp_path / "keys.json"
    keys.write_text(json.dumps({"m/a": "secret-a"}))
    with pytest.raises(MissingApiKey, match="m/z") as exc:
        Settings(fastweb_keys_file=keys).api_key_for("m/z")
    assert "secret" not in str(exc.value)


def test_no_keys_file(tmp_path) -> None:
    assert Settings(fastweb_keys_file=tmp_path / "absent.json").fastweb_keys() == {}


def test_relative_keys_file_is_from_repo_root() -> None:
    from tesseract.core.config import REPO_ROOT

    s = Settings(fastweb_keys_file=".secrets/fastweb_keys.json")
    assert s.fastweb_keys_file == REPO_ROOT / ".secrets" / "fastweb_keys.json"
