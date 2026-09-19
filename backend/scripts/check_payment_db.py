from app.database import SessionLocal
from app.models import Payment, User


USER_ID = "docker-demo-user"


def main():
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.user_id == USER_ID)
            .first()
        )

        print()
        print("===================================")
        print("SentinelL402 User Payment Check")
        print("===================================")
        print(f"User: {USER_ID}")

        if not user:
            print("User not found.")
            return

        payments = (
            db.query(Payment)
            .filter(Payment.user_id == user.id)
            .order_by(Payment.id.desc())
            .all()
        )

        print(f"Payments for user: {len(payments)}")
        print()

        for payment in payments:
            print("-----------------------------------")
            print(f"Payment ID      : {payment.id}")
            print(f"Amount (sats)   : {payment.amount_sats}")
            print(f"Status          : {payment.status}")
            print(f"Credits granted : {payment.credits_granted}")
            print(f"Created at      : {payment.created_at}")
            print(f"Expires at      : {payment.expires_at}")

    finally:
        db.close()


if __name__ == "__main__":
    main()