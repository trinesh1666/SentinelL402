import logging
from unittest.mock import Mock

from app.services import llm_service


def test_llm_logging_does_not_log_prompt(
    monkeypatch,
    caplog,
):
    prompt_secret = "CONFIDENTIAL_SECURITY_EVENT_DATA"

    fake_response = Mock()
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = {
        "response": "Safe LLM response",
    }

    monkeypatch.setattr(
        llm_service.requests,
        "post",
        lambda *args, **kwargs: fake_response,
    )

    llm_logger = logging.getLogger("sentinell402.llm")
    original_propagate = llm_logger.propagate

    try:
        llm_logger.propagate = True

        with caplog.at_level(
            logging.INFO,
            logger="sentinell402.llm",
        ):
            result = llm_service.generate_text(
                prompt_secret,
            )
    finally:
        llm_logger.propagate = original_propagate

    assert result == "Safe LLM response"

    logs = "\n".join(
        record.getMessage()
        for record in caplog.records
        if record.name == "sentinell402.llm"
    )

    assert "LLM request started" in logs
    assert "LLM request completed" in logs
    assert prompt_secret not in logs