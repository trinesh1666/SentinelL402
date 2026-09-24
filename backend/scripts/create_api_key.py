from app.database import SessionLocal
from app.services.api_key_service import create_api_key

USER_ID = "string"
KEY_NAME = "sentinell402-development-key"


def main():
    db = SessionLocal()

    try:
        raw_key, api_key = create_api_key(
            db=db,
            user_id=USER_ID,
            name=KEY_NAME,
        )

        print()
        print("===================================")
        print("API KEY CREATED")
        print("===================================")
        print(f"User: {USER_ID}")
        print(f"Key ID: {api_key.id}")
        print(f"API Key: {raw_key}")
        print("===================================")
        print()
        print("IMPORTANT: Save this API key.")
        print("It cannot be recovered from the database later.")

    finally:
        db.close()


if __name__ == "__main__":
    main()