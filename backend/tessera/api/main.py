"""Thin, run-bound API. Database connections are created lazily, never on import."""

from threading import Lock

from fastapi import FastAPI
from sqlalchemy import Engine

from tessera import __version__
from tessera.api.models import Health
from tessera.api.routers.runs import router
from tessera.core.config import Settings, get_settings
from tessera.core.db import create_schema, make_engine
from tessera.core.registry import Registry


def create_app(
    *,
    engine: Engine | None = None,
    registry: Registry | None = None,
    settings: Settings | None = None,
) -> FastAPI:
    app = FastAPI(title="Tessera", version=__version__)
    app.state.engine = engine
    app.state.engine_lock = Lock()
    app.state.registry = registry
    app.state.settings = settings
    app.include_router(router)

    @app.get("/api/health", response_model=Health)
    def health() -> dict:
        s = app.state.settings or get_settings()
        return {
            "status": "ok",
            "version": __version__,
            "llm_mode": s.llm_mode,
            "fastweb_models_configured": sorted(s.fastweb_keys()),
            "sources_present": s.sources_dir.is_dir(),
        }

    return app


def app_engine(app: FastAPI) -> Engine:
    with app.state.engine_lock:
        if app.state.engine is None:
            settings = app.state.settings or get_settings()
            settings.data_dir.mkdir(parents=True, exist_ok=True)
            engine = make_engine(settings.db_url)
            create_schema(engine)
            app.state.engine = engine
    return app.state.engine


app = create_app()
