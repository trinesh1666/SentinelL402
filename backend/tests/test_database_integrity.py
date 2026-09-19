import pytest
from sqlalchemy.exc import IntegrityError

from app.models import (
    Account,
    Payment,
    User,
)


def test_user_can_have_only_one_account(db):
    user = User(
        user_id="pytest-one-account-user",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    first_account = Account(
        user_id=user.id,
        credits=5,
        total_requests=0,
    )

    db.add(first_account)
    db.commit()

    second_account = Account(
        user_id=user.id,
        credits=5,
        total_requests=0,
    )

    db.add(second_account)

    with pytest.raises(IntegrityError):
        with db.begin_nested():
            db.flush()

    db.rollback()


def test_payment_hash_must_be_unique(db):
    user = User(
        user_id="pytest-payment-hash-user",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    first_payment = Payment(
        user_id=user.id,
        amount_sats=10,
        payment_hash="duplicate-payment-hash",
        status="pending",
        credits_granted=0,
    )

    db.add(first_payment)
    db.commit()

    second_payment = Payment(
        user_id=user.id,
        amount_sats=10,
        payment_hash="duplicate-payment-hash",
        status="pending",
        credits_granted=0,
    )

    db.add(second_payment)

    with pytest.raises(IntegrityError):
        with db.begin_nested():
            db.flush()

    db.rollback()


def test_payment_invoice_must_be_unique(db):
    user = User(
        user_id="pytest-payment-invoice-user",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    first_payment = Payment(
        user_id=user.id,
        amount_sats=10,
        invoice="duplicate-invoice",
        payment_hash="invoice-test-hash-1",
        status="pending",
        credits_granted=0,
    )

    db.add(first_payment)
    db.commit()

    second_payment = Payment(
        user_id=user.id,
        amount_sats=10,
        invoice="duplicate-invoice",
        payment_hash="invoice-test-hash-2",
        status="pending",
        credits_granted=0,
    )

    db.add(second_payment)

    with pytest.raises(IntegrityError):
        with db.begin_nested():
            db.flush()

    db.rollback()

def test_payment_invoice_cannot_be_duplicated(db):
    from sqlalchemy.exc import IntegrityError

    from app.models import Payment, User

    user = User(
        user_id="duplicate-invoice-test-user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    payment_one = Payment(
        user_id=user.id,
        amount_sats=10,
        invoice="same-invoice",
        payment_hash="hash-one",
        status="pending",
    )

    db.add(payment_one)
    db.commit()

    payment_two = Payment(
        user_id=user.id,
        amount_sats=10,
        invoice="same-invoice",
        payment_hash="hash-two",
        status="pending",
    )

    db.add(payment_two)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
    else:
        raise AssertionError(
            "Duplicate payment invoice was allowed."
        )