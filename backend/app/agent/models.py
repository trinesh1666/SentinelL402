from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class AgentRequest:
    user_id: str
    intent: str
    parameters: Dict[str, Any]


@dataclass
class AgentResponse:
    action: str
    tool: str
    result: Dict[str, Any]