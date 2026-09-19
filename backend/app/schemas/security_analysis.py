from typing import Dict

from pydantic import BaseModel, Field


class SecurityAnalysisRequest(BaseModel):

    source: str = Field(
        ...,
        description="Client or detector identifier"
    )

    event_type: str = Field(
        ...,
        description="Type of security event"
    )

    severity: str = Field(
        ...,
        description="Initial event severity"
    )

    description: str = Field(
        ...,
        description="Description of the security event"
    )

    features: Dict[str, float] = Field(
        ...,
        description="The 78 network-flow features"
    )


class SecurityAnalysisResponse(BaseModel):

    source: str

    event_type: str

    ml_prediction: int

    ml_label: str

    confidence: float | None = None

    probabilities: list[float] | None = None

    risk_level: str

    explanation: str

    recommendation: str

    credits_remaining: int