from fastapi import Request

from app.services.rate_limit_service import RateLimiter


def test_rate_limiter_allows_requests_under_limit():
    limiter = RateLimiter(
        max_requests=3,
        window_seconds=60,
    )

    assert limiter.allow("client-1") is True
    assert limiter.allow("client-1") is True
    assert limiter.allow("client-1") is True


def test_rate_limiter_blocks_requests_over_limit():
    limiter = RateLimiter(
        max_requests=2,
        window_seconds=60,
    )

    assert limiter.allow("client-1") is True
    assert limiter.allow("client-1") is True
    assert limiter.allow("client-1") is False


def test_rate_limiter_is_per_client():
    limiter = RateLimiter(
        max_requests=1,
        window_seconds=60,
    )

    assert limiter.allow("client-1") is True
    assert limiter.allow("client-1") is False

    assert limiter.allow("client-2") is True


def test_rate_limiter_reset():
    limiter = RateLimiter(
        max_requests=1,
        window_seconds=60,
    )

    assert limiter.allow("client-1") is True
    assert limiter.allow("client-1") is False

    limiter.reset()

    assert limiter.allow("client-1") is True