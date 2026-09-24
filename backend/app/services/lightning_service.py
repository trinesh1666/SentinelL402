import asyncio
import logging
from unittest import result
from nostrwalletconnect import NWCClient

from app.config import NWC_CONNECTION_STRING, require_setting
from app.middleware.error_handling import LightningServiceError
logger = logging.getLogger("sentinell402.lightning")
PAYMENT_AMOUNT_SATS = 10

from app.config import (
    NWC_CONNECTION_STRING,
    require_setting,
)

from app.middleware.error_handling import (
    LightningServiceError,
)
logger.info(
    "Lightning payment lookup completed",
    extra={
        "payment_status": getattr(
            result,
            "status",
            None,
        ),
        "payment_paid": getattr(
            result,
            "paid",
            None,
        ),
    },
)
def _get_nwc_uri() -> str:
    return require_setting(
        NWC_CONNECTION_STRING,
        "NWC_CONNECTION_STRING",
    )


async def _create_invoice(
    amount_sats: int,
    description: str,
):
    try:
        nwc_uri = _get_nwc_uri()

        async with NWCClient(nwc_uri) as nwc:
            invoice = await nwc.make_invoice(
                amount=amount_sats * 1000,
                description=description,
            )

        return invoice

    except LightningServiceError:
        raise

    except Exception as exc:
        raise LightningServiceError(
            "Lightning invoice creation failed."
        ) from exc

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
    try:
        nwc_uri = _get_nwc_uri()

        async with NWCClient(nwc_uri) as nwc:
            result = await nwc.lookup_invoice(
                payment_hash=payment_hash
            )

        print("LIGHTNING PAYMENT LOOKUP")
        print(
            payment_hash,
            result,
            type(result),
            getattr(result, "paid", None),
            getattr(result, "status", None),
        )

        return result

    except LightningServiceError:
        raise

    except Exception as exc:
        raise LightningServiceError(
            "Lightning payment lookup failed."
        ) from exc


def check_lightning_payment(
    payment_hash: str,
):
    return asyncio.run(
        _check_lightning_payment(
            payment_hash
        )
    )