def test_request_id_is_returned(client):
    response = client.get(
        "/api/usage/nonexistent-request-id-test"
    )

    assert "X-Request-ID" in response.headers

    request_id = response.headers["X-Request-ID"]

    assert request_id
    assert len(request_id) > 10


def test_client_request_id_is_preserved(client):
    custom_request_id = "test-request-12345"

    response = client.get(
        "/api/usage/nonexistent-request-id-test",
        headers={
            "X-Request-ID": custom_request_id
        },
    )

    assert response.headers["X-Request-ID"] == (
        custom_request_id
    )