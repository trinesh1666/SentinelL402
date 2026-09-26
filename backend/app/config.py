import os

from dotenv import load_dotenv


load_dotenv()


APP_ENV = os.getenv(
    "APP_ENV",
    "development",
)


OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate",
)


OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:3b",
)


NWC_CONNECTION_STRING = os.getenv(
    "NWC_CONNECTION_STRING",
)


TEST_PAYER_NWC_CONNECTION_STRING = os.getenv(
    "TEST_PAYER_NWC_CONNECTION_STRING",
)


CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://127.0.0.1:5500,http://localhost:5500",
    ).split(",")
    if origin.strip()
]

LIGHTNING_PROVIDER = os.getenv(
    "LIGHTNING_PROVIDER",
    "nwc",
).strip().lower()
def require_setting(
    value: str | None,
    name: str,
) -> str:
    if not value:
        raise RuntimeError(
            f"Required configuration setting "
            f"'{name}' is missing."
        )

    return value