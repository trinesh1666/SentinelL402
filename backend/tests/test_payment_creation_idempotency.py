from unittest.mock import patch

from app.models import Payment, User
from app.services.payment_service import create_payment


def test_create_payment_reuses_existing_pending_payment(db):
    user_id = "pytest-payment-creation-idempotency"

    user = User(user_id=user_id)
    db.add(user)
    db.commit()
    db.refresh(user)

    existing_payment = Payment(
        user_id=user.id,
        amount_sats=10,
        invoice="existing-test-invoice",
        payment_hash="existing-test-payment-hash",
        status="pending",
        credits_granted=0,
    )

    db.add(existing_payment)
    db.commit()
    db.refresh(existing_payment)

    existing_payment_id = existing_payment.id

    with patch(
        "app.services.payment_service.create_lightning_invoice"
    ) as mock_create_invoice:

        result = create_payment(
            db,
            user_id,
        )

        mock_create_invoice.assert_not_called()

    assert result.id == existing_payment_id
    assert result.invoice == "existing-test-invoice"
    assert result.payment_hash == "existing-test-payment-hash"
    assert result.status == "pending"

    payment_count = (
        db.query(Payment)
        .filter(Payment.user_id == user.id)
        .count()
    )

    assert payment_count == 1

    print()
    print("PAYMENT CREATION IDEMPOTENCY TEST")
    print("--------------------------------")
    print("Existing payment ID:", existing_payment_id)
    print("Returned payment ID:", result.id)
    print("Lightning invoice was NOT recreated.")
    print("Only one pending payment exists.")