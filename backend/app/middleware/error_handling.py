import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from app.middleware.database_errors import DatabaseServiceError

logger = logging.getLogger("sentinell402")


class LLMServiceError(Exception):
    """Raised when the configured LLM service cannot be used."""
class LightningServiceError(Exception):
    """Raised when the Lightning/NWC service cannot be used."""

async def database_service_exception_handler(
    request: Request,
    exc: DatabaseServiceError,
) -> JSONResponse:
    """Return a safe response for database dependency failures."""

    logger.error(
        "Database service failure",
        exc_info=True,
        extra={
            "method": request.method,
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=503,
        content={
            "error": "database_service_unavailable",
            "message": (
                "The database service is temporarily "
                "unavailable. Please try again later."
            ),
        },
    )

async def llm_service_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Return a safe response for LLM dependency failures."""

    logger.error(
        "LLM service failure",
        exc_info=True,
        extra={
            "method": request.method,
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=503,
        content={
            "error": "llm_service_unavailable",
            "message": (
                "The AI analysis service is temporarily "
                "unavailable. Please try again later."
            ),
        },
    )

async def lightning_service_exception_handler(
    request: Request,
    exc: LightningServiceError,
) -> JSONResponse:
    """Return a safe response for Lightning dependency failures."""

    logger.error(
        "Lightning service failure",
        exc_info=True,
        extra={
            "method": request.method,
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=503,
        content={
            "error": "lightning_service_unavailable",
            "message": (
                "The Lightning payment service is temporarily "
                "unavailable. Please try again later."
            ),
        },
    )

async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle unexpected application exceptions safely."""

    logger.exception(
        "Unhandled application exception",
        extra={
            "method": request.method,
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": (
                "An unexpected internal error occurred. "
                "Please try again later."
            ),
        },
    )