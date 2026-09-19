from app.services.llm_service import generate_text


def main():
    prompt = """
You are the SentinelL402 cybersecurity assistant.

Explain what a benign network flow means in cybersecurity.

Give:
1. A short explanation.
2. The security significance.
3. One recommended defensive action.

Keep the answer concise.
"""

    print()
    print("===================================")
    print("SentinelL402 - LLM Service Test")
    print("===================================")
    print()

    print("Model response:")
    print()

    result = generate_text(prompt)

    print(result)

    print()
    print("===================================")
    print("LLM TEST SUCCESSFUL")
    print("===================================")


if __name__ == "__main__":
    main()