import uuid
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

    with patch(
        "app.services.payment_service.check_lightning_payment",
        return_value=FakePaymentStatus(),
    ):
        verified_payment = verify_payment(
            db,
            payment.id,
        )

    assert verified_payment is not None
    assert verified_payment.status == "paid"
    assert verified_payment.credits_granted == 5

    db.refresh(account)

    assert account.credits == 5

    # Verify the same payment again.
    verified_payment_again = verify_payment(
        db,
        payment.id,
    )


    db.refresh(account)

    # Credits must NOT increase again.
    assert verified_payment_again.status == "paid"
    assert verified_payment_again.credits_granted == 5
    assert account.credits == 5
