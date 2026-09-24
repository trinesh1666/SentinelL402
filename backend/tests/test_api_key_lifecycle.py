import uuid
from datetime import datetime, timedelta, timezone
from typing import cast

import pytest

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


def test_api_key_can_have_expiration(db):
    user_id = f"pytest-lifecycle-{uuid.uuid4()}"

    user = create_test_user(
        db,
        user_id,
    )

    before = (
        datetime.now(timezone.utc)
        + timedelta(days=29)
    )

    raw_api_key, api_key_record = create_api_key(
        db=db,
        user_id=str(user.user_id),
        name="pytest-expiring-key",
        expires_in_days=30,
    )

    assert raw_api_key.startswith(
        "sk_sentinel_"
    )

    assert api_key_record.expires_at is not None

    expiration = cast(datetime | None, api_key_record.expires_at)

    assert expiration is not None

    if expiration.tzinfo is None:
        expiration = expiration.replace(
            tzinfo=timezone.utc
        )

    assert expiration > before

    assert expiration < (
        datetime.now(timezone.utc)
        + timedelta(days=31)
    )


def test_api_key_can_be_non_expiring(db):
    user_id = f"pytest-no-expiry-{uuid.uuid4()}"

    user = create_test_user(
        db,
        user_id,
    )

    raw_api_key, api_key_record = create_api_key(
        db=db,
        user_id=str(user.user_id),
        name="pytest-non-expiring-key",
    )

    assert raw_api_key.startswith(
        "sk_sentinel_"
    )

    assert api_key_record.expires_at is None


def test_api_key_rejects_invalid_expiration(db):
    user_id = f"pytest-invalid-expiry-{uuid.uuid4()}"

    user = create_test_user(
        db,
        user_id,
    )

    with pytest.raises(
        ValueError,
        match="expires_in_days must be greater than 0",
    ):
        create_api_key(
            db=db,
            user_id=str(user.user_id),
            name="pytest-invalid-key",
            expires_in_days=0,
        )