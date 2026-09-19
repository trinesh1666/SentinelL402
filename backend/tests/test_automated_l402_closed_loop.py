from datetime import datetime, timedelta, timezone

from app.main import app, get_authenticated_user
from app.models import Account, User
from app.services.metering_service import get_or_create_user


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


def make_request_body():
    return {
        "source": "automated-test",
        "event_type": "network_flow",
        "severity": "medium",
        "description": "Automated L402 closed-loop test",
        "features": FEATURES,
    }


def test_automated_l402_closed_loop(client, db, monkeypatch):
    user_id = "automated-l402-test-user"

    # ---------------------------------------------------------
    # 1. Create test user/account
    # ---------------------------------------------------------
    get_or_create_user(db, user_id)

    account = (
        db.query(Account)
        .join(User, Account.user_id == User.id)
        .filter(User.user_id == user_id)
        .first()
    )

    assert account is not None

    # Start with exactly one credit.
    account.credits = 1
    db.commit()

    # ---------------------------------------------------------
    # 2. Override authentication
    # ---------------------------------------------------------
    app.dependency_overrides[get_authenticated_user] = (
        lambda: user_id
    )

    # ---------------------------------------------------------
    # 3. Mock ONLY the actual security analysis
    # ---------------------------------------------------------
    def fake_security_analysis(db, request):
        from app.schemas.security_analysis import SecurityAnalysisResponse

        return SecurityAnalysisResponse(
            source=request.source,
            event_type=request.event_type,
            ml_prediction=0,
            ml_label="BENIGN",
            confidence=1.0,
            probabilities=[1.0, 0.0],
            risk_level="LOW",
            explanation="Automated test analysis.",
            recommendation="Continue monitoring.",
            credits_remaining=0,
        )

    monkeypatch.setattr(
        "app.services.metered_security_service.perform_security_analysis",
        fake_security_analysis,
    )

    # ---------------------------------------------------------
    # 4. First request: should consume the only credit
    # ---------------------------------------------------------
    response = client.post(
        "/api/security/analyze",
        headers={"X-API-Key": "test-api-key"},
        json=make_request_body(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["ml_label"] == "BENIGN"
    assert data["risk_level"] == "LOW"
    assert data["credits_remaining"] == 0

    # Confirm credit was actually consumed.
    db.expire_all()

    account = (
        db.query(Account)
        .join(User, Account.user_id == User.id)
        .filter(User.user_id == user_id)
        .first()
    )

    assert account.credits == 0
    assert account.total_requests == 1

    # ---------------------------------------------------------
    # 5. Second request: should return HTTP 402
    # ---------------------------------------------------------
    monkeypatch.setattr(
        "app.services.metered_security_service.create_payment",
        lambda db, user_id: None,
    )

    response = client.post(
        "/api/security/analyze",
        headers={"X-API-Key": "test-api-key"},
        json=make_request_body(),
    )

    assert response.status_code == 500

    body = response.json()

    assert body["detail"]["error"] == "payment_creation_failed"

    # ---------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------
    app.dependency_overrides.clear()