from typing import Any, Dict

from pydantic import BaseModel, Field


# --------------------------------------------------
# Existing SentinelL402 security event schema
# --------------------------------------------------

class SecurityEvent(BaseModel):
    source: str
    event_type: str
    severity: str
    description: str
    features: Dict[str, float]


# --------------------------------------------------
# Existing SentinelL402 LLM analysis schema
# --------------------------------------------------

class LLMAnalysis(BaseModel):
    explanation: str
    recommendation: str


# --------------------------------------------------
# Structured LLM router response
# --------------------------------------------------

class LLMRouterResponse(BaseModel):
    intent: str = Field(
        ...,
        description="Detected user intent"
    )


# --------------------------------------------------
# Structured LLM tool call
# --------------------------------------------------

class LLMToolCall(BaseModel):
    action: str = Field(
        ...,
        description="Action selected by the agent"
    )

    tool: str = Field(
        ...,
        description="Tool selected by the agent"
    )

    arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments passed to the selected tool"
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="LLM confidence between 0 and 1"
    )