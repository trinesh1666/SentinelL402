import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "sentinell402.db"


def migrate():
    print("===================================")
    print("SentinelL402 Database Migration")
    print("===================================")
    print(f"Database: {DB_PATH}")

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute("PRAGMA table_info(payments)")
        columns = [row[1] for row in cursor.fetchall()]

        print(f"Existing payment columns: {columns}")

        if "expires_at" in columns:
            print()
            print("expires_at already exists.")
            print("No changes were made.")
            return

        print()
        print("Adding expires_at column...")

        cursor.execute(
            """
            ALTER TABLE payments
            ADD COLUMN expires_at DATETIME
            """
        )

        connection.commit()

        print("expires_at column added successfully.")

        cursor.execute("PRAGMA table_info(payments)")
        updated_columns = [row[1] for row in cursor.fetchall()]

        print()
        print(f"Updated payment columns: {updated_columns}")

        if "expires_at" not in updated_columns:
            raise RuntimeError(
                "Migration verification failed."
            )

        print()
        print("===================================")
        print("Migration successful.")
        print("Existing payments were preserved.")
        print("===================================")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    migrate()