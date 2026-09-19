from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import Account, Payment
from app.services.lightning_service import (
    PAYMENT_AMOUNT_SATS,
    check_lightning_payment,
    create_lightning_invoice,
)

CREDITS_PER_PAYMENT = 5
PAYMENT_EXPIRY_MINUTES = 60


def _utc_now():
    return datetime.now(timezone.utc)


def _is_payment_expired(payment: Payment) -> bool:
    if payment.expires_at is None:
        return False

    expires_at = payment.expires_at

    # SQLite may return DateTime values without timezone information.
    # Treat those values as UTC.
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    return expires_at <= _utc_now()


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
            return existing_payment

        # The invoice is too old. Mark it expired before creating
        # a fresh payment request.
        existing_payment.status = "expired"
        db.commit()

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
    db.commit()
    db.refresh(payment)

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

    payment.status = "paid"
    payment.payment_hash = payment_hash

    account = (
        db.query(Account)
        .filter(Account.user_id == payment.user_id)
        .first()
    )

    if account and payment.credits_granted == 0:
        account.credits += CREDITS_PER_PAYMENT
        payment.credits_granted = CREDITS_PER_PAYMENT

    db.commit()
    db.refresh(payment)

    return payment


def verify_payment(db: Session, payment_id: int):
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        return None

    # Payment is already confirmed.
    # Only grant credits if they have not been granted yet.
    if payment.status == "paid":
        if payment.credits_granted == 0:
            account = (
                db.query(Account)
                .filter(
                    Account.user_id == payment.user_id
                )
                .first()
            )

            if account:
                account.credits += CREDITS_PER_PAYMENT
                payment.credits_granted = CREDITS_PER_PAYMENT

                db.commit()
                db.refresh(payment)

        return payment

    if payment.status == "expired":
        return payment

    if not payment.payment_hash:
        raise RuntimeError(
            "Payment does not contain a payment hash."
        )

    invoice_status = check_lightning_payment(
        payment.payment_hash
    )

    paid = getattr(
        invoice_status,
        "paid",
        False,
    )

    if not paid:
        # Only expire it when its local expiry time has passed.
        if _is_payment_expired(payment):
            payment.status = "expired"
        else:
            payment.status = "pending"

        db.commit()
        db.refresh(payment)

        return payment

    # Lightning payment confirmed.
    payment.status = "paid"

    account = (
        db.query(Account)
        .filter(Account.user_id == payment.user_id)
        .first()
    )

    if account and payment.credits_granted == 0:
        account.credits += CREDITS_PER_PAYMENT
        payment.credits_granted = CREDITS_PER_PAYMENT

    db.commit()
    db.refresh(payment)

    return payment