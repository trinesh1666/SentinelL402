from app.database import SessionLocal
from app.services.api_key_service import create_api_key


USER_ID = "test_user_001"


db = SessionLocal()

try:
    print()
    print("===================================")
    print("SentinelL402 - Generate API Key")
    print("===================================")
    print()

    api_key, api_key_record = create_api_key(
        db=db,
        user_id=USER_ID,
        name="SentinelL402 Test User Key",
    )

    print("API KEY CREATED SUCCESSFULLY")
    print()
    print("User ID:")
    print(USER_ID)
    print()
    print("Database API Key ID:")
    print(api_key_record.id)
    print()
    print("API Key:")
    print(api_key)
    print()
    print("===================================")
    print("IMPORTANT")
    print("Save this API key securely.")
    print("It will not be recoverable from the database.")
    print("===================================")
    print()

finally:
    db.close()