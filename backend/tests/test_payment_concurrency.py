from datetime import datetime, timedelta, timezone

from app.models import Account, User
from app.services import payment_service


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

    return user


def test_existing_pending_payment_is_reused(
    db,
    monkeypatch,
):
    user = create_test_user(
        db,
        "concurrency-test-user",
    )

    from app.models import Payment

    existing_payment = Payment(
        user_id=user.id,
        amount_sats=10,
        invoice="existing-concurrency-invoice",
        payment_hash="existing-concurrency-hash",
        status="pending",
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(minutes=30)
        ),
    )

    db.add(existing_payment)
    db.commit()
    db.refresh(existing_payment)

    invoice_calls = []

    def fake_create_invoice(*args, **kwargs):
        invoice_calls.append(True)

        raise AssertionError(
            "A second invoice should not be created."
        )

    monkeypatch.setattr(
        payment_service,
        "create_lightning_invoice",
        fake_create_invoice,
    )

    result = payment_service.create_payment(
        db,
        user.user_id,
    )

    assert result.id == existing_payment.id
    assert result.invoice == "existing-concurrency-invoice"
    assert result.status == "pending"
    assert len(invoice_calls) == 0