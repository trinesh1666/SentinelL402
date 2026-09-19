import asyncio
import json
from pathlib import Path

from nostrwalletconnect import NWCClient

from app.config import NWC_CONNECTION_STRING, require_setting


NWC_URI = require_setting(
    NWC_CONNECTION_STRING,
    "NWC_CONNECTION_STRING",
)

INVOICE_FILE = Path(__file__).parent / "lightning_invoice.json"


async def create_invoice():
    async with NWCClient(NWC_URI) as nwc:

        print()
        print("===================================")
        print("SentinelL402 - Create Invoice")
        print("===================================")
        print()

        print("Creating 1-sat invoice...")
        print()

        result = await nwc.make_invoice(
            amount=1000,
            description="SentinelL402 L402 payment test",
        )

        data = {
            "invoice": result.invoice,
            "payment_hash": result.payment_hash,
        }

        with open(INVOICE_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

        print("Invoice created successfully.")
        print()
        print("Invoice:")
        print(result.invoice)
        print()
        print("Payment hash:")
        print(result.payment_hash)
        print()
        print("Invoice saved to:")
        print(INVOICE_FILE)
        print()

        print("===================================")
        print("PAY THIS INVOICE FROM YOUR")
        print("LIGHTNING WALLET")
        print("===================================")
        print()


async def check_invoice():
    if not INVOICE_FILE.exists():
        print()
        print("ERROR: No saved invoice found.")
        print()
        print("Run option 1 first.")
        return

    with open(INVOICE_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    invoice = data["invoice"]
    payment_hash = data["payment_hash"]

    async with NWCClient(NWC_URI) as nwc:

        print()
        print("===================================")
        print("SentinelL402 - Check Payment")
        print("===================================")
        print()

        print("Saved payment hash:")
        print(payment_hash)
        print()

        print("Checking invoice status...")
        print()

        status = await nwc.lookup_invoice(
            payment_hash=payment_hash
        )

        print("Invoice status:")
        print(status)
        print()

        if status.paid:
            print("===================================")
            print("PAYMENT VERIFIED")
            print("paid=True")
            print("===================================")
        else:
            print("===================================")
            print("PAYMENT NOT RECEIVED")
            print("paid=False")
            print("===================================")

        print()


async def main():

    print()
    print("===================================")
    print("SentinelL402 Lightning Controller")
    print("===================================")
    print()

    print("1. Create new invoice")
    print("2. Check saved invoice")
    print()

    choice = input("Enter option (1/2): ").strip()

    if choice == "1":
        await create_invoice()

    elif choice == "2":
        await check_invoice()

    else:
        print()
        print("Invalid option.")
        print("Please enter 1 or 2.")


if __name__ == "__main__":
    asyncio.run(main())