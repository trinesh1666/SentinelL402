import asyncio

from nostrwalletconnect import NWCClient

from app.config import (
    TEST_PAYER_NWC_CONNECTION_STRING,
    require_setting,
)


PAYER_NWC_URI = require_setting(
    TEST_PAYER_NWC_CONNECTION_STRING,
    "TEST_PAYER_NWC_CONNECTION_STRING",
)


async def main():

    print()
    print("===================================")
    print("SentinelL402 - API Invoice Payer")
    print("===================================")
    print()

    invoice = input(
        "Paste the API-generated Lightning invoice: "
    ).strip()

    if not invoice:
        print()
        print("ERROR: Invoice cannot be empty.")
        return

    print()
    print("Paying API-generated invoice...")
    print()

    async with NWCClient(PAYER_NWC_URI) as nwc:

        result = await nwc.pay_invoice(
            invoice=invoice
        )

        print("===================================")
        print("PAYMENT SUCCESSFUL")
        print("===================================")
        print()

        print("Payment completed successfully.")
        print()

        print("Payment result:")
        print(result)
        print()


if __name__ == "__main__":
    asyncio.run(main())