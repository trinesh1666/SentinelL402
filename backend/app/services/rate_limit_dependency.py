from fastapi import HTTPException, Request

from app.services.rate_limit_service import rate_limiter


def check_rate_limit(request: Request):
    api_key = request.headers.get("X-API-Key")

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key.",
        )

    client_key = api_key.strip()

    if not client_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key.",
        )

    if not rate_limiter.allow(client_key):
        raise HTTPException(
            status_code=429,
            detail={
                "error": "rate_limit_exceeded",
                "message": "Too many requests. Please try again later.",
                "retry_after_seconds": 60,
            },
        )