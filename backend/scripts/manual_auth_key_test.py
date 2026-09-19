from app.database import SessionLocal
from app.services.api_key_service import authenticate_api_key


db = SessionLocal()

try:
    print()
    print("===================================")
    print("SentinelL402 - Direct API Key Test")
    print("===================================")
    print()

    api_key = input("Paste your SentinelL402 API key: ").strip()

    if not api_key:
        print()
        print("ERROR: API key cannot be empty.")
    else:
        print()
        print("Testing API key authentication...")
        print()

        user = authenticate_api_key(
            db,
            api_key
        )

        if user is None:
            print("===================================")
            print("AUTHENTICATION FAILED")
            print("authenticate_api_key() returned None")
            print("===================================")
        else:
            print("===================================")
            print("AUTHENTICATION SUCCESSFUL")
            print("===================================")
            print()
            print("Database User ID:", user.id)
            print("User ID:", user.user_id)
            print("Email:", user.email)
            print()

finally:
    db.close()