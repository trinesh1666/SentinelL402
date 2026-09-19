import json

from app.agent.llm_router import (
    classify_intent,
)


def test_llm_router_security_intent(monkeypatch):

    def fake_generate_text(prompt):

        return json.dumps({
            "intent": "security"
        })

    monkeypatch.setattr(
        "app.agent.llm_router.generate_text",
        fake_generate_text,
    )

    result = classify_intent(
        "Analyze this network traffic for security threats."
    )

    assert result["intent"] == "security"


def test_llm_router_unsupported_intent(monkeypatch):

    def fake_generate_text(prompt):

        return json.dumps({
            "intent": "unsupported"
        })

    monkeypatch.setattr(
        "app.agent.llm_router.generate_text",
        fake_generate_text,
    )

    result = classify_intent(
        "Tell me a joke about cricket."
    )

    assert result["intent"] == "unsupported"