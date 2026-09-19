from datetime import datetime, timedelta, timezone

from app.models import Payment
from app.services.payment_service import verify_payment


def test_pending_payment_does_not_grant_credits(db, monkeypatch):
    payment = Payment(
        user_id=1,
        amount_sats=10,
        payment_hash="test-pending-hash",
        invoice="test-pending-invoice",
        status="pending",
        credits_granted=0,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    class FakeInvoiceStatus:
        paid = False

    monkeypatch.setattr(
        "app.services.payment_service.check_lightning_payment",
        lambda payment_hash: FakeInvoiceStatus(),
    )

    result = verify_payment(db, payment.id)

    assert result.status == "pending"
    assert result.credits_granted == 0