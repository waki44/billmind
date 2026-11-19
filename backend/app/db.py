"""Database engine + session wiring (SQLAlchemy 2.0)."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables. Day-1 convenience for local dev/tests.

    The Docker/Postgres path uses the same models; Alembic migrations get
    introduced when the schema first needs to change on a live database.
    """
    from . import models  # noqa: F401  (importing registers the tables)

    models.Base.metadata.create_all(bind=engine)
