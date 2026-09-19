from typing import Dict

from pydantic import BaseModel


class SecurityToolArguments(BaseModel):

    source: str

    event_type: str

    severity: str

    description: str

    features: Dict[str, float]