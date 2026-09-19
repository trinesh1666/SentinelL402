from pydantic import BaseModel
from typing import Dict

from pydantic import BaseModel, Field


class MLPredictionRequest(BaseModel):
    features: Dict[str, float] = Field(
        ...,
        description="The 78 network-flow features expected by the Random Forest model."
    )


class MLPredictionResponse(BaseModel):
    prediction: int
    label: str
    confidence: float | None = None
    probabilities: list[float] | None = None


class MLPredictionRequest(BaseModel):
    """
    Request containing CIC-IDS2017 network-flow features.
    """

    features: Dict[str, float]
