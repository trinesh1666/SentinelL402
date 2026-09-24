from sqlalchemy import text
from sqlalchemy.orm import Session


def check_database(db: Session) -> bool:
    """Return True when the database is reachable."""
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False