from typing import Any, Dict

from pydantic import BaseModel, Field


class AgentRequestSchema(BaseModel):
    user_id: str = Field(
        ...,
        description=(
            "Client-supplied user identifier. "
            "The authenticated API-key identity is authoritative."
        ),
    )

    intent: str = Field(
        ...,
        description="Natural language intent",
    )

    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters required by the selected tool",
    )


class AgentResponseSchema(BaseModel):
    action: str
    tool: str
    result: Dict[str, Any]