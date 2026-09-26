import logging
from datetime import datetime, timedelta, timezone
from typing import cast

from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.middleware.database_errors import DatabaseServiceError
from app.models import Account, Payment, User
from app.services.lightning_service import (
    PAYMENT_AMOUNT_SATS,
    check_lightning_payment,
    create_lightning_invoice,
)

logger = logging.getLogger("sentinell402.payment")


CREDITS_PER_PAYMENT = 5
PAYMENT_EXPIRY_MINUTES = 60


def _utc_now():
    return datetime.now(timezone.utc)


def _is_payment_expired(payment: Payment) -> bool:
    expires_at = cast(
        datetime | None,
        payment.expires_at,
    )

    if expires_at is None:
        return False

    # SQLite may return DateTime values without timezone information.
    # Treat those values as UTC.
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    return bool(
        expires_at <= _utc_now()
    )


def _grant_payment_credits_once(
    db: Session,
    payment: Payment,
) -> bool:
    """
    Atomically grant credits for a payment.

    The payment row is first claimed by changing
    credits_granted from 0 to CREDITS_PER_PAYMENT.

    Returns:
        True  -> credits were granted by this transaction.
        False -> credits had already been granted.
    """

    account = (
        db.query(Account)
        .filter(
            Account.user_id == payment.user_id
        )
        .first()
    )

    if account is None:
        raise DatabaseServiceError(
            "Payment account not found."
        )

    # Atomically claim the credit grant.
    #
    # Only one transaction can successfully change
    # credits_granted from 0 to 5.
    result = db.execute(
        update(Payment)
        .where(
            Payment.id == payment.id,
            Payment.credits_granted == 0,
        )
        .values(
            credits_granted=CREDITS_PER_PAYMENT,
        )
    )

    if result.rowcount != 1:
        return False

    # Grant the credits in the same database transaction.
    account_update = db.execute(
        update(Account)
        .where(
            Account.id == account.id,
        )
        .values(
            credits=Account.credits
            + CREDITS_PER_PAYMENT,
        )
    )

    if account_update.rowcount != 1:
        raise DatabaseServiceError(
            "Failed to update payment account credits."
        )

    return True


def create_payment(
    db: Session,
    user_id: str,
):
    from app.services.metering_service import (
        get_or_create_user,
    )

    user = get_or_create_user(
        db,
        user_id,
    )

    # Look for the most recent pending payment.
    existing_payment = (
        db.query(Payment)
        .filter(
            Payment.user_id == user.id,
            Payment.status == "pending",
        )
        .order_by(
            Payment.created_at.desc()
        )
        .first()
    )

    if existing_payment:
        # Reuse the existing invoice if it has not expired.
        if not _is_payment_expired(
            existing_payment
        ):
            logger.info(
                "Payment request reused | "
                "user_id=%s | payment_id=%s",
                user_id,
                existing_payment.id,
            )

            return existing_payment

        # The invoice is too old.
        # Mark it expired before creating a fresh payment.
        setattr(
            existing_payment,
            "status",
            "expired",
        )

        try:
            db.commit()

        except SQLAlchemyError as exc:
            db.rollback()

            raise DatabaseServiceError(
                "Failed to update payment expiration state."
            ) from exc

    # Create a new Lightning invoice.
    invoice_response = create_lightning_invoice(
        PAYMENT_AMOUNT_SATS,
        "SentinelL402 AI credits",
    )

    invoice = getattr(
        invoice_response,
        "invoice",
        invoice_response,
    )

    payment_hash = getattr(
        invoice_response,
        "payment_hash",
        None,
    )

    now = _utc_now()

    payment = Payment(
        user_id=user.id,
        amount_sats=PAYMENT_AMOUNT_SATS,
        invoice=invoice,
        payment_hash=payment_hash,
        status="pending",
        expires_at=(
            now
            + timedelta(
                minutes=PAYMENT_EXPIRY_MINUTES
            )
        ),
    )

    db.add(payment)

    try:
        db.commit()
        db.refresh(payment)

    except SQLAlchemyError as exc:
        db.rollback()

        raise DatabaseServiceError(
            "Failed to save payment."
        ) from exc

    return payment


def get_pending_payment(
    db: Session,
    user_id: str,
):
    user = (
        db.query(User)
        .filter(
            User.user_id == user_id
        )
        .first()
    )

    if not user:
        return None

    return (
        db.query(Payment)
        .filter(
            Payment.user_id == user.id,
            Payment.status == "pending",
        )
        .order_by(
            Payment.created_at.desc()
        )
        .first()
    )


def mark_payment_paid(
    db: Session,
    payment_id: int,
    payment_hash: str,
):
    payment = (
        db.query(Payment)
        .filter(
            Payment.id == payment_id
        )
        .first()
    )

    if not payment:
        return None

    setattr(
        payment,
        "status",
        "paid",
    )

    setattr(
        payment,
        "payment_hash",
        payment_hash,
    )

    try:
        _grant_payment_credits_once(
            db,
            payment,
        )

        db.commit()
        db.refresh(payment)

    except SQLAlchemyError as exc:
        db.rollback()

        raise DatabaseServiceError(
            "Failed to finalize payment."
        ) from exc

    return payment


def verify_payment(
    db: Session,
    payment_id: int,
    authenticated_user_id: str | None = None,
    user_id: str | None = None,
):
    payment = (
        db.query(Payment)
        .filter(
            Payment.id == payment_id
        )
        .first()
    )

    if not payment:
        return None

    effective_user_id = (
        authenticated_user_id
        if authenticated_user_id is not None
        else user_id
    )

    # Verify that the authenticated user owns
    # this payment.
    if effective_user_id is not None:
        payment_owner = (
            db.query(User)
            .filter(
                User.id == payment.user_id
            )
            .first()
        )

        if (
            payment_owner is None
            or cast(
                str,
                payment_owner.user_id,
            )
            != effective_user_id
        ):
            return None

    # ---------------------------------------------------------
    # Payment is already confirmed.
    # ---------------------------------------------------------
    if cast(
        str,
        payment.status,
    ) == "paid":

        if cast(
            int,
            payment.credits_granted,
        ) == 0:

            try:
                _grant_payment_credits_once(
                    db,
                    payment,
                )

                db.commit()
                db.refresh(payment)

            except SQLAlchemyError as exc:
                db.rollback()

                raise DatabaseServiceError(
                    "Failed to restore payment credits."
                ) from exc

        return payment

    # ---------------------------------------------------------
    # Payment has expired.
    # ---------------------------------------------------------
    if cast(
        str,
        payment.status,
    ) == "expired":
        return payment

    # ---------------------------------------------------------
    # Payment must contain a payment hash.
    # ---------------------------------------------------------
    if not cast(
        str | None,
        payment.payment_hash,
    ):
        raise RuntimeError(
            "Payment does not contain a payment hash."
        )

    # ---------------------------------------------------------
    # Check Lightning provider.
    # ---------------------------------------------------------
    invoice_status = check_lightning_payment(
        cast(
            str,
            payment.payment_hash,
        )
    )

    paid = getattr(
        invoice_status,
        "paid",
        False,
    )

    invoice_amount = getattr(
        invoice_status,
        "amount",
        None,
    )

    expected_amount = (
        payment.amount_sats * 1000
    )

    # ---------------------------------------------------------
    # Payment has not been completed.
    # ---------------------------------------------------------
    if not paid:

        if _is_payment_expired(
            payment
        ):
            setattr(
                payment,
                "status",
                "expired",
            )
        else:
            setattr(
                payment,
                "status",
                "pending",
            )

        try:
            db.commit()
            db.refresh(payment)

        except SQLAlchemyError as exc:
            db.rollback()

            raise DatabaseServiceError(
                "Failed to update payment status."
            ) from exc

        return payment

    # ---------------------------------------------------------
    # Verify exact Lightning payment amount.
    # ---------------------------------------------------------
    if invoice_amount != expected_amount:

        setattr(
            payment,
            "status",
            "pending",
        )

        try:
            db.commit()
            db.refresh(payment)

        except SQLAlchemyError as exc:
            db.rollback()

            raise DatabaseServiceError(
                "Failed to update payment status."
            ) from exc

        return payment

    # ---------------------------------------------------------
    # Payment is valid and fully paid.
    # ---------------------------------------------------------
    setattr(
        payment,
        "status",
        "paid",
    )

    try:
        _grant_payment_credits_once(
            db,
            payment,
        )

        db.commit()
        db.refresh(payment)

    except SQLAlchemyError as exc:
        db.rollback()

        raise DatabaseServiceError(
            "Failed to finalize payment verification."
        ) from exc

    return payment