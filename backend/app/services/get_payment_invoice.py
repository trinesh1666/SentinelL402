from app.database import SessionLocal
from app.models import Payment


PAYMENT_ID = 411


db = SessionLocal()

try:
    payment = (
        db.query(Payment)
        .filter(Payment.id == PAYMENT_ID)
        .first()
    )

    if not payment:
        print("Payment #411 not found.")
    else:
        print("Payment ID:", payment.id)
        print("Status:", payment.status)
        print("Amount:", payment.amount_sats, "sats")
        print("Invoice:")
        print(payment.invoice)

finally:
    db.close()