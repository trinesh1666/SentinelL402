import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import cast

from sqlalchemy.orm import Session

from app.models import APIKey, User


API_KEY_PREFIX = "sk_sentinel_"


def generate_api_key() -> str:
    random_part = secrets.token_urlsafe(32)

    return f"{API_KEY_PREFIX}{random_part}"


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(
        api_key.encode("utf-8")
    ).hexdigest()


def create_api_key(
    db: Session,
    user_id: str,
    name: str = "default",
    expires_in_days: int | None = None,
):
    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not user:
        raise ValueError(
            f"User '{user_id}' does not exist."
        )

    if (
        expires_in_days is not None
        and expires_in_days <= 0
    ):
        raise ValueError(
            "expires_in_days must be greater than 0."
        )

    raw_api_key = generate_api_key()

    key_hash = hash_api_key(raw_api_key)

    expires_at = None

    if expires_in_days is not None:
        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(days=expires_in_days)
        )

    api_key = APIKey(
        user_id=user.id,
        key_hash=key_hash,
        name=name,
        active=1,
        expires_at=expires_at,
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return raw_api_key, api_key

def authenticate_api_key(
    db: Session,
    raw_api_key: str,
):
    if not raw_api_key:
        return None

    raw_api_key = raw_api_key.strip()

    key_hash = hash_api_key(raw_api_key)

    api_key = (
        db.query(APIKey)
        .filter(
            APIKey.key_hash == key_hash,
            APIKey.active == 1,
        )
        .first()
    )

    if not api_key:
        return None

    now = datetime.now(timezone.utc)
    expires_at = cast(datetime | None, api_key.expires_at)

    if expires_at is not None:
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_at = expires_at.astimezone(timezone.utc)

        if expires_at <= now:
            return None

    setattr(api_key, "last_used_at", now)

    db.commit()

    user = (
        db.query(User)
        .filter(User.id == api_key.user_id)
        .first()
    )

    return user
def list_user_api_keys(
    db: Session,
    user_id: str,
):
    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not user:
        return []

    return (
        db.query(APIKey)
        .filter(APIKey.user_id == user.id)
        .order_by(APIKey.created_at.desc())
        .all()
    )


def revoke_api_key(
    db: Session,
    user_id: str,
    api_key_id: int,
):
    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not user:
        return None

    api_key = (
        db.query(APIKey)
        .filter(
            APIKey.id == api_key_id,
            APIKey.user_id == user.id,
        )
        .first()
    )

    if not api_key:
        return None

    setattr(api_key, "active", 0)

    db.commit()
    db.refresh(api_key)

    return api_key