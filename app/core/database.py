from typing import Generator, Annotated

from fastapi import Depends

from sqlalchemy.sql import text
from sqlmodel import create_engine, Session

from .logger import logger
from .metrics import DB_CONNECTION_ERRORS
from .settings import settings


engine = create_engine(settings.DATABASE_URL)


def get_db() -> Generator[Session, None, None]:
    """Yields a database session for use in FastAPI endpoints."""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


def create_db_and_tables():
    """Creates the database and tables if they don't exist, but should be replaced with migrations."""
    try:
        with engine.connect() as conn:
            stmt = text("select * from pg_database")
            print(conn.execute(stmt).fetchall())
    except Exception as e:
        DB_CONNECTION_ERRORS.inc()
        logger.error(
            "db.connection_failed",
            extra={"event": "db.connection_failed", "error": str(e)},
            exc_info=True,
        )


SessionDep = Annotated[Session, Depends(get_db)]
