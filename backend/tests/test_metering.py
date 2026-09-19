import uuid

from app.models import UsageRecord
from app.services.metering_service import (
    consume_credit,
    get_or_create_user,
    get_usage,
)


def test_user_gets_initial_credits(db):
    user_id = f"pytest-metering-{uuid.uuid4()}"

    user = get_or_create_user(
        db,
        user_id,
    )

    assert user.user_id == user_id

    usage = get_usage(
        db,
        user_id,
    )

    assert usage["credits_remaining"] == 5
    assert usage["total_requests"] == 0


def test_consume_credit(db):
    user_id = f"pytest-consume-{uuid.uuid4()}"

    get_or_create_user(
        db,
        user_id,
    )

    usage_before = get_usage(
        db,
        user_id,
    )

    assert usage_before["credits_remaining"] == 5
    assert usage_before["total_requests"] == 0

    success = consume_credit(
        db,
        user_id,
    )

    assert success is True

    usage_after = get_usage(
        db,
        user_id,
    )

    assert usage_after["credits_remaining"] == 4
    assert usage_after["total_requests"] == 1

    records = (
        db.query(UsageRecord)
        .filter(
            UsageRecord.user_id
            == get_or_create_user(db, user_id).id
        )
        .filter(
            UsageRecord.credits_used == 1
        )
        .all()
    )

    assert len(records) == 1