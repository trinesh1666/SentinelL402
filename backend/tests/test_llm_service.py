from app.services.llm_service import generate_text


class FakeResponse:

    def raise_for_status(self):
        pass

    def json(self):
        return {
            "response": (
                "SentinelL402 local LLM is working."
            )
        }


def test_llm_service_returns_text(monkeypatch):

    def fake_post(
        url,
        json,
        timeout,
    ):
        assert url == (
            "http://localhost:11434/api/generate"
        )

        assert json["model"] == "llama3.2:3b"

        assert (
            json["prompt"]
            == "Reply with a short sentence "
            "confirming that SentinelL402 local LLM "
            "is working."
        )

        assert json["stream"] is False

        assert timeout == 120

        return FakeResponse()

    monkeypatch.setattr(
        "app.services.llm_service.requests.post",
        fake_post,
    )

    result = generate_text(
        "Reply with a short sentence "
        "confirming that SentinelL402 local LLM "
        "is working."
    )

    assert isinstance(result, str)
    assert len(result.strip()) > 0
    assert result == (
        "SentinelL402 local LLM is working."
    )