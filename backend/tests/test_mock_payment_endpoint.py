import uuid

from app import models
from app.config import LIGHTNING_PROVIDER
from app.main import app
from app.services.api_key_service import create_api_key
from app.services.metering_service import get_or_create_user
from app.services.mock_lightning_service import create_mock_invoice


def test_mock_payment_complete_requires_existing_mock_payment(
    db,
    client,
):
    user_id = f"pytest-mock-payment-{uuid.uuid4()}"

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

    api_key, _ = create_api_key(
        db=db,
        user_id=user_id,
        name="pytest-mock-payment-key",
    )

    headers = {
        "X-API-Key": api_key,
    }

    response = client.post(
        "/api/payment/mock/complete/999999",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found."


def test_mock_payment_complete_marks_payment_paid(
    db,
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.main.LIGHTNING_PROVIDER",
        "mock",
    )

    user_id = f"pytest-mock-payment-{uuid.uuid4()}"

    user = get_or_create_user(
        db,
        user_id,
    )

    api_key, _ = create_api_key(
        db=db,
        user_id=user_id,
        name="pytest-mock-payment-key",
    )

    headers = {
        "X-API-Key": api_key,
    }

    mock_invoice = create_mock_invoice(
        10,
        "pytest mock payment",
    )

    payment = models.Payment(
        user_id=user.id,
        amount_sats=10,
        invoice=mock_invoice.invoice,
        payment_hash=mock_invoice.payment_hash,
        status="pending",
        credits_granted=0,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    response = client.post(
        f"/api/payment/mock/complete/{payment.id}",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["payment_id"] == payment.id
    assert data["user_id"] == user_id
    assert data["status"] == "paid"
    assert data["mock_payment"] is True
    assert data["amount_sats"] == 10


def test_mock_payment_complete_rejects_wrong_user(
    db,
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.main.LIGHTNING_PROVIDER",
        "mock",
    )

    owner_user_id = f"pytest-payment-owner-{uuid.uuid4()}"
    other_user_id = f"pytest-payment-other-{uuid.uuid4()}"

    owner = get_or_create_user(
        db,
        owner_user_id,
    )

    other_user = get_or_create_user(
        db,
        other_user_id,
    )

    owner_api_key, _ = create_api_key(
        db=db,
        user_id=owner_user_id,
        name="owner-key",
    )

    other_api_key, _ = create_api_key(
        db=db,
        user_id=other_user_id,
        name="other-key",
    )

    mock_invoice = create_mock_invoice(
        10,
        "pytest ownership test",
    )

    payment = models.Payment(
        user_id=owner.id,
        amount_sats=10,
        invoice=mock_invoice.invoice,
        payment_hash=mock_invoice.payment_hash,
        status="pending",
        credits_granted=0,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    response = client.post(
        f"/api/payment/mock/complete/{payment.id}",
        headers={
            "X-API-Key": other_api_key,
        },
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "You are not authorized to complete this payment."
    )


def test_mock_payment_endpoint_disabled_for_nwc(
    db,
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.main.LIGHTNING_PROVIDER",
        "nwc",
    )

    user_id = f"pytest-nwc-mock-endpoint-{uuid.uuid4()}"

    get_or_create_user(
        db,
        user_id,
    )

    api_key, _ = create_api_key(
        db=db,
        user_id=user_id,
        name="pytest-nwc-key",
    )

    response = client.post(
        "/api/payment/mock/complete/1",
        headers={
            "X-API-Key": api_key,
        },
    )

    assert response.status_code == 404
    assert (
        response.json()["detail"]
        == "Mock payment endpoint is disabled."
    )