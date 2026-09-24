import uuid
from typing import cast

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

    return user


def test_api_key_list_requires_authentication(
    client,
):
    response = client.get(
        "/api/auth/api-keys"
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Missing API key."
    }


def test_api_key_revoke_requires_authentication(
    client,
):
    response = client.post(
        "/api/auth/api-keys/999999/revoke"
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Missing API key."
    }


def test_user_can_list_own_keys_through_api(
    client,
    db,
):
    user_id = (
        f"pytest-management-api-{uuid.uuid4()}"
    )

    user = create_test_user(
        db,
        user_id,
    )

    raw_api_key, api_key_record = create_api_key(
        db=db,
        user_id=str(user.user_id),
        name="api-list-test-key",
    )

    response = client.get(
        "/api/auth/api-keys",
        headers={
            "X-API-Key": raw_api_key,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1

    matching_keys = [
        item
        for item in data
        if item["id"] == cast(int, api_key_record.id)
    ]

    assert len(matching_keys) == 1

    key_data = matching_keys[0]

    assert key_data["name"] == (
        "api-list-test-key"
    )

    assert key_data["active"] is True

    assert "key_hash" not in key_data
    assert "api_key" not in key_data


def test_user_can_revoke_own_key_through_api(
    client,
    db,
):
    user_id = (
        f"pytest-management-revoke-{uuid.uuid4()}"
    )

    user = create_test_user(
        db,
        user_id,
    )

    raw_api_key, api_key_record = create_api_key(
        db=db,
        user_id=str(user.user_id),
        name="api-revoke-test-key",
    )

    response = client.post(
        f"/api/auth/api-keys/"
        f"{cast(int, api_key_record.id)}/revoke",
        headers={
            "X-API-Key": raw_api_key,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == cast(int, api_key_record.id)
    assert data["name"] == (
        "api-revoke-test-key"
    )
    assert data["active"] is False

    assert data["message"] == (
        "API key revoked successfully."
    )


def test_user_cannot_revoke_another_users_key(
    client,
    db,
):
    user_a_id = (
        f"pytest-management-a-{uuid.uuid4()}"
    )

    user_b_id = (
        f"pytest-management-b-{uuid.uuid4()}"
    )

    user_a = create_test_user(
        db,
        user_a_id,
    )

    user_b = create_test_user(
        db,
        user_b_id,
    )

    api_key_a, _ = create_api_key(
        db=db,
        user_id=str(user_a.user_id),
        name="user-a-key",
    )

    _, api_key_b_record = create_api_key(
        db=db,
        user_id=str(user_b.user_id),
        name="user-b-key",
    )

    response = client.post(
        f"/api/auth/api-keys/"
        f"{cast(int, api_key_b_record.id)}/revoke",
        headers={
            "X-API-Key": api_key_a,
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "API key not found."
    }

    db.refresh(api_key_b_record)

    assert cast(int, api_key_b_record.active) == 1