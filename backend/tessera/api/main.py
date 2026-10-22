"""FastAPI app. Routers live in `tessera.api.routers`, one file per resource (RFC §4.6)."""

from fastapi import FastAPI

from tessera import __version__
from tessera.core.config import get_settings

app = FastAPI(title="Tessera", version=__version__)


@app.get("/api/health")
def health() -> dict:
    s = get_settings()
    return {
        "status": "ok",
        "version": __version__,
        "llm_mode": s.llm_mode,
        "fastweb_key_configured": s.fastweb_api_key is not None,
        "sources_present": s.sources_dir.is_dir(),
    }
