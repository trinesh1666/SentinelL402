from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.schemas.security_analysis import (
    SecurityAnalysisRequest,
)
from app.services.metering_service import (
    can_use_ai,
    consume_credit,
    get_usage,
)
from app.services.payment_service import (
    create_payment,
    get_pending_payment,
)
from app.services.security_analysis_service import (
    perform_security_analysis,
)


def run_metered_security_analysis(
    db: Session,
    request: SecurityAnalysisRequest,
    authenticated_user: str,
):
    """
    Run security analysis through the SentinelL402
    metering and payment boundary.

    authenticated_user is the identity obtained from
    the X-API-Key authentication layer.

    request.source is only the source of the
    security/network data.
    """

    usage_before = get_usage(
        db,
        authenticated_user,
    )

    if not can_use_ai(
        db,
        authenticated_user,
    ):
        pending_payment = get_pending_payment(
            db,
            authenticated_user,
        )

        if not pending_payment:
            pending_payment = create_payment(
                db,
                authenticated_user,
            )

        if not pending_payment:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "payment_creation_failed",
                    "message": (
                        "Unable to create "
                        "Lightning payment."
                    ),
                },
            )

        raise HTTPException(
            status_code=402,
            detail={
                "error": "payment_required",
                "message": (
                    "AI credits exhausted. "
                    "Please pay the Lightning invoice "
                    "to continue."
                ),
                "payment_method": "lightning",
                "payment_id": pending_payment.id,
                "amount_sats": pending_payment.amount_sats,
                "invoice": pending_payment.invoice,
                "payment_hash": pending_payment.payment_hash,
                "credits_to_add": 5,
            },
        )

    result = perform_security_analysis(
        db,
        request,
    )

    success = consume_credit(
        db,
        authenticated_user,
    )

    if not success:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "payment_required",
                "message": (
                    "Unable to consume AI credit."
                ),
                "payment_method": "lightning",
                "amount_sats": 10,
            },
        )

    usage_after = get_usage(
        db,
        authenticated_user,
    )

    result.credits_remaining = (
        usage_after["credits_remaining"]
    )

    return result