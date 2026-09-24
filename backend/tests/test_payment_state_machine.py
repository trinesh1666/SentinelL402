import uuid
from datetime import datetime, timedelta, timezone
from typing import cast

from app.models import Account, Payment, User
from app.services.payment_service import verify_payment


def create_test_user(db):
    user = User(
        user_id=f"state-machine-{uuid.uuid4()}"
    )

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
    db.refresh(account)

    return user, account


def test_pending_payment_can_become_paid(
    db,
    monkeypatch,
):
    user, account = create_test_user(db)

    payment = Payment(
        user_id=user.id,
        amount_sats=10,
        invoice=f"invoice-{uuid.uuid4()}",
        payment_hash=f"hash-{uuid.uuid4()}",
        status="pending",
        credits_granted=0,
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(minutes=30)
        ),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    class FakePaymentStatus:
        paid = True
        amount = 10_000

    monkeypatch.setattr(
        "app.services.payment_service.check_lightning_payment",
        lambda payment_hash: FakePaymentStatus(),
    )

    payment_id = cast(int, payment.id)
    result = verify_payment(
        db,
        payment_id,
        cast(str, user.user_id),
    )

    assert result is not None
    assert cast(str, result.status) == "paid"
    assert cast(int, result.credits_granted) == 5
    assert cast(int, account.credits) == 5


def test_pending_payment_can_become_expired(
    db,
    monkeypatch,
):
    user, account = create_test_user(db)

    payment = Payment(
        user_id=user.id,
        amount_sats=10,
        invoice=f"invoice-{uuid.uuid4()}",
        payment_hash=f"hash-{uuid.uuid4()}",
        status="pending",
        credits_granted=0,
        expires_at=(
            datetime.now(timezone.utc)
            - timedelta(minutes=1)
        ),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    class FakePaymentStatus:
        paid = False
        amount = 0

    monkeypatch.setattr(
        "app.services.payment_service.check_lightning_payment",
        lambda payment_hash: FakePaymentStatus(),
    )

    payment_id = cast(int, payment.id)
    result = verify_payment(
        db,
        payment_id,
        cast(str, user.user_id),
    )

    assert result is not None
    assert cast(str, result.status) == "expired"
    assert cast(int, result.credits_granted) == 0
    assert cast(int, account.credits) == 0


def test_expired_payment_does_not_become_paid(
    db,
    monkeypatch,
):
    user, account = create_test_user(db)

    payment = Payment(
        user_id=user.id,
        amount_sats=10,
        invoice=f"invoice-{uuid.uuid4()}",
        payment_hash=f"hash-{uuid.uuid4()}",
        status="expired",
        credits_granted=0,
        expires_at=(
            datetime.now(timezone.utc)
            - timedelta(minutes=1)
        ),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    class FakePaymentStatus:
        paid = True
        amount = 10_000

    monkeypatch.setattr(
        "app.services.payment_service.check_lightning_payment",
        lambda payment_hash: FakePaymentStatus(),
    )

    payment_id = cast(int, payment.id)
    result = verify_payment(
        db,
        payment_id,
        cast(str, user.user_id),
    )

    assert result is not None
    assert cast(str, result.status) == "expired"
    assert cast(int, result.credits_granted) == 0
    assert cast(int, account.credits) == 0


def test_paid_payment_remains_paid(
    db,
    monkeypatch,
):
    user, account = create_test_user(db)

    payment = Payment(
        user_id=user.id,
        amount_sats=10,
        invoice=f"invoice-{uuid.uuid4()}",
        payment_hash=f"hash-{uuid.uuid4()}",
        status="paid",
        credits_granted=5,
    )

    setattr(account, "credits", 5)
    db.add(payment)
    db.commit()
    db.refresh(payment)

    def fail_if_lightning_is_checked(*args, **kwargs):
        raise AssertionError(
            "A completed payment should not query "
            "Lightning again."
        )

    monkeypatch.setattr(
        "app.services.payment_service.check_lightning_payment",
        fail_if_lightning_is_checked,
    )

    payment_id = cast(int, payment.id)
    result = verify_payment(
        db,
        payment_id,
        cast(str, user.user_id),
    )

    assert result is not None
    assert cast(str, result.status) == "paid"
    assert cast(int, result.credits_granted) == 5
    assert cast(int, account.credits) == 5