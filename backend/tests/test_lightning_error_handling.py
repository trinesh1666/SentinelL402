from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.error_handling import (
    LightningServiceError,
    lightning_service_exception_handler,
)


def create_test_app() -> FastAPI:
    test_app = FastAPI()

    test_app.add_exception_handler(
        LightningServiceError,
        lightning_service_exception_handler,
    )

    @test_app.get("/test-lightning-error")
    def test_lightning_error():
        raise LightningServiceError(
            "SECRET_NWC_CONNECTION_STRING"
        )

    return test_app


def test_lightning_service_error_returns_503():
    test_app = create_test_app()

    client = TestClient(
        test_app,
        raise_server_exceptions=False,
    )

    response = client.get(
        "/test-lightning-error"
    )

    assert response.status_code == 503

    assert response.json() == {
        "error": "lightning_service_unavailable",
        "message": (
            "The Lightning payment service is temporarily "
            "unavailable. Please try again later."
        ),
    }

    assert (
        "SECRET_NWC_CONNECTION_STRING"
        not in response.text
    )

    assert "LightningServiceError" not in response.text


def test_create_invoice_converts_nwc_failure(
    monkeypatch,
):
    from app.services import lightning_service

    class FailingNWCClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            raise RuntimeError(
                "SECRET_NWC_INTERNAL_ERROR"
            )

        async def __aexit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

    monkeypatch.setattr(
        lightning_service,
        "NWCClient",
        FailingNWCClient,
    )

    monkeypatch.setattr(
        lightning_service,
        "LIGHTNING_PROVIDER",
        "nwc",
    )

    try:
        lightning_service.create_lightning_invoice(
            10,
            "test invoice",
        )

        assert False, (
            "Expected LightningServiceError "
            "was not raised."
        )

    except lightning_service.LightningServiceError as exc:
        assert str(exc) == "Lightning invoice creation failed."