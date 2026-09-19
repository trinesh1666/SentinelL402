import asyncio

from nostrwalletconnect import NWCClient

from app.config import NWC_CONNECTION_STRING, require_setting


NWC_URI = require_setting(
    NWC_CONNECTION_STRING,
    "NWC_CONNECTION_STRING",
)


async def main():

    print()
    print("===================================")
    print("SentinelL402 - Invoice Object Test")
    print("===================================")
    print()

    async with NWCClient(NWC_URI) as nwc:

        print("Creating fresh 10-sat invoice...")
        print()

        result = await nwc.make_invoice(
            amount=10_000,
            description="SentinelL402 API invoice debug",
        )

        print("Invoice response type:")
        print(type(result))
        print()

        print("Invoice response:")
        print(result)
        print()

        print("Invoice attribute type:")
        print(type(getattr(result, "invoice", None)))
        print()

        print("Invoice length:")
        print(len(getattr(result, "invoice", "")))
        print()

        invoice = getattr(result, "invoice", "")

        print("Invoice prefix:")
        print(invoice[:20])
        print()

        print("Payment hash exists:")
        print(bool(getattr(result, "payment_hash", None)))
        print()

        print("===================================")
        print("INVOICE OBJECT TEST COMPLETE")
        print("===================================")
        print()


if __name__ == "__main__":
    asyncio.run(main())