"""Thin, run-bound API. Database connections are created lazily, never on import."""

from asyncio import TaskGroup, to_thread
from contextlib import asynccontextmanager
from threading import Lock

from fastapi import FastAPI
from sqlalchemy import Engine

from tesseract import __version__
from tesseract.api.models import Health
from tesseract.api.routers.clarifications import execute_answer
from tesseract.api.routers.clarifications import router as clarifications_router
from tesseract.api.routers.investigations import router as investigations_router
from tesseract.api.routers.options import router as options_router
from tesseract.api.routers.runs import router
from tesseract.api.routers.voice import router as voice_router
from tesseract.api.voice_boundary import VoiceBoundary
from tesseract.core.config import Settings, get_settings
from tesseract.core.db import connect
from tesseract.core.registry import Registry
from tesseract.modules.agents.answer_registry import pending_follow_ups


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = app.state.settings or get_settings()
    # Accepted answer events survive a restart before an HTTP background task starts.
    # Scan existing databases only, preserving lazy database creation for a new app.
    async with TaskGroup() as workers:
        for namespace in ("product", "fixture"):
            if namespace == "fixture" and not settings.fixture_mode:
                continue
            engine = app.state.engines[namespace]
            if engine is None:
                isolated = settings.model_copy(update={"fixture_mode": namespace == "fixture"})
                if not isolated.db_path.is_file():
                    continue
                engine = app_engine(app, namespace)
            pending = await to_thread(
                pending_follow_ups, engine, fixture_mode=namespace == "fixture"
            )
            for job in pending:
                workers.create_task(
                    to_thread(
                        execute_answer,
                        engine,
                        job,
                        namespace == "fixture",
                        app.state.registry,
                        settings,
                    )
                )
        yield


def create_app(
    *,
    engine: Engine | None = None,
    fixture_engine: Engine | None = None,
    registry: Registry | None = None,
    settings: Settings | None = None,
) -> FastAPI:
    app = FastAPI(title="Tesseract", version=__version__, lifespan=lifespan)
    app.add_middleware(VoiceBoundary)
    app.state.engines = {"product": engine, "fixture": fixture_engine}
    app.state.engine_lock = Lock()
    app.state.registry = registry
    app.state.settings = settings
    app.include_router(router)
    app.include_router(options_router)
    app.include_router(clarifications_router)
    app.include_router(investigations_router)
    app.include_router(voice_router)

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
