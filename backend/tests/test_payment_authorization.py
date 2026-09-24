import uuid
from typing import cast

from app.models import Account, Payment, User
from app.services.payment_service import verify_payment


def create_test_user(db, user_id):
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
    db.refresh(account)

    return user


def test_user_cannot_verify_another_users_payment(db):
    owner = create_test_user(
        db,
        f"payment-owner-{uuid.uuid4()}",
    )

    attacker = create_test_user(
        db,
        f"payment-attacker-{uuid.uuid4()}",
    )

    payment = Payment(
        user_id=owner.id,
        amount_sats=10,
        invoice=f"invoice-{uuid.uuid4()}",
        payment_hash=f"hash-{uuid.uuid4()}",
        status="pending",
        credits_granted=0,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    payment_id = cast(int, payment.id)

    result = verify_payment(
        db,
        payment_id,
        cast(str, attacker.user_id),
    )

    assert result is None

    db.refresh(payment)

    assert cast(str, payment.status) == "pending"
    assert cast(int, payment.credits_granted) == 0


def test_payment_owner_can_verify_own_payment(
    db,
    monkeypatch,
):
    owner = create_test_user(
        db,
        f"payment-owner-{uuid.uuid4()}",
    )

    payment = Payment(
        user_id=owner.id,
        amount_sats=10,
        invoice=f"invoice-{uuid.uuid4()}",
        payment_hash=f"hash-{uuid.uuid4()}",
        status="pending",
        credits_granted=0,
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
        cast(str, owner.user_id),
    )

    assert result is not None
    assert cast(str, result.status) == "paid"
    assert cast(int, result.credits_granted) == 5


def test_wrong_lightning_amount_does_not_grant_credits(
    db,
    monkeypatch,
):
    owner = create_test_user(
        db,
        f"payment-owner-{uuid.uuid4()}",
    )

    payment = Payment(
        user_id=owner.id,
        amount_sats=10,
        invoice=f"invoice-{uuid.uuid4()}",
        payment_hash=f"hash-{uuid.uuid4()}",
        status="pending",
        credits_granted=0,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    class FakePaymentStatus:
        paid = True
        amount = 9_000

    monkeypatch.setattr(
        "app.services.payment_service.check_lightning_payment",
        lambda payment_hash: FakePaymentStatus(),
    )

    payment_id = cast(int, payment.id)

    result = verify_payment(
        db,
        payment_id,
        cast(str, owner.user_id),
    )

    assert result is not None
    assert cast(str, result.status) == "pending"
    assert cast(int, result.credits_granted) == 0

    account = (
        db.query(Account)
        .filter(
            Account.user_id == owner.id
        )
        .first()
    )

    assert account.credits == 0