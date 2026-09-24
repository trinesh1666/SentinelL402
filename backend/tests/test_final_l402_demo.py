from typing import cast

from app.main import app, get_authenticated_user
from app.models import Account, Payment, User
from app.schemas.security_analysis import SecurityAnalysisResponse


USER_ID = "final-l402-demo-user"


FEATURES = {
    "Destination_Port": 80,
    "Flow_Duration": 1000000,
    "Total_Fwd_Packets": 10,
    "Total_Backward_Packets": 8,
    "Total_Length_of_Fwd_Packets": 5000,
    "Total_Length_of_Bwd_Packets": 4000,
    "Fwd_Packet_Length_Max": 1000,
    "Fwd_Packet_Length_Min": 40,
    "Fwd_Packet_Length_Mean": 500,
    "Fwd_Packet_Length_Std": 100,
    "Bwd_Packet_Length_Max": 1000,
    "Bwd_Packet_Length_Min": 40,
    "Bwd_Packet_Length_Mean": 500,
    "Bwd_Packet_Length_Std": 100,
    "Flow_Bytes/s": 9000,
    "Flow_Packets/s": 18,
    "Flow_IAT_Mean": 50000,
    "Flow_IAT_Std": 10000,
    "Flow_IAT_Max": 100000,
    "Flow_IAT_Min": 1000,
    "Fwd_IAT_Total": 500000,
    "Fwd_IAT_Mean": 50000,
    "Fwd_IAT_Std": 10000,
    "Fwd_IAT_Max": 100000,
    "Fwd_IAT_Min": 1000,
    "Bwd_IAT_Total": 400000,
    "Bwd_IAT_Mean": 50000,
    "Bwd_IAT_Std": 10000,
    "Bwd_IAT_Max": 100000,
    "Bwd_IAT_Min": 1000,
    "Fwd_PSH_Flags": 0,
    "Bwd_PSH_Flags": 0,
    "Fwd_URG_Flags": 0,
    "Bwd_URG_Flags": 0,
    "Fwd_Header_Length": 200,
    "Bwd_Header_Length": 160,
    "Fwd_Packets/s": 10,
    "Bwd_Packets/s": 8,
    "Min_Packet_Length": 40,
    "Max_Packet_Length": 1000,
    "Packet_Length_Mean": 500,
    "Packet_Length_Std": 100,
    "Packet_Length_Variance": 10000,
    "FIN_Flag_Count": 0,
    "SYN_Flag_Count": 1,
    "RST_Flag_Count": 0,
    "PSH_Flag_Count": 0,
    "ACK_Flag_Count": 1,
    "URG_Flag_Count": 0,
    "CWE_Flag_Count": 0,
    "ECE_Flag_Count": 0,
    "Down/Up_Ratio": 0.8,
    "Average_Packet_Size": 500,
    "Avg_Fwd_Segment_Size": 500,
    "Avg_Bwd_Segment_Size": 500,
    "Fwd_Header_Length.1": 200,
    "Fwd_Avg_Bytes/Bulk": 0,
    "Fwd_Avg_Packets/Bulk": 0,
    "Fwd_Avg_Bulk_Rate": 0,
    "Bwd_Avg_Bytes/Bulk": 0,
    "Bwd_Avg_Packets/Bulk": 0,
    "Bwd_Avg_Bulk_Rate": 0,
    "Subflow_Fwd_Packets": 10,
    "Subflow_Fwd_Bytes": 5000,
    "Subflow_Bwd_Packets": 8,
    "Subflow_Bwd_Bytes": 4000,
    "Init_Win_bytes_forward": 65535,
    "Init_Win_bytes_backward": 65535,
    "act_data_pkt_fwd": 10,
    "min_seg_size_forward": 20,
    "Active_Mean": 1000,
    "Active_Std": 100,
    "Active_Max": 2000,
    "Active_Min": 100,
    "Idle_Mean": 5000,
    "Idle_Std": 500,
    "Idle_Max": 10000,
    "Idle_Min": 1000,
}


def test_final_l402_closed_loop(client, db, monkeypatch):
    user = User(
        user_id=USER_ID,
        email="final-l402@example.com",
    )
    db.add(user)
    db.flush()

    account = Account(
        user_id=user.id,
        credits=1,
        total_requests=0,
    )
    db.add(account)
    db.commit()

    app.dependency_overrides[
        get_authenticated_user
    ] = lambda: USER_ID

    def fake_security_analysis(db, request):
        return SecurityAnalysisResponse(
            source=request.source,
            event_type=request.event_type,
            ml_prediction=0,
            ml_label="BENIGN",
            risk_level="low",
            confidence=0.99,
            explanation="The test network flow is classified as benign.",
            recommendation="No immediate action is required.",
            credits_remaining=1,
        )
    monkeypatch.setattr(
        "app.services.metered_security_service.perform_security_analysis",
        fake_security_analysis,
    )

    request_body = {
        "source": "CIC-IDS2017",
        "event_type": "network_traffic",
        "severity": "medium",
        "description": "Final L402 closed-loop test",
        "features": FEATURES,
    }

    first_response = client.post(
        "/api/security/analyze",
        json=request_body,
    )

    assert first_response.status_code == 200

    first_data = first_response.json()

    assert first_data["credits_remaining"] == 0

    pending_payment = Payment(
        user_id=user.id,
        amount_sats=10,
        invoice="final-test-invoice",
        payment_hash="final-test-hash",
        status="pending",
        credits_granted=0,
    )

    db.add(pending_payment)
    db.commit()
    db.refresh(pending_payment)

    class FakePaymentResult:
        paid = True
        amount = 10_000

    monkeypatch.setattr(
        "app.services.payment_service.check_lightning_payment",
        lambda payment_hash: FakePaymentResult(),
    )

    from app.services.payment_service import verify_payment

    verified_payment = verify_payment(
        db,
        cast(int, pending_payment.id),
        cast(str, user.user_id),
    )

    assert verified_payment is not None
    assert cast(str, verified_payment.status) == "paid"
    assert cast(int, verified_payment.credits_granted) == 5

    retry_response = client.post(
        "/api/security/analyze",
        json=request_body,
    )

    assert retry_response.status_code == 200

    retry_data = retry_response.json()

    assert retry_data["credits_remaining"] == 4

    final_account = (
        db.query(Account)
        .filter(Account.user_id == user.id)
        .first()
    )

    assert final_account.total_requests == 2
    assert final_account.credits == 4

    app.dependency_overrides.clear()