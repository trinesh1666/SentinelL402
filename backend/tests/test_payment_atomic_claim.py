import uuid

from app import models
from app.services.metering_service import get_or_create_user
from app.services.payment_service import (
    CREDITS_PER_PAYMENT,
    _grant_payment_credits_once,
)


def test_atomic_payment_credit_claim_grants_only_once(db):
    user_id = (
        f"pytest-atomic-payment-{uuid.uuid4()}"
    )

    user = get_or_create_user(
        db,
        user_id,
    )

    account = (
        db.query(models.Account)
        .filter(
            models.Account.user_id == user.id
        )
        .first()
    )

    assert account is not None

    account.credits = 0
    db.commit()

    payment = models.Payment(
        user_id=user.id,
        amount_sats=10,
        invoice=f"lnmock_{uuid.uuid4().hex}",
        payment_hash=f"mock_hash_{uuid.uuid4().hex}",
        status="paid",
        credits_granted=0,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    first_claim = _grant_payment_credits_once(
        db,
        payment,
    )

    assert first_claim is True

    db.commit()
    db.refresh(payment)
    db.refresh(account)

    assert payment.credits_granted == CREDITS_PER_PAYMENT
    assert account.credits == CREDITS_PER_PAYMENT

    second_claim = _grant_payment_credits_once(
        db,
        payment,
    )

    assert second_claim is False

    db.commit()
    db.refresh(payment)
    db.refresh(account)

    assert payment.credits_granted == CREDITS_PER_PAYMENT
    assert account.credits == CREDITS_PER_PAYMENT