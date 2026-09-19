import uuid

from app.models import Account
from app.services.api_key_service import create_api_key
from app.services.metering_service import get_or_create_user


def create_test_user(db, user_id: str):
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


def create_test_api_key(db, user_id: str):
    api_key, _ = create_api_key(
        db=db,
        user_id=user_id,
        name="pytest-auth-key",
    )

    return api_key


def test_missing_api_key_returns_401(client):
    response = client.get(
        "/api/usage/test-user"
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Missing API key."
    }


def test_invalid_api_key_returns_403(client):
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


def test_valid_api_key_authenticates_user(client, db):
    user_id = f"pytest-auth-{uuid.uuid4()}"

    create_test_user(
        db,
        user_id,
    )

    api_key = create_test_api_key(
        db,
        user_id,
    )

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


def test_user_cannot_access_another_users_usage(
    client,
    db,
):
    user_a_id = f"pytest-auth-a-{uuid.uuid4()}"
    user_b_id = f"pytest-auth-b-{uuid.uuid4()}"

    create_test_user(
        db,
        user_a_id,
    )

    create_test_user(
        db,
        user_b_id,
    )

    api_key_a = create_test_api_key(
        db,
        user_a_id,
    )

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


def test_inactive_api_key_returns_403(
    client,
    db,
):
    user_id = f"pytest-inactive-{uuid.uuid4()}"

    create_test_user(
        db,
        user_id,
    )

    api_key, api_key_record = create_api_key(
        db=db,
        user_id=user_id,
        name="pytest-inactive-key",
    )

    api_key_record.active = 0

    db.commit()

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