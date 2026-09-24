from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.error_handling import (
    LLMServiceError,
    llm_service_exception_handler,
)


def create_test_app() -> FastAPI:
    test_app = FastAPI()

    test_app.add_exception_handler(
        LLMServiceError,
        llm_service_exception_handler,
    )

    @test_app.get("/test-llm-error")
    def test_llm_error():
        raise LLMServiceError(
            "SECRET_OLLAMA_CONNECTION_DETAILS"
        )

    return test_app


def test_llm_service_error_returns_503():
    test_app = create_test_app()

    client = TestClient(
        test_app,
        raise_server_exceptions=False,
    )

    response = client.get(
        "/test-llm-error"
    )

    assert response.status_code == 503

    body = response.json()

    assert body == {
        "error": "llm_service_unavailable",
        "message": (
            "The AI analysis service is temporarily "
            "unavailable. Please try again later."
        ),
    }

    assert (
        "SECRET_OLLAMA_CONNECTION_DETAILS"
        not in response.text
    )

    assert "LLMServiceError" not in response.text
def test_generate_text_converts_request_failure(
    monkeypatch,
):
    from app.services import llm_service

    def failing_post(*args, **kwargs):
        import requests

        raise requests.ConnectionError(
            "SECRET_CONNECTION_FAILURE"
        )

    monkeypatch.setattr(
        llm_service.requests,
        "post",
        failing_post,
    )

    try:
        llm_service.generate_text(
            "test prompt"
        )
        assert False, (
            "Expected LLMServiceError was not raised."
        )

    except llm_service.LLMServiceError as exc:
        assert str(exc) == (
            "LLM service request failed."
        )