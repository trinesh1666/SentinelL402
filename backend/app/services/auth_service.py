from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.api_key_service import authenticate_api_key


API_KEY_HEADER = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
)


def get_authenticated_user(
    api_key: str | None = Security(
        API_KEY_HEADER
    ),
    db: Session = Depends(get_db),
) -> str:

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key.",
        )

    api_key = api_key.strip()

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key.",
        )

    user = authenticate_api_key(
        db=db,
        raw_api_key=api_key,
    )

    if not user:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key.",
        )

    return user.user_id