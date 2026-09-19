from app.database import SessionLocal
from app.models import APIKey, User


db = SessionLocal()

try:
    keys = db.query(APIKey).all()

    print()
    print("===================================")
    print("SentinelL402 - API Key Diagnostic")
    print("===================================")
    print()

    if not keys:
        print("No API keys found in database.")

    for key in keys:

        user = (
            db.query(User)
            .filter(User.id == key.user_id)
            .first()
        )

        print("Key ID:", key.id)
        print("Database User ID:", key.user_id)

        if user:
            print("User ID:", user.user_id)
            print("Email:", user.email)
        else:
            print("User: NOT FOUND")

        print("Name:", key.name)
        print("Active:", key.active)
        print("-----------------------------------")

finally:
    db.close()