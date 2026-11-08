"""
Database engine, session management, and SQLite foreign key enforcement.
"""

from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from database.base import Base

# Project root: c:\Users\ASUS\Videos\CareerAI\CareerMind-AI\backend
BACKEND_ROOT = Path(__file__).resolve().parent.parent

# Database file location: backend/careermind.db
DATABASE_PATH = BACKEND_ROOT / "careermind.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# Enable SQLite foreign-key enforcement
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a scoped database session.
    Guarantees session closure upon request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
