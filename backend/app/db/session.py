from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.models.models import Base


def _build_engine() -> object:
    database_url = settings.DATABASE_URL or "sqlite:///./medigenie_cdss.db"
    if database_url.startswith("postgresql") and database_url.count("localhost"):
        return create_engine("sqlite:///./medigenie_cdss.db", pool_pre_ping=True)
    return create_engine(database_url, pool_pre_ping=True)


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
    """
    FastAPI dependency that provides a database session.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()