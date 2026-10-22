"""Settings from environment / `.env` (RFC §4.7.2). Never log or commit the API key."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=REPO_ROOT / ".env", extra="ignore")

    fastweb_api_key: SecretStr | None = None
    fastweb_base_url: str = "https://spod.ai-factory.fastweb.it/v1"
    chat_model: str = "google/gemma-4-26B-A4B-it"
    embed_model: str = "Qwen/Qwen3-VL-Embedding-2B"
    asr_model: str = "openai/whisper-large-v3-turbo"
    llm_mode: Literal["live", "record", "replay"] = "replay"

    sources_dir: Path = REPO_ROOT / "generated" / "sources"
    data_dir: Path = REPO_ROOT / "data"
    config_dir: Path = REPO_ROOT / "config"
    mocks_base_url: str = "http://127.0.0.1:8088"

    @property
    def db_url(self) -> str:
        return f"sqlite:///{self.data_dir / 'tessera.db'}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
