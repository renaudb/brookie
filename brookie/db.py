import os
from collections.abc import Generator
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session as DbSession
from sqlalchemy.orm import sessionmaker

# SQLAlchemy's own `Session` class shares a name with our domain `Session`
# model (brookie.models.session.Session). Import it as `DbSession` everywhere
# a database session is passed around to avoid the collision.

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./brookie.db")

_connect_args: dict[str, Any] = (
    {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

engine: Engine = create_engine(DATABASE_URL, connect_args=_connect_args)


def enable_sqlite_foreign_keys(dbapi_connection: Any, _: Any) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


if engine.dialect.name == "sqlite":
    event.listen(engine, "connect", enable_sqlite_foreign_keys)


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[DbSession, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
