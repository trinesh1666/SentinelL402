import uuid
from typing import cast
from unittest.mock import patch

from app.models import Account, Payment
from app.services.metering_service import get_or_create_user
from app.services.payment_service import verify_payment


def test_payment_verification_grants_credits_once(db):
    user_id = f"pytest-payment-{uuid.uuid4()}"

    user = get_or_create_user(
        db,
        user_id,
    )

    account = (
        db.query(Account)
        .filter(
            Account.user_id == user.id
        )
        .first()
    )

    # Start with zero credits.
    account.credits = 0
    db.commit()

    payment = Payment(
        user_id=user.id,
        amount_sats=10,
        invoice="lnbc-test-verification",
        payment_hash="test-payment-hash",
        status="pending",
        credits_granted=0,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    # Fake Lightning response:
    # pretend the invoice has actually been paid.
    class FakePaymentStatus:
        paid = True
        amount = 10_000

    payment_id = cast(int, payment.id)

    with patch(
        "app.services.payment_service.check_lightning_payment",
        return_value=FakePaymentStatus(),
    ):
        verified_payment = verify_payment(
            db,
            payment_id,
            user_id,
        )

    assert verified_payment is not None
    assert cast(str, verified_payment.status) == "paid"
    assert cast(int, verified_payment.credits_granted) == 5

    db.refresh(account)

    assert account.credits == 5

    # Verify the same payment again.
    verified_payment_again = verify_payment(
        db,
        payment_id,
    )

    assert verified_payment_again is not None

    db.refresh(account)

    # Credits must NOT increase again.
    assert cast(str, verified_payment_again.status) == "paid"
    assert cast(int, verified_payment_again.credits_granted) == 5
    assert account.credits == 5
