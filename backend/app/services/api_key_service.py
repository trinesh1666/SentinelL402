import hashlib
import secrets
from datetime import datetime, timezone

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

    raw_api_key = generate_api_key()

    key_hash = hash_api_key(raw_api_key)

    api_key = APIKey(
        user_id=user.id,
        key_hash=key_hash,
        name=name,
        active=1,
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

    api_key.last_used_at = datetime.now(timezone.utc)

    db.commit()

    user = (
        db.query(User)
        .filter(User.id == api_key.user_id)
        .first()
    )

    return user