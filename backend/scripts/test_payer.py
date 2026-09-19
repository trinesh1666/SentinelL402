import asyncio
import json
from pathlib import Path

from nostrwalletconnect import NWCClient

from app.config import TEST_PAYER_NWC_CONNECTION_STRING, require_setting


PAYER_NWC_URI = require_setting(
    TEST_PAYER_NWC_CONNECTION_STRING,
    "TEST_PAYER_NWC_CONNECTION_STRING",
)

INVOICE_FILE = Path(__file__).parent / "lightning_invoice.json"


async def main():

    print()
    print("===================================")
    print("SentinelL402 - Test Payer")
    print("===================================")
    print()

    if not INVOICE_FILE.exists():
        print("ERROR: lightning_invoice.json not found.")
        print()
        print("Create an invoice first.")
        return

    with open(INVOICE_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    invoice = data.get("invoice")

    if not invoice:
        print("ERROR: No invoice found in lightning_invoice.json.")
        return

    print("Saved invoice found.")
    print()
    print("Paying the saved 1-sat invoice...")
    print()

    async with NWCClient(PAYER_NWC_URI) as nwc:

        result = await nwc.pay_invoice(
            invoice=invoice
        )

        print("===================================")
        print("PAYMENT SUCCESSFUL")
        print("===================================")
        print()

        print("Payment result:")
        print(result)
        print()


if __name__ == "__main__":
    asyncio.run(main())