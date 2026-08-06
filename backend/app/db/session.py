from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IllegalStateChangeError
from sqlalchemy.engine import URL
import logging
import re

from app.core.config import settings
from app.models.models import Base


def _build_engine() -> object:
    """Create and return a SQLAlchemy engine with a short connect timeout for network DBs.

    For SQLite we preserve `check_same_thread`. For other drivers (Postgres) we set
    a `connect_timeout` so failed connections fail fast during startup instead of
    blocking for a long default timeout.
    """
    database_url = settings.DATABASE_URL or "sqlite:///./medigenie_cdss.db"
    connect_args = {}
    # If a local Postgres URL is configured (localhost), prefer a lightweight
    # SQLite fallback for local test runs to avoid requiring a running DB.
    if database_url.startswith("postgresql") and "localhost" in database_url:
        database_url = "sqlite:///./medigenie_cdss.db"

    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    else:
        # ensure network connections timeout quickly (seconds)
        connect_args = {"connect_timeout": 5}

    return create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


engine = _build_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def create_database():
    """Create tables if the database is available."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency that provides a database session."""
    logger = logging.getLogger("app.db.session")
    db: Session = SessionLocal()
    logger.debug("Opened new DB session %s", db)
    try:
        yield db
    finally:
        logger.debug("Closing DB session %s", db)
        try:
            db.close()
        except IllegalStateChangeError:
            logger.exception("IllegalStateChangeError while closing DB session")
            raise
        except Exception:
            logger.exception("Unexpected error while closing DB session")
            raise


def get_masked_database_url() -> str:
    """Return the configured DATABASE_URL with the password masked for safe logging."""
    raw = settings.DATABASE_URL or ""
    try:
        # replace :password@ with :***@ to avoid printing credentials
        return re.sub(r"://([^:/@]+):([^@]+)@", r"://\1:***@", raw)
    except Exception:
        return raw


def test_connection() -> None:
    """Attempt a simple connection and select 1 to validate DB reachability.

    Raises the underlying exception if the DB cannot be reached.
    """
    logger = logging.getLogger("app.db.session")
    logger.debug("Testing DB connection to %s", get_masked_database_url())
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection test succeeded")
    except Exception:
        logger.exception("Database connection test failed")
        raise