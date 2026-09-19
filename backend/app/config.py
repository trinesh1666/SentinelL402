import os

from dotenv import load_dotenv


load_dotenv()


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


def require_setting(value: str | None, name: str) -> str:
    if not value:
        raise RuntimeError(
            f"Required configuration setting '{name}' is missing."
        )

    return value