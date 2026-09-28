import os
import logging

import requests
from dotenv import load_dotenv

from app.middleware.error_handling import LLMServiceError


load_dotenv()


logger = logging.getLogger("sentinell402.llm")


# ============================================================
# LLM PROVIDER CONFIGURATION
# ============================================================

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "ollama",
).strip().lower()


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:3b",
)


# ============================================================
# OPENROUTER CONFIGURATION
# ============================================================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    "",
).strip()

OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL",
    "https://openrouter.ai/api/v1",
).strip()

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "",
).strip()


def _generate_with_ollama(
    prompt: str,
    model: str | None = None,
) -> str:
    """
    Generate text using the local Ollama service.
    """

    selected_model = model or OLLAMA_MODEL

    payload = {
        "model": selected_model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        generated_text = data.get("response")

        if not isinstance(generated_text, str):
            raise LLMServiceError(
                "LLM response did not contain a valid response field."
            )

        return generated_text

    except LLMServiceError:
        raise

    except requests.RequestException as exc:
        raise LLMServiceError(
            "LLM service request failed."
        ) from exc

    except (ValueError, TypeError) as exc:
        raise LLMServiceError(
            "LLM service returned an invalid response."
        ) from exc


def _generate_with_openrouter(
    prompt: str,
    model: str | None = None,
) -> str:
    """
    Generate text using OpenRouter's OpenAI-compatible API.
    """

    if not OPENROUTER_API_KEY:
        raise LLMServiceError(
            "OpenRouter API key is not configured."
        )

    selected_model = (
        model
        or OPENROUTER_MODEL
    )

    if not selected_model:
        raise LLMServiceError(
            "OpenRouter model is not configured."
        )

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
        )

        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        if not response.choices:
            raise LLMServiceError(
                "OpenRouter response did not contain any choices."
            )

        message = response.choices[0].message
        generated_text = message.content

        if not isinstance(generated_text, str):
            raise LLMServiceError(
                "OpenRouter response did not contain valid text."
            )

        return generated_text

    except LLMServiceError:
        raise

    except Exception as exc:
        logger.exception(
            "OpenRouter request failed"
        )

        raise LLMServiceError(
            "LLM service request failed."
        ) from exc


def generate_text(
    prompt: str,
    model: str | None = None,
) -> str:
    """
    Generate text using the configured LLM provider.

    Supported providers:

    - ollama
    - openrouter

    Existing callers continue to use:

        generate_text(prompt)

    without needing to know which provider is active.
    """

    logger.info(
        "LLM request started | provider=%s",
        LLM_PROVIDER,
    )

    if LLM_PROVIDER == "ollama":
        generated_text = _generate_with_ollama(
            prompt=prompt,
            model=model,
        )

    elif LLM_PROVIDER == "openrouter":
        generated_text = _generate_with_openrouter(
            prompt=prompt,
            model=model,
        )

    else:
        raise LLMServiceError(
            f"Unsupported LLM provider: {LLM_PROVIDER}"
        )

    logger.info(
        "LLM request completed | provider=%s",
        LLM_PROVIDER,
    )

    return generated_text


def analyze_security_event(
    event_type: str,
    severity: str,
    description: str,
    ml_prediction: int,
    ml_label: str,
    confidence: float,
    risk_level: str,
    ml_explanation: str,
    ml_recommendation: str,
) -> str:
    """
    Generate an LLM explanation based on the actual
    machine-learning security analysis result.
    """

    prompt = f"""
You are the SentinelL402 cybersecurity assistant.

Your job is to explain the result produced by the
machine-learning security detector.

IMPORTANT RULES:

1. Treat the ML result as authoritative for this analysis.
2. Do not change or contradict the ML prediction.
3. Do not invent network statistics.
4. Do not claim that an attack is confirmed unless the
   supplied ML result supports that conclusion.
5. Clearly distinguish the ML classification from your explanation.
6. If the ML result is BENIGN, explain why the event is currently
   classified as benign and recommend continued monitoring.
7. If the ML result indicates malicious activity, explain the
   detected risk and recommend defensive investigation.
8. Do not invent facts that are not present in the supplied data.

SECURITY EVENT
---------------

Event type:
{event_type}

Severity:
{severity}

Description:
{description}

MACHINE LEARNING RESULT
-----------------------

ML prediction:
{ml_prediction}

ML label:
{ml_label}

ML confidence:
{confidence}

Risk level:
{risk_level}

ML explanation:
{ml_explanation}

ML recommendation:
{ml_recommendation}

Provide the response using exactly these three sections:

1. Security Analysis
2. Security Risk
3. Recommended Defensive Action

Keep the response concise, professional, and evidence-based.
"""

    return generate_text(prompt)