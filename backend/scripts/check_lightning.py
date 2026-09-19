import asyncio
import os

from nostrwalletconnect import NWCClient
from nostrwalletconnect.types import NWCError

from app.config import NWC_CONNECTION_STRING
NWC_URI = NWC_CONNECTION_STRING

HASH_FILE = "backend/test_payment_hash.txt"


async def main():

    print()
    print("===================================")
    print("VERIFY FRESH LIGHTNING PAYMENT")
    print("===================================")

    if not NWC_URI:
        print("ERROR: NWC_CONNECTION_STRING is not configured.")
        return

    if not os.path.exists(HASH_FILE):
        print("ERROR: Payment hash file does not exist.")
        print("Run create_test_invoice.py first.")
        return

    with open(HASH_FILE, "r", encoding="utf-8") as file:
        payment_hash = file.read().strip()

    if not payment_hash:
        print("ERROR: Payment hash file is empty.")
        return

    print()
    print("Payment hash loaded successfully.")
    print("Connecting to receiver wallet...")
    print("Looking up payment...")
    print()

    try:

        async with NWCClient(NWC_URI) as nwc:

            try:

                result = await nwc.lookup_invoice(
                    payment_hash=payment_hash
                )

                print("===================================")
                print("RECEIVER LOOKUP RESULT")
                print("===================================")

                print("Result type:", type(result))
                print("Paid:", getattr(result, "paid", None))
                print("Amount:", getattr(result, "amount", None))
                print("Description:", getattr(result, "description", None))
                print("Created at:", getattr(result, "created_at", None))
                print("Settled at:", getattr(result, "settled_at", None))

                print("===================================")

            except NWCError as exc:

                print()
                print("NWC ERROR")
                print("-----------------------------------")
                print("Error:", exc)
                print("-----------------------------------")

    except Exception as exc:

        print()
        print("CONNECTION ERROR")
        print("-----------------------------------")
        print("Error:", exc)
        print("-----------------------------------")


if __name__ == "__main__":
    asyncio.run(main())