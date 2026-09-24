import uuid
from unittest.mock import patch

from app.main import app
from app.models import Account, Payment
from app.services.auth_service import get_authenticated_user
from app.services.metering_service import get_or_create_user


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


def create_payload(user_id):
    return {
        "user_id": user_id,
        "intent": "Analyze this network traffic for security threats",
        "parameters": {
            "source": "CIC-IDS2017",
            "event_type": "network_flow",
            "severity": "high",
            "description": "L402 end-to-end test",
            "features": FEATURES,
        },
    }


def test_l402_end_to_end_flow(
    db,
    client,
    mock_ollama,
):
    user_id = f"pytest-l402-end-to-end-{uuid.uuid4()}"

    # --------------------------------------------------
    # CREATE TEST USER
    # --------------------------------------------------

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

    assert account is not None

    # Start with zero credits.
    account.credits = 0
    account.total_requests = 0
    db.commit()

    # --------------------------------------------------
    # AUTHENTICATE AS TEST USER
    # --------------------------------------------------

    app.dependency_overrides[
        get_authenticated_user
    ] = lambda: user_id

    try:
        payload = create_payload(user_id)

        # --------------------------------------------------
        # 1. ZERO CREDITS -> HTTP 402
        # --------------------------------------------------

        def fake_create_payment(
            db,
            user_id,
        ):
            payment = Payment(
                user_id=user.id,
                amount_sats=10,
                invoice="test-invoice",
                payment_hash="test-payment-hash",
                status="pending",
                credits_granted=0,
            )

            db.add(payment)
            db.commit()
            db.refresh(payment)

            return payment

        with patch(
            "app.services.metered_security_service.create_payment",
            side_effect=fake_create_payment,
        ):
            response_402 = client.post(
                "/api/agent/run",
                json=payload,
            )

        assert response_402.status_code == 402

        detail = response_402.json()["detail"]

        assert detail["error"] == "payment_required"
        assert detail["payment_method"] == "lightning"
        assert detail["amount_sats"] == 10
        assert detail["credits_to_add"] == 5
        assert detail["invoice"] == "test-invoice"
        assert detail["payment_hash"] == "test-payment-hash"

        payment_id = detail["payment_id"]

        # --------------------------------------------------
        # 2. VERIFY PAYMENT
        # --------------------------------------------------

        class FakePaymentStatus:
            paid = True
            amount = 10_000

        with patch(
            "app.services.payment_service.check_lightning_payment",
            return_value=FakePaymentStatus(),
        ):
            verify_response = client.post(
                f"/api/payment/verify/{payment_id}"
            )

        assert verify_response.status_code == 200

        verification = verify_response.json()

        assert verification["payment_id"] == payment_id
        assert verification["user_id"] == user_id
        assert verification["amount_sats"] == 10
        assert verification["status"] == "paid"
        assert verification["credits_added"] == 5
        assert verification["credits_remaining"] == 5

        # --------------------------------------------------
        # 3. RETRY ORIGINAL REQUEST -> HTTP 200
        # --------------------------------------------------

        response_200 = client.post(
            "/api/agent/run",
            json=payload,
        )

        assert response_200.status_code == 200

        result = response_200.json()

        assert result["action"] == "analyze_security"
        assert result["tool"] == "analyze_network_security"

        security_result = result["result"]

        assert security_result["source"] == "CIC-IDS2017"
        assert security_result["event_type"] == "network_flow"

        assert security_result["ml_prediction"] in [
            0,
            1,
        ]

        assert security_result["ml_label"] in {
            "BENIGN",
            "DDoS",
        }

        assert 0.0 <= security_result["confidence"] <= 1.0

        assert len(
            security_result["probabilities"]
        ) == 2

        assert security_result["risk_level"] in {
            "LOW",
            "HIGH",
        }

        assert security_result["explanation"]
        assert security_result["recommendation"]

        # One credit consumed by successful retry.
        assert security_result["credits_remaining"] == 4

    finally:
        app.dependency_overrides.pop(
            get_authenticated_user,
            None,
        )
