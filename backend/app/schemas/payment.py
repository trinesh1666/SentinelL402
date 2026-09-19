from pydantic import BaseModel, Field


class PaymentRequiredResponse(BaseModel):
    error: str = Field(
        default="payment_required",
        description="Error identifier",
    )
    message: str = Field(
        ...,
        description="Explanation of why payment is required",
    )
    payment_method: str = Field(
        default="lightning",
        description="Payment method accepted by the API",
    )
    payment_id: int | None = Field(
        default=None,
        description="Pending payment identifier",
    )
    amount_sats: int = Field(
        ...,
        description="Payment amount in satoshis",
    )
    invoice: str | None = Field(
        default=None,
        description="Lightning invoice to pay",
    )
    payment_hash: str | None = Field(
        default=None,
        description="Lightning payment hash",
    )
    credits_to_add: int = Field(
        default=5,
        description="Number of AI credits granted after successful payment",
    )


class PaymentCreateResponse(BaseModel):
    payment_id: int
    user_id: str
    amount_sats: int
    invoice: str | None = None
    payment_hash: str | None = None
    status: str
    credits_to_add: int = 5


class PaymentVerifyResponse(BaseModel):
    payment_id: int
    user_id: str
    amount_sats: int
    status: str
    credits_added: int
    credits_remaining: int