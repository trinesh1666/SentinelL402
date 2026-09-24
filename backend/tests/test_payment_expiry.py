from datetime import datetime, timedelta, timezone
from typing import cast

from app.models import Account, Payment, User
from app.services import payment_service


def create_test_user(db, user_id="expiry-test-user"):
    user = User(user_id=user_id)
    db.add(user)
    db.commit()
    db.refresh(user)

    account = Account(
        user_id=user.id,
        credits=0,
        total_requests=0,
    )
    db.add(account)
    db.commit()

    return user


def test_unexpired_pending_payment_is_reused(db, monkeypatch):
    user = create_test_user(
        db,
        "expiry-reuse-user",
    )

    payment = Payment(
        user_id=user.id,
        amount_sats=10,
        invoice="existing-invoice",
        payment_hash="existing-hash",
        status="pending",
        expires_at=datetime.now(timezone.utc)
        + timedelta(minutes=30),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    def fail_if_new_invoice_is_created(*args, **kwargs):
        raise AssertionError(
            "A new invoice should not be created "
            "for an unexpired pending payment."
        )

    monkeypatch.setattr(
        payment_service,
        "create_lightning_invoice",
        fail_if_new_invoice_is_created,
    )

    result = payment_service.create_payment(
        db,
        cast(str, user.user_id),
    )

    assert cast(int, result.id) == cast(int, payment.id)
    assert cast(str, result.status) == "pending"
    assert cast(str, result.invoice) == "existing-invoice"


def test_expired_pending_payment_creates_new_payment(
    db,
    monkeypatch,
):
    user = create_test_user(
        db,
        "expiry-new-payment-user",
    )

    old_payment = Payment(
        user_id=user.id,
        amount_sats=10,
        invoice="expired-invoice",
        payment_hash="expired-hash",
        status="pending",
        expires_at=datetime.now(timezone.utc)
        - timedelta(minutes=1),
    )

    db.add(old_payment)
    db.commit()
    db.refresh(old_payment)

    class FakeInvoice:
        invoice = "new-invoice"
        payment_hash = "new-hash"

    monkeypatch.setattr(
        payment_service,
        "create_lightning_invoice",
        lambda *args, **kwargs: FakeInvoice(),
    )

    result = payment_service.create_payment(
        db,
        cast(str, user.user_id),
    )

    db.refresh(old_payment)

    assert cast(str, old_payment.status) == "expired"

    assert cast(int, result.id) != cast(int, old_payment.id)
    assert cast(str, result.status) == "pending"
    assert cast(str, result.invoice) == "new-invoice"
    assert cast(str, result.payment_hash) == "new-hash"
    assert result.expires_at is not None

    expires_at = cast(datetime, result.expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    assert expires_at > datetime.now(timezone.utc)


def test_paid_payment_is_not_expired(db):
    user = create_test_user(
        db,
        "expiry-paid-user",
    )

    payment = Payment(
        user_id=user.id,
        amount_sats=10,
        invoice="paid-invoice",
        payment_hash="paid-hash",
        status="paid",
        credits_granted=5,
        expires_at=datetime.now(timezone.utc)
        - timedelta(minutes=1),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    payment_id = cast(int, payment.id)

    result = payment_service.verify_payment(
        db,
        payment_id,
        cast(str, user.user_id),
    )

    assert result is not None
    assert cast(str, result.status) == "paid"
    assert cast(int, result.credits_granted) == 5