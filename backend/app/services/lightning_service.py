import asyncio
import logging

from nostrwalletconnect import NWCClient

from app.config import (
    LIGHTNING_PROVIDER,
    NWC_CONNECTION_STRING,
    require_setting,
)
from app.middleware.error_handling import LightningServiceError
from app.services.mock_lightning_service import (
    check_mock_payment,
    create_mock_invoice,
)

logger = logging.getLogger("sentinell402.lightning")

PAYMENT_AMOUNT_SATS = 10


def _get_nwc_uri() -> str:
    return require_setting(
        NWC_CONNECTION_STRING,
        "NWC_CONNECTION_STRING",
    )


async def _create_nwc_invoice(
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


async def _check_nwc_payment(
    payment_hash: str,
):
    try:
        nwc_uri = _get_nwc_uri()

        async with NWCClient(nwc_uri) as nwc:
            result = await nwc.lookup_invoice(
                payment_hash=payment_hash
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

        return result

    except LightningServiceError:
        raise

    except Exception as exc:
        raise LightningServiceError(
            "Lightning payment lookup failed."
        ) from exc


def create_lightning_invoice(
    amount_sats: int,
    description: str,
):
    provider = LIGHTNING_PROVIDER

    if provider == "mock":
        return create_mock_invoice(
            amount_sats,
            description,
        )

    if provider == "nwc":
        return asyncio.run(
            _create_nwc_invoice(
                amount_sats,
                description,
            )
        )

    raise LightningServiceError(
        f"Unsupported LIGHTNING_PROVIDER: {provider}"
    )


def check_lightning_payment(
    payment_hash: str,
):
    provider = LIGHTNING_PROVIDER

    if provider == "mock":
        return check_mock_payment(
            payment_hash
        )

    if provider == "nwc":
        return asyncio.run(
            _check_nwc_payment(
                payment_hash
            )
        )

    raise LightningServiceError(
        f"Unsupported LIGHTNING_PROVIDER: {provider}"
    )