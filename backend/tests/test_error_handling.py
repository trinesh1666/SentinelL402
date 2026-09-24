from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.error_handling import (
    unexpected_exception_handler,
)


def create_test_app() -> FastAPI:
    test_app = FastAPI()

    test_app.add_exception_handler(
        Exception,
        unexpected_exception_handler,
    )

    @test_app.get("/test-unexpected-error")
    def test_unexpected_error():
        raise RuntimeError(
            "SECRET_INTERNAL_DATABASE_PASSWORD"
        )

    return test_app


def test_unexpected_exception_returns_safe_500_response():
    test_app = create_test_app()

    client = TestClient(
        test_app,
        raise_server_exceptions=False,
    )

    response = client.get(
        "/test-unexpected-error"
    )

    assert response.status_code == 500

    body = response.json()

    assert body == {
        "error": "internal_server_error",
        "message": (
            "An unexpected internal error occurred. "
            "Please try again later."
        ),
    }

    assert (
        "SECRET_INTERNAL_DATABASE_PASSWORD"
        not in response.text
    )

    assert "RuntimeError" not in response.text