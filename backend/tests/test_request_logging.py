from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.request_logging import request_logging_middleware


def create_test_app() -> FastAPI:
    app = FastAPI()
    app.middleware("http")(request_logging_middleware)

    @app.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    return app


def test_request_id_is_generated():
    app = create_test_app()
    client = TestClient(app)

    response = client.get("/test")

    assert response.status_code == 200

    request_id = response.headers.get("X-Request-ID")

    assert request_id is not None
    assert len(request_id) > 0


def test_client_request_id_is_preserved():
    app = create_test_app()
    client = TestClient(app)

    response = client.get(
        "/test",
        headers={
            "X-Request-ID": "test-request-001",
        },
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-001"


def test_sensitive_headers_are_not_logged(caplog):
    app = create_test_app()
    client = TestClient(app)

    secret_api_key = "sk_sentinel_super_secret_test_key"

    with caplog.at_level("INFO", logger="sentinell402.request"):
        response = client.get(
            "/test",
            headers={
                "X-API-Key": secret_api_key,
                "X-Request-ID": "safe-request-001",
            },
        )

    assert response.status_code == 200

    logs = "\n".join(
        record.getMessage()
        for record in caplog.records
    )

    assert secret_api_key not in logs
    assert "X-API-Key" not in logs
    assert "safe-request-001" in logs