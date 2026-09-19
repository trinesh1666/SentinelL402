from app.database import SessionLocal
from app.models import Payment, User
from app.services.lightning_service import check_lightning_payment


USER_ID = "docker-demo-user"
PAYMENT_ID = 459


def main():
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.user_id == USER_ID)
            .first()
        )

        if not user:
            print("User not found.")
            return

        payment = (
            db.query(Payment)
            .filter(
                Payment.id == PAYMENT_ID,
                Payment.user_id == user.id,
            )
            .first()
        )

        if not payment:
            print("Payment not found.")
            return

        print()
        print("===================================")
        print("SentinelL402 Lightning Diagnostic")
        print("===================================")
        print(f"Payment ID : {payment.id}")
        print(f"User       : {USER_ID}")
        print(f"Status     : {payment.status}")
        print(f"Amount     : {payment.amount_sats} sats")
        print()

        if not payment.payment_hash:
            print("No payment hash available.")
            return

        print("Checking Lightning wallet...")
        print()

        result = check_lightning_payment(
            payment.payment_hash
        )

        print()
        print("===================================")
        print("RESULT")
        print("===================================")
        print(f"Result type : {type(result)}")
        print(f"Paid        : {getattr(result, 'paid', None)}")
        print(f"Status      : {getattr(result, 'status', None)}")
        print("===================================")

    finally:
        db.close()


if __name__ == "__main__":
    main()