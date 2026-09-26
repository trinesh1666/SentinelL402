import uuid
from unittest.mock import patch

from app import models
from app.services.api_key_service import create_api_key
from app.services.metering_service import get_or_create_user
from app.services.payment_service import verify_payment


def test_verify_paid_payment_does_not_grant_credits_twice(
    db,
):
    user_id = f"pytest-payment-idempotency-{uuid.uuid4()}"

    user = get_or_create_user(
        db,
        user_id,
    )

    account = (
        db.query(models.Account)
        .filter(
            models.Account.user_id == user.id
        )
        .first()
    )

    assert account is not None

    account.credits = 0
    db.commit()

    payment = models.Payment(
        user_id=user.id,
        amount_sats=10,
        invoice=f"lnmock_{uuid.uuid4().hex}",
        payment_hash=f"mock_hash_{uuid.uuid4().hex}",
        status="pending",
        credits_granted=0,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    class FakePaymentStatus:
        paid = True
        amount = 10_000

    with patch(
        "app.services.payment_service.check_lightning_payment",
        return_value=FakePaymentStatus(),
    ) as mock_check:

        first_result = verify_payment(
            db,
            payment.id,
            authenticated_user_id=user_id,
        )

        assert first_result is not None
        assert first_result.status == "paid"
        assert first_result.credits_granted == 5

        db.refresh(account)

        assert account.credits == 5

        second_result = verify_payment(
            db,
            payment.id,
            authenticated_user_id=user_id,
        )

        assert second_result is not None
        assert second_result.status == "paid"
        assert second_result.credits_granted == 5

        db.refresh(account)

        assert account.credits == 5

        assert mock_check.call_count == 1


def test_verify_payment_cannot_be_used_by_another_user(
    db,
):
    owner_user_id = (
        f"pytest-payment-owner-{uuid.uuid4()}"
    )

    other_user_id = (
        f"pytest-payment-other-{uuid.uuid4()}"
    )

    owner = get_or_create_user(
        db,
        owner_user_id,
    )

    get_or_create_user(
        db,
        other_user_id,
    )

    payment = models.Payment(
        user_id=owner.id,
        amount_sats=10,
        invoice=f"lnmock_{uuid.uuid4().hex}",
        payment_hash=f"mock_hash_{uuid.uuid4().hex}",
        status="pending",
        credits_granted=0,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    result = verify_payment(
        db,
        payment.id,
        authenticated_user_id=other_user_id,
    )

    assert result is None


def test_already_paid_payment_with_granted_credits_is_idempotent(
    db,
):
    user_id = (
        f"pytest-payment-already-paid-{uuid.uuid4()}"
    )

    user = get_or_create_user(
        db,
        user_id,
    )

    account = (
        db.query(models.Account)
        .filter(
            models.Account.user_id == user.id
        )
        .first()
    )

    assert account is not None

    account.credits = 5
    db.commit()

    payment = models.Payment(
        user_id=user.id,
        amount_sats=10,
        invoice=f"lnmock_{uuid.uuid4().hex}",
        payment_hash=f"mock_hash_{uuid.uuid4().hex}",
        status="paid",
        credits_granted=5,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    result = verify_payment(
        db,
        payment.id,
        authenticated_user_id=user_id,
    )

    assert result is not None
    assert result.status == "paid"
    assert result.credits_granted == 5

    db.refresh(account)

    assert account.credits == 5