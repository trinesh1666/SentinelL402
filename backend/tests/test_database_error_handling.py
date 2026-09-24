from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.database_errors import (
    DatabaseServiceError,
)
from app.middleware.error_handling import (
    database_service_exception_handler,
)


def create_test_app() -> FastAPI:
    test_app = FastAPI()

    test_app.add_exception_handler(
        DatabaseServiceError,
        database_service_exception_handler,
    )

    @test_app.get("/test-database-error")
    def test_database_error():
        raise DatabaseServiceError(
            "SECRET_DATABASE_CONNECTION_STRING"
        )

    return test_app


def test_database_service_error_returns_503():
    test_app = create_test_app()

    client = TestClient(
        test_app,
        raise_server_exceptions=False,
    )

    response = client.get(
        "/test-database-error"
    )

    assert response.status_code == 503

    assert response.json() == {
        "error": "database_service_unavailable",
        "message": (
            "The database service is temporarily "
            "unavailable. Please try again later."
        ),
    }

    assert (
        "SECRET_DATABASE_CONNECTION_STRING"
        not in response.text
    )

    assert "DatabaseServiceError" not in response.text

def test_get_db_rolls_back_when_request_fails():
    from app.database import get_db

    generator = get_db()
    db = next(generator)

    rollback_called = False
    original_rollback = db.rollback

    def tracking_rollback():
        nonlocal rollback_called
        rollback_called = True
        original_rollback()

    db.rollback = tracking_rollback

    try:
        generator.throw(
            RuntimeError(
                "SECRET_DATABASE_FAILURE"
            )
        )
    except RuntimeError:
        pass

    assert rollback_called is True