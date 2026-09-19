from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import (
    Account,
    APIKey,
    Payment,
    UsageRecord,
    User,
)
from app.services.api_key_service import hash_api_key


client = TestClient(app)


def cleanup_user(user_id: str):
    db = SessionLocal()

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not user:
        db.close()
        return

    db.query(APIKey).filter(
        APIKey.user_id == user.id
    ).delete(
        synchronize_session=False
    )

    db.query(Payment).filter(
        Payment.user_id == user.id
    ).delete(
        synchronize_session=False
    )

    db.query(UsageRecord).filter(
        UsageRecord.user_id == user.id
    ).delete(
        synchronize_session=False
    )

    db.query(Account).filter(
        Account.user_id == user.id
    ).delete(
        synchronize_session=False
    )

    db.delete(user)
    db.commit()
    db.close()


def test_register_new_user():
    user_id = "pytest-registration-user-001"

    cleanup_user(user_id)

    response = client.post(
        "/api/auth/register",
        json={
            "user_id": user_id,
            "email": "registration@example.com",
            "api_key_name": "test-key",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["user_id"] == user_id
    assert data["email"] == "registration@example.com"
    assert data["api_key_name"] == "test-key"
    assert data["initial_credits"] == 5
    assert data["api_key"].startswith("sk_sentinel_")
    assert data["message"]


def test_duplicate_registration_is_rejected():
    user_id = "pytest-registration-duplicate"

    cleanup_user(user_id)

    first_response = client.post(
        "/api/auth/register",
        json={
            "user_id": user_id,
            "email": "duplicate@example.com",
            "api_key_name": "first-key",
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/auth/register",
        json={
            "user_id": user_id,
            "email": "duplicate@example.com",
            "api_key_name": "second-key",
        },
    )

    assert second_response.status_code == 409

    assert second_response.json() == {
        "detail": "User already exists."
    }


def test_registered_api_key_authenticates():
    user_id = "pytest-registration-auth"

    cleanup_user(user_id)

    register_response = client.post(
        "/api/auth/register",
        json={
            "user_id": user_id,
            "email": "auth@example.com",
            "api_key_name": "auth-test-key",
        },
    )

    assert register_response.status_code == 201

    api_key = register_response.json()["api_key"]

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


def test_wrong_api_key_is_rejected():
    user_id = "pytest-registration-wrong-key"

    cleanup_user(user_id)

    register_response = client.post(
        "/api/auth/register",
        json={
            "user_id": user_id,
            "email": "wrong-key@example.com",
            "api_key_name": "wrong-key-test",
        },
    )

    assert register_response.status_code == 201

    response = client.get(
        f"/api/usage/{user_id}",
        headers={
            "X-API-Key": "sk_sentinel_invalid_key",
        },
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail": "Invalid API key."
    }


def test_inactive_api_key_is_rejected():
    user_id = "pytest-registration-inactive"

    cleanup_user(user_id)

    register_response = client.post(
        "/api/auth/register",
        json={
            "user_id": user_id,
            "email": "inactive@example.com",
            "api_key_name": "inactive-test-key",
        },
    )

    assert register_response.status_code == 201

    api_key = register_response.json()["api_key"]

    db = SessionLocal()

    api_key_hash = hash_api_key(api_key)

    key_record = (
        db.query(APIKey)
        .filter(
            APIKey.key_hash == api_key_hash
        )
        .first()
    )

    assert key_record is not None

    key_record.active = 0
    db.commit()

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