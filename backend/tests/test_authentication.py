import uuid

from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import Account
from app.services.api_key_service import create_api_key
from app.services.metering_service import get_or_create_user


client = TestClient(app)


def create_test_user(user_id: str):
    db = SessionLocal()

    try:
        user = get_or_create_user(
            db,
            user_id,
        )

        account = (
            db.query(Account)
            .filter(
                Account.user_id == user.id
            )
            .first()
        )

        account.credits = 5
        account.total_requests = 0

        db.commit()

        return user.user_id

    finally:
        db.close()


def create_test_api_key(user_id: str):
    db = SessionLocal()

    try:
        api_key, _ = create_api_key(
            db=db,
            user_id=user_id,
            name="pytest-auth-key",
        )

        return api_key

    finally:
        db.close()


def test_missing_api_key_returns_401():
    response = client.get(
        "/api/usage/test-user"
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Missing API key."
    }


def test_invalid_api_key_returns_403():
    response = client.get(
        "/api/usage/test-user",
        headers={
            "X-API-Key": "sk_sentinel_invalid_key",
        },
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail": "Invalid API key."
    }


def test_valid_api_key_authenticates_user():
    Base.metadata.create_all(bind=engine)

    user_id = f"pytest-auth-{uuid.uuid4()}"

    create_test_user(user_id)

    api_key = create_test_api_key(user_id)

    response = client.get(
        f"/api/usage/{user_id}",
        headers={
            "X-API-Key": api_key,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == user_id
    assert data["credits_remaining"] == 5
    assert data["total_requests"] == 0


def test_user_cannot_access_another_users_usage():
    Base.metadata.create_all(bind=engine)

    user_a_id = f"pytest-auth-a-{uuid.uuid4()}"
    user_b_id = f"pytest-auth-b-{uuid.uuid4()}"

    create_test_user(user_a_id)
    create_test_user(user_b_id)

    api_key_a = create_test_api_key(user_a_id)

    response = client.get(
        f"/api/usage/{user_b_id}",
        headers={
            "X-API-Key": api_key_a,
        },
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail": (
            "You are not authorized to view "
            "this user's usage."
        )
    }


def test_inactive_api_key_returns_403():
    Base.metadata.create_all(bind=engine)

    user_id = f"pytest-inactive-{uuid.uuid4()}"

    create_test_user(user_id)

    db = SessionLocal()

    try:
        api_key, api_key_record = create_api_key(
            db=db,
            user_id=user_id,
            name="pytest-inactive-key",
        )

        api_key_record.active = 0

        db.commit()

    finally:
        db.close()

    response = client.get(
        f"/api/usage/{user_id}",
        headers={
            "X-API-Key": api_key,
        },
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail": "Invalid API key."
    }