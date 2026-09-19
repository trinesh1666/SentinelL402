from app.database import SessionLocal
from app.models import Payment


PAYMENT_ID = 460


db = SessionLocal()

try:

    print()
    print("===================================")
    print("SentinelL402 - Payment Record Test")
    print("===================================")
    print()

    payment = (
        db.query(Payment)
        .filter(Payment.id == PAYMENT_ID)
        .first()
    )

    if payment is None:
        print("ERROR: Payment not found.")
    else:

        invoice = payment.invoice

        print("Payment ID:")
        print(payment.id)
        print()

        print("User ID:")
        print(payment.user_id)
        print()

        print("Amount:")
        print(payment.amount_sats)
        print()

        print("Status:")
        print(payment.status)
        print()

        print("Invoice Python type:")
        print(type(invoice))
        print()

        print("Invoice length:")
        print(len(invoice) if invoice else 0)
        print()

        print("Invoice prefix:")
        print(invoice[:20] if invoice else "")
        print()

        print("Invoice starts with lnbc:")
        print(
            invoice.lower().startswith("lnbc")
            if invoice
            else False
        )
        print()

        print("Payment hash exists:")
        print(bool(payment.payment_hash))
        print()

        print("Expires at:")
        print(payment.expires_at)
        print()

        print("Credits granted:")
        print(payment.credits_granted)
        print()

        print("===================================")
        print("PAYMENT RECORD TEST COMPLETE")
        print("===================================")
        print()

finally:
    db.close()