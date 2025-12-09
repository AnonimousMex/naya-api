from typing import Generator, Annotated

from fastapi import Depends

from sqlalchemy.sql import text
from sqlmodel import create_engine, Session

from .settings import settings


engine = create_engine(settings.DATABASE_URL_EFFECTIVE, pool_pre_ping=True)


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
        print(f"An error occurred while connecting to the database: {e}")


SessionDep = Annotated[Session, Depends(get_db)]
