import asyncio

from nostrwalletconnect import NWCClient

from app.config import NWC_CONNECTION_STRING, require_setting


PAYMENT_AMOUNT_SATS = 10


def _get_nwc_uri() -> str:
    return require_setting(
        NWC_CONNECTION_STRING,
        "NWC_CONNECTION_STRING",
    )


async def _create_invoice(
    amount_sats: int,
    description: str,
):
    nwc_uri = _get_nwc_uri()

    async with NWCClient(nwc_uri) as nwc:
        invoice = await nwc.make_invoice(
            amount=amount_sats * 1000,
            description=description,
        )

        return invoice


def create_lightning_invoice(
    amount_sats: int,
    description: str,
):
    return asyncio.run(
        _create_invoice(
            amount_sats,
            description,
        )
    )


async def _check_lightning_payment(
    payment_hash: str,
):
    nwc_uri = _get_nwc_uri()

    async with NWCClient(nwc_uri) as nwc:
        result = await nwc.lookup_invoice(
            payment_hash=payment_hash
        )

        print()
        print("===================================")
        print("LIGHTNING PAYMENT LOOKUP")
        print("===================================")
        print(f"Payment hash: {payment_hash}")
        print(f"Lookup result: {result}")
        print(f"Result type: {type(result)}")
        print(
            f"Paid attribute: "
            f"{getattr(result, 'paid', None)}"
        )
        print(
            f"Status attribute: "
            f"{getattr(result, 'status', None)}"
        )
        print("===================================")

        return result


def check_lightning_payment(
    payment_hash: str,
):
    return asyncio.run(
        _check_lightning_payment(
            payment_hash
        )
    )