from app.models import Account, Payment, User
from app.services.payment_service import verify_payment


def test_paid_payment_does_not_grant_credits_twice(db):
    user_id = "pytest-idempotency-user"

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not user:
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
    else:
        account = (
            db.query(Account)
            .filter(Account.user_id == user.id)
            .first()
        )

        if not account:
            account = Account(
                user_id=user.id,
                credits=0,
                total_requests=0,
            )
            db.add(account)
            db.commit()
            db.refresh(account)

        account.credits = 0
        db.commit()

    payment = Payment(
        user_id=user.id,
        amount_sats=10,
        payment_hash="pytest-idempotency-hash",
        status="paid",
        credits_granted=0,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    payment_id = payment.id

    # First verification should grant credits.
    first_result = verify_payment(
        db,
        payment_id,
    )

    db.refresh(account)

    first_credits = account.credits

    assert first_result.status == "paid"
    assert first_result.credits_granted == 5
    assert first_credits == 5

    # Second verification must NOT grant another 5 credits.
    second_result = verify_payment(
        db,
        payment_id,
    )

    db.refresh(account)

    second_credits = account.credits

    assert second_result.status == "paid"
    assert second_result.credits_granted == 5
    assert second_credits == 5

    print()
    print("PAYMENT IDEMPOTENCY TEST")
    print("------------------------")
    print("Payment ID:", payment_id)
    print(
        "Credits after first verification:",
        first_credits,
    )
    print(
        "Credits after second verification:",
        second_credits,
    )
    print("Credits were granted only once.")