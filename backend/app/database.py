from pathlib import Path

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
)


# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# SQLite database
DATABASE_URL = (
    f"sqlite:///{DATA_DIR / 'sentinell402.db'}"
)


# SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
)


@event.listens_for(
    engine,
    "connect",
)
def enable_sqlite_foreign_keys(
    dbapi_connection,
    connection_record,
):
    cursor = dbapi_connection.cursor()

    cursor.execute(
        "PRAGMA foreign_keys=ON"
    )

    cursor.close()


# Database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Base model
Base = declarative_base()


def upgrade_schema():
    """Apply small additive migrations to existing SQLite databases."""
    columns = {
        column["name"]
        for column in inspect(engine).get_columns("payments")
    }

    if "expires_at" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE payments "
                    "ADD COLUMN expires_at DATETIME"
                )
            )


# Dependency
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()