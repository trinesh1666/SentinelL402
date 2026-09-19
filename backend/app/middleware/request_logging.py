import logging
import time
import uuid

from fastapi import Request


logger = logging.getLogger("sentinell402")


async def request_logging_middleware(
    request: Request,
    call_next,
):
    request_id = request.headers.get(
        "X-Request-ID"
    )

    if not request_id:
        request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    start_time = time.perf_counter()

    try:
        response = await call_next(request)

        elapsed_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(
                    elapsed_ms,
                    2,
                ),
            },
        )

        response.headers["X-Request-ID"] = request_id

        return response

    except Exception:
        elapsed_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.exception(
            "request_failed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "duration_ms": round(
                    elapsed_ms,
                    2,
                ),
            },
        )

        raise