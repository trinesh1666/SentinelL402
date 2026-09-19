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
        print("No saved invoice found.")
        print("Create an invoice first.")
        print()
        return

    with open(INVOICE_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    payment_hash = data["payment_hash"]
    invoice = data["invoice"]

    async with NWCClient(NWC_URI) as nwc:

        print()
        print("===================================")
        print("SentinelL402 - Check Payment")
        print("===================================")
        print()

        print("Checking payment hash:")
        print(payment_hash)
        print()

        status = await nwc.lookup_invoice(
            payment_hash=payment_hash
        )

        print("Invoice:")
        print(invoice)
        print()

        print("Payment status:")
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
        print("Invalid option.")


if __name__ == "__main__":
    asyncio.run(main())