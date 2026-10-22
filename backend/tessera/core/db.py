"""SQLite schema for immutable run snapshots and their artifacts (PLT-03).

Schema creation initializes a new database; it is not a migration mechanism.
Each job owns its Session/transaction. No global connection or mutable replay clock.
"""

from sqlalchemy import JSON, Boolean, ForeignKeyConstraint, Index, String, create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class RunRow(Base):
    __tablename__ = "runs"
    namespace: Mapped[str] = mapped_column(String, primary_key=True)
    run_id: Mapped[str] = mapped_column(String, primary_key=True)
    spec: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String, default="pending")
    published: Mapped[bool] = mapped_column(Boolean, default=False)


class ArtifactRow(Base):
    __tablename__ = "artifacts"
    namespace: Mapped[str] = mapped_column(String, primary_key=True)
    run_id: Mapped[str] = mapped_column(String, primary_key=True)
    kind: Mapped[str] = mapped_column(String, primary_key=True)
    id: Mapped[str] = mapped_column(String, primary_key=True)
    version: Mapped[str] = mapped_column(String, primary_key=True)
    store_id: Mapped[str | None] = mapped_column(String)
    sku: Mapped[str | None] = mapped_column(String)
    case_id: Mapped[str | None] = mapped_column(String)
    available_at: Mapped[str | None] = mapped_column(String)
    computed_at: Mapped[str | None] = mapped_column(String)
    producer: Mapped[str | None] = mapped_column(String)
    input_refs: Mapped[list] = mapped_column(JSON)
    payload: Mapped[dict] = mapped_column(JSON)
    __table_args__ = (
        ForeignKeyConstraint(["namespace", "run_id"], ["runs.namespace", "runs.run_id"]),
        Index("ix_artifacts_replay", "namespace", "run_id", "kind", "available_at"),
        Index("ix_artifacts_store", "namespace", "run_id", "store_id", "sku"),
    )


class ArtifactScopeRow(Base):
    __tablename__ = "artifact_stores"
    namespace: Mapped[str] = mapped_column(String, primary_key=True)
    run_id: Mapped[str] = mapped_column(String, primary_key=True)
    kind: Mapped[str] = mapped_column(String, primary_key=True)
    id: Mapped[str] = mapped_column(String, primary_key=True)
    version: Mapped[str] = mapped_column(String, primary_key=True)
    store_id: Mapped[str] = mapped_column(String, primary_key=True)
    __table_args__ = (
        ForeignKeyConstraint(
            ["namespace", "run_id", "kind", "id", "version"],
            [
                "artifacts.namespace",
                "artifacts.run_id",
                "artifacts.kind",
                "artifacts.id",
                "artifacts.version",
            ],
            ondelete="CASCADE",
        ),
    )


class ModuleRunRow(Base):
    __tablename__ = "module_runs"
    namespace: Mapped[str] = mapped_column(String, primary_key=True)
    run_id: Mapped[str] = mapped_column(String, primary_key=True)
    module_id: Mapped[str] = mapped_column(String, primary_key=True)
    payload: Mapped[dict] = mapped_column(JSON)
    __table_args__ = (
        ForeignKeyConstraint(
            ["namespace", "run_id"],
            ["runs.namespace", "runs.run_id"],
        ),
    )


class ERPRow(Base):
    __tablename__ = "erp_facts"
    namespace: Mapped[str] = mapped_column(String, primary_key=True)
    run_id: Mapped[str] = mapped_column(String, primary_key=True)
    table_name: Mapped[str] = mapped_column(String, primary_key=True)
    id: Mapped[str] = mapped_column(String, primary_key=True)
    version: Mapped[str] = mapped_column(String, primary_key=True)
    store_id: Mapped[str | None] = mapped_column(String)
    sku: Mapped[str | None] = mapped_column(String)
    available_at: Mapped[str | None] = mapped_column(String)
    payload: Mapped[dict] = mapped_column(JSON)
    __table_args__ = (
        ForeignKeyConstraint(["namespace", "run_id"], ["runs.namespace", "runs.run_id"]),
        Index("ix_erp_replay", "namespace", "run_id", "table_name", "available_at", "store_id"),
    )


def make_engine(url: str) -> Engine:
    """Create a SQLite engine with real transactions and foreign keys enabled."""
    if not url.startswith("sqlite:"):
        raise ValueError("PLT-03 supports SQLite databases only")
    options = {"connect_args": {"autocommit": False, "check_same_thread": False, "timeout": 30}}
    if url in {"sqlite://", "sqlite:///:memory:"}:
        options["poolclass"] = StaticPool
    engine = create_engine(url, **options)

    @event.listens_for(engine, "connect")
    def configure(connection, _record):
        previous = connection.autocommit
        connection.autocommit = True
        try:
            connection.execute("PRAGMA foreign_keys=ON")
        finally:
            connection.autocommit = previous

    return engine


def create_schema(engine: Engine) -> None:
    Base.metadata.create_all(engine)
