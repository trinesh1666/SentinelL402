from app.schemas.tool_arguments import (
    SecurityToolArguments,
)


def test_security_tool_arguments_valid():

    arguments = SecurityToolArguments(
        source="CIC-IDS2017",
        event_type="network_flow",
        severity="high",
        description="Suspicious network traffic",
        features={
        "Destination_Port": 80.0,
        },
    )

    assert arguments.event_type == "network_flow"
    assert arguments.severity == "high"
    assert len(arguments.features) == 1


def test_security_tool_arguments_requires_event_type():

    try:

        SecurityToolArguments(
            severity="high",
            description="Suspicious traffic",
            features={},
        )

    except ValueError as exc:

        assert "event_type" in str(exc)

    else:

        raise AssertionError(
            "Expected validation error"
        )


def test_security_tool_arguments_requires_features():

    try:

        SecurityToolArguments(
            event_type="network_flow",
            severity="high",
            description="Suspicious traffic",
        )

    except ValueError as exc:

        assert "features" in str(exc)

    else:

        raise AssertionError(
            "Expected validation error"
        )