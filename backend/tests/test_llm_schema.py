import pytest

from app.schemas.llm import (
    LLMRouterResponse,
    LLMToolCall,
)


def test_llm_router_response_valid():

    result = LLMRouterResponse(
        intent="security"
    )

    assert result.intent == "security"


def test_llm_tool_call_valid():

    result = LLMToolCall(
        action="analyze_security",
        tool="analyze_network_security",
        arguments={
            "event_type": "network_flow"
        },
        confidence=0.95,
    )

    assert result.action == "analyze_security"
    assert result.tool == "analyze_network_security"
    assert result.confidence == 0.95


def test_llm_tool_call_rejects_invalid_confidence():

    with pytest.raises(ValueError):

        LLMToolCall(
            action="analyze_security",
            tool="analyze_network_security",
            arguments={},
            confidence=1.5,
        )