"""Settings from environment / `.env` (RFC §4.7.2). Never log or commit the API keys."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class MissingApiKey(LookupError):
    """No key for this model in the keys file. The message names the model, never a key."""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=REPO_ROOT / ".env", extra="ignore")

    fastweb_base_url: str = "https://spod.ai-factory.fastweb.it/v1"
    # Fastweb issues one key per model: JSON object {model_id: key}, gitignored.
    fastweb_keys_file: Path = REPO_ROOT / ".secrets" / "fastweb_keys.json"
    chat_model: str = "google/gemma-4-26B-A4B-it"
    embed_model: str = "Qwen/Qwen3-VL-Embedding-2B"
    asr_model: str = "openai/whisper-large-v3-turbo"
    llm_mode: Literal["live", "record", "replay"] = "replay"

    sources_dir: Path = REPO_ROOT / "generated" / "sources"
    data_dir: Path = REPO_ROOT / "data"
    config_dir: Path = REPO_ROOT / "config"
    mocks_base_url: str = "http://127.0.0.1:8088"

    @field_validator("fastweb_keys_file")
    @classmethod
    def _from_repo_root(cls, v: Path) -> Path:
        return v if v.is_absolute() else REPO_ROOT / v

    @property
    def db_url(self) -> str:
        return f"sqlite:///{self.data_dir / 'tessera.db'}"

    def fastweb_keys(self) -> dict[str, SecretStr]:
        if not self.fastweb_keys_file.is_file():
            return {}
        raw = json.loads(self.fastweb_keys_file.read_text())
        return {model: SecretStr(key) for model, key in raw.items()}

    def api_key_for(self, model: str) -> SecretStr:
        try:
            return self.fastweb_keys()[model]
        except KeyError:
            raise MissingApiKey(f"no key for model {model!r} in {self.fastweb_keys_file}") from None


@lru_cache
def get_settings() -> Settings:
    return Settings()
