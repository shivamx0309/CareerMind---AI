"""
Database engine, session management, and SQLite foreign key enforcement.
Supports environment-driven DATABASE_URL for seamless PostgreSQL portability.
"""

import os
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

# Project root: c:\Users\ASUS\Videos\CareerAI\CareerMind-AI\backend
BACKEND_ROOT = Path(__file__).resolve().parent.parent

# Database file location: backend/careermind.db
DATABASE_PATH = BACKEND_ROOT / "careermind.db"
DEFAULT_SQLITE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)

is_sqlite = DATABASE_URL.startswith("sqlite")

# Ensure the database parent directory exists before connecting (critical for /var/data on Render)
if is_sqlite:
    db_file_str = DATABASE_URL.replace("sqlite:///", "", 1)
    if db_file_str and not db_file_str.startswith(":memory:"):
        db_file_path = Path(db_file_str)
        try:
            db_file_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

engine_kwargs = {}
if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    echo=False,
    **engine_kwargs,
)

# Enable SQLite foreign-key enforcement only when using SQLite
if is_sqlite:
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
