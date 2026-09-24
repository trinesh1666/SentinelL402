import uuid
from datetime import datetime, timedelta, timezone
from typing import cast

from app.models import Account, Payment, User
from app.services.payment_service import verify_payment


def test_pending_payment_does_not_grant_credits(
    db,
    monkeypatch,
):
    user = User(
        user_id=f"pending-payment-{uuid.uuid4()}"
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

    payment = Payment(
        user_id=user.id,
        amount_sats=10,
        payment_hash=f"hash-{uuid.uuid4()}",
        invoice=f"invoice-{uuid.uuid4()}",
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

    class FakeInvoiceStatus:
        paid = False
        amount = 10_000

    monkeypatch.setattr(
        "app.services.payment_service.check_lightning_payment",
        lambda payment_hash: FakeInvoiceStatus(),
    )

    payment_id = cast(int, payment.id)
    result = verify_payment(
        db,
        payment_id,
        cast(str, user.user_id),
    )

    assert result is not None
    assert cast(str, result.status) == "pending"
    assert cast(int, result.credits_granted) == 0
    assert cast(int, account.credits) == 0