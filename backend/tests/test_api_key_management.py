import uuid
from typing import cast

from app.models import Account
from app.services.api_key_service import (
    create_api_key,
    list_user_api_keys,
    revoke_api_key,
)
from app.services.metering_service import (
    get_or_create_user,
)


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


def test_user_can_list_own_api_keys(db):
    user_id = (
        f"pytest-key-list-{uuid.uuid4()}"
    )

    user = create_test_user(
        db,
        user_id,
    )

    raw_api_key, api_key_record = (
        create_api_key(
            db=db,
            user_id=str(user.user_id),
            name="list-test-key",
        )
    )

    keys = list_user_api_keys(
        db=db,
        user_id=str(user.user_id),
    )

    assert len(keys) == 1
    assert cast(int, keys[0].id) == cast(int, api_key_record.id)
    assert cast(str, keys[0].name) == "list-test-key"
    assert cast(int, keys[0].active) == 1

    assert raw_api_key.startswith(
        "sk_sentinel_"
    )

    assert not hasattr(
        keys[0],
        "raw_api_key",
    )


def test_user_can_revoke_own_api_key(db):
    user_id = (
        f"pytest-key-revoke-{uuid.uuid4()}"
    )

    user = create_test_user(
        db,
        user_id,
    )

    raw_api_key, api_key_record = (
        create_api_key(
            db=db,
            user_id=str(user.user_id),
            name="revoke-test-key",
        )
    )

    revoked_key = revoke_api_key(
        db=db,
        user_id=str(user.user_id),
        api_key_id=cast(int, api_key_record.id),
    )

    assert revoked_key is not None
    assert cast(int, revoked_key.id) == cast(int, api_key_record.id)
    assert cast(int, revoked_key.active) == 0

    assert raw_api_key.startswith(
        "sk_sentinel_"
    )


def test_user_cannot_revoke_another_users_key(
    db,
):
    user_a_id = (
        f"pytest-key-owner-a-{uuid.uuid4()}"
    )

    user_b_id = (
        f"pytest-key-owner-b-{uuid.uuid4()}"
    )

    user_a = create_test_user(
        db,
        user_a_id,
    )

    user_b = create_test_user(
        db,
        user_b_id,
    )

    _, api_key_record = create_api_key(
        db=db,
        user_id=str(user_b.user_id),
        name="user-b-key",
    )

    result = revoke_api_key(
        db=db,
        user_id=str(user_a.user_id),
        api_key_id=cast(int, api_key_record.id),
    )

    assert result is None

    db.refresh(api_key_record)

    assert cast(int, api_key_record.active) == 1