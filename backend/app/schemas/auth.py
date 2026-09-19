from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    user_id: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Unique user identifier",
    )

    email: EmailStr | None = Field(
        default=None,
        description="Optional user email",
    )

    api_key_name: str = Field(
        default="default",
        min_length=1,
        max_length=100,
        description="Name for the generated API key",
    )


class RegisterResponse(BaseModel):
    user_id: str
    email: EmailStr | None
    api_key: str
    api_key_name: str
    initial_credits: int
    message: str