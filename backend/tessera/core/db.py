"""SQLite tables (PLAN §2 rule 4). Read and write them only through `tessera.core.repo`.

One generic `artifacts` table holds every DTO, partitioned by `run_id`, so a new field or DTO
never needs a migration. ERP rows live in `erp_rows`, shared by all runs and filtered by
`available_at`. `create_all` does not alter existing tables: a schema change bumps
`SCHEMA_VERSION` and an old DB file is refused instead of being silently reused (RFC §4.3).
"""

from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Engine,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    TypeDecorator,
    UniqueConstraint,
    create_engine,
    event,
    inspect,
    text,
)

SCHEMA_VERSION = 1


class SchemaMismatch(RuntimeError):
    """The DB file was created by another schema version: export what is durable, then delete it."""


class UTCDateTime(TypeDecorator):
    """Aware datetimes in, aware UTC datetimes out; stored naive UTC so SQL comparisons work."""

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("naive datetime: every instant must be timezone-aware")
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, dialect) -> datetime | None:
        return None if value is None else value.replace(tzinfo=UTC)


metadata = MetaData()

runs = Table(
    "runs",
    metadata,
    Column("run_id", String, primary_key=True),
    Column("scenario_id", String, nullable=False),
    Column("as_of", UTCDateTime, nullable=False),
    # pending -> running -> published | failed. Only published runs are complete (RFC §4.3).
    Column("status", String, nullable=False),
    Column("spec", JSON, nullable=False),
    Column("created_at", UTCDateTime, nullable=False),
    Column("finished_at", UTCDateTime),
)

module_runs = Table(
    "module_runs",
    metadata,
    Column("run_id", String, ForeignKey("runs.run_id"), primary_key=True),
    Column("module_id", String, primary_key=True),
    Column("payload", JSON, nullable=False),
)

artifacts = Table(
    "artifacts",
    metadata,
    Column("seq", Integer, primary_key=True, autoincrement=True),
    Column("run_id", String, ForeignKey("runs.run_id"), nullable=False),
    Column("kind", String, nullable=False),
    Column("id", String, nullable=False),
    Column("version", String, nullable=False),
    Column("store_id", String),
    Column("sku", String),
    Column("case_id", String),
    Column("available_at", UTCDateTime),
    Column("payload", JSON, nullable=False),
    Column("input_refs", JSON, nullable=False),
    Column("producer", String),
    Column("computed_at", UTCDateTime),
    UniqueConstraint("run_id", "kind", "id", "version"),
    Index("ix_artifacts_run_kind", "run_id", "kind", "available_at"),
)

erp_rows = Table(
    "erp_rows",
    metadata,
    Column("seq", Integer, primary_key=True, autoincrement=True),
    Column("tbl", String, nullable=False),
    Column("id", String, nullable=False),
    Column("version", String, nullable=False),
    Column("store_id", String),
    Column("sku", String),
    Column("available_at", UTCDateTime),
    Column("availability_basis", String, nullable=False),
    Column("source_refs", JSON, nullable=False),
    Column("data", JSON, nullable=False),
    UniqueConstraint("tbl", "id", "version"),
    Index("ix_erp_rows_tbl", "tbl", "store_id", "sku", "available_at"),
)


def _sqlite_pragmas(dbapi_connection, _record) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    # WAL: API reads and short writes proceed while a pipeline module transaction is open.
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


def connect(url: str) -> Engine:
    """Engine with the schema created, or `SchemaMismatch` for a DB of another version."""
    engine = create_engine(url)
    event.listen(engine, "connect", _sqlite_pragmas)
    with engine.begin() as conn:
        found = conn.execute(text("PRAGMA user_version")).scalar_one()
        if found != SCHEMA_VERSION and inspect(conn).get_table_names():
            raise SchemaMismatch(
                f"{engine.url.database} has schema {found}, code expects {SCHEMA_VERSION}"
            )
        metadata.create_all(conn)
        conn.execute(text(f"PRAGMA user_version={SCHEMA_VERSION}"))
    return engine
