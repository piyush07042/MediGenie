"""
Shared pytest fixtures for MediGenie.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    from fastapi.testclient import TestClient
except Exception:  # pragma: no cover - fallback for incompatible deps
    TestClient = None

from app.db.session import get_db
from app.main import app
from app.models.models import Base

TEST_DATABASE_URL = "sqlite:///./test_medigenie.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Create all database tables before tests
    and drop them afterwards.
    """

    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """
    Shared FastAPI test client.
    """

    if TestClient is None:
        pytest.skip("FastAPI TestClient is unavailable in this environment")

    return TestClient(app)