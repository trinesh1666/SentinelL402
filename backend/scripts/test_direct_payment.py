import asyncio

from nostrwalletconnect import NWCClient

from app.config import (
    NWC_CONNECTION_STRING,
    TEST_PAYER_NWC_CONNECTION_STRING,
    require_setting,
)


RECEIVER_NWC_URI = require_setting(
    NWC_CONNECTION_STRING,
    "NWC_CONNECTION_STRING",
)

PAYER_NWC_URI = require_setting(
    TEST_PAYER_NWC_CONNECTION_STRING,
    "TEST_PAYER_NWC_CONNECTION_STRING",
)


async def main():

    print()
    print("===================================")
    print("SentinelL402 - Direct Payment Test")
    print("===================================")
    print()

    # ---------------------------------
    # STEP 1: Create invoice
    # ---------------------------------

    print("Creating fresh 10-sat invoice...")
    print()

    async with NWCClient(RECEIVER_NWC_URI) as receiver:

        invoice_result = await receiver.make_invoice(
            amount=10_000,
            description="SentinelL402 direct payment test",
        )

        invoice = invoice_result.invoice
        payment_hash = invoice_result.payment_hash

    print("Invoice created.")
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
    print("Payment hash exists:")
    print(bool(payment_hash))
    print()

    # ---------------------------------
    # STEP 2: Pay invoice
    # ---------------------------------

    print("Paying fresh invoice...")
    print()

    async with NWCClient(PAYER_NWC_URI) as payer:

        payment_result = await payer.pay_invoice(
            invoice=invoice
        )

    print("===================================")
    print("PAYMENT SUCCESSFUL")
    print("===================================")
    print()
    print("Payment result type:")
    print(type(payment_result))
    print()

    # ---------------------------------
    # STEP 3: Verify payment
    # ---------------------------------

    print("Checking payment status...")
    print()

    async with NWCClient(RECEIVER_NWC_URI) as receiver:

        status = await receiver.lookup_invoice(
            payment_hash=payment_hash
        )

    print("Payment status:")
    print(status)
    print()

    print("Paid:")
    print(getattr(status, "paid", None))
    print()

    print("===================================")
    print("DIRECT PAYMENT TEST COMPLETE")
    print("===================================")
    print()


if __name__ == "__main__":
    asyncio.run(main())