from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.agent.models import (
    AgentRequest,
    AgentResponse,
)

from app.agent.tools import (
    analyze_network_security,
)

from app.agent.llm_router import (
    classify_intent,
    select_tool,
)

from app.schemas.tool_arguments import (
    SecurityToolArguments,
)


ALLOWED_TOOLS = {
    "analyze_network_security",
}


class SentinelAgent:

    def __init__(self, db: Session):
        self.db = db

    def run(
        self,
        request: AgentRequest,
    ) -> AgentResponse:

        # -------------------------------------------------
        # 1. Classify user intent
        # -------------------------------------------------

        intent_result = classify_intent(
            request.intent
        )

        detected_intent = intent_result.get(
            "intent",
            "unsupported",
        )

        # -------------------------------------------------
        # 2. Reject unsupported intents
        # -------------------------------------------------

        if detected_intent != "security":

            return AgentResponse(
                action="unsupported_intent",
                tool="none",
                result={
                    "message": (
                        "The SentinelL402 agent "
                        "does not support this intent yet."
                    )
                },
            )

        # -------------------------------------------------
        # 3. Select the tool
        # -------------------------------------------------

        tool_decision = select_tool(
            request.intent
        )

        # -------------------------------------------------
        # 4. Security check: allow only approved tools
        # -------------------------------------------------

        if tool_decision.tool not in ALLOWED_TOOLS:

            return AgentResponse(
                action="unsupported_tool",
                tool=tool_decision.tool,
                result={
                    "message": (
                        "The requested tool is not "
                        "allowed by SentinelL402."
                    ),
                    "confidence": (
                        tool_decision.confidence
                    ),
                },
            )

        # -------------------------------------------------
        # 5. Validate the selected action
        # -------------------------------------------------

        if (
            tool_decision.action
            != "analyze_security"
        ):

            return AgentResponse(
                action="unsupported_action",
                tool=tool_decision.tool,
                result={
                    "message": (
                        "The requested agent action "
                        "is not supported."
                    ),
                    "confidence": (
                        tool_decision.confidence
                    ),
                },
            )

        # -------------------------------------------------
        # 6. Validate tool arguments
        # -------------------------------------------------

        try:

            tool_arguments = SecurityToolArguments(
                **request.parameters
            )

        except ValidationError as exc:

            return AgentResponse(
                action="invalid_arguments",
                tool=tool_decision.tool,
                result={
                    "message": (
                        "Invalid arguments supplied "
                        "for the security analysis tool."
                    ),
                    "errors": exc.errors(),
                },
            )

        # -------------------------------------------------
        # 7. Validate exactly 78 ML features
        # -------------------------------------------------

        if len(tool_arguments.features) != 78:

            return AgentResponse(
                action="invalid_arguments",
                tool=tool_decision.tool,
                result={
                    "message": (
                        "Security analysis requires "
                        "exactly 78 network-flow features."
                    ),
                    "feature_count": (
                        len(tool_arguments.features)
                    ),
                    "required_feature_count": 78,
                },
            )

        # -------------------------------------------------
        # 8. Execute the approved security tool
        # -------------------------------------------------

        result = analyze_network_security(
            db=self.db,
            authenticated_user=request.user_id,
            source=tool_arguments.source,
            event_type=tool_arguments.event_type,
            severity=tool_arguments.severity,
            description=tool_arguments.description,
            features=tool_arguments.features,
        )

        # -------------------------------------------------
        # 9. Return agent response
        # -------------------------------------------------

        return AgentResponse(
            action="analyze_security",
            tool="analyze_network_security",
            result=result,
        )