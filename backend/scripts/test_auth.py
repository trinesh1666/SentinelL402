from app.database import SessionLocal
from app.models import User


db = SessionLocal()

try:
    users = db.query(User).all()

    print()
    print("===================================")
    print("SentinelL402 - Users Diagnostic")
    print("===================================")
    print()

    if not users:
        print("No users found in database.")

    for user in users:
        print("Database ID:", user.id)
        print("User ID:", user.user_id)
        print("Email:", user.email)
        print("-----------------------------------")

finally:
    db.close()