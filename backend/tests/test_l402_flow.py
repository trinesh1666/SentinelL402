import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient
from app.services.auth_service import get_authenticated_user
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import Account
from app.services.metering_service import get_or_create_user


client = TestClient(app)


def create_test_features():
    return {
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


def test_complete_l402_flow():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        user_id = f"pytest-l402-{uuid.uuid4()}"
        payment_invoice = f"lnbc-test-l402-flow-{uuid.uuid4().hex}"
        payment_hash = f"test-l402-payment-hash-{uuid.uuid4().hex}"

        user = get_or_create_user(
            db,
            user_id,
        )
        app.dependency_overrides[get_authenticated_user] = (
    lambda: user_id
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

        payload = {
            "source": user_id,
            "event_type": "network_flow",
            "severity": "high",
            "description": "Full L402 flow test",
            "features": create_test_features(),
        }

        # --------------------------------------------------
        # STEP 1: Request with zero credits
        # --------------------------------------------------

        def fake_create_payment(db, user_id):
            from app.models import Payment

            payment = Payment(
                user_id=user.id,
                amount_sats=10,
                invoice=payment_invoice,
                payment_hash=payment_hash,
                status="pending",
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
                "/api/security/analyze",
                json=payload,
            )

        assert response_402.status_code == 402

        detail = response_402.json()["detail"]

        assert detail["error"] == "payment_required"
        assert detail["payment_method"] == "lightning"
        assert detail["amount_sats"] == 10
        assert detail["credits_to_add"] == 5

        payment_id = detail["payment_id"]

        # --------------------------------------------------
        # STEP 2: Simulate successful Lightning payment
        # --------------------------------------------------

        class FakePaymentStatus:
            paid = True

        with patch(
            "app.services.payment_service.check_lightning_payment",
            return_value=FakePaymentStatus(),
        ):
            verify_response = client.post(
                f"/api/payment/verify/{payment_id}"
            )

        assert verify_response.status_code == 200

        verify_data = verify_response.json()

        assert verify_data["payment_id"] == payment_id
        assert verify_data["status"] == "paid"
        assert verify_data["credits_added"] == 5
        assert verify_data["credits_remaining"] == 5

        # --------------------------------------------------
        # STEP 3: Retry original request
        # --------------------------------------------------

        response_200 = client.post(
            "/api/security/analyze",
            json=payload,
        )

        assert response_200.status_code == 200

        result = response_200.json()

        assert result["source"] == user_id
        assert result["event_type"] == "network_flow"
        assert result["ml_prediction"] in [0, 1]
        assert result["ml_label"] in ["BENIGN", "DDoS"]
        assert 0.0 <= result["confidence"] <= 1.0
        assert len(result["probabilities"]) == 2
        assert result["risk_level"] in ["LOW", "HIGH"]
        assert result["explanation"]
        assert result["recommendation"]

        # One credit was consumed by the successful retry.
        assert result["credits_remaining"] == 4

    finally:
        app.dependency_overrides.pop(
        get_authenticated_user,
        None,
    )
    db.close()