import logging
from datetime import datetime, timedelta, timezone
from typing import cast
from sqlalchemy import exc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.middleware.database_errors import DatabaseServiceError
from app.models import Account, Payment, User
from app.schemas import payment
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
    expires_at = cast(datetime | None, payment.expires_at)

    if expires_at is None:
        return False

    # SQLite may return DateTime values without timezone information.
    # Treat those values as UTC.
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    return bool(expires_at <= _utc_now())


def create_payment(db: Session, user_id: str):
    from app.services.metering_service import get_or_create_user

    user = get_or_create_user(db, user_id)

    # Look for the most recent pending payment.
    existing_payment = (
        db.query(Payment)
        .filter(
            Payment.user_id == user.id,
            Payment.status == "pending",
        )
        .order_by(Payment.created_at.desc())
        .first()
    )

    if existing_payment:
        # Reuse the existing invoice if it has not expired.
        if not _is_payment_expired(existing_payment):
            logger.info(
                "Payment request reused | user_id=%s | payment_id=%s",
                user_id,
                existing_payment.id,
            )
            return existing_payment

        # The invoice is too old. Mark it expired before creating
        # a fresh payment request.
        setattr(existing_payment, "status", "expired")
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
        expires_at=now + timedelta(
            minutes=PAYMENT_EXPIRY_MINUTES
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


def get_pending_payment(db: Session, user_id: str):
    from app.models import User

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
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
        .order_by(Payment.created_at.desc())
        .first()
    )


def mark_payment_paid(
    db: Session,
    payment_id: int,
    payment_hash: str,
):
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        return None

    setattr(payment, "status", "paid")
    setattr(payment, "payment_hash", payment_hash)

    account = (
        db.query(Account)
        .filter(Account.user_id == payment.user_id)
        .first()
    )

    if account is not None and cast(int, payment.credits_granted) == 0:
        setattr(
            account,
            "credits",
            cast(int, account.credits) + CREDITS_PER_PAYMENT,
        )
        setattr(payment, "credits_granted", CREDITS_PER_PAYMENT)

    try:
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
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        return None

    effective_user_id = (
        authenticated_user_id
        if authenticated_user_id is not None
        else user_id
    )

    if effective_user_id is not None:
        payment_owner = (
            db.query(User)
            .filter(User.id == payment.user_id)
            .first()
        )

        if payment_owner is None or cast(str, payment_owner.user_id) != effective_user_id:
            return None

    # Payment is already confirmed.
    if cast(str, payment.status) == "paid":
        if cast(int, payment.credits_granted) == 0:
            account = (
                db.query(Account)
                .filter(Account.user_id == payment.user_id)
                .first()
            )

            if account is not None:
                setattr(
                    account,
                    "credits",
                    cast(int, account.credits) + CREDITS_PER_PAYMENT,
                )
                setattr(payment, "credits_granted", CREDITS_PER_PAYMENT)
                try:
                    db.commit()
                    db.refresh(payment)
                except SQLAlchemyError as exc:
                    db.rollback()
                    raise DatabaseServiceError(
                        "Failed to restore payment credits."
                    ) from exc

        return payment

    if cast(str, payment.status) == "expired":
        return payment

    if not cast(str | None, payment.payment_hash):
        raise RuntimeError(
            "Payment does not contain a payment hash."
        )

    invoice_status = check_lightning_payment(
        cast(str, payment.payment_hash)
    )

    paid = getattr(invoice_status, "paid", False)
    invoice_amount = getattr(invoice_status, "amount", None)
    expected_amount = payment.amount_sats * 1000

    if not paid:
        if _is_payment_expired(payment):
            setattr(payment, "status", "expired")
        else:
            setattr(payment, "status", "pending")

        try:
            db.commit()
            db.refresh(payment)
        except SQLAlchemyError as exc:
            db.rollback()
            raise DatabaseServiceError(
                "Failed to update payment status."
            ) from exc

        return payment

    # A Lightning payment is only valid when the
    # amount paid exactly matches the invoice amount.
    if invoice_amount != expected_amount:
        setattr(payment, "status", "pending")

        try:
            db.commit()
            db.refresh(payment)
        except SQLAlchemyError as exc:
            db.rollback()
            raise DatabaseServiceError(
                "Failed to update payment status."
            ) from exc

        return payment

    setattr(payment, "status", "paid")

    account = (
        db.query(Account)
        .filter(Account.user_id == payment.user_id)
        .first()
    )

    if account is not None and cast(int, payment.credits_granted) == 0:
        setattr(
            account,
            "credits",
            cast(int, account.credits) + CREDITS_PER_PAYMENT,
        )
        setattr(
            payment,
            "credits_granted",
            CREDITS_PER_PAYMENT,
        )

    try:
        db.commit()
        db.refresh(payment)
    except SQLAlchemyError as exc:
        db.rollback()
        raise DatabaseServiceError(
            "Failed to finalize payment verification."
        ) from exc

    return payment