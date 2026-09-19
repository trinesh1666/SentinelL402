import asyncio

from nostrwalletconnect import NWCClient

from app.config import (
    TEST_PAYER_NWC_CONNECTION_STRING,
    require_setting,
)
from app.database import SessionLocal
from app.models import Payment


PAYMENT_ID = 461

PAYER_NWC_URI = require_setting(
    TEST_PAYER_NWC_CONNECTION_STRING,
    "TEST_PAYER_NWC_CONNECTION_STRING",
)


async def main():

    print()
    print("===================================")
    print("SentinelL402 - Database Invoice Payer")
    print("===================================")
    print()

    db = SessionLocal()

    try:
        payment = (
            db.query(Payment)
            .filter(Payment.id == PAYMENT_ID)
            .first()
        )

        if payment is None:
            print("ERROR: Payment not found.")
            return

        invoice = payment.invoice

        print("Payment ID:")
        print(payment.id)
        print()

        print("Amount:")
        print(payment.amount_sats)
        print()

        print("Invoice type:")
        print(type(invoice))
        print()

        print("Invoice length:")
        print(len(invoice))
        print()

        print("Invoice prefix:")
        print(invoice[:20])
        print()

        print("Paying database invoice...")
        print()

    finally:
        db.close()

    async with NWCClient(PAYER_NWC_URI) as nwc:

        result = await nwc.pay_invoice(
            invoice=invoice
        )

    print("===================================")
    print("PAYMENT SUCCESSFUL")
    print("===================================")
    print()

    print("Payment result type:")
    print(type(result))
    print()

    print("Payment completed successfully.")
    print()


if __name__ == "__main__":
    asyncio.run(main())