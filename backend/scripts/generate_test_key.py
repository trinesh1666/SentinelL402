from app.database import SessionLocal
from app.services.api_key_service import create_api_key

USER_ID = "l402-agent-api-demo-user"

db = SessionLocal()

try:
    raw_api_key, api_key = create_api_key(
        db,
        USER_ID,
        "manual-curl-test",
    )

    print("=" * 50)
    print("NEW TEST API KEY")
    print("=" * 50)
    print("User:", USER_ID)
    print("Key ID:", api_key.id)
    print("API Key:", raw_api_key)
    print("=" * 50)
    print("Use this key for the next test.")
    print("Do NOT share it.")
finally:
    db.close()