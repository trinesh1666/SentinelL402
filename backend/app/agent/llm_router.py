import json

from app.schemas.llm import (
    LLMRouterResponse,
    LLMToolCall,
)

from app.services.llm_service import (
    generate_text,
)


# =========================================================
# INTENT CLASSIFICATION PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are the routing component of SentinelL402.

Classify the user's request into exactly one of these intents:

security
unsupported

Use "security" when the user's request is related to:

- network traffic
- network security
- cybersecurity
- attacks
- threats
- malicious traffic
- intrusion detection
- DDoS
- suspicious network activity
- security analysis
- firewall
- packet analysis

Use "unsupported" for unrelated requests.

Return ONLY valid JSON.

Security request:

{"intent":"security"}

Unsupported request:

{"intent":"unsupported"}
"""


# =========================================================
# TOOL SELECTION PROMPT
# =========================================================

TOOL_SYSTEM_PROMPT = """
You are the tool-selection component of SentinelL402.

You may select ONLY the following tool:

analyze_network_security

For a security-analysis request, return ONLY valid JSON:

{
    "action": "analyze_security",
    "tool": "analyze_network_security",
    "arguments": {},
    "confidence": 0.0
}

The confidence value must be between 0 and 1.

Never invent tools.

For an unsupported request, return:

{
    "action": "unsupported",
    "tool": "none",
    "arguments": {},
    "confidence": 0.0
}
"""


# =========================================================
# SECURITY KEYWORDS
# =========================================================

SECURITY_KEYWORDS = {
    "security",
    "network",
    "attack",
    "attacks",
    "threat",
    "threats",
    "traffic",
    "malicious",
    "cybersecurity",
    "intrusion",
    "ddos",
    "suspicious",
    "firewall",
    "packet",
    "packets",
    "security analysis",
}


# =========================================================
# INTENT FALLBACK
# =========================================================

def _fallback_classify(
    user_message: str,
) -> str:

    text = user_message.lower()

    for keyword in SECURITY_KEYWORDS:

        if keyword in text:
            return "security"

    return "unsupported"


# =========================================================
# TOOL FALLBACK
# =========================================================

def _fallback_tool_selection(
    user_message: str,
) -> LLMToolCall:

    detected_intent = _fallback_classify(
        user_message
    )

    if detected_intent == "security":

        return LLMToolCall(
            action="analyze_security",
            tool="analyze_network_security",
            arguments={},
            confidence=1.0,
        )

    return LLMToolCall(
        action="unsupported",
        tool="none",
        arguments={},
        confidence=1.0,
    )


# =========================================================
# INTENT CLASSIFICATION
# =========================================================

def classify_intent(
    user_message: str,
) -> dict:

    prompt = f"""
{SYSTEM_PROMPT}

User request:
{user_message}
"""

    try:

        response = generate_text(
            prompt
        )

        data = json.loads(response)

        validated = LLMRouterResponse.model_validate(
            data
        )

        if validated.intent in {
            "security",
            "unsupported",
        }:

            return {
                "intent": validated.intent
            }

    except (
        json.JSONDecodeError,
        ValueError,
        KeyError,
        TypeError,
    ):
        pass

    # -----------------------------------------------------
    # Deterministic fallback
    # -----------------------------------------------------

    return {
        "intent": _fallback_classify(
            user_message
        )
    }


# =========================================================
# TOOL SELECTION
# =========================================================

def select_tool(
    user_message: str,
) -> LLMToolCall:

    prompt = f"""
{TOOL_SYSTEM_PROMPT}

User request:
{user_message}
"""

    try:

        response = generate_text(
            prompt
        )

        data = json.loads(response)

        validated = LLMToolCall.model_validate(
            data
        )

        # -------------------------------------------------
        # IMPORTANT SECURITY CHECK
        #
        # The LLM is NOT trusted to choose arbitrary tools.
        # Only our explicitly allowed tool can be accepted.
        # -------------------------------------------------

        if (
            validated.action
            == "analyze_security"
            and validated.tool
            == "analyze_network_security"
        ):

            return validated

        # -------------------------------------------------
        # If LLM returns unsupported/wrong tool,
        # use deterministic application fallback.
        # -------------------------------------------------

        return _fallback_tool_selection(
            user_message
        )

    except (
        json.JSONDecodeError,
        ValueError,
        KeyError,
        TypeError,
    ):

        # -------------------------------------------------
        # LLM failed to produce valid structured output.
        # Never crash the agent.
        # -------------------------------------------------

        return _fallback_tool_selection(
            user_message
        )