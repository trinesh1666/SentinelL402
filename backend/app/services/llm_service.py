import os

import requests
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


def generate_text(
    prompt: str,
    model: str | None = None,
) -> str:
    selected_model = model or OLLAMA_MODEL

    payload = {
        "model": selected_model,
        "prompt": prompt,
        "stream": False,
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    return data["response"]


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