"""Thin, run-bound API. Database connections are created lazily, never on import."""

from threading import Lock

from fastapi import FastAPI
from sqlalchemy import Engine

from tessera import __version__
from tessera.api.models import Health
from tessera.api.routers.clarifications import router as clarifications_router
from tessera.api.routers.investigations import router as investigations_router
from tessera.api.routers.options import router as options_router
from tessera.api.routers.runs import router
from tessera.core.config import Settings, get_settings
from tessera.core.db import connect
from tessera.core.registry import Registry


def create_app(
    *,
    engine: Engine | None = None,
    fixture_engine: Engine | None = None,
    registry: Registry | None = None,
    settings: Settings | None = None,
) -> FastAPI:
    app = FastAPI(title="Tessera", version=__version__)
    app.state.engines = {"product": engine, "fixture": fixture_engine}
    app.state.engine_lock = Lock()
    app.state.registry = registry
    app.state.settings = settings
    app.include_router(router)
    app.include_router(options_router)
    app.include_router(clarifications_router)
    app.include_router(investigations_router)

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


def app_engine(app: FastAPI, namespace: str = "product") -> Engine:
    with app.state.engine_lock:
        if app.state.engines[namespace] is None:
            settings = app.state.settings or get_settings()
            settings.data_dir.mkdir(parents=True, exist_ok=True)
            isolated = settings.model_copy(update={"fixture_mode": namespace == "fixture"})
            app.state.engines[namespace] = connect(isolated.db_url)
    return app.state.engines[namespace]


app = create_app()
