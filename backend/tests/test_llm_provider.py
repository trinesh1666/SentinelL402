import os
import sys
from unittest.mock import MagicMock, patch


# Make backend imports available when pytest runs from project root.
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    ),
)


def test_ollama_provider_is_selected():
    """
    Verify that LLM_PROVIDER=ollama routes the request
    to the Ollama implementation.
    """

    from app.services import llm_service

    with patch.object(
        llm_service,
        "LLM_PROVIDER",
        "ollama",
    ), patch.object(
        llm_service,
        "_generate_with_ollama",
        return_value="Ollama response",
    ) as mock_ollama, patch.object(
        llm_service,
        "_generate_with_openrouter",
    ) as mock_openrouter:

        result = llm_service.generate_text(
            "Test Ollama provider"
        )

    assert result == "Ollama response"

    mock_ollama.assert_called_once_with(
        prompt="Test Ollama provider",
        model=None,
    )

    mock_openrouter.assert_not_called()


def test_openrouter_provider_is_selected():
    """
    Verify that LLM_PROVIDER=openrouter routes the request
    to the OpenRouter implementation.
    """

    from app.services import llm_service

    with patch.object(
        llm_service,
        "LLM_PROVIDER",
        "openrouter",
    ), patch.object(
        llm_service,
        "_generate_with_openrouter",
        return_value="OpenRouter response",
    ) as mock_openrouter, patch.object(
        llm_service,
        "_generate_with_ollama",
    ) as mock_ollama:

        result = llm_service.generate_text(
            "Test OpenRouter provider"
        )

    assert result == "OpenRouter response"

    mock_openrouter.assert_called_once_with(
        prompt="Test OpenRouter provider",
        model=None,
    )

    mock_ollama.assert_not_called()


def test_openrouter_requires_api_key():
    """
    Verify that OpenRouter refuses to run when the API key
    is not configured.
    """

    from app.services import llm_service
    from app.middleware.error_handling import LLMServiceError

    with patch.object(
        llm_service,
        "OPENROUTER_API_KEY",
        "",
    ):
        try:
            llm_service._generate_with_openrouter(
                "Test missing API key"
            )
        except LLMServiceError as exc:
            assert str(exc) == (
                "OpenRouter API key is not configured."
            )
        else:
            raise AssertionError(
                "Expected LLMServiceError for missing API key."
            )


def test_openrouter_requires_model():
    """
    Verify that OpenRouter refuses to run when no model
    is configured.
    """

    from app.services import llm_service
    from app.middleware.error_handling import LLMServiceError

    with patch.object(
        llm_service,
        "OPENROUTER_API_KEY",
        "test-api-key",
    ), patch.object(
        llm_service,
        "OPENROUTER_MODEL",
        "",
    ):
        try:
            llm_service._generate_with_openrouter(
                "Test missing model"
            )
        except LLMServiceError as exc:
            assert str(exc) == (
                "OpenRouter model is not configured."
            )
        else:
            raise AssertionError(
                "Expected LLMServiceError for missing model."
            )


def test_openrouter_calls_openai_compatible_client():
    """
    Verify that the OpenRouter implementation creates an
    OpenAI-compatible client and sends the expected chat request.

    No real network request is made.
    """

    from app.services import llm_service

    mock_response = MagicMock()

    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content="Mocked OpenRouter response"
            )
        )
    ]

    mock_client = MagicMock()

    mock_client.chat.completions.create.return_value = (
        mock_response
    )

    mock_openai_class = MagicMock(
        return_value=mock_client
    )

    with patch.object(
        llm_service,
        "OPENROUTER_API_KEY",
        "test-api-key",
    ), patch.object(
        llm_service,
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1",
    ), patch(
        "openai.OpenAI",
        mock_openai_class,
    ):

        result = llm_service._generate_with_openrouter(
            prompt="Explain this security event.",
            model="test-provider/test-model",
        )

    assert result == "Mocked OpenRouter response"

    mock_openai_class.assert_called_once_with(
        api_key="test-api-key",
        base_url="https://openrouter.ai/api/v1",
    )

    mock_client.chat.completions.create.assert_called_once_with(
        model="test-provider/test-model",
        messages=[
            {
                "role": "user",
                "content": "Explain this security event.",
            }
        ],
    )