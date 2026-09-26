from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import SecurityAnalysis, User

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

    # --------------------------------------------------------
    # RUN ML SECURITY ANALYSIS
    # --------------------------------------------------------

    result = perform_security_analysis(
        db,
        request,
    )

    # --------------------------------------------------------
    # CONSUME ONE AI CREDIT
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # UPDATE REMAINING CREDITS
    # --------------------------------------------------------

    usage_after = get_usage(
        db,
        authenticated_user,
    )

    result.credits_remaining = (
        usage_after["credits_remaining"]
    )

    # --------------------------------------------------------
    # FIND AUTHENTICATED USER
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.user_id == authenticated_user
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Authenticated user was not found.",
        )

    # --------------------------------------------------------
    # SAVE SECURITY ANALYSIS HISTORY
    # --------------------------------------------------------

    security_analysis = SecurityAnalysis(
        user_id=user.id,
        source=request.source,
        event_type=request.event_type,
        severity=request.severity,
        description=request.description,
        ml_prediction=result.ml_prediction,
        ml_label=result.ml_label,
        confidence=result.confidence,
        risk_level=result.risk_level,
        explanation=result.explanation,
        recommendation=result.recommendation,
        llm_analysis=None,
    )

    db.add(security_analysis)
    db.commit()
    db.refresh(security_analysis)

    return result