import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite local database file inside backend directory
DATABASE_URL = "sqlite:///./medigenie.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} # Required for SQLite with FastAPI
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()