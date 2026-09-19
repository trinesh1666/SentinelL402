import uuid

from app.main import app
from app.models import Account
from app.services.api_key_service import create_api_key
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


def test_real_api_key_can_call_agent(
    db,
    client,
):
    user_id = f"pytest-real-agent-auth-{uuid.uuid4()}"

    # ---------------------------------------------------------
    # 1. Create user and account
    # ---------------------------------------------------------

    user = get_or_create_user(
        db,
        user_id,
    )

    account = (
        db.query(Account)
        .filter(Account.user_id == user.id)
        .first()
    )

    assert account is not None

    account.credits = 5
    account.total_requests = 0
    db.commit()

    # ---------------------------------------------------------
    # 2. Create a real API key
    # ---------------------------------------------------------

    api_key, _ = create_api_key(
        db=db,
        user_id=user_id,
        name="pytest-real-agent-key",
    )

    # ---------------------------------------------------------
    # 3. Build the actual agent request
    # ---------------------------------------------------------

    payload = {
        "user_id": "attacker-supplied-user-id",
        "intent": "Analyze this network traffic for security threats",
        "parameters": {
            "source": "CIC-IDS2017",
            "event_type": "network_flow",
            "severity": "high",
            "description": "...",
            "features": FEATURES,
        },
    }

    headers = {
        "X-API-Key": api_key,
    }

    # ---------------------------------------------------------
    # 4. Call the real agent endpoint.
    #
    # IMPORTANT:
    # The payload contains a deliberately incorrect user_id.
    # The server must use the identity from the API key instead.
    # ---------------------------------------------------------

    response = client.post(
        "/api/agent/run",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    # ---------------------------------------------------------
    # 5. Validate agent response
    # ---------------------------------------------------------

    assert data["action"] == "analyze_security"
    assert data["tool"] == "analyze_network_security"

    result = data["result"]

    assert result["source"] == "CIC-IDS2017"
    assert result["event_type"] == "network_flow"

    assert result["ml_prediction"] in {
        0,
        1,
    }

    assert result["ml_label"] in {
        "BENIGN",
        "DDoS",
    }

    assert 0.0 <= result["confidence"] <= 1.0

    assert len(result["probabilities"]) == 2

    assert result["risk_level"] in {
        "LOW",
        "HIGH",
    }

    assert result["explanation"]
    assert result["recommendation"]

    # One credit must have been consumed.
    assert result["credits_remaining"] == 4

    # ---------------------------------------------------------
    # 6. Verify account directly
    # ---------------------------------------------------------

    db.refresh(account)

    assert account.credits == 4
    assert account.total_requests == 1

    print()
    print("REAL API KEY → AGENT TEST")
    print("-------------------------")
    print("Authenticated user:", user_id)
    print("Supplied payload user_id:", "attacker-supplied-user-id")
    print("Server identity:", result["source"])
    print("Agent action:", data["action"])
    print("Agent tool:", data["tool"])
    print("ML label:", result["ml_label"])
    print("Credits remaining:", result["credits_remaining"])
    print("API key authentication → agent → ML succeeded.")