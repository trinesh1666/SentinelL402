from app.services.llm_service import analyze_security_event


def main():
    print()
    print("===================================")
    print("SentinelL402 - Agent LLM Test")
    print("===================================")
    print()

    result = analyze_security_event(
        event_type="network_flow",
        severity="high",
        description=(
            "The machine learning detector classified the "
            "network flow as benign."
        ),
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

    print("LLM Security Explanation:")
    print()
    print(result)

    print()
    print("===================================")
    print("AGENT LLM TEST SUCCESSFUL")
    print("===================================")


if __name__ == "__main__":
    main()