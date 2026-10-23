"""Settings from environment / `.env` (RFC §4.7.2). Never log or commit the API keys."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
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
    # ASR-01: our OpenAI-compatible server on the team Mac mini (`tools/asr-server/`), not
    # Fastweb. The URL is part of every transcription cache key, so keep the shared default.
    asr_base_url: str = "https://hack-sst.lorenzocorallo.net/v1"
    asr_api_key: SecretStr | None = None
    # Explicit capability for the opt-in live phone demo; never put provider keys in a QR.
    voice_access_token: SecretStr | None = None
    # Enters the cache key; the server ignores it and runs its own model. Keep the name the
    # earlier .env.example already set, or existing .env files would miss every recording.
    asr_model: str = "openai/whisper-large-v3-turbo"
    asr_timeout_seconds: float = Field(default=120, gt=0, allow_inf_nan=False)
    # Server limit (tools/asr-server ASR_MAX_UPLOAD_MB): refuse before uploading.
    asr_max_upload_mb: int = Field(default=25, gt=0)
    llm_mode: Literal["live", "record", "replay"] = "replay"
    # Per-run provider allowance (RFC §4.7.2); raise via env for full record runs.
    llm_max_calls: int = 100
    llm_max_tokens: int = 200_000
    llm_deadline_seconds: float = 180
    # Parallel provider calls per run (client semaphore and module thread pools).
    llm_concurrency: int = Field(default=4, ge=1, le=32)

    sources_dir: Path = REPO_ROOT / "generated" / "sources"
    data_dir: Path = REPO_ROOT / "data"
    config_dir: Path = REPO_ROOT / "config"
    # Display-only product metadata (data/catalog/README.md); never a pipeline input.
    catalog_dir: Path = REPO_ROOT / "data" / "catalog"
    mocks_base_url: str = "http://127.0.0.1:8088"
    # Fixture namespace (RFC §4.6): its own DB file, never mixed with real runs.
    fixture_mode: bool = False

    @field_validator("fastweb_keys_file")
    @classmethod
    def _from_repo_root(cls, v: Path) -> Path:
        return v if v.is_absolute() else REPO_ROOT / v

    @property
    def db_path(self) -> Path:
        return self.data_dir / ("tesseract_fixture.db" if self.fixture_mode else "tesseract.db")

    @property
    def db_url(self) -> str:
        return f"sqlite:///{self.db_path}"

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

    def asr_key(self) -> SecretStr:
        if self.asr_api_key is None or not self.asr_api_key.get_secret_value():
            raise MissingApiKey("no ASR_API_KEY in .env (one per consumer, see tools/asr-server)")
        return self.asr_api_key


@lru_cache
def get_settings() -> Settings:
    return Settings()
