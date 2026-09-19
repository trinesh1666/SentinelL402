from app.services.llm_service import analyze_security_event


def main():
    print()
    print("===================================")
    print("SentinelL402 - Grounded LLM Test")
    print("===================================")
    print()

    result = analyze_security_event(
        event_type="network_flow",
        severity="high",
        description="CIC-IDS2017 network flow security analysis test",
        ml_prediction=0,
        ml_label="BENIGN",
        confidence=1.0,
        risk_level="LOW",
        ml_explanation=(
            "The machine learning detector classified "
            "the network flow as benign."
        ),
        ml_recommendation=(
            "No immediate malicious activity was detected. "
            "Continue monitoring the network flow."
        ),
    )

    print("Grounded LLM Response:")
    print()
    print(result)

    print()
    print("===================================")
    print("GROUNDED LLM TEST SUCCESSFUL")
    print("===================================")


if __name__ == "__main__":
    main()
