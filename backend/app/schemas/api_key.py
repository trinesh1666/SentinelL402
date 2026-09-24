from datetime import datetime

from pydantic import BaseModel


class APIKeyResponse(BaseModel):
    id: int
    name: str | None
    active: bool
    created_at: datetime | None
    last_used_at: datetime | None
    expires_at: datetime | None


class APIKeyRevokeResponse(BaseModel):
    id: int
    name: str | None
    active: bool
    message: str