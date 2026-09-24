import logging
import time
import uuid

from fastapi import Request


logger = logging.getLogger("sentinell402.request")


async def request_logging_middleware(
    request: Request,
    call_next,
):
    request_id = request.headers.get("X-Request-ID")

    if not request_id:
        request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    start_time = time.perf_counter()

    logger.info(
        "Request started | request_id=%s | method=%s | path=%s",
        request_id,
        request.method,
        request.url.path,
    )

    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        logger.exception(
            "Request failed | request_id=%s | method=%s | "
            "path=%s | duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            elapsed_ms,
        )

        raise

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    response.headers["X-Request-ID"] = request_id

    logger.info(
        "Request completed | request_id=%s | method=%s | "
        "path=%s | status=%s | duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )

    return response