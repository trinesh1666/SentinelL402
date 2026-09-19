from sqlalchemy.orm import Session
from typing import cast

from app.models import (
    User,
    Account,
    UsageRecord,
)


INITIAL_CREDITS = 5
CREDIT_COST_PER_REQUEST = 1


def get_or_create_user(
    db: Session,
    user_id: str,
) -> User:
    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if user:
        return user

    try:
        user = User(
            user_id=user_id,
        )

        db.add(user)
        db.flush()

        account = Account(
            user_id=user.id,
            credits=INITIAL_CREDITS,
            total_requests=0,
        )

        db.add(account)
        db.commit()
        db.refresh(user)

        return user

    except Exception:
        db.rollback()
        raise


def get_account(
    db: Session,
    user_id: str,
) -> Account | None:
    user = get_or_create_user(db, user_id)

    return (
        db.query(Account)
        .filter(Account.user_id == user.id)
        .first()
    )


def can_use_ai(
    db: Session,
    user_id: str,
) -> bool:
    account = get_account(
        db,
        user_id,
    )

    if account is None:
        return False

    return cast(int, account.credits) > 0


def consume_credit(
    db: Session,
    user_id: str,
) -> bool:
    account = get_account(
        db,
        user_id,
    )

    if account is None:
        return False

    updated_rows = (
        db.query(Account)
        .filter(
            Account.id == account.id,
            Account.credits >= CREDIT_COST_PER_REQUEST,
        )
        .update(
            {
                Account.credits: (
                    Account.credits - CREDIT_COST_PER_REQUEST
                ),
                Account.total_requests: (
                    Account.total_requests + 1
                ),
            },
            synchronize_session=False,
        )
    )

    if updated_rows != 1:
        db.rollback()
        return False

    usage = UsageRecord(
        user_id=account.user_id,
        request_type="ai_analysis",
        credits_used=CREDIT_COST_PER_REQUEST,
    )

    db.add(usage)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return True


def get_usage(
    db: Session,
    user_id: str,
) -> dict:
    account = get_account(
        db,
        user_id,
    )

    if account is None:
        return {
            "user_id": user_id,
            "credits_remaining": 0,
            "total_requests": 0,
        }

    return {
        "user_id": user_id,
        "credits_remaining": account.credits,
        "total_requests": account.total_requests,
    }
