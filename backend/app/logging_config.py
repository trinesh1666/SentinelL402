import logging
import os


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def configure_logging() -> None:
    """Configure application-wide logging."""

    numeric_level = getattr(
        logging,
        LOG_LEVEL,
        logging.INFO,
    )

    logging.basicConfig(
        level=numeric_level,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        force=True,
    )

    logging.getLogger("sentinell402").setLevel(
        numeric_level
    )