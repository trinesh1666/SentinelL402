import pytest

from app.models import Account, Payment, User
from app.services.payment_service import verify_payment


def test_payment_verification_grants_credits_once(db):
    user = User(
        user_id="pytest-payment-transaction-user",
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
        payment_hash="pytest-transaction-payment-hash",
        status="paid",
        credits_granted=0,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    payment_id = payment.id

    result = verify_payment(
        db,
        payment_id,
    )

    db.refresh(account)
    db.refresh(payment)

    assert result.status == "paid"
    assert payment.status == "paid"
    assert payment.credits_granted == 5
    assert account.credits == 5

    # Verify the same payment again.
    result_again = verify_payment(
        db,
        payment_id,
    )

    db.refresh(account)
    db.refresh(payment)

    assert result_again.status == "paid"
    assert payment.credits_granted == 5
    assert account.credits == 5

    print()
    print("PAYMENT TRANSACTION TEST")
    print("------------------------")
    print("Payment ID:", payment_id)
    print("Payment status:", payment.status)
    print("Credits granted:", payment.credits_granted)
    print("Account credits:", account.credits)
    print("Repeated verification did not duplicate credits.")