import uuid

from app.main import app
from app.models import Account, Payment, User
from app.services.auth_service import get_authenticated_user
from app.services.payment_service import mark_payment_paid


FEATURES = {
    "Destination_Port": 80.0,
    "Flow_Duration": 1000000.0,
    "Total_Fwd_Packets": 10.0,
    "Total_Backward_Packets": 8.0,
    "Total_Length_of_Fwd_Packets": 5000.0,
    "Total_Length_of_Bwd_Packets": 4000.0,
    "Fwd_Packet_Length_Max": 1000.0,
    "Fwd_Packet_Length_Min": 100.0,
    "Fwd_Packet_Length_Mean": 500.0,
    "Fwd_Packet_Length_Std": 100.0,
    "Bwd_Packet_Length_Max": 1000.0,
    "Bwd_Packet_Length_Min": 100.0,
    "Bwd_Packet_Length_Mean": 500.0,
    "Bwd_Packet_Length_Std": 100.0,
    "Flow_Bytes/s": 9000.0,
    "Flow_Packets/s": 18.0,
    "Flow_IAT_Mean": 50000.0,
    "Flow_IAT_Std": 10000.0,
    "Flow_IAT_Max": 100000.0,
    "Flow_IAT_Min": 1000.0,
    "Fwd_IAT_Total": 500000.0,
    "Fwd_IAT_Mean": 50000.0,
    "Fwd_IAT_Std": 10000.0,
    "Fwd_IAT_Max": 100000.0,
    "Fwd_IAT_Min": 1000.0,
    "Bwd_IAT_Total": 400000.0,
    "Bwd_IAT_Mean": 50000.0,
    "Bwd_IAT_Std": 10000.0,
    "Bwd_IAT_Max": 100000.0,
    "Bwd_IAT_Min": 1000.0,
    "Fwd_PSH_Flags": 0.0,
    "Bwd_PSH_Flags": 0.0,
    "Fwd_URG_Flags": 0.0,
    "Bwd_URG_Flags": 0.0,
    "Fwd_Header_Length": 200.0,
    "Bwd_Header_Length": 160.0,
    "Fwd_Packets/s": 10.0,
    "Bwd_Packets/s": 8.0,
    "Min_Packet_Length": 100.0,
    "Max_Packet_Length": 1000.0,
    "Packet_Length_Mean": 500.0,
    "Packet_Length_Std": 100.0,
    "Packet_Length_Variance": 10000.0,
    "FIN_Flag_Count": 0.0,
    "SYN_Flag_Count": 1.0,
    "RST_Flag_Count": 0.0,
    "PSH_Flag_Count": 0.0,
    "ACK_Flag_Count": 1.0,
    "URG_Flag_Count": 0.0,
    "CWE_Flag_Count": 0.0,
    "ECE_Flag_Count": 0.0,
    "Down/Up_Ratio": 0.8,
    "Average_Packet_Size": 500.0,
    "Avg_Fwd_Segment_Size": 500.0,
    "Avg_Bwd_Segment_Size": 500.0,
    "Fwd_Header_Length.1": 200.0,
    "Fwd_Avg_Bytes/Bulk": 0.0,
    "Fwd_Avg_Packets/Bulk": 0.0,
    "Fwd_Avg_Bulk_Rate": 0.0,
    "Bwd_Avg_Bytes/Bulk": 0.0,
    "Bwd_Avg_Packets/Bulk": 0.0,
    "Bwd_Avg_Bulk_Rate": 0.0,
    "Subflow_Fwd_Packets": 10.0,
    "Subflow_Fwd_Bytes": 5000.0,
    "Subflow_Bwd_Packets": 8.0,
    "Subflow_Bwd_Bytes": 4000.0,
    "Init_Win_bytes_forward": 65535.0,
    "Init_Win_bytes_backward": 65535.0,
    "act_data_pkt_fwd": 10.0,
    "min_seg_size_forward": 20.0,
    "Active_Mean": 10000.0,
    "Active_Std": 1000.0,
    "Active_Max": 20000.0,
    "Active_Min": 1000.0,
    "Idle_Mean": 50000.0,
    "Idle_Std": 5000.0,
    "Idle_Max": 60000.0,
    "Idle_Min": 40000.0,
}


def fake_create_payment(db, user_id):
    user = (
        db.query(User)
        .filter(
            User.user_id == user_id
        )
        .first()
    )

    payment = Payment(
        user_id=user.id,
        amount_sats=10,
        invoice="lnbc10u1pytestfakeinvoice",
        payment_hash="pytest-fake-payment-hash",
        status="pending",
        credits_granted=0,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


def test_402_payment_retry_flow(
    db,
    client,
    monkeypatch,
):
    user_id = f"pytest-402-retry-{uuid.uuid4()}"

    user = User(
        user_id=user_id,
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

    monkeypatch.setattr(
        "app.services.metered_security_service.create_payment",
        fake_create_payment,
    )

    app.dependency_overrides[
        get_authenticated_user
    ] = lambda: user_id

    try:
        payload = {
            "source": user_id,
            "event_type": "network_flow",
            "severity": "high",
            "description": "Testing HTTP 402 payment retry flow",
            "features": FEATURES,
        }

        # ---------------------------------------------------------
        # 1. Credits exhausted → HTTP 402
        # ---------------------------------------------------------

        response = client.post(
            "/api/security/analyze",
            json=payload,
        )

        assert response.status_code == 402

        payment_data = response.json()["detail"]

        assert payment_data["error"] == "payment_required"
        assert payment_data["payment_method"] == "lightning"
        assert payment_data["amount_sats"] == 10
        assert payment_data["payment_id"] is not None
        assert payment_data["invoice"] is not None
        assert payment_data["payment_hash"] is not None

        payment_id = payment_data["payment_id"]
        payment_hash = payment_data["payment_hash"]

        # ---------------------------------------------------------
        # 2. Simulate successful Lightning payment
        # ---------------------------------------------------------

        payment = mark_payment_paid(
            db=db,
            payment_id=payment_id,
            payment_hash=payment_hash,
        )

        assert payment is not None
        assert payment.status == "paid"
        assert payment.credits_granted == 5

        db.refresh(account)

        assert account.credits == 5

        # ---------------------------------------------------------
        # 3. Retry original request
        # ---------------------------------------------------------

        response = client.post(
            "/api/security/analyze",
            json=payload,
        )

        assert response.status_code == 200

        data = response.json()

        assert data["source"] == user_id
        assert data["event_type"] == "network_flow"
        assert data["ml_label"] in {
            "BENIGN",
            "DDoS",
        }
        assert data["credits_remaining"] == 4

    finally:
        app.dependency_overrides.pop(
            get_authenticated_user,
            None,
        )