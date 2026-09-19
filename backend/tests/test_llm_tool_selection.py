import json

from app.agent.llm_router import select_tool


def test_security_tool_selection(monkeypatch):

    def fake_generate_text(prompt):

        return json.dumps({
            "action": "analyze_security",
            "tool": "analyze_network_security",
            "arguments": {},
            "confidence": 0.95,
        })

    monkeypatch.setattr(
        "app.agent.llm_router.generate_text",
        fake_generate_text,
    )

    result = select_tool(
        "Analyze this network traffic for security threats."
    )

    assert result.action == "analyze_security"

    assert result.tool == (
        "analyze_network_security"
    )

    assert 0.0 <= result.confidence <= 1.0


def test_unsupported_tool_selection(monkeypatch):

    def fake_generate_text(prompt):

        return json.dumps({
            "action": "unsupported",
            "tool": "none",
            "arguments": {},
            "confidence": 0.95,
        })

    monkeypatch.setattr(
        "app.agent.llm_router.generate_text",
        fake_generate_text,
    )

    result = select_tool(
        "Tell me a joke about cricket."
    )

    assert result.action == "unsupported"

    assert result.tool == "none"

    assert 0.0 <= result.confidence <= 1.0